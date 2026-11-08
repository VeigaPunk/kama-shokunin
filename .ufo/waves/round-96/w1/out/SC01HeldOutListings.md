# SC01HeldOutListings — round-96 wave-1: held-out listings the frozen 12 cells do not cover

Seat `SC01HeldOutListings` (Godspeed). Lane `kama-shokunin`. Frozen claims read first
(`plans/round-96-claims.md`) and treated as binding; no frozen predicate was changed and no
tracked lane file was edited; no git/jj mutation run. Machine receipts in
`w1/out/SC01HeldOutListings/receipts/`.

**Tip measured:** `b3289c18` (round-96 amendment 3). **Frozen base:** `5d43528b`.
**Probe under test:** `tools/kama-probe.sh` at the tip, sha256
`11e5b01b8d01b5c56ad0200f04c0871a95d398eafc71a3819cb2629fc561e709`; base probe sha256
`b49d961a0548f3c30a264d036b080c0b99a2bb8dfce523f575fbdb00d76a85df`.
**Method:** every number below comes from the probe's *own* bytes. The `ROUTER_PY` python block was
extracted from `tools/kama-probe.sh` at the given revision (`ROUTER_PY_tip.py` /
`ROUTER_PY_stepcount.py`, the latter adding a step counter at the two `steps[0] += 1` sites), and
every listing was driven end-to-end through the real probe (`check --port … --expect good --json`)
against a stub llama.cpp router on loopback. No re-implementation of the decision was used for any
verdict.

Axes named: **operability** (does the listing decide, and does the verdict depend on the bytes),
**coverage** (which shapes the frozen 12 cells never reach), **calibration** (do the disclosed
figures match the bytes beside them).

## Verdict summary

| # | Finding | Verdict |
|---|---|---|
| H1 | A listing's verdict is **not** a function of its candidates' bytes: one undecidable (`-`) candidate masks every invalid sibling and grades the whole listing `MODEL_OK` | **confirmed — undefended** |
| H2 | The amended SKILL.md ceiling table's **nd=3 row is one too high** (625,000 published; 624,999 measured) | **confirmed** |
| H3 | The C1 counter's own `fixture_class` oracle **disagrees with the probe** at exactly 833,333 nd=1 headers | **confirmed** |
| H4 | Four GGUF shapes llama.cpp's loader **rejects** are graded **loadable** by the probe | **confirmed — false passes** |
| H5 | The pass-level wall clock is still live but not reachable at the sizes the frozen cells use | **measured, not exploitable here** |
| H6 | Listing size is bounded by the 4 MiB answer cap, not by the step budget | **confirmed** |

Reproduced-and-refuted: the W12 fixture defect (fixed by amendment 3 before this seat's report
landed) and the `nd`-dependence / 833,332-ceiling findings (independently found and fixed by
amendment 2). Those are recorded in §5 for the record, not claimed as new.

---

## H1 — the verdict is a property of the listing, not of the candidate (the big one)

**Verdict: confirmed, and no frozen cell covers it.**

The frozen 12 cells are all *homogeneous* listings (every candidate names a file of the same class)
except W05, which mixes 7 slow files with 1 valid one. The probe's `router_refine` grades a listing
`MODEL_UNLOADED` only when **every** candidate is decidably bad:

```sh
# tools/kama-probe.sh:934 (router_refine)
missing|invalid) nbad=$((nbad + 1)); [ -n "$unloadable" ] || unloadable="router-model-$fstate" ;;
# tools/kama-probe.sh:937
if [ "$nbad" -lt "$ncand" ]; then unloaded=1; fi
```

One candidate whose state is `-` (undecidable) leaves `nbad < ncand`, so `unloaded=1` and the
listing grades `MODEL_OK/router-unloaded-autoload` — *loadable*. Measured (`receipts/compose-results.json`):

| Listing | Tip verdict |
|---|---|
| C1 — 8 × invalid | `MODEL_UNLOADED/router-model-invalid` |
| C7 — 1 × over-budget (`-`) | `MODEL_OK/router-unloaded-autoload` |
| C3 — 1 × invalid + 1 × over-budget (`-`) | `MODEL_OK/router-unloaded-autoload` |
| C2 — 8 × invalid + 1 × over-budget (`-`) | `MODEL_OK/router-unloaded-autoload` |
| C6 — 1 × invalid (nd=1) + 1 × 700k **nd=3** (`-`) | `MODEL_OK/router-unloaded-autoload` |
| C9 — 1 × file with a *real* defect (missing data section) | `MODEL_UNLOADED/router-model-invalid` |
| C8 — same file **+ 1 × over-budget (`-`)** | `MODEL_OK/router-unloaded-autoload` |

