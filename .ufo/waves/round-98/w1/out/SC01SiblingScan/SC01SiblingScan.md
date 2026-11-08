# SC01SiblingScan — fleet read-only scan for the two round-98 shapes

Seat: SC01SiblingScan (leaf, no dispatch) · lane: kama · round 98 w1 · scope: read-only recon
across sibling lanes `/home/vgpnk/Projects/shokunin/*-shokunin` and the fleet root
`.ufo/reports/round-9*/`. No file outside my out dir and my scratch dir was written; no git/jj
mutation was run; no clone or fixture was needed (the scan is a read of committed bytes).

## Shapes searched

- **(a) one-direction counter** — a budget/probe check that can only fail in one direction, so it
  goes green on a probe that over-charges (charges more, refuses more, or hides a population).
- **(b) heading-line blindness** — a section heading or a stated count that no counter grades:
  the heading line is read off, or the count is asserted in prose and nothing re-derives it.

## PRESENT rows (12)

| # | Lane | file:line | Shape | Phrase that shows the class |
|---|---|---|---|---|
| A1 | tameshi | `.ufo/evidence/round-91/c2/measure-c2-v91.sh:60-62` (read via `corpus/lessons/round-91-verifier-spotcheck.md:68`) | a | `expect=$(sha256sum "$WORK/blobrun-ledger-witness.py" …)` and `pinned=$(sha256sum "$WORK/blobrun-ledger-witness.py" …)` hash the **same file**: "structurally can only fail on a missing blob, never on a wrong pin" |
| A2 | kaidoku | `tools/round-31/c2-sqlite-refusals.py:42` (fixtures `:109` `sparse-268435457`, `:128` `wal-sparse`; `corpus/evidence/round-31/c2/predictions.tsv:23-24`) | a | `BUDGET = 268435456` with mutants **only over** the ceiling; the largest accepted carrier is `chinook` 1 067 008 B (`corpus/evidence/round-31/c1/carriers.tsv:7`), so a probe refusing above ~10 MB passes every cell — the 256 MiB value is pinned from the over-charge side only |
| A3 | kotodama | `reports/round-90/measure90.py:160` (routed in `corpus/lessons/round-90-verifier-spotcheck.md:113`) | a | `ok = ('SELFTEST' in text and 'FAIL' in text and 'MUTATION' in text and 'broken-pattern' in text)` — the STUB leg is "a presence check, so it cannot fail" |
| A4 | kaidoku | `tools/round-96/kill-rule-v2.py:5` | a | "a kill rule whose checks never called the counter's `main()` and never ran the probe, so five of the ten round-95 mutants survived it" |
| A5 | kake | `corpus/lessons/round-91-verifier-spotcheck.md:72` | a | `mutants=34 killed=20 survivors=14 met=true` — the counter's own verdict is green with 14 forgery-class survivors |
| A6 | mori | `corpus/lessons/round-93-verifier-spotcheck.md:113` | a | "**D6 — no reject in the round's Gate.** Discernment sample is one-sided." |
| B1 | kaidoku | `tools/round-36/c1-counter.py:59` (same helper at `round-38:62`, `round-39:150`, `round-40:270`, `round-41:365`, `round-42:597`, `round-44:508`, `round-49:516`, `round-50:571`) | b | docstring `"""Lines after an exact heading line up to the next line starting with '## '."""` — the heading itself is never graded. Only `round-37/c1-counter.py:51` (`out = [line]`) keeps it |
| B2 | kotodama | `tools/check-advance-evidence.py:701` (routed in `corpus/lessons/round-90-verifier-spotcheck.md:115`) | b | `if len(heads) < args.min_headings:` — a floor, never an equality, so "The entry has 8 `##` headings, not 10 (report and SCORECARD)" was never graded |
| B3 | tameshi | `SKILL.md:1477` | b | `### Where to enter — four readers` — a count word in a heading; `grep -rn "four readers" tameshi-shokunin/tools tameshi-shokunin/verifiers` → 0 hits, so no counter in the lane reads it |
| B4 | tameshi | `.ufo/evidence/round-91/c1/measure-v91.py:138` (read via `corpus/lessons/round-92-verifier-spotcheck.md:56`) | b | `re.match(r"^\|\s*(C\d\d)\s*\|", raw)` matches only two-digit ids — "a hidden `C001`-`C012` table is invisible to it" |
| B5 | kasegi | `LOG.md:5` vs `LOG.md:184` vs `SKILL.md:8` (fleet record `.ufo/reports/round-9/protocol.md:32`) | b | "275 claim dirs" vs "295 claim dirs" vs "274 program dirs / 295 packages" in one lane; the fleet row lists it among "6 major count defects"; kasegi ships no `tools/` at all |
| B6 | kengaku | `corpus/knowledge/bench-arena-round7-noise-n25.md:24` (table `:13`, erratum `:80`; fleet record `.ufo/reports/round-9/protocol.md:35`) | b | "0/12 PASSes (discordance 0/25)" against the file's own `PASS/25` table (17/25 PASS) and its own erratum "`0/12` → `0/17`"; the fleet row says the denominator is still wrong (`0/25` should be `0/17`); kengaku ships no `tools/` and no `verifiers/` |

Rows are **PRESENT** (the class occurs at that site), not claims that the sibling is currently red —
several of these were routed and fixed by the sibling after the fact (A3 → kotodama round 91, A4 →
kaidoku round 96, B2 → kotodama round 91, B6 → kengaku errata). The class is what the site shows.

