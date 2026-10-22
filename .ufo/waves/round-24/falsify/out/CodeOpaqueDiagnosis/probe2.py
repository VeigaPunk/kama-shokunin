#!/usr/bin/env python3
"""Second bounded round against the same pinned r24 auditor.

Axes: promisor metadata must not change a verdict; a missing commit
hidden behind a present annotated tag must still be an opaque hole; a
hole in the fleet store alone must not block a clean lane; and the
store-wide walk must fit inside the auditor's own GIT_TIMEOUT.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe import (AUDIT, ROOT, WORK, base_env, body_for, build, commit,  # noqa
                   drop, g, init_repo, republish, FAKE)

MOD = importlib.util.spec_from_file_location("auditor_r24b", AUDIT)
M = importlib.util.module_from_spec(MOD)
MOD.loader.exec_module(M)

RESULTS = []


def case(name, expect, ok, observed):
    RESULTS.append({"case": name, "expect": expect, "observed": observed,
                    "pass": bool(ok)})
    print(f"{'OK  ' if ok else 'FAIL'} {name}: expect={expect}\n"
          f"      observed={observed}")


def audit(lane, fleet, extra=()):
    env = base_env()
    env["TMPDIR"] = str(WORK / "tmp")
    cmd = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
           "--rounds", "1", "--json", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                       cwd=str(WORK))
    defects = []
    doc = None
    if p.stdout.strip():
        doc = json.loads(p.stdout)
        for res in doc["results"]:
            for d in res["defects"]:
                defects.append((d["kind"], d["token"]))
    return p.returncode, p.stderr.strip(), defects


def fresh(tag):
    d = WORK / tag
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def sets(lane, fleet):
    lm, lo = M.missing_reachable(lane, g(lane, "rev-parse", "HEAD"))
    fm, fo = M.missing_reachable(fleet, g(fleet, "rev-parse", "HEAD"))
    return lm, lo, fm, fo


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "tmp").mkdir(parents=True, exist_ok=True)

    # S12 promisor metadata + unrelated missing blob + fabricated token
    tmp = fresh("s12")
    lane, fleet, info = build(tmp)
    drop(lane, info["noise_blob"])
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    for k, v in (("remote.origin.promisor", "true"),
                 ("remote.origin.url", "ssh://example.invalid/x.git")):
        g(lane, "config", k, v)
    rc, err, defects = audit(lane, fleet)
    lm, lo, _, _ = sets(lane, fleet)
    ok = (rc == 1 and defects == [("unresolved-full-hash", FAKE)]
          and info["noise_blob"] not in lo)
    case("S12-promisor-metadata-blob-hole-stays-non-opaque",
         "exit 1 unresolved-full-hash; blob hole not opaque",
         ok, f"rc={rc} defects={defects} err={err!r} blob_in_opaque="
             f"{info['noise_blob'] in lo}")

    # S13 promisor marker without a url, no hole at all
    tmp = fresh("s13")
    lane, fleet, info = build(tmp)
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    g(lane, "config", "remote.origin.promisor", "true")
    rc, err, defects = audit(lane, fleet)
    ok13a = rc == 1 and defects == [("unresolved-full-hash", FAKE)]
    case("S13a-promisor-marker-without-url", "exit 1 (no metadata refusal)",
         ok13a, f"rc={rc} defects={defects} err={err!r}")

    # S13b extensions.partialClone pointing at a url-less origin
    tmp = fresh("s13b")
    lane, fleet, info = build(tmp)
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    g(lane, "config", "extensions.partialClone", "origin")
    g(lane, "config", "remote.origin.promisor", "true")
    rc, err, defects = audit(lane, fleet)
    ok13b = rc == 1 and defects == [("unresolved-full-hash", FAKE)]
    case("S13b-partialclone-extension-without-url",
         "exit 1 (no metadata refusal)", ok13b,
         f"rc={rc} defects={defects} err={err!r}")

    # S14 missing commit hidden behind a present annotated tag
    tmp = fresh("s14")
    lane, fleet, info = build(tmp)
    # a detached commit that no ref reaches, then an annotated tag on it
    tree = g(lane, "rev-parse", f"{info['first']}^{{tree}}")
    gone = subprocess.run(["git", "-C", str(lane), "commit-tree", tree,
                           "-m", "vanished"], capture_output=True, text=True,
                          env=base_env(GIT_AUTHOR_DATE="@900 +0000",
                                       GIT_COMMITTER_DATE="@900 +0000")
                          ).stdout.strip()
    g(lane, "tag", "-a", "-m", "hole", "v-hole", gone,
      env=base_env(GIT_AUTHOR_DATE="@910 +0000",
                   GIT_COMMITTER_DATE="@910 +0000"))
    drop(lane, gone)
    lm, lo, _, _ = sets(lane, fleet)
    ok14 = gone in lm and gone in lo
    case("S14-tag-hidden-missing-commit-is-an-opaque-hole",
         "missing commit in missing and in opaque", ok14,
         f"in_missing={gone in lm} in_opaque={gone in lo} "
         f"opaque={sorted(x[:12] for x in lo)}")

    # S14b a hole in the fleet store alone does not block a clean lane
    tmp = fresh("s14b")
    lane, fleet, info = build(tmp)
    fblob = g(fleet, "rev-parse", f"HEAD:{info['rel']}")
    drop(fleet, fblob)
    rc, err, defects = audit(lane, fleet)
    ok14b = (rc == 2 and "unavailable required object" in err
             and info["rel"] in err)
    case("S14b-fleet-report-blob-itself-missing",
         "exit 2 naming the required fleet report (required_read path)",
         ok14b, f"rc={rc} err={err!r}")

    # S14c a hole in the fleet store alone does not block a CLEAN lane run
    tmp = fresh("s14c")
    lane, fleet, info = build(tmp)
    # a fleet-side object that no read needs: an extra committed file
    (fleet / "extra.txt").write_text("extra\n", encoding="utf-8")
    commit(fleet, "fleet: extra", 2000, {"extra.txt": "extra\n"})
    eblob = g(fleet, "rev-parse", "HEAD:extra.txt")
    drop(fleet, eblob)
    rc, err, defects = audit(lane, fleet)
    ok14c = rc == 0 and defects == []
    case("S14c-unrelated-fleet-hole-does-not-block", "exit 0, no defects",
         ok14c, f"rc={rc} defects={defects} err={err!r}")

    # S15 walk cost on the real clone (GIT_TIMEOUT is 20 s per git call)
    clone = ROOT / "repo"
    head = g(clone, "rev-parse", "HEAD")
    t0 = time.time()
    roots = M.present_roots(clone)
    t1 = time.time()
    missing, opaque = M.missing_reachable(clone, head)
    t2 = time.time()
    counts = g(clone, "count-objects", "-v")
    ok15 = (t2 - t0) < 20 and len(roots) > 0
    case("S15-store-wide-walk-fits-the-auditors-timeout",
         "present_roots + both walks under 20 s", ok15,
         f"roots={len(roots)} present_roots={t1 - t0:.2f}s "
         f"walks={t2 - t1:.2f}s missing={len(missing)} opaque={len(opaque)}")

    print("\n---- summary ----")
    for r in RESULTS:
        print(f"{'OK  ' if r['pass'] else 'FAIL'} {r['case']}")
    failed = [r for r in RESULTS if not r["pass"]]
    print(f"cases={len(RESULTS)} failed={len(failed)}")
    (ROOT / "probe2-results.json").write_text(
        json.dumps(RESULTS, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
