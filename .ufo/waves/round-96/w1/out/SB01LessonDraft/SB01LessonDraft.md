# Round 96 — the step budget decides 700 000-tensor files; every disclosure names the bytes it sits beside

L1 `KamaR96`. Base `5d43528badc31ad6c0ca1848c00561f531924e4d` (round-95 admitted). Plan:
`plans/round-96-claims.md`; amendments 1–4 (`plans/round-96-amendment-{1,2,3,4}.md`). Previous closure:
`corpus/lessons/round-95-verifier-spotcheck.md` (admitted; six defects routed here, five closed).

**Draft status.** This is the scribe's draft of `corpus/lessons/round-96.md`, written from the
wave-1 evidence at lane tip `20317286`. It is **not** the landed file: the L1 integrator owns the
landing. Every figure below was measured by this seat against the named bytes; where a figure is
carried from a prior round rather than re-measured here, it says so.

## Gate

Rows opened this round come from the pinned llama.cpp `b12177` tag, fetched 2026-11-08 as per-file
raw URLs (`https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`). Each row names the
file's measured sha256 and a ≤25-word located quote with its line; the digests below were computed
by this seat from the fetched bytes.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S618 `ggml/include/ggml.h` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-08, sha256 `590e00a5…67392` | `nb[0] = ggml_type_size(type)` (line 697, in `struct ggml_tensor`) | The tensor descriptor's per-rank element counts and byte strides are what a GGUF header parser prices; the row carries the tensor-header cost that `MAX_STEPS` is sized against. Filed at the freeze commit `58001b71`. |
| S619 `gguf-py/README.md` @ b12177 | **admit** (A, docs, mined) — *not yet filed* | raw URL — 2026-11-08, sha256 `f759ed01…18af` | `This is a Python package for writing binary files in the [GGUF](https://github.com/ggml-org/ggml/pull/302)` (line 3) | The reference writer's own statement of the GGUF container the probe parses; grounds the header-layout claim from the implementation side, next to S618's runtime side. The plan names this row as opened this round (C2 "Sourced") but `corpus/SOURCES.md` carries no S619 row at tip — see the M-classes below and the L1 finding list. |
| `ggml/src/gguf.cpp` @ b12177 (the "gguf.cpp reconsideration") | **reject** (duplicate of S129) | raw URL — 2026-11-08, sha256 `51bd966a…dd78` | `GGML_LOG_ERROR("%s: invalid magic characters: '%c%c%c%c', expected 'GGUF'\n", __func__, c0, c1, c2, c3);` (line 482) | The candidate construct is byte-identical to what S129 already teaches at `704366d` (same file, same line 482, same message — this seat fetched both revisions and diffed the region: only the surrounding lines moved). S129's scope is pinned to `704366d`; the b12177 revision is the same construct at a newer tag, so a new row would teach nothing S129 does not, and would restate the same digest-less anchor. Flip: the construct moves in a later release. |
| The b12177 codeload archive as a SOURCES row | **reject** (input, not a teaching source) | https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177 — 2026-11-08 | n/a (binary archive) | The archive is the counter's pinned population input; what the lane learns is cited per file through the raw rows above. Carried from rounds 94–95, re-checked here. |

