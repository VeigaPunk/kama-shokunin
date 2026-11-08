# SN01StepFlips — the real probe's step boundary, measured without the counters

Seat `SN01StepFlips`, lane `kama-shokunin`, round 98 wave 1, milestone `kama r98 w1`.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only; no tracked lane file touched).
Scratch: `/fast/scratch/hyaku/kama-r98/SN01StepFlips/` (deleted before yield).
Receipts: `.ufo/waves/round-98/w1/out/SN01StepFlips/receipts.json`.

**Method.** I built my own GGUF fixtures and my own stub router; I did not import the frozen
counter's fixtures or reuse its verdict logic for the primary measurement. The probe bytes are
`git show HEAD:tools/kama-probe.sh` (sha256 `40ab387e…4a6e`, identical at base `681c80a4` and at
the freeze `34ad44e9`), copied into scratch and never edited in place. The stub mirrors the
counter's shape: `GET /v1/models` returns one entry `{"id":"good","status":{"value":"unloaded",
"args":[<existing abs file>,"-m",<fixture>]}}`, `GET /props` returns
`{"role":"router","models_autoload":true}`; the probe runs as `check --port P --expect good
--timeout 5 --connect-timeout 2 --json`.

**Step boundary measured from the running code, not from prose.** Rather than trusting
`4 + T x (5 + nd)`, I binary-searched `MAX_STEPS` on scratch copies of the probe bytes and found
the smallest `MAX_STEPS` at which the parser still DECIDES (`invalid`) — i.e. the number of steps
the real parser actually charges. A threshold near 4 means the size guard decided before the
tensor loop; a threshold equal to `4 + T x (5 + nd)` means the header parse completed and the
offset check decided.

---

## 1. Fixture table (my own bytes; verdicts from the real probe)

| fixture | T | nd | bytes | size guard needs | size guard fires | MAX_TENSORS fires | plan steps | **real verdict / reason** | wall (3 runs) |
|---|---|---|---|---|---|---|---|---|---|
| `t800k_nd1` | 800 000 | 1 | 32 000 048 | 19 200 000 | **no** | no | 4 800 004 | `MODEL_UNLOADED` / `router-model-invalid` (rc=2) | 1.96 / 2.01 / 2.00 s |
| `t520k_nd4` | 520 000 | 4 | 33 280 048 | 12 480 000 | **no** | no | 4 680 004 | `MODEL_UNLOADED` / `router-model-invalid` (rc=2) | 2.34 / 2.42 / 2.41 s |
| `t714286_nd1` | 714 286 | 1 | 28 571 504 | 17 142 864 | **no** | no | 4 285 720 | `MODEL_UNLOADED` / `router-model-invalid` (rc=2) | 2.36 / 2.52 / 2.31 s |
| `t555554_nd4` | 555 554 | 4 | 35 555 504 | 13 333 296 | **no** | no | 4 999 990 | `MODEL_UNLOADED` / `router-model-invalid` (rc=2) | 2.77 / 2.69 / 2.79 s |

All four grade **`invalid`**, exactly as the plan's arithmetic predicts. **No fixture's real
verdict differs from the plan — C3's arithmetic and C2's cell expectations stand.** The probe's
own parser (`ROUTER_PY` "files" mode, the call `router_file_states` makes) returns `invalid` for
all four in 1.87 / 2.32 / 2.17 / 2.63 s.

Cross-check against the frozen counter's bytes: my `t800k_nd1` and `t520k_nd4` are **byte-identical**
to the counter's `gguf(OVER_TENSORS,1,False)` and `gguf(OVER4_TENSORS,1,False,nd=4)` (sha256
`2231f28b…` / `cd39ff55…`, `identical=1`), so the numbers above apply to the counter's own W18/W19
fixtures. Its byte-oracle labels them `invalid`, matching the live verdict.

### Measured step threshold vs. the plan's formula

| fixture | measured deciding threshold | plan `4+T(5+nd)` | match | measured **+1/header** threshold | plan `4+T(6+nd)` | match |
|---|---|---|---|---|---|---|
| `t800k_nd1` | **4 800 004** | 4 800 004 | yes | **5 600 004** | 5 600 004 | yes |
| `t520k_nd4` | **4 680 004** | 4 680 004 | yes | **5 200 004** | 5 200 004 | yes |
| `t714286_nd1` | **4 285 720** | 4 285 720 | yes | **5 000 006** | 5 000 006 | yes |
| `t555554_nd4` | **4 999 990** | 4 999 990 | yes | **5 555 544** | 5 555 544 | yes |

The formula `steps = 4 + T x (5 + nd)` is **exactly** what the running parser charges, and the
`+1/header` mutant charges exactly `4 + T x (6 + nd)`. Eight of eight match, to the step.

### Which guard decides (question 3 of my brief)

**Neither the size guard nor MAX_TENSORS decides either of the two new cells' fixtures — the
step budget does.** Measured, not asserted:

- **size guard** (`n_kv*13 + n_tensors*24 > size`, `tools/kama-probe.sh:729`): needs 19 200 000
  (W18) and 12 480 000 (W19) bytes; the files are 32 000 048 and 33 280 048. Not fired. (The
  counter's own `gguf()` writes the same byte counts — the guard's threshold is met with 12.8 MB
  and 20.8 MB of slack.)
- **MAX_TENSORS** (`1_000_000`, `tools/kama-probe.sh:562`): 800 000 and 520 000 are below it.
  Not fired.
- **step budget**: the measured threshold EQUALS the plan's step count exactly for all four, so
  the verdict is decided by the header parse completing inside `MAX_STEPS` and then failing the
  offset check (`tools/kama-probe.sh:766`, the fixture carries no data section).

Control experiments proving the measurement discriminates the guards (same harness, forced):

| forced case | measured threshold | verdict | meaning |
|---|---|---|---|
| 800k header **truncated** to 10 000 000 bytes | **4** | `invalid` | the size guard fired at the preamble — before the tensor loop. Threshold ≈ 4, not 4 800 004. |
| same truncated file under the `+1/header` mutant | **4** | `invalid` | the mutant's threshold is also 4 — the cell would be **vacuous** (both sides `invalid`). |
| 1 200 000 headers (> MAX_TENSORS) | **none** | never `invalid` | MAX_TENSORS decides; the file is undecidable at every budget. |

So the guard order is unambiguous: **size guard → MAX_TENSORS → step budget**, and the two new
cells' fixtures land squarely on the **step budget**, the only one of the three that a `+1/header`
probe can flip.

### The window edges, measured

Six extra fixtures on the boundary, same stub, same probe:

| T | nd | real verdict | +1/header verdict | in the +1 window? |
|---|---|---|---|---|
| 714 285 | 1 | `MODEL_UNLOADED`/`router-model-invalid` | `MODEL_UNLOADED`/`router-model-invalid` | no (both decide) |
| **714 286** | 1 | `MODEL_UNLOADED`/`router-model-invalid` | `MODEL_OK`/`router-unloaded-autoload` | **yes — first T that flips** |
| 714 287 | 1 | `MODEL_UNLOADED`/`router-model-invalid` | `MODEL_OK`/`router-unloaded-autoload` | yes |
| 499 999 | 4 | `MODEL_UNLOADED`/`router-model-invalid` | `MODEL_UNLOADED`/`router-model-invalid` | no |
| **500 000** | 4 | `MODEL_UNLOADED`/`router-model-invalid` | `MODEL_OK`/`router-unloaded-autoload` | **yes — first T that flips** |
| 500 001 | 4 | `MODEL_UNLOADED`/`router-model-invalid` | `MODEL_OK`/`router-unloaded-autoload` | yes |

The window's lower edge is exactly **T = 714 286 at nd=1** and **T = 500 000 at nd=4**, i.e.
`714 285 < T` and `499 999 < T`. The plan writes the window as `714,286 < T ≤ 833,332` at nd=1
and `500,000 < T ≤ 555,555` at nd=4 (`plans/round-98-claims.md:99`); measured, the window is
`714 286 ≤ T ≤ 833 332` and `500 000 ≤ T ≤ 555 555` — the plan's left inequality is off by one
at both ranks. **This does not falsify any claim** (W18/W19 are far inside the window; the two
new cells are correctly sized), but it is a stated bound that a reader would use to decide
whether a given file decides under a `+1/header` probe, and it is wrong exactly at the edge.
The same off-by-one appears in `corpus/lessons/round-98.md` and in the wave's own
`.ufo/waves/round-98/w1/CN01Overlap.md:130` and `CR01Boundary.md:39-40`.

### Falsification verdict for my brief

**C3's arithmetic holds and C2's cell expectations hold — measured, not assumed.** All four
fixtures grade `invalid` as the plan predicts; the formula is exact to the step; neither of the
two new cells' fixtures is decided by the size guard or MAX_TENSORS; and a `+1/header` probe
flips exactly the two new cells (and the two new boundary rows) to `-` while the six round-97
rows it also flips are the ones already on the far side. The `+1/header` probe's true nd=1
ceiling is **714 285** and its nd=4 ceiling **499 999**, against the 833 332 / 555 555 the lane
documents — the defect the round exists to close is real and the two new cells close it.

---

## 2. The blocking defect I found: C1 cannot go green, and the fix touches a frozen counter

**Severity: HIGH (operability + calibration). C1's predicate `mismatches=0 met=True` is
UNREACHABLE at any M1 that leaves the frozen counter bytes alone.**

`tools/round98-self-assessment-audit.py:305,309` (check 16):

```python
doc_cells = re.search(r"adds (\w+) cells", rdoc)
...
and doc_cells and WORDS.get(doc_cells.group(1).lower()) == len(new_cells)
```

`rdoc` is the docstring of `tools/round98-router-budget.py`, whose line 14 reads:

> `Round 98 adds two cells past that (new set = six cells, mutants = five):`

The regex matches **`adds two cells`** → `WORDS["two"] = 2`, but `len(new_cells) = 6`
(`NEW_CELLS` = W14…W19). `2 != 6` → the term is **false unconditionally**. The string
`adds six cells` does not occur anywhere in the docstring; `new set = six cells` does (offset 794)
and is *not* what the regex reads.

**Evidence — a "perfect M1" clone.** I cloned the lane (`git clone --shared`, toplevel asserted),
edited every surface check 16/19/20 grade to the values the plan wants (heading "the five graded
forgeries", the eight boundary rows including (800 000, nd=1) and (520 000, nd=4), W14–W19 and
`overcharge` named in both the depth row and the §Round 97 body, S622 cited, depth-row sha256 /
line count / `## `-count refreshed), and committed. Then the **frozen** counters, run from the
lane against that clone:

