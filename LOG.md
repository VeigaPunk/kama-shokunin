# kama-shokunin — Iteration Log

Single-writer file (L1 owns it). Per-contributor detail lives in `corpus/`.

- 2026-09-28 — round 0: minted as shonen (sibling mint; rationale in MINT.md).

## round 1 — operability axis (measured via freshness)

**Move:** ship a runnable endpoint-identity gate for the local model-serving domain.
Before: `ls tools/ registry/` absent — the repo had no executable artifact and the
domain's one recurring defect (a consumer pin that no longer points at the model) was
still being discovered by accident in *other* lanes (kagi r3, kengaku r4, see MINT.md).
After: `tools/kama-probe.sh` (788 lines, 0755, md5 `932ea3dc365e066e740731cf6a939506`)
+ `registry/endpoint-consumers.tsv` (11 rows × 6 cols, md5 `87eb156b7cc36e98f3cbfb37c00f5351`).

**Gate (run by L1 on the shipped build):**

```
$ bash tools/kama-probe.sh check; echo $?
… 11 row table …
registry_rows_evaluated=11 model_ok=3 drift=8 exit=2
EXIT=2
$ bash tools/kama-probe.sh check --json | jq .summary
{"registry_rows_evaluated": 11, "model_ok": 3, "drift": 8, "exit": 2}
```
3 `MODEL_OK` rows are positive controls (`systemd-qwen-coder` @34113, `ufo-fsd-thetick`,
`ufo-fsd-local-helper`); 8 `FOREIGN_SERVICE`/`html-non-model` rows are the stale 8080
family. `--json` valid on stdout, stderr empty; `listeners` exits 0.

**Mutation matrix executed by L1 against the shipped build** (fixtures on scratch ports,
removed after): M3 correct port + bare-id expectation → `MODEL_OK` exit 0 (proves the
basename/`.gguf` normalization); M4 look-alike JSON with a wrong id → `MODEL_MISMATCH`
`served-id-mismatch`; M5 `:8790` → `UNAUTHORIZED_SERVICE` `http-401`; M6 non-HTTP bytes →
`NOT_HTTP` `no-http-response` (no hang); M2 nothing listening → `DEAD` `connection-refused`;
M7 wrong expected id on the healthy 34113 → `MODEL_MISMATCH`. All six verdict classes were
exercised; every rule hole filed by `corpus/lessons/probe-mutation-matrix.md` (M7 identity
semantics, M6 timeouts, M4 schema boundary, M2 transport map) is closed in the shipped build.

**Two probe defects found by running the artifact, fixed in-round:** the port resolver
synthesised `30` from the string `Qwen3-Coder-30B` (red: `file=no@30 … rc=7`), and every
`--json` path died on a trailing comma produced by `$(…)` stripping the newline (red:
`JSONDecodeError: Illegal trailing comma`). Both are now covered by the matrix above.

**Drift proven, not inferred (live 2026-09-28):** `~/.config/opencode/opencode.json:158`
(mtime 2026-09-28 16:46 — freshly edited, pin still stale), `~/.config/opencode/agents/janitor.md:21`
("there is no fallback"), `~/.config/the-janitor/opencode.json:16` (`enabled_providers`
= `qwen-local` only — fails closed), `~/.local/bin/the-janitor:19`, and the omp binary's
builtin `baseUrl = LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"` all target `127.0.0.1:8080`,
which is now `docker-jitsi-meet-jvb-1` (Jetty HTML 404 on `/v1/*`; `/metrics` returns
**200** Jitsi openmetrics, so status-only liveness false-passes). The model is
`llama-server` pid 1299 on `127.0.0.1:34113` (`qwen-coder.service`, enabled/active,
`--port 34113`), and `~/Projects/origin-work/ufo-fsd-alpha/{config/the-tick.machine.json:16,
scripts/local-helper.mjs:8}` already pin the correct port — the box holds the bug and its
fix simultaneously.
*[errata 2026-10-14: `origin-work/ufo-fsd-alpha` relocated to `~/Projects/ufo-fsd-alpha`
(HEAD `964f443e`); the path above is historical — see `corpus/knowledge/consumer-registry.md` §Errata.]*

**Facts that changed the contract mid-round** (each verified live, each in `corpus/`):
llama.cpp answers `POST /v1/chat/completions` with **200** for any requested model name and
serves the loaded model, so request success is not identity evidence; the served id is a
full GGUF path while consumers declare a bare id, so normalization is load-bearing;
`systems` 8080 family has no verbatim rule for 4xx-non-model or TCP-accept-then-RST, hence
contract v3's ordered precedence.

**Method traps recorded** (each cost a peer a wrong conclusion): bare `ss -tnp` cannot see
listeners (`0` vs `23` with `-l`); `/home/vgpnk/projects` ≠ `/home/vgpnk/Projects`
(inodes `101125103` / `27238`) so a lowercase-root sweep misses the entire ufo-fsd-alpha
family; `git remote -v | head -2` invents a remote difference.

**Peer ledger (13 L2 subagents, one batched call, all resolved by live commands):**
`KamaScoutConsumers` 38-row registry + falsified the "no consumer pins 34113" expectation;
`KamaScoutListeners` 23-listener census (died after landing its artifact — Devin quota);
`KamaExecutorProbe` probe+registry; `KamaPlanner` `endpoint-identity.md` (7 rows);
`KamaScribeSkill` SKILL.md (315 lines, 47 citations); `KamaRevengerTimeline` drift timeline;
`KamaLabratIdentity` served-id reconciliation; `KamaCriticFalsify` verdict CLAIM HOLDS with
corrected wording (8080 is HTTP-alive-but-foreign, not "dead"; kernel NAT undecidable
without root); `KamaReviewerCitations` re-derived F1–F12 and **caught one stale L1 fact**
(`m_flash` is `charm-hyper/…`, not `alibaba-token-plan/…`); `KamaSentinelSafety` probe
redaction/authority audit; `KamaMutationMatrix` the rule holes above; `KamaDistillerAliases`
alias→endpoint normalization (no alias resolves to loopback today);
`KamaConnectorSiblings` cross-lane scope + handoffs.

**Hygiene:** a whole-file read of `~/.omp/agent/config.yml` returned its credential line
(key `token`, line 169). No artifact contains that value — verified by a key-side scan over
every corpus/report file (`0` hits). One L1 redaction pass misfired in the *other*
direction (a substring regex matched the model route `alibaba-token-plan/...` because it
contains "token") and was reverted; rule recorded in `corpus/lessons/round-1.md`.

**Operator decision filed** (`.ufo/l0-questions.md`): who applies the 8080→34113 repoint to
the four operator-owned pins — kama is charter-bound to detect and report, not rewrite
`~/.config`, `~/.local/bin`, or systemd units (`PROVINCE.md` §Write boundary).

**Adjacency (reported, not absorbed):** `kengaku`'s `/home/vgpnk/bench-arena/loop.sh:5`
scrapes `:8080/metrics` (`-fsS` passes on Jitsi's 200, and the parser's `prompt|eval`
substring match yields 0 names there vs 4 on 34113, so telemetry silently degrades to
`journal`); `0.0.0.0:40993` exposes a browsable `/tmp` listing on the LAN;
`127.0.0.1:9222` DevTools with 21 logged-in targets; 8790/8791 are the fleet's credential
brokers (kagi) — a model consumer repointed there would aim prompts at `omp auth-gateway`.

## round 2 — freshness axis

**Move:** turn point-in-time endpoint reconciliation into durable,
invocation-to-invocation comparison. Before: freshness **6**; `check` sampled the
current 11 rows but retained no predecessor, so repeated exit-2 runs could not say
whether drift changed. After: freshness **7**; `tools/kama-probe.sh snapshot`
writes a dated `kama-probe/v2` JSON, compares normalized state with
`registry/history/latest.tsv`, and appends field/row transitions to
`registry/history/DELTA.md`. The honest boundary is **invocation history**, not
periodic monitoring: no scheduler was installed.

**Shipped build:**

- `tools/kama-probe.sh`: 1051 lines, mode 0755, md5
  `61e82ee22dc89292175c5431f1ed6dc1`; fourth subcommand `snapshot`,
  `--history DIR`, JSON stdout, lock + atomic baseline replacement, symlink
  refusal, persistence-field normalization.
- `tools/test-snapshot.sh`: 171 lines, mode 0755, md5
  `860f26ac05938cdfc1a8816eff1570b4`.
- tracked state: `registry/history/latest.tsv` sha256
  `fd98f07a2d845a31cdf0582aa0faf9180e0903754b33248897a7e4211d9843da`;
  `registry/history/DELTA.md` sha256
  `493afecbd6dd85df0f08f4541ecd340b03dc5df797a73bf8744cfd94edebab5a`;
  dated JSON and `.lock` are ignored.
- domain memory: `corpus/knowledge/snapshot-history.md`,
  `corpus/lessons/round-2.md`, round-2 citation errata, updated corpus index,
  `SKILL.md`, `PROVINCE.md`, `SHONEN.md`, and this scorecard/log.

**Live proof on the shipped build:**

```text
snapshot=20260929T043044Z prev=- rows=11 model_ok=3 drift=8 transitions=0 exit=2
snapshot=20260929T043052Z prev=20260929T043044Z rows=11 model_ok=3 drift=8 transitions=0 exit=2
```

Both runs wrote valid dated JSON. The unchanged second run left both tracked
sha256 values above unchanged, so a future timer does not dirty the repository on
every stable sample. Exit 2 is the gate result (eight live drifts), not a
persistence error. Final `bash tools/kama-probe.sh check` remained
`registry_rows_evaluated=11 model_ok=3 drift=8 exit=2`.

**Behavioral gate:** `bash -n` clean; `shellcheck -S warning` clean;
`bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0` in 1.15 s. The hermetic
fixture proves initial baseline, valid/redacted JSON stdout+file, byte-stable
unchanged state, `MODEL_OK→DEAD`, served-id change, row add, row removal,
malformed-baseline recovery + audit note, no phantom transition, `--port`
refusal, and symlinked-history containment. Scratch probes additionally classified
vLLM- and Ollama-shaped `/v1/models` responses as `MODEL_OK` and a plain JSON
look-alike as `FOREIGN_SERVICE`; because neither runtime/package is installed,
this is parser evidence only, not real-runtime integration.

**Persistence boundary:** tracked state excludes resolved URLs, registry notes,
raw evidence, query/userinfo, and full model paths. It stores only id, verdict,
reason, normalized served basename, port, and file-match; control characters are
removed. Dated JSON validates before `DELTA.md` or `latest.tsv` advances.
Malformed baselines rebaseline with warnings and a ledger note instead of
fabricating `row-absent` events or breaking the endpoint gate. `flock` serializes
writers; tmp+rename makes the baseline atomic.

**Freshness re-verification:** all load-bearing live domain facts held: 8080 still
returns Jitsi HTML/non-model responses, 34113 still serves the expected llama.cpp
model, the registry still evaluates 11 rows (3 ok / 8 drift), and the stale pins
remain unrepaired. Review caught and recorded three citation-state changes:
`enabled_providers` is at `~/.config/the-janitor/opencode.json:5-7` (not line 16);
`~/bench-arena/loop.sh` moved to `~/archive/bench-arena/loop.sh`; the round-1
23-listener census refreshed to 20 due ephemeral socket churn. The bad line
attribution and moved path are corrected in corpus; the filed round-1 log remains
historical.

**Scheduling handoff:** `systemctl --user list-timers --all` showed only
`ai-usage.timer`, `webzites-probe.timer`, and `charter-scribe.timer`; `crontab`,
`crond`, `cron`, `at`, `atd`, and `anacron` are absent. Kama cannot install or
enable units (`PROVINCE.md` write boundary), so `.ufo/l0-questions.md` asks the
operator whether to add a user timer. Until answered, sampling remains
per-round/manual and can miss short-lived transitions.

**L2 ledger (11 agents, one batched dispatch):** `KamaPlannerSnap` bounded the
state contract; `KamaLabratRuntime` measured response-shape compatibility and
runtime absence; `KamaExecutorDocs` drafted the operator contract;
`KamaCriticClaims` rejected the “periodic” overclaim; `KamaConnectorSib`
confirmed no sibling owns this check and no existing timer runs it;
`KamaReviewerFresh` re-derived citations and caught the stale line/path/count;
`KamaSentinelSnap` found credential-shaped persistence, control-character,
symlink, and torn-write risks; `KamaMutationSnap` supplied transition scenarios;
`KamaRevengerHist` reconstructed why a ledger would have distinguished the
8080→34113 cutover; `KamaScribeReport` supplied the report skeleton;
`KamaSimplifier` removed derivable `index.jsonl` dead weight. L1 integrated and
re-tested the findings; scratch prose was not copied as authority.

