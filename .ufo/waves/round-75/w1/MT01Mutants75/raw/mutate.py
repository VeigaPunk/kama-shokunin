#!/usr/bin/env python3
"""MT01Mutants75 mutation harness. Scratch-only; never writes the lane tree.

Phase baseline: run each module's --selftest and real-lane command on pristine bytes.
Phase mutants:  for each mutant patch, restore pristine, apply patch (assert unique
anchor), run --selftest and the real-lane command, record rc/output, restore pristine.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
ROOT = Path("/fast/scratch/hyaku/kama-r75/MT01Mutants75")
CLONE = ROOT / "clone"
PRISTINE = ROOT / "pristine"
RUNS = ROOT / "runs"
RESULTS = ROOT / "results"

PINS = "round75-interpretation-pins.py"
SURV = "round75-survivor-probe.py"
ACPT = "round75-append-accepted.py"

MUT = {
    PINS: {
        "real": ["--repo", str(LANE)],
        "work": True,
        "mutants": {
            "A1-declared-flip": (
                '    declared = sum(pin["observed"] == pin["declared"] for pin in pins)\n',
                '    declared = sum(pin["observed"] != pin["declared"] for pin in pins)\n'),
            "A2-kill-rule-drop": (
                '    killed = sum(pin["mutant"] != pin["declared"] and pin["mutant_ok"] for pin in pins)\n',
                '    killed = sum(pin["mutant_ok"] for pin in pins)\n'),
            "A3-finding-exit-to-0": (
                '"exit": 0 if declared == killed == len(pins) else 1}',
                '"exit": 0 if declared == killed == len(pins) else 0}'),
            "A4-clean-exit-to-1": (
                '"exit": 0 if declared == killed == len(pins) else 1}',
                '"exit": 1 if declared == killed == len(pins) else 0}'),
            "A5a-grade-one-pin": (
                '         "mutant_name": "c1_f2c_literal_hex", "runs": results},\n    ])',
                '         "mutant_name": "c1_f2c_literal_hex", "runs": results},\n    ][:1])'),
            "A5b-fake-P2-leg": (
                '         "observed": pristine["exit"], "mutant": mutant["exit"],\n'
                '         "mutant_ok": mutant["exit"] == 1 and\n'
                '                       "RECEIPT_CLAIM_V2_FINDING stale-revision " in mutant["stdout"],\n',
                '         "observed": 0, "mutant": 1, "mutant_ok": True,\n'),
            "A6-trust-P2-observed": (
                '         "observed": pristine["exit"], "mutant": mutant["exit"],\n',
                '         "observed": 0, "mutant": mutant["exit"],\n'),
            "A7-oracle-declared-and-kill": (
                '            ("declared-and-kill", clean["exit"] == 0), ("cheat-escaped", cheat_ok)]',
                '            ("declared-and-kill", True), ("cheat-escaped", cheat_ok)]'),
            "A8-oracle-predicate": (
                '("predicate", plan_predicate(repo) == PREDICATE),',
                '("predicate", True),'),
        },
    },
    SURV: {
        "real": ["--repo", str(LANE)],
        "work": True,
        "mutants": {
            "B1-killed-flip": (
                '    killed = sum(row["mutant_exit"] == 1\n'
                '                 and EXPECTED_ARMS.get(row["mutant"]) in row["failed_arms"]\n'
                '                 for row in rows)\n',
                '    killed = sum(row["mutant_exit"] != 1\n'
                '                 and EXPECTED_ARMS.get(row["mutant"]) in row["failed_arms"]\n'
                '                 for row in rows)\n'),
            "B2-arm-check-drop": (
                '    killed = sum(row["mutant_exit"] == 1\n'
                '                 and EXPECTED_ARMS.get(row["mutant"]) in row["failed_arms"]\n'
                '                 for row in rows)\n',
                '    killed = sum(row["mutant_exit"] == 1 for row in rows)\n'),
            "B3-finding-exit-to-0": (
                '            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 1,\n',
                '            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 0,\n'),
            "B4-clean-exit-to-1": (
                '            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 1,\n',
                '            "exit": 1 if complete and pristine_exit == 0 and killed == 5 else 0,\n'),
            "B5-skip-pristine-verdict": (
                '        doc = grade(pristine.returncode, rows, MUTANTS)\n',
                '        doc = grade(0, rows, MUTANTS)\n'),
            "B6-skip-mutant-leg": (
                '            copy.write_text(original.replace(old, new, 1), encoding="utf-8")\n',
                '            copy.write_text(original, encoding="utf-8")\n'),
            "B8-oracle-complete-kills": (
                '        "complete-kills": grade(0, rows, MUTANTS)["exit"] == 0,\n',
                '        "complete-kills": True,\n'),
            "B9-summary-line-hardcode": (
                '    print("SURVIVORS2 mutants={mutants} killed={killed} escaped={escaped}".format(**doc))\n',
                '    print("SURVIVORS2 mutants=5 killed=5 escaped=0")\n'),
        },
    },
    ACPT: {
        "real": ["--repo", str(LANE)],
        "work": False,
        "mutants": {
            "C1-accepted-unconditional": (
                '        if not missing and key not in invalid:\n            accepted += 1\n',
                '        if True:\n            accepted += 1\n'),
            "C2-unaccepted-zero": (
                '"unaccepted": len(pending) - accepted,',
                '"unaccepted": 0,'),
            "C3-bad-rows-drop": (
                '    def bad(kind, detail, key=None):\n        nonlocal bad_rows\n        bad_rows += 1\n',
                '    def bad(kind, detail, key=None):\n        nonlocal bad_rows\n        bad_rows += 0\n'),
            "C4-finding-exit-to-0": (
                '    return int(bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))\n',
                '    return 0\n'),
            "C5-clean-exit-to-1": (
                '    return int(bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))\n',
                '    return int(not bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))\n'),
            "C6-grade-one-event": (
                '    pending = {key: e for key, e in all_events.items() if e["undisclosed"] and e["status"] != "restored"}\n',
                '    _pending_all = {key: e for key, e in all_events.items() if e["undisclosed"] and e["status"] != "restored"}\n'
                '    pending = dict(list(_pending_all.items())[:1])\n'),
            "C7-accept-any-row": (
                '        entry = expected.get(row_key)\n'
                '        if entry is None or not re.fullmatch(r"[0-9a-f]{64}", digest):\n'
                '            bad("hash-mismatch", detail, key)\n'
                '            continue\n',
                '        entry = expected.get(row_key)\n'
                '        if entry is None and key in pending:\n'
                '            covered.add(row_key)\n'
                '            continue\n'
                '        if entry is None or not re.fullmatch(r"[0-9a-f]{64}", digest):\n'
                '            bad("hash-mismatch", detail, key)\n'
                '            continue\n'),
            "C8-bad-declarations-zero": (
                '              "bad_rows": bad_rows, "bad_declarations": data["summary"]["bad_declarations"]}\n',
                '              "bad_rows": bad_rows, "bad_declarations": 0}\n'),
            "C9-oracle-and-to-or": (
                '        ok = actual == want and (finding is None or any(f["class"] == finding for f in result["findings"]))\n',
                '        ok = actual == want or (finding is None or any(f["class"] == finding for f in result["findings"]))\n'),
        },
    },
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(tag, argv):
    work = RUNS / ("tmp-" + tag)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    env = dict(os.environ, TMPDIR=str(work), PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run(argv, cwd=str(work), env=env, capture_output=True,
                          text=True, timeout=900)
    return proc


def one(tag, tool, extra, use_work):
    target = CLONE / "tools" / tool
    argv = [sys.executable, str(target)] + extra
    if use_work:
        wdir = RUNS / ("wd-" + tag)
        if wdir.exists():
            shutil.rmtree(wdir)
        argv += ["--work", str(wdir)]
    proc = run(tag, argv)
    return {
        "tag": tag, "argv": argv[1:], "rc": proc.returncode,
        "stdout_tail": proc.stdout[-6000:], "stderr_tail": proc.stderr[-1500:],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module", choices=sorted(MUT))
    ap.add_argument("--phase", choices=["baseline", "mutants"], required=True)
    args = ap.parse_args()
    tool = args.module
    spec = MUT[tool]
    RESULTS.mkdir(parents=True, exist_ok=True)
    pristine_path = PRISTINE / tool
    target = CLONE / "tools" / tool
    out = {"module": tool, "phase": args.phase, "runs": []}

    if args.phase == "baseline":
        shutil.copyfile(pristine_path, target)
        st = one(tool + "-base-st", tool, ["--selftest"] if tool != PINS else
                 ["--selftest", "--repo", str(LANE)], spec["work"])
        out["runs"].append(st)
        rl = one(tool + "-base-rl", tool, spec["real"], spec["work"])
        out["runs"].append(rl)
    else:
        source = pristine_path.read_text(encoding="utf-8")
        for name, (old, new) in spec["mutants"].items():
            count = source.count(old)
            entry = {"mutant": name, "anchor_count": count}
            if count != 1:
                entry["error"] = "anchor not unique"
                out["runs"].append(entry)
                continue
            shutil.copyfile(pristine_path, target)
            target.write_text(source.replace(old, new, 1), encoding="utf-8")
            st = one(tool + "-" + name + "-st", tool,
                     ["--selftest"] if tool != PINS else ["--selftest", "--repo", str(LANE)],
                     spec["work"])
            entry["selftest"] = st
            rl = one(tool + "-" + name + "-rl", tool, spec["real"], spec["work"])
            entry["real"] = rl
            out["runs"].append(entry)
        shutil.copyfile(pristine_path, target)
    restored = sha256(target) == sha256(pristine_path)
    out["restored_matches_pristine"] = restored
    (RESULTS / (Path(tool).stem + "." + args.phase + ".json")).write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"module": tool, "phase": args.phase,
                      "runs": len(out["runs"]), "restored": restored}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
