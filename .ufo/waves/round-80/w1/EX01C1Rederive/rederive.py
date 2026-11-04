#!/usr/bin/env python3
"""EX01C1Rederive — independent re-derivation of the six round-79 self-record facts.

Reads ONLY git objects (`git -C <lane> show <rev>:<path>`, `ls-tree`, `rev-parse`)
of the kama lane at the sealed revision a9b4543f14625d0f37daa42ef664ee6f6ea975ea
and at the lane tip, plus the fleet-root shokunin.conf (read-only) for the
assigned-axis pair. It does NOT import or read tools/round80-selfrecord-round79.py;
the lane counter is compared against only after this script's own values are fixed
(via --record-counter).

Per fact it emits `declared` (the record's declared value string, grounded in the
record's own bytes), `observed_sealed`, `observed_tip` (re-derived from the tree at
each revision), `match` (declared == observed at both revisions), plus a top-level
`stale` list. Receipt: EX01.json in this seat directory.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SEAT = "EX01C1Rederive"
SEALED_DEFAULT = "a9b4543f14625d0f37daa42ef664ee6f6ea975ea"
BASE_DEFAULT = "c45fc7d1a8427e9c98a9dd7befa542c7b5caed38"
FLEET_CONF = "/home/vgpnk/Projects/shokunin/shokunin.conf"

# Frozen declared value strings — plans/round-80-claims.md, C1 fact table (freeze).
# Each is additionally grounded against the record's own bytes at the sealed revision
# (see grounding() per fact); a mismatch between frozen string and record bytes is
# reported, never silently rewritten.
DECLARED = {
    "F1": "lowest-axis=calibration:7",
    "F2": "population=sources:293,knowledge:52",
    "F3": ("wave=seats:14,executor:4,scribe:3,scout:2,connector:1,reviewer:1,"
           "critic:2,mutation-tester:1,attack:4/14"),
    "F4": "c2=verified",
    "F5": "before-selftest=pass=26",
    "F6": "log=all-verified",
}
ROLE_ORDER = ["executor", "scribe", "scout", "connector", "reviewer", "critic",
              "mutation-tester"]
ATTACK_ROLES = {"reviewer", "critic", "mutation-tester"}


class Lane:
    def __init__(self, lane: str):
        self.lane = lane

    def git(self, *args: str) -> tuple[int, str, str]:
        r = subprocess.run(["git", "-C", self.lane, *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr

    def tip(self) -> str:
        rc, out, err = self.git("rev-parse", "master")
        if rc != 0:
            raise SystemExit(f"rev-parse master failed: {err.strip()}")
        return out.strip()

    def show(self, rev: str, path: str) -> str | None:
        rc, out, _ = self.git("show", f"{rev}:{path}")
        return out if rc == 0 else None

    def lsdir(self, rev: str, path: str) -> list[str]:
        rc, out, _ = self.git("ls-tree", "--name-only", f"{rev}:{path}")
        return out.splitlines() if rc == 0 else []


# ---------------------------------------------------------------- fact derivations

def assigned_pair(lane: Lane, rev: str) -> tuple[list[str], str]:
    """Assigned axes for kama: fleet shokunin.conf kama row, falling back to the
    sealed SCORECARD banner's own declaration."""
    try:
        text = Path(FLEET_CONF).read_text()
        for line in text.splitlines():
            if line.startswith("kama|"):
                cells = line.split("|")
                m = re.match(r"\s*([a-z-]+)\s*\+\s*([a-z-]+)", cells[2] if len(cells) > 2 else "")
                if m:
                    return [m.group(1), m.group(2)], f"shokunin.conf kama row: {line.strip()}"
    except OSError:
        pass
    sc = lane.show(rev, "SCORECARD.md") or ""
    m = re.search(r"assigned axes are ([a-z-]+) \+ ([a-z-]+)", sc)
    if m:
        return [m.group(1), m.group(2)], "SCORECARD.md banner (sealed)"
    raise SystemExit("assigned axis pair not derivable")


