# SN01VerdictBoundary — the decision boundary MAX_STEPS = 5 000 000 induces

Seat: SN01VerdictBoundary. Lane: `kama-shokunin`.
Scratch: `/fast/scratch/hyaku/kama-r96/SN01VerdictBoundary/` (deleted on exit).
No tracked lane file was edited; no mutating git command was run against the lane.

**Tip note.** The lane moved five times during this seat: `bbdfc930` (round-96 wave-1 start) →
`fb5cd3cd` + `4a0f6a35` (amendment 2, "wave-1 RV01 findings") → `b3289c18` (amendment 3) →
`20317286` (amendment 4) → `bb4a997a` (amendment 5). Amendments 2–4 repair several findings this
seat had already measured independently, and the report is split accordingly:
**Part A** records what was measured at `bbdfc930`; **Part B** re-measures at `b3289c18` and
carries forward through amendments 4 and 5 to the tip `bb4a997a`, reporting what remains live.
Every number below is measured, not inferred.

## Scope

Binary-search the largest decidable tensor count (where a file flips from `invalid` to `-`),
check the landed ceiling sentence and step-cost table against the measured flip, exercise a KV
string-array whose element count exceeds `MAX_STEPS` (the W12 shape), and exercise a file whose
tensor total costs exactly `MAX_STEPS`.

## Method

* The parser was read out of the **landed** probe bytes (`git show <rev>:tools/kama-probe.sh`),
  extracted as the `ROUTER_PY` heredoc and instrumented to record the highest step count any
  `need()` call observed. No parser logic was rewritten.
* Binary search over the tensor count on the *landed* `gguf_state()` — the state the probe
  actually computes, not a re-implementation.
