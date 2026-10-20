# CriticScoreDeltas — round 16 score-delta attack (advice only; L1 decides)

Axes I tested: calibration (C1), operability (C2 plus a capability row), and harm to freshness, adjacency, depth and coverage.
Read-only checks I ran: sha256 of the asset and the model, `llama-server --version`, and a comparison of tar members against the files on disk. None of these runs a lane gate. No installs.

## Verdict on the planned numbers

| Axis | Planned | Critic position | Why |
|---|---|---|---|
| calibration | 7 → 7 | **Keep 7. The verdict is "improved" only if F1 is fixed. Otherwise the round harms calibration.** | See F1 and F2 |
| operability | 8 → 8 plus capability row | **Keep 8. The verdict can be "improved" through the capability row only (one credit).** | See F3 and F4 |
| freshness / depth / coverage | unchanged | **"unchanged" is defensible only if F5 and F6 are handled.** Otherwise there is a latent freshness harm and a duplicate coverage authority. | See F5 and F6 |
| adjacency | unchanged | **"unchanged" holds only if F7 is disclosed** | See F7 |

### Against raising calibration to 8
- The SCORECARD itself still contradicts repo state, and repo-state match is the definition of calibration. AXES.md:15: "Self-assessment quality: gaps named honestly, confidence graded, overreach caught | SHONEN.md/SCORECARD entries match observed repo state". Evidence in the current file:
  - SCORECARD.md:6-7: "assigned LIVE axes remain operability and freshness". This is contradicted by `../shokunin.conf:52` ("kama|kama-shokunin|operability + calibration") and by SCORECARD.md:226.
  - SCORECARD.md:20/22: §Axes still shows freshness 7 and coverage 8. These are superseded only by the erratum at :205-213.
  - All four SHONEN boxes are still `[~]` author assertions (SHONEN.md:5-12).
- Precedent: the outside reviewers held every comparable bounded repair at delta 0. round-15-verifier-spotcheck.md:7 says: "Repairing a falsified executable assessment promise is a bounded improvement, not evidence of a higher mastery score." round-14-verifier-spotcheck.md:127 says: "score7→7, not a mastery score increase". C1 fixes one verdict class against a finite stub matrix, so it is the same kind of move.

### Against raising operability to 9
- None of the lane's own stated caps is lifted. SCORECARD.md:26-28: "the gate is verified against a real llama.cpp runtime only (vLLM/Ollama are fixture-shaped parser tests), the registry pins host-specific paths, and comparison is still invocation-driven". C2 adds a llama.cpp-only, invocation-driven harness and does not touch any of these caps.
- 8 is the saturation line. SCORECARD.md:132: "Saturation line 8/10 on every owned axis". AXES.md:57-64 sends "what the shokunin can now do" to the capability table, not to the scalar.
- Counter-precedent, which I reject: round 10 moved coverage 8 → 9 on a capability acquisition (SCORECARD.md:197, "coverage (capability acquisition) | … | 8 → 9"). That was before outside review began. Every round with an outside verdict since then (11-15) recorded a capability or repair at delta 0. Raising now would break consistency with those rulings.
- Stagnation nudge: inactive both before and after this round. AXES.md:68 requires "every axis the lane owns sits at or above the lane's saturation line", and calibration is 7. So the lowest-axis obligation still applies, and C1 must carry it (F2).

## Findings

**F1 — calibration harm (blocking): C1 leaves the lane's own fixed-vocabulary statements false.** Counterexample: after C1 lands, these lane texts still declare a closed six-verdict set without MODEL_LOADING:
- corpus/knowledge/endpoint-identity.md:3: "The verdict vocabulary is fixed: `MODEL_OK`, `MODEL_MISMATCH`, `FOREIGN_SERVICE`, `UNAUTHORIZED_SERVICE`, `DEAD`, and `NOT_HTTP`."
- endpoint-identity.md:163: "The model-list probe implementation and verdict vocabulary are unchanged."
- corpus/knowledge/consumer-registry.md:84-85: "binding vocabulary: `MODEL_OK` | `MODEL_MISMATCH` | `FOREIGN_SERVICE` | `UNAUTHORIZED_SERVICE` | `DEAD` | `NOT_HTTP`"
- registry/endpoint-consumers.tsv:31-32: "Verdicts come from tools/kama-probe.sh: MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | UNAUTHORIZED_SERVICE | DEAD | NOT_HTTP"
- SKILL.md:125-134: the decision table has no row for a loading verdict. This also affects depth: AXES.md:11 says "A reader can act on SKILL.md alone".

