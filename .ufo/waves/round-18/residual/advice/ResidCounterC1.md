VERDICT: partial — E1's exact forgery and the declared-exclusion/E5 rules reproduce exactly, but one bucket-less row still launders an `accepted_bad` row to exit-0 CLEAN, and E3 refuses at exit 1, not the expected exit-2 fault.

## Evidence

Copy: `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-res-ResidCounterC1` (lane HEAD `101f3991d3` + uncommitted fixes; copy `measure.py` sha256 `8f4dc2dc…`, Python 3.14.8). Frozen inputs extracted with `git show e75cf680…:tools/kama-llamacpp-live.py` (`0efd1723…`) and `…:tests/llamacpp-live/check-receipt.py` (`ad680179…`); `pins {frozen_tool, frozen_gate} verified True` in every reported run below. Forged children hash the passed `--tool/--gate` (so the counter's sha cross-check passes), live in `/tmp`, hence only the registry-absent warning.

Selftest: `python3 …/c1/measure.py --selftest` → exit 0, `selftest: 43/43 cases passed`, 5.95 s.

| forged child (doc; retained rows) | exit | observed |
|---|---|---|
| `child_honest` (zeros; matching rows) | 0 | clean, faults/reasons/notes `[]` |
| E1 `child_launder_ab` (`accepted_bad=0`; k1 `bucket=accepted_bad`) | **2** | both sides: `accepted_bad=0 but 1 accepted_bad bucket row(s) + 0 accepted gate-flip row(s)` |
| E3 `child_unc_model` (`uncontrolled_checks=['model_unchanged']`, no `input_integrity_checks`) | **1** | no fault; reason `uncontrolled_checks=model_unchanged`; note `… not declared in input_integrity_checks; counted as uncontrolled` |
| E3' `child_unc_model_declared` (same, declared) | 0 | clean; `uncontrolled_excluded=['model_unchanged']` |
| E5 `child_gfa_conflict` (`gate_flip_arms=99`, 1 flip row) | 0 | clean; note `gate_flip_arms=99 exceeds 1 row(s) with a gate_flip object` |
| symmetric `child_launder_gr` (`good_rejected=0`; 1 bucket row) | 2 | `good_rejected=0 but 1 row(s) have a good_rejected outcome bucket` |
| `child_classonly_mc` (`misclassified=0`; bucket-less misclassified row) | 2 | `misclassified=0 but 1 row(s) have a misclassified outcome bucket` (fallback works) |
| NEW `child_bucket_gap_ab` (`accepted_bad=0`; k1 has `bucket=accepted_bad`, k2 has no bucket) | **0** | clean; faults/reasons/notes `[]` |
| NEW `child_classonly_ab` (zeros; accepted rows, no buckets) | **0** | clean |
| NEW `child_gfa_zero_noflip` (`gate_flip_arms=0`, no flip objects) | **0** | clean |
| NEW `child_goodok_false_exit0` (`good_ok=false`, exit 0) | 2 | `controls exited 0 against its own counts: good_ok=false` |
| NEW `child_goodok_false_exit1` (`good_ok=false`, `good_rejected=0`, exit 1) | **0** | clean, no fault, no note |
| NEW `child_overreport_ab_exit1` (`accepted_bad=5`, 1 bucket row, exit 1) | 1 | faults `[]`, notes `[]`; exit 1 only via reason `accepted_bad=5` |

Pristine real arms (`--controls tests/llamacpp-live/controls.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py`, frozens from git, 39.9 s): exit 0, faults/warnings `[]`, `leaked_processes []` both sides, pins verified; counts `accepted_bad 5→0`, `good_rejected 1→0`, `misclassified 1→0`, `uncontrolled_checks 0→0`, `gate_flip_arms 16→17`, `good_ok true→true` — exact match to the four promised arms.

## Findings

1. MEDIUM — the row-vs-count guard is document-wide, so one un-bucketed row re-enables the E1 forgery. `measure.py:617` gates both checks on `if rows and all(row['bucket_source'] == 'reported' …)`. Executed `child_bucket_gap_ab` still carries `bucket='accepted_bad'` on k1 and reports `accepted_bad=0`, yet exits 0 CLEAN with no note, because unrelated k2 lacks a bucket. `child_classonly_ab` is clean too. Fix direction: drop the `all()` gate and compare `accepted_bad < n_ab + n_flip` and `good_rejected < n_gr` over reported-bucket rows only (the legacy selftest `no_bucket`, `measure.py:1506-1519`, still passes since `n_ab=0`), and surface un-bucketed accepted rows as unverifiable instead of a global exemption.
2. LOW — `good_ok=false` with `controls exit 1` is certified CLEAN: `clean_reasons` (`measure.py:667-681`) covers exactly four counts and the exit-0-against-counts check (`measure.py:650`) does not run at exit 1; no `good_ok`↔`good_rejected` cross-check exists in the reported shape. The selftest asserts this scope (`measure.py:1526-1528`), so it is deliberate, but E1-style internal contradiction survives here.
3. LOW — `gate_flip_arms` is only checked directionally (`measure.py:545-550`): a child reporting `0` with no `gate_flip` objects is clean (executed). This is the documented consistent-misreport class, but it means the certified `16→17` arm is not independently evidenced against an empty row set.
4. LOW (doc) — docstring `measure.py:48-49` says an over-reported `accepted_bad` partial projection is "only noted"; executed `child_overreport_ab_exit1` produced no note on either side. Either emit the note or drop the claim.
5. INFO — E3's expected exit 2 is not what the implementation does: it refuses with exit 1 plus a named reason, matching the selftest (`measure.py:1575-1580`) and the lesson's wording ("exclusion only when declared"). The substantive rule holds; an acceptance text promising exit 2 would be false.
6. Positive controls held: honest child clean; E1/E3'/E5, `child_launder_gr`, `child_classonly_mc`, `child_goodok_false_exit0` all fail exactly as named; real arms exact.

## Limits

Synthetic children only (no servers); the real-arms run is the only loopback activity (ephemeral, reaped). `--self-mutants` mode not re-exercised (CounterC1 did not either). No interpreter pin (CounterC1 F4) retested. No resume/routing path exists in this artifact. No installs, no services; copy deleted after the report; lane state untouched except this report.
