# SN01StepFlips — round 97 (kama) wave-1 findings

Seat: `SN01StepFlips` (sentinel). Lane: `kama-shokunin`.
Scope: measure the real probe's step boundary **without the counters**, then attack C3's
boundary table and C2's cell sizing with the result.

Scratch: `/fast/scratch/hyaku/kama-r97/SN01StepFlips/` (deleted before yield).
No tracked lane file was edited. No `git add/commit/stash/checkout/switch/reset/pull/push`
was run against the lane repo; the fixture repos below are separate `git init` trees under
the scratch dir (each asserted `git rev-parse --show-toplevel` == its own path before any
commit).

**Lane HEAD moved under this seat.** The lane was at `9e605d41` (the round-97 freeze) when
I started; it is now `e057166e` ("round-97 amendment 1: C2 host-speed slow-files 72").
That amendment touches only `.ufo/waves/round-97/{controls,measured}/c2.out`,
`.ufo/waves/round-97/w1.ready*` and a new `plans/round-97-amendment-1.md` — **not** the
probe, `SKILL.md`, or any counter. `tools/kama-probe.sh` is byte-identical at both commits
(sha256 `0897ebff…`), and `tools/round97-router-budget.py` is byte-identical at both
(sha256 `24e2fad7…`), so kill rule K1 is untouched and **every finding below was
re-confirmed against the new HEAD** (F1–F4 re-verified; C3 and C1 counters re-run green
at `e057166e`).

**Tooling:** none installed. `python3` 3.14.8 (system), `git` (system) — both pre-existing.
No pacman, no `uv tool install`, no release binary, no `cargo install`, no `npx`.

---

## 0. Method

The probe under test is the **tracked bytes at `HEAD` (`9e605d41`)**, read with
`git show HEAD:tools/kama-probe.sh` — never a working-tree copy.

Three independent measurement paths were used, so no conclusion rests on one harness:

1. **End-to-end.** `bash kama-probe.sh check --port P --expect good --timeout 5
   --connect-timeout 2 --json` against a lane-style stub router (`/v1/models` listing with
   `status.args = [file, "-m", path]`, `/props` = `{"role":"router","models_autoload":true}`),
   exactly the pattern `tools/round97-router-budget.py` uses (`Runner.check`, `Stub`,
   `router_body`). Verdict/reason read from `rows[0]`.
2. **Parser-level.** `ROUTER_PY` extracted from the probe bytes and executed standalone
   against each fixture, with a scratch-only instrumentation patch that names the guard
   that raised (`steps:N` / `meta:N` / `size:N` / `ok:steps=N`).
3. **Mutant.** The same three paths re-run against byte-patched probes.

**Fixture families.** Two byte-layout-independent families per `(T, nd)`, so a verdict
cannot depend on one byte trick:

* `famA` — counter-identical layout: sequential 32-aligned offsets, **no data section**
  (the `invalid` verdict comes from `start + off + nbytes > size`).
* `famB` — a real data section with tensor 0's declared offset broken by 64 bytes
  (the `invalid` verdict comes from `off != expect`); the file is large enough that the
  size guard `n_kv*13 + n_tensors*24 > size` can never fire.
* `famC` (mutant study only) — **well-formed**: correct offsets *and* a real data section,
  i.e. a file the loader accepts.

**Fixture–counter byte identity.** The counter's own builder was imported and compared:
`rb.gguf(rb.BIG_TENSORS, 1, False)` (900 000), `rb.gguf(rb.MID_TENSORS, 1, False, nd=4)`
(700 000 @ nd=4) and `rb.gguf(rb.EDGE_TENSORS, 1, False)` (833 333) are **byte-identical**
to my independently written `famA` files (sha256 `0e0a51cf…`, `868d489b…`, `90d60f50…`).
The measurement is therefore on exactly the bytes C2 grades.

---

## 1. Fixture table — the six claimed boundary classes

Claim under test: `plans/round-97-claims.md` §C3, rows
(833 332, nd=1) `invalid`, (833 333, nd=1) `-`, (900 000, nd=1) `-`,
(700 000, nd=4) `-`, (555 555, nd=4) `invalid`, (555 556, nd=4) `-`.

### 1a. End-to-end verdicts (`check --json` through the stub router)