The item list in spec.json shows nobody owns these files: ProbeLoadingVerdict owns only `tools/kama-probe.sh`, and the scribes write only drafts. Under AXES.md:35 ("admitted only if every claim verifies and no axis is harmed"), the claimed axis would be harmed.
Impacted axes: calibration, depth.
Smallest fix: append a dated `[correction 2026-10-20 (round 16)]` after endpoint-identity.md:3 and :163 and after consumer-registry.md:84-85, never rewriting existing text. Add MODEL_LOADING to the registry tsv comment at line 32. Integrate the SKILL decision-table row (ScribeSkillSection draft).

**F2 — the claim could lose its calibration identity (high risk).** If the verifier reads C1 as probe-behaviour work (operability) or a new edge class (coverage), the round has two operability claims. AXES.md:32-33: "two claims on one axis in one round count as one claim. At least one claim works the lane's lowest-scoring non-retired axis". The lowest axis would then go unworked.
The strongest defence is already in the repo: the tool's output contradicted the lane's own documented knowledge.
- corpus/knowledge/runtime-health-surface-matrix.md:14: "503 `unavailable_error` "Loading model" while loading; 200 `{"status": "ok"}` when loaded"
- tools/kama-probe.sh:522 nonetheless emits "(non-2xx HTTP from a non-model service)".

That is "overreach caught" (AXES.md:15).
Smallest fix: the round report frames C1 explicitly as correcting a verdict that contradicted S001-documented lane knowledge. It must credit matrix:14 and S001 as prior knowledge and claim **no** depth or coverage credit for the loading fact.

**F3 — new mirror-image overreach inside C1 (calibration).** The planned evidence string (ProbeLoadingVerdict item, spec.json) says "(llama.cpp loading envelope: not ready, not a foreign service)". The reason name is `llamacpp-loading`. Both assert positive runtime identity from a three-field body fingerprint that any responder can emit. Per pinned server-http.cpp:307-325, the body is fixed bytes with no per-instance identity.
Smallest fix: wording such as "body matches the llama.cpp loading envelope; not ready; served identity unverified". Keep the reason token if L1 wants, but have the lesson/KQ define it as a *fingerprint*, not proof.

**F4 — no double credit for measurement machinery (operability).** round-15-verifier-spotcheck.md:151: "operability | unchanged | Existing serving tools preserved; no double credit for regression machinery". `tests/probe-verdicts/check.py`, the Family JSONs, `measure.py` and `tests/llamacpp-live/check-receipt.py` all measure claims. Only `tools/kama-llamacpp-live.py` (C2) is new repertoire, and it should be credited once, as the capability row.
The row must also credit the prior capability. SKILL.md:333-334: "Their real-runtime evidence is llama.cpp-specific and dated". SCORECARD.md:26 already claims real llama.cpp verification. What is new is acquiring a pinned runtime on demand and *proving teardown*, not "verified against real llama.cpp".
Smallest fix: suggested row text: "on-demand pinned llama-server lifecycle capture + probe + proven teardown on a non-registered loopback port; toy model; no registered consumer served". Append it in a round-16 section, following the round-14 pattern (SCORECARD.md:457-459).
Note: the canonical §Capabilities table (SCORECARD.md:124-126) still lists only `sources-registry`, while the round-14 row lives at :457-459. That is already a duplicate authority. Do not deepen it: point to both, or add an appended pointer note.

**F5 — latent freshness harm: the live capture contradicts a corpus claim that is not qualified.**
- Pinned README.md:1258 (704366d): "The `meta` field can be `null` (for example, while the model is still loading)."
- Lane copies of the same claim:
  - SKILL.md:361: "No: llama.cpp may list an id during loading"
  - endpoint-identity.md:161: "S001's pinned llama.cpp README permits `meta: null` while loading"
  - runtime-health-surface-matrix.md:55: "documents nullable `/v1/models` `meta` while loading"
- But pinned server-http.cpp:313-314 says "no endpoints are allowed to be accessed when the server is not ready". L1's smoke run observed /v1/models → 503 during load on b11755 in direct (non-router) mode.

