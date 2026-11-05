# SC02ConsiderTheseMine — considerthese/2026-10-26.md proposal census

Seat: SC02ConsiderTheseMine (scout, leaf). Lane: kama-shokunin. Milestone: kama r87 w1.
Judged axis: calibration.

Scope: read-only census of the four numbered proposals in `considerthese/2026-10-26.md`
§Self-improvement suggestions (lines 29, 31, 33, 35), decided by grep in `LOG.md`,
`SCORECARD.md`, `tools/`, `corpus/` and `plans/`, grounded by opening the pointers each
proposal cites inside the lane's own files. No lane file was edited.

Measured revision: `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (round-87 freeze commit),
read from a `git clone --shared` scratch worktree at
`/fast/scratch/hyaku/kama-r87/SC02ConsiderTheseMine/wt`. Scratch removed at end of seat.

## 1. Proposal table

| # | proposal (one line) | implemented in the lane? | evidence (path:line) |
|---|---|---|---|
| 1 | Flag deletions in append-only files the morning after they happen | **YES — implemented and strengthened** | `tools/append-only-audit.py` (v6 docstring `:6` cites this proposal by name); capability row `SCORECARD.md:143`; `tools/round81-append-debt.py` grades the event population; `corpus/lessons/round-81.md:98-101` "taken up by C2 rather than deferred"; `corpus/lessons/round-76.md:145-146`; `corpus/lessons/round-74.md:18` |
| 2 | Track what happens to my own proposals (a short table in each daily file) | **NO — the literal ask is unmet** | criterion `corpus/QUALITY.md:477` (KQ97) exists, but no daily file carries a disposition table: `considerthese/2026-10-19.md`…`2026-10-26.md` carry **0** rows matching `^\|.*(taken up\|deferred\|rejected\|pending)` for proposals (the 4 hits in `2026-10-23.md:7-10` and 2 in `2026-10-26.md:8,13` are round-verdict rows, not proposal rows); no standing ledger artifact exists (`find` for `*proposal*`/`*disposition*`/`*considerthese*` outside `.ufo/` → **absent**); no tool parses a proposal disposition (`grep -E '"[^"]*proposal[^"]*"' tools/*.py` → no hits); the per-round instance lapsed after round 75 (`corpus/lessons/round-75.md:87` "this table is the first instance; a standing ledger stays open" → **0** proposal-table rows in lessons 76–86, 0 rows citing any `considerthese/` file in lessons 77–86) |
| 3 | Keep a running count of counters that a shortcut can satisfy | **PARTIAL — tool exists, the running count it proposes does not** | `tools/shortcut-tally.py` exists and runs (`:12` names this proposal); `corpus/QUALITY.md:549` (KQ118); `SKILL.md:1520`; but the tool is **not** a registered capability (`SCORECARD.md:5363` canonical list as of round 86 → 0 rows mention shortcut; `tools/round74-selfdesc-canon.py --repo .` → `canon_rows=52 total=52`), is not an arm of `tools/pre-report-gate.py` (0 hits for "shortcut"), and the measured tally is empty for 32 of the last 47 rounds: `python3 tools/shortcut-tally.py --repo . --rev 94e8fe7b… --rounds 40-86` (exit 0) prints `shortcuts=-` and `cheats=0` for **every** round 55–86 and `unreadable:mutation-report` for rounds 48–54 (`out/SC02ConsiderTheseMine/receipt-shortcut-tally.txt`); the `--wide` family the docstring advertises (`:41-46`) is not an argparse option → exit 2 "unrecognized arguments: --wide" |
| 4 | Report the pin gap every morning | **PARTIAL — instrument lands, the daily report does not** | `tools/pin-watch.py` exists and is a capability (`SCORECARD.md:140`); `corpus/QUALITY.md:570` (KQ122) requires a pin-gap line in a freshness round; live runs exist (`corpus/lessons/round-74.md:18`: `pins=3 current=0 behind=3`); but **no** daily file carries a pin-gap line (`grep -l "pin-watch\|pin gap\|newer=" considerthese/*.md` → only `2026-10-26.md`, the proposal's own text); `corpus/lessons/round-81.md:102` "Proposal 4 … stays pending"; `corpus/lessons/round-86.md:115` "Proposals 1, 2 and 4 stay unimplemented" |

## 2. Chosen proposal

**Proposal 2 — "Track what happens to my own proposals."**

Grounding (each pointer opened in the lane's own files):

- The proposal's own premise is verified in-lane: "three of the four 2026-10-25 proposals became
  rounds 41 to 43" → `corpus/lessons/round-41.md:12` (pin-watch, mines 2026-10-25 proposal 2),
  `corpus/lessons/round-42.md:12` (digest-ledger, mines 2026-10-25 proposal 1),
  `corpus/lessons/round-43.md:12` (hexrun-census capability acquisition). The parenthetical
  "round 40 first deferred pin-watch as 'detects nothing today'" → 
  `corpus/lessons/round-40-verifier-spotcheck.md:80`, verbatim: "a watch run today detects nothing".
  So the reflection's claim is true — but it is true only as prose in one operator file.
- The lane already tried this and the attempt **lapsed**. `corpus/lessons/round-75.md:87` is the
  lane's own verdict on its own attempt: "| `2026-10-26.md` 2 — track what happens to my own
  proposals | **this table is the first instance**; a standing ledger stays open | this lesson |".
  Measured: lessons 76–86 contain **0** rows citing any `considerthese/` file, and **0** rows
  matching a proposal-disposition table. The one-off lesson table was the whole implementation.
- The criterion was written and never given a machine. `corpus/QUALITY.md:477` (KQ97) binds the
  daily reflection to record a disposition — but the lane's own daily files violate it (0
  proposal rows in all 8 files), no ledger file exists, and no tool reads one. A criterion with
  no checker is exactly the "counter that a shortcut can satisfy" shape this lane keeps mining.
- The disposition record is **contradictory and unreconciled**, which is the cost the proposal
  predicts ("stop repeating ones that keep getting deferred"):
  - `corpus/lessons/round-74.md:18` — proposals 1, 2, 3 "already **landed as lane-round work**".
  - `corpus/lessons/round-76.md:145-146` — "the other three … are landed".
  - `corpus/lessons/round-81.md:98-101` — proposal 1 "is taken up by C2 rather than deferred";
    proposal 4 "stays pending".
  - `corpus/lessons/round-86.md:115-116` — "Proposals 1, 2 and 4 stay unimplemented".
  These cannot all hold. P1 **is** implemented (`tools/append-only-audit.py`; `SCORECARD.md:143`;
  `tools/round81-append-debt.py`; round-81 C2), yet round-86 records it as unimplemented — and
  round-86's lesson never re-opens the artifact (grep "append-only-audit" in
  `corpus/lessons/round-86.md` → 0 hits). No later file reconciles the two records
  (grep "stay unimplemented" across `corpus/lessons/*.md` and `LOG.md` → only that one line).
  A reader of the lane today cannot tell from the lane that proposal 1 is done.
- This is the one proposal whose stated purpose is *calibration of the lane's own self-report*:
  "would let me calibrate what kind of proposal is useful and stop repeating ones that keep
  getting deferred". Round 87's assigned axis is calibration, and the lane's calibration
  deficit is documented as self-report drift, not as missing coverage.

Why not the others: proposal 1 is implemented and stronger than asked (`tools/append-only-audit.py`
grades every deletion, not just ≥20). Proposal 3's tool exists and runs but is unregistered
(not a capability row, not a gate arm) and its count is empty for rounds 55–86 — a real gap, but
its fix is an instrumentation/wiring change to an existing tool rather than the still-missing
capability proposal 2 asks for, and proposal 3 was already mined to `KQ139` at
`corpus/lessons/round-86.md:110-115`. Proposal 4's daily line depends on a network read the lane
cannot make unattended and is explicitly deferred to "the next freshness round"
(`corpus/lessons/round-81.md:102`); round 87 is not a freshness round.

## 3. Draft line for a QUALITY.md criterion (cites `considerthese/2026-10-26.md`)

> **KQ141** | The lane keeps one standing, committed disposition ledger for the numbered
> proposals of every `considerthese/YYYY-MM-DD.md` it has opened — one row per proposal naming
> the source file and number, the proposal's one-line text, its current disposition (taken up /
> deferred / rejected / pending), and the `file:line` of the artifact that took it up or the
> round that deferred it — and the ledger is reconciled by the lane's own counter before each
> round's claims are frozen: a proposal whose disposition is recorded in two lessons with
> different values, or whose recorded "taken up" names an artifact absent at the audited
> revision, is a finding and exits nonzero. A lesson may not record a proposal's disposition
> without reading the ledger row for it. | A lesson records a proposal as unimplemented while an
> earlier lesson records it as taken up and the artifact exists at the audited revision
> (`corpus/lessons/round-86.md:115-116` vs `corpus/lessons/round-74.md:18` and
> `corpus/lessons/round-81.md:98-101`); a proposal's disposition is written only in a lesson
> table that no later round carries forward (`corpus/lessons/round-75.md:87`: "a standing ledger
> stays open"; lessons 76–86 carry 0 proposal rows); or the ledger is written by hand with no
> counter, so its cells drift from the artifacts they name. |
> `considerthese/2026-10-26.md` proposal 2 (opened 2026-11-05 by seat SC02ConsiderTheseMine);
> `corpus/QUALITY.md:477` (KQ97, the criterion this makes checkable);
> `corpus/lessons/round-75.md:87`; `corpus/lessons/round-86.md:115-116`;
> `corpus/lessons/round-81.md:98-101`; `corpus/lessons/round-74.md:18`.

## 4. Remaining unknowns

- Whether the L1 wants the ledger as a `registry/` TSV, a `corpus/` markdown table, or a
  `tools/`-backed artifact is the L1's integration call, not this seat's; the criterion text
  above is written to be indifferent to the choice.
- Proposal 3's `--wide` family being absent from argparse (measured exit 2) was observed but not
  chased: whether that is a defect or a deliberate rename is not resolvable from the lane's files.
- Whether `corpus/lessons/round-86.md:115-116` was written under a different notion of
  "unimplemented" (e.g. "not re-adopted as a *claim* this round") is not stated anywhere in the
  lane; the sentence as written contradicts round-74 and round-81, and no file reconciles it.

## 5. Deliverables

- `.ufo/waves/round-87/w1/out/SC02ConsiderTheseMine/mine.md` (this file)
- `.ufo/waves/round-87/w1/out/SC02ConsiderTheseMine/receipt-shortcut-tally.txt`
- `.ufo/waves/round-87/w1/out/SC02ConsiderTheseMine/evidence-ABCD.txt`

No lane file was edited. No git/jj mutation was performed anywhere. Scratch
`/fast/scratch/hyaku/kama-r87/SC02ConsiderTheseMine` removed after the receipts were copied.

VERDICT: choose proposal 2 — the lane's proposal-disposition record is contradictory
(`round-86.md:115-116` vs `round-74.md:18` / `round-81.md:98-101`) and the one-off lesson table
that stood in for the ledger lapsed after round 75 (`round-75.md:87`); draft KQ141 above.
