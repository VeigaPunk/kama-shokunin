# kama-shokunin — SCORECARD

Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,
each bound to an evidence pointer and the round that last changed it.

**Current authority (round 57):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 57. Calibration 7 is the lowest assigned axis, below operability 8 and the saturation line, so the stagnation nudge is inactive. Round 57 froze and measured C1 (no-op battery roster-control, operability) and C2 (stale self-description verifier-spotcheck count, calibration) with controls committed before data (SCORECARD §Round 57). Scores remain operability 8 and calibration 7; no capability enters. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived by `tools/round42-selfdesc-reconcile.py`; the historic round-56 statement is preserved under §Historical pre-integration authority.

## Axes

Round 43 re-anchors the `SKILL.md` and `PROVINCE.md` hashes after the round-43 edits and restates the closure count of the calibration row. Round 42 added, to every row, one axis-specific run fact (routed defect R41A03: a true fact is not yet a relevant one) and re-anchored the `PROVINCE.md` hash after the round-42 edit. Reconciled in round 41 against the measured commit (`tools/round41-scorecard-reconcile.py`, claim C1): every hash, line count, run line and path in the table below re-derives there, and the scores are the lane's last-declared assessment (round 39 and round 40 sections). The round-3 table it replaces is kept below, byte-intact, as history; its md5s, line counts and bare file names no longer matched the tree, and its freshness 7 and coverage 8 predate the round-10 moves to 8 and 9.

| Axis | Score | Evidence pointer (re-derivable at the measured commit) | Last change |
|---|---|---|---|
| **operability** | **8** | registry gate `tools/kama-probe.sh` sha256 `4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4` (1138 lines); run `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0`; run `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0`; run `python3 tools/report-landing-audit.py --selftest` → `selftest cases=79 failed=0`; run `python3 tools/sources-append-only.py --selftest` → `45/45 selftest cases passed`. Limit: the registered endpoints sample DEAD (no authorized serving runtime; operator-owned), so no model-readiness verdict is evidenced | score round 3; evidence re-anchored round 52 |
| **freshness** | **8** | snapshot/diff harness `tools/test-snapshot.sh` sha256 `236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646` (194 lines); run `python3 tools/citation-provenance.py --selftest` → `selftest: ok (24 cases)`; live drift evidence `.ufo/waves/round-41/c2/ls-remote-vllm.txt` sha256 `13388e483163357aa4daea784d0e67cdc8d6b5438d3166d613a2a044590b9282`; run `python3 -c "recheck=[l.split(chr(124))[10].strip() for l in open('corpus/SOURCES.md') if l.startswith(chr(124)+' S') and int(l.split(chr(124))[1].strip()[1:])<=477];print(sum(1 for r in recheck if r))"` → `218` (registry rows S001–S477 carrying a recheck cadence). Limit: snapshots are invocation-driven (no clock), and source rechecks run on each row's `recheck` cadence; release re-verification ledger `registry/release-recheck-b11889.tsv`: the 91 `on-release` registry rows pinned to a llama.cpp commit re-verified at release b11889 (counter `tools/round44-release-recheck-audit.py`, §Round-44 measured results: 82 holds, 3 holds-reworded, 6 unchanged-file, 0 drifted, 0 removed) | score round 10; evidence re-anchored round 44 |
| depth | **7** | `SKILL.md` sha256 `2d7c22125c3eee4d55134df9e15a92d1d2a8071337e96522c768a4c8cf3f4c14` (1612 lines); run `grep -c '^## ' SKILL.md` → `43`; `corpus/knowledge/endpoint-identity.md` sha256 `0100ac6d89876b2f11a58542ae1ab75c3765f61d9d138fdad4d720074ddf13d7` (218 lines) | score round 1; evidence re-anchored round 55 |
| coverage | **9** | surface list `PROVINCE.md` sha256 `aa7915a8590d9180ac559864897679ecb532a3c5b6595f58a4d19a5491e5d67d` (186 lines); run `python3 -c "import glob;print(len([f for f in glob.glob('corpus/knowledge/*.md') if 'engine-sides' not in f and 'processes' not in f]))"` → `34` (knowledge entries held before rounds 42 and 43); held ground includes `corpus/knowledge/endpoint-health-probe-conventions.md`, `corpus/knowledge/kv-cache-reclamation-models.md`, `corpus/knowledge/serving-alias-contract.md` | score round 10; evidence re-anchored round 48 |
| calibration | **7** | run `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`; run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `43` (outside closures on record, including round 56; exact count is re-derived at the measured tip); that figure is the number of `corpus/lessons/*verifier-spotcheck.md` blobs at the measured commit; run `python3 tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0`; this table's counters `tools/round41-scorecard-reconcile.py` and `tools/round42-selfdesc-reconcile.py`; latest outside closure `corpus/lessons/round-56-verifier-spotcheck.md` (admitted); trend-verdict ledger `registry/verdict-ledger.tsv` (204 rows, self against outside for rounds 10–43: `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`, §Round-44 calibration ledger); claim-outcome ledger `registry/claim-outcome-ledger.tsv` (126 rows, the 63 claims of rounds 10–44, self against outside: `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`, §Round-45 claim-outcome ledger) | score round 1; evidence re-anchored round 56 |
| adjacency | **7** | `corpus/knowledge/cross-lane-scope.md` sha256 `1801cb7fa45ef6f56ff96cb67c7840256fcffce000a56067cd8133797b9728a9` (87 lines); run `python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))"` → `16` (lines starting with a table pipe, header and separator lines included); contested scope stays reported, not absorbed (`PROVINCE.md` paragraph "Out of province → report, never absorb") | score round 1; evidence re-anchored round 42 |

### Historical axes table (round-3 assessment; superseded in round 41)

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

Superseded in round 42. The live plan is `### Planned (round 58)` at the end of this file; the round-5 plan this section carried is kept verbatim under §Historical head sections.

## Retired

None. 6 axes and 11 capabilities remain active. Neither assigned axis is retired: the registered consumers still sample DEAD (`registry/history/latest.tsv`; restoring a serving runtime is operator-owned), while the lane-owned llama.cpp fixture reaches `MODEL_OK` on an unregistered loopback port (`.ufo/waves/round-16/live/receipt.json`), so the surface is not permanently gone. Retirement would need evidence of permanent absence or of saturation, and neither is observed.

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

## Capabilities-RENAMED

Mirror of the round-49 canonical capability list that §Round 49 carries (a mirror, not the canonical source: the counters resolve the highest-numbered canonical heading below this line). Registry counts are not restated here: `scripts/sources-census.sh census --file corpus/SOURCES.md` derives them.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |
| append-only-audit | Set the lane's contract-declared append-only self-description - the paths and patterns `registry/append-only-contract.tsv` names, each row naming the lane line that declares the rule and the `region` it grades (`*`; `exempt=` `## ` sections that stay ungraded while their line count's window maximum is not below the parent's; or a single `only=` section) - against its git history: every row must bind (the declaring line says append-only for that path and is not a negation within three words of it, the row token occurs there as a whole word, a wildcard row binds only through a line that names its directory, an exempt pointer names the line that declares those sections re-derived, and an `only=` pointer names its prefix), grade a deleted line in an eligible exempt section only when its text was born in an exempt section (origin), list every commit that deletes >= 20 lines from one of those files with a deleted count equal to `git diff --numstat` (byte-exact, so no `--`-prefixed line is lost), report the largest share of the graded lines any commit in the event's own window holds again (a multiset maximum, so a later head re-anchor cannot lower it) and which later commit first holds all of them, and exit 1 on an unbound row, a partial or unrestored mass deletion, or a regression (the tip holds fewer graded lines than the event's best window commit) | `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `.ufo/waves/round-49/measured/c2-build.out` | 46 |
| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v5` receipt's server release archive and model from the https URLs its provenance block records - the model pinned to a 40-hex `/resolve/<commit>/` revision that the receipt also states as `provenance.model.commit` - verify both sha256 values before anything is extracted or executed, check the archive and its member against the asset and server digests before the server starts so a v5 receipt's `provenance.verified` block is recorded rather than asserted, re-run the lifecycle from an empty home passing the downloaded archive as `--server-archive`, hold the rerun server up for an outside observer on request (`--witness-dir`: `ready.json` names the port and the server child's pid, the server stays up until `release` or the bounded timeout, and the rerun receipt records `witness.released`), refuse a server-archive member that is sparse or whose declared size differs from the `--server` file before hashing it, compare the rerun with the original past check pass/fail on a stable projection of the captured surfaces (props fields, slots count and body digest, health status and body digest, models ids and owned_by, metrics status, loading envelope, teardown outcome, listener ownership), refuse a receipt whose provenance is missing or unverified, whose recorded digest does not match what it downloads, or whose server-archive member is unsafe, and answer `--compare A B` on two receipts without the network | `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`; `.ufo/waves/round-48/c2/live/receipt-1.json` | 47 |

Rows enter only through a round that demonstrates the capability running (`AXES.md` §Capabilities).

## Saturation

Saturation line **8/10** (declared round 10, unchanged); stagnation window **N = 4** rounds. Derived at the measured commit by `tools/round42-selfdesc-reconcile.py` (kept current in round 49): score vector operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7 (from `## Axes`); capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47 (highest canonical list); the assigned axes are operability + calibration and calibration 7 is below the line, so nudge inactive. The last capability entered in round 47 is older than the N=4 stagnation window; the nudge remains inactive solely because the lowest assigned axis remains below saturation.

## Historical head sections (superseded in round 42)

The text below is the lane's head self-description as it stood through round 41, kept verbatim. Its statements are history, not the current state: the current state is the head of this file.

**Current authority (round 53):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 53. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. Round 53 measured C1 operability against its frozen counter; C2's counter printed met=True but its hide-a-SKILL-citation control also met=True, so C2 is not admitted (SCORECARD §Round-53 measured results). No axis score or capability changes. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current through round 53; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections, and from round 48 every authority banner this line replaces is appended byte-exact under §Superseded head banners at the end of this file (`registry/append-only-contract.tsv` row SCORECARD.md, region `exempt=`). Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

### Banner (round-5 text)

**Current authority (actual round 5, blocked attempt):** assigned LIVE axes
remain operability and freshness (`../MISSION.md`); freshness is the lower
inherited author assessment. The numeric rows below are historical assessments,
not remeasured present file lengths, coverage denominators, or a completion
counter. Round-5 per-axis evidence below supersedes their current-state reading;
no scalar score is advanced. Historical reports exist for rounds 1, 2 and 4;
round 3's report gap remains unresolved. The headless launch counter 1 is not a
verified completed round. This attempt adds **zero** verified completed rounds.

### Planned (round-5 text)

After operator-owned route/binding repair, a **fresh session** remeasures the
lowest LIVE axis and chooses the next falsifiable freshness move. Do not repeat
the landed round-5 runbook correction as new progress. Candidate frontier:
re-anchor still-live probe citations through explicit corpus correction entries;
retain the dated source records. See `.ufo/round-5/continuation.md`.

Declared-vs-served context size remains a separate blocked feature: no current
serving context is available. Service restoration, scheduling and global route
configuration remain operator-owned; no timer or successor unit is installed.

### Retired (round-3 text)

None. Both assigned axes remain active — though round 3 observed the
retirement precondition beginning to materialize: `qwen-coder.service` is
inactive and deleted, and every model endpoint is dead. Retirement still
requires evidence the surface is *permanently* gone (not observed — the
34113 pins ship in a maintained upstream repo), or that invocation history
and context drift have saturated (not observed).

### Capabilities (round-10 head table)

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns: 30 opened, tier-scoped, revision-anchored rows (17 mined by 3 knowledge entries, 8 queued, 5 rejected with reason + flip), 4 study paths, 3 search-log notes; contract-v1 census runs clean | `corpus/SOURCES.md`; census commands in §Round 10 below (rows 30, malformed 0, dups none, enum/tier-inflation none, missing used-by none) | 10 |

Rows enter only through a round that demonstrates the capability running (`AXES.md` §Capabilities); none enter through this rollout.

### Saturation (round-10 text)

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

## Round 32 — claim-row evidence corrections (round-qualified)

Appended by the kama L1, round 32, for the repaired counter
`.ufo/waves/round-32/count-c2r.py` (sha256 `ef298b6311cc30907590317f1e477704d28bf880c292d25e1c711cd8f379c92e`,
frozen at `9afaf0e9f03ea513e8ee54b43793d2f01cfa309e`). The three rows below share the Claim cell
`C1`; each id carries its claim row's round so the counter's `(round, row, class)` key stays
injective. The round-31 corrections table above stays byte-untouched.

| id | row | class | observed |
|---|---|---|---|
| CR31:11:C1:p1 | C1 | p1 | p1:no-revision |
| CR31:12:C1:p1 | C1 | p1 | p1:no-revision |
| CR31:13:C1:p1 | C1 | p1 | p1:no-revision |

### Round-31 record corrections (routed defects 5 and 6, reconciled this round)

- SCORECARD.md:1723 (round-31 attempt-3 table) cites `w2/out/RefRepair/`; the reference-repair
  receipt lives at `.ufo/waves/round-31/controls/RefRepair/receipt.txt` (`w2/out/MutC2Key/` is
  correctly cited beside it). The filed fleet round-31 report carries the same drift; filed bytes
  are corrected here by append, never rewritten (KQ26).
- Wave-2 seat census, re-run 2026-10-24 at the round-32 start:
  `find .ufo/waves/round-31/w2/out -maxdepth 1 -type d | wc -l` → 44 including the `out`
  directory itself, i.e. **43 seat-output dirs**. The w2 `spec.json`/`taskCall.json` name 44
  distinct seats; the connector seat `ConnInstrumentDup` has no output directory, and the sweep
  `grep -rli instrumentdup .ufo/waves/round-31/w2/out` prints nothing (only spec/plan/validate/
  taskCall copies name it). The round-31 report's "44 returned reports" is corrected to: 44
  planned seats, 43 committed seat-output dirs, one seat (`ConnInstrumentDup`) unverifiable as
  returned — recorded as dead/unverifiable rather than silently counted.

## Round 32 — round-qualified claim-row evidence (calibration) and registry-row meaning (operability)

Authority: assigned axes operability + calibration (`../shokunin.conf` kama row); lowest axes at
round start depth, calibration, adjacency all 7; stagnation nudge inactive. Priority queue: the
round-31 closure-routed defects. Preregistration `.ufo/waves/round-32/preregistration.json`,
frozen at `9afaf0e9f03ea513e8ee54b43793d2f01cfa309e` before any data receipt; base
`18464d0866afd5c4b471c8478d72b079d82d1fa8`. Both claims are instrument repairs: the axis scores
are held (calibration 7, operability 8) and the measured deltas below are the claim evidence.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — round-qualified claim-row-evidence counter (repaired instrument, supersedes the `(row, class)` key for new corrections) | calibration 7 → 7 | base `18464d0866afd5c4b471c8478d72b079d82d1fa8`: `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False` (`.ufo/waves/round-32/c1/before-base.json`; the frozen round-31 counter prints the same counts) → landed tip: `rows 30 base_mismatched 13 exempt 1 valid_corrections 13 false_corrections 0 unresolved 0 append_only True met True` (`.ufo/waves/round-32/c2r/c2r-tip.json`) | `/usr/bin/python3 .ufo/waves/round-32/count-c2r.py --repo <fresh clone> --tip <full commit> --out <receipt>` (counter sha256 `ef298b63…c92e`, frozen at `9afaf0e9`) | data tip `c4c46ad5b87d`; final re-run at the landed tip recorded in `.ufo/waves/round-32/c2r/c2r-tip.json` | `.ufo/waves/round-32/preregistration.json`; `.ufo/waves/round-32/c1/before-base.json`; kill-rule controls `.ufo/waves/round-32/c1/controls/KeyCollapse/` (frozen counter flips `met True` on one collapsed correction; the repaired counter refuses it) and `.ufo/waves/round-32/c1/controls/DupKey/` (two corrections, one qualified key → both false); `corpus/lessons/round-32.md` |
| C2 — instrument-registry gate grades meaning, not presence (routed defect 3) | operability 8 → 8 | v1 gate (bytes from base) reconstructing the r31 w2 controls: exit 0 `registered 9 unregistered 0` on a thin empty row, on an empty-exit-map row, on a row citing `.ufo/waves/round-999/count-c999.py`, and on the base tree whose `.ufo/waves/round-17/count-verdicts.py` and `.ufo/waves/round-26/count-c1.py` are prose-only (`.ufo/waves/round-32/c2/controls/*-v1.out`, `prose-only-v1.out`) → v2 gate at the landed tip: exit 0, `registered 10 unregistered 0 defective 0` (`c2/gate-tip.out`); each fixture exits 1 with its named defect under v2 (`c2/controls/*-v2.out`); the v2 semantics on the base tree exit 1 with the two prose-only counters unregistered (`c2/before-base.out`) | `python3 tools/gate-registry-check.py --rev <full commit>` and `python3 tools/gate-registry-check.py --selftest` | data tip `c4c46ad5b87d`; final re-run at the landed tip recorded in `.ufo/waves/round-32/c2/gate-tip.out` and `c2/selftest-final.out` | `.ufo/waves/round-32/preregistration.json`; `.ufo/waves/round-32/c2/SUMMARY.md`; mutation arms `c2/mutations/` (each single-check removal flips exactly its fixture; thin-row entanglement disclosed); registry-row semantics row S193 (`corpus/lessons/round-32.md` Gate); SKILL round-32 registry block |

Surface moved by C1: the claim-row-evidence census's correction key. Before, three distinct
failing rows (rounds 11-13, all named `C1`) collapsed into one `(row, class)` key, one shortcut
correction flipped `met` True while two dispositions stayed uncorrected, and two honest
corrections for one key were silently uncounted; now every disposition is separately expressible,
round-qualified, under a declared uniqueness precondition, and the frozen counter's shortcut is
receipted red-handed. What it does not show: that the rows behind the corrections were ever
true claims — the census calibrates evidence discipline, not claim truth.

Surface moved by C2: the instrument-registry gate's verdict. Before, occurrence in any SKILL.md
text (prose, a thin row, an empty exit map, a nonexistent pin) certified registration; now
registration requires a registry-table row whose cells carry an entry command, a non-empty exit
map and only resolvable cited paths, and the gate also exposed two counters that had been
prose-registered for rounds (round-17, round-26 — registered properly by the round-32 block).
What it does not show: that any registered instrument is correct — the gate grades the registry,
not the instruments.

No capability row enters (the two repairs are instrument repairs, and
`instrument-agreement` from round 30 is unchanged). Other scores held: depth 7, freshness 8,
coverage 9, adjacency 7. No axis harmed: both changes are additive to the lane's own
calibration/operability surfaces; the frozen round-31 counters are byte-untouched and re-run
unchanged at the new tip (`.ufo/waves/round-32/kq36/`).

### Planned (round 33)

Re-earn depth under a repaired C1-eligibility counter (a counted row names a parameter and value
the base request does not already carry; the `ignored` class excludes session-consumed keys) with
wave falsification first, or take the `response_format`/`json_schema` → grammar transform
(S192; a live lane-fixture measurement) — both are prepared as wave items under
`.ufo/waves/round-32/w1/` (validated, orchestrator-dispatched). Then: KQ42 probe gating for the
remaining meaning cells, and pin declared bytes plus refusal of working-tree pin edits
(routed defects 1, 2, 4). Open calibration ground: the round-30 extractor still finds 69 of 141
statements by itself; any statement outside both populations remains invisible.

## Round 33 — routed receipt evidence corrections (2026-10-24)

Authority: kama remains assigned operability + calibration (`../shokunin.conf`);
calibration 7 is the lowest assigned axis and the stagnation nudge is inactive.
The preregistration is `.ufo/waves/round-33/preregistration.json` (base
`cc46980359278d0967cf65e785b41c27b8d9c36c`, claim predicates frozen before
data). Both claims hold the numeric axis reading; the measured deltas are
explicit record/evidence counts, not a conversion to mastery scores.

### Round 33 — correction of round-32 gate-control receipt references

The round-32 C2 row at `SCORECARD.md:1791`, written at
`dc4258bdb08d658f1c5b15abc8378461659bd155`, says that each fixture exits 1
with its named defect and cites `c2/controls/*-v2.out`. Three files in that
glob contain the base-tree clean output, not the named fixture finding; they
remain byte-intact as historical evidence. The exact output receipts that do
show the findings are:

| Fault | Replacement receipt | Observed output |
|---|---|---|
| thin-row | `.ufo/waves/round-32/c2/controls/thin-v2.out` | `defective .ufo/waves/round-29/count-c1.py: thin-row` |
| empty-exit-map | `.ufo/waves/round-32/c2/controls/noexit-v2.out` | `defective .ufo/waves/round-29/count-c1.py: empty-exit-map` |
| missing-path | `.ufo/waves/round-32/c2/controls/badpath-v2.out` | `defective .ufo/waves/round-29/count-c1.py: missing-path:.ufo/waves/round-999/count-c999.py` |

### Round-32 filed report receipt-lineage correction (routed defect 1)

The filed report's sentence “`c2r/c2r-tip.json` and the gate/selftest finals
measure the data tip `967d88528c1d` and are committed in `3f1a7330`” is
superseded only as to its grouping of receipts. The committed
`c2r/c2r-tip.json` records `tip=dc4258bdb08d658f1c5b15abc8378461659bd155`
and was first added by `967d88528c1d83535563f971863f7855f76b4849`. The
separate `gate-tip.out` and `selftest-final.out` record the `967d88528c1d`
lane-tip run and were added by `3f1a73308bec9c2f4497c557d01bc58ec8e72eca`.
The filed report is not rewritten.

### S193 quote correction (routed defect 3)

The round-32 lesson's Gate text says “line 22” and “16 words”. At the pinned
source revision, the sentence is in the docstring “Contract”, lines 15–16,
and contains 17 whitespace-delimited words. S194 appends the corrected exact
anchor and quote; S193 and the filed round-32 lesson remain unchanged.

### Round 33 measured claims

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — round-32 C2 self-assessment correction (S194) | calibration 7 → 7, delta 0 | `false_at_writing=3 valid_corrections=0 unresolved=3 met=False` at base `cc46980359278d0967cf65e785b41c27b8d9c36c` → `false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True` | `python3 tools/round33-claim-audit.py --repo . --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 --tip 1c881bbd3e1cce5f0b01f1afc6d3229866cbe712` | `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712` | `.ufo/waves/round-33/c1/{base-control-amend1,after-evidence-tip}.out`; original false statement at its writing revision; correction table above; S194 |
| C2 — complete r32 gate replay receipts (S194) | operability 8 → 8, delta 0 | `complete=0/4 missing=4 invalid=0 met=False` at base `cc46980359278d0967cf65e785b41c27b8d9c36c` → `complete=4/4 missing=0 invalid=0 met=True` | `python3 tools/round33-gate-receipts.py audit --repo . --tip 1c881bbd3e1cce5f0b01f1afc6d3229866cbe712 --source-rev 967d88528c1d83535563f971863f7855f76b4849 --receipt-dir .ufo/waves/round-33/c2/final` | `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712` | `.ufo/waves/round-33/c2/{base-control-amend2,after-evidence-tip}.out`; exact captured receipts in `c2/final/`; source row S194 |

The first C2 after-run at `88331197a7de5fcc171bc7290fdd7beb43487a63` raised a
`TypeError` before emitting an audit verdict; it is not counted as a pass or
kill. The auditor fix and visible error receipt are in `corpus/lessons/round-33.md`
and `.ufo/waves/round-33/c2/after-data-tip.out`; the unchanged 4/4 predicate
re-ran successfully at `1c881bbd`.

No capability row enters: the work corrects lane evidence and tools, not a new
serving operation. Other numeric readings stay held: depth 7, freshness 8,
coverage 9, adjacency 7. No endpoint or registered-consumer state was sampled.

### Planned (round 34)

Calibration remains the lower assigned axis at 7. Use KQ39 to identify any
separate SCORECARD/SHONEN statement mismatch at its writing revision; freeze a
nonzero no-op control before data and append only observed corrections. Do not
repeat the three resolved round-32 receipt references. If no reachable
calibration mismatch exists, choose the next evidence-backed operability move
within kama's lane rather than claiming a no-op census as progress.

## Round 34 — capability repertoire and instrument-registry coverage (2026-10-24)

Authority: assigned axes operability 8 + calibration 7 (`../shokunin.conf` kama
row); calibration is the lowest assigned non-retired axis, below the saturation
line 8, so no stagnation waiver. Preregistration
`.ufo/waves/round-34/preregistration.json` (base `7c35289da5f4b94e062cd900eb086919e5094003`),
frozen before any data row landed.

**Capabilities — canonical list as of round 34**

Same four columns as the round-16 canonical list; the round-16 table stays
byte-intact. Every capability the lane demonstrated with a passing round
demonstration is listed here, with an evidence pointer that resolves under the
lane root.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |

The round-16 table listed three of these six: the round-20, round-25 and
round-30 capabilities were demonstrated in their own append sections and never
entered the canonical repertoire table. That gap is what C1 measures and what
this table closes; the append sections stay byte-intact.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — canonical capability repertoire table | calibration 7 → 7 (delta 0) | `listed 3 observed 6 missing 3 unsubstantiated 0 met False` (exit 1) at base `7c35289` → `listed 6 observed 6 missing 0 unsubstantiated 0 met True` (exit 0) | `python3 tools/capability-repertoire-audit.py --repo . --tip <full-commit> --out <receipt.json>` | see `.ufo/waves/round-34/c1-after.out` | `.ufo/waves/round-34/c1-before.out`; `.ufo/waves/round-34/c1-after.out`; `corpus/lessons/round-34.md` |
| C2 — instrument-registry gate sees every tracked round counter | operability 8 → 8 (delta 0) | `registered 10 unregistered 2 defective 0` (exit 1) at base `7c35289` with the widened population → `registered 12 unregistered 0 defective 0` (exit 0) | `python3 tools/gate-registry-check.py --rev <full-commit>` | see `.ufo/waves/round-34/c2-after.out` | `.ufo/waves/round-34/c2-before.out`; `.ufo/waves/round-34/c2-after.out`; `corpus/lessons/round-34.md` |

Both scores are held: a table that finally lists what the lane demonstrated, and
a gate that can see two more instruments, are bounded repairs, not mastery
changes.

### Planned (round 35)

Outside non-author sampling of round 34. The round-33 wave's late-arriving
seat outputs are inherited evidence, not this round's seats. The remaining
calibration ground is the `capability-repertoire-audit.py` population itself: it
reads the SCORECARD's own tables, so a capability demonstrated only in a lesson
is still invisible to it.

## Round 35 — r34 self-assessment corrections and probe-signal coverage (2026-10-24)

Authority: conf assigns operability 8 + calibration 7. Calibration is the lowest
non-retired numeric axis (tied with depth and adjacency at 7). MISSION.md:29
still says operability + freshness. That file was not edited. The conflict is
named and does not change either predicate. Stagnation nudge inactive.
Preregistration `.ufo/waves/round-35/preregistration.json`, frozen before seats
scored. Base `719655f12517a9ce6b1a5ca44316897fed8420b0`.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — four r34 self-assessment statements corrected by append | calibration 7 → 7 (delta 0) | `uncorrected 4 false_corrections 0 report_unchanged 1 met False` (exit 1) with no lesson → `uncorrected 0 false_corrections 0 report_unchanged 1 met True` (exit 0) | `python3 tools/round35-statement-audit.py --repo . --lesson <round-35.md>` | `d419b99df20d1f0b34caf65807e913784e69baf5` | `.ufo/waves/round-35/controls/c1-noop.out`; `.ufo/waves/round-35/c1-after.out`; `corpus/lessons/round-35.md` |
| C2 — coverage map names the probe-convention entry | coverage 9 → 9 (delta 0) | `named 0 file_exists 0 cited_row 0 met False` at base `719655f` → `named 1 file_exists 1 cited_row 1 met True` | `python3 tools/round35-coverage-audit.py --repo . --tip <full-commit>` | `d419b99df20d1f0b34caf65807e913784e69baf5` | `.ufo/waves/round-35/controls/c2-base.out`; `.ufo/waves/round-35/c2-after.out`; S327 |

Both scores are held. C1 does not make the filed r34 report true. C2 adds one
coverage-map pointer the base README did not hold. No capability row enters.
Other readings held: operability 8, freshness 8, depth 7, adjacency 7.

### Planned (round 36)

Outside non-author sampling of round 35. The capability-repertoire audit still
cannot see a capability demonstrated only in a lesson. Quarantine rows that
located this round but were not cited by an admitted entry stay unappended.

## Round 36 — r35 routed corrections and the published-route-versus-engine-route ground (2026-10-24)

Authority: conf assigns operability 8 + calibration 7. Calibration is the lowest
non-retired numeric axis (tied with depth and adjacency at 7). MISSION.md:29
still says operability + freshness; that file was not edited and no duplicate
L0 was filed — the round-35 question stands open. Stagnation nudge inactive.
Preregistration `.ufo/waves/round-36/preregistration.json`, frozen before any
seat scored. Base `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — four r35 routed statements corrected by append | calibration 7 → 7 (delta 0) | `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) at base → `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0) | `python3 tools/round36-statement-audit.py --repo . --tip <full-commit>` | `2e8beda5b2a2dcc62d6782838ee6e47cda04df55` | `.ufo/waves/round-36/controls/c1-noop.out`; `.ufo/waves/round-36/c1/after.out`; `corpus/lessons/round-36.md` |
| C2 — coverage map names the published-route entry | coverage 9 → 9 (delta 0) | `named 0 file_exists 0 cited_new 0 met False` at base → `named 1 file_exists 1 cited_new 1 met True` (exit 0) | `python3 tools/round36-coverage-audit.py --repo . --tip <full-commit>` | `2e8beda5b2a2dcc62d6782838ee6e47cda04df55` | `.ufo/waves/round-36/controls/c2-base.out`; `.ufo/waves/round-36/c2/after.out`; S328, S329 |

Both scores are held. C1 corrects four statements the round-35 closure routed,
by append only: the r35 lesson blob and the r35 fleet report blob are unchanged
and the counter re-derives each correction from committed bytes. C2 adds one
coverage-map pointer the base README did not hold. No capability row enters.
Other readings held: operability 8, freshness 8, depth 7, adjacency 7.

### Frontier step (round 36)

One theme from the read-only shokuknow `corpus-expansion-1` package: a
published native route name is not the engine's current route. One admitted
entry, `corpus/knowledge/sglang-native-route-deprecation.md`, and two registry
rows, S328 and S329, each opened and located by this lane on 2026-10-24. The
scratch mirror's first build failed with E12 on both rows (appended at the end
of the file they fell outside the Registry section); the rows were re-placed
inside the table and the gate then exited 0 with 93 pre-existing W04 warnings.
The seven kama rows of the campaign absent-defect register were hand-checked:
S202, S206 and S230 are present, S200, S210 and S211 are absent, S224's
compound span does not locate. No register row is appended; S230's anchor is
carried by the lane's own S329 row. Id collision: registry 201, staged 134
(S325 to S458), collisions 1 (S327, the same document the lane already holds).
Lesson, rejects and flip conditions: `corpus/lessons/round-36.md`.

### Instrument repair in this round

`tools/round36-coverage-audit.py`'s selftest built its base arm from the tip's
README and entry paired with the base registry, and its outside arm from the
tip's README. Once the round landed, that base arm reported `met True` at a
landed tip and the selftest exited 1. Both arms now load the BASE revision's
README, entry and registry. `score()`, `PREDICATE`, `HEADING`, `ENTRY` and
`BASE` are unchanged; the measurement line is byte-identical before and after
(`.ufo/waves/round-36/c2/after.out`). The selftest exits 0 at the base tip and
at the landed tip.

### VCS incident, recorded not repaired in place

The wave-3 mutation-tester seat ran `jj commit` inside the lane repo instead of
its sandbox clone and parked the working copy on three foreign-identity commits
(`28a8bf50` "baseline", `10094ed1` "mut1", `f3517a161e` "mut2", author
`MutLessonRow sandbox <sandbox@mut.invalid>`). `jj-lane.sh commit` refuses a
non-empty working copy on a non-tip base by design, and `jj-lane.sh recover`
requires a candidate that is both a direct child of the tip and the working
copy's direct parent — no commit in the chain is both. The claim work was
therefore committed and pushed through `jj-lane.sh` in a scratch clone of the
lane remote, and the lane's own branch was advanced by `jj-lane.sh push`,
which adopted the moved remote tip through the helper's own recovery path. The
foreign commits were never pushed and are not ancestors of the branch tip. The
lane's local working copy remains parked on them; that is an operator item, not
a lane mutation, and it is filed as an L0 question.

### Planned (round 37)

Re-anchor the lane's working copy off the foreign-identity chain (operator
item, L0 filed). Outside non-author sampling of round 36, with the S211
reason, the S327 word count and the mixed-mirror description checked again
against the filed r35 lesson and r35 report, which this round did not rewrite.

## Round 37 — r36 routed corrections and the KV-cache reclamation/prefix-reuse ground (2026-10-25)

Authority: conf assigns operability 8 + calibration 7. Calibration is the lowest
non-retired numeric axis (tied with depth and adjacency at 7). MISSION.md:29
still says operability + freshness; that file was not edited and no duplicate
L0 was filed — the round-35 question stands open. Stagnation nudge inactive.
Preregistration `.ufo/waves/round-37/preregistration.json`, frozen before any
seat scored. Base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — four r36 routed statements corrected by append | calibration 7 → 7 (delta 0) | `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) at base → `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0) | `python3 tools/round37-statement-audit.py --repo . --tip <full-commit>` | see `.ufo/waves/round-37/c1/after.out` | `.ufo/waves/round-37/controls/c1-noop.out`; `.ufo/waves/round-37/c1/after.out`; `corpus/lessons/round-37.md` |
| C2 — coverage map names three KV-cache/prefix-reuse entries | coverage 9 → 9 (delta 0) | `named 0 files_exist 0 cited_new 0 met False` (exit 1) at base → `named 3 files_exist 3 cited_new 3 met True` (exit 0) | `python3 tools/round37-coverage-audit.py --repo . --tip <full-commit>` | see `.ufo/waves/round-37/c2/after.out` | `.ufo/waves/round-37/controls/c2-base.out`; `.ufo/waves/round-37/c2/after.out`; S330, S333, S334, S335, S346, S347, S363 |

Both scores are held. C1 corrects four statements the round-36 verifier routed,
by append only: the r36 lesson blob and the r36 fleet report blob are unchanged
and the counter re-derives each correction from committed bytes. C2 adds three
coverage-map pointers the base README did not hold. No capability row enters.
Other readings held: operability 8, freshness 8, depth 7, adjacency 7.

### Frontier step (round 37)

One theme from the read-only shokuknow `corpus-expansion-1` package: engine
internals that shape what a served endpoint answers — KV-cache reclamation and
prefix-cache reuse models in vLLM and SGLang. Three admitted entries
(`corpus/knowledge/kv-cache-reclamation-models.md`,
`corpus/knowledge/prefix-cache-reuse-models.md`,
`corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`) and
seven registry rows (S330, S333, S334, S335, S346, S347, S363), each opened by
this lane on 2026-10-25 and re-opened by wave-1 seats. Rejects (with flip
conditions), the id-collision record (0 collisions), the scratch validate
receipt and the quarantine hand-check are in
`corpus/lessons/round-37.md`. The D3 seat accounting (ScribeLog and RevQ206,
`rc=1`, `provider.rate_limit: 429`) is named in the round-37 fleet report.

## Round 38 — the R36-D2C correction, the SGLang docs version-pinning ground, and round-37 instrument closure (2026-10-25)

Authority: conf assigns operability 8 + calibration 7. Calibration is the lowest non-retired numeric axis (tied with depth and adjacency at 7). Stagnation nudge inactive. Preregistration `.ufo/waves/round-38/preregistration.json`, frozen at `41e149ceee28b24596b5d8567a0ccf43ebbc6d50` before any seat scored. Base `2a4a97dc890fe393035986c951797c5d65b6cc69`.

| Claim | Axis, score | Before → after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|
| C1 — the R36-D2 third sub-fact (R36-D2C) corrected by append | calibration 7 → 7 (delta 0) | `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) at base → `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0) | `python3 /fast/scratch/hyaku/kama-r38/tools/round38-statement-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>` | `d854475aecc1d793f84c10021daaed46f735f270` | `.ufo/waves/round-38/controls/c1-noop.out`; `.ufo/waves/round-38/c1/after.out`; `corpus/lessons/round-38.md` |
| C2 — coverage map names the two SGLang docs version-pinning entries | coverage 9 → 9 (delta 0) | `named 0 files_exist 0 cited_new 0 met False` (exit 1) at base → `named 2 files_exist 2 cited_new 3 met True` (exit 0) | `python3 /fast/scratch/hyaku/kama-r38/tools/round38-coverage-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>` | `d854475aecc1d793f84c10021daaed46f735f270` | `.ufo/waves/round-38/controls/c2-base.out`; `.ufo/waves/round-38/c2/after.out`; S352, S353, S472 |
| C3 — the round-37 counting instruments and the wave's 37th seat report land | operability 8 → 8 (delta 0) | `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1) at base → `found 2 base_found 0 help_ok 2 rerun_ok 2 report_37 1 receipt_ok 1 met True` (exit 0) | `python3 /fast/scratch/hyaku/kama-r38/tools/round38-operability-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>` | `d854475aecc1d793f84c10021daaed46f735f270` | `.ufo/waves/round-38/controls/c3-base.out`; `.ufo/waves/round-38/c3/after.out`; `tools/round37-statement-audit.py`; `tools/round37-coverage-audit.py`; `.ufo/waves/round-37/w1/out/CriticEntries.md`; `.ufo/waves/round-37/w1/out/seat-exit-codes.json` |

