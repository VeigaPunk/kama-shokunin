#!/usr/bin/env python3
"""CaseCrossRepoFound — offline oracle case for the round-24 promisor repair.

Not production code.  A candidate builder + evidence producer for the
round-24 promisor grid (`tests/report-audit/promisor-grid.py`, owner of the
adopting grid) and for the L1's own verification.

CASE UNDER SPECIFICATION
    The lane under audit is a promisor-marked partial clone: git's own
    `--filter=blob:limit=` clone, so the repository carries

      * `remote.origin.promisor = true`
      * `remote.origin.partialclonefilter = blob:limit=1024`
      * a paired `<pack>.promisor` marker next to `<pack>.pack`
      * `core.repositoryformatversion = 1`

    and the local object store is missing exactly one object: the cited
    source blob (>1024 bytes, filtered out by the clone).  The report
    cites that blob.  The very same blob is present in the FLEET's local
    object store (the fleet vendors the lane's source file byte for byte,
    so both sides have one blob OID).

    The audit must therefore resolve the citation from the fleet, and must
    not refuse the lane before it has looked at the fleet.

EXPECTED RESULT (fixed before any candidate implementation is consulted)
    The promisor-marked arm must produce the SAME substantive verdict as
    its otherwise identical FULL-clone twin:

        exit 0, no findings (by_kind all zero, defects [])

    The expectation is the twin's verdict, observed with the same binary in
    the same run; it is not a value copied from the implementation under
    test.  Exit 2 (could-not-evaluate) is the base's blanket refusal
    ("partial clone (promisor pack)") and is exactly the failure this
    case exists to catch.

    Base (r23, 0df800e) on this fixture: exit 2, stderr
    `could-not-evaluate: <lane>: partial clone (promisor pack)`.

DISCRIMINATION (what a wrong repair fails)
    (a) repair that keeps the up-front promisor refusal      -> exit 2 (wrong)
    (b) repair that resolves citations only inside the lane  -> exit 1
        `unresolved-full-hash` for the fleet-resident blob (wrong)
    (c) repair that treats any lane-side absence as unknown and
        exits 2 WITHOUT consulting the fleet                -> exit 2 (wrong)
    (d) repair that ignores promisor metadata and proves the
        absence from the lane alone                         -> exit 1
        `unresolved-full-hash` (wrong: absence in a promisor-backed
        repository is not evidence)

SAFETY
    * Everything is local and offline.  The only transport used is the
      local `file://` clone that creates the partial clone (git's own
      filter machinery needs it); no host is contacted, no credential or
      program is configured, nothing is executed.
    * The AUDIT itself must not fetch: `--no-lazy-fetch` is on every git
      call inside the auditor, and this script re-checks the lane's
      object inventory before and after the run (P8) and that the cited
      blob is still absent afterwards (P9).
    * All fixture paths are under the work directory the caller names.

USAGE
    python3 xrepo_found_case.py --workdir DIR [--auditor PATH] [--out JSON]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

AUDIT_REL = "tools/report-landing-audit.py"
FROZEN_COMMIT = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
REL = ".ufo/reports/round-1/kama.md"
LANE = "kama"
BIG = ("cross-repo token evidence\n" + "x" * 4096 + "\n")
SMALL_LIMIT = 1024          # clone filter: blobs larger than this are absent
TIMEOUT = 60


class Premise(Exception):
    """The fixture did not establish its premise: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       input=data, capture_output=True, env=env(**extra),
                       timeout=TIMEOUT)
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def require(cond, what):
    if not cond:
        raise Premise(what)


