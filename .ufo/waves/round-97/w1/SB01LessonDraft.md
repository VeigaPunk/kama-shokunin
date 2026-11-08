# SB01LessonDraft — round-97 prose draft: lesson §Gate/§Mistakes, report §Sources & frontier, §Before → after

**Seat:** `SB01LessonDraft` (scribe) · **Lane:** `kama-shokunin`
(`/home/vgpnk/Projects/shokunin/kama-shokunin`) · **Milestone:** `kama r97 w1`
**Axes:** operability, calibration, depth · **Status:** complete — draft delivered, nothing committed

**Base** `40763bd2ca1e3f99881247eaa9f5e3ef3b596653` (round-96 closure `rejected-honest-stop`) ·
**Freeze** `9e605d41` · **Amendment 1** `e057166e` (C2 `--slow-files 72`).

## Deliverable

The prose draft is at
`.ufo/waves/round-97/w1/out/SB01LessonDraft/SB01LessonDraft.md`, with receipts at
`.ufo/waves/round-97/w1/out/SB01LessonDraft/receipts/`. It contains:

1. **§1 — the lesson's `## Gate` table, rewritten.** Four rows (S620 admit, S621 admit, S619
   reject, `llama.cpp docs/gguf.md` @ b12177 path-absent reject), each with URL, access date
   (2026-11-08), the `sha256` recomputed from the fetched bytes, and a ≤25-word located quote.
   This seat re-fetched all three sources and reproduced the committed digests exactly
   (`receipts/sources-opened-recheck.txt` vs `controls/sources-opened.out`).
2. **§2 — the lesson's `## Mistakes` rows, rewritten** so each carries class, a resolved
   evidence pointer, captured-by, and a fix with a **committed** "shown able to fail" receipt
   (M1–M3; M4 recommended for removal, see finding F5).
3. **§3 — the report's `## Before → after measurements`** for C1/C2/C3, with `<<measured:…>>`
   placeholders wherever the L1 has not yet measured a number, and every measured figure quoted
   from the receipt that carries it.
4. **§4 — the report's `## Sources & frontier` paragraph** (rows before → after with the census
   command, rows added by tier, rows touched old → new, frontier rows advanced).
5. **§5 — the report's `## SHONEN` block**, one `[~]` line per `SHONEN.md` box in box order,
   which is what the round-96 closure's conformance defect 1 requires
   (`corpus/lessons/round-96-verifier-spotcheck.md:39-44`).

## Behaviour — what this seat did

Read-only against committed bytes; the only writes were this seat's out directory and its scratch
(now removed). No tracked lane file was edited; no `git add/commit/stash/checkout/switch/reset/pull/push`
and no mutating `jj` command was run — the only git verbs used were read-only (`show`, `log`,
`diff`, `rev-parse`, `status`, `ls-files`), plus `merge-base` inside the frozen counter. The fleet
repo was read only (the report skeleton, `scripts/sources-census.sh`,
`scripts/hyaku/prefile-falsification.py`); nothing under the fleet root was written.

Commands actually run, with their real output:

| Command | Result |
|---|---|
| `python3 tools/round97-self-assessment-audit.py --repo . --rev 40763bd2` | `SELF_ASSESS97 checks=14 mismatches=9 met=False`, exit 1 |
| `python3 tools/round97-self-assessment-audit.py --repo . --rev 9e605d41` | `SELF_ASSESS97 checks=14 mismatches=0 met=True`, exit 0 |
| `python3 tools/round97-depth-boundary-audit.py --repo . --rev 40763bd2` | `DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False`, exit 1 |
| `python3 tools/round97-depth-boundary-audit.py --repo . --rev 9e605d41` | `DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True`, exit 0 |
| `scripts/sources-census.sh validate --root … kama` | exit 0, `kama ok …` |
| `scripts/sources-census.sh census --root … kama` / `--file <base blob>` | 361 rows (A 344 / B 11 / C 6; mined 324 / queued 8 / rejected 29) vs 358 rows (A 342 / B 11 / C 5; mined 322 / queued 8 / rejected 28) |
| `scripts/hyaku/prefile-falsification.py --lane kama --round 97` | `FINDING wave-missing …/w1-results.json`, `FINDING ledger-missing …/claim-falsification.tsv`, `SETUP findings=2`, exit 2 |
| `curl` re-fetch of the three round-97 sources | HTTP 200 ×3 with digests matching `controls/sources-opened.out`; HTTP 404 for `llama.cpp docs/gguf.md` @ b12177 |
| per-check instrumentation of the C1 counter (copy in scratch) | base: 9 mismatches over 14 checks, each traced to its source line; freeze: 0 |

## Gates

- **Bounds:** honoured. Writes only under `.ufo/waves/round-97/w1/out/SB01LessonDraft/` (plus the
  `Report:` trailer path, which is inside the wave's report dir alongside the other seats'
  reports) and `/fast/scratch/hyaku/kama-r97/SB01LessonDraft/`.
- **Scratch:** created, receipts copied into the out dir first, scratch removed on exit.
- **Fixtures/clones:** none created; no git mutation of any kind.
- **Tools:** none installed, upgraded or removed — the existing toolchain was sufficient
  (`git`, `python3`, `bash`, `curl`, `grep`, `sha256sum`). `pacman` untouched (paused host-wide by
  the orchestrator ruling of 2026-10-20). No host service restarted, no sysctl written, no
  unbounded process started.

## Touched surfaces

- **Written:** `.ufo/waves/round-97/w1/out/SB01LessonDraft/SB01LessonDraft.md` (the draft),
  `.ufo/waves/round-97/w1/out/SB01LessonDraft/receipts/*` (9 receipts),
  `.ufo/waves/round-97/w1/SB01LessonDraft.md` (this report).
