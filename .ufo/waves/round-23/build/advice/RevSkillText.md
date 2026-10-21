# RevSkillText — round 23 findings

Seat: CloseKama22.RevSkillText (leaf reviewer, no dispatch). Scope: draft text and
findings for SKILL.md, corpus/QUALITY.md, and the tool's own guarantee text for the
report-landing audit. No production edits, no commits, no index writes, no installs.

Anchors refer to these bytes:

- Lane HEAD `e0f0434` (`round-23: neutralize repository-local git state in
  report-landing-audit; fault grid and isolation mutants`). Its parent `4fe9339` is the frozen base.
- `tools/report-landing-audit.py` at e0f0434, blob sha256
  `684764108872cea153284dfec89848d5efdf5b30dd37db026434dea2b623e210` (equal to the working tree
  at probe time). Frozen blob at 4fe9339: sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`.
- `SKILL.md` and `corpus/QUALITY.md` were not changed by e0f0434 (`git diff --name-only 4fe9339 e0f0434`
  lists neither). Their blob sha256 values equal the 4fe9339 blobs.
- Git 2.56.0 is the only git available to this review.

The lane's working tree changed several times during the review. Earlier revisions
(sha256 `d0a96599…`, `79d9e124…`, `68476410…`) are superseded. All probe results below were
produced on the committed `684764…` bytes.

## 1. Findings, by severity

### F1 (High) — SKILL.md states round-22 limits as current

- `SKILL.md:683` (registry row "Report landing audit"). The verdict map lists the old
  exit-2 cases only. It omits partial-clone, non-top-level, non-sha1 detail, ref-named citation,
  and non-UTF-8 report or draft. Its self-test cell says nothing about where the round-23
  channel evidence lives. `--selftest` has 50 cases on both arms (see §3), and none of its
  `check("…")` names covers a repository channel (grep of `check(` names for
  replace, lazy, sign, graft, shallow, follow, showroot, include, alternat, textconv, utf,
  promisor, partial, mailmap, fsmonitor, filter, sha256, object-format: no match).
- `SKILL.md:732–738` says "UTF-8/error/top-level handling … remain unclaimed". The committed tool
  implements strict UTF-8 git output (`tools/report-landing-audit.py:124–127`) and the
  top-level refusal (`:437–438`), and pins the channels at `:94–97`. The sentence is now false.
- `SKILL.md:769–771` says "D4 … UTF-8 hardening remains frontier". Round 23 closes part of D4.
  Replacement drafts D1–D3 (§2).

### F2 (High for citation, not for exit) — two grid expectations contradict observed behaviour

Both rows are open or tradeoff, so the grid reports them and does not grade them. Do not cite
them as evidence until corrected.

- `tests/report-audit/repo-state-grid.py:535–536` (O01, alternates). The declared expectation is
  exit 1 with `landed-unresolved` and `unresolved-full-hash`. Running the builder `o_alternates`
  with the grid's own argv (`--json --rounds 1 --no-errata`) gives exit 0, status `clean`, no defects, on
  **both** arms (committed e0f0434 and frozen 4fe9339). The donor commit resolves through
  `objects/info/alternates`. The expectation matches a handled channel, not the open one.
- `tests/report-audit/repo-state-grid.py:538` (T01, blobless partial clone, tradeoff). The
  declared expectation is exit 0 with no kinds. Committed e0f0434 gives exit 2
  `could-not-evaluate: … partial clone (promisor pack)` (the declared new refusal). Frozen 4fe9339
  gives exit 0 clean. The expectation matches the frozen arm.

### F3 (Medium) — docstring version and reason claims need measurement or removal

- `tools/report-landing-audit.py:55` says "git >= 2.45 is required"; `:93` says "Old git (< 2.45)
  rejects --no-lazy-fetch". Only git 2.56.0 was available here. Nothing in this review measures an
  older git. Keep the version only if the grid measured it; otherwise state "measured on git 2.56.0".
- `:48–55` "`.mailmap` neutralized" is supported. A worktree `.mailmap` that is a FIFO makes plain
  `git log` block: the plain run timed out at 5 s, and the committed argv (`log.mailmap=false`)
  returned rc 0 (§3). The `%an` field is raw under both settings (§3), so mailmap does not rewrite
  the author name. The reason is the hang, not author rewriting.
- `:44–45` Exit list omits partial-clone, non-top-level, ref-named citation, and non-UTF-8
  `--report` draft or ledger. Replacement at D6.
- `:50–51` "a plain --branch name means refs/heads/<name>". The committed code falls back to
  revision resolution when `refs/heads/<name>` does not exist (`resolve_branch`, `:454–462`).
  That fallback is untested here. State "when refs/heads/<name> exists".

### F4 (Medium) — channels the text must not call closed

Observed on git 2.56.0, committed argv unless noted:

- `objects/info/alternates`: a borrowed object resolves (`lookup` → `found`; plain `cat-file -t` → `commit`;
  `check_history_repo` accepts). Open row O01.
- `.git` gitfile: followed; `lookup` → `found`; `check_history_repo` accepts. Open row O02.
- Author identity is the `%an` string. Signatures are not verified.
- Config-consumed knobs of commands the audit does not run, measured on git 2.56.0:
  - `git show HEAD:<blob>` (the audit's default call) does **not** run `diff.<driver>.textconv`;
    `git show --textconv` and `git cat-file --textconv` do (positive control: attribute resolves,
    `check-attr` → `report.md: diff: pwn`).
  - `core.fsmonitor`: not run by `log`, `show`, `ls-tree`, `rev-parse`, `cat-file --batch-check`, or
    `lookup`; run by `status` (positive control).
  - clean/smudge filter: not run by `show` or `cat-file`; run by `checkout` (positive control).
  - Not measured: `diff`, hooks, commit-graph forging, `core.alternateRefsCommand`, and unpinned
    `include.path` keys beyond those probed. The live lane and fleet have no commit-graph or
    multi-pack-index.
- Partial clones: refused with exit 2 by design (T01).
- Shallow, grafted, sha256, non-top-level: refused with exit 2 by design.

### F5 (Medium) — KQ32 must not be silently satisfied

`corpus/QUALITY.md:165` (KQ32) says the audit stays trusted-only "until repository-local
Git-config/history and UTF-8/error hardening is demonstrated separately". Round 23 demonstrates a
subset. Edit nothing in KQ32. Add KQ34 (D5) that refines KQ32 for the enumerated channels and keeps
its untrusted-repo prohibition. The QUALITY header (lines 3–5) says criteria are added as new rows.

### F6 (Info) — knowledge and sources

- No file under `corpus/knowledge/` names the audit or a landing check. Grep for `landing` and
  `KQ3[0-9]` returned no matches. Names appear only in `corpus/QUALITY.md:151` (KQ28, names the
  script, still true), `corpus/QUALITY.md:165` (KQ32), `corpus/lessons/round-21.md:10–66`
  (historical), and `corpus/SOURCES.md:119` (search-log note). No knowledge edit is needed.
- `corpus/SOURCES.md:44` (S032, git-show DESCRIPTION: "For plain blobs, it shows the plain
  contents") and `:45` (S033, git-cat-file `--textconv` opt-in) are the only opened rows that
  bear on the new text. The drafts cite them only for the textconv default.
- No opened rows exist for `log.showSignature`, `gpg.program`, `--no-replace-objects`,
  `--no-lazy-fetch`, `log.showRoot`, `log.follow`, `include.path`, `info/grafts`, `shallow`,
  gitfile, or alternates. Any doc citation for them needs a row first (KQ6, KQ31). Nothing here
  cites those docs.

### F7 (Info) — the live repositories show none of the refusal conditions

Read-only checks on the lane (`kama-shokunin`) and the fleet root: object format sha1;
`rev-parse --is-shallow-repository` false; no `.git/shallow`, `.git/info/grafts`, or
`objects/info/alternates`; no `*.promisor` pack (lane 10 pack files, fleet 11); no
`extensions.partialclone` or `remote.*.promisor`; no commit-graph or multi-pack-index; no local
config keys matching `include.|log.|gpg.|diff.|filter.|core.fsmonitor|core.sshcommand|core.hookspath|core.alternaterefs|i18n.|extensions.`.
I did not run the audit on either repository.

### F8 (Info) — the committed grid and mutant files are present

`tests/report-audit/repo-state-grid.py` (675 lines) and `isolation-mutants.py` (125 lines) are
committed in e0f0434, so the docstring path at `tools/report-landing-audit.py:48` resolves. I did
not run either. I cross-checked O01 and T01 only (F2).

## 2. Exact draft text (not applied)

All paths are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin/`. Line numbers are
e0f0434 for the tool and the grid, and base for SKILL.md and QUALITY.md (identical bytes).

### D1 — `SKILL.md:683`: replace the whole row

```
| Report landing audit | gate on fleet reports: `python3 tools/report-landing-audit.py [--rounds 10-] [--report N=DRAFT] [--errata PATH \| --no-errata] [--json]` | 0 clean (no uncorrected defect, no unmatched/invalid ledger row); 1 failed; 2 could-not-evaluate (missing, irregular or non-UTF-8 report, draft or ledger; non-UTF-8 git output; shallow, grafted, partial-clone, non-sha1 or non-top-level lane/fleet repository; ref-named citation; malformed ledger; empty round set; output failure). Undecodable committed report bytes are exit 2 (the frozen tool exited 1 with a traceback) | `--selftest`: 50 cases on the committed tool (unchanged in round 23): temporary lane+fleet repos under an inherited decoy `GIT_DIR`; splice, omissions, rebase/author-time cutoff, hex words, ledger matching/invalid corrections, exit-2 inputs. It has no repository-channel case; those are measured by `tests/report-audit/repo-state-grid.py` and `tests/report-audit/isolation-mutants.py` (§Round-23 below) | ledger `registry/report-landing-errata.tsv` read from the committed branch-tip blob; `GIT_ISOLATION` pins and `check_history_repo` refusals in the script; defect kinds and round-commit rule in the script | stdout only; reads lane and fleet git objects; no writes | kama |
```

### D2 — `SKILL.md:732–738`: replace the paragraph

```
**R21 outside-routing trust restriction (learned R22; narrowed R23).** The report-landing
audit is supported only on this trusted lane and fleet repository. Round 23 pins or refuses the
repository-local channels listed in §Round-23 report-landing isolation boundary. It is not a
history-integrity proof, not a safe execution boundary for arbitrary repositories, and it does
not authenticate author names or objects borrowed through `objects/info/alternates` or a `.git`
gitfile. Undecodable committed report, draft, ledger, or git output is could-not-evaluate
(exit 2). The late selftest GIT_DIR debt named in round 22 is not changed by round 23. Never point
it at an untrusted repository (KQ32, KQ34; round-22 lesson D4).
```

### D3 — `SKILL.md:769–771`: replace the paragraph

```
The main report auditor retains its existing entry/exit contract and `--selftest`; source URL
loading is from committed `--branch` bytes, never the worktree. Round 23 narrows the round-22 D4
frontier: the channels in §Round-23 report-landing isolation boundary are pinned or refused;
alternates, gitfile redirects, unlisted config-consumed knobs, and author identity remain frontier.
```

### D4 — `SKILL.md`: append after line 774 (blank line first)

```
## Round-23 report-landing isolation boundary (owner: kama)

Scope: `tools/report-landing-audit.py` at commit e0f0434, measured on git 2.56.0. A channel is
closed only where the frozen arm (4fe9339) misbehaves and the committed tool does not. Each
observation is a fixture under a temporary directory with `GIT_CONFIG_GLOBAL=/dev/null` and
`GIT_CONFIG_NOSYSTEM=1`. Grid rows: `tests/report-audit/repo-state-grid.py` (F01–F23, O01–O02, T01).

| Repository-local channel | Frozen 4fe9339 | Committed e0f0434 | Grid |
|---|---|---|---|
| `refs/replace/<40-hex>` | citation resolves (`found`) | `missing` (`--no-replace-objects`) | F03, F04 |
| promisor remote with `core.sshCommand` | the configured command runs on a lazy fetch | no fetch; partial clones refused (exit 2) | F06, F23 |
| `log.showSignature` with `gpg.program` | program runs; its output enters the records and corrupts tokens | program does not run (`log.showSignature=false`) | F09 |
| `log.follow=true` | rename moves the cutoff; false clean | cutoff from the path's first add; the defect is reported | F07 |
| `log.showRoot=false`, also via `include.path` | valid root-commit report: exit 2 | evaluated; the `-c` pin wins over the include | F08 |
| `info/grafts`, `shallow` | omitted round commit hidden; false clean | exit 2 (`rewrites history`, `shallow repository`) | F10, F11 |
| `i18n.logOutputEncoding` | UnicodeDecodeError traceback (CLI exit 1) | output forced to UTF-8; evaluated | F01 |
| undecodable committed report bytes | UnicodeDecodeError traceback (CLI exit 1) | exit 2 (`output is not UTF-8`) | F02, F16 |
| branch named like a tag | the tag's history is audited | `refs/heads/<name>` when it exists | F12 |
| citation equal to a ref name | `found` | exit 2 (`names a ref`) | F13 |
| worktree `.mailmap` that is a FIFO | plain `git log` blocks (5 s timeout) | not read (`log.mailmap=false`) | F14 |
| sha256 object format; nested subdirectory; partial-clone pack | no refusal in the frozen code | exit 2 | F15, F21, F23 |

Not closed. Do not describe these as isolated:

- `objects/info/alternates`: borrowed objects resolve as local (open row O01).
- `.git` gitfile redirection: followed as local (open row O02).
- Author identity is the `%an` string. Signatures are not verified.
- Config-consumed knobs of commands the audit does not run. Measured on git 2.56.0: `git show <blob>`
  does not run `diff.<driver>.textconv`, and `--textconv` does (`S032`, `S033` describe the
  default); `show`, `cat-file`, `log`, `ls-tree` and `rev-parse` do not run `core.fsmonitor`, and
  `status` does; `show` and `cat-file` do not run smudge filters, and `checkout` does. Not measured:
  `diff`, hooks, commit-graph forging, `core.alternateRefsCommand`, and unpinned `include.path`
  keys beyond those probed.
- Git versions other than 2.56.0 are not measured here. A minimum-version statement needs its own
  measurement.

Refusals are exit 2 by design. Shallow and grafted lanes and fleets, partial clones, sha256
repositories, and subdirectory arguments cannot be audited. The trust scope stays as in §R21
outside-routing trust restriction (KQ32, KQ34).

Reviewer observation, not a gate and not registry-owned: `.ufo/waves/round-23/build/out/RevSkillText/isolation-probe.py`
(output `isolation-probe.json`, sha256 `6cbef51f7266c143a515cfc98e40036be95ec69701e856851355fc2bf87db9d0`).
```

### D5 — `corpus/QUALITY.md`: append after line 171 (blank line first)

```
## Criterion added — round 23 (repository-local channel boundary)

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ34 | A report-landing audit claim about repository-local Git state names each channel it pins or refuses, the git version it was measured on, and the frozen-versus-committed observation that closes it. Every channel it does not pin is listed as unclaimed (object borrowing through alternates, gitfile redirects, author identity, and config-consumed knobs of commands it does not run). Refusals are typed could-not-evaluate and never a clean verdict. KQ34 refines the "until … demonstrated" condition of KQ32 for the enumerated channels only; KQ32 still forbids untrusted-repository use. | A blanket "repository-local config is isolated" or "safe for arbitrary repositories" claim; a selftest count offered as channel coverage; a channel called closed without a frozen arm that misbehaves; a minimum git version that was not measured; an alternates or gitfile object treated as proof of local history. | `lessons/round-23.md` (L1 files); `lessons/round-22.md` D4 (lines 116–121); `tests/report-audit/repo-state-grid.py` rows F01–F23, O01–O02, T01 |
```

### D6 — `tools/report-landing-audit.py`: replace docstring lines 42–46 (exit)

```
Exit: 0 clean (no uncorrected defect, no unmatched/invalid errata row);
1 failed (at least one); 2 could-not-evaluate (missing, irregular or
non-UTF-8 report or --report draft; unusable git or non-UTF-8 git output;
shallow, grafted, partial-clone, non-sha1 or non-top-level lane/fleet
repository; ref-named citation; malformed ledger; empty round selection;
output failure). Errors are never verdicts.
```

### D7 — `tools/report-landing-audit.py`: replace docstring lines 48–55 (trust)

```
Repository trust (round 23; rows F01-F23 in tests/report-audit/repo-state-grid.py):
refs/replace, lazy fetch, signature display, log re-encoding, log.follow,
log.showRoot and a worktree .mailmap FIFO are pinned per command; a plain
--branch name means refs/heads/<name> when that ref exists; shallow, grafted,
partial-clone, non-sha1 and non-top-level repositories and ref-named citations
are refused. Objects borrowed through objects/info/alternates and a .git
gitfile still resolve as local (open rows O01, O02). Other repository-local
channels are not claimed. Measured on git 2.56.0. Audit trusted repositories only.
```

### D8 — `tools/report-landing-audit.py`: replace comment lines 89–93 (GIT_ISOLATION rationale)

```
# Repository-local state observed to change, crash, block or hijack verdicts
# in the round-23 grid (git 2.56.0): refs/replace substitutions; promisor lazy
# fetch (runs core.sshCommand); signature display (runs gpg.program and writes
# its output into the records); re-encoded log output; log.follow and
# log.showRoot moving the report cutoff; a worktree .mailmap FIFO that blocks
# git log. --no-lazy-fetch needs a git that accepts it; an older git is an
# EvalError, not a fallback. The minimum git version is not measured here.
```

### D9 — `tests/report-audit/repo-state-grid.py`: expectation corrections for the L1 (not applied)

Replace line 535–536 (O01) with one line:

```
    ("O01-alternates-foreign-object", "open", o_alternates, 0, []),
```

Replace line 538 (T01) and add one `REASONS` entry (after line 553):

```
    ("T01-blobless-partial-clone", "tradeoff", t_blobless, 2, None),
```

```
    "T01-blobless-partial-clone": "partial clone",
```

No `corpus/knowledge/` edit is drafted: no entry needs one (F6). No SOURCES row is drafted
(§4 lists the rows a doc citation would need).

## 3. Evidence

Probe: `python3 -B .ufo/waves/round-23/build/out/RevSkillText/isolation-probe.py --candidate tools/report-landing-audit.py --lane-repo . --out .ufo/waves/round-23/build/out/RevSkillText/isolation-probe.json`.
rc 0 in 7.1 s. Candidate sha256 `684764…`, base sha256 `09ecd63…`, `git version 2.56.0`.
Each fixture ran under `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` in a temporary
directory, removed afterwards; `gpg.program`, `core.sshCommand`, `core.fsmonitor`, and the smudge
and textconv drivers are marker scripts; the only remote is `ssh://example.invalid/`.

Channel results (candidate uses its own `GIT_ISOLATION`; "plain" means git without flags):

| Probe | Result |
|---|---|
| `log.showSignature` + `gpg.program` | candidate: marker absent; plain: marker present, `[GNUPG:] BADSIG` text in stdout |
| `refs/replace/<fabricated>` | base `found`; candidate `missing`; plain `cat-file -t` → `commit` |
| promisor + `core.sshCommand` | candidate lookup `missing`, marker absent; plain `cat-file --batch-check` marker present, rc 0 |
| `info/grafts` / `shallow` | `log` honours both under candidate argv (2 of 3 commits visible); `check_history_repo` refuses both |
| `objects/info/alternates` | `lookup` `found`; plain `cat-file -t` `commit`; `check_history_repo` accepts |
| gitfile `.git` | `lookup` `found`; `check_history_repo` accepts |
| ref named `abcdef12` | base `found`; candidate EvalError `citation abcdef12 names a ref` (lookup level) |
| `.mailmap` FIFO | plain `git log` timed out at 5 s; candidate rc 0, not timed out |
| `%an` with `.mailmap` | `raw-name` under candidate argv and under `log.mailmap=true` |
| `git show HEAD:report.md` textconv | default: marker absent, output raw; `--textconv`: marker present, `CONVERTED` |
| `core.fsmonitor` | `log`, `show`, `ls-tree`, `rev-parse`, `cat-file`, `lookup` marker absent; `status` marker present |
| smudge filter | `show`, `cat-file` marker absent; `checkout` marker present |
| `i18n.logOutputEncoding=ISO-8859-1` | plain subject bytes `\xe9`; candidate `\xc3\xa9`; base `round_commits` UnicodeDecodeError; candidate evaluates |
| invalid UTF-8 commit subject | candidate counts the round commit (`surrogateescape`); strict `git log` EvalError; base UnicodeDecodeError |
| refusals | sha256 → `object format 'sha256', not sha1`; `extensions.partialclone` → `partial clone`; promisor pack → `partial clone (promisor pack)`; `-C <sub>` → `not a repository top level`; top level → accepted |

End-to-end (committed unless marked base; `status` is the audit exit; CLI rc from `--no-errata --rounds 10`):

| Scenario | Base 4fe9339 | Committed e0f0434 |
|---|---|---|
| S1 textconv driver on fleet report | status 1; marker absent | status 1; marker absent (same defects) |
| S2 lane `info/grafts` (omitted round commit) | status 0, CLI rc 0 `clean` (false) | EvalError `rewrites history`, CLI rc 2 |
| S2 lane `shallow` | status 0 (false) | EvalError `shallow repository` |
| S3 lane signed round commit, `gpg.program` | status 1, marker present, defect token `[GNUPG:] BADSIG fixture\n932a…` | status 1, marker absent, clean token `932a…` |
| S4 fleet root report, `log.showRoot=false` | EvalError `has no fleet commit`, CLI rc 2 | status 0, CLI rc 0 `clean` |
| S5 renamed report, no config | status 1 (`landed-omitted`) | status 1 (same) |
| S5 renamed report, `log.follow=true` | status 0, required 0 (false clean) | status 1 (`landed-omitted`) |
| S6 `include.path` sets `log.showRoot=false` | EvalError `has no fleet commit` | status 0 |
| S7 report with byte `0xff` | UnicodeDecodeError; CLI rc 1 with traceback | EvalError `output is not UTF-8`; CLI rc 2 |
| S8 tag named `master` | status 1, `landed-omitted` of the tag target (false) | status 0; `resolve_branch` → `refs/heads/master` |

Selftest: committed e0f0434 `selftest cases=50 failed=0`; frozen 4fe9339 `selftest cases=50 failed=0`.

Cross-check of grid rows (not a grid run): `tests/report-audit/repo-state-grid.py` builders
`o_alternates` and `t_blobless` run with the grid's own argv (`--json --rounds 1 --no-errata`, its
environment) against committed e0f0434 and against the frozen 4fe9339 blob:

