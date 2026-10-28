import importlib.util
spec = importlib.util.spec_from_file_location('c1', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round63-c1-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for p in (None, 'abc', 99999, -1):
    try:
        r = m.http(p, '/v1/completions', {'prompt': 'x'}, timeout=2)
        print(repr(p), 'ok status=', r[0], 'body=', r[2][:40])
    except Exception as e:
        print(repr(p), 'CRASH', type(e).__name__, e)
try:
    m.observe(None, None, {'alias': 'a'}, None, 'r63-x')
    print('observe(None) ok')
except Exception as e:
    print('observe(None) CRASH', type(e).__name__, e)
