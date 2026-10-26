import json,os,signal,socket,subprocess,sys,time
S=os.path.dirname(os.path.abspath(__file__))
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
LANE_REPLAY=os.path.join(LANE,"tools","kama-live-replay.py")
PATCHED_LIVE=os.path.join(S,"fake-lane","tools","kama-llamacpp-live.py")
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
def start(tag):
    wd=os.path.join(S,f"wd-{tag}"); work=os.path.join(S,f"w-{tag}")
    os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
    out=os.path.join(S,f"j-{tag}.json")
    argv=[sys.executable,LANE_REPLAY,"--receipt",RECEIPT,"--work",work,"--out",out,
          "--witness-dir",wd,"--live",PATCHED_LIVE]
    log=open(os.path.join(S,f"replay-{tag}.log"),"wb")
    p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,cwd=S,start_new_session=True)
    t0=time.time()
    while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and p.poll() is None:
        time.sleep(0.05)
    ready=json.load(open(os.path.join(wd,"ready.json")))
    live=None
    for e in os.listdir("/proc"):
        if not e.isdigit(): continue
        try:
            st=open(f"/proc/{e}/stat").read().rsplit(")",1)[1].split()
            if int(st[1])==p.pid: live=int(e)
        except OSError: continue
    return dict(tag=tag,wd=wd,work=work,out=out,p=p,live=live,log=log,
                ready=ready,server=ready["pid"],port=ready["port"],
                replay_argv=" ".join(argv))
# H1: cooperated release, patched live only
h1=start("H1")
t=time.time(); open(os.path.join(h1["wd"],"release"),"w").write("x1kill\n")
try: code=h1["p"].wait(timeout=60)
except subprocess.TimeoutExpired:
    h1["p"].kill(); code=None
j=json.load(open(h1["out"]))
rr=json.load(open(j["rerun_receipt"])) if j.get("rerun_receipt") else {}
recH1={"tag":"H1","replay_argv":h1["replay_argv"],"replay_exit":code,"match":j.get("match"),
       "refused":j.get("refused"),"mismatches":j.get("mismatches"),
       "witness":rr.get("witness"),"outcome":rr.get("outcome"),
       "server_alive_after":alive(h1["server"]),"port_listening_after":listening(h1["port"]),
       "wait_s":round(time.time()-t,2)}
print("H1",recH1,flush=True)
json.dump(recH1,open(os.path.join(S,"result-H1.json"),"w"),indent=1)
# H2: SIGTERM the (unpatched) replay; patched live tool must abort its hold when orphaned
h2=start("H2")
ts=time.time(); os.kill(h2["p"].pid,signal.SIGTERM)
samples=[]
while time.time()-ts<20:
    el=round(time.time()-ts,2)
    s={"t":el,"live":alive(h2["live"]),"server":alive(h2["server"]),"listening":listening(h2["port"])}
    samples.append(s)
    if not s["server"] and not s["listening"] and not s["live"]: break
    time.sleep(0.2)
recH2={"tag":"H2","replay_argv":h2["replay_argv"],
       "server_gone_at_s":next((s["t"] for s in samples if not s["server"]),None),
       "port_closed_at_s":next((s["t"] for s in samples if not s["listening"]),None),
       "live_gone_at_s":next((s["t"] for s in samples if not s["live"]),None),
       "replay_exit":h2["p"].poll(),"samples_last":samples[-3:],
       "ss":subprocess.run(["ss","-ltnp",f"sport = :{h2['port']}"],capture_output=True,text=True).stdout}
try: recH2["rerun_receipt_witness"]=json.load(open(os.path.join(h2["work"],"rerun-receipt.json"))).get("witness")
except (OSError,ValueError) as exc: recH2["rerun_receipt_witness"]=f"error:{exc}"
print("H2",{k:recH2[k] for k in ("server_gone_at_s","port_closed_at_s","live_gone_at_s","replay_exit","rerun_receipt_witness")},flush=True)
json.dump(recH2,open(os.path.join(S,"result-H2.json"),"w"),indent=1)
for h in (h1,h2):
    for pid in (h["server"],h["live"]):
        if alive(pid):
            try: os.kill(pid,signal.SIGKILL)
            except OSError: pass
    try: os.killpg(h["p"].pid,signal.SIGKILL)
    except OSError: pass
    h["log"].close()
