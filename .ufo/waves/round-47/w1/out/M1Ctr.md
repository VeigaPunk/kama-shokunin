# M1Ctr — C1 counter mutation test (round 47, lane kama)

Verdict: **29/44 mutants killed, 13 survived, 2 equivalent** on the two targets (lane at
`3a09a1d93dcc16799cf6c4b48786e6440af134c4` and the v1 control at `172b8ad040d51ce8c011238c1408d4e0b6aa9595`
with the contract from the lane tip added). All 13 survivors are **findings**: each preserves real
behavior (documented below with a proposed killing case); both equivalent mutants are loop/format
no-ops. No counter source was changed; edits are in scratch only. No tools installed (python3/git
only; pacman untouched; `time` binary absent — runs timed with `date`).

## Targets and baselines

- Frozen counter: `tools/round47-append-audit-v2-check.py`, sha256
  `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed` (matches preregistration) — copied
  to scratch unchanged, then mutated.
- Lane target: `git clone --shared <lane> $S/lane`, run
  `python3 <mutant> --repo $S/lane --tip 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --scratch $S/run-*`.
  Pristine (3/3 runs identical): exit 0,
  `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`
  (matches the L1 pre-wave dry run).
- v1 control: `git clone --shared <lane> $S/control`; checkout `172b8ad…`; add (one commit, fixture
  identity `fixture@kama.invalid`, `GIT_CONFIG_GLOBAL=/dev/null`) the tip's real contract
  `registry/append-only-contract.tsv` from `3a09a1d…`; control tip `2dbd1cd121bf5f2ced25164281a119583fe1506d`.
  Pristine (3/3 runs identical): exit 1,
  `selftest=1 contract=0 lane=0 fixture=0 stable=0 files=85 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False`
  (v1 tool at tip exits 2 for `--json --contract`, so lane/stable/fixture legs fail; same shape as the
  `junk-c1-v1-contract` control, with the real tip contract instead of the synthetic one).
- Verdict rule: a mutant is **killed** if any of 3 runs on either target differs from pristine in
  stdout or exit code; **equivalent** if the edit cannot change behavior on any input; otherwise
  **survived**. Runs use separate scratch dirs; fixture randomness is intrinsic (os.urandom seed).

## Mutants

44 single-point mutants across the seeded categories (threshold, hunk-header parse, numstat parse,
K = parent − D, held formula, window start, restored_best/restored_by, status classes, contract
header/rule/declared_at, REQUIRED, lessons, files equality, stable direction, round47 guard, fixture
construction; plus expected-exit and lane-compare sensitivity). Each edit applied with an exact
single-occurrence string match; `python3 -m py_compile` clean for all 44. Patches:
`out/patches/<mutant>.patch`.

## Results

