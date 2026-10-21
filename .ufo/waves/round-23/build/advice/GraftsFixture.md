# GraftsFixture: `.git/info/grafts` and `.git/shallow` against `report-landing-audit.py`

**Seat:** CloseKama22.GraftsFixture (round-23 build, leaf). **Auditor under test:** `tools/report-landing-audit.py` at frozen base `4fe9339f` (git blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`). **Tools:** git 2.56.0 (`/usr/bin/git`), Python 3.14.8, `jq` (host binary reports `jaq 3.1.1`). **Installs or updates:** none. The frozen auditor's selftest on this host: `cases=50 failed=0 rc=0` (baseline).

**Scope and safety:** every audited repository was a fresh `mktemp` repo under `/tmp`, run with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. The only remote was `ssh://example.invalid/x.git`. The real lane and fleet repos were inspected read-only (no `.git/shallow`, no `.git/info/grafts`, no `refs/replace`, no promisor or partialclone config, `rev-parse --is-shallow-repository` false) and were never audited.

## Answers

1. **`git --no-replace-objects` does NOT disable `.git/info/grafts` in git 2.56.0.** A graft that re-parents a commit still applies with the option. `GIT_NO_REPLACE_OBJECTS=1` behaves the same. Neither option affects `.git/shallow`.
2. **`GIT_GRAFT_FILE=/dev/null` disables grafts; `GIT_SHALLOW_FILE=/dev/null` disables the shallow file.** Both verified in plain git and through the frozen auditor.
3. **Storage form matters.** `git replace --convert-graft-file` (the path git's own deprecation hint recommends) turns the graft into `refs/replace/<C3>`. Then `--no-replace-objects` disables it, while `GIT_GRAFT_FILE` does not. The two neutralizers cover different forms.
4. **Verdict impact.** Repo-local grafts or shallow state can turn a missing round citation into a silent exit-0 "clean" with no stderr and no error. They can also produce false failures. This contradicts `report-landing-audit.py` line 45 ("Errors are never verdicts") and lines 80–81 (audited repos cannot be redirected).
5. **Real shallow clones with missing objects** are the sharpest case. A `--depth 1` clone of the lane, with three uncited round commits, exits **0 clean** (`round_commits=1 required=0`). With `GIT_SHALLOW_FILE=/dev/null` it fails closed with exit 2.

## Where the frozen auditor touches this state

| Site | Lines | Walks history | Effect of grafts or shallow |
|---|---|---|---|
| `round_commits`: `git log --format=… <branch>` in lane | 147–162 | yes | hides round commits, shrinking `required` |
| `report_cutoff`: `git log --diff-filter=A -- <rel>` in fleet | 165–168 | yes | fleet graft or shallow moves the cutoff |
| `lookup`: `cat-file --batch-check` | 100–132 | no | changes only when an object is missing (real shallow clone) |
| `load_source_urls`, `show HEAD:rel`, errata `show` | 208–224, 266, 339 | no | none |
| `git_env()` strips inherited `GIT_*` | 79–84 | n/a | env neutralizers never reach the auditor; `.git/info/grafts` and `.git/shallow` are repo-local and are not stripped |
| `git()` captures stderr | 87–97 | n/a | git's graft deprecation hint is captured and discarded (0-byte auditor stderr on the sampled clean runs) |

The auditor reads only `%H %an %at %s` from `git log` and `%at` from the cutoff walk, so parent changes act through reachability. Object lookups are unaffected for objects that are present.

## Fixture and matrix

Artifact: `out/GraftsFixture/graft-shallow-fixture.sh`. Reusable functions: `gf_build`, `gf_fault`, `gf_shim`, `gf_run`, `gf_plain_one`, `gf_promisor_probe`, `gf_matrix`.

- **Lane** (kama-shokunin): R0 `base: lane init`@900, C1 `round-1: work`@1000, C2 `round-1: measure`@1100, C3 `checkpoint(r1) save`@1150, C4 `round-1: late`@2050 (tip, post-report).
- **Fleet:** P0@1500, report commit F `round-1: report`@2000 (audit cutoff), P1@2100 (HEAD).
- **Citation families:** A cites C1–C3; B omits C2; C cites C3 only; D cites nothing.
- **Faults (11, plus fault-free control):** `lane-graft-hide-mid` (C3→C1); `lane-graft-tip-root`; `lane-graft-inject-decoy` (C1→orphan round commit); `lane-graft-hide-mid-converted` (same graft converted to a replace ref); `lane-shallow-tip` (C4); `lane-shallow-mid` (C2); `lane-realclone-depth1` (real shallow clone); `fleet-graft-cutoff-early` (F→orphan dated 1050); `fleet-shallow-at-report`; `fleet-shallow-at-head`.
- **Modes (6):** `none`; `nro` (`--no-replace-objects`); `nro-env` (`GIT_NO_REPLACE_OBJECTS=1`); `nograft` (`GIT_GRAFT_FILE=/dev/null`); `noshallow` (`GIT_SHALLOW_FILE=/dev/null`); `nro+nograft+noshallow`. These are injected at the git layer by a PATH shim.
- **Runs:** 11 faults × 4 families × 6 modes = 264 auditor runs per full matrix. Three full matrix runs (before and after the header and lazy-fetch-mode edits) gave byte-identical `results.tsv` and `plain-git-semantics.txt`.

Each fault × family cell is classified against the fault-free truth for the same family (`out/GraftsFixture/classify-results.py`). FALSE-CLEAN means truth failed and observed clean. FALSE-FAIL means truth clean and observed failed. UNDER-REPORT and OVER-REPORT mean the verdict is right but the defect list is a strict subset or superset. WRONG-DEFECTS means failed for a different reason, such as unresolved instead of omitted.

Frozen auditor (mode `none`):

| fault | A | B | C | D |
|---|---|---|---|---|
| lane-graft-hide-mid | OK | **FALSE-CLEAN** | UNDER-REPORT | UNDER-REPORT |
| lane-graft-tip-root | OK | **FALSE-CLEAN** | **FALSE-CLEAN** | **FALSE-CLEAN** |
| lane-graft-inject-decoy | **FALSE-FAIL** | OVER-REPORT | OVER-REPORT | OVER-REPORT |
| lane-graft-hide-mid-converted | OK | **FALSE-CLEAN** | UNDER-REPORT | UNDER-REPORT |
| lane-shallow-tip | OK | **FALSE-CLEAN** | **FALSE-CLEAN** | **FALSE-CLEAN** |
| lane-shallow-mid | OK | OK | UNDER-REPORT | UNDER-REPORT |
| lane-realclone-depth1 | **FALSE-FAIL** | WRONG-DEFECTS | WRONG-DEFECTS | **FALSE-CLEAN** |
| fleet-graft-cutoff-early | OK | **FALSE-CLEAN** | UNDER-REPORT | UNDER-REPORT |
| fleet-shallow-at-report | OK | OK | OK | OK |
| fleet-shallow-at-head | **FALSE-FAIL** | OVER-REPORT | OVER-REPORT | OVER-REPORT |

Counts across the 40 fault cells, by mode:

| mode | FALSE-CLEAN | FALSE-FAIL | REFUSED (exit 2) | OK | UNDER / OVER / WRONG-DEFECTS |
|---|---|---|---|---|---|
| none (frozen) | **10** | **3** | 0 | 11 | 8 / 6 / 2 |
| nro | 9 | 3 | 0 | 14 | 6 / 6 / 2 |
| nro-env | 9 | 3 | 0 | 14 | 6 / 6 / 2 |
| nograft | 5 | 2 | 0 | 24 | 4 / 3 / 2 |
| noshallow | 6 | 1 | 4 | 20 | 6 / 3 / 0 |
| nro+nograft+noshallow | **0** | **0** | 4 | 36 | 0 / 0 / 0 |

Fault-free controls: every mode is OK in all four families.

Key rows from `results.tsv` (columns: fault, family, mode, rc, status, round_commits, required, cutoff, defects):

- `lane-graft-hide-mid B none 0 clean 3 2 2000 -`: C2 hidden, silent clean.
- `lane-graft-hide-mid B nro 0 clean 3 2 2000 -`: `--no-replace-objects` does not help.
- `lane-graft-hide-mid B nograft 1 failed 4 3 2000 landed-omitted:0eaa7835487c`: `GIT_GRAFT_FILE` restores the verdict.
- `lane-graft-hide-mid-converted B none 0 clean 3 2 2000 -`, and `… B nro 1 failed 4 3 2000 landed-omitted:0eaa7835487c`: the replace-ref form is disabled by `--no-replace-objects`.
- `lane-shallow-tip D none 0 clean 1 0 2000 -`, and `… D noshallow 1 failed 4 3 2000 …`: a shallow tip hides three uncited round commits.
- `lane-realclone-depth1 D none 0 clean 1 0 2000 -`: real shallow clone, silent clean.
- `lane-realclone-depth1 D noshallow 2 could-not-evaluate … fatal: Failed to traverse parents of commit 21de6b6562a8…`: fails closed.
- `fleet-graft-cutoff-early B none 0 clean 4 1 1050 -`: fleet graft moves the cutoff from 2000 to 1050, so C2 becomes post-report.
- `fleet-shallow-at-head A none 1 failed 4 4 2100 landed-omitted:21de6b6562a8…`: false failure, since post-report C4 becomes required.
- `lane-graft-inject-decoy A none 1 failed 5 4 2000 landed-omitted:dbbea815eceb…`: injected parent, false failure.

Commit prefixes: C1 `2a737a80d3ce`, C2 `0eaa7835487c`, C3 `0ba8af856ef0`, C4 `21de6b6562a8`, R0 `b67a752`, decoy `dbbea815eceb`.

Plain git on `lane-graft-hide-mid` (`plain-git-semantics.txt`, `%h>%p subject`):

```
[none]    log master: 21de6b6>0ba8af8 round-1: late; 0ba8af8>2a737a8 checkpoint(r1) save; 2a737a8>b67a752 round-1: work; …
[nro]     log master: identical to [none]
[nograft] log master: 21de6b6>0ba8af8 round-1: late; 0ba8af8>0eaa783 checkpoint(r1) save; 0eaa783>2a737a8 round-1: measure; …
```

Under the graft, C3's parent shows as C1 (`2a737a8`). `cat-file -p` still shows the raw parent C2 (`0eaa783`).

Deprecation: git 2.56 prints `hint: Support for <GIT_DIR>/info/grafts is deprecated …` to stderr whenever grafts are used, and whenever `GIT_GRAFT_FILE` is set, even to `/dev/null`. `rev-parse --is-shallow-repository` is false when only grafts are present, so detection needs a file-existence check.

## Lazy-fetch exposure (`gf_promisor_probe`, `promisor-probe.tsv`)

The real shallow clone was also made a promisor remote (`ssh://example.invalid/x.git`, `core.sshCommand="touch <marker>; false"`, repo format 1). The fleet report cites the three missing lane commits by full 40-hex SHA.

| mode | rc | configured command | last stderr line |
|---|---|---|---|
| none (frozen) | 1 | **EXECUTED** | — |
| noshallow | 2 | **EXECUTED** | `fatal: Failed to traverse parents of commit 21de6b6562a8…` |
| nolazy (`GIT_NO_LAZY_FETCH=1`) | 1 | not executed | — |
| noshallow + nolazy | 2 | not executed | `fatal: Failed to traverse parents …` |
| noshallow + `--no-lazy-fetch` | 2 | not executed | `fatal: Failed to traverse parents …` |

Controls:
- A direct `git cat-file --batch-check <full sha>` executes the command at repo format 0 and at format 1.
- Abbreviated 12-hex citations do not trigger a fetch. The first exploratory attempt used 12-hex citations and showed no execution.
- `git log` traversal does not fetch. A direct `git log` with `GIT_SHALLOW_FILE=/dev/null` fails with "Failed to traverse parents" and executes nothing.

So the executed fetch comes from full-OID lookups, which `GIT_SHALLOW_FILE` does not affect. This is consistent with L1 probe (e). `GIT_SHALLOW_FILE` adds no exposure, but it does not close the path. `GIT_NO_LAZY_FETCH=1` (or `--no-lazy-fetch`) does.

## Implications for L1 (decision inputs; nothing changed in the lane)

- The "global `--no-replace-objects`" direction alone removes 1 of the 10 false cleans in this grid, the converted graft. It does nothing for `info/grafts` or `.git/shallow`.
- The measured set that closes the grid is `--no-replace-objects` + `GIT_GRAFT_FILE=/dev/null` + `GIT_SHALLOW_FILE=/dev/null` + `GIT_NO_LAZY_FETCH=1`. The last comes from the promisor probe; the matrix itself did not include it. Result: 0 false cleans and 0 false failures in the grid. The four real-shallow-clone cells become exit 2, a typed refusal. Fault-free controls are unchanged.
- Alternative, measured only as detection: refuse with exit 2 when `$GIT_DIR/info/grafts` exists, when `$GIT_DIR/shallow` exists or `rev-parse --is-shallow-repository` is true, or when `for-each-ref refs/replace` is non-empty, in either repo. The detection markers fired on all 10 faulted fixtures. This alternative does not address lazy fetch, so it would need its own promisor guard (`extensions.partialclone` or `remote.*.promisor`) or `GIT_NO_LAZY_FETCH`.
- Current state: the real lane and fleet have none of these markers, so neither option changes present verdicts. I did not re-run the rounds 10–22 ledger under any option.

## Not verified

- Only git 2.56.0. Other versions were not checked.
- The frozen auditor was not patched. Neutralizers were applied with PATH shims that inject the flags or env a fix would pass through `git()` or `git_env()`. That is equivalent by construction, but it is not a patch test of the candidate code.
- Historical ledger (rounds 10–22) not re-run under any mode.
- Not tested: `core.useReplaceRefs`, commit-graph, alternates, `log.follow` in `report_cutoff`, the `--report` draft path, SHA-256 object format, linked worktrees, a fleet-side real shallow clone (only the fleet `.git/shallow` boundary was tested), and partial-clone filters other than the single plain promisor configuration.
- The `nro+nograft+noshallow` row was measured without `GIT_NO_LAZY_FETCH`. The promisor probe measured the lazy-fetch guard separately, not in combination with the full grid.

## Files written

- `out/GraftsFixture/` (under the lane's `.ufo/waves/round-23/build/`): `graft-shallow-fixture.sh` (reusable fixture functions and matrix driver), `classify-results.py`, `graft-shallow-fixture.patch` (`git diff` of both new files from the scratch clone), `results.tsv`, `plain-git-semantics.txt`, `classification.txt`, `promisor-probe.tsv`, `run-info.txt`.
- `advice/GraftsFixture.md` (this file).
- Scratch only: `/tmp/kama-r23/GraftsFixture` (detached at `4fe9339f`; untracked `fixtures/`; `git add -N` index entries in the scratch clone only). Temp repos: matrix runs `/tmp/gf-matrix.H4ffJ3`, `/tmp/gf-matrix.nlnjJu`, `/tmp/gf-matrix.A6g5uz` (final, copied to out); promisor runs `/tmp/gf-promisor.xdbdEB` (exploratory, 12-hex) and `/tmp/gf-promisor.AJ8KS1` (final); probes `/tmp/gf-probe.Ks2WjG`, `/tmp/gf-single.wGDEkl`.
- Not written: the lane's tracked files, `.jj`, the Git index, the fleet root, sibling lanes, global config, `~/.omp`.
