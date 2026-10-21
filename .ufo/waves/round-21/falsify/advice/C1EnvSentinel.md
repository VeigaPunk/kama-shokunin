VERDICT: partial - listed GIT_* vars, XDG git/config, hooks, gpgsign, core.fsmonitor and safe.directory do not redirect; audited-repo config/refs/alternates/shallow and GIT_CEILING stripping do (code exec, false PASS, wrong repo)

Attacked: tools/report-landing-audit.py @a6617149 - git_env() (GIT_* strip, GIT_CONFIG_GLOBAL/NOSYSTEM pin), git(), selftest(), and the audited repos' own .git state. Throwaway fixtures only; lane and fleet are never passed to the tool.
Harness: out/C1EnvSentinel/repro.py --tool <a6617149 tool> --work <dir> --out results.txt -> exit 0 (run 3, unmodified tool; out/C1EnvSentinel/results.txt). Candidate run -> results-candidate.txt, exit 0.

## Refuted (isolated)
- GIT_DIR, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_COMMON_DIR, GIT_WORK_TREE, GIT_NAMESPACE, GIT_CONFIG_COUNT, GIT_CONFIG_GLOBAL/SYSTEM: audit output identical (A1-A7 ISOLATED). Control: A3/A4 change output if honored, so the probe discriminates.
- Selftest rc 0, 32/32, with every GIT_* decoy set plus a GIT_TEMPLATE_DIR hook exit 1 (B2, hook_marks=0). TMPDIR inside a worktree: rc 0 (B3).
- XDG_CONFIG_HOME/git/config and HOME/.gitconfig carrying gpgsign, templateDir hook, fsmonitor, showSignature, safe.directory: audit and selftest unaffected, marks=0 (C1a-b, C2a-b). Plain git under the same config fires them (C1c, C2c). git does not read XDG_CONFIG_DIRS (C4 NOT-READ).
- gpgsign: the GIT_CONFIG_GLOBAL pin alone suffices; dropping the explicit `-c commit.gpgsign=false` still passes (S-D PIN-HOLDS).
- Audited repo's core.hooksPath and core.fsmonitor are NOT run by the audit (F6a, F7a); the same repo runs them on commit/status (F6b, F7b).
- safe.directory: fail-closed, not a bypass. Root-owned lane: rc 2 "detected dubious ownership" (D1). Operator safe.directory is ignored by design (D3); plain git accepts it (D2).

## Confirmed
1. [HIGH] Audited config runs a program as the operator (F1, F9). Exploit: lane/.git/config `log.showSignature=true` + `gpg.program=<payload>`, plus one commit whose gpgsig header is written by plumbing (`hash-object --literally`, no key) on master. The routine audit runs `git log`, so the payload runs. Evidence: F1a marks=0 -> F1b EXEC `gpg-F1.sh --keyid-format=long --status-fd=1 --verify ...`. F9: same via the fleet repo's config. Impact: lane-to-operator code execution on the normal audit path. Fix: `-c log.showSignature=false` on every git call.
2. [MED] Audited-repo state silences the audit, exit 0 "clean" (F3, F4, F5, F5b). refs/replace hides omitted c2 (F3a). Fleet objects/info/alternates resolves a decoy-only hash (F4). .git/shallow (F5, rev-list 3->1) and info/grafts (F5b) hide history. Operator GIT_NO_REPLACE_OBJECTS=1 is stripped, so it cannot turn replacement off (F3b). Fix: GIT_NO_REPLACE_OBJECTS=1 in git_env; fail closed on shallow/alternates/grafts.
3. [MED] Selftest blind spot. It sets only GIT_DIR. A strip-only-GIT_DIR mutant passes selftest (S-B1) while the CLI with GIT_ALTERNATE_OBJECT_DIRECTORIES is redirected (S-B2 rc 0 clean). Dropping the global pin still gives selftest rc 0 with 30 fsmonitor + 10 pre-commit executions (S-C2).
4. [LOW] Discovery. --lane-repo/--fleet-repo are not checked to be a repository top level, so a non-repo dir inside the fleet is audited as the fleet (E1: real lane commits become landed-unresolved). GIT_CEILING_DIRECTORIES is stripped, so the operator's ceiling is ignored (E2); plain git honors it (E3 rc 128). Fix: assert `--show-toplevel` equals the path.
5. [LOW, contract] A raw commit with an invalid-UTF-8 subject gives an uncaught UnicodeDecodeError: rc 1, the "failed" verdict, where the contract says could-not-evaluate (U1, stdout empty). Fix: catch UnicodeDecodeError in git().
6. [LOW, fail-closed] XDG git/ignore and git/attributes sit outside GIT_CONFIG_GLOBAL (git-config(1): core.excludesFile defaults to $XDG_CONFIG_HOME/git/ignore; attributes likewise): selftest rc 2 (C3b, C5b); audit unaffected (C3a, C5a). Repo-local i18n.logOutputEncoding: rc 2 (F8).
7. [INFERENCE, untested] git < 2.32 ignores GIT_CONFIG_GLOBAL (introduced in 2.32.0, https://git-scm.com/docs/git/2.32.0); the tool has no git-version check. Not tested: PATH-resolved git binary, commit-graph forgery, non-UTF-8 locales.

## Candidate fix: out/C1EnvSentinel/remediation.patch (58 lines; scratch copy only, lane untouched)
- `git -C <scratch lane> apply --check remediation.patch` at a6617149: exit 0. Candidate `--selftest`: cases=32 failed=0, exit 0.
- Candidate repro (results-candidate.txt, exit 0): F1b/F9 NOT-EXEC; F3a rc 1 (omitted c2 detected); F4/F5/F5b rc 2 fail-closed; U1 rc 2; C3b/C5b ISOLATED; F8 equals baseline; E1/E2 rc 2; A/B/C/D unchanged. S-C2 leaks 0 because XDG/HOME are pinned too.
- Real lane and fleet: .git/shallow, objects/info/alternates and info/grafts all absent (test -e, 6/6), so the new guard does not fire today. Their .git/config (read only) carries no showSignature, gpg, fsmonitor, hooksPath or i18n keys.
- Not fixed by the patch: selftest coverage (item 3). Fix: add GIT_* decoys and a no-marker assertion to selftest.

## Hygiene
- Installs/updates: none. git 2.56.0 and Python 3.14.8 are pre-existing. `sudo -n chown` was used only on the throwaway root-owned fixture and restored (0 root-owned entries left).
- Real lane/fleet: read .git/config and ran `test -e` only, except ONE mistake: I ran `git -C <lane> status --porcelain -- .ufo/waves/round-21/falsify` (read-only intent) at ~08:36. Git status can refresh the lane index stat cache; `.git/index` mtime is now 08:36:22 (size 746864). My earlier directory listing showed it at 356.1KB, about 5 min before that rewrite. Whether my call rewrote it or concurrent peer writes did is [INFERENCE], unverified. I changed no commit, ref, tree or tracked file. Lane owner: check `git -C <lane> status` / index integrity before relying on it.
- Scratch /tmp/kama-r21-C1EnvSentinel removed after writing; repro.py needs --tool.
