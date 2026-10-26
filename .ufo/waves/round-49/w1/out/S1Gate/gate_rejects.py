#!/usr/bin/env python3
"""S1Gate round-49: three groundable rejects for the round-49 gate.

Each probe starts a loopback stub on an ephemeral port, measures it exactly the
way the frozen C1 counter (tools/round49-replay-witness-audit.py, observe()
at line 258) measures a witnessed server, and prints one machine-readable line
per proposed witness. The stub is never llama-server.

  A  /health 200 + /props model_path: the stub answers both, naming a real file
     whose sha256 is the frozen MODEL_SHA, while /proc/<pid>/exe is python.
  B  /proc/<pid>/cmdline alone: a plain python process whose argv carries
     `-m <frozen model>` (hash matches), no socket at all.
  C  a `piece` comparison that is only self-consistent between /tokenize and
     /detokenize: an invented 3-char vocabulary round-trips the nonce with
     pieces that do not equal the model's own vocabulary.

Also runs the frozen counter's own observe() against A (gguf-vocabulary stub) so
the discriminator is visible, and against C (invented vocabulary).

Nothing is written outside the paths named on argv; the stubs are torn down and
the port is checked to refuse before exit.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

LANE = os.environ["LANE"]
MODEL = os.environ["MODEL"]
OUT = os.environ["OUT"]
COUNTER = os.path.join(LANE, "tools/round49-replay-witness-audit.py")

spec = importlib.util.spec_from_file_location("c49", COUNTER)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

CHILD = r'''#!/usr/bin/env python3
import http.server, importlib.util, json, socketserver, sys
cpath, mode, portf = sys.argv[1:4]
model = sys.argv[sys.argv.index("-m") + 1]
spec = importlib.util.spec_from_file_location("c", cpath)
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
if mode == "gguf":
    V = c.gguf_tokens(model)
    inv = sorted(((v.replace("\u2581", " "), i) for i, v in enumerate(V) if v and not v.startswith("<")),
                 key=lambda x: -len(x[0]))
    def tok(s):
        s = " " + s; out = []
        while s:
            for p, i in inv:
                if s.startswith(p):
                    out.append({"id": i, "piece": p}); s = s[len(p):]; break
            else:
                s = s[1:]
        return out
    def detok(ids):
        return "".join(V[i].replace("\u2581", " ") for i in ids)
else:
    INV = []
    def tok(s):
        INV.clear()
        out = []
        for i, o in enumerate(range(0, len(s), 3)):
            INV.append(s[o:o + 3]); out.append({"id": i, "piece": s[o:o + 3]})
        return out
    def detok(ids):
        return "".join(INV[i] for i in ids)
class H(http.server.BaseHTTPRequestHandler):
    def _send(self, obj):
        d = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(d)))
        self.end_headers()
        self.wfile.write(d)
    def do_GET(self):
        if self.path == "/health":
            self._send({"status": "ok"})
        elif self.path == "/props":
            self._send({"model_path": model, "model_alias": "kama-r48-live",
                        "total_slots": 1, "default_generation_settings": {"n_ctx": 256}})
        else:
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers()
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/tokenize":
            self._send({"tokens": tok(b["content"])})
        else:
            self._send({"content": detok(b["tokens"])})
    def log_message(self, *a):
        pass
s = socketserver.TCPServer(("127.0.0.1", 0), H)
open(portf, "w").write(str(s.server_address[1]))
s.serve_forever()
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get(port, path):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with op.open(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
        return r.status, json.loads(r.read())


def cmdline_model(pid):
    with open(f"/proc/{pid}/cmdline", "rb") as fh:
        argv = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0")]
    try:
        mpath = argv[argv.index("-m") + 1]
    except (ValueError, IndexError):
        return argv, None, None
    if not os.path.isabs(mpath):
        mpath = os.path.join(os.readlink(f"/proc/{pid}/cwd"), mpath)
    return argv, mpath, sha(mpath)


def start(mode, tmp):
    portf = os.path.join(tmp, f"port-{mode}")
    stub = os.path.join(tmp, "stub.py")
    if not os.path.exists(stub):
        with open(stub, "w") as fh:
            fh.write(CHILD)
    p = subprocess.Popen([sys.executable, stub, COUNTER, mode, portf, "-m", MODEL])
    for _ in range(200):
        if os.path.exists(portf) and open(portf).read().strip():
            return p, int(open(portf).read())
        time.sleep(0.05)
    p.kill()
    raise SystemExit("stub did not bind")


def facts(tag, pid, port, note=""):
    out = [f"{tag}: pid {pid} port {port}{note}"]
    exe = sha(f"/proc/{pid}/exe")
    out.append(f"{tag}: exe sha256={exe} frozen_server={int(exe == c.SERVER_SHA)} "
               f"frozen={c.SERVER_SHA}")
    li = c.listen_inodes(port)
    owned = bool(li and (li & c.pid_socket_inodes(pid)))
    out.append(f"{tag}: listen inodes={sorted(li)} owned_by_pid={int(owned)}")
    argv, mpath, msha = cmdline_model(pid)
    out.append(f"{tag}: cmdline -m {mpath} sha={msha} frozen_model={int(msha == c.MODEL_SHA)}")
    return out


def run():
    tmp = tempfile.mkdtemp(prefix="gate-rejects-", dir=os.environ.get("SCRATCH", OUT))
    lines, vocab = [], c.gguf_tokens(MODEL)
    lines.append(f"model={MODEL} sha={sha(MODEL)} frozen_model={int(sha(MODEL) == c.MODEL_SHA)} "
                 f"vocab={len(vocab)} tokens")
    procs = []

    # ---- A: /health 200 + /props model_path, gguf-vocabulary tokenizer
    pa, porta = start("gguf", tmp)
    procs.append(pa)
    st, body = get(porta, "/health")
    lines.append(f"A: GET /health status={st} body={json.dumps(body)}")
    st, props = get(porta, "/props")
    mpath = props.get("model_path")
    lines.append(f"A: GET /props status={st} model_path={mpath} "
                 f"sha={sha(mpath) if mpath and os.path.isfile(mpath) else None} "
                 f"frozen_model={int(bool(mpath) and os.path.isfile(mpath) and sha(mpath) == c.MODEL_SHA)}")
    lines += facts("A", pa.pid, porta)
    a_probs = []
    anonce = c.observe(pa.pid, porta, vocab, a_probs)
    lines.append(f"A: counter observe() nonce={anonce!r} problems={json.dumps(a_probs)}")

    # ---- B: argv-only, no socket
    pb = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)", "-m", MODEL])
    procs.append(pb)
    argv, bpath, bsha = cmdline_model(pb.pid)
    lines.append(f"B: pid {pb.pid} argv={json.dumps(argv)}")
    lines.append(f"B: cmdline -m {bpath} sha={bsha} frozen_model={int(bsha == c.MODEL_SHA)} "
                 f"sockets={len(c.pid_socket_inodes(pb.pid))}")
    bexe = sha(f"/proc/{pb.pid}/exe")
    lines.append(f"B: exe sha256={bexe} frozen_server={int(bexe == c.SERVER_SHA)}")

    # ---- C: invented vocabulary, self-consistent tokenize/detokenize
    pc, portc = start("invented", tmp)
    procs.append(pc)
    nonce = f"kama witness {os.urandom(8).hex()}"
    tk = c.post(portc, "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
    ids = [t["id"] for t in tk]
    dt = c.post(portc, "/detokenize", {"tokens": ids})["content"]
    bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                 and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
    lines.append(f"C: nonce={nonce!r} tokenize={json.dumps(tk)}")
    lines.append(f"C: detokenize {dt!r} equals_nonce={int(dt == nonce)} (a detokenize-only check passes)")
    lines.append(f"C: pieces disagreeing with the model vocabulary={len(bad)}/{len(tk)} "
                 f"example={json.dumps(bad[:1])} vocab[0]={vocab[0]!r}")
    c_probs = []
    c.observe(pc.pid, portc, vocab, c_probs)
    lines.append(f"C: counter observe() problems={json.dumps(c_probs)}")
    lines += facts("C", pc.pid, portc)

    for p in procs:
        p.kill()
        p.wait()
    time.sleep(0.3)
    lines.append(f"teardown: A refuses={int(c.port_refuses(porta))} C refuses={int(c.port_refuses(portc))} "
                 f"B alive={int(c.pid_alive(pb.pid))}")
    text = "\n".join(lines)
    print(text)
    with open(os.path.join(OUT, "gate_rejects.out"), "w") as fh:
        fh.write(text + "\n")


run()
