VERDICT: partial — the operator reflection's four self-improvement suggestions versus the round-16 artifact set at `b8e485c`: none is fully satisfied; suggestion 2's data source contradicts itself, suggestion 4's seat counter records a false zero, and suggestions 1 and 3 are unimplemented (suggestion 1 is contradicted by a dangling receipt in the round's own lesson).

# ConnectConsiderTheseLedger — four suggestions, one missing property

Seat: connector (leaf, read-only). Source of the four proposals:
`considerthese/2026-10-20.md:22-28` (suggestions 1-4). Attack target: what the
round-16 artifacts at lane commit `b8e485c` already satisfy or contradict.
Axes considered: assigned `operability + calibration` (`../shokunin.conf:52`);
lane readings operability 8, calibration 7 (lowest), freshness 8, coverage 9,
depth 7, adjacency 7 (`SCORECARD.md:559-563`).

## Verdicts, one row per suggestion

| # | Suggestion (paraphrased) | Round-16 state | Evidence |
|---|---|---|---|
| 1 | Window-completeness receipt for the reflection's own pass: list every counted SHA, reconcile author vs committer date, add push time | **Unimplemented in the lane; its analogous claim is contradicted.** Round-16 records a start revision and wave UTC instants, but no commit-window enumeration, no date reconciliation, no push time. The round's own evidence pointer is dangling. | lesson `corpus/lessons/round-16.md:94` says "Final numbers at the measured commit are in `.ufo/waves/round-16/acceptance.json`"; `ls` → exit 2, `git ls-tree -r --name-only b8e485c \| grep -c round-16/acceptance.json` → `0`. `git log -1` on `b8e485c`: author `2026-10-20T10:50:42-03:00`, committer `2026-10-20T10:50:49-03:00` — a 7 s divergence exists that no receipt reconciles. `dispatch-provenance.py:12-23` records wave `started`/`ended` UTC and spec/`taskCall` digests, which is a reusable half-step, not a window receipt. |
| 2 | Stagnation tracker: rounds-since-last-capability and axes still below 8 | **Partially satisfied; the data source contradicts itself.** The new "Current state (round 16)" block gives axes, readings, the lowest axis versus the saturation line, and "nudge inactive" — but no rounds-since number, and three different capability counts exist. | `SCORECARD.md:559-568` (block) vs canonical table `SCORECARD.md:124-126` = **1 row** (`sources-registry`, round 10) vs round-14 row only at `SCORECARD.md:459` vs prose `:565-567` = **2 rows**. `AXES.md:57-64` makes the single `capabilities:` table the repertoire, and `:66-73` derives the nudge from "no capability has entered the table within the window". A tracker reading the table gets last=10, rounds_since=6 (11-16) ≥ N=4 → stagnation; reading the prose gets last=14, rounds_since=2. Round 16 correctly withholds its own third row pending L1's report (`AXES.md:62-64`; corroborated by build advice `CriticCapabilityRow.md` §A), but the round-14 omission already breaks the source. |
| 3 | Promise inventory: pair each "rejects/refuses/never" with the test that exercises its negative case | **Unimplemented, and round 16 adds at least one unpaired promise.** Some new promises are genuinely paired; the new tool's promise set is larger than its controls. | Paired: `.ufo/waves/round-16/live/controls.txt` records digest mismatch exit 3, `--port 34113`/`8080` exit 2, in-use 631 exit 2, gate selftest 16 mutations exit 0. Unpaired: `tools/kama-llamacpp-live.py:232-233` "Never pass 0 through to llama-server", guarded at `:235-236` (`1 <= requested <= 65535` → `explicit-port-out-of-range`), but `grep -rn "explicit-port-out-of-range"` outside the tool → no hits (exit 1); no `--port 0` or out-of-range invocation in `tests/`, `controls.txt`, or `SKILL.md`. Also `tools/kama-llamacpp-live.py:12` "the only filesystem artifacts are a temp stdout/stderr log" has no test I can find. The reflection's defect class (KQ18) is therefore live in round 16's own new tool. |
| 4 | Routed-defect and seat-budget ledger: open/closed across rounds; seats dispatched/completed/failed by cause | **Partial on defects, contradicted on seats.** Round-16 dispositions the six round-15 defects and prior D2/R1/R2 are closed, but closure lives across four lesson files with no ledger. The new dispatch ledger cannot count the wave it receipts. | Defects: `corpus/lessons/round-16.md:70-82`; prior D2 closed at `corpus/lessons/round-14-verifier-spotcheck.md:144`; R1/R2 closed at `corpus/lessons/round-15-verifier-spotcheck.md:165-166`; no single table (grep for a cross-round ledger finds none). Seats: `.ufo/waves/round-16/falsify/provenance-ledger.json` attempt entry `{label:"spawned", spawned:0, refused:0}` while the bound `wave_run` records `counts.dispatch.spawn=79, tasks=79`; the payload has 79 `progress` rows all `status:"pending"` and `results: []` (python count). `ProvenanceLedger.md` (build advice) admits the mechanism: "a refusal shape that reports zero via absence of fields yields `refused: 0`, not a flag". The schema has no `pending`, `completed`, `failed`, or cause bucket (402 / `RESOURCE_EXHAUSTED` / job-limit). Build wave: `build/completion-summary.json` (81/0) is untracked (`git status` `??`), so the pushed artifact set has no terminal seat tally at all. |

