# ScoutPriorRules — every audit-trust sentence, and what the round-23 fix does to it

Scout: `CloseKama22.ScoutPriorRules` (leaf; no dispatch). Read-only w.r.t. the lane:
I ran no write operations against the lane or fleet repos, no fault fixtures against
them, and no nested agents. No tools installed or upgraded.

Base: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (`git rev-parse HEAD` at
`/home/vgpnk/Projects/shokunin/kama-shokunin`, 2026-10-21). The lane worktree was
already dirty when I read it: ` M tools/report-landing-audit.py` plus untracked
`.ufo/waves/round-23/`. I treat that diff as the L1's in-progress round-23 fix and
attribute nothing in it to me.

Sources read (complete files unless a range is given):
- `corpus/QUALITY.md` (KQ28–KQ33, lines 148–171; earlier rows skimmed for supersession)
- `corpus/lessons/round-21.md` (full)
- `corpus/lessons/round-22.md` (full, 365 lines)
- `SKILL.md` (audit/fidelity/registry sections, lines 379–423, 664–774)
- `tools/report-landing-audit.py` at `4fe9339f` (base blob) and the current worktree
- `SCORECARD.md:996–1020,1104–1110,1146–1150`; `LOG.md:1280–1295,1338–1350`
  (adjacent authority docs that repeat the same trust claims)

Labels used below:
- **F** — becomes false after this round's fix (as the fix reads in the worktree).
- **O** — overbroad: true only for a narrower scope than the sentence implies.
- **Q** — needs qualification: still true, but incomplete (new exit classes, a host
  dependency, or a changed reason).
- **S** — survives and must remain / must not be loosened by this round.

## 1. What the in-progress fix actually covers

`git diff tools/report-landing-audit.py` at the time of reading adds exactly one
mechanism and one decoder change:

- `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", "-c",
  "i18n.logOutputEncoding=UTF-8", "-c", "log.follow=false")`, prepended to every
  `git` call (`tools/report-landing-audit.py:79–85,101` in the worktree).
- `git()` now captures bytes and decodes strict UTF-8, raising `EvalError` on
  `UnicodeDecodeError` (`:97–114`); one `git show` error message is reworded
  (`:283–286`).
- The module docstring, the exit map (`:42–45`), `main()` (`:830–860`, catches only
  `EvalError` and `OSError`) and `--selftest` are unchanged; no test case name in the
  worktree matches `utf|decode|replace|lazy|isolation|redirect|graft`.

So the fix covers four measured repository-local channels plus strict decoding of git
stdout. It does **not** add a top-level catch-all, and it does **not** isolate
repository-local state generally. Every sentence below has to be read against that.

## 2. Inventory — claim or restriction, by path:line

### `tools/report-landing-audit.py` (base blob `4fe9339f`; line numbers identical in
the worktree for the docstring)

| # | path:line | Claim / restriction (quote) | After fix | Required action |
|---|---|---|---|---|
| 1 | `tools/report-landing-audit.py:45` | "Errors are never verdicts." | **O** (was **F** before) | Keep as a headline but name the channels: git invocation, stdout decoding and input reads are now `EvalError`→2. Two counterexamples remain: an uncaught non-`EvalError` (no top-level catch beyond `EvalError`/`OSError`) still exits **1**, which is the `failed` verdict code; and a closed stdout exits **0** (observed today in both base and worktree, §3 R7). |
| 2 | `tools/report-landing-audit.py:42–44` | "2 could-not-evaluate (missing/irregular report, unusable git, malformed ledger, empty round selection, output failure)." | **F** for "output failure"; **Q** otherwise | "Output failure" is falsified by the closed-stdout exit 0 (R7). Add the new exit-2 inputs: non-UTF-8 git output, a git that rejects `--no-lazy-fetch` (before 2.45.0), and promisor-`missing` reports. |
| 3 | `tools/report-landing-audit.py:75–76` | "Could not evaluate: never converted into a verdict." | **Q** | True as an invariant on raised `EvalError`; it does not cover escapes that bypass `main()`'s two handlers or the closed-stdout path. Say "raised `EvalError` at the `main()` boundary" rather than an unbounded promise. |
| 4 | `tools/report-landing-audit.py:79–81` (base) | "No inherited GIT_* variables and no user/system config, so neither the audited repos nor the selftest fixtures can be redirected." | **F** before fix; the worktree replacement at `:88–91` is **O** | The base sentence was falsified by round-23 faults a–e (repository-local config/refs redirected the verdict). The replacement ("git() adds GIT_ISOLATION for the channels the fault grid covers") is directionally right but must name the four channels and the residues: `info/grafts` still rewrites `git log` under these flags (R2), a repo-local `log.showSignature` plus gpg program still executes it (R3), and alternates/other config keys are untouched. |
| 5 | `tools/report-landing-audit.py:17–24` | "URL classification is not source-validity proof" (and the exact-URL/committed-blob restriction) | **S** | Keep verbatim; this round must not be described as validating sources or repositories. |

