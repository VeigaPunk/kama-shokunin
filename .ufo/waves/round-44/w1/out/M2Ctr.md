VERDICT: 21/22 mutants of the frozen C2 counter killed (13 over-accept kills on hand fixtures, 8 over-reject kills — 7 of them by the fully-valid fixture alone), 1 survivor: M03b (`ok = len(got) >= 2` → `== 2`), byte-equivalent to the frozen counter on all three committed controls and all 19 hand fixtures, because no line in the 68 frozen corpus files gives any trend ≥ 3 distinct verdict words — a coverage finding, not a counter defect. Baseline: my runner reproduced all three committed C2 control receipts byte-identically (modulo the fixture `tip=` line).

# Round 44 / seat M2Ctr — mutation test of the frozen C2 counter

Target: `tools/round44-verdict-ledger-audit.py` sha256 `1933e75b2a5308d09d0cfafd166c95cfcb1b7c15eaf1bf9ad2b321a453224bd1` (matches `preregistration.json` C2 `counter_sha256`; lane HEAD `098df344d977a9047ea346a01a93c307887570b0`, file committed clean). The lane file was never edited; every mutant was applied to a `git clone --shared` copy under `/fast/scratch/hyaku/kama-r44/M2Ctr/`.

## Method

1. **Baseline faithfulness.** Re-ran the committed builder unchanged:
   `python3 build_controls.py --lane <scratch lane clone> --upstream /fast/scratch/hyaku/kama-r44/shared/llama.cpp --fleet /home/vgpnk/Projects/shokunin --scratch <scratch>/ctl-baseline` → builder exit 0, 8.7 s wall; all three C2 receipts (`base`, `junk-c2-allimproved`, `junk-c2-noscorecard`) and all five C1 receipts byte-identical to `.ufo/waves/round-44/controls/*.out` after stripping the `tip=` line (fixture commit hash differs per run). Receipts: `out/M2Ctr/receipts/base.c2.out` etc. vs `out/M2Ctr/receipts/committed-*.out`.
2. **Mutants.** 22 single-point mutants over the ten assigned mutation points, applied as exact-string replacements (each anchor asserted to match exactly N times) to a per-mutant scratch lane clone's `tools/round44-verdict-ledger-audit.py`; unified diffs in `out/M2Ctr/diffs/<id>.diff`.
3. **Committed controls per mutant.** Re-ran `build_controls.py` with the mutant as the C2 counter (`--lane <mutant lane clone>`); compared the three C2 receipts against the committed ones (normalized). All 22 builder runs exit 0; all C1 receipts identical in every run (the mutant only replaces the C2 file).
4. **Hand fixtures.** 19 fixture repos (each `git clone --shared` of the lane at base `9d9cc93e`, ledger + SCORECARD committed with a throwaway identity inside the scratch clone, `rev-parse --show-toplevel` verified equal to the clone dir):
   - `good` — the anchor: the automatic last-hit ledger (204 rows, row-for-row identical to the lane's `.ufo/waves/round-44/c2/draft-ledger.tsv` on round/trend/side/verdict/line — verified programmatically, `identical: True`) plus the exact SCORECARD (26 mismatch rows parsed from the pristine counter's own `table missing` detail, summary `agreement=61/72 overclaim=3 underclaim=8 other=15 absent=15`, `## Axes` calibration row naming `registry/verdict-ledger.tsv`). Pristine counter: `met=True`, exit 0.
   - `ns-good` — the same ledger with no scorecard rewrite (replicates the committed `junk-c2-noscorecard` control, decoupled from counter-driven generation). Pristine: `met=False`.
   - 17 corruption fixtures `k*`, each the smallest edit that should flip one rule; pristine verdict recorded for every fixture (`good`/`k9b` True, all others False). Files: `out/M2Ctr/fixtures/good/`, spec in `out/M2Ctr/fixtures.json`.
5. **Kill rule.** A mutant is killed when its `met`/exit flips against the pristine counter on a fixture where the pristine verdict is the correct one (over-accept: mutant True on a defective fixture; over-reject: mutant False on `good`), or when any committed control receipt changes. Scorecards of five fixtures (`k2`, `k2b`, `k3a`, `k3c`, `k4b`, `k7b`) were convergence-patched against the mutant itself (from its own `summary line wanted` / `table missing|extra` detail) before the pristine cross-check, so the mutant gets every chance to reach `met=True`.

