# X03OutcomeCases — outcome checker: baseline + four injected faults

Seat: X03OutcomeCases (executor leaf), round 59 / kama, wave w1. Date 2026-10-27.
Role: falsification, not judge. Advisory only. No source edits, no commits, no installs.

## Subject and identities

- Attacked clause: `.ufo/waves/round-59/controls/freeze.txt`, C1 sentence — "The checker must
  establish for each named `run`/mutant leg that its own `--expect` maps to that leg's returned
  `ld_audit` value **and declared exit**, with only that leg's predicate determining its pass/fail".
  Checker predicate string: `C1-r59 each named leg returns a bound expected outcome; one-leg faults propagate`.
  The four injected faults are the checker's own `LABELS` (`tools/round59-battery-outcome-check.py:17`):
  `base-old-counter`, `round56-counter`, `m-drop-ldaudit`, `mutant-assert`.
- Lane HEAD (read-only): `/home/vgpnk/Projects/shokunin/kama-shokunin` @ `4a541190b6d494a4e99116249632e99aab80adcc`.
- Measured tip under test: `aca8d0067ea25627c5015c2193c843965148bc8e` ("round-59: score counterfactual leg failures").
- Checker blob identity: worktree `git hash-object tools/round59-battery-outcome-check.py`
  = `64e91f64c05f057f7ae97c50b784aca642f63e59`; `git rev-parse aca8d006:tools/round59-battery-outcome-check.py`
  = `64e91f64c05f057f7ae97c50b784aca642f63e59` (identical, so the run is the measured blob).
- Scratch: `TMPDIR=/fast/scratch/hyaku/kama-r59/X03OutcomeCases` (removed before yield; receipts below).
- No installs were needed; no version/channel/reason to record.

## Verdict

**Required case: holds.** The checker, run directly against a genuine fixture built from the
measured tip, passes baseline 5/5 (`met=True`, exit 0) and, for each of the four injected faults,
exactly the intended leg returns non-`True` while the other three legs return `True` and the
battery exits 1.

**Calibration finding (outside the required four-fault receipt):** the four faults cannot
establish the "and declared exit" conjunct. `fake_run` derives the child's exit code from the
same field comparison (`rc = 0 if expected == observed else 1`,
`tools/round59-battery-outcome-check.py:68-75`), so every fault flips field and exit together.
Two probe batteries that bind only one conjunct (field-only, exit-only) each pass all five
checker runs with `met=True`. Evidence in section 5. This does not overturn the required
receipt; it bounds what the receipt can be cited for.

I did not run the C1 counter (X01/X02 seats). The committed control receipt
`.ufo/waves/round-59/controls/c1-candidate-final.out` (tip `aca8d006`, genuine 1/1, benign 3/3,
no-ops 16/16, exit 0) is context only, not evidence produced by this seat.

## 1. Integrated run (checker main, builds its own genuine fixture from the tip)

```
cd /fast/scratch/hyaku/kama-r59/X03OutcomeCases
export TMPDIR=/fast/scratch/hyaku/kama-r59/X03OutcomeCases
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-battery-outcome-check.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e --out integrated.out
echo "EXIT=$?"
```

Verbatim output (exit 0):

```
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 each named leg returns a bound expected outcome; one-leg faults propagate
runs=5 passed=5/5 errors=0 met=True
{"error": null, "exit": 0, "fault": "baseline", "labels": true, "passed": true, "per_leg": {"base-old-counter": {"call": true, "returned_true": true}, "m-drop-ldaudit": {"call": true, "returned_true": true}, "mutant-assert": {"call": true, "returned_true": true}, "round56-counter": {"call": true, "returned_true": true}}}
{"error": null, "exit": 1, "fault": "base-old-counter", "labels": true, "passed": true, "per_leg": {"base-old-counter": {"call": true, "returned_true": false}, "m-drop-ldaudit": {"call": true, "returned_true": true}, "mutant-assert": {"call": true, "returned_true": true}, "round56-counter": {"call": true, "returned_true": true}}}
{"error": null, "exit": 1, "fault": "round56-counter", "labels": true, "passed": true, "per_leg": {"base-old-counter": {"call": true, "returned_true": true}, "m-drop-ldaudit": {"call": true, "returned_true": true}, "mutant-assert": {"call": true, "returned_true": true}, "round56-counter": {"call": true, "returned_true": false}}}
{"error": null, "exit": 1, "fault": "m-drop-ldaudit", "labels": true, "passed": true, "per_leg": {"base-old-counter": {"call": true, "returned_true": true}, "m-drop-ldaudit": {"call": true, "returned_true": false}, "mutant-assert": {"call": true, "returned_true": true}, "round56-counter": {"call": true, "returned_true": true}}}
{"error": null, "exit": 1, "fault": "mutant-assert", "labels": true, "passed": true, "per_leg": {"base-old-counter": {"call": true, "returned_true": true}, "m-drop-ldaudit": {"call": true, "returned_true": true}, "mutant-assert": {"call": true, "returned_true": false}, "round56-counter": {"call": true, "returned_true": true}}}
```

