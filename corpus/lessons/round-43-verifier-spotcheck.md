author: hyaku closure (non-author integrator, @m_opus)

# kama round 43 — non-author closure spot-check

Date: 2026-10-26. Round measured: base `6897ead55c24ba08c9ac0b09466d4fbfe005a459` (round-42 spot-check; child of the closure prompt's "before" pin `3e6fdbe9e0ca1ca5b633d0b312d5561301e924c4`), measured commit `25df591a4e50f315b920ec0d0acba6145989e267`, lane tip `9307b15e0731f91efbd17ea10ef0d579fc1c9065` (`git ls-remote origin refs/heads/master` prints it). Measurements ran in fresh clones of the lane repo checked out at those three commits (`/tmp/kama-r43-closure/{base,meas,tip}`, scratch only; every result below names a command a fresh session can re-run). No lane gate was executed; lane counters and the lane's selftests are evidence-verified from committed receipts, and the underlying facts were re-measured with my own commands.

Verdict: **admitted**. All three claims verify, no axis is harmed, and the spot-check agrees on both admits and both rejects sampled. The round is short (38 of a 64-seat floor, no falsify wave) and the tip commit misplaced the SCORECARD measured section (D1); both are conformance defects, routed in section 7, status-neutral.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an %H' -- .ufo/reports/round-43/kama.md` → `kama-shokunin 70e6cd5f317cd6f7a5431c819bf0f5971fc64f15` (23:59:43 -03:00, after the lane tip's 23:59:37) | ok |
| `SHONEN` heading, one line per box | lane `SHONEN.md` has 4 boxes (`grep -n '^\s*- \[' SHONEN.md` → lines 5, 7, 9, 11); report `## SHONEN` carries 4 `[~]` lines | ok |
| Cited lane commits exist and are on the branch | `895793e0`, `1af8d516`, `6fd85332`, `a2c70a73`, `25df591a`, `9307b15e`, base `6897ead5`: `git cat-file -t` exists and `git merge-base --is-ancestor <h> master` holds for all seven | ok |
| Lane pushed, no leftover round work | `scripts/hyaku/jj-lane.sh state …/kama-shokunin` → `branch=master local=9307b15e… remote=9307b15e… ahead=0 behind=0 head=attached tracked=0 untracked=0`; `git status --porcelain \| wc -l` → 0 | ok |
| Prompt carries the template contract | `diff` of `.ufo/prompts/kama-round-43.md` lines 1-140 against `kimi-shokunin/templates/round-prompt.md`: only `{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}`, `{{AXES}}` substitutions differ; §6 hyaku addendum follows at line 141 | ok |
| Marker report? | No: 20 round commits, receipts, 38 seat reports (`ls .ufo/waves/round-43/w1/out/*.md \| wc -l` → 38; results JSON `seats 38 results 38`) | not `failed` |
| Counters frozen | `git diff --stat 895793e0 9307b15e -- tools/round43-{registry,hexrun,health}-audit.py .ufo/waves/round-43/preregistration.json .ufo/waves/round-43/controls/build_controls.py` → empty | ok |
| Append-only | `git diff --numstat 6897ead5 9307b15e -- LOG.md corpus/SOURCES.md 'corpus/lessons/round-4[0-2]*.md'` → `11 0`, `6 0`, earlier lessons untouched | ok |

Driver digest (`.ufo/watchdog.log`, mutable): `2026-10-25T22:25:38-03:00 launch kama round=43 pgid=4093527 driver=hyaku-inline attempt=1`; `2026-10-26T01:03:33-03:00 complete kama round=43; hyaku-inline attempt=1`.

Conformance notes (status-neutral):

- **N-A, round shape:** one 38-seat build wave ran; the 48-seat falsify wave (`.ufo/waves/round-43/w2/spec.json`, `dispatch.json`) was generated and never dispatched (no `w2.ready`); attack seats 3 of 38. Below the 64-seat floor and the 25 % attack share; disclosed by the report and the lesson.
- **N-B, commit path:** the lane committed with plain `git` from fresh clones, not `jj-lane.sh`, because the parked worktree was detached at launch. At closure the parked worktree is attached at the tip and clean (state line above), so the round-40 D5 / L0 `kama | round-41..43` premise no longer holds as of this pass.
- **N-C, dispatch-evidence identity:** the dispatched prompt was committed in the fleet repo by `kama-shokunin` (`b408e768`, "kama dispatch evidence (hyaku inline attempt 1)"); driver-side, not a lane defect.