## Results (`out/M2Ctr/mutants.tsv`, per-mutant counts in `out/M2Ctr/kill-evidence.tsv`)

| Mutant | Mutation point | Controls | Smallest killing fixture | Direction |
|---|---|---|---|---|
| M01a | read_line nearest-preceding trend (`:93-105`) → first-trend | junk-c2-noscorecard | `good` | over-reject (valid 204→202: the two non-first trends on spotcheck round-10 line 17 lose their verdict) |
| M01b | read_line → next-trend (deferred) | junk-c2-noscorecard | `good` | over-reject (valid 204→31, bad=173: trend-first lines — the corpus norm — yield no verdict) |
| M02 | ubb/unprovable distinction (`:101`) | junk-c2-noscorecard | `good` + `k2b` | both: over-reject (the 2 ubb rows become unverifiable, valid 202) and over-accept (`k2b`: both ubb rows re-filed as `unprovable` on their ubb lines → met=True; pristine bad=2) |
| M03a | mixed `>=2`→`>=1` (`:184`) | — | `k3a` | over-accept (mixed on a 1-verdict line accepted) |
| M03b | mixed `>=2`→`==2` (`:184`) | — | **none — survivor** | byte-identical everywhere |
| M03c | mixed `>=2`→`!=1` (`:184`) | — | `k3c` | over-accept (mixed on a zero-verdict line accepted) |
| M04a | absent note/line form dropped (`:173`) | — | `k4a` | over-accept (absent with note `x` accepted) |
| M04b | absent has-verdict check dropped (`:175`) | — | `k4b` | over-accept (absent claimed while spotcheck round-10 line 17 gives the trend `improved`) |
| M04c | absent only-when-file-missing (`:175`) | junk-c2-noscorecard | `good` | over-reject (the 3 round-38 self absent rows sit on an existing file; valid 204→201) |
| M05a | repo/rev/path pinning dropped (`:167`) | — | `k5` | over-accept (path `.ufo/reports/round-10/kama.md.bak` accepted) |
| M05b | pinning reduced to repo (`:167`) | — | `k5` | over-accept (same fixture) |
| M06a | duplicate-key check dropped (`:165`) | — | `k6` | over-accept (duplicated row accepted, last wins) |
| M07a | overclaim/underclaim swapped (`:211`) | junk-c2-noscorecard | `good` + `k7a` | both: over-reject (summary flips to `overclaim=8 underclaim=3`) and over-accept (`k7a`: swapped summary accepted) |
| M07b | equal-pair `agree` branch dropped (`:209`) | junk-c2-noscorecard | `good` + `k7b` | both: over-reject (agree 61→0, underclaim 69) and over-accept (`k7b`) |
| M08a | `textra` dropped from met (`:251`) | — | `k8a` | over-accept (extra table row for an agreeing key accepted) |
| M08b | table matched on (round,trend) only (`:229`) | junk-c2-noscorecard | `k8b` | over-accept (self/outside cells swapped in a table row, accepted) |
| M08c | `tmiss` dropped from met (`:251`) | — | `k8c` | over-accept (mismatch row removed from table, accepted) |
| M09a | summary check dropped (`:237`) | base, junk-c2-allimproved, junk-c2-noscorecard | `k9a` | over-accept (summary line removed, met=True) |
| M09b | summary exact-match (`:237`) | — | `k9b` | over-reject (summary with trailing prose rejected; pristine accepts) |
| M09c | summary `n` = agree only (`:235`) | junk-c2-noscorecard | `good` | over-reject (wants `agreement=61/61`, correct ledger rejected) |
| M10a | axes cite dropped from met (`:240`) | base, junk-c2-allimproved, junk-c2-noscorecard | `k10a` | over-accept (calibration row without the ledger cite accepted) |
| M10b | `calibration` word requirement dropped (`:245`) | — | `k10b` | over-accept (Axes row naming the ledger without the calibration cell accepted) |

