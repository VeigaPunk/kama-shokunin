import json, os, shutil, socket, subprocess, sys, threading, time
R="/fast/scratch/hyaku/kama-r89/SN01ProbeSafety"
D=R+"/tmp/race3"; shutil.rmtree(D,ignore_errors=True); os.makedirs(D)
GOOD=D+"/good.gguf"; FIFO=D+"/fifo"; LINK=D+"/m.gguf"
shutil.copy(R+"/fx/good.gguf",GOOD); os.mkfifo(FIFO)
body={"object":"list","data":[{"id":"m","status":{"value":"unloaded","args":[R+"/fx/llama-server","--model",LINK]}}]}
BODY=D+"/body.json"; open(BODY,"w").write(json.dumps(body))
def swap(t):
    if os.path.lexists(D+"/.t"): os.remove(D+"/.t")
    os.symlink(t,D+"/.t"); os.replace(D+"/.t",LINK)
stop=False
def flip():
    while not stop: swap(FIFO); swap(GOOD)
threading.Thread(target=flip,daemon=True).start(); time.sleep(0.05)
s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close()
srv=subprocess.Popen([sys.executable,R+"/srv.py",str(port),BODY,"",""],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
time.sleep(0.4)
env=dict(os.environ,TMPDIR=R+"/tmp",KAMA_PROBE_TMPDIR=R+"/tmp")
N=120; blocked=0; worst=0.0; t_end=time.time()+150; done=0; evidence=[]
for i in range(N):
    if time.time()>t_end: break
    t=time.time()
    p=subprocess.Popen(["bash",R+"/probe-M.sh","listeners","--port",str(port),"--expect","*","--timeout","2"],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)
    try:
        p.wait(timeout=3); done+=1; worst=max(worst,time.time()-t)
    except subprocess.TimeoutExpired:
        blocked+=1
        kids=subprocess.run(["pgrep","-P",str(p.pid)],capture_output=True,text=True).stdout.split()
        for k in kids:
            try: evidence.append(open(f"/proc/{k}/syscall").read().strip()[:90])
            except OSError: pass
        try: os.killpg(p.pid,9)
        except ProcessLookupError: pass
        try: p.wait(timeout=5)
        except subprocess.TimeoutExpired: pass
        subprocess.run(["pkill","-9","-f",f"SN01ProbeSafety/probe-M.sh listeners --port {port}"])
stop=True; os.killpg(srv.pid,9)
print(f"runs={done+blocked} completed={done} blocked_over_3s={blocked} worst_completed={worst:.2f}s")
print("blocked-child syscall samples:", evidence[:3])
shutil.rmtree(D,ignore_errors=True)
