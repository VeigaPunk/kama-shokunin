#!/usr/bin/env python3
"""build_controls.py - build the round-57 seat R57Item24CanonicalBinding control trees
and run every receipt.  Scratch only: all trees live under --scratch; the lane is
read-only and is only ever read through symlinked directories.

Each receipt records: the exact command, the working directory, stdout, stderr, exit.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FIXTURES = os.path.join(LANE, ".ufo/waves/round-57/controls")
AUDIT = "canonical_rows_audit.py"
WITNESS = "b89bdab2cc114735ec5d331c6c610134258f7864"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(name, args, outdir, cwd):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    body = [
        "$ " + " ".join(args),
        "cwd=" + cwd,
        "--- stdout ---",
        p.stdout.rstrip("\n"),
        "--- stderr ---",
        p.stderr.rstrip("\n"),
        "exit=%d" % p.returncode,
    ]
    text = "\n".join(body) + "\n"
    with open(os.path.join(outdir, name + ".out"), "w", encoding="utf-8") as f:
        f.write(text)
    return p.returncode, p.stdout, text


def tree(root, scorecard_text):
    """A mutant tree: one SCORECARD.md plus symlinks to the lane's real directories."""
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    with open(os.path.join(root, "SCORECARD.md"), "w", encoding="utf-8") as f:
        f.write(scorecard_text)
    for d in ("tools", "registry", "corpus", ".ufo"):
        os.symlink(os.path.join(LANE, d), os.path.join(root, d))
    return root


