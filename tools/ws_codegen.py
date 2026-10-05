"""Keep generated WitcherScript lists below the REDkit parser stack budget."""
import re
from html import unescape

def localized_plain_text(value):
    """Presentation copy only; leave the canonical Beta catalogue untouched."""
    value = re.sub(r'<br\s*/?\s*>', '\n', value, flags=re.I)
    value = unescape(re.sub(r'<[^>]+>', '', value))
    return value.replace('\\r\\n', '\n').replace('\\n', '\n').replace('/n', '\n').replace('\r\n', '\n')

def bounded_helpers(lines):
    text='\n'.join(lines)
    # Large terminal-return switches overflow the native parser even with enough RAM.
    pattern=r'function (\w+)\(id : int\) : bool\s*\{\s*switch\s*\(id\)\s*\{((?:\s*case \d+: return true;)+)\s*\}\s*return false;\s*\}'
    def split(m):
        name=m[1];ids=re.findall(r'case (\d+):',m[2])
        if len(ids)<=100:return m[0]
        groups=[ids[i:i+100] for i in range(0,len(ids),100)]
        out=[f'function {name}(id : int) : bool','{','    return '+' || '.join(f'{name}Part{i}(id)' for i in range(len(groups)))+';','}']
        for i,group in enumerate(groups):out+=[f'function {name}Part{i}(id : int) : bool','{','    switch(id)','    {']+[f'    case {v}: return true;' for v in group]+['    }','    return false;','}']
        return '\n'.join(out)
    text=re.sub(pattern,split,text)
    pattern=r'function (\w+)\(out ids : array<int>\)\s*\{\s*(ids.Clear\(\);)?((?:\s*ids.PushBack\(\d+\);)+)\s*\}'
    def split_list(m):
        name=m[1];ids=re.findall(r'ids.PushBack\((\d+)\)',m[3])
        if len(ids)<=100:return m[0]
        groups=[ids[i:i+100] for i in range(0,len(ids),100)]
        out=[f'function {name}(out ids : array<int>)','{']
        if m[2]:out+=['    ids.Clear();']
        out+=[f'    {name}Part{i}(ids);' for i in range(len(groups))]+['}']
        for i,group in enumerate(groups):out+=[f'function {name}Part{i}(out ids : array<int>)','{']+[f'    ids.PushBack({v});' for v in group]+['}']
        return '\n'.join(out)
    text=re.sub(pattern,split_list,text)
    # WitcherScript reports a script error (with an expensive stack trace) for
    # an unmatched switch without default, even if the function returns below.
    # Generated membership tables deliberately receive IDs they do not contain.
    # Scan tokens rather than braces in localized quoted descriptions/comments.
    tokens = re.finditer(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/|\b(?:switch|default)\b|[{}]', text)
    stack = []
    pending_switch = False
    insertions = []
    for token in tokens:
        value = token[0]
        if value.startswith(('"', '//', '/*')):
            continue
        if value == 'switch':
            pending_switch = True
        elif value == '{':
            stack.append(dict(is_switch=pending_switch, has_default=False))
            pending_switch = False
        elif value == 'default':
            for frame in reversed(stack):
                if frame['is_switch']:
                    frame['has_default'] = True
                    break
        elif value == '}':
            frame = stack.pop()
            if frame['is_switch'] and not frame['has_default']:
                line_start = text.rfind('\n', 0, token.start()) + 1
                indent = text[line_start:token.start()]
                if indent.strip():
                    insertions.append((token.start(), ' default: break; '))
                else:
                    insertions.append((line_start, indent + '    default: break;\n'))
    for position, value in reversed(insertions):
        text = text[:position] + value + text[position:]
    return text.splitlines()
