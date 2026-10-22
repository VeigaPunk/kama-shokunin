#!/usr/bin/env python3
"""Bounded, offline falsification probe for the audit tool's five-state
lookup ranking (found / ambiguous / unknown / wrongtype / absent).

No network, no promisor remote, no lazy fetch, no execution payload.
Every git probe runs with --no-lazy-fetch and an empty global/system config.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeStatusPriority")
WORK = ROOT / "work"
TOOL = ROOT / "tools" / "report-landing-audit.py"
BASE_TOOL = ROOT / "base" / "report-landing-audit.py"
os.environ["TMPDIR"] = str(ROOT)

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def g(repo, *args, stdin=None, check=True):
    proc = subprocess.run(
        ["git", "--no-lazy-fetch", "-C", str(repo), *args],
        input=None if stdin is None else stdin.encode(),
        capture_output=True, env=ENV, text=True)
    if check and proc.returncode != 0:
        raise SystemExit(f"git {args} in {repo}: rc={proc.returncode}\n"
                         f"{proc.stderr}")
    return proc.stdout


def init(repo):
    repo.mkdir(parents=True, exist_ok=True)
    g(repo, "init", "-q", "-b", "master")
    g(repo, "config", "user.name", "kama-shokunin")
    g(repo, "config", "user.email", "kama@shokunin.local")
    g(repo, "config", "commit.gpgsign", "false")
    return repo


def commit(repo, message, when, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    g(repo, "add", "--", path)
    env = dict(ENV)
    env.update(GIT_AUTHOR_DATE=f"@{when} +0000",
               GIT_COMMITTER_DATE=f"@{when} +0000")
    subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "commit", "-q",
                    "-m", message], capture_output=True, env=env, check=True)
    return g(repo, "rev-parse", "HEAD").strip()


def drop_object(repo, oid):
    """Remove one loose object so the repository cannot serve it (a hole)."""
    p = Path(repo, ".git", "objects", oid[:2], oid[2:])
    assert p.is_file(), p
    p.unlink()


def build_pair(base, lane_has_blob, fleet_has_blob, blob_text="notes\n"):
    """Two complete, non-promisor repositories.

    lane:  one commit on master: the cited round commit, plus an empty
           errata registry so the default errata path is exercised.
    fleet: one commit adding notes.md, whose blob is the wrong-type
           citation; plus the published report.
    The notes blob is identical on both sides when both hold it, so the
    40-hex citation names the same object either way.
    """
    lane = init(base / "lane")
    fleet = init(base / "fleet")
    lane_commit = commit(lane, "round-24: work", 1000, "f", "fixture file\n")
    commit(lane, "round-24: errata registry", 1050,
           "registry/report-landing-errata.tsv", "")
    fleet_commit = commit(fleet, "fleet: init", 1900, "notes.md", blob_text)
    blob = g(fleet, "rev-parse", f"{fleet_commit}:notes.md").strip()
    if lane_has_blob:
        commit(lane, "round-24: notes", 1100, "notes.md", blob_text)
    if not fleet_has_blob:
        drop_object(fleet, blob)
        g(fleet, "rm", "-q", "--cached", "notes.md")
    return lane, fleet, lane_commit, fleet_commit, blob


def build_tag_pair(base, lane_has_target, fleet_has_target):
    """lane and fleet both hold an annotated tag whose target is a blob;
    exactly one side cannot serve that blob."""
    lane = init(base / "lane")
    fleet = init(base / "fleet")
    lane_commit = commit(lane, "round-24: work", 1000, "f", "fixture file\n")
    commit(lane, "round-24: errata registry", 1050,
           "registry/report-landing-errata.tsv", "")
    blob = g(lane, "rev-parse", f"{lane_commit}:f").strip()
    g(lane, "tag", "-a", "v1", "-m", "annotated", blob)
    tag = g(lane, "rev-parse", "refs/tags/v1").strip()
    subprocess.run(["git", "--no-lazy-fetch", "-C", str(fleet), "fetch", "-q",
                    str(lane), "refs/tags/v1:refs/tags/v1"], check=True,
                   env=ENV, capture_output=True)
    if not fleet_has_target:
        drop_object(fleet, blob)
    if not lane_has_target:
        drop_object(lane, blob)
    return lane, fleet, lane_commit, tag, blob


def write_report(fleet, lane_commit, extra_tokens=(), errata_rows=(),
                 lane=None, lane_tokens=()):
    rel = ".ufo/reports/round-24/kama.md"
    lines = ["# kama round 24", "", "## Landed changes", "", f"- {lane_commit}"]
    for t in lane_tokens:
        lines.append(f"- {t}")
    for t in extra_tokens:
        lines.append(f"- {t}")
    text = "\n".join(lines) + "\n"
    path = Path(fleet, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    env = dict(ENV)
    env.update(GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    subprocess.run(["git", "--no-lazy-fetch", "-C", str(fleet), "add", "--",
                    rel], capture_output=True, env=env, check=True)
    subprocess.run(["git", "--no-lazy-fetch", "-C", str(fleet), "commit", "-q",
                    "-m", "fleet: report"], capture_output=True, env=env,
                   check=True)
    if errata_rows:
        assert lane is not None
        row = "".join("\t".join(r) + "\n" for r in errata_rows)
        rel2 = "registry/report-landing-errata.tsv"
        p = Path(lane, rel2)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(row, encoding="utf-8")
        subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "add", "--",
                        rel2], capture_output=True, env=env, check=True)
        subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane), "commit",
                        "-q", "-m", "lane: errata"], capture_output=True,
                       env=env, check=True)
    return text


def lane_commits(repo):
    """Every commit on master (the report cites them all, so the only
    defect under study is the one under study)."""
    return g(repo, "log", "--format=%H", "master").split()


def missing_ids(repo):
    """The objects the repository references but cannot serve."""
    out = g(repo, "-c", "core.commitGraph=false", "rev-list", "--objects",
            "--missing=print", "--no-object-names", "--all")
    return sorted(line[1:] for line in out.split("\n")
                  if line.startswith("?"))


def import_tool(path=TOOL):
    import importlib.util
    spec = importlib.util.spec_from_file_location("rla_" + str(abs(hash(path))),
                                                   path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(lane, fleet, tool=TOOL, extra=()):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", "24", "--json", *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return proc.returncode, proc.stdout, proc.stderr


def summarise(code, out, err):
    entry = {"exit": code}
    if code == 2:
        entry["stderr"] = err.strip()
        return entry
    try:
        doc = json.loads(out)
    except json.JSONDecodeError:
        entry["stdout"] = out.strip()[:400]
        return entry
    entry["status"] = doc["summary"]["status"]
    entry["defects"] = [{"kind": d["kind"], "token": d["token"]}
                        for res in doc["results"] for d in res["defects"]]
    entry["errata_unmatched"] = doc["summary"]["errata_unmatched"]
    entry["errata_invalid"] = doc["summary"]["errata_invalid"]
    return entry


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    mod = import_tool()
    results = []

    # ---------------------------------------------------------- unit level
    unit = {}

    def store(repo, root):
        return mod.build_store(repo, root)

    for name, lane_has, fleet_has in (
            ("blob-in-lane-only", True, False),
            ("blob-in-fleet-only", False, True)):
        base = WORK / ("unit-" + name)
        lane, fleet, lc, fc, blob = build_pair(base, lane_has, fleet_has)
        s_lane, s_fleet = store(lane, lc), store(fleet, fc)
        unit[name + " | stores(lane,fleet)"] = mod.lookup((s_lane, s_fleet),
                                                          [blob], "^{commit}")
        unit[name + " | stores(fleet,lane)"] = mod.lookup((s_fleet, s_lane),
                                                          [blob], "^{commit}")
        unit[name + " | bare (lane,fleet)"] = mod.lookup((s_lane, s_fleet),
                                                        [blob])
        unit[name + " | bare (fleet only)"] = mod.lookup((s_fleet,), [blob])
        unit[name + " | bare (lane only)"] = mod.lookup((s_lane,), [blob])

    base = WORK / "unit-cross-repo"
    lane, fleet, lc, fc, blob = build_pair(base, True, True)
    s_lane, s_fleet = store(lane, lc), store(fleet, fc)
    unit["cross-repo-found | fleet commit only (lane,fleet)"] = mod.lookup(
        (s_lane, s_fleet), [fc], "^{commit}")
    unit["cross-repo-found | fleet commit only (fleet,lane)"] = mod.lookup(
        (s_fleet, s_lane), [fc], "^{commit}")
    unit["cross-repo-found | lane commit only (lane,fleet)"] = mod.lookup(
        (s_lane, s_fleet), [lc], "^{commit}")

    # genuine unavailable tag target: the tag object is present, its target
    # blob is not; the tag names the blob, so it cannot peel to a commit.
    base = WORK / "unit-tag-missing"
    lane, fleet, lc, tag, blob = build_tag_pair(base, True, False)
    s_lane, s_fleet = store(lane, lc), store(fleet, lc)
    unit["tag-target-missing | stores(lane,fleet)"] = mod.lookup(
        (s_lane, s_fleet), [tag], "^{commit}")
    unit["tag-target-missing | stores(fleet,lane)"] = mod.lookup(
        (s_fleet, s_lane), [tag], "^{commit}")
    unit["tag-target-missing | single store (fleet)"] = mod.lookup(
        (s_fleet,), [tag], "^{commit}")
    unit["tag-target-missing | bare (fleet)"] = mod.lookup((s_fleet,), [tag])

    # conclusive wrongtype in store 1 + genuine unknown in store 2
    base = WORK / "unit-wrongtype-vs-unknown"
    lane, fleet, lc, tag, blob = build_tag_pair(base, True, False)
    s_lane, s_fleet = store(lane, lc), store(fleet, lc)
    unit["wrongtype(lane)+unknown(fleet) | stores(lane,fleet)"] = mod.lookup(
        (s_lane, s_fleet), [tag], "^{commit}")
    unit["wrongtype(lane)+unknown(fleet) | stores(fleet,lane)"] = mod.lookup(
        (s_fleet, s_lane), [tag], "^{commit}")
    results.append({"level": "unit", "cases": unit})

    # ------------------------------------------------------ cli end to end
    cli = []
    for name, lane_has, fleet_has, cite in (
            ("A-blob-in-lane-only", True, False, True),
            ("B-blob-in-fleet-only", False, True, True),
            ("C-control-no-blob-citation", True, True, False)):
        base = WORK / ("cli-" + name)
        lane, fleet, lc, fc, blob = build_pair(base, lane_has, fleet_has)
        write_report(fleet, lc, extra_tokens=[blob] if cite else [],
                     lane=lane, lane_tokens=lane_commits(lane))
        code, out, err = run_cli(lane, fleet)
        entry = summarise(code, out, err)
        entry["case"] = name
        entry["cited_token"] = blob
        entry["premise"] = {"lane_missing": missing_ids(lane),
                            "fleet_missing": missing_ids(fleet),
                            "blob_in_lane": blob in missing_ids(lane),
                            "blob_in_fleet": blob in missing_ids(fleet)}
        cli.append(entry)

    # D: the lane holds the tag and its target (conclusive wrongtype); the
    #    fleet holds the tag but not its target (genuine unknown).
    base = WORK / "cli-D-tag-lane-conclusive"
    lane, fleet, lc, tag, blob = build_tag_pair(base, True, False)
    write_report(fleet, lc, extra_tokens=[tag], lane=lane,
                 lane_tokens=lane_commits(lane))
    code, out, err = run_cli(lane, fleet)
    entry = summarise(code, out, err)
    entry["case"] = "D-tag-lane-conclusive-fleet-unknown"
    entry["cited_token"] = tag
    entry["premise"] = {"lane_missing": missing_ids(lane),
                        "fleet_missing": missing_ids(fleet)}
    cli.append(entry)

    # E: the same two repositories with the roles swapped: the lane cannot
    #    serve the tag target (unknown), the fleet can (wrongtype).
    base = WORK / "cli-E-tag-lane-unknown"
    lane, fleet, lc, tag, blob = build_tag_pair(base, False, True)
    write_report(fleet, lc, extra_tokens=[tag], lane=lane,
                 lane_tokens=lane_commits(lane))
    code, out, err = run_cli(lane, fleet)
    entry = summarise(code, out, err)
    entry["case"] = "E-tag-lane-unknown-fleet-conclusive"
    entry["cited_token"] = tag
    entry["premise"] = {"lane_missing": missing_ids(lane),
                        "fleet_missing": missing_ids(fleet)}
    cli.append(entry)

    # F: an errata correction that names an object only the fleet holds.
    base = WORK / "cli-F-errata-fleet-only-blob"
    lane, fleet, lc, fc, blob = build_pair(base, False, True)
    write_report(fleet, lc, lane=lane, lane_tokens=lane_commits(lane),
                 errata_rows=[("24", "unresolved-full-hash", blob, blob, "ev")])
    code, out, err = run_cli(lane, fleet)
    entry = summarise(code, out, err)
    entry["case"] = "F-errata-correction-fleet-only-blob"
    entry["cited_token"] = blob
    entry["premise"] = {"lane_missing": missing_ids(lane),
                        "fleet_missing": missing_ids(fleet)}
    cli.append(entry)

    # G: the same errata correction with the blob held by the lane too.
    base = WORK / "cli-G-errata-lane-blob"
    lane, fleet, lc, fc, blob = build_pair(base, True, True)
    write_report(fleet, lc, lane=lane, lane_tokens=lane_commits(lane),
                 errata_rows=[("24", "unresolved-full-hash", blob, blob, "ev")])
    code, out, err = run_cli(lane, fleet)
    entry = summarise(code, out, err)
    entry["case"] = "G-errata-correction-lane-blob"
    entry["cited_token"] = blob
    entry["premise"] = {"lane_missing": missing_ids(lane),
                        "fleet_missing": missing_ids(fleet)}
    cli.append(entry)

    # H: a citation that only the fleet holds (a commit) must resolve:
    #    "found wins across repositories".
    base = WORK / "cli-H-cross-repo-found"
    lane, fleet, lc, fc, blob = build_pair(base, True, True)
    write_report(fleet, lc, extra_tokens=[fc], lane=lane,
                 lane_tokens=lane_commits(lane))
    code, out, err = run_cli(lane, fleet)
    entry = summarise(code, out, err)
    entry["case"] = "H-cross-repo-found-fleet-commit"
    entry["cited_token"] = fc
    entry["premise"] = {"lane_missing": missing_ids(lane),
                        "fleet_missing": missing_ids(fleet)}
    cli.append(entry)

    # I: the tag target is unavailable in BOTH repositories: the genuine
    #    unknown case.
    base = WORK / "cli-I-tag-both-missing"
    lane, fleet, lc, tag, blob = build_tag_pair(base, False, False)
    write_report(fleet, lc, extra_tokens=[tag], lane=lane,
                 lane_tokens=lane_commits(lane))
    code, out, err = run_cli(lane, fleet)
    entry = summarise(code, out, err)
    entry["case"] = "I-tag-target-missing-both"
    entry["cited_token"] = tag
    entry["premise"] = {"lane_missing": missing_ids(lane),
                        "fleet_missing": missing_ids(fleet)}
    cli.append(entry)

    results.append({"level": "cli", "cases": cli})

    # ------------------------------------- inherited base (r23) comparison
    base_cases = []
    for name, lane_has, fleet_has, cite in (
            ("A-blob-in-lane-only", True, False, True),
            ("B-blob-in-fleet-only", False, True, True)):
        base = WORK / ("base-" + name)
        lane, fleet, lc, fc, blob = build_pair(base, lane_has, fleet_has)
        write_report(fleet, lc, extra_tokens=[blob] if cite else [],
                     lane=lane, lane_tokens=lane_commits(lane))
        code, out, err = run_cli(lane, fleet, tool=BASE_TOOL)
        entry = summarise(code, out, err)
        entry["case"] = "r23-base-" + name
        base_cases.append(entry)
    results.append({"level": "cli-r23-base", "cases": base_cases})

    print(json.dumps(results, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
