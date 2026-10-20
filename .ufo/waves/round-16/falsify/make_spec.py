#!/usr/bin/env python3
"""Build the kama round-16 wave-2 (falsify) spec. L1-authored; deterministic."""
import json, pathlib

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
W = LANE + "/.ufo/waves/round-16"
ADV = W + "/falsify/advice"
GOD = pathlib.Path("/home/vgpnk/.agents/skills/godspeed/directive.md").read_text()
HEAD = "/skill:godspeed\n" + GOD.rstrip("\n") + "\n\n"
IMPL = "b8e485c"

CONTEXT = f"""# Goal
kama-shokunin round 16, FALSIFY wave. Attack what the build wave produced; every seat attacks exactly the item it names and reports confirm / refute / partial with evidence. Seats advise; L1 integrates and owns the final measurements.
Landed and pushed at lane commit {IMPL} (lane root {LANE}):
- C1 calibration: `tools/kama-probe.sh` adds verdict MODEL_LOADING / reason llamacpp-loading (drift, exit 2) only when GET /v1/models answers 503 and the JSON body's `error` object has message == "Loading model", type == "unavailable_error", integer code 503 (bool/float/string rejected; extra top-level keys allowed; python3 required, else old FOREIGN_SERVICE). Frozen pre-round probe: `{W}/frozen/kama-probe-before.sh` (manifest `{W}/frozen/manifest.json`). Literal stub matrix `{LANE}/tests/probe-verdicts/*.json` (72 rows, 9 families, 17 MODEL_LOADING) run by `{LANE}/tests/probe-verdicts/check.py`; counting command `python3 {W}/measure.py` → L1 result: frozen 55 pass / 17 fail, current 72/72, changed set == the 17 loading rows. Receipts `{W}/run-before.json`, `{W}/run-after.json`, `{W}/measure-stdout.txt`. Appended corrections in `{LANE}/corpus/knowledge/{{endpoint-identity,consumer-registry,listener-census,served-identity-crosswalk,runtime-health-surface-matrix,snapshot-history,ollama-evidence-replay}}.md`, `{LANE}/registry/endpoint-consumers.tsv:32`, `{LANE}/SKILL.md` §Round-16, `{LANE}/corpus/QUALITY.md` KQ19. Planned score calibration 7 → 7.
- C2 operability capability `live-llamacpp-lifecycle`: `{LANE}/tools/kama-llamacpp-live.py` starts ~/.local/opt/llama-b11755/llama-server (official b11755, commit 704366d76) with ~/.cache/kama-shokunin/models/stories260K.gguf (sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d) on a free unregistered loopback port, captures surfaces, runs the probe, tears down; gate `{LANE}/tests/llamacpp-live/check-receipt.py`. L1 receipts `{W}/live/receipt.json` (10/10, VALID), `{W}/live/receipt-frozen-probe.json` (10/10 with the frozen probe — separability control), `{W}/live/controls.txt` (digest mismatch exit 3, --port 34113/8080 exit 2, --port 631 exit 2, post-run no llama-server and nothing on 8080/34113). Planned score operability 8 → 8 plus a capability row.
- New knowledge `{LANE}/corpus/knowledge/llamacpp-loading-lifecycle.md`; lesson `{LANE}/corpus/lessons/round-16.md`; SOURCES rows S035-S041 (+S017 used-by) in `{LANE}/corpus/SOURCES.md`; pinned upstream copies + digests in `{W}/sources/`; README/PROVINCE/SHONEN/SCORECARD/LOG round-16 appends. Build-wave advice: `{W}/build/advice/*.md`.

# Contract
- Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>. All paths absolute. Write ONLY your own Report, plus scratch under /tmp/kama-r16-<YourName>/ (remove it when done). Never edit any lane file, fleet file, MANIFEST.json, .ufo/state, or a sibling lane repo; never write the fleet root /home/vgpnk/Projects/shokunin outside this lane directory.
- Never read `.ufo/interactive-sessions/`, ~/.omp sessions/history, or any session/transcript/credential store; bound every grep/glob to the paths your item names; never dump environment variables.
- You MAY run the commands your item names (re-runs are the point of this wave) but never `{W}/measure.py` (it rewrites L1 receipts) — run `tests/probe-verdicts/check.py --probe PATH --json` instead and redirect output into /tmp. Only items that say so may start llama-server; any server you start must be torn down and you must confirm `pgrep -x llama-server` is empty afterwards. Never bind or probe 8080 or 34113 except through the tool's own refusal path.
- Operator tooling authorization (2026-10-19): you may install or upgrade tools that help the task — read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate, record tool/version/channel/reason in your Report). pacman guard (orchestrator ruling 2026-10-20): ALL pacman transactions are PAUSED host-wide — install only via `uv tool`/`npx`/an official binary in ~/.local/bin; never -Sy/-Syu/-U/-R, never downgrade, never restart a host service. When the pause lifts, run `pacman -Sp --print-format '%n %v' <pkgs>` first and proceed only if no listed package is installed.
- Leaf seat: no subagents (an executor may spawn at most one read-only labrat). Never message agent://all. Report: first line `VERDICT: confirm|refute|partial — <what you attacked>`, then evidence (command + exit + output excerpt, or path:line / URL + <=25-word quote), limitations, installs.
"""

