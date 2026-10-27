# R57Item08ScorecardAudit — current SCORECARD/SHONEN calibration assertions vs tree

Seat R57Item08ScorecardAudit (revenger, leaf member — no subagent dispatch). Judged axes: calibration + operability, per the lane's live `shokunin.conf` assignment and SCORECARD banner (the `MISSION.md:29` operability + freshness conflict is left unresolved, as instructed). Read-only against `/home/vgpnk/Projects/shokunin/kama-shokunin`; no commits, no shared-file edits, no installs.

**Pinned revision for every number below: `8a7f19760242bbe523fa2d7d1b22528b587633c1` (HEAD at audit time). Every derived value is read from git at that revision (`git show` / `git ls-tree`), so concurrent worktree churn by sibling seats cannot change it. Three tracked deletions under `.ufo/waves/round-57/controls/` appeared during the seat; they are another seat's and were not touched here.**

## Result

29 independent count assertions were re-derived at the pin (`receipts/consolidated.out`, `receipts/case29-derive.out`). **28 hold; 1 is stale:**

| # | Assertion | Asserted | Derived at pin | Verdict |
|---|---|---|---|---|
| 1 | **freshness** row recheck count, window `S001–S477` | `218` | live registry `S001–S516` = **257** rows, **257** carrying a recheck cadence | **STALE** — window excludes 39 rows (S478–S516); count understates by 39 |

Separately, two count facts were stale at the frozen base and are no longer stale at the pin (repaired by lane-author commits, not by this seat):

| # | Assertion | At `b89bdab2` / `7c873d7b` | At pin | Status |
|---|---|---|---|---|
| 2 | **calibration** row spot-check glob count | asserted `42`, tree `43` (`verifier-spotcheck` blobs) → round-42 counter `mismatches=1 met=False`, exit 1 | asserted `43`, tree `43` → `mismatches=0 met=True`, exit 0 | stale at base, repaired at `8640e34c` |
| 3 | frozen claim text "counter currently reports `maxN=56` instead of **expected 46**" | counter reports 56 at `7c873d7b`, 57 at pin | `maxN` = highest `## Round N` heading, not 46 and not a capability-row count | claim's expectation is unsupported by the tree; the counter's value is correct |

## Assertion-by-assertion (pin `8a7f1976`)

