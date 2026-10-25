# ScribeLesson — kama round 37, w1: lesson skeleton

Seat: `L1Kama37.WidespreadGoat` (scribe, leaf). Wrote only this report and the draft under its seat
directory. No corpus file was written; no git/jj mutation; no tool installed or upgraded.

## Behavior

Drafted the round-37 lesson skeleton with the four requested sections, in the r36 lesson's style:

- `## Corrections — round 37` — four single-line rows keyed `R36-D1`, `R36-D2A`, `R36-D2B`,
  `R36-D3`, each carrying facts re-derived from the cited bytes this round.
- `## Gate` — three candidate entries, seven candidate registry rows with URL, access date
  (2026-10-25), HTTP status/bytes where a receipt exists, and located quotes all ≤25 words; three
  staged reject slots (reason + flip as `<PLACEHOLDER>`); the exact README coverage heading and a
  three-row coverage table with `<covers>` placeholders.
- `## Mistakes` — one `id-drift` row, evidence `corpus/lessons/round-36-verifier-spotcheck.md` §6
  item 2, captured-by `QUALITY.md`, fix `KQ46`.
- `## Wave evidence` — frozen preregistration, both do-nothing controls with their exact output
  lines and exits, round-start census (94 lines: 93 `W04` + one `kama<TAB>ok<TAB><path>`), wave-1
  spec/run counts, the seven source-reopening receipts, assimilation scratch, the counting-tip
  hazard, and the report-side D3 obligation.
- Plus a clearly marked `## Draft notes — remove before landing` with the placeholder inventory and
  build dependencies.

No real corpus path (`corpus/lessons/round-37.md`) exists or was touched.

## Gates exercised

1. **Draft vs the frozen C1 counter (simulated tip facts, not a real tip).** I imported
   `tools/round37-statement-audit.py` and called its pure `score()` on the draft bytes with
   `census_tip` = the on-disk `.ufo/waves/round-36/census-end.out` (12426 bytes),
   `census_base = None` (base 6a4afdfe has no such path), `exitcodes` and `seatlogs` read from the
   `master:` blobs, and `lesson_blob`/`report_blob` set to the tool's pinned constants. Result:
   `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True`. All four
   `forbidden_in` checks return `None`. This is a content falsifier for the draft; the shipped
   counting command was not run at a real commit.
2. **Pinned blobs.** `git rev-parse master:corpus/lessons/round-36.md` =
   `6fb1ec151407b1207e8d540e83ba87d6a909d8ea` and fleet
   `HEAD:.ufo/reports/round-36/kama.md` = `8b7408e663c1b1ea95826d240f498637f1961604`; both match the
   counter's constants. Lane `master` = `6a4afdfe` = base.
3. **Quote counts re-derived by whitespace split** (not trusted from receipts): S330 20, S333 12,
   S334 20, S335 10, S346 5, S347 17, S363 13 — all within the 25-word bound. The first draft said
   11 for S335; the re-derivation returned 10 and the draft was corrected before scoring.
4. **Staged-id facts re-derived** from `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md`
   (read-only): S371's URL names `native_api.mdx`; S366 is the AWS SageMaker page; S364, S365, S377,
   S396 are the `http_server.py` rows. The staged
   `merge/kama/amendments/corpus/knowledge/endpoint-health-probe-conventions.md` `source:` lines are
   S332, S336, S337, S338, S339 — the five-id correction is right.
5. **Base-registry absence.** `git show 6a4afdfe:corpus/SOURCES.md` has no row for S330, S333, S334,
   S335, S346, S347 or S363. `ExecCollision.md` reports lane ids 203, staged ids 142,
   `comm -12` empty, and zero URL matches in lane SOURCES for all seven.

## Findings

1. **D1 is build-blocked on one untracked receipt.** `.ufo/waves/round-36/census-end.out` is absent
   at base and at `master`, and untracked in the lane tree, but exists on disk (12426 bytes) ending
   `kama<TAB>ok<TAB>/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. The correction
   row can only hold if the round-37 counting tip's tree carries that file. The r36
   `seat-exit-codes.json` and both d3 seat logs already resolve at `master:`, so D3 has no such
   dependency.
2. **Counting-tip hazard.** Lane `HEAD` is detached at `873c5d77`, the last commit of a four-step
   r36 sandbox mutation series; `873c5d77:corpus/lessons/round-36.md` is `0418795f…`, not the pinned
   `6fb1ec15…`. `master` is `6a4afdfe`; jj `@` is `7e4b6071` with the clean bytes. The tip must be a
   commit carrying the clean r36 blobs, the census, and the round-37 bytes (also re-derived in
   `ReviewAppend.md`).
3. **A real constraint conflict, recorded verbatim.** The frozen C1 counter's `forbidden_in` for
   `R36-D3` rejects any row containing `rc=0` or `rc=143`, while spot-check §6 item 3 routes
   "Name them, with their last error text, in the lane's next report." The draft therefore names
   only the two `rc=1` seats in the lesson row and assigns the full three-class wave split to the
   round-37 fleet report (matching `CriticD3Accounting.md` §0: both artifacts are required).
4. **D3 row text.** Both seat logs carry the identical last error
   `error: failed to run prompt: provider.rate_limit: 429 Rate limit reached for requests`;
   `RevQ206`'s log records an S206 fetch at HTTP 200 before the error and its report file exists.
5. **Gate quotes are drawn from this round's receipts**, not from the staged entry text: S330
   (`Chunked prefill…`, 20 words), S333 (12), S334 (20), S335 (10), S346 (5), S347 (17), S363 (13).
   S346 is marked tier B at most; S333 is marked as carrying no version pin.
6. **Coverage-block placement.** C2 counts names only inside `## Coverage map — round 37 addition`
   in `corpus/README.md`; the skeleton carries the exact heading and the three entry names but not
   the final `covers` prose.

## Placeholders left (all marked `<...>` in the draft)

Author/L1 prose; ScribeEntries draft paths (seat had not landed at write time); three coverage-map
`covers` cells; three reject verdicts and flips from `CriticReject.md`; final KQ46 text
(`ScribeKQ46.md`); L1 Claims prose and control receipts; report-side D3 wording.

## Touched surfaces / out of scope

- Written: `.ufo/waves/round-37/w1/out/ScribeLesson/round-37-skeleton.md` (draft) and this report.
- Read-only: lane corpus files, tools, wave receipts; the staged package; read-only `git show`/`git
  rev-parse`.
- Not done (by assignment or bounds): no `corpus/lessons/round-37.md`, no `corpus/README.md` edit,
  no `corpus/QUALITY.md` edit, no `corpus/SOURCES.md` edit, no commit/push/jj mutation, no census
  copy, no campaign tool, no subagent. No installs.

## Artifacts

- Draft: `.ufo/waves/round-37/w1/out/ScribeLesson/round-37-skeleton.md` — 16079 bytes, 123 lines,
  sha256 `bb1c734436fd0c0bc18545861b0672dc52600306dd2df84f0d78a620486406e6`.
- This report: `.ufo/waves/round-37/w1/out/ScribeLesson.md`.
- Receipts relied on: `FetchS330.md`, `FetchS333.md`, `FetchS334.md`, `FetchS335.md`, `FetchS346.md`,
  `FetchS347.md`, `FetchS363.md`, `ExecCollision.md`, `ReviewAppend.md`, `ReviewFrontier.md`,
  `CriticD3Accounting.md` (all under `.ufo/waves/round-37/w1/out/`), plus
  `.ufo/waves/round-37/{preregistration.json,controls/*,census-start.out,assimilation/*}`.
