#!/usr/bin/env python3
"""Round-57 E03: runnable frozen-counter selftest for the no-op and stale-count defects.

The selftest never trusts the instrument's own verdict.  For every fixture it
(a) runs the instrument under test, (b) independently re-derives the fact the
instrument claims from the fixture's committed bytes, and (c) compares the two.
An instrument that prints a green summary without reading the tree therefore
fails, and a stale self-description count is detected even when the instrument's
own summary is green.

Modes
  --mode c1  instrument = tools/round56-prereg-check.py shape
             fixtures: genuine, no-op variants, stale roster, absent, bad JSON
  --mode c2  instrument = tools/round42-selfdesc-reconcile.py shape
             fixtures: stale count, repaired count, count-regressed tree,
             trimmed maxN, inflated maxN, missing SCORECARD

Verdict: PASS only if every check in the matrix holds.  Exit 0 PASS, 1 FAIL, 2
fixtures missing.

Integration design (see report):
  * every well-formed fixture carries the fact the instrument must bind;
  * the no-op fixtures must be red for the instrument, and the frozen no-op
    control script `.ufo/waves/round-57/controls/c1-noop.py` must be red here;
  * --require-witness additionally demands content digests of the bytes the
    instrument read (battery_sha256/prereg_sha256, sc_sha256): the only cheap
    proof that a green summary came from the tree.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

S = pathlib.Path("/fast/scratch/hyaku/kama-r57/E03CounterSelftest")
FIX = json.loads((S / "out" / "fixtures.json").read_text())
CLEAN = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
CLEAN = {k: v for k, v in CLEAN.items() if not k.startswith("GIT_")} | {
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(repo, *args, text=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, env=CLEAN)
    return p.stdout.decode(errors="replace") if text else p.stdout


def blob(repo, tip, path):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:{path}"],
                       capture_output=True, env=CLEAN)
    return p.stdout if p.returncode == 0 else None


def summary_fields(out):
    f = {}
    for line in out.splitlines():
        if "mismatches=" in line or "roster_match=" in line:
            for tok in line.split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    f[k] = v
    return f


def run_instrument(instrument, repo, tip):
    p = subprocess.run([sys.executable, instrument, "--repo", repo, "--tip", tip],
                       capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout, p.stderr


class Checks:
    def __init__(self, mode, label):
        self.mode, self.label, self.rows = mode, label, []

    def check(self, ident, ok, expected, observed):
        self.rows.append((ident, bool(ok), expected, observed))
        print(f"check {ident} {'PASS' if ok else 'FAIL'} expected={expected} observed={observed}")

    def finish(self):
        failed = sum(1 for _, ok, _, _ in self.rows if not ok)
        verdict = "PASS" if failed == 0 else "FAIL"
        print(f"SELFTEST mode={self.mode} instrument={self.label} checks={len(self.rows)} "
              f"failed={failed} verdict={verdict}")
        return 0 if failed == 0 else 1


# ---------------------------------------------------------------- C1 fixtures
def c1_expected(repo, tip):
    """What a complete execution-binding checker must decide, derived independently."""
    bat = blob(repo, tip, "tools/round56-env-leg-battery.py")
    pre = blob(repo, tip, ".ufo/waves/round-56/preregistration.json")
    if bat is None or pre is None:
        return {"present": False, "digest": hashlib.sha256(bat or pre or b"").hexdigest()}
    return {"present": True,
            "battery_sha256": hashlib.sha256(bat).hexdigest(),
            "prereg_sha256": hashlib.sha256(pre).hexdigest()}


def c1_matrix(instrument, label, require_witness):
    c = Checks("c1", label)
    fx = FIX["c1"]
    verdicts = {}
    for name, meta in fx.items():
        rc, out, err = run_instrument(instrument, meta["dir"], meta["tip"])
        f = summary_fields(out)
        exp = c1_expected(meta["dir"], meta["tip"])
        verdicts[name] = (rc, f, out, exp)

    rc, f, out, _ = verdicts["c1-genuine"]
    c.check("c1-genuine/green", rc == 0 and f.get("met") == "True",
            "exit=0 met=True", f"exit={rc} met={f.get('met')}")
    for name in ("c1-noop-deadcode", "c1-noop-unusedfn", "c1-noop-literal"):
        rc, f, out, _ = verdicts[name]
        c.check(f"{name}/red", rc != 0 and f.get("met") == "False",
                "exit!=0 met=False", f"exit={rc} met={f.get('met')}")
    rc, f, out, _ = verdicts["c1-stale-roster"]
    c.check("c1-stale-roster/red", rc != 0 and f.get("met") == "False" and f.get("roster_match") == "0",
            "exit!=0 met=False roster_match=0",
            f"exit={rc} met={f.get('met')} roster_match={f.get('roster_match')}")
    rc, f, out, _ = verdicts["c1-absent"]
    c.check("c1-absent/red", rc == 1 and f.get("present") == "0" and f.get("met") == "False",
            "exit=1 present=0 met=False",
            f"exit={rc} present={f.get('present')} met={f.get('met')}")
    rc, f, out, _ = verdicts["c1-badjson"]
    c.check("c1-badjson/exit2", rc == 2, "exit=2", f"exit={rc}")
    if require_witness:
        rc, f, out, exp = verdicts["c1-genuine"]
        c.check("c1-genuine/witness",
                f"battery_sha256={exp['battery_sha256']}" in out
                and f"prereg_sha256={exp['prereg_sha256']}" in out,
                f"battery_sha256={exp['battery_sha256']} prereg_sha256={exp['prereg_sha256']}",
                "present" if "battery_sha256=" in out else "absent")
    return c


# ---------------------------------------------------------------- C2 fixtures
SPOT = "corpus/lessons/*verifier-spotcheck.md"
COUNT_RE = re.compile(r"run\s+`([^`]+)`\s*(?:\u2192|->)\s*`([^`]+)`")


def c2_expected(repo, tip):
    sc = blob(repo, tip, "SCORECARD.md")
    if sc is None:
        return {"sc": None, "maxn": None, "declared": None, "observed": None, "stale": None}
    text = sc.decode(errors="replace")
    rounds = [int(m.group(1)) for m in (re.match(r"^## Round (\d+)", l) for l in text.split("\n")) if m]
    declared = None
    for line in text.split("\n"):
        if "verifier-spotcheck" in line and "capability-repertoire-audit" in line:
            for cmd, want in COUNT_RE.findall(line):
                if "verifier-spotcheck" in cmd:
                    declared = want
            break
    files = [p for p in git(repo, "ls-tree", "-r", "--name-only", tip).split("\n")
             if re.fullmatch(r"corpus/lessons/[^/]*verifier-spotcheck\.md", p)]
    observed = len(files)
    return {"sc": hashlib.sha256(sc).hexdigest(), "maxn": max(rounds) if rounds else None,
            "declared": declared, "observed": observed,
            "stale": None if declared is None else declared != str(observed)}


def c2_matrix(instrument, label, require_witness):
    c = Checks("c2", label)
    out = {}
    for name, meta in FIX["c2"].items():
        rc, so, se = run_instrument(instrument, meta["dir"], meta["tip"])
        out[name] = (rc, summary_fields(so), so, c2_expected(meta["dir"], meta["tip"]))

    rc, f, so, exp = out["c2-base"]
    c.check("c2-base/red", rc == 1 and int(f.get("mismatches", "-1")) >= 1
            and "verifier-spotcheck" in so,
            "exit=1 mismatches>=1 detail names verifier-spotcheck",
            f"exit={rc} mismatches={f.get('mismatches')} detail={('verifier-spotcheck' in so)}")
    c.check("c2-base/indep-stale", exp["stale"] is True,
            f"declared!=observed (declared={exp['declared']} observed={exp['observed']})",
            f"declared={exp['declared']} observed={exp['observed']} stale={exp['stale']}")

    rc, f, so, exp = out["c2-fixed"]
    c.check("c2-fixed/green", rc == 0 and f.get("mismatches") == "0" and f.get("met") == "True",
            "exit=0 mismatches=0 met=True",
            f"exit={rc} mismatches={f.get('mismatches')} met={f.get('met')}")
    c.check("c2-fixed/indep-fresh", exp["stale"] is False,
            "declared==observed", f"declared={exp['declared']} observed={exp['observed']}")

    rc, f, so, exp = out["c2-fixed-minus-lesson"]
    c.check("c2-fixed-minus-lesson/red", rc == 1 and int(f.get("mismatches", "-1")) >= 1,
            "exit=1 mismatches>=1", f"exit={rc} mismatches={f.get('mismatches')}")
    c.check("c2-fixed-minus-lesson/indep-stale", exp["stale"] is True,
            "declared!=observed", f"declared={exp['declared']} observed={exp['observed']}")

    for name in ("c2-maxn-trim", "c2-maxn-inflated"):
        rc, f, so, exp = out[name]
        c.check(f"{name}/maxN", f.get("maxN") == str(exp["maxn"]),
                f"maxN={exp['maxn']} (independent heading max)",
                f"maxN={f.get('maxN')} exit={rc}")

    rc, f, so, exp = out["c2-no-scorecard"]
    c.check("c2-no-scorecard/exit2", rc == 2, "exit=2", f"exit={rc}")

    agree = all((out[n][1].get("met") == "False") == out[n][3]["stale"]
                for n in ("c2-base", "c2-fixed", "c2-fixed-minus-lesson"))
    c.check("c2/met-agrees-with-independent-staleness", agree,
            "met==False iff independent staleness", f"agree={agree}")
    if require_witness:
        rc, f, so, exp = out["c2-fixed"]
        c.check("c2-fixed/sc-witness", f"sc_sha256={exp['sc']}" in so,
                f"sc_sha256={exp['sc']}", "present" if "sc_sha256=" in so else "absent")
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("c1", "c2"), required=True)
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--label", default=None)
    ap.add_argument("--require-witness", action="store_true")
    a = ap.parse_args()
    label = a.label or pathlib.Path(a.instrument).name
    matrix = c1_matrix if a.mode == "c1" else c2_matrix
    rc = matrix(a.instrument, label, a.require_witness).finish()
    return rc


if __name__ == "__main__":
    sys.exit(main())
