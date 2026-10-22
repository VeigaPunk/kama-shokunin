# ReviewerC1Patch evidence: C1 patch 1fc41e346853afd98cbd7010af5db4e54dc877f7

Environment: git 2.56.0; /usr/bin/python3 Python 3.14.8. Scratch (heavy, not in the lane):
`/fast/scratch/hyaku/kama-r25a2/ReviewerC1Patch/` holds `clone` (detached at 1fc41e34), `r23`
(a git worktree of e876b95 created inside my clone), and `gitprobe` (a two-commit probe repo).
No llama-server was started and no port was opened. No tool was installed or updated. No jj
command was run. Lane git was read-only (show, log, rev-parse, cat-file only).

## 1. Lane reads (read-only)
- `git -C <lane> show --numstat --format= 1fc41e34` → `30	3	tests/report-audit/isolation-mutants.py`, exit 0
- `git -C <lane> show --format= --name-status 1fc41e34` → `M	tests/report-audit/isolation-mutants.py`, exit 0
- `git -C <lane> rev-parse master 1fc41e34` → both `1fc41e346853afd98cbd7010af5db4e54dc877f7`, exit 0
- `git -C <lane> log -4` → 1fc41e34 (C1), 5388b7cf (amendment 2), efe58e96 (preregistration), 147f5bdd (base), exit 0

## 2. Clone checks (scratch clone at 1fc41e34)
- `git show --check 1fc41e34` → no output, exit 0
- `git diff --quiet 147f5bdd 1fc41e34 -- tools/report-landing-audit.py` → exit 0 (auditor identical base→tip)
- `git diff --quiet 5388b7cf 1fc41e34 -- tools/report-landing-audit.py` → exit 0 (identical parent→tip)
- `git diff --quiet 5388b7cf 1fc41e34 -- tests/report-audit/isolation-mutants.py` → exit 1 (the patch)
- Added lines (30): tabs 0, CR 0, non-ASCII 0, trailing whitespace 0. File mode `index a16e7e9..a49871e 100755` (unchanged). File ends with a newline.

## 3. Registered counting command (C1 measure), cwd = clone at 1fc41e34
Command: `python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"`
Output: `registered 28 stale 0 []`, exit 0.
Before, reproduced: the parent registry (5388b7cf, 27 entries) against the same auditor gives stale `['M11-listing-surrogates', 'M17-ref-shadow']` (literal-id-checks.out line 5).

## 4. Literal, id and site checks (`literal-id-checks.py` → `literal-id-checks.out`, exit 0)
Line numbers below refer to literal-id-checks.out.
- Lines 1-5: 28 entries, unique, sorted; added `M33-ref-shadow-bare-objects`; removed none; changed tuples `M11`, `M17` only; RETIRED ids `M14, M22, M27, M29` unchanged; numbers absent from MUTANTS and RETIRED: `[8]`.
- Lines 6-33: every anchor occurs exactly once at tip; every mutated auditor parses (28 of 28).
- Lines 34-36: anchors as repr. M11 has `\n` followed by 29 spaces; M17 and M33 have `\n` followed by 16 spaces.
- Lines 37-45: tip lines 681-683 (M11 site, parse_rounds), 212-214 (M33 site, bare_objects), 275-277 (M17 site, lookup).
- Lines 46-49: `names a ref` only at tip lines 214 (bare_objects) and 277 (lookup); `startswith(token)` also at 787 (unknown_citation, not a refusal); `bare_objects(` called only at 246 inside lookup; lookup callers at 538 (audit_round), 550 and 630 (peel `^{commit}`), 1170-1174 (selftest).
- Lines 50-52: round 23 (e876b95): guard at lines 170-172 in lookup; M11 call at line 430 in parse_rounds; recursive no-peel bare lookup at line 148-149.
- Lines 53-59: mutant id lists at e0f0434, 34b2376, e876b95, ed1cc3a, 92063cf, base, tip. M08 is absent in every version.

