# ScoutKamaDomainTie — where the report-landing audit verdict lands in kama's process

VERDICT: confirm — in every documented kama consumer the audit's **process exit is the whole signal**. The official harness grades exit equality only, and the summary is pasted into the permanent fleet report. A false clean therefore passes the round pre-commit gate silently; a crash-exiting-1 is read as the registered `failed` verdict and can satisfy the one recipe row whose declared exit is 1.

Base: lane master `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (HEAD). Citations marked HEAD are `git show HEAD:tools/report-landing-audit.py` line numbers; the worktree copy is currently modified (`git status`: ` M tools/report-landing-audit.py`) and was not used for those lines.

## Feed chain (observed)

1. **Registered contract.** `SKILL.md:683` — instrument row: entry command, and verdict map `0 clean (...) 1 failed; 2 could-not-evaluate (...)`. Every consumer below inherits this map.
2. **Round checklist.** `SKILL.md:687-691` — before committing a round report, run `--rounds 10-<N-1> --report <N>=<draft>`; "it must exit 0, and its summary line goes into the report under Landed changes"; Landed generated from `git log --reverse`, never memory.
3. **Quality criterion KQ28.** `corpus/QUALITY.md:151` — a report admits only when that command "exits 0 before the fleet commit and its summary is pasted"; the rejected failures are exactly a spliced hash, a Landed list written from memory, and a ledger row correcting with an unrelated commit.
4. **Permanent fleet attestation.** `.ufo/reports/round-21/kama.md:25` pastes the literal `summary reports=12 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean`; `.ufo/reports/round-22/kama.md:269-277` records `Observed exit0, stderr empty` plus the JSON summary. Corrections to filed reports are append-only with the superseded text named (`corpus/QUALITY.md:143`, KQ26).
5. **Official recipe rows.** `.ufo/waves/round-21/recipe.json:16-24` selftest exit 0; `:26-37` raw audit declared exit **1**; `:39-48` ledger run declared exit 0. `.ufo/waves/round-22/recipe.json:49-57` selftest 0; `:58-70` ledger 0.
6. **Harness grades exits only.** `.ufo/waves/round-21/run.py:56` `result['as_expected'] = code == result['expected_exit']`; `:62` harness returns 0 only if every row is `as_expected`. stdout/stderr are written and **hashed** (`:50-55`), never parsed. `SCORECARD.md:1005-1008` publishes the result as "28/28 commands met their declared exits".
7. **Published score claim.** `SCORECARD.md:1012` — C1 calibration 7→7 with "0 FP, 0 FN", counting commands raw exit 1 / ledger exit 0. Closure no-harm: `SCORECARD.md:1139-1143` audit selftest 50/50 and "Historic rounds10–21 still yield exactly9 raw defects … uncorrected0, invalid0, unmatched0".
8. **Historical repair channel.** `registry/report-landing-errata.tsv:1-11`; the tool reads the ledger from the committed `--branch` blob and requires each correction to resolve (`report-landing-audit.py` HEAD `:34-40`, `:355-359`).

## Operational consequence

### False clean (probe faults c/d: `git replace` of an omitted commit; `refs/replace/<fabricated 40-hex>`)

- The KQ28/checklist pre-commit condition is satisfied falsely (`SKILL.md:689`; `corpus/QUALITY.md:151`). The pasted `status=clean` line then becomes a permanent false attestation — the same sentence shape as `.ufo/reports/round-21/kama.md:25` — and no errata row is written, because the ledger is fed only by detected defects (`report-landing-audit.py` HEAD `:34-40`, `:355-359`).
- The defect class the detector exists for — dropped round commits and spliced hashes (`corpus/lessons/round-21.md:63-64`, M1/M2) — returns to invisibility while the round records that a check ran and passed. Round 21's own motivation text is `corpus/lessons/round-21.md:11` ("had no mechanical check").
- A fabricated **correction** also passes `errata-invalid`: validity is a `cat-file … ^{commit}` lookup (`report-landing-audit.py` HEAD `:114-115` via `lookup`, applied at `:355-359`), and a repo-local replace ref makes the fabricated name resolve. That falsifies the ledger inventory behind `uncorrected=0` in `SCORECARD.md:1139-1143`. [INFERENCE: same mechanism as the probe's fault (d); the code path is HEAD `:114-115`.]

### False failed (probe faults a/b: non-UTF-8 git stdout → traceback, exit 1)

- The registered map calls exit 1 "failed", i.e. a defect verdict, not could-not-evaluate (`SKILL.md:683`). The promise is HEAD `:42-45` ("Errors are never verdicts"; exit 2 for unusable git) and the CNE handler is HEAD `:831-843`. At HEAD, `git()` decodes with `text=True` (HEAD `:87-97`), so `UnicodeDecodeError` bypasses the `EvalError`/`OSError` handlers entirely.
- **The raw-audit row declares exit 1** (`round-21/recipe.json:35`) because 9 historical defects are expected. Since the harness compares only the exit (`round-21/run.py:56`), a traceback that exits 1 marks `c1-audit-raw` `as_expected=true`; `commands.json` records the round's C1 counting command as met while its stdout carries no verdict. That is exactly the credit KQ25 forbids — "an error remains visible and non-passing" (`corpus/QUALITY.md:142`). [INFERENCE: the traceback is in the captured stdout/stderr files, but no consumer reads them; `run.py:50-55` only writes and hashes.]
- The same crash on the selftest or ledger rows (declared 0: `round-21/recipe.json:22,47`; `round-22/recipe.json:55,69`) is loud: harness exit 1 (`round-21/run.py:62`), so the measured-tree claim cannot be produced and the report is blocked rather than falsified. This is the only fail-loud path, and it exists only when the fault lands on a row declared 0.

### Command execution (probe fault e: promisor remote + repo-local `core.sshCommand`)

- At HEAD the audit runs plain `git -C <repo>` with no replace/lazy-fetch isolation (HEAD `:87-91`), while `git_env` promises "neither the audited repos nor the selftest fixtures can be redirected" (HEAD `:79-84`). A promisor remote plus repo-local `core.sshCommand` executes during `cat-file --batch-check` (HEAD `:114-115`). Inside the trusted lane/fleet the consequence is audit-context execution, not a verdict flip, and it falls outside the "Errors are never verdicts" sentence because the side effect precedes any output.

## Scope boundaries already on record (the round report should carry these)

- `corpus/QUALITY.md:165` (KQ32): the audit is limited to the trusted fleet/lane repositories until repository-local Git-config/history and UTF-8/error hardening is demonstrated separately; environment scrubbing is not local-config isolation.
- `SKILL.md:732-738`: "UTF-8/error/top-level handling and the late selftest fallback/GIT_DIR debt remain unclaimed until separately hardened. Never point it at an untrusted repository under the current guarantee (KQ32; round-22 lesson D4)." `SKILL.md:771`: "D4 local-Git-config/history and UTF-8 hardening remains frontier."
- `SCORECARD.md:1120-1121`: the round-22 component "is not a new axis, source-validity guarantee, serving capability or D4 security hardening." `corpus/lessons/round-22.md:116-121` (D4) records the same gap and that "Environment scrubbing does not suppress repository-local configuration."
- Consequence for wording: the fault surface is repository-local state in the **trusted** lane/fleet (a stray local config, replace ref, or promisor remote), not arbitrary untrusted-repository execution.

## Not verified

- I did not run `report-landing-audit.py`, its selftest, or any fixture. The lane worktree already carries an uncommitted modification to `tools/report-landing-audit.py` (`git status`: ` M …`), and the fault grid belongs to L1's probe; every exit observation here is L1's probe or HEAD source at `4fe9339f`.
- No `lsp` device is mounted (`read xd://lsp` → "No such tool: xd://lsp"), so tracing was direct source reading at the pinned lines; `grep` was used only to discover files.
- No other automated consumer was found or verified: a grep over the lane excluding `.ufo/` matched only `SKILL.md`, `corpus/QUALITY.md`, `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-21.md`, `considerthese/2026-10-21.md`, and the ledger header comment. Closure seats may re-run the audit manually; that route is not machine-enforced.
- Fleet-report immutability enforcement was not verified (none found; KQ26 is procedural).
- No tools installed or updated.

Files written: `.ufo/waves/round-23/build/advice/ScoutKamaDomainTie.md`.
