import importlib.util, sys
sys.path.insert(0, '/fast/scratch/hyaku/kama-r63/w/KR07Routed62/mod')
spec = importlib.util.spec_from_file_location('c2', '/fast/scratch/hyaku/kama-r63/w/KR07Routed62/mod/c2.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
print('selftest total =', c.sensitivity_selftest(), 'expect', c.EXPECT_SELFTEST)
out, pat = 'xx ok=1 yy', 'ok=1'
plants = {
 'P1 always-true': lambda o, rc, d, p: True,
 'P2 rc-only (no pattern)': lambda o, rc, d, p: rc == 0 and not d,
 'P3 pattern-only (no exit)': lambda o, rc, d, p: p in o and not d,
}
for k, v in plants.items():
    print(k, 'is_sensitive=', c.is_sensitive(out, 0, False, pat, vfn=v), '-> rejected' if not c.is_sensitive(out, 0, False, pat, vfn=v) else '-> ESCAPED')
print('real verdict_fn is_sensitive(out)=', c.is_sensitive(out, 0, False, pat))
print('real verdict on exit-2 output=', c.is_sensitive(out, 2, False, pat))
# the 4th plant: the r62 expression on pattern 'a' in output 'a'
print('P4 r62_formula(a,a)=', c.r62_formula('a', 0, False, 'a'), ' is_sensitive(a,a)=', c.is_sensitive('a', 0, False, 'a'))
