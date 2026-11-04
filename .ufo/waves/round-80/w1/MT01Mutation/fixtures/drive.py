#!/usr/bin/env python3
"""Run the bounded behavioral detectors on pristine, mutated and restored bytes."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

S = Path(sys.argv[1])
LANE = Path(sys.argv[2])
OUT = S / "out"
LOGS = OUT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
PY = sys.executable

C1 = "round80-selfrecord-round79.py"
C2 = "round80-engine-pin-relations.py"
C3 = "round80-ollama-census.py"

TAGS = S / "fixtures/c2/tags"


def run(tag, detector, cmd, timeout=900, env=None):
    log = LOGS / f"{tag}__{detector.replace('/', '_').replace(':', '_')}.out"
    try:
        proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                              timeout=timeout, env=env)
        result = {"cmd": " ".join(str(c) for c in cmd), "exit": proc.returncode,
                  "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        result = {"cmd": " ".join(str(c) for c in cmd), "exit": "timeout",
                  "stdout": "", "stderr": ""}
    log.write_text(f"# {result['cmd']}\n# exit={result['exit']}\n"
                   f"--- stdout ---\n{result['stdout']}\n--- stderr ---\n{result['stderr']}\n")
    return result


def same(a, b):
    return a["exit"] == b["exit"] and a["stdout"].strip() == b["stdout"].strip()


def verdict_of(baseline, mutant):
    if baseline["exit"] != 0 and baseline["exit"] is not False:
        return "INCONCLUSIVE (baseline red)"
    if same(baseline, mutant):
        return "SURVIVED"
    return "CAUGHT"


def main():
    c1_fix = json.loads((S / "fixtures/c1/index.json").read_text())
    c2_fix = json.loads((S / "fixtures/c2/index.json").read_text())
    c3_fix = json.loads((S / "fixtures/c3/index.json").read_text())

    def c1(mod):
        return {
            "selftest": run("c1", "selftest", [PY, mod, "--selftest"]),
            **{f"fixture-{name}": run("c1", f"fixture-{name}",
                                      [PY, mod, "--repo", c1_fix[name]["repo"],
                                       "--sealed", c1_fix[name]["sealed"],
                                       "--tip", c1_fix[name]["tip"]])
               for name in ("good", "ancestor-at", "garbage-on-fresh", "outside-container")},
        }

    def c2(mod, register_name):
        return {
            "selftest": run("c2", "selftest", [PY, mod, "--selftest"]),
            "lane-register-good": run("c2", "lane-register-good",
                                      [PY, mod, "--repo", LANE, "--tags-dir", TAGS,
                                       "--register", c2_fix["register_good"], "--tip", "master"]),
            "lane-register-no-b7200": run("c2", "lane-register-no-b7200",
                                          [PY, mod, "--repo", LANE, "--tags-dir", TAGS,
                                           "--register", c2_fix["register_no_b7200"],
                                           "--tip", "master"]),
            "uncommitted-receipt": run("c2", "uncommitted-receipt",
                                       [PY, mod, "--repo", c2_fix["git_uncommitted_receipt"]["repo"],
                                        "--tags-dir", Path(c2_fix["git_uncommitted_receipt"]["repo"]) / "tags",
                                        "--pins", "pins.tsv", "--register", "register.tsv",
                                        "--tip", c2_fix["git_uncommitted_receipt"]["tip"]]),
        }

    grade_script = r'''
import importlib.util, json, sys
path, fixture = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("census_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
idx = json.load(open(fixture))
docs, port = idx["docs"], idx["port"]
out = {}
for name, arg in (("green", ("green_yes", "green_no")),
                  ("governed_without_class", ("green_yes", "governed_without_class"))):
    res = mod.grade(docs[arg[0]], docs[arg[1]], port)
    out[name] = {"summary": res["summary"], "findings": res["findings"]}
print(json.dumps(out, sort_keys=True))
'''

    def c3(mod):
        return {
            "selftest": run("c3", "selftest", [PY, mod, "--selftest"]),
            "grade-fixture": run("c3", "grade-fixture",
                                 [PY, "-c", grade_script, mod, S / "fixtures/c3/grade.json"]),
            **{f"audit-{name}": run("c3", f"audit-{name}",
                                    [PY, mod, "--repo", c3_fix[f"audit_{name}"],
                                     "--audit", "--register", "registry.tsv", "--tip", "HEAD"])
               for name in ("green", "other_engine", "one_engine")},
        }

    result = {"baselines": {}, "mutants": {}}

    result["baselines"]["c1"] = c1(S / "pristine" / C1)
    result["baselines"]["c2"] = c2(S / "pristine" / C2, "good")
    result["baselines"]["c3"] = c3(S / "pristine" / C3)

    mut_index = json.loads((S / "mutants/index.json").read_text())
    for spec in mut_index:
        tag, mod = spec["tag"], Path(spec["path"])
        module = spec["module"]
        if module == C1:
            got = c1(mod)
            base = result["baselines"]["c1"]
        elif module == C2:
            got = c2(mod, "good")
            base = result["baselines"]["c2"]
        else:
            got = c3(mod)
            base = result["baselines"]["c3"]
        checks = {}
        for key in got:
            checks[key] = {"baseline_exit": base[key]["exit"], "mutant_exit": got[key]["exit"],
                           "baseline_line": base[key]["stdout"].strip().splitlines()[-1:] or [""],
                           "mutant_line": got[key]["stdout"].strip().splitlines()[-1:] or [""],
                           "same": same(base[key], got[key])}
        caught_by = [key for key, c in checks.items() if not c["same"]]
        result["mutants"][tag] = {"module": module, "note": spec["note"],
                                  "pristine_sha256": spec["pristine_sha256"],
                                  "mutant_sha256": spec["mutant_sha256"],
                                  "checks": checks,
                                  "caught_by": caught_by,
                                  "verdict": "CAUGHT" if caught_by else "SURVIVED"}

    # restored bytes: re-copy pristine and re-run one representative detector per module
    restored = S / "restored"
    restored.mkdir(exist_ok=True)
    for name in (C1, C2, C3):
        shutil.copyfile(S / "pristine" / name, restored / name)
        assert (restored / name).read_bytes() == (S / "pristine" / name).read_bytes()
    result["restored"] = {
        "c1": run("restored", "c1-representative",
                  [PY, restored / C1, "--repo", c1_fix["ancestor-at"]["repo"],
                   "--sealed", c1_fix["ancestor-at"]["sealed"],
                   "--tip", c1_fix["ancestor-at"]["tip"]]),
        "c2": run("restored", "c2-representative",
                  [PY, restored / C2, "--repo", LANE, "--tags-dir", TAGS,
                   "--register", c2_fix["register_no_b7200"], "--tip", "master"]),
        "c3": run("restored", "c3-representative",
                  [PY, restored / C3, "--repo", c3_fix["audit_other_engine"],
                   "--audit", "--register", "registry.tsv", "--tip", "HEAD"]),
    }
    (OUT / "matrix.json").write_text(json.dumps(result, indent=2) + "\n")
    for tag, entry in result["mutants"].items():
        print(f"{tag}: {entry['verdict']} caught_by={entry['caught_by']}")
    print("restored:")
    for key, r in result["restored"].items():
        print(f"  {key}: exit={r['exit']} last={r['stdout'].strip().splitlines()[-1:]}")


if __name__ == "__main__":
    main()
