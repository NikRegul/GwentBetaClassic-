"""WitcherScript (BetaGwent battle subset) -> JavaScript transpiler for headless self-play.

Value semantics of WS structs/arrays are reproduced with explicit copies at
assignment/argument/return of lvalues; `out` parameters are boxed.
"""
from pathlib import Path
import re, sys, json

# ---------------------------------------------------------------- lexer
TOK = re.compile(r'''
 (?P<ws>\s+|//[^\n]*|/\*.*?\*/)
|(?P<float>\d+\.\d*f?|\d+f\b|\.\d+f?)
|(?P<hex>0[xX][0-9a-fA-F]+)
|(?P<int>\d+)
|(?P<str>"(?:\\.|[^"\\])*")
|(?P<name>'(?:\\.|[^'\\])*')
|(?P<id>[A-Za-z_]\w*)
|(?P<op>==|!=|<=|>=|&&|\|\||\+=|-=|\*=|/=|%=|\|=|&=|\^=|\+\+|--|[-+*/%<>=!&|^~(){}\[\];:,.?@])
''', re.S | re.X)

class Tok:
    __slots__ = ('k', 'v', 'pos')
    def __init__(s, k, v, pos): s.k, s.v, s.pos = k, v, pos
    def __repr__(s): return f'{s.k}:{s.v}'

def lex(src):
    out = []; i = 0
    while i < len(src):
        m = TOK.match(src, i)
        if not m: raise SyntaxError('lex error at %r' % src[i:i+40])
        k = m.lastgroup; i = m.end()
        if k == 'ws': continue
        out.append(Tok(k, m.group(k), m.start()))
    out.append(Tok('eof', '', len(src)))
    return out

# ---------------------------------------------------------------- AST helpers
class N(dict):
    __getattr__ = dict.get

MODS = {'private', 'public', 'protected', 'final', 'latent', 'timer', 'exec', 'quest', 'storyscene',
        'cleanup', 'entry', 'reward', 'import', 'saved', 'editable', 'inlined', 'const', 'abstract', 'statemachine'}