- O01: candidate rc 0 `clean`, `defects: []`; frozen rc 0 `clean`, `defects: []`. Expectation: exit 1.
- T01: candidate rc 2, stderr `could-not-evaluate: … partial clone (promisor pack)`; frozen rc 0 `clean`. Expectation: exit 0.

Live repositories (read-only): see F7.

## 4. Not verified

- Older git. The `>= 2.45` statement and the availability of `--no-lazy-fetch` on other versions
  were not measured. Only git 2.56.0 was available.
- The grid (`repo-state-grid.py`, 23 fault rows) and `isolation-mutants.py` were not run by me.
  I cross-checked O01 and T01 only.
- Historical ledger rounds 10–22 under the committed tool. Not run.
- `resolve_branch` fallback when `refs/heads/<name>` is absent. Code reading only.
- The Landed-path ref-named token. The `bare` pre-lookup at `tools/report-landing-audit.py:131–164`
  raises the same guard; the CLI path was not run. Grid F13 expects exit 2.
- Commit-graph or multi-pack-index forging, hooks, `core.alternateRefsCommand`, `diff`, and unpinned
  `include.path` keys beyond those probed.
- Gitfile redirects through the CLI, beyond `lookup` and `check_history_repo`.
- Doc claims for the git options listed in F6. No SOURCES row was opened and none is drafted.
- KQ34 and `lessons/round-23.md` are for the L1 to file.

