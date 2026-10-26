author: hyaku closure (non-author integrator, @m_opus)

# kama round 44 — non-author closure spot-check

Date: 2026-10-26. Round measured: base `9d9cc93ec50783cd114829a91757b90d57c78dc6` (round-43 spot-check), measured commit `ef76777e5fbdc39a80ec7a93e41dc177366168db`, lane tip `d48e8cc32feffccb44d00a9cc04a3c9b4d9cfc50` (`git ls-remote origin refs/heads/master` prints it). Measurements ran in fresh clones of the lane repo at those three commits (`/tmp/kama-r44-closure/{base,meas,tip}`, scratch only) and in a blobless shallow fetch of `ggml-org/llama.cpp` holding `704366d76`, `ad1b88ca0`, `c0fd78626` and `d854d98b` (`/tmp/kama-r44-closure/llama`, scratch only). Every result below names a command a fresh session can re-run. No lane gate or counter was executed: the two frozen counters, the gate selftest and the regression counters are evidence-verified from committed receipts, and the underlying facts were re-measured with my own scripts.

Verdict: **admitted**. Both claims verify on my own measurement, no axis is harmed, and the spot-check agrees on both admits and both rejects sampled. Conformance notes and routed items are status-neutral (sections 1 and 7).

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an %H' -- .ufo/reports/round-44/kama.md` → `kama-shokunin 463f498cc8e8af89aa7b3bb594bb4b494a0571de` (05:25:35 -03:00, after the lane tip's 05:23:52) | ok |
| `SHONEN` heading, one line per box | lane `SHONEN.md` has 4 boxes (`grep -nE '^\s*- \[' SHONEN.md` → lines 5, 7, 9, 11); report `## SHONEN` carries 4 `[~]` lines | ok |
| Cited lane commits exist and are on the branch | `77d1bbf5`, `098df344`, `ef76777e`, `d48e8cc3`, base `9d9cc93e`, and `9307b15e` (cited for D1): `git rev-parse --verify <h>^{commit}` resolves and `git merge-base --is-ancestor <h> master` holds for all six | ok |
| Lane pushed, no leftover round work | `scripts/hyaku/jj-lane.sh state …/kama-shokunin` → `branch=master local=d48e8cc3… remote=d48e8cc3… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` → empty | ok |
| Prompt carries the template contract | `diff <(sed -n 1,140p .ufo/prompts/kama-round-44.md) kimi-shokunin/templates/round-prompt.md`: only `{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}`, `{{AXES}}` substitutions differ (axes rendered "operability + calibration"); §6 hyaku addendum at line 141, §7 scratch discipline at line 569 | ok |
| Marker report? | No: 4 round commits, receipts under `.ufo/waves/round-44/`, `w1-results.json` `seats 65`, 65 `results` | not `failed` |
| Counters frozen | `sha256sum tools/round44-{release-recheck,verdict-ledger}-audit.py` at the tip → `87503e18…`, `1933e75b…`, equal to `preregistration.json` `counter_sha256`; `git diff --stat 77d1bbf5 d48e8cc3 -- <both counters> preregistration.json controls/build_controls.py` → empty | ok |
| Append-only | `git diff --numstat 9d9cc93e d48e8cc3`: `LOG.md 11 0`, `corpus/QUALITY.md 10 0`, `corpus/lessons/round-44.md 84 0`, four knowledge entries additions only; `corpus/SOURCES.md 13 2` where the two changed rows S480, S481 are byte-identical in cells 1–10 and differ only in `used-by` (logged old→new in the lesson's Gate); `runtime-health-surface-processes.md 1 1` is the routed D2 `source:` line; `SKILL.md 20 2` are the two D5 backtick fixes | ok |

Driver digest (`.ufo/watchdog.log`, mutable): `2026-10-26T04:34:53-03:00 launch kama round=44 pgid=2711885 driver=hyaku-inline attempt=1`; `2026-10-26T05:26:49-03:00 complete kama round=44; hyaku-inline attempt=1`.

Conformance notes (status-neutral):

- **N-A, seat-report count:** the report says K1J07 "wrote no `.md` report, so 64 reports are committed". `.ufo/waves/round-44/w1/out/` has 64 top-level `<seat>.md` files, and K1J07's 12277-byte report is committed at `out/K1J07/K1J07.md` (in the tip commit, whose subject says "65 seat reports"). All 65 seats have a committed report; the report understates.
- **N-B, unreceipted tip regressions:** the report's tip-side lines for the round-42 counter (`mismatches=0 met=True maxN=44`), the capability census (`listed 9 observed 9 …`) and "all 12 `run … →` facts" have no committed tip receipt (`grep -rl 'maxN=44' .ufo/waves/round-44` → only `measured/r42-after.out`, which reads `mismatches=2 met=False` at `ef76777e`). I plain-checked the two legs that failed at `ef76777e`: the tip `SCORECARD.md` has one `Latest measured round: 44` line and `### Planned (round 45)` at line 2396 followed by item `1. Freshness: …`. Both hold.
- **N-C, dispatch-evidence identity:** the dispatched prompt was committed in the fleet repo by `kama-shokunin` (`b0fd7b7f`, "round-44: kama dispatch evidence (hyaku inline attempt 1)"). This is driver-side, not a lane defect.
- **N-D, worktree state:** at closure the helper reports `head=detached` with `tracked=0 untracked=0`. That is the ordinary jj-colocated state; the round's four commits carry the lane identity and the branch is pushed.

## 2. Claims

### C1 — freshness 8→8: 91 llama.cpp-pinned rows re-verified at b11889 (re-measured against upstream bytes; counter evidence-verified)

- Committed receipts: `controls/base.c1.out` → `pop=91 rows=0 … unverified=91 … met=False` exit 1; `c1/after.out` (tip=`ef76777e…`) → `pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=82 reworded=3 drifted=0 removed=0 flags_missing=0 section=1 met=True`. Equal to the report. All five controls read `met=False` (`controls/junk-*.c1.out`, exit 1).
- Population, mine: base `corpus/SOURCES.md` rows with `recheck` `on-release` and a `llama.cpp` source → 93 (91 mined, 1 queued, 1 rejected). Set difference against the ledger ids: S026 (rejected PR #18001, not a pinned file) and S038 (the release-identity record, not a file). That leaves exactly the frozen 91 ids. Pins (ledger column 3): `704366d76` 89, `ad1b88ca0` 1 (S015), `c0fd78626` 1 (S001). This matches the lesson's correction "89 not 90".
- Release identity: `git ls-remote https://github.com/ggml-org/llama.cpp.git refs/tags/b11889 refs/tags/b11755` → `d854d98bae598388ecea1ed84396587e5edc326d`, `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`.
- Independent byte check (`/tmp/kama-r44-closure/c1check.py`, my own code; for every ledger row, `git rev-parse <commit>:<path>` and a line-range text comparison in the upstream fetch):
  - `pin_blob` equals the blob at the row's pin commit for **91/91** rows. `release_blob` equals the blob at `d854d98b` for **91/91**. The `changed` flag is consistent with blob inequality for **91/91** (6 unchanged, 85 changed).
  - Of the 82 `holds` rows, the pinned ranges and the release ranges are **text-equal in 80**. They are equal after whitespace normalisation in 2: S121 differs only in indentation at `server-context.cpp` 5803 → 6852, and S112 in whitespace inside its README ranges. All 6 `unchanged-file` rows are text-equal. The 3 `holds-reworded` rows (S037, S043, S108) differ, as filed.
- Reworded rows read by me at `d854d98b`:
  - S043 `tools/server/server.cpp`: `signal_handler` is still at 26-38 with `exit(1)` at 34. `shutdown_handler` is set at 645-649, after `load_model` (633) and `is_ready.store(true)` (641). `if (opts.install_signal_handlers) server_install_signal_handlers();` is at 651-653, and the `sigaction(SIGINT/SIGTERM)` body is at 318-325. `start_loop()` is at 671 and `return 0` at 684. The default `bool install_signal_handlers = true;` is at line 42 (comment: "off when embedded in llama-cli"), and only `llama_server()`, the llama-cli embedding, sets `opts.install_signal_handlers = false`; the standalone path calls `server_run(…, server_run_opts{})`.
  - S108: the `role_type != SERVER_ROLE_ROUTER` block is at 116-132, and the `--kv-unified-per-slot` sizing is at 134-144 (`params.n_ctx = params.n_parallel * params.kv_unified_per_slot` at 141).
  - Both notes are accurate.
- Out-of-population drift: `git grep -n dry_sequence_breakers <commit> -- tools/server common`, filtered for `limit|max|64`, → at `d854d98b` `server-schema.cpp:264` "Error: dry_sequence_breakers must contain at most %d distinct entries" and README line 566 "At most 64 distinct breakers"; at `704366d76`, no such line. The `SKILL.md:1218-1219` flag is correct.
- Limits (lane-disclosed, judged here): the counter's `holds-reworded`/`drifted` branches check only a note length (K1Cheat), and S043/S047 are two-file rows (K1Design). My byte check closes the first gap for the landed ledger, since every `holds` row is text-equal up to whitespace and every blob is right. The minor "86 of 91 rows sit on changed files" in the report's planning bullet is 85 by blob (planning figure, not a claim value).
- C1 verifies. The freshness score is held at 8, by design.

### C2 — calibration 7→7: trend-verdict ledger, rounds 10–43 (re-measured; counter evidence-verified)

- Committed receipts: `controls/base.c2.out` → `rows=0 valid=0 missing=204 … met=False` exit 1; `c2/after.out` (tip=`ef76777e…`) → `rows=204 valid=204 missing=0 bad=0 agree=69 overclaim=2 underclaim=16 other=0 absent=15 table_missing=0 table_extra=0 summary=1 axes=1 met=True`. Equal to the report.
- Independent ledger check (`/tmp/kama-r44-closure/c2check.py`, my own code; it reads each row's cited line with `git show <rev>:<path>` in the fleet repo at `b0fd7b7f` or the lane at `9d9cc93e`):
  - **189/189** non-absent rows cite a line that names the row's trend and carries the row's verdict word.
  - The 15 `absent` rows: 12 outside rows for rounds 20–23, whose spot-check files do not exist at the lane revision, and 3 self rows for round 38, whose `# Trends` section gives axis verdicts only. No line in those files gives the trend a verdict.
- Agreement recomputed from the ledger, with order harmed < unchanged < unprovable < unprovable-but-better < improved: **agree 69, overclaim 2, underclaim 16, other 0, absent 15, n = 87**.
  - The 18 mismatch keys are rounds 10, 11, 12, 14, 15, 16, 17, 18, 19, 27, 34, 35, 39, 40 and 43 discernment (underclaim `unchanged` vs `improved`), plus 19 expansion (over), 28 expansion (over, `improved` vs `unprovable-but-better`) and 29 expansion (under).
  - These are exactly the 18 rows of `SCORECARD.md` §Round-44 calibration ledger (line 2347), and its summary line 2351 reads `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`.
- MANIFEST cross-check, mine (current fleet `MANIFEST.json`, kama entries with `trends`, last wins): **90/90** non-absent outside verdicts equal the MANIFEST trend, 0 differ. The 12 absent keys (rounds 20–23) have MANIFEST verdicts: `rounds[397]` `{improved, improved, unchanged}`, `[406]` `{unchanged, improved, unchanged}`, `[418]` `{unchanged, improved, improved}` and `[428]` `{unchanged, harmed, improved}`. These match the ledger notes (11 agreements and the round-23 quality reversal).
- The `## Axes` calibration row names `registry/verdict-ledger.tsv` and the summary figures; the score is held at 7.
- Limit (lane-disclosed, accepted): the measure is concurrence with the deciding closure (K2Design), not independent calibration. Still, it is the first surface that shows the lane's systematic discernment underclaim (15 of 16). The ledger is honest and reproducible.
- Side observation: `c2/manifest-crosscheck.py` always exits 0; the `exit=0` in `manifest-crosscheck-mutant.out` is appended. The mistake row 4 "shown able to fail" therefore rests on the printed `DIFF` line and `diff=1`, not on an exit code. It is a probe, not a gate (routed, item 4).
- C2 verifies.

### Separability and SCORECARD

- `measured/separability-c1only.out`: C1 files on the freeze tree give C1 `met=True` and C2 `missing=204 met=False`. `separability-c2only.out` is the mirror image. Both claims touch disjoint files (`registry/release-recheck-b11889.tsv` and `SOURCES.md`, against `registry/verdict-ledger.tsv` and `SCORECARD.md`).
- `git diff 9d9cc93e d48e8cc3 -- SCORECARD.md`: all six scores held (operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7). The depth row is re-anchored to `SKILL.md` sha256 `91440eb8…` (1420 lines, 32 `## `), and the calibration row cites the ledger.
- Routed round-43 D1 is fixed: tip `SCORECARD.md:53` reads "The live plan is `### Planned (round 45)` at the end of this file". `### Round-43 measured results` has its own heading at 2320, and `### Correction appended in round 44 (round-43 closure D1)` is at 2343.
- Gate: `measured/gate-check.out` → `registered 33 unregistered 0 defective 0` exit 0. `c1/gate-selftest-tip.out` → `GATE_SELFTEST pass=6 fail=0`, with the lane-tip arm at `ef76777e` (evidence-verified; this closes D4). `measured/r41-after.out` and `r43c1-after.out` read `mismatches=0 met=True` at `ef76777e`.

## 3. Axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| freshness | improved | 91 `on-release` rows re-verified at the newer release b11889. My byte check: blobs 91/91 at both commits, 86 text-equal, 2 whitespace-only, 3 reworded and read correct. The one stale statement found (`dry_sequence_breakers`) is flagged in `SKILL.md`, and I confirmed it upstream. Score held at 8 by design. |
| calibration | improved | New self-against-outside ledger, 204 rows reproduced by my reader (189 lines carry the verdict, 15 justified absences). Agreement 69/87, o2, u16, and the SCORECARD table and summary are exact. MANIFEST 90/90. D1 pointer fixed. Score held at 7. |
| operability | unchanged | No claim; score held at 8. Ancillary tool repairs: `release-recheck.py` exit 2 paths (`git diff --stat 77d1bbf5 ef76777e -- tools/release-recheck.py` → 25+/4−), plus `pin-trigger-consumed.py`, `planned-pointer-check.py` and the 15-case selftest extension, all registered (gate 33/0/0). |
| depth | unchanged | No claim; score held at 7. `SKILL.md` grew by registry rows and the drift flag. |
| coverage | unchanged | No claim; score held at 9. No new ground: 0 new knowledge entries, capability list 9. |
| adjacency | unchanged | No claim; score held at 7. N1Overlap's sibling-embedding report is filed, not absorbed, and `PROVINCE.md` is unchanged (`git diff --stat` empty). |

## 4. Discernment spot-check (LEARNING.md)

Sample of `corpus/lessons/round-44.md` `## Gate`: two admits and two rejects (the lesson's full decision list), plus one new-row quote check.

| Item | Decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| S482 llama.cpp release b11889 | admit | `gh api repos/ggml-org/llama.cpp/releases/tags/b11889`; `git ls-remote … refs/tags/b11889` | **agree** | Today: `tag_name` b11889, `target_commitish` `d854d98bae598388ecea1ed84396587e5edc326d`, `published_at` `2026-10-25T23:44:54Z`, `prerelease` true, `draft` false. `jq -S 'del(.assets[].download_count)'` is sha256-equal to the committed copy `w1/out/S1Rel/release-b11889.json`, and the body is identical. `ls-remote` gives the same commit. The tier A docs row is scoped to the release identity only. |
| S483 vLLM `preload.py` @ v0.31.0 | admit | `curl -sS https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py` | **agree** | sha256 `d2704e80c08f…` equals the committed copy. Line 73 is `@app.get("/health", include_in_schema=False)` in `_build_health_app` (70). Line 75 returns `200 if state.is_ready else 503`. `is_ready` is at 63-67, the flag help at 137 reads "Port for the parent /health endpoint; disabled by default.", the startup exit path is at 288-301 and `mark_ready()` at 302, all as anchored. This closes round-43 D2. |
| K1J07's `drifted` reading of S043 | reject | upstream `tools/server/server.cpp` at `d854d98b` (lines 26-38, 42, 633-673, 318-325, 754-766) | **agree** | The single-model exit behaviour survives: the default `install_signal_handlers = true` (42) is only turned off by the llama-cli embedding, and the install moved to 651-653, still after `load_model` and `is_ready`. K1J07's objection is ledger mechanics (the second-file `server-queue.cpp` anchor), not drift. `holds-reworded` is the honest verdict, and the note records the dissent. |
| S2Calib's "MANIFEST rounds 20–23 carry no `trends`" | reject | `python3 -c "…json.load(open('MANIFEST.json'))['rounds'][i]['trends']…"` for i = 397, 406, 418, 428 | **agree** | All four are kama lane-rounds 20–23 and each carries a three-key `trends` object (values in section 2, C2). The seat's claim is false, and the rejection is right. |
| New `corpus/SOURCES.md` row S483 (quote check) | admit | row `corpus/SOURCES.md:236` vs today's fetch | **agree** | The anchor quotes line 73 `@app.get("/health", include_in_schema=False)` (3 tokens) and line 75 `return Response(status_code=200 if state.is_ready else 503)` (8 words), each ≤25 words with its line location, and both are verbatim in today's bytes. S482's located quotes are single JSON values (`target_commitish`, `published_at`), also verbatim today. |

Registry validate: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit **0**, 93 `W04`, 1 `W01` (S481 tierC mined, now with 6 used-by paths), 0 `E`, `ok`. `census --file kama-shokunin/corpus/SOURCES.md` → rows 224, tier A 213, B 7, C 4, mined 205, queued 8, rejected 11, missing 0. This equals the report (222 → 224).

## 5. Trend verdicts

- **expansion: unchanged.** No knowledge entry was admitted on uncovered ground, and the capability list is still 9. S482 and S483 serve re-verification and an already-held entry. I agree with the lane.
- **quality: improved.** By the trend's definition, stale-prone entries re-verify with none failing: I re-measured the 91 llama.cpp-pinned rows myself against upstream bytes. The one stale statement found (`SKILL.md` §Round-28 `dry_sequence_breakers`) is marked, and I confirmed it upstream. The round-43 held-entry defects are corrected append-only: process qualifications in four entries, and the `CANNOT-ANSWER.md` pointer withdrawn. No admitted entry was found false and left unmarked. The round-26 lesson's drifted rerank candidates are history, and they are recorded in this round's lesson for the next recheck.
- **discernment: improved.** The spot-check agrees with the Gate on both admits and both rejects; the rejects are concrete and grounded in the source. KQ58–KQ61 each cite `corpus/lessons/round-44.md` mistakes with checks shown able to fail. The lane filed `unchanged` pending this check, which is the same pattern its own C2 ledger exposes (15 of 16 underclaims are discernment filed before the closure). That is disclosed, not a defect.

## 6. SHONEN

All four boxes remain `[~]`. Box 2 (end-to-end task) gains a run I reproduced independently: my byte check reproduces the release re-verification ledger's blobs and verdict classes against upstream. Boxes 1 and 3 are partly supported by the 33-row instrument registry; I checked the gate receipt, not every flag. Box 4: `PROVINCE.md` is unchanged and N1Overlap's report is not absorbed. None of the boxes is fully checkable by a non-author from this round alone. Promotion stays operator-owned, and no `[x]` is written.

## 7. Routed defects for round 45

1. **D1 (lane, report accuracy):** `.ufo/reports/round-44/kama.md:11` says K1J07 wrote no `.md` report and that 64 reports are committed. Its report is at `.ufo/waves/round-44/w1/out/K1J07/K1J07.md`, so 65 reports are committed. State the path layout and count correctly in the round-45 report (the fleet report is not edited by closure).
2. **D2 (lane, evidence):** commit tip-side receipts for regression lines the report states at the tip: the round-42 counter `mismatches=0 met=True maxN=44`, the capability census `listed 9 observed 9`, and the 12 SCORECARD `run … →` re-executions. Only the `ef76777e` receipts exist.
3. **D3 (lane, registry hygiene, the round-43 D2 pattern):** the process qualifications appended to `runtime-health-surface-matrix.md` (113, 124, 128), `endpoint-health-probe-conventions.md` (42, 61) and `engine-pin-watch.md` (85, 102) cite "(S480, S481)" for which process answers the second `/health`. S480's own `teaches` cell disclaims that, and S481 is tier C. Cite S483 there (two of them already name `preload.py:75` by path without the row id), and update S483 `used-by`.
4. **D4 (lane, probe vs gate):** `.ufo/waves/round-44/c2/manifest-crosscheck.py` has no failing exit code, so its "shown able to fail" (lesson mistake row 4, KQ61 support) rests on printed output. Give it `exit 1` on `diff>0` or register it as a probe, and say which.
5. **Carried (lane):** counters prove facts, not sufficiency. K1Cheat and K2Cheat met both frozen counters with shortcuts, and M1Ctr left 7 equivalent mutants. The next release recheck owes S038, S477, S041/S046/S055, S014/S058, the U9Pins non-llama.cpp pins (S010, S019, S048), and the round-26 lesson's rerank candidates. `base-unresolved.tsv` still has no producer.
6. **Operator:** L0 `kama | round-35` (MISSION.md axes pair), `kama | round-39` (validator band and planner) and `kama | round-41..43` (parked-worktree disposition; clean at this closure, `ahead=0 tracked=0 untracked=0`) are still open.
