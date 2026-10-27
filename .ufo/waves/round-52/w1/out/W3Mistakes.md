# W3Mistakes — round-52 lesson `## Mistakes` rows (draft)

**Verdict:** five mistakes rows drafted for `corpus/lessons/round-52.md` — the four routed
ones (D1 report-before-WAVE-DONE, D3 receipt-that-does-not-read-that-way, X7Regen/D1
in-place rewrite, plus a round-52 build defect) and one recurrence of round-50 Mistakes #2
(untracked wave markers); each fix is a runnable check, and each check is shown both
passing and failing (fixture + real history). No lane file was modified.

## Deliverable

`.ufo/waves/round-52/w1/out/W3Mistakes/mistakes.md` — the rows, the evidence table, and the
limits. It is a drop-in `## Mistakes` section for the round-52 lesson (which at the build
`5dacf2c7` carries only `## Claims` and `## Gate`).

## Rows and their evidence (all exits from commands run here)

| Row | Class | Evidence | Check proposed | Real-history run |
|---|---|---|---|---|
| 1 | Report filed before the wave landed its seat output (D1) | fleet `.ufo/reports/round-51/kama.md` added at `39877b17` (author `01:11:01-03:00`); lane `9ff76b1f` (author `01:27:15-03:00`, +974 s) "…salvage of a2w1 seat output written after the round's report landed (closure rounds[802], defect D1), plus the wave results record", adding `a2w1-results.json` + 15 seat reports | `report-wave-order.py` | round 51 **exit 1** (`report BEFORE by 974s`, both legs); rounds 49/50 **exit 0**; round 52 **exit 2** (no report yet) |
| 2 | Claim firmed up against receipts that read the other way (D3) | `SCORECARD.md:2927` at `1ab1de39` and at `5dacf2c7`: "The planned-pointer check resolves only once this subsection exists (receipt at the final tip)." Receipts at that tip: `pointer.out` (`tip=be8169a6`) `met=False`, `pointer-int.out` (`tip=c5ec93d5`) `met=False`; only `pointer-build.out` (`tip=73bf2a7a`) reads `met=True`. Fleet report `.ufo/reports/round-51/kama.md:79` repeats it | `claim-vs-receipt.py` | **exit 1** at `1ab1de39` *and* at the build (`UNCITED SCORECARD.md:2927 round=51 want=met=True`) — the erratum has not landed |
| 3 | Committed seat report rewritten in place (D1) — remediation covered 1 of 10 | `X7Regen.md` blob `d0be0660…` at `1ab1de39`; rewritten by `9ff76b1f` (13+/13−) and restored by `5dacf2c7` with `X7Regen.late-rewrite.md` (byte-identical to the pre-restore file). Nine other reports still differ from their first-add blobs: r25 `ReviewerC1Patch/evidence.md`, r47 `S9Cap.md` + `S9Cap/{companion-head-and-province,receipt}.md` + `S9Scorecard/head-reanchors.md`, r48 `Sen2Live.md`, r49 `Sen1Witness.md`, `X1Kill.md`, `X1Sparse/table.md`; no `registry/append-only-contract.tsv` row covers `.ufo/waves/*/out` | `seat-report-immutability.py` | `9ff76b1f` **exit 1**, 10 violations (X7Regen named); `5dacf2c7` **exit 1**, 9 violations (X7Regen resolved, the nine stand) |
| 4 | New instrument registry cites receipts that do not exist (row-2 class, same round) | `SKILL.md:1545` at `5dacf2c7`: "…before landing (`.ufo/waves/round-52/measured/*-pre.out`)". At `5dacf2c7` that directory holds only `measure.sh`; the glob matches 0 paths at `5dacf2c7` and at `34d82600`; the tree's only `*pre.out` is unrelated (`.ufo/waves/round-32/c2/selftest-pre.out`) | `cited-path-exists.py` | **exit 1**, `misses=51 new=1` at both `5dacf2c7` and `34d82600`; the one new miss is the `*-pre.out` glob |
| 5 | Wave markers untracked — repeat of round-50 Mistakes #2 | at `34d82600` round-52 has 0 committed `.ufo/waves/round-52/*.ready*` files; rounds 49/50/51 have 2 each; worktree `w1.ready` (148 B, 02:05) and `w1.ready.dispatched` (1779 B, 02:14) are untracked and not ignored (`git check-ignore` rc 1) | tree assertion in the round-closing commit | same command returns 0 for round 52, 2 for rounds 49–51 |

