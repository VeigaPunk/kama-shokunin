#!/usr/bin/env python3
"""V3Review round-51: fixture probes for tools/append-only-audit.py v6 findings."""
import hashlib
import importlib.util
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
NM_CONTRACT = CONTRACT + "no-such-*.md\tA\tN.md:3\t*\tx\n"
NMD = ["# n", "SRC.md is append-only by row.", "LOG.md is append-only."]


def sh(*args, **kw):
    return subprocess.run(list(args), capture_output=True, text=True, **kw)


def mkrepo(name):
    d = os.path.join(S, "fx-" + name)
    subprocess.run(["rm", "-rf", d])
    os.makedirs(d)
    sh("git", "-C", d, "init", "-q")
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), f"toplevel mismatch {name}: {top}"
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


def run_tool(d, to, contract, ledger=None):
    argv = [sys.executable, TOOL, "--repo", d, "--to", to, "--contract", contract, "--json"]
    if ledger:
        argv += ["--disclosures", ledger]
    p = subprocess.run(argv, capture_output=True, text=True)
    try:
        res = json.loads(p.stdout)
    except ValueError:
        res = None
    return p.returncode, res, p.stderr.strip()


def run_sources(d, a, b):
    p = subprocess.run([sys.executable, SRCT, "--repo", d, "--from", a, "--to", b,
                        "--path", "SRC.md"],
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def write_ledger(name, rows):
    p = os.path.join(S, name)
    with open(p, "w") as fh:
        fh.write(DHEADER + "\n" + "".join(r + "\n" for r in rows))
    return p


def ev(res, f):
    e = [x for x in (res or {}).get("events", []) if x.get("file") == f]
    return e[0] if len(e) == 1 else {}


def sha(x):
    return hashlib.sha256(x.encode()).hexdigest()


def report(tag, code, res, err, keys=("status", "permitted", "graded", "disclosed")):
    if res is None:
        print(f"[{tag}] tool exit={code} NO-JSON stderr={err[:200]!r}")
        return
    e_all = res.get("events", [])
    s = res.get("summary", {})
    print(f"[{tag}] tool exit={code} events=" +
          str([(e["file"], *[e.get(k) for k in keys]) for e in e_all]) +
          f" undisclosed={[e.get('undisclosed') for e in e_all]}" +
          f" bad_disclosures={s.get('bad_disclosures')} regressed={s.get('regressed')}" +
          f" unmatched={s.get('unmatched')} vanished={s.get('vanished')}" +
          f" bad_declarations={s.get('bad_declarations')}")


with open(os.path.join(S, "contract.tsv"), "w") as _fh:
    _fh.write(CONTRACT)


# ---------------------------------------------------------------- parser unit view
def parser_view():
    def load(path, nm):
        spec = importlib.util.spec_from_file_location(nm, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    v6 = load(TOOL, "v6tip")
    src = load(SRCT, "srctip")
    esc = "| S102 | doc 2 | docs | A | scope a\\|b | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |"
    plain = "| S102 | doc 2 | docs | A | scope ab | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |"
    for tag, ln in (("escaped", esc), ("plain", plain)):
        v6c = v6.row_cells(ln.encode())
        src_c = src.split_cells(ln)
        print(f"[parser {tag}] v6.row_cells n={None if v6c is None else len(v6c)} "
              f"cells={v6c!r}")
        print(f"[parser {tag}] sources.split_cells n={None if src_c is None else len(src_c)}")
    return v6, src


# ---------------------------------------------------------------- F1 escaped pipe
def f1():
    d = mkrepo("f1")
    rows = ["| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |",
            "| S102 | doc 2 | docs | A | scope a\\|b | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |",
            "| S103 | doc 3 | docs | A | scope 3 | sec | lesson 3 | mined | 2026-09-03 | 60d | a.md |"]
    base = commit(d, {"N.md": NMD, "SRC.md": rows, "LOG.md": ["log one"]})
    new = [r.replace("| mined |", "| queued |").replace("60d", "30d") if r.startswith("| S102") else r
           for r in rows]
    tip = commit(d, {"SRC.md": new}, "status+recheck edit on escaped-pipe row")
    code, res, err = run_tool(d, tip, os.path.join(S, "contract.tsv"))
    report("F1 escaped-pipe status-only edit", code, res, err)
    sc, so, se = run_sources(d, base, tip)
    print(f"[F1] sources-append-only exit={sc} out={so[:160]!r} err={se[:120]!r}")
    with open(os.path.join(S, "f1-SRC-tip.txt"), "w") as fh:
        fh.write("\n".join(new))
    return base, tip


# ---------------------------------------------------------------- F2 duplicate-id decoy
def f2():
    d = mkrepo("f2")
    rows = ["| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |",
            "| S102 | doc 2 | docs | A | scope 2 | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |",
            "| S103 | doc 3 | docs | A | scope 3 | sec | lesson 3 | mined | 2026-09-03 | 60d | a.md |"]
    base = commit(d, {"N.md": NMD, "SRC.md": rows, "LOG.md": ["log one"]})
    old_s102 = rows[3]
    mutated = rows[3].replace("lesson 2", "lesson TWO")
    new = rows[:3] + [mutated, rows[4], old_s102]      # teaches mutated in place; OLD row re-added after S103
    tip = commit(d, {"SRC.md": new}, "mutate teaches + re-add old row (duplicate id)")
    code, res, err = run_tool(d, tip, os.path.join(S, "contract.tsv"))
    report("F2 duplicate-id decoy", code, res, err)
    sc, so, se = run_sources(d, base, tip)
    print(f"[F2] sources-append-only exit={sc} out={so[:160]!r} err={se[:120]!r}")


# ---------------------------------------------------------------- F4 duplicate ledger rows
def f4():
    d = mkrepo("f4")
    log = ["dup alpha", "dup alpha", "tail one"]
    commit(d, {"N.md": NMD, "SRC.md":
               ["| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
                "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"],
               "LOG.md": log})
    key = sha("dup alpha")
    t2 = commit(d, {"LOG.md": ["tail one", "kept two"]}, "delete both dup lines")
    led = write_ledger("led-f4a.tsv", [f"{'?'*0}{t2}\tLOG.md\t{key}\t1\tremoval\t",
                                       f"{t2}\tLOG.md\t{key}\t1\tremoval\t"])
    code, res, err = run_tool(d, t2, os.path.join(S, "contract.tsv"), led)
    report("F4a dup ledger rows sum (2 unheld)", code, res, err)
    d2 = mkrepo("f4b")
    commit(d2, {"N.md": NMD, "SRC.md":
                ["| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
                 "|---|---|---|---|---|---|---|---|---|---|---|",
                 "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"],
                "LOG.md": log})
    t2b = commit(d2, {"LOG.md": ["dup alpha", "kept two"]}, "delete one dup line")
    led_b = write_ledger("led-f4b.tsv", [f"{t2b}\tLOG.md\t{key}\t1\tremoval\tx",
                                         f"{t2b}\tLOG.md\t{key}\t1\tremoval\tx"])
    code, res, err = run_tool(d2, t2b, os.path.join(S, "contract.tsv"), led_b)
    report("F4b dup ledger rows over-count", code, res, err)
    if res:
        print(f"[F4b] disclosure verdicts={[(d['line_sha256'][:8], d['ok'], d['reason']) for d in res['disclosures']]}")


# ---------------------------------------------------------------- F7 ledger/exit-code edges
def f7():
    d = mkrepo("f7")
    log = ["alpha one", "beta two"]
    commit(d, {"N.md": NMD, "SRC.md":
               ["| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
                "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"],
               "LOG.md": log})
    t2 = commit(d, {"LOG.md": ["beta two"]}, "delete one line")
    # malformed: 5 fields (note column missing)
    led = os.path.join(S, "led-f7-5f.tsv")
    with open(led, "w") as fh:
        fh.write(DHEADER + f"\n{t2}\tLOG.md\t{sha('alpha one')}\t1\tremoval\n")
    code, res, err = run_tool(d, t2, os.path.join(S, "contract.tsv"), led)
    print(f"[F7a 5-field row] exit={code} res={'yes' if res else 'no'} stderr={err[:160]!r}")
    # note carries a tab (7 fields)
    led = os.path.join(S, "led-f7-tab.tsv")
    with open(led, "w") as fh:
        fh.write(DHEADER + f"\n{t2}\tLOG.md\t{sha('alpha one')}\t1\tremoval\tnote\twith-tab\n")
    code, res, err = run_tool(d, t2, os.path.join(S, "contract.tsv"), led)
    print(f"[F7b note-with-tab] exit={code} res={'yes' if res else 'no'} stderr={err[:160]!r}")
    # empty class
    led = write_ledger("led-f7-class.tsv", [f"{t2}\tLOG.md\t{sha('alpha one')}\t1\t\tx"])
    code, res, err = run_tool(d, t2, os.path.join(S, "contract.tsv"), led)
    report("F7c empty class", code, res, err)
    if res:
        print(f"[F7c] verdicts={[(dd['ok'], dd['reason']) for dd in res['disclosures']]}")
    # unmatched pattern -> exit code?
    d2 = mkrepo("f7d")
    commit(d2, {"N.md": NMD, "LOG.md": ["alpha one"],
                "SRC.md": ["| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |",
                           "|---|---|---|---|---|---|---|---|---|---|---|",
                           "| S101 | doc 1 | docs | A | scope 1 | sec | lesson 1 | mined | 2026-09-01 | 60d | a.md |"]})
    t = commit(d2, {"LOG.md": ["alpha one", "beta two"]}, "append only")
    ct = os.path.join(S, "contract-f7d.tsv")
    with open(ct, "w") as fh:
        fh.write(NM_CONTRACT)
    code, res, err = run_tool(d2, t, ct)
    report("F7d unmatched-pattern exit", code, res, err)


if __name__ == "__main__":
    parser_view()
    f1()
    f2()
    f4()
    f7()
