"""Read-only REDkit/TW3 audit; outputs evidence in the workspace, no game launch.

SWF inspection covers container tags/SymbolClass only, not AVM2 decompilation.
Binary quest hits are candidate references, never parsed graph edges.
"""
import argparse
import collections
import csv
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zlib
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def info(path, root):
    data = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "bytes": len(data), "sha256": digest(data)}


def swf_info(path, root):
    raw = path.read_bytes()
    result = info(path, root)
    signature = raw[:3]
    result.update(signature=signature.decode("ascii"), version=raw[3])
    if signature == b"CWS":
        body = zlib.decompress(raw[8:])
    elif signature == b"FWS":
        body = raw[8:]
    else:
        raise ValueError(f"Unsupported SWF signature: {path}")
    declared = struct.unpack_from("<I", raw, 4)[0]
    if declared != len(body) + 8:
        raise ValueError(f"SWF length mismatch: {path}")
    # RECT: UB[5] Nbits followed by four signed Nbits coordinates.
    rect_bytes = (5 + 4 * (body[0] >> 3) + 7) // 8
    pos = rect_bytes + 4  # frame rate and frame count
    tags = collections.Counter()
    symbols = []
    abc = []
    end_seen = False
    while pos < len(body):
        header = struct.unpack_from("<H", body, pos)[0]
        pos += 2
        code, size = header >> 6, header & 63
        if size == 63:
            size = struct.unpack_from("<I", body, pos)[0]
            pos += 4
        if pos + size > len(body):
            raise ValueError(f"SWF tag out of bounds: {path}")
        payload = body[pos:pos + size]
        pos += size
        tags[code] += 1
        if code == 76:  # SymbolClass
            count = struct.unpack_from("<H", payload)[0]
            at = 2
            for _ in range(count):
                character_id = struct.unpack_from("<H", payload, at)[0]
                at += 2
                end = payload.index(b"\0", at)
                symbols.append({"characterId": character_id, "class": payload[at:end].decode("utf-8")})
                at = end + 1
            if at != len(payload):
                raise ValueError(f"Unexpected SymbolClass trailer: {path}")
        if code == 82:  # DoABC; inspect metadata without executing bytecode
            end = payload.index(b"\0", 4)
            abc.append({"name": payload[4:end].decode("utf-8"), "bytes": len(payload) - end - 1})
        if code == 0:
            end_seen = True
            break
    result.update(declaredUncompressedBytes=declared, endTag=end_seen,
                  trailingBytes=len(body) - pos, tagCounts=dict(tags), symbols=symbols,
                  rootClasses=[s["class"] for s in symbols if s["characterId"] == 0], abc=abc)
    return result


