#!/usr/bin/env python3
"""Replays run-battery.py's exact kill predicate against receipts it did not produce.

The harness (line 154-158) decides a kill with:
    leg_failed = f"{leg} " in "\\n".join(ln for ln in text.splitlines()
                                         if ln.startswith("detail: "))
    ok = rc == 1 and not met and leg_failed
This script shows that `leg_failed` is satisfied by a receipt in which the named leg
PASSED, on the frozen battery's own files. Run:
    python3 leg-check.py <receipt-dir>
"""
import sys

B = sys.argv[1] if len(sys.argv) > 1 else "."


def leg_failed(text, leg):
    return f"{leg} " in "\n".join(ln for ln in text.splitlines() if ln.startswith("detail: "))


def met(text):
    return "met=True" in text.splitlines()[1]


print("A. the predicate against the positive control (every leg passed, met=True):")
control = open(f"{B}/control.out").read()
for leg in ("bind", "sealed", "code", "twopass", "envnames", "hostlibs", "rehash", "newrow"):
    print(f"   leg={leg:<9} leg_failed={leg_failed(control, leg)}")

print("\nB. a receipt relabelled to a leg that passed: verdict the harness would print")
for name, leg in (("m-member-flip", "code"), ("m-text-flip", "rehash"), ("m-ldpreload", "hostlibs")):
    text = open(f"{B}/{name}.out").read()
    ok = (not met(text)) and leg_failed(text, leg)  # rc==1 in every one of these receipts
    print(f"   {name} labelled leg={leg!r}: met={met(text)} leg_failed={leg_failed(text, leg)}"
          f" -> {'ok' if ok else 'BATTERY-FAIL'}")
print("\n   For comparison, the header field the harness never reads:")
for name in ("m-member-flip", "m-text-flip", "m-ldpreload"):
    hdr = open(f"{B}/{name}.out").read().splitlines()[1]
    print(f"   {name}: {hdr[:160]}")
