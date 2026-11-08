# RV01StepBudget — round-96 wave-1 review: step budget, W11-700k, W12-strings

Seat `RV01StepBudget` (Godspeed). Lane `kama-shokunin`, tip `bbdfc930`, frozen base `5d43528b`,
claims read first (`plans/round-96-claims.md`) and treated as binding. No lane file touched; no
git/jj mutation run; receipts in `w1/out/RV01StepBudget/receipts.txt`.

Axes named: **operability** (does the budget decide the files the claim names?), **depth**
(is the step-cost table the arithmetic the code enforces?), **calibration** (do the repeated
ceiling/disclosure sentences match the bytes beside them?). Moves kept only where they improve
one and harm none; every claim below is measured, not inferred.

## Verdict summary

| # | Finding | Verdict |
|---|---|---|
| F1 | C1 W12-strings cell cannot grade `MODEL_OK`; the frozen predicate is unreachable at M1 | **falsified (BLOCKER)** |
| F2 | "a 700 000-tensor file parses to a decision" holds only for tensors with `nd ≤ 2` | **falsified as stated**; confirmed for nd 0–2 |
| F3 | The enforced nd=1 ceiling is 833,332 headers, not the exact 833,333 SKILL states | **falsified (SKILL exact figure)**; probe's `~833 333` holds |
| F4 | C2's before-state sentence and its "ceiling 1,000,000" check do not match the base bytes | **falsified**; C2 predicate itself still met |
| F5 | C3 prints `met=True` while the new counter's docstring repeats `MAX_STEPS (4 000 000)` | **falsified for C3's stated scope** |
| F6 | The committed C1 base control used `--skip-load`, not the specified two natural passes | **confirmed deviation** |
| F7 | The plan's W03 parenthetical names round 95 for a truncation that belongs to round 94 | **falsified (plan prose)** |

Confirmed in the same pass: the W11-700k discriminator; the `MAX_STEPS` raise as the only
behavioral ROUTER_PY change; the 4M-era 666,666 ceiling; `KILL=1200` vs the 1020 s derived limit;
`--skip-load` cannot pass; the `20 + 25 * npaths` docstring/wrapper agreement; the capability-row
evidence commit; C2/C3 tip-green/base-red.

## C1 diff: every behavioral change in ROUTER_PY

`git diff 5d43528b -- tools/kama-probe.sh` is **one hunk, 22 lines** (18 files changed overall,
this file `11 +-`). Enumerated:

1. **Behavioral:** `MAX_STEPS` `4_000_000` → `5_000_000` (`tools/kama-probe.sh:581`; base
   `git show 5d43528b:tools/kama-probe.sh` line 575). Files needing 4M–5M steps now decide
   instead of grading `-`.
2. **Textual only:** the disclosed-limit comment is replaced (`kama-probe.sh:575-584`). The old
   sentence did not name 1,000,000; it said "a file whose declared tensor count exceeds
   MAX_TENSORS, or that needs more than MAX_STEPS, is still `-`". No behavior.
3. `MAX_STEP_BYTES` follows `MAX_STEPS` (`:585`) but is **never read** — dead constant.
4. **No change** to `need()`, `skip_strings()`, per-element string charging, or per-path pass
   pricing in this diff: round 95's `c810f51e` ("charge one step per string element and price the
   pass allowance by model paths") is already at the base (base probe line 687 comment,
   `MAX_STEPS = 4_000_000` line 575). The assignment's "per-path step charging" is base state,
   not this round's change.

## F1 — BLOCKER: W12-strings cannot grade `MODEL_OK`; C1 is unreachable at M1

**Verdict: falsified.** The frozen cell expects `MODEL_OK/router-unloaded-autoload`; the probe
grades `MODEL_UNLOADED/router-model-invalid` at tip (and at base).

