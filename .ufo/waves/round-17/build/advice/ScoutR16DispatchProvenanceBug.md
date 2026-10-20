VERDICT: n/a — diagnostic question; mechanism reproduced: no key or status value in the real payload can satisfy either counting rule, so 79 spawns record as `spawned: 0`.

## Short answer

`tally_counts` (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/dispatch-provenance.py:162-175`) recognises exactly two shapes: a dict key literally `refused`/`spawned` carrying an int, or a `status`/`state` string equal to `refused`/`spawned`. The real task result contains **neither**: zero `spawned`/`refused` keys exist anywhere in the file (`grep -c '"spawned"'` = 0, `grep -c '"refused"'` = 0), the 79 per-seat rows carry `status: "pending"` only, and the number 79 appears solely as prose inside `result.text`. `extract_counts` seeds both tallies at 0 (`:179`) and returns them unconditionally, so a parseable-but-unmatched payload becomes a confident zero at `:314-315`. Replaying `tally_counts` verbatim over the file yields `{'refused': 0, 'spawned': 0}` with **zero rule hits**, while `len(result.details.progress) == 79`.

## 1. What the receipt promised, and what it graded

- `dispatch-provenance.py:34-36` — "refused/spawned counts when the result JSON is parseable". Counts are contingent on JSON validity only, not on any rule having matched.
- `dispatch-provenance.py:157-158` — the heuristic's declared basis: "or `spawned` adds to that tally (per-member progress rows)." The progress-row branch is the one written for this payload family, and it is dead for it.
- `dispatch-provenance.py:179` — "counts = {"refused": 0, "spawned": 0}". The default is a number, not "unknown".
- `dispatch-provenance.py:299` — "counts = extract_counts(result_json)". The operator-supplied `label` is never passed to the extractor.
- `dispatch-provenance.py:308` — "label": args.label. The tool already held `spawned` as ground truth in its own argv and ignored it for counting.
- `dispatch-provenance.py:313-315` — "spawned": counts["spawned"] if counts else None. `None` only on unparseable JSON; zero hits still write `0`.

## 2. The real task result shape

File `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/spawn-result.json`: 1,361 lines, 369,263 bytes, sha256 `b0c9a495…`, which matches the ledger's recorded digest (`provenance-ledger.json:55` "b0c9a495078dd6888c0755950ca9478167e34a82950978e0785160b80cbf9d08").

- Line 1-3 wrapper: `{`, `"at": "2026-10-20T13:53:14.911901+00:00"`, `"result": {` — a timestamped envelope around the harness task result.
- Line 4 `"text": "Spawned 79 background agents using reviewer, executor, mutation-tester, critic, sentinel, scout, connector, revenger, scribe, simplifier."` — a single 5,792-character JSON string; the number 79 lives here as prose.
- Line 7 `"results": []` — no completed seat results at receipt time; nothing per-seat to tally.
- Line 8 `"totalDurationMs": 2` — the only int directly under `details` (row counters are all 0), and its key is not `spawned`.
- Line 9 `"progress": [` — an array of 79 rows, each with keys `index, id, agent, agentSource, modelRole, status, task, assignment, recentTools, recentOutput, toolCount, requests, tokens, cost, durationMs`.
- Line 16 `"status": "pending"` — first of 79 identical values (`grep -c` = 79; last at line 1342). `recentTools: []`, `toolCount: 0`, `durationMs: 0` in every row.
- Lines 1354-1358 `"async": { "state": "running", "jobId": "KamaR16.RerunMatrixFrozen", "type": "task" }` — the call returned while the wave was still running.
- Bulk: `task` echoes each full 2,282-char assignment; 161,621 characters across 79 rows out of 369,263 total. The file is dominated by prompt copies, not counts.

**First 2 KB:** the head is entirely the `text` string; byte 2,048 lands mid-bullet (`…- \`Kam`). `"details"` does not begin until byte 5,947, and `"progress"` until byte 6,035 (`"async"` at byte 369,154). Anyone sizing the extractor from the first 2 KB sees only prose and would still have to guess the machine shape.

## 3. The traversal, rule by rule

| Node (file:line) | Value | Rule at `:165-170` | Contribution |
|---|---|---|---|
| `result.text` (`:4`) | 5,792-char string | no string pass exists | 0 |
| `result.details.results` (`:7`) | `[]` | empty list | 0 |
| `result.details.totalDurationMs` (`:8`) | `2` | key not `refused`/`spawned`, so `else` recurses into an int | 0 |
| `result.details.progress[0..78].status` (`:16`-`:1342`) | `"pending"` | `:168-169` requires exactly `"refused"`/`"spawned"`; `else` recurses into a string | 0 |
| `result.details.async.state` (`:1355`) | `"running"` | same `:168-169` test, same miss | 0 |

`tally_counts` line references: int-key branch `:165-167` — "if key in ("refused", "spawned") and isinstance(value, int)"; string-status branch `:168-170` — "elif key in ("status", "state") and isinstance(value, str)" with "value in ("refused", "spawned")"; recursion fallback `:171-172`.

## 4. Why this is systematic, not one unlucky payload

Census of every committed spawn result in the lane (runs 12-17): `.ufo/waves/round-12/…` 32 rows pending, round-13 32, round-14 32, round-15/falsify 32, round-16/build 81, round-16/falsify 79, round-17/build 82 — **all rows `pending`, no other status observed**. [INFERENCE] Completion statuses are the roster's `running`/`idle`/`completed`/`failed`; none is `spawned`, so the `:168-170` branch cannot fire for any async dispatch receipt, not just this one. Round-11's payload is a different hand-written shape (`spawn_count`, `returned_job_ids`), which `tally_counts` would also miss.

## 5. The ledger contradicts itself, with the binding proving it

- `provenance-ledger.json:14-15` — ""spawn": 79," and ""total": 79" on the `wave_run` entry, copied verbatim from the wave stdout (`dispatch-provenance.py:237` — ""dispatch": payload.get("counts")"), whose source `.ufo/waves/round-16/falsify/dispatch.json:16-19` reads `"counts": {`, `"spawn": 79,`, `"resume": 0,`, `"total": 79`.
- `provenance-ledger.json:18` — ""tasks": 79" derived by `len(task_call["tasks"])`.
- `provenance-ledger.json:49` — ""bound_task_call_sha256": "72e81bc6…"" ties the attempt to that exact taskCall.
- `provenance-ledger.json:51` — ""label": "spawned"".
- `provenance-ledger.json:56` — ""spawned": 0".

Same ledger, same bound digest: 79 dispatched, 0 spawned. The `wave_run` path is correct only because it copies a machine field named `spawn`; the `attempt` path invents the key name `spawned` and then counts its absence.

## 6. The calibration consequence

Because zero is the initializer (`:179`) and `None` requires total unparseability (`:314`), `parseable: true` + `spawned: 0` is indistinguishable from a genuine "nothing spawned" receipt. `refused: 0` is equally unevidenced here — no refusal signal exists in the payload — so both counts are fabricated, one accidentally correct. A refusal payload lacking those two keys would read `refused: 0, spawned: 0` too.

## 7. What the v2 must key on (already routed)

- `.ufo/waves/round-17/build/make_spec.py:124` — "count spawned members from an OMP task tool result text/JSON where members are async and still `pending`" (and explicitly notes "(round 16 recorded spawned:0 for 79)").
- `corpus/lessons/round-16-verifier-spotcheck.md:182` — "Fix `dispatch-provenance.py` so it counts async `pending` spawns". `:53` corroborates the observed state: "the committed spawn results show `pending`".
- Minimum truthful derivation from this payload: `len(result.details.progress)` = 79 distinct `id`s across 10 agents, cross-checked against the "Spawned N background agents" head of `result.text`; `spawned` must otherwise be `null`/`unknown`, never 0.

## 8. Correction owed to the round-16 advice

- `.ufo/waves/round-16/build/advice/ProvenanceLedger.md:22` — "matches the real `build/spawn-result.json` progress-row shape, `status: "pending"|..."". That sentence names the mismatch as the match: the rows are `pending`, and the rule only accepts `spawned`.

## Limitations / remaining unknowns

- The exact `--attempt-result` CLI is not recorded; attempt entries carry no `argv` (`provenance-ledger.json:45-57`), so the flags are an [INFERENCE] from `label: "spawned"` plus the recorded digest matching `spawn-result.json`.
- [INFERENCE] `status: "pending"` is the harness's dispatch-time value; no completed-row payload exists in the lane to prove the completion vocabulary.
- No `omp` task-tool source was read; claims about its status vocabulary rest on the seven observed payloads.
- Read-only seat: nothing outside this Report was written; no server started, no binding used, no measurement or gate run.

## Installs

None.