```
=== round98-self-assessment-audit.py at the perfect-M1 clone ===
SELF_ASSESS98 checks=20 mismatches=1 met=False rev=700c6587… exit = 1

=== round98-depth-boundary-audit.py at the perfect-M1 clone ===
DEPTH_BOUNDARY98 rows=8 checks=12 mismatches=0 met=True rev=700c6587… exit = 0
```

**C3 goes green; C1 stays red.** An instrumented copy of C1 (per-check PASS/FAIL, the frozen file
untouched) shows the sole failing check is **n=16**. Term-by-term isolation of check 16's own
expression shows **12 of 13 terms true** and exactly one false:

```
WORDS[doc word] == len(new_cells)   False   two -> 2 vs 6
```

The failing term's inputs are `rdoc` and `new_cells` — **both parsed from
`tools/round98-router-budget.py`**, the counter C2 freezes. SKILL.md and SCORECARD.md edits
cannot change it. And the frozen counter's own docstring line 14 is *true as written* ("round 98
adds two cells" past round 97's four) — the defect is in the regex's choice of sentence, not in
the prose. Rewriting the prose to "adds six cells" would make it false.

**Two remedies, both proven, both touching a frozen counter** (so K1 as written must be
re-scoped, or the freeze amended — the freeze commit `34ad44e9` is still the tip of `master` and
`measured/` is empty, so it is amendable):

