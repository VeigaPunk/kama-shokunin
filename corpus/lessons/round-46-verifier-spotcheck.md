author: hyaku closure (non-author integrator, @m_opus)

# kama round 46: non-author closure spot-check

Date: 2026-10-26. Round measured: base `0163fea2dab3f282ebd70c71da9ab5de4cedf733` (round-45 spot-check), freeze `5790944350ae41bfe2ce50934bba59e086e747f4`, measured commit `4340cf2f68ebbfb618086e16825c2e7effd7fa58`, lane tip `e8fa87ef19ec5eb28f5fd9701a0a42da45bd688d`. I read committed bytes with `git show <rev>:<path>`. I made one blobless clone of `https://github.com/ggml-org/llama.cpp.git` under `/fast/scratch/hyaku/kama-r46-closure/`. That directory is scratch and was deleted after use. Every result below names a command that a fresh session can re-run.

I did not execute any lane gate, counter or lane tool. The frozen counters, the `append-only-audit` selftest, the gate registry and the regression counters were checked against their committed receipts. Both claims were also re-measured with my own plain commands: Python over `git rev-parse`/`git show` against the upstream clone for C1, and `git log --numstat` for C2.

Driver digest (copied from `.ufo/watchdog.log`, which is mutable):
`2026-10-26T16:39:29-03:00 launch kama round=46 pgid=368305 driver=hyaku-inline attempt=1`
`2026-10-26T17:53:47-03:00 complete kama round=46; hyaku-inline attempt=1`

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify on their frozen predicates and on my own independent measurement.
- No axis is harmed.
- The spot-check agrees with the Gate on the two admits and the two rejects I sampled.
- Seats disclosed the counter weaknesses in the report and in SCORECARD §Round 46. The lane did not hide or narrow them. They are routed below.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an %H' -- .ufo/reports/round-46/kama.md` → `kama-shokunin 8bca0cf333e7ceab5e734b354c87075c6efec86c`. Committer date 17:48:10 -03, after the lane tip commit date 17:46:38. | pass |
| `SHONEN` heading, one line per box | `## SHONEN` has 4 box lines, all `[~]`, each with a pointer | pass |
| Cited lane commits exist and descend to the branch | `git merge-base --is-ancestor <h> master` holds for all 9 cited hashes (base, freeze, `4a2a4d55`, `96d32918`, `7d057345`, `4340cf2f`, `4991ecc2`, `42ea1204`, `e8fa87ef`). `4d71b42f` is an upstream llama.cpp commit, not a lane commit: `git -C up rev-parse b11906` → `4d71b42fd87db24b8b7c808c151b713aa4459cfd`. | pass |
| Lane pushed and clean | `jj-lane.sh state` → `branch=master local=e8fa87ef… remote=e8fa87ef… ahead=0 behind=0 head=detached tracked=0 untracked=0`. `git status --porcelain` printed nothing. `ls-remote origin refs/heads/master` → `e8fa87ef…`. | pass |
| Prompt carries the template contract | `diff templates/round-prompt.md` against lines 1–140 of `.ufo/prompts/kama-round-46.md` differs only in placeholder substitution. The vendored template is byte-equal to the kimi-shokunin canonical template (`cmp` returned 0). Lines 141–624 are the hyaku addendum, also differing only in placeholders. No L2 route map is quoted. | pass |
| Counters frozen before data | `git diff --stat 57909443 e8fa87ef -- tools/round46-*.py` is empty. The sha256 of each counter at the tip (`502e6f57…`, `4dcfbe10…`) equals `claims[*].counter_sha256` in the preregistration. `frozen_at_utc` 19:50:02Z precedes the freeze commit (16:50:10 -03 = 19:50:10Z). The ledger and the tool are both absent at the freeze commit. | pass |
| L2 floor role split | The spec has 65 seats (`grep -o '"role": …' spec.json \| sort \| uniq -c`). There is no `planner` seat: the L1 held that role because the policy-v2 validator rejects `planner`. | **defect** (status-neutral; already carried as L0 `kama \| round-39`) |
| Red gate at tip | `hexrun-census` `unknown=21`, `exit=1` (`measured/hexrun-final.out`). This equals the base, so it is pre-existing and was not raised by this round. | **defect** (status-neutral, routed D4) |

