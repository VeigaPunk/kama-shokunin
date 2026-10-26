#!/usr/bin/env python3
"""V2Replay fixtures part 2: F2 (replay crash path), F3 (file://), F5-F10."""
import json, os, subprocess, sys, hashlib, shutil, tarfile, re, importlib.util

REPLAY = "/fast/scratch/hyaku/kama-r48/V2Replay/lane/tools/kama-live-replay.py"
LIVE = "/fast/scratch/hyaku/kama-r48/V2Replay/lane/tools/kama-llamacpp-live.py"
S = "/fast/scratch/hyaku/kama-r48/V2Replay/fix2"
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
    "import os,json,sys,hashlib\n"
    "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
    "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
    "open(os.environ.get('ARGV_DUMP','/dev/null'),'w').write(repr(a))\n"
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

def run_cli(args, env=None):
    p = subprocess.run([sys.executable, REPLAY] + args, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr

print("== F2: replay() crash path (compare raises) writes no J ==")
orig = base(captures={"models": {"body": json.dumps({"data": 5})}})
po = wjson("f2-orig.json", orig)
res_path = os.path.join(D, "f2-J.json")
rc, out, err = run_cli(["--receipt", po, "--work", os.path.join(D, "w2"), "--out", res_path,
                        "--live", fake_live])
print(f"replay exit={rc} J_exists={os.path.exists(res_path)} "
      f"stderr_tail={err.strip().splitlines()[-1] if err.strip() else ''!r}")

print("== F3: file:// URLs accepted end-to-end (no network, exit 0) ==")
rev_dir = os.path.join(D, "resolve", commit)
os.makedirs(rev_dir)
shutil.copy(mdl, os.path.join(rev_dir, "m.gguf"))
pinned_file = "file://" + os.path.join(rev_dir, "m.gguf")
rc, out, err = run_cli(["--receipt", wjson("f3.json", base(schema="kama-llamacpp-live/v5",
                    url=pinned_file, commit_=commit, verified={"at": "record"})),
                    "--work", os.path.join(D, "w3"), "--out", os.path.join(D, "f3-J.json"),
                    "--live", fake_live])
print(f"replay exit={rc} stdout={out.strip()!r}")

print("== F5: argv insertion position for v5 ==")
env = dict(os.environ, ARGV_DUMP=os.path.join(D, "argv.txt"))
rc, out, err = run_cli(["--receipt", wjson("f5.json", base(schema="kama-llamacpp-live/v5",
                    url=pinned_file, commit_=commit, verified={"at": "record"})),
                    "--work", os.path.join(D, "w5"), "--out", os.path.join(D, "f5-J.json"),
                    "--live", fake_live], env=env)
argv = eval(open(os.path.join(D, "argv.txt")).read())
i = argv.index("--server-archive")
print(f"replay exit={rc}; argv={argv}")
print(f"--server-archive before --out: {argv[i+2] == '--out'}; after --model-url value: {argv[i-2] == '--model-url'}")

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
rc, out, err = run_cli(["--receipt", wjson("f7.json", base()),
                        "--work", os.path.join(D, "w7"), "--out", os.path.join(D, "f7-J.json"),
                        "--live", v5live])
j = json.load(open(os.path.join(D, "f7-J.json")))
print(f"exit={rc} match={j['match']} mismatches={j['mismatches']}")

print("== F8: --compare skips provenance validation (replay refuses same receipt) ==")
nov = base(schema="kama-llamacpp-live/v5")  # v5 with no commit, no verified
pn = wjson("f8.json", nov)
rc, out, _ = run_cli(["--compare", pn, pn])
print(f"--compare self: exit={rc} out={out.strip()!r}")
rc, out, _ = run_cli(["--receipt", pn, "--work", os.path.join(D, "w8"), "--out", os.path.join(D, "f8-J.json")])
print(f"replay:         exit={rc} out={out.strip()!r}")

print("== F9: URL containment weakness (commit in query passes both tools) ==")
spec = importlib.util.spec_from_file_location("klr", REPLAY)
klr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(klr)
evil = ("https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/"
        "stories260K.gguf?pin=/resolve/" + commit + "/x")
rec = base(schema="kama-llamacpp-live/v5", url=evil, commit_=commit, verified={"at": "record"})
try:
    klr.provenance(rec)
    print("replay provenance(): ACCEPTED main-resolved URL with query-injected commit")
except klr.Refused as e:
    print(f"replay provenance(): refused {e}")
src = open(LIVE).read()
pin = re.search(r"^PINNED_MODEL_URL = (.+)$", src, re.M).group(1)
PIN = eval(pin)
m = PIN.match(evil)
print(f"live-tool regex {pin}: {'MATCH commit=' + m.group(1)[:8] + '...' if m else 'refused'}")

print("== F10: verified-block digests not cross-checked by replay ==")
rec = base(schema="kama-llamacpp-live/v5", url=pinned_file, commit_=commit,
           verified={"at": "record", "archive_sha256": "0" * 64, "member_sha256": "0" * 64,
                     "model_sha256": "0" * 64})
try:
    klr.provenance(rec)
    print("replay provenance(): ACCEPTED verified block whose digests contradict the receipt")
except klr.Refused as e:
    print(f"replay provenance(): refused {e}")
