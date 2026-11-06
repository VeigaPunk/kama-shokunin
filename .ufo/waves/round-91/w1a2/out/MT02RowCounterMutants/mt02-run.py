#!/usr/bin/env python3
"""MT02 mutant runner — round 91 wave w1a2.

Runs a counter (pristine frozen bytes or one mutant) through
  1. the adapted frozen forgery battery (c2-forgeries-path.py, V1-V4), and
  2. the counter's own predicate on the measured lane revision M2,
then classifies the mutant against the pristine run:
  KILLED-aggregate : a variant's final THRESHOLD_ROWS numbers or exit code differ, or the counter
                     crashed / printed no final line, or the M2 final line / exit differs.
  KILLED-rowwhy    : only per-row (bound, why) lines differ (the battery's printed expectation).
  SURVIVED         : every stdout byte differs only in rev=<hex> (fixture commit hashes move).

Usage: mt02-run.py --frozen <counter> --lane <scratch checkout> --rev <M2> \
                   --battery <c2-forgeries-path.py> --mutants <dir> --scratch <dir> --out <dir> [--jobs 4]
Writes <out>/<tag>.battery.out, <out>/<tag>.m2.out, <out>/summary.json.
"""
import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
from pathlib import Path

AGG = re.compile(r"^THRESHOLD_ROWS rows=(\d+) bound=(\d+) unbound=(\d+) duplicates=(\d+) "
                 r"engines=(\d+) fetch_failures=(\d+) rev=(\S+)$", re.M)
ROW = re.compile(r"^THRESHOLD_ROW (\S+) bound=(\d+) why=(\S+)$", re.M)
VAR = re.compile(r"^== (\S+):", re.M)


def parse_battery(text):
    blocks = {}
    marks = [(m.start(), m.group(1)) for m in VAR.finditer(text)]
    for i, (pos, name) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        body = text[pos:end]
        agg = AGG.search(body)
        rows = {f"{r} {b}": w for r, b, w in ROW.findall(body)}
        exits = re.findall(r"^exit=(-?\d+)$", body, re.M)
        blocks[name] = {
            "agg": tuple(int(x) for x in agg.groups()[:6]) if agg else None,
            "exit": int(exits[0]) if exits else None,
            "rows": rows,
        }
    return blocks


def parse_m2(text):
    agg = AGG.search(text)
    return {
        "agg": tuple(int(x) for x in agg.groups()[:6]) if agg else None,
        "exit": int(re.findall(r"^exit=(-?\d+)$", text, re.M)[-1]) if re.findall(r"^exit=(-?\d+)$", text, re.M) else None,
    }


def run(tag, counter, a):
    out = Path(a.out)
    b = subprocess.run([sys.executable, str(Path(a.battery)), "--lane", a.lane,
                        "--counter", str(counter), "--scratch", a.scratch],
                       capture_output=True, text=True)
    (out / f"{tag}.battery.out").write_text(b.stdout)
    (out / f"{tag}.battery.err").write_text(b.stderr)
    m = subprocess.run([sys.executable, str(counter), "--repo", a.lane, "--rev", a.rev],
                       capture_output=True, text=True)
    (out / f"{tag}.m2.out").write_text(m.stdout)
    (out / f"{tag}.m2.err").write_text(m.stderr)
    try:
        bat = parse_battery(b.stdout)
    except Exception as e:  # noqa: BLE001 - a malformed counter is itself a result
        bat = {"__parse_error__": {"agg": None, "exit": None, "rows": {}, "err": repr(e)}}
    return {"tag": tag, "battery": bat,
            "battery_exit": b.returncode, "m2": parse_m2(m.stdout),
            "m2_exit": m.returncode}


def verdict(base, mut):
    diffs = []
    for v, bb in base["battery"].items():
        mm = mut["battery"].get(v)
        if mm is None:
            diffs.append(f"{v}: variant missing from mutant battery output")
            continue
        if bb["agg"] != mm["agg"] or bb["exit"] != mm["exit"]:
            diffs.append(f"{v}: aggregate/exit {bb['agg']}/{bb['exit']} -> {mm['agg']}/{mm['exit']}")
    for v in mut["battery"]:
        if v not in base["battery"]:
            diffs.append(f"{v}: extra variant in mutant battery output")
    if base["m2"] != mut["m2"] or base["m2_exit"] != mut["m2_exit"]:
        diffs.append(f"M2: {base['m2']} exit {base['m2_exit']} -> {mut['m2']} exit {mut['m2_exit']}")
    if base["battery_exit"] != mut["battery_exit"]:
        diffs.append(f"battery driver exit {base['battery_exit']} -> {mut['battery_exit']}")
    if diffs:
        return "KILLED-aggregate", diffs
    rowdiff = []
    for v, bb in base["battery"].items():
        mm = mut["battery"].get(v, {"rows": {}})
        if bb["rows"] != mm["rows"]:
            changed = sorted(k for k in set(bb["rows"]) | set(mm["rows"])
                             if bb["rows"].get(k) != mm["rows"].get(k))
            rowdiff.append(f"{v}: rows {[(k, bb['rows'].get(k), mm['rows'].get(k)) for k in changed]}")
    if rowdiff:
        return "KILLED-rowwhy", rowdiff
    return "SURVIVED", []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen", required=True)
    ap.add_argument("--lane", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--battery", required=True)
    ap.add_argument("--mutants", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    pristine = run("pristine", a.frozen, a)
    muts = sorted(Path(a.mutants).glob("M*.py"))
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(run, p.stem, str(p), a): p.stem for p in muts}
        results = []
        for f in cf.as_completed(futs):
            results.append(f.result())
    results.sort(key=lambda r: r["tag"])
    summary = {"pristine": pristine, "mutants": []}
    print(f"{'mutant':42s} {'verdict':17s} detail")
    for r in results:
        v, d = verdict(pristine, r)
        summary["mutants"].append({"tag": r["tag"], "verdict": v, "diff": d})
        print(f"{r['tag']:42s} {v:17s} {d[0] if d else ''}")
    (Path(a.out) / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"\npristine battery aggregates: "
          f"{ {k: (v['agg'], v['exit']) for k, v in pristine['battery'].items()} }")
    print(f"pristine M2: {pristine['m2']} exit={pristine['m2_exit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
