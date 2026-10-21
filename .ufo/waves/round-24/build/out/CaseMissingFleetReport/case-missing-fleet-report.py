#!/usr/bin/env python3
"""CaseMissingFleetReport — offline oracle case for the round-24 promisor repair.

Subject: the *fleet report blob* (the committed bytes of
`.ufo/reports/round-1/kama.md`) is committed at fleet HEAD but its blob is
absent from the local object store of a partial (promisor) clone.

Expected outcome (post-repair), fixed before any candidate implementation:

  exit 2 (could-not-evaluate) — the required evidence is unavailable
  stdout: no findings at all (no "defects", no "landed-section-missing")
  stderr: "could-not-evaluate: ..." naming the unavailable required object
  the report blob is STILL absent afterwards (no lazy fetch)
  no traceback, bounded runtime

Forbidden outcomes (the harm this case pins):
  exit 1 + "landed-section-missing"  (missing blob read as an empty report)
  exit 1 + "landed-omitted"          (uncited lane commit derived from absence)
  exit 0 "clean"                     (round silently skipped = guessed completeness)
  exit 2 whose reason names only promisor metadata (base's blanket refusal)

Fixture construction (all local, offline, no network, no executed payload):
  * lane repo: one complete commit "round-1: work" by kama-shokunin
  * fleet origin repo: complete, commits the report citing that lane commit
  * fleet partial clone: `clone --filter=blob:none --no-local file://origin`
    -> promisor metadata present, report blob absent locally, trees/commits
    present.  The promisor remote stays a reachable local origin, so a lazy
    fetch would MATERIALIZE the blob and be detected afterwards.

Usage:
  case-missing-fleet-report.py --work DIR [--auditor PATH] [--json]

Exit: 0 every premise and every expectation of the audited arm held;
1 at least one did not; 2 the fixture premise itself could not be established.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 30
AUDIT_TIMEOUT = 60

# ---------------------------------------------------------------- expectations
EXPECTED = {
    "exit": 2,
    "stdout_has_findings": False,
    "stderr_prefix": "could-not-evaluate:",
    "forbidden_stdout_substrings": [
        "landed-section-missing", "landed-omitted", "unresolved-full-hash",
        "landed-unresolved", "landed-ambiguous", "unresolved-full-hash",
    ],
    "forbidden_stderr_substrings": [
        "landed-section-missing", "landed-omitted", "unresolved-full-hash",
    ],
    "stderr_must_mention_unavailable_object": [
        REL, "missing", "unavailable", "not available", "cannot read",
    ],
    "no_traceback": True,
    "blob_still_absent_after_run": True,
    "no_lazy_fetch": True,
}

# Exit 2 whose stderr names only promisor metadata is the base's blanket
# refusal: it is a *different* reason and must be reported as such.
METADATA_ONLY_REASONS = ("partial clone (extensions.partialclone)",
                          "partial clone (remote.",
                          "partial clone (promisor pack)")


class Premise(Exception):
    """The fixture did not establish its premise: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def git_global(repo, *args, check=True):
    """git with the audit's global isolation flags (no lazy fetch)."""
    p = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                        "-C", str(repo), *args], capture_output=True,
                       env=env())
    if check and p.returncode:
        raise Premise(f"git --no-lazy-fetch {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def build(work: Path):
    """Lane complete, fleet origin complete, fleet partial clone blobless."""
    work.mkdir(parents=True, exist_ok=True)
    lane, origin = work / "lane", work / "fleet-origin"
    for repo in (lane, origin):
        repo.mkdir(exist_ok=True)
        g(repo.parent, "init", "-q", "-b", "master", str(repo))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                b"lane work\n")
    report = ("# kama round 1\n\n## Work performed\n\nmeasured\n\n"
              "## Landed changes\n\n- `" + lc + "` work\n").encode()
    commit(origin, "fleet", 2000, "round-1: kama report", REL, report)
    blob = g(origin, "rev-parse", f"HEAD:{REL}")
    g(origin, "config", "uploadpack.allowFilter", "true")
    partial = work / "fleet-partial"
    subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                    "--no-checkout", "--filter=blob:none", "--no-local",
                    f"file://{origin}", str(partial)], capture_output=True,
                   env=env(), check=True)
    return {"lane": lane, "origin": origin, "partial": partial,
            "lane_commit": lc, "report_blob": blob, "report": report}


