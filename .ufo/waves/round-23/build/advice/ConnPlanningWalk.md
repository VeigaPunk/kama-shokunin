# ConnPlanningWalk — build dependency order and falsify-wave list

Seat: `CloseKama22.ConnPlanningWalk` (connector, leaf; no dispatch). Access date 2026-10-21.
Lane base `master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, git 2.56.0, Python 3.14.8.
No tool installed, no pacman transaction, no network fetch, no write outside `/tmp/kama-r23-plan/`
and this file. All fault fixtures ran in fresh `/tmp` repos with
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`; the only real repos touched were read-only
(`--fleet-repo /home/vgpnk/Projects/shokunin`, lane read).

This is a planning walk, not a verdict: measurements below are inputs to the L1's order and to the
falsify wave, not a gate pass.

---

## 1. Axes (godspeed)

| axis | meaning for this round | how it is moved |
|---|---|---|
| **A1 claim fidelity** (round axis 7, C1 CALIBRATION) | every declared repository-local channel ends in a typed refusal (exit 2) or the correct verdict; never a wrong exit-0/1 | frozen-vs-current grid per channel |
| **A2 no-harm** | selftest, historical ledger, witness, citation census and controls stay bit-identical | fixed constants re-measured (§2.3) |
| **A3 discrimination** | each fault case is *sensitive* (frozen arm actually crashes/executes/flips; a broken fixture must not pass) and each control can fail | per-case sensitivity assertion + mutants |
| **A4 measurement integrity** | arms, env, cwd, repo args and script digests pinned; no moving "current" path | digest-pinned grid runs; clean-tree recipe |
| **A5 scope honesty** (round axis 8, operability) | no D4/untrusted-repo overclaim; old-git and object-format costs named | Limits + floor sentence |

Contradictions are stated in §3.2, never averaged into a score.

---

## 2. Measured facts (E-items)

### 2.1 Identity and instrument

- **E1** Frozen auditor = `git show 4fe9339f:tools/report-landing-audit.py` → 847 lines,
  sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`.
  Cross-check: round-22 witness records `candidate_sha256 = 09ecd63b…b3f`
  (`.ufo/waves/round-22/report-source-fix/runs/80a6d07c/source-witness.stdout`), i.e. the frozen
  blob is exactly the script the r22 witness froze.
- **E2** Lane worktree `tools/report-landing-audit.py` is **dirty relative to base**:
  sha256 `b6064767b1ce6b8833f977bb9fdfb45702c70427a9a792961ed3cc2636d89bda`, 864 lines,
  `git diff --numstat` = `26 9`, `git status --porcelain` = `M tools/report-landing-audit.py` +
  `?? .ufo/waves/round-23/`. It already contains `GIT_ISOLATION`
  (worktree lines 78–86: `--no-replace-objects`, `--no-lazy-fetch`,
  `-c i18n.logOutputEncoding=UTF-8`, `-c log.follow=false`), bytes-mode strict decode
  (lines 97–117), and a narrowed `git_env` docstring (lines 88–96). It adds **no** selftest case
  (still 50/50, E3). Ownership/authorisation of this edit is not established by any file I read —
  treat it as the integration candidate, not as base.
- **E3** Selftest `cases=50 failed=0 exit=0` for **both** the frozen blob and the worktree script
  (`python3 <script> --selftest`). Baseline is real and the worktree edit is selftest-neutral.
- **E4** Frozen arm's argparse defaults are **script-relative**: `--lane-repo` default `str(here)`
  where `here = Path(__file__).resolve().parent.parent` (worktree lines 831–835). A frozen copy
  placed in `/tmp` therefore audits `/tmp` and exits 2
  (`could-not-evaluate: git rev-parse --verify master^{commit} in /tmp: rc=128`), unless the grid
  passes `--lane-repo`/`--fleet-repo` explicitly. My first frozen ledger run failed exactly this
  way. **This is a harness confound, not a fault result.**
- **E5** Option presence on git 2.56.0: `git --no-lazy-fetch --version`,
  `git --no-replace-objects --version` and the full combination with
  `-c i18n.logOutputEncoding=UTF-8 -c log.follow=false` all exit 0. The local man pages do not
  document `--no-lazy-fetch` (`zcat /usr/share/man/man1/git.1.gz | grep -i lazy` → empty), so the
  version floor and doc citation belong to `OldGitFloor` / `SrcGitEnv`; I only measured the binary.

### 2.2 Fault grid baseline (frozen arm and worktree arm)

L1 probe `.ufo/waves/round-23/probe/probe.sh` (read in full) and its recorded run
`probe-4fe9339f.{stdout,stderr,exit}`; rerun by me against the worktree script with
`AUDIT=<worktree>/tools/report-landing-audit.py bash .ufo/waves/round-23/probe/probe.sh`.

| case | fixture | frozen (recorded) | worktree script (my rerun) |
|---|---|---|---|
| control | clean report, lane commit at 2000 | exit0, `defects []`, required 1, cutoff 2000 | exit0, `[]`, required 1 |
| a `f1-logenc` | lane `i18n.logOutputEncoding=ISO-8859-1` + subject `note café` | **exit1**, `UnicodeDecodeError … byte 0xe9` traceback | exit0, `[]` |
| b `f2-report-bytes` | `\xff\xfe` committed into fleet report | **exit1**, `UnicodeDecodeError … byte 0xff` traceback | **exit2**, `output is not UTF-8` |
| c `f3-replace-omit` | `git replace` hides an omitted round commit | **exit0**, `[]` (false clean) | **exit1**, `landed-omitted 4312b0a58238` |
| d `f4-replace-fake` | `refs/replace/<fabricated 40-hex>` | **exit0**, `[]` (false clean) | **exit1**, `unresolved-full-hash` + `landed-unresolved` |
| e `f5-lazyfetch` | promisor + `core.sshCommand` marker, `ssh://example.invalid/x.git` | exit1, 2 defects, **MARKER CREATED** | exit1, 2 defects, **no marker** |
| f `f6-follow` | `log.follow` rename case | exit0, `[]`, required 1 | exit0 — **vacuous** |

