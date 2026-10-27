# R02ProfileReturnBinding — profile return-event capture audit (round 59, kama)

Seat: R02ProfileReturnBinding (leaf; no subagents). Target: `tools/round59-battery-outcome-check.py`
at measured C1 commit `aca8d0067ea25627c5015c2193c843965148bc8e` (worktree verified byte-identical:
`diff -q` of `git show aca8d006...:tools/round59-battery-outcome-check.py` vs worktree → no output,
exit 0). Attacked claims: C1 predicate sentence clauses "its own `--expect` maps to that leg's
returned `ld_audit` value and declared exit" and "A leg that discards its result ... must not
meet"; counter kill rule "any outcome-unbound control accepted". Seat work is falsification, not
judgement; verdicts below are recommendations.

Environment: Python 3.14.8, Arch x64. No installs (pacman/uv/binary) — none needed. All scratch
under `/fast/scratch/hyaku/kama-r59/R02ProfileReturnBinding/` with `TMPDIR` set explicitly; lane
untouched except this report. Fixture git commands used explicit `git -C`, toplevel asserted equal
to the fixture dir before commit, fixed identity `kama-r59-probe` used only inside scratch fixtures.

## Mechanics audited

- `fake_run` (lines 62-75): attributes every battery subprocess call to `stack[-1]`; fault flip at
  line 72 (`if rec["label"] == fault_label`).
- `profile` return branch (line 114-116): pops and records `returned=arg` only when
  `stack[-1]["label"]` equals the frame's CURRENT `frame.f_locals.get("label")` (call-time label
  comes from `co_varnames[0]`, line 111-112). Binding is by label equality against stack top, not
  frame identity.
- Parent verdict (lines 184-198): `returns_ok[label] = frame.get("returned") is True`; fault runs
  pass on `not returns_ok.get(fault, False)` — line 197 cannot distinguish "captured False" from
  "never captured (None)".

## Answer to the seat question (positive result)

For the genuine battery, every run return IS tied to the correct frame — across sequential legs,
all four fault injections, nesting, and exceptions:

