# LazyFetchFix — C1 fault (e) lazy fetch during audit: fixed, fail-closed, selftested

Seat: CloseKama22.LazyFetchFix (leaf). Clone /tmp/kama-r23/LazyFetchFix at base
4fe9339f8fc3a4a4a479d9c938a850da12f1124d. Deliverables: `out/LazyFetchFix/lazyfetch.patch`,
`out/LazyFetchFix/rationale.md`. One tracked file: `tools/report-landing-audit.py` (+74/−4).

## What changed

1. `git()` (the script's only subprocess site) now runs every git invocation as
   `git --no-lazy-fetch -C <repo> ...` — git's global flag (same family as `--no-replace-objects`;
   documented at https://git-scm.com/docs/git, 2.56.0; cf. sibling S090 in `advice/SrcPartialClone.md`).
   Covers `cat-file --batch-check` (the L1 probe vector), `log`, `ls-tree`, `show`, `rev-parse`.
2. Fail-closed: unknown-option exit 129 with `no-lazy-fetch` in stderr → typed EvalError → exit 2
   ("refusing to evaluate where a lazy fetch could run"), never a silent fetch. Chose the global
   flag over `GIT_NO_LAZY_FETCH=1` because the env var is silently ignored by old git (fail-open);
   flag-only also keeps the selftest's unsuppressed control clean.
3. Selftest +3 cases (own TemporaryDirectory; fixture: `extensions.partialClone=origin`, remote
   `ssh://example.invalid/x.git`, `core.sshCommand` touching a marker): `lazyfetch-trap-armed`
   (raw cat-file touches marker — trap live), `lazyfetch-no-fetch-verdict-intact` (audit of a
   missing 40-hex token: marker absent, verdict exactly `unresolved-full-hash`, exit 1),
   `lazyfetch-old-git-refused` (PATH shim without the flag → EvalError).

## Measured results (2026-10-21, git 2.56.0)

- Selftest **53/53** (base was 50/50; controls unchanged), exit 0.
- Baseline fault reproduced pre-fix: `cat-file --batch-check` on missing oid → exit 0, `missing`,
  **core.sshCommand executed** (marker touched) — silent execution, verdict unchanged.
- Post-fix CLI audit of same fixture: exit 1, `unresolved-full-hash`, marker **absent**;
  raw control still touches marker (suppression is the difference, not the fixture).
- Old-git shim via real CLI: `could-not-evaluate: git --no-lazy-fetch unsupported (needs git
  >= 2.44); refusing to evaluate where a lazy fetch could run`, exit **2**, marker absent.

## Grid impact (finite fault grid, frozen 4fe9339f vs current)

- Fault (e) promisor+sshCommand lazy fetch: executed pre → suppressed post (verdict kept, no exec).
- New sub-fault covered: git lacking the flag → crash-free typed refusal exit 2 pre-existing
  generic error path, now with explicit message and selftest.
- Controls: all 50 original selftest cases pass unchanged; no other verdict path touched.

## Risks / limits

- No genuine pre-2.44 git available (pacman paused); 129 behavior emulated by shim (matches
  observed git parse-options exit 129 on host).
- "git>=2.44" introduction claim not checked against release notes; detection is behavioral,
  so the exact version is immaterial.
- Faults (a,b,c,d) (encoding, replace refs) intentionally out of scope.
- No installs performed; no pacman; no tooling changes to record.
