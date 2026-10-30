import sys
p=sys.argv[1]+'/SCORECARD.md'
t=open(p).read()
old='.ufo/waves/round-16/live/receipt.json'
new='.ufo/waves/round-16/live/receipt-DOES-NOT-EXIST.json'
# only inside the round-64 canonical list (last occurrence block)
i=t.index('**Capabilities — canonical list as of round 64**')
head,tail=t[:i],t[i:]
assert old in tail
tail=tail.replace(old,new,1)
open(p,'w').write(head+tail)
print("M3: round-64 canonical capability evidence pointer -> nonexistent file")
