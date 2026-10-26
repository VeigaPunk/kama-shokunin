#!/usr/bin/env python3
"""Round-44 freeze controls: score the do-nothing base and shortcut trees with
both frozen counters. Each control is a `git clone --shared` of the lane at the
frozen base under --scratch, committed there only (fixture identity, isolation
checked), scored, and removed. Receipts land beside this file.

  build_controls.py --lane <lane repo> --upstream <llama.cpp clone>
                    --fleet <fleet repo> --scratch <dir>
"""
import argparse
import os
import shutil
import subprocess
import sys

BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"
HERE = os.path.dirname(os.path.abspath(__file__))
C1 = "round44-release-recheck-audit.py"
C2 = "round44-verdict-ledger-audit.py"
REL = "d854d98bae598388ecea1ed84396587e5edc326d"


def sh(*a, cwd=None, check=True):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=check)


def clone(lane, scratch, name):
    d = os.path.join(scratch, name)
    shutil.rmtree(d, ignore_errors=True)
    sh("git", "clone", "-q", "--shared", "--no-checkout", lane, d)
    sh("git", "-C", d, "checkout", "-q", BASE)
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").stdout.strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise SystemExit(f"isolation check failed for {d}")
    return d


def commit(d, msg):
    sh("git", "-C", d, "add", "-A")
    sh("git", "-C", d, "-c", "user.name=r44-control", "-c", "user.email=r44-control@fixture.invalid",
       "commit", "-qm", msg, "--allow-empty")
    return sh("git", "-C", d, "rev-parse", "HEAD").stdout.strip()


def score(tools, d, tip, name, a):
    for tag, tool, extra in (("c1", C1, ["--upstream", a.upstream]), ("c2", C2, ["--fleet", a.fleet])):
        out = os.path.join(HERE, f"{name}.{tag}.out")
        p = sh(sys.executable, os.path.join(tools, tool), "--repo", d, "--tip", tip, *extra, "--out", out,
               check=False)
        with open(out, "a") as fh:
            fh.write(f"exit={p.returncode}\n")
        print(name, tag, p.stdout.splitlines()[1] if len(p.stdout.splitlines()) > 1 else p.stderr.strip(),
              f"exit={p.returncode}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--fleet", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    tools = os.path.join(a.lane, "tools")
    os.makedirs(a.scratch, exist_ok=True)

    # base: the do-nothing tree
    d = clone(a.lane, a.scratch, "base")
    score(tools, d, BASE, "base", a)

    # junk-c1-allunchanged: every population row claims an unchanged file
    d = clone(a.lane, a.scratch, "junk-c1-allunchanged")
    draft = sh(sys.executable, os.path.join(tools, "release-recheck.py"), "draft", "--sources",
               os.path.join(d, "corpus/SOURCES.md"), "--upstream", a.upstream, "--release-name", "b11889",
               "--release-commit", REL).stdout.splitlines()
    rows = [draft[0]]
    for x in draft[1:]:
        f = x.split("\t")
        lines = f[7] if f[7] != "-" else "1-3"
        f[5], f[6], f[8], f[9], f[10] = f[4], "0", lines, "unchanged-file", "shortcut control"
        f[7] = lines
        rows.append("\t".join(f))
    os.makedirs(os.path.join(d, "registry"), exist_ok=True)
    open(os.path.join(d, "registry/release-recheck-b11889.tsv"), "w").write("\n".join(rows) + "\n")
    open(os.path.join(d, "corpus/SOURCES.md"), "a").write("\n## Round-44 release re-verification (control)\n\nnone\n")
    score(tools, d, commit(d, "junk-c1-allunchanged"), "junk-c1-allunchanged", a)

    # junk-c1-draftonly: the mechanical draft as is (TODO rows left), no SOURCES section, no flags
    d = clone(a.lane, a.scratch, "junk-c1-draftonly")
    open(os.path.join(d, "registry/release-recheck-b11889.tsv"), "w").write("\n".join(draft) + "\n")
    score(tools, d, commit(d, "junk-c1-draftonly"), "junk-c1-draftonly", a)

    # junk-c2-allimproved: 204 rows, every verdict improved on line 1
    d = clone(a.lane, a.scratch, "junk-c2-allimproved")
    out = ["\t".join(["round", "trend", "side", "verdict", "repo", "rev", "path", "line", "note"])]
    for r in range(10, 44):
        for t in ("expansion", "quality", "discernment"):
            out.append("\t".join([str(r), t, "self", "improved", "fleet", "b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025",
                                  f".ufo/reports/round-{r}/kama.md", "1", "control"]))
            out.append("\t".join([str(r), t, "outside", "improved", "lane", BASE,
                                  f"corpus/lessons/round-{r}-verifier-spotcheck.md", "1", "control"]))
    open(os.path.join(d, "registry/verdict-ledger.tsv"), "w").write("\n".join(out) + "\n")
    score(tools, d, commit(d, "junk-c2-allimproved"), "junk-c2-allimproved", a)

    # junk-c2-noscorecard: an automatic last-hit ledger, no SCORECARD section, no axes cite
    sys.path.insert(0, tools)
    import importlib.util
    spec = importlib.util.spec_from_file_location("c2", os.path.join(tools, C2))
    c2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c2)
    d = clone(a.lane, a.scratch, "junk-c2-noscorecard")
    out = [out[0]]
    for r in range(10, 44):
        for side in ("self", "outside"):
            repo, rev, path = c2.side_spec(r, side)
            p = sh("git", "-C", a.fleet if repo == "fleet" else d, "show", f"{rev}:{path}", check=False)
            text = p.stdout.splitlines() if p.returncode == 0 else None
            for t in ("expansion", "quality", "discernment"):
                hits = [] if text is None else [(i + 1, c2.read_line(x)[t]) for i, x in enumerate(text)
                                                if t in c2.read_line(x)]
                if not hits:
                    out.append("\t".join([str(r), t, side, "absent", repo, rev, path, "-",
                                          "automatic control: no line gives this trend a verdict"]))
                    continue
                ln, vs = hits[-1]
                v = sorted(vs)[0] if len(vs) == 1 else "mixed"
                out.append("\t".join([str(r), t, side, v, repo, rev, path, str(ln), "automatic"]))
    open(os.path.join(d, "registry/verdict-ledger.tsv"), "w").write("\n".join(out) + "\n")
    score(tools, d, commit(d, "junk-c2-noscorecard"), "junk-c2-noscorecard", a)

    for n in ("base", "junk-c1-allunchanged", "junk-c1-draftonly", "junk-c2-allimproved", "junk-c2-noscorecard"):
        shutil.rmtree(os.path.join(a.scratch, n), ignore_errors=True)


if __name__ == "__main__":
    main()
