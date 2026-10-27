## Seats by role (66 total)

| role | seats | share | axes |
|---|---:|---:|---|
| executor | 23 | 34.85% | calibration,operability |
| critic | 8 | 12.12% | calibration,operability |
| scout | 8 | 12.12% | adjacency,calibration,coverage,operability |
| reviewer | 7 | 10.61% | calibration,operability |
| mutation-tester | 6 | 9.09% | calibration,operability |
| scribe | 5 | 7.58% | calibration,operability |
| sentinel | 4 | 6.06% | calibration,operability |
| connector | 3 | 4.55% | adjacency,calibration,operability |
| simplifier | 1 | 1.52% | calibration,operability |
| revenger | 1 | 1.52% | calibration |
| **total** | **66** | 100.00% | |

## Attack share

| definition | roles | seats | share | floor | result |
|---|---|---:|---:|---:|---|
| seat item (primary) | reviewer/critic/mutation-tester | 21/66 | 31.82% | ≥25% | PASS |
| addendum §2 (extended) | reviewer/critic/mutation-tester/labrat | 21/66 | 31.82% | ≥25% | PASS |

## Route by role (live `task.agentModelOverrides`)

| role | seats | override | alias → model | fallback head | in enabledModels |
|---|---:|---|---|---|---|
| connector | 3 | `@m_antigravity` | `google-antigravity/gemini-3.8-flash:high` | `cursor/gemini-3.8-flash` | yes |
| critic | 8 | `@m_kfc` | `kimi-code/kimi-for-coding:max` | `@m_swe` | yes |
| executor | 23 | `@m_mim` | `minimax-code/MiniMax-M3.1-Flash:high` | `opencode-go/deepseek-v4.1-flash` | yes |
| mutation-tester | 6 | `@m_zfl` | `zai/glm-5.3-flash:max` | `devin/glm-5-3-flash-1m` | yes |
| revenger | 1 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |
| reviewer | 7 | `@m_zfl` | `zai/glm-5.3-flash:max` | `devin/glm-5-3-flash-1m` | yes |
| scout | 8 | `@m_kfc` | `kimi-code/kimi-for-coding:max` | `@m_swe` | yes |
| scribe | 5 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |
| sentinel | 4 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |
| simplifier | 1 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |

## Seats per model

| model | seats | share | roles |
|---|---:|---:|---|
| `minimax-code/MiniMax-M3.1-Flash:high` | 23 | 34.85% | executor 23 |
| `kimi-code/kimi-for-coding:max` | 16 | 24.24% | critic 8, scout 8 |
| `zai/glm-5.3-flash:max` | 13 | 19.70% | reviewer 7, mutation-tester 6 |
| `opencode-go/deepseek-v4.1-flash:high` | 11 | 16.67% | scribe 5, sentinel 4, revenger 1, simplifier 1 |
| `google-antigravity/gemini-3.8-flash:high` | 3 | 4.55% | connector 3 |
| **distinct models: 5** | **66** | 100.00% | |

## Checks

| check | result | detail |
|---|---|---|
| `roles.resolve` | PASS | 10/10 wave roles have an agentModelOverrides entry |
| `models.enabled` | PASS | every resolved model id is in config enabledModels (base id, effort suffix dropped) |
| `aliases.fallback` | PASS | every used alias has a retry.fallbackChains entry |
| `roles.in_policy_proposalRoles` | PASS | wave roles ⊆ proposalRoles (10 roles) |
| `roles.in_policy_lanes` | WARN | policy lanes[] enumerates 10 role ids; wave roles absent from it: ['sentinel'] (4 seats) |
| `wave.band` | PASS | 66 seats in policy band [64,128] |
| `wave.hard_ceiling` | PASS | 66 seats <= policy maxLanes 256 |
| `wave.declared_slack` | WARN | spec maxLanes=66 vs 66 items (slack 0) |
| `attack.share` | PASS | 21/66 = 31.82% >= 25% |
| `dispatch.no_model_passthrough` | PASS | model-ish keys in dispatch.json: 0 (routing is role-only) |
| `seats.agreement` | PASS | spec items 66, dispatch tasks 66, registry members 66 |
| `registry.roles_match_spec` | PASS | registry role != spec role for: none |
| `concurrency.profile_ceiling` | WARN | 66 seats in one task call vs omp-native-v1.concurrencyCeiling 32 |
| `route.l1_alias` | WARN | policy l1Alias @m_strong -> anthropic/claude-opus-5-5:max; live main -> @m_opus -> anthropic/claude-opus-5-5:high |
| `route.run9_map_equality` | PASS | live agentModelOverrides vs binding run-9 map: 18 roles compared, drift none, roles outside the map none |