## Checks shown able to fail *and* to pass

`fixture-checks.sh` / `fixture-checks.out` (fixture repo in scratch, `git init` + fixture
identity, toplevel asserted):

- A1 ordered fixture → `report-wave-order` exit 0; A2 a 15th seat report authored after the
  report → exit 1 (`report BEFORE by 10800s`).
- B1 untouched → `seat-report-immutability` exit 0; B2 in-place rewrite → exit 1; B3 restore
  + `.late-rewrite.md` sibling → exit 0.
- C1 pointer receipt `met=True` → `claim-vs-receipt` exit 0; C2 receipt flipped to
  `met=False` → exit 1.
- D1 all citations present → `cited-path-exists` exit 0; D2 phantom `*-pre.out` glob → exit 1
  (`new=1`); D3 citation fixed → exit 0.

Real-history capture: `checks-real.out`.

## Verified in the build and not reported as mistakes

Independent recomputation, not the build's own receipts: all **155** restored lines are
verbatim deletions of the commits their blocks name (`checked_lines 155 non_verbatim 0`,
18 files, 45 blocks); ledger 166 → 11 lines (165 → 10 rows, 155 removed; 7 SOURCES + 3
errata); `X7Regen.md` blob equals `1ab1de39`'s `d0be0660…` and the late-rewrite file is
byte-identical to the pre-restore bytes; head re-anchors re-derive (`SKILL.md`
`e749b350…f154`, 1558 lines, 40 `## `; 38 spot-check blobs); frozen counter bytes equal the
preregistration (`053ff502…121f5`, `29dfd886…53ea`); the freeze timestamp is 7 s *before*
its commit (`04:42:00Z` vs `04:42:07Z`, no KQ64 flag); the new hexrun `wrong` row is
well-formed and its `correct` hash resolves to a real lane commit
(`git cat-file -t 907cdcc0…a50725…` → `commit`; receipt `unknown=0 ledger_bad=0`).

## Touched surfaces

- Wrote: `.ufo/waves/round-52/w1/out/W3Mistakes/` (this report's evidence) and
  `.ufo/waves/round-52/w1/out/W3Mistakes.md` (this report).
- Lane, fleet and siblings: read-only (`git show`, `git log`, `git cat-file`, `git
  ls-tree`, `git status --porcelain`, `grep`, `find`). No commit, checkout, add or stash in
  the lane; no write at the fleet root; the scratch clone was `git clone --shared` in
  `/fast/scratch/hyaku/kama-r52/W3Mistakes/` and was deleted.
- No frozen counter was run (C1 downloads ~75 MB and starts servers; its numbers are cited
  as the L1's). No `llama-server` was started by this seat.

## Out of scope / for the L1 at integration

- Row 4's fix is a sentence edit in `SKILL.md` §Round-52 instrument registry (cite the
  receipts that exist, or land a `*-pre.out` set) — the lane's file, so it is proposed here
  only.
- Row 3's finding (nine older in-place rewrites) needs a decision, not a silent edit: adopt
  the sibling convention retrospectively, or scope the rule in `registry/append-only-contract.tsv`.
- Row 2's erratum is already scheduled for round-52 integration (D2/D3/D4/D6); the sentence
  at `SCORECARD.md:2927` is still false at the build, and my check will keep failing until
  the errata row replaces it.
- Row 5 is a tree assertion for the round-closing commit; it is outside the assigned build
  range (`…5dacf2c7`) because the markers were written after it.

## Limits

- `report-wave-order.py` decides on author time and counts only *added* seat reports.
- `seat-report-immutability.py` treats every `.ufo/waves/*/*/out/**/*.md` as a seat report
  (1806 paths, ~2 min) and knows only the `.late-rewrite.md` sibling as an authorised edit.
- `claim-vs-receipt.py` is targeted at pointer sentences in measured-results sections.
- `cited-path-exists.py` has 50 pre-existing misses at the base, so only the `--base` delta
  is decision-bearing.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/mistakes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/cited-path-exists.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/seat-report-immutability.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/report-wave-order.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/claim-vs-receipt.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/fixture-checks.sh`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/fixture-checks.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/checks-real.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/receipt-round51-pointer.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/receipt-round51-pointer-int.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/receipt-round51-pointer-build.out`
