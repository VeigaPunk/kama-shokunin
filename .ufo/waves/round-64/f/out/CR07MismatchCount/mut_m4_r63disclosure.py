import sys
p=sys.argv[1]+'/SCORECARD.md'
lines=open(p).read().split('\n')
out=[l for l in lines if not l.startswith('What `met=True` does not show: for C1, that the answering process')]
assert len(out)==len(lines)-1
open(p,'w').write('\n'.join(out))
print("M4: round-63 'What met=True does not show' disclosure paragraph deleted")
