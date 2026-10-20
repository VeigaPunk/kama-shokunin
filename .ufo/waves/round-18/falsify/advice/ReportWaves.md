VERDICT: partial — committed provenance supports the 95-refused → 75-dispatched refit and role mix; completion is summary-reported, the raw spawn snapshot is pending, and 32 capacity records exceed the prose count of thirty.

# ReportWaves — evidence draft only

## Scope and axes

- Target revision: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.
- Assigned product axes: **operability 8 → 8** and **calibration 7 → 7**, calibration lowest. This report audits wave accounting, not either product claim's admission. Evidence: `SCORECARD.md:737–760`, `corpus/lessons/round-18.md:13–29`.
- Reporting axes: distinguish attempted/validated/spawned/completed/reported seats; preserve refusal and capacity evidence; separate declared role/planner routing from execution evidence; do not infer an actual answering model.
- All substantive wave observations below come from the target revision checked out in the separate scratch clone. No current, uncommitted falsify-wave totals are promoted into committed evidence.
- KQ23/KQ24 were read at `corpus/QUALITY.md:125–133`. No new control-path, lifecycle, mutant-kill, or runtime-health claim is made here. This is L1 advice, **not an outside non-author judgment**.

Paths in citations and the digest manifest are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`; actual reads and commands used absolute paths. The digest manifest binds the findings to the committed bytes, not the concurrently changing working tree.

## Behavior and wave totals

### W1 — refusal, refit, dispatch, and distinct denominators

Evidence: `.ufo/waves/round-18/build/validation-95.json:1–29`, `validation.json:1–30`, `attempts.json:1–9,165–175`, `refused-result-1.json:1–8`, `spawn-result.json:1–9`, `assignments.json:1–77`, and `make_spec.py:269–281`.

| Population / observation | Count | Evidence level |
|---|---:|---|
| Initial payload validated at 19:55:28.510562Z | 95 spawn, 0 resume | Retained validation receipt, recorded exit 0 |
| Initial task call at 19:55:45.804562Z | 95 refused, 0 spawned | Attempt record plus 95 distinct labels in raw refusal prose; raw `details.results` is empty |
| Refit payload validated at 20:59:16.522003Z | 75 spawn, 0 resume | Retained validation receipt, recorded exit 0 |
| Refit task call at 20:59:22.366243Z | 75 spawned, 0 refused recorded | Raw spawn header and 75 pending progress entries; assignments allocate 75 IDs |
| Build completion | 75 completed, dead `[]` | **Recorded by completion-summary.json**, not a terminal raw task-result capture |
| Build report inventory | 75 files: 45 confirm, 26 partial, 0 refute, 4 n/a | **Recorded by completion-summary.json**; this scribe did not rerun the counter |

The initial refused 95 are **not** 95 dead workers and are **not** additional completed seats. The 20 omitted refit items are retained declarations, not executions. The populations are 95 attempted and refused, followed by a separate 75-seat refit dispatch; do not describe them as 170 completed seats or as a 95-seat successful build.

Exact raw refusal message suffix, repeated for 95 distinct labels:

> Background job limit reached (100). Wait for running jobs to finish or cancel one.

Exact first entry:

> Failed to start background task jobs: KamaR18.C1LiveTool: Background job limit reached (100). Wait for running jobs to finish or cancel one.

The raw refused envelope has `projectAgentsDir: null`, `results: []`, `totalDurationMs: 0`. The retained attempted-call error is exactly `Background job limit reached (100)`.

The refit is recorded as one revalidated wave, not a split. `dispatch.json` contains 75 task entries, no resumes, and the instruction to issue exactly one batched task call. One successful task-call entry is retained in `attempts.json`. This supports the recorded one-wave refit; it is not an independent capture of every orchestrator action.

### W2 — role mix and registry trap

Evidence: `validation-95.json:17–28`, `validation.json:17–29`, `completion-summary.json:5–13`; queried `.taskCall.tasks` in each dispatch artifact and `.members` in `build/advice/swarm-registry.json`.

| Role | Initial refused payload | Refit dispatched payload |
|---|---:|---:|
| executor | 13 | 13 |
| mutation-tester | 4 | 4 |
| sentinel | 2 | 2 |
| scout | 23 | 19 |
| reviewer | 20 | 16 |
| critic | 8 | 6 |
| connector | 8 | 4 |
| scribe | 11 | 8 |
| revenger | 4 | 2 |
| simplifier | 2 | 1 |
| **Total** | **95** | **75** |

The committed registry still contains **95 member declarations**, but only **75 non-null agentId allocations**. Its allocated role mix matches the 75-seat validation. Counting all registry members as spawned would incorrectly restore the refused/dropped population. `build/record.stdout:453–475,525–571` provides concrete null-ID examples.

The 20 null-ID/dropped names, matching the explicit DROP set in `make_spec.py:272–279`, are:

`ScoutPySignal`, `ScoutAutomakeExitCodes`, `ScoutLlamaApiKeyPublic`, `ScoutPortsSafety`, `RevLowestAxis`, `RevReportContract`, `RevOperatorLessons`, `RevExitTables`, `CritTrendPreview`, `CritScopeCreep`, `ConnectMori`, `ConnectSouji`, `ConnectKengaku`, `ConnectRevengerLane`, `ScribeLessonSkeleton`, `ScribeLogEntry`, `ScribeScorecardRound18`, `RevengerZeroObsDecision`, `RevengerK6Exit`, `SimplifyC1Plan`.

Their preserved prompts do not prove that L1 executed their work. The phrase “L1-held/low-yield” explains routing, not completion.

### W3 — capacity checks: preserve the raw total and prose discrepancy

Evidence: `attempts.json:10–169`; `make_spec.py:269–271`; `corpus/lessons/round-18.md:107–110`.

The retained attempts array contains **32**, not 30, entries with `kind == "capacity_check"`:

- First: `2026-10-20T19:57:07.801925+00:00`, `running_jobs: 129`.
- Last: `2026-10-20T20:59:22.366004+00:00`, `running_jobs: 25`, immediately before the successful dispatch record.
- Minimum **15**, maximum **153**; **zero** recorded checks reach `<=5`.
- The first 30 end at `20:54:25.958437+00:00` with 65 running jobs.
- Two additional records are `20:56:26.046434+00:00` with 37 and `20:59:22.366004+00:00` with 25.
- Full ordered values: `129,110,80,139,121,103,74,54,38,37,42,35,27,20,18,15,107,98,80,74,74,146,132,118,97,78,153,136,101,65,37,25`.

Conflicting/count-sensitive text preserved verbatim for the canonical Rust judge:

> “Thirty capacity checks never reached ≤5 running jobs.” — `corpus/lessons/round-18.md:108`

> `# 30 gated capacity checks (16:58-17:56) never saw <=5 running jobs (min 15), so the` — `build/make_spec.py:270`

