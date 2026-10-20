# ReportScribe — round-11 report checklist, SHONEN box mapping, reporting requirements

Advisory, read-only. Seat: ReportScribe (scribe). Lane: kama-shokunin. Round label is the steered 2026-10-19; actual UTC review date is 2026-10-20 (`date -u`, 2026-10-20T02:14:38Z). No new verification is claimed under the steered date. No fleet report written; no measurement claimed. Nothing was executed except read, glob and grep. No sibling report, LOG.md, SCORECARD.md, SKILL.md, corpus/README.md, QUALITY or lesson was edited.

Installs or updates by this seat: **none**. `~/.omp/agent/RULES.md` and `~/.agents/AGENTS.md` were read; no tool was needed for a read-only mapping.

## 1. SHONEN.md — verbatim checklist (SHONEN.md#8CE4, reviewed 2026-10-20 UTC; file content as observed, historical author assertions unchanged)

Header and gate line, verbatim:

```
# kama-shokunin — Promotion checklist

Promotion to shokunin requires all of:
```

Four boxes, verbatim (lines 5–12). Each box is one `[~]` line followed by one `→ Author assertion:` line:

| Box | SHONEN.md lines | Verbatim box text | Verbatim evidence pointer (author assertion) |
|---|---|---|---|
| B1 | 5–6 | `- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources` | `→ Author assertion: \`SKILL.md\` §§Decision table, Error signatures, Checklist; no named non-author verifier.` |
| B2 | 7–8 | `- [~] At least one end-to-end domain task executed and logged in LOG.md` | `→ Author assertion: \`LOG.md\` §§round 1–3 records executed endpoint reconciliation and invocation history; current \`DEAD\` is not model readiness.` |
| B3 | 9–10 | `- [~] Instructions executable by an agent without oral context` | `→ Author assertion: \`SKILL.md\` §Checklist and \`corpus/knowledge/snapshot-history.md\` §Run it; independent execution review remains open.` |
| B4 | 11–12 | `- [~] No cross-domain bleed (PROVINCE.md still accurate)` | `→ Author assertion: \`PROVINCE.md\` §Write boundary and \`corpus/knowledge/cross-lane-scope.md\`; service repair, routing and credentials remain operator/sibling-owned.` |

Mapping rules that follow from the file and its lane records:

- `[~]` is the lane's author-assertion marker, not a pass. SCORECARD.md (round 10 learning table) and reports/round-5/kama.md §SHONEN both say author assertions "remain `[~]`, never promotion `[x]`". No `[x]` may be written in round 11.
- No box is verified by a non-author. Each box's own text says so (B1 "no named non-author verifier"; B3 "independent execution review remains open"). The round-5 report states "No promotion or independent spot-check is asserted." Round 11 must carry the same sentence.
- Round 11 C1 changes `corpus/knowledge/*.md` provenance; C2 adds one served-identity knowledge entry. Of these, B3 and B4 point at `snapshot-history.md` and `cross-lane-scope.md`. Both are among the nine legacy files that will receive appended provenance. Their pointers stay valid only if the append-only rule holds (see §3, item 6).
- B2 cites LOG rounds 1–3 only. Any round-11 LOG entry does not change B2's evidence pointer; B2's "current `DEAD` is not model readiness" is a standing caveat, not a round-11 measurement.
- SHONEN.md is not in the spec's owned or parent-owned lists (spec.json contract). No seat owns it. Integration should either state "SHONEN unchanged" or name an owner. No box is changed by C1/C2 as specified.

## 2. Round-11 report checklist (what the final fleet report must contain)

Derived from reports/round-5/kama.md (structure) and the spec.json contract. Every item is required; "n/a" must be stated, not omitted.

