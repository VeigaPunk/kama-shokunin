# X14FenceLane — lane impact of the v5 fence and CRLF fixes, and merge-parent order independence

**Verdict: zero hits.** Across the lane's whole 1,052-commit graph (all refs, including the
`refs/jj/keep/*` archives) no blob of the seven named files — nor of any of the 94 paths the
append-only contract ever declares — carries a `## ` line inside a CommonMark fenced block or
a single `\r` byte. `sections()` therefore assigns the same title to every line at every
commit under v4 and v5, so the fence fix (F4) and the CRLF fix (F5) change no lane verdict:
all five events keep their exact graded/ungraded split (23/23, 72/72, 0/0, 0/0, 0/0 under
both definitions). The lane verdict is also order-independent at the frozen threshold: with
both merge commits' parents swapped, `tools/append-only-audit.py` at the measured commit
`97c864bead3ee4a2f629574e77263d33834ec98a` produces **byte-identical** JSON (sha256
`62e3b5c6…`, same 5 events, exit 0), and the v5 origin sets for all five event files are
equal under either parent order. One calibration boundary is worth recording (F1 below):
the order-a/b guarantee is threshold-bounded at a *dropping* merge, and the counter's 12
fixtures never build one; on this lane the two merges carry at most 2 second-parent
deletions, far below the threshold 20 that would turn them into events.

## Setup

| item | value |
|---|---|
| clone | `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (exit 0) |
| measured commit | `97c864bead3ee4a2f629574e77263d33834ec98a`, 327 commits, 2 merges, 0 octopus merges |
| lane HEAD in the clone | `3b79eaddf38246c637cc7ba1a94ab363422876b6`, 330 commits |
| all refs | 1,052 commits after `fetch 'refs/jj/keep/*:refs/jj/keep/*'` (read-only on the lane) |
| scratch | `/fast/scratch/hyaku/kama-r50/X14FenceLane` |

Frozen counter C2 at the measured commit, as an independent cross-check of the numbers
below (exit 0, 5.3 s):

```
fixture=1 lane=1 scenarios=12/12 met=True
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
```

My own replication of the same v5 measure (parent section is an exempt title *and* origin ∩
exempt titles, without the tool's `eligible` window filter) returns exactly 23 and 72, i.e.
the counter's lane detail and my scan agree to the line.

## 1. Fence and CR scan of every blob of the seven named files

`scan.py` (bytes) and `scan2.py` (per-blob census) walk every blob of
`SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md, AGENTS.md,
SKILL.md` at every commit; fence state follows CommonMark 0.31.2 §4.5 exactly as
`fence_open`/`fence_close` implement it (`tools/append-only-audit.py:282,295`,
`tools/round50-append-audit-v5-check.py:305,316`).

| measured graph | commits | blob ids | blobs with a `## ` line inside a fence | blobs with any `\r` |
|---|---|---|---|---|
| reachable from the measured commit | 327 | 407 | **0** | **0** |
| all refs (incl. jj keeps) | 1,052 | 430 | **0** | **0** |

Per-file census over all 1,052 commits (`census-all.json`; 434 path×blob instances):

| file | blobs | blobs with fences | fenced blocks | lines inside fences | `## ` inside fences | CR bytes | v4-vs-v5 section diffs |
|---|---|---|---|---|---|---|---|
| SCORECARD.md | 103 | 12 | 24 | 144 | 0 | 0 | 0 |
| LOG.md | 110 | 107 | 519 | 2,499 | 0 | 0 | 0 |
| corpus/QUALITY.md | 46 | 0 | 0 | 0 | 0 | 0 | 0 |
| corpus/README.md | 52 | 0 | 0 | 0 | 0 | 0 | 0 |
| corpus/SOURCES.md | 67 | 0 | 0 | 0 | 0 | 0 | 0 |
| AGENTS.md | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| SKILL.md | 53 | 52 | 75 | 785 | 0 | 0 | 0 |
| **total** | **434** | **171** | **618** | **3,428** | **0** | **0** | **0** |

The scan is not vacuous: 618 real fenced blocks and 3,428 lines inside them are parsed, so
the fence state machine is exercised by lane content; none of those lines starts with
`## `. Supplementary, the same census over every path any ref ever matched by a contract
pattern (`scan3.py`, 10 patterns, 94 matched paths, `unmatched_patterns: []`) finds 567
blobs, 672 fenced blocks, 3,690 fenced lines, 164 blobs with fences, and again
`heading_inside 0, section_diffs 0, cr_bytes 0`.

