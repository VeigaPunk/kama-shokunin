VERDICT: confirm — C2's refusal and digest gates hold: every negative input was refused pre-launch with the documented exit code and no llama-server was left running.

# Attack executed
Re-ran the live tool `tools/kama-llamacpp-live.py` (commit b8e485c checkout) with five negative invocations. Server: `/home/vgpnk/.local/opt/llama-b11755/llama-server`; model: `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`; correct sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` used wherever the digest was not the variable under attack. All `--out` paths pointed into `/tmp/kama-r16-RerunLiveNegatives/`; no receipt files were written because every run exited before receipt emission (`ls r*.json` → no matches).

| # | Invocation (variable) | Expected | Exit | stderr |
|---|---|---|---|---|
| T1 | `--model-sha256 0000…0000` | 3, no launch | **3** | `model digest mismatch / expected: 0000… / actual: 270cba1b… / refusing to launch` |
| T2 | `--port 34113` | 2 | **2** | `kama-llamacpp-live: port-refused-registered:34113` |
| T3 | `--port 8080` | 2 | **2** | `kama-llamacpp-live: port-refused-registered:8080` |
| T4 | `--port 8787` (live listener, unregistered) | 2 | **2** | `kama-llamacpp-live: port-in-use:8787` |
| T5 | `--server /tmp/…/nonexec` (regular file, mode 644) | report exit | **2** | `kama-llamacpp-live: server not executable: /tmp/kama-r16-RerunLiveNegatives/nonexec` |

Port choice for T4: `ss -ltn` listed 127.0.0.1:8787 as LISTEN; `grep -nw 8787 registry/endpoint-consumers.tsv` returned nothing (rc=1), so it exercised the `port-in-use:` branch (tools/kama-llamacpp-live.py:246), not the registered-port branch. T2/T3 exercised `port-refused-registered:` (tools/kama-llamacpp-live.py:238). T5 exited 2 via the not-executable check at tools/kama-llamacpp-live.py:697-700.

# Teardown verification
`pgrep -x llama-server` before the battery: rc=1 (none). `pgrep -x llama-server` after all five runs: rc=1 (none). Nothing was launched or leaked; refusals fire in the pre-check block before `subprocess.Popen`.

# Limitations / inferences
- Exit-2 refusals are distinguished by reason token, not by code alone; codes alone cannot separate registered-port vs in-use refusals [INFERENCE: that matches the documented gate design].
- T4's listener identity was not investigated further; only its LISTEN state and absence from the registry were verified.
- No run reached the ready/probe/capture phase, so post-refusal receipt fields are untested by this attack (by design).

# Installs
None. Tools used: python3, ss, grep, pgrep (all pre-installed).
