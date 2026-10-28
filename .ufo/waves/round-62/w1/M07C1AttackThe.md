# M07C1AttackThe — C1 hold-family attack (round 62, w1)

**Axis:** operability. Instrument: tip blob `master:tools/round62-c1-counter.py`
at `65d7cad0fce90e34de37527cde22e97b63b118bf`, sha256 `275610b5…`; `score()`/`grade()`
exercised unmodified (imported from the sha-verified blob) against a genuine
`(receipt, witness)` pair from a replicated `witness_run` lifecycle in my
isolated scratch (nonce `r62-61f4c588ff`, port 41339, verdict `REQUEST_OK`).
Full detail + artifacts: `.ufo/waves/round-62/w1/out/M07C1AttackThe/report.md`.

## Verdicts (ACCEPTED/REJECTED per forgery, score() verbatim)

```
[B0-pristine] REJECTED score()={"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true}
[H0-released-false-checks-intact] REJECTED score()={"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true}   (= the counter's own hold family; byte-identical to B0)
[F4-fs-probe] hold dir present vs absent: score JSON identical: True
[F1-released-true-no-timestamp-no-dir] ACCEPTED score()={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
[F2-released-false-no-timestamp-no-dir] ACCEPTED score()={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
```

## Findings

1. **ASSIGNED ANSWER — yes, ACCEPTED (falsification of the C1 predicate).** The
   grading core accepts `hold.released=true` with the hold window semantics
   broken (no release timestamp — the receipt schema has none —, no hold dir
   reference, dir absent on disk) with `met=true, inconsistent=[]`. The counter
   accepts hold released **without checking the hold doc schema**: `grade()`
   never reads `hold.json` (schema `kama-completion-hold/v1`, release `at`
   timestamp) and never stats the hold dir (F4: score byte-identical with dir
   present vs deleted).
2. **Mirror forgery also ACCEPTED.** `released=false` (never released) is
   accepted with the same shape: the hold family's `1/1` rejection is
   accidental, not semantic.
3. **Vacuity + dead logic.** The tip `grade()` gates the `hold_released`
   recomputation on `if 'hold' in checks`, but the tip tool writes
   `checks['hold_released']`; key-set equality (`set(stored)==required`) is
   then impossible for genuine receipts (`unexpected-checks` on B0 — the
   counter rejects its own genuine receipt), and provably **every accepting
   path skips the hold boolean entirely** (`hold ∈ stored` contradicts set
   equality; `hold ∉ stored` disables the gate). The hold family rejects
   pristine and mutant with byte-identical JSON (H0=B0): zero signal.
4. **End-to-end state of the committed instrument.** Tip blob: crash, no tally,
   exit 1 — `AttributeError: 'NoneType' object has no attribute 'get'` at
   `round62-c1-counter.py:130` (`u = cj.get('usage') or {}`, unguarded when a
   mutated completion capture fails its body-sha check), raised in the controls
   loop at line 440. The worktree counter (uncommitted, sha `a3498308…`) prints
   `… errors=0 met=True`, exit 0 — the spec-time `met=True` reproduces only
   from non-tip bytes (corroborates E01/E06/W03).
5. Mutation-tester verdict: **SURVIVED** (coverage finding). No lane source
   changed; no contract reinterpreted. Bounds kept: no pacman/tools installed,
   no sibling files touched, live runs only on unregistered loopback ports, no
   process killed; scratch removed after receipts were preserved in the out
   dir; tip blob hash unchanged before/after (`275610b5…`).

Tally: tip blob end-to-end = crash, exit 1, no line; worktree bytes =
`tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True`;
grading core (this item): `F1 ACCEPTED score()={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}`.

Report: .ufo/waves/round-62/w1/M07C1AttackThe.md