1. **Header and status line.** Wave `kama-round-11`; sole-lane statement; one sentence stating whether the round is admitted or a verified completed round. Do not count a headless launch, a dispatch count, or a report file as a completed round (round-5 and SCORECARD precedent).
2. **Scope and commit.** Lane baseline commit and the work commit, each stated as a full hash. Inherited `lane_head` is `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` (`.ufo/waves/round-11/inherited-state.json`). Work commit: to be supplied by integration. Do not assert a work commit that was not observed.
3. **Work performed.** One bullet per landed change, each with the exact file and the evidence path.
4. **Before → after measurements.** Name the measured field set and the exact command. For C1 the baseline is `.ufo/waves/round-11/legacy-baseline.json` (9 files, 27 missing fields: `source`, `verified-at`, `recheck` on each). The after-value must come from a counting command run in round 11; none has been run by this seat. Report the baseline sha256 and the post-change sha256 of each of the nine files, and state whether the original bytes are a strict prefix (append-only).
5. **Axes and learning trends.** Two tables:
   - Axis table, format from reports/round-5 and SCORECARD: `Axis | Verdict | Evidence/limit`. Verdict vocabulary: `improved`, `unchanged`, `harmed`. Axes: operability, freshness, depth, coverage, calibration, adjacency.
   - Learning-trend table, format from SCORECARD round-10: `expansion | quality | discernment`, same verdict vocabulary.
   - Scores: a number is allowed only if a counting command produced it and it is labelled "self-assessed, pending non-author verification" (round-10 precedent). Blocked or unmeasured rounds advance no scalar ("No scalar score is advanced", SCORECARD round 5/6–9).
6. **Sources and trends.** Report the `corpus/SOURCES.md` census as observed, with its command. Baseline, from `.ufo/waves/round-11/sources-census-before.json` (exit 0, stdout recorded, not re-run by this seat): rows 30; tier A 27; tier C 3; tier B 0; status mined 17, queued 8, rejected 5; missing 0; invalid 0. `sources-validate-before.json`: `kama ok`, exit 0. Any after-census must be shown alongside these, and any change in row count must be explained. Queued rows (S011, S012, S016, S021, S022, S023, S025, S029) and rejected rows (S024, S026, S027, S028, S030) must be named if a round-11 entry touches them. A queued row used as evidence for a present-tense claim is a KQ6 violation.
7. **Stale-lane reporting.** State explicitly what is stale rather than letting it read as current:
   - Last live endpoint sample on record is round 5 (2026-10-15): `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`, all three rows DEAD/connection-refused (`.ufo/reports/round-5/kama.md`; PROVINCE.md:31-38). Any round-11 endpoint statement needs its own probe command, timestamp and exit (KQ1). Without one, write "not sampled this round".
   - Blocked dispatch rounds 6–9 (SCORECARD) and blocked round 5 (native role bindings unrealised). They are history, not admission.
   - Round-3 report gap (`.ufo/reports/round-3/kama.md`) remains recorded as a gap. Not verified this seat.
   - `corpus/lessons/round-1-relaunch-freshness.md` and the round-1 log text are inherited historical records. Do not relabel them as round 11.
   - Round label: round 11 must be `max+1` from the log history; never reuse a label (round-10 Mistake 16).
8. **Installs and tool records.** Every install or update: tool, version, channel, reason. Round 11 seats: none recorded by this seat. Parent to record any it performs.
9. **Inherited state.** Report `inherited-state.json` verbatim in substance: lane head `2f7303c…`; untracked `.ufo/round-10/SEAT-PROTOCOL.md` and `.ufo/round-10/plan.json`; disposition "retained as historical undelivered plan … no old route or dispatch is executed." Say that these untracked files were not executed.
10. **Blocking debt and unblock.** Carry forward, named with owner: operator (serving runtime restoration or retirement ruling; route bindings for native roles — reports/round-5 §Native task route contract); fleet integrator (real taskKey/receipt binding; cumulative verified-round reconciliation, round-3 gap). No "unblocked" claim without evidence.
11. **Continuation.** One line: next fresh-session candidate, and "NO PUSH" if nothing was pushed. Never restart a counter at 1; never count the landed correction twice.
12. **Non-claims.** Explicit list: no runtime integration, no vLLM/Ollama real-runtime evidence (fixture/parser only, per README §Known gaps), no outside verification, no promotion `[x]`, no completed round.
13. **Defects and limits** (spec contract: "defects and limits" are required output).
14. **Evidence paths.** Every number in the report points to a file path plus a command or a quote of ≤25 words with location.