| mutant | category | mutation | lane | control | verdict |
|---|---|---|---|---|---|
| m01_threshold19 | threshold | THRESHOLD 20→19 | ✗ | ✗ | killed |
| m02_threshold21 | threshold | THRESHOLD 20→21 | = | ✗ | killed (flaky, fixture draw) |
| m03_thresh_le | threshold | `ns[f] < threshold` → `<=` | = | = | **killed (flaky)** — 4/11 lane runs |
| m04_thresh_off | threshold | `ns[f] < threshold-1` | ✗ | ✗ | killed |
| m05_hunk_start_count | hunk parse | `nd` := start line | ✗ | ✗ | killed |
| m06_hunk_no_cap | hunk parse | drop `got_d < nd` cap | = | = | equivalent |
| m07_hunk_regex_break | hunk parse | regex stops matching counted hunks | ✗ | ✗ | killed |
| m08_numstat_split | numstat parse | `split('\t')` → `split()` | = | = | **survived** |
| m09_numstat_addition | numstat parse | deleted := additions column | ✗ | ✗ | killed |
| m10_numstat_plus1 | numstat parse | deleted +1 | ✗ | ✗ | killed |
| m11_K_kept | K = parent − D | K := parent lines | ✗ | ✗ | killed |
| m12_held_noneg | held formula | drop `max(0, …)` | = | = | **survived** |
| m13_held_nocap | held formula | drop `min(n, …)` | ✗ | = | killed |
| m14_win_after | window start | window starts after event commit | ✗ | ✗ | killed |
| m15_win_all | window start | window := all commits | ✗ | ✗ | killed |
| m16_tie_last | restored_best/by | `h > best` → `>=` | ✗ | ✗ | killed |
| m17_by_early | restored_best/by | `by` set at `h >= deleted-1` | ✗ | = | killed |
| m18_nobreak | restored_best/by | remove full-restore `break` | = | = | equivalent |
| m19_status_swap | status classes | restored/unrestored swapped | ✗ | ✗ | killed |
| m20_status_nopartial | status classes | drop partial class | ✗ | ✗ | killed |
| m21_rules_missing | contract checks | RULES drops A-corr | ✗ | ✗ | killed |
| m22_header_unchecked | contract checks | header check removed | = | = | **survived** |
| m23_decl_prefix_match | contract checks | `fullmatch` → `match` | = | = | **survived** |
| m24_append_case | contract checks | 'append' check case-sensitive | ✗ | ✗ | killed |
| m25_required_extra | REQUIRED | + phantom lessons file | ✗ | ✗ | killed |
| m26_required_drop | REQUIRED | − SOURCES | = | = | **survived** |
| m27_lessons_unchecked | lessons | lessons check removed | = | = | **survived** |
| m28_lessons_all | lessons | `any` → `all` | ✗ | ✗ | killed |
| m29_patterns_exact | files equality | fnmatchcase → `==` | ✗ | ✗ | killed |
| m30_keys_nostatus | files equality | KEYS drops status | = | = | **survived** |
| m31_stable_flip | stable | `t < e` → `t > e` | = | = | **survived** |
| m32_stable_deleted_flip | stable | `t.deleted != e` → `<` | = | = | **survived** |
| m33_stable_wrong_empty | stable | checks tip instead of base | = | = | **survived** |
| m34_round47_guard | round47 guard | looks for `roundXX` | = | = | **survived** |
| m35_exit_any_restored | expected exit | any restored → 1 | = | = | **survived** |
| m36_exit_any_unrestored | expected exit | any unrestored → 1 | ✗ | = | killed |
| m37_lane_mismatch_ignored | lane compare | event mismatch ignored | = | = | **survived** |
| m38_fx_move21to19 | fixture | block 21→19 | ✗ | ✗ | killed |
| m39_fx_cut19to20 | fixture | cut 19→20 | ✗ | ✗ | killed |
| m40_fx_k2_range | fixture | E2 20-26→10-19 | ✗ | ✗ | killed |
| m41_fx_k1_range | fixture | E1 22-30→15-19 | ✗ | ✗ | killed (crash) |
| m42_fx_e1_status | fixture | E1 expected partial→restored | ✗ | ✗ | killed |
| m43_fx_e3_status | fixture | E3 expected restored→partial | ✗ | ✗ | killed |
| m44_fx_e2_status | fixture | E2 expected unrestored→restored | ✗ | ✗ | killed |

`✗` = stdout or exit differs from pristine in ≥1 of 3 runs; `=` = identical in all 3. Full per-run
table: `out/mutant-verdicts.tsv`; run-level kill flags: `out/summary-killed.tsv`; representative
outputs: `out/evidence/`; patches: `out/patches/`.

## Killed — kill evidence (representative)

- Threshold/fixture self-check (m01, m04, m11, m14, m15, m16, m19, m20, m38, m39, m40, m42, m43,
  m44): counter exits 2 `could-not-evaluate: fixture construction disagrees with the counter's
  recomputation` — the fixture self-check compares `recompute` against the constructed `exp`, so any
  drift in threshold, window, K or expected-status is caught the *fixture leg* (lane run).
- m41: uncaught `ValueError: empty range in randint(4, 3)` (k1=15..19 shrinks `d1_plain` below the
  `randint(4, len-4)` lower bound) — crash, exit 1.
- m05: `could-not-evaluate: hunk parse 24 != numstat 31 at dd9f5dc6c0e6 SCORECARD.md`.
- m07: `IndexError: no such group` (regex rewrite drops group 4).
- m09: `hunk parse 0 != numstat 93 at c6199a254244 LOG.md`; m10: `hunk parse 31 != numstat 32`.
- m13 (held without cap): lane mismatch 8 — e.g. restored_max 2296 vs 2292 (LOG.md), 2480 vs 2421
  (SCORECARD.md): dropping `min(n, …)` inflates held, restoring `partial`→`restored` etc.
- m17 (restored_by early): lane mismatch 2 — restored_by set to `82b5e9d3…` where pristine None:
  `0718b6ab` SCORECARD.md has 9 window commits with `h == deleted-1` (diag).
- m21: contract rows 2,3,4,5,7 rule `'A-corr' not in ['A','A-row']` → contract=0.
- m24: declared lines `corpus/README.md:86` ("Appended …") and `registry/history/DELTA.md:3`
  ("# Append-only …") lack lowercase `append` → contract=0 — case-sensitive check is a live landmine.
- m25: `contract expansion lacks corpus/lessons/r999.md`; m28: no lessons file; m29: `files=6`
  (wildcard `corpus/lessons/*.md` stops expanding).
