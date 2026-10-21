#!/usr/bin/env python3
"""Round-23 ExecLocaleArms out-of-grid probe (scratch; not part of the repo).

The grid runs the auditor only with --json, which keeps output ASCII via
json.dumps(ensure_ascii=True). Text mode prints errata tokens and corrections
verbatim, so an stdout encoding that cannot represent them turns the verdict
into the auditor's catch-all exit 2. This probe builds three fresh /tmp
fixtures (ASCII control, non-ASCII errata token, non-ASCII errata correction)
and runs each in text and JSON mode under the locale variants.

Usage: probe-errata-text-mode.py AUDIT_PY OUT_JSON
Fixture git: GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, explicit
identity at example.invalid, no network.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

AUDIT = Path(sys.argv[1])
OUT = Path(sys.argv[2])

FIX_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
FIX_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")

# name -> (variables set, variables removed), applied to the probe's own env
VARIANTS = {
    "baseline": ({}, ("LC_ALL", "PYTHONIOENCODING")),
    "LC_ALL=C": ({"LC_ALL": "C"}, ("PYTHONIOENCODING",)),
    "LANG=C.UTF-8": ({"LANG": "C.UTF-8"}, ("LC_ALL", "PYTHONIOENCODING")),
    "PYTHONIOENCODING=ascii": ({"PYTHONIOENCODING": "ascii"}, ("LC_ALL",)),
    "LC_ALL=C+PYTHONIOENCODING=ascii": ({"LC_ALL": "C", "PYTHONIOENCODING": "ascii"}, ()),
    "LANG=C.UTF-8+PYTHONIOENCODING=ascii": ({"LANG": "C.UTF-8", "PYTHONIOENCODING": "ascii"}, ("LC_ALL",)),
    "strict-C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0": (
        {"LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"},
        ("LANG", "PYTHONIOENCODING")),
}

FIXTURES = {
    "control-ascii-token": "1\tlanded-unresolved\tdeadbeef1\t{lc}\tev\n",
    "nonascii-token": "1\tlanded-unresolved\tcaf\u00e9\t{lc}\tev\n",
    "nonascii-correction": "1\tlanded-unresolved\tdeadbeef1\tcaf\u00e9\tev\n",
}


def git(repo, *args, env=FIX_ENV):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)
    if p.returncode:
        raise SystemExit(f"fixture git {' '.join(args)} failed: "
                         f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode("utf-8", errors="replace").strip()


def commit(repo, path, data, msg, when):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    git(repo, "add", "--", path)
    env = dict(FIX_ENV, GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg, env=env)
    return git(repo, "rev-parse", "HEAD")


def build(tmp, errata_template):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    for repo in (lane, fleet):
        repo.mkdir()
        git(repo, "init", "-q", "-b", "master")
    lc = commit(lane, "f", b"work\n", "round-1: work", 1000)
    commit(lane, "registry/report-landing-errata.tsv",
           errata_template.format(lc=lc).encode("utf-8"), "errata", 1600)
    report = f"# kama round 1\n\n## Landed changes\n\n- {lc}\n".encode()
    commit(fleet, ".ufo/reports/round-1/kama.md", report, "round-1: report", 2000)
    return lane, fleet


def run_auditor(lane, fleet, text_mode, sets, drops):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for k in drops:
        env.pop(k, None)
    env.update(sets)
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1"]
    if not text_mode:
        argv.append("--json")
    return subprocess.run(argv, capture_output=True, env=env, timeout=60,
                          cwd=str(lane.parent))


def record(p, text_mode):
    out = p.stdout.decode("utf-8", errors="replace")
    err = p.stderr.decode("utf-8", errors="replace")
    rec = {"rc": p.returncode,
           "traceback": "Traceback (most recent call last)" in err,
           "stdout": out.strip()[:400], "stderr": err.strip()[:300]}
    if not text_mode and p.returncode in (0, 1):
        s = json.loads(out)["summary"]
        rec["summary"] = {k: s[k] for k in ("uncorrected", "errata_unmatched",
                                            "errata_invalid", "status")}
    return rec


def main():
    root = Path(tempfile.mkdtemp(prefix="kama-r23-locale-probe-", dir="/tmp"))
    fixtures = {}
    for name, template in FIXTURES.items():
        Path(root, name).mkdir()
        fixtures[name] = build(Path(root, name), template)
    cells = []
    for name, (lane, fleet) in fixtures.items():
        for vname, (sets, drops) in VARIANTS.items():
            for text_mode in (True, False):
                p = run_auditor(lane, fleet, text_mode, sets, drops)
                cells.append({"fixture": name, "variant": vname,
                              "mode": "text" if text_mode else "json",
                              **record(p, text_mode)})
    doc = {"fixture_root": str(root), "auditor": str(AUDIT), "cells": cells}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    for c in cells:
        print(f"{c['fixture']:20s} {c['mode']:4s} rc={c['rc']} traceback={int(c['traceback'])} {c['variant']}")
    print("fixture_root", root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
