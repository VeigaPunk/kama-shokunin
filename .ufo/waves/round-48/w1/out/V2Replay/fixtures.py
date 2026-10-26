#!/usr/bin/env python3
"""V2Replay fixtures: exercise each reviewed behavior of kama-live-replay.py at 380bcdf."""
import json, os, subprocess, sys, tempfile, hashlib, shutil

REPLAY = "/fast/scratch/hyaku/kama-r48/V2Replay/lane/tools/kama-live-replay.py"
S = "/fast/scratch/hyaku/kama-r48/V2Replay/fix"
shutil.rmtree(S, ignore_errors=True)
os.makedirs(S)
D = os.path.join(S, "d")
os.makedirs(D)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# --- build a fake archive + model, like the selftest ---
import tarfile
srcdir = os.path.join(D, "src", "build", "bin")
os.makedirs(srcdir)
with open(os.path.join(srcdir, "llama-server"), "w") as fh:
    fh.write("#!/bin/sh\nexit 0\n")
arc = os.path.join(D, "srv.tar.gz")
with tarfile.open(arc, "w:gz") as tf:
    tf.add(os.path.join(D, "src", "build"), arcname="build")
mdl = os.path.join(D, "m.gguf")
with open(mdl, "wb") as fh:
    fh.write(os.urandom(64))
asha, msha = sha256_file(arc), sha256_file(mdl)
ssha = sha256_file(os.path.join(srcdir, "llama-server"))
commit = "c" * 40

FAKE_LIVE = (
    "import json,sys,hashlib\n"
    "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
    "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
    "open(os.environ.get('ARGV_DUMP','/dev/null'),'w').write(repr(a))\n"
    "import os\n"
    "r={'schema':'kama-llamacpp-live/v4','outcome':'pass','server':{'sha256':h(s)},"
    "'model':{'sha256':h(m)},'checks':[{'id':'health_ready','passed':True,'evaluated':True}]}\n"
    "if '--server-archive' in a:\n"
    "    r['schema']='kama-llamacpp-live/v5'\n"
    "json.dump(r,open(o,'w'))\n")
fake_live = os.path.join(D, "fake-live.py")
with open(fake_live, "w") as fh:
    fh.write(FAKE_LIVE)

def base(schema="kama-llamacpp-live/v4", url=None, commit_=None, verified=None, **over):
    r = {"schema": schema, "outcome": "pass", "alias": "a", "ctx": 256, "threads": 1,
         "server": {"sha256": ssha}, "model": {"sha256": msha},
         "checks": [{"id": "health_ready", "passed": True, "evaluated": True}],
         "provenance": {"server": {"asset_url": "file://" + arc, "asset_sha256": asha,
                                   "member": "build/bin/llama-server"},
                        "model": {"url": url or ("file://" + mdl), "sha256": msha}}}
    if commit_ is not None:
        r["provenance"]["model"]["commit"] = commit_
    if verified is not None:
        r["provenance"]["verified"] = verified
    r.update(over)
    return r

def wjson(name, obj):
    p = os.path.join(D, name)
    with open(p, "w") as fh:
        json.dump(obj, fh)
    return p

