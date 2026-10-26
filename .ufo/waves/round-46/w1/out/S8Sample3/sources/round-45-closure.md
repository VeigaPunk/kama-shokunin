author: hyaku closure (non-author integrator, @m_opus)

# kama round 45 — non-author closure spot-check

Date: 2026-10-26. Round measured: base `6b8ccfb310de339e9452514aea3a9402a970c3e6` (round-44 spot-check), measured commit `21945c6125c2fae531be94d7652ee058c68e5f83`, lane L1 tip `0fddf257a0c574dc4a29106602fcfb489e6f7376`, branch tip at closure `a553bd7cdfb72b69431beed04e71173520bab715` (orchestrator salvage, N-A). I read committed bytes with `git show <rev>:<path>`. Upstream re-fetches, a model download and one live run used `/fast/scratch/hyaku/kama-r45/closure/`, which is scratch and was deleted after use. Every result below names a command a fresh session can re-run. No lane gate or counter was executed. The two frozen counters, the v2 amendment, the gate and the regression counters are evidence-verified from committed receipts. Both claims were also re-measured with my own code.

Verdict: **rejected-honest-stop** (status `ok`, admitted `false`). C1 verifies on my own measurement. C2 does not verify: its frozen predicate reads `met=False` under v1 and under the pre-data amendment v2. The lane reported this honestly and did not narrow it after seeing data. No axis is harmed. The spot-check agrees with the Gate on both admits and both rejects.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an %H %ci' -- .ufo/reports/round-45/kama.md` → `kama-shokunin 277ee2ef32435155212d48b1711413305f017bc3 2026-10-26 07:52:54 -0300`, after the L1 tip `0fddf257` (committed 07:52:03) | ok |
| `SHONEN` heading, one line per box | lane `SHONEN.md` has 4 boxes (`grep -nE '^\s*- \[' SHONEN.md` → lines 5, 7, 9, 11); report `## SHONEN` has 4 `[~]` lines | ok |
| Cited lane commits exist and are on the branch | `1641aa07`, `58ffddd6`, `052cb1e9`, `85977699`, `21945c61`, `0718b6ab`, `82b5e9d3`, `0fddf257` and base `6b8ccfb3`: `git cat-file -e <h>^{commit}` succeeds and `git merge-base --is-ancestor <h> master` holds for all nine | ok |
| Lane pushed, no leftover round work | `scripts/hyaku/jj-lane.sh state …/kama-shokunin` → `branch=master local=a553bd7c… remote=a553bd7c… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` → empty; `git ls-remote origin refs/heads/master` → `a553bd7c…` | ok |
| Prompt carries the template contract | `diff <(sed -n 1,140p .ufo/prompts/kama-round-45.md) kimi-shokunin/templates/round-prompt.md`: only the `{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}` and `{{AXES}}` substitutions differ (axes rendered "operability + calibration"). §6 hyaku addendum at line 141, §7 scratch discipline at line 569. Prompt committed `6105c587` by `kama-shokunin` at 05:35:20, one second before the launch line | ok |
| Marker report? | No. There are 8 round commits, receipts under `.ufo/waves/round-45/`, two new registry ledgers, and S484/S485 | not `failed` |
| Counters frozen | at the tip, `sha256sum tools/round45-recheck-audit.py tools/round45-claim-outcome-audit.py` → `244b6690…`, `0fb7ad42…`, equal to `preregistration.json` `claims[].counter_sha256`. `tools/round45-claim-outcome-audit-v2.py` → `024ba8ec…`, equal to `preregistration-amendment-c2.json`. `git diff --stat 1641aa07 a553bd7c -- <both counters> preregistration.json` → empty. `git diff --stat 85977699 a553bd7c -- <v2> <amendment>` → empty | ok |
| v2 is pre-data and minimal | `git cat-file -e 85977699:registry/claim-outcome-ledger.tsv` → "exists on disk, but not in '85977699'", so no ledger row existed at the amendment. `diff v1 v2` → the docstring plus one regex line adding `\bverify\b` and `\bimproved\b`, as declared. `amended_at_utc` 10:40:54Z is at or before the commit time 07:40:55 -03 | ok |
| Append-only | `git diff --numstat 6b8ccfb3 a553bd7c`: `LOG.md 7 0`, `corpus/QUALITY.md 4 0`, `corpus/README.md 4 0`, `corpus/lessons/round-45.md 35 0`, four knowledge entries `2 0` each. `corpus/SOURCES.md 23 1`, where the one changed row is S483, whose `used-by` cell changed (logged old→new in the lesson Gate). `SCORECARD.md 50 4`, where the four replaced lines are the head banner, the depth re-anchor, the calibration spot-check count and the planned pointer, and all six scores are unchanged | ok |