| T | nd | fam | bytes | verdict | reason | wall (s) | claim | match |
|---|---|---|---|---|---|---|---|---|
| 833 332 | 1 | A | 33 333 328 | `MODEL_UNLOADED` | `router-model-invalid` | 2.76 | `MODEL_UNLOADED`/`router-model-invalid` | ✅ |
| 833 332 | 1 | B | 59 999 936 | `MODEL_UNLOADED` | `router-model-invalid` | 2.46 | same | ✅ |
| 833 333 | 1 | A | 33 333 360 | `MODEL_OK` | `router-unloaded-autoload` | 2.71 | `MODEL_OK`/`router-unloaded-autoload` | ✅ |
| 833 333 | 1 | B | 60 000 000 | `MODEL_OK` | `router-unloaded-autoload` | 2.63 | same | ✅ |
| 900 000 | 1 | A | 36 000 048 | `MODEL_OK` | `router-unloaded-autoload` | 2.59 | same | ✅ |
| 900 000 | 1 | B | 64 800 032 | `MODEL_OK` | `router-unloaded-autoload` | 2.40 | same | ✅ |
| 700 000 | 4 | A | 44 800 048 | `MODEL_OK` | `router-unloaded-autoload` | 2.44 | same | ✅ |
| 700 000 | 4 | B | 67 200 032 | `MODEL_OK` | `router-unloaded-autoload` | 2.26 | same | ✅ |
| 555 555 | 4 | A | 35 555 568 | `MODEL_UNLOADED` | `router-model-invalid` | 2.25 | `MODEL_UNLOADED`/`router-model-invalid` | ✅ |
| 555 555 | 4 | B | 53 333 312 | `MODEL_UNLOADED` | `router-model-invalid` | 2.33 | same | ✅ |
| 555 556 | 4 | A | 35 555 632 | `MODEL_OK` | `router-unloaded-autoload` | 2.21 | same | ✅ |
| 555 556 | 4 | B | 53 333 408 | `MODEL_OK` | `router-unloaded-autoload` | 2.36 | same | ✅ |

**12 / 12 match the claim.** The `-`/`invalid` split is exactly as C3 states, and the
split is identical across two byte-layout-independent families — so it is not a fixture
artifact.

### 1b. Which guard decided each case (parser-level trace)

| T | nd | fam | steps `4 + T·(5+nd)` | probe state | deciding guard | parse (s) |
|---|---|---|---|---|---|---|
| 833 332 | 1 | A | 4 999 996 | `invalid` | offset/data check (decided) | 2.16 |
| 833 332 | 1 | B | 4 999 996 | `invalid` | offset chain `off != expect` (decided) | 2.29 |
| 833 333 | 1 | A | 5 000 002 | `-:steps:5000001` | **step budget** | 2.20 |
| 833 333 | 1 | B | 5 000 002 | `-:steps:5000001` | **step budget** | 2.34 |
| 900 000 | 1 | A | 5 400 004 | `-:steps:5000001` | **step budget** | 2.51 |
| 900 000 | 1 | B | 5 400 004 | `-:steps:5000001` | **step budget** | 2.34 |
| 700 000 | 4 | A | 6 300 004 | `-:steps:5000001` | **step budget** | 2.72 |
| 700 000 | 4 | B | 6 300 004 | `-:steps:5000001` | **step budget** | 2.59 |
| 555 555 | 4 | A | 4 999 999 | `invalid` | offset/data check (decided) | 2.72 |
| 555 555 | 4 | B | 4 999 999 | `invalid` | offset chain (decided) | 2.62 |
| 555 556 | 4 | A | 5 000 008 | `-:steps:5000001` | **step budget** | 2.45 |
| 555 556 | 4 | B | 5 000 008 | `-:steps:5000001` | **step budget** | 2.47 |

### 1c. Do the `-` fixtures decide by the size guard or MAX_TENSORS first?

**No — the step budget decides all four `-` cases, and it fires first.**

* **Size guard** (`n_kv*13 + n_tensors*24 > size`): for every `-` fixture the file is large
  enough that it does not fire (`size_guard=False` for all six shapes; e.g. 833 333 needs
  19 999 992 bytes and the file is 33 333 360). Proved by truncation: shaving the same
  declared tensor count below the threshold flips the verdict to `invalid-SIZE-GUARD`,
  while the untruncated file stays `-`. So the guard is *reachable* but *not* what fires
  for the claimed fixtures.
