#!/usr/bin/env python3
"""Demonstrate that the five escaped variants are genuinely wrong per the v3
definition: canonical tool vs variant on bespoke repos (expectations by construction)."""
import os, subprocess, sys, json

ROOT = "/fast/scratch/hyaku/kama-r48/K1Fixture/demos"
os.makedirs(ROOT, exist_ok=True)
CANON = "/fast/scratch/hyaku/kama-r48/K1Fixture/aoa-canonical.py"
VAR = "/fast/scratch/hyaku/kama-r48/K1Fixture/var"
ENV = dict(os.environ, GIT_AUTHOR_NAME="demo", GIT_AUTHOR_EMAIL="demo@fixture.invalid",
           GIT_COMMITTER_NAME="demo", GIT_COMMITTER_EMAIL="demo@fixture.invalid",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
HEADER = "path\trule\tdeclared_at\tregion\tnote"

def git(d, *a):
    p = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=ENV)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(a)}: {p.stderr[:300]}")
    return p.stdout

def mk(name):
    d = os.path.join(ROOT, name)
    if os.path.exists(d):
        subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    assert os.path.realpath(git(d, "rev-parse", "--show-toplevel").strip()) == os.path.realpath(d)
    n = [0]
    def commit(files, delete=()):
        for path, body in files.items():
            full = os.path.join(d, path)
            os.makedirs(os.path.dirname(full) or d, exist_ok=True)
            with open(full, "wb") as fh:
                fh.write(body if isinstance(body, bytes) else ("\n".join(body) + "\n").encode())
        for path in delete:
            git(d, "rm", "-q", path)
        git(d, "add", "-A")
        n[0] += 1
        git(d, "commit", "-q", "--allow-empty", "-m", f"c{n[0]}")
        return git(d, "rev-parse", "HEAD").strip()
    return d, commit

def run(tool, d):
    p = subprocess.run([sys.executable, tool, "--repo", d, "--to", "HEAD", "--json"],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr[-300:]

def show(tag, d, tool):
    rc, out, err = run(tool, d)
    if rc == 2:
        return f"{tag} exit=2 could-not-evaluate: {err.strip()[:120]}"
    j = json.loads(out)
    evs = [(e["commit"][:8], e["file"], e["deleted"], e["graded"], e["ungraded"], e["status"], e["restored_max"])
           for e in j["events"]]
    s = j["summary"]
    return (f"{tag} exit={rc} events={evs} summary=events{s['events']} ungraded_lines="
            f"{s['ungraded_lines']} partial={s['partial']} unrestored={s['unrestored']} "
            f"vanished={s['vanished']} bad={s['bad_declarations']} regressed={s['regressed']}")

# ---- demo A (va): exempt-title startswith vs exact ----
d, commit = mk("A_exempt_prefix")
NOTES = ["# notes", "score.md is append-only below its head.",
         "The ## Axes head of score.md is re-derived in place."]
ROW = "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@NOTES.md:3\tx"
commit({"NOTES.md": NOTES, "registry/append-only-contract.tsv": [HEADER, ROW]})
body = ["# score", "## Axes"] + [f"a{i}" for i in range(24)] + ["## Axesomething"] + [f"s{i}" for i in range(21)]
commit({"score.md": body})
commit({"score.md": ["# score", "## Axes"] + [f"a{i}" for i in range(24)] + ["## Axesomething"]})
print("== demo A: exempt-title match, delete 21 lines of `## Axesomething` (not an exempt title, but startswith `## Axes`)")
print(show("canonical", d, CANON))
print(show("va-variant", d, os.path.join(VAR, "va_startswith_title.py")))

# ---- demo B (vb): union of two exempt rows; last-row-only drops the earlier title ----
d, commit = mk("B_union_rows")
NOTES = ["# notes", "score.md is append-only below its head.",
         "The ## Axes and ## Plan heads of score.md are re-derived in place."]
ROWS = ["score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Plan@NOTES.md:3\tx",
        "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@NOTES.md:3\tx"]
commit({"NOTES.md": NOTES, "registry/append-only-contract.tsv": [HEADER] + ROWS})
body = ["# score", "## Axes"] + [f"a{i}" for i in range(24)] + ["## Plan"] + [f"p{i}" for i in range(22)]
commit({"score.md": body})
# c1: delete 21 of the 22 `## Plan` lines (section gutted at the event)
commit({"score.md": ["# score", "## Axes"] + [f"a{i}" for i in range(24)] + ["## Plan"]})
# c2: regrow `## Plan` to 30 lines -> window max(Plan)=31 >= parent 23 -> eligible at the event
commit({"score.md": ["# score", "## Axes"] + [f"a{i}" for i in range(24)] + ["## Plan"]
        + [f"p{i}" for i in range(30)]})
print("== demo B: two exempt rows (union Axes|Plan vs last-row-only Axes); delete 21 `## Plan` lines,")
print("   then regrow Plan later in the window: canonical exempts Plan (ungraded), variant grades it")
print(show("canonical", d, CANON))
print(show("vb-variant", d, os.path.join(VAR, "vb_last_row_only.py")))

# ---- demo C (vf): binary change must be skipped, not become an event ----
d, commit = mk("C_binary")
NOTES = ["# notes", "bin.bin is append-only."]
ROW = "bin.bin\tA\tNOTES.md:2\t*\tx"
commit({"NOTES.md": NOTES, "registry/append-only-contract.tsv": [HEADER, ROW],
        "bin.bin": b"\x00\x01" * 40})
commit({"bin.bin": b"\x00\x02" * 41})
print("== demo C: binary change to bin.bin (numstat `-`): definition says skipped, no event")
print(show("canonical", d, CANON))
print(show("vf-variant", d, os.path.join(VAR, "vf_binary_as_event.py")))

# ---- demo D (vi): empty region cell is malformed -> cannot evaluate; variant accepts as `*` ----
d, commit = mk("D_empty_region")
NOTES = ["# notes", "score.md is append-only below its head."]
ROW = "score.md\tA-corr\tNOTES.md:2\t\tx"
commit({"NOTES.md": NOTES, "registry/append-only-contract.tsv": [HEADER, ROW],
        "score.md": [f"a{i}" for i in range(30)]})
commit({"score.md": [f"a{i}" for i in range(5)]})
print("== demo D: contract row with empty region cell; definition requires `*`/exempt/only (else 2)")
print(show("canonical", d, CANON))
print(show("vi-variant", d, os.path.join(VAR, "vi_empty_region_star.py")))

# ---- demo E (vl): unmatched pattern is informational; exit must stay 0 ----
d, commit = mk("E_unmatched")
NOTES = ["# notes", "LOG.md is append-only.", "nope is append-only."]
ROWS = ["LOG.md\tA\tNOTES.md:2\t*\tx", "nope/*.md\tA\tNOTES.md:3\t*\tx"]
commit({"NOTES.md": NOTES, "registry/append-only-contract.tsv": [HEADER] + ROWS,
        "LOG.md": [f"a{i}" for i in range(30)]})
commit({"LOG.md": [f"a{i}" for i in range(30)] + ["appended"]})
print("== demo E: clean repo + unmatched pattern `nope/*.md`; definition keeps unmatched informational (exit 0)")
print(show("canonical", d, CANON))
print(show("vl-variant", d, os.path.join(VAR, "vl_exit_on_unmatched.py")))
