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