# M2Ctr — C2 counter mutation test (round 46, w1, lane kama)

**Verdict: 32 single-site mutants of the frozen C2 counter (`tools/round46-append-audit-check.py` @ lane `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, sha256 `4dcfbe10…ff3cb0a`) run against 3 scenarios: 20 killed, 12 survived, 0 equivalent — and the headline finding is a baseline failure: the pristine counter itself accepts a broken tool (CLI-default threshold 20→21) with `met=True` exit 0.**

## 1. Scenarios (fixtures under scratch, ids recorded in `M2Ctr/fixtures.txt`)

| scenario | repo tip | content | ground truth |
|---|---|---|---|
| a | `df79a8d14c9c…` | lane @ `4a2a4d55` + SCORECARD row `\| append-only-audit \| capability acquisition (C2 round 46) \| selftest=1 fixture=1 lane=1 table=1 \| tools/round46-append-audit-check.py \| 46 \|` committed (identity `m2ctr-fixture`) | counter must pass (met, exit 0) |
| b1 | `0ded8cc76bfa…` | a + tool **CLI argparse default** `--threshold default=20 → 21`, committed | counter must fail |
| b2 | `bd3ca42386fd…` | a + tool `audit()` **function default** `threshold=20 → 21`, committed | counter must fail |

Toplevel asserts passed before every fixture commit; `git status` clean after. Pristine baseline (exit code / met): a = 0/True, b1 = 0/**True**, b2 = 1/False. Lane events recomputed at these tips (all three): `dd9f5dc6 SCORECARD deleted=31 restored 24 partial; 0718b6ab SCORECARD deleted=2417 restored 2416 partial; 0718b6ab LOG 2290/2290, QUALITY 375/375, README 663/663 restored by 82b5e9d3` — matches the C2 event list (5 events, 2 partial).

## 2. Headline finding (F1): pristine counter misses the b1 broken tool

`python3 counter --repo fixb --tip HEAD` → exit 0, `selftest=1 fixture=1 lane=1 table=1 … met=True` (`M2Ctr/baseline_b1.txt`). Mechanism, all three legs blind:

- **lane leg**: tool(21) vs recompute(20) differ only on a `(commit,file)` diff deleting **exactly 20** lines; the lane has none (event sizes 31, 2417, 2290, 375, 663).
- **selftest leg**: the tool's selftest calls `audit(f.d, t)` and therefore exercises the **function default** (20), not the CLI default the counter actually invokes (`tools/append-only-audit.py:280 etc.` vs `:299`), so it stays green.
- **fixture leg**: counter fixture events are 30 and 25 deletions, far above the boundary.

So C2's "working capability" claim does not pin the tool's CLI threshold contract. b2 *is* caught (selftest case `t_exact_unrestored` pins a 20-line event → `pass=9 fail=1`, rc 1 → `selftest=0`). **Proposed fix (counter is frozen — proposal only, for L1):** add a fixture event with deleted exactly == THRESHOLD (e.g. a 20-line deletion, unrestored) to `build_fixture`/`exp_full`; then any default drift (CLI or function) breaks the fixture leg. One changed constant + one expectation tuple.

## 3. Mutants and verdicts (killed = verdict triple (a,b1,b2) differs from pristine's rc triple (0,0,1); survivors = coverage findings)

| mutant | site (all 1-occurrence replacements, asserted) | rc (a,b1,b2) | verdict |
|---|---|---|---|
| M01_thr19 | recompute THRESHOLD 20→19 | 0,0,1 | SURVIVED |
| M02_thr21 | recompute THRESHOLD 20→21 | 0,0,1 | SURVIVED |
| M03_thr25 | recompute THRESHOLD 20→25 | 0,0,1 | SURVIVED |
| M04_thr_boundary_le | `len(dele) < THRESHOLD` → `<=` | 0,0,1 | SURVIVED |
| M05_diff_order_swap | diff `p, c` → `c, p` | 1,1,1 | KILLED (a,b1) |
| M06_diff_empty_tree | parent → empty-tree hash | 1,1,1 | KILLED (a,b1) |
| M07_revlist_no_topo | drop `--topo-order` | 0,0,1 | SURVIVED |
| M08_rat_plus1 | restored_at_tip `k+1` | 1,1,1 | KILLED (a,b1) |
| M09_rat_distinct | `k` distinct-line count | 1,1,1 | KILLED (a,b1) |
| M10_status_never_unrest | `k == 0` → `k < 0` | 0,0,1 | SURVIVED |
| M11_partial_renamed | "partial" → "part" | 1,1,1 | KILLED (a,b1) |
| M12_status_tol_one | restored if `k >= len-1` | 1,1,1 | KILLED (a,b1) |
| M13_rb_include_self | restored_by scan from `i` | 0,0,1 | SURVIVED (≈equiv, §4) |
| M14_rb_any | restored_by `all` → `any` | 1,1,1 | KILLED (a,b1) |
| M15_rb_no_break | drop `break` (last restorer) | 1,1,1 | KILLED (a,b1) |
| M16_rb_skip_one | scan from `i+2` | 1,1,1 | KILLED (a,b1) |
| M17_fx_B_rat_1 | fixture exp B restored 0→1 | 1,1,1 | KILLED (a,b1) |
| M18_fx_mid_rc1 | fixture `rc2 == 0` → `== 1` | 1,1,1 | KILLED (a,b1) |
| M19_fx_drop_B | drop expected event B | 1,1,1 | KILLED (a,b1) |
| M20_fx_del29 | fixture event A 30→29 deleted | 1,1,1 | KILLED (a,b1) |
| M21_lane_rc_zero | lane `rc3 == (1 if bad…)` → `== 0` | 1,1,1 | KILLED (a,b1) |
| M22_lane_rc_any | → `rc3 in (0,1)` | 0,0,1 | SURVIVED |
| M23_bad_false | `bad = any(…)` → `False` | 1,1,1 | KILLED (a,b1) |
| M24_table_cell45 | last cell "46" → "45" | 1,1,1 | KILLED (a,b1) |
| M25_table_drop_cell | drop last-cell check | 0,0,1 | SURVIVED |
| M26_table_name_x | name → "append-only-audit-x" | 1,1,1 | KILLED (a,b1) |
| M27_selftest_floor60 | pass floor 6 → 60 | 1,1,1 | KILLED (a,b1) |
| M28_selftest_floor1 | pass floor 6 → 1 | 0,0,1 | SURVIVED |
| M29_selftest_tol1 | `fail == 0` → `<= 1` | 0,0,1 | SURVIVED |
| M30_met_lane_table | `met = lane and table` | 0,0,**0** | KILLED (b2) |
| M31_met_any | `met = any(legs)` | 0,0,**0** | KILLED (b2) |
| M32_fx_ok1_drop_rc | drop `rc1 == 1` from ok1 | 0,0,1 | SURVIVED |

Note: M30/M31 print `met=1`/`met=True` and exit 0 on b2 — they mask the one break the counter *does* catch; only the met-composition mutants are killed via b2, i.e. **b2's rejection rests entirely on the selftest leg**.

## 4. Survivors = what the two scenarios cannot see (coverage findings, not license to change the contract)

- **M01–M04 (threshold family)**: no scenario input contains a `(commit,file)` deletion in [19,25] — lane sizes {31,…,2417} and fixture {30,25,5,40-undeclared} all sit away from the 20 boundary. Same blindness that causes F1.
- **M07**: lane has 2 merges; topo vs date order changes no event/restored_by here. Fixture is linear.
- **M10**: no lane event is unrestored (`lane_unrestored=0`), and fixture expectations are constants — recompute's unrestored label never flows into a comparison.
- **M13**: scan from `i` includes the event commit itself; deleted lines are absent from the event commit's post-image, so the extra candidate never matches on these inputs. Argued equivalent-on-inputs; not provably equivalent for all inputs (deleted line texts could recur elsewhere in the same file), so recorded as survived.
- **M22, M32 (exit-code agreement legs)**: in every scenario the tool's event sets and exit codes co-vary, so `rc3`/`rc1` checks are never the deciding leg. A tool that reports right events with a wrong exit code would pass. Redundancy with F1's fix: an exactly-20 fixture event would also re-arm these.
- **M25**: table leg only ever sees a correct row ending `| 46 |`; a row naming the tool with a wrong round cell would pass.
- **M28/M29 (selftest floor)**: selftest always passes 10/10 in scenarios (floor never binding; floor 60 kills), and the `fail == 0` check is redundant given `rc == 0` plus the tool's exit contract — b2 keeps failing via rc even with `fail <= 1`.

## 5. Evidence, commands, restoration

- Pristine: `python3 …/counter/pristine.py --repo <fix> --tip HEAD --scratch <work>` → a: rc 0; b1: rc 0 (finding F1); b2: rc 1, `detail: selftest rc=1 line=AOA_SELFTEST pass=9 fail=1`.
- Mutants: 96 runs (32 × 3), each mutant built from pristine bytes with exactly one asserted-count-1 replacement; receipts per mutant/scenario in `M2Ctr/mutants/<name>_{a,b1,b2}.txt`. Exit codes are the verdict signal; `results.json` holds triples.
- Restoration control: pristine sha256 before/after `4dcfbe1063d600d103ebbccf1ac3008771a6962ae0dac9b91980b1e93ff3cb0a` (unchanged; mutants were separate files); pristine re-run on a/b1/b2 after all mutants — outputs byte-identical to baseline, rc 0/0/1.
- Lane untouched (read-only git only: `clone --shared`, `show`, `rev-parse`, `merge-base`); all writes confined to scratch + `M2Ctr/` out dir. Tooling: none installed (python3 + system git only); no pacman.

## 6. Deliverables

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/M2Ctr.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/M2Ctr/results.json` (baseline + 32 verdict triples)
- `…/M2Ctr/baseline_a.txt`, `…/M2Ctr/baseline_b1.txt`, `…/M2Ctr/baseline_b2.txt`
- `…/M2Ctr/mutants/` (96 receipts), `…/M2Ctr/runner.py` (repro), `…/M2Ctr/fixtures.txt`
