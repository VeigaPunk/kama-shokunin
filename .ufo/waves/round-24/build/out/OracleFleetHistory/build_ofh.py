#!/usr/bin/env python3
"""Offline fixture builder — round-24 C1 promisor repair, OracleFleetHistory.

Case: a COMPLETE fleet repository that carries promisor *metadata* and a
report whose history contains add -> delete -> re-add commits.  The audit's
cutoff must be the FIRST add (author time of the fleet commit that first
added the report), never the re-add.

Synthetic only: no network, no transport command, no fetched payload, no
execution of fixture content.  Every path is created under ROOT, which the
builder refuses to place outside /fast/scratch/hyaku/kama-r24/OracleFleetHistory.

Layout produced under ROOT:
  lane/                    plain lane repo (unmarked)
  fleet_plain/             plain fleet repo, report v1==v2 (clean case)
  fleet_marked_cfg/        fleet_plain + remote.origin.promisor=true
  fleet_marked_pack/       fleet_plain + paired .promisor/.pack markers
  fleet_hist/              fleet with report v1 != v2 (HEAD-bytes case)
  fleet_hist_missing/      fleet_hist with the FIRST-ADD report blob deleted
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ALLOWED = Path("/fast/scratch/hyaku/kama-r24/OracleFleetHistory").resolve()
ROOT = (Path(sys.argv[1]).resolve() if len(sys.argv) > 1
        else ALLOWED / "fixtures" / "out")

REL = ".ufo/reports/round-1/kama.md"
V1 = (
    "# Round 1 kama report\n"
    "\n"
    "## Work performed\n"
    "Synthetic fixture report for the round-24 promisor completeness case.\n"
    "\n"
    "## Landed changes (commits)\n"
    "- `{alpha}` alpha work\n"
)
# v2 differs from v1 only in a trailing section, so a tool that reads the
# first-add bytes instead of the HEAD bytes reports a different defect set.
V2_TAIL = (
    "\n"
    "## Notes\n"
    "second revision of the same round report\n"
    "marker {phantom}\n"
)
PHANTOM = "0123456789abcdef0123456789abcdef01234567"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def git(repo, *args, when=None, name="kama-shokunin", check=True):
    env = dict(ENV)
    if when is not None:
        env.update(GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL="a@x",
                   GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL="a@x",
                   GIT_AUTHOR_DATE=f"@{when} +0000",
                   GIT_COMMITTER_DATE=f"@{when} +0000")
    proc = subprocess.run(["git", "-C", str(repo), *args], env=env,
                          capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} in {repo} failed: "
                         f"{proc.stderr.strip()}")
    return proc


def init(repo):
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "master")
    git(repo, "config", "user.name", "kama-shokunin")
    git(repo, "config", "user.email", "a@x")
    git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo, rel, text):
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(repo, subject, when, name="kama-shokunin"):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", subject, when=when, name=name)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def build_lane(root):
    lane = init(root / "lane")
    shas = {}
    for key, subject, when, name in (
            ("alpha", "round-1: alpha", 500, "kama-shokunin"),
            ("beta", "round-1: beta", 1500, "kama-shokunin"),
            ("gamma", "round-1: gamma", 2500, "kama-shokunin"),
            ("foreign", "round-1: foreign author", 1600, "someone"),
            ("other", "round-10: other round", 1700, "kama-shokunin")):
        write(lane, f"lane/work-{key}.md", f"{subject}\n")
        sha = commit(lane, subject, when, name=name)
        if name == "kama-shokunin":
            shas[key] = sha
    return lane, shas


def build_fleet(root, name, v1, v2):
    """add(1000) -> delete(2000) -> re-add(3000) -> delete(4000) -> re-add(5000).

    Two delete/readd cycles: the cutoff must still be the FIRST add (1000),
    not the newest re-add (5000) and not the last add before a delete."""
    fleet = init(root / name)
    write(fleet, REL, v1)
    f1 = commit(fleet, "round-1: kama report", 1000)
    git(fleet, "rm", "-q", REL)
    f2 = commit(fleet, "round-1: drop report", 2000)
    write(fleet, REL, v2)
    f3 = commit(fleet, "round-1: re-add report", 3000)
    git(fleet, "rm", "-q", REL)
    f4 = commit(fleet, "round-1: drop report again", 4000)
    write(fleet, REL, v2)
    f5 = commit(fleet, "round-1: re-add report again", 5000)
    blob1 = git(fleet, "rev-parse", f"{f1}:{REL}").stdout.strip()
    blob2 = git(fleet, "rev-parse", f"{f5}:{REL}").stdout.strip()
    return fleet, {"f1": f1, "f2": f2, "f3": f3, "f4": f4, "f5": f5,
                   "blob1": blob1, "blob2": blob2}


def copy_repo(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)
    return dst


def build_lane_skew(root):
    """Lane twin with one extra uncited commit between the two candidate
    cutoffs (500 vs 1000) so a time-minimum cutoff and a topological
    first-add cutoff give different required sets."""
    lane = init(root / "lane_skew")
    shas = {}
    for key, subject, when in (("alpha", "round-1: alpha", 500),
                               ("mid", "round-1: mid", 700),
                               ("beta", "round-1: beta", 1500),
                               ("gamma", "round-1: gamma", 2500)):
        write(lane, f"lane/work-{key}.md", f"{subject}\n")
        shas[key] = commit(lane, subject, when)
    return lane, shas


def build_fleet_skew(root, name, v1):
    """add(1000) -> delete(2000) -> re-add(500): the re-add carries the
    EARLIER author time, so the oldest author time among add commits is not
    the topologically first add."""
    fleet = init(root / name)
    write(fleet, REL, v1)
    f1 = commit(fleet, "round-1: kama report", 1000)
    git(fleet, "rm", "-q", REL)
    commit(fleet, "round-1: drop report", 2000)
    write(fleet, REL, v1)
    f3 = commit(fleet, "round-1: re-add report", 500)
    return fleet, {"f1": f1, "f3": f3,
                   "blob1": git(fleet, "rev-parse", f"{f1}:{REL}").stdout.strip(),
                   "blob3": git(fleet, "rev-parse", f"{f3}:{REL}").stdout.strip()}


def main():
    if ALLOWED not in ROOT.parents and ROOT != ALLOWED:
        raise SystemExit(f"refusing to build outside {ALLOWED}: {ROOT}")
    ROOT.mkdir(parents=True, exist_ok=True)
    lane, shas = build_lane(ROOT)
    alpha = shas["alpha"]
    prefix = alpha[:7]
    if not (any(c.isdigit() for c in prefix) and any(c in "abcdef" for c in prefix)):
        prefix = alpha[:8]
    v1 = V1.format(alpha=prefix)
    v2_plain = v1
    v2_hist = v1 + V2_TAIL.format(phantom=PHANTOM)

    plain, p = build_fleet(ROOT, "fleet_plain", v1, v2_plain)
    hist, h = build_fleet(ROOT, "fleet_hist", v1, v2_hist)
    build_lane_skew(ROOT)
    skew, sk = build_fleet_skew(ROOT, "fleet_skew", v1)
    skew_cfg = copy_repo(skew, ROOT / "fleet_skew_marked_cfg")
    git(skew_cfg, "config", "remote.origin.url", "https://example.invalid/fleet.git")
    git(skew_cfg, "config", "remote.origin.promisor", "true")

    cfg = copy_repo(plain, ROOT / "fleet_marked_cfg")
    hist_cfg = copy_repo(hist, ROOT / "fleet_hist_marked_cfg")
    git(hist_cfg, "config", "remote.origin.url", "https://example.invalid/fleet.git")
    git(hist_cfg, "config", "remote.origin.promisor", "true")
    git(cfg, "config", "remote.origin.url", "https://example.invalid/fleet.git")
    git(cfg, "config", "remote.origin.promisor", "true")

    pack = copy_repo(plain, ROOT / "fleet_marked_pack")
    git(pack, "repack", "-a", "-d")
    packs = sorted((pack / ".git" / "objects" / "pack").glob("pack-*.pack"))
    if len(packs) != 1:
        raise SystemExit(f"expected one pack, got {packs}")
    packs[0].with_suffix(".promisor").write_bytes(b"")
    git(pack, "config", "--unset", "remote.origin.promisor", check=False)

    missing = copy_repo(hist, ROOT / "fleet_hist_missing")
    git(missing, "config", "remote.origin.url", "https://example.invalid/fleet.git")
    git(missing, "config", "remote.origin.promisor", "true")
    blob = h["blob1"]
    loose = missing / ".git" / "objects" / blob[:2] / blob[2:]
    if not loose.exists():
        raise SystemExit(f"first-add blob is not loose: {loose}")
    loose.unlink()
    # the loose removal must leave the re-added blob intact
    keep = missing / ".git" / "objects" / h["blob2"][:2] / h["blob2"][2:]

    facts = {
        "root": str(ROOT),
        "lane": {"alpha": shas["alpha"], "beta": shas["beta"],
                 "gamma": shas["gamma"], "cited_prefix": prefix},
        "fleet_plain": p,
        "fleet_hist": h,
        "fleet_skew": sk,
        "report": REL,
        "first_add": 1000,
        "delete": 2000,
        "readd": 3000,
        "deleted_loose_blob": str(loose),
        "kept_loose_blob": str(keep),
        "kept_blob_present": keep.exists(),
        "phantom_token": PHANTOM,
    }
    (ROOT / "facts.json").write_text(json.dumps(facts, indent=1,
                                                sort_keys=True) + "\n",
                                     encoding="utf-8")
    print(json.dumps(facts, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
