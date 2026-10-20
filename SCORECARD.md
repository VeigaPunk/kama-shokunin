# kama-shokunin — SCORECARD

Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,
each bound to an evidence pointer and the round that last changed it.

**Current authority (actual round 5, blocked attempt):** assigned LIVE axes
remain operability and freshness (`../MISSION.md`); freshness is the lower
inherited author assessment. The numeric rows below are historical assessments,
not remeasured present file lengths, coverage denominators, or a completion
counter. Round-5 per-axis evidence below supersedes their current-state reading;
no scalar score is advanced. Historical reports exist for rounds 1, 2 and 4;
round 3's report gap remains unresolved. The headless launch counter 1 is not a
verified completed round. This attempt adds **zero** verified completed rounds.

## Axes

| Axis | Before → After | Evidence pointer | Last change |
|---|---|---|---|
| **operability** (worked round 1) | **0 → 8** | `tools/kama-probe.sh` md5 `1f81e859c2d7f43f87d1f7e01327b2cf` (1092 lines, 0755) + `registry/endpoint-consumers.tsv` (3 rows); live `check` → `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`; `--ufo-src` derives the ufo-fsd checkout (`$UFO_SRC` env → `~/Projects/ufo-fsd-alpha` → `~/Projects/origin-work/ufo-fsd-alpha` → fail-closed `file=missing`); `bash -n` clean (shellcheck absent on this box) | round 3 |
| **freshness** (worked round 2) | **6 → 7** | `snapshot` writes dated `kama-probe/v2` JSON and diffs tracked `registry/history/latest.tsv` into append-only `DELTA.md`; live re-census run: `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` — the 16 transitions are the honest record of 8 consumer files deleted from the box plus MODEL_OK→DEAD on the dead ports; stable re-run `transitions=0`; `tools/test-snapshot.sh` md5 `860f26ac05938cdfc1a8816eff1570b4` → `RESULT pass=24 fail=0` | round 3 |
| depth | 1 → 7 | `SKILL.md` (323 lines: 12-row decision table, 11 verbatim error signatures, 11 anti-patterns, 14-step checklist); `corpus/knowledge/endpoint-identity.md` (7 rule rows); `snapshot-history.md` | round 1 |
| coverage | 1 → 8 | `listener-census.md` (23-row round-1 sample; 20 listeners on round-2 refresh), `consumer-registry.md` (38 rows), `alias-endpoint-normalization.md`; registry covers all 6 consumer pin classes incl. the binary default | round 1 |
| calibration | 1 → 7 | round-1 audit records the wrong F11 route; round-2 critic rejected “periodic” for unscheduled invocation history; runtime fixtures are explicitly parser evidence, not vLLM/Ollama integration; corpus keeps open gaps | round 1 |
| adjacency | 1 → 7 | `cross-lane-scope.md` (ownership table, arbitration rule, per-lane handoffs); out-of-province findings remain reported, not absorbed; round-2 scheduler decision handed to L0 | round 1 |

Why operability stops at 8 and freshness at 7: the gate is verified against a real
llama.cpp runtime only (vLLM/Ollama are fixture-shaped parser tests), the registry pins
host-specific paths, and comparison is still **invocation-driven**. No clock runs
`snapshot`; a transition that starts and ends between invocations remains invisible.

Round-3 verdicts (godspeed axes): **operability — improved** (gates run bare again on
derived `--ufo-src`; before, two rows failed `file=missing` and one row crashed the
JSON resolver). **freshness — improved** (baseline now reflects live truth; DELTA.md
carries the 16-transition teardown record). **coverage — unchanged** (census corpus
kept, errata-marked; registry surface genuinely shrank — the files are gone, not
miscounted). **calibration — improved** (every changed anchor re-measured, dead-path
citations zero outside errata). **adjacency — unchanged** (out-of-province findings
reported, not absorbed).

**Carried debt:** the two positive-control rows (`ufo-fsd-thetick`,
`ufo-fsd-local-helper`) read `DEAD` — the pins verify `file=yes` at the relocated
tree but nothing listens on 34113. Unblock: operator restarts `qwen-coder.service`
(or a successor unit). Until then `model_ok=0` is ground truth, not a gate defect.

## Planned

