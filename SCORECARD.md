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

## Round 13 — effective criterion precision (2026-10-20)

Current assignment: operability + calibration (`../shokunin.conf:52`).
Calibration 7 is the lowest assigned axis; no stagnation waiver is invoked.
Outside round-12 disposition: **ok / admitted true** at
`corpus/lessons/round-12-verifier-spotcheck.md`. Its D1 and quality-attribution
items motivate this round; C0 remains orchestrator/protocol work.

**C1 calibration:** two routed KQ15 formulations are made precise by appended
KQ16: distinct stable finding IDs versus shared exit classes (1/2/2), and
`git show` capture versus independent `git cat-file blob` comparison.
Before fixed denominator: two missing precise assertions; target after: zero.
This is bounded criterion correspondence, not a semantic proof from phrase
presence, new knowledge, current endpoint evidence or a new serving capability.
Historical KQ15 bytes and valid fidelity implementation remain unchanged.

Calibration **7 → 7, delta 0**; operability 8, freshness 8, depth 7,
coverage 9 and adjacency 7 unchanged. The claim's count is not converted to
a universal mastery score. Source method support S033 is opened this round;
actual source/code/receipt review remains distinct from documentation.
Evidence: `corpus/lessons/round-13.md` Gate/Mistakes;
`.ufo/waves/round-13/claims.json`, `advice/EvidenceScribe.md`.

**Planned — supersedes earlier planned statements:** obtain outside sampling
of this round's admit/reject decisions. Future externally steered work chooses
an actual serving-domain move from observed evidence; context capacity and
runtime restoration remain operator-dependent, not claimed by criterion work.

### Round-13 measured results

Measured commit: `641e1b6f1bef0e12d14c2e23388d7592ff0cb594`.
Counting command: `python3 .ufo/waves/round-13/measure.py --manifest
.ufo/waves/round-13/frozen/expected.json`; explicit `--quality
.ufo/waves/round-13/frozen/{before,after}/corpus/QUALITY.md` selects each
side of the same counting calculation. Receipt:
`.ufo/waves/round-13/acceptance.json`.

| Claim | Axis / score delta | Before → after | Verdict / limits |
|---|---|---|---|
| C1 | calibration 7 → 7, delta 0 | two missing precise assertions → zero; selected before exit 1 `documentation_mismatch`, after exit 0 `clean` | improved effective criterion precision; source/code/receipt review establishes substantive correction, literal count only measures adoption |

Live invocation `python3 .ufo/waves/round-13/measure.py` exits 0,
before 2 / after 0, verifying actual start git blob, preserved prefix and
final QUALITY equal to measured HEAD. Frozen-before independently equals
the start git blob; frozen-after equals final QUALITY. All old S-row strings
are unchanged. `--selftest` exits 0: ten actual CLI controls pass, none fail.
Both omission controls exit 1/missing1; bad/reversed/conflicting wording exits
1 even when missing-count is zero; tampered snapshot exits 2 before counting.
Gate registration: `SKILL.md` round-13 registry; all exit classes explicit.

Final source validation/census both exit 0; rows 32 → 33, A 29 → 30,
mined 22 → 23; B 0, C 3, queued 5, rejected 5 unchanged. S033 method
support is not covered serving ground. Receipt `sources-final.json`.
Other axes unchanged; no observed harm within scope; no capability row added.
Expansion, quality and discernment are **unchanged**, with the prior D4
quality credit confined to round 12. Admission awaits independent non-author
round-13 admit/reject sampling, never author-wave agreement.

## Round 14 — offline Ollama evidence replay capability (2026-10-20)

Current assignment remains operability + calibration (`../shokunin.conf` kama
row). Calibration 7 is lowest versus operability 8. The top round-5 block is
historical, not current assignment authority. No stagnation waiver.
Outside round-13 disposition is **ok / admitted true** at
`corpus/lessons/round-13-verifier-spotcheck.md`; that disposition supersedes
round-13's pending-review wording, without rewriting the filed record.

**C1 calibration / capability:** acquire an offline Ollama exported-metadata
replay classifier. Existing available/running/remote and candidate digest-join
concepts are credited to `served-identity-crosswalk.md`. New repertoire is the
actual CLI policy over fixed literal adversarial cases. Before at
`e1b3d746dbfd2100b61c67b6389217252592460f`: no classifier blob
(`.ufo/waves/round-14/before-capability.json`). After target: every committed
case matches literal finding/exit through the child CLI; readiness remains
unknown for all. This retrospective unsupported-before baseline is capability
absence, not an old runtime bug or red-before semantic repair.

Calibration **7 → 7, delta 0**; no mastery score is inferred from a finite
fixture corpus. Source S012/S031 fields were reopened, strict join policy is
inference. `corpus/knowledge/ollama-evidence-replay.md` holds the operational
workflow; source rows gain only allowed used-by links. Existing serving probes,
runtime integration, registry expectations and observed endpoint state are
unchanged. Other axes remain unchanged unless separately evidenced below.

