# R1Sample — round 47, lane kama — ground-truth hand sample of append-only-audit v2

**Verdict: no defect — for 10 seeded-random events (and an independent recompute of all 91 events at threshold 1) my by-hand derivation of `deleted`, `restored_max`, `restored_best`, `restored_by` and `status` agrees with v2 on every field; deleted counts equal `git numstat` everywhere; zero hand-vs-v2 differences.**

Measured commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (the frozen build; lane HEAD `46a924e027f05614558c45ff02bf7a94ca57d3e1` has drifted past it, but `git -C <clone> diff --stat 3a09a1d HEAD -- tools/append-only-audit.py registry/append-only-contract.tsv` is empty, so the HEAD tool run at `--to 3a09a1d` is the measured build).

## Commands and exit codes

- Clone (my own, in scratch): `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r47/R1Sample/lane` → toplevel asserted = clone dir.
- Audit (the item's command): `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo <clone> --to 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --contract /home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-contract.tsv --threshold 1 --json` → exit **1**, schema `append-only-audit/v2`, 303 commits, 85 files, 91 events (12 restored / 8 partial / 71 unrestored). Exit 1 is correct: partial and unrestored events exist.
- Hand derivation: `python3 handcheck.py` (copied to the out dir; independent code, imports nothing from the tool) → exit 0, sampled mismatches 0, all-91 mismatches 0.

## Method (what "by hand" means here)

For each event `(C, F)` I recomputed, without importing any tool code:

1. `deleted`: the deleted lines reconstructed by slicing the **parent blob** with each `-U0` hunk header's old range (a different reading than the tool's `-`-body parse at `tools/append-only-audit.py:146-171`), cross-checked two more ways: a `-`-body parse of the same diff, and `git diff --numstat --no-renames C^ C -- F`. All three were asserted equal per event; no assertion fired on any of the 91 events.
2. `K` = parent-line multiset minus the deleted multiset (containment asserted).
3. Window = `C` and every later commit of `git rev-list --topo-order --reverse <to>`; `held(x) = Σ_l min(D[l], max(0, M_x[l] − K[l]))` with `M_x` read as the actual blob of `F` at **every** window commit (one `cat-file --batch-check` per event, no history simplification).
4. `restored_max` = max held over the window; `restored_best`/`restored_by` = first window commits attaining it / attaining `|D|`; status per the frozen docstring (`tools/round47-append-audit-v2-check.py:40-46`).

## Seed and the 10 sampled events

`random.Random(47).sample(events, 10)` — seed **47**, from the 91 threshold-1 events:

| # | commit | file | deleted | restored_max | status | hand vs v2 |
|---|--------|------|---------|--------------|--------|------------|
| 1 | `fd48f9a3` | SCORECARD.md | 6 | 0 | unrestored | match |
| 2 | `ea72c3ea` | corpus/README.md | 3 | 0 | unrestored | match |
| 3 | `54c6f4fe` | corpus/SOURCES.md | 4 | 0 | unrestored | match |
| 4 | `8bc8e375` | corpus/SOURCES.md | 1 | 0 | unrestored | match |
| 5 | `5890d1a0` | corpus/SOURCES.md | 7 | 7 (`df61204c`) | restored | match |
| 6 | `dabc6eee` | SCORECARD.md | 1 | 0 | unrestored | match |
| 7 | `f4066979` | LOG.md | 3 | 0 | unrestored | match |
| 8 | `028235e6` | corpus/lessons/round-18.md | 1 | 0 | unrestored | match |
| 9 | `dd9f5dc6` | SCORECARD.md | 31 | 24 (`dd9f5dc6`) | partial | match |
| 10 | `4d2e74f4` | corpus/lessons/round-27.md | 5 | 0 | unrestored | match |

Full per-event evidence (deleted lines shown, held trajectories, hand-vs-v2 lines) is in `handcheck2.out` in the out dir. Representative derivations:

