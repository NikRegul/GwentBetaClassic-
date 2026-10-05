"""Independent round-trip checks of the structural catalog against source XML."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from import_beta924 import ROOT, SOURCE, mask_words


def same_tree(xml, record):
    if xml.tag != record['tag'] or dict(xml.attrib) != record['attributes'] or (xml.text or '') != record['text']:
        return False
    return len(xml) == len(record['children']) and all(same_tree(child, value) for child, value in zip(xml, record['children']))


def main():
    target = ROOT / 'data/beta924'
    manifest = json.loads((target / 'manifest.json').read_text(encoding='utf-8'))
    for name, item in manifest['outputs'].items():
        raw = (target / name).read_bytes()
        assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
    catalog = json.loads((target / 'normalized/catalog.json').read_text(encoding='utf-8'))
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert manifest['sourceSha256'] == catalog['sourceSha256'] == source_hash
    words, high_words = 0, 0
    with zipfile.ZipFile(SOURCE) as archive:
        templates = ET.fromstring(archive.read('Templates.xml'))
        abilities = ET.fromstring(archive.read('Abilities.xml'))
        assert len(templates) == len(catalog['templates']) == 698
        assert len(abilities) == len(catalog['abilities']) == 567
        for original, record in zip(templates, catalog['templates']):
            assert same_tree(original, record['sourceTree'])
            assert record['templateId'] == int(original.attrib['Id'])
            for source_name, normalized_name in [('Categories', 'categoryWords'), ('SemanticTags', 'semanticTagWords')]:
                source_words = list(original.find(source_name))
                assert len(source_words) == len(record[normalized_name])
                for original_word, word in zip(source_words, record[normalized_name]):
                    value = int(original_word.attrib['V'])
                    assert value == int(word['decimal']) == word['low32'] + (word['high32'] << 32)
                    words += 1
                    high_words += value > 0xffffffff
        connections = 0
        for index, (original, record) in enumerate(zip(abilities, catalog['abilities'])):
            assert record['sourceIndex'] == index and record['recordKey'] == f'ability/{index}'
            assert same_tree(original, record['sourceTree'])
            original_connections = list(original.findall('Connections/*'))
            assert len(original_connections) == len(record['connections'])
            for source, connection in zip(original_connections, record['connections']):
                assert connection['sourceId'] == int(source.attrib['SrcId'])
                assert connection['destinationId'] == int(source.attrib['DstId'])
            connections += len(original_connections)
        assert connections == 9713
    # Reject truncation/overflow and holes in word indexing at the import edge.
    rejected = 0
    for text in ['<M><e0 V="18446744073709551616"/></M>', '<M><e0 V="-1"/></M>', '<M><e1 V="1"/></M>']:
        try:
            mask_words(ET.fromstring(text))
        except ValueError:
            rejected += 1
    assert rejected == 3
    coverage = json.loads((target / 'coverage.json').read_text(encoding='utf-8'))
    assert not coverage['implementedExecutableNodeTypes']
    assert len(coverage['unsupportedExecutableNodeTypes']) == 183
    assert coverage['extendedCategoryTemplates'] == [152214]
    report = {'templatesRoundTrip': 698, 'abilitiesRoundTrip': 567,
        'orderedConnections': connections, 'maskWordsRoundTrip': words,
        'maskWordsAboveUInt32': high_words, 'maskGuardRejections': rejected,
        'duplicateNIdValuesPreserved': len(coverage['repeatedNIds']),
        'executableNodeTypesImplemented': 0, 'sourceSha256': source_hash,
        'catalogSha256': manifest['outputs']['normalized/catalog.json']['sha256'],
        'scope': 'Independent structural round trip, output hashes and overflow guards; no runtime card behavior.'}
    (ROOT / 'docs/evidence/beta-catalog-checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
