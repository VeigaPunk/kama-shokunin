source: S480 — vLLM release notes v0.31.0 — https://github.com/vllm-project/vllm/releases/tag/v0.31.0 (sha256 `20c282d566d6788b0913bae9090b85a36263d0adb6ecb9112ea923100a71ab21`, copy `.ufo/waves/round-43/c3/vllm-v0.31.0-release.json`); S481 — vLLM pull request #58552 — https://github.com/vllm-project/vllm/pull/58552 (sha256 `976ea2ea9d6230005eda35adc3b49cbf048fb4f7c37756c461b70a3781a314b9`, copy `.ufo/waves/round-43/c3/vllm-pr-58552.json`)
verified-at: 2026-10-25 — both objects opened 2026-10-25 (`.ufo/waves/round-43/c3/fetch-time.txt` reads 2026-10-26T01:46:17Z UTC, the same fetch on a host at 2026-10-25T22:46:17-03); this seat re-fetched both and compared `body` and `title`
recheck: 90d — re-open both URLs and re-check three things: the "Fast restart" bullet still names `vllm preload` and "(#58552)"; the pull request body still carries its three-state sentence; `vllm/entrypoints/cli/preload.py` at the pull request's merge commit still serves `/health` as 200/503
coverage-map: runtime-health-surface-matrix — which process vLLM's `/health` route belongs to; adds the second process the vLLM row at `runtime-health-surface-matrix.md:15` (row S004) does not name
ground: frontier item "endpoint health probes" — the round-42 closure and the staged round-12/round-13 amendments asked which process vLLM's shipped `/health` endpoint belongs to. It is the weight-cache supervisor, not the inference server.

# vLLM ships `/health` twice, and only one of them belongs to the inference server

vLLM v0.31.0's notes list a new `/health` endpoint under **Fast restart**, beside
`vllm preload`. The pull request behind it adds the endpoint to the weight cache
daemon's parent process — a different process from the inference server whose
`/health` route row S004 documents. A matrix row reading `vLLM: /health` names a
URL and not a process, so it cannot be rechecked or compared across engines.

## Decision table

| process | route | states | status | source |
|---|---|---|---|---|
| inference server (`vllm serve`, OpenAI-compatible API surface) | `GET /health` | 200; row S004's cell records that "render-only servers always return 200", so a 200 is not a load-state signal | shipped, documented; held since round 10 | S004, `runtime-health-surface-matrix.md:15` |
| weight-cache supervisor (the `vllm preload` CLI) | `GET /health` on the opt-in `--weight-cache-health-port` | 503 until every expected target and draft rank reports, 200 after; an exited rank returns it to 503; the supervisor exits if a rank dies during startup | shipped in v0.31.0 (merged 2026-09-27); disabled unless the port is set | S480, S481 |
| weight-cache daemon ranks (one per GPU) | none of their own | they report readiness to the supervisor over a multiprocessing queue, not over HTTP | shipped; internal to the supervisor | S481 |
| inference-server readiness (`/ready`, `/readyz`) | none shown by either source | — | not covered by this entry; the two readiness pull requests (#46811, #59179) are recorded at `corpus/lessons/round-39-verifier-spotcheck.md:67` | `corpus/lessons/round-39-verifier-spotcheck.md:67` |

## What the two sources say

- Release body §Highlights (line 8), the Fast restart item: "**Fast restart**: the new `vllm preload` CLI launches the weight-cache daemon"; the same item lists, among the restart features, "a `/health` endpoint (#58552) and a readiness wait (#58370)". The item appears again in body §Engine Core (line 66) as "readiness wait (#58370), `/health` (#58552)".
- Pull request body §Purpose: "Add an HTTP `/health` endpoint to the weight cache daemon parent process."
- Same section: "The endpoint reports `starting` while daemon ranks are loading, `ready` after all expected target and draft ranks are available, and `failed` if a daemon process exits. This allows external service management systems to distinguish daemon startup from readiness."
- Merge state: `state` closed, `merged` true, `merged_at` 2026-09-27T17:48:55Z, merge commit `e7900156e130c9880eb03b7c1f2df32820e7a2be`; the same body says "Stacked on #58370."

## Which process serves it, from the pull request's own commits

The commit list of the pull request this entry opened holds
`ff54ad893015a13e869a9c51b8f30f44dfbb8ef7`, "[Fast Start] Move daemon health
endpoint to preload CLI" (2026-09-27T07:56:50Z), which puts the endpoint in
`vllm/entrypoints/cli/preload.py` (+87/-0). That module's docstring says it
"Launches one weight cache daemon per GPU", and that "Engines then load from the
daemons with:" a `vllm serve` command carrying `--load-format ipc_cache`. The
process that answers the route is therefore the supervisor that launches the
daemons — a different process from the inference server, which is its client.

## The description names three states; the merged route reports two codes

At merge commit `e7900156`, that file serves `@app.get("/health",
include_in_schema=False)` as `Response(status_code=200 if state.is_ready else
503)` with no body. Its state is a boolean (`_ready`, `mark_ready`, `is_ready`),
not a named state: `failed` occurs zero times in the file, and the only
"starting" in it is inside "restarting" in the module docstring. So a client
cannot tell `failed` from `starting` — both are 503.
`_HealthState.is_ready` is false while any daemon process has an exit code, and a
rank that dies during startup makes the supervisor `sys.exit`. The three state
names describe the mechanism in the pull request's prose; no client can read them
off the route. `--weight-cache-health-port` is documented in the same file as
"Port for the parent /health endpoint; disabled by default."

## What has NOT changed

- No readiness route is shipped in the inference server by anything these two sources show: `/ready` occurs zero times in both bodies.
- The release's `#58370` item is a "readiness wait" and the pull request is stacked on it; neither object shows a readiness route for the engine.
- The two readiness pull requests (#46811, #59179) are not covered by this entry.
- The inference server's `/health` reading is unchanged: row S004's cell still says "`/health` calls engine `check_health()` and render-only servers always return 200."

## Limits

- Two JSON objects. `body` and `title` matched a 2026-10-25 re-fetch; the pull request object as a whole is volatile — `.base.repo.open_issues`, `open_issues_count` and `size` differed between the committed copy and the re-fetch — so a row's anchor pins the committed copy's bytes, not the live object.
- The commit-list and merged-file paragraphs rest on `gh api` reads of the pull request object at 2026-10-25 (`pulls/58552/commits`, `contents/…/preload.py?ref=e7900156`). No copy of that file is committed under `.ufo/waves/round-43/c3/`; the closure must commit one or drop those paragraphs.
- The inference-server side is the lane's held row, not a re-read of S004 this round.
