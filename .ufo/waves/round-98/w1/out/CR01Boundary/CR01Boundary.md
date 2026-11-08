# CR01Boundary — C3 depth attack: boundary table vs probe MAX_STEPS

Lane: kama-shokunin. Base `681c80a4e3c745c22559f74b2c2a1917bdc66fc6`;
freeze HEAD `34ad44e9f783b35a804f020d6b02c48c04ade481`. Seat CR01Boundary, lane-bound, no lane edits.
No subagents dispatched (leaf member).

The frontier axis for this seat is **depth** (7, below the 8 saturation line). C3's sentence is:
every row of `SKILL.md` §Round 97 correction recomputes from the probe's `MAX_STEPS` in
`tools/kama-probe.sh`'s `ROUTER_PY`.

## 1. Independent derivation of `steps = a + T*(b + nd)`

`need()` (`tools/kama-probe.sh:648-651`) charges one step per call and raises `Unknown`
(→ `-`) iff the running total will exceed `MAX_STEPS`; `rd()`/`skip()` also call `need()`
once each (`:658-667`). Counting `need()` calls:

**Preamble (`a = 4`).** On any path that reaches the tensor loop, four `need()` calls happen
first: `rd(4)` magic (`:720`), `u32()` version (`:722`), `u64()` `n_tensors` (`:725`),
`u64()` `n_kv` (`:725`). The audit's `PREAMBLE = 4` is exactly this count, and S622's
`gguf_header_t` fields (magic/version/tensor_count/metadata_kv_count) are those four reads.
(The count is path-conditional — see §4.)

**Per-tensor loop (`b = 5`, `:747-753`).** Each iteration performs:

- `skip(u64())` — `u64()` is `rd(8)` = 1 `need()`, `skip()` = 1 `need()` → **2** (name length + skip);
- `nd = u32()` — `rd(4)` → **1**;
- `[u64() for _ in range(nd)]` — `nd` × `rd(8)` → **`nd`**;
- `tt = u32()` + `off = u64()` — 1 + 1 → **2**.

Total `2 + 1 + nd + 2 = 5 + nd`. The round-96 probe comment (`:575-578`) states the same split,
and the round-98 audit (`PREAMBLE = 4`, `want_steps = 4 + T*(5+nd)`) re-derives it.

`MAX_STEPS = 5_000_000` (`:584`), `MAX_TENSORS = 1_000_000` (`:562`), `MAX_META = 512 MiB` (`:562`).

Ceiling at rank `nd`: `floor((5_000_000 − 4) / (5 + nd))` → nd=0: 999,999; nd=1: 833,332;
nd=2: 714,285; nd=3: 624,999; nd=4: 555,555. +1-overcharge ceiling: `floor(4_999_996/(6+nd))`
→ nd=1: 714,285; nd=4: 499,999. +2-overcharge ceiling: nd=1: 624,999; nd=4: 454,545.

So the **+1 window** (real decides `invalid`, +1 decides `-`) is
`714,286 < T ≤ 833,332` at nd=1 and `500,000 < T ≤ 555,555` at nd=4. The plan's W18 (800,000,
nd=1 → real 4,800,004; +1 5,600,004) and W19 (520,000, nd=4 → real 4,680,004; +1 5,200,004)
both sit strictly inside; the widened +2 window is `625,000..833,332` (nd=1) and
`454,546..555,555` (nd=4). `2×800,000+4,800,004 = 6,400,004 > MAX` confirms the plan's
"class is ≥+1" sentence.

## 2. Per-row verdict (@ freeze HEAD; base bytes identical — `SKILL.md`/`kama-probe.sh` diff = 0)

`python3 tools/round98-depth-boundary-audit.py --repo . --rev HEAD` → `rows=6 checks=12
mismatches=4 met=False` (exit 1); `--rev 681c80a4` → identical line by the base rev (exit 1).
Both reproduce `controls/c3-base.out`; the four mismatches at HEAD/base are: 2 missing required
rows + S622 absent + `rows != 8`. That is the do-nothing control behaving as declared (C3 is
`pending` at M3 in `claims.json`); the counter discriminates.

Recomputed against the probe's `MAX_STEPS = 5,000,000` (real probe: `steps ≤ MAX` → proceeds
to later checks, fixture ⇒ `invalid`; `steps > MAX` → raises `Unknown` ⇒ `-`):