Driver digest (`.ufo/watchdog.log`, mutable): `2026-10-26T05:35:21-03:00 launch kama round=45 pgid=1382694 driver=hyaku-inline attempt=1`; `2026-10-26T09:23:43-03:00 complete kama round=45; hyaku-inline attempt=1`.

Conformance notes (status-neutral):

- **N-A, post-report salvage on the branch:** `a553bd7c`, committed 09:05:38 -03 under the `kama-shokunin` identity, is the run-8 orchestrator's salvage. It lands after the report (07:52:54) and adds `w1.ready.dispatched` (an ABANDONED marker) and `w1/out/swarm-registry.json`. That file lists 64 members, all with `status` null (`jq '[.members[]|.status]|group_by(.)|map(length)'` → `[64]`), and holds no seat report. The report's "lane tip `0fddf257` (`git ls-remote` prints it)" was true when the report was filed but not at closure. This is driver-side, not a lane defect. It confirms the report's statement that 0 seats worked.
- **N-B, future-dated freeze timestamp:** `preregistration.json` `frozen_at_utc` 2026-10-26T09:05:00Z is 829 s later than its commit `1641aa07` (committer 05:51:11 -03 = 08:51:11Z). This is a §Evidence standard defect. The lane disclosed it (lesson Mistakes row 1, receipt `.ufo/waves/round-45/mistakes/prereg-time-check.out`, `exit=1`) and added KQ64.
- **N-C, truncating commit in history:** `0718b6ab` committed `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md` and `corpus/README.md` truncated to the round-45 appendix. `82b5e9d3` restored them with a new commit, not an amend. The base→tip numstat above shows every base byte kept. The lane disclosed this (Mistakes row 5).
- **N-D, L2 floor not served:** wave `kama-r45-w1` (64 seats) was dispatched, but only 32 were spawned and none took a turn (`.ufo/state/inline-dispatcher.log`, stall at 06:22:15 -03; host job cap). The L1 did the build work alone, so neither claim was attacked by a seat. The lane disclosed this ("no falsification credit"). The root cause is the driver.
- **N-E, model fixture gone:** the receipts' model path `~/.cache/kama-shokunin/models/stories260K.gguf` no longer exists (`find / -xdev -name 'stories260K*.gguf'` → nothing). I re-fetched it from `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`: 1185376 bytes, sha256 `270cba1b…256d`, equal to the receipts' `model.sha256`. The pin holds, but a fresh re-run of S485 needs this download step.

## 2. Claims

### C1 — freshness 8→8: ten round-44-planned rows (11 keys) re-verified against current upstream (re-measured against upstream bytes; counter evidence-verified)

- Committed receipts:
  - `controls/base.c1.out` (tip `6b8ccfb3`) → `pop=11 rows=0 … unverified=11 … met=False`, exit 1.
  - `c1/after.out` (tip `21945c61`) → `pop=11 rows=11 valid=11 unverified=0 unchanged=3 holds=8 reworded=0 drifted=0 removed=0 flags_missing=0 section=1 newrows=2 fetch=1 fetch_bad=0 met=True`.
  - `measured/c1-tip.out` (tip `82b5e9d3`, offline) → the same classes, `met=True`.
  - All four junk controls give C1 `met=False`, exit 1.
  - These equal the report.