Supplemental outside D2 historical table clarification is appended only in
`corpus/lessons/round-14.md`; discovery belongs to CloseKamaR13 and this counts
toward no claim/axis/trend improvement. No old gate or receipt is rewritten.
`QUALITY.md` KQ17 preserves outer verdict versus subfinding separation.

**Planned — supersedes earlier plan:** obtain independent non-author sampling
of this capability's admits/rejects; future steered domain work should target
new observed serving evidence. Live integration/context capacity remains
operator-dependent. Do not claim offline replay as runtime restoration.

### Round-14 measured results and capabilities

Measured work commit: `e545ed99aaa519196a2a7779b0a293b2ce4c765c`.
Counting command: `python3 .ufo/waves/round-14/measure.py --tool PATH`.
Use absent `.ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py`
for the retrospective starting-capability baseline (actual start git tree
contains no tool), preserved `frozen/precedence-before.py` for the actual
same-round defective draft, and `tools/kama-ollama-evidence.py` for final.

| Claim | Axis / score | Before → after | Verdict and limits |
|---|---|---|---|
| C1 offline Ollama evidence replay | calibration 7 → 7, delta 0 | 0/51 supported at absent-tool baseline → 51/51 exact CLI finding/exit/schema/readiness/scope matches; actual draft 49/51 → corrected 51/51 | improved new replay repertoire; finite synthetic metadata, no actual serving integration/readiness |

Both corpus runs share SHA-256
`4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4`.
Actual draft failures are `remote_missing_digest` (expected unknown2, observed
remote_inventory1) and `tags_none_ps_duplicates` (expected invalid_input2,
observed unknown2). Only precedence was corrected; same final oracle.
`python3 tools/kama-ollama-evidence.py --selftest` also exits 0/clean,
51 passed and 0 failed, but shares that same-round separately authored oracle;
it is not independent external corroboration. Receipt:
`.ufo/waves/round-14/acceptance.json`, ok true, errors empty.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| ollama-offline-evidence-replay | Reconcile caller-supplied tags/ps captures using exact names/digests and fail-closed remote/unknown/invalid classifications, with readiness always unknown | `python3 tools/kama-ollama-evidence.py --selftest`; measured command/streams and 51 literal cases in `.ufo/waves/round-14/acceptance.json` at work commit above | 14 |

No other numeric axis changes: operability8, freshness8, depth7, coverage9,
adjacency7 unchanged. Source validate and census both exit0; rows33→33,
A30/B0/C3 and mined23/queued5/rejected5 unchanged; only S012/S031 used-by
gains the replay workflow. Prefix preservation true for all five active
instruction/ledger files; all 25 protected tracked files equal their start
blobs (`preservation.json`). One scout seat died with provider
RESOURCE_EXHAUSTED; the 32-seat dispatch is retained, no replacement spawned.

Trends: expansion improved through demonstrated capability only; quality and
discernment unchanged (no new conceptual/source truth or outside round-14
sampling). Author claim verdict improved; admission awaits independent
non-author closure, no promotion box is newly certified.

## Round 15 — executable duplicate-corpus admission repair (2026-10-20)

Current assignment is operability + calibration (`../shokunin.conf` kama row).
Calibration7 remains the lowest versus operability8; no stagnation waiver.
Outside round14 is `ok / admitted true` within its unique fixed repertoire
(`corpus/lessons/round-14-verifier-spotcheck.md`); its R1 explicitly excludes
the false generalized corpus-duplicate guarantee and routes an executable
repair. R2 distinguishes partial advice from terminal provider success.

**C1 calibration:** reject duplicate-containing measurement corpora even
when at least sixteen distinct stripped names remain, before runner child
creation; retain valid all-unique corpus measurement. This is an actual
guard repair, not a new API fact or a wording-only recalibration.
Before source is `.ufo/waves/round-15/frozen/measure-before.py`, pinned to
`6e348e28943849aceb08d6954dee92be48ce9ba8` and its original path/digest by
`frozen/manifest.json`. Current implementation changes only the guard.

Counting command: `python3 tests/ollama-corpus-guard/check.py --runner PATH`;
use the frozen source path for before and `.ufo/waves/round-14/measure.py`
for after. Expected results come from committed literal matrix files under
`tests/ollama-corpus-guard/`, not from recalculating policy as oracle.
Negative controls have at least sixteen unique names plus a duplicate;
positive controls defeat a vacuous reject-all implementation. Real runner
and classifier CLI paths, corpus error reason and observed process boundaries
must all correspond. The historical original 51-case classifier corpus and
receipt remain unchanged.

