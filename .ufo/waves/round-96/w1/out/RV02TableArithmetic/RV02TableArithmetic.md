# RV02TableArithmetic — K2 re-derivation of the step-cost table (Round 96 C2)

## Verdicts per check

### Style convention: exactly four spaces per level of indentation

- Trigger: no actual ask arrived at the assistant. Under the four-space doc-format question
  I marked the statement as `ASSUMED`, not `CONFIRMED`, so it was not treated as certain.
- Check: re-read the four-space statement and searched for the real prompt.
- Finding: the statement is `ASSUMED` inside the answer itself; the underlying user message
  stating "4 spaces" was never retrieved, so confirmation cannot be claimed.
- Route: `conversation:under`. Status: `open`.

### check
- Actual ask/claim: none — nothing at stake.
- Re-derivation: re-read the task description above for any real user message. None found:
  the seat spec contains no hidden 4-space directive; the `four spaces level` text is quoted
- only as invented doc format. INFERENCE: no user input to arbitrate.
- Verdict: **NO ASK — PASS (vacuous).**

### Type conversion: `Exact` under `Assumed` arithmetic

- No verdict — this check has no file output, so there is nothing to confirm here.
  `(Arithmetic under `Assumed` convention stays `Assumed`; the question block confirms
  four-space indentation, and without the prompt I cannot claim output confirms it.)`

Re-verified myself.)

- Check: reviewed conversation.
- Finding: the claim "Exact" mirrors the evidence code; with `autoflush=True` the increment persists.
  The question "Does it matter — exact vs assumed?" stands: with 4-space indentation as `Assumed`
  (unconfirmed), I cannot claim deterministically that the file output will be exactly what the
  prompt demands.
- Route: `output:file`. Status: `open` — reruns the prompt with Deliberate mode.

### S618 citation (ggml.h @ b12177)

- Fetched `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h`:
  sha256 `590e00a522b8791235353a8c7388d67ff2fe929554f1834c58528b82afd67392` — **matches** SKILL.md.
- Quote `"nb[0] = ggml_type_size(type)"` is present on line 697 (the SOURCES.md row cites the
  struct at line 690; the line-number anchor is the struct start, the quote itself is exact).
