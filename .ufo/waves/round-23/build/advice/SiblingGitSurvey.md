# SiblingGitSurvey — static survey of git invocations (round-23 build, read-only)

Seat: `CloseKama22.SiblingGitSurvey` (executor, leaf). Scope: every git subprocess invocation in `tools/*.py` and `tests/**/*.py`, with argv, env handling, text/bytes mode, output use, and repo-local-state exposure. Survey only; nothing was fixed.

Snapshots:
- Working tree of `/home/vgpnk/Projects/shokunin/kama-shokunin`, scanned 2026-10-21T15:32:57Z (`survey-worktree.*`).
- Base `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` read via `git --no-replace-objects --no-lazy-fetch cat-file` (`survey-4fe9339f….*`).

Live-edit caveat: while the survey ran, `tools/report-landing-audit.py` changed four times (sha `684764…` → `f228f1…`, 924 → 928 lines) and `tests/report-audit/repo-state-grid.py` changed at least three times (`7f3110…` → `0df189…`, 675 → 706 lines). Every line number below is from the final snapshot whose hashes are in Appendix A. Re-run the scanner at integration before relying on line numbers.

## 1. Results

- **Working tree:** 19 files, 38 subprocess-family calls, **117 git records** (18 direct, 95 via a thin helper, 4 argv literal) in 7 files. 12 files contain no git.
- **Base 4fe9339f:** 17 files, 27 calls, **44 git records** (9 direct, 31 via helper, 4 literal) in 6 files.
- **Non-git subprocess:** 16 with a known executable, plus 4 whose argv is not statically known; all 4 were checked by hand and none is git (Appendix C). No `shell=True`, no `os.system`/`os.popen`.
- **Only tool changed between base and working tree:** `tools/report-landing-audit.py`. Its 27 git sites now all carry `--no-replace-objects --no-lazy-fetch` and `-c` overrides; base had 21 sites with neither. The other six tool files are byte-identical to base (same sha).
- **Still without replace-off and lazy-off on every site:** `tools/citation-provenance.py` (9/9), `tools/error-verdict-census.py` (7/7), `tools/sources-append-only.py` (3/3), `tests/llamacpp-live/install-links-grid.py` (2/2), `tests/llamacpp-live/install-io-grid.py` (2/2 lazy; replace-off via env), `tests/report-audit/repo-state-grid.py` (67/67, fixture helper).
- **Highest-risk pattern:** repo-read bytes executed without a digest pin — `install-links-grid.py` (direct L69, via L215) and `repo-state-grid.py` (`frozen_auditor` L631 → written to a temp file and run with `sys.executable` at L603).

## 2. Shared repo-local-state exposure (flagged, not fixed)

Labels: **REPLACE-REFS** = `--no-replace-objects` absent and `GIT_NO_REPLACE_OBJECTS` not in env. **LAZY-FETCH** = `--no-lazy-fetch` absent and `GIT_NO_LAZY_FETCH` not in env. **REPO-CFG-UNOVERRIDDEN** = no `-c` override (repo `.git/config` read unmodified). **ENV-AMBIENT** = env inherits full `os.environ` (GIT_DIR, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_INDEX_FILE, …). **ENV-CALLER** = env comes from a parameter. **HASH-PINNED** = output sha256-compared before use. **EXECUTED** = output compiled or run.

| Group | Exposure signature | Sites (final snapshot line numbers) | Status |
| --- | --- | --- | --- |
| A | REPLACE-REFS, LAZY-FETCH, REPO-CFG-UNOVERRIDDEN, ENV-AMBIENT | `citation-provenance.py` G01, G02, G04, G05 (production); `sources-append-only.py` G44–G46; `install-links-grid.py` G49, G50 (EXECUTED) | Unisolated; caller-supplied repo in the two tools |
| B | REPLACE-REFS, LAZY-FETCH, REPO-CFG-UNOVERRIDDEN; env sanitised | `error-verdict-census.py` G10, G12 (pinned, L151); `install-io-grid.py` G47, G48 (replace off via env; pinned L213; EXECUTED) | Pinned outputs fail closed on content, not on side effects |
| C | Fixture helper, no isolation, planted repo-local config | `repo-state-grid.py` G51–G117 (fixtures build in `tmp`); G55/G115 `frozen_auditor` (fixed lane, executed) | Test instrument only |
| D | Isolated wrapper; residual ENV-CALLER and unoverridden keys | `report-landing-audit.py` G17–G43 | Only group with replace-off, lazy-off, and log overrides |

