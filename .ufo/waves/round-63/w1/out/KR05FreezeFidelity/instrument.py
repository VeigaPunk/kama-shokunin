# Scratch-only instrument: loads the frozen-tip amended counter unmodified and
# records, for every is_hit call, the failure-set size and names.
import importlib.util, sys
S = '/fast/scratch/hyaku/kama-r63/w/KR05FreezeFidelity'
spec = importlib.util.spec_from_file_location('c1amend', S + '/amended-c1.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
orig = m.is_hit
rows = []
def wrapped(s, expect, cap=None):
    r = orig(s, expect) if cap is None else orig(s, expect, cap)
    rows.append((expect, m.MAX_COLLATERAL if cap is None else cap,
                 len(s['fails']), s['met'], r, sorted(s['fails'])))
    return r
m.is_hit = wrapped
rc = m.main(sys.argv[1:])
with open(S + '/fail-sizes.tsv', 'w') as f:
    f.write('expect\tcap\tnfails\tmet\thit\tfails\n')
    for e, c, n, met, r, fl in rows:
        f.write(f'{e}\t{c}\t{n}\t{met}\t{r}\t{",".join(fl)}\n')
sys.exit(rc)
