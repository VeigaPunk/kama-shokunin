#!/usr/bin/env python3
"""xstab_fixture.py - round-48 X1Stable: does an event's graded/ungraded count change
with `--to` under append-only-audit.py v3 (exempt region eligibility is a window maximum)?

Builds a throwaway repo (asserted to be its own toplevel) and runs the lane tool at four
tips of the SAME history.  Expectations are by construction (line counts below), not read
back from the tool:

  score.md at c1 (parent of the event):
      "# score"           section None
      "## Body"           section "## Body"   (heading counts: 11 lines in Body)
      b01..b10            section "## Body"   (10)
      "## Axes"           section "## Axes"   (heading counts: 17 lines in Axes)
      a01..a16            section "## Axes"   (16)
  c2  deletes b01..b10 and a01..a14 = 24 lines (10 Body + 14 Axes) >= threshold 20.
      Axes count at c2 = heading + a15 + a16 = 3 < 17  -> Axes NOT eligible -> graded 24.
  c3  re-inserts b01..b10 byte-exact (Body).  Axes still 3 < 17 -> graded 24, restored 24.
  c4  appends a17..a30 (14 lines) -> Axes count 3 + 14 = 17 >= 17 -> Axes ELIGIBLE
      -> graded 10 (Body only), ungraded 14, held 10 (Body lines restored).
  c5  deletes a17..a30 again (14 lines, sub-threshold: no new event).  Window maximum keeps
      Axes eligible -> graded 10, ungraded 14, held 10: still excused.

Usage: xstab_fixture.py --tool <append-only-audit.py> --dir <empty dir under scratch>
Writes fixture-contract.tsv beside the report output; prints a table and the counter's
stable-leg field comparison between c3 and c4.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HEADER = "path\trule\tdeclared_at\tregion\tnote"
NOTES = ["# notes",
         "score.md is append-only (round-48 X1Stable fixture).",
         "The ## Axes head of score.md is re-derived in place."]
CONTRACT = [HEADER, "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@NOTES.md:3\tfixture"]


def b(n):
    return [f"b{i:02d}" for i in range(1, n + 1)]


def a(lo, hi):
    return [f"a{i:02d}" for i in range(lo, hi + 1)]


def git(d, *args, env_ok=True):
    return subprocess.run(["git", "-C", d, *args], capture_output=True, text=True, check=True).stdout


def commit(d, files, msg):
    for name, lines in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(p) else None
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    git(d, "add", "-A")
    git(d, "-c", "user.name=xstab", "-c", "user.email=xstab@invalid",
        "commit", "-q", "-m", msg)
    return git(d, "rev-parse", "HEAD").strip()


def run(tool, d, rev, contract):
    p = subprocess.run([sys.executable, tool, "--repo", d, "--to", rev,
                        "--contract", contract, "--json"], capture_output=True, text=True)
    return json.loads(p.stdout), p.returncode, subprocess.run(
        [sys.executable, tool, "--repo", d, "--to", rev, "--contract", contract],
        capture_output=True).returncode


def case_b(tool, d, contract):
    """restored_max falls as the tip advances (24 -> 10): the exempt section is regrown with
    NEW text after the deleted texts were restored outside it (the preregistered whole-file
    multiset limit).  Parent Axes count = heading + a01..a39 = 40; the event leaves 26."""
    git(d, "init", "-q")
    top = git(d, "rev-parse", "--show-toplevel").strip()
    assert top == d, f"toplevel {top} != fixture {d}"
    c1 = commit(d, {"NOTES.md": NOTES, "score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(1, 39)}, "c1 seed")
    c2 = commit(d, {"score.md": ["# score", "## Body", "## Axes"] + a(15, 39)},
                "c2 event: delete 24 (10 Body + 14 Axes), Axes 26 < 40")
    c3 = commit(d, {"score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(15, 39)
                    + ["## Cited"] + a(1, 14)}, "c3 restore all 24 texts outside the exempt section")
    c4 = commit(d, {"score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(15, 39) + ["x%02d" % i for i in range(1, 15)]
                    + ["## Cited"] + a(1, 14)}, "c4 regrow Axes to 40 with new text")
    with open(contract, "w", encoding="utf-8") as fh:
        fh.write("\n".join(CONTRACT) + "\n")
    print("case B: restored_max and graded/ungraded as the tip moves")
    print("tip tag  tip       event    deleted graded ungraded restored_max held_at_to status    rc restored_best")
    js = {}
    for tag, rev in (("c2", c2), ("c3", c3), ("c4", c4)):
        j, _, rc = run(tool, d, rev, contract)
        js[tag] = (j, rc)
        e = j["events"][0]
        print(f"{tag:7s} {rev[:8]}  {e['commit'][:8]}  {e['deleted']:7d} {e['graded']:6d} {e['ungraded']:8d} "
              f"{e['restored_max']:12d} {e['held_at_to']:10d} {e['status']:9s} {rc:2d} {(e['restored_best'] or '-')[:8]}")
    a_, b_ = js["c3"][0]["events"][0], js["c4"][0]["events"][0]
    print(f"restored_max c3={a_['restored_max']} -> c4={b_['restored_max']} (falls: "
          f"{b_['restored_max'] < a_['restored_max']}); graded {a_['graded']} -> {b_['graded']}; "
          f"ungraded {a_['ungraded']} -> {b_['ungraded']}")
    return {"commits": {"c1": c1, "c2": c2, "c3": c3, "c4": c4},
            "runs": {t: js[t][0] for t in js}, "rc": {t: js[t][1] for t in js}, "toplevel": top}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--contract", required=True)
    ap.add_argument("--case-b-dir")
    ap.add_argument("--case-b-contract")
    args = ap.parse_args()
    if args.case_b_dir:
        out = case_b(args.tool, os.path.abspath(args.case_b_dir), args.case_b_contract)
        with open(os.path.join(os.path.dirname(args.case_b_contract), "xstab-fixture-b.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print(f"case B toplevel={out['toplevel']} commits={out['commits']}")
        return
    d = os.path.abspath(args.dir)
    if os.path.exists(d) and os.listdir(d):
        sys.exit(f"refusing non-empty dir {d}")
    os.makedirs(d, exist_ok=True)
    git(d, "init", "-q")
    top = git(d, "rev-parse", "--show-toplevel").strip()
    assert top == d, f"toplevel {top} != fixture {d}"

    c1 = commit(d, {"NOTES.md": NOTES, "score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(1, 16)},
                "c1 seed")
    c2 = commit(d, {"score.md": ["# score", "## Body", "## Axes"] + a(15, 16)}, "c2 event: delete 24 (10 Body + 14 Axes)")
    c3 = commit(d, {"score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(15, 16)}, "c3 restore the 10 Body lines")
    c4 = commit(d, {"score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(15, 30)}, "c4 regrow Axes to 17 (14 new lines)")
    c5 = commit(d, {"score.md": ["# score", "## Body"] + b(10) + ["## Axes"] + a(15, 16)}, "c5 gut Axes again (14 lines, sub-threshold)")

    with open(args.contract, "w", encoding="utf-8") as fh:
        fh.write("\n".join(CONTRACT) + "\n")

    rows, js = [], {}
    for tag, rev in (("c2", c2), ("c3", c3), ("c4", c4), ("c5", c5)):
        p = subprocess.run([sys.executable, args.tool, "--repo", d, "--to", rev,
                            "--contract", args.contract, "--json"], capture_output=True, text=True)
        j = json.loads(p.stdout)
        js[tag] = j
        for e in j["events"]:
            rows.append((tag, rev[:8], e["commit"][:8], e["file"], e["deleted"], e["graded"],
                         e["ungraded"], e["restored_max"], e["held_at_to"], e["status"], p.returncode,
                         (e["restored_best"] or "-")[:8]))
    print("tip tag  tip       event    file       deleted graded ungraded restored_max held_at_to status      rc restored_best")
    for r in rows:
        print(f"{r[0]:7s} {r[1]}  {r[2]}  {r[3]:9s} {r[4]:7d} {r[5]:6d} {r[6]:8d} {r[7]:12d} {r[8]:10d} {r[9]:11s} {r[10]:2d} {r[11]}")

    # the counter's stable-leg field predicate (tools/round48-append-audit-v3-check.py:747-758)
    FIELDS = ("deleted", "graded", "ungraded", "restored_max", "restored_best")
    base = {(e["commit"], e["file"]): e for e in js["c3"]["events"]}
    tip = {(e["commit"], e["file"]): e for e in js["c4"]["events"]}
    for k, e in base.items():
        t = tip.get(k)
        diff = {f: (e.get(f), None if t is None else t.get(f)) for f in FIELDS
                if t is None or t.get(f) != e.get(f)}
        print(f"\nstable-leg predicate base=c3 tip=c4 event {k[0][:8]} {k[1]}: "
              f"{'CHANGED -> stable=0' if diff else 'equal -> stable=1'}")
        for f, (x, y) in diff.items():
            print(f"  {f}: base={x} tip={y}")
    # monotonicity of ungraded over the four tips
    us = [(t, js[t]["events"][0]["ungraded"]) for t in ("c2", "c3", "c4", "c5")]
    gs = [(t, js[t]["events"][0]["graded"]) for t in ("c2", "c3", "c4", "c5")]
    print(f"\nungraded by tip: {us}  non-decreasing={all(us[i][1] <= us[i + 1][1] for i in range(3))}")
    print(f"graded   by tip: {gs}  non-increasing={all(gs[i][1] >= gs[i + 1][1] for i in range(3))}")
    print(f"exit codes: " + " ".join(f"{t}={subprocess.run([sys.executable, args.tool, '--repo', d, '--to', r, '--contract', args.contract], capture_output=True).returncode}"
                                    for t, r in (("c2", c2), ("c3", c3), ("c4", c4), ("c5", c5))))
    with open(os.path.join(os.path.dirname(args.contract), "xstab-fixture.json"), "w", encoding="utf-8") as fh:
        json.dump({"commits": {"c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5}, "runs": js}, fh, indent=1)
    print(f"\ncommits c1={c1} c2={c2} c3={c3} c4={c4} c5={c5}")
    print(f"fixture toplevel={top}")


if __name__ == "__main__":
    main()