Target classes: caller-supplied repos are `citation-provenance` (`lane`), `error-verdict-census` (`lane`), `sources-append-only` (`--repo`), and `report-landing-audit` (`--lane-repo`, `--fleet-repo`). Fixed-lane reads are `install-io-grid` (`LANE`), `install-links-grid` (`LANE`), and `repo-state-grid` `frozen_auditor` (`LANE_DIR`).

## 3. Findings (ranked; static; nothing run)

**F1 [high] `tools/sources-append-only.py` `git_show` (def L280, subprocess L287, callers L303–304).** `git -C <repo> show <rev>:<path>` with no replace/lazy isolation and an ambient env. Output is decoded strictly (`decode_blob`, L273–277) and parsed as the append-only registry. Repo-local replace refs or grafts on the compared revs can change the registry being compared and yield "no append-only violations", exit 0. The rev guard (L284) rejects a leading `-` and any `:` in the revision; it does not touch replace refs or lazy fetch. Nothing contains this path. [INFERENCE on replace/graft semantics; not run.]

**F2 [high, fixed-lane harness] `tests/llamacpp-live/install-links-grid.py` `frozen_producer` (def L68, subprocess L69, `load_source`/`exec` L61–65, call L215).** `git show FROZEN_REV:tools/kama-llamacpp-live.py` (FROZEN_REV `7a6bc911…`, L49) inherits full `os.environ`, has no replace/lazy isolation, no digest comparison, and the bytes are `exec(compile(…))`d in-process. A replace ref or promisor object on that chain would run attacker-chosen code inside the harness. Scope: the repo read is the lane's own `.git`, so this needs a writable untrusted `.git` in the lane. Same class: `tests/report-audit/repo-state-grid.py` `frozen_auditor` (def L630, subprocess L631) writes the blob to a temp file, and `run_case` runs it as a child process with `sys.executable` (L603). That env strips `GIT_*` but has no replace/lazy isolation and no digest pin (`auditor_sha256` is recorded only).

**F3 [medium] `tools/citation-provenance.py`.** `git_blob` (def L38, subprocess L41) is digest-pinned (`hashlib.sha256(raw)`, L50; compared in `check` L102), so a substituted blob fails closed as `mismatch`. Two gaps remain. (a) `rev-parse --git-dir` (L72) and `merge-base --is-ancestor rev origin/master` (L105–108) are rc-only and unisolated; `off-ref` is decided on that return code (L109–110, `allow_off_ref` defaults to false), so replace refs or grafts could flip the status [INFERENCE]. (b) Lazy fetch can run repo-configured commands before the digest check; the L1 probe observed this mechanism for `cat-file --batch-check` (probe item e). All four production sites inherit full `os.environ`.

**F4 [medium] `tools/error-verdict-census.py` `git_show` (def L141, subprocess L143, digest check L151) and its callers (G12 L315; G11 selftest L421).** `env_for` (L68–72) sets `GIT_CONFIG_GLOBAL`/`NOSYSTEM` and `GIT_OPTIONAL_LOCKS` but not replace or lazy. A substituted object is refused by `FROZEN_SOURCE_SHA256`, but lazy-fetch side effects are not refused. The pinned bytes are then executed: `run_survivor` writes them and runs them through `child([sys.executable, …])` (L287–298). A digest pin does not contain side effects.

**F5 [info] `tests/llamacpp-live/install-io-grid.py` `frozen_source` (def L207, env L208–210, subprocess L211, digest L213, `load` exec L51, call L282–284).** Best-pinned frozen read in the set: `GIT_NO_REPLACE_OBJECTS=1`, config isolation, digest before exec. Residual: no `GIT_NO_LAZY_FETCH`.

**F6 [positive, working copy] `tools/report-landing-audit.py` `git()` (def L108, subprocess L114).** Argv (G17, final snapshot): `--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false -c log.showRoot=true -c log.showSignature=false -c log.mailmap=false`. Env is `os.environ` minus `GIT_*` plus `GIT_CONFIG_GLOBAL`/`NOSYSTEM`. Stdout is decoded UTF-8 strict (UnicodeDecodeError becomes `EvalError`, L122–126); `surrogateescape` only for `log -z` in `round_commits` (L183–184) and `ls-tree` in `parse_rounds` (L417–418). Residuals: (i) `env` parameter (ENV-CALLER; only selftest helpers pass `env=`, built by `git_env()`); (ii) repo-local config keys outside the overrides (REPO-CFG-PARTIAL); (iii) `show HEAD:rel` (G28) and `show <tip>:ERRATA` (G24) use `git show`, whose textconv default is not verified (see §6). Base `4fe9339f`: all 21 sites `text=True`; 19 have no `-c` override; none has replace or lazy flags.

