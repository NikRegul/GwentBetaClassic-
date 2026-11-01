"""Minimal ECMA-335 IL dumper (Linux, no .NET): python dump_il096.py Assembly-CSharp.dll TypeName..."""
import struct,sys
data=open(sys.argv[1],'rb').read()
pe=struct.unpack_from('<I',data,0x3c)[0];assert data[pe:pe+4]==b'PE\0\0'
nsec=struct.unpack_from('<H',data,pe+6)[0];optsz=struct.unpack_from('<H',data,pe+20)[0];opt=pe+24
magic=struct.unpack_from('<H',data,opt)[0];dd=opt+(96 if magic==0x10b else 112)
secs=[];so=opt+optsz
for i in range(nsec):
    n,vs,va,rs,ra=struct.unpack_from('<8sIIII',data,so+i*40);secs.append((va,vs,ra,rs))
def rva(r):
    for va,vs,ra,rs in secs:
        if va<=r<va+max(vs,rs):return r-va+ra
    raise ValueError(r)
cli_rva=struct.unpack_from('<I',data,dd+14*8)[0];cli=rva(cli_rva)
md_rva,md_size=struct.unpack_from('<II',data,cli+8);md=rva(md_rva)
assert data[md:md+4]==b'BSJB';vl=struct.unpack_from('<I',data,md+12)[0];p=md+16+vl
nstreams=struct.unpack_from('<H',data,p+2)[0];p+=4;streams={}
for i in range(nstreams):
    off,size=struct.unpack_from('<II',data,p);p+=8;e=data.index(b'\0',p);name=data[p:e].decode();p=(e+4)&~3;streams[name]=(md+off,size)
T=streams['#~'][0];hs=data[T+6];valid=struct.unpack_from('<Q',data,T+8)[0];q=T+24
rows={}
for i in range(64):
    if valid>>i&1:rows[i]=struct.unpack_from('<I',data,q)[0];q+=4
sidx=4 if hs&1 else 2;gidx=4 if hs&2 else 2;bidx=4 if hs&4 else 2
def big(*tabs):return max(rows.get(t,0) for t in tabs)
def simple(t):return 4 if rows.get(t,0)>0xffff else 2
def coded(bits,tabs):return 4 if max(rows.get(t,0) for t in tabs if t is not None)>=(1<<(16-bits)) else 2
TypeDefOrRef=(2,[2,1,0x1b]);HasConstant=(2,[4,8,0x17]);HasCustomAttribute=(5,[6,4,1,2,8,9,10,0,0xe,0x17,0x14,0x11,0x1a,0x1b,0x20,0x23,0x26,0x27,0x28,0x2a,0x2c,0x2b])
HasFieldMarshall=(1,[4,8]);HasDeclSecurity=(2,[2,6,0x20]);MemberRefParent=(3,[2,1,0x1a,6,0x1b]);HasSemantics=(1,[0x14,0x17]);MethodDefOrRef=(1,[6,10])
MemberForwarded=(1,[4,6]);Implementation=(2,[0x26,0x23,0x27]);CustomAttributeType=(3,[None,None,6,10,None]);ResolutionScope=(2,[0,0x1a,0x23,1]);TypeOrMethodDef=(1,[2,6])
def C(c):return ('c',c)
S='s';G='g';B='b';
def Tb(t):return ('t',t)
schema={0:[2,S,G,G,G],1:[C(ResolutionScope),S,S],2:[4,S,S,C(TypeDefOrRef),Tb(4),Tb(6)],3:[Tb(4)],4:[2,S,B],5:[Tb(6)],6:[4,2,2,S,B,Tb(8)],7:[Tb(8)],8:[2,2,S],
 9:[Tb(2),C(TypeDefOrRef)],10:[C(MemberRefParent),S,B],11:[2,C(HasConstant),B],12:[C(HasCustomAttribute),C(CustomAttributeType),B],13:[C(HasFieldMarshall),B],
 14:[2,C(HasDeclSecurity),B],15:[2,4,Tb(2)],16:[4,Tb(4)],17:[B],18:[Tb(2),Tb(20)],19:[Tb(20)],20:[2,S,C(TypeDefOrRef)],21:[Tb(2),Tb(23)],22:[Tb(23)],23:[2,S,B],
 24:[2,Tb(6),C(HasSemantics)],25:[Tb(2),C(MethodDefOrRef),C(MethodDefOrRef)],26:[S],27:[B],28:[2,C(MemberForwarded),S,Tb(26)],29:[4,Tb(4)],30:[4,4],31:[4],
 32:[4,2,2,2,2,4,B,S,S],33:[4],34:[4,4,4],35:[2,2,2,2,4,B,S,S,B],36:[4,Tb(0x23)],37:[4,4,4,Tb(0x23)],38:[4,S,B],39:[4,4,S,S,C(Implementation)],40:[4,4,S,C(Implementation)],
 41:[Tb(2),Tb(2)],42:[2,2,C(TypeOrMethodDef),S],43:[C(MethodDefOrRef),B],44:[Tb(0x2a),C(TypeDefOrRef)]}