class Parser:
    def __init__(s, toks, types):
        s.t = toks; s.i = 0; s.types = types
    def peek(s, o=0): return s.t[s.i + o]
    def at(s, v, o=0): t = s.t[s.i + o]; return t.v == v and t.k in ('op', 'id')
    def next(s): t = s.t[s.i]; s.i += 1; return t
    def expect(s, v):
        t = s.next()
        if t.v != v: raise SyntaxError(f'expected {v} got {t.v} near {s.ctx()}')
        return t
    def ident(s):
        t = s.next()
        if t.k != 'id': raise SyntaxError(f'expected identifier got {t.v} near {s.ctx()}')
        return t.v
    def ctx(s): return ' '.join(x.v for x in s.t[max(0, s.i-8):s.i+8])

    def type_(s):
        n = s.ident()
        if n == 'array':
            s.expect('<'); inner = s.type_(); s.expect('>')
            return ('array', inner)
        return n

    # ---- top level
    def decl(s):
        mods = set()
        while s.peek().k == 'id' and s.peek().v in MODS: mods.add(s.next().v)
        t = s.peek()
        if t.v == 'enum': return s.enum()
        if t.v == 'struct': return s.struct()
        if t.v == 'class': return s.klass(mods)
        if t.v == 'function': return s.function(mods)
        raise SyntaxError('unknown decl ' + s.ctx())

    def enum(s):
        s.expect('enum'); name = s.ident(); s.expect('{'); items = []; val = 0
        while not s.at('}'):
            n = s.ident()
            if s.at('='):
                s.next(); neg = 1
                if s.at('-'): s.next(); neg = -1
                tk = s.next(); val = neg * int(tk.v, 0)
            items.append((n, val)); val += 1
            if s.at(','): s.next()
        s.expect('}')
        if s.at(';'): s.next()
        return N(kind='enum', name=name, members=items)

    def vardecl(s):
        s.expect('var'); names = [s.ident()]
        while s.at(','): s.next(); names.append(s.ident())
        s.expect(':'); t = s.type_(); s.expect(';')
        return names, t

    def struct(s):
        s.expect('struct'); name = s.ident(); s.expect('{'); fields = []; defaults = {}
        while not s.at('}'):
            while s.peek().v in MODS: s.next()
            if s.at('var'):
                names, t = s.vardecl(); fields += [(n, t) for n in names]
            elif s.at('default'):
                s.next(); n = s.ident(); s.expect('='); defaults[n] = s.expr(); s.expect(';')
            else: raise SyntaxError('struct member ' + s.ctx())
        s.expect('}')
        if s.at(';'): s.next()
        return N(kind='struct', name=name, fields=fields, defaults=defaults)

    def klass(s, mods):
        s.expect('class'); name = s.ident(); base = None
        if s.at('extends'): s.next(); base = s.ident()
        s.expect('{'); fields = []; methods = []; defaults = {}
        while not s.at('}'):
            m = set()
            while s.peek().k == 'id' and s.peek().v in MODS: m.add(s.next().v)
            if s.at('var'):
                names, t = s.vardecl(); fields += [(n, t) for n in names]
            elif s.at('default'):
                s.next(); n = s.ident(); s.expect('='); defaults[n] = s.expr(); s.expect(';')
            elif s.at('function'):
                methods.append(s.function(m))
            elif s.at('event'):
                s.next(); s.function_rest(m)  # discard
            else: raise SyntaxError('class member ' + s.ctx())
        s.expect('}')
        if s.at(';'): s.next()
        return N(kind='class', name=name, base=base, fields=fields, methods=methods, defaults=defaults, abstract='abstract' in mods)

    def function(s, mods):
        s.expect('function'); return s.function_rest(mods)

    def function_rest(s, mods):
        name = s.ident(); s.expect('('); params = []
        while not s.at(')'):
            pm = set()
            while s.peek().v in ('out', 'optional'): pm.add(s.next().v)
            pn = s.ident(); s.expect(':'); pt = s.type_()
            params.append(N(name=pn, type=pt, out='out' in pm, optional='optional' in pm))
            if s.at(','): s.next()
        s.expect(')'); ret = None
        if s.at(':'): s.next(); ret = s.type_()
        body = None
        if s.at(';'): s.next()
        else: body = s.block()
        return N(kind='function', name=name, params=params, ret=ret, body=body, mods=mods)

    # ---- statements
    def block(s):
        s.expect('{'); st = []
        while not s.at('}'): st.append(s.stmt())
        s.expect('}'); return N(kind='block', body=st)

    def stmt(s):
        t = s.peek()
        if t.k == 'op' and t.v == '{': return s.block()
        if t.k == 'op' and t.v == ';': s.next(); return N(kind='empty')
        if t.k == 'id':
            v = t.v
            if v == 'var':
                names, ty = s.vardecl(); return N(kind='var', names=names, type=ty)
            if v == 'if':
                s.next(); s.expect('('); c = s.expr(); s.expect(')'); a = s.stmt(); b = None
                if s.at('else'): s.next(); b = s.stmt()
                return N(kind='if', cond=c, then=a, els=b)
            if v == 'while':
                s.next(); s.expect('('); c = s.expr(); s.expect(')'); return N(kind='while', cond=c, body=s.stmt())
            if v == 'do':
                s.next(); b = s.stmt(); s.expect('while'); s.expect('('); c = s.expr(); s.expect(')')
                if s.at(';'): s.next()
                return N(kind='do', cond=c, body=b)
            if v == 'for':
                s.next(); s.expect('('); a = None if s.at(';') else s.expr(); s.expect(';')
                c = None if s.at(';') else s.expr(); s.expect(';')
                d = None if s.at(')') else s.expr(); s.expect(')')
                return N(kind='for', init=a, cond=c, step=d, body=s.stmt())
            if v == 'switch':
                s.next(); s.expect('('); e = s.expr(); s.expect(')'); s.expect('{'); cases = []
                while not s.at('}'):
                    if s.at('case'):
                        s.next(); lab = s.expr(); s.expect(':'); cases.append(['case', lab, []])
                    elif s.at('default'):
                        s.next(); s.expect(':'); cases.append(['default', None, []])
                    else:
                        if not cases: raise SyntaxError('switch body ' + s.ctx())
                        cases[-1][2].append(s.stmt())
                s.expect('}'); return N(kind='switch', expr=e, cases=cases)
            if v == 'break': s.next(); s.expect(';'); return N(kind='break')
            if v == 'continue': s.next(); s.expect(';'); return N(kind='continue')
            if v == 'return':
                s.next(); e = None
                if not s.at(';'): e = s.expr()
                s.expect(';'); return N(kind='return', expr=e)
        e = s.expr(); s.expect(';'); return N(kind='expr', expr=e)

    # ---- expressions
    ASSIGN = ('=', '+=', '-=', '*=', '/=', '%=', '|=', '&=', '^=')
    BIN = [('||',), ('&&',), ('|',), ('^',), ('&',), ('==', '!='), ('<', '>', '<=', '>='), ('+', '-'), ('*', '/', '%')]

    def expr(s):
        left = s.binary(0)
        if s.peek().k == 'op' and s.peek().v in s.ASSIGN:
            op = s.next().v; right = s.expr()
            return N(kind='assign', op=op, left=left, right=right)
        if s.at('?'):
            s.next(); a = s.expr(); s.expect(':'); b = s.expr()
            return N(kind='cond', cond=left, a=a, b=b)
        return left

    def binary(s, level):
        if level == len(s.BIN): return s.unary()
        left = s.binary(level + 1)
        while s.peek().k == 'op' and s.peek().v in s.BIN[level]:
            op = s.next().v; right = s.binary(level + 1)
            left = N(kind='bin', op=op, left=left, right=right)
        return left

    def unary(s):
        t = s.peek()
        if t.k == 'op' and t.v in ('!', '-', '~', '+'):
            s.next(); return N(kind='un', op=t.v, e=s.unary())
        if t.k == 'op' and t.v in ('++', '--'):
            s.next(); return N(kind='preinc', op=t.v, e=s.unary())
        if t.k == 'op' and t.v == '(' and s.peek(1).k == 'id' and s.peek(2).v == ')' and s.peek(1).v in s.types:
            nt = s.peek(3)
            if nt.k in ('id', 'int', 'float', 'hex', 'str', 'name') or nt.v in ('(', '!', '-'):
                s.next(); ty = s.next().v; s.next()
                return N(kind='cast', type=ty, e=s.unary())
        return s.postfix(s.primary())

    def postfix(s, e):
        while True:
            if s.at('.'):
                s.next(); n = s.ident()
                if s.at('('): e = N(kind='call', target=e, name=n, args=s.args())
                else: e = N(kind='member', obj=e, name=n)
            elif s.at('['):
                s.next(); i = s.expr(); s.expect(']'); e = N(kind='index', obj=e, idx=i)
            elif s.peek().k == 'op' and s.peek().v in ('++', '--'):
                e = N(kind='postinc', op=s.next().v, e=e)
            else: return e

    def args(s):
        s.expect('('); a = []
        while not s.at(')'):
            a.append(s.expr())
            if s.at(','): s.next()
        s.expect(')'); return a

    def primary(s):
        t = s.next()
        if t.k == 'int': return N(kind='lit', v=t.v, type='int')
        if t.k == 'hex':
            v = int(t.v, 16)
            if v >= 2**31: v -= 2**32
            return N(kind='lit', v=str(v), type='int')
        if t.k == 'float': return N(kind='lit', v=t.v.rstrip('f') or '0', type='float')
        if t.k == 'str': return N(kind='lit', v=t.v, type='string')
        if t.k == 'name': return N(kind='lit', v=json.dumps(t.v[1:-1]), type='string')
        if t.k == 'op' and t.v == '(':
            e = s.expr(); s.expect(')'); return N(kind='paren', e=e)
        if t.k == 'id':
            if t.v in ('true', 'false'): return N(kind='lit', v=t.v, type='bool')
            if t.v == 'NULL': return N(kind='lit', v='null', type='null')
            if t.v == 'this': return N(kind='this')
            if t.v == 'new':
                cls = s.ident()
                if s.at('in'): s.next(); s.unary()
                return N(kind='new', cls=cls)
            if s.at('('): return N(kind='call', target=None, name=t.v, args=s.args())
            return N(kind='id', name=t.v)
        raise SyntaxError('primary ' + s.ctx())

