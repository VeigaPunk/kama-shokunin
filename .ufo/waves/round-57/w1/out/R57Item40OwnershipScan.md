# R57Item40OwnershipScan — counterpart-lane boundary for the canonical self-assessment gate

Seat: leaf simplifier, item `round57/OwnershipScan/40`. Axes: operability + calibration (lane
`shokunin.conf` kama row; the historical MISSION example is left unresolved). Build/attack wave:
this is evidence, not a closure judgment, and no source or shared file was edited. No installs or
upgrades were performed; pacman transactions remain paused. Scratch lived at
`/fast/scratch/hyaku/kama-r57/R57Item40OwnershipScan/` (TMPDIR pinned inside it); every receipt was
copied to `.ufo/waves/round-57/OwnershipScan/40/receipts/` before cleanup.

Question: does a counterpart lane own or claim the canonical self-assessment gate that kama's
C2 subject (actual canonical-row execution/content binding) belongs to, and does the boundary hold
when either side's gate is pointed at the other's tree?

Definition used: kama's gate is `tools/round42-selfdesc-reconcile.py`, registered at
`SKILL.md:1404`, whose `canon()` takes the highest `canonical list as of round N` heading and its
rows. Ownership per `PROTOCOL.md:394-417`: registry home = the lane's own `SKILL.md`; each row has
eight fields including an explicit **owner**; the integrator does not execute a sibling's gate.

## Finding 1 — registry plane: one name, but kama's row cannot declare an owner

- Fleet scan of every `*/SKILL.md` registry table for `self[- ]assess|self[- ]description` rows
  (`OwnershipScan/40/receipts/r09-registry-owners.out`): `tsukuroi` carries 16 rows named
  `self-assessment`, each **8 cells** with `OWNER=tsukuroi` (first at `SKILL.md:2356`, entry
  `python3 tools/check-self-assessment.py --revision <REV>`); kama carries 4 rows, all **5 cells**
  with **no owner column**, including the canonical gate row at `SKILL.md:1404` (table header at
  `1387`: `| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`).
- kama's registry runs two schemas for one unit: **19 five-column tables vs 13 seven-column tables
  with `Owner`** (`receipts/r11-schema.out`: `header variants: {5: 19, 7: 13}`).
- No counter-claim: `round42-selfdesc` occurs **0** times outside kama's tree (excluding fleet round
  reports) and **1** time in `kama-shokunin/SKILL.md` (`receipts/r10-gate-refs.out`). No sibling
  gate source reads kama's `SCORECARD.md`/`SKILL.md`; the only sibling reference to a kama path is
  `souji-shokunin/tools/souji-quarantine.sh`, which takes an arbitrary `<repo>` target and grades no
  self-assessment.

Reading: owner overlap in the registry plane is **absent**, but the declared boundary is
**inexpressible** on kama's side — the row that owns the gate has no owner field while the
counterpart lane's row names its owner. `PROTOCOL.md:401-406` requires that field.

## Finding 2 — execution plane: the boundary is crossed and emits verdict classes

| Probe | Command | Exact result | Exit |
|---|---|---|---|
| tabi gate → kama @`8640e34c` | `node tabi-shokunin/scripts/check-selfassessment.mjs --repo <kama> --rev 8640e34c…` | `SELFASSESSMENT verdict=clean … mismatches=0 could_not_evaluate=35 superseded=0`; all 35 findings are `class=m4-nudge-state … could-not-evaluate=no 'Axes at round start:' with all six axes in the round group` | `0` |
| tabi gate → revenger @HEAD | same gate `--repo <revenger> --rev HEAD` | `SELFASSESSMENT verdict=clean … mismatches=0 could_not_evaluate=0 superseded=0` | `0` |
| tabi gate → tabi @HEAD (owner control) | same gate `--repo <tabi> --rev HEAD` | `SELFASSESSMENT verdict=clean … could_not_evaluate=116 superseded=48` | `0` |
| tabi gate → empty dir (negative control) | same gate `--repo <empty dir> --rev HEAD` | `SELFASSESSMENT verdict=could-not-evaluate detail=revision does not resolve: HEAD` | `2` |
| kama gate → tsukuroi @`f6a46fa9` | `python3 kama-shokunin/tools/round42-selfdesc-reconcile.py --repo <tsukuroi> --tip f6a46fa9…` | uncaught `r41c1.EvalError: no line exactly '## Axes' in SCORECARD.md` traceback; the gate's own row maps `EvalError` to `2 could not evaluate`, not `1` | `1` |
| tsukuroi gate → kama @`8640e34c` | `python3 tsukuroi-shokunin/tools/check-self-assessment.py --repo <kama> --revision 8640e34c…` | `{"status": "CANNOT_EVALUATE", "error": "missing file", "detail": "tools/tsukuroi-census.sh", …}` | `2` |

Receipts: `receipts/p2.out` (35 CNE lines, full), `p5.out`, `p7.out`, `p6.out`, `p4.out`, `p1.out`.

Readings:

1. A counterpart lane's canonical self-assessment gate returns `clean` for kama's tree while every
   finding is CNE (`mismatches=0 could_not_evaluate=35`); CNE is excluded from the mismatch tally, so
   an unparseable tree reads as a clean verdict. The same clean appears on a third lane with 0 CNE
   and on the owner's own tree with 116 CNE — `clean` is the gate's default, not an owner-scoped or
   data-bound verdict. Only an unresolvable revision is refused.
