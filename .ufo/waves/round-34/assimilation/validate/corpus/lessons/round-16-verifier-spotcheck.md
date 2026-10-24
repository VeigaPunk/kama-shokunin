# Round 16 — independent verifier spot-check

author: hyaku closure (non-author integrator, @m_opus)

Reviewed 2026-10-20 UTC by ClosureKamaR16-3. The hyaku orchestrator dispatched this closure; kama did not. Four read-only reviewer seats did bounded re-counts: C1Remeasure, C2Receipt, WaveCount and GateReopen. The integrator owns every ruling below. No lane-owned gate, harness, selftest, probe, `measure.py`, `stale-statements.py` or live tool was executed. This file records plain committed-byte measurements, public source re-opens, the required fleet census and read-only host inspections (`sha256sum`, `readlink`, `pgrep`, `ls`). No lane-authored file was edited. Tools installed or updated: none.

**Closure: status `ok`, admitted `true`.** C1 calibration verifies as **improved** (numeric 7 → 7). C2 operability capability `live-llamacpp-lifecycle` verifies as **improved** (numeric 8 → 8, capability row added). No owned axis is harmed. Admission covers two things only. First, the exact llama.cpp b11755 loading envelope on `GET /v1/models`. Second, one lane-owned, GET-only, ephemeral fixture run on an unregistered loopback port. It does not certify registered-consumer health or restoration, other engines, router or sleep modes, generation, timing or model quality. It does not ratify the PROVINCE fixture exception, which is pending L0.

## Dispatch and completion digest

Copied verbatim from the closure prompt. This committed digest, not the mutable watchdog line numbers, preserves the termination evidence:

```text
2026-10-20T10:14:08-03:00 launch kama round=16 pgid=11634 driver=hyaku-inline attempt=1
2026-10-20T11:16:57-03:00 complete kama round=16; hyaku-inline attempt=1
```

Report: fleet `.ufo/reports/round-16/kama.md`. Prompt: fleet `.ufo/prompts/kama-round-16.md`.
Start: `20e392ea683a36bc223eb7cb45897acfb45456a3`. Delivered: `ccc4bb31267f061c1d3cc4099eb9fb46ed48d004`. Measured implementation: `726f737a942f1606d66e032f1efbcbb6f689ccf1`.

## Step-1 conformance

```sh
git -C /home/vgpnk/Projects/shokunin log --format='%an %ae %H %ad' -- .ufo/reports/round-16/kama.md .ufo/prompts/kama-round-16.md
git -C <lane> log --format='%h %an <%ae> %s' 20e392e..refs/heads/master
for h in b8e485c 726f737 ccc4bb3 836b018 20e392e c6199a2; do git -C <lane> merge-base --is-ancestor $h refs/heads/master && echo "$h anc-ok"; done
/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/kama-shokunin
git -C <lane> status --porcelain
git -C <lane> ls-remote origin refs/heads/master
```

Observed results:

- **Report commit.** `kama-shokunin kama@shokunin.local 9ec9c524441282c396313054bb0afae312b105c5`, 11:16:30 -03:00, which is after the last lane commit `ccc4bb3` at 11:15:00 -03:00. The report therefore lands last. It was committed by the lane identity, and the same commit appends the L0 question.
- **Prompt commit.** The prompt was committed by kama in `6c4f0c29a2e9412175c75088c8d1ba66e6ad3046` at 10:14:06 -03:00.
- **Round commits.** The range contains `b8e485c`, `726f737` and `ccc4bb3`, all by `kama-shokunin <kama@shokunin.local>`, plus the operator's `836b018` (considerthese). The lane did not edit `836b018`.
- **Ancestry.** Every cited hash is an ancestor of `refs/heads/master`: `anc-ok` ×6.
- **Push state.** The helper reported `state branch=master local=ccc4bb3… remote=ccc4bb3… ahead=0 behind=0 head=attached tracked=0 untracked=0`, exit 0. Porcelain output was empty. `ls-remote` returned `ccc4bb31267f061c1d3cc4099eb9fb46ed48d004 refs/heads/master`.
- **Report contents.** The report is a real report, not a marker. It has work performed, evidence pointers, a landed-changes table tied to two `LOG.md` entries, Sources & frontier, Trend verdicts, and `## SHONEN` with exactly four `[~]` lines.
- **Prompt fidelity.** I rendered the fleet `templates/round-prompt.md` with the driver's substitution order: the `{{FLEET_ROOT}}/<{{LANE}}-repo>` form first, then `<{{LANE}}-repo>`, `{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}` and `{{AXES}}` = `operability + calibration (local model serving and endpoint health)` (`shokunin.conf:52`). `prompt.startswith(rendered.rstrip() + '\n')` returned **True** (140 template lines). The §6 hyaku addendum follows. It sets the 64–100 band per wave and ≤200 per round, maps the planner seat to L1, and carries the tooling and pacman pause.
- **SCORECARD.** `git diff 20e392e ccc4bb3 -- SCORECARD.md` is **88 additions / 0 deletions**. It is append-only, with no score change and one new capability row.
- **Other lane-owned deletions in the range.** `SHONEN.md` has one in-place extension of an existing `[~]` pointer line; no `[x]` was written. `PROVINCE.md` changes only end-of-file newline handling. `SKILL.md` changes one end-of-section line, which a new section follows. `SOURCES.md` has one in-place change: the S017 `used-by` cell, which the lesson logs.

