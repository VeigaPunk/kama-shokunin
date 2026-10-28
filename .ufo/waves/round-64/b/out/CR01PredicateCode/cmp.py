import re,sys
fz=open('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-64/controls/freeze.txt').read()
i=fz.index('C1-r64:'); j=fz.index('Counter:',i)
a=' '.join(fz[i:j].split())
src=open('clone/tools/round64-c1-counter.py').read()
k=src.index('C1-r64:'); l=src.index('"""',k)
b=' '.join(src[k:l].split())
import difflib
print('freeze len',len(a),'docstring len',len(b))
for op in difflib.SequenceMatcher(None,a,b).get_opcodes():
    if op[0]!='equal': print(op, repr(a[op[1]:op[2]]), repr(b[op[3]:op[4]]))
print('IDENTICAL' if a==b else 'DIFFERENT')
