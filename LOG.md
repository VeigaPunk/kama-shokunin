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