#!/usr/bin/env python3
"""Round-24 offline oracle case: complete local marked store + `clone --shared`.

ONE case, one fixture store, three arms over identical content:

  control  plain full clone (own objects, nothing marked)   expected exit 1
  case-1   `git clone --shared` of the marked store          expected exit 1
  case-2   same shared clone, and the clone itself is marked expected exit 1

Fixture content (deterministic; fixed author/committer names, dates and
bytes, so every object id below is reproducible):

  store            one local repository, master branch
    A  author kama-shokunin  @1000  "round-1: work"   path f
    B  author kama-shokunin  @1100  "round-1: more"   path g
    R  author fleet          @2000  "round-1: report" path .ufo/reports/round-1/kama.md
                              (the report cites A only)

  the report's first-add cutoff is R's author time 2000, so A and B are both
  required lane commits; the report cites A only, so B is the one substantive
  defect (`landed-omitted`).

Expected result, identical in all three arms:

  exit 1 (failed), one defect: landed-omitted <sha of B>
  summary: reports=1 defects=1 uncorrected=1 required=2 post_report=0
           by_kind {landed-omitted: 1}

Why the marked arms are *entitled* to that verdict: the store holds every
object the audit needs (proved by enumeration, not by metadata), so the
shared clones can resolve the cited commit A, the omitted commit B and the
report blob locally, through `objects/info/alternates`, with zero missing
objects. A promisor declaration is metadata; content completeness is the
evidence. The case fails if an arm answers exit 2 "could-not-evaluate" on
the strength of the marking alone, and equally if an arm answers exit 0:
the defect must be found.

Offline guarantees, checked by this script:

  * every path it creates is under its scratch root (no /tmp, no home);
  * the promisor remotes of the marked repos point at a nonexistent LOCAL
    path, so no transport (network or file) can ever succeed;
  * a `git` shim on PATH records every git invocation the auditor makes:
    no fetch/ls-remote/upload-pack/pull/push/clone may appear;
  * no repository-configured program is run (no core.sshCommand, no filters).

Usage:
  case_alternates_complete.py --build --auditor PATH [--arm all|control|case-1|case-2]
                              [--policy after|before] [--json]

Exit: 0 every selected arm matched its expectation; 1 at least one did not;
2 could not evaluate (fixture premise failed, git or auditor unusable).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseAlternatesComplete/run")
REAL_GIT = shutil.which("git") or "/usr/bin/git"
REL = ".ufo/reports/round-1/kama.md"
LANE = "kama"
TIMEOUT = 60

# Deterministic object ids of the fixture (recomputed and asserted at build
# time; a mismatch means the fixture changed and the oracle must be re-derived).
EXPECTED_A = "db796f8b820bf3825c58832419138cdba23206a7"
EXPECTED_B = "ce743590588f9a15c068e2c3a3e4a1b6648fdf8f"
EXPECTED_R = "1940965bce034fac27efbdbeb7284f48d654324f"
EXPECTED_BLOB = "315f23b8fdb782eabb6e4cf8201d4f79fc18b885"


class Premise(Exception):
    """The fixture did not establish what it claims: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, cwd=None, **extra):
    p = subprocess.run([REAL_GIT, "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra),
                       cwd=str(cwd) if cwd else None)
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    git(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return git(repo, "rev-parse", "HEAD")


def report_text(a_sha):
    """The fleet report: cites A only; B is the omission."""
    return ("# kama round 1\n"
            "\n"
            "## Work performed\n"
            "\n"
            "Round-1 fixture: two local lane commits, one cited below.\n"
            "\n"
            "## Landed changes\n"
            "\n"
            f"- {a_sha} round-1: work\n")


def build_store(root):
    store = root / "store"
    subprocess.run([REAL_GIT, "init", "-q", "-b", "master", str(store)],
                   check=True, capture_output=True, env=env())
    a = commit(store, "kama-shokunin", 1000, "round-1: work", "f",
               b"round-1: work\n")
    b = commit(store, "kama-shokunin", 1100, "round-1: more", "g",
               b"round-1: more\n")
    r = commit(store, "fleet", 2000, "round-1: report", REL,
               report_text(a).encode())
    return store, a, b, r


def mark_promisor(repo, url):
    """Declare the repo a promisor clone: config only, no promisor pack.

    The remote URL is a nonexistent LOCAL path: even if some git invocation
    tried to use it, no transport could succeed and no network is reachable.
    """
    git(repo, "config", "core.repositoryformatversion", "1")
    git(repo, "config", "extensions.partialclone", "origin")
    git(repo, "config", "remote.origin.url", str(url))
    git(repo, "config", "remote.origin.promisor", "true")
    git(repo, "config", "remote.origin.partialclonefilter", "blob:none")


def build(root):
    """Materialise store, control clones and the two shared-clone arms."""
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    store, a, b, r = build_store(root)
    nowhere = root / "no-such-promisor-remote"
    mark_promisor(store, nowhere)

    arms = {}

    # control: plain full clone, own objects, nothing marked
    ctl_lane, ctl_fleet = root / "control-lane", root / "control-fleet"
    for dest in (ctl_lane, ctl_fleet):
        subprocess.run([REAL_GIT, "clone", "-q", "--no-hardlinks",
                        str(store), str(dest)],
                       check=True, capture_output=True, env=env())
    arms["control"] = (ctl_lane, ctl_fleet)

    # case-1: `git clone --shared` of the marked store; the clone itself
    # carries no promisor metadata (git does not inherit it: observed).
    c1_lane, c1_fleet = root / "case1-lane", root / "case1-fleet"
    for dest in (c1_lane, c1_fleet):
        subprocess.run([REAL_GIT, "clone", "-q", "--shared", str(store),
                        str(dest)], check=True, capture_output=True, env=env())
    arms["case-1"] = (c1_lane, c1_fleet)

    # case-2: same shared clones, additionally marked promisor themselves
    c2_lane, c2_fleet = root / "case2-lane", root / "case2-fleet"
    for dest in (c2_lane, c2_fleet):
        subprocess.run([REAL_GIT, "clone", "-q", "--shared", str(store),
                        str(dest)], check=True, capture_output=True, env=env())
        mark_promisor(dest, nowhere)
    arms["case-2"] = (c2_lane, c2_fleet)

    # diagnostic arm: the same shared clones with the declaration removed.
    # If this arm answers like the control and case-2 does not, then the
    # declaration alone is what moved the verdict.
    d_lane, d_fleet = root / "case2u-lane", root / "case2u-fleet"
    for dest in (d_lane, d_fleet):
        subprocess.run([REAL_GIT, "clone", "-q", "--shared", str(store),
                        str(dest)], check=True, capture_output=True, env=env())
        for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone"):
            git(dest, "config", "--unset", key, check=False)
    arms["case-2-unmarked"] = (d_lane, d_fleet)

    return arms, {"store": store, "A": a, "B": b, "R": r,
                  "nowhere": nowhere, "root": root}


# --------------------------------------------------------------------- premise

def premise(arms, info):
    """Every claim the expectation rests on, checked on content."""
    store, a, b, r = info["store"], info["A"], info["B"], info["R"]
    checks = {}

    # 0. the fixture is byte-deterministic: the object ids the oracle names
    #    are the ids this run produced
    checks["fixture_ids_deterministic"] = (a == EXPECTED_A
                                           and b == EXPECTED_B
                                           and r == EXPECTED_R)
    if not checks["fixture_ids_deterministic"]:
        raise Premise(f"fixture ids moved: A={a} B={b} R={r}")

    # 1. the store really holds every object, and every object it holds is
    #    reachable: nothing is missing from it.
    missing = [line for line in git(store, "rev-list", "--objects", "--all",
                                    "--missing=print").splitlines()
               if line.startswith("?")]
    checks["store_no_missing_objects"] = not missing
    if missing:
        raise Premise(f"store has missing objects: {missing[:3]}")

    # 2. every object the audit needs is physically in the store
    for name, oid in (("A", a), ("B", b), ("R", r)):
        kind = git(store, "cat-file", "-t", oid)
        checks[f"store_has_{name}"] = kind == "commit"
        if kind != "commit":
            raise Premise(f"store lacks commit {name} {oid}")
    blob = git(store, "rev-parse", f"{r}:{REL}")
    checks["store_has_report_blob"] = git(store, "cat-file", "-t", blob) \
        == "blob"
    checks["report_blob_id_deterministic"] = blob == EXPECTED_BLOB
    if blob != EXPECTED_BLOB:
        raise Premise(f"report blob id moved: {blob}")

    # 3. the report cites A and not B (the omission is real, not an artefact
    #    of a missing object)
    text = git(store, "show", f"{r}:{REL}")
    checks["report_cites_A"] = a in text
    checks["report_omits_B"] = b not in text
    if a not in text or b in text:
        raise Premise("fixture report does not cite A and omit B")

    # 4. every arm can resolve the required objects locally, through its own
    #    object store (own objects or alternates) and without any fetch
    for name, (lane, fleet) in arms.items():
        for role, repo in (("lane", lane), ("fleet", fleet)):
            for oid, want in ((a, "commit"), (b, "commit"), (blob, "blob")):
                got = git(repo, "--no-lazy-fetch", "cat-file", "-t", oid)
                if got != want:
                    raise Premise(f"{name}/{role}: {oid} resolves to {got!r}, "
                                  f"want {want!r}")
            checks[f"{name}_{role}_resolves_required_objects"] = True
            absent = git(repo, "rev-list", "--objects", "--all",
                         "--missing=print")
            if any(line.startswith("?") for line in absent.splitlines()):
                raise Premise(f"{name}/{role}: reachable object missing")
            checks[f"{name}_{role}_nothing_missing"] = True

    # 5. the shared arms really borrow: no own objects, an alternates file
    for name in ("case-1", "case-2"):
        lane, _ = arms[name]
        own = git(lane, "count-objects", "-v")
        counts = dict(line.split(": ") for line in own.splitlines()
                      if ": " in line)
        checks[f"{name}_borrows_not_copies"] = counts.get("count") == "0" \
            and counts.get("in-pack") == "0"
        alt = Path(lane, ".git/objects/info/alternates")
        checks[f"{name}_has_alternates"] = alt.is_file() \
            and str(info["store"]) in alt.read_text()
        if not checks[f"{name}_has_alternates"]:
            raise Premise(f"{name}: no alternates to the marked store")

    # 6. the marked repos name a promisor remote that cannot be reached
    for repo in [info["store"]] + [arms["case-2"][0], arms["case-2"][1]]:
        url = git(repo, "config", "--get", "remote.origin.url")
        if Path(url).exists():
            raise Premise(f"{repo}: promisor remote {url} exists")
        checks[f"{repo.name}_promisor_remote_unreachable"] = True

    # 6b. every arm resolves exactly the same object set: the arms differ in
    #     metadata and in where the bytes live, not in the content
    for role in (0, 1):
        base_set = git(arms["control"][role], "rev-list", "--objects", "--all")
        for name in ("case-1", "case-2"):
            got = git(arms[name][role], "rev-list", "--objects", "--all")
            checks[f"{name}_role{role}_same_objects_as_control"] = \
                got == base_set
            if got != base_set:
                raise Premise(f"{name} role{role}: object set differs from "
                              f"control")
    ctl = dict(line.split(": ") for line in
               git(arms["control"][0], "count-objects", "-v").splitlines()
               if ": " in line)
    checks["control_has_own_objects"] = (ctl.get("count") != "0"
                                          or ctl.get("in-pack") != "0")
    if not checks["control_has_own_objects"]:
        raise Premise("control arm does not hold its own objects")

    # 7. nothing was created outside the scratch root
    root = info["root"]
    outside = [p for p in root.rglob("*")
               if not str(p).startswith(str(root))]
    checks["all_paths_under_scratch"] = not outside
    if outside:
        raise Premise(f"fixture escaped the scratch root: {outside[:3]}")

    return checks


# ----------------------------------------------------------------------- audit

def write_shim(root, arm):
    """A `git` wrapper that records every invocation (transport proof)."""
    shim = root / "shim"
    shim.mkdir(parents=True, exist_ok=True)
    log = root / f"git-calls-{arm}.log"
    script = shim / "git"
    script.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> '{log}'\n"
        f"exec '{REAL_GIT}' \"$@\"\n")
    script.chmod(0o755)
    return shim, log


FORBIDDEN = ("fetch", "ls-remote", "upload-pack", "send-pack", "pull",
             "push", "clone", "remote get-url", "archive --remote",
             "submodule", "credential", "ssh ")


def run_auditor(auditor, lane, fleet, root, arm):
    shim, log = write_shim(root, arm)
    if log.exists():
        log.unlink()
    cmd = [sys.executable, str(auditor), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", LANE,
           "--rounds", "1", "--no-errata", "--json"]
    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{shim}{os.pathsep}{old_path}"
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT,
                              env=env())
    finally:
        os.environ["PATH"] = old_path
    calls = log.read_text().splitlines() if log.exists() else []
    return proc, calls