* **MAX_TENSORS** (1 000 000): all six `T` values are below it (900 000 is the largest), so
  it cannot fire. Proved by construction: at `T = 1 000 001` the probe returns
  `-MAX_TENSORS(n=1000001)` in 0.00 s — a *different* and much cheaper `-`. The 900 000
  cell sits below that cliff, which is what makes W14 a step-budget cell rather than a
  MAX_TENSORS cell. Worth stating explicitly: **900 000 is 90 % of the MAX_TENSORS cliff**,
  so the W14 discriminator has only 100 001 tensors of headroom.

### 1d. The probe's own step counter confirms the formula

Instrumented `ok:steps=` output from the probe itself:

* `T = 833 332, nd = 1` → `ok:steps=4999996` (claim: 4 999 996) — **exact match**.
* `T = 555 555, nd = 4` → `ok:steps=4999999` (claim: 4 999 999) — **exact match**.

The `5 + nd` per header and 4 preamble steps are the probe's *actual* accounting, not a
restatement.

### 1e. Contrast row (SKILL.md prose, round-96 §)

`T = 700 000` at nd = 1, 2, 3, 4, measured: `invalid` (4 200 004), `invalid` (4 900 004),
`-` (5 600 004), `-` (6 300 004). SKILL.md's "that file now decides `invalid` at `nd ≤ 2`
and stays `-` at `nd ≥ 3`" is **confirmed**.

---

## 2. Falsification verdict on the six rows

**The `-`/`invalid` split of C3 is CORRECT.** All six rows reproduce, on two independent
fixture families, end-to-end through the real probe's `check --json`, and the deciding
guard is the step budget in every `-` case (not the size guard, not MAX_TENSORS). The
probe's own step counter matches the table's stated step counts to the digit.

**But the table's verdict column is only conditionally true, and the counters cannot see
why.** See F1 below — this is where the round's depth claim breaks.

---

## 3. Findings

### F1 — HIGH — C3's table states `invalid` where the probe says `ok`; the counter cannot grade this

**Evidence.** The probe's `gguf_state` has **four** outcomes, not three:
`"missing"`, `"-"` (undecidable), `"invalid"`, **`"ok"`** (`tools/kama-probe.sh:768`
`return "ok"`). The C3 counter's `ROW` regex accepts only two verdict tokens:

```
tools/round97-depth-boundary-audit.py:39-41
r"\s*(<=|>)\s*budget\s*|"
r"\s*(invalid|-)\s*\|\s*$")      # <- 'ok' is not in the vocabulary
```

So the table's within-budget rows are graded `invalid`, but the probe returns `ok` for a
**well-formed** file of exactly that shape. Measured with the real probe on `famC`
(correct offsets + real data section):

