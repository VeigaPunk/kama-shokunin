#!/usr/bin/env python3
"""M2Ctr C2-counter mutation test - repro script (executed 2026-10-26, lane round-46 w1).

Builds fixture clones of the lane at 4a2a4d5 (a: + SCORECARD row; b1: + broken CLI
default threshold 21; b2: + broken audit() default threshold 21), runs the pristine
counter and 32 single-site mutants against all three, classifies killed/survived
against the pristine verdict triple, and re-runs pristine (restoration control).
"""
import subprocess, os, shutil, json, hashlib, time
from concurrent.futures import ThreadPoolExecutor

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
S    = "/fast/scratch/hyaku/kama-r46/M2Ctr"
PIN  = "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"

def git(repo, *args, ident=False):
    cmd = ["git", "-C", repo]
    if ident:
        cmd += ["-c", "user.name=m2ctr-fixture", "-c", "user.email=m2ctr-fixture@invalid", "-c", "commit.gpgsign=false"]
    p = subprocess.run(cmd + list(args), capture_output=True, text=True)
    assert p.returncode == 0, (args, p.stderr)
    return p.stdout

def clone(src, dst, at=None):
    if os.path.exists(dst): shutil.rmtree(dst)
    p = subprocess.run(["git", "clone", "-q", "--shared", "--no-hardlinks", src, dst], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    if at: git(dst, "checkout", "-q", "--detach", at)
    assert os.path.realpath(git(dst, "rev-parse", "--show-toplevel").strip()) == os.path.realpath(dst)
    return dst

fixa = clone(LANE, f"{S}/fixa", PIN)
with open(f"{fixa}/SCORECARD.md", "a") as fh:
    fh.write("| append-only-audit | capability acquisition (C2 round 46) | selftest=1 fixture=1 lane=1 table=1 | tools/round46-append-audit-check.py | 46 |\n")
git(fixa, "add", "SCORECARD.md"); git(fixa, "commit", "-q", "-m", "fixture a", ident=True)
A = git(fixa, "rev-parse", "HEAD").strip(); assert git(fixa, "status", "--porcelain").strip() == ""

fixb = clone(fixa, f"{S}/fixb", A)
toolp = f"{fixb}/tools/append-only-audit.py"; src = open(toolp).read()
old = 'ap.add_argument("--threshold", type=int, default=20)'
assert src.count(old) == 1
open(toolp, "w").write(src.replace(old, old.replace("default=20", "default=21")))
git(fixb, "add", "tools/append-only-audit.py"); git(fixb, "commit", "-q", "-m", "fixture b1", ident=True)

fixb2 = clone(fixa, f"{S}/fixb2", A)
toolp = f"{fixb2}/tools/append-only-audit.py"; src = open(toolp).read()
old = 'def audit(repo_path, to="HEAD", threshold=20, files=None):'
assert src.count(old) == 1
open(toolp, "w").write(src.replace(old, old.replace("threshold=20", "threshold=21")))
git(fixb2, "add", "tools/append-only-audit.py"); git(fixb2, "commit", "-q", "-m", "fixture b2", ident=True)

pristine = f"{S}/counter/pristine.py"; shutil.copyfile(f"{LANE}/tools/round46-append-audit-check.py", pristine)
SCEN = {"a": fixa, "b1": fixb, "b2": fixb2}

def run(counter, scen, tag):
    work = f"{S}/runs/{tag}/{scen}"; os.makedirs(work, exist_ok=True)
    p = subprocess.run(["python3", counter, "--repo", SCEN[scen], "--tip", "HEAD", "--scratch", work],
                       capture_output=True, text=True, env=dict(os.environ, TMPDIR=work), timeout=900)
    return {"rc": p.returncode, "out": p.stdout, "err": p.stderr}

MUT = [
 ("M01_thr19",            "THRESHOLD = 20", "THRESHOLD = 19"),
 ("M02_thr21",            "THRESHOLD = 20", "THRESHOLD = 21"),
 ("M03_thr25",            "THRESHOLD = 20", "THRESHOLD = 25"),
 ("M04_thr_boundary_le",  "if len(dele) < THRESHOLD:", "if len(dele) <= THRESHOLD:"),
 ("M05_diff_order_swap",  '"-U0", p, c, "--", f', '"-U0", c, p, "--", f'),
 ("M06_diff_empty_tree",  "p = par.stdout.strip()", 'p = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"'),
 ("M07_revlist_no_topo",  '"rev-list", "--topo-order", "--reverse", to', '"rev-list", "--reverse", to'),
 ("M08_rat_plus1",        "k = sum(1 for x in dele if x in tip)", "k = sum(1 for x in dele if x in tip) + 1"),
 ("M09_rat_distinct",     "k = sum(1 for x in dele if x in tip)", "k = len({x for x in dele if x in tip})"),
 ("M10_status_never_unrest", '("unrestored" if k == 0 else "partial")', '("unrestored" if k < 0 else "partial")'),
 ("M11_partial_renamed",  'else "partial")', 'else "part")'),
 ("M12_status_tol_one",   'status = "restored" if k == len(dele) else', 'status = "restored" if k >= len(dele) - 1 else'),
 ("M13_rb_include_self",  "for c2 in commits[i + 1:]:", "for c2 in commits[i:]:"),
 ("M14_rb_any",           "if all(x in have for x in dele):", "if any(x in have for x in dele):"),
 ("M15_rb_no_break",      "rb = c2\n                    break", "rb = c2"),
 ("M16_rb_skip_one",      "for c2 in commits[i + 1:]:", "for c2 in commits[i + 2:]:"),
 ("M17_fx_B_rat_1",       '(shas["c6"], "LOG.md", 25, 0, "unrestored", None),', '(shas["c6"], "LOG.md", 25, 1, "unrestored", None),'),
 ("M18_fx_mid_rc1",       "ok2 = e2 is not None and norm(e2) == exp_mid and rc2 == 0", "ok2 = e2 is not None and norm(e2) == exp_mid and rc2 == 1"),
 ("M19_fx_drop_B",        '                (shas["c6"], "LOG.md", 25, 0, "unrestored", None),\n', ""),
 ("M20_fx_del29",         "log3 = log2[:5] + log2[35:]", "log3 = log2[:6] + log2[35:]"),
 ("M21_lane_rc_zero",     "rc3 == (1 if bad else 0)", "rc3 == 0"),
 ("M22_lane_rc_any",      "rc3 == (1 if bad else 0)", "rc3 in (0, 1)"),
 ("M23_bad_false",        'bad = any(e["status"] != "restored" for e in lane_ev)', "bad = False"),
 ("M24_table_cell45",     'cells[-1] == "46"', 'cells[-1] == "45"'),
 ("M25_table_drop_cell",  'if cells and cells[-1] == "46":', "if cells:"),
 ("M26_table_name_x",     '"append-only-audit" in x', '"append-only-audit-x" in x'),
 ("M27_selftest_floor60", "int(m.group(1)) >= 6", "int(m.group(1)) >= 60"),
 ("M28_selftest_floor1",  "int(m.group(1)) >= 6", "int(m.group(1)) >= 1"),
 ("M29_selftest_tol1",    "int(m.group(2)) == 0", "int(m.group(2)) <= 1"),
 ("M30_met_lane_table",   "met = all(legs.values())", 'met = legs["lane"] and legs["table"]'),
 ("M31_met_any",          "met = all(legs.values())", "met = any(legs.values())"),
 ("M32_fx_ok1_drop_rc",   "ok1 = e1 is not None and norm(e1) == exp_full and rc1 == 1", "ok1 = e1 is not None and norm(e1) == exp_full"),
]
src = open(pristine).read(); os.makedirs(f"{S}/counter/mutants", exist_ok=True)
mfiles = {}
for name, old, new in MUT:
    assert src.count(old) == 1, (name, src.count(old))
    mfiles[name] = f"{S}/counter/mutants/{name}.py"
    open(mfiles[name], "w").write(src.replace(old, new))

def job(a):
    name, scen = a
    return name, scen, run(mfiles[name], scen, f"mut_{name}")

jobs = [(n, s) for n in mfiles for s in SCEN]
res = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, scen, r in ex.map(job, jobs):
        res[(name, scen)] = r
base = {s: run(pristine, s, f"base_{s}") for s in SCEN}
ptrip = tuple(base[s]["rc"] for s in ("a", "b1", "b2"))
out = {}
for n in mfiles:
    rc = tuple(res[(n, s)]["rc"] for s in ("a", "b1", "b2"))
    out[n] = {"rc": rc, "verdict": "SURVIVED" if rc == ptrip else "KILLED",
              "differs_on": [s for s, (x, y) in zip(("a","b1","b2"), zip(rc, ptrip)) if x != y]}
json.dump({"pristine_rc": ptrip, "mutants": out}, open(f"{S}/results.json", "w"), indent=1)
for n, v in out.items(): print(n, v["rc"], v["verdict"], v["differs_on"])
# restoration control
for s in SCEN:
    r = run(pristine, s, f"restored_{s}")
    print("restored", s, "rc", r["rc"], "identical", r["out"] == base[s]["out"])
