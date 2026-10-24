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

## Round 17 — graded fields backed by failing detectors; fail-capable live checks (2026-10-20)

Outside round 16 is `ok / admitted true` (`corpus/lessons/round-16-verifier-spotcheck.md`);
its routed defects and the jj-migration risks are dispositioned in
`corpus/lessons/round-17.md`. Calibration 7 is the lowest assigned axis; no
stagnation waiver. Claim separation criterion: `corpus/lessons/round-17.md`
§Declared claims (C1 touches only check.py and its detectors, C2 only the live
tool, its gate and its controls; the probe is byte-identical throughout).

**C1 calibration (lowest axis):** `SKILL.md:533` claimed check.py "grades
verdict, reason, exit and drift" and maps harness errors to exit 2; no detector
could fail any of those gradings (round-16 mutants 5/5 survived), `served_model`
and the route were not graded, and a non-object probe row ended in a traceback.
Repair: graded `served_model` and route, per-row malformed/non-UTF-8 handling,
fault-control detector, mutant grid. Counting commands: `python3
tests/probe-verdicts/fault-controls.py --check <frozen|current> --json` and
`python3 .ufo/waves/round-17/c1/mutants.py --grid --out PATH`. Score **7 → 7**:
an instrument's self-description made true is a bounded calibration repair, not
a mastery change.

**C2 operability (hardening of `live-llamacpp-lifecycle`, sourced on S042–S044):**
receipt v2 checks fail on the misbehaviour they name. Counting command:
`python3 tests/llamacpp-live/controls.py --tool ABS --gate ABS --json` on the
frozen and the current tool+gate, plus three real b11755 runs gated with four
pins. Score **8 → 8**; no new capability row (the round-16 row is hardened, not
new).

### Round-17 measured results

Measured against the working tree that the round-17 build commit lands (hash in
`LOG.md` §round 17); raw outputs `.ufo/waves/round-17/runs/` and
`.ufo/waves/round-17/live/`.

| Claim | Axis / score | Counting command | Before → after | Verdict (author) |
|---|---|---|---|---|
| C1 graded fields backed by a failing detector | calibration **7 → 7**, delta 0 | `fault-controls.py --check …`; `mutants.py --grid` | fixed detector: frozen check.py accepts 3 of 8 faults (served_model, route skip, malformed) → current 0 of 8; mutants under the full detector: frozen 7 of 8 applicable killed → current 10 of 10; under the round-16 pair detector both gates kill only reject-all (1 of 8, 1 of 10) | improved, bounded |
| C2 fail-capable live checks | operability **8 → 8**, delta 0 | `controls.py --tool … --gate …`; `kama-llamacpp-live.py` ×3 + `check-receipt.py` with four pins | frozen tool+gate accept 6 of 8 bad controls (+1 inconclusive) → current 0 of 8, each failing its targeted check; gate-flip arm 0 accepted; real runs 11/11 ×3, `VALID` | improved |

No-harm: probe `36b64978…` unchanged; matrix digest `bf9068d8…` unchanged;
round-16 `measure.py` PASS in a `/tmp` clone with the new check.py;
`test-snapshot.sh` 30/0; round-16 v1 receipts `VALID` with four pins. Other axes
unchanged: freshness 8 (llama.cpp b11756/b11757 checked: the three server files
are byte-identical; no registered endpoint re-sampled), depth 7 (one appended
section deepens an existing entry), coverage 9 (no new surface), adjacency 7
(handoffs advised, nothing absorbed). Sources validate exit 0; rows 41 → 46
(A 38 → 43, mined 31 → 36).

**Capabilities — canonical list as of round 17:** unchanged from round 16
(`sources-registry` now 46 rows; `ollama-offline-evidence-replay`;
`live-llamacpp-lifecycle`, whose evidence pointer is now receipt v2
`.ufo/waves/round-17/live/receipt-1.json` + `check-receipt.py` and the controls).
Stagnation window: last capability entry round 16 (window 1 of 4).

Trend verdicts (author, pending outside review): expansion unchanged (no
uncovered ground; one existing entry deepened; no new capability); quality
improved (the round-16 entry's v1 limits are superseded by graded checks backed
by sources and controls; seven lane statements corrected by appended text; no
admitted entry failed re-check); discernment unchanged (no non-author sample yet).

**Planned — supersedes earlier planned statements:** outside non-author sampling
of round 17. Next steered move: K05 (declared versus served context) on the
lane-owned fixture, or the round-16 M3 harness `shutdown()` design gap; the
matrix-byte debts (why-line numbers, one duplicate class) wait for a round that
re-pins the matrix digest.

### Round-17 falsify results (appended)

