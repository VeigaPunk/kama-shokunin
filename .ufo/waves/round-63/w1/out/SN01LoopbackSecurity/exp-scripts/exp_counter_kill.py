import json, os, signal, subprocess, sys, time
S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
W = f'{S}/exp/counter-kill'
subprocess.run(['rm', '-rf', W]); os.makedirs(W)
c = subprocess.Popen([sys.executable, f'{S}/clone/tools/round63-c1-counter.py', '--repo', f'{S}/clone',
                      '--tip', '03a6a1d850902a66a13dfad33f89cf3a8b759a09', '--work', W],
                     cwd=f'{S}/clone/tools', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
def ppid(pid):
    try:
        return int(open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()[1])
    except OSError:
        return None
def cmd(pid):
    try:
        return open(f'/proc/{pid}/cmdline', 'rb').read().replace(b'\0', b' ').decode(errors='replace')
    except OSError:
        return ''
def find(pred):
    out = []
    for d in os.listdir('/proc'):
        if d.isdigit() and pred(int(d)):
            out.append(int(d))
    return out
def alive(pid):
    try:
        st = open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()[0]
        return st != 'Z'
    except OSError:
        return False
t0 = time.monotonic(); tool = llama = None
while time.monotonic() - t0 < 120:
    if tool is None:
        t = find(lambda p: ppid(p) == c.pid and 'kama-completion-live.py' in cmd(p))
        if t: tool = t[0]
    if tool and llama is None:
        l = find(lambda p: ppid(p) == tool and 'llama-server' in cmd(p))
        if l: llama = l[0]
    if llama and os.path.exists(f'{W}/hold/hold.json'):
        break
    time.sleep(0.05)
info = {'counter_pid': c.pid, 'tool_pid': tool, 'llama_pid': llama,
        'hold_json_present': os.path.exists(f'{W}/hold/hold.json'),
        'llama_alive_before_kill': alive(llama) if llama else None,
        'llama_cmd_is_ours': cmd(llama)[:120] if llama else None}
if not (tool and llama and info['hold_json_present']):
    os.kill(c.pid, signal.SIGKILL); print(json.dumps(info, indent=1)); sys.exit(0)
os.kill(c.pid, signal.SIGKILL)   # harness death, counter spawned by this driver
c.wait(timeout=10)
t1 = time.monotonic()
for name, pid in (('tool', tool), ('llama', llama)):
    while alive(pid) and time.monotonic() - t1 < 30:
        time.sleep(0.05)
    info[f'{name}_alive_after_counter_kill'] = alive(pid)
    info[f'{name}_dead_after_s'] = round(time.monotonic() - t1, 2)
print(json.dumps(info, indent=1))
