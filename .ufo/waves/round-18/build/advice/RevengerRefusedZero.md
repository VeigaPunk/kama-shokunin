VERDICT: confirm — refused: 0 reproduces: the 82 refusals exist only as prose in `result.text`, and the refused tally (dispatch-provenance.py:365-384) reads no prose.

# Reconstruction: how dispatch-provenance.py recorded the refused attempt as `refused: 0`

## 1. The invocation

Reconstructed from the ledger entry, whose fields are the tool's own argv echo (`build_attempt_entry` stores `label`, `os.path.abspath(path)`, policy; `.ufo/waves/round-17/dispatch-provenance.py:489-509`), plus the Mode-2 contract (`dispatch-provenance.py:61-64`, quote: `dispatch-provenance.py --attempt-result PATH --label refused|spawned --out LEDGER.json`):

```
dispatch-provenance.py \
  --attempt-result /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/refused-result-1.json \
  --label refused \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/provenance-ledger.json
```

Evidence, all in `.ufo/waves/round-17/build/provenance-ledger.json`:
- :6 `"label": "refused"`; :8 `"attempt_result": ".../round-17/build/refused-result-1.json"`; out-path = the ledger itself (`cmd_attempt` appends and `write_ledger(args.out, ...)`, `dispatch-provenance.py:677-681`).
- :7 `"at": "2026-10-20T15:36:40.628649Z"` — record time (entry `at` = `utc_now()` at append, `dispatch-provenance.py:494`). A second Mode-2 call, `--label spawned` on `spawn-result.json`, followed 40 ms later (ledger :33-36, `"at": "2026-10-20T15:36:40.668223Z"`).
- :10-22 policy block read at record time from `POLICY_PATH = ENV_BINDINGS["UFO_CONFIG_PATH"]` (`dispatch-provenance.py:148`, `:141-143`), not from argv.
- :29-30 `bound_task_call_sha256`/`bound_run_index` null for BOTH entries → the ledger contained no `wave_run` entry at either append (`last_wave_run` returned None, `dispatch-provenance.py:349-354`); `load_ledger` seeded a fresh v2 skeleton. The committed ledger holds exactly these two attempt entries.
- Tool exit 0 regardless of counts (`dispatch-provenance.py:689`, quote: `sys.exit(0)`).
[INFERENCE] Only the interpreter spelling (`python3` vs absolute path) and cwd are unpinned; every recorded field matches this one argv shape.

## 2. The input it parsed

`refused-result-1.json` — 9427 bytes, sha256 `71679919…041a5c` (ledger :9-10), the raw OMP taskCall refusal result. Shape (`.ufo/waves/round-17/build/refused-result-1.json:2-10`): `{at, result: {text, details: {projectAgentsDir: null, results: [], totalDurationMs: 0}}}`. The 82 refusals exist ONLY as repeated prose in `result.text` (:4, quote: "Failed to start background task jobs: KamaR17.C1HarnessGrading: Background job limit reached (100)."); verified by count: 82 occurrences of "Background job limit reached", 82 unique `KamaR17.*` ids, and `details.results` is an empty list (:8, quote: `"results": []`). Its inner `"at": "2026-10-20T15:03:50.107692+00:00"` (:2) is byte-identical to `build/attempts.json:3` — the same single refused task_call event.

## 3. The precise failing lines (dispatch-provenance.py)

1. `:381-384 extract_counts` — the ONLY refused counter: `counts = {"refused": 0, "spawned": 0}` (:382) seeded, tallied, returned. Nothing else writes `refused`.
2. `:365-378 tally_counts` — refused grows only via (a) a dict key literally `"refused"`/`"spawned"` holding a non-bool int (:368-370, quote: `if key in ("refused", "spawned") and isinstance(value, int)`) or (b) a `"status"`/`"state"` string exactly `"refused"`/`"spawned"` (:371-373). Every other node — including every string value — is merely recursed (:374-375, quote: `else: tally_counts(value, counts)`). String contents are never scanned on the refused path. `refused-result-1.json` contains neither shape, so `extract_counts` returns `{"refused": 0, "spawned": 0}`.
3. `:476-477 parse_attempt_result` wires that tally as refused's sole source (`tally = extract_counts(result_json) if parseable else {"refused": None, "spawned": None}`) while :478-479 additionally hands spawned to text-based evidence.
4. The asymmetry is deliberate, not an accident: the section comment `:360-364` states (quote: "`refused` keeps the round-16 legacy tally"). Round-17's defect-1c fix repaired `spawned` only: `_iter_texts` (:387-388, quote: "Yield every string value stored under a 'text' key.") reaches `result.text`, but its output feeds `spawned_observations` (:416-419) alone — header regex `SPAWN_HEADER_RE = re.compile(r"Spawned (\d+) background agents")` (:166) matched at :426-428.
5. `:506 build_attempt_entry` persists the zero verbatim (`"refused": detail["refused"]` → ledger :24 `"refused": 0` next to :11 `"parseable": true`), and `cmd_attempt` exits 0 (:689) — a refusal counted as zero is recorded as a clean, successful observation with no signal.

## 4. Why attempts.json says 82 while the ledger says 0

Different artifact, different counter, same event. `build/attempts.json:4-8` records the 15:03:50 task_call as (quotes: `"result": "refused"`, `"refused": 82`, `"error": "Background job limit reached (100)"`) — its writer counted the prose refusals (count factually verified above: 82 messages / 82 unique ids; the writer's identity is not in-repo [INFERENCE]). Note the tally would also have found 82 had the tool been pointed at attempts.json (:368-370 matches the int key at attempts.json:6; the `"result": "refused"` string at attempts.json:5 would NOT tally — `"result"` is not `"status"`/`"state"`). The decisive miss is the input choice — the raw OMP payload whose only count carrier is prose — combined with a refused extractor that reads no prose. Contrast: the sibling `spawned` label on the same ledger worked (ledger :52-53, quotes: `"spawned": 82`, `"spawned_method": "omp_text_spawned_header"`) precisely because a text extractor exists for it — proof the same approach is feasible for refused.

## 5. Side observation for the fix wave

The committed ledger has NO `wave_run` entry, yet `build/validation.json:18` records `"taskCall_sha256": "70e994a0…8fb4f"` with a policy block; `cmd_emit_validation` (:692-695) refuses a ledger without one (stderr: "no wave_run entry", exit EX_USAGE). So that validation.json cannot have been emitted from the committed ledger file [INFERENCE: produced by a separate `--run` invocation whose `--out` ledger was not committed]. C2's refused-symmetry fix and its controls should not depend on that uncommitted-run gap.

## 6. Contract guidance for the C2 fix (advice, not verdict)

Add a text-based refused extractor symmetric to `spawned_observations` (method-tagged, e.g. count of `<id>: Background job limit reached` with unique-id discipline like `SPAWN_BULLET_RE` at :167/:429), keep the unparseable→`null` semantics (:476-477), keep integer-key tally precedence, and add a retained control whose fixture is refused-prose-only so a mutant dropping the extractor fails a control — mirroring how the spawned fix is guarded.

## Limitations

- Read-only seat; no rerun of the tool (lane gates/measure scripts are L1's). The count claims (82/82/empty results) are direct counts over the committed artifact; the `refused: 0` verdict is corroborated by the committed ledger and by round-17's independent rerun (`falsify/advice/ProvenanceRerun.md`, quote: "again appended `parseable: true, refused: 0` (exit 0)").
- attempts.json's writer and the interpreter spelling of the invocation are [INFERENCE] as noted.
- No `lsp` device was used; plain file reads sufficed for this static reconstruction.

## Installs

None.
