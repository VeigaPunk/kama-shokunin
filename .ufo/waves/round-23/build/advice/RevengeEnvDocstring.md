# RevengeEnvDocstring: intent of the `git_env()` docstring in `tools/report-landing-audit.py`

VERDICT: overclaim; correct it. The clause "neither the audited repos nor the selftest fixtures can be redirected" was meant as "inherited environment and user/system git config cannot steer the audit or its selftest." That holds for the environment and config channels. It is false for the audited repos' own repository-local state (config, refs, grafts, shallow boundary, signature programs), which the audit reads as evidence. The selftest-fixture half holds for every channel I tested.

Scope: lane `kama-shokunin`, HEAD `4fe9339f` (committed tool blob `fcc255ce`). `HEAD:` cites the committed file. The working tree is uncommitted (` M tools/report-landing-audit.py`) and was changing during this run; `WT:` cites it at sha256 `d0a96599…` (§5).

## 1. Introducing commit

- `1471344` (2026-10-21, "round-21: integrate build-wave findings into report audit and install-links pin…") is an ancestor of HEAD (`git merge-base --is-ancestor 1471344 HEAD`: yes). It introduces `git_env()` at `tools/report-landing-audit.py:72-74`:
  `"""No inherited GIT_* variables and no user/system config, so neither` / `the audited repos nor the selftest fixtures can be redirected."""`
- Parent `a29bb84` (the draft) had no env handling: `git()` ran `subprocess.run(["git","-C",…])` with inherited `os.environ` (`git log -L '/^def git_env/,+9:…'` shows the function first appears in `1471344`).
- HEAD carries the same text unchanged at `HEAD:79-81` (`git log -L` lists no later commit touching those lines).
- `git log --all -S "def git_env"` also returns `7947e46`, `4773402`, `d9643ac`. These share parent `a29bb84`, carry the same wording at line 74, are not ancestors of HEAD, and survive only as `refs/jj/keep/*`. They are abandoned siblings, not the landed introduction.
- `git log -S "neither the audited repos"` finds nothing because the docstring wraps after "neither". The phrase is "the audited repos nor the selftest fixtures can be redirected."

## 2. Motivating round lesson and evidence

- Lesson: `corpus/lessons/round-21.md:71-74`: "Adopted into the audit after the draft `a29bb84`: scrubbed git environment and config for every git call … (AuditGitEnvExec, AuditGitEnvSentinel, AuditExitContract)."
- `.ufo/waves/round-21/build/advice/AuditGitEnvExec.md:1` (verdict "refute"): the draft's selftest "is not env-isolated: GIT_DIR rewrites the decoy and fails, hostile global git config crashes it." `:18` root cause: "no `GIT_*` scrub and no config isolation." `:36` threat model: "callers that export `GIT_*` into the audit, such as git hooks or CI [INFERENCE]."
- `.ufo/waves/round-21/build/advice/AuditGitEnvSentinel.md:1` (verdict "confirm"): "inherited GIT_DIR, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY or GIT_COMMON_DIR redirect selftest writes into the named repo; inherited git config runs hooks or breaks the selftest." `:20` F2: "the audit itself is redirected by GIT_DIR (A1)." Its minimal fix (`:27-28`) is the env scrub plus `GIT_CONFIG_GLOBAL=os.devnull` and `GIT_CONFIG_NOSYSTEM=1` that landed.
- Intent, reconstructed: the two protected things are the repos the tool reads (audited) and the temp repos it writes (fixtures). "Redirected" means steered by an inherited channel.
- Selftest coverage: `HEAD:804` `inherited-GIT_DIR-untouched` is the only env case. No `check("…")` name in HEAD (grep, lines 548–804) exercises refs, repo config, grafts, shallow, promisor remotes or signature programs.

## 3. Did "redirected" mean GIT_DIR only? No.

