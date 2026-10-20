VERDICT: partial — SKILL.md §Round-16 (lines 507-534): every command runs as written, every exit map matches its tool except one conflated C1 cell, and every pinned digest/value re-verifies; two prose claims in the same section are false as written ("the list at lines 11-14 gains" and "VOCAB is the single source").

Seat: KamaR16.ReviewSkillSection (leaf; no subagents). Lane root /home/vgpnk/Projects/shokunin/kama-shokunin at b8e485c. All commands below ran from that directory; outputs redirected to /tmp/kama-r16-ReviewSkillSection/.

## Findings (severity order)

F1 LOW — SKILL.md:509-511 is self-contradictory about the header verdict list.
"SKILL.md:509: The verdict list at lines 11-14 gains a seventh verdict, `MODEL_LOADING`."
but lines 11-14 still read: "`MODEL_OK` | `MODEL_MISMATCH` | `FOREIGN_SERVICE` | `UNAUTHORIZED_SERVICE` | `DEAD` | `NOT_HTTP`."
and line 510-511 says the list "is kept as history". `git show b8e485c -- SKILL.md` confirms the diff adds §Round-16 but never touches lines 11-14. Read literally, the first sentence is false; only the VOCAB in tools/kama-probe.sh has seven. Fix wording to "the vocabulary gains …" (or update the header) before an agent greps the header and believes there are six verdicts.
Evidence: `nl -ba SKILL.md | sed -n '11,14p;509,511p'`; `git show b8e485c -- SKILL.md` (§Round-16 is an append only).

F2 LOW — SKILL.md:510 "VOCAB is the single source" is not structurally true.
tools/kama-probe.sh duplicates the seven-word vocabulary as literals outside VOCAB (line 62): line 117 emits it in the `--help` heredoc (`verdicts: MODEL_OK … MODEL_LOADING`), line 939 repeats it in the `latest.tsv` baseline-validation `case`, and line 733 adds a MODEL_LOADING counting arm. All three lists agree today (the 72/72 matrix run proves the behavior), but adding an eighth verdict to VOCAB alone would leave `--help` stale and make line 939 drop new-verdict baseline rows as malformed. No test derives either list from VOCAB. Claim should be narrowed ("VOCAB is the authoritative list for outputs") or the literals generated from it.
Evidence: `nl -ba tools/kama-probe.sh | sed -n '62p;117p;733p;939p'`; `grep -rn VOCAB tests/` → no matches (nothing enforces the claim).

F3 LOW — adjacent tool defect, SKILL is the accurate side: check.py says "3 embedded malformed tests" in its own help/docstring.
`tests/probe-verdicts/check.py:29` ("feeds 3 embedded malformed tests") and `:448` (`--help`: "rejects 3 embedded malformed tests") contradict `SELFTEST_MALFORMED` at `:359-380`, which holds 4 entries, and the real run, which prints `selftest: 4/4 malformed tests rejected (ok)`. SKILL.md:530 says 4 and is correct. The gate's help text should say 4.
Evidence: `python3 tests/probe-verdicts/check.py --help | grep -A1 selftest` → "3 embedded"; `python3 tests/probe-verdicts/check.py --selftest` → exit 0, "4/4 malformed tests rejected (ok)".

F4 NIT — SKILL.md:531 C1 exit cell conflates 3 and 4.
The cell reads "3/4 frozen snapshot manifest or blob mismatch". Code (`measure.py:20-27,57-61,70-87,90-136`) and a scratch mirror show: exit 3 = manifest unreadable/malformed (missing file tested), exit 4 = frozen bytes/git-blob verification mismatch (tested by removing git discovery). Exit 3 is not a mismatch. Reword as "3 manifest unreadable/malformed; 4 snapshot/blob mismatch".
Evidence: mirror of measure.py at /tmp with the lane's real manifest: missing manifest → exit 3; manifest present but `git cat-file` unavailable → exit 4 ("frozen verification failed: git cat-file blob 20e392e:tools/kama-probe.sh exited 128").

## Confirmations (what I ran; exit codes exact)

