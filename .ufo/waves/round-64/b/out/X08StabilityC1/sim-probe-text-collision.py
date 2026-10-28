import importlib.util, os, random, subprocess, sys, time, hashlib, signal, collections
spec = importlib.util.spec_from_file_location('c1', sys.argv[1]+'/tools/round64-c1-counter.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
server = c.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
port = c.free_port()
log = open(sys.argv[2]+'/sim-server.log','wb')
p = subprocess.Popen([server,'--model',model,'--alias',c.ALIAS,'--port',str(port),'--host','127.0.0.1','-c','512','-t','1'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
try:
    for _ in range(300):
        st,_,b,_ = c.http(port,'/health',timeout=2.0)
        if st==200: break
        time.sleep(0.2)
    N=int(sys.argv[3]); eq_text=eq_usage=both=swapfail_text=0; ex=[]
    for i in range(N):
        rng = random.Random(int.from_bytes(os.urandom(8),'big'))
        nonce='r64p'+hashlib.sha256(os.urandom(8)).hexdigest()[:8]
        reqs=c.draw_probes(rng,nonce)
        r=[c.probe(port,q) for q in reqs]
        t=r[0]['text']==r[1]['text']
        u=(r[0]['usage_prompt_tokens'],r[0]['usage_completion_tokens'])==(r[1]['usage_prompt_tokens'],r[1]['usage_completion_tokens'])
        eq_text+=t; eq_usage+=u; both+=(t and u)
        if t and len(ex)<5: ex.append((reqs[0]['n_predict'],reqs[1]['n_predict'],r[0]['text'],r[1]['text']))
    print('trials',N,'texts_equal',eq_text,'usage_equal',eq_usage,'both',both)
    for e in ex: print(e)
finally:
    p.send_signal(signal.SIGTERM); p.wait(timeout=15)