FOOT = "\n# Acceptance\nWrite only your Report (and /tmp scratch). State exactly what you ran and its exit codes; mark inferences [INFERENCE]."
items = []
def add(name, role, body):
    items.append({"name": name, "role": role, "prompt": HEAD + "# Attack\n" + body.strip() + "\n" + FOOT})

# A. re-run counting commands
add("RerunMatrixFrozen", "reviewer", f"Attacks C1's red arm. Run `python3 {LANE}/tests/probe-verdicts/check.py --probe {W}/frozen/kama-probe-before.sh --json > /tmp/kama-r16-RerunMatrixFrozen/before.json`. Compare passes/failures and the exact failing-name set with {W}/run-before.json; confirm every failure is an expected MODEL_LOADING row observed as FOREIGN_SERVICE/non-2xx-non-model-http (or html-non-model) exit 2.")
add("RerunMatrixCurrent", "reviewer", f"Attacks C1's green arm. Run the matrix against {LANE}/tools/kama-probe.sh (`--json` into /tmp) and compare with {W}/run-after.json record by record (verdict, reason, exit, drift). Report any difference or flake; run it twice.")
add("RerunMatrixSelftest", "reviewer", f"Attacks the harness self-check. Run `python3 {LANE}/tests/probe-verdicts/check.py --selftest`; then read check.py and decide whether the 4 malformed tests it rejects cover duplicate names, unknown keys, bad R shapes and bad exit values. Report gaps.")
add("RerunSnapshotHarness", "reviewer", f"Attacks the no-harm claim for snapshot history. Run `bash {LANE}/tools/test-snapshot.sh` (expect RESULT pass=30 fail=0). Then copy {LANE}/tools to /tmp/kama-r16-RerunSnapshotHarness/tools, replace the copy's kama-probe.sh with {W}/frozen/kama-probe-before.sh, run the copied test-snapshot.sh, and report whether the MODEL_LOADING baseline case goes red on the frozen probe.")
add("RerunLiveHarness", "executor", f"Attacks C2 reproducibility. You MAY start llama-server via the tool only: `python3 {LANE}/tools/kama-llamacpp-live.py --server ~/.local/opt/llama-b11755/llama-server --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --alias kama-stories260k --out /tmp/kama-r16-RerunLiveHarness/receipt.json`, then validate with `python3 {LANE}/tests/llamacpp-live/check-receipt.py` (with --expect-model-sha256). Compare every check with {W}/live/receipt.json; confirm no llama-server remains.")
add("RerunReceiptGate", "reviewer", f"Attacks the receipt gate. Run check-receipt.py on {W}/live/receipt.json and receipt-frozen-probe.json (with --expect-model-sha256 and --expect-server-sha256 = sha256 of ~/.local/opt/llama-b11755/llama-server) and `--selftest`. Then hand-mutate a /tmp copy of receipt.json in 6 ways the selftest does not cover (your choice; e.g. probe declared port mismatch, child_env_keys containing a value, port inside port_refusal_set, install_tree missing the server basename) and report which are accepted.")
add("RerunCensus", "reviewer", f"Attacks the SOURCES conformance claim. Run `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` and `.../sources-census.sh --root /home/vgpnk/Projects/shokunin kama`; compare with {W}/sources-before-*.txt; report rows/tier/status before→after and any warning other than the known W04 S031.")
add("RerunLiveNegatives", "executor", f"Attacks C2's refusal and digest gates. Using the live tool only, run: wrong --model-sha256 (expect 3, no launch), --port 34113 and --port 8080 (expect 2), --port of a port currently listening (pick one from `ss -ltn`, never 8080/34113; expect 2), and a --server path pointing at a non-executable file (report exit). Confirm with `pgrep -x llama-server` that nothing was left running.")