**Probe defect (important for A3):** `f6` is broken as written. `probe.sh` runs
`git -C "$F" commit -q -m mv` after `GIT_CONFIG_GLOBAL=/dev/null`, with no author/committer env;
my rerun shows `Author identity unknown … fatal: unable to auto-detect email address` and
`nothing to commit, working tree clean` in probe stdout. The rename-into-place commit never formed,
so `f6`'s "exit0" proves nothing. `FollowFixture` must rebuild it (§2.2, E6) and
`MutProbeSensitivity` must classify f6 as currently unfalsifiable.

### 2.3 No-harm baselines (measured twice: frozen blob vs worktree script)

Command:
`python3 <script> --rounds 10-22 --fleet-repo /home/vgpnk/Projects/shokunin --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin --json`

| constant | frozen | worktree |
|---|---|---|
| exit | 0 | 0 |
| reports / rounds | 13 / 10–22 | identical |
| defects / corrected / uncorrected | 9 / 9 / 0 | identical |
| by_kind | `landed-omitted 8`, `unresolved-full-hash 1` | identical |
| required_commits / post_report | 54 / 5 | identical |
| errata_rows / unmatched / invalid | 9 / 0 / 0 | identical |

`--no-errata` variant: exit **1**, same 9 defects, `corrected 0`, `uncorrected 9`.
Round-22 artifacts: witness exit0, `failures: []`, candidate clean / old failed, selftest 6 passed
(`…/runs/80a6d07c/source-witness*`); citation census `required 17, found 17, verified 17,
missing 0` and its selftest 24 cases (`…/runs/6433390a/nh-citation*`). These are the constants the
fixed auditor must reproduce.

### 2.4 Channels the probe did not cover — measured now

- **E6 `log.follow` is a real verdict flip** (raw git + end-to-end). Fixture: fleet creates
  `old/k.md` at author time 1500, renames it out of place, renames it to
  `.ufo/reports/round-1/kama.md` at 2500; lane `round-1: mid` at 2000; report cites nothing.
  - `git log --diff-filter=A --format='%at %s' -- <report>` → `2500 rename into place`.
  - `git -c log.follow=true log …` → `1500 create elsewhere`.
  - Frozen with repo-local `log.follow=true`: **exit0, cutoff 1500, required 0** (false clean).
  - Worktree script: **exit1, cutoff 2500, `landed-omitted babe44bb…`**.
  - Frozen with `log.follow=false` (control): exit1, cutoff 2500.
  Correct cutoff is the path-add at 2500: the docstring says "the fleet commit that first added
  the report" (worktree lines 24–31); `--follow` answers *content provenance*, a different
  question. `-c log.follow=false` restores the documented default, so the fix is semantic, not
  merely deterministic.
- **E7 `log.showSignature` + repo-local `gpg.program` EXECUTES a repo command** during
  `git log`, and the candidate tuple does **not** close it.
  Fixture: crafted commit object carrying a fake `gpgsig` header (`git hash-object -t commit -w`),
  repo-local `log.showSignature=true`, `gpg.program=<marker script>`.
  - `git log --format=…` with config true → **marker created** (`EXECUTED_DEFAULT`).
  - same with `-c log.showSignature=false` → **no marker** (`NO_EXEC`); output text identical.
  - End-to-end via the auditor: frozen **exit0, marker YES**; worktree script **exit0, marker NO**
    would require the override it lacks; I measured a `/tmp` candidate carrying the override:
    exit0, no marker, required 2, defects `[]`. Verdict is unchanged; only execution is.
  - Unsigned commits with `log.showSignature=true` → no exec, no output change (control).
- **E8 `.git/info/grafts` hides commits and `--no-replace-objects` does NOT disable grafts.**
  Fixture: lane c1(1000), c2(1050, omitted), c3(1100, cited); `.git/info/grafts` line `c3 c1`.
  - `git log` → only `c3, c1` (c2 hidden); with `--no-replace-objects` → still only `c3, c1`.
  - Frozen end-to-end: **exit0, required 2, `defects []`** (false clean).
  - `GIT_GRAFT_FILE=/dev/null git log` → all three commits.
  - `/tmp` candidate with `GIT_GRAFT_FILE=os.devnull` in `git_env`: **exit1, required 3,
    `landed-omitted c954b2d3`** — the correct verdict. No harm: its selftest stayed 50/50 and its
    historical summary stayed identical to E3/E-2.3.
  - `gitrepository-layout(5)` (`/usr/share/man/man5/gitrepository-layout.5.gz`, read 2026-10-21):
    "This file records fake commit ancestry information …" and "the grafts mechanism is outdated".
    `GIT_GRAFT_FILE` itself is **not** in the local man pages; portability/attribution must be
    checked by `GraftsFixture`/`SrcGitRepoLayout` before the report leans on it.
- **E9 old-git floor is a hard refusal.** PATH shim that exits 129 on `--no-lazy-fetch`:
  frozen **exit0**; worktree script **exit2**
  (`could-not-evaluate: git rev-parse --verify master^{commit} … rc=129 unknown option`).
  Fail-closed as designed, but it refuses *every* repo on git < 2.45, not only promisor repos.
  That is the operability (axis 8) cost that must be declared or narrowed (probe promisor config
  only on old git).
- **E10 `extensions.objectFormat=sha256` produces a false verdict in BOTH arms.**
  Fixture: sha256 lane/fleet, lane commit `2a735b7f…a9079`, report cites the 64-hex hash in
  `## Landed changes`. Frozen and worktree both **exit1** with `landed-omitted 2a735b7f…a9079`:
  `FULL` is 40-hex only and `ABBREV` caps at 40 (worktree lines 60–61), so a 64-hex citation is
  invisible; `cat-file --batch-check` on a 40-hex *prefix* of a sha256 commit resolves as `found`
  (measured), and a fabricated 40-hex returns `missing` (→ false `unresolved-full-hash`).
  This is repository-local state changing the verdict and is **not** converted to a refusal.
