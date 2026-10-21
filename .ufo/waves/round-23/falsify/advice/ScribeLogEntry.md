# ScribeLogEntry — round-23 LOG.md entry draft (scribe report)

Verdict: **draft complete; counts re-observed and match the L1 claim except one traceback count (frozen arm: 9 observed, 8 recorded in the lesson).** Draft only. LOG.md, lesson, SCORECARD and SOURCES were not edited.

## Draft
- `.ufo/waves/round-23/falsify/out/ScribeLogEntry/LOG-round-23-entry.md` — `## round 23 — repository-local git state in the report landing audit (2026-10-21)`, in the round-21/22 entry style: declared claim, motivation (probe), commits, grid counts per arm, mutants, no-harm, sources, limits.

## Observations (scribe re-run, read-only, at clean clone `/tmp/kama-r23w2/ScribeLogEntry` of `245a37f69628c2c6bb29bbf17897d8fb5946c857`, HEAD verified; git 2.56.0, Python 3.14.8)
| command | exit (declared) | observed |
|---|---|---|
| `tests/report-audit/repo-state-grid.py --arm current --json` | 0 (0) | faults 26/26, controls 8/8, tracebacks 0, executed 0, timeouts 0 |
| `tests/report-audit/repo-state-grid.py --arm frozen --json` | 1 (1) | faults 0/26, controls 8/8, **tracebacks 9** (L1 lesson: 8), executed 2 (F06, F09), timeouts 1 (F14) |
| `tools/report-landing-audit.py --selftest` | 0 | cases 50, failed 0 |
| `--rounds 10-22 --json` current vs frozen blob `4fe9339f` | 0 / 0 | status clean, corrected 9, errata_rows 9, unmatched 0, invalid 0; outputs byte-identical |
| `--rounds 10-22 --no-errata --json` current vs frozen | 1 / 1 | status failed, 9 defects (landed-omitted 8, unresolved-full-hash 1); byte-identical |
| `tests/report-audit/isolation-mutants.py --json` | 0 | pristine passed; 24 mutants, 22 killed; survivors M02-lazy-fetch, M20-log-sha-shape |

Evidence files: `.ufo/waves/round-23/falsify/out/ScribeLogEntry/` (`commands.tsv`, `grid-current.json`, `grid-frozen.json`, `mutants.json`, `selftest.out`, four `ledger-10-22-*.json`, `frozen-4fe9339f-report-landing-audit.py`).

## Discrepancies for the L1 / main agent
1. **Frozen-arm tracebacks: 9 observed vs 8 in `corpus/lessons/round-23.md` (M1) and in the brief.** Per-row trace: F01, F02, F16, F18, F19, F20, F22, F24, F26 each `traceback=True` with `UnicodeDecodeError` (F24/F26: `int` max-digits ValueError). The 8 in the lesson may be a count from an earlier run or may exclude one row; not determined. The draft states 9 and notes the L1 figure. Either the lesson or the draft must be reconciled before LOG.md is committed.
2. **Python version drift:** S095 pins Python 3.14.9; host runs 3.14.8. Local observations are on 3.14.8; not a contradiction of the quoted page, but the LOG should not claim the 3.14.9 run.
3. **Ledger scope:** `--rounds 10-22` (the brief's form) was run against the live fleet root `/home/vgpnk/Projects/shokunin` read-only; results depend on fleet state at 2026-10-21. Round-21 entry used `--rounds 10-20`. Draft states the fleet-state dependency.

## Checks not run (not passes)
- Sources S089–S095 were not reopened online; quotes are carried from the lesson Gate table and the SOURCES rows only.
- `sources-append-only.py`, `sources-validate`/`census`, `check-receipt.py`, `citation-provenance.py`, the live llama.cpp receipt and the official `run.py` recipe were not run (not needed for the LOG draft; no claim depends on them).
- Probe `probe.sh` was not re-run; its numbers are quoted from the recorded `.ufo/waves/round-23/build/out/probe-4fe9339f.stdout`.
- Lesson's Mistake M2 (probe fixture premise) and M3 (operator-shell env leak) are quoted from the lesson; not re-verified.

## Installs / updates
None. No tool installed or upgraded. No pacman transaction.

## Files written
- `.ufo/waves/round-23/falsify/out/ScribeLogEntry/LOG-round-23-entry.md` (draft)
- `.ufo/waves/round-23/falsify/out/ScribeLogEntry/commands.tsv`
- `.ufo/waves/round-23/falsify/out/ScribeLogEntry/grid-current.json`, `grid-frozen.json`, `mutants.json`, `selftest.out`, `ledger-10-22-current.json`, `ledger-10-22-frozen.json`, `ledger-10-22-no-errata-current.json`, `ledger-10-22-no-errata-frozen.json`, `frozen-4fe9339f-report-landing-audit.py`
- `.ufo/waves/round-23/falsify/advice/ScribeLogEntry.md` (this report)
- Scratch only (outside the lane): `/tmp/kama-r23w2/ScribeLogEntry` (clone), `/tmp/kama-r23w2/*.json|*.out|*.err`.

No commits, pushes, jj commands or lane tracked-file edits. No subagents spawned.