`status`/`recheck`/`used-by` changes on existing rows: none. S618 is a new row (`mined`, recheck
`on-release`, used-by `SKILL.md`). Census before → after: **357 → 358** rows as measured by this seat
(`grep -c '^| S[0-9]'` on the base blob and on the tip blob; the shared census script agrees:
`kama rows 358`). `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
exits 0 (only the pre-existing W04 duplicate-URL warnings and W01 S481).

**Gate finding for the L1 — S619 is named as a sourced row but is not filed.** `plans/round-96-claims.md`
C2 names S619 (`gguf-py/README.md` @ b12177) as opened this round and as part of the sourced claim,
and the round's frontier step records "Rows: 357 → 359 at the time of writing". The tip's
`corpus/SOURCES.md` carries **358** rows: S618 is filed, S619 is not, and no census receipt at tip
claims 359. This seat fetched the file and measured its sha256 (`f759ed01…18af`) so the row can be
filed from a measured digest; the quote above is the located line.

## Mistakes

The four classes below are the rounds-92→95 mistake classes this round's claims close. Each is
written as class · evidence · captured-by · fix, with the receipt or file that carries the evidence.

**M1 — a counter cell whose expectation the fixture bytes cannot reach.** Class: *a discriminator
that cannot discriminate* — the fixture does not exercise the branch the cell grades, so the cell's
expectation is unreachable and the counter is green for the wrong reason. Evidence: the W12-strings
cell's first fixture (freeze commit `58001b71`, `tools/round96-router-budget.py` `gguf_strbig()`)
declared a string array of 6 000 000 elements but wrote `8 * N` length prefixes followed by a
single 6 MB payload run — the bytes were contiguous, not interleaved. This seat extracted the
probe's own parser from `tools/kama-probe.sh` and graded the two layouts on identical bytes: the
contiguous layout grades `invalid` (the reader lands one byte into the next length prefix, reads a
huge length, and the `base + off > size` guard fires), while the interleaved layout grades `-`.
The cell therefore graded `MODEL_UNLOADED/router-model-invalid` where the plan's disclosed `-` was
expected. Captured-by: wave-1 seat `RV01StepBudget` (BLOCKER F1), answered by amendment 2's repair
and then re-broken by amendment 2's own contiguous layout — amendment 3 writes
`(pack("<Q", 1) + b"x") * n` and the cell grades `MODEL_OK/router-unloaded-autoload` (this seat
measured the amended fixture: 54 000 049 bytes → `-`). Fix: the interleaved layout, amendment 3.
Shown able to fail: the base-revision control at tip, re-run by this seat, grades the same fixture
`-` at both base and tip, so the cell is now decided by bytes and not by the probe's revision.

**M2 — a plan figure that no code path computes.** Class: *a stated figure the code does not
enforce* — the prose names a number the parser never derives, so the filing is true only of one
shape of file. Evidence: the frozen claim and the freeze-commit `SKILL.md` priced one tensor header
at **6** steps ("1 tensor header = 6 steps") and the ceiling at **833 333**. This seat instrumented
the probe's `need()` calls and counted them per header on files this seat built at four ranks: the
cost is `5 + nd` (name length + skip = 2, `nd` = 1, `nd` dims = `nd`, type + offset = 2), so 6 is the
`nd = 1` case only, and the ceiling is `(5 000 000 - 4) / (5 + nd)` after the four preamble steps.
The consequence is measurable, not cosmetic: this seat built a 700 000-header file at `nd = 3` and
graded it `-` (undecidable → loadable) at tip, while the same file at `nd = 1` grades `invalid` —
so the "700 000-tensor file decides" claim holds at rank ≤ 2 only, and a rank-3 file is exactly the
case the round was opened to decide. The freeze-commit SKILL row for `nd = 3` stated **625 000**;
this seat measured the boundary and it is **624 999** (625 000 grades `-`). Captured-by: wave-1 seat
`RV01StepBudget` (F2, F3), answered by amendment 2 and amendment 4. Fix: the `5 + nd` table with the
per-rank ceiling row, amendment 2, and the `nd = 3` row corrected to 624 999, amendment 4 — this
seat measured the boundary independently (`624 998 → ok`, `624 999 → ok`, `625 000 → -`) and the
amended depth counter now grades all five ranks arithmetically
(`DEPTH_AUDIT checks=14 mismatches=0 met=True` at tip, `checks=14 mismatches=14 met=False` at base,
both re-run by this seat).

**M3 — a disclosure that repeats a figure the same filing has already corrected.** Class: *the
registry row and the prose it grounds disagree* — the source row's teaching cell carries a figure
the corrected prose has already replaced, so a reader grounding from the row gets the falsified
number back. Evidence: `corpus/SOURCES.md` row S618 (filed at `58001b71`) still teaches "the header
cost a parser pays per tensor is five width-tagged fields over a name, so **6 read/seek steps per
header** is the budget against which MAX_STEPS is sized", and its anchor names line 690
(`struct ggml_tensor {`) while the quote sits at line 697. `SKILL.md` §Round 96 correction (amendment
2) says the same thing differently and correctly: `5 + nd`, six being the `nd = 1` case only. The
depth counter grades the prose's five ranks but reads S618 only for `status not rejected`, so no
instrument in the lane catches the row repeating the falsified figure. The probe's own comment
(`tools/kama-probe.sh` line 575) still says "The binding ceiling is 6 steps per tensor header", and
the disclosure counter's check (1) requires that exact string to be present — so the instrument
*requires* the falsified phrasing to stay. Captured-by: this seat's reading of the row against the
amended prose; not caught by any counter at tip (`DISCLOSURE_AUDIT checks=6 mismatches=0 met=True`).
Fix: none landed at tip — the S618 row's teaching cell, its anchor line, and the probe's comment all
still carry the pre-amendment figure. This is open at tip and is routed below.

**M4 — a receipt whose summary line reports a counter state it did not run.** Class: *a receipt
that misstates what ran* — the summary prints counts the run never produced, so a reader cannot
tell a measured verdict from a structurally red one. Evidence: the frozen base control
`.ufo/waves/round-96/controls/c1-base.out` was produced with `--skip-load`, and that branch of the
counter prints a hard-coded `mismatches=-2 positive_mismatches=-2 load_cells=0 load_stable=0`
together with `load_skipped=true`. The plan requires the base control to express the *discriminator*
("It must redden W11"), and a summary whose counts are a constant cannot express which cell
reddened; the per-cell lines carry it instead. The same receipt's `W12-strings` line reads
`ok=0 … MODEL_UNLOADED/router-model-invalid`, which is the M1 defect seen from the control side.
This seat re-ran the current counter against the base revision: with the amended fixture the base
run now reads `W11-700k ok=0 … MODEL_OK/router-unloaded-autoload` (the intended discriminator) and
`W12-strings ok=1 … MODEL_OK/router-unloaded-autoload` — i.e. the amended counter reddens exactly
W11 at base and nothing else, which is what the plan asked the control to show. Captured-by: wave-1
seat `RV01StepBudget` (F6) and amendment 2's own re-run; the amended control is present in the
working tree at this seat's reading (`controls/c1-base.out` shows `nat` and `load` passes), while the
committed receipt at tip is still the `--skip-load` one. Fix: amendment 2's `--allow-clock --burners 0`
re-run; the receipt in the working tree is not yet committed at tip.

**M5 — a filed source row the census counts but the round's own plan does not.** Class: *a
registry row named as evidence that the registry does not carry* — a claim cites a row id that
exists in the plan but not in `corpus/SOURCES.md`, so the census count and the plan's frontier-step
count disagree. Evidence: `plans/round-96-claims.md` names S619 as opened this round and as part of
C2's sourced claim, and its frontier step records "Rows: 357 → 359 at the time of writing". This
seat counted the rows on both blobs: base 357, tip 358. S618 is filed; **S619 is not**. The census
agrees (`kama rows 358`) and `validate` exits 0, because the census counts rows, not the plan's
arithmetic. Captured-by: this seat's row count and the plan's frontier-step line, compared; not
caught by the census. Fix: file S619 (digest and located quote measured by this seat, in the Gate
table above). Open at tip.

**M6 — a do-nothing control that cannot report a discriminator on this host.** Class: *a frozen
control whose named expectation is host-speed dependent* — the control refuses to evaluate unless
the measured pass is slower than a wall-clock multiple, so on a fast or idle host the instrument
answers "could-not-evaluate" instead of a verdict. Evidence: the counter's margin guard
(`tools/round96-router-budget.py`, `MARGIN = 1.25`, `BASE_WRAPPER = 60.0`) requires the W03 natural
pass to cost at least 75 s or it prints
`ROUTER_BUDGET96 could-not-evaluate: W03 natural pass … < 1.2 x 60s` and exits 2. This seat hit
that on an idle host: the natural W03 pass cost 52.7 s (and 59.6 s under 64 burners) and the run
exited 2 without grading any cell — on both the pre-amendment and the amended counter. The same
host-speed sensitivity then produced a wrong cell verdict in the lane's own M1 receipt: under the
synthetic load the `W02-slow-x8` cell graded `MODEL_OK/router-unloaded-autoload` where
`MODEL_UNLOADED/router-model-invalid` was expected (`.ufo/waves/round-96/measured/c1.out`, load
pass, `ok=0`), because the pass-level wrapper (`20 + 25 * npaths` seconds, `tools/kama-probe.sh`
line 871) truncated the listing under load. Amendment 3 acknowledges the guard as "a host-speed
parameter" and re-runs with `--slow-files 96`; the receipt names the count it used. Captured-by:
amendment 3's own measurement; the load-pass cell flip is visible in the M1 receipt. Fix: the
host-parameterised count, amendment 3. Open at tip: the receipt in the working tree is the one with
the load-pass flip, and the pass-level wall clock remains the lane's disclosed limit (r94 SC02 F4
family), routed again rather than claimed.

## Dispositions of the round-95 closure

- **Defect 1 (C1 counter has no cell exercising `MAX_STEPS`/`MAX_META`; W10 cannot observe the
  ctime memo key).** Closed: C1's counter adds W11-700k (700 000 headers, `nd = 1`, 4 200 004
  steps — over the old 4 000 000 budget, under the new 5 000 000), W12-strings (a 6 000 000-element
  string array past the step budget), and W10-rewrite keeps the ctime discriminator. This seat
  measured the amended fixture at both revisions: W11 grades `-` at base and `invalid` at tip, so
  the cell now carries the discriminator it claims.
- **Defect 2 (`--skip-load` misreports `load_cells=10`).** Closed: the counter prints
  `load_skipped=true load_cells=0 load_stable=0 load_note=skipped` and exits 1, so the predicate
  cannot be met without load evidence. This seat's `--skip-load` runs all end with that line.
- **Defect 3 (counter docstring says `20 + 15 * ncand`; the probe says `20 + 25 * npaths`).**
  Closed: the frozen counter's docstring states `20 + 25 * npaths` and the disclosure counter's
  check (2) compares the two.
- **Defect 4 (slow `/props` still decides the verdict — r94 SC02 F4).** **Carried, not claimed.**
  The pass-level wrapper is still a wall clock; the M6 finding above shows what that costs under
  load. Routed again, unchanged.
- **Defect 5 (`router-byte-decided` cites `f6325660` while the claim was filed at `c810f51e`).**
  Closed: the SCORECARD row now cites `c810f51e`, and the disclosure counter's check (3) requires
  the row's evidence commit to resolve as an object and to lie at or before the tip. This seat
  confirmed `c810f51e` resolves and is an ancestor of the tip.
- **Defect 6 (minor: fleet report path).** Operator note, not a lane deliverable.

## Carried, not claimed

- `round75-instruments` red (`APPEND_DEBT … bad_rows=19`, L0 r87/r89 open) — carried.
- `round78-instruments` live-reconcile red — the host's non-lane Ollama listener on 8080; operator-owned.
- The pass-level wall clock (r94 SC02 F4) — carried; see M6.
- **New at this seat's reading:** the S618 teaching cell and the probe's comment still carry the
  falsified six-steps figure (M3), and S619 is named but unfiled (M5). Both are open at tip and are
  for the L1 to land or route.

## Gate receipts and the L1's finding list

Measured by this seat at lane tip `20317286` (all re-runs against the committed counters; scratch
under `/fast/scratch/hyaku/kama-r96/SB01LessonDraft/`, removed on exit):

| Check | Command | Result |
|---|---|---|
| Depth counter at tip | `python3 tools/round96-depth-audit.py --repo . --rev HEAD` | `DEPTH_AUDIT checks=14 mismatches=0 met=True`, exit 0 |
| Depth counter at base | same, `--rev 5d43528b` | `DEPTH_AUDIT checks=14 mismatches=14 met=False`, exit 1 |
| Disclosure counter at tip | `python3 tools/round96-disclosure-audit.py --repo . --rev HEAD` | `DISCLOSURE_AUDIT checks=6 mismatches=0 met=True`, exit 0 |
| Disclosure counter at base | same, `--rev 5d43528b` | `DISCLOSURE_AUDIT checks=6 mismatches=3 met=False`, exit 1 |
| Step cost per header | instrumented `need()` counter over 1 000-header files at nd = 1,2,3,4 | 6, 7, 8, 9 steps/header ⇒ `5 + nd` |
| Per-rank ceiling boundary | graded 624 998/624 999/625 000/625 001 headers at nd = 3 | `ok`, `ok`, `-`, `-` ⇒ 624 999 decidable |
| nd = 1 boundary | graded 833 332 / 833 333 headers | `ok`, `-` ⇒ 833 332 decidable |
| W11 discriminator | 700 000 headers at nd = 1, graded at base and at tip | base `-`, tip `invalid` |
| W12 element layout | graded the contiguous and the interleaved layouts on identical bytes | contiguous `invalid`, interleaved `-` |
| Census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0; `kama rows 358` |
| Row count | `grep -c '^| S[0-9]'` on base blob and tip blob | 357 → 358 |

**Findings for the L1 (not landed by this seat, which never edits a tracked lane file):**

1. `corpus/SOURCES.md` row **S618** still teaches "6 read/seek steps per header", the figure
   amendment 2 falsified; its anchor names line 690 while its quote sits at line 697. The
   `SKILL.md` table says `5 + nd`. Either the row's teaching cell and anchor are corrected, or the
   row is re-scoped to the tensor descriptor it actually anchors. (M3)
2. `tools/kama-probe.sh` line 575 still says "The binding ceiling is 6 steps per tensor header", and
   `tools/round96-disclosure-audit.py` check (1) *requires* that string — so the instrument pins the
   falsified phrasing. Amendment 2 noted the probe comment was left as "the only rounded figure", but
   `6 steps` is not a rounding of `5 + nd`; it is a different formula. (M3)
3. **S619** (`gguf-py/README.md` @ b12177, sha256 `f759ed01…18af`) is named by the plan as opened and
   sourced this round but has no row; the census reads 358 where the plan's frontier step says 359.
   (M5)
4. The committed base control `.ufo/waves/round-96/controls/c1-base.out` is still the `--skip-load`
   receipt whose summary prints constant `-2` counts; the amended `--allow-clock --burners 0` re-run
   is in the working tree, not committed. (M4)
5. The M1 receipt in the working tree records a load-pass cell flip
   (`W02-slow-x8 ok=0 … MODEL_OK/router-unloaded-autoload`) and then a `FileNotFoundError` traceback
   — a receipt committed mid-run is exactly the round-95 M4 class; the receipt must not land until
   its producer exits and its summary line is present. (M6)