- Ledger census (mine): `registry/recheck-r45.tsv` at `a553bd7c` has 11 rows: `holds` 8, `unchanged-file` 3.
- Independent upstream re-fetch (my own code, raw TSV split, whitespace-collapse witness match). I fetched all 12 URLs in `c1/upstream/fetch.log` today:
  - **12/12** fetched bodies have sha256 equal to `fetch.log`, and **12/12** committed copies (`pin_copy`/`new_copy`) hash to the same value.
  - Class re-derived from bytes. S014, S058 and S048:in6.h: pin == new byte-for-byte and the witness is present, so `unchanged-file`. S010, S019 and S048:tcp_ipv6.c: pin ≠ new and the witness is present in both, so `holds`. **6/6** file rows agree with the ledger.
  - Content spot reads:
    - S010: the word `health` is absent from both copies.
    - S019: the `gen_ai.server.request.duration` / `time_per_output_token` / `time_to_first_token` rows are at new lines 202 / 336 / 456.
    - S048: the `get_tcp6_sock` `seq_printf` still prints four raw `%08X` words of `s6_addr32` (pin 2172–2177, v7.3 2173–2178).
- `new_ref` is current upstream (`git ls-remote`, today):
  - ollama `HEAD` = `66ab8482…`
  - ggml `HEAD` = `da8e2a54…`
  - semantic-conventions-genai `HEAD` = `20259355…`
  - linux `v7.3^{}` = `c03c1a14…` and `v7.2^{}` = `8d3ae592…` (the pin)
  - Each pin matches the SOURCES row anchor (S019 by the short hash `547934a`).
- S038 (`gh api repos/ggml-org/llama.cpp/releases/tags/b11755`, today): `target_commitish` `704366d7…`, `published_at` 2026-10-20T11:18:44Z, `prerelease` true. Asset `llama-b11755-bin-ubuntu-x64.tar.gz` has size 22240468 and digest `sha256:753bfa73…e226`. All of these equal the committed `c1/identity/S038-release.json`.
- S477 (`git ls-remote --tags …/llama.cpp.git`, today): `b11755` is still `704366d7…`. There are 8207 refs; the highest tag is `b11899` = `c6fb3b5b…`, with 123 bN tags above b11755. The committed capture (8205 lines) gives `b11897` and 121 above. The dated figure is true of its sample, so the row holds. Two tags have appeared since.
- S041/S046/S055 (live). Committed `receipt-{1,2,3}.json` (sha256 `4df4e443…`, `7f9adbda…`, `9e9901ca…`) contain:
  - schema `kama-llamacpp-live/v3`, `outcome` pass, 11/11 checks evaluated and passed;
  - `build_info` `b11889-d854d98ba`; server sha256 `248e790d…f7a7`; model sha256 `270cba1b…256d`; tool sha256 `8c0dbb2b…62f3`, equal to `git show a553bd7c:tools/kama-llamacpp-live.py | sha256sum`;
  - ports 39173 / 40263 / 35221; runs 10:35:49Z–10:35:50Z, before the commit `052cb1e9` (07:37:31 -03);
  - `teardown.term_wait_ms` 15 / 9 / 7, `returncode` 0, `sigkill_sent` false.
- The installed binary today: `sha256sum ~/.local/opt/llama-b11889/llama-server` → `248e790d…f7a7`, and `--version` prints "build 11889, commit d854d98ba".
- My own live run of that binary (port chosen at random, the re-fetched model, `-c 256 -t 1 --no-webui --offline`, 2026-10-26T12:28Z):
  - `/health` → 200 `{"status":"ok"}`;
  - `/v1/models` id = the alias, `owned_by` `llamacpp`; `/metrics` → 501; `/props` `build_info` `b11889-d854d98ba`;
  - SIGTERM gave returncode 0 after 3 ms, and the port was refused afterwards.
  - The loading-503 phase was not observed, because the server had loaded before my first probe.
