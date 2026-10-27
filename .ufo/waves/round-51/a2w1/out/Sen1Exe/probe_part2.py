#!/usr/bin/env python3
"""Battery part 2: identity-collapse, namespace, shebang, and consumer-semantics edges."""
import errno, hashlib, importlib.util, json, os, shutil, stat, subprocess, sys, time

S, TOOL, COUNTER, OUT = sys.argv[1:5]
T = os.path.join(S, 't2')
os.makedirs(T, exist_ok=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


live = load('live', TOOL)
counter = load('counter', COUNTER)
rows = []


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def idd(st):
    return "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)), str(st.st_ino)


def spawn(p):
    return subprocess.Popen([p, '45'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def kill(p):
    try:
        p.kill(); p.wait(5)
    except Exception:
        pass


# ---- 11a: plain decoy (exec an identical-bytes file elsewhere) must be caught by inode
host = os.path.join(T, 'host-install')      # stands in for ~/.local/opt/.../llama-server
member = os.path.join(T, 'member')          # stands in for <work>/server/<member>
shutil.copy2('/usr/bin/sleep', host)
shutil.copy2('/usr/bin/sleep', member)
frozen = sha_file(member)
p = spawn(host)                              # decoy execs the host file, never the member
time.sleep(0.3)
r = live.server_exe(p.pid)
got = (r['dev'], r['inode'])
want = idd(os.stat(member))
rows.append({'case': '11a-decoy-exec-host-file', 'sha_equal': r['sha256'] == frozen,
             'got': got, 'want': want, 'own_predicate': got == want,
             'verdict': 'CAUGHT-inode-differs' if got != want else 'MISSED'})
kill(p)

# ---- 11b: hardlink collapse (same filesystem): member unlinked, hardlinked to host
member2 = os.path.join(T, 'member2')
shutil.copy2('/usr/bin/sleep', member2)
os.unlink(member2)
os.link(host, member2)                       # the decoy puts the host file at the member path
p = spawn(host)                              # and execs it
time.sleep(0.3)
r = live.server_exe(p.pid)
got = (r['dev'], r['inode'])
want = idd(os.stat(member2))
rows.append({'case': '11b-hardlink-collapse', 'sha_equal': r['sha256'] == frozen,
             'got': got, 'want': want, 'own_predicate': got == want,
             'nlink_now': os.stat(member2).st_nlink,
             'verdict': 'PASSES-own-leg (identity indistinguishable)'
                        if got == want else 'caught'})
kill(p)

# device numbers, for the hardlink-feasibility condition
dev_rows = {}
for pth in ('/fast', '/home', os.path.dirname(S)):
    st = os.stat(pth)
    dev_rows[pth] = (st.st_dev, "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)))
rows.append({'case': '11c-hardlink-cross-device', 'devs': dev_rows,
             'exdev_expected': dev_rows['/fast'][0] != dev_rows['/home'][0]})

# ---- 12: mount-namespace disguise (unprivileged userns + bind mount)
m12_member = os.path.join(T, 'ns-member')
shutil.copy2('/usr/bin/true', m12_member)    # on-disk bytes differ from the image that will run
inner = ('mount --bind /usr/bin/sleep %s && exec %s 45' % (m12_member, m12_member))
us = subprocess.Popen(['unshare', '-Ur', '-m', 'sh', '-c', inner],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(0.8)
if us.poll() is not None:
    o, e = us.communicate()
    rows.append({'case': '12-userns-bindmount', 'verdict': 'SETUP-FAILED',
                 'stderr': e.decode()[-400:], 'rc': us.returncode})
else:
    r = live.server_exe(us.pid)
    got = (r.get('dev'), r.get('inode'))
    want = idd(os.stat(m12_member))
    rows.append({'case': '12-userns-bindmount', 'server_exe': r,
                 'member_dev_inode': want, 'own_predicate': got == want,
                 'member_sha_outside': sha_file(m12_member),
                 'verdict': 'CAUGHT-inode-differs' if got != want
                            else 'MISSED-identity-collapse'})
    kill(us)

# ---- 13a: shebang script that does not exec -> image is the interpreter
script = os.path.join(T, 'sleeper.sh')
open(script, 'w').write('#!/bin/sh\nsleep 45\n')
os.chmod(script, 0o755)
p = spawn(script)
time.sleep(0.3)
r = live.server_exe(p.pid)
rows.append({'case': '13a-shebang-no-exec', 'script_sha': sha_file(script),
             'server_exe': r, 'bash_sha': sha_file('/usr/bin/bash'),
             'verdict': 'image-is-interpreter' if r.get('path') in ('/usr/bin/bash', '/bin/bash')
                        and r.get('sha256') == sha_file('/usr/bin/bash') else 'OTHER'})
kill(p)

# ---- 13b: replay consumer semantics for an unlinked member (kama-live-replay.py:359)
m13 = os.path.join(T, 'member13')
shutil.copy2('/usr/bin/sleep', m13)
p = spawn(m13)
time.sleep(0.3)
os.unlink(m13)
se = live.server_exe(p.pid)
out = {'case': '13b-replay-consumer-unlinked-member', 'server_exe': se}
try:
    own = os.stat(m13)                        # kama-live-replay.py:359
    out['os_stat'] = 'ok'
    out['verdict'] = 'MISSED'
except OSError as e:
    out['os_stat_err'] = f'{e.errno}:{e.strerror}'
    out['verdict'] = 'replay raises OSError -> Refused(could-not-run), exit 2 (fail closed)'
rows.append(out)
kill(p)

# ---- 13c: replay consumer semantics for a swapped member (inode mismatch branch)
m14 = os.path.join(T, 'member14')
shutil.copy2('/usr/bin/sleep', m14)
p = spawn(m14)
time.sleep(0.3)
shutil.copy2('/usr/bin/true', m14 + '.new')
os.replace(m14 + '.new', m14)
se = live.server_exe(p.pid)
own_id = idd(os.stat(m14))
rows.append({'case': '13c-replay-consumer-swapped-member', 'server_exe_di': (se['dev'], se['inode']),
             'os_stat_di': own_id,
             'mismatch': (se['dev'], se['inode']) != own_id,
             'verdict': 'mismatch appended -> exit 1 (fail closed)'})
kill(p)

# ---- 14: counter own_exe fd hygiene over 300 calls, plus its member-path failure branch
m15 = os.path.join(T, 'member15')
shutil.copy2('/usr/bin/sleep', m15)
p = spawn(m15)
time.sleep(0.3)
nfd = lambda: len(os.listdir('/proc/self/fd'))
before = nfd()
probs = []
for _ in range(300):
    counter.own_exe(p.pid, m15, probs)
mid = nfd()
for _ in range(50):
    counter.own_exe(p.pid, m15 + '.nope', probs)
after = nfd()
rows.append({'case': '14-own_exe-fd', 'fd_before': before, 'fd_after_300': mid,
             'fd_after_missing_member': after, 'problems': probs[:2],
             'verdict': 'PASS-no-leak' if before == mid == after else 'LEAK'})
kill(p)

json.dump(rows, open(OUT, 'w'), indent=1, default=str)
print(json.dumps(rows, indent=1)[:6000])