def sub(text, old, new, count=1):
    """Replace exactly `count` occurrences; refuse a silent miss."""
    n = text.count(old)
    if n < count:
        raise SystemExit("edit anchor absent (%d < %d): %r" % (n, count, old[:80]))
    return text.replace(old, new, count)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.scratch, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    audit = os.path.join(here, AUDIT)
    with open(os.path.join(LANE, "SCORECARD.md"), encoding="utf-8") as f:
        lane_sc = f.read()
    with open(os.path.join(FIXTURES, "no-canonical/SCORECARD.md"), encoding="utf-8") as f:
        nocanon_sc = f.read()
    with open(os.path.join(FIXTURES, "canonical-noop/SCORECARD.md"), encoding="utf-8") as f:
        canonnoop_sc = f.read()

    results = []

    # ---- A/B: the lane itself, frozen base and HEAD -----------------------------
    results.append(("lane-base",) + run(
        "lane-base",
        ["python3", audit, "--repo", LANE, "--tip", WITNESS],
        a.out, here))
    head = subprocess.run(["git", "-C", LANE, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    results.append(("lane-head",) + run(
        "lane-head",
        ["python3", audit, "--repo", LANE, "--tip", head, "--witness-tip", WITNESS],
        a.out, here))

    # ---- C/D: the frozen fixtures as committed ----------------------------------
    results.append(("fixture-no-canonical",) + run(
        "fixture-no-canonical",
        ["python3", audit, "--repo", os.path.join(FIXTURES, "no-canonical")],
        a.out, here))
    results.append(("fixture-canonical-noop",) + run(
        "fixture-canonical-noop",
        ["python3", audit, "--repo", os.path.join(FIXTURES, "canonical-noop")],
        a.out, here))

    # ---- E: the omission control, isolated (frozen bytes + a live tree) ---------
    t_nocanon = tree(os.path.join(a.scratch, "tree-no-canonical"), nocanon_sc)
    results.append(("omission-isolated",) + run(
        "omission-isolated",
        ["python3", audit, "--repo", t_nocanon],
        a.out, here))
    # the frozen do-nothing instrument for the canonical question, as committed at
    # the pre-data freeze (it was removed from the worktree while this seat ran)
    results.append(("omission-noop-frozen",) + run(
        "omission-noop-frozen",
        ["git", "-C", LANE, "show",
         "89dc4f52:.ufo/waves/round-57/controls/noop-c2.out"],
        a.out, here))
    # a faithful reproduction of that instrument: it reads nothing and declares met=True
    noop = os.path.join(a.scratch, "noop_canon.py")
    with open(noop, "w", encoding="utf-8") as f:
        f.write('#!/usr/bin/env python3\n'
                '# the frozen do-nothing instrument, reproduced: zero reads of any tree\n'
                'print("control=no-op instrument")\n'
                'print("canonical_table_reads=0")\n'
                'print("self_description_reads=0")\n'
                'print("summary=mismatches=0 maxN=46 met=True")\n')
    results.append(("omission-noop-repro",) + run(
        "omission-noop-repro", ["python3", noop], a.out, here))

    t_canonnoop = tree(os.path.join(a.scratch, "tree-canonical-noop"), canonnoop_sc)
    results.append(("canonical-noop-isolated",) + run(
        "canonical-noop-isolated",
        ["python3", audit, "--repo", t_canonnoop],
        a.out, here))

    # ---- F: drop the newest canonical row, leave every other surface alone -----
    row = ("| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v5` receipt's "
           "server release archive and model from the https URLs its provenance block "
           "records - the model pinned to a 40-hex `/resolve/<commit>/` revision that "
           "the receipt also states as `provenance.model.commit` - verify both sha256 "
           "values before anything is extracted or executed, check the archive and its "
           "member against the asset and server digests before the server starts so a "
           "v5 receipt's `provenance.verified` block is recorded rather than asserted, "
           "re-run the lifecycle from an empty home passing the downloaded archive as "
           "`--server-archive`, hold the rerun server up for an outside observer on "
           "request (`--witness-dir`: `ready.json` names the port and the server "
           "child's pid, the server stays up")
    at = lane_sc.rindex(row)                     # the newest canonical table's row
    lo = lane_sc.rfind("\n", 0, at) + 1
    hi = lane_sc.index("\n", at) + 1
    m1 = lane_sc[:lo] + lane_sc[hi:]
    t_m1 = tree(os.path.join(a.scratch, "tree-m1-drop-row"), m1)
    results.append(("m1-drop-row",) + run(
        "m1-drop-row", ["python3", audit, "--repo", t_m1], a.out, here))

    # ---- G: two omission strengths ---------------------------------------------
    # G1 drops the row wherever the v5 wording carries it: an in-file leg must catch it.
    g1 = "\n".join(ln for ln in lane_sc.split("\n")
                   if not (ln.startswith("| live-receipt-replay |")
                           and "kama-llamacpp-live/v5" in ln))
    g1 = sub(g1, "Eleven capabilities, as in round 48.", "Ten capabilities, as in round 48.")
    g1 = sub(g1, "43, 46, 47 (highest canonical list)", "43, 46 (highest canonical list)")
    t_g1 = tree(os.path.join(a.scratch, "tree-g1-row-drop"), g1)
    results.append(("g1-row-drop",) + run(
        "g1-row-drop", ["python3", audit, "--repo", t_g1], a.out, here))
    # G2 scrubs the row from every capability table and corrects every in-file
    # statement: nothing inside the file can see the loss, only the witness can.
    g2 = "\n".join(ln for ln in lane_sc.split("\n")
                   if not ln.startswith("| live-receipt-replay |"))
    g2 = g2.replace("Eleven capabilities", "Ten capabilities")
    g2 = sub(g2, "43, 46, 47 (highest canonical list)", "43, 46 (highest canonical list)")
    t_g2 = tree(os.path.join(a.scratch, "tree-g2-consistent-omission"), g2)
    results.append(("g2-witness",) + run(
        "g2-witness",
        ["python3", audit, "--repo", t_g2, "--witness-dir", LANE],
        a.out, here))
    results.append(("g2-no-witness",) + run(
        "g2-no-witness", ["python3", audit, "--repo", t_g2], a.out, here))

    # ---- H: a capability cell that claims what its evidence does not contain ----
    # Locate the newest canonical table's row by line index (not by first match) and
    # replace its whole capability cell - and the mirror copy - with vocabulary that
    # no evidence file carries.
    rows = lane_sc.split("\n")
    marks = [i for i, l in enumerate(rows) if "canonical list as of round 49**" in l]
    if len(marks) != 1:
        raise SystemExit("M3: round-49 marker count %d" % len(marks))
    i = marks[0]
    while i < len(rows) and not rows[i].startswith("|"):
        i += 1
    cap_at = None
    while i < len(rows) and rows[i].startswith("|"):
        if rows[i].split("|")[1].strip() == "live-receipt-replay":
            cap_at = i
            break
        i += 1
    if cap_at is None:
        raise SystemExit("M3: no live-receipt-replay row in the round-49 canonical table")
    old_cap = rows[cap_at].split("|")[2].strip()
    new_cap = ("Perform an `--orbital-rewrap` sweep with a `polarised-tally` "
               "`frobnicate.json` seal")
    if lane_sc.count(old_cap) < 2:
        raise SystemExit("M3: capability-cell anchor count %d" % lane_sc.count(old_cap))
    m3 = lane_sc.replace(old_cap, new_cap)
    for lit in ("orbital-rewrap", "polarised-tally", "frobnicate.json"):
        if any(lit.lower() in open(os.path.join(LANE, p), encoding="utf-8",
                                   errors="replace").read().lower()
               for p in ("tools/kama-live-replay.py", "tools/kama-llamacpp-live.py")):
            raise SystemExit("M3: foreign literal %r occurs in the evidence" % lit)
    t_m3 = tree(os.path.join(a.scratch, "tree-m3-content"), m3)
    results.append(("m3-content",) + run(
        "m3-content", ["python3", audit, "--repo", t_m3], a.out, here))

    # ---- I: an evidence pointer that is not there ------------------------------
    m4 = lane_sc.replace("| `tools/pin-watch.py`; `registry/engine-pins.tsv`; "
                         "`corpus/knowledge/engine-pin-watch.md` |",
                         "| `tools/pin-watch-missing.py`; `registry/engine-pins.tsv`; "
                         "`corpus/knowledge/engine-pin-watch.md` |")
    t_m4 = tree(os.path.join(a.scratch, "tree-m4-evidence"), m4)
    results.append(("m4-evidence",) + run(
        "m4-evidence", ["python3", audit, "--repo", t_m4], a.out, here))

    # ---- J: the generation marker moved without its references ----------------
    m5 = sub(lane_sc, "**Capabilities \u2014 canonical list as of round 49**",
             "**Capabilities \u2014 canonical list as of round 50**")
    t_m5 = tree(os.path.join(a.scratch, "tree-m5-generation"), m5)
    results.append(("m5-generation",) + run(
        "m5-generation", ["python3", audit, "--repo", t_m5], a.out, here))

    # ---- K: a duplicated canonical row -----------------------------------------
    dup = lane_sc[lo:hi - 1]
    m6 = lane_sc[:lo] + dup + "\n" + lane_sc[lo:]
    t_m6 = tree(os.path.join(a.scratch, "tree-m6-duplicate"), m6)
    results.append(("m6-duplicate",) + run(
        "m6-duplicate", ["python3", audit, "--repo", t_m6], a.out, here))

    # ---- L: repair the one divergence the audit found; the verdict must clear ---
    # the head mirror row is the only cell without the round-49 pointer; restore it
    head_ev = "`tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`; `.ufo/waves/round-48/c2/live/receipt-1.json`"
    m7 = sub(lane_sc, head_ev,
             "`tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`; "
             "`.ufo/waves/round-49/measured/c1-build.out`; `.ufo/waves/round-48/c2/live/receipt-1.json`")
    t_m7 = tree(os.path.join(a.scratch, "tree-m7-mirror-repaired"), m7)
    results.append(("m7-mirror-repaired",) + run(
        "m7-mirror-repaired", ["python3", audit, "--repo", t_m7], a.out, here))

    # ---- M: distinct case 45, second implementation ----------------------------
    case = os.path.join(here, "case45_independent.py")
    results.append(("case45-lane-base",) + run(
        "case45-lane-base", ["python3", case, "--repo", LANE, "--tip", WITNESS],
        a.out, here))
    results.append(("case45-lane-head",) + run(
        "case45-lane-head", ["python3", case, "--repo", LANE, "--tip", head],
        a.out, here))
    results.append(("case45-omission",) + run(
        "case45-omission", ["python3", case, "--repo", t_nocanon], a.out, here))
    results.append(("case45-m1-drop-row",) + run(
        "case45-m1-drop-row", ["python3", case, "--repo", t_m1], a.out, here))

    summary = ["tool_sha256=%s" % sha(audit),
               "case45_sha256=%s" % sha(os.path.join(here, "case45_independent.py")),
               "lane_head=%s" % head,
               "witness_tip=%s" % WITNESS]
    for name, rc, out, _text in results:
        first = [l for l in out.split("\n")
                 if l.startswith(("rows=", "CASE45", "control=", "summary="))]
        summary.append("%-26s exit=%d %s" % (name, rc, first[0] if first else out.split("\n")[0][:120]))
    with open(os.path.join(a.out, "SUMMARY.out"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