All three scores are held. C1 corrects the one statement the round-37 verifier routed as uncorrected (`corpus/lessons/round-37-verifier-spotcheck.md` §6 item 4): the round-36 Gate's range "it cites S331 to S334" names the wrong rows; the five staged rows citing that entry are S332, S336, S337, S338 and S339 (`SOURCES.append.md` lines 9, 13, 14, 15, 16). The correction is an append: the r37 lesson blob (`20f7909b6c8161f2bcc868a4472585733c81ae83`) and the r37 fleet report blob (`1c6ea9faa0e25d48f70d354e0a140bcb709ca7db`) are unchanged, and the counter re-derives the five ids from the read-only package. C2 adds two coverage-map pointers the base README did not hold, and C3 makes the round-37 counting commands reproducible from landed bytes. No capability row enters. Other readings held: freshness 8, depth 7, adjacency 7.

### Frontier step (round 38)

One theme from the read-only shokuknow `corpus-expansion-1` package: SGLang documentation version pinning. The published docs pages carry no version marker; their sources are contained unchanged in release tag v0.5.22, and the tag inventory is verifiable with `git ls-remote --tags`. Two admitted entries (`corpus/knowledge/sglang-docs-version-pinning.md`, `corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md`) and three registry rows: S352 and S353 (the v0.5.22 raw `.mdx` sources; wave-1 fetches returned HTTP 200, 6243 and 2820 bytes, receipts in `.ufo/waves/round-38/w1/out/FetchS352/` and `.../FetchS353/`), and S472, the lane's own tag-inventory row. Staged S360 (the GitHub REST `/tags` endpoint) is rejected: on this host it returned HTTP 403 with "API rate limit exceeded" (`.ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt`, `api-body.json`). Flip: a fetchable anchor for the tag inventory. The lane's `git ls-remote --tags` receipt supersedes it: exit 0 at 2026-10-25T09:12:47Z, git 2.56.0, 190 ref lines, 166 tag names, `refs/tags/v0.5.22` an annotated tag object `35ce313293052f8362e0829e7512bc9bc3d336c9` peeling to commit `baa9befa381511cd4d56f83980951e5a45fffc6d` (`.ufo/waves/round-38/assimilation/exec-tag-inventory/ls-remote-tags.txt`). Id collision: lane-vs-staged `comm -12` prints 7 round-37 adoptions (S330/S333/S334/S335/S346/S347/S363), none a duplicate id; S352/S353/S472 free in both. Scratch validate: rows + entries in a mirror pass `sources-census.sh validate --file` exit 0 (93 baseline W04). Lesson, rejects and flip conditions: `corpus/lessons/round-38.md`.

### Inherited round-37 state, resolved in this round

