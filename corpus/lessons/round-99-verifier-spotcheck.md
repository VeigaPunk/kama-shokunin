# Round 99 — non-author verifier spot-check (integrator, @m_zfl)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-08

Lane `kama`, round 99. Base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`; measured commit (amendment 1)
`00394f3ba7662a01d24ddec4b699ca8e1a793fd5`; lane tip before this file's commit
`a60e57cd168cc4b62e8cc02099598cb8955e30fd`. Report: `.ufo/reports/round-99/kama.md` (fleet repo).
I authored none of the round's files. The lane counters were not executed (Gate standard: the
integrator verifies committed evidence, it does not run a sibling's gate); everything below was
re-derived from committed bytes with plain git/grep/python-json reads, plus `curl` re-opens of the
sampled upstream sources.

Driver digest (`.ufo/watchdog.log`, copied): `2026-11-08T11:43:19-03:00 launch kama round=99
pgid=4143118 driver=hyaku-inline attempt=1`; `2026-11-08T13:39:49-03:00 complete kama round=99;
hyaku-inline attempt=1`.

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-99/kama.md` (fleet) | `kama-shokunin 3f2c51ae…`, `kama-shokunin 0e0e27f4…` (13:38/13:39 -03:00, before the 13:39:49 completion line) | pass |
| `SHONEN` heading, one line per box | read report §SHONEN | 4 lines, all `[~]`, each names its evidence and "author-asserted"/"independent review open" | pass |
| Cited commits are ancestors of `master` | `git merge-base --is-ancestor <h> master` for 439fdb3d f6e7ccc2 00394f3b 71838fdd 9ee0c3c4 3ed7a8df a60e57cd | all `ok` | pass |
| Lane pushed, clean | `scripts/hyaku/jj-lane.sh state …` ; `git status --porcelain` | `branch=master local=remote=a60e57cd… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty | pass |
| Prompt carries template contract | `.ufo/prompts/kama-round-99.md` headings | §1 MISSION/AXES, §2 Claims, §2b Frontier, §3 L2 floor, §4 Report contract, §5 Commit/push, §6 hyaku addendum, §7 scratch, §8 pre-file ledger (998 lines) | pass |
| Prefile ledger | `python3 scripts/hyaku/prefile-falsification.py --lane kama --round 99` | `PREFILE-FALSIFICATION: pass claims=3 rows=9 attack_seats=6 findings=0`, exit 0 | pass |
| Census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | `kama ok …/corpus/SOURCES.md`, exit 0 (W04 duplicate-URL and one W01 warnings only, incl. S624/S625/S627 duplicate-url-across-scopes) | pass |

Ledger adjudication: 9 rows, each `falsifies-wording` → `plans/round-99-amendment-1.md`; every
row's narrowing is visible in the measured instruments (C1 id sets + `population_shaped` + grader
negative arm; C2 twelve hardened propositions + `--rev` replay; C3 eight cells + exit grading +
`set -e` call shape). No spurious or unreconciled row.

## Per-claim re-check

Measured commit `00394f3b`; `git diff --stat 00394f3b a60e57cd -- tools/` is empty, so the measured
instruments and probe are the tip's.

**C1 operability — control refuses a population it did not run.** Evidence-verified + re-measured.
- Re-measured: `git show 439fdb3d:tools/round98-router-budget.py | grep -c -E 'selected_ids|population_ok'` → `0`;
  `git show a60e57cd:tools/round99-router-budget.py` line 680 `population_ok = int(bool(want_ids) and set(want_ids) == set(natural))`,
  line 695 `ok = int(ok and population_ok)` — id-set (not count) comparison and a non-empty selection guard are present.
- Receipts: `measured/c1.out` `CONTROL_POP99 … selected=6 ran=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_exit=0 positive_ok=1 complete=1 mutant_cell_lines=5 positive_cell_lines=6 population_shaped=1 met=True rev=00394f3b…`, `exit=0`;
  `controls/c1-before.out` `ROUTER_BUDGET98_CONTROL cells=5 … ok=1`, `exit=0`; `controls/c1-candidate-mutant.out`
  `selected=6 ran=5 … population_ok=0 … ok=0`, `exit=1`; `controls/c1-positive.out` `ran=6 population_ok=1 ok=1`, `exit=0`;
  `controls/c1-grader-base.out` `refused=0 … population_shaped=0 met=False`, `exit=1`. All match the report and `claims.json`.
- Verdict: verified. Axis **operability: improved** (score 8 → 8; the improvement is the instrument, not a score move).

**C2 calibration — round-98 records agree with committed wave evidence.** Evidence-verified + re-measured.
- Re-measured from committed bytes: `.ufo/waves/round-98/w1-results.json` → `seats=12`, 12 results, all non-empty;
  `.ufo/waves/round-98/w1-spec.json` roles → reviewer×2, critic×2, mutation-tester, sentinel, revenger (= 7 attack:
  RV01SelfAssess, RV02BudgetCells, CR01Boundary, CR02Wording, MT01Forgeries, SN01StepFlips, RV03Intent) and scout×2,
  executor×2, connector (= 5 non-attack) — matches the correction blocks; `.ufo/waves/round-98/measured/pre-report-gate.out`
  → `PRE_REPORT round=98 arms=14 failed=6`, FAIL arms selfdesc, newest-closure, round-scope, round-clean,
  round75-instruments, round78-instruments — matches. Correction blocks exist at `SCORECARD.md:6464` and `LOG.md:4047`.
- Pointers: `grep -n '10 reported, 2 dead'` → `SCORECARD.md:6431` and `LOG.md:4040` at 439fdb3d, f6e7ccc2 and 00394f3b (pointer
  correct at the measured commit); at the tip a60e57cd the SCORECARD sentence is at **6446** (15 lines of `### Planned (round 100)`
  inserted at line 65 by 71838fdd), so `SCORECARD.md:6431` is stale at tip. `LOG.md:4040` still holds.
