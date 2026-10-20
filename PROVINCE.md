# kama-shokunin — Province

**Domain:** local model serving & endpoint health — local LLM endpoints, baseURL
drift, served-model reconciliation, probe conventions.

**Owns (surfaces):**

| Surface | Concrete artifact on this box |
|---|---|
| producer discovery & read-only service inspection of local serving ports | `tools/kama-probe.sh listeners` (`ss -ltn` loopback enumeration + per-listener classification). The serving unit formerly pinned here — `~/.config/systemd/user/qwen-coder.service` (llama-server, `127.0.0.1:34113`) — is deleted; row-absent since snapshot `20261014T124232Z` (`registry/history/DELTA.md:20`). kama governs discovering whatever serves these ports and never claims an installed server |
| baseURL pins in surviving/loadable consumers | the three surviving registry rows in `registry/endpoint-consumers.tsv`: `~/.local/bin/omp` (`LLAMA_CPP_BASE_URL` fallback → `http://127.0.0.1:8080`, `file_match=inherited`, not proof of an effective environment-selected endpoint), `$UFO_SRC/config/the-tick.machine.json:16`, `$UFO_SRC/scripts/local-helper.mjs:8`. Historical, no longer live pins: `~/.config/opencode/opencode.json:158` (the provider block was removed; the file is now 5 lines holding `$schema`/`theme`/`autoupdate` only) and `~/.config/opencode/agents/janitor.md:21` (file deleted); both verified by read-only host inspection, never rewritten |
| served-model-id reconciliation | `GET /v1/models` vs `--alias` vs the configured model id |
| liveness/readiness probe conventions | `/health`, `/props`, `/slots` |
| endpoint-drift detection + invocation history | `tools/kama-probe.sh snapshot`, `registry/endpoint-consumers.tsv`, `registry/history/{latest.tsv,DELTA.md}` |
| endpoint-consumers cross-lane registry | `corpus/knowledge/consumer-registry.md`, `cross-lane-scope.md` |

**Observed state (lane baseline `c390918`, tracked snapshot `20261014T124232Z`):**
`bash tools/kama-probe.sh check` evaluates 3 registry rows — `model_ok=0`, `drift=3`,
exit 2; every row in `registry/history/latest.tsv` is `DEAD` connection-refused
(`8080` and `34113`). `ufo-fsd-thetick` and `ufo-fsd-local-helper` are
correct-pin/dead-endpoint: `file_match=yes` attests the pin, NOT a live `MODEL_OK` —
this lane reports pin correctness and serving liveness separately and never asserts
`MODEL_OK` from retired samples (`registry/history/DELTA.md:9,:12,:20` keep the former
`MODEL_OK`/`systemd-qwen-coder` state as history). Serving runtime is explicitly
unavailable on the concrete surfaces — nothing listens on `8080` or `34113` (probe
connection-refused verdicts; `systemctl --user status qwen-coder` → "Unit
qwen-coder.service could not be found"); restoring a unit is operator-owned work under the
boundary below. The outage retires nothing in this domain: server/health discovery and
drift reconciliation remain governed here — province contraction is an L0 decision.

**Actual round-5 sample (2026-10-15):** the same three rows still sample
`DEAD` / connection-refused, exit 2. Explicit UFO pins resolve `file_match=yes`;
the builtin fallback is `inherited`/`raw`, not proof of an effective runtime
URL or active traffic. Bounded service/socket metadata agrees with the
not-found producer and unserved registered ports. Full command evidence:
`.ufo/round-5/{before-check,host-shape,acceptance}.json`. This supersedes a
current-readiness reading of older successful examples without retiring the
producer-discovery domain or authorizing service restoration.

**Refuses:** model quality/eval (kengaku), credential material & auth flows (kagi),
dispatch/route mechanism (kumitate), remote web surfaces (kake). Boundary rule: kama
answers *"is the thing at this baseURL the model this config believes it is, right
now"* — never *"is the model good"* or *"is the request safe"*.

**Write boundary (hard):** kama never writes to `~/.config`, `~/.omp`, or systemd
units. Those are operator-owned; kama *detects and reports* stale pins, and the
operator repoints them. Rationale: a lane that silently repoints a credential-bearing
consumer config would be acting outside its authority (see
`corpus/lessons/round-1-safety.md`).

**Out of province → report, never absorb.** Anything found outside the domain is
named in the round report for the owning lane (see
`corpus/knowledge/cross-lane-scope.md`).

**Round-16 note — lane-owned live fixture (2026-10-20).** `tools/kama-llamacpp-live.py`
starts one llama-server child (official release b11755, installed by the
operator-authorized tooling directive at `~/.local/opt/llama-b11755`, linked
`~/.local/bin/llama-server`) with a pinned 1.2 MB GGUF kept in the lane-owned
cache `~/.cache/kama-shokunin/`, on a free loopback port that is never a
registered consumer port or a listening port, and tears it down in the same run.
This proposes narrowing round 1's "L0 must approve any endpoint outside the
declared local model registry" only for the process this tool started, **pending
L0 ratification** (`.ufo/l0-questions.md`, kama round-16); any other unregistered
endpoint still needs L0. It is not service restoration, starts no unit, writes
nothing under `~/.config`, `~/.omp` or systemd, and changes no registered row:
the three consumers stay `DEAD`. The release is a GitHub Pre-release; the
install is identified by its asset digest (S038), not the tag. The install tree,
its `~/.local/bin/llama-server` link (which now precedes `/usr/bin` on PATH) and
the cache persist on the host; removal is the operator's call.
**Round-17 note — the same fixture, stricter receipt (2026-10-20).** The lane-owned
child is unchanged in scope (same install, same pinned GGUF, unregistered
loopback ports, torn down in the run) and still **pending L0 ratification**. The
tool now emits `kama-llamacpp-live/v2`: exact ready body, harness-SIGTERM
graceful teardown with returncode 0, ownership-gated port closure, every loading
503 graded, a receipt on internal faults, and loopback-only listener ownership.
Fake-server controls run only `/tmp` fakes on ephemeral loopback ports. No
`/usr/bin/llama-server` exists, so the `~/.local/bin` link shadows nothing; the
"precedes `/usr/bin` on PATH" wording above is shell-local. The retained release
archive `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (sha256 `753bfa73…e226`)
is part of the operator-owned footprint.
