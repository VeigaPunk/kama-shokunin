# ScoutReportLineage — r32 c2r claim vs. receipt contents and creation history

Scope: reconstruct the round-32 c2r claim against the committed receipt bytes and
`git log --diff-filter=A`. Lane repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`
(jj-colocated, branch master). Read-only git only; no mutations performed.

## The claim under reconstruction

Filed fleet report `/home/vgpnk/Projects/shokunin/.ufo/reports/round-32/kama.md`
(fleet repo, added by fleet commit `1d9840bb5c30bdc7012ef20399956c1769a2a964`
"round-32: kama report", 2026-10-24T03:18:39-03:00; not tracked in the lane repo —
lane `.ufo/reports/` contains only `round-5`). Bullet at lines 99–101:

> "Receipt lineage honesty: `c2r/c2r-tip.json` and the gate/selftest finals measure
> the data tip `967d88528c1d` and are committed in `3f1a7330`; SCORECARD cites the
> data tip `c4c46ad5b87d` for the row revisions (ancestor of the tip)."

## Receipt contents (observed)

`.ufo/waves/round-32/c2r/c2r-tip.json` (214 lines) records in its own fields:

- `"tip": "dc4258bdb08d658f1c5b15abc8378461659bd155"` (line 3) — the measured
  revision is the docs commit `dc4258bd`, not `967d8852`.
- `"summary": "... met True tip dc4258bdb08d"` (line 2) — same.
- `"base": "07794a4d30a54a60ebdff50ac76d12c6df40a0f1"` — the counter-internal base
  field (same value appears in `c1/before-base.json`); the *claim* base differs
  (`18464d08…` below).
- Counts `rows 30 base_mismatched 13 exempt 1 valid_corrections 13
  false_corrections 0 unresolved 0 append_only True met True` — match the report's
  after-numbers verbatim, so the measured values are right; only the revision
  attribution is wrong.

Companion receipts in the same lane tree:

- `.ufo/waves/round-32/c1/before-base.json`: `"tip": "18464d0866afd5c4b471c8478d72b079d82d1fa8"` — the C1 before/base.
- `c2/gate-tip.out` (`registered 10 unregistered 0 defective 0`) and
  `c2/selftest-final.out` (`PASS …` lines) — the "gate/selftest finals".
- `c2/gate-data-tip.out` / `c2/selftest-data-tip.out` — separate earlier receipts;
  `gate-data-tip.out` itself shows `defective …/count-c2r.py: missing-path:…/c2r/c2r-tip.json`, i.e. it ran on a tree before the receipt existed.

## Creation history (read-only `git log --diff-filter=A`, lane repo)

| Receipt path | First added by | Commit subject |
|---|---|---|
| `.ufo/waves/round-32/c2r/c2r-tip.json` | `967d88528c1d83535563f971863f7855f76b4849` (2026-10-24T03:15:16-03:00) | "round-32: receipts — C1 after (met True, valid 13), C2 data-tip gate/selftest, KQ36 re-runs …, census end exit 0" |
| `.ufo/waves/round-32/c2/gate-tip.out`, `c2/selftest-final.out` | `3f1a73308bec9c2f4497c557d01bc58ec8e72eca` (03:16:02) | "round-32: final receipts — gate/selftest at data tip 967d88528c1d" |

`git show --stat` confirms `967d8852` added exactly: `c2r-tip.json`,
`gate-data-tip.out`, `selftest-data-tip.out`, `census-end.out`, four `kq36/*`
receipts (991 insertions); `3f1a7330` added exactly: `gate-tip.out`,
`selftest-final.out` (8 insertions).

Parent chain (verified via `git log -1 %P`):
`c4c46ad5` → `dc4258bd` → `967d8852` → `3f1a7330` — each named commit is the
parent of the next; `dc4258bd` is a strict ancestor of `967d8852`.

## Measured tip vs. receipt commit — the distinction the bullet conflates

- `c2r-tip.json` **measures** `dc4258bd` (its own `"tip"` field) but **was
  committed in** `967d8852` — plausible mechanically: `967d8852`'s only tree delta
  vs. `dc4258bd` is the receipt files themselves, so a counter run on the
  `967d8852` worktree targeting the pre-receipt state (or run before commit and
  recorded with tip `dc4258bd`) produces identical counts.
- `gate-tip.out`/`selftest-final.out` **measure** the `967d88528c1d` lane tip
  (per their commit subject and report line 89) and **were committed in**
  `3f1a7330`.

So "measure the data tip `967d88528c1d`" + "committed in `3f1a7330`" is the true
lineage of the gate/selftest finals only; the bullet wrongly extends it to
`c2r-tip.json`.

## The false sentence (identified)

`.ufo/reports/round-32/kama.md:99-101` —

> "`c2r/c2r-tip.json` and the gate/selftest finals measure the data tip
> `967d88528c1d` and are committed in `3f1a7330`"

is **false as written, in both conjuncts as applied to `c2r-tip.json`**:

1. `c2r-tip.json` records `tip=dc4258bdb08d658f1c5b15abc8378461659bd155`, not `967d88528c1d`.
2. `c2r-tip.json` was first added by `967d88528c1d83535563f971863f7855f76b4849`, not `3f1a73308bec9c2f4497c557d01bc58ec8e72eca`.

Internal corroboration: the same report's "Landed changes" table (line 62) already
says `967d8852` = "`c2r/`, `c2/` data-tip receipts, `kq36/` re-runs, census end"
and line 63 says `3f1a7330` = "final receipts (gate/selftest at data tip)" — the
bullet contradicts the report's own table on which commit added `c2r/`.

Nuance: report line 75–76 calls the after-measurement "data tip `967d88528c1d`
(re-run of the `dc4258bd` measurement, receipt `c2r/c2r-tip.json`)". The
*"re-run at 967d8852 produced identical counts"* framing is plausible (receipts
are the only delta), but the receipt bytes pin the measured revision field to
`dc4258bd`; the bullet then upgraded "re-run" into "measures 967d88528c1d".

The second clause "SCORECARD cites the data tip `c4c46ad5b87d` for the row
revisions" — `c4c46ad5` is the C2 gate commit, parent of `dc4258bd`; this wording
is loose but the clause is not what the routed defect targets. (The lane
SCORECARD grep shows no literal "cites the data tip" phrasing to verify verbatim;
report's own characterization.)

## Round-33 erratum already appended (observed)

Lane `SCORECARD.md` §"Round-32 filed report receipt-lineage correction (routed
defect 1)" (lines ~1848–1858) quotes the sentence verbatim and records:
`tip=dc4258bd…` first added by `967d8852…`; `gate-tip.out`/`selftest-final.out`
record the `967d88528c1d` run, added by `3f1a7330…`; filed report not rewritten.
My independent reconstruction agrees field-for-field. Round-33 report line 16
carries the same correction.

## Confidence & remaining unknowns

- **High confidence** on the false-sentence identification: receipt `"tip"` field
  (direct bytes) + `--diff-filter=A` creation commit + `git show --stat` file
  lists all agree; no conflicting evidence.
- Unknown / not resolved (out of scope): whether a counter run against the exact
  `967d8852` tree would print `tip 967d88528c1d` (the counter records the `--tip`
  argument, and `gate-data-tip.out` shows the gate flagging `c2r-tip.json` as
  missing on the pre-receipt tree — consistent with the run targeting `dc4258bd`).
- `git log --diff-filter=A` on `.ufo/reports/round-32/kama.md` was run in the
  **fleet** repo (the filed report is not a lane-tracked file); result:
  `1d9840bb5c30bdc7012ef20399956c1769a2a964`.
- No tool installs needed; all evidence from `git log`/`git show` and file reads.

Report: `.ufo/waves/round-33/w1/out/ScoutReportLineage.md` (this file).
