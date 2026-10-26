#!/usr/bin/env python3
"""build_controls.py - round-43 freeze-time controls (do-nothing and shortcut edits).

Each control is a throwaway CLONE of the lane clone at the base commit, edited and
committed there (every git call names -C <dir>; the toplevel is verified equal to
the directory before the first commit), then scored by the three frozen counters
with the counters taken from the freeze tree. Receipts land in --out.

    build_controls.py --clone <lane clone> --base <full hash> --counters <dir with tools/> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ID = ["-c", "user.name=control", "-c", "user.email=control@invalid"]


def sh(*a, cwd=None, check=True):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, check=check)


def fresh(clone, base):
    d = tempfile.mkdtemp(prefix="r43ctl-")
    sh("git", "clone", "-q", "--no-hardlinks", clone, d)
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").stdout.strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise SystemExit("control clone toplevel mismatch")
    sh("git", "-C", d, "checkout", "-q", "--detach", base)
    return d


def commit(d):
    sh("git", "-C", d, "add", "-A")
    sh("git", "-C", d, *ID, "commit", "-qm", "control", "--allow-empty")
    return sh("git", "-C", d, "rev-parse", "HEAD").stdout.strip()


def wr(d, rel, text, mode="w"):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, mode).write(text)


def rd(d, rel):
    return open(os.path.join(d, rel)).read()


NEWSET_ROWS = [p for p in """round35-coverage-audit round35-statement-audit round36-coverage-audit round36-statement-audit
round37-coverage-audit round37-statement-audit round38-coverage-audit round38-operability-audit round38-statement-audit
round40-calibration-audit round40-operability-audit round41-pinwatch-audit round41-scorecard-reconcile
round42-capacity-audit round42-digest-audit round42-selfdesc-reconcile""".split()]


def skill_rows(flags):
    hdr = "\n| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |\n|---|---|---|---|---|\n"
    rows = "".join(f"| {n} | measurement: `python3 tools/{n}.py{flags}` | 0 ok; 1 not; 2 error | pinned x | read-only |\n"
                   for n in NEWSET_ROWS)
    return hdr + rows


def c1_sidefiles(d):
    sc = rd(d, "SCORECARD.md").replace("`28` (outside closures on record)", "`29` (outside closures on record)")
    wr(d, "SCORECARD.md", sc)
    rm = rd(d, "README.md") + "\nHidden entries: `.gitignore` and `.ufo`.\n"
    wr(d, "README.md", rm)
    so = rd(d, "corpus/SOURCES.md").split("\n")
    i = next(k for k, l in enumerate(so) if "round-42 K05 engine-side sources" in l)
    so.insert(i + 1, "\n- **2026-10-25 — correction to the round-42 entry above.** S401 and S424 were opened and re-checked in round 42.")
    wr(d, "corpus/SOURCES.md", "\n".join(so))


CONTROLS = {}


def control(name):
    def deco(f):
        CONTROLS[name] = f
        return f
    return deco


@control("base")
def _(d):
    pass


@control("junk-c1-fillerrows")
def _(d):
    wr(d, "SKILL.md", rd(d, "SKILL.md") + skill_rows(""))


@control("junk-c1-flagpaste")
def _(d):
    wr(d, "SKILL.md", rd(d, "SKILL.md") + skill_rows(" --repo R --tip T --out O"))


@control("junk-c1-sidefilesonly")
def _(d):
    c1_sidefiles(d)


@control("junk-c2-stub")
def _(d):
    wr(d, "tools/hexrun-census.py", "#!/usr/bin/env python3\nimport sys\nprint('tokens=0 distinct=0 lane_oid=0 md5_blob=0 upstream_ok=0 unverifiable=0 wrong_flagged=0 ledger_bad=0 unknown=0')\nsys.exit(0)\n")
    os.chmod(os.path.join(d, "tools/hexrun-census.py"), 0o755)
    sc = rd(d, "SCORECARD.md") + ("\n**Capabilities — canonical list as of round 43**\n\n| Capability | What it can now do | Evidence pointer | First-working round |\n"
                                  "|---|---|---|---|\n| hexrun-census | classify hex runs | `tools/hexrun-census.py` | 43 |\n")
    wr(d, "SCORECARD.md", sc)


@control("junk-c2-rowonly")
def _(d):
    sc = rd(d, "SCORECARD.md") + ("\n**Capabilities — canonical list as of round 43**\n\n| Capability | What it can now do | Evidence pointer | First-working round |\n"
                                  "|---|---|---|---|\n| hexrun-census | classify hex runs | `tools/hexrun-census.py` | 43 |\n")
    wr(d, "SCORECARD.md", sc)


def c3_rows(d, quote_in_copy):
    rel = {"REL": "release.json", "PR": "pr.json"}
    bodies = {"REL": "a `/health` endpoint (#58552) and more " + quote_in_copy,
              "PR": "Add an HTTP `/health` endpoint to the weight cache daemon parent process. distinguish daemon startup from readiness " + quote_in_copy}
    import hashlib
    rows = []
    for i, (k, url, kind, tier) in enumerate([
            ("REL", "https://github.com/vllm-project/vllm/releases/tag/v0.31.0", "docs", "A"),
            ("PR", "https://github.com/vllm-project/vllm/pull/58552", "community", "C")]):
        copy = f".ufo/waves/round-43/c3/{'vllm-v0.31.0-release.json' if k == 'REL' else 'vllm-pr-58552.json'}"
        data = json.dumps({"title": "t", "body": bodies[k]})
        wr(d, copy, data)
        sha = hashlib.sha256(data.encode()).hexdigest()
        rows.append(f"| S{480 + i} | control row {k} — {url} | {kind} | {tier} | scope | anchor {sha} | teaches | mined | 2026-10-25 | 90d | corpus/knowledge/runtime-health-surface-processes.md |")
    so = rd(d, "corpus/SOURCES.md").split("\n")
    j = max(k for k, l in enumerate(so) if re.match(r"^\|\s*S\d{3}\s*\|", l))
    for r in reversed(rows):
        so.insert(j + 1, r)
    wr(d, "corpus/SOURCES.md", "\n".join(so))
    return rows


@control("junk-c3-rowsonly")
def _(d):
    c3_rows(d, "")


@control("junk-c3-fabricated")
def _(d):
    fake = "the weight cache daemon is the inference server itself"
    c3_rows(d, fake)
    wr(d, "corpus/knowledge/runtime-health-surface-processes.md",
       "source: S480, S481\nverified-at: 2026-10-25\nrecheck: 90d\n\nThe weight cache daemon (vllm preload, #58552) reports starting, ready, failed; "
       "a different process from the inference server (S004).\n")
    wr(d, "corpus/README.md", rd(d, "corpus/README.md") + "\n- `corpus/knowledge/runtime-health-surface-processes.md` — process map.\n")
    les = ("# round 43\n\n## Gate\n\n"
           f"- S480 https://github.com/vllm-project/vllm/releases/tag/v0.31.0 2026-10-25 \"{fake}\"\n"
           f"- S481 https://github.com/vllm-project/vllm/pull/58552 2026-10-25 \"{fake}\"\n\n"
           "### Assimilation set\n\n| x | admit |\n| y | reject |\n")
    wr(d, "corpus/lessons/round-43.md", les)
    A = ".ufo/waves/round-43/assimilation"
    for f, t in (("reg-ids", "S001\n"), ("staged-ids", "S330\n"), ("collisions", ""), ("quarantine-slice", "S200 payload-absent\n")):
        wr(d, f"{A}/{f}", t)
    wr(d, f"{A}/guard/proof", "x\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--counters", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tools = {"c1": "round43-registry-audit.py", "c2": "round43-hexrun-audit.py", "c3": "round43-health-audit.py"}
    for name, fn in CONTROLS.items():
        if a.only and name not in a.only:
            continue
        d = fresh(a.clone, a.base)
        try:
            fn(d)
            tip = commit(d)
            for c, t in tools.items():
                cmd = [sys.executable, os.path.join(a.counters, "tools", t), "--repo", d, "--tip", tip]
                if c == "c2":
                    cmd += ["--seed", "43"]
                if c == "c3":
                    cmd += ["--base", a.base]
                p = subprocess.run(cmd, capture_output=True, text=True)
                text = p.stdout + p.stderr + f"exit={p.returncode}\n"
                open(os.path.join(a.out, f"{name}.{c}.out"), "w").write(text)
                first = [l for l in p.stdout.splitlines() if "met=" in l]
                print(name, c, p.returncode, first[0][:160] if first else p.stderr[:120])
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