# B. mutation testers (m_sol <=4)
add("MutateMatcher", "mutation-tester", f"Attacks KQ19's claim that the matrix kills weak matchers. Copy {LANE}/tools/kama-probe.sh to /tmp/kama-r16-MutateMatcher/ (copy the whole tools/ dir so REPO_ROOT logic works) and create >=8 single-change mutants of body_is_llamacpp_loading()/the classify branch: drop the type check, drop the message check, substring 'Loading', case-insensitive message, accept float code, drop the 503 status check, move the branch after the HTML sniff, accept any dict error. Run the matrix (`check.py --probe MUTANT --json`) per mutant; report killed/survived with the killing test names.")
add("MutateHarness", "mutation-tester", f"Attacks check.py's grading. In /tmp copies of {LANE}/tests/probe-verdicts/ (copy the dir including JSON files), mutate check.py to ignore reason, ignore exit, ignore drift, compare verdict case-insensitively, and treat probe timeout as pass. For each, run against the frozen probe and the current probe; report which mutants still reproduce the L1 numbers (survivors = grading not load-bearing).")
add("MutateReceiptGate", "mutation-tester", f"Attacks check-receipt.py. Mutate /tmp copies of the gate (skip model_unchanged derivation, accept metrics status 200, skip port_refusal_set membership, trust `passed` instead of re-deriving probe verdicts, accept any child_env_keys) and run each mutant on {W}/live/receipt.json plus its --selftest. Report survivors.")
add("MutateLiveRefusal", "mutation-tester", f"Attacks the live tool's refusal logic without starting a server: in a /tmp copy of {LANE}/tools/kama-llamacpp-live.py mutate refused_ports() (drop registry parsing; drop 34113; fail-open on unreadable registry) and run each mutant with `--port 34113` and with a pointed-at unreadable registry if the tool allows; report which mutants the existing controls would catch. Do not let any mutant reach launch (use a wrong --model-sha256 where needed: the digest gate runs first — verify that ordering).")