Source: `receipts/consolidated.out` (all assertions derived independently of the lane's counters; exit 1 because of the single FAIL).

| Assertion | Asserted | Derived | Verdict |
|---|---|---|---|
| §Retired "6 axes" | 6 | 6 axis rows | PASS |
| §Retired "11 capabilities" | 11 | 11 canonical rows (canonical list as of round 49, line 2844) | PASS |
| §Saturation score vector | op 8, fresh 8, depth 7, cov 9, cal 7, adj 7 | identical from `## Axes` | PASS |
| §Saturation first-working rounds | 10,14,16,20,25,30,41,42,43,46,47 | identical from canonical rows | PASS |
| Banner "Latest measured round" | 57 | 57 (highest `## Round` section citing `.ufo/waves/round-N/measured/`) | PASS |
| Calibration spot-check glob | 43 | 43 blobs at pin | PASS |
| Freshness recheck count (windowed) | 218 | 218 in stated window | PASS (value) |
| Freshness count vs live registry | window S477 | 257 rows, max S516, 39 excluded | **FAIL** |
| Depth `grep -c '^## ' SKILL.md` | 43 | 43 | PASS |
| Depth 1612 lines + sha256 | 1612 / `2d7c2212…` | 1612 / `2d7c2212…` | PASS |
| Coverage knowledge entries | 34 | 34 | PASS |
| Coverage 186 lines + sha256 | 186 / `aa7915a8…` | 186 / `aa7915a8…` | PASS |
| Adjacency table pipes | 16 | 16 | PASS |
| Adjacency 87 lines + sha256 | 87 / `1801cb7f…` | 87 / `1801cb7f…` | PASS |
| Operability selftests | `RESULT pass=30 fail=0`; `selftest pass=9 fail=0`; `cases=79 failed=0`; `45/45` | identical | PASS |
| Operability 1138 lines + sha256 | 1138 / `4393ab81…` | 1138 / `4393ab81…` | PASS |
| Calibration selftests | `CAP_SELFTEST pass=2 fail=0`; `IA_SELFTEST pass=4 fail=0` | identical | PASS |
| Verdict ledger rows | 204 | 204 data rows | PASS |
| Claim-outcome ledger rows | 126 | 126 data rows | PASS |
| Verdict ledger tally | `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15` | identical under order harmed<unchanged<unprovable<unprovable-but-better<improved | PASS |
| Claim-outcome tally | `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1` | identical (mixed→other, unprovable ranks between partial and not-met) | PASS |
| `## Capabilities` mirror names | 11 names | identical to canonical names | PASS |
| SHONEN round-16 live receipt | "10/10 checks" | `receipt.json.checks` = 10 | PASS |
| SHONEN round-17 receipts | "11/11 checks each" | `receipt-{1,2,3}.json.checks` = 11 each | PASS |

Hash/line anchors recomputed with `sha256sum`/`wc -l`; selftests run bare from the lane (`receipts/` has the transcripts in `case29-derive.out`).

## Stale count 1 — freshness `218` bound to a dead registry window (live defect)

Row (SCORECARD.md line 15 at pin):

```
run `python3 -c "recheck=[l.split(chr(124))[10].strip() for l in open('corpus/SOURCES.md') if l.startswith(chr(124)+' S') and int(l.split(chr(124))[1].strip()[1:])<=477];print(sum(1 for r in recheck if r))"` → `218` (registry rows S001–S477 carrying a recheck cadence)
```

Measured (`receipts/scope-window-vs-registry.out`):

- stated-window command (`<=477`) prints **`218`** — equal to the row, so the pointer "re-derives" as written.
- full registry at the pin: **257** rows, `S001–S516`, and **257** of them carry a recheck cadence.
- excluded by the bound: `S478 … S516` (**39 rows**, ids enumerated in the receipt).

Provenance of the staleness (`receipts/provenance.out`; all values read with `git show <rev>:corpus/SOURCES.md`):

| rev | context | row bound / count | registry rows / max | excluded |
|---|---|---|---|---|
| `dd9f5dc6` | round 42 wrote the row | no `<=` bound / `220` | 220 / S479 | 0 |
| `c8c92db4` | round 42 "decouple head-table count facts" introduces `<=477` | S477 / `218` | 220 / S479 | **2** (born stale) |
| `82b5e9d3` | round 45 restore | S477 / `218` | 226 / S485 | 8 |
| `b9d5a091` | round-56 measured tip | S477 / `218` | 256 / S515 | 38 |
| `8a7f1976` | round-57 pin | S477 / `218` | 257 / S516 | **39** |

Why no counter fires:

- `tools/round41-scorecard-reconcile.py` executes the row's own command and compares stdout to the printed value; the stale command prints `218`, so `run_bad=0`. At the pin it reports `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True`, exit 0 (`receipts/counter-r41-pin.out`).
- `tools/round42-selfdesc-reconcile.py` only checks that the freshness row holds a run fact containing the needle `recheck` (`rel` counter), so it reports `mismatches=0 maxN=57 met=True`, exit 0 (`receipts/counter-r42-pin.out`).

Neither counter binds the row's *stated scope* (`S001–S477`) to the live registry bound. This is the calibration-axis defect AXES.md names — "SHONEN.md/SCORECARD entries match observed repo state" — on the freshness row, undetected by both standing counters.

**Minimal repair (hypothesis only; not applied — shared-file writes are outside this seat):** drop the `<=477` clause (or bind it to the live maximum row id) and re-anchor `218` to `257`; if the window is meant as a historical snapshot, label it "as of round 42" instead of presenting it as current coverage. Either way the count changes from 218 to 257.

## Stale count 2 — calibration `42` vs `43` (stale at the frozen base; repaired before this read)

- Round-56 measured tip `b9d5a091`: `corpus/lessons/` holds **42** `*verifier-spotcheck.md` blobs; the calibration row asserts 42 — consistent.
- Round-57 base `b89bdab2` adds the 43rd closure (`corpus/lessons/round-56-verifier-spotcheck.md`, commit `b89bdab2`, "round-56 verifier spot-check (integrator, hyaku): non-author admit/reject") without re-anchoring the row: row still asserts **42**, tree **43**.
- Reproduced: `round42-selfdesc-reconcile.py --tip b89bdab2` and `--tip 7c873d7b` → `r41=1 … mismatches=1 maxN=56 met=False`, detail `no stdout line == '42' (exit 0)`, exit 1 (`receipts/counter-r42-at-b89bdab2.out`, `receipts/counter-r42-at-7c873d7b.out`).
- Repaired at `8640e34c` (row now `43`, closure pointer `round-56`, wording "including round 56"). At the pin the row asserts 43 vs 43 blobs and the counter is `mismatches=0 maxN=57 met=True`, exit 0.

This seat made no edit; the change is the lane authors' round-57 work.

## Frozen claim's "expected 46" — falsified as a count

- `maxN` in `tools/round42-selfdesc-reconcile.py:167-168` is `max(rounds)` over every `^## Round (\d+)` heading. At `7c873d7b` the maximum heading is 56 → `maxN=56`; at the pin a `## Round 57` section exists → `maxN=57`. Nothing derives 46.
- The only 46 in the record is the round-46 measurement itself: SCORECARD line 2676 records "round-42 self-description counter `mismatches=0 maxN=46 met=True`" at `4340cf2f` — a historical reading, not a target.
- The canonical row count is 11 (round-49 heading, line 2844), and `canon()` selects round 49, not 46. `mismatches=0` at the pin is therefore honest on both counts.
- Consequence: the claim's "repair … counter currently reports maxN=56 instead of expected 46" has no tree-derivable basis; the counter value is right and the expectation is stale-by-copy from the round-46 line. The real stale count in the same area is the freshness window above.

## SHONEN

Four checklist items, all `[~]` author assertions; no numeric claim misses. The only counts are round-16 `10/10` and round-17 `11/11` receipt checks, and all four receipts carry exactly those check arrays at the pin (verified by JSON length, `receipts/consolidated.out`). SHONEN is thus count-clean; its open items are "no named non-author verifier / independent execution review remains open", which are judgment items, not stale counts.

## Shortcut-tally relevance (`considerthese/2026-10-26.md` proposal 3)

Proposal 3 (opened this round) asks for a running count of counters that a shortcut can satisfy. The freshness finding above is an instance of exactly that class: the row's run fact is satisfied by leaving a dead registry bound in place, and both registered counters stay green. Disclosure state at the pin: the `What met=True does not show` subsections run for rounds 46, 47, 48, 49, 50, 51, 52, 53 and 55 (nine subsections, SCORECARD lines 2661–3090), with none for round 56 or round 57 (round 54 has no SCORECARD section at all), and no paragraph discloses that the freshness run fact is value-bound rather than scope-bound. Round 56's C2 no-op limit is disclosed in prose instead ("C2's frozen counter checks a declared ROSTER literal, not that the harness executes its entries"). Advisory only: the tally, the disclosure paragraph and any row repair are lane-author or wave-author work, not this seat's.

## Limits and inference

- The lane's HEAD moved through `7c873d7b` → `8640e34c` → `16efcf5e` → `3d2d5d4d` → `77e7f5ee` → `8a7f1976` while this seat ran, as lane-author seats committed. Every number above is pinned to `8a7f1976`; receipts carry the `tip=` line.
- *Inference:* the freshness row is meant to evidence registry-wide recheck coverage (the row's own parenthetical says "registry rows … carrying a recheck cadence"), so a window ending 38–39 rows before the current registry understates it. The row's literal re-derivability is intact; only its scope is stale. No axis score is judged here.
- `receipts/consolidated.out` uses one hand-encoded rule not stated in the lane text: "latest measured round" = highest `## Round N` section that cites its own `.ufo/waves/round-N/measured/` directory. At the pin that derives 57, matching the banner.
- Non-author S515 spot-check (Git config runtime environment pairs; Git manual round source; ≤25-word quote) and the round-56 outside-defect lesson routing are other seats' deliverables; as a lane-author seat this report only advises that both remain open in round 57.

## Receipts (this directory)

`.ufo/waves/round-57/reports/R57Item08ScorecardAudit.receipts/`: `pin.txt`, `counter-r42-pin.out`, `counter-r41-pin.out`, `counter-r42-at-b89bdab2.out`, `counter-r42-at-7c873d7b.out`, `consolidated.out`, `consolidated.py`, `case29-derive.out`, `case29_derive.py`, `provenance.out`, `provenance.py`, `scope-window-vs-registry.out`.

## Tooling

No tools installed or upgraded; no pacman transactions (still paused). Python 3 stdlib, system `sha256sum`/`wc` only.

Report: .ufo/waves/round-57/reports/R57Item08ScorecardAudit.md