## 2. Claims

### C1 — calibration 7→7: instrument registry and its describing files (re-measured; gate selftest evidence-verified)

- Committed receipts: `controls/base.c1.out` → `unreg=16 defect=0 flags=2 pins=19 selftest=1 dc=1 spot=1 hidden=2 pop=28 registered=12 mismatches=42 met=False`; `c1/after.out` (tip=`25df591a…`) → `… mismatches=0 met=True`; `c1/gate-after.out` → `registered 31 unregistered 0 defective 0`. Equal to the report.
- Plain re-measurement, mine (Python over `git ls-files 'tools/round*'` and `SKILL.md` text): tracked `tools/round*.py|sh` not named anywhere in `SKILL.md` → base **16** of 18 (exactly the round-35..42 list), measured **0** of 21, tip **0** of 21.
- `SKILL.md` §Round-43 registry completion (line 1378) has **19** `| Round-` rows. For each, sha256 of the tool at the tip starts with the row's pinned prefix: **19/19** (17 written `counter sha256 \`<12hex>\``, the two round-41 rows `sha256 \`<12hex>\`\`` with a stray backtick, D5). All 19 rows name exit codes 0 and 1.
- Spot count: `git ls-files 'corpus/lessons/*verifier-spotcheck.md' | wc -l` → 29 at base, measured and tip; SCORECARD calibration row says `28` at base and `29` at the tip. Fixed.
- README hidden entries: tip `README.md:28` names `.gitignore` and `.ufo/` as hidden entries; `ls -a` shows exactly those two (plus `.git`). Fixed.
- D-C: `corpus/SOURCES.md` gains an appended "correction to the round-42 entry above" stating S401 and S424 were opened in round 42 (append-only, `6 0`). The round-42 closure re-opened both and found the Gate accurate (`round-42-verifier-spotcheck.md` §4), so the correction is right.
- `GATE_SELFTEST pass=6 fail=0` at `SKILL.md:1325` is unchanged base→tip; the claim is that the tree now makes it true again. Evidence-verified only: base receipt `gate-selftest-base.out` (arm 6 failing) and the counter's `selftest=0` leg in `c1/after.out`; no standalone tip-side selftest receipt is committed (D4).
- Limits (lane-disclosed, judged here): the counter accepts a mega-row shortcut (W1R01). I read the 19 landed rows: individual rows, each with its own entry command, exit map and pin, so the landed tree is the honest one.
- Tip-commit regression (D1): at `9307b15e` the measured-results block was inserted *inside* the `## Planned` pointer sentence (`SCORECARD.md:53-67`, "The live plan is `### Round-43 measured results … ### Planned (round 44)` at the end of this file"); at `25df591a` line 53 correctly read "The live plan is `### Planned (round 44)` at the end of this file". The §Round 43 claim table points to "§Round-43 measured results", which now has no heading of its own. The numbers in the block are true; the placement and the pointer are wrong. This does not touch the claim's predicate (measured at `25df591a`), so C1 verifies, with D1 routed.

### C2 — operability 8→8, capability `hexrun-census` (re-measured; selftest evidence-verified)

