VERDICT: partial — round-16 SCORECARD/LOG appends: the Current-state block and nearly every number/pointer resolve, but both files end in a dangling "measured results" promise and three numeric/scope claims are wrong or unbound.

Scope: HEAD b8e485c. At my first status read the tree was clean except `.ufo/waves/round-16/build/completion-summary.json` and `.ufo/waves/round-16/falsify/`; later in the run a sibling seat modified `.ufo/waves/round-16/measure.py` in the worktree (+33 lines: `EXPECTED_MATRIX_SHA256`/`EXPECTED_TESTS`/`EXPECTED_LOADING` breadth pin), so the tree is no longer clean and the counting command cited at SCORECARD.md:583 now differs from HEAD. I did not run or edit `measure.py`; I re-ran `tests/probe-verdicts/check.py` into /tmp instead. No llama-server started.

## Findings

### High — the promised measured-results sections do not exist at HEAD

- `SCORECARD.md:597-598`: "Sourced claim: C1 rests on S036/S037 (llama.cpp code at 704366d76), opened this round. **Measured values are appended below after execution.**" — the file ends at line 598; nothing follows.
- `LOG.md:952-953`: "… sources S035-S041 added, S017 used-by extended. **Measured results follow in the next entry.**" — the file ends at line 953; no next entry.
- Commands: `wc -l SCORECARD.md LOG.md` → `598 953`, exit 0; `grep -n 'measured results' SCORECARD.md | tail -1` → `434` (Round-14, no round-16 section).
- The measurement already happened and is committed in the same commit: `.ufo/waves/round-16/measure-stdout.txt` reads `before 1 55 17 / after 0 72 0` and `result: PASS`; `run-before.json` has `passes 55, failures 17`; `run-after.json` `72/0`; `live/receipt.json` and `live/receipt-frozen-probe.json` are both 10/10 and gate-VALID.
- Consequence: both scores remain "Planned score 7 → 7" / "Planned score 8 → 8", no `live-llamacpp-lifecycle` capability row is entered, and a reader of the two authority files cannot obtain the round's measured numbers. Acceptance "every number and pointer resolves" fails on exactly these two pointers. [INFERENCE] the append may be staged for a post-falsify integration commit, but the text says "after execution" while HEAD already contains the execution receipts.

### Medium — "five knowledge entries" undercounts the committed correction appends

- `LOG.md:936`: "appended corrections in five knowledge entries, the registry header comment and SKILL.md".
- `git show b8e485c -- corpus/knowledge | grep -c '^+## Correction — round 16'` → `6`, exit 0; `git show --name-only --format= b8e485c -- corpus/knowledge | grep -c '\.md$'` → `8` (7 existing + 1 new). The six `## Correction — round 16` headings are consumer-registry, endpoint-identity, listener-census, runtime-health-surface-matrix, served-identity-crosswalk, snapshot-history; ollama-evidence-replay additionally gets "**Repair ordering precision (appended round 16, …)**".
- "Five" is true only for the vocabulary/state subset that `SCORECARD.md:582` qualifies as "every lane document that called the vocabulary fixed or the state foreign" (consumer-registry, endpoint-identity, listener-census, runtime-health-surface-matrix, served-identity-crosswalk). LOG states no such scope, so as written it undercounts the same commit's correction appends by two. Fix: say "seven, of which five are vocabulary/state corrections", or scope the sentence to C1.

### Low — C2's historical anchor "(last real llama.cpp sample round 3)" is wrong

- `SCORECARD.md:592-593`: "Before: no lane tool could start a runtime (last real llama.cpp sample round 3)."
- Round 3 (2026-10-14, `LOG.md` §round 3) sampled only refused connections: "check: registry_rows_evaluated=3 model_ok=0 drift=3 exit=2". The last run that actually reached a llama.cpp runtime is round 2 (2026-09-29, "snapshot=20260929T043044Z … model_ok=3"). Round 3 is the last *census*, not a real llama.cpp sample; cite round 2 or reword to "last sample round 3 returned all DEAD".

### Low — the motivating 10:17 503 observation has no committed receipt