def colsize(c):
    if c==S:return sidx
    if c==G:return gidx
    if c==B:return bidx
    if isinstance(c,int):return c
    if c[0]=='t':return simple(c[1])
    bits,tabs=c[1];return 4 if max(rows.get(t,0) for t in tabs if t is not None)>=(1<<(16-bits)) else 2
tables={};pos=q
for t in sorted(rows):
    cols=schema[t];sizes=[colsize(c) for c in cols];rs=sum(sizes);recs=[]
    for r in range(rows[t]):
        vals=[];o=pos+r*rs
        for s in sizes:vals.append(struct.unpack_from('<I' if s==4 else '<H',data,o)[0]);o+=s
        recs.append(vals)
    tables[t]=(cols,recs);pos+=rs*rows[t]
SH=streams['#Strings'][0];US=streams['#US'][0];BL=streams['#Blob'][0]
def st(i):e=data.index(b'\0',SH+i);return data[SH+i:e].decode('utf8','replace')
def us(i):
    o=US+i;b=data[o]
    if b&0x80==0:n=b;o+=1
    elif b&0xc0==0x80:n=((b&0x3f)<<8)|data[o+1];o+=2
    else:n=((b&0x1f)<<24)|(data[o+1]<<16)|(data[o+2]<<8)|data[o+3];o+=4
    return data[o:o+n-1].decode('utf-16le','replace') if n else ''
def row(t,i):return tables[t][1][i-1]
def decode(c,v):
    bits,tabs=c;return tabs[v&((1<<bits)-1)],v>>bits
def typename(t,i):
    if t==2:r=row(2,i);return st(r[2])+'.'+st(r[1]) if st(r[2]) else st(r[1])
    if t==1:r=row(1,i);return (st(r[2])+'.' if st(r[2]) else '')+st(r[1])
    if t==0x1b:return 'TypeSpec#%d'%i
    return '?'
def tdr(v):t,i=decode(TypeDefOrRef,v);return typename(t,i) if i else '-'
td=tables[2][1];fields=tables.get(4,([],[]))[1];methods=tables[6][1]
def owner_of_method(mi):
    for k in range(len(td)):
        a=td[k][5];b=td[k+1][5] if k+1<len(td) else len(methods)+1
        if a<=mi<b:return typename(2,k+1)
def owner_of_field(fi):
    for k in range(len(td)):
        a=td[k][4];b=td[k+1][4] if k+1<len(td) else len(fields)+1
        if a<=fi<b:return typename(2,k+1)
def token(tok):
    t=tok>>24;i=tok&0xffffff
    if t==0x70:return '"'+us(i)+'"'
    if t in(1,2):return typename(t,i)
    if t==4:return owner_of_field(i)+'::'+st(row(4,i)[1])
    if t==6:return owner_of_method(i)+'::'+st(row(6,i)[3])
    if t==10:
        r=row(10,i);pt,pi=decode(MemberRefParent,r[0]);par=typename(pt,pi) if pt in(1,2,0x1b) else str(pt)
        return par+'::'+st(r[1])
    if t==0x2b:r=row(0x2b,i);mt,mi=decode(MethodDefOrRef,r[0]);return token((mt<<24)|mi)+'<>'
    if t==0x1b:return 'TypeSpec#%d'%i
    return hex(tok)
