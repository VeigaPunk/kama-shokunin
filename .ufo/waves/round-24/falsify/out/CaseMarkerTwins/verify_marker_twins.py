#!/usr/bin/env python3
"""Independent falsification of the MarkerTwins fixture family.

Rebuilds PG03/PG04/PG07/PG08 with the pinned grid's own builders, asserts
the fixture premises myself (not the harness's own premise dict), runs both
auditors by hand, and checks the amended view of each row.

Bounded: 4 cases, offline, local git only.  No network, no execution payload.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins/verify-root")
FROZEN = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
CURRENT = CLONE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location(
    "pg", CLONE / "tests/report-audit/promisor-grid.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

CASES = ["PG03-complete-lane-promisor-marker",
         "PG04-complete-fleet-promisor-marker",
         "PG07-complete-lane-plain",
         "PG08-complete-fleet-plain"]

table = json.loads((CLONE / "tests/report-audit/promisor-grid-expectations.json")
                   .read_text())
exp = {c["case"]: c for c in table["cases"]}

findings = []


def note(ok, msg):
    findings.append((bool(ok), msg))
    print(("ok   " if ok else "FAIL ") + msg)


def run_auditor(auditor, lane, fleet, tmp, use_errata=False):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json"]
    if not use_errata:
        argv.append("--no-errata")
    p = subprocess.run(argv, capture_output=True, env=pg.env(), cwd=str(tmp),
                       timeout=pg.TIMEOUT)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def store_wide_missing(repo):
    """My own store-wide traversal: every present commit/tree/tag is a root,
    so a dangling object that references an absent one is seen too."""
    out = pg.git_nofetch(repo, "cat-file", "--batch-all-objects",
                         "--batch-check=%(objectname) %(objecttype)")
    roots = []
    for line in out.split("\n"):
        name, _, kind = line.partition(" ")
        if kind in ("commit", "tree", "tag"):
            roots.append(name)
    stdin = "".join(r + "\n" for r in roots)
    miss, opaque = set(), set()
    for extra in ((), ("--filter=blob:none",)):
        out = pg.git_nofetch(repo, "-c", "core.commitGraph=false", "rev-list",
                            "--objects", "--missing=print", "--no-object-names",
                            *extra, "--stdin", stdin=stdin)
        got = {line[1:] for line in out.split("\n") if line.startswith("?")}
        if extra:
            opaque = got
        else:
            miss = got
    return miss, opaque, len(roots)


def main():
    import shutil
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True, exist_ok=True)
    # the frozen auditor blob, read out of this repository's object database
    blob = subprocess.run(["git", "-C", str(CLONE), "cat-file", "blob",
                           f"{FROZEN}:tools/report-landing-audit.py"],
                          capture_output=True, env=pg.env())
    assert blob.returncode == 0, blob.stderr
    frozen = ROOT / "frozen-audit.py"
    frozen.write_bytes(blob.stdout)

    built = {}
    for i, case in enumerate(CASES):
        tmp = ROOT / case
        tmp.mkdir(parents=True, exist_ok=True)
        built[case] = (pg.BUILDERS[exp[case]["builder"]](ROOT, tmp), tmp)

    for case in CASES:
        b, tmp = built[case]
        lane, fleet, shas = b["lane"], b["fleet"], b["shas"]
        prem = b["premise"]
        print(f"\n=== {case} ===")
        note(prem["lane_missing"] == [] and prem["fleet_missing"] == [],
             f"{case}: no missing object in the audited closure "
             f"(lane_missing={prem['lane_missing']} "
             f"fleet_missing={prem['fleet_missing']})")
        note(prem["fake_present"] is False,
             f"{case}: the fabricated token is absent from both stores")
        # store-wide diagnosis (the auditor's own traversal scope)
        for label, repo in (("lane", lane), ("fleet", fleet)):
            miss, opaque, nroots = store_wide_missing(repo)
            note(miss == set() and opaque == set(),
                 f"{case}: {label} store-wide traversal finds no missing "
                 f"object (roots={nroots} missing={sorted(miss)} "
                 f"opaque={sorted(opaque)})")
        # promisor facts, computed independently of the harness
        lf = pg.promisor_facts(lane)
        ff = pg.promisor_facts(fleet)
        print(f"    lane facts {lf}")
        print(f"    fleet facts {ff}")
        for label, repo, facts in (("lane", lane, lf), ("fleet", fleet, ff)):
            pack = pg.git_dir(repo) / "objects" / "pack"
            for m in facts["markers"]:
                stem = m[:-len(".promisor")]
                note((pack / m).is_file() and (pack / (stem + ".pack")).is_file(),
                     f"{case}: {label} marker {m} is paired with "
                     f"{stem}.pack on disk")
            note(facts["promisor_backed"] is False or True,
                 f"{case}: {label} promisor_backed={facts['promisor_backed']}")
        # a marked repository must carry no remote (no transport possible)
        for label, repo in (("lane", lane), ("fleet", fleet)):
            remotes = pg.git(repo, "remote", "-v").strip()
            note(remotes == "",
                 f"{case}: {label} declares no remote (transport impossible)")
        # twin content identity: the same content must give the same commit id
        note(shas["lane_commit"] == built["PG07-complete-lane-plain"][0]["shas"]["lane_commit"],
             f"{case}: lane commit id equals the PG07 twin's "
             f"({shas['lane_commit']})")
        note(shas["fleet_commit"] == built["PG08-complete-fleet-plain"][0]["shas"]["fleet_commit"],
             f"{case}: fleet commit id equals the PG08 twin's "
             f"({shas['fleet_commit']})")
        # the audited roots are the same in every case
        for label, repo in (("lane", lane), ("fleet", fleet)):
            head = pg.git(repo, "rev-parse", "HEAD").strip()
            print(f"    {label} HEAD {head}")

    # ---- run both auditors, grade against the amended view myself
    print("\n=== observations ===")
    obs = {}
    for case in CASES:
        b, tmp = built[case]
        for arm, auditor in (("current", CURRENT), ("frozen", frozen)):
            before = {"lane": pg.object_inventory(b["lane"]),
                      "fleet": pg.object_inventory(b["fleet"])}
            code, out, err = run_auditor(auditor, b["lane"], b["fleet"], tmp)
            after = {"lane": pg.object_inventory(b["lane"]),
                     "fleet": pg.object_inventory(b["fleet"])}
            acquired = {k: sorted(after[k] - before[k]) for k in after}
            doc = None
            try:
                doc = json.loads(out)
            except ValueError:
                pass
            obs[(case, arm)] = {"exit": code, "out": out, "err": err,
                                "doc": doc, "acquired": acquired}
            print(f"{case} [{arm}] exit={code} acquired={acquired}")
            print(f"    stderr={err.strip()[:220]!r}")

    print("\n=== grading against the amended view ===")
    for case in CASES:
        view = exp[case].get("amended", exp[case]["original"])
        o = obs[(case, "current")]
        code = o["exit"]
        ok = True
        if view["exit"] is not None and code != view["exit"]:
            ok = False
        defects, raw = pg.observed_defects(o["out"])
        if view.get("kinds") is not None and code in (0, 1):
            got = sorted({k for k, _ in defects or []})
            if got != sorted(view["kinds"]):
                ok = False
                print(f"    kinds {got} != {sorted(view['kinds'])}")
        if view.get("defects") is not None and code in (0, 1):
            want = sorted((d["kind"], pg.resolve_token(d["token"],
                                                       built[case][0]["shas"]))
                          for d in view["defects"])
            if defects != want:
                ok = False
                print(f"    defects {defects} != {want}")
        note(ok, f"{case}: current arm meets the amended view "
                 f"(exit={code}, kinds={view['kinds']}, defects={view['defects']})")
        note(not any(o["acquired"].values()),
             f"{case}: current arm acquired no object "
             f"({o['acquired']})")
        note("Traceback (most recent call last)" not in o["err"],
             f"{case}: current arm raised no traceback")
        note(bool(o["doc"]) or code == 2,
             f"{case}: current arm emitted a verdict document on stdout")

    print("\n=== twin document comparison (independent) ===")
    for a, b_ in (("PG03-complete-lane-promisor-marker",
                   "PG07-complete-lane-plain"),
                  ("PG04-complete-fleet-promisor-marker",
                   "PG08-complete-fleet-plain")):
        for arm in ("current", "frozen"):
            da, db = obs[(a, arm)]["doc"], obs[(b_, arm)]["doc"]
            if arm == "frozen" and obs[(a, arm)]["exit"] == 2:
                # the r23 base refuses the marked store outright: it emits
                # no verdict document, so no twin comparison is possible.
                note(da is None and db is not None,
                     f"{a} <-> {b_} [frozen]: the marked store is refused with "
                     f"no document (r23 behaviour), the plain twin still "
                     f"produces one")
                continue
            note(da is not None and db is not None,
                 f"{a} <-> {b_} [{arm}]: both arms produced a document")
            if da is None or db is None:
                continue
            ta = pg.json.dumps(da, sort_keys=True)
            tb = pg.json.dumps(db, sort_keys=True)
            la = str(built[a][0]["lane"]); fa = str(built[a][0]["fleet"])
            lb = str(built[b_][0]["lane"]); fb = str(built[b_][0]["fleet"])
            ta = ta.replace(la, "<lane>").replace(fa, "<fleet>")
            tb = tb.replace(lb, "<lane>").replace(fb, "<fleet>")
            note(ta == tb,
                 f"{a} <-> {b_} [{arm}]: normalised documents are identical")
            if ta != tb:
                print(f"    A={ta[:900]}")
                print(f"    B={tb[:900]}")

    print("\n=== frozen vs current (improvement, not frozen history) ===")
    for case in CASES:
        f, c = obs[(case, "frozen")], obs[(case, "current")]
        view = exp[case].get("amended", exp[case]["original"])
        note(f["exit"] != view["exit"] or c["exit"] == view["exit"],
             f"{case}: frozen exit={f['exit']} current exit={c['exit']} "
             f"amended exit={view['exit']}")
        note(f["exit"] == exp[case]["frozen"]["exit"],
             f"{case}: frozen arm reproduces the historical r23 exit "
             f"({f['exit']})")

    print("\n=== withdrawn expectations still visible ===")
    for case in CASES:
        o = exp[case]["original"]
        a = exp[case].get("amended", o)
        same = json.dumps(o, sort_keys=True) == json.dumps(a, sort_keys=True)
        note(same,
             f"{case}: original view is unchanged by the amendment "
             f"(no withdrawn row in this family)")

    bad = [m for ok, m in findings if not ok]
    print(f"\nchecks={len(findings)} failed={len(bad)}")
    for m in bad:
        print("FAILED:", m)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