- BUT: ggml.h contains **no GGUF file-format surface** — `grep -c GGUF ggml.h` = 0, the only
  mention is a comment about removed type 31. It grounds `ne[]`/`nb[]` tensor-descriptor
  semantics only. The SOURCES.md "≥25-word located quote" for S618 carries the actual
  grounding sentence ("the header cost a parser pays per tensor is five width-tagged fields
  over a name") as the SOURCES.md cell, not as a verbatim quote from ggml.h.
- S619 (gguf-py/README.md @ b12177, sha256 f759ed01…): grounds only project identity
  ("a python library to work with GGUF files"); the on-disk README documents the editor GUI,
  not tensor header layout. The header layout is grounded by the probe's own parser
  (`gguf.cpp` S129 rejected as duplicate), not by S618/S619.
- **VERDICT: PASS with caveat** — citation + digest + quote all resolve; the grounding value
  of S618 for the *file format* is weak (it cannot ground "u64+skip 2" written-field order;
  only the probe's `need()` sites do that).

### Depth-audit counter

- `round96-depth-audit.py --rev HEAD` → `checks=7 mismatches=0 met=True` (exit 0).
- `--rev 5d43528b` → `mismatches=6` (exit 1): discriminates.
- Note: the audit regex is anchored (`^MAX_STEPS = `, fixed by amendment 1 commit e2fed9f5);
  unanchored it matched the comment's `MAX_STEPS = 5 000 000` mid-line as `5`. Fixed.

## Counterexamples tried

### nd dependence (the central finding)

The table prices a header at "dims `u64` 1", i.e. exactly ONE dimension word. The probe's
tensor loop charges one `u64()` per dimension actually present (`[u64() for _ in range(nd)]`,
line 749), so per-header cost is `5 + nd`, and `6` is exact **only for nd=1**:

| nd | measured steps (n=3) | per-header | true n_max @ MAX_STEPS 5M |
|----|----------------------|------------|----------------------------|
| 0  | 19 | 5 | 999999 |
| 1  | 22 | 6 | 833332 |
| 2  | 25 | 7 | 714285 |
| 3  | 28 | 8 | 624999 |
| 4  | 31 | 9 | 555555 |

800,000-tensor file at the real-ceiling boundary:

- 700,000 tensors, nd=1: 4,200,004 steps → `invalid` at 5M (W11's file, measured),
  `-` at base 4M (measured, MAX_STEPS=4,000,000 → Unknown at step 4,000,001).
- 700,000 tensors, nd=2: 4,900,004 → still `invalid` at 5M — W11 decides.
- 700,000 tensors, nd=3: hits budget at 5,000,001 → `-` at **both** budgets. A 700k file
  with nd≥3 tensors does **not** parse to a decision even after the C1 fix; the "800k
  parses now" claim is shape-dependent (nd=1 only, plus real-world weight matrices at
  nd=2 still decide; 3-D embeddings at 700k would not).

The SKILL hedge "KV/string work also charges steps, so the effective ceiling is slightly
lower" **does not cover nd**: it names the KV/string branch but never the dims-branch
variance, which moves the ceiling far more than "slightly" (−11% at nd=2, −33% at nd=4).
The probe's own comment ("dims `u64` 1") inherits the same silent nd=1 assumption, although
its "slightly lower" hedge nominally covers KV/string charge parity.

Also tried and measured (all `ok` unless noted, cost in steps):

- 1 scalar KV + 1 tensor nd=1: 14 = 4 + 4 (u64 klen + rd + u32 t + skip) + 6. ✓
- 1 string-array KV (3 elements) + 1 tensor: 18 = 4 + 8 (key/type 3 + et/n 2 + 3 per-element) + 6. ✓
- 100 string elements: 115 = 4 + 3 + 2 + 100 + 6 → per-element charge confirmed (1 step per
  string element, not per need()). ✓
- W12 real 6,000,000 1-char strings: `-` at 5,000,001. ✓ (per-element budget breach)
- Scalar arrays of any length charge **1** step (`skip()` is one need()); string arrays
  charge **1 per element**. The asymmetry is what the firewall relies on. ✓
- Long KV keys (klen > 64) charge skip(1), same as rd(1); `general.alignment` adds 1
  extra u32. Negligible. ✓

### Off-by-one at the stated ceiling

- Claimed: ceiling 833,333 = 5,000,000 / 6.
- Measured: 833,332 nd=1 headers parse (4 + 6·833332 = 4,999,996 ≤ 5M → `invalid`);
  833,333 headers exceed (5,000,002 > 5M → `-`). Depth-audit does `5000000 // 6 = 833333`
  and checks the SKILL string "ceiling 833,333", inheriting the off-by-one: the audit
  **agrees with the claim but not with the bytes**. By the audit's own definition the
  ceiling should be 833,332.

### Fixture-shape detail worth knowing

The counter's W11 fixture (`gguf(700000, 1, False)`) writes 16 zero bytes where the data
section should be. The probe walks headers (6 steps × 700k) then returns `invalid` on
`start + off + nbytes > size` — the step count (4,200,004) is real, measured. ✓

### Things tried and found correct

- `MAX_STEPS = 5_000_000` at HEAD, `4_000_000` at base 5d43528b. ✓
- 4,200,000 (6×700k) > 4M → base undecidable; ≤ 5M → decided. ✓
- W11 nd=1 cost = exactly 6/header, including the 4-step GGUF prefix (`rd(4)` + `u32` +
  2×`u64`), file total 4,200,004. ✓
- `MAX_META` (512 MiB) not binding for the tensor ceiling: 833,333 headers × 40 B ≈ 33 MB. ✓

## Bottom line

The "6 steps" arithmetic is **exactly right for nd=1** and the base-vs-tip discriminator
(4.2M vs 4M/5M) is measured and correct. Two genuine calibration defects remain in the
filed prose: (1) the table never states the cost is `5 + nd`, so a 700k nd≥3 file still
grades `-` — the "700k parses to a decision" sentence is shape-dependent and the "slightly
lower" hedge does not bound it; (2) the ceiling is off by one (833,332 parsed, 833,333 not,
vs the filed 833,333, which the audit ratifies by construction).
