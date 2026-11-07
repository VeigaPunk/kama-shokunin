# Round-93 lesson `## Mistakes` — remaining corrections (SB01LessonDraft)

Status at tip `54b8578f` (2026-11-06 23:56 -03): the L1 has integrated two wave-1 mistakes into
`corpus/lessons/round-93.md` — **M4** (P05–P07 labels) and **M5** (the ctime key) — and the SKILL dated correction
now carries both K2 hits plus the `--port 0` and source-range limits. What the lesson still needs is: the three
corrections to M1–M3, a row for the **R16 argv-order K2 hit** (it lives only in the SKILL correction), and the M4
`Captured-by` fix. This file keeps only those. Every number is a token a named receipt prints; inferences from
printed tokens are labelled `[INFERENCE]`.

## Corrections to landed rows

**M1 — a held-out cell sized below the threshold of the forgery it was meant to kill.** The class, evidence and fix
stand. **Correct the parenthetical "(≈1.4 s at load 21)"**: no receipt prints it. The only `1.4` in the round's
record is `w1/out/EX01HeldOutRepeat/heldout.out` `A-distinct-x2` at `load1=73.48` — **two distinct files**, base
`1.40s`/M1 `1.46s` — a different shape and load. The measured four-parse run is `measured/m1-v0-alias-F2.out`
`R05` `2.64s/2.96s/2.64s` at `load1=73.48`; at its own rate (~0.70 s/parse `[INFERENCE]`) the frozen 33-string cell
needs ~23 s of parses, so it is load-robust, while the 4-string cell sat ~1.0–1.4 s inside the 4 s deadline at load
73 and the margin shrinks with load. Also state that the v0 counter bytes are not committed (the receipt's `cmd`
names `<scratch>/v0-counter.py`; the "4 strings" is supported by the plan's "four-alias R05" and the receipt
header), and that "plan §9" does not resolve (`plans/round-93-claims.md` has no §9). Shown able to fail: the v0+F2
receipt (10/10, exit 0) against the frozen F2 (`controls/c1-forgeries.out`, `R05 ok=0`, exit 1).

**M2 — a range shorthand hid ids from a decision's named-set rule.** The class and fix stand. **Correct
`Captured-by`**: `measured/m2-range-decision.out` is a **post-freeze reconstruction** (`rev=4c4adc63`,
`--skill-file <scratch>/SKILL-range.md`), not a retained pre-freeze run; the committed P0 is green
(`controls/c2-forgeries.out` P0 `decisions_bound=2`). Say: "captured by the counter's `decision-names` arm;
exercised by a reconstruction at `4c4adc63`; no pre-freeze receipt retained". P0 did not exhibit the failure.

**M3 — a lesson number with no committed round receipt.** `grep -rn 'APPEND_DEBT' .ufo/waves/round-93/` (excluding
this seat's out dir) returns nothing at tip `54b8578f`; there is no round-93 gate receipt, and
`grep -rn 'events=100' .ufo/waves/round-93/` matches only the lesson line. The r92 side is backed
(`.ufo/waves/round-92/measured/gate-final.out`: `events=97 … unaccepted=18`). Fix: run
`python3 tools/pre-report-gate.py --repo . --round 93` and commit its output (e.g. `measured/gate-final.out`), then
quote that line; until then write "not yet measured this round" and keep R1 in Dispositions. Shown able to fail: a
check that every number in the lesson appears in a committed round-93 receipt fails on the current text and passes
after the gate receipt lands.

**M4 (landed) — `Captured-by` says `none`, but the K2 kill rule fired.** The same commit (`54b8578f`) is titled
"K2 fired (wave-1 RV02: P05–P07 labels, R16 router-child argv order)", and round-91 M1's convention is
`Captured-by: K2 (non-author reviewer read) — fired as designed`. Read: **Captured-by: K2 (RV02, non-author) —
fired; no QUALITY criterion named label-vs-definition consistency before KQ151.** This does not change the fix or
KQ151; it corrects the attribution.

## Missing row (the lesson has no row for the second K2 hit)

**M6 — R16's router-child clause is defeated by a later-sorting preset option (K2).** Class: a decision states a
port for a start that another population row changes. Evidence: `common/preset.cpp:44-50` renders a preset by
iterating a `std::map` keyed by `strcmp(args[0], …)` (`common/arg.h:91-96`), so `--port` sorts before
`--vision-gemma-4b-default`; the latter's lambda sets `params.port = 8014;` (`common/arg.cpp:4753`, P23/P24) after
`--port`; `server-models.cpp:314-322` leaves the preset option in place (`unset_reserved_args(preset,false)` removes
only SSL/API/models/connect keys) and sets `args = preset.to_args(bin_path)`. A router child registered with a
vision-gemma preset listens on 8014, not "the free port the router chose". Non-author read:
`w1/RV02SetterRows.md` DEFECT-2; the SKILL dated correction (`54b8578f`) records it, the lesson does not. Captured-by:
K2's second clause (reported per row). Fix: keep the SKILL correction; add the lesson row so "C2 not verified" does
not rest on M4 alone; the counter cannot read decision prose, so this stays a reviewer read. Shown able to fail: the
three source facts above; a lane-owned router child started with the preset would answer on 8014 (not run here — the
claim is the source read, and RV02 is the non-author read).

## Notes, not mistakes

- **The R05 retune was not goal-seeking on the counted population.** R05 is red in both base controls (v0
  `4.20/4.22/4.21s`, frozen `4.39/4.40/4.40s`); the v0→frozen `mismatches` delta 4→5 is R02's load flip (green at
  `load1=20.88`, red at `48.05`), not the alias widening. The retune shows only against F2 (M1 above).
- **Access-date convention.** Round-92 uses the local date (2026-11-06) with the UTC instant printed; round-93 uses
  the UTC date (2026-11-07). Both pass `sources-census.sh validate`, whose default `TODAY=$(date -u +%F)` is UTC;
  keep printing both instants (`2026-11-07T02:33:36Z = 2026-11-06 23:33 -03`).
- **Counter limits widened by wave 1, routed.** CR02: 14/31 forgeries bind (20/38 with `forgeries2`); MT02: 16/26
  single-point mutants survive, 13 false greens. They extend the claims' disclosed limit L1 and belong in the
  round-94 carry; they do not change the K2 outcome.
- **The landed M5 (ctime) leaves one disclosure gap.** The claims' C1 rule text names a four-field identity
  (device, inode, size, mtime); the tip's key is five fields (`+st_ctime_ns`, `b3765799`), so the frozen prose is
  incomplete. The SKILL correction does not say so; add the delta to the lesson's M5 or a dated note.