**Operator relay — model fallback (reported, out of kama province):** effective
config has `modelRoles.m_swe = devin/swe-2:max`,
`modelRoles.m_daybreak = openai-codex/gpt-daybreak-blue-latest:max`,
`retry.modelFallback = true`, but `retry.fallbackChains.m_swe = null` and
`fallbackChains.m_daybreak = null`. Therefore the exact
`m_swe → openai-codex/gpt-daybreak-blue-latest:max` chain is **not configured**.
This session logged nine genuine `Devin stream error resource_exhausted` events
from `03:35:54Z` through `03:49:17Z`; no model-change event accompanied them.
The only model changes were `devin/swe-2` at `03:19:34Z` and a later direct
`openai-codex/gpt-daybreak-blue-latest` selection at `04:13:34Z`, both with
`resolvedModelIsFallback:false`. Observed result: capacity failures did **not**
advance through a configured chain; the later Daybreak switch was not marked as
fallback. No failure was forced and no route/mission config was changed.

## round 3 — re-census: substrate relocation + box teardown (freshness axis)

**Move:** bring the lane back to verified ground after two external shocks —
the `ufo-fsd-alpha` tree relocated (`~/Projects/origin-work/ufo-fsd-alpha` →
`~/Projects/ufo-fsd-alpha`, HEAD `964f443e`) and the box deleted most of the
consumer surface outright — then restart the gate loop on the surviving rows.

**Survey (before):** `bash tools/kama-probe.sh check` →
`registry_rows_evaluated=11 model_ok=0 drift=11 exit=2` — every row DEAD
`connection-refused`, the two `ufo-fsd` rows additionally `file=missing`
(hardcoded `origin-work/` path), and a python `KeyError: 'provider'` on stderr
because `opencode.json` lost its `qwen-local` block. `tools/test-snapshot.sh`
→ `RESULT pass=24 fail=0` (hermetic suite unaffected).

**Failure classification:** (a) stale origin path — 2 registry rows + 5 corpus
docs; (b) citations to deleted files — 8 registry rows (opencode/janitor/
systemd-qwen files) + `webzites` second checkout + llm-wiki rows;
(c) moved-and-restructured citations (line drift) — `the-tick.test.js:87,:1858`
→ `:61,:1457`, `local-helper.test.js:247-250` → `:263-266`, `THE-TICK.md:40` →
`:29`, `local-helper.mjs:159/:163-165` → `:312/:325/:155-161`,
`run-logic.md:556` → `:495`, `wwkd/SKILL.md:131` → `:129`; (d) genuine lane
defect — zero.

**Repair:** `kama-probe.sh` gained `--ufo-src` + `$UFO_SRC` env + first-existing
candidate derivation (kumitate round-23/24 pattern); `$UFO_SRC` rows degrade to
`file=missing`, never to a guessed path. Registry cut 11 → 3 rows: the eight
consumer files no longer exist, and the registry contract admits only
LIVE-or-LOADABLE consumers — deletion recorded as 16 transitions in DELTA.md,
not silent edit. Corpus: append-only §Errata in `consumer-registry.md`; live
re-anchoring to measured lines everywhere the claim still verifies; historical
markers on the rest.

**Live proof after:**

```text
check:    registry_rows_evaluated=3 model_ok=0 drift=3 exit=2
snapshot: snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2
snapshot: snapshot=20261014T124525Z prev=20261014T124232Z rows=3 model_ok=0 drift=3 transitions=0 exit=2
consumers: consumer_rows_evaluated=3 exit=0 (ufo-fsd rows resolve file=yes via $UFO_SRC)
test:     RESULT pass=24 fail=0; bash -n clean (shellcheck absent on this box)
```

**Domain change (larger than the relocation):** `qwen-coder.service` is
inactive and its unit deleted; ports 34113 and 8080 both refuse connections;
`~/.config/opencode/opencode.json` is 5 lines with no `qwen-local` provider;
`~/.config/the-janitor/`, `~/.local/bin/the-janitor`,
`~/.config/opencode/agents/`, all `opencode.json.*.bak*`,
`~/.config/systemd/user/qwen-coder*`, `~/archive/bench-arena/loop.sh`,
`/tmp/fleet-override.yml`, `~/Projects/webzites/`, and `~/Projects/ephemeral/`
are gone. The stale-pin drift this lane was minted to watch is resolved by
deletion, not repoint. Surviving pins: `~/.local/bin/omp` builtin
`LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"` (still in the binary) and the
two ufo-fsd 34113 pins (verified at the relocated path).

**Carried debt:** the probe's positive controls (`ufo-fsd-thetick`,
`ufo-fsd-local-helper`) read DEAD today — correct *pin* but dead *endpoint*.
Unblock: operator restarts `qwen-coder.service` (or a successor unit); then
MODEL_OK returns and the controls regain meaning. Named in SCORECARD.

**Out-of-province report:** the local model-serving surface is nearly empty.
If `qwen-coder` is permanently retired, this lane's province contracts to the
omp binary default + cross-repo pins; a province revision is an L0/fleet
decision, not a lane self-edit.
## 4 — re-census round (freshness axis-move)

2026-10-14 · steered round 4 · axis: freshness · 32-lane fleet wave + parent integration.

Full round detail: `corpus/lessons/round-4-recensus.md`. Advisory inventories:
`../.ufo/waves/shokunin12h-20261014-p1-repair/members/`.

## round-1 — 2026-10-15 relaunch: current runbook freshness

**Steer and scope.** This explicit round-1 follows the recorded training rounds
through round 4 at `c390918f8f6d5d1b52787e4720c8642377fdcb8c`; it does not
renumber or rewrite them. `MISSION.md:29` assigns operability + freshness,
whereas the generated prompt and `shokunin.conf:52` say operability +
calibration. Mission precedence selects freshness, the lower assigned axis
(7 versus operability 8 in the inherited scorecard). Scores are author
assessments, not measurements of model quality.

**Motivating re-verification.** `bash tools/kama-probe.sh check` returned
`registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`: the builtin fallback
row at 8080 and both explicit UFO pins at 34113 were `DEAD` /
`connection-refused`; explicit pins resolved `file=yes`, the builtin row
`file=inherited`. This is endpoint unavailability now, not a broken probe,
verified active traffic, or permanent retirement.

The active runbook still described a successful September runtime, missing
janitor/unit paths, and an eleven-row JSON summary. At the baseline commit,
the following fixed-denominator counting command produced
`fields_checked=4 mismatches=3`: documented/observed rows 11/3,
model_ok 3/0, drift 8/3, exit 2/2.

