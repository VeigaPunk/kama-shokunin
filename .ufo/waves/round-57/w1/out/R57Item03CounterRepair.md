# R57 item 03 — stale maxN counter repair (scratch prototype)

Seat: `R57Item03CounterRepair`, executor, kama round 57 wave `kama-r57-w1`. Axes: calibration + operability. Scratch: `/fast/scratch/hyaku/kama-r57/R57Item03CounterRepair/` (trap-cleaned fixtures/tmp; receipts copied here first). Lane repo writes: none — this directory only. No commits, pushes, jj mutations, fleet files, source-tree writes or installs; pacman transactions remain paused. Counter runs are read-only (`git cat-file` / `git archive` / `git ls-tree`) with `TMPDIR` inside scratch.

## 1. Frozen claim tested

Frozen claim text: *"counter currently reports maxN=56 instead of expected 46; before output mismatch=1."*

| Check | Exact result |
|---|---|
| Counter bytes (frozen base and every round-57 commit at seat time, `b89bdab2`…`8640e34c`) | `sha256 9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0` (297 lines) |
| Frozen base `b89bdab2cc114735ec5d331c6c610134258f7864` | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`, exit 1 — reproduces `controls/base-c1.out` exactly |
| `maxN` at that base, two independent scanners | 56 / 56 (`receipts/case24-independent.out`, `receipts/independent-maxn.out`) |
| Where 46 comes from | max round heading at historical commit `4340cf2f68ebbfb618086e16825c2e7effd7fa58` (round 46) is 46; `46` is also the hardcoded literal in `controls/c1-noop.py`, which reads no tree bytes (`noop_literal_46= True`, `noop_reads_tree= False`) |
| Current tip at seat time | `8640e34cad02adcd247ba0862da63f6fb2aab0df`: frozen counter `r41=0 … mismatches=0 maxN=57 met=True`, exit 0 |

**Verdict: the claim as stated is false.** `maxN` is tree-derived and was 56 at the frozen base and 57 at `8640e34c` once the round-57 SCORECARD section landed; 46 is a stale historical value and the no-op control's literal, not an expected value derived from the tree. A gate that demands 46 is satisfied by the no-op and rejected by the real counter (`receipts/naive-gate46-noop.out` `naive_gate46=pass exit=0`; `receipts/naive-gate46-real-base.out` `naive_gate46=fail exit=1`).

The freeze amendment's C2 (stale calibration count 42→43, require `mismatches=0`) is already satisfied in-tree: commit `7b74e2f2` changed `SCORECARD.md` calibration evidence `→ 42` to `→ 43`, and r41 reads 0 mismatches there and at `8640e34c`. That literal repair is outside this seat's write scope and is recorded, not claimed. HEAD moved under the seat (`b89bdab2` → `7c873d7b` → `7b74e2f2` → `8640e34c`); every receipt pins the commit it ran against.

## 2. Prototype repair (minimal)

`receipts/patch.diff` — two edits to `prototype/base/round42-selfdesc-reconcile.py` (identical to the lane counter):

1. add `live_lines(text)`: drops lines inside fenced code blocks (opening fence of 3+ backticks or tildes, closed by the same character with at least the opening length) and inside multi-line `<!-- … -->` comments;
2. derive `rounds`/`maxN` from `live_lines(sc)` instead of `sc.split("\n")`.

Everything else (r41 import, banner/Planned/Retired/Saturation/Caps/receipts/readme/province/rel facts, output format, exit codes) is byte-unchanged. **Canonical heading semantics preserved:** `maxN` remains the greatest N over lines matching `^## Round (\d+)`; only non-live (fenced/commented) copies of such lines are ignored — the exact shape the append-only audit restores deleted SCORECARD blocks in (`SCORECARD.md:2969` is such a fenced `## Round 30` today).

| Case | Base counter | Prototype |
|---|---|---|
| Real lane, frozen base `b89bdab2` | `mismatches=1 maxN=56 met=False` exit 1 | byte-identical output, exit 1 |
| Real lane, tip `8640e34c` | `mismatches=0 maxN=57 met=True` exit 0 | byte-identical output, exit 0 |
| Fixture: base SCORECARD + fenced restored `## Round 99` | `banner=1 planned=2 maxN=99 mismatches=63` exit 1 | `banner=0 planned=0 maxN=56 mismatches=60` exit 1 |
| Fixture: base SCORECARD + `<!-- ## Round 98 -->` block | `banner=1 planned=2 maxN=98` exit 1 | `banner=0 planned=0 maxN=56` exit 1 |
| Positive control: base SCORECARD + **live** `## Round 99` | `maxN=99` | `maxN=99` (semantics preserved) |
| 11 unit cases (fence lengths, nested 3-in-5 fence, tildes, unclosed fence, inline comment, indented heading) | — | `cases_failed= 0`, exit 0 |

