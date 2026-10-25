## Gate

Draft only. This file is not `corpus/lessons/round-35.md`. That lesson was not
edited. No row was appended to `corpus/SOURCES.md` by this seat. The staged
package under `/home/vgpnk/Projects/shokuknow/merge/kama/` was read, not written.
Quarantine rows were not hand-checked here. `considerthese/` was not edited.
Neither frozen predicate was changed.

Admit rule: a lane-written `corpus/knowledge/endpoint-health-probe-conventions.md`
is admitted only if a seat located a quote. The condition is met by this seat
(ScribeGate), which re-opened the pages below on 2026-10-24 (local clock;
fetches saved 21:24 -0300, UTC date 2026-10-25). It is not met by any other
seat. At 2026-10-24T21:28:36-0300 the quote-location reports
`ScoutProbeEntry.md`, `ScoutVllm503.md`, `ScoutDockerHc.md`, and
`ScoutHostedReject.md` were absent. Their prompts are not evidence. If the
quotes below are struck, the admit does not hold.

### Admit

| candidate | why admitted | located quote | words | re-open |
|---|---|---|---|---|
| lane-written `corpus/knowledge/endpoint-health-probe-conventions.md` | a health-probe signal, or an engine admission status, is not the same fact as a remote platform health route. Condition: a seat located a quote. Met by ScribeGate. | When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance. | 20 | https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/ heading EngineArgs → SchedulerConfig → `--max-num-queued-reqs`. Saved body `fetch/vllm-engine-args.html`. `grep -c 'rejected with HTTP 503'` = 2. |

Same page, `--max-num-queued-tokens`: "When the limit is reached, new requests
are rejected with HTTP 503." (12 words). Same admission status, second cap.
Not a second probe convention.

Further quotes this seat located. They satisfy the same admit rule. They are
not in the committed entry (that file says they were not re-opened into it).
This draft does not add them to the corpus.

| staged label (not an append) | source re-opened | heading located | quote | words | saved-body count |
|---|---|---|---|---|---|
| S333 | https://docs.docker.com/reference/dockerfile/ | `HEALTHCHECK` (`id=healthcheck`) | After a certain number of consecutive failures, it becomes unhealthy. | 10 | `unhealthy` = 3 |
| S333 | same | `HEALTHCHECK` | Probe failure during that period will not be counted towards the maximum number of retries. | 15 | same body |
| S332 | https://docs.docker.com/reference/compose-file/services/ | `depends_on` long syntax | Specifies that a dependency is expected to be "healthy" (as indicated by healthcheck) before starting a dependent service. | 18 | `service_healthy` = 5 |
| S332 | same | `depends_on` short syntax | With short syntax, Compose does not wait for dependency services to be "healthy" before starting a dependent service. | 18 | same body |
| S334 | https://raw.githubusercontent.com/prometheus/blackbox_exporter/8eff0fc90e725fc7325186a530d3252507b032ca/README.md | `## Running this software` → `### Checking the results`. Staged label `§Probing` is not in this README. | The `probe_success` metric indicates if the probe succeeded. | 8 | `probe_success` = 1 |
| S331 | https://llm-d.ai/docs/dev/architecture/model-servers/sglang | `Health Checks` (`id=health-checks`). Staged label `§Health endpoints` is not the heading. | Liveness: GET /health — confirms the SGLang server process is alive. | 10 | `Readiness` = 1 |

What the admitted entry may say from the quote that is already in the committed
file, and only as that contrast:

- The vLLM 503 sentence is an API-server admission rejection when
  `--max-num-queued-reqs` is reached. It is not a health-route death and not a
  statement that a process on this host is down.
- It does not replace `corpus/knowledge/runtime-health-surface-matrix.md:15`
  (vLLM `GET /health` returns 503 only on `EngineDeadError`, S002/S004). That
  is a different page and a different surface.