- Environment channels round 21 tested (`AuditGitEnvSentinel.md:7-12`, `:22`): GIT_DIR (E1, E1b, A1), GIT_INDEX_FILE (E2), GIT_OBJECT_DIRECTORY and GIT_COMMON_DIR (E3, E3b), GIT_WORK_TREE (E4), `GIT_CONFIG_COUNT` / `git -c` / `GIT_CONFIG_PARAMETERS` (E5–E8), GIT_TEMPLATE_DIR, GIT_DEFAULT_HASH (E9).
- User/system config (`AuditGitEnvSentinel.md:15`): core.hooksPath, commit.gpgsign, init.templatedir, include.path, core.fsmonitor, user.signingkey.
- The scrub (`HEAD:82-83`) drops every `GIT_*` and sets `GIT_CONFIG_GLOBAL` / `GIT_CONFIG_NOSYSTEM`. That covers the whole class. GIT_DIR was the headline example, not the boundary.
- Never covered: the audited repos' own files. Round 21 recorded one repo-local effect and did not fix it: F6, "ref shadowing. A branch named `deadbee1` hides `landed-unresolved deadbee1`" (`AuditGitEnvSentinel.md:24`). It still reproduces at HEAD (§4, row 3).
- PATH: `git` is resolved through PATH (`HEAD:89`). PATH is not a `GIT_*` variable, so the claim does not reach it. [INFERENCE: outside the stated caller-environment model; untested.]

## 4. Overclaim test (committed tool at HEAD, fixtures, git 2.56.0)

Recipe: throwaway repos under `/tmp`, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. Lane: three commits `round-1: alpha/beta/gamma` by `kama-shokunin`, built with `git commit-tree` and fixed dates. Fleet: one commit with no report. Each run: `python3 <tool> --lane-repo L --fleet-repo F --rounds 1 --report 1=DRAFT --no-errata`. Drafts cite 12-char prefixes under `## Landed changes`.

| Repo-local state of the audited lane | HEAD result (committed tool) | Control (no repo state) | Reading |
|---|---|---|---|
| `.git/shallow` at beta; draft cites beta, gamma | exit 0 `status=clean` (required=2) | exit 1, `landed-omitted` alpha | false clean |
| `.git/info/grafts` gamma→alpha; draft cites alpha, gamma | exit 0 `status=clean` (required=2) | exit 1, `landed-omitted` beta | false clean |
| branch `deadbee1` exists; draft cites fabricated `deadbee1` | exit 0 `status=clean` | exit 1, `landed-unresolved deadbee1` | false clean |
| signed-looking tip + repo `gpg.program` + `log.showSignature=true` | exit 0 `status=clean`; the configured program **ran** | exit 0, program not run | silent execution |
| `.mailmap` remapping the author email | unchanged | — | not a channel: the tool uses `%an`; `%aN` does change |

Git-level checks: with the GIT_ISOLATION tuple as I first read it (`--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false`), `log --format=%H` still lists `[gamma, beta]` under shallow and `[gamma, alpha]` under grafts. `--no-show-signature` and `-c log.showSignature=false` each stop the gpg run with identical stdout. `cat-file --batch-check` gives `deadbee1^{commit}` found and `deadbee2^{commit}` missing.

Not re-run, per the rule on user-reported observations: L1's probes (a) encoding traceback, (b) invalid UTF-8 traceback, (c) and (d) `refs/replace` false clean, (e) promisor fetch executing `core.sshCommand`. I take them as given.

Verdict on the two clauses:
- "the audited repos … cannot be redirected": false at HEAD. Repo-local state flips verdicts (rows 1–3) and runs a repo-chosen program (row 4).
- "the selftest fixtures … cannot be redirected": not refuted. The tool builds the fixtures, and every env-bearing git call goes through `git_env` (`HEAD:89-91`, `457-466`, `527-539`). The only `os.environ` mutation is the GIT_DIR decoy at `491-492`, restored at `801-803`.

