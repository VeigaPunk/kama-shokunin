# ConfirmM04 — advice (round 29, W1)

sid `SCORECARD.md:Q:4f8083e30a:0` (SCORECARD.md:211 at base 2aa46e24, token
`rows=50 resolved=48 terminal=2 unresolved=0`) — **confirmed-false**; the counter's
`q:no-artifact` is correct. Full evidence: `.ufo/waves/round-29/w1/out/ConfirmM04/verdict.json`.

- W = `40660352d4a9eb00a5d6195f0f064f5c64618143` (blame for line 211; matches receipt).
- Hand-applied class-Q rule: no blob of the W tree outside SCORECARD.md/SHONEN.md/LOG.md/
  corpus/** contains the span (`git grep -F` with the frozen exclusions, exit 1).
- Referent: stdout of `.ufo/round-10/audit/validate-new-pointers.sh` (script at W prints
  exactly this format). The run was committed at W only in `corpus/lessons/round-10.md:148`
  (excluded surface) and in the fleet report `.ufo/reports/round-10/kama.md:120` (outside the
  lane tree). Ledger at W corroborates the numbers: `stale-anchors.tsv` has 50 data rows,
  terminal = A17 + A51.
- Suggested correction-row cause (≤25 words): "Quoted validator stdout was committed at W
  only in corpus/lessons/round-10.md:148, which class Q excludes; no allowed blob contains it."
- Not a counter defect; no routing change implied. Nit only: the L1's existing tip row
  (HEAD:1457) cause cell "no committed file at W holds this text" overstates — a committed
  file (corpus lesson) does hold it; the row stays valid since the last cell is checked.
