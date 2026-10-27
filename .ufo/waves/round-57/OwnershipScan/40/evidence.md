# R57Item40OwnershipScan — counterpart-lane boundary for the canonical self-assessment gate

Axes: operability + calibration (lane `shokunin.conf` kama row; the historical MISSION example is
not resolved here). Read-only investigation; no source-tree, registry, SCORECARD, SKILL.md, LOG.md
or sibling-lane writes. No installs or tool upgrades were performed; pacman transactions remain
paused, so nothing is recorded under the tooling directive. Scratch lived at
`/fast/scratch/hyaku/kama-r57/R57Item40OwnershipScan/` (TMPDIR pinned inside it), receipts were
copied to this directory before cleanup.

## Question and boundary definition

"Canonical self-assessment gate" = the lane instrument that grades the lane's self-description
against its committed tree; in kama that is `tools/round42-selfdesc-reconcile.py` (registered at
`SKILL.md:1404`, whose `canon()` selects the highest `canonical list as of round N` heading and
parses its rows). Ownership is defined by `PROTOCOL.md` §Gate standard **Registry**
(`PROTOCOL.md:394-408`): a child lane's registry home is its own `SKILL.md`, and each row's eight
fields include an explicit **owner**; the integrator "does not execute a sibling's gate, whose
dependencies and write scope are the lane's" (`PROTOCOL.md:413-417`).

Two planes are checked separately: the **registry plane** (who is declared owner) and the
**execution plane** (what the gate actually does when pointed at a tree another lane owns).

## F1 — registry plane: one declared owner, and kama's row cannot declare one

`python3` scan of every lane's `SKILL.md` registry tables for rows matching
`self[- ]assess|self[- ]description` (`receipts/r09-registry-owners.out`):