The first thirty do satisfy the stated minimum/threshold observation, but the complete retained ledger has thirty-two. No explanation for the count difference is asserted. Recommended evidence-draft wording: **“32 capacity snapshots are retained, none at or below five running jobs (minimum 15); the earlier lesson/generator text says thirty.”** Do not silently rewrite the retained prose or describe the dispatch as satisfying the <=5 condition: its last snapshot is 25.

Capacity counts are observations of a shared job population, not this wave's executing-seat count. The configured wave ceiling 100 and `globalRunnerCeiling: 1056` in `dispatch-95.json.policy` are policy fields, not proof of available capacity or a diagnosis of the runtime refusal.

### W4 — terminal evidence is bounded by its source

Evidence: `completion-summary.json:5–14`; `spawn-result.json:5–25`, JSON paths `.result.details.results`, `.result.details.progress`, `.result.details.async`.

Conflicting evidence levels preserved verbatim:

> `"completed": 75,` and `"dead": [],` — completion summary, lines 6–7.

> `"results": [],` and `"status": "pending",` — raw spawn snapshot, lines 7 and 16; all 75 progress entries have status `pending`.

The raw envelope's async state is `running`, not a terminal capture. This is a timing/evidence distinction, not proof that the eventual 75-completed summary is false. Safe draft: **“75 dispatched; completion summary records 75 completed, no dead seats, and 75 conformant report files. The retained raw spawn response is the initial pending snapshot, not independent terminal-status evidence.”**

