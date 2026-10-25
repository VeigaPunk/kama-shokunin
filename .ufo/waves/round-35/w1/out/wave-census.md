# round-35 wave census

shape: one v1 wave, 32 seats, policy v1 band 32-64
grant: wave-slot.sh acquire kama round-35-w1 32 -> granted live=34 pending=0 cap=256
transport: kimi --agent ufo-<role> -p ; no --auto. AgentSwarm tool unavailable.
dispatcher: launch script crashed after Popen on NameError; waiter attached to the same 32 pids. No seat replaced.

roles: connector 1, critic 4, executor 4, mutation-tester 3, revenger 1, reviewer 4, scout 12, scribe 3
attack reviewer+critic+mutation-tester = 11 / 32
reports_exist=32 stdout_persisted=14 timed_out=7
timed_out: ScoutProbeEntry, ScoutQuarantineS200, ScoutQuarantineS210, ScoutCoverageAbsence, ExecDisposition, ConnSibling, RevengerScope

| seat | role | timed_out | stdout_persisted | log_bytes |
|---|---|---|---|---|
| ScoutProbeEntry | scout | True | True | 50385 |
| ScoutVllm503 | scout | False | True | 23755 |
| ScoutDockerHc | scout | False | True | 24415 |
| ScoutHostedReject | scout | False | True | 30038 |
| ScoutQuarantineS200 | scout | True | True | 31155 |
| ScoutQuarantineS202 | scout | False | True | 45391 |
| ScoutQuarantineS210 | scout | True | True | 40812 |
| ScoutQuarantineS211 | scout | False | True | 26600 |
| ScoutQuarantineS224 | scout | False | True | 26927 |
| ScoutQuarantineS230 | scout | False | True | 29824 |
| ScoutCoverageAbsence | scout | True | True | 32052 |
| ScoutConsiderthese | scout | False | True | 18490 |
| ExecCollision | executor | False | False | 22651 |
| ExecNormalize | executor | False | False | 32311 |
| ExecDisposition | executor | True | True | 179016 |
| ExecC1Selftest | executor | False | False | 13381 |
| ScribeCorrection | scribe | False | False | 65364 |
| ScribeGate | scribe | False | False | 65859 |
| ScribeCoverage | scribe | False | False | 69600 |
| ConnSibling | connector | True | True | 57331 |
| ReviewC1Facts | reviewer | False | False | 67894 |
| ReviewC2Ground | reviewer | False | False | 51396 |
| ReviewManifestDiff | reviewer | False | False | 48590 |
| ReviewR33Count | reviewer | False | False | 28290 |
| CriticC1Rewrite | critic | False | False | 29251 |
| CriticC2Outside | critic | False | False | 62339 |
| CriticProvince | critic | False | False | 58279 |
| CriticMission | critic | False | False | 57005 |
| MutC1FalseRow | mutation-tester | False | False | 13741 |
| MutC2Junk | mutation-tester | False | False | 51085 |
| MutCensusPipe | mutation-tester | False | False | 31813 |
| RevengerScope | revenger | True | False | 49370 |
