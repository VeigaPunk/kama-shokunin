# K2Origin — attack on the v4 origin definition (round 49, kama C2)

Verdict: **the v4 origin rule is byte-text-global and traversal-ordered, so it (a) re-grades the lane's own head mirror-table rows (7 lines in event `0718b6abbda6` — a live false-positive), (b) makes the verdict depend on rev-list sibling order (identical final trees give exit 0 vs exit 1), (c) hides a dated-section loss when a fenced fake `## ` title precedes it, and (d) grades CRLF variants of head lines; the dated-deletion direction (laundering) is correctly closed. The frozen counter shares the same logic, so `met=True` still holds — the findings are definition-level, not counter failures.**

## Method

- Read `tools/append-only-audit.py` v4 docstring (lines 4–22), `origins()` (423–441), `sections()` (265–272), audit loop (443–493), `file_regions()` (384–394), the frozen counter `tools/round49-append-audit-v4-check.py` (fixtures 173–229, lane leg 283–360, origins 317–335).
- Baselines at measured tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (shared clone at $S/lane):
  - `python3 tools/append-only-audit.py --repo $S/lane --to 74558c71… --json` → exit 0; summary commits=319 events=5 restored=5 ungraded=0 ungraded_lines=82 regressed=0 bad_declarations=0.
  - `python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71… --scratch $S --out c2-baseline.txt` → `fixture=1 lane=1 scenarios=8/8 met=True` (exit 0), lane detail `event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65`.
- Fixture repos built under `/fast/scratch/hyaku/kama-r49/K2Origin/` (`mktemp -d -p`, `git init -q`, toplevel assert), contract outside the repo (exactly like the counter); each run: `append-only-audit.py --repo <fx> --to HEAD --contract <cp> --json`.
- Lane-instance search on SCORECARD.md history: merges touching the file, fence scan over all 92 blobs (`rev-list --all --objects` + `cat-file`), CRLF scan over all blobs, shared-text analysis between exempt heads and dated sections, plus per-line anatomy of both lane events (see `event_anatomy.out`).

## Findings

### F1. Dated-section deletions are correctly graded (laundering closed) — no defect
Born in the head, carried into a dated section, then deleted from the **dated** section: ungraded requires parent section ∈ eligible exempt, so a dated deletion is always graded.
Fixture FIX1: 25 dated lines whose text was born under `## Axes`, deleted from `## Round 1` → `exit=1 event deleted=25 graded=25 ungraded=0 status=unrestored`. True loss = yes (dated append-only content), and it is reported. Verdict correct.
Lane instance: the rule behaves as declared; no counter-example on the file.

### F2. Head deletion of head-born text stays ungraded (allowed re-derivation) — no defect
Fixture FIX2: 25 head-born lines deleted in a head rewrite (dated copies kept) → `exit=0 event deleted=20 graded=0 ungraded=20 status=ungraded`. True loss = no (head declared re-derived in place; text survives in dated copies). Verdict correct.

### F3. Traversal-ordered origin: identical final trees give opposite verdicts (side-branch/sibling case)
`origins()` assigns origin from the **first blob in `git rev-list --topo-order --reverse <to>`** that holds the text. Among sibling commits (parallel branches merged later) that order is a ref/object-order artifact, not content or chronology.
Fixture FIX3 (two constructions with byte-identical merged trees and identical event trees; only the branch that first introduced line `X twin` differs):
- X born under `## Axes` on main first → `exit=0 event deleted=21 graded=0 ungraded=21 status=ungraded` (X ungraded).
- X born under `## Round 1` on main first → `exit=1 event deleted=21 graded=1 ungraded=20 status=unrestored` (X graded).
Same final state, two different calibration outcomes. Because `--topo-order` only guarantees parent-before-child, sibling order (and thus the "first appearance" definition) is not content-determined.
Lane instance: the two merge commits in history (`2f7303c2`, `5396a876`) touch only LOG.md/README.md/considerthese — no merge ever touched SCORECARD.md, so no live instance; risk is prospective. Note the gate's own lane-leg origin copy (round49-…-check.py:317–335) uses the same order, so it cannot detect this.

