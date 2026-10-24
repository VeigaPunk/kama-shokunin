<!-- WAVE-CENSUS:BEGIN -->
| seat | role | report returned | report bytes | seat log bytes | first line of the report |
|---|---|---|---|---|---|
| ExecCapabilityAudit | executor | no | 0 | 29546 | - |
| ExecGatePopulation | executor | yes | 3872 | 2443 | # ExecGatePopulation — round 34, wave 1 |
| ExecRegistryRows | executor | no | 0 | 36886 | - |
| ExecIdCollision | executor | yes | 2443 | 24926 | # Item-10 ID collision check — round 34, W1 |
| ExecTransformAppend | executor | no | 0 | 32532 | - |
| ScribeLesson | scribe | no | 0 | 34468 | - |
| ScribeSourcesRows | scribe | no | 0 | 19907 | - |
| ScribeScorecard | scribe | yes | 9248 | 62684 | # ScribeScorecard — round 34, wave 1 |
| ScoutCanonicalCaps | scout | no | 0 | 44864 | - |
| ScoutAliasContract | scout | no | 0 | 48318 | - |
| ScoutServedIdResolution | scout | no | 0 | 2846 | - |
| ScoutR7Amendment | scout | no | 0 | 6289 | - |
| ScoutCoverageMap | scout | no | 0 | 62579 | - |
| ScoutAbsenceRegister | scout | no | 0 | 4602 | - |
| ConnSiblingScope | connector | no | 0 | 33435 | - |
| ConnSeparability | connector | no | 0 | 20541 | - |
| ConnRouteTable | connector | no | 0 | 24725 | - |
| ReviewC1Control | reviewer | no | 0 | 35574 | - |
| ReviewC2Control | reviewer | no | 0 | 49469 | - |
| ReviewAliasQuotes | reviewer | no | 0 | 58130 | - |
| ReviewCensusBlock | reviewer | no | 0 | 2355 | - |
| CriticC1Target | critic | yes | 7561 | 44331 | # CriticC1Target — attack on the C1 target |
| CriticC2Population | critic | no | 0 | 103837 | - |
| CriticAliasScope | critic | no | 0 | 32976 | - |
| CriticPredicateIdentity | critic | no | 0 | 43971 | - |
| MutC1Counter | mutation-tester | no | 0 | 31984 | - |
| MutC2Gate | mutation-tester | no | 0 | 42551 | - |
| MutAppendBlock | mutation-tester | no | 0 | 10978 | - |
| RevengerNoOp | revenger | no | 0 | 44585 | - |
| RevengerQuarantine | revenger | yes | 3776 | 24667 | # Revenger quarantine review — kama |
| SentinelScope | sentinel | no | 0 | 354811 | - |
| SentinelReceipts | sentinel | no | 0 | 159240 | - |
| SimplifyRows | simplifier | no | 0 | 51018 | - |

**Round shape:** one v1 wave of 33 seats (policy v1 band 32-64; `ufo-swarm-wave.mjs plan`
exit 0, `counts.spawn=33`, `waveMinLanes=32`, `waveMaxLanes=64`, hard ceiling 256, one
dispatch call). Role mix: connector 3, critic 4, executor 5, mutation-tester 3, revenger 2, reviewer 4, scout 6, scribe 3, sentinel 2, simplifier 1. Attack seats (reviewer, critic, mutation-tester,
revenger, sentinel): **15 of 33 = 45.5%** (the round contract requires >=25%).
The §3 L2 floor is met inside this one wave: connector 3, executor 5, scribe 3,
scout 6, reviewer 4, critic 4. The canonical §3 planner seat is held by the L1
(Kimi fresh L1); no planner role was added - the validator refuses it - and the
bounded planning data-walk is the preregistration and this wave's spec.

**Grant:** `scripts/hyaku/wave-slot.sh acquire kama round-34-w1 33` -> exit 0,
`granted lane=kama wave=round-34-w1 seats=33 live=18 pending=0 cap=256`, taken
immediately before the dispatch; the reservation is released when the wave settles.

**Transport:** one batched dispatch of the validator's `taskCall` (33 lanes) on this
Kimi surface - one `kimi --agent ufo-<role> --add-dir <fleet> --add-dir <shokuknow>
-p <lane task>` process per lane, all launched in the same batch, each carrying the
validator's composed lane text unchanged (`/skill:godspeed` + the verbatim Godspeed
directive bytes + the shared wave context + the lane task).

**Actual seats at report time:** 5 of 33 lane reports committed under
`.ufo/waves/round-34/w1/out/`; 2 lane processes still live. A first dispatch
attempt died at spawn for all 33 seats with `error: Cannot combine --prompt with
--auto.`; it is recorded in `.ufo/waves/round-34/w1/out/dispatch-manifest.json`.
No seat was replaced, no wave was split, and the failed attempt is not counted as
returned work. Seats without a report are reported as dead or in flight - not as
returned - and their seat logs stay in the lane as the evidence of what they did.
<!-- WAVE-CENSUS:END -->