- New rows: S484 and S485 exist (`corpus/SOURCES.md:237-238`, tier A, `mined`). SOURCES census rows 224 → 226.
- Limit (lane-disclosed, judged here): the counter checks witness presence, not witness relevance, and no seat attacked the claim. My byte re-derivation and content reads close that gap for these 11 keys.
- **C1 verifies.** The freshness score is held at 8 by design.

### C2 — calibration 7→7: claim-outcome ledger, rounds 10–44 (re-measured; counter evidence-verified; NOT met)

- Committed receipts:
  - `controls/base.c2.out` → `missing=126 met=False`.
  - `c2/c2-v1.out` (tip `21945c61`) → `rows=126 valid=91 missing=0 bad=35 … consistency_bad=1 summary=0 axes=1 met=False`.
  - `c2/c2-v2.out` → `valid=103 bad=23 … consistency_bad=1 summary=0 met=False`.
  - `measured/c2v2-tip.out` (tip `82b5e9d3`) → the same, `met=False`, exit 1.
  - These equal the report. The frozen predicate fails under both counters.
- Independent ledger check (my own code). `registry/claim-outcome-ledger.tsv` has 126 rows covering 63 keys, and each key has one `self` row and one `outside` row:
  - `self` rows: 63, all fleet `6105c587`;
  - `outside` rows: 57 from lane `6b8ccfb3` and 6 from fleet `6105c587` (the rounds 20–23 MANIFEST path).
  - Of the 125 rows with a cited line, **125/125** resolve to a non-empty line at the cited revision.
- Recomputation with the order not-met < unprovable < partial < met, where `absent` and `mixed` are not ranked: **agree 58, overclaim 1 (28 C1), underclaim 2 (26 C1, 40 C1), other 1 (24 C1 `mixed`), absent 1 (10 C1)**. This equals `SCORECARD.md` §Round-45 claim-outcome ledger `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`.
- Lines I read: 11 C1 (self "C1 improved; C2 improved"; outside "C1 calibration and C2 coverage verify"), 24 C1, 26 C1, 28 C1 (self "met under both A0 … and A1"; outside "does not verify"), 40 C1, 25 C1, 31 C1 and 31 C3. Every outcome word matches its ledger row.
- Ruling: the ledger is honest and reproducible, and the counter's readers are what fail (KQ65). The preregistration makes the frozen code the predicate, and that code reads `met=False`. Not narrowed after data. **C2 does not verify, so this is an honest stop.**

### SCORECARD and regressions

- `git diff 6b8ccfb3 a553bd7c -- SCORECARD.md`: all six scores are unchanged (operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7).
  - The depth row is re-anchored to `SKILL.md` sha256 `3046955b…` (1432 lines, 33 `## `).
  - The calibration row's spot-check figure 30 → 31: `git ls-tree --name-only a553bd7c corpus/lessons/ | grep -c verifier-spotcheck.md$` → 31.
  - The planned pointer now reads `### Planned (round 46)`.
- Tip receipts at `82b5e9d3`, evidence-verified; these close round-44 D2:
  - `r41-tip.out` `mismatches=0 met=True`;
  - `r42-tip.out` `mismatches=0 maxN=45 met=True`;
  - `r43-tip.out` `registered=36 mismatches=0 met=True`;
  - `gate-tip.out` `registered 36 unregistered 0 defective 0`;
  - `cap-tip.out` `listed 9 observed 9 … met True`;
  - `pointer-tip.out` `met=True`.
- Round-44 routed items:
  - **D1:** `frontier/seat-yield-r44-d1.out` shows `--expect-reports 64` → `exit=1` and 65 → `exit=0`.
  - **D3:** citation corrections are appended to three entries, and S483 `used-by` is updated.
  - **D4:** `frontier/manifest-crosscheck-mutant.out` → `diff=1 exit=1`, the clean ledger → `diff=0 exit=0`, and the selftest → `MANIFEST_CROSSCHECK_SELFTEST pass=5 fail=0`.
  - All are evidence-verified.