If the C2 receipt records that 503 and the lane leaves the "may list an id during loading" text unqualified, the round holds evidence of a stale item and does not flag it. AXES.md:14 freshness: "stale items flagged or fixed". Router mode (README.md:1849, :2069 `"value": "loading"`) may still expose loading status [INFERENCE: untested].
A related calibration limit must be named: a 200 /v1/models with `meta: null` and a matching id would still grade MODEL_OK under C1.
Impacted axes: freshness (not assigned, but harm counts), calibration.
Smallest fix: append dated qualifications at those three anchors. Each should cite the b11755 middleware lines and, after L1's measured run, the receipt's `loading_observed`. Report freshness as "unchanged (stale item flagged)". Do not claim "improved", because only an unregistered toy endpoint was sampled; round-15-verifier-spotcheck.md:152 ties freshness to present serving-state verification.

**F6 — duplicate coverage authority risk.** ScribeKnowledgeEntry drafts `drafts/llamacpp-loading-lifecycle.md`. The lane counts knowledge entries as coverage (SCORECARD.md:212: "`ls corpus/knowledge/*.md | wc -l` 9 → 12"). Landing a new entry whose core fact already sits at runtime-health-surface-matrix.md:14 either silently inflates the coverage count or creates two authorities for the same fact.
Smallest fix: the entry must name matrix:14 as the prior authority and limit its new ground to the observed lifecycle transitions and the toy-runtime limits. Record coverage as "unchanged, entry +1 is not a coverage claim", or declare it as an explicit third claim (it would be unassigned).

**F7 — adjacency and "ephemeral" overreach.** Only the process is ephemeral. The install is a persistent host change:
- `~/.local/bin/llama-server -> ~/.local/opt/llama-b11755/llama-server` (symlink mtime Oct 20 10:17)
- a 22,240,468-byte tarball left at `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`

PROVINCE.md:10: "kama governs discovering whatever serves these ports and never claims an installed server".
Smallest fix:
- The report records the install (tool llama.cpp b11755 / commit 704366d76, channel: official GitHub release binary into ~/.local, reason C2, performed by L1), as GENERIC-RULES require.
- The PROVINCE note (ScribeProvinceNote) distinguishes a lane-owned test runtime binary from registered producers.
- Teardown evidence must not be read as "no host change".

The write boundary itself holds: no ~/.config, ~/.omp or systemd write is implied (PROVINCE.md:45).

**F8 — false-provenance gap in C2's server identity (calibration of the C2 receipt).** The harness records only "realpath and sha256 of that file" (LiveHarness item). I observed:
- `llama-b11755/llama-server` is **17,864 bytes**, a launcher.
- The server code is in `libllama-server-impl.so`, **7,671,544 bytes**.
- Read-only comparison: launcher asset member and disk copy are both `b6a31a8e…cd804`. impl.so asset member and disk copy are both `e404b91a…59ed`.
- Asset sha256 `753bfa73…e226` and model sha256 `270cba1b…256d` match the spec.
- `--version` → "version: 0.7.0-dev (build 11755, commit 704366d76)".

So the receipt pins a binary that does not contain the code producing the HTTP behaviour.
Smallest fix: the receipt or the lesson records the sha256 of `libllama-server-impl.so` (and ideally every `lib*.so` under the realpath directory). It also records the asset → member equality, e.g. `tar -xzOf ASSET llama-b11755/<m> | sha256sum`, so "official release" is shown rather than asserted. Loader resolution through RPATH vs LD_LIBRARY_PATH is unverified [INFERENCE].

**F9 — separability holds; prove it cheaply.** C2's required checks (LiveReceiptGate item: `health_ready … probe_model_ok, probe_mismatch, teardown_*`) exclude any loading verdict. Loading is "observed or not-observed is recorded, never required" (LiveHarness item). So C2 does not depend on C1 (AXES.md:31 "causally separable").
Smallest fix: L1 runs the harness once with `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh` and gets the same pass, which demonstrates separability directly.

**Not a risk (checked):** historical rows will not be reinterpreted. Every `FOREIGN_SERVICE` in registry/history/DELTA.md:7,15-22 is a port-8080 Jitsi-era row, e.g. "janitor-cli row-absent (was verdict=FOREIGN_SERVICE port=8080)". None is a loading sample, so the append-only history stays truthful.

## Limitations
- Advice only. I ran no lane gate, matrix or harness, and no server.
- Findings depend on drafts and items that were still being written (drafts/ was empty when I read it).
- Router-mode loading behaviour and api-key middleware ordering were not examined.
