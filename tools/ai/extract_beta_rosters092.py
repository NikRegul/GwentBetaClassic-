"""Read original serialized Beta deck/player assets, preserving exact source IDs."""
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/vendor/audio-python"))
import UnityPy


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def unpack(self, fmt):
        value = struct.unpack_from("<" + fmt, self.data, self.pos)
        self.pos += struct.calcsize("<" + fmt)
        return value[0] if len(value) == 1 else value

    def string(self):
        size = self.unpack("i")
        assert 0 <= size <= len(self.data) - self.pos
        text = self.data[self.pos:self.pos + size].decode("utf-8")
        self.pos = (self.pos + size + 3) & ~3
        return text

    def card(self):
        template = self.unpack("i")
        premium = self.unpack("B")
        assert premium in (0, 1)
        self.pos = (self.pos + 3) & ~3
        return {"templateId": template, "premium": bool(premium)}

    def pointer(self):
        file_id, path_id = self.unpack("iq")
        return {"fileId": file_id, "pathId": path_id}

    def count(self):
        count = self.unpack("i")
        assert 0 <= count <= 100
        return count

    def header(self):
        self.pos = 28  # Unity MonoBehaviour base: GameObject, enabled, MonoScript.
        return self.string()

    def finish(self):
        assert self.pos == len(self.data), (self.pos, len(self.data))


base = ROOT / "Gwent 0.9.24.3.432/Gwent_Data"
files = sorted(p for p in base.iterdir() if p.name.endswith(".assets") or p.name.startswith("level") and p.is_file())
env = UnityPy.load(*(str(p) for p in files))
decks, players = [], []
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    # Custom fields have stripped type trees; read only Unity header here.
    header = obj.read(check_read=False)
    try:
        script = header.m_Script.read()
    except (ValueError, FileNotFoundError):
        continue
    if script.m_ClassName not in ("DeckDefinition", "PlayerDefinition"):
        continue
    raw = obj.get_raw_data()
    r = Reader(raw)
    name = r.header()
    assert name == header.m_Name
    source = {"file": obj.assets_file.name, "pathId": obj.path_id,
              "rawSha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    if script.m_ClassName == "DeckDefinition":
        display_name, faction, leader, banner = r.string(), r.unpack("i"), r.card(), r.card()
        trinkets = [r.card() for _ in range(r.count())]
        entries = []
        for _ in range(r.count()):
            card, quantity = r.card(), r.unpack("i")
            assert 0 < quantity <= 100
            entries.append({**card, "copies": quantity})
        r.finish()
        decks.append({"asset": name, "name": display_name, "faction": faction,
                      "leader": leader, "banner": banner, "trinkets": trinkets,
                      "entries": entries, "cards": [c["templateId"] for c in entries for _ in range(c["copies"])],
                      "source": source})
    else:
        # PlayerInfo fields, then serialized PlayerDefinition deck/difficulty/level.
        player_name, title, personality = r.string(), r.string(), r.string()
        level, mmr, rank = r.unpack("iii")
        vanity = dict(zip(("avatar", "tauntPack", "border", "title", "board"), r.unpack("QQQQQ")))
        deck = r.pointer()
        difficulty, definition_level = r.unpack("ii")
        r.finish()
        players.append({"asset": name, "name": player_name, "title": title, "personality": personality,
                        "level": level, "mmr": mmr, "rank": rank, "vanity": vanity,
                        "deck": deck, "difficulty": difficulty, "definitionLevel": definition_level, "source": source})

by_id = {(d["source"]["file"], d["source"]["pathId"]): d for d in decks}
for player in players:
    pointer = player["deck"]
    if pointer["pathId"]:
        assert pointer["fileId"] == 0, "Cross-file deck pointer needs explicit resolver"
        deck = by_id[(player["source"]["file"], pointer["pathId"])]
        player["deckAsset"] = deck["asset"]
        deck.setdefault("players", []).append({k: player[k] for k in ("asset", "personality", "difficulty")})

used_files = sorted({d["source"]["file"] for d in decks + players})
report = {"schema": 1, "scope": "Exact serialized original deck and player assets; not tournament eligibility or strength",
          "sources": {name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in used_files},
          "deckCount": len(decks), "playerCount": len(players), "decks": decks, "players": players}
output = ROOT / "BetaGwent/drafts/day-iteration-20261023/beta-original-js/original-rosters.json"
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"decks": len(decks), "players": len(players),
                  "practiceDecks": sum("Practice" in d["asset"] for d in decks),
                  "cardCounts": sorted(set(len(d["cards"]) for d in decks)),
                  "output": str(output.relative_to(ROOT))}))