After operator-owned route/binding repair, a **fresh session** remeasures the
lowest LIVE axis and chooses the next falsifiable freshness move. Do not repeat
the landed round-5 runbook correction as new progress. Candidate frontier:
re-anchor still-live probe citations through explicit corpus correction entries;
retain the dated source records. See `.ufo/round-5/continuation.md`.

Declared-vs-served context size remains a separate blocked feature: no current
serving context is available. Service restoration, scheduling and global route
configuration remain operator-owned; no timer or successor unit is installed.

## Retired

None. Both assigned axes remain active — though round 3 observed the
retirement precondition beginning to materialize: `qwen-coder.service` is
inactive and deleted, and every model endpoint is dead. Retirement still
requires evidence the surface is *permanently* gone (not observed — the
34113 pins ship in a maintained upstream repo), or that invocation history
and context drift have saturated (not observed).

## Move log

| Round | Axis | Before | After | Evidence |
|---|---|---|---|---|
| 4 | freshness | measured at HEAD (see lesson) | verdicts recorded per gate, no scalar | `corpus/lessons/round-4-recensus.md` |
| 5 (blocked attempt) | freshness | 3 mismatches / same 4 summary fields | 0 mismatches / 4; local delta only, no round admission | `.ufo/round-5/acceptance.json`; `corpus/lessons/round-5.md` |
| 6 (blocked dispatch) | — | — | — | `.ufo/round-6/telemetry.json` |
| 7 (blocked dispatch) | — | — | — | `.ufo/round-7/telemetry.json` |
| 8 (blocked dispatch) | — | — | — | `.ufo/round-8/telemetry.json` |
| 9 (blocked dispatch) | — | — | — | `.ufo/round-9/telemetry.json` |

## Actual round 5 — local verdicts, not native judgment

Measured tree: work commit bound by `.ufo/round-5/landed-evidence.json`; real
commands and full streams/exits in `.ufo/round-5/acceptance.json`. The probe and
snapshot implementations, registry identities/URLs/model expectations and
tracked history are unchanged. Only registry notes were inherited as edits.

| Axis | Verdict | Evidence and limit |
|---|---|---|
| freshness | improved | The four dependent documented summary fields agree with the real sample: mismatches 3 → 0. Active instructions date September successes and distinguish dead endpoints from correct pins. This is a local documentation delta, not an admitted round. |
| operability | unchanged | Existing command paths still run: check exit 2, consumers exit 0; fixture `RESULT pass=24 fail=0`, exit 0; two isolated snapshots exit 2 with byte-stable TSV/ledger. No runtime recovery or new behavior claimed. |
| depth | unchanged | No new serving/runtime knowledge admitted; existing normalized-id and identity/liveness rules retained. Historical counts of lines/signatures/checklist steps are not current measurements. |
| coverage | unchanged | Same three registry ids and domain surfaces; no new consumer census or integration with vLLM/Ollama. Historical census totals are not a live denominator. |
| calibration | unchanged | Missing independent spot-check, receipt binding, native dispatch and round-3 report stay explicit; correction of overclaims is not proof of externally calibrated judgment. |
| adjacency | unchanged | Route, service, credentials, scheduling and fleet-ledger actions remain with their owners; only lane-local records changed. |

| Learning trend | Verdict | Evidence and limit |
|---|---|---|
| expansion | unchanged | No new frontier knowledge or consumer surface admitted. |
| quality | improved | Stale active runbook superseded by measured instructions; `corpus/QUALITY.md` grounds admission criteria in the round-5 lesson. Historical corpus is explicitly dated, not erased. |
| discernment | unchanged | No outside non-author admit/reject spot-check. Author assertions remain `[~]`, never promotion `[x]`. |

**Admission: BLOCKED, not saturated.** Canonical wave plan validates exactly
32 scopes, exit 0, but authorized native routing cannot be realized; zero task
calls and zero verified-round increment. `wave-payload.json` is a rendered
plan, not a run. No native Phase 0/self-iter failure was re-executed.

**Named debt and unblock:**
- Operator/global route owner: content executor/scribe → `@m_composer`,
  audit/review/scout/critic (including sentinel/revenger/simplifier/mutation
  roles when used) → `@m_grok`, connector → `@m_antigravity` with requested
  `@m_zfl` fallback. Observed mappings and exact differences:
  `.ufo/round-5/route-preflight.json`; native routes currently select generic
  buckets instead.
