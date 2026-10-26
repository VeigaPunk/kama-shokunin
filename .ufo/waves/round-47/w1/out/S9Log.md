# S9Log — round-47 `## Round 47` LOG entry (scribe)

**Verdict:** draft complete and append-ready. Every freeze and build fact it states was re-checked read-only at `bbcc6dc2` (freeze) and `3a09a1d9` (build) from a private `git clone --shared`; the measured commit, both counter receipts, the b11909 source row and the wave/commit chain are left as grep-able placeholders, because the measurement and the integration have not happened yet and the L1's pre-wave dry run is not the measurement.

## Deliverable

- `.ufo/waves/round-47/w1/out/S9Log/log.md` — the `## Round 47` entry, ready to append at EOF of `LOG.md`. At the build `LOG.md` is 181762 bytes, ends in `\n`, and its last entry is Round 46, so the entry is a pure append (0 deletions) — which is the property `append-only-audit` v2 audits.
- Shape follows the round-46 entry: two claim bullets with motivating evidence, one routed/frontier bullet (freeze, build, wave), a measured-receipts paragraph, a wave/commit-chain paragraph, and the lesson line.

### Placeholders (16, all `__UPPER__` and grep-able)

| Token | Substitute with | Source |
|---|---|---|
| `__S_B11909__` | the SOURCES row id opened for b11909 | `corpus/SOURCES.md` after the integration append (228 rows at the build, 0 name b11909) |
| `__MEASURED_COMMIT__` | full 40-hex measured commit | the L1's measured commit |
| `__C1_MEASURED_LINE__`, `__C1_EXIT__`, `__C1_RECEIPT__` | C1 counter stdout line, its exit, its committed receipt path | `.ufo/waves/round-47/c1/…` |
| `__C2_MEASURED_LINE__`, `__C2_EXIT__`, `__C2_RECEIPT__` | C2 counter stdout line, its exit, its committed receipt path | `.ufo/waves/round-47/c2/…` |
| `__CENSUS_END__` | end-census summary (rows, W04/W01/E, exit) | `scripts/sources-census.sh validate …` at the measured commit |
| `__WAVE_SEATS__` | spawned seats / dead count / role mix | `.ufo/waves/round-47/w1/` results |
| `__WAVE_RESULTS__` | results json path | `.ufo/waves/round-47/w1/kama-r47-w1-results.json` |
| `__WAVE_LIMITS__` | counter limits the wave found (shortcut controls, mutants) | lesson §Mistakes |
| `__CLAIM_COMMITS__`, `__INTEGRATION_COMMIT__`, `__FINAL_TIP__` | lane commits | lane history |
| `__KQ__` | KQ numbers added | `corpus/QUALITY.md` |

## What I checked (read-only)

Private clone `/fast/scratch/hyaku/kama-r47/S9Log/lane` (`git clone --shared`); every command below ran against it. Nothing in the lane was written; no counter was run.

