# X2Receipts — round 47 / lane kama / C2 live receipts

**Verdict: all three b11909 receipts are sound — schema `kama-llamacpp-live/v4`, `outcome=pass`, 11/11 checks evaluated and passed, `build_info=b11909-caa8191df`, provenance and both digests independently re-derived from upstream, teardown fully proven; b11906 → b11909 differs in binaries only (7 of 51 files), with no observed HTTP surface change.**

Full comparison tables: `.ufo/waves/round-47/w1/out/X2Receipts/compare.md`. Receipts under audit are copied to the same directory.

## 1. What I re-derived (not trusted from the receipts)

| claim | how | result |
|---|---|---|
| release asset digest | `curl` the frozen URL, `sha256sum` (exit 0) | `bf94332a…695b`, 22,475,032 B — equals `provenance.server.asset_sha256`, `c2/live/install.txt:1`, `c2/release-b11909.json` asset digest |
| `server.sha256` | extract archive, `sha256sum llama-b11909/llama-server` | `35ac50fb…7ff0` — equals `server.sha256` in all 3 receipts and `install.txt:4` |
| whole install tree | hashed all 51 regular members and 10 symlink targets of the archive | 51/51 and 10/10 equal `install_tree`/`install_links`; canonical digests recompute to `9f1198f4…` (tree) and `5cb9f486…` (links) = `install_tree_sha256`/`install_links_sha256` |
| receipts describe the *served* install | hashed `/home/vgpnk/.local/opt/llama-b11909` read-only | identical 51 files + 10 links, identical tree digest |
| build identity | `./llama-b11909/llama-server --version` (no listener started) | `0.7.0-dev (build 11909, commit caa8191df)` = `build_info` |
| model digest | `curl` HF URL, `sha256sum` | `270cba1b…256d`, 1,185,376 B = `model.sha256` = `model_sha256_post` = `provenance.model.sha256` |
| `source_binding` (5 spans) | fetched `tools/server/*` at `704366d7…`, compared `file_sha256`, exact span text, `span_sha256` | 5/5 exact; block byte-identical to the round-46 receipts |
| harness identity | `git cat-file -p 3a09a1d9…:tools/kama-llamacpp-live.py \| sha256sum` | `65301a3c…ae65d` = `tool.sha256` in all three receipts (`probe.sha256` likewise) |

Teardown in all three: `alive_at_teardown_start=true`, `sigterm_sent=true`, `sigkill_sent=false`, `returncode=0`, `term_wait_ms=3`, `port_refuses=true`, `port_listener_ownership="child"`, `log_path=null`, and `log_lines[-1]` names the receipt's own port (37903 / 44883 / 39739). Three independent runs: distinct pids/ports, 0.2 s each, `started_utc` 21:16:50.545Z–21:16:51.030Z.

## 2. b11906 vs b11909 — the answer

* **Checks:** all 11 ids and `documented_by` strings identical between rounds; every check evaluated+passed in all six receipts. Only `models_alias_id` (alias), `props_alias` (`build_info` + alias) and the loading-503 *count* differ.
* **Captures:** `/health` body and sha identical (`a29ee2b1…`); `/slots` identical (`6d345b40…`, 4 elements); `/metrics` 501 both; loading envelope body identical (`baa09177…`, `exact=true`, `distinct_bodies=1`, `bodies_dropped=0`). `/v1/models` parses to the same tree — only `data[0].created` (epoch seconds, `1793044659` → `1793049410`) and the alias differ; no key added or removed. `/props` recorded fields differ only in `build_info` (`b11906-4d71b42fd` → `b11909-caa8191df`) and `model_alias`; both rounds are `Content-Length: 2067`.
* **Binaries:** 44 of 51 files byte-identical; 7 changed (`llama-server`, `libllama-server-impl.so`, `libllama.so.0.7.0` 5,275,320→5,275,808, `libllama-common.so.0.7.0`, `libggml-base.so.0.27.0`, `llama-bench`, `llama-quantize`). The 10 soname links are unchanged. Verified against the b11906 archive itself (asset `064ade62…`) that this delta is upstream, not local drift.
* **Source:** `tools/server/{server-context.cpp,server-http.cpp,server.cpp,README.md}` are byte-identical at `4d71b42fd` and `caa8191df`; consequently there is no documented-surface change between the two builds, which is exactly what the captures show.
* **Timeline (one `gh api` call):** b11909 published 21:00:58Z, receipts ran 21:16:50Z, b11910 published 21:20:07Z. b11909 was current when measured and was superseded 3.2 min later; the receipts stay replayable because they pin digests, not "latest".