| T | nd | steps = 4+T·(5+nd) | `<=`/`>` vs 5,000,000 | verdict (audit expectation) | real-probe outcome | +1 probe | so-old-6-could-catch-+1? |
|---|---|---|---|---|---|---|---|
| 833,332 | 1 | 4,999,996 | <= | invalid | invalid (≤ MAX, reaches later checks) | `-` (5,833,328) | **NO** — old row already `-` under real at the boundary's other side; see below |
| 833,333 | 1 | 5,000,002 | > | `-` | `-` (raises at 5,000,002nd need) | `-` (5,833,335) | no |
| 900,000 | 1 | 5,400,004 | > | `-` | `-` | `-` | no |
| 700,000 | 4 | 6,300,004 | > | `-` | `-` | `-` | no |
| 555,555 | 4 | 4,999,999 | <= | invalid | invalid (1 step of slack) | `-` (5,555,554) | **no** (same structural blindness as 833,332) |
| 555,556 | 4 | 5,000,008 | > | `-` | `-` | `-` | no |
| 800,000 | 1 | 4,800,004 | <= | invalid (required W18 row; not yet in SKILL) | invalid | `-` (5,600,004) | **yes — the window row** |
| 520,000 | 4 | 4,680,004 | <= | invalid (required W19 row; not yet in SKILL) | invalid | `-` (5,200,004) | **yes — the window row** |

Wait — the two "within-budget" old rows (833,332/nd=1, 555,555/nd=4) *also* discriminate:
under +1 they exceed the budget. The plan's premise "the six rows are all on the budget's far
side" is **wrong as a structural statement**: two old rows are on the near side and *do* split
real vs +1. What the old rows lack is a *clean* split, because at the ceiling vertex the only
difference is `invalid` vs `-` and the old section pointed readers at the ceiling — the RV03 F5
finding stands on the **17 budget cells**, not on the table. The C2 cells being overcharge-blind
was a fixture property; the table's near-side rows would have caught +1 too if graded as verdicts.
The new rows are better placed (mid-window, ~200k/100k steps of slack) but they are not the
*first* two rows that split on +1. This does not falsify C3; it means C3's "before" sentence
("the round-97 table's six rows are all on the budget's far side") understates the table it
replaces. The audit still enforces exactly the rows the claim names.

Every present row's arithmetic recomputes from `MAX_STEPS`:
`4 + 833,332×6 = 4,999,996 ≤` ✓; `4 + 833,333×6 = 5,000,002 >` ✓;
`4 + 900,000×6 = 5,400,004 >` ✓; `4 + 700,000×9 = 6,300,004 >` ✓;
`4 + 555,555×9 = 4,999,999 ≤` ✓; `4 + 555,556×9 = 5,000,008 >` ✓.
The `<=`/`>` symbols match (probe raises iff `steps > MAX_STEPS` — `need()` `:650`, so equality
decides) and each verdict string matches the audit's rule `invalid iff steps ≤ MAX_STEPS`.
The required new rows compute identically: `4 + 800,000×6 = 4,800,004 ≤` ✓,
`4 + 520,000×9 = 4,680,004 ≤` ✓.

**Round-96 vs §97. No arithmetic contradiction.** The §96 ceiling table recomputes exactly
(999,999 / 833,332 / 714,285 / 624,999 / 555,555) and matches §97's ceiling citations. The
real tension is prose-vs-table: §96 line 2441's "now decides invalid at nd ≤ 2 and stays `-`
at nd ≥ 3" for the 700,000-tensor file is correct (nd=2: 4,900,004 ≤; nd=3: 5,600,004 >), but
§96 states ceilings with no KV-free precondition while §97 adds it (`KV-free`, `nd > 4`). The
§97 caveat is a restriction, not a correction of §96's numbers. §97's heading "the three
graded forgeries" vs its own four-mutant body remains a contradiction — that is C1's check 19,
not C3's, and C3's counter does not grade the heading.

## 3. Width attack: what the table as frozen does not name

