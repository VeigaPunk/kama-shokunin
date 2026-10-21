VERDICT: confirm - no pinned measurement breaks at a29bb84; the gate selftest count is the only measured output that changes (6+1/77 -> 9+1/90), and an untracked round-21/build/ directory still blocks the official runner

# RevengeGateConsumers (round 21, BUILD advice; revenger leaf, no dispatch)

Scope: every consumer of install_tree / install_tree_sha256 / install_links and of the gate selftest count, at base 7a6bc911 and draft a29bb84. Lane not modified; scratch clones removed (`rm -rf` exit 0). Evidence: `.ufo/waves/round-21/build/out/RevengeGateConsumers/` (commands.txt lists each command and exit; consumers-core.tsv; consumers-tracked.tsv; recipe-replay.tsv; receipt-verdicts.tsv; selftests.tsv; inflight-machine-consumers.tsv; raw/).

## 1. What changes on rerun at a29bb84 (executed, both revisions)
- `check-receipt.py --selftest`: `6 VALID + 1 NOT-EVALUATED, 77 mutations` -> `9 + 1, 90 mutations`; exit 0 both. Text only.
- Recipe replay, 19 lane-bound rows: every exit equals the recipe's expected exit. Stdout differs only by gate count, temp-dir names (grid rows), clone path (citation-count, gguf-measure) and the `--to` HEAD string (append-round). Normalized, all identical except the count.
- Producer: every new receipt gains `install_links` / `install_links_sha256` (draft L1230, L1294, L1308-1309). `install_tree` body (L178-202) is untouched; real install still 51 entries, `6c216313...`.
- Gate: `install_links` checks (L441-477) are skipped when the field is absent. All 21 committed receipt-named JSON keep the same verdict and exit.

## 2. Pinned measurements: none breaks
| Pin | Location | At a29bb84 |
|---|---|---|
| 21 recipe exit codes (recipe sha fdac0eaf...) | .ufo/waves/round-20/recipe.json | hold for 19 lane-bound rows; 2 `sources-*` rows argv-pin the fleet root, not clone-bound (exit 0 live) |
| `--tree-sha 6c216313...` | recipe grid-tree-pin | holds: real install tree unchanged |
| `--tool-sha 83eac5c0...` | recipe grid rows | holds: equals round-18 receipt-1 `tool.sha256`. Gate compares only that field (check-receipt.py:530-536), never the live file |
| FROZEN_SOURCE_SHA256 GRID 6f51803c..., CITATION 5c887572..., SURVIVORS ac934794... | tools/error-verdict-census.py:33-37 | holds: checked against `git show` at FROZEN_REV 37bd4c5 (:315, :421). Working-tree grid d9689c07... differs by design |
| freshness check, installed tree vs round-18 receipt-1 | round-20 FreshnessS039 (read-only) | exit 0, 16 match, 0 mismatch |
| "77 mutations" text | runs/{9add96e4,04de7a87,c7311039,0957ce61}, SelftestsAtCommit/*, RegReceiptSixPin, round-19 final-selftests; SCORECARD.md:906; corpus/lessons/round-20.md:153 | historical at their commits. Nothing parses the count; run.py:56 compares exit only |

## 3. Latent breaks (verified; none in committed pins)
1. Re-pinning the grid to the current tool file breaks it: `--tool-sha c05cd8bf...` against round-18 receipt-1 gives baseline INVALID, exit 2 (receipt holds 83eac5c0...). Keep recipe pins at the receipt value; a re-pin needs regenerated receipts.
2. Lane state, observed at scan time: ` M tools/kama-llamacpp-live.py` (one blank line, sha 7de1e81e..., committed c05cd8bf...). At my final check that edit was gone and the producer matched the committed blob; I did not touch the lane. The untracked `.ufo/waves/round-21/build/` remains, and any untracked entry makes round-20 `run.py` refuse (exit 2, no out dir; reproduced in scratch with one untracked file). Round-18 `runs/run.py` has the same guard (L8-17). The producer hashes its own file (L1332), so a live run from a dirty tree records that file's hash [INFERENCE: live not run].
3. Pre-existing silent skip, base and draft: `install_tree` (L190-199) and `install_links` drop any entry that raises OSError, and the digest covers the rest with no error. Reproduced: a chmod-000 regular file vanished (keys `['llama-server']`). Not introduced by a29bb84; C2's "fail closed" needs this fixed.

## 4. In flight (untracked; not in the commit)
- `build/out/LinksDigestFix/patch.diff` applies to a29bb84 (exit 0). Scratch result: gate 9+1/93, producer selftest exit 0, links grid 12/0, install-tree grid 0. Real-tree digests unchanged (6c216313..., b58f1b4d...), so pins made at a29bb84 survive it.
- 103 untracked round-21 machine-type files mention these terms (snapshot of 608 files, 184 with a mention). None is in a committed recipe; they become consumers only if integrated.
- No committed file holds the draft gate sha (01fbf813...) or the draft tool sha (c05cd8bf...). A pin to either can only land in a later commit.

## 5. Consumer counts
- Tracked, `git grep` at a29bb84: 456 lines in 127 files (402 in 126 at base). Categories: prose 164; gate code 62; grid/controls code 30; build copies of code 50; frozen copies 45; build outputs 35; orchestration 23; live receipts 22; run records 13; producer 11; census 1.
- Excluded: `.jj/` and `.ufo/interactive-sessions/` (git-ignored, not committed: op store and transcripts).

## 6. Calls for L1 (not done by me)
- Commit or ignore `.ufo/waves/round-21/build/` before any official run; the runner refuses on any untracked entry.
- Record 9+1/90 in the round-21 SCORECARD/lesson; leave round-20 rows unchanged.
- Keep the recipe's `--tool-sha` at the receipt value.

Confidence: high for exit, verdict and digest facts (executed at the cited revisions). [INFERENCE] only where marked. Installs or updates: none (python 3.14.8 and git 2.56.0 pre-existing; stdlib only). Live llama-server, live producer runs and the round-18 runner were not executed.
