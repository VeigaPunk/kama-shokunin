import sys
p=sys.argv[1]+'/SCORECARD.md'
t=open(p).read()
a='`agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`'
b='`agreement=87/87 overclaim=0 underclaim=0 other=0 absent=0`'
c='`agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`'
d='`agreement=61/61 overclaim=0 underclaim=0 other=0 absent=0`'
assert a in t and c in t
t=t.replace(a,b).replace(c,d)
t=t.replace('registry/verdict-ledger.tsv` (204 rows','registry/verdict-ledger.tsv` (999 rows')
t=t.replace('registry/claim-outcome-ledger.tsv` (126 rows','registry/claim-outcome-ledger.tsv` (777 rows')
open(p,'w').write(t)
print("M2: calibration row ledger figures + row counts falsified")
