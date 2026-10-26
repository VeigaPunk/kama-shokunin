# W1C08 — registry rows and index lines (round 43, kama)

Scope: two `corpus/SOURCES.md` registry rows (S480, S481), one `## Search log` line,
the `corpus/README.md` coverage-map and frontier-disposition blocks, and the
`PROVINCE.md` Owns row for the C3 entry
`corpus/knowledge/runtime-health-surface-processes.md`.

Every cell below is grounded in the two sources opened this round with `gh api`
(read-only): `repos/vllm-project/vllm/releases/tags/v0.31.0` (exit 0,
`tag_name` v0.31.0, `published_at` 2026-10-05T06:44:55Z) and
`repos/vllm-project/vllm/pulls/58552` (exit 0, title
``[Fast Start] Add `/health` endpoint for the weight cache daemon``,
`state` closed, `merged` true, `merged_at` 2026-09-27T17:48:55Z).
No `|` occurs inside any cell below.

## 1. Registry rows — append to the single table under `## Registry`

Next unused ids: the freeze registry's highest id is S479 (`grep -o '^| S[0-9]\{3,\}' corpus/SOURCES.md`
at 895793e, 220 row lines), so S480 and S481 are free and are not reused.

```
| S480 | vLLM release notes v0.31.0 — https://github.com/vllm-project/vllm/releases/tag/v0.31.0 | docs | A | what the v0.31.0 release notes list as shipped for health and readiness and which feature the entry is filed under — the release-level statement; not what the endpoint does at runtime, not the HTTP route table, and not the merge state or later location of any pull request | §the "Fast restart" bullet — "a `/health` endpoint (#58552) and a readiness wait (#58370)", where the same sentence names "the new `vllm preload` CLI launches the weight-cache daemon"; §the same release's feature list — "readiness wait (#58370), `/health` (#58552)"; release v0.31.0 published 2026-10-05; API https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.31.0, committed copy .ufo/waves/round-43/c3/vllm-v0.31.0-release.json sha256 <PLACEHOLDER-RELEASE> (observed value 20c282d566d6788b0913bae9090b85a36263d0adb6ecb9112ea923100a71ab21) | the release files the `/health` endpoint under "Fast restart", the `vllm preload` feature that keeps post-quantized weights resident, so the release page by itself does not say which process answers the route | mined | 2026-10-25 | 90d | corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md |
| S481 | vLLM pull request 58552 — https://github.com/vllm-project/vllm/pull/58552 | community | C | which process the `/health` endpoint was added to and the three states the pull request's own purpose statement names; the author's description of a merged change, not runtime behaviour, not the endpoint's later location, and never sole support for an admitted entry | §Purpose — "Add an HTTP `/health` endpoint to the weight cache daemon parent process."; the state sentence — "The endpoint reports `starting` while daemon ranks are loading, `ready` after all expected target and draft ranks are available, and `failed` if a daemon process exits."; the purpose consequence — "This allows external service management systems to distinguish daemon startup from readiness."; merge state merged 2026-09-27; API https://api.github.com/repos/vllm-project/vllm/pulls/58552, committed copy .ufo/waves/round-43/c3/vllm-pr-58552.json sha256 <PLACEHOLDER-PR> (observed value 976ea2ea9d6230005eda35adc3b49cbf048fb4f7c37756c461b70a3781a314b9) | the endpoint vLLM shipped in v0.31.0 belongs to the weight cache daemon parent process and reports starting, ready and failed — a startup-versus-readiness split the inference server's single `/health` handler (S004) does not carry | mined | 2026-10-25 | 90d | corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md |
```

Notes for the L1:

- `<PLACEHOLDER-RELEASE>` / `<PLACEHOLDER-PR>` are to be replaced by the SHA-256 of
  the copy actually committed at `.ufo/waves/round-43/c3/` (the frozen counter hashes
  the blob at the tip, not the working tree). The observed values printed beside each
  placeholder are the hashes of the copies committed by `1af8d51`
  (`sha256sum .ufo/waves/round-43/c3/*.json`, run 2026-10-25). A fresh
  `gh api repos/vllm-project/vllm/pulls/58552` fetch on 2026-10-25 hashed
  `aff67c2ea3ae8214fff117d5c13796f0c6dac90ddea2f4a3d460e66020b78a21`; the only
  differing top-level field is the mutable `base`, and the `body` bytes that carry
  both frozen quotes are identical, so either fetch grounds the row's cells but only
  the committed bytes satisfy the anchor check.