| remedy | change | result |
|---|---|---|
| **A** (counter regex) | `round98-self-assessment-audit.py:305` → `re.search(r"new set = (\w+) cells", rdoc)` | perfect-M1 → `mismatches=0 met=True` exit 0; **base control receipt byte-identical** to the committed `controls/c1-base.out` (`mismatches=4`, exit 1) |
| **B** (budget docstring) | `round98-router-budget.py:14` → "adds six cells" | perfect-M1 → `mismatches=0 met=True` exit 0; but the sentence becomes **false on its face** |

Remedy **A** is the honest one: it makes the counter read the number the sentence actually
asserts about the new set, leaves every other byte and every committed control receipt intact,
and is confined to C1's own counter. (The seat `RV01SelfAssess` filed the same term as **F6 —
LOW**, "check 16 forces one reading of an ambiguous sentence"; my measurement upgrades the
*consequence*, not the diagnosis: with the surfaces otherwise perfect the predicate is still
unreachable, so this is a **blocking** defect for C1, not a wording nit.)

**Do-nothing control is honest.** `controls/c1-base.out` says `mismatches=4` at base; I reproduced
`mismatches=4` at base with the frozen counter, and the per-check split at base is checks
**15, 16, 19, 20** — exactly the four the plan names. C1's control is not vacuous.

