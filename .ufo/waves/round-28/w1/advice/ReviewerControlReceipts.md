# ReviewerControlReceipts — non-author check of pre-freeze control receipts

Read-only re-check of every directory under `.ufo/waves/round-28/controls/` plus `HOLDS.md`.
Method: re-read each `REPORT.md`, `receipt.json` and `fixture/`; re-verified `counter_sha256`,
verdict-vs-receipt agreement, fixture-vs-claim match, receipt arithmetic, and (mechanically,
by joining each counted id's registry claim against its receipt `live` record) that no counted
row was scored for a reason the predicate forbids. No control re-run; all checks are on the
committed files.

## Counter hash

All 11 committed receipts (incl. the four CtlDoNothing variants and the CtlSourceMisuse
skill-ordering receipt) carry `counter_sha256 e6a706bb…c0540c`. `git show d8bf1804:…/count-c1.py
| sha256sum` == `e6a706bb…c0540c`, i.e. the receipts scored the frozen counter. The working-tree
counter now hashes `a38faefe…` because HEAD is amendment commit `75b78bb` (post-freeze,
post-controls); receipts are not polluted by it.

## Per-control table

| control | receipt(s) | verdict line agrees with counted/target/met | fixture shows claimed attack | counted rows clean | verdict |
|---|---|---|---|---|---|
| CtlDoNothing (do-nothing) | 4 receipts, all reg 0 counted 0 | yes — `VERDICT: does-not-meet / counted 0 registered 0` | yes — `{"rows": []}` registry + header-only SKILL diff | n/a | **holds** |
| CtlJunk (junk) | reg 30 counted 0 | yes — `counted 0 registered 30` | yes — 30 invented fields (`kv_spill_ratio`, `sigma_clip`, …), none a schema literal | n/a — all rows `b:line-does-not-declare-field,d:not-shown`, matching report's per-clause table | **holds** |
| CtlLabelKeyed (label-keyed) | reg 41 counted 12 | yes — `counted 12 registered 41` | yes — 41 rows, `origin` key per row: pilot renames, README cells, E26, round-25 K, round-26 base gs | all 12 counted rows: `live` shows true 400+bounds or effective≠sent≠base (checked by re-evaluating claim vs `live`) | **holds** |
| CtlSourceBlind (source-blind) | reg 38 counted 14 | yes — `counted 14 registered 38` (+ pristine/restored receipts in fixture/evidence, both counted 0) | yes — `policy.json`/`guess.py`/`declarations.json` record blind-guess provenance; 38 registry rows | all 14 counted rows consistent with `live` (7 reject bounds, 7 clamp/effective ≠sent≠default) | **holds** |
| CtlDuplicateField (duplicate-field) | reg 26 counted 0 | yes — `counted 0 registered 26` | yes — 26 rows: 4× n_predict, 2× speculative.n_max, 2× temperature, aliases, `dry_base `, `Mirostat`, repeated id F28-25 | n/a — every row refused; 4 live-true hits voided only by `b:duplicate-line-or-field` as report claims | **holds** |
| CtlEcho (echo) | reg 21 counted 1 | yes — `counted 1 registered 21` | yes — fixture.diff: 10 identity, 4 float32, 2 default, 4 request-bounds, 1 alias row | 1 counted (top_p 5.0→1.0): live shows real soft-limit clamp, not an echo — report says so | **holds internally; NOT evidence (HOLD)** |
| CtlSourceMisuse (source-misuse) | reg 12 counted 2 + ordering receipt counted 0 | yes — `counted 2 registered 12` | yes — SOURCES rows S940–S950 match each claimed trick (set_desc line, wrong commit `1234abc`, server-task.cpp, L440 substring, shared S950, junk-wrapped SKILL cells) | 2 counted = the two pilot outcomes (excluded fields); report discloses this | **holds internally; NOT evidence (HOLD)** |
| CtlNoReader (no-reader) | — | — | — | — | **no receipt exists; hold, no files committed** |
| CtlObjectStore (object-store) | — | — | — | — | **no receipt exists; hold, no files committed** |
| CtlAllFalse (all-false) | — | — | — | — | **no receipt exists; hold, no files committed** |

Arithmetic: every receipt has `registered == |rows| == counted + |not_counted|` and `counted ==
|counted_ids|` (CtlDuplicateField's not_counted correctly repeats F28-25).

## HOLDS.md truthfulness

- Five holds named exactly as my task states: CtlNoReader, CtlObjectStore, CtlAllFalse
  (provider refusals, quoted), CtlEcho and CtlSourceMisuse (automatic model switch after a
  safety filter; files kept "as a record, not evidence").
- Held seats' committed files are described truthfully: CtlEcho's report ends with a
  model-switch caveat consistent with the hold reason; CtlSourceMisuse's two receipts exist
  and match `2 of 12` / `0`. The three refusal seats have no files, matching "no receipt;
  never retried".
- No held-seat numbers are used as evidence: HOLDS.md's "Margins" paragraph cites only
  CtlSourceBlind (14) and CtlLabelKeyed (12); the held counts (1, 2) appear only in the
  seat-status column marked "HOLD — not evidence". No other committed file promotes them.
- `controls_required` classes lacking an evidential receipt (per HOLDS.md and confirmed):
  **no-reader, object-store, all-false, echo, source-misuse.**

## Findings (all minor; none change an outcome)

1. HOLDS.md says "CtlLabelKeyed and CtlSourceBlind hit d and e". CtlSourceBlind's receipt hits
   only `d:not-shown` (24/24 misses); no row trips clause (e) — its own report states this.
   Only CtlLabelKeyed hit `e` (2 rows `e:default`). Wording overstates, harmless.
2. HOLDS.md "CtlJunk and CtlDuplicateField hit clauses b and d": CtlDuplicateField's receipt
   also records `a:no-skill-row` on 4 rows (F28-13/16/18/21). Harmless understatement.
3. CtlLabelKeyed REPORT.md says the P90 pattern is "reused for 18 other integer fields";
   the fixture `origin` values show 19 reuses (plus the rename = 20 P90-derived rows). The
   per-row table is correct; the prose count is off by one.
4. CtlSourceMisuse REPORT.md lists F28-16's refusals as `b:not-schema-file +
   c:no-new-sources-row`; the receipt emits the same set in different order
   (`c:no-new-sources-row,b:not-schema-file`). Cosmetic.
5. Already-disclosed: `excluded_fields` is not enforced by the counter — CtlLabelKeyed
   F28-01/02 (renamed pilots) counted; both receipts report it as a finding, and claim data
   excludes these fields by lane rule, not by predicate code.

## Residual risk / gaps

- echo and source-misuse have committed receipts that are self-consistent but were produced
  by seats whose output ends with an automatic model switch; per the hold rule they prove
  nothing about those classes. all-false, no-reader and object-store have no receipt at all —
  five of ten required control classes carry zero evidential coverage this round.
- My live-outcome check re-evaluated each counted row against the receipt's own `live`
  record; I did not re-run the server, so `live` values are trusted as recorded (all rows of
  evidential controls carry `body_sha256`, consistent with a real POST).
- The strongest shortcut remains CtlSourceBlind at 14/18 and CtlLabelKeyed at 12/18; both are
  honest counts (live-true rows), correctly below target — no amendment trigger.