The lane already states the limit, and HEAD contradicts it:
- `corpus/QUALITY.md:165` KQ32: the audit is "explicitly limited to the trusted fleet/lane repositories until repository-local Git-config/history … hardening is demonstrated"; treating "environment scrubbing" as suppressing local config or as a guarantee for arbitrary repos is a failure.
- `corpus/lessons/round-22.md:116-119` D4: "Environment scrubbing does not suppress repository-local configuration." Round 22 wrote this down and the docstring was not updated.

## 5. Working tree (uncommitted; not written by me)

- `git status` shows ` M tools/report-landing-audit.py`. The file changed during my reads: `4c606df9…` (first copy I ran) and `d0a96599…` (current).
- It already narrows the docstring. `WT:98-101`: "No inherited GIT_* variables and no user/system config. This alone does not isolate repository-local config or refs; git() adds GIT_ISOLATION for the channels the fault grid covers." Module paragraph `WT:48-51`: "…objects borrowed through objects/info/alternates still resolve as local, and other repository-local channels are not claimed. Audit trusted repositories only."
- Current copy (`d0a96599…`) on the same fixtures:
  - shallow: exit 2, `could-not-evaluate: …: shallow repository` (`WT:434-435`, `check_history_repo` at `WT:426`).
  - grafts: exit 2, `…/.git/info/grafts rewrites history` (`WT:436-439`).
  - gpg: exit 0, program not run (`GIT_ISOLATION` includes `-c log.showSignature=false`, `WT:91-95`).
  - branch shadow: exit 2, `citation deadbee1 names a ref` (`WT:161-162`). The earlier copy (`4c606df9…`) returned a false clean here.
  - Controls match HEAD.
- Still open: the PATH channel. Alternates (`objects/info/alternates`) are honored by design (`WT:49-50`; the contract calls alternates legitimate); not tested by me. `log.mailmap=false` is precautionary; no HEAD effect was observed.
- Process note: `corpus/lessons/round-21.md:66` (M4) records a build seat writing into the lane checkout. The uncommitted edit is the same class of write. I did not write it and do not know its author.

## 6. Recommendation (L1 decision; not applied)

Correct the docstring in the same commit as the round-23 change. Replace the clause with a scope statement, for example:

> No inherited GIT_* variables and no user/system git config, so the environment cannot steer the audited repos or the selftest fixtures. Repository-local state of an audited repo is evidence, not isolated: only the GIT_ISOLATION channels are neutralized; shallow, grafted, promisor and ref-named citations are refused (KQ32).

Also add fail-capable selftest cases for the four HEAD rows (shallow, grafts, gpg/showSignature, ref-named citation). HEAD's selftest has none, and the working-tree refusals are verified only by my fixture runs.

## 7. Confidence and what I did not verify

- High: the introducing commit, the lesson and advice chain, the threat model, and the HEAD overclaim (rows 1–4 executed on fixtures).
- Medium: working-tree behavior. One run per snapshot, and the file was still moving.
- Not verified: L1 probes (a)–(e) (not re-run, per rule); other git versions; real lane/fleet runs (none done); alternates; a PATH shim; `safe.directory`; `.mailmap` beyond `%an`; whether production reports would change.
- Not run: the lane selftest and any lane `--rounds` audit (out of scope for this assignment).

## 8. Files, hygiene, installs

- Written: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/RevengeEnvDocstring.md` (this file). Nothing else in the lane.
- Scratch: fixture roots under `/tmp/kama-r23-RevengeEnvDocstring-*`. Each harness removed its root (`scratch_removed: true`).
- Lane access: read-only git (`log`, `log -L`, `log -S`, `show`, `grep`, `for-each-ref`, `merge-base`, `rev-parse`, `diff`, `status`). No commits, jj, or config writes. My first `git status --porcelain` and `git diff` ran without `GIT_OPTIONAL_LOCKS=0`, so `.git/index` may have had a stat-cache refresh (no content staged). Observed `.git/index` mtime now: 2026-10-21 11:40:20 -0300.
- Installs or updates: none.