| T | nd | table verdict | probe state | steps (probe's own counter) |
|---|---|---|---|---|
| 833 332 | 1 | `invalid` | **`ok:steps=4999996`** | 4 999 996 — the table's own number |
| 555 555 | 4 | `invalid` | **`ok:steps=4999999`** | 4 999 999 — the table's own number |

At the router level the well-formed files of the same two shapes grade
`MODEL_OK / router-unloaded-autoload` — i.e. **loadable**, not `router-model-invalid`:

```
WELLFORMED T=833332 nd=1 router_verdict=MODEL_OK/router-unloaded-autoload wall=2.34s
WELLFORMED T=555555 nd=4 router_verdict=MODEL_OK/router-unloaded-autoload wall=2.37s
```

**The step count is right and the verdict is wrong for a class of real files.** The table
answers "does the budget bind?" correctly, but the *verdict* column asserts `invalid`
unconditionally for the two within-budget rows, when the probe's answer there is
`ok` for a well-formed file and `invalid` only for a malformed one. SKILL.md's prose
("`MAX_STEPS = 5,000,000` decides it (`invalid`) when that sum fits") states the same
over-generalisation: the budget decides *whether the file is decided*, not *what* it is
decided to be.

**Why this matters for the round, not just for the table.** This is the round-96 closure
defect recurring in a new shape. Round 96's C3 counter was green on a false sentence
because check 1 *required* the literal string `"6 steps per tensor header"`
(`plans/round-97-claims.md:35-37`). Round 97's C3 counter is green on a false verdict
because `ROW`'s regex *requires* the literal token `invalid` and there is no `ok` in its
vocabulary. **The counter cannot express the truth**, so it cannot grade it.

**The counter's own oracle carries the same wrong model.** `tools/round97-router-budget.py`
`fixture_class()` decides a fixture's designed class from its bytes and hardcodes:

```python
    steps = 4 + n_tensors * (5 + nd)
    if steps > 5_000_000:  # undecidable -> loadable
        return "-"
    return "ok" if n_tensors <= 2 else "invalid"
```

Run against the **well-formed** 833 332-tensor file:

```
counter's fixture_class(WELL-FORMED T=833332 nd=1) = 'invalid'   (probe says 'ok')
counter's fixture_class(WELL-FORMED T=555555 nd=4) = 'invalid'   (probe says 'ok')
```

The oracle says `invalid` where the probe says `ok`. C2's cells are all malformed
fixtures, so the oracle is never wrong *there* — but the oracle is the same model, and
the model is wrong in general.

**Smallest remediation** (lane-side, one of):
* (a) Change the table's two within-budget verdicts from `invalid` to a wording that
  names the *decision*, not the verdict — e.g. `decided` / `invalid-or-ok` — and widen
  `ROW`'s verdict group to accept it. This is one SKILL.md line and one regex.
* (b) Keep `invalid` and add a column naming the file class the row is about (e.g.
  "malformed fixture"), so the row is true as written.
* (c) If `invalid` is intended to describe the counter's own fixtures only, say so in
  SKILL.md's prose and in the counter's docstring.

Under (a) or (b) the C3 counter must be re-frozen — which is a kill-rule-K1 event
(`the counter's bytes change after the freeze commit`), so this is a *next-round* fix, not
a round-97 edit. **This round cannot fix it without voiding K1.**

**Scope note.** The task brief asks whether "every row recomputes from the probe's
`MAX_STEPS`". It does — the *step arithmetic* recomputes exactly, and mutation D (a row's
stated step count changed 4 999 996 → 4 999 995) is correctly caught
(`DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=1 met=False`, rc=1). The recomputation is
sound. What does not recompute is the **verdict**, and the counter's regex makes the
correct verdict unrepresentable. Same defect class as round 96, one level down.

### F2 — HIGH — C3 grades the *formula*, not the probe: a probe charging `6 + nd` per header keeps every counter green while the table is false

`tools/round97-depth-boundary-audit.py` never runs the probe. It reads the probe only to
extract `MAX_STEPS`:

```python
tools/round97-depth-boundary-audit.py:69-73
m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
...
tools/round97-depth-boundary-audit.py:103
want_steps = PREAMBLE + t * (5 + nd)     # PREAMBLE = 4, hardcoded at line 35
```

`PREAMBLE = 4` and the `5 + nd` per-header term are **hardcoded in the counter**, not
derived from the probe's bytes. So the counter recomputes the table from the formula, not
from the probe — and a probe that charges a different amount still passes.

**Mutation B** (probe bytes patched to charge one extra step per tensor header —
`need(1)` inserted after `skip(u64())  # name`, anchor count = 1). Real probe, real
fixtures:

| T | nd | honest | +1 per header |
|---|---|---|---|
| 833 332 | 1 | `invalid` | **`-`** ← table says `invalid`, probe now says `-` |
| 555 555 | 4 | `invalid` | **`-`** ← table says `invalid`, probe now says `-` |

Both within-budget rows of the table are now **false**. Yet:

```
C3 vs +1-per-header probe:  DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True   rc=0
C1 vs +1-per-header probe:  SELF_ASSESS97 checks=14 mismatches=0 met=True             rc=0
```

**Mutation C** (preamble 4 → 5, `need(1)` inserted before the magic read) — same result,
both counters green:

```
C3 vs preamble+1 probe:     DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True   rc=0
C1 vs preamble+1 probe:     SELF_ASSESS97 checks=14 mismatches=0 met=True             rc=0
```

