#!/usr/bin/env python3
"""V2C2Delta: exercise the round-55 superseded block of round54-cited-path-check.py
in synthetic scratch repos (never in the lane)."""
import importlib.util, os, subprocess, sys, tempfile, shutil

S = "/fast/scratch/hyaku/kama-r55/w1/V2C2Delta"
spec = importlib.util.spec_from_file_location("ctr", os.path.join(S, "counter-tip.py"))
ctr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctr)

ENV = ctr.clean_env({"GIT_AUTHOR_NAME": "fx", "GIT_AUTHOR_EMAIL": "fx@invalid",
                     "GIT_COMMITTER_NAME": "fx", "GIT_COMMITTER_EMAIL": "fx@invalid",
                     "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"})
LED = "registry/cited-path-corrections.tsv"
HDR = "surface\ttoken\tclass\tevidence\tnote\n"


def mkrepo():
    D = tempfile.mkdtemp(prefix="v2d-", dir=S)
    subprocess.run(["git", "-C", D, "init", "-q"], env=ENV, check=True, capture_output=True)
    top = subprocess.run(["git", "-C", D, "rev-parse", "--show-toplevel"], env=ENV,
                         capture_output=True, text=True).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(D), top
    return D


def w(D, p, t):
    full = os.path.join(D, p)
    os.makedirs(os.path.dirname(full) or D, exist_ok=True)
    with open(full, "w") as fh:
        fh.write(t)


def commit(D, msg="c"):
    subprocess.run(["git", "-C", D, "add", "-A"], env=ENV, check=True, capture_output=True)
    subprocess.run(["git", "-C", D, "commit", "-q", "--allow-empty", "-m", msg], env=ENV,
                   check=True, capture_output=True)
    return subprocess.run(["git", "-C", D, "rev-parse", "HEAD"], env=ENV,
                          capture_output=True, text=True).stdout.strip()


def repo_pair(base_scard, tip_scard, base_files, tip_files, base_rows, tip_rows):
    """Build one scratch repo; returns (tip_repo, base_repo)."""
    D = mkrepo()
    w(D, "SCORECARD.md", base_scard)
    w(D, "SHONEN.md", "x\n")
    w(D, "SKILL.md", "x\n")
    for p, t in base_files.items():
        w(D, p, t)
    if base_rows is not None:
        w(D, LED, HDR + base_rows)
    brev = commit(D, "base")
    w(D, "SCORECARD.md", tip_scard)
    for p, t in tip_files.items():
        w(D, p, t)
    if tip_rows is None:
        if os.path.exists(os.path.join(D, LED)):
            os.unlink(os.path.join(D, LED))
    else:
        w(D, LED, HDR + tip_rows)
    trev = commit(D, "tip")
    return ctr.Repo(D, trev), ctr.Repo(D, brev), D


def run(name, tip, base, extra=""):
    det = []
    ok, c = ctr.evaluate(tip, None, base, det)
    badlines = [d for d in det if d.startswith("bad ledger")]
    print(f"{name}: ok={ok} counts={c}")
    for d in badlines:
        print(f"    {d}")
    for d in det:
        if d.startswith("dropped") or d.startswith("stale") or d.startswith("undisclosed"):
            print(f"    {d}")
    return ok, c, det


print("== clause reachability matrix ==")

# honest: base cites live.py (resolves); tip re-points to new.py + superseded row
tip, base, _ = repo_pair(
    "closure `tools/live.py`\n", "closure `tools/new.py`\n",
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    None, "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\tn\n")
run("honest (expect met)", tip, base)

# clause (a): token still cited at tip
tip, base, _ = repo_pair(
    "closure `tools/live.py`\n", "still `tools/live.py` and `tools/new.py`\n",
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    None, "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\tn\n")
run("clause-a still-cited (expect bad)", tip, base)

# clause (b): replacement not cited at tip
tip, base, _ = repo_pair(
    "closure `tools/live.py`\n", "closure moved away in prose\n",
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    None, "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\tn\n")
run("clause-b replacement-uncited (expect bad)", tip, base)

# clause (c): replacement cited but does not resolve
tip, base, _ = repo_pair(
    "closure `tools/live.py`\n", "closure `tools/new.py`\n",
    {"tools/live.py": "l\n"},
    {"tools/live.py": "l\n"},   # tools/new.py never committed -> cited but missing
    None, "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\tn\n")
run("clause-c replacement-unresolving (expect bad + undisclosed)", tip, base)