KQ5 applies to the report body: nonsecret shape evidence only; no config bodies, environment values or credential lines. Round-10 Mistake 9 is a precedent for a whole-file config read leaking a credential line.

## 3. Defects and inconsistencies found in the round-11 inputs

1. **Legacy file count conflict.** `corpus/SCORECARD.md`/`SCORECARD.md` line 203 (Planned round 11) says "provenance … for the **18** pre-round-10 entries". `.ufo/waves/round-11/legacy-baseline.json` and spec.json C1 say **9** files, **27** missing fields (9×3). The directory `corpus/knowledge/` holds 12 `.md` files: nine legacy plus three round-10 (`runtime-health-surface-matrix.md`, `serving-metrics-crosswalk.md`, `gguf-runtime-compatibility-boundary.md`). The report must use 9/27 with the baseline hashes and mark the "18" as an unreconciled planning figure.
2. **`QUALITY.md` path.** spec.json contract and the ReportScribe prompt ask the seat to read "repo PROVINCE.md/QUALITY.md". There is no root `QUALITY.md`; read returned not found. The real quality bar is `corpus/QUALITY.md` (KQ1–KQ10). Treat the spec's bare `QUALITY.md` as `corpus/QUALITY.md`.
3. **Axis authority vs coverage work.** spec.json C2 is a coverage move. SCORECARD.md header (lines 6–8) and the round-10 entry name the LIVE axes as operability and freshness; coverage is non-LIVE. The C1 freshness move is the lowest LIVE tie. Report C2 under `coverage` only, and do not let its entry raise an operability or freshness verdict.
4. **Report location.** Round-11 `reportDir` is `.ufo/waves/round-11/advice`. Prior fleet reports sit at `.ufo/reports/round-N/kama.md` (SCORECARD round 6–9 pointers; reports/round-5/kama.md exists). Integration must state which location is the fleet report. This seat writes only to the advice path.
5. **Path error in my own read.** `.ufo/waves/round-10/SEAT-PROTOCOL.md` does not exist; the file is `.ufo/round-10/SEAT-PROTOCOL.md` (confirmed by glob). Recorded so the parent does not chase the wrong path.
6. **Append-only pointer risk.** B3 and B4 pointers and the KQ3 rule ("Corrections preserve old corpus bytes") mean the nine legacy files must be appended, not rewritten. The round-11 report must include the before and after sha256 of each to prove it. Baseline hashes are in `legacy-baseline.json`.
7. **Freshness tie.** Round-5 SCORECARD gives freshness 7 and operability 8 (inherited); round-10 errata gives freshness 8 and operability 8. The spec's "both 8" follows the round-10 errata. Report the value as "8 (round-10 errata)" and do not restate the inherited 7 as current.
8. **Unverified claims in SHONEN B2/B3.** `LOG.md` §§round 1–3 and `corpus/knowledge/snapshot-history.md` §Run it were not opened by this seat beyond their existence in the glob. [INFERENCE] they are the cited sections; not verified.

## 4. Not done, by design

- No census, probe, listener scan or endpoint contact was run (spec contract: no endpoint census; KQ10).
- No measurement result is stated as round-11 evidence. The only numbers above come from the `*-before.json` baselines and the round-10 SCORECARD, labelled as such.
- No fleet report, LOG, SCORECARD, SKILL, corpus README, QUALITY or lesson file was written.
- No commit, push, test, lint, build or formatter was run.