| Check | Command | Result |
|---|---|---|
| Commit chain is linear first-parent | `git rev-parse <c>^` for `bbcc6dc2 3a09a1d9 46a924e0` | `172b8ad0 ← bbcc6dc2 ← 3a09a1d9 ← 46a924e0`; `master = 46a924e0`, `git status --porcelain` empty |
| Counters frozen before data | `git show bbcc6dc2:{tools/round47-append-audit-v2-check.py,tools/round47-live-replay-audit.py} \| sha256sum` | `a180ab84…55ed`, `15408dce…8b0f` — equal to `claims[*].counter_sha256` in the preregistration |
| Shortcut controls all fail | `cat .ufo/waves/round-47/controls/*.out` | `base.c1`/`base.c2` and the three `junk-*` receipts all `met=False`, exit 1 |
| Freeze-time check | `git show 3a09a1d9:.ufo/waves/round-47/freeze/prereg-time-check.out` | `RESULT pass`, `exit=0` |
| Contract rows and their declaring lines | copy of `registry/append-only-contract.tsv` at `3a09a1d9`, each `declared_at` line read from its file | 7 rows (`LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md`, `registry/history/DELTA.md`); all 7 lines contain `append` (case-insensitive) — `receipts/numstat-recount.tsv` §2 |
| v2 expansion and lane events | `python3 <tool@3a09a1d9> --repo lane --to 3a09a1d9 --contract <contract@3a09a1d9> --json` | `files=85` (79 `corpus/lessons/*.md` + 6), `commits=303`, 5 events, `restored=3 partial=2 unrestored=0`, **exit 1** — `receipts/aoa2-lane-3a09a1d9.{json,txt}` |
| Event values at the build | same run | `dd9f5dc6` SCORECARD 31/24 partial; `0718b6ab` LOG 2292/2292 restored (`82b5e9d3`), SCORECARD 2421/2420 partial, QUALITY 375/375, README 663/663 restored |
| Independent ground truth (numstat) | `git log --no-renames --numstat --format='C %H' 3a09a1d9 -- <85 paths>` | same 5 events, deletions 2292 / 2421 / 375 / 663 / 31 — equal to the tool's `deleted`; this closes r46-D1 numerically — `receipts/numstat-recount.tsv` §1 |
| Stability (r46-D2) | same tool at `--to 172b8ad0` and `--to 3a09a1d9`, build contract (the counter's own `stable`-leg setup) | identical `deleted` and `restored_max` for all five events (`0718b6ab` SCORECARD 2420 at both); the v1 2416 → 2409 drop does not recur — `receipts/aoa2-lane-172b8ad0.json` |
| Tool selftest | `python3 <tool@3a09a1d9> --selftest --scratch <existing dir>` | `AOA_SELFTEST pass=15 fail=0`, exit 0 (cases include `dashdash-lines`, `crlf-and-eof`, `multiset`, `window-max`, `relocation`, `contract`) — `receipts/aoa2-selftest.out` |
| Replay selftest | `python3 <kama-live-replay.py@3a09a1d9> --selftest --scratch <existing dir>` | `KLR_SELFTEST pass=10 fail=0`, exit 0 — `receipts/replay-selftest.out` |
| C2 receipts | the three receipt blobs at `3a09a1d9` | each `kama-llamacpp-live/v4`, `outcome pass`, 11 checks, 11 passed, `build_info b11909-caa8191df`, asset sha `bf94332a…e695b`, member `llama-b11909/llama-server`, model sha `270cba1b…bd256d`, `teardown.log_path` null — `receipts/c2-receipts-inventory.tsv` |
| Release record | `.ufo/waves/round-47/c2/release-b11909.json` at the freeze | `tag_name b11909`, `target_commitish caa8191df159f764fb0160e3d2fc6be008948aee`, `published_at 2026-10-26T21:00:58Z`, `prerelease true`, asset 22475032 bytes `sha256:bf94332a…e695b` |
| Install record | `.ufo/waves/round-47/c2/live/install.txt` at the build | asset + url + extraction path, `version: 0.7.0-dev (build 11909, commit caa8191df)`, server sha256 `35ac50fb…7ff0`, model url + sha256 — `receipts/install.txt` |
| Start census | `.ufo/waves/round-47/census/start.out` at the build | `exit=0`, `93 W04`, `1 W01`; `corpus/SOURCES.md` has 228 `\| S` rows |
| Counter's anti-collusion guard | `grep -c round47` on the tool source | `0` (the lane-leg requirement that the tool not contain `round47`) |

Facts the LOG entry states but that are *not* re-derived here, and are cited as the closure's own text: the v1 numbers 2417/2421 and 2290/2292 and the 2416 → 2409 drop (`corpus/lessons/round-46-verifier-spotcheck.md:137`, `:84`, `:138`), Rev2Decl's `68 files, 292 commits` (`…/round-46/w1/out/Rev2Decl/contract.md`), and r45-D3's vanished model cache (`corpus/lessons/round-45-verifier-spotcheck.md:148`).

## Findings

1. **Nit (tooling, not a predicate): both selftests abort when `--scratch` does not exist.** `tools/append-only-audit.py:477` (`root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())`) and `tools/kama-live-replay.py:178` (same pattern, reached from `:256`) raise `FileNotFoundError: … '/…/sfx/aoa-…'` with a traceback and exit 1 when the caller names a directory that has not been created. Show it:
   `python3 <tool@3a09a1d9> --selftest --scratch /fast/scratch/hyaku/kama-r47/S9Log/sfx` → traceback, `exit=1`; `mkdir -p` the same path → `AOA_SELFTEST pass=15 fail=0`, `exit=0`. Proposed fix: `os.makedirs(root, exist_ok=True)` (or `parser.error`) before `mkdtemp`, in both files. Neither frozen counter is affected — `tools/round47-append-audit-v2-check.py:597-598` creates its root first — so this is not scored; it only makes a manual `--selftest` look broken.
2. **Expected exit 1, stated so it cannot be misread.** The v2 tool exits 1 at the build because two of five events are `partial`; both are the documented SCORECARD head re-derivations the contract's SCORECARD row exempts. The C1 predicate is the counter's five legs (which compare the tool against the counter's own recomputation), not the tool's exit 0. The entry says this explicitly.
3. **Documented limits carried into the entry, not softened:** v2 restoration is text identity (a line restored elsewhere in the file counts), and the contract only covers what its declaring lines name, so an undeclared append-only file is invisible — this is the attack surface the wave seats were pointed at. C2 is three sampled instants on one 260K model with check-by-check pass/fail equality, and the counter replays receipt-1 only.
4. **No lane inconsistency found** between the preregistration, the controls and the build: `before` lines in `claims[*]` match `controls/base.c*.out` byte-for-byte on the five legs each names, and the `release` block matches `release-b11909.json`.

## Out of scope (not done, by assignment)

- Neither frozen counter was run (measurement seats; C2 also needs ~23 MB from github.com and ~1.2 MB from huggingface.co per replay).
- No C2 network replay, no llama-server started, no services touched.
- No lane mutation: no `git add/commit/checkout/stash/reset`, no jj, read-only git only. No pacman transaction; no tool installed (python3 and git sufficed).
- No subagents, no `agent://all`.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Log/log.md` — the entry.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Log.md` — this report.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Log/receipts/` — `aoa2-lane-3a09a1d9.json`, `aoa2-lane-3a09a1d9.txt`, `aoa2-lane-172b8ad0.json`, `aoa2-selftest.out`, `replay-selftest.out`, `numstat-recount.tsv`, `append-only-contract.tsv`, `c2-receipts-inventory.tsv`, `install.txt`.