* Every boundary claim was re-confirmed **end-to-end** through the real `bash kama-probe.sh`
  against a stub router (the frozen counter's own `Stub`/`Runner`), reading `rows[0].verdict`
  and `rows[0].reason` — the same channel C1 grades.

---

# Part A — measured at `bbdfc930` (wave-1 start)

## A1. The measured boundary

Fixed cost before the tensor loop: **4 steps** (`rd(4)` magic, `u32` version, `u64` n_tensors,
`u64` n_kv).

Per-tensor-header cost is **not a constant**. It is `5 + nd` steps:

| part of the header | steps |
|---|---|
| `skip(u64())` name (u64 read + skip) | 2 |
| `u32` nd | 1 |
| `u64` dims — **one per dimension** | `nd` |
| `u32` type + `u64` offset | 2 |

Measured (100 tensors, no KV): nd=0 → 504 steps, nd=1 → 604, nd=2 → 704, nd=3 → 804, nd=4 → 904.
That is `4 + 100·(5+nd)` exactly.

Binary-searched largest decidable tensor count (the file grades `invalid` — a decision was
reached — rather than `-`):

| nd | steps/header | largest decidable | at +1 |
|---|---|---|---|
| 1 | 6 | **833 332** (4 999 996 steps) | 833 333 → `-` (5 000 001 steps) |
| 2 | 7 | **714 285** (4 999 999 steps) | 714 286 → `-` |
| 3 | 8 | **624 999** (4 999 996 steps) | 625 000 → `-` |
| 4 | 9 | **555 555** (4 999 999 steps) | 555 556 → `-` |

The budget is spent at 5 000 000 steps **inclusive**: a parse whose last `need()` lands on
exactly 5 000 000 still decides; the next step (5 000 001) raises `Unknown()` → `-`.

## A2. W12 could not grade `MODEL_OK` — the blocking defect

The frozen counter's `gguf_strbig()` built a string array of 6 000 000 elements but wrote only
6 000 057 bytes: one length-prefixed string plus 6 M payload bytes. The parser's `skip_strings()`
checks the size **before** the step budget:

```python
if base + 8 * n > size:
    raise Bad()
```

`base` = 49, `8 × 6 000 000` = 48 000 049 > 6 000 057 → `Bad` → **`invalid`**, before a single
element step is charged. The file grades `invalid` (a decisive verdict), not `-` (undecidable →
loadable). Measured at both revisions:

| probe | counter's W12 bytes | correctly sized W12 (n elements, each with its own 8-byte prefix) |
|---|---|---|
| base `5d43528b` (4 M steps) | `invalid` | `-` |
| `bbdfc930` (5 M steps) | `invalid` | `-` |

So the W12 fixture did not exercise the step budget's far side at all. Running the frozen
counter at `bbdfc930`:

```
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload
    run1=MODEL_UNLOADED/router-model-invalid/0.18s run2=MODEL_UNLOADED/router-model-invalid/0.17s
```

Every other cell passed. The counter's `fixture_class()` oracle also returned `"-"` for this
fixture (`n_tensors == 0 and n_kv >= 1` → `-`), so oracle and probe disagreed here too — the
oracle wrong in the opposite direction from A4.

The base control `controls/c1-base.out` already showed `W12-strings ok=0`, but it is a
`--skip-load` run whose summary is structurally red (`mismatches=-2`) and short-circuits, so it
does not isolate the W12 failure.

## A3. The published step-cost table priced a fixed 6 steps per header

`SKILL.md:2431` and `tools/kama-probe.sh:575-581` both priced a header as

> name `u64`+skip 2: u64 1 + skip 1; `nd` `u32` 1; dims `u64` 1; type `u32` + offset `u64` 2 = 6

But the parser reads the dims as a **loop**, not one value:

```python
ne = [u64() for _ in range(nd)] or [1]
```

so the dims row costs `nd` steps. The published "6" is the `nd=1` case only; a 4-D header costs
9 steps, 50 % more. The published ceiling was therefore the ceiling for the cheapest header
shape only:

| header shape | published ceiling | actual |
|---|---|---|
| nd=1 | 833 333 | 833 332 |
| nd=2 | 833 333 | 714 285 |
| nd=3 | 833 333 | 624 999 |
| nd=4 | 833 333 | 555 555 |

## A4. The counter's fixture oracle disagreed with the landed probe at its own boundary

`fixture_class()` graded a fixture with `if n_tensors > 833_333: return "-"`. Measured against
the landed `gguf_state()`:

| n_tensors | oracle | landed probe | |
|---|---|---|---|
| 700 000 | `invalid` | `invalid` | agree |
| 833 332 | `invalid` | `invalid` | agree |
| **833 333** | **`invalid`** | **`-`** | **disagree** |
| 833 334 | `-` | `-` | agree |

The threshold is one too high: the oracle calls a file `invalid` that the probe calls `-`. This
is the same class of error the counter exists to prevent — an oracle that disagrees with the
probe. Latent only because no cell sits exactly on 833 333 (W11 uses 700 000).

## A5. The C3 disclosure audit's evidence-pointer check cannot detect the defect it names

The plan's C3 "Before" says the evidence pointer "cites evidence at `f6325660` (the first
revision) while the claim was filed at M1b `c810f51e` — a stale evidence pointer". But the check
only requires the cited commit to *resolve* and be an *ancestor* of the revision under audit.
`f6325660` resolves and is an ancestor of the base revision, so the check **passes on the very
defect it was written to catch**.

Per-check, base vs `bbdfc930`:

| check | base | tip | discriminates |
|---|---|---|---|
| c1 `MAX_STEPS` == 5 M and "6 steps per tensor header" present | FAIL | PASS | yes |
| c2 old `MAX_TENSORS = 1_000_000` + `the ceiling is 1,000,000` both present | FAIL | FAIL | **no** |
| c3 counter docstring formula | FAIL | PASS | yes |
| c4 capability evidence pointer resolves AND ancestor | PASS | PASS | **no** |
| c5 probe contains `20 + 25 * npaths` | PASS | PASS | **no** |

c2 is **inert**: the probe has never contained the literal `MAX_TENSORS = 1_000_000` — the
constant is written `MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, 1_000_000,
512 * 1024 ** 2` (`tools/kama-probe.sh:562`), so the substring never matches at any revision and
the check can never fire. Three of five checks were base-true; only c1 and c3 discriminated, and
c1's discriminator is the very string A3 shows is wrong.

## A6. The counter's W03 margin guard made the C1 predicate host-dependent

Running the frozen counter at `bbdfc930` on this host (`--burners 0`):

```
ROUTER_BUDGET96 could-not-evaluate: W03 natural pass 65.8s < 1.2 x 60s — the round-94 constant
wrapper would not truncate this listing on this host, so no discriminator is claimed
```