def premises(fx):
    """Every fact the expectation depends on, each re-verified locally."""
    out = {}
    lane, origin, partial = fx["lane"], fx["origin"], fx["partial"]
    # P1 the report blob is absent from the partial clone, and stays absent
    p = git_global(partial, "cat-file", "-e", fx["report_blob"], check=False)
    out["P1_blob_absent_locally"] = p.returncode != 0
    out["P1_stderr"] = p.stderr.decode(errors="replace").strip()[:200]
    # P2 the same blob IS present in the origin (the fixture, not the data)
    p2 = git_global(origin, "cat-file", "-e", fx["report_blob"], check=False)
    out["P2_blob_present_in_origin"] = p2.returncode == 0
    # P3 the report path is committed at the partial clone's HEAD
    rev = git_global(partial, "rev-parse", f"HEAD:{REL}", check=False)
    out["P3_path_committed_at_head"] = (rev.returncode == 0
                                         and rev.stdout.decode().strip()
                                         == fx["report_blob"])
    # P4 commits and trees are local; only the blob is missing
    out["P4_commit_local"] = git_global(partial, "cat-file", "-e",
                                        "HEAD^{commit}", check=False
                                        ).returncode == 0
    ls = git_global(partial, "ls-tree", "-r", "--name-only", "HEAD", "--",
                    ".ufo/reports", check=False)
    out["P4_tree_listing_local"] = (ls.returncode == 0
                                    and REL in ls.stdout.decode())
    # P5 promisor metadata is present (partial clone, promisor remote)
    out["P5_extensions_partialclone"] = g(partial, "config", "--get",
                                          "extensions.partialclone",
                                          check=False)
    out["P5_remote_promisor"] = g(partial, "config", "--get",
                                  "remote.origin.promisor", check=False)
    out["P5_promisor_packs"] = sorted(p.name for p in
                                       (partial / ".git/objects/pack").glob(
                                           "*.promisor"))
    out["P5_promisor_pack_companion"] = sorted(
        p.with_suffix(".pack").name for p in
        (partial / ".git/objects/pack").glob("*.promisor")
        if p.with_suffix(".pack").exists())
    out["P5_remote_url"] = g(partial, "config", "--get", "remote.origin.url",
                             check=False)
    # P6 the same content audits clean when the blob is available
    out["P6_control"] = run_auditor(AUDITORS[0], lane, origin)
    # P7 the partial clone is not shallow and is a top-level repository
    out["P7_shallow"] = g(partial, "rev-parse", "--is-shallow-repository")
    out["P7_prefix"] = g(partial, "rev-parse", "--show-prefix")
    return out


AUDITORS = [None]


def run_auditor(auditor, lane, fleet, rounds="1", cwd=None):
    """Run the auditor as its own process group; return exit/stdout/stderr."""
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", rounds, "--no-errata",
            "--json"]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(),
                            cwd=str(cwd or lane.parent),
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=AUDIT_TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        code, timed_out = None, True
    text_out = out.decode(errors="replace")
    text_err = err.decode(errors="replace")
    kinds = None
    if code in (0, 1):
        try:
            doc = json.loads(text_out)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    return {"exit": code, "timed_out": timed_out, "kinds": kinds,
            "stdout": text_out, "stderr": text_err,
            "traceback": "Traceback (most recent call last)" in text_err}


def judge(arm, blob_absent_after):
    """Apply EXPECTED to one auditor arm."""
    checks = {}
    checks["exit_is_2"] = arm["exit"] == EXPECTED["exit"]
    checks["no_timeout"] = not arm["timed_out"]
    checks["no_traceback"] = not arm["traceback"]
    checks["stderr_is_cne"] = arm["stderr"].startswith(
        EXPECTED["stderr_prefix"])
    checks["stdout_has_no_findings"] = (
        arm["stdout"].strip() == "" if arm["exit"] == 2
        else arm["kinds"] == [])
    checks["no_forbidden_finding_strings"] = not any(
        s in arm["stdout"] or s in arm["stderr"]
        for s in EXPECTED["forbidden_stdout_substrings"]
        + EXPECTED["forbidden_stderr_substrings"])
    checks["names_unavailable_object"] = any(
        s in arm["stderr"] for s in
        EXPECTED["stderr_must_mention_unavailable_object"])
    checks["not_metadata_only_reason"] = not any(
        r in arm["stderr"] for r in METADATA_ONLY_REASONS)
    checks["blob_still_absent"] = blob_absent_after
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--auditor", action="append", default=[],
                    help="auditor path (repeatable); first is the control arm")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.auditor:
        print("case-missing-fleet-report: need at least one --auditor",
              file=sys.stderr)
        return 2
    AUDITORS[:] = [str(Path(a).resolve()) for a in args.auditor]
    work = Path(args.work).resolve()
    try:
        fx = build(work)
        prem = premises(fx)
    except Premise as exc:
        print(json.dumps({"premise_error": str(exc)}, indent=1))
        return 2
    required = ("P1_blob_absent_locally", "P2_blob_present_in_origin",
                "P3_path_committed_at_head", "P4_commit_local",
                "P4_tree_listing_local", "P5_remote_promisor")
    failed = [k for k in required if not prem[k]]
    if failed or not prem["P5_promisor_pack_companion"]:
        print(json.dumps({"premise_error": f"not established: {failed}",
                          "premises": prem}, indent=1))
        return 2
    control = prem["P6_control"]
    if control["exit"] != 0 or control["kinds"]:
        print(json.dumps({"premise_error": "control arm is not clean",
                          "control": control}, indent=1))
        return 2
    arms = {}
    for auditor in AUDITORS:
        res = run_auditor(auditor, fx["lane"], fx["partial"])
        still = git_global(fx["partial"], "cat-file", "-e", fx["report_blob"],
                           check=False).returncode != 0
        res["blob_absent_after_run"] = still
        res["checks"] = judge(res, still)
        res["all_checks_met"] = all(res["checks"].values())
        arms[auditor] = res
    doc = {"case": "CaseMissingFleetReport", "expected": EXPECTED,
           "premises": prem, "control": control, "arms": arms}
    print(json.dumps(doc, indent=1, sort_keys=True))
    ok = all(a["all_checks_met"] for a in arms.values())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
