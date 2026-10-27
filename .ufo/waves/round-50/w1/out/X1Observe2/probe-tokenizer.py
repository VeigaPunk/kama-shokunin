import json, struct, subprocess, sys, time, urllib.request

def gguf_tokens(path, key="tokenizer.ggml.tokens"):
    with open(path,'rb') as f:
        assert f.read(4)==b'GGUF'
        ver=struct.unpack('<I',f.read(4))[0]
        nt=struct.unpack('<Q',f.read(8))[0]; nkv=struct.unpack('<Q',f.read(8))[0]
        sizes={0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:4,11:8,12:8}
        def rstr():
            n=struct.unpack('<Q',f.read(8))[0]; return f.read(n)
        def skip(t):
            if t==8: return rstr()
            if t==9:
                et=struct.unpack('<I',f.read(4))[0]; cnt=struct.unpack('<Q',f.read(8))[0]
                for _ in range(cnt): skip(et)
                return None
            return f.read(sizes[t])
        for _ in range(nkv):
            k=rstr().decode()
            vt=struct.unpack('<I',f.read(4))[0]
            if vt==9:
                et=struct.unpack('<I',f.read(4))[0]; cnt=struct.unpack('<Q',f.read(8))[0]
                if k==key:
                    out=[]
                    for _ in range(cnt):
                        if et==8: out.append(rstr())
                        else: skip(et)
                    return out
                for _ in range(cnt): skip(et)
            else:
                skip(vt)
    return None

M='obs/work-1/download/stories260K.gguf'
toks=gguf_tokens(M)
print('vocab size', len(toks))
print('first 20', toks[:20])
PORT=38427
p=subprocess.Popen(['/home/vgpnk/.local/opt/llama-b11909/llama-server','--host','127.0.0.1','--port',str(PORT),'-m',M,'--alias','probe','--ctx-size','256','--threads','1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(200):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{PORT}/health',timeout=1).read(); break
        except Exception: time.sleep(0.1)
    def post(path, body):
        req=urllib.request.Request(f'http://127.0.0.1:{PORT}{path}',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
        return json.loads(urllib.request.urlopen(req,timeout=20).read())
    nonce='observer nonce 0123456789abcdef'
    ids=post('/tokenize',{'content':nonce})['tokens']
    print('ids',ids)
    det=post('/detokenize',{'tokens':ids})
    print('server detok',repr(det))
    pieces=[toks[i] for i in ids]
    print('pieces',pieces)
    raw=b''.join(pieces)
    print('raw',repr(raw))
    sp=raw.replace('▁'.encode(),b' ')
    print('sp',repr(sp))
    print('strip',repr(sp.lstrip(b' ')))
    ids2=post('/tokenize',{'content':' '+nonce})['tokens']
    print('ids with leading space',ids2, 'pieces', [toks[i] for i in ids2])
    comp=post('/completion',{'prompt':nonce,'n_predict':16,'temperature':0,'top_k':1,'seed':424242,'stream':False})
    print('comp keys',sorted(comp.keys()))
    print('comp content',repr(comp.get('content')),'tokens',comp.get('tokens'),'pred',comp.get('tokens_predicted'))
    ccontent=comp.get('content')
    cids=post('/tokenize',{'content':ccontent})['tokens']
    print('content ids',cids,'pieces',[toks[i] for i in cids])
    print('content detok server',repr(post('/detokenize',{'tokens':cids}).get('content')))
finally:
    p.kill(); p.wait()
