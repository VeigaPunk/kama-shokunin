# W1C05 — claims ledger for draft A (`entry.md`)

Every factual sentence of `entry.md`, the quote that supports it, its locator in the object I read, and how it was checked. Sources: the two objects the counter freezes (`c3/vllm-v0.31.0-release.json`, `c3/vllm-pr-58552.json`, read from the lane clone, byte-checked against my own `gh api` fetches in this directory), the same pull request's file list (`pr-files.json`, seat copy), and the lane tree at the freeze commit `895793e0b4c56bdcb939277b8ff0251b26306d4d`.

Fetch provenance (checked): `fetch-time.txt` = `2026-10-26T01:47:49Z` (my re-fetch; L1's `c3/fetch-time.txt` = `2026-10-26T01:46:17Z`). SHA-256: release `20c282d566d6788b0913bae9090b85a36263d0adb6ecb9112ea923100a71ab21`, pull request `976ea2ea9d6230005eda35adc3b49cbf048fb4f7c37756c461b70a3781a314b9`. `cmp` of my `rel.json` against `c3/vllm-v0.31.0-release.json` → identical; `vllm-pr-58552.json` differs, and a recursive key walk prints exactly three differences, all volatile repository counters: `base.repo.open_issues_count` 9433→9432, `base.repo.open_issues` 9433→9432, `base.repo.size` 328276→328195. `body` and `title` are equal (`a["body"]==b["body"]` → `True`).

Word counts below are `len(quote.split())`; the Gate leg accepts only a quote of ≤25 words located in the copy's `body`/`title`.

## Provenance lines

| id | sentence | source | locator | quote / value | check |
|---|---|---|---|---|---|
| P1 | release object is tag v0.31.0, published 2026-10-05T06:44:55Z, 60454 bytes, SHA-256 `20c282d5…ab21`, copy `c3/vllm-v0.31.0-release.json` | release JSON | `tag_name`, `published_at`, `name`, file size, `sha256sum` | `"v0.31.0"`, `"2026-10-05T06:44:55Z"`, `"v0.31.0"` | `sha256sum c3/vllm-v0.31.0-release.json` → `20c282d5…ab21` |
| P2 | pull request 58552 merged 2026-09-27T17:48:55Z, 25514 bytes, SHA-256 `976ea2ea…14b9`, copy `c3/vllm-pr-58552.json` | PR JSON | `merged_at`, file size, `sha256sum` | `"2026-09-27T17:48:55Z"` | `sha256sum c3/vllm-pr-58552.json` → `976ea2ea…14b9` |
| P3 | both objects fetched 2026-10-26T01:46:17Z by the round-43 L1 (`gh api`) | L1 receipt | `c3/fetch-time.txt` | `2026-10-26T01:46:17Z` | `cat c3/fetch-time.txt` |
| P4 | re-fetched 2026-10-26T01:47:49Z in this seat; release byte-identical; PR differs only in two repo counters; `body`/`title` equal | my fetches | `fetch-time.txt`, `rel-fetch-W1C05.json`, `pr-fetch-W1C05.json` | diff walk output: the three keys above | `cmp` + recursive walk (output reproduced in the seat log) |
| P5 | the pull request's file list was fetched at 2026-10-26T01:52Z | my fetch | `pr-files.json`, `pr-files-W1C05` fetch time | file list of 2 entries | `gh api repos/vllm-project/vllm/pulls/58552/files` → exit 0, `files: 2` |

Note: 2026-10-26T01:46Z UTC is 2026-10-25 22:46 in the lane's local day, which is why the trio's `verified-at` and the row `opened` date are `2026-10-25`.

## Claim and release section

| id | sentence | locator | quote | check |
|---|---|---|---|---|
| C1 | v0.31.0 lists a `/health` endpoint (#58552) under `Fast restart`, in the same bullet as `vllm preload` | release `body`, line 8 (char 1125 for the route item) | "the new `vllm preload` CLI launches the weight-cache daemon that keeps post-quantized weights resident in GPU memory across engine restarts (#56680), now with data parallelism (#57386), MTP draft models (#57312), a `/health` endpoint (#58552) and a readiness wait (#58370)." | `body.count("a `/health` endpoint (#58552)")` → 1 |
| C2 | the PR names the process: the weight cache daemon's parent process | PR `body` line 3 | "Add an HTTP `/health` endpoint to the weight cache daemon parent process." (12 words) | substring present, count 1 |
| C3 | the PR carries a later commit that moves the endpoint to the preload CLI | PR commits | `ff54ad893015a13e869a9c51b8f30f44dfbb8ef7` "[Fast Start] Move daemon health endpoint to preload CLI" | `gh api …/pulls/58552/commits` → 2 entries, first commit title as quoted |
| C4 | that is a different process from the inference server whose one `/health` route the lane holds (S004) | lane tree, held row | `corpus/SOURCES.md:16` teaches cell: "`/health` calls engine `check_health()` and render-only servers always return 200." | `sed -n 16p corpus/SOURCES.md` |
| C5 | a matrix row reading "vLLM: `/health`" is ambiguous without process and read date | derived | follows from C1–C4; no new quote | — |
| R2 | the bullet's grammatical subject is the new CLI, which launches the daemon; the `/health` item carries no process subject | release `body` line 8 | the full bullet in C1; the route item is a noun phrase in the same list as "#57312", "#56680" | read of the whole bullet (one sentence) |
| R3 | the bullet spells the process "weight-cache daemon", hyphenated once | release `body` line 8 | "launches the weight-cache daemon" | `body.count("weight-cache daemon")` → 1; `body.count("weight cache daemon")` → 0 |
| R4 | the unhyphenated name, the states and the owner come from the pull request | PR `body` | C2 quote has "weight cache daemon" (no hyphen) | count in PR `body` → 1 |

## Pull-request section

| id | sentence | locator | quote / value | check |
|---|---|---|---|---|
| B1 | title "Add `/health` endpoint for the weight cache daemon" | PR `title` | "Add `/health` endpoint for the weight cache daemon" (8 words) | field read |
| B2 | closed, merged true, `merged_at` 2026-09-27T17:48:55Z, `merged_by` Isotr0py, base `main` | PR fields | `state="closed"`, `merged=True`, `merged_by.login="Isotr0py"`, `base.ref="main"` | fields printed |
| B3 | purpose sentence | PR `body` line 3 | C2 quote | substring, count 1 |
| B4 | the body describes `starting`, `ready`, `failed` | PR `body` line 5 | "The endpoint reports `starting` while daemon ranks are loading, `ready` after all expected target and draft ranks are available, and `failed` if a daemon process exits." (26 words — **not Gate-eligible**, >25) | substring, count 1 |
| B5 | reason: distinguish daemon startup from readiness | PR `body` line 5 | "This allows external service management systems to distinguish daemon startup from readiness." — the Gate candidate is its 5-word span "distinguish daemon startup from readiness" | substring, count 1 |
| B6 | opening condition: stacked on #58370 | PR `body` line 7 | "Stacked on #58370. Will rebase once #58370 is merged." (9 words) | substring, count 1 |
| B7 | two commits: the move `ff54ad89…` (2026-09-27T07:56:50Z) and the merge head `087ebc20…` | PR `commits`=2, commits list, `head.sha` | as quoted | `commits.json` printed |
| B8 | as merged the endpoint sits with the preload CLI | commits + file list | B7 title, and the route's file is `vllm/entrypoints/cli/preload.py` (D1) | two independent locators agree |

## Diff section (same pull request's file list — seat copy `pr-files.json`)

| id | sentence | locator | quote / value | check |
|---|---|---|---|---|
| D1 | two files modified: `vllm/entrypoints/cli/preload.py` (+87) and `tests/model_executor/model_loader/test_weight_cache.py` (+19) | `pr-files.json` entries | `additions` 87 / 19, `changed_files` 2 in the PR object | list printed |
| D2 | the route is `@app.get("/health", include_in_schema=False)` | `pr-files[1].patch` | `@app.get("/health", include_in_schema=False)` | substring in patch |
| D3 | its body is `return Response(status_code=200 if state.is_ready else 503)` | `pr-files[1].patch` | as quoted | substring in patch |
| D4 | `is_ready` is `ready and not any(proc.exitcode is not None for proc in self.processes)` over a `_ready` flag set by `mark_ready()` | `pr-files[1].patch` | as quoted; `_HealthState.__init__` sets `self._ready = False`, `mark_ready` sets it True | substring in patch |
| D5 | two HTTP outcomes, not three: `ready` → 200; `starting` and `failed` → 503; no body distinguishes them | D2+D3+D4 | the route returns one status code and `Response()` with no content argument | read of the whole `preload.py` patch (87 added lines, printed in full) |
| D6 | the three names are the description's vocabulary; `failed` is observable only as "not ready" | B4 vs D3 | both quoted above | comparison |
| D7 | `--weight-cache-health-port` defaults to `None`, help "Port for the parent /health endpoint; disabled by default."; host defaults to `0.0.0.0` | `pr-files[1].patch` | the flag block: `default=None`, the help string, `--weight-cache-health-host`/`default="0.0.0.0"` | substring in patch |
| D8 | the test's `check_health` accepts only 200 and raises "Weight cache daemon is not ready: HTTP {error.code}" otherwise | `pr-files[0].patch` | `assert response.status == 200`, then the raised message | substring in patch |

## S004 section and scope statements

| id | sentence | locator | quote | check |
|---|---|---|---|---|
| S1 | S004 is docs, tier A, opened 2026-10-19 | `corpus/SOURCES.md:16` | the row cells (`docs`, `A`, `2026-10-19`) | row read |
| S2 | the inference server's handler calls the engine's `check_health()` and render-only servers always return 200 | `corpus/SOURCES.md:16` | "calls engine `check_health()` and render-only servers always return 200" | `sed -n 16p` |
| S3 | the matrix records that render-only servers have no engine and return 200 unconditionally | `corpus/knowledge/runtime-health-surface-matrix.md:15` | "Render-only servers have no engine and return 200 unconditionally — a passing `/health` may not even reach an engine" | `sed -n 15p` |
| S4 | that route is answered with no engine attached and its contract has no model-loaded flag | matrix line 15 | "no model-loaded flag in the contract"; the caveat cell quoted in S3 | same line |
| S5 | the preload route is a different process and meaning: 200 certifies every daemon process is up and none exited | D4 | `is_ready` expression | derived from D4 only |
| S6 | on 2026-10-25 the lane can name exactly two vLLM `/health` surfaces (S004, S481) | this entry's sources | — | scope statement; the entry cites exactly two vLLM rows |
| N1 | the inference server keeps one health route; neither source adds a second, so on this evidence no readiness route has shipped there | release `body`, PR `body` | `body.count("/ready")` → 0 in the release; the PR adds only `/health`; the release's other route item is "a readiness wait (#58370)", a wait, not a route | counts + full read of both `body` fields |
| N2 | the release's readiness wait (#58370) is listed beside `/health` and is not read here | release `body` lines 8 and the "Get started" bullet | "and a readiness wait (#58370)" (5 words) | substring; #58370 not opened for this entry |
| N3 | #46811 and #59179 were not opened for this entry; no claim about their state | staged round-13 amendment, read-only | the staged text names both; neither appears in this entry's fetches | this seat made 4 `gh api` calls: release, PR, PR commits, PR files — none is 46811/59179 |
| N4 | no vLLM process was run and no host contacted | this seat's command log | — | all evidence is GitHub API bytes plus tree reads |

## Gate quote candidates for `corpus/lessons/round-43.md` (each must sit on a line that also carries the row id, the page URL and `2026-10-25`)

| row | candidate | words | located in |
|---|---|---|---|
| S480 (release, docs/A) | "a `/health` endpoint (#58552)" | 4 | release `body`, line 8, char 1125 |
| S481 (PR, community/C) | "Add an HTTP `/health` endpoint to the weight cache daemon parent process." | 12 | PR `body`, line 3, char 14 |
| S481 alternative | "distinguish daemon startup from readiness" | 5 | PR `body`, line 5, char 311 |

Do **not** use the 26-word states sentence as the Gate quote (over the limit), and do not use it as a wire-behavior claim: the route it describes returns 200/503 (D3).

## Sentences I deliberately did **not** write (and why)

- "the endpoint reports three states" as route behavior: contradicted by D3/D4 for the HTTP surface; the entry attributes the three names to the body and the two codes to the patch.
- "v0.31.0 contains this merge": `merged_at` 2026-09-27 precedes `published_at` 2026-10-05, but ordering is not inclusion; the release's own mention of #58552 (C1) is the evidence used instead.
- "the readiness route shipped/not shipped in the inference server" as a global negative: not in either source; the entry scopes it to "neither source read here adds a second route".
- anything about PR 46811, PR 59179, the agentic-api gateway or the semantic router: not opened this round (N3).

## Artifact paths (this seat)

`entry.md`, `claims.md`, `pr-files.json`, `pr-fetch-W1C05.json`, `rel-fetch-W1C05.json`, `pr-commits-W1C05.json`, `fetch-time.txt` — all under `.ufo/waves/round-43/w1/out/W1C05/`.
