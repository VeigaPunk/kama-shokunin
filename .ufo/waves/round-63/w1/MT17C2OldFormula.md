# MT17C2OldFormula — falsify the C2 counter's sensitivity test

Seat: mutation-tester (leaf, advisory). Attack item: C2 calibration.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane HEAD at scoring time).
Counter: tools/round63-c2-counter.py (unmutated, read from clone and lane archive).
Receipts: .ufo/waves/round-63/w1/out/MT17C2OldFormula/

## 1. Baseline (unmutated counter at the tip)

Command: `python3 tools/round63-c2-counter.py --repo <lane> --tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09 --work <scratch>/work-base`

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```

Baseline is `met=False` for one reason only: `selfdesc_mismatches=8`. The freeze
states that this stays at 8 on purpose at this tip (the L1 re-derives the SCORECARD
head, PROVINCE.md pointers and Planned section after measurement). Every other field
is at its pass value: sens_selftest=4/4, controls 12/12, mismatches=0, errors=0.

Consequence for this attack: at this tip the counter's exit status is `met=False`
regardless of the sensitivity test. A `met=False` printed by a mutant therefore does
not, by itself, prove a kill. The kill is attributed only to the field that moves
relative to baseline: `sens_selftest`.

## 2. Mutant M1 — round-62 sensitivity expression restored

Mutation (clone m1r62, commit 334c6722c81817cdfa9ac1737deb9147fa27b717; diff in
out/MT17C2OldFormula/m1-r62.diff): the body of `is_sensitive` is replaced by the
round-62 expression
`return not (pat in out.replace(pat, "__kama_mut__") and rc == 0 and not dead)`.

Run: from `m1r62/tools/`, `--repo m1r62 --tip 334c6722...`.

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=0/4 controls_rejected=12/12 errors=0 met=False
```

Verdict: **KILLED by sens_selftest=0/4** (baseline 4/4). Not killed by the row-level
`sensitive=` field: it reads 12/12, the same as baseline, because the round-62
expression returns True for any real verdict-true output. The expression is vacuous
on the real rows: it reports every bound row sensitive. The planted-defect self-test
is the only place it is exposed. All four planted checks fail under it, including
the "always-true verdict" plant that the round-62 expression cannot see.

Note: the 12 control families are unchanged (12/12) under M1. No control family
targets `is_sensitive`; the only detector is `sensitivity_selftest()`, whose expected
count `EXPECT_SELFTEST = 4` is a hard-coded constant. That constant is what kills M1.

## 3. Mutant M2 — is_sensitive skips its rc leg

Mutation (clone m2norc, commit 4d30bbfcb436f474e6d2fbf1862b286f8f931e42; diff in
out/MT17C2OldFormula/m2-norc.diff): `is_sensitive` keeps the verdict guard and the
pattern-strip leg but drops the exit-code leg:
`return not vfn(strip_all(out, pat), rc, dead, pat)`.