The stale case also fixes derived keys, not just the printed number: the counter demanded `### Planned (round 100)` at base and `### Planned (round 57)` after repair (`receipts/maxn-cases.out` `planned_round_base= 100`, `planned_round_build= 57`).

## 3. Receipts (all under `.ufo/waves/round-57/w1/out/R57Item03CounterRepair/receipts/`)

| Receipt | Exact key line / exit |
|---|---|
| `base-counter-at-base.out` | `r41=1 … mismatches=1 maxN=56 met=False`, exit 1 |
| `build-counter-at-base.out` | identical to above, exit 1 |
| `base-counter-at-tip.out` | `r41=0 … mismatches=0 maxN=57 met=True`, exit 0 (`8640e34c`) |
| `build-counter-at-tip.out` | identical to above, exit 0 |
| `base-counter-fixture-stale-fence.out` / `build-counter-fixture-stale-fence.out` | `maxN=99` / `maxN=56`; both exit 1 (fixture is intentionally incomplete: no README/PROVINCE/SOURCES) |
| `base-counter-fixture-stale-comment.out` / `build-counter-fixture-stale-comment.out` | `maxN=98` / `maxN=56` |
| `base-counter-fixture-live-stale.out` / `build-counter-fixture-live-stale.out` | `maxN=99` / `maxN=99` |
| `maxn-cases.out` | `cases_failed= 0`, exit 0 |
| `independent-maxn.out` | base `raw=56 live=56` |
| `noop-frozen-c1.out` | `mismatches=0 maxN=46 met=True`, exit 0 (no data read) |
| `noop-build.out` | `mismatches=0 maxN=56 met=True`, exit 0 (no data read) |
| `naive-gate-noop.out` | `naive_gate=pass exit=0` |
| `naive-gate46-noop.out` / `naive-gate46-real-base.out` | `pass exit=0` / `fail exit=1` |
| `canon-scope-limit.out` | `canon_round_after_fenced_stale_block=99`, `maxN_after_same_text= 56` |
| `patch.diff`, `sha256sums.out`, `fixture-toplevels.out` | patch + `sha256(base)=9736923e…`, `sha256(build)=6f72a807…`; each fixture `rev-parse --show-toplevel` equals its own dir |

Reproduce: `bash .ufo/waves/round-57/w1/out/R57Item03CounterRepair/run.sh` (self-locating; writes receipts into scratch `S` and is read-only against the lane; includes the r41 dependency the counter imports). After copying receipts, this evidence copy was re-run from its own directory with `S=/fast/scratch/hyaku/kama-r57/R57Item03CounterRepair/repro-test`: run exit 0, `case24_ok= True`, `fenced_stale_canon_selected=True`, with the same `maxN` lines; the scratch tree was then removed. `MANIFEST.sha256` covers every file here except itself.

## 4. No-op control

`controls/c1-noop.py` prints `mismatches=0 maxN=46 met=True`, exit 0 while reading nothing. A do-nothing build summary (`noop-build.py`) likewise prints `met=True`; both pass a summary-token gate (`naive-gate.sh`, `naive-gate46.sh`). Summary/substring verification therefore cannot distinguish a real derivation from a no-op — the repair must be accepted only on tree-derived values (the fixture pair above), never on the printed `met`.

## 5. Limits and routed observations

- `live_lines` approximates CommonMark fences/comments: fences indented >3 spaces, blockquote- or list-nested fences, and inline HTML comments spanning a fence are not modelled. An indented `    ## Round 99` is not a heading and is already ignored by both derivations.
- **Only `maxN` is repaired.** `sections()`, the `planned` heading search and `canon()` still scan raw text. `canon-scope-limit.out` shows a fenced restored canonical table (`canonical list as of round 99`) is still selected after the repair (`canon_round_after=99`); this prototype does **not** provide canonical-row execution/content binding (routed to the canonical-binding/selftest seats).
- Untested by this seat: the frozen prereg checker/battery, integration of the patch, and any rerun at a later tip. Prototype only; no axis score is claimed.
- Concurrency: the lane tip moved during the seat and another seat/L1 repaired the 42→43 count. Receipts pin `b89bdab2`, `7b74e2f2`-era output and `8640e34c`; re-running against a moving `HEAD` will print a different `maxN`/`tip`.
- No tool installs or version changes were made.

## Files changed

- `.ufo/waves/round-57/w1/out/R57Item03CounterRepair.md` (this report)
- `.ufo/waves/round-57/w1/out/R57Item03CounterRepair/` (prototype copy, scripts, `receipts/`, `case24-independent.md`, `MANIFEST.sha256`)

Report: .ufo/waves/round-57/w1/out/R57Item03CounterRepair.md