def init(path):
    subprocess.run(["git", "init", "-q", "-b", "master", str(path)], check=True,
                   capture_output=True, env=env())
    return path


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        content = content.encode()
    target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def build(work: Path):
    """Build the fixture; return the paths and the two cited tokens."""
    origin = init(work / "origin")
    g(origin, "config", "uploadpack.allowFilter", "true")
    lc = commit(origin, f"{LANE}-shokunin", 1000, "round-1: work",
                "notes.md", BIG)
    commit(origin, "fixture", 1100, "registry: errata",
           "registry/report-landing-errata.tsv", "")
    blob = g(origin, "rev-parse", f"{lc}:notes.md")

    # The lane: a genuine partial clone.  The promisor remote stays a
    # reachable local path so the fixture is a real partial clone, but the
    # auditor must never contact it (--no-lazy-fetch).
    lane = work / "lane"
    subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                    "--no-local", "--filter=blob:limit=%d" % SMALL_LIMIT,
                    "--no-checkout", f"file://{origin}", str(lane)],
                   check=True, capture_output=True, env=env())
    # The twin: the same upstream, complete.  It is the control that fixes
    # the expected verdict.
    twin = work / "twin"
    subprocess.run(["git", "-c", "protocol.file.allow=always", "clone", "-q",
                    "--no-local", f"file://{origin}", str(twin)],
                   check=True, capture_output=True, env=env())

    # The fleet: the report, and a byte-identical vendored copy of the
    # lane's source file, so the cited blob exists in the fleet's local
    # object store (same content => same blob OID).
    fleet = init(work / "fleet")
    fleet_commit = commit(fleet, "fleet", 1500, "round-1: evidence vendor",
                          "vendor/notes.md", BIG)
    report = (f"# {LANE} round 1\n\n"
              "The source blob below is vendored in the fleet; the lane copy\n"
              "is promisor-backed and has not fetched it.\n\n"
              f"blob {blob}\n\n"
              "## Landed changes\n\n"
              f"- {lc}\n"
              f"- {fleet_commit}\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report)
    return {"origin": origin, "lane": lane, "twin": twin, "fleet": fleet,
            "lc": lc, "blob": blob, "fleet_commit": fleet_commit,
            "report": report}


def promisor_keys(repo):
    out = g(repo, "config", "--null", "--list")
    keys = {}
    for entry in out.split("\0"):
        if not entry:
            continue
        key, _, value = entry.partition("\n")
        keys[key] = value
    return keys


def missing_objects(repo):
    out = g(repo, "rev-list", "--objects", "--all", "--missing=print")
    return sorted(l[1:] for l in out.splitlines() if l.startswith("?"))


def inventory(repo):
    """Object inventory of a repository; used to prove that no fetch
    happened during the audit."""
    objects = g(repo, "cat-file", "--batch-all-objects", "--batch-check")
    packs = sorted(p.name for p in Path(repo, ".git/objects/pack").glob("*"))
    return {"objects": sorted(objects.splitlines()), "packs": packs}


def premises(fx, work):
    lane, twin, fleet, origin = fx["lane"], fx["twin"], fx["fleet"], fx["origin"]
    blob, lc = fx["blob"], fx["lc"]
    prem = {}

    # P1 the lane is promisor-marked, with git's own metadata
    keys = promisor_keys(lane)
    prem["P1_remote_promisor"] = keys.get("remote.origin.promisor")
    prem["P1_partialclonefilter"] = keys.get("remote.origin.partialclonefilter")
    prem["P1_repositoryformatversion"] = keys.get("core.repositoryformatversion")
    prem["P1_promisor_packs"] = sorted(p.name for p in
                                       Path(lane, ".git/objects/pack")
                                       .glob("*.promisor"))
    prem["P1_pack_companion"] = all(
        (Path(lane, ".git/objects/pack", p.name.replace(".promisor", ".pack"))
         ).is_file() for p in Path(lane, ".git/objects/pack").glob("*.promisor"))
    require(prem["P1_remote_promisor"] == "true", "lane is not promisor-marked")
    require(prem["P1_partialclonefilter"], "lane has no partialclonefilter")
    require(prem["P1_promisor_packs"] and prem["P1_pack_companion"],
            "lane has no paired .promisor pack")

    # P2 the cited blob is absent from the lane's local object store
    prem["P2_missing_in_lane"] = missing_objects(lane)
    require(blob in prem["P2_missing_in_lane"],
            "cited blob is not absent from the lane")
    require(g(lane, "cat-file", "--batch-check", data=f"{blob}\n".encode())
            .endswith(" missing"), "lane still resolves the cited blob")

    # P3 the cited blob exists in the lane's promisor upstream: its
    # absence locally is "not fetched yet", not "never existed".
    prem["P3_upstream_type"] = g(origin, "cat-file", "-t", blob)
    require(prem["P3_upstream_type"] == "blob",
            "cited blob is not in the lane upstream")

    # P4 the cited blob is present in the fleet's local object store
    prem["P4_fleet_type"] = g(fleet, "cat-file", "-t", blob)
    prem["P4_fleet_size"] = g(fleet, "cat-file", "-s", blob)
    require(prem["P4_fleet_type"] == "blob",
            "cited blob is not present in the fleet")

    # P5 the lane is otherwise complete for this audit: the errata blob
    # is local, the tip tree is local, the lane is not shallow, has no
    # grafts and uses sha1.
    errata = g(lane, "rev-parse", "HEAD:registry/report-landing-errata.tsv")
    prem["P5_errata_local"] = errata
    require(g(lane, "cat-file", "-t", errata) == "blob",
            "the lane's errata blob is not local")
    prem["P5_is_shallow"] = g(lane, "rev-parse", "--is-shallow-repository")
    prem["P5_object_format"] = g(lane, "rev-parse", "--show-object-format")
    prem["P5_show_prefix"] = g(lane, "rev-parse", "--show-prefix")
    prem["P5_grafts"] = Path(lane, g(lane, "rev-parse", "--git-path",
                                      "info/grafts")).exists()
    require(prem["P5_is_shallow"] == "false", "lane is shallow")
    require(prem["P5_object_format"] == "sha1", "lane is not sha1")
    require(prem["P5_show_prefix"] == "", "lane is not a top-level repository")
    require(not prem["P5_grafts"], "lane has info/grafts")

    # P6 the fleet holds the report at HEAD
    prem["P6_report_in_head"] = lc in g(fleet, "show", f"HEAD:{REL}")
    prem["P6_report_cutoff"] = g(fleet, "log", "--diff-filter=A", "--format=%at",
                                 "--", REL).split()[-1]
    require(prem["P6_report_in_head"], "the fleet report is not at HEAD")
    require(prem["P6_report_cutoff"] == "2000", "unexpected report cutoff")

    # P7 the lane has the cited commit locally (commits are not filtered)
    prem["P7_lane_commit_type"] = g(lane, "cat-file", "-t", lc)
    require(prem["P7_lane_commit_type"] == "commit",
            "the lane commit is not local")

    # P13 the fleet-resident commit token: absent from the lane, present in
    # the fleet.  It is cited in the Landed section, so it is resolved
    # through the PEELED lookup (a bare name first, then `<token>^{commit}`),
    # i.e. the path whose bare recursion must not raise before the fleet is
    # read.
    fleet_commit = fx["fleet_commit"]
    prem["P13_fleet_commit"] = fleet_commit
    prem["P13_absent_in_lane"] = g(lane, "cat-file", "--batch-check",
                                    data=f"{fleet_commit}\n".encode())
    prem["P13_present_in_fleet"] = g(fleet, "cat-file", "-t", fleet_commit)
    require(prem["P13_absent_in_lane"].endswith(" missing"),
            "the fleet-resident commit is not absent from the lane")
    require(prem["P13_present_in_fleet"] == "commit",
            "the fleet-resident commit is not in the fleet")
    require(fleet_commit in g(fleet, "show", f"HEAD:{REL}"),
            "the fleet-resident commit is not cited in the report")

    # P8 the twin is complete: nothing missing
    prem["P8_twin_missing"] = missing_objects(twin)
    require(not prem["P8_twin_missing"], "the twin is not complete")

    prem["P9_before_inventory"] = inventory(lane)
    prem["P10_twin_inventory"] = inventory(twin)
    return prem


def run_auditor(auditor, lane, fleet, work):
    argv = [sys.executable, str(auditor),
            "--lane-repo", str(lane), "--fleet-repo", str(fleet),
            "--branch", "master", "--lane", LANE, "--rounds", "1", "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), timeout=TIMEOUT)
    out = p.stdout.decode(errors="replace")
    err = p.stderr.decode(errors="replace")
    doc = None
    try:
        doc = json.loads(out)
    except json.JSONDecodeError:
        pass
    kinds = []
    if doc:
        for res in doc.get("results", []):
            kinds.extend(d["kind"] for d in res.get("defects", []))
    return {"argv": argv, "exit": p.returncode, "stdout": out, "stderr": err,
            "doc": doc, "kinds": sorted(kinds)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workdir", required=True,
                    help="scratch directory that will hold the fixture")
    ap.add_argument("--auditor", help="auditor to run (default: the base "
                                      "tool extracted from the lane git)")
    ap.add_argument("--lane-repo", default=None,
                    help="lane repository holding the auditor (default: the "
                         "repository this script lives under)")
    ap.add_argument("--out", help="write the evidence JSON here")
    args = ap.parse_args(argv)

    work = Path(args.workdir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    lane_repo = Path(args.lane_repo).resolve() if args.lane_repo else None
    if lane_repo is None:
        lane_repo = Path(__file__).resolve().parents[6]

    auditor = Path(args.auditor).resolve() if args.auditor else \
        (work / "auditor-base.py")
    if not args.auditor:
        blob = subprocess.run(["git", "-C", str(lane_repo), "cat-file", "blob",
                               f"{FROZEN_COMMIT}:{AUDIT_REL}"],
                              capture_output=True, env=env(), check=True).stdout
        auditor.write_bytes(blob)

    fx = build(work)
    prem = premises(fx, work)

    lane_run = run_auditor(auditor, fx["lane"], fx["fleet"], work)
    twin_run = run_auditor(auditor, fx["twin"], fx["fleet"], work)

    # after the audit: no fetch happened, the blob is still absent
    after = inventory(fx["lane"])
    prem["P11_after_inventory"] = after
    prem["P11_no_fetch"] = after == prem["P9_before_inventory"]
    prem["P12_blob_still_absent"] = blob_in(fx["lane"], fx["blob"])

    evidence = {
        "case": "CaseCrossRepoFound",
        "workdir": str(work),
        "auditor": str(auditor),
        "frozen_commit": FROZEN_COMMIT,
        "tokens": {"lane_commit": fx["lc"], "cited_blob": fx["blob"],
                   "fleet_commit": fx["fleet_commit"]},
        "premises": prem,
        "lane_run": lane_run,
        "twin_run": twin_run,
        "expected": {
            "lane": {"exit": 0, "kinds": []},
            "twin": {"exit": 0, "kinds": []},
            "rule": "the promisor-marked lane must equal its full-clone twin; "
                    "exit 2 is the base's blanket refusal",
        },
        "observed": {
            "lane": {"exit": lane_run["exit"], "kinds": lane_run["kinds"],
                     "stderr": lane_run["stderr"].strip()},
            "twin": {"exit": twin_run["exit"], "kinds": twin_run["kinds"],
                     "stderr": twin_run["stderr"].strip()},
        },
    }
    text = json.dumps(evidence, indent=1, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def blob_in(repo, oid):
    out = g(repo, "cat-file", "--batch-check", data=f"{oid}\n".encode())
    return out.endswith(" missing")


if __name__ == "__main__":
    sys.exit(main())
