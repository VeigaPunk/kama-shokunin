#!/usr/bin/env python3
"""V3Review round-51 probes, batch 3: F2 corrected (duplicate-id decoy, proper indices),
F4d over-count with the mechanically correct class."""
import hashlib
import json
import os
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r51/V3Review"
TOOL = os.path.join(S, "v6-tip.py")
SRCT = os.path.join(S, "sources-tip.py")
IDENT = ["-c", "user.name=fx", "-c", "user.email=fx@invalid", "-c", "commit.gpgsign=false"]
DHEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
CONTRACT = "path\trule\tdeclared_at\tregion\tnote\nSRC.md\tA-row\tN.md:2\t*\tx\nLOG.md\tA\tN.md:3\t*\tx\n"
NMD = ["# n", "SRC.md is append-only by row.", "LOG.md is append-only."]
HEAD = ["## Registry",
        "| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]
with open(os.path.join(S, "contract.tsv"), "w") as fh:
    fh.write(CONTRACT)


def sh(*a):
    return subprocess.run(list(a), capture_output=True, text=True)


def mkrepo(name):
    d = os.path.join(S, "fx-" + name)
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    sh("git", "-C", d, "init", "-q")
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), f"toplevel mismatch {name}"
    sh("git", "-C", d, "config", "user.name", "fx")
    sh("git", "-C", d, "config", "user.email", "fx@invalid")
    return d


def commit(d, files, msg="fx"):
    for fn, body in files.items():
        with open(os.path.join(d, fn), "w") as fh:
            fh.write("".join(x + "\n" for x in body))
    sh("git", "-C", d, "add", "-A")
    r = sh("git", "-C", d, *IDENT, "commit", "-q", "-m", msg)
    assert r.returncode == 0, r.stderr
    return sh("git", "-C", d, "rev-parse", "HEAD").stdout.strip()


def run_tool(d, to, ledger=None):
    argv = [sys.executable, TOOL, "--repo", d, "--to", to, "--contract",
            os.path.join(S, "contract.tsv"), "--json"]
    if ledger:
        argv += ["--disclosures", ledger]
    p = subprocess.run(argv, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr.strip()


def run_sources(d, a, b):
    p = subprocess.run([sys.executable, SRCT, "--repo", d, "--from", a, "--to", b, "--path", "SRC.md"],
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip()[:160], p.stderr.strip()[:160]


def sha(x):
    return hashlib.sha256(x.encode()).hexdigest()


# ---- F2x: teaches mutated on S102 + old S102 row re-added after S103 (duplicate id)
d = mkrepo("f2x")
rows = HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |",
    "| S102 | doc 2 | docs | A | scope 2 | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |",
    "| S103 | doc 3 | docs | A | scope 3 | sec | lesson 3 | mined | 2026-09-03 | 60d | a.md |"]
base = commit(d, {"N.md": NMD, "SRC.md": rows, "LOG.md": ["log one"]})
old_s102 = rows[4]
new = rows[:3] + [rows[4].replace("lesson 2", "lesson TWO"), rows[5], old_s102]
tip = commit(d, {"SRC.md": new}, "teaches mutated + old S102 row re-added")
code, out, err = run_tool(d, tip)
res = json.loads(out)
e = [x for x in res["events"] if x["file"] == "SRC.md"][0]
print(f"[F2x] tool exit={code} SRC.md status={e['status']} permitted={e['permitted']} "
      f"graded={e['graded']} deleted={e['deleted']} summary.bad_disclosures={res['summary']['bad_disclosures']}")
sc, so, se = run_sources(d, base, tip)
print(f"[F2x] sources-append-only exit={sc} out={so!r} err={se!r}")

# ---- F4d: over-count with correct (removal) class: two rows 1+1, one unheld line
d = mkrepo("f4d")
log = ["dup alpha", "tail one"]
commit(d, {"N.md": NMD, "SRC.md": HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"],
    "LOG.md": log})
t2 = commit(d, {"LOG.md": ["tail one", "kept two"]}, "delete one line")
key = sha("dup alpha")
led = os.path.join(S, "led-f4d.tsv")
with open(led, "w") as fh:
    fh.write(DHEADER + f"\n{t2}\tLOG.md\t{key}\t1\tremoval\tx\n"
                        f"{t2}\tLOG.md\t{key}\t1\tremoval\tx\n")
code, out, err = run_tool(d, t2, led)
res = json.loads(out)
e = res["events"][0]
print(f"[F4d] tool exit={code} status={e['status']} graded={e['graded']} disclosed={e['disclosed']} "
      f"undisclosed={e['undisclosed']} bad_disclosures={res['summary']['bad_disclosures']}")
print(f"[F4d] verdicts={[(x['ok'], x['reason']) for x in res['disclosures']]}")
