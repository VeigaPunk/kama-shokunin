# CON01Overlap — scoped findings, kama round 74 wave 1

Seat: CON01Overlap (connector, cross-lane overlap scan) · 2026-11-04 · milestone kama r74 w1.
Write scope exercised: this file and `.ufo/waves/round-74/w1/CON01Overlap/` only; everything
else READ-ONLY. No git/jj mutations; no fixture writes; no installs/upgrades; no scratch dir
created (pure read scan), nothing under `/fast/scratch/hyaku/kama-r74/` to delete.

## Verdict

No sibling lane implements, amends, or names any of the round's three frozen instruments
(`round74-selfdesc-canon.py`, `round74-receipt-claim-binding.py`,
`round74-province-host-drift.py` — 0 hits for all three module names outside kama-shokunin).
No **identical** overlap anywhere; no contested scope. Prior art worth citing exists and is
mapped below; the action for kama's report is "cite sibling prior art", never "contested-scope".

## Overlap table (lane · class · surface · class · action)

| lane | class | surface | overlap | action |
|---|---|---|---|---|
| souji | C1 | `tools/souji-citation-reconcile.py:2` (r37–39 self-assessment citation reconciler; committed-bytes row↔citation↔receipt binding; r38 40-hex ancestor arm) | strong | cite in C1 knowledge entry (different leg — citation→receipt, not heading→repertoire) |
| mori | C1 | `corpus/lessons/round-77-verifier-spotcheck.md:98-99,193-195` (closures grade canonical SCORECARD capability-table headings 26→26; r75 discharged register-vs-demonstrated mismatch) | weak | cite as same-surface/different-check precedent |
| tameshi | C1 | `tools/wave-reconcile.py:2` (r73–75; record-span claim binding) | weak | cite as paragraph-scoping precedent, different surface |
| tameshi | C2 | `tools/receipt-revision-gate.py:2-4` (r55–56 frozen; receipt `rev=` bound to certified rev, drift+ancestor arms) | strong | cite in C2 knowledge entry + one prior-art line in the C2 receipt |
| tameshi | C2 | `tools/receipt-commit-bind.py:1-2` (r65–66; message-span receipt binding across line breaks, delimited-token v2) | strong | cite as the line-split-escape sibling of wrapped/offset claims |
| kaidoku | C2 | `tools/round-62/base-binding-sweep.py:2-4` (r62; threads the receipt's OWN `base:` 40-hex binding from committed bytes) | strong | cite as explicit-revision-binding prior art (self-binding; kama's leg is cross-binding) |
| tsukuroi | C2 | `tools/check-revision-binding.py:1-2` (r17–18; tool `--revision` gates bound to landed/pushed revisions) | weak | cite frame-level only |
| souji | C2 | `corpus/lessons/round-57.md:170-172` — "LANE-FIRST on C2's digest binding, SHARED on the general idea" | weak | cite as the house novelty-phrasing precedent |
| kengaku | C2 | `corpus/lessons/round-72.md:126` — presence-check-read-as-attribution-check (swapped revision tokens pass) | weak | cite as the named wrapped/offset failure class in a sibling lesson |
| kaidoku | C3 | `tools/round-29/freeze-gate.py:132` (per-commit any-change walk over `rev-list '{freeze}..{measured}' -- path`) | strong | cite in `corpus/knowledge/host-block-base-revision.md` as the closest preservation-leg mechanism prior art (different surface, no `recorded at` token) |
| kotoba | C3 | `verifiers/check_host_skill_surfaces.py` (r82+; live host skill-drift census) | weak | cite as different-frame adjacency |
| tameshi | C3 | `tools/additivity-receipt.py:1-4` (r63; committed-bytes preservation receipts, raw vs normalized) | weak | cite as the byte-preservation receipt frame |
| all other lane×class pairs | — | (see `overlap.md` §Scan coverage) | none | none |

## Reverse direction (siblings observing kama, rounds 70–74)

- kumitate `K74ConnectorOverlap.md:11,16` — r74 sweep of all 20 siblings: kama **none**,
  "zero surface overlap"; observed this wave's KamaR74a2 live.
- tameshi `T74W1CN1.md:47-53,150,173-198` + `round-74-verifier-spotcheck.md:149` — cites
  kama `tools/append-only-audit.py:587`: frame ruled general (kama+kaidoku), attribution
  lane-local; closure ruled "a different frame … not claimed general (one lane only)".
- tsukuroi `C1Connector.md:152-153` — overlap-risk analysis vs kama: none.
- kotoba `ScoutSibKamaKasegiR74.md:3,23` — kama `adjacent`, unchanged from r49; no instrument overlap.
- kengaku `.ufo/reports/round-72/kengaku.md:237,291`, `round-73/kengaku.md:15,19` — kama's
  r50 canary + `/proc/<pid>/environ` arm named as a routed sibling site, retained without copying.
- kake `round-71-verifier-spotcheck.md:59` — admits S132 (kama's
  `corpus/knowledge/self-assessment-at-writing.md`) as its C1 sourced basis.

## MANIFEST.json

`MANIFEST.json:41567-41579` (`rounds[1135]`): kama round 73 closure, verdict
**`rejected-honest-stop`**; calibration/operability/freshness improved; depth/coverage/
adjacency unchanged; routed defects (1,2,5) → this round's C1/C2/C3, (3) → SCORECARD
calibration row, (4) → queued disclosed, (6) → lesson mistake 2.

## Contradictions (stated, not smoothed)

1. tameshi's r74 connector (`T74W1CN1.md:150`) calls the range-additivity frame **general**
   on kama+kaidoku evidence; tameshi's r74 closure (`round-74-verifier-spotcheck.md:149`)
   says the kama pattern is "**not** claimed general (one lane only)". Reconcilable
   (frame-general vs novelty-claim) — cite both texts together.
2. `T74W1CN1.md:53` mislabels the 1529-line kama file as `round50-append-audit-v5-check.py`;
   the file with `rev-list … --parents` at `:587` is `tools/append-only-audit.py` (verified
   `wc -l`: 1529 vs 545).

## One bounded proposal

Mirror T74W1CN1's citation convention in kama's round-74 record: one labelled
"read-only primary surface, not a governed leg" prior-art line per overlapping lane in the
C1/C2/C3 knowledge entries (six citations above), plus a `## Gate` citation in
`corpus/lessons/round-74.md`; novelty clauses narrowed to kama's actual new legs
(heading-markup resolution semantics; paragraph-scoped record→receipt binding with
case-insensitive hex; `recorded at <rev>` host-block byte-identity). Improves **adjacency**
and **calibration** receipt truthfulness; harms no axis; touches no instrument byte
(`PREDICATE` constants must stay byte-equal to the frozen plan sentences). Verification:
grep the six path:line citations into the entries; cmp `PREDICATE` constants against
`plans/round-74-claims.md`; re-run `.ufo/waves/round-74/controls/score-survivors.py`
unchanged.

## Evidence & commands

Full command list with outputs: `.ufo/waves/round-74/w1/CON01Overlap/report.md`.
Master table + scan coverage: `.ufo/waves/round-74/w1/CON01Overlap/overlap.md`.
All findings grounded in path:line citations verified by `grep -n` / direct reads this seat.