Commands runnable as written:
- `python3 tests/probe-verdicts/check.py --json` → 0. Doc: `tests 72 passes 72 failures 0`; 9 matrix files cover 9 families; 17 rows expect MODEL_LOADING; 8 MODEL_OK, 3 MODEL_MISMATCH, 5 UNAUTHORIZED_SERVICE, 37 FOREIGN_SERVICE, 1 DEAD, 1 NOT_HTTP (sums to 72). Matches SKILL.md:530 "72 rows, 9 families, 17 MODEL_LOADING".
- `python3 tests/probe-verdicts/check.py --selftest` → 0: full matrix 72/72 plus "4/4 malformed tests rejected".
- `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → 1: 55 passes / 17 failures; all 17 failed rows expect MODEL_LOADING. Independent diff of the two `--json` documents: exactly 17 verdict changes, all 17 expected MODEL_LOADING, nothing else changed. Confirms SKILL.md:531's C1 map (0/1) and the context claim "changed set == the 17 loading rows".
- Exit-map negatives: `--probe /nonexistent/probe.sh` → 2; `--only no-such-test` → 2.
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json` → 0 "VALID"; `--selftest` → 0 "16 mutations + unreadable case all rejected; valid receipt accepted"; missing path → 2; malformed JSON → 2; `--expect-model-sha256 00` → 1 with an enumerated problem list ("INVALID … 2 problem(s)").
- All three expectation flags at once (`--expect-model-sha256 270cba…`, `--expect-server-sha256 b6a31a8e…`, `--expect-probe-sha256 6edd3c4c…`) → 0. `receipt-frozen-probe.json` → 0, and with `--expect-probe-sha256 93ee43…` → 0. Both receipts carry exactly 10 check ids (health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_exited, teardown_port_closed, model_unchanged) — SKILL.md:533 "10 check ids".
- `python3 tools/kama-llamacpp-live.py --help` → 0; every documented flag exists (`--server --model --model-sha256 --alias --out`, plus --probe/--ctx/--threads/--ready-timeout/--port).
- Documented live invocation with only `--model-sha256` replaced by zeros → 3 before launch: "model digest mismatch … refusing to launch"; no receipt written; `pgrep -x llama-server` empty before and after.
- Documented live invocation with `--port 8080` → 2 before launch: "port-refused-registered:8080"; no receipt. Confirms SKILL.md:532 exit 2 for a refused registered port without starting a server.
- `python3 .ufo/waves/round-16/measure.py --help` → 0; `--probe noequalsign` → 2 (usage), both before any receipt write. I did not run measure.py itself (contract forbids; it rewrites run-*.json).
- Stored C1 receipts corroborate 0/1: run-before.json exit 1, 55/17; run-after.json exit 0, 72/0; measure-stdout.txt "directional: loading_expectations=17 before_failed=17 changed=17 equal=True", "result: PASS".

Pinned values (all re-derived):
- Frozen probe sha256 `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` = sha256 of `.ufo/waves/round-16/frozen/kama-probe-before.sh`, = the `sha256` field of frozen/manifest.json, = sha256 of `git cat-file blob 20e392e:tools/kama-probe.sh` (blob 447e29b397405a3ee9813ca2e44aedf88abe2763; file size 47443 = manifest bytes). Current probe is 6edd3c4c….
- Model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` = sha256 of `~/.cache/kama-shokunin/models/stories260K.gguf`, size 1185376 (matches S039).
- Asset sha256 `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` = sha256 of `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`, size 22240468 (both match S038). The tarball's `llama-b11755/llama-server` is b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804, identical to the installed binary and to the receipt's `server.sha256`; the tarball's `libllama-server-impl.so` is e404b91a…, identical to the receipt's `server_impl_sha256`. So the recorded asset digest does identify the executed build.
- Refused ports: `HARD_REFUSED_PORTS = {8080, 34113}` (`tools/kama-llamacpp-live.py:57`); parsing registry/endpoint-consumers.tsv with the harness's own six patterns yields exactly {8080, 34113}; the only `:<port>` tokens in the registry are :34113 (×3) and :8080. `--port 8080` refused before launch (above).
- Pinned upstream sources: README.md 714c067…, server-common.cpp b4f4aae…, server-common.h ee401cf…, server-http.cpp 24ede17… all equal pins.json; server.cpp 214396… is not in pins.json but equals S037's recorded raw sha256. Pinned server-http.cpp:307-328 is the exact `middleware_server_state` 503 envelope with the three fields; :347-359 runs `middleware_server_state` before `middleware_validate_api_key`, confirming SKILL.md:518-519 "before the API-key check" (contrary to my initial suspicion).
- SKILL.md:530's "grades verdict, reason, exit and drift": check.py:337-346 reads verdict/reason/drift/served_model/evidence and asserts `drift == (verdict != MODEL_OK)`, so a MODEL_LOADING row with drift=false fails. Verified in code and by the 72/72 run.

§Round-16 table row-by-row against the tools: probe matrix (530) ok except F3's adjacent help text; C1 (531) ok except F4 wording; live capability (532) ok for flags/exit 3/exit 2 and pinned values; receipt gate (533) ok for 0/1/2 and the 16-mutation selftest.

## Limitations
- I did not start llama-server (no explicit live-launch authorization in this seat; RerunLiveHarness/RerunLiveNegatives own that). Exit 0/1 of the live harness and "all 10 checks pass" are grounded in the gated receipt plus code, not a fresh launch; [INFERENCE] that a fresh run reproduces them.
- I did not run `.ufo/waves/round-16/measure.py` (contract forbids; it rewrites L1 receipts). Its 0/1 condition was checked from stored receipts + code; 2/3/4 were exercised on a scratch copy of the script in /tmp (same bytes, real manifest/frozen blobs).
- `curl https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755` returned HTTP 403 (rate limit), so S038 was verified against the local tarball instead; the tarball digest+size and its member hashes match the recorded values and the receipt.
- "Router mode never emits the body", "a sleeping server answers /v1/models 200 from cache", and the no-python3 FOREIGN_SERVICE fallback were not executed here (owned by Scout*/Exec* seats); the no-python3 path is code-clear (`HAVE_PY` guard at tools/kama-probe.sh:79-80,428-429 → generic non-2xx branch at :556-567).
- Untracked `__pycache__/` dirs appeared in tools/ and tests/probe-verdicts/ during the wave (concurrent seats' Python tooling; one sibling dir already disappeared); I left them untouched.
- Host state after my runs: `pgrep -x llama-server` empty; no listener on 8080 or 34113.

Installs/updates: none.