Controls notes: the `junk-c2-noscorecard` diffs for M01a/M01b/M02/M04c/M07a/M07b/M08b/M09c are partly **generation-coupled** — `build_controls.py` builds that control's ledger *with the counter under test* (it imports `read_line`/`side_spec` from `--lane/tools`), so a read_line mutant also changes the fixture it is scored on. The decoupled `ns-good` fixture (pristine-generated ledger, no scorecard) separates the two; every mutant above is also killed or cleared there. M09a/M10a diff `base`/`junk-c2-allimproved` only in the counts line (`summary=1`/`axes=1` forced; `met` stays False there) — the strong kill is the fixture.

## Survivor M03b — analysis

`ok = len(got) >= 2` → `ok = len(got) == 2` (mixed rule, `tools/round44-verdict-ledger-audit.py:184`). `got` is the set of distinct verdict words the cited line gives the row's trend; the mutant differs from the frozen counter only when that set has ≥ 3 members. A scan of all 68 corpus files (34 fleet reports at `b0fd7b7f`, 30 lane spotchecks at `9d9cc93e`; rounds 20-23 spotchecks are missing at base — `out/M2Ctr/receipts/corpus-analysis.json`, `ge3: []`, `multi_trend` count 1) finds **no line giving any trend 3 or more distinct verdict words**, so no ledger row over the frozen bytes can distinguish the two. All three committed controls and all 19 hand fixtures — including `good`, where the mutant reproduces `met=True` with the identical counts line — are byte-identical between mutant and pristine (`out/M2Ctr/results/M03b.results.json`). Smallest input that would kill it: a cited line like `expansion improved, harmed and unchanged` (one trend, three distinct verdict words) in any of the 68 files at the frozen revs; none exists. This is a coverage finding about the corpus, not permission to change the contract: the frozen counter's mixed rule is minimally tested because the frozen corpus never exercises a 3-verdict line.

## Findings summary

1. **M03b survives** (above) — the only mutant no fixture kills; smallest would-be killing input documented.
2. **Control-builder coupling** (`.ufo/waves/round-44/controls/build_controls.py:104-128`, the `junk-c2-noscorecard` block): the control ledger is generated by the counter under test, so read_line mutants perturb their own control fixture. A finding for future control design (build the control ledger with a pinned pristine copy), not a defect in the frozen counter; the decoupled `ns-good` fixture covers the gap here.
3. No mutant was over-accepted by the committed controls alone in a way that flips `met` on them — every over-accept kill required a hand fixture; the controls' value for C2 is the valid-ledger-no-scorecard shape (`junk-c2-noscorecard`) and the all-invalid shape (`junk-c2-allimproved`).

## Commands (evidence)

- Baseline: `python3 build_controls.py --lane $S/lane --upstream /fast/scratch/hyaku/kama-r44/shared/llama.cpp --fleet /home/vgpnk/Projects/shokunin --scratch $S/ctl-baseline` → exit 0; receipts byte-identical to committed (diff after stripping `tip=`: empty for all 3 C2 + 5 C1).
- Per mutant: `python3 mtest.py run-mutant <ID>` (wraps the builder above with the mutant in `tools/`, then runs the pristine and mutant counters over every fixture: `python3 <counter> --repo <fixture> --tip <fixture HEAD> --fleet /home/vgpnk/Projects/shokunin --out <receipt>`). 22/22 builder runs exit 0; no missing receipts; all C1 receipts identical.
- Aggregate: `python3 mtest.py collect` → `out/M2Ctr/mutants.tsv`; per-mutant counts/first-detail → `out/M2Ctr/kill-evidence.tsv`.

No lane file was edited; no git state in the lane was touched (read-only `git clone --shared` sources only); all fixture commits used throwaway identities inside scratch clones with `rev-parse --show-toplevel` isolation checks. Scratch `/fast/scratch/hyaku/kama-r44/M2Ctr` removed after artifact copy.

## Deliverables

- `mutants.tsv` — 22 rows: mutant, family, mutation, controls diff, fixture kills, verdict, smallest killing fixture.
- `kill-evidence.tsv` — per-mutant mutant/pristine counts lines and first detail on the killing fixture.
- `diffs/` — 22 unified diffs (mutant vs frozen counter).
- `results/` — 22 per-mutant results.json (controls comparison + all fixture verdicts).
- `receipts/` — baseline + committed control receipts, corpus-analysis.json, per-mutant cited counter receipts.
- `fixtures/good/` — the anchor fixture's ledger and SCORECARD; `fixtures.json` — full fixture specs and pristine verdicts; `mtest.py` — the driver.
