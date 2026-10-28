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

## Round24 — W2 corrective cutover of the local-object audit

The W2 readers used pinned parent2e254a1763a9c08aa07fc53081287f506c447d84;
canonical code and frozen expectations stayed pinned. The documentation
hold was violated by an outside-scope 80-line append; its bytes/chronology
are VOID incident evidence, not accepted erratum credit. This cutover
adopts the per-store presence/same-canonical proof, selected-ledger scope,
actual-required-read identities and selected-root-only opaque fallback.
Known missing references still come from every present local commit/tree/tag
root; no whole-object-store or reachable-tree completeness precondition is
introduced. The chosen source packet is recorded in
`.ufo/waves/round-24/postfix/integration-inputs-final.json`; exact
pre-cutover identities are in `postfix/frozen-parent-inputs.json`.

The grid now authenticates the immutable47 manifest, records per-arm
comparable metrics, rejects unavailable/tampered oracle inputs distinctly,
establishes genuine blobless absence before hydration, preserves connected
local origins as acquisition controls, and distinguishes full-stderr
internal errors from content-derived refusals. Its negative controls name
the actual failed clause instead of accepting any setup failure.

The promisor mutation observer rejects runtime faults and out-of-envelope
failures as could-not-evaluate with no kill credit; it preserves actual exit
classes without calling same normal exits a substantive exit change. PM08
is manual/uncredited, not a permanent wiring assertion or executable
mutation. The original PM07 recipe is retained, not retargeted to force a
kill. The legacy27-operator probe rejects empty selections before any
source/pristine/grid read. The unused metadata constant and speculative
internal-flag aliases are removed.

Four mutable source consumer cells(S093/S095/S097/S098) receive their actual
new links and old→new log; immutable source claims and statuses are kept.
The source-facet/quote qualification is appended without inventing S106.
All earlier drafts/proposals/receipts remain filed, with the stale/masked
premises and exit-only observer flags explicitly qualified. The frozen
primary 47 and its expected bytes/twin links are unchanged.

This is an adoption entry, not final verification: no final candidate
numerator, score promotion or admission is asserted here. The original
unknown clause remains withdrawn/not-achieved; R23-H2 remains open and
unapproved. No tool was installed or updated in this cutover step.

The final interface review additionally closes frozen-arm false sensitivity,
unique per-arm violation accounting, retained grading explanations and
portable requested scratch behavior; actual producer/population identities
are preserved. The L1 primary-source re-derivation receipt supports new
legacy-scope/historical-count corrections independently of the VOID prose.
The legacy F28/F29 content-derived reason coverage stays open.

The original W2 reader barrier is complete:64 spawned,64 settled and64
durable reports at parent2e, with no provider death. The final reader
qualifies oracle chronology (not universal before-L1-inspection proof);
value preservation and original/prospective fields remain intact. See
`postfix/w2-reader-barrier.json` and `oracle-chronology-qualification.json`.

## Round24 — fixed-epoch cohort and final negative original judgment

- Fixed source epoch: `92063cfc60e217fa7e2098c568578119b16a1b95`.
  The genuine fresh postfix W3 dispatched64 new identities after the true
  W2 barrier; W1/W2/W3 author spend is192/200. No replacement, backfill,
  extra wave, new mission or next round was dispatched. W3 roles were
  reviewer50/mutation-tester10/critic3/connector1; actual captured model
  bindings were m_mim61/m_auto3, not retroactively retagged.
- W3's true terminal barrier is64/64 completed with64 reports, zero failed
  seats/provider deaths and zero running/pending for that wave at the
  recorded barrier. Slot acquire/release, validation and assignment
  recording exited0. These are finite grant/barrier observations, not a
  whole-host or continuous concurrency-floor certificate. W1 and W2 also
  completed64/64; their original bindings/receipts remain filed.
- Counted already-recorded raw primary captures, not a target replay:
  `final/distributed-primary-count-v2.json` covers all47 assigned cells
  bound to auditor b9be4f42, grid30483830 and immutable manifest d86b7bea.
  All recorded amended cells match; seven original expectations remain
  unmet. The first filename-only inventory missed PG12's extensionless
  JSON stdout; v2 corrects that inventory without rerunning or selecting a
  more favorable verdict.
- Counted existing replay-v3 consumer captures: six red-before strict
  comparisons at2e and six exact after matches at92063, including separate
  no-ledger controls. Nine executable mutation samples have named failed
  graded rows; PM07 finite survival and PM08 manual/uncredited status
  remain explicit. Neither record is a new full population sweep.
- Recorded raw PM04 null twin metadata overrides its narrative true;
  Case18/19's unchanged2→2 is not normal-verdict over-refusal. Case42's
  later clean result followed an external hydrating read: changed input,
  not an unchanged-fixture false clean or detector repair. Grid frozen/both
  remains valid; only sensitivity is current-only. Case31's extra sample,
  Case11's extra frozen-program execution and other recorded probe-bound/
  forensic-read deviations are not certified conformant.
- Preserved FinalCase15's scratch-only raw output byte-for-byte in its
  durable out directory with diff-qr exit0. Preserved the existing r23
  outside-closure JSON before removing165 owned scratch children, including
  unused author-verification clones. The unattributed
  `/fast/scratch/hyaku/kama-r24/promisor-grid-pvnuiemp` was deliberately
  retained; unrelated `/tmp/repo-state-grid-4eddb0bx` was not touched.
  A scoped command-line-reference scan found no match for the own scratch
  prefix at cleanup, not absence of all processes/effects.
- Actual current source validate/census exited0:105 rows, A100/B2/C3,
  mined86/queued8/rejected11, zero invalid/missing. Committed-source
  transition counting found four new A rows and eleven old used-by-only
  edits, with no immutable old-cell change. No tool was installed/updated.
- Full original after-clause judgment is NOT ACHIEVED/unprovable in full;
  C1 stays7→7. The initial unknown clause stays withdrawn/not-achieved,
  full global isolation/deadline claims remain unproved, H2 remains open,
  and oracle value preservation does not prove universal before-L1/
  before-any-candidate chronology. No new full final-epoch target/grid/
  legacy/selftest/parity/default-mutation confirmation was run.

These post-barrier documentation/record corrections do not change the
four frozen source programs, original47 oracle, expectations, cohort or
source-byte measurement epoch. VOID80 remains excluded incident evidence,
not accepted erratum credit. Historical private-report amendments and
their custody limits remain disclosed. Fresh outside Main closure alone
may judge this landed negative/unprovable original claim.

## Round 25 — registered instrument re-anchor; declared versus served context capacity (2026-10-22, attempt 2)

Attempt 1 was stood down by the orchestrator for capacity. Attempt 2 is a
fresh author; it committed the attempt-1 build wave as a record only
(5388b7cf, `build/ATTEMPT-1-DISPOSITION.md`, corrected by
`errata-attempt-2.json`).

- Motivating evidence (C1): the outside round-24 spot-check found the
  registered isolation mutant instrument stale (M11 zero matches, M17 two).
  Re-verified at efe58e96: `registered 27 stale 2`; the full instrument
  exits 2 on reaching M11 after M01-M10 ran.
- C1 landed at 1fc41e34: M11 re-anchored, M17 kept on its round-23 line,
  M33 registered for the second call site. `registered 28 stale 0 []`.
  Full run: exit 0, 26 of 28 killed, survivors M17 and M20. M17 survives
  because round-24 commit 92063cf moved the reachable path to
  `bare_objects()`; F13 now kills M33. The instrument docstring says so.
- Motivating evidence (C2): K05 (declared versus served context) had been
  deferred since round 10; the attempt-1 critic CriticLearningBar showed
  the round-20 rule already predicted every per-slot K-cell value, so new
  cells X1-X3 (fit) and L1-L3 (concurrency) were registered in amendment 2.
- C2 landed: tool `tools/kama-context-capacity.py` (5ea4fc44, request
  timing added at 46fb04bd), counter tightened by amendments 3 (c808ba07)
  and 4 (46fb04bd), final receipt re-run after amendment 4 (5c95c8f1):
  `registered 14 observed 14 bound True missing []`. Entry
  `corpus/knowledge/context-capacity.md`, SKILL.md round-25 decision rows,
  sources S106-S113.
- Findings: X1 (`-np 4 --no-kv-unified`, no `-c`) serves 2048 per slot
  from an 8192 pool, where the round-20 wave rule gives 512; X3 (fit off)
  gives 512. L1: two concurrent 1000 + 600 token requests on a shared 2048
  pool both fail with HTTP 500 `Context size has been exceeded.` at 1025
  tokens each; L2 (split, pool 8192) and L3 (sequential) pass. K1 and X2
  return identical endpoint values with pools 2048 and 8192.
- Routed repairs: PM08 wording in `SKILL.md` corrected (manual, review-only,
  unexecuted, uncredited). Correction to the historical line
  `LOG.md:1501-1502` ("PM08 remains static-only"): read it as "PM08 remains
  a manual review-only note, unexecuted and uncredited"; the old bytes stay.
  SKILL registry counts 27 → 28. `SKILL.md:188-190` now states the
  `--kv-unified` premise. Round-24 locator erratum in the round-25 lesson.
- New criterion KQ36 (registered instruments re-run at the landed tip).
- Evidence handling: seat file `a2-build/out/ExecLoadReplicate/runs.json`
  (11141804 bytes, sha256 38e4ab053e5cc7bfc53bdd8d9479a206d29dd37ccbc36f7f352582f42d766a09)
  is committed gzip-compressed as `runs.json.gz`; `zcat | cmp` matched
  before the original was removed.
- Tool installs: none by the author; no seat reported an install.

## Round 26 — live llama-server error signatures (depth); round-25 routed repairs (2026-10-23)

**Claim C1 (depth).** Before: SKILL.md held two live b11755 error signatures
(the `Loading model` 503, the round-25 `Context size has been exceeded.` 500)
and none of the 17 E26 strings; the counter `python3 .ufo/waves/round-26/count-c1.py` printed
`registered 0 counted 0 target 12 met False` at base 1560e4d8. After: 17
signatures, each reproduced by the counter against the pinned binary and
fixture, verbatim in a pinned 704366d source line, cited by a new SOURCES row
(S114-S130), absent from SKILL.md and corpus/ at base, absent from a healthy
run and from `--help`/`--version`. Freeze, controls and amendments:
`.ufo/waves/round-26/preregistration.json`, `.ufo/waves/round-26/controls/`.
Pre-freeze control wave: KamaR26CtlAllFalse met the A0 counter with help text
(12/14); A1 closed it before data (0/14). Wave 1 (36 seats): executors filed
57 candidate entries (`w1-build/out/*/candidates.json`), and the fault-survey
scout listed 8, of which 3 no executor found; 17 registered, the
rest rejected or held back with reasons in `corpus/lessons/round-26.md` §Gate.

**Counter discrimination (found after data).** Wave-2 critic CriticShortcutRows
met the frozen counter 12/12 from the base tree with echoed non-error literals
(counter limit F2). The 17 landed rows were each re-run by a wave-2 attack seat
and none is of a shortcut type, but the counter alone does not establish C1;
no score promotion is claimed.

**Motivating evidence.** `round-25-verifier-spotcheck.md` routed defect 8
(work a lowest axis); the anti-loop note (leave calibration and the
report-landing auditor); SKILL.md "Historical error signatures" is a September
sample from registered ports; 34113 does not listen today (8790 and 8791 do).

**Re-verification (freshness).** The historical llama.cpp rows still match
704366d source (wave-1 ScoutBaseOverlap). KQ36: the registered round-25 C2
command re-run at the round-26 landed tip (round report).

**Repairs.** Defects 1-7 of the round-25 spot-check (lesson §Routed defects):
the 42 late `git status` entries (220 added, 2 modified and 1 deleted round-25 files) committed at a4a159c3, plus one
1.4 MB log the directory commit skipped, committed at 7e5ff9b5, KQ36 qualification, round-25 erratum,
S131-S135 supersession rows, context-capacity errata, count-c2.py raw-hash
binding, SCORECARD trend correction. Mined mistake: false timestamps, now
checked by `tools/prereg-time-check.py` (exit 1 at a4a159c3).

**Falsify wave (34 seats).** Each E26 row was re-run by its own attack seat;
corrections applied to row prose (E26-02, 03, 04, 05, 06, 08, 09, 10, 11, 12,
13, 14, 15, 16, 17: guards, statuses, next actions), the section header (fixture
scope, escape note, unpinned server library, one-mechanism groups, kumitate and
kengaku boundaries), the lesson Gate (verbatim quotes, routing of S131-S135,
three source files added to the snapshot) and the round's own SCORECARD/LOG
"before" statement. Signature, id and source cells did not change. The final
counter receipt is `.ufo/waves/round-26/final/c1-final-tip.out`.

## Correction (appended round 27, 2026-10-23) — the round-26 entry was rewritten in place

The `## Round 26 — live llama-server error signatures` entry above (it starts
at LOG.md line 1680) is not the text first landed. It landed at `7f84cd0e`
(2026-10-23 00:50:35 -0300) and was rewritten in place at `fd48f9a3`
(01:09:37 -0300). The rewrite changed three sentences and appended two
paragraphs: the false "Before: SKILL.md held no live error signature for the
b11755 runtime" became "held two live b11755 error signatures"; the
"58 candidates" sentence became the 57 + 8 candidate account; the motivating
"ports that are now dead" became "registered ports; 34113 does not listen
today"; the repairs sentence gained the 220/2/1 file account and 7e5ff9b5;
and the "Counter discrimination (found after data)" and "Falsify wave"
paragraphs were added. Original text: `git show 7f84cd0e:LOG.md`; full change:
`git diff 7f84cd0e fd48f9a3 -- LOG.md`. The current text is the corrected
one; the original "Before" sentence was false (base SKILL.md held the
`Loading model` 503 and the `Context size has been exceeded.` 500). Routed by
`corpus/lessons/round-26-verifier-spotcheck.md` defect 1. From this round on a
LOG correction is a new appended entry like this one, never an in-place edit.

## Correction (appended round 27, 2026-10-23) — to the correction entry above

