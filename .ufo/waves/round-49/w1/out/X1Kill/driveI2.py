import json,os,signal,socket,subprocess,sys,time
S=os.path.dirname(os.path.abspath(__file__))
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY=os.path.join(LANE,"tools","kama-live-replay.py")
RECEIPT=os.path.join(LANE,".ufo/waves/round-48/c2/live/receipt-1.json")
def alive(pid):
    if not pid: return False
    try: os.kill(pid,0)
    except ProcessLookupError: return False
    try: return open(f"/proc/{pid}/stat").read().rsplit(")",1)[1].split()[0]!="Z"
    except OSError: return False
def listening(port):
    try:
        with socket.create_connection(("127.0.0.1",port),timeout=0.4): return True
    except OSError: return False
def children(pid):
    out=[]
    for e in os.listdir("/proc"):
        if not e.isdigit(): continue
        try:
            st=open(f"/proc/{e}/stat").read().rsplit(")",1)[1].split()
            if int(st[1])==pid: out.append(int(e))
        except OSError: continue
    return sorted(out)
def name(pid):
    try: return open(f"/proc/{pid}/cmdline","rb").read().decode("utf-8","replace").split("\0")[0]
    except OSError: return None
wd=os.path.join(S,"wd-I2"); work=os.path.join(S,"w-I2"); os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
outj=os.path.join(S,"j-I2.json")
pidfile=os.path.join(S,"counter-shape-pids.txt")
if os.path.exists(pidfile): os.unlink(pidfile)
env=dict(os.environ, HOME=S, XDG_CACHE_HOME=os.path.join(S,"cache"), TMPDIR=S)
par=subprocess.Popen([sys.executable, os.path.join(S,"counter_shape.py"), S, REPLAY, RECEIPT, wd, work, outj],
                     env=env, cwd=S, start_new_session=True)
t0=time.time()
while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and par.poll() is None:
    time.sleep(0.05)
cpids=[int(x) for x in open(pidfile).read().split()]
counter_pid,replay_pid=cpids[0],cpids[1]
ready=json.load(open(os.path.join(wd,"ready.json")))
live=next((c for c in children(replay_pid)),None)
rec={"tag":"I2","counter_pid":counter_pid,"parent_launcher_pid":par.pid,"replay_pid":replay_pid,
     "live_pid":live,"server_pid":ready["pid"],"port":ready["port"],"ready":ready,
     "names":{"counter":name(counter_pid),"replay":name(replay_pid),"live":name(live),"server":name(ready["pid"])},
     "ppid_check":{"replay_parent":int(open(f"/proc/{replay_pid}/stat").read().rsplit(')',1)[1].split()[1]),
                   "live_parent":int(open(f"/proc/{live}/stat").read().rsplit(')',1)[1].split()[1])}}
os.kill(counter_pid, signal.SIGTERM)
ts=time.time(); samples=[]
while time.time()-ts<15:
    el=round(time.time()-ts,2)
    s={"t":el,"parent":alive(par.pid),"counter":alive(counter_pid),"replay":alive(replay_pid),
       "live":alive(live),"server":alive(ready["pid"]),"listening":listening(ready["port"])}
    samples.append(s); time.sleep(0.25)
rec["samples_first"]=samples[:3]; rec["samples_last"]=samples[-3:]; rec["samples_n"]=len(samples)
rec["at_15s"]={"counter":alive(counter_pid),"replay":alive(replay_pid),"live":alive(live),
               "server":alive(ready["pid"]),"listening":listening(ready["port"]),
               "server_cmdline":(open(f"/proc/{ready['pid']}/cmdline","rb").read().decode("utf-8","replace").replace("\0"," ") if alive(ready['pid']) else None),
               "ss":subprocess.run(["ss","-ltnp",f"sport = :{ready['port']}"],capture_output=True,text=True).stdout}
steps=[]
for pid,nm in ((replay_pid,"replay"),(live,"live"),(ready["pid"],"server")):
    if alive(pid):
        os.kill(pid,signal.SIGTERM); time.sleep(1.0)
        steps.append({"sigterm":nm,"pid":pid,"alive_after_1s":alive(pid)})
    else: steps.append({"sigterm":nm,"pid":pid,"already_dead":True})
for pid,nm in ((live,"live"),(ready["pid"],"server")):
    if alive(pid):
        os.kill(pid,signal.SIGKILL); time.sleep(0.5)
        steps.append({"sigkill":nm,"pid":pid,"alive_after_0_5s":alive(pid)})
try: os.killpg(par.pid, signal.SIGKILL)
except OSError: pass
time.sleep(1)
rec["cleanup_steps"]=steps
rec["after_cleanup"]={"server":alive(ready["pid"]),"live":alive(live),"replay":alive(replay_pid),
                      "listening":listening(ready["port"]),
                      "ss":subprocess.run(["ss","-ltnp",f"sport = :{ready['port']}"],capture_output=True,text=True).stdout}
json.dump(rec,open(os.path.join(S,"result-I2.json"),"w"),indent=1)
print("I2 names:",rec["names"])
print("I2 at_15s:",{k:rec["at_15s"][k] for k in ("counter","replay","live","server","listening")})
print("I2 cleanup:",steps)
print("I2 after:",{k:rec["after_cleanup"][k] for k in ("server","live","replay","listening")})
