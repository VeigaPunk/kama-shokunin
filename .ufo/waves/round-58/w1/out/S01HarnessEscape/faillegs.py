#!/usr/bin/env python3
"""R01: every leg assertion evaluates False; battery records its own failures."""
import json
import pathlib
import subprocess

ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}
LOG = pathlib.Path("/fast/scratch/hyaku/kama-r58/S01HarnessEscape/probes/faillegs.json")
SEEN = []


def run(label, counter, expected, out):
    p = subprocess.run(["python3", "tools/round56-env-leg-test.py", "--counter", str(counter),
                        "--expect", expected], capture_output=True, text=True)
    fields = {t.split("=", 1)[0]: t.split("=", 1)[1] for t in p.stdout.split() if "=" in t}
    ok = p.returncode == 0 and fields.get("ld_audit") == expected
    SEEN.append({"label": label, "ok": ok, "observed": fields.get("ld_audit")})
    out.write_text(p.stdout)
    return ok


def assert_mutant_breaks_detection(counter, out):
    p = subprocess.run(["python3", "tools/round56-env-leg-test.py", "--counter", str(counter),
                        "--expect", "detected"], capture_output=True, text=True)
    ok = p.returncode == 1
    SEEN.append({"label": "assert", "ok": ok})
    out.write_text(p.stdout)
    return ok


def main():
    out = pathlib.Path("/nonexistent")
    res = [run("base-old-counter", "x", "missed", out),
           run("round56-counter", "x", "detected", out),
           run("m-drop-ldaudit", "x", "missed", out),
           assert_mutant_breaks_detection("x", out)]
    with open(LOG, "w") as fh:
        json.dump({"legs": SEEN, "all_ok": all(res)}, fh, indent=1)
    return 0 if all(res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
