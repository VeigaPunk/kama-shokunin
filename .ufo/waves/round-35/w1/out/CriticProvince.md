# CriticProvince — do not admit hosted-health-route-configuration.md

Judged axis: adjacency. Seat did not write the entry, did not edit `PROVINCE.md`, `corpus/README.md`, or `corpus/SOURCES.md`, and did not install tools.

Verdict: **reject**. The file is out of province. The in-province hook is real and still loses. A kake-only handoff is a false deed.

## Counterexample

Admitting the staged file freezes this sentence as kama ground:

> the same vLLM image that answers `/health` locally is probed at `/ping` when it is deployed on that platform.

Re-opened on 2026-10-24, the English twin of the page the entry cites for `/ping` (`https://docs.cloud.google.com/vertex-ai/generative-ai/docs/open-models/vllm/use-vllm?hl=en`, same upload snippet as the Japanese page) contains `serving_container_health_route = "/ping"` and `serving_container_predict_route = "/generate"`. Stripped text count of `/health` on that page: **0**. It does not say the image answers `/health`, and it does not say the image answers `/ping`. It sets a field of a remote `Model.upload` spec.

The client of that field is named on the requirements page fetched the same day (`https://docs.cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements?hl=en`). Stripped text contains, as consecutive phrases:

- `containerSpec.healthRoute`
- `AIP_HEALTH_ROUTE`
- `This variables specifies the HTTP path on the container that Agent Platform sends health checks to.`
- `stops routing inference traffic to the container`
- `Agent Platform doesn't restart the container`
- `503 Service Unavailable`
- `The contents of the response body don't matter`

The same page's liveness section says the platform's **TCP liveness probe** restarts the container (`Agent Platform restarts your container`) and that the HTTP server needs no special behavior for that probe. The staged entry's restart split — container `HEALTHCHECK` versus platform probe — is not the split the page states. Both instruments on that page are the platform's. Admitting the file would hold a mis-assigned restart actor.

The entry's own limit already gives the counterexample to ownership: "The platform that probes the container is the only authority on which route it will use" and "no endpoint was probed." An authority that is only the remote platform is not a path `tools/kama-probe.sh` must hit.

## Strongest out-of-province case

The subject is a remote platform probe client and its traffic policy, not a local engine route.

1. **Lane contract already refuses it.** `PROVINCE.md:3` is local model serving and endpoint health. `PROVINCE.md:13` owns liveness/readiness probe conventions as `/health`, `/props`, `/slots`. `PROVINCE.md:40-43` refuses dispatch/route mechanism (kumitate) and remote web surfaces (kake), and limits the question to whether the thing at this baseURL is the model this config believes it is, right now. `corpus/README.md:64` already records: "No coverage of *remote* endpoint health (that is kake/kumitate territory)."
2. **The probe this lane runs cannot be renamed by that field.** `tools/kama-probe.sh:2` is a loopback probe. It calls `probe_short` on `"/health"` (`tools/kama-probe.sh:508`, `:545`). `tools/kama-llamacpp-live.py` likewise GETs `/health`. A Vertex `serving_container_health_route` does not change those calls.
3. **The page's operative facts are platform policy.** Configurable path, 200-within-10-seconds with body ignored, non-200 (503 is the example) or silence means unhealthy, up to 3 extra checks at 10-second intervals, four consecutive unhealthy responses stop inference routing, HTTP health check does not restart, TCP liveness probe does. That is who receives traffic on a managed endpoint. `corpus/knowledge/runtime-health-surface-matrix.md:22` already assigns "Routing/gateway health dispatch" to kumitate and says Kubernetes probe categories are borrowed vocabulary, not a policy this lane applies.
4. **Held precedent stops at vocabulary.** `corpus/SOURCES.md` S040 (llm-d) is mined only as "process liveness on `/health` versus model-aware `/v1/models`," used by `llamacpp-loading-lifecycle.md`, which says S040 does not support the llama.cpp body. That is the lawful use of a platform probe page. The staged file goes past it into deploy-spec fields and routing-stop rules.
5. **Admitting the file imports a package, not a sentence.** The staged tree also holds five amendments (SageMaker fixed `/ping`, Azure Container Apps, Azure ML three-route contract). The 2026-10-24 r7 amendment says the base entry is one "which the lane already holds." The lane file is absent (`test -e corpus/knowledge/hosted-health-route-configuration.md` → ABSENT). Admitting the base file would bless a false "already held" provenance and a second-platform saturation the lane has not hand-checked. S346, S349, and S350 are not in `corpus/SOURCES.md` (`grep -c` of those id cells → 0).

### The kake label is the defective part of the reject

"Remote platform; kake" is the right reject and the wrong owner.

