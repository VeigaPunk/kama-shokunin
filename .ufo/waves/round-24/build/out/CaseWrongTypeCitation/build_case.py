#!/usr/bin/env python3
"""Case C-WT1: a locally present BLOB cited as a Landed commit.

Builds two arms of one offline fixture and runs an auditor on each:

  full              plain offline clone of the origins, no promisor metadata
  promisor-metadata identical content plus promisor metadata only
                    (core.repositoryformatversion=1, remote.origin.promisor=true,
                     remote.origin.partialclonefilter=blob:none); every object
                     is already present locally and remote.origin.url is a
                     local filesystem path

The fleet report's `## Landed changes` section cites the real lane commit LC
and the lane file blob sha T.  T exists, so the existence scan resolves it;
T is not a commit, so the Landed requirement fails.  The expected outcome is
one failed finding (exit 1, kind landed-unresolved) in BOTH arms.

No network transport, no remote command, no credential helper: the only
remote URL is a local path and the fixture is cloned with --no-hardlinks.

Usage: build_case.py [--root DIR] [--auditor PATH] [--frozen-rev REV]
                     [--repo REPO] [--out DIR] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 60


class Premise(Exception):
    """The fixture did not establish what the case claims."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       input=None if data is None else data.encode(),
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))} in {repo}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def g_rc(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env())
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo) / path
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


def build_origins(root):
    """origin lane: one round-1 commit by kama-shokunin holding file 'f';
    origin fleet: the round-1 report commit."""
    lane_o = Path(root, "origin-lane")
    fleet_o = Path(root, "origin-fleet")
    g(root, "init", "-q", "-b", "master", str(lane_o))
    g(root, "init", "-q", "-b", "master", str(fleet_o))
    lc = commit(lane_o, "kama-shokunin", 1000, "round-1: work")
    blob = g(lane_o, "rev-parse", f"{lc}:f")
    text = ("# kama round 1\n\n## Work performed\n"
            f"landed the round-1 work as {lc}\n\n"
            "## Landed changes\n\n"
            f"- `{lc}` round-1: work\n"
            f"- `{blob}` round-1: work\n")
    commit(fleet_o, "fleet", 2000, "round-1: report", REL, text.encode())
    return lane_o, fleet_o, lc, blob


def clone_arm(root, name, lane_o, fleet_o):
    """Offline clone (--no-hardlinks copies objects; no transport, no
    network) of both origins."""
    lane = Path(root, f"lane-{name}")
    fleet = Path(root, f"fleet-{name}")
    g(root, "clone", "-q", "--no-hardlinks", str(lane_o), str(lane))
    g(root, "clone", "-q", "--no-hardlinks", str(fleet_o), str(fleet))
    return lane, fleet


def make_unrelated_hole(lane):
    """An unrelated missing blob: a post-report lane commit whose tree
    references a blob that is deleted from the store.  The blob is not
    cited anywhere and no audit read needs it; a peel failure on a
    *present* object is not absence."""
    work = Path(lane, "g")
    work.write_text("round-1: later\n", encoding="utf-8")
    g(lane, "add", "--", "g")
    tree = g(lane, "write-tree")
    blob = g(lane, "rev-parse", f"{tree}:g")
    parent = g(lane, "rev-parse", "HEAD")
    body = f"round-1: later\n"
    commit_obj = g(lane, "commit-tree", tree, "-p", parent, "-m",
                   "round-1: later",
                   GIT_AUTHOR_NAME="kama-shokunin",
                   GIT_COMMITTER_NAME="kama-shokunin",
                   GIT_AUTHOR_DATE="@3000 +0000",
                   GIT_COMMITTER_DATE="@3000 +0000")
    # move the branch without touching the worktree (the blob is gone)
    g(lane, "update-ref", "refs/heads/master", commit_obj)
    # delete the loose blob object: the hole is referenced by a present tree
    path = git_path(lane, f"objects/{blob[:2]}/{blob[2:]}")
    if not path.exists():
        raise Premise(f"expected a loose object for {blob} at {path}")
    path.unlink()
    if g_rc(lane, "cat-file", "-e", blob)[0] == 0:
        raise Premise("the hole did not materialize")
    return commit_obj, blob


def mark_promisor(repo):
    """Promisor metadata only.  All objects stay present; the origin URL is
    a local path, so even an attempted lazy fetch could not leave the host."""
    g(repo, "config", "core.repositoryformatversion", "1")
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "remote.origin.partialclonefilter", "blob:none")


def git_path(repo, rel):
    """git rev-parse --git-path, resolved against the repository."""
    p = Path(g(repo, "rev-parse", "--git-path", rel))
    return p if p.is_absolute() else Path(repo) / p