**Inside the overcharge window, unnamed (T, nd):** the table will name one vertex per rank
(800,000 @ nd=1; 520,000 @ nd=4) of windows 119,047 and 55,556 wide. Unnamed examples voters
could still ask about: (714,286, nd=1) (the +1 ceiling's first failing T — the window's edge,
neither old row touches it), (750,000, nd=1), (500,000, nd=4) (the window's edge),
(510,000, nd=4), (833,332, nd=1) itself (discriminates, per above). The audit's `rows != 8`
freeze **forbids** adding them: a table with nd=0/2/3 window rows would fail C3 even if every
row were correct. The claim freezes the incompleteness it discloses.

**Outside the +1 window where a +2/header probe is misread:** the table's most salient row is
(700,000, nd=4) with verdict `-`. A reader pattern-matching "700,000 headers → `-`" misreads
(700,000, nd=1): real = 4,200,004 `invalid`, +2 probe = 5,600,004 `-`. The same count flips by
rank inside the window, and the table's unranked salience invites the error. §97's prose
sentence "a 700,000-tensor nd=1 file decides invalid" catches a careful reader, but the table
*as a table* (which C3 grades) carries no T ∈ [625,000, 714,285] @ nd=1 row at all, so a
+2-probe auditor selecting table rows to falsify +2 has only (800,000, nd=1) and (520,000, nd=4)
— both work (+2: 6,400,004 and 5,720,004), but the table never says the +2 window is wider.
The `rows=8` kill-forbidding also blocks a clarifying +2 row.

**Two more concealed width gaps (both bind M3, neither blocks it):**

- **Ranks 0, 2, 3 have +1 windows with no rows at all** (nd=0: 833,333..999,999; nd=2:
  625,000..714,285; nd=3: 555,556..624,999). "It is not a proof over all (T, nd) pairs, which
  the per-rank ceiling formula already covers in the round-96 table" assumes formula-attention;
  the §97 section's own text ("this section is the boundary decision a reader can apply
  without re-parsing") promises row-level usability the eight rows do not have for nd=0/2/3.
- **The audit skips non-matching rows silently** (`continue`, line 95): a 9th boundary row in
  a different column shape would be graded by nobody and `rows = 8` would still pass. The
  counter grades "every row present" only in the exact 5-cell shape.

## 4. Limits the C3 sentence does not carry (defects, not killers — all M3-binding)

1. **"Verdict recomputes from MAX_STEPS" is only half-true.** The verdict *is* a function of
   (T, nd) only through the budget side. Within budget the parser continues to alignment/size
   checks (`:763-768`); a *well-formed* file at (800,000, nd=1) returns `ok` (→ router
   loadable), not `invalid`. The table's `invalid` is the crafted fixtures' verdict, and §97's
   prose "decides it (invalid) when that sum fits" (SKILL:2447) overclaims decidability as
   invalidity. The counter never runs the probe, so this is structurally ungradeable by C3.
2. **"4 preamble steps" is path-conditional.** A bad-magic file pays 1 step and is `invalid`
   without ever reading `n_tensors`; an oversize-declared file pays 4 and is `-` before any
   header (`:731`); a file with `n_kv > MAX_KV` is `-` before the loop. A file that reaches
   the loop at reduced preamble never exists, but the formula's universality is fiction — the
   fixtures sit on the happy path.
3. **Doubled path to `-`:** `MAX_META`/position (`:653`) and unknown-type (`:754-755`) free
   exits exist below the budget. A file inside step budget can still be `-` for reasons the
   table's KV-free/nd≤4 caveat does not name. The fixtures don't exercise them; C3 discloses
   only the all-pairs limit.
4. **Newly-checkable evidence the counter ignores:** the audit reads `MAX_STEPS` from the
   probe by regex (line 69) but nothing binds PREAMBLE/5 to the probe constants; a probe
   edit changing only the comment's candor would not move the counter. Kill rule K1 (frozen
   counter bytes) is the only guard, and it binds the audit, not the probe.

## 5. Does C3's sentence hold?

**At HEAD/base, as a sentence about the future M3 table: yes for arithmetic, narrowly — the
eight rows the plan names are correct and re-derive from `MAX_STEPS = 5,000,000` exactly.**
It does not hold as a sentence about the present text: at both HEAD and base the section carries
six rows and the counter is red; M3 must land two rows and the S622 citation before the
predicate can print `met=True`. The table's *width* overclaims: the old six rows already split
real vs +1 at two vertices (the "far side" premise is false of the table, true only of the
17 cells), the eight rows leave three ranks' windows unnamed while the `rows=8` freeze forbids
naming them, and the audit's exact-shape skip can hide a malformed ninth row. The verdict
column half-recomputes (budget side; `invalid` needs the fixture's later-invalid property).
No arithmetic, comparison or verdict cell in the six rows — or the two required rows — is
wrong; the attacks above are about completeness, conditioning and what the counter can see,
and would survive a green M3 run.

Commands run:
`python3 tools/round98-depth-boundary-audit.py --repo . --rev HEAD` (exit 1, pasted above);
`--rev 681c80a4` (identical); `diff SKILL.md/kama-probe.sh 681c80a4..HEAD` = 0 lines;
independent recompute scripts for ceilings, windows, and all eight rows.