2. kama's gate emits exit `1` — the `not met` class in its own exit map — on a sibling tree, via an
   uncaught traceback, although the same row maps `EvalError` to `2 could not evaluate`.
3. tsukuroi's gate refuses kama, but incidentally: its K13 reads its own
   `tools/tsukuroi-census.sh`, absent from kama. None of the three gates has an owner guard.

## Finding 3 — owner side reproduces the frozen control, and the canonical count is 11 / round 49

- Frozen base `b89bdab2cc114735ec5d331c6c610134258f7864`: `r41=1 … mismatches=1 maxN=56 met=False`,
  exit `1`, single detail quoting the R41 calibration run expecting `42` (`receipts/p8.out`). This
  is the same summary line as `controls/base-c1.out`.
- Lane HEAD `8640e34c` (after `89dc4f52`, `7c873d7b`, `7b74e2f2`, `8640e34c`): `mismatches=0 maxN=57
  met=True`, exit `0` (`receipts/p3.out`). The lane worktree is detached here while branch `master`
  is at `77e7f5ee`, which is the tree the fixture arms use.
- Independent parse of `git show 8640e34c:SCORECARD.md`: the highest canonical heading is
  `**Capabilities — canonical list as of round 49**` with **11 data rows** (`sources-registry`,
  `ollama-offline-evidence-replay`, `live-llamacpp-lifecycle`, `gguf-declared-identity-replay`,
  `context-capacity-receipt`, `instrument-agreement`, `pin-watch`, `digest-ledger`, `hexrun-census`,
  `append-only-audit`, `live-receipt-replay`). `## Round` headings number 58, maximum 57 at HEAD and
  57 headings / maximum 56 at the frozen base — so `maxN` is the round-heading maximum, and neither
  11 nor 49 is 46. Recorded for the C1/C2 owners; this seat does not adjudicate those claims.

## Finding 4 — canonical content binds by row, not by list existence (fixture clone)

Fixture: local clone of branch HEAD `77e7f5ee` (local `--depth` is ignored, so the clone carries
full history), toplevel asserted
(`/fast/scratch/hyaku/kama-r57/R57Item40OwnershipScan/case61/clone`) before any in-fixture commit.

- Control `77e7f5ee`: `mismatches=0 maxN=57 met=True`, exit `0` (`receipts/case61-p9.out`).
- One canonical row deleted: `retired=1 caps=1 mismatches=2 met=False`, exit `1`; details name the
  missing row (`caps: head names [11] != canon (round 49) [10]`) (`receipts/case61-p10.out`).
- The round-49 canonical **heading** deleted while the byte-identical round-48 list remains:
  `mismatches=0 maxN=57 met=True`, exit `0` (`receipts/case61-p11.out`). `canon()` picks the highest
  *present* heading, so deleting the newest canonical list is invisible; the round-48 table is
  identical in its 11 row names (verified independently).

## Boundary answer and advice (advice only — lane-authors own these files)

Owner overlap: **none in the registry plane, present in the execution plane**. kama is the only
named owner and no sibling claims the gate, but a sibling gate returns `clean` on kama's tree over
35 CNE, kama's gate returns `1 not met` on a sibling tree through a traceback, and the newest
canonical list can be deleted without a verdict change.

1. kama's registry rows for the canonical self-assessment gate should carry the eight
   `PROTOCOL.md` fields (including `owner`) instead of the 5-cell shape.
2. A gate repointed at a foreign tree should CNE (exit 2) rather than emit `clean`/`1`; kama's
   missing-`## Axes` path should be a declared CNE, not a traceback.
3. The canonical leg should require the newest canonical heading to exist at the measured revision;
   today's content binding is row-identity only.
4. Any consumer of a sibling `verdict=clean` must also read `could_not_evaluate` — the
   `clean` + 35 CNE pair is a false green of the class this round's C1/C2 controls target.

## Handoffs not absorbed (adjacency)

- The lane-context non-author spot-check duties — re-opening `corpus/SOURCES.md` row S515 (Git
  config runtime environment pairs) against the Git manual and the round-56 lesson quote, and one
  admit/reject decisions spot check — are non-author duties assigned to the sources/reopen and
  closure seats (e.g. `S01SourcesReopen`, its item-06/26 siblings). This seat is a dispatched
  lane-author seat and did not absorb them; no S515 row, source URL or lesson text was read or
  quoted here, so no second authority competes with those seats.

## Observed concurrent change (not this seat)

While this seat ran, the shared controls directory changed by another seat: `git status` shows
`D .ufo/waves/round-57/controls/noop-c1.out` and `D .ufo/waves/round-57/controls/noop-c2.out`
(tracked in `89dc4f52`) and a new untracked `controls/noop-fixture/tools/round56-env-leg-battery.py`
(directory created 15:17). This seat did not touch either path; `controls/base-c1.out` (cited in
Finding 3) is still present with its original bytes. Flagged so the closure can account for the
frozen receipt set.

## Artifacts

- `.ufo/waves/round-57/OwnershipScan/40/evidence.md` — full seat evidence, separability, replay.
- `.ufo/waves/round-57/OwnershipScan/40/commands.txt` — exact commands, revisions, observed exits.
- `.ufo/waves/round-57/OwnershipScan/40/receipts/` — `p1..p8`, `r09..r11`, `case61-p9..p11` raw outputs.
- `.ufo/waves/round-57/reports/R57Item40OwnershipScan-case61.md` — distinct case 61, independent test.

Report: .ufo/waves/round-57/w1/out/R57Item40OwnershipScan.md
