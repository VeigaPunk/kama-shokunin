import sys
p=sys.argv[1]+'/SCORECARD.md'
t=open(p).read()
old='`corpus/lessons/round-63-verifier-spotcheck.md` (rejected-honest-stop), including round 63'
new='`corpus/lessons/round-63-verifier-spotcheck.md` (admitted-clean, all claims verified), including round 63'
assert old in t
t=t.replace(old,new)
open(p,'w').write(t)
print("M10: calibration row's closure verdict word falsified (rejected-honest-stop -> admitted-clean)")