# C. critics (m_opus) and sentinels  (<=10 total)
critics = {
 "C1Admission": "Attack C1 as landed: does it verify as a calibration move (overreach caught, docs corrected) under /home/vgpnk/Projects/shokunin/AXES.md, or is it an operability patch? Is 7 → 7 honest? Name any falsifying evidence in the landed files.",
 "C2Admission": "Attack C2 as a capability acquisition under AXES.md §Capabilities: does the demonstration run, verify and stay inside the province (PROVINCE.md round-16 note, QUALITY KQ5)? Is 8 → 8 honest?",
 "NoHarm": "Hunt for any harmed axis (depth, coverage, freshness, adjacency, operability, calibration) caused by the round-16 changes: e.g. a correction that overstates, the PROVINCE note widening authority, an install outside the boundary, a stale claim newly introduced. Cite path:line.",
 "TrendVerdicts": "Propose and defend trend verdicts for expansion, quality, discernment (LEARNING.md at /home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/LEARNING.md) from the landed evidence; attack any 'improved' that rests on author-only judgment.",
 "SourceRows": "Attack S035-S041 in corpus/SOURCES.md against /home/vgpnk/Projects/shokunin/CORPUS.md §SOURCES.md rules: tiers, scopes, the S040-supersedes-S021 mechanism, S041 own-work tier A, mined status with used-by, and whether each Gate quote in corpus/lessons/round-16.md is located and <=25 words.",
 "MistakesFailCapable": "Attack corpus/lessons/round-16.md §Mistakes: is each fix shown able to fail (protocol requirement)? Is M1 truly 'captured-by none'? Are M2-M5 honest and complete versus the build advice?",
 "Separability": "Attack the separability argument: the frozen-probe live control and the stub-only C1 measure. Could either claim's verification depend on the other? Also check that no C2 check reads MODEL_LOADING.",
 "CapabilityRow": "Attack the planned capability row `live-llamacpp-lifecycle` (SCORECARD round-16 section and SKILL.md registry rows): pre-claiming, evidence pointer resolvability, first-working round, and whether a 1.2 MB toy model demonstration is described within its limits everywhere it is cited (SHONEN, README, knowledge entry).",
}
for n, q in critics.items():
    add(f"Critic{n}", "critic", q)
add("SentinelLiveFinal", "sentinel", f"Security review of the FINAL {LANE}/tools/kama-llamacpp-live.py at {IMPL}: env allowlist, --offline, loopback-only bind, refusal set, listener ownership checks before captures/probes, teardown ordering and signal handling, PDEATHSIG, body caps, atomic receipt write, temp-log deletion, no secrets in receipts ({W}/live/*.json). Read-only; cite lines.")
add("SentinelHostFootprint", "sentinel", "Audit the host footprint of round 16 read-only: no llama-server process (`pgrep -x llama-server`), nothing listening on 8080/34113, `find ~/.config ~/.omp/agent ~/.config/systemd -newer /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/manifest.json -maxdepth 3 -name '*llama*'` (names only), the install tree ~/.local/opt/llama-b11755 and ~/.cache/kama-shokunin ownership/permissions, the ~/.local/bin/llama-server link. Never read config bodies.")

