VERDICT: confirm — every assigned build-provenance number reproduces byte-exactly (95 refusals/0 spawned, 75 refit, policy sha 70418a0f, band 64–100, taskCall 7390f6cb, 75 unique assignments, 75/75 reports); two artifact-description caveats below, neither a fabricated number.

# Scope

Read-only verification of the round-18 **build** dispatch provenance at lane master
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (clone `/tmp/kama-r18-falsify-WaveProvenance`,
branch `seat/WaveProvenance`). No production file edited; no jj/git writes; no experiment
assigned by the item, so all results below are independent Python re-computation over the
committed bytes, not reruns of the lane's validators/counters. LSP is unavailable in the
mounted tool inventory, so code claims are static reads with path:line, not semantic LSP proof.

Artifact digests used (sha256):

| artifact | sha256 |
|---|---|
| `build/spec.json` (raw) | `33243724a8b94dfa001720976062f353435cdb844e5025e1cacd3b38b5b7b51e` |
| `build/dispatch.json` (raw) | `470ae3ad6fd13e6142cf45143a34c9d99581ea339c606aa23756513c857434e4` |
| `build/dispatch-95.json` (raw) | `59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744` |
| `build/validation.json` | `54114a162187fe70fd3b432535f697dae4ea2aa8c975fe9dbfaf68e0b47b4a48` |
| `build/validation-95.json` | `f2028478282a301d427438568fe24442ac3e4129d6cb4f36a261426270a5df73` |
| `build/refused-result-1.json` | `83533c134a04ddab64771a02e3b7e41ab2fc89740dbc57ff219609e6e664d6cf` |
| `build/spawn-result.json` | `cb0e2b10223606ffaf1f4287a6304a0b320c8d361b3b1af202d2ceffc48f4898` |
| `build/assignments.json` | `0a49c657eeef55ba2c3add803957e7cc29e9cbaa4fffa42fd5d7879d3760bb9a` |
| `build/completion-summary.json` | `e52505d66a4d307e2c76dd6a3f0cbe642e73f89ec740c4b1aba967214ae07b0d` |
| `build/advice/swarm-registry.json` | `a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0` |
| `build/attempts.json` | `a0dc17a89dd43e297f9977dc48c5c60cbdd640db68f80abe6ebeb95999414ae9` |
| `build/make_spec.py` | `d148592ceebba1c7488ef2d100c05ce4cdbe532a7734651530d069139977c19a` |
| policy `scripts/hyaku/ufo-wave-policy-v2.json` | `70418a0f0b89288b6b481d682fb91a884de18001ecf87d06469955ffa64f59f9` |

# Findings

## 1. 95-seat payload was wholly refused with zero spawned — CONFIRMED

- `.ufo/waves/round-18/build/refused-result-1.json`: `text` contains **95** occurrences of
  `Background job limit reached (100)` and **95 distinct** task labels; the label sequence
  equals `dispatch-95.json`'s registry member order exactly after stripping the `KamaR18.`
  prefix (set equality True, order equality True).
- Same file: `details` keys are exactly `projectAgentsDir`, `results`, `totalDurationMs`
  — **no `progress`, no `async`** — with `"results": []` and `"totalDurationMs": 0`.
  Contrast `spawn-result.json` `details`, which carries `progress` (75 rows) and `async`.
  The refusal message itself says `Failed to start background task jobs` for every one of
  the 95 (`.ufo/waves/round-18/build/refused-result-1.json`, `text`).
- `.ufo/waves/round-18/build/attempts.json:3-11`: `{"kind":"task_call","result":"refused",
  "refused":95,"spawned":0,"error":"Background job limit reached (100)"}` at
  `2026-10-20T19:55:45.804562+00:00`.
- The repaired provenance tool's own extractor, re-applied to the committed bytes, agrees:
  `REFUSED_TASK_RE` (`.ufo/waves/round-18/dispatch-provenance.py:178-179`) gives
  **95 hits / 95 unique**; `SPAWN_HEADER_RE` and `SPAWN_BULLET_RE` (`:175-176`) give
  header **75** and **75** bullets on `spawn-result.json`.
- The 95 `run` registry entries in `dispatch-95.json` all carry `"agentId": null`; the
  persisted registry's 20 null-AgentId rows are exactly the 20 dropped lanes (finding 3),
  so no dropped lane ever received a handle.

Zero spawned is therefore supported three ways: refusal text (95/95 failed to start),
absence of progress/async in the refusal details, and null handles for every non-assigned
member. [INFERENCE] The `-2` suffix on all 75 second-wave job ids
(`KamaR18.<name>-2`) records that the refused call reserved the unsuffixed job names; the
refusal text itself lists those unsuffixed names, and no artifact shows any of them
running.

## 2. Refit-75 payload validation: policy hash, band, spec and taskCall canonical SHA — CONFIRMED