### L2 waves (WaveCount, from committed `dispatch.json` / `completion-summary.json` / `advice/`)

| Wave | Seats | Role mix | Terminal | Advice files |
|---|---:|---|---|---:|
| build | 81 | scout20 executor16 reviewer14 scribe10 connector8 critic6 revenger4 sentinel2 simplifier1 | completed81 / failed0 | 81, 1:1 with seat names |
| falsify | 79 | reviewer33 scout10 executor9 critic8 connector6 mutation-tester4 revenger3 scribe3 sentinel2 simplifier1 | completed79 / failed0 | 79, 1:1 with seat names |

Both waves are inside the 64–100 band, and the round total is 160 ≤ 200. Each wave was one `taskCall`, and zero tasks carry a `model` key. Recomputing the falsify `taskCall` sha256 reproduces `72e81bc6…0812`. The role mixes match the report exactly.

Terminal completion is corroborated by the 1:1 nonempty advice files, but its only source is L1's record: the committed spawn results show `pending`. Status-neutral provenance defects, routed below:

- Build `validation.json` has no policy version field.
- Falsify has no `validation.json` and no policy block; only the env path names v2.
- The build `taskCall` digest `cdf02ba7…` reproduces only with `ensure_ascii=True`, while the falsify producer uses `False`.
- The falsify ledger attempt records `spawned:0 refused:0` for 79 spawned seats.
- Falsify `completion-summary.json` `verdict_first_lines` says 36/41/2. A count of the committed `VERDICT:` lines gives 36 confirm / 43 partial / 0 refute, and 5 of 79 reports do not open with `VERDICT`.

## Claims — re-measured vs evidence-verified

**Re-measured by this closure:**

- matrix cardinality and labels
- recount of the run receipts
- failing and changed row sets
- every digest in `acceptance.json` and the receipts against the committed or installed bytes
- the doc-ledger counts
- the census
- the SCORECARD diff

**Evidence-verified only (gate standard, never executed):**

- the exits of `measure.py` and `stale-statements.py`
- the `check.py --selftest` tally
- the `test-snapshot.sh` tally
- the `check-receipt.py` `VALID` verdict and its 26-mutation selftest
- the live runs

### C1 calibration — `MODEL_LOADING` for the exact loading envelope

- Matrix: `for f in $(git -C L ls-tree --name-only ccc4bb3 tests/probe-verdicts/ | grep '\.json$'); do git -C L cat-file blob ccc4bb3:$f; done | jq -s 'add|{n:length, ml:(map(select(.expected.verdict=="MODEL_LOADING"))|length)}'`. Result: **9 files, 72 rows, 72 unique names, 17 `MODEL_LOADING`**. The other expected verdicts are FOREIGN_SERVICE 37, MODEL_OK 8, UNAUTHORIZED_SERVICE 5, MODEL_MISMATCH 3, DEAD 1 and NOT_HTTP 1. The 72/17 figure matches.
- Receipts, from `git cat-file blob ccc4bb3:.ufo/waves/round-16/run-{before,after}.json`: before is **55 pass / 17 fail, exit 1**; after is **72 / 0, exit 0**. The 17 rows failing before are exactly the 17 `MODEL_LOADING` rows. Before the repair they all graded `FOREIGN_SERVICE`: 16 as `non-2xx-non-model-http` and 1 as `html-non-model`. The changed set equals the loading set, and the harness `passed` field is reproduced on all 144 of 144 records. Matches.
- Frozen probe: `.ufo/waves/round-16/frozen/kama-probe-before.sh` sha256 `93ee4302…cd64` is byte-identical to `20e392e:tools/kama-probe.sh`. The current probe is `36b64978…a29d3` at both `726f737` and `ccc4bb3`. Matches.
- `acceptance.json`: `ok: true`, `errors: []`, measured revision `726f737a…`. All **16 of 16** recorded digests match the committed blobs, including the matrix set `bf9068d8…1f32`. `recorded_utc` 14:13:02Z falls between `726f737` (14:10:32Z) and `ccc4bb3` (14:15:00Z), so the evidence is not future-dated.
- Doc ledger: `stale-before.txt` shows `ledger_rows=17 uncorrected=17`. `stale-after.txt` shows `uncorrected=0`. An independent replication of the committed ledger gives 17 at `20e392e` and 0 at `726f737` and `ccc4bb3`. 17 → 0 matches.
- Static diff `git diff 20e392e 726f737 -- tools/kama-probe.sh` (+54/−8): `MODEL_LOADING` requires all of the following:
  - status 503 on `GET /v1/models`
  - top-level `error.message == "Loading model"`
  - `error.type == "unavailable_error"`
  - `error.code` an integer (not a bool) equal to 503

  Without python3 the probe falls back to the old `FOREIGN_SERVICE`. No other verdict branch changed; the remaining hunks are vocabulary, help, the `listeners` counter and the baseline whitelist.