## 3. Findings (none fails a check)

1. **`/props` body is not captured and its digest is per-run variable.** `tools/kama-llamacpp-live.py:771` — `_capture(port, '/props', keep_body=False)`. Round 47 `/props` shas are all different (`fb5e3e82…`, `4afdf3c5…`, `9089951c…`); round 46 likewise (`fe6aa72e…`, `031b7426…`, `33c7615f…`), at constant `Content-Length` 2067 and identical recorded fields, so an unrecorded field varies per process and cannot be localised from the receipts. Show with `jq -r '.captures.props.body_sha256' .ufo/waves/round-47/c2/live/receipt-*.json`. Proposed fix (not applied): `keep_body=True` for `/props` (2,067 B ≪ `CAPTURE_BODY_CAP = 65536` at line 81), or record every parsed key.
2. **`/v1/models` body digest is unstable across runs** because `data[0].created` is wall-clock epoch seconds (r47-3 `…411` vs r47-1/2 `…410`), which flips the body sha at constant length 670. Cross-round sha inequality is therefore *not* surface drift — the parsed diff is alias + `created` only. Proposed fix: record/normalise `created` beside the digest.
3. **`documented_by`/`source_binding` are anchored to b11755 (`704366d7…`), four releases behind the measured b11909 (`caa8191df…`), and the line numbers have moved:** `get_health` `server-context.cpp:5609-5620` (cited 5288-5299, +321), 503 block `server-http.cpp:313-327`, signal handlers `server.cpp:318-330` (cited 529-534), `shutdown_handler`→`terminate()` `server.cpp:645-649` (cited 519-523), `start_loop`/`return 0` `server.cpp:671`/`684` (cited 575-590). I read the b11909 spans: the predicates still hold, so this is dated sourcing, not a wrong claim. Proposed fix: re-anchor `LLAMA_COMMIT`/`_LLAMA_RAW` (`tools/kama-llamacpp-live.py:61-63`) to the measured release commit, or record `cited_commit` and `measured_commit` separately.
4. **`pdeathsig.prctl_ok` is `"unknown"` in all six receipts** (`tools/kama-llamacpp-live.py:461-468`, returned honestly); parent-death is requested but unverified and no check grades it. Teardown rests on ownership + `port_refuses` + `returncode 0`, which are proven.
5. Round-46 (v3) receipts carry dangling `teardown.log_path` values under `/fast/scratch/hyaku/kama-r46/X1Live/` (all three absent, `ls` exit 1). v4's `log_path: null` is the correct fix and is applied consistently in all three round-47 receipts — no action on round 47.

No edits were made to the lane, the counters, the preregistration, the controls or the receipts: items 1–3 are proposed changes only, written here.

## 4. Risks / blockers

* No blocker. Nothing was started as a service; no lane or git state was mutated (read-only `git cat-file`/`log`, read-only hashing of `/home/vgpnk/.local/opt/llama-b11909`).
* Residual risk: `/props` and `/v1/models` bodies cannot be byte-compared across runs from the receipts (findings 1–2), so a future unrecorded-field change in those two endpoints would be invisible to receipt-level drift checks — C2's `compare()` only reconciles schema, outcome, `server.sha256`, `model.sha256` and per-check booleans (`tools/kama-live-replay.py:108-124`), so it explicitly does not depend on the volatile digests.
* No tooling installs were needed (curl, python3 stdlib, jq, gh already present); `pacman` untouched per the host guard.

## 5. Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Receipts.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Receipts/compare.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Receipts/receipt-1.json`, `receipt-2.json`, `receipt-3.json` (copies of the audited receipts)
