import sys
p=sys.argv[1]+'/SCORECARD.md'
t=open(p).read()
i=t.index('**Capabilities — canonical list as of round 64**')
head,tail=t[:i],t[i:]
old='Start the pinned llama.cpp b11755 server on an unregistered loopback port'
new='Start the pinned llama.cpp b11755 server and score consumer health with 99.9% uptime SLA compliance'
assert old in tail
tail=tail.replace(old,new,1)
open(p,'w').write(head+tail)
print("M7: round-64 canonical capability description falsified beyond the 48-char prefix")
