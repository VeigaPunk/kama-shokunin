VERDICT: confirm - inherited GIT_DIR, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY or GIT_COMMON_DIR redirect selftest writes into the named repo; inherited git config runs hooks or breaks the selftest; no report-to-shell path
# AuditGitEnvSentinel (kama R21): tools/report-landing-audit.py at a29bb84 (sha256 a60acc3a…)

Method: throwaway lane clone (`git clone --no-hardlinks`), fresh victim repos, fixture fleet built from the real round-20 report (read-only). Harness: `out/AuditGitEnvSentinel/probe_env.py`; per-case JSON in `results-*.json`; table in `comparison.txt`; commands with exits in `commands.txt`.

## Answers
1. Does an inherited env make selftest commits write into lane/fleet? Yes, into whichever repo the env names (E = selftest case, A = audit case):
   - `GIT_DIR=<victim>/.git` (E1): rc1, 4 FAIL, 7 new commits (`kama-shokunin round-1: work|measure|late advice|kama report`, `checkpoint(r1): save`, `round-10: other round`, and a foreign-author commit); victim master moved; index changed; +24 loose objects.
   - `GIT_INDEX_FILE` absolute (E2): victim index rewritten; entry `f` points to blob 6e98d18, absent from the victim's object store; rc1.
   - `GIT_OBJECT_DIRECTORY` or `GIT_COMMON_DIR` (E3, E3b): rc0, yet +24 objects written into the named repo.
   - `GIT_WORK_TREE` alone or with `GIT_DIR` (E4, E1b): rc1 crash, no write. Relative `GIT_INDEX_FILE=.git/index` with cwd in the repo, the form git exports to hooks (E2b): rc0, no write.
   - `GIT_CONFIG_*` and outer `git -c` (E5-E8): no write, but config reaches temp repos. Global `core.hooksPath` runs a hook on every temp commit (marker=7, rc0). `init.templateDir` pre-commit: rc1. `commit.gpgsign` with failing gpg: rc1. Same via `GIT_CONFIG_COUNT`, `GIT_TEMPLATE_DIR`, and `git -c` (GIT_CONFIG_PARAMETERS).
   - [INFERENCE] Real lane: HEAD is detached at a29bb84 (`git branch --show-current` empty), so an inherited GIT_DIR there would add commits to HEAD and rewrite its index. Not run on the lane.
   - Who sets GIT_DIR: git 2.56 did not export GIT_DIR to hooks or aliases in my probe; it did export GIT_INDEX_FILE (relative) and GIT_CONFIG_PARAMETERS. Exposure therefore needs an outer tool or shell that sets GIT_DIR or passes `-c` [INFERENCE on which tools].
2. Do hooks or commit.gpgsign interfere today? No. `git config --global --get` for core.hooksPath, commit.gpgsign, gpg.program, init.templatedir, include.path, core.fsmonitor and user.signingkey: all rc1 (unset). `/usr/share/git-core/templates/hooks` holds only `*.sample`. Lane `.git/hooks` has no active hook (grep -v exit 1). The exposure is inherited env and any future global config.
3. Do report contents reach a shell? No. Grep for shell=True, os.system, os.popen, eval, exec and `sh -c` in the tool: 0 matches; every subprocess call is an argv list. Report-derived argv is only `[0-9a-f]{7,40}`. Payloads `$(touch …)`, `;` and backticks in a Landed bullet (A8) and in an errata correction (A6) created no file (PWN_files_created=[]). No tracked caller pipes output to a shell (grep of tools/, tests/, registry/, scripts/, AGENTS.md, SKILL.md, CORPUS.md, PROTOCOL.md).

## Findings
- F1 HIGH (integrity; latent, needs inherited GIT_DIR, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY or GIT_COMMON_DIR). Forged `kama-shokunin round-N:` commits could enter a closure evidence chain. Cause: `_commit()` uses `dict(os.environ)`, `_sh()` passes env=None, `git()` has no env.
- F2 MEDIUM: the audit itself is redirected by GIT_DIR (A1): required 0 and 12 defects, against required 9 and 5 defects clean (A0).
- F3 MEDIUM (robustness): inherited hooks, gpgsign or templates change or break the selftest (E5-E8). E5 executes hook code 7 times.
- F4 LOW: exit contract. Missing git gives a FileNotFoundError traceback and rc1 (meaning "failed") in the selftest (E10) and the audit (A4); the docstring says rc2. Selftest crashes (E4-E8) also exit 1. GIT_DEFAULT_HASH=sha256 gives 3 false FAILs (E9).
- F5 LOW: errata. Raw ESC bytes are printed in text mode (A5). The correction reaches `git cat-file` argv unvalidated: A6 `$(touch …)` did not run, but errata_invalid=1 while the defect still shows corrected=1. A `HEAD~1` correction clears a landed-omitted defect (A7).
- F6 LOW: ref shadowing. A branch named `deadbee1` hides `landed-unresolved deadbee1` (A2 7 defects, A3 6). `rev-parse --disambiguate` is object-only.
- F7 INFO (not fixed): prose words and numbers in `## Landed changes` are flagged (`defaced`, A2). `$(echo <40hex>)` counts as a citation (A8: omitted 33a6777 disappears, 5 defects down to 4).

## Minimal fix (validated in scratch; lane not modified)
- `out/AuditGitEnvSentinel/fix-A-env-isolation.patch` (`git apply --check` rc0). `git_env()` = os.environ minus every GIT_* key, plus GIT_CONFIG_GLOBAL=os.devnull and GIT_CONFIG_NOSYSTEM=1, used by git(), _sh() and _commit(). Selftest guard: after temp `init`, `rev-parse --absolute-git-dir` must equal `<temp>/.git`.
  Result: E1, E1b, E2, E2b, E3, E3b, E4, E5, E5b, E6, E6b, E7, E8 and E9 all rc0; victim unchanged; hook marker 0; A1 equals the clean run; real round 10-20 JSON byte-identical to orig (cmp rc0). E10 and A4 still rc1 with A alone.
- `out/AuditGitEnvSentinel/fix-AB-full.patch` (`git apply --check` rc0). Adds: OSError becomes could-not-evaluate (rc2), selftest exceptions become rc2, errata lines with control characters rc2, correction must be hex (else errata-invalid), object-only prefix lookup for ABBREV tokens.
  Result: E10, A4, A5 rc2; A7 errata-invalid; A3 flags deadbee1; real output byte-identical in JSON and text modes (cmp rc0).
- Still open (recommend, not applied): landed-omitted correction must equal token (all 8 ledger rows already do; selftest case "unmatched-errata-fails" must change); an invalid correction should not mark a defect corrected; prose tokens; add a selftest decoy case (GIT_DIR pointing at a decoy must leave it unchanged).

## Hygiene and tooling
- Lane: every probe ran on a `--no-hardlinks` clone; I wrote nothing into the lane. Disclosure: my first-batch `git status --short` ran with default optional locks and likely wrote `.git/index` at 07:47:52 (tested: default `git status` rewrites the index, `GIT_OPTIONAL_LOCKS=0` does not). The index later moved to 08:02:05; my later lane access was read-only (`GIT_OPTIONAL_LOCKS=0` rev-parse, ls-tree, stat), so that write is unattributed (live sibling seats share this lane). HEAD a29bb84 at end.
- Fleet: read-only (git log, cat-file, rev-parse; reads of round-10..20 reports).
- Installed: nothing. git 2.56.0 (/usr/bin/git), Python 3.14.8 (/usr/bin/python3). No processes left running; scratch `/tmp/kama-r21-AuditGitEnvSentinel` removed at end.