## 2. Would `sections()` change a verdict at any commit? No — and the check has teeth

For every event the tool reports at the measured commit, `scan.py` recomputes, from the
parent blob, the set of deleted lines that v5 would call ungraded, and the set v4 would call
ungraded (fence-blind `sections()`, byte-exact origin keys), and compares positions:

| event | file | deleted | v5 native ungraded | v4-hypothesis ungraded | same positions | deleted lines with CR | fake headings in parent | deleted lines whose section changed |
|---|---|---|---|---|---|---|---|---|
| `dd9f5dc6c0e6` | SCORECARD.md | 31 | 23 | 23 | yes | 0 | 0 | 0 |
| `0718b6abbda6` | LOG.md | 2,292 | 0 | 0 | yes | 0 | 0 | 0 |
| `0718b6abbda6` | SCORECARD.md | 2,421 | 72 | 72 | yes | 0 | 0 | 0 |
| `0718b6abbda6` | corpus/QUALITY.md | 375 | 0 | 0 | yes | 0 | 0 | 0 |
| `0718b6abbda6` | corpus/README.md | 663 | 0 | 0 | yes | 0 | 0 | 0 |

5,782 deleted lines in total; none has a trailing CR and none sits behind a fenced heading,
so the F5 key normalization (`tools/append-only-audit.py:275`) is a no-op on this lane and
the F4 fence rule (`:306`) never fires.

Teeth test (`analysis.json → teeth_test`), in memory only: inserting a fenced
```` ```text / ## Axes / ``` ```` block directly after the `## Round 49 …` heading of
`SCORECARD.md` at the measured commit moves the census from `heading_inside 0,
section_diffs 0` to `heading_inside 1, section_diffs 59`, with v4 titling those 59 lines
`## Axes` (an exempt title) while v5 keeps
`## Round 49 — the replay execution witness (operability) and append-only-audit v4 by line origin (calibration) (2026-10-26)`.
So the scanner would have reported a real F4 witness if one existed in the lane.

## 3. The two-parent case: merge commits, origins under both orders

The lane has exactly two merges in the whole graph:

| merge | subject | p1 | p2 | deletions vs p1 (contract paths) | deletions vs p2 (contract paths) | merge tree = p2 tree |
|---|---|---|---|---|---|---|
| `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` | Integrate remote documentation; preserve local round log | `03b5f0e8` | `893e3c5d` | none | SCORECARD.md 2, corpus/README.md 1, corpus/knowledge/consumer-registry.md 1 (SKILL.md 1, not contract-declared) | no |
| `5396a876c466fcaa2c0b78715793ec280dfced6a` | Merge pull request #2 from VeigaPunk/devin/wiki-link | `69780977` | `1e489406` | none (LOG.md +7 insertions) | none | yes |

(a) **Origins are order-free.** The v5 origin is a union over births (`git rev-list`
independently of listing order): both the tool (`tools/append-only-audit.py:480-505`) and
the counter (`tools/round50-append-audit-v5-check.py:437-457`) short-circuit to "no birth"
when *any* parent holds the same blob and otherwise union *all* parents' key sets, so parent
position cannot matter. Measured for all five event files with the parent list reversed:
origin dicts identical (`n_origin_keys`: SCORECARD 2,178, LOG 2,055, QUALITY 240,
README 1,025; `origin_sets_equal_both_orders: true` for every event).

(b) **The lane verdict is empirically order-independent.** `swap-check.sh` re-creates both
merges with their parents swapped (same tree; `git replace` scoped to `refs/r50swap` via
`GIT_REPLACE_REF_BASE`, inside my own clone), shows
`rev-list --parents -1 2f7303c2 → 893e3c5d 03b5f0e8`, and runs the frozen tool on both
graphs:

```
frozen threshold:  sha256 62e3b5c6… (baseline) == sha256 62e3b5c6… (swapped) → BYTE-IDENTICAL
                   5 events, ungraded_lines 89, bad_declarations 0, exit 0 in both
```

(c) **Why:** event selection is first-parent by definition (`tools/append-only-audit.py:86-87`,
code `:512`; the counter mirrors it at `round50-append-audit-v5-check.py:466`), so a swap
only matters when the *second* parent holds ≥ threshold (20) deleted lines for a contract
file. The maximum second-parent deletion of either merge is 2.