# ---------------------------------------------------------------- program model
def split_blocks(src):
    """Split top-level declarations by brace depth (strings/comments aware)."""
    toks = lex(src); out = []; start = 0; depth = 0
    for i, t in enumerate(toks):
        if t.k == 'op' and t.v == '{': depth += 1
        elif t.k == 'op' and t.v == '}':
            depth -= 1
            if depth == 0:
                j = i + 1
                if toks[j].v == ';': j += 1
                out.append(toks[start:j]); start = j
    if toks[start].k != 'eof': raise SyntaxError('tail ' + ' '.join(x.v for x in toks[start:start+10]))
    return out

def head_name(block):
    i = 0
    while block[i].v in MODS: i += 1
    return block[i].v, block[i + 1].v

JS_RESERVED = {'delete', 'with', 'yield', 'let', 'typeof', 'void', 'instanceof', 'export', 'package', 'interface',
               'arguments', 'eval', 'static', 'await', 'enum', 'implements', 'Math', 'Array', 'Object', 'constructor',
               'prototype', 'undefined', 'NaN', 'Infinity', 'name', 'length', 'toString', 'valueOf', 'in', 'of', 'super', 'catch', 'try', 'throw', 'finally', 'debugger', 'import', 'const'}

def jsname(n): return '$' + n if n in JS_RESERVED else n