```sh
bash tools/kama-probe.sh check --json | python3 -c 'import json,re,sys,pathlib; actual=json.load(sys.stdin)["summary"]; text=pathlib.Path("SKILL.md").read_text(); expected=json.loads(re.search(r"`summary` = `([^`]+)`",text).group(1)); mismatches={k:{"documented":v,"observed":actual[k]} for k,v in expected.items() if actual[k]!=v}; print(json.dumps({"fields_checked":len(expected),"mismatches":len(mismatches),"details":mismatches},sort_keys=True))'
```

**Single change.** Reconcile active instructions and province surfaces with
that sampled state; retain September successes as dated historical evidence,
not readiness guarantees. Registry row identities, URLs, model expectations,
probe implementation and snapshot schema remain unchanged. Note-only registry
corrections distinguish correct pins from live positive controls. Regenerate
the inherited bare-checkmarked SHONEN evidence as canonical author assertions
(`[~]`); no independent promotion verifier exists in this round.
The new `corpus/lessons/round-1-relaunch-freshness.md` supersedes stale-current
interpretations without rewriting historical corpus entries.

**Dispatch evidence.** One native OMP `task` batch returned “Spawned 9
background agents”: `KamaPlannerFresh` (planner), `KamaConnectorScope`
(connector), `KamaExecutorRunbook`, `KamaExecutorProvince`,
`KamaExecutorLesson` (executors), `KamaScribeEvidence` (scribe),
`KamaScoutSurface` (scout), `KamaReviewerRunbook` (reviewer), and
`KamaCriticFreshness` (critic). Role selectors used the unchanged host
`task.agentModelOverrides`; no model parameter, alias pin, routing change,
or domain-source write. This bounded shared-writer craft batch follows the
shokunin OMP binding, not a claimed validated generic UFO wave: the latter
excludes planner (`ufo-swarm-wave.mjs:256-269`). The inherited L0 question
“kama | round-1 | Reconcile the relaunched counter…” records that conflict.

**Acceptance boundary.** Keep the same four summary fields; compare the
delivered revision to a fresh real probe. Matching that sample cannot prove
continuous freshness, four independent checks, endpoint recovery, or runtime
integration. Review must also eliminate unconditional historical success
claims and allow expected exit 2 to complete this documentation-only task.
Service restoration, consumer repointing, timer installation, and context-size
reconciliation are not part of this move. Delivery measurement follows in an
appended entry once its measured commit exists.

## Actual round 5 — interactive cutover and dispatch blocker

2026-10-15. Start revision `c390918f8f6d5d1b52787e4720c8642377fdcb8c`.
One attempted axis-move: freshness. Plan saved before implementation at
`plans/wwkd-round-5-interactive-freshness.md`.

**Correction to the inherited relaunch entry above:** its `round-1` label and
nine-seat batch describe interrupted headless work, not a new verified round
or authority for this interactive dispatch. Historical round-4 work and reports
remain intact; round 3's report is still missing. The prior driver launch
counter 1 is not a completed-round count. This session made zero native task
calls and adds zero verified completed rounds. No historical log, report or
native session bytes were overwritten.

**Motivation and local change.** A new registered-endpoint measurement
(`.ufo/round-5/before-check.json`) found the same three dead rows, while the
active SKILL JSON example still documented 11 rows, MODEL_OK=3 and drift=8.
The same four dependent fields had `fields_checked=4 mismatches=3`.
The runbook now records the measured negative result, dates September examples,
separates inherited defaults from effective runtime URLs, distinguishes correct
pins from endpoint readiness, and makes operator-owned restoration a handoff,
not an implicit completion condition. No probe/schema/model-expectation change.

Inherited province/registry-note corrections, corpus index text, author-asserted
SHONEN marks and the unfinished relaunch lesson were preserved and reconciled.
`corpus/lessons/round-5.md` explicitly supersedes current-state interpretations
without rewriting corpus history. Missing `corpus/QUALITY.md` now carries five
domain criteria grounded in the actual admit/reject decisions; the corpus index
links both and records the unverified frontier. SKILL registers existing local
gate/probe semantics without pretending a new self-test exists.

**Checks, complete output retained.** `.ufo/round-5/acceptance.json` stores every
argv, stdout, stderr and exit code. Delivered local summary comparison:
`fields_checked=4 mismatches=0`. Full verdict lines:

```text
registry_rows_evaluated=3 model_ok=0 drift=3 exit=2
consumer_rows_evaluated=3 exit=0
RESULT pass=24 fail=0
snapshot=20261015T051015Z prev=- rows=3 model_ok=0 drift=3 transitions=0 exit=2
snapshot=20261015T051015Z prev=20261015T051015Z rows=3 model_ok=0 drift=3 transitions=0 exit=2
```

`check` and `check --json` exited 2; `consumers`, existing fixture suite and
shell syntax invocation exited 0. Both isolated real snapshots exited 2 and
left their TSV/ledger byte-stable. The temporary history was removed after
capturing normalized baseline/ledger bytes; tracked default history was not
advanced. No arbitrary listener scan, external research, native transcript/
credential/environment/journal read, service repair or host config write.

**Dispatch blocker, not a smaller substitute.** Exactly 32 distinct review
scopes validated through canonical `ufo-swarm-wave.mjs plan --route-families`,
exit 0 (`spawn=32 resume=0 total=32`); the canonical pure renderer produced the
saved payload. Route-family status is `unprobed`, not a model-health check.
Actual required aliases are not selected by the global native task overrides:
executor → @m_mid instead of @m_composer; scribe → @m_fast instead of
@m_composer; reviewer/sentinel/revenger → @m_mid and
scout/simplifier/mutation-tester → @m_fast instead of @m_grok; critic →
@m_strong instead of @m_grok; connector → @m_mid instead of @m_antigravity.
The antigravity fallback chain is empty, not the requested @m_zfl fallback.
Evidence: `.ufo/round-5/route-preflight.json`, `wave-validation.json`,
`wave-plan.json`, `wave-payload.json`. No task batch, runtime registry, agent
handle or specialist report was fabricated. Global route repair belongs to the
operator; no pins or overlays were introduced.

**Admission and trends.** Local axis verdicts in SCORECARD: freshness improved;
operability/depth/coverage/calibration/adjacency unchanged. Learning quality
improved locally; expansion and discernment unchanged. No harmed axis observed,
but this does **not** admit the round: the mandatory dispatch did not occur.
No outside spot-check or promotion `[x]`; no Rust/native verdict or saturation.
The previously reported red native Phase 0/self-iter path was not rerun.

**Receipt boundary.** The matching interactive Sighting metadata has no
taskKey, resultPath/receiptPath or prompt/config digest binding at top level or
under dispatch. No arbitrary task key or digest is substituted. The receipt
prerequisite artifact names the missing binding; a display-only mission-result
envelope is not task acceptance. No applicable task receipt is claimed and the
Sighting mission must not be completed. Only the fleet integrator can provide
the binding and reconcile the historical verified-round total.

**Concrete continuation.** After authorized global role routes and real receipt
binding are supplied, redispatch a fresh session on the same logical lane,
preserving all old artifacts. Re-measure the lowest LIVE axis; do not reset to
round 1 or re-count this landed correction. Next candidate freshness work:
still-live source-anchor correction entries, not corpus rewrites. Operator
serving-runtime disposition, missing round-3 report and independent admit/reject
review remain named debt. Exact work commit and file-byte binding are published
after the work commit in `.ufo/round-5/landed-evidence.json` and the own-repo
report `.ufo/reports/round-5/kama.md`. NO PUSH.

### Actual round-5 landing and handoff evidence

Work landed as `e246c40ec1b4ba08c36359934f69b8064b7dc54a` under
`kama-shokunin <kama@shokunin.local>`. The post-commit real `check --json`
again exited 2 with all three registered rows DEAD and the runbook comparison
`fields_checked=4 mismatches=0`; complete streams and manifest digest:
`.ufo/round-5/landed-evidence.json`.

The own-repo report was written after that work commit at
`.ufo/reports/round-5/kama.md`. `.ufo/round-5/continuation.json` binds its
actual bytes and the fresh-session markdown handoff by SHA-256. Additional
metadata-only binding search is retained at `.ufo/round-5/binding-search.json`:
matching Sighting, launch and panes rows lack receipt bindings; the documented
default queue and matching prompt digest sidecars were not found. This does
not assert global absence of all possible operator artifacts.

The display-only mission-result envelope was minted and validated (both exit
0), recording zero subagents and unsound/blocked/incomplete. It is not a task
receipt, native verdict, completed round, or fleet acceptance. No applicable
receipt was fabricated and Sighting completion was not invoked. The blocked
report/handoff are landed for durability, not as an admission signal. This
attempt adds zero verified completions; external route and receipt prerequisites
remain the concrete unblock. No second round and no push.

## 2026-10-16 — protocol conformance: SCORECARD contract fields

Operator conformance rollout under the 2026-10-16 fleet amendment (`84bade0`), not a craft round: `Axes`, `Planned` and `Retired` already existed as real recordable sections.
`Capabilities` (empty `— none yet —` repertoire row) and `Saturation` (line + window N deferred to the lane's next round), the genuinely missing contract fields, were appended as additive scaffolds per `AXES.md` §SCORECARD.md contract. No axis claim was made and no score moved; no push.

## round 6 — blocked dispatch (goal-mode load-test, loop 1)

- 2026-10-18 — Round 6 dispatched per operator goal: 64 seats, ONE batched
  AgentSwarm call, model `opencode-go/deepseek-v4.1-flash-free` (free
  variant; wire-default effort — AgentSwarm exposes no per-seat effort pin).
  Result: 64/64 spawn failures with the identical upstream error
  `400 Upstream request failed: Model is unavailable.`; wave wall 41.6 s;
  zero completions; peak concurrency 0. Single-seat re-probe ~2 min later:
  same error (persistent, not transient). Alias accepted by the host
  dispatch catalog — failure originates at the provider gateway. Zero tokens
  generated; no TPS inferable; the unavailability IS the loop-1 finding.
  No corpus/probe/registry content changed; no axis claims executed; no
  scalar advanced. Admission: BLOCKED-WITH-DATA.
  Evidence: `.ufo/round-6/{plan.json,SEAT-PROTOCOL.md,telemetry.json}`;
  report at fleet root `.ufo/reports/round-6/kama.md`.

## round 7 — blocked dispatch (goal-mode load-test, loop 1, availability re-test)

- 2026-10-18 — Round 7 re-tested `opencode-go/deepseek-v4.1-flash-free`:
  64 seats, ONE batched AgentSwarm call. 64/64 spawn failures with the
  identical upstream error `400 Upstream request failed: Model is
  unavailable.`; wave wall 41.5 s; zero completions. Third probe of this
  model in ~25 min (18:32, 18:33, 18:37Z) — unavailability is persistent,
  not a transient rate limit. No content changed; no axis claims executed;
  no scalar advanced. Admission: BLOCKED-WITH-DATA. Loop-1 deepseek
  concurrency ceiling: 0 usable seats.
  Evidence: `.ufo/round-7/{plan.json,SEAT-PROTOCOL.md,telemetry.json}`;
  report at fleet root `.ufo/reports/round-7/kama.md`.

## round 8 — blocked dispatch (goal-mode load-test, loop 1, glm round 1)

- 2026-10-18 — Round 8 attempted `opencode-go/glm-5.3-flash-free` (64 seats,
  ONE batched AgentSwarm call). The host runtime rejected the wire id in its
  model catalog BEFORE any seat was created — zero spawn attempts, zero
  upstream contact. Verbatim error + full host catalog:
  `.ufo/round-8/telemetry.json`. Distinct from rounds 6-7: those aliases were
  catalog-valid and died upstream (provider outage); this alias does not
  exist locally (host catalog gap). No opencode-go glm variant (free or
  paid) is dispatchable on this host; glm-5.3-flash exists only as
  `zai-coding-plan/glm-5.3-flash[-low]` and `devin/glm-5-3-flash-*`.
  No substitution made (goal stop rule requires operator sign-off).
  L0 question appended: fleet `.ufo/l0-questions.md` (kama | round-8).
  No content changed; no axis claims executed; no scalar advanced.
  Admission: BLOCKED-WITH-DATA.
  Evidence: `.ufo/round-8/{plan.json,SEAT-PROTOCOL.md,telemetry.json}`;
  report at fleet root `.ufo/reports/round-8/kama.md`.

## round 9 — blocked dispatch (goal-mode load-test, loop 1, glm round 2; loop 1 closes)

- 2026-10-18 — Round 9 re-attempted `opencode-go/glm-5.3-flash-free` (64
  seats, ONE batched AgentSwarm call). Identical local rejection to round 8:
  wire id absent from the host model catalog, call failed validation before
  any seat was created (zero spawns, zero upstream contact, 0.0 s). The
  29-alias catalog was byte-identical to round 8's — unchanged 18:39Z ->
  18:41Z. L0 question (kama | round-8) remains unanswered; no substitution
  made (goal stop rule). No content changed; no axis claims executed; no
  scalar advanced. Admission: BLOCKED-WITH-DATA.
  Evidence: `.ufo/round-9/{plan.json,SEAT-PROTOCOL.md,telemetry.json}`;
  report at fleet root `.ufo/reports/round-9/kama.md`.
- 2026-10-18 — Loop 1 closure artifact: new knowledge entry
  `corpus/knowledge/free-tier-provider-limits.md` (loop-1 final table:
  deepseek-free 128/128 upstream 400s, 0-seat ceiling, outage persistent
  18:32-18:37Z; glm-free not dispatchable on host, catalog gap across two
  probes; loop tokens 0; inferred TPS not measurable). Indexed in
  `corpus/README.md`. Loops 2-3 sections left pending for their rounds.

## round 10 — sources registry, cross-engine entries, stale anchors (kaika campaign, 2026-10-19)

- Steered round 10 = the never-dispatched 2026-10-18 plan; collision check clean (no `round-10/kama.md` report at the fleet root or ledger worktree; this LOG had no round-10 entry). Worktree `.tower/worktrees/kaika/kama-shokunin`, branch `kaika/round`, base `35e9175`. Axis authority `MISSION.md:29` (operability + freshness) over the prompt's "operability + calibration".
- L2 swarm: 12 seats in one batched call (planner, connector, 4 executors, scribe, 2 scouts, reviewer, critic, sentinel); the C1 executor stalled on a provider rate limit (route `m_swe` exhausted per the orchestrator) and was re-dispatched fresh; one follow-up pin scout.
- **C1 freshness** — 50 stale anchors (42 active, 8 historical moves) corrected by end-of-file entries; counting loop 50 → 0. Review changes: A12 withdrawn (false positive), 18 circular checks rewritten shape-only, A18 reduced to `wc -l` after a 4-line read of a domain config body (slip recorded), A51 added from the critic's sweep (offset UNDECIDABLE).
- **C3 capability + coverage** — `corpus/SOURCES.md` (30 rows, census clean), 3 knowledge entries (`runtime-health-surface-matrix`, `serving-metrics-crosswalk`, `gguf-runtime-compatibility-boundary`), KQ6–KQ10 appended to `QUALITY.md`, `lessons/round-10.md` (24 mistakes, Gate for every row), coverage additions appended to `corpus/README.md`, one SKILL.md pointer line.
- Plan claim 2 closed (re-verification is not an operability move). L1 slip: `kama-probe.sh listeners` was run outside checklist step 7's scope; output excluded (Mistake 25 → KQ10). The L1's checklist gate runs (check/consumers/test-snapshot/isolated snapshot) are contested by the sentinel and critic under the campaign's documentation-only rule: S030 rejected, no claim rests on them, L0 question in the report. Re-verification result for the record: 3 rows DEAD connection-refused, exit 2; rows identical to baseline `20261014T124232Z`; fixtures 24/0.
- Append-only exceptions, recorded: `SKILL.md`, `corpus/README.md` and `consumer-registry.md` lacked a final newline, so each append rewrites that last line's bytes (text identical); `SCORECARD.md` capability and saturation rows replaced 1:1 (contract fields, no line shift).

## round 10 — post-review fixes (2026-10-19)

- Orchestrator adjudication: ADMIT conditional. Appended, append-only: SCORECARD axes erratum (freshness 7 → 8, coverage 8 → 9, superseding the stale top table) and C3 restatement on knowledge entries (9 → 12; sourced 0 → 3) with per-entry rationale; lesson errata retiring Mistake 14's substring count (15 base / 29 head — it matches correction lines); C1 measurement split into resolved 48 / terminal 2 (A17 dead surface, A51 UNDECIDABLE — not re-anchored) / unresolved 0 via new `.ufo/round-10/audit/validate-new-pointers.sh` (negative control unresolved=2); gate-run ruling recorded (in-province; S030 stays rejected).
- Fleet census `sources-census.sh validate` → `ok`, exit 0.

## 2026-10-17 — README: Devin wiki link

- Operator directive (2026-10-17): insert the Devin wiki link into the README header of every repository with a generated wiki.
- Change: `README.md` created (lane-header convention) with a `**Wiki:**` link to https://app.devin.ai/org/veigapunk/wiki/VeigaPunk/kama-shokunin?branch=master.
- Evidence: the org's Devin wiki index lists this repo's generated wiki; sibling lane READMEs carry the same `**Wiki:**` header.
- Documentation-only change; no round run, no axis moved, no verdict changed.

## round 11 — explicit provenance and served-identity limits (2026-10-20)

- Claims: **C1 calibration**, the lowest assigned axis, adds honest provenance
  supplements to nine legacy knowledge files while preserving original prefixes;
  **C2 coverage** admits one documentation crosswalk with remote-inventory,
  nullable-loading, router-state and alias/digest limits beyond prior coverage.
  Declaration/errata: `.ufo/waves/round-11/claims.json`; neither changes runtime
  health or claims local Ollama integration. Scores remain 7/9, delta 0 each.
- Motivation: the round-10 plan's “18 entries” combines nine legacy knowledge
  files with lessons, and the original metadata is absent from those nine files;
  frozen source bytes and field inventory are in `.ufo/waves/round-11/frozen/`
  and `legacy-baseline.json`. Existing matrix:17 already held tags versus ps;
  the new crosswalk credits this rather than counting it again.
- Inherited headless round-11 outputs are resolved under this entry: reuse the
  reviewed supplements, source edits, crosswalk, QUALITY/README corrections and
  frozen baseline; retain original spec/declaration/advice as historical work,
  not final verdicts. `.ufo/round-10/plan.json` and `SEAT-PROTOCOL.md` are inherited
  undelivered planning artifacts, committed only for durability; their old
  provider/route instructions are not executed.
- Source frontier: S001/S010/S011/S012/S016 reopened, S031 added from documented
  remote fields; exact cell changes/quote in `corpus/lessons/round-11.md` §Gate.
  K02 crosswalk held; K05 context capacity still needs an authorized runtime.
  `corpus/SOURCES.md` old nonmutable cells are preserved; W04 duplicate URL
  denotes a scoped superseding row, not independent corroboration.
- Review-driven repairs: correct host-presence/retirement overclaims, baseline
  line 6, obsolete config-body rechecks, unsafe privilege implications and
  metadata-versus-documentation authority; append source-attribution limits to
  endpoint identity and a shape-evidence limit to consumer registry. QUALITY
  KQ11–KQ14 and SKILL's interpretation table/gate registry capture the lessons.
  `corpus/lessons/round-11.md` records accepted/rejected candidates and review
  dispositions; old corpus prefixes remain immutable.
- Swarm: inherited 32-seat build dispatch plus a validated 32-seat continuation
  verification dispatch, each one task call, role-routed without model arguments.
  L1 is canonical planner; bounded revenger data-walks advise. Specs/dispatch/
  registries/seat reports are under `.ufo/waves/round-11/`. Missing inherited
  Measure/Safety advisory reports are not fabricated; current evidence covers
  those concerns. Three misrooted continuation reports were copied into this
  lane and fleet-original cleanup routed to Main.
- Reproducibility: `measure.py` keeps field/prefix measurements distinct from
  semantic admission; `reproduce.py` checks frozen input digests, runs CLI/
  fixture cases and isolated negative controls. Fresh measurements are recorded
  in the later append below after measuring this committed revision.
- Boundaries: no live endpoint, environment or credential inspection, service
  mutation, scheduling or upstream push. No tools installed. Outside non-author
  admit/reject review requested from the orchestrator; all lane-dispatched
  reviewers remain author advisors, and SHONEN boxes remain `[~]`.

## round 11 — committed-revision measurements (2026-10-20)

- Measured `3285cdf7a50481694a36c4425cf32c915ab5e5f0` using
  `python3 .ufo/waves/round-11/reproduce.py`: receipt `acceptance.json`
  under that wave directory, overall success; C1 missing fields 27 → 0,
  original prefixes preserved; C2 entry 0 → 1. Original measurements
  exit 1, final exit 0. This is corpus metadata/calibration and documented
  coverage, not local runtime integration.
- Self-invocation fixture suite 19/19, exit 0; isolated missing-field and
  prefix-mutation controls exit 1 with stable expected finding IDs;
  tampered baseline exits 2 `snapshot_tampered`. Eleven frozen input digests
  verified before comparison; no live-tree mutation.
- Source census/validation: `.ufo/waves/round-11/sources-census-final.json`;
  original 30 rows → final 31, mined 17 → 21, queued 8 → 5,
  rejected 5 → 5, tiers A 27 → 28 / C 3 → 3. Validation exit 0,
  W04 intentional same-URL/different-scope supersession. Source gates and
  full before/after command streams are committed, not quoted from memory.
- Claim verdicts: calibration improved (score 7 → 7), coverage improved
  (score 9 → 9); operability/freshness/depth/adjacency unchanged.
  Trends: expansion/quality improved, discernment unchanged awaiting
  outside round-11 admit/reject sampling. No new capability or promotion.

## round 12 — source fidelity and routed clarification (2026-10-20)

- Declared C1 calibration (lowest assigned): one auxiliary frozen snapshot
  mismatch → zero in a new corrective snapshot, separately checking source
  correspondence and digest integrity. Scores stay calibration 7 → 7; no new
  serving capability, readiness, coverage or runtime freshness claim.
  Declaration: `.ufo/waves/round-12/claims.json`; motivation: non-author
  `corpus/lessons/round-11-verifier-spotcheck.md` D1 with its unequal actual/
  frozen SHA-256 values and finding that internal digest agreement was insufficient.
- D1 corrective evidence is new under `.ufo/waves/round-12/`; old round-11
  frozen bytes, manifest and receipt remain untouched. Fail-capable
  `fidelity.py` and `reproduce.py` distinguish source mismatch, integrity
  tampering and unavailable authority. Their committed-revision results are
  appended below after the single integrated acceptance run.
- D2–D5 are explicit clarifications, not additional claims: SOURCES appends
  opening-date and landed-K02 navigation correction plus inference/registry
  supersession boundaries; crosswalk appends the matching inference limit;
  SKILL appends complete applicable QUALITY authority and the local gate row;
  the undelivered historical round-10 seat protocol receives an unmistakable
  in-file archival disclaimer. Its historical directions are void, not replayed.
  Lesson `round-12.md` §Mistakes maps every routed item to its rule/criterion.
- QUALITY KQ15, motivated by D1, requires exact immutable-source comparison
  independently of a shipped integrity manifest and preserves KQ14's semantic
  human-review boundary. Reopened own-work source evidence and registry row
  are recorded in the lesson Gate after access, never pre-claimed as observed.
- One validated 32-seat wave: 7 executor, 5 scout, 4 connector, 7 reviewer,
  4 critic, 2 sentinel, 2 scribe, 1 revenger. L1 holds canonical planner seat;
  PlannerWalk is the bounded revenger planning advisor. Complete validator
  taskCall dispatched once unchanged, roles host-routed with no model argument.
  Evidence: `.ufo/waves/round-12/{spec,dispatch,record,spawn-result}.json`
  and `advice/`; no advisor is outside non-author closure.
- Starting tree clean at `79fa257719e8688692ed1dc443589331ba22b7fe`; no
  inherited lane-authored leftovers. Non-author verifier files are read-only.
  No endpoint/service/config/environment/credential inspection or mutation,
  routing change, scheduler or upstream push. Tools installed/updated: none.
  Stale-lane: respawn-per-round; no other kama mission is open. Operator-side
  cleanup item in round-11 closure remains Main's action, not this lane's write.

### round-12 erratum to round-11 frozen-source wording

This corrects the current reading of round-11 lines 547–548 (“frozen source
bytes”) and lines 594–595 (“Eleven frozen input digests were verified”).
The eleven integrity checks did **not** independently establish source-commit
correspondence. Outside round-11 review found nine original knowledge blobs
matching git, but the auxiliary SOURCES snapshot differed:
actual `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`,
old frozen `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1`.
The old file's truncated line and display footer were frozen self-consistently.
The round-generated legacy baseline is metadata, not a source blob at the
older revision. C1 has a fixed one-file denominator chosen from D1, not a new
ten-file audit or a rediscovered defect. A new snapshot matching the source
is a construction check; the improvement is a separately source-anchored,
fail-capable gate plus this explicit limit correction. The old bytes and
receipts stay committed unchanged. Authority:
`corpus/lessons/round-11-verifier-spotcheck.md` §Checking frozen input correspondence;
`corpus/lessons/round-12.md` §Claim limit and prior-overlap credit.

Archive-placement ruling (D5): L1 authorized a **prepended**, unmistakable
historical/nonexecuted warning in `.ufo/round-10/SEAT-PROTOCOL.md`, a
non-corpus undelivered planning artifact. This is an explicit exception to the
initial seat's append/prefix instruction, not an exception to corpus/LOG or
SOURCES append-only rules. All original 4,413 bytes remain a contiguous suffix;
original SHA-256 is `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a`.
The old binding title is now preceded by its override, never current permission.
Owner evidence: `.ufo/waves/round-12/advice/ArchiveDisclaimer.md`.

## round 12 — committed-revision measurement and disposition (2026-10-20)

- Measured work `33f46685b418af868259952884e34b93633820cb` once with
  `python3 .ufo/waves/round-12/reproduce.py` (absolute path, fleet-root cwd).
  Receipt `.ufo/waves/round-12/acceptance.json`: exit 0 / ok true; all seven
  records match expected exits/findings; HEAD unchanged during measurement.
  Old snapshot source mismatch 1 (`source_mismatch`, exit 1) versus corrective
  snapshot 0 (`clean`, exit 0), both with valid independent source anchors.
- Self-invocation: 11/11, exit 0. Coherent snapshot+manifest mutation remains
  `source_mismatch`, exit 1; pristine snapshot with corrupt pin remains source
  match/count 0 but `snapshot_tampered`, exit 2. Redirected source manifest is
  `manifest_invalid`, exit 2; missing source is `source_unavailable`, exit 2.
  This demonstrates the D1 fix can fail without modifying historical evidence.
- Final source validation/census both exit 0; required command and full output
  in `.ufo/waves/round-12/sources-final.json`, before in `sources-before.json`.
  Rows 31 → 32, tier A 28 → 29, mined 21 → 22; queued 5/rejected 5 and C 3
  unchanged. New S032 docs/A supports capture method, not serving readiness;
  lesson Gate contains the opened URL/date/located quotes and all cell changes.
- Author verdict: C1 calibration improved, score 7 → 7 (delta 0); other axes
  unchanged, no observed harm. Trends expansion unchanged, quality improved,
  discernment unchanged pending fresh outside round-12 sampling. No capability,
  new knowledge entry, runtime repair or promotion is claimed.
- The superseded-claim sweep covered every changed domain document and archive
  using pattern `Every row was opened|every row was opened|next entry, K02|KQ11–KQ13|binding on all 64|supersedes S011|frozen_digests_verified|Eleven frozen input digests`.
  Historical hits have explicit overriding supplements in SOURCES, SKILL,
  crosswalk and this LOG, or the archive's leading warning. A chronology typo
  in the newly added archive banner was corrected: verifier D5 followed, not
  preceded, the round-11 introduction commit. Gate/code/frozen bytes unchanged
  after measurement.

## round 13 — criterion precision after outside review (2026-10-20)

- Trigger: `corpus/lessons/round-12-verifier-spotcheck.md` D1 identifies
  KQ15's mistaken “distinct nonzero exits” and capture/comparison wording.
  The implementation already distinguishes finding IDs with exit classes
  1/2/2; valid code and historical criterion bytes are preserved.
- Declared C1 calibration (lowest assigned 7 versus operability 8):
  two effective criterion discrepancies → target zero. Fixed denominator
  is the two routed formulations, not a corpus-wide truth claim.
  `corpus/lessons/round-13.md` Gate/Mistakes and
  `.ufo/waves/round-13/claims.json` carry the scope and rejection decisions.
- Appended KQ16 learns that disagreement without a new admission method.
  Source S033 supports `git cat-file blob` comparison semantics separately
  from S032's `git show` capture semantics; method documentation never
  proves a recorded comparison occurred or establishes present endpoints.
- The outside review's quality-attribution item is addressed explicitly:
  round-12 quality rests on the stronger D4 interpretation in
  `corpus/knowledge/served-identity-crosswalk.md`, not gate machinery alone.
  No new serving-knowledge quality or expansion delta is claimed here.
- One validated 32-seat wave, one unchanged taskCall, canonical planner held
  by L1; advice is author-side, never independent admission. Specs, registry,
  dispatch and roles live in `.ufo/waves/round-13/`.
- No tool installation, endpoint/config/service mutation, timer, route change
  or credential inspection. No inherited uncommitted lane work. Existing
  outside verifier lessons remain read-only. No new L0 operator decision.
- Measurement receipts and measured work revision are appended after final
  integration; unrun checks are not asserted as passed.

### round-13 attribution correction and static-review limits

The phrase “learns that disagreement” in the entry above is superseded:
CloseKamaR12 agreed with all sampled gate decisions; D1 is outside criterion
precision debt, not a new admit/reject disagreement. That closure already
credited round-12 discernment subject to this wording repair. Round-13
trends are **expansion unchanged; quality unchanged; discernment unchanged
pending outside sampling**. The calibration repair is still a bounded
correspondence improvement, score 7 → 7, not discovery or new knowledge.

The earlier author critic `.ufo/waves/round-12/advice/AttackSourceCuration.md`
already flagged capture/comparison conflation; the previous sweep fixed its
lesson but missed KQ15. `corpus/lessons/round-13.md` mines that own miss.
The outside D1 and static code/receipt review establish the two substantive
defects. Red-before phrase absence is a documentation-conformance count,
not independent semantic falsification; its isolated mutations demonstrate
only the bounded checker's failure behavior.

Capture with `git show` is author-recorded provenance, not inferable from
matching bytes. Comparison uses `git cat-file blob`, independent of the
manifest but sharing the same repository object store. Exit mapping applies
to primary findings; `snapshot_tampered` can coexist with source mismatch
and still exit 2. The old fidelity.py:55–56 “every exit-2 finding” comment
is inaccurate because `unpinned` ranks below `source_mismatch`; its code
and historical receipts remain unchanged and the comment is marked here
and in SKILL/lesson, not treated as current authority.

## round 13 — measured work and author disposition (2026-10-20)

- Work commit `641e1b6f1bef0e12d14c2e23388d7592ff0cb594` carries KQ16,
  bounded textual gate/frozen inputs, SKILL registry, source S033, corpus
  navigation and the 32-seat evidence. Every change above belongs to the
  criterion-precision trigger at this LOG's round-13 entry.
- Executed once after integration: `python3 .ufo/waves/round-13/measure.py
  --manifest .ufo/waves/round-13/frozen/expected.json`, selecting frozen
  before/after QUALITY separately: before exit 1 `documentation_mismatch`,
  missing2; after exit 0 `clean`, missing0. Live default exits 0 with the
  original git blob, preserved prefix and final QUALITY at measured HEAD.
  `.ufo/waves/round-13/acceptance.json`: ok true, errors empty.
- `--selftest` exits 0, ten passed / zero failed. Symmetric omissions,
  reintroduced exit/comparator wording, contradictory roles/values and
  missing active row fail with their committed expected findings/counts;
  tampered frozen input exits 2 `snapshot_tampered` before counting.
  Literal counts and controls are bounded conformance, never semantic truth.
- Independently retrieved start git bytes equal frozen-before; final QUALITY
  equals frozen-after; original byte prefix preserved. Existing S001–S032
  row strings unchanged; only S033 added. The receipt records full commands,
  digests and raw streams. No old fidelity/serving gate was rerun.
- Required final source validate and census both exit 0:
  `.ufo/waves/round-13/sources-final.json`; rows32→33/A29→30/mined22→23,
  B0/C3/queued5/rejected5 unchanged. Before and after validation retain
  scoped W04 S031; no invalid tier/status or missing registry.
- Author verdict: C1 calibration improved, numeric score 7→7 (delta0);
  every other axis unchanged, no observed harm in this scope. All three
  learning trends unchanged. Independent round-13 closure must sample
  admits/rejects before admission; no promotion is asserted.
- Final dispositions and limits:
  `.ufo/waves/round-13/integration-review.json`;
  `corpus/lessons/round-13.md` measured section. No tool installs or new L0
  question. Runtime restoration/timer disposition remains operator-owned.

## round 14 — executable offline Ollama evidence reconciliation (2026-10-20)

- Trigger: latest SCORECARD plan requested an actual serving-domain move after
  two bounded wording/evidence rounds. Existing `served-identity-crosswalk.md`
  holds tags/ps and digest-join concepts but no executable offline replay.
  C1 calibration capability targets the lowest assigned axis (7 versus
  operability 8), with score held 7 → 7. `claims.json` and `rulings.json`
  under `.ufo/waves/round-14/` fix scope, before state and conflict precedence.
- Changes: `tools/kama-ollama-evidence.py`, independent literal
  `tests/ollama-evidence/cases.json`, measurement runner, source-grounded
  `corpus/knowledge/ollama-evidence-replay.md`, KQ17, SKILL registry and corpus
  navigation. Each belongs to this one capability claim. S012/S031 fields
  were reopened; strict joins and ps remote-field handling are lane inference.
- Outside round-13 D2: append historical count-table clarification in
  `corpus/lessons/round-14.md`: redirected manifest has source-only mismatch
  count 1 under verified anchor, outer `manifest_invalid` exit 2. Historical
  lesson, receipts, implementation and all non-author files remain unchanged.
  This is routed presentation-debt resolution, not a second axis claim.
- One validated 32-seat wave is dispatched unchanged in one task call;
  L1 canonical planner plus bounded revenger data-walk. Seats never execute
  verification. Every report and registry binding is committed as evidence.
  Existing endpoint probe, consumer registry, snapshots, external services,
  routes, credentials and operator configs remain untouched.
- New capture classifier never contacts a runtime. Readiness is always unknown;
  input origin, timing and same-daemon identity are not established. Exact
  metadata correspondence is not present serving capability or permission to
  route. Final measured revision, command outputs and per-axis disposition
  are appended after integration. No tool installs or new L0 decision yet.

## round 14 — committed measurement and capability admission by author (2026-10-20)

- Work commit `e545ed99aaa519196a2a7779b0a293b2ce4c765c` is pushed.
  `.ufo/waves/round-14/acceptance.json` records actual commands/streams and
  named revision: absent tool0/51 supported exit1 → final51/51 matches exit0;
  actual draft49/51 exit1 → corrected51/51; selftest51/51 exit0 `clean`.
- Current draft implementation mistakes: remote marker preempted missing
  digest, and no-tags return preempted duplicate ps selection. Preserved actual
  draft plus AST-derived causal control reproduce the same two named failures.
  The causal control changes only `classify()` back to its actual draft
  ordering; all other final-source bytes remain identical. This satisfies the
  mistake fix's fail-capability obligation without inventing prior behavior.
- Counting command: `python3 .ufo/waves/round-14/measure.py --tool PATH`,
  shared fixed oracle SHA256
  `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4`.
  Six-field assertions cover exit/finding/schema/reported-exit/readiness/scope.
  Fixed findings10/3/10/5/5/18; constant-answer maximum18/51.
  Same oracle supports selftest and measurement, not independent authority.
- `SCORECARD.md` now adds demonstrated `ollama-offline-evidence-replay`,
  first-working round14. C1 calibration improved, score7→7; other axes
  unchanged. Expansion improved through executable repertoire only; quality
  and discernment unchanged pending new knowledge/outside sampling. No live
  Ollama integration, current serving state or readiness is claimed.
- Final required source validate/census exit0, rows33→33/A30/B0/C3,
  mined23/queued5/rejected5 unchanged; allowed S012/S031 used-by additions
  only. `preservation.json` records all five instruction/ledger prefixes true,
  all immutable source cells true and all25 protected tracked files equal.
- One 32-seat wave, one provider-failed scout, no replacement; roles and
  validated payload/seat reports retained. All verification was L1 final
  execution after owners finished, never sibling gates. No tool installs,
  new L0 questions, operator config changes or self-certified promotion.
  Final author verdict and historical D2 clarification:
  `corpus/lessons/round-14.md`; outside closure still owns admission.

## round 15 — executable duplicate-corpus admission repair (2026-10-20)

- Trigger: non-author `corpus/lessons/round-14-verifier-spotcheck.md` R1 found
  the runner promised duplicate rejection while enforcing only a minimum
  unique-name count. R2 requires partial-output versus terminal-success
  clarification. Both discoveries are credited to CloseKamaR14.
- C1 calibration, the lowest assigned axis (7 versus operability8), repairs
  the duplicate predicate only. Before source is preserved with pinned
  revision/path/digest at `.ufo/waves/round-15/frozen/manifest.json`; same
  new child-CLI matrix must expose that defect and pass after correction.
  Numeric calibration stays7; no arbitrary-input mastery or new runtime.
- `tests/ollama-corpus-guard/` supplies literal invalid controls above the
  minimum-cardinality threshold and valid controls. The harness invokes the
  actual runner and classifier, with temporary observation of invocation
  boundaries. Expected values are committed independently of recomputation.
- Named historical corrections and admit/reject decisions live in
  `corpus/lessons/round-15.md`; KQ18 adds the missing discriminating
  corpus-validator criterion. No old receipt or lesson is rewritten.
- S012 was reopened for the loaded-memory versus readiness boundary, not
  vendor authority over the lane's corpus policy. Source handling, all
  actual commands/exits and measured revision are recorded after integration.
- First two 64-seat build dispatch attempts were completely refused with
  the session-wide background-job limit100; no agents spawned. One direct
  unchanged retry subsequently spawned64. Refusal and validated payload
  evidence are retained under `.ufo/waves/round-15/build/`.
- L1 holds the canonical planner seat; bounded PlannerWalk is a revenger.
  No per-task model, route mutation, host service action, installation,
  consumer modification, credential/session/database access or promotion.

## round 15 — committed red/green measurement and bounded verdict (2026-10-20)

- Initial pushed implementation `70af36c2b15b46d3b4b3c15ef20459cff640dfaf`
  added the two-line guard. Falsification prompted explicit declared-nonblank
  scope in active prose, the private fork-exec audit event and a final-prose-
  matched causal control. Final measured/pushed work revision:
  `4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`.
- Counting command `python3 tests/ollama-corpus-guard/check.py --runner PATH`
  uses the same50 literal tests: original snapshot23 passed/27 failed exit1
  → repaired50/50 exit0; predicate-only red23/50 exit1. The old/source
  correspondence, literal digest and sole-predicate causal delta are
  verified in `.ufo/waves/round-15/fidelity.json`.
- Duplicate controls' classifier/Popen invocations483/483→0/0; positive
  controls402/402 retained. The exact corpus error, null per-case findings/
  exits and zero audited process events distinguish real rejection from
  missing-tool or unsupported behavior. Full nested streams/results are
  retained; summary `.ufo/waves/round-15/acceptance.json` is ok true,
  errors empty. No command is inferred from another run.
- New guard selftest exits0,50/50; same oracle as measurement, not independent
  corroboration. Original `.ufo/waves/round-14/measure.py` on its original
  corpus exits0,51/51 exact findings/exits/scope. No live endpoint/probe,
  current readiness or service restoration is claimed.
- Required source validate and census exit0 at both ends; rows33→34,
  A30→31, mined23→24; B0/C3/queued5/rejected5 unchanged. New own-workS034
  records outside R1's original-code diagnosis; only existing S012 used-by
  changes. Row growth earns no coverage/capability/discovery credit.
- C1 calibration improved, score7→7; all other axes unchanged. Expansion,
  quality and discernment unchanged: this is measurement-guard enforcement,
  not newly held serving knowledge or independent outside15 judgment.
  No new capability row or promotion. Final lesson:
  `corpus/lessons/round-15.md` §Executed author disposition.
- Validated build64/falsify32, actual total96. Build60 complete/4 provider-
  failed scouts, no replacement; falsify32 complete/0 failed. Refused
  dispatch attempts spawned0. Canonical planner is L1, bounded data-walk
  revenger. Reports/role mix/handles preserved under the round15 wave.
- Pacman pause was relayed to live seats and added before falsify dispatch.
  No installs/updates. Disclosed seat search/syntax/in-process-evaluation
  deviations are recorded in the lesson; excluded as measurement evidence.
  Host-cap mechanics were reported to Main/kumitate, not absorbed into
  endpoint ownership. No new L0 question; existing operator runtime/cadence
  decisions remain open. Stale-lane: no other kama mission open.

## round 16 — loading-envelope verdict and live llama.cpp lifecycle (2026-10-20)

- Start `20e392ea683a36bc223eb7cb45897acfb45456a3`, clean tree, nothing
  inherited. Assignment operability + calibration; calibration 7 is lowest
  (7 versus operability 8); no stagnation waiver.
- Motivating evidence: L1 smoke at 10:17 -03 saw a real b11755 llama-server
  answer `GET /v1/models` with 503 `{"error":{"message":"Loading model",
  "type":"unavailable_error","code":503}}` while loading; the frozen probe on
  a stub of that body returned `FOREIGN_SERVICE` / `non-2xx-non-model-http`
  exit 2 ("non-2xx HTTP from a non-model service").
- C1 calibration: `MODEL_LOADING` for the exact envelope only (KQ19), with
  appended corrections in five knowledge entries, the registry header comment
  and SKILL.md. C2 operability capability: `tools/kama-llamacpp-live.py` plus
  `tests/llamacpp-live/check-receipt.py`.
- Install (operator tooling directive 2026-10-19, pacman paused): llama.cpp
  b11755 official release asset `llama-b11755-bin-ubuntu-x64.tar.gz` (sha256
  `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, equal to
  the GitHub API digest) into `~/.local/opt/llama-b11755`, linked
  `~/.local/bin/llama-server`; reason C2. Model `stories260K.gguf` (sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`) into
  `~/.cache/kama-shokunin/models/`.
- Build wave: 81 seats validated under policy v2 (64-100) and dispatched in one
  task call: executor 16, scout 20, reviewer 14, critic 6, sentinel 2,
  connector 8, revenger 4, scribe 10, simplifier 1. Canonical planner is L1;
  `RevengerPlannerWalk` is the bounded planning data-walk. Provenance:
  `.ufo/waves/round-16/build/validation.json` (argv, cwd, three environment
  bindings, `taskCall` sha256).
- Lesson `corpus/lessons/round-16.md`; sources S035-S041 added, S017 used-by
  extended. Measured results follow in the next entry.

## round 16 — committed measurement and bounded verdict (2026-10-20)

- Measured and pushed revision `726f737a942f1606d66e032f1efbcbb6f689ccf1`
  (first implementation `b8e485c` was not final). Receipt
  `.ufo/waves/round-16/acceptance.json`, ok true, errors empty.
- C1: `python3 .ufo/waves/round-16/measure.py` exit 0. Frozen probe
  (`93ee4302…cd64` = blob `20e392e:tools/kama-probe.sh`) 55 pass / 17 fail
  exit 1; current probe 72/72 exit 0; changed verdicts exactly the 17
  `MODEL_LOADING` rows; matrix set digest and counts pinned. Doc ledger
  `stale-statements.py`: 17 uncorrected at `20e392e` → 0 at HEAD. Calibration
  score 7 → 7.
- C2: live tool exit 0, 10/10 checks, gate `VALID` with model, server, probe
  and tool pins; frozen-probe control 10/10; the loading window was captured
  live (38 exact-envelope 503s on `/v1/models`) and its body replays as
  `MODEL_LOADING` (current) versus `FOREIGN_SERVICE` (frozen). Controls: digest
  mismatch exit 3; ports 34113, 8080 and listening 631 exit 2; nothing left
  running. Capability `live-llamacpp-lifecycle` added; operability 8 → 8.
- Corrections appended in seven knowledge files (vocabulary, loading state,
  harness count, round-15 defect 5) plus SKILL.md, README, registry header.
  The earlier entry's "five knowledge entries" counted only the
  vocabulary/loading subset.
- Falsify wave: 79 seats validated (policy v2) and dispatched in one call:
  reviewer 33, scout 10, executor 9, critic 8, connector 6, mutation-tester 4,
  revenger 3, scribe 3, sentinel 2, simplifier 1; 79 completed, 0 failed.
  Provenance ledger `.ufo/waves/round-16/falsify/provenance-ledger.json`
  (argv, three environment bindings, `taskCall` sha256 `72e81bc6…0812`, spawned
  attempt bound to it). Round total 160 seats, 0 dead.
- Repairs and remaining debt: `corpus/lessons/round-16.md` §Falsify wave.
  Process incidents M6 (a seat ran `measure.py`; restored) and M7
  (session-store traversal recurred) are recorded, not evidence. One misrooted
  seat report moved from the fleet root into the lane (byte-exact, `cmp`).
- Trends (author): expansion improved, quality improved, discernment unchanged.
  L0 question filed on the lane-owned fixture and the persistent install.
  Tools installed: llama.cpp b11755 (official release asset into
  `~/.local/opt`, linked into `~/.local/bin`) and the pinned GGUF; no pacman.
  Stale-lane: respawn-per-round; no other kama mission open.

## round 17 — graded fields and fail-capable live checks (2026-10-20)

- Start `cff9e62f05aa7cfb9059444f62eb787100719713`, clean tree, nothing inherited.
  Lane VCS is jj-colocated; commits only through `scripts/hyaku/jj-lane.sh`.
- Motivating evidence, C1 (calibration): round-16 `MutateHarness.md` — 5/5
  check.py grading mutants survive the only detector; `served_model` and route
  ungraded; a non-object probe row tracebacks. C2 (operability):
  `ReviewLiveHarnessCode.md` — `health_ready`, `teardown_exited`,
  `teardown_port_closed` cannot fail on the behaviour they name; the loading
  envelope is graded by nothing; a teardown fault escapes without a receipt.
  Mined mistake: S041 edited in place (routed defect 3). jj risks: round-13
  live gate false failure, `.ufo/state/` unignored.
- Build wave: 82 seats validated under policy v2 (band 64–100) and dispatched as
  one task call after one job-cap refusal (82 refused, 0 spawned) and gated
  retries: scout 19, executor 15, reviewer 14, scribe 10, connector 8, critic 6,
  revenger 4, sentinel 2, simplifier 2, mutation-tester 2; 82 completed, 0
  dead; first-line verdicts 34 confirm / 32 partial / 1 refute / 15 n/a / 0
  nonconformant. L1 holds the planner seat; the planning data-walk rode
  `RevengerPlannerWalk`.
- Landed: `tests/probe-verdicts/check.py` (graded served_model and route,
  per-row malformed and non-UTF-8 output), `tests/probe-verdicts/fault-controls.py`,
  `.ufo/waves/round-17/c1/mutants.py`; `tools/kama-llamacpp-live.py` receipt v2,
  `tests/llamacpp-live/check-receipt.py` v1+v2, `tests/llamacpp-live/controls.py`;
  `tools/sources-append-only.py`; `.ufo/waves/round-13/measure.py` exit 4;
  `.ufo/waves/round-17/count-verdicts.py`, `dispatch-provenance.py`; SOURCES
  S042–S046; QUALITY KQ20–KQ22; appended corrections (OPTIONS wording) in
  README, SKILL.md and three knowledge entries; `.gitignore` (`.ufo/state/`,
  `__pycache__/`); `AGENTS.md` VCS rule.
- Measured (L1): C1 fixed-detector accepted faults 3 → 0, full-detector mutants
  7/8 → 10/10 killed (pair detector 1/8 → 1/10); C2 accepted-bad controls 6 (+1
  inconclusive) → 0; three real b11755 v2 runs 11/11, gate `VALID` with four
  pins. No-harm: probe and matrix bytes unchanged; round-16 measure PASS in a
  `/tmp` clone; snapshot 30/0; v1 receipts `VALID`. Details:
  `corpus/lessons/round-17.md` §Measurements, `SCORECARD.md` §Round 17.
- Measured lane commit (build): `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (landed
  by the helper). `PROVINCE.md` (+round-17 note) and `SHONEN.md` (box-2 pointer
  extension) were also in that commit.

## round 17 — falsify wave and corrections (2026-10-20)

- Falsify wave: 80 seats validated (policy v2) and dispatched in one task call at
  18:35:33Z after capacity-gated waits (no refused call): reviewer 34, scout 8,
  critic 7, executor 6, connector 6, scribe 6, revenger 5, mutation-tester 4,
  sentinel 2, simplifier 2. 71 completed; 9 failed on 429 rate limits (m_opus ×7,
  m_haiku ×1, one no final message); 7 left no report (dead, not respawned). Seats
  spawned after the orchestrator's routing notes ran on the routes then in force.
  First-line verdicts: 22 confirm / 45 partial / 0 refute / 5 n/a / 1 nonconformant.
- Every C1/C2 number re-ran identically in `/tmp` clones; no-harm reconfirmed.
- Corrections (appended): S047 supersedes S043 (lost-signal window); SKILL.md
  §Round-17 seven cells and the round-13 row exit 4; knowledge-entry correction
  (signal window, replay limit, saturation false failure); `AGENTS.md` exit 3/exit 4
  wording; lesson §Falsify wave with dispositions, debt and M8; SCORECARD falsify
  verdicts and planned row. Debt named in the lesson.
- Round total 162 seats (82 + 80). Tools installed by L1 or its seats this round:
  none recorded (two `uv tool` installs, ruff 0.17.1 and vulture 2.16 at 13:14 -03,
  exist on the host and are not attributed to any kama seat report).
  Stale-lane: respawn-per-round driver; no other kama mission open.

## round 18 — receipt outcome classification and named-survivor calibration (2026-10-20)

- Declared C1 operability (8 → 8), C2 calibration (7 → 7; lowest assigned axis).
  Motivation: outside round-17 R4's false failure on zero 503 observations;
  R5's six untested v2 checks; R6's schema/argv/transitions/ownership/exception
  debts; R7's surviving detector weaknesses and refused-count zero.
  Full contract and bounded universe: `corpus/lessons/round-18.md`.
- C1: v3 tri-state receipt + schema-floor gate, exact argv (raw model.arg retained),
  transition loading bodies and coverage checked, sourced Linux tcp6 ownership,
  BaseException cleanup/receipts. `tools/kama-llamacpp-live.py`,
  `tests/llamacpp-live/check-receipt.py`, `tests/llamacpp-live/controls.py`.
  S048/S050/S051/S054 are load-bearing; S052 is convention only.
- C2: malformed-decoder rows and process-group timeout cleanup, expanded
  fault-controls and their self-checks, append-only selftests (opened/blank lines),
  textual refusal provenance. `tests/probe-verdicts/`, `tools/sources-append-only.py`,
  `.ufo/waves/round-18/dispatch-provenance.py`, `.ufo/waves/round-18/c2/`.
  Numeric survivor outcomes are recorded after the official counting runs.
- Frontier: S048–S054 opened/curated; new
  `corpus/knowledge/loopback-listener-ownership.md` holds previously absent
  mechanism; `corpus/README.md` appends its coverage row and S047 correction.
  KQ23 mines round-17 M8 and KQ24 distinguishes an unobserved trigger. S047's
  missing Gate row is appended in the new lesson; historical lesson untouched.
- Integration found a paired synthetic/source-URL bug (real receipt rejected)
  and an ids-intact ready-capture 503 gap; both repaired in tool/gate with retained
  selftest coverage. Evidence: round-18 lesson M6/M7.
- Build wave refit 95 → 75 after one wholly refused 95-seat dispatch and capacity
  gating; validated under policy v2 and dispatched as one taskCall. L1 is planner.
  Work is integrated from isolated seat clones, not concurrent production writers.
  Specs, validation, assignments and refused payload retained under round-18/build.
- Round-17's final outside discernment verdict is **improved**, superseding the
  author's pending/unchanged reading in SCORECARD line 702
  (`round-17-verifier-spotcheck.md:217–221`). Round-18 author/seat checks do not
  themselves satisfy the independent non-author spot-check duty.

## round 18 — measured c6dc46f and counter-interface corrections

- Landed implementation `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`.
  Official `python3 .ufo/waves/round-18/runs/run.py`: 32 commands, 30 expected,
  two counter own-faults retained (not called passes). Three real v3 runs each
  11/11, schema-floor/four-pin VALID; legacy pairs unchanged; snapshot 30/0 and
  round-16 measure PASS in sandbox clone. Commands, outputs and exits in `runs/`.
- Corrected C1 counter's two-axis seam: expected-outcome bucket determines
  misclassified count; observed classification remains rejected-targeted for
  frozen k16. Exact raw regression added; counter selftest 38/38 in owner clone.
- Corrected C2 counter's independent-arm combination: a named targeted selftest
  kill survives an inconclusive main arm; main exit2 alone is still inconclusive.
  Both arm outcomes retained; regression cases give selftest 60/60 in owner clone.
  No subject predicate or control was weakened by either counter repair.
- S055 records the measured real v3 receipts; old SOURCE cells remain immutable
  except the logged S047 used-by addition. Lesson records the two execution
  conformance disclosures (late canonical reread; the argv probe's brief wildcard
  launch). Final claim measurements await corrected counting invocations.

## round 18 — recovery attempt 2: falsify integration, clean-tree measurement, residual call (2026-10-21)

- Attempt 1 died on provider quota (`lane-dead-no-report`, fleet `.ufo/watchdog.log:536`)
  leaving pushed checkpoint `101f3991…`. Re-verified and reused: commits `c6dc46f`/`1c325b2`,
  both wave specs/registries/advice, the live receipts (restored to their checkpoint bytes
  after the recovery run overwrote them in place), the frozen manifest,
  strict-canonicalisation tooling, and the corpus text already integrated at the checkpoint.
  Discarded: the 20 never-assigned build members, the 10 dead falsify seats, and the
  pre-repair counter artifact (kept under `runs/pre-repair/`).
- Fixed from the falsify wave (76 seats; 66 reports: 28 confirm / 34 partial / 1 refute /
  3 nonconformant): the `PrivacyScope` refute (no `child_env_keys` value in diagnostics, plus
  raw-token and non-string cases), `GateCaptureHashes` H1 (`/health` loading envelope cannot
  stay NOT-EVALUATED), `ConnectTsukuroi` impl binding (fifth pin + field↔tree cross-check),
  `CounterC1` seams (row/count under-report, declared exclusion, arms, bucket-gap gap),
  guarded finalizer signal-handler restore (`ToolFaultPaths` P2, unit-tested), and C2
  docstring/count/empty-arms corrections. Corpus appends: ownership honest-limit and
  endianness; lifecycle window-exclusion evidence and the five-pin residual; lesson
  dispositions and M8/M9.
- Residual call: 7 reviewer/critic seats (the ≤8 allowance; no 64–100 wave with ≤49 seats
  left): five confirm, two partial, and `ResidClaims` partial on commit labelling and the
  overwritten receipts. Fixes and named residuals are in `corpus/lessons/round-18.md`
  §Residual falsification call.
- Work commit `0c75c611…`, evidence commit `888cd384…`, harness commit `eb78788b…`; the
  official `python3 .ufo/waves/round-18/runs/run.py` on that clean tip ran 32 commands with
  every expected exit and harness exit 0. The measured tree is the tip recorded in
  `runs/commands.json`.
- C1 (operability 8 → 8): accepted-bad 5 → 0, good-rejected 1 → 0, misclassified 1 → 0,
  uncontrolled 0 → 0; gate_flip_arms 16 → 17; counter exit 0 with no faults.
- C2 (calibration 7 → 7): 15 named items; before survived 11 / miscount 1 / accepted 3 →
  after killed 11 / correct 1 / handled 3; exit 0; the family-b rerun diverged 0 times.
- Census 47 → 56 rows (A 44 → 53, C 3; mined 37 → 45, rejected 5 → 6), both exits 0;
  validate keeps three W04 duplicates (S031, S043, S056).
- No installs or host mutations. Stale-lane: respawn-per-round driver; no other kama mission open.

## round 19 — revision-qualified citations and the install-tree pin (2026-10-21)

- Routed round-18 defects fixed first: residual verdicts are 4 confirm / 3
  partial with a committed dispatch record; S055/`Gate` pointers are
  revision-qualified; the SCORECARD C2 command erratum names `--json`; the
  6-reviewer/1-critic split is in `residual/assignments.json`.
- C1 calibration 7 → 8: `tools/citation-provenance.py` +
  `registry/required-citations.json` bind `cite(rev, path, sha256=…)` tokens to
  a required document and verify the blob at that revision. Counting:
  missing=3 exit 1 → missing=0 verified=3 exit 0; selftest 15 cases
  (`evidence/c1-counting.txt`).
- C2 operability 8 → 8: sixth gate pin `--expect-install-tree-sha256`, passed
  by the runner from the producer's `install_tree()` digest;
  `tests/llamacpp-live/install-tree-grid.py` (with `--selftest`, absent defaults
  fail closed). Counting: consistent swaps `rejected=0/3` exit 1 → `3/3`
  exit 0 (`evidence/c2-grid.txt`).
- Frontier: S057 (man7 ld.so(8)) row + lesson Gate (10- and 11-word located
  quotes); census 56 → 57 (A 54, C 3; mined 46), exits 0; validate exit 0 with
  the three expected W04s.
- Waves: build wave 64 seats (scout 18, reviewer 12, executor 10, critic 6,
  scribe 5, connector 4, mutation-tester 3, revenger 3, sentinel 2,
  simplifier 1; planner = L1). Falsify wave validated at 66 seats; dispatch
  refused at the host job cap (66/66 failed to start, none spawned, recorded in
  `falsify/refused-attempt-1.json`), never split or shrunk. Wave-1 findings
  integrated where they were claim-critical; the rest are named debt.
- No installs or host mutations. Stale-lane: respawn-per-round driver; no other
  kama mission open.

### round 19 erratum (appended)

- The round-18 residual verdicts are **4 confirm / 3 partial** (not "five
  confirm, two partial"); the dispatch record is
  `.ufo/waves/round-18/residual/assignments.json`.
- C1 lands **calibration 7 → 7** (improved-bounded), not 7 → 8: a fresh critic
  refuted the "machine-checkable for all four defects" wording; the checker
  binds three registry-row digests in the bound document and does not check the
  sentence beside a token. `gate-live-1` is re-pinned to `1b85a24`
  (`1cb5a41b…`).

## round 20 — corrections to round-19 records (2026-10-21)

- Round-19 C1 `missing=3` / `verified=3` at 1146 and "three registry-row
  digests" at 1172 are superseded: final registry **4**; before missing4,
  after verified4; evidence `round-19/evidence/c1-counting.txt`, measured
  `028235e6`. Selftest printed15 (earlier five-case wording was stale).
- CritC1Inflation/CritAxisHarm/TreeCap were build seats, not falsify seats;
  round-19 falsify spawned0/66. The outside closure's expansion verdict was
  unchanged (a source row alone is not new repertoire).
- "Dispatch record" for round-18 residual assignments is superseded by the
  explicitly retrospective `assignments.PROVENANCE.md`; verdicts4/3 are
  supported, roles6/1 are assertions without original dispatch evidence.
- Round-18 lesson line42 in-place rewrite (`30ed378`) recorded by a named
  appended correction quoting original and superseding wording verbatim.
- Clean-commit round-19 selftests (37bd4c5), retrospective census receipts
  (56→57), stale-count sweep and SOURCE append-only checks retained under
  `.ufo/waves/round-20/build/out/`; none claimed original round-19 receipts.
- Removed authorized `/tmp/kama-r19-*` scratch (~5.9 GiB), after stopping
  orphan ScorecardErratum strace/survivors process tree. Elapsed24:31 total,
  about13 minutes after round completion (not24 minutes after completion).
  Exact paths and action receipt `round-20/evidence/r19-scratch-removal.txt`.


## round 20 — landed implementation and committed measurement

- Declared C1 calibration7→7 (named error classification), C2 operability8→8
  (new offline GGUF declared-identity replay capability). Motivation and sourced
  Gate: `corpus/lessons/round-20.md`; mistakes M1–M6, KQ25–KQ27.
- Work/frozen population landed `33a6777866d0f63d894ef21bc863486bcb35b56c`;
  counting tools/recipe completed at measured
  `0957ce619789d13bb5779606078fa1498114d2c7`.
- Official `python3 .ufo/waves/round-20/run.py --recipe
  .ufo/waves/round-20/recipe.json --out .ufo/waves/round-20/runs/0957ce61`:
  21/21 expected exits, harness0. C1 cells15, false classes6→0, no unrun/witness
  mismatch; C2 absent→working, fixtures23/23, real-file oracle and captured
  receipt engine-agreement. Model declares2048; captured train2048, props256.
- Source census57→64 (A54→61, C3; mined46→51, queued5→6, rejected6→7),
  validate0, five W04 duplicate URLs (S031/S043/S056/S060/S064). New knowledge
  entries cite mined sources, not row-count expansion alone.
- Citation checker now24 counted invocations, registry17 verified (4 old +13
  material revision/path instances); observed-digest branch fail-capable.
  Official gate77 mutation tally is committed; the record is not dirty-tree
  `working-tree-on-5b108c1a`. Survivor pure classifier checks49/49; no full
  42-run survivor measurement this round.
- Build wave72 spawned after one whole-call72 refusal and same-payload retry;
  original terminal70 completed/2 dead (CellDesign, SrcGateStandard), no
  replacement. Reports71, including SrcGateStandard's partial artifact;
  KnowGguf format nonconformant. Counts41 confirm/27 partial/2 refute/1
  nonconformant; terminal status is separate from first-line report counts.
- New capability row follows the executed demonstration; no model quality,
  current consumer health or authenticated execution claim. Cross-domain
  findings stay advisory; detailed conformance defects/limits in lesson20.


- R19 residuals re-verified and bounded: grid rejection now requires an emitted `INVALID` verdict (15-cell frozen/current census); citation observed-digest selftest case is fail-capable; the 13 R18 citation instances are in the 17-row registry and verify. R18 `SCORECARD.md:813`'s “they agree” is corrected at the end of the scorecard and in `corpus/lessons/round-18.md:474-480`: only summary/outcome/run-status fields agree; full results and tool hashes differ, and no R20 full 42-run survivor measurement is claimed.
- S051’s shifted source pointer is corrected append-only at `corpus/lessons/round-18.md:447-451`; the stable “S051 identity-label clarification” heading replaces an unqualified line range. The current source span is `corpus/SOURCES.md:210-215`; no registry cells were rewritten.

- **Erratum to S051 pointer wording above:** `SOURCES.md:210-215` is the S056 supplement; the current S051 identity-label clarification is at `SOURCES.md:217-222`. The R18 lesson's stable-heading/revision-qualified correction remains authoritative.
- S063 `used-by` old `—` → `corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-20.md`; appended S065 records the Python 3.14.8 `sys.exit(None)` zero-exit exception that narrows S061. Full detail and source quote are in `corpus/lessons/round-20.md` and its Gate supplement.
- Wave-2 coverage note: the C2 `v3-all-scalars` fixture has 12 expected `test.*` values, but the measure compares the selected identity projection, not those arbitrary scalar values; C2 remains limited to its declared identity fields. The grid signal/timeout guard mutants preserve the `error` class through fallback and only lose reason detail.

- S051 range after S065: the preceding `SOURCES.md:217-222` reference was current before appending S065; at the resulting tip the S051 identity-label clarification is at `SOURCES.md:218-223`. Use its stable heading / revision-qualified correction rather than another unqualified range.

- R20 falsify wave: attempt 1 cap-refused before spawning; after ≥180s the unchanged 86-seat payload spawned86. Roles reviewer60/mutation-tester17/scout6/critic2/connector1; 73 reports, 13 dead, no replacements; total round spawns158. `falsify/{dispatch-attempts.json,seat-failures.json,completion-summary.json,verdict-count.json}` records the accounting; top-level advice counts are confirm66/partial7/refute0/nonconformant0.
- Wave-2 integration: S063 `used-by` changed `—` → `corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-20.md`; S065 appends the `sys.exit(None)` exception for S061; S051 current range is now `SOURCES.md:218-223` after S065 (M8's old `210-215` and the pre-S065 LOG range are time-bounded). The `CellGridRealInvalidVerdict` source is additionally bound to clean measured commit `0957ce6` and file SHA-256 `d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`.
- GGUF fixture metadata correction: `make_fixtures.py`/`expected.json` old max-KV1,000,000 and max-string16,777,216 → current parser defaults100,000 and1,048,576; fixture-basis text now separates the upstream uint64 fact from local parser default. Regeneration reports 23 fixtures and unchanged `SHA256SUMS` digest `ab51c80f26ce1c155f5b5e8377a6363df9fa93ff6ac1669000a9aaf70d995812`; parser behavior unchanged. `v3-all-scalars` arbitrary scalar-value coverage and timeout-reason precision remain unclaimed.
- Trend reconciliation: R19 outside verifier judged expansion unchanged and discernment improved after its two-admit/one-reject sample (`round-19-verifier-spotcheck.md:160-172`). R20 expansion is improved for its first-working GGUF capability row, quality improved within the bounded repairs, and discernment unchanged without a new outside R20 sample; details appended to SCORECARD and round-20 lesson.

- First post-manifest measurement at `c7311039` failed closed: `gguf-measure-selftest` and `gguf-measure` both exited2 because `measure-reference.json` still pinned `1ffe884a523fb85866ac43775fee0a5be1f69398c09a3dae8b8832f39c9f7f9f` while regenerated `expected.json` hashed to `714226dfb6ae578fb1718f6c19b76c1328cf9dfc74ced01e5f280b39bfeccd48`. The retained output says `snapshot_tampered` for all23 and `parser_attempted=false`; no C2 result was credited. Updated the reference pin exactly; the failed run is retained, followed by a clean-tree rerun after this commit.

- Second post-manifest run `04de7a87` still failed closed before fixture parsing: `measure.py` expected reference SHA `fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6`, while updated `measure-reference.json` is `e3f0349ab13cf08c7934d43c71a6ec27c7283150e90e39f3dd2d63f9be9c7bcb`. `gguf-measure` credited no fixture outcome; `REFERENCE_SHA256` now matches the updated reference file. The run is retained as a second fail-closed diagnostic, not a pass.

- Final corrected measurement: `run.py` at `9add96e462e62dc5141cd02730b7a699268b3513` ran 21/21 commands at expected exits, harness0 (`runs/9add96e4`). C1: 15 cells, frozen misclassified6/current0, mismatches0/unrun0. C2: 23/23 fixture predicates; no mismatches, snapshot tampering or unavailable rows; real-file oracle/receipt agree.
- Final S065 census: rows57→65, A54→62/C3, mined46→52, queued5→6, rejected6→7, missing0; `sources-validate`/`sources-census` exit0 with six W04 warnings S031/S043/S056/S060/S064/S065. The failed c731 and 04de measurements are retained but not credited.

- R19 verifier routed instrument-registration item is closed by `SKILL.md:652-654` at `0957ce619789d13bb5779606078fa1498114d2c7`: `citation-provenance.py`, `install-tree-grid.py`, and receipt-gate `--expect-install-tree-sha256` now have explicit rows and verdict/selftest contracts.

## round 21 — report landing audit and soname-aware install identity

- Motivation C1: the round-20 closure (fleet `221707d`) found report line 7's spliced hash and four Landed omissions; no instrument checked either. Motivation C2: R19 TreeCap — a soname retarget left every pin unchanged.
- Draft `a29bb84a`; build wave 86 seats; integration `1471344b`; first official measurement `b76727f3` 28/28 (`runs/b76727f3`), live v3 receipt with 10 links. Falsify wave 67 seats (1 dead: ConnectorSiblingReports, Antigravity 429 quota). Falsify fixes and final measurement are recorded in `corpus/lessons/round-21.md` §Falsify-wave integration and `SCORECARD.md` §Round 21.
- C1 calibration 7→7 detector: `report-landing-audit.py --rounds 10-20 --no-errata` exit 1, 9 defects; with ledger exit 0. C2 operability 8→8: grid frozen link 0/13 → current 13/13. Sources S066–S074 (rows 65→74).

## round 22 — helper I/O refusal and finite comparison calibration

- Declared C1 calibration7→7 at start `10271460cc575fc2280aa831e442726385fc2319`;
  motivating evidence: R21 SCORECARD Planned bare-helper debt and
  `corpus/lessons/round-22.md` M1. Existing producer backstop is distinguished
  from helper returns; no producer-level red-before or new capability claimed.
- Three `install_tree` OSError fallbacks now raise stage/member-specific
  SetupError with the original cause; successful sorted regular-file digest
  unchanged. Direct links-grid and e2e caller error boundaries migrated; receipt
  gate changes only its legacy-null explanatory comment.
- New finite matrix, selftest mutants and official recipe:
  `tests/llamacpp-live/install-io-grid.py`, `.ufo/waves/round-22/{run.py,recipe.json}`.
  Official clean-tree measurement and pushed hash are recorded in the appended
  results, not inferred from a dirty working tree.
- S075/S076 ground real operation errors; S077 rejects access-only remediation.
  Knowledge/SKILL supplements and KQ30 preserve helper/caller and null/partial
  distinctions, old receipt-schema compatibility and scan-time/race limitations.
- Build wave64 dispatched as one validated call; code-writing and scribe seats
  died before code delivery. The L1 integrated code directly; read-only advice
  mistaking these known L1 edits for seat writes is retained without rewriting.

- Prior outside closure (fleet rounds[406]) learned: R21's final measured
  commit7054dba1 has33 commands/0 mismatches, not the earlier b76727f3/28
  table; SCORECARD now appends that correction. R21 original wave deaths2
  (RegressSkillGates Haiku429; ConnectorSiblingReports Gemini429), reports
  build85/falsify66 at closure, not the stale still-running description.
- D2's marked-but-prose-only source corrections now have freshly reopened
  S078–S086 superseding rows; old S066–S074 stay unchanged. KQ31 rejects the
  missing-row pattern. Total new source rows this round12, including C1's
  S075–S077; this corrects the provisional three-row population above.
- D4 learned via a trusted-repositories-only warning and KQ32; no claim to
  repository-local Git-config/history/UTF-8 hardening. Broader hardening,
  prelaunch races, gate chain bound and JSON edge cases remain frontier
  rather than quietly certified by the narrow helper repair.

- Build accounting corrected/retained:64 unique seats,47 original successes
  and17 original provider deaths. Peer messages resumed the same ApiFix,
  CallerRepair and Matrix identities; candidates are preserved but not
  integrated. Latest build outcomes50 successes/14 failures; reports52
  include two terminal-failed partial reports. No replacement identities.
- Residual ordinary batch8 (under64 distinct attack items; no padded wave):
  three completed/five Devin-rate-limit deaths. Actual producer mutants5/5
  killed; independent claim critic found no blocker at971d4549, pending
  official measurement. Receipt paths and informational diagnostic suffix
  survivor are recorded in the round lesson; no exact-text guarantee.
- FinalSources reopened all12 initial rows and found missing knowledge
  used-by entries plus Python micro-version page drift. Used-by changes for
  S075–S080 are logged old→new in the lesson; freshly reopened S087/S088
  clarify series URLs without rewriting immutable cells. Final additions14.
  Official recipe includes each consecutive source-touching commit pair.

## round 22 — committed-tree measured results and publication

- Implementation landed971d4549; source/residual integration landed6433390a.
  Official recipe at clean input commit
  `6433390a5c8f4412c2410c114309ffced5c0572f` ran29/29 commands at expected
  exits, harness0, no timeouts/mismatches. Outputs are published separately
  under `.ufo/waves/round-22/runs/6433390a/`, not attributed as input files.
- C1 calibration7→7 verified: activated faults18, helper refusals0→18,
  null returns3→0, partial digests15→0, controls14/14 both arms; selftest8/8.
  Counting commands/stream hashes and population SHA are in commands.json,
  summary.json and the round lesson. Old producer backstop18/18 not credited
  as new behavior. Five actual-producer mutants killed with clean positives.
- No-harm receipt/producer/grid/legacy-receipt, error-census, GGUF23/23,
  citation17/17, snapshot30/0 and prelaunch3/3 checks meet declared exits.
  Final source rows88 (74→88), added A13/B1/C0, mined72/queued8/rejected8;
  census/validate0 with20 duplicate-URL warnings, missing0. Both consecutive
  source-touching commit-pair guards pass; all pre-round rows immutable.
- Trends: expansion unchanged; quality improved; discernment improved
  narrowly through learned prior outside D2/D4 feedback and KQ31/KQ32.
  No new capability/promotion, no model-quality/current consumer-health claim.
  Existing fixture/archive L0 questions retained; no new question or install.

## round22 — final report/source classification conformance repair

- Preparing mandatory verbatim source-validation output exposed a new
  calibration distinction: upstream40-hex values inside curated source URLs
  are not owned commit citations. Both actual repositories returned128
  missing for the upstream object; those lookups were not repeated.
  Old-script false-positive behavior is a static inference until the pinned
  red/green witness executes; the manifest declares expected old1/current0.
- Two fresh ordinary seats completed (executor ReportSourceFix and critic
  ReportSourceCritic); no replacements. L1 integrated committed-source URL
  occurrence classification, stricter nested-URL boundaries, unchanged Landed
  checks including its heading, and no hash-specific whitelist/errata row.
  An unused private section wrapper was removed with its maintained caller
  migrated. D4 untrusted-repo hardening remains unclaimed.
- Added a manifest-pinned synthetic CLI witness and its own CLI selftest;
  relocated it off the disposable clone. KQ33, SKILL registry and lesson M4
  record the distinction. This is within C1 calibration, not another axis or
  new serving repertoire. Original6433390a/29-command evidence is unchanged.
- Followup source/fixtures/recipe are under `.ufo/waves/round-22/report-source-fix/`;
  verification follows a clean commit and results append afterward. Total74
  unique seats,22 original provider deaths,57 retained reports; the2-seat
  ordinary followup's headroom grant was late and is disclosed in its roster.

## round22 — final scoped conformance results

- Followup implementation landed
  `80a6d07c09593191b7a6f86d92851fe3cc0619c2`; its clean-tree scoped recipe
  ran10/10 commands at expected exits, harness0, no timeouts/mismatches.
  The original6433390a/29-command run remains a separate measured input.
- Pinned report/census witness now observes the prior inference: old audit
  exit1/one false owned-hash finding → current exit0/zero, same synthetic
  repos/report, no actual lane/fleet Git writes. Auditor selftest50/50;
  witness CLI selftest6/6. Registered URLs classify by occurrence only;
  bare copies, unregistered/superset/Leads/worktree rows and Landed remain
  checked. No token-specific errata or whitelist.
- Historic12 reports retain9 raw defects/all9 corrected, required49,
  post-report5, invalid/unmatched/uncorrected0. Citation17/17 clean;
  helper current18/18 refusal and14/14 controls unchanged. Final source
  census/validate0, rows88, immutable-source guard0.
- C1 calibration7→7 verified narrowly; no new capability/axis/promotion.
  Final publication carries the followup receipts separately from measured
  input80a6d07c; the fleet report names every pushed round22 commit.

## round 23 — repository-local git state in the report landing audit (2026-10-21)

- Declared C1 calibration 7→7 (narrow D4 movement) for
  `tools/report-landing-audit.py`: on the graded rows of
  `tests/report-audit/repo-state-grid.py`, repository-local git state in the
  audited lane and fleet no longer crashes the auditor into exit 1, flips a
  verdict, hangs it, or runs a repository-configured program. Motivation: the
  base auditor promised "Errors are never verdicts" and unredirectable
  repositories (`4fe9339f:tools/report-landing-audit.py:42-45,79-81`); the
  first L1's probe saw tracebacks, false clean verdicts through replace refs
  and a lazy fetch that ran `core.sshCommand`. Lesson
  `corpus/lessons/round-23.md` (Gate, M1–M7, falsify disposition).
- Lane commits by the first L1 (CloseKama22): `e0f0434`, `34b2376`,
  `245a37f`. It died with the host session at 13:10:51 -03 mid-integration
  of the falsify wave; KamaR23-2 inherited the uncommitted integration,
  re-verified it, added the grafts-content check (C13/M32/S101) and the
  grid's session kill, and landed `e876b953e9da28d2dffd29c923052bc626148c27` (code) and the round's
  prose/evidence commit.
- Measured at `e876b953e9da28d2dffd29c923052bc626148c27`: grid `--arm both --json` exit 1 by design —
  current faults 26/26, contracts 4/4, controls 13/13, 0 tracebacks/
  executions/timeouts; frozen faults 0/26, contracts 1/4, controls 13/13,
  9 tracebacks, 3 executions, 2 timeouts. Mutants: exit 0; 31 mutants, 30 killed on grid exit 1, each with its failed rows listed (M16/M19/M22/M24 by contract rows F21/F17/F23/F24); survivor M20 (40-hex `%H` check). Selftest
  50/50. Rounds 10–22 ledger and `--no-errata` byte-identical between arms
  (`nh-history-parity` exit 0; 13 reports, 54 required, 9 raw defects all
  corrected). Evidence `.ufo/waves/round-23/final/`.
- Sources 88→101 (S089–S101; S095 mined→rejected, superseded by S096;
  S099/S100 supersede S092/S091). KQ34 added. Census/validate exit 0.
- Trades reported, not prettified: T01 blobless partial clone and F23
  paired promisor pack without config refuse where frozen gave a verdict;
  git ≥ 2.45 floor. Open channels and near variants are listed in the lesson.
- Seats: build wave 68 (1 dead: RevClaimScope), falsify wave 73 (4 dead with
  the host session: RowC01Clean, RowF07LogFollow, RowF09SignatureProgram,
  CritOpenHonesty); round total 141 of 200. Fleet incidents: four `.promisor`
  markers written into the fleet repo by a falsify probe (removed, M4); one
  scribe misroot swept into this lane (M5).

## round 24 — repair-first preregistration (2026-10-21)

- Round-23 outside closure, MANIFEST rounds[428], rejected-harmed:
  calibration improved but operability harmed. This supersedes any admission
  reading of the round-23 author verdict and its quality-improved trend.
  Disclosure of a trade does not waive the no-trade rule.
- Correction to filed `.ufo/reports/round-23/kama.md`: falsify wave has
  69 durable lane reports, not 68 (RowC03 wrote before its final response
  aborted); 40 of the 56 killed FIFO-process identities were retained, not
  all 56. Filed round-23 bytes remain immutable.
- Preregistered C1 calibration7→7 narrow: restore justified correct local
  verdicts on complete promisor-marked repositories while retaining
  no-lazy-fetch/execution isolation and refusing unavailable evidence.
  Expected outcomes are fixed before implementation in
  `.ufo/waves/round-24/preregistration.json`; base `0df800e8`.
  A metadata marker alone is not evidence of missing objects.
- Build wave validated at 64 seats; first call refused by background-job
  cap, unchanged payload spawned on the next attempt. Planner is L1;
  bounded data-walk is connector ConnPlan. Evidence in
  `.ufo/waves/round-24/build/`; no actual round-24 improvements claimed yet.

### Round-24 correction provenance refinement

CritEvidence's independent reading corrects the gloss above at
`d1b9d95:LOG.md:1417-1420`: the literal "68 reports" occurs in
`corpus/lessons/round-23.md:178`, not in the filed fleet report (whose
73 seats minus 4 missing reports already implies 69). The lesson count
is superseded by 69 durable falsify reports.

The old process claim is also narrower than the retained record proves:
56 was a matching-process count, while a different listing pattern kept
40 truncated identity rows (38 git, gpg-agent, scdaemon), not 56 identified
FIFO-blocked git processes. Only 19 retained rows could be linked to FIFO
fixtures; 16 counted identities were not retained. The matching count
became zero after cleanup, but this does not independently prove every
victim's identity or blocking cause. Retained listing and classification:
`.ufo/waves/round-24/build/out/CritEvidence/`.

### Prospective oracle correction before candidate inspection

The initial preregistration's missing-citation→unknown solely because of
promisor metadata conflicts with the original local-object contract
(`tools/report-landing-audit.py:12-19`) and the exact historical restoration
witness: its authorized errata correct a locally missing spliced hash.
CritScores identified that contradiction before L1 candidate inspection.
`oracle-amendment-1.json` records a prospective correction: required
unavailable reads remain could-not-evaluate; metadata alone does not alter
ordinary local resolution, missing findings or errata. No whole-root
completeness precondition is introduced for unused data. A missing citation
known to name unavailable referenced local content still refuses.

The original unknown-citation expectation remains filed and is explicitly
withdrawn/not-achieved, not retroactively passed. This entry and amendment
were written before L1 inspected, measured or integrated any candidate.

The independent 44-case original/amended expectation manifest is frozen in
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json` before L1
candidate source inspection or measurements. Its exact finding/token
crosswalk includes complete missing-token failures, referenced missing
content refusals, wrong-type failures, unrelated-hole controls, and the
historical corrected-missing-token workflow. Later oracle changes, if
needed, must be separately disclosed rather than replacing this snapshot.

Before L1 candidate inspection, CritUnknown independently exposed a hidden
dependency: a missing subtree can conceal the cited missing blob's name.
`oracle-supplement-2.json` adds that adversarial case and controls without
changing the frozen44. Only an actually unresolved citation can invoke this
opaque-dependency refusal; known-present wrong-type objects still fail
normally, and an unused hole with all citations resolved is not a blanket
refusal. The supplement also forbids newer Git flags that would raise the
existing version prerequisite.

### Round24 implementation and integration

- Integrated AuditRepair's local evidence rule: deleted the metadata
  classifier, retained the Git isolation/deadline, preserved ordinary
  local absence/authorized errata, and diagnosed unavailable referenced
  content only for unresolved tokens. Opaque tree/commit dependencies
  cannot produce guessed findings. Actual failed required reads name the
  required path/object, including a root-tree OID where available.
- Integrated GridOracle's47-cell original/amended oracle, including the
  unchanged44 snapshot plus3 independent supplement cells. L1 retained
  strong object-identity grading, adopting only the PG46 fixture repair
  from the later proposal, not its path-based grader relaxation.
- Migrated the legacy grid's F06 local-missing outcome, F23 content reason
  and T01 graded-control classification. Filed r23 evidence is unchanged.
  Retired4 obsolete metadata-classifier mutations without ID reuse;
  retained27 applicable elements, with M17's moved message migrated.
- Integrated the11-mutation promisor experiment: inventory completion is
  exit0, evaluation error exit2, never a kill. Pristine errors, timeouts,
  leaks and uncompiled/unapplied mutants receive no credit. PM08 remains
  static-only; no new transport/execution payload is required.
- Added sources S102–S104 (two mined, one rejected) and KQ35; appended
  SKILL, README, knowledge and lesson corrections. No new serving
  capability or numeric score promotion.
- Main measurement follows the fresh falsification stage. Preliminary
  seat results remain attributed to their exact candidate/harness hashes,
  not substituted for the final committed-tree run.

ConnPriorSources' final build review found ledger-level source support
debts: the current bytes-mode auditor was still a consumer of rejected
S095 rather than narrowed S096, and the knowledge appendix omitted the
existing S089/S100 boundary authorities. Reconciled only mutable used-by
cells with every old→new transition recorded in the lesson, and appended
the missing knowledge source chain. Freshly reopened bytes.decode docs
support S105, an explicit superseding rejection record for S095's
cross-API inference (the old immutable teaches cell stays filed).
Source rows now extend through S105; the retained public reader snapshot
and source receipt are under `.ufo/waves/round-24/sources/`.