Commit `2f780765f09f917f876bbbd1f76768bc63c646ea` (after the freeze) lands the two counters round 37 cited but never committed (`tools/round37-statement-audit.py`, `tools/round37-coverage-audit.py`), the 37th seat report `.ufo/waves/round-37/w1/out/CriticEntries.md` (seat `L1Kama37.WetHornet`; 21012 bytes landed, against the 20238 bytes the round-37 verifier recorded at `round-37-verifier-spotcheck.md:72,196` — the difference is unexplained), and `.ufo/waves/round-37/w1/out/seat-exit-codes.json` (37 members, each `report_exists: true`, `rc: null`; the rc reason records that an in-process task seat has no OS exit code and that the round-37 wave's per-seat process records were not persisted into the lane). The receipt records which seats returned reports; it does not record exit codes, so the round-37 report's "Dead seats: none" closes as report presence, not as exit status (§6 item 3). The rest of the uncommitted round-37 tree (item 2: 29 scratch files beyond the 123 already landed — pre-fix drafts, mirrors and seat scratch) was deliberately not copied into the lane; the 37th report was. The round-38 C2 counter reads cited ids from `source:` lines only and validates them against the registry, carrying §6 item 5.

### Instrument notes (round 38)

- The committed C3 control `.ufo/waves/round-38/controls/c3-base.out` was regenerated with the repaired counters; it prints `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1), matching the preregistration's `do_nothing_control` text byte for byte. The earlier committed control (receipt_ok 1) was a stale artifact of the pre-repair disk-based receipt leg; it is superseded, not edited.
- The C2 counter was repaired before data (see lesson §Claims); `PREDICATE` and the measurement-line shape are unchanged; all three controls re-run identically at the base.
- In the C3 counter, `help_ok` and `rerun_ok` execute the working-tree files (`--repo` path), not the bytes at `--tip`; at the base they read 2 although `found` reads 0. Only `found` and `base_found` are tip-pinned.
- The C2 counter's `met` requires `cited_new == 3`; "each cites" is evaluated on the union of both entries' new ids, and per-entry new-id presence is required.
- The C1 counter gates `met` on `has_all` and on the staged-row check; it reads the r37 report blob from the fleet repo's HEAD. Wave-1 attack seats showed the C1 counter over-credits adversarial rows (a correction row plus a separate wrong-id line passes; id tokens split across lines pool) and reads the staged package's uncommitted working-tree bytes; these limits are disclosed, and the R36-D2C row is written so it passes the frozen counter without relying on either weakness.

## Round 39 — model-card field distinction and sourced coverage pointer (2026-10-25)

Authority: lane row remains operability + calibration; calibration 7 is the lowest assigned numeric axis, below operability 8. Scores remain self-assessments, not promotion.

Attempt 2 (replay-and-land): attempt 1 froze these predicates at base `6a4afdfe` and measured them there; its commits never reached the lane remote. The predicates, counters and kill rules are unchanged and are re-measured here at the replay base `d7954be870a785054287ef5d7b3690e6cca0478e`. The adopted row was staged as S472, which round 38 already holds on the lane remote for the SGLang tag inventory; it is renumbered to S473 by document (same URL and anchor) and every live citation is re-pointed.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — grounded assimilation admit/reject decisions | calibration 7 → 7 | frozen counter, base `admit=0 rejects=0 sourced_rows=0` → tip `admit=1 rejects=2 sourced_rows=1` (met=True); the declared grep string reads tip `admit=0 rejects=1 sourced_rows=1` — counter defect, see notes | frozen counter: `grep -c '^Admit ' corpus/lessons/round-39.md; grep -c '^Reject' corpus/lessons/round-39.md; grep -c '^| S473 |' corpus/SOURCES.md` (declared attempt-1 string was `grep -c 'Admit the amendment'` and undercounts) | `.ufo/waves/round-39/assimilation/{c1-noop-replay.out,claim-after-replay.out}` |
| C2 — map the created-time/catalog distinction | coverage 9 → 9 | base `round39_pointer=0 entry=0 S473=0` → tip `round39_pointer=1 entry=1 S473=1` | `grep -c 'served-identity-crosswalk-amendment-2026-10-24-r16.*| 39 |' corpus/README.md; test -f corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md; grep -c '^| S473 |' corpus/SOURCES.md` | `.ufo/waves/round-39/assimilation/{c2-noop-replay.out,claim-after-replay.out}` |

Before/after census at the replay base: rows 213 → 214; tier A 203 → 204, B 7 → 7, C 3 → 3; statuses mined 194 → 195, queued 8 → 8, rejected 11 → 11. Counting command: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md` (both exit 0; base re-derived from the `d7954be8` registry bytes, receipt `.ufo/waves/round-39/assimilation/census-replay.out`). S473 is the only added row; no prior registry cells changed.

No capability row: neither claim adds a demonstrated runnable operation. Other numeric assessments held: operability 8, freshness 8, depth 7, adjacency 7. No live endpoint was sampled. Coverage novelty remains subject to independent closure; the counter measures map/file/row presence, not semantic uniqueness against pre-existing entries.

### Round-39 closure qualification

The frozen C1 predicate is present at the working tip (admit=1, two rejects, S473=1); the counted `^Reject` lines are the two Gate rejections. C2's frozen presence predicate is present (one round-39 map row, file exists, S473=1), but an outside wave found the crosswalk already held the general OpenAI card field set, so the pointer-presence counter alone does not establish novel coverage. Hold coverage at 9; report expansion unchanged and leave independent admission to closure. No SHONEN box is promoted.

### Instrument notes (round 39)

- **C1 counter defect (disclosed, not repaired after data).** The preregistration's frozen counter is prose: "Round lesson Gate has an admit and at least one package-theme reject with reason and flip; admitted source is newly cited by the amendment, and its located quote resolves at Markdown line 17." Against committed bytes that reads `admit=1 rejects=2 sourced_rows=1`, met. Attempt 1's SCORECARD cell operationalized the admit leg as `grep -c 'Admit the amendment'`, but the lesson's admit line reads `Admit \`corpus/knowledge/...\``, so the literal string reads `admit=0`; attempt 1's `claim-after.out` (`admit=1 rejects=2`) is therefore not reproducible from the bytes it committed. The replay keeps the frozen prose counter, discloses both readings, and records the declared string's undercount rather than retuning it to pass.
- **Replay receipts replace attempt-1 receipts as evidence.** `claim-after-replay.out`, `c1-noop-replay.out`, `c2-noop-replay.out`, `census-replay.out`, `validate-replay.out`, `reg-ids-replay`, `staged-ids-replay`, `collisions-replay`, `id-choice-collision` and `renumber-map.md`. The attempt-1 files keep their bytes and are superseded.
- **Id collision.** The mechanical 0–3-space `comm -12` at the replay base returns 9 ids (S330, S333, S334, S335, S346, S347, S352, S353, S363) — all rows r37/r38 already adopted from the same staged package, none new. The real collision is the id attempt 1 *chose*: `S472` is round 38's own-work SGLang tag-inventory row (`corpus/SOURCES.md:225`), so the adopted row moves to `S473` by document.
- **Append validation.** A full repository mirror (corpus + root + `.ufo`, `.git` excluded) validates exit 0, 0 E findings, W04 warnings only: `validate-replay.out`. The mirror itself is scratch and not committed.


## Round 40 — digest citation corrections and r38 wave-evidence closure (2026-10-25)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned non-retired axis, below operability 8. Frozen base `efe25f962a0b3a2b9b111c03bb5b5386c9548195`; freeze commit `f327904b72b2ff2aa1c9668cb23aa90054098e81`.

| Claim | Axis, score | Before → after | Counting command | Result / evidence |
|---|---|---|---|---|
| C1 — correct routed r38 digests (unverified) | calibration 7 → 7 | base frozen control `s474_row=0 amend_corrected=0 r36d2c_fixed=0 false_corrections=1 met=False` → schema-valid S474 row still reads `s474_row=0`; frozen counter cannot verify its predicate | `python3 tools/round40-calibration-audit.py --repo <fresh clone> --tip <full commit> --out <receipt>` | **Unverified**: counter indexes status (`row[7]`) instead of teaches (`row[6]`); see wave reports R40A02, R40A05, R40F01. Do not treat a status-cell marker as a pass: census E07. |
| C2 — stage exact r38 spec/run evidence | operability 8 → 8 | `spec_exists=0 run_exists=0 spec_sha_ok=0 run_sha_ok=0 counts_ok=0 met=False` → `spec_exists=1 run_exists=1 spec_sha_ok=1 run_sha_ok=1 counts_ok=1 met=True` | `python3 tools/round40-operability-audit.py --repo <fresh clone> --tip <full commit> --out <receipt>` | `.ufo/waves/round-40/c2/{base,after}.out`; copies of exact r38 bytes, SHA-256 pins in frozen predicate. |

Both scalar scores held. C1's frozen instrument has a demonstrated false-accept path; its claim is reported unverified, not retuned after data. C2 is a pure staging operation.

## Round 40 measured results

C1 base-control command at frozen base: `python3 tools/round40-calibration-audit.py --repo /fast/scratch/hyaku/kama-r40 --tip efe25f962a0b3a2b9b111c03bb5b5386c9548195 --out .ufo/waves/round-40/controls/c1-base.out` → `s474_row=0 amend_corrected=0 r36d2c_fixed=0 false_corrections=1 met=False`, exit 1. C1's after-counter `met` value is **not** an admission signal because it can pass on a non-schema-compliant status value and fails the schema-valid teaches value.

C2 base: `python3 tools/round40-operability-audit.py --repo /fast/scratch/hyaku/kama-r40 --tip efe25f962a0b3a2b9b111c03bb5b5386c9548195 --out .ufo/waves/round-40/controls/c2-base.out` → `spec_exists=0 run_exists=0 spec_sha_ok=0 run_sha_ok=0 counts_ok=0 met=False`, exit 1.


### Round-40 landed-tip measurements

Measured against lane commit `2429f48e2c679048d94566a9f3e800d5278b23eb` (the counter and its required input blobs are unchanged at the final evidence commit):

- C1 command: `python3 tools/round40-calibration-audit.py --repo <fresh clone> --tip 2429f48e2c679048d94566a9f3e800d5278b23eb --out .ufo/waves/round-40/c1/after.out` → `s474_row=0 amend_corrected=1 r36d2c_fixed=1 false_corrections=0 met=False`, exit 1. **Unverified** due to the frozen counter’s index defect; no C1 score delta is claimed.
- C2 command: `python3 tools/round40-operability-audit.py --repo <fresh clone> --tip 2429f48e2c679048d94566a9f3e800d5278b23eb --out .ufo/waves/round-40/c2/after.out` → `spec_exists=1 run_exists=1 spec_sha_ok=1 run_sha_ok=1 counts_ok=1 met=True`, exit 0. Claim verified, score held.
- Census command: `sources-census.sh census --file corpus/SOURCES.md` → rows 214→215; tier A 204→205, B=7, C=3; mined 195→196, queued=8, rejected=11; missing=0. Full-mirror `sources-census.sh validate --root <mirror> kama` → exit 0, 93 W04, 0 E.

## Round 41 — head axes table reconciled to the tree (calibration) and the pin-watch capability (operability) (2026-10-25)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned non-retired axis, below operability 8; the stagnation nudge is inactive. Frozen base `8893b89466250c4d542912a867392698d2da00ce`; freeze commit `6fec0c4cd7b63ac733f2ae47fe73d1366b40c6dd` (`.ufo/waves/round-41/preregistration.json`, counters, controls). Measurement root: a fresh clone of the lane remote; the parked worktree is on the mutation-sandbox lineage (round-40 D5).

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the `## Axes` table matches observed repository state | calibration 7 → 7 | base `mismatches=16 met=False` → measured value recorded under §Round-41 measured results | `python3 tools/round41-scorecard-reconcile.py --repo <fresh clone> --tip <full commit> --out <receipt>` | `.ufo/waves/round-41/controls/base.c1.out`; `.ufo/waves/round-41/c1/after.out` |
| C2 — capability acquisition `pin-watch` (considerthese 2026-10-25 proposal 2; sourced S475, S476, S477) | operability 8 → 8, new capability row | base `tool=0 contract=0 live=0 sourced=0 capability=0 met=False` → measured value recorded under §Round-41 measured results | `python3 tools/round41-pinwatch-audit.py --repo <fresh clone> --tip <full commit> --out <receipt>` | `.ufo/waves/round-41/controls/base.c2.out`; `.ufo/waves/round-41/c2/after.out` |

**Capabilities — canonical list as of round 41**

Same four columns as the round-34 canonical list, which stays byte-intact; one row is added.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |

### Round-40 record corrections (append-only; round-40 closure defect D4)

- N3: the round-40 C2 row above cites `.ufo/waves/round-40/c2/{base,after}.out`, but `c2/base.out` was never written. The base receipt is `.ufo/waves/round-40/controls/c2-base.out`, and the after receipt is `.ufo/waves/round-40/c2/after.out`. The row stays as filed.
- N2: the round-40 report (fleet repo `.ufo/reports/round-40/kama.md`, §Sources & frontier) prints the SGLang v0.5.22 tag object as the 39-hex `35ce313293052f8362e0829e7512bc9bc3d336c`. The correct 40-hex value is `35ce313293052f8362e0829e7512bc9bc3d336c9`, as in S474 and `corpus/lessons/round-40.md`. The filed report is not edited; this correction is also recorded in `corpus/lessons/round-41.md`.

### Round-41 measured results

Measured commit: `4fe239a479bd86478912f3d79d42ec036ac9ae04`, the integration commit (lane branch tip at measurement). Measurement root: fresh clone of the lane remote.

| Claim | Base `8893b894` | Measured `4fe239a4` | Command | Receipt |
|---|---|---|---|---|
| C1 calibration 7 → 7 | `axes=6 facts=13 hash_bad=2 lines_bad=2 run_bad=0 dead=6 score_bad=2 hollow=4 mismatches=16 met=False` (exit 1) | `axes=6 facts=24 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True` (exit 0) | `python3 tools/round41-scorecard-reconcile.py --repo <clone> --tip <commit> --out <receipt>` | `.ufo/waves/round-41/controls/base.c1.out`; `.ufo/waves/round-41/c1/after.out` |
| C2 operability 8 → 8, capability `pin-watch` | `tool=0 contract=0 live=0 sourced=0 capability=0 met=False` (exit 1) | `tool=1 contract=1 live=1 sourced=1 capability=1 met=True` (exit 0; random seed 788600741, and seed 41), live reference `error=0` | `python3 tools/round41-pinwatch-audit.py --repo <clone> --tip <commit> [--seed N] --out <receipt>` | `.ufo/waves/round-41/controls/base.c2.out`; `.ufo/waves/round-41/c2/after.out`; `.ufo/waves/round-41/c2/after-seed41.out` |

Capability census (`tools/capability-repertoire-audit.py`): base `listed 6 observed 6 missing 0 unsubstantiated 0 met True` → measured `listed 7 observed 7 missing 0 unsubstantiated 0 met True` (`.ufo/waves/round-41/c2/capability-audit.out`). Sources census: rows 215 → 218 (tier A 205 → 208; mined 196 → 199). Mirror validate exit 0, 93 W04, 0 E, at start and end (`.ufo/waves/round-41/census-{start,end}-*.out`).

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. C1's counter checks that cited facts are true, not that they are relevant. Wave seats judged four of six rows weak evidence for their axis (`.ufo/waves/round-41/w1/out/R41A03.md`) and showed the counter can be met by low-cost edits (`R41A06.md`). No score moves on C1. C2's `live` leg is degenerate under total network loss (`R41B20.md`). The measured receipt's live reference shows `error=0`.

### Planned (round 42)

1. Calibration: reconcile the remaining stale self-assessment surfaces seat R41A10 itemized (SCORECARD banner, §Planned, §Saturation, head `## Capabilities` row counts), with a counter that a do-nothing control fails. Strengthen the head-table facts per `R41A03.md`.
2. Operability: counter hygiene (temporary exports removed; the live leg requires `error=0`), or pin rows for the four older vLLM docs lines (`R41C03.md`) as a coverage move.

## Round 42 — self-description surfaces reconciled (calibration), the digest-ledger capability (operability) and the engine-side K05 entry (coverage) (2026-10-25)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned non-retired axis, below operability 8; the stagnation nudge is inactive. Frozen base `0b606b03bf0b2a87b791aa537f6c72c941624cf0`; freeze commit `0bfd47abdda1f5ac21a0834654122644fc23e861` (`.ufo/waves/round-42/preregistration.json`, three counters, controls). Measurement root: a fresh clone of the lane remote; the parked worktree is still on the mutation-sandbox lineage (round-40 D5).

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the SCORECARD head and the README and PROVINCE files match observed repository state | calibration 7 → 7 | base `mismatches=40 met=False` → measured value recorded under §Round-42 measured results | `python3 tools/round42-selfdesc-reconcile.py --repo <fresh clone> --tip <full commit> --out <receipt>` | `.ufo/waves/round-42/controls/base.c1.out` |
| C2 — capability acquisition `digest-ledger` (considerthese 2026-10-25 proposal 1) plus counter hygiene | operability 8 → 8, new capability row | base `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False` → measured value recorded under §Round-42 measured results | `python3 tools/round42-digest-audit.py --repo <fresh clone> --tip <full commit> [--seed N] --out <receipt>` | `.ufo/waves/round-42/controls/base.c2.out` |
| C3 — the engine-side K05 entry, assimilated from the staged package (sourced: S478, S479) | coverage 9 → 9 | base `entry=0 rows=0 coverage=0 gate=0 census=1 met=False` → measured value recorded under §Round-42 measured results | `python3 tools/round42-capacity-audit.py --repo <fresh clone> --tip <full commit> --base 0b606b03bf0b2a87b791aa537f6c72c941624cf0 --out <receipt>` | `.ufo/waves/round-42/controls/base.c3.out` |

**Capabilities — canonical list as of round 42**

Same four columns as the round-41 canonical list, which stays byte-intact; one row is added.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |

### Round-42 measured results

Measured commit: `2c0181074050d1995baa3d752572882db62d570e`, the integration commit (lane branch tip at measurement, after the wave's findings were integrated). Measurement root: a fresh clone of the lane remote. Base `0b606b03`. The counters are the frozen bytes of freeze commit `0bfd47ab`; the two round-41 counters carry the round-42 cleanup patch (export removal, SIGTERM handler) and are scored, not frozen, by C2's `hygiene` leg.

| Claim | Base `0b606b03` | Measured `2c018107` | Command | Receipt |
|---|---|---|---|---|
| C1 calibration 7 → 7 | `r41=0 banner=4 planned=3 retired=4 saturation=3 caps=4 receipts=0 readme=11 province=5 rel=6 mismatches=40 met=False` (exit 1) | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 met=True` (exit 0) | `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip <commit> --out <receipt>` | `.ufo/waves/round-42/controls/base.c1.out`; `.ufo/waves/round-42/c1/after.out` |
| C2 operability 8 → 8, capability `digest-ledger` | `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False` (exit 1) | `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True` (exit 0; seeds 42 and 7), live reference `tokens=97 blob=88 external_ok=5 external_absent=0 unverifiable=3 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` | `python3 tools/round42-digest-audit.py --repo <clone> --tip <commit> [--seed N] --out <receipt>` | `.ufo/waves/round-42/controls/base.c2.out`; `.ufo/waves/round-42/c2/after.out`, `after-seed7.out` |
| C3 coverage 9 → 9, assimilation | `entry=0 rows=0 coverage=0 gate=0 census=1 met=False` (exit 1) | `entry=1 rows=1 coverage=1 gate=1 census=1 met=True` (exit 0) | `python3 tools/round42-capacity-audit.py --repo <clone> --tip <commit> --base 0b606b03bf0b2a87b791aa537f6c72c941624cf0 --out <receipt>` | `.ufo/waves/round-42/controls/base.c3.out`; `.ufo/waves/round-42/c3/after.out` |

Base digests: `python3 tools/digest-ledger.py scan --repo <clone> --rev 0b606b03…` → `tokens=94 blob=84 … wrong_unflagged=1 unknown=9` (exit 1). Capability census: `python3 tools/capability-repertoire-audit.py --repo <clone> --tip <commit>` base `listed 7 observed 7 missing 0 unsubstantiated 0 met True` → measured `listed 8 observed 8 missing 0 unsubstantiated 0 met True` (`.ufo/waves/round-42/c2/capability-audit-after.out`). Sources census: rows 218 → 220 (tier A 208 → 210, mined 199 → 201, queued 8, rejected 11); mirror validate exit 0 with 93 W04 and 0 E at start and end (`.ufo/waves/round-42/census-{start,end}-*.out`). Tool self-test: `python3 tools/digest-ledger.py selftest` → `selftest pass=10 fail=0`.

Separability: each claim's file set alone, scored by all three counters (`controls/sep-c{1,2,3}-only.*.out`, regenerated at the measured commit; the pre-filter C1 receipt is kept as `controls/sep-c1-only.c1.before-filter.out`). Shortcut controls all read `met=False` (`controls/junk-*.out`). `controls/probe-canon-rename.c1.out`: a renamed row of the §Round 42 canonical list now fails C1's `caps` fact.

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. What `met=True` does not show (wave findings, `corpus/lessons/round-42.md` §Wave-1 findings): C1's relevance needles are substring tests and a 15-line edit that makes the self-description less true meets the counter (R42A05, R42A13); C2's `contract` leg mirrors the tool and three cheap mutants reach `met=True` (R42B05, R42B06); C3's coverage leg is not a sourcing test (R42C06). No score moves; the closure judges relevance and sufficiency.

### Planned (round 43)

1. Calibration: the second half of `considerthese/2026-10-25.md` proposal 1 — cross-check every S-id a lesson names against the registry row it is said to be (round 36's five misattributed ids were this class), with a counter a do-nothing control fails.
2. Coverage or operability: the llama.cpp single-model `/v1/models` body and the older vLLM docs lines (R41C03) as pin rows, or the refused round-8 llama-cpp-python settings theme once a claim consumes it.


## Round 43 — instrument registry reconciled (calibration), the hexrun-census capability (operability) and the vLLM `/health` process map (coverage) (2026-10-25)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned non-retired axis, below operability 8; the stagnation nudge is inactive. Frozen base `6897ead55c24ba08c9ac0b09466d4fbfe005a459`; freeze commit `895793e0b4c56bdcb939277b8ff0251b26306d4d` (`.ufo/waves/round-43/preregistration.json`, three counters, controls). Measurement root: a fresh clone of the lane remote; the parked worktree is still on the mutation-sandbox lineage (round-40 D5).

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — SKILL.md's instrument registry, its documented self-test line, the calibration row's closure count, the SOURCES search-log correction and README's hidden entries match the tree | calibration 7 → 7 | base `mismatches=42 met=False` → measured value recorded under §Round-43 measured results | `python3 tools/round43-registry-audit.py --repo <fresh clone> --tip <full commit> --out <receipt>` | `.ufo/waves/round-43/controls/base.c1.out` |
| C2 — capability acquisition `hexrun-census` (considerthese 2026-10-25 proposal 1, the non-64 hex-run half) | operability 8 → 8, new capability row | base `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False` → measured value recorded under §Round-43 measured results | `python3 tools/round43-hexrun-audit.py --repo <fresh clone> --tip <full commit> [--seed N] --out <receipt>` | `.ufo/waves/round-43/controls/base.c2.out` |
| C3 — the vLLM `/health` process map, assimilated from the staged package (sourced: S480, S481) | coverage 9 → 9 | base `entry=0 rows=0 coverage=0 gate=0 met=False` → measured value recorded under §Round-43 measured results | `python3 tools/round43-health-audit.py --repo <fresh clone> --tip <full commit> --base 6897ead55c24ba08c9ac0b09466d4fbfe005a459 --out <receipt>` | `.ufo/waves/round-43/controls/base.c3.out` |

**Capabilities — canonical list as of round 43**

Same four columns as the round-42 canonical list, which stays byte-intact; one row is added.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |

### Round-43 measured results

Measured commit: `25df591a4e50f315b920ec0d0acba6145989e267`, the integration commit (lane branch tip at measurement; the final commit adds receipts, the end census and this section). Measurement root: a fresh clone of the lane remote. Base `6897ead55c24ba08c9ac0b09466d4fbfe005a459`. Counters are the frozen bytes of freeze commit `895793e0b4c56bdcb939277b8ff0251b26306d4d`.

| Claim | Base `6897ead5` | Measured `25df591a` | Command | Receipt |
|---|---|---|---|---|
| C1 calibration 7 → 7 | `unreg=16 defect=0 flags=2 pins=19 selftest=1 dc=1 spot=1 hidden=2 pop=28 registered=12 mismatches=42 met=False` (exit 1) | `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=31 registered=31 mismatches=0 met=True` (exit 0) | `python3 tools/round43-registry-audit.py --repo <clone> --tip <commit> --out <receipt>` | `.ufo/waves/round-43/controls/base.c1.out`; `.ufo/waves/round-43/c1/after.out` |
| C2 operability 8 → 8, capability `hexrun-census` | `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False` (exit 1) | `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True` (exit 0; seeds 43 and 7), scan `tokens=778 distinct=215 lane_oid=138 md5_blob=1 upstream_ok=65 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=0` | `python3 tools/round43-hexrun-audit.py --repo <clone> --tip <commit> [--seed N] --out <receipt>` | `.ufo/waves/round-43/controls/base.c2.out`; `.ufo/waves/round-43/c2/after.out`, `after-seed7.out` |
| C3 coverage 9 → 9, assimilation | `entry=0 rows=0 coverage=0 gate=0 refetch=1 census=1 met=False` (exit 1) | `entry=1 rows=1 coverage=1 gate=1 refetch=1 census=1 met=True` (exit 0) | `python3 tools/round43-health-audit.py --repo <clone> --tip <commit> --base 6897ead55c24ba08c9ac0b09466d4fbfe005a459 --out <receipt>` | `.ufo/waves/round-43/controls/base.c3.out`; `.ufo/waves/round-43/c3/after.out` |

Capability census: `python3 tools/capability-repertoire-audit.py --repo <clone> --tip <commit>` base `listed 8 observed 8 missing 0 unsubstantiated 0 met True` → measured `listed 9 observed 9 missing 0 unsubstantiated 0 met True`. Sources census: rows 220 → 222 (tier A 210 → 211, tier C 3 → 4, mined 201 → 203, queued 8, rejected 11); mirror validate exit 0 with 93 W04 and 0 E at start and end (`.ufo/waves/round-43/census-{start,end}-*.out`). Regression at the measured commit: the round-41 and round-42 head counters still read `mismatches=0 met=True`; `tools/digest-ledger.py scan` reads `unknown=0`; the gate reads `registered 31 unregistered 0 defective 0`; `tools/sources-append-only.py` finds no violation.

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. What `met=True` does not show (wave-1 findings, `corpus/lessons/round-43.md` §Wave-1 findings): C1 is met by one mega-row of 11 inserted lines (W1R01); C2 by a 78-line fixture-name shell tool (W1R02); C3 by a keyword-shell entry over stub copies with true but irrelevant live quotes (W1R02); 20 of 53 counter mutants survive (W1R03). The landed tree carries 19 individual rows, a content-based tool and real API copies, but the counters cannot tell it from the shortcuts. **The planned falsify wave (48 seats) was not dispatched** (run 7 closed), so no claim was attacked beyond wave 1's four early falsifiers; separability controls (each claim's file set alone) were not built. No score moves; the closure judges relevance and sufficiency.

### Planned (round 44)

1. Calibration: the descriptor-based half of the S-id cross-check (`considerthese/2026-10-25.md` proposal 1, second half): the round-36 misattributions named staged ids by description, which the URL form cannot see (`.ufo/waves/round-43/frontier/sid-prototype.out`); re-open every new SOURCES row's quote at its cited line (`considerthese/2026-10-24.md` proposal 2).
2. Coverage: the refused round-13 amendment rows (S438, S439, S442, S443) once a claim consumes the readiness column, or the llama.cpp single-model `/v1/models` body and the older vLLM docs lines as pin rows.

## Round 44 — llama.cpp release re-verification at b11889 (freshness) and the trend-verdict ledger (calibration) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned non-retired axis (tied with depth and adjacency at 7), below the saturation line 8, so the stagnation nudge is inactive. Frozen base `9d9cc93ec50783cd114829a91757b90d57c78dc6`; freeze commit `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40` (`.ufo/waves/round-44/preregistration.json`, counters `tools/round44-release-recheck-audit.py` and `tools/round44-verdict-ledger-audit.py`, controls under `.ufo/waves/round-44/controls/`). The parked worktree is attached to the lane branch again, so every round-44 commit went through `scripts/hyaku/jj-lane.sh`.

### Correction appended in round 44 (round-43 closure D1)

The round-43 tip commit `9307b15e` inserted its measured-results block inside the `## Planned` pointer sentence. Round 44 moved that block, byte for byte, under its own heading `### Round-43 measured results` immediately before `### Planned (round 44)`, and restored the pointer to name `### Planned (round 45)` (seat X9Fix, `.ufo/waves/round-44/w1/out/X9Fix/d1.diff`). No number in the block changed.

### Round-44 calibration ledger

For rounds 10–43, each LEARNING.md trend verdict the lane filed (fleet report `.ufo/reports/round-<N>/kama.md` at fleet commit `b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025`) is set beside the outside closure's verdict (`corpus/lessons/round-<N>-verifier-spotcheck.md` at lane commit `9d9cc93e`), each on a cited line: `registry/verdict-ledger.tsv`, 204 rows. Order used by the frozen counter: harmed < unchanged < unprovable < unprovable-but-better < improved — an assertion-strength order, not a merit scale.

agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15

| round | trend | self | outside | class | evidence |
|---|---|---|---|---|---|
| 10 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-10/kama.md:93` (fleet `b0fd7b7f`); outside `corpus/lessons/round-10-verifier-spotcheck.md:17` (lane `9d9cc93e`) |
| 11 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-11/kama.md:250` (fleet `b0fd7b7f`); outside `corpus/lessons/round-11-verifier-spotcheck.md:198` (lane `9d9cc93e`) |
| 12 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-12/kama.md:108` (fleet `b0fd7b7f`); outside `corpus/lessons/round-12-verifier-spotcheck.md:123` (lane `9d9cc93e`) |
| 14 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-14/kama.md:91` (fleet `b0fd7b7f`); outside `corpus/lessons/round-14-verifier-spotcheck.md:136` (lane `9d9cc93e`) |
| 15 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-15/kama.md:114` (fleet `b0fd7b7f`); outside `corpus/lessons/round-15-verifier-spotcheck.md:159` (lane `9d9cc93e`) |
| 16 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-16/kama.md:156` (fleet `b0fd7b7f`); outside `corpus/lessons/round-16-verifier-spotcheck.md:174` (lane `9d9cc93e`) |
| 17 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-17/kama.md:101` (fleet `b0fd7b7f`); outside `corpus/lessons/round-17-verifier-spotcheck.md:217` (lane `9d9cc93e`) |
| 18 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-18/kama.md:130` (fleet `b0fd7b7f`); outside `corpus/lessons/round-18-verifier-spotcheck.md:126` (lane `9d9cc93e`) |
| 19 | expansion | improved | unchanged | overclaim | self `.ufo/reports/round-19/kama.md:108` (fleet `b0fd7b7f`); outside `corpus/lessons/round-19-verifier-spotcheck.md:162` (lane `9d9cc93e`) |
| 19 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-19/kama.md:115` (fleet `b0fd7b7f`); outside `corpus/lessons/round-19-verifier-spotcheck.md:170` (lane `9d9cc93e`) |
| 27 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-27/kama.md:121` (fleet `b0fd7b7f`); outside `corpus/lessons/round-27-verifier-spotcheck.md:219` (lane `9d9cc93e`) |
| 28 | expansion | improved | unprovable-but-better | overclaim | self `.ufo/reports/round-28/kama.md:203` (fleet `b0fd7b7f`); outside `corpus/lessons/round-28-verifier-spotcheck.md:198` (lane `9d9cc93e`) |
| 29 | expansion | unchanged | improved | underclaim | self `.ufo/reports/round-29/kama.md:136` (fleet `b0fd7b7f`); outside `corpus/lessons/round-29-verifier-spotcheck.md:69` (lane `9d9cc93e`) |
| 34 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-34/kama.md:204` (fleet `b0fd7b7f`); outside `corpus/lessons/round-34-verifier-spotcheck.md:89` (lane `9d9cc93e`) |
| 35 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-35/kama.md:63` (fleet `b0fd7b7f`); outside `corpus/lessons/round-35-verifier-spotcheck.md:114` (lane `9d9cc93e`) |
| 39 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-39/kama.md:47` (fleet `b0fd7b7f`); outside `corpus/lessons/round-39-verifier-spotcheck.md:76` (lane `9d9cc93e`) |
| 40 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-40/kama.md:294` (fleet `b0fd7b7f`); outside `corpus/lessons/round-40-verifier-spotcheck.md:93` (lane `9d9cc93e`) |
| 43 | discernment | unchanged | improved | underclaim | self `.ufo/reports/round-43/kama.md:102` (fleet `b0fd7b7f`); outside `corpus/lessons/round-43-verifier-spotcheck.md:97` (lane `9d9cc93e`) |

What the figures say:

- **The lane never wrote `improved` for discernment before its closure; 15 of the 16 underclaims are that pair (self `unchanged`, outside `improved`).** Every self report was committed before the spot-check that judged it (lag 0 to 258 minutes, `.ufo/waves/round-44/w1/out/S2Calib/timing.tsv`), and LEARNING.md makes discernment `improved` wait on the outside spot-check agreeing with the gate. A filed `unchanged` with the owed act named was true when it was written; the closure then supplied the act. These rows are ordering pairs, not calibration failures, and the ledger keeps them visible as underclaims.
- **The sixteenth underclaim** is round 29 expansion: the lane applied a serving-surface bar stricter than LEARNING.md's entry bar.
- **Both overclaims are expansion credited before admission:** round 19 (one new source row counted as expansion; closure: "LEARNING's `improved` row needs" an admitted entry or capability) and round 28 (wave evidence counted as landed ground; closure: `unprovable-but-better`). Both closures recorded the disagreement at the time.
- **Absent (15 keys):** round 38's report gives axis verdicts in its `# Trends` section and no LEARNING trend verdict (3 self keys); rounds 20–23 have no lane spot-check file (12 outside keys). Their outside verdicts exist outside the frozen path, in the fleet `MANIFEST.json` closure entries' `trends` objects (rounds[397], [406], [418], [428]): read against the lane's filed verdicts they are 11 agreements and one sign reversal, round 23 quality (self `improved`, closure `harmed`), which this file already recorded in §Round24 (the line beginning "Outside closure rounds[428] supersedes"). The ledger carries those verdicts in its notes.
- **Cross-check:** every one of the 90 non-absent outside verdicts equals the `trends` object of the same round's `MANIFEST.json` closure entry (`python3 .ufo/waves/round-44/c2/manifest-crosscheck.py registry/verdict-ledger.tsv <fleet>/MANIFEST.json` → `outside_rows_compared=90 agree=90 diff=0 absent_with_manifest=12`, receipt `.ufo/waves/round-44/c2/manifest-crosscheck.out`).
- **What the ledger measures:** whether a filed verdict survived the closure that decides the round. It is concurrence with the deciding authority, written after and with the self report in view (seat K2Design), not an independent calibration measure; it is the lane's first ledger of that concurrence across all its closures, not the first surface to note a disagreement (round 23 was noted in round 24).

### Round-44 measured results

Measured commit: `ef76777e5fbdc39a80ec7a93e41dc177366168db`, the integration commit (lane branch tip at measurement; the next commit adds these receipts, the end census and this section). Measurement root: a fresh clone of the lane remote. Base `9d9cc93e`. Counters are the frozen bytes of freeze commit `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40`.

| Claim | Base `9d9cc93e` | Measured `ef76777e` | Command | Receipt |
|---|---|---|---|---|
| C1 freshness 8 → 8 | `pop=91 rows=0 valid=0 unverified=91 … section=0 met=False` (exit 1) | `pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=82 reworded=3 drifted=0 removed=0 flags_missing=0 section=1 met=True` (exit 0) | `python3 tools/round44-release-recheck-audit.py --repo <clone> --tip <commit> --upstream <llama.cpp clone> --out <receipt>` | `.ufo/waves/round-44/controls/base.c1.out`; `.ufo/waves/round-44/c1/after.out` |
| C2 calibration 7 → 7 | `rows=0 valid=0 missing=204 … met=False` (exit 1) | `rows=204 valid=204 missing=0 bad=0 agree=69 overclaim=2 underclaim=16 other=0 absent=15 table_missing=0 table_extra=0 summary=1 axes=1 met=True` (exit 0) | `python3 tools/round44-verdict-ledger-audit.py --repo <clone> --tip <commit> --fleet <fleet repo> --out <receipt>` | `.ufo/waves/round-44/controls/base.c2.out`; `.ufo/waves/round-44/c2/after.out` |

Separability (`.ufo/waves/round-44/measured/separability-c{1,2}only.out`): C1's files alone on the freeze tree read C1 `met=True`, C2 `missing=204 met=False`; C2's files alone read C2 `met=True`, C1 `unverified=91 met=False`. Regression at the measured commit: gate `registered 33 unregistered 0 defective 0` and `GATE_SELFTEST pass=6 fail=0` (`measured/gate-check.out`, `c1/gate-selftest-tip.out`); round-41 head counter `mismatches=0 met=True`; round-43 registry counter `mismatches=0 met=True`; round-42 self-description counter `mismatches=2` at `ef76777e` (banner and `### Planned (round 45)`, both written by this section's commit). Capability census `listed 9 observed 9 missing 0 unsubstantiated 0 met True` (no capability row added). Sources census: rows 222 → 224 (tier A 211 → 213, mined 203 → 205, queued 8, rejected 11); validate exit 0 at start and end with 93 W04, 1 W01, 0 E (`.ufo/waves/round-44/census/`).

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. What `met=True` does not show: both counters accept shortcut ledgers (seat K1Cheat: a mass `holds-reworded` or `drifted` ledger with filler notes meets C1; seat K2Cheat: the unread automatic draft plus a generated table meets C2). The landed ledgers are the read ones — 15 executors and 8 independent critics for C1 (90/91 agree), 9 executors, 6 independent reviewers and K2Design for C2 (204/204 verdicts agree, one line choice differs) — but the counters cannot tell them from the shortcuts.

### Planned (round 45)

1. Freshness: re-verify the b11755-dependent rows outside the round-44 population (S038, S477, S041/S046/S055, the `ggml-org/ggml` rows S014/S058) and the changed non-llama.cpp pins seat U9Pins found (S010, S019, S048), with a counter whose `drifted` and `holds-reworded` branches need a machine witness (K1Cheat F1/F2).
2. Calibration: add the outside verdicts of rounds 20–23 (fleet `MANIFEST.json` `trends`) to the ledger under a widened outside path, and score round 44's own trend verdicts once its closure lands.

## Round 45 — ten planned rows re-verified with machine witnesses (freshness) and the claim-outcome ledger (calibration) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned non-retired axis (tied with depth and adjacency at 7), below the saturation line 8, so the stagnation nudge is inactive. Base `6b8ccfb310de339e9452514aea3a9402a970c3e6` (round-44 spot-check); freeze commit `1641aa076647754b0b6b7017cd4a86b7501ecb8c` (`.ufo/waves/round-45/preregistration.json`; counters `tools/round45-recheck-audit.py` and `tools/round45-claim-outcome-audit.py`; controls `.ufo/waves/round-45/controls/`). C2 amendment v2 (`tools/round45-claim-outcome-audit-v2.py`, `.ufo/waves/round-45/preregistration-amendment-c2.json`, commit `85977699b4afe2a1d5a9eea491d431146d97286a`) was committed before any C2 ledger row existed; both counters are reported.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the ten round-44-planned rows (11 keys) re-verified against current upstream, each class re-derived by the counter from committed evidence (sourced: S484, S485) | freshness 8 → 8 | base `unverified=11 met=False` → measured value under §Round-45 measured results | `python3 tools/round45-recheck-audit.py --repo <fresh clone> --tip <full commit> --fetch --out <receipt>` | `.ufo/waves/round-45/controls/base.c1.out`; `registry/recheck-r45.tsv` |
| C2 — every claim the lane declared in rounds 10–44 ledgered self against outside on cited lines | calibration 7 → 7 | base `missing=126 met=False` → measured value under §Round-45 measured results | `python3 tools/round45-claim-outcome-audit.py --repo <fresh clone> --tip <full commit> --fleet <fleet repo> --out <receipt>` (and `-v2.py`) | `.ufo/waves/round-45/controls/base.c2.out`; `registry/claim-outcome-ledger.tsv` |

### Round-45 claim-outcome ledger

For each of the 63 claims the lane declared in rounds 10–44, the outcome the lane filed (fleet report `.ufo/reports/round-<N>/kama.md` at fleet commit `6105c5870859f15ba5372ccbe3835d65b0d9d38b`) is set beside the outcome the outside closure gave it (`corpus/lessons/round-<N>-verifier-spotcheck.md` at lane commit `6b8ccfb3`; for rounds 20–23, the kama closure entry of the fleet `MANIFEST.json` at the same fleet commit): `registry/claim-outcome-ledger.tsv`, 126 rows, each citing the line that states the outcome. Order used for the classes: not-met < unprovable < partial < unprovable-but-better < met — an assertion-strength order, not a merit scale.

agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1

| round | claim | self | outside | class | evidence |
|---|---|---|---|---|---|
| 24 | C1 | mixed | unprovable | other | self `.ufo/reports/round-24/kama.md:63` (fleet `6105c587`); outside `corpus/lessons/round-24-verifier-spotcheck.md:14` (lane `6b8ccfb3`) |
| 26 | C1 | not-met | unprovable | underclaim | self `.ufo/reports/round-26/kama.md:240` (fleet `6105c587`); outside `corpus/lessons/round-26-verifier-spotcheck.md:118` (lane `6b8ccfb3`) |
| 28 | C1 | met | not-met | overclaim | self `.ufo/reports/round-28/kama.md:278` (fleet `6105c587`); outside `corpus/lessons/round-28-verifier-spotcheck.md:65` (lane `6b8ccfb3`) |
| 40 | C1 | not-met | unprovable | underclaim | self `.ufo/reports/round-40/kama.md:14` (fleet `6105c587`); outside `corpus/lessons/round-40-verifier-spotcheck.md:49` (lane `6b8ccfb3`) |

What the figures say:

- **At claim level the lane's filed outcomes survive their closures: 58 of 61 comparable claims agree.** The trend-level ledger of round 44 found 16 underclaims, 15 of them discernment filed before the closure existed; at claim level the lane neither systematically underclaims nor overclaims.
- **The one overclaim is round 28 C1:** the lane filed C1 met under both A0 and A1 while disclosing that A1 was adopted after a seat scored and that a type-only shortcut met A0; the closure ruled that C1 does not verify under its own rule. The disclosure was honest; the filed outcome was not the frozen rule's.
- **The two underclaims (rounds 26 and 40, C1) are both rejections**, filed by the lane as `not-met` (honest stop, unverified) and ruled `unprovable` by the closure; they differ by the order, not in direction. Round 24 is the `other` key: the lane filed C1 as "not achieved/unprovable in full", the closure as `unprovable`.
- **Absent (1 key):** the round-10 closure (17 lines) admits the round and names only C3, so no line gives C1 an outcome.
- **What the counters read.** Both frozen readers fail to read part of the true evidence (receipts under §Round-45 measured results): self reports of rounds 16–21, 30, 32 and 34 state outcomes as before→after measurements with no outcome word; file-context attribution gives an outcome to the wrong claim when one line or section discusses two claims (round 10 self line 50, round 11 outside line 9, round 19 outside line 176, round 21 outside line 10587); and `met on the frozen counter; NOT admitted` (rounds 25 and 31) is read as `met` where the ledger records `partial`. The ledger cites the line that states the outcome, not a line that happens to parse.

### Round-45 measured results

Measured commit: `21945c6125c2fae531be94d7652ee058c68e5f83` (fresh clone of the lane remote). Base `6b8ccfb3`. Counters: frozen bytes of `1641aa07`; C2 v2 of `85977699`.

| Claim | Base | Measured `21945c61` | Command | Receipt |
|---|---|---|---|---|
| C1 freshness 8 → 8 | `unverified=11 met=False` (exit 1) | `pop=11 rows=11 valid=11 unverified=0 unchanged=3 holds=8 reworded=0 drifted=0 removed=0 flags_missing=0 section=1 newrows=2 fetch=1 fetch_bad=0 met=True` (exit 0) | `python3 tools/round45-recheck-audit.py --repo <clone> --tip <commit> --fetch` | `.ufo/waves/round-45/controls/base.c1.out`; `.ufo/waves/round-45/c1/after.out` |
| C2 calibration 7 → 7 | `missing=126 met=False` (exit 1) | v1 `valid=91 bad=35 agree=34 overclaim=1 underclaim=2 other=1 absent=0 consistency_bad=1 summary=0 axes=1 met=False` (exit 1); v2 `valid=103 bad=23 agree=40 … consistency_bad=1 summary=0 met=False` (exit 1) | `python3 tools/round45-claim-outcome-audit[-v2].py --repo <clone> --tip <commit> --fleet <fleet>` | `.ufo/waves/round-45/c2/c2-v1.out`, `c2-v2.out` |

C2 is **not achieved** under the frozen counter or the amendment: an honest stop. The ledger and its reading (`agreement=58/61`) stand as evidence; the counters cannot certify them (lesson §Mistakes row 2, KQ65). Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. The planned wave did not run (dispatch stalled at 32 of 64 spawned), so neither claim was attacked by a seat.

### Planned (round 46)

1. Calibration: re-freeze a claim-outcome counter that reads a hand-picked sample of true outcome lines (KQ65) and re-score `registry/claim-outcome-ledger.tsv` unchanged; route the 23 unreadable rows as the sample.
2. Freshness: llama.cpp releases after b11889 (b11897 at the round-45 sample) for the 91 round-44 rows and S484/S485, and the floating-series rows S013, S022.

**Capabilities — canonical list as of round 46**

Same four columns as the round-43 canonical list, which stays byte-intact; one row is added.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |
| append-only-audit | Set the lane's five append-only self-description files (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md) against its git history: list every commit that deletes >= 20 lines from one of them, report how many of those lines the file holds again at the audited revision and which later commit first restored all of them, and exit 1 on a partial or unrestored mass deletion | `tools/append-only-audit.py`; `tools/round46-append-audit-check.py`; run `python3 tools/append-only-audit.py --repo . --to <commit> --json` | 46 |

## Round 46 — llama.cpp release re-verification at b11906 with machine witnesses (freshness) and the append-only-audit capability (calibration) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each), and C2 works calibration; calibration is below the saturation line 8, so the stagnation nudge is inactive. Base `0163fea2dab3f282ebd70c71da9ab5de4cedf733` (round-45 spot-check); freeze commit `5790944350ae41bfe2ce50934bba59e086e747f4` (`.ufo/waves/round-46/preregistration.json`; counters `tools/round46-release-recheck-audit.py` and `tools/round46-append-audit-check.py`; controls `.ufo/waves/round-46/controls/`; KQ64 receipt `.ufo/waves/round-46/freeze/prereg-time-check.out` exit 0). The capability tool `tools/append-only-audit.py` landed after the freeze at `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, before the wave.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the 91 on-release llama.cpp rows re-verified at b11906 (`4d71b42f`) with a machine witness for every reworded, drifted or removed verdict; b11906 registered (sourced: S486, S487) | freshness 8 → 8 | base `unverified=91 section=0 newrow=0 met=False` → measured value under §Round-46 measured results | `python3 tools/round46-release-recheck-audit.py --repo <fresh clone> --tip <full commit> --upstream <llama.cpp clone> --out <receipt>` | `.ufo/waves/round-46/controls/base.c1.out`; `registry/release-recheck-b11906.tsv` |
| C2 — capability `append-only-audit`: the lane's append-only self-description set against its history, matching an independent recomputation on a random fixture and on the lane, entered in the capability table (considerthese/2026-10-26.md proposal 1) | calibration 7 → 7 (capability acquisition) | base `selftest=0 fixture=0 lane=0 table=0 met=False` → measured value under §Round-46 measured results | `python3 tools/round46-append-audit-check.py --repo <fresh clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-46/controls/base.c2.out`; `tools/append-only-audit.py` |

Controls (all `met=False`, `.ufo/waves/round-46/controls/`): C1 carry-forward of the b11889 ledger `valid=71 unverified=20`; C1 mass `holds-reworded` with boilerplate witnesses `valid=6 unverified=85`; C2 a tool replaying the lane's events fixed at build time `fixture=0`; C2 the event finder without restoration `fixture=0 lane=0`.

### Round-46 append-only audit

The lane treats five files as append-only — `SCORECARD.md`, `LOG.md`,
`corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`; earlier outside
closures read a round's SCORECARD diff as `+65/−0` / "0 removed lines" and called
that append-only (`corpus/lessons/round-29-verifier-spotcheck.md:32`,
`corpus/lessons/round-30-verifier-spotcheck.md:41`). `python3
tools/append-only-audit.py --repo <lane> --to 4a2a4d55` sets that description
against 294 commits and exits **1**:

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 status=partial restored_by=-
event 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial restored_by=-
event 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_at_tip=375 status=restored restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/README.md deleted=663 restored_at_tip=663 status=restored restored_by=82b5e9d33a19
summary commits=294 events=5 restored=3 partial=2 unrestored=0
```

The same command at `0163fea2` (292 commits) and at the tip as read (`96d32918`,
295 commits) reports the same five events, so the picture is not an artifact of one
revision. Five is the count **above the frozen threshold**: `--threshold 1` on
the same tree reports 66 events (SCORECARD 23, SOURCES 20, LOG 13, README 8,
QUALITY 2; 11 restored, 6 partial, 49 unrestored) and exits 1. "Append-only"
here is a statement about deletions of >= 20 lines in one commit, not a
byte-level property of the five files.

**The three restored events are one bug and one repair.** `0718b6ab` (round-45
integration, 2026-10-26 07:46) deleted 2,290 lines of `LOG.md`, 663 of
`corpus/README.md`, 375 of `corpus/QUALITY.md` and 2,417 of `SCORECARD.md` — 5752
deletions against 565 insertions in that commit. `82b5e9d3` (07:50, "restore
SCORECARD/LOG/QUALITY/README bodies truncated by the previous commit (append
bug)") put them back text-for-text: `LOG.md` 2290/2290, `corpus/README.md`
663/663, `corpus/QUALITY.md` 375/375, `SCORECARD.md` 2416/2417 (`git show
--numstat 82b5e9d3 -- SCORECARD.md` → `2428 0`, a pure addition). No body line of those four files was lost.

**The two partials are the SCORECARD head, which the file declares re-derived.**
The round-42 event `dd9f5dc6` removed 31 lines, and 24 are held again:

- 23 came back in the same commit as archived blocks under §Historical head
  sections — the round-5 banner (8 lines), the round-5 plan (9) and the round-3
  Retired block (6);
- 1 (`## Saturation`) is held only because the current head carries the same
  heading; its archived copy was retitled `### Saturation (round-10 text)`;
- the 7 not held are the six round-41 `## Axes` rows and the round-41 reconcile
  sentence. The rows survive only as re-anchored rows (`depth` in that diff:
  `SKILL.md` sha256 `151023b9…`, 1375 lines, `grep -c '^## '` → `30`; at the tip
  `3046955b…`, 1432 lines, `33` — `git show dd9f5dc6^1:SCORECARD.md | grep -c
  151023b99bec` → `1`, `grep -c 151023b99bec SCORECARD.md` → `0`), and the
  round-41 sentence survives only inside the tip line (`grep -c 'Reconciled in
  round 41 against the measured commit' SCORECARD.md` → `1`).

The round-45 event `0718b6ab` left exactly one line unrestored of its 2,417: the
pre-round-45 `depth` row (`SKILL.md` sha256 `91440eb8…`, 1420 lines, `32`
headings), replaced inside the repair commit by the re-anchored row
(`3046955b…`, 1432, `33`): `git show 82b5e9d3^1:SCORECARD.md | grep -c 3046955b`
→ `0`, `git show 82b5e9d3:SCORECARD.md | grep -c 3046955b` → `1`.

What that means for the claim "SCORECARD.md is append-only":

- For the record it holds. No round section, correction row, historical table
  or capability row is among the unrestored lines; `unrestored=0`, and the
  three mass deletions of body text were repaired text-for-text.
- For the head it does not, and the file itself says so: `SCORECARD.md:6`
  declares the `## Axes` table, §Planned, §Retired, §Saturation and
  §Capabilities re-derived from the tree by `tools/round42-selfdesc-reconcile.py`
  since round 42. Both partials are that carve-out exactly — 7 superseded head
  lines in round 42, 1 superseded head row in round 45.
- The head's own promise is wider than its practice. `SCORECARD.md:6` says "the
  round-5 banner and the head sections they replace are kept verbatim under
  §Historical head sections"; the round-5 banner, round-5 plan and round-3
  Retired block are (23 lines), but the `## Axes` rows it re-derives are not
  archived — the six round-41 rows and the round-45 `depth` row exist only in
  git history. Either those rows are appended under §Historical head sections,
  or the sentence is narrowed to the blocks that are.

**Limits of the instrument, read off its own output and source.**

- `restored_by=-` on a partial is definitional — no later commit holds *every*
  deleted line — and does not mean nothing was restored: `82b5e9d3` holds
  2416/2417 counted lines (1789/1790 unique) of the SCORECARD event.
- `restored_at_tip` is set membership, not position or identity: a deleted line
  that recurs as another line counts, which is how `## Saturation` is "held".
- The filter at `tools/append-only-audit.py:102` (`not x.startswith("---")`)
  drops deleted lines whose *text* begins `--`, as if each were the `---`
  header: four `--out …` lines in the SCORECARD event
  (`git show 0718b6ab^1:SCORECARD.md | grep -c '^--out '` → `4`; at the tip →
  `4`) and two (`--tip …`, `--rev …`) in the LOG event. A header-aware recount
  (`.ufo/waves/round-46/w1/out/S2Events/recount.py`) reads `2421`/`2420` for SCORECARD and
  `2292`/`2292` for LOG; no verdict class changes, and the counter
  `tools/round46-append-audit-check.py:115` carries the same filter, so tool and
  counter agree on the undercount.

**Verdict.** The five-file append-only self-description survives its own history
at mass-deletion scale: 0 unrestored, 3 repaired text-for-text after a real
truncation, 2 accounted head re-derivations, 0 lost record lines. It does not
survive as a literal whole-file claim; the honest form is that the record is
append-only while the head is re-derived, and the head's superseded rows are not
archived. The instrument is red at the tip (exit 1) and this section reports the
red, not a green.

---

## Seat notes — S2Events (not part of the section text above)

### Provenance of every figure

| Figure | Command | Exit | Receipt |
|---|---|---|---|
| 5 events / 3 restored / 2 partial / 0 unrestored at `4a2a4d55`, 294 commits | `python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` | 1 | `audit-at-4a2a4d55.out` |
| same 5 events at `0163fea2`, 292 commits | same with `--to 0163fea2dab3f282ebd70c71da9ab5de4cedf733` | 1 | `audit-at-0163fea2.out` |
| same 5 events at tip `96d32918`, 295 commits | same with `--to HEAD` | 1 | `audit-at-head.out` |
| 66 events (11/6/49) at threshold 1 | same with `--threshold 1 --json` | 1 | `audit-threshold1.json` |
| `AOA_SELFTEST pass=10 fail=0` | `python3 tools/append-only-audit.py --selftest` | 0 | `selftest.out` |
| header-aware 2421/2420, 2292/2292, 31/24, 663/663, 375/375 | `python3 <out>/S2Events/recount.py <lane> 4a2a4d55` | 0 | `recount.out` |
| C2 legs at `4a2a4d55`: `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_partial=2 met=False` | `python3 tools/round46-append-audit-check.py --repo <lane> --tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --scratch <scratch>` | 1 | `c2-counter-at-4a2a4d55.out` |
| SCORECARD event breakdown 8/1/6/9/6/1 = 31 | `git diff --no-renames --no-color --no-ext-diff -U0 dd9f5dc6^1 dd9f5dc6 -- SCORECARD.md` | 0 | `recount.out`, this note |
| 2416/2417 held by `82b5e9d3`; `2428 0` numstat | `git show --numstat 82b5e9d3 -- SCORECARD.md` + counted intersection | 0 | `recount.out` |
| no round section/correction row among unrestored lines | `recount.out` `absent:` lines: six `## Axes` rows + one reconcile sentence | 0 | `recount.out` |

`table=0` at `4a2a4d55` is expected: the C2 counter's table leg needs the
capability row naming `append-only-audit` with last cell `46`, which is this
round's entry and lands with the measured commit. The measured result belongs to
§Round-46 measured results, not to this paragraph.

### Findings

**F1 (instrument, frozen) — the `---` filter also drops `--…` content lines.**
`tools/append-only-audit.py:102` and `tools/round46-append-audit-check.py:115`
both read `not x.startswith("---")`. After the diff marker is stripped, a
deleted content line that begins `--` (a wrapped `--out`, `--tip`, `--rev`) is
excluded as if it were the `---` header, contradicting the docstring ("the
`---` header excluded"). Evidence: `git show 0718b6ab^1:SCORECARD.md | grep -c
'^--out '` → `4`; the SCORECARD event reads `deleted=2417` where the
header-aware count is `2421` (LOG: `2290` vs `2292`). Verdict classes
unchanged. Proposed fix (not applied — both files are frozen; the counter
carries `counter_sha256 4dcfbe10…`):

```diff
-            dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]
+            body = d.split("\n")
+            dele = [x[1:] for i, x in enumerate(body) if x.startswith("-")
+                    and not (x.startswith("---") and i + 1 < len(body) and body[i + 1].startswith("+++"))]
```

Applied to the frozen tool, this changes two `deleted`/`restored_at_tip` pairs
and no `status`/`restored_by` value, so C2's `lane` leg still agrees if both
copies take the fix in the same round.

**F2 (self-description) — §Historical head sections covers less than
`SCORECARD.md:6` promises.** The sentence says "the round-5 banner and the head
sections they replace are kept verbatim under §Historical head sections". The
`## Axes` rows re-derived in rounds 42 and 45 are not archived: `grep -c
151023b99bec SCORECARD.md` → `0`, `grep -c 91440eb8 SCORECARD.md` → `0`, both
present in the pre-change files (`git show dd9f5dc6^1:SCORECARD.md`,
`git show 0718b6ab^1:SCORECARD.md`, each `1`). Proposed narrowing of the
sentence at `SCORECARD.md:6` (full proposed line text in
`proposed-scorecard-head-line6.txt`):

> … the round-5 banner, the round-5 plan and the round-3 Retired and round-10
> Capabilities blocks they replace are kept verbatim under §Historical head
> sections; the superseded `## Axes` rows are kept in git history only.

The alternative fix — appending each superseded row as a dated line under
§Historical head sections — is what would make the claim unqualified but adds
about seven lines per re-anchoring round.

**F3 (contract limit, disclosed, no fix).** `restored_by` is null for a partial
by definition, so the check cannot name the commit that restored the bulk of a
partially restored file (`82b5e9d3`, 2416/2417). That is the frozen contract,
not a defect; the paragraph states it so a reader does not read `-` as "nothing
came back".

### Out of scope / not done

- The capability-table row for `append-only-audit` (C2's `table` leg) is not
  added here; that is the round's capability entry.
- No counter, preregistration or control was edited; the F1 fix is proposed
  only, in this directory.
- No measured-commit receipt is filed: the measured commit does not exist yet;
  this paragraph reports `4a2a4d55`, `0163fea2` and `96d32918`.

### What `met=True` does not show (round-46 wave attacks)

- **C1 verdicts are machine-checked text, not meaning.** Seat K1Cheat greens 91/91 rows with a two-second script from git alone: 17 of the 20 read rows are verified by text relocation, which the preregistration names as the verification itself, but the three `holds-reworded` rows on the byte-identical `server.cpp` (S037, S043, S108) can be rubber-stamped with auto-picked witnesses and a 40-character note. Critics K1R01–K1R10 each showed a range choice the counter accepts for a wrong or weaker verdict (a guard-omitting single-line `holds`, a decoy-witnessed `drifted`, positional range pairing); the S121 case was caught and corrected in the ledger (lesson §Gate). Seat V1Code: `check-fragment.py` prints `VALID` for an id outside the population (F1) and exits 0 when rows are invalid (F4); the counter's `removed` rule checks only the first line of each range (F2) and exits 1, not 2, on a non-git exception (F3). Seat M1Ctr: 46 counter mutants, 43 killed, 3 equivalent. The flag leg reads only `corpus/knowledge/*.md`, so a drifted row used by `SKILL.md` alone could not be flagged (K1R07); no row drifted this round.
- **C2's "independent recomputation" shares the tool's definition.** Both drop deleted lines that begin with `--` (lesson §Mistakes, shared-definition row; seat K2Hist: lane counts low by 4 and 2, a 21-line fixture deletion read as 0 events); seat X2Fixture found 7 fixtures where tool and counter agree and both differ from a byte-exact oracle (6 of them a ≥20-line deletion passing with exit 0). Seat K2Cheat built three non-capabilities that reach `met=True` (importing the counter's own `recompute`, recognising the fixture's shape, exec of the genuine tool); seat M2Ctr: 12 of 32 counter mutants survive, and the pristine counter accepts a tool whose default threshold is 21; seat M2Tool: 10 of 39 tool mutants survive the selftest and the counter. Seat K2Design: three of the five files are declared append-only nowhere in the lane, and `restored` counts same-commit relocations and blank lines. These are routed to round 47 (planned item 2), not fixed in place: the tool stays on the frozen definition, which the counter is.
- **Separability holds** (seat N2Couple): the counters read disjoint surfaces; a C1-shaped SOURCES append creates no C2 event and the C2 capability line changes no C1 output.

### Round-46 measured results

Measured commit: `4340cf2f68ebbfb618086e16825c2e7effd7fa58` (fresh clone of the lane remote; upstream: a bare clone of `https://github.com/ggml-org/llama.cpp.git` holding every pin and b11906). Base `0163fea2`. Counters: frozen bytes of `5790944350ae41bfe2ce50934bba59e086e747f4`.

| Claim | Base | Measured `4340cf2f` | Command | Receipt |
|---|---|---|---|---|
| C1 freshness 8 → 8 | `unverified=91 section=0 newrow=0 met=False` (exit 1) | `pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=81 reworded=4 drifted=0 removed=0 flags_missing=0 section=1 newrow=1 met=True` (exit 0) | `python3 tools/round46-release-recheck-audit.py --repo <clone> --tip <commit> --upstream <llama.cpp clone>` | `.ufo/waves/round-46/controls/base.c1.out`; `.ufo/waves/round-46/measured/c1-after.out` |
| C2 calibration 7 → 7 (capability) | `selftest=0 fixture=0 lane=0 table=0 met=False` (exit 1) | `selftest=1 fixture=1 lane=1 table=1 lane_events=5 lane_unrestored=0 lane_partial=2 met=True` (exit 0) | `python3 tools/round46-append-audit-check.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-46/controls/base.c2.out`; `.ufo/waves/round-46/measured/c2-after.out` |

Regressions at `4340cf2f` (`.ufo/waves/round-46/measured/`): round-41 head counter `mismatches=0 met=True`; round-42 self-description counter `mismatches=0 maxN=46 met=True`; gate `registered 38 unregistered 0 defective 0`; capability census `listed 10 observed 10 missing 0 unsubstantiated 0 met True`; `append-only-audit --selftest` `pass=10 fail=0`; seat yield `seats=65 reports=65 missing=0` (exit 0). Three harms the measured commit introduced, corrected in the next commit (lesson §Mistakes): the round-43 registry counter read `spot=1 mismatches=1 met=False` because the re-anchored calibration row broke its `(outside closures on record)` pattern; `digest-ledger` unknown 2 → 5 and `hexrun-census` unknown 21 → 26 (b11906 binary digests, b11906/b11907 commits and blobs, the S013 re-pin commit) — five digest-ledger rows (two of them the round-45 b11889 leftovers) and five hexrun-ledger rows with evidence `.ufo/waves/round-46/hexrun-evidence/` are appended; tip receipts follow under the same directory (`*-fix.out`). Both scans stay exit 1 on their pre-existing unknowns (digest 2 → 0 not claimed; hexrun 21 at base).

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Capabilities 9 → 10 (`append-only-audit`, first-working round 46).

### Planned (round 47)

1. Calibration: the claim-outcome reader re-freeze routed by the round-45 closure (D1), scored first against the round-46 hand-read sample (`.ufo/waves/round-46/w1/out/S8Sample{1,2,3}/sample.tsv`, `R8Sample/sample.tsv`) before it reads `registry/claim-outcome-ledger.tsv`; or `append-only-audit` v2 with a `git diff --numstat` cross-check for `--`-prefixed lines, byte-exact line identity and the declared regions and exemptions seat Rev2Decl mapped (`.ufo/waves/round-46/w1/out/Rev2Decl/contract.md`), under a counter amendment frozen before it is scored.
2. Freshness: llama.cpp after b11906 (b11907 = `4b851fbee…` tagged 2026-10-26T19:57:59Z), the ten off-population llama.cpp rows seat K1Pop lists, the S013 citation defect seat U9Floating found; C1 counter fixes F1–F4 (seat V1Code) and `SKILL.md` as a flag target (K1R07) at the next freeze.

**Capabilities — canonical list as of round 47**

Same four columns as the round-46 canonical list, which stays byte-intact; one row is added (`live-receipt-replay`) and `append-only-audit` is reworded for v2 - contract-declared file set, deleted counts equal to `git diff --numstat`, restoration as a maximum over the event's own window - with its first-working round unchanged at 46.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |
| append-only-audit | Set the lane's contract-declared append-only self-description - the paths and patterns `registry/append-only-contract.tsv` names, each row pointing at the lane line that declares the rule - against its git history: list every commit that deletes >= 20 lines from one of those files with a deleted count equal to `git diff --numstat` (byte-exact, so no `--`-prefixed line is lost), report the largest share of those lines any commit in the event's own window holds again (a multiset maximum, so a later head re-anchor cannot lower it) and which later commit first holds all of them, and exit 1 on a partial or unrestored mass deletion | `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `tools/round47-append-audit-v2-check.py` | 46 |
| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v4` receipt's server release archive and model from the URLs its provenance block records, verify both sha256 values before anything is extracted or executed, re-run the lifecycle from an empty home and compare every check the original evaluated, and refuse a receipt whose provenance is missing, whose recorded digest does not match what it downloads, or whose server-archive member is unsafe | `tools/kama-live-replay.py`; `.ufo/waves/round-47/c2/live/receipt-1.json` | 47 |

## Round 47 — append-only-audit v2 against git numstat and a declared contract (calibration) and replayable live receipts at b11909 (operability) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each); C1 works calibration (the lowest assigned axis) and C2 works operability (the other assigned axis); calibration is below the saturation line 8, so the stagnation nudge is inactive. Base `172b8ad040d51ce8c011238c1408d4e0b6aa9595` (round-46 spot-check); freeze commit `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` (`.ufo/waves/round-47/preregistration.json`; counters `tools/round47-append-audit-v2-check.py` and `tools/round47-live-replay-audit.py`; controls `.ufo/waves/round-47/controls/`; KQ64 receipt `.ufo/waves/round-47/freeze/prereg-time-check.out` exit 0). The build — `tools/append-only-audit.py` v2, `registry/append-only-contract.tsv`, `tools/kama-llamacpp-live.py` v4, `tools/kama-live-replay.py` and the three b11909 receipts — landed after the freeze at `3a09a1d93dcc16799cf6c4b48786e6440af134c4`, before the wave.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — append-only-audit v2: files from a contract whose rows point at declaring lines (corpus/lessons included), deleted counts equal to git numstat (round-46 closure D1), restoration a byte-exact multiset maximised over the event's window (closure D2); matches the counter's recomputation on the lane and a constructed fixture | calibration 7 → 7 | base `selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False` → measured value under §Round-47 measured results | `python3 tools/round47-append-audit-v2-check.py --repo <fresh clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-47/controls/base.c1.out`; `tools/append-only-audit.py`; `registry/append-only-contract.tsv` |
| C2 — replayable live evidence: three b11909 receipts (schema v4) record where the server archive and the model came from; `tools/kama-live-replay.py` re-acquires both into an empty home, verifies both digests, re-runs and reproduces receipt-1's checks, refuses a wrong recorded digest; b11909 registered (sourced: S488, S489) | operability 8 → 8 | base `receipts=0 replay=0 tamper=0 newrow=0 met=False` → measured value under §Round-47 measured results | `python3 tools/round47-live-replay-audit.py --repo <fresh clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-47/controls/base.c2.out`; `.ufo/waves/round-47/c2/live/receipt-1.json` … `-3.json`; `tools/kama-live-replay.py` |

Controls (all `met=False`, `.ufo/waves/round-47/controls/`): C1 v1 plus a contract `contract=0 lane=0 fixture=0`; C1 v1 with the `---` filter fixed, contract expansion and v2 key names `lane_mismatch=4 fixture_mismatch=6`; C2 the b11906 receipts relabelled v4 with b11909 provenance plus a replay that copies receipt-1 `receipts=0 replay=0 tamper=0`.

### Round-47 measured results

Measured commit: `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` (fresh clone of the lane remote). Base `172b8ad0`. Counters: frozen bytes of `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba`. Re-measured at the post-measure fix commit `3442d707fdf926ec5ea3f34363cf2f0899cc79b5` with the same claim values (`*-fix.out`).

| Claim | Base | Measured `383f1fc7` | Command | Receipt |
|---|---|---|---|---|
| C1 calibration 7 → 7 | `selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False` (exit 1) | `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=86 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True` (exit 0) | `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-47/controls/base.c1.out`; `.ufo/waves/round-47/measured/c1-after.out`, `c1-fix.out` |
| C2 operability 8 → 8 | `receipts=0 replay=0 tamper=0 newrow=0 met=False` (exit 1) | `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` (exit 0) | `python3 tools/round47-live-replay-audit.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-47/controls/base.c2.out`; `.ufo/waves/round-47/measured/c2-after.out`, `c2-fix.out` |

Regressions (`.ufo/waves/round-47/measured/*-after.out` at `383f1fc7`, `*-fix.out` at `3442d707`): round-41 head counter `mismatches=0 met=True` (red at the base: the spot-check count 32 → 33); round-42 self-description `mismatches=0 maxN=47 met=True`; round-43 registry `mismatches=0 met=True`; gate `registered 40 unregistered 0 defective 0`; capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; `digest-ledger` `unknown=0`; `hexrun-census` `unknown=1 ledger_bad=1` at `383f1fc7`, `unknown=0 ledger_bad=0`, exit 0, at `3442d707` (base 22 unknown; round-46 closure D4 closed); `append-only-audit --selftest` `pass=19 fail=0`; `kama-live-replay --selftest` `pass=12` at `383f1fc7`, `pass=13` at `3442d707`; `check-receipt.py --selftest` and `kama-llamacpp-live.py --selftest` pass; seat yield `seats=65 reports=65 missing=0` (exit 0). `append-only-audit` on the lane exits 1 (the two SCORECARD head partials, lesson §KQ71 report). End census exit 0 (`.ufo/waves/round-47/census/end.out`).

### What `met=True` does not show (round-47 wave attacks)

- **C1.** Seat K1Cheat met the frozen counter with a tool that recognises the fixture by shape and plays back the lane's five events, and with a print-only selftest stub beside a working audit; copying the counter's recompute under another name also passes (a legitimate equivalent). Seat V1Ctr: the contract leg accepts any line containing `append`, even one that negates the rule; the stable leg is vacuous when base and tip coincide or the tool ignores `--to`; the `round47` guard is a string tripwire. Seat K1Fixture: the `max(0, …)` clamp's negative branch and merge first-parent selection are exercised by no leg, and the exact-20 threshold appears in the fixture in about one run of three. Seat M1Ctr: 13 of 44 counter mutants survive. Seat X1Stable: the window maximum keeps a restored-then-re-deleted event `restored` (now reported as `held_at_to`/`regressed`, not in the exit code). Seat L1Lowthr: below the 20-line threshold the declared files hold 22 unrestored deletion events in `corpus/lessons/*.md` and 7 in-place rewrites and one lost 6-line record in `LOG.md` (`ed135b3c`), so "append-only" holds at mass-deletion scale only. Seat K1Design: the knowledge `## Errata` regions and the SCORECARD head carve-out are not expressible in the v2 contract.
- **C2.** Seat K2Cheat met the frozen counter with a replay that copies host-cache bytes without any download (also with the network dead), with a fabricated rerun of 0-byte placeholders and with a forged `started_utc`: the counter trusts the rerun receipt's contents. Seat K2Tamper: the tamper leg pins only two digit flips; other wrong receipts are caught by other legs or not at all. Seats M2Ctr and M2Replay: 10 of 23 counter mutants and 10 of 24 replay mutants survive. Seat K2Checks: replay agreement is check pass/fail, not the captured bodies. Seat K2Design: provenance is recorded unverified at record time and the model URL names the moving `main` (seat X2Revision). Seat Sen2Replay: the replay executed the archive member before comparing it with `server.sha256` — fixed after the measured commit (lesson addendum).
- **Separability holds** (seat N2Couple): each counter reaches all its legs on a clone carrying only its own build.

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Capabilities 10 → 11 (`live-receipt-replay`, first-working round 47).

### Planned (round 48)

1. Calibration: append-only-audit v3 under a re-frozen counter — the SCORECARD head carve-out and the knowledge `## Errata` regions in machine-readable form (seats Rev1Restore, K1Design), `declared_at` bound to the row's path and rule rather than any line containing `append` (V1Ctr F1), `held_at_to`/`regressed` in the exit semantics (X1Stable), a stable leg whose base differs from the tip and a fixture that covers the `max(0, …)` clamp, merges and the exact threshold deterministically (K1Fixture, V1Ctr); promote the shortcut tally (`.ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py`) to `tools/` with its `--check`.
2. Operability: v5 receipts recording the pinned Hugging Face revision URL (seat X2Revision: `resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/…` serves the same bytes), provenance checked at record time (K2Design F1) and a stable-projection replay comparison (K2Checks); repair `tools/sources-append-only.py`, blind since round 45 (lesson §Mistakes); the b11906 ledger population at b11909+ (seat U2Server: `src/llama-context.cpp` and `src/llama-kv-cache.cpp` changed).

### Superseded head banners (kept verbatim; round 48)

Round-48 C1 build finding: `tools/append-only-audit.py` v3 at the round-47 tip reported `regressed=1` on the `0718b6ab` SCORECARD.md event. Its one graded line that the repair `82b5e9d3` held and the tip no longer holds is the round-45 authority banner (line 6, before the first `## ` heading): rounds 46 and 47 rewrote the banner in place without keeping the superseded text, although line 6 says the head text it replaces is kept verbatim under §Historical head sections. The banners rounds 45 and 46 replaced are appended below byte-exact (`git show 82b5e9d3:SCORECARD.md | sed -n 6p`, `git show 42ea1204:SCORECARD.md | sed -n 6p`); from round 48 on, each round appends the banner it replaces here.

**Current authority (round 45):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 45. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44 and 45; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 46):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 46. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45 and 46; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 47):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 47. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45, 46 and 47; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

Round-48 seat X1Banner: the round-42, round-43 and round-44 banners were rewritten in place too, but each replacement deleted only 1 line of SCORECARD.md line 6 inside commits of 9, 1 and 3 deleted lines (`44fa5627`, `d48e8cc3`, `21945c61`), below the 20-line event threshold of `tools/append-only-audit.py`, so no v3 event graded them. Appended byte-exact below, oldest first (`git show dd9f5dc6:SCORECARD.md | sed -n 6p`, `git show 44fa5627:SCORECARD.md | sed -n 6p`, `git show d48e8cc3:SCORECARD.md | sed -n 6p`).

**Current authority (round 42):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 42. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1); the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 43):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 43. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in round 43; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 44):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 44. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43 and 44; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