def run_cli(args):
    p = subprocess.run([sys.executable, REPLAY] + args, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

print("== F1: malformed rerun fields crash compare (uncaught TypeError/AttributeError) ==")
# (a) models body is a JSON object value (not a string)
a = base(captures={"models": {"body": {"data": []}}})
b = base(captures={"models": {"body": {"data": []}}})
pa, pb = wjson("f1a.json", a), wjson("f1b.json", b)
rc, out, err = run_cli(["--compare", pa, pb])
print(f"(a) body-as-object: exit={rc} stdout={out!r} stderr_tail={err.strip().splitlines()[-1] if err.strip() else ''!r}")
# (b) models body parses but data is not iterable
a = base(captures={"models": {"body": json.dumps({"data": 5})}})
pa = wjson("f1c.json", a)
rc, out, err = run_cli(["--compare", pa, pa])
print(f"(b) data=5: exit={rc} stdout={out!r} stderr_tail={err.strip().splitlines()[-1] if err.strip() else ''!r}")
# (c) server field is a string
a = base(server="notadict")
pa = wjson("f1e.json", a)
rc, out, err = run_cli(["--compare", pa, pa])
print(f"(c) server-as-string: exit={rc} stdout={out!r} stderr_tail={err.strip().splitlines()[-1] if err.strip() else ''!r}")

print("== F2: replay() crash path writes no J (docstring says Writes J) ==")
orig = base(captures={"models": {"body": json.dumps({"data": 5})}})
po = wjson("f2-orig.json", orig)
res_path = os.path.join(D, "f2-J.json")
rc, out, err = run_cli(["--receipt", po, "--work", os.path.join(D, "w2"), "--out", res_path])
print(f"replay exit={rc} J_exists={os.path.exists(res_path)} stderr_tail={err.strip().splitlines()[-1] if err.strip() else ''!r}")

print("== F3: file:// URLs accepted by replay (https-only not enforced) ==")
rc, out, err = run_cli(["--receipt", wjson("f3.json", base(schema="kama-llamacpp-live/v5",
                    url="file://" + mdl, commit_=commit, verified={"at": "record"})),
                    "--work", os.path.join(D, "w3"), "--out", os.path.join(D, "f3-J.json")])
print(f"replay exit={rc} stdout={out.strip()!r}")

print("== F4: None vs absent conflation in projection ==")
a = base(captures={"slots": {"element_count": None, "body_sha256": None}})
b = base()  # no captures at all
pa, pb = wjson("f4a.json", a), wjson("f4b.json", b)
rc, out, err = run_cli(["--compare", pa, pb])
print(f"null-captures vs no-captures: exit={rc} stdout={out.strip()!r}")
# models body "null" vs absent
a = base(captures={"models": {"body": "null"}})
b = base()
pa, pb = wjson("f4c.json", a), wjson("f4d.json", b)
rc, out, err = run_cli(["--compare", pa, pb])
print(f"models-body-null vs absent: exit={rc} stdout={out.strip()!r}")
# and the good direction: real value vs absent must differ
a = base(captures={"slots": {"element_count": 4, "body_sha256": "s"}})
rc, out, err = run_cli(["--compare", wjson("f4e.json", a), pb])
print(f"real-slots vs absent: exit={rc} stdout={out.strip()!r}")

print("== F5: argv insertion position for v5 ==")
env = dict(os.environ, ARGV_DUMP=os.path.join(D, "argv.txt"))
p = subprocess.run([sys.executable, REPLAY, "--receipt",
                    wjson("f5.json", base(schema="kama-llamacpp-live/v5", url="file://" + mdl,
                                          commit_=commit, verified={"at": "record"})),
                    "--work", os.path.join(D, "w5"), "--out", os.path.join(D, "f5-J.json"),
                    "--live", fake_live], capture_output=True, text=True, env=env)
argv = eval(open(os.path.join(D, "argv.txt")).read())
i = argv.index("--server-archive")
print(f"replay exit={p.returncode}; argv tail={argv[-6:]}")
print(f"--server-archive at index {i}; between --model-url(value at {argv.index('--model-url')+1}) and --out(at {argv.index('--out')}): "
      f"{argv[i-1] == '--model-url' or argv[i-2] == '--model-url'} and {argv[i+2] == '--out'}")

print("== F6: --compare exit codes 0/1/2 ==")
good = wjson("f6a.json", base())
other = wjson("f6b.json", base(alias="b"))
diff = wjson("f6c.json", base(captures={"slots": {"element_count": 7}}))
rc, out, _ = run_cli(["--compare", good, other]); print(f"equal: exit={rc} out={out.strip()!r}")
rc, out, _ = run_cli(["--compare", good, diff]); print(f"differ: exit={rc} out={out.strip()!r}")
rc, out, _ = run_cli(["--compare", good, os.path.join(D, "nope.json")]); print(f"missing: exit={rc} out={out.strip()!r}")
bad = os.path.join(D, "f6d.json")
open(bad, "w").write("[1,2]")
rc, out, _ = run_cli(["--compare", good, bad]); print(f"json-list: exit={rc} out={out.strip()!r}")

print("== F7: v4 original + v5-emitting live -> schema flip caught ==")
v5live = os.path.join(D, "v5-live.py")
with open(v5live, "w") as fh:
    fh.write(FAKE_LIVE.replace("if '--server-archive' in a:", "if True:"))
p = subprocess.run([sys.executable, REPLAY, "--receipt", wjson("f7.json", base()),
                    "--work", os.path.join(D, "w7"), "--out", os.path.join(D, "f7-J.json"),
                    "--live", v5live], capture_output=True, text=True)
j = json.load(open(os.path.join(D, "f7-J.json")))
print(f"exit={p.returncode} match={j['match']} mismatches={j['mismatches']}")

print("== F8: --compare skips provenance validation (replay would refuse) ==")
# v5 receipt with NO commit and NO verified block: replay refuses (exit 2), --compare exits 0
nov = base(schema="kama-llamacpp-live/v5")  # no commit_, no verified
pn = wjson("f8.json", nov)
rc, out, err = run_cli(["--compare", pn, pn])
print(f"--compare self: exit={rc} out={out.strip()!r}")
rc, out, err = run_cli(["--receipt", pn, "--work", os.path.join(D, "w8"), "--out", os.path.join(D, "f8-J.json")])
print(f"replay:    exit={rc} out={out.strip()!r}")

print("== F9: URL containment weakness (commit in query passes) ==")
sys.path.insert(0, os.path.dirname(REPLAY))
import importlib.util
spec = importlib.util.spec_from_file_location("klr", REPLAY)
klr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(klr)
evil = "https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf?pin=/resolve/" + commit + "/x"
rec = base(schema="kama-llamacpp-live/v5", url=evil, commit_=commit, verified={"at": "record"})
try:
    klr.provenance(rec)
    print(f"replay provenance(): ACCEPTED main-resolved URL with query-injected commit")
except klr.Refused as e:
    print(f"replay provenance(): refused {e}")
# the live tool's record-time regex on the same URL
import re
PIN = re.compile(r"^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+")
m = PIN.match(evil)
print(f"live-tool PINNED_MODEL_URL regex: {'MATCH commit=' + m.group(1)[:8] + '...' if m else 'refused'}")

print("== F10: verified block digests not cross-checked by replay ==")
rec = base(schema="kama-llamacpp-live/v5", url="file://" + mdl, commit_=commit,
           verified={"at": "record", "archive_sha256": "0" * 64, "member_sha256": "0" * 64,
                     "model_sha256": "0" * 64})
try:
    klr.provenance(rec)
    print("replay provenance(): ACCEPTED verified block whose digests contradict the receipt")
except klr.Refused as e:
    print(f"replay provenance(): refused {e}")
