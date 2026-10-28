import importlib.util, sys, os
mod_path, out = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('c1mut', mod_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
orig = m.is_hit
rows = []
def wrapped(s, expect, cap=None):
    r = orig(s, expect) if cap is None else orig(s, expect, cap)
    rows.append((expect, m.MAX_COLLATERAL if cap is None else cap, len(s['fails']), s['met'], r, sorted(s['fails'])))
    return r
m.is_hit = wrapped
rc = m.main(sys.argv[3:])
with open(out, 'w') as f:
    f.write('expect\tcap\tnfails\tmet\thit\tfails\n')
    for e, c, n, met, r, fl in rows:
        f.write(f'{e}\t{c}\t{n}\t{met}\t{r}\t{",".join(fl)}\n')
sys.exit(rc)
