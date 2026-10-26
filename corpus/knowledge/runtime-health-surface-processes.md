source: S480 — vLLM v0.31.0 release notes — https://github.com/vllm-project/vllm/releases/tag/v0.31.0 — §Fast restart — opened 2026-10-25 (`gh api repos/vllm-project/vllm/releases/tags/v0.31.0`, tag published 2026-10-05T06:44:55Z, 60454 bytes, SHA-256 `20c282d566d6788b0913bae9090b85a36263d0adb6ecb9112ea923100a71ab21`, copy `.ufo/waves/round-43/c3/vllm-v0.31.0-release.json`); S481 — vLLM pull request 58552 — https://github.com/vllm-project/vllm/pull/58552 — §Purpose — opened 2026-10-25 (`gh api repos/vllm-project/vllm/pulls/58552`, merged 2026-09-27T17:48:55Z, 25514 bytes, SHA-256 `976ea2ea9d6230005eda35adc3b49cbf048fb4f7c37756c461b70a3781a314b9`, copy `.ufo/waves/round-43/c3/vllm-pr-58552.json`); S483 — vLLM `preload.py` at tag v0.31.0 — https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py — §`_build_health_app` lines 70-77 — opened 2026-10-26 (raw re-fetched 2026-10-26, 12631 bytes, SHA-256 `d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d`, byte-identical to the committed copy `.ufo/waves/round-43/c3/vllm-v0.31.0-preload.py` and to the merged blob at `e7900156e130c9880eb03b7c1f2df32820e7a2be`, copy `.ufo/waves/round-44/w1/out/S9D2Row/vllm-v0.31.0-preload.py`)
verified-at: 2026-10-25 — both objects fetched 2026-10-26T01:46:17Z by the round-43 L1 and re-fetched 2026-10-26T01:47:49Z by seat W1C05: the release JSON is byte-identical, the pull-request JSON differs only in the repository's open-issue and size counters while `body` and `title` are equal, and the pull request's file list was fetched at 2026-10-26T01:52Z
recheck: 90d — re-open the release page and the pull request, re-count `/health` in the `vllm preload` bullet, and re-read `vllm/entrypoints/cli/preload.py` at the then-current merge: expect one `@app.get("/health")` answering 200/503, or record what replaced it (ran 2026-10-25)
coverage-map: runtime-health-surface-matrix — which process each vLLM health route belongs to, and which `/health` a matrix row means
ground: frontier item "endpoint health probes" — the round-12 and round-13 ledger asked whether the readiness work had shipped and which process owns the shipped route. The round-13 amendment's answer leaned on a follow-on commit title; this entry opens the pull request itself and keeps every sentence inside the two objects it read.

# vLLM's shipped `/health` belongs to the weight cache daemon's parent, not to the inference server

## Claim