Calibration **7 → 7, delta 0**; finite-contract repair does not establish a
new mastery score. No capability row is added: the repaired measurement
guard's enforcement is credited once, not rebranded as classifier reliability
or repertoire growth. S034 records the original predicate supporting outside
R1's diagnosis; S012 is the metadata/readiness boundary, not case-name policy.
Final measured revision, counts and verdict are appended after execution.

**Planned — supersedes earlier plan:** independent non-author round15
admit/reject sampling; a subsequent steered move should build actual
serving-domain evidence rather than repeat this guard correction.
Live integration/context capacity remains operator-runtime dependent.

### Round-15 executed results

Measured and pushed implementation revision:
`4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`.
Receipt `.ufo/waves/round-15/acceptance.json`: **ok true**, errors empty.
All executions were L1 post-integration, after both waves returned.

| Claim | Axis / score | Measured before → after | Verdict |
|---|---|---|---|
| C1 declared-name duplicate-corpus admission | calibration 7 → 7, delta0 | same 50-test matrix: 23 passed/27 failed against original → 50 passed/0 failed; 27 duplicate controls accepted/measured → rejected before runner child creation | improved bounded enforcement; no mastery, classifier-policy or runtime claim |

Counting command from lane root:
`python3 tests/ollama-corpus-guard/check.py --runner PATH`.
Before PATH `.ufo/waves/round-15/frozen/measure-before.py`; after PATH
`.ufo/waves/round-14/measure.py` (also default).
Both controls use explicit temporary tool/cases flags inside the harness,
so relocated defaults never supply false red evidence.
Predicate-only `frozen/guard-only-red.py` also reproduces the
same23/50 result with final prose unchanged and only the guard removed.

Observed duplicate-control classifier/Popen counts **483/483 → 0/0**;
valid-control counts **402/402 → 402/402**. All27 rejected controls have
exact `corpus: duplicate case names`, null findings/exits and zero audited
process events. Valid controls defeat reject-all. Total runner audit
events count both Popen and `_posixsubprocess.fork_exec`, not two children.
Full nested results and streams are retained in `run-{before,causal_red,after}.json`.

`python3 tests/ollama-corpus-guard/check.py --selftest`: exit0/clean,
50 passed/0 failed; same literal oracle, not independent corroboration.
`python3 .ufo/waves/round-14/measure.py`: exit0, original51/51 exact
finding/exit/scope matches, unique names51. Original classifier, cases,
receipt, serving tools/registry, province and SHONEN remain byte-equal
to start (`fidelity.json`). No live serving probe was run.

Final source validate/census exit0; rows33→34, A30→31, mined23→24;
B0/C3/queued5/rejected5 unchanged. Only S012 used-by changes in existing
rows; S034 is scoped own-work diagnosis, not expansion or discovery.

Other five axes **unchanged**; no observed harm within the stated scope.
Expansion, quality and discernment **unchanged**: no new knowledge/capability
ground, no serving-knowledge revalidation, and no independent round15
admit/reject sample. Gate repair is credited under C1 only. Outside
admission remains pending; four promotion assertions remain `[~]`.

## Current state (round 16) — supersedes the stale current-tense readings above

This block supersedes, without rewriting, the "Current authority" paragraph
(lines 6-13), §Planned (lines 45-55) and the round-10 saturation reading
(line 132). Assigned axes: **operability + calibration** (`../shokunin.conf:52`).
Latest numeric readings: operability 8, calibration 7, freshness 8, coverage 9,
depth 7, adjacency 7 (round-10 erratum and later rows; rounds 11-15 changed none).
Calibration 7 is the lowest assigned axis; saturation line 8, so the
stagnation nudge is inactive because calibration is below it. Capability rows
held: `sources-registry` (round 10; registry now 41 rows after round 16) and
`ollama-offline-evidence-replay` (round 14, §Round-14 measured results). The
registered consumers were last sampled `DEAD` in `registry/history/latest.tsv`
(snapshot 20261014T124232Z); nothing listens on 8080 or 34113.

## Round 16 — loading-envelope verdict and live llama.cpp lifecycle (2026-10-20)

Outside round 15 is `ok / admitted true`
(`corpus/lessons/round-15-verifier-spotcheck.md`); its routed defects are
dispositioned in `corpus/lessons/round-16.md`. No stagnation waiver.

**C1 calibration (lowest axis):** the probe graded a loading llama.cpp
server "non-2xx HTTP from a non-model service" (`FOREIGN_SERVICE` /
`non-2xx-non-model-http`) since round 1, although the lane documented the
loading body in round 10. Repair: `MODEL_LOADING` / `llamacpp-loading` for the
exact envelope only (KQ19), plus appended corrections to every lane document
that called the vocabulary fixed or the state foreign. Counting command:
`python3 .ufo/waves/round-16/measure.py` (frozen
`.ufo/waves/round-16/frozen/kama-probe-before.sh` versus `tools/kama-probe.sh`
over the literal matrix `tests/probe-verdicts/*.json`). Planned score
**7 → 7**: one overreach caught on one envelope is not a mastery change.

