# LazyFetchFix — rationale for lazy-fetch suppression in `tools/report-landing-audit.py`

Base: master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d (scratch clone /tmp/kama-r23/LazyFetchFix).
One tracked file changed: `tools/report-landing-audit.py` (+74/−4). No new CLI flag on the script.

## Decision: git's global `--no-lazy-fetch`, injected at the single chokepoint

The ticket offered "`--no-lazy-fetch` global option (git>=2.44) or GIT_NO_LAZY_FETCH=1". I verified
on host git 2.56.0 that both mechanisms work and chose the **global flag** because it is the only
one that fails closed:

- `git --no-lazy-fetch` is a top-level git option (git(1) OPTIONS, next to `--no-replace-objects`).
  `strings /usr/bin/git` shows it in the usage line `[-p | --paginate | -P | --no-pager]
  [--no-replace-objects] [--no-lazy-fetch]`; sibling survey `advice/SrcPartialClone.md` S090
  documents it from https://git-scm.com/docs/git (2.56.0, opened 2026-10-21). The ticket's
  "git>=2.44" is the introduction version; I did not pin by version — I detect by behavior (below).
- On an old git the unknown global option exits **129**, which the `git()` helper already converts
  to `EvalError` → `main()` exit 2. The env var `GIT_NO_LAZY_FETCH=1`, by contrast, is *silently
  ignored* by an old git — fail-open. So the flag is primary; I did not add the env var (it would
  only be defense-in-depth and would have to be stripped for the selftest's unsuppressed control).

Every git call in the script goes through the one `git()` helper (`subprocess.run` appears only at
line ~93, previously line 89). Inserting `"--no-lazy-fetch"` into its argv covers all object-
resolving call sites at once: `lookup` (cat-file --batch-check, the L1 probe vector), `log` (round
commits, report cutoff), `ls-tree` (round listing, SOURCES.md), `cat-file blob` (SOURCES.md),
`show` (committed report bytes, errata ledger), `rev-parse`. Selftest fixture commands (`init`,
`add`, `commit`, `config`, `remote`, `hash-object`) go through the same helper.

## Fail-closed on older git

`git()` now special-cases `rc==129` with `no-lazy-fetch` in stderr into an explicit message:
`could-not-evaluate: git --no-lazy-fetch unsupported (needs git >= 2.44); refusing to evaluate
where a lazy fetch could run` → exit 2. Never a silent retry without the flag (that would be the
silent fetch the ticket forbids). A repo-controlled stderr cannot forge this path in a harmful
direction: the generic branch also raises EvalError, so every 129 is a refusal. Exit code proven
end-to-end with a PATH shim that emulates a pre-2.44 binary (below).

## Scope discipline

Narrow D4 movement only: lazy-fetch suppression. I did NOT add `--no-replace-objects`,
`-c i18n.logOutputEncoding=UTF-8`, `-c log.follow=false`, or bytes-mode git — those are the
other C1 faults (c, d, a, b), still open for other seats / later waves. Alternates and
`clone --shared` semantics are untouched.

## Evidence (all commands run 2026-10-21, git 2.56.0, GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1)

1. Baseline fault reproduced (`/tmp/lz-fx`: promisor repo, `extensions.partialClone=origin`,
   remote `ssh://example.invalid/x.git`, `core.sshCommand` → `touch MARKER`):
   `printf '%s\n' $MISS | git cat-file --batch-check` → exit **0**, stdout `... missing`,
   **MARKER TOUCHED** — repo-configured command executed during audit, verdict unchanged (silent).
2. With suppression: `git --no-lazy-fetch cat-file --batch-check` → exit 0, `missing`, stderr empty,
   marker **absent**. Same with `-C` after the flag, and same via `GIT_NO_LAZY_FETCH=1`.
3. Selftest: **53/53** (was 50/50 at base; +3 new cases), exit 0:
   - `lazyfetch-trap-armed` — raw unsuppressed `cat-file --batch-check` in the fixture touches the
     marker (proves the trap is live, so the next check is not vacuous);
   - `lazyfetch-no-fetch-verdict-intact` — after auditing a draft citing the missing 40-hex token:
     marker absent **and** verdict is exactly `unresolved-full-hash` exit 1 (verdict, not error);
   - `lazyfetch-old-git-refused` — PATH shim emulating a git without the flag (exit 129) makes
     `run()` raise EvalError. Restores PATH; each new fixture lives in its own TemporaryDirectory.
4. CLI end-to-end (`/tmp/lz-cli`, fresh fixture): audit exit 1 with
   `UNCORRECTED unresolved-full-hash 1234567890abcdef1234567890abcdef12345678`, marker absent;
   raw control re-run touched the marker.
5. Old-git CLI: `PATH=<shim>:$PATH ... report-landing-audit.py ...` → stderr
   `could-not-evaluate: git --no-lazy-fetch unsupported (needs git >= 2.44); refusing to evaluate
   where a lazy fetch could run`, exit **2**, marker absent.

## Not verified / limits

- Did not test against a genuine pre-2.44 git binary (no such binary available; pacman paused) —
  the 129/unknown-option behavior is emulated by the shim, matching observed git parse-options
  behavior (exit 129 verified on this host for unknown options).
- Did not verify the git>=2.44 introduction claim against release notes; behavior-detection makes
  the exact version immaterial.
- `GIT_NO_LAZY_FETCH=1` works (verified standalone) but is deliberately not used; if the
  integrator wants belt-and-braces, adding it to `git_env()` would require adjusting the
  selftest's unsuppressed control.
- Hooks of audited repos are never run by the audit (read-only ops only); fixture `add`/`commit`
  run in selftest-owned repos.