The summary's report counts include `nonconformant: 0`, `missing: []`, `unexpected: []`, `unreadable: []`. Its recorded counter command is retained metadata; it was not rerun by this seat. Report verdicts, including 45 confirms, are advice classifications, not gate outcomes or automatic admission.

### W5 — planner and connector mapping; no actual-model attribution

Evidence: `build/make_spec.py:19–20,228–240`; `completion-summary.json:9,14`; `assignments.json:62–65`; no `agent == "planner"` task appears in either committed dispatch.

- Planner mapping is the declared **“L1-held frozen topology seat”**. L1 is not a seventy-sixth spawned build worker and not an independently observed outside judge.
- `ConnectKagi` → `KamaR18.ConnectKagi-2`: declared kagi overlap scan on argv credentials/exact argv.
- `ConnectKumitate` → `KamaR18.ConnectKumitate-2`: declared kumitate wave-provenance/tooling ownership handoff scan.
- `ConnectTameshi` → `KamaR18.ConnectTameshi-2`: declared tameshi mutation/fault-control/equivalent-mutant doctrine scan.
- `ConnectTsukuroi` → `KamaR18.ConnectTsukuroi-2`: declared tsukuroi host/llama-server/pacman-pause/stress-tooling scan.

These are retained assignment mappings, not this report's verification of each scan's execution or result. The four other initial connector declarations have null allocations after the refit.

The summary says exactly:

> not recorded; role routing is host-owned; claims rest on executable artifacts, not a model label

Raw `modelRole` fields and generator role comments do not identify an actual answering model. **No actual answering model is inferred.**

## Gates and provenance bindings

- Both build validator receipts record exit **0**; they were read, not executed anew.
- Policy pin in both validation receipts: `70418a0f0b89288b6b481d682fb91a884de18001ecf87d06469955ffa64f59f9`.
- Initial recorded spec digest: `ce07c5407e449cc9ae430379600c4320ab7cffc48277587228428c4cdd544a05`; initial recorded canonical taskCall digest: `fe887fc466de6d74f2f934a9856b784f41240a7e639d5d379e4eb9936a446125`.
- Refit recorded spec digest: `33243724a8b94dfa001720976062f353435cdb844e5025e1cacd3b38b5b7b51e`, also observed directly from committed `spec.json` bytes; recorded canonical taskCall digest: `7390f6cbfa63a4f56ccefb53a759d42ce518ee695b7bcb12bf8cb93b5b6ab28d`.
- Canonical taskCall digests and the external policy bytes were **not independently recomputed/reopened** by this scribe. Recorded canonicalization is `json sort_keys, separators (',',':'), ensure_ascii=False, utf-8`.
- Official retained runs identify measured production revision `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`, not the report target tip. `runs/commands.json` records `provenance-selftest` exit 0 and stdout SHA-256 `99118cedaefe49a02646c0f1b0d6b41ddb53a3c15c23b9ef21367ea0a7a17a9a`; retained stdout ends `selftest: 30/30 checks passed`. This is an earlier executable parser-selftest observation, **not** a fresh dispatch or terminal-status proof.
- The same official command metadata records `c1-measure` and `c2-survivors` exit **2**, expected **0**, `as_expected: false`. Those are preserved official could-not-evaluate results, not green gates inferred from worker completion. Their product diagnosis and later reruns belong to other assigned seats.
- This seat executed **no tests, builds, formatters, official counting commands, mutants, or gate/runtime experiments**. There is no new pristine/mutant/restoration sequence and no fresh-mutant denominator.

