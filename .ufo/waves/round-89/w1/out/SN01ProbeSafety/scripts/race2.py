import json, os, shutil, socket, stat, subprocess, sys, threading, time
R="/fast/scratch/hyaku/kama-r89/SN01ProbeSafety"
D=R+"/tmp/race"; shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
GOOD=D+"/good.gguf"; FIFO=D+"/fifo"; LINK=D+"/m.gguf"
shutil.copy(R+"/fx/good.gguf",GOOD); os.mkfifo(FIFO)
body={"object":"list","data":[{"id":"m","status":{"value":"unloaded",
      "args":[R+"/fx/llama-server","--model",LINK]}}]}
BODY=D+"/body.json"; open(BODY,"w").write(json.dumps(body))
swap=lambda t: (os.path.lexists(D+"/.t") and os.remove(D+"/.t"), os.symlink(t,D+"/.t"), os.replace(D+"/.t",LINK))
stop=False
def flip():
    while not stop: swap(FIFO); swap(GOOD)
threading.Thread(target=flip,daemon=True).start(); time.sleep(0.05)
s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close()
srv=subprocess.Popen([sys.executable,R+"/srv.py",str(port),BODY,"",""],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
time.sleep(0.4)
env=dict(os.environ,TMPDIR=R+"/tmp",KAMA_PROBE_TMPDIR=R+"/tmp")
N=200; hang=0; worst=0.0; verdicts={}
for i in range(N):
    t=time.time()
    p=subprocess.Popen(["bash",R+"/probe-M.sh","listeners","--port",str(port),"--expect","*","--timeout","2"],
                       stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True,env=env,text=True)
    try:
        out,_=p.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        hang+=1; os.killpg(p.pid,9); p.communicate()
        continue
    dt=time.time()-t; worst=max(worst,dt)
    for line in out.splitlines():
        if "| override |" in line:
            key="MODEL_UNLOADED" if "MODEL_UNLOADED" in line else ("MODEL_OK" if "MODEL_OK" in line else "other")
            verdicts[key]=verdicts.get(key,0)+1
stop=True; os.killpg(srv.pid,9); shutil.rmtree(D,ignore_errors=True)
print(f"runs={N} blocked_over_3s={hang} worst_wall={worst:.2f}s verdicts={verdicts}")