Measured lane commit: `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (the pointer above
to LOG named no hash). Falsify wave: 80 seats, 71 completed, 9 failed on provider
rate limits (7 left no report); every C1 and C2 number re-ran identically in `/tmp`
clones (`corpus/lessons/round-17.md` §Falsify wave). Rows 46 → 47 (S047 supersedes
S043; A 43 → 44, mined 36 → 37).

Verdicts after falsification (author, pending outside review):

- **C1 calibration — improved, bounded.** The self-description is now backed for
  the named fields and the two new invariants; non-author-authored mutants H1–H3,
  H5–H7 survive both detectors, so the claim is "each documented grading has a
  killing fault", not "the gate cannot be weakened". Score 7 → 7.
- **C2 operability — improved, with a disclosed trade risk.** Accepted-bad controls
  6 → 0 and three plus twenty-three real runs `VALID`; but 1 of 60 real runs under
  32x CPU saturation failed `loading_envelope_graded` on a healthy server (the v1
  receipt would have passed it), and six v2 checks have no retained bad control, so
  C2 rests on the four checks the controls flip. The operator may read the
  saturation false failure as an operability trade; it is reported, not netted out.
  Score 8 → 8.

Planned (supersedes the planned row above): (1) classify zero loading observation as
could-not-evaluate (exit 2) and retain bad controls for the six uncontrolled v2
checks; (2) gate hardening: `--require-schema v2`, exact argv re-derivation, grade
every 503 in `transitions`; (3) frozen-manifest prior-exposure field; then K05.

## Round 18 — outcome classification and detector self-calibration (2026-10-20)

Round-17 outside review admitted the two bounded claims and judged **discernment
improved** (`round-17-verifier-spotcheck.md:217–221`), superseding the pending
author reading at line 702. R1–R7 dispositions are in `lessons/round-18.md`.
Assignment remains operability + calibration; calibration 7 is lowest, no waiver.

**C1 operability, sourced, score 8 → 8 (delta 0):** receipt v3 separates no loading
observation from an observed failure; retains subject-misbehaviour controls for six
checks; hardens schema floor, exact argv, loading transitions, IPv6 ownership and
internal-fault receipts. Counting command:
`python3 .ufo/waves/round-18/c1/measure.py` with its explicit tool/gate/control
inputs (official invocation and input hashes in `round-18/runs/`). The same
capability is hardened, not newly acquired. One engine, host paths and
invocation-driven sampling still cap operability.

**C2 calibration, score 7 → 7 (delta 0):** a statement→mutant→detector ledger makes
the named round-17 survivors and escaped fault paths explicit. Counting command:
`python3 .ufo/waves/round-18/c2/survivors.py --json --out PATH`, with the
frozen/source manifest and current file pins. The universe is H1–H3/H5–H7,
the named detector-self/append-only survivors, refusal prose and two malformed
decoder/process-group faults; it is not a claim of universal detector adequacy.
Fresh falsify-wave mutants are reported separately, never silently added to the
original denominator or hidden if they survive.

Capabilities unchanged from the canonical round-16 list: sources-registry,
ollama-offline-evidence-replay, live-llamacpp-lifecycle. New knowledge ground
(procfs ownership/IPv6 encoding) is coverage expansion under C1, not a fourth
claim or another runtime. Other scores unchanged: freshness 8, coverage 9,
depth 7, adjacency 7. Last capability entry round 16; stagnation window 2 of 4.
Measured results, measured commit and exact commands are appended after execution.

### Round-18 measured results (recovery attempt 2)

Work commit `0c75c611474cfc9f3c549e056fb0b736b20b854f` (code/corpus),
evidence commit `888cd384a9cd06dd93d3fe6b05a9d829b9972122`, harness commit
`eb78788b35b832d08887d4c366d1d0c1df3a6c19`; the official
`python3 .ufo/waves/round-18/runs/run.py` started on that clean tip and
`runs/commands.json` records `measured_commit` = that tip, 32 commands, all
expected exits, harness exit 0. Raw stdout/stderr, exits and input digests are
retained under `runs/`.

| Claim | Axis / score | Before → after (measured) | Counting command | Evidence pointer |
|---|---|---|---|---|
| C1 — outcome classification and receipt boundary | operability **8 → 8** (delta 0) | accepted_bad **5 → 0**; good_rejected **1 → 0**; misclassified **1 → 0**; uncontrolled_checks **0 → 0**; gate_flip_arms 16 → 17; counter exit 0, faults none | `python3 .ufo/waves/round-18/c1/measure.py --controls tests/llamacpp-live/controls.py --frozen-tool … --frozen-gate … --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --json` (full argv in `runs/commands.json` `c1-measure`) | `runs/c1-measure.json`; real v3 runs and five-pin gate VALID in `runs/live-gate-{1,2,3}.stdout` |
| C2 — statement→mutant→detector ledger | calibration **7 → 7** (delta 0) | 15 named items; before survived 11 / miscount 1 / accepted 3 → after killed 11 / correct 1 / handled 3; inconclusive 0 → 0; exit 0 | `python3 .ufo/waves/round-18/c2/survivors.py --json` (full argv in `runs/commands.json` `c2-survivors`; the JSON document is `runs/c2-survivors.stdout`, and the counter's exclusive `--out` is never clobbered) | `runs/c2-survivors.stdout`; frozen witnesses 15/15 matched; family-b rerun 0 divergences (`residual/advice/ResidCounterC2.md`) |

Disclosures for these numbers: C2's denominator is the ledger's 15 named
items, not the full detector-self (a)–(d) set — mutant (b) "any nonzero exit
counts" is named in `SurvivorUniverse.md` and excluded with reason; two of the
11 kills (FC-target, FC-f6cache) flip from inconclusive to killed only because
the counter's arm-combination rule was repaired, while their raw main-arm
results did not change. The stale pre-repair artifact is retained at
`runs/pre-repair/c2-survivors.json`. The earlier exit-2 pass at `c6dc46f` is
historical and not overwritten.

Other axes unchanged: freshness 8, coverage 9, depth 7, adjacency 7.
Capabilities unchanged from the canonical round-16 list; no capability row
enters this round (the C1/C2 moves are hardened measurement and classification,
not new repertoire). Last capability entry round 16; stagnation window now 3 of
4 — the next round should be a capability/frontier move unless an axis drops.

**Planned (supersedes earlier planned rows):** (1) close the named gate leaves
from `GateCaptureHashes` M1–M4 and the fresh-mutant survivors (`FreshGate`,
`FreshControls`, `FreshAppend`, `FaultF0`, `FaultTarget`,
`GateLoadingTransitions`, `GateModelsStatus`, `GateNullLicense`, `AppendCells`);
(2) add an enumeration check to the C2 selftest-kill arm and decide the
detector-self denominator (mutant (b)); (3) pin the remaining install-tree
members the receipt names, or state the boundary as policy; (4) obtain the
outside non-author admit/reject spot-check for this round; K05 remains
runtime-dependent and operator-owned.

**Erratum (round 19, routed defect 3):** the official C2 counting invocation is
`python3 .ufo/waves/round-18/c2/survivors.py --json` — the JSON document is
`runs/c2-survivors.stdout`; the `--out PATH` wording in the C2 declaration row
above is superseded. `runs/c2-survivors.json` is a pre-official corrected run
retained beside the official stdout; they agree.

## Round 19 — revision-qualified citations and the install-tree pin (2026-10-21)

Assignment remains operability + calibration; **calibration 7 is the lowest
assigned axis**. The four routed round-18 defects are corrected first
(lesson erratum, S055 qualification, SCORECARD erratum, residual assignments).

**C1 calibration, 7 → 8, sourced:** revision-qualified citations become
machine-checkable. Counting command `python3 tools/citation-provenance.py`:
before `required=3 found=0 verified=0 missing=3` exit 1; after
`required=3 found=3 verified=3 missing=0 mismatch=0` exit 0, selftest 5 cases.
Evidence: `registry/required-citations.json`, the `cite(...)` tokens in
`corpus/lessons/round-18.md`, S057's admission of the identity-boundary limit.

**C2 operability, 8 → 8 (delta 0):** sixth pin
`--expect-install-tree-sha256`; counting command
`python3 tests/llamacpp-live/install-tree-grid.py … --gate
tests/llamacpp-live/check-receipt.py --receipt
.ufo/waves/round-18/live-recovery/receipt-1.json …` — without the pin
`baseline=VALID members=3 rejected=0/3` exit 1, with `--tree-sha`
`baseline=VALID rejected=3/3` exit 0. The pin binds observed bytes, not an
upstream constant, and does not authenticate execution.

Other axes unchanged: freshness 8, coverage 9, depth 7, adjacency 7.
Capabilities unchanged; stagnation window 4 of 4 is reached at round end —
the next round should be a capability/frontier move unless the operator rules
otherwise. Planned: close the named gate coverage leaves, add the C2
enumeration check, and obtain the outside non-author spot-check.


**Round-19 C1 erratum (falsify-wave refutation accepted):** C1 lands
**calibration 7 → 7 (delta 0)**, verdict *improved-bounded*, not 7 → 8. The
checker binds three registry-row digests (document-bound, ancestry-gated,
15 selftest cases); it does not bind the sentence beside a token, and routed
defects 1 and 4 are record corrections rather than pointer checks. The
`gate-live-1` row is re-pinned to `1b85a24`/`1cb5a41b…` as the blob that names
`live-recovery/`. Wording correction: see `corpus/lessons/round-19.md`
§C1 scope correction.

### Round-20 correction of round-19 record

The round-19 declaration at 823–824 and erratum at 846 are superseded:
four registry-row digests, not three; `required=4 found=0 verified=0 missing=4`
exit 1 → `required=4 found=4 verified=4 missing=0 mismatch=0 off_ref=0` exit 0
at `028235e6` (`round-19/evidence/c1-counting.txt`). Its selftest printed
"15 cases", not five. C1 still holds calibration **7 → 7**.
"Falsify-wave refutation" is a label error: the critics were build seats;
the round-19 66-seat falsify call spawned zero. Append-only corrections and
clean-commit retrospective selftest/census receipts are recorded in
`corpus/lessons/round-20.md` and the appended round-19 lesson correction.

## Round 20 — named error regressions and GGUF declared identity

Assigned axes remain operability 8 + calibration 7 (lowest non-retired
assigned axis). Calibration below saturation 8 means no stagnation waiver.
Capability window 4/4 motivates C2 without waiving C1.

**C1 calibration, 7 → 7:** named grid/selftest error-classification regression
repair, not a universal census. A frozen named-cell population and real-verdict
controls distinguish crash/abort from credited rejection or kill. Counting
command `python3 tools/error-verdict-census.py --json`. Base instrument revision
`37bd4c5bd456a2f8a54d3312c28495c321715856`; the cell registry is committed
before official measurement. Sources S061/S062/S064; counterexample S063.

**C2 operability, capability acquisition, 8 → 8:** bounded offline GGUF metadata
identity and captured-receipt comparison, `tools/gguf-identity.py`.
Independent real-file oracle is `gguf==0.19.0`; the one existing CI GGUF and
committed independent synthetic fixtures form the finite population.
Sources S058/S060. Reading declarations does not establish loaded-weight
identity, current endpoint health, model quality or authenticated execution.

Other axes held: freshness 8, coverage 9, depth 7, adjacency 7. The final
measurement appendix records commands, counts and the measured revision.


### Round-20 measured results — committed tree 0957ce61

Work/frozen-population commit `33a6777866d0f63d894ef21bc863486bcb35b56c`;
measured tree `0957ce619789d13bb5779606078fa1498114d2c7`.
`python3 .ufo/waves/round-20/run.py --recipe .ufo/waves/round-20/recipe.json
--out .ufo/waves/round-20/runs/0957ce61` ran **21 commands**, all declared
exits met, harness exit0. Raw streams, exits, argv and SHA256 are retained in
that output directory; no live model server was launched.

| Claim | Axis/score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 finite named error regressions | calibration 7 → 7 | **15** pinned cells; misclassified **6 → 0**; frozen witness mismatches0, red-vector mismatches0, unrun0; frozen arm exits1, current arm0, pair0 | `python3 tools/error-verdict-census.py --arm frozen --json`; `--arm current --json`; `--json` | `runs/0957ce61/error-{frozen,current,pair}.stdout`; frozen source at 37bd4c5 |
| C2 offline GGUF declared identity / captured agreement | operability 8 → 8; new capability | tool absent at base → working reader; **23/23** independent fixtures pass; real-file oracle and receipt agreement pass, mismatches0/unavailable0 | `python3 .ufo/waves/round-20/c2/measure.py --json` | `runs/0957ce61/gguf-measure.stdout`; model version3, tensors48, KV19, declared2048 = captured training2048; props256 informational |

Supplementary routed repairs: citation registry **4 → 17** (13 reconstructed
revision/path instances, not all citations), all17 verified; citation selftest24
invocations, GGUF selftest30/30, measurement selftest7/7, survivor pure-classifier
checks49/49. Receipt gate6 VALID +1 NOT-EVALUATED, 77 mutations and unreadable
rejected. No-tree-pin grid remains0/3 rejected (exit1); six-pin grid3/3 (exit0).

### capabilities: append — first working round 20

| Name | What it can do | Demonstration | First-working round |
|---|---|---|---|
| gguf-declared-identity-replay | decode bounded local GGUF metadata offline, bind the file SHA to a captured v3 receipt and compare declared training/embedding/vocabulary metadata; not loaded-weight authentication | `python3 tools/gguf-identity.py /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --receipt .ufo/waves/round-18/live-recovery/receipt-1.json --json`; `runs/0957ce61/gguf-receipt.stdout` exit0; independent oracle/fixture measure above | 20 |

The three canonical round-16 capabilities remain; this adds one repertoire row.
Other scores held (freshness8, coverage9, depth7, adjacency7); score changes and
outside admission remain the non-author closure's decision. Capability window
resets by this working demonstration, not by source-row growth.

Planned: historical crash-as-kill leaves outside the 15-cell set, broader
receipt-header minimization, symlinked soname identity and K05/other-engine
serving evidence remain named frontier. No next round is started here.

### Round-20 correction — R18 C2 survivor output scope

The unqualified “they agree” at line 813 is limited by `corpus/lessons/round-18.md:474-480`: the pre-official JSON and official stdout agree on the 15 item outcomes, summary counts, frozen witnesses and 42 run-status tuples, not on the full documents. The R20 comparison found equal `.counts` but unequal `.results` and different `tool.sha256` values (`87cad1ca…` vs `ac934794…`). R20 did not rerun the full 42-run survivor counter.

### Round-20 fixture coverage boundary

The 23/23 figure at line 901 covers the predicates implemented by `c2/measure.py`, not every value in every fixture. `v3-all-scalars` carries 12 `test.*` scalar values in `expected.json`; the measurement compares identity keys/types, arrays, header fields, size and digest, not those arbitrary scalar values. C2 remains the bounded declared-identity capability; no general scalar-value recovery is claimed.

### Round-20 trend verdicts and prior-closure reconciliation

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | improved | One first-working offline GGUF identity capability is added at lines 909–918; this is a real capability surface, not source-row growth. |
| quality | improved | C1's 15-cell misclassification count falls 6→0 and C2's declared 23-fixture predicates plus oracle/receipt comparison pass; bounded by the fixture-coverage note above. |
| discernment | unchanged | No independent non-author R20 admit/reject sample. The prior R19 closure's two admits and one reject agreed, so it credited R19 discernment as improved after the author record was written. |

The R19 verifier also judged expansion unchanged at that time because R19 added
no knowledge/capability surface, contrary to the author's then-current
“improved (narrow)” wording; R20 expansion is improved for the new capability
row, not for source growth. See `corpus/lessons/round-19-verifier-spotcheck.md:160-172`.

### Round-20 fixture manifest correction

The partial `FixtureKvCount2pow40` review found stale local-tool defaults in
the generated fixture manifest. `make_fixtures.py` and regenerated
`tests/gguf-identity/expected.json` now record `--max-kv` 100,000 and
`--max-str` 1,048,576, matching `tools/gguf-identity.py:32-35`; the KV fixture
basis separately attributes the uint64 field to the pinned format text. The
23 fixture digests are unchanged (`SHA256SUMS` SHA-256
`ab51c80f26ce1c155f5b5e8377a6363df9fa93ff6ac1669000a9aaf70d995812`). No parser
behavior or C2 coverage claim changed.

### First post-manifest verification — failed closed

The run at `runs/c7311039` correctly failed `gguf-measure-selftest` and
`gguf-measure` (exit 2): the updated manifest hash
`714226dfb6ae578fb1718f6c19b76c1328cf9dfc74ced01e5f280b39bfeccd48` disagreed
with the old `c2/measure-reference.json` pin
`1ffe884a523fb85866ac43775fee0a5be1f69398c09a3dae8b8832f39c9f7f9f`.
`gguf-measure.stdout` marks all 23 fixtures `snapshot_tampered` and
`parser_attempted: false`; no C2 outcomes are credited from this run. The
reference pin is now updated to the exact manifest digest; this run remains
retained as failure evidence, not a passing measurement.

### Second post-manifest verification — failed closed

The rerun at `runs/04de7a87` reached the updated manifest but exposed a second
stale pin: `c2/measure.py` expected reference SHA-256
`fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6`, while the
updated `measure-reference.json` is
`e3f0349ab13cf08c7934d43c71a6ec27c7283150e90e39f3dd2d63f9be9c7bcb`. It exited
2 before fixture evaluation; no C2 outcomes are credited. The test-harness
constant is now bound to the exact current reference file, and this failed run
is retained separately from final verification.

### Corrected final measurement — clean tree 9add96e4

`python3 .ufo/waves/round-20/run.py --recipe .ufo/waves/round-20/recipe.json
--out .ufo/waves/round-20/runs/9add96e4` records measured commit
`9add96e462e62dc5141cd02730b7a699268b3513`: **21/21 commands met their declared
exits; harness exit 0**. C1 remains 15 pinned cells, frozen misclassified6 →
current0, no witness/red-vector mismatch and no unrun cell. C2 reports 23/23
fixture predicates, zero mismatches/snapshot tampering/unavailable rows, and
successful real-file oracle plus receipt agreement; this remains declared
metadata identity, not loaded-weight authentication or arbitrary scalar-value
recovery.

The post-S065 census is rows57→65: tier A54→62/C3; mined46→52, queued5→6,
rejected6→7, missing0. Validation/census both exit0; six W04 duplicate-URL
warnings (S031/S043/S056/S060/S064/S065) are explicit. Exact streams and exits
are retained under `runs/9add96e4/`.

## Round 21 — report landing audit and soname-aware install identity

Assigned axes operability 8 + calibration 7 (`../shokunin.conf`); calibration
is the lowest non-retired assigned axis, below saturation 8, so no stagnation
waiver. Round start `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d` (round 20
admitted by CloseKama20). Lesson: `corpus/lessons/round-21.md`.

### Round-21 measured results — clean committed tree b76727f3

`python3 .ufo/waves/round-21/run.py --recipe .ufo/waves/round-21/recipe.json
--out .ufo/waves/round-21/runs/b76727f3` on measured commit
`b76727f31e522763ce24e43d6ec86d21b507a11f`: **28/28 commands met their declared
exits**, harness exit 0 (`runs/b76727f3/commands.json`).

| Claim | Axis/score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 report landing audit (detector) | calibration 7 → 7 | instrument absent at round start (`git cat-file -e 7a6bc911:tools/report-landing-audit.py` exit 128) → 9 defects detected over the 11 reports of rounds 10–20 (1 unresolved full hash r20; 8 landed omissions r10×1, r18×3, r20×4), 42 required / 4 post-report commits, each hand-confirmed by an independent build-seat recount (0 FP, 0 FN); ledger run corrected 9, uncorrected 0 (bookkeeping, not the credited move); selftest 32/32 | `python3 tools/report-landing-audit.py --rounds 10-20 --no-errata --json` (exit 1) and `--rounds 10-20 --json` (exit 0) | `runs/b76727f3/c1-audit-{raw,ledger,selftest}.stdout`; `build/advice/AuditReport1{0..9}.md`, `AuditReport20.md` |
| C2 soname-aware install identity | operability 8 → 8 | real b11755 tree, 19 cells: frozen arm (install_tree at 7a6bc911) link 0/13, subdir 0/1, regular 3/3, type 1/1, null 0/1 → current link 13/13, subdir 1/1, regular 3/3, type 1/1, null 0/1, real tree gate-clean; `install_tree_sha256` unchanged (6c216313…); gate selftest 6+1/77 → 11+1/91; live v3 receipt with 10 links (`5cb9f486…`) VALID pinned with `--require-install-links`, INVALID on a wrong links pin; three R18 legacy receipts VALID, INVALID under `--require-install-links` | `python3 tests/llamacpp-live/install-links-grid.py --arm frozen --json` (exit 1), `--arm current --json` (exit 0), `--arm both --json` (exit 1) | `runs/b76727f3/c2-*.stdout`, `runs/b76727f3/live-receipt.json` |

No-harm reruns in the same recipe: error-verdict census pair/selftest, install-tree
grid selftest, GGUF selftest and capability measure, citation provenance and
selftest, SOURCES append-only guard (9 appended rows, no violations), snapshot
selftest (RESULT pass=30 fail=0), census validate/census — all at their declared
exits. Other scores held: freshness 8, coverage 9, depth 7, adjacency 7.

Sources: census rows 65 → 74 (A 62 → 70, B 0 → 1, C 3; mined 52 → 60, queued
6 → 7, rejected 7), validate exit 0; S066–S069 ground C2, S070–S073 ground C1,
S074 queued.

Capabilities: no row added. C2 hardens the existing live-receipt capability's
install pin (wave-1 CapabilityRuleReader); C1 is a calibration instrument, not
new serving repertoire. Capability window: 1 of 4 rounds since round 20's row.

Planned: obtain the outside non-author round-21 spot-check; remaining frontier —
historical crash-as-kill leaves, receipt-header minimization, system-library
(outside-directory) identity, K05/other-engine serving evidence, and an
unreadable-member fail-closed rule for `install_tree` consumers outside the
live producer. No next round is started here.

## Round 22 — install_tree helper error/identity separation

Declared C1 calibration **7 → 7**, the lowest assigned non-retired axis
(operability8); no stagnation waiver. Round-start branch master:
`10271460cc575fc2280aa831e442726385fc2319`.

Before: raised listing errors return an empty/null pair; raised stat/hash
errors silently omit a member from a comparable digest. After criterion:
the bare helper explicitly refuses each activated OSError before returning
a comparison result, while successful map/digest and non-OSError propagation
remain unchanged. Counting command:
`python3 tests/llamacpp-live/install-io-grid.py --arm both --json`.
The measured revision/counts are appended after the official clean-tree run.

This works the existing calibration gap, not a new capability. The producer's
existing two-helper backstop is not claimed as a new improvement; historical
receipt schema, intentional symlink/nonregular exclusions and scan-time/race
limits remain. Sources S075/S076 and rejected remedy S077; motivating lesson
`corpus/lessons/round-22.md`. Other axis scores held. No capability row added;
window 2 of4 since round20.

### Round-22 correction of round-21 measured-record lag (D1)

The R21 table at lines1003–1023 is an earlier measurement, not its final one.
The final committed receipt
`.ufo/waves/round-21/runs/7054dba1/commands.json` names measured commit
`7054dba144ec04b0ffb3c427783f3ece85b5adc4`: **33 commands, zero mismatches**,
not the earlier b76727f3/28-command run. Counting command:
`python3 -c 'import json; d=json.load(open(".ufo/waves/round-21/runs/7054dba1/commands.json")); print(d["measured_commit"], len(d["commands"]), sum(not r["as_expected"] for r in d["commands"]))'`.
The outside CloseKama21 closure independently reran all33 successfully and
records the final grid21 cells (link13/13, subdir3/3, regular3/3, type1/1,
null0/1), gate12 VALID+1 NOT-EVALUATED/99 mutations, producer/e2e and
no-harm results (`../MANIFEST.json` rounds[406]). This is an appended record
correction, not a fresh R22 execution of the R21 live recipe.

### Round-22 final measured results — clean tree 6433390a

`python3 .ufo/waves/round-22/run.py --recipe .ufo/waves/round-22/recipe.json
--out .ufo/waves/round-22/runs/6433390a` measured committed branch tip
`6433390a5c8f4412c2410c114309ffced5c0572f`: **29/29 declared exits met**,
zero timeouts/mismatches, harness exit0 (`commands.json`).

| Claim | Axis/score | Before → after | Counting commands | Evidence |
|---|---|---|---|---|
| C1 helper I/O error/identity separation | calibration7 → 7; verified narrow improvement | faults18; explicit refusals0/18 → 18/18; null returns3 → 0; partial digests15 → 0; controls14/14 in both arms; current violations0 | `python3 tests/llamacpp-live/install-io-grid.py --arm frozen --json` (1), `--arm current --json` (0), `--arm both --json` (1 intentionally red frozen) | `runs/6433390a/c1-io-{frozen,current,both}.stdout`; frozen producer10271460/SHAcec67949, current SHA8c0dbb2b; population SHA5b38422c |

The frozen two-helper backstop refuses18/18 after the transient faults; no
new producer-level escape is credited. Gate selftest8/8; five actual-producer
mutants killed with clean/restored positives (`residual/FinalMutations/`).
The error-detail suffix is informational, not graded; first-file diagnostic
grammar change and scan-time/race limits are explicit in the knowledge entry.

No-harm: install-links grid current21 cells all expected (links13/13,
subdirs3/3, regular3/3, type1/1, null0/1), gate12 VALID+1 NOT-EVALUATED/99
mutations+unreadable, producer selftest, three R18 legacy receipts, GGUF23/23
with real-file oracle/receipt agreement, citation17/17, error census current
misclassified0/unrun0, snapshot30 pass0 fail, and prelaunch refusal3/3 all
meet declared exits. No live model server launched or registered consumer
sampled; this is capability reliability/calibration, not a new repertoire row.

Source census command `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`:
rows74→88, A70→83/B1→2/C3, mined60→72/queued7→8/rejected7→8, missing0;
validate exit0 with20 W04 duplicate-URL warnings. Actual absolute argv/streams
are in the recipe receipts. Both consecutive source-touching commit-pair
guards pass; S075–S080 used-by changes are logged in the lesson.

Trends: expansion **unchanged** (no new entry/capability); quality **improved**
(measured helper gap and sourced corrections); discernment **improved**
narrowly because prior outside D2/D4 feedback became grounded KQ31/KQ32,
not because author-dispatched review is outside attestation.

Planned: keep the remaining receipt-header, historical crash-as-kill,
external-library/loader identity and K05/other-engine frontier explicit;
trusted-repo audit hardening and richer diagnostics are not acquired here.
Await outside R22 admit/reject sampling. No next round is started.

### C1 calibration — final report conformance component

The same axis also needs to distinguish a curated source-URL occurrence
from an owned commit citation when pasting mandatory source-census output.
The old report checker would reject the upstream40-hex in those URLs
([INFERENCE] before the fixed-input witness executes). C1 therefore includes
this independently measurable conformance repair, with score still7→7:
`python3 .ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py`
must observe old exit1/one false owned-hash finding → current exit0/zero,
while preserving real bare/Landed/omission findings. This is not a new axis,
source-validity guarantee, serving capability or D4 security hardening.
The original helper32-cell and29-command results remain unchanged; final
committed-tree followup counts are appended after measurement.

### Final scoped committed-tree measurement — 80a6d07c

`python3 .ufo/waves/round-22/run.py --recipe
.ufo/waves/round-22/report-source-fix/recipe.json --out
.ufo/waves/round-22/report-source-fix/runs/80a6d07c` measured
`80a6d07c09593191b7a6f86d92851fe3cc0619c2`: **10/10 declared exits**,
zero timeouts/mismatches, harness0. This is a scoped later run, not a claim
that the earlier29 commands reran on this tree.

| C1 calibration component | Before → after | Counting command / observed verdict | Evidence |
|---|---|---|---|
| Owned-commit versus registered-source URL classification | one false owned-hash finding → zero on the same pinned census report; old1 → current0 | `python3 .ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py`: red-green-match/0, failures[] | `report-source-fix/runs/80a6d07c/source-witness.stdout`; old script SHA80a58825…, current09ecd63b…, manifest SHA499442f1… |
| Existing helper component, no harm | current remains18/18 refusals,14/14 controls,0 null/partial/violations | `python3 tests/llamacpp-live/install-io-grid.py --arm current --json`:0 | `io-current-noharm.stdout`; source8c0dbb2b…, population5b38422c… |

Audit selftest **50/50**; witness CLI selftest **6/6**, including tampered
inputs, genuine old-as-current mismatch and child-error CNE. Historic
rounds10–21 still yield exactly9 raw defects, all9 corrected by the unchanged
ledger; uncorrected0, invalid0, unmatched0, required49/post-report5 over12
reports. Citation17/17 remains clean. Final census/validate again0 at88 rows;
SOURCES immutable data/rows unchanged since6433390a.

Final C1 author verdict remains **verified**, calibration7→7, no observed
axis harm. No new capability; trends remain expansion unchanged, quality
improved, discernment improved through learned outside feedback. The
registered-URL classification is not upstream-source validation or D4
untrusted-repository hardening.

## Round 23 — repository-local git state and the auditor's exit class

Declared claim C1, **calibration 7 → 7** (narrow; lowest assigned
non-retired axis), sourced on S089–S101. Round base `4fe9339f`; code measured
at `e876b953e9da28d2dffd29c923052bc626148c27` (auditor sha256 `da5041a8…5af1`, grid population
`f29fab8d…364a`). Frontier **D4 partially advanced**: report-audit
repository trust on the graded rows only; KQ32's trusted-repository-only use
stays in force, KQ34 governs credit.

| C1 component | Before (frozen `4fe9339f`) → after (current) | Counting command | Evidence |
|---|---|---|---|
| Repository-local fault rows met (crash/flip/hang/execute → typed refusal or correct verdict) | 0/26 → 26/26; tracebacks 9 → 0, executed programs 3 → 0, timeouts 2 → 0 | `python3 tests/report-audit/repo-state-grid.py --arm both --json` (exit 1: frozen red by design) | `corpus/lessons/round-23.md` §Falsify-wave integration; `.ufo/waves/round-23/final/grid-both.json` |
| Contract rows (declared contract changes) | 1/4 → 4/4 | same | same |
| Controls (no-harm on unfaulted and inert states) | 13/13 → 13/13 | same | same |
| Isolation elements killed by a named row | 22/24 killed (245a37f) → 30/31 killed on a named row; survivor M20 defensive-only | `python3 tests/report-audit/isolation-mutants.py --json` | `.ufo/waves/round-23/final/mutants.json` |
| Existing selftest / historical ledger, no harm | 50/50 → 50/50; rounds 10–22 ledger and `--no-errata` byte-identical to frozen (exit 0 / exit 1, 9 raw defects all corrected) | `python3 tools/report-landing-audit.py --selftest`; recipe line `nh-history-parity` | `.ufo/waves/round-23/final/` |

Not 26 independent isolation wins: F17/F21/F23/F24 are contract changes and
several rows pin current's own refusal wording (CritFrozenFairness); the
catch-all alone removes every traceback (CritSeparabilityW2). Operability
is **traded, not unchanged**, on two declared states: a complete blobless
partial clone (T01) and a paired promisor pack without promisor config (F23)
now refuse (exit 2) where frozen gave a verdict; git ≥ 2.45 is required.
Open, both arms: alternates/gitfile redirect, `--shared`-of-partial bypass,
second Landed section, ambiguity overwrite, errata CR, `--errata` FIFO,
memory ceilings, near variants named in the lesson, unisolated sibling gates.

Trend verdicts: expansion **unchanged** (no new knowledge entry or
capability; one entry deepened, 13 source rows); quality **improved** (KQ34,
superseding rows for three defective source rows); discernment **improved**
(falsify findings turned into graded rows, corrected counts and a rejected
source row).

**Planned — supersedes earlier planned statements:** outside non-author
closure of r23; then either close the open near-variant channels one graded
row at a time or bound the auditor's input sizes, and decide with the
operator whether the T01/F23 trades stand.

## Round24 — authority and declared repair

Outside closure rounds[428] supersedes the round23 author's admission and
quality-improved readings: rejected-harmed, calibration improved but
operability/quality harmed. The historical measurements above remain filed;
disclosing a trade did not make it admissible.

Declared C1 calibration7→7 (lowest assigned non-retired axis): distinguish
metadata from actual local evidence availability, restoring justified
correct verdicts without allowing acquisition or guessed unavailable data.
The initial registration's blanket unknown-citation expectation is
withdrawn/not-achieved, not retroactively passed. Its original view stays
in `.ufo/waves/round-24/preregistration.json` and
`tests/report-audit/promisor-grid-expectations.json`, alongside the
prospective correction `.ufo/waves/round-24/oracle-amendment-1.json` and
`.ufo/waves/round-24/oracle-supplement-2.json`.

Integration is pinned at `ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05`;
the comparable quantitative record is the amended47-cell target, not the
frozen-history reproduction column. Final measurements are separate
committed-tree evidence after fresh falsification; this declaration does
not claim that those runs have occurred. No numeric promotion or new
capability. The Git>=2.45 prerequisite remains an unresolved R23-H2
operator decision, not older-Git restoration.

### Round24 final author record — original claim not achieved

The fixed algorithm epoch is `92063cfc60e217fa7e2098c568578119b16a1b95`.
This append is a later documentation/record correction, not a repaired
algorithm or a new measurement at that epoch. C1 remains calibration
**7 → 7**, with no promotion or author admission. The full original after
claim is **NOT ACHIEVED / unprovable in full**; the withdrawn unknown-citation
clause remains false, not relabelled as success.

| Record | Before → after / actual scope | Counting evidence and limitation |
|---|---|---|
| Primary amended oracle | Earlier loose16/47 and stricter14/47 are distinct prior-producer observations; final recorded cohort covers47/47 amended cells | `final/distributed-primary-count-v2.json` reads existing W3 captures bound to the fixed auditor/grid/oracle identities. It is NOT a new single full paired grid run, a common-producer before/after measurement, or fulfillment of the promised full measurement plan. |
| Original view | Seven primary expectations remain unmet: PG22/23/24/28/30/34/41 | Original fields, immutable47 expected bytes and twin links remain unchanged. Five concern the literal unknown clause; the other two are disclosed prospective corrections, not extra evidence for that clause. |
| Six generic consumers | 0/6 strict declared-field matches at2e → 6/6 at92063; all six retain red-before evidence | `final/recorded-consumers.json` independently counts existing replay-v3 records, comparing exit AND exact kinds AND errata_invalid, with no-ledger controls separate. Supplemental, not six additional primary cells or a full-domain execution. |
| Bounded mutation observations | Nine of ten sampled executable operators have a named failed graded row; canonical PM07 survives its finite sample | `final/bounded-mutation-record.json`; not a full ten-operator ×47 sensitivity run. PM08 is manual/unexecuted/uncredited, and same2→2 diagnostic loss is not acceptance. |
| Source census | 101→105 rows; A96→100/B2→2/C3→3; mined84→86, queued8→8, rejected9→11 | Actual current census/validate exit0 in `final/sources-census.json`; four new A rows, eleven old used-by-only edits, no immutable old-cell change in `final/source-transitions.json`. |

Every original clause is judged in
`.ufo/waves/round-24/final/full-original-after-judgment.json` and the final
lesson: finite metadata/omission/required-object/local-policy controls
support bounded statements; the global acquisition/isolation/deadline
clause is unprovable; r23 corrections do not certify all40 retained process
rows as FIFO-tied identities. No fresh final-epoch full both-arm grid,
legacy population, selftest/parity or default sensitivity confirmation was
performed. Prior preliminary runs are not promoted into those missing runs.

W1/W2/W3 each actually spawned64, all192 returned durable reports; none
died. W3's captured bindings are m_mim61/m_auto3, retained as observed.
Grants and terminal counts are not continuous active-floor, whole-host
no-effects or absence-of-chain certificates. The VOID80 canonical-write
incident, private evidence edits, out-of-scope samples, hydration changes
and oracle chronology limits remain disclosed. H2 is unresolved/unapproved;
universal pre-inspection chronology is not proved. Final author trends:
expansion unchanged; quality harmed by the provenance/conformance breach
despite bounded functional recovery; discernment unchanged at the held7.
Only fresh outside closure may decide admission.

## Round 25 — registered instrument re-anchor and declared versus served context capacity (2026-10-22, attempt 2)

Two declared claims (preregistration `.ufo/waves/round-25/preregistration.json`,
amendments 1-4). Attempt 1 was stood down for capacity; attempt 2 is a fresh
author. Measured commits are lane branch tips named per row.

| Claim | Axis, score | Before → after | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 (repair-first) | calibration 7 → 7 (no promotion) | `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` at efe58e96 → `registered 28 stale 0 []` | preregistration.json C1.command (enumerates the whole MUTANTS list) | 1fc41e346853afd98cbd7010af5db4e54dc877f7 (instrument unchanged since, except its docstring) | supporting full run `.ufo/waves/round-25/final/c1/c1-tip-mutants.json`: exit 0, pristine passed, 28 mutants, 26 killed, survivors M17 and M20; lesson `corpus/lessons/round-25.md` §C1 |
| C2 (learning claim, frontier K05) | coverage 9 → 9 (no promotion) | no receipt (counter exits 2, prints no count) → `registered 14 observed 14 bound True missing []` | `python3 .ufo/waves/round-25/count-c2.py` (amendment-4 bytes) | receipt 5c95c8f111a981e316cd4933e38fc363e51f8604 | `.ufo/waves/round-25/final/context-capacity-receipt.json` with 70 raw files; entry `corpus/knowledge/context-capacity.md`; SKILL.md §Round-25 decision rows |

Erratum: the preregistration wrote C2's axis as "coverage 8 -> 8"; the
lane's current coverage reading is 9 (SCORECARD lines 562 and 1019). The
claim makes no numeric move either way.

C1 axis fit, filed verbatim from non-author critic seat KamaR25a2.CriticC1Calibration
(`.ufo/waves/round-25/a2-build/advice/CriticC1Calibration.md`):

> C1's measured instrument repair is registered 27 stale 2 → registered 28 stale 0, with no removed or reused ids; M33 separately covers the second call site of the existing ref-shadow refusal. This counts instrument-to-auditor anchor mismatches, not demonstrated SCORECARD/SHONEN self-assessment mismatches. SCORECARD line 1166 is a historical round-23 measurement and remains historical. Calibration-axis fit is therefore not established; no calibration claim success or promotion is asserted. The before command aborts on reaching M11, after earlier mutants have run, and emits no completed JSON report. This repairs only the M-series portion of routed defect 2; PM08 remains outside the claim.

The author's position: the SCORECARD row registers that command as the
lane's re-derivation path, and the lane's live SKILL registry row
(`SKILL.md` "Retained isolation mutation experiment") promised an evaluated
inventory the command could not deliver. That is a reading, not a proof; the
closure decides the axis fit. The author does not relabel the axis.

Correction after the falsify wave (non-author critic KamaR25a2.CriticC1AxisFit,
`.ufo/waves/round-25/a2-falsify/advice/CriticC1AxisFit.md`): the author's
position does not hold. At the before revision the SKILL row's verdict map
already registered exit 2 as could-not-evaluate, its "27 retained literals"
was true, and SCORECARD line 1166 was true at its bound auditor (the counter
prints `stale 0` at e876b95). The anchors went stale at round-24 commit
92063cf, after the registry text was written at ed1cc3a: drift, which AXES
files under freshness, not overreach. The author accepts this. **C1's axis
fit to calibration is not established**, so this round does not show the
lowest-axis obligation (calibration 7; depth and adjacency also 7; no
stagnation waiver, calibration is below the saturation line 8). The measured
value stands as repair evidence. In the quoted critic text above, "the before
command aborts" refers to the full instrument run (exit 2 on reaching M11);
the counting command itself exits 0 and prints `registered 27 stale 2`.

M17 survival: since round-24 commit 92063cf no caller reaches the
`lookup()` refusal, so M17 survives and grid row F13 now kills M33
(`.ufo/waves/round-25/a2-build/advice/RevengerM17Sites.md`, causal run on
ed1cc3a). This is reported, not hidden (KQ36).

### capabilities: append — first working round 25

| Name | What it can do | Demonstration | First-working round |
|---|---|---|---|
| context-capacity-receipt | run the 14 registered context-capacity cells on the lane-owned llama.cpp fixture (b11755, stories260K.gguf), one child at a time on unregistered loopback ports, and write a receipt with per-slot value, slot count, KV pool from the verbose log, request outcomes and the sha256 of every raw response and log; a cell counts only after its child is reaped and its port closed | `python3 tools/kama-context-capacity.py --out .ufo/waves/round-25/final/context-capacity-receipt.json` exit 0 (2026-10-22T09:42:42Z to 09:42:50Z), then `python3 .ufo/waves/round-25/count-c2.py` → `registered 14 observed 14 bound True missing []`; not registered-consumer serving | 25 |

Other scores held: operability 8, freshness 8, depth 7, adjacency 7.
Sources: census rows 105 → 113 (A 100 → 108; mined 86 → 94), validate exit 0.
Trend reading by the author: expansion improved (one entry on uncovered
ground, one capability), quality unchanged-to-improved (routed wording and
count corrections, KQ36), discernment improved (five attack findings turned
into stricter counters, scoped claims and a filed axis dispute). Outside
closure alone decides admission.

## Round 26 — live error signatures on the serving runtime (2026-10-23)

One declared claim (preregistration `.ufo/waves/round-26/preregistration.json`,
pre-data amendments A0 and A1). Lowest axes at the start: depth, calibration
and adjacency, all 7. The rejected streak (rounds 23-25) worked calibration and
the report-landing auditor (round 25's C2, verified on coverage, already worked
this serving runtime); this round works depth on the serving runtime.

| Claim | Axis, score | Before → after | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 | depth 7 → 7 (no promotion: after data a shortcut control also met the frozen counter, 12/12 with no error knowledge; lesson §Mistakes row 3) | `registered 0 counted 0 target 12 met False` at base 1560e4d8 → `registered 17 counted 17 target 12 met True` | `python3 .ufo/waves/round-26/count-c1.py --out <receipt.json>` (counter sha256 6501737c…6588, unchanged since a23c0e04) | receipts name their tree: `final/c1-tip.out` (7e5ff9b5) and `final/c1-final-tip.out` (the final landed tip) | SKILL.md "## Round-26 live error signatures" (E26-01 to E26-17), `registry/error-signatures-r26.json`, SOURCES S114-S130, lesson `corpus/lessons/round-26.md` |

Surface moved: the SKILL.md error-signature table for the live b11755
runtime. Before this round SKILL.md held the September sample
("Historical error signatures") and two live b11755 signatures (the
`Loading model` 503 at base SKILL.md:521-523 and the round-25 `Context size
has been exceeded.` 500 at :689), and none of the 17 E26 strings.
(Corrected before the report; the first landed text said SKILL.md held only the
September sample, which wave-2 seat ReviewerScorecardLogTruth showed false.) The command that would show it unmoved
is the same counter at base (counted 0). After data, wave-2 critic
CriticShortcutRows met the frozen counter from the base tree with 12 echoed
non-error literals (`registered 12 counted 12 target 12 met True`), so the
counter does not by itself discriminate the claimed work; the 17 rows rest on
the per-row wave-2 attacks, which found none of them of a shortcut type. The
pre-freeze shortcut control had been refused by the provider and the L1 did
not replace it before data. Known counter limits found after data
(warning lines, decoded echoes, file-content echoes, the 19-row port limit)
are listed in the lesson and were not repaired this round.

Repairs (routed by the round-25 outside spot-check, not claims): defects 1-7,
lesson §Routed defects. `.ufo/waves/round-25/count-c2.py` now binds raw
hashes; KQ36 re-run at the landed tip is in the round report.

### Round 26 correction — round-25 trend verdicts (routed defect 6)

The round-25 trend line above ("quality unchanged-to-improved",
"discernment improved") conflicts with the round-25 report
(`.ufo/reports/round-25/kama.md:120-129`: quality unchanged, discernment
unchanged) and the outside closure (`corpus/lessons/round-25-verifier-spotcheck.md:187,194`).
Corrected round-25 trend verdicts: expansion improved, quality unchanged,
discernment unchanged. The earlier bytes stay as written.

Other scores held: operability 8, freshness 8, coverage 9, calibration 7,
adjacency 7. Capabilities: no row claimed; `tools/prereg-time-check.py` is the
mined-mistake check, demonstrated in the lesson, not claimed as a capability.

### Planned (round 27)

Register a stricter error-signature counter (per-row healthy control with the
same argv, decoded-request and file-content echo checks, port reuse) before
data, then land the held-back confirmed signatures (lesson §Gate, rejected
table). Work calibration or adjacency (7) if depth moves.

## Round 27 — echo-discriminating counters (calibration, exploratory); C1 miss; round-26 repairs (2026-10-23, attempt 3)

| Claim | Axis | Before → after | Verdict | Evidence pointer | Counting command | Measured commit |
|---|---|---|---|---|---|---|
| C1 (measured) | depth | 7 → 7 | **miss** (honest stop): withdrawn before data, no data seat dispatched; under the frozen kill rule counted < 15 at the landed tip is a miss | `.ufo/waves/round-27/a3/plan.json`; lesson `corpus/lessons/round-27.md` §Claims; tip receipt `.ufo/waves/round-27/a3/c1-tip.out` | `/usr/bin/python3 .ufo/waves/round-27/count-c1.py --out <receipt.json>` (preregistration.json C1.command) | `d183ec57` (receipt `.ufo/waves/round-27/a3/c1-tip.out`: registered 0 counted 0 target 15 met False; later round-27 commits change no file the counter reads for C1 rows) |
| X1 (exploratory) | calibration | 7 → 7 (no number) | `unprovable` until a named non-author reviewer rules; wave seats are evidence only | `corpus/knowledge/echo-discriminating-counters.md`; `corpus/QUALITY.md` KQ37 and its round-27 qualification; lesson §X1 evidence | none (exploratory) | — |

Surface moved by X1: the lane's claim-measurement method for error-signature
counters (a knowledge entry and an admission criterion), not a new server
error signature. Prior state: the round-26 counter's echo test read stored
request text (round-26 `count-c1.py:384`), a base-tree shortcut met it 12/12,
and QUALITY.md held no echo rule; the round-26 preregistration and spot-check
named the echo and split-message classes as round evidence only.

Repairs (routed by `corpus/lessons/round-26-verifier-spotcheck.md`, not
claims): defects 1, 3, 4, 5, 6, 7 repaired; defect 2 met by the A3 counter and
KQ37 with the shortfalls recorded in the entry (its "receipt per class before
data" leg only vacuously: no data seat ran); defect 8 (`count-c2.py` reads
cell values from the receipt) open. Details: lesson §Repairs.

Calibration note: this round's own first landed texts carried four errors
that wave seats caught (LOG correction miscount, S136 escape wording,
"neither meets nor misses", 1853 vs 1846). LOG.md and SOURCES.md were
corrected by appended entries and a superseding row; the round's own lesson,
knowledge entry and this section were revised in place before the report
(lesson §Mistakes and §Gate list each change). A non-author self-assessment
check at `52632caa` found 1 mismatch in 57 statements (this row's measured
commit, now fixed; `residual/advice/ReviewSelfAssessment.md`).

Other scores held: operability 8, freshness 8, coverage 9, adjacency 7.
Capabilities: none claimed.

### Planned (round 28)

Repair defect 8 (`count-c2.py` cell trust). If depth is worked again, the
counter must meet KQ37 with its round-27 qualification (boundary leg, Unicode
case folding) and carry committed non-author control receipts per class
before any data seat.

## Round 28 — request-field outcomes on the serving runtime (depth); round-27 repairs (2026-10-23, attempt 1)

One measured claim. Lowest axes at the start: depth, calibration and adjacency,
all 7 (round-27 section). Preregistration
`.ufo/waves/round-28/preregistration.json` (A0 frozen `d8bf1804`, amendment A1
`75b78bb4` before any data row landed but after data seat DataG01 had checked
its drafts with A0 counter functions at 08:35:54Z; reasons and the correction
in the lesson).

| Claim | Axis, score | Before → after | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 (measured) | depth 7 → 7 (no promotion by the author: under the rule frozen before data, A0, a type-only control also meets the counter, 20/52; A1, which refuses it, was written after a data seat had checked drafts with counter functions; closure rules) | `registered 0 counted 0 target 18 met False` at base 4179301f (`before/c1-base.out`) → `registered 34 counted 26 target 18 met True` (8 rows not counted: `e:generic-conversion`) | `/usr/bin/python3 .ufo/waves/round-28/count-c1.py --out <receipt.json>` from a fresh clone of the lane remote (counter sha256 a38faefe…49a5, A1) | `e49b4cf7` (`.ufo/waves/round-28/final/c1-e49b4cf7.out`; A0 counter on the same tree: 34/34, `final/c1-A0-e49b4cf7.out`) | SKILL.md "## Round-28 request-field outcomes" (F28-01..F28-34), `registry/request-field-outcomes-r28.json`, SOURCES S140-S173, lesson `corpus/lessons/round-28.md` |

Surface moved: SKILL.md gains a decision table for llama-server's request-field
schema (`tools/server/server-schema.cpp` @704366d76) on the lane fixture:
which fields reject an out-of-range value with HTTP 400 and their hard bounds,
which clamp silently and to what, and which handlers transform the value
(`lora`, `logit_bias`, `ignore_eos`, `stop`, `samplers`, `preserved_tokens`).
Before this round no lane document named server-schema.cpp, `set_hard_limits`
or the bounds message (`.ufo/waves/round-28/w1/out/ScoutProvince/grep-hits.txt`).
The command that shows it unmoved is the same counter at base (counted 0).
Controls: pre-freeze evidential maximum 14 (source-blind, A0); the type-only
conversion policy built after data meets A0 (20/52) and not A1 (0/52); re-scored pre-freeze fixtures at most 9, a fixed
README-and-names policy 11/38 (`controls/`, `controls-A1/`). Five pre-freeze
control seats are holds (`controls/HOLDS.md`). Limits: one fixture build,
model and argv; one request per field; "200, key = value" is the stored
setting, not sampler effect; `n_cmpl`'s bound depends on `n_parallel`.

Repairs (routed by `corpus/lessons/round-27-verifier-spotcheck.md`, not
claims): defects 1-7, lesson §Repairs. Mined mistake: lesson §Mistakes.
Other scores held: operability 8, freshness 8, coverage 9, calibration 7,
adjacency 7, depth 7. Capabilities: none claimed.

### Planned (round 29)

Work calibration or adjacency (7). Candidate: the other endpoints'
request-field handling (`/v1/chat/completions` parameters mapped onto the
same schema) and the json_schema → grammar transform, with the A1 rule kept.

## Round 29 — self-assessment corrections

Appended by the kama L1, round 29, after the frozen counter (`.ufo/waves/round-29/count-c1.py`,
sha256 fe11d599…7383, frozen at `827d1365`) and its control receipts (`35b90184`) landed. Each row
names one base statement (SCORECARD.md/SHONEN.md at `2aa46e24`) that was false at the commit that
wrote its line (W, from `git blame --line-porcelain`), and states what the check observed there.
The original lines stay as written. Causes were read by the L1 from the lines and W; the wave-1
Confirm seats check each one independently (`.ufo/waves/round-29/w1/out/ConfirmM01..11/`).

| id | line at base | class | statement token | W | cause | observed |
|---|---|---|---|---|---|---|
| SA29:SCORECARD.md:Q:f4c42debcc:0 | SCORECARD.md:20 | Q | `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` | ea72c3ea | quoted as live re-census output; no committed file at W holds this line | q:no-artifact |
| SA29:SCORECARD.md:Q:f4c42debcc:2 | SCORECARD.md:20 | Q | `RESULT pass=24 fail=0` | ea72c3ea | test-snapshot result quoted; at W no committed file held it (a later commit does) | q:no-artifact |
| SA29:SCORECARD.md:P:980355388a:0 | SCORECARD.md:192 | P | `MISSION.md` line 29 | 1e41928a | names the fleet file ../MISSION.md (line 29 is the kama row); no lane path MISSION.md | p:absent |
| SA29:SCORECARD.md:Q:4f8083e30a:0 | SCORECARD.md:211 | Q | `rows=50 resolved=48 terminal=2 unresolved=0` | 40660352 | quoted audit result; no committed file at W holds this text | q:no-artifact |
| SA29:SCORECARD.md:P:312b3e69b1:0 | SCORECARD.md:740 | P | `round-17-verifier-spotcheck.md` lines 217–221 | c6dc46fa | bare file name; the lane file is corpus/lessons/round-17-verifier-spotcheck.md | p:absent |
| SA29:SCORECARD.md:Q:0ccd533544:0 | SCORECARD.md:823 | Q | `required=3 found=0 verified=0 missing=3` | 7229fa95 | quoted citation-provenance before-run; no committed file at W holds this text | q:no-artifact |
| SA29:SCORECARD.md:Q:4c5d902830:0 | SCORECARD.md:824 | Q | `required=3 found=3 verified=3 missing=0 mismatch=0` | 7229fa95 | quoted citation-provenance after-run; no committed file at W holds this text | q:no-artifact |
| SA29:SCORECARD.md:Q:f1021c03db:0 | SCORECARD.md:833 | Q | `baseline=VALID members=3 rejected=0/3` | 7229fa95 | quoted gate output; no committed file at W holds this text | q:no-artifact |
| SA29:SCORECARD.md:Q:a7e98b1030:0 | SCORECARD.md:834 | Q | `baseline=VALID rejected=3/3` | 7229fa95 | quoted gate output; no committed file at W holds this text | q:no-artifact |
| SA29:SCORECARD.md:P:1c6c1f3e4c:0 | SCORECARD.md:1349 | P | `.ufo/reports/round-25/kama.md` lines 120–129 | 7f84cd0e | a fleet-repo report path written as if lane-relative | p:absent |
| SA29:SCORECARD.md:P:17a7db7c81:0 | SCORECARD.md:1375 | P | `count-c1.py` line 384 | d183ec57 | bare file name; the lane file is .ufo/waves/round-26/count-c1.py (line 384 exists there) | p:absent |

## Round 29 — self-assessment evidence at writing (calibration); round-28 repairs (2026-10-23, attempt 1)

One measured claim. Lowest axes at the start: depth, calibration and adjacency, all 7
(round-28 section); calibration is the lowest assigned axis (`../shokunin.conf:52`).
Preregistration `.ufo/waves/round-29/preregistration.json`, frozen at `827d1365` before any seat;
control receipts `35b90184` before any correction row (`.ufo/waves/round-29/controls/SUMMARY.md`).

| Claim | Axis, score | Before → after | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 (measured) | calibration 7 → 7 (no promotion by the author; closure rules) | `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 2aa46e2481d2` at base (`.ufo/waves/round-29/before/c1-base.out`) → `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a` | `/usr/bin/python3 .ufo/waves/round-29/count-c1.py --repo <fresh clone of the lane remote> --tip <full commit> --out <receipt.json>` (counter sha256 fe11d599…7383; the preregistration's `--tip refs/heads/master` resolves only on a remote clone whose master is at the measured commit — pin the explicit revision) | `513eba3ba51a142c9936553e3a85918345eb5c4c` (`.ufo/waves/round-29/final/c1-513eba3b.out`) | §Round 29 — self-assessment corrections above; `corpus/knowledge/self-assessment-at-writing.md`; lesson `corpus/lessons/round-29.md` |

Surface moved: the lane's self-assessment evidence record. Eleven base statements whose stated
evidence did not resolve in the lane at the commit that wrote them (4 pointers: two fleet files,
two lane files cited without their directory; 7 quoted outputs not retained verbatim in a lane file
outside the self-report files) now carry appended rows saying so. What it does not show: that any
of the lane's past judgments were wrong. Wave-1 critic CriticAxisFit found the judgments behind
lines 740 and 1375 true at W, and Q failures show missing retained output, not wrong values; the
author accepts that reading (lesson §Claims). Controls: none meets the target (closest: text-only
prediction, unresolved 9; base-tree check, unresolved 9); the reference policy that records the
check's observed values meets it by design. Limits: the extractor finds 69 of at least 141
checkable statements of its six classes (RecallA/B: 72 misses, 2 of them false at W, not
counted); the predicate is stated in two sentences plus the docstring's class rules, not one
literal sentence (CriticPredicateIdentity).

Correction to the cause cells above (ConfirmM02, ConfirmM04): where a Q cell says "no committed
file at W holds this text", read "no committed file at W outside SCORECARD.md, SHONEN.md, LOG.md and
corpus/"; the spans of lines 20 (RESULT) and 211 sat at W in LOG.md and
`corpus/lessons/round-10.md`. The observed cells are unaffected.

Repairs (routed by `corpus/lessons/round-28-verifier-spotcheck.md`, not claims): items 1-9,
lesson §Repairs. The round-28 A1 authoring record: preregistration text time "2026-10-23 ~08:45Z" is
wrong; the authoring record logs the A1 edit call at 08:37:23.720Z and its result at 08:37:23.732Z,
and commit `75b78bb4` is committer-dated 2026-10-23T05:38:16-03:00. Mined mistake: `tools/prereg-time-check.py` missed the round-28 A1 misdate; fixed
and shown able to fail (lesson §Mistakes). Other scores held: operability 8, freshness 8,
coverage 9, depth 7, adjacency 7. Capabilities: none claimed.

### Planned (round 30)

Work depth or adjacency (7). A depth re-claim meets KQ38 (credit only outcomes not predictable from
declared bounds or type rules; both shortcuts scored before any seat). The 72 extractor misses and
the line-824 "5 cases" prose mismatch are open calibration ground.

## Round 30 — self-assessment corrections

Appended by the kama L1, round 30, after the frozen counter (`.ufo/waves/round-30/count-c1.py`,
sha256 `c3f16ef1…9ce40d`, frozen at `fdf8cda1`) and its pre-data control receipts
(`.ufo/waves/round-30/controls/SUMMARY.md`, committed `14bb1a32`) landed. Each row names one base
statement the round-29 recall sweeps enumerated but the round-29 counter could not see; the round-30
counter re-derived its class check at the writing revision W. The original lines stay as written.

| id | line at base | class | statement token | W | cause | observed |
|---|---|---|---|---|---|---|
| SA30:SCORECARD.md:Q:4a6f7c911e:o0 | SCORECARD.md:41 | Q | `file=yes` | ea72c3ea | the round-29 extractor's Q rule required a digit; this span has `=` and no digit | q:no-artifact |
| SA30:SCORECARD.md:Q:422b431349:o0 | SCORECARD.md:901 | Q | declared2048 = captured training2048 | 92b14625 | not backticked at W; outside the frozen quoted-span rule | q:no-artifact |

Both spans were re-checked with `git grep -F` at W under the counter's four exclusions (exit 1 for
both): the quoted values are not retained in any committed lane file outside the self-report files.
This is the same bounded reading as round 29 — an evidence-resolution defect recorded, not proof
that the judgments behind the statements were wrong. Round-29 record correction (routed defect 5):
the round-29 appended note at SCORECARD.md:1490-1493 omits that the M02 span also sat at
`corpus/lessons/round-2.md:49`; the note's point stands.

## Round 30 — recall-population census (calibration) and run-agreement capability (operability)

Authority: assigned axes operability + calibration (`../shokunin.conf` kama row). Lowest axes at the
start: depth, calibration and adjacency all 7; C1 works calibration. Stagnation nudge inactive.
Preregistration `.ufo/waves/round-30/preregistration.json`, frozen at `fdf8cda1` before any seat;
pre-data control receipts committed at `14bb1a32`; data (the two SA30 rows above) at `4d498001`.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 (measured) | calibration 7 → 7 (no promotion by the author; closure rules) | `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 0 false_corrections 0 unresolved 13 met False` at base → `… valid_corrections 13 false_corrections 0 unresolved 0 met True` at the landing tip | `/usr/bin/python3 .ufo/waves/round-30/count-c1.py --repo <fresh clone> --tip <commit> --out <receipt>` (counter sha256 `c3f16ef1…9ce40d`, frozen at `fdf8cda1`) | the tip recorded in `final/c1-tip.json` (the round-30 landing commit) | `c1/before/c1-base.out`; `c1/before/c1-r29-tip.json` (rows-only arm: valid 11, unresolved 2); `final/c1-tip.out`; the two SA30 rows above; lesson `corpus/lessons/round-30.md` |
| C2 (capability acquisition) | operability 8 → 8, **new capability row** | tool absent at base (`git cat-file -e 2aa46e24:tools/instrument-agreement.py` exit 128) → selftest `IA_SELFTEST pass=4 fail=0` exit 0 with the nondeterministic arm `agree=2 disagree=1`, two receipts `IA runs=3 agree=3 disagree=0` | `python3 tools/instrument-agreement.py --selftest; echo SELFTEST_EXIT=$?` and `python3 tools/instrument-agreement.py --runs 3 --out <receipt> -- <instrument>` | `1d3e8ba4` (tool + selftest + first receipt) | `c2/selftest.out`; `c2/receipt-a.json` (`error-verdict-census.py --json`); `c2/receipt-b.json` (`sources-append-only.py --from 2aa46e24 --to 52ac3af --json`); `c2/receipt-b-corpusguard-refused.json` (the guard refused as a subject: staging-path digest) |

Surface moved by C1: the lane's self-assessment census. Before, its population was whatever its
extractor found (69 statements) and 72 further checkable statements were disclosed as invisible; now
the population is explicit (141), each of the 72 is classified at its writing revision by committed
instrument bytes, and the 2 that do not hold carry observed values. What it does not show: that the
extractor generalizes (its bytes are unchanged and still find 69 alone), or that any past judgment was
wrong. The command that shows it unmoved is the same counter at base (`oracle 0`, `unresolved 13`).

Surface moved by C2: the lane's instrument-reproducibility repertoire. Before, no lane tool could
state whether an instrument's output is reproducible across runs; now one can, with a fail-capable
selftest and receipts. What it does not show: that any instrument is correct.

### capabilities: append — first working round 30

| Name | What it can do | Demonstration | First-working round |
|---|---|---|---|
| instrument-agreement | run a lane instrument N times over one tree in isolated temp dirs, normalize only declared volatile fields, and emit a receipt with per-run exit/normalized-output digests and an `IA runs=N agree=A disagree=D` counter; refuse a stub that always agrees and an instrument whose deviations are undeclared | `python3 tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0` exit 0; `python3 tools/instrument-agreement.py --runs 3 --out .ufo/waves/round-30/c2/receipt-a.json -- python3 tools/error-verdict-census.py --json` → `IA runs=3 agree=3 disagree=0`; the corpus guard as a refused subject | 30 |

Other scores held: operability 8, freshness 8, depth 7, coverage 9, adjacency 7.
Sources: census rows 177 → 179 (S178, S179 opened this round, both own-work tier A), validate exit 0.
Trend reading by the author: expansion improved (one admitted knowledge entry on new ground, one
capability, two sourced rows); quality improved (KQ40; the corpus guard's path-dependent digest
refused rather than normalized away; three instrument defects found and fixed by their own receipts);
discernment unchanged-to-improved (14 control arms, no shortcut meets; the predicate's weakest term
named by an arm). Outside closure alone decides admission.

### Planned (round 31)

Work depth or adjacency (7). A depth re-claim still meets KQ38. Open calibration ground: the
extractor still finds only 69 of the 141 by itself (see the README frontier note); any statement
outside both populations remains invisible. C2's next step, if claimed, must name an instrument whose
volatile fields are declared in advance, never normalized after a disagreement.

## Round 31 — the chat-completions adapter (depth) and claim-row evidence (calibration)

Authority: assigned axes operability + calibration (`../shokunin.conf` kama row); lowest axes at the
start: depth, calibration and adjacency all 7. Stagnation nudge inactive. Preregistration
`.ufo/waves/round-31/preregistration.json`, frozen at `0e6f8ed6` before any seat; pre-data control
call (12 seats) committed at `3b1e84f8`; data in `54c6f4fe`.

| Claim | Axis, score | Before → after | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 (measured; **not admissible**) | depth 7 → 7 (no promotion: the frozen counter is met at the landed tip, but a do-nothing registry of twelve duplicate rows also meets it, so the counter cannot separate depth from a no-op) | registry and SKILL table absent at base (`count-c1.py` exits 2: no table) → `registered 18 counted 17 target 12 met True not-counted ['K31-10']` | `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane . --repo <scratch clone> --tip <full commit> --out <receipt>` (counter sha256 `d86c4a94…9216`, frozen at `0e6f8ed6`) | `54c6f4fe` (`.ufo/waves/round-31/c1/c1-54c6f4fe.json`) | SKILL.md "## Round-31 chat-completions parameter outcomes" (K31-01..K31-18); `registry/chat-param-outcomes-r31.json`; S180-S191; `corpus/knowledge/chat-adapter-outcomes.md`; lesson `corpus/lessons/round-31.md` |
| C2 (measured; **not met — counter defect**) | calibration 7 → 7 (no promotion) | `rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False` at base → `rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False` at the landed tip | `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo <scratch clone> --tip <full commit> --out <receipt>` (counter sha256 `2d06f38d…c6fe`, frozen at `0e6f8ed6`) | the tip recorded in `.ufo/waves/round-31/c2/c2-tip.json` | the corrections section below; `.ufo/waves/round-31/before/c2-base.out`; `.ufo/waves/round-31/controls/RefRepair/` (the reference repair also fails: valid 10 / false 3 / unresolved 3) |

Surface moved by C1: the committed corpus now holds the chat-completions adapter on the lane
fixture — 18 measured rows in four outcome classes (reject with the exact `{code,message,type}`
envelope, slot with the stored key/value from `/slots`, ignored with a zero slot delta and an
unchanged normalized response, response with one of four response-contract facts), each bound to a
pinned `server-common.cpp`/`server-schema.cpp` line at 704366d, plus the knowledge entry that states
the mapping and the observability boundary. What it does not show: that the counter measures depth.
The control call's two KQ38 policies failed (`CtlTypeGuess` 1/12, `CtlSchemaProjection` 0/12) but a
cheaper shortcut found after the freeze meets the target: twelve duplicate rows asserting the base
request's own `n_predict = 1` count 12/12 (`w1/out/CriticClaimSize/c1-noop.json`), and a mapping row
whose stored value equals the base's own value counts as well
(`w1/out/RevCounterFair/f2-receipt.json`). The counter's uniqueness test is per id, not per
parameter or per value, and its `ignored` class accepts a field the session layer consumes
(`f1-receipt.json`). Those are frozen-counter defects routed to round 32; the claim is reported met
on the counter and not admitted as an improvement.

Surface moved by C2 (partially): ten claim rows of rounds 10-18 that recorded no measured revision
now carry an appended correction row with the counter's observed value (`p1:no-revision`). Three
more failing rows (`C1` in rounds 11, 12 and 13) share the Claim cell `C1`, so the counter's
`(row, class)` correction key cannot express their three dispositions: the reference repair arm
appends all thirteen and reads `valid 10 false 3 unresolved 3` — the frozen predicate is unreachable
for this population. The three rows are named below without being expressed as corrections, so the
tree carries no knowingly-false row; the defect and its receipts are the round's calibration finding.

### capabilities: append — none

No new capability row. The two counters are instruments, not capabilities under the `AXES.md`
table; `instrument-agreement` (round 30) is unchanged.

## Round 31 — claim-row evidence corrections

Appended by the kama L1, round 31, after the frozen counter
(`.ufo/waves/round-31/count-c2.py`, sha256 `2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe`)
landed its observations at the freeze tip `0e6f8ed6`. Each row names one base claim row that records
no measured revision; the original lines stay as written.

| id | row | class | observed |
|---|---|---|---|
| CR31:10:C1 re-anchor stale source anchors:p1 | C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1) | p1 | p1:no-revision |
| CR31:10:C3 sources-registry:p1 | C3 — `sources-registry` capability + 3 entries on uncovered ground | p1 | p1:no-revision |
| CR31:11:C2:p1 | C2 | p1 | p1:no-revision |
| CR31:14:C1 Ollama replay:p1 | C1 offline Ollama evidence replay | p1 | p1:no-revision |
| CR31:15:C1 duplicate-corpus:p1 | C1 declared-name duplicate-corpus admission | p1 | p1:no-revision |
| CR31:16:C2 lifecycle:p1 | C2 `live-llamacpp-lifecycle` | p1 | p1:no-revision |
| CR31:17:C1 graded fields:p1 | C1 graded fields backed by a failing detector | p1 | p1:no-revision |
| CR31:17:C2 fail-capable checks:p1 | C2 fail-capable live checks | p1 | p1:no-revision |
| CR31:18:C1 outcome classification:p1 | C1 — outcome classification and receipt boundary | p1 | p1:no-revision |
| CR31:18:C2 ledger:p1 | C2 — statement→mutant→detector ledger | p1 | p1:no-revision |

Not expressible under the frozen key (three failing rows share the Claim cell `C1`): round 11 `C1`
(SCORECARD.md:266), round 12 `C1` (SCORECARD.md:320) and round 13 `C1` (SCORECARD.md:379), all class
`p1`, observed `p1:no-revision`. The counter's `(row, class)` key collapses them, so one correction
row would silently resolve three distinct dispositions; the reference repair receipt
(`.ufo/waves/round-31/controls/RefRepair/`) records `valid 10 false 3 unresolved 3` when all thirteen
are appended. Fix routed to round 32 (round-qualified composite key or a declared uniqueness
precondition); no re-keying of history here.

### Planned (round 32)

Repair the two frozen-counter defects as instruments (uniqueness precondition for C2's correction key;
C1's counted row must name a parameter and value the base request does not already carry, and the
`ignored` class must exclude keys the session layer consumes). Then either re-earn the depth claim
under a repaired counter, or take the next frontier item: the `response_format`/`json_schema` →
grammar transform (`/slots` does not expose it) or `/v1/completions`. Open calibration ground: the
P2-first-failure masking the mutation arm found (a `p1` correction resolves a row that also lacks an
evidence path) and the duplicate-id case the counter does not count.

## Round 31 attempt 2 — inherited claims re-measured, registry coverage, meaning-cell corrections (2026-10-23)

Authority unchanged: assigned axes operability + calibration (`../shokunin.conf` kama row); lowest
axes at round start were depth, calibration and adjacency at 7; the stagnation nudge is inactive
(operability 8 is above the 8/10 saturation line but the window is not exhausted). Attempt 1 of this
round froze C1/C2 at `0e6f8ed6` (base `07794a4d`) and landed their data through `382d11b2`, then the
session died without a fleet report. This attempt inherits that state, re-measures it, freezes one
further claim (**C3**, `preregistration-c3.json` at `bda324bb`, before its row existed), dispatches a
44-seat falsification wave (wave 2), and lands the report. No inherited predicate was amended and no
row was rewritten.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Verdict |
|---|---|---|---|---|---|
| C1 (depth; frozen attempt 1) | depth 7 → 7 | base `07794a4d`: `cannot evaluate: .ufo/waves/round-31/sources/SNAPSHOT.json missing at tip`, exit 2 → tip: `registered 18 counted 17 target 12 met True not-counted ['K31-10']`, exit 0 | `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --repo <clone> --tip <full commit> --out <receipt>` (sha256 `d86c4a94…9216`) | `bda324bbc5c1d7db93553adb13c5f380492c3c93` | **met on the frozen counter; not admitted** — a twelve-row no-op registry padded with a matching SKILL table counts 12/12 (`w2/out/CriticNoop/`: `registered 12 counted 12 target 12 met True`), so the counter cannot separate depth from a no-op; three further mutants survive (`w2/out/MutC1Pin`) |
| C2 (calibration; frozen attempt 1) | calibration 7 → 7 | base: `rows 28 base_mismatched 13 valid_corrections 0 unresolved 13 append_only True met False` → tip: `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False` | `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo <clone> --tip <full commit> --out <receipt>` (sha256 `2d06f38d…c6fe`) | `bda324bbc5c1d7db93553adb13c5f380492c3c93` | **not met** — three failing rows share the Claim cell `C1` (rounds 11–13) and the `(row, class)` key is non-injective: one collapsed correction flips `met` True while two dispositions stay uncorrected, and three honest corrections are counted false (`w2/out/MutC2Key/`) |
| C3 (operability; frozen this attempt) | operability 8 → 8 | `unregistered .ufo/waves/round-29/count-c1.py` / `registered 8 unregistered 1`, exit 1 → `registered 9 unregistered 0`, exit 0 | `/usr/bin/python3 tools/gate-registry-check.py [--rev <commit>]` | `addeb57c5d717785a94105a2e36cc8a76940fb6c` | **met on the frozen predicate; not admitted as an improvement** — the gate is an occurrence check: a row with an empty exit map and even a nonexistent metadata path also reads `registered 9 unregistered 0` (`w2/out/ExecC3Control/`, `w2/out/CriticC3Control/`) |

Wave 2 also re-measured the round's own evidence and found six overclaiming `meaning` cells (K31-02,
K31-05, K31-08, K31-09, K31-11, K31-12); all eighteen `outcome` cells rendered byte-identically and
reproduced live (`w2/out/RevRow{A..E}/`). They are corrected by an appended block in `SKILL.md`, not
by rewriting the counted rows.

### capabilities: append — none

C3 registers an existing instrument, it does not add one; no capability row enters. The round-30
`instrument-agreement` row is unchanged.

### round-31 record corrections (appended, attempt 2)

- §Round 31 C2 row cites `.ufo/waves/round-31/c2/c2-tip.json`, which does not exist; the receipts are
  `c2/c2-b4f3edc0.json` and `c2/c2-bda324bb.json`.
- The same row's Before column reads `rows 28` at base and tip; the counter's population is 30 rows at
  both (`rows 30` in `c2-bda324bb.json`); 28 is the count at base only because two round-31 rows did
  not exist yet — the base receipt itself prints `rows 28`.
- `corpus/README.md` §Frontier disposition said `19 rows`, `19 live rows` and `13 pinned source rows
  S180–S192`; the measured counts are 18 registry rows, 18 SKILL rows (17 counted) and 12 source rows
  S180–S191 (appended correction in README).
- `PROVINCE.md` round-31 note said `S180–S192`; corrected by appended record to S180–S191.
- `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` was a committed `404: Not Found` body;
  `server-http.cpp` and `server-models.cpp` were unpinned byte-identical duplicates of earlier
  rounds' snapshots and `c1/c1-remap.json` duplicated `c1-54c6f4fe.json`; all four were removed at
  `a9181096` (wave 1 evidence retained; the 1.2 MB `CriticIgnoredClass/raw.json` is kept because it
  backs a wave-1 counter-defect finding, and its size is disclosed in the report).

### Planned (round 32) — supersedes the round-31 Planned

1. **C2 repair as a new instrument**: adopt a round-qualified correction key with a declared
   uniqueness precondition. The three-hunk working candidate is committed as evidence at
   `w2/out/MutC2Key/counter-roundkey.py` (one correction → `valid 11 unresolved 2`;
   three corrections → `valid 13 unresolved 0 met True`; pristine counts unchanged).
2. **C1 eligibility rules**: a counted row must name a parameter and value the base request does not
   already carry, and the `ignored` class must exclude keys the chat session consumes. Then re-earn
   depth or take the `response_format`/`json_schema` → grammar transform.
3. **Meaning cells gated by a probe, not a word count** (KQ42): a graded prose cell is admitted only
   after a counterexample search on the pinned fixture, with the probe receipt committed.
4. Pin verification: `count-c1.py` verifies only sha256 fields read from the tip blob; working-tree pin
   edits and the declared `bytes` field are ignored (`w2/out/MutC1Pin/`), and C2's append-only check is
   a base-prefix check only (`w2/out/MutC2Append/`).

## Round 31 attempt 3 — inherited claims re-executed at write time, frontier row S192, wave-3 prepared (2026-10-24)

Authority unchanged: assigned axes operability + calibration (`../shokunin.conf` kama row); lowest
axes at round start depth, calibration, adjacency all 7; stagnation nudge inactive. Attempts 1-2 of
this steered round (2026-10-23) froze all three claims and landed their data but died without a
fleet report (watchdog: six `lane-dead-no-report kama round=31` lines). This attempt inherits the
committed tree at `f129e27b3b57a8fed7a34a8e6fe96d481e6c959d`, re-executes every frozen counter at
write time on a fresh scratch clone (`/tmp/kama-r31-clone`, clean at `f129e27b`), runs the frontier
step, prepares the round-32 wave under the accepted host mapping (L1 prepares; the orchestrator
dispatches between rounds), and lands the report.

| Claim | Axis, score | Re-executed at write time (2026-10-24) | Verdict (unchanged from attempt 2) |
|---|---|---|---|
| C1 (depth; frozen attempt 1) | depth 7 → 7 | `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane . --repo /tmp/kama-r31-clone --tip f129e27b… --out .ufo/waves/round-31/res/out/KamaR31a3.ResReRunC1/c1-tip.json` → `registered 18 counted 17 target 12 met True not-counted ['K31-10']`, exit 0; every per-row live observation byte-identical to attempt 2's inherited receipt (`res/out/KamaR31a1b.ResReRunC1/c1-tip.json`, diff none) | **met on the frozen counter; not admitted** — a twelve-duplicate-row no-op registry also meets it (`w2/out/CriticNoop/`); counter defect routed to round 32 |
| C2 (calibration; frozen attempt 1) | calibration 7 → 7 | `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo /tmp/kama-r31-clone --tip f129e27b… --out .ufo/waves/round-31/res/out/KamaR31a3.ResReRunC2/c2-tip.json` → `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False`, exit 0 | **not met** — three rows (rounds 11-13) share the Claim cell `C1`; the `(row, class)` key is non-injective; reference repair also fails (`w2/out/RefRepair/`, `w2/out/MutC2Key/`) |
| C3 (operability; frozen attempt 2) | operability 8 → 8 | `python3 tools/gate-registry-check.py --rev f129e27b…` → `registered 9 unregistered 0`, exit 0 | **met on the frozen predicate; not admitted** — occurrence check; an empty-exit-map row and a nonexistent metadata path also pass (`w2/out/ExecC3Control/`, `w2/out/CriticC3Control/`) |

Frontier step this attempt: census before exit 0 (191 rows) → after exit 0 (192 rows,
`.ufo/waves/round-31/census-end-attempt3.out`); one new row **S192** opened 2026-10-24 (OpenAI Chat
Completions API reference, `response_format`; tier A scoped to the OpenAI-side declared semantics;
`used-by` `corpus/lessons/round-31.md`); zero cells changed old→new on S180-S191; zero rejections.
Mistake mined: lesson row 9 — recurrence of mistake 5's class (uncommitted re-run receipts in
`res/`, again inherited untracked); fix enforced this attempt (receipts committed with this
section; report-time untracked gate passes only at zero). Sourced claim: C1's rows rest on
S180-S191 opened this round; S192 carries the round-32 frontier item. Wave-3 (32 seats, policy v1
band 32-64, validator exit 0, attack roles 20/32 = 62.5%) is prepared at
`.ufo/waves/round-31/w3/spec.json` + `taskCall.json`, NOT dispatched — host mapping: the
orchestrator dispatches prepared waves between rounds. Other scores held: operability 8, freshness
8, coverage 9, depth 7, adjacency 7. No capability row enters.

### Planned (round 32) — restated, unchanged in substance from attempt 2's plan

Repair the two frozen-counter defects as instruments (round-qualified C2 correction key with a
declared uniqueness precondition — candidate `w2/out/MutC2Key/counter-roundkey.py`; C1 eligibility:
a counted row names a parameter and value the base request does not already carry, and the
`ignored` class excludes session-consumed keys), gate graded meaning cells by a probe, not a word
count (KQ42), and pin declared bytes plus refuse working-tree pin edits. Then re-earn depth or take
the `response_format`/`json_schema` → grammar transform (S192; scout item ScoutGrammarTransform in
the prepared wave) or `/v1/completions`. Wave-3's 32 prepared items attack and build exactly these
candidates.
