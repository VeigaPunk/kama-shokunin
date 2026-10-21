#!/usr/bin/env python3
"""Round-24 oracle case: a COMPLETE fleet repository marked as a promisor.

The case is a pair of otherwise identical fleet repositories:

  full      ordinary clone-equivalent fleet (no promisor configuration)
  promisor  the same bytes, plus promisor metadata
            (extensions.partialClone=origin, remote.origin.promisor=true,
             remote.origin.url=<a local path that does not exist>)

Both fleets are built from the same commits (identical commit ids, identical
trees, identical report bytes) and both are COMPLETE: every object reachable
from HEAD is present locally, verified offline with
`git rev-list --objects --all --missing=print` (no `?<oid>` line).

Oracle (fixed before any implementation):
  the promisor arm must return exactly what the full arm returns.
  The expected values are the FULL-CLONE arm's values, which the base
  auditor (0df800e, tools/report-landing-audit.py) already produces:

    exit            0
    findings        []            (no defect of any kind)
    cutoff          1200          (author time of the fleet commit that
                                   FIRST ADDED the report; the later report
                                   revision at 1400 must not move it)
    required        2             (lane commits authored <= the cutoff)
    post_report     [<late sha>]  (lane commit authored after the cutoff)
    summary.status  clean

  promisor arm at base (0df800e) instead exits 2 with
  "could-not-evaluate: ...: partial clone (extensions.partialclone)":
  the blanket refusal this round repairs.

The case pins the first-add cutoff: the fleet touches the report twice
(add at 1200, revise at 1400) and the lane holds a round-1 commit at 1300
that is NOT cited.  A correct first-add cutoff (1200) makes that lane
commit post_report (not required, clean); a last-touch cutoff (1400) would
make it required and turn the clean verdict into landed-omitted.  The clean
verdict therefore depends on the cutoff being the first add.

Offline only: no network transport, no core.sshCommand/gpg.program traps,
no executed repository program.  The promisor URL is a nonexistent LOCAL
path, so even an accidental fetch attempt is a local open() failure, never
a transport.

Usage:
  case_complete_fleet.py [--auditor PATH] [--scratch DIR] [--json]

Exit: 0 the oracle holds (promisor arm == full arm, both clean);
1 the oracle is violated (the arms differ) or a premise failed to hold;
2 could not evaluate (fixture premise, unusable auditor, timeout).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

CASE = "complete-fleet-promisor-config"
REL = ".ufo/reports/round-1/kama.md"
SCRATCH_DEFAULT = "/fast/scratch/hyaku/kama-r24/CaseCompleteFleet/fixture"
KAMA = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
TIMEOUT = 60

# ---- expected values, fixed before implementation (source: the full-clone
# ---- arm of the base auditor; see EXPECTED_SOURCE below)
FIRST_ADD = 1200        # author time of the fleet commit that added the report
REVISION = 1400         # author time of the later fleet report revision
LANE_TIMES = (1000, 1100, 1300)
EXPECTED = {
    "exit": 0,
    "findings": [],
    "cutoff": FIRST_ADD,
    "required": 2,
    "post_report_count": 1,
    "summary_status": "clean",
    "summary_defects": 0,
    "summary_uncorrected": 0,
    "summary_required_commits": 2,
    "summary_post_report_commits": 1,
}
EXPECTED_SOURCE = (
    "base auditor 0df800e tools/report-landing-audit.py, full-clone arm of "
    "this fixture (no promisor configuration); the promisor arm must equal "
    "it, field for field")


class Premise(Exception):
    """The fixture did not establish what the case claims: exit 2."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    path.mkdir(parents=True, exist_ok=True)
    g(path, "init", "-q", "-b", "master")
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


# ------------------------------------------------------------------ fixture

def build_lane(root, name):
    """Lane: two cited round-1 commits before the cutoff, one uncited round-1
    commit after it, and an empty errata registry (default errata path)."""
    lane = init(root / name)
    shas = {}
    shas["work"] = commit(lane, "kama-shokunin", LANE_TIMES[0],
                          "round-1: work")
    shas["measure"] = commit(lane, "kama-shokunin", LANE_TIMES[1],
                             "round-1: measure")
    shas["late"] = commit(lane, "kama-shokunin", LANE_TIMES[2],
                          "round-1: late advice")
    # author is not kama-shokunin: never a required round candidate
    commit(lane, "fixture", 1350, "fixture: empty errata registry",
           "registry/report-landing-errata.tsv", b"")
    return lane, shas


