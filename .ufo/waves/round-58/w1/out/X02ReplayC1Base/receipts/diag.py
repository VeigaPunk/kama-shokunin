import os, pathlib, shutil, subprocess, sys, tempfile
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "dcd69473dd7e33b316e2ba238a48e5119a6cd809"
BASE_CHECKER = "2f53614e6f5895560edb775cc3e74841aa0dd44c:tools/round56-prereg-check.py"
VARIANTS = "tests/round58-battery-variants"
BENIGN = ["B1-rename-comment", "B2-helper-leg", "B3-concat-labels"]
NOOPS = ["N01-calls-removed","N02-if-false","N03-unused-function","N04-early-return","N05-env-guard",
         "N06-run-body-noop","N07-mutant-assert-noop","N08-main-not-invoked","N09-empty-loop",
         "N10-run-rebound","N11-try-else"]
PREREG = ".ufo/waves/round-56/preregistration.json"
BATTERY = "tools/round56-env-leg-battery.py"
SIDE = ["tools/round56-env-leg-test.py","tools/round54-replay-code-audit.py","tools/round56-replay-code-audit.py"]

def genv():
    e = {k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
    e["GIT_CONFIG_GLOBAL"] = os.devnull; e["GIT_CONFIG_NOSYSTEM"] = "1"
    return e

def git(repo,*a):
    return subprocess.run(["git","-C",str(repo),*a],capture_output=True,env=genv())

def blob(rev,p):
    r = git(LANE,"show",f"{rev}:{p}")
    if r.returncode: raise SystemExit(f"missing {rev}:{p}")
    return r.stdout

work = pathlib.Path(tempfile.mkdtemp(prefix="diag-", dir=os.environ["TMPDIR"]))
try:
    checker = work/"checker-under-test.py"
    r,_,pth = BASE_CHECKER.partition(":")
    checker.write_bytes(blob(r,pth))
    common = {PREREG: blob(TIP,PREREG)}
    for f in SIDE: common[f] = blob(TIP,f)
    for name in ["genuine"]+BENIGN+NOOPS:
        fx = work/name; fx.mkdir()
        assert git(fx,"init","-q").returncode == 0
        top = git(fx,"rev-parse","--show-toplevel").stdout.decode().strip()
        assert os.path.realpath(top)==os.path.realpath(fx), (top, fx)
        files = dict(common); files[BATTERY] = blob(TIP,f"{VARIANTS}/{name}.py")
        for rel,data in files.items():
            d = fx/rel; d.parent.mkdir(parents=True, exist_ok=True); d.write_bytes(data)
        git(fx,"add","-A")
        c = git(fx,"-c","user.name=x02-diag","-c","user.email=x02-diag@invalid","commit","-q","-m","fixture")
        assert c.returncode == 0, c.stderr
        p = subprocess.run([sys.executable,str(checker),"--repo",str(fx),"--tip","HEAD"],
                           capture_output=True,text=True,cwd=str(fx),timeout=120,
                           env={**genv(),"PYTHONDONTWRITEBYTECODE":"1"})
        body = (p.stdout.strip().replace("\n"," | ") or "<no stdout>")
        print(f"{name}\trc={p.returncode}\t{body}")
finally:
    shutil.rmtree(work, ignore_errors=True)