# D. reviewers of each landed file
files = {
 "ProbeDiff": f"`git -C {LANE} diff 20e392e {IMPL} -- tools/kama-probe.sh`: every hunk scoped to MODEL_LOADING? wording claims body-shape only? listeners/whitelist/VOCAB consistent?",
 "CheckPy": f"{LANE}/tests/probe-verdicts/check.py: schema validation, stub fidelity (headers, Server, Content-Length), timeouts, drift grading, exit contract 0/1/2.",
 "MeasurePy": f"{W}/measure.py: frozen verification (manifest + git blob), directional set equality, exit codes; can it pass vacuously?",
 "LiveHarnessCode": f"{LANE}/tools/kama-llamacpp-live.py: correctness of each of the 10 checks against what it captures; any check that cannot fail?",
 "ReceiptGateCode": f"{LANE}/tests/llamacpp-live/check-receipt.py: does it bind to the producer's exact keys and re-derive every check from stored evidence?",
 "TestSnapshotDiff": f"`git -C {LANE} diff 20e392e {IMPL} -- tools/test-snapshot.sh`: is the new case correct, offline, and red on the frozen probe by construction?",
 "KnowledgeEntry": f"{LANE}/corpus/knowledge/llamacpp-loading-lifecycle.md: every factual line against its cited source (pinned copies in {W}/sources/llama.cpp-704366d/) and the receipt; flag overclaims.",
 "EndpointIdentityCorrection": f"{LANE}/corpus/knowledge/endpoint-identity.md §Correction — round 16: accurate versus rule table lines 9-20 and the landed probe? append-only?",
 "CrosswalkCorrection": f"{LANE}/corpus/knowledge/served-identity-crosswalk.md §Correction — round 16 versus lines 27-60 and S036/S037 at the pinned commit.",
 "HealthMatrixCorrection": f"{LANE}/corpus/knowledge/runtime-health-surface-matrix.md §Correction — round 16: are the engine contrasts faithful to the cited build advice files?",
 "SmallCorrections": f"Appended round-16 corrections in {LANE}/corpus/knowledge/consumer-registry.md, listener-census.md, snapshot-history.md, ollama-evidence-replay.md and registry/endpoint-consumers.tsv:32 — accurate, append-only, no prior line rewritten (`git diff 20e392e {IMPL}` on those paths).",
 "QualityKq19": f"{LANE}/corpus/QUALITY.md KQ19: does each admit/reject clause correspond to something the matrix or gates actually check? any clause unenforced?",
 "SkillSection": f"{LANE}/SKILL.md §Round-16: commands runnable as written? exit maps match the tools? pinned values correct?",
 "SourcesRowsA": f"Re-open S035, S036, S037 at the pinned commit (raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/...) and verify every line number, sha256 and claim in those rows and in corpus/lessons/round-16.md §Gate.",
 "SourcesRowsB": "Re-open S038 (release b11755 API digest), S039 (HF models-moved tree API: size, LFS oid, commit), S040 (v0.10 page and the 404 on S021's URL) and S017 (probes.md readiness sentence); verify every cell and quote.",
 "Lesson": f"{LANE}/corpus/lessons/round-16.md as a whole: numbers consistent with receipts? routed-defect dispositions accurate versus corpus/lessons/round-15-verifier-spotcheck.md:163-172?",
 "ReadmeProvinceShonen": f"Round-16 appends in {LANE}/corpus/README.md, PROVINCE.md and SHONEN.md: accurate, bounded, no [x] claimed, no authority widened beyond the C2 fixture?",
 "ScorecardLog": f"Round-16 appends in {LANE}/SCORECARD.md (Current state block + round 16) and LOG.md: every number and pointer resolves; the current-state block is correct versus shokunin.conf and earlier rows.",
}
for n, q in files.items():
    add(f"Review{n}", "reviewer", q)

# E. matrix families
for fam in ["AuthAndDead", "EnvelopeShapes", "ForeignControls", "LoadingEnvelope", "LoadingRace", "NearMissTriple", "NonLoadingStatuses", "Overbroad503", "ReadyControls"]:
    add(f"Family{fam}", "reviewer", f"Attack every row of {LANE}/tests/probe-verdicts/{fam}.json: is each literal oracle (verdict, reason, exit) right by the C1 rule and the landed classify()? Is each `why` accurate (esp. any line citations, which may refer to the frozen numbering)? Is any row redundant or non-discriminating?")

# F. scouts: source re-opens and extras
scouts = {
 "NoSlotStream": "Re-open llama.cpp @704366d76 tools/server/server-context.cpp (no slot available) and server-models.cpp (Stream owner model is loading) and confirm the quoted messages, lines and that both map to unavailable_error/503.",
 "MetricsSource": "Locate in llama.cpp @704366d76 source why GET /metrics returns 501 without --metrics (server-context.cpp / server-common.cpp) and confirm the receipt's metrics_not_enabled expectation is source-grounded.",
 "PropsBuildInfo": "Confirm from llama.cpp @704366d76 source that /props exposes model_alias, build_info, is_sleeping and default_generation_settings.n_ctx, so the receipt's props capture fields are real.",
 "MasterFreshness": "Check llama.cpp master today: is middleware_server_state's envelope identical to 704366d76 (diff the block)? Has any newer release changed it? Report the newest tag checked.",
 "ApiKeyOrder": "Re-verify from llama.cpp @704366d76 server-http.cpp that the state gate precedes the API-key check and OPTIONS short-circuits, quoting lines; confirm AuthAndDead.json's 401-carrying-loading rows are about probe precedence, not llama.cpp behaviour.",
 "OwnedByLlamacpp": "Confirm owned_by \"llamacpp\" and the alias-as-id behaviour in llama.cpp @704366d76 server-context.cpp, and whether `--alias` comma lists change data[].id.",
 "OfflineFlag": "Confirm `--offline` and the LLAMA_ARG_* environment handling in llama.cpp @704366d76 common/arg.cpp, and that the harness's env allowlist removes every LLAMA_ARG_* influence.",
 "PromiseInventoryProbe": f"Operator suggestion (considerthese/2026-10-20.md item 3): list every 'rejects/refuses/never/only' promise in the round-16 changes to {LANE}/tools/kama-probe.sh and pair each with the matrix row or test that exercises its negative case; flag unpaired promises.",
 "PromiseInventoryLive": f"Same promise inventory for {LANE}/tools/kama-llamacpp-live.py and tests/llamacpp-live/check-receipt.py: pair each refusal/never statement with a control in {W}/live/controls.txt or the gate selftest; flag unpaired ones.",
 "RegistryNoContact": f"Verify the round touched no registered consumer: grep {W}/ receipts and run-*.json for ports 8080/34113 outside refusal messages; confirm registry/history/ is unchanged since 20e392e (`git -C {LANE} diff --stat 20e392e {IMPL} -- registry/history`).",
}
for n, q in scouts.items():
    add(f"Scout{n}", "scout", q)

