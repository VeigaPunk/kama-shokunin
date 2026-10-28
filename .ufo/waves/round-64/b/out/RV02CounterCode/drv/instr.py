import importlib.util, sys, json
REPO, TIP, W2, LOG = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
spec = importlib.util.spec_from_file_location('c1c', REPO + '/tools/round64-c1-counter.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
log = []
orig = c.is_hit
def wrap(s, expect, cap=c.MAX_COLLATERAL):
    r = orig(s, expect, cap)
    log.append({'expect': expect, 'cap': cap, 'n': len(s['fails']), 'hit': r, 'fails': sorted(s['fails'])})
    return r
c.is_hit = wrap
rc = c.main(['--repo', REPO, '--tip', TIP, '--work', W2])
json.dump(log, open(LOG, 'w'), indent=1)
print('rc', rc, 'calls', len(log))
