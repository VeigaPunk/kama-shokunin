VERDICT: confirm — registry-driven snapshot persists MODEL_LOADING across two runs: latest.tsv records it, the second run reports transitions=0, and no malformed-row-dropped note appears.

# Item attacked
Snapshot history with MODEL_LOADING: one-row TSV registry whose consumer file declares http://127.0.0.1:P (stub serving the llama.cpp loading envelope), `tools/kama-probe.sh snapshot --registry R --history /tmp/.../hist` run twice; assert latest.tsv holds MODEL_LOADING, run 2 transitions=0, no malformed-row-dropped.

# Setup (all under /tmp/kama-r16-ExecSnapshotPersistence, never lane paths)
- `loading_stub.py` — ThreadingHTTPServer on 127.0.0.1:0; every path returns HTTP 503 `Content-Type: application/json` body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (the exact b11755 envelope the gate at tools/kama-probe.sh:428-447 requires; Server header `kama-loading-stub`, no `Server: llama.cpp` claim).
- `consumer.json` — `{"llama-cpp": {"baseURL": "http://127.0.0.1:35623"}}` (port 35623 assigned by bind(0)).
- `registry.tsv` — single row: `falsify-loading` | `/tmp/.../consumer.json` | `grep:http://127\.0\.0\.1:[0-9]+` | `http://127.0.0.1:35623` | `-` | notes. Resolver kind=url, file_match=yes (resolved URL byte-identical to declared).
- `drive.py` — orchestrator: start stub, wait for port file, write consumer+registry, run probe twice, dump artifacts. Only the python3 stdlib stub ran; no llama-server started (contract: this item does not name one).

# Commands run and exit codes
- `bash /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh snapshot --registry /tmp/kama-r16-ExecSnapshotPersistence/registry.tsv --history /tmp/kama-r16-ExecSnapshotPersistence/hist` (run 1) → **exit 2** (drift, expected: MODEL_LOADING != MODEL_OK).
- Same command (run 2) → **exit 2**.
- python3 3.14.8 present → envelope gate active (HAVE_PY=1).

# Evidence
Run 1 stdout:
```
falsify-loading | /tmp/kama-r16-ExecSnapshotPersistence/consumer.json | MODEL_LOADING | llamacpp-loading | - | 35623 | yes
snapshot=20261020T135629Z prev=- rows=1 model_ok=0 drift=1 transitions=0 exit=2
```
Run 1 stderr: `<empty>` — no baseline warnings.

Run 2 stdout:
```
falsify-loading | /tmp/kama-r16-ExecSnapshotPersistence/consumer.json | MODEL_LOADING | llamacpp-loading | - | 35623 | yes
snapshot=20261020T135629Z prev=20261020T135629Z rows=1 model_ok=0 drift=1 transitions=0 exit=2
```
Run 2 stderr: `<empty>` — critically, **no** `latest.tsv: dropping malformed baseline row` warning, i.e. the MODEL_LOADING baseline row written by run 1 parsed back through the vocabulary check at tools/kama-probe.sh:938-943 (MODEL_LOADING is in the accepted case list at :939).

hist/latest.tsv (verbatim, after both runs):
```
#@snapshot_id 20261020T135629Z	# columns: id	verdict	reason	served_model	port	file_match
falsify-loading	MODEL_LOADING	llamacpp-loading	-	35623	yes
```

hist/DELTA.md (verbatim tail — the only appended line):
```
- 2026-10-20T13:56:29Z baseline recorded (1 rows); transitions begin with the next snapshot
```
No `malformed-row-dropped`, no transition lines on run 2.

Dated JSONs: `20261020T135629Z.json` (summary `{"registry_rows_evaluated": 1, "model_ok": 0, "drift": 1, "transitions": 0, "exit": 2}`, prev_snapshot `-`, row verdict `MODEL_LOADING`/`llamacpp-loading`/drift=true) and `20261020T135629Z-p66323.json` (same summary, prev_snapshot `20261020T135629Z` — predecessor link works; second file carries the `-p$$` collision suffix because both runs landed in the same UTC second, handled per tools/kama-probe.sh:1025-1028).

Design note confirmed: run 2 appends zero DELTA lines ⇒ `latest.tsv` is not rewritten (guarded by `DELTA_LINES` non-empty at :1087), so `#@snapshot_id` retains run 1's id while each dated JSON links its own predecessor — stable-state runs do not churn the baseline.

# Teardown
- Stub terminated (STUB_EXIT=-15); `pgrep -f loading_stub.py` → empty (exit 1); `ss -ltn` shows nothing on 35623; `pgrep -x llama-server` → empty (exit 1). Never touched 8080/34113.
- Lane files untouched: only this Report written inside the lane; registry/history under the lane were never referenced.
- /tmp scratch removed after writing this report: `rm -rf /tmp/kama-r16-ExecSnapshotPersistence`.

# Limitations
- Single-row registry only; multi-row ordering/mixed-verdict persistence not exercised (out of item scope).
- Both snapshots shared a wall-clock second, exercising the `-p$$` collision path rather than distinct ids — a bonus observation, not a gap.
- [INFERENCE] The stub's envelope matches byte-for-byte the shape body_is_llamacpp_loading accepts; whether real b11755 emits identical bytes during load was already covered by the C2 live receipts, not re-proven here.

# Installs
None. Used only system python3 3.14.8, bash, curl/ss/flock already present. No pacman transaction (host-wide pause honored).
