# Alias endpoint normalization

## Canonical dispatch table

The canonical unit is the global `modelRoles` alias (`m_*`). The selector is the provider/model selector after the alias is expanded. `baseURL` means an endpoint URL declared by the routing configuration itself (not a provider's private transport): none of these aliases carries one.

| alias | selector | provider class | carrying a baseURL? | source path:line |
|---|---|---|---|---|
| `m_kimi` | `cursor/kimi-k3-max:max` | remote-oauth | no | `~/.omp/agent/config.yml:21` |
| `m_dsflash` | `alibaba-token-plan/deepseek-v4.1-flash:max` | remote-token-plan | no | `~/.omp/agent/config.yml:23` |
| `m_flash` | `charm-hyper/deepseek-v4.1-flash:max` | remote-oauth | no | `~/.omp/agent/config.yml:24` |
| `m_qwen` | `alibaba-token-plan/qwen3.8-max:xhigh` | remote-token-plan | no | `~/.omp/agent/config.yml:25` |
| `m_luna` | `openai-codex/gpt-5.6-luna:low` | remote-oauth | no | `~/.omp/agent/config.yml:26` |
| `m_lunamax` | `openai-codex/gpt-6-luna:max` | remote-oauth | no | `~/.omp/agent/config.yml:27` |
| `m_daybreak` | `openai-codex/gpt-daybreak-blue-latest:max` | remote-oauth | no | `~/.omp/agent/config.yml:28` |
| `m_grok` | `xai-oauth/grok-4.5:low` | remote-oauth | no | `~/.omp/agent/config.yml:29` |
| `m_grok46` | `xai-oauth/grok-4.6:xhigh` | remote-oauth | no | `~/.omp/agent/config.yml:30` |
| `m_composer` | `cursor/composer-2.5` | remote-oauth | no | `~/.omp/agent/config.yml:31` |
| `m_astra` | `openai-codex/gpt-6-astra:max` | remote-oauth | no | `~/.omp/agent/config.yml:32` |
| `m_swe` | `devin/swe-2:max` | remote-oauth | no | `~/.omp/agent/config.yml:33` |
| `m_z53` | `zai/glm-5.3:max` | remote-oauth | no | `~/.omp/agent/config.yml:34` |
| `m_zfl` | `zai/glm-5.3-flashx:xhigh` | remote-oauth | no | `~/.omp/agent/config.yml:35` |
| `m_zflx` | `zai/glm-5.3-flashx:xhigh` | remote-oauth | no | `~/.omp/agent/config.yml:36` |
| `m_grok47` | `xai-oauth/grok-4.7:high` | remote-oauth | no | `~/.omp/agent/config.yml:37` |
| `m_sol` | `openai-codex/gpt-5.6-sol:high` | remote-oauth | no | `~/.omp/agent/config.yml:38` |
| `m_kcode` | `kimi-code/kimi-for-coding:high` | remote-oauth | no | `~/.omp/agent/config.yml:39` |
| `m_opus` | `anthropic/claude-opus-5-5:max` | remote-oauth | no | `~/.omp/agent/config.yml:40` |
| `m_opus_h` | `anthropic/claude-opus-5-5:high` | remote-oauth | no | `~/.omp/agent/config.yml:41` |
| `m_sol6` | `openai-codex/gpt-6-sol:high` | remote-oauth | no | `~/.omp/agent/config.yml:42` |
| `m_composer_h` | `xai-oauth/grok-composer-2.5-fast:high` | remote-oauth | no | `~/.omp/agent/config.yml:43` |
| `m_antigravity` | `google-antigravity/gemini-3.8-flash:high` | remote-oauth | no | `~/.omp/agent/config.yml:44` |

**Loopback answer (2026-09-28): no.** The required metadata-only search was:

```text
$ grep -nE "(baseURL|baseUrl|endpoint):[[:space:]]*https?://(127\\.0\\.0\\.1|localhost)(:|/)" ~/.omp/agent/config.yml /tmp/fleet-override.yml ~/Projects/ufo-fsd-alpha/.omp/config.yml ~/Projects/ufo-fsd-alpha/config/*.yml 2>/dev/null
```

Output: no matching lines (empty output, exit status 1). Therefore no alias in the merged/overlay routing configs carries a loopback baseURL. This is about dispatch aliases; the separate local llama-server endpoint is not an alias route.

*2026-10-14 errata:* re-measured at the relocated tree `~/Projects/ufo-fsd-alpha` (HEAD `964f443e`) — same empty result. `/tmp/fleet-override.yml` no longer exists; `~/.omp/agent/config.yml` still has no loopback baseURL (its `auth.broker.url` is also gone).

## Normalization and precedence

1. Read `modelRoles` from the global config as the alias registry; retain one row per alias and preserve its selector verbatim.
2. Apply the mission route bucket from `MISSION.md:37-43` and the kama route map at `kama-round-1.md:7`: role classes select `@m_*` aliases, but neither file defines a second selector or endpoint.
3. Apply `/tmp/fleet-override.yml` as the dispatch-time `--config` overlay. It repeats role-to-alias assignments only; it does not redefine `modelRoles`, so it adds no alias rows and no baseURL.
4. Apply the project config and mission overlays at dispatch precedence for their own keys. `config/mission-nightcall.yml:4-5` explicitly says model delegation resolves through the global `m_*` table and carries no project route pins (re-measured 2026-10-14); `config/l1-max-context.yml:19-22` is context policy only. The project `.omp/config.yml` likewise contains no model alias table.
5. When an alias or assignment is repeated, collapse it to the effective highest-precedence value (overlay/`--config` over global for keys it actually defines); identical repeats are one row. No credential or token values are copied.

## Residual risk and detection

A future change that adds a `baseURL`/`baseUrl` to a global `modelRoles` selector, or adds a new `m_*` selector whose provider is configured to a loopback URL, would put fleet dispatch on kama's local-serving surface. A future overlay could also redirect a role directly to such an alias if it begins defining `modelRoles`.

Kama should detect this in two layers: (1) rerun the loopback grep above against global, `--config`, project, and mission-overlay files and fail freshness review on any match; (2) run `tools/kama-probe.sh check --json` against `registry/endpoint-consumers.tsv` and treat `MODEL_OK`/`MODEL_MISMATCH` at the declared local endpoint as the only accepted local-model evidence, while classifying foreign/dead/unauthorized endpoints with the binding verdict vocabulary.
The route census also found a non-alias consumer pin: `~/.local/bin/the-janitor:16-19` sets `MODEL_PROVIDER="qwen-local"`, the expected model id, and `MODEL_ENDPOINT="http://127.0.0.1:8080/v1"`. This is a consumer of the local surface, not a dispatch alias; it must remain covered by the endpoint-consumer registry. `~/.config/opencode/agents/distiller.md:5-8` pins the same qwen-local model but has an explicit cloud cascade, so it is cascade-protected rather than proof that an alias carries a loopback URL.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A16): `MISSION.md:37-43` at line 46 is stale (nl -ba /home/vgpnk/Projects/shokunin/MISSION.md | sed -n '37,43p'; test ! -e /home/vgpnk/Projects/shokunin/kama-round-1.md && printf 'kama-round-1.md missing at fleet root\n'; test ! -e /home/vgpnk/Projects/shokunin/kama-shokunin/kama-round-1.md && printf 'kama-round-1.md missing at kama checkout\n' => MISSION 37-43 is the axes framework and no kama-round-1.md exists at either checked root); the companion `kama-round-1.md:7` anchor is also absent; current route semantics are in fleet-root `../MISSION.md:11-15`, which says routes resolve via the host model route table, not role-to-@m_* aliases; current anchor: `../MISSION.md:11-15` (fleet-root MISSION.md, resolved from the lane main checkout)]*

