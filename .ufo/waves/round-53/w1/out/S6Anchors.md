# S6Anchors — round 53 mistake mining, the S505 class (wrong line anchor)

**Verdict: 1 of 30 sampled `path:N` / `path:N-M` citations is a wrong anchor (3.3%) — `SKILL.md:533` at SCORECARD.md:707 names the instrument-registry table header; the claimed check.py grading row is at SKILL.md:535; 29/30 hold at the commit their citing sentence was written.**

- Sample unit: 30 of the 86 backticked line-anchored citations in `SCORECARD.md` and
  `SKILL.md` at the lane build commit `c22602bd8d83ab26349d1087e916ca537ee4f9d1`
  (full list in `out/S6Anchors/anchors.json`; per-item trace in `out/S6Anchors/trace.json`).
- Method, per seat spec: for each citation, the commit the citing sentence was written is
  `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -S'<anchor>' --format=%H -1 -- <citing file>`;
  the cited file is then opened at that commit (`git show <commit>:<path>`) and the cited
  line(s) judged against the citing sentence. Fleet paths (`.ufo/reports/...`, `MISSION.md`)
  were resolved in the fleet repo `/home/vgpnk/Projects/shokunin` at the commit named in the
  citing row, or at the fleet commit contemporary with the writing lane commit
  (`git log --until=<write timestamp> -1`). Host paths were opened on disk.
  Because the anchor string often survives many round rewrites, the pickaxe's *newest* hit is
  the commit that (re)wrote the current sentence instance; where the semantic author differs
  (round-45 restore `82b5e9d33a`), both were checked. All commands run read-only against the
  lane and fleet; no counter was executed (this seat mines citations, it does not re-grade).

## The wrong case (1/30)

`SCORECARD.md:707` → `SKILL.md:533` (detail in `out/S6Anchors/wrong-anchor-case.md`,
proposed diff in `out/S6Anchors/proposed-fix-SCORECARD-707.diff`):

- Sentence (at `c22602bd`, and as re-appended by `82b5e9d33a`):
  "**C1 calibration (lowest axis):** `SKILL.md:533` claimed check.py "grades verdict, reason,
  exit and drift" and maps harness errors to exit 2; no detector could fail any of those
  gradings (round-16 mutants 5/5 survived) ..."
- Evidence:
  - `git show 82b5e9d33a:SKILL.md | sed -n '533p'` →
    `| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |`
    (the table header). The claim is the "Probe verdict stub matrix" row at line 535 of the
    same commit, and of `c22602bd`.
  - `git show c22602bd:SKILL.md | sed -n '533p;535p'` → header at 533, check.py row at 535 (exit 0).
  - The sentence was correct when first authored: at `54a29268e2` (round-17) `SKILL.md:533`
    was the check.py row. SKILL.md then gained two lines above the table; by `0718b6ab`
    (parent of the restore) 533 was already the header, and the round-45 restore re-appended
    the sentence with the stale `533`.
- Proposed fix: `SKILL.md:533` → `SKILL.md:535` at SCORECARD.md:707 (diff in out dir).

## The 29 correct cases (grouped)

- Self-claim rows, fleet reports at the commit the row itself names — all hold:
  - `SCORECARD.md:2357` `.ufo/reports/round-10/kama.md:93` (fleet `b0fd7b7f`) → "Discernment:
    unchanged pending outside check." matches the row's self verdict "unchanged".
  - `SCORECARD.md:2369` `.ufo/reports/round-29/kama.md:136` (fleet `b0fd7b7f`) → "expansion:
    unchanged" matches self "unchanged".
  - `SCORECARD.md:2420` `.ufo/reports/round-24/kama.md:63` (fleet `6105c587`) → the report's
    C1 section header "C1 calibration7 → 7 — original claim not achieved/unprovable in full",
    the round-24 C1 self-verdict the row summarizes as "mixed".
  - `SCORECARD.md:2423` `.ufo/reports/round-40/kama.md:14` (fleet `6105c587`) → "- **C1 —
    unverified:** ... schema-valid registry content cannot satisfy the frozen predicate", the
    round-40 C1 self-verdict the row records as "not-met".
