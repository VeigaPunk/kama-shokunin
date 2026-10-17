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

## 2026-10-17 — readable front door

Root README was absent. Claims are taken from PROVINCE.md (`bash tools/kama-probe.sh check`, exit 2 is drift, write boundary) and the `tools/kama-probe.sh` header. SHONEN.md boxes are `[~]` author assertions.

Corpus index: `corpus/README.md` is sha256-pinned in `.ufo/round-5/worktree-byte-manifest.json` and was not edited, including its missing final newline. `corpus/knowledge/`, `corpus/lessons/`, evidence, fixtures, and earlier LOG entries were not rewrapped.

Lint fixes: none. Human-legible Markdown in this repo had no unpinned same-line defect.

Lint left in place:
- PROVINCE.md: missing final newline; sha256 pinned in .ufo/round-5/worktree-byte-manifest.json
- SKILL.md: missing final newline; sha256 pinned in .ufo/round-5/worktree-byte-manifest.json
- SHONEN.md: missing final newline; sha256 pinned in .ufo/round-5/worktree-byte-manifest.json
- corpus/README.md: missing final newline; sha256 pinned in .ufo/round-5/worktree-byte-manifest.json

Devin: a search for `devin.ai` in this repo found no URL to edit. No wiki URL was added.
