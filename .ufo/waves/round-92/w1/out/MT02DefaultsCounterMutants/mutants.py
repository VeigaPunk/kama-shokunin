#!/usr/bin/env python3
"""mutants.py - 22 single-point mutants of tools/round92-server-defaults.py, graded by c1-mutbattery.py.

Each mutant is one literal replacement (exactly one occurrence asserted) in a private copy of the
frozen counter. A mutant is KILLED when any battery case (P0, P1-real-M1, V1-V8) exits differently
from the same case on the pristine counter; SURVIVED otherwise. Writes mutants, per-mutant battery
logs and results.json under --work.
Usage: mutants.py --work DIR --battery FILE --lane DIR --binary PATH --section FILE --rows FILE
"""
import argparse, concurrent.futures as cf, json, re, subprocess, sys
from pathlib import Path

MUTANTS = [
    ("M01-B1-empty-cell-off",
     '        if not c or (c == "-" and i != 3):',
     '        if not c and (c == "-" and i != 3):'),
    ("M02-B2-value-in-literal-off",
     '    if not nums or nums[0] not in lit:',
     '    if not nums:'),
    ("M03-B2-num-regex-unsigned",
     'NUM_RE = re.compile(r"-?\\d+(?:\\.\\d+)?")',
     'NUM_RE = re.compile(r"\\d+(?:\\.\\d+)?")'),
    ("M04-B3-status-tier-off",
     '    if status != "mined" or tier not in ("A", "B"):',
     '    if False:'),
    ("M05-B4-pin-not-in-url-off",
     '    if words[-1] not in url:',
     '    if False:'),
    ("M06-B4-engine-not-in-url-off",
     '    if eng not in url.lower():',
     '    if False:'),
    ("M07-B4-moving-ref-off",
     '    if any(x in url for x in MOVING):',
     '    if False:'),
    ("M08-B5-sha256-pin-off",
     '    if hashlib.sha256(body).hexdigest() != h.group(1):',
     '    if False:'),
    ("M09-B6-literal-at-line-off",
     '    if not 1 <= n <= len(lines) or lit not in lines[n - 1]:',
     '    if not 1 <= n <= len(lines):'),
    ("M10-B7-name-in-literal-off",
     '    if not any(t in lit for t in toks):',
     '    if False:'),
    ("M11-H1-help-value-compare-off",
     '            if d is None or d != nums[0]:',
     '            if d is None:'),
    ("M12-H1-help-default-regex-unsigned",
     '            m = re.search(r"default:\\s*(-?\\d+(?:\\.\\d+)?)", " ".join(b))',
     '            m = re.search(r"default:\\s*(\\d+(?:\\.\\d+)?)", " ".join(b))'),
    ("M13-H2-entry-point-loosened",
     '            if "/tools/server/" not in url:',
     '            if "/tools/" not in url:'),
    ("M14-H3-llama-flag-not-option-off",
     '            return False, "llama-flag-not-option", False, False, False',
     '            pass'),
    ("M15-supersedes-gate-13",
     'and len(sup) == len(SUPERSEDE))',
     'and len(sup) >= len(SUPERSEDE) - 1)'),
    ("M16-supersede-set-drops-T14",
     'SUPERSEDE = {f"T{i:02d}" for i in range(1, 15)}',
     'SUPERSEDE = {f"T{i:02d}" for i in range(1, 14)}'),
    ("M17-duplicate-pair-rule-off",
     '        if rid in seen_id or (pair and pair in seen_pair):',
     '        if rid in seen_id:'),
    ("M18-duplicates-gate-off",
     'and unbound == 0 and dup == 0 and fails == 0',
     'and unbound == 0 and fails == 0'),
    ("M19-MIN_ROWS-10",
     'MIN_ROWS = 14',
     'MIN_ROWS = 10'),
    ("M20-MIN_ENGINES-2",
     'MIN_ENGINES = 3',
     'MIN_ENGINES = 2'),
    ("M21-MIN_HELP-5",
     'MIN_HELP = 7',
     'MIN_HELP = 5'),
    ("M23-supersede-membership-off",
     '            sup.update(t for t in re.findall(r"T\\d{2}", cells[8]) if t in SUPERSEDE)',
     '            sup.update(re.findall(r"T\\d{2}", cells[8]))'),
    ("M22-MOVING-drops-main",
     'MOVING = ("/main/", "/master/", "/HEAD/", "refs/heads")',
     'MOVING = ("/master/", "/HEAD/", "refs/heads")'),
]
CASES = ["P0-candidate", "P1-real-M1", "V1-r91-T07-transplant", "V2-shared-struct-line",
         "V3-derived-not-entry-point", "V4-drop-R15", "V5-option-as-derived", "V6-env-not-option",
         "V7-typecheck-line-LIMIT", "V8-unpinned-binary"]
CASE_RE = re.compile(r"^CASE (\S+) exit=(\d+) want=(\d+) ", re.M)


def run_battery(args, counter, label, log):
    p = subprocess.run([sys.executable, args.battery, "--lane", args.lane, "--work", args.work,
                        "--binary", args.binary, "--section", args.section, "--rows", args.rows,
                        "--counter", str(counter), "--label", label], capture_output=True, text=True)
    Path(log).write_text(p.stdout + ("\nSTDERR:\n" + p.stderr if p.stderr else ""))
    return p.returncode, {m.group(1): int(m.group(2)) for m in CASE_RE.finditer(p.stdout)}


def main():
    ap = argparse.ArgumentParser()
    for x in ("--work", "--battery", "--lane", "--binary", "--section", "--rows"):
        ap.add_argument(x, required=True)
    a = ap.parse_args()
    work = Path(a.work).resolve()
    mdir = work / "mutants"
    mdir.mkdir(parents=True, exist_ok=True)
    src = (Path(a.lane).resolve() / "tools" / "round92-server-defaults.py").read_text()
    pristine = work / "pristine-counter.py"
    pristine.write_text(src)

    base_rc, base = run_battery(a, pristine, "pristine", work / "battery-pristine.log")
    print(f"PRISTINE rc={base_rc} exits={base}")
    if base_rc != 0 or len(base) != len(CASES):
        print("BASELINE-FAILED: mutated runs are inconclusive")
        return 2

    made = []
    for name, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            print(f"GEN-REFUSED {name} occurrences={n}")
            continue
        f = mdir / (name.split("-")[0] + ".py")
        f.write_text(src.replace(old, new, 1))
        made.append((name, f))

    results = []
    def one(name, f):
        rc, exits = run_battery(a, f, name, work / f"battery-{f.stem}.log")
        diff = {c: (base[c], exits.get(c)) for c in CASES if exits.get(c) != base[c]}
        return {"mutant": name, "file": str(f), "battery_rc": rc, "exits": exits,
                "changed_cases": diff, "verdict": "killed" if diff else "survived"}

    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(lambda t: one(*t), made):
            results.append(r)
            print(f"{r['verdict'].upper():8s} {r['mutant']:42s} changed={sorted(r['changed_cases'])}")

    (work / "results.json").write_text(json.dumps({"pristine": base, "results": results}, indent=1))
    k = sum(r["verdict"] == "killed" for r in results)
    print(f"MUTANTS total={len(results)} killed={k} survived={len(results)-k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