### F4. Fenced fake `## ` title hides a dated-section loss
`sections()` (append-only-audit.py:265–272) treats any line starting with `## ` as a title, including inside ``` fenced blocks. A literal `## Axes` inside a fence that precedes dated content silently re-titles everything after it.
Fixture FIX4: dated `## Round 1` content born *after* a fenced but## Axes` line (same bytes as the real exempt title), then deleted → `exit=0 event deleted=25 graded=0 ungraded=25 status=ungraded`. True loss = yes (25 dated lines removed, exit 0). This is the only true-loss-still-ungraded vector left in v4.
Lane instance: **none observed**. Correct ```-aware scan over all 92 SCORECARD.md blobs: 0 headings inside fences (tip fence toggles at 2487/2494, 2615/2620 contain no `## ` lines). Latent risk: the file does carry fenced blocks in dated sections.

### F5. CRLF variants of head lines are falsely graded
Origin keys are byte-exact (`split_lines` keeps `\r`). A line whose CRLF variant never appeared before has no origin → graded even when deleted from an exempt head.
Fixture FIX5: line `crlf born\r\n` born in `## Round 1`, carried into `## Axes`, deleted in a head rewrite → `exit=1 event deleted=21 graded=1 ungraded=20 status=unrestored` — the CRLF head line is the 1 graded line (false positive; head re-derivation is allowed).
Lane instance: **none observed** — zero `\r` bytes in any SCORECARD.md blob in history (CRLF scan over `rev-list --all`).

### F6. Shared/boilerplate text: dated-born table separators and mirror rows are falsely graded in the head, and this hits the lane live
A head line whose text was first born in a dated section (or the preamble, section None) is graded when a head rewrite deletes it.
- Fixture FIX6 (table separator `|---|---|---|` born in `## Round 1`, reused in `## Axes`, deleted by head rewrite): `exit=1 event deleted=21 graded=1 ungraded=20 status=unrestored` (the separator is the 1 graded line).
- Fixture FIX7 (preamble-born line `# kama-shokunin - SCORECARD` reused in the head): same shape, `graded=1`.
- **Lane instance (live)**: event `0718b6abbda6 SCORECARD.md deleted=2421 graded=2356 ungraded=65` contains 7 deleted lines inside the exempt `## Capabilities` section whose origin is dated round sections — parent positions 121–127 in the event anatomy:
  - `| sources-registry | Curate where kama learns: …` … `| instrument-agreement | …` (6 lines, origin `## Round 34 — capability repertoire and instrument-registry coverage (2026-10-24)`)
  - `| pin-watch | …` (1 line, origin `## Round 41 — head axes table reconciled to the tree …`)
  These rows were born in dated round sections, mirrored into the head `## Capabilities` table (which the contract declares re-derived in place, `registry/append-only-contract.tsv:3`), and v4 re-grades their deletion. Same class of text (carried mirror rows) appears in the head at tip (the `## Capabilities` table, lines ~121–135 of the current file).

## Impact on axes

- **Calibration (C2)**: the tool's declared measure is correct for the laundering direction (F1, F2) but (a) is order-dependent (F3), (b) hides a dated loss behind fenced titles (F4), (c) byte-keys CRLF (F5), and (d) over-reports the lane's own head rewrites (F6). The frozen counter computes "natively exempt" with the identical logic, so the lane leg cannot see these — the gap is in the definition, not the implementation.

## Proposed corrections (frozen counters cannot change; forward)

1. **Fence-aware sections (`append-only-audit.py:265–272`)**: track ``` regions; ignore headings inside fences (one flag; fixes F4).
2. **CRLF-normalized origin lookup (F5)**: consult both `orig.get(text)` and `orig.get(text.rstrip(b"\r"))` in the ungraded test (line 475), leaving the byte-exact restore measure untouched.
3. **First-appearance restricted to the event's own lineage (F3)**: build origin only from blobs on the event's first-parent ancestor chain (plus side blobs that survive the merge, i.e. equal to an ancestor-chain blob). Removes side-branch-only births and ref-order dependence.
4. **Mirror-vs-laundering distinction for exempt-head deletions (F6)**: keep v4's origin test, and additionally keep a head-deleted line ungraded when its text still exists in a dated section at `<to>` (mirror refresh of a re-derived head). This protects the lane's `## Capabilities` mirror rows while still grading laundering (text gone from the file). Under this rule the 7 rows above would be ungraded; the launder fixture (counter scenario 1) still grades.

## Evidence files

- `lane-v4-tip.json` (tool JSON at measured tip), `event_anatomy.out` (per-line verdicts of both lane SCORECARD events), `c2-baseline.txt` (frozen counter, met=True), `fixture-summary.txt`, `fixtures-run1.out`, `fixtures-run3.out` (attack fixtures exit/event lines) — all in `.ufo/waves/round-49/w1/out/K2Origin/`.
