# N2Couple — round 47 separability: C1 and C2 each verify without the other

Verdict: **Separable.** C1 and C2 share no read path except `corpus/SOURCES.md`, which C2 only appends to (additions, no deletions), so each counter reaches all its legs on a fixture containing only its own build, and neither a C2 SOURCES append nor a receipt commit changes a single C1 event (verified byte-identical). Both counters pass alone and together.

## 1. Paths each counter reads (from frozen counter code)

### C1 counter `tools/round47-append-audit-v2-check.py` (sha256 a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed)

All reads go through `git -C <repo>` on `--repo` (read-only), plus subprocess runs of the tool it extracts from the repo:

| Read | Where in code |
|---|---|
| `rev-parse --verify <tip>^{commit}` and `<base>^{commit}` (base default `172b8ad040d51ce8c011238c1408d4e0b6aa9595`) | main() lines 602-603 |
| `git show <tip>:tools/append-only-audit.py` (extracted to scratch, then executed) | main() lines 607-612; `TOOL` line 119 |
| `git show <tip>:registry/append-only-contract.tsv` | `read_contract` lines 241-261; `tip_contract` lines 358-362 (`CONTRACT` line 120) |
| `git show <tip>:<declared_at path>` for every contract row (path must exist; line N must contain "append") | `leg_contract` lines 287-294 |
| `git ls-tree -r --name-only <tip>` (contract pattern expansion) | `contract_files` lines 264-271 |
| `git rev-list --topo-order --reverse --parents <tip>` (whole lane history) | `recompute` line 203 |
| Per (parent, commit, file): `git diff --numstat --no-renames <p> <c> -- <files>`; `git diff --no-renames --no-color --no-ext-diff -U0 --text <p> <c> -- <file>`; `git cat-file -p <rev>:<file>` | `numstat` line 193; `deleted_lines` lines 163-164; `blob_lines` line 150 |
| Tool subprocess runs (selftest, lane `--json --to <tip> --contract <contract-at-tip>`, fixture, stable twice) | `leg_selftest` 335-345, `leg_lane` 365-391, `leg_fixture` 515-552, `leg_stable` 555-584 |

The contract at the build commit declares exactly: `LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md`, `registry/history/DELTA.md` (expansion = 85 files at the measured tip). **No `.ufo/waves/round-47/c2/` path and no `tools/kama-*` path is read.** Static grep: the v2 tool source contains no `ufo`, `kama-`, `round47` or `live-replay`; the counter source contains no `c2/live`, `kama-` or `receipt` path usage (only the `--out` help string).

### C2 counter `tools/round47-live-replay-audit.py` (sha256 15408dce5b2f8f5dbe4dd7bacf17ddb0737fcbe480686907f40483273b128b0f)

| Read | Where in code |
|---|---|
| `rev-parse --verify <tip>^{commit}` | main() line 221 |
| `git archive --format=tar <tip>` — whole tree, extracted under scratch (links skipped) | main() lines 222-231 |
| `git show <tip>:.ufo/waves/round-47/c2/live/receipt-1.json| -2 | -3.json` | main() lines 240-252; `RECEIPTS` line 96 |
| `git cat-file -e <tip>:<log_path>` only when `teardown.log_path` is non-null | `check_receipt` line 177 |
| `git show <tip>:tools/kama-live-replay.py` (presence; then executed from the extracted tree) | main() line 255; `REPLAY` line 97 |
| `git show <tip>:corpus/SOURCES.md` (newrow leg) | main() line 321 |
| Network: `https://github.com/.../llama-b11909-bin-ubuntu-x64.tar.gz` and `https://huggingface.co/.../stories260K.gguf` (via the replay tool, replay + tamper legs) | `ASSET_URL` 93-94; replay tool `fetch`/`acquire` |
| The replay tool additionally executes `tools/kama-llamacpp-live.py` from the extracted tree (with `--server/--model/--server-asset-url/--server-asset-sha256/--server-member/--model-url/--model-sha256`) | `run_replay` 184-196; replay tool `replay()` |

**No `tools/append-only-audit.py`, no `registry/append-only-contract.tsv`, no other registry path is read.** The only overlap with C1's read set is `corpus/SOURCES.md` (C1 scans its history for deletions; C2 checks it for a `| S` row naming b11909).

## 2. Fixture construction (clone at bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba + only that build)

`git clone --shared $S/lane $F`; detached at `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba`; `git checkout 3a09a1d93dcc16799cf6c4b48786e6440af134c4 -- <build paths>`; one commit (local identity, in scratch only; toplevel asserted before first commit).