# G. executors: behavioural attacks needing small harness code in /tmp
execs = {
 "NoPythonFallback": f"Attack the 'without python3 the old FOREIGN_SERVICE path returns' claim: start a stub HTTP server (python, absolute path) serving the exact loading envelope as 503 on /v1/models, then run `bash {LANE}/tools/kama-probe.sh check --port P --expect '*' --json` with a PATH that contains bash, curl, ss and coreutils but no python3 (build a /tmp bin dir of symlinks). Report verdict, reason and exit; also note what --json output does without python3.",
 "ListenersSummary": f"Attack the listeners integration: serve the loading envelope on a stub port and run `bash {LANE}/tools/kama-probe.sh listeners --port P --json`; confirm the row verdict MODEL_LOADING and summary model_loading=1 with probed equal to the sum of buckets; repeat with the frozen probe for contrast.",
 "SnapshotPersistence": f"Attack snapshot history with MODEL_LOADING: in /tmp, write a one-row registry TSV whose consumer file declares http://127.0.0.1:P (a stub serving the loading envelope), run `bash {LANE}/tools/kama-probe.sh snapshot --registry R --history /tmp/.../hist` twice; confirm latest.tsv records MODEL_LOADING, the second run reports transitions=0 and no malformed-row-dropped note. Never use the lane's registry/history.",
 "ConsumersCheck": f"Attack `check` (registry mode) with a /tmp registry row pointing at a loading stub: verdict MODEL_LOADING, drift true, exit 2, summary counts consistent.",
 "ApiKeyLiveOrder": "You MAY start ONE llama-server directly (absolute path ~/.local/opt/llama-b11755/llama-server, the pinned GGUF, --api-key kama-test-only, --host 127.0.0.1, a free port you pick with bind-to-0 that is not 8080/34113, env -i PATH=$PATH HOME=$HOME). Poll GET /v1/models in a tight loop from launch without a key and record whether any 503 Loading model or only 401 appears; then stop it and confirm pgrep is empty. This tests the precedence claim live (the window is ~8 ms; report honestly if no 503 is seen).",
 "LoadingWindowCapture": "You MAY start llama-server (absolute path, pinned GGUF, loopback, free non-registered port, env allowlist) up to 10 times with a tight GET /v1/models loop from launch, to try to capture a live 503 body; when captured, save status, headers and body, feed that exact body to a stub and run the current and frozen probe on it. Report capture count out of tries, the verbatim body, and both verdicts. Always tear down.",
 "MatrixDeterminism": f"Run the full matrix against the current probe 5 times (`check.py --json` into /tmp) and report any non-deterministic row; also run 4 copies concurrently to check port-collision robustness.",
}
for n, q in execs.items():
    add(f"Exec{n}", "executor", q)

