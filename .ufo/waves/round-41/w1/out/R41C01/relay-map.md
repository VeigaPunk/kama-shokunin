# R41C01 companion — correction-relay map, rounds 34–41

Compact per-round map supporting the main report. All citations are to committed
blobs in the lane clone (`/fast/scratch/kama-r41/clone`).

| Round | C1 target (predicate) | Corrects previous closure's routed statements? | Closure's routed defects → who fixed | Counter guard added |
|---|---|---|---|---|
| 34 | capability self-assessment list | n/a (origin) | r34 verifier: 4 unsupported statements | `tools/capability-repertoire-audit.py` |
| 35 | r34 statements (R34-MAP/R33COUNT/LIVE/MANIFEST) | yes | r35 verifier: S211 reason, word count, mirror label, sweep → r36 | `round35-statement-audit.py` (row-name+byte re-derivation, report blob pin) |
| 36 | r35 statements (R35-S211/WORDS/MIRROR/KEEP) | yes | r36 verifier D1/D2A/D2B/D3 → r37 | `round36-statement-audit.py` (forbids token 429; re-derives quote word count) |
| 37 | r36 statements (R36-D1/D2A/D2B/D3) | yes | r37 verifier items 1–5 → r38 (C1: D2C; C3: counters/report/receipt) | `round37-statement-audit.py` (forbids wrong-id restatement) |
| 38 | R36-D2C correction row | yes (partial: one of five routed items) | r38 verifier: S472 digest, package digest abbrev, wave evidence, SHONEN → r40 | `round38-statement-audit.py` (byte re-derivation of correction) |
| 39 | assimilation (1 admit + 1 reject with flip) | **no** (relay pause) | r39 verifier D1/D2/D3 (erratum, counter fidelity, freeze/base) | grep decision-count command (`counting-command mismatch, D2) |
| 40 | digest recomputation (S474 supersedes S472) | partial (r38 defect 1) | r40 verifier D1–D5 (counter-schema, reject specificity, D3 sweep, N2/N3, D5) | `round40-calibration-audit.py` — **schema defect (row[7] vs row[6]) → honest stop** |
| 41 | SCORECARD head `## Axes` table = tree | **no** (un-routed; stale since round 10) | r41 fixes D1/D3/D4 in-round as non-claim work (KQ48, pointer, N2/N3) | `round41-scorecard-reconcile.py` — generic table re-derivation; **first guard over the standing self-assessment artifact** |

Recurring defect class: **evidence-citation drift** (digests, S-ids, counts, paths, statuses, hashes, command strings that do not re-derive from committed bytes). Every closure found a fresh instance despite a new narrow guard each round — confirming operator lesson 2 (`considerthese/2026-10-25.md:19`).

Instrument that would end it: generalized pre-landing citation re-derivation linter over lessons/reports/SCORECARD/SOURCES prose (operator proposal 1, `considerthese/2026-10-25.md:27`) — prototype: `tools/round41-scorecard-reconcile.py` (hash/line/run/path re-derivation + hollow/score checks).