This is not a marker: the round left real lane commits and evidence. Status `ok`.

## 2. Claims (step 2)

### C1: freshness 8→8, 91 on-release llama.cpp rows re-verified at b11906

Re-measured, not just evidence-checked. My Python re-derived each row of `registry/release-recheck-b11906.tsv` at `e8fa87ef` against the upstream clone. It reads `git rev-parse <pin>:<path>` and `git rev-parse 4d71b42f:<path>`, compares whitespace-normalised range text, and checks the witness strings inside the cited ranges. Results:

- Population: base `corpus/SOURCES.md` has 95 `on-release` rows that name `ggml-org/llama.cpp`. The four not in the ledger are outside the frozen definition:
  - S026 is `rejected` (a PR page).
  - S038, S482 and S484 are release, tag or asset pages, not file-pinned `blob/tree/raw` URLs.
  - Population is therefore **91**, and the set equals the 91 ledger ids. No duplicates.
- Verdict histogram: `holds 81`, `unchanged-file 6`, `holds-reworded 4`, `drifted 0`, `removed 0`. This equals the report.
- Blob and range checks:
  - All 91 `pin_blob` and `release_blob` values re-derive, and every `changed` flag re-derives: **0 mismatches**.
  - The `holds` and `unchanged-file` ranges are text-equal: **0 failures**.
  - For the 6 `unchanged-file` rows, the pin blob equals the release blob.
- Witnesses for the 4 `holds-reworded` rows:
  - S037 and S108: the witness is in the pin file and absent from the release file. The new witness is the reverse.
  - S043 and S121: whole-file containment fails because the witnesses are whitespace-collapsed multi-line strings. Checked inside the whitespace-normalised cited ranges instead: the pin witness is only in the pin range and the new witness is only in the release range. Pass.
- Commit distances, from my own count: b11889 (`d854d98b`) → b11906 is 17 commits. Of the 91 files, 73 are byte-identical between b11889 and b11906; 18 changed, all in `server-context.cpp` and `server-models.cpp`. This matches the lane's corrected 73/18 (lesson Mistakes, spec-prose-miscount row).
- SOURCES rows 226 → 228, new rows `S486` and `S487`. S486's line contains `b11906` and `4d71b42fd87db24b8b7c808c151b713aa4459cfd`, so `newrow=1`. The heading `## Round-46 release re-verification (llama.cpp b11906, appended 2026-10-26)` is present, so `section=1`.
- Committed receipts agree:
  - `controls/base.c1.out`: `unverified=91 … met=False`.
  - `measured/c1-after.out` at `4340cf2f`: `pop=91 rows=91 valid=91 unverified=0 … section=1 newrow=1 met=True`, `exit=0`.
  - `c1-final.out` at `42ea1204`: same result.
- Not shown by this measurement (the lane disclosed these):
  - `holds` is a text-equality check, and K1Cheat greened all 91 rows with a relocation script.
  - V1Code's checker defects F1–F4 are open.

**Verdict: freshness `improved`** (score 8→8 by design; 91 stale-prone rows re-verified at a newer release, none failing).

### C2: calibration 7→7, capability `append-only-audit`

Re-measured on the lane leg. Evidence-verified on the selftest and fixture legs.

- My independent recount uses a different definition from the tool: `git log --numstat 4a2a4d55 -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md corpus/SOURCES.md`, filtered to deletions ≥ 20. It runs over 294 commits and finds **5 events**:
  - `0718b6ab` LOG.md del=2292
  - `0718b6ab` SCORECARD.md del=2421
  - `0718b6ab` QUALITY.md del=375
  - `0718b6ab` README.md del=663
  - `dd9f5dc6` SCORECARD.md del=31
