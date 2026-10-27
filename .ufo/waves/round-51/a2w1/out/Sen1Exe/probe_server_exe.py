#!/usr/bin/env python3
"""Edge battery for kama-llamacpp-live.py server_exe() at build 138af25b.

Each case builds a process whose /proc/<pid>/exe has the property under test, then
calls the tool's own server_exe(pid) (imported by path from the clone) and records
the returned dict plus independent ground truth (readlink, fstat of our own open,
sha256 of the on-disk bytes we planted).
"""
import errno, hashlib, importlib.util, json, os, shutil, signal, stat, subprocess, sys, time

S = sys.argv[1]
TOOL = sys.argv[2]
OUT = sys.argv[3]
T = os.path.join(S, 't')
os.makedirs(T, exist_ok=True)

spec = importlib.util.spec_from_file_location('live', TOOL)
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)
server_exe = live.server_exe

rows, kids = [], []


def sha(path_or_fd_bytes):
    return hashlib.sha256(path_or_fd_bytes).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def spawn(path, args=('60',)):
    p = subprocess.Popen([path] + list(args), stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    kids.append(p)
    return p


def truth(pid):
    """Ground truth independent of the tool."""
    t = {'readlink': None, 'readlink_err': None, 'own_sha': None, 'own_err': None,
         'stat': None, 'stat_err': None}
    try:
        t['readlink'] = os.readlink(f'/proc/{pid}/exe')
    except OSError as e:
        t['readlink_err'] = f'{e.errno}:{e.strerror}'
    try:
        fd = os.open(f'/proc/{pid}/exe', os.O_RDONLY)
        try:
            st = os.fstat(fd)
            h = hashlib.sha256()
            while True:
                c = os.read(fd, 1 << 20)
                if not c:
                    break
                h.update(c)
            t['own_sha'] = h.hexdigest()
            t['stat'] = {'dev': '%02x:%02x' % (os.major(st.st_dev), os.minor(st.st_dev)),
                         'inode': str(st.st_ino), 'size': st.st_size,
                         'mode_regular': stat.S_ISREG(st.st_mode)}
        finally:
            os.close(fd)
    except OSError as e:
        t['own_err'] = f'{e.errno}:{e.strerror}'
    return t


def case(name, pid, extra):
    r = server_exe(pid)
    row = {'case': name, 'pid': pid, 'result': r, 'truth': truth(pid), **extra}
    rows.append(row)
    return row


def kill(p):
    try:
        p.kill()
        p.wait(timeout=5)
    except Exception:
        pass


# ---------------------------------------------------------------- case 1: unlinked
src = os.path.join(T, 'exe-unlinked')
shutil.copy2('/usr/bin/sleep', src)
orig_sha, orig_st = sha_file(src), os.stat(src)
p = spawn(src)
time.sleep(0.3)
os.unlink(src)
time.sleep(0.05)
row = case('1-unlinked-after-exec', p.pid, {
    'planted_sha': orig_sha,
    'planted_inode': str(orig_st.st_ino),
    'on_disk_now': os.path.exists(src),
    'os_stat_path_err': None})
try:
    os.stat(src)
except OSError as e:
    rows[-1]['os_stat_path_err'] = f'{e.errno}:{e.strerror}'
r = row['result']
row['verdict'] = ('PASS-open-works-old-bytes'
                  if r.get('opened') is True and r.get('sha256') == orig_sha
                  and r.get('inode') == str(orig_st.st_ino)
                  and r.get('path', '').endswith(' (deleted)')
                  else 'FAIL')
kill(p)

# ------------------------------------------- case 2: exe path renamed over after exec
src2 = os.path.join(T, 'exe-swapped')
shutil.copy2('/usr/bin/sleep', src2)
old_sha, old_ino = sha_file(src2), str(os.stat(src2).st_ino)
p = spawn(src2)
time.sleep(0.3)
new_src = os.path.join(T, 'exe-swapped.new')
shutil.copy2('/usr/bin/true', new_src)
new_sha, new_ino = sha_file(new_src), str(os.stat(new_src).st_ino)
os.replace(new_src, src2)          # the path now holds different bytes, same name
time.sleep(0.05)
row = case('2-renamed-over-after-exec', p.pid, {
    'old_sha': old_sha, 'old_inode': old_ino, 'new_sha': new_sha, 'new_inode': new_ino,
    'path_sha_now': sha_file(src2), 'path_inode_now': str(os.stat(src2).st_ino)})
r = row['result']
row['verdict'] = ('PASS-runs-old-bytes' if r.get('opened') is True
                  and r.get('sha256') == old_sha and r.get('inode') == old_ino
                  and sha_file(src2) == new_sha
                  else 'FAIL')
row['path_vs_fd_identity'] = ('diverged: fd inode %s vs path inode %s' % (r.get('inode'), row['path_inode_now'])
                              if r.get('inode') != row['path_inode_now'] else 'same')
kill(p)

# ------------------------------------------------ case 3: modified in place (ETXTBSY)
src3 = os.path.join(T, 'exe-inplace')
shutil.copy2('/usr/bin/sleep', src3)
base_sha = sha_file(src3)
p = spawn(src3)
time.sleep(0.3)
w = {'r+b': None, 'wb-truncate': None, 'os.truncate': None, 'remove': True}
try:
    fh = open(src3, 'r+b'); fh.close(); w['r+b'] = 'unexpected-ok'
except OSError as e:
    w['r+b'] = f'{errno.errorcode.get(e.errno, e.errno)}:{e.strerror}'
try:
    open(src3, 'wb').close(); w['wb-truncate'] = 'unexpected-ok'
except OSError as e:
    w['wb-truncate'] = f'{errno.errorcode.get(e.errno, e.errno)}:{e.strerror}'
try:
    os.truncate(src3, 0); w['os.truncate'] = 'unexpected-ok'
except OSError as e:
    w['os.truncate'] = f'{errno.errorcode.get(e.errno, e.errno)}:{e.strerror}'
try:
    os.unlink(src3); w['remove'] = 'unlinked while running'
except OSError as e:
    w['remove'] = f'{errno.errorcode.get(e.errno, e.errno)}:{e.strerror}'
row = case('3-modified-in-place', p.pid, {'planted_sha': base_sha, 'write_attempts': w})
r = row['result']
row['verdict'] = ('PASS-ETXTBSY-blocks-inplace' if 'ETXTBSY' in w['r+b']
                  and r.get('opened') is True and r.get('sha256') == base_sha else 'FAIL')
kill(p)

# -------------------------------------------------------------- case 4: zombie child
p = subprocess.Popen(['/usr/bin/sleep', '0'])
zpid = p.pid
for _ in range(200):
    try:
        st = open(f'/proc/{zpid}/stat').read().rsplit(') ', 1)[1].split()[0]
    except OSError:
        st = 'gone'
    if st == 'Z':
        break
    time.sleep(0.01)
zstate = st
row = case('4-zombie-child', zpid, {'proc_state': zstate})
r = row['result']
row['verdict'] = ('PASS-fails-closed' if r.get('opened') is False else 'FAIL-opened-on-zombie')
row['reason_note'] = r.get('reason')
p.wait()

# ------------------------------------------------------- case 5: pid owned by root
row = case('5-pid1-root-owned', 1, {})
r = row['result']
row['verdict'] = 'PASS-fails-closed' if r.get('opened') is False else 'FAIL-opened-pid1'

row_k = case('5b-kthread-pid2', 2, {})
row_k['verdict'] = 'PASS-fails-closed' if row_k['result'].get('opened') is False else 'FAIL-opened-kthread'

# ---------------------------- case 6a: same uid, NOT a descendant (yama scope=1 here)
out = subprocess.run(['bash', '-c', 'setsid sleep 45 >/dev/null 2>&1 & echo $!'],
                     capture_output=True, text=True)
time.sleep(0.3)
npid = int(out.stdout.strip())
ppid = open(f'/proc/{npid}/stat').read().rsplit(') ', 1)[1].split()[1]
row = case('6a-nondescendant-same-uid', npid, {'ppid': ppid, 'yamascope': open('/proc/sys/kernel/yama/ptrace_scope').read().strip()})
r = row['result']
row['verdict'] = ('PASS-opened' if r.get('opened') is True else 'FAIL-fail-closed-' + str(r.get('reason')))
os.kill(npid, signal.SIGKILL)

# ------------------------------ case 6b: same uid, non-dumpable (setuid-like, no setuid)
nd = subprocess.Popen([sys.executable, '-c',
                       'import ctypes,time; ctypes.CDLL("libc.so.6").prctl(4,0,0,0,0); time.sleep(45)'],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
kids.append(nd)
time.sleep(0.5)
row = case('6b-nondumpable-same-uid', nd.pid, {
    'uid': os.stat(f'/proc/{nd.pid}').st_uid,
    'status_uid': [l.strip() for l in open(f'/proc/{nd.pid}/status') if l.startswith(('Uid:', 'NoNewPrivs'))]})
r = row['result']
row['verdict'] = 'PASS-fails-closed' if r.get('opened') is False else 'FAIL-opened-nondumpable-'
kill(nd)

# ------------------------------------------- case 7: shebang script (image = interpreter)
sh7 = os.path.join(T, 'sleeper.sh')
with open(sh7, 'w') as fh:
    fh.write('#!/bin/sh\nexec sleep 45\n')
os.chmod(sh7, 0o755)
p = spawn(sh7, ())
time.sleep(0.3)
row = case('7-shebang-target', p.pid, {'script_sha': sha_file(sh7),
                                       'bash_sha': sha_file('/usr/bin/bash')})
r = row['result']
row['verdict'] = ('PASS-image-is-interpreter' if r.get('path') == '/usr/bin/bash'
                  and r.get('sha256') == sha_file('/usr/bin/bash') else 'INFO')
kill(p)

# --------------------------------- case 8: exe chmod 000 after exec (perm bypass check)
src8 = os.path.join(T, 'exe-chmod000')
shutil.copy2('/usr/bin/sleep', src8)
p8_sha = sha_file(src8)
p = spawn(src8)
time.sleep(0.3)
os.chmod(src8, 0o000)
row = case('8-exe-chmod000-after-exec', p.pid, {'planted_sha': p8_sha,
                                                'mode': oct(os.stat(src8).st_mode & 0o777)})
r = row['result']
row['verdict'] = ('PASS-magic-link-ignores-file-mode' if r.get('opened') is True
                  and r.get('sha256') == p8_sha else 'FAIL/' + str(r.get('reason')))
os.chmod(src8, 0o755)
kill(p)

# ------------------------------------------------- case 9: fd leak over N calls + exit path
src9 = os.path.join(T, 'exe-leak')
shutil.copy2('/usr/bin/sleep', src9)
p = spawn(src9)
time.sleep(0.3)
def nfd():
    return len(os.listdir('/proc/self/fd'))
before = nfd()
for _ in range(500):
    server_exe(p.pid)
after = nfd()
# error path: non-existent pid must not leak either
for _ in range(500):
    server_exe(999999)
after_err = nfd()
rows.append({'case': '9-fd-leak', 'fd_before': before, 'fd_after_500_ok': after,
             'fd_after_500_err': after_err,
             'verdict': 'PASS-no-leak' if before == after == after_err else 'FAIL-LEAK'})
kill(p)

# ------------------------------------- case 10: reused/gone pid after reaping (ENOENT)
p = subprocess.Popen(['/usr/bin/sleep', '0'])
gp = p.pid
p.wait()
time.sleep(0.05)
row = case('10-reaped-pid', gp, {})
r = row['result']
row['verdict'] = ('PASS-fails-closed' if r.get('opened') is False else 'FAIL-opened-reaped')

json.dump(rows, open(OUT, 'w'), indent=1, default=str)
for r in rows:
    print(json.dumps({k: r[k] for k in ('case', 'pid', 'verdict') if k in r},
                     default=str), '|', json.dumps(r.get('result') or
                     {k: r[k] for k in r if k.startswith('fd_')}, default=str)[:400])