- `LOG.md:930-932`: "L1 smoke at 10:17 -03 saw a real b11755 llama-server answer `GET /v1/models` with 503 `{"error":{"message":"Loading model", …}}` while loading".
- The only structured live run at HEAD records the opposite observation: `.ufo/waves/round-16/live/receipt.json` has `loading_observed: false`, `loading_envelope_exact: null`, and three transitions — refused, refused, `/health` 200 at 22 ms; its teardown log `/tmp/kama-llamacpp-live-j9achou8.log` shows the whole lifecycle in ~42 ms. `/tmp/kama-ls.log` (10:18, port 43961) is a smoke server log with no request line.
- The pinned code does make the window reachable (server.cpp: `ctx_http.start()` before `load_model()`, `is_ready.store(true)` after — verified in `.ufo/waves/round-16/sources/llama.cpp-704366d/server.cpp:493-515`), so the claim is not contradicted, but it is prose-only. Mark it as an L1 observation/[INFERENCE] or attach the smoke capture; do not let it read as receipted evidence.

### Low — "capability rows held" names a row that is not in the capabilities table

- `SCORECARD.md:565-567`: "Capability rows held: `sources-registry` … and `ollama-offline-evidence-replay` (round 14, §Round-14 measured results)."
- `AXES.md:60-63` requires "a separate `capabilities:` table … Rows enter only through a round that demonstrates the capability running". The §Capabilities table (SCORECARD.md:122-126) holds only `sources-registry`; the ollama row lives in a round section. The pointer resolves, but the contract table is incomplete, and after the 10/10 live receipt `live-llamacpp-lifecycle` is demonstrated yet absent from both (ties to the High finding).

### Info — two brief-vs-HEAD gaps (outside my item, for the integration ledger)

- The wave brief lists "README/PROVINCE/SHONEN/SCORECARD/LOG round-16 appends"; `git show --stat b8e485c` does not touch README.md and `grep -n 'round 16\|Round 16\|round-16' README.md` returns nothing. PROVINCE.md and SHONEN.md were touched.
- `corpus/lessons/round-16.md` §Measurements says "Final numbers at the measured commit are in `.ufo/waves/round-16/acceptance.json`"; `test -e .ufo/waves/round-16/acceptance.json` → NO (only `run-before.json`, `run-after.json`, `measure-stdout.txt` and the two live receipts). The lesson is currently the only prose carrier of 55/17 → 72/72, so the missing acceptance receipt compounds the High finding. Owner: lesson/receipt seat; I did not edit it.
- Concurrent lane-file write: `.ufo/waves/round-16/measure.py` is `M` in `git status --porcelain` (33 insertions) during this run; HEAD's committed version does not contain the matrix-breadth pin. My numbers come from HEAD's receipts and from `check.py`, so they are unaffected, but L1 must adopt or revert that edit before claiming the cited counting command and its receipts are byte-identical artifacts.

## Verified — resolves (same item, passes)