PRIM = {'int', 'float', 'bool', 'string', 'name', 'byte', 'Uint64', 'EngineTime', 'StringAnsi'}

class Program:
    def __init__(s):
        s.enums = {}; s.enum_vals = {}; s.structs = {}; s.classes = {}; s.functions = {}
        s.order = []

    def add(s, d):
        if d.kind == 'enum':
            s.enums[d.name] = d
            for n, v in d.members: s.enum_vals[n] = v
        elif d.kind == 'struct': s.structs[d.name] = d
        elif d.kind == 'class': s.classes[d.name] = d
        elif d.kind == 'function': s.functions[d.name] = d
        s.order.append(d)

    # type utils
    def norm(s, t):
        if isinstance(t, tuple): return ('array', s.norm(t[1]))
        if t in s.enums or t in ('byte',): return 'int'
        if t == 'name': return 'string'
        return t
    def is_value(s, t):
        t = s.norm(t)
        return isinstance(t, tuple) or t in s.structs
    def init(s, t):
        t = s.norm(t)
        if isinstance(t, tuple): return '[]'
        if t in ('int', 'float'): return '0'
        if t == 'bool': return 'false'
        if t == 'string': return '""'
        if t in s.structs: return f'new {t}()'
        return 'null'
    def field_type(s, owner, n):
        owner = s.norm(owner)
        if owner in s.structs:
            for fn, ft in s.structs[owner].fields:
                if fn == n: return s.norm(ft)
            return None
        c = s.classes.get(owner)
        while c:
            for fn, ft in c.fields:
                if fn == n: return s.norm(ft)
            c = s.classes.get(c.base)
        return None
    def method(s, owner, n):
        c = s.classes.get(s.norm(owner) if isinstance(owner, str) else None)
        while c:
            for m in c.methods:
                if m.name == n: return m
            c = s.classes.get(c.base)
        return None
    def is_member(s, owner, n):
        return s.field_type(owner, n) is not None or s.method(owner, n) is not None