- Fixture bytes: `tools/round96-router-budget.py:164-172` writes `GGUF`+v3+`0,1`, one KV key `k`,
  a `<IIQ` header `(type 9, elem type 8, count 6 000 000)`, then **one** `struct.pack("<Q",1) +
  b"x" * 6_000_000`. File is **6,000,057 bytes**. A GGUF string array of 6,000,000 elements cannot
  occupy fewer than `49 + 8*6_000_000 = 48,000,049` bytes (each element carries an 8-byte length).
- Branch that decides first: `kama-probe.sh:693-694` `if base + 8 * n > size: raise Bad()` —
  raised **before** the per-element loop at `:700-703` that charges `MAX_STEPS`. State is
  `invalid`, so `file_state` → `invalid` → `MODEL_UNLOADED`.
- Measured through the counter's own `Runner`+`Stub`+`check`:
  `W12-strings: got MODEL_UNLOADED/router-model-invalid, want MODEL_OK/router-unloaded-autoload
  -> MISMATCH` (0.1 s).
- Measured through the counter's own `evaluate_pass` (40 slow files, 1 run):
  `NATURAL PASS tip: cells=12 mismatches=1 bad=['W12-strings'] elapsed=97.2s`.
- The freeze-time control already shows it: `controls/c1-base.out:11`
  `W12-strings ok=0 ... MODEL_UNLOADED/router-model-invalid`.
- Counter-proof that the intent is achievable: a correctly shaped fixture (9 bytes/element,
  54,000,049 bytes, same 6,000,000 elements) grades `MODEL_OK/router-unloaded-autoload` in 0.9 s —
  the step budget trips at element 5,000,001. So the defect is the fixture's size, not the budget.

Consequences: the predicate line `mismatches=0` is **unreachable** as frozen (`KILL` rule K1
fires); the claims' disclosed-limit sentence ("a file whose string-array element count exceeds
MAX_STEPS → `MODEL_OK` … (disclosed `-`)") and the counter docstring's `strbig.gguf … -> '-'`
line are false of the bytes. The `positive_mismatches` counter also cannot see this cell: the
`cid.startswith("W0")` test (`round96-router-budget.py:468-470`) excludes W10/W11/W12 by prefix.

## F2 — HIGH: 6 steps/header is nd=1 only; a 700 000-tensor file with nd ≥ 3 stays undecidable

**Verdict: falsified as written; confirmed for nd 0–2.** The parser charges `5 + nd` steps per
header, not 6:

- `kama-probe.sh:744-750`: `skip(u64())` = 2, `nd = u32()` = 1, `[u64() for _ in range(nd)]` = nd,
  `u32(), u64()` = 2 → **5 + nd**. Six holds only when `nd == 1`.
- Grounded on the loader: `ggml/src/gguf.cpp:676-745` reads name (u64 len + bytes), `n_dims` u32,
  `n_dims × ne` u64, then type u32, then offset u64; `ggml.h:690-697` (`ne[GGML_MAX_DIMS]`,
  S618 sha256 verified `590e00a5…67392`). `nd ∈ 0..4`.
- Measured (700,000 tensors, probe `check`):
  nd=0 → `invalid` (3,500,004 steps) · nd=1 → `invalid` (4,200,004) · nd=2 → `invalid` (4,900,004)
  · nd=3 → `-` (5,600,004) · nd=4 → `-` (6,300,004). A 700k file decides iff average `nd ≤ 2.1428`.
- The frozen W11 fixture is nd=1 only (`gguf()` packs `struct.pack("<IQIQ", 1, elems, 0, off)`), so
  W11 cannot see the nd>2 class.
- Disclosed limit (b) says only "KV and string-array work also charges steps"; dims charge steps
  too, and they are the **larger** charge (up to +3/header = +50%).
- Ceils at 5M: nd=2 → 714,285; nd=3 → 625,000; nd=4 → 555,555 — not 833,333.

Fix direction (not applied; frozen): either qualify the sentence/table with `nd = 1`, or price
`dims u64 nd` in the table and state the nd=4 ceiling.

## F3 — MEDIUM: the enforced nd=1 boundary is 833,332, not 833,333