def object_inventory(repo):
    """(object count, pack file list) - a lazy fetch would change both."""
    out = g(repo, "cat-file", "--batch-all-objects", "--batch-check")
    count = len([ln for ln in out.split("\n") if ln.strip()])
    packdir = git_path(repo, "objects/pack")
    packs = sorted(p.name for p in packdir.iterdir()) if packdir.is_dir() else []
    return {"objects": count, "packs": packs}


def config_entries(repo):
    listing = g(repo, "config", "--null", "--list")
    out = []
    for entry in listing.split("\0"):
        if not entry:
            continue
        key, _, value = entry.partition("\n")
        out.append((key, value))
    return out


def premises(name, lane, fleet, lc, blob, mark_lane, mark_fleet, hole_info):
    """Every claim the case rests on, checked before the auditor runs."""
    checks = {}

    def rec(name_, ok, detail):
        checks[name_] = {"ok": bool(ok), "detail": detail}

    rec("lane-blob-is-present", g(lane, "cat-file", "-t", blob) == "blob",
        f"cat-file -t {blob} -> {g(lane, 'cat-file', '-t', blob)}")
    rc, _, err = g_rc(lane, "rev-parse", "--verify", f"{blob}^{{commit}}")
    rec("blob-does-not-peel-to-commit", rc != 0,
        f"rev-parse {blob}^{{commit}} rc={rc} ({err.splitlines()[-1][:120] if err else ''})")
    rec("lane-commit-is-a-commit", g(lane, "cat-file", "-t", lc) == "commit",
        f"cat-file -t {lc} -> {g(lane, 'cat-file', '-t', lc)}")
    report = g(fleet, "show", f"HEAD:{REL}")
    rec("report-committed-with-both-tokens",
        lc in report and blob in report and "## Landed changes" in report,
        f"report holds LC and T; bytes={len(report)}")
    rec("report-first-add-time",
        g(fleet, "log", "--diff-filter=A", "--format=%at", "--", REL) == "2000",
        g(fleet, "log", "--diff-filter=A", "--format=%at", "--", REL))
    for label, repo in (("lane", lane), ("fleet", fleet)):
        packdir = git_path(repo, "objects/pack")
        rec(f"{label}-no-promisor-pack", not any(
            p.name.endswith(".promisor")
            for p in (packdir.iterdir() if packdir.is_dir() else [])),
            "no *.promisor marker")
    lane_cfg = dict(config_entries(lane))
    fleet_cfg = dict(config_entries(fleet))
    lane_marked = lane_cfg.get("remote.origin.promisor") == "true"
    fleet_marked = fleet_cfg.get("remote.origin.promisor") == "true"
    rec("promisor-metadata-as-declared",
        lane_marked == mark_lane and fleet_marked == mark_fleet,
        f"lane.remote.origin.promisor={lane_cfg.get('remote.origin.promisor')!r} "
        f"fleet.remote.origin.promisor={fleet_cfg.get('remote.origin.promisor')!r}")
    rec("promisor-partialclonefilter-as-declared",
        (lane_cfg.get("remote.origin.partialclonefilter") == "blob:none")
        == mark_lane and
        (fleet_cfg.get("remote.origin.partialclonefilter") == "blob:none")
        == mark_fleet,
        "filter matches the marking plan")
    rec("no-extensions-partialclone",
        "extensions.partialclone" not in lane_cfg
        and "extensions.partialclone" not in fleet_cfg,
        "only remote.* promisor metadata, as git 2.56 clone --filter writes")
    urls = [v for k, v in lane_cfg.items() if k.endswith(".url")] + \
           [v for k, v in fleet_cfg.items() if k.endswith(".url")]
    rec("no-network-remote",
        bool(urls) and all(u.startswith("/") or u.startswith("file://")
                           for u in urls),
        f"remote urls={urls}")
    all_cfg = set(lane_cfg) | set(fleet_cfg)
    rec("no-remote-command-or-credential",
        not any(k in ("core.sshcommand", "credential.helper", "core.gitproxy",
                      "remote.origin.uploadpack", "gpg.program",
                      "gpg.ssh.program", "core.askpass")
                for k in all_cfg),
        "no sshCommand/credential/proxy/uploadpack/gpg program configured")
    rec("required-objects-locally-present",
        g(lane, "cat-file", "-e", blob) == "" and
        g(lane, "cat-file", "-e", lc) == "" and
        g(fleet, "cat-file", "-e", f"HEAD:{REL}") == "",
        "LC, T and the report blob all resolve without a fetch")
    if hole_info:
        hole_commit, hole_blob = hole_info
        rc, _, _ = g_rc(lane, "cat-file", "-e", hole_blob)
        rec("unrelated-hole-is-absent", rc != 0,
            f"cat-file -e {hole_blob} rc={rc}")
        tree_entry = g(lane, "ls-tree", hole_commit, "--", "g")
        rec("unrelated-hole-is-referenced-by-a-present-tree",
            hole_blob in tree_entry, f"ls-tree {hole_commit}: {tree_entry}")
        rec("unrelated-hole-is-not-cited",
            hole_blob not in g(fleet, "show", f"HEAD:{REL}"),
            "the missing blob appears nowhere in the report")
        log = g(lane, "log", "--format=%H", "master")
        rec("lane-history-still-readable", lc in log.split("\n"),
            f"git log over the lane tip still works ({len(log.splitlines())} commits)")
    return checks