---

## 3. Two more findings, both proven by construction

### 3a. C1 check 18 does not reject the `+1/header` probe — its docstring says it does

`tools/round98-self-assessment-audit.py:47-49` claims:

> `a flat-6, 6+nd or +1/header parser fails the set equality.`

I reproduced check 18's own expression verbatim and ran it against the probe bytes after each of
the counter's own five `apply_mutant` patches:

```
mutant         check18_ok  mismatches_c1_18  charged
none           True        False             skip(u64()) | nd = u32() | ne = [u64() ...] | tt, off = u32(), u64()
flat6          False       True              skip(u64()) | nd = u32() | _b = rd(8 * nd) | tt, off = u32(), u64()
undercharge    True        False             (unchanged)
maxmeta        True        False             (unchanged)
nopreamble     True        False             (unchanged)
overcharge     True        False             (unchanged)
```

**Only `flat6` fails the set equality.** The `+1/header` mutant inserts `steps[0] += 1` on its own
line *inside* the loop, and `charge_line` (`:331-333`) keys on `need(`, `rd(`, `u64()`, `u32()`,
`skip(` — none of which appear in `steps[0] += 1`, so the inserted line is invisible to the
check. The docstring's claim is **false** for the very forgery the round is about.

Consequence, end-to-end: I took the perfect-M1 clone, installed the `+1/header` mutant in the
**probe** (a clone-only byte patch; the lane file untouched) and ran the **frozen** counters:

```
=== round98-self-assessment-audit.py at the perfect-M1 + OVERCHARGING-PROBE clone ===
SELF_ASSESS98 checks=20 mismatches=0 met=True rev=059801a1… exit = 0

=== round98-depth-boundary-audit.py at the perfect-M1 + OVERCHARGING-PROBE clone ===
DEPTH_BOUNDARY98 rows=8 checks=12 mismatches=0 met=True rev=059801a1… exit = 0
```

**Both green on a probe whose true nd=1 ceiling is 714 285, not the documented 833 332.** So the
round-97 defect RV03 F5 — "a false self-assessment still passes" — is *not* closed by C1 or C3 at
round 98; only C2's W18/W19 cells close it behaviourally. C3's rows are recomputed from the
probe's `MAX_STEPS` (`round98-depth-boundary-audit.py:69-73,103`) but the *charge model*
`4 + T x (5+nd)` is a **literal in the counter** (`:35`, `:103`), never compared against the
parser's actual charges — the same weakness RV03 named. C1 check 18 was the surface that was
supposed to bind the formula to the code, and it does not.

**Smallest remediation (tested).** Add one term to C3: the tensor loop must contain no direct
`steps[0] +=` increment (the per-header charge must come only from the counted read sites). With
that one guard added to a clone, the honest probe stays green (`rows=8 checks=13 mismatches=0
met=True`, exit 0) and the overcharging probe turns **red** (`rows=8 checks=13 mismatches=1
met=False`, exit 1). The base control's *verdict* is unchanged (`rows=6 mismatches=4 met=False`,
exit 1) but its `checks=` field moves 12→13, so the committed `controls/c3-base.out` line would
need re-issuing. The equivalent one-liner on the C1 side (reject a `steps[0] +=` inside the
tensor loop) closes the same hole at the calibration surface.