- **E11 channels tested negative (controls, not faults).** `core.fsmonitor` command →
  no exec during `log`/`cat-file`/`rev-parse`; `core.hooksPath` hook → no exec during `log`;
  `.mailmap` with `log.mailmap=true` changes `%aN` but **not** `%an` (measured:
  `kama-shokunin | Other | …`), and `round_commits` uses `%an` (worktree line 166), so mailmap is
  not a channel; unsigned `log.showSignature` no-ops.
- **E12 7-hex ambiguity is not constructible cheaply.** The selftest manufactures ambiguity from
  **4-hex** prefixes over 1500 blobs (worktree lines 722–741), but the report-level `ABBREV`
  minimum is 7 (line 61). A real `landed-ambiguous` end-to-end control would need a 7-hex
  collision (~16⁷ objects). `RevControls`' requested "real ambiguous abbrev" control cannot be
  built; keep the lookup-level unit test and record the limit, or drop the control explicitly.
- **E13 measurement gate.** `.ufo/waves/round-22/run.py:22-25` refuses to run when
  `git status --porcelain` is non-empty, and pins `refs/heads/master`. The lane is currently
  dirty (E2) and `.ufo/waves/round-23/` is untracked, while r22 committed 461 wave files
  (`git ls-files .ufo/waves/round-22 | wc -l`). Therefore **recipe measurement cannot run until
  L1 commits the fix and the wave artifacts** (or the runner is changed). This is an ordering
  constraint, not a style preference.
- **E14 output failure is already typed**: `--json >/dev/full` → exit2,
  `could-not-evaluate: output: [Errno 28]`. Broken pipe to `head -c 20` was inconclusive
  (python side exited 0 because the pipe buffer swallowed the output); do not claim it either way.

---

## 3. Dependency order

### 3.1 Stages, owners, gates

Nominal order from the ticket: *fix parts → grid → selftest → mutants → recipe → measurement.*
The actual dependency edges invert the first two: the grid is the **measuring instrument** and must
exist, frozen-only, before any fix is scored. "Fix parts" can be drafted in parallel, but cannot be
*accepted* before the instrument is sensitive.

| # | stage | artifacts | depends on | gate (must be measured, not asserted) |
|---|---|---|---|---|
| **D0** | Pin identity | frozen blob at `09ecd63b…`; worktree digest `b6064767…`; git/python versions; L1 ruling on the uncommitted edit | — | every later artifact records the script sha256 it ran; frozen copy is byte-identical to `git show 4fe9339f:…` |
| **D1** | Case table + fixtures (grid skeleton) | `tests/report-audit/repo-state-grid.py` with `--arm frozen|current|both`, explicit `--lane-repo/--fleet-repo`, case table incl. E6/E7/E8 | D0 | **G0 replication**: frozen arm reproduces rows a–e of §2.2 exactly (exit, defect set, traceback, marker) and clean control = exit0/`[]`; a deliberately broken fixture must fail the grid |
| **D2a** | Channel experiments (parallel, read-only) | FollowFixture, GraftsFixture, scouts (ShowSignature, ObjectFormat, SafeDirectory, Alternate, Notes, IncludeIf, FsmonitorHooks, Mailmap), OldGitFloor, Sentinel* | D0 | each returns measured yes/no with the exact invocation; no production edits |
| **D2b** | Fix parts (parallel drafts) | DecodeFix / ReplaceFix / LazyFetchFix patches **plus** any admitted channel from D2a | D1 case table (for expected outcomes) | patches are textually compatible with the one `git()`/`git_env()` shape; no per-call-site edits (SimplifyWrapper) |
| **D3** | Consolidated isolation change | one `GIT_ISOLATION` tuple + one env update + docstring correction | D2a, D2b | single integration owner; the current worktree content is the candidate unless L1 rules otherwise |
| **D4** | Grid current arm | grid run `--arm both --current <pinned copy>` | D3, D1 | **G1 movement**: each fault that was crash/false-clean/exec before is typed refusal or correct verdict after; **G2 control identity**: every control identical between arms; **G3 sensitivity**: each fault row's frozen outcome equals §2.2 (not merely "not clean") |
| **D5** | Selftest extension | new cases in `selftest()` for each closed channel | D3 | 50 existing case names unchanged and passing; new cases fail on a mutant that removes the channel; total = 50 + admitted channels (expected 56–58) |
| **D6** | Mutants | `out/GridMutants/mutants.py` | D4, D5 | mutants **generated from the tuple/env**, not hand-listed: remove each global flag, each `-c k=v`, each env entry, plus decode-`errors='replace'`, catch-`UnicodeDecodeError→clean`, surrogateescape; every mutant killed by grid or selftest, pristine passes |
| **D7** | Recipe (+ runner) | `recipe.json` in r22 `{lane}/{python}/{out}` shape; run.py | D4–D6, D0 | expected exits pinned: selftest 0; grid frozen ≠ 0; grid current 0; grid both ≠ 0; ledger 10-22 exit0; `--no-errata` exit1; witness 0; citation 0 |
| **D8** | Integration commit (L1) | committed lane master + committed wave artifacts | D7 | `git status --porcelain` empty (E13); recipe `{revision}` = new master |
| **D9** | Measurement | recipe receipts under `out/` | D8 | every recipe exit equals expectation; §2.3 constants identical on the committed tree; probe rows a–e as §2.2 worktree column; mutants all killed |
| **D10** | Report/lesson/scorecard | Scribe/Conn artifacts consumed by L1 | D9 | wording matches measured channels + Limits; no D4 overclaim |

**Parallel wings (5):** (i) grid + mutants + probe fixtures; (ii) fix parts/one wrapper; (iii)
channel scouts (read-only); (iv) no-harm/witness/citation/ledger; (v) report/lesson/scorecard
sources. Wings ii and iii are read-only vs the lane; i/iv write only `out/`; only D8 writes the lane.

