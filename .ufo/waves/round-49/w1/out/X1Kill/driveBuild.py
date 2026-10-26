"""Measurements against the blobs extracted from build commit 74558c71.

Re-extracts the three build blobs (git show, read-only) into ./build-tree if absent and
checks them against the digests recorded in X1Kill.md, then runs B1 (SIGTERM the replay)
and B2 (SIGKILL the live tool child) for 15 s each. Writes only below this directory.
Usage: python3 driveBuild.py
"""
import hashlib, json, os, signal, socket, subprocess, sys, time

S = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(S, "build-tree")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "74558c71c38ceaeace15fd4cf8aa9d84977584b1"
WANT = {"kama-live-replay.py": "636074f9628f8c6106a0b5508dd7a15e8d677ea89cfbe0cd2a665f85ddd1e01a",
        "kama-llamacpp-live.py": "72e76079995c5ba8269bbaa31e30b8c15c5e503de2a58e603b78561424bffd4c"}
if not os.path.isfile(os.path.join(B, "tools", "kama-live-replay.py")):
    os.makedirs(os.path.join(B, "tools"), exist_ok=True)
    for name in ("kama-live-replay.py", "kama-llamacpp-live.py", "kama-probe.sh"):
        blob = subprocess.run(["git", "-C", LANE, "show", f"{TIP}:tools/{name}"],
                              capture_output=True, check=True).stdout
        with open(os.path.join(B, "tools", name), "wb") as fh:
            fh.write(blob)
        os.chmod(os.path.join(B, "tools", name), 0o755)
    if not os.path.lexists(os.path.join(B, "registry")):
        os.symlink(os.path.join(LANE, "registry"), os.path.join(B, "registry"))
for name, want in WANT.items():
    got = hashlib.sha256(open(os.path.join(B, "tools", name), "rb").read()).hexdigest()
    assert got == want, f"{name}: {got} != {want}"
REPLAY = os.path.join(B, "tools", "kama-live-replay.py")
RECEIPT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json"
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
def scenario(tag, what):
    wd=os.path.join(S,f"wd-B{tag}"); work=os.path.join(S,f"w-B{tag}")
    os.makedirs(wd,exist_ok=True); os.makedirs(work,exist_ok=True)
    outj=os.path.join(S,f"j-B{tag}.json")
    argv=[sys.executable,REPLAY,"--receipt",RECEIPT,"--work",work,"--out",outj,"--witness-dir",wd]
    log=open(os.path.join(S,f"replay-B{tag}.log"),"wb")
    p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,cwd=S,start_new_session=True)
    t0=time.time()
    while time.time()-t0<240 and not os.path.exists(os.path.join(wd,"ready.json")) and p.poll() is None:
        time.sleep(0.05)
    ready=json.load(open(os.path.join(wd,"ready.json")))
    live=next((c for c in children(p.pid)),None)
    rec={"tag":"B"+tag,"what":what,"cmd":" ".join(argv),"ready":ready,"replay_pid":p.pid,
         "live_pid":live,"server_pid":ready["pid"],"port":ready["port"],
         "server_exe_sha256":subprocess.run(["sha256sum",f"/proc/{ready['pid']}/exe"],capture_output=True,text=True).stdout.split()[0],
         "before_ss":subprocess.run(["ss","-ltnp",f"sport = :{ready['port']}"],capture_output=True,text=True).stdout,
         "before_live_parent":int(open(f"/proc/{live}/stat").read().rsplit(")",1)[1].split()[1])}
    target, signum, nm = ((p.pid,signal.SIGTERM,"replay"),(live,signal.SIGKILL,"live"))[0 if tag=="1" else 1]
    rec["signal"]={"target":nm,"pid":target,"sig":signal.Signals(signum).name}
    os.kill(target, signum)
    ts=time.time(); samples=[]
    while time.time()-ts<15:
        el=round(time.time()-ts,2)
        s={"t":el,"replay":alive(p.pid),"live":alive(live),"server":alive(ready["pid"]),"listening":listening(ready["port"])}
        samples.append(s); time.sleep(0.25)
    rec["samples_n"]=len(samples)
    rec["gone_after_s"]={"server":next((s["t"] for s in samples if not s["server"]),None),
                         "port_closed":next((s["t"] for s in samples if not s["listening"]),None),
                         "live":next((s["t"] for s in samples if not s["live"]),None),
                         "replay":next((s["t"] for s in samples if not s["replay"]),None)}
    rec["at_15s"]={"server":alive(ready["pid"]),"listening":listening(ready["port"]),
                   "live":alive(live),"replay":alive(p.pid),
                   "live_ppid":int(open(f"/proc/{live}/stat").read().rsplit(")",1)[1].split()[1]) if alive(live) else None,
                   "ss":subprocess.run(["ss","-ltnp",f"sport = :{ready['port']}"],capture_output=True,text=True).stdout,
                   "replay_exit":p.poll()}
    rec["hypothesis_held"]=(not alive(ready["pid"])) and (not listening(ready["port"]))
    # cleanup
    open(os.path.join(wd,"release"),"w").write("x1kill\n"); time.sleep(2)
    rec["after_release"]={"server":alive(ready["pid"]),"live":alive(live),"listening":listening(ready["port"])}
    for pid in (live,ready["pid"]):
        if alive(pid):
            try: os.kill(pid,signal.SIGTERM)
            except OSError: pass
    time.sleep(2)
    for pid in (live,ready["pid"]):
        if alive(pid):
            try: os.kill(pid,signal.SIGKILL)
            except OSError: pass
    try: os.killpg(p.pid,signal.SIGKILL)
    except OSError: pass
    log.close()
    rec["after_cleanup"]={"server":alive(ready["pid"]),"live":alive(live),"listening":listening(ready["port"])}
    json.dump(rec,open(os.path.join(S,f"result-B{tag}.json"),"w"),indent=1)
    print("B"+tag,rec["signal"],"gone",rec["gone_after_s"],"at_15s server",rec["at_15s"]["server"],"listen",rec["at_15s"]["listening"],"held",rec["hypothesis_held"],flush=True)
scenario("1","SIGTERM the replay built at 74558c71")
scenario("2","SIGKILL the live tool child built at 74558c71")