def run(workspace, redkit, game):
    out = workspace / "docs/evidence"
    out.mkdir(parents=True, exist_ok=True)
    root = redkit / "r4data"

    def save(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files = sorted(Path(directory) / name for directory, _, names in os.walk(root) for name in names)
    downloads = [p.relative_to(root).as_posix() for p in files if p.name.endswith(".download")]
    projects = sorted((Path(directory) / name).relative_to(workspace).as_posix()
                      for directory, _, names in os.walk(workspace) for name in names if name.endswith(".w3edit"))
    comparisons = []
    differences = []
    script_root = root / "scripts"
    game_scripts = game / "content/content0/scripts"
    for source in sorted(script_root.rglob("*.ws")):
        relative = source.relative_to(script_root)
        target = game_scripts / relative
        original = source.read_bytes()
        record = {"path": relative.as_posix(), "redkitSHA256": digest(original)}
        if target.exists():
            installed = target.read_bytes()
            record.update(gameSHA256=digest(installed), byteEqual=original == installed)
            left = original.decode("utf-8-sig").splitlines()
            right = installed.decode("utf-8-sig").splitlines()
            record["textEqualIgnoringBOMAndLineEndings"] = left == right
            if left != right:
                differences.extend(difflib.unified_diff(left, right, fromfile="REDkit/" + relative.as_posix(),
                                                       tofile="TW3/" + relative.as_posix(), lineterm=""))
        else:
            record["missingInGame"] = True
        comparisons.append(record)
    save("redkit-script-comparison.json", comparisons)
    (out / "redkit-script-differences.diff").write_text("\n".join(differences) + "\n", encoding="utf-8")

    xml_records = []
    for path in files:
        if path.suffix.lower() != ".xml" or not re.search(r"gwi?nt|gwent", path.name, re.I):
            continue
        tree = ET.parse(path)
        collections_found = []
        for group in tree.getroot().iter("deck_collection"):
            decks = [{"attributes": dict(deck.attrib), "cards": [dict(c.attrib) for c in deck.findall("card")]} for deck in group.findall("deck")]
            dynamic = [{"attributes": dict(node.attrib), "cards": [dict(c.attrib) for c in node.findall("card")]}
                       for node in group.findall("dynamicCards")]
            collections_found.append({"attributes": dict(group.attrib), "decks": decks, "dynamicCards": dynamic})
        definitions = []
        for parent in tree.getroot().iter():
            if parent.tag in ("gwint_card_definitions_final", "gwint_king_card_definitions", "gwint_battle_king_card_definitions"):
                definitions.extend({"tag": child.tag, "attributes": dict(child.attrib),
                                    "flags": {sub.tag: [dict(x.attrib) for x in sub] for sub in child}}
                                   for child in parent)
        items = [dict(item.attrib) for item in tree.getroot().iter("item")]
        xml_records.append({**info(path, root), "tagCounts": dict(collections.Counter(e.tag for e in tree.getroot().iter())),
                            "deckCollections": collections_found, "cardDefinitions": definitions, "items": items})
    save("redkit-gwent-xml.json", xml_records)
    with (out / "redkit-deck-catalog.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "deckCollection", "difficulty", "leaderCard", "specialCard", "fixedCards", "dynamicEntries"])
        for record in xml_records:
            for group in record["deckCollections"]:
                dynamic_count = sum(len(node["cards"]) for node in group["dynamicCards"])
                for deck in group["decks"]:
                    attrs = deck["attributes"]
                    writer.writerow([record["path"], group["attributes"]["name"], attrs.get("difficulty", ""),
                                     attrs.get("leaderCard", ""), attrs.get("specialCard", ""), len(deck["cards"]), dynamic_count])

    rewards = []
    for path in files:
        if path.name != "rewards.xml":
            continue
        tree = ET.parse(path)
        selected = []
        for reward in tree.getroot().iter("reward"):
            items = [dict(item.attrib) for item in reward.iter("item")]
            name = reward.get("name", "")
            if (any(item.get("name", "").startswith("gwint_") for item in items)
                    or re.match(r"cg(?:_|\d)|sq306_", name)):
                selected.append({"attributes": dict(reward.attrib), "items": items})
        if selected:
            rewards.append({**info(path, root), "rewards": selected})
    save("redkit-gwent-rewards.json", rewards)

    source_root = root / "gameplay/gui_new/actionscript/red/game/witcher3/menus/gwint"
    as_records = []
    for path in sorted(source_root.glob("*.as")):
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        matches = []
        for number, line in enumerate(lines, 1):
            if re.search(r"\bfunction\b|GameEvent\.(CALL|REGISTER)|stateMachine\.(AddState|ChangeState)", line):
                matches.append({"line": number, "text": line.strip()})
        as_records.append({**info(path, root), "lines": len(lines), "symbols": matches})
    save("redkit-gwent-actionscript.json", as_records)
    swfs = [swf_info(root / f"gameplay/gui_new/swf/gwint/{name}.swf", root) for name in ("gwint_game", "deck_builder")]
    save("redkit-gwent-swf.json", swfs)
    fla_records = []
    for path in sorted((root / "gameplay/gui_new/fla/witcher3/gwint").glob("*.fla")):
        data = path.read_bytes()
        record = {**info(path, root), "headerHex": data[:12].hex()}
        eocd_at = data.rfind(b"PK\x05\x06")
        if eocd_at >= 0:
            eocd = struct.unpack_from("<4s4H2IH", data, eocd_at)
            record.update(zipEOCDOffset=eocd_at, zipDeclaredCentralOffset=eocd[6],
                          zipCentralSignatureHex=data[eocd[6]:eocd[6]+4].hex())
        try:
            with zipfile.ZipFile(path) as archive:
                record["zipEntries"] = len(archive.namelist())
                record["documentSettings"] = []
                for name in ("DOMDocument.xml", "PublishSettings.xml"):
                    if name in archive.namelist():
                        record["documentSettings"].extend(line.strip() for line in archive.read(name).decode("utf-8").splitlines()
                                                          if re.search(r"documentClass|libraryPath|sourcePath|classPath", line, re.I))
        except (zipfile.BadZipFile, UnicodeDecodeError) as error:
            record["zipReadError"] = str(error)
            record["note"] = "Generic ZIP reader failure does not establish Adobe authoring-tool compatibility."
        fla_records.append(record)
    save("redkit-gwent-fla.json", fla_records)

    deck_names = sorted({c["attributes"]["name"] for record in xml_records for c in record["deckCollections"]})
    quest_records = []
    # Class-name hits establish presence only; no attempt to decode CR2W properties/connections.
    class_pattern = re.compile(rb"C(?:Quest|StoryScene)[A-Za-z]*(?:[Mm]ini[Gg]ame|Gwint)[A-Za-z]*")
    interesting = re.compile(r"gwint|gwent|mini.?game|card|reward|tournament|sq306|cg[12367]00|q001|academic|EMS_", re.I)
    for path in files:
        if path.suffix.lower() not in (".w2quest", ".w2phase", ".w2scene"):
            continue
        data = path.read_bytes()
        classes = sorted({m.decode("ascii") for m in class_pattern.findall(data)})
        if not classes:
            continue
        strings = sorted({s.decode("ascii") for s in re.findall(rb"[\x20-\x7e]{4,}", data)})
        # Exact ASCII string match avoids substring joins such as North/NorthFoo.
        candidates = sorted(set(strings).intersection(deck_names))
        quest_records.append({**info(path, root), "classNameHits": classes,
                              "deckNameStringCandidates": candidates,
                              "relevantASCIIStrings": [s for s in strings if interesting.search(s)],
                              "confidence": "raw binary strings only; not graph edges or NPC bindings"})
    save("redkit-quest-candidates.json", quest_records)
    summary = {"redkit": str(redkit), "game": str(game), "r4dataFiles": len(files),
               "downloadFiles": downloads, "workspaceW3EditProjects": projects,
               "scriptsCompared": len(comparisons),
               "scriptsByteEqual": sum(bool(x.get("byteEqual")) for x in comparisons),
               "scriptsTextEqual": sum(bool(x.get("textEqualIgnoringBOMAndLineEndings")) for x in comparisons),
               "scriptsMissingInGame": sum(bool(x.get("missingInGame")) for x in comparisons),
               "gwentXMLFiles": len(xml_records), "deckCollectionNames": deck_names,
               "modernGwentASFiles": len(as_records), "questCandidateFiles": len(quest_records),
               "selectedRewardRecords": sum(len(record["rewards"]) for record in rewards),
               "swfRootClasses": [s["rootClasses"] for s in swfs],
               "note": "Installed r4data availability audit, not validation of an uncooked user depot or runtime."}
    save("redkit-summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("downloadFiles", "deckCollectionNames")}, ensure_ascii=False))
    print("downloadFiles:", len(downloads), "deckCollectionNames:", len(deck_names))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(r"D:\w3mod"))
    parser.add_argument("--redkit", type=Path, default=Path(r"D:\GOG Galaxy\Games\The Witcher 3 REDkit"))
    parser.add_argument("--game", type=Path, default=Path(r"F:\Steam\steamapps\common\The Witcher 3"))
    args = parser.parse_args()
    run(args.workspace, args.redkit, args.game)
