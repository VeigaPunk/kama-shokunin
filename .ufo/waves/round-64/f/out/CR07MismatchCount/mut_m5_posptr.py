import sys
p=sys.argv[1]+'/SCORECARD.md'
t=open(p).read()
old='`corpus/lessons/round-63-verifier-spotcheck.md` (rejected-honest-stop), including round 63'
new='`corpus/lessons/round-57-verifier-spotcheck.md` (rejected-honest-stop), including round 57'
assert old in t
t=t.replace(old,new)
open(p,'w').write(t)
print("M5 POSITIVE CONTROL: calibration row closure pointer rolled back to round-57")