## What I ran (exact commands and exits)

All from the lane root, all read-only; no server started; `measure.py` not run.

- `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` → **exit 0**, `tests 72, passes 72, failures 0`, `probe_sha256 6edd3c4c…`.
- `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → **exit 1**, `tests 72, passes 55, failures 17`; all 17 expected verdicts are `MODEL_LOADING`; changed set equals the expected-loading set (`true`); observed `FOREIGN_SERVICE` with reasons `non-2xx-non-model-http`/`html-non-model`.
- `ls .ufo/waves/round-16/acceptance.json` → **exit 2** (no such file).
- `git ls-tree -r --name-only b8e485c | grep -c round-16/acceptance.json` → **`0`**.
- `git log -1 --format='%H%n%aI%n%cI' b8e485c` → author/committer dates above.
- python census of `.ufo/waves/round-16/falsify/spawn-result.json` → `progress rows 79 statuses {'pending': 79}`, `results rows 0`; ledger attempt `spawned 0 refused 0 label spawned`.
- `grep -rn "explicit-port-out-of-range"` outside the live tool → **no hits**.
- `grep -rn "promise inventory|unpaired promise|promise-scan"` → only `considerthese/2026-10-20.md:26`.
- `grep -rn "D2|R1|R2|routed defect"` across `corpus/lessons/round-1[3-6]*.md`, `SCORECARD.md` → closure prose only, no ledger.

I did not re-run the live tool or the receipt gate; `CriticCapabilityRow.md` §B and
`RerunLiveNegatives.md` already re-derived those and I take their results as
corroboration only.

## The move (one bounded follow-up for the next round)

**Admit a round-close resolvability gate: one fenced `kama-round-ledger` JSON block
per round section, plus one read-only stdlib checker `tests/round-close/check.py`
that re-derives it.**

All four suggestions are proxies for one property the lane does not yet have:
*the round's claims are resolvable by a machine from the round's own published
artifacts*. The lane has learned to make tool promises fail-capable (KQ18/KQ19),
but never the round's own bookkeeping. Round 16 demonstrates the gap three times:
a cited receipt that does not exist, a capability count with three answers, and a
seat counter that says zero for 79 pending seats. The non-obvious move is not
another hand-written self-test (that is exactly round-16 M2's failure mode:
"self-authored selftest hides producer drift") — it is a checker whose red control
is the *pushed tree* and whose green control is a corrected copy outside the repo.

Minimal block (appended; old bytes untouched):

```json
{"round":16,
 "cites":[{"path":".ufo/waves/round-16/acceptance.json","sha256":null}],
 "capabilities":["sources-registry","ollama-offline-evidence-replay"],
 "axes":{"operability":8,"calibration":7,"freshness":8,"coverage":9,"depth":7,"adjacency":7},
 "commits":[{"sha":"b8e485c","author_date":"2026-10-20T10:50:42-03:00","committer_date":"2026-10-20T10:50:49-03:00"}],
 "seats":{"planned":79,"pending":79,"terminal":0,"failed_by_cause":{}}}
