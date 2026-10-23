ATTACK routed defects 2, 4 and 6 as applied: holds

Seat: KamaR26.ReviewerRoutedApplied (wave 2 FALSIFY, round 26). Read-only. No
llama-server started, frozen counter not run, no installs.

Scope: compare the appended text in `corpus/QUALITY.md`, `corpus/lessons/round-25.md`,
`corpus/knowledge/context-capacity.md` and `SCORECARD.md` with the routed text in
`corpus/lessons/round-25-verifier-spotcheck.md:203-232`. Check every cited line against
f4066979096e3452ae731c0e09e50155c6d8258a and `.ufo/waves/round-25/final/raw/`. Check that the
change from 1560e4d8 to f4066979 adds bytes and changes none.

## 1. Append-only check (all four files): holds

Command (lane root, GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE unset):
`git diff --stat 1560e4d83f42b04f40336357de6f9637eafa0f4b f4066979096e3452ae731c0e09e50155c6d8258a -- corpus/QUALITY.md corpus/lessons/round-25.md corpus/knowledge/context-capacity.md SCORECARD.md`
gave `4 files changed, 83 insertions(+), 0 deletions(-)`, exit 0.

Byte-prefix check: for each file, `git show <rev>:<file>` went to scratch, then
`cmp -n <base bytes> base tip`.

| File | base bytes | tip bytes | `cmp -n` exit | diff `-` lines |
|---|---|---|---|---|
| corpus/QUALITY.md | 43329 | 43874 | 0 | 0 |
| corpus/lessons/round-25.md | 12096 | 12895 | 0 | 0 |
| corpus/knowledge/context-capacity.md | 16434 | 17498 | 0 | 0 |
| SCORECARD.md | 94838 | 97484 | 0 | 0 |

Each tip file begins with every byte of its base version. Every change is an
append at the end of the file.

## 2. Defect 2, part F1 (KQ36 "landed tip" qualification): holds

- Routed text (spotcheck:208-210): "defines 'landed tip' (bytes of the measured
  source and the instrument identical to the landing commit, and any later change
  disclosed)".
- Applied text (QUALITY.md, appended section "Round 26 qualification — KQ36"): the
  measured source bytes and the instrument bytes each match the landing commit. An
  earlier run counts only when those bytes are identical at the landing commit. Any
  later change is disclosed with the revision it first appears in. A run against
  different bytes is not a landed-tip measurement. This matches the routed text
  clause for clause.
- Its label "(F1)" matches spotcheck:168 (`**F1, "landed tip".**`).

Observation, not a defect. The qualification follows the routed text literally, so
it is stricter than the F1 narrative at spotcheck:168-172. That narrative accepts the
round-25 run at 1fc41e34 even though the instrument "differs only in its docstring".
Under the appended rule, a docstring-only instrument change disqualifies a run. The
wording also leaves one point open: "any later change … disclosed" can only mean
changes after the landing commit, because identity is already required before it.
[INFERENCE] Nothing landed depends on that reading.