*[correction 2026-10-19 (round 10, A17): `/tmp/fleet-override.yml` at line 47 is stale (test -e /tmp/fleet-override.yml && printf 'overlay present\n' || printf 'overlay missing\n' => overlay missing, also recorded at line 41); current anchor: `none — dead surface`]*

*[correction 2026-10-19 (round 10, A18): `config/l1-max-context.yml:19-22` at line 48 is stale (wc -l /home/vgpnk/Projects/ufo-fsd-alpha/config/l1-max-context.yml => 20 lines: the relative path resolves under ~/Projects/ufo-fsd-alpha and the cited range runs past EOF; shape-only check, content not re-read); current anchor: `~/Projects/ufo-fsd-alpha/config/l1-max-context.yml:19-20` (range clipped to EOF, content unverified this round)]*

## Provenance supplement — round 11 (2026-10-19)

source: retained in-repo history only — the underlying host surface `~/.omp/agent/config.yml:21-44` is not retained in this repository and was not re-read in round 11; retained evidence: this file's own frozen 23-row alias table (host config read 2026-09-28; the loopback question re-measured 2026-10-14 at the relocated tree, same empty result, `/tmp/fleet-override.yml` gone), preserved byte-for-byte by this append; `LOG.md:77-80` (round-1 peer ledger: `KamaDistillerAliases` alias→endpoint normalization — no alias resolves to loopback; the `m_flash` route was caught stale); `corpus/lessons/round-1.md:3-4,70-72` and `corpus/lessons/round-1-citations.md:17,28` (F11 re-derivation: live line 24 is `charm-hyper/deepseek-v4.1-flash:max`); `corpus/lessons/round-4-recensus.md:79` (round-10 A48 re-anchor to this file's line 11); appended corrections A16–A18 with ledger `.ufo/round-10/audit/stale-anchors.tsv:16-18` (2026-10-19); file history commits `c6199a2` (round 1, 2026-09-28, table already 23 rows), `ea72c3e` (round 3 errata, 2026-10-14 — relocated the recorded grep paths from `~/Projects/origin-work/ufo-fsd-alpha` to `~/Projects/ufo-fsd-alpha`, dropped "today" from the answer sentence, added the errata line), `1e41928` (round 10, 2026-10-19 — appended A16–A18 only).
verified-at: original observations 2026-09-28 and 2026-10-14, with 2026-10-19 anchor corrections; metadata review 2026-10-20 only. Retained bytes and in-repo pointers reviewed; host routing config, environment, endpoints, listeners and dispatch surfaces were not inspected. The original 7595-byte prefix is pinned by `.ufo/waves/round-11/legacy-baseline.json`; no live revalidation is claimed and no observation is refreshed.
recheck: on a future authorized correction round, `bash tools/kama-probe.sh check --json` reconciles only declared registered identifiers; it does not establish inference readiness. Alias-row and loopback-baseURL re-derivation belongs to operator/kumitate with approved shape-only tooling; credential-bearing routing config bodies are not read here. Local metadata checks may establish only existence/size/mtime of named artifacts, never their effective route or endpoint health. No such host or endpoint check was run in round 11.

*[provenance supplement appended 2026-10-20 (round-11 wave; steered label 2026-10-19): no byte above is rewritten and no observation above is refreshed by this supplement.]*
