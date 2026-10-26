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
wd=os.path.join(S,"wd-E"); work=os.path.join(S,"w-E")
os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
out=os.path.join(S,"j-E.json")
argv=[sys.executable,REPLAY,"--receipt",RECEIPT,"--work",work,"--out",out,"--witness-dir",wd]
log=open(os.path.join(S,"replay-E.log"),"wb")
p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,cwd=S,start_new_session=True)
t0=time.time()
while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and p.poll() is None:
    time.sleep(0.05)
ready=json.load(open(os.path.join(wd,"ready.json")))
server,port=ready["pid"],ready["port"]
live=None
for e in os.listdir("/proc"):
    if not e.isdigit(): continue
    try:
        st=open(f"/proc/{e}/stat").read().rsplit(")",1)[1].split()
        if int(st[1])==p.pid: live=int(e)
    except OSError: continue
ts=time.time(); os.kill(live,signal.SIGTERM)
samples=[]
while time.time()-ts<30:
    el=round(time.time()-ts,2)
    s={"t":el,"live":alive(live),"server":alive(server),"listening":listening(port),"replay_exit":p.poll()}
    samples.append(s)
    if not s["live"] and not s["server"] and not s["listening"] and s["replay_exit"] is not None: break
    time.sleep(0.2)
rec={"tag":"E","ready":ready,"replay_pid":p.pid,"live_pid":live,"port":port,"server_pid":server,
     "signal":"SIGTERM to live child","samples_n":len(samples),"samples_first":samples[:3],"samples_last":samples[-3:],
     "server_gone_at_s":next((s["t"] for s in samples if not s["server"]),None),
     "port_closed_at_s":next((s["t"] for s in samples if not s["listening"]),None),
     "live_exit_at_s":next((s["t"] for s in samples if not s["live"]),None),
     "replay_exit":p.poll(),
     "ss":subprocess.run(["ss","-ltnp",f"sport = :{port}"],capture_output=True,text=True).stdout,
     "pgrep":subprocess.run(["pgrep","-af","llama-server"],capture_output=True,text=True).stdout}
try: rec["rerun_receipt"]=json.load(open(os.path.join(work,"rerun-receipt.json")))
except (OSError,ValueError) as exc: rec["rerun_receipt"]=f"error:{exc}"
try: rec["out_json"]=json.load(open(out))
except (OSError,ValueError) as exc: rec["out_json"]=f"error:{exc}"
log.close(); rec["replay_log"]=open(os.path.join(S,"replay-E.log"),errors="replace").read()[-1500:]
if alive(server):
    try: os.kill(server,signal.SIGKILL)
    except OSError: pass
json.dump(rec,open(os.path.join(S,"result-E.json"),"w"),indent=1)
print("E server_gone_at=",rec["server_gone_at_s"],"port_closed_at=",rec["port_closed_at_s"],
      "replay_exit=",rec["replay_exit"],"out_json=",(rec["out_json"] if isinstance(rec["out_json"],str) else {k:rec["out_json"].get(k) for k in ("match","refused","live_exit")}),
      "witness=",(rec["rerun_receipt"] if isinstance(rec["rerun_receipt"],str) else rec["rerun_receipt"].get("witness")))