### 3.2 Hard edges and contradictions (do not smooth)

1. **Three "fix parts", one function.** Decode/Replace/LazyFetch all rewrite `git()`/`git_env()`
   (worktree lines 78–117). They cannot be three independent patches applied in any order; the
   single-shape rule (SimplifyWrapper) wins. Cheapest path: adopt the existing worktree content as
   the integration candidate (it already passes E3/E2.3), then add only channels with a measured
   fault case.
2. **"Current" is a path, but must be a digest.** GridHarness' prompt names the lane worktree as
   current; E2 shows it is dirty and will keep changing. The grid must accept `--current PATH`,
   record its sha256, and the recipe must pass a committed copy; otherwise a concurrent edit can
   silently move the measurement.
3. **Frozen-arm default is script-relative (E4).** Without explicit repos the frozen arm exits 2
   on every case. A naive grid would read that as "typed refusal" and over-credit the fix. G0 must
   include `frozen clean control == exit0`.
4. **Probe f6 is vacuous (E-2.2).** It cannot be a control or a fault until FollowFixture rebuilds
   it; E6 supplies the valid shape (three commits, identity set, verified `--follow` difference).
5. **Grafts are not replace refs.** `--no-replace-objects` leaves `.git/info/grafts` active
   (E8). Either `GIT_GRAFT_FILE=/dev/null` (measured working, undocumented) or an explicit
   "grafts remain open" limit; the current worktree script silently leaves the channel open while
   its comment (line 78) implies the grid covers the channels that "changed or crashed" it.
6. **showSignature is an exec channel the tuple misses (E7).** It is the same class as lazy fetch:
   repo-local config selects a command (`gpg.program`) that git runs. One `-c` closes it
   (measured), so leaving it open is a choice, not a cost.
7. **sha256 objectFormat breaks the claim literally (E10).** Both arms mis-verdict. A one-call
   guard (`git rev-parse --show-object-format` ≠ `sha1` → EvalError) would make the claim true, at
   the cost of one subprocess and a new refusal class; otherwise it must appear in Limits as a
   known non-refusal. L1 decision; the falsify wave must include it either way.
8. **Old-git floor (E9).** Unconditional `--no-lazy-fetch` refuses all repos on git < 2.45.
   Declare the floor in the docstring/lesson and add a recipe item pinning `git --version`;
   alternatively refuse only when the repo is promisor — cheaper claim, more code.
9. **Ambiguous control is unbuildable (E12).** RevControls' list must drop it or downgrade it to a
   lookup-level unit case; claiming grid coverage of `landed-ambiguous` would be false.
10. **Measurement cannot start dirty (E13).** The wave artifacts are untracked; r22 committed
    them. L1 must commit fix + wave before D9, or the recipe runner must change (and then the
    "clean tree" guarantee in r22 receipts is lost).
11. **The `git_env` docstring overclaim is the actual defect.** The base text says audited repos
    "cannot be redirected" (base lines 88–91) while replace/lazy-fetch/encoding/follow all
    redirect it. Whatever wording survives must enumerate covered channels (replace, grafts-env,
    lazy fetch, log encoding, log.follow, showSignature) and name uncovered ones (objectFormat,
    shallow, alternates, commit-graph, resource DoS).

---

## 4. Falsify-wave item list — 85 distinct attack items

Surface codes: **G** grid case, **S** selftest case, **M** mutant, **R** recipe/no-harm rerun.
`M` in the "frozen" column = measured by me (§2); `P` = predicted from code/docs, must be measured
before use. Every row is an *attack*: it must be able to fail, otherwise it is not evidence.

### Decode / encoding (12)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F01 | G,S | lane `i18n.logOutputEncoding=ISO-8859-1` + `note café` | M: exit1 + `UnicodeDecodeError 0xe9` traceback | exit0 clean |
| F02 | G,S | invalid UTF-8 bytes committed in fleet report at HEAD | M: exit1 + traceback | exit2 `could-not-evaluate`, no traceback |
| F03 | S | invalid UTF-8 in committed errata blob | P: traceback or verdict | exit2 |
| F04 | G | invalid UTF-8 in committed `corpus/SOURCES.md` blob | P: traceback | exit2 |
| F05 | S | invalid UTF-8 in lane `%an` author name | P: decode crash | exit2 |
| F06 | G | commit with `encoding ISO-8859-1` header + non-ASCII subject | P: git re-encodes to UTF-8 | exit0 clean |
| F07 | G | `i18n.logOutputEncoding=SHIFT-JIS` on lane | P: re-encode error/exit2 | exit2 or clean, never traceback |
| F08 | G | `i18n.logOutputEncoding=<bogus>` | P: git fatal → EvalError | exit2 |
| F09 | S | invalid UTF-8 only in an older report commit, HEAD clean | P: control | identical verdict |
| F10 | S | report with CRLF headings/lines | P: control (universal newlines) | identical verdict |
| F11 | S | report with BOM and an embedded NUL | P: control (section still found; NUL harmless) | identical verdict |
| F12 | G | 8 MB single line in report | P: linear regex, slow | limit recorded, no hang |

### Replace / graft / shallow / alternates (12)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F13 | G | `git replace` hides omitted round commit | M: exit0 `[]` false clean | exit1 `landed-omitted` |
| F14 | G | `refs/replace/<fabricated 40-hex>` | M: exit0 `[]` false clean | exit1 2 defects |
| F15 | G | replace cited commit with unrelated commit | P: control (original exists) | same found verdict |
| F16 | G | replace chain X→Y→Z | P: chain honoured | `--no-replace-objects` breaks chain |
| F17 | G | replace ref pointing at a missing object | P: warning/odd type | typed result, no verdict flip |
| F18 | G | `.git/info/grafts` rewrites tip parent to hide omitted c2 | M: exit0 required2 false clean | exit1 required3 (`GIT_GRAFT_FILE=/dev/null`) |
| F19 | S | graft makes tip parentless (hides c1,c2) | P: frozen sees only tip | candidate sees all commits |
| F20 | G | `.git/shallow` marks a round commit boundary | P: log honours shallow; graft env does **not** disable it | explicit limit or refusal |
| F21 | G | `objects/info/alternates` store holds omitted commit object only | P: cat-file found, log silent | boundary wording (legitimate `clone --shared`) |
| F22 | G | alternates points at a nonexistent directory | P: control | identical verdict |
| F23 | G | replace SOURCES.md / committed report blob | P: classification could change | isolated by `--no-replace-objects` |
| F24 | S | inherited `GIT_NO_REPLACE_OBJECTS=1` with option removed (mutant) | P: env would mask mutant | mutant must be killed via option removal only |

