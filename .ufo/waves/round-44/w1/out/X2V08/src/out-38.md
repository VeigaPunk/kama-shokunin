# kama round 38 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_flash)
round: kama 38 (attempt 2; watchdog digest 1290–1301)
date: 2026-10-25
judged lane state: origin master `ce41bae692c86d7b9f56cec8466157673c3bed4e` (scratch clone `/fast/scratch/hyaku/kama-r38-closure`); report commit `f8116dcd64114fdc9f9776a84949062b5ba420b4` (fleet repo)
base: `2a4a97dc890fe393035986c951797c5d65b6cc69` (round-37 verifier spot-check); reported tip `d854475aecc1d793f84c10021daaed46f735f270`; frozen `41e149ceee28b24596b5d8567a0ccf43ebbc6d50`

## 1. Conformance

| check | result |
|---|---|
| report committed by lane identity in fleet repo | OK — f8116dcd author AND committer `kama-shokunin <kama@shokunin.local>` |
| report has `SHONEN` heading, one `[~]` line per box with pointer | heading present, 4 `[~]` lines with pointers; DEFECT: lines assess per-axis outcomes, not the repo's four SHONEN.md boxes (SKILL.md content / E2E task / executable instructions / no cross-domain bleed) |
| cited lane commits exist | OK — 6a4afdfe, 2a4a97dc, 41e149ce, 2f780765, 7c5a584, 54e2952, d854475a, ce41bae6 all present |
| cited commits are ancestors of branch ref | OK — `git merge-base --is-ancestor <h> master` true for all cited hashes |
| no uncommitted round-38 work in lane repo | OK — `git status --porcelain` in parked worktree shows only pre-round-38 leftovers (r35/r36 wave files; untracked `.ufo/waves/round-37/`); `find … -newermt 2026-10-25T06:04` empty |
| pushed | OK — `jj-lane.sh state`: `ahead=0`; origin `refs/heads/master` = ce41bae6 contains the round-38 work (note: local remote-tracking ref in parked worktree is stale at 6a4afdfe; true origin verified by ls-remote) |
| prompt carries template contract | OK — dispatched prompt `.ufo/prompts/kama-round-38.md` embeds mission/axes binding, claim rules, frontier step, L2 floor (≥8 batched), commit-then-push, push scope, L0 side channel, report path, commit-before-report ordering, SHONEN heading requirement, hash-citation rule, write scope |
| watchdog digest | matches prompt lines: 1290 launch attempt 1, 1293 lane-dead-no-report, 1294 launch attempt 2, 1301 complete |
| report minimum content | work performed, evidence pointers, before→after per claim with counting command + measured commit, frontier census, trend verdicts, SHONEN — present; DEFECT: no literal `Landed changes` / `Before → after measurements` headings (substance present under Claims/Work performed) |

Status: `ok`.

## 2. Claims — re-measured (all on committed bytes; no sibling gate executed)

All counters run from the scratch clone at origin master `ce41bae6` (identical results at reported tip `d854475a`).

| claim | command (run at tip) | observed output | exit | reported | re-check |
|---|---|---|---|---|---|
| C1 | `python3 tools/round38-statement-audit.py --repo /fast/scratch/hyaku/kama-r38-closure --tip ce41bae6` | `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` / `note: staged rows present` | 0 | `met True`, exit 0 | MATCH |
| C2 | `python3 tools/round38-coverage-audit.py --repo /fast/scratch/hyaku/kama-r38-closure --tip ce41bae6` | `named 2 files_exist 2 cited_new 3 met True` / `new ids: S352, S353, S472` | 0 | `met True`, exit 0 | MATCH |
| C3 | `python3 tools/round38-operability-audit.py --repo /fast/scratch/hyaku/kama-r38-closure --tip ce41bae6` | `found 2 base_found 0 help_ok 2 rerun_ok 2 report_37 1 receipt_ok 1 met True` | 0 | `met True`, exit 0 | MATCH |

Controls reproduced at base `2a4a97dc` with the same counters (met False, exit 1): C1 `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`; C2 `named 0 files_exist 0 cited_new 0 met False`; C3 `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False`. Committed control files `.ufo/waves/round-38/controls/{c1-noop,c2-base,c3-base}.out` and after-receipts `.ufo/waves/round-38/{c1,c2,c3}/after.out` are byte-identical to my runs.

Cross-checks: r37 lesson blob at tip = `20f7909b6c8161f2bcc868a4472585733c81ae83` = C1 `LESSON_BLOB`; fleet HEAD `.ufo/reports/round-37/kama.md` blob = `1c6ea9faa0e25d48f70d354e0a140bcb709ca7db` = C1 `REPORT_BLOB`; staged package `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` lines 9/13/14/15/16 carry S332/S336/S337/S338/S339; w1 registry has 36 seats with roles reviewer 8, scout 9, critic 4, scribe 5, executor 5, mutation-tester 3, connector 1, revenger 1; `seat-exit-codes.json` has 36 members.

### Per-axis verdicts