- `kake-shokunin/PROVINCE.md:3` is web properties and publishing (ds4cc.com, kimi.page, Pages deploys). `PROVINCE.md:41` says kama owns local model-serving endpoints and kake owns remote web properties. Vertex / Agent Platform model deploy is not that surface.
- Kake does hold the *shape* for its own property: `kake-shokunin/corpus/knowledge/render-web-services.md:35` ("Web services can receive health checks as HTTP GET requests to a path you specify"). That is Render `healthCheckPath` on a publishing deploy, not a deed to Google model-container health routes.
- Kumitate holds platform-polled probe vocabulary (`corpus/knowledge/worker-heartbeat-liveness.md`, S119: kubelet probes, remedy is restart) and is the lane `runtime-health-surface-matrix.md:22` names for routing/gateway health dispatch. It does not hold this Vertex page either. `PROVINCE.md` there still refuses local model serving back to kama.

`corpus/README.md:64`'s "kake/kumitate territory" is a shrug, not a transfer. Reporting the page out is required. Absorbing it into kake, or into kumitate, from this seat would be a second false provenance. Out of province means do not write it here. It does not mean another lane already owns the bytes.

## Strongest in-province case

A platform can configure a path other than the engine default, so a probe that hardcodes the engine route can miss a live server.

Re-opened 2026-10-24, two guides set the same field to different values:

| Page fetched | `serving_container_health_route` | `serving_container_predict_route` |
|---|---|---|
| use-vllm, `hl=en` and `hl=ja` | `"/ping"` (2 occurrences each) | `"/generate"` |
| deploy-custom-vllm, `hl=en` and `hl=ja` | `"/health"` (3 occurrences each) | `"/v1/completions"` |

The requirements page tells the container to read `AIP_HEALTH_ROUTE` and to answer that path. Its env table default is not an engine route: `` `/v1/endpoints/<ENDPOINT>/deployedModels/<DEPLOYED_MODEL>` ``, and the description cell says that variable is the HTTP path Agent Platform sends health checks to. A custom server that only binds the engine's `/health` can fail the platform's probe, or can 404 a client that still uses the engine path, while the process is up.

That is a probe-convention hazard, and it is why this round's theme separates an engine route from a platform deployment. `PROVINCE.md:13` does own probe conventions. `runtime-health-surface-matrix.md` already says one `/health` shape is not portable across engines. A renamed path is a further non-portability: the route a probe must hit may not be the route the engine documents. If a process this lane is allowed to probe honored that override, hardcoding `/health` would grade a live server `DEAD` or foreign. That sentence, and only that sentence, is the in-province case.

## Why that case still loses

It is a consequence for a probe client, not ownership of the deployment spec.

- The entry concedes the authority: the platform is "the only authority on which route it will use." The rename is performed by `containerSpec.healthRoute` / `serving_container_health_route`, which the requirements page defines as the path **Agent Platform sends** checks to. It is not an engine flag `kama-probe.sh` reads.
- No loopback consumer, and not the lane-owned llama-server fixture, is shown to honor `AIP_HEALTH_ROUTE`. The entry says no endpoint was probed. The in-province harm is hypothetical for this host.
- The useful sentence is not separable inside this file. The file also holds the 10-second window, body-ignored 200, 503-as-example, three retries, stop-routing, and the no-restart claim. Those are the out-of-province payload. Keeping the file to save the rename observation harms adjacency and does not move the frozen C2 target, which names `knowledge/endpoint-health-probe-conventions.md`, not this file.
- Two guide values are not a local convention. The requirements-page default is a third path (`/v1/endpoints/.../deployedModels/...`). The entry's "one platform, one field, two documented values" understates the same document family. The r7 amendment then generalizes to Azure ML ports and routes. That is premature saturation.
- Duplicate authority if both this file and a probe-conventions entry are admitted: two owners for "what path a health signal names." The round theme is the distinction. Admitting this file collapses it.
- Identity change: lane `/health` today means the engine liveness route a loopback probe hits (`endpoint-identity.md` liveness row; probe and live-fixture GETs). The staged sentence would make `/health` "whatever a cloud spec named, or not, depending on the guide." That is the collapse the counterexample catches, and the use-vllm page does not support it.

Fixable defect versus tradeoff the L1 must reject: the kake-only label is fixable in the reject wording. Admitting the file in order to keep the rename observation is not a fixable wording defect. It trades adjacency away for a fact whose client is another actor. Per-axis, adjacency must reject that trade. Coverage must not accept this path as a substitute for the C2 entry.

## Reject reason

Remote platform health-route configuration. The sources are Google Cloud / Agent Platform deployment guides. They name the path the platform probes, the status and timing it treats as healthy, and when it stops routing inference traffic. That is not a local engine route and not a path this lane's loopback probe must hit. `corpus/README.md:64` already leaves remote endpoint health uncovered. Do not write `corpus/knowledge/hosted-health-route-configuration.md` or its amendments into the lane. Do not append S346, S349, or S350.

