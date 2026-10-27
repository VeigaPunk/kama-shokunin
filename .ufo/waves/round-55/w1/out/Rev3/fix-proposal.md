# Rev3 proposed fixes (NOT applied; frozen artifacts are findings, not edit targets)

All paths relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## D1 — C1 frozen battery list vs executed battery (calibration, blocking)

Finding (observed):
- `.ufo/waves/round-55/preregistration.json:44` froze four mutants including `m-ldaudit-writable (code leg)`; `:19` requires each named mutant receipt to print `met=False`; `:20` makes `met=True` on any battery mutant a falsifier.
- `.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out:2` prints `... met=True`.
- `.ufo/waves/round-55/c1/battery/run-battery.py:23-85` no longer contains `m-ldaudit-writable`; it runs `m-text-flip` (not in the frozen list) and treats `m-ldaudit-foreign` as a `"vector"` expected to print `met=True` (see `:57-62`, `:137-138`), an exemption the frozen kill rule does not state. `m-extra-in-tree.out` has no mutant in the driver either.

Command that shows it:
```
grep -n 'm-ldaudit-writable\|m-text-flip' .ufo/waves/round-55/preregistration.json .ufo/waves/round-55/c1/battery/run-battery.py
sed -n 2p .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
```

Remediation (choose one; the preregistration is frozen and must not be edited in place):

### (a) Honest-stop reading (no edit; record in the round-55 report)
C1 is falsified by its own frozen kill rule; score no claim, keep operability 8, and cite the two commands above. This is the reading a non-author verifier applies to the frozen documents.

### (b) Freeze-drafting-error errata + corrected re-freeze (round 56)
Record the post-freeze substitution and the vector class, then re-freeze a corrected claim in a new attempt. Proposed lesson errata diff (insert after `corpus/lessons/round-55.md:76`):

```diff
--- a/corpus/lessons/round-55.md
+++ b/corpus/lessons/round-55.md
@@ -73,6 +73,19 @@
   the kill battery (`.ufo/waves/round-55/c1/battery/`) whose named mutants must each
   fail the frozen counter. Fix shown able to fail: the base control itself is the
   red-before state (`dropped=1` → `met=False`, committed receipt), and each battery
   mutant receipt names the leg it kills.
+- **class: undisclosed — the executed battery was not the frozen battery.**
+  Evidence: `preregistration.json:44` froze `m-ldaudit-writable (code leg)` and
+  `:19` requires every named mutant receipt to print `met=False`; the committed
+  receipt `c1/battery/m-ldaudit-writable.out:2` prints `met=True` (LD_AUDIT is
+  outside the counter's `BAD_ENV` set, `tools/round54-replay-code-audit.py:146`).
+  The committed driver (`c1/battery/run-battery.py:23-85`) runs `m-text-flip`
+  instead — a mutant the frozen list does not name — and also carries receipts
+  (`m-extra-in-tree`, `m-ldaudit-writable`) that no committed mutant defines. Under
+  the frozen kill rule (`preregistration.json:20`) a named mutant printing
+  `met=True` is a falsifier, not a void vector; the "each battery mutant receipt
+  names the leg it kills" claim above is false for three of the seven receipts.
+  Captured-by: round-55 Rev3 outside check. Fix: correction named in the round-55
+  report; a re-freeze must name the vector class before data.
 - **class: vacuous — a counter/target a do-nothing control can reach (caught before data).**
   Evidence: the first round-55 freeze re-frozen C2's BASE to the round-54 tip
   (`3a600d2f`); the pre-freeze base-control run then printed
```

Proposed re-freeze fragment (round 56, replaces `controls.c1_kill_battery`):

```json
"c1_kill_battery": {
  "description": "named mutants of the replay tool in a fixture clone; kind=kills must print met=False with the named leg failing; kind=vector must be named before data and its met=True is evidence of an out-of-predicate vector, never an admissible survivor",
  "mutants": [
    {"name": "m-ldpreload",        "leg": "envnames", "kind": "kills"},
    {"name": "m-text-flip",        "leg": "code",     "kind": "kills"},
    {"name": "m-member-flip",      "leg": "rehash",   "kind": "kills"},
    {"name": "m-ldaudit-foreign",  "leg": "hostlibs", "kind": "vector"},
    {"name": "m-ldaudit-writable", "leg": "code",     "kind": "vector"}
  ],
  "receipt_dir": ".ufo/waves/round-56/c1/battery/",
  "summary_receipt": ".ufo/waves/round-56/c1/battery/summary.out",
  "reproducible_from": "c1/battery/run-battery.py at the measured commit; every mutant definition lives in the driver"
}
```

with kill rule: "... falsified if ... any battery mutant of kind=kills prints met=True, if the driver's committed mutant set differs from this list, or if a battery receipt lacks its exit code in the committed summary."

Alternative (extends the predicate instead of exempting): add `"LD_AUDIT"` to `BAD_ENV` at `tools/round54-replay-code-audit.py:146`, which changes the counter bytes → new counter sha256 and a new claim, with `m-ldaudit-writable` re-frozen as `kind=kills`.

## D2 — cited census receipt does not exist

Finding: `corpus/lessons/round-55.md:95` and `:101` cite `.ufo/waves/round-55/census/end.out`; the file is absent from the `9c60eae6`/`HEAD` trees and from disk.

Fix (preferred): generate it from the lesson's own command at the round end, then commit it:
```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
  --root /home/vgpnk/Projects/shokunin kama \
  > .ufo/waves/round-55/census/end.out 2>&1
printf 'exit=%s\n' "$?" >> .ufo/waves/round-55/census/end.out
```
(verified red→green: the same command exits 0 on the `9c60eae6` tree today; see `Rev3/census-validate-fleet-kama.out`).

Alternative: strike the receipt parenthetical at `:95`/`:101` and cite the wrap-up commit instead.

## D3 — battery receipts lack exit codes and two are unreproducible

Fix: commit `run-battery.py`'s stdout summary (`run-battery.py:146-148`, which carries `exit=`/`met=`/`ok`) as `c1/battery/summary.out`; either add `m-extra-in-tree` and `m-ldaudit-writable` definitions to `MUTANTS` (`run-battery.py:23`) or relabel those `.out` files as exploratory vectors and move them outside `battery/` (a directory the frozen prereg names as the mutant receipt dir).