```

Three checks, each with a known red finding on today's tree:

1. **Cites resolve.** Every `cites[].path` exists; when `sha256` is non-null it
   matches. Red today: `acceptance.json` missing (`ls` exit 2).
2. **Capability counter is derived, not narrated.** `capabilities[]` must equal
   the canonical `§Capabilities` rows ∪ this round's demonstrated rows;
   `rounds_since_capability = round - max(first_working_round)`; print
   `axes_below_saturation`. Red today: table 1 row vs block/prose 2 rows
   (6 vs 2 rounds since — one of which crosses N=4).
3. **Seat census by status value, never by key presence.** Recompute from the
   bound `spawn-result.json`; emit `pending/completed/failed/refused/unknown`,
   `null` for unobserved buckets, and reject `terminal: 0` when `results == []`
   and `pending > 0`. Red today: `label:"spawned"` with `spawned:0` for 79
   pending seats.

Fail-capable controls, in the lane's idiom: run on the pushed `b8e485c` tree
(must exit 1 with exactly those findings); on a `/tmp` copy with the three fixes
(exit 0); and 3 single-field mutations, one per assertion (each exit 1). Digests
are computed by the gate from the files, not pasted by the author, so the green
fixture cannot be shaped to pass.

**Suggestion 3 is deliberately deferred, not bundled.** A promise inventory needs
its own enumeration rule for docstrings/`LIMITS` and a pairing oracle; adding it
before the receipts resolve would create a second unverified oracle — the exact
M2 failure. Once the block exists, `promises:[{text, promise_path, test_path,
negative_control}]` is a natural fourth field for the following round, and
`tools/kama-llamacpp-live.py` `explicit-port-out-of-range` is its first red row.

## Affected axes and harm check

- **Calibration 7 (lowest, assigned): improves.** Round claims become
  mechanically re-derivable; the stagnation counter stops depending on which
  table a reader opens. Planned **7 → 7**: a receipt gate is not mastery.
- **Freshness 8: improves incidentally.** The block is derived from the measured
  artifacts, so a stale `§Capabilities`/saturation reading cannot sit silently.
- **Operability 8: unchanged by construction.** No edits to `tools/kama-probe.sh`,
  `tools/kama-llamacpp-live.py`, the probe matrix, or the live receipt gate; no
  server, no network, no new runtime.
- **Coverage/depth/adjacency: unchanged.** No new sources, knowledge or frontier
  ground; the gate adds no capability row for itself.

## Risks

- **R1 — another self-authored oracle.** Mitigation is structural: red control is
  the published tree at `b8e485c`; green is a `/tmp` correction; the gate computes
  all digests from files. If the gate's first run is not red on today's tree, it
  is vacuous and must not be admitted.
- **R2 — prose parsing drift.** The gate reads only the fenced block, never
  prose; `§Capabilities` is read as a table with a fixed four-column contract
  (`AXES.md:60-64`).
- **R3 — capability semantics.** The canonical table is missing round 14; the fix
  is an appended row (append-only is allowed), and the gate must compare
  table ∪ demonstrated rows so a mid-round capability is neither pre-claimed nor
  lost.
- **R4 — payload shape drift.** The seat census must enumerate observed `status`
  values and report unknown keys, not silently ignore them; freeze the 79-pending
  falsify payload as the red fixture.
- **R5 — round-16 timing.** The round is mid-flight; if L1 writes
  `acceptance.json` before close, finding 1 resolves and the gate should go green
  on cites while keeping findings 2 and 3. The lesson's present-tense claim is
  still false at `b8e485c` and needs either the file or an appended correction.

## Limitations and inferences

- `[INFERENCE]` that a stagnation tracker would read `§Capabilities`
  mechanically: no tracker exists yet, but `AXES.md:60-64` designates that table
  as the repertoire, so it is the intended source.
- The "unpaired promise" finding for `--port 0` is based on repo-wide grep of
  `tests/`, `controls.txt`, `SKILL.md` and the wave receipts; a control run
  outside the repo is possible but unrecorded.
- Suggestion 1 is the reflection's own pass, outside lane province. The lane can
  only supply a mechanical commit ledger; it cannot reconcile the reflection's
  window.
- `acceptance.json` may be a known pending L1 deliverable; this report records
  its state at falsify time, not a judgment about L1's intent.
- Two findings overlap build-wave advice and are cited as corroboration, not
  novelty: `ReviewScorecardCurrency.md` F2/F3 (stale canonical table, round-10
  saturation line) and `CriticCapabilityRow.md` Gap B1 (`acceptance.json` absent).
  The new contribution here is the synthesis — one round-close property — and the
  false-zero seat census, which no advice file reports.

## Installs

None. Tools used: `python3`, `git`, `grep`, `ls`, `sed`, `wc` (all pre-installed).
No pacman/uv/npx transaction; no llama-server started; nothing bound to 8080 or
34113.