`runs=5 passed=5/5 errors=0 met=True`; baseline `exit=0`, every fault `exit=1`, `labels=true`
in all five (exactly the four expected labels, no duplicates), and exactly one
`returned_true=false` per fault.

## 2. Genuine fixture identity (independent of the checker's internal mkdtemp)

Fixture built under `/fast/scratch/hyaku/kama-r59/X03OutcomeCases/fixture`, `git init` +
`git -c user.name=x03-r59 -c user.email=x03-r59@invalid commit` inside the fixture only;
`git rev-parse --show-toplevel` printed `/fast/scratch/hyaku/kama-r59/X03OutcomeCases/fixture`
(asserted equal to the fixture path before commit). Fixture HEAD
`30139e9d80232990d42723951a69fd86114cea35`.

Blob identity, tip vs fixture (`git rev-parse <tip>:<path>` == `git rev-parse HEAD:<path>`):

```
OK   .ufo/waves/round-56/preregistration.json cf222614fea85304710e443fdf0227ac76463007
OK   tools/round56-env-leg-battery.py 1f4ebff0a62cc9e09d90c6a2f44b613c7027235b
OK   tools/round56-env-leg-test.py 7d5cad3bcecf0eaf6d30ffbe74a0320e99bc6c23
OK   tools/round54-replay-code-audit.py e3cfc996344586851b7e20b3591c57248b86c456
OK   tools/round56-replay-code-audit.py 11535fc02e7637bf3b6d9bb02248f062b72a3c03
OK   tools/round59-battery-outcome-check.py 64e91f64c05f057f7ae97c50b784aca642f63e59
```

## 3. Checker child mode, one process per case (no checker-main aggregation)

```
F=/fast/scratch/hyaku/kama-r59/X03OutcomeCases/fixture
for fault in baseline base-old-counter round56-counter m-drop-ldaudit mutant-assert; do
  flag=""; [ "$fault" != baseline ] && flag="$fault"
  python3 "$F/tools/round59-battery-outcome-check.py" --child --repo "$F" --tip HEAD \
    --source "$F/tools/round56-env-leg-battery.py" --out "out/$fault.json" --fault "$flag"
  echo "CHILD $fault exit=$?"
done
```

```
CHILD baseline exit=0
CHILD base-old-counter exit=0
CHILD round56-counter exit=0
CHILD m-drop-ldaudit exit=0
CHILD mutant-assert exit=0
```

All stderr files 0 bytes. Battery stdout per run (the observed field/exit that the harness
returned to each leg):

```
=== baseline
comparator-selftest: substring-counterexample expected=detected field=undetected accepted=False -> pass
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
m-drop-ldaudit-positive-target: ld_audit=missed exit=1 -> killed
=== base-old-counter
comparator-selftest: ... -> pass
base-old-counter: ld_audit=detected exit=1 -> fail
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
m-drop-ldaudit-positive-target: ld_audit=missed exit=1 -> killed
=== round56-counter
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=missed exit=1 -> fail
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
m-drop-ldaudit-positive-target: ld_audit=missed exit=1 -> killed
=== m-drop-ldaudit
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=detected exit=1 -> fail
m-drop-ldaudit-positive-target: ld_audit=missed exit=1 -> killed
=== mutant-assert
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
m-drop-ldaudit-positive-target: ld_audit=detected exit=0 -> SURVIVED
```