Round-49 seat S9Scorecard: the round-48 banner was replaced by the round-49 re-anchor at the head of this file and is appended byte-exact below (`git show 122c4ee9:SCORECARD.md | sed -n 6p`).

**Current authority (round 48):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 48. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45, 46, 47 and 48; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections, and from round 48 every authority banner this line replaces is appended byte-exact under §Superseded head banners at the end of this file (`registry/append-only-contract.tsv` row SCORECARD.md, region `exempt=`). Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

Round-51 build finding (append-only-audit v6, threshold 1): the round-50 integration `1c030f18` replaced the round-49 banner at the head of this file but did not append it here, so the banner's own sentence (every replaced banner is appended byte-exact) was false for one round; the v6 audit graded it as a lost line (disclosure row at `73bf2a7a`). The round-49 banner (`git show 1c030f18^:SCORECARD.md`, line 6) and the round-50 banner this round replaces (`git show 57a2e25b:SCORECARD.md`, line 6) are appended byte-exact below.

**Current authority (round 49):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 49. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45, 46, 47, 48 and 49; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections, and from round 48 every authority banner this line replaces is appended byte-exact under §Superseded head banners at the end of this file (`registry/append-only-contract.tsv` row SCORECARD.md, region `exempt=`). Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 50):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 50. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45, 46, 47, 48, 49 and 50; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections, and from round 48 every authority banner this line replaces is appended byte-exact under §Superseded head banners at the end of this file (`registry/append-only-contract.tsv` row SCORECARD.md, region `exempt=`). Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 51):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 51. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45, 46, 47, 48, 49, 50 and 51; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections, and from round 48 every authority banner this line replaces is appended byte-exact under §Superseded head banners at the end of this file (`registry/append-only-contract.tsv` row SCORECARD.md, region `exempt=`). Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