### Lazy fetch / promisor (8)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F25 | G | promisor + `core.sshCommand` marker, `example.invalid` | M: exit1, **marker created** | exit1, no marker |
| F26 | G | `remote.origin.uploadpack=<marker>` + missing object | P: no fetch with `--no-lazy-fetch` | no marker |
| F27 | G | repo-local `credential.helper=<marker>` | P: no auth attempted | no marker |
| F28 | G | promisor, missing *commit* during `git log master` | P: fetch attempt / error | exit2, no marker |
| F29 | G | promisor, missing *tree* during `git log` | P: same | exit2, no marker |
| F30 | G | promisor URL `file:///tmp/...` (self-contained) | P: fetch would be local | no marker / exit2 |
| F31 | S | inherited `GIT_NO_LAZY_FETCH=1` | P: control (stripped) | identical |
| F32 | G,R | PATH shim rejects `--no-lazy-fetch` (simulated <2.45) | M: frozen exit0, candidate exit2 | exit2 fail-closed; floor documented |

### log.follow / cutoff (8)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F33 | G | rename chain into report path at 2500, lane commit 2000 | M: exit0 cutoff1500 required0 (false clean) | exit1 cutoff2500 |
| F34 | G | same fixture, repo config absent/false | M: control exit1 cutoff2500 | identical |
| F35 | S | `log.follow=true` in the **lane** | P: no path in `round_commits` | identical |
| F36 | G | rename out of place and back | P: follow jumps to first create | correct path-add cutoff |
| F37 | G | copy (not rename) into report path | P: follow does not follow copies | path-add cutoff |
| F38 | G | report deleted and re-added (`--diff-filter=A`, `out[-1]`) | P: oldest add wins | unchanged semantics |
| F39 | G | `log.follow=1` / `"true"` bool spellings | P: parsed as bool | override wins |
| F40 | G | rename commit author time == lane commit author time | P: `<= cutoff` boundary | required |

### log.showSignature / exec (5)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F41 | G | lane `log.showSignature=true` + fake `gpgsig` + `gpg.program` marker | M: exit0, **marker YES** | exit0, no marker (`-c log.showSignature=false`) |
| F42 | G | same config in the **fleet** repo | P: identical path | no marker |
| F43 | S | `log.showSignature=true`, unsigned commits | M: no exec, output unchanged | identical |
| F44 | S | `gpg.program` set, `showSignature=false` | M: no exec | identical |
| F45 | G | `log.showSignature` injected through `include.path` | P: `-c` precedence wins | no marker |

### Object format / ref storage (4)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F46 | G | sha256 lane+fleet, 64-hex citation in Landed | M: exit1 false `landed-omitted` | guard→exit2 **or** explicit limit (decision) |
| F47 | G | sha256, 40-hex prefix citation in Landed | M: cat-file `found` | found (no defect) |
| F48 | G | sha256, fabricated 40-hex in body | M: `missing` → defect | defect in both arms (not refusal) |
| F49 | G | `extensions.refStorage=reftable` | P: log/cat-file unchanged | identical verdict |

### round_commits matching (7)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F50 | S | author `kama-shokunin-extra` | M: ignored (selftest) | identical |
| F51 | S | `.mailmap` + `log.mailmap=true` maps lane author | M: `%an` unchanged, `%aN` changed | identical |
| F52 | S | subject `round-1:work` (no space) | M: required (selftest) | identical |
| F53 | S | subject `Round-1:` uppercase | P: not matched | identical |
| F54 | S | subject `checkpoint (r1)` with space | P: not matched | identical |
| F55 | G | author time far future | P: required forever | unchanged |
| F56 | G | round commit only on a non-`master` ref | P: not listed by `git log master`; cat-file found | explicit limit (branch scope) |

### Citation / token regex (9)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F57 | S | 40-hex inside registered source URL | M: exempt (selftest) | identical |
| F58 | S | 40-hex inside unregistered URL | M: defect (selftest) | identical |
| F59 | S | source URL inside `## Landed changes` | M: both checks kept (selftest) | identical |
| F60 | S | 39-hex / 41-hex bounds | M: not tokens (selftest) | identical |
| F61 | S | uppercase hex citation | P: not matched | identical |
| F62 | S | 7-hex all-hex word without digit | P: not checkable | identical |
| F63 | S | splice of two commit hashes (20+20) | M: `unresolved-full-hash` (selftest) | identical |
| F64 | S | zero-width space / line break inside a token | P: not matched | identical (document split-token limit) |
| F65 | S | 40-hex of a blob/tree in Landed | P: peel `^{commit}` → `landed-unresolved` | identical |

### Errata (6)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F66 | S | errata row matching no defect | M: failed (selftest) | identical |
| F67 | S | correction is not a lane/fleet commit | M: `errata-invalid` (selftest) | identical |
| F68 | S | malformed row (wrong columns) | M: exit2 (selftest) | identical |
| F69 | S | row present only in worktree, not committed blob | M: not authoritative (selftest) | identical |
| F70 | S | duplicate identical rows | P: both match, no double correction | identical |
| F71 | G | errata blob swapped via replace ref | P: classification changes | isolated by `--no-replace-objects` |

### Exit / IO (7)

