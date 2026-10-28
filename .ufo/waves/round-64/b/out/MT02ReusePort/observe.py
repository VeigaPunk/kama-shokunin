#!/usr/bin/env python3
"""Observer for one forged run: holds the tool exactly as the counter does
(counter's own hold protocol), prints the counter's listeners()/holder_pids()
output, an independent ss cross-check and the forge-helper's procfs visibility,
probes 127.0.0.1 (and optional extra addresses), then releases.
Usage: observe.py <clone_tools_dir> <tool.py> <workdir> <label> [probe_addrs]
The counter module is loaded from the clone and used only as a reader."""
import importlib.util, json, os, shutil, subprocess, sys, time, hashlib, urllib.request

TOOLS, TOOL, WORK, LABEL = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
PROBE_ADDRS = sys.argv[5].split(',') if len(sys.argv) > 5 else ['127.0.0.1']
spec = importlib.util.spec_from_file_location('c1', os.path.join(TOOLS, 'round64-c1-counter.py'))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
SERVER = os.path.expanduser('~/.local/opt/llama-b11755/llama-server')
MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
wd = os.path.join(WORK, LABEL); shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
hold = os.path.join(wd, 'hold'); os.makedirs(hold, mode=0o700)
nonce = 'obs-' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')}
proc = subprocess.Popen([sys.executable, TOOL, '--nonce', nonce, '--work', os.path.join(wd, 'tool-work'),
    '--server', SERVER, '--model', MODEL, '--model-sha256', C.MODEL_SHA, '--server-sha256', C.SERVER_SHA,
    '--alias', C.ALIAS, '--hold-dir', hold, '--hold-timeout', '90', '--out', os.path.join(wd, 'receipt.json')],
    stdout=open(os.path.join(wd, 'tool.stdout'), 'w'), stderr=open(os.path.join(wd, 'tool.stderr'), 'w'), env=env)
hp = os.path.join(hold, 'hold.json'); t0 = time.time(); doc = None
while time.time() - t0 < 120:
    if os.path.exists(hp):
        try:
            doc = json.load(open(hp)); break
        except ValueError:
            pass
    if proc.poll() is not None:
        break
    time.sleep(0.1)
print(f'[{LABEL}] tool pid={proc.pid} hold.json={"present" if doc else "absent"} tool_rc={proc.poll()}')
if doc:
    port = doc['port']; print(f'[{LABEL}] hold.json port={port} pid={doc["pid"]} schema={doc["schema"]}')
    ls = C.listeners(port)
    print(f'[{LABEL}] listeners({port}) = {ls}')
    pids, unread = C.holder_pids([i for i, _ in ls])
    print(f'[{LABEL}] holder_pids = {sorted(pids)} unreadable_own_uid = {sorted(unread)}')
    for p in sorted(pids):
        r = C.holder_record(p, os.path.dirname(SERVER))
        print(f'[{LABEL}]   holder pid={p} exe={r["exe"]} exe_sha={str(r["exe_sha256"])[:12]} argv0={(r["cmdline"] or [None])[0]} ppids={r["ppids"]}')
    helpers = []
    for n in os.listdir('/proc'):
        if not n.isdigit():
            continue
        try:
            if b'forge-helper' in open(f'/proc/{n}/cmdline', 'rb').read():
                helpers.append(int(n))
        except OSError:
            pass
    for hpid in helpers:
        try:
            hfd = f'readable({len(os.listdir(f"/proc/{hpid}/fd"))} fds)'
        except OSError as e:
            hfd = f'NOT readable ({e.strerror})'
        print(f'[{LABEL}] forge-helper pid={hpid} owner_uid={os.stat(f"/proc/{hpid}").st_uid} me={os.getuid()} '
              f'fd_table={hfd} in_holder_pids={hpid in pids} in_unreadable_own={hpid in unread}')
    print(f'[{LABEL}] tool fd dir: ', end='')
    try:
        print('readable', len(os.listdir(f'/proc/{proc.pid}/fd')), 'fds')
    except OSError as e:
        print('NOT readable:', e.strerror, '| stat uid of /proc/<tool> =', os.stat(f'/proc/{proc.pid}').st_uid)
    ss = subprocess.run(['ss', '-H', '-ltnp', f'( sport = :{port} )'], capture_output=True, text=True)
    print(f'[{LABEL}] ss -ltnp :{port} ->', ' | '.join(ss.stdout.split('\n')[:3]).strip() or '(none)')
    for addr in PROBE_ADDRS:
        url = f'http://[{addr}]:{port}/tokenize' if ':' in addr else f'http://{addr}:{port}/tokenize'
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        seen = {'canned {"status":"ok"}': 0, 'real tokenize': 0, 'error': 0}
        for i in range(20):
            try:
                req = urllib.request.Request(url, data=json.dumps({'content': f'probe {i}', 'add_special': True}).encode(),
                                             headers={'Content-Type': 'application/json'})
                body = op.open(req, timeout=5).read().decode()
                if body == '{"status":"ok"}':
                    seen['canned {"status":"ok"}'] += 1
                elif body.startswith('{"tokens"'):
                    seen['real tokenize'] += 1
                else:
                    seen['error'] += 1
            except Exception:
                seen['error'] += 1
        print(f'[{LABEL}] 20x POST /tokenize to {addr}:{port} answered by: {seen}')
    open(os.path.join(hold, 'release'), 'w').write('go\n')
    print(f'[{LABEL}] released')
else:
    print(f'[{LABEL}] no hold; stderr tail:', open(os.path.join(wd, 'tool.stderr')).read()[-600:])
    if proc.poll() is None:
        proc.kill()
try:
    proc.wait(timeout=90)
except subprocess.TimeoutExpired:
    print(f'[{LABEL}] tool did not exit within 90 s after release (helper teardown?)')
    proc.kill(); proc.wait()
rc = proc.returncode
try:
    r = json.load(open(os.path.join(wd, 'receipt.json')))
    print(f'[{LABEL}] receipt verdict={r.get("verdict")} setup_error={r.get("setup_error")} listener_holders={r.get("listener_holders")}')
    print(f'[{LABEL}] receipt checks failing={[k for k,v in (r.get("checks") or {}).items() if v.get("passed") is False]}')
except (OSError, ValueError) as e:
    print(f'[{LABEL}] no receipt: {e}')
print(f'[{LABEL}] tool exit rc={rc}; listeners after exit = {C.listeners(doc["port"]) if doc else "n/a"}')
