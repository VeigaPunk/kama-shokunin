# Round 97 — the self-assessment the lane repeats, and the probe forgeries the old cell set cannot see

Lane `kama`, round 97, L1 `KamaR97`. Base `40763bd2ca1e3f99881247eaa9f5e3ef3b596653` (round-96
closure rejected-honest-stop). Claims: C1 calibration (the lane's graded self-assessments match the
repo), C2 operability (the budget counter grades four probe forgeries the 13-cell set misses), C3
depth (the step-budget boundary table).

## Gate

Every row below was opened this round (2026-11-08) and re-fetched; the digest is the `sha256sum` of
the bytes fetched, not a transcription.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S620 GGUF specification `docs/gguf.md` @ ggml `57e2c2ca` | **admit** (A, spec, mined) | https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md — 2026-11-08, sha256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` (43 175 B) | "uint64_t dimensions[n_dimensions];" (line 313; "Currently at most 4" line 310) | The tensor-info struct is five fields — `name`, `n_dimensions`, `dimensions[n_dimensions]`, `type`, `offset` (lines 305-325) — with one dimension entry per rank, which is why a header costs `5 + nd` reads and why the ceiling is per rank. |
| S621 `ggml/include/ggml.h` @ b12177, corrected reading of S618 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h — 2026-11-08, sha256 `590e00a522b8791235353a8c7388d67ff2fe929554f1834c58528b82afd67392` (119 369 B) | "nb[0] = ggml_type_size(type)" (line 697; "int64_t ne[GGML_MAX_DIMS];" line 695) | Supersedes S618's `teaches` cell, which stated "6 read/seek steps per header": `ne` is one element count per rank, so the cost is `5 + nd`. S618's anchor "line 690" was the struct header; the fields are at 695-697. |
| S619 `gguf-py/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/gguf-py/README.md — 2026-11-08, sha256 `f759ed01b8899c392cee7f1bc9012356090dd46014898c2cface1cca5f1e18af` (3 339 B) | "This is a Python package for writing binary files in the [GGUF](https://github.com/ggml-org/ggml/pull/302)" (lines 3-4) | The page documents the Python writer, not the file layout the probe parses; it grounds no step cost. Flip: the page states the header field order and widths. |
| `llama.cpp` `docs/gguf.md` @ b12177 | **reject** (path absent) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/docs/gguf.md — 2026-11-08 | HTTP 404 (14 B body, sha256 `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed`) | The spec moved to the ggml repository; S620 is the live location. Flip: a llama.cpp `docs/gguf.md` appears at a pinned tag. |