### `SKILL.md`

| # | path:line | Claim / restriction (quote) | After fix | Required action |
|---|---|---|---|---|
| 6 | `SKILL.md:683` | Registry row: verdict map "2 could-not-evaluate (… unusable git …)"; selftest "inherited decoy `GIT_DIR`; splice, omissions, rebase/author-time cutoff, hex words, ledger matching/invalid corrections, exit-2 inputs"; pinned values "defect kinds and round-commit rule in the script" | **Q** | Verdict map needs the new exit-2 classes (#2). Selftest description needs the isolation/UTF-8 cases **only if they are actually added** — at read time the worktree has none, so the current text stays accurate but silent. Pinned values should name `GIT_ISOLATION` and the minimum git version. |
| 7 | `SKILL.md:687–689` | "Before committing a round report … it must exit 0" | **Q** | The exit-0 requirement now presupposes host git ≥ 2.45.0 (R5) and a full-clone lane/fleet pair. On older git the flag is rejected → `EvalError` → exit 2, so the checklist is unsatisfiable there; a promisor partial clone now yields `missing` records → defect (exit 1) instead of a lazy fetch. Name both premises. |
| 8 | `SKILL.md:698–703` | "The audit reads committed fleet report bytes (`git show HEAD:`), not working-tree files; `--rounds 10-` lists committed reports only." | **Q** | Still true; add that committed bytes are now decoded strictly, so a report with invalid UTF-8 is exit 2 (could-not-evaluate) — not a defect, not a traceback. |
| 9 | `SKILL.md:732–735` | "Its Git environment/system/global-config scrubbing is not repository-local config isolation, history-integrity proof or safe arbitrary-repository execution." | **O**, partly **F** | "Not repository-local config isolation" becomes overbroad: four named channels are now isolated. "History-integrity proof" and "safe arbitrary-repository execution" remain true restrictions and must stay. Rewrite as: four measured channels only; grafts/alternates/other keys/history provenance remain. |
| 10 | `SKILL.md:736–737` | "UTF-8/error/top-level handling and the late selftest fallback/GIT_DIR debt remain unclaimed until separately hardened." | **F** for the UTF-8 half; **Q** for the rest | UTF-8 decoding and the git-run error path are hardened for git stdout/input reads this round. Top-level handling is genuinely still absent (no catch-all in `main()`), and the selftest `GIT_DIR` fallback debt is untouched (selftest byte-identical, 50/50). Split the sentence: claim the UTF-8 half, keep the other two as unclaimed. |
| 11 | `SKILL.md:737–738` | "Never point it at an untrusted repository under the current guarantee (KQ32; round-22 lesson D4)." | **S** | Must remain, but its stated reason changes: not "UTF-8/errors unhandled", rather the residual channels (R2/R3/R4/R5) and alternates/shared clones. Loosening this to "now hardened" would be a false claim (the round context itself says this is not general untrusted-repository hardening). |
| 12 | `SKILL.md:762–763` | "It does not validate upstream bytes/claims, broaden the trusted-repository scope, or alter the Landed omission rules (KQ33)." | **S** | Keep verbatim. Channel hardening is not scope broadening; the restriction must survive this round. |
| 13 | `SKILL.md:769–771` | "The main report auditor retains its existing entry/exit contract … D4 local-Git-config/history and UTF-8 hardening remains frontier." | **F** for the last clause; **Q** for the first | The entry contract is unchanged, but the exit contract gains exit-2 classes (#2, #7). "UTF-8 … remains frontier" is false after this round; "history" remains true only for provenance/grafts/alternates. Replace with the exact split. |

### `corpus/QUALITY.md`

| # | path:line | Claim / restriction (quote) | After fix | Required action |
|---|---|---|---|---|
| 14 | `corpus/QUALITY.md:151` (KQ28) | "`python3 tools/report-landing-audit.py --rounds 10-<N-1> --report N=<draft>` exits 0 before the fleet commit and its summary is pasted." | **Q** | The criterion is unchanged in intent but now carries an environment premise: host git ≥ 2.45.0 (R5) and full-clone lane/fleet repos. KQ28 tells a future round to require exit 0; without the version premise that instruction can be impossible to satisfy on a legitimate host. |
| 15 | `corpus/QUALITY.md:165` (KQ32) | "explicitly limited to the trusted fleet/lane repositories until repository-local Git-config/history and UTF-8/error hardening is demonstrated separately" / reject "environment scrubbing is treated as suppressing local Git configuration" | **O**, partly **F** | The "until" condition is now demonstrated for a finite grid (four channels + UTF-8), so the row must be narrowed, not deleted: the limit remains for `info/grafts`, alternates/`clone --shared`, unmeasured config keys, history provenance, arbitrary repositories and hosts below git 2.45.0. The rejection cell must distinguish "environment scrubbing **alone**" (still the wrong inference) from "no local config is suppressed" (now false for the four channels). Append a new row that supersedes only this stated basis; do not edit the KQ32 cells (KQ7/KQ22/KQ31 append-only). |
| 16 | `corpus/QUALITY.md:171` (KQ33) | reject "classification is called source-validity or untrusted-repository proof" | **S** | Keep; explicitly record that this round does not make the audit untrusted-repository proof. |

### `corpus/lessons/round-21.md`

| # | path:line | Claim / restriction (quote) | After fix | Required action |
|---|---|---|---|---|
| 17 | `corpus/lessons/round-21.md:71–72` | "scrubbed git environment and config for every git call" | **O** (already overbroad at base; falsified by round-23 probes a–e) | Historical line; cannot be rewritten (KQ26/KQ7). Append an erratum naming it: "config" meant user/system config only; repository-local config/refs could still redirect the verdict; round 23 adds four measured channels and still leaves grafts/signature programs. |
| 18 | `corpus/lessons/round-21.md:102–108` (Limits) | "C1's population … Prose correctness, cross-round citations and unlabelled non-commit hashes are not judged." | **Q** / omission | The Limits paragraph has no repository-trust limit. Append the KQ32 limit plus the git-version premise; otherwise the Limits section reads as if the only limits are population and clocks. |
| 19 | `corpus/lessons/round-21.md:125–126,133` | "committed fleet report bytes are read (`git show HEAD:`) … closed stdout still exits 0." | **Q** (first), **observed-true** (second) | Add the strict-decode line (non-UTF-8 committed report → exit 2). The "closed stdout still exits 0" limit is reproduced today (§3 R7) and is direct evidence that the script's own "Errors are never verdicts"/"output failure → 2" sentences are not currently true; the erratum should cross-reference it. |

### `corpus/lessons/round-22.md`

| # | path:line | Claim / restriction (quote) | After fix | Required action |
|---|---|---|---|---|
| 20 | `corpus/lessons/round-22.md:117–118` | "Restricted guidance to trusted fleet/lane repos; KQ32 rejects extrapolation to untrusted repositories." | **S** | Dated and still true; keep. |
| 21 | `corpus/lessons/round-22.md:119` | "Environment scrubbing does not suppress repository-local configuration." | **F** as a present-tense statement about the current script | After this round the script suppresses four repository-local channels. Dated lesson text stays byte-intact; append an erratum naming round 23 and the four channels, and keep the residual list (grafts, alternates, other keys). |
| 22 | `corpus/lessons/round-22.md:121–123` | "Existing selftest fallback/GIT_DIR assertion debt, prelaunch races, chain bound, JSON duplicate-key/Unicode limits remain unclaimed." | **S** today | The worktree selftest is unchanged (same 50 cases, no isolation case), so the `GIT_DIR` assertion debt is still unclaimed. If the fix later adds selftest cases, this sentence must be re-scoped rather than silently reused. |
| 23 | `corpus/lessons/round-22.md:177–178` | "…4 routed records,1 trust restriction…" | **Q** (bookkeeping) | If round 23 files a new trust-restriction record (it should, per #15/#9), this inventory count and any SCORECARD cardinality must be recounted at the new measured commit (KQ27). |
| 24 | `corpus/lessons/round-22.md:336–337` | "Source URL classification is neither source truth/provenance validation nor D4 untrusted-repository hardening." | **S** | Keep. |
| 25 | `corpus/lessons/round-22.md:356–358` | "No upstream validity or untrusted-repository security guarantee is inferred from URL classification." | **S** | Keep. |

### Adjacent authority docs that repeat the same claim (outside the three mandated files, listed for completeness)

| # | path:line | Claim / restriction | After fix | Required action |
|---|---|---|---|---|
| 26 | `SCORECARD.md:1106–1108` | "trusted-repo audit hardening and richer diagnostics are not acquired here." | **O** (dated r22 statement) | Append (do not rewrite) that r23 acquires four measured channels; history/untrusted-repo hardening still not acquired. |
| 27 | `SCORECARD.md:1148–1150` | "The registered-URL classification is not upstream-source validation or D4 untrusted-repository hardening." | **S** | Keep. |
| 28 | `LOG.md:1289–1292` | "no claim to repository-local Git-config/history/UTF-8 hardening" | **O** (dated) | Append the exact split: four channels + UTF-8 stdout claimed; history/grafts/alternates/other keys not. |
| 29 | `LOG.md:1345` | "D4 untrusted-repo hardening remains unclaimed." | **S** in the general sense | Keep; qualify as "general", since four channels are now claimed. |

Excluded on purpose: `SKILL.md:396,404–409` (round-12 `fidelity.py` "a manifest cannot
redirect that anchor") is a different instrument with its own immutable-source pin;
this round's git hardening does not change it, and none of its claims should be
copied onto the report auditor. `corpus/QUALITY.md` KQ29/KQ30/KQ31 and
`corpus/lessons/round-22.md:88–89` ("No secret/config/environment values were
inspected") make no audit-trust claim; the latter is about inspected values, not
config scrubbing.

## 3. Observed probes that constrain the post-fix wording

All in fresh `/tmp` repos with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`;
nothing pointed at a network host. Scripts: `/tmp/scout-replace.sh`,
`/tmp/scout-graft.sh` (inline), `/tmp/scout-sigexec2.sh`, `/tmp/scout-flagorder.sh`,
`/tmp/scout-probe.sh`; no lane/fleet fixture runs.

- **R1 — replace refs (confirms the mechanism of probe d).** With a hand-written
  `.git/refs/replace/0123456789abcdef0123456789abcdef01234567` → a real commit,
  `git cat-file --batch-check` printed `0123…4567 commit 151`, rc 0; the same
  invocation with the exact worktree argv (`git --no-replace-objects --no-lazy-fetch
  -c i18n.logOutputEncoding=UTF-8 -c log.follow=false -C . cat-file --batch-check`)
  printed `0123…4567 missing`, rc 0. Note `git cat-file -e <fake>` returned rc 1 even
  without isolation — the fabrication resolves through `--batch-check`, not `-e`.
- **R2 — `info/grafts` survives the flags.** A graft hiding the middle commit removed
  it from `git log --reverse --format='%H %s'` identically with and without
  `--no-replace-objects` (git 2.56.0 also prints a deprecation hint on stderr).
  **This is a repository-local history channel the fix does not neutralize.**
- **R3 — a repo-configured program still executes.** With repo-local
  `log.showSignature=true`, `gpg.format=ssh`, `gpg.ssh.program=<wrapper>` and
  `gpg.ssh.allowedSignersFile` on a signed commit, `git log -1 --format='%H %s'`
  executed the wrapper **both** plain and with the exact `GIT_ISOLATION` argv
  (marker file: `EXECUTED` twice). Stdout gained an extra signature line before the
  format output, which the auditor's log parser would reject as
  `unexpected git log record` → `EvalError` → exit 2. So the *verdict* is a typed
  refusal, but **execution still happened**: no post-fix sentence may say or imply
  "no repository-configured command can execute".
- **R4 — `-c` precedence is real.** With repo-local `log.follow=true`,
  `git -c log.follow=false config --get log.follow` → `false`. With repo-local
  `i18n.logOutputEncoding=ISO-8859-1`, `git log -1 --format=%s` emitted `caf\351`;
  the forced `-c i18n.logOutputEncoding=UTF-8` emitted `caf\303\251`. Both flags
  therefore override the repository-local key for these calls.
- **R5 — host version premise.** `--no-lazy-fetch` first appears in the Git v2.45
  release notes (read 2026-10-21:
  https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.45.0.adoc,
  §Performance, Internal Implementation, Development Support:
  "`git --no-lazy-fetch cmd` allows to run "cmd" while disabling lazy fetching of
  objects from the promisor remote"). Installed git here is 2.56.0 and accepts the
  option. [INFERENCE] On git < 2.45.0 the option is rejected (rc ≠ 0) → `EvalError`
  → exit 2; I did not execute an old git.
- **R6 — current lane/fleet state is clean for these channels.** In both repos:
  no `refs/replace`, no `.git/info/grafts`, no `.git/objects/info/alternates`, and no
  local promisor/partial-clone/`log.*`/`i18n.*` keys (local key names only; values
  not inspected/recorded). The post-fix audit therefore keeps its current verdicts
  on these two repositories [INFERENCE from state, not re-run against the lane].
- **R7 — closed stdout still exits 0.** `python3 <base-blob> --selftest 1>&-` → 0;
  the in-progress worktree script → 0. Normal runs: `selftest cases=50 failed=0` for
  both. This reproduces round-21's known limit today and falsifies the docstring's
  "output failure → 2" clause.
- **R8 — no isolation selftest coverage in the worktree.** No case name matches
  `utf|decode|replace|lazy|isolation|redirect|graft`; 47 literal `check("…")` names.
  If the round keeps the selftest at 50 cases, the isolation flags have no
  fail-capable witness inside `--selftest`.

## 4. Recommended wording (for the L1 to integrate; I made no edits)

1. `git_env` docstring (replaces base `:80–81` and tightens worktree `:88–91`):
   "No inherited GIT_* variables and no user/system config. `git()` also passes
   `--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
   -c log.follow=false`, which neutralizes four measured repository-local channels
   on git ≥ 2.45.0. It is not repository-local config isolation: `info/grafts`
   still rewrites `git log`, a repo-local `log.showSignature` with a gpg program
   still executes it, and alternates/unmeasured keys are untouched."
2. Module docstring: keep "Errors are never verdicts" only as "Git invocation,
   stdout decoding and input-read errors exit 2; an uncaught non-`EvalError` still
   exits 1 and a closed stdout has been observed to exit 0."
3. Exit map: add non-UTF-8 output, "git without `--no-lazy-fetch` (before 2.45.0)"
   and promisor-`missing` as defect-vs-refusal cases; stop claiming output failure
   generally.
4. `SKILL.md:732–738`: keep the trusted-repo restriction and the "never point it at
   an untrusted repository" instruction; replace the unclaimed list with the
   four-channel claim plus the residual list (grafts, signature program, alternates,
   unmeasured keys, git version). Delete "UTF-8/error … remain unclaimed" and keep
   "top-level handling and the selftest fallback/GIT_DIR debt remain unclaimed".
5. `SKILL.md:687–689` and `QUALITY.md:151`: add the host premise "git ≥ 2.45.0,
   full-clone lane/fleet"; a host below it is exit 2, not a failed audit.
6. `QUALITY.md`: append a new criterion that supersedes KQ32's *stated basis* only
   (KQ7/KQ22/KQ31 shape), for example: the audit's hardening claim names the
   measured channels and git version; it is not called repository-local config
   isolation, history-integrity proof or untrusted-repository safety while
   `info/grafts`, a repo-configured signature program, alternates/shared clones and
   unmeasured config keys are demonstrated to change output or execute under the
   same flags, and while a closed stdout can still exit 0.
7. `round-21.md` / `round-22.md` / `SCORECARD.md` / `LOG.md`: append errata naming
   the superseded sentences (`round-21.md:71–72`, `round-22.md:119`,
   `SCORECARD.md:1106–1108`, `LOG.md:1289–1292`) with the four channels, the version
   premise and the residual list; do not rewrite the dated lines.

## 5. Not verified

- I did not run the round-23 fault grid (a–e) or the official measurement; I relied on
  the context's probe report for a–e and reproduced only R1–R4, R7, R8.
- I did not execute the audit against the lane/fleet repos (no fixture runs permitted
  there); "current verdicts unchanged" is inference from R6 state, not a run.
- I did not verify git < 2.45.0 behavior; the version introduction is read from the
  v2.45 release notes, and rejection on older git is inference.
- I did not test GPG-signed commits with `gpg.program` (only SSH-signed commits with
  `gpg.ssh.program`); whether a repo-local `gpg.program` also executes under
  `log.showSignature` is unverified, but the same code path makes it plausible.
- I did not audit `core.fsmonitor`, `core.hooksPath` or index-touching commands: the
  auditor invokes `show`, `rev-parse`, `ls-tree`, `log`, `cat-file` (plus `init/add/
  commit/rm/hash-object` only in `--selftest`), and only `log`/`show` were shown to
  reach a repo-configured program.
- I did not verify `core.quotePath` / `log.mailmap` / `core.abbrev` as channels; they
  are named as unmeasured, not as demonstrated.

## Files written

- `.ufo/waves/round-23/build/advice/ScoutPriorRules.md` (this file). No other lane or
  fleet file was created or modified.
