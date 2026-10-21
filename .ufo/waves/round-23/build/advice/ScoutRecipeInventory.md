# ScoutRecipeInventory — round-23 recipe inventory and draft

Seat: `CloseKama22.ScoutRecipeInventory` (scout, leaf). Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, base `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, host git 2.56.0. Read-only over lane/fleet except deliverables under `.ufo/waves/round-23/build/`. No installs. Scratch fixtures only under `/tmp/r23-inv` and the L1 probe's `/tmp`.

## Godspeed axes

| Axis | Move |
|---|---|
| Measurement integrity | Every expected exit is either observed or taken from the grid's declared/implemented gate; the counting command runs both arms and compares controls. |
| No-harm coverage | Audit selftest, historical raw/ledger, round-22 pinned witness, citation/install-io/sources gates. |
| Robustness | Absolute `--current`; explicit `--repo {lane}`; no self-writing harness command; no relative paths resolved against case cwds. |
| Minimality | 13 commands: 4 grid, 3 audit, 6 cross-tool gates. `{out}` is unused because `run.py` owns receipts. |

## 1. Round-22 commands touching the auditor or its selftest

Direct (invoke `tools/report-landing-audit.py`):

| Recipe anchor | Command (placeholder form) | Exit | Timeout |
|---|---|---|---|
| `.ufo/waves/round-22/recipe.json:49-58` (`c1-audit-selftest`) | `{python} {lane}/tools/report-landing-audit.py --selftest` | 0 | 180 |
| `.ufo/waves/round-22/recipe.json:59-70` (`c1-audit-ledger`) | `… --rounds 10-21 --json --fleet-repo /home/vgpnk/Projects/shokunin` | 0 | 180 |
| `.ufo/waves/round-22/report-source-fix/recipe.json:2-10` (`audit-selftest`) | same selftest | 0 | 180 |
| `.ufo/waves/round-22/report-source-fix/recipe.json:30-43` (`audit-historical-raw`) | `… --rounds 10-21 --fleet-repo … --no-errata --json` | 1 | 180 |
| `.ufo/waves/round-22/report-source-fix/recipe.json:45-57` (`audit-historical-ledger`) | `… --rounds 10-21 --fleet-repo … --json` | 0 | 180 |

Indirect (run the current auditor inside a witness):

| Anchor | Command | Exit |
|---|---|---|
| `report-source-fix/recipe.json:11-19` (`source-witness-selftest`) | `{python} {lane}/.ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py --selftest` | 0 |
| `report-source-fix/recipe.json:20-28` (`source-witness`) | same witness without arguments; runs pinned `cc9f8d3` and the current auditor on one synthetic census repo (`red-green-witness.py:67-124`) | 0 |

Measured receipts agree: `round-22/runs/6433390a/commands.json` has `c1-audit-selftest 0/0`, `c1-audit-ledger 0/0`; `round-22/report-source-fix/runs/80a6d07c/commands.json` has all ten commands `as_expected=true` (audit-historical-raw 1, ledger 0, witness 0). No other round-22 recipe command invokes the auditor; `citation-noharm`, `io-current-noharm`, `fr-*/nh-*` are cross-tool gates only.

`run.py` contract (`.ufo/waves/round-22/run.py`): placeholders `{lane}`/`{python}`/`{revision}`/`{out}` (lines 32-33), clean committed tree enforced (26), timeout recorded as 124 (47), `as_expected` (56), nonzero if any mismatch (62). No round-22 recipe used `{out}`.

## 2. Candidate observations (sha 6847641…, 2026-10-21T15:2xZ)

The lane working tree changed repeatedly while scouting. At candidate sha `684764108872cea153284dfec89848d5efdf5b30dd37db026434dea2b623e210` (98 insertions/21 deletions vs base):

| Command | Observed |
|---|---|
| auditor `--selftest` | exit 0, `selftest cases=50 failed=0`; stdout byte-identical to frozen (`1618` bytes, sha256 `91c3a6c99522c42e…`) |
| `--rounds 10-22 --fleet-repo … --json` | exit 0; `status=clean reports=13 defects=9 corrected=9 uncorrected=0 required=54 post_report=5 errata_rows=9` |
| same `--no-errata` | exit 1; `status=failed defects=9 corrected=0 uncorrected=9` |
| round-22 `source-witness` | exit 0 |
| `citation-provenance.py --json` | exit 0 |
| `install-io-grid.py --arm current --json` | exit 0 |
| `sources-census.sh validate` / `census` | 0 / 0 |
| `sources-append-only --from 4fe9339f --to 4fe9339f --repo .` | exit 0, `no append-only violations` |

Frozen-vs-current historical equivalence at that sha: ledger stdout byte-identical (sha256 `1ae84922500fe6e4…`), raw stdout byte-identical (`13b17b1cb1e50423…`), selftest stdout byte-identical; exits 0/1 and 0 both. Frozen copies must be given explicit `--lane-repo`/`--fleet-repo`: a `/tmp` copy derives its defaults from its own location and my first run exited 2 with `git rev-parse … in /tmp`.

L1 probe at that sha (frozen → current): F1 `exit 1` traceback → `exit 0` clean; F2 `1` traceback → `2` `output is not UTF-8`; F3 false clean `0` → `1 landed-omitted` (correct fixture); F4 `0` clean → `1 unresolved-full-hash`+`landed-unresolved`; F5 frozen `1` + `MARKER CREATED` → `2` `partial clone (extensions.partialclone)`, no marker.

## 3. Gate blocker: F5-promisor-sshcommand

Final GridHarness artifact: `.ufo/waves/round-23/build/out/GridHarness/repo-state-grid.py`, sha256 `141c0c2c8e4dee11db35af05e725edd901b07e562f07294fed25cfd1f9482be1` (33947 B). It pins the frozen blob and gates over 23 rows: 14 fault, 7 control, 1 open, 1 tradeoff (`repo-state-grid.py:416-472`, `563-580`). Expected exits per its own usage (`:12-19`): frozen 1, current 0, both 0.

Measured with `--repo {lane} --current {lane}/tools/report-landing-audit.py`:

```
--selftest                  exit 0  selftest checks=19 failed=0
--arm frozen                exit 1  14/14 fault rows violated, 7/7 controls met
--arm current @6847641      exit 1  reasons ["current expectation not met: F5-promisor-sshcommand"]
--arm both    @6847641      exit 1  same single reason
```

F5 row: expected `exit 1`, kinds `["unresolved-full-hash"]`, no marker; candidate observed `exit 2`, `could-not-evaluate: … partial clone (extensions.partialclone)`. The candidate's `check_history_repo` refuses any repo whose config declares `extensions.partialclone`/`remote.*.promisor` (`tools/report-landing-audit.py:448-450` at 6847641). F5 has only the config and no promisor pack, so `--no-lazy-fetch` alone is sufficient and the audit should complete with the fabricated hash unresolved. F12 (sha256), F8/F9 (shallow/grafts), and T1 (blob-filtered clone with a real promisor pack) still exercise the refusal paths.

Experiment (copy only; lane tool untouched): `/tmp/r23-inv/candidate-noconfig.py` = 6847641 with the config-name loop removed, keeping pack/shallow/grafts/format/top-level checks. Against the final grid:

```
--arm current  exit 0  pass True, reasons []
--arm both     exit 0  pass True; 14 fault rows frozen-false/current-true; 7/7 controls equal
F5 current: exit 1, ["unresolved-full-hash"], marker false
T1 tradeoff: exit 2 (promisor pack), observed only
```

So the recipe's grid gate is satisfiable by one narrow change: drop the config-only partial-clone refusal (option 1), or relax the F5 expectation to accept a typed exit-2 refusal (option 2, weaker: loses the "correct verdict" oracle). Do not change the recipe exits; resolve the fork before measurement.

## 4. Lane artifact hazard

The lane's untracked `tests/report-audit/repo-state-grid.py` (observed sha `7f3110ac…`, 27306 B) is **not** GridHarness's file (the seat disowns it; its own artifact is the 33947 B file above). That stray copy has no `--selftest` (argparse exits 2 `unrecognized arguments`), grades `--arm both` as 1 (`bad = any(violations)`), and one run aborted with `could-not-evaluate: fixture premise: promisor pack/missing blob not observed`. It has since been removed from the lane. Integrate the `out/GridHarness/repo-state-grid.py` bytes (or its patch), never the stray.

## 5. Proposed round-23 recipe

Written to `.ufo/waves/round-23/build/out/ScoutRecipeInventory/recipe-draft.json` (13 commands, 2-space JSON, sha256 `c00e02ba4b8b9a42137f1f32ebd58cca7a705ef8527fd57403dc088065bb74c8`):

| # | Name | Exit | Timeout | Role |
|---|---|---|---|---|
| 1 | `grid-selftest` | 0 | 300 | harness self-check (19 checks); a stray/old harness fails here |
| 2 | `grid-frozen` | 1 | 300 | frozen auditor violates all 14 faults; controls 7/7 |
| 3 | `grid-current` | 0 | 300 | the fix: 14/14 faults + 7/7 controls |
| 4 | `grid-both` | 0 | 300 | counting command: current passes, frozen reproduces every fault, controls equal |
| 5 | `audit-selftest` | 0 | 180 | 50/50 unchanged |
| 6 | `audit-historical-raw` | 1 | 180 | 9 uncorrected defects remain |
| 7 | `audit-historical-ledger` | 0 | 180 | clean via errata |
| 8 | `source-witness` | 0 | 180 | round-22 pinned witness unchanged |
| 9 | `citation-noharm` | 0 | 180 | sibling tool |
| 10 | `io-current-noharm` | 0 | 180 | prior-round grid |
| 11 | `sources-validate` | 0 | 180 | corpus gate |
| 12 | `sources-census` | 0 | 180 | corpus census |
| 13 | `sources-append-only` | 0 | 180 | base→`{revision}` only |

Grid argv uses `--repo {lane}` and an absolute `--current {lane}/tools/report-landing-audit.py`. `--current` with `--arm frozen` is a usage error in the final harness (`repo-state-grid.py:783`), so it is passed only for current/both. Grid timings observed: selftest 2 s, current 1.5 s, frozen 31 s, both 33 s; 300 s covers a 30 s per-case timeout.

No-harm exact baselines to compare against the stored JSON receipts (exit codes alone only prove clean/failed, not "unchanged"): reports 13, defects 9, corrected 9, uncorrected 0, required 54, post_report 5, errata_rows 9, errata_invalid/unmatched 0, by_kind landed-omitted 8/unresolved-full-hash 1; selftest 50/50.

Optional stronger gate: `.ufo/waves/round-23/build/out/HistoricalNoHarm/run-historical.sh` now exits 0 only when `gate=PASS` (`[ "$gate" = PASS ]`, line 158), comparing frozen vs current stdout/stderr bytes, exits, and exact counts. It is excluded from the minimal recipe because it rewrites its own `out/` receipt files and depends on a build artifact; if L1 accepts those writes, it can replace commands 5-7.

## 6. Not verified

- Did not run the recipe through `run.py` (lane tree dirty, no integration commit; `run.py:25-27` requires a clean committed tree).
- Did not run the final harness from its integrated lane path; ran the byte-identical `out/GridHarness` copy with `--repo {lane}`.
- Did not apply or verify the F5 fix in the lane; the passing run used the `/tmp` copy.
- Did not verify git < 2.44 behavior for `--no-lazy-fetch` (OldGitFloor seat).
- Did not verify the final integrated auditor sha; the lane tool changed after 6847641 (at 15:31Z it was `b0281f18…` with only a catch-all `Exception → exit 2` diff, i.e. mid-integration, not the declared fix). Re-measure only after the final bytes are committed.
- Open/tradeoff grid rows are observed, never gates; their text output still prints `NOT-MET` for them (JSON `kind` disambiguates).

## 7. Files written

- `.ufo/waves/round-23/build/advice/ScoutRecipeInventory.md` (this report)
- `.ufo/waves/round-23/build/out/ScoutRecipeInventory/recipe-draft.json`
- Scratch only: `/tmp/r23-inv/` (fixtures, receipts, `candidate-noconfig.py`); no lane/fleet source edited, no commits, no installs.