| # | surface | fixture | frozen before | expected after |
|---|---|---|---|---|
| F72 | S | missing report | M: exit2 (selftest) | identical |
| F73 | S | report path is a directory / irregular file | M: exit2 (selftest) | identical |
| F74 | G | report path is a FIFO | P: `stat` not regular → exit2 | identical |
| F75 | G | report path is a symlink to `/dev/zero` | P: `stat` follows; read blocks | resource limit recorded |
| F76 | G | `--json >/dev/full` | M: exit2 `output: [Errno 28]` | identical |
| F77 | G | `--json | head -c 20` (broken pipe) | M inconclusive (python side 0) | measure decisively or drop |
| F78 | S | inherited `GIT_DIR` decoy untouched | M: selftest (decoy objects unchanged) | identical |

### No-harm / recipe (7)

| # | surface | fixture | before | expected after |
|---|---|---|---|---|
| F79 | R | `--selftest` | M: 50/50 exit0 | 50/50 + new cases, exit0 |
| F80 | R | ledger `--rounds 10-22` | M: exit0, 9/9, 54 required, 13 reports | identical |
| F81 | R | ledger `--no-errata` | M: exit1, 9 defects | identical |
| F82 | R | r22 witness | M: exit0, `failures []`, selftest 6/6 | unchanged |
| F83 | R | r22 citation census | M: 17/17, selftest 24 cases | unchanged |
| F84 | R | L1 probe rows a–e + control | M: §2.2 table | §2.2 collapse to typed refusals/correct verdicts |
| F85 | R | selftest executed from a hostile cwd/repo config | P: fixtures in tempdir, env scrubbed | identical (proves selftest is not self-referential) |

**Count: 85 distinct items** (12+12+8+8+5+4+7+9+6+7+7), above the 64 floor. Items marked `P` are
not evidence yet; the falsify wave must run them before citing them.

---

## 5. Non-obvious moves (one primary, two supporting)

**M1 (primary, synthesis of SimplifyWrapper + GridMutants + ScoutShowSignature + GraftsFixture):
make the isolation tuple the single source of both mutants and grid cases, and admit a channel only
with a measured frozen-arm fault.** Concretely: `GIT_ISOLATION` gains
`("-c","log.showSignature=false")` and `git_env` gains `GIT_GRAFT_FILE=os.devnull` (both measured
to change frozen behaviour: E7 marker, E8 false clean), and `GridMutants` derives one mutant per
tuple element/env entry instead of a hand-written list. Effects: A1 rises (two more channels
closed with existing evidence), A3 rises (mutant count == decision count, cannot go stale), A2 is
untouched (candidate selftest 50/50 and ledger summary identical — measured), A4 unchanged. Risk:
`GIT_GRAFT_FILE` is undocumented; mitigate by keeping F18 in the grid — if the variable stops being
honoured, the case flips to false-clean 0 and the grid fails, so the assumption is self-guarding.
`log.showSignature=false` is a documented `-c` key; its no-op on unsigned history is measured.

**M2 (supporting): invert the first dependency.** Build the grid frozen-only and prove G0 before
scoring any fix (contradicts the ticket's literal order, follows from the grid being the
instrument). Prevents the "fix looks good because the harness silently exits 2" failure (E4).

**M3 (supporting): treat the historical ledger as a digest-pinned equality, not a status check.**
Compare the full summary object (not just exit) between arms; the constants in §2.3 are exact and
the frozen/worktree equality is already demonstrated, so any drift becomes a diff rather than a
judgement.

---

## 6. What I did NOT verify

- A real git older than 2.45; only a PATH shim rejecting `--no-lazy-fetch` (E9). The version that
  introduced the option, and the local doc text, are `OldGitFloor`/`SrcGitEnv` work; the installed
  man page here does not mention it.
- Documentation/portability of `GIT_GRAFT_FILE` (works on 2.56, absent from local man pages).
- The 7-hex `landed-ambiguous` path end to end (E12: infeasible collision); selftest only proves
  `lookup()` with a 4-hex token.
- Any claim about hostile-repo safety beyond the grid; no network fetch was attempted, all promisor
  fixtures used `example.invalid`/`file://`/markers only.
- Whether the uncommitted lane edit (E2) is L1's intended integration; I only measured it.
- `commit-graph` tampering (stale/crafted generations could hide parents) — predicted channel, not
  tested.
- Real `core.fsmonitor` daemon behaviour; only a command-path config on a repo the auditor never
  runs `status`/`add` on.
- Broken-pipe exit (E14 inconclusive); `--json >/dev/full` exit2 is measured.
- Any git-scm.com URL content: I did not open the web sources this round, so I cite no quote from
  them. Local man-page quotes used: `gitrepository-layout(5)`
  (`/usr/share/man/man5/gitrepository-layout.5.gz`, read 2026-10-21) — "This file records fake
  commit ancestry information, to pretend the set of parents a commit has is different …"; and
  `git-replace(1)`, "… convert a `$GIT_DIR/info/grafts` file and use replace refs instead."

