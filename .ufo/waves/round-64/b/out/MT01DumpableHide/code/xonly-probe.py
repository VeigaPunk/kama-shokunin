import os, subprocess, sys, time
child = subprocess.Popen(['/fast/scratch/hyaku/kama-r64/b/MT01DumpableHide/xonly/py-xonly', '-c', 'import time;print("ready",flush=True);time.sleep(30)'], stdout=subprocess.PIPE, text=True)
print('child', child.stdout.readline().strip(), child.pid)
pid = child.pid
try:
    st = os.stat(f'/proc/{pid}').st_uid
except OSError as e:
    st = f'err{e.errno}'
try:
    os.listdir(f'/proc/{pid}/fd'); fd = 'readable'
except OSError as e:
    fd = f'err{e.errno}'
print('st_uid', st, 'fd', fd, [l.strip() for l in open(f'/proc/{pid}/status') if l.startswith('Uid:')][0])
child.kill()