- Committed receipts: `controls/base.c2.out` `tool=0 … met=False`; `c2/after.out` (seed 43) and `after-seed7.out` `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True`; `c2/scan-after.out` `tokens=778 distinct=215 lane_oid=138 md5_blob=1 upstream_ok=65 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=0`; `c2/selftest.out` `selftest pass=18 fail=0`; `c2/capability-audit-after.out` `listed 9 observed 9 missing 0 unsubstantiated 0 met True`.
- Independent census, my own code (regex `(?<![0-9A-Za-z])[0-9a-f]{32,127}(?![0-9A-Za-z])`, L≠64, `.md`/`.tsv` blobs outside `.ufo/` minus the two ledgers, `git cat-file --batch-check` for 40-hex, MD5 over every blob via `git cat-file --batch`):
  - base `6897ead5`: tokens 766, distinct 210, lane_oid 136, md5_blob 1, **residual 73** (by length 40:64, 32:7, 39:1, 65:1) — equals the lane's base census.
  - measured `25df591a`: tokens 778, distinct 215, lane_oid 138, md5_blob 1, residual 76 — equals `scan-after.out`.
  - residual 76 at the tip, classified by me against `registry/hexrun-ledger.tsv` (77 rows, 0 duplicate tokens): upstream with evidence file containing both token and repo text **65**, unverifiable with a ≥10-char note **9**, wrong **2**, unknown **0**. The 77th ledger row is the `correct` token of a wrong row.
- Upstream sample re-queried today with `gh api`: `sgl-project/sglang git/tags/35ce3132…` → tag `v0.5.22`, object `baa9befa…`, tagger `2026-10-15T23:39:11Z`; `ggml-org/llama.cpp commits/704366d7…` → `2026-10-20T11:02:05Z` "metal : fix missing MoE kernel variant … (#30610)"; `vllm-project/vllm commits/d4ee7fe7…` → `2026-09-14T20:24:18Z`, 6 files; `vllm-project/vllm commits/8d2cff81…` → "[Examples] Resettle Observability examples. (#40123)"; `VeigaPunk/shokunin commits/a7361db0…` → "round-37: kama report". All five agree with their ledger notes. Wrong row `0957ce619789d13d894e…` → `gh api repos/VeigaPunk/kama-shokunin/git/commits/…` HTTP 404, as flagged.
- Implementation read: `tools/hexrun-census.py` (642 lines) imports no counter and reads blobs through one `git cat-file --batch` stream; it is not the 78-line fixture-name shortcut W1R02 built.
- Capability row `hexrun-census`, first-working round 43, is in the round-43 canonical list (`SCORECARD.md` §Round 43). Score held 8.

### C3 — coverage 9→9, assimilation from `merge/kama` (re-measured; sources re-opened)

- Committed receipts: `controls/base.c3.out` `entry=0 rows=0 coverage=0 gate=0 refetch=1 census=1 met=False`; `c3/after.out` `entry=1 rows=1 coverage=1 gate=1 refetch=1 census=1 met=True`.
- Coverage ground, plain: `git grep -il -e 'weight cache daemon' -e 'weight-cache daemon' -e 'vllm preload' -- '*.md' ':!.ufo'` → base **0** files, tip 5.
- Entry `corpus/knowledge/runtime-health-surface-processes.md` (64 lines) opens with `source:` (S480, S481), `verified-at:`, `recheck:`; S480 and S481 are `mined` rows at `corpus/SOURCES.md:233-234` (13 fields each).
- Re-opened today: release `gh api repos/vllm-project/vllm/releases/tags/v0.31.0` → 60454 bytes, `body` identical to the committed copy (whole-file sha256 differs only in asset `download_count` fields, `diff <(jq -S …)`), published `2026-10-05T06:44:55Z`; body line 8 contains "a `/health` endpoint (#58552) and a readiness wait (#58370)". PR `gh api repos/vllm-project/vllm/pulls/58552` → title "[Fast Start] Add `/health` endpoint for the weight cache daemon", `merged true`, `2026-09-27T17:48:55Z`, `body` identical to the copy; body line 3 "Add an HTTP `/health` endpoint to the weight cache daemon parent process." and line 5 "… distinguish daemon startup from readiness." `curl` of `raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py` → sha256 `d2704e80…a57d`, equal to `.ufo/waves/round-43/c3/vllm-v0.31.0-preload.py`; lines 70-75 are `_build_health_app`, `@app.get("/health", include_in_schema=False)`, `return Response(status_code=200 if state.is_ready else 503)` — the entry's "one route, 200 or 503; the three states are the PR description's vocabulary" is accurate.
- Discernment note (D2): the process-attribution claim rests on S481 (tier C, "never sole support") plus the committed `preload.py` copy, which has no `SOURCES.md` row (`grep -c preload.py corpus/SOURCES.md` → 0); S480's own `teaches` cell says the release page "by itself does not say which process answers the route". Fleet validate flags this as `W01 S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md` — present in the lane's own `census-end-mirror.out`, but the report summarises that receipt as "93 W04, 0 E" (D3). The admission is substantively right (the code confirms it), so this is a registry-hygiene defect, not a disagreement.
- Score held 9.

