#!/usr/bin/env python3
"""X7 evidence artifact: the harness's own leg-attribution predicate
(.ufo/waves/round-55/c1/battery/run-battery.py:139-141)

    leg_failed = f"{leg} " in "\\n".join(
        ln for ln in text.splitlines() if ln.startswith("detail: "))

is satisfied by the PASSING detail lines of the very same receipt.  Running
the harness's predicate over the delivered positive control (control.out, every
leg green, met=True) shows which leg names it can actually distinguish.

Then: the predicate as written, applied to the m-ldpreload receipt (whose
summary says code=1, coderuns=3/3 - the CODE leg PASSED and only envnames
failed) with leg="code", returns True.  The harness would therefore certify
"leg=code ... -> ok" for a mutant whose code leg passed.
"""
import os
import re

BAT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/c1/battery"
MINE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X7BatteryReplay"


def leg_failed(text, leg):
    """run-battery.py:139-141, verbatim."""
    return f"{leg} " in "\n".join(
        ln for ln in text.splitlines() if ln.startswith("detail: "))


def harness_ok(rc, met, text, leg, kind="kill"):
    """run-battery.py:136-142, verbatim."""
    if kind == "vector":
        return rc == 0 and met
    return rc == 1 and not met and leg_failed(text, leg)


def main():
    print("### 1. the predicate over the POSITIVE CONTROL (every leg green, met=True)")
    text = open(os.path.join(BAT, "control.out")).read()
    summary = text.splitlines()[1]
    print(f"    {summary}")
    for leg in ("envnames", "code", "rehash", "bind", "sealed", "twopass"):
        print(f"    leg={leg:9s} leg_failed={leg_failed(text, leg)!s:5s}  "
              f"(a real kill would need this False)")
    print("    -> the predicate cannot distinguish ANY of these legs from a pass.")

    print()
    print("### 2. the predicate applied to the m-ldpreload receipt, named leg 'code'")
    text = open(os.path.join(MINE, "m-ldpreload.out")).read()
    summary = text.splitlines()[1]
    print(f"    {summary}")
    m = re.search(r"\bcode=(\d)(?:/(\d))?", summary)
    print(f"    summary says code={m.group(0)}  -> the CODE leg PASSED "
          f"(only envnames=0/3 failed)")
    print(f"    leg_failed(text, 'code') = {leg_failed(text, 'code')}  "
          f"-> harness ok (rc=1, met=False, leg_failed=True) = "
          f"{harness_ok(1, False, text, 'code')}")
    print("    -> the harness would certify 'leg=code ... -> ok' for a mutant whose")
    print("       code leg passed: the leg attribution is vacuous.")

    print()
    print("### 3. which committed battery receipts the harness can produce")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rb", os.path.join(BAT, "run-battery.py"))
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    producible = set(rb.MUTANTS) | {"control"}
    onfile = {f[:-4] for f in os.listdir(BAT) if f.endswith(".out")}
    print(f"    harness MUTANTS keys : {sorted(rb.MUTANTS)}")
    print(f"    receipts producible   : {sorted(producible)}")
    print(f"    receipts on disk      : {sorted(onfile)}")
    print(f"    ORPHAN receipts (on disk, no harness entry): {sorted(onfile - producible)}")
    import json
    prereg = json.load(open(os.path.join(
        BAT, "..", "..", "preregistration.json")))
    named = [re.search(r"(m-[a-z-]+)", s).group(1) for s in prereg["controls"]["c1_kill_battery"]["mutants"]]
    print(f"    prereg named mutants  : {named}")
    print(f"    prereg names NOT in harness MUTANTS: {sorted(set(named) - set(rb.MUTANTS))}")
    print(f"    harness MUTANTS NOT named in prereg: {sorted(set(rb.MUTANTS) - set(named))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