- `build/validation.json:5-11` records policy path
  `/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json` and
  `sha256 70418a0f…`; `sha256sum` of that file is exactly `70418a0f…`. Band from
  `sighting.dispatch.swarm`: `minLanes 16`, `waveMinLanes 64`, `waveMaxLanes 100`,
  `maxLanes 100`; `75 ∈ [64,100]` and `95 ∈ [64,100]`, both below the `hardCeiling 100`
  recorded in `dispatch.json`'s policy block. The policy note itself states
  "band 64-100 because the validator hard-caps any wave".
- `build/validation.json:9` `spec_sha256 33243724…` equals the **raw** sha256 of
  `build/spec.json` (`sha256sum`). This matches the tool's Mode-1 semantics:
  `spec_sha256 = sha256_bytes(fh.read())` on the spec file bytes
  (`.ufo/waves/round-18/dispatch-provenance.py:623`), while `taskCall_sha256` uses the
  canonical JSON below. The record's `canonicalization` field applies to the taskCall.
- `build/validation.json:10` `taskCall_sha256 7390f6cb…` reproduces exactly from
  `dispatch.json`'s `taskCall` with
  `json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')`.
  The same computation reproduces `validation-95.json:10` `fe887fc4…` from
  `dispatch-95.json`.
- `build/validation-95.json:9` `spec_sha256 ce07c540…` is likewise reproducible even
  though no `spec-95.json` is committed: rebuilding
  `{context, reportDir: ".ufo/waves/round-18/build/advice", maxLanes: 100,
  items:[{name, role, prompt}]}` from `dispatch-95.json`'s 95 tasks (prompt = task text cut
  at the validator's `\n\nLane bounds: ` trailer), then
  `json.dumps(indent=1, ensure_ascii=False) + "\n"`, yields **ce07c540… exactly**. The same
  method round-trips the 75 prompts from `spec.json` 75/75.
- `dispatch.json`: `counts {spawn:75, resume:0, total:75}`, 75 tasks, 75 unique names,
  `context` == `spec.context`; role counts equal `validation.json`'s `roles`
  (executor 13, mutation-tester 4, sentinel 2, scout 19, reviewer 16, critic 6, connector 4,
  scribe 8, revenger 2, simplifier 1). The 95 side is equally consistent
  (95 tasks, roles sum 95 == `validation-95.json` roles).
- The committed taskCall is the validator's literal output: the `Lane bounds:` and
  `Report: write your scoped findings to …` lines are emitted by
  `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs:209` and `:725-726`, and all
  75 sent task strings in `spawn-result.json`'s `details.progress` contain the corresponding
  `dispatch.json` task **byte-exactly** (0 mismatches), wrapped only by the host's constant
  `Complete assignment thoroughly:\n\n` prefix and the operator tooling-directive suffix
  (1 distinct head, 1 distinct tail across 75). So "one unchanged validator taskCall" holds
  at the lane/host boundary; no raw request capture of the literal JSON exists (limitation).

## 3. Registry/75 assignments — CONFIRMED, with a row-count caveat

- `build/assignments.json`: 75 unique keys == the 75 `dispatch.json` registry member names
  == the 75 `spec.json` item names (set equality both ways). All 75 values are unique,
  `KamaR18.`-prefixed and `-2`-suffixed; 0 duplicate targets.
- `build/advice/swarm-registry.json` (persisted by the `run` + `record` pair): **0 mismatches**
  between its `agentId` values and `assignments.json`; every assigned member has a handle.
- **Caveat (reported, not a kill):** the persisted registry has **95 members**, not 75 —
  75 assigned + **20 with `agentId: null`**, and those 20 are *exactly* the dropped names
  (set equality). This is the validator's documented merge-over-existing-registry behavior,
  and the 20 nulls are the honest never-spawned record, but "registry75" must be read as
  "75 assigned handles among 95 merged rows". The role mix computed over the **assigned**
  members reproduces `completion-summary.json`'s `role_mix` exactly; a naive count of
  registry rows overcounts by 20.

## 4. Terminal/dead counts — CONFIRMED

- `build/advice/` holds 75 `.md` reports plus `swarm-registry.json`; the 75 `.md` names equal
  the 75 spec names (missing [], unexpected []).
- Applying round-17's exact classifier regex
  (`.ufo/waves/round-17/count-verdicts.py:59`, `^VERDICT:[ \t]+(confirm|partial|refute|n/a)…$`
  to the first non-empty line) gives **confirm 45, partial 26, refute 0, n/a 4,
  nonconformant 0** — identical to `completion-summary.json` `reports`
  (`files 75, confirm 45, partial 26, refute 0, n/a 4, nonconformant 0, missing [],
  unexpected [], unreadable []`). Smallest report is 3,100 B (no placeholder reports).
- `completion-summary.json` `spawned: 75`, `completed: 75`, `dead: []`; spawn evidence
  agrees (`spawn-result.json` header 75, 75 member bullets, 75 `progress` rows) and the
  assigned-member count is 75. No seat lacks a report.
- `attempts.json` holds 34 records: 1 refused task_call + 1 spawned task_call + 32 capacity
  checks (30 inside the declared 19:58–20:56Z gate window, 1 at 19:57 before it, 1 at
  20:59:22 simultaneous with the spawn); every record is classified, none unexplained.