- m36: `lane: exit 1 vs expected 0` (partial events no longer counted → exit expectation wrong).
- m02/m03 (flaky): the fixture's E3 deletion is `THRESHOLD + randint(0,4)`; when it draws exactly 20
  (prob 1/5 per run) the threshold mutants disagree with the construction → self-check fires. m03
  matched pristine in 3/3 first runs, then 4/8 extra lane runs exited 2 (`out/evidence/m03.extra-runs.txt`).
  m02 died on the control in 2/3 runs; lane 3/3 identical. Both are real, potentially non-deterministic
  kills — the counter's own fixture is the most sensitive detector.

## Equivalent mutants (no possible behavior change)

- m06: git unified diffs emit all `-` lines before `+` lines inside a hunk; collecting every `-` line
  without the `got_d < nd` cap yields exactly the same deleted multiset, and the loop still terminates
  on the `got_a < na` bound.
- m18: the `break` after full restore is a pure optimization — `by` is guarded by `by is None`, and no
  later commit can beat `best` once `h == len(dl)` (h is capped at len(dl)).

## Survived mutants — findings with proposed killing cases

1. **m08** (`split('\t')` → `split()` in numstat): a repo-relative file with a space in its name
   (git quotes/escapes but numstat prints `N\tM\tpath with space` → `split()` yields
   `parts[2]='path'`, misattributing deletions). Lane contract files and fixture files have no spaces.
2. **m12** (drop `max(0, …)` in held): negatives occur on the lane (dd9f5dc6 SCORECARD.md has total
   deficit 425 across window commits) but never reduce the window *maximum*, so all reported tuples
   are unchanged. Killing case: parent has line L twice; event deletes {a,b,c,d,e,L}; a later commit
   restores a–e but not L → raw held = 4 vs clamped 5 → restored_max differs (status can flip
   restored↔partial).
3. **m22** (header check removed): a contract whose first line is not exactly
   `path\trule\tdeclared_at\tnote` but whose rows resolve would pass every leg. Killing case: write a
   contract with a wrong header + otherwise valid rows; pristine contract=0, mutant contract=1.
4. **m23** (`fullmatch` → `match` on declared_at): `AGENTS.md:2junk` would be accepted as `path:line`.
   Killing case: such a row must be rejected; mutant accepts it.
5. **m26** (REQUIRED drops SOURCES): a contract expansion missing `corpus/SOURCES.md` passes.
   Killing case: strip the SOURCES row; mutant contract=1, pristine contract=0.
6. **m27** (lessons check removed): a contract covering no `corpus/lessons/*.md` passes. Killing case:
   a contract without a lessons row.
7. **m30** (KEYS drops `status`): the lane/fixture event comparison stops checking status.
   Killing case: a tool that reports the right count fields but a wrong status (mutant lane=1,
   pristine lane=0).
8. **m31** (stable direction `t > e`): base and tip event sets are *equal* on this lane (both report
   identical deleted/restored_max — see evidence), so the flipped check never fires. Killing case: a
   repo where an event's restored_max strictly improves between base and tip (v2 explicitly must allow
   this; the flip would fail it).
9. **m32** (stable `t.deleted < e`): tip never lowers a deleted count here. Killing case: a tip that
   lowers a base event's deleted count (pristine fails stable; mutant passes).
10. **m33** (stable checks `res["tip"]` instead of `res["base"]`): both non-empty here. Killing case:
    a repo with an empty base window and non-empty tip (pristine fails "no event at base"; mutant
    passes).
11. **m34** (guard looks for `roundXX`): the lane tool contains neither string. Killing case: a tool
    embedding `round47` (the independence guard must flag it; mutant does not).
12. **m35** (expected exit: any restored → 1): every target exits 1 anyway (partial events exist), so
    the inverted expectation never disagrees with the tool. Killing case: a repo whose events are all
    restored (tool exits 0; pristine expects 0, mutant expects 1 → lane leg mismatch).
13. **m37** (lane event mismatch ignored): pristine has zero mismatch, so the removed check never fires.
    Killing case: a v2 tool reporting wrong events (valid JSON, agreeing exit) — mutant lane=1,
    pristine lane=0 (this is exactly the `junk-c1-v1-numstat` shape once the tool is v2-schema).

## Note on the v1 control

The control reproduces `junk-c1-v1-contract` (v1 tool + contract file): the counter correctly scores it
met=False. Control runs add little discriminating power for fixture-heavy mutants (its fixture leg fails
early on the v1 tool), which is why five fixture-construction mutants were killed via the lane target
alone.

## Evidence

- Commands (representative): as in "Targets" above; each mutant run recorded in
  `out/evidence/<mutant>.lane.out` / `.control.out` (and `m03.extra-runs.txt`).
- Pristine baselines: `out/pristine-lane.out`, `out/pristine-control.out`.
- Full verdict table: `out/mutant-verdicts.tsv`; run-level kill flags: `out/summary-killed.tsv`;
  patches: `out/patches/`.
- All scratch outputs under `/fast/scratch/hyaku/kama-r47/M1Ctr/` (removed before finish; copies above).