**C8 is the sharpest form:** one file's own bytes are decisive for its verdict, but the *listing*
it sits in decides it for it. The same bytes grade `MODEL_UNLOADED` alone (C9) and `MODEL_OK`
alongside one undecidable sibling (C8). This is the round-95 SC02 F1 falsification ("verdict is a
function of the bytes") in a shape the frozen cells do not exercise: it is not the *file* whose
bytes change the verdict, it is the *number and class of siblings*.

**C6 is the same effect with a file the round-96 work itself created**: a 700 000-tensor file with
`nd = 3` is undecidable at the raised `MAX_STEPS` (see H2/§5), and it hides a sibling that the
probe *can* decide.

**Why this matters for the wave.** C1's predicate is "`mismatches=0 positive_mismatches=0`" over
12 homogeneous cells. A homogeneous cell cannot express "the listing's verdict is decided by its
weakest candidate". A listing where the router reports *several* models — the normal llama.cpp
router case — is exactly the shape where one undecidable entry turns a real "this model cannot
load" into "this model is fine". The disclosed limits cover the *per-file* case
(plans limit (a): "a candidate whose declared tensor count exceeds `MAX_TENSORS` or that needs
more than `MAX_STEPS` stays `-`") but not the *per-listing* aggregation that follows from it.

**Not a defect in the frozen claims as written** — the claims do not claim per-listing
independence. It is a **coverage gap**: nothing in round 96 measures it, and the wave's own
predicate cannot see it. Recommended: a 13th cell, e.g. *W13-mixed-1-invalid-1-undecided* →
`MODEL_OK/router-unloaded-autoload`, with a `-` candidate and an invalid candidate in one listing,
so the aggregation rule becomes an asserted, frozen expectation rather than an accident.

## H2 — the amended SKILL.md ceiling table's nd=3 row is one too high

**Verdict: confirmed.**

`SKILL.md` (amendment 2) publishes a per-rank table:

| `nd` | steps/header | decidable headers |
|---|---|---|
| 0 | 5 | 999,999 |
| 1 | 6 | 833,332 |
| 2 | 7 | 714,285 |
| 3 | 8 | **625,000** |
| 4 | 9 | 555,555 |

The formula in the prose is `(5 000 000 - 4) / (5 + nd)`. At `nd = 3` that is `4 999 996 / 8 =
624 999.5` → **624,999**, not 625,000. Measured with the probe's own bytes
(`receipts/ceiling-table.json`, `receipts/final-results.json`):

```
nd=3, n=624999 -> state='invalid'  steps=4999996   (4 + 8n = 4999996 ≤ 5 000 000)
nd=3, n=625000 -> state='-'        steps=5000001   (4 + 8n = 5000004 >  5 000 000)
```

End-to-end through the probe as a router candidate:

```
F-A-nd3-624999-headers  -> MODEL_UNLOADED/router-model-invalid   (3.45s)
F-A-nd3-625000-headers  -> MODEL_OK/router-unloaded-autoload      (3.88s)
```

So a file with exactly 625,000 3-D tensor headers is *undecidable*, while the published table says
625,000 headers are decidable. Every other row of the table is right — my independent
binary-search measurement (`receipts/ceiling-table.json`, `measured max decidable` column) matches
999,999 / 833,332 / 714,285 / **624,999** / 555,555 against the table's
999,999 / 833,332 / 714,285 / **625,000** / 555,555. (The `nd = 0` row needed a corrected fixture:
the parser reads `ne = [u64() for _ in range(nd)] or [1]`, so a `nd = 0` header carries **no** dim
bytes on the wire. Measured with that correction: 999,999 headers → `invalid` at 4,999,999 steps,
1,000,000 → `-` at 5,000,001, so the published 999,999 is right.)

**The C2 counter cannot catch this.** `tools/round96-depth-audit.py:68-73` checks the four ceiling
rows by **string presence** (`"625,000" in skill`), not by arithmetic — only the `nd = 1` row is
derived (`derived = (max_steps - PREAMBLE) // STEPS_PER_HEADER`). The counter therefore prints
`DEPTH_AUDIT checks=9 mismatches=0 met=True` at the tip while the table it blesses is one row off.
That is the same class of defect as round-95's "verdict is a function of the bytes" falsification
reaching a *counter* instead of a probe: the instrument checks that a string is present, not that
the number is right.

## H3 — the C1 counter's own oracle disagrees with the probe at exactly 833,333 headers

**Verdict: confirmed.**

`tools/round96-router-budget.py`'s `fixture_class` decides a fixture's designed class from the
bytes it wrote, without consulting the probe. It says:

```python
if n_tensors > 833_333:  # at M1 (MAX_STEPS = 5 000 000): > MAX_STEPS/6 -> undecidable
    return "-"
```

The enforced ceiling is 833,332 (`(5 000 000 - 4) // 6`), so the correct predicate is
`> 833_332`. Measured (`receipts/final-results.json`):

| headers (nd=1) | counter `fixture_class` | probe's own parser | agree? |
|---|---|---|---|
| 833,332 | `invalid` | `invalid` | yes |
| **833,333** | `invalid` | **`-`** | **no** |

End-to-end: a listing naming a 833,333-header nd=1 file grades `MODEL_OK/router-unloaded-autoload`
(the probe's `-` → loadable), while the counter's oracle believes the fixture is `invalid` and
would expect `MODEL_UNLOADED/router-model-invalid`. The counter's own `build_fixtures` sanity gate
(`if got != want: raise CannotEvaluate`) would fire on such a fixture — a *counter* defect, not a
probe verdict, by the counter's own doctrine. No frozen cell uses a file at that exact header
count, so it is latent today; the `> 833_333` comment also re-states the superseded
`MAX_STEPS/6` figure.

## H4 — four loader-rejected shapes are graded loadable (false passes)

**Verdict: confirmed.** The probe's header comment claims to implement the loader's checks:

> "…cannot pass the GGUF loader's header checks (S584 ggml/src/gguf.cpp @ b12177…)" —
> `tools/kama-probe.sh:543-545`

Four shapes llama.cpp's `gguf.cpp` **rejects** are graded `ok` (⇒ loadable ⇒
`MODEL_OK/router-unloaded-autoload`) by the probe. Each fixture is otherwise a perfectly loadable
GGUF (valid offsets, data section present), so the *only* difference is the checked rule.
Verified by feeding the identical bytes to the probe's parser and to a reader mirroring
`ggml/src/gguf.cpp`'s rules (`receipts/loader-parity.json`, `receipts/parity-e2e.json`):

| Shape | llama.cpp (`gguf.cpp`) | probe | end-to-end verdict |
|---|---|---|---|
| L1 duplicate tensor name | REJECTS (`seen_tensor_names.insert` fails, `gguf.cpp:665`) | `ok` | `MODEL_OK/router-unloaded-autoload` |
| L2 tensor name ≥ 64 bytes | REJECTS (`name.length() >= GGML_MAX_NAME`, `gguf.cpp:657`) | `ok` | `MODEL_OK/router-unloaded-autoload` |
| L3 KV array with ARRAY element type | REJECTS (`switch(type)` default → "invalid GGUF type", `gguf.cpp:606-610`) | `ok` | `MODEL_OK/router-unloaded-autoload` |
| L4 duplicate KV key | REJECTS (`seen_keys.insert` fails, `gguf.cpp:575`) | `ok` | `MODEL_OK/router-unloaded-autoload` |
| L5 control — a plain valid file | accepts | `ok` | `MODEL_OK/router-unloaded-autoload` |

`GGML_MAX_NAME` is 64 (`ggml/include/ggml.h:229`, the file the lane's own S618 pins).

**Why this is a soundness gap and not a rounding difference.** The probe's verdict vocabulary has
no "the loader might reject this" state between `invalid` and `-`: `file_state` returns `missing`
or `invalid` for a file that "cannot pass the GGUF loader's header checks", and `-` only for
"nothing can be decided". These four shapes are *decidable* — a two-line addition to the probe's
parser would decide them — yet they are graded as loadable, which is the **false-pass** direction:
the operator is told a model that llama.cpp would refuse to load is fine. The probe's own
comment (`kama-probe.sh:63`) says a header "the loader rejects (S584 gguf.cpp checks) grades
router-model-invalid", so the code does not implement the claim its comment makes.

None of the 12 frozen cells exercises any of these shapes: they all use well-formed GGUFs with a
single scalar KV or no KV at all.

## H5 — the pass-level wall clock (plans limit (d), "SC01"): measured, not reachable here

**Verdict: measured; the disclosed limit is real but the frozen cells cannot reach it.**

`router_file_states` still bounds the whole pass with `timeout $limit`, `limit = 20 + 25 * npaths`
(`tools/kama-probe.sh:871-873`). The allowance assumes 25 s per path covers a `MAX_STEPS`-bounded
parse *at a loaded host*. Measured (`receipts/wall.json`), the probe's own parser on the worst-case
file (833,332 headers = 4 999 996 steps, the largest decidable nd=1 file):

| file | natural | 64 burners | allowance |
|---|---|---|---|
| ceiling-833332-nd1 | 1.64 s | **5.28 s** | 25 s/path |
| counter-slow-600000-nd1 | 1.21 s | 5.24 s | 25 s/path |
| nd3-700000 (undecidable) | 1.59 s | 4.98 s | 25 s/path |

~4.7× headroom at 64 burners, so the pass limit does not bite at the frozen cells' sizes. This is
the residual wall clock the plan discloses as limit (c)/(d) and routes to round 97; my measurement
confirms it is *not* the mechanism behind any finding above. Two independent confirmations that
the **file-level** decision is now byte-only: 8 repeated runs of the same 700k listing graded
identically (1.45–1.63 s, `MODEL_UNLOADED/router-model-invalid` every time), and the base-vs-tip
sweep below shows base/tip differ exactly where the step budget differs.

## H6 — listing size is bounded by the 4 MiB answer cap, not by the step budget

**Verdict: confirmed; reported for completeness.** A listing of N candidates costs
~188 bytes of `/v1/models` body each. The probe caps that answer at `MAX_BODY = 4 194 304`
(`curl --max-filesize`). Measured (`receipts/size-results.json`):

| candidates | body bytes | verdict |
|---|---|---|
| 1,000 | 189,916 | `MODEL_UNLOADED/router-model-invalid` |
| 5,000 | 953,916 | `MODEL_UNLOADED/router-model-invalid` |
| 20,000 | 3,828,916 | `MODEL_UNLOADED/router-model-invalid` |
| 30,000 | 5,748,916 | `FOREIGN_SERVICE/body-too-large` |

The pass cost stays flat in listing size (50 → 2,000 candidates: 0.13 s → 0.24 s), so there is no
quadratic blow-up in the candidate loop; the wall is the answer cap, and past it the verdict stops
being a router verdict at all. The frozen cells top out at 40 candidates, so this cliff is
unmeasured in round 96.

---

## 5. Findings reproduced and already fixed (recorded, not claimed as new)

These were found independently by this seat, then fixed by the lane's own amendments while this
seat was measuring. Reported so the evidence trail is complete:

- **W12's fixture bytes were not interleaved.** The probe's `skip_strings` reads each element as
  `[u64 length][payload]`; the counter's first fixture wrote `8*n` length prefixes followed by one
  payload run, so element 1 read a huge length and the file graded `invalid`, not `-`.
  Measured three shapes end-to-end (`receipts/w12-results.json`):

  | shape | base | tip |
  |---|---|---|
  | W12-amended (prefixes then payload) | `MODEL_UNLOADED/router-model-invalid` | `MODEL_UNLOADED/router-model-invalid` |
  | W12-correct (interleaved, 9 B/element) | `MODEL_OK/router-unloaded-autoload` | `MODEL_OK/router-unloaded-autoload` |
  | W12-old (one 6 MB element) | `MODEL_UNLOADED/router-model-invalid` | `MODEL_UNLOADED/router-model-invalid` |

  **Fixed by amendment 3** (`b3289c18`), which writes `(pack("<Q",1) + b"x") * n`. I verified the
  amended counter's `gguf_strbig()` bytes now grade `-` (steps 5,000,001) and that the counter's
  own W12 cell passes at the tip.
- **`nd`-dependence and the 833,332 ceiling.** My independent measurement of the per-header step
  cost (`5 + nd`, plus a 4-step file preamble) and the exact nd=1 boundary (833,332 decidable,
  833,333 → `-`) matches amendment 2's repaired table and the C2 counter's `PREAMBLE`/`CEILING`
  constants. **Fixed by amendment 2** (`fb5cd3cd`).

## 6. Base-vs-tip discrimination of the held-out listings

`receipts/discriminate.json` — which held-out shapes distinguish the frozen base from the tip
(a base-red/tip-green cell is a discriminator the frozen 12 cells may not cover):

| held-out listing | base | tip | discriminates? |
|---|---|---|---|
| nd1-700k (the frozen W11 shape) | `MODEL_OK` | `MODEL_UNLOADED` | yes |
| nd2-700k | `MODEL_OK` | `MODEL_UNLOADED` | yes |
| nd3-700k | `MODEL_OK` | `MODEL_OK` | no |
| nd4-700k | `MODEL_OK` | `MODEL_OK` | no |
| nd1-x833332 | `MODEL_OK` | `MODEL_UNLOADED` | yes |
| nd1-x833333 | `MODEL_OK` | `MODEL_OK` | no |
| strdefect-4999980 (real defect, under budget) | `MODEL_OK` | `MODEL_UNLOADED` | yes |
| strdefect-4999990 (real defect, over budget) | `MODEL_OK` | `MODEL_OK` | no |
| strarr-4999980 / strarr-5000000 | `MODEL_OK` | `MODEL_OK` | no |
| 600k+700k in one listing | `MODEL_OK` | `MODEL_UNLOADED` | yes |

6 of 12 discriminate. The **`nd3-700k` and `nd4-700k` rows are the notable ones**: at the tip they
still grade `MODEL_OK/router-unloaded-autoload` for a file the router oracle rejects — the exact
symptom C1 was raised to fix, surviving at `nd ≥ 3` because the step budget is spent per *rank*.
Amendment 2's SKILL.md does now disclose this ("That file now decides `invalid` at `nd ≤ 2` and
stays `-` at `nd ≥ 3`"), so it is disclosed prose — but **no frozen cell measures it**, so the
disclosure is not instrumented.

## 7. What I did not do

- No tracked lane file was edited; no frozen predicate, counter, or control was changed.
- No git/jj mutation was run (seat rule).
- The round-96 counters were run read-only (`round96-depth-audit.py`, `round96-disclosure-audit.py`,
  `round96-router-budget.py`) to see what they can and cannot catch; their verdicts are quoted, not
  re-litigated.
- I did not verify the `-` → loadable aggregation against a *live* llama.cpp router; the router
  oracle in every measurement is llama.cpp's `gguf.cpp` rules read from the pinned checkout
  (`/home/vgpnk/src/llama.cpp`) and the lane's S618/S619 rows, not a running server. The H1 and H4
  findings are therefore stated at the level the probe's own comment claims them
  ("cannot pass the GGUF loader's header checks").

## 8. Receipts

Machine-readable, all under `w1/out/SC01HeldOutListings/receipts/`:

| file | what it holds |
|---|---|
| `boundary.json` | per-shape step counts and states from the probe's own parser |
| `ceiling-table.json` | binary-searched max decidable header count per `nd` vs the published table |
| `listings-results.json` | H1..H7 held-out listings end-to-end through the tip probe |
| `decisive-results.json` | nd-sweep, exact-budget, scale and 8× stability runs |
| `discriminate.json` | base-vs-tip discrimination for 12 held-out shapes |
| `compose-results.json` | the H1 listing-composition cells |
| `size-results.json` | listing-size cliff at the 4 MiB answer cap |
| `wall.json` | per-file parse wall time, natural and under 64 burners |
| `oracle.json` | probe states for the loader-rule shapes |
| `loader-parity.json` | probe vs `gguf.cpp` rules on identical bytes (4 false passes) |
| `parity-e2e.json` | the same four shapes end-to-end through the probe |
| `w12-results.json` | W12 fixture shapes, base and tip |
| `final-results.json` | H2 (nd=3 row) and H3 (833,333) end-to-end |

Scratch (deleted on exit, receipts copied first): `/fast/scratch/hyaku/kama-r96/SC01HeldOutListings/`.