### 3b. The plan's +1 window is off by one at the lower edge

Measured above: the window opens at **T = 714 286 (nd=1)** and **T = 500 000 (nd=4)** — both
flip there. The plan writes `714,286 < T ≤ 833,332` and `500,000 < T ≤ 555,555`
(`plans/round-98-claims.md:99`), i.e. it excludes the two values that are the *first* to flip.
Correct: `714,286 ≤ T ≤ 833,332` and `500,000 ≤ T ≤ 555,555`. The same off-by-one appears in
this wave's own reports — `.ufo/waves/round-98/w1/CN01Overlap.md:130`,
`CR01Boundary.md:39-40`, `EX02BudgetControl.md:125`, `RV02BudgetCells.md:153`,
`RV03Intent.md:71-72` — so it will be copied forward if the plan text is taken as the source.
(`corpus/lessons/round-98.md` does NOT state the bounds — it names the window but not its edges.)
Severity MEDIUM (calibration): the bound is a published decision rule
for "does this file decide under a `+1/header` probe", it is wrong at exactly the edge a reader
would query, and it is cheap to fix. It does **not** move either new cell, so no claim is
falsified and no kill rule fires.

---

## 4. C2 operability and the control receipts — honest

The two freeze-time control receipts are honest and reproduce.

- `controls/c2-new-mutants.out` (50 lines) names each mutant with `--expect-cell` and the cell
  that reddens: `flat6`→W15-700k-nd4, `undercharge`→W14-900k-nd1, `maxmeta`→W16-maxmeta,
  `nopreamble`→W17-833333-nd1, `overcharge`→W18-800k-nd1 **and** W19-520k-nd4. Each row reads
  `cell_ok=0 caught=1` with `probe_sha256=` and `rev=681c80a4…` — bound to a concrete probe
  revision, not a bare claim. `mutant=none` → `survived=1` on the six new cells with the honest
  probe (the control's own green case).
- `controls/c2-legacy-mutants.out` (19 lines): `cells=17 cells_ok=17 mutant=overcharge …
  survived=1 caught=0` — the 17 round-97 cells all survive the `+1/header` probe, exactly the
  do-nothing control the plan promises. **The count is 17**, so the M2 defect (a dropped
  `W01-slow-x1` giving `cells=16`) is repaired.
- `controls/c1-base.out` `mismatches=4` at base and `controls/c3-base.out` `rows=6 checks=12
  mismatches=4` at base both reproduce under the frozen counters, and the C1 per-check split at
  base is checks 15/16/19/20 — the four the plan names.

My own end-to-end runs on the two new cells' fixtures under the `+1/header` probe show the
verdict pair the cells depend on, measured end-to-end through the probe:

| fixture | real probe | `+1/header` probe |
|---|---|---|
| `t800k_nd1` (W18) | `MODEL_UNLOADED` / `router-model-invalid` | `MODEL_OK` / `router-unloaded-autoload` |
| `t520k_nd4` (W19) | `MODEL_UNLOADED` / `router-model-invalid` | `MODEL_OK` / `router-unloaded-autoload` |

— the flip is real, and it is the flip that turns the cell red.

**C2's cells are correctly sized.** The two new cells sit strictly inside the measured window
with 200 000 (nd=1) and 120 000 (nd=4) tensors of slack below the `+1` ceiling, and their real
parse completes with 199 996 / 319 996 steps of slack below `MAX_STEPS`. A `+2/header` probe
also lands past the budget (measured mutant thresholds 5 600 004 and 5 200 004 for `+1`; `+2`
gives 6 400 004 / 5 720 004), so the ≥+1 class holds.

**One disclosed limit is worth stating more plainly.** C2 disclosed limit (f) says "W18/W19 …
do not pin the budget's lower bound (**W11 does**, in the same run)". My measurements show
**W11 does not**: `W11-700k` (700 000, nd=1) costs 4 200 004 steps real and 4 900 004 under
`+1/header` — both under `MAX_STEPS`, so both verdicts are `invalid` and the cell stays green
under the overcharge probe. The `+1` window's lower edge at nd=1 is T = 714 286; 700 000 is
below it, so W11 is outside the window entirely. The cell that pins the lower bound is
**W14-900k-nd1** (`5 400 004 > MAX_STEPS` real; an undercharging probe decides `invalid` → red,
as `controls/c2-new-mutants.out` itself shows with `expect_cell=W14-900k-nd1 cell_ok=0 caught=1`).
This is a **disclosure-accuracy** defect in the plan's parenthetical (f)
(`plans/round-98-claims.md:121-122`), MEDIUM severity on calibration: it names the wrong sentinel
in a sentence a reader will use to reason about which cell catches which forgery. It does not
falsify C2 — the cells and the receipts are correct. (Sibling seat `CR02Wording` reached the same
conclusion by the arithmetic route — `CN01Overlap.md:116-121` — so this is a **confirmed**
disclosure defect, not a solo reading.)

---

## 5. What I could not settle / disclosed limits

- I did not run the frozen C2 counter end-to-end (its full 19-cell pass needs 72 slow files and
  minutes of CPU); the C2 evidence above is from **my** fixtures and **my** stub through the
  **real** probe, plus the committed receipts, which I read and reproduced where cheap. The
  counter's own cell verdicts are its own claim; mine independently confirm the geometry.
- The mutants' byte application used the frozen counter's own `apply_mutant`, so the probe bytes
  under test are exactly the ones the receipts were produced with.
- `MAX_TENSORS` and the size guard were exercised with deliberately-built fixtures (1 200 000
  headers; a truncated 800k header) rather than by mutating the probe — the guards are in the
  probe's parser, and the measurement shows each guard's decision point unambiguously.
- I did not touch the live lane services, the registry, or any tracked lane file. The lane repo
  is byte-identical to `34ad44e9` except for this seat's out-dir receipt and this report.

## 6. Tools

No tools installed or upgraded. Everything ran on the host's `python3` (3.14.8), `git`, `curl`
(8.23.0), `ss` and `flock`, all pre-existing. No `pacman`, no `uv tool install`, no downloads.

## 7. Recommendations, smallest first

1. **Unblock C1** — amend the freeze commit (still the `master` tip; `measured/` is empty) to
   change `round98-self-assessment-audit.py:305` to `re.search(r"new set = (\w+) cells", rdoc)`.
   Proven: perfect-M1 goes green, the committed base control receipt stays byte-identical. State
   in the plan that K1 binds the *amended* freeze commit.
2. **Close the C3/C1 hole on the `+1/header` probe** — add the "no `steps[0] +=` inside the
   tensor loop" term to C3 (and/or C1 check 18). Proven: honest probe green, overcharging probe
   red. Re-issue `controls/c3-base.out` with the new `checks=` count.
3. **Fix the two off-by-one window bounds** — `plans/round-98-claims.md:99` and the three
   surfaces that copy it: the window opens at 714 286 (nd=1) and 500 000 (nd=4) *inclusive*.
4. **Correct disclosed limit (f)** — W11 does not pin the lower bound; W14 does.
5. **Re-verify C3's charge model against the parser** rather than against the literal
   `4 + T x (5+nd)`; my measured thresholds are the ground truth to compare against.

## 8. Lane hygiene

- Lane repo: no tracked file modified. `git status --porcelain` shows only the untracked
  `.ufo/waves/round-98/w1/` wave tree (pre-existing) plus this seat's out-dir receipt.
- All clones/fixtures lived under `/fast/scratch/hyaku/kama-r98/SN01StepFlips/` and were deleted
  before this report was written. Every clone asserted
  `git rev-parse --show-toplevel` equals the clone dir before any commit.
- No `git add/commit/stash/checkout/switch/reset/pull/push` and no mutating `jj` command was run
  against the lane repo; the only `git commit` calls were inside my scratch clones.
