import importlib.util, sys, os, hashlib
spec = importlib.util.spec_from_file_location('c1', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
orig_collect = m.collect
def col(*a, **k):
    r = orig_collect(*a, **k)
    mp = r.get('model_path')
    data = open(mp, 'rb').read()
    print('COLLECT model size=%d sha=%s hold_pid=%s holders=%s' % (len(data), hashlib.sha256(data).hexdigest()[:12], r.get('hold_pid'), [h['pid'] for h in r['holders']]), file=sys.stderr)
    for h in r['holders']:
        print('  cmdline model arg:', [x for x in (h.get('cmdline') or []) if 'gguf' in x], file=sys.stderr)
    return r
m.collect = col
sys.exit(m.main(sys.argv[2:]))
