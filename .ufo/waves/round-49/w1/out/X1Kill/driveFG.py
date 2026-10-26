import json,os,signal,socket,subprocess,sys,time
S=os.path.dirname(os.path.abspath(__file__))
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"
PATCHED=os.path.join(S,"prop","kama-live-replay.py")
LANE_LIVE=os.path.join(LANE,"tools","kama-llamacpp-live.py")
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
def run(tag, sig):
    wd=os.path.join(S,f"wd-{tag}"); work=os.path.join(S,f"w-{tag}")
    os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
    out=os.path.join(S,f"j-{tag}.json")
    argv=[sys.executable,PATCHED,"--receipt",RECEIPT,"--work",work,"--out",out,
          "--witness-dir",wd,"--live",LANE_LIVE]
    log=open(os.path.join(S,f"replay-{tag}.log"),"wb")
    p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,cwd=S,start_new_session=True)
    t0=time.time()
    while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and p.poll() is None:
        time.sleep(0.05)
    if not os.path.exists(os.path.join(wd,"ready.json")):
        return {"tag":tag,"no_ready":True,"replay_exit":p.poll(),
                "log":open(os.path.join(S,f"replay-{tag}.log"),errors="replace").read()[-1500:]}
    ready=json.load(open(os.path.join(wd,"ready.json")))
    server,port=ready["pid"],ready["port"]
    live=None
    for e in os.listdir("/proc"):
        if not e.isdigit(): continue
        try:
            st=open(f"/proc/{e}/stat").read().rsplit(")",1)[1].split()
            if int(st[1])==p.pid: live=int(e)
        except OSError: continue
    before={"server":alive(server),"listening":listening(port),
            "ss":subprocess.run(["ss","-ltnp",f"sport = :{port}"],capture_output=True,text=True).stdout,
            "live_ppid":int(open(f"/proc/{live}/stat").read().rsplit(")",1)[1].split()[1]) if live else None,
            "live_session_id":int(open(f"/proc/{live}/stat").read().rsplit(")",1)[1].split()[3]) if live else None,
            "replay_pid":p.pid}
    ts=time.time(); os.kill(p.pid,sig)
    samples=[]
    while time.time()-ts<20:
        el=round(time.time()-ts,2)
        s={"t":el,"live":alive(live),"server":alive(server),"listening":listening(port),"replay_exit":p.poll()}
        samples.append(s)
        if not s["server"] and not s["listening"] and s["replay_exit"] is not None: break
        time.sleep(0.2)
    rec={"tag":tag,"sig":signal.Signals(sig).name,"ready":ready,"before":before,
         "server_gone_at_s":next((s["t"] for s in samples if not s["server"]),None),
         "port_closed_at_s":next((s["t"] for s in samples if not s["listening"]),None),
         "live_gone_at_s":next((s["t"] for s in samples if not s["live"]),None),
         "replay_exit":p.poll(),"samples_n":len(samples),"samples_last":samples[-3:],
         "ss":subprocess.run(["ss","-ltnp",f"sport = :{port}"],capture_output=True,text=True).stdout,
         "hypothesis_held":(not alive(server)) and (not listening(port))}
    try: rec["out_json"]=json.load(open(out))
    except (OSError,ValueError) as exc: rec["out_json"]=f"error:{exc}"
    log.close(); rec["log_tail"]=open(os.path.join(S,f"replay-{tag}.log"),errors="replace").read()[-1200:]
    for pid in (server,live):
        if alive(pid):
            try: os.kill(pid,signal.SIGKILL)
            except OSError: pass
    try: os.killpg(p.pid,signal.SIGKILL)
    except OSError: pass
    json.dump(rec,open(os.path.join(S,f"result-{tag}.json"),"w"),indent=1)
    j=rec["out_json"]
    print(tag,rec["sig"],"server_gone_at=",rec["server_gone_at_s"],"port_closed_at=",rec["port_closed_at_s"],
          "live_gone_at=",rec["live_gone_at_s"],"replay_exit=",rec["replay_exit"],
          "refused=",(j.get("refused") if isinstance(j,dict) else j),flush=True)
run("F",signal.SIGTERM)
run("G",signal.SIGKILL)
