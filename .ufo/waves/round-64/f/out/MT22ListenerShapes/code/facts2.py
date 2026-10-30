#!/usr/bin/env python3
"""Raw-address facts: how the kernel prints ::1 / ::ffff:127.0.0.1 /
::ffff:127.0.0.2 in procfs, which procfs file each lands in, and how the
AMENDED counter's _hex_loopback and the tool's _tcp6_is_loopback classify
them. Also the SO_REUSEPORT orderings against the real pinned server.
"""
import os
import socket
import subprocess
import sys
import time
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


def rows(port):
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


def show(tag, port):
    print(f'  {tag}: port={port}')
    for fam, addr, inode in rows(port):
        print(f'    {fam} raw_addr={addr} inode={inode} '
              f'counter._hex_loopback={c1._hex_loopback(addr)} '
              f'tool._tcp6_is_loopback={kl._tcp6_is_loopback(addr)} '
              f'counter.listeners={c1.listeners(port)} '
              f'tool._listen_inodes={sorted(kl._listen_inodes(port))}')


def bind6(addr, v6only):
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, v6only)
    except OSError as e:
        print(f'    setv6only({v6only}) failed {e!r}')
    try:
        s.bind((addr, 0))
        s.listen(5)
        port = s.getsockname()[1]
        print(f'    bind {addr} v6only={v6only}: OK port={port}')
        return s, port
    except OSError as e:
        print(f'    bind {addr} v6only={v6only}: FAILED {e!r}')
        s.close()
        return None, None


print('== raw procfs address forms for v6 loopback variants')
socks = []
for addr, v6only in (('::1', 1), ('::ffff:127.0.0.1', 0),
                     ('::ffff:127.0.0.2', 0), ('::ffff:127.0.0.1', 1)):
    s, port = bind6(addr, v6only)
    if s is not None:
        socks.append(s)
        show(f'{addr} v6only={v6only}', port)

print('== v4 raw form for 127.0.0.1 / 127.0.0.2')
for addr in ('127.0.0.1', '127.0.0.2'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, 0))
    s.listen(5)
    show(f'v4 {addr}', s.getsockname()[1])
    socks.append(s)

print('== SO_REUSEPORT orderings against the pinned server')


def start_server(port):
    p = subprocess.Popen(
        [SERVER, '--model', MODEL, '--alias', 'kama-completion-probe',
         '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 30:
        try:
            c = socket.create_connection(('127.0.0.1', port), timeout=0.5)
            c.close()
            return p, True
        except OSError:
            if p.poll() is not None:
                return p, False
            time.sleep(0.1)
    return p, False


# child first, forger second
s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s0.bind(('127.0.0.1', 0))
port = s0.getsockname()[1]
s0.close()
child, up = start_server(port)
time.sleep(0.5)
print(f'  child-first: child up={up} rc={child.poll()}')
f = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
f.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
try:
    f.bind(('127.0.0.1', port))
    f.listen(5)
    print('    forger SO_REUSEPORT bind: OK')
except OSError as e:
    print(f'    forger SO_REUSEPORT bind: FAILED {e!r}')
f.close()
show('child-first reuseport', port)
child.terminate()
child.wait()

# forger first (SO_REUSEPORT), child second
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
s1.bind(('127.0.0.1', 0))
port = s1.getsockname()[1]
s1.listen(5)
child2, up2 = start_server(port)
time.sleep(1.5)
print(f'  forger-first: child up={up2} rc={child2.poll()}')
show('forger-first reuseport', port)
if child2.poll() is None:
    child2.terminate()
child2.wait()
s1.close()

for s in socks:
    s.close()