# ---------------------------------------------------------------- emitter
class Emitter:
    def __init__(s, prog):
        s.p = prog; s.lines = []

    def fn_ctx(s, f, cls):
        s.cls = cls; s.locals = {}; s.outs = set(); s.tmp = 0; s.tmpmax = 0
        for p in f.params:
            s.locals[p.name] = s.p.norm(p.type)
            if p.out: s.outs.add(p.name)
        s.ret = s.p.norm(f.ret) if f.ret else None; s.params = {p.name for p in f.params}
        # WS: locals are function-scoped; collect all var decls up front
        def walk(st):
            if st is None: return
            k = st.kind
            if k == 'var':
                for n in st.names: s.locals[n] = s.p.norm(st.type)
            elif k == 'block':
                for x in st.body: walk(x)
            elif k == 'if': walk(st.then); walk(st.els)
            elif k in ('while', 'do', 'for'): walk(st.body)
            elif k == 'switch':
                for c in st.cases:
                    for x in c[2]: walk(x)
        walk(f.body)

    # ---- typing
    def typeof(s, e):
        k = e.kind
        if k == 'lit': return e.type
        if k == 'paren': return s.typeof(e.e)
        if k == 'cast': return s.p.norm(e.type)
        if k == 'this': return s.cls
        if k == 'new': return e.cls
        if k == 'id':
            n = e.name
            if n in s.locals: return s.locals[n]
            if s.cls and s.p.field_type(s.cls, n): return s.p.field_type(s.cls, n)
            if n in s.p.enum_vals: return 'int'
            return None
        if k == 'member':
            ot = s.typeof(e.obj)
            return s.p.field_type(ot, e.name) if ot else None
        if k == 'index':
            ot = s.typeof(e.obj)
            return ot[1] if isinstance(ot, tuple) else None
        if k == 'call':
            if e.target is None:
                if s.cls:
                    m = s.p.method(s.cls, e.name)
                    if m: return s.p.norm(m.ret) if m.ret else None
                f = s.p.functions.get(e.name)
                if f: return s.p.norm(f.ret) if f.ret else None
                return {'Max': 'int', 'Min': 'int', 'Abs': 'int', 'FloorF': 'int', 'RandRange': 'int', 'Clamp': 'int',
                        'MaxF': 'float', 'MinF': 'float', 'AbsF': 'float', 'RoundF': 'int', 'CeilF': 'int'}.get(e.name)
            ot = s.typeof(e.target)
            if isinstance(ot, tuple):
                return {'Size': 'int', 'Contains': 'bool', 'FindFirst': 'int', 'PopBack': ot[1], 'Last': ot[1]}.get(e.name)
            m = s.p.method(ot, e.name) if ot else None
            return s.p.norm(m.ret) if m and m.ret else None
        if k == 'bin':
            if e.op in ('==', '!=', '<', '>', '<=', '>=', '&&', '||'): return 'bool'
            a, b = s.typeof(e.left), s.typeof(e.right)
            if e.op == '+' and ('string' in (a, b)): return 'string'
            if 'float' in (a, b): return 'float'
            if a == 'int' and b == 'int': return 'int'
            if e.op in ('|', '&', '^'): return 'int'
            return a or b
        if k == 'un':
            return 'bool' if e.op == '!' else s.typeof(e.e)
        if k in ('postinc', 'preinc'): return s.typeof(e.e)
        if k == 'assign': return s.typeof(e.left)
        if k == 'cond': return s.typeof(e.a)
        return None

    def is_lvalue(s, e):
        if e.kind == 'paren': return s.is_lvalue(e.e)
        return e.kind in ('id', 'member', 'index', 'this')

    def copy_if(s, code, e, t):
        if t is not None and s.p.is_value(t) and s.is_lvalue(e): return f'__cp({code})'
        if t is None and s.is_lvalue(e) and e.kind != 'this':
            return f'__cpu({code})'  # unknown type: runtime check
        return code

    # ---- expressions
    def ex(s, e):
        k = e.kind
        if k == 'lit': return e.v
        if k == 'paren': return '(' + s.ex(e.e) + ')'
        if k == 'this': return 'this'
        if k == 'new': return f'new {e.cls}()'
        if k == 'cast':
            t = s.p.norm(e.type); inner = s.ex(e.e)
            if t == 'int': return f'Math.trunc({inner})'
            if t in ('float', 'bool', 'string'): return f'({inner})'
            if t in s.p.classes: return f'__cast({inner},{t})'
            return f'({inner})'
        if k == 'id':
            n = e.name
            if n in s.locals: return jsname(n) + ('.v' if n in s.outs else '')
            if s.cls and s.p.is_member(s.cls, n): return 'this.' + jsname(n)
            if n in s.p.enum_vals: return str(s.p.enum_vals[n])
            return jsname(n)
        if k == 'member': return s.ex(e.obj) + '.' + jsname(e.name)
        if k == 'index': return s.ex(e.obj) + '[' + s.ex(e.idx) + ']'
        if k == 'call': return s.call(e)
        if k == 'un':
            inner = s.ex(e.e)
            if e.op == '!': return '!' + inner
            return e.op + inner
        if k == 'preinc': return e.op + s.ex(e.e)
        if k == 'postinc': return s.ex(e.e) + e.op
        if k == 'cond': return f'({s.ex(e.cond)}?{s.ex(e.a)}:{s.ex(e.b)})'
        if k == 'bin':
            a, b = s.ex(e.left), s.ex(e.right)
            ta, tb = s.typeof(e.left), s.typeof(e.right)
            ints = ta in ('int', None) and tb in ('int', None) and 'float' not in (ta, tb)
            if e.op == '/' and ints and not (ta is None and tb is None): return f'__idiv({a},{b})'
            if e.op == '/' and ta is None and tb is None: return f'__idiv({a},{b})'
            if e.op == '*' and ta == 'int' and tb == 'int': return f'Math.imul({a},{b})'
            if e.op == '==' : return f'({a}=={b})'
            if e.op == '!=' : return f'({a}!={b})'
            return f'({a}{e.op}{b})'
        if k == 'assign': return s.assign(e)
        raise ValueError('expr ' + k)

    def assign(s, e):
        L = s.ex(e.left); tl = s.typeof(e.left)
        if e.op == '=':
            return f'{L}={s.copy_if(s.ex(e.right), e.right, tl if tl is not None else s.typeof(e.right))}'
        op = e.op[0]; R = s.ex(e.right); tr = s.typeof(e.right)
        if op == '/' and tl == 'int': return f'{L}=__idiv({L},{R})'
        if op == '*' and tl == 'int' and tr == 'int': return f'{L}=Math.imul({L},{R})'
        return f'{L}{e.op}{R}'

    def call(s, e):
        args = e.args
        if e.target is not None:
            tt = s.typeof(e.target); obj = s.ex(e.target)
            if isinstance(tt, tuple):
                el = tt[1]
                if e.name == 'Resize':
                    return f'{obj}.Resize({s.ex(args[0])},()=>{s.p.init(el)})'
                if e.name in ('PushBack', 'Insert'):
                    conv = [s.ex(a) for a in args]
                    conv[-1] = s.copy_if(conv[-1], args[-1], el)
                    return f'{obj}.{e.name}({",".join(conv)})'
                return f'{obj}.{e.name}({",".join(s.ex(a) for a in args)})'
            f = s.p.method(tt, e.name) if tt else None
            if f is None and tt is None:
                # unknown receiver type: search unique method among classes
                cands = [m for c in s.p.classes.values() for m in c.methods if m.name == e.name]
                f = cands[0] if cands and all(len(c.params) == len(cands[0].params) and [p.out for p in c.params] == [p.out for p in cands[0].params] for c in cands) else None
                if f is None and cands: raise ValueError(f'ambiguous method {e.name} receiver {obj}')
            return s.invoke(f, f'{obj}.{jsname(e.name)}', args)
        n = e.name
        if s.cls and s.p.method(s.cls, n):
            return s.invoke(s.p.method(s.cls, n), 'this.' + jsname(n), args)
        f = s.p.functions.get(n)
        return s.invoke(f, jsname(n), args)

    def invoke(s, f, callee, args):
        if f is None:
            return f'{callee}({",".join(s.ex(a) for a in args)})'
        conv = []; outs = []
        for i, a in enumerate(args):
            p = f.params[i] if i < len(f.params) else None
            if p is not None and p.out:
                s.tmp += 1; s.tmpmax = max(s.tmpmax, s.tmp); t = f'__o{s.tmp}'
                outs.append((t, a)); conv.append(t)
            else:
                code = s.ex(a)
                if p is not None and p.name in (f.mut if f.mut is not None else {p.name}): code = s.copy_if(code, a, s.p.norm(p.type))
                conv.append(code)
        call = f'{callee}({",".join(conv)})'
        if not outs: return call
        s.tmp += 1; s.tmpmax = max(s.tmpmax, s.tmp); r = f'__o{s.tmp}'
        pre = ','.join(f'{t}={{v:{s.ex(a)}}}' for t, a in outs)
        post = ','.join(f'{s.ex(a)}={t}.v' for t, a in outs)
        return f'({pre},{r}={call},{post},{r})'

    # ---- statements
    def st(s, x, ind):
        p = '  ' * ind; k = x.kind; L = s.lines
        if k == 'block':
            for y in x.body: s.st(y, ind)
        elif k == 'empty' or k == 'var': pass
        elif k == 'expr': L.append(p + s.ex(x.expr) + ';')
        elif k == 'if':
            L.append(p + f'if({s.ex(x.cond)}){{'); s.st(x.then, ind + 1)
            if x.els: L.append(p + '}else{'); s.st(x.els, ind + 1)
            L.append(p + '}')
        elif k == 'while':
            L.append(p + f'while({s.ex(x.cond)}){{'); s.st(x.body, ind + 1); L.append(p + '}')
        elif k == 'do':
            L.append(p + 'do{'); s.st(x.body, ind + 1); L.append(p + f'}}while({s.ex(x.cond)});')
        elif k == 'for':
            a = s.ex(x.init) if x.init else ''; c = s.ex(x.cond) if x.cond else ''; d = s.ex(x.step) if x.step else ''
            L.append(p + f'for({a};{c};{d}){{'); s.st(x.body, ind + 1); L.append(p + '}')
        elif k == 'switch':
            L.append(p + f'switch({s.ex(x.expr)}){{')
            for c in x.cases:
                L.append(p + (f' case {s.ex(c[1])}:' if c[0] == 'case' else ' default:') + '{')
                for y in c[2]: s.st(y, ind + 1)
                L.append(p + ' }')
            L.append(p + '}')
        elif k == 'break': L.append(p + 'break;')
        elif k == 'continue': L.append(p + 'continue;')
        elif k == 'return':
            if x.expr is None: L.append(p + 'return;')
            else:
                e = x.expr
                while e.kind == 'paren': e = e.e
                plain_local = e.kind == 'id' and e.name in s.locals and e.name not in s.params
                L.append(p + 'return ' + (s.ex(x.expr) if plain_local else s.copy_if(s.ex(x.expr), x.expr, s.ret)) + ';')
        else: raise ValueError(k)

    def function(s, f, cls, method):
        s.fn_ctx(f, cls)
        params = []
        for p in f.params:
            if p.out: params.append(jsname(p.name))
            elif p.optional: params.append(f'{jsname(p.name)}={s.p.init(p.type)}')
            else: params.append(jsname(p.name))
        head = (f'{jsname(f.name)}(' if method else f'function {jsname(f.name)}(') + ','.join(params) + '){'
        start = len(s.lines); s.lines.append(head)
        for p in f.params:
            if p.out: s.lines.append(f'  if({jsname(p.name)}===undefined){jsname(p.name)}={{v:{s.p.init(p.type)}}};')
        pnames = {p.name for p in f.params}
        decl = [f'{jsname(n)}={s.p.init(t)}' for n, t in s.locals.items() if n not in pnames]
        decl_index = len(s.lines); s.lines.append('')
        if f.body: s.st(f.body, 1)
        tmps = [f'__o{i}' for i in range(1, s.tmpmax + 1)]
        s.lines[decl_index] = ('  let ' + ','.join(decl + tmps) + ';') if decl or tmps else ''
        s.lines.append('}')

    def program(s):
        P = s.p; L = s.lines
        for d in P.order:
            if d.kind == 'struct':
                L.append(f'class {d.name}{{constructor(){{')
                for n, t in d.fields:
                    v = s.ex_default(d.defaults.get(n)) if n in d.defaults else P.init(t)
                    L.append(f'  this.{jsname(n)}={v};')
                L.append('}}')
                L.append(f'{d.name}.prototype.__copy=function(){{const o=new {d.name}();' +
                         ''.join(f'o.{jsname(n)}=' + ((f'this.{jsname(n)}.__copy()' if P.norm(t) in P.structs else f'__cp(this.{jsname(n)})') if P.is_value(t) else f'this.{jsname(n)}') + ';' for n, t in d.fields) + 'return o;};')
        done = set()
        def emit_class(c):
            if c.name in done: return
            if c.base and c.base in P.classes: emit_class(P.classes[c.base])
            done.add(c.name)
            base = c.base if c.base in P.classes else 'IScriptable'
            L.append(f'class {c.name} extends {base}{{')
            L.append('constructor(){super();')
            for n, t in c.fields:
                v = s.ex_default(c.defaults.get(n)) if n in c.defaults else P.init(t)
                L.append(f'  this.{jsname(n)}={v};')
            for n, v in c.defaults.items():
                if not any(n == fn for fn, _ in c.fields): L.append(f'  this.{jsname(n)}={s.ex_default(v)};')
            L.append('}')
            for m in c.methods:
                if m.body is None: continue
                s.function(m, c.name, True)
            L.append('}')
        for d in P.order:
            if d.kind == 'class': emit_class(d)
        for d in P.order:
            if d.kind == 'function' and d.body is not None: s.function(d, None, False)
        return '\n'.join(L)

    def ex_default(s, e):
        s.cls = None; s.locals = {}; s.outs = set(); return s.ex(e)