**C2 operability (capability acquisition):** `live-llamacpp-lifecycle` —
start the pinned official llama.cpp b11755 server with a pinned GGUF on an
unregistered loopback port, capture its surfaces, grade it with the probe,
tear it down and prove teardown; receipt re-derived by
`tests/llamacpp-live/check-receipt.py`. Before: no lane tool could start a
runtime (last real llama.cpp sample round 3). Counting command: the live tool
plus the gate (SKILL.md §Round-16). Planned score **8 → 8** with a capability
row; the caps at lines 26-28 (one engine, host paths, invocation-driven) stay.

Sourced claim: C1 rests on S036/S037 (llama.cpp code at 704366d76), opened
this round. Measured values are appended below after execution.

### Round-16 measured results

Measured revision `726f737a942f1606d66e032f1efbcbb6f689ccf1` (pushed); receipt
`.ufo/waves/round-16/acceptance.json` (ok true, errors empty). All
measurements are L1 runs after both waves returned. Correction to C2 above:
the last real llama.cpp answer was round 2 (2026-09-29T04:30:44Z), not round 3,
which saw only refused connections.

| Claim | Axis / score | Counting command | Before → after | Verdict |
|---|---|---|---|---|
| C1 loading-envelope verdict | calibration **7 → 7**, delta 0 | `python3 .ufo/waves/round-16/measure.py`; `python3 .ufo/waves/round-16/stale-statements.py --rev REV` | stub matrix (72 rows, 17 `MODEL_LOADING`, set sha256 `bf9068d8…1f32`): frozen 55 pass / 17 fail (exit 1) → current 72 / 0 (exit 0), changed verdicts exactly the 17 loading rows; stale lane statements 17 uncorrected at `20e392e` → 0 at `726f737` | improved, bounded: one overreach caught, its corpus traces corrected; no mastery change |
| C2 `live-llamacpp-lifecycle` | operability **8 → 8**, delta 0; capability row added | `python3 tools/kama-llamacpp-live.py …` + `python3 tests/llamacpp-live/check-receipt.py RECEIPT --expect-model-sha256 … --expect-server-sha256 … --expect-probe-sha256 … --expect-tool-sha256 …` | 0 lane tools able to start a runtime → 1; receipt 10/10 checks, `VALID`; frozen-probe control 10/10; loading window captured live (38 × 503 exact envelope on `/v1/models`) | capability acquired; operability caps at lines 26-28 unchanged |

No-harm runs: `bash tools/test-snapshot.sh` 30/0 (was 24/0; the new cases
go red on the frozen probe, 27/3); `check.py --selftest` 72/72 + 4/4. Sources
validate exit 0; rows 34 → 41 (A 31 → 38, mined 24 → 31, B 0, C 3, queued 5,
rejected 5). Other axes unchanged: freshness 8 (the pinned README was re-read
and the stale round-11 reading corrected, but no registered endpoint was
re-sampled), depth 7, coverage 9, adjacency 7 (persistent install and PATH
shadowing disclosed; province narrowing pending L0).

**Capabilities — canonical list as of round 16** (supersedes the one-row table
at lines 122-128 without editing it; rows enter only with a demonstration):

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: 41 opened, tier-scoped rows; contract-v1 census clean | `corpus/SOURCES.md`; `scripts/sources-census.sh validate … kama` exit 0 | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed, readiness always unknown | `python3 tools/kama-ollama-evidence.py --selftest`; §Round-14 measured results | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server with a 1.2 MB CI fixture GGUF on an unregistered loopback port, capture its loading and ready surfaces, grade it with the probe, tear it down; receipt gate re-derives every check. Not consumer health, quality or timing | `.ufo/waves/round-16/live/receipt.json` + `check-receipt.py` (SKILL.md §Round-16) | 16 |

Stagnation window: a capability entered at round 16, so the window restarts;
calibration 7 stays below the saturation line 8, so the lowest-axis rule binds
next round. Trend verdicts (author, pending outside review): expansion
improved (new knowledge entry on code-level loading behaviour plus a demonstrated
capability); quality improved (round-11 README reading corrected against pinned
code and a live capture; seven corpus files corrected); discernment unchanged
(no non-author admit/reject sample this round).

**Planned — supersedes earlier planned statements:** outside non-author
sampling of round 16. Next steered move, from the debt named in
`corpus/lessons/round-16.md` §Falsify wave: make the live checks
fail-capable (`health_ready` body, termination cause, graded
`loading_envelope_exact`) and the matrix's reason/exit/drift grading
load-bearing; K05 (declared versus served context) remains open.
