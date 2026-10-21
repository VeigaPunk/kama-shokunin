# Scout — repo-local ref-name channels (`report-landing-audit.py`)

Scope: ONE repo-local state channel for `tools/report-landing-audit.py` at base
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d` — ref *name resolution*: tag vs branch
`master`, `$GIT_DIR/master`, `refs/master`, `refs/remotes/master`, packed-refs
oddities, `git notes`, `refs/namespaces`, hex-shaped ref names. Fixtures only under
`/tmp`; no lane repo was modified (one read-only `git status`/`for-each-ref`).

## Verdict

**affects-verdict.** Repo-local ref naming silently redirects every lane-side read
the audit makes: `git log <branch>` (`round_commits`, base blob line 148),
`git ls-tree <branch>` (`load_source_urls`, 211), `git show <branch>:<errata>` (339)
and the `rev-parse --verify <branch>^{commit}` gate (403). Both directions observed:
false **clean** (omitted lane commit disappears) and false **failed** (forged commit
appears). Separate effect: a ref whose *name* is a cited abbreviation makes
`landed-unresolved`/`landed-ambiguous` resolve to `found`.

- Crashes on this channel are already typed: broken refs → `fatal` rc 128 → `EvalError`
  → exit 2, never a verdict (F9/F10 below).
- No command execution was found on this channel (unlike the promisor/`sshCommand` fault).
- The uncommitted round-23 candidate in the lane worktree
  (`GIT_ISOLATION = --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
  -c log.follow=false`, sha256 `b6064767b1ce6b8833f977bb9fdfb45702c70427a9a792961ed3cc2636d89bda`)
  changes **none** of these outcomes; it already concedes in its own `git_env`
  docstring that it "does not isolate repository-local config or refs".

## Governing doc

gitrevisions(7), section `<refname>` — <https://git-scm.com/docs/gitrevisions>
(2.56.0, page updated 2026-09-28; accessed 2026-10-21):

> "When ambiguous, a *<refname>* is disambiguated by taking the
> first match in the following rules:" (15 words)

then "3. otherwise, *refs/tags/<refname>* if it exists;", "4. otherwise,
*refs/heads/<refname>* if it exists;" — i.e. **tags outrank branches**, and
`$GIT_DIR/<refname>` and `refs/<refname>` outrank both. Local `man 7 gitrevisions`
on git 2.56.0 shows identical text (`/tmp/kama-r23-refs/gitrevisions.txt:37-52`).
The audit invokes the bare name, so this documented order applies to it.

## Observed facts (git 2.56.0, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`)

Micro, `/tmp/kama-r23-refs/micro` (branch `master` at B, `refs/tags/master` at A):

    git rev-parse master            -> A            (warning: refname 'master' is ambiguous.)
    git rev-parse master^{commit}   -> A
    git rev-parse refs/heads/master -> B
    git log --format='%H %s' master -> A only, rc=0, stderr "warning: refname 'master' is ambiguous."

The audit's `git()` (base 87-98) checks only `returncode` and returns stdout; the
warning goes to the captured stderr and is never printed. Observed directly on the
F1 fixture: `git log` rc=0 with stderr `warning: refname 'master' is ambiguous.\n`,
while the audit itself returned rc=0 with **empty stderr** and `status=clean`.

Resolution channels, each verified to move `git rev-parse master` / `git log master`
without a non-zero exit (rule numbers from the doc above):

