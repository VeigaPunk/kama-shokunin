# R2Rerun — C2 independent re-measurement (round 49, kama lane)

**Verdict: C2 met=True at tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, reproduced identically on two runs (byte-identical receipts, exit 0 both), and correctly fails at base `438127bc01ff3b99f98468549d58046f932490ef` exactly per the frozen control; counter bytes equal preregistration `counter_sha256`.**

## 1. Counter byte verification (preregistration.json, C2)

Expected `counter_sha256`: `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945` (preregistration.json `claims[1].counter_sha256`).

```
$ sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-append-audit-v4-check.py
26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945  .../round49-append-audit-v4-check.py
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 36d5ed2681111b68c180f8ab1646d8dc9beaedee:tools/round49-append-audit-v4-check.py | sha256sum
26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945  -
$ sha256sum /fast/scratch/hyaku/kama-r49/R2Rerun/lane/tools/round49-append-audit-v4-check.py
26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945  .../lane/tools/round49-append-audit-v4-check.py
```

All three (fleet working tree, blob at the preregistration commit `36d5ed2`, fresh clone) hash to the preregistered value.

## 2. Clone setup

`git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r49/R2Rerun/lane` succeeded; `git rev-parse --show-toplevel` = `/fast/scratch/hyaku/kama-r49/R2Rerun/lane`, `HEAD` = `122c4ee95701587cef7f4342c3d175622ec2f4ad` (lane branch head sits past the measured build commit — expected; the counter reads the tree of the passed `--tip` via `git archive`, so HEAD is irrelevant to the measurement). Both measured commits present as objects (`cat-file -t` → commit/commit), `438127bc` verified ancestor of `74558c71` (`merge-base --is-ancestor` → 0).

## 3. Runs (all three with the clone counter; `--scratch $S`; standard output captured per run)

Command (twice at tip, once at base):
```
python3 $S/lane/tools/round49-append-audit-v4-check.py \
  --repo $S/lane --tip <TIP> --scratch $S --out $OUT/c2-{build,base}.out
```

### Run 1 — tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1` — exit 0
Receipt (`c2-run1.stdout`, 13 lines):
```
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
fixture=1 lane=1 scenarios=8/8 met=True
detail: scenario launder: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'} want {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
detail: scenario native-head: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} want {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
detail: scenario dated-loss: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'status': 'unrestored'} want {'deleted': 25, 'graded': 25, 'status': 'unrestored'}
detail: scenario substring: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario word-token: ok exit 0 (want 0) bad_declarations 0 want 0
detail: scenario negated: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-self: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-named: ok exit 0 (want 0) bad_declarations 0 want 0
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
```

### Run 2 — same tip — exit 0
Receipt `c2-run2.stdout` byte-identical to run 1 (`sha256sum` of both = `c26c1b5b0e96a763b68eb4a56b5636afa6ac7cb5c3b5b3e17699b9e460daf42b`). Deterministic.

### Run 3 — base `438127bc01ff3b99f98468549d58046f932490ef` — exit 1
Receipt (`c2-base.stdout`):
```
tip=438127bc01ff3b99f98468549d58046f932490ef
fixture=0 lane=0 scenarios=4/8 met=False
detail: scenario launder: FAIL exit 0 (want 1)
detail: scenario native-head: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} want {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
detail: scenario dated-loss: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'status': 'unrestored'} want {'deleted': 25, 'graded': 25, 'status': 'unrestored'}
detail: scenario substring: FAIL exit 0 (want 1)
detail: scenario word-token: ok exit 0 (want 0) bad_declarations 0 want 0
detail: scenario negated: FAIL exit 0 (want 1)
detail: scenario wildcard-self: FAIL exit 0 (want 1)
detail: scenario wildcard-named: ok exit 0 (want 0) bad_declarations 0 want 0
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 > natively exempt 65
```
Lines 1–13 equal the frozen control `.ufo/waves/round-49/controls/base.c2.out` lines 1–13 exactly (control adds a trailing `exit=1`, which my captured `echo` documented as exit code 1).

All three runs had empty stderr (`wc -c` = 0). No `--out` divergence: `c2-build.out` (after run 2) and `c2-base.out` equal the respective captured stdout receipts (sha256 `c26c1b5b…` / `ab09fef7…`).

## 4. Claim cross-check (calibration)

The C2 claim "grades 7 more lines of the `0718b6ab` SCORECARD.md event (ungraded 72 -> 65; they are held, so the event stays restored)" is confirmed by the measured delta: base `ungraded 72 > natively exempt 65` (lane leg fails, `ungraded_lines 89`) → tip `ungraded 65 <= natively exempt 65` (lane leg passes, `ungraded_lines 82`). Delta = 7 lines. All 8 fixture scenarios pass at tip, including the four v4 escapes (launder, substring, negated, wildcard-self) that fail at base, so the fix is attributable to the v4 definitions in the build, not to fixture drift.

## 5. Findings / defects

No defects found in scope. The counter executed per its docstring contract on all three runs; no deviation from expected outputs; no leftover state (counter removes its `--scratch` temp dirs on exit; scratch cleaned after this report; no llama-server processes seen — `pgrep -f llama-server` empty, nothing started by C2).

## 6. Verification gaps

- Controls other than `base.c2.out` (junk-* variants) were not re-run; they constrain C1 semantics and other seats (`base.c2.out` was cross-checked above and reproduced exactly).
- Counter was executed against a fresh full clone; the fleet working-tree copy was hashed but not executed (identical bytes, so execution equivalence is implied by the hash match).

## 7. Environment / tools

No tools installed or upgraded (none needed; `python3` interpreter already present). No services started; no repo mutations anywhere (fleet lane and clone read-only; clone removed on cleanup).