Registry changes: S619 (rejected row, replacing round 96's prose-only rejection), S620 (admit),
S621 (append-only correction of S618). No existing row's `status`/`recheck`/`used-by` changed; S618
stays `mined` as history and S621's `teaches` opens `supersedes S618 —` (CORPUS.md rule 2).
Measured: `git diff 40763bd2 HEAD -- corpus/SOURCES.md` is 3 insertions and 0 deletions.

Census before → after: 358 → 361 rows,
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
exit 0 at round start (`.ufo/waves/round-97/controls/census-start.out`) and at round end
(`controls/census-end.out`); tiers measured with the census at HEAD (361 rows: A 344, B 11, C 6;
mined 324, queued 8, rejected 29) against base (358: A 342, B 11, C 5; mined 322, queued 8,
rejected 28).

Assimilation: none — `considerthese/2026-11-07.md` proposal 3 (a file-identity memo is not frozen
without a mutation-control receipt) is mined as QUALITY KQ152, not as a package row; no
`merge/kama/` theme was adopted.

## Mistakes

**M1 — the C3 counter required the false sentence it was supposed to catch.**
Class: `number-drift`. Evidence: `corpus/lessons/round-96-verifier-spotcheck.md` ("the instrument is
green **because** the falsified sentence is present") and `tools/round96-disclosure-audit.py:57-60`
(`"6 steps per tensor header" not in probe -> mismatches += 1`). Captured-by: the round-96 closure
spot-check (non-author), not the round's own counter. Fix: `tools/round97-self-assessment-audit.py`
derives every ceiling from `MAX_STEPS` and the rank and rejects the constant-6 sentence, a false
"binding" line, and (amendment 2) a parser whose tensor loop does not charge the declared sites.
Shown able to fail: at base it prints `mismatches=10` (v2) / 9 (v1), at the measured commit
`mismatches=0` (`controls/c1-base.out`, `measured/c1.out`).

**M2 — a fixture that could not grade its own design, found by the mutant control.**
Class: `vacuous`. Evidence: the first `maxmeta.gguf` wrote the KV value as `struct.pack("<II", 8, 0)`
— a GGUF string has no element-type field — so the length read landed one field early and the probe
graded `invalid` at the size guard; the `maxmeta` mutant then printed `caught=0` while both probes
agreed. Captured-by: the counter's own `--control --expect caught` mutant run (it refused to agree).
Fix: the KV is `type u32` then `u64 length` (`tools/round97-router-budget.py:243-260`), and the
committed receipt prints `mutant=maxmeta … cell_ok=0 … caught=1` (`controls/c2-new-mutants.out`).
Shown able to fail: `controls/m2-red-maxmeta.out` grades both layouts — the pre-fix layout makes
the real probe and the `MAX_META`-100 MiB mutant agree (`MODEL_UNLOADED` both), while the fixed
layout flips the mutant (`MODEL_UNLOADED` vs `MODEL_OK`), so the cell discriminates only after the
fix.

**M3 — the prefile ledger's coverage was per claim, not per claim-finding pair.**
Class: `vacuous`. Evidence: `corpus/lessons/round-96-verifier-spotcheck.md` step 2b ("files no row
for the C3 × RV01 F2 wording falsification it could have filed"). Captured-by: the round-96
closure, step 2b. Fix (landed with this round's filing): `.ufo/waves/round-97/claim-falsification.tsv`
names, for every attack seat, the claim(s) its artifact attacks, and a row for every claim an
artifact's finding falsifies; the gate `prefile-falsification.py --lane kama --round 97` prints
`PREFILE-FALSIFICATION: pass` in the report.

## Routed-defect answers

- **Round-96 routed defect 1 (the false disclosure and the literal-presence counter).** Both
  disclosures are corrected append-only (S621 supersedes S618; the probe comment states `5 + nd` and
  the five ceilings), and the new audit grades the arithmetic, not the string.
- **Round-96 routed defect 2 (`SHONEN` re-filing).** The round-97 report carries one line per
  `SHONEN.md` box.
- **Round-96 routed defect 3 (identity revision).** `SCORECARD.md`'s round-96 header names the
  measured revision `f175a902`, and check 12 verifies that `tools/round96-router-budget.py` at
  `f175a902` is byte-identical to the graded file. The round-96 docstrings keep their freeze-time
  sentence as history; the binding statement is the SCORECARD-named revision.
- **Round-96 routed defect 6 (ledger width).** See M3.
- **Round-96 routed defects 4/5/7 (report-correction discipline, seat accounting, carried reds).**
  Round 97 files a fresh report with the 13 seats enumerated from `w1-results.json`; the carried reds
  stay disclosed, not claimed.

## Spot-check

Non-author closure pending; this lesson is the author's Gate/Mistakes record.

**M4 — a mutant patch that conditions on the counter it mutates is a fixed point.**
Class: `vacuous`. Evidence: the shipped `nopreamble` patch was `steps[0] += 0 if steps[0] < 4 else 1`
— with `steps[0]` starting at 0 it never increments, so the "preamble drop" charged **zero** steps
and was an `undercharge`-class probe (its receipt reddened W14/W15/W17, not W17 only). Captured-by:
RV02BudgetCells F2 and MT01Forgeries F2, independently. Fix: the patch counts calls in a separate
list (`calls[0] += 1; steps[0] += 0 if calls[0] <= 4 else 1`); shown able to fail: the true drop reds
only W17 (`cells_ok=3`, `controls/c2-new-mutants.out`), and the old patch's collateral reds are the
counterexample.
