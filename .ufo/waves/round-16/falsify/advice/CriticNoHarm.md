VERDICT: partial — round-16 (b8e485c) "harms no axis": operability holds, but there is one overstated calibration/depth claim (router), one adjacency side effect (PATH shadow plus an unpinned default server), and one governance tradeoff (PROVINCE narrows an L0 gate)

Axes checked: depth, coverage, freshness, adjacency, operability, calibration.

## Confirmed no harm (operability and exit semantics)

- `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/...` → **exit 0**; `tests 72, passes 72, failures 0`, probe_sha256 `6edd3c4c…fa50`.
- `bash tools/test-snapshot.sh` → **exit 0**, `RESULT pass=30 fail=0`.
- Gating is unchanged. `check` counts drift generically (`tools/kama-probe.sh:848-849,866`: anything other than `MODEL_OK` is drift), so `MODEL_LOADING` stays exit 2, as `FOREIGN_SERVICE` was. The new branch (`tools/kama-probe.sh:503-508`) runs after 401/403 (`:494-501`) and before HTML (`:510-518`), as `endpoint-identity.md` §Correction round 16 says.
- S036 code claim verified in the pinned copy: `.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp:314-325` builds the 503 body, and `:354` (state gate) comes before `:357` (API key).
- Host footprint is clean after the run. `pgrep -ax llama-server` → exit 1 (none). `ss -ltn` on 8080/34113 → no rows. `~/.cache/llama.cpp` and `~/.cache/huggingface` are absent. No llama-server user systemd unit was found. The tarball sha256 `753bfa73…6e226` equals S038. The release page shows "Pre-release" (2 hits), consistent with S038.
- Calibration is not inflated: SCORECARD plans 7→7 and 8→8.

## F1 — the "router mode never emits the envelope" claim is wider than the code (calibration, depth; fixable)

Where the claim appears:
- `SKILL.md:523` "Router mode never emits the body"
- `tools/kama-probe.sh:35-36`
- `corpus/knowledge/endpoint-identity.md:204-205`
- `corpus/knowledge/llamacpp-loading-lifecycle.md:39-41` "so it never emits this body"
- `corpus/SOURCES.md:49` (S037 teaches cell) "the router … never emits that body"

Counterexample, from code at the same commit 704366d76. I fetched `tools/server/server-models.cpp` (sha256 `9c5a6f2c…8b4a`) and `server-models.h` (`566a6eea…f48e6`); neither is in the pinned source set.
- The router maps `/metrics`, `/slots` and `/lora-adapters` to `proxy_get`, and the POST inference routes to `proxy_post` (pinned `server.cpp:242,262,264`).
- `router_validate_model` rejects a request only when `!models_autoload && !meta->is_running()` (`server-models.cpp:2175`).
- `is_running()` includes `SERVER_MODEL_STATUS_LOADING` (`server-models.h:98-100`).
- With `autoload=false`, `proxy_get` skips `ensure_model_ready` (`server-models.cpp:2274-2277`). `proxy_request` checks only `is_running` (`:1852`), then forwards to the child.
- The child runs the single-model path: listener starts first, then the `child.is_child()` callback, then `load_model`, then `is_ready` (pinned `server.cpp:493-515`). So during that window the child answers the S036 envelope.

Conclusion: a router can relay the exact envelope on proxied per-model routes [INFERENCE: static code read, not executed]. What does hold is that the router's own middleware, `/health` and `/v1/models` (`get_router_models`, `server.cpp:269`) never emit it, because `is_ready` is set at `server.cpp:460`.

Impact: probe verdicts are unaffected, since the probe reads only `/v1/models`. The harm is to the documented limit and to S037's teaches cell, which claims more than `server.cpp` alone shows.

Smallest correction: reword all five sites to "the router's own middleware, `/health` and `/v1/models` never emit it; per-model routes the router proxies (`/metrics`, `/slots`, `/lora-adapters`, POST inference, with `autoload` off) can relay a loading child's envelope". Pin `server-models.cpp` and `server-models.h` if the claim is kept.

## F2 — PATH shadow plus an unpinned default server (adjacency, operability; tradeoff plus a fixable gate gap)

- `which -a llama-server` → only `/home/vgpnk/.local/bin/llama-server` → `~/.local/opt/llama-b11755/llama-server`. In PATH, `~/.local/bin` is entry 4 and `/usr/bin` is entry 13.
- So a bare `llama-server` resolves host-wide to a GitHub Pre-release, and it would shadow any later package-installed `/usr/bin/llama-server`.
- `SKILL.md:538-539` warns only about the opposite confusion ("a later `/usr/bin/llama-server` must not be confused with the pinned build").
- No documented round-16 command needs the link: the SKILL capability row passes an absolute `--server`.