def report_text(shas):
    body = (
        "# kama round 1\n"
        "\n"
        "## Work performed\n"
        "\n"
        "Built the round-1 lane work and measured the result.\n"
        "\n"
        "## Landed changes\n"
        "\n"
        f"- `{shas['work']}` round-1: work\n"
        f"- `{shas['measure']}` round-1: measure\n")
    return body


def revision_text(shas):
    return report_text(shas) + (
        "\n"
        "## Notes\n"
        "\n"
        "The report body was revised after the first add; the first-add\n"
        "cutoff of the report must not move with it.\n")


def build_fleet(root, name, shas, promisor, add_at=FIRST_ADD,
                revise_at=REVISION):
    """Fleet: the report is first added at FIRST_ADD and revised at
    REVISION.  With promisor=True the repository additionally carries
    promisor metadata; the commit ids are identical either way because the
    metadata lives in .git/config, not in a commit.

    add_at=REVISION, revise_at=None builds the cutoff discriminator: the
    same report bytes, but first added at REVISION, so the cutoff is 1400
    and the uncited lane commit at 1300 becomes a required citation."""
    fleet = init(root / name)
    commit(fleet, "fleet", add_at, "round-1: kama report", REL,
           report_text(shas).encode())
    if revise_at is not None:
        commit(fleet, "fleet", revise_at, "round-1: kama report revision",
               REL, revision_text(shas).encode())
    if promisor:
        origin = root / "no-such-origin.git"      # never created, never fetched
        for key, value in (("remote.origin.url", str(origin)),
                           ("remote.origin.promisor", "true"),
                           ("remote.origin.partialclonefilter", "blob:none"),
                           ("extensions.partialclone", "origin")):
            g(fleet, "config", key, value)
    return fleet


def inventory(repo):
    """Everything an acquisition attempt would change."""
    git_dir = Path(g(repo, "rev-parse", "--absolute-git-dir"))
    objs = sorted(p.relative_to(git_dir).as_posix()
                   for p in git_dir.rglob("*") if p.is_file())
    refs = sorted(g(repo, "for-each-ref", "--format=%(refname) %(objectname)").splitlines())
    return {"head": g(repo, "rev-parse", "HEAD"),
            "objects": objs,
            "refs": refs,
            "count": g(repo, "count-objects", "-v").replace("\n", " ")}


def missing_objects(repo):
    out = g(repo, "rev-list", "--objects", "--all", "--missing=print")
    return [line for line in out.splitlines() if line.startswith("?")]


# ------------------------------------------------------------------ premises

