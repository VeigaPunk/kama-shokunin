# ScoutK8sProbes — S017 re-open (Kubernetes probes doc)

Read-only scout, 2026-10-20. Axes: operability + calibration (calibration 7). Opened:
`https://kubernetes.io/docs/concepts/workloads/pods/probes/` (HTTP/2 200, Netlify, `date: Tue, 20 Oct 2026
13:26:45 GMT`). Page source pinned for line citations: `content/en/docs/concepts/workloads/pods/probes.md`
in `kubernetes/website` at commit `751b927b5a68…`, re-checked against `main` — every line cited below has the
same number in both (max cited line 260). Old path
`/docs/concepts/configuration/liveness-readiness-startup-probes/` still answers `HTTP/2 301`,
`location: /docs/concepts/workloads/pods/probes/` — the S017 row's canonical-URL claim holds.

## 1. Last-modified date (recorded)

- Page footer: "Last modified June 30, 2026 at 3:26 PM PST: [KEP-5999: Add docs for HTTP/2 cleartext (h2c)
  support in container probes (alpha) (751b927b5a)]" → **page-stamped last-modified = 2026-06-30**.
- Page metadata: `article:modified_time: "2026-06-30T15:26:34+05:30"` = `2026-06-30T09:56:34Z`.
- Commit `751b927b5a6869aab39fc81350f0b55b3c035216` (GitHub API): `author.date 2026-06-30T09:56:34Z`,
  `committer.date 2026-07-31T06:31:47Z` — the meta instant is exactly the author date.
- No `last-modified` HTTP response header is served; the date above is page content only.
- Freshness caveat (observed, then inferred): the body contains the KEP-4939 gRPC-TLS paragraph
  (`mode` / `InsecureSkipVerify`), added by `7099403` (author 2026-07-28) and **absent** at `751b927b`
  (grep for `TLS`/`InsecureSkipVerify` = 0 matches there; control pattern `tcpSocket` matches). The newest
  commit touching this path is merge `6a20979` (2026-08-04). The edge served a stored object
  (`cache-status: "Netlify Edge"; fwd=stale; …; stored`). [INFERENCE] Hugo's Lastmod is the *author date* of the
  newest commit touching the file ordered by commit date (`751b927b`, committer 07-31), so the stamp names the
  build's commit, not the newest content change; a rebuild after `6a20979` will likely re-stamp this page to
  2026-08-04 with no prose change. Treat 2026-06-30 as "what the page says", not "the doc's newest text".

## 2. Readiness-class sentences → MODEL_LOADING (not ready for traffic, not dead)

| Citation (URL §anchor / path:line) | Quote (≤25 words) | Work it does |
|---|---|---|
| `probes.md:70` §readiness-probe | "Readiness probes determine when a container is ready to accept traffic." | Defines the verdict's meaning: traffic admission, not survival. |
| `probes.md:71-73` §readiness-probe | "time-consuming initial tasks, such as establishing network connections, loading files, and warming caches" | Loading is named as the canonical readiness wait. |
| `probes.md:146-147` §when-should-you-use-a-readiness-probe | "an app that has failed and an app that is still processing its startup data" | **The distinction C1 needs**: failed vs still-loading are different states. |
| `probes.md:198-199` §probe-results (line-joined) | "For readiness probes, the kubelet marks the container as not ready, and the Pod stops receiving traffic from matching Services." | Failure action is *withhold traffic*, not *kill*. |
| `probes.md:260` §configure-probes (failureThreshold) | "For a failed readiness probe, the kubelet continues running the container that failed checks" | The container keeps running — MODEL_LOADING is not DEAD. |
| `probes.md:82` §readiness-probe | "Readiness probes run on the container during its whole lifecycle." | A load phase is inside the probe's normal window, not an anomaly. |
| `probes.md:33-34` §startup-probe | "Kubernetes does not execute liveness or readiness probes until the startup probe succeeds" | Startup gating: a slow load must not be scored as death. |
| `probes.md:121-124` §when-should-you-use-a-liveness-probe | "the pod is observed as not-ready for some period of time before it is hard killed" | Explicit staging: not-ready first, kill only after tolerance. |
| `probes.md:206-207` §probe-results | "For readiness probes specifically, the result is considered `Failure` before the initial delay." | Not-ready is the *default* before any success. |
| `probes.md:141-142` §when-should-you-use-a-readiness-probe (line-joined) | "This helps you avoid directing traffic to Pods that can only respond with error messages." | A 503-with-error body is a not-ready pod, not a foreign one. |

## 3. Liveness-class sentences → DEAD (restart / gone)