Exit code 2 — the predicate was not reached at all. The frozen counter's `MARGIN = 1.25` guard
demands the honest W03 pass cost ≥ 1.25 × 60 s; on this host 40 distinct 600 000-tensor files
cost 65.8 s, so the counter refuses to evaluate. The committed base control was measured on a
slower host (`w03_seconds=101.7`), where the guard is satisfied. The behaviour is disclosed in
the counter's own source ("the counter refuses to claim it unless..."), so it is not a claim
defect — but the C1 predicate's *reachability* is host-dependent, and on this host the counter
exits 2 rather than 0 or 1. (Amendment 3 later reclassified the file count as a host-speed
parameter and measured M1 with `--slow-files 96`; see B7.)

Two smaller items in the same counter, both non-load-bearing for the verdict:
* The counter's docstring says the guard is "1.5 x 60 s" (line 55) while the code is
  `MARGIN = 1.25` (line 98) and the refusal message prints "1.2 x 60s" — the docstring and the
  message disagree with the constant.
* `KILL = 1200` vs the probe's derived limit `20 + 25 × 40 = 1020` s: 1200 > 1020, as the plan
  states. Correct.

## A7. What was confirmed correct at `bbdfc930`

* **The 700 000-tensor file decides** — the C1 headline held. `W11-700k` graded
  `MODEL_UNLOADED/router-model-invalid` at the tip and `MODEL_OK/router-unloaded-autoload` at
  base: the discriminator works.
* **A file costing exactly `MAX_STEPS` decides.** 4 header steps + 4 KV steps (one `u64` key
  length, one `u32` value type, a 4-byte scalar skip) + 6 × 833 332 header steps = 5 000 000
  exactly → `invalid` / `MODEL_UNLOADED/router-model-invalid`. One tensor more would need
  5 000 006 steps; the parse trips at the 5 000 001st `need()` → `-` /
  `MODEL_OK/router-unloaded-autoload`. The boundary is inclusive at 5 000 000 and sharp.
* **The 6-step figure is exactly right for `nd=1`**, and `nd=1` is what the counter's fixture
  builder emits (`struct.pack("<IQIQ", 1, elems, 0, off)` — a literal 1 dimension). The counter's
  internal consistency was sound; its *reach* was not.
* The C2 and C3 audits both passed at the tip and both reddened at base.

---

# Part B — re-measured at the tip `b3289c18` (after amendments 2 and 3)

Amendment 2 (`plans/round-96-amendment-2.md`) cites wave-1 seat `RV01StepBudget`. Its F1/F2/F3
answers the same three defects this seat measured independently as A2/A3/A4, and its repairs
land in the tip. Amendment 3 (`plans/round-96-amendment-3.md`) then repaired a defect amendment 2
introduced in its own W12 fixture (its length prefixes were contiguous, not interleaved, so the
reader landed mid-prefix and graded the file `invalid`). Amendment 4 (`20317286`) then repaired
B3 below (the nd=3 row), and amendment 5 (`bb4a997a`) restated the predicates' identity clause.

Amendment 5's identity table pins **C1's counter to `b3289c18`** — the exact revision this seat
measured — and states the authoritative C1 predicate as
`--rev b3289c18 --work <private> --slow-files 96` printing `cells=12 mismatches=0
positive_mismatches=0 load_cells=12 load_stable=1`. This seat's run of that exact command
(§B1) is the same measurement.

**Tip note.** The lane moved five times during this seat (`bbdfc930` → `fb5cd3cd`/`4a0f6a35` →
`b3289c18` → `20317286` → `bb4a997a`). One counter run this seat launched at `4a0f6a35` was
killed after it had loaded a **stale** copy of the counter source (the file changed on disk 29 s
after the process started); its `W12-strings ok=0` line is a stale-source artifact, not a verdict
at the tip. Every W12 verdict below is from a fresh run against the tip's own bytes.

## B1. FIXED — W12 now grades `-` (A2)

Amendment 2's fixture wrote `8 * n` length prefixes followed by one contiguous 6 MB payload run;
the parser reads each element as `[u64 length][payload]`, so after element 0 it landed one byte
into the next length prefix, read a huge length, and the `base + off > size` guard graded the
file `invalid` — amendment 2's own repair was still red. Amendment 3 interleaves them
(`(pack("<Q", 1) + b"x") * n`, 9 bytes per element, 54 000 049 bytes total).

Verified at the tip, against the tip's own counter source and the tip's own probe bytes:

```
amendment-3 strbig size: 54000049 bytes
landed probe state: -
{"verdict": "MODEL_OK", "reason": "router-unloaded-autoload", "rc": 0,
 "want": "MODEL_OK/router-unloaded-autoload", "ok": true, "seconds": 0.75}
```