## Commands, query evidence, and outcomes

Executed shell command, exit 0, empty stdout/stderr:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-ReportWaves && git -C /tmp/kama-r18-falsify-ReportWaves switch -q -c seat/ReportWaves 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
```

Two `sha256sum` invocations exited 0, no stderr, with ordered absolute-path arguments listed below. Each prefix is `/tmp/kama-r18-falsify-ReportWaves/`; these suffix lists specify the exact argv paths without abbreviating the underlying filenames:

1. `.ufo/waves/round-18/build/attempts.json`, `.ufo/waves/round-18/build/completion-summary.json`, `.ufo/waves/round-18/build/validation-95.json`, `.ufo/waves/round-18/build/validation.json`, `.ufo/waves/round-18/build/refused-result-1.json`, `.ufo/waves/round-18/build/spawn-result.json`, `.ufo/waves/round-18/build/dispatch-95.json`, `.ufo/waves/round-18/build/dispatch.json`, `.ufo/waves/round-18/build/assignments.json`, `.ufo/waves/round-18/build/advice/swarm-registry.json`, `.ufo/waves/round-18/build/make_spec.py`, `corpus/lessons/round-18.md`, `.ufo/waves/round-18/runs/commands.json`.
2. `.ufo/waves/round-18/build/spec.json`, `.ufo/waves/round-18/build/record.stdout`, `SCORECARD.md`, `corpus/QUALITY.md`.

Read-tool JSON queries (not Python/Node execution) included these exact expressions against the committed files:

- `attempts.json`: `{task_calls:map(select(.kind=="task_call")),capacity_count:(map(select(.kind=="capacity_check"))|length),capacity_values:map(select(.kind=="capacity_check")|.running_jobs),capacity_min:(map(select(.kind=="capacity_check")|.running_jobs)|min),capacity_max:(map(select(.kind=="capacity_check")|.running_jobs)|max)}` → **32**, minimum **15**, maximum **153**, two task calls.
- `refused-result-1.json`: `{literal_refusal_count:((.text|split("Background job limit reached (100)"))|length)-1,label_count:(.text|split("; ")|length),distinct_message_suffixes:(.text|split("; ")|map(split(": ")|last)|unique)}` → **95**, **95**, exact suffix quoted above.
- `refused-result-1.json`: `{distinct_labels:(.text|sub("^Failed to start background task jobs: ";"")|split("; ")|map(split(": ")[0])|unique|length)}` → **95**.
- `swarm-registry.json`: `{allocated_count:([.members[]|select(.agentId!=null)]|length),unallocated:[.members|to_entries[]|select(.value.agentId==null)|.key],allocated_roles:([.members[]|select(.agentId!=null)]|group_by(.role)|map({role:.[0].role,count:length}))}` → **75** allocated, **20** null-ID names, role mix above.
- Spawn progress grouping `.result.details.progress|group_by(.status)|map({status:.[0].status,count:length})` → one group, `pending`, **75**. The initial attempted envelope query failed on an incorrect nested-results assumption; the actual envelope keys were then read and the correct progress array queried. That read-query failure is not a product failure.

No experiment source was created; the exact counting expressions above are the reporting derivations.

`ss -H -ltnp` exited 0 with no stderr. It showed no listener on 8080/34113. This seat launched no server or other persistent process, created no listening socket, and therefore had no seat-owned listener/process group to tear down. Existing host listeners were observed only, not contacted or modified; the snapshot is not a global health or ownership audit.

Cleanup command, exit 0, empty stdout/stderr:

```sh
rm -rf /tmp/kama-r18-falsify-ReportWaves && test ! -e /tmp/kama-r18-falsify-ReportWaves
```

## Committed artifact digest manifest

SHA-256 values observed with the two commands above:

| Artifact | SHA-256 |
|---|---|
| `.ufo/waves/round-18/build/attempts.json` | `a0dc17a89dd43e297f9977dc48c5c60cbdd640db68f80abe6ebeb95999414ae9` |
| `.ufo/waves/round-18/build/completion-summary.json` | `e52505d66a4d307e2c76dd6a3f0cbe642e73f89ec740c4b1aba967214ae07b0d` |
| `.ufo/waves/round-18/build/validation-95.json` | `f2028478282a301d427438568fe24442ac3e4129d6cb4f36a261426270a5df73` |
| `.ufo/waves/round-18/build/validation.json` | `54114a162187fe70fd3b432535f697dae4ea2aa8c975fe9dbfaf68e0b47b4a48` |
| `.ufo/waves/round-18/build/refused-result-1.json` | `83533c134a04ddab64771a02e3b7e41ab2fc89740dbc57ff219609e6e664d6cf` |
| `.ufo/waves/round-18/build/spawn-result.json` | `cb0e2b10223606ffaf1f4287a6304a0b320c8d361b3b1af202d2ceffc48f4898` |
| `.ufo/waves/round-18/build/dispatch-95.json` | `59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744` |
| `.ufo/waves/round-18/build/dispatch.json` | `470ae3ad6fd13e6142cf45143a34c9d99581ea339c606aa23756513c857434e4` |
| `.ufo/waves/round-18/build/assignments.json` | `0a49c657eeef55ba2c3add803957e7cc29e9cbaa4fffa42fd5d7879d3760bb9a` |
| `.ufo/waves/round-18/build/advice/swarm-registry.json` | `a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0` |
| `.ufo/waves/round-18/build/make_spec.py` | `d148592ceebba1c7488ef2d100c05ce4cdbe532a7734651530d069139977c19a` |
| `corpus/lessons/round-18.md` | `13142d960465790f4955e4e1698ae4a66dccf4a897049ad04bf97faa69e1f253` |
| `.ufo/waves/round-18/runs/commands.json` | `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a` |
| `.ufo/waves/round-18/build/spec.json` | `33243724a8b94dfa001720976062f353435cdb844e5025e1cacd3b38b5b7b51e` |
| `.ufo/waves/round-18/build/record.stdout` | `df40fd5c904fb5700d04e863827c50788e09c5d31f60e18fe72ced464c25a22a` |
| `SCORECARD.md` | `665b1fd8e8b01895f7c3d18990f01d8e53c4130478a54adac8d62821e43b0055` |
| `corpus/QUALITY.md` | `8eb5e414398f31b895d5fc806fb0dc67af537b9f6fb6a309a5225d243e972955` |

## Touched surfaces, limits, and handoff

- Permanent write: **only** `.ufo/waves/round-18/falsify/advice/ReportWaves.md`.
- Temporary write: the isolated scratch clone, removed before writing this report. No product code, source evidence, fleet state, index, jj state, sibling repo, or frozen artifact was edited. No commit/push/publish/deploy occurred.
- Installs/updates: **none**. No package transaction, host-service action, environment dump, private session-store read, or credentials read.
- Out of scope: independent terminal-status reconstruction; actual answering-model identification; current uncommitted falsify-wave census; checking each connector scan's execution; product claim admission; new runtime experiments; repairing the prose/registry; and rerunning official gates/counters merely to decorate this report.
- Remaining limits are explicit: 75 completed/no-dead is summary-recorded, not raw-terminal-verified; the <=5 capacity condition is never observed; 95 registry declarations must not be counted as 95 executions; canonical taskCall hashes and unchanged-dispatch wording remain retained provenance assertions rather than an independently reconstructed API-call transcript.
- L1 may use the bounded wording above. The canonical Rust judge, not this advice, resolves the preserved count/evidence-level conflicts.

Report: .ufo/waves/round-18/falsify/advice/ReportWaves.md