## Round 48 — append-only-audit v3 under declared carve-outs (calibration) and v5 live receipts replayed from committed bytes (operability) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each); C1 works calibration (the lowest assigned axis) and C2 works operability (the other assigned axis); calibration is below the saturation line 8 and no capability entered since round 47, so the stagnation nudge is inactive. Base `33e005827742b29772b153cda036ec9f27f653be` (the round-47 closure, which is also the round-48 start census). Freeze commit `12284ba39fb1b46b43d43ee82423bebe08c700dc` (`.ufo/waves/round-48/preregistration.json`, frozen 2026-10-26T22:19:34Z; counters `tools/round48-append-audit-v3-check.py` sha256 `92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7` and `tools/round48-live-replay-v5-audit.py` sha256 `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09`; controls `.ufo/waves/round-48/controls/`; freeze-time receipt `.ufo/waves/round-48/freeze/prereg-time-check.out` exit 0; start census `.ufo/waves/round-48/census/start.out` exit 0). The build landed after the freeze at `380bcdff9c8af06997c482f6eb03db926a794a2b`, before the wave: `tools/append-only-audit.py` v3, `registry/append-only-contract.tsv` with the `region` cell (nine rows), `tools/kama-llamacpp-live.py` v5, `tools/kama-live-replay.py` v5 with `--compare`, the three b11909 v5 receipts under `.ufo/waves/round-48/c2/live/`, `corpus/SOURCES.md` rows S492–S493, and the two superseded head banners the v3 finding required at the round-47 tip. Separability (frozen before the build): C1 touches only the audit tool and the contract; C2 only the live tools, the three receipts and one `SOURCES.md` row.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — append-only-audit v3: the lane's append-only files graded under the rule the lane declares, carve-outs included — the contract's `region` cell (`exempt=<## title>` ungraded while the section is not gutted, `only=<## prefix>` graded alone; SCORECARD's re-derived head exempt, the knowledge `## Errata` region graded), every declaration bound to a line that says append-only for that path and is not a negation, `regressed` in the exit code, eleven constructed fixtures and a stable leg whose base differs from the tip | calibration 7 → 7 | base `selftest=0 contract=0 lane=0 fixture=0 stable=0 met=False` (exit 1, `.ufo/waves/round-48/controls/base.c1.out`) → measured value under §Round-48 measured results | `python3 tools/round48-append-audit-v3-check.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-48/controls/base.c1.out`, `junk-c1-v2-relabel.c1.out`, `junk-c1-drop-scorecard.c1.out`; `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `.ufo/waves/round-48/preregistration.json` |
| C2 — v5 live evidence: three b11909 receipts record a model URL pinned to the Hugging Face revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81` and provenance the live tool verified at record time against the archive, the archive member and the model; the tool refuses unverifiable provenance before a server starts; every receipt replays from committed bytes with re-acquired inputs the counter hashes itself and an equal stable projection; wrong digests and swapped URLs are refused; the pinned revision is a source row | operability 8 → 8 | base `receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 met=False` (exit 1, `.ufo/waves/round-48/controls/base.c2.out`) → measured value under §Round-48 measured results | `python3 tools/round48-live-replay-v5-audit.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-48/controls/base.c2.out`, `junk-c2-r47-relabel.c2.out`; `.ufo/waves/round-48/c2/live/receipt-1.json` … `-3.json`; `.ufo/waves/round-48/c2/hf-revision-499bc882.txt`; `tools/kama-live-replay.py` |

Controls (all `met=False`, `.ufo/waves/round-48/controls/`, builder `build_controls.py` sha256 `c892d0c9dd0e897711b9a5a9f69c480b9c7d151acabfd53340a78b420a309d8a`): `base.c1.out` `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 lane_events=0 lane_failures=NA ungraded_lines=0 fixture_fail=11 met=False` (exit 1) and `base.c2.out` `receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False` (exit 1) at the base `33e00582`; `junk-c1-v2-relabel.c1.out` — the v2 tool relabelled v3 beside a v3 contract, so it skips region grading, binding and the exit work: `rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=11 met=False`; `junk-c1-drop-scorecard.c1.out` — the v3 contract with the SCORECARD row dropped, the cheap way to a clean lane: `rows=8 files=88 met=False`; `junk-c2-r47-relabel.c2.out` — the round-47 receipts relabelled v5 with a fabricated verified block and a copying replay, so the receipts leg alone is structural: `receipts=1 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False`.

### What `met=True` does not show (round-48 wave attacks)

- **Disclosed before the wave** (`.ufo/waves/round-48/preregistration.json`, `limits` — not wave findings): C1's counter recomputes the v3 definition on its own code path, so lane equality is not independent of the definition; the fixture expectations and `git diff --numstat` are the outside ground truth. The exemption reads `## ` headings only, so a heading inside a fenced block counts. Held lines are a multiset over the whole file, so an exempt line's text can count toward a graded line with the same text. The threshold stays 20, so sub-threshold deletions are not graded. C2's replay needs github.com and huggingface.co and b11909 is a GitHub prerelease; the stable projection is a chosen set of surfaces (timing, ports, pids, log text and the models `created` field are excluded as instance facts); the receipts leg is structural, so fabricated receipts with self-consistent digests pass it and the replay and urlswap legs carry the evidence; the record-time leg uses a stub server and a stub archive, so it shows the refusal happens before execution, not that the real archive is genuine.
- **C1, wave findings.** Seat K1Regions: the exemption is title-based and content-blind — a dated-section loss laundered by moving its text under an exempt heading while the section's line count is sustained (same-commit filler, or regrowth later in the window) exits 0 with the lines `ungraded`; on the lane the 89 ungraded lines are all genuine head text (seat R1Sample: the 17-vs-8 gap to the round-47 Rev1Restore proposal is exactly the nine `## Planned` lines parent 60–68, eligible because that section regrew to 18 lines at `9307b15e`, and all nine survive verbatim under §Historical head sections), so the hole is latent, not exercised. Seat K1Binding: the binding rule accepts a token by substring (`log` inside `catalog`) and any line of a file a wildcard row covers (the `corpus/lessons/*.md` row bound only that way; re-anchored at integration to `corpus/QUALITY.md:143`, KQ26); its negation list is four fixed strings. Seat K1Cheat: a tool that copies the counter's own recomputation, or hard-codes the lane's five events beside it, meets the counter (a legitimate equivalent and a shortcut, respectively). Seat K1Fixture: five v3 clauses are exercised by no fixture (exact-title match, per-file union of rows, binary changes, malformed-region rejection, unmatched-pattern exit neutrality) — a tool wrong only in one of them meets the counter. Seat M1Ctr: 21 of 52 counter mutants survive (every probe event is `restored` with `held_at_to == restored_max == graded`, so the counter's partial/unrestored/negative-held logic is unobservable on the lane); seat M1Tool: 15 of 55 tool mutants survive both the selftest and the counter, including a tool that hard-codes `AOA_SELFTEST … fail=0` (the selftest leg is self-certified). Seat X1SelftestPower: the clamp case also passes on v2, and no case covered a rewrite before the first `## ` heading — the shape of this round's banner finding (case `preamble-graded` added at integration). Seat L1Lowthr: at `--threshold 1` 66 graded sub-threshold events are partial or unrestored; 65 are corrections or re-anchors, one is a real loss (`ed135b3c` deleted the 2026-10-13 HOURS ledger opening from `LOG.md`, 7 lines, 2 held later). Seat X1Banner: the round-42, 43 and 44 banners were also lost below the threshold (appended byte-exact at integration). Seat X1Stable: graded/ungraded never moved across the 32 tips of the round, but the quantity is tip-indexed by construction.
- **C2, wave findings.** Seat K2Cheat: a 19-line change to the committed replay tool meets all seven legs without running the lifecycle (it downloads and digest-checks the inputs, then writes a rerun that copies the original's checks and captures with paths rewritten), and the three receipts could be one recording duplicated. Seat K2Urlswap: a replay that refuses the four swapped or tampered receipts by comparing URL and digest with the frozen constants before any fetch, and serves the genuine replays from host bytes, meets the counter with the network provably dead. So `replayed=3/3` shows the inputs are re-acquirable and the replay's comparison holds, not that a server ran — an execution witness (a counter-supplied nonce the server must echo, or a liveness join on the rerun's pid and port) is the next counter's job. Seat K2Record: record-time verification binds local bytes to operator-supplied digests and never fetches the recorded URLs, so three forged-provenance forms record a v5 pass receipt; the replay refuses every one later. Seat K2Design: the stable projection has blind spots (models `meta`, slots body content beyond its digest), v4 receipts are still accepted against the moving `main`, and the prerelease cliff (closure D7) stands. Seat K2Projection: five fresh replays agree on every projected surface; several captured values stay unprojected. Seat X2Offline: `--timeout` bounds the live child only. Seats M2Ctr (6 of 27 counter mutants survive, all coverage gaps) and K2Selftest (a v5 rerun with no provenance used to match; uppercase hex commits are refused by both tools, consistently).
- **Integration fixes after the wave (before the measured commit):** `tools/kama-live-replay.py` — https-only outside the selftest, malformed receipts refused instead of crashing, `--compare` validates provenance, two unparseable models bodies no longer compare equal (seat V2Replay F1–F4, F11), a present `provenance.verified` digest must equal the asset/server/model sha256 (F7), and a v5 rerun must carry the original's commit and verified digests (seat K2Selftest), `KLR_SELFTEST pass=22`; `tests/llamacpp-live/check-receipt.py` and `tools/gguf-identity.py` read v5 (seat K0Harm F2/F3; the build had broken them, the round-47 pattern again); `tools/sources-append-only.py` grades transitions again (seat X9SourcesGuard, closure D8); `tools/shortcut-tally.py` promoted (seat X9Tally); the contract re-anchors the lessons row and adds `corpus/knowledge/error-is-not-a-verdict.md` (`only=## Round24`; seat K1Contract); the round-42/43/44 banners appended (seat X1Banner); one hexrun ledger row (seat X4Hex).
- **Separability holds** (seat N2Couple): C1 reaches all five legs on a clone at the freeze plus only the C1 build, C2 all seven legs plus only the C2 build.

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Capabilities 11 → 11: round 48 re-words `append-only-audit` for v3 and `live-receipt-replay` for v5, their first-working rounds stay 46 and 47, and no capability enters.

**Capabilities — canonical list as of round 48**

Same four columns as the round-47 canonical list, which stays byte-intact; no row is added, and two rows are reworded for the tools the round-48 build landed: `append-only-audit` for v3 (a per-row `region` cell, declarations that must bind, `regressed` in the exit semantics) with its first-working round unchanged at 46, and `live-receipt-replay` for v5 (provenance verified at record time, the model pinned to a 40-hex `/resolve/<commit>/` revision, a stable-projection comparison and `--compare`) with its first-working round unchanged at 47. Eleven capabilities, as in round 47.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |
| append-only-audit | Set the lane's contract-declared append-only self-description - the paths and patterns `registry/append-only-contract.tsv` names, each row naming the lane line that declares the rule and the `region` it grades (`*`; `exempt=` `## ` sections that stay ungraded while their line count's window maximum is not below the parent's; or a single `only=` section) - against its git history: every row must bind (the declaring line says append-only for that path and is not a negation, an exempt pointer names the line that declares those sections re-derived, and an `only=` pointer names its prefix), list every commit that deletes >= 20 lines from one of those files with a deleted count equal to `git diff --numstat` (byte-exact, so no `--`-prefixed line is lost), report the largest share of the graded lines any commit in the event's own window holds again (a multiset maximum, so a later head re-anchor cannot lower it) and which later commit first holds all of them, and exit 1 on an unbound row, a partial or unrestored mass deletion, or a regression (the tip holds fewer graded lines than the event's best window commit) | `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `tools/round48-append-audit-v3-check.py` | 46 |
| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v5` receipt's server release archive and model from the https URLs its provenance block records - the model pinned to a 40-hex `/resolve/<commit>/` revision that the receipt also states as `provenance.model.commit` - verify both sha256 values before anything is extracted or executed, check the archive and its member against the asset and server digests before the server starts so a v5 receipt's `provenance.verified` block is recorded rather than asserted, re-run the lifecycle from an empty home passing the downloaded archive as `--server-archive`, compare the rerun with the original past check pass/fail on a stable projection of the captured surfaces (props fields, slots count and body digest, health status and body digest, models ids and owned_by, metrics status, loading envelope, teardown outcome, listener ownership), refuse a receipt whose provenance is missing or unverified, whose recorded digest does not match what it downloads, or whose server-archive member is unsafe, and answer `--compare A B` on two receipts without the network | `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`; `.ufo/waves/round-48/c2/live/receipt-1.json` | 47 |

### Planned (round 49)

1. Calibration: content-aware eligibility for the exempt head sections (seat K1Regions: the window-maximum line count is content-blind), a word-bounded binding token and a denial window (seat K1Binding), fixtures for the five unexercised v3 clauses and for partial/unrestored states in the counter's own recompute (seats K1Fixture, M1Ctr), a selftest leg the tool cannot self-certify (seat M1Tool); decide the sub-20 boundary (seat L1Lowthr's 66 graded sub-threshold events, one real `LOG.md` loss at `ed135b3c`).
2. Operability: an execution witness in the replay leg (seats K2Cheat, K2Urlswap: a replay that never runs a server meets the round-48 counter), record-time fetching of the recorded URLs or a stated reason not to (seat K2Record), the prerelease cliff (closure D7), and the b11906 ledger population at b11909+ (round-47 seat U2Server).

### Round-48 measured results

Measured commit: `c4b2175d2ff9466beaed039dc8330176362e7d82` (fresh clone of the lane). Base `33e00582`. Counters: frozen bytes of `12284ba39fb1b46b43d43ee82423bebe08c700dc`.

| Claim | Base | Measured `c4b2175d` | Command | Receipt |
|---|---|---|---|---|
| C1 calibration 7 → 7 | `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 lane_events=0 lane_failures=NA ungraded_lines=0 fixture_fail=11 met=False` (exit 1) | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=10 files=91 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` (exit 0) | `python3 tools/round48-append-audit-v3-check.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-48/controls/base.c1.out`; `.ufo/waves/round-48/measured/c1-after.out` |
| C2 operability 8 → 8 | `receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False` (exit 1) | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` (exit 0) | `python3 tools/round48-live-replay-v5-audit.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-48/controls/base.c2.out`; `.ufo/waves/round-48/measured/c2-after.out` |

Regressions at `c4b2175d` (`.ufo/waves/round-48/measured/*.out`, each with its `tip=` line): gate `registered 42 unregistered 0 defective 0`; capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; round-41 head counter `mismatches=0 met=True`; round-43 registry `mismatches=0 met=True`; `digest-ledger` `unknown=0`; `hexrun-census` `unknown=0`; `sources-append-only.py --from 33e00582` exit 0 (blind since round 45 until this round); `append-only-audit` on the lane exit 0 (`regressed=0`); selftests `AOA_SELFTEST pass=28`, `KLR_SELFTEST pass=22`, `check-receipt` 16 VALID / 107 rejected, live `selftest: ok`; round-47 C2 counter `met=True` (v4 replays still work). Two head items the measured commit missed, fixed in the next commit and re-run at the final tip (`*-final.out`): the round-42 self-description counter wanted `### Planned (round 49)` named in the head §Planned pointer, and the pointer check wanted this section. The round-47 C1 counter fails by construction (it grades the v2 contract format v3 replaced; seat X2V4Compat).

## Round 49 — the replay execution witness (operability) and append-only-audit v4 by line origin (calibration) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each); C2 works calibration (the lowest assigned axis) and C1 works operability (the other assigned axis); calibration is below the saturation line 8 and no capability entered since round 47, so the stagnation nudge is inactive. Base `438127bc01ff3b99f98468549d58046f932490ef` (the round-48 closure, which is also the round-49 start census). Freeze commit `36d5ed2681111b68c180f8ab1646d8dc9beaedee` (`.ufo/waves/round-49/preregistration.json`, frozen 2026-10-26T23:17:45Z; counters `tools/round49-replay-witness-audit.py` sha256 `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` and `tools/round49-append-audit-v4-check.py` sha256 `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945`; controls `.ufo/waves/round-49/controls/`; freeze-time receipt `.ufo/waves/round-49/freeze/prereg-time-check.out` exit 0; start census `.ufo/waves/round-49/census/start.out` exit 0; C1 source captures `.ufo/waves/round-49/c1/server-README-caa8191d.md` and `.ufo/waves/round-49/c1/proc_pid_exe.5.txt`). The build landed after the freeze at `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, before the wave: `tools/kama-llamacpp-live.py` `hold_for_witness()` (writes `ready.json` with the port and the server child's pid, holds until `release` or the bounded `--witness-timeout`) and the bounded `verify_archive_member()`, `tools/kama-live-replay.py --witness-dir`, `tools/append-only-audit.py` v4 definitions, and `corpus/SOURCES.md` rows S494–S495. Separability (frozen before the build): C1 touches only the live tools and one `SOURCES.md` row; C2 only the audit tool (and, only on a real lane loss, a byte-exact restoration in the affected file).

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the replay execution witness: a replay of each of the three committed b11909 v5 receipts holds its rerun server up for an outside observer, which finds the frozen llama-server binary executing as the listener of the announced port with the frozen model, round-trips a fresh nonce through `POST /tokenize` (`with_pieces`) and `POST /detokenize` against the vocabulary the counter decodes from the model itself, and sees the server gone after release; the live tool refuses a sparse or size-mismatched archive member before hashing it; the tokenize surface is a source row | operability 8 → 8 | base `witness=0 cap=0 newrow=0 witnessed=0/3 met=False` (exit 1, `.ufo/waves/round-49/controls/base.c1.out`) → measured value under §Round-49 measured results | `python3 tools/round49-replay-witness-audit.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-49/controls/base.c1.out`, `junk-c1-fake-witness.c1.out`; `.ufo/waves/round-48/c2/live/receipt-1.json` … `-3.json`; `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`; `.ufo/waves/round-49/preregistration.json` |
| C2 — append-only-audit v4: a deleted line in an eligible exempt section stays ungraded only when its text was born in an exempt section (origin), the row token must occur in the declaring line as a whole word, a negation within three words of append-only unbinds, and a wildcard row binds only through a line that names its directory; eight constructed fixtures with expectations by construction; on the lane every contract row binds and the tool exits 0 | calibration 7 → 7 | base `fixture=0 lane=0 scenarios=4/8 met=False` (exit 1, `.ufo/waves/round-49/controls/base.c2.out`) → measured value under §Round-49 measured results | `python3 tools/round49-append-audit-v4-check.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-49/controls/base.c2.out`, `junk-c2-no-exempt.c2.out`, `junk-c2-word-token.c2.out`; `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `.ufo/waves/round-49/preregistration.json` |

Controls (all `met=False`, `.ufo/waves/round-49/controls/`, builder `build_controls.py` sha256 `9e7a7873e0bf4335391450004d49afabb69b883d5545ea53a9341452fda0eba2`): `base.c1.out` `witness=0 cap=0 newrow=0 witnessed=0/3 met=False` (exit 1) and `base.c2.out` `fixture=0 lane=0 scenarios=4/8 met=False` (exit 1) at the base `438127bc`; `junk-c1-fake-witness.c1.out` — a clone whose `tools/kama-live-replay.py` is replaced by a replay that never executes the live tool, so the counter observes the host's own llama-server binary instead: `witness=0 cap=0 newrow=0 witnessed=0/3 met=False` with `exe sha256 375532f8… is not the frozen server` on all three receipts; `junk-c2-no-exempt.c2.out` — v4 with the eligible-exempt `continue` removed, so the native head carve-out is lost: `scenarios=4/8` (the `native-head` scenario exits 1) and the lane `regressed=1 ungraded_lines=0`; `junk-c2-word-token.c2.out` — binding with the whole-word token and the negation window but no origin rule: `scenarios=7/8` (the `launder` scenario stays ungraded) `met=False`.

### What `met=True` does not show (round-49 wave attacks)

- **Disclosed before the wave** (`.ufo/waves/round-49/preregistration.json`, `limits` — not wave findings): C1 witnesses that the frozen binary executed as the listener with the frozen model and that its tokenizer answered a counter nonce; it does not show the binary came from the downloaded archive at replay time (the round-48 replay leg's digest checks carry that), and a replay that runs the same binary from a host copy still passes the witness. The exe check reads `/proc/<pid>/exe`, so it is Linux-only and fails closed on a process the counter cannot read. C2's origin is the text's first appearance in the file, so a line born in the head, later carried in a dated section and deleted from the head again stays ungraded, and identical text born in both places counts as exempt-born. C2's lane leg bounds the tool's ungraded count by the counter's own natively-exempt count per event; it does not recompute eligibility or the held measures, and the sub-20 threshold is unchanged.
- **C1, wave findings.** Seat K1Cheat: two shortcuts still reach `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` — a decoy replay that never runs the live tool (it starts the host's own b11909 binary with the model, writes `ready.json` and copies the original receipt as the rerun with `witness.released` true), and a `PYTHONPATH`/`sitecustomize` hijack of the counter's inherited environment over the pristine build tree; the counter never joins the observed pid with the rerun receipt's `child_pid` (the decoys' copied receipts carry `child_pid` 611093, not the observed pid). Seat R0Controls: a host-copy server passes every witness leg (the stated limit) and `released`/`waited_ms` are self-asserted. Seat K1Design: the observed server is not bound to the captures, nor the loaded model bytes to the `-m` file. Seat U1Prior: the witness is a local, unsigned observer-nonce check (RFC 9334 sense), not an exec-time measurement. Seats R1Rerun, R1Provenance, X1Observe, X1Concurrent (3-way and 9-way), X1Nonce (30/30 nonces), X1Record (new v5 receipt recorded and replayed), X1Hold, X1Compat, K1Fresh: no defect in the claim path. Host-safety findings fixed at integration (below): X1Kill and Sen1Witness F5 (a killed replay left the held server up for the whole timeout), X1Offline and Sen1Witness F2/F3 (a stale `release` ended the hold at once; a stale `ready.json` could name a foreign live server), Sen1Witness F1 (symlink followed at `ready.json.tmp`), F4 (`--witness-timeout inf`), V1Live F1 (stat/open TOCTOU on the archive) and F2 (announce of a dead child).
- **C2, wave findings.** Seat K2Origin: origin is byte-text-global and traversal-ordered — sibling order in `git rev-list` can flip a verdict, a fenced fake `## ` title can hide a dated loss, CRLF variants of head lines are graded, and head mirror rows born in dated sections are graded (the seven lines of `0718b6abbda6`, seat X2Seven: the round-34/41 capability rows; held, so the event stays `restored`; seat X2Lane: v4 changes no lane event's status across 8 tips and 5 thresholds). Seat K2Cheat: a no-origin tool that under-reports its `ungraded` count (`graded + ungraded != deleted`) plus a fixture-shape heuristic meets the counter — the lane leg only upper-bounds the tool's self-reported count. Seat V2Ctr: the counter's binder is a copy of the tool's rule, not an independent oracle. Seat K2Negation: six negation forms escaped the window and three declaring forms are read as negations; `cannot`/`can't`, curly apostrophes and en/em dashes were added at integration, other punctuation and trailing negations remain. Seat X2Fixtures: four more latent v4 escapes and a rename blindness. Seat K2Binding: the `corpus/lessons/*.md` row bound by coincidence to the KQ26 criterion; re-anchored at integration. Seats R2Rerun, V2Sample (30/30 sampled ungraded lines are genuine head text), X2HeadSim, X2SelftestPower: no defect in the claim path. The round-48 C1 counter now fails its lane leg by construction (it recomputes v3: seats X2R48, U0Consumers).
- **Integration fixes after the wave (before the measured commit):** `tools/kama-llamacpp-live.py` — one descriptor (`O_NONBLOCK`, `fstat`) for the archive checks and reads; `prepare_witness_dir()` clears an earlier run's `ready.json`/`release` and refuses an unusable dir before any server starts; the temp file is per-pid and opened `O_EXCL|O_NOFOLLOW`; `ready.json` is withdrawn when the hold ends; the announce needs a running child; the hold ends when the tool's parent dies (`witness.orphaned`; measured: server gone 0.05 s after a SIGKILL of the replay); `--witness-timeout` bounded to (0, 3600] in both tools; selftest case `provenance-archive-too-many-members` (seat X1Selftest). `tools/kama-live-replay.py` — selftest case `witness-passthrough` (`KLR_SELFTEST pass=23`). `tools/append-only-audit.py` — negation set widened (K2Negation F1) and seven selftest cases (X2SelftestPower, `AOA_SELFTEST pass=36`). `registry/append-only-contract.tsv` — lessons row re-anchored to `corpus/README.md:1239`. Not reported by the measured commit: mutation seats M1Ctr, M1Live, M2Ctr, M2Tool and seats X1Sparse, Sen2Archive, V2Tool, X2Perf (late; folded after measurement if they land).
- **Separability holds** (seat N2Couple): C1 reaches all three legs on a clone at the freeze plus only the C1 build, C2 both legs plus only the `tools/append-only-audit.py` from `74558c71`.

Scores held: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Capabilities 11 → 11: round 49 re-words `append-only-audit` for v4 (line origin, whole-word token, negation window, wildcard self-declaration refused) and `live-receipt-replay` for the execution witness and the bounded archive member, their first-working rounds stay 46 and 47, and no capability enters.

**Capabilities — canonical list as of round 49**

Same four columns as the round-48 canonical list, which stays byte-intact; no row is added, and two rows are reworded for the tools the round-49 build landed: `append-only-audit` for v4 (a deleted line in an eligible exempt section stays ungraded only when its text was born in an exempt section, the row token is a whole word, a negation within three words unbinds, a wildcard row binds only through a line that names its directory) with its first-working round unchanged at 46, and `live-receipt-replay` for the execution witness (`--witness-dir`, `ready.json`, a bounded hold) and the sparse/size-mismatched archive member refused before hashing, with its first-working round unchanged at 47. Eleven capabilities, as in round 48.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |
| append-only-audit | Set the lane's contract-declared append-only self-description - the paths and patterns `registry/append-only-contract.tsv` names, each row naming the lane line that declares the rule and the `region` it grades (`*`; `exempt=` `## ` sections that stay ungraded while their line count's window maximum is not below the parent's; or a single `only=` section) - against its git history: every row must bind (the declaring line says append-only for that path and is not a negation within three words of it, the row token occurs there as a whole word, a wildcard row binds only through a line that names its directory, an exempt pointer names the line that declares those sections re-derived, and an `only=` pointer names its prefix), grade a deleted line in an eligible exempt section only when its text was born in an exempt section (origin), list every commit that deletes >= 20 lines from one of those files with a deleted count equal to `git diff --numstat` (byte-exact, so no `--`-prefixed line is lost), report the largest share of the graded lines any commit in the event's own window holds again (a multiset maximum, so a later head re-anchor cannot lower it) and which later commit first holds all of them, and exit 1 on an unbound row, a partial or unrestored mass deletion, or a regression (the tip holds fewer graded lines than the event's best window commit) | `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `.ufo/waves/round-49/measured/c2-build.out` | 46 |
| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v5` receipt's server release archive and model from the https URLs its provenance block records - the model pinned to a 40-hex `/resolve/<commit>/` revision that the receipt also states as `provenance.model.commit` - verify both sha256 values before anything is extracted or executed, check the archive and its member against the asset and server digests before the server starts so a v5 receipt's `provenance.verified` block is recorded rather than asserted, re-run the lifecycle from an empty home passing the downloaded archive as `--server-archive`, hold the rerun server up for an outside observer on request (`--witness-dir`: `ready.json` names the port and the server child's pid, the server stays up until `release` or the bounded timeout, and the rerun receipt records `witness.released`), refuse a server-archive member that is sparse or whose declared size differs from the `--server` file before hashing it, compare the rerun with the original past check pass/fail on a stable projection of the captured surfaces (props fields, slots count and body digest, health status and body digest, models ids and owned_by, metrics status, loading envelope, teardown outcome, listener ownership), refuse a receipt whose provenance is missing or unverified, whose recorded digest does not match what it downloads, or whose server-archive member is unsafe, and answer `--compare A B` on two receipts without the network | `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`; `.ufo/waves/round-49/measured/c1-build.out`; `.ufo/waves/round-48/c2/live/receipt-1.json` | 47 |

### Planned (round 50)

1. Calibration: origin with a per-file line identity independent of rev-list order, fence-aware sections and CRLF-normalised lookup (seats K2Origin, X2Fixtures); an arithmetic invariant `graded + ungraded == deleted` and an oracle independent of the tool's binder in the next counter (seats K2Cheat, V2Ctr); the remaining negation forms (K2Negation); decide the sub-20 boundary (66 graded sub-threshold events at `--threshold 1`, one real `LOG.md` loss at `ed135b3c`).
2. Operability: bind the witness to the replay's own process (observed pid = rerun `child_pid`, the pid a descendant of the replay, an allow-listed child environment) and to the model bytes the server mapped (seats K1Cheat, K1Design, R0Controls); record-time fetching of the recorded URLs or a stated reason not to (round-48 seat K2Record); the prerelease cliff (closure D7) with a watch on the b11909 asset and the pinned model object (seat U2Pins: pin-watch tracks b11755); the b11906 ledger population at b11909+ (round-47 seat U2Server).

### Round-49 measured results

Measured commit: pending — the lane L1 takes it after integration; the counters are the frozen bytes of `36d5ed2681111b68c180f8ab1646d8dc9beaedee`. Base `438127bc`. Build-time values (not the measurement) are in `.ufo/waves/round-49/measured/*-build.out` at `74558c71`.

| Claim | Base | Measured (pending) | Command | Receipt |
|---|---|---|---|---|
| C1 operability 8 → 8 | `witness=0 cap=0 newrow=0 witnessed=0/3 met=False` (exit 1) | pending | `python3 tools/round49-replay-witness-audit.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-49/controls/base.c1.out`; `.ufo/waves/round-49/measured/c1-build.out` (build time: `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0) |
| C2 calibration 7 → 7 | `fixture=0 lane=0 scenarios=4/8 met=False` (exit 1) | pending | `python3 tools/round49-append-audit-v4-check.py --repo <clone> --tip <commit> --scratch <dir>` | `.ufo/waves/round-49/controls/base.c2.out`; `.ufo/waves/round-49/measured/c2-build.out` (build time: `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0; lane `ungraded_lines=82`, event `0718b6abbda6` ungraded 65 = natively exempt 65) |

Regressions at build time `74558c71` (`.ufo/waves/round-49/measured/*-build.out`): capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; `digest-ledger` `unknown=0`; `sources-append-only.py --from 438127bc` exit 0 (`added S494 (allowed)`, `added S495 (allowed)`); `append-only-audit` on the lane exit 0 (`regressed=0 ungraded_lines=82`); selftests `AOA_SELFTEST pass=30`, `KLR_SELFTEST pass=22`, `check-receipt` 16 VALID / 107 rejected, live `selftest: ok`; round-48 C2 counter `met=True`; `shortcut-tally.py` exit 0 over rounds 40–47; round-48 C1 counter fails by construction (it recomputes v3 while the tool grades v4: lane `ungraded_lines tool=82 counter=89`, seat X2V4Compat). Open at build time and owned by integration: gate `registered 42 unregistered 2 defective 0` (the two round-49 counters are not yet in `SKILL.md`'s registry, seat S9Skill) and `GATE_SELFTEST pass=5 fail=1` because the gate's own lane-tip case grades that same registry; round-41 head counter `mismatches=1` and round-43 registry `spot=1` for the stale spot-check count, which this section's head re-anchor (34 → 35) fixes; `hexrun-census` `unknown=2` (two fleet object ids in `corpus/lessons/round-48-verifier-spotcheck.md`, present at the base `438127bc`, seat K0Harm). The measured run must re-take all of these.

Measured values (appended after the measured commit; the `pending` cells above are superseded by this paragraph, not rewritten). Measured commit: `24e906f034bc5635ee46d9743b1aa9ff93707362` (the integration commit; fresh clone of the lane), counters the frozen bytes of `36d5ed26`. C1 operability 8 → 8: `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0 (`.ufo/waves/round-49/measured/c1.out`). C2 calibration 7 → 7: `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0 (`.ufo/waves/round-49/measured/c2.out`). Regressions at `24e906f0` (`.ufo/waves/round-49/measured/*.out`, each with its `tip=` line): gate `registered 44 unregistered 0 defective 0`; capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; round-41 `mismatches=0 met=True`; round-42 `mismatches=0 maxN=49 met=True`; round-43 `mismatches=0 met=True` (gate selftest green again); pointer `met=True`; `digest-ledger` `unknown=0`; `hexrun-census` `unknown=0` (the two round-48 fleet report commits ledgered); `sources-append-only.py --from 438127bc` exit 0; `append-only-audit` on the lane exit 0 (`ungraded_lines=82 regressed=0 bad_declarations=0`); selftests `AOA_SELFTEST pass=36`, `KLR_SELFTEST pass=23`, `check-receipt` 16 VALID / 107 rejected, live `selftest: ok`; round-48 C2 counter exit 0; round-48 C1 counter exit 1 by construction (v3 recompute against the v4 tool). End census exit 0 (`ok` 1, `W01` 1, `W04` 93; `.ufo/waves/round-49/census/end.out`). Late finding (seat X1Kill, after the measured commit): a killed counter still leaves replay, live tool and server up, because `tools/kama-live-replay.py` spawns the live child without its own session or signal handling (`.ufo/waves/round-49/w1/out/X1Kill/proposed-replay-spawn.diff`); routed to round 50, not fixed this round.

Late wave findings (reports landed after the measured commit; WAVE-DONE: all 71 seats settled, `.ufo/waves/round-49/w1/w1-results.json`; `tools/seat-yield.py` → `seats=71 reports=71 missing=0`, `.ufo/waves/round-49/measured/seat-yield-w1.out`): seat M1Ctr — 9 of 20 C1 counter mutants killed, 11 survive (load-bearing checks exercised only against the side that already fails); seat M1Live — 23 live/replay mutants at the build, 5 killed by selftest, 8 by the counter, 10 survive; seat M2Ctr — 49 C2 counter mutants, 28 killed, 16 survive with proposed killing cases, 5 equivalent; seat M2Tool — 29 v4 tool mutants, 13 killed by selftest, 1 by the counter only, 8 survive (several closed by the seven selftest cases integrated before measurement). Seats X1Sparse (all eight round-48 Sen2Live inputs refused in 0.001–0.043 s), Sen2Archive (bounded verification safe on every axis measured), V2Tool (no defect in the v4 diff) and X2Perf (origin pass +13 % time, +27 % peak RSS on the lane; linear) report no defect in the claim path. Survivors route to round 50 with §Planned (round 50).

## Round 50 — the process-bound replay witness (operability) and append-only-audit v5 by birth-DAG origin (calibration) (2026-10-27)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each); C2 works calibration (the lowest assigned axis) and C1 works operability (the other assigned axis); calibration is below the saturation line 8 and no capability entered since round 47, so the stagnation nudge is inactive. Base `26ecba64ad6fb571d09074b07202d1618a46ecd1` (the round-49 closure, which is also the round-50 start census). Freeze commit `601c8889f33d1797c712feb753974c20cf891264` (`.ufo/waves/round-50/preregistration.json`, frozen 2026-10-27T00:20:47Z; counters `tools/round50-replay-bind-audit.py` sha256 `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89` and `tools/round50-append-audit-v5-check.py` sha256 `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46`). Build `97c864bead3ee4a2f629574e77263d33834ec98a`.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the process-bound replay witness: a replay of each of the three committed v5 b11909 receipts, started isolated with planted environment canaries, holds a server that the counter finds executing the frozen binary as the listener, answering a fresh nonce against the model's own vocabulary, descending from the replay, free of the canaries, mapping a file that hashes to the frozen model, and recorded in the rerun receipt with the same pid and the same mapped file; killing the replay's invoker removes every process of the tree within 30 s; the maps surface is a source row | operability 8 → 8 | base `bind=0 teardown=0 newrow=0 bound=0/3 met=False` (exit 1, `.ufo/waves/round-50/controls/base.c1.out`) → measured value under §Round-50 measured results | `python3 tools/round50-replay-bind-audit.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-50/controls/base.c1.out`; `.ufo/waves/round-50/measured/c1-build.out` (build: `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0) |
| C2 — append-only-audit v5: origin is the union of section titles at every birth of a line's key (a commit holding it while no parent does), so it is a property of the commit graph, not of rev-list order; sections ignore `## ` lines inside CommonMark fenced code blocks; origin keys drop one trailing carriage return; graded + ungraded equals deleted for every event; twelve constructed fixtures with expectations by construction; on the lane every contract row binds and the tool exits 0 | calibration 7 → 7 | base `fixture=0 lane=1 scenarios=9/12 met=False` (exit 1, `.ufo/waves/round-50/controls/base.c2.out`) → measured value under §Round-50 measured results | `python3 tools/round50-append-audit-v5-check.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-50/controls/base.c2.out`; `.ufo/waves/round-50/measured/c2-build.out` (build: `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0; lane `ungraded_lines 89`, event `0718b6abbda6` ungraded 72 = natively exempt 72, event `dd9f5dc6c0e6` ungraded 17 <= 23) |

Controls (all `met=False`, `.ufo/waves/round-50/controls/`): `base.c1.out` and `base.c2.out` at the base (do-nothing controls); after the build, ablation controls — C1: `junk-c1-no-env`, `junk-c1-no-pdeathsig`, `junk-c1-no-mapping`, `junk-c1-decoy` (one mechanism removed per clone, each `met=False`); C2: `junk-c2-fence-blind`, `junk-c2-byte-exact-keys`, `junk-c2-first-rev-list-origin` (each `fixture=0`).

### What `met=True` does not show (round-50 wave attacks)

### Planned (round 51)

1. Calibration: the outside binder (seat V2Ctr: the counter's binder is still the v4 copy); the sub-20 threshold decision (66 graded sub-threshold events at `--threshold 1`, one real `LOG.md` loss at `ed135b3c`); decide whether the seven `## Capabilities` mirror rows (now ungraded under v5) should be declared mirror-refresh explicitly.
2. Operability: the counter's pid-join edges (a shell-launched replay defeats `replay_pid`; decoy replays that copy the original `child_pid`), the mapped-file rewrite-after-load indistinguishability, btrfs dev mismatch fail-closed; record-time fetching of the recorded URLs or a stated reason not to; the prerelease cliff (b11909) with a watch on the asset and pinned model object.

### Round-50 measured results

Measured commit: `8370e39cc9a0589b831a724b00e6fa4a6293e52f` (the integration-fix commit; fresh clone of the lane), counters the frozen bytes of `601c8889`. C1 operability 8 → 8: `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0 (`.ufo/waves/round-50/measured/c1.out`). C2 calibration 7 → 7: `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0 (`.ufo/waves/round-50/measured/c2.out`). Regressions at `8370e39c` (`.ufo/waves/round-50/measured/*.int.out`, each with its `tip=` line): gate `registered 46 unregistered 0 defective 0`; capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; round-41 `mismatches=0 met=True`; round-42 `mismatches=0 maxN=50 met=True`; round-43 `registered=46 mismatches=0 met=True`; pointer `met=True`; digest-ledger `unknown=0`; `sources-append-only --from 26ecba64` exit 0 (`no append-only violations`); `append-only-audit` exit 0 (`ungraded_lines=89`); selftests `AOA_SELFTEST pass=36`, `KLR_SELFTEST pass=23`, live `selftest: ok`, check-receipt 16 VALID / 107 rejected; round-48 C2 counter exit 0; round-49 C1 counter still `met=True`; round-49 C2 counter `fixture=1 lane=0 scenarios=8/8 met=False` (expected supersession: v4's origin counts the seven `## Capabilities` mirror rows as natively exempt 65 while v5 gives them a head birth 72). hexrun-census `unknown=1` (`f8cdb853…`, the round-49 fleet report commit cited in `corpus/lessons/round-49-verifier-spotcheck.md`) — carried from base, documented by seat X15NoHarm2. End census exit 0 (`.ufo/waves/round-50/measured/census-end.out`: 93 W04, 1 W01, 1 ok).

## Round 51 — the replay's own server image (operability) and append-only-audit v6: every deletion graded, the A-row rule as declared, every loss named (calibration) (2026-10-27)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each); C2 works calibration (the lowest assigned axis) and C1 works operability (the other assigned axis); calibration 7 is below the saturation line 8, so the stagnation nudge is inactive. Attempt 2 of the round (attempt 1 left no lane writes; `.ufo/watchdog.log` `lane-dead-no-report kama round=51`). Base `57a2e25bf702b03aa61f9265e968cf68058ecb82` (the round-50 closure; start census `.ufo/waves/round-51/census/start.out`, exit 0). Freeze `804bde75164444bdf0fe6783d7aa45774bf562bd` (`.ufo/waves/round-51/preregistration.json`; counters `tools/round51-replay-exe-audit.py` sha256 `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155` and `tools/round51-append-audit-v6-check.py` sha256 `254e63bab046428d4099d008929751701ed7b0600b96874760838a56eb9a1660`; freeze time of record 03:38:24Z, the file's `frozen_at_utc` is 6 s late — erratum `.ufo/waves/round-51/freeze/frozen-at-erratum.md`, KQ64 receipt `freeze/prereg-time-check.out` exit 1). Build `b6bed925`, build-fix `73bf2a7a` (ledger regenerated), build-fix 2 `138af25b` (digest-ledger scope). Starting point: §Planned (round 51) items 1 and 2 and the round-50 closure's R6.

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the replay's own server image, sourced on S499 (proc_pid_exe(5)): the live tool records `server_exe` (the running child's image opened through `/proc/<pid>/exe`: dev, inode, digest) and the replay refuses a rerun whose `server_exe` is not its own extracted `<work>/server/<member>`; the counter keeps every round-50 bind and teardown leg and adds `own` (its own `/proc/<pid>/exe` read equals the extracted member, the receipt and `own_server`) and `newrow` | operability 8 → 8 | base `bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False` (exit 1, `.ufo/waves/round-51/controls/base.c1.out`) → measured value under §Round-51 measured results | `python3 tools/round51-replay-exe-audit.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `tools/kama-llamacpp-live.py` `server_exe()`; `tools/kama-live-replay.py` own-member block; `corpus/SOURCES.md` S499; `corpus/lessons/round-51.md` |
| C2 — append-only-audit v6: default threshold 1 (v5 graded 5 of 106 deletion events); A-row `permitted` rows (only status, recheck, used-by changed; 58 lines); `registry/append-only-disclosures.tsv` names every graded line not held at the tip by commit, file, key sha256, count and mechanical class, and a bad row exits 1; the counter checks nine constructed scenarios and recomputes the lost lines itself, key for key, in every whole-file-graded file | calibration 7 → 7 | base `fixture=0 lane=0 scenarios=0/9 met=False` (exit 1, `.ufo/waves/round-51/controls/base.c2.out`) → measured value under §Round-51 measured results | `python3 tools/round51-append-audit-v6-check.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `tools/append-only-audit.py` v6; `registry/append-only-disclosures.tsv`; `.ufo/waves/round-51/c2/build_ledger.py`; `corpus/lessons/round-51.md` |

Scores held: operability 8, calibration 7; capabilities 11 → 11 (C1 deepens `live-receipt-replay`, C2 deepens `append-only-audit`; the round-49 canonical capability list stays canonical).

Controls (all `met=False`): the base controls above, committed at the freeze; after the build, ablations on the build tree by wave seats (`.ufo/waves/round-51/a2w1/out/`): C1 — J1NoRecord (no `server_exe` record: `bind=0 own=0`), J2DecoyHost (the round-50 J4Decoy shape, host install exec'd and the replay's own check removed: `bind=1 own=0 owned=0/3`); C2 — J5NoLedger (`fixture=1 lane=0 disclosed=0`), J6NoArow (permitted rule removed: `fixture=0 lane=0 scenarios=8/9`), J7Thresh20 (default threshold 20: `fixture=0 lane=0 scenarios=1/9`), J8OneClass (every class `in-place-edit`, one row dropped, one junk row: `lane=0` each).

Integration hardening after the freeze (tools only; the frozen counters are unchanged and were re-run on it): the ledger read from `<to>` may only disclose commits that precede its own introduction (a later deletion must be restored by append — seats K2Cheat, K2Design); the replay holds its member open from before exec to the comparison and refuses a member with more than one link (seats K1Design3, J4Hardlink); an unwritable replay `--out` exits 2 instead of a traceback (seat X1Fresh); four selftest cases kill seat M3Tool's survivors (revert class, CR-stripped key, CR ledger refusal, two-digit ids); `AOA_SELFTEST pass=51`, `KLR_SELFTEST pass=27`. The round-49 banner that round 50 replaced without appending (a v6 finding) is appended under §Superseded head banners.

### What `met=True` does not show (round-51 wave attacks)

- C1: a byte-identical copy of the host binary written to `<work>/server/<member>` before exec meets the counter (K1Cheat3, J3CopyDecoy: `met=True`; preregistered limit); so does a hardlink of the host install at the member path in the counter's own leg (J4Hardlink) — the replay now refuses that (`server-exe:member-links`), the frozen counter does not check it. Whether the replay downloaded the archive at all is not observed. The live tool, the replay and the counter take separate dev/inode snapshots, not one atomic observation, and the counter stats the member path rather than a held descriptor (K1Design3).
- C2: the counter recomputes lost lines only for whole-file-graded files; in `SCORECARD.md` (exempt head sections) and the two `only=## …` knowledge entries a dropped ledger row is caught by the tool alone (J8OneClass p1; preregistered limit). A disclosure carries a mechanical class and the deleting commit's subject, not a judged reason; the slice audits (L1Slice–L6Slice) found every class mechanically right and no moved line missed, and judged the in-place edits contrary to the files' own A-corr practice. As frozen, the counter would accept a ledger that discloses a fresh deletion (K2Cheat); the tool's introduction cutoff now refuses that, the counter does not test it.

### Planned (round 52)

1. Operability: bind the replay's server to the extraction event itself, not to dev and inode of a path — the copy decoy (K1Cheat3, J3CopyDecoy) and an unobserved download stay open (a network witness for the two recorded URLs, or the member digest taken from the replay's own extraction stream and a held descriptor the counter reads); carry the round-50 limits (probe PATH execution, model bytes rewritten after mapping, kills during download or readiness).
2. Calibration: make the C2 recomputation independent of the tool's section logic for the `exempt=` and `only=` files, and test the ledger's introduction cutoff in the counter; decide whether the 166 disclosed in-place edits warrant appended corrections in their files (the slice audits' A-corr finding).

### Round-51 measured results

Measured commit: `be8169a667301dc2b8118615e262968266959303` (post-wave fixes on top of integration `c5ec93d5`; fresh clone of the lane), counters the frozen bytes of `804bde75`. C1 operability 8 → 8: `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0 (`.ufo/waves/round-51/measured/c1.out`; also met at integration `c5ec93d5`, `c1-int.out`, and at build-fix `73bf2a7a`, `c1-build.out`). C2 calibration 7 → 7: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=165 met=True`, exit 0 (`.ufo/waves/round-51/measured/c2.out`; lane `events 107`, 165 disclosed lines in 50 events, 58 permitted lines — one row fewer than the build because the round-49 banner is restored). Regressions at `be8169a6` (`.ufo/waves/round-51/measured/*.out`, each with its `tip=` line): gate `registered 48 unregistered 0 defective 0`; capability census `listed 11 observed 11 met True`; round-41 `mismatches=0 met=True`; round-42 `mismatches=0 maxN=51 met=True`; round-43 `registered=48 mismatches=0 met=True`; digest-ledger `unknown=0`; hexrun-census `unknown=0` (was 2 at the base); `sources-append-only --from 57a2e25b` no violations; append-only-audit exit 0 (`unrestored=0 partial=0 regressed=0 bad_disclosures=0`); selftests AOA 51/51, KLR 27/27, live ok. The planned-pointer check resolves only once this subsection exists (receipt at the final tip). The round-50 C2 counter reads `lane=0` under v6 (stated supersession; round-49 C2 already did at the base).

### Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `fd48f9a3b7ca` (round-26: falsify-wave corrections (SKILL row prose and header, lesson Gate and Mistakes incl. post-data shortcut break, SCORECARD/LOG calibration fixes, no depth promotion), snapshot files fit.cpp/llama-kv-cache.cpp/README.md, wave-2 evidence):

`````text
the report-landing auditor; this round works depth on the serving runtime.
| C1 | depth 7 → 8 (author reading; the closure decides) | `registered 0 counted 0 target 12 met False` at base 1560e4d8 → `registered 17 counted 17 target 12 met True` | `python3 .ufo/waves/round-26/count-c1.py --out <receipt.json>` (counter sha256 6501737c…6588, unchanged since a23c0e04) | the landed lane tip named in the round report (receipt `.ufo/waves/round-26/final/c1-tip-receipt.json`) | SKILL.md "## Round-26 live error signatures" (E26-01 to E26-17), `registry/error-signatures-r26.json`, SOURCES S114-S130, lesson `corpus/lessons/round-26.md` |
runtime; before this round SKILL.md held only the September sample from dead
ports ("Historical error signatures"). The command that would show it unmoved
is the same counter at base (counted 0). Known counter limits found after data
adjacency 7. Capabilities: none added.
`````

Deleted by `4d2e74f421bc` (round-27: residual review call (7 seats) evidence; late w1a3 seat outputs; X1 entry corrections (string-body reachability, literal binding, ASCII scope, frame replay provenance, boundary-leg cost); KQ37 residual qualification; SCORECARD measured-commit fix; lesson residual evidence and Gate decisions):

`````text
| C1 (measured) | depth | 7 → 7 | **miss** (honest stop): withdrawn before data, no data seat dispatched; under the frozen kill rule counted < 15 at the landed tip is a miss | `.ufo/waves/round-27/a3/plan.json`; lesson `corpus/lessons/round-27.md` §Claims; tip receipt `.ufo/waves/round-27/a3/c1-tip.out` | `/usr/bin/python3 .ufo/waves/round-27/count-c1.py --out <receipt.json>` (preregistration.json C1.command) | lane tip at report time (see the report) |
KQ37 with the shortfalls recorded in the entry; defect 8 (`count-c2.py` reads
"neither meets nor misses", 1853 vs 1846); each is corrected by an appended
entry or a superseding row (lesson §Mistakes).
`````

Deleted by `6de225c289b7` (round-29 attempt 2: verification wave w2 (64 seats, orchestrator-dispatched) integration; narrative, verbatim repairs, wave evidence, lesson/knowledge/SOURCES landing):

`````text
| SA29:SCORECARD.md:P:980355388a:0 | SCORECARD.md:192 | P | `MISSION.md:29` | 1e41928a | names the fleet file ../MISSION.md (line 29 is the kama row); no lane path MISSION.md | p:absent |
| SA29:SCORECARD.md:P:312b3e69b1:0 | SCORECARD.md:740 | P | `round-17-verifier-spotcheck.md:217–221` | c6dc46fa | bare file name; the lane file is corpus/lessons/round-17-verifier-spotcheck.md | p:absent |
| SA29:SCORECARD.md:P:1c6c1f3e4c:0 | SCORECARD.md:1349 | P | `.ufo/reports/round-25/kama.md:120-129` | 7f84cd0e | a fleet-repo report path written as if lane-relative | p:absent |
| SA29:SCORECARD.md:P:17a7db7c81:0 | SCORECARD.md:1375 | P | `count-c1.py:384` | d183ec57 | bare file name; the lane file is .ufo/waves/round-26/count-c1.py (line 384 exists there) | p:absent |
`````

Deleted by `026eede9f46a` (round-30: SCORECARD round-30 section (C1 measured row, C2 capability row, planned), lesson with seat findings):

`````text
## Round 30 — self-assessment corrections (recall population)
`````

Deleted by `ce41bae692c8` (round-38: measurement receipts (c1/c2/c3 after.out) and scorecard/log measurement values):

`````text
| C1 — the R36-D2 third sub-fact (R36-D2C) corrected by append | calibration 7 → 7 (delta 0) | `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) at base → `{{C1_AFTER_LINE}}` (exit {{C1_AFTER_EXIT}}) | `python3 /fast/scratch/hyaku/kama-r38/tools/round38-statement-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>` | `{{MEASURED_COMMIT}}` | `.ufo/waves/round-38/controls/c1-noop.out`; `{{C1_AFTER_PATH}}`; `corpus/lessons/round-38.md` |
| C2 — coverage map names the two SGLang docs version-pinning entries | coverage 9 → 9 (delta 0) | `named 0 files_exist 0 cited_new 0 met False` (exit 1) at base → `{{C2_AFTER_LINE}}` (exit {{C2_AFTER_EXIT}}) | `python3 /fast/scratch/hyaku/kama-r38/tools/round38-coverage-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>` | `{{MEASURED_COMMIT}}` | `.ufo/waves/round-38/controls/c2-base.out`; `{{C2_AFTER_PATH}}`; S352, S353, S472 |
| C3 — the round-37 counting instruments and the wave's 37th seat report land | operability 8 → 8 (delta 0) | `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1) at base → `{{C3_AFTER_LINE}}` (exit {{C3_AFTER_EXIT}}) | `python3 /fast/scratch/hyaku/kama-r38/tools/round38-operability-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>` | `{{MEASURED_COMMIT}}` | `.ufo/waves/round-38/controls/c3-base.out`; `{{C3_AFTER_PATH}}`; `tools/round37-statement-audit.py`; `tools/round37-coverage-audit.py`; `.ufo/waves/round-37/w1/out/CriticEntries.md`; `.ufo/waves/round-37/w1/out/seat-exit-codes.json` |
`````

Deleted by `ef76777e5fbd` (round-44: integration — C1 release-recheck ledger at b11889 + S482, C2 verdict ledger + SCORECARD calibration ledger, routed D1-D6, S483, KQ58-KQ61, tools, lesson, LOG):

`````text
Superseded in round 42. The live plan is `### Round-43 measured results
### Planned (round 44)` at the end of this file; the round-5 plan this section carried is kept verbatim under §Historical head sections.
`````

Deleted by `42ea1204aef3` (round-46: move the measured-results block out of the head pointer sentence (repeat of round-43 D1), lesson row, tip receipts at 4991ecc2):

`````text
Superseded in round 42. The live plan is `### Round-46 measured results
### Planned (round 47)` at the end of this file; the round-5 plan this section carried is kept verbatim under §Historical head sections.
`````

Deleted by `db6bfa8d9354` (round-50: measured results filled into scorecard section):

`````text
(placeholder — filled after the measured commit)
`````

## Round 52 — the replay's server runs from a sealed anonymous memfd (operability) and the A-corr files hold every line they declared append-only (calibration) (2026-10-27)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring non-retired axes are calibration, depth and adjacency (7 each); C2 works calibration (the lowest assigned axis) and C1 works operability (the other assigned axis); calibration 7 is below the saturation line 8, so the stagnation nudge is inactive. Attempt 1. Base `9ff76b1f763512be2f554cbbfd0b2213b63b0847` (the round-51 tip after the hyaku orchestrator's salvage of late a2w1 seat output; start census `.ufo/waves/round-52/census/start.out`, exit 0). Freeze `8551ba7f2056f2465d20f5b50586978133212fe1` (`.ufo/waves/round-52/preregistration.json`; counters `tools/round52-replay-memfd-audit.py` sha256 `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` and `tools/round52-append-restore-check.py` sha256 `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea`; `.ufo/waves/round-52/freeze/prereg-time-check.out` → `RESULT pass`). Build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`; wave `kama-r52-w1` (70 seats, spec `34d82600`); integration hardening after the wave (tools and selftests only; the frozen counters are unchanged).

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the replay's server runs from a sealed anonymous memfd, sourced on S500 (memfd_create(2)): the replay copies the verified member from the archive's tar stream into a memfd, seals it (F_SEAL_WRITE, SHRINK, GROW, SEAL) and hands it to the live tool (`--server-fd`), which execs the server from that descriptor; the counter keeps the round-50 bind and teardown legs and adds `sealed` (its own `/proc/<pid>/exe` open: `/memfd:` link, link count 0, seals 15, frozen digest, the same dev/inode/seals in the rerun's `server_exe` and the replay's `own_server`) and `newrow` | operability 8 → 8 | base `bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False` (exit 1, `.ufo/waves/round-52/controls/base.c1.out`) → the value appended under the round-52 measured-results heading below | `python3 tools/round52-replay-memfd-audit.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | `tools/kama-live-replay.py` (`sealed_member()`), `tools/kama-llamacpp-live.py` (`sealed_fd()`, `--server-fd`), `corpus/SOURCES.md` S500 (S501, S502 at integration), `corpus/lessons/round-52.md` |
| C2 — the A-corr files hold every line they declared append-only: the 155 lines `LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md` and 14 filed lessons lost in place are re-appended verbatim (fenced, one block per deleting commit) and their ledger rows removed; the ledger keeps the 10 A/A-row lines a re-append would duplicate; the counter decides graded regions with its own fence-aware section logic and tests the ledger cutoff, `only=` and `exempt=` regions on eight constructed scenarios | calibration 7 → 7 | base `fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False` (exit 1, `.ufo/waves/round-52/controls/base.c2.out`) → the value appended under the round-52 measured-results heading below | `python3 tools/round52-append-restore-check.py --repo <lane clone> --tip <full commit> --scratch <dir> --out <receipt>` | 18 `Restored lines (round 52)` blocks, `registry/append-only-disclosures.tsv` (10 rows), `corpus/lessons/round-52.md` |

Scores held: operability 8, calibration 7; capabilities 11 → 11 (C1 deepens `live-receipt-replay` and `live-llamacpp-lifecycle`, C2 deepens `append-only-audit`'s ground truth; the round-49 canonical capability list stays canonical). What `corr_lost` counts (seat K7Calib): lines the lane's declared A-corr contract grades as deleted and no longer held — a contract-bound count of self-description against history, not a census of every append-only sentence in the lane.

Controls (all `met=False` unless named as a limit): the base controls above, committed at the freeze; after the build, ablations on the build tree by wave seats (`.ufo/waves/round-52/w1/out/`): C1 — J1PathExec (exec from the extracted path: `sealed=0`), J2Unsealed (memfd without seals: `sealed=0`; a descriptor held across exec can still rewrite an unsealed running image), J3CopyDecoy (the round-51 copy shape: `sealed=0`, link count 1), J4Hardlink (`sealed=0`, link count 2); limit probes J5HostMemfd (memfd filled from the host's byte-identical install: `met=True`, preregistered) and J6RenameOver (a rename-over at the member path: `met=True` on the build because the image is the memfd; the same rename-over met the round-51 replay and counter at the base); C2 — J7Prefix (restored lines prefixed `> `: `corr_lost=306`, `lane=0`), J8LeaveRows (A-corr ledger rows left: `lane=0`, `bad_disclosures=155`), J9DropContract (the lessons row dropped or LOG narrowed: `lane=0` through the base-contract leg; the tool alone exits 0 on the dropped row), J10CorrRow (a disclosure row for an A-corr file: `lane=0`).

Integration hardening after the wave (tools only; the frozen counters are unchanged and were re-run on it): `tests/llamacpp-live/check-receipt.py` admits `LD_LIBRARY_PATH` in `child_env_keys` only when the receipt's server block records `fd` (seat V2Review: the build's fd-mode receipts were rejected by the committed checker; selftest `17 VALID`, `108 mutations`); the replay passes MFD_EXEC (S502; seat S4NoExec), re-hashes the sealed bytes (`memfd-content-mismatch`), and its selftest gains five cases that kill seat M2Replay's five survivors (`KLR_SELFTEST pass=36`, `.ufo/waves/round-52/integration/m2replay-survivors-killed.out`); the live tool's selftest now exercises `sealed_fd()` (seat X5Selftest: no case called it), refuses an F_SEAL_EXEC memfd by name and reports a launch failure's errno (seat Sen1Exec).

### What `met=True` does not show (round-52 wave attacks)

- C1: the bytes in the memfd are the frozen ones, but the counter does not observe that the replay read them from its downloaded archive — a memfd filled from the host's byte-identical install meets (J5HostMemfd; preregistered), and so would a memfd made by the live tool from `--server` or passed in by another process (K1Cheat, argued, not run). The server launcher is 17,864 bytes; the code lives in `libllama-server-impl.so` (7.9 MB) and `libggml*`, which still load by path from the extracted tree (K2Design; preregistered). On a host with `vm.memfd_noexec=2` no memfd server can run (S502; the replay refuses with `memfd-create-failed`).
- C2: the counter proves byte retention, not visibility — the restored blocks wrapped in an HTML comment still meet it (K4Cheat). Its `exempt=` rule is simpler than the tool's: four restored `SCORECARD.md` lines (`## Planned`, round 44 and 47 pointers) are ungraded by the counter and graded by the tool (L2Slice; preregistered). The counter's eight fixtures kill only the two ledger-cutoff mutants of the tool among eight behavioural mutants (M5Fixtures); the tool's own selftest is the stronger net there. The restored blocks are history: the preamble says the later text stands, but individual restored claims are not marked superseded line by line (K6Semantics).

### Planned (round 53)

1. Operability: give the replay's server bytes a verifier-owned reference — the counter extracting the receipt's archive member itself, or a witness of the replay's own archive stream — so a memfd filled from the host install (seat J5HostMemfd) fails; and per-mapping identity for the code the launcher loads (`libllama-server-impl.so`, `libggml*`, the chosen CPU backend) and for the model, read from `/proc/<pid>/maps` and `map_files` (seats K2Design, N2Pattern), with a control that swaps a library after the member check.
2. Calibration: make the C2 counter's `exempt=` rule the tool's (origin and not-gutted), add fixtures that kill seat M5Fixtures' six surviving tool mutants, and check restored blocks for visibility (seat K4Cheat: an HTML comment hides them); land seat W3Mistakes' seat-report-immutability and cited-path-exists checks as lane instruments.

### Round-52 measured results

Measured commit: `35e3b1dc9ca32c24e543366c6ff78e15c0bdb32e` (integration on top of the build `5dacf2c7`; fresh clone of the lane, `.ufo/waves/round-52/measured/measure.sh`), counters the frozen bytes of `8551ba7f`. C1 operability 8 → 8: `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0 (`.ufo/waves/round-52/measured/c1.out`; also met at the build, `c1-build.out`, and by seats X1Rerun and X2Rerun independently). C2 calibration 7 → 7: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0 (`.ufo/waves/round-52/measured/c2.out`; also met at the build, `c2-build.out`, and by seat X6Rerun). Regressions at `35e3b1dc` (`.ufo/waves/round-52/measured/*.out`, each with its `tip=` line): gate `registered 50 unregistered 0 defective 0`; capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; r41 `mismatches=0 met=True`; r42 `mismatches=0 maxN=52 met=True`; r43 `registered=50 mismatches=0 met=True`; planned pointer `met=True`; digest-ledger `unknown=0`; hexrun-census `unknown=0`; `sources-append-only.py --from 9ff76b1f` `no append-only violations`; append-only-audit `unrestored=0 partial=0 regressed=0 disclosed_lines=10 bad_disclosures=0`, exit 0; `AOA_SELFTEST pass=51`, `KLR_SELFTEST pass=36`, live `selftest: ok`, check-receipt `17 VALID … 108 mutations`; r48c2, r49c1, r50c1 and r51c2 `met=True`; census exit 0. The round-51 C1 counter now reads `own=0 met=False` (`r51c1.out`): its leg binds the image to the extracted path, which the memfd replaces — a supersession by a stronger binding, not a lost capability (seats R1Old, K5Harm). The planned-pointer receipt at this file's own commit is taken after it lands and committed in the next lane commit (round-51 closure D3).

### Evidence-pointer corrections (round 53)

Round-53 claim C2: 16 repository paths cited outside fences in this file, `SHONEN.md` and `SKILL.md` resolved in neither the lane tree nor the fleet tree at the round-53 base (`.ufo/waves/round-53/controls/base.c2.out`). The lines that cite them stand as filed; each miss is disclosed, with a reason `tools/round53-cited-path-check.py` re-derives from git history, in `registry/cited-path-corrections.tsv`: 7 citations here name paths that were never committed (four of them already said so in their own sentence, one is a range notation for eleven existing directories), one names a 404 body that commit `9874e455` removed, one names the fleet driver's untracked runtime log, and one names llama.cpp's own `tools/server/server-schema.cpp` at the pinned snapshot `704366d76`, re-fetched with the digest `SKILL.md` pins. `SKILL.md`, which is not append-only, is corrected in place where a citation was wrong (two lines) and discloses its four llama.cpp file names the same way.

Correction (round-53 falsification): the prior sentence overstates C2's re-derivation. The frozen counter checks current disk/tree state for `untracked` and HTTP 200 for `upstream`; it does not validate the note's full truth or the upstream content digest (X8Regen, J11BadFixed). The `.ufo/watchdog.log` row's original note was wrong: fleet history tracked it from `609ecb6e` until `7930399e`; an appended correction comment is in `registry/cited-path-corrections.tsv`. The frozen counter's green C2 receipt is not a general self-assessment truth check (J12Hide).

## Round 53 — archive executable mappings and cited-path calibration (2026-10-27)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest assigned axis (depth and adjacency also 7), below saturation 8; the stagnation nudge is inactive. Base `4229ea1b9a789148dded1f159c20967d9a01373f`; freeze `d01b2b6d48a54ffe0e475000737d3e302c62e28e`; build `c22602bd8d83ab26349d1087e916ca537ee4f9d1`; wave spec `bc8e6e7f1c53ea6f557001cea1e4d1e8b586c18e` (one v2 wave, 66 seats; 21 attack roles). Frozen predicates and counter hashes are in `.ufo/waves/round-53/preregistration.json`.

| Claim | Axis, score | Before → after | Frozen counting command | Evidence / verdict |
|---|---|---|---|---|
| C1 — the replay's server code mappings are archive members checked by the replay, and an independent observer reads executable ranges from the running process and compares them with its own archive download; retains round-52 bind/sealed/teardown legs | operability 8 → 8 | base `bind=1 sealed=1 code=0 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False` (exit 1) → build `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True` (exit 0) | `python3 tools/round53-replay-code-audit.py --repo <clone> --tip <full-commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-53/controls/base.c1.out`, `.ufo/waves/round-53/measured/c1-build.out`; X1Rerun/X2Rerun independently reproduce; J1/J2/J3 controls show the byte-swap leg is load-bearing. C1 counter result verified at build; limits: root-owned outside-tree code is accepted, host libraries are not byte-compared, and counter skips executable memfd mappings. |
| C2 — cited repository paths resolve or their miss is disclosed by a correction row | calibration 7 → 7 | base `fixture=1 lane=0 scenarios=8/8 cited=679 unresolved=16 undisclosed=16 bad=0 stale=0 dropped=0 met=False` (exit 1) → build `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` (exit 0) | `python3 tools/round53-cited-path-check.py --repo <clone> --tip <full-commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-53/controls/base.c2.out`, `.ufo/waves/round-53/measured/c2-build.out`; X7Rerun/X8Regen reproduce the miss counts. **Not verified/admissible:** J12Hide hides dead SKILL.md citations and removes their ledger rows while the frozen counter still returns `met=True`; J11BadFixed also shows `upstream` accepts HTTP 200 without verifying pinned bytes. The target's kill rule is falsified. |

Scores remain 8/7; capabilities remain 11. No measured axis score delta is claimed. C1's measured counter predicate passes; C2's count passes but its attack control invalidates the claim. No round-53 acceptance is asserted.

### What `met=True` does not show (round 53)

- C1 does not compare the 13 root-owned host executable libraries against a byte reference; J5Preload demonstrated that arbitrary root-owned, non-writable code outside the archive is accepted. A byte-identical host installation remains indistinguishable from an archive-derived one. Data/RELRO segments and the model's mapped bytes are not compared, the download is not witnessed, and a mutation after the counter's single memory read is not observed. A second executable memfd is rejected by the integrated replay, but the frozen counter itself skips `/memfd:` mappings.
- C2 is an existence/disposition instrument, not a truth or reachability checker. J12Hide changes SKILL.md citations to non-citation forms and removes their ledger rows; all variants meet the counter. Its `dropped` leg protects SCORECARD.md tokens only. J11BadFixed shows an upstream row can point at content with a different digest (or a mutable ref) and still pass on HTTP 200. The `untracked` row checks present disk/tree state, not a history-derived explanation; its original note was false and a correction comment was appended. Sen4Fixture found inherited `GIT_*` environment can redirect fixture git calls; do not run this frozen counter in an environment with untrusted Git overrides.
### Planned (round 54)

1. Operability: bind every non-archive executable mapping to a verified allowlist/provenance, including the root-owned host-library route, and extend the counter to inspect executable memfd mappings; explore the model's mapped bytes without relying on a pathname. Keep the byte-identical host-install, data-segment, post-read rewrite, download, and ptrace-scope limits explicit.
2. Calibration: do not reuse round-53 C2 as an admission gate without first replacing its frozen weaknesses in a new preregistered counter: guard citation drops across all registered surfaces, validate upstream bytes against a pinned digest, validate ledger reasons/notes, make fixture Git environment hermetic, and attack scorecard/skill hiding controls before data.

Assimilation: none from shokuknow (`A1Assim`). One considerthese proposal mined: `considerthese/2026-10-26.md` proposal 2 is captured in `corpus/QUALITY.md` KQ97; this is a curation criterion, not a new round-53 claim.

## Round 55 — the round-54 counters frozen, measured and battery-killed (2026-10-27)

Authority: `shokunin.conf` assigns operability + calibration; calibration 7 is the lowest
assigned axis (depth and adjacency also 7), below the saturation line 8; the stagnation
nudge is inactive. Base `3a600d2f729828419aaea34cc402c8b0d20fb720` (round-54 tip);
freeze `9c60eae6f7ed84f7da93d219a406aadc30958c6c`; wave `kama-r55-w1` (one v2 wave,
64 seats, 44 settled at the integration commit; the wave was still settling at wrap-up
- see the round report). Frozen predicates, counter sha256s and kill rules:
`.ufo/waves/round-55/preregistration.json`.

| Claim | Axis, score | Before → after (measured) | Counting command | Evidence |
|---|---|---|---|---|
| C1 — the round-54 replay-code counter frozen for round 55 (BASE re-frozen to the round-54 tip, newrow row re-pointed at S511, every git call `GIT_*`-stripped) | operability 8 → 8 | base `bind=1 sealed=1 code=1 teardown=1 newrow=0 ... met=False` (exit 1) → build `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True` (exit 0); kill battery: control green; m-ldpreload kills envnames; m-text-flip kills code; m-member-flip kills rehash; m-ldaudit-foreign vector analysis (`met=True` by design) | `python3 tools/round54-replay-code-audit.py --repo <clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-55/controls/base.c1.out`, `measured/c1-build.out`, `c1/battery/*.out`; independently reproduced by seats X1Rerun, X7, K1DoNothing |
| C2 — the round-54 cited-path counter frozen with the `superseded` ledger class + fixture scenario (BASE stays at the round-53 tip so the drop horizon covers the round-54 re-anchor; the pre-freeze do-nothing catch reverted a same-tip BASE) | calibration 7 → 7 | base `fixture=1 lane=0 scenarios=15/15 dropped=1 met=False` (exit 1) → build `fixture=1 lane=1 scenarios=15/15 undisclosed=0 bad=0 stale=0 dropped=0 met=True` (exit 0) | `python3 tools/round54-cited-path-check.py --repo <clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-55/controls/base.c2.out`, `measured/c2-build.out`; reproduced by seats X2C2Rerun, X6C2Smoke, K1DoNothing |

Scores remain 8/7; no capability enters (both counters were already registered as
round-54 instruments; round 55 freezes and measures them).

### Kill-rule disposition (round 55)

The frozen C1 kill rule ("falsified if any battery mutant prints met=True") fires on
its literal text: the bring-up-redesigned battery (committed `8abadfed`) contains the
vector-analysis receipt `m-ldaudit-foreign.out` (`met=True` by design) and the roster
diverged from the preregistration's named mutants (`m-ldaudit-writable` replaced by
`m-text-flip`; two stale first-run receipts deleted at integration, named in the
lesson). The three kill-designated mutants each print `met=False` with their named leg
failing; seats Rev1/L1Probe grounded the hostlibs vector (a conforming audit module IS
loaded by glibc; the live hostlibs kill stays root-gated) and Rev1 demonstrated the
anon leg killing an in-set-basename plant (`anon=6`). Reported honestly: C1 measured
green on predicate and target; the kill rule as frozen fired; the closure rules.
C2's kill rule is discharged (base red, build green, 15/15 fixture, forged-superseded
mutants killed by seat M3LedgerMut 5/5).

### What `met=True` does not show (round 55)

C1: host libraries bound by basename, not bytes (a root-owned in-set-basename plant
survives - seat Rev1 D3; LD_AUDIT is not a named BAD_ENV; the host count is printed,
not asserted); model/data mappings uncompared; the sampling window (two passes + a
post-exit re-hash); under Yama ptrace_scope > 1 the counter exits 1 instead of
could-not-evaluate (seat Sen2); `git archive` honors tree and global `export-ignore`
attributes, which fails the counter closed with no receipt (seat Rev2); inherited
user gitconfig/`XDG_CONFIG_HOME` still reaches every git call - a malformed config
crashes C2's moved branch with no receipt (seat Sec1). C2: existence/disposition, not
truth; upstream rows validate bytes at the pinned commit, not content; prose root
tokens advisory; the `superseded` branch checks cited-at-base, not resolved-at-base
(seats K2Predicate/K4Sizing - next-freeze wording); the round-53 `untracked`-row
present-disk-state/no-history limit remains open (seat Rev4 D1).

### Planned (round 56)

1. Operability: close the root-owned host-library route with byte-provenance (e.g.
   package-owner binding) and assert the host count; name LD_AUDIT in BAD_ENV; make
   the counters' git environment fully config-hermetic (the C2 fixture's own
   `GIT_CONFIG_GLOBAL=/dev/null` + `GIT_CONFIG_NOSYSTEM=1` pair) and pin
   `--worktree-attributes`-free archive extraction.
2. Calibration: re-freeze the C1 battery roster with the preregistration (kill-designated
   mutants only, vector analyses named as controls); adopt the KQ98 criterion proposal
   (seat Sc4Quality) once the outside closure agrees the classification.

Integration repairs (wave seats, inherited from base `3a600d2f`): SCORECARD calibration
run-fact 40→41 (seat X8Regression; the round-54 closure's own spotcheck file is the
41st); hexrun-ledger row + evidence for fleet commit `e2e2d10f`. Census: start exit 1
(E11 S510) → end exit 0 (receipts `.ufo/waves/round-55/census/{start,end}.out`).

## Round 56 — LD_AUDIT environment classifier and roster-fidelity gate (2026-10-27)

Base `e10b6d39af450e8d652be9ac2986768b531fe13f`; freeze `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`; measured implementation tip `b9d5a091d25676e6c5078d330ebd6abd21a4fc7d`. One v2 wave `kama-r56-w1`, 64 seats; L1 held the planner seat. Claims are distinct and measured at their final committed implementation tip:

| Claim | Axis, score | Before → after | Counting command and evidence |
|---|---|---|---|
| C1 — `LD_AUDIT` is rejected by the replay counter's env-name leg | operability 8 → 8 | old counter `ld_audit=missed` (exit 0) → round-56 counter `ld_audit=detected` (exit 0); one-line deletion mutant misses and fails the positive expected-detected assertion (exit 1); comparator selftest rejects `undetected` as `detected` | `python3 tools/round56-env-leg-battery.py`; base `.ufo/waves/round-56/controls/base-c1.out`; final `.ufo/waves/round-56/measured/{base-c1,build-c1,m-drop-ldaudit,m-drop-ldaudit-target-fails,comparator-selftest}.out`; frozen counter `tools/round56-replay-code-audit.py` SHA-256 `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` |
| C2 — preregistered battery-roster fidelity (counter target falsified for admission) | calibration 7 → 7 | base `present=0 roster_match=0 met=False` (exit 1) → final `present=1 roster_match=1 kills=1 controls=2 met=True` (exit 0); no-op fixture `e6417941` carries the matching ROSTER but executes no battery entries and still returns `met=True`, so §9's do-nothing-control rule invalidates C2 as a calibration move | `python3 tools/round56-prereg-check.py --repo <lane clone> --tip b9d5a091d25676e6c5078d330ebd6abd21a4fc7d`; base `.ufo/waves/round-56/controls/base-c2.out`, final `.ufo/waves/round-56/measured/final-c2.out`, no-op `.ufo/waves/round-56/measured/c2-noop-control.out`; frozen checker SHA-256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` |

Scores remain operability 8 and calibration 7; no capability enters. C1 demonstrates a variable-name rejection in a synthetic child process, not successful audit-DSO injection or a live model-server/endpoint-health result. C2's frozen counter checks a declared ROSTER literal, not that the harness executes its entries; the no-op fixture proves that target is reachable without the claimed battery execution, so C2 is not admitted. Its dead `BASE` constant and roster-only scope are named limits; the M07 metadata-base probe also stays green, outside the frozen predicate.

Routed work and integration: round-55 stale lesson receipt claim corrected append-only in `corpus/lessons/round-56.md`; battery records exits, checks exact fields, and includes an `undetected` comparator negative control; S510/S511 anchor revision omissions are corrected by append-only superseding rows S514/S515; SCORECARD depth and calibration labels re-anchored, including the 42-spotcheck count and round-55 admitted closure; 305 inherited round-55 late outputs/results committed under `.ufo/waves/round-55/`; all 64 round-56 seat outputs/results committed under `.ufo/waves/round-56/w1/`.

### Sources and frontier — round 56

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`: before exit 0, 252 rows (A/B/C 239/9/4; mined/queued/rejected 228/8/16); after exit 0, 256 rows (A/B/C 242/10/4; mined/queued/rejected 231/8/17). Receipts `.ufo/waves/round-56/census/{start,end}.out` and `end.exit`. Rows added: A=3 (S512, S513, S514), B=1 (S515); statuses mined=3, rejected=1. Touched row: S512 `used-by` old `corpus/lessons/round-56.md` → new `corpus/lessons/round-56.md, tools/round56-replay-code-audit.py`; no status/recheck edits in place. Frontier rows advanced: none. Assimilation: none. `considerthese/2026-10-26.md` proposal 4 remains pending.

### Trend verdicts

- **expansion — unchanged:** no new `corpus/knowledge/` entry or uncovered knowledge ground was admitted; S512–S515 are curated source rows, not expansion credit (`CORPUS.md` rule 4).
- **quality — improved:** the frozen environment classifier now detects LD_AUDIT; the exact comparator selftest rejects the `undetected` false positive; C1/C2 final measurements and receipts are at the implementation tip above.
- **discernment — unchanged:** no outside non-author admit/reject spot-check of this round is on record; the swarm's reviewers and critics are lane-dispatched seats and do not count as non-author judgment.

### Planned (round 57)

1. Operability: continue the remaining round-56 plan—host-library package-byte provenance and asserted host count, fully config-hermetic Git environment, and attribute-free archive extraction—with freeze-bound counters and red do-nothing controls.
2. Calibration: re-freeze C2 only after its counter is causally bound to executed battery invocations and a no-op harness fails the frozen counter; address the KQ98 criterion proposal only after outside closure agreement. Do not retroactively amend round-56 predicates.

## Round 57 — no-op control and stale calibration census (2026-10-27)

Pre-data freeze: `89dc4f5239fe1f875adda4613812e77fb9bbc7cc`; ordering correction, still before seat evidence: `7c873d7b4e3839489a93d6334cdf93fe5d34d19f`. C1 is the frozen round-56 prereg checker no-op defect (operability); C2 corrects the verifier-spotcheck count (calibration). Base `b89bdab2cc114735ec5d331c6c610134258f7864`.

| Claim | Axis, score | Before → after | Counting command and evidence |
|---|---|---|---|
| C1 — bind declared roster to actual battery call sites | operability 8→8 | genuine round-56 roster: `met=True` → `met=True`; matching-roster no-op: `met=True` → `met=False` (exit 1) | `python3 tools/round56-prereg-check.py --repo <repo> --tip <revision>`; `.ufo/waves/round-57/measured/noop-c1.out` |
| C2 — re-anchor the SCORECARD verifier-spotcheck count | calibration 7→7 | frozen round-42 counter `mismatches=1 met=False` (expected 42, observed 43) → `mismatches=0 met=True` | `python3 tools/round42-selfdesc-reconcile.py --repo <repo> --tip <revision>`; `.ufo/waves/round-57/controls/base-c1.out`, `.ufo/waves/round-57/measured/c2-final.out` |

Scores held at operability 8 and calibration 7; no capability added. C1 does not assert that every runtime effect of a battery call was executed; it checks the call-site inventory in the committed battery AST. C2 corrects one stale factual count; it is not a mastery score.

## Historical authority banner — round 55

The prior pre-heading banner is preserved verbatim because the append-only audit
grades that preamble line; the round-56 authority above supersedes it.

```text
**Current authority (round 55):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 55. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. Round 55 froze and measured the two round-54 counters (C1 operability, C2 calibration) with red base controls committed before data (SCORECARD §Round 55); the C1 kill rule fired on its literal text and is reported for the closure to rule. No axis score or capability changes. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current through round 55; the round-53 banner and the head sections it replaces are kept verbatim under §Historical head sections.
```

## Historical pre-integration authority text — round 56

The exact former current-authority line is retained here; the live authority above supersedes it.

```text
**Current authority (round 56):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 56. Calibration 7 is the lowest assigned axis, below operability 8 and the saturation line, so the stagnation nudge is inactive. Round 56 froze and measured C1 (LD_AUDIT environment-name rejection, operability) and C2 (preregistration/battery roster fidelity, calibration) with red base controls committed before data (SCORECARD §Round 56). Scores remain operability 8 and calibration 7; no capability enters. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current through round 56; the round-55 authority is kept under §Historical head sections.
```

