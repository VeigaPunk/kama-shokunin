import csv, collections, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
LANE=os.environ.get('KAMA_LANE') or os.path.abspath(os.path.join(HERE,'../../../../../..'))
ORDER = {"harmed":0,"unchanged":1,"unprovable":2,"unprovable-but-better":3,"improved":4}
def load(p):
    rows=list(csv.DictReader(open(p), delimiter='\t'))
    return rows
# verdict ledger: key (round,trend) -> side verdict
vr=load(os.path.join(LANE,'registry/verdict-ledger.tsv'))
print("verdict-ledger rows:", len(vr))
side=collections.defaultdict(dict)
for r in vr:
    side[(int(r['round']),r['trend'])][r['side']]=r['verdict']
agree=over=under=other=absent=0
for k,d in side.items():
    s=d.get('self'); o=d.get('outside')
    if s=='absent' or o=='absent':
        absent+=1; continue
    if s=='mixed' or o=='mixed':
        other+=1; continue
    if s==o: agree+=1
    elif ORDER[s]>ORDER[o]: over+=1
    elif ORDER[s]<ORDER[o]: under+=1
    else: other+=1
print(f"verdict-ledger: agree={agree} overclaim={over} underclaim={under} other={other} absent={absent}  (SCORECARD claims agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15)")
co=load(os.path.join(LANE,'registry/claim-outcome-ledger.tsv'))
print("claim-outcome rows:", len(co))
cside=collections.defaultdict(dict)
for r in co:
    cside[(int(r['round']),r['claim'])][r['side']]=r['outcome']
ca=co_=cu=cot=coab=0
# the audit tool's own assertion-strength order:
#   not-met < unprovable < partial < unprovable-but-better < met
RANK={'not-met':0,'unprovable':1,'partial':2,'unprovable-but-better':3,'met':4}
for k,d in cside.items():
    s=d.get('self'); o=d.get('outside')
    if s is None or o is None or s=='absent' or o=='absent':
        coab+=1; continue
    if s=='mixed' or o=='mixed':
        cot+=1; continue
    if s==o: ca+=1
    elif RANK[s]>RANK[o]: co_+=1
    elif RANK[s]<RANK[o]: cu+=1
    else: cot+=1
print(f"claim-outcome: agree={ca} overclaim={co_} underclaim={cu} other={cot} absent={coab}  (SCORECARD claims agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1)")