Under mutation C the probe's own counter reads `ok:steps=4999997` for the 833 332 row,
while the table still states 4 999 996 — the table's *arithmetic* is now false and the
counter does not notice, because it computed 4 999 996 from its own hardcoded constants.

**Impact.** C1's check 7-9 grade the probe's *comment text* (`"5 + nd"` present,
`"6 steps per tensor header"` absent, the four ceilings present) — a **string** check, not
a behaviour check. C2's four new cells catch four *named* mutants; a `+1`-per-header
mutant is not one of them, and I confirmed it **survives all four new cells** with the
real counter:

```
ROUTER_BUDGET97_CONTROL cells=4 cells_ok=4 mutant=none expect=survived survived=1 caught=0
    probe=override probe_sha256=b9d5ee8f… rev=e057166e…
```

So the whole three-counter suite is blind to a probe whose *actual* step accounting
disagrees with the table — and the round-97 correction is *precisely* about the probe's
actual step accounting.

**The `+1`-per-header mutant survives all 17 cells, not just the four new ones.** Run
against the real counter with the mutant probe installed via `--probe-file`:

```
# new cells (W14-W17)
ROUTER_BUDGET97_CONTROL cells=4 cells_ok=4 mutant=none expect=survived survived=1 caught=0
    probe=override probe_sha256=b9d5ee8f… rev=e057166e…  ok=1

# legacy cells (W01-W13), every one ok=1
ROUTER_BUDGET97_CELL nat W01-slow-x1 ok=1 … W02-slow-x8 ok=1 … W03-slow-x40 ok=1 …
    W04-ok-x8 ok=1 … W05-slow-then-ok ok=1 … W06-missing-x8 ok=1 … W07-fast-k40 ok=1 …
    W08-hardlink-x8 ok=1 … W09-undecided-big ok=1 … W11-700k ok=1 … W12-strings ok=1 …
    W13-budget-kill ok=1 … W10-rewrite ok=1
ROUTER_BUDGET97_CONTROL cells=13 cells_ok=13 mutant=none expect=survived survived=1 caught=0
    probe=override probe_sha256=b9d5ee8f… rev=e057166e…  ok=1
```

So this mutant passes C2's entire 17-cell set, passes C1's 14 checks and passes C3's
8 checks, while making two of C3's six table rows false. It is the single most effective
attack found in this wave.

**Smallest remediation.** C3's counter should derive the per-header and preamble costs
from the probe's bytes (parse the `need()`/`u64()` call sites in the header loop) rather
than hardcode `PREAMBLE = 4` and `5 + nd`, and C1's check 7 should compare the probe's
*comment* against that derived value rather than against the literal string `"5 + nd"`.
Alternatively, C2 should gain a fifth graded mutant — `plus1` — whose patch anchor is
already unique in the probe bytes, so a per-header mischarge is caught by W14/W15/W17.

### F3 — MEDIUM — C2's new cells are sized *past* the forgeries they claim, but one forgery class (per-header mischarge) slips through all four

C2's four new cells do catch the three named mutants (frozen receipt
`controls/c2-new-mutants.out`: `flat6` caught at W15, `maxmeta` at W16, `undercharge` and
`nopreamble` at W14/W17). Independently confirmed: W15 is the only cell that flips under
`flat6`, because `700 000 × nd=4` is the only new shape where a rank-blind 6-vs-`5+nd`
price crosses `MAX_STEPS`. The cells are correctly sized for the named classes.

**But** a probe that charges `6 + nd` per header (mutation B above) — a per-header
mischarge, i.e. *not* one of the four named classes but a natural neighbour of `flat6` —
survives **all 17 cells**: the four new ones (`cells=4 cells_ok=4 survived=1`) *and* all
thirteen legacy ones (`cells=13 cells_ok=13 survived=1`), both quoted verbatim in F2. It
also leaves C1 and C3 green (F2). The plan's disclosed limit (a) says "a probe that
charges a wrong number of steps inside a single header (not preamble, header, dims, or
cap) is not graded" — the `+1`-per-header mutant charges a wrong number of steps **at the
header**, so it is arguably inside the disclosed "not graded" carve-out rather than an
undisclosed hole. Still worth the lane's attention, because it is the mutation that
makes C3's own table false while every counter in the round stays green.

