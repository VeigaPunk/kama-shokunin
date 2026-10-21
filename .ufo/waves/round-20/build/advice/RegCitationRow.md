VERDICT: partial - Registry row for `tools/citation-provenance.py` drafted and executed at 37bd4c5; the verdict map has a real error-as-verdict defect (unusable git at a rev exits 1) and the self-test label says 15 cases while 14 are executed.

# RegCitationRow — round-20 advisory (CloseKama18.RegCitationRow-2)

Lane pinned at `37bd4c5bd456a2f8a54d3312c28495c321715856` (scratch clone `/tmp/kama-r20-RegCitationRow/lane`, checked out at that commit; lane untouched). Tool blob sha256 `5c887572b37a80c0757b59a7735da386be2885e463ec2682c1d59f8e9b55110b`, last changed by `30ed378`. Python 3.14.8, git 2.56.0 (already present; no install).

## Commands executed (all exit codes observed)
| # | Command (cwd = scratch lane unless noted) | Observed | Exit |
|---|---|---|---|
| 1 | `python3 tools/citation-provenance.py --selftest` | `selftest: ok (15 cases)` | 0 |
| 2 | `python3 tools/citation-provenance.py --lane $L` | `required=4 docs_unreadable=0 found=4 verified=4 missing=0 mismatch=0 off_ref=0` | 0 |
| 3 | same with `--json`, counts extracted | identical counts | 0 |
| 4 | in-process wrapper counting `check()` calls during `selftest()` | `selftest rc: 0`, printed `ok (15 cases)`, **`check() calls: 14`** | 0 (wrapper) |
| 5 | `--registry` = `{}` object | `registry must be a non-empty JSON array` | 2 |
| 6 | `--lane` = non-git dir | `lane is not a git repository` | 2 |
| 7 | `--docs` = absent file | `cannot read ...absent.md`; counts `docs_unreadable=1 missing=4` | 2 |
| 8 | registry row rev `f000…0` (nonexistent), doc carries matching token | `mismatch: badrev … observed=absent (fatal: invalid object name …)` | **1** |
| 9 | registry row rev `f000…0`, doc absent | `cannot read …none.md`; `missing=1 docs_unreadable=1` | 2 |
| 10 | off-ref: commit on branch `offref` not ancestor of `origin/master`, token present | `off_ref=1`, `off-ref: offref …` | 1 |
| 11 | same, with `--allow-off-ref` | `verified=1` | 0 |
| 12 | `git merge-base --is-ancestor <offref> origin/master` (throwaway clone) | ancestry check negative | 1 |

Scratch fixtures lived under `/tmp/kama-r20-RegCitationRow/exp` (deleted at finish).

## Registry row (drafted for SKILL.md; proposed heading `## Round-20 citation provenance gate registry (owner: kama)`, appended after the Round-18 block, line ~601+; no existing row changed)

| Name | Kind / entry command | Verdict map (code → class) | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Revision-qualified citation provenance | gate: `python3 tools/citation-provenance.py [--json] [--allow-off-ref] [--registry PATH] [--docs PATH ...] [--lane PATH]`; defaults: lane = tool's parent repo, docs = `corpus/lessons/round-18.md`, `corpus/lessons/round-19.md`, `corpus/SOURCES.md`, `SCORECARD.md`, `LOG.md` | 0 clean (every required row found, verified, rev an ancestor of `origin/master`); 1 failed (any `missing`, `mismatch` or `off_ref` row); 2 could-not-evaluate (unreadable or non-array registry, lane not a git repository, any unreadable document); any other code reads could-not-evaluate. Known gap: an unresolvable rev in git exits 1 (`mismatch`), not 2 — see Defects | `python3 tools/citation-provenance.py --selftest` (spelling `--selftest`); prints `selftest: ok (15 cases)`, exit 0; 14 `check()` invocations measured | `registry/required-citations.json` (4 rows at 37bd4c5: `s055-commands`, `gate-live-1`, `c2-official-stdout`, `gate-live-checkpoint`); each row must be matched by a `cite(<rev>, <path>, sha256=<64 hex>)` token in a document and by the `git cat-file blob` digest | Read-only over the lane: reads docs, registry and `git cat-file blob`; self-test creates and removes a temp git repo under the system temp dir; writes nothing in the lane | kama |

Default run at 37bd4c5 (command 2): exit 0, 4/4 verified. [INFERENCE] the exit is clean only because the cited blobs and the 4 tokens still match in the tree at that commit; the verdict grades the tree it runs on, which is not frozen (see Gaps).

## Defects found (route to owner kama; not fixed here)
1. **Error reported as verdict.** `git_blob()` returns an error string for an unresolvable rev; `check()` sets `status="mismatch"`; `main()` exits 1. Observed (cmd 8): a git-unusable rev exits 1 `failed`. The docstring says exit 2 covers "unusable registry/docs/git". Under the Gate standard (errors are not verdicts) this should be could-not-evaluate (2). Same path for a `git cat-file` timeout.
2. **Self-test label drift.** `selftest()` hard-codes `"selftest: ok (15 cases)"`; the function body issues 14 `check()` calls (10 `run(...)`, `stale-equal`, `doc-binding`, `doc-binding-ok`, `unreadable-doc`) plus one trivial `DEFAULT_DOCS` assertion (not a `check()` call). Cite the measured figure, not 15, until the label is corrected.
3. **Exit mapping not self-tested.** `selftest()` calls `check()` in-process and never calls `main()`, so no self-test asserts the 0/1/2 map above (cmds 5–8 were only observed by hand). Expected finding-ids are not committed; assertions are inline counts.
4. **off_ref classed as failed (exit 1).** [INFERENCE] a rev off `origin/master` is a provenance scope fault rather than a failed citation; the lane may prefer 2. Left as observed.

## Gaps against PROTOCOL §Gate standard
- "Two evidences": no frozen snapshot run with committed `expected.json` exists for this gate, although its verdict depends on mutable docs (`corpus/lessons/*`, `LOG.md`, `SCORECARD.md`). The row must say so, or a frozen run is owed.
- Verdict names the revision only through each row's `rev`; the run's own worktree HEAD is not recorded in output.
- Routed round-19 defect "register citation-provenance.py in SKILL.md" is satisfied by this row once appended; the carried "13 unregistered round-18 citations" and "citation checker observed-branch selftest gap" are not closed by it.

## Out of scope / not done
- No lane edits, no commit, no subagent dispatch, no tool installed or upgraded, no live server, no model download.
- `corpus/`, `SKILL.md` and `registry/required-citations.json` were read only, in scratch.
- Scratch `/tmp/kama-r20-RegCitationRow` is removed at finish.
