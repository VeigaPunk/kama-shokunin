# Round 1 safety audit — kama probe

**Scope.** This is an adversarial audit of the read-only endpoint probe and its
round-1 surfaces. Claims below are grounded in the frozen L1 observations or in
commands run against the live local service; no request was state-changing.

## Secret leakage

- L1-F8 identifies the running service as `llama-server` on loopback port
  34113. A live `/proc/1299/cmdline` read produced:
  `... --chat-template-file /home/vgpnk/.config/llama/qwen-coder-godspeed.jinja ...
  --alias /scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf
  ... --model /scratch/models/qwen3-coder-30b/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf ...`.
  It contained paths and model identifiers, but no token, password, cookie, or
  authorization value. (Command: `tr '\0' ' ' </proc/1299/cmdline`.)
- A live `GET http://127.0.0.1:34113/metrics` returned `200`,
  `Content-Type: text/plain; version=0.0.4`, `Content-Length: 2612`; the body
  contained only llama.cpp counters/gauges such as
  `llamacpp:prompt_tokens_total`, `llamacpp:requests_processing`, and
  `llamacpp:n_busy_slots_per_decode`. No credential material was observed.
- The probe contract permits metadata responses only. Its output must therefore
  enforce this concrete rule: **emit only fixed verdicts, endpoint/port,
  HTTP status/content-type, and the served/expected model identifiers; never
  emit response bodies, request bodies, headers (especially `Authorization`,
  `Cookie`, and `Set-Cookie`), command lines, environment values, or raw curl
  diagnostics.** On errors, print a fixed class (`DEAD`, `NOT_HTTP`, or probe
  error), not the URL payload, headers, or body. `--json` applies the same
  allow-list; it is not a debug dump.

## Scope and authority

The round-1 write boundary is explicit in `PROVINCE.md:22-26`: kama never
writes `~/.config`, `~/.omp`, or systemd units. The probe is specified as bash,
read-only, loopback-only, and dependent on `ss`, `curl`, and coreutils; it has no
need for `sudo`, Docker-socket access, or service control. Its only permitted
scratch side effect is temporary files under `/tmp`, with cleanup. A future
implementation that invokes `systemctl`, `docker`, `sudo`, or writes an
operator-owned path violates this boundary and must be rejected rather than
made convenient.

## Contract surface and non-model ports

L1-F3 shows that `http://127.0.0.1:8080/` and
`POST http://127.0.0.1:8080/v1/chat/completions` currently reach a Jetty/Jitsi
service and return HTML `404`, not a model JSON response. The probe's endpoint
checks must use metadata-safe requests: no `Authorization` header, no cookie,
no request body, and no credentials in diagnostics. In particular, it must not
send `POST` to `/v1/chat/completions` (or any other model-generation route) when
checking a declared consumer: that would be a stateful/expensive operation on a
foreign service. A model identity check is `GET /v1/models`; liveness metadata
checks are `GET /health`, `/props`, or `/slots` only where explicitly needed.
The 8080 observation is therefore classified `FOREIGN_SERVICE` under the
binding vocabulary (2xx HTML), while the observed 404 is a probe mismatch/error,
not evidence that the model is present.

## Trust boundary and failure mode

`PROVINCE.md:22-26` is the operator-approval boundary. Round-1 artifacts may
report that `~/.config/opencode/opencode.json:158`,
`~/.config/opencode/agents/janitor.md:21`, and
`~/.local/bin/the-janitor:16-19` are stale (L1-F6/L1-F7; live command
`nl -ba /home/vgpnk/.local/bin/the-janitor` showed
`MODEL_ENDPOINT="http://127.0.0.1:8080/v1"`), but must not repoint them. The
same live scan of executable files under `~/.local/bin` found `MODEL_*` lines in
`xask`/`xask-l3` as well, but those are model-selection inputs rather than a
declared local endpoint and are not silently classified as consumers. If a
future round silently changed a consumer config or a systemd unit, it could
redirect credential-bearing traffic, break the operator's chosen service, or
create an endpoint-confusion/credential-disclosure path; blast radius includes
every invocation of that consumer and any credentials it attaches. The correct
action is to stop and request an operator decision.

The shell pin is especially consequential: `/home/vgpnk/.local/bin/the-janitor:46-47`
states that it has no cloud or model fallback. A stale 8080 pin therefore fails
closed or reaches the foreign Jetty service rather than transparently surviving
through a cascade.

## Ambiguities requiring L0 operator decision

1. **Which endpoint is authoritative?** The live model is on `127.0.0.1:34113`
   (L1-F4/L1-F5), while consumer pins still name `127.0.0.1:8080`
   (L1-F6/L1-F7 and `/home/vgpnk/.local/bin/the-janitor:19`). L0 must approve
   any repointing; detection alone is authorized.
2. **May any probe carry credentials?** Default is no credentials and no auth
   headers. If an operator later requires authenticated health checks, L0 must
   explicitly name the credential broker, header policy, redaction policy, and
   approved endpoint; kama must not discover or copy secrets itself.
3. **May non-model services be probed?** L0 must approve any endpoint outside
   the declared local model registry. The default remains GET-only metadata
   probes on loopback; no generation, mutation, or service-control request.
4. **What model identity is acceptable during a rollout?** L0 must choose the
   expected model id/alias and whether a transition window is allowed. The probe
   must report `MODEL_MISMATCH`, not guess or auto-correct.

## Residual risk

Even read-only GETs reveal local service metadata to the local process running
kama, and a foreign service can return misleading JSON. A compromised local
process with access to `/proc` or the loopback interface can observe metadata;
this audit does not claim to solve host compromise. The fixed output allow-list
limits blast radius to endpoint/model metadata and verdicts; it does not grant
kama authority to repair configuration or control services.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A42): `PROVINCE.md:22-26` at line 32 is stale (nl -ba PROVINCE.md | sed -n '22,26p;45,49p' => lines 22-26 now describe sampled health state; the write boundary is at 45-49); current anchor: `PROVINCE.md:45-49`]*

*[correction 2026-10-19 (round 10, A43): `PROVINCE.md:22-26` at line 58 is stale (nl -ba PROVINCE.md | sed -n '22,26p;45,49p' => lines 22-26 now describe sampled health state; the operator approval/write boundary is at 45-49); current anchor: `PROVINCE.md:45-49`]*
