import sys
p=sys.argv[1]+'/SCORECARD.md'
lines=open(p).read().split('\n')
i=next(i for i,l in enumerate(lines) if l.startswith('**Capabilities — canonical list as of round 64**'))
hit=0
for j in range(i,min(i+40,len(lines))):
    if lines[j].startswith('| sources-registry |'):
        cells=lines[j].split('|')
        assert cells[4].strip()=='10', cells
        cells[4]=' 3 '
        lines[j]='|'.join(cells); hit=1; break
assert hit
open(p,'w').write('\n'.join(lines))
print("M6: round-64 canonical list 'sources-registry' first-working round 10 -> 3")
