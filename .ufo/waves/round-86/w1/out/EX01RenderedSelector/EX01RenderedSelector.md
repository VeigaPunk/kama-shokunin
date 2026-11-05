# EX01RenderedSelector — round 86 w1 findings (C1 calibration)

Seat: EX01RenderedSelector (leaf executor). Target: `tools/round86-rendered-cells.py` (frozen C1
instrument). Lane revisions: base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`, freeze
`c07e1f909414aafb2d8de5605a81fd3bd4e3550e`, lane HEAD at read time `f4c7acaa0563d1cf813fff90e4b927494a88091f`.
The instrument and `count.py` are byte-identical between freeze and HEAD (`identity.txt`, empty diff).
Note: the lane worktree shows ` M SCORECARD.md` (not this seat's; not touched). All runs read committed bytes.
Report path per contract: `.ufo/waves/round-86/w1/EX01RenderedSelector.md` is outside this seat's writable
dir; this note is written in `out/EX01RenderedSelector/` instead.

## Verdict

**C1's selector is NOT admissible as frozen.** Five fixtures that hold correct tokens while the live
cells are stale exit 0 (the R85 false-green class is not fully closed). The frozen kill rule
("every shadow … MUST exit 1") fires.

Escapes, each measured on a committed fixture, exit 0 with stale live cells:

| id | construct | why it escapes |
|---|---|---|
| V10b | flush inline `<!--x-->` + cell on the same line | `rendered()` keeps the text after `-->` at column 0 |
| V16 | comment closer line `-->` + cell (cell flush after the closer) | same split; CommonMark 4.6 says the whole closer line is inside the HTML block |
| V21 | green cell as lazy continuation of a block quote (no blank line, no `>`) | a lazy line is a column-0 line to the selector |
| V21c | plain top-level green cell placed **above** the stale head (no quote, no fence) | liveness is the FIRST column-0 cell; a top-level copy above the head wins |
| V22 | calibration row supplied by a **later** `## Axes` while the first has none | `select_cells` sets `row` from any `## Axes` section, not the first (frozen: "first `## Axes` section") |
| V23a | gate coupling: cell names revision A whose receipt lacks the token; the token exists only at the tip | `gate_fact` reads the receipt with `tree.blob(path)` at the **graded revision**, not at R (frozen: "the receipt's bytes at R") |

Divergence (not a false green today): V20, an info string containing a backtick. CommonMark 0.31.2 §4.4
says this is not a fence; the instrument fences it anyway. The result is exit 1 only by accident. A
strict-CommonMark fix would make this shadow first-match live and green, so any fix must change the
first-occurrence rule together with the fence opener.

Correct as frozen (exit matches the bar): V00, V01, V02–V06, V07 (exit 2), V08, V09, V10, V11, V12 (exit 1),
V12b (exit 2), V13, V14, V15, V17 (exit 2), V18 (control, exit 0), V19 (exit 2), V22c (control, exit 1), V23b (control, exit 0).
Fail-closed (exit 2) on unclosed fences/comments and on wrong-char closers means a live cell can be hidden
without a green result. That is acceptable under the frozen rule.

## Counter receipts (real counter, `count.py c1`; instrument bytes from freeze checkout, tree at --rev)

Command (fixture clone, `--work` under scratch): `python3 .ufo/waves/round-86/count.py c1 --repo . --rev <rev> --work <dir>`

base `3ff23da3`, exit **1** (`counter-base.out`, `counter-base.exit`):
```
RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85
RENDERED_CELLS_FINDING gate declared round=84 newest terminal receipt round=85 (.ufo/waves/round-85/measured/after/gate.out)
RENDERED_CELLS_FINDING closure row names round-84 newest committed closure is round-85 (corpus/lessons/round-85-verifier-spotcheck.md)
RENDERED_CELLS_FINDING disposition row does not name `round85 rejected-honest-stop`
```
freeze `c07e1f90`, exit **1** (`counter-freeze.out`, `counter-freeze.exit`): identical output.
Instrument selftest at freeze: `python3 tools/round86-rendered-cells.py --selftest` → `RENDERED_CELLS_SELFTEST pass=11 fail=0`, exit 0.

## Fixture battery (23 constructs + 4 controls; driver `build_variants.py`, `build_fix.py`, `build_more.py`)

Receipts: `receipts/V*.out|.exit|.sha`, `receipts/variants-summary.txt`, `receipts/fix-driver.out`, `receipts/more-driver.out`.
Each fixture is a committed SCORECARD in a clone detached at the freeze commit; every R is an ancestor.

Exit codes measured: fence3 1, fence3-info 1, fence4-info 1, tilde 1, fence closed by longer run 1, unclosed fence before live 2, unclosed fence after live 1, comment multi-line 1, comment single-line inline 1, **comment flush inline 0 (V10b)**, indent4 1, correction EOF 1, correction before live 2, fence in comment 1, comment in fence 1, blockquote `>` 1, **comment closer tail 0 (V16)**, unclosed comment 2, fenced-stale control 0, tilde closed by backtick 2, backtick info 1 (V20), **lazy blockquote green over stale 0 (V21)**, **plain green above stale 0 (V21c)**, **row from later Axes 0 (V22)**, first-Axes stale control 1 (V22c), **receipt token only at tip 0 (V23a)**, token-at-A control 0 (V23b).

## Real SCORECARD census (`census_real.py`, `receipts/census-real.out`, `real-positions.out`, freeze bytes)

- 5252 lines; 0 HTML comment openers or closers; 0 indented (4+) non-blank lines; 0 fence anomalies (every fence closes, none opens with a backtick in its info string).
- 42 fence delimiter lines, first at L2531. 4 correction headings (L4912, L4950, L5073, L5195). 4 column-0 blockquote lines (L1367, L2680–2682), none followed by a cell-shaped line.
- Live cells: authority at L6, `## Axes` at L8, calibration row at L18, all above every construct. Nothing above L6 can hide them.
- Constructs that could still hide a live cell in the future: a fence opened above L6 (unclosed → exit 2); a `-->` tail or flush `<!--x-->CELL` above the head (V10b/V16); any top-level copy of a cell above L6 (V21c); a second `## Axes` with the calibration row when the first omits it (V22); any copy of the receipt token placed only at the tip (V23a). None is present in the real file at the freeze.

## Recommendations for the integrator (not applied; I did not edit production)

1. Bind the gate coupling to the receipt at R: read the receipt with `tree.blob` at `R`, not at `self.rev` (V23a).
2. Stop the first-occurrence liveness: require the head cell to be the unique top-level cell, or the last one, and fail if more than one authority or calibration row exists at column 0 (V21c, V22).
3. Take the comment tail as part of the comment: after `-->`, drop the text up to the end of the line, or reject the line as a block (V10b, V16).
4. Align the fence opener with CommonMark 0.31.2 §4.4 (reject a backtick in the info string) only together with item 2 (V20).
5. Add V10b, V16, V21, V21c, V22, V23a as frozen controls that must go red before C1 is re-measured.

Tooling: none installed. Scratch `/fast/scratch/hyaku/kama-r86/EX01RenderedSelector/` removed after receipts were copied here.
