"""Current lane worktree: (W1) SIGTERM the replay while held; (W2) SIGTERM a counter-shape
parent of the replay (the shape at round49-replay-witness-audit.py:297-298)."""
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
def obs(port,server,live,replay,counter=None,secs=15):
    ts=time.time(); samples=[]
    while time.time()-ts<secs:
        el=round(time.time()-ts,2)
        s={"t":el,"replay":alive(replay),"live":alive(live),"server":alive(server),"listening":listening(port)}
        if counter is not None: s["counter"]=alive(counter)
        samples.append(s); time.sleep(0.25)
    return samples
def launch(tag, via_parent):
    wd=os.path.join(S,f"wd-{tag}"); work=os.path.join(S,f"w-{tag}")
    os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
    outj=os.path.join(S,f"j-{tag}.json")
    log=open(os.path.join(S,f"replay-{tag}.log"),"wb")
    if via_parent:
        par=subprocess.Popen([sys.executable,os.path.join(S,"counter_shape.py"),S,REPLAY,RECEIPT,wd,work,outj],
                             env=dict(os.environ,HOME=S,XDG_CACHE_HOME=os.path.join(S,"cache"),TMPDIR=S),
                             cwd=S,start_new_session=True)
        t0=time.time()
        while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and par.poll() is None:
            time.sleep(0.05)
        counter_pid,replay_pid=[int(x) for x in open(os.path.join(S,"counter-shape-pids.txt")).read().split()]
        return dict(tag=tag,par=par,counter=counter_pid,replay=replay_pid,wd=wd,work=work,outj=outj,log=log,via_parent=True)
    p=subprocess.Popen([sys.executable,REPLAY,"--receipt",RECEIPT,"--work",work,"--out",outj,"--witness-dir",wd],
                       stdout=log,stderr=subprocess.STDOUT,cwd=S,start_new_session=True)
    t0=time.time()
    while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and p.poll() is None:
        time.sleep(0.05)
    return dict(tag=tag,par=p,counter=None,replay=p.pid,wd=wd,work=work,outj=outj,log=log,via_parent=False)
def finish(ctx, ready, live, server, port, rec):
    rec["after_15s"]={"server":alive(server),"listening":listening(port),"live":alive(live),
                      "replay":alive(ctx["replay"]),
                      "ss":subprocess.run(["ss","-ltnp",f"sport = :{port}"],capture_output=True,text=True).stdout,
                      "ready_json_left":os.path.exists(os.path.join(ctx["wd"],"ready.json")),
                      "release_left":os.path.exists(os.path.join(ctx["wd"],"release"))}
    # cleanup
    open(os.path.join(ctx["wd"],"release"),"w").write("x1kill\n"); time.sleep(2)
    rec["after_release"]={"server":alive(server),"live":alive(live),"listening":listening(port)}
    for pid in (live,server):
        if alive(pid):
            try: os.kill(pid,signal.SIGTERM)
            except OSError: pass
    time.sleep(2)
    for pid in (live,server):
        if alive(pid):
            try: os.kill(pid,signal.SIGKILL)
            except OSError: pass
    if ctx["counter"] and alive(ctx["counter"]):
        try: os.kill(ctx["counter"],signal.SIGKILL)
        except OSError: pass
    try: os.killpg(ctx["par"].pid,signal.SIGKILL)
    except OSError: pass
    ctx["log"].close()
    rec["after_cleanup"]={"server":alive(server),"live":alive(live),"listening":listening(port)}
    json.dump(rec,open(os.path.join(S,f"result-{ctx['tag']}.json"),"w"),indent=1)
    print(ctx["tag"],{k:rec.get(k) for k in ("signal","gone_after_s","hypothesis_held","after_15s_observed")},flush=True)
def w1():
    ctx=launch("W1",False)
    ready=json.load(open(os.path.join(ctx["wd"],"ready.json")))
    server,port=ready["pid"],ready["port"]; live=next((c for c in children(ctx["replay"])),None)
    os.kill(ctx["replay"],signal.SIGTERM); ts=time.time()
    samples=obs(port,server,live,ctx["replay"])
    rec={"tag":"W1","what":"current lane worktree: SIGTERM the replay while the server is held",
         "ready":ready,"replay_pid":ctx["replay"],"live_pid":live,"server_pid":server,"port":port,
         "signal":{"target":"replay","pid":ctx["replay"],"sig":"SIGTERM"},
         "gone_after_s":{"server":next((s["t"] for s in samples if not s["server"]),None),
                          "port_closed":next((s["t"] for s in samples if not s["listening"]),None),
                          "live":next((s["t"] for s in samples if not s["live"]),None)},
         "hypothesis_held":(not alive(server)) and (not listening(port)),
         "samples_n":len(samples)}
    try: rec["rerun_receipt_witness"]=json.load(open(os.path.join(ctx["work"],"rerun-receipt.json"))).get("witness")
    except (OSError,ValueError) as exc: rec["rerun_receipt_witness"]=f"error:{exc}"
    finish(ctx,ready,live,server,port,rec)
def w2():
    ctx=launch("W2",True)
    ready=json.load(open(os.path.join(ctx["wd"],"ready.json")))
    server,port=ready["pid"],ready["port"]; live=next((c for c in children(ctx["replay"])),None)
    os.kill(ctx["counter"],signal.SIGTERM); ts=time.time()
    samples=obs(port,server,live,ctx["replay"],counter=ctx["counter"])
    rec={"tag":"W2","what":"current lane worktree: SIGTERM a counter-shape parent of the replay (round49 counter :297-298)",
         "ready":ready,"counter_pid":ctx["counter"],"replay_pid":ctx["replay"],"live_pid":live,
         "server_pid":server,"port":port,"signal":{"target":"counter-shape parent","pid":ctx["counter"],"sig":"SIGTERM"},
         "cleanup_steps":[],"samples_n":len(samples)}
    rec["after_15s_observed"]={k:samples[-1][k] for k in samples[-1] if k!="t"}
    rec["after_15s_observed"]["ss"]=subprocess.run(["ss","-ltnp",f"sport = :{port}"],capture_output=True,text=True).stdout
    rec["after_15s_observed"]["server_proc"]={k:(open(f"/proc/{server}/{k}","rb").read().decode("utf-8","replace")[:200] if k=="cmdline" else os.readlink(f"/proc/{server}/{k}")) for k in ("exe","cmdline") if alive(server)}
    for pid,nm in ((ctx["replay"],"replay"),(live,"live")):
        if alive(pid):
            os.kill(pid,signal.SIGTERM); time.sleep(1.0)
            rec["cleanup_steps"].append({"sigterm":nm,"pid":pid,"alive_after_1s":alive(pid)})
    rec["hypothesis_held"]=(not alive(server)) and (not listening(port))
    finish(ctx,ready,live,server,port,rec)
W=os.environ.get("W","w1,w2").split(",")
if "w1" in W: w1()
if "w2" in W: w2()
