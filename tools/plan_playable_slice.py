"""Structural card shortlist for the first strict-Beta slice, not a deck validator.

Reads the existing normalized catalogue; never treats fewer nodes as semantic
support. Explicit TemplateId/LinkedTemplateId closure is only a lower bound:
random/filter/provider-selected cards and location abilities require analysis.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/beta924/normalized/catalog.json"
OUT = ROOT / "data/beta924/planning"
FACTIONS = {2: "Monsters", 4: "Nilfgaard", 8: "Northern Realms", 16: "Scoia'tael", 32: "Skellige"}
TIERS = {1: "Leader", 2: "Bronze", 4: "Silver", 8: "Gold"}


def trees(root):
    yield root
    for child in root["children"]:
        yield from trees(child)


def references(tree):
    for element in trees(tree):
        raw = element["attributes"].get("TemplateId")
        if raw is not None and int(raw) != 0:
            yield int(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=6, help="Shortlist entries per faction/tier")
    parser.add_argument("--cards", type=int, nargs="*", default=[], help="Explicit exploratory IDs; no legality claim")
    args = parser.parse_args()
    if not 1 <= args.limit <= 40:
        parser.error("limit must be1..40")
    raw = CATALOG.read_bytes()
    catalog = json.loads(raw)
    templates = {item["templateId"]: item for item in catalog["templates"]}
    abilities = defaultdict(list)
    location_abilities = []
    for ability in catalog["abilities"]:
        if ability["type"] == "CardAbility":
            abilities[ability["templateId"]].append(ability)
        else:
            location_abilities.append(ability)
    if any(card not in templates for card in args.cards):
        parser.error("unknown exploratory TemplateId")

    def summary(records):
        nodes = Counter(node["type"] for ability in records for node in ability["nodes"])
        variables = Counter()
        for ability in records:
            for node in ability["nodes"]:
                for element in trees(node["sourceTree"]):
                    if element is node["sourceTree"]:
                        continue
                    attributes = element["attributes"]
                    kind = attributes.get("Type")
                    if kind:
                        variables[kind + ("<" + attributes["GArg"] + ">" if "GArg" in attributes else "")] += 1
        return dict(abilityRecordKeys=[a["recordKey"] for a in records],
            nodeCount=sum(nodes.values()), nodeTypeCount=len(nodes),
            nodeTypes=dict(sorted(nodes.items())), connectorVariableTypes=dict(sorted(variables.items())),
            connectionCount=sum(len(a["connections"]) for a in records),
            nonNodeDeclarations=[dict(recordKey=a["recordKey"], attributes=a["attributes"],
                children=[child for child in a["sourceTree"]["children"]
                    if child["tag"] not in ("Nodes", "Connections")]) for a in records])

    def closure(ids):
        selected = set(ids)
        pending = sorted(selected, reverse=True)
        while pending:
            template_id = pending.pop()
            template = templates[template_id]
            linked = template["fields"]["LinkedTemplateId"]
            dependencies = {linked} if linked else set()
            for ability in abilities[template_id]:
                dependencies.update(references(ability["sourceTree"]))
            for dependency in sorted(dependencies):
                if dependency not in templates:
                    raise ValueError(f"Missing explicit dependency {dependency}")
                if dependency not in selected:
                    selected.add(dependency)
                    pending.append(dependency)
        ordered = sorted(selected)
        records = [a for template_id in ordered for a in abilities[template_id]]
        return dict(templateIds=ordered, **summary(records))

    def describe(template):
        template_id = template["templateId"]
        fields = template["fields"]
        explicit = closure([template_id])
        ru = catalog["localization"]["ru_ru"].get(f"{template_id}_name", "")
        en = catalog["localization"]["en_us"].get(f"{template_id}_name", "")
        return dict(templateId=template_id, nameRu=ru, nameEn=en,
            availability=int(template["attributes"]["Availability"]), **fields,
            placement=template["placement"],
            directGraph=summary(abilities[template_id]), explicitDependencies=explicit,
            runtimeEffectCoverageVerified=False, deckLegalVerified=False,
            dynamicDependenciesComplete=False)

    descriptions = {template_id: describe(template) for template_id, template in templates.items()}
    shortlists = []
    for faction_id, faction in FACTIONS.items():
        for tier_id, tier in TIERS.items():
            candidates = [d for d in descriptions.values() if d["availability"] == 1
                and d["Tier"] == tier_id and d["Kind"] == 1
                and (d["FactionId"] == faction_id or (tier_id != 1 and d["FactionId"] == 1))]
            candidates.sort(key=lambda d: (d["explicitDependencies"]["nodeTypeCount"],
                d["explicitDependencies"]["nodeCount"], len(d["explicitDependencies"]["templateIds"]), d["templateId"]))
            shortlists.append(dict(factionId=faction_id, faction=faction, tier=tier,
                metadataCandidateCount=len(candidates), cards=candidates[:args.limit]))
    result = dict(schema=1, source=str(CATALOG), sourceSha256=hashlib.sha256(raw).hexdigest(),
        generatorSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        target=catalog["target"], shortlistLimit=args.limit,
        gameplayTestsRun=False, runtimeEffectCoverageVerified=False, legalDecksCreated=False,
        scope="Structural planning only. BaseSet1/Normal1, faction-or-neutral and tier metadata filter. Not complete Availability/copy/leader/deck legality or implemented effects.",
        limits="Explicit references only; dynamic card selection and original global/default subscriptions are unresolved. Node count is not execution complexity or handler coverage. All location-token records shown as a conservative separate universe, not automatically active.",
        locationAbilityUniverse=summary(location_abilities),
        allNodeTypes=sorted({n["type"] for a in catalog["abilities"] for n in a["nodes"]}),
        shortlists=shortlists,
        exploratoryCards=[descriptions[i] for i in args.cards],
        exploratoryExplicitClosure=closure(args.cards))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "first_slice_candidates.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Кандидаты первого карточного slice", "", "Сгенерировано tools/plan_playable_slice.py.", "",
        "Это структурный shortlist, **не две готовые legal decks** и не реализованные эффекты.",
        "Порядок: число node types → число nodes → число explicit TemplateIds → ID.",
        "Все типы пока без проверенных effect handlers. Меньше nodes не означает проще runtime.",
        "Нулевой graph не отменяет declarations/variables и общий card lifecycle; они сохранены в JSON.",
        "Dynamic dependencies, subscriptions и полная legality ещё требуют разбора.", "",
        f"Catalogue SHA256: {result['sourceSha256']}.", "",
        f"Отдельная conservative universe: {len(location_abilities)} location abilities, "
        f"{result['locationAbilityUniverse']['nodeTypeCount']} типов nodes; не считать их все активными.", ""]
    for entry in shortlists:
        lines += [f"## {entry['faction']} / {entry['tier']}", "",
            "| ID | Название | Faction/type | Power/armor | Direct records | Explicit node types/nodes |",
            "|---|---|---|---|---|---|"]
        for card in entry["cards"]:
            name = (card["nameRu"] or card["nameEn"]).replace("|", "/").replace("\n", " ")
            dependency = card["explicitDependencies"]
            lines.append(f"|{card['templateId']}|{name}|{card['FactionId']}/{card['Type']}|{card['Power']}/{card['Armor']}|"
                f"{len(card['directGraph']['abilityRecordKeys'])}|{dependency['nodeTypeCount']}/{dependency['nodeCount']}|")
        lines.append("")
    (OUT / "first_slice_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Structural shortlists: {len(shortlists)} faction/tier groups. Legal decks created: false. Gameplay tests: none.")


if __name__ == "__main__":
    main()