def check_premises(full, promisor, lane_a, lane_b, shas):
    """Every property the oracle rests on, checked offline."""
    facts = {}

    # 1. the two fleets are the same repository content
    facts["fleet_head_equal"] = inventory(full)["head"] == inventory(promisor)["head"]
    if not facts["fleet_head_equal"]:
        raise Premise("fleet heads differ")
    facts["fleet_trees_equal"] = (
        g(full, "rev-parse", "HEAD^{tree}") == g(promisor, "rev-parse", "HEAD^{tree}"))

    # 2. both fleets are COMPLETE: no object is missing
    facts["full_missing_objects"] = missing_objects(full)
    facts["promisor_missing_objects"] = missing_objects(promisor)
    if facts["full_missing_objects"] or facts["promisor_missing_objects"]:
        raise Premise("fleet is not complete; the case claims completeness")

    # 3. the promisor arm really is promisor-marked
    facts["extensions_partialclone"] = g(promisor, "config",
                                         "--get", "extensions.partialclone")
    facts["remote_promisor"] = g(promisor, "config", "--get",
                                 "remote.origin.promisor")
    facts["full_extensions_partialclone"] = g(full, "config", "--get",
                                              "extensions.partialclone",
                                              check=False) or ""
    facts["full_remote_promisor"] = g(full, "config", "--get",
                                      "remote.origin.promisor",
                                      check=False) or ""
    if facts["extensions_partialclone"] != "origin" or \
            facts["remote_promisor"] != "true":
        raise Premise("promisor arm carries no promisor metadata")
    if facts["full_extensions_partialclone"] or facts["full_remote_promisor"]:
        raise Premise("full arm is promisor-marked")

    # 4. the promisor remote is a LOCAL path that does not exist: no
    #    transport can be attempted, ever
    origin = g(promisor, "config", "--get", "remote.origin.url")
    facts["promisor_url"] = origin
    if not origin.startswith("/") or Path(origin).exists():
        raise Premise("promisor url is not a nonexistent local path")

    # 5. no promisor pack file in either fleet (the case is about config
    #    metadata, not about a blobless clone)
    for name, repo in (("full", full), ("promisor", promisor)):
        packs = sorted(p.name for p in
                       Path(g(repo, "rev-parse", "--absolute-git-dir"),
                            "objects", "pack").glob("*.promisor"))
        facts[f"{name}_promisor_packs"] = packs
        if packs:
            raise Premise(f"{name} fleet carries a .promisor pack file")

    # 6. the report is touched twice: first add at FIRST_ADD, revision at
    #    REVISION.  A last-touch cutoff would be REVISION, not FIRST_ADD.
    adds = g(promisor, "log", "--diff-filter=A", "--format=%at", "--", REL).split()
    facts["report_add_times"] = adds
    facts["report_touch_times"] = g(promisor, "log", "--format=%at", "--", REL).split()
    if adds != [str(FIRST_ADD)]:
        raise Premise(f"report first add is not {FIRST_ADD}: {adds}")
    if sorted(facts["report_touch_times"]) != sorted([str(FIRST_ADD), str(REVISION)]):
        raise Premise("report is not touched twice")

    # 7. the lane round-1 candidates are what the case claims
    facts["lane_head"] = inventory(lane_a)["head"]
    facts["lane_copy_head"] = inventory(lane_b)["head"]
    if facts["lane_head"] != facts["lane_copy_head"]:
        raise Premise("lane copies differ")
    log = g(lane_a, "log", "--format=%at %an %s", "master").splitlines()
    facts["lane_log"] = log
    round_candidates = [line for line in log
                         if " kama-shokunin " in line
                         and line.split(" ", 2)[2].startswith("round-1:")]
    facts["round_candidates"] = round_candidates
    if len(round_candidates) != 3:
        raise Premise(f"expected 3 round-1 lane candidates: {round_candidates}")
    if not any(line.startswith(str(LANE_TIMES[2])) for line in round_candidates):
        raise Premise("no post-cutoff round-1 lane commit")

    # 8. the report cites exactly the two pre-cutoff lane commits
    text = g(promisor, "show", f"HEAD:{REL}")
    for key in ("work", "measure"):
        if shas[key] not in text:
            raise Premise(f"report does not cite {key}")
    if shas["late"] in text:
        raise Premise("report cites the post-cutoff lane commit")
    facts["report_cites"] = [shas["work"], shas["measure"]]
    return facts


# ------------------------------------------------------------------ the run

def run_auditor(auditor, lane, fleet, cwd):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json"]
    started = time.time()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env(), cwd=str(cwd),
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=TIMEOUT)
        code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        code, timed_out = None, True
    doc = None
    if code in (0, 1):
        try:
            doc = json.loads(out.decode())
        except ValueError:
            doc = None
    return {"argv": argv, "exit": code, "timed_out": timed_out,
            "seconds": round(time.time() - started, 3),
            "stdout": out.decode(errors="replace"),
            "stderr": err.decode(errors="replace"), "doc": doc}


# An auditor that contacted the promisor remote leaves these in git's
# output.  The promisor url of this fixture is a nonexistent LOCAL path, so
# a contact attempt cannot reach a network: it can only produce one of
# these messages.  Any of them is a transport attempt, which this case
# forbids.
TRANSPORT_MARKERS = (
    "does not appear to be a git repository",
    "Could not read from remote repository",
    "unable to access",
    "Connection refused",
    "Connection timed out",
    "ssh:",
    "fatal: unable to access",
    "promisor remote",
)


def transport_markers(text):
    return [m for m in TRANSPORT_MARKERS if m.lower() in text.lower()]