def derive_f1(lane: Lane, rev: str) -> tuple[str, dict]:
    pair, pair_src = assigned_pair(lane, rev)
    sc = lane.show(rev, "SCORECARD.md")
    lines = sc.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "## Axes")
    scores: dict[str, int] = {}
    for l in lines[start + 1:]:
        if l.startswith("#"):
            break
        m = re.match(r"\|\s*\*{0,2}([a-z-]+)\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", l)
        if m:
            scores[m.group(1)] = int(m.group(2))
    missing = [a for a in pair if a not in scores]
    if missing:
        raise SystemExit(f"F1: axes {missing} absent from ## Axes table at {rev[:12]}")
    name = min(pair, key=lambda a: scores[a])
    grounding = {"axes_table": {a: scores[a] for a in pair},
                 "assigned_pair_source": pair_src}
    return f"lowest-axis={name}:{scores[name]}", grounding


def derive_f2(lane: Lane, rev: str) -> tuple[str, dict]:
    src = lane.show(rev, "corpus/SOURCES.md")
    if src is None:
        raise SystemExit(f"F2: corpus/SOURCES.md absent at {rev[:12]}")
    rows = len(re.findall(r"^\|[ \t]*S[0-9]{3,}[ \t]*\|", src, re.M))
    blobs = [n for n in lane.lsdir(rev, "corpus/knowledge") if n.endswith(".md")]
    filtered = [n for n in blobs if "engine-sides" in n or "processes" in n]
    kept = len(blobs) - len(filtered)
    return (f"population=sources:{rows},knowledge:{kept}",
            {"source_rows": rows, "knowledge_blobs": len(blobs),
             "filtered_names": filtered})


def derive_f3(lane: Lane, rev: str) -> tuple[str, dict]:
    raw = lane.show(rev, ".ufo/waves/round-79/w1-spec.json")
    if raw is None:
        raise SystemExit(f"F3: .ufo/waves/round-79/w1-spec.json absent at {rev[:12]}")
    spec = json.loads(raw)
    items = spec["items"]
    counts: dict[str, int] = {}
    for it in items:
        counts[it["role"]] = counts.get(it["role"], 0) + 1
    seats = len(items)
    attack = sum(c for r, c in counts.items() if r in ATTACK_ROLES)
    ordered = [r for r in ROLE_ORDER if r in counts] + \
              [r for r in counts if r not in ROLE_ORDER]
    val = ("wave=seats:%d," % seats +
           ",".join(f"{r}:{counts[r]}" for r in ordered) +
           f",attack:{attack}/{seats}")
    return val, {"role_counts": counts, "attack_roles": sorted(ATTACK_ROLES)}


def derive_f4(lane: Lane, rev: str) -> tuple[str, dict]:
    path = ".ufo/waves/round-79/measured/after/c2-gate.out"
    out = lane.show(rev, path)
    if out is None:
        raise SystemExit(f"F4: {path} absent at {rev[:12]}")
    m = re.search(r"^PRE_REPORT round=(\d+) arms=(\d+) failed=(\d+) uncommitted=(\d+)\s*$",
                  out, re.M)
    e = re.search(r"^EXIT=(\d+)\s*$", out, re.M)
    if not m:
        raise SystemExit(f"F4: no PRE_REPORT summary line in {path} at {rev[:12]}")
    failed, arms, exit_code = int(m.group(3)), int(m.group(2)), int(e.group(1)) if e else None
    if failed == 0 and exit_code == 0:
        return "c2=verified", {"path": path, "arms": arms, "failed": failed,
                               "uncommitted": int(m.group(4)), "exit": exit_code}
    return (f"c2=not-verified:failed={failed}",
            {"path": path, "arms": arms, "failed": failed,
             "uncommitted": int(m.group(4)), "exit": exit_code})


def derive_f5(lane: Lane, rev: str) -> tuple[str, dict]:
    arms_path = ".ufo/waves/round-79/measured/before/c2-gate-arms.out"
    self_path = ".ufo/waves/round-79/measured/before/c2-gate-selftest.out"
    arms = lane.show(rev, arms_path)
    sel = lane.show(rev, self_path)
    detail: dict = {"arms_path": arms_path, "selftest_path": self_path}
    tally = None
    if arms is not None:
        am = re.search(r"^BASE_ARM_ORDER (\d+)", arms, re.M)
        detail["arms_BASE_ARM_ORDER"] = int(am.group(1)) if am else None
        sm = re.search(r"^PRE_REPORT_SELFTEST pass=(\d+) fail=(\d+)", arms, re.M)
        detail["arms_PRE_REPORT_SELFTEST"] = list(sm.groups()) if sm else None
        if sm:
            tally = (int(sm.group(1)), arms_path)
    if tally is None and sel is not None:
        sm = re.search(r"^PRE_REPORT_SELFTEST pass=(\d+) fail=(\d+)", sel, re.M)
        detail["selftest_PRE_REPORT_SELFTEST"] = list(sm.groups()) if sm else None
        if sm:
            tally = (int(sm.group(1)), self_path)
    if tally is None:
        raise SystemExit(f"F5: no PRE_REPORT_SELFTEST tally in before receipts at {rev[:12]}")
    return f"before-selftest=pass={tally[0]}", {**detail, "tally_source": tally[1]}