**Verdict: falsified for SKILL's exact figure; probe's `≈` holds.** Four preamble steps are paid
before the first header: `rd(4)` magic, `u32()` version, `u64()` n_tensors, `u64()` n_kv
(`kama-probe.sh:717-722`). So total = `4 + 6n`.

- Measured: 833,332 headers → `invalid` (4,999,996 steps); 833,333 headers → `-` (5,000,002).
- `SKILL.md:2431` states "`5 000 000 / 6 = **833 333 tensor headers** (ceiling 833,333)`" — off by
  one against the code's decision boundary. The probe comment (`:576`) writes "~833 333", which is
  defensible.
- `tools/round96-depth-audit.py:23` hard-codes `CEILING = 833_333` and `:86-88` compares it to
  `max_steps // 6` = 833,333, so the counter is green without ever touching the boundary.

## F4 — MEDIUM: C2's before-state sentence and one check do not match the base bytes

**Verdict: falsified (description); C2's predicate is still met at tip.**

- `git show 5d43528b:SKILL.md` contains **no** "1 000 000", "1,000,000" or `MAX_TENSORS`
  tensor-ceiling sentence. The nearest prose is the router limit "gives up … after a 4 s deadline
  or 4 M reads" (round 93), and unrelated `n_ctx`/errata/memory-ceiling lines.
- The plan's C2 "Before" ("SKILL.md §Round 95 names a ceiling of 1 000 000 tensors") and the
  `controls/c2-base.out` description ("the ceiling sentence still says 1 000 000") describe bytes
  that are absent.
- Consequently `round96-depth-audit.py:74-76` `if "ceiling 1,000,000" in skill: mismatches += 1`
  is satisfied at **neither** revision — a vacuous check. The base control is red (7 checks,
  6 mismatches) for the absence of the new table, not for a false 1M sentence.

## F5 — MEDIUM: C3 green while the new counter's docstring repeats `MAX_STEPS (4 000 000)`

**Verdict: falsified for C3's stated scope ("every disclosure the lane repeats matches the bytes
it sits beside").**

- `tools/round96-router-budget.py:19`: "Work is bounded deterministically - `MAX_STEPS`
  (4 000 000) counts the parser's read/seek steps". The probe beside it (`kama-probe.sh:581`) says
  `5_000_000`.
- `tools/round96-disclosure-audit.py:44-80` grades only (a) the probe's `MAX_STEPS` value +
  `"6 steps per tensor header"`, (b) the docstring formula `20 + 25 * npaths`, (c) the capability
  row commit. It never reads the stale 4,000,000, so it prints
  `DISCLOSURE_AUDIT checks=5 mismatches=0 met=True`.

## F6 — LOW/MEDIUM: the committed C1 base control is not the frozen control

**Verdict: confirmed deviation.**

- `controls/c1-base.out:13`: `load_skipped=true load_cells=0 load_stable=0 … mismatches=-2 …
  burners=0` — produced with `--skip-load`.
- The plan's Do-nothing control specifies "with `--burners 0` (two natural passes; with
  `--skip-load` the predicate is structurally unreachable)". `--skip-load` returns 1
  unconditionally (`round96-router-budget.py:441-444`), so the receipt's summary cannot express
  "W11 red, all else green". The per-cell lines do (W11 `ok=0` at line 10) — and also show W12
  `ok=0` (line 11), i.e. the freeze-time control already contained the F1 defect.

## F7 — LOW: the W03 discriminator is attributed to the wrong round

**Verdict: falsified (plan prose).** Claims C1 cells: "W03 … the round-95 probe truncates /
un-decides W03's slow files at its `MAX_STEPS`". At 600,000 tensors the round-95 probe charges
`4 + 600 000×6 = 3,600,004 ≤ 4,000,000` and **decides** `invalid`; its own committed control says
`W03-slow-x40 ok=1 … 84.06 s/101.73 s` (`controls/c1-base.out:3`). The truncation belongs to the
round-94 constant 60 s (`BASE_WRAPPER = 60.0`, `MARGIN = 1.25`), which the counter's docstring
states correctly.