The size guard is satisfied (`base + 8·n ≤ size`), each element's length prefix is read at the
right offset, the per-element loop charges a step, and the budget trips at element 5 000 001 →
`-` → `MODEL_OK/router-unloaded-autoload`, the cell's expectation. **The blocking defect is
repaired and confirmed end-to-end through the real `bash kama-probe.sh`.**

Confirmed by the frozen counter itself at `b3289c18` (`--slow-files 96` per amendment 3,
natural pass):

```
ROUTER_BUDGET96_CELL nat W11-700k    ok=1 want=MODEL_UNLOADED/router-model-invalid
    run1=MODEL_UNLOADED/router-model-invalid/1.69s run2=MODEL_UNLOADED/router-model-invalid/1.59s
ROUTER_BUDGET96_CELL nat W12-strings ok=1 want=MODEL_OK/router-unloaded-autoload
    run1=MODEL_OK/router-unloaded-autoload/0.83s run2=MODEL_OK/router-unloaded-autoload/0.84s
```

Both cells green, and the load pass's W01 green too. For contrast, the same counter at
`bbdfc930` (before the amendments) printed `W12-strings ok=0 … run1=MODEL_UNLOADED/
router-model-invalid` — the defect and its repair, both from the counter's own mouth.

**The full C1 predicate is met.** The complete counter run at `b3289c18`
(`--slow-files 96 --burners 0 --allow-clock`) ended with all twelve cells green in both the
natural and the load pass:

```
ROUTER_BUDGET96 cells=12 mismatches=0 positive_mismatches=0 load_cells=12 load_stable=1
    budget=work probe=rev probe_sha256=11e5b01b8d01b5c56ad0200f04c0871a95d398eafc71a3819cb2629fc561e709
    rev=b3289c18ba1a2504afc3afe3c982ce6304876c5b w03_seconds=305.6 load1_nat=46.94 burners=0
```

(W03's natural pass cost 305.6 s here — well above the 75 s guard — so the amendment-3
`--slow-files 96` remedy makes the discriminator true on this host, as predicted.)

## B1a. Every boundary re-confirmed end-to-end at the tip

All seven boundary fixtures driven through the real probe against a stub router, reading
`rows[0].verdict` / `rows[0].reason` — the channel C1 grades:

| fixture | steps | verdict / reason | expected | ok |
|---|---|---|---|---|
| nd=1, n=833 332 | 4 999 996 | `MODEL_UNLOADED` / `router-model-invalid` | MODEL_UNLOADED | yes |
| nd=1, n=833 333 | 5 000 001 | `MODEL_OK` / `router-unloaded-autoload` | MODEL_OK | yes |
| nd=3, n=624 999 | 4 999 996 | `MODEL_UNLOADED` / `router-model-invalid` | MODEL_UNLOADED | yes |
| **nd=3, n=625 000** | 5 000 001 | `MODEL_OK` / `router-unloaded-autoload` | MODEL_OK | yes |
| nd=4, n=555 555 | 4 999 999 | `MODEL_UNLOADED` / `router-model-invalid` | MODEL_UNLOADED | yes |
| nd=4, n=555 556 | 5 000 008 | `MODEL_OK` / `router-unloaded-autoload` | MODEL_OK | yes |
| exactly 5 000 000 steps (833 332 headers + 1 KV entry) | 5 000 000 | `MODEL_UNLOADED` / `router-model-invalid` | MODEL_UNLOADED | yes |

The bolded row is the one `SKILL.md`'s nd=3 row got wrong at `b3289c18`: 625 000 is the first
**undecidable** count, and the probe grades it `MODEL_OK` / `router-unloaded-autoload` — loadable
— end-to-end, while the table published it as decidable. Amendment 4 corrected the row to
624 999 (B3); the boundary itself is unchanged, and this measurement is the one that shows it.

## B2. FIXED — the SKILL table now prices `5 + nd` and names the per-rank ceilings (A3)