- Fleet integrator: provide the real taskKey, report/receipt paths and
  prompt/config digest binding absent from the interactive Sighting record.
  No applicable task receipt or Sighting completion is claimed.
- Operator: restore an authorized serving runtime or decide permanent
  retirement. Until then the registered endpoints sample DEAD; do not change
  expected values to hide it.
- Fleet integrator: reconcile historical round-3 report omission and establish
  an evidence-backed cumulative verified-round total; no retroactive pass.
- Kama next fresh-session move: re-anchor still-live corpus citations while
  preserving dated history, then obtain authorized independent review.

## Capabilities

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns: 30 opened, tier-scoped, revision-anchored rows (17 mined by 3 knowledge entries, 8 queued, 5 rejected with reason + flip), 4 study paths, 3 search-log notes; contract-v1 census runs clean | `corpus/SOURCES.md`; census commands in §Round 10 below (rows 30, malformed 0, dups none, enum/tier-inflation none, missing used-by none) | 10 |

Rows enter only through a round that demonstrates the capability running (`AXES.md` §Capabilities); none enter through this rollout.

## Saturation

Saturation line **8/10 on every owned axis**; stagnation window **N = 4 consecutive rounds** with no capability entering the table (declared round 10; blocked attempts count toward N but never establish saturation). Round 10: not saturated (depth/calibration/adjacency self-assessed 7), nudge inactive.

## Round 6 — blocked dispatch, no axis claims (2026-10-18)

Goal-mode round 6 (loop 1 of 3, deepseek free round 1 of 2): 64-seat
AgentSwarm dispatched on `opencode-go/deepseek-v4.1-flash-free`; 64/64 seats
failed at spawn with the identical upstream error
`400 Upstream request failed: Model is unavailable.` (wave wall 41.6 s); a
single-seat re-probe ~2 min later failed with the same error. Zero seats
reached model execution — no claim work ran, no self-measurement exists.
Verdicts: **all axes unchanged** (no round executed). Admission:
**BLOCKED-WITH-DATA** — the upstream unavailability of the free wire id is
itself the loop-1 availability finding; effective concurrency ceiling at
2026-10-18T18:33Z: 0 usable seats. No scalar advanced. Evidence:
`.ufo/round-6/telemetry.json`; report at fleet root
`.ufo/reports/round-6/kama.md`.

## Round 7 — blocked dispatch, no axis claims (2026-10-18)

Goal-mode round 7 (loop 1 of 3, deepseek free round 2 of 2): availability
re-test of `opencode-go/deepseek-v4.1-flash-free`. 64/64 seats failed at
spawn with the identical upstream error
`400 Upstream request failed: Model is unavailable.` (wave wall 41.5 s) —
the same failure as round 6 ~4 min earlier. Verdicts: **all axes
unchanged** (no round executed). Admission: **BLOCKED-WITH-DATA**.
Unavailability persistent across three probes spanning ~25 min
(18:32, 18:33, 18:37Z); loop-1 deepseek concurrency ceiling: 0 usable
seats. No scalar advanced. Evidence: `.ufo/round-7/telemetry.json`; report
at fleet root `.ufo/reports/round-7/kama.md`.

## Round 8 — blocked dispatch, no axis claims (2026-10-18)

Goal-mode round 8 (loop 1 of 3, glm free round 1 of 2): the host runtime
rejected the wire id `opencode-go/glm-5.3-flash-free` in its model catalog
**before any seat was created** — zero spawns, zero upstream contact
(distinct failure class from rounds 6-7, where catalog-valid aliases died
upstream with 400). Verdicts: **all axes unchanged** (no round executed).
Admission: **BLOCKED-WITH-DATA**. No opencode-go glm variant (free or paid)
exists in this host's catalog; glm-5.3-flash is present only on the zai and
devin lanes, which are different providers — substitution deferred to
operator sign-off. L0 question filed at fleet `.ufo/l0-questions.md`
(kama | round-8). No scalar advanced. Evidence:
`.ufo/round-8/telemetry.json`; report at fleet root
`.ufo/reports/round-8/kama.md`.

## Round 9 — blocked dispatch, no axis claims (2026-10-18)

