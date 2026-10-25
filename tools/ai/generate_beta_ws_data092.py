"""Static WS data for selected original profiles and validated deck bindings."""
import argparse, json
from pathlib import Path


def literal(value, kind):
    if kind=='bool':return 'true' if value else 'false'
    if kind=='string':return json.dumps(str(value),ensure_ascii=False)
    if kind=='float':return format(value,'.17f').rstrip('0').rstrip('.')+'.0f' if float(value).is_integer() else format(value,'.17f').rstrip('0')+'f'
    return str(value)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);args=parser.parse_args()
    data=json.loads((args.directory/'source-data.json').read_text('utf8'))
    fields={k:('float' if s['type'] in ('float','double') else 'bool' if s['type']=='bool' else 'int' if s['type']=='int' else 'string') for k,s in data['scalarSchema'].items()}
    lines=['// Generated from source-checked JS tables. Source profiles plus validated per-deck bindings.',
           '// Does not enable an AI difficulty. Handlers/search/replay must also be ported.',
           'struct SBetaOriginalSemantic { var id, usage, rounds : int; var weight : float; }',
           'struct SBetaOriginalAssociation { var kind, templateId, sourceHint, handlerId : int; }',
           'struct SBetaOriginalTemplate { var id, linkedTemplateId, placementOwn, placementEnemy, printedPower, typeMask, tierMask, tokens : int; var semanticTags, categories : array<int>; }',
           'class CBetaOriginalPersonality extends IScriptable {',
           '    public var profileName : string; public var semanticTags : array<SBetaOriginalSemantic>; public var associations : array<SBetaOriginalAssociation>;']
    lines += [f'    public var {k} : {kind};' for k,kind in fields.items()]
    lines += ['    public function Initialize(faction : int) : bool {','        switch(faction) {']
    lines += [f'        case {faction}: BetaOriginalProfile{i}(this); return true;' for i,faction in enumerate([2,4,8,16,32])]
    lines += ['        default: return false;', '        }', '    }']
    lines += ['    public function InitializeNamed(sourceProfile : string) : bool {', '        switch(sourceProfile) {']
    lines += [f'        case {literal(p["name"],"string")}: BetaOriginalProfile{i}(this); return true;' for i,p in enumerate(data['profiles'])]
    lines += ['        default: return false;', '        }', '    }',
              '    public function InitializeForDeck(preset : int, faction : int) : bool {',
              '        var sourceProfile : string; sourceProfile=BetaOriginalDeckProfile(preset);',
              '        if(sourceProfile!="")return InitializeNamed(sourceProfile);return Initialize(faction);', '    }', '}']
    lines += ['function BetaOriginalDeckProfile(preset : int) : string {', '    switch(preset) {']
    lines += [f'    case {b["presetId"]}: return {literal(b["profile"],"string")};' for b in data.get('deckBindings',[])]
    lines += ['    default: return "";', '    }', '}']
    for i,p in enumerate(data['profiles']):
        lines += [f'function BetaOriginalProfile{i}(p : CBetaOriginalPersonality) {{','    var tag : SBetaOriginalSemantic; var association : SBetaOriginalAssociation;',
                  '    p.profileName='+json.dumps(p['name'],ensure_ascii=False)+'; p.semanticTags.Clear(); p.associations.Clear();']
        lines += [f'    p.{k}={literal(p[k],kind)};' for k,kind in fields.items()]
        for t in p['semanticTags']:
            lines += [f'    tag.id={t["id"]}; tag.usage={t["usage"]}; tag.rounds={t["rounds"]}; tag.weight={literal(t["weight"],"float")}; p.semanticTags.PushBack(tag);']
        # Keep the four source list orders; instances are created per turn,
        # never shared between profile associations by the static dedup table.
        for kind,(key,associations) in enumerate(p['associations'].items(),1):
            lines += [f'    BetaOriginalProfile{i}Associations{kind}(p);']
        lines += ['}']
        for kind,(key,associations) in enumerate(p['associations'].items(),1):
            lines += [f'function BetaOriginalProfile{i}Associations{kind}(p : CBetaOriginalPersonality) {{','    var association : SBetaOriginalAssociation;']
            for a in associations:
                attr=a['attributes']
                lines += [f'    association.kind={kind}; association.templateId={int(attr["TemplateId"])}; association.sourceHint={int(attr.get("AIHIntId",1))}; association.handlerId={a["handlerDefinitionId"]}; p.associations.PushBack(association);']
            lines += ['}']
    templates=sorted(data['templates'].values(),key=lambda t:t['id']);groups=[templates[i:i+12] for i in range(0,len(templates),12)]
    lines += ['function BetaOriginalTemplate(id : int) : SBetaOriginalTemplate {','    var t : SBetaOriginalTemplate;']
    lines += [f'    if(id>={group[0]["id"]} && id<={group[-1]["id"]})return BetaOriginalTemplates{i}(id);' for i,group in enumerate(groups)]
    lines += ['    return t;', '}']
    for i,group in enumerate(groups):
        lines += [f'function BetaOriginalTemplates{i}(id : int) : SBetaOriginalTemplate {{','    var t : SBetaOriginalTemplate;','    switch(id) {']
        for t in group:
            placement=t.get('placement') or {'player':0,'opponent':0}
            lines += [f'    case {t["id"]}: t.id={t["id"]}; t.linkedTemplateId={t["linkedTemplateId"]}; t.placementOwn={placement["player"]}; t.placementEnemy={placement["opponent"]}; t.printedPower={t["power"]}; t.typeMask={t["type"]}; t.tierMask={t["tier"]}; t.tokens={t["tokens"]};']
            lines += ['        t.semanticTags.PushBack('+str(v)+');' for v in t['semanticTags']]
            lines += ['        t.categories.PushBack('+str(v)+');' for v in t['categories']]
            lines += ['        break;']
        lines += ['    }','    return t;','}']
    (args.directory/'betaOriginalData.ws').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
    if data.get('handlerDefinitions'):
        render_handlers(args.directory,data)
        render_hints(args.directory,data)
    print('Generated typed data:',len(fields),'scalars,',len(data['profiles']),'profiles,',len(templates),'templates')