- `opened` is 2026-10-25 as the assignment fixes it; the committed copy's
  `fetch-time.txt` reads `2026-10-26T01:46:17Z` (UTC), the same access session at a
  UTC date boundary. Round 42's row set carries the same relationship
  (opened 2026-10-25, fetch 2026-10-25T21:06Z).
- The anchor cells contain no 32–127-character non-64 hex run other than the two
  64-character SHA-256 values, so the C2 hex-run census has nothing new to classify
  from these rows.
- Used-by names `corpus/lessons/round-43.md`; the row is `mined` only once that
  lesson exists (census E11 resolves used-by paths on disk).

## 2. Search log line — append under `## Search log`

```
- **2026-10-25 — round-43 vLLM `/health` process sources (assimilation from the staged merge/kama package).** Question: in which process does the `/health` endpoint vLLM shipped in v0.31.0 live, and what does the release note list beside it? Where: the staged `merge/kama` package read-only (registry rows S430, S431, S438, S439, S442, S443 and the two health amendments of 2026-10-24), then the two sources those rows cite, opened read-only with `gh api` on 2026-10-25 — `repos/vllm-project/vllm/releases/tags/v0.31.0` and `repos/vllm-project/vllm/pulls/58552` — with the API responses committed as copies under `.ufo/waves/round-43/c3/`. Identified 6, screened 6, included 2 (S480 release notes, S481 the pull request), excluded 4: S438 and S439 are open, unmerged pull requests, so they read as proposals rather than released contracts (the same reason S026 was rejected in round 10); S442 is a commit in another repository and another process (the agentic-api gateway) and grounds no cell of this entry; S443 is the Semantic Router's Chinese reference, a third process again. Stop: the release page names the feature and the pull request names the process and the three states, which is every cell the entry carries; the four excluded rows would ground claims the frozen C3 entry does not make, and they stay staged with no row this round.
```

## 3. `corpus/README.md` — coverage map and frontier disposition blocks

Append after the round-42 frontier block and its appended correction paragraph:

```
## Coverage map — round 43 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/runtime-health-surface-processes.md` (`corpus/knowledge/runtime-health-surface-processes.md`) | Which vLLM process answers `/health`: the v0.31.0 release notes list a `/health` endpoint and a readiness wait under "Fast restart" (`vllm preload`, the weight cache daemon), and pull request 58552 states the endpoint was added to the weight cache daemon parent process with `starting`, `ready` and `failed` states — a different process from the inference server whose one `/health` route the lane already holds (S004); S480, S481 | 43 |

## Frontier disposition — round 43

Advanced: the process map of vLLM's `/health` surface. The endpoint the v0.31.0 release notes announce is the weight cache daemon's (`vllm preload`), not the inference server's; the pull request behind it names the three states and the reason for them, "distinguish daemon startup from readiness". Entry: `knowledge/runtime-health-surface-processes.md` (S480, S481).

Still frontier:
- K05 (declared versus served context capacity): the served side on a registered endpoint still needs an authorised serving runtime. No endpoint was sampled this round; round 42's engine-side source readings (`knowledge/context-capacity-engine-sides.md`, S478, S479) stand and nothing here widens them.
- Whether the daemon endpoint stayed in the daemon process. The staged round-13 amendment records a follow-on commit "Move daemon health endpoint to preload CLI"; neither row opened this round grounds that move, so the entry names the daemon parent process as the pull request's purpose states and says nothing about later relocation.
- Shipped readiness for the inference server: pull requests 46811 and 59179 remain open proposals, and the shipped server route set is still the single `/health` of S004.

No endpoint was sampled, no serving runtime was started, and registered consumers still sample DEAD; that stays operator-owned.
```

## 4. `PROVINCE.md` — Owns row

Insert as a new row of the **Owns (surfaces)** table (after the
`liveness/readiness probe conventions` row):

```
| which vLLM process serves `/health` — weight cache daemon (`vllm preload`) versus inference server | `corpus/knowledge/runtime-health-surface-processes.md` — source readings of the v0.31.0 release note and pull request 58552 (S480, S481); names the process from the sources and samples no endpoint |
```

No round-43 note is added to `PROVINCE.md`: the Owns row is the whole deliverable
assigned to this seat, and any note paragraph would duplicate the frontier block.