- Outside-spotcheck rows, lane reports at the commit the row names — all hold:
  - `SCORECARD.md:2357` `corpus/lessons/round-10-verifier-spotcheck.md:17` (lane `9d9cc93e`)
    → line ends "...quality improved (anchors corrected; KQ6–KQ10), discernment improved.",
    matching the row's outside verdict "improved".
  - `SCORECARD.md:2369` `corpus/lessons/round-29-verifier-spotcheck.md:69` → "expansion:
    improved — independent grade per LEARNING.md's observable ...".
  - `SCORECARD.md:2420` `corpus/lessons/round-24-verifier-spotcheck.md:14` → "The full
    original C1 calibration claim is **unprovable / not achieved**", matching outside
    "unprovable".
  - `SCORECARD.md:2423` `corpus/lessons/round-40-verifier-spotcheck.md:49` → "Ruling:
    **unprovable.**", matching outside "unprovable".
- Prose citations — all hold at the writing commit:
  - `SCORECARD.md:6` `MISSION.md:29` (fleet `a714799f`, the fleet commit at the sentence's
    write time 2026-10-27 02:31:52 -0300) → line 29 reads
    `kama: { cwd: kama-shokunin/, axes: "operability + freshness (local model serving/endpoints)" }`,
    matching "still says operability + freshness".
  - `SCORECARD.md:1402` `.ufo/reports/round-25/kama.md:120-129` (fleet `7a79b894`, at write
    time 2026-10-27 01:56:49 -0300) → the range holds "quality: unchanged ... discernment:
    unchanged", matching the parenthetical.
  - `SCORECARD.md:979` `corpus/lessons/round-18.md:474-480` → the "Agreement qualification
    for 'they agree'" paragraph (15 item outcomes, counts, frozen witnesses, 42 run-status
    tuples, not entire documents), matching the sentence.
  - `SCORECARD.md:996` `corpus/lessons/round-19-verifier-spotcheck.md:160-172` → "## Trend
    verdicts" with the expansion-improved-for-capability-row-not-source-growth distinction
    the sentence cites it for.
  - `SCORECARD.md:1003` `tools/gguf-identity.py:32-35` → `MAX_STR_LIMIT = 1024 * 1024` (=
    1,048,576), matching "--max-str 1,048,576".
  - `SCORECARD.md:1428` `count-c1.py:384` → the round-26 counter at
    `.ufo/waves/round-26/count-c1.py` line 384, `c["e_not_echoed"] = sig not in req_bytes`
    — the stored-request-text echo test the sentence describes ("read stored request text").
  - `SCORECARD.md:1579` `corpus/lessons/round-2.md:49` →
    `` `bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0` `` — the RESULT span that is
    the subject of the ConfirmM02 correction sentence.
  - `SCORECARD.md:1890` `SCORECARD.md:1791` → at the sentence's author commit `88331197`
    (round-33), line 1791 IS the round-32 C2 row ("each fixture exits 1 with its named
    defect under v2 (`c2/controls/*-v2.out`)..."), and at `dc4258bd` (the commit the sentence
    says the row was written) 1791 is the same row. Correct at write time (see drift note).
  - `SCORECARD.md:2173` `corpus/SOURCES.md:225` → the S472 own-work SGLang release-tag
    inventory row, matching "`S472` is round 38's own-work SGLang tag-inventory row".
  - `SCORECARD.md:2482` / `2483` `corpus/lessons/round-29-verifier-spotcheck.md:32` /
    `round-30-verifier-spotcheck.md:41` → "+65/−0 (append-only)" and "0 removed lines ...
    (append-only True)", matching "read a round's SCORECARD diff as +65/−0 / '0 removed
    lines' and called that append-only".
  - `SCORECARD.md:2540` / `2627` / `2633` `SCORECARD.md:6` → at the writing commit
    `4340cf2f68` line 6 declares both quoted promises ("The `## Axes` table, §Planned,
    §Retired, §Saturation and §Capabilities below are re-derived from the tree by
    `tools/round42-selfdesc-reconcile.py`..." and "the round-5 banner and the head sections
    they replace are kept verbatim under §Historical head sections"). Line 6 at `c22602bd`
    still carries both sentences.
  - `SCORECARD.md:2560` / `2605` `tools/append-only-audit.py:102` →
    `dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]`,
    the filter named in the sentence.
  - `SCORECARD.md:2567` / `2605` `tools/round46-append-audit-check.py:115` → the identical
    filter line, matching "carries the same filter".
  - `SCORECARD.md:2780` `corpus/QUALITY.md:143` → the KQ26 row ("Corrections to filed
    lessons, reports and append-only records are appended with the superseded text/revision
    named"), matching "re-anchored at integration to corpus/QUALITY.md:143, KQ26".
  - `SCORECARD.md:2837` `corpus/README.md:1239` → "Lesson files under `corpus/lessons/` are
    append-only as the `A-corr` contract row declares ...", matching "lessons row
    re-anchored to corpus/README.md:1239".
  - `SKILL.md:1094` `corpus/knowledge/cross-lane-scope.md:28` → "**Kumitate** owns how a
    dispatch/alias resolves; **kama** owns what the resolved local baseURL serves", matching
    "how an omp dispatch or alias resolves ... is kumitate's".
  - `SKILL.md:1343` `tools/gate-registry-check.py:15-16` → the docstring's gate definition
    ("A path is ``registered`` iff it occurs in a cell of / a row of such a table"), matching
    "The gate definition is the docstring 'Contract' at tools/gate-registry-check.py:15-16
    (S194)".
  - `SKILL.md:279` `the-tick.machine.json:16` → the host config at
    `~/Projects/ufo-fsd-alpha/config/the-tick.machine.json` line 16 is
    `"endpoint": "http://127.0.0.1:34113/v1/chat/completions"`, matching "hit 34113 with
    MODEL_OK".
  - `SKILL.md:89` `~/.config/opencode/opencode.json:158` → the sentence itself records the
    evidence ("still reads `http://localhost:8080/v1` at mtime 2026-09-28 16:46:43"); the
    host file matched that mtime claim when written. The file has since been rewritten
    (2026-10-24, now 4 lines) — see drift note; not a wrong anchor at write.

## Notes for the integrator (not counted in the 3.3%)

- Correct-at-write, **stale at the tip** (the C2 counter only checks file length, so these
  pass it; they are drift, not S505-at-write):
  - `SCORECARD.md:1890` cites `SCORECARD.md:1791` — the round-32 C2 row has moved to line
    1844 at `c22602bd`; line 1791 is now blank.
  - `SCORECARD.md:1578-1579` cites `SCORECARD.md:1490-1493` for the round-29 appended note —
    that note now sits at ~1543 at `c22602bd`.
  - `SKILL.md:89` cites `~/.config/opencode/opencode.json:158` — host file rewritten
    2026-10-24; the pinned line no longer exists (the sentence's own mtime evidence makes
    the at-write reading verifiable, so this is host drift, not an authoring defect).
- Wrong-anchor rate in this sample: **1/30 (3.3%)**. The single case is off-by-two (table
  header vs the row two lines below), the mildest S505 shape; no wholly-wrong-line case
  (the round-52 R1 "491 not 431" shape) was found in the sample.
- Fleet-path citations in the claim-outcome table carry their fleet commit inline
  (`fleet b0fd7b7f` / `fleet 6105c587`); resolving at those commits, all sampled rows hold.

## Evidence inventory (out/S6Anchors/)

- `anchors.json` — all 86 extracted citations (source file:line, citation, citing line).
- `trace.json` — per sampled citation: pickaxe commit list, writing commit, cited lines at
  the writing commit, file length.
- `wrong-anchor-case.md`, `proposed-fix-SCORECARD-707.diff` — the single defect with
  proposed fix.

No counters were run; no lane or fleet file was modified; scratch was `/fast/scratch/hyaku/kama-r53/S6Anchors` (removed after the report was written).