### Separability and SCORECARD

Separability controls were not built (planned seat W2D08 was in the undispatched wave). From the file sets: C1 pins the C2/C3 counter blobs (it registers them), and C2's ledger carries the PR-58552 commit ids that C3's entry cites; otherwise the claims touch disjoint files. Each claim verified on its own evidence above. `git diff 3e6fdbe9 9307b15e -- SCORECARD.md`: all six scores held (operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7); depth row re-anchored to the new `SKILL.md` sha256 `542d6da2…` (1402 lines, 31 `## ` headings), coverage row to `PROVINCE.md` `36d6bb3a…`; capability list 8→9; the D1 misplacement is the only regression found.

## 3. Axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| calibration | improved | registry 16 unregistered → 0, 19 rows with 19/19 correct pins, spot count 28→29, README hidden entries, D-C corrected append-only; re-measured by me; D1 (tip-commit SCORECARD misplacement) routed |
| operability | improved | new `hexrun-census` capability; independent census reproduces 73 unexplained → 0 unknown; 5 upstream oids and the wrong row re-queried on GitHub; selftest 18/0 evidence-verified |
| coverage | improved | new entry on ground absent at base (0 → 5 files), both sources re-opened with bodies identical, `preload.py` re-fetched byte-equal |
| freshness | unchanged | no claim; score 8 held |
| depth | unchanged | no claim; score 7 held; `SKILL.md` grew only by registry rows |
| adjacency | unchanged | no claim; gateway (S442) and router (S443) refused as other processes, `PROVINCE.md` round-43 note keeps them out |

## 4. Discernment spot-check (LEARNING.md)

Sample of `corpus/lessons/round-43.md` `## Gate`: two admits, two rejects, plus one new-row quote check.

| Item | Decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| S480 (staged S430) vLLM v0.31.0 release notes | admit | `gh api repos/vllm-project/vllm/releases/tags/v0.31.0` | **agree** | 60454 bytes, body identical to the committed copy; quote "a `/health` endpoint (#58552)" (4 words) on body line 8 in the `vllm preload` / weight-cache daemon bullet; ground new to the lane (0 files at base); tier A docs for the release-level statement it is scoped to |
| S481 (staged S431, S441 collapsed) vLLM PR 58552 | admit | `gh api repos/vllm-project/vllm/pulls/58552` | **agree** | merged 2026-09-27; quote "Add an HTTP `/health` endpoint to the weight cache daemon parent process." (12 words) is body line 3; tier C kept conservatively; process claim also checked against `preload.py` at v0.31.0 lines 70-75 (re-fetched, sha256 equal). D2: the code copy should be a registered row |
| S440 vLLM health API reference at `stable` | reject (duplicate) | staged `merge/kama/SOURCES.append.md:117` vs lane `corpus/SOURCES.md:16` | **agree** | both rows carry the URL `https://docs.vllm.ai/en/stable/api/vllm/entrypoints/serve/instrumentator/health/`; a second row would double-count one page; flip named (S004 retired) |
| S438 vLLM PR 46811 `/ready` | reject (scope) | `gh api repos/vllm-project/vllm/pulls/46811 --jq '[.title,.state,.merged]'` | **agree** | "[Frontend] Add low-overhead /ready GPU health check", `open`, `merged false`: an unmerged proposal for another process's route; `grep -c 'S438\|S440' preregistration.json` → 0; flip (merge + in-tree copy) is concrete |
| New `corpus/SOURCES.md` row S481 (quote check) | admit | row at `corpus/SOURCES.md:234` | **agree** | anchor quote "Add an HTTP `/health` endpoint to the weight cache daemon parent process." is 12 words (≤25), located at §Purpose, and found verbatim in today's fetch |