# H. connectors
conns = {
 "SiblingCollision": "Read-only: `git -C /home/vgpnk/Projects/shokunin status --porcelain` and list untracked fleet-root files that name kama or round-16 (misroot candidates from kama seats); report paths only, do not move anything.",
 "CrossLaneScope": "Compare kama-shokunin/corpus/knowledge/cross-lane-scope.md with the round-16 changes: should a handoff row exist for the persistent ~/.local/opt install (tsukuroi), the GGUF cache (souji), --api-key (kagi), router mode (kumitate)? Advise exact append text.",
 "KagiHealthBranch": "Read kagi-shokunin/SKILL.md around its /health rule (read-only) and draft the handoff note kama should report (not write) about the 503 Loading model branch.",
 "MoriFootprint": "Read mori-shokunin/PROVINCE.md (read-only) and advise how kama's report should hand off the transient process/listener footprint of the live harness, if at all.",
 "TameshiConventions": "Read tameshi-shokunin/corpus/QUALITY.md (read-only) and compare the round-16 stub matrix + mutation evidence with tameshi's fixture conventions; list the top 3 gaps, if any.",
 "ConsiderTheseLedger": f"Read {LANE}/considerthese/2026-10-20.md (operator reflection) and check which of its 4 suggestions the round-16 artifacts already satisfy or contradict; advise one bounded follow-up for the next round.",
}
for n, q in conns.items():
    add(f"Connect{n}", "connector", q)

# I. revengers
add("RevengerFrozenProvenance", "revenger", f"Reconstruct and verify the frozen-probe chain: {W}/frozen/manifest.json versus `git -C {LANE} cat-file blob 20e392ea683a36bc223eb7cb45897acfb45456a3:tools/kama-probe.sh` versus the snapshot bytes; and that run-before.json's probe_sha256 equals it.")
add("RevengerRunReceipts", "revenger", f"Reconstruct L1's C1 numbers from {W}/run-before.json, run-after.json and measure-stdout.txt only: recount passes/failures, the changed set, and verify stdout_sha256 fields; report any inconsistency.")
add("RevengerLiveTimeline", "revenger", f"Reconstruct the live run timeline from {W}/live/receipt.json (transitions, captures, probes, teardown, log lines) and check internal consistency (timestamps ordered, port consistent across argv/captures/probes, probe declared URL port, teardown after probes).")

# J. scribes (prose consistency)
add("ScribeNumbersLedger", "scribe", f"Build a table of every round-16 number (72/17/55, 10/10, 30/0, 41 rows, ports, digests, seat counts) as stated in {LANE}/corpus/lessons/round-16.md, SKILL.md §Round-16, SCORECARD.md round 16, LOG.md round 16, corpus/README.md round 16, knowledge entry and SHONEN; flag every mismatch.")
add("ScribeReportSources", "scribe", f"Draft (in your Report only) the round report's 'Sources & frontier' section from {W}/sources-before-*.txt, the current census (run `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh --root /home/vgpnk/Projects/shokunin kama`) and corpus/lessons/round-16.md §Gate: rows before→after, rows added by tier, rows touched old→new, frontier rows advanced.")
add("ScribeReportWaves", "scribe", f"Draft (in your Report only) the wave accounting for the build wave from {W}/build/spec.json, dispatch.json, assignments.json and build/advice/ (count reports present per role); list any seat without a report.")
add("SimplifierFinal", "simplifier", f"Review the landed round-16 code ({LANE}/tools/kama-llamacpp-live.py, tests/llamacpp-live/check-receipt.py, tests/probe-verdicts/check.py, {W}/measure.py) for dead code or duplicated logic that adds failure surface; recommend deletions with reasons (advice only).")

spec = {"context": CONTEXT, "reportDir": ".ufo/waves/round-16/falsify/advice", "maxLanes": 100, "items": items}
names = [i["name"] for i in items]
assert len(names) == len(set(names))
(pathlib.Path(W) / "falsify" / "spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
from collections import Counter
print(len(items), dict(Counter(i["role"] for i in items)))
