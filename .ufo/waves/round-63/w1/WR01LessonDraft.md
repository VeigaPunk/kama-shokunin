# WR01LessonDraft — round 63 lesson draft (kama)

Seat: WR01LessonDraft (scribe, leaf, no subagent dispatch). Tip under test `03a6a1d850902a66a13dfad33f89cf3a8b759a09`; base `7ee8cbdf160f8c945954e4737e7a2f797e3b2987`; freeze `.ufo/waves/round-63/controls/freeze.txt` (AMENDMENT 1 read).
Draft: `.ufo/waves/round-63/w1/out/WR01LessonDraft/round-63-lesson.md` (landing text; not copied to `corpus/lessons/`, which is the L1's step).
Receipts: `.ufo/waves/round-63/w1/out/WR01LessonDraft/` (see Evidence below).

## Provenance deviation (read first)

- The item says to take gate quotes only from the SC01/SC02/SC03 seat reports. Those seats were never run: `.ufo/waves/round-63/w1/swarm-registry.json` lists `SC01ServerTask`, `SC02TokenizeDoc`, `SC03Considerthese` with `agentId: null`, and agent spawning is disabled in this session. No SC report exists under `.ufo/waves/round-63/w1/` or `out/`.
- Instead of inventing quotes or leaving the gate empty, WR01 opened the three sources itself, fetched the pinned raw files with `curl` from `raw.githubusercontent.com` at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` into scratch, and verified each quote against those bytes by line number. Hashes match the saved copies and the registry rows (see Evidence). The lesson says so and marks the gate for L1 re-check.

## Findings

1. **Round-62 C2 counter: controls are credited under a failing baseline, and scoring errors are excluded from `errors`.** Verified by reading `tools/round62-c2-counter.py` (controls 292–348, `met` 420–426, `facts['errors'] = len(parse errors)` line 200, `err_list` 201–241). A stubbed-live harness reproduces the measured `c2-final.out` (`mismatches=4 controls_rejected=8/8 errors=0 met=False`) exactly. With a clean baseline the same counter gives `controls_rejected=7/8` and lets the `free` control escape (an unbound always-green echo row, whose error only lands in `err_list`). Fixed in `tools/round63-c2-counter.py` (lines 280/331 count scoring errors; 526–527 withhold control credit unless the baseline is met). Open: the round-63 control set has not been checked for an analogue of the `free` escape; that belongs to the attack seats.
2. **Round-62 sensitivity expression is vacuous for every real pattern.** `tools/round62-c2-counter.py` 270–271 measured with the verbatim expression: 0 of 12 manifest patterns are `sensitive=false` (`sensitivity-real-patterns.out`). A05's case (`P='a'`) is degenerate. The round-62 lesson's "false by construction for any nonempty pattern" overstated the mechanism; the new lesson corrects it. The r63 counter replaces it with `verdict_fn`/`strip_all`/`is_sensitive` (215–243) and a 4-plant selftest (`EXPECT_SELFTEST = 4`, line 122; selftest at 250); the old expression survives only as a witness (244–247).
3. **Ollama nonce `ctrun` is rejected before any child starts.** `tools/kama-ollama-live.py` `NONCE_RE = ^[a-z0-9]{8,32}$` (lines 69, 109) and the check at 315–317. Run with `--nonce ctrun`: `verdict SETUP_ERROR`, `setup_error nonce-invalid`, `checks []`, exit 2, no server (`ollama-ctrun-receipt.json`). The r62 row (`registry/capability-claims-r62.tsv` line 13) could not have produced `"verdict": "MODEL_OK"`. Repaired to `ctrun0001` in `registry/capability-claims-r63.tsv` line 13. WR01 did not run the repaired row (a live child; left to the C2 counter). Attribution of the four r62 mismatches to this row is `[INFERENCE]`: `c2-final.out` carries no per-row output.
4. **Hexrun `unknown` from a closure-cited fleet hash: mechanism verified for round 62.** The round-62 spot-check cites `795b7be59e908caae6198c1e953c8ca587ea1a11` (line 7), introduced in commit `307466ca`. Read-only census: `307466ca` and base `7ee8cbdf` give `unknown=1`, exit 1, `795b7be… class=unknown`. Tip `03a6a1d8` gives `unknown=0` with `795b7be… class=upstream_ok`, because of `registry/hexrun-ledger.tsv` line 125 plus `.ufo/waves/round-63/census/fleet-commit-evidence.json`. `cat-file -t` on the fleet repo says `commit`. Archived earlier rounds show `unknown>0` (r46 26→21, r47 1, r49 2, r50 1, r51 2, r53 1) but kept no per-token detail, so their cause is `[INFERENCE]` and not claimed.
5. **Registry state at the tip differs from the working tree.** `corpus/SOURCES.md` at the tip ends at S526; the working tree adds S527 (`server_task_result_cmpl_final::to_json_oaicompat`) and S528 (`server_slot_stats::to_json`) as uncommitted rows. `PROVINCE.md` and `corpus/knowledge/completion-request-plane.md` are also modified in the working tree. The lesson therefore treats S527/S528 as candidates, not admitted rows. WR01 did not touch those files.
6. **SC02 claim (`usage.prompt_tokens` = `/tokenize add_special=true` count) has no docs support** at the pinned README. The `/v1/completions` section (1314–1344) has no usage or BOS statement; the BOS rule (500–503) is in the `/completion` section. Keep it observation-only, as the knowledge file already does.

## Evidence (all under `.ufo/waves/round-63/w1/out/WR01LessonDraft/`)

- `controls-vacuity.out` — harness output (`vac_demo.py`): clean baseline 7/8, escape `free`; 4-mismatch baseline 8/8, errors=0.
- `sensitivity-real-patterns.out` — `sens_demo.py`: 0/12 manifest patterns sensitive=false; A05 toy case False; `P='ab', out='aab'` True.
- `ollama-ctrun-receipt.json`, `ollama-ctrun.stdout`, `ollama-ctrun.stderr` — lane tool run with `--nonce ctrun`.
- `hexrun-tip.stdout|details`, `hexrun-af33.stdout|details`, `hexrun-307466ca.stdout|details`, `hexrun-7ee8cbdf.stdout|details` — read-only census at four revisions.
- `pinned-sha256.txt` — fetched `README.md` `714c067b…` (matches S526 raw sha); `server-task.cpp` `4c3f413b…` (matches saved copy and S527 sha); `server-common.cpp` `b4f4aae7…` (matches saved copy; fetched and hashed, not separately stored).
- `r63c2-tip.py` — blob copy of `tools/round63-c2-counter.py` at the tip, for the line citations.
- Harness copies `vac_demo.py`, `sens_demo.py` (both run with `python3 -B`, no bytecode written into the lane).

## Commands run (WR01, read-only or in scratch)

- `cat .ufo/waves/round-63/controls/freeze.txt`; `cat corpus/lessons/round-62.md`; `cat corpus/lessons/round-62-verifier-spotcheck.md`; `cat .ufo/waves/round-62/w1/A05C2Sensitivity.md`.
- `git show 03a6a1d8:<path>` for counters, registries, `SOURCES.md`, `kama-ollama-live.py`; `git status --porcelain`, `git diff --stat`, `git log --oneline`, `git cat-file -t/-e`, `git rev-parse`.
- `python3 -B tools/hexrun-census.py scan --repo <lane> --rev <rev> --details` (four revisions, read-only).
- `python3 -B tools/kama-ollama-live.py --work <scratch>/ollama-ctrun --nonce ctrun --out <scratch>/ollama-ctrun.json` (exit 2, nonce-invalid, no child).
- `python3 -B vac_demo.py`, `python3 -B sens_demo.py` (import `tools/round62-c2-counter.py` via importlib; `controls()` run with a stubbed live scorer; no repository writes).
- `curl -sSfL` of three pinned llama.cpp raw files into scratch; `sha256sum`.
- `git -C /home/vgpnk/Projects/shokunin cat-file -t 795b7be…` → `commit`.

## Tools installed or updated

None. Pacman not used.

## Lane observations (not acted on)

- The lane working tree is dirty: modified `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/completion-request-plane.md`; untracked `.ufo/waves/round-63/source/`, `w1.ready*`, `w1/`, and an empty untracked directory `kama-shokunin/` in the lane root (`ls -la` shows no entries). Not mine; the L1 should decide ownership before landing.

## Scratch and state

- Scratch `/fast/scratch/hyaku/kama-r63/w/WR01LessonDraft` is removed after receipts were copied.
- No commit, push, or mutating git/jj command was run anywhere. Lane and fleet files were not edited; the only write is the draft and this report.

## Tally

`hexrun-census.py scan --rev 03a6a1d850902a66a13dfad33f89cf3a8b759a09` → `tokens=2071 distinct=399 lane_oid=277 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0` (exit 0).
`round62 controls() baseline-as-measured` → `controls_rejected=8/8 errors=0 mismatches=4` (reproduces `c2-final.out`); `clean baseline` → `controls_rejected=7/8` (escape `free`).