- Receipts: `measured/c2.out` `RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=00394f3b…`, exit 0; `controls/c2-base.out`
  `mismatches=10 met=False`, exit 1; `controls/c2-forge-matrix.out` 15 variants, 14 `rc=1`, `J-arms-negation rc=0` (disclosed);
  `controls/c2-forged-rev.out` `mismatches=3 … forged_exit=1`.
- Verdict: verified at the measured commit (the claim's scope). Axis **calibration: improved** (7 → 7), with the tip pointer
  drift routed below.

**C3 depth — unread `/props` autoload flag reads `router-autoload-unread`.** Evidence-verified + re-measured.
- Re-measured: `grep -c router-autoload-unread tools/kama-probe.sh` → 0 at 439fdb3d, 3 at a60e57cd; `router_autoload` call kept
  inside a condition at line 955 (`if router_autoload "$port"; then ra=0; else ra=$?; fi`); `SKILL.md` line 1773 decision row and
  §Round 99 (line 1811) present; `SKILL.md` sha256 `f48f5c8e…`, 2511 lines, 60 `## ` headings — matches the SCORECARD depth cell.
- Receipts: `measured/c3.out` `cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True`, exit 0 (P1 explicit-off stays
  `router-unloaded`; U5–U7 read `router-autoload-unread` exit 2); `controls/c3-base.out` `mismatches=7 met=False`, exit 1;
  `controls/c3-harness.out` `tests=77 passes=77 failures=0`; `controls/c3-plaincall.out` all `ok=1`; `controls/c3-regression.out`
  `cells=19 mismatches=0 positive_mismatches=0 load_stable=1 … burners=0`, exit 0.
- Verdict: verified. Axis **depth: improved** (7 → 7).

No exploratory claim this round. `SCORECARD.md` diff 439fdb3d→a60e57cd: axis scores unchanged (operability 8, freshness 8,
depth 7, coverage 9, calibration 7, adjacency 7); only evidence cells, banner, `### Planned (round 100)` and capability rows
(`control-population-identity`, `record-evidence-audit`, `autoload-state-vocabulary`) change. No axis harmed.

## Per-axis verdicts

| Axis | Verdict |
|---|---|
| operability | improved |
| calibration | improved |
| depth | improved |
| coverage | unchanged |
| freshness | unchanged |
| adjacency | unchanged |

## Discernment spot-check (`corpus/lessons/round-99.md` §Gate)

Re-opened 2026-11-08 with `curl -sL` against `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`.

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S624 `tools/server/server-models.cpp` | admit | HTTP 200, 111 675 B, sha256 `cab14969…` (matches) | agree | line 2030 is exactly `{"models_autoload",      params.models_autoload},` |
| S627 `common/arg.cpp` | admit | HTTP 200, 224 666 B, sha256 `c69c0e07…` (matches) | agree | line 3682 `params.models_autoload = value;` inside the `--models-autoload`/`--no-models-autoload` callback; the only assignment in arg.cpp/common.h/server-models.cpp ("only writer" checked within those three files, not tree-wide) |
| S626 `tools/server/README.md` | reject | HTTP 200, 136 429 B, sha256 `eafc1b53…` (matches) | agree | line 234 names the flag and default; `grep models_autoload` in the README finds no `/props` JSON field |
| S628 `tests/unit/test_router.py` | reject | HTTP 404, 14 B (matches) | **disagree on substance** | the cited path is wrong, not the claim: `tools/server/tests/unit/test_router.py` at b12177 is HTTP 200, 33 103 B, and line 23 is `assert res.body["models_autoload"] is False` (line 17 `server.no_models_autoload = True`) — the seat's line-23 assertion exists; the rejection's flip condition is met at the correct path |

SOURCES row re-opened: S625 (`common/common.h`) — HTTP 200, 58 830 B, sha256 `c3010a3c…` (matches); line 705
`bool models_autoload = true;` — quote is 4 words (≤25), located exactly. Agree.

## Trend verdicts

- **expansion: improved** — `corpus/knowledge/router-props-autoload.md` (49 lines) added; three capability rows added; three
  admitted A-tier sources (census 363 → 368, validate exit 0).
- **quality: improved** — three instruments replaced by successors that refuse the wave's demonstrations (receipts above);
  the round-98 record defects are corrected and re-derivable.
- **discernment: unchanged** — the wave-driven amendment and the disclosed J escape are real discipline, but the sampled
  reject S628 missed the upstream test at its actual path (`tools/server/tests/unit/`), which a domain lane should know;
  one of four sampled decisions disagrees on substance, so I do not credit an improvement.

## Defects (status-neutral) and routed items for round 100

1. `SCORECARD.md:6431` pointer (in both round-99 correction blocks) is stale at the tip: the sentence moved to `SCORECARD.md:6446`
   when 71838fdd inserted `### Planned (round 100)`. Re-anchor or bind pointers to a revision; C2's audit should run at tip, not only at M.
2. Round-99 wave mix "58% attack counting the connector" (report, `SCORECARD.md` §Round 99) is arithmetic-wrong: 5 attack + 1 connector
   = 6/12 = 50% (`claims.json` already says `6 of 12 (50%)`). The same record class C2 corrected for round 98.
3. S628: re-file `tools/server/tests/unit/test_router.py` @ b12177 (line 23) as an admit candidate; the 404 was a path error.
4. `claims.json` still carries `"measured": "pending"` for C1–C3 and the freeze-time C3 `before` (`cells=5 mismatches=4`); the amended
   values live only in the report/LOG.
5. Carried pre-report arms (newest-closure, round75/round78 instruments) remain red as disclosed.

SHONEN: all four boxes remain `[~]`, author-asserted; none is fully checkable by a non-author from this round's evidence.
