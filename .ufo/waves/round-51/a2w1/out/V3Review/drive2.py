#!/usr/bin/env python3
"""V3Review round-51 probes, batch 2: sources-append-only cross-checks (Registry heading),
corrected F4b count check, revert-class disclosure."""
import hashlib
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
    return p.returncode, p.stdout.strip().replace("\n", " | ")[:200], p.stderr.strip()[:200]


def sha(x):
    return hashlib.sha256(x.encode()).hexdigest()


def show(tag, code, out, err):
    try:
        import json as j
        res = j.loads(out)
        evs = [(e["file"], e["status"], e.get("permitted"), e.get("graded"), e.get("disclosed"))
               for e in res.get("events", [])]
        print(f"[{tag}] tool exit={code} events={evs} bad_disclosures={res['summary']['bad_disclosures']}")
    except ValueError:
        print(f"[{tag}] tool exit={code} NO-JSON stderr={err[:200]!r}")


# ---- F1r: escaped-pipe row, status+recheck only; v6 vs sources, both on same fixture
d = mkrepo("f1r")
rows = HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |",
    "| S102 | doc 2 | docs | A | scope a\\|b | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |",
    "| S103 | doc 3 | docs | A | scope 3 | sec | lesson 3 | mined | 2026-09-03 | 60d | a.md |"]
base = commit(d, {"N.md": NMD, "SRC.md": rows, "LOG.md": ["log one"]})
new = [r.replace("| mined |", "| queued |").replace("60d", "30d") if r.startswith("| S102") else r
       for r in rows]
tip = commit(d, {"SRC.md": new}, "status+recheck edit, escaped-pipe row")
code, out, err = run_tool(d, tip)
show("F1r escaped-pipe mutable-only edit", code, out, err)
sc, so, se = run_sources(d, base, tip)
print(f"[F1r] sources-append-only exit={sc} out={so!r} err={se!r}")

# ---- F2r: teaches mutated + old row re-added (duplicate id)
d = mkrepo("f2r")
rows = HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |",
    "| S102 | doc 2 | docs | A | scope 2 | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |",
    "| S103 | doc 3 | docs | A | scope 3 | sec | lesson 3 | mined | 2026-09-03 | 60d | a.md |"]
base = commit(d, {"N.md": NMD, "SRC.md": rows, "LOG.md": ["log one"]})
old = rows[3]
new = rows[:3] + [rows[3].replace("lesson 2", "lesson TWO"), rows[4], old]
tip = commit(d, {"SRC.md": new}, "teaches mutated + old row re-added")
code, out, err = run_tool(d, tip)
show("F2r duplicate-id decoy", code, out, err)
sc, so, se = run_sources(d, base, tip)
print(f"[F2r] sources-append-only exit={sc} out={so!r} err={se!r}")

# ---- F4c: two ledger rows, counts 1+1, only 1 unheld, class correct
d = mkrepo("f4c")
log = ["dup alpha", "tail one"]
commit(d, {"N.md": NMD, "SRC.md": HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"],
    "LOG.md": log})
t2 = commit(d, {"LOG.md": ["tail one", "kept two"]}, "delete one dup line")
key = sha("dup alpha")
led = os.path.join(S, "led-f4c.tsv")
with open(led, "w") as fh:
    fh.write(DHEADER + f"\n{t2}\tLOG.md\t{key}\t1\tin-place-edit\tx\n"
                        f"{t2}\tLOG.md\t{key}\t1\tin-place-edit\tx\n")
code, out, err = run_tool(d, t2, led)
show("F4c dup rows over-count, right class", code, out, err)
import json as _j
try:
    res = _j.loads(out)
    print(f"[F4c] verdicts={[(x['ok'], x['reason']) for x in res['disclosures']]}")
except ValueError:
    pass

# ---- F8: revert-class disclosure end-to-end (subject fetch)
d = mkrepo("f8")
commit(d, {"N.md": NMD, "SRC.md": HEAD + [
    "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"],
    "LOG.md": ["alpha one", "beta two"]})
t2 = commit(d, {"LOG.md": ["beta two"]}, 'Revert "fx"')
key = sha("alpha one")
for klass in ("revert", "removal"):
    led = os.path.join(S, f"led-f8-{klass}.tsv")
    with open(led, "w") as fh:
        fh.write(DHEADER + f"\n{t2}\tLOG.md\t{key}\t1\t{klass}\trevert subject\n")
    code, out, err = run_tool(d, t2, led)
    show(f"F8 revert subject, class={klass}", code, out, err)
    if out:
        try:
            res = _j.loads(out)
            print(f"[F8] verdict={[(x['ok'], x['reason']) for x in res['disclosures']]}")
        except ValueError:
            pass
