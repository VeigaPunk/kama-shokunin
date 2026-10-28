# (iii) argv: a process rewrites its own argv area via /proc/self/mem; the counter's holder_record reads it back
import os, subprocess, sys, time
sys.path.insert(0, os.environ['S_WORK']); os.environ['PYTHONDONTWRITEBYTECODE']='1'
import c1
CH = r'''
import os
st = open('/proc/self/stat').read().split(')')[1].split()
start, end = int(st[45]), int(st[46])          # arg_start, arg_end (proc_pid_stat(5) fields 48, 49)
new = b'/home/vgpnk/.local/opt/llama-b11755/llama-server\0--port\x0051333\0--model\0/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf\0--alias\0kama-completion-probe\0'
old = end - start
new = (new + b'\0' * old)[:old]
with open('/proc/self/mem', 'r+b', buffering=0) as m:
    m.seek(start); m.write(new)
import time; time.sleep(20)
'''
p = subprocess.Popen([sys.executable, '-c', CH, '--port', '1', '--model', '/tmp/decoy.gguf'])
time.sleep(0.5)
rec = c1.holder_record(p.pid, '/home/vgpnk/.local/opt/llama-b11755')
print('launched argv :', [sys.executable, '-c', '<script>', '--port', '1', '--model', '/tmp/decoy.gguf'][2:])
print('cmdline after self-rewrite:', rec['cmdline'])
p.kill(); p.wait()