## Confirmed (positive evidence)

- **W11-700k discriminates:** tip → `MODEL_UNLOADED/router-model-invalid` (4,200,004 steps, 1.64 s);
  base `5d43528b` (4M) → `MODEL_OK/router-unloaded-autoload`. Matches the claim.
- **Only behavioral ROUTER_PY change** is `MAX_STEPS` 4M→5M (one hunk); per-element string charging
  and per-path pass pricing are already at base (`c810f51e`).
- **Old ceiling arithmetic:** `(4,000,000 − 4)/6 = 666,666`, matching the claim's ≈666,666.
- **KILL:** `KILL = 1200` > W03 derived limit `20 + 25×40 = 1020` (`kama-probe.sh:871`); round-95
  counter had `KILL = 400`.
- **`--skip-load` cannot pass:** unconditional `return 1`, prints `load_cells=0 load_stable=0`.
- **Docstring formula:** wrapper literal `local limit=$((20 + 25 * npaths))` matches; the round-95
  counter's `20 + 15 * ncand` is the confirmed before-state.
- **Capability row:** `SCORECARD.md:6320` cites `c810f51e`, which resolves and is an ancestor of the
  tip.
- **C2/C3 counters:** tip `7/0 met=True`, `5/0 met=True`; base `7/6 met=False`, `5/2 met=False`.
- **Other deciding branches:** `MAX_META` (512 MiB) never binds for ≤1M tensors (max header ≈64 MB
  at nd=4); a truncated 700k declaration is `invalid` via `n_kv*13 + n_tensors*24 > size`
  (`:726-727`); `MAX_TENSORS` >1M grades `-`; `MAX_ARR` (50M) is not W12's decider.
- **b12177 source:** tarball `f50a52f4…eea13`; extracted `ggml.h` = S618's
  `590e00a5…67392`; loader field order confirmed at `gguf.cpp:655-745`.

## Residual risk and verification gaps

1. **Loaded pass not run.** The natural pass alone already falsifies the predicate (W12 is
   load-independent), so a burner pass cannot rescue it; `load_stable` cannot turn a natural
   mismatch green. The loaded pass would add nothing to F1.
2. **W03 margin is host-dependent.** At `load1=18.58` the natural W03 took 52.62 s < the counter's
   75 s guard, so a full run here would return 2 (could-not-evaluate). The freeze receipt was
   measured at `load1=93.48`, W03 101.73 s. The plan doesn't disclose that M1 reproducibility needs
   a host slow enough to keep W03 ≥ 75 s. Not a claim defect; a reproducibility condition.
3. **nd class measured by construction**, not by loading a real 700k-tensor model (none exists);
   the claim prices the probe's parser, which is what was measured.
4. **MAX_META** was reasoned from header sizes, not exercised with a >512 MB header fixture
   (unnecessary — `MAX_TENSORS` caps first; and a >50 MB fixture is outside the /tmp caution).
5. Text grep was used for SKILL/SOURCES/SCORECARD strings; no LSP server serves Markdown/`.sh`
   here, so those matches are literal, not semantic. The probe behavior itself is measured
   end-to-end through the counter's own code path.

## Smallest falsification set for L1

1. Build the W12 fixture at ≥48,000,049 bytes (9 bytes/element) **or** drop W12 to a disclosed
   `invalid` expectation; then re-run C1.
2. Add `dims u64 nd` to the step table and state the nd=4 ceiling (555,555), or qualify C1's
   sentence with `nd = 1`.
3. Change the stated exact ceiling to 833,332 (or keep `≈` everywhere and drop "ceiling 833,333").
4. Fix the C1 counter docstring's `MAX_STEPS (4 000 000)` → 5,000,000 and extend C3 to grade it.
5. Re-run the base control with two natural passes as frozen; correct the C2 before-state and the
   W03/round-95 attribution.