def summarize(run):
    """The comparable surface of one arm: exit, findings, cutoff, counts."""
    doc = run["doc"]
    if not doc or not doc.get("results"):
        return {"exit": run["exit"], "findings": None,
                "stderr_tail": run["stderr"].strip()[-300:],
                "timed_out": run["timed_out"]}
    res = doc["results"][0]
    findings = sorted((d["kind"], d["token"]) for d in res["defects"])
    return {"exit": run["exit"],
            "findings": findings,
            "cutoff": res["cutoff"],
            "required": res["required"],
            "post_report": res["post_report"],
            "report_committed": res["report_committed"],
            "round_commits": res["round_commits"],
            "summary_status": doc["summary"]["status"],
            "summary_defects": doc["summary"]["defects"],
            "summary_uncorrected": doc["summary"]["uncorrected"],
            "summary_required_commits": doc["summary"]["required_commits"],
            "summary_post_report_commits":
                doc["summary"]["post_report_commits"],
            "stderr_tail": run["stderr"].strip()[-300:],
            "timed_out": run["timed_out"]}


def kama_state():
    head = subprocess.run(["git", "-C", str(KAMA), "rev-parse", "HEAD"],
                          capture_output=True, env=env()).stdout.decode().strip()
    status = subprocess.run(["git", "-C", str(KAMA), "status", "--porcelain"],
                            capture_output=True, env=env()).stdout.decode()
    count = subprocess.run(["git", "-C", str(KAMA), "count-objects", "-v"],
                           capture_output=True, env=env()).stdout.decode()
    return {"head": head, "status": status, "count": count}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--auditor", required=True,
                    help="tools/report-landing-audit.py under test")
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    scratch = Path(args.scratch).resolve()
    auditor = Path(args.auditor).resolve()
    doc = {"case": CASE, "auditor": str(auditor),
           "auditor_sha256": hashlib.sha256(auditor.read_bytes()).hexdigest(),
           "scratch": str(scratch), "expectations": EXPECTED,
           "expectations_source": EXPECTED_SOURCE}

    if not str(scratch).startswith("/fast/scratch/"):
        print(f"could-not-evaluate: scratch {scratch} is not under "
              f"/fast/scratch/", file=sys.stderr)
        return 2
    if not auditor.is_file():
        print(f"could-not-evaluate: no auditor at {auditor}", file=sys.stderr)
        return 2

    before_kama = kama_state()
    scratch.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="case-", dir=str(scratch)))
    try:
        lane_a, shas = build_lane(root, "lane-full")
        lane_b = root / "lane-promisor"
        shutil.copytree(lane_a, lane_b, symlinks=True)
        full = build_fleet(root, "fleet-full", shas, promisor=False)
        promisor = build_fleet(root, "fleet-promisor", shas, promisor=True)
        # cutoff discriminator: same report bytes, first added at REVISION
        late = build_fleet(root, "fleet-late-add", shas, promisor=False,
                           add_at=REVISION, revise_at=None)
        facts = check_premises(full, promisor, lane_a, lane_b, shas)
        doc["premises"] = facts
        doc["lane_shas"] = shas

        inv_full_before = inventory(full)
        inv_promisor_before = inventory(promisor)
        inv_late_before = inventory(late)
        inv_lane_a_before = inventory(lane_a)
        inv_lane_b_before = inventory(lane_b)

        run_full = run_auditor(auditor, lane_a, full, root)
        run_promisor = run_auditor(auditor, lane_b, promisor, root)
        run_late = run_auditor(auditor, lane_a, late, root)
        doc["arms"] = {"full": summarize(run_full),
                       "promisor": summarize(run_promisor)}
        doc["arms"]["full"]["stdout"] = run_full["stdout"]
        doc["arms"]["promisor"]["stdout"] = run_promisor["stdout"]
        doc["arms"]["full"]["stderr"] = run_full["stderr"]
        doc["arms"]["promisor"]["stderr"] = run_promisor["stderr"]
        doc["arms"]["full"]["seconds"] = run_full["seconds"]
        doc["arms"]["promisor"]["seconds"] = run_promisor["seconds"]
        doc["discriminator"] = summarize(run_late)
        doc["discriminator"]["stderr"] = run_late["stderr"]
        doc["discriminator"]["seconds"] = run_late["seconds"]
        doc["discriminator"]["expectation"] = {
            "exit": 1, "findings": [["landed-omitted", shas["late"]]],
            "why": "the same lane and report bytes, first added at 1400: the "
                   "uncited lane commit at 1300 becomes a required citation, "
                   "so the clean verdict of the case is reachable only "
                   "through the correct first-add cutoff"}
        doc["transport_markers"] = {
            "full": transport_markers(run_full["stderr"]),
            "promisor": transport_markers(run_promisor["stderr"]),
            "discriminator": transport_markers(run_late["stderr"]),
        }

        # containment: no acquisition, no refs, no new objects, no writes
        doc["no_acquisition"] = {
            "fleet_full_unchanged": inventory(full) == inv_full_before,
            "fleet_promisor_unchanged": inventory(promisor) == inv_promisor_before,
            "fleet_late_unchanged": inventory(late) == inv_late_before,
            "lane_full_unchanged": inventory(lane_a) == inv_lane_a_before,
            "lane_promisor_unchanged": inventory(lane_b) == inv_lane_b_before,
        }
        doc["kama_repo_unchanged"] = kama_state() == before_kama
        doc["kama_before"] = before_kama
        doc["kama_after"] = kama_state()
        doc["fixture_root"] = str(root)
        doc["fixture_under_scratch"] = str(root).startswith("/fast/scratch/")
        doc["transport_attempted"] = any(doc["transport_markers"].values())

        # verdict
        a, b = doc["arms"]["full"], doc["arms"]["promisor"]
        comparable = ("exit", "findings", "cutoff", "required", "post_report",
                      "summary_status", "summary_defects",
                      "summary_uncorrected", "summary_required_commits",
                      "summary_post_report_commits")
        differences = [k for k in comparable if a.get(k) != b.get(k)]
        doc["arm_differences"] = differences
        full_matches_expectation = all(
            a.get(k) == v for k, v in EXPECTED.items()
            if k in ("exit", "cutoff", "required", "summary_status",
                     "summary_defects", "summary_uncorrected",
                     "summary_required_commits", "summary_post_report_commits")
        ) and a.get("findings") == EXPECTED["findings"] \
            and len(a.get("post_report") or []) == EXPECTED["post_report_count"]
        doc["full_arm_matches_expectation"] = full_matches_expectation
        doc["promisor_arm_matches_expectation"] = full_matches_expectation \
            and not differences
        disc = doc["discriminator"]
        doc["discriminator_matches_expectation"] = (
            disc.get("exit") == 1
            and disc.get("findings") == [("landed-omitted", shas["late"])])
        doc["fault_reproduced"] = (
            b.get("exit") == 2 and "partial clone" in b.get("stderr_tail", ""))
        doc["oracle_holds"] = bool(doc["promisor_arm_matches_expectation"])

        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        else:
            print(f"case {CASE}")
            print(f"expectations {json.dumps(EXPECTED, sort_keys=True)}")
            for arm in ("full", "promisor"):
                r = doc["arms"][arm]
                print(f"arm {arm}: exit={r.get('exit')} "
                      f"findings={r.get('findings')} cutoff={r.get('cutoff')} "
                      f"required={r.get('required')} "
                      f"post_report={r.get('post_report')} "
                      f"status={r.get('summary_status')} "
                      f"seconds={r.get('seconds')}")
                if r.get("stderr_tail"):
                    print(f"  stderr: {r['stderr_tail']}")
            print(f"discriminator: exit={disc.get('exit')} "
                  f"findings={disc.get('findings')} "
                  f"matches={doc['discriminator_matches_expectation']}")
            print(f"arm differences: {differences}")
            print(f"no acquisition: {doc['no_acquisition']}")
            print(f"transport markers: {doc['transport_markers']}")
            print(f"kama repo unchanged: {doc['kama_repo_unchanged']}")
            print(f"fault reproduced (base refusal): {doc['fault_reproduced']}")
            print(f"oracle holds: {doc['oracle_holds']}")
        if (not doc["kama_repo_unchanged"]
                or not all(doc["no_acquisition"].values())
                or not doc["fixture_under_scratch"]
                or doc["transport_attempted"]):
            return 2
        return 0 if doc["oracle_holds"] else 1
    except Premise as exc:
        doc["premise_failure"] = str(exc)
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # errors are never verdicts
        doc["error"] = f"{type(exc).__name__}: {exc}"
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