- The commit and file set is identical to the tool's 5 events. My deletion counts for SCORECARD and LOG are higher than the tool's (2421 vs 2417, 2292 vs 2290). This is the `---`-prefix blind spot the lane disclosed: `tools/append-only-audit.py:102` drops deleted lines that start with `---`. No event status changes on the lane.
- The capability row is present: `git grep -n '^| append-only-audit' e8fa87ef -- SCORECARD.md` matches line 130 (mirror) and line 2463 (canonical round-46 list), with last cell `46`.
- Registry rows are present: `SKILL.md:1441` (counter) and `SKILL.md:1442` (tool and selftest), matching `gate-final.out` `registered 38 unregistered 0 defective 0`.
- Committed receipts:
  - `aoa-selftest.out`: `AOA_SELFTEST pass=10 fail=0`, `exit=0`.
  - `controls/base.c2.out`: `selftest=0 fixture=0 lane=0 table=0 met=False`.
  - `measured/c2-after.out` at `4340cf2f` and `c2-final.out` at `42ea1204`: `selftest=1 fixture=1 lane=1 table=1 lane_events=5 lane_unrestored=0 lane_partial=2 met=True`, `exit=0`.
- Calibration value:
  - The tool caught a real overreach in the lane's own self-description. The round-45 lesson said the four truncated files were restored. The audit shows 2 of 5 events still `partial`. The lane turned that into a Mistakes row and accounted for all 8 missing lines.
  - Disclosed weaknesses (K2Cheat, X2Fixture, the shared `---` definition, mutant survivors, and K2Design's point that 3 of the 5 files are declared append-only nowhere) limit how far the counter's `met=True` proves sufficiency. They do not falsify the frozen predicate.
- Observation (new, not in the report): the restoration measure is relative to the tip. SCORECARD `restored_at_tip` for `0718b6ab` reads 2416 at base and 2409 at `4340cf2f` (`base.c2.out` vs `c2-after.out`). This round's head re-anchor changed the measure without any new deletion. Routed as D2.

**Verdict: calibration `improved`** (capability acquired with a passing demonstration, and it surfaced a real stale self-description). Score stays 7.

### Other axes (harm check)

- `git diff --numstat 0163fea2 e8fa87ef`:
  - LOG.md +6/−0, QUALITY.md +10/−0, README.md +101/−0, SOURCES.md +63/−0.
  - SKILL.md +10/−0 (registry rows).
  - PROVINCE.md +1/−1 (instrument clause).
  - SCORECARD.md +244/−8. All 8 removed lines are head re-anchors: the authority banner, the depth/coverage/calibration hashes and spot-check count 31→32, the planned pointer 46→47, capabilities 9→10, and two mirror and saturation sentences.
- Axis scores: none changed.
- Tip regression receipts:
  - r41 `mismatches=0 met=True`, r42 `met=True`, r43 `mismatches=0 met=True`
  - `digest-ledger` `unknown=0` (base 2)
  - `hexrun-census` `unknown=21`, the same as base
  - pointer check `met=True`
- The three harms the measured commit introduced were fixed in-round (`4991ecc2`, `42ea1204`) and filed as Mistakes rows.

Per-axis verdicts:

| Axis | Verdict | Basis |
|---|---|---|
| freshness | improved | C1 re-measured above |
| calibration | improved | C2 re-measured on the lane leg; selftest and fixture legs evidence-verified |
| operability | unchanged | score 8; three b11906 live receipts are evidence for C1, not an operability move |
| depth | unchanged | score 7; SKILL.md +10 registry lines |
| coverage | unchanged | score 9; PROVINCE instrument clause only |
| adjacency | unchanged | score 7; N1Overlap and N3Fleet reported, not absorbed |

## 3. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S486 (b11906 binary and tag identity) | admit | `gh api repos/ggml-org/llama.cpp/releases/tags/b11906` → `target_commitish 4d71b42fd87db24b8b7c808c151b713aa4459cfd`, `published_at 2026-10-26T19:45:36Z`, `prerelease true`, asset `llama-b11906-bin-ubuntu-x64.tar.gz 22478121 sha256:064ade62…eef3` (unauthenticated curl was rate-limited). Also `git -C up rev-parse b11906` → the same commit. | agree | The quote is located and exact (one token, within 25 words). The scope (identity only, not behaviour) fits a tier-A release record. |
| S487 (b11906 live receipts) | admit | `jq '.captures.health.body' .ufo/waves/round-46/c1/live/receipt-1.json` → `"{\"status\":\"ok\"}"`; `.outcome` → `pass`; `.captures.props.fields.build_info` → `b11906-4d71b42fd` | agree | The quote is exact. Scope is limited to three sampled instants on one model. The receipts were committed in `7d057345` before the row was cited. |
| S121, critic over builder | admit `holds-reworded` on the full range 5800-5805 → 6852-6857; reject the builder's single-line `holds` | `git show 704366d7:tools/server/server-context.cpp \| sed -n 5799,5806p` vs `git show 4d71b42f:… \| sed -n 6851,6858p` | agree | The error line and its `if` guard are byte-equal. The enclosing construct changed from the lambda `this->post_rerank = [this](…)` to `server_routes::handle_rerank_impl(…)`, and the anchor names "the error *and its guard*". Filing the full range with machine witnesses is the stricter, correct reading. A single-line `holds` would hide the relocation. |
| Teardown duration as a b11906 property | reject | `jq '.teardown.term_wait_ms' receipt-{1,2,3}.json` → `3`, `3`, `3`; the lesson records b11889 as 15, 9, 7 | agree | Three samples at two releases vary by 5×. That is an observation, not a property. This is consistent with the round-45 reject. |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → `exit=0`, with 93 `W04`, 1 `W01` (S481) and 0 `E`. This equals the report's start and end census.

Discernment: the spot-check agrees with the Gate on both admits and both rejects.

## 4. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | improved | A capability was admitted to SCORECARD with a passing demonstration (`append-only-audit`, rows 130 and 2463). LEARNING lists "a capability admitted to `SCORECARD.md`" as an expansion observable. No new `knowledge/` entries. |
| quality | improved | 91 on-release rows re-verify at b11906 with none failing (my re-derivation: 0 mismatches). `digest-ledger` unknown went 2→0. No admitted entry failed its re-check. |
| discernment | improved | The non-author spot-check agrees on 2 admits and 2 rejects (table above). |

## 5. Routed defects (lane fixes next round unless marked)

- **D1 (lane, C2 tool definition).** `tools/append-only-audit.py:102`, and the counter that shares its rule, drop deleted lines that start with `---`. On the lane this undercounts by 4 (SCORECARD) and 2 (LOG), compared with `git log --numstat`. A 21-line fixture with 2 such lines reads 0 events. Ship the planned v2 under a pre-data amendment with a recomputation leg that does not share the definition, for example `--numstat`.
- **D2 (lane, C2 measure stability).** `restored_at_tip` is measured against the tip. The SCORECARD `0718b6ab` restoration went 2416 → 2409 between `0163fea2` and `4340cf2f` from this round's head re-anchor alone. Either define partial-restoration against the event's own restore window, or state in the capability row that head re-derivations lower the number.
- **D3 (lane, C1 counter sufficiency).** Carry the open items: K1Cheat's relocation script greens all 91 rows, the reworded witnesses could be auto-picked, and V1Code's F1–F4 are unfixed. Together with the sufficiency family the lane's own S9Lesson sweep found (routed in rounds 41–45 and never a Mistakes row), write it as a lesson row with a check that can fail, or drop it with a reason.
- **D4 (lane, red gate).** `hexrun-census` `unknown=21`, `exit=1` at the tip, the same as base. Close or ledger the 21 unknowns.
- **D5 (lane, evidence durability).** The b11906 receipts' `teardown.log_path` points into deleted seat scratch (lesson Mistakes, dead-pointer row). Adopt the proposed in-tree or basename rule.
- **D6 (operator / aggregator, adjacency).** Seat N3Fleet reports the truncation class in 14 of 21 sibling lanes and was not absorbed. This is cross-lane evidence for the aggregator to arbitrate; the lane must not act on sibling repos.
- **Operator, L0.** The planner seat is still impossible under the policy-v2 validator (`kama | round-39`). The MISSION axes pair (`kama | round-35`) and the parked worktree (`kama | round-41..43`) are also still open.
- **Operator, promotion.** The four `SHONEN` boxes are `[~]` and look checkable by a non-author:
  - box 2: the live receipts and X1Replica, both re-opened above
  - box 1: the gate registry `registered 38 … defective 0`
  - box 3: `--selftest pass=10`
  - box 4: PROVINCE changed only in its instrument clause
  Promotion is operator-owned. Nothing was marked here.
