# kotodama — round 37 report (2026-10-19)

Regimen 2 (`REGIMEN.md`), loop 1, position 5 — the VERIFY round. One 64-worker
batch on `openai-codex/gpt-6-luna-max`, auditing rounds 33-36. Completed **64/64**;
two seats wrote declared-out-name variants (`O02-controls-verify.md`,
`O04-receipt-draft.md`), recorded in `missing_dependencies`. Baseline `57c8409`.
Claims Ca/O/A. Acceptance: `python3 reports/round-37/run-validation.py` →
`reports/round-37/validation.json`.

## Work performed

- **Calibration (claim Ca — verified):** the rounds 33-36 verify recount landed
  (`calib/recount-ledger.json`, 34 rows): 25 matches, 5 named mismatches, 4
  could-not-reproduce. The mismatches are all legitimate later-tree or
  environmental deltas (r33/A's tracked-path count grew with the tree; r33/cross
  cannot read the fleet report from an isolated archive; r35/C's counts moved
  when r36 landed timekeeping — match at the r35 close commit). The
  could-not-reproduce rows are the runner-isolation hazard (absolute-root
  chdir), now defect **O12**. Two independent samplers (Ca07 32%, Ca08 36%
  disjoint) verified.
- **Operability (claim O — verified):** the consolidated defect queue landed
  (`op/defect-queue.json`, 24 rows): every census defect dispositioned
  fixed-with-evidence (R34-N1 stays closed) or carried-with-owner+reason+
  next-touch; the r37 wave's new findings added — **A01's read-set roster
  defect**, the contract-digest drift vs lore's read, **O10** (the r36 receipt's
  `runner_sha256: null`), **O12** (runner isolation), and the basename-couples
  policy question. Census coverage named honestly (K02 was provisional at its
  cut; set-equality is carried, not claimed).
- **Adjacency (claim A — verified):** the freeze-drift question adjudicated —
  `examples/culture-d4/components/13-register-law.yml` is in the packet's own
  26-component manifest but not the r7 freeze read set: a **roster defect, not
  a documented skip**; the pair still re-renders faithfully (digest verification
  reads the packet manifest), so the defect is real but not packet-corrupting.
  All 334 couples references in the eleven new entries resolve with zero bleed
  (the 15 basename-only references are the documented policy question). The r36
  rejection stands untouched (sentinel X04). Contested scope stays
  routed-not-absorbed.

## Landed changes

- `reports/round-37/calib/recount-ledger.json`, `reports/round-37/op/defect-queue.json` — the two durable ledgers.
- `corpus/README.md` — repaired: two `__E3_PLACEHOLDER__` lines left by the
  round-35 row-apply (sub-with-count + single-replace bug) are removed; sweep
  re-green (this is the round-35 prediction-vs-delivery nuance's root cause —
  recorded, and the r35 apply defect is logged against its integrator).
- `reports/round-37/` — the full verify-round record.
- Filed bytes: **zero** other writes (P1 clean; the 212 baseline corpus entries
  byte-identical).

## Before → after measurements

Counting command: `python3 reports/round-37/run-validation.py` (exit 0;
receipt `reports/round-37/validation.json`).

- **Ca:** no cross-round recount → 34-row ledger (25/5/4 with named causes);
  100% of the K01 inventory covered.
- **O:** defects scattered across four rounds → 24-row dispositioned queue;
  every fixed row carries non-author verification; carried rows are owner-complete.
- **A:** an open freeze-drift question → an adjudicated roster defect with
  evidence and a named fix route (next re-freeze absorbs the member).

## SHONEN

All four boxes untouched; marks stay operator-owned; nothing here is a
promotion, canon, clearance or closure verdict. The verify round found real
defects — including two in the integrator's own round-35/36 landings — and they
are filed with owners rather than smoothed.