- `tsukuroi` — 16 rows named `self-assessment`, each 8 cells with `OWNER=tsukuroi`
  (first at `SKILL.md:2356`; the row's entry command is `python3 tools/check-self-assessment.py
  --revision <REV>` and its owner cell is the literal `tsukuroi`).
- `kama` — 4 rows, all in **5-cell** tables with `NO-OWNER-COL`; the canonical gate row is
  `SKILL.md:1404` (`Round-42 C1 self-description reconcile …`), in the table headed at
  `SKILL.md:1387` (`| Name | Kind / entry command | Exit map | Self-test / pinned values |
  Write scope |`).
- `kaidoku` — 2 rows, 7 cells, no owner column.

kama's own registry carries two schemas for the same unit: 19 five-column tables vs 13 seven-column
tables with an `Owner` column (`receipts/r11-schema.out`: `header variants: {5: 19, 7: 13}`;
`tables with Owner column: [396, 430, … 886]`; the gate row's header is line `1387`). So the
counterpart lane declares its owner in the canonical shape and kama cannot: the canonical
self-assessment gate has no owner field anywhere in kama's registry.

No counter-claim exists either. Fleet-wide search for the gate's own token outside the lane
(`receipts/r10-gate-refs.out`):

```
count_outside_kama_excluding_fleet_reports=0
count_in_kama_skill=1
```

Only kama's `SKILL.md` registers it; the remaining hits are fleet round reports describing kama's
own rounds, not registry rows or gate executions. No lane's registry names kama's gate, and no
sibling gate source reads kama's `SCORECARD.md`/`SKILL.md` (search over `*.py|*.sh|*.mjs` outside
kama and `.ufo/` returned nothing; the only kama path in a sibling tool is
`souji-shokunin/tools/souji-quarantine.sh`, which takes an arbitrary `<repo>` argument as a
quarantine target and re-checks nothing in kama's self-assessment).

**Verdict for F1:** owner overlap in the registry plane is **absent** — one lane names the gate and
no sibling claims it — but the declared boundary is **inexpressible** on kama's side: the row that
owns the gate has no owner field, against `PROTOCOL.md`'s eight-field row.

## F2 — execution plane: the boundary is crossed and emits verdict classes

Both gates accept an arbitrary `--repo`/`--rev` (or `--tip`) and neither enforces lane ownership.

| Probe | Command (repo argument) | Exact summary | Exit | Receipt |
|---|---|---|---|---|
| P2 | tabi `scripts/check-selfassessment.mjs --repo <kama> --rev 8640e34c` | `SELFASSESSMENT verdict=clean rev=8640e34c… mismatches=0 could_not_evaluate=35 superseded=0` | `0` | `receipts/p2.out` |
| P5 | same gate `--repo <revenger> --rev HEAD` | `SELFASSESSMENT verdict=clean rev=1c5b748e… mismatches=0 could_not_evaluate=0 superseded=0` | `0` | `receipts/p5.out` |
| P7 | same gate `--repo <tabi> --rev HEAD` (owner control) | `SELFASSESSMENT verdict=clean rev=a1b1e939… mismatches=0 could_not_evaluate=116 superseded=48` | `0` | `receipts/p7.out` |
| P6 | same gate `--repo <empty dir> --rev HEAD` (negative control) | `SELFASSESSMENT verdict=could-not-evaluate detail=revision does not resolve: HEAD` | `2` | `receipts/p6.out` |
| P4 | kama `tools/round42-selfdesc-reconcile.py --repo <tsukuroi> --tip f6a46fa9` | uncaught `r41c1.EvalError: no line exactly '## Axes' in SCORECARD.md` traceback | `1` | `receipts/p4.out` |
| P1 | tsukuroi `tools/check-self-assessment.py --repo <kama> --revision 8640e34c` | `{"status": "CANNOT_EVALUATE", "error": "missing file", "detail": "tools/tsukuroi-census.sh", …}` | `2` | `receipts/p1.out` |

Readings:

1. **tabi's gate certifies kama's self-assessment clean.** P2 emits `verdict=clean` for kama's tree
   while every finding is `could-not-evaluate` (`mismatches=0 could_not_evaluate=35`; all 35 lines in
   `p2.out` are `class=m4-nudge-state … could-not-evaluate=no 'Axes at round start:' with all six
   axes in the round group`). CNE findings are excluded from the mismatch tally, so a tree the gate
   cannot parse reads as a clean verdict. The same clean verdict appears on a third lane (P5) with
   `could_not_evaluate=0`, and on the owner's own tree (P7) with 116 CNE — so `clean` is not an
   ownership-scoped or data-bound result at all; it is the gate's default when nothing matches.
   Only a tree whose revision does not resolve is refused (P6, exit 2).
2. **kama's gate emits a failed-class verdict on a sibling tree.** P4 exits `1` — which its own
   registry row maps to `1 not met` — with an uncaught `EvalError` traceback, although the same row
   maps `EvalError` to `2 could not evaluate` (`SKILL.md:1404`, exit-map cell: "2 could not evaluate
   … from an EvalError"). The predicate `## Axes` is kama-specific, so the traceback is the honest
   signal that the gate is not tree-agnostic — but the process still leaves a verdict-class code
   (`1`) that a reader could record as a found lane's failed state.
3. **tsukuroi's gate refuses kama's tree** (P1, exit 2, `CANNOT_EVALUATE`), but only incidentally:
   its K13 reads its own `tools/tsukuroi-census.sh`, which does not exist in kama. No principled
   owner guard exists in any of the three gates.

**Verdict for F2:** owner overlap in the execution plane is **present in both directions** — a
counterpart lane's canonical self-assessment gate returns `clean` on kama's tree (a false clean over
35 CNE), and kama's gate returns `1 not met` (traceback) on a counterpart tree, contradicting its
declared exit map.

## F3 — owner-side controls (the gate is real on its own tree)

- Frozen base `b89bdab2cc114735ec5d331c6c610134258f7864`: `receipts/p8.out` reads
  `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0
  mismatches=1 maxN=56 met=False`, exit `1`, with the single `detail:` line quoting the R41
  calibration command expecting `42`. This reproduces `controls/base-c1.out` byte-for-byte in its
  summary line.
- Lane HEAD `8640e34cad02adcd247ba0862da63f6fb2aab0df` (post-freeze commits `89dc4f52`, `7c873d7b`,
  `7b74e2f2`, `8640e34c`): `receipts/p3.out` reads `mismatches=0 maxN=57 met=True`, exit `0`.
- Canonical content binding on a fixture clone of branch HEAD `77e7f5ee`
  (`.ufo/waves/round-57/reports/R57Item40OwnershipScan-case61.md` §Arm C): unmutated
  `mismatches=0 maxN=57 met=True` exit 0 (`receipts/case61-p9.out`); one canonical row deleted →
  `retired=1 caps=1 mismatches=2 met=False` exit 1, with the detail lines naming the missing row
  `live-receipt-replay` (`receipts/case61-p10.out`); the newest canonical heading deleted while the
  byte-identical round-48 list remains → `mismatches=0 maxN=57 met=True` exit 0
  (`receipts/case61-p11.out`). `canon()` selects the highest *present* heading, so removal of the
  newest canonical list is invisible.
- Canonical data at HEAD (independent parse of `git show 8640e34c:SCORECARD.md`): highest canonical
  heading is `**Capabilities — canonical list as of round 49**`, its table holds 11 data rows
  (`sources-registry`, `ollama-offline-evidence-replay`, `live-llamacpp-lifecycle`,
  `gguf-declared-identity-replay`, `context-capacity-receipt`, `instrument-agreement`, `pin-watch`,
  `digest-ledger`, `hexrun-census`, `append-only-audit`, `live-receipt-replay`); `## Round` headings
  number 58 with maximum 57 at HEAD and 57 headings with maximum 56 at the frozen base.
  The canonical row count is therefore 11, the canonical heading round is 49, and `maxN` is the
  round-heading maximum, not a capability-row count. The frozen instruction's "expected 46" matches
  neither (it equals the round-46 receipt's `maxN`), so the frozen base reading is bound to a stale
  historical numeric, not to canonical rows. This seat does not adjudicate C1/C2; the number is
  recorded for the owners of those claims.

## Conclusion — owner overlap

- Registry plane: **no overlap**; kama is the only owner by reference (0 sibling registrations,
  0 foreign owner cells fleet-wide), but kama's owning row omits the `PROTOCOL.md` owner field while
  the counterpart lane's row carries `OWNER=tsukuroi`.
- Execution plane: **overlap** — tabi's canonical self-assessment gate returns `verdict=clean` on
  kama's tree with 35 CNE and on a third lane with 0 CNE; kama's gate returns exit `1` with an
  uncaught traceback on tsukuroi's tree against its declared `2 could-not-evaluate` mapping. No gate
  enforces its lane's ownership of the tree it grades.
- Canonical selection inside the owned gate: **row content is bound** (deleting one canonical row
  reads `met=False`), but **the newest canonical list is not** — deleting the round-49 heading falls
  back to the identical round-48 list and still reads `met=True`. Any claim that the gate binds the
  canonical list's existence needs a heading-existence leg that this counter does not have.

## Advice (no edits made; dispatched lane-authors own these files)

1. kama's registry rows for the canonical self-assessment gate should carry the eight
   `PROTOCOL.md:401-406` fields, including `owner`; the lane currently runs two registry schemas
   (19 × 5-column, 13 × 7-column) for one unit.
2. A gate repointed at a foreign tree should refuse with the CNE code instead of emitting a
   clean/failed class — for kama that means classifying a missing `## Axes`/lane marker as
   `could-not-evaluate` (exit 2) rather than an uncaught `EvalError` that exits 1.
3. A consumer that reads `verdict=clean` from a sibling's self-assessment gate must also read
   `could_not_evaluate`; P2's `clean` with `could_not_evaluate=35` is a false green of exactly the
   class the round's C1/C2 controls target.

## Separability

F1 (registry/owner declaration) is verifiable without F2/F3: it reads only `SKILL.md` registry
tables. F2 requires the two gate binaries. F3 requires only kama's counter plus git blobs.

## Adjacency

The lane-context non-author spot-check (re-open `corpus/SOURCES.md` row S515, Git config runtime
environment pairs, against the Git manual and the round-56 lesson quote; one admit/reject decisions
spot check) belongs to the sources/reopen and closure seats. This dispatched lane-author seat did
not read or quote S515 and offers no second ruling; per the wave rules that duty is advisory here.

## Replay

All commands, revisions and exit codes are in `commands.txt`; each table row's raw output is the
named file in `receipts/`.

Report: .ufo/waves/round-57/w1/out/R57Item40OwnershipScan.md
