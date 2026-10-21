# ScribeKnowledgeEntry — report-landing-audit repo-local git channels (round 23, DRAFT)

Seat: CloseKama22.ScribeKnowledgeEntry. Draft only; no corpus file was edited.

## Target entry
- `grep report-landing-audit` over `corpus/knowledge/` returned no hits. No knowledge entry names the tool.
- Nearest entry chosen: `corpus/knowledge/error-is-not-a-verdict.md` (frontmatter `verified-at 2026-10-21`). It holds the tool's governing rule, "Errors are never verdicts" (`tools/report-landing-audit.py:45`, HEAD blob `fcc255ce`), in its exit-status form.
- Draft section: `.ufo/waves/round-23/build/out/ScribeKnowledgeEntry/error-is-not-a-verdict.appended.md`. Integration into the corpus file is L1's call. It will also need the frontmatter `verified-at`/`recheck` lines updated, which the draft does not touch.

## What the section says (summary)
- **Isolated** in the lane working tree (`tools/report-landing-audit.py` lines 83-85 `GIT_ISOLATION`; 88-94 `git_env`; 97-114 `git()`): inherited `GIT_*` env, user/system/global config, `refs/replace` (`--no-replace-objects`), promisor lazy fetch and its `core.sshCommand` (`--no-lazy-fetch`), `i18n.logOutputEncoding` (`-c ...=UTF-8`), `log.follow` (`-c log.follow=false`), and undecodable output (EvalError, exit 2).
- **Still open**, observed in fixtures at git 2.56.0: (1) a tag named `master` shadows branch `master` for `--branch` resolution, so `log master` walks the tag history and an omission can vanish as a false clean; (2) `.git/info/grafts` still applies under `--no-replace-objects`; (3) `.git/shallow` still applies; (4) `objects/info/alternates` makes foreign objects resolvable.
- **Checked, not a channel:** repo-local `diff.<driver>.textconv` plus committed `.gitattributes` does not alter `git show HEAD:<path>` or `cat-file blob` output.
- **Not probed:** `log.showSignature`, other repo-local config keys read by `log`/`show`/`ls-tree`/`cat-file`, and rename detection on the `--diff-filter=A` cutoff.

## Evidence
- Working-tree tool (uncommitted): `git -C kama-shokunin status --short` → ` M tools/report-landing-audit.py`, `?? .ufo/waves/round-23/`. Working-tree file: 864 lines, `git hash-object` `9b12bb8a`. HEAD `4fe9339f` blob `fcc255ce` (847 lines, no `GIT_ISOLATION`; `git show HEAD:... | grep -c GIT_ISOLATION` → 0). The working-tree change was made by someone other than this seat; I did not modify the lane file.
- Fixture probes (`/tmp/kama-r23-scribe-*`, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, `git version 2.56.0`):
  - P1 tag shadow: `rev-parse --verify -q master^{commit}` → tag commit (rc 0), stderr `warning: refname 'master' is ambiguous.`; `git log --format=%H master | wc -l` → 1 (branch has 2).
  - P2 grafts: `git log` → 1 with and without `--no-replace-objects` (3 commits, graft cuts parents).
  - P3 shallow: 2 with and without `--no-replace-objects` (3 commits, boundary on middle).
  - P4 alternates: `git -C a cat-file -t <oid only in other repo>` → `commit`, rc 0.
  - P5 textconv: `git show HEAD:f.md` and `git cat-file blob HEAD:f.md` both → `hello report` (driver `tr a-z A-Z` not applied).
- Source rows cited in the draft already exist: S070 (gitrevisions), S071 (cat-file `--batch-check`), S073 (git-log `%at`, `--diff-filter=A`). No new S-row was added; refname precedence, grafts, shallow and alternates rest on the fixtures above and are marked `[INFERENCE]` where they go beyond them.

## Not verified
- I did not run the tool's `--selftest` or any audit against the lane or fleet repos.
- The "before" column in the draft's isolation table is taken from round-21 and round-23 L1 probe observations at base `a29bb84`/`4fe9339f`; I did not re-run those.
- `log.showSignature`, other repo-local keys, and rename detection are unprobed (listed in the draft).

## Suggested follow-ups for L1 (not applied)
- Resolve `--branch` as `refs/heads/<branch>` in `round_commits`, `load_source_urls`, `load_errata`, and the rev-parse guard, and add a selftest case with a tag named `master` (channel 1).
- Decide whether grafts, shallow, and alternates are refused, detected, or disclosed as limits (channels 2-4). The draft discloses them.

## Tools
No installs or updates. Read-only and fixture-only work with existing `git` 2.56.0.

## Files written
- `.ufo/waves/round-23/build/out/ScribeKnowledgeEntry/error-is-not-a-verdict.appended.md` (draft section, 5377 bytes)
- `.ufo/waves/round-23/build/advice/ScribeKnowledgeEntry.md` (this report)
- Temp fixtures under `/tmp/kama-r23-scribe-*` (removed after the probe run below)
