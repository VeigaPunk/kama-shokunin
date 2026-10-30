#!/usr/bin/env python3
# runs the prototype counter unchanged and prints what conn_owner observed
import importlib.util, json, sys
path, repo, tip, work = sys.argv[1:5]
spec = importlib.util.spec_from_file_location('c1', path)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)
orig = c1.conn_owner
def spy(port, timeout=5.0):
    r = orig(port, timeout)
    print('CONN_OWNER port=%s -> %s' % (port, json.dumps(r, default=str)),
          file=sys.stderr, flush=True)
    return r
c1.conn_owner = spy
sys.exit(c1.main(['--repo', repo, '--tip', tip, '--work', work]))