MUTATORS = {'PushBack', 'Clear', 'Erase', 'EraseFast', 'Insert', 'Resize', 'PopBack', 'Remove', 'Grow'}
def mutated_params(prog, f):
    """Names of value-type params the body may modify (needs a defensive copy at call sites)."""
    names = {p.name for p in f.params if not p.out}
    hit = set()
    def root(e):
        while e is not None and e.kind in ('member', 'index', 'paren'):
            e = e.obj if e.kind != 'paren' else e.e
        return e.name if e is not None and e.kind == 'id' else None
    def ex(e):
        if e is None or not isinstance(e, dict): return
        k = e.kind
        if k == 'assign' or k in ('preinc', 'postinc'):
            r = root(e.left if k == 'assign' else e.e)
            if r in names: hit.add(r)
        if k == 'call':
            if e.target is not None:
                r = root(e.target)
                if r in names and e.name in MUTATORS: hit.add(r)
            # passing a param (or part of it) to another function: conservatively mutated if that slot is out
            callee = prog.functions.get(e.name) if e.target is None else None
            cands = [callee] if callee else [m for c in prog.classes.values() for m in c.methods if m.name == e.name]
            for i, a in enumerate(e.args):
                if any(c and i < len(c.params) and c.params[i].out for c in cands):
                    r = root(a)
                    if r in names: hit.add(r)
        for v in e.values():
            if isinstance(v, dict): ex(v)
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, dict): ex(x)
    def st(x):
        if x is None: return
        for v in x.values():
            if isinstance(v, dict):
                if v.get('kind') in ('block','if','while','do','for','switch','expr','return','var','empty','break','continue'): st(v)
                else: ex(v)
            elif isinstance(v, list):
                for y in v:
                    if isinstance(y, dict): st(y) if y.get('kind') in ('block','if','while','do','for','switch','expr','return','var','empty','break','continue') else ex(y)
                    elif isinstance(y, list):
                        for z in y:
                            if isinstance(z, dict): st(z) if z.get('kind') in ('block','if','while','do','for','switch','expr','return','var','empty','break','continue') else ex(z)
                            elif isinstance(z, list):
                                for w in z:
                                    if isinstance(w, dict): st(w)
    st(f.body)
    return hit