# clause (d): token never cited at base
tip, base, _ = repo_pair(
    "clean\n", "closure `tools/new.py`\n",
    {"tools/new.py": "n\n"}, {"tools/new.py": "n\n"},
    None, "SCORECARD.md\ttools/ghost.py\tsuperseded\ttools/new.py\tn\n")
run("clause-d not-cited-at-base (expect bad)", tip, base)

# clause (d) None path: evaluate with base_lane=None -> base_citelines={}
tip, base, _ = repo_pair(
    "clean\n", "closure `tools/new.py`\n",
    {"tools/new.py": "n\n"}, {"tools/new.py": "n\n"},
    None, "SCORECARD.md\ttools/ghost.py\tsuperseded\ttools/new.py\tn\n")
run("no-base evaluate (expect bad via base_citelines={})", tip, None)

# direct check_row: same row, base_citelines=None vs {}
cited, unres = ctr.survey(tip, None)
row = {"line": 2, "surface": "SCORECARD.md", "token": "tools/ghost.py",
       "class": "superseded", "evidence": "tools/new.py"}
r1 = ctr.check_row(row, None, tip, None, cited, {}, base_citelines=None)
r2 = ctr.check_row(row, None, tip, None, cited, {}, base_citelines={})
print(f"check_row base_citelines=None -> {r1!r}   base_citelines={{}} -> {r2!r}")

print("== laundering: unresolved-at-base token rowed superseded ==")

# base cites a NEVER-committed path (unresolved at base, disclosed by an honest
# `never` row at base); tip drops the citation, deletes the never row, and adds a
# fabricated superseded row re-pointing it at any resolving citation.
tip, base, _ = repo_pair(
    "see `tools/ghost.py` and `tools/live.py`\n", "see `tools/live.py`, now `tools/new.py`\n",
    {"tools/live.py": "l\n"},
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    "SCORECARD.md\ttools/ghost.py\tnever\t-\thonest at base\n",
    "SCORECARD.md\ttools/ghost.py\tsuperseded\ttools/new.py\tforged: ghost never resolved\n")
run("laundering (defect -> expect met=True under current code)", tip, base)

# same tip but keep the never row: stale kills met (row deletion is required)
tip, base, _ = repo_pair(
    "see `tools/ghost.py` and `tools/live.py`\n", "see `tools/live.py`, now `tools/new.py`\n",
    {"tools/live.py": "l\n"},
    {"tools/live.py": "l\n", "tools/new.py": "n\n"},
    "SCORECARD.md\ttools/ghost.py\tnever\t-\thonest at base\n",
    "SCORECARD.md\ttools/ghost.py\tnever\t-\tkept\n"
    "SCORECARD.md\ttools/ghost.py\tsuperseded\ttools/new.py\tforged\n")
run("laundering with never row kept (expect stale)", tip, base)

print("== fixture clobber demonstration ==")

fxdir1 = os.path.join(S, "fx1"); os.makedirs(fxdir1, exist_ok=True)
d1 = []
got1 = ctr.fixture(fxdir1, d1)
print(f"unpatched fixture: got={got1}/15; superseded line: "
      f"{[d for d in d1 if 'superseded' in d]}")

# Monkeypatch: superseded rows always pass check_row (clause (b) regressed).
orig_check_row = ctr.check_row
def patched(row, bad_exp, lane, fleet, cited_tip, base_unres, base_citelines=None,
            digest_of=None, base_rows=None):
    if row["class"] == "superseded":
        return None
    return orig_check_row(row, bad_exp, lane, fleet, cited_tip, base_unres,
                          base_citelines, digest_of, base_rows)
ctr.check_row = patched

# instrument evaluate to record every call's result
calls = []
orig_eval = ctr.evaluate
def logging_eval(lane, fleet, base_lane, detail, verbose=True):
    ok, c = orig_eval(lane, fleet, base_lane, detail, verbose)
    calls.append((ok, dict(c)))
    return ok, c
ctr.evaluate = logging_eval

fxdir2 = os.path.join(S, "fx2"); os.makedirs(fxdir2, exist_ok=True)
d2 = []
got2 = ctr.fixture(fxdir2, d2)
sup_line = [d for d in d2 if "superseded" in d]
print(f"patched (clause-b dead) fixture: got={got2}/15; superseded line: {sup_line}")
print(f"last two evaluate() results (honest, forged): {calls[-2:]}")