## 5. Git history (read-only)
- `git log --format='%h %s' -S'bare = lookup(repos, tokens)' -- tools/report-landing-audit.py` → `ed1cc3a` (removed), `7054dba` (added), exit 0.
- `git log -S'if not parts[0].startswith(token)' -- tools/report-landing-audit.py` → `92063cf` only, exit 0.
- `git log -S'if not peel and not parts[0].startswith(token)' -- tools/report-landing-audit.py` → `e0f0434` only, exit 0.
- `git log -- tests/report-audit/isolation-mutants.py` → 1fc41e3, 92063cf, ed1cc3a, e876b95, 34b2376, e0f0434, exit 0.

## 6. Targeted grid runs (`isolation-mutants.py`, which runs the grid with `--arm current`)
- Tip (cwd clone), `--only M11-listing-surrogates --only M17-ref-shadow --only M33-ref-shadow-bare-objects --json`, exit 0, wall 131.7 s. Output: `changed-mutants.json`, `changed-mutants.stderr` (empty).
  - pristine passed
  - M11: grid exit 1, failed row F20-quotepath-open-range (killed)
  - M17: grid exit 0, no failed rows (survived)
  - M33: grid exit 1, failed row F13-ref-named-abbreviation (killed)
  - summary: mutants 3, killed 2, surviving `['M17-ref-shadow']`
- Round 23 (cwd `r23` worktree at e876b95), `--only M11-listing-surrogates --only M17-ref-shadow --json`, exit 0, wall 98.4 s. Output: `r23-changed-mutants.json`, `r23-changed-mutants.stderr` (empty).
  - pristine passed
  - M11: grid exit 1, failed row F20-quotepath-open-range (killed)
  - M17: grid exit 1, failed row F13-ref-named-abbreviation (killed)

## 7. Reachability of the M17 and M33 elements
- git 2.56.0 on the probe repo (A = HEAD~1 = ae164c9b...; B = HEAD = fe1a81a8...; a branch named A points at B; a branch named A[:7] points at B):
  - `printf '%s\n' A | git cat-file --batch-check` → `ae164c9b... commit 116`, exit 0 (the token's own object, not B)
  - `printf '%s\n' A[:7] | git cat-file --batch-check` → `fe1a81a8... commit 164`, exit 0 (the same-named ref wins)
- `m17-reachability-probe.py` → `m17-reachability-probe.out`, exit 0:
  - TIP full 40-hex, no peel → found (the production shape at audit_round, line 538)
  - TIP ref-named short, no peel → EvalError "names a ref" (guard live when such a token is passed directly)
  - TIP ref-named short, peel `^{commit}` → EvalError "names a ref" (production shape)
  - M17-mutated ref-named short, no peel → found
  - M33-mutated ref-named short, peel → found
- FULL tokens come from `classify_full_hashes` (tools/report-landing-audit.py lines 463-479); the FULL regex is at line 90 (40 lowercase hex). The grep over tools/ and tests/ found no other caller of the auditor's lookup (promisor-mutants.py has its own stub `lookup` at line 1271).

## 8. Full registry run (all 28, cwd clone at 1fc41e34)
Command: `python3 tests/report-audit/isolation-mutants.py --json` → `full-mutants.json`, `full-mutants.stderr`.
Status at the time of writing: running as background job bg_2008. The exit code and survivor list are recorded in the report once the job reports.

## 9. Lane file operations (mine only)
- Created under the lane: `.ufo/waves/round-25/a2-build/advice/` (the report), `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/` (this folder and its files).
- Mis-write, disclosed: two files (`literal-id-checks.py`, `m17-reachability-probe.py`) were first written with a relative path, which resolved against the fleet root. They were copied byte-identical into the lane folder (`cmp` checked), then removed from the fleet root, together with the directories `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/`, `.../a2-build/out/` and `.../a2-build/`, which that write had created (06:45). Nothing else in the fleet root was touched; `.ufo/waves/round-25/build/` is untouched.
