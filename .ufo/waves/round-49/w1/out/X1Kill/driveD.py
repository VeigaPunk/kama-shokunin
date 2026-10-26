import json,os,signal,socket,subprocess,sys,time
S=os.path.dirname(os.path.abspath(__file__))
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY=os.path.join(LANE,"tools","kama-live-replay.py")
RECEIPT=os.path.join(LANE,".ufo/waves/round-48/c2/live/receipt-1.json")
def alive(pid):
    if not pid: return False
    try: os.kill(pid,0)
    except ProcessLookupError: return False
    try:
        st=open(f"/proc/{pid}/stat").read().rsplit(")",1)[1].split()[0]
        return st!="Z"
    except OSError: return False
def listening(port):
    try:
        with socket.create_connection(("127.0.0.1",port),timeout=0.4): return True
    except OSError: return False
wd=os.path.join(S,"wd-D"); work=os.path.join(S,"w-D")
os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
out=os.path.join(S,"j-D.json")
argv=[sys.executable,REPLAY,"--receipt",RECEIPT,"--work",work,"--out",out,"--witness-dir",wd]
log=open(os.path.join(S,"replay-D.log"),"wb")
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
        if int(st[1])==p.pid:
            live=int(e)
    except OSError: continue
os.kill(p.pid,signal.SIGTERM)
ts=time.time()
rec={"tag":"D","ready":ready,"replay_pid":p.pid,"live_pid":live,"port":port,
     "server_pid":server,"killed_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
samples=[]
while time.time()-ts<180:
    el=round(time.time()-ts,2)
    s={"t":el,"live":alive(live),"server":alive(server),"listening":listening(port),"replay_exit":p.poll()}
    samples.append(s)
    if not s["server"] and not s["listening"] and not s["live"]:
        break
    time.sleep(0.25)
rec["samples"]=samples[-6:]; rec["samples_n"]=len(samples)
rec["orphan_lifetime_s"]=round(time.time()-ts,2)
rec["server_gone_at_s"]=next((s["t"] for s in samples if not s["server"]),None)
rec["port_closed_at_s"]=next((s["t"] for s in samples if not s["listening"]),None)
rec["live_exit_at_s"]=next((s["t"] for s in samples if not s["live"]),None)
rec["after"]={"server":alive(server),"live":alive(live),"listening":listening(port),
              "pgrep":subprocess.run(["pgrep","-af","llama-server"],capture_output=True,text=True).stdout,
              "ss":subprocess.run(["ss","-ltnp",f"sport = :{port}"],capture_output=True,text=True).stdout}
try: rec["rerun_receipt_exists"]=os.path.isfile(os.path.join(work,"rerun-receipt.json"))
except OSError: rec["rerun_receipt_exists"]=None
try: rec["rerun_receipt"]=json.load(open(os.path.join(work,"rerun-receipt.json")))
except (OSError,ValueError) as exc: rec["rerun_receipt"]=f"error:{exc}"
rec["replay_exit"]=p.poll()
log.close()
rec["replay_log"]=open(os.path.join(S,"replay-D.log"),errors="replace").read()[-2500:]
json.dump(rec,open(os.path.join(S,"result-D.json"),"w"),indent=1)
print("D orphan_lifetime_s=",rec["orphan_lifetime_s"],"server_gone_at=",rec["server_gone_at_s"],
      "port_closed_at=",rec["port_closed_at_s"],"live_exit_at=",rec["live_exit_at_s"],
      "rerun_receipt=",rec["rerun_receipt_exists"])