Self-application check (the rule applied to round 26's own receipts):
- `.ufo/waves/round-26/final/c1-tip.out` and `c2-kq36-tip.out` both record
  `tree=7e5ff9b5454dd27f0520cb36a3cbc3a995e48162`. The landing commit is f4066979.
- `git diff --stat 7e5ff9b5 f4066979 -- SKILL.md corpus registry .ufo/waves/round-26/sources .ufo/waves/round-26/count-c1.py`
  printed nothing, exit 0.
- `git diff --stat 7e5ff9b5 f4066979 -- .ufo/waves/round-25/count-c2.py .ufo/waves/round-25/final tools/kama-context-capacity.py`
  printed nothing, exit 0.
- The inputs read by `count-c1.py` are `SKILL.md`, `corpus/SOURCES.md`, the registry,
  the source directory, and `git show`/`git grep` at BASE (count-c1.py:58, 74, 108-120,
  325-333). Their bytes are therefore identical at the landing commit, and both
  receipts qualify as landed-tip measurements under the new text.
- Gap (low, still open before closure): no landed text records this identity.
  SCORECARD.md:1319 (C1 row, "Measured commit" cell) says "the landed lane tip named
  in the round report". SCORECARD.md:1332 says "KQ36 re-run at the landed tip is in
  the round report". `/home/vgpnk/Projects/shokunin/.ufo/reports/round-26/` holds no
  `kama.md`; I listed it at 2026-10-23 ~04:00 UTC and found only chousa, kagi,
  kaidoku, kake and kengaku files. Both cells therefore point to a document that
  does not exist yet.
  - Smallest correction: the round-26 report (or the SCORECARD "Measured commit"
    cell) names receipt tree 7e5ff9b5 and landing commit f4066979, and quotes the two
    empty `git diff --stat` commands above.

## 3. Defect 2, part F2 (round-25 lesson erratum): holds

- Routed (spotcheck:210-212): append an erratum to §Mistakes row 2 stating that the
  SKILL registry row does not say M17 survives.
- The quoted clause is exact. round-25.md:49 (Fix cell) reads "the instrument
  docstring and SKILL registry row now say M17 survives and why". The erratum at
  round-25.md:138-139 quotes the same bytes.
- SKILL.md M17 mentions: `git show <rev>:SKILL.md | grep -n M17` returns only lines
  883 ("…M17 follows the current local-store spelling.") and 889 ("M11 and M17
  re-anchored; M33 is the second call site of the M17 refusal"). The result is
  identical at a23c0e04 (the commit the erratum cites), at a46a6181 (the commit the
  spot-check used), at base 1560e4d8 and at tip f4066979. Neither line says M17
  survives.
- `final/c1/c1-tip-mutants.json` (that is, `.ufo/waves/round-25/final/c1/`, tracked
  at the tip) contains `mutants 28, killed 26, pristine passed` and
  `surviving ['M17-ref-shadow', 'M20-log-sha-shape']`. Its `.exit` file says `exit=0`.
  This matches the erratum's corrected attribution.
- The half of the clause the erratum leaves standing is true. At tip,
  `tests/report-audit/isolation-mutants.py:33-36` says "…F13 now kills M33 and M17
  survives the grid (full run at 1fc41e34: 28 mutants, 26 killed, survivors M17 and
  M20)".
- The draft file it cites exists at tip:
  `.ufo/waves/round-26/w1-build/out/ScribeRoutedRepairs/Defect2-KQ36-and-lesson.md`.
- Nit (info): the erratum pins a23c0e04, a round-26 commit, rather than the
  spot-check's a46a6181. Both give the same lines, so nothing is affected.

## 4. Defect 4 (context-capacity wording errata): holds

- Lines 55-56 (base 1560e4d8): "…and the only trace / is a log warning
  `n_ctx_seq (4096) > n_ctx_train (2048)`." The line numbers are correct.
  - `sed -n 1083p .ufo/waves/round-25/final/raw/K5.server.log` gives
    `0.00.008.336 W srv    load_model: the slot context (4096) exceeds the training context of the model (2048) - capping`.
    The quoted substring is exact.
  - The warning the original wording cites is at K5.server.log:295 and :828.
- Line 137 (base): "`n_tokens = 1025` (`final/raw/L1.server.log` lines 1849-1866):
  2 × 1025". The line number is correct.
  - L1.server.log:1852 and :1866 both show
    `stop processing: n_tokens = 1025, truncated = 0` (slots 0 and 1). The citation
    is exact.
  - Claim "each slot held 1024 cells": L1.server.log:1748-1749 show
    `slot decode token … n_tokens = 1024` for both slots. Lines 1846 and 1848 show
    `failed to find a memory slot for batch of size 1` and then
    `Context size has been exceeded`. Line 304 shows a `2048 cells` pool.
  - Source check. A fresh fetch of
    `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`
    (curl exit 0) has sha256
    `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`, equal to the
    lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp`.
    In that file, `handle_last_sampled_token` logs `prompt.n_tokens()` at line 559
    before `prompt.tokens.push_back(sampled)` at line 582. `release()` logs after the
    push, at line 590.
  - So 1024 cells per slot were placed, and the 1025 count includes the sampled
    token that could not be placed: 2 × 1024 = 2048, a full pool.
  - "Both requests failed": `send_error` appears for task 2 at line 1849 and task 3
    at line 1863. Holds.
- The fixture logs are tracked and unmodified: the working-tree and tip sha256
  prefixes match (K5 `b48213de5e133c7c`, L1 `b025f239cb601a51`).
- Low nits (optional fixes, nothing is false):
  - (a) The errata cite `L1.server.log:1852` without a directory. They give the full
    path only for K5. Smallest fix: write `.ufo/waves/round-25/final/raw/L1.server.log`.
  - (b) The 1024-cell claim cites only the 1025 release lines. Lines 1748-1749 are the
    direct evidence.
  - (c) The errata section is headed "Routed by … defect 4", but its third bullet
    (S131-S135 supersede S106/S107/S109/S112/S113, KQ31) carries defect 3. Those rows
    exist at SOURCES.md:143-147. I did not verify their content; that belongs to the
    ReopenS131 to ReopenS135 seats.

## 5. Defect 6 (SCORECARD round-25 trend correction): holds

- The quoted trend line is exact: base SCORECARD.md:1307-1308 reads "quality
  unchanged-to-improved … discernment improved".
- The closure citations are exact. spotcheck:180 is `**Expansion: improved.**`, :187
  is `**Quality: unchanged.**` and :194 is `**Discernment: unchanged.**`. The
  corrected verdicts ("expansion improved, quality unchanged, discernment
  unchanged") match all three.
- The round-25 report citation `.ufo/reports/round-25/kama.md:120-129` is correct in
  content but resolves only from the fleet root.
  - `git show f4066979:.ufo/reports/round-25/kama.md` gives
    `fatal: path … does not exist`. The lane `.ufo/reports/` holds only `round-5`.
  - The fleet copy `/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md`
    (sha256 `609bb5be4c2313cd105b5f986c4eea5182586b7eca789032aeaa43a8f4d6549f`,
    mtime 2026-10-22 07:19 -0300) shows `- **quality: unchanged**` at line 120 and
    `- **discernment: unchanged**` at line 127. The range 120-129 covers both
    verdict paragraphs.
  - SCORECARD rows for rounds 6-9 (lines 147, 160, 175, 187) already use this
    fleet-root form, so the citation follows the existing convention (low).
  - Residual risk: the lane commit does not pin the cited bytes. A later edit to the
    fleet report would break the citation without trace. Optional fix: add the
    sha256 above next to the citation.
- Labelling holds. The correction opens "The earlier bytes stay as written", and
  section 1 confirms it.

## Residual risk and verification gaps

- I did not verify the S131-S135 row content (defect 3) or the count-c2 raw-hash
  binding (defect 5); both are outside this seat's scope.
- I did not run the frozen counter. Section 2 rests on `git diff` byte identity
  between 7e5ff9b5 and f4066979, not on a fresh run.
- The round-26 report does not exist yet, so SCORECARD.md:1319 and :1332 point to
  nothing until closure.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/ReviewerRoutedApplied.md` (this report)
- Scratch, outside the lane: `/fast/scratch/hyaku/kama-r26w2/ReviewerRoutedApplied/`
  (`*.diff`, `*.base`, `*.tip` for the four files, and the fetched
  `server-context.cpp`)

Installs: none. Processes started: none still running (no llama-server).
