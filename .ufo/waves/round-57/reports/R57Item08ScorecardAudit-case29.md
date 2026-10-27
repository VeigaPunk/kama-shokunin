# R57Item08ScorecardAudit — distinct case 29 (independent test of the stale-count audit)

Seat R57Item08ScorecardAudit (revenger, leaf). Case 29 tests the assigned case — "compare current SCORECARD/SHONEN calibration assertions to tree; identify concrete stale counts" — with an implementation that does **not** import or reuse the lane's counters, and with the lane counters run only as objects under test.

Pinned revision: `8a7f19760242bbe523fa2d7d1b22528b587633c1`. Scratch: `/fast/scratch/hyaku/kama-r57/R57Item08ScorecardAudit/` with `TMPDIR` inside it; no `/tmp` use; no lane writes except this report and its receipts.

## Test instruments (independent of `tools/round41-*` / `round42-*`)

| Instrument | What it does | Independence |
|---|---|---|
| `receipts/consolidated.py` | Parses SCORECARD at a revision via `git show`, derives every count claim from tree state (`git ls-tree`, direct ledger CSV parse, receipt JSON), emits PASS/FAIL per assertion | No import of lane counters; ledger tallies recomputed from TSV with its own ordering rule |
| `receipts/case29_derive.py` | Parses the `## Axes` table, re-executes every `run CMD → OUT` fact and recomputes every `HASH/LINES` fact, and adds a scope check the lane counters lack: does the freshness row's stated window (`S001–S477`) still bound the live registry? | Own parser + own executor; no reuse of `RUN_RE`/`evaluate` from the lane |
| `receipts/provenance.py` | Revision-bound stale-count provenance: asserted value from `git show <rev>:SCORECARD.md`, derived value from `git show <rev>:corpus/SOURCES.md` / `git ls-tree <rev>` | Pure `git` reads; no worktree dependence |

## Test 1 — does the audit reproduce the known calibration stale count?

`python3 provenance.py dd9f5dc6 c8c92db4 82b5e9d3 b9d5a091 b89bdab2 7c873d7b 8640e34c 16efcf5e 8a7f1976` (`receipts/provenance.out`, exit 0):

| rev | calibration row asserted | spot-check blobs | result |
|---|---|---|---|
| `b9d5a091` (round-56 tip) | 42 | 42 | consistent |
| `b89bdab2` (round-57 base) | 42 | 43 | **stale** |
| `7c873d7b` (frozen ordering correction) | 42 | 43 | **stale** |
| `8640e34c` | 43 | 43 | repaired |
| `8a7f1976` (pin) | 43 | 43 | consistent |

Cross-check with the lane counter as object under test (`receipts/counter-r42-at-b89bdab2.out`, `...-7c873d7b.out`): `mismatches=1 maxN=56 met=False`, detail `no stdout line == '42' (exit 0)`, **exit 1**. At the pin (`receipts/counter-r42-pin.out`): `mismatches=0 maxN=57 met=True`, **exit 0**. Both independent and lane-side readings agree.

## Test 2 — find stale counts the standing counters miss (the actual case-29 delta)

Freshness row at the pin asserts `218` over the window `S001–S477`.

- Stated-window command, run as written: output **`218`**, exit 0 → equals the row.
- Full-registry command derived independently (`| S` rows with a non-empty 11th cell): output **`257`**, exit 0.
- Registry at pin: **257 rows**, `S001–S516`; excluded by the bound: `S478 … S516` (**39 rows**, listed in `receipts/scope-window-vs-registry.out`).

Counter blindness proof at the pin:

- `round41-scorecard-reconcile.py`: `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True`, **exit 0** (`receipts/counter-r41-pin.out`) — it compares stdout to the printed value, so the stale window passes.
- `round42-selfdesc-reconcile.py`: `... mismatches=0 maxN=57 met=True`, **exit 0** (`receipts/counter-r42-pin.out`) — it only requires the string `recheck` in a run fact.

Independent audit result: `consolidated.py 8a7f1976` → 29 assertions, **28 PASS / 1 FAIL** (`freshness_scope_binds_live_registry`), exit 1; `case29_derive.py` → all 19 RUN/HASH facts OK (12 `RUN`, 7 `HASH`), `FAILURES=1` contributed solely by the scope check, exit 1. So the only live stale count in SCORECARD/SHONEN at the pin is the freshness window, and it is invisible to both registered counters.

Staleness provenance (`receipts/provenance.out`): introduced with the `<=477` bound at `c8c92db4` (round 42) when the registry already held S479 → 2 rows excluded at birth; 8 excluded at round 45 (`82b5e9d3`); 38 at the round-56 tip (`b9d5a091`); 39 at the pin.

## Test 3 — falsify the frozen claim's "expected 46"

- `maxN` = `max(^## Round N headings)`: 56 at `7c873d7b`, 57 at the pin (a `## Round 57` section exists). Confirmed by two independent runs of the counter at those tips (exit 1 and exit 0 respectively, `maxN=56` / `maxN=57`).
- The only "46" in the record is the round-46 measured reading: SCORECARD line 2676, "round-42 self-description counter `mismatches=0 maxN=46 met=True`" at `4340cf2f`.
- Canonical capability rows = 11 (round-49 heading, line 2844), so 46 is neither the row count nor the canonical round.
- Verdict: the claim's expected value is unsupported; the counter's reported value is correct. The stale count to repair is the freshness window, not `maxN`.

## Test 4 — SHONEN counts

SHONEN's only numeric claims are round-16 `10/10` and round-17 `11/11` checks. Independent JSON length reads of `.ufo/waves/round-16/live/receipt.json` (10) and `.ufo/waves/round-17/live/receipt-{1,2,3}.json` (11 each) agree at the pin. No stale count; SHONEN's remaining gaps are judgment items (no non-author verifier / independent execution review open), not counts.

## Case verdict

**Confirmed, with one correction to the claim framing.** The audit independently reproduces the calibration `42→43` staleness and its repair, and independently identifies one live stale count the counters cannot see — the freshness row's `218` / `S001–S477` window against a `S001–S516`, 257-row registry (39 rows excluded). The frozen text "counter reports maxN=56 instead of expected 46" is falsified: `maxN` tracks the highest `## Round` heading and the 46 is a historical round-46 reading.

## Receipts

`R57Item08ScorecardAudit.receipts/`: `consolidated.py`, `consolidated.out`, `case29_derive.py`, `case29-derive.out`, `provenance.py`, `provenance.out`, `scope-window-vs-registry.out`, `counter-r41-pin.out`, `counter-r42-pin.out`, `counter-r42-at-b89bdab2.out`, `counter-r42-at-7c873d7b.out`, `pin.txt`. No tools installed; no pacman transactions.

Report: .ufo/waves/round-57/reports/R57Item08ScorecardAudit-case29.md