`SKILL.md:2431` now reads "One tensor header costs **`5 + nd` steps** (`nd` = rank) … name `u64`
length + `skip` = 2, `nd` `u32` = 1, `nd` dims `u64` = `nd`, type `u32` + offset `u64` = 2.
Six steps is the `nd = 1` case only." The table carries a per-`nd` decidable-header column and
the `(5 000 000 - 4) / (5 + nd)` formula. The C2 counter (`tools/round96-depth-audit.py`) now
derives `CEILING = (max_steps - PREAMBLE) // STEPS_PER_HEADER` with `PREAMBLE = 4`, so the
counter and the prose share one arithmetic. `DEPTH_AUDIT checks=9 mismatches=0 met=True` at the
tip, `checks=9 mismatches=9 met=False` at base.

**One residual error survived in the same table at that revision** — the nd=3 row, now repaired
by amendment 4; see B3.

## B3. FIXED by amendment 4 — the nd=3 row of the new table was off by one

At `b3289c18` this was **live**: `SKILL.md`'s new table and the C2 counter's new needle both said
**625,000** for `nd=3`, while the arithmetic gives `floor((5 000 000 − 4) / 8) = 624 999` and the
landed parser agrees:

```
nd=3 n=624998: state=invalid steps=4999988  decidable=True
nd=3 n=624999: state=invalid steps=4999996  decidable=True
nd=3 n=625000: state=-       steps=5000001  decidable=False
```

So 624 999 headers decide and 625 000 does not — the published nd=3 row named the first
**undecidable** count as the decidable one, and the depth audit's needle was the literal string
`"625,000"`, so the audit *enforced* the wrong figure rather than detecting it.

**Amendment 4 (`20317286`) repaired it**: `SKILL.md:2438` now reads `| 3 | 8 | 624,999 |` and the
depth counter's needle is `("624,999", "nd3-ceiling")`, with the per-rank arithmetic checks added
(the counter's docstring now names all five ceilings: 999,999 / 833,332 / 714,285 / 624,999 /
555,555 — all five match this seat's measurements). `DEPTH_AUDIT checks=14 mismatches=0 met=True`
at the tip, `checks=14 mismatches=14 met=False` at base. **Verified fixed.**

## B4. LIVE — the probe's own comment still prices a fixed 6 steps and the C3 audit enforces it

`tools/kama-probe.sh` was **not changed** by amendment 2 (`git diff --stat bbdfc930..HEAD --
tools/kama-probe.sh` is empty). Its comment at lines 575-577 still reads:

```
# The binding ceiling is 6 steps per tensor header: name u64+skip 2, nd u32 1, dims u64 1,
# tensor type+offset 2 = 6, so MAX_STEPS = 5 000 000 puts the ceiling at ~833 333 tensor
# headers.
```

and line 581 still says "6 steps per tensor header made a 700 000-tensor file decode as
undecidable". This now **contradicts `SKILL.md` in the same tree**, which says `5 + nd`. One of
the two disclosures is wrong and they are graded by different instruments.

Worse, the C3 disclosure audit **requires** the probe to keep the wrong string:
`tools/round96-disclosure-audit.py:51` — `if max_steps != 5_000_000 or "6 steps per tensor
header" not in probe: mismatches += 1`. Its module docstring likewise still says "(6 steps per
tensor header)". The needle matches **two** places in the probe (line 575, the ceiling comment,
and line 581, the `MAX_STEPS` assignment comment), so correcting the ceiling comment alone
would leave the needle satisfied and the audit green — the defect would then be *invisible* to
the instrument that is supposed to police it. (Correcting both lines would redden
`DISCLOSURE_AUDIT`; correcting only line 575 would not, because line 581 still carries the
phrase — which is why the coupling is a trap in both directions.)