Do not record the reject as "owned by kake." Kake owns remote web properties and a Render health-path note for those properties. Kumitate owns route/dispatch and platform-polled liveness vocabulary. Neither `PROVINCE.md` deeds this Vertex page. Report the page out. Do not absorb it.

## Flip condition

Flip the **file** only if L0 reassigns province so kama owns remote model-platform health-route configuration, and kake and kumitate `PROVINCE.md` files release that surface. This seat cannot make that edit. A relabel to kake is not a flip.

Flip a **narrower sentence** — not this file — only when all of these hold:

1. A re-opened first-party page shows a process this lane may probe on loopback (lane-owned llama-server fixture, or an installed local engine) reads a health-path override and will not answer its documented default.
2. The override is an engine flag or environment variable that process honors, not `serving_container_health_route` / `containerSpec.healthRoute` as a field a remote platform probes.
3. The sentence cites an S-id already present in `corpus/SOURCES.md` after a hand-check. It does not include the platform retry count, 10-second window, body-ignored rule, stop-routing rule, or restart rule.
4. `hosted-health-route-configuration.md` and the amendment chain stay out of `corpus/knowledge/`.
5. `PROVINCE.md` and `corpus/README.md:64` are not quietly rewritten to make the remote page in-province. That remains the L0 flip above.

Until then the rename observation stays a reported-out limit, not held ground. "A deployment guide was worth opening" is not an admit.

## Evidence

Commands run against the lane, read-only except this report:

```
test -e corpus/knowledge/hosted-health-route-configuration.md
# ABSENT
# staged path PRESENT:
# /home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/hosted-health-route-configuration.md
grep -c -E '^\| S346 \||^\| S349 \||^\| S350 \|' corpus/SOURCES.md
# 0
nl -ba corpus/README.md | sed -n '64p'
# 64  - No coverage of *remote* endpoint health (that is kake/kumitate territory).
nl -ba PROVINCE.md | sed -n '3p;13p;40,43p'
nl -ba tools/kama-probe.sh | sed -n '2p;508p;545p'
```

Sibling reads (not edited): `kake-shokunin/PROVINCE.md:3,41`; `kake-shokunin/corpus/knowledge/render-web-services.md:35`; `kumitate-shokunin/PROVINCE.md` adjacent band (local model serving → kama); `kumitate-shokunin/corpus/knowledge/worker-heartbeat-liveness.md` S119 row.

Fetches, 2026-10-24, public docs only, no endpoint-admin state:

- `https://docs.cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements?hl=en` — health-check and `AIP_HEALTH_ROUTE` phrases above; TCP liveness restarts, HTTP health check does not.
- `https://docs.cloud.google.com/vertex-ai/generative-ai/docs/open-models/vllm/use-vllm?hl=en` and `?hl=ja` — `serving_container_health_route = "/ping"`; en stripped text has zero `/health`.
- `https://docs.cloud.google.com/vertex-ai/generative-ai/docs/open-models/deploy-custom-vllm?hl=en` and `?hl=ja` — `serving_container_health_route = "/health"`, predict route `"/v1/completions"`.

The Chinese S350 quote in the staged file was not re-fetched. The English requirements page is the same contract family and is what this reject relies on. Quote-audit of the zh-tw row is not this seat's admit path.

## Impacted axes

- **Adjacency (reject):** writing the file into kama absorbs a remote platform probe contract. Handing it to kake as if kake owned it is a false sibling deed. Both fail this axis.
- **Coverage (do not use):** C2 names `knowledge/endpoint-health-probe-conventions.md`. This path must not be substituted for that name, and must not be cited as new local probe ground. The lane already holds non-portable `/health` as documentation (`runtime-health-surface-matrix.md`) and S040 as a limit.
- **Calibration (harmed if admitted as written):** the "image answers `/health`, probed at `/ping`" sentence is not on the re-opened use-vllm page. The restart actor in the staged prose is not the page's TCP-versus-HTTP split. The amendment's "lane already holds" line is false at this tree.

No axis improves by admitting the file. The kake-label correction improves adjacency and harms none, because it does not add a corpus entry.

## Smallest safe correction

In the gate, reject `hosted-health-route-configuration.md` with the reject reason and flip condition above. Do not copy the file. Do not append S346/S349/S350. Do not name kake as the owner of the page.

If a lane-written probe-conventions note is admitted on other grounds, it may say only this, with no Vertex S-id: a remote platform health-route field is not the engine route and is not a path `kama-probe.sh` hits. That sentence is a boundary, not a substitute for this file, and it is not required to satisfy this reject.
