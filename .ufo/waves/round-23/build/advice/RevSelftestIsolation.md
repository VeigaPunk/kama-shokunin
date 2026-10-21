# RevSelftestIsolation: selftest isolation and fault coverage

Axes: (1) whether the selftest inherits state; (2) whether it covers faults (a)–(e) and the working copy's new behavior; (3) where new cases fit without renaming the existing 50. Findings only. No production edit, no lane write, no commit, no tool install.

## Pinned state

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`: HEAD = master = `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. git 2.56.0, Python 3.14.8.
- The working copy of `tools/report-landing-audit.py` changed during review (read tags #D359 → #8D0A → #8374; 847 → 864 → 919 lines). Every line number below refers to a byte-exact snapshot, `/tmp/kama-r23/RevSelftestIsolation/snap-worktree.py` (sha256 `d0a96599ed0bf68103ac8bd107186ef1600c052d6646fc1a0f55db9b38517e22`, 919 lines). The frozen base is `base-4fe9339f.py` = `git show 4fe9339f:tools/report-landing-audit.py` (sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`, 847 lines).
- Observed in lane status during review, not created by me: `?? tests/report-audit/`.

## Findings

**F1 (high). The selftest body is unchanged, so its 50/50 covers only old behavior.** `diff` of base vs snapshot from `def _commit` (snap:528) to EOF is empty. The 47 literal check names match base exactly; the 3 loop labels (`round-must-equal`, `kind-must-equal`, `token-must-equal`) make 50. None of the snapshot's new behavior is asserted: `GIT_ISOLATION` (snap:91-95), strict `git()` decoding (107-126), the ref-name refusal in `lookup` (160-162), `surrogateescape` in `round_commits` (181), `check_history_repo` (426-446, called at 473-474), `resolve_branch` (449-457, used at 475), and the errata hex regex (390, 393). `selftest cases=50 failed=0` is not evidence for any of them.

**F2 (high). The selftest is blind to faults (a)–(e) on base and on the snapshot.** Both run `--selftest` to `cases=50 failed=0`, rc 0, while each fault reproduces on base (§4). Setting `i18n.logOutputEncoding=ISO-8859-1` on the shared lane under the base code also stays 50/50 (`out/…/probe-out/mut-a-base.selftest.txt`). The mechanism, verified: the only non-ASCII subject any fixture produces is the em dash in the `source-fixture` commit (snap:694-695). Its `%s` is the whole single-paragraph message, and git cannot encode the em dash in ISO-8859-1, so it emits the raw UTF-8 bytes and the fault never fires. A representable character does fire: subject `round-1: café` is emitted as `caf\xe9`, which is not UTF-8. So (a) is untriggered by accident. No fixture writes non-UTF-8 bytes (`_commit`, snap:535, writes with `encoding="utf-8"`), creates replace refs, or sets promisor config or `core.sshCommand`. The only `replace` tokens in `selftest()` are str `.replace(` calls (snap:744). The sibling `.ufo/waves/round-23/build/advice/MutExistingSelftest.md` (lines 30-32) independently shows that dropping `GIT_CONFIG_NOSYSTEM` and switching to `errors="replace"` both survive.

**F3 (medium). The selftest inherits nothing from outside, but its cases share state with each other.**
- Outside. Fixtures are fresh `git init -q -b master` repos under `TemporaryDirectory` (snap:559, 566-569) with no repo-local config writes. Positive control: `$HOME/.gitconfig` and a `GIT_CONFIG_SYSTEM` file, both setting `i18n.logOutputEncoding`, `log.showSignature`, `log.follow`, `core.sshCommand`, and a `diff.forge.textconv`; the process env had no `GIT_CONFIG_GLOBAL` or `GIT_CONFIG_NOSYSTEM`. Base and snapshot both gave `cases=50 failed=0`, rc 0. The decoy `GIT_DIR` probe (snap:563-564, check at 876-877) covers only `GIT_*` env.
- `/etc/gitconfig` and `/etc/git` are absent on this host, so no fixture can observe `GIT_CONFIG_NOSYSTEM` being dropped. The only in-selftest handle is a direct assertion on `git_env()` output.
- Inside. `lane` and `fleet` are shared, mutable, and order-dependent. `_commit(lane, source_fixture, …)` (snap:694-695) changes the lane for every later case, and `absent-source-registry-is-no-exemption` (snap:690-691) must run before it. Moving that commit ahead of the absent case gives `failed=1`, with exactly `FAIL absent-source-registry-is-no-exemption` (`probe-out/mut-order.selftest.txt`). Injecting a `git replace` of round commit `c` into the shared lane under base (M-c) fails 13 differently named cases (`probe-out/mut-c-base.selftest.txt`). A repo-local fault in shared state cannot be attributed to a single case.

**F4 (medium). A verdict change in the snapshot has no case: errata corrections must now be hex.** The snapshot's `apply_errata` (390-395) marks a correction invalid unless it matches `[0-9a-f]{7,40}`. A row `1<TAB>unresolved-full-hash<TAB><40-hex fabricated><TAB>master<TAB>probe` gives base `status=clean` (`errata_invalid=0`, since base resolves `master` as a commit) and the snapshot `status=failed` (`errata-invalid line=1 correction=master`, rc 1). No existing case tests a non-hex correction; the only invalid-correction case uses `"f"*40`, which is hex. Ledger impact: `registry/report-landing-errata.tsv` on master has 9 rows (8 `landed-omitted`, 1 `unresolved-full-hash`), and none has a non-hex correction (read with `git show master:…`), so the committed ledger is not affected.

**F5 (low). Docs and counts.** `git grep` finds no tracked file that pins `cases=50` or `50/50` for this tool, so adding cases breaks no pin. `SKILL.md:683` describes the selftest's coverage in prose and needs an update when cases land. `corpus/QUALITY.md:165` (KQ32) says Git-config/history and UTF-8/error hardening must be "demonstrated separately"; the new cases in §3 are that demonstration.

## 3. Where new cases go (Q3)

- **Insertion point.** Inside the `with tempfile` block of `selftest()`, after `check("inherited-GIT_DIR-untouched", …)` (snap:876-877) and before `failed = [...]` (snap:878). Lines 546–877 stay untouched, so the 47 literal names and 3 loop labels remain byte-identical and in order, and the new cases append after them. `check` and `is_error` are closures inside `selftest()`, so the block sits there or they are passed in. Alternative: `def _repo_local_cases(tmp, check, is_error)` after `_ns` (snap:542-544), called at snap:877.
- **Isolation.** Each new case uses its own fresh lane and fleet pair under `tmp`, never the shared `lane`/`fleet`. Each gets a clean control fixture so that a broken fixture cannot pass as the fault.
- **Assertions.** Assert exact defect `kinds`, or `EvalError` for refusals. Do not assert only `rc`: the sibling's killed mutant shows a bare nonzero exit can come from fixture setup.
- **Before-state evidence** (base crashing or flipping) stays out of the selftest, which runs current code only. It lives in `out/RevSelftestIsolation/probe-out`.
- **Setup helpers.** Setup goes through `git()`, so the `GIT_ISOLATION` flags also apply during fixture creation. `init`, `add`, `commit`, `config`, `tag`, `commit-tree` are safe. `replace` and `update-ref` through `git()` were not probed here; verify on the first run. `_commit` cannot write non-UTF-8 bytes, so fault (b) needs a bytes writer.

Proposed cases. Names are new; none collides with the 50.

| # | Proposed name | Fault | Fixture (fresh pair under tmp) | Assertion |
|---|---|---|---|---|
| 1 | `log-encoding-latin1-subject-verdict` | a | lane `i18n.logOutputEncoding=ISO-8859-1`; subject `round-1: café measure`; report cites all three | rc 0, kinds `[]`, required 3 |
| 2 | `invalid-utf8-committed-report-refused` | b | fleet report committed as bytes `\xff\xfe` | `EvalError`, not a traceback |
| 3 | `replace-ref-cannot-hide-round-commit` | c | `git replace c` with a non-round commit whose parent is b; report cites a and b only | kinds `[("landed-omitted", c)]` |
| 4 | `fabricated-replace-ref-unresolved` | d | `update-ref refs/replace/<fab> a`; fab appears in Work performed | kinds `[("unresolved-full-hash", fab)]` |
| 5 | `promisor-lane-refused-no-command` | e | `extensions.partialClone`, `remote.origin.promisor=true`, `remote.origin.url=ssh://example.invalid/x.git`, `core.sshCommand` = local script that appends to a marker file | `EvalError`; marker absent |
| 6 | `shallow-history-refused` | f | `.git/shallow` = c; report cites c | `EvalError` |
| 7 | `grafts-file-refused` | g | `.git/info/grafts` = c; report cites c | `EvalError` |
| 8 | `same-name-tag-cannot-shadow-branch` | i | tag `master` → b; report cites a and b | kinds `[("landed-omitted", c)]` |
| 9 | `ref-named-like-abbrev-refused` | j | tag `deadbee1` → a; Landed cites `deadbee1` | `EvalError` |
| 10 | `errata-correction-must-be-hex` | F4 | fabricated unresolved hash plus errata row with correction `master` | rc 1, errata_invalid 1 |
| 11 | `git-env-disables-global-and-system` | env | `git_env()["GIT_CONFIG_GLOBAL"] == os.devnull` and `git_env()["GIT_CONFIG_NOSYSTEM"] == "1"` | direct equality |

## 4. Probe matrix (evidence for Q2)

Fixture method: `lane` and `fleet` are `git init -b master` repos under `/tmp/kama-r23/RevSelftestIsolation/fixtures/<case>/`, with commit dates set through `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`. Audit command: `python3 <script> --lane-repo lane --fleet-repo fleet --rounds 1 --no-errata`, with env `PATH`, `HOME=/tmp/kama-r23/RevSelftestIsolation`, `LC_ALL=C.UTF-8`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`. Controls: three round commits (`round-1: work` 1000, `round-1:measure` 1100, `checkpoint(r1) save` 1150) all cited, report fleet commit at 1200, result clean on both. The probe driver was an inline Python session; its outputs are saved in `out/RevSelftestIsolation/probe-out/`.

| Case | Fixture delta | Base 4fe9339f | Snapshot | Selftest sees it |
|---|---|---|---|---|
| control | none | rc 0 clean | rc 0 clean | n/a |
| a | lane `i18n.logOutputEncoding=ISO-8859-1`; subject with é; all cited | rc 1, `UnicodeDecodeError` traceback | rc 0 clean (correct) | no |
| b | fleet report bytes `\xff\xfe` | rc 1, `UnicodeDecodeError` traceback | rc 2, could-not-evaluate (correct refusal) | no |
| c | `git replace c <non-round commit>`; cites a, b only | rc 0 clean (false) | rc 1, landed-omitted c (correct) | no |
| d | `refs/replace/<fabricated 40-hex>` → a; fabricated hash in prose | rc 0 clean (false) | rc 1, unresolved-full-hash (correct) | no |
| e | promisor lane, `core.sshCommand` = local marker script | rc 1; marker CREATED (repo-configured command executed) | rc 2, partial-clone refusal; marker absent | no |
| f | `.git/shallow` = c; cites c only | rc 0 clean (false) | rc 2, refusal | no |
| g | `.git/info/grafts` = c; cites c only | rc 0 clean (false) | rc 2, refusal | no |
| i | tag `master` → b; cites a and b | rc 0 clean (false) | rc 1, landed-omitted c (correct) | no |
| j | tag `deadbee1` → a; Landed cites `deadbee1` | rc 0 clean (false) | rc 2, "citation deadbee1 names a ref" | no |
| errata | fabricated unresolved hash; errata correction `master` | rc 0 clean | rc 1, errata-invalid | no |
| k | `*.md diff=forge` plus textconv printing cites for c | rc 1 (raw bytes used) | rc 1, identical | not reproduced: `git show HEAD:<path>` did not apply the textconv on 2.56.0 |

Selftests: base `cases=50 failed=0` rc 0; snapshot `cases=50 failed=0` rc 0; both with hostile global and system config (§3 F3) `cases=50 failed=0` rc 0. The hostile-config run printed only; its output is recorded here.

## 5. Limits and not verified

- Only git 2.56.0 and Python 3.14.8 on this host.
- `GIT_ISOLATION` members `log.showSignature=false`, `log.mailmap=false`, `log.showRoot=true`, `core.quotePath=true`, and `log.follow=false` have no fixture here. Their effect was not verified by me. Sibling advice (`ScoutShowSignature.md`, `ScoutMailmap.md`, `ScoutLogFollow.md`) covers those channels; I did not review it.
- `objects/info/alternates` is documented as unclaimed; not tested.
- The historical ledger was not run. The errata impact was checked by reading the committed file only.
- The snapshot may be superseded. Re-run the selftest and the new cases against the final file.

## Files written

- `.ufo/waves/round-23/build/advice/RevSelftestIsolation.md` (this report, new).
- `.ufo/waves/round-23/build/out/RevSelftestIsolation/probe-out/` (49 files: per-case stdout and stderr for base and snapshot, selftest and mutant outputs).
- `.ufo/waves/round-23/build/out/RevSelftestIsolation/worktree-vs-base.diff` and `snap-worktree.py.txt` (copies, not executable).
- Scratch outside the lane only: `/tmp/kama-r23/RevSelftestIsolation/` (base and snapshot copies, fixtures, mutants, fake-ssh marker script, hostile HOME and system config).
- Lane tracked files, index, `.jj`, and history were not touched. Git was used read-only (`status`, `show`, `diff`, `grep` with `GIT_OPTIONAL_LOCKS=0`). No tools were installed or updated.

## Correction to F5 (appended after writing)

F5's first sentence overstated. `git grep -e 'cases=50' -e '50/50'` (run with `GIT_OPTIONAL_LOCKS=0`) finds tracked historical records: `.ufo/waves/round-22/report-source-fix/runs/80a6d07c/audit-selftest.stdout:51` (`selftest cases=50 failed=0`), and prose in `LOG.md:901`, `SCORECARD.md:1139`, and `corpus/lessons/round-22.md:350` (50/50). Nothing enforces these counts; they stay true as history and need no edit. A future selftest prints `cases=50+k`, so do not treat those records as a current pin.
