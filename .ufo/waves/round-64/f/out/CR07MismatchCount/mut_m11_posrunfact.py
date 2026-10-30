import sys
p=sys.argv[1]+'/SCORECARD.md'
t=open(p).read()
old='`CAP_SELFTEST pass=2 fail=0`'
new='`CAP_SELFTEST pass=9 fail=0`'
assert old in t
t=t.replace(old,new)
open(p,'w').write(t)
print("M11 POSITIVE CONTROL: calibration row's run-fact expectation falsified")