This is the same shape of defect the round-96 C3 claim exists to close ("every disclosure the
lane repeats matches the bytes it sits beside") — the probe's comment is a disclosure the lane
repeats, and it sits beside a `SKILL.md` that now says something different.

## B5. LIVE — the counter's fixture oracle still uses the pre-amendment-2 threshold (A4)

`tools/round96-router-budget.py` `fixture_class()` still reads (line 201, unchanged by amendments
2 and 3):

```python
if n_tensors > 833_333:  # at M1 (MAX_STEPS = 5 000 000): > MAX_STEPS/6 -> undecidable
    return "-"
```

Amendment 2 corrected the *published* figure to 833 332 in SKILL.md and in the depth counter,
but left the C1 counter's oracle at 833 333. The oracle still disagrees with the landed probe at
exactly 833 333 (measured: oracle `invalid`, probe `-`). The comment's own arithmetic
("> MAX_STEPS/6") is also the wrong formula — it omits the 4 preamble steps, so even the
threshold it names is one too high.

Latent (no cell sits on 833 333), but it is a live inconsistency between two numbers in the same
tree that the amendments were supposed to harmonize.

## B6. STILL LIVE — the C3 evidence-pointer check cannot detect the defect it names (A5)

Amendment 2 added a fourth check (counter docstring states `MAX_STEPS`) and the depth audit
dropped its vacuous check. The **disclosure** audit's check (2) and its evidence-pointer check
are unchanged. Per-check at the tip:

| check | base | tip | discriminates |
|---|---|---|---|
| c1 `MAX_STEPS` == 5 M and "6 steps per tensor header" present in probe | FAIL | PASS | yes |
| c2 old `MAX_TENSORS = 1_000_000` + `the ceiling is 1,000,000` both present | FAIL | FAIL | **no** (inert) |
| c3 counter docstring `20 + 25 * npaths`, not `20 + 15 * ncand` | FAIL | PASS | yes |
| c4 counter docstring states `MAX_STEPS` | FAIL | PASS | yes (new) |
| c5 capability evidence pointer resolves AND ancestor | PASS | PASS | **no** |
| c6 probe contains `20 + 25 * npaths` | PASS | PASS | **no** |

`DISCLOSURE_AUDIT checks=6 mismatches=0 met=True` at the tip, `checks=6 mismatches=3 met=False`
at base. The evidence-pointer check still passes on the stale pointer it was written to catch,
and c2 is still inert (the probe never contained the literal `MAX_TENSORS = 1_000_000`).

## B7. Confirmed correct at the tip

* **W12 is repaired** (B1) and grades `-` through the landed parser.
* **C1's frozen predicate is met**: `cells=12 mismatches=0 positive_mismatches=0
  load_cells=12 load_stable=1`, all twelve cells green in both the natural and the load pass
  (B1).
* **`SKILL.md` carries the `5 + nd` table, the 4-step preamble, and the per-rank ceilings** (B2).
* **The C2 depth audit derives its ceiling from the probe's constants** (`(max_steps - 4) // 6`)
  rather than hardcoding a pair — the off-by-one class of defect is closed at the instrument
  level, and `checks=9 mismatches=9 met=False` at base shows it discriminates.
* **The C1 counter's docstring now states `MAX_STEPS` (5 000 000)**, matching the probe — the
  round-95 `4 000 000` residue is gone, and the C3 audit grades it (new check c4).
* **The 700 000-tensor discriminator still holds**, and the base control was re-run as
  `--allow-clock --burners 0` (amendment 2 F6) rather than the structurally-red `--skip-load`.
* **Amendment 3 correctly diagnoses the W03 guard as a host-speed parameter.** This seat
  independently measured the same thing (A6 at `bbdfc930`: the W03 natural pass cost 65.8 s
  on this host, below the 1.25 × 60 s guard, so the counter returned
  `could-not-evaluate` exit 2 rather than a verdict). Amendment 3's remedy — measuring the M1
  receipt with `--slow-files 96` so the guard is true on this host — is the right shape, and the
  receipt names the count it used, which is what makes it checkable.

## Severity summary at the tip `bb4a997a` (amendments 1–5)

**C1's frozen predicate is met** (`cells=12 mismatches=0 positive_mismatches=0 load_cells=12
load_stable=1`, all twelve cells green in both passes), and the C2 and C3 predicates are met at
their amendment-5 reference revisions (`DEPTH_AUDIT checks=14 mismatches=0 met=True`,
`DISCLOSURE_AUDIT checks=6 mismatches=0 met=True`). The blocking defect (A2, W12 ungradeable)
was fixed — twice, since amendment 2's own repair was still red — and verified end-to-end against
the tip's own bytes.

Two of this seat's four findings are now repaired by the amendments (A2→B1, A3→B2, A4→B5, and
B3 by amendment 4). The two that remain are **figure and instrument defects**, both confirmed
still live at `bb4a997a`, in descending order:

1. **B4 — the probe's comment contradicts `SKILL.md`, and the C3 audit's needle matches the
   probe's stale figure.** `tools/kama-probe.sh` is byte-identical across every amendment
   (`git diff --stat 4a0f6a35..HEAD -- tools/kama-probe.sh` is empty), so its comment still
   prices a fixed 6 steps per header and still names "~833 333", while `SKILL.md` in the same
   tree says `5 + nd` and 833 332. `tools/round96-disclosure-audit.py:51` requires the probe to
   keep the string `"6 steps per tensor header"`, which appears twice in the probe (lines 575
   and 581) — so a partial correction leaves the audit green over a still-wrong probe, and a
   full correction turns the audit red without touching its needle. Two contradictory
   disclosures of one fact now coexist, and the calibration instrument's needle is anchored to
   the wrong one.
2. **B5 — the C1 counter's fixture oracle still carries the pre-amendment-2 threshold**
   (`n_tensors > 833_333`, with the wrong `> MAX_STEPS/6` formula) while the published figure is
   833 332. Unchanged by amendments 2, 3, 4 and 5. Re-verified at `bb4a997a`: oracle `invalid`
   vs landed probe `-` at exactly 833 333.
3. **B6 — the C3 evidence-pointer check still passes on the stale pointer it was written to
   catch, and its "old ceiling" check is still inert.** Unchanged by every amendment.

None of these can make a *correct* file grade incorrectly: they are figure and instrument
defects. B4 makes the lane publish two contradictory disclosures of the same fact — precisely
what C3 claims to police — and B5 leaves an oracle that disagrees with the probe it is supposed
to model.

**Not claimed, and worth stating:** this seat measured the *decision boundary*. It did not
audit the router-mode verdict logic, the `/props` path, the snapshot ledger, or any other
surface. The claims' own disclosed limits (slow `/props`, the wall-clock wrapper) remain routed
by the lane and were not examined here.

## Smallest remediation (not applied — no remediation scope was granted)

1. **B4:** correct `tools/kama-probe.sh` lines 575-577 *and* 581 to the `5 + nd` arithmetic and
   the 833 332 nd=1 ceiling, and amend `tools/round96-disclosure-audit.py` (its docstring and its
   check (1) needle `"6 steps per tensor header"`) to grade `5 + nd` instead. The needle matches
   two probe sites, so all three edits must move together: correcting the probe without the
   needle leaves the audit green over a wrong probe; correcting the needle without the probe
   reddens the audit. Since the counters are frozen after their commit, this needs a round-96
   amendment 4 with re-frozen counters and re-run base controls.
2. **B5:** change the C1 counter's `fixture_class()` threshold to `n_tensors > 833_332` and its
   comment to `(5 000 000 - 4) // 6`, or better derive it from `MAX_STEPS` and the header cost.
   (B3 needs nothing further — amendment 4 did it.)
3. **B6:** make the disclosure audit's evidence-pointer check assert the pointer names the
   commit the claim was filed at (or that it is not the superseded first revision), and either
   fix its "old ceiling" check to match the probe's actual constant spelling or drop it.

## Reproduction

Scratch (deleted on exit): `extract.py` (pull the landed `ROUTER_PY` and instrument `need()`),
`boundary.py` (binary search + end-to-end runner against a stub router), `c3_new.py`
(per-check base-vs-tip discriminator table for the amended audit), `e2e_nd.py` (per-rank
end-to-end verdicts), `e2e_w12_new.py` (the amended W12 fixture and the seven boundary fixtures
through the real probe at the tip).

Receipts, all in `receipts/`:

| file | what it shows |
|---|---|
| `bsearch-boundaries.out` | the four dimensionality boundaries (A1) |
| `e2e-verdicts.out` | nine end-to-end verdicts through the real `bash kama-probe.sh` (A1/A2) |
| `nd3-boundary.out` | the nd=3 boundary, 624 999 vs 625 000 (B3) |
| `e2e-boundaries-at-tip.out` | all seven boundary fixtures re-confirmed end-to-end at the tip (B1a) |
| `w12-at-tip.out` | the tip's own W12 fixture: 54 000 049 bytes → `-` → `MODEL_OK` (B1) |
| `c1-counter-at-head-full.out` | the counter at `bbdfc930`, showing `W12-strings ok=0` (A2) |
| `c1-counter-at-tip-full.out` | the counter at `b3289c18`: all 12 cells green, `mismatches=0` (B1) |
| `oracle-vs-probe-at-tip.out` | the B5 oracle disagreement and the nd=3 boundary, re-verified at `bb4a997a` |
| `c3-per-check-discrimination.out` | the per-check table at `bbdfc930` (A5) |
| `c3-per-check-discrimination-amended.out` | the per-check table at the tip (B6) |