---

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/ConnPlanningWalk.md`
  (this report).
- Scratch only, under `/tmp/kama-r23-plan/`: `frozen.py`, `candidate.py` (worktree + the two
  proposed pins, used solely to test M1), `ledger-*.json`, `follow/`, `follow2/`, `graft2/`,
  `sig/`, `sig2/`, `sha/`, `shim/`, `mm/`, `fs/`, `ch/`, `gr/`, `px/`. No lane, fleet, sibling
  lane, config, index or tracked file was modified.

---

# ADDENDUM — the live candidate moved during this walk (append-only; supersedes named parts of §2–§5)

## A.1 Identity supersession

I measured the lane script at 12:12 (`b6064767…`, 864 lines, `26 9`), and it changed under me by
12:15. All conclusions below are pinned to the **live** digest:

- `tools/report-landing-audit.py` sha256
  `d0a96599ed0bf68103ac8bd107186ef1600c052d6646fc1a0f55db9b38517e22`, **919 lines**,
  `git diff --numstat` = `94 22`, status still `M tools/report-landing-audit.py` +
  `?? .ufo/waves/round-23/` (uncommitted).
- **This is the A4 hazard realized:** every "current path" citation in v1 §2.1/§3.2 is stale; the
  frozen digest `09ecd63b…` remains valid.
- Live anchors for the superseded v1 line citations: trust docstring **42–50**; `GIT_ISOLATION`
  **91–95**; `git_env` **98–105**; `git()` **107–126**; `lookup` ref guard **155–163**;
  `round_commits` **179–195** (surrogateescape at 181); `report_cutoff` **198–202**;
  `audit_round` **291–346**; `check_history_repo` **426–448**; `resolve_branch` **451–458**;
  `run` **462–503**; `selftest` **548–884**; ambiguity fixture **772–790**; `main` **887–917**.

## A.2 What the live candidate now does (read, not inferred)

- Tuple (91–95): `--no-replace-objects`, `--no-lazy-fetch`, `-c i18n.logOutputEncoding=UTF-8`,
  `-c log.follow=false`, `-c log.showRoot=true`, `-c log.showSignature=false`,
  `-c log.mailmap=false`, `-c core.quotePath=true`.
- `git(..., errors="strict")` default; **surrogateescape** only at the lane-log and round-listing
  call sites (181, 418). Report/errata/SOURCES bytes stay strict.
- `check_history_repo` (426–448) **refuses** (exit 2): non-sha1 object format, shallow repo,
  `info/grafts` present, `.promisor` pack, `extensions.partialClone`, any `remote.*.promisor`.
- `resolve_branch` (451–458) pins `refs/heads/<branch>` first (a same-named tag cannot shadow).
- `lookup` (155–163): a token that resolves to an oid not starting with the token (i.e. a **ref**
  named like the citation) is an EvalError.
- `GIT_GRAFT_FILE` from my `/tmp` M1 prototype is **not** in the live code; grafts are refused
  instead. Both satisfy "typed refusal or correct verdict"; the live choice loses the true defect
  list but needs no undocumented variable.

## A.3 Live measurements (frozen → live d0a96599)

| case | frozen | live | note |
|---|---|---|---|
| probe control | 0, `[]` | 0, `[]` | unchanged |
| f1 latin-1 logenc | **1 + traceback** | **0** | clean |
| f2 report bytes | **1 + traceback** | **2** | typed refusal |
| f3 replace omit | **0 false clean** | **1** | correct defect |
| f4 replace fake | **0 false clean** | **1** | correct 2 defects |
| f5 promisor+sshCommand | **1 + marker** | **2, no marker** | refusal replaces the 2-defect verdict; recipe expectation must change from 1 to 2 |
| f6 follow (probe) | 0 | 0 | still vacuous (fixture bug §2.2) |
| selftest | 50/50 | **50/50** | D5 not started |
| ledger 10–22 | exit0, 9/9, 54, 5, 13 | **identical summary** | no harm |
| log.follow chain | 0, cutoff1500, req0 | **1, cutoff2500, req1** | correct |
| showSignature + gpg | **marker YES**, exit0 | **marker no**, exit0 | closed |
| info/grafts | 0 false clean | **2 refusal**; twin (grafts removed) **1 correct** | refusal + differential twin |
| sha256 64-hex citation | 1 false `landed-omitted` | **2 refusal** | measured |
| shallow clone (`--depth 1`) | 0 false clean | **2 refusal** | legitimate shallow clones now unauditable |
| promisor config, all objects present | 0 | **2 refusal** | false refusal: no fetch was possible |
| branch named `deadbee1` cited | 0 false clean | **2** (`citation deadbee1 names a ref`) | new channel |
| tag `master` shadows branch | **1 false failed** (audits tag ghost) | **0 correct** | `resolve_branch` |
| lane subject `round-1: caf\xe9`, cited | **1 + traceback** | **0, required 2** | surrogateescape policy |

## A.4 Consequences for the order and gates

- **D3 exists but is uncommitted; D5 is not started** (selftest still 50/50, no new cases); **D1
  does not exist** (`tests/report-audit/` absent). The grid remains the first artifact.
- New gates on top of §3.1:
  - **G4 refusal-twin**: every `check_history_repo` refusal needs a matched twin that differs only
    in the refused property and exits with the *correct* verdict (measured examples: clean control
    0; graft twin 1). Without twins a refusal is indistinguishable from an unrelated startup error.
  - **G5 policy pin**: the strict-vs-surrogateescape decision must be one grid row that fails on
    the rejected policy. `DecodeFix`'s patch (strict everywhere; `LOG_UTF8` only on the two log
    calls) **conflicts** with the live worktree (strict default + surrogateescape at two call
    sites); the `round-1: caf\xe9` fixture distinguishes them (frozen 1 traceback; live 0; strict
    patch 2). L1 must pick one and the report must not claim both.
  - **G6 unfalsifiable pins**: `log.showRoot=true`, `log.mailmap=false`, `core.quotePath=true` have
    no reproduced fault (`%an` is mailmap-immune, both other keys default to the pinned value).
    Each needs a mutant that flips a case, or must be marked defensive-only and excluded from the
    coverage claim.
- Recipe updates: f5 expectation becomes **2**; add grid rows for ref-shadow, tag-shadow, shallow,
  promisor-config; add the twin controls; `--rounds 10-22` unchanged.

## A.5 Additional falsify items (F86–F95; total 95)

| # | surface | fixture | frozen | live/expected |
|---|---|---|---|---|
| F86 | G | lane branch named `deadbee1` cited in Landed | M: 0 false clean | M: 2 `names a ref` |
| F87 | G | tag `master` shadows branch with a ghost round commit | M: 1 false failed | M: 0 correct |
| F88 | G | shallow twin: same content non-shallow (`--depth` omitted) | P: 0 | P: 0 (correct) |
| F89 | G | promisor-config twin: config removed, objects already present | P: 0 | P: 0 (must not refuse) |
| F90 | G | graft twin: `info/grafts` removed | M: 1 defect | M: 1 (must not refuse) |
| F91 | G | sha1 twin of the sha256 fixture | P: 0/1 by content | P: same verdict, no refusal |
| F92 | G | non-UTF-8 lane subject with ASCII `round-1:` prefix, cited | M: 1 traceback | M: 0, required 2 |
| F93 | S | non-UTF-8 `%an` author | P: ignored (cannot equal lane name) | P: ignored, never traceback |
| F94 | M | remove `log.showRoot=true` / `core.quotePath=true` | P: no change | if no mutant kills, drop the pin or label defensive |
| F95 | M | remove `log.mailmap=false` | P: no change (`%an`) | if no mutant kills, drop or label defensive |

## A.6 Revised primary move

**M1′**: keep the live design's refusals, but make each refusal *evidence-shaped* — one differential
twin per refused class (G4) — and pin the decode policy as a single grid row (G5), with mutants
generated from the live 8-element tuple plus each `check_history_repo` check. This keeps A1 (every
frozen fault becomes refusal or correct verdict, both measured) and A2 (selftest 50/50 + ledger
identical), and repairs the two places where the live design currently cannot be falsified (A3:
refusals without twins; A5: three pins with no fault case). Cost: one extra fixture per refusal
class, and an explicit L1 decision on strict-vs-surrogateescape. The earlier `GIT_GRAFT_FILE`
prototype is superseded; it remains a cheaper alternative *if* L1 prefers verdicts over refusals
for grafts.

## A.7 Additional unverified

- Whether the live uncommitted edit is L1's intended integration; it changed twice during this walk
  and my v1 digests/lines are historical only.
- Minimum git versions for `rev-parse --show-object-format` and `--is-shallow-repository` (the
  old-git shim only exercised `--no-lazy-fetch`).
- `.promisor` pack-marker semantics in repos that are not actually partial.
- Whether `log.showRoot` / `core.quotePath` can change `--format` output at all (predicted no;
  F94 decides, not this report).

## A.8 Final state at close (12:19) — script moved again, grid landed

- Live lane script now sha256
  `79d9e124e8171b47dc69f5af657bcf938fcb77a4915f7758d50eccd6c72f226c`, **921 lines**,
  `git diff --numstat` `96 22`, still uncommitted. Re-measured on this digest: selftest **50/50**
  (D5 still open), ledger 10–22 **exit0 with the identical summary** (9/9, 54 required, 5
  post_report, 13 reports), probe **control0 / f1 0 / f2 2 / f3 1 / f4 1 / f5 2 (no marker) /
  f6 0**. So the A.3 table holds; only the digest moved.
- `tests/report-audit/repo-state-grid.py` now exists (24,581 bytes, untracked, 12:18). It is the
  D1 instrument and is stronger than §3.1 assumed: frozen/current/both arms, per-case premise
  `require(...)` checks (a fault that did not materialize → exit 2, never a pass), marker checks
  for lazy fetch and `showSignature`, traceback detection, `open`/`tradeoff` rows reported but not
  graded, and `auditor_sha256` recorded per arm. Case table lines 455–497 covers controls C01–C07
  and faults F01–F21 (encoding, report bytes, replace×3, lazy fetch, follow, showRoot, signature,
  shallow, grafts, tag shadow, ref-named abbreviation, mailmap FIFO, sha256, errata bytes/revision,
  bad-byte subjects, quotepath, nested subdir) plus O01/O02/T01.
- Three planning notes on the grid, not defects:
  1. Expectations are **fixed-arm** expectations; `--arm frozen` is expected to exit 1. For refusal
     rows (F10/F11/F13/F15) the frozen arm will not refuse, so the frozen run failing is the
     evidence, not an error.
  2. F12's expected `exit 1 / landed-omitted` must be re-derived against `resolve_branch`: my
     independent tag-shadow fixture produced **live 0** (correct) with a ghost tag at 1500, so the
     grid's fixture shape differs or the expectation is wrong. Same caution for F08/F14/F18/F19/
     F20 — each positive expectation needs a measured basis, not a guessed one.
  3. The grid has **no `--selftest` flag** (the GridHarness prompt asked for one); its premise
     checks plus exit 2 are the substitute. The recipe must therefore call `--arm current`
     (expect 0), `--arm frozen` (expect ≠0), `--arm both`, and treat exit 2 as harness failure —
     and must assert the recorded `auditor_sha256` equals the committed blob digest, because
     `--current` defaults to the moving worktree path (line 555).
- D2b/D3 are now embodied in the uncommitted script; D5 (new selftest cases), D6 mutants, D7
  recipe and D8 commit remain. §3.1 row order stands with D1 done, and the "three fix parts" edge
  is resolved in practice by one consolidated file.

## A.9 L1 rulings received at close (recorded, not re-litigated)

- **Decode policy decided**: split policy kept — `errors="strict"` default, surrogateescape only
  for lane log records and the fleet `ls-tree` round listing. `DecodeFix`'s strict-everywhere
  patch is **not** integrated. This closes A.4/G5; the grid pins it with F18 (unrelated bad-byte
  subject → 0) and F19 (bad-byte round subject → 1 `landed-omitted`). My independent fixture was
  consistent with both (bad-byte round subject, *cited* → live 0 required2; *uncited* would be the
  1 the grid expects).
- **Refusal rows pin their reason**: F06 expectation is exit 2 with stderr containing
  `partial clone`; every exit-2 row now pins a refusal-reason substring. That is the differential
  provenance G4 asked for, in stderr form; the twin-per-class idea reduces to "the pinned reason
  must name the property, not the harness".
- **Pins have red-before rows**: `showRoot`/`mailmap`/`quotePath` are covered by F08/F14/F20, and
  killing mutants run before measurement; any pin no mutant kills is labelled defensive-only.
  This closes A.4/G6 in the only honest way available.
- **Order unchanged**: measurement only after L1 commits, via `run.py` (clean-tree gate). My A.8
  note 2 (F12's expected exit 1 vs my measured live 0 on an independent tag-shadow fixture) is
  the one open check I would keep: settle it from the grid's own `--arm current` receipt, not from
  this report.

