# ConfirmM09 — scoped findings (round 29, W1)

Item: sid `SCORECARD.md:Q:a7e98b1030:0` (SCORECARD.md:834 at base 2aa46e24,
token `baseline=VALID rejected=3/3`), W = 7229fa95eb122310e9e5334ad799ee3006293ebd.

**Verdict: `confirmed-false`** — counter's `q:no-artifact` stands.

- Hand-applied the frozen class-Q rule at W (counter-argv mirror grep, binary
  included): the span occurs in no blob of the tree at 7229fa95 outside
  SCORECARD.md/SHONEN.md/LOG.md/corpus; unrestricted, it occurs only in
  SCORECARD.md:834 itself. Line identity confirmed: sha256(line) =
  a7e98b1030bd… (sid hash match); blame confirms W.
- Intended referent: the round-19 C2 counting run of
  `tests/llamacpp-live/install-tree-grid.py … --tree-sha 6c216313…`.
  The tool (added in W itself) prints at W, blob lines 113-115:
  `baseline=VALID members=3 rejected=3/3 tree_pin=on` — the SCORECARD quote
  drops `members=3 tree_pin=on`, i.e. a hand-abbreviated paraphrase, matching
  the phrasing in the fleet report /home/vgpnk/.ufo/reports/round-19/kama.md:85
  (fleet tree read-only). Its named evidence `evidence/c2-grid.txt` is absent
  from /home/vgpnk/Projects/shokunin/.ufo/reports/round-19/ and from every
  committed lane tree I searched (W and master; pickaxe shows the span only in
  SCORECARD and later round-29 counter machinery).
- Correction-row cause (≤25 words): Writer quoted a truncated paraphrase of
  the grid run's output; the verbatim line (with members=3 tree_pin=on) was
  never committed to the lane.

Gap: the raw grid output bytes remain unverified (measurement truth out of
scope for class Q); `evidence/c2-grid.txt` was searched only under the fleet
reports dir and the lane trees at W/master.

Full evidence: .ufo/waves/round-29/w1/out/ConfirmM09/REPORT.md and verdict.json.
