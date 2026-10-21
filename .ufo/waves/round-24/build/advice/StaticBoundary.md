# StaticBoundary — round 24

**Verdict: PASS for the production Git wrapper’s inspected flag placement and per-call deadline; CONDITIONAL MEDIUM concern at executable resolution; do not execute the existing fault-grid probes under this static-only assignment.**

Axes reviewed: command integrity, local-only object/history semantics, signature/helper suppression, and timeout/cleanup. Static source review only: no Git, fixture, build, or test commands were run; runtime behavior is unverified in this seat.

## Findings

### MEDIUM — ambient `PATH` can replace the Git executable

**Exploit path:** An actor who controls the environment in which the auditor is launched can put a shim named `git` earlier in `PATH`. The call still supplies all intended safety flags, but the shim can ignore them, run arbitrary code as the auditor user, or emit fabricated output and forge the audit result.

**Evidence:** `tools/report-landing-audit.py:103-105` copies the caller environment except for `GIT_*` variables and sets global/system config isolation, leaving `PATH` intact. At `:117`, the subprocess argv starts with the bare executable name `git`; `shell=False` is implicit in `subprocess.run`, so shell metacharacters in later argv elements are not a shell-injection route, but executable lookup remains PATH-based.

**Impact:** The no-lazy-fetch/no-replace guarantees and result integrity depend on the selected binary actually being Git; current environment sanitization does not establish that.

**Smallest remediation:** Resolve the executable once from a trusted absolute path (or a trusted, validated absolute operator setting) and use that path as argv[0]. Keep the argument-vector invocation; do not replace it with a shell command.

### LOW — existing grid setup deliberately invokes configured programs and is not bounded throughout

**Exploit path:** Running `tests/report-audit/repo-state-grid.py` builds fixtures before its timed auditor subprocess. The shared `g()` helper at `:53-59` calls Git without `--no-lazy-fetch`, `--no-replace-objects`, signature suppression, or a timeout. The `f_lazy_fetch` builder at `:272-287` configures a promisor URL and `core.sshCommand`, then calls `git cat-file -e` on a missing object at `:283`; that is specifically a probe which causes Git to invoke the configured command. `f_filter_promisor` repeats this pattern at `:482-498`. `f_signature_program` creates an executable fixture program and calls `git log -1` at `:320-337` after configuring `gpg.program` and `log.showSignature=true`. These are execution-bearing tests, not safe static checks. `run_case` starts its 30-second timeout only after the builder returns (`:717-737`); that timeout cannot bound a stuck builder.

**Impact:** Executing these cases runs the fixture-configured program(s); an unexpectedly hanging builder is not covered by `run_case`’s timeout. This is a test-harness boundary, not evidence that the production wrapper drops its flags. No such commands were run here.

**Smallest remediation:** For this assignment, keep the review static and do not invoke the grid or these builders. For future authorized measurement, replace execution-based fetch/signature probes with a static argv-policy assertion and inert local fixture checks; bound fixture Git calls separately (and clean up a process group if a helper can be spawned). Do not run a mutant with the lazy-fetch flag removed against a promisor fixture.

## Production wrapper controls confirmed from source

- `tools/report-landing-audit.py:93-96` places `--no-replace-objects` and `--no-lazy-fetch` in the shared global-option tuple, alongside explicit overrides for log encoding, follow/root behavior, signature display, and mailmap. `:117` places that tuple before `-C <repo>` and before the subcommand; the production Git calls found in this file route through this wrapper. Keep this order. Do **not** put `--no-lazy-fetch` after a subcommand: prior recorded evidence says it is global-only.
- `:99-105` drops inherited `GIT_*` controls and disables global/system config. This is useful isolation but, as above, does not pin the `git` executable or erase repository-local configuration.
- `:107-108` defines a 20-second Git-call timeout and `:117-120` passes it to every wrapper invocation. This is a per-call ceiling, not a total audit deadline. `subprocess.run(timeout=...)` manages the direct child; process-tree cleanup is not explicit in this wrapper. If an allowed Git operation can spawn helpers, use a dedicated session/process-group timeout path so descendants are also terminated.

## Explicit safe alternatives

- Keep the production shape as `trusted-absolute-git --no-replace-objects --no-lazy-fetch -c log.showSignature=false -C <absolute-repo> <subcommand> ...`, with all global options before the subcommand and a Python argv list (no shell). The existing wrapper already has the correct flag ordering apart from executable pinning.
- Require Git **2.45 or newer** for `--no-lazy-fetch`; when the global option is rejected, return could-not-evaluate (exit 2). Do not fall back to `GIT_NO_LAZY_FETCH=1`: `.ufo/waves/round-23/build/out/OldGitFloor/findings:6-23,39-44` records that 2.24.1, 2.43.2, and 2.44.0 reject the CLI option, while the environment form is silently ignored on those older versions. The same evidence records that placing the option after the subcommand is rejected even on tested newer Git.
- Retain `--no-replace-objects` as a global option. The same OldGitFloor evidence at `:12,45-48` records the explicit flag works on all tested binaries; no reason to trade it for a weaker, implicit setting.
- Retain `-c log.showSignature=false` for every invocation that could inspect commits. Do not add `--show-signature` or run `git verify-commit` in this audit path; repository-local signature configuration must not cause `gpg.program` execution.
- Keep `timeout=GIT_TIMEOUT` on every production Git subprocess. If a subprocess could invoke a helper, the safe deadline alternative is a `Popen` in a new session with timeout handling that kills and waits for the whole process group, not just the Git PID.

## Files reviewed

- `tools/report-landing-audit.py:88-136, 189-218, 438-465, 489-520`
- `tests/report-audit/repo-state-grid.py:44-59, 272-287, 320-337, 482-498, 717-758`
- `.ufo/waves/round-23/build/out/OldGitFloor/findings:6-23, 36-53`
- `.ufo/waves/round-24/preregistration.json:8-12`

No production files, fixtures, or out artifacts were edited or created. Report path: `.ufo/waves/round-24/build/advice/StaticBoundary.md`.