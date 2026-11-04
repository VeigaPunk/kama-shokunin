# MT01Mutants75 — scoped findings (kama r75 w1)

Full matrix, per-mutant patches, raw harness output: `.ufo/waves/round-75/w1/MT01Mutants75/report.md` (+ `raw/`).

```
MUTANTS75 tools/round75-interpretation-pins.py applied=9 killed=5 escaped=4
MUTANTS75 tools/round75-survivor-probe.py     applied=8 killed=5 escaped=3
MUTANTS75 tools/round75-append-accepted.py    applied=9 killed=7 escaped=2
```

Escaped mutants (verdicts against the committed bytes `fac5ffbb…` / `25551516…` / `f2899667…`; every mutant ran `--selftest` AND the real-lane command; killed = an arm or the real run went red):

| Module | Escaped mutant | Class | Missing arm (L1 decision needed) |
|---|---|---|---|
| interpretation-pins | A5b-fake-P2-leg | scope cut: P2 pin hardcoded observed/mutant/mutant_ok | `cheat-p2-escaped` — composed variant that fakes the P2 leg must go red (no new fixture) |
| interpretation-pins | A6-trust-P2-observed | input-trust: pristine P2 exit hardcoded to 0 | same arm as A5b (same anchor family) |
| interpretation-pins | A7-oracle-declared-and-kill | selftest-oracle tamper (`→ True`) | `oracle-liveness` — injected fault must prove each arm can fail (doctored plan copy under `--work`) |
| interpretation-pins | A8-oracle-predicate | selftest-oracle tamper (`→ True`) | same `oracle-liveness` arm |
| survivor-probe | B5-skip-pristine-verdict | scope cut: `grade(0, …)` discards the real pristine rc | `probe-pristine-red` — CLI run against a fixture repo whose committed target module has one broken arm; needs that red-pristine clone fixture |
| survivor-probe | B8-oracle-complete-kills | selftest-oracle tamper (`complete-kills → True`) | `complete-kills-liveness` — synthetic one-green-row case must FAIL the check |
| survivor-probe | B9-summary-line-hardcode | output oracle: printed `SURVIVORS2` line hardcoded | composed-counter cheat arm (pins' `cheat-escaped` analog) binding the printed line to `doc` |
| append-accepted | C3-bad-rows-drop | comparison flip (`bad_rows += 1 → += 0`) | `stray-bad-row` — bad row ADDED to a complete register; today `restored-event` passes via `unaccepted`, `bad_rows` is never the sole red signal |
| append-accepted | C9-oracle-and-to-or | selftest-oracle tamper (`and → or` in case harness) | `oracle-liveness` — one deliberately mis-expected case must FAIL |

Pattern: 7 escapes, all in composed-counter / leg-wiring / selftest-oracle space; six of the seven missing arms need no new repo fixture. Killed detectors worth keeping in mind for review: pins' `cheat-escaped` arm killed A2/A3/A5a; survivors' `wrong-arm` killed B2 and the real lane killed B6; accepted's real lane killed C6 (`events=1 accepted=1 bad_rows=388`, 388 hash-mismatch findings, exit 1 — mutant-attributed, not lane-state).

Lane untouched (hashes four-way verified pristine == worktree == HEAD blob == clone before/after; lane git used read-only only). Scratch `/fast/scratch/hyaku/kama-r75/MT01Mutants75/` removed; receipts retained under `report.md`'s `raw/`.
