import os, sys, socket, subprocess, time, ctypes
sys.path.insert(0, os.environ['S_WORK']); os.environ['PYTHONDONTWRITEBYTECODE']='1'
import c1
CH = r'''
import ctypes, socket, sys, time
fd = int(sys.argv[1]); ctypes.CDLL(None).prctl(4, 0, 0, 0, 0)
s_=socket.socket(fileno=fd); print("ready", flush=True); time.sleep(20)
'''
# (i) a non-dumpable own-uid holder that started BEFORE the tool: unreadable_old, never graded
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1',0)); s.listen(4)
port = s.getsockname()[1]
A = subprocess.Popen([sys.executable,'-c','import socket,time,sys;s_=socket.socket(fileno=int(sys.argv[1]));print("ready",flush=True);time.sleep(20)', str(s.fileno())], pass_fds=(s.fileno(),), stdout=subprocess.PIPE, text=True)
B = subprocess.Popen([sys.executable,'-c',CH,str(s.fileno())], pass_fds=(s.fileno(),), stdout=subprocess.PIPE, text=True)
A.stdout.readline(); B.stdout.readline(); s.close(); time.sleep(0.3)
time.sleep(0.2)
TOOL = subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'])   # the 'tool' started AFTER B
time.sleep(0.2)
tool_ticks = c1.start_ticks_of(TOOL.pid)
hold_doc = {'pid': A.pid, 'port': port, 'schema':'kama-completion-hold/v1'}
raw = c1.collect(port, hold_doc, time.time_ns(), 0, TOOL.pid, tool_ticks, '/home/vgpnk/.local/opt/llama-b11755/llama-server', '/x/model.gguf')
print("(i) holders=", [h['pid'] for h in raw['holders']], "A=",A.pid, "B(nondump, pre-tool)=",B.pid)
print("    unreadable_own=", raw['unreadable_own'], " unreadable_old=", raw['unreadable_old'])
g = c1.grade_binding(raw)
print("    grade_binding bind_holders=", g['bind_holders'], " (requires holders=={hold pid} and not unreadable_own)")
for p in (A,B,TOOL): p.kill(); p.wait()
