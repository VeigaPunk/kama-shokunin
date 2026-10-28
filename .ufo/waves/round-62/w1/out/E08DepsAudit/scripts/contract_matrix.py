#!/usr/bin/env python3
"""E08: capture the dependency primitive contract matrix (as observed) plus
the import-resolution record, as standalone JSON artifacts.
"""
import builtins
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
TIP = os.path.join(S, 'tip', 'tools')


def load_dep():
    spec = importlib.util.spec_from_file_location(
        'dep', os.path.join(TIP, 'kama-llamacpp-live.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def primitives(dep):
    out = {}
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 0))
    s.listen(1)
    mine = s.getsockname()[1]
    u = socket.socket()
    u.bind(('127.0.0.1', 0))
    unused = u.getsockname()[1]
    u.close()
    fx = socket.socket()
    fx.bind(('127.0.0.1', 0))
    other = fx.getsockname()[1]
    fx.close()
    q = subprocess.Popen([sys.executable, '-m', 'http.server', '--bind',
                          '127.0.0.1', str(other)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         cwd=S)
    for _ in range(60):
        try:
            socket.create_connection(('127.0.0.1', other), timeout=0.5).close()
            break
        except OSError:
            time.sleep(0.1)
    out['own_listener'] = {
        'port': mine,
        'listen_inodes': sorted(dep._listen_inodes(mine)),
        'port_owned_by_self': dep.port_owned_by(os.getpid(), mine),
    }
    out['no_listener'] = {
        'port': unused,
        'listen_inodes': sorted(dep._listen_inodes(unused)),
        'port_owned_by_self': dep.port_owned_by(os.getpid(), unused),
    }
    out['stranger_listener'] = {
        'port': other,
        'listen_inodes': sorted(dep._listen_inodes(other)),
        'port_owned_by_self': dep.port_owned_by(os.getpid(), other),
    }
    q.terminate()
    q.wait()
    real_open = builtins.open

    def deny(p, *a, **k):
        if isinstance(p, str) and p.startswith('/proc/net/tcp'):
            raise PermissionError(13, 'denied')
        return real_open(p, *a, **k)

    builtins.open = deny
    try:
        out['procfs_unreadable'] = {
            'port_with_live_listener': mine,
            'listen_inodes': sorted(dep._listen_inodes(mine)),
            'port_owned_by_self': dep.port_owned_by(os.getpid(), mine),
        }
    finally:
        builtins.open = real_open
    s.close()
    return out


def resolution():
    code = r'''
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("probe", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
attrs = ["_utc_now","sha256_file","http_get","refused_ports","pick_port",
         "prepare_witness_dir","SetupError","_FORKED_PPID",
         "_preexec_pdeathsig","port_owned_by","hold_for_witness",
         "_listen_inodes"]
print(json.dumps({
  "tool_REPO": m.REPO,
  "dep_file": str(m._live.__file__),
  "dep_module_name": m._live.__name__,
  "dep_LANE": str(m._live.LANE),
  "dep_REGISTRY": str(m._live.REGISTRY),
  "dep_in_sys_modules": m._live.__name__ in sys.modules,
  "bound": {a: type(getattr(m._live, a)).__name__ for a in attrs
            if hasattr(m._live, a)},
  "missing": [a for a in attrs if not hasattr(m._live, a)],
}, indent=1))
'''
    for label, argv, cwd in (
            ('copied_tree', [sys.executable, '-c', code,
                             os.path.join(TIP, 'kama-completion-live.py')], S),
            ('isolated_cwd_root', [sys.executable, '-I', '-c', code,
                                   os.path.join(TIP,
                                                'kama-completion-live.py')],
             '/')):
        p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
        yield label, {'rc': p.returncode,
                      'json': json.loads(p.stdout) if p.returncode == 0
                      else None,
                      'stderr': p.stderr.strip().splitlines()[-1:]}


def main():
    dep = load_dep()
    res = {'resolution': dict(resolution()),
           'primitives': primitives(dep)}
    out = os.path.join(S, 'contract-matrix.json')
    with open(out, 'w') as f:
        json.dump(res, f, indent=1, sort_keys=True)
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