- **Read only:** `plans/round-97-claims.md`, `plans/round-97-amendment-1.md`,
  `corpus/lessons/round-97.md`, `corpus/lessons/round-96-verifier-spotcheck.md`,
  `corpus/SOURCES.md`, `corpus/QUALITY.md`, `SKILL.md`, `SCORECARD.md`, `SHONEN.md`,
  `tools/kama-probe.sh`, the three round-97 counters, `.ufo/waves/round-97/{controls,measured}/*`,
  `.ufo/waves/round-97/claims.json`, and the fleet report skeleton.
- **Out of scope / not touched:** every tracked lane file; the lane's Git index; sibling lanes; the
  fleet repo's tracked files; the frozen plan, the frozen counters, and the frozen predicates.

## Findings (the L1 must weigh these before integrating)

Full text, with file:line and the command that shows each, is in the draft's §0.

- **F1 — the frozen C2 predicate says "three new cells"; the counter grades four.**
  `plans/round-97-claims.md:76-77` vs `NEW_CELLS` at `tools/round97-router-budget.py:146` (four
  members) and `cells=4` in every new-cell block of `controls/c2-new-mutants.out`. The counter's
  own docstring says "Round 97 adds three cells past that:" and then lists four
  (`tools/round97-router-budget.py:13-26`). `CELLS = 17` is consistent with 13 + 4. The substance
  (17 cells, four new cells, four mutants each caught once) is what the receipts show; "three" is
  a stale count in the frozen prose. No frozen instrument grades the plan or the docstring, so
  nothing catches it. **The report prose must use 17 / four / four.** The connector seat's
  proposed move (`.ufo/waves/round-97/w1/CN01Overlap.md`) reaches the same conclusion from the
  other direction.
- **F2 — `SKILL.md` §Round 97 correction names three graded forgeries; the counter grades four.**
  `SKILL.md:2463-2467` lists three variants and maps them to W14/W15/W16; the fourth mutant
  `nopreamble` (`tools/round97-router-budget.py:174-175`), caught by W17, is absent. Neither the C1
  counter (which grades only its 14 named surfaces) nor the C3 counter (which grades only the six
  boundary rows) grades that sentence. **Editing `SKILL.md` requires re-stating SCORECARD's live
  `depth` row digest/line count/section count in the same commit**, or C1 check 1 flips to a
  mismatch — the risk the connector seat also flags.
- **F3 — the lesson's M2 cites a byte string that exists nowhere in the tree.**
  `corpus/lessons/round-97.md:44` cites `struct.pack("<II", 8, 0)`; `grep -rn` finds it only in
  the lesson itself. The committed fixture already writes the **fixed** two-field KV encoding
  (`tools/round97-router-budget.py:253-254`), and no committed receipt shows the pre-fix
  `caught=0` state. The defect may well be real (the L1 found it while authoring, before the
  freeze), but the lesson must cite the committed writer and the receipt pair
  (`controls/c2-new-mutants.out:6` and `:27`), not a byte string the tree does not contain.
- **F4 — the lesson's M3 fix names a file that does not exist yet.**
  `.ufo/waves/round-97/claim-falsification.tsv` is absent, as is `w1-results.json`; the fleet gate
  refuses with `ledger-missing` / `wave-missing` and exit 2. Write M3 as a fix **to be landed**.
- **F5 — M4 misattributes a routed defect to wave-1.** `corpus/lessons/round-97.md:58-62` gives
  "captured-by: the round-96 closure step 1" while reading as a defect this round's wave caught.
  It is routed defect 2 (`plans/round-97-claims.md:11-14`), already answered in the lesson's
  `## Routed-defect answers` (`:68-76`). Recommend dropping M4 from `## Mistakes`.
- **F6 — the fleet report skeleton still holds `<<measurements>>` and `<<shonen>>`.**
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-97/kama.md:43` and `:75`; this draft's §3–§5
  fill both.
- **F7 — the plan counts the lesson's Gate as three rows; the lesson's Gate has four.**
  `plans/round-97-claims.md:138-139` ("one admit, two rejects") vs the four rows at
  `corpus/lessons/round-97.md:15-18` (two admits — one of them a correction row — and two
  rejects, one of them not a registry row). The L1 should reconcile the two; the plan is frozen
  and this seat cannot edit it.

## What was verified vs what is a placeholder

Verified by this seat (numbers quoted from committed receipts, reproducible from the commands
above): the C1 counter's red/green pair and the identity of all nine base mismatches; the C3
counter's red/green pair and the re-derivation of all six boundary rows from
`MAX_STEPS = 5_000_000` with `steps = 4 + T x (5 + nd)`; the census row/tier/status deltas; the
three source digests and the 404; the four legacy-survival and four new-catch control blocks; the
absence of the round-97 ledger and wave results; the absence of the M2 byte string.

Left as `<<measured:…>>` (not measured by the L1 yet, and not guessed here): C1's after-line and
exit at M1, C2's after-line and exit at M2, C3's after-line and exit at M3. `measured/c2.out` is
empty at the time of this draft (the L1's run is in flight); `measured/c1.out` and
`measured/c3.out` already carry green lines but are uncommitted and are not bound to a named
revision, so the draft quotes them as interim and asks the L1 to re-quote after the measurement
commit is fixed.

## Not claimed

This seat is the scribe: it drafts prose and reports conflicts; it does not decide, amend, commit,
or file. The lesson draft is not the landed `corpus/lessons/round-97.md`, and the report skeleton
is not the filed report. Whether round 97's claims hold is the L1's to measure and the non-author
closure's to judge.