def build(files, extra_struct_files, excluded_functions=()):
    srcs = [Path(f).read_text(encoding='utf-8-sig') for f in files]
    extra = [Path(f).read_text(encoding='utf-8-sig') for f in extra_struct_files]
    blocks = []
    for src in srcs: blocks += split_blocks(src)
    known = {head_name(b)[1] for b in blocks}
    for src in extra:
        try: bl = split_blocks(src)
        except SyntaxError: continue
        for b in bl:
            kw, name = head_name(b)
            if kw in ('struct', 'enum') and name not in known: blocks.append(b); known.add(name)
    types = set(PRIM)
    for b in blocks:
        kw, name = head_name(b)
        if kw in ('struct', 'class', 'enum'): types.add(name)
    prog = Program()
    for b in blocks:
        kw, name = head_name(b)
        if kw == 'function' and name in excluded_functions: continue
        pr = Parser(b + [Tok('eof', '', 0)], types)
        prog.add(pr.decl())
    for f in list(prog.functions.values()) + [m for c in prog.classes.values() for m in c.methods]:
        f['mut'] = mutated_params(prog, f) if f.body else {p.name for p in f.params}
    return Emitter(prog).program(), prog

if __name__ == '__main__':
    out = sys.argv[1]; files = sys.argv[2:]
    js, _ = build(files, [])
    Path(out).write_text(js, encoding='utf-8')