def run_auditor(auditor, lane, fleet, tmp):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    proc = subprocess.run(argv, capture_output=True, env=env(), cwd=tmp,
                          timeout=TIMEOUT)
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    kinds, tokens, doc = None, None, None
    if proc.returncode in (0, 1):
        try:
            doc = json.loads(out)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
            tokens = sorted({d["token"] for r in doc["results"]
                             for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds, tokens = "unparseable", "unparseable"
    return {"exit": proc.returncode, "kinds": kinds, "tokens": tokens,
            "traceback": "Traceback (most recent call last)" in err,
            "stdout": out, "stderr": err.strip(),
            "argv": argv}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="/fast/scratch/hyaku/kama-r24/"
                                      "CaseWrongTypeCitation/run")
    ap.add_argument("--repo", default="/home/vgpnk/Projects/shokunin/"
                                      "kama-shokunin")
    ap.add_argument("--frozen-rev", default="0df800e896f6bce285a81e794ad4ae1d1e6c3a71")
    ap.add_argument("--auditor", default=None,
                    help="run this auditor instead of the frozen blob")
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    lane_o, fleet_o, lc, blob = build_origins(root)
    # name -> (mark lane, mark fleet, unrelated hole)
    plan = {
        "full": (False, False, False),
        "promisor-lane-only": (True, False, False),
        "promisor-fleet-only": (False, True, False),
        "promisor-metadata": (True, True, False),
        "promisor-metadata-unrelated-hole": (True, True, True),
        "non-promisor-unrelated-hole": (False, False, True),
    }
    arms = {}
    for name, (mark_lane, mark_fleet, hole) in plan.items():
        lane, fleet = clone_arm(root, name, lane_o, fleet_o)
        hole_info = None
        if hole:
            hole_info = make_unrelated_hole(lane)
        if mark_lane:
            mark_promisor(lane)
        if mark_fleet:
            mark_promisor(fleet)
        arms[name] = (lane, fleet, mark_lane, mark_fleet, hole_info)

    if args.auditor:
        auditor = Path(args.auditor).resolve()
        auditor_kind = "current"
    else:
        blob_bytes = subprocess.run(
            ["git", "-C", args.repo, "cat-file", "blob",
             f"{args.frozen_rev}:tools/report-landing-audit.py"],
            capture_output=True, env=env())
        if blob_bytes.returncode:
            raise SystemExit("cannot read frozen auditor: "
                             + blob_bytes.stderr.decode(errors="replace"))
        auditor = root / "frozen-report-landing-audit.py"
        auditor.write_bytes(blob_bytes.stdout)
        auditor_kind = f"frozen:{args.frozen_rev}"

    doc = {"case": "C-WT1-wrong-type-citation-landed", "root": str(root),
           "auditor": auditor_kind, "auditor_path": str(auditor),
           "lane_commit": lc, "blob": blob, "arms": {}}
    for name, (lane, fleet, mark_lane, mark_fleet, hole_info) in arms.items():
        checks = premises(name, lane, fleet, lc, blob, mark_lane, mark_fleet,
                          hole_info)
        before = {r: object_inventory(p) for r, p in
                  (("lane", lane), ("fleet", fleet))}
        res = run_auditor(auditor, lane, fleet, root)
        after = {r: object_inventory(p) for r, p in
                 (("lane", lane), ("fleet", fleet))}
        res["premises"] = checks
        res["premises_ok"] = all(c["ok"] for c in checks.values())
        res["inventory_before"] = before
        res["inventory_after"] = after
        res["no_new_objects"] = before == after
        doc["arms"][name] = res

    out = Path(args.out) if args.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "results.json").write_text(json.dumps(doc, indent=1,
                                                      sort_keys=True),
                                           encoding="utf-8")
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for name, res in doc["arms"].items():
            print(f"arm={name} exit={res['exit']} kinds={res['kinds']} "
                  f"tokens={res['tokens']} premises_ok={res['premises_ok']} "
                  f"no_new_objects={res['no_new_objects']}")
            if res["stderr"]:
                print(f"  stderr: {res['stderr'][:400]}")
            for k, c in res["premises"].items():
                if not c["ok"]:
                    print(f"  PREMISE FAILED {k}: {c['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