- No-harm evidence: `run-test-snapshot.txt` reports `RESULT pass=30 fail=0`. The diff adds exactly 6 assertions to `tools/test-snapshot.sh`, which fits 24 → 30. `run-check-selftest.txt` reports `tests=72 passes=72 failures=0` and `selftest: 4/4 malformed tests rejected (ok)`, exit 0.
- **Verdict: calibration improved.** The round-1 overreach is caught and shown able to fail (frozen 55/17). The vocabulary and the "foreign" statements are corrected across the corpus. The score stays 7 → 7: this is a bounded repair, not a higher mastery reading.

### C2 operability — capability `live-llamacpp-lifecycle`

- `receipt.json`: 10 checks, all passed. Check ids equal the gate's `REQUIRED_CHECKS`: health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_exited, teardown_port_closed, model_unchanged. The run spans 2026-10-20T14:06:27.859Z–.974Z on port 37527. It precedes `726f737`.
- Digests against actual bytes:
  - tool `b8c5e8d4…` and probe `36b64978…` match the blobs.
  - server `b6a31a8e…0cd804` matches `sha256sum ~/.local/opt/llama-b11755/llama-server`.
  - model `270cba1b…256d` matches `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf`.
  - `readlink -f ~/.local/bin/llama-server` resolves to the receipt's `server.realpath`.
- `receipt-frozen-probe.json`: 10/10 using the frozen probe `93ee4302…`. This shows the claims are separable: C2 does not depend on C1.
- `controls.txt`: `digest_mismatch_exit=3`; ports 34113, 8080 and 631 give `exit=2`; `post_pgrep_llama_server=0`. Today `pgrep -a llama-server` prints nothing (rc 1), so no server is left running.
- Loading window: receipt `transitions[1]` records status 503 with `repeats: 37`, which gives 38 identical samples and matches the reported "38". `replay-captured-503.txt` grades the captured body `MODEL_LOADING` under the current probe and `FOREIGN_SERVICE` under the frozen one.
- Surfaces contacted: a grep of `726f737:tools/kama-llamacpp-live.py` for path literals finds `/health`, `/v1/models`, `/props`, `/slots` and `/metrics` only. There is no generation or completion route and no POST request. This is consistent with round 1's GET-only metadata default.
- Registration: the `SCORECARD.md` capability row names first-working round 16. The `SKILL.md` row registers `check-receipt.py` with exits 0 valid / 1 invalid / 2 unreadable and its selftest spelling. The gate source has 26 `mut(` cases at `ccc4bb3` versus 16 at `b8e485c`. The lesson's M2 "16" is the superseded first gate; M8 records 26.
- S038 re-opened on GitHub. The API returned 403 (rate limit), so the check used the release page and the expanded-assets HTML. Asset `llama-b11755-bin-ubuntu-x64.tar.gz` has `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, labelled "Pre-release", commit `704366d76…`. The retained tarball `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` hashes to the same value.
- **Verdict: operability improved** through capability acquisition, demonstrated running and evidence-verified. Score 8 → 8.

### Install judgment (llama.cpp b11755, operator-owned; not undone)

**In scope.** Under the 2026-10-19 tooling directive (`~/.omp/agent/RULES.md`), any agent may install a tool that helps its task. C2 needs a runtime, and the host had none: `/usr/bin/llama-server` is absent and no package owns it. The channel is the directive's third: an official release binary, extracted to `~/.local/opt/llama-b11755` with a `~/.local/bin/llama-server` link. The asset digest matches upstream, pacman was not used (it is paused), and nothing was piped to a shell. The 1.2 MB GGUF is CI fixture data from an official upstream repository, kept in a lane-owned cache, not a tool.

**Honestly reported.** The report, PROVINCE and the L0 question all record the version, commit, channel, asset digest, reason, paths, the Pre-release status and the persistent footprint. Removal is left to the operator through L0 question (b).

Running an unregistered child endpoint before L0 ratifies the PROVINCE narrowing is a lane interpretation of round-1 safety question 3 (`round-1-safety.md:88`). It is disclosed and bounded: the child is the lane's own, on a non-registered, non-listening loopback port, contacted with GET metadata only, then torn down. I do not rate it as harm. Two precision nits:

- The PATH statement "now precedes `/usr/bin`" shadows nothing: no `/usr/bin/llama-server` exists.
- The retained release tarball in `~/.local/opt/` is not named in the report or the L0 question.

## Discernment sample and source re-opens

Outside review on 2026-10-20, sampled from the round-16 lesson `## Gate`. Every source was fetched from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/…`, except S040, which came from llm-d.ai. The fetched file digests equal the pinned S035, S036 and S037 copies.

