VERDICT: partial — the ignore rules and detached-HEAD guidance check out; the exit-3 and round-13 exit-4 explanations need qualifiers.

Attacked: the round-17 `.gitignore` additions and `AGENTS.md:6` VCS rule, against `scripts/hyaku/jj-lane.sh` and the older `scripts/hyaku/fleet-commit.sh`.

## Findings (by severity)

### Low — `AGENTS.md:6`: exit 3 is described too broadly

Quote: “Exit 3 means committed but not pushed.” In `jj-lane.sh`, the commit path exits 3 after committing and attempting `do_push` (`scripts/hyaku/jj-lane.sh:602-605, 658-670`). But the separate `push` command also exits 3 from push preflight, push rejection, landing verification, or `do_push` (`scripts/hyaku/jj-lane.sh:675-702`); that command does not create a commit. Thus exit 3 does not universally mean this invocation committed something. Clarify that the commit-subcommand’s exit 3 means its new commit was kept after a failed push, while the push-subcommand’s exit 3 reports a failed push attempt. Retrying `push` remains the safe instruction.

### Low — `AGENTS.md:6`: round-13 exit-4 rationale omits its condition

Quote: “an uncommitted QUALITY.md now exits 4”. The live gate returns `worktree_not_at_measured_revision` (exit 4) only “whenever every other check is clean”; a real content failure stays exit 1, and unreadable input or a failed Git read stays exit 3 (`.ufo/waves/round-13/measure.py:39-44`). Its decision branch also returns `documentation_mismatch` when the checks are not clean (`.ufo/waves/round-13/measure.py:465-484`). Qualify the note as a clean, otherwise-passing uncommitted edit. The advice to run after committing remains reasonable.

## Confirmed behavior

- Diffing `cff9e62..54a29268e2083caa2b1e0d54ee1e7d90961302f3` shows `.gitignore` adds exactly `.ufo/state/` and `__pycache__/`; `git check-ignore -v` matched `.ufo/state/` and its nested files to line 2, and root/nested `__pycache__/` contents to line 3. `.ufo/waves/...` and ordinary source paths were not ignored. The bare path `.ufo/state` without a slash returned 1; the directory spelling `.ufo/state/` and descendants matched. `git ls-files -c -i --exclude-standard` returned no tracked-but-ignored files.
- `jj-lane.sh` explicitly verifies the remote tip via `git ls-remote` and prints `landed <hash>` (`scripts/hyaku/jj-lane.sh:232-259`). Push recovery rebases the unpushed range and reports `rewritten` before the landed hash when applicable (`:318-337, 246-258`). The older `fleet-commit.sh` emits a `committed` line and then `pushed` after success (`scripts/hyaku/fleet-commit.sh:53-64`), so the rule’s `landed` versus older `pushed` distinction is accurate.
- On the lane at the round commit, `git rev-parse '@{u}'` failed with exit 128 and `fatal: HEAD does not point to a branch`; `git rev-parse --abbrev-ref HEAD` printed `HEAD` with exit 0; `git branch --show-current` printed nothing with exit 0. `git rev-parse refs/heads/master` returned the round commit, and `git remote -v` showed the GitHub `origin`. `.jj` is present. These observations support the detached-HEAD read guidance and colocated-repository description.
- Upstream Jujutsu Git-compatibility documentation confirms `.gitattributes` and hooks are unsupported: <https://docs.jj-vcs.dev/latest/git-compatibility/> — “.gitattributes: No” and “Hooks: No”.

## Commands and evidence

Read-only commands and results (all paths below are the lane unless noted):

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:.gitignore` — exit 0.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:AGENTS.md` — exit 0.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- .gitignore AGENTS.md` — exit 0; 2 ignore lines and 1 AGENTS rule added.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` — exit 0, round commit. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin symbolic-ref -q HEAD` — exit 1 (detached). `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` — exit 0; before this report it showed only the untracked falsify directory.
- `git check-ignore -v` matrix over `.ufo/state`, its descendants, root/nested `__pycache__`, `.ufo/interactive-sessions`, `.ufo/watchdog.log`, `.ufo/waves/...`, the report target, and `tools/check.py` — matrix shell exited 0; matches and nonmatches are summarized above.
- `git check-ignore -v -- '.ufo/state/' '__pycache__/' 'tools/__pycache__/'` — exit 0; each matched the expected `.gitignore` line. `git check-ignore -v -- '.ufo/state'` — exit 1; `git check-ignore -v -- '.ufo/state/nope'` and `git check-ignore -v -- 'a/b/__pycache__/nope'` — exit 0.
- `git ls-files -c -i --exclude-standard` — exit 0, empty output. `git ls-tree -r 54a29268e2083caa2b1e0d54ee1e7d90961302f3 --name-only | grep -E '__pycache__|\\.pyc$|^\\.ufo/state/' || echo no-tracked-matches` — no tracked matches.
- `git rev-parse '@{u}'` — exit 128; `git rev-parse --abbrev-ref HEAD` — exit 0, `HEAD`; `git branch --show-current` — exit 0, empty; `git rev-parse refs/heads/master` — exit 0; `git remote -v` — exit 0.
- `command -v jj && jj --version` — exit 0; installed `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a`.

## Residual risk and verification gaps

- No LSP device is mounted (`read xd://lsp` returned “No such tool”); no caller/diagnostic query was available. The shell helper and gate were inspected read-only, not executed; running the helper could commit or push. The literal claim “jj resets the git index on every mutation” was not independently reproduced; upstream docs establish that jj ignores Git’s staging area, not that exact universal wording.
- No tools were installed or updated. No scratch files were created; no lane history or tracked files were changed. This report is the sole lane write.