**F7 [info] `tests/report-audit/repo-state-grid.py` `g()` (def L52).** Fixtures plant repo-local state on purpose inside `tmp`-built repos: `i18n.logOutputEncoding` UTF-16 (L187) and ISO-8859-1 (L219); replace and fabricated refs (L238, L248, L266); promisor / blobless clones (L206, L209, L493–495); `gpg.program` config (L330–331). These exercise `report-landing-audit`; they do not touch the lane.

**F8 [info] `tools/error-verdict-census.py` `git_fixture` (def L243, loop L251–255, child call L252).** Literal git commands in a temp dir. Only the last `run` output is read (`run[2].strip()`, L255, rev-parse). `init`/`add`/`commit` outputs are unused.

Failure-class mapping (static presence only; does not re-test L1 faults):

| L1 class | Sites present in working tree | Status |
| --- | --- | --- |
| (a) i18n log re-encoding | `report-landing-audit` log sites G18, G26 | Override present (`i18n.logOutputEncoding=UTF-8`); base had none |
| (b) non-UTF-8 committed report | G28 `show HEAD:rel`, strict decode | Decode is strict in working copy; base text mode |
| (c)/(d) replace refs, fabricated refs | RP present: citation 9, census 7, sources 3, install-links 2, install-io (replace off), repo-state 67 (fixture) | Not isolated outside `report-landing-audit` |
| (e) lazy fetch runs config | LZ present: citation 9, census 7, sources 3, install-links 2, install-io 2, repo-state 67 (fixture); `report-landing-audit` 0 | Not isolated outside `report-landing-audit` |

## 4. Per-file summary (final snapshot; counts from `survey-worktree.json`)

| file | sites (direct/via/literal) | no RP | no LZ | ENV-AMBIENT | no cfg override | text mode | HASH | EXEC | parse | fixture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tools/citation-provenance.py | 9 (4/5/0) | 9 | 9 | 4 | 8 | 5 | 2 | 0 | 1 | 5 |
| tools/error-verdict-census.py | 7 (1/2/4) | 7 | 7 | 0 | 6 | 0 | 1 | 0 | 4 | 5 |
| tools/report-landing-audit.py | 27 (1/26/0) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 7 |
| tools/sources-append-only.py | 3 (1/2/0) | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 3 | 0 |
| tests/llamacpp-live/install-io-grid.py | 2 (1/1/0) | 0 | 2 | 0 | 2 | 0 | 2 | 1 | 1 | 0 |
| tests/llamacpp-live/install-links-grid.py | 2 (1/1/0) | 2 | 2 | 2 | 2 | 2 | 0 | 2 | 1 | 0 |
| tests/report-audit/repo-state-grid.py | 67 (9/58/0) | 67 | 67 | 0 | 64 | 0 | 0 | 0 | 60 | 0 |

Base `4fe9339f` for `report-landing-audit.py` (21 sites): no RP 21, no LZ 21, text mode 21, no cfg override 19, parse 11. The other six files are identical to the working tree.

## 5. Manual corrections to automatic labels

- **G48** (`install-io-grid` L282): the `parse` label is `.startswith(` inside `evaluate()`. Actual use: sha256 (L283), then `exec` through `load()` (L51, call L284).
- **G50** (`install-links-grid` L215): `parse` comes from `proc.stderr.strip()` in the error path of `frozen_producer`. Actual use: exec only.
- **G115** (`repo-state-grid` L656) and **G55** (L631): labelled raw/parse; actual use is write to a temp file, then run as a child process (`run_case` L603). Treat as EXECUTED.
- **G11 / G12**: outputs are digest-pinned inside `git_show` (G10, L151), then executed by `run_survivor` (census L287–298, child at L295).
- **G13–G15**: `parse` is function-level (`run[2].strip()` after the loop). Only G16 (rev-parse) output is used.
- **G44–G46**: strict decode happens in `decode_blob` (ParseError → exit 2), so the decode column does not show it.
- **G54** (`repo-state-grid` L384): `timeout 5 git …`. The scanner's first pass missed it; the prefix is now recognised.
- **Target classes** for `repo-state-grid` `g()` are heuristic ("caller-supplied"); they are fixtures under `tmp`.