**Also note the headroom** (§1c): W14's 900 000 tensors sit 100 001 below the
`MAX_TENSORS = 1 000 000` cliff. A cell at `T ≥ 1 000 001` would grade `-` for a
completely different reason (`-MAX_TENSORS`, 0.00 s), so the W14 discriminator is
sensitive to `MAX_TENSORS` being lowered — which is exactly what the `maxmeta` mutant
family does to a *different* constant. Disclosed, but fragile.

### F4 — MEDIUM — `SKILL.md` §Round 97 says "three graded forgeries" and names "W14, W15 and W16"; the counter grades **four** mutants over **four** new cells (W14–W17)

`SKILL.md:2443` — the section heading reads:

```
### Round 97 correction (step-budget boundary table and the three graded forgeries; dated 2026-11-08)
```

`SKILL.md:2467` — the prose reads:

```
round-97 counter `tools/round97-router-budget.py` grades each with W14, W15 and W16
respectively.
```

But the counter has **four** new cells and **four** mutants:

```python
tools/round97-router-budget.py:146
NEW_CELLS = {"W14-900k-nd1", "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1"}
tools/round97-router-budget.py:163-176
MUTANTS = {"flat6": …, "undercharge": …, "maxmeta": …, "nopreamble": …}
```

`W17-833333-nd1` and the `nopreamble` mutant exist, are exercised, and are the reason
the frozen control receipt `controls/c2-new-mutants.out` has a fourth block
(`mutant=nopreamble … caught=1`). `SKILL.md` never mentions W17 or the preamble-drop
forgery. `plans/round-97-claims.md:83-91` correctly says "This round's **four** graded
mutants are … and a preamble-drop (`nopreamble`, this round's own shape)" and lists W17.

**This is exactly the class of defect C1 exists to close, and C1 does not catch it.**
Grepping the C1 counter for the forgery enumeration: **no check grades it**. C1's 14
checks cover the depth/adjacency digests, the capability pointer, the probe's comment
string, the five ceilings, the S620/S621 rows, the round-96 identity clause and two quoted
receipts — none of them looks at whether SKILL.md's description of the counter matches the
counter. A stale SKILL.md sentence about its own tooling passes C1 green.

**Impact.** The reader of `SKILL.md` believes the round-97 forgery coverage is three cells
(W14–W16) and does not know a fourth (W17) exists. Since the omitted forgery is the
preamble-drop — the one that pins the **4 preamble steps** in the very formula C3's table
is built on — the omission removes the reader's only evidence that the `4 +` term is
graded at all. This is a *calibration* defect (the lane's self-description disagrees with
the repo) and a *depth* one (the disclosure a reader relies on is incomplete).

**Smallest remediation.** Either (a) correct `SKILL.md:2443` and `SKILL.md:2467` to say
"four graded forgeries" and "W14, W15, W16 and W17" and add the `nopreamble` clause to
the prose — one sentence, no counter change, no kill-rule event; or (b) leave SKILL.md
alone and add a C1 check that the section's forgery/cell enumeration matches
`NEW_CELLS`/`MUTANTS` in the counter. (a) is cheaper; (b) is the durable fix and is
next-round (C1's bytes are frozen → K1).

### F5 — LOW — C2's predicate is host-speed-conditional; the lane caught this itself (amendment 1), but the guard is still host-bound

`tools/round97-router-budget.py` refuses the predicate unless the W03 natural pass costs
`≥ 1.25 × 60 s = 75 s`:

```
tools/round97-router-budget.py:157
MARGIN = 1.25         # the honest pass must exceed 1.25 x the base constant
```

The frozen control `controls/c2-could-not-evaluate.out` records the refusal:

```
ROUTER_BUDGET97 could-not-evaluate: W03 natural pass 55.0s < 1.25 x 60s — the round-94
constant wrapper would not truncate this listing on this host, so no discriminator is claimed
c2_exit=2
```

and the four W03 timings inside `controls/c2-legacy-mutants.out` (59.11 s, 53.62 s,
61.84 s, 70.95 s) are all below 75 s. **The lane found this itself** and recorded
`plans/round-97-amendment-1.md` (commit `e057166e`, "recorded before any C2 cell
scored"): the C2 predicate command gains the declared host-speed parameter
`--slow-files 72` (72 × ~1.37 s ≈ 99 s > 75 s). The counter's bytes are **unchanged**
(sha256 `24e2fad7…` at both `9e605d41` and `e057166e`), so kill rule K1 holds, and the
guard is not widened or bypassed — the cell count is sized so the discriminator exists.
That is a legitimate, well-disclosed repair and it is **not** a finding against the lane.

**My own independent confirmation of the host-speed dependence** (this seat, legacy cells,
`--burners 0`, real probe at `e057166e`):

```
ROUTER_BUDGET97 cells=13 mismatches=0 positive_mismatches=0 load_cells=13 load_stable=1
    budget=work probe=rev mutant=none
    probe_sha256=0897ebff… base_sha256=27065a5c… rev=e057166e…
    w03_seconds=214.6 load1_nat=87.28 burners=0
```

Note `load1_nat=87.28` — the host was heavily loaded (by this wave), and W03 then cost
214.6 s, comfortably over the 75 s guard. On an idle host the same cell costs ~55 s and
the predicate **exits 2 instead of scoring**. So the margin is satisfied or not depending
on ambient load, not on the lane's work. The remaining disclosure gap is small but real:
the plan's C2 "Disclosed limits" does not mention the margin or the host-speed
dependence (grep of `plans/round-97-claims.md` for `margin|1.25|host speed`: no hits),
and `plans/round-97-amendment-1.md` is a new file that the frozen plan's receipt list does
not mention. A reader working only from `plans/round-97-claims.md` would not know the
predicate command now carries `--slow-files 72`.

### F6 — INFO — the C3 base control and the C1 base control both reproduce exactly

Both frozen do-nothing controls were re-run against the lane repo at base `40763bd2`:

```
C3: DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False   rc=1
    (frozen controls/c3-base.out: "DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False" — identical)
C1: SELF_ASSESS97 checks=14 mismatches=9 met=False   rc=1
    (frozen controls/c1-base.out: "SELF_ASSESS97 checks=14 mismatches=9 met=False" — identical)
```

Both counters discriminate base from `HEAD` as the plan requires. The C3 base control
also shows the counter cannot be *reached* without the section (rows=0), so it is not a
vacuous green.

### F7 — INFO — the C3 counter does catch a wrong step count (it is not vacuous)

Mutation D (row 833 332's stated step count 4 999 996 → 4 999 995) in a scratch fixture
repo:

```
DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=1 met=False   rc=1
```

The arithmetic half of C3 is genuinely graded. Combined with F2, the counter's blind spot
is specifically the **verdict** and the **probe-behaviour link**, not the arithmetic.

---

## 4. What is falsified and what is not

| Claim | Verdict | Basis |
|---|---|---|
| **C3 step arithmetic** (`4 + T·(5+nd)`, the `<=`/`>` comparison, the six step counts) | **CONFIRMED** | 12/12 fixtures reproduce end-to-end; the probe's own step counter reads 4 999 996 and 4 999 999 exactly; mutation D caught |
| **C3 `-`/`invalid` split** | **CONFIRMED** for the counter's fixture class; **the verdict column is over-general** | two independent families agree; but a well-formed file of the same shape grades `ok`, and `ROW`'s regex has no `ok` |
| **C3 "every row recomputes from the probe's MAX_STEPS"** | **PARTIAL** — the arithmetic recomputes from `MAX_STEPS`, but `PREAMBLE=4` and `5+nd` are hardcoded, so a probe charging differently keeps the counter green (F2) | mutation B and C both leave C1+C3 green while the table is false |
| **C2 cell sizing for the four named mutants** | **CONFIRMED** | frozen receipt re-verified; flat6 caught only at W15, as the rank arithmetic predicts |
| **C2 catches a per-header mischarge** | **NOT GRADED** — a `+1`-per-header mutant survives **all 17** cells (F3) | real counter, new `cells_ok=4 survived=1`, legacy `cells_ok=13 survived=1` |
| **C2 predicate reachability** | **HOST-CONDITIONAL**, repaired by the lane's own amendment 1 (F5) | frozen `c2-could-not-evaluate.out` exit 2; my own run: W03 = 214.6 s at loadavg 87, ~55 s idle |
| **C1's 14 checks** | **REPRODUCE** (base mismatches=9, HEAD mismatches=0) but **do not grade SKILL.md's description of its own tooling** (F4) | grep: no check touches the forgery enumeration |

**No C3 row's real verdict differs from the claim for the counter's fixture class.**
C2's cell expectations are met on the real probe. The falsifications are of the
*counter's* coverage (F1, F2) and of *SKILL.md's* self-description (F4) — not of the
six-row table's numbers.

---

## 5. Recommended routing (lane-side, next round)

1. **F1 (HIGH).** The C3 table's `invalid` for the two within-budget rows is true only
   for malformed files. Either widen `ROW`'s verdict vocabulary and reword the rows
   (e.g. `decided`), or qualify the rows by file class. The C3 counter's
   `fixture_class()` oracle needs the same correction. **Counter bytes change → K1 →
   next round.**
2. **F2 (HIGH).** C3 must derive the preamble and per-header costs from the probe's
   bytes instead of hardcoding `PREAMBLE = 4` and `5 + nd`; C1 check 7 should compare the
   probe's comment against that derived value, not the literal `"5 + nd"`. Adding a
   `plus1` mutant to C2 (its anchor is already unique) is the cheaper half.
3. **F4 (MEDIUM).** Correct `SKILL.md:2443` and `SKILL.md:2467` — "three graded
   forgeries" → four, "W14, W15 and W16" → "W14, W15, W16 and W17" — and name the
   preamble-drop forgery in the prose. **No counter change; no K1 event.** Cheapest
   highest-value fix in this report.
4. **F5 (LOW).** Add the `1.25 × 60 s` margin and its host-speed dependence to C2's
   disclosed limits, and reference `plans/round-97-amendment-1.md` from the frozen plan's
   receipt list (the amendment is currently invisible to a reader of
   `plans/round-97-claims.md` alone).

**Note on scope.** F1, F2 and F4 are *not* repairable inside round 97 without voiding
kill rule K1 (the counters' bytes are frozen) — except F4, which is a `SKILL.md` edit
only and touches no counter. F1's remediation in particular requires re-freezing the C3
counter, so it is a next-round item by construction, and the round-97 claim should
acknowledge it as routed rather than closed.

---

## 6. Reproduction commands

```bash
L=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r97/SN01StepFlips

# fixture build (12 files, two families) + guard arithmetic
python3 "$S/mkfix.py" "$S/fix"

# end-to-end: real probe bytes + stub router -> check --json
python3 "$S/driver.py"                    # writes $S/results.json

# parser-level: which guard decided each case
python3 "$S/trace_parse.py"               # writes $S/trace/trace_results.json

# the size-guard vs step-budget question
python3 "$S/sizeguard.py"

# well-formed files of the same shapes (the 'ok' finding)
python3 "$S/wellformed.py"
python3 "$S/router_check_wf.py"

# mutants: +1 per header, preamble+1
python3 "$S/mutant_probe.py"
python3 "$S/mutants_empirical.py"

# C3 counter vs a probe charging 6+nd per header (fixture clone)
git clone --shared -q "$L" "$S/fixclone" && cd "$S/fixclone"
git checkout -q 9e605d416c199b3c9913a2125b04f9c5a16f5668
# apply +1-per-header patch to tools/kama-probe.sh, commit, then:
python3 tools/round97-depth-boundary-audit.py --repo . --rev HEAD   # -> met=True (blind)
python3 tools/round97-self-assessment-audit.py --repo . --rev HEAD   # -> met=True (blind)

# C3 counter vs a corrected verdict ('ok' instead of 'invalid')
#   in a scratch fixture repo with SKILL.md from HEAD:
#   -> DEPTH_BOUNDARY97 rows=4 checks=8 mismatches=2 met=False  (the counter rejects the truth)
```

Fixture repos used (all under the scratch dir, `git init` + `git rev-parse --show-toplevel`
asserted before each commit): `c3fix.ezkhnY` (C3 table mutations A and D),
`fixclone` (probe mutations B and C). Both removed with the scratch dir.

**Receipts copied into this report** (the out dir holds the markdown only; the JSON
evidence trees were under scratch and are summarised in §1 and §3 inline, quoted verbatim
from the real runs).
