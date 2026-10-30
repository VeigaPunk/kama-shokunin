#!/usr/bin/env python3
"""Kernel facts for the listener-topology attacks (seat MT22ListenerShapes).

Records, per case: whether the bind succeeds, what /proc/net/tcp{,6} shows
for the port, and what the AMENDED counter's own classifiers
(round64-c1-counter._hex_loopback / listeners, and the tool's
kama-llamacpp-live._listen_inodes) make of it.
"""
import os
import socket
import subprocess
import sys
import importlib.util

D = '/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes/clone'
spec = importlib.util.spec_from_file_location(
    'c1', os.path.join(D, 'tools', 'round64-c1-counter.py'))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)
spec2 = importlib.util.spec_from_file_location(
    'kl', os.path.join(D, 'tools', 'kama-llamacpp-live.py'))
kl = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(kl)

SERVER = os.path.expanduser('~/.local/opt/llama-b11755/llama-server')
MODEL = os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf')


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def net_rows(port):
    out = []
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(path) as fh:
                next(fh)
                for line in fh:
                    f = line.split()
                    if len(f) < 10 or f[3] != '0A':
                        continue
                    addr, _, p = f[1].partition(':')
                    if int(p, 16) != port:
                        continue
                    out.append((os.path.basename(path), addr, f[9]))
        except OSError:
            pass
    return out


def report(tag, port):
    rows = net_rows(port)
    print(f'  {tag}: port={port} LISTEN rows:')
    for fam, addr, inode in rows:
        print(f'    {fam} addr_hex={addr} inode={inode} '
              f'counter_loopback={c1._hex_loopback(addr)}')
    print(f'    counter.listeners()={c1.listeners(port)}')
    print(f'    tool._listen_inodes()={sorted(kl._listen_inodes(port))}')


def start_server(port):
    p = subprocess.Popen(
        [SERVER, '--model', MODEL, '--alias', 'kama-completion-probe',
         '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import time
    for _ in range(600):
        try:
            s = socket.create_connection(('127.0.0.1', port), timeout=0.5)
            s.close()
            return p
        except OSError:
            if p.poll() is not None:
                return p
            time.sleep(0.1)
    return p


def case_reuseport_after_child():
    print('== case A: SO_REUSEPORT second listener on 127.0.0.1 (after child)')
    port = free_port()
    child = start_server(port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            s.bind(('127.0.0.1', port))
            print('    bind SO_REUSEPORT: OK (server sets SO_REUSEPORT)')
            s.listen(5)
        except OSError as e:
            print(f'    bind SO_REUSEPORT: FAILED {e!r} '
                  f'(server does not set SO_REUSEPORT)')
            s.close()
        report('after-child', port)
    finally:
        child.terminate()
        child.wait()


def case_reuseport_before_child():
    print('== case A2: SO_REUSEPORT first, child second')
    port = free_port()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('127.0.0.1', port))
    s.listen(5)
    child = start_server(port)
    time.sleep(1)
    print(f'    child rc={child.poll()} (1 == child could not bind)')
    report('reuseport-first', port)
    s.close()
    if child.poll() is None:
        child.terminate()
        child.wait()


def case_other_addr(child_port):
    print('== case B: same port on 127.0.0.2 and ::1, child on 127.0.0.1')
    for fam, addr, v6only in (
            (socket.AF_INET, ('127.0.0.2', child_port), None),
            (socket.AF_INET6, ('::1', child_port), 1),
            (socket.AF_INET6, ('::ffff:127.0.0.1', child_port), 1),
            (socket.AF_INET6, ('::ffff:127.0.0.1', child_port), 0)):
        tag = f'{fam} {addr} v6only={v6only}'
        try:
            s = socket.socket(fam, socket.SOCK_STREAM)
            if v6only is not None:
                s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, v6only)
            try:
                s.bind(addr)
                s.listen(5)
                print(f'  {tag}: bind OK')
            except OSError as e:
                print(f'  {tag}: bind FAILED {e!r}')
                s.close()
        except OSError as e:
            print(f'  {tag}: socket FAILED {e!r}')
    report('other-addr', child_port)


def case_unix():
    print('== case D: unix-socket front')
    path = '/tmp/mt22-facts.sock'
    try:
        os.unlink(path)
    except OSError:
        pass
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(path)
    s.listen(5)
    print(f'    unix listen OK at {path}')
    print('    /proc/net/tcp rows for any port unaffected: '
          f'count={len(c1.listeners(free_port()))}')
    s.close()
    os.unlink(path)


def case_netns():
    print('== case F: listener inside a user+net namespace')
    script = (
        'import socket,os,sys\n'
        's=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]\n'
        'print(port, flush=True)\n'
        'os.unshare(os.CLONE_NEWUSER|os.CLONE_NEWNET)\n'
        't=socket.socket(); t.bind(("127.0.0.1",port)); t.listen(5)\n'
        'print("bound", flush=True)\n'
        'import time; time.sleep(20)\n')
    p = subprocess.Popen([sys.executable, '-c', script],
                         stdout=subprocess.PIPE, text=True)
    port = int(p.stdout.readline().strip())
    p.stdout.readline()
    print(f'    netns listener bound on 127.0.0.1:{port} inside the new ns')
    report('host-view', port)
    p.kill()
    p.wait()


if __name__ == '__main__':
    port = free_port()
    child = start_server(port)
    try:
        report('baseline-child', port)
        case_reuseport_after_child()
        case_other_addr(port)
        case_unix()
        case_netns()
    finally:
        child.terminate()
        child.wait()
    case_reuseport_before_child()