Goal-mode round 9 (loop 1 of 3, glm free round 2 of 2): re-attempt of
`opencode-go/glm-5.3-flash-free` — identical host-catalog rejection, zero
seats created, catalog byte-identical to round 8's listing 2 min earlier.
Verdicts: **all axes unchanged**. Admission: **BLOCKED-WITH-DATA**.
Loop 1 closes: rounds 6-9 all blocked-with-data, 0 tokens generated by
either free provider. Loop-1 final telemetry published in
`corpus/knowledge/free-tier-provider-limits.md`. No scalar advanced.
Evidence: `.ufo/round-9/telemetry.json`; report at fleet root
`.ufo/reports/round-9/kama.md`.


## Round 10 — sources registry + cross-engine entries; stale anchors re-anchored (2026-10-19)

Steered round 10 (the 2026-10-18 plan `.ufo/round-10/plan.json`, never dispatched, finished here). Axis authority: `MISSION.md:29` — operability + freshness; the round prompt's "operability + calibration" is overridden by the mission file (the G5 recurrence). Measured at this round's commit on branch `kaika/round` (hash cited in the fleet report). Scores are self-assessed and pending non-author verification.

| Claim | Axis | Before → after (measured) | Score | Counting command | Evidence |
|---|---|---|---|---|---|
| C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1) | freshness (lowest LIVE) | uncorrected stale-anchor rows 50 → 0 (42 active, 8 historical moves; 12 files; 0 dated lines rewritten) | 7 → 8 | the hardened ledger loop in `corpus/lessons/round-10.md` §Corrections / `.ufo/round-10/audit/stale-anchors.tsv` (prints `uncorrected …` lines piped to `wc -l`) | `.ufo/round-10/audit/stale-anchors.tsv`; `## Corrections — round 10` blocks |
| C3 — `sources-registry` capability + 3 entries on uncovered ground | coverage (capability acquisition) | `corpus/SOURCES.md` absent → 30 rows, census clean; knowledge entries 9 → 12; entries with `source: S###` 0 → 3; coverage-map rows 19 → 24 | 8 → 9 | contract-v1 census (`SOURCES-CONTRACT-v1.md` §Census); `ls corpus/knowledge/*.md \| wc -l`; `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md \| wc -l`; coverage awk over `## Coverage map*` sections | `corpus/SOURCES.md`; the three new `corpus/knowledge/*.md` |

Closed, not claimed: plan claim 2 (gate-bundle refresh as operability) — re-running unchanged gates is re-verification, not an operability move; its L1 samples are contested under the documentation-only rule and support no claim (`corpus/lessons/round-10.md` §Closed plan claim, §Contested L1 gate runs). Other axes: operability unchanged (probe/harness/registry bytes unchanged, md5 `1f81e859c2d7f43f87d1f7e01327b2cf`); depth unchanged (no SKILL decision rows added; one pointer line); calibration unchanged as a score — 24 mistakes mined and KQ6–KQ10 appended, but discernment awaits a non-author spot-check; adjacency unchanged (boundaries to kumitate/kengaku stated in each new entry; handoffs in the report).

Census at this commit: rows 30; malformed 0; tiers A=27 C=3; status mined=17 queued=8 rejected=5; duplicate ids none; enum/tier-inflation none; missing used-by none.

**Planned (round 11)** — supersedes §Planned above: (1) freshness — `source:`/`verified-at:`/`recheck:` provenance for the 18 pre-round-10 entries, appended, never invented (`source: none — historical record` where no live source exists); (2) coverage — K02 served-identity crosswalk (S016 → S001 → S010 → S011 → S012) and, only with an authorized runtime, K05 context capacity; (3) calibration — non-author admit/reject spot-check plus the SKILL.md stale-anchor sweep (scout: 13 of 14 anchor-bearing lines) appended as corrections.

## Erratum — round 10 post-review (2026-10-19): axes table and C3 restatement

The §Axes table at the top of this file (rows `freshness 6 → 7`, `coverage 1 → 8`, last change round 3/1) predates round 10 and was not updated by the round-10 commit `1e41928`. It is superseded, not rewritten, by these rows:

| Axis | Before → After | Evidence pointer | Last change |
|---|---|---|---|
| **freshness** (LIVE) | **7 → 8** | C1: 50 stale anchors corrected by appended entries (uncorrected 50 → 0); new-pointer validation `bash .ufo/round-10/audit/validate-new-pointers.sh` → `rows=50 resolved=48 terminal=2 unresolved=0` (A17 dead surface, A51 UNDECIDABLE — corrected, not re-anchored) | round 10 |
| coverage | **8 → 9** | C3, restated on knowledge entries only: `ls corpus/knowledge/*.md \| wc -l` 9 → 12; `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md \| wc -l` 0 → 3 | round 10 |
| operability, depth, calibration, adjacency | unchanged (8, 7, 7, 7) | §Round 10 above | — |