Run: from `m2norc/tools/`, `--repo m2norc --tip 4d30bbfcb436f474e6d2fbf1862b286f8f931e42`.

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=3/4 controls_rejected=12/12 errors=0 met=False
```

Verdict: **KILLED by sens_selftest=3/4**. Planted check 3 (`p in o and not d`, a verdict
that ignores exit code) was accepted as sensitive once the rc leg is gone; that is
the only plant the rc leg catches. The row-level `sensitive=` field stays 12/12.

Observation: against the frozen `verdict_fn` (which itself requires `rc == 0`), the rc
leg is redundant on real rows, because flipping 0 to 1 always falsifies it. The rc leg
therefore only protects against future verdicts that ignore rc, and it is checked
only by that one planted defect. That is a weak guard, but M2 is caught.

## 4. Three verdict functions a clean strip-all cannot catch

Test: `out/MT17C2OldFormula/vf_test.py` run against the unmutated counter's
`is_sensitive` (imported from the clone at 03a6; no bytecode written). Output
verbatim (`vf_test.out`):

```
W1 any-record: verdict=True is_sensitive=True (rc=0, fail record present)
W2 last-line: verdict=True is_sensitive=True (rc=0, fail record present)
W3 key-only: verdict=True is_sensitive=True (rc=0, fail record present)
frozen verdict_fn on W3 output: True sensitive: True
W1 honest: True W2 honest: True W3 honest: True
```

Each function is sensitive in the counter's sense: its verdict is true on the real
output, and it flips to false when the pattern is stripped and when the rc is flipped.
Each accepts an output that contradicts the claim. The counter tests dependence on
the pattern, not sufficiency for the claim. None of the three can be caught by
strip-all or the rc leg.

- W1 any-record: `any(pat in line for line in out.splitlines()) and rc == 0`.
  Accepts a run where one record passes and another fails, e.g.
  `{"status": "passed"}` plus `{"status": "failed"}` (pattern `"status": "passed"`).
  Stripping removes the only passing record, so the verdict flips and is counted
  sensitive. The gguf-identity pattern (`"status": "passed"`) has this shape; I did
  not run that tool to confirm its per-record output, so this is a class risk only.
- W2 last-line: `pat in last non-empty line and rc == 0`. Accepts a failing record
  earlier in the run whenever the final summary line carries the pattern.
  Stripping flips the verdict; rc flipping flips it. Sensitive, and wrong.
- W3 key-only: the key before `=` in the pattern is the only thing checked. Accepts
  `IA_SELFTEST pass=3 fail=2` at rc 0. The same defect is present in the frozen
  manifest: the instrument-agreement pattern is `IA_SELFTEST pass=` with no `fail=0`,
  and `verdict_fn` on the output above returns True and is_sensitive True.
  The tool exits 1 on any fail (tools/instrument-agreement.py:116-117), so the frozen
  binding is defended only by the exit code, not by the pattern. A tool that exited 0
  with fail>0 would be accepted. This is a latent counter defect in the frozen
  pattern set, not an observed live failure at this tip.

Suggested hardening (not implemented; scope is measurement): add a negative output
fixture per family (a failing record or `fail=N>0` at rc 0) that must be rejected,
and pin `fail=0` in the manifest patterns (instrument-agreement, and any other
pattern that matches a prefix of a count).

## 5. Findings for the L1

1. The counter's sensitivity defects are exposed only by `sens_selftest`; the row-level
   `sensitive=` field and the 12 control families are blind to both mutants (12/12
   in M1 and M2). Calibration of the sensitivity test rests on one hard-coded self-test.
2. At this tip `met` is `False` regardless of the sensitivity test, because of the
   intended `selfdesc_mismatches=8`. A mutant's `met=False` is not a kill by itself;
   compare the sens_selftest field against baseline (4/4).
3. W1-W3 show the counter's sensitivity concept is pattern-dependence only. A
   correct sufficiency control needs negative fixtures (rc=0 with a failing record)
   scored through the same verdict path.
4. The run exit code for the three runs was not captured (the `exit=` trailer did not
   reach the output files); the printed `met=False` line is the observed result, and
   the counter's contract is exit 1 iff not met.

## 6. Tools and bounds

No tools installed. Scratch root /fast/scratch/hyaku/kama-r63/w/MT17C2OldFormula
(clones base/m1r62/m2norc, work dirs, vf_test.py); removed before yield. Every
mutating git call ran only in clones inside scratch (`rev-parse --show-toplevel`
asserted each time). The lane was read-only for this seat; no lane file touched.
Live tools ran only through the counter (llama-server on unregistered loopback ports;
the foreign llama-server processes were untouched).

## 7. Tally (one line, counter output)

M1 (r62 expression): `sens_selftest=0/4 ... met=False` — KILLED.
M2 (no rc leg): `sens_selftest=3/4 ... met=False` — KILLED.
Baseline: `sens_selftest=4/4 ... selfdesc_mismatches=8 ... met=False` (intended).
SURVIVED: none. 3 own verdict functions reported (W1-W3), all sensitive=True.
