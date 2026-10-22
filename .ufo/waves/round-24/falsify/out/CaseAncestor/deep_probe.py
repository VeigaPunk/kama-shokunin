#!/usr/bin/env python3
"""Deeper-ancestor probe: is PG21's refusal caused by the hole the audit
actually needs, or by any hole at all?

Variant E: the lane has a three-commit chain (round-1: older -> round-1:
earlier -> round-1: work tip).  The GRANDparent commit is dropped, while
the parent and the tip stay readable.  The audit still needs the whole
round-1 history to decide the omission question, so the refusal must
persist, and it must still be content-derived.

Variant F: a hole in a commit that is NOT on the audited lane history (a
side branch) must NOT block: the audit reads only the pinned tip's
history.  This is the no-blanket-precondition direction.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out")
import promisor_grid_py as G  # noqa: E402

ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out/deep-root")
AUDIT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo/tools/report-landing-audit.py")


def commit(repo, author, when, msg, path, content):
    return G.commit(repo, author, when, msg, path, content)


def build_deep(root, tmp, marked=True, drop_grandparent=True):
    lane = G.init_repo(root, Path(tmp, "lane"))
    fleet = G.init_repo(root, Path(tmp, "fleet"))
    older = commit(lane, "kama-shokunin", 800, "round-1: older", "f", "older\n")
    earlier = commit(lane, "kama-shokunin", 900, "round-1: earlier", "f", "earlier\n")
    Path(lane, "f").write_text("fixture file\n", encoding="utf-8")
    Path(lane, "corpus").mkdir(parents=True, exist_ok=True)
    Path(lane, "corpus", "SOURCES.md").write_text(G.SOURCES, encoding="utf-8")
    G.git(lane, "add", "--", "f", "corpus/SOURCES.md")
    G.git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work",
          GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
          GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    tip = G.git(lane, "rev-parse", "HEAD").strip()
    G.publish(fleet, G.report_text([tip]), 2000)
    if marked:
        G.mark_config(lane, tmp)
    dropped = None
    if drop_grandparent:
        dropped = G.drop_object(lane, older)
    return {"lane": lane, "fleet": fleet,
            "shas": {"ancestor": older, "parent": earlier, "lane_commit": tip,
                     "dropped": dropped},
            "premise": {"lane_promisor": G.promisor_facts(lane)["promisor_backed"],
                        "lane_missing": G.missing_objects(lane, "refs/heads/master"),
                        "fleet_missing": G.missing_objects(fleet, "HEAD")}}


def build_side_hole(root, tmp, marked=True):
    """A hole on an UNSELECTED branch; the audited tip's history is intact."""
    lane = G.init_repo(root, Path(tmp, "lane"))
    fleet = G.init_repo(root, Path(tmp, "fleet"))
    Path(lane, "corpus").mkdir(parents=True, exist_ok=True)
    Path(lane, "corpus", "SOURCES.md").write_text(G.SOURCES, encoding="utf-8")
    Path(lane, "f").write_text("fixture file\n", encoding="utf-8")
    G.git(lane, "add", "--", "f", "corpus/SOURCES.md")
    G.git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work",
          GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
          GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    tip = G.git(lane, "rev-parse", "HEAD").strip()
    G.git(lane, "checkout", "-q", "-b", "side")
    side = commit(lane, "kama-shokunin", 1200, "side: file", "side.txt", "side\n")
    G.git(lane, "checkout", "-q", "master")
    G.publish(fleet, G.report_text([tip]), 2000)
    if marked:
        G.mark_config(lane, tmp)
    dropped = G.drop_object(lane, side)
    return {"lane": lane, "fleet": fleet,
            "shas": {"lane_commit": tip, "dropped": dropped},
            "premise": {"lane_promisor": G.promisor_facts(lane)["promisor_backed"],
                        "lane_missing": G.missing_objects(lane, "refs/heads/master"),
                        "fleet_missing": G.missing_objects(fleet, "HEAD")}}


def run(name, built):
    tmp = built["lane"].parent
    before = {k: G.object_inventory(built[k]) for k in ("lane", "fleet")}
    code, out, err, to = G.run_auditor(AUDIT, built["lane"], built["fleet"], tmp, False)
    after = {k: G.object_inventory(built[k]) for k in ("lane", "fleet")}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = []
    if doc:
        for res in doc["results"]:
            for d in res.get("defects", []):
                defects.append((d.get("kind"), d.get("token")))
    return {"variant": name, "exit": code, "defects": sorted(defects),
            "acquired": {k: sorted(after[k] - before[k]) for k in after},
            "stderr": err.strip(), "stdout_bytes": len(out),
            "premise": built["premise"], "shas": built["shas"]}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    res = []
    for i, (name, maker, opt) in enumerate([
        ("E-grandparent-missing-marked", build_deep, dict(marked=True)),
        ("F-unselected-side-hole-marked", build_side_hole, dict(marked=True)),
        ("G-unselected-side-hole-unmarked", build_side_hole, dict(marked=False)),
    ]):
        tmp = ROOT / f"{i:02d}-{name}"
        tmp.mkdir(parents=True, exist_ok=True)
        res.append(run(name, maker(ROOT, tmp, **opt)))
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