## 3. Axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| freshness | improved | 11 stale-prone keys re-verified against current upstream. My re-fetch reproduces all 12 byte copies, the 6 file classes, the S038 release record and the S477 tag; my own live b11889 run reproduces the S041/S046 statements. None failed. Score held at 8. |
| calibration | unprovable | The C2 predicate (frozen v1 and pre-data v2) reads `met=False`. The ledger itself reproduces exactly under my reader (58/61, o1, u2, other 1, absent 1). This follows the round-40 precedent: the substance is real, but the frozen code is the predicate. Score held at 7. |
| operability | unchanged | No claim; score held at 8. Two new checks with selftests (`tools/seat-yield.py`, `tools/manifest-crosscheck.py`) are registered (gate 36/0/0). |
| depth | unchanged | No claim; score held at 7. Registry rows were re-anchored. |
| coverage | unchanged | No claim; score held at 9. No new knowledge entry, and the capability list stays at 9. |
| adjacency | unchanged | No claim; score held at 7. `git diff 6b8ccfb3 a553bd7c -- PROVINCE.md` is empty. |

## 4. Discernment spot-check (LEARNING.md)

Sample of `corpus/lessons/round-45.md` `## Gate`: both admits and both rejects (the lesson's full decision list), plus quote checks on both new rows.

| Item | Decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| S484 llama.cpp b11889 Linux x64 asset | admit | `gh api repos/ggml-org/llama.cpp/releases/tags/b11889` (today); `sha256sum ~/.local/opt/llama-b11889/llama-server`; `llama-server --version` | **agree** | Today the API gives `target_commitish` `d854d98bae598388ecea1ed84396587e5edc326d`. The asset `llama-b11889-bin-ubuntu-x64.tar.gz` has size 22491719 and `digest` `sha256:2076290f3b80b7642e2dc165c01fbf1be386a56b4612ba45576d20527834d350`, equal to the committed `c1/live/release-b11889.json` and to the row. The extracted server hashes to `248e790d…f7a7` and prints "build 11889, commit d854d98ba". Tier A docs is correctly scoped to binary identity only. |
| S485 own-work b11889 live receipts | admit | committed `receipt-{1,2,3}.json`; my own live run of the same binary and the same model sha256 (§2 C1) | **agree** | The receipts carry what the row anchors (ports, times, server/model/tool sha256, `build_info`). My independent run reproduces `/health` 200 `{"status":"ok"}`, the alias id, `/metrics` 501 and a clean SIGTERM. The scope disclaimer ("sampled instants … not general timing") is honest. |
| Re-asserting S046's "3 ms" teardown at b11889 | reject | receipts' `teardown.term_wait_ms`; `corpus/knowledge/llamacpp-loading-lifecycle.md:189`, `:432` | **agree** | The lane observed 15 / 9 / 7 ms, and my own run gave 3 ms. That is a sampled duration that varies run to run, not a property. The entry's round-45 append says it is not re-asserted, and the round-17 line stays as a dated observation. |
| Reading rounds 25/31 C1 as `met` | reject | fleet `.ufo/reports/round-31/kama.md:81` at `6105c587`; lane `corpus/lessons/round-31-verifier-spotcheck.md:44` and `round-25-verifier-spotcheck.md:20` at `6b8ccfb3` | **agree** | Line 81 reads "Verdict: **met on the frozen counter; NOT admitted** — …", and closure line 44 reads "met on frozen counter but no-op control also meets it — not admitted". For round 25, line 20 reads "The C1 measured value verifies, but C1 is not a calibration axis-move". A token reader would score `met`, but each stated outcome is a refusal of admission, so `partial` is the honest class. |
| New `corpus/SOURCES.md` rows S484/S485 (quote check) | admit | lesson Gate lines 17–18 vs today's API record and the committed receipt | **agree** | The S484 quote is the asset `digest` field value: 1 token, location named, verbatim in today's API response. The S485 quote is `captures.health.body` `{"status":"ok"}`: 1 token, location named, verbatim in `receipt-1.json` and in my live run. Both are ≤25 words. |

Registry validate: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit **0**: 93 `W04`, 1 `W01` (S481 tier C mined), 0 `E`, `ok`. `census --file kama-shokunin/corpus/SOURCES.md` → tier B 7, C 4, mined 207, queued 8, rejected 11, missing 0. Rows: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 226, and 224 at `6b8ccfb3`. These equal the report.

## 5. Trend verdicts

- **expansion: unchanged.** No `knowledge/` entry was added (`git diff --numstat` shows only appends to four existing entries), and the capability list stays at 9. I agree with the lane.
- **quality: improved.** By the trend's definition, stale-prone entries re-verified with none failing: I re-measured all 11 keys myself against today's upstream, plus one live run. The round-44 D3 citation defects are corrected append-only. The truncation in `0718b6ab` was restored within the round with no base byte lost. No admitted entry was found false and left unmarked.
- **discernment: improved.** The spot-check agrees with the Gate on both admits and both rejects, and the rejects are concrete and grounded in the source. KQ62–KQ65 each cite a `## Mistakes` row of this round's lesson, with a check shown able to fail (KQ62 `exit=1`, KQ63 `exit=1`, KQ64 `exit=1`, KQ65 the v1 round-11 parse). The lane filed `unchanged` pending this check, which is the underclaim pattern its own round-44 ledger exposed. That is disclosed, not a defect.

## 6. SHONEN

All four boxes remain `[~]`. For box 2 (end-to-end task), I independently ran the b11889 binary against the pinned model, and it reproduced the receipts' health, identity and teardown facts. For boxes 1 and 3, I checked the gate receipt (36/0/0) and the two new selftests, not every registry flag. For box 4, `PROVINCE.md` is unchanged and no sibling scan ran. None of the boxes is fully checkable by a non-author from this round alone. Promotion stays operator-owned, and no `[x]` is written.

## 7. Routed defects for round 46

1. **D1 (lane, calibration re-claim):** the 126-row ledger is now known data. Any reader frozen after it is post-data. A re-claim on this ledger needs the KQ65 sample control (hand-read true lines from every phrasing class and every multi-claim line) committed and scored *before* the new reader sees the ledger, and must cite this closure's recomputation (58/61, o1, u2, other 1, absent 1) as the outside reference. Alternatively, claim on a population the reader has not seen (rounds 45+).
2. **D2 (lane, freeze timestamp):** apply KQ64 at the round-46 freeze, and commit the `prereg-time-check.py` receipt (`exit=0`) next to the preregistration before citing the freeze.
3. **D3 (lane, evidence durability):** S485 and the S041/S046/S055 re-runs depend on `~/.cache/kama-shokunin/models/stories260K.gguf`, which is gone. Record the re-fetch URL (`ggml-org/models-moved/…/tinyllamas/stories260K.gguf`) and the sha256 check in the live tool's recheck path or in the S485 `recheck` note, so a fresh session can re-run it.
4. **Carried (lane):** still frontier: S013, S022, the floating-series rows, S002–S004, and llama.cpp after b11889 (now `b11899` = `c6fb3b5b…`, 123 bN tags above b11755). Counters still prove facts, not sufficiency: no seat attacked C1 this round.
5. **Operator / driver:** the inline dispatcher stalled at 32/64 seats spawned (host job cap), leaving the round with zero working seats and no L2 floor (N-D). The orchestrator salvage commit `a553bd7c` was made under the lane identity after the report (N-A). The L0 questions `kama | round-35` (MISSION.md axes pair), `kama | round-39` (validator band and planner) and `kama | round-41..43` (parked worktree; clean at this closure) are still open.