| axis | score | verdict |
|---|---|---|
| calibration | 7 → 7 | improved (C1: routed uncorrected statement corrected by append; counter re-derives the fact) |
| coverage | 9 → 9 | improved (C2: two admitted entries on ground the map did not hold, three new mined rows) |
| operability | 8 → 8 | improved (C3: r37 counters reproducible from landed bytes; 37th seat report + receipts land) |
| freshness | 8 held | unchanged (no claim; 90d recheck run) |
| depth | 7 held | unchanged |
| adjacency | 7 held | unchanged |

`git diff 2a4a97dc..ce41bae6 -- SCORECARD.md` appends the round-38 section only; no prior score row changes → no axis harmed.

## 3. Discernment spot-check («LEARNING.md» — sample from `corpus/lessons/round-38.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S352 (admit) | admit | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/radix_eviction_policy.mdx` | agree | HTTP 200, 6243 bytes, sha256 `4ba2e6210d27ed1de045ae5b6aad9e475f9a7debdd64671178c04193c560876b` match; quote at line 13 byte-exact: "The policy scores each candidate and the **lowest score is evicted first**." |
| S353 (admit) | admit | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/session_radix_cache.mdx` | agree | HTTP 200, 2820 bytes, sha256 `0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd` match; quote at line 9 byte-exact: "Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient." |
| S472 (admit, own-work) | admit | `git ls-remote --tags https://github.com/sgl-project/sglang.git` (rerun) | agree on substance / disagree on cited digest | rerun exit 0, 190 lines, `refs/tags/v0.5.22` = tag `35ce313293052f8362e0829e7512bc9bc3d336c9` peeled to `baa9befa381511cd4d56f83980951e5a45fffc6d`, no v0.5.23/v0.5.24; output byte-identical to committed evidence `.ufo/waves/round-38/assimilation/exec-tag-inventory/ls-remote-tags.txt`. DEFECT: row, amendment and lesson cite sha256 `5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2`, which is not the digest of the committed evidence nor of the rerun (actual `5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2`). |
| S360 (reject) | reject | `https://api.github.com/repos/sgl-project/sglang/tags?per_page=20` | agree | rerun: HTTP 403, `x-ratelimit-remaining: 0` — anchor not reproducible on this host; flip condition reasonable |
| wave-1 reject `runtime-health-surface-matrix-amendment-2026-10-24-r7.md` (S396) | reject | staged entry `merge/kama/knowledge/corpus/knowledge/runtime-health-surface-matrix-amendment-2026-10-24-r7.md` + lane S329 row | agree | staged S396 URL = lane S329 URL exactly (`…/python/sglang/srt/entrypoints/http_server.py` @ v0.5.22); one-URL-one-row reject is correct |
| new SOURCES row quote (≤25 words, located) | — | S352/S353 rows in `corpus/SOURCES.md` | agree | quotes word-count within cap; locations (line 13 / line 9) verified |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, 93 W04 warnings, no E findings; same on the landed registry (`--file /fast/scratch/hyaku/kama-r38-closure/corpus/SOURCES.md`) → exit 0, 93 W04. Matches report ("census start and end both exit 0; warnings 93").

## 4. Trend verdicts

- expansion: **improved** — two admitted knowledge entries on coverage-map ground the base did not hold, each `source:` citing a mined row (S352/S353/S472); README coverage block added; no row quota gaming (3 rows for 2 entries).
- quality: **improved** — the release-pinned revision rows (S352/S353) are stronger anchors than the unversioned published-page rows S333/S334; rechecks are concrete commands with expected digests; no admitted entry failed its re-check.
- discernment: **improved** — outside spot-check agrees with the gate on all sampled admits and rejects; KQ47 criterion added with its lesson/evidence. One citation defect (S472 digest) is routed below as an evidence defect, not a gate-decision disagreement.

## 5. Routed defects (lane to fix next round)

1. S472 row + amendment entry + lesson cite a sha256 that does not match the committed evidence blob or a fresh rerun (actual `5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2`). Correct by a superseding row/recheck (append-only).
2. R36-D2C correction paragraph cites `SOURCES.append.md` sha256 `3ad0df68e8423a3b…` which matches neither current package bytes (`3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`) nor common variants. Correct the citation.
3. Wave evidence incomplete: `.ufo/waves/round-38/w1/spec.json` and `run.json` are cited in the lesson but absent from origin (only `out/seat-exit-codes.json` and `out/swarm-registry.json` are committed). Commit the wave spec/registry per the round prompt ("commit them as wave evidence").
4. Report `SHONEN` section lists per-axis lines instead of the repo's four SHONEN.md boxes (one-line-per-box contract). Re-file under the canonical boxes next round.
5. Report lacks literal `Landed changes` / `Before → after measurements` headings (substance present under Claims/Work performed) — align headings with the template.

Notes (non-defects): parked worktree still carries stale uncommitted r35/r36 material and an untracked `.ufo/waves/round-37/` dir (inherited; untouched by this round); MISSION.md:29 names kama axes "operability + freshness" while the prompt says "operability + calibration" — disclosed in the report, operator-side; the parked lane's remote-tracking ref is stale (state prints remote=6a4afdfe) though true origin master is ce41bae6 — the lane's pushes were verified by ls-remote.
