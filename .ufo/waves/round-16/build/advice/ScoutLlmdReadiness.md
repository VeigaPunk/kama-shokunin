# ScoutLlmdReadiness — S021 re-open (llm-d model-aware readiness)

Axes: citation freshness (S021 URL/version/date), claim scope (what the page can support
for MODEL_LOADING), calibration risk (not-ready vs DEAD/FOREIGN). Read-only seat; no lane
gate, harness or test was run.

## Observed page state (accessed 2026-10-20)

| View | URL | Version label | Date evidence |
|---|---|---|---|
| v0.10 (S021's pinned version) | https://llm-d.ai/docs/0.10/operations/readiness-probes | "Version: v0.10" (rendered l.30); "This is documentation for llm-d **v0.10**, which is no longer actively maintained." (l.26) | No page date. Nearest: release v0.10.0 `published_at` "2026-09-29T00:00:25Z" (https://api.github.com/repos/llm-d/llm-d/releases?per_page=6); file last commit on release-0.10 is 1e9a86a3, `"date": "2026-09-21T18:56:25Z"`, a link-only rename (https://api.github.com/repos/llm-d/llm-d/commits?sha=release-0.10&path=docs/operations/readiness-probes.md) |
| v1.0 (latest) | https://llm-d.ai/docs/operations/lifecycle/readiness-probes | "Version: v1.0 (latest)" (rendered l.26) | No page date. Nearest: release v1.0.0 `published_at` "2026-10-20T02:30:10Z" (same releases API); main file last commit 094ea472, `"date": "2026-10-12T21:00:24Z"` (https://api.github.com/repos/llm-d/llm-d/commits?path=docs/operations/lifecycle/readiness-probes.md) |
| URL recorded by S021 | https://llm-d.ai/docs/operations/readiness-probes | — | HTTP 404 on 2026-10-20 (two fetches). File moved on main by commit 551e26b6 (2026-10-07T19:47:38Z): "lifecycle/: rollouts, graceful-shutdown, readiness-probes" (https://github.com/llm-d/llm-d/commit/551e26b6e816c59e478845d3c14e781497e9dd9d) |

- Neither page carries a rendered date: grep for `last updated|lastUpdated|datePublished`
  returned no matches on both URLs. The raw markdown has no frontmatter; its first line is
  "# vLLM Model-Aware Readiness Probes"
  (https://raw.githubusercontent.com/llm-d/llm-d/release-0.10/docs/operations/readiness-probes.md).
  So the page version label plus release/commit dates are the only dated anchors; the prose
  itself cannot be dated. [Observed absence]
- [INFERENCE] The 404 is the v1.0 docs cutover, not a second move: S021 opened the
  unversioned URL on 2026-10-19 (corpus/SOURCES.md:33), while the main-branch move to
  `lifecycle/` predates that (2026-10-07), so the unversioned path was serving the v0.10
  docs; v1.0.0 published 2026-10-20T02:30:10Z, and the unversioned path now resolves to the
  v1.0 tree, where the page lives under `lifecycle/`.
- The v0.10 page still carries every quoted passage. The v1.0 page repeats all six passages
  verbatim (line numbers below in parentheses); the observed edits are confined to the
  port-role table's decode row, the example (`Wide Endpoint Deployment` → `Disaggregated
  Decode Pod`, l.201), and the two resource links (v0.10.0 → v1.0.0 README, versioned →
  unversioned observability page).

## Located passages (v0.10 rendered lines; v1.0 lines in parentheses)

| # | Location | Quote (<=25 words) | Bearing |
|---|---|---|---|
| Q1 | §Problem Statement, final paragraph, l.55 (l.51) | "The vLLM `/health` endpoint only indicates that the server process is running, **not** that models are loaded and ready to serve." (21) | `/health` is process liveness, not model readiness |
| Q2 | §How It Works → `/health` Endpoint, l.118, 128-129 (l.114, 124-125) | "The `/health` endpoint provides a basic liveness check:" … "Does **not** wait for model loading / Use for `livenessProbe` only" | liveness route, explicitly not readiness |
| Q3 | §`/v1/models` Endpoint (OpenAI-Compatible), l.133 (l.129) | "The `/v1/models` endpoint is model-aware and indicates true readiness:" (11) | readiness route is the model API |
| Q4 | same section, Behavior, l.152-153 (l.148-149) | "Returns `503` or connection refused during model loading / Returns `200 OK` with model metadata once ready" (16) | loading is a not-ready HTTP state on the model route, resolved by the same route |
| Q5 | §Probe Lifecycle, l.165-166 (l.161-162) | "[livenessProbe on /health] ← Restarts if server crashes / [readinessProbe on /v1/models] ← Routes traffic when ready" | crash/restart is the liveness axis; load gates traffic only |
| Q6 | §Overview, l.40-42 | "Container Running" … "API Server Ready" … "Model Loaded" | three stages; a state exists between alive and ready |

All six lines are from https://llm-d.ai/docs/0.10/operations/readiness-probes; the same text is at
https://llm-d.ai/docs/operations/lifecycle/readiness-probes at the lines in parentheses. S021's
recorded quote ("The `/v1/models` endpoint is model-aware and indicates true readiness",
corpus/SOURCES.md:33; corpus/lessons/round-10.md:81) is still exact and located at Q3.

## Bearing on "MODEL_LOADING is not-ready, not dead/foreign"

Supports (documentation only):
- Process liveness and model readiness are distinct questions (Q1-Q3, Q6).
- A 503 from the model route during loading is a normal lifecycle answer on that same route,
  with no restart: liveness fires on a crash, readiness on load (Q4-Q5). This is the "not
  dead" half — a loading 503 is not a crash signal.
- "Not foreign": the loading answer arrives on `/v1/models`, the model API kama already uses
  for identity, not on an unrelated surface (Q3-Q4).

Does not support:
- Any response body. The page documents status codes only; no JSON, no `error` object, no
  `message`/`type`/`code`. A grep of the page and its raw source for
  `llama.cpp|unavailable_error|"code"` returned no matches. The C1 matcher must rest on
  llama.cpp `server-http.cpp:307-328` and README, as pinned in
  `.ufo/waves/round-16/build/advice/SourcePins.md` (README line 486; cpp 314-325).
- llama.cpp behavior. The page is vLLM-specific and never names llama.cpp; S021's tier-A
  scope is "llm-d v0.10 Kubernetes probe guidance for vLLM" (corpus/SOURCES.md:33).
- The liveness-route mapping. "Returns `200 OK` immediately when vLLM server starts" (l.127)
  is vLLM-specific; llama.cpp's `/health` is 503 while loading
  (corpus/knowledge/runtime-health-surface-matrix.md:14, corpus/SOURCES.md:6). Importing
  S021's `/health`-as-liveness mapping to llama.cpp would misclassify a loading server as dead.
- "connection refused" as a loading signal. Q4's disjunction must not be imported:
  kama-probe classifies rc=7 as `DEAD`/`connection-refused` (tools/kama-probe.sh:460-462).
  Importing it would collapse MODEL_LOADING into DEAD.
- Kubernetes probe policy. The lane's own path already says "borrow Kubernetes lifecycle
  vocabulary and llm-d's model-aware readiness without importing either into a local service"
  (corpus/SOURCES.md:50); the matrix's Kubernetes row says a local server "inherits none of
  these semantics" (runtime-health-surface-matrix.md:18).

## Flip advice: yes, conditional

`queued` → `mined` is defensible this round only as support for the lifecycle distinction,
not for C1's exact-body matcher.

All four conditions:
1. The new knowledge entry exists first and names S021 in `used-by`. Otherwise `mined` trips
   W03 (mined but unused) or E11 (missing used-by path on disk):
   scripts/sources-census.sh:559-568 (E11) and 673-674 (W03).
2. The entry's claim is scoped to: three lifecycle stages; `/health` = process liveness for
   vLLM/llm-d; `/v1/models` = model-aware readiness; 503 during load = not-ready. Give it a
   per-engine row (vLLM via S021; llama.cpp via S001, or S035 if L1 adopts the later pin) and
   say explicitly that S021 documents neither llama.cpp nor any body or error code.
3. Do not import Q4's "or connection refused"; keep DEAD as `DEAD`/`connection-refused`.
4. Cell changes: S021 `status` `queued` → `mined`; `used-by` `—` → the new entry path
   (suggested `corpus/knowledge/model-loading-readiness.md`, which does not exist yet);
   `opened` stays 2026-10-19; `recheck` stays `on-release`; the `teaches` cell already states
   the distinction and need not change; `anchor` may add "/health Endpoint, /v1/models
   Endpoint" but already lists them.

Do not flip if the entry will cite S021 for the exact "Loading model"/`unavailable_error`/
`code: 503` matcher: that text is not on the page, and the row's tier-A scope is vLLM
guidance, so the citation would be false (KQ6, corpus/QUALITY.md:28).

## URL cell (secondary)

Do not rewrite S021's `source` URL in the same pass without logging it: the round's verifier
pattern compares old rows as whole strings (corpus/lessons/round-11.md:54-63 is the precedent
for logging each old→new cell). Record the 404 and the live v0.10 view
(`https://llm-d.ai/docs/0.10/operations/readiness-probes`) in the new entry's source line and
the round Search log. If L1 does correct the cell, log old→new and pin the v0.10 versioned
URL, not the v1.0 path, so URL, `scope` ("llm-d v0.10") and `anchor` stay consistent.

## Residual unknowns

- The prose date is unknown; no rendered or frontmatter date exists, and the nearest dated
  facts are the release and the file's last commit (2026-09-21 for release-0.10).
- [INFERENCE] The v0.10 docs are generated from `release-0.10` (path and content match), but
  no build/version manifest mapping was located, so the version pin is the site label plus
  the release tag, not a doc commit.
- Whether L1 admits the new entry this round decides the flip; a re-open alone is source
  curation, not admission (round-12 lesson pattern).

## Tooling

- Installs or updates: none. Read-only fetches via `read`/`grep`, GitHub REST API; no local
  service started, no environment dump, no lane gate/harness/test run.