| Item | Decision | Re-opened source | Outside judgment | Reason |
|---|---|---|---|---|
| `MODEL_LOADING` for the exact triple on `/v1/models` 503 | admit (KQ19) | `server-http.cpp:312` `// no endpoints are allowed to be accessed when the server is not ready`; 314 `res.status = 503`; 318–320 `"Loading model"` / `"unavailable_error"` / `503`; `/v1/models` route at `server.cpp:284`; only `/` and UI assets exempt (240–248, 309–311) | agree | The unconditional pre-routing gate emits exactly this body on `/v1/models`. The probe predicate matches all four conjuncts and nothing wider. Nit: OPTIONS bypasses the gate (347–352), so "every non-frontend path" overstates by one method. |
| Widen to any 503, any `unavailable_error`, or substring "loading" | reject | `server-context.cpp:5396` `"no slot available"` and `server-models.cpp:2585` `"Stream owner model is loading, retry later"`, both `ERROR_TYPE_UNAVAILABLE`; `server-common.cpp:119-122` maps that type to `unavailable_error` / 503 | agree | Two unrelated endpoints share type and code, and one also contains "loading". Widening would conflate a slot shortage and a router stream with the start-up gate. |
| README alone supports the `/v1/models` 503 | reject | README:1258 (in GET `/v1/models`, 1254) "The `meta` field can be `null` (for example, while the model is still loading)."; README:487 (GET `/health`) "Explanation: the model is still being loaded." | agree | The README documents 503 only for `/health` (485–487) and `/slots` (987). For `/v1/models` it describes a 200 list with `meta: null`, so the code is the deciding source. |
| S040 supersedes S021 (URL 404) | admit | `curl -L https://llm-d.ai/docs/operations/readiness-probes` returned **404**; https://llm-d.ai/docs/0.10/operations/readiness-probes renders "Version: v0.10", §Problem Statement | agree | The quote is present verbatim, and the row is correctly scoped to vLLM-only guidance, not llama.cpp behaviour. |
| A green live receipt proves registered-consumer health or restoration | reject | `git show ccc4bb3:registry/history/latest.tsv` lists all three consumers as `DEAD connection-refused`; receipt port 37527 is outside the refusal set {8080, 34113} | agree | The receipt describes a lane-owned child at one sampled instant. Nothing registered was contacted or restored. |

Quote checks:

- S036, `server-http.cpp:312`: 13 words.
- S037, `server.cpp:493`: "start the HTTP server before loading the model to be able to serve /health requests", 15 words. Lines 494 `start()`, 507 `load_model()` and 515 `is_ready.store(true)` confirm the single-model window is reachable.
- S035: 14 and 7 words.
- Newly written S040 row, re-opened by this integrator: "The vLLM `/health` endpoint only indicates that the server process is running, not that models are loaded and ready to serve." That is **21 words** (`wc -w`), at §Problem Statement, matching the lesson's stated location and count.

All quotes are ≤25 words and all anchors resolve. Nit: the S036 Gate cell says "body literal at 318-320" but quotes only line 318; type and code are at 319–320.