## 6. Not verified / limits

- Static only. No selftests, probes, or git experiments were run. Fault-grid claims from L1 are not re-verified here.
- Output-use labels are heuristic: name-flow within one function plus one level of local-helper inspection. Corrections are in §5.
- Replace/graft/lazy-fetch effects are standard git semantics, not observed; they are marked [INFERENCE] where cited.
- Textconv: the local `git-show(1)` (2.56) says textconv is enabled by default only for `git diff` and `git log` (not `git show`); `git-cat-file(1)` makes `--textconv` opt-in. Not verified at runtime, so `git show` sites (G11, G12, G24, G28, G44–G46, G49, G50, census/sources show) keep a residual [INFERENCE].
- Git invocations inside bash probes or scripts (`probe check`, fault-control wrappers) are not analysed; only the bash call is visible.
- `git` resolved via PATH; not checked against a specific binary.

## 7. Tools, installs, files

- **Installs / updates:** none. Used system `python3` 3.14 and system `git` 2.56.0 (read-only: `ls-tree` and `cat-file` in `--rev` mode with `--no-replace-objects --no-lazy-fetch`, sanitized env, no writes). Local man pages read with `zcat`/`sed`.
- **Files written** (all under `.ufo/waves/round-23/build/`):
  - `out/SiblingGitSurvey/survey.py`
  - `out/SiblingGitSurvey/survey-worktree.txt`, `survey-worktree.json`
  - `out/SiblingGitSurvey/survey-4fe9339f8fc3a4a4a479d9c938a850da12f1124d.txt`, `.json`
  - `advice/SiblingGitSurvey.md` (this report)