| Citation | Quote | Work it does |
|---|---|---|
| `probes.md:44` §liveness-probe | "Liveness probes determine when to restart a container." | Only liveness owns the restart decision. |
| `probes.md:49-50` §liveness-probe | "If a container fails its liveness probe more times than the configured tolerance, the kubelet restarts that container." | Restart requires repeated failure past tolerance. |
| `probes.md:58-59` §liveness-probe caution | "Liveness probes must be configured carefully to ensure that they truly indicate unrecoverable application failure" | Restart is reserved for unrecoverable, not transient, states. |
| `probes.md:61` §liveness-probe caution | "Incorrect implementation of liveness probes can lead to cascading failures." | Why C1 must not let a loading server read as dead/foreign. |
| `probes.md:195-196` §probe-results | "For liveness and startup probes, the kubelet kills the container" | The kill branch. |
| `probes.md:112-115` §when-should-you-use-a-liveness-probe | "able to crash on its own whenever it encounters an issue or becomes unhealthy" | Crash handling is delegated to `restartPolicy`, not to a probe. |
| `probes.md:39` §startup-probe | "If the startup probe fails, the kubelet kills the container" | The one case where load-time failure does kill — hence startup gating matters. |

## 4. Mapping table (kama ↔ doc)

| kama verdict (`tools/kama-probe.sh`) | Doc concept | Verdict on support |
|---|---|---|
| `MODEL_LOADING` (`kama-probe.sh:501-506`, `llamacpp-loading`) | Readiness Failure / startup-gated liveness | Supported as *vocabulary*: not ready, container keeps running, no restart, no foreign-service label (§2). |
| `DEAD` (`kama-probe.sh:461-468`, connect rc 6/7/28) | Liveness Failure → restart; crash → `restartPolicy` (`probes.md:112-115`) | Contrast only: DEAD is a layer *below* probes (nothing listening). [INFERENCE] the doc has no probe-visible state for "process gone". |
| `NOT_HTTP` | none | No analogue; `tcpSocket` counts an open port healthy (`probes.md:171-174`), which would erase NOT_HTTP/DEAD. Do not import. |
| `FOREIGN_SERVICE` | none | No analogue; see counterweight below. |

**Counterweight that bounds the claim.** The doc's `httpGet` rule is status-only: "The diagnostic is
considered successful if the response has a status code greater than or equal to 200 and less than 400"
(`probes.md:166-167`, line-joined). Kubernetes would therefore fail *every* non-2xx — it cannot tell
llama.cpp's loading envelope from "no slot available", a bare string error, or HTML maintenance. So S017
supports "a 503 on the model route is a failed readiness probe, not a foreign service" **as a class**, and
supports none of C1's exactness rule (`message == "Loading model"`, `type == "unavailable_error"`,
`code == 503`). That exactness — and its scope limit (`Overbroad503.json` no-slot/lowercase cases stay
`FOREIGN_SERVICE`) — remains kama's own narrowing, attributed to b11755, not to Kubernetes.

## 5. Advice for the lane

1. **S017 stays `mined`; no date edit needed.** `corpus/SOURCES.md:29` says "page modified 2026-06-30", which
   both page stamps confirm. If a content-lineage date is preferred, note 2026-07-28 (KEP-4939) and the
   pending 2026-08-04 merge (§1) — do not silently replace the stamp.
2. **Cite by section anchor, not by commit.** Use the live URL with `#readiness-probe`, `#liveness-probe`,
   `#probe-results`; a commit pin is unstable (§1). If a path:line is wanted, pin `751b927b` and say lines are
   stable through current `main`.
3. **Two load-bearing quotes are enough** for a knowledge entry: `probes.md:146-147` (failed vs still
   processing) and `probes.md:260` (readiness failure keeps the container running). Together they say
   "not-ready ≠ dead" without importing HTTP or engine semantics.
4. **Do not write "Kubernetes treats llama.cpp's 503 as not-ready".** The doc's status-only rule
   (`probes.md:166-167`) would also fail 401/403/404/500 and HTML 503s. Attribute the vocabulary, not the
   matcher.
5. **`LoadingRace.HealthAlreadyOk` is consistent with the doc's split-endpoint pattern**
   (`probes.md:121-124`, `:134-136`): readiness may be judged on a different surface than liveness, and a green
   `/health` must not override a still-loading `/v1/models`. The doc licenses "different endpoints answer
   different questions"; it does not license "open port = healthy" (`probes.md:171-174`).
6. Existing row boundary stands: the doc governs Kubernetes API behaviour and says nothing about model
   servers; `corpus/SOURCES.md:29`'s "a non-Kubernetes local server inherits none of these semantics" is
   confirmed by re-reading — no model/vendor text appears on the page.

## 6. Limitations / unresolved

- Reader returned rendered text (tooltip shortcodes expanded); every quote above was then matched verbatim
  against the pinned Markdown and `main`, and rows marked "(line-joined)" join a sentence broken across source
  lines. Line numbers are the Markdown file's.
- No LSP applies to an external doc page; the search is literal text matching. The URL-read control
  (`tcpSocket` matched, `TLS` did not at `751b927b`) rules out a silent empty read.
- Exact mechanism of the footer stamp (§1) is [INFERENCE]; only the two values and the content mismatch are
  observed.
- No lane gate, harness, probe, or test was run. No installs or upgrades were made.
