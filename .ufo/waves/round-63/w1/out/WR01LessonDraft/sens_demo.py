import importlib.util, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('r62c2', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round62-c2-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
MUT = m.MUT
def sensitive(P, out, rc=0, dead=False):   # verbatim expression from run_bound (round-62 counter)
    mut = out.replace(P, MUT)
    return not (P in mut and rc == 0 and not dead)
n_false = 0
for slug, (prefix, tpls) in m.MANIFEST.items():
    for t in tpls:
        P = t['pattern']
        out = 'log line before\n' + P + '\nlog line after\n'   # decisive output present, exit 0
        s = sensitive(P, out)
        n_false += (not s)
        print(f"{slug:32s} sensitive={s} pattern={P!r}")
print("patterns with sensitive=False:", n_false, "of", sum(len(t) for _, t in m.MANIFEST.values()))
print("A05 toy P='a', out='a' ->", sensitive('a', 'a'))
print("P='ab', out='aab' ->", sensitive('ab', 'aab'))