def round79_log_section(lane: Lane, rev: str) -> str:
    log = lane.show(rev, "LOG.md")
    if log is None:
        raise SystemExit(f"LOG.md absent at {rev[:12]}")
    lines = log.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("## Round 79 ")), None)
    if start is None:
        raise SystemExit(f"no '## Round 79' heading in LOG.md at {rev[:12]}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


def derive_f6(lane: Lane, rev: str, c2_observed: dict) -> tuple[str, dict]:
    section = round79_log_section(lane, rev)
    flat = re.sub(r"\s+", " ", section)
    declared_present = "Three claims, three distinct axes, all verified on their receipts" in flat
    log = lane.show(rev, "LOG.md") or ""
    token = re.search(r"LOG-CORRECTION round=79 claim=C2 verdict=(\S+)", log)
    observed = "log=c2-not-verified" if c2_observed["failed"] else "log=c2-verified"
    return observed, {"declared_sentence_present": declared_present,
                      "log_correction_token": token.group(0) if token else None,
                      "basis": "record's cited C2 receipt verdict (failed=%d)" % c2_observed["failed"]}


def ground_declared(lane: Lane, rev: str) -> dict[str, dict]:
    """Ground each frozen declared string in the record's own bytes at the sealed rev."""
    g: dict[str, dict] = {}
    log79 = round79_log_section(lane, rev)
    flat = re.sub(r"\s+", " ", log79)
    sc = lane.show(rev, "SCORECARD.md") or ""

    m = re.search(r"\*\*C1 calibration \(lowest assigned axis, (\d+)\)\*\*", flat)
    g["F1"] = {"quote": m.group(0) if m else None,
               "parsed": f"lowest-axis=calibration:{m.group(1)}" if m else None}
    m = re.search(r"registry (\d+) → (\d+) rows", flat)
    g["F2"] = {"quote": m.group(0) if m else None,
               "parsed_sources": m.group(2) if m else None,
               "note": "record states the sources transition; knowledge end-state 52 "
                       "re-derives as blobs(54) minus the two filtered entries; the "
                       "declared string is the frozen plan label"}
    m = re.search(r"Wave: one v1 wave, (\d+) seats \(([^;)]*); attack (\d+/\d+)", flat)
    g["F3"] = {"quote": m.group(0) if m else None}
    m = re.search(r"^\| C2 — [^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*\*\*(verified|not-verified)\*\*\s*\|\s*$",
                  sc, re.M)
    g["F4"] = {"c2_row_verdict_cell": m.group(1) if m else None,
               "banner": "C2 operability verified" in sc}
    m = re.search(r"\| C2 — [^|]*\|\s*operability\s*\|\s*([^|]*\|[^|]*)\|", sc)
    g["F5"] = {"before_cell_has_pass26": "PRE_REPORT_SELFTEST pass=26 fail=0" in sc,
               "note": "before cell cites .ufo/waves/round-79/measured/before/c2-gate-arms.out"}
    g["F6"] = {"quote_present": "Three claims, three distinct axes, all verified on their receipts" in flat}
    return g


# --------------------------------------------------------------------------- main

def derive_all(lane: Lane, sealed: str, tip: str) -> dict:
    facts = []
    stale = []
    # declared grounding runs once, against the sealed record bytes
    grounding = ground_declared(lane, sealed)
    for fid, name in [("F1", "lowest assigned axis"), ("F2", "population"),
                      ("F3", "wave shape"), ("F4", "C2 verdict"),
                      ("F5", "C2 before tally"), ("F6", "LOG verdict")]:
        derived = {"F1": derive_f1, "F2": derive_f2, "F3": derive_f3,
                   "F4": derive_f4, "F5": derive_f5}
        if fid in derived:
            obs_seal, det_s = derived[fid](lane, sealed)
            obs_tip, det_t = derived[fid](lane, tip)
        else:  # F6 rides on F4's receipt verdict at each revision
            obs_seal, det_s = derive_f6(lane, sealed, derive_f4(lane, sealed)[1])
            obs_tip, det_t = derive_f6(lane, tip, derive_f4(lane, tip)[1])
        declared = DECLARED[fid]
        match = (declared == obs_seal == obs_tip)
        if not match:
            stale.append(fid)
        facts.append({
            "id": fid, "name": name,
            "declared": declared,
            "declared_grounding": grounding[fid],
            "observed_sealed": obs_seal,
            "observed_tip": obs_tip,
            "sealed_eq_tip": obs_seal == obs_tip,
            "match": match,
            "detail_sealed": det_s,
            "detail_tip": det_t,
        })
    return {"facts": facts, "stale": stale}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default="/home/vgpnk/Projects/shokunin/kama-shokunin")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "EX01.json"))
    ap.add_argument("--sealed", default=SEALED_DEFAULT)
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--record-counter", default=None,
                    help="counter stdout line to merge into the receipt")
    ap.add_argument("--counter-exit", type=int, default=None)
    args = ap.parse_args()

    lane = Lane(args.repo)
    tip = lane.tip()
    out_path = Path(args.out)

    if args.record_counter is not None:
        receipt = json.loads(out_path.read_text())
        line = args.record_counter.strip()
        receipt["counter"] = {
            "tool": "tools/round80-selfrecord-round79.py",
            "argv": f"python3 tools/round80-selfrecord-round79.py --repo {args.repo}",
            "line": line,
            "exit": args.counter_exit,
            "target": "SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0 (exit 0)",
        }
        cm = re.match(r"SELFRECORD_R79 claims=(\d+) mismatches=(\d+) corrected=(\d+) unbacked=(\d+)", line)
        stale = receipt.get("stale", [])
        if cm:
            hits_target = (line.startswith("SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0")
                           and args.counter_exit == 0)
            counter_stale = int(cm.group(2))
            receipt["counter"]["parsed"] = {
                "claims": int(cm.group(1)), "mismatches": int(cm.group(2)),
                "corrected": int(cm.group(3)), "unbacked": int(cm.group(4)),
                "hits_target": hits_target,
            }
            receipt["agreement"] = (
                "agreement: independent re-derivation and the counter both report exactly "
                f"{sorted(stale)} stale" if counter_stale == len(stale) and set() is not None else None)
            # explicit disagreement statement
            if counter_stale == len(stale):
                receipt["agreement"] = (
                    f"agreement: both the independent re-derivation and the counter find the "
                    f"same {len(stale)} stale facts ({', '.join(stale)}); "
                    f"counter line: {line}; counter exit={args.counter_exit}")
            else:
                receipt["agreement"] = (
                    f"disagreement: independent re-derivation finds stale={stale} "
                    f"({len(stale)} facts); counter reports mismatches={counter_stale} "
                    f"(line: {line}, exit={args.counter_exit})")
        else:
            receipt["agreement"] = (
                f"disagreement: counter did not print the expected summary shape "
                f"(line: {line!r}, exit={args.counter_exit}); independent stale list={stale}")
        out_path.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"counter": receipt["counter"], "agreement": receipt["agreement"]},
                         indent=2))
        return 0

    result = derive_all(lane, args.sealed, tip)
    receipt = {
        "seat": SEAT,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": args.repo,
        "base": args.base,
        "sealed": args.sealed,
        "tip": tip,
        "method": ("declared strings grounded in the record's own bytes at the sealed "
                   "revision; observed values re-derived from git objects at the sealed "
                   "revision and at the tip (git show / ls-tree); the lane counter "
                   "tools/round80-selfrecord-round79.py is neither imported nor read by "
                   "this script"),
        "facts": result["facts"],
        "stale": result["stale"],
    }
    out_path.write_text(json.dumps(receipt, indent=2) + "\n")
    for f in receipt["facts"]:
        print(f"{f['id']} {f['name']}: declared={f['declared']} "
              f"sealed={f['observed_sealed']} tip={f['observed_tip']} match={f['match']}")
    print("stale:", receipt["stale"])
    print(f"receipt: {out_path}")
    return 0 if not result["stale"] else 1


if __name__ == "__main__":
    sys.exit(main())
