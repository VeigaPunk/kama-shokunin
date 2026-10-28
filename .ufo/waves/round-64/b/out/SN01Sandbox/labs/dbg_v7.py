import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('c1', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
orig = m.grade_binding
def gb(raw):
    out = orig(raw)
    bad = {k: v for k, v in out.items() if v is not True}
    if bad:
        print('BIND-FAIL', bad, file=sys.stderr)
        print('holders', [(h.get('pid'), h.get('exe')) for h in (raw or {}).get('holders', [])], 'hold_pid', (raw or {}).get('hold_pid'), 'unreadable_own', (raw or {}).get('unreadable_own'), 'unreadable_old', (raw or {}).get('unreadable_old'), file=sys.stderr)
    return out
m.grade_binding = gb
sys.exit(m.main(sys.argv[2:]))