In every fault run the flipped leg is exactly the intended one; the `mutant-assert` fault flips
only `assert_mutant_breaks_detection` (the `m-drop-ldaudit` `run` leg stays `pass`), so the
return-value attribution is per-leg, not global.

## 4. Independent frame accounting (does not trust `passed`)

Script: load each `out/<case>.json`, enumerate `frames`, print `returned is True` per label.

```
baseline         battery_exit=0 frames=4 false=[] true=['base-old-counter', 'round56-counter', 'm-drop-ldaudit', 'mutant-assert']
base-old-counter battery_exit=1 frames=4 false=['base-old-counter'] true=['round56-counter', 'm-drop-ldaudit', 'mutant-assert']
round56-counter  battery_exit=1 frames=4 false=['round56-counter'] true=['base-old-counter', 'm-drop-ldaudit', 'mutant-assert']
m-drop-ldaudit   battery_exit=1 frames=4 false=['m-drop-ldaudit'] true=['base-old-counter', 'round56-counter', 'mutant-assert']
mutant-assert    battery_exit=1 frames=4 false=['mutant-assert'] true=['base-old-counter', 'round56-counter', 'm-drop-ldaudit']
```

Each frame carries exactly one `subprocess` argv with both flags, and the per-leg `--expect`
is the leg's own declared expectation (from the genuine battery, `tools/round56-env-leg-battery.py:52-72`):

```
base-old-counter ['python3', .../tools/round56-env-leg-test.py, '--counter', .../tools/round54-replay-code-audit.py, '--expect', 'missed']
round56-counter  ['python3', .../tools/round56-env-leg-test.py, '--counter', .../tools/round56-replay-code-audit.py, '--expect', 'detected']
m-drop-ldaudit   ['python3', .../tools/round56-env-leg-test.py, '--counter', /virtual/round59/counter.py, '--expect', 'missed']
mutant-assert    ['python3', .../tools/round56-env-leg-test.py, '--counter', /virtual/round59/counter.py, '--expect', 'detected']
```

## 5. Calibration probes (unenumerated; outside the required receipt)

Mechanism under attack: `tools/round59-battery-outcome-check.py:68-75`

```
observed = result_for(counter) if counter else ""
...
if rec["label"] == fault_label:
    observed = "missed" if observed == "detected" else "detected"
...
rc = 0 if expected == observed else 1
```

The simulated exit is computed from the same equality as the field, so a fault always changes
both. Consequence: the four faults cannot distinguish a leg that binds the field from a leg
that binds the declared exit, nor detect a leg that checks only one of the two.

Probe A — exit-blind battery (`fx-exitblind`, HEAD `64f54550d01b150d9ffc4025abad198b1683ba03`),
only diffs from the genuine battery:

```
-    ok = p.returncode == 0 and exact_field_match(fields, "ld_audit", expected)
+    ok = exact_field_match(fields, "ld_audit", expected)
-    ok = p.returncode == 1 and fields.get("ld_audit") == "missed"
+    ok = fields.get("ld_audit") == "missed"
```

```
python3 "$F/tools/round59-battery-outcome-check.py" --repo "$F" --tip HEAD --out out/exitblind.out
EXITBLIND_CHECKER_EXIT=0
tip=64f54550d01b150d9ffc4025abad198b1683ba03
runs=5 passed=5/5 errors=0 met=True
"fault": "baseline", "labels": true, "passed": true
"fault": "base-old-counter", "labels": true, "passed": true
"fault": "round56-counter", "labels": true, "passed": true
"fault": "m-drop-ldaudit", "labels": true, "passed": true
"fault": "mutant-assert", "labels": true, "passed": true
```

Probe B — field-blind battery (`fx-fieldblind`, HEAD `806f41683b892cca174c35ecb14b785e629edc67`):

```
-    ok = p.returncode == 0 and exact_field_match(fields, "ld_audit", expected)
+    ok = p.returncode == 0
-    ok = p.returncode == 1 and fields.get("ld_audit") == "missed"
+    ok = p.returncode == 1
```

