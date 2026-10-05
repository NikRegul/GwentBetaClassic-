"""Deterministic structural catalog of canonical Beta data, not executable effect IR."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import io
import json
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'
SCALARS = ('Rarity', 'Kind', 'LinkedTemplateId', 'LinkedTemplateOrder', 'FactionId',
           'Tier', 'Type', 'Tokens', 'Power', 'Armor', 'InitialTimer')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def tree(element):
    """Preserve polymorphic field names, raw attributes and child order."""
    return {'tag': element.tag, 'attributes': dict(element.attrib),
            'text': element.text or '', 'children': [tree(child) for child in element]}


def mask_words(element):
    words = [int(child.attrib['V']) for child in element]
    if not words or [child.tag for child in element] != [f'e{i}' for i in range(len(words))] or any(word < 0 or word > 0xffffffffffffffff for word in words):
        raise ValueError('Expected ordered uint64 mask words: ' + element.tag)
    # BitArray stores UInt64[]. Decimal strings plus two32-bit halves avoid
    # silent precision loss when JSON is later read by JavaScript tooling.
    return [{'decimal': str(word), 'low32': word & 0xffffffff, 'high32': word >> 32} for word in words]


def build_catalog():
    source_bytes = SOURCE.read_bytes()
    source_hash = digest(source_bytes)
    baseline = json.loads((ROOT / 'docs/evidence/beta-archive.json').read_text(encoding='utf-8-sig'))
    if source_hash.lower() != baseline['sha256'].lower():
        raise ValueError('Canonical source differs from audited Beta archive')
    with zipfile.ZipFile(io.BytesIO(source_bytes)) as archive:
        entry_hashes = {name: digest(archive.read(name)) for name in archive.namelist()}
        template_xml = ET.fromstring(archive.read('Templates.xml'))
        ability_xml = ET.fromstring(archive.read('Abilities.xml'))
        templates, abilities, locales = [], [], {}
        for index, element in enumerate(template_xml):
            if {child.tag for child in element} != set(SCALARS) | {
                    'ArtDefinition', 'ResetInInactive', 'Placement', 'Categories', 'SemanticTags'}:
                raise ValueError('Unexpected template schema')
            boolean = element.findtext('ResetInInactive')
            if boolean not in ('True', 'False'):
                raise ValueError('Unexpected ResetInInactive')
            templates.append({'sourceIndex': index, 'templateId': int(element.attrib['Id']),
                'attributes': dict(element.attrib),
                'fields': {key: int(element.findtext(key)) for key in SCALARS},
                'resetInInactive': boolean == 'True',
                'categoryWords': mask_words(element.find('Categories')),
                'semanticTagWords': mask_words(element.find('SemanticTags')),
                'art': dict(element.find('ArtDefinition').attrib),
                'placement': dict(element.find('Placement').attrib),
                'sourceTree': tree(element)})
        template_ids = {record['templateId'] for record in templates}
        if len(template_ids) != len(templates):
            raise ValueError('Duplicate Template ID')
        for record in templates:
            linked = record['fields']['LinkedTemplateId']
            if linked and linked not in template_ids:
                raise ValueError('Unresolved linked template: ' + str(linked))
        node_types = collections.Counter()
        nid_counts = collections.Counter()
        total_connections = 0
        for index, element in enumerate(ability_xml):
            nid = int(element.attrib['NId'])
            nid_counts[nid] += 1
            # NId is local data, not a unique ability key. Preserve each record.
            kind = element.attrib['Type']
            template_id = int(element.attrib['Template']) if 'Template' in element.attrib else None
            if template_id is not None and template_id not in template_ids:
                raise ValueError('Unresolved CardAbility.Template')
            id_elements = [child for child in element.iter() if 'Id' in child.attrib]
            id_counts = collections.Counter(int(child.attrib['Id']) for child in id_elements)
            if any(count != 1 for count in id_counts.values()):
                raise ValueError('Duplicate graph-local Id: ability index ' + str(index))
            ports = {}
            nodes = []
            for node_index, node in enumerate(element.findall('Nodes/*')):
                node_id, node_type = int(node.attrib['Id']), node.attrib['Type']
                node_types[node_type] += 1
                for child in node.iter():
                    if child is node or 'Id' not in child.attrib:
                        continue
                    ports[int(child.attrib['Id'])] = {'nodeId': node_id, 'field': child.tag,
                                                       'type': child.attrib.get('Type')}
                nodes.append({'sourceIndex': node_index, 'nodeId': node_id,
                              'type': node_type, 'attributes': dict(node.attrib),
                              'sourceTree': tree(node)})
            connections = []
            for connection in element.findall('Connections/*'):
                source_id, destination_id = int(connection.attrib['SrcId']), int(connection.attrib['DstId'])
                if source_id not in ports or destination_id not in ports:
                    raise ValueError('Connection endpoint does not resolve to a node field')
                if connection.attrib['Type'] != 'Connection':
                    raise ValueError('Unexpected connection type')
                connections.append({'id': int(connection.attrib['Id']),
                    'sourceId': source_id, 'destinationId': destination_id,
                    'sourcePort': ports[source_id], 'destinationPort': ports[destination_id],
                    'attributes': dict(connection.attrib)})
            for child in element.iter():
                ref = child.attrib.get('TemplateId')
                if ref and int(ref) and int(ref) not in template_ids:
                    raise ValueError('Unresolved nested template reference')
            total_connections += len(connections)
            abilities.append({'recordKey': f'ability/{index}', 'sourceIndex': index,
                'nid': nid, 'type': kind, 'templateId': template_id,
                'attributes': dict(element.attrib), 'nodes': nodes,
                'connections': connections, 'sourceTree': tree(element)})
        for language in ('ru_ru', 'en_us'):
            rows = list(csv.DictReader(io.StringIO(
                archive.read('Localization/' + language + '.csv').decode('utf-8-sig'), newline=''), delimiter=';'))
            keys = [row['Key'] for row in rows if row.get('Key')]
            if len(keys) != len(set(keys)):
                raise ValueError('Duplicate localization keys: ' + language)
            locales[language] = {row['Key']: row[language] for row in rows if row.get('Key')}
            if any(str(template_id) + '_name' not in locales[language] for template_id in template_ids):
                raise ValueError('Missing localized template name')
        catalog = {'schema': 1, 'target': '0.9.24.3.432', 'sourceSha256': source_hash,
            'templates': templates, 'abilities': abilities, 'localization': locales,
            'scope': 'Structural data only; raw polymorphic payload retained. No executable effect handlers.'}
        coverage = {'schema': 1, 'templates': len(templates), 'abilities': len(abilities),
            'connections': total_connections, 'nodeTypeCount': len(node_types),
            'nodeCounts': dict(node_types), 'implementedExecutableNodeTypes': [],
            'unsupportedExecutableNodeTypes': sorted(node_types),
            'repeatedNIds': {str(key): count for key, count in sorted(nid_counts.items()) if count > 1},
            'unresolvedGraphEndpoints': 0, 'unresolvedTemplateReferences': 0,
            'localizationKeys': {language: len(values) for language, values in locales.items()},
            'categoryWordCounts': dict(collections.Counter(len(record['categoryWords']) for record in templates)),
            'extendedCategoryTemplates': [record['templateId'] for record in templates if len(record['categoryWords']) > 3],
            'maskWordBits': 64,
            'maskWordsAboveUInt32': sum(int(word['decimal']) > 0xffffffff for record in templates
                                       for key in ('categoryWords', 'semanticTagWords') for word in record[key]),
            'warnings': ['NId is not globally unique; recordKey is archive-index scoped and bound to source hash.',
                         'Availability/tokens remain raw; collectible pool and legality are not classified.',
                         'All183 executable node types are unsupported until handlers and oracle traces exist.']}
        outputs = {'normalized/catalog.json': encoded(catalog), 'coverage.json': encoded(coverage)}
        manifest = {'schema': 1, 'source': str(SOURCE), 'sourceSha256': source_hash,
            'entrySha256': entry_hashes, 'target': '0.9.24.3.432',
            'outputs': {name: {'sha256': digest(raw), 'bytes': len(raw)} for name, raw in outputs.items()},
            'scope': 'Source-preserving catalog; does not install cards or generated scripts into the mod.'}
        outputs['manifest.json'] = encoded(manifest)
        return outputs, coverage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'data/beta924')
    parser.add_argument('--verify', action='store_true', help='Rebuild in memory and require byte-identical outputs; writes nothing.')
    args = parser.parse_args()
    target = args.out.resolve()
    if not target.is_relative_to(ROOT) or target == ROOT:
        raise SystemExit('Output must be a subdirectory of the workspace')
    outputs, coverage = build_catalog()
    for name, raw in outputs.items():
        path = target / name
        if not path.resolve().is_relative_to(target):
            raise SystemExit('Output escapes catalog directory')
        if path.exists() and path.read_bytes() != raw:
            raise SystemExit('Existing catalog differs; inspect before regenerating: ' + str(path))
        if args.verify and (not path.exists() or path.read_bytes() != raw):
            raise SystemExit('Catalog is not byte-identical: ' + str(path))
    if not args.verify:
        for name, raw in outputs.items():
            path = target / name
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects a concurrently created file.
            with path.open('xb') as stream:
                stream.write(raw)
    print(json.dumps({'verified': args.verify, 'templates': coverage['templates'],
        'abilities': coverage['abilities'], 'connections': coverage['connections'],
        'nodeTypes': coverage['nodeTypeCount'], 'executableNodeTypesImplemented': 0,
        'repeatedNIds': len(coverage['repeatedNIds'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