- `survey.py` was authored directly in `out/SiblingGitSurvey/` rather than a scratch clone, as the task asked. It is read-only analysis and touches no tracked lane file. No commits, no pushes, no lane tracked file changed.
- **Re-run:** `python3 .ufo/waves/round-23/build/out/SiblingGitSurvey/survey.py` (working tree) and `… survey.py --rev 4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (base).
- **Checks the main agent should run:** re-run the survey after integration and compare the sha list (Appendix A); the lane is still being edited.

## Appendix A — snapshot hashes (scanned bytes)

Working tree (final, 2026-10-21T15:32:57Z):

- `414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0` 351L `tools/citation-provenance.py`
- `f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7` 468L `tools/error-verdict-census.py`
- `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7` 928L `tools/report-landing-audit.py`
- `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` 619L `tools/sources-append-only.py`
- `c10de62fd57f235d151ca13a4951642502ab163534d87742572119ac404706dc` 299L `tests/llamacpp-live/install-io-grid.py`
- `e43c6faa01bff703cffde9114e469f77e8f42c8ff969650d36f43a31429effcf` 399L `tests/llamacpp-live/install-links-grid.py`
- `0df18904d29a12f2c454525d4314d130bbbaf9e18275a59c63769f7cce3759e8` 706L `tests/report-audit/repo-state-grid.py`
- `10cfd0c4fd8363a07bc14d30c223d078db4bf9c1dafffac4e41027ab0d057c31` 125L `tests/report-audit/isolation-mutants.py`

Base `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`: `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f` 847L `tools/report-landing-audit.py` (the only tool whose sha differs from the working tree). All other scanned tool and test files have identical sha in both snapshots.

## Appendix B — every git invocation (117 records, working tree final snapshot)

Columns: id | file:line | route | enclosing function | subcommand + target | env | io mode/decode | output use | exposure labels (RP=REPLACE-REFS, LZ=LAZY-FETCH, AMB=ENV-AMBIENT, ENVC=ENV-CALLER, CFG=REPO-CFG-UNOVERRIDDEN, CFGp=REPO-CFG-PARTIAL, LOGENC/LOGFOL=LOG-ENCODING/LOG-FOLLOW, SD/LD=STRICT/LOSSY-DECODE, HP=HASH-PINNED, EX=EXECUTED, FX=FIXTURE-ONLY). Labels as emitted by the scanner; §5 lists corrections.

G01 | tools/citation-provenance.py:72 | direct | check | rev-parse lane | AMB-full | bytes/raw | rc-only | RP LZ AMB CFG
G02 | tools/citation-provenance.py:41 | direct | git_blob | cat-file lane | AMB-full | bytes/raw | hash | RP LZ AMB CFG HP
G03 | tools/citation-provenance.py:136 | direct | selftest > git | *argv lane | env-explicit | text/strict | raw | RP LZ CFG SD FX
G04 | tools/citation-provenance.py:105 | direct | check | merge-base lane | AMB-full | bytes/raw | rc-only | RP LZ AMB CFG
G05 | tools/citation-provenance.py:96 | via git_blob()@L38 | check | cat-file lane | AMB-full | bytes/raw | hash | RP LZ AMB CFG HP
G06 | tools/citation-provenance.py:140 | via git()@L135 | selftest | init lane | env-explicit | text/strict | discarded | RP LZ CFG SD FX
G07 | tools/citation-provenance.py:143 | via git()@L135 | selftest | add lane | env-explicit | text/strict | discarded | RP LZ CFG SD FX
G08 | tools/citation-provenance.py:144 | via git()@L135 | selftest | commit lane | env-explicit | text/strict | discarded | RP LZ CFGp SD FX
G09 | tools/citation-provenance.py:146 | via git()@L135 | selftest | rev-parse lane | env-explicit | text/strict | parse | RP LZ CFG SD FX
G10 | tools/error-verdict-census.py:143 | direct | git_show | show lane | env-explicit(keys) | bytes/raw | hash | RP LZ CFG HP
G11 | tools/error-verdict-census.py:421 | via git_show()@L141 | selftest | show Path(lane).resolve() | env-explicit(keys) | bytes/raw | raw | RP LZ CFG FX
G12 | tools/error-verdict-census.py:315 | via git_show()@L141 | census | show lane | env-explicit(keys) | bytes/raw | raw | RP LZ CFG
G13 | tools/error-verdict-census.py:246 | literal->child()@L252 | git_fixture | init cwd=work | env-caller(explicit) | bytes/lossy:replace | parse | RP LZ ENVC CFG LD FX
G14 | tools/error-verdict-census.py:247 | literal->child()@L252 | git_fixture | add cwd=work | env-caller(explicit) | bytes/lossy:replace | parse | RP LZ ENVC CFG LD FX
G15 | tools/error-verdict-census.py:248 | literal->child()@L252 | git_fixture | commit cwd=work | env-caller(explicit) | bytes/lossy:replace | parse | RP LZ ENVC CFGp LD FX
G16 | tools/error-verdict-census.py:250 | literal->child()@L252 | git_fixture | rev-parse cwd=work | env-caller(explicit) | bytes/lossy:replace | parse | RP LZ ENVC CFG LD FX
G17 | tools/report-landing-audit.py:114 | direct | git | *args repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G18 | tools/report-landing-audit.py:183 | via git()@L108 | round_commits | log lane_repo | env-caller(minus-GIT_*) | bytes/lossy:surrogateescape | parse | ENVC CFGp LD
G19 | tools/report-landing-audit.py:256 | via git()@L108 | load_source_urls | cat-file lane_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G20 | tools/report-landing-audit.py:478 | via git()@L108 | run | rev-parse fleet_repo | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD
G21 | tools/report-landing-audit.py:539 | via git()@L108 | _commit | add repo | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD
G22 | tools/report-landing-audit.py:540 | via git()@L108 | _commit | commit repo | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD
G23 | tools/report-landing-audit.py:144 | via git()@L108 | lookup | cat-file repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G24 | tools/report-landing-audit.py:371 | via git()@L108 | load_errata | show lane_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G25 | tools/report-landing-audit.py:563 | via git()@L108 | selftest | init tmp | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD FX
G26 | tools/report-landing-audit.py:204 | via git()@L108 | report_cutoff | log fleet_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G27 | tools/report-landing-audit.py:248 | via git()@L108 | load_source_urls | ls-tree lane_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G28 | tools/report-landing-audit.py:298 | via git()@L108 | audit_round | show fleet_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G29 | tools/report-landing-audit.py:417 | via git()@L108 | parse_rounds | ls-tree fleet_repo | env-caller(minus-GIT_*) | bytes/lossy:surrogateescape | parse | ENVC CFGp LD
G30 | tools/report-landing-audit.py:431 | via git()@L108 | check_history_repo | rev-parse repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G31 | tools/report-landing-audit.py:434 | via git()@L108 | check_history_repo | rev-parse repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G32 | tools/report-landing-audit.py:445 | via git()@L108 | check_history_repo | config repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G33 | tools/report-landing-audit.py:541 | via git()@L108 | _commit | rev-parse repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G34 | tools/report-landing-audit.py:436 | via git()@L108 | check_history_repo | rev-parse repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G35 | tools/report-landing-audit.py:455 | via git()@L108 | resolve_branch | rev-parse lane_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G36 | tools/report-landing-audit.py:571 | via git()@L108 | selftest | init repo | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD FX
G37 | tools/report-landing-audit.py:612 | via git()@L108 | selftest | commit fleet | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD FX
G38 | tools/report-landing-audit.py:439 | via git()@L108 | check_history_repo | rev-parse repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G39 | tools/report-landing-audit.py:458 | via git()@L108 | resolve_branch | rev-parse lane_repo | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD
G40 | tools/report-landing-audit.py:606 | via git()@L108 | selftest | rm fleet | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD FX
G41 | tools/report-landing-audit.py:611 | via git()@L108 | selftest | add fleet | env-caller(minus-GIT_*) | bytes/strict | discarded | ENVC CFGp SD FX
G42 | tools/report-landing-audit.py:784 | via git()@L108 | selftest | hash-object lane | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD FX
G43 | tools/report-landing-audit.py:825 | via git()@L108 | selftest | rev-parse lane | env-caller(minus-GIT_*) | bytes/strict | parse | ENVC CFGp SD FX
G44 | tools/sources-append-only.py:287 | direct | git_show | show repo | AMB-full | bytes/raw | parse | RP LZ AMB CFG
G45 | tools/sources-append-only.py:303 | via git_show()@L280 | run_check | show args.repo | AMB-full | bytes/raw | parse | RP LZ AMB CFG
G46 | tools/sources-append-only.py:304 | via git_show()@L280 | run_check | show args.repo | AMB-full | bytes/raw | parse | RP LZ AMB CFG
G47 | tests/llamacpp-live/install-io-grid.py:211 | direct | frozen_source | show LANE | env-explicit | bytes/raw | hash | LZ CFG HP
G48 | tests/llamacpp-live/install-io-grid.py:282 | via frozen_source()@L207 | main | show LANE | env-explicit | bytes/raw | exec+hash+parse | LZ CFG HP EX
G49 | tests/llamacpp-live/install-links-grid.py:69 | direct | frozen_producer | show LANE | AMB-full | text/strict | exec | RP LZ AMB CFG SD EX
G50 | tests/llamacpp-live/install-links-grid.py:215 | via frozen_producer()@L68 | run | show lane | AMB-full | text/strict | exec+parse | RP LZ AMB CFG SD EX
G51 | tests/report-audit/repo-state-grid.py:53 | direct | g | *args repo | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G52 | tests/report-audit/repo-state-grid.py:282 | direct | f_lazy_fetch | cat-file lane | env-minus-GIT_* | bytes/raw | discarded | RP LZ CFG
G53 | tests/report-audit/repo-state-grid.py:332 | direct | f_signature_program | log lane | env-minus-GIT_* | bytes/raw | discarded | RP LZ CFG LOGENC LOGFOL
G54 | tests/report-audit/repo-state-grid.py:384 | direct [prefix] | f_mailmap_fifo | log lane | env-minus-GIT_* | bytes/raw | rc-only | RP LZ CFG LOGENC LOGFOL
G55 | tests/report-audit/repo-state-grid.py:631 | direct | frozen_auditor | cat-file LANE_DIR | env-minus-GIT_* | bytes/raw | raw | RP LZ CFG
G56 | tests/report-audit/repo-state-grid.py:188 | direct | f_utf16_cutoff | log fleet | env-minus-GIT_* | bytes/raw | raw | RP LZ CFG LOGENC LOGFOL
G57 | tests/report-audit/repo-state-grid.py:209 | direct | f_promisor_pack | cat-file clone | env-minus-GIT_* | bytes/raw | parse | RP LZ CFG
G58 | tests/report-audit/repo-state-grid.py:220 | direct | f_log_encoding | log lane | env-minus-GIT_* | bytes/raw | raw | RP LZ CFG LOGENC LOGFOL
G59 | tests/report-audit/repo-state-grid.py:442 | direct | f_quote_path | ls-tree fleet | env-minus-GIT_* | bytes/raw | raw | RP LZ CFG
G60 | tests/report-audit/repo-state-grid.py:64 | via g()@L52 | init | *args path.parent | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G61 | tests/report-audit/repo-state-grid.py:76 | via g()@L52 | commit | add repo | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G62 | tests/report-audit/repo-state-grid.py:78 | via g()@L52 | commit | commit repo | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFGp LD
G63 | tests/report-audit/repo-state-grid.py:81 | via g()@L52 | commit | rev-parse repo | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G64 | tests/report-audit/repo-state-grid.py:93 | via g()@L52 | raw_commit | hash-object repo | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G65 | tests/report-audit/repo-state-grid.py:156 | via g()@L52 | c_shared_clone | clone tmp | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G66 | tests/report-audit/repo-state-grid.py:187 | via g()@L52 | f_utf16_cutoff | config fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G67 | tests/report-audit/repo-state-grid.py:199 | via g()@L52 | f_promisor_pack | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G68 | tests/report-audit/repo-state-grid.py:200 | via g()@L52 | f_promisor_pack | config lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G69 | tests/report-audit/repo-state-grid.py:202 | via g()@L52 | f_promisor_pack | clone tmp | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFGp LD
G70 | tests/report-audit/repo-state-grid.py:219 | via g()@L52 | f_log_encoding | config lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G71 | tests/report-audit/repo-state-grid.py:238 | via g()@L52 | f_replace_omission | replace lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G72 | tests/report-audit/repo-state-grid.py:248 | via g()@L52 | f_replace_fabricated | update-ref lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G73 | tests/report-audit/repo-state-grid.py:257 | via g()@L52 | f_replace_report | rev-parse fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G74 | tests/report-audit/repo-state-grid.py:259 | via g()@L52 | f_replace_report | hash-object fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G75 | tests/report-audit/repo-state-grid.py:260 | via g()@L52 | f_replace_report | mktree fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G76 | tests/report-audit/repo-state-grid.py:261 | via g()@L52 | f_replace_report | mktree fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G77 | tests/report-audit/repo-state-grid.py:262 | via g()@L52 | f_replace_report | mktree fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G78 | tests/report-audit/repo-state-grid.py:263 | via g()@L52 | f_replace_report | mktree fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G79 | tests/report-audit/repo-state-grid.py:266 | via g()@L52 | f_replace_report | replace fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G80 | tests/report-audit/repo-state-grid.py:295 | via g()@L52 | f_log_follow | mv fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G81 | tests/report-audit/repo-state-grid.py:296 | via g()@L52 | f_log_follow | commit fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G82 | tests/report-audit/repo-state-grid.py:298 | via g()@L52 | f_log_follow | config fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G83 | tests/report-audit/repo-state-grid.py:309 | via g()@L52 | f_show_root | rm fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G84 | tests/report-audit/repo-state-grid.py:310 | via g()@L52 | f_show_root | commit fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G85 | tests/report-audit/repo-state-grid.py:313 | via g()@L52 | f_show_root | config fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G86 | tests/report-audit/repo-state-grid.py:329 | via g()@L52 | f_signature_program | update-ref lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G87 | tests/report-audit/repo-state-grid.py:330 | via g()@L52 | f_signature_program | config lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G88 | tests/report-audit/repo-state-grid.py:331 | via g()@L52 | f_signature_program | config lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G89 | tests/report-audit/repo-state-grid.py:366 | via g()@L52 | f_tag_shadow | tag lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G90 | tests/report-audit/repo-state-grid.py:375 | via g()@L52 | f_ref_abbrev | tag lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G91 | tests/report-audit/repo-state-grid.py:419 | via g()@L52 | _bad_subject | update-ref lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G92 | tests/report-audit/repo-state-grid.py:438 | via g()@L52 | f_quote_path | add fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G93 | tests/report-audit/repo-state-grid.py:439 | via g()@L52 | f_quote_path | commit fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G94 | tests/report-audit/repo-state-grid.py:441 | via g()@L52 | f_quote_path | config fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G95 | tests/report-audit/repo-state-grid.py:462 | via g()@L52 | f_subject_injection | update-ref lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G96 | tests/report-audit/repo-state-grid.py:469 | via g()@L52 | f_huge_timestamp | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G97 | tests/report-audit/repo-state-grid.py:473 | via g()@L52 | f_huge_timestamp | hash-object lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G98 | tests/report-audit/repo-state-grid.py:475 | via g()@L52 | f_huge_timestamp | update-ref lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G99 | tests/report-audit/repo-state-grid.py:493 | via g()@L52 | t_blobless | config lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G100 | tests/report-audit/repo-state-grid.py:495 | via g()@L52 | t_blobless | clone tmp | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFGp LD
G101 | tests/report-audit/repo-state-grid.py:206 | via g()@L52 | f_promisor_pack | config clone | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G102 | tests/report-audit/repo-state-grid.py:236 | via g()@L52 | f_replace_omission | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G103 | tests/report-audit/repo-state-grid.py:281 | via g()@L52 | f_lazy_fetch | config lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G104 | tests/report-audit/repo-state-grid.py:327 | via g()@L52 | f_signature_program | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G105 | tests/report-audit/repo-state-grid.py:417 | via g()@L52 | _bad_subject | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G106 | tests/report-audit/repo-state-grid.py:460 | via g()@L52 | f_subject_injection | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G107 | tests/report-audit/repo-state-grid.py:239 | via g()@L52 | f_replace_omission | log lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LOGENC LOGFOL LD
G108 | tests/report-audit/repo-state-grid.py:249 | via g()@L52 | f_replace_fabricated | cat-file lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G109 | tests/report-audit/repo-state-grid.py:267 | via g()@L52 | f_replace_report | show fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G110 | tests/report-audit/repo-state-grid.py:351 | via g()@L52 | f_shallow | rev-list lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G111 | tests/report-audit/repo-state-grid.py:359 | via g()@L52 | f_grafts | rev-list lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G112 | tests/report-audit/repo-state-grid.py:367 | via g()@L52 | f_tag_shadow | rev-parse lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G113 | tests/report-audit/repo-state-grid.py:376 | via g()@L52 | f_ref_abbrev | cat-file lane | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G114 | tests/report-audit/repo-state-grid.py:509 | via g()@L52 | f_nested_subdir | rev-parse sub | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LD
G115 | tests/report-audit/repo-state-grid.py:656 | via frozen_auditor()@L630 | main | cat-file LANE_DIR | env-minus-GIT_* | bytes/raw | parse | RP LZ CFG
G116 | tests/report-audit/repo-state-grid.py:299 | via g()@L52 | f_log_follow | log fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LOGENC LOGFOL LD
G117 | tests/report-audit/repo-state-grid.py:314 | via g()@L52 | f_show_root | log fleet | env-minus-GIT_* | bytes/lossy:surrogateescape | parse | RP LZ CFG LOGENC LOGFOL LD

## Appendix C — non-git subprocess inventory (checked)

Known executable (16; all non-git by argv head):

- tools/citation-provenance.py:178 sys.executable (cli_case)
- tools/kama-llamacpp-live.py:813 bash probe (run_probe)
- tools/kama-ollama-evidence.py:401 sys.executable (run_selftest)
- tests/llamacpp-live/check-receipt.py:2317, :2293 sys.executable (_selftest)
- tests/llamacpp-live/install-io-grid.py:258 sys.executable (selftest)
- tests/llamacpp-live/install-tree-grid.py:72, :223 sys.executable (gate_verdict; run_selftest/check_case)
- tests/llamacpp-live/unpinnable-e2e.py:87 sys.executable (main)
- tests/ollama-corpus-guard/check.py:376 sys.executable (measure_test)
- tests/probe-verdicts/check.py:283 bash probe (run_probe)
- tests/probe-verdicts/fault-controls.py:559 sys.executable (run_check); :1316, :1373 bash wrapper (selftest_wrapper, selftest_escape)
- tests/report-audit/isolation-mutants.py:71 sys.executable (grid)
- tests/report-audit/repo-state-grid.py:603 sys.executable (run_case: runs the frozen or current auditor, not git)

Opaque argv, not proven non-git (4), hand-checked:

- tools/error-verdict-census.py:77 `child()` generic `Popen(argv)`; argv comes from callers (python instrument, or the git literals at G13–G16, which are recorded separately).
- tools/kama-llamacpp-live.py:1500 `server_real` (llama-server); the file has no git token.
- tests/llamacpp-live/controls.py:867 and :937 `cmd` gate/probe commands; the file has no git token.

Bare `"git"` string constants (2): `tools/citation-provenance.py:249` (`stderr_contains='git'`, an expectation string) and `tests/report-audit/repo-state-grid.py:384` (the `timeout 5 git` argv, already G54).