(d) **Plumbing teeth, and the exact boundary.** The same two runs at `--threshold 1` (an
instrumentation run, not the frozen measurement) differ, which proves the swap reached the
tool's event loop:

```
events 102 (original parents) → 105 (parents swapped); ungraded_lines 201 → 204
+ 2f7303c24231 SCORECARD.md                         deleted 2  graded 0  ungraded 2  ungraded
+ 2f7303c24231 corpus/README.md                     deleted 1  graded 1  ungraded 0  restored
+ 2f7303c24231 corpus/knowledge/consumer-registry.md deleted 1  graded 0  ungraded 1  ungraded
```

So the order-a/b guarantee holds on this lane *because of* the threshold, not only because
of the origin definition.

## Findings

**F1 (calibration, informational — no lane effect, counters not edited).** The counter's
`order-a`/`order-b` scenarios (docstring "Fixture scenarios", `round50-append-audit-v5-check.py`)
build merges whose merge commit deletes nothing against either parent, so they exercise
order-independence of `origin()` only. The complementary shape — a *dropping* merge whose
first-parent diff is 0 but whose second-parent diff is ≥ threshold — is not among the 12
scenarios, and with a swapped parent order such a merge becomes an event for the tool. The
tool's own selftest already covers exactly that shape
(`t_merge_first_parent`, body at `tools/append-only-audit.py:714`, registered at `:1093`:
`merge -s ours` dropping a side branch's 30 deleted lines, asserting the only event is on
the side commit). On this lane the
effect is nil (max 2 deletions). Proposed (not applied — the counter is frozen):
1. one sentence after the order-a/order-b paragraph: the guarantee is threshold-bounded —
   a merge that drops ≥ threshold lines from its second parent would gain events under a
   swap, and the lane's two merges carry at most 2;
2. route a 13th scenario `merge-drop` to round 51 (a `-s ours` merge over a 25-line side
   deletion, expecting the event on the side commit and none on the merge under both parent
   orders).

**F2 (calibration record).** The lane supplies no natural witness for F4/F5: 434 blobs,
618 fenced blocks, 3,428 fenced lines, zero `## ` inside fences, zero CR bytes; the
contract-wide supplementary scan (567 blobs over 94 paths) agrees. The fence and CRLF
repairs are therefore fixture-only proofs on this lane's content; round-50 prose (SCORECARD,
lesson, QUALITY) should say the lane-side coverage is zero-hit, not that lane data
corroborated the rule. Scribe items; nothing edited here.

## Risks and limits

* Path-scoped: only blobs held under a path a contract pattern matches are audited; a
  historical blob under a different path is out of scope by construction (the tool grades
  the same way).
* Byte-level: any `\r` anywhere in a blob counts, so CRLF, lone CR and CR inside prose are
  all covered; zero found means the F5 normalization is untested by lane data.
* First-parent event selection is frozen definition, not a defect; the swap experiment
  changes a graph's *meaning* (which parent is the baseline), which is why (c)/(d) quantify
  the boundary instead of calling it a bug.
* My per-event v5 measure omits the tool's `eligible` window filter and is therefore an
  upper bound (23 ≥ tool 17 at `dd9f5dc6`); it matches the counter's own lane detail exactly.
* The swapped-parent runs used `git replace` in my own clone only, scoped to
  `refs/r50swap`; afterwards `for-each-ref refs/r50swap/` is 0 and `rev-list --parents -1`
  shows the original order again.
* C2 was re-run (exit 0, `met=True`); C1 was out of this seat's scope and was not run.
* No service was started by this seat; `pgrep -af llama-server` lists only chains under
  `/fast/scratch/hyaku/kama-r50/Sen3Teardown/` (another seat).

## Files written

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X14FenceLane.md`

Bundle: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X14FenceLane/`
`RUNLOG.md`, `scan.py`, `scan2.py`, `scan3.py`, `scan6.py`, `swap-check.sh`,
`scan-tip.json`, `scan-all.json`, `census-all.json`, `census-contract.json`, `analysis.json`,
`tool-tip.json`, `tool-tip-swapped.json`, `swap-baseline.json`, `swap-swapped.json`,
`swap-baseline-t1.json`, `swap-swapped-t1.json`, `swap-check.out`, `c2-tip.out`.