```
python3 "$F/tools/round59-battery-outcome-check.py" --repo "$F" --tip HEAD --out out/fieldblind.out
FIELDBLIND_CHECKER_EXIT=0
tip=806f41683b892cca174c35ecb14b785e629edc67
runs=5 passed=5/5 errors=0 met=True
"fault": "baseline", "labels": true, "passed": true
"fault": "base-old-counter", "labels": true, "passed": true
"fault": "round56-counter", "labels": true, "passed": true
"fault": "m-drop-ldaudit", "labels": true, "passed": true
"fault": "mutant-assert", "labels": true, "passed": true
```

Both are accepted green by the checker self-test even though neither leg "maps `--expect` to the
returned `ld_audit` value **and declared exit**" in the frozen sentence's sense.

Boundary check on the enumerated no-op set (checker only, single fixture each, from tip blobs):

```
N12-ignore-leg-result    checker_exit=1 runs=5 passed=4/5 errors=0 met=False (baseline passed; fault round56-counter exit=0, so propagation fails)
N13-wrong-leg-expected   checker_exit=1 runs=5 passed=0/5 errors=0 met=False (baseline round56-counter returned false)
N14-ignore-mutant-result checker_exit=1 runs=5 passed=4/5 errors=0 met=False (baseline passed; fault mutant-assert exit=0, so propagation fails)
N15-duplicate-leg-label  checker_exit=1 runs=5 passed=0/5 errors=0 met=False (labels=false, round56-counter call=false)
N16-decoy-counter-call   checker_exit=1 runs=5 passed=0/5 errors=0 met=False (call=false for three legs)
```

So N12/N14 are rejected only through fault-run exit propagation (baseline alone accepts them);
N13/N15/N16 fail at baseline. This is consistent with the committed counter control receipt and
is reported as boundary context only — those variant verdicts belong to X04/X05/X06.

## Findings

1. F1 (required, positive): with the genuine battery at `aca8d006`, the outcome checker produces
   baseline all-four-legs-true / exit 0, and each of the four injected faults yields **exactly
   one** false leg — the intended one — plus exit 1 and the exact four labels. Independent frame
   enumeration in section 4 confirms this without relying on the checker's `passed` field.
2. F2 (required, attribution): the `mutant-assert` fault leaves the `m-drop-ldaudit` `run` leg
   true, so the result is attributed to the correct frame; duplicate/missing labels would fail
   `names_ok` (section 5, N15).
3. F3 (calibration gap): the four-fault mechanism cannot test field-vs-exit binding separately.
   Because `rc` is a function of `expected == observed` (lines 68-75), any battery that checks
   only one conjunct still returns the same per-leg booleans under all four faults and passes
   `met=True` (section 5, probes A/B). The frozen sentence's "and declared exit" conjunct is
   therefore not established by this receipt.
4. F4 (model boundary): the child harness replaces `subprocess.run`/`Popen`, `os.system`,
   `tempfile.TemporaryDirectory`, and `Path.read_text/write_text` (lines 78-101), and derives
   `ld_audit` synthetically from a `BAD_ENV` regex over counter source (lines 30-34, 66-70).
   The receipt measures per-leg accounting inside that model, not real `LD_AUDIT` observability.

## Risks and blockers

- No blocker for the required case.
- If the judge reads C1's kill rule "any outcome-unbound control accepted" as covering novel,
  unenumerated controls, probes A and B are accepting controls and the clause is falsified. If
  the kill rule is read as the enumerated finite controls only (freeze wording: "finite controls:
  tests/round59-battery-variants"), the four-fault receipt stands and this is a calibration
  limit, not a violation.
- The checker self-test is internal to the checker; `main` iterates `("", *LABELS)` and accepts
  no caller-supplied fault list, so a fifth fault cannot be scored through the public path.
  `--child --fault bogus` performs no flip: observed run gives battery `exit=0`, all four
  `returned=True` (`out/bogus.json`); child mode computes no pass/fail, so this is not a
  false-green path, just an unscored label. (`main`'s fault branch would require exit 1 and
  the named leg false, so an unknown label could only fail closed if it were reachable there.)
- Scratch `/fast/scratch/hyaku/kama-r59/X03OutcomeCases` was removed after this report was
  written; the receipts above are the retained evidence.

## Not claimed

- No C1/C2 overall verdict, no score or closure change, no discernment progress. External
  S517/S518 spot-check remains unrecorded and is not claimed. No lane/fleet file was modified
  other than this report. C1 counter and C2 were not run by this seat.
