#!/usr/bin/env python3
"""V3Review round-51 probes, batch 4: clean duplicate-id decoy (decoy after S103) with
sources cross-check, and a corpus row census under both cell splitters."""
import importlib.util
import json
import os
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r51/V3Review"
TOOL = os.path.join(S, "v6-tip.py")
SRCT = os.path.join(S, "sources-tip.py")
IDENT = ["-c", "user.name=fx", "-c", "user.email=fx@invalid", "-c", "commit.gpgsign=false"]
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


def run_tool(d, to):
    p = subprocess.run([sys.executable, TOOL, "--repo", d, "--to", to, "--contract",
                        os.path.join(S, "contract.tsv"), "--json"], capture_output=True, text=True)
    return p.returncode, p.stdout


def run_sources(d, a, b):
    p = subprocess.run([sys.executable, SRCT, "--repo", d, "--from", a, "--to", b, "--path", "SRC.md"],
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip()[:160], p.stderr.strip()[:160]


# ---- F2y: teaches mutated on S102; old S102 row re-added AFTER S103
d = mkrepo("f2y")
rows = HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |",
    "| S102 | doc 2 | docs | A | scope 2 | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |",
    "| S103 | doc 3 | docs | A | scope 3 | sec | lesson 3 | mined | 2026-09-03 | 60d | a.md |"]
base = commit(d, {"N.md": NMD, "SRC.md": rows, "LOG.md": ["log one"]})
new = rows[:4] + [rows[4].replace("lesson 2", "lesson TWO"), rows[5], rows[4]]  # S102 mutated, S103 kept, old S102 appended
tip = commit(d, {"SRC.md": new}, "teaches mutated + old S102 re-added after S103")
code, out = run_tool(d, tip)
res = json.loads(out)
e = [x for x in res["events"] if x["file"] == "SRC.md"][0]
print(f"[F2y] tool exit={code} SRC.md status={e['status']} deleted={e['deleted']} "
      f"permitted={e['permitted']} graded={e['graded']} ungraded={e['ungraded']} "
      f"bad_disclosures={res['summary']['bad_disclosures']}")
sc, so, se = run_sources(d, base, tip)
print(f"[F2y] sources-append-only exit={sc} out={so!r} err={se!r}")

# ---- corpus census: every SOURCES.md row at the tip under both splitters
def load(path, nm):
    spec = importlib.util.spec_from_file_location(nm, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v6 = load(TOOL, "v6tip2")
src = load(SRCT, "srctip2")
ROWR = v6.ROW
n_rows = n_disagree = 0
with open(os.path.join(S, "SOURCES-tip.md"), encoding="utf-8") as fh:
    for ln in fh:
        raw = ln.rstrip("\n")
        if not ROWR.match(raw):
            continue
        n_rows += 1
        c6 = v6.row_cells(raw.encode())
        cs = src.split_cells(raw)
        if (c6 is None) != (cs is None) or (c6 is not None and cs is not None and len(c6) != len(cs)):
            n_disagree += 1
            print(f"[census] DISAGREE: v6={None if c6 is None else len(c6)} "
                  f"sources={None if cs is None else len(cs)}: {raw[:100]}")
print(f"[census] SOURCES.md@tip rows matching v6 ROW regex: {n_rows}; cell-count disagreements: {n_disagree}")
