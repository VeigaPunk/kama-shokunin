#!/usr/bin/env python3
import hashlib, json, os, shutil, signal, socket, struct, subprocess, sys, time
import http.client as _httpclient
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r93/EX02LiveRouterRepeat").resolve()
WORK = SCRATCH / "run"
SERVER = Path.home() / ".local/opt/llama-b12177/llama-server"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
BASE = "5af794958b0fc08f574aa2e67650282269549b02"
M1 = "fe5f031cb1b9d33e1160360d892149b8ac3c7771"
TENSORS = 150000

CHILDREN = []
def kill_children():
    for p in CHILDREN:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass
    CHILDREN.clear()

def gguf(n_tensors, elems, with_data):
    out = [b"GGUF", struct.pack("<I",3), struct.pack("<QQ",n_tensors,0)]
    off=0
    for i in range(n_tensors):
        name=b"t%07d"%i
        out.append(struct.pack("<Q",len(name))+name+struct.pack("<IQIQ",1,elems,0,off))
        off+=(elems*4+31)//32*32
    head=b"".join(out)
    pad=(len(head)+31)//32*32-len(head)
    return head+b"\0"*pad+(b"\0"*off if with_data else b"\0"*16)

def free_port():
    s=socket.socket(); s.bind(("127.0.0.1",0)); p=s.getsockname()[1]; s.close(); return p

def http(method, port, path, body=None, timeout=60):
    data=json.dumps(body).encode() if body is not None else None
    headers={"Content-Type":"application/json"} if data else {}
    conn=_httpclient.HTTPConnection("127.0.0.1",port,timeout=timeout)
    conn.request(method,path,body=data,headers=headers)
    r=conn.getresponse()
    txt=r.read().decode("utf-8","replace")
    conn.close()
    return r.status, txt

def entries(port):
    code, txt = http("GET", port, "/v1/models", timeout=5)
    if code!=200: raise RuntimeError(f"models {code} {txt[:200]}")
    return txt

def probe_bytes(rev):
    return subprocess.run(["git","-C",str(LANE),"show",f"{rev}:tools/kama-probe.sh"],capture_output=True,check=True).stdout

def run_one(rev, port, expect, label):
    probe = WORK/f"probe-{label}.sh"
    probe.write_bytes(probe_bytes(rev))
    pcwd = WORK/f"pcwd-{label}"; pcwd.mkdir(exist_ok=True)
    env=dict(os.environ,TMPDIR=str(pcwd))
    t0=time.time()
    p=subprocess.run(["bash",str(probe),"check","--port",str(port),"--expect",expect,"--json","--timeout","5","--connect-timeout","2"],capture_output=True,text=True,timeout=120,env=env,cwd=pcwd)
    dt=time.time()-t0
    try:
        doc=json.loads(p.stdout)
        row=(doc.get("rows") or doc.get("consumers") or [])[0]
        print(f"{label} rev={rev[:8]} expect={expect!r} rc={p.returncode} verdict={row.get('verdict')} reason={row.get('reason')} dt={dt:.2f}s", flush=True)
    except Exception as e:
        print(f"{label} rev={rev[:8]} expect={expect!r} rc={p.returncode} UNPARSED {e} stdout={p.stdout[:300]!r} stderr={p.stderr[:300]!r} dt={dt:.2f}s", flush=True)
    return dt

def main():
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    files=WORK/"files"; files.mkdir()
    empty=WORK/"empty-models"; empty.mkdir()
    slow=files/"slow.gguf"
    print("building slow.gguf...",flush=True)
    slow.write_bytes(gguf(TENSORS,1,False))
    print(f"slow size={slow.stat().st_size} sha256={hashlib.sha256(slow.read_bytes()).hexdigest()}",flush=True)
    m1=files/"m1.gguf"; shutil.copyfile(MODEL,m1)
    print(f"m1 size={m1.stat().st_size}",flush=True)
    # preset: 12 bad entries all naming slow, 1 valid
    ini=WORK/"presets.ini"
    lines=[]
    for i in range(1,13):
        lines.append(f"[bad{i:02d}]")
        lines.append(f"model = {slow}")
        lines.append("")
    lines.append("[goodone]")
    lines.append(f"model = {m1}")
    lines.append("")
    ini.write_text("\n".join(lines))
    print(ini.read_text(),flush=True)

    port=free_port()
    log=(WORK/"router.log").open("w")
    proc=subprocess.Popen([str(SERVER),"--host","127.0.0.1","--port",str(port),"--models-max","1","--models-dir",str(empty.resolve()),"--models-preset",str(ini.resolve())],stdout=log,stderr=subprocess.STDOUT,cwd=WORK,start_new_session=True,env=dict(os.environ))
    CHILDREN.append(proc)
    print(f"router pid={proc.pid} port={port}",flush=True)
    try:
        # wait
        raw=None
        for _ in range(120):
            if proc.poll() is not None:
                print(f"router exited rc={proc.returncode}"); print(open(WORK/"router.log").read()[-2000:]); return 2
            try:
                raw=entries(port); break
            except Exception as e:
                print(f"wait try {e!r}", flush=True)
                time.sleep(0.25)
        else:
            print("router never answered"); print(open(WORK/"router.log").read()[-2000:]); return 2
        print("=== /v1/models raw ===",flush=True)
        print(raw[:12000],flush=True)
        (WORK/"models-raw.json").write_text(raw)
        doc=json.loads(raw)
        data=doc.get("data",[])
        print(f"entries={len(data)}",flush=True)
        for e in data:
            print(f" id={e.get('id')} status={json.dumps(e.get('status'))[:400]}",flush=True)
        # /props
        code, props = http("GET",port,"/props",timeout=5)
        print(f"/props {code}: {props[:500]}",flush=True)
        # check all unloaded?
        # skip oracle in this fresh run; probing pre-oracle state
        for mid in ():
            t0=time.time()
            try:
                code, txt = http("POST",port,"/v1/chat/completions",{"model":mid,"messages":[{"role":"user","content":"hi"}],"max_tokens":2},timeout=60)
                print(f"ORACLE POST {mid} http={code} dt={time.time()-t0:.2f}s body={txt[:400]!r}",flush=True)
            except Exception as e:
                print(f"ORACLE POST {mid} EXC {e!r}",flush=True)
            # re-list after oracle attempt (may have triggered load fail -> status?)
            try:
                raw2=entries(port)
                d2=json.loads(raw2).get("data",[])
                for e in d2:
                    if e.get("id")==mid:
                        print(f" post-oracle /v1/models {mid} status={json.dumps(e.get('status'))[:600]}",flush=True)
            except Exception as e:
                print(f" re-list exc {e!r}",flush=True)

        print("uptime:", subprocess.run(["uptime"],capture_output=True,text=True).stdout.strip(),flush=True)
        # probes: base vs M1, expect bad01 and *
        for rev,label in [(BASE,"base"),(M1,"M1")]:
            for expect in ("bad01","*"):
                run_one(rev,port,expect,label)
                print("uptime:", subprocess.run(["uptime"],capture_output=True,text=True).stdout.strip(),flush=True)
    finally:
        kill_children()
        try: log.close()
        except: pass
        print("router log tail:",flush=True)
        try: print(open(WORK/"router.log").read()[-3000:],flush=True)
        except Exception as e: print(e)
    return 0

if __name__=="__main__":
    sys.exit(main())
