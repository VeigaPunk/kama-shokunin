import importlib.util
spec = importlib.util.spec_from_file_location('c2', '/fast/scratch/hyaku/kama-r63/w/KR07Routed62/mod/c2.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
for out, pat in [('xx a yy','a'), ('xx b yy','b'), ('xx ok=1 yy','ok=1'), ('xx ok=1 yy','ok')]:
    r62 = c.r62_formula(out, 0, False, pat)   # True = r62 calls it SENSITIVE
    r63 = c.is_sensitive(out, 0, False, pat)
    print(f'pattern={pat!r:8} in-token={pat in "__kama_mut__"!s:5} r62_sensitive={r62!s:5} r63_sensitive={r63}  P4_witness_fires={r63 and not r62}')