| Channel | Result |
|---|---|
| `refs/tags/master` -> A | A, warning only (rule 3) |
| `$GIT_DIR/master` -> `ref: refs/heads/sideline` | A, warning only (rule 1) |
| `refs/master` -> A | A, warning only (rule 2) |
| branch deleted, `refs/remotes/master` -> A | A, **no warning** (rule 5) |
| branch deleted, `refs/remotes/master/HEAD` symref | A, **no warning** (rule 6) |
| loose `refs/heads/master` = `ref: refs/heads/other` | other@A, **no warning** (symref file) |
| `refs/tags/master` written as a symref file | other@A, warning only |
| packed-refs duplicate `refs/heads/master` line | **last line wins**, silent, rc=0 |
| packed-refs broken line `not-an-oid refs/heads/broken` | `fatal: unexpected line in .git/packed-refs`, rc=128 |
| packed-refs `ref: refs/heads/other refs/heads/master` | `fatal: unexpected line`, rc=128 — packed-refs cannot store symrefs: "with the exception of hidden refs, broken refs, and symbolic refs" (<https://git-scm.com/docs/git-pack-refs>, accessed 2026-10-21) |
| packed-refs forged peel `^<other-oid>` under an annotated `master` tag | `for-each-ref`/`show-ref -d` show the forged peel; `rev-parse master^{commit}` and `cat-file --batch-check master^{commit}` still return the real tag target → **no audit effect** |
| `git notes add` on lane HEAD | `log`/`show`/`ls-tree` unchanged (F11) |
| `refs/namespaces/ns/refs/heads/master` -> A | `rev-parse master` unchanged (F12) |
| 40-hex ref name (`refs/tags/aaaaaaaa…a7`) | `cat-file --batch-check` on that 40-hex still `missing` → full-hash citations immune (F13) |
| 7-hex ref name `deadbee1` | `cat-file --batch-check` resolves it to the ref target, and a ref **beats a unique object prefix** (blob prefix `45b983b` became a commit once a tag of that name existed) → citation spoof (F8) |

`git rev-parse --disambiguate=<prefix>` was checked as a ref-free primitive
(`/tmp/kama-r23-refs/disamb`): it returns only object-DB matches, ignores refs
(same prefix before/after adding a same-named tag), exits 0 with empty output for
a nonexistent 7-hex or a fabricated 40-hex. Doc: git-rev-parse(1)
`--disambiguate=<prefix>` — "Show every object whose name begins with the given
prefix" (<https://git-scm.com/docs/git-rev-parse>, accessed 2026-10-21).

## End-to-end grid

Fixtures `/tmp/kama-r23-refs/grid/<case>/{lane,fleet}`: lane has an empty
`registry/report-landing-errata.tsv` (author 900), `round-1: a` (1000), `round-1: b`
(1100); fleet commits `.ufo/reports/round-1/kama.md` at 1200 citing `a` only.
Command: `python3 <script> --lane-repo lane --fleet-repo fleet --rounds 1 [--branch B]`.
`base` = blob `4fe9339f:tools/report-landing-audit.py` (847 lines, sha256
`09ecd63b…ab3b3f`); `cur` = lane worktree copy (864 lines); `+refs` = `cur` with
`--branch refs/heads/master` (zero code edits).

| Case | base | cur | cur + refs/heads/master |
|---|---|---|---|
| C0 control, `b` omitted | rc1 `landed-omitted <b>` | rc1 same | rc1 same |
| F1 `refs/tags/master` -> a | **rc0 clean** | **rc0 clean** | rc1 `landed-omitted <b>` |
| F2 `$GIT_DIR/master` symref -> sideline@a | **rc0 clean** | **rc0 clean** | rc1 correct |
| F3 `refs/master` -> a | **rc0 clean** | **rc0 clean** | rc1 correct |
| F4 branch gone, `refs/remotes/master` -> a | **rc0 clean** | **rc0 clean** | rc2 typed refusal |
| F5 packed-refs duplicate -> a | **rc0 clean** (silent) | **rc0 clean** | rc0 clean (residual) |
| F6 `refs/heads/master` symref -> other@a | **rc0 clean** (silent) | **rc0 clean** | rc0 clean (residual) |
| F7 `refs/tags/master` with forged `round-1: forged` | **rc1 landed-omitted 474437…** (false fail) | rc1 same | rc0 correct |
| F8 report cites `deadbee1` (no such object) | control rc1 `landed-unresolved deadbee1`; with `refs/tags/deadbee1` **rc0 clean** | same | **rc0 clean** (needs a `lookup` fix) |
| F9 `refs/tags/master` -> tree | rc2 refusal | rc2 | rc1 correct |
| F10 packed-refs broken line | rc2 refusal | rc2 | rc2 |
| F11 `git notes` | rc1 unchanged | rc1 | rc1 |
| F12 `refs/namespaces/.../master` -> a | rc1 unchanged | rc1 | rc1 |
| F13 fabricated 40-hex + `refs/tags/<40hex>` | rc1 `unresolved-full-hash aaaa…a7` | same | same |
| F14 annotated tag `master` + forged peel | **rc0 clean** (tag redirect) | rc0 | rc1 correct |

Raw output: `/tmp/kama-r23-refs/grid.out`. Fixture runner: `/tmp/kama-r23-refs/grid.py`.

## What this means for the C1 calibration claim

1. The claim's fault grid is incomplete for the stated promise. The candidate
   direction closes replace / lazy-fetch / encoding / `log.follow`, but ref naming is
   an independent channel that yields a **silent clean** from a one-command
   `git tag master <old>` (F1), a stray `.git/master` (F2), a remote-tracking ref when
   the branch is absent (F4), and a malformed packed-refs duplicate (F5).
2. Minimal fix A (branch qualification) — pass `refs/heads/<branch>` at base lines
   148 (`log`), 211 (`ls-tree`), 339 (`show {branch}:{ERRATA}`), 403 (`rev-parse
   --verify`) — was verified by running the **unmodified** current script with
   `--branch refs/heads/master`: it restores the correct verdict on F1-F4, F7, F9,
   F14 while leaving C0/F11/F12/F13 untouched. F4 then becomes a typed exit 2, which
   is the intended "cannot evaluate" outcome for a missing branch.
3. Fix B (citations) is separate: `lookup` (base 100-134) feeds tokens straight to
   `git cat-file --batch-check` (114), which accepts ref names. F8 shows a fabricated
   abbreviation `deadbee1` going from `landed-unresolved` to `clean` once a 7-hex ref
   of that name exists, and a ref also overrides a unique object prefix. Using
   `rev-parse --disambiguate=<token>` (object DB only) plus a 40-hex/
   `^{commit}` type check would close it; note the current grid's `--branch
   refs/heads/master` run still reports F8 clean.
4. Residual, not closable by name qualification: the branch's own ref storage is the
   audited state. A packed-refs duplicate line (F5) and a symref `refs/heads/master`
   (F6) both read as a normal branch with no warning; distinguishing them from an
   honestly rewritten branch is not possible with `rev-parse`/`log` alone. The
   toolkit wording should therefore say "ref *names* are resolved to the branch, not
   to tags/aliases", not "audited repos cannot redirect it". For reference,
   `git rev-parse --symbolic-full-name master` on an ambiguous name prints
   `error: refname 'master' is ambiguous` to stderr but **exits 0** with empty stdout,
   so it can detect ambiguity only by parsing text, not by exit code.

## Not verified

- Not run against the real lane/fleet repos (fixtures only). The live lane currently
  has only `refs/heads/master` and `refs/remotes/origin/{HEAD,master}` and no
  `.git/master`, so the fault is latent, not active, at base.
- No execution vector found here; I did not test config-driven execution
  (`core.fsmonitor`, pager, textconv) — that is the config channel, not refs.
- Only git 2.56.0; no older/newer git, no sha256-object repositories, no packed-refs
  trait-header variants beyond the two malformed lines above.
- No code change and no selftest run with these cases added (out of seat scope).
- The current-worktree script was copied read-only for comparison; its uncommitted
  state is another seat's work and was not modified.

## Files written

- `.ufo/waves/round-23/build/advice/ScoutNotesRefs.md` (this report).
- Scratch only: `/tmp/kama-r23-refs/audit-base.py`, `audit-current.py`, `harness.py`,
  `qualify.py`, `grid.py`, `grid.out`, `gitrevisions.txt`, and fixture repos under
  `/tmp/kama-r23-refs/{micro,packed,packed2,garbage,notes,peeled,symref,symref2,head,
  ambig,disamb,rules,tagsym,e2e,grid}`.
- No installs or upgrades; no pacman transactions.