**Class fit.** A1, A2, A3, A5 are exact (a named budget/probe/counter leg that can only redden in one
direction). A4 is exact in effect (a kill rule that never exercised the probe, so five mutants
survived it). A6 is adjacent, not exact: mori's one-sided *Gate sample* (no rejected candidate
sampled), not a budget bound — it shows the same "green on one side only" reflex in the sampling
design rather than in a threshold. B1–B4 are exact (a heading line or a stated count that no counter
reads). B5, B6 are exact as *ungraded count claims* in lane prose, with no counter in either lane to
grade them (kasegi: no `tools/`; kengaku: no `tools/`, no `verifiers/`).

## One-line conclusion

**Kama's round-98 instruments are AHEAD of the siblings on both shapes** — kama is the only lane in
the fleet whose counter reads a count word off a heading (`round98-self-assessment-audit.py:346-349`),
the only one whose budget counter names the cell that must redden (`--expect-cell`,
`round98-router-budget.py:605`) and closes the overcharge window with two decidable cells, and the
only one whose depth table recomputes every row from the probe's own `MAX_STEPS` read at the
measured revision (`round98-depth-boundary-audit.py:69-71`) — with the caveat that kama's r98
instruments are still **unmeasured** (`.ufo/waves/round-98/measured/` is empty; only the freeze-time
controls exist), and that `SKILL.md` at HEAD still reads "the three graded forgeries" (`:2443`) with
six boundary rows (`:2449`), so check 19 and C3's `rows=8` will red until the wave lands the
SKILL.md roll-forward.

## Supporting detail (fleet evidence used for the conclusion)

- **Heading-count grading is unique to kama.** Fleet-wide `grep -rn --include="*.py" "graded
  forgeries" */tools/ */verifiers/` returns only `kama-shokunin/tools/round97-self-assessment-audit.py`
  and `round98-self-assessment-audit.py`; the count-word table `WORDS = {…}` (`:72`) exists in kama
  only — the near neighbours are `kaidoku-shokunin/tools/round-77/verdict-bind.py:63` and
  `round-78/attack-gate.py:115`, which bind count words in **body** clauses, not headings.
- **Named-red-cell control is unique to kama.** Fleet-wide `grep -rn --include="*.py" "expect_cell"`
  hits only `kama-shokunin/tools/round97-router-budget.py` and `round98-router-budget.py`.
- **Sibling `section()` helpers are heading-blind, kama's r98 counter is not.** kaidoku's r36/r38/
  r39/r40/r41/r42/r44/r49/r50 helpers all slice `lines[i + 1:]`; kama's r98 audit keeps that helper
  for the body (`round98-self-assessment-audit.py:95-104`) but reads the heading line separately for
  check 19 (`:346-348`) — the same fix kaidoku once had at `round-37/c1-counter.py:51`.
- **Kama's r98 budget cells are sized inside the overcharge window.** `W18-800k-nd1` (800 000
  headers, nd=1: real 4 800 004 ≤ MAX_STEPS, +1 probe 5 600 004 → `-`) and `W19-520k-nd4` (520 000,
  nd=4: real 4 680 004, +1 probe 5 200 004 → `-`); both sit strictly inside 714 286 < T ≤ 833 332
  (nd=1) and 500 000 < T ≤ 555 555 (nd=4). The freeze-time controls show the overcharge mutant
  reddening exactly those two cells (`controls/c2-new-mutants.out`: `expect_cell=W18-800k-nd1
  cell_ok=0 caught=1` and `expect_cell=W19-520k-nd4 cell_ok=0 caught=1`) while the 17 round-97 cells
  survive it (`controls/c2-legacy-mutants.out`: `cells=17 cells_ok=17 … survived=1`) — the class the
  round set out to close, demonstrated by its own receipts.
- **Kama's r98 depth audit re-derives the bound from the probe.** `MAX_STEPS` is parsed out of
  `tools/kama-probe.sh` at the measured revision (`round98-depth-boundary-audit.py:69-73`), each
  row's `4 + T x (5 + nd)` is recomputed and compared against it, and the eight required rows are
  enforced as a set (`:37-38`, `:111-113`).

## Method, limits, and honesty

- Commands used: `grep -rn`/`glob`-style searches over `*/tools/*.py`, `*/verifiers/*.py`,
  `*/corpus/lessons/round-9*-verifier-spotcheck.md`, `.ufo/reports/round-9*/`; `sed -n` line reads
  for every quoted site; `awk`/`grep -c` counts for the table/row claims. All read-only.
- No LSP server was consulted for these lanes (the scan is text-shaped: heading strings and count
  words across Markdown and Python); the grep results above are literal evidence, not semantic
  proof of call-graph reachability.
- Not searched (out of the seat's named scope, so no claim is made either way): sibling lanes with
  no `tools/` dir at all (audio, game-dev-2d/3d, lore, kasegi, kengaku — the last two are represented
  by their corpus prose rows B5/B6), and `kumitate`/`tabi`/`souji` prose-only rounds.
- Counts quoted as "no counter grades it" were verified by grepping the lane's `tools/` and
  `verifiers/` trees for the literal string (B3: 0 hits; B6: no `tools/`, no `verifiers/`).
- The kotodama B2 entry's live count ("8 `##` headings") is quoted from the lane's own lesson
  (`:115`); the entry path named there was not present at this scan, so no live re-derivation is
  claimed.
- Tool installs: none — no package was needed for this read-only scan, so no channel/version record
  is owed.
- Scratch `/fast/scratch/hyaku/kama-r98/SC01SiblingScan/` was created and removed; it stayed empty
  (no clone, no fixture, no `/tmp` payload).