def render_handlers(directory,data):
    settings={'CardGroup':'int','SemanticTagId':'int','TagsTokenType':'int','Location':'int','UnitOrEvent':'int','Health':'int','TemplateId':'int','MinRange':'int','MaxRange':'int',
              'Negate':'bool','SortOrder':'string','PlayerType':'string','EffectType':'string','SummationName':'string','LocationAction':'string','PowerLevel':'string','NumCards':'string','Destination':'string','WedgeType':'string'}
    definitions=data['handlerDefinitions'];groups=[definitions[i:i+10] for i in range(0,len(definitions),10)]
    lines=['// Generated normalized XML handler settings; int.TryParse defaults are already resolved.',
           'function BetaOriginalCreateHandler(id : int, owner : IScriptable) : CBetaOriginalHandler {','    var h : CBetaOriginalHandler;',
           '    h=new CBetaOriginalHandler in owner; h.Initialize();']
    lines += [f'    if(id>={g[0]["id"]} && id<={g[-1]["id"]}){{BetaOriginalHandlerData{i}(h,id);return h;}}' for i,g in enumerate(groups)]
    lines += ['    if(id==0){h.kind="Random";return h;}','    return NULL;','}']
    masks={'None':0,'One':1,'Two':2,'Three':4,'NotOne':6,'NotTwo':5,'NotThree':3,'All':7}
    for i,g in enumerate(groups):
        lines += [f'function BetaOriginalHandlerData{i}(h : CBetaOriginalHandler, id : int) {{','    var scoreEntry : SBetaOriginalSummationEntry;','    switch(id) {']
        for d in g:
            lines += [f'    case {d["id"]}: h.kind={literal(d["kind"],"string")}; h.propagate={literal(d["propagate"],"float")}; h.hasSheet={literal(d["hasSheet"],"bool")};']
            for k,v in d['settings'].items():
                assert k in settings,(d['id'],k)
                lines += [f'        h.{k}={literal(v,settings[k])};']
            lines += [f'        h.children.PushBack(BetaOriginalCreateHandler({child},h));' for child in d['children']]
            for e in d['entries']:
                lines += [f'        scoreEntry.weight={literal(e["weight"],"float")}; scoreEntry.scoring={literal(e["scoring"],"string")}; scoreEntry.rounds={masks.get(e["rounds"],7)}; h.entries.PushBack(scoreEntry);']
            lines += ['        break;']
        lines += ['    }','}']
    (directory/'betaOriginalHandlerData.ws').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')


def render_hints(directory,data):
    records=sorted(data['requestHints'].items(),key=lambda x:int(x[0]));groups=[records[i:i+12] for i in range(0,len(records),12)]
    lines=['// Exact source graph request node IDs and hints; phase mapping is handwritten.',
           'struct SBetaOriginalSourceHint { var node, sourceHint : int; var kind : string; }',
           'function BetaOriginalSourceRequests(source : int, out hints : array<SBetaOriginalSourceHint>) {','    hints.Clear();']
    lines += [f'    if(source>={g[0][0]} && source<={g[-1][0]}){{BetaOriginalSourceHints{i}(source,hints);return;}}' for i,g in enumerate(groups)]
    lines+=['}']
    for i,g in enumerate(groups):
        lines += [f'function BetaOriginalSourceHints{i}(source : int, out hints : array<SBetaOriginalSourceHint>) {{','    var h : SBetaOriginalSourceHint;','    switch(source) {']
        for template,requests in g:
            lines += [f'    case {template}:']
            lines += [f'        h.node={r["node"]};h.sourceHint={r["hint"]};h.kind={literal(r["kind"],"string")};hints.PushBack(h);' for r in requests]
            lines += ['        break;']
        lines += ['    }','}']
    lines += ['function BetaOriginalHasPlayCardsNode(source : int) : bool {','    switch(source) {']
    lines += [f'    case {tid}: return true;' for tid,record in data['requestTemplateInfo'].items() if record.get('hasPlayCardsNode')]
    lines += ['    }','    return false;','}']
    (directory/'betaOriginalRequestData.ws').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')


if __name__=='__main__':main()