- **Fixture A (C1-only)**, tip `2e6f587a6337b56413e1571356fc4b6260d95189`: tree delta vs bbcc = only `registry/append-only-contract.tsv` (+8) and `tools/append-only-audit.py` (v1→v2, 395 lines changed). No C2 path present.
- **Fixture B (C2-only)**, tip `7f15fa17840a333309935e21712f911e34257853`: tree delta vs bbcc = only `tools/kama-llamacpp-live.py` (v3→v4, 34 lines), `tools/kama-live-replay.py` (new, 267), `.ufo/waves/round-47/c2/live/{receipt-1,-2,-3.json,install.txt}` (new), `corpus/SOURCES.md` (+1 row `| S488 | ... b11909 ... caa8191df159f764fb0160e3d2fc6be008948aee ...`). No C1 path present.

## 3. Does each reach its legs alone? Yes — both pass

C1 counter on fixture A:

```
$ python3 tools/round47-append-audit-v2-check.py --repo fxA-* --tip 2e6f587a6337b56413e1571356fc4b6260d95189 --scratch $S
selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True
tip=2e6f587a6337b56413e1571356fc4b6260d95189 base=172b8ad040d51ce8c011238c1408d4e0b6aa9595
exit=0
```

C2 counter on fixture B (downloads ~23 MB asset + ~1.2 MB model per replay; 3 replays: replay + 2 tamper):

```
$ python3 tools/round47-live-replay-audit.py --repo fxB-* --tip 7f15fa17840a333309935e21712f911e34257853 --scratch $S
receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True
tip=7f15fa17840a333309935e21712f911e34257853 started=2026-10-26T21:26:37.663297+00:00
exit=0
```

So C1 verified with only the C1 build in the tree, and C2 verified with only the C2 build: each reaches its legs alone (C1's 5 events and 85 files match the L1's lane numbers; C2's 11 rerun checks match receipt-1's 11 evaluated checks).

## 4. Can a C2 SOURCES append or receipt commit change a C1 event? No

Static reasons: C1 only diffs contract-declared files; a C2 commit touches only non-contracted paths plus `corpus/SOURCES.md`, where it only appends lines. An event needs ≥20 *deleted* lines in one commit — appends delete nothing, so no new event, no deleted-count change. Restoration is a window maximum, so an added line can only ever raise a `restored_max`, never lower it (status cannot regress; the stable leg's `restored_max(tip) >= restored_max(base)` cannot be violated).

Empirical check — fixture A+ (fixture A + the exact C2 build on top, tip `acf4c7316af57c6411cf941c1de6361a84830ffb`):

```
$ python3 fxA-*/tools/append-only-audit.py --repo fxA-* --to 2e6f587a... --contract .../append-only-contract.tsv --json   # exit 1
$ python3 fxA-*/tools/append-only-audit.py --repo fxA-* --to acf4c731... --contract .../append-only-contract.tsv --json   # exit 1
files A 85 A+ 85 ; events A 5 A+ 5 ; events identical: True
```

The full event tuple set (commit, file, deleted, restored_max, restored_best, restored_by, status) is byte-identical before/after the C2 landing, and the C1 counter still passes on A+:

```
selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True  (exit=0)
```

Reverse direction (C1 landing cannot disturb C2): fixture B+ (fixture B + the C1 build, tip `e80fb8fe2263fb5ca32e9a35ea05fcdc562574d8`) — C2 counter still passes:

```
receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True  (exit=0)
```

## 5. Answers

1. **Does each reach its legs alone?** Yes — C1 on fixture A: `met=True` (all 5 legs); C2 on fixture B: `met=True` (all 4 legs). The C2 counter's `git archive` does extract the whole tree, but its legs read only receipts/replay tool/SOURCES; extra files cannot affect verdicts.
2. **Can a C2 SOURCES append or receipt commit change a C1 event?** No — events identical byte-for-byte (5 events, same restored values/statuses), counter still `met=True`. Same conclusion in reverse: C1 build leaves C2 `met=True`.
3. **Shared-surface caveat:** the only overlapping read path is `corpus/SOURCES.md` (C1 event history, C2 newrow). The overlap is append-only by construction (contract rule A-row: "registry rows appended"), so it is benign; a hypothetical C2 *editing* rather than appending SOURCES would be the one theoretical cross-surface, and it is not what the C2 build does.

## 6. Risks / notes

- C2's legs require live network (github.com, huggingface.co); both were reachable during this run and all digests verified against the frozen values (asset `bf94332a...`, model `270cba1b...`).
- The test is exactly as strong as the frozen counters: C1's lane leg is a self-consistency check (tool vs counter recomputation) over the history present at the tip; the fixture legs give independent ground truth. A fixture containing the full real history up to bbcc is the faithful "clone at bbcc" per the item.
- No defects found in either counter or build; no installation performed (python3 + git only). No lane/fleet files were modified; all fixture commits are inside scratch ($S) and will be removed.