- Authority: `grep -n '^kama|' ../shokunin.conf` → `52:kama|kama-shokunin|operability + calibration …`; `MISSION.md:16-38` labels its kama row "Historical example — the upstream fleet's initial nine-lane config, not the current roster" and `MISSION.md:50` says "Axis assignments in `shokunin.conf` are initial". The block's "Assigned axes: operability + calibration (`../shokunin.conf:52`)" is correct.
- Line pointers: SCORECARD `6-13` = the Current-authority paragraph, `45-55` = §Planned, `132` = the Saturation reading — all exact; `26-28` holds the three named caps.
- Axis numbers: operability 8, calibration 7, freshness 8, coverage 9, depth 7, adjacency 7 match the round-10 erratum and every round 11-15 statement ("rounds 11-15 changed none" holds); calibration is the lowest assigned; line 132 states saturation 8.
- "registry now 41 rows after round 16": `bash scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` → exit 0, `kama rows 41`, `tier.A 38`, `tier.C 3`, `mined 31`, `queued 5`, `rejected 5`; round-start `sources-before-census.txt` = rows 34, plus S035-S041 = 41.
- "last sampled DEAD … snapshot 20261014T124232Z; nothing listens on 8080 or 34113": `registry/history/latest.tsv` header `#@snapshot_id 20261014T124232Z` and three `DEAD connection-refused` rows; `ss -ltn | grep -E ':(8080|34113)\b'` empty; `pgrep -x llama-server` empty.
- Round-15 outside: `corpus/lessons/round-15-verifier-spotcheck.md:6` "Closure: status `ok`, admitted `true`"; its six routed items map one-to-one to the six dispositions in `corpus/lessons/round-16.md` §Routed defects.
- Counting command reproduces independently: `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json > /tmp/.../before.json` → exit 1, `tests 72, passes 55, failures 17`, `probe_sha256 93ee4302…a2cd64`; same with `tools/kama-probe.sh` → exit 0, `72/72`, changed verdicts 17, all expected `MODEL_LOADING`. Frozen sha equals `git cat-file blob 20e392e:tools/kama-probe.sh` (manifest matches).
- Live capability: `check-receipt.py` on `receipt.json` and `receipt-frozen-probe.json` → both exit 0 `VALID`; receipt `checks 10 passed 10` (`health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_exited`, `teardown_port_closed`, `model_unchanged`), port 32845, `pdeathsig.prctl_ok true`, teardown log present.
- Install numbers: tar `sha256 753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, size `22240468` (matches S038 row); `llama-server --version` → `build 11755, commit 704366d76`; model `sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; `readlink -f ~/.local/bin/llama-server` → `~/.local/opt/llama-b11755/llama-server`.
- Build-wave numbers: `.ufo/waves/round-16/build/spec.json` has exactly 81 items with role counts `executor 16, scout 20, reviewer 14, critic 6, sentinel 2, connector 8, revenger 4, scribe 10, simplifier 1` (= 81, matching LOG.md:946-949); `validation.json` `counts.spawn 81 / resume 0 / total 81`, policy `waveMinLanes 64 / waveMaxLanes 100`, argv/cwd/three env bindings/`taskCall_sha256` present; 81 `advice/*.md` names equal the 81 spec names exactly.
- Sources: `S035`-`S041` rows exist (grep `^\| S[0-9]{3}` → 41); S017 used-by diff adds `corpus/knowledge/llamacpp-loading-lifecycle.md`; pinned-file digests match S035/S036/S037 rows and `pins.json` (README 714c067b…, server-http 24ede172…, server.cpp 21439622…). KQ19 at `corpus/QUALITY.md:104,109`; `SKILL.md:507` §Round-16; `registry/endpoint-consumers.tsv:32` lists `MODEL_LOADING`.
- Historical support for C1's wording: "since round 1" — `git log -S 'non-2xx-non-model-http'` earliest is `c6199a2` (round-1 commit); "documented the loading body in round 10" — `git show 836b018:corpus/knowledge/runtime-health-surface-matrix.md:14` already records `503 unavailable_error "Loading model" while loading`.

## Limitations

- `measure.py` was not run (contract); the independent `check.py` runs above are the substitute and reproduce both arms.
- GitHub API re-fetch of tag b11755 returned HTTP 403 (read tool) / unparseable body (curl); "equal to the GitHub API digest", `published 2026-10-20T11:18:44Z` and `Pre-release` are unverified now. Local tar digest and size match the values S038 records, so only the API provenance clause remains [INFERENCE].
- `/tmp/kama-ls.log` is attributed to the 10:17 smoke by mtime/content only; it contains no HTTP request evidence.
- No server was started, so "nothing listens" is a point-in-time read-only observation.
- Line numbers are HEAD working-tree numbers (tree clean at b8e485c).

## Commands run (exits)

`wc -l` 0; `grep`/`tail` 0; `git show`/`git log`/`git ls-tree`/`git cat-file` 0; `bash scripts/sources-census.sh census` 0; `check.py --probe frozen` 1 (expected red) and `--probe tools/kama-probe.sh` 0; `check-receipt.py` ×2 0; `sha256sum`/`stat`/`readlink` 0; `python3` JSON inspections 0; `ss`/`pgrep` 0 with empty output; GitHub API fetch 403 (reported, not used as evidence).

## Installs

None.
