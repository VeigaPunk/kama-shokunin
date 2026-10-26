#!/usr/bin/env python3
"""Round-49 controls: score the frozen counters on states that skip the claimed work.

usage: build_controls.py <lane> <scratch>   (receipts land beside this file)
  base.c1.out / base.c2.out          both counters at the round-49 base (the round-48 closure)
  junk-c1-fake-witness.c1.out        base + a replay that accepts --witness-dir and never runs
                                     llama-server: it serves /tokenize and /detokenize itself from
                                     the model's own vocabulary (a python process named `-m <model>`),
                                     writes ready.json, copies the original receipt as the rerun with
                                     witness.released true, and reports match true (K2Cheat shape)
  junk-c2-no-exempt.c2.out           base + an audit that grades every exempt line (drops the
                                     carve-out: the cheapest way to make laundering impossible)
  junk-c2-word-token.c2.out          base + an audit with the word-bounded token and negation window
                                     but no origin rule
Fixture commits are made in `git clone --shared` copies under <scratch> with a fixture identity;
each clone's toplevel is checked before its first commit.
"""
import os
import subprocess
import sys

LANE, SCR = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "438127bc01ff3b99f98468549d58046f932490ef"
C1 = os.path.join(LANE, "tools/round49-replay-witness-audit.py")
C2 = os.path.join(LANE, "tools/round49-append-audit-v4-check.py")
IDENT = ["-c", "user.name=r49-control", "-c", "user.email=r49-control@invalid", "-c", "commit.gpgsign=false"]

FAKE_REPLAY = r'''#!/usr/bin/env python3
"""junk control: a replay that never runs llama-server (round-49 control, not a lane tool)."""
import argparse, importlib.util, json, os, subprocess, sys, time, urllib.request
ap = argparse.ArgumentParser()
for f in ("--receipt", "--work", "--out", "--witness-dir", "--live", "--timeout"):
    ap.add_argument(f)
a = ap.parse_args()
rec = json.load(open(a.receipt))
os.makedirs(a.work, exist_ok=True)
model = os.path.join(a.work, "m.gguf")
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with op.open(rec["provenance"]["model"]["url"], timeout=120) as r, open(model, "wb") as fh:
    fh.write(r.read())
stub = os.path.join(a.work, "stub.py")
here = os.path.dirname(os.path.abspath(__file__))
open(stub, "w").write("""
import json, sys, importlib.util, http.server, socketserver
spec = importlib.util.spec_from_file_location('c', sys.argv[3]); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
V = c.gguf_tokens(sys.argv[2])
inv = sorted(((v.replace(chr(0x2581), ' '), i) for i, v in enumerate(V) if v and not v.startswith('<')), key=lambda x: -len(x[0]))
def tok(s):
    s = ' ' + s; out = []
    while s:
        for p, i in inv:
            if s.startswith(p):
                out.append({'id': i, 'piece': p}); s = s[len(p):]; break
        else:
            s = s[1:]
    return out
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if self.path == '/tokenize':
            r = {'tokens': tok(b['content'])}
        else:
            r = {'content': ''.join(V[i].replace(chr(0x2581), ' ') for i in b['tokens'])}
        d = json.dumps(r).encode(); self.send_response(200); self.send_header('Content-Length', str(len(d))); self.end_headers(); self.wfile.write(d)
    def log_message(self, *a): pass
s = socketserver.TCPServer(('127.0.0.1', 0), H)
open(sys.argv[4], 'w').write(str(s.server_address[1]))
s.serve_forever()
""")
portf = os.path.join(a.work, "port")
p = subprocess.Popen([sys.executable, stub, "-m", model, os.path.join(here, "round49-replay-witness-audit.py"), portf])
while not os.path.exists(portf) or not open(portf).read():
    time.sleep(0.1)
port = int(open(portf).read())
tmp = os.path.join(a.witness_dir, "ready.tmp")
json.dump({"port": port, "pid": p.pid}, open(tmp, "w")); os.replace(tmp, os.path.join(a.witness_dir, "ready.json"))
while not os.path.exists(os.path.join(a.witness_dir, "release")):
    time.sleep(0.1)
p.kill(); p.wait()
rerun = dict(rec, witness={"released": True}, started_utc=time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()))
rp = os.path.join(a.work, "rerun-receipt.json")
json.dump(rerun, open(rp, "w"))
json.dump({"match": True, "refused": None, "mismatches": [], "rerun_receipt": rp}, open(a.out, "w"))
'''


def sh(*argv, cwd=None):
    p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    if p.returncode != 0:
        raise SystemExit(f"{argv[:4]}: {p.stderr[-300:]}")
    return p.stdout


def clone(name):
    d = os.path.join(SCR, name)
    sh("git", "clone", "-q", "--shared", "--no-checkout", LANE, d)
    sh("git", "-C", d, "checkout", "-q", "--detach", BASE)
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise SystemExit(f"toplevel {top} != {d}")
    # the counters are frozen in the lane; copy them into the control so they are present at its tip
    for c in (C1, C2):
        sh("cp", c, os.path.join(d, "tools", os.path.basename(c)))
    return d


def commit(d, msg):
    sh("git", "-C", d, "add", "-A")
    sh("git", "-C", d, *IDENT, "commit", "-q", "-m", msg)
    return sh("git", "-C", d, "rev-parse", "HEAD").strip()


def score(counter, repo, tip, name):
    out = os.path.join(HERE, name)
    p = subprocess.run([sys.executable, counter, "--repo", repo, "--tip", tip, "--scratch", SCR, "--out", out],
                       capture_output=True, text=True)
    with open(out, "a") as fh:
        fh.write(f"exit={p.returncode}\n")
    print(name, p.stdout.split("\n")[1] if "\n" in p.stdout else p.stdout, f"exit={p.returncode}")


os.makedirs(SCR, exist_ok=True)
score(C1, LANE, BASE, "base.c1.out")
score(C2, LANE, BASE, "base.c2.out")

d = clone("junk-c1")
with open(os.path.join(d, "tools/kama-live-replay.py"), "w") as fh:
    fh.write(FAKE_REPLAY)
score(C1, d, commit(d, "control: fake witness replay"), "junk-c1-fake-witness.c1.out")

AOA = "tools/append-only-audit.py"
d = clone("junk-c2a")
src = open(os.path.join(d, AOA)).read()
old = "                if s in eligible:\n                    continue\n"
assert old in src
open(os.path.join(d, AOA), "w").write(src.replace(old, ""))
score(C2, d, commit(d, "control: no exemption"), "junk-c2-no-exempt.c2.out")

d = clone("junk-c2b")
src = open(os.path.join(d, AOA)).read()
old = "    return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)\n"
new = ("    neg = re.search(r\"(?:\\b(?:not|never|no|nor|neither|non|isn't|aren't)\\b|\\bno longer\\b)\"\n"
       "                    r\"(?:[\\s\\-]+[\\w'’]+){0,3}?[\\s\\-]+append[- ]only\", low)\n"
       "    wild = any(ch in pattern for ch in \"*?[\")\n"
       "    word = bool(tok) and re.search(r\"(?<![a-z0-9_])\" + re.escape(tok) + r\"(?![a-z0-9_])\", low)\n"
       "    return not neg and ((not wild and fnmatch.fnmatchcase(decl_path, pattern)) or bool(word))\n")
assert old in src
open(os.path.join(d, AOA), "w").write(src.replace(old, new))
score(C2, d, commit(d, "control: word token, no origin rule"), "junk-c2-word-token.c2.out")
