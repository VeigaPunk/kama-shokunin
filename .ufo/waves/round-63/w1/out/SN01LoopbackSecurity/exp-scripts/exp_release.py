#!/usr/bin/env python3
"""E7/E8: (a) a release file created while the requests run (before the hold window opens)
- does the receipt still say released=true with a real observation window? (b) receipt and
server-log leakage of home paths / environment values."""
import json, os, re, shutil, socket, subprocess, sys, time

S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
TOOL = f'{S}/clone/tools/kama-completion-live.py'
OUT = f'{S}/exp/release'
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
hold = f'{OUT}/hold'
os.makedirs(hold)
rec = f'{OUT}/receipt.json'
env = dict(os.environ)
env['KAMA_SECRET_PROBE'] = 'do-not-leak-7731'
p = subprocess.Popen([sys.executable, TOOL, '--work', f'{OUT}/work', '--out', rec,
                      '--nonce', 'early-release', '--hold-dir', hold,
                      '--hold-timeout', '30'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     stdin=subprocess.DEVNULL, env=env)
# watcher: as soon as the run port accepts a TCP connect (server up, requests about to run),
# drop the release file - long before the tool reaches hold_for_witness.
rel_at = None
t0 = time.monotonic()
seen_port = None
srv_log = f'{OUT}/work/server.log'
while time.monotonic() - t0 < 60 and p.poll() is None:
    if seen_port is None and os.path.exists(srv_log):
        m = re.search(r'--port\s+(\d+)', open(srv_log, errors='replace').read()[:4000])
        # the argv is not in server.log; discover the port from the receipt-free sources below
    try:
        # the child listens on the port the tool picked; find it via /proc of the tool's child
        kids = subprocess.run(['pgrep', '-P', str(p.pid)], capture_output=True, text=True).stdout.split()
        if kids:
            cmd = open(f'/proc/{kids[0]}/cmdline', 'rb').read().split(b'\0')
            if b'--port' in cmd:
                seen_port = int(cmd[cmd.index(b'--port') + 1])
                s = socket.create_connection(('127.0.0.1', seen_port), timeout=0.5)
                s.close()
                open(f'{hold}/release', 'w').write('early\n')
                rel_at = round(time.monotonic() - t0, 2)
                break
    except (OSError, ValueError, IndexError, socket.timeout, ConnectionRefusedError):
        pass
    time.sleep(0.02)
p.wait(timeout=120)
r = json.load(open(rec))
print(json.dumps({'release_created_at_s': rel_at, 'verdict': r.get('verdict'),
                  'hold': r.get('hold'),
                  'hold_released_check': r['checks'].get('hold_released'),
                  'port': r.get('port')}, indent=1))

# (b) leakage scan over every produced artifact
pat = re.compile(r'/home/[A-Za-z0-9_.-]+|vgpnk|do-not-leak-7731|LD_LIBRARY_PATH')
hits = {}
for dp, _, fns in os.walk(OUT):
    for fn in fns:
        fp = os.path.join(dp, fn)
        try:
            txt = open(fp, errors='replace').read()
        except OSError:
            continue
        found = sorted(set(pat.findall(txt)))
        if found:
            hits[os.path.relpath(fp, OUT)] = found
print(json.dumps({'leak_hits': hits}, indent=1))
for k in ('model', 'server', 'argv', 'hold', 'port'):
    print(k, json.dumps(r.get(k))[:300])
print('captures:', sorted((r.get('captures') or {}).keys()))
print('props_body_model_path:', re.findall(r'"model_path":\s*"[^"]*"', (r.get('captures') or {}).get('props', {}).get('body', ''))[:1])