vLLM v0.31.0 lists a `/health` endpoint (#58552) under `Fast restart`, in the same bullet as `vllm preload`. The pull request behind that endpoint names the process it went into — the weight cache daemon's parent process — and carries a later commit that moves it to the preload CLI. That is a different process from the inference server whose one `/health` route the lane already holds (row S004). So a matrix row reading "vLLM: `/health`" is ambiguous until it names the process and the date it was read.

## Decision table

| process | route | states | status | source |
|---|---|---|---|---|
| inference server (`vllm serve`, OpenAI-compatible API surface) | `GET /health` | 200; row S004's cell records that "render-only servers always return 200", so a 200 is not a load-state signal | shipped, documented; held since round 10 | S004, `runtime-health-surface-matrix.md:15` |
| weight-cache supervisor (the `vllm preload` CLI) | `GET /health` on the opt-in `--weight-cache-health-port` | 503 until every expected target and draft rank reports, 200 after; an exited rank returns it to 503; the supervisor exits if a rank dies during startup | shipped in v0.31.0 (merged 2026-09-27); disabled unless the port is set | S480, S481 |
| weight-cache daemon ranks (one per GPU) | none of their own | they report readiness to the supervisor over a multiprocessing queue, not over HTTP | shipped; internal to the supervisor | S481 |
| inference-server readiness (`/ready`, `/readyz`) | none shown by either source | — | not covered by this entry; the two readiness pull requests (#46811, #59179) are recorded at `corpus/lessons/round-39-verifier-spotcheck.md:67` | `corpus/lessons/round-39-verifier-spotcheck.md:67` |

## The release: the route is an item of the `vllm preload` feature

The `Fast restart` bullet of the v0.31.0 notes (release `body`, line 8) reads: "the new `vllm preload` CLI launches the weight-cache daemon that keeps post-quantized weights resident in GPU memory across engine restarts (#56680), now with data parallelism (#57386), MTP draft models (#57312), a `/health` endpoint (#58552) and a readiness wait (#58370)."

That sentence has one grammatical subject — the new CLI, which launches the daemon — and the `/health` item carries no process subject of its own. The bullet spells the process "weight-cache daemon", hyphenated once; the unhyphenated name, the route's states and the route's owner come from the pull request, not from here.

## The pull request: the daemon parent process, three named states, one later commit

- Title: "Add `/health` endpoint for the weight cache daemon". The object reads `state: closed`, `merged: true`, `merged_at` 2026-09-27T17:48:55Z, `merged_by` Isotr0py, base `main`.
- Purpose (PR `body`, line 3): "Add an HTTP `/health` endpoint to the weight cache daemon parent process."
- The states are described in the body (line 5): "The endpoint reports `starting` while daemon ranks are loading, `ready` after all expected target and draft ranks are available, and `failed` if a daemon process exits."
- The body gives the reason for the split: "This allows external service management systems to distinguish daemon startup from readiness."
- Opening condition, recorded in the body: "Stacked on #58370. Will rebase once #58370 is merged."
- The pull request has two commits (`commits` 2): `ff54ad893015a13e869a9c51b8f30f44dfbb8ef7` "[Fast Start] Move daemon health endpoint to preload CLI" (2026-09-27T07:56:50Z) and `087ebc203d88f0aa0491ba808e70e3ebd1537904` "Merge branch 'main' into vllm-daemon-health" (the head). The move is shown in the object this entry read, not inferred from the release: as merged the endpoint sits with the preload CLI, and "the daemon" alone describes the earlier commit.

## What the same pull request's diff adds, read against the body's three states

The file list of the same pull request (`.ufo/waves/round-43/c3/vllm-pr-58552-files.json`, fetched 2026-10-26T01:52Z) modifies two files: `vllm/entrypoints/cli/preload.py` (+87) and `tests/model_executor/model_loader/test_weight_cache.py` (+19). The file itself, read at tag v0.31.0 (`.ufo/waves/round-43/c3/vllm-v0.31.0-preload.py`, 12631 bytes, SHA-256 `d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d`; `gh api` at the PR's merge commit `e7900156e130c9880eb03b7c1f2df32820e7a2be` returns the same digest), registers the route at `preload.py:73`, `@app.get("/health", include_in_schema=False)`, inside `_build_health_app` (`:70`), and its handler returns one expression at `:75`: `return Response(status_code=200 if state.is_ready else 503)`. `is_ready` (`:64-67`) is `ready and not any(proc.exitcode is not None for proc in self.processes)` over a single `_ready` flag set by `mark_ready()` (`:59`).

Read against the body, that is two HTTP outcomes, not three: `ready` is 200, and `starting` and `failed` are both 503, with no body distinguishing them. The three names are the description's vocabulary, and `failed` is observable on the wire only as "not ready". The same file also makes the route opt-in — `--weight-cache-health-port` (`preload.py:134-137`) defaults to `None` with the help "Port for the parent /health endpoint; disabled by default." — and the test's `check_health` accepts only 200, raising "Weight cache daemon is not ready: HTTP {error.code}" otherwise.

## Which `/health` a row means: S004 is the other process

Row S004 (docs, tier A, opened 2026-10-19) holds the inference server: its `/health` handler "calls engine `check_health()` and render-only servers always return 200" (`corpus/SOURCES.md:16`), and `corpus/knowledge/runtime-health-surface-matrix.md:15` records "Render-only servers have no engine and return 200 unconditionally — a passing `/health` may not even reach an engine". That route is answered with no engine attached and carries no model-loaded flag in its contract. The preload route is a different process and a different meaning: 200 certifies that every daemon process is up and none has exited.

A matrix row must therefore carry a process value and a read date. On 2026-10-25 this lane can name two vLLM `/health` surfaces and no more: the inference server's (S004) and the weight cache daemon's parent, served from the preload CLI (S481).

## What this entry does not change

- The inference server keeps one health route. Neither source read here adds a second route to it, so on this evidence no readiness route has shipped there; the release's readiness wait (#58370) is listed beside `/health` and is not read here.
- The two readiness-proposal pull requests the staged round-13 amendment names (#46811, #59179) were not opened for this entry, which makes no claim about their state, paths or merges.
- No vLLM process was run and no host was contacted: this is a reading of two GitHub API objects, one file list and one source file, and nothing here says the endpoint answers anywhere (KQ4).

## Limits

- Two API objects, one file list and one source file at a tag. The file is `preload.py` at tag v0.31.0, byte-identical to the merge commit's; a later change to it (v0.32.0 or `main`) is outside this reading, which is why the recheck re-reads it.
- The body's "Test Result" section is the author's own statement; it is recorded as a description, not treated as evidence that the states behave as described.
- Tier split is deliberate (KQ6): the release page (docs, A) grounds that v0.31.0 shipped a `/health` item, and the pull request (community, C) grounds the process, the states and the move; no sentence here rests on the C row alone.
- The release `body` is a curated summary and lists the same two fixes again in its "Get started" section; a later tag can reword either occurrence.

## Cited sources

S480 vLLM v0.31.0 release notes §Fast restart, release `body` line 8 (opened 2026-10-25); S481 vLLM pull request 58552 §Purpose, title, commit list and file list (opened 2026-10-25) and `vllm/entrypoints/cli/preload.py` at tag v0.31.0, read through the same row's pull request (the file copy is evidence, not a separate row); S004 vLLM `health(raw_request)` handler, held at `corpus/SOURCES.md:16` (opened 2026-10-19).
