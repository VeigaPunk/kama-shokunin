
## Repo-local git state in `report-landing-audit.py` — round 23 channel map (DRAFT, not integrated)

Scope: `tools/report-landing-audit.py` as it stands in the lane working tree on 2026-10-21 (uncommitted; HEAD `4fe9339f` blob `fcc255ce` carries the older `git_env` only). Evidence: static reading of the working-tree file plus five fixture probes in `/tmp` with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, git 2.56.0. The audited repo's own state is not trusted by default; this section lists which of its channels the tool now refuses, which it still follows, and which were not probed.

The docstring's "Errors are never verdicts" (line 45) covers exit status. It does not cover repository-local state, which changes the answer without any error. Keep the two apart.

### Isolated by the working-tree version

| Channel | Mechanism | Observed effect before |
|---|---|---|
| Inherited `GIT_*` env (`GIT_DIR`, object dirs, index) | `git_env()` strips every `GIT_*` key (lines 88-94) | selftest wrote into the named repo |
| User, system, global config | `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1` | hooks and `gpgsign` from global config broke selftest |
| `refs/replace/*` substitution | `--no-replace-objects` in `GIT_ISOLATION` (line 83) | `git replace` made an omitted commit look clean |
| Promisor lazy fetch and its `core.sshCommand` | `--no-lazy-fetch` (line 83) | a repo-configured command ran during `cat-file --batch-check` |
| Log re-encoding via `i18n.logOutputEncoding` | `-c i18n.logOutputEncoding=UTF-8` (line 84) | non-ASCII subject under ISO-8859-1 config raised a traceback |
| `log.follow` | `-c log.follow=false` (line 85) | repo-local config changed the `--diff-filter=A` cutoff history |
| Undecodable bytes in git output | strict `decode("utf-8")` raises `EvalError` (lines 109-113) | traceback, exit 1 |

Rule: a channel is isolated only when the flag or config override is passed on every `git()` call. Passing `GIT_*` scrubbing alone isolates the environment, not the repository.

### Still open (observed in fixtures, git 2.56.0)

1. **Branch-name shadowing by a tag.** A tag named `master` beside branch `master` at a different commit makes `rev-parse --verify master^{commit}` return the tag's commit, rc 0. Git prints `warning: refname 'master' is ambiguous.` to stderr. `log master` then walks the tag's history (one commit in the fixture, the branch has two). `--branch` is therefore read as a bare refname in `round_commits` (line 165), `load_source_urls` (line 228), the errata `show` (line 356), and the rev-parse guard (line 420). An older history means fewer `round-N:` commits, so an omission can disappear: a false clean. [INFERENCE] Mitigation is to pass `refs/heads/<branch>`; not applied.

2. **`.git/info/grafts` still applies under `--no-replace-objects`.** Fixture: three empty commits, grafts file cutting the newest commit's parent; `git log master` lists 1 commit with and without `--no-replace-objects`. Deprecation hint goes to stderr. A graft can hide history the same way as channel 1.

3. **`.git/shallow` still applies.** Fixture: shallow boundary on the middle commit; both invocations list 2 of 3 commits. Same false-clean risk as channel 2.

4. **`objects/info/alternates` makes foreign objects resolvable.** Fixture: a commit present only in another repo's object store reports `commit`, rc 0, via `cat-file -t`. The contract treats alternates as legitimate, so "resolvable" means "resolvable in lane, fleet, or an alternate object store". A fabricated 40-hex citation that exists in an alternate passes `unresolved-full-hash`.

### Checked and not a channel

- `diff.<driver>.textconv` in repo-local config plus a committed `.gitattributes` `diff=` rule does not change `git show HEAD:<path>` or `git cat-file blob HEAD:<path>` (fixture: both return the raw `hello report`). The report reader is therefore not exposed to textconv on this git version.

### Not probed

- `log.showSignature` (repo-local): would print signature lines into the `--format` output; expected to fail as `EvalError` (exit 2), not as a clean verdict. Unverified.
- `diff.renames` and rename detection on the `--diff-filter=A` cutoff: pathspec-limited to the report path, so the rename source is excluded. Unverified.
- Other `.git/config` keys read by `log`, `show`, `ls-tree`, `cat-file`. Unverified.

### Boundary

The working-tree version isolates the channels in the table above. It does not make the audited repository trusted. Channels 1-4 remain. Treat a clean verdict from an untrusted repository as clean only for the channels listed as isolated. Exit-code limits from the round-21 exit-contract probes are outside this section and are not claimed fixed here.

Sources for the git semantics cited: S070 (gitrevisions, abbreviated names and `^{commit}` peeling), S071 (cat-file `--batch-check` missing/ambiguous output), S073 (git-log `%at` and `--diff-filter=A`). Refname precedence, grafts, shallow and alternates behavior are from the local fixtures above, not from a fetched source row. [INFERENCE] they match the upstream documentation; no source row was added.

recheck: rerun the fixtures named above on any git upgrade; reopen `tools/report-landing-audit.py` lines 83-85 and 88-114 and the four `git()` call sites (`round_commits`, `load_source_urls`, `load_errata`, `run`) before reusing this map.
