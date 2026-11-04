source: S542 — Git git-status, https://git-scm.com/docs/git-status §Porcelain Format Version 1 (version-1 records "guaranteed not to change in a backwards-incompatible way", retained sha256 22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180); `plans/round-71-claims.md` §C1 (frozen predicate, counter, kill rule, do-nothing control); code `tools/pre-report-gate.py` sha256 07cfc04fbba413f851034734bfee1122b12463ed5d65486762d6bd736cb3bd0b (re-entry guard) and the four instruments it wires
verified-at: b43e71a8 (freeze base) and e2b860c8 (the integration commit that landed the tool, this entry and the calibration row; the counter was re-run there) — the gate was read and run from the round-71 worktree (absent from b43e71a8, `git status --porcelain -uall -- tools/pre-report-gate.py` → `??` at first read; the pre-guard revision `d0957e0b…` was probed first, then `07cfc04f…`); receipts `.ufo/waves/round-71/w1/SCR01KnowledgeEntry/{selftest,gate-round70,gate-round71,shortcut-rerun,recursion-guard-direct,run-fact-recursion-probe}.out`
recheck: `python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=6 fail=0` (exit 0); re-run the counter at the report tip; S542 recheck on-release

# One pre-report verdict: arms green at the tip and round work committed

## Why one verdict exists

At the round-70 report tip every existing instrument exited 0 while round work sat
uncommitted: `.ufo/waves/round-70/` carried 26 uncommitted files in 14 status entries
(7 modified seat outputs; 7 untracked paths, one the 13-file `MT01Mutants/logs/` directory
that plain `git status` collapses into one entry). The landed-work check could not see them
— it grades only its declared self-record paths (`WORKTREE_LANDING_CHECK paths=5`) — so the
non-author closure caught the class by hand (`corpus/lessons/round-70-verifier-spotcheck.md`
§7 defect 1). The gate replaces "run four instruments and hope" with one verdict requiring
both: instruments green at the measured tip, and the round's wave dir committed.

Base receipts: `.ufo/waves/round-71/measured/before/git-status.out` (14 entries) and
`.../pre-report-shortcut.out` → `SHORTCUT_CONTROL arms=4 failed=0 uncommitted=26`, exit 0: the
do-nothing control meets every instrument exit and cannot see the class. Re-run live at `af6eb6c2`: same four exits 0, `uncommitted=26`.

## The five arms

Fixed order, each graded by the child's exit status (`ok` iff 0):

| Arm | Instrument | Fails when |
|---|---|---|
| selfdesc | `tools/round42-selfdesc-reconcile.py --repo R --tip T` | the SCORECARD head/banner, Planned/Retired/Saturation, Capabilities-vs-canon counts, receipt tokens, README backticks, PROVINCE tokens, per-axis run-fact needles or the round-41 head table disagree with the tree at T (needs `mismatches=0 met=True`) |
| newest-closure | `tools/round69-newest-closure-counter.py --rev T --since-round 63` | the `## Axes` calibration row's "latest outside closure" is not the newest in-scope closure by (date, round) |
| receipt-audit | `tools/round68-receipt-pointer-audit.py --rev T` | a section-relative `measured/...` pointer in SCORECARD/LOG has no blob at T — directly, by brace/glob expansion, or by a ledger target that exists |
| worktree-landing | `tools/round67-worktree-landing-check.py --repo R` | a declared self-record path is DIRTY (any byte, newline translation included), MISSING, UNTRACKED or UNREADABLE against HEAD |
| round-clean | `git -C R status --porcelain -uall -- .ufo/waves/round-<N>` | any record; one `-uall` record is one file (directories collapse only without `-uall`) |

Failure classes: arms 1-3 are self-description or receipt inconsistencies at one revision; arm 4
is worktree bytes that differ from HEAD; arm 5 is uncommitted round work — the class arms 1-4 cannot see.

## CLI and output contract

`python3 tools/pre-report-gate.py --repo <lane> --round <N> --tip <rev>` (also `--selftest`,
`--json`, `--tools-dir`, `--work`). One line per arm, then the verdict:

    PRE_REPORT_ARM <name> exit=<e> ok|FAIL <detail>
    PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>

`failed` counts arms that did not pass (round-clean included); `uncommitted` is arm 5's file
count. Exit 0 iff `failed=0 and uncommitted=0`; 1 names every failed arm; 2 is reserved for
CLI misuse (missing `--round`, `--repo` not a directory) and unevaluable selftest fixtures.
The verdict line carries no tip field: the measured revision is the `--tip` argument, so a
receipt quotes the command with its tip.

Observed at `e2b860c8` (round-71 worktree): `PRE_REPORT round=70 arms=5 failed=3 uncommitted=0`
(selfdesc `r41 calibration run … exit 3 != 0`, receipt-audit `unresolved=3`, worktree-landing `DIRTY SCORECARD.md`) and `PRE_REPORT round=71 arms=5 failed=4 uncommitted=19`, exit 1.

## Decision table

| Output shape | Meaning | Next action |
|---|---|---|
| `failed=0 uncommitted=0`, exit 0 | instruments green at the tip, round wave dir committed | file the report; cite this line as the pre-report receipt |
| `failed>0 uncommitted>0` | both classes: an instrument red and round work unlanded | commit the wave files (L1) and fix the named surface |
| only `round-clean FAIL` (`uncommitted=u>0`) | instruments green, round work unlanded — the round-70 defect-1 class | commit before reporting; no instrument repair |
| `failed>0 uncommitted=0` | a reconciled instrument red at the tip: stale closure pointer, stale count, dangling receipt path, or a dirty declared path | read the `FAIL` arm line and repair that surface |
| exit 2 | CLI misuse or an unevaluable selftest fixture: not a verdict | fix the invocation |
| `No such file or directory`, exit 2 | the tool is absent (the round-71 base state) | nothing to read; never read it as green |

## Limits

- The gate grades arm exits, not each instrument's verdict text: it echoes the verdict line in
  `detail`, but a child that exits 0 on an unevaluable state still reads green. The
  instruments' own could-not-evaluate exits (1/2) do count as failures.
- Cleanliness covers `.ufo/waves/round-<N>/` only. Edits elsewhere are seen only through arm 4,
  and only for its five default declared paths (SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md,
  corpus/SOURCES.md): an uncommitted `corpus/knowledge/` entry or `tools/` file is not graded.
- Everything is measured at one revision: token presence, pointer resolution, blob identity.
  The gate does not check that a claim is true, that a registry row's content is correct, or
  that report prose matches the tree.
- `git status --porcelain` version 1 is S542's script-stable record shape; a shape break is an
  upstream guarantee break, not a parser bug. A failed `git status` marks round-clean FAIL
  while `uncommitted` prints 0, so the exit stays nonzero (code read, not probed).
- It is a step the L1 runs, not a hook. A RUN fact that executes the scored gate loops (selfdesc arm →
  reconciler → r41 run-fact harness → gate; the harness mirrors `refs/heads/master` at the tip). The tool
  refuses a re-entry at depth>=1 (`PRE_REPORT_RECURSION depth=<d> refused`, exit 3): bounded, still red —
  the live row showed `r41 calibration run … exit 3 != 0`, so a tip carrying that row cannot print
  `failed=0`; cite `--selftest` or a committed after-receipt there, never the scored gate.
- S052, the freeze's second grounding, is the fail-closed-on-no-verdict precedent: an arm with no verdict is a failure, never a skip.
