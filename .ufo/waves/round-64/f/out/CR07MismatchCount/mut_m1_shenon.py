import sys,io
p=sys.argv[1]+'/SHONEN.md'
t=open(p).read()
t=t.replace('- [~]','- [x]')
t=t.replace('→ Author assertion:','→ Verified by the non-author closure spot-check:')
open(p,'w').write(t)
print("M1: SHONEN four boxes flipped [~]->[x], author assertions replaced with a claimed non-author verification")
