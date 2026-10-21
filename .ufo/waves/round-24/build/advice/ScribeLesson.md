# ScribeLesson — round-24 Gate/Mistakes lesson draft (scoped findings)

Seat: `KamaR23-2.ScribeLesson-2` (leaf member; no subagent dispatch).
Date: 2026-10-21. Round base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(git 2.56.0, Python 3.14.8).
Assignment: draft the round-24 lesson Gate/Mistakes structure from the
rejected-harmed r23, keeping the honesty of the fixed known harms and of the
source scope; draft only in the out directory; no production edits.

## Behavior

Read the round-24 preregistration, the committed round-23 lesson
(`corpus/lessons/round-23.md`), the base auditor, the round-23 grid and the
round-23 wave advice that recorded the harm. Drafted a round-24 lesson
skeleton with the four sections the corpus format uses — Declared claim, Gate,
Mistakes, Integration and boundaries — with:

- a **Gate** that carries the r23 rows forward unchanged (S089, S090, S093,
  S094, S096–S101), names the superseded rows that stay superseded (S091, S092,
  S095), and adds four **candidate** new rows opened by this scribe on the
  official git manuals (S102 git-rev-list `--missing=print`, S103 git-cat-file
  `--batch-check`, S104 git-config promisor/partial-clone keys, S105
  partial-clone promisor-remote key list), each with the located quote, the
  page digest and the "last updated in 2.56.0" version;
- a **Mistakes** section that carries r23 M1–M7 forward as *fixed* with their
  existing pointers, adds M8 (metadata-only refusal shipped as isolation),
  M9 (refusal-scope inversion after the repair) and M10 (the repair must not
  re-open the transport channel), and records the two preregistration
  corrections (C-1 69 reports not 68; C-2 40 of 56 killed FIFO-process
  identities retained) as append-only items for the L1;
- an **Integration and boundaries** section stating the claim, the trades
  (git ≥ 2.45), what stays open from r23, and what this scribe did not verify.

No corpus, tool, grid, config or Git-index file was written. No commit, no
push. No build, test, formatter, grid or selftest run was executed.

## Gates

- Gate rows opened by this scribe (plain HTTPS docs, 2026-10-21):
  `https://git-scm.com/docs/git-rev-list` (page sha256 `6eca09d9ef21dd42…`),
  `https://git-scm.com/docs/git-cat-file` (`539830429faea901…`),
  `https://git-scm.com/docs/git-config` (`5a63888b1c15a172…`),
  `https://git-scm.com/docs/partial-clone` (`8a6493225f76dba8…`).
  Each page reports "last updated in 2.56.0"; the host git is 2.56.0.
- No pass/fail gate was run, and no exit or finding expectation is claimed
  from this seat.

## Touched surfaces

