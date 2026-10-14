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
