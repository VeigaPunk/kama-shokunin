#!/usr/bin/env python3
"""L02LogTail: does llama-server write the captured lines to STDERR (the stream the
tool claims to capture), and does anything go to stdout? Spawns its own child on a
free unregistered loopback port and SIGTERMs it."""
import importlib.util
import os
import signal
import subprocess
import sys
import time

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
spec = importlib.util.spec_from_file_location(
    'kl', os.path.join(LANE, 'tools', 'kama-llamacpp-live.py'))
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

R = '/fast/scratch/hyaku/kama-r62/w/L02LogTail/streams'
os.makedirs(R, exist_ok=True)
port = kl.pick_port(kl.refused_ports(), None)
server = os.path.realpath(subprocess.check_output(['which', 'llama-server'], text=True).strip())
model = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
argv = [server, '--model', model, '--alias', 'l02-stream-probe', '--port', str(port),
        '--host', '127.0.0.1', '-c', '512', '-t', '1']
env = {k: v for k, v in os.environ.items()
       if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH', 'XDG_CACHE_HOME')}
with open(os.path.join(R, 'stdout.log'), 'wb') as so, open(os.path.join(R, 'stderr.log'), 'wb') as se:
    p = subprocess.Popen(argv, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=env)
    t0 = time.monotonic()
    while time.monotonic() - t0 < 20:
        r = kl.http_get(port, '/health', timeout=1.0)
        if r['status'] == 200:
            break
        time.sleep(0.1)
    p.send_signal(signal.SIGTERM)
    rc = p.wait(timeout=20)
print('port', port, 'rc', rc)
for name in ('stdout.log', 'stderr.log'):
    path = os.path.join(R, name)
    raw = open(path, 'rb').read()
    print(f'{name}: {len(raw)} bytes, lines={raw.count(b"\\n")}')
    for probe in (b'model loaded', b'listening on http://127.0.0.1:' + str(port).encode()):
        print(f'  {probe!r}: {probe in raw}')