The correction entry immediately above (landed `324d5d62`) has two errors,
found by wave seat ReviewRepairD1Log (`.ufo/waves/round-27/w1a3/advice/ReviewRepairD1Log.md`).
It says the rewrite "changed three sentences"; the diff changes four (the
Before, candidate-count, ports and repairs sentences), as its own list
shows. And it presents a two-step history: the round-26 entry was also
rewritten in place at `f4066979` (00:56:41 -0300, "LOG candidate count
corrected") between `7f84cd0e` and `fd48f9a3`, so the candidate sentence
reached its final form in two steps (`git log --format='%h %ci %s' 7f84cd0e..fd48f9a3 -- LOG.md`).
The "Counter discrimination" paragraph was inserted mid-entry, not appended.
The entry above is not edited.

## Round 27 — echo-discriminating counters (exploratory, calibration); C1 miss; round-26 repairs (2026-10-23, attempt 3)

**C1 (measured, depth) — miss.** Preregistered by attempt 1 (`530eaa99`,
amendments A1-A3 to `1471f676`), target `counted >= 15`. The attempt-2
control wave (37 seats, 05:41:33Z) died with the orchestrator at 06:19:06Z
without committed receipts; a dead seat's task is not resent and no data seat
was dispatched. Attempt 3 withdrew C1 before data (`a3/plan.json`); under the
frozen kill rule the landed tip's count is a miss.

**X1 (exploratory, calibration).** `corpus/knowledge/echo-discriminating-counters.md`
and QUALITY KQ37 (+ round-27 qualification): refuse decoded-request echoes,
one row per message frame, signature inside server-owned text. Motivating
evidence: the round-26 shortcut (`lessons/round-26-verifier-spotcheck.md:98-116`);
RFC 8259 §7 (S136, S139); `server-common.cpp:1375` (S137); live probe
`w1a3/out/ExecLiveEchoProbe/receipt.json`; offline replay and mutation
receipts under `w1a3/out/`. Verdict pending a named non-author reviewer.

**Repairs.** Round-26 spot-check defects 1 (LOG correction entries above), 3
(`repairs/d3-r26-shortcut-pins/`), 4 (`repairs/d4-r26-dead-seat-errors/`),
5 and 6 (lesson §Repairs), 7 (S138); 2 via A3 + KQ37; 8 open.

**Re-verification (freshness).** Round-start census re-run on a clone at
`0ec32cac` (`a3/census-start-0ec32cac.out`, exit 0) and reproduced by
ReviewCensusStart; S133's source re-fetched (sha256 unchanged) for S138.

**Housekeeping.** 1846 untrusted attempt-2 files moved out of the lane unread
(`/fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/`); three
orphan llama-server processes left by attempt-2 seats (ports 47636, 47637,
47644) killed at 07:18Z.

## Round 28 — request-field outcomes (depth); round-27 routed repairs (2026-10-23)

**Claim C1 (depth), measured.** SKILL.md "## Round-28 request-field outcomes":
34 rows from 17 data seats that each measured their assigned fields live on
the pinned b11755 fixture (own ports 48201-48217) and cited the declaring line
of `tools/server/server-schema.cpp` @704366d76 (S140-S173). Frozen counter
from a fresh clone at `e49b4cf7`: `registered 34 counted 26 target 18 met
True` (`.ufo/waves/round-28/final/c1-e49b4cf7.out`). Order of events, controls
and amendment A1: `corpus/lessons/round-28.md` §Claims.

**Evidence that motivated A1.** Data seats DataG03, DataG05, DataG07 and
DataG08 returned rows whose stored value was only a type conversion (1e39 →
3.4028234663852886e38; 4294967296 → 0; 2.5 → 2). CtlA1Conversion then showed
a type-only policy meets the A0 counter (20/52) and not A1 (0/52).

**Repairs.** Round-27 spot-check defects 1-7 (lesson §Repairs): `count-c2.py`
recomputes cells from raw bytes; KQ37 round-28 qualification; entry recheck
line and `tools/echo-recheck.py`; SKILL instrument registry rows;
`tools/gate-registry-check.py` (base exit 1, tip exit 0).

**Re-verification (freshness).** The pinned snapshot server-schema.cpp was
re-fetched by 13 data seats (sha256 1f9d7b73…0050 each time); round-27 live
echo probe re-run by ExecEchoRecheck: `echo-recheck same 6/6`.

**Wave 2 (falsify, 32 seats).** Every row re-measured live by a second seat;
all 34 outcomes reproduced. Meaning-cell over-generalisations corrected (18
cells, counted cells unchanged). CriticA1Legitimacy: A1 was written after a
data seat had checked drafts with A0 counter functions (08:35:54Z), and a
type-only control meets A0 (20/52); the author does not promote depth (7 → 7)
and reports both rules (lesson §Claim verdict).

Round-28 source-digest correction: the server-schema.cpp SHA-256 is
`1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
(`1f9d7b73…4050`); the abbreviation `1f9d7b73…0050` in the round-28 entry
above is a transcription error (residual seat ResNoHarm).

Round-28 count corrections (residual seat ResSelfAssessment, 3 mismatches in
46 checkable round-28 statements): the 34 landed rows come from 13 data seats
(DataG01-09, DataG11, DataG13-15), not 17 — 17 data seats measured fields and
DataG10/12/16/17 landed no row; the pinned server-schema.cpp was re-fetched by
14 data seats (the 13 SOURCES-row openers plus DataG10), not 13. The third
mismatch, SHONEN.md box 2's round-17 "8 bad fake-server shapes ... accepted 6"
wording, is inherited from round 17 and left for a round that re-reads the
round-17 receipts.

## Round 29 — self-assessment evidence at writing (calibration) (2026-10-23)

C1 (measured, calibration): frozen counter `.ufo/waves/round-29/count-c1.py` (`827d1365`) checks
69 statements of six classes in SCORECARD.md/SHONEN.md at base `2aa46e24` against the commit that
wrote each line; 11 were false at writing (4 pointers, 7 quoted outputs). 14 control seats scored
before any data (`35b90184`): no control meets `unresolved == 0`. The L1 appended 11 correction
rows (`513eba3b`); fresh-clone receipt `unresolved 0 met True` (`.ufo/waves/round-29/final/c1-513eba3b.out`). All 11
confirmed false under the class rule by non-author ConfirmM seats; CriticAxisFit: the failures are
evidence-resolution defects, not proven wrong judgments (accepted). Calibration 7 → 7, no
promotion.

Repairs: round-28 A1 time corrected by appended record (edit call 08:37:23.720Z, result
08:37:23.732Z, commit 08:38:16Z, not
"~08:45Z"; frozen bytes untouched); DataG01/DataG15 timing transcript excerpts committed with
sha256 (`.ufo/waves/round-29/w1/out/ExecTimingTranscript/`); echo-recheck exit-2 receipt
(`.ufo/waves/round-29/repairs/echo-exit2/receipt.txt`); round-28 lesson Gate preamble 4 → 8
non-verbatim seat quotes (appended); SHONEN.md box 2 line 8: "8 bad fake-server shapes rejected,
frozen pair accepted 6" → "8 adverse controls rejected: 7 bad server shapes + 1 injected teardown
fault; frozen accepted-bad = 6 (5 accepted bad receipts + 1 receiptless escape), with K3
inconclusive"; QUALITY KQ38 (depth counters) and KQ39 (calibration at writing).
Mined mistake: `tools/prereg-time-check.py` now reads `YYYY-MM-DD ~HH:MMZ` / `YYYY-MM-DD HH:MMZ`
(was blind to the round-28 A1 text; now flags it, exit 1).
Sources S174-S177 (git-blame, git-merge-base, git-grep + gitglossary, pretty-formats) opened this
round; census 173 → 177 rows, exit 0.
Re-verification (freshness): `tools/prereg-time-check.py --selftest` 13 cases PASS plus the
SELFTEST PASS aggregate line, exit 0 (landed tool at the round's tip, seat-unique /tmp scratch);
ScoutHeldRules re-ran citation-provenance, report-landing-audit and sources-append-only self-tests,
all exit 0.

## Round 29 attempt 2 — verification wave and integration (2026-10-23)

Attempt 1 died with the phase-4 orchestrator (~09:30 -03) after landing `827d1365` (freeze),
`35b90184` (pre-data controls) and `513eba3b` (C1 data); its uncommitted narrative and wave
evidence are inherited and verified, not trusted (addendum §5/§6). Attempt 2 (L1 KamaR29)
re-verified C1 before touching anything: fresh clone of the lane remote at `513eba3b`, frozen
counter sha256 `fe11d599…7383`, receipt `statements 69 mismatched_at_base 11 append_only True
valid_corrections 11 false_corrections 0 unresolved 0 met True` (this session, 15:13 -03).

Wave round-29-w2: one v2 wave, 64 seats, policy `ufo-wave-policy-v2.json` (band 64–128; attack
42/64 = 65.6%), dispatched by the orchestrator per the operator's mid-flight directive (no seat
dispatched from the L1 session); wave-slot grant `granted lane=kama wave=round-29-w2 seats=64
live=21 pending=65 cap=256`. Spec/dispatch/registry: `.ufo/waves/round-29/w2/`; seat reports:
`.ufo/waves/round-29/w2/out/`. Verdicts: all 64 seats returned (none dead); 11/11 per-row
confirmations confirmed-false by hand; both closest controls (CtlSourceBounds 9/7/9, CtlBaseTree
6/4/9) reproduced exactly; frozen bytes verified untampered across `827d1365`/`35b90184`/`513eba3b`;
9+ counter mutants killed (row-kill, append, heading-binding, base-tip fail-closed); receipts
byte-identical under `env -i`; controls SUMMARY recomputed 14/14. Disclosed defects fixed at
integration: S174/S176 located-quote paraphrases repaired to verbatim pre-landing; lesson
timestamps aligned to git metadata (freeze 10:55:43Z, data 12:02:52Z, dispatch 12:02:03Z); A1
sub-second record (08:37:23.720Z/.732Z) added here and in SCORECARD; lesson "3 surviving mutants"
corrected to 2 (`mined/survivor-recheck.out`); controls SUMMARY wording erratum appended
(verdict receipts vs seat-disclosed DIAGNOSTIC copies). Disclosed, unfixed limits: counter recall
69 of ≥141 checkable statements; predicate is two sentences plus docstring class rules (not one
literal sentence — CriticPredicateIdentity, accepted as a conformance defect); counter enforces
on tip bytes, not authorship; `blame.ignoreRevsFile` config can shift receipts (fail-closed
direction; host unset); counter exit code signals execution, not verdict — the gate reads the
receipt's `met`/`unresolved`; `in_lane()` skips absolute-pointer statements at extraction;
scanner behavior under `###` subheadings unexercised. W2 item-text defects (mine): two
arithmetic predictions wrong (counter self-consistent under the frozen contract); sid described
as a revision prefix (it is `sha256(line)[:10]`); prereg-time-check items omitted `--scratch`
(steered mid-flight; one pre-steering invocation left residue under
/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck/ptc-selftest-ywq_7og0 — scratch space, disclosed).
Prospective citation disclosed (RevengerPrereg F1): `513eba3b`'s prose cites w1 Confirm outputs
created minutes after the commit; the artifacts materialized and reproduce. Origin/master moved
to `49f849f292c3` (operator daily-reflection commit, descendant of `513eba3b`); the integration
commit rebases over it. Census end: 177 rows, exit 0 (receipt `.ufo/waves/round-29/final/census-end.out`).

## Round 30 — calibration census over its recall population; run-agreement capability (2026-10-23)

Two claims, both frozen at `fdf8cda1` before any seat (`.ufo/waves/round-30/preregistration.json`).
C1 (calibration, measured): the round-29 census now classifies its declared recall population — the
72 statements two independent round-29 sweeps enumerated at `6de225c2` — at their writing revisions;
the two that do not hold carry appended observed values (SCORECARD.md §Round 30 — self-assessment
corrections). Base receipt `.ufo/waves/round-30/c1/before/c1-base.out`; the rows-only arm at the
round-29 tip reads `valid_corrections 11 unresolved 2 met False`. C2 (operability, capability):
`tools/instrument-agreement.py` runs a lane instrument N times over one tree, normalizes only
declared volatile fields, and reports `IA runs=N agree=A disagree=D`; selftest `IA_SELFTEST
pass=4 fail=0` with a nondeterministic arm refused, and receipts `c2/receipt-a.json` and
`c2/receipt-b.json` read `agree=3 disagree=0`. Pre-data control call: 14 arms, one row per arm in
`.ufo/waves/round-30/controls/SUMMARY.md`, committed `14bb1a32` before any correction row; no
shortcut meets the target, the reference policy does by design.

Landed hashes this round: freeze `fdf8cda1` (counter, preregistration, base receipt, census start);
C2 instrument and wave/control calls `1d3e8ba4`; control receipts `14bb1a32`. Round-29 attempt-2
hashes named for the closure's routed defect 2: `6de225c289b7682bf280cffb4a07de3fb7d1275c`
(verification wave w2 integration and landing) and `227dd1eeff95` (final tip receipts: frozen
counter met True and sources census exit 0 at pushed tip `6de225c2`). The round-29 w2 files
`VerifyLogFreshness.md` and `out/VerifyLogFreshness/report.md` were already tracked at `40b122d`
before this round; no new write was needed.

Sources: S178 (kumitate r48 counter-rerun, own-work `ce9aee5`) and S179 (mori r36 source-drift,
own-work `e57c58b`/`6827d6e`) opened this round; census 177 → 179 rows, validate exit 0
(`.ufo/waves/round-30/census-end.out`). QUALITY KQ40 added (census population declares its recall
gap). No endpoint was sampled; K05 remains operator-runtime dependent.

## round 31 — the chat-completions adapter (depth) + claim-row evidence (calibration), 2026-10-23

**Claims.** C1 depth: `counted >= 12` over a new SKILL table of `/v1/chat/completions`
parameter outcomes on the lane fixture. C2 calibration: every SCORECARD claim row names a
commit that resolves at the measured tip, an evidence path that exists, and its counter
script (`rows >= 28`, `unresolved 0`, `false_corrections 0`, `append_only True`).

**Before → after (measured).**
- C1: base `07794a4d` has no registry and no table (counter exits 2) → tip `54c6f4fe`
  `registered 18 counted 17 target 12 met True not-counted ['K31-10']`
  (`.ufo/waves/round-31/c1/c1-54c6f4fe.json`). K31-10 is refused because the adapter
  appends the offending `response_format` type to its message, so the message is not a
  verbatim pinned string — the row stays in the table as a true observation, uncounted.
- C2: base `rows 28 base_mismatched 13 valid 0 unresolved 13 met False` → tip `b4f3edc0`
  `rows 30 base_mismatched 13 valid_corrections 10 false_corrections 0 unresolved 3
  append_only True met False` (`.ufo/waves/round-31/c2/c2-b4f3edc0.json`).

**Landed.**
- SKILL.md §Round-31 chat-completions parameter outcomes (18 rows, four outcome classes,
  fixture pins, limits) and two instrument-registry rows for the new counters.
- `registry/chat-param-outcomes-r31.json`; `corpus/knowledge/chat-adapter-outcomes.md`;
  S180-S191 (twelve pinned `server-common.cpp`/`server-schema.cpp` lines @ 704366d).
- SCORECARD §Round 31 (both claims recorded with verdicts), §Round 31 corrections (ten
  claim rows), §Planned (round 32); `corpus/QUALITY.md` KQ41; README coverage + frontier.
- Preregistration, both frozen counters, the 12-seat pre-data control call and the wave
  fragments under `.ufo/waves/round-31/`.

**Not admitted.** C1's frozen counter is met at the landed tip, but a do-nothing registry
of twelve duplicate rows asserting the base request's own `n_predict = 1` also meets it
(`.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json`), and two further counted-row
classes prove nothing (`RevCounterFair` F1/F2). C2's predicate is unreachable: three
failing rows share the Claim cell `C1` (rounds 11-13), so the `(row, class)` correction
key collapses three dispositions (`controls/RefRepair/`: valid 10, false 3, unresolved 3).
Both counters are frozen bytes; fixes are routed to round 32 (KQ41).

**Hold.** The round-30 frozen counter still reads `met True`, 141 statements, unresolved 0
at the round-31 tip (`.ufo/waves/round-31/c1/hold-r30.out`).

## Round 31 attempt 2 — inherited claims re-measured, C3 registry coverage, meaning-cell corrections (2026-10-23)

Attempt 1 of round 31 froze C1/C2 at `0e6f8ed6` (base `07794a4d`), landed the chat-adapter surface and
both counters through `382d11b2`, and died before the fleet report. This attempt inherited that state
rather than restarting the round: it re-measured both frozen counters at the inherited tip, froze one
further claim (C3, `.ufo/waves/round-31/preregistration-c3.json` at `bda324bb`, before its row
existed), dispatched a 44-seat falsification wave (wave 2) under policy v1
(`.ufo/waves/round-31/w2/{spec,plan,taskCall}.json`, validator exit 0, 44/44 spawn), and lands the
round report. No inherited predicate was amended; no counted row was rewritten.

**Landed hashes, in order.**
- `bda324bb` — C3 freeze, C3 before receipt (`registered 8 unregistered 1`, exit 1), wave-2 spec /
  plan / taskCall, round-start census (`validate`, exit 0).
- `addeb57c` — SKILL instrument-registry row for `.ufo/waves/round-29/count-c1.py`; gate reads
  `registered 9 unregistered 0`, exit 0; round-31 re-run of that counter
  (`statements 69 mismatched_at_base 11 valid_corrections 11 unresolved 0 met True`).
- `a9181096` — SKILL §Round-31 attempt-2 meaning-cell corrections (six rows, each with its measured
  counterexample), `PROVINCE.md` and `corpus/README.md` count corrections (S180-S191, 18 rows/17
  counted), removal of the committed 404 body `utils.hpp`, two unpinned duplicate snapshot files and
  the duplicate `c1/c1-remap.json`.
- the integration commit carrying this entry, `SCORECARD.md` §Round 31 attempt 2, KQ42, the
  attempt-2 lesson section and the wave-2 evidence (`.ufo/waves/round-31/w2/**`);
- the receipt-only commit that follows it: C1/C2 at the final tip, C3 at the final tip, census end.
  This entry is appended before those two commits exist, so their hashes are recorded in the fleet
  report and in the receipt files they carry, not here; every hash above was produced by
  `scripts/hyaku/jj-lane.sh`'s `landed` line.

**Measurements.** C1 at `bda324bb`: base `07794a4d` exits 2 (`SNAPSHOT.json missing at tip`) → tip
`registered 18 counted 17 target 12 met True not-counted ['K31-10']`, exit 0
(`.ufo/waves/round-31/c1/c1-bda324bb.json`). C2 at `bda324bb`: base `rows 28 base_mismatched 13
unresolved 13` → tip `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0
unresolved 3 append_only True met False` (`.ufo/waves/round-31/c2/c2-bda324bb.json`). C3: `registered
8 unregistered 1` exit 1 at `bda324bb` → `registered 9 unregistered 0` exit 0 at `addeb57c`;
dropping the row from a scratch SKILL returns exit 1 (`.ufo/waves/round-31/c3/`). Round-30 hold:
`statements 141 … unresolved 0 met True` at the round-31 tip, only the `tip` field differs from the
committed receipt (`w2/out/ReRunHold/`, `w2/out/ExecHoldRepro/`).

**Verdicts.** C1 met on its frozen counter, not admitted (independent no-op counts 12/12,
`w2/out/CriticNoop/`); C2 not met and its key non-injective (one collapsed correction flips `met`
True while two dispositions stay uncorrected, `w2/out/MutC2Key/`); C3 met on its frozen predicate, not
admitted (the gate is an occurrence check; an empty-exit-map row passes, `w2/out/ExecC3Control/`). No
axis score moved; no capability row entered.

**Wave.** 44 seats in one batched call: reviewer 13, critic 10, mutation-tester 5, executor 5, scribe
4, connector 2, scout 2, sentinel 2, simplifier 1 (attack roles 28/44 = 64%). Findings that changed the
record: six meaning cells falsified by probe; three surviving C1 pin mutants; C2 suffix deletion passes
`append_only`; the committed 404 snapshot body; the README/PROVINCE count drift; the 1.2 MB
`CriticIgnoredClass/raw.json` kept as evidence with its size disclosed.

**Census.** Round start `validate` exit 0 (`.ufo/waves/round-31/w2/census-validate-start.out`); a
wave seat's `census` run reports 191 rows, 0 missing (`w2/out/ExecCensusRows/`); round end receipts are
in the receipt-only commit.

## Round 31 attempt 3 — re-execution at write time, frontier row, prepared wave-3 (2026-10-24)

Attempts 1-2 of this steered round landed all claim data and died without a fleet report (six
`lane-dead-no-report kama round=31` watchdog lines on 2026-10-23). This attempt inherited the tree
at `f129e27b3b57a8fed7a34a8e6fe96d481e6c959d` and:

- re-executed all three frozen counters at write time on a fresh scratch clone
  (`/tmp/kama-r31-clone` at `f129e27b`): C1 `registered 18 counted 17 target 12 met True
  not-counted ['K31-10']` exit 0; C2 `rows 30 base_mismatched 13 exempt 1 valid_corrections 10
  false_corrections 0 unresolved 3 append_only True met False` exit 0; C3 `registered 9
  unregistered 0` exit 0 — every value byte-identical to attempt 2's committed receipts
  (`.ufo/waves/round-31/res/out/KamaR31a3.ResReRun{C1,C2}/`, `diff` against the inherited
  `KamaR31a1b`/`ResReRunC2` receipts: none);
- committed the inherited-untracked re-run receipts (`res/`) under this round's entry, closing the
  recurrence mined as lesson row 9;
- opened source row S192 (OpenAI chat `response_format` reference) for the round-32 grammar
  frontier; census 191 → 192 rows, validate exit 0 at start and end
  (`.ufo/waves/round-31/census-end-attempt3.out`);
- prepared wave-3 (32 seats, policy v1 validator exit 0) for the round-32 repair candidates under
  `.ufo/waves/round-31/w3/` — not dispatched per the accepted host mapping; the orchestrator
  dispatches prepared waves between rounds;
- landed the round-31 fleet report that attempts 1-2 never filed.

**Measurements.** Counting commands and receipts: C1 `.ufo/waves/round-31/res/out/KamaR31a3.ResReRunC1/c1-tip.json`;
C2 `.ufo/waves/round-31/res/out/KamaR31a3.ResReRunC2/c2-tip.json`; C3
`python3 tools/gate-registry-check.py --rev f129e27b3b57a8fed7a34a8e6fe96d481e6c959d`. Verdicts
unchanged: C1 met-on-counter/not admitted; C2 not met (key defect); C3 met-on-predicate/not
admitted. No axis score moved; no capability entered.

## Round 32 — round-qualified evidence counter and meaning-grading registry gate (2026-10-24, attempt 1)

Declared claims (`.ufo/waves/round-32/preregistration.json`, frozen at `9afaf0e9f03ea513e8ee54b43793d2f01cfa309e`):
**C1 (calibration 7 → 7)** — `.ufo/waves/round-32/count-c2r.py` repairs the frozen round-31
`(row, class)` correction key with a round-qualified `(round, row, class)` key and a uniqueness
precondition; base `18464d0866afd5c4b471c8478d72b079d82d1fa8` reads `valid_corrections 10
unresolved 3 met False` → landed tip reads `valid_corrections 13 false_corrections 0 unresolved 0
met True` (receipts `.ufo/waves/round-32/c1/before-base.json`, `.ufo/waves/round-32/c2r/c2r-tip.json`).
Kill rule: one collapsed `CR31:`-prefixed correction flips the FROZEN counter to `met True`
while the repaired counter refuses it (`.ufo/waves/round-32/c1/controls/KeyCollapse/`); two
corrections on one qualified key are both false (`controls/DupKey/`).
**C2 (operability 8 → 8)** — `tools/gate-registry-check.py` v2 grades registry rows for meaning
(table-row presence, cell presence, non-empty exit map, cited-path existence); the v1 do-nothing
control exits 0 on all three r31 defective fixtures and on the prose-only counters
(`.ufo/waves/round-32/c2/controls/*-v1.out`); v2 at the landed tip exits 0
`registered 10 unregistered 0 defective 0` (`.ufo/waves/round-32/c2/gate-tip.out`,
`selftest-final.out`), each fixture exit 1 with its named defect, and single-check-removal
mutations flip exactly their fixtures (`c2/mutations/`). Two prose-registered counters
(round-17, round-26) exposed by the repair are registered by SKILL's round-32 registry block.

Repairs, not claims: RefRepair pointer drift (routed defect 5) and the w2 seat census
44-planned/43-dirs/ConnInstrumentDup-unverifiable reconciliation (routed defect 6) — appended
records in SCORECARD §Round 32. Routed defects 1 (C1 eligibility), 2 (KQ42 probe gating) and 4
(pin bytes) are prepared as wave items under `.ufo/waves/round-32/w1/` (validated; the
orchestrator dispatches prepared waves between rounds — this seat has no dispatch tool) and are
not claimed. Frontier step: census 192 → 193 (S193, own-work, the repaired gate's contract;
cited by C2's lesson Gate and the SKILL registry block), lesson `corpus/lessons/round-32.md`
(mistakes: reference-drift, number-drift, prose-only registration). KQ36: the frozen round-31
counters and the round-30 hold counter are re-run at the new tip (`.ufo/waves/round-32/kq36/`).
No capability row enters; other scores held (depth 7, freshness 8, coverage 9, adjacency 7).
Measured data tip `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279`.

## Round 33 — receipt lineage and gate evidence correction (2026-10-24, attempt 1)

Two frozen claims target the round-32 closure defects; both retain numeric axis scores. C1 calibration 7→7 applies KQ39 to the round-32 C2 Scorecard statement at its writing revision `dc4258bdb08d658f1c5b15abc8378461659bd155`: three false fixture references, unresolved 3→0. C2 operability 8→8 counts complete attributed receipts for the pinned clean gate run plus three controls, 0/4→4/4. Preregistration and no-op controls: `.ufo/waves/round-33/preregistration.json`, `.ufo/waves/round-33/c1/base-control-amend1.out`, `c2/base-control-amend2.out`; both controls exit 1 and miss their frozen after predicates.

**Landed commits (jj-lane helper `landed` lines):**
- `4fdd4e663ba8d3353b5cd431c2d21373d930a6c5` — claim freeze, census start, C1/C2 no-op controls, and 33-seat prepared v1 wave spec/plan/taskCall.
- `f2c0fc1eccbf8c875827d24b9fe6fe451315e7eb` — pre-data amendment 1: corrected C1's observed missing-path line and the C2 fixture's accidental `tools/measure.py` path; exact stdout control and updated no-op receipts. The target and labels did not change.
- `88331197a7de5fcc171bc7290fdd7beb43487a63` — append-only r32 receipt/reference corrections, S194, KQ43, SKILL/README/lesson changes, and the four final replay receipts.
- `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712` — outside Gate spot-check recorded; the current tree also carries the corrected C2 replay auditor and its failure/repair evidence.

**Measurements at evidence tip `1c881bbd3e1cce5f0b01f1afc6d3229866cbe712`:**
- C1: `python3 tools/round33-claim-audit.py --repo . --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 --tip 1c881bbd3e1cce5f0b01f1afc6d3229866cbe712` → `false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True`, exit 0 (`.ufo/waves/round-33/c1/after-evidence-tip.out`). The legacy bad bytes remain present; the active correction points to the three exact correct outputs.
- C2: `python3 tools/round33-gate-receipts.py audit --repo . --tip 1c881bbd3e1cce5f0b01f1afc6d3229866cbe712 --source-rev 967d88528c1d83535563f971863f7855f76b4849 --receipt-dir .ufo/waves/round-33/c2/final` → `complete=4/4 missing=0 invalid=0 met=True`, exit 0 (`.ufo/waves/round-33/c2/after-evidence-tip.out`). The four receipts each carry full source/evaluated revisions, the exact gate digest, the captured runner digest, argv, exit, stdout/stderr.
- The first C2 audit after data at `88331197a7de5fcc171bc7290fdd7beb43487a63` raised `TypeError: Strings must be encoded before hashing`, exit 1, with no claim verdict (`c2/after-data-tip.out`). KQ25 treats this as a visible runtime error, not a kill or pass. The auditor was corrected to hash committed runner blobs as bytes and validate historic runner digests/argv; the unchanged predicate then passed at the evidence tip. Amendment: `.ufo/waves/round-33/amendment-2.json`.

**Frontier and mistakes.** Round-start validation (`.ufo/waves/round-33/census-start.out`) and round-end validation (`census-end.out`) both exit 0; census counts `193 → 194`, tier A `188 → 189`, B `2 → 2`, C `3 → 3`, mined `174 → 175`, queued `8 → 8`, rejected `11 → 11` (`sources-start-count.out`, `sources-end-count.out`). S194 is the only new row, tier A own-work; no old row cells/status/recheck/used-by changed, no knowledge entry or frontier row advanced. `corpus/lessons/round-33.md` records the receipt-lineage, three false references, S193 quote, incomplete receipts, accidental fixture path, misroot, and C2 audit runtime error; KQ43 is the new receipt criterion.

Non-author `CJ-kama-r32` re-opened and agreed with S194's exact line/quote/scope and S104's retained reject. No endpoint, service, consumer, or model-quality state was sampled. No capability row entered. Wave policy v1 plan and taskCall rendered with exit 0: 33 prepared tasks (connector 3, executor 4, scribe 3, scout 4, reviewer 7, critic 5, mutation-tester 5, revenger 1, sentinel 1); L1 held planner. Accepted host mapping: 0 dispatched, 0 dead; no residual call. No tool installed or upgraded.

## round 34 — capability repertoire census, instrument-registry coverage, alias-theme assimilation (2026-10-24)

Two declared claims, both measured on committed bytes. C1 (calibration 7 → 7):
the lane's SCORECARD capability self-assessment now lists every capability the
lane demonstrated — `python3 tools/capability-repertoire-audit.py --repo .
--tip <full-commit>` reads `listed 3 observed 6 missing 3 unsubstantiated 0 met
False` (exit 1) at base `7c35289da5f4b94e062cd900eb086919e5094003` and `listed 6
observed 6 missing 0 unsubstantiated 0 met True` (exit 0) at the data tip
`29f9d1e1b20ef6e16e578e6e039f95f4f3fb4007`; the do-nothing control (names
without a resolving evidence pointer) reads `unsubstantiated 6 met False`. The
counter is new: `tools/capability-repertoire-audit.py`, selftest
`CAP_SELFTEST pass=2 fail=0`. C2 (operability 8 → 8): the lane's own
instrument-registry gate now evaluates round-scoped counters held in `tools/`
as well as in the wave directories — `python3 tools/gate-registry-check.py
--rev <full-commit>` reads `registered 10 unregistered 2 defective 0` (exit 1)
at base and `registered 12 unregistered 0 defective 0` (exit 0) at the data
tip; the prose-only control stays red and the gate selftest stays 6/6. The
frontier step assimilated ONE theme (served-name / alias resolution) from the
read-only shokuknow package: two knowledge entries admitted
(`corpus/knowledge/serving-alias-contract.md`,
`corpus/knowledge/served-model-id-resolution.md`), five source rows appended
(S196, S205, S206, S209, S223) after an empty collision check, a scratch
transformation and a mirror census that exited 0 before the first append, plus
one own-work row S324 for the widened gate population. Sources validate exit
0. Lessons and rejections with their flip conditions:
`corpus/lessons/round-34.md`. Report: `.ufo/reports/round-34/kama.md`.

## round 35 — r34 self-assessment corrections and probe-signal coverage (2026-10-24)

Two declared claims, measured on committed bytes at `d419b99df20d1f0b34caf65807e913784e69baf5`. C1 (calibration 7 → 7): four frozen r34 self-assessment statements are corrected by appended rows; the filed report blob is unchanged. The do-nothing control prints `uncorrected 4 met False`. The tip counter prints `uncorrected 0 false_corrections 0 report_unchanged 1 met True`. C2 (coverage 9 → 9): the round-35 coverage block names `knowledge/endpoint-health-probe-conventions.md`, the file exists, and it cites S327, which was opened 2026-10-24. Base `719655f` prints `named 0 file_exists 0 cited_row 0 met False`. The tip prints `named 1 file_exists 1 cited_row 1 met True`. MISSION.md:29 still says operability + freshness; it was not edited. Inherited round-33 and round-34 paths were re-verified; three nested git clones were discarded and the rest kept. Lessons: `corpus/lessons/round-35.md`. Report: `.ufo/reports/round-35/kama.md`.

## round 36 — r35 routed corrections and the published-route-versus-engine-route ground (2026-10-24)

Two declared claims, frozen in `.ufo/waves/round-36/preregistration.json` before
any seat scored, measured on committed bytes at `2e8beda5b2a2dcc62d6782838ee6e47cda04df55`.

C1 (calibration 7 → 7) corrects, by append only, the four statements the
round-35 closure routed: the S211 quarantine reason (the closure and this
round's own fetch both record HTTP 200 for the cited URL, and the seat report
records a successful fetch with the token still-live absent from the page; the
row stays unappended because no located quote exists), the S327 quote's word
count (20 words, not the 18 its paragraph records — re-derived three ways from
the committed lesson blob `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412`), the
mixed-mirror description (11 symlinks and 84 regular files, not a symlink
tree), and the seven r35 leftovers (3 seat-log flushes, 1 report overwrite, 1
mixed mirror, 2 helper-skipped 1066624-byte HTML files), which are classified
and left unswept. Counter: `uncorrected 4 false_corrections 0 met False` (exit
1) at base → `uncorrected 0 false_corrections 0 met True` (exit 0) at the
landed commit. The r35 lesson blob and the r35 fleet report blob are unchanged;
the filed r35 report was not rewritten.

C2 (coverage 9 → 9) adds `corpus/knowledge/sglang-native-route-deprecation.md`
to the coverage map. At tag v0.5.22 the published SGLang native-API page still
lists `/get_model_info` and never names `/model_info`, while the same tag's
`http_server.py` registers both routes and warns in the deprecated route's own
response that `/get_model_info` will be removed. Counter: `named 0 file_exists
0 cited_new 0 met False` at base → `named 1 file_exists 1 cited_new 1 met True`
(exit 0). Sources S328 and S329 appended, each opened and located by this lane
on 2026-10-24.

Frontier step: the read-only shokuknow `corpus-expansion-1` package, one theme,
one entry, two rows. The scratch validate mirror's first build failed with E12
on both rows — appended at the end of `corpus/SOURCES.md` they fell outside the
Registry section — and the rows were re-placed inside the table before the
gate exited 0 with 93 pre-existing W04 warnings. The seven kama rows of the
campaign absent-defect register were hand-checked this round: S202, S206 and
S230 present; S200, S210 and S211 absent; S224's compound span does not
locate. No register row is appended. Id collision: registry 201, staged 134
(S325 to S458), one collision (S327, the same document the lane already holds);
the 0-3 leading-space guard proves it can see an indented row where the
column-zero pattern cannot. `corpus/QUALITY.md` gains KQ45, mined from
`considerthese/2026-10-24.md` proposal 2 and grounded by the drift measured on
S174, S192 and S193 — the reflection was a pointer; the three sources were
opened.

Instrument repair: the C2 counter's selftest built its base and outside arms
from the tip's README and entry, so after the round landed the base arm
reported `met True` and the selftest exited 1. Both arms now load the BASE
revision. `score()` and the frozen predicate are unchanged and the measurement
line is byte-identical.

VCS incident, recorded: the wave-3 mutation-tester seat ran `jj commit` inside
the lane repo instead of its sandbox clone and parked the lane's working copy
on three foreign-identity commits. `jj-lane.sh commit` refuses a non-empty
working copy on a non-tip base, and `jj-lane.sh recover` cannot accept a
candidate that is both a direct child of the tip and the working copy's direct
parent. The claim work was committed and pushed through `jj-lane.sh` in a
scratch clone of the lane remote, and the lane's branch was advanced by
`jj-lane.sh push` through the helper's own moved-remote recovery path. The
foreign commits were never pushed. The lane's working copy is still parked on
them; that is filed as an L0 question for the operator.

Lessons, rejects, flip conditions and the seven quarantine verdicts:
`corpus/lessons/round-36.md`. Report: `.ufo/reports/round-36/kama.md`.

## round 37 — r36 routed corrections and the KV-cache reclamation/prefix-reuse ground (2026-10-25)

The four r36 routed statements are corrected by append in
`corpus/lessons/round-37.md` (R36-D1: census-end.out committed; R36-D2A:
S371 native_api miswritten; R36-D2B: S364/S365/S377/S396 http_server.py;
R36-D3: ScribeLog/RevQ206 with 429). The r36 lesson and r36 fleet report
blobs are unchanged; the C1 counter re-derives each fact from committed bytes
(`python3 tools/round37-statement-audit.py --repo . --tip <full-commit>` →
`uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met
True`). Three knowledge entries on new ground (KV-cache reclamation, prefix
reuse, the v0.11 hashing-default amendment) and seven registry rows S330, S333,
S334, S335, S346, S347, S363, all opened 2026-10-25 and re-opened by wave-1
seats; C2 counts `named 3 files_exist 3 cited_new 3 met True`. Id collision 0;
scratch validate exit 0 with pre-existing W04 warnings; quarantine hand-check
7/7 agree with round 36. D3 seat accounting (ScribeLog, RevQ206, rc=1,
provider.rate_limit: 429) is named in the round-37 fleet report. KQ46 added to
`corpus/QUALITY.md` for the id-drift class. The lane's working copy is still
parked on the foreign-identity chain (L0 open); this round's commits were made
through `jj-lane.sh` in a scratch clone of the lane remote.

Lessons, rejects, flip conditions and the quarantine verdicts:
`corpus/lessons/round-37.md`. Report: `.ufo/reports/round-37/kama.md`.

## round 38 — the R36-D2C correction, the SGLang docs version-pinning ground, and round-37 instrument closure (2026-10-25)

Three declared claims, frozen in `.ufo/waves/round-38/preregistration.json` at `41e149ceee28b24596b5d8567a0ccf43ebbc6d50` before any seat scored, measured on committed bytes at `d854475aecc1d793f84c10021daaed46f735f270`. Base `2a4a97dc890fe393035986c951797c5d65b6cc69`.

C1 (calibration 7 → 7) corrects the R36-D2 third sub-fact by append in `corpus/lessons/round-38.md`. Round 37 froze only R36-D2A and R36-D2B; the third sub-fact appeared only in the `## Mistakes` evidence cell of `round-37.md`, so the wrong range stood (round-37 verifier spot-check §6 item 4). The correction row R36-D2C names the five staged rows (S332, S336, S337, S338, S339 at `SOURCES.append.md` lines 9, 13, 14, 15, 16) instead of the wrong range. Counter: `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) at base → `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0). The r37 lesson blob and the r37 fleet report blob are unchanged.

C2 (coverage 9 → 9) adds `corpus/knowledge/sglang-docs-version-pinning.md` and `corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md` to the coverage map. The published SGLang docs pages carry no version marker; their sources are contained unchanged in release tag v0.5.22. Counter: `named 0 files_exist 0 cited_new 0 met False` (exit 1) at base → `named 2 files_exist 2 cited_new 3 met True` (exit 0). Sources S352 and S353 (the v0.5.22 raw `.mdx` pages) and S472 (the lane's `git ls-remote --tags` row, first id free in both the lane registry and the staged package) are appended. Staged S360 is rejected: the GitHub REST `/tags` endpoint returned HTTP 403 (rate limit) on this host; the lane's ls-remote receipt carries the tag inventory instead (exit 0, 166 tags, `refs/tags/v0.5.22` peeling to commit `baa9befa`).

C3 (operability 8 → 8) closes the inherited round-37 evidence gaps the verifier routed (§6 items 1–3). Commit `2f780765` lands `tools/round37-statement-audit.py` and `tools/round37-coverage-audit.py`, which round 37 cited but never committed, together with the 37th seat report `CriticEntries.md` and `seat-exit-codes.json`. Counter: `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1) → `found 2 base_found 0 help_ok 2 rerun_ok 2 report_37 1 receipt_ok 1 met True` (exit 0). The receipt parses to 37 members, all with `rc: null`; "Dead seats: none" closes as report presence, not exit status. The rest of the uncommitted round-37 tree (29 scratch files) was not copied; named in the report.

Frontier step: read-only shokuknow `corpus-expansion-1` package, one theme, two entries, three rows (S352, S353, S472); S360 rejected with flip. Id collision: only the 7 round-37 adoptions share bytes; no duplicate ids. Scratch validate exit 0. This round's lane work ran in the scratch clone `/fast/scratch/hyaku/kama-r38`; the parked worktree was left alone on its foreign-identity chain (L0 open); attempt 1 died with no work (watchdog 1293), attempt 2 landed (watchdog 1294).

Lessons, rejects, flip conditions and the quarantine verdicts: `corpus/lessons/round-38.md`. Report: `.ufo/reports/round-38/kama.md`.

## round 39 — source-grounded model-card distinction (2026-10-25)

C1 calibration 7→7 records a sourced assimilation admission and two documented rejects; base no-op had no decisions or S473. C2 coverage 9→9 adds a round-39 README pointer and amendment about model-card `created` metadata, sourced by S473; base lacked pointer, file and row. The OpenAI List models Markdown was re-opened on 2026-10-25 (1,657 bytes); its 10-word quote at line 17 says the field is the model creation timestamp. `corpus/lessons/round-39.md` records the per-entry Gate, mistake findings, rejection reasons and quarantine context. Scratch append mirror validation passed exit 0 with 93 pre-existing W04 warnings before registry append. Fleet-root census validation passed exit 0 at the end (204 rows; A=195, B=6, C=3; mined=185, queued=8, rejected=11). The row was staged by attempt 1 as S472, which round 38 already held on the lane remote for the SGLang tag inventory; attempt 2 renumbered it to S473 by document (URL unchanged) before landing.

Round-start census against the scratch root returned exit 2 because it lacks fleet `shokunin.conf`; `.ufo/waves/round-39/assimilation/census-start.out` records this. The baseline row count 203 is re-derived from the base registry bytes, not from a successful scratch census.

Round-39 wave attack qualification: the required v1 task batch was accidentally dispatched twice; 66 seats were attempted, the same 33 member names in each call. This is disclosed, not represented as one dispatch. One first-call reviewer (R39Attack10, openai-codex/gpt-6-luna) died with `Invalid prompt`; its duplicate completed. Thirty-two unique attack reports were recovered into scratch evidence. No wave 2 or residual call.

Attempt 2 (replay-and-land): attempt 1's commits `eaa4106c` and `8e953f68` were made on the stale base `6a4afdfe` in the parked lane worktree and never reached the lane remote; this replay re-applies their content on `d7954be8` (r37 + r38), renumbers S472→S473, re-runs both frozen counters and the census, and lands through `jj-lane.sh`. The attempt-1 receipts are kept byte-exact under `.ufo/waves/round-39/assimilation/`; the replay receipts are `claim-after-replay.out`, `census-replay.out` and `renumber-map.md`.


## Round 40 — digest citations, authentic wave evidence, and counter defect (2026-10-25)

- **C1 calibration 7→7:** the round-38 verifier routed wrong evidence digests in the S472 citation and R36-D2C package-byte paragraph. Re-opened and hashed both sources; appended S474 and correction notes without rewriting historical text. The frozen C1 counter is invalid for its own sentence: it reads status column `row[7]` instead of teaches `row[6]`, and mutation probes show both false-accept and inability to recognize the valid row. C1 therefore remains unverified. Evidence: `corpus/lessons/round-40.md`; `.ufo/waves/round-40/w1/out/{R40A02,R40A05,R40F01}.md`; base receipt `controls/c1-base.out`.
- **C2 operability 8→8:** staged the byte-exact round-38 session spec/run artifacts, verified SHA-256 pins, and recorded after-counter. Evidence: `.ufo/waves/round-38/w1/{spec,run}.json`; `.ufo/waves/round-40/c2/after.out`; base `controls/c2-base.out`.
- Frontier sourced row S474 was opened against the committed ls-remote output; citation corrections remain append-only.

**Round-40 measured receipts:** frozen C1 command at `2429f48e2c679048d94566a9f3e800d5278b23eb` gives `s474_row=0 amend_corrected=1 r36d2c_fixed=1 false_corrections=0 met=False` (exit 1); no C1 improvement is verified. Frozen C2 at the same revision gives `spec_exists=1 run_exists=1 spec_sha_ok=1 run_sha_ok=1 counts_ok=1 met=True` (exit 0). Full-mirror corpus validation at the landed registry: exit 0, 93 W04, no E; rows 214→215, tier A 204→205, mined 195→196. Receipts: `.ufo/waves/round-40/{c1,c2}/after.out`, `census-end-counts.out`, `census-end-mirror.out`.

**Round-40 wave and commit chain:** one validated v2 wave (`kama-r40-w1`), 64 seats, single batched handoff, 64 final outputs and 64/64 report files. Role mix: reviewer 17, critic 6, mutation-tester 3, scout 8, sentinel 1, connector 3, executor 14, scribe 11, simplifier 1; attack roles 26/64; m_flash content roles executor+scribe+critic+sentinel+simplifier = 33/64. L1 held the planner seat. No dead seat was identified in the 64-result envelope (it records a final output for every member and has no separate status field). Freeze `f327904b72b2ff2aa1c9668cb23aa90054098e81` preceded data; claim/source work landed `697f897f54b027355ab63152e02b0cb3ac206be8`, lesson completion `2429f48e2c679048d94566a9f3e800d5278b23eb`, and final measured evidence/results `03ea3f597b1342927f02f148ad6e06fde7426ca2`. The validated dispatch, orchestrator final-output envelope, and seat reports are under `.ufo/waves/round-40/w1/`.

Round-end fleet-root census rerun: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exited 0 with 93 W04 warnings and no E findings; receipt `.ufo/waves/round-40/census-end-fleetroot.out` is committed with the round. This validates the parked registry independently; before/after row counts remain measured on the fresh lane clone because the parked worktree has inherited stale sandbox lineage.

## Round 41 — head axes table reconciled; pin-watch capability (2026-10-25)

- **C1 calibration 7→7.** The SCORECARD head `## Axes` table had stayed at its round-3 state since round 10, when a superseding table was added lower down. At base `8893b894`, `tools/round41-scorecard-reconcile.py` reads `mismatches=16 met=False`. The head table was replaced with one whose every hash, line count, run line and path re-derives at the measured commit. Scores equal the last-declared vector. The round-3 table is kept byte-intact below it. Evidence: `.ufo/waves/round-41/controls/base.c1.out`, `.ufo/waves/round-41/c1/`.
- **C2 operability 8→8, capability `pin-watch`.** Mines `considerthese/2026-10-25.md` proposal 2. Adds `tools/pin-watch.py`, `registry/engine-pins.tsv` (SGLang v0.5.22, vLLM v0.32.0, llama.cpp b11755) and `corpus/knowledge/engine-pin-watch.md`, sourced on S475 (git-ls-remote manual, opened 2026-10-25) and own-work S476/S477. Result at 2026-10-25T20:03Z: SGLang current, vLLM current, llama.cpp 115 builds behind (b11887). Base: all counter legs 0. Evidence: `.ufo/waves/round-41/controls/base.c2.out`, `.ufo/waves/round-41/c2/`.
- Freeze `6fec0c4c` (counters, preregistration, failing, positive and shortcut controls). Claim commit `24aa1d34`. Integration commit: routed r40 defects D1 (KQ48), D2 (named package reject), D3 (round-38 pointer) and D4 (SCORECARD/lesson corrections); KQ49; pin-watch hardening per the security seat; entry limits per the wave; LOG/README/lesson.
- Wave: one validated v2 wave `kama-r41-w1`, 64 seats through the inline handoff. Results: `.ufo/waves/round-41/w1/kama-r41-w1-results.json`; reports: `.ufo/waves/round-41/w1/out/`. Seat R41D07 left no report file, and its yield was recovered from the transcript.
- Census at start: 215 rows; mirror and fleet-root validate both exit 0, 93 W04. The fleet-root run reads the parked worktree, not the tip (R41A19). Assimilation: none adopted from `merge/kama/` (named reject in the lesson Gate); considerthese proposal 2 mined.
- Lesson: `corpus/lessons/round-41.md`. Measured values: SCORECARD §Round-41 measured results.

## Round 42 — self-description surfaces reconciled; digest-ledger capability; engine-side K05 entry (2026-10-25)

- **C1 calibration 7→7.** Round 41's counter covered only the `## Axes` table; seat R41A10 itemised the surfaces around it that the tree contradicts. At base `0b606b03`, `tools/round42-selfdesc-reconcile.py` reads `mismatches=40 met=False` (banner 4, Planned 3, Retired 4, Saturation 3, head Capabilities 4, README 11, PROVINCE 5, relevance needles 6). The head sections were re-derived from the tree and the round-5 text moved verbatim under §Historical head sections; README names every top-level entry; PROVINCE names every instrument the capability list cites (closing round-41 closure item 2, `pin-watch` absent from Owns); each axis row carries one axis-specific run fact, a substring-needle relevance check that seat R42A05 showed is weak (round-41 closure item 1 is narrowed, not closed).
- **C2 operability 8→8, capability `digest-ledger`.** Mines `considerthese/2026-10-25.md` proposal 1. `tools/digest-ledger.py` classifies every full SHA-256 the lane's documents cite; at base 94 distinct digests are cited and 10 are unexplained (9 unknown, 1 `wrong_unflagged`: the round-38 S472 digest). `registry/digest-ledger.tsv` explains them: 4 external artifacts re-hashed on this host, the S472 wrong digest linked to its correct blob, 5 unverifiable with reasons. Also repairs round-41 R41A10-10: both round-41 counters now remove their export (`TMPDIR` check, claim C2 hygiene leg).
- **C3 coverage 9→9, assimilation from `merge/kama`.** Theme context-capacity, re-grounded in-round from bytes fetched 2026-10-25: `corpus/knowledge/context-capacity-engine-sides.md`, sourced on S478 (vLLM v0.32.0 `kv_cache_utils.py`) and S479 (llama.cpp 704366d7 `server-models.cpp`). Two staged amendments admitted and merged, two refused with flips (`corpus/lessons/round-42.md` §Gate). Id collision check and mirror validation in `.ufo/waves/round-42/assimilation/`.
- Freeze `0bfd47ab` (preregistration, three counters, base/freeze and eight shortcut controls). Census at start: 218 rows, mirror and fleet-root validate exit 0, 93 W04.
- Wave: one validated v2 wave `kama-r42-w1`, 64 seats through the inline handoff (queued at the host capacity cap about 40 minutes). Results: `.ufo/waves/round-42/w1/kama-r42-w1-results.json`; reports: `.ufo/waves/round-42/w1/out/`. Wave findings and what was done: `corpus/lessons/round-42.md` §Wave-1 findings. Integration commit: C3 entry rewritten after attack (hybrid and host-bound vLLM configurations), Gate quotes and refusal rows, ledger rows corrected, `tools/digest-ledger.py` hardened (streaming, confinement, promisor refusal, duplicates), SIGTERM cleanup for the round-41 counters, head-mirror wording, PROVINCE and README corrections, KQ50-KQ53 and six Mistakes rows.
- Counter limits found by the wave and not repaired (counters frozen): C1 relevance needles are substring tests and a 15-line edit meets the counter; C2 three cheap mutants reach `met=True`; C3 coverage leg is not a sourcing test. Listed in the lesson and the report.
- Lesson: `corpus/lessons/round-42.md`. Measured values: SCORECARD §Round-42 measured results.

## Round 43 — instrument registry reconciled; hexrun-census capability; vLLM `/health` process map (2026-10-25)

- **C1 calibration 7→7.** The round-42 wave (seat R42A02) and the outside closure left a standing mismatch: SKILL.md's instrument registry names 12 of the 28 tracked round counters, the gate `tools/gate-registry-check.py` has read `registered 12 unregistered 16 defective 0` since round 35 and its own `--selftest` prints `GATE_SELFTEST pass=5 fail=1` while SKILL.md documents `pass=6 fail=0`. At base `6897ead5`, `tools/round43-registry-audit.py` reads `mismatches=42 met=False` (unreg 16, flags 2, pins 19, selftest 1, dc 1, spot 1, hidden 2). Landed: 19 registry rows (the 16 counters and the three round-43 counters, each with a SHA-256 pin and the exit codes the source returns), the two retired-counter rows given their real flags, the round-42 search-log correction (closure defect D-C), the calibration row's closure count 28→29, README's hidden entries. Wave seat W1R01 showed the frozen counter is met by one mega-row of 11 inserted lines; the landed tree holds 19 individual rows and the limit is reported, not repaired (counter frozen).
- **C2 operability 8→8, capability `hexrun-census`.** Mines `considerthese/2026-10-25.md` proposal 1 (the non-64 half the round-42 digest ledger cannot see) and the round-42 closure item 6. `tools/hexrun-census.py` (implementation B of two independent builds) classifies every 32-127 character hex run other than 64 in the lane's `.md`/`.tsv` documents; at base 210 distinct runs are cited and 73 are unexplained (64 upstream object ids, 7 MD5 sums, a 39-hex truncated tag object and the 65-character citation of round 38). `registry/hexrun-ledger.tsv` explains them: 62 upstream objects each with a committed GitHub API response (`.ufo/waves/round-43/c2/evidence/`), 9 unverifiable with reasons, 2 flagged wrong with their correct objects.
- **C3 coverage 9→9, assimilation from `merge/kama`.** Theme runtime-health, staged round-12 amendment re-grounded in-round from `gh api` objects fetched 2026-10-25: `corpus/knowledge/runtime-health-surface-processes.md`, sourced on S480 (vLLM v0.31.0 release) and S481 (PR 58552). Wave seat W1C01 read the shipped code: `/health` is one route in `vllm/entrypoints/cli/preload.py` answering 200/503; the three states are the PR description's vocabulary. Two staged rows admitted, the round-13 rows (PR 46811, PR 59179, the agentic-api gateway commit, the Semantic Router page) refused with scope reasons and flips (`corpus/lessons/round-43.md` §Gate). Id collision check: lane ids 220, collisions 9, none adopted.
- Freeze `895793e0` (preregistration, three counters, base control and seven shortcut controls). The committed `freeze.c*.out` receipts are byte copies of the base receipts; the counters measured at the real freeze commit are `controls/freeze-measured.c*.out` (C1 reads `mismatches=45` there). Census at start: 220 rows, mirror and fleet-root validate exit 0, 93 W04.
- Wave: one v1 build wave `kama-r43-w1`, 38 seats through the inline handoff (0 dead seats). The planned 48-seat falsify wave was validated but never dispatched: run 7 closed (spawn cap 0). Round total 38, below the 64-100 band. Wave results: `.ufo/waves/round-43/w1/kama-r43-w1-results.json`; reports `.ufo/waves/round-43/w1/out/`. Counter limits found by wave 1 and not repaired (counters frozen): one 11-line mega-row meets C1, a fixture-name shell tool meets C2, stub copies with true irrelevant quotes meet C3, 20 of 53 counter mutants survive; listed in the lesson.
- Measured at `25df591a`: C1 `mismatches=0 met=True`, C2 `met=True` (seeds 43, 7), C3 `met=True` (SCORECARD §Round-43 measured results).
- Frontier: `considerthese/2026-10-25.md` proposal 3 implemented as `registry/staged-refusals.tsv` (73 refused items, 6 stale flips, one quarantine row the registry contradicts); KQ54-KQ57 added to `corpus/QUALITY.md`; five Mistakes rows in the lesson (1a, 1b, 2, 3, 4).
- Lesson: `corpus/lessons/round-43.md`. Measured values: SCORECARD §Round-43 measured results.


## Round 44 — llama.cpp release re-verification at b11889; trend-verdict ledger against 30 closures (2026-10-26)

- **C1 freshness 8→8 (sourced on S482).** Motivating evidence: `tools/pin-watch.py` has reported llama.cpp `behind` since round 41 (b11755 → b11887, now b11889, 117 newer: `.ufo/waves/round-44/c1/pin-watch-freeze.out`) and no row was rechecked (lesson §Mistakes row 1). At base `9d9cc93e` the frozen counter reads `pop=91 … unverified=91 met=False`. Landed: `registry/release-recheck-b11889.tsv` (91 rows: 6 unchanged-file, 82 holds, 3 holds-reworded, 0 drifted, 0 removed), every row read for the code its `teaches` cell depends on by 15 executors and independently re-judged by 8 critics (90/91 agree; S043 disagreement on ledger mechanics only); row S482 (release b11889); `corpus/SOURCES.md` §Round-44 release re-verification; drift outside the population flagged in `SKILL.md` (§Round-28, `dry_sequence_breakers`, commit 63412d873).
- **C2 calibration 7→7.** Motivating evidence: the lane's self-assessed trend verdicts had never been set against its outside closures as a whole. At base the counter reads `missing=204 met=False`. Landed: `registry/verdict-ledger.tsv` (204 rows), `SCORECARD.md` §Round-44 calibration ledger (`agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`) and the calibration row's cite; MANIFEST cross-check 90/90.
- Routed round-43 defects: D1 (SCORECARD pointer) and D5 fixed; D2 row S483 plus the entry's `source:`; D3 forward (every class stated); D4 gate selftest receipt; D6 held-entry corrections appended (eight process qualifications; `CANNOT-ANSWER.md` pointer withdrawn).
- Tools: `tools/release-recheck.py` (draft helper; exit codes repaired after seats V1Code and S9Registry), `tools/release-recheck-selftest-extra.py` (15 cases, seat M3Tool), `tools/pin-trigger-consumed.py` (KQ58), `tools/planned-pointer-check.py` (KQ59); KQ58–KQ61 in `corpus/QUALITY.md`; SKILL.md §Round-44 instrument registry (gate `registered 33 unregistered 0 defective 0`).
- Freeze `77d1bbf5` (preregistration, two counters, base and four shortcut controls, all `met=False`). Census at start: 222 rows, validate exit 0 with 93 W04, 1 W01, 0 E.
- Wave: one v2 wave `kama-r44-w1`, 65 seats through the inline handoff, all 65 settled (seat K1J07 returned its output but wrote no `.md` report; its out directory holds `verdicts.tsv`). Reports `.ufo/waves/round-44/w1/out/`, results `.ufo/waves/round-44/w1/w1-results.json`. Counter limits found (counters frozen): both counters are met by shortcut ledgers (K1Cheat, K2Cheat); listed in the lesson.
- Lesson: `corpus/lessons/round-44.md`. Measured values: SCORECARD §Round-44 measured results.

## Round 45 — ten planned rows re-verified with machine witnesses; claim-outcome ledger (2026-10-26)

- **C1 freshness 8→8 (sourced on S484, S485).** Motivating evidence: the round-44 plan and pin survey (`.ufo/waves/round-44/w1/out/U9Pins.md`) left S010, S014, S019, S038, S041, S046, S048, S055, S058, S477 unrechecked, and the round-44 counter accepted note-only `drifted`/`holds-reworded` (K1Cheat). Landed `registry/recheck-r45.tsv` (11 keys: 3 unchanged-file, 8 holds), upstream copies, three b11889 live receipts, S484/S485, SOURCES §Round-45 re-verification, a b11889 note in `corpus/knowledge/llamacpp-loading-lifecycle.md`. Counter `--fetch` at `21945c61`: `unverified=0 newrows=2 fetch_bad=0 met=True`.
- **C2 calibration 7→7 — not achieved (honest stop).** `registry/claim-outcome-ledger.tsv` (126 rows) and SCORECARD §Round-45 claim-outcome ledger (`agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1` by reading). v1 `valid=91 bad=35 met=False`, v2 amendment `valid=103 bad=23 met=False`: the readers cannot read the population's outcome phrasing (lesson §Mistakes row 2).
- Routed round-44 defects: D1 `tools/seat-yield.py` (KQ62), D3 S483 citation corrections in three entries plus S483 used-by, D4 `tools/manifest-crosscheck.py` (KQ63); KQ64, KQ65. SKILL.md §Round-45 instrument registry (gate `registered 36 unregistered 0 defective 0`). SCORECARD head re-anchored (banner, calibration row spot-check count 31, depth hash).
- Wave `kama-r45-w1` (64 seats) stalled at 32 spawned with no seat turn; no WAVE-DONE. Lesson `corpus/lessons/round-45.md`.

## Round 46 — llama.cpp re-verification at b11906 with machine witnesses; append-only-audit capability (2026-10-26)

- **C1 freshness 8→8 (sourced on S486, S487).** Motivating evidence: llama.cpp moved 17 commits past the b11889 re-verification (b11906 = `4d71b42f`, published 2026-10-26T19:45:36Z), and the round-44 counter accepted note-only `holds-reworded`/`drifted` verdicts (round-44 seat K1Cheat). Landed `registry/release-recheck-b11906.tsv` (91 rows: 6 unchanged-file, 81 holds, 4 holds-reworded, 0 drifted, 0 removed; frozen counter `tools/round46-release-recheck-audit.py` with witness columns), S486 (b11906 binary/tag identity), S487 (three b11906 live receipts, 11/11 checks each), SOURCES §Round-46 release re-verification. The stories260K model was re-fetched from `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` at its pinned sha256 (r45-D3; `.ufo/waves/round-46/c1/live/model-fetch.txt`).
- **C2 calibration 7→7 (capability acquisition; considerthese/2026-10-26.md proposal 1).** Motivating evidence: round-45 commit `0718b6ab` truncated four append-only files and only a same-round repair (`82b5e9d3`) caught it. Landed `tools/append-only-audit.py` (10-case selftest), its SCORECARD capability row (canonical list as of round 46), SKILL.md §Round-46 instrument registry, PROVINCE instrument list. On the lane at base: 5 events, 3 restored by `82b5e9d3`, 2 SCORECARD partials that are documented head re-derivations (seats X2Hist, R2Restore).
- Wave `kama-r46-w1` (65 seats, one v2 wave, 0 dead); KQ66–KQ68; lesson `corpus/lessons/round-46.md` (S121 critic-over-builder decision; shared-definition blind spot of C2's tool and counter; spec-prose miscount). KQ65 hand-read sample (411 + 142 labelled lines) committed as wave evidence for a later reader; no reader frozen (r45-D1 deferred). Freeze timestamp check exit 0 (r45-D2).

## Round 47 — append-only audit v2 checked against git numstat and a declared contract; live receipts re-runnable from committed provenance (2026-10-26)

- **C1 calibration 7→7 (instrument correction against outside ground truth: `git diff --numstat` and a constructed fixture).** Motivating evidence: the round-46 outside closure's D1 and D2 and two round-46 wave seats. D1 (`corpus/lessons/round-46-verifier-spotcheck.md:137`): v1 dropped every deleted line whose text starts with `--` as if it were the `---` header (`tools/append-only-audit.py:102` at `172b8ad0` filters `not x.startswith("---")`), so on the lane its deleted counts sat below git's own — `0718b6ab` SCORECARD.md 2417 vs numstat 2421, LOG.md 2290 vs 2292. D2 (`:84`, `:138`): `restored_at_tip` was measured against the audited tip, and the SCORECARD `0718b6ab` restoration fell 2416 → 2409 between `0163fea2` and `4340cf2f` with no new deletion. Seat K2Design (`.ufo/waves/round-46/w1/out/K2Design.md:15`) found the five-file default declared nowhere — 3 of its 5 files are append-only by no declaration — and seat Rev2Decl (`.ufo/waves/round-46/w1/out/Rev2Decl/contract.md`) reconstructed the real contract: region-scoped, three exceptions, and `corpus/lessons/` (68 files, 292 commits) declared append-only while yielding 0 events under v1. Landed at `3a09a1d9`: `tools/append-only-audit.py` v2 (`append-only-audit/v2`) and `registry/append-only-contract.tsv`, whose 7 rows are LOG.md, SCORECARD.md, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md` and `registry/history/DELTA.md`, each row's `declared_at` line carrying the declaration that names it (all 7 checked). v2 reads deleted lines from the `-U0` diff by hunk-header counts, byte-exact, and requires equality with `git diff --numstat`; restoration is `held(x) = Σ_l min(D[l], max(0, M_x[l] − K[l]))` maximised over the event's own window, so a later head re-anchor cannot lower it. At the build the tool expands 85 files (79 lessons + 6) over 303 commits and reports 5 events with `summary restored=3 partial=2 unrestored=0`, exit 1: `0718b6ab` LOG.md 2292/2292 restored, `corpus/QUALITY.md` 375/375, `corpus/README.md` 663/663, SCORECARD.md 2421/2420 partial; `dd9f5dc6` SCORECARD.md 31/24 partial. The two partials are the documented SCORECARD head re-derivations (seats X2Hist, R2Restore) that the contract's SCORECARD row exempts, so exit 1 is the expected build state and the counter's lane leg compares the tool with its own recomputation, not with zero partials. A recount independent of the tool (`git log --numstat --no-renames` over the same 85 paths) gives the same five events and the same deletions (2292, 2421, 375, 663, 31). `--selftest` prints `AOA_SELFTEST pass=15 fail=0`; with the build's contract, `--to 172b8ad0` and `--to 3a09a1d9` give equal `deleted` and `restored_max` on all five events, so the v1 2416 → 2409 drop is gone. Limits (preregistration): restoration is text identity, so a line restored elsewhere in the file counts; the contract covers only what its declaring lines name, so an undeclared append-only file stays invisible to the counter.
- **C2 operability 8→8 (sourced on S488 (b11909 release) and S489 (b11909 receipts)).** Motivating evidence: r45-D3 (`corpus/lessons/round-45-verifier-spotcheck.md:148`) — S485 and the S041/S046/S055 re-runs depended on `~/.cache/kama-shokunin/models/stories260K.gguf`, which was gone, and nothing recorded the re-fetch URL or the digest — and r46-D5 (`corpus/lessons/round-46-verifier-spotcheck.md:141`) — the b11906 receipts' `teardown.log_path` pointed into deleted seat scratch. Landed at `3a09a1d9`: live receipts schema `kama-llamacpp-live/v4` (`tools/kama-llamacpp-live.py`) with a `provenance` block recorded from `--server-asset-url`/`--server-asset-sha256`/`--server-member`/`--model-url`, and `teardown.log_path` always null because the temp log is always deleted (its kept lines are inlined in `teardown.log_lines`); `tools/kama-live-replay.py`, which re-acquires both inputs from the receipt's URLs into `--work`, verifies both sha256 values before anything is extracted or executed, re-runs the lifecycle and compares the original check by check (exit 0 match, 1 differs, 2 refused); three receipts `.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json` at llama.cpp b11909 = `caa8191d` (published 2026-10-26T21:00:58Z, prerelease), each 11/11 checks passed with `build_info b11909-caa8191df`, provenance server `llama-b11909-bin-ubuntu-x64.tar.gz` sha256 `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` member `llama-b11909/llama-server`, model `stories260K.gguf` sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, `teardown.log_path` null; and `.ufo/waves/round-47/c2/live/install.txt` recording the asset (22475032 bytes, digest equal to the release record `.ufo/waves/round-47/c2/release-b11909.json`), `version: 0.7.0-dev (build 11909, commit caa8191df)` and the model URL with its cache-copy history. b11906 = `4d71b42f` was round 46; `corpus/SOURCES.md` holds 228 rows at the build and none names b11909, so the row lands at integration. `tools/kama-live-replay.py --selftest` prints `KLR_SELFTEST pass=10 fail=0` (model digest wrong, asset digest wrong, digest differs from receipt, v3 receipt, missing url, unsafe member, absent member, http refused, check differs, match). Limits (preregistration): three sampled instants on one 260K model, not model quality or timing; agreement is check-by-check pass/fail equality; the counter replays receipt-1 only and needs github.com and the model host.
- Routed defects: r46-D1 and r46-D2 to C1; r46-D5 and r45-D3 to C2; r46-D3 to the frontier as this round's lesson Mistakes row — `considerthese/2026-10-26.md` proposal 3, a running count of counters a shortcut can satisfy, written with a check that can fail; r46-D4 to the frontier — the 21 `hexrun-census` unknowns ledgered or closed by wave seats, no claim —; r46-D6 is operator/aggregator (cross-lane truncation class) and was not acted on. Assimilation: none — both claims work the lane's own instruments and evidence. Freeze `bbcc6dc2`: preregistration, both counters (sha256 `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed` C1, `15408dce5b2f8f5dbe4dd7bacf17ddb0737fcbe480686907f40483273b128b0f` C2, equal to the preregistration), the base and three shortcut controls (all `met=False`), the start census (exit 0, 93 W04, 1 W01, 228 rows) and the b11909 release record. Build `3a09a1d9` (9 files, +2517/−114) also carries the freeze-time receipt `freeze/prereg-time-check.out` (`exit=0`). Wave `kama-r47-w1` (65 seats, one v2 wave, policy v2, dispatch `46a924e0`).

**Round-47 integration:** SOURCES S488–S491 (b11909 release, b11909 v4 receipts, the stories260K resolve URL, git `--numstat`); KQ69–KQ71 in `corpus/QUALITY.md`; `SKILL.md` §Round-47 instrument registry (gate `registered 40 unregistered 0 defective 0`) and a how-to for re-running live evidence; capability `live-receipt-replay` (first-working round 47) and the v2 wording of `append-only-audit` in a round-47 canonical capability list; PROVINCE instrument cell; 22 hexrun-ledger rows (round-46 closure D4) and 2 digest-ledger rows; `tests/llamacpp-live/check-receipt.py` and `tools/gguf-identity.py` accept v4; post-wave hardening of both tools (lesson §Wave). Wave `kama-r47-w1`, one v2 wave of 65 seats. Measured values, the commit chain and the wave's counter limits: SCORECARD §Round-47 measured results and §Round 47 "What `met=True` does not show".

- Lesson: `corpus/lessons/round-47.md`.

## Round 48 — append-only audit v3 grades the declared carve-outs; live evidence a shortcut cannot replay (2026-10-26)

- **C1 calibration 7→7 (instrument correction: the lane's declared append-only rule, carve-outs included, in machine-readable bound form; outside ground truth `git diff --numstat` and fixtures whose expectations are written by construction).** Motivating evidence: the round-47 outside closure's D5 (`corpus/lessons/round-47-verifier-spotcheck.md:101`) and four round-47 wave seats. Seat Rev1Restore (`.ufo/waves/round-47/w1/out/Rev1Restore.md:3`) showed v2's two `partial` events are the SCORECARD §Axes head re-anchor that the contract note already called expected — "the exit 1 is an instrument gap, not a lane violation" — so the carve-out lived in prose only. Seat K1Design (`:58`, `:59`) found the append-only `## Errata` region of `corpus/knowledge/consumer-registry.md` declared but unguarded and two declared ledgers absent from the contract. Seat V1Ctr F1 (`V1Ctr.md:20`) found the contract leg accepting any line containing `append`: the round-47 row `corpus/QUALITY.md:24` bound only because the word "appended" contains it. Seat K1Fixture (`:3`) found the `max(0, ·)` clamp's negative branch and merge first-parent selection exercised by no leg and the exact-20 threshold hit in about one run of three (P≈11/35); seat X1Stable (`:3`) found `restored_max` never falling while the tip loses restored lines in sub-threshold commits. Landed at `380bcdff`: `tools/append-only-audit.py` v3 (`append-only-audit/v3`, sha256 `ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`) and `registry/append-only-contract.tsv` v3 (header `path/rule/declared_at/region/note`, sha256 `ca0618e5…`, 9 rows: the seven round-47 rows, of which `corpus/QUALITY.md` and `corpus/README.md` are re-pointed because their v2 `declared_at` lines only say "appended" and `SCORECARD.md`'s to the paragraph that names all five files, plus `registry/report-landing-errata.tsv` (K1Design D3) and `corpus/knowledge/consumer-registry.md` with `only=## Errata@corpus/knowledge/consumer-registry.md:30` (K1Design D2)). `SCORECARD.md` now carries `exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`, a title ungraded only while the window maximum of its line count reaches its parent's; `regressed` and vanishing/binding failures reach the exit code; every declaring line must say append-only for its row's path and not negate it. The build's C1 finding: with the v3 tool and the v3 contract, the round-47 tip `33e00582` reports `regressed=1` — the `0718b6ab` SCORECARD.md event's `held_at_to` 2348 against `restored_max` 2349, its one graded missing line being the round-45 authority banner at `SCORECARD.md:6`, which rounds 46 and 47 rewrote in place although that line promises the replaced head text is kept verbatim. The build appended the r45 and r46 banners byte-exact under `SCORECARD.md` §Superseded head banners (`git show 82b5e9d3:SCORECARD.md | sed -n 6p`, `git show 42ea1204:SCORECARD.md | sed -n 6p`), and states the rule that from round 48 each round appends the banner it replaces. Measured at the build (`.ufo/waves/round-48/w1/out/S9Log/c1-build.out`): `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0 — the tool expands 89 files over 311 commits and reports 5 events, all `restored`: `dd9f5dc6` SCORECARD.md 31 deleted / 14 graded / 17 ungraded / restored 14, `0718b6ab` LOG.md 2292/2292/0/2292, SCORECARD.md 2421/2349/72/2349, `corpus/QUALITY.md` 375/375/0/375, `corpus/README.md` 663/663/0/663; `regressed 0`, `vanished 0`, `bad_declarations 0`; tool `--selftest` `AOA_SELFTEST pass=27 fail=0` (the counter requires ≥20) and the counter's eleven constructed fixtures pass (threshold 20 vs 19, exempt head rewritten vs gutted, a dated section rewritten in the exempt file, `only=## Errata`, the `max(0, ·)` clamp 20-of-40, a merge whose first parent keeps the lines, a restoration re-deleted to `held_at_to` 15 with `regressed 1`, `--`/CRLF lines, three declarations that must not bind, and a clean repo). The binding rule is not vacuous: re-expressed in v3 form, the round-47 declaring pointers yield `corpus/QUALITY.md` and `corpus/README.md` unbound (`bad_declarations=2`, exit 1; `.ufo/waves/round-48/w1/out/S9Log/v2-pointers-under-v3.out`), which is why three rows moved to the paragraph at `corpus/README.md:761` that names the five files append-only. Limits (preregistration): the counter recomputes the v3 definition on its own code path, so lane equality is not independent of the definition (the fixtures and numstat are the outside ground truth); the exemption reads `## ` headings only, so a heading inside a fenced block counts; held lines are a whole-file multiset, so an exempt line's text can pay for a graded line with the same text; the threshold stays 20 and sub-threshold deletions are ungraded — so the round-48 banner re-anchor is itself a single line and creates no event; it is graded only through the historic `0718b6ab` event's `held_at_to` (2349 exactly while every banner that deletion held stays somewhere in the file, which the §Superseded head banners append keeps true).
- **C2 operability 8→8 (sourced on S492, the pinned Hugging Face revision, and S493, the hub download guide).** Motivating evidence: the round-47 closure's D1–D4 and D6 (`corpus/lessons/round-47-verifier-spotcheck.md:97`–`:100`, `:102`) and four round-47 wave seats. Seat K2Cheat met the round-47 counter with three of four probed shortcuts — a host-cache copy, a fabricated 0-byte rerun and a forged `started_utc` — because the counter trusted the rerun receipt's own paths and digests; seat K2Tamper and seats M2Ctr/M2Replay added that the tamper leg pinned only two digit flips; seat K2Design F1/F2 found provenance recorded unverified at record time and replay agreement limited to check pass/fail; seat K2Checks showed two receipts can agree on every check and still disagree on the observed bodies; seat X2Revision showed the model URL named the moving `main` (`resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/…` serves the same `270cba1b…` bytes; `main` served three different byte strings). Landed at `380bcdff`: live receipts schema `kama-llamacpp-live/v5` (`tools/kama-llamacpp-live.py`, sha256 `1e5ea0fd…`) — the four v4 provenance flags must come together with `https://` URLs, `--server-archive` selects v5, and the tool hashes the release archive, the named archive member and the model *before* starting a server, refusing with exit 2 otherwise; the receipt adds `provenance.model.commit` (40 hex) and `provenance.verified{at:record, archive_sha256, member_sha256, model_sha256}`; `tools/kama-live-replay.py` v5 (sha256 `69837013…`) accepts v4 and v5, passes `--server-archive` for v5, compares schema, outcome, digests, checks **and a stable projection of the captured surfaces** (props fields, slots count + body digest, health status + body digest, models ids/owned_by, metrics status, loading envelope, teardown outcome, listener ownership), and gains `--compare A B`; three receipts `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` at llama.cpp b11909 with `provenance.model.url` pinned to `/resolve/499bc882…/`, `verified.at=record`, archive `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`, member `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`, model `270cba1b…`, 11/11 checks each, `build_info b11909-caa8191df`, `teardown.log_path` null (install record `.ufo/waves/round-48/c2/live/install.txt`; no new install this round); and rows S492/S493 in `corpus/SOURCES.md`. Measured at the build (`.ufo/waves/round-48/w1/out/S9Log/c2-build.out`, started 2026-10-26T22:35:31Z, 14 s): `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0 — all three receipts replay from committed bytes on real downloads from github.com and huggingface.co, the counter hashes the re-acquired archive, member and model itself, the rerun's `started_utc` is not earlier than the counter's start, `--compare` accepts an instance-only copy and refuses each of five stable-surface changes, and swapped asset/model URLs exit 2 with `digest-mismatch` and no rerun receipt. `tools/kama-live-replay.py --selftest` prints `KLR_SELFTEST pass=21 fail=0`. The control `junk-c2-r47-relabel` (round-47 receipts relabelled v5 with a fabricated `verified` block and a copying replay) fails at `receipts=1 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 met=False`, which bounds the receipts leg: it is structural, and the replay/urlswap legs carry the evidence. Limits (preregistration): replay needs github.com and huggingface.co and b11909 is a GitHub prerelease, so pruning the tag makes the replays refuse permanently (r47-D7 disclosed, no cache hardening this round); the stable projection is a chosen set of surfaces and excludes timing, ports, pids, log text and the models `created` field as instance facts; the record-time leg drives the real tool against a stub server, stub archive and stub model, so it shows the refusal happens before execution, not that the real archive is genuine (the receipts' `verified` block and the replay show that).
- Routed defects: r47-D1, D2, D3, D4 and D6 to C2 (counter-side hashing and urlswap, all-three replay, record-time provenance, stable projection, pinned revision); r47-D5 to C1 (bound regions, binding rule, `regressed` in the exit, fixture coverage, non-vacuous stable leg); r47-D7 as the disclosed prerelease-cliff limit; r47-D8 to the frontier (the blind `tools/sources-append-only.py` parser, a wave seat's repair, no claim); r47-D9 to report discipline (regression receipts re-run and committed at the final tip, with their `tip=` line; lesson Mistakes row 2). Frontier, not claims: `considerthese/2026-10-26.md` proposal 3 (a running count of counters a shortcut can satisfy, promoted to `tools/` with its `--check`) and the b11906 ledger population at b11909+ (seat U2Server: `src/llama-context.cpp` and `src/llama-kv-cache.cpp` changed). Assimilation: none — both claims work the lane's own instruments and evidence. **Integration item found at the build by seat S9Log and not fixed by the wave:** the independent validator `tests/llamacpp-live/check-receipt.py` refuses the round-48 v5 receipts — `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-48/c2/live/receipt-1.json` exits 1 with `schema is 'kama-llamacpp-live/v5', want … v4` plus three spurious check-set problems, because `RECEIPT_SCHEMA_V5` does not exist (`tests/llamacpp-live/check-receipt.py:51-54`), the schema gate lists v1–v4 (`:310-314`) and the required-check branch falls back to the v1 set (`:1005`); the v5 check ids equal v4's, so the verified minimal fix is one constant plus the three membership tuples, the schema gate and the `--require-schema` map (`.ufo/waves/round-48/w1/out/S9Log/check-receipt-v5.diff`, 51 lines, `git apply --check` clean at `380bcdff`: the patched copy prints `VALID` on all three receipts and its `--selftest` still prints `14 VALID and 1 NOT-EVALUATED receipts accepted; 103 mutations + unreadable case rejected`), with a v5 block for `provenance.model.commit`/`verified` as the fuller fix.
- Freeze `12284ba3`: preregistration (`frozen_at_utc` 2026-10-26T22:19:34Z), both counters with sha256 `92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7` (C1) and `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09` (C2), equal to the preregistration; the base and five shortcut control receipts, all `met=False` (`base.c1` at `33e00582`: `selftest=0 contract=0 lane=0 fixture=0 stable=0 fixture_fail=11`; `base.c2`: `receipts=0 … replayed=0/3`, the receipts and the pinned row absent; `junk-c1-v2-relabel`: v2 tool relabelled v3 with a v3 contract, `met=False`; `junk-c1-drop-scorecard`: v2 tool with a v3 contract minus the SCORECARD row, `rows=8 files=88 met=False`; `junk-c2-r47-relabel`: `met=False`); the start census (`.ufo/waves/round-48/census/start.out`, exit 0, 93 `W04`, 1 `W01`, 232 rows) and the pinned-revision record (`.ufo/waves/round-48/c2/hf-revision-499bc882.txt`, `x-repo-commit` and `x-linked-etag` plus the download digest). The KQ64 freeze-time check (`.ufo/waves/round-48/freeze/prereg-time-check.out`) prints `RESULT pass`, exit 0, for both timestamps. Build `380bcdff` (23 files, +4359/−79) also carries the superseded-banner append and the round-48 receipts. Wave `kama-r48-w1` (one v2 wave, policy v2, dispatch `b85783e8`; `spawn 69`: critic 16, reviewer 13, executor 12, scribe 11, mutation-tester 5, scout 5, connector 4, simplifier 1, revenger 1, sentinel 1; attack roles reviewer+critic+mutation-tester = 34/69).

**Round-48 integration:** wave kama-r48-w1 (69 seats) attacks folded into SCORECARD §Round 48; post-wave fixes: replay hardening (V2Replay, K2Selftest), v5 readers (K0Harm F2/F3), sources guard repair (X9SourcesGuard, closure D8), shortcut tally promoted (X9Tally), contract rows (K1Binding, K1Contract), r42-r44 banners (X1Banner), hexrun row (X4Hex). Measured values: SCORECARD §Round-48 measured results (appended after the measured commit).

- Lesson: `corpus/lessons/round-48.md`.

## Round 49 — a replay an outside observer can watch run; append-only carve-outs that follow where text was born (2026-10-26)

- **C1 operability 8→8 (sourced on S494, the llama.cpp server README at b11909, and S495, proc_pid_exe(5)).** Motivating evidence: the round-48 outside closure's R5 (`corpus/lessons/round-48-verifier-spotcheck.md:114`, seats K2Cheat and K2Urlswap: a replay that never runs a server met the round-48 counter, so `replayed=3/3` proved re-acquisition and comparison, not execution) and R1 (`:110`, seat Sen2Live F1: a ~104-byte archive declaring a 10^15-byte GNU sparse member made `verify_archive_member()` hash for days before the server started). Build: `tools/kama-live-replay.py --witness-dir` and `tools/kama-llamacpp-live.py --witness-dir/--witness-timeout` (`hold_for_witness()`: `ready.json` {port, pid of the llama-server child}, held until `release`); `verify_archive_member()` bounded before it reads the member (regular archive ≤ 1 GiB, ≤ 4096 entries, member not sparse, member size = `--server` size). Counter `tools/round49-replay-witness-audit.py` observes the held server from `/proc` and through a nonce sent to `/tokenize` and `/detokenize`, checked against its own decoding of the model vocabulary.
- **C2 calibration 7→7 (instrument correction: the lane's append-only carve-out graded by where a line's text was born; declarations bound by whole-word tokens, a negation window and no wildcard self-declaration).** Motivating evidence: round-48 seats K1Regions (dated text moved under an exempt heading and deleted there exits 0, `ungraded`) and K1Binding (`log` inside `catalog` binds; `not strictly append-only` binds; a lesson's own line bound the whole `corpus/lessons/*.md` row), carried in SCORECARD §Round 48 "What met=True does not show" and the closure's R5. Build: `tools/append-only-audit.py` v4 definitions (JSON shape unchanged, `"definition": "v4"`). On the lane v4 grades seven more lines of the `0718b6ab` SCORECARD.md event (ungraded 72 → 65: six `## Capabilities` mirror rows born in §Round 34 and one born in §Round 41, seat K2Origin F6); all are held, so the event stays `restored` and the lane exits 0.
- Freeze `36d5ed26`: preregistration (`frozen_at_utc` 2026-10-26T23:17:45Z), counters `tools/round49-replay-witness-audit.py` and `tools/round49-append-audit-v4-check.py` with the sha256 the preregistration names; controls all `met=False` (`base.c1`/`base.c2` at `438127bc`; `junk-c1-fake-witness`: a python stub answering `/tokenize` from the model's own vocabulary with `-m <model>` in its argv fails only the exe digest; `junk-c2-no-exempt`; `junk-c2-word-token` 7/8); start census exit 0; source captures `.ufo/waves/round-49/c1/`. Build `74558c71` (after the freeze, before the wave). Wave spec `122c4ee9` (71 seats, policy v2).
- Routed defects: r48-R1 → C1 (bounded verification); r48-R5 → C1 (execution witness) and C2 (K1Regions, K1Binding); r48-R2/R3 → report discipline (lesson Mistakes rows 1–2, KQ79); r48-R4 → role share computed from the live route map (Mistakes row 3).

- Lesson: `corpus/lessons/round-49.md`.

## Round 50 — the server bound to the replay that started it and to the model bytes it mapped; append-only origins that follow the commit graph (2026-10-26)

- **C1 operability 8→8 (sourced on S496, Linux proc_pid_maps(5), and S497, PR_SET_PDEATHSIG(2const)).** Motivating evidence: the round-49 outside closure's R1 (`corpus/lessons/round-49-verifier-spotcheck.md:103`, seats K1Cheat, K1Design, R0Controls) and R2 (`:104`, late seat X1Kill). Seat K1Cheat (`.ufo/waves/round-49/w1/out/K1Cheat.md:3`, `:46`) met the round-49 counter with a decoy replay — no archive download, no live tool, the round-48 rerun receipts with `witness` injected, 5.5 s against an honest ~20 s — and with a `PYTHONPATH`/`sitecustomize` hijack of the counter's inherited environment; the counter never joined the observed pid to the rerun receipt's `child_pid`. Seat K1Design (`K1Design.md:3`) showed the witness proved a frozen-binary server was alive and answering, not that it was the process whose captures the rerun receipt holds, nor the model bytes it had loaded. Seat R0Controls (`R0Controls.md:28`, `:42`) met the counter with a stub that writes `ready.json`, answers the nonce from the model's own vocabulary and copies the original receipt; the hold was self-asserted. Late seat X1Kill (`X1Kill.md:3`, `:48`) showed SIGKILL of a replay left replay, live tool and server up, `pdeathsig` covering one hop only (live tool → server, 0.25 s). Build at `97c864be`: `tools/kama-live-replay.py` starts the live tool with `python -I` and only `PATH`/`HOME`/`LANG`/`LC_ALL` plus a `TMPDIR` under the replay's work dir (`LIVE_ENV_KEYS`, `live_env()` at `:88`, `:112`; the child's argv and `preexec_fn` at `:319` and `:332`), the replay sets its own parent-death signal (`set_own_pdeathsig()`, `:100`, called at `:587`) so killing whatever started it takes replay, live tool and server down, and a rerun whose `model_mapping` is absent or hashes to anything but the receipt's model is refused (`:346`, `:348`). `tools/kama-llamacpp-live.py:678` records `model_mapping`: the file-backed mapping of the server child whose pathname is `--model`, read from `/proc/<pid>/maps` (dev, inode, pathname), re-opened by that pathname with `O_NOFOLLOW`, accepted only when `fstat()` shows the same dev and inode and a regular file of the mapped size, then hashed; written into the receipt at `:2003` while the child is running (`:1763` default `None`, never a check id — the v1–v5 check lists are unchanged). The frozen counter `tools/round50-replay-bind-audit.py` (sha256 `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`) starts each replay through a `python3 -I -c` invoker with an environment of `PATH`/`LANG`/`HOME`/`XDG_CACHE_HOME`/`TMPDIR` (last three under `--scratch`), the proxy variables when it has them, and two canaries (`KAMA_R50_CANARY`, a `PYTHONPATH` `sitecustomize.py` that stamps `<pid> <argv>`), and while the replay holds its server it checks the exe digest, a LISTEN socket whose inode is one of the pid's fds, a fresh nonce against its own decoding of the model's tokenizer vocabulary, descent from the replay process, canary absence in the process and its parent plus an empty marker file, and the mapped dev/inode/pathname hashed to the frozen model; after release it joins the observed pid with the rerun receipt's `child_pid`, reads the same dev and inode back from `model_mapping`, and requires the pid gone and the port refusing. Build-time value (`.ufo/waves/round-50/measured/c1-build.out`): `bind=1 teardown=1 newrow=1 bound=3/3 met=True` — three replays held servers on pids 2876695/2920026/2958773 (ports 40197/41321/35623), each exe+listen+tree+env+mapped ok with a nonce round-trip, mapping dev 103:05 with inodes 1082269665/613853333/1149932363, teardown `invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`, newrow `3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']`. Base control (`.ufo/waves/round-50/controls/base.c1.out` at `26ecba64`): `bind=0 teardown=0 newrow=0 bound=0/3 met=False` — each receipt's server parent carries `KAMA_R50_CANARY`, `model_mapping None`, the planted `sitecustomize` imported by one interpreter, and after SIGKILL of the invoker `after 30.06 s alive [531059, 568483, 573554] port ACCEPTS`. Limits (preregistration): the mapped check compares the maps dev/inode with a `stat()` of the pathname and hashes that path now, so a file rewritten in place with identical bytes is indistinguishable and a filesystem whose maps dev differs from `st_dev` (btrfs subvolumes) fails closed; the env leg plants two canaries, not `LD_PRELOAD` or a modified `python` on `PATH`; the teardown leg kills the invoker once, during the hold, not during download or readiness.
- **C2 calibration 7→7 (instrument correction: the lane's append-only rule graded independently of rev-list sibling order, of headings inside fenced code blocks and of a moved line's line ending, with every deleted line accounted for; outside ground truth twelve constructed fixtures whose expectations are written by construction and `git diff --numstat`; sourced on S498, CommonMark 0.31.2 §4.5).** Motivating evidence: the round-49 outside closure's R3 (`corpus/lessons/round-49-verifier-spotcheck.md:105`, seats K2Origin, X2Fixtures, K2Cheat, V2Ctr). Seat K2Origin (`K2Origin.md:24` F3) showed v4 origin taken from the first blob in `git rev-list --topo-order --reverse`, so identical merge trees with the parents swapped gave exit 0 vs exit 1; F4 (`:32`) a fenced fake `## Axes` title re-titling the dated lines after it, hiding a 25-line dated loss at exit 0; F5 (`:37`) CRLF variants of head lines having no origin and being graded; F6 (`:42`) seven `## Capabilities` mirror rows of the lane's own head falsely graded. Seat K2Cheat (`K2Cheat.md:3`) met the round-49 counter with a no-origin tool that under-reported `ungraded`, because the lane leg only upper-bounded the tool's self-reported count. Seat V2Ctr (`V2Ctr.md:3`, `:38`) showed the binder is a verbatim copy of the tool's rule (a consistency pass, not an independent oracle) and the per-event check is skipped when the tool reports `ungraded=0`. Build at `97c864be`: `tools/append-only-audit.py` v5 (JSON shape unchanged, `"schema": "append-only-audit/v3"`, `"definition": "v5"` at `:573`) — `key(l)` drops one trailing CR (`:275`), `fence_open()`/`fence_close()` implement CommonMark 0.31.2 §4.5 including an unclosed fence running to the end of the file (`:282`, `:295`), `sections()` ignores `## ` lines inside (or being) a fence line (`:306`), and `origins()` unions the section titles at every birth of a key — a commit holding the key while no parent's blob does (`:480`) — so origin is a property of the commit graph, not of listing order; the graded/ungraded carve-out reads the CRLF-normalised key (`:544`). The frozen counter `tools/round50-append-audit-v5-check.py` (sha256 `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46`) runs 12 constructed fixture scenarios under its own `--scratch`, each also asserting `graded + ungraded == deleted` for every event, and on the lane requires exit 0, `bad_declarations 0`, ≥5 events, its own binder over every contract row, `graded + ungraded == deleted` with `deleted` equal to `git diff --numstat`, and the tool's `ungraded` at most its own v5 count per event. The four new scenarios: order-a/order-b (one base, branch A adds `twin line` at the end of `## Axes`, branch B the same line at the end of `## Round 1`, merge holding both, then `## Axes` rewritten with the twin deleted; the same trees with the parents swapped must both report `deleted=25 graded=0 ungraded=25 ungraded` and exit 0), fence (25 dated lines behind a fenced fake `## Axes` deleted while `## Axes` regrows: `deleted=25 graded=25 status=unrestored`, exit 1), crlf-launder (25 dated lines moved under `## Axes` as CRLF, then deleted there: same graded 25, exit 1). Build-time value (`.ufo/waves/round-50/measured/c2-build.out`): `fixture=1 lane=1 scenarios=12/12 met=True`; lane `tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89`, event `dd9f5dc6c0e6` ungraded 17 ≤ v5 natively exempt 23 and event `0718b6abbda6` ungraded 72 ≤ 72 — `ungraded_lines` 82 → 89 because the seven `## Capabilities` mirror rows now have a head birth under the v5 key and origin (F6 resolved), all five events still `restored`. Base control (`.ufo/waves/round-50/controls/base.c2.out` at `26ecba64`): `fixture=0 lane=1 scenarios=9/12 met=False` — order-b fails (exit 1, want 0), fence fails (exit 0, want 1), crlf-launder reports `ungraded=25` where v5 grades 25; lane `ungraded_lines 82`, event `0718b6abbda6` ungraded 65. Limits (preregistration): births are computed over every commit reachable from `<to>` (all parents), so a key reborn after deletion adds the titles of its rebirth, and text born in both an exempt and a dated section counts as exempt-born (v4 rule kept); the lane leg's binder is still the v4 copy (V2Ctr) and the sub-20 threshold is unchanged.
- Freeze `601c8889`: preregistration (`frozen_at_utc` 2026-10-27T00:20:47Z, base `26ecba64`, kill conditions "any leg 0 at the measured commit, or met=True on any control"), both counters (`ff6ac2ac…` C1, `925f07a4…` C2, equal to the preregistration's `counter_sha256` as `sha256sum` reads them at the tip), the base controls both `met=False` (`base.c1`: `bind=0 teardown=0 newrow=0 bound=0/3`; `base.c2`: `fixture=0 lane=1 scenarios=9/12`), the start census (`.ufo/waves/round-50/census/start.out`, exit 0, 93 `W04`, 1 `W01`) and the three source captures (`c1/proc_pid_maps.5.txt` 269 lines, `c1/PR_SET_PDEATHSIG.2const.txt` 232, `c2/commonmark-0.31.2-s4.5.txt` 578). The freeze-time timestamp check prints `RESULT pass` (exit 0) for the preregistration's one timestamp against the commit's committer time (`2026-10-26T21:20:51-03:00`). The preregistration also names seven ablation controls (C1: no env allow-list, no replay parent-death signal, no `model_mapping` record, a decoy replay copying the original `child_pid`; C2: v4 fence-blind sections, byte-exact origin keys, v4 first-in-rev-list origin), every one of which must read `met=False`; only the two base controls are committed at the freeze, and the ablation receipts land with the wave. Source rows `S496` (proc_pid_maps(5)), `S497` (PR_SET_PDEATHSIG(2const)) and `S498` (CommonMark §4.5), each used-by `corpus/lessons/round-50.md`.
- Build `97c864be` (5 files, +238/−53: `tools/append-only-audit.py`, `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, `corpus/SOURCES.md` rows S496–S498, the freeze-time check receipt). Build-fix `3d42897b`: the S498 row quoted the spec's own backtick characters (`` (`) ``) beside a second backticked fragment, so the row carried an odd tick count and `tools/sources-append-only.py` ended it early at `97c864be` (`error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)`, exit 2); with the fragment and the stray tick dropped the guard reads `added S496 (allowed)`/`S497`/`S498` and `no append-only violations`, exit 0 (re-run on a clone at `3d42897b` and at the battery tip). Wave spec `6f3bd322`: one v2 wave `kama-r50-w1` (attack and frontier together), 66 seats, `w1/validate.out` the validator's normalised spec with `w1/validate.stderr` empty; roles executor 22, reviewer 10, scribe 10, critic 6, connector 5, mutation-tester 4, scout 4, sentinel 3, revenger 1, simplifier 1. Build regression battery at `3b79eadd` (`.ufo/waves/round-50/measured/`, each receipt carrying its `tip=` line, not the measurement): capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; `append-only-audit` on the lane exit 0 (`events=5 regressed=0 vanished=0 ungraded_lines=89`); selftests `AOA_SELFTEST pass=36 fail=0`, `KLR_SELFTEST pass=23 fail=0`, live `selftest: ok`, `check-receipt` `16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected`; `digest-ledger` `unknown=0`; `planned-pointer-check` `met=True`. The battery's non-green legs, integration-owned and itemised in the round report: gate `registered 44 unregistered 2 defective 0` (exit 1, the two round-50 counters not yet in SKILL.md — the known item), `round41-scorecard-reconcile` and `round42-selfdesc-reconcile` `mismatches=1` each (the head calibration run line expects `35` `corpus/lessons/*verifier-spotcheck.md` blobs while the tree holds 36), `round43-registry-audit` `mismatches=4` (the same two unregistered counters, the documented-vs-run gate selftest, and the same 35/36 spot count), `hexrun-census` `unknown=1` (exit 1; the run `f8cdb853aaff29393faeb0b6d4c2a2296778b698`, which is the round-49 report commit in the **fleet** repository, cited at `corpus/lessons/round-49-verifier-spotcheck.md:21` — not a lane object), and `sources-append-only` exit 2 at `97c864be`, fixed at `3d42897b`. `measure.sh`'s last three legs (`r48c2`, `r49c1`, `r49c2`) have no receipt in `.ufo/waves/round-50/measured/`, so the round-48 and round-49 claim counters are not observed at the battery tip.
- Routed defects: r49-R1 and r49-R2 to C1 (pid join, environment, mapped model, parent-death teardown); r49-R3 to C2 (birth-DAG origin, fence-aware sections, CRLF keys, the arithmetic invariant, the counter's own per-event count); r49-R4 (mutation coverage: C1 counter 11/20, live/replay 10/23, C2 counter 16/49, v4 tool 8/29) to the wave's four mutation seats (M1Ctr, M2Live, M3Tool, M4Ctr), no claim; r49-R5 carried and not claimed (sub-20-line deletions unwatched, the b11909 prerelease cliff, the b11906 ledger population); r49-R6 operator-side (the prompt's §6 route map still quotes critic `@m_flash`; the live map routes `@m_kfc`).

## Round 51 — the replay's server is the file the replay extracted; every append-only deletion graded, each loss restored or named (2026-10-27)

- **C1 operability 8→8 (sourced on S499, Linux proc_pid_exe(5)).** Motivating evidence: the round-50 outside closure's R6 (`corpus/lessons/round-50-verifier-spotcheck.md:119`): seat J4Decoy's replay exec'd the host's own b11909 install and met the round-50 counter, because the exe digest says which bytes run, not which file. The live tool now records `server_exe` (the running image opened through `/proc/<pid>/exe`: dev, inode, digest); the replay accepts a rerun only when that image is its own extracted member (held open from before exec, one link) and records it as `own_server`. Counter `tools/round51-replay-exe-audit.py`; base `bind=1 own=0 teardown=1 newrow=0 met=False`.
- **C2 calibration 7→7 (every deletion graded, the A-row rule as declared, every loss named).** Motivating evidence: the round-50 closure's R6 (`:120`: the sub-20 threshold hid 97 events, among them the real `LOG.md` loss at `ed135b3c`), `considerthese/2026-10-26.md` proposal 1, and SCORECARD §Planned (round 51) item 1. `tools/append-only-audit.py` v6 grades every deletion (threshold 1: 106 events where v5 saw 5), permits A-row status/recheck/used-by edits (58 lines), and reads `registry/append-only-disclosures.tsv`, which names the 166 graded lines gone at the build; a bad row exits 1, and a ledger read from the revision discloses only commits before its own introduction. Counter `tools/round51-append-audit-v6-check.py`; base `fixture=0 lane=0 met=False`.
- **The `ed135b3c` loss, recorded here as a correction entry (not restored).** That commit (`Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"`) removed five lines of this file — the 2026-10-13 craft-hours ledger entry, operator canon withdrawn fleet-wide by a whole-commit revert (seat Rev1Loss, `.ufo/waves/round-51/a2w1/out/Rev1Loss.md`). Restoring a withdrawn bar would restate a retracted rule; the five lines are disclosed as `revert` rows in `registry/append-only-disclosures.tsv`.
- Freeze `804bde75`; build `b6bed925`; build-fix `73bf2a7a` (the S499 build restored the blank separator `97c864be` had removed, so its ledger row became an over-count — the tool's own rule caught it); build-fix 2 `138af25b` (digest-ledger leaves the disclosure ledger's line keys out of scope); wave `a2w1` (66 seats, spec `4eca4892`); integration and measurement: SCORECARD §Round 51 and §Round-51 measured results.
- Re-verification (freshness, no claim): S496–S499 re-opened live by seat Sc1Exe — S499 verbatim at §DESCRIPTION (man-pages 6.19, 2026-02-08); S498's `teaches` quote still drops the spec's two parenthesised fence characters (round-50 R5; erratum in `corpus/lessons/round-51.md`). llama.cpp upstream at b11913 while b11909 stays a prerelease (seat Sc4Watch); the pinned model object still resolves.
- Routed defects: r50-R1 (report row count 236 → 239, not 237 → 240) and r50-R4 (Gate reject 2 wording) and r50-R5 (S498 elision) → errata in `corpus/lessons/round-51.md`; r50-R2 → the regression receipts are committed at the round-51 measured commit (`.ufo/waves/round-51/measured/*.out`, each with its `tip=` line); r50-R3 → the calibration row re-anchored (37 spot-checks, latest closure round 50) and the depth row re-anchored with `evidence re-anchored round 51`; r50-R6 → C1 (J4Decoy) and C2 (sub-20 threshold), the rest carried; r50-R7 (route map) → seat Sen4Policy recorded the live map and its mtime at dispatch. The two `hexrun-census` unknowns carried since round 49 (fleet report commits `f8cdb853`, `9e38a361` cited by the round-49/50 spot-checks) are classified `upstream` with evidence files (`registry/hexrun-ledger.tsv`, `.ufo/waves/round-51/hexrun-evidence/`; seat X4Hexrun).
- Lesson: `corpus/lessons/round-51.md`.

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `ed135b3cb869` (Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"):

`````text
## 2026-10-13 — HOURS.md ledger opened
- Operator seed per PROTOCOL.md §Craft-hours: shonen→shokunin now requires
  ≥10,000 verified craft-hours AND the SHONEN gate. Ledger starts at 0;
  instrumented rounds accrue collective in-domain lane-minutes.
- Evidence: fleet commit; PROTOCOL.md §Craft-hours.
`````

Deleted by `47f3aedd6fa3` (round-4: audit corrections — lane-root-resolvable pointers; kotoba index row + tracked_files pin refresh; kama line ref; kasegi census regeneration):

`````text
`.ufo/waves/shokunin12h-20261014-p1-repair/members/`.
`````

Deleted by `f4066979096e` (round-26: LOG candidate count corrected; wave-1 final seat outputs):

`````text
(12/14); A1 closed it before data (0/14). Wave 1 (36 seats) found 58
candidates; 17 registered, the rest rejected or held back with reasons in
`corpus/lessons/round-26.md` §Gate.
`````

Deleted by `fd48f9a3b7ca` (round-26: falsify-wave corrections (SKILL row prose and header, lesson Gate and Mistakes incl. post-data shortcut break, SCORECARD/LOG calibration fixes, no depth promotion), snapshot files fit.cpp/llama-kv-cache.cpp/README.md, wave-2 evidence):

`````text
**Claim C1 (depth).** Before: SKILL.md held no live error signature for the
b11755 runtime; the counter `python3 .ufo/waves/round-26/count-c1.py` printed
scout listed 8 more, 3 of them not found by an executor; 17 registered, the
sample from ports that are now dead.
42 late paths committed (a4a159c3), KQ36 qualification, round-25 erratum,
`````

Deleted by `9cb3abae9d48` (round-29 attempt 2: VerifyLogFreshness late relay — stale qualifier fix, late-seat record in lesson):

`````text
SELFTEST PASS aggregate line, exit 0 (working-tree tool, seat-unique /tmp scratch);
`````

Deleted by `ce41bae692c8` (round-38: measurement receipts (c1/c2/c3 after.out) and scorecard/log measurement values):

`````text
Three declared claims, frozen in `.ufo/waves/round-38/preregistration.json` at `41e149ceee28b24596b5d8567a0ccf43ebbc6d50` before any seat scored, measured on committed bytes at `{{MEASURED_COMMIT}}`. Base `2a4a97dc890fe393035986c951797c5d65b6cc69`.
C1 (calibration 7 → 7) corrects the R36-D2 third sub-fact by append in `corpus/lessons/round-38.md`. Round 37 froze only R36-D2A and R36-D2B; the third sub-fact appeared only in the `## Mistakes` evidence cell of `round-37.md`, so the wrong range stood (round-37 verifier spot-check §6 item 4). The correction row R36-D2C names the five staged rows (S332, S336, S337, S338, S339 at `SOURCES.append.md` lines 9, 13, 14, 15, 16) instead of the wrong range. Counter: `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) at base → `{{C1_AFTER_LINE}}` (exit {{C1_AFTER_EXIT}}). The r37 lesson blob and the r37 fleet report blob are unchanged.
C2 (coverage 9 → 9) adds `corpus/knowledge/sglang-docs-version-pinning.md` and `corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md` to the coverage map. The published SGLang docs pages carry no version marker; their sources are contained unchanged in release tag v0.5.22. Counter: `named 0 files_exist 0 cited_new 0 met False` (exit 1) at base → `{{C2_AFTER_LINE}}` (exit {{C2_AFTER_EXIT}}). Sources S352 and S353 (the v0.5.22 raw `.mdx` pages) and S472 (the lane's `git ls-remote --tags` row, first id free in both the lane registry and the staged package) are appended. Staged S360 is rejected: the GitHub REST `/tags` endpoint returned HTTP 403 (rate limit) on this host; the lane's ls-remote receipt carries the tag inventory instead (exit 0, 166 tags, `refs/tags/v0.5.22` peeling to commit `baa9befa`).
C3 (operability 8 → 8) closes the inherited round-37 evidence gaps the verifier routed (§6 items 1–3). Commit `2f780765` lands `tools/round37-statement-audit.py` and `tools/round37-coverage-audit.py`, which round 37 cited but never committed, together with the 37th seat report `CriticEntries.md` and `seat-exit-codes.json`. Counter: `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1) → `{{C3_AFTER_LINE}}` (exit {{C3_AFTER_EXIT}}). The receipt parses to 37 members, all with `rc: null`; "Dead seats: none" closes as report presence, not exit status. The rest of the uncommitted round-37 tree (29 scratch files) was not copied; named in the report.
`````

Deleted by `2c0181074050` (round-42: integrate wave-1 — entry and Gate corrections, ledger evidence and tool hardening, SIGTERM cleanup, Mistakes, wave findings, 62 seat reports):

`````text
- **C1 calibration 7→7.** Round 41's counter covered only the `## Axes` table; seat R41A10 itemised the surfaces around it that the tree contradicts. At base `0b606b03`, `tools/round42-selfdesc-reconcile.py` reads `mismatches=40 met=False` (banner 4, Planned 3, Retired 4, Saturation 3, head Capabilities 4, README 11, PROVINCE 5, relevance needles 6). The head sections were re-derived from the tree and the round-5 text moved verbatim under §Historical head sections; README names every top-level entry; PROVINCE names every instrument the capability list cites (closing round-41 closure item 2, `pin-watch` absent from Owns); each axis row carries one axis-specific run fact (round-41 closure item 1).
`````

Deleted by `8bee4e56a995` (round-43: LOG wording):

`````text
- Freeze `895793e0` (preregistration, three counters, base and nine shortcut/freeze controls). The committed `freeze.c*.out` receipts are byte copies of the base receipts; the counters measured at the real freeze commit are `controls/freeze-measured.c*.out` (C1 reads `mismatches=45` there). Census at start: 220 rows, mirror and fleet-root validate exit 0, 93 W04.
- Frontier: `considerthese/2026-10-25.md` proposal 3 implemented as `registry/staged-refusals.tsv` (73 refused items, 6 stale flips, one quarantine row the registry contradicts); KQ54-KQ57 added to `corpus/QUALITY.md`; six Mistakes rows in the lesson.
`````

## Round 52 — the replay's server runs from a sealed anonymous memfd; every line the A-corr files lost is restored by append (2026-10-27)

- **C1 operability 8→8 (sourced on S500, Linux memfd_create(2); S501 F_GET_SEALS(2const), S502 kernel mfd_noexec at integration).** Motivating evidence: the round-51 outside closure's D5 (`corpus/lessons/round-51-verifier-spotcheck.md:138`–`:143`): a byte-identical copy at the member path met the round-51 counter (seat J3CopyDecoy), a hardlink met its own leg (J4Hardlink), and rename-over provenance was an `[INFERENCE]`; SCORECARD §Planned (round 52) item 1. The replay now copies the verified member from the archive's tar stream into a memfd, seals it (seals 15) and hands it to the live tool (`--server-fd`), which execs the server from that descriptor; the replay refuses a rerun whose `server_exe` is not its own sealed, linkless `/memfd:` image. Counter `tools/round52-replay-memfd-audit.py`; base `bind=1 sealed=0 teardown=1 newrow=0 met=False`.
- **C2 calibration 7→7 (the A-corr files hold every line they declared append-only).** Motivating evidence: SCORECARD §Planned (round 52) item 2 and the closure's D5 C2 part (region-restricted files only bound-checked; the ledger cutoff untested). The 155 graded lines the A-corr files lost in place are re-appended verbatim in 18 files, fenced, one block per deleting commit, and their ledger rows removed; the ledger keeps the 10 A/A-row lines (7 `corpus/SOURCES.md`, 3 `registry/report-landing-errata.tsv`) whose re-append would duplicate a registry id or an errata key. Counter `tools/round52-append-restore-check.py`; base `fixture=1 lane=0 corr_lost=151 row_lost=10 disclosed=165 met=False`.
- **The `ed135b3c` loss is restored this round, reversing round 51's choice to disclose it.** The five lines are the 2026-10-13 craft-hours entry that `Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"` withdrew. They sit in this file's `## Restored lines (round 52)` block as retracted canon kept as history; they bind nothing. Reason and flip condition: `corpus/lessons/round-52.md` §Gate (continued).
- Freeze `8551ba7f` (`frozen_at_utc` 04:42:00Z written from `date -u`, commit 04:42:07Z; `.ufo/waves/round-52/freeze/prereg-time-check.out` → `RESULT pass`); build `5dacf2c7`; wave `kama-r52-w1` (70 seats, spec `34d82600`); integration and measurement: SCORECARD §Round 52 and the round-52 measured-results subsection.
- Integration hardening from the wave: `tests/llamacpp-live/check-receipt.py` admits `LD_LIBRARY_PATH` only in fd mode (seat V2Review: the build's fd-mode receipts were INVALID under the committed checker); the replay passes MFD_EXEC (S502, seat S4NoExec), re-hashes the sealed bytes, and five selftest cases kill seat M2Replay's survivors (`KLR_SELFTEST pass=36`); the live tool's selftest drives `sealed_fd()` (seat X5Selftest) and names an F_SEAL_EXEC memfd and a launch errno (seat Sen1Exec).
- Re-verification (freshness, no claim): S500 re-opened live by seat S1Source; S501 and S502 re-opened by the L1 (2026-10-27T05:16:59Z; text copies under `.ufo/waves/round-52/c1/`); llama.cpp upstream at b11913 while b11909 stays a prerelease, and the pinned model object still resolves (`x-repo-commit 499bc882…`, seat Sc2Watch).
- Routed defects (round-51 closure): D1 → `X7Regen.md` restored to its committed bytes (late rewrite kept beside it) and this report filed after WAVE-DONE; D2, D3, D4, D6, D7 → `corpus/lessons/round-52.md` §Errata (D3's pointer receipt `.ufo/waves/round-52/d3/pointer-1ab1de39.out`, `met=True`); D5 → the two claims, the rest carried in SCORECARD §Round 52 "What `met=True` does not show".
- Lesson: `corpus/lessons/round-52.md`.

## Round 53 — executable library bytes checked in process memory; cited-path misses disclosed (2026-10-27)

- **C1 operability 8→8 (S506 proc_pid_mem(5); S507 ptrace/Yama scope 1).** Motivating evidence: round-52 closure R2 (`corpus/lessons/round-52-verifier-spotcheck.md:135`): the launcher image was sealed, but `libllama-server-impl.so` and `libggml*` still loaded by path. At build `c22602bd`, the live tool records each executable file mapping; the replay hashes mapped archive members, and the frozen counter independently reads 8 executable library ranges from `/proc/<pid>/mem` per run, comparing with its own archive download. Base control `code=0`, build `code=1`, three of three witnessed replays. J1/J2/J3 show swap/forged-record controls are caught. Limits and the root-owned host-library bypass are in SCORECARD §Round 53.
- **C2 calibration 7→7 (counter output met, claim not admitted).** Motivating evidence: round-52 closure R3/R4 and W3Mistakes' prototype left 50 "pre-existing" citation misses unexamined. At base the frozen counter counts 16 unresolved; at build it counts 14 and reports `undisclosed=0`, `bad=0`, `stale=0`, `dropped=0`. The `J12Hide` control removes SKILL.md citations and their ledger rows while the frozen counter still returns `met=True`; `J11BadFixed` shows its upstream class accepts HTTP 200 without matching bytes. The claim's adversarial kill rule therefore fails; the counter output is recorded but C2 is not admitted. Its full boundary and the fixture-environment risk (Sen4Fixture) are recorded in SCORECARD and this lesson.
- Round-52 closure R1 → S509 appends the corrected b11909 anchor; S505 stands as filed. R4 → X9Immut delivered a 13/13 selftested tool and found 8 rewritten seat reports plus one restored in rounds 46–52, but it was not installed before this user-directed wrap. Operator question about restored `ed135b3c` history was filed to L0; the first L1 wording was corrected twice append-only.
- Freeze `d01b2b6d`; build `c22602bd`; wave `kama-r53-w1`, policy v2, 66 seats (executor 23, mutation-tester 6, reviewer 7, critic 8, sentinel 4, scout 8, scribe 5, connector 3, simplifier 1, revenger 1; attack share 21/66 = 31.8%). The latest user instruction required wrapping before the orchestrator's `WAVE-DONE`; the wave's final settled statuses/dead-seat tally were therefore unavailable. No settlement is claimed. Measured outputs: `.ufo/waves/round-53/measured/{c1-build,c2-build}.out`; base controls in `controls/`.
- Round-52 outside closure R1–R4, the ed135b3c operator question, C2 falsification, and the outstanding seat-report tool are in `corpus/lessons/round-53.md` §Errata/Mistakes. Sources census start `exit=0`; end receipt is in `.ufo/waves/round-53/census/end.out`.
- Re-verification (freshness, no claim): S506–S509 were opened and copied under `.ufo/waves/round-53/c1/`; seat S1Source confirms the three man-page quotes, seat S2Anchor confirms S509 line 491. Seat Sc2Watch rechecked b11909 (still prerelease, three releases behind b11913) and both pinned downloads.
- Lesson: `corpus/lessons/round-53.md`.
- Round 55 (2026-10-27, attempt 1): answers the round-54 wrap-up (outside closure `corpus/lessons/round-54-verifier-spotcheck.md`, rejected-honest-stop; routed defects 1-5). Froze the two round-54 counters with preregistration and red base controls committed before data: C1 base `newrow=0 met=False` (exit 1), C2 base `dropped=1 met=False` (exit 1) - C2's BASE deliberately stays at the round-53 tip after the pre-freeze do-nothing catch (a same-tip base let the base control pass; reverted before data, recorded in the lesson). Build measurements green at `9c60eae6` (C1 `met=True` exit 0; C2 `fixture=1 lane=1 scenarios=15/15 met=True` exit 0). Kill battery: control green; m-ldpreload kills envnames; m-text-flip kills code; m-member-flip kills rehash; m-ldaudit-foreign is a vector analysis (met=True by design: glibc ignores a non-audit LD_AUDIT DSO - L1Probe/Rev1 grounded; the hostlibs live kill is root-gated). Disclosed process defect: the battery roster diverged from the frozen preregistration's named mutants (bring-up redesign; recorded in the lesson; the frozen kill rule fires on its literal text and the closure rules). One v2 wave `kama-r55-w1`, 64 seats, 44 settled at this commit. S511 opened (git-config(1) GIT_CONFIG_COUNT; cited by C1's newrow leg and both counters' clean_env); S510 used-by re-pointed old->new to `corpus/lessons/round-55.md` (round-start census exit 1 E11 -> round-end exit 0); `superseded` ledger class rows the round-52->round-53 re-point. Integration repairs from wave seats: SCORECARD calibration run-fact 40->41 and the hexrun-ledger row for the round-54 closure's fleet commit `e2e2d10f` (both inherited reds from base `3a600d2f`, fixes per seat X8Regression). New disclosed limits: ptrace_scope>1 exit-class (Sen2), LD_AUDIT not in BAD_ENV + host count unasserted (Rev1 D3/D4), git-archive export-ignore poisoning (Rev2), inherited user gitconfig reaches the counters (Sec1). Lesson `corpus/lessons/round-55.md`; receipts under `.ufo/waves/round-55/`.

## Round 56 — LD_AUDIT env-name leg and preregistered battery roster (2026-10-27)

- **C1 operability 8→8.** Round-55 outside closure routed the omitted `LD_AUDIT` name in `BAD_ENV` (defect 1). Base/old counter at `e10b6d39`: `ld_audit=missed`, exit 0. At implementation tip `b9d5a091`, the round-56 counter: `ld_audit=detected`, exit 0; one-line `BAD_ENV` deletion mutant: observed `missed`, exit 0 under the mutant observation expectation, and `missed`, exit 1 when asserted against the frozen positive target `detected`. Exact field comparator selftest rejects `expected=detected field=undetected` (`accepted=False`, exit 0). Counting command `python3 tools/round56-env-leg-battery.py`; receipts under `.ufo/waves/round-56/measured/`.
- **C2 calibration 7→7, not admitted (do-nothing target is reachable).** Round-55 closure routed preregistration/battery roster drift (defect 1). Base `e10b6d39`: `present=0 roster_match=0 met=False`, exit 1. At `b9d5a091`: `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0. But a scratch no-op harness that carries the exact ROSTER and executes no battery entry also prints `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0 (`.ufo/waves/round-56/measured/c2-noop-control.out`). The frozen checker grades only the declarative ROSTER, not the executed call list; the do-nothing reaches the target, invalidating the calibration move per §9. The frozen checker hash/predicate were not changed after data.
- Freeze `efc6b3ec`; measured implementation commit `b9d5a091`; v2 wave `kama-r56-w1`, 64 seats, all 64 settled, no dead seats. Role mix: reviewer 16, critic 8, mutation-tester 8, executor 8, scout 8, sentinel 4, revenger 4, scribe 4, connector 2, simplifier 2. Attack roles (reviewer+critic+mutation-tester+sentinel+revenger) 40/64; the strict falsification classification (reviewer+critic+mutation-tester) 32/64=50%; connector count 2. The planner seat was held by the L1; frozen topology rejected a planner role.
- Round-55 routed defects addressed: roster/freeze alignment; stale lesson claim corrected append-only in `corpus/lessons/round-56.md` (defect 2); battery receipts record exit codes and exact fields, including a comparator negative control (defects 4/5); S510/S511 revision-anchor omissions receive append-only superseding rows S514/S515 (defect 6); SCORECARD depth/calibration labels re-anchored, including the 42-spotcheck count and round-55 admitted closure (defect 10); 305 inherited late round-55 seat-output/result entries swept into `.ufo/waves/round-55/` without deletion (defect 7). Defect 9's attack classification is recorded above and in the report. The broader host-library package-byte provenance/count, fully config-hermetic Git environment, and attribute-free archive-extraction routes were not claimed or closed; carried explicitly to round 57. KQ98 remains a proposal pending outside closure agreement.
- Source curation: S512 admitted from `rtld-audit(7)`; S513 opened then rejected as broader/overlapping; S514/S515 append-only revision-anchor corrections supersede S510/S511. S512 `used-by` old→new is logged in lesson Gate. Before census exit 0, 252 rows; after census exit 0, 256 rows; full outputs `.ufo/waves/round-56/census/{start,end}.out`. Assimilation: none; considerthese proposal 4 remains pending.
- Seat integrity observation: S01WriteScope observed only metadata-side effects from lane-cwd reads (`.git/index` stat-cache refresh and one jj snapshot op); its attribution found no content/ref changes. A seat reported temporary `/tmp` artifacts; details and limits are in `.ufo/waves/round-56/w1/out/S01WriteScope.md`. No tool installs.
- Lesson: `corpus/lessons/round-56.md`. Round-55 late outputs were preserved and committed; no prior lane-authored round-56 leftovers were inherited.

## Round 57 — counter control and calibration count (2026-10-27)

- C1 operability: `tools/round56-prereg-check.py` now binds preregistered roster members to battery call sites; round-56 closure documented the passing no-op roster control (`corpus/lessons/round-56-verifier-spotcheck.md:14`).
- C2 calibration 7→7: SCORECARD's verifier-spotcheck count corrected from 42 to the observed 43; the re-derivation command counts `corpus/lessons/*verifier-spotcheck.md`.
- Pre-data controls and frozen predicates: `.ufo/waves/round-57/controls/`; round-56 outside defect lesson: `corpus/lessons/round-57.md`.
- Opened S516 from the round-56 battery's committed call sites; append-only row added and cited by C1/lesson. S515 was also reopened from its authoritative Git manual; no existing row cell changed.
- The round-56 S513 rejection disagreement remains unresolved; this round made no source-admission decision and claims no discernment improvement (`corpus/lessons/round-57.md`).
- Post-filing seat falsification: R57Item05CounterSelftest finds two AST-only no-op mutants still meet C1; the operability claim is not verified. Evidence `.ufo/waves/round-57/measured/R57Item05CounterSelftest/`; recorded append-only in lesson §Mistakes.
- WAVE-DONE: all 64 seats settled (62 complete, 1 done, 1 closed, 0 dead); role mix is in the validated dispatch and seat outputs/results under `.ufo/waves/round-57/`. Integration commit `46d1fde97cd24c2ee1dd3338ee52071fc0bec98e`. R04CounterSemantics additionally found equal-number duplicate canonical headings select the first match; this is a counter limitation, not a change to C2's frozen count target.

## Round 58 — execution-bound battery checker and closure-pointer binding (2026-10-27)

- C1 operability 8→8 (sourced on S517): `tools/round58-battery-exec-check.py` runs the committed round-56 battery as `__main__` under a hermetic harness with a `sys.setprofile` hook and requires every preregistered roster label to reach a `run` frame whose recorded subprocess call carries `--counter` and the label's preregistered `--expect`. Frozen counter `tools/round58-c1-counter.py` over `tests/round58-battery-variants/` (1 genuine, 3 behaviour-preserving rewrites, 11 no-ops). Base round-57 checker: `genuine=1/1 benign=1/3 noop_rejected=1/11 met=False` (`.ufo/waves/round-58/controls/c1-base-r57-checker.out`). Do-nothing checkers (always-accept, always-reject, hash-only) fail the predicate (`controls/c1-ctl-*.out`).
- C2 calibration 7→7: SCORECARD calibration row now names `corpus/lessons/round-57-verifier-spotcheck.md (rejected-honest-stop)` and `including round 57`; the round-56 `(admitted)` pointer was false against the fleet MANIFEST. Frozen counter `tools/round58-c2-counter.py` base `mismatches=4` (`controls/c2-base.out`); claim-deleted and verdict-flipped controls fail it.
- Freeze `dcd69473`, controls `cb1ef102`, both before any seat result. Post-freeze checker hardening from seat findings (expect-binding, one-shot result nonce, scrubbed child environment, crashed battery is not met) was re-scored with the unchanged frozen counter: still `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0`.
- Opened S517 (Python `sys.setprofile`) and S518 (ld.so(8) LD_AUDIT secure-execution rule; claim-scoped supersession of S513). KQ98 added to `corpus/QUALITY.md` from the S513 disagreement (lesson `corpus/lessons/round-58.md`).
- Seat survivors outside the 11 enumerated no-ops are limits, not credit: a thread-issued leg, a leg that ignores its result, a decoy `--counter`, an unwrapped `os.posix_spawn`, PyPy portability (`.ufo/waves/round-58/w1/out/`).
- Misroot: a seat that ran the real battery overwrote four round-56 receipts under `.ufo/waves/round-56/measured/`; restored byte-exact from the branch before commit.
- WAVE-DONE: all 72 seats settled, 0 dead (v2 wave `kama-r58-w1`: executor 12, reviewer 10, critic 10, mutation-tester 10, scout 10, scribe 8, connector 3, sentinel 3, revenger 3, simplifier 3; attack roles reviewer+critic+mutation-tester = 30). Seat evidence `.ufo/waves/round-58/w1/out/`, results `w1-results.json`. No seat falsified a frozen predicate; limits and post-freeze checker hardening are in `corpus/lessons/round-58.md` §Mistakes. Added `corpus/knowledge/battery-execution-evidence.md` (S517) and a README coverage note; round-end census exit 0, 259 rows.

## Round 59 — outcome-bound battery probe and dynamic closure-row counter (2026-10-27)

- Claims frozen at `.ufo/waves/round-59/controls/freeze.txt` (`5d957d24`), against base `8f7f58cd`: C1 operability 8→8 (sourced on S517); C2 calibration 7→7 (lowest assigned axis).
- C1's measured finite set changed from the prior r58 checker (`13/16` no-ops rejected) to the r59 checker (`16/16`; genuine 1/1, benign 3/3, zero errors) at `aca8d006`. Wave R04 then falsified the exact frozen predicate: a one-call `python3 other-script --counter ...` battery was accepted; R15 showed a fixture-name-keyed checker also passes. C1 is not verified and earns no score change (`.ufo/waves/round-59/w1/out/R04DecoyArgv.md`, `R15CounterGaming.md`).
- C2 changed the calibration row from a typed count/pinned revision to a dynamic `--fleet-ref` command. The counter measured `3 mismatches` at base → `0` at edited row; K05's static assertion and M12's eight clause-deletion mutants still met, and no independent S517/S518 spot-check exists. C2 is not verified (`.ufo/waves/round-59/w1/out/K05C2Noop.md`, `M12C2Clauses.md`); scores stay 8/7.
- `SOURCES.md` remains 259 rows, exit 0; S517 `used-by` changed old→new to include this lesson. S517/S518/S513 and all seven quarantine ids were reopened; no new source row or knowledge entry was admitted. Assimilation: none; `considerthese/2026-10-26.md` proposal 3 does not fit the frozen claims.
- KQ99 appended to `corpus/QUALITY.md` from the observed runner-decoy/name-oracle mistake; it is a future admission bar, not a repair or retroactive pass. Lesson: `corpus/lessons/round-59.md`.
- WAVE-DONE: one policy-v2 wave, 64 entries; roles: reviewer 16, critic 14, mutation-tester 12, executor 12, scout 6, connector 2, scribe 2; 42/64 attack roles. Results `.ufo/waves/round-59/w1/w1-results.json`; 64 entries/null notes, with M08AlwaysReject's unfinished output and no report artifact (incomplete/unverifiable; no dead-seat count asserted).
- Changes landed through `jj-lane.sh`: freeze `5d957d24`, instruments/row `494c1657`, checker correction `2c7443ab` and `aca8d006`, pre-data controls `114fdf78`, dispatch `4a541190`, wave evidence `22b5916c`; this entry and final round record land in the integration commit.

- Final post-integration remeasure at lane `ad7f1d6239c7fecf83a9a7a69b0367ad26a894fa`, fleet `a41c6644b749e8b1289be73d10706217fa070357`: C1 `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` (exit 0), C2 `rows=44 mismatches=0 met=True` (exit 0), and `tools/round42-selfdesc-reconcile.py` `mismatches=0 met=True` (exit 0). These reproduce the counters; the R04/K05/M12 falsifications still make both frozen claims unverified. Receipts `.ufo/waves/round-59/measured/`.

## Round 60 — live Ollama trial; frozen claim predicates falsified (2026-10-27)

- Froze C1 operability 8→8 (live Ollama lifecycle capability, source S519) and C2 calibration 7→7 (14-line self-assessment population) before data at `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`; base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`. Base controls: C1 tool-absent `met=False`; C2 empty registry `covered=0/14 met=False` (`.ufo/waves/round-60/controls/`).
- Built `tools/kama-ollama-live.py`, its v0.40.11/archive/model pin, and counters `tools/round60-c1-counter.py` / `tools/round60-c2-counter.py`; initial C1 counter at freeze tip reports `live_ok=1/1`, 7/7 controls rejected, `met=True`. Committed receipt `MODEL_OK`, nonce `b61c98ad5747`, with empty `/v1/models data:null`, list-vs-single id difference; evidence `.ufo/waves/round-60/live/receipt.json`. This measured green is falsified, not an admitted capability.
- W1: one v1 wave, 49 seats (executor 19, reviewer 10, scribe 6, critic 5, mutation-tester 4, connector 3, scout 1, sentinel 1), 46 report directories; all 49 result rows have null status/note, so no dead-seat count inferred. W2: one v1 wave, 32 seats (reviewer 16, critic 8, mutation-tester 4, scout 2, connector 2), 31 output dirs; all 32 settled, no structured dead status. Specs/dispatch/results committed under `.ufo/waves/round-60/{w1,w2}/`.
- W1 A09/F01 and W2 F05 demonstrate a canned `run_evidence()` stub is accepted by C1 verifier; W1 A09/F01 also demonstrate an external SIGTERM after final server contact can reach accepted MODEL_OK; W1 A03 demonstrates SIGKILL of the tool leaves the child server alive; W1/W2 F02 show `/api/show` is ungraded. W1 K01 plus W2 F17/F19 demonstrate C2 accepts 5 unrelated capture-literal predicates + 9 boilerplate not-observable rows; F21 found excessive predicate cost and uncaught RecursionError. Claims C1 and C2 are not verified; scores stay operability 8, calibration 7; no capability entered.
- Frontier: S519/S520/S521/S523 mined tier A, S524 rejected for same URL/scope as S010; S513 `used-by` old `—` → `corpus/lessons/round-60.md`, status/recheck unchanged. Census validate exit 0 start 259 → end 264; receipts `.ufo/waves/round-60/census/{start,end}.out` and `.exit`. New knowledge: `corpus/knowledge/ollama-live-lifecycle.md`; lesson records the S513/S518 closure disagreement and unverified claims. Assimilation: none.
- Updated `SKILL.md`, `PROVINCE.md`, `corpus/README.md`, SCORECARD and added L0 question about extending the pending lane-owned ephemeral child exception to Ollama. No tools installed/updated by the L1 beyond the official Ollama v0.40.11 archive extracted into `~/.local/opt/ollama-v0.40.11`; it was downloaded to scratch and the archive removed. `pacman` was not used.
- Inherited untracked lane state: `.ufo/scopes/kama-r57-w1/swarm-registry.json` remains untouched; the stale generated nested fixture tree `.ufo/waves/round-57/ClaimFalsifier/09/fixtures/` was removed after spot-check review. No other lane leftovers were modified.

## Round 61 — v2 live Ollama hold-verified lifecycle + bounded claim-registry evaluator (2026-10-28)

- Froze C1 operability (fresh-nonce hold-verified v2 live run + 16/16 controls) and C2 calibration (18-line frozen population covered by sensitive bound registry rows + 9/9 controls) before data; base `a107b75f3650981d191d73fde73987415e292e14` (round-60 tip). Base controls committed at `.ufo/waves/round-61/controls/`: C1 `tool_present=0` exit 1; C2 `header` error exit 1 — a do-nothing tip reaches neither predicate.
- Built `tools/kama-ollama-live.py` v2 (`--hold-dir` outside-verifier window, `PR_SET_PDEATHSIG` pdeathsig, graded `/api/show`, per-evidence replay records, `teardown.child_pre_dead`), `tools/round61-c1-counter.py` (re-contacts held child, re-runs classifier, re-hashes manifest+blob), and `tools/round61-c2-counter.py` (18-entry frozen manifest with verbatim 60-char prefixes, bounded evaluator: eq/ne/contains/regex/nonempty/isnull/hex64/int/same-as over a `key[lit=v]`/`[*]`/`[i]` path DSL; sensitivity by mutation; located-quote check; amendment ledger).
- Fresh v2 receipt `MODEL_OK` nonce `r61live01` port 47887 committed at `.ufo/waves/round-61/live/receipt.json`: outside verifier contact on `/api/version` + `/api/ps` during the hold window, `hold.released=true`, clean SIGTERM teardown. Registry `registry/ollama-live-claims-r61.tsv` 28 rows (17 bound + 11 notobs) evaluates `sensitive=17/17 contradicted=0 controls_rejected=9/9 met=True` in fixture at pre-commit test.
- W1: one v2 wave, 68 seats (executor 22, mutation-tester 14, reviewer 10, scribe 6, scout 6, connector 5, critic 4, sentinel 1; 31/68 attack-share roles). Spec/dispatch `.ufo/waves/round-61/w1/`; results land post-WAVE-DONE.
- Frontier: S525 (Ollama OpenAPI yaml) candidate-admitted for `/api/show`+`/api/ps` field semantics; census before exit 0; lesson `corpus/lessons/round-61.md` records Gate + Mistakes (r60 unrelated-predicate registry class). Assimilation: quarantine slice regenerated; merge package stays unadopted this round (verdicts in lesson).
- KQ101 added to `corpus/QUALITY.md` (manifest-triple + located-quote + flip-tested verdict bar).

## Round 62 — completion request plane + capability live-check audit (2026-10-28, attempt 2)

- Freeze `.ufo/waves/round-62/controls/freeze.txt` at `6c25a77e`, base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`, before tip measurements or wave seat evidence. Attempt 1 had authored uncommitted counter/tool drafts but died before freeze/report (`.ufo/watchdog.log` 2026-10-28T08:59:38-03:00); attempt 2 re-read and smoke-tested those drafts and froze the predicates unchanged from the counter docstrings.
- C1 operability 8→8: added `tools/kama-completion-live.py`, which grades one real POST `/v1/completions` on pinned llama.cpp b11755 (model SHA `270cba1b…`, server SHA `b6a31a8e…`), records body hashes/checks, requires a fresh outside nonce-bound contact during a hold, and tears down the owned child. Initial smoke: `REQUEST_OK`, all 16 checks true. Initial frozen-counter run exposed a None-dereference on a deliberately tampered body and a check-name mismatch (`hold` vs actual `hold_released`); both counter fixes are post-freeze instrumentation repairs, predicate unchanged. Red-before traceback `.ufo/waves/round-62/measured/c1-before-fix.txt`; corrected run `tools/round62-c1-counter.py --repo <repo> --tip <tip> --work <scratch>` → `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True` (exit 0, pre-wave measurement; final committed-tip remeasurement pending).
- C2 calibration 7→7 (not verified): added 12-row `registry/capability-claims-r62.tsv`, canonical SCORECARD list as of round 62 (12 capabilities), and frozen counter `tools/round62-c2-counter.py`, which executes all bound templates. Pre-wave run at `65d7cad0fce90e34de37527cde22e97b63b118bf`: `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False` (exit 1). Four computed mismatches mean the frozen predicate is not met; do not claim calibration credit. Separately, the sensitivity calculation replaces every occurrence of its pattern before checking for the same pattern, making `sensitive` tautologically true for nonempty patterns; this is a frozen-counter defect, not evidence of sensitivity. Report honest stop; freeze cannot be amended after data.
- Bound-run defects repaired: `tools/kama-live-replay.py --selftest --scratch <nonexistent-dir>` previously raised `FileNotFoundError`; now creates the scratch root and passes `KLR_SELFTEST pass=48 fail=0`. `tools/kama-context-capacity.py --only K1` refused with `host-not-idle-before-K1` after 120 s (exit 2); the frozen C2 template was changed to a 900-second wait before data, but the measured run still had four mismatches. This availability risk is recorded, not hidden.
- Sourced C1 on newly opened S526, the pinned b11755 server README §POST `/v1/completions`; quote “Given an input `prompt`, it returns the predicted completion.” at line 1316. Added `corpus/knowledge/completion-request-plane.md` distinguishing documented route scope from receipt-observed fields; added row S526 to `corpus/SOURCES.md`, citing both lesson and knowledge entry.
- `considerthese/2026-10-26.md` proposal 3 (“Keep a running count of counters that a shortcut can satisfy”) was opened and adopted as method for the C2 control matrix; this does not make its counter pass. Staged `merge/kama/` package remains deferred; r61's quarantine verdict was not re-adopted without hand-checking sources.
- New ledger classifications: 3 previously unknown SHA-256 digests in `registry/digest-ledger.tsv` (Ollama release archive unverifiable, installed binary external and re-hashed, server-computed model digest unverifiable); 9 fleet commit object ids classified upstream via `.ufo/waves/round-62/census/fleet-commit-evidence.json` and `registry/hexrun-ledger.tsv`. Attempt-1 census start receipt is `.ufo/waves/round-62/census/start.out` (exit 0; existing W04 duplicate-URL warnings and W01 used-by warning).
- Claim counters/results, wave and report still pending. No axis score changes or capability admission until non-author closure; C1 stays provisional pending WAVE-DONE; C2 is a frozen-predicate miss.
- Correction (same round, appended): `considerthese/2026-10-26.md` proposal 3 is **deferred**, not adopted: one C2 counter run is not the proposal's longitudinal per-round shortcut tally; see `corpus/lessons/round-62.md` §Gate for the flip condition. C1's final committed-tip measure at `dc5e1010cf2fb8168b7ecb0278a1452a8ed99504` is `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True` (exit 0; `.ufo/waves/round-62/measured/c1-final.out`). C2 remains unverified at its recorded pre-wave tip; the digest ledger was corrected after that run and now scans `unknown=0` at `a837c8f7`.
- Honest-stop correction: final C2 run at `e092f2b6940a77395a9182e22f23cd4d9b06afe0` still reports `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False` (exit 1; `.ufo/waves/round-62/measured/c2-final.out`); no calibration credit. At user stop, W1 was dispatched (64-seat v2, `.ufo/waves/round-62/w1/`) but WAVE-DONE/results handoff had not arrived; no seat conclusions or dead-seat count are claimed. Honest-stop report filed at `.ufo/reports/round-62/kama.md`.
