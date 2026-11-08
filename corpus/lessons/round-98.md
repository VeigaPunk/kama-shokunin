# Round 98 — the overcharge window and the heading no counter read

Lane `kama`, round 98, L1 `KamaR98`. Base `681c80a4e3c745c22559f74b2c2a1917bdc66fc6` (round-97
closed `ok`: C1 calibration, C2 operability, C3 depth all verified; expansion unchanged,
quality/discernment improved — `corpus/lessons/round-97-verifier-spotcheck.md`). Claims: C1
calibration (the graded self-assessments match the repo, heading included), C2 operability (the
budget counter grades the +1/header overcharge probe the 17-cell set misses), C3 depth (the
step-budget boundary table grades the overcharge-window rows).

## Gate

Every row below was opened this round (2026-11-08), committed digest of the bytes fetched, not a
transcription.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S622 GGUF spec `gguf_header_t` @ `57e2c2ca` | **admit** (A, spec, mined) | https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md — 2026-11-08, sha256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` (43 175 B), HTTP 200 | "struct gguf_header_t {" (line 277; fields lines 277-300) | The header struct carries magic, version, tensor_count, metadata_kv_count — the four fields the probe prices as the preamble, so `preamble = 4` for the boundary table is grounded in the spec, not in parser trivia. |
| S623 GGUF spec Naming Convention @ `57e2c2ca` | **reject** (spec, C-class lead only) | Same URL, 2026-11-08, same digest | "It is not intended to be perfectly parsable in the field due to the diversity of existing gguf filenames." (line 23) | The section is filename provenance, not header layout; it grounds no step cost. Flip: the section states header field order and widths. |

Registry changes: S622 (admit), S623 (rejected row). No existing row's `status`/`recheck`/`used-by`
changed; both rows carry the same URL as S620 with a different anchor (standing W04 duplicate-URL
warning, cross-scope, same as the round-97 S619 row). Measured: `git diff 681c80a4 HEAD --
corpus/SOURCES.md` is the two inserted rows.

Census before → after: 361 → 363 rows,
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
exit 0 at round start (`.ufo/waves/round-98/controls/census-start.out`) and at round end
(`controls/census-end.out`); tiers measured with the census at HEAD (361 rows: A 344, B 11, C 6;
mined 324, queued 8, rejected 29) against base (361: A 344, B 11, C 6; mined 324, queued 8,
rejected 29).

Assimilation: none from `merge/kama/` this round (the package holds no step-budget theme; the
campaign rows are not adopted as-is per §10). `considerthese/2026-11-08.md` proposal 1 (the
gate-receipt continuity check: report the age in rounds of the newest full pre-report gate run)
is mined as a lesson note below, not as a package row.

## Mistakes

**M1 — the round-97 audit never read the section heading it graded the body of.**
Class: `vacuous`. Evidence: `tools/round97-self-assessment-audit.py` check 16 reads
`section(skill, "### Round 97 correction")`, which collects lines from `start + 1` — the heading
line itself is outside the slice, so the live "the three graded forgeries" heading passed while
the body said four (`.ufo/waves/round-97/w1/out/RV01SelfAssess/` §2.1; `plans/round-97-amendment-2.md`
A corrected the body but not the heading). Captured-by: the round-97 wave (RV01SelfAssess), not the
round-97 counter. Fix: `tools/round98-self-assessment-audit.py` check 19 parses the heading's
count word and requires it to equal the counter's parsed mutant count (five). Shown able to fail:
at base it prints `mismatches=4` (heading, counts, W18/W19, overcharge) with exit 1
(`controls/c1-base.out`), at M1 `mismatches=0` (`measured/c1.out`).

**M2 — a round-98 fixture cell sets was dropped by a patch that re-anchored past it.**
Class: `vacuous`. Evidence: the first r97set control receipt printed `cells=16`, not 17 —
`W01-slow-x1` had been dropped from the cells list when the W18/W19 rows were inserted (the
`cells += [` list previously headed by W01). Captured-by: the counter's own control run (the
`cells=` count in the summary line). Fix: W01 restored as the first slow-gated cell; the re-run
prints `cells=17 … survived=1` (`controls/c2-legacy-mutants.out`). Shown able to fail: the 16-cell
receipt stands in the wave dir as the red evidence.

## Routed-defect answers

- **Round-97 carried disclosures (the closure's routed-defects list).** All six stand as filed and
  are carried again this round, not claimed: `round75-instruments` red (L0 r87/r89 open), the
  `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080 (re-checked
  this round: still listening), the slow `/props` verdict (r94 SC02 F4), the pass-level wall-clock
  wrapper (SC01), the ctime memo shape (unobservable, disclosed in the plan), and the round-97 C1
  checks 13–14 receipt-needle limit (RV01 §2.10).
- **Round-97 wave RV03 F5 (the +1/header overcharge window).** Answered by C2 (W18/W19 + the
  `overcharge` mutant) and C3 (the two boundary rows inside the window).

## Spot-check

Non-author closure pending; this lesson is the author's Gate/Mistakes record.

**Lesson note (considerthese proposal 1, 2026-11-08).** The newest full pre-report gate run is
round 94 (`.ufo/waves/round-94/measured/gate-final.out`); rounds 95–97 filed `prefile-gate.out`
only. The continuity check proposal is a pointer, not evidence; the gate continuity this round is
recorded here for the closure to verify.
