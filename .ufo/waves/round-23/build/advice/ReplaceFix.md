# ReplaceFix: replace-ref and grafts isolation for tools/report-landing-audit.py

Seat: CloseKama22.ReplaceFix (leaf executor). Base: master `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, git 2.56.0. Scratch clone: `/tmp/kama-r23/ReplaceFix` (clone of base; base blob `fcc255c`). Nothing committed, pushed, or written to the lane checkout, the lane index, or the fleet root.

## Deliverable

- `.ufo/waves/round-23/build/out/ReplaceFix/replace.patch`: `git diff` of `tools/report-landing-audit.py` against base, 120 insertions and 6 deletions. It applies to `4fe9339f`. It does not apply cleanly to the lane working tree, which carries L1's uncommitted candidate (see Integration).
- Evidence: `out/ReplaceFix/replace-evidence.sh` and `replace-evidence.txt`; `out/ReplaceFix/grafts-replace-probe.sh` and `grafts-replace-probe.txt`.

## Axes

1. Verdict fidelity under `refs/replace/*` (substituted objects, blobs, commits).
2. Verdict fidelity under `.git/info/grafts` (rewritten parents).
3. Operability: the historical ledger must not change on the real repos.
4. Footprint: one script, no new tools.

## Decisions (each with observed evidence)

**1. `--no-replace-objects` on every git call: yes.** `git()` is the only `subprocess` call site (`tools/report-landing-audit.py`, base line 89, patched line 104). It now runs `["git", *GIT_ISOLATION, "-C", repo, *args]` with `GIT_ISOLATION = ("--no-replace-objects",)`.
Quote, local `git(1)` (`/usr/share/man/man1/git.1.gz`): "Do not use replacement refs to replace Git objects. This is equivalent to exporting the GIT_NO_REPLACE_OBJECTS environment variable with any value."
Observed in `replace-evidence.txt` and `grafts-replace-probe.txt`:
- Tip commit replaced by an unrelated same-parent commit. Default `git log`: `ec9f588|z|unrelated;69c64e9|...one`. With the flag: `ec9f588|kama-shokunin|two;69c64e9|...one` (E7, E8).
- `cat-file --batch-check` of the replaced tip: default size 160, flag size 178 (E10).
- Fabricated 40-hex `1234567890abcdef1234567890abcdef12345678` with `refs/replace/<fake>`: default `commit 118` (found), flag `missing` (E11 in `replace-evidence.txt`).
- Committed report blob replaced: `git show HEAD:f` default `tampered`, flag `one` (E12).

**2. `GIT_NO_REPLACE_OBJECTS` env: not required; included as the mirror.** git itself exports the variable to processes it starts when the flag is given: alias child sees `1` with the flag and `0` without (E21, `replace-evidence.txt`). The flag already reaches child processes (E14: alias child shows the un-replaced commit with the flag). `git_env()` still sets `GIT_NO_REPLACE_OBJECTS="1"`, because the lane's own gates set both: `.ufo/waves/round-12/fidelity.py:84` and `.ufo/waves/round-12/reproduce.py:33`. It is defense in depth, not a correctness requirement. Lazy-fetch children were not tested directly.

**3. Grafts: refused (exit 2), not neutralized.** `--no-replace-objects` does not cover grafts. E18: with a graft that makes the tip parentless, the default and flag walks both show 1 commit; `GIT_GRAFT_FILE=/dev/null` shows 2. `GIT_GRAFT_FILE` and `GIT_SHALLOW_FILE` are present in the git binary (`strings`), but neither appears in git(1) (`zcat git.1.gz`, only `GIT_NO_REPLACE_OBJECTS` matches) nor in the official page https://git-scm.com/docs/git (fetched with curl on 2026-10-21; grep matched only `GIT_NO_REPLACE_OBJECTS`). I rejected neutralizing with an undocumented variable: a future git that honors grafts under a renamed variable would regress silently to a false clean. The refusal depends only on the file's existence:
`refuse_grafts(repo)` runs `git rev-parse --git-path info/grafts` (E22: returns `.git/info/grafts`) and raises `EvalError` when that path exists. It is called for the lane and the fleet repo in `run()` after the two `rev-parse --verify` checks. Cost: a repo with a grafts file gets could-not-evaluate rather than a verdict. The real repos have no grafts file (`kama-shokunin/.git/info/grafts` and `shokunin/.git/info/grafts` both absent, checked by path existence).

**4. Shallow (`.git/shallow`): not covered; not in the assignment.** E20: with a shallow boundary, the default walk shows only the tip, and `GIT_SHALLOW_FILE=/dev/null` shows both commits. This is the same family as grafts and is a residual for L1. If L1 wants it, the same refusal applies to `rev-parse --git-path shallow`. Real repos: absent.

**5. Blob substitution: covered by the flag.** E12 shows the report bytes read by `git show HEAD:<rel>` can be substituted without the flag. Fixtured as the fourth selftest case.

## Patch contents

- Module docstring: a paragraph on the replace/grafts policy; the exit-2 list adds "grafts file".
- `GIT_ISOLATION` (lines 84–87) with comment.
- `git_env()` (line 90): docstring corrected. The old text said the environment could not redirect the audited repos, which is true of `GIT_*` variables but says nothing about repo-local state. Adds `GIT_NO_REPLACE_OBJECTS="1"`.
- `git()` (line 102): argv includes `*GIT_ISOLATION`.
- `refuse_grafts()` (line 405) and two calls in `run()` (lines 430–431).
- Selftest (lines 826–912), four new cases:
  - `replace-ref-does-not-hide-omitted-commit`: lane has `round-1: work` and `round-1: omitted`; `omitted` is replaced by an unrelated same-parent commit by someone else. Fleet report cites only `work`. Expects exactly `[("landed-omitted", <omitted full sha>)]`, rc 1.
  - `replace-ref-does-not-resolve-fabricated-hash`: `refs/replace/<fake>` points at a real commit; fake hash in `## Notes`. Expects exactly `[("unresolved-full-hash", fake)]`, rc 1.
  - `grafts-file-is-refused`: `.git/info/grafts` written in the fixture; `is_error(run)` must be true.
  - `replace-ref-does-not-substitute-report-bytes`: a replacement blob for the committed report. Expects rc 0 and zero defects.

## Expected selftest outcome (not executed)

The base selftest has 50 cases: 47 literal `check("...")` calls plus the three-iteration loop `check(label, ...)`. This matches L1's "50/50".
- Patched expected: `selftest cases=54 failed=0`.
- Base-behavior expected by construction, using the E-series semantics: the four new cases fail. Case 1 gives rc 0 and no defects, because the replacement hides the omitted commit. Case 2 gives rc 0, because the fake hash resolves to the replacement. Case 3 raises no error. Case 4 gives `landed-omitted` for the work commit, because the substitute blob has an empty Landed section.

## Not run or not verified

- Did not run `--selftest`, the probe, or the audit on the real repos. The lane rule skips tests during the wave. I ran one `ast.parse` syntax-only check on the version before case 4, which passed. Case 4 has not been parse-checked.
- Only the git-level behavior (E7–E22) was exercised, on git 2.56.0.
- Not covered by this patch: probe rows (a) logOutputEncoding, (b) invalid UTF-8, (e) promisor lazy-fetch executing `core.sshCommand`. The L1 candidate's `GIT_ISOLATION` carries those channels; this patch does not.
- Shallow: see decision 4.

## Checks for the main agent (post-integration)

1. `python3 -m py_compile tools/report-landing-audit.py`, then `python3 tools/report-landing-audit.py --selftest`. Expect `selftest cases=54 failed=0`.
2. Sensitivity: run the patched selftest against base `4fe9339f`. Expect exactly the four new case names as FAIL and the 50 existing as ok.
3. Ledger invariance: run `python3 tools/report-landing-audit.py --rounds 10- --json` on the same lane and fleet commit with the base script and the patched script, and compare. Static basis: neither repo has any `refs/replace` entry (`for-each-ref` and `replace -l` empty), no packed replace refs, no grafts, no shallow file.
4. Probe rows (c) and (d): rerun `/tmp/kama-r23-probe/probe.sh` with `AUDIT` pointing at the patched script. Expect `failed` with `landed-omitted` and `unresolved-full-hash` respectively.

## Integration notes

- L1's working-tree candidate already defines `GIT_ISOLATION` with `--no-replace-objects` first, and the same `git()` argv. Take the tuple and keep L1's extra entries. Expect conflicts in `git_env` (docstring and env), `git()`, the module docstring's exit list, and the selftest tail.
- `probe.sh` line 43 (F3) runs `git commit-tree` with no identity environment. In this seat's shell the same call fails with `fatal: unable to auto-detect email address`. Two probe runs I inspected (`run.26zX/f3`, `run.5M1Q/f3`) do contain the replace ref, so row (c) holds in those runs. It should still carry `GIT_AUTHOR_*` and `GIT_COMMITTER_*` to be deterministic.
- Identical fixtures produced different verdicts across probe runs (`run.26zX/f3` clean, `run.5M1Q/f3` failed). That is consistent with different `AUDIT` script versions. Confirm which script each run used before reading the grid.

## Tooling

No installs or updates. Used the pre-installed git 2.56.0, curl, zcat, and strings.

## Files written

- `.ufo/waves/round-23/build/advice/ReplaceFix.md` (this report)
- `.ufo/waves/round-23/build/out/ReplaceFix/replace.patch`
- `.ufo/waves/round-23/build/out/ReplaceFix/replace-evidence.sh`, `replace-evidence.txt`
- `.ufo/waves/round-23/build/out/ReplaceFix/grafts-replace-probe.sh`, `grafts-replace-probe.txt`
- Scratch clone `/tmp/kama-r23/ReplaceFix` (working copy with the patch applied, not a deliverable)