- **#5 `5890d1a0` corpus/SOURCES.md** — 7 deleted lines (blank line + source rows S196, S205, S206, S209, S223, one more), e.g. `- | S196 | vLLM \`vllm serve\` CLI reference — https://docs.vllm.ai/en/v0.17.0/cli/serve/ | ...`. Held trajectory: `5890d1a0 held=6` (six of the seven lines re-added in the same commit's file state), `df61204c held=7` (the last one) → restored_max=7, best=by=`df61204c`, restored. v2 identical.
- **#9 `dd9f5dc6` SCORECARD.md** (the brief's headline partial) — 31 deleted lines from the round-5 authority block (e.g. `- **Current authority (actual round 5, blocked attempt):** assigned LIVE axes`). Held trajectory: `dd9f5dc6 held=24` → `0718b6ab held=0` → `82b5e9d3 held=24`. Window max = 24 < 31 → partial with `restored_best=dd9f5dc6`, `restored_by=null`. v2 identical — the window-max definition demonstrably refuses to lower a restoration when `0718b6ab` re-deletes the lines (round-46 D2 behavior).
- **#1 `fd48f9a3` SCORECARD.md** — 6 deleted lines (e.g. `- the report-landing auditor; this round works depth on the serving runtime.`), none of the six texts ever reappear in any window blob (held=0 at all 303-window positions) → unrestored. v2 identical.

## The one near-miss (my bug, not v2's) — worth recording

My first checker cached `M_x` across commits listed by `git rev-list <to> -- path` (history-**simplified**) and flagged `1e41928a SCORECARD.md` as a v2 difference (I said unrestored; v2 said restored at `1e489406`). Hand interrogation:

- `1e41928a` deletes 2 lines: `- | — none yet — | | | |` and `- The lane's saturation line and stagnation window N are to be declared by the lane on its next round per \`AXES.md\` ...`.
- `1e489406`'s parent is `69780977` — `1e41928a` is **not** an ancestor of `1e489406` (parallel branch; `git merge-base --is-ancestor` fails). Blob at `1e41928a` is `272aa0e6` (neither line present), blob at `1e489406` is `532c5a37` (both lines present again).
- Topo order puts `1e489406` after `1e41928a`, and the frozen window is "the event commit and every later commit of the rev-list", so the parallel-branch restoration counts. Held trajectory: `1e41928a held=0` → `1e489406 held=2` → `2f7303c2 held=0` (deleted again later; the window max keeps 2). Corrected derivation: `restored_max=2 restored_best=restored_by=1e489406 restored` — exactly v2.

So v2 is right per the frozen contract; my shortcut (simplified touching set) was wrong. The tool avoids it by resolving the blob at every window commit (`tools/append-only-audit.py:206-232`, `Repo.blobs` at :174). **Observation, not a defect against the frozen docstring:** the window includes non-descendant commits, so a restoration can be credited from a parallel branch that later gets deleted again (`2f7303c2`); this is the documented window semantics, but anyone reading "restored" as "still present at tip" should note it.

## Aggregate cross-check

- All 91 events recomputed with the corrected machinery: **0 mismatches** on all five fields.
- The threshold-20 subset of my run is exactly the brief's 5 events, same numbers: `dd9f5dc6 SCORECARD 31/24 partial`; `0718b6ab LOG 2292 restored`, `SCORECARD 2421/2420 partial`, `QUALITY 375 restored`, `README 663 restored` → exit 1 consistent.

## Residual risk and verification gaps

- My recompute shares the **frozen v2 definition** (docstring); the only definition-independent ground truth exercised is `git numstat` for deleted counts (matched on all 91) and the two independent deletion readings agreeing. Line identity and restoration semantics are definition-internal — but that is what the item asked me to sample, and the counter's fixture leg covers the constructed cases (CRLF, `--`, duplicates, no-final-newline), which I did not re-derive here (out of my item's scope).
- The known preregistered limit stands: contract coverage is only as good as its declaring lines; a declared-but-unlisted file is undetectable by this instrument (attacked by other seats, not re-tested here).
- Tooling installs: **none** (no pacman, no new tools; python3 and git only).

## Evidence files (also the answer's absolute paths)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R1Sample.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R1Sample/audit.json (the tool's v2 JSON, threshold 1, 91 events)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R1Sample/handcheck.py (my independent deriver)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R1Sample/handcheck2.out (per-event evidence, seed, aggregate result)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R1Sample/parallel_case.out (the 1e41928a parallel-branch derivation)
