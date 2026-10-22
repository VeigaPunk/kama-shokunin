#!/usr/bin/env python3
"""Third bounded round: cross-store opaque attribution, wrong-type
citations under an unrelated opaque hole, gitlink entries, and the walk
cost on the real fleet repository.
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
                   drop, g, republish, FAKE)

SPEC = importlib.util.spec_from_file_location("auditor_r24c", AUDIT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

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
    defects, doc = [], None
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

    # S16 the fleet store's opaque hole is the one named
    tmp = fresh("s16")
    lane, fleet, info = build(tmp)
    # a real subtree inside the fleet store, then delete the subtree object
    blob = subprocess.run(["git", "-C", str(fleet), "hash-object", "-w",
                           "--stdin"], input="fleet payload\n", text=True,
                          capture_output=True, env=base_env()).stdout.strip()
    sub = subprocess.run(["git", "-C", str(fleet), "mktree"],
                         input=f"100644 blob {blob}\tf\n", capture_output=True,
                         text=True, env=base_env()).stdout.strip()
    entries = g(fleet, "ls-tree", "HEAD")
    top = subprocess.run(["git", "-C", str(fleet), "mktree"],
                         input=entries + f"\n040000 tree {sub}\td\n",
                         capture_output=True, text=True, env=base_env()
                         ).stdout.strip()
    tree = subprocess.run(["git", "-C", str(fleet), "commit-tree", top, "-p",
                           "HEAD", "-m", "fleet: subtree"],
                          capture_output=True, text=True,
                          env=base_env(GIT_AUTHOR_DATE="@2000 +0000",
                                       GIT_COMMITTER_DATE="@2000 +0000")
                          ).stdout.strip()
    g(fleet, "reset", "-q", "--hard", tree)
    body = body_for(info["required"], FAKE + "\n")
    republish(fleet, info, body)
    drop(fleet, sub)
    rc, err, defects = audit(lane, fleet)
    lm, lo, fm, fo = sets(lane, fleet)
    ok = (rc == 2 and "could be hidden behind the missing tree or commit" in err
          and str(fleet) in err and sub in fo and sub not in lo)
    case("S16-fleet-store-opaque-hole-is-named",
         "exit 2 naming the fleet tree", ok,
         f"rc={rc} err={err!r} fleet_opaque={sub in fo} "
         f"fleet_missing={sub in fm}")

    # S17 a present blob cited under an unrelated opaque hole stays a finding
    tmp = fresh("s17")
    lane, fleet, info = build(tmp, subtree=True)
    head = g(lane, "rev-parse", "HEAD")
    sub = g(lane, "rev-parse", f"{head}:d")
    drop(lane, sub)
    blob = g(lane, "rev-parse", f"{info['first']}:a.txt")
    body = body_for(info["required"], "")
    body = body.replace("## Landed changes\n", f"## Landed changes\n- `{blob}`\n")
    republish(fleet, info, body)
    rc, err, defects = audit(lane, fleet)
    ok = (rc == 1 and ("landed-unresolved", blob) in defects
          and "unavailable required object" not in err)
    case("S17-wrongtype-citation-under-an-opaque-hole-stays-a-finding",
         "exit 1 landed-unresolved (no refusal)", ok,
         f"rc={rc} defects={defects} err={err!r}")

    # S18 a gitlink (submodule) entry whose commit is absent
    tmp = fresh("s18")
    lane, fleet, info = build(tmp)
    absent = "1234567890123456789012345678901234567890"
    lentries = g(lane, "ls-tree", "HEAD")
    top = subprocess.run(["git", "-C", str(lane), "mktree"],
                         input=lentries + f"\n160000 commit {absent}\tsub\n",
                         capture_output=True, text=True, env=base_env()
                         ).stdout.strip()
    c = subprocess.run(["git", "-C", str(lane), "commit-tree", top, "-p",
                        "HEAD", "-m", "round-1: gitlink"],
                       capture_output=True, text=True,
                       env=base_env(GIT_AUTHOR_DATE="@450 +0000",
                                    GIT_COMMITTER_DATE="@450 +0000")
                       ).stdout.strip()
    g(lane, "reset", "-q", "--hard", c)
    body = body_for(info["required"] + [c], FAKE + "\n")
    republish(fleet, info, body)
    rc, err, defects = audit(lane, fleet)
    lm, lo, _, _ = sets(lane, fleet)
    ok = (absent not in lm and rc == 1
          and defects == [("unresolved-full-hash", FAKE)])
    case("S18-gitlink-entry-is-not-a-missing-object",
         "gitlink oid absent from the missing set; exit 1 finding", ok,
         f"gitlink_in_missing={absent in lm} gitlink_in_opaque={absent in lo} "
         f"rc={rc} defects={defects} err={err!r}")

    # S19 the walk cost on the real fleet repository (read-only)
    fleet_real = Path("/home/vgpnk/Projects/shokunin")
    t0 = time.time()
    roots = M.present_roots(fleet_real)
    t1 = time.time()
    fmissing, fopaque = M.missing_reachable(fleet_real,
                                            g(fleet_real, "rev-parse", "HEAD"))
    t2 = time.time()
    ok = (t2 - t0) < 20
    case("S19-real-fleet-walk-fits-the-timeout", "under 20 s", ok,
         f"roots={len(roots)} present_roots={t1 - t0:.2f}s walks={t2 - t1:.2f}s "
         f"missing={len(fmissing)} opaque={len(fopaque)}")

    print("\n---- summary ----")
    for r in RESULTS:
        print(f"{'OK  ' if r['pass'] else 'FAIL'} {r['case']}")
    failed = [r for r in RESULTS if not r["pass"]]
    print(f"cases={len(RESULTS)} failed={len(failed)}")
    (ROOT / "probe3-results.json").write_text(
        json.dumps(RESULTS, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
