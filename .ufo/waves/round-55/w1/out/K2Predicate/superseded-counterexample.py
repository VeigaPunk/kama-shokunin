#!/usr/bin/env python3
"""K2Predicate counterexample driver (round 55, seat K2Predicate).

Read-only import of the frozen C2 counter; builds scratch git fixtures and calls
m.evaluate() directly. Three cases:

  1. dead-base  - base cites tools/dead.py (never exists => UNRESOLVED at base);
                  tip re-points to tools/new.py + a `superseded` row.
  2. live-base  - control: base citation resolves (the fixture's own honest shape).
  3. line-bypass- dead base token, replacement cited at a different line; then a
                  `fixed`-row control over the same shape (stem check bites first).

Frozen sentence under test (preregistration.json:30 and tools/round54-cited-path-check.py:128):
  "`superseded` rows disclosing a live base citation re-pointed to a cited,
   resolving replacement"
Docstring class text (tools/round54-cited-path-check.py:~105-113):
  "the original token was cited in that surface at --base and resolved there
   (unlike `fixed`, which corrects an UNRESOLVED citation ...)".
"""
import importlib.util, subprocess, tempfile, os, shutil, sys

S = os.environ.get("K2SCRATCH", "/fast/scratch/hyaku/kama-r55/w1/K2Predicate")
C2 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py"

spec = importlib.util.spec_from_file_location("c2", C2)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def mk():
    D = tempfile.mkdtemp(prefix="k2fx-", dir=S)
    env = m.clean_env({"GIT_AUTHOR_NAME": "fx", "GIT_AUTHOR_EMAIL": "fx@invalid",
                       "GIT_COMMITTER_NAME": "fx", "GIT_COMMITTER_EMAIL": "fx@invalid"})
    def g(*a):
        p = subprocess.run(["git", "-C", D, *a], capture_output=True, env=env)
        if p.returncode:
            raise SystemExit(f"git {a}: {p.stderr.decode()[:200]}")
        return p.stdout.decode().strip()
    def w(path, text):
        full = os.path.join(D, path)
        os.makedirs(os.path.dirname(full) or D, exist_ok=True)
        open(full, "w").write(text)
    def commit(msg):
        g("add", "-A"); g("commit", "-q", "-m", msg)
        return g("rev-parse", "HEAD")
    g("init", "-q")
    assert os.path.realpath(g("rev-parse", "--show-toplevel")) == os.path.realpath(D)
    w("tools/ok.py", "ok\n"); w("tools/new.py", "new\n")
    for s in ("SCORECARD.md", "SHONEN.md", "SKILL.md"):
        w(s, "x\n")
    return D, env, g, w, commit

def run(lane_rev, base_rev, g, D):
    detail = []
    ok, counts = m.evaluate(m.Repo(D, lane_rev), None, m.Repo(D, base_rev), detail)
    return ok, counts, detail

def case_dead_live(which):
    D, env, g, w, commit = mk()
    tok = "tools/ok.py" if which == "live-base" else "tools/dead.py"
    w("SCORECARD.md", f"see `{tok}`\n")
    base = commit("base")
    w("SCORECARD.md", "see `tools/new.py`\n")
    w("registry/cited-path-corrections.tsv",
      "surface\ttoken\tclass\tevidence\tnote\n"
      f"SCORECARD.md\t{tok}\tsuperseded\ttools/new.py\t\n")
    tip = commit("tip")
    ok, counts, detail = run(tip, base, g, D)
    print(f"--- case={which} (base token {tok}) ---")
    print("met:", ok, counts)
    for d in detail:
        print("detail:", d)
    shutil.rmtree(D, ignore_errors=True)

def case_line_bypass():
    D, env, g, w, commit = mk()
    w("SCORECARD.md", "l1\nl2\nl3\nl4 `tools/dead.py`\n")       # dead token, line 5
    base = commit("base")
    w("SCORECARD.md", "l1\nl2\nl3\nl4\nl5\nl6 `tools/new.py`\n")  # replacement, line 7
    w("registry/cited-path-corrections.tsv",
      "surface\ttoken\tclass\tevidence\tnote\n"
      "SCORECARD.md\ttools/dead.py\tsuperseded\ttools/new.py\t\n")
    tip = commit("tip")
    ok, counts, detail = run(tip, base, g, D)
    print("--- case=line-bypass (superseded, dead base token, replacement at another line) ---")
    print("met:", ok, counts)
    for d in detail:
        print("detail:", d)
    g("reset", "-q", "--hard", base)
    w("SCORECARD.md", "l1\nl2\nl3\nl4\nl5\nl6 `tools/new.py`\n")
    w("registry/cited-path-corrections.tsv",
      "surface\ttoken\tclass\tevidence\tnote\n"
      "SCORECARD.md\ttools/dead.py\tfixed\ttools/new.py\t\n")
    tip2 = commit("tip2")
    ok2, counts2, detail2 = run(tip2, base, g, D)
    print("--- control=fixed-row over the same dead-base shape ---")
    print("met:", ok2, counts2)
    for d in detail2:
        print("detail:", d)
    shutil.rmtree(D, ignore_errors=True)

case_dead_live("dead-base")
print()
case_dead_live("live-base")
print()
case_line_bypass()
