# ScribeSkillAppend — report (round-23 falsify, SKILL.md append draft)

## Verdict

Holds for the draft. The round-23 section is drafted as an append-only section
(`out/ScribeSkillAppend/SKILL-append.md`) and every factual claim I could check
statically matches `tools/report-landing-audit.py` at 245a37f6. Two wording
issues and one integration hazard are below. Nothing was applied to the lane
checkout. No grid, mutant, or selftest run was performed by the scribe; L1
figures are labelled as L1-reported.

## Exercised verification (scribe, static only)

- `git rev-parse HEAD` → `245a37f69628c2c6bb29bbf17897d8fb5946c857` (lane HEAD).
- `git show HEAD:SKILL.md` → 774 lines; R22 section ends at line 771–774.
- `git diff` on the lane: SKILL.md has an **uncommitted** 29-line round-23
  section appended at lines 775–803; `corpus/QUALITY.md` also modified.
- `git show HEAD:tools/report-landing-audit.py | grep subprocess` → one site,
  `subprocess.run(["git", *GIT_ISOLATION, "-C", …])` at `tools/report-landing-audit.py:114`
  (HEAD). Every git call therefore goes through `git()`.
- `GIT_ISOLATION` literal at `:93-96` matches the draft's argv list exactly.
- `errors="surrogateescape"` used only at `:184` (lane `log -z`) and `:418`
  (`ls-tree` report listing), matching the draft.
- Refusals at `:428-449` (`check_history_repo`): non-sha1, not top level, shallow,
  info/grafts, `objects/pack` `.promisor`, `remote.*.promisor` /
  `extensions.partialclone`. Ref-named citation, unparseable log record and
  catch-all at `:918`; ref-named citation refusal at `:163` (HEAD). All refusals return 2 (`:909-924`).
- `--branch` pin at `:452-458` (`refs/heads/<name>^{commit}` first).
- Git floor: `git --version` → 2.56.0 locally. `--no-lazy-fetch` introduced in
  2.45 per the 2.45.0 release announcement
  (`https://public-inbox.org/git/xmqq8r0ww0sj.fsf@gitster.g/`):
  "git --no-lazy-fetch cmd" allows to run "cmd" while disabling lazy …
- Grid row count: `tests/report-audit/repo-state-grid.py` case table
  `:527-575` — C01–C08 (8 controls), F01–F26 (26 faults), O01–O02 (open),
  T01 (tradeoff). Counts match the lesson and the draft.
- Mutant count: `tests/report-audit/isolation-mutants.py:28-72` — M01–M07,
  M09–M25 (**M08 absent**): 24 mutants, matching the stated count.
- Frozen arm: `git cat-file -t 4fe9339f8fc3a4a4a479d9c938a850da12f1124d` →
  `commit`. The file blob at that commit is `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`.
- KQ32 (`corpus/QUALITY.md:165`) and KQ34 (`corpus/QUALITY.md:177`, "narrows, does
  not supersede, KQ32") exist; the draft cites them correctly.

## Findings

1. **Integration hazard (must resolve before applying).** The lane working tree
   already carries an uncommitted round-23 section at SKILL.md:775–803. The
   draft is written for the 245a37f6 committed text. If the draft is applied on
   top of the working-tree copy, the section is duplicated. Integrator should
   replace the working-tree block with the draft, not append a second one.
2. **Wording: "frozen auditor blob" is wrong.** Both the working-tree section
   and the grid row describe `4fe9339f:tools/report-landing-audit.py` as a
   "blob". `4fe9339f…` is a commit; the file blob is `fcc255ce…`. The draft says
   "file … at commit `4fe9339f` (blob `fcc255ce`)". The grid's code
   (`FROZEN = "4fe9339f…"`, `git show FROZEN:tools/…`) is correct; only the prose
   is wrong. Not a behavioural defect.
3. **Numbering gap.** The isolation-mutant table has no M08 (M07→M09). The count
   of 24 is right, but a reader comparing IDs will see a gap. Either renumber in
   a future round or note it; the draft flags it as "M08 is not present".
4. **Git floor citation.** The lesson's "2.44.0 rejects it with exit 129" is an
   L1 observation and was not re-run here. The draft labels it that way.

## Not verified (unrun checks are not passes)

- `python3 tests/report-audit/repo-state-grid.py --arm current` /
  `--arm frozen` (26/26, 0/26 claims), `isolation-mutants.py` (22/24 killed),
  `--selftest` (50/50) and the rounds 10–22 ledger no-harm check were **not run**
  by the scribe; their figures are L1-reported and labelled that way in the draft.
- git 2.44 behaviour (exit 129 → audit exit 2) not reproduced; no git < 2.45 is
  installed locally.
- Interaction with `alternates` / gitfile (O01/O02) not exercised.
- Repo-local channels outside the graded rows not examined; the draft does not
  claim them.

## Out of scope observed

- The R21 verdict map (SKILL.md:683) still lists only the old exit-2 causes; the
  round-23 refusals are carried by the new section, so the R21 row was not
  edited (append-only rule).

## Tools installed

None. No package installs or updates were made by this scribe.

## Files written

- `.ufo/waves/round-23/falsify/out/ScribeSkillAppend/SKILL-append.md` (draft section)
- `.ufo/waves/round-23/falsify/advice/ScribeSkillAppend.md` (this report)

No lane tracked files, index, `.jj`, fleet root, sibling lanes, or `~/.omp` were
written. No commits, pushes or jj commands were run. No subagents spawned.