C3 restatement: the coverage-map delta `19 → 24` quoted in §Round 10 counts two administrative rows (`SOURCES.md`, `lessons/round-10.md`); the coverage measure is the knowledge-entry count above (3 new entries). Per-entry uncovered-ground rationale:
- `runtime-health-surface-matrix.md` — the map covered llama.cpp health/readiness only (`endpoint-identity.md`; README §Known gaps "real-runtime reconciliation is proven for llama.cpp only"); the entry extends it to documented cross-engine semantics (vLLM engine health and render-only exception, SGLang `/health_generate`, Ollama's undocumented health route). An extension, not a wholly absent topic.
- `serving-metrics-crosswalk.md` — no local engine-exporter row existed; `free-tier-provider-limits.md` is provider load-testing, and `served-model-identity.md` holds one dated llama.cpp metrics sample, not a cross-engine name/flag/boundary table.
- `gguf-runtime-compatibility-boundary.md` — no GGUF/quantization runtime-compatibility row existed; the served-id normalization rule was the only GGUF-related content.

Ruling recorded: the orchestrator ruled (2026-10-19) that the L1's read-only gate runs against the lane's own registered local endpoints are inside kama's province; the documentation-only rule targeted external live targets. No claim rests on them either way; S030 stays rejected under append-only (its flip condition is now met; a re-admitting row may be added in a later round).

## Round 11 — authority and declared moves (2026-10-20)

This section supersedes every earlier **current** assignment/planned statement,
not the historical observations. MISSION's Fleet shape delegates assignment to
`../shokunin.conf`: the current kama row is **operability + calibration**, not the
historical example's operability + freshness. Calibration 7 is lowest assigned
(operability 8); across the full historical table it ties depth/adjacency at 7.
Round-10 outside review exists at `corpus/lessons/round-10-verifier-spotcheck.md`;
earlier missing-review prose describes earlier attempts, never round 10's final
disposition or this round's verification.

Declared C1 is calibration of historical provenance, not refreshed runtime
observations; C2 works the previously tracked coverage axis on additional
local-model identity edge classes, an in-domain extension permitted by AXES.
The nine legacy knowledge files, not eighteen knowledge-plus-lesson records,
are C1's fixed denominator. New entries open with provenance; legacy corrections
append it to preserve frozen bytes and citation anchors.

Self-assessments stay calibration **7 → 7 (delta 0)**, coverage **9 → 9 (delta 0)**.
The measured field/entry counts are the falsifiable claim evidence, not an
objective conversion to a global 0–10 scale. Prior scalar moves remain historical
self-assessments. Operability 8, freshness 8, depth 7 and adjacency 7 are
unchanged; none is claimed to improve. No new capability is asserted.

The fresh reproduction command is
`python3 .ufo/waves/round-11/reproduce.py`; it runs the pinned original tree,
current tree, CLI self-test and isolated missing-field/prefix/tampered-baseline
controls. Its committed receipt records the revision actually measured.

**Planned — supersedes earlier planned rows:** obtain outside admit/reject
sampling for this round; use the next externally steered round to address
remaining actionable serving-domain evidence, never launch a new round here.
K05 remains runtime-dependent. No service restoration, automatic schedule,
provider substitution or route change is authorized by these claims.

### Round-11 measured results

Measured work commit: `3285cdf7a50481694a36c4425cf32c915ab5e5f0`.
Counting command for both separable modes:
`python3 .ufo/waves/round-11/reproduce.py`; complete stdout/exit receipt:
`.ufo/waves/round-11/acceptance.json`.

| Claim | Axis / score delta | Before → after | Verdict and limit |
|---|---|---|---|
| C1 | calibration 7 → 7; delta 0 | nine legacy files: missing fields 27 → 0; prefix violations 0 → 0; original exit 1 → final exit 0 | improved explicit evidence calibration; human/source dispositions in lesson; no runtime freshness claim |
| C2 | coverage 9 → 9; delta 0 | crosswalk entry 0 → 1, metadata-mode exit 1 → 0 | improved documented edge-case coverage; prior tags/ps/expiry/alias facts credited; metadata check is not semantic verification |

The same run verified eleven frozen input digests, self-test **19/19** (exit 0),
and isolated missing-field/prefix mutants (exit 1 with their named findings)
plus altered baseline (exit 2 `snapshot_tampered`). Source census:
`sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` yields
rows 31, A=28/C=3, mined=21/queued=5/rejected=5; validation exit 0 with
intentional W04 for S031. Original frozen census is rows 30,
A=27/C=3, mined=17/queued=8/rejected=5 (exit 0).

Admission remains **awaiting outside round-11 admit/reject spot-check**;
author-dispatched review and green measurements do not replace it.
Trend assessment: expansion improved (one new sourced extension), quality
improved (bounded corrections and safe rechecks); discernment unchanged pending
the round-11 outside sample. No axis harm observed within the documented scope.

## Round 12 — source-correspondence calibration (2026-10-20)

Current assignment remains operability + calibration (`../shokunin.conf:52`).
Calibration 7 is lower than operability 8; the stagnation nudge is inactive.
The outside round-11 decision is **ok / admitted true**, at
`corpus/lessons/round-11-verifier-spotcheck.md`; this supersedes round 11's
pending-review statement without rewriting that historical statement.

Declared **C1 calibration**: one historical auxiliary snapshot disagrees with
its declared source commit; a new byte-exact corrective snapshot reduces source
mismatches **1 → 0**, with integrity checked independently. Counting command:
`python3 .ufo/waves/round-12/reproduce.py`. Source revision is
`2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`; round-start revision is
`79fa257719e8688692ed1dc443589331ba22b7fe`. They identify different things:
the immutable source blob and the tree receiving this correction.

Numeric calibration stays **7 → 7 (delta 0)**. Other assessments remain
operability 8, freshness 8, depth 7, coverage 9, adjacency 7. No conversion
from mismatch counts to a universal mastery score, capability repertoire entry,
new serving surface, runtime validation or coverage expansion is claimed.
Evidence: `.ufo/waves/round-12/claims.json`; lesson `round-12.md` §Mistakes
and §Gate; source row S032 after the opened evidence is recorded there.

**Planned — supersedes earlier next-round prose:** outside non-author sampling
of this round's admit/reject decisions; future externally steered work chooses
serving-domain claims from fresh evidence. Context capacity and runtime
restoration remain operator-dependent, not silently replaced with bookkeeping.

### Round-12 measured results

Measured work revision: `33f46685b418af868259952884e34b93633820cb`.
Command: `python3 .ufo/waves/round-12/reproduce.py`, invoked from the fleet
root with the absolute script path; receipt
`.ufo/waves/round-12/acceptance.json`, overall exit 0 / `ok: true`.

| Claim | Axis / score delta | Before → after | Verdict / limit |
|---|---|---|---|
| C1 | calibration 7 → 7, delta 0 | One source path: old snapshot mismatch 1 / exit 1 `source_mismatch`; corrective snapshot mismatch 0 / exit 0 `clean` | improved fail-capable source correspondence plus explicit integrity-only erratum; old snapshot intentionally retained, not overwritten; new match is a construction check, not a discovery |

Both observations had `source_anchor_matches: true`; before
`source_matches: false`, after `true`. Integrity is independently checked on
the corrective snapshot. Selftest 11 passed / 0 failed; coherent snapshot+pin
mutation exits 1 `source_mismatch`, pin-only corruption exits 2
`snapshot_tampered` with **source mismatches 0**, source-redirection manifest
exits 2 `manifest_invalid`, empty source repo exits 2 `source_unavailable`.
All seven runner records matched their literal expectations and HEAD stayed
unchanged during measurement. No existing serving tool or endpoint was run.

Final source validation exit 0; rows 31 → 32, A 28 → 29, mined 21 → 22,
queued/rejected unchanged. Source S032 is opened Git documentation supporting
capture semantics; no capability or covered-ground row enters the repertoire.
Receipt `.ufo/waves/round-12/sources-final.json`.
Other axes unchanged; no observed axis harm within this evidence-repair scope.
Trends: expansion unchanged, quality improved, discernment unchanged pending
outside round-12 admit/reject sampling. Round admission awaits that non-author
closure; these are author-measured results, not promotion.
