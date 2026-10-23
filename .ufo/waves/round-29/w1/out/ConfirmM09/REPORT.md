# ConfirmM09 — sid `SCORECARD.md:Q:a7e98b1030:0`

## Verdict: `confirmed-false`

The counter's `q:no-artifact` for this statement is correct. I established this
without running the counter, by hand-applying the frozen class-Q rule
(count-c1.py docstring: a quoted span of 6-200 chars containing a digit and
`=` … HOLDS iff the span occurs verbatim in at least one blob of the tree at W
other than SCORECARD.md, SHONEN.md, LOG.md and corpus/**).

## Statement and W

- Base 2aa46e24, SCORECARD.md line 834 (sha256 of the line =
  `a7e98b1030bd5152…` → sid hash `a7e98b1030`, index 0 — identity confirmed):
  `` `baseline=VALID rejected=3/3` exit 0. The pin binds observed bytes, not an ``
  (continuation line of the round-19 C2 paragraph; the sentence starts on line
  833 with the sibling quote `` `baseline=VALID members=3 rejected=0/3` exit 1 ``).
- `git blame -L 834,834 --line-porcelain 2aa46e24 -- SCORECARD.md` names
  W = `7229fa95eb122310e9e5334ad799ee3006293ebd`
  ("round-19: citation provenance, install-tree pin, r18 defect corrections").
  Confirmed.

## Hand application of the Q rule at W

- Counter-argv mirror (fixed-string, case-sensitive, excludes
  SCORECARD.md/SHONEN.md/LOG.md/corpus, binary included — no `-I`):
  `git --no-replace-objects grep -F -q -e 'baseline=VALID rejected=3/3' 7229fa95… -- . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'`
  → exit 1: no blob in the tree at W contains the span.
- Unrestricted grep at W: the span occurs only in SCORECARD.md:834 itself
  (the writing file, which the rule excludes). LOG.md and SHONEN.md at W do
  not contain `rejected=3/3` either.
- Therefore the class-Q check fails at W → `q:no-artifact`. Not a
  counter false positive: the implementation I read (count-c1.py check(),
  class Q) mirrors the docstring rule exactly, and my independent run agrees.

## What the statement most likely referred to

- The round-19 C2 counting run: `python3 tests/llamacpp-live/install-tree-grid.py
  --gate tests/llamacpp-live/check-receipt.py --receipt
  .ufo/waves/round-18/live-recovery/receipt-1.json … --tree-sha 6c216313…`
  (this is the counting command named on lines 829-833, and the fleet report
  /home/vgpnk/Projects/shokunin/.ufo/reports/round-19/kama.md:85 names the
  same command with `--tree-sha 6c216313…`).
- Not the intended lane path (class P) — no path is quoted; this is a Q quote.
- Not a reformatted artifact at W: install-tree-grid.py was itself added by W
  (its only commit up to W is 7229fa9), and its print statement at W (blob
  lines 113-115) is
  `baseline={baseline} members={len(rows)} rejected={rejected}/{len(rows)} tree_pin={'on' if args.tree_sha else 'off'}`
  — so the genuine output of the with-pin run was
  `baseline=VALID members=3 rejected=3/3 tree_pin=on`. The SCORECARD span
  `baseline=VALID rejected=3/3` (and its sibling `baseline=VALID members=3
  rejected=0/3`) are truncations/paraphrases; no committed version of the tool
  could have printed either span verbatim.
- Artifact committed later: none. Pickaxe over master finds the span only at
  7229fa9 (SCORECARD itself), then round-29 freeze/control/data commits — all
  counter machinery echoing the token (c1-base.json, controls/* receipts,
  correction rows). No measurement artifact ever carried it.
- Fleet report: /home/vgpnk/Projects/shokunin/.ufo/reports/round-19/kama.md:85
  quotes the same abbreviated phrasing (`rejected=0/3` exit 1 → `rejected=3/3`
  exit 0, "tree pin on") and names evidence file `evidence/c2-grid.txt`, which
  is NOT present under /home/vgpnk/Projects/shokunin/.ufo/reports/round-19/
  (12 .md files only; no `tree_pin=on` anywhere in that directory). The raw
  grid output was apparently captured in a session-local evidence file that
  never reached any committed tree I searched. Its actual content is
  **unverified**.
- So: the quote most likely came from the writer's session transcript of the
  real run, abbreviated by hand (dropping `members=3 tree_pin=on`) to match
  the phrasing used in the fleet report, and never committed as evidence.

## Cause (for the correction row)

Writer quoted a truncated paraphrase of the grid run's output; the verbatim
line (with members=3 tree_pin=on) was never committed to the lane.

## Residual risk / verification gaps

- I did not and could not rerun the grid (the measurement's truth is out of
  scope; the class-Q predicate only tests committed evidence at W). The
  measurement itself may well be genuine — the fleet report and the tool's
  exit-code contract are consistent with `baseline=VALID members=3 rejected=3/3
  tree_pin=on` — but the raw output bytes remain unverified.
- `evidence/c2-grid.txt` was searched only under
  /home/vgpnk/Projects/shokunin/.ufo/reports/round-19/ (read-only) and the lane
  trees at W and master; another location is not excluded.
- grep equivalence: my hand check used the same fixed-string semantics as the
  counter's implementation; no encoding/binary corner was exercised beyond
  including binary blobs (no `-I` in the mirror run).