The link also matters inside kama:
- `tools/kama-llamacpp-live.py:691` defaults the server to `shutil.which('llama-server')`.
- None of the 10 receipt check ids tests the build or the server digest. The ids are `health_ready … model_unchanged`. `build_info` is captured (`:507`) but never graded.
- `--expect-server-sha256` is optional (`tests/llamacpp-live/check-receipt.py:979`), and the SKILL entry command does not pass it.

Result: a run that resolves to a different llama-server gets a VALID receipt. That leaves "10/10 on the pinned llama.cpp b11755 build" (`SHONEN.md:8`, S041) unenforced by the gate. The L1 receipt itself is genuine: realpath `~/.local/opt/llama-b11755/llama-server`, sha256 `b6a31a8e…cd804`, which I re-hashed and found equal.

The install is inside the operator directive's channel (`~/.local/bin`), so this is not a boundary breach.

Smallest correction:
- Make `--server` required, or add `--expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` to the SKILL gate command.
- Name the PATH shadow in the PROVINCE note so the operator can decide whether to keep the symlink.

## F3 — PROVINCE narrows an L0 gate on lane authority (adjacency; tradeoff for the judge)

- `PROVINCE.md:61-63` says: "This narrows round 1's 'L0 must approve any endpoint outside the declared local model registry' only for the process this tool started".
- The gate is at `corpus/lessons/round-1-safety.md:88-90`.
- The only authority cited is a build seat's reading: `ReviewProvinceBoundary.md:11-13` "no L0 ruling is required for it as designed". No L0 ruling is cited.

Mitigations:
- The narrowing is scoped to the child the tool itself starts.
- Lane-owned loopback stubs already run on ephemeral ports (`tests/probe-verdicts`, `tools/test-snapshot.sh`).
- Round-1 Q3 is framed as "May non-model services be probed?"

Still, a charter document now carries a self-granted exception. Smallest correction: reword as "kama reads round-1 Q3 as not covering a child this tool starts; pending L0 confirmation", or cite an L0 ruling.

## F4 — "every lane document" correction claim has residue (freshness; minor)

- SCORECARD round-16 C1 and `corpus/lessons/round-16.md:19-20` say corrections were appended to each document "that called the vocabulary fixed".
- `corpus/knowledge/listener-census.md:7-8` still says "Verdict vocabulary and classification rules are the frozen L1 binding contract". Its round-16 correction (`:389-397`) narrows only the foreign clause.
- `SKILL.md:11-14`, the first thing an agent reads, still lists six verdicts in the present tense. Only the append at `:509` corrects it.

Smallest correction: a one-line pointer in listener-census's correction, or accept this as append-only residue and soften "every".

## F5 — registry header edit breaks a historical byte pin (adjacency; low)

- `git show 836b018:registry/endpoint-consumers.tsv | sha256sum` = `674cc70c…8b67`, which equals `.ufo/round-5/worktree-byte-manifest.json:14`.
- At b8e485c the file hashes to `bf343625…bc6c`; only the comment at line 32 changed.
- No tool or test consumes that manifest (grep over `tools`, `tests` and `.ufo/round-5`: no hits). Registry rows are unchanged, so this is historical only.

Nit: `LOG.md:936` says "five knowledge entries", but the commit appends to seven knowledge files. The two extra ones are the snapshot-history test count and the round-15 ollama-evidence-replay defect.

## Commands and exits

| Command | Exit |
|---|---|
| `git show --stat b8e485c`, and `git show b8e485c -- <files>` | 0 |
| `check.py --probe tools/kama-probe.sh --json` | 0 (72/72) |
| `bash tools/test-snapshot.sh` | 0 (pass=30) |
| `which -a llama-server` | 0 |
| `pgrep -ax llama-server` | 1 (none) |
| `curl` raw `server-models.cpp` / `server-models.h` @704366d | 0 |
| `curl` GitHub API releases/tags/b11755 | 22 (HTTP 403, rate limit); used the HTML release page instead (exit 0) |
| sha256 of tarball, binary and registry blobs | 0 |

## Limitations

- F1 is a static code read; no router was run, and llama-server was not started.
- `server-models.*` were fetched once from raw GitHub and are not pinned by the lane.
- Grep was bounded to the lane paths named above.

## Installs

None. Scratch `/tmp/kama-r16-CriticNoHarm/` was removed.