- Genuine baseline + 4 fault runs through the frozen checker (5 child runs each): baseline
  `passed=True exit=0`, every fault run `passed=True exit=1` with the fault leg `returned=False`
  (captured, not None) and other legs `returned=True`. Reproduced frozen C1 counter matrix over
  all 20 enumerated worlds: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`,
  counter exit 0 — frozen behavior reproduced in isolation, not overturned.
- Instrumented probe copy of the frozen checker (scratch-only; identical except the profile hook
  additionally records whether the popped record is the returning frame's own record): genuine
  baseline events show 8/8 pops with `top_is_own=True` (`pop='identity'`), depth 0→1→0 per leg;
  fault run `m-drop-ldaudit`: `return m-drop-ldaudit arg=False popped top_is_own=True`.
- Exceptions (V1-exc probe: round56-counter leg raises `KeyError` after its subprocess call, main
  swallows): CPython 3.14.8 fires the profile `return` event on unwind with `arg=None` and pops
  the CORRECT frame (`return round56-counter arg=None popped top_is_own=True`); subsequent legs
  unaffected; the world is honestly rejected (met=False). No stale-stack corruption.
- Nesting (V3-nest: tracked inner `run` live inside outer `run`): LIFO identity pops —
  `call round56-counter depth->1 | call round56-counter-inner depth->2 | return
  round56-counter-inner popped top_is_own=True | return round56-counter popped top_is_own=True`.
  Same-label recursion (V4-nest-same) also pops identity LIFO. Both worlds are honestly rejected
  by the parent `len(frames)==4`/label-set checks (false reds, correct verdicts).

## Findings by severity

### F1 — HIGH — false green: outcome-unbound `run()` accepted by the frozen counter

Attacked clause: "A leg that discards its result ... must not meet"; kill rule "any
outcome-unbound control accepted -> claim not met".

Crafted control `V2-sneaky` (full battery in scratch `crafted/V2-sneaky.py`): `run()` computes the
observation faithfully but RETURNS LITERAL `True` unconditionally (outcome-unbound return), and on
a failing leg drifts its local `label = label + "-drifted"` before returning; failures propagate
to exit 1 via a module-level side channel, not via the returned values.

Result — frozen checker passes all 5 runs and the frozen counter ACCEPTS the world:

```
$ python3 extract/round59-c1-counter.py --repo worlds-repo2 --tip HEAD --work <scratch>
...
detail: N12-ignore-leg-result accept exit=0        <- V2-sneaky bytes as an N12-class control
genuine=1/1 benign=3/3 noop_rejected=15/16 errors=0 met=False
counter exit=1   (counter correctly reports not-met; the ACCEPT line is the defect)
```

Mechanism, proven with the instrumented probe copy on the fault run:

```
return round56-counter-drifted arg=True NO-POP top_label='round56-counter'
frame label='round56-counter' ... returned=None pop='skipped-label-mismatch' returned_uncaptured=True
```

The label-equality pop gate (line 114) skips the pop, so the leg's actual return — `True`, the
smoking gun of outcome-unboundness, visible as `returned_uncaptured=True` — is discarded; the
parent then reads `returned=None` and line 197 `not returns_ok.get(fault, False)` scores it as
"fault leg did not return True". All 4 fault runs pass on `exit==1` (faked by the side channel)
plus other legs `True`. The uncaptured-return and captured-False cases are indistinguishable to
the verdict. Conditional drift is essential and invisible: unconditional drift (V6) or a renamed
first parameter (V7) leaves ALL returns uncaptured and is honestly rejected in the baseline; the
failure-conditional drift leaves the baseline fully green while disarming every fault run.

### F2 — MEDIUM — false green: legs blind to the declared exit accepted

Attacked clause: predicate "accepted only when its own named expected outcome is tied to that
leg's actual observed field/value **and exit**".

Crafted control `V5-exitblind`: `run()` consumes the leg via `subprocess.check_output` (patched
funnel returns stdout only; the frozen patch at line 87 drops kwargs and rc) and never observes
the declared exit; pass/fail binds to the `ld_audit` field alone.

Result — frozen counter ACCEPTS the world (same harness as F1, V5 bytes as the control):

```
detail: N12-ignore-leg-result accept exit=0
genuine=1/1 benign=3/3 noop_rejected=15/16 errors=0 met=False
counter exit=1
```

The capture itself is faithful here (`returned=True` recorded); the hole is that neither the
per-leg `calls_ok` nor `returns_ok` criteria ever verify that the leg's return depended on the
declared exit, so the "and exit" half of the frozen clause is unenforced. (Real battery's N16
decoy call is caught only incidentally by `len(calls)==1`.)

### F3 — LOW — capture infidelity on drift/rename (safe verdicts, unfaithful frames)

V6-drift-all (unconditional `label = label + "-x"`) and V7-paramrename (first parameter `leg`):
every `run` return is uncaptured — probe shows `return base-old-counter-x arg=True NO-POP` and
`return None arg=True NO-POP` respectively, i.e. frozen frames would record `returned=None` while
the battery actually returned `True` in all legs. Both worlds are rejected (met=False), so this
is a false-negative/fragility defect, not a green: the return branch (line 114) hardcodes
`f_locals.get("label")` while the call branch (line 111) reads `co_varnames[0]` — an extraction
asymmetry — and any post-call mutation of the label local silently disarms return capture. Under
the drift the stack also stays over-populated (V6 depths 0,1,2,3), but `fake_run` attribution and
fault flips remain correct because each leg pushes its own record before its body runs.

## Residual risk

- The F1/F2 controls are OUTSIDE the 16 enumerated variants; the round-59 measured C1 pass at
  `aca8d006` over the enumerated worlds is real (reproduced, counter exit 0) and is not overturned
  by this seat. The kill rule, however, quantifies over ANY outcome-unbound control; F1/F2 show
  that quantification is falsifiable, i.e. the counter's world set is not saturating for the
  checker's guarantee. Relevant to calibration (7): the checker passes its enumerated controls
  while a strictly stronger reading of its own kill rule fails.
- Theoretical, unprobed: a drifted label crafted to equal a DIFFERENT leg's label could bind a
  later return event to the wrong record (label-equality pop against stale top); V2-sneaky's
  `-drifted` suffix avoids collision, and no collision path was constructed.
- Untested shapes: generator-based `run` (yield/resume semantics vs profile events), threaded or
  asyncio legs (setprofile is per-thread; missed frames would produce honest reds), battery retry
  of a leg (caught by `len(calls)==1`).

## Verification gaps

- Verdicts for F1/F2 cite the frozen counter and frozen checker bytes (`extract/` copies, diffed
  byte-identical to `aca8d006`); the probe-copy (`crafted/probe-checker.py`) was used only to
  observe pop binding and never for verdicts.
- Generator/thread shapes not probed (listed above as residual, unexercised).
- No S517/S518 external spot-check claims made (frozen condition: not recorded).

## Commands and exits (all under scratch, TMPDIR explicit)

- `python3 probe_run.py` (driver: STEP A frozen counter matrix → exit 0 `met=True`; STEP C frozen
  checker on crafted worlds: V1-exc/V3-nest/V4-nest-same/V6-drift-all/V7-paramrename met=False,
  V2-sneaky/V5-exitblind met=True; STEP D instrumented forensics; STEP E V2-sneaky-as-N12 frozen
  counter → `N12-ignore-leg-result accept exit=0`, counter exit 1).
- V5-as-N12 frozen counter rerun: `counter exit=1`, `detail: N12-ignore-leg-result accept exit=0`.
- Scratch tree removed before yield; lane modified only by this report file.
