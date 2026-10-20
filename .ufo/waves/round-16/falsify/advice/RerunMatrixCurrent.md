VERDICT: confirm — the C1 green arm reproduces: three independent matrix runs against the current `tools/kama-probe.sh` are record-for-record identical to `.ufo/waves/round-16/run-after.json` on (verdict, reason, exit, drift), 72/72 each, no flake observed in 216 row executions.

# Attack
Re-ran the literal stub matrix against the current probe, twice (concurrently) plus once with the exact argv recorded in `run-after.json`, and compared every row to the committed receipt. No llama-server was started or needed.

# Commands and exits (cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`)
| run | command | exit | wall | result |
|---|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/kama-r16-RerunMatrixCurrent/run1.json` | 0 | 38.07s | stderr `tests=72 passes=72 failures=0` |
| 2 | same, started 2s after run 1 (overlapping; run 1 still live for ~36s) → `run2.json` | 0 | 40.02s | `tests=72 passes=72 failures=0` |
| 3 | exact `run-after.json.command`: `python3 …/tests/probe-verdicts/check.py --probe …/tools/kama-probe.sh --json` → `run3-exact.json` | 0 | 38.11s | `tests=72 passes=72 failures=0` |

Ambient state: `pgrep -x llama-server` rc=1 before run 3 and rc=1 after; `http_proxy/https_proxy/HTTP_PROXY/HTTPS_PROXY/all_proxy/ALL_PROXY/no_proxy/NO_PROXY` all unset. `sha256sum tools/kama-probe.sh` = `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`, equal to `run-after.json:parsed.probe_sha256`; `tests/probe-verdicts/check.py` sha256 = `fd49ff7c0621bf3799c835b8e2baffbac61c35ce8e2c6e91b92fc495ce376140` and is git-clean at HEAD `b8e485c`.

# Record-by-record comparison (`run-after.json` vs each run)
Method: key by `name` (72/72 names match, no missing/extra row in any run). Compare `(verdict, reason, probe_exit, drift)`, then every other field with `port` excluded, then re-hash with each row's own ephemeral `port` and its occurrence in `evidence` replaced by `<PORT>`.

- run 1 vs `run-after`: **0 key diffs**. run 2 vs `run-after`: **0 key diffs**. run 1 vs run 2: **0 diffs** on all non-`port` fields.
- run 3 (exact argv) vs `run-after`: **0 diffs on any field except per-row `port`**, and canonical-JSON sha256 of the port-normalized documents is identical (`22a9d4d49222b827a07b09a0c3db562ff3e1c27be0506666a83acb1191b4bb23` both). Profiles: 30× FOREIGN_SERVICE/non-2xx-non-model-http, 17× MODEL_LOADING/llamacpp-loading, 5× MODEL_OK/matched, 3× UNAUTHORIZED_SERVICE/http-401, 3× FOREIGN_SERVICE/schema-unrecognized, 3× MODEL_OK/expected-wildcard, 3× MODEL_MISMATCH/served-id-mismatch, 2× UNAUTHORIZED_SERVICE/http-403, 2× FOREIGN_SERVICE/html-non-model, 2× FOREIGN_SERVICE/non-model-2xx, 1× DEAD/connection-refused, 1× NOT_HTTP/empty-reply, all exit 2 except the 8 MODEL_OK rows at exit 0. `error` is null on all 72 rows in base and all 3 runs; no probe timeouts.
- **Only differences found, both structurally ephemeral, no verdict impact:** (a) `port` is a fresh kernel-assigned value on all 72 rows (72 distinct ports per run); (b) `AuthAndDead.closed-port-connection-refused` is the one row whose `evidence` string embeds that port — base `"rc=7 Failed to connect to 127.0.0.1:51349 …"` vs `:39875`, `:45615`, `:37567` in my runs. Every other field of all 72 rows is byte-identical across base and all three runs.
- Passing two matrix instances concurrently on the same host produced identical records: no port-collision or CPU-contention flake.

# Findings
1. **[info] Green arm reproducible.** The committed receipt's assertions (`tests=72`, `passes=72`, `failures=0`, per-row verdict/reason/exit) are exactly what a fresh run produces. `run-after.json` is git-clean at HEAD, so the comparison base is the committed artifact, not a working-tree edit.
2. **[note] `drift` carries no independent evidence.** `check.py:337` copies `drift` from the probe's JSON row, and `check.py:346` makes a row pass only if `record["drift"] == (record["verdict"] != "MODEL_OK")`. So "drift identical" is entailed by the pass set; the 8 `drift:false` rows are exactly the 8 MODEL_OK rows. My drift comparison cannot corroborate the probe beyond its own self-consistency.
3. **[note] `stdout_sha256` is not a reproducible verification handle.** Base `64fe78af…`, run 1 `513f9c46…`, run 2 `563ebc7b…`, run 3 `3e6fde34…` — all 76 386 bytes and port-normalized-identical in content. `measure.py` only assigns it (`:163`) and never compares it (`:15`, `:147`, `:163` are the sole references). Any future "verify the receipt digest" step will false-fail; use per-row verdicts or a port-normalized digest instead.
4. **[note] Harness identity is not attested by the receipt.** `run-after.json` pins the probe digest but not `check.py`'s; the digest I observed is recorded above for the record.
5. **[cross-check] The "changed set == 17 loading rows" claim reproduces without `measure.py`.** Diffing HEAD's committed `run-before.json` against my run 3: exactly 17 rows differ, identical to the 17 MODEL_LOADING rows. Of the four requested keys, only verdict and reason actually move — on those 17 rows `probe_exit` is 2→2 and `drift` true→true in every case. Before: 16× FOREIGN_SERVICE/non-2xx-non-model-http + 1× FOREIGN_SERVICE/html-non-model (`NearMissTriple.exact-envelope-labelled-html`, `"GET /v1/models -> 503 text/html (Server: kama-stub)"`); after: 17× MODEL_LOADING/llamacpp-loading.
6. **[lane-state observation, not caused by me]** At 10:54 `git status --porcelain` reported ` M .ufo/waves/round-16/run-before.json`. A byte/deep comparison against `git show HEAD:.ufo/waves/round-16/run-before.json` was identical (0 diff lines, parsed docs deep-equal, same `stdout_sha256 68a15ac3…`, same 55/17), and a follow-up `git diff --raw`/status for that path is clean; mtime was touched at 10:55:04. Content integrity of the baseline is intact — stat churn only. [INFERENCE] another falsify process rewrote the receipt with identical content. I wrote nothing under the lane except this report.

# Limitations
- Three runs on this one host/kernel/python; no cross-environment claim, and ~0.5 s/row means a rare (<1/72) row flake could slip through.
- `measure.py` was not run (forbidden), so the L1 counting table was not re-derived; only `check.py`'s exit 0 / `failures=0` and my own before→after set computation were used.
- The live llama.cpp arm (C2) was not exercised; `pgrep` confirms no server existed before or after.
- Scratch under `/tmp/kama-r16-RerunMatrixCurrent/` was removed after this report; every run is reproducible with the commands above in ~40 s.

# Installs
None. No pacman/uv/npx/network tooling used; no package changes.