- It does not repeat llama.cpp loading-503 as new ground.
- `corpus/knowledge/served-model-id-resolution.md:39-46` already narrates a
  `/health` EngineDeadError 503 versus a `/v1/chat/completions` admission-rejection
  503, and says no new row was opened for the handler already held as S004.
  That paragraph limits novelty of the distinction. It does not contain the
  engine-args sentence located above. S327 is that other URL.

What this seat does not admit from the staged blob:

- The paraphrase that a long-loading model must not be declared unhealthy
  merely for being slow to start. The located sentence is the start-period
  retry rule, not that model claim.
- "one `probe_success` metric per target and module." Not in the opened README.
  `http_2xx` appears only as a query parameter in an example URL.
- The llm-d readiness item that maps `GET /health_generate` to readiness. The
  matrix already excludes that route from kama probes because it is a
  generation request. Do not admit it as a probe this lane may send.
- A byte-copy of the staged file. Two staged section labels were not on the
  pages (`§Probing`, `§Health endpoints`).

Observation, not this seat's write: at HEAD `82886c28f7da564a706bb4385b45b72d49b49bcb`
the lane file exists, cites S327, and `corpus/SOURCES.md:213` is an S327 row
whose quote cell is the 20-word sentence above. `corpus/README.md` has
`## Coverage map — round 35 addition` naming the entry once. This seat did not
write those paths and did not commit. C2 against that tip read
`named 1 file_exists 1 cited_row 1 met True` (exit 0). Against base
`719655f12517a9ce6b1a5ca44316897fed8420b0` it read
`named 0 file_exists 0 cited_row 0 met False` (exit 1). The predicate is
unchanged. This draft is not what met the counter.

### Reject

| candidate | reason | flip |
|---|---|---|
| `corpus/knowledge/hosted-health-route-configuration.md` | remote platform health (kake). Absent at HEAD `82886c28f7da564a706bb4385b45b72d49b49bcb` (`git cat-file -e` exit 128). This seat re-opened the three staged URLs. S346 locates `serving_container_health_route="/ping"` inside `aiplatform.Model.upload`. S349 locates `serving_container_health_route="/health"` and `serving_container_predict_route="/v1/completions"` inside `upload_model_gpu`. S350, heading `預設健康狀態檢查`, locates `containerSpec.healthRoute` and `AIP_HEALTH_ROUTE` as the path Agent Platform GETs on a deployed container. Those are hosted deployment fields, not a local probe convention. kama `PROVINCE.md` refuses remote web surfaces (kake). kake `PROVINCE.md` adjacent line: "kama owns local model-serving endpoints; kake owns remote web properties." | Admit only if both hold: (1) a seat locates a quote that a local probe on this host, or a local container the lane probe observes, must request that configured path; (2) `PROVINCE.md` and `corpus/README.md:64` no longer assign that surface away from kama. A cloud vendor guide does not meet (1). Neither clause holds. Do not append S346, S349, or S350. |
| staged `endpoint-health-probe-conventions.md` as a byte-copy | heading labels `§Probing` and `§Health endpoints` were not on the opened pages, and the file's novelty sentence is broader than the quotes located here. The committed entry already excludes Docker, Compose, llm-d, and blackbox. | Copy only a sentence whose quote this seat, or a later seat, located. Do not copy the staged file. |

### Conflict for the L1 (not resolved here)

`corpus/README.md:64`: "No coverage of *remote* endpoint health (that is kake/kumitate territory)."

kama `PROVINCE.md` refuses "remote web surfaces (kake)" and "dispatch/route mechanism (kumitate)".

kumitate `PROVINCE.md`: "Local model serving and endpoints → kama."

This draft follows the assigned reject label, remote platform health (kake). It does not reassign the README split.

`corpus/lessons/round-35.md` Gate, not edited, conflicts with this seat's count and with the re-opens above. Verbatim in the seat report. Predicates unchanged.

`MISSION.md:29` still says operability + freshness. This seat is judged on coverage. `MISSION.md` was not edited. The conflict is named and does not change either predicate.
