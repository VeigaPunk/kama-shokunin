#!/usr/bin/env python3
"""Mutation sensitivity for the CaseCrossRepoFound oracle case.

Not production code.  Each mutant is a textual edit of the BASE auditor
(r23, 0df800e) applied to a COPY under the scratch directory; the copy is
run against the CaseCrossRepoFound fixture (promisor-marked lane, cited
blob absent from the lane and present in the fleet).

The case passes only for a repair that consults the fleet:

  M1  naive repair: the up-front promisor refusal is removed and nothing
      else changes.  Expected: exit 0, no findings (the case's twin).
  M2  lane-only resolution: the refusal is removed AND the citation
      lookup is restricted to the lane.  Expected: exit 1 with
      `unresolved-full-hash` for the fleet-resident blob -> the case
      catches a repair that stops consulting the fleet.
  M3  refuse before considering the fleet: the refusal is removed AND a
      lane-side miss in a promisor-backed repository raises EvalError
      before the fleet is consulted.  Expected: exit 2 -> the case catches
      a repair that gives up before the fleet.

The base itself (no edit) exits 2 with "partial clone (promisor pack)".
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent / "xrepo_found_case.py"


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def read(path):
    return Path(path).read_text(encoding="utf-8")


def m1_no_promisor_refusal(text):
    """Remove the up-front promisor refusal (pack marker + config keys)."""
    pack_block = """    for rel in ("info/grafts", "objects/pack"):
        path = Path(repo, git(repo, "rev-parse", "--git-path", rel).strip())
        if rel == "info/grafts" and grafts_effective(path):
            raise EvalError(f"{repo}: {path} rewrites history")
        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")
"""
    pack_new = """    for rel in ("info/grafts",):
        path = Path(repo, git(repo, "rev-parse", "--git-path", rel).strip())
        if rel == "info/grafts" and grafts_effective(path):
            raise EvalError(f"{repo}: {path} rewrites history")
"""
    cfg_block = """    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
"""
    assert pack_block in text, "pack block not found"
    assert cfg_block in text, "config block not found"
    return text.replace(pack_block, pack_new).replace(cfg_block, "")


def m2_lane_only_lookup(text):
    """Remove the refusal AND resolve citations in the lane only."""
    text = m1_no_promisor_refusal(text)
    old = "    repos = (lane_repo, fleet_repo)\n"
    assert old in text, "repos line not found"
    return text.replace(old, "    repos = (lane_repo,)\n")


def m3_refuse_before_fleet(text):
    """Remove the refusal AND give up on a lane-side miss before the
    fleet is consulted."""
    text = m1_no_promisor_refusal(text)
    old = """    for repo in repos:
        out = git(repo, "cat-file", "--batch-check",
"""
    new = """    for repo in repos:
        if repo == repos[0] and git_bool(git(repo, "config", "--get",
                                               "remote.origin.promisor",
                                               errors="surrogateescape")):
            out = git(repo, "cat-file", "--batch-check",
                      stdin="".join(f"{t}{peel}\\n" for t in tokens))
            for token, line in zip(tokens, out.split("\\n")[:len(tokens)]):
                if line.endswith(" missing"):
                    raise EvalError(f"{repo}: required object {token} is not "
                                    "available in a promisor-backed repository")
        out = git(repo, "cat-file", "--batch-check",
"""
    assert old in text, "lookup loop not found"
    return text.replace(old, new)


def m4_raise_inside_bare_recursion(text):
    """Remove the refusal AND raise inside the BARE recursion of the
    peeled lookup: the bare name is asked first, and a lane-side miss in a
    promisor-backed repository aborts the lookup before the fleet is
    consulted (tools/report-landing-audit.py:148-150, the recursive call at
    :149; the per-repository loop with the peeled names is at :152-153)."""
    text = m1_no_promisor_refusal(text)
    old = """    if peel:
        bare = lookup(repos, tokens)
"""
    new = """    if peel:
        if _promisor_backed(repos[0]):
            out0 = git(repos[0], "cat-file", "--batch-check",
                       stdin="".join(f"{t}\\n" for t in tokens))
            for token, line in zip(tokens, out0.split("\\n")[:len(tokens)]):
                if line.endswith(" missing"):
                    raise EvalError(f"{repos[0]}: required object {token} is "
                                    "not available in a promisor-backed "
                                    "repository")
        bare = lookup(repos, tokens)
"""
    assert old in text, "bare recursion not found"
    helper = '''
def _promisor_backed(repo):
    """True when the repository carries git's own promisor metadata."""
    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            return True
    return False


def lookup(repos, tokens, peel=""):'''
    assert "\ndef lookup(repos, tokens, peel=\"\"):" in text
    text = text.replace("\ndef lookup(repos, tokens, peel=\"\"):", helper, 1)
    return text.replace(old, new)


MUTANTS = {
    "M1-naive-no-refusal": (m1_no_promisor_refusal,
                            {"exit": 0, "kinds": []}),
    "M2-lane-only-lookup": (m2_lane_only_lookup,
                            {"exit": 1, "kinds": ["landed-unresolved",
                                                  "unresolved-full-hash"]}),
    "M3-refuse-before-fleet": (m3_refuse_before_fleet,
                                {"exit": 2, "kinds": []}),
    "M4-raise-in-bare-recursion": (m4_raise_inside_bare_recursion,
                                   {"exit": 2, "kinds": []}),
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--lane-repo", required=True)
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    work = Path(args.workdir).resolve()
    work.mkdir(parents=True, exist_ok=True)

    base = work / "auditor-base.py"
    subprocess.run([sys.executable, str(BASE), "--workdir", str(work),
                    "--lane-repo", args.lane_repo,
                    "--out", str(work / "evidence.json")],
                   check=True, capture_output=True, env=env())
    evidence = json.loads((work / "evidence.json").read_text())
    lane = evidence["workdir"] + "/lane"
    fleet = evidence["workdir"] + "/fleet"

    rows = []
    for name, (fn, expect) in MUTANTS.items():
        path = work / f"auditor-{name}.py"
        path.write_text(fn(read(base)), encoding="utf-8")
        p = subprocess.run([sys.executable, str(path), "--lane-repo", lane,
                            "--fleet-repo", fleet, "--branch", "master",
                            "--lane", "kama", "--rounds", "1", "--json"],
                           capture_output=True, env=env(), timeout=60)
        out = p.stdout.decode(errors="replace")
        kinds = []
        try:
            doc = json.loads(out)
            for res in doc.get("results", []):
                kinds.extend(d["kind"] for d in res.get("defects", []))
        except json.JSONDecodeError:
            pass
        rows.append({
            "mutant": name,
            "exit": p.returncode,
            "kinds": sorted(kinds),
            "stderr": p.stderr.decode(errors="replace").strip()[:300],
            "expected": expect,
            "matches_expectation": (p.returncode == expect["exit"]
                                    and sorted(kinds) == expect["kinds"]),
            "passes_the_case": (p.returncode == 0 and not kinds),
        })
    evidence["mutants"] = rows
    text = json.dumps(evidence, indent=1, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    for row in rows:
        print(row["mutant"], "exit", row["exit"], "kinds", row["kinds"],
              "| case-pass:", row["passes_the_case"], "|", row["stderr"][:90])
    return 0


if __name__ == "__main__":
    sys.exit(main())