def observed(proc):
    rc = proc.returncode
    doc = None
    try:
        doc = json.loads(proc.stdout.decode())
    except (ValueError, UnicodeDecodeError):
        doc = None
    out = {"exit": rc, "stderr": proc.stderr.decode(errors="replace").strip(),
           "defects": [], "summary": {}}
    if doc:
        out["defects"] = sorted([d["kind"], d["token"]]
                                for res in doc.get("results", [])
                                for d in res.get("defects", []))
        s = doc.get("summary", {})
        res0 = (doc.get("results") or [{}])[0]
        out["summary"] = {k: s.get(k) for k in
                          ("reports", "defects", "uncorrected", "status")}
        out["summary"]["required"] = res0.get("required")
        out["summary"]["post_report"] = len(res0.get("post_report", []))
        out["summary"]["by_kind"] = s.get("by_kind")
    return out


def expectation(b_sha, policy):
    """The oracle. `after` is the invariant the round-24 repair must hold."""
    good = {"exit": 1, "defects": [["landed-omitted", b_sha]]}
    if policy == "before":
        # r23 base: a promisor declaration alone refuses the repository
        return {"control": good, "case-1": good,
                "case-2-unmarked": good,
                "case-2": {"exit": 2, "defects": []}}
    return {arm: dict(good) for arm in ("control", "case-1", "case-2-unmarked",
                                        "case-2")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", action="store_true",
                    help="materialise the fixture under the scratch root")
    ap.add_argument("--build-only", action="store_true",
                    help="build and check the premises, then stop")
    ap.add_argument("--auditor", required=True,
                    help="path to the report-landing-audit.py under test")
    ap.add_argument("--arm", default="all",
                    choices=["all", "control", "case-1", "case-2",
                             "case-2-unmarked"])
    ap.add_argument("--policy", default="after", choices=["after", "before"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = SCRATCH
    try:
        arms, info = build(root) if args.build else (None, None)
    except Premise as exc:
        print(f"could-not-evaluate: fixture build: {exc}", file=sys.stderr)
        return 2
    if args.build:
        checks = premise(arms, info)
        note = sys.stderr if args.json else sys.stdout
        print(f"fixture built under {root}", file=note)
        for key in sorted(checks):
            print(f"  premise {key}: {checks[key]}", file=note)
        if args.build_only:
            return 0

    if arms is None:
        raise SystemExit("--build is required in this script version")

    want = ["control", "case-1", "case-2", "case-2-unmarked"] \
        if args.arm == "all" else [args.arm]
    exp = expectation(info["B"], args.policy)
    results = {}
    failures = []
    for arm in want:
        lane, fleet = arms[arm]
        proc, calls = run_auditor(args.auditor, lane, fleet, root, arm)
        obs = observed(proc)
        transport = [c for c in calls
                     if any(f in c.split() for f in FORBIDDEN)]
        obs["git_calls"] = len(calls)
        obs["transport_calls"] = transport
        obs["call_log"] = str(root / f"git-calls-{arm}.log")
        obs["expected"] = exp[arm]
        ok = (obs["exit"] == exp[arm]["exit"]
              and obs["defects"] == sorted([list(d) for d in
                                            exp[arm]["defects"]])
              and not transport)
        obs["match"] = ok
        if not ok:
            failures.append(arm)
        results[arm] = obs

    doc = {"root": str(root), "A": info["A"], "B": info["B"],
           "policy": args.policy, "arms": results}
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for arm, obs in results.items():
            print(f"{arm}: exit={obs['exit']} expected={obs['expected']['exit']} "
                  f"defects={obs['defects']} "
                  f"expected_defects={obs['expected']['defects']} "
                  f"git_calls={obs['git_calls']} "
                  f"transport={obs['transport_calls']} "
                  f"match={obs['match']}")
            if obs["stderr"]:
                print(f"  stderr: {obs['stderr']}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