## 5. No missing refused attempts — CONFIRMED

- Only one refusal record exists in the round-18 build tree:
  `build/refused-result-1.json` (95 messages). Every other `Background job limit` occurrence
  is prose in advice reports or the tool/spec source, not a second event.
- `attempts.json` contains exactly two `task_call` entries: the 95/0 refusal
  (`19:55:45.804Z`) and the 75 spawn (`20:59:22.366Z`, `refused: 0`). The capacity series
  has 32 observations; the 30 in the declared gate window `19:58–20:56Z` have
  **min 15 / max 153** running jobs and never ≤5, matching
  `build/make_spec.py:269-271` ("30 gated capacity checks (16:58-17:56) … min 15").
  The arithmetic is coherent: a 95 wave needs `100−95 = 5` free slots (never reached), while
  the 75 refit needs `100−75 = 25`; the final check records exactly **25** running at
  `20:59:22.36`, immediately before the spawn, and the spawn returned `refused: 0`.
- The 20 dropped prompts are fully retained in `dispatch-95.json`
  (min task length 1,041 chars) and are exactly `make_spec.py`'s `DROP` set (20 names,
  `:272-281`), matching the lesson's "remain in dispatch-95.json / L1-held or low-yield".
  No prompt exists in the 75 that is absent from the 95.

## 6. No fabricated answering model — CONFIRMED (with an inaccurate "not recorded" statement)

- No artifact claims a concrete answering model. `completion-summary.json:14` says
  `"actual_answering_model": "not recorded; role routing is host-owned; claims rest on
  executable artifacts, not a model label"`, and the lesson disclaims model quality.
- **Caveat/defect (artifact description, not fabrication):** the statement "not recorded" is
  contradicted by the committed spawn result: every one of the 75 `progress` rows in
  `spawn-result.json` carries a `modelRole`, and the mapping is exactly the planned per-role
  alias from `make_spec.py`'s section comments:
  executor/sentinel `m_luna` (15), mutation-tester `m_sol` (4), scout/simplifier `m_flash`
  (20), reviewer/revenger `m_zfl` (18), critic `m_swe` (6), connector `m_grok` (4),
  scribe `m_haiku` (8). The concrete alias→model resolution is indeed host-owned and not in
  the artifact. Correct wording: *model role alias recorded per seat; concrete model not
  recorded.* No invented model label appears anywhere.

## 7. Provenance-tool and record-shape notes (limits, not claim failures)

- The official selftest evidence is committed and matches the lesson's M5 claim:
  `runs/provenance-selftest.stdout` ends `selftest: 30/30 checks passed`,
  `runs/provenance-selftest.exit` = `exit=0`, and `runs/commands.json` records the exact
  argv plus `measured_commit: c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (tip `1c325b2`
  retains the evidence commit).
- There is **no `dispatch-provenance-ledger-v2`** for the build wave, and
  `build/validation.json` is not in the tool's Mode-3 schema
  (`{argv,cwd,env_bindings,exit,stdout_sha256,taskCall_sha256,canonicalization,counts,
  policy{path,sha256,version,band},recorded_at}`). It is an L1-recorded file
  (`validator/exit/policy/spec_sha256/taskCall_sha256/canonicalization/counts/roles/note`).
  Nothing in the lesson claims tool emission, so this is a limitation of the record, not a
  contradiction; a later verification that wants tool-emitted provenance would need the
  ledger that does not exist.
- Stale in-tree citation: `build/advice/RevengerRefusedZero.md:42` cites
  `build/validation.json:18` with `taskCall_sha256 70e994a0…`; the committed file's line 18
  is `"executor": 13` and its taskCall hash is `7390f6cb…`. The interim file with
  `70e994a0…` is not retained anywhere in round-18 (grep: no match). This is a point-in-time
  build report superseded by the 20:59 refit validation; the final lesson must not quote that
  line as current.

# Limitations

- No experiment was assigned; I did not execute `ufo-swarm-wave.mjs`, `dispatch-provenance.py`
  (including `--selftest`), `c1/measure.py`, `c2/survivors.py`, or any official counter.
  All numbers are independent recomputation over committed bytes, plus the committed run
  outputs read as data.
- The 95 spec source file is not committed; its claimed digest is verified by exact
  reconstruction (method in finding 2), not by hashing a retained `spec-95.json`.
- The sent taskCall's identity rests on the spawn result's per-seat task/agent text and the
  validator emitter lines; no raw request-body capture is committed.
- Capacity observations are L1-recorded timestamps; no independent job-table snapshot from
  19:55/20:59 is available.
- LSP is unavailable in the mounted tool inventory; static reads only.

# Installs

None. No tools installed or upgraded.

# Cleanup

`/tmp/kama-r18-falsify-WaveProvenance` removed after this report. No listener was started
by this seat; `pgrep -af kama-r18-falsify-WaveProvenance` → nothing, and `ss -ltnp` contains
no seat-owned socket.
