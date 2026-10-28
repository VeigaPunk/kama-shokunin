#!/usr/bin/env python3
"""E2/E3: hold-window behaviour of the lane tool, live.
Run A: planted hold.json symlink -> victim outside the hold dir; loopback bind; release, REQUEST_OK.
Run B: kill -9 the tool while the server is held; the child must die (PR_SET_PDEATHSIG)."""
import json, os, signal, subprocess, sys, time

S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
TOOL = f'{S}/clone/tools/kama-completion-live.py'
OUT = f'{S}/exp/hold'
os.makedirs(OUT, exist_ok=True)


def wait_for(path, timeout):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if os.path.exists(path):
            return True
        time.sleep(0.05)
    return False


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        st = open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()[0]
        return st != 'Z'
    except OSError:
        return False


def run_tool(tag, hold, rec, work, extra=()):
    return subprocess.Popen(
        [sys.executable, TOOL, '--work', work, '--out', rec,
         '--nonce', 'hold-' + tag, '--hold-dir', hold, '--hold-timeout', '60',
         *extra],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL)


result = {}

# ---------- Run A: symlink planted at hold.json ----------
hA = f'{OUT}/A-hold'
victim = f'{OUT}/A-victim.txt'
if os.path.lexists(hA):
    import shutil; shutil.rmtree(hA)
os.makedirs(hA)
with open(victim, 'w') as fh:
    fh.write('VICTIM-ORIGINAL-CONTENT\n')
os.symlink(victim, f'{hA}/hold.json')
recA = f'{OUT}/A-receipt.json'
pA = run_tool('A', hA, recA, f'{OUT}/A-work')
ready = f'{hA}/ready.json'
ok = wait_for(ready, 120)
info = {'ready_seen': ok}
if ok:
    rd = json.load(open(ready))
    port, cpid = rd['port'], rd['pid']
    info.update({'port': port, 'child_pid': cpid,
                 'child_ppid_is_tool': open(f'/proc/{cpid}/stat').read()
                 .rsplit(')', 1)[1].split()[1] == str(pA.pid),
                 'victim_after_hold_json_write': open(victim).read()[:200],
                 'hold_json_is_symlink': os.path.islink(f'{hA}/hold.json')})
    ss = subprocess.run(['ss', '-ltnp', f'sport = :{port}'],
                        capture_output=True, text=True).stdout
    info['ss_listen'] = [l for l in ss.splitlines() if str(port) in l]
    open(f'{hA}/release', 'w').write('go\n')
try:
    pA.wait(timeout=120)
except subprocess.TimeoutExpired:
    pA.kill(); info['A_timeout'] = True
rA = json.load(open(recA)) if os.path.exists(recA) else {}
info['A_verdict'] = rA.get('verdict')
info['A_hold'] = rA.get('hold')
info['A_victim_final'] = open(victim).read()[:200]
result['A'] = info
print('A', json.dumps(info, indent=1))

# ---------- Run B: SIGKILL the tool during the hold ----------
hB = f'{OUT}/B-hold'
if os.path.lexists(hB):
    import shutil; shutil.rmtree(hB)
os.makedirs(hB)
recB = f'{OUT}/B-receipt.json'
pB = run_tool('B', hB, recB, f'{OUT}/B-work')
okB = wait_for(f'{hB}/ready.json', 120)
infoB = {'ready_seen': okB}
if okB:
    rd = json.load(open(f'{hB}/ready.json'))
    cpid = rd['pid']
    infoB['child_pid'] = cpid
    infoB['child_alive_before_kill'] = alive(cpid)
    infoB['tool_pid'] = pB.pid
    os.kill(pB.pid, signal.SIGKILL)  # tool spawned by this driver
    pB.wait(timeout=10)
    t0 = time.monotonic()
    dead_at = None
    while time.monotonic() - t0 < 5:
        if not alive(cpid):
            dead_at = round((time.monotonic() - t0) * 1000)
            break
        time.sleep(0.02)
    infoB['child_dead_after_ms'] = dead_at
    infoB['child_alive_5s_after_tool_kill'] = alive(cpid)
    if alive(cpid):  # clean up our own orphan only
        os.kill(cpid, signal.SIGKILL)
result['B'] = infoB
print('B', json.dumps(infoB, indent=1))
json.dump(result, open(f'{OUT}/summary.json', 'w'), indent=1)