Registry validate: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit **0**, 93 `W04`, 1 `W01` (S481, D2/D3), 0 `E`, `ok`. It now reads the tip (the parked worktree is at `9307b15e`). `census --file kama-shokunin/corpus/SOURCES.md` → rows 222, tier A 211, B 7, C 4, mined 203, queued 8, rejected 11, missing 0 (equals the report).

## 5. Trend verdicts

- **expansion: improved.** One admitted entry on uncovered ground (`runtime-health-surface-processes.md`, base 0 hits), citing two `mined` rows (220 → 222), one new capability (`hexrun-census`), and the staged-refusals ledger. No admitted entry fails its bar on re-check (section 2, C3).
- **quality: unprovable-but-better.** Better, on my re-check: the registry gate is green for the first time since round 35 and the documented gate selftest line is true again; D-C is corrected append-only; two wrong hex citations are flagged with their correct tokens; the entry's first draft was corrected by source reading and its 200/503 sentence matches the code. Not `improved` by the trend's definition: no entry was superseded, and the lane found held-entry defects (`served-model-id-resolution.md:46` → absent `CANNOT-ANSWER.md`; eight held sentences needing the process qualification) that it recorded in the lesson but did not mark in the entries; and the tip commit introduced D1. No falsify wave attacked the claims. Reviewer: this closure (non-author).
- **discernment: improved.** The spot-check agrees with the Gate on both admits and both rejects; the rejects name scope or duplication with concrete flips; of the round-42 routed items, 1, 3 and 4 are fixed, 6 is narrowed with a prototype, 2 is re-proved open by the wave's own falsifiers and disclosed, and 5 is operator-owned. D2 is a registry-hygiene finding, not a disagreement with a gate decision.

## 6. SHONEN

All four boxes remain `[~]`. Box 2 (end-to-end task) gains an independently reproducible run: my census reproduces `tools/hexrun-census.py scan` exactly at the measured commit. Box 1 and box 3 are partly supported by the 19 registry rows (I checked pins and exit-code presence, not every flag against `add_argument`). None is fully checkable by a non-author from this round alone; promotion stays operator-owned and no `[x]` is written.

## 7. Routed defects for round 44

1. **D1 (lane, calibration):** `SCORECARD.md:53-67` — the round-43 measured-results block sits inside the `## Planned` pointer sentence (a first-occurrence replacement of `### Planned (round 44)`). Restore line 53 to point at `### Planned (round 44)` and give `### Round-43 measured results` its own heading before `### Planned (round 44)` at the end of the file (append a correction note in §Round 44; do not rewrite cited text silently).
2. **D2 (lane, discernment/registry):** register the `vllm/entrypoints/cli/preload.py` at tag v0.31.0 code source (committed copy `.ufo/waves/round-43/c3/vllm-v0.31.0-preload.py`, sha256 `d2704e80…`) as its own `code`/A row and cite it from the entry's `source:`, so the process claim is not resting on tier-C S481 plus an unregistered file; clears validate `W01`.
3. **D3 (lane, report accuracy):** the report and lesson summarise `census-end-mirror.out` as "93 W04, 0 E"; it also carries one `W01`. State every warning class.
4. **D4 (lane, evidence):** commit a tip-side `gate-registry-check.py --selftest` receipt; the documented `GATE_SELFTEST pass=6 fail=0` currently rests on the C1 counter's `selftest=0` leg only.
5. **D5 (lane, cosmetic):** the two round-41 rows in `SKILL.md` §Round-43 registry completion read `sha256 \`<hex>\`\`` (stray backtick); ledger note for `a7361db0…` has `2026-10-25:T08:05:18Z`.
6. **Carried (lane):** counters prove facts, not sufficiency (W1R01, W1R02, W1R03: 20 of 53 mutants survive); the undispatched falsify wave and separability controls; the held-entry defects the wave found (`served-model-id-resolution.md:46`; eight sentences needing the process qualification) should be marked or corrected; `base-unresolved.tsv` has no in-repo producer (lesson N2).
7. **Operator:** the parked worktree is now attached at the tip and clean; L0 `kama | round-41/42/43` (parked-worktree disposition) can be answered or closed. The round-43 re-dispatch question (38 seats, no falsify wave) is the orchestrator's.