Written (lane, untracked, inside the wave's own build tree):

- `.ufo/waves/round-24/build/out/ScribeLesson/round-24-lesson-draft.md` — the
  draft lesson (Gate/Mistakes structure).
- `.ufo/waves/round-24/build/advice/ScribeLesson.md` — this report.

Scratch only (own clone, no production file, no commit):

- `/fast/scratch/hyaku/kama-r24/ScribeLesson` — `git clone --no-hardlinks` of
  the lane at base `0df800e`.
- `/fast/scratch/hyaku/kama-r24/ScribeLesson/.docs-cache/` — the four fetched
  manual pages.
- `/fast/scratch/hyaku/kama-r24/ScribeLesson/.scratch/` — two throwaway local
  repositories used for the two offline observations below.

Read only: `.ufo/waves/round-24/preregistration.json`,
`.ufo/waves/round-24/build/{spec,assignments,dispatch}.json`,
`corpus/lessons/round-23.md`, `corpus/SOURCES.md` (rows S089–S101),
`corpus/QUALITY.md` (KQ30–KQ34), `tools/report-landing-audit.py` (lines
39–133, 430–503, 468–482), `tests/report-audit/repo-state-grid.py` (lines
195–300, 482–700), and the round-23 advice files cited below.

## Findings (exact evidence)

1. **The harm is in the base auditor, at three named lines.**
   `tools/report-landing-audit.py:438` `check_history_repo` raises
   `partial clone (promisor pack)` at `:457` for any `*.promisor` file that has
   a sibling `.pack`, and `partial clone (<key>)` at `:465` for
   `extensions.partialclone` or any `remote.*.promisor` key. Both are
   *metadata* conditions: no object is inspected.
2. **The r23 wave already measured the flip, in both directions.**
   `.ufo/waves/round-23/build/advice/RevCalibrationAxis.md:57` — "TRADE:
   partial clone, every cited object local | exit 0, clean, req 1 | exit 2,
   'partial clone (extensions.partialclone)' | clean input flips to refusal
   (H2)"; `:72` names `L445–448` as the refusing lines of that revision.
   `RevSkillText.md:51` — committed `e0f0434` gives exit 2
   `could-not-evaluate: … partial clone (promisor pack)` where frozen
   `4fe9339` gives exit 0 clean; `:323` — T01 candidate exit 2, frozen exit 0.
   `RevLookup.md:75` — "a benign `file://` partial clone was `found` in base
   and is now refused".
3. **The r23 grid could not detect the harm, because the harm was the
   expectation.** `corpus/lessons/round-23.md:207-208` records T01 and F23 as
   *declared trades*; `tests/report-audit/repo-state-grid.py:670,689` register
   F23 (contract) and T01 (tradeoff) with exit 2 as the expected outcome. The
   lesson drafted here therefore treats the r23 grid numbers
   (`corpus/lessons/round-23.md:112-121`: current `faults 26/26, tracebacks 0,
   executed 0, timeouts 0`; mutants `31, 30 killed`; selftest `50/50`) as
   evidence about the *r23 isolation mechanisms only* — not as evidence that
   refusing a complete promisor-marked repository was correct.
4. **The manual supports the round-24 discrimination directly.** git-config(1)
   `extensions.partialClone`: "Such a remote is called a "promisor remote" and
   it promises that all such omitted objects can be fetched from it in the
   future." (24 words) and `remote.<name>.promisor`: "When set to true, this
   remote will be used to fetch promisor objects." partial-clone(1) lists the
   promisor-remoteness keys as configuration variables. git-rev-list(1)
   `--missing=print`: "will also print a list of the missing objects. Object
   IDs are prefixed with a "?" character." git-cat-file(1) `--batch-check`:
   a name that "cannot be resolved to an object in the repository" is reported
   as `<object> SP missing LF`. These are the four candidate rows S102–S105.
5. **The availability mechanism works offline, without a fetch.**
   In a throwaway promisor-marked repository whose blob loose object was
   deleted, `git --no-lazy-fetch rev-list --objects --missing=print HEAD`
   printed `?ce013625030ba8dba906f756967f9e9ca394464a` and returned
   immediately; `git --no-lazy-fetch cat-file --batch-check` printed
   `ce013625030ba8dba906f756967f9e9ca394464a missing`; `git --no-lazy-fetch
   cat-file -e <oid>` exited 1. No remote was contacted (`example.invalid` was
   an inert URL). These are scribe-side observations of the documented
   mechanism, not a lane measurement.
6. **A citation trap avoided.** git-config(1) renders `extensions.partialClone`
   with its section and variable in separate markup, so a literal search for
   the joined key misses it; the draft anchors S104 on the rendered entry.
   Separately, `git config --list` prints the key lower-cased
   (`extensions.partialclone=origin` for a repository configured with
   `extensions.partialClone=origin`), so the auditor's lower-case comparison
   at `:462` does match git's own output — recorded as a local observation, not
   as a Gate row.
7. **The two preregistration corrections anchor to exact filed text.**
   `corpus/lessons/round-23.md:178` — "73 seats dispatched (68 reports; dead:
   RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty…)";
   73 seats − 4 dead = 69. `corpus/lessons/round-23.md:174` (M7) — "56 blocked
   `git` processes … (12:18–13:29 -03)"; the preregistration states 40 of the
   56 killed identities were retained, so "56" is a process count, not full
   identity evidence. A repository-wide search of the round-23 wave tree and
   the lesson found no other record of the 40, so both corrections are
   recorded as **declared, not re-derived**.

## Out of scope (not done)

- No edit to `corpus/lessons/round-23.md`, `corpus/lessons/round-24.md`,
  `corpus/SOURCES.md`, `corpus/QUALITY.md`, the auditor, the grids, the
  knowledge files or any operator/sibling/fleet file.
- No grid, mutant, selftest, historical-ledger or no-harm run; no exit or
  finding oracle of my own.
- No design of the repair itself (the availability algorithm, the per-object
  policy and the reason strings are the L1's and the executor seats').
- No KQ rule added or edited; KQ30–KQ34 were read only, to name the rule a
  mistake is captured by.
- No dispatch: leaf member, no subagents.

## Not verified

- The round-24 exit/finding expectations themselves (the preregistration's
  oracle, owned by the L1).
- The 69-report count and the 40-of-56 identity retention, beyond the filed
  text they attach to.
- Whether the repaired auditor keeps the r23 numbers `faults 26/26, tracebacks
  0, executed 0, timeouts 0`, `mutants 30/31`, `selftest 50/50`, and the
  historical ledger parity.
- The frozen-arm behaviour of the new grid rows, and the r23 F23/T01 rows
  under repaired code.
- Whether the candidate Gate rows are adopted; the ids S102–S105 are
  provisional and the L1 appends the rows under KQ22/KQ31.

## Tools installed or updated

None. `git` 2.56.0 and `curl` were already present; `curl` was used for four
plain HTTPS reads of git-scm.com manual pages into the scratch clone's
`.docs-cache/`. No pacman transaction, no `uv`/`cargo`/`npm` install, no
service or host configuration change.

## Artifacts

- Draft lesson: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/ScribeLesson/round-24-lesson-draft.md`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/ScribeLesson.md`
- Scratch clone and fetched pages: `/fast/scratch/hyaku/kama-r24/ScribeLesson/`
  (`.docs-cache/`, `.scratch/`)