# opcodes
one={0x00:('nop',0),0x01:('break',0),0x02:('ldarg.0',0),0x03:('ldarg.1',0),0x04:('ldarg.2',0),0x05:('ldarg.3',0),0x06:('ldloc.0',0),0x07:('ldloc.1',0),0x08:('ldloc.2',0),0x09:('ldloc.3',0),
0x0a:('stloc.0',0),0x0b:('stloc.1',0),0x0c:('stloc.2',0),0x0d:('stloc.3',0),0x0e:('ldarg.s',1),0x0f:('ldarga.s',1),0x10:('starg.s',1),0x11:('ldloc.s',1),0x12:('ldloca.s',1),0x13:('stloc.s',1),
0x14:('ldnull',0),0x15:('ldc.i4.m1',0),0x16:('ldc.i4.0',0),0x17:('ldc.i4.1',0),0x18:('ldc.i4.2',0),0x19:('ldc.i4.3',0),0x1a:('ldc.i4.4',0),0x1b:('ldc.i4.5',0),0x1c:('ldc.i4.6',0),0x1d:('ldc.i4.7',0),0x1e:('ldc.i4.8',0),
0x1f:('ldc.i4.s','b'),0x20:('ldc.i4','i'),0x21:('ldc.i8','q'),0x22:('ldc.r4','f'),0x23:('ldc.r8','d'),0x25:('dup',0),0x26:('pop',0),0x27:('jmp','T'),0x28:('call','T'),0x29:('calli','T'),0x2a:('ret',0),
0x2b:('br.s','b'),0x2c:('brfalse.s','b'),0x2d:('brtrue.s','b'),0x2e:('beq.s','b'),0x2f:('bge.s','b'),0x30:('bgt.s','b'),0x31:('ble.s','b'),0x32:('blt.s','b'),0x33:('bne.un.s','b'),0x34:('bge.un.s','b'),0x35:('bgt.un.s','b'),0x36:('ble.un.s','b'),0x37:('blt.un.s','b'),
0x38:('br','i'),0x39:('brfalse','i'),0x3a:('brtrue','i'),0x3b:('beq','i'),0x3c:('bge','i'),0x3d:('bgt','i'),0x3e:('ble','i'),0x3f:('blt','i'),0x40:('bne.un','i'),0x41:('bge.un','i'),0x42:('bgt.un','i'),0x43:('ble.un','i'),0x44:('blt.un','i'),
0x45:('switch','S')}
names2='ldind.i1 ldind.u1 ldind.i2 ldind.u2 ldind.i4 ldind.u4 ldind.i8 ldind.i ldind.r4 ldind.r8 ldind.ref stind.ref stind.i1 stind.i2 stind.i4 stind.i8 stind.r4 stind.r8 add sub mul div div.un rem rem.un and or xor shl shr shr.un neg not conv.i1 conv.i2 conv.i4 conv.i8 conv.r4 conv.r8 conv.u4 conv.u8'.split()
for k,n in enumerate(names2):one[0x46+k]=(n,0)
one.update({0x6f:('callvirt','T'),0x70:('cpobj','T'),0x71:('ldobj','T'),0x72:('ldstr','T'),0x73:('newobj','T'),0x74:('castclass','T'),0x75:('isinst','T'),0x76:('conv.r.un',0),0x79:('unbox','T'),0x7a:('throw',0),
0x7b:('ldfld','T'),0x7c:('ldflda','T'),0x7d:('stfld','T'),0x7e:('ldsfld','T'),0x7f:('ldsflda','T'),0x80:('stsfld','T'),0x81:('stobj','T'),0x8c:('box','T'),0x8d:('newarr','T'),0x8e:('ldlen',0),0x8f:('ldelema','T'),
0x90:('ldelem.i1',0),0x91:('ldelem.u1',0),0x92:('ldelem.i2',0),0x93:('ldelem.u2',0),0x94:('ldelem.i4',0),0x95:('ldelem.u4',0),0x96:('ldelem.i8',0),0x97:('ldelem.i',0),0x98:('ldelem.r4',0),0x99:('ldelem.r8',0),0x9a:('ldelem.ref',0),
0x9b:('stelem.i',0),0x9c:('stelem.i1',0),0x9d:('stelem.i2',0),0x9e:('stelem.i4',0),0x9f:('stelem.i8',0),0xa0:('stelem.r4',0),0xa1:('stelem.r8',0),0xa2:('stelem.ref',0),0xa3:('ldelem','T'),0xa4:('stelem','T'),0xa5:('unbox.any','T'),
0xb3:('conv.ovf.i1',0),0xb4:('conv.ovf.u1',0),0xb5:('conv.ovf.i2',0),0xb6:('conv.ovf.u2',0),0xb7:('conv.ovf.i4',0),0xb8:('conv.ovf.u4',0),0xb9:('conv.ovf.i8',0),0xba:('conv.ovf.u8',0),0xc2:('refanyval','T'),0xc3:('ckfinite',0),0xc6:('mkrefany','T'),
0xd0:('ldtoken','T'),0xd1:('conv.u2',0),0xd2:('conv.u1',0),0xd3:('conv.i',0),0xd4:('conv.ovf.i',0),0xd5:('conv.ovf.u',0),0xd6:('add.ovf',0),0xd7:('add.ovf.un',0),0xd8:('mul.ovf',0),0xd9:('mul.ovf.un',0),0xda:('sub.ovf',0),0xdb:('sub.ovf.un',0),
0xdc:('endfinally',0),0xdd:('leave','i'),0xde:('leave.s','b'),0xdf:('stind.i',0),0xe0:('conv.u',0)})
two={0x00:('arglist',0),0x01:('ceq',0),0x02:('cgt',0),0x03:('cgt.un',0),0x04:('clt',0),0x05:('clt.un',0),0x06:('ldftn','T'),0x07:('ldvirtftn','T'),0x09:('ldarg','h'),0x0a:('ldarga','h'),0x0b:('starg','h'),0x0c:('ldloc','h'),0x0d:('ldloca','h'),0x0e:('stloc','h'),0x0f:('localloc',0),0x11:('endfilter',0),0x12:('unaligned.',1),0x13:('volatile.',0),0x14:('tail.',0),0x15:('initobj','T'),0x16:('constrained.','T'),0x17:('cpblk',0),0x18:('initblk',0),0x1a:('rethrow',0),0x1c:('sizeof','T'),0x1d:('refanytype',0),0x1e:('readonly.',0)}
def body(r):
    o=rva(r);h=data[o]
    if h&3==2:size=h>>2;code=o+1
    else:fl=struct.unpack_from('<H',data,o)[0];hsz=(fl>>12)*4;size=struct.unpack_from('<I',data,o+4)[0];code=o+hsz
    out=[];i=0
    while i<size:
        b=data[code+i];at=i;i+=1
        if b==0xfe:b2=data[code+i];i+=1;n,op=two[b2]
        else:n,op=one.get(b,('?%02x'%b,0))
        arg=''
        if op==1:arg=str(data[code+i]);i+=1
        elif op=='b':v=struct.unpack_from('<b',data,code+i)[0];i+=1;arg='%d'%(i+v) if n.startswith('b') or n.startswith('leave') else str(v)
        elif op=='h':arg=str(struct.unpack_from('<H',data,code+i)[0]);i+=2
        elif op=='i':v=struct.unpack_from('<i',data,code+i)[0];i+=4;arg='%d'%(i+v) if (n.startswith('b') or n.startswith('leave')) else str(v)
        elif op=='q':arg=str(struct.unpack_from('<q',data,code+i)[0]);i+=8
        elif op=='f':arg=repr(struct.unpack_from('<f',data,code+i)[0]);i+=4
        elif op=='d':arg=repr(struct.unpack_from('<d',data,code+i)[0]);i+=8
        elif op=='T':arg=token(struct.unpack_from('<I',data,code+i)[0]);i+=4
        elif op=='S':n2=struct.unpack_from('<I',data,code+i)[0];i+=4+4*n2;arg='[%d]'%n2
        out.append('IL_%04x: %s %s'%(at,n,arg))
    return out
want=sys.argv[2:]
for k,r in enumerate(td):
    nm=st(r[1])
    if nm not in want:continue
    print('TYPE',typename(2,k+1),'base',tdr(r[3]))
    fa=r[4];fb=td[k+1][4] if k+1<len(td) else len(fields)+1
    for fi in range(fa,fb):print('FIELD',st(fields[fi-1][1]))
    ma=r[5];mb=td[k+1][5] if k+1<len(td) else len(methods)+1
    for mi in range(ma,mb):
        m=methods[mi-1];print('METHOD',st(m[3]))
        if m[0]:
            for l in body(m[0]):print(' ',l)