## 5. Files written and installs

Written:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/RevSkillText.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/RevSkillText/isolation-probe.py` (probe script)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/RevSkillText/isolation-probe.json` (probe output)

Scratch outside the lane (removed after the run): `/tmp/rst-probe/` (lane snapshots, base blob,
run fixtures), and `/tmp/o01-*`, `/tmp/t01-*` (grid cross-check fixtures). The probe script removes
its own temporary directory on exit.

Lane reads used `git --no-optional-locks` or `git show` only. No commit, index write, or tracked-file
edit. Installs: none.
## 6. Corrections appended after writing

Earlier lines are kept; each item below names the line it corrects.

- Header, lane versions: `684764…` is the committed tool at e0f0434, not a superseded revision. The superseded working-tree revisions are `d0a96599…` and `79d9e124…`.
- F1, first bullet: "non-sha1 detail" should read "the sha1 object-format check". The old row also omits partial-clone, non-top-level, ref-named citation, and non-UTF-8 report or draft.
- F7: the counts are entries in `objects/pack` (lane 10, fleet 11), not pack files.
- §2 D4, i18n row: the CLI exit 1 is inferred from `main`, which catches only EvalError and OSError (`tools/report-landing-audit.py:912–920`). It was not run for this scenario. The UnicodeDecodeError was observed from `round_commits`.
- §2 D4, ref-name row: "found" is the lookup-level result. The CLI-level frozen result was not run.
- §3 S3: "clean token `932a…`" should read "correct token `932a…`".
- §4 adds: the undecodable draft path (`read_report`, `tools/report-landing-audit.py:204–210`) and ledger path (`load_errata`, `:365–375`) are code reading only. Frozen-arm `core.fsmonitor` and smudge results are inferred from the same subcommands, since the pins do not touch them. They were not run on the frozen argv.
- D2 debt sentence: no `GIT_DIR` or `decoy` line appears in `git diff 4fe9339 e0f0434 -- tools/report-landing-audit.py`, so the round-22 selftest debt lines are unchanged.
- §5: the scratch directories listed there are removed after this section is appended.
- Post-review state: after the review, the working tree differed from HEAD e0f0434 again: `M tools/report-landing-audit.py` (42 changed lines, sha256 `f228f174…`), `M tests/report-audit/repo-state-grid.py` (41 lines), `M tests/report-audit/isolation-mutants.py` (4 lines). A keyword grep of the tool diff (GIT_ISOLATION, log., replace, lazy, shallow, grafts, partialclone, show-prefix, show-object) found no changed line in those areas. This review did not probe the uncommitted revision. Every anchor and probe result here refers to HEAD e0f0434 (tool sha256 `684764…`).
