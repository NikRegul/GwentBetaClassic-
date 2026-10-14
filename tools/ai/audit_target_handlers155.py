"""Audit request-opening branches against their continuation handlers."""
import json
import sys
from pathlib import Path
import gen_clone

ROOT=Path(__file__).resolve().parents[2]

def walk(node):
    if isinstance(node,dict):
        yield node
        for value in node.values():yield from walk(value)
    elif isinstance(node,(list,tuple)):
        for value in node:yield from walk(value)

def values(node,variable):
    result=set()
    for item in walk(node):
        if item.get('kind')!='bin' or item.get('op')!='==':continue
        left,right=item['left'],item['right']
        if left.get('kind')=='id' and left.get('name')==variable and right.get('kind')=='lit':
            try:result.add(int(right['v']))
            except ValueError:pass
        if left.get('kind')=='member' and left.get('name')=='specialMode' and variable=='mode' and right.get('kind')=='lit':
            try:result.add(int(right['v']))
            except ValueError:pass
    return result

def main():
    program=gen_clone.program();report=[]
    for cls in program.classes.values():
        methods={m.name:m.body for m in cls.methods}
        if 'Played' not in methods or 'Select' not in methods:continue
        def closure(body,seen=None):
            seen=set() if seen is None else seen
            nodes=list(walk(body));result=list(nodes)
            for node in nodes:
                if node.get('kind')=='call' and node.get('target') is None and node['name'] in methods and node['name'] not in seen:
                    seen.add(node['name']);result+=closure(methods[node['name']],seen)
            return result
        select_nodes=closure(methods['Select'])
        played_nodes=closure(methods['Played'])
        for variable in ('id','mode'):
            opened=set();row_targets=set()
            for node in played_nodes:
                if node.get('kind')!='if':continue
                branches=values(node['cond'],variable)
                if not branches:continue
                called=closure(node['then'])
                requests=[x for x in called if x.get('kind')=='call' and x.get('name')=='MonsterRequest']
                if requests:opened.update(branches)
                if 'Row' in methods and requests and all(len(x['args'])>2 and x['args'][2].get('kind')=='lit' and x['args'][2].get('v')=='3' for x in requests):row_targets.update(branches)
            handled=values(select_nodes,variable)
            report.append(dict(handlerClass=cls.name,selector=variable,requestBranches=sorted(opened),rowBranches=sorted(row_targets),
                               continuationBranches=sorted(handled),review=sorted(opened-handled-row_targets)))
    out=ROOT/'docs/evidence/target-handler-audit155.json'
    passed=not any(r['review'] for r in report)
    out.write_text(json.dumps(dict(classes=report,passed=passed,scope='Explicit request branches and reachable own-class continuation helpers; dynamic routing requires semantic review.'),indent=2)+'\n','utf8')
    print(json.dumps([r for r in report if r['requestBranches']],indent=2))
    if '--strict' in sys.argv and not passed:raise SystemExit('Unreviewed request continuation branches')

if __name__=='__main__':main()