Census, committed bytes: rows **34 → 41**. Tier A rose 31 → 38, tier C stayed at 3. Mined rose 24 → 31; queued 5 and rejected 5 are unchanged. The added ids are exactly S035–S041. The only existing cell changed in place is S017's `used-by` (logged).

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

Exit **0**. Tabs are shown as spaces:

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

W04 is pre-existing scoped curation of one URL across scopes.

## Axis and trend verdicts

| Axis | Verdict | Evidence / limit |
|---|---|---|
| calibration | improved | C1: frozen 55/17 → 72/0 on a 72-row, 17-loading matrix; doc ledger 17 → 0; score 7 → 7 |
| operability | improved | C2: capability `live-llamacpp-lifecycle`, receipt 10/10 with every digest matching, frozen-probe control 10/10, controls exit 3/2; score 8 → 8 |
| depth | unchanged | The new code-level entry is credited under C1 and C2, not double-counted |
| coverage | unchanged | No registered consumer or surface added; consumers remain `DEAD` |
| freshness | unchanged | The live b11755 sample is a dated fixture run, credited under C2, not a re-verification of serving state |
| adjacency | unchanged | Not harmed. Kagi, kumitate, tsukuroi and souji handoffs were advised, not absorbed (`falsify/advice/ConnectCrossLaneScope.md`). The fixture exception is pending L0. Seat over-reads are disclosed incidents (M5). |

- **expansion: improved.** `corpus/knowledge/llamacpp-loading-lifecycle.md` opens with `source:`/`verified-at:`/`recheck:` and cites mined rows S035–S037 and S040. It holds a new coverage-map row (`corpus/README.md` §Round-16), and the `live-llamacpp-lifecycle` capability was demonstrated running.
- **quality: improved.** The round-11 "`/v1/models` answers 200 while loading" reading is corrected against pinned code and a live capture. Seventeen stale statements are corrected by appended text (17 → 0). The dead S021 URL is superseded by S040 as a new row. No admitted entry failed its re-check in this sample.
- **discernment: improved.** The author's `unchanged` correctly described pending outside review. This closure supplies the non-author sample: it agrees on two admits (KQ19 triple; S040 supersession) and three rejects, with re-opened sources and quote checks.

No exploratory claim was declared. No axis is harmed.

SHONEN: the four boxes remain author assertions. Box 2 now has a receipt a non-author could verify, but it is a lane-owned control, not consumer reconciliation. Boxes 1 and 3 still lack a non-author execution review. Do not promote and do not write `[x]` from these receipts; promotion is operator-owned.

## Routed defects (kama, next steered round)

1. **Wave provenance.** Record the policy version in every wave's validation, and give falsify a `validation.json` with a policy block. Use a single `taskCall` digest canonicalization: build `ensure_ascii=True` vs falsify `False`. Fix `dispatch-provenance.py` so it counts async `pending` spawns: the ledger shows `spawned:0` for 79.
2. **Falsify summary accuracy.** Correct `verdict_first_lines` by an appended note: 36/41/2 recorded vs 36/43/0 committed. Enforce the `VERDICT` first line (5/79 deviated) or report non-conformant seats.
3. **Append-only SOURCES.** S041's anchor and teaches cells were amended after the row's first commit in `b8e485c` (disclosed). Contract rule 2 lets only `status`/`recheck`/`used-by` change in place, so a later receipt regeneration must take a superseding row.
4. **Wording precision.** Narrow "every non-frontend path" (corpus README §Round-16 row, S036 cell) to exclude OPTIONS, which bypasses the gate at `server-http.cpp:347-352`. Quote or cite 319–320 for type and code alongside 318. Append the corrections; do not rewrite.
5. **Install disclosure precision.** In the next report or an L0 follow-up, name the retained tarball `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` under L0 question (b). Note that no `/usr/bin/llama-server` exists, so the PATH link shadows nothing. Leave the install itself alone; it is operator-owned.
6. **Carried debt (lesson §Falsify wave).** Five `check.py` harness mutants survive. `served_model` is not graded and there is no route-match assertion. Live checks `health_ready`, `teardown_*` and `loading_envelope_exact` are weak or ungraded. The harness `finally` block can leak an escaped exception. M3 (harness hang design) and M7 (session-store traversal recurrence) remain open. M7 needs exact exclusions in the wave context.

Open L0, operator-owned and unassessed here: `kama | round-16 | Ratify or reject the lane-owned live llama.cpp fixture …` (fleet `.ufo/l0-questions.md:58`). No promotion, mint, host transaction, service action, tool install, sibling-gate run or lane-authored-file edit was performed by this closure.
