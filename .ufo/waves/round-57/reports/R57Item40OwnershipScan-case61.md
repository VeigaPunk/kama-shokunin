# R57Item40OwnershipScan — distinct case 61 (independent test)

Assigned case: the counterpart-lane boundary for the canonical self-assessment gate. This file is
the independent test of that case; the seat's report is
`.ufo/waves/round-57/w1/out/R57Item40OwnershipScan.md` and the shared evidence is
`.ufo/waves/round-57/OwnershipScan/40/evidence.md`.

Axes: operability + calibration. Read-only over the lane and sibling lanes; the only writes are
this file and `OwnershipScan/40/` receipts plus `/fast/scratch/hyaku/kama-r57/R57Item40OwnershipScan/`
(fixture clone under it, removed after the receipts were copied). No installs; pacman transactions
remain paused.

## Predicate under test (P61)

The canonical self-assessment gate's ownership boundary holds only if all three arms hold:

- **A — unique declared owner.** Exactly one lane registry home names the gate, and that row
  carries the `PROTOCOL.md:401-406` `owner` field.
- **B — no foreign verdict.** A sibling lane's canonical self-assessment gate, pointed at kama's
  committed tree, does not emit a `clean` or `failed` class (it may only CNE/refuse).
- **C — canonical content is bound.** The owner's gate changes verdict when the canonical
  capability table's content changes, and does not pass when the newest canonical list is removed.

## Arm A — unique declared owner: uniqueness holds, owner field does not

- Gate token `round42-selfdesc` occurs outside kama's tree **0** times (excluding fleet round
  reports) and **1** time in `kama-shokunin/SKILL.md` (`receipts/r10-gate-refs.out`:
  `count_outside_kama_excluding_fleet_reports=0`, `count_in_kama_skill=1`).
- The registry row is `kama-shokunin/SKILL.md:1404`, inside the **5-cell** table headed at line
  `1387` — `| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`
  — so it has **no owner field** (`receipts/r09-registry-owners.out`, `receipts/r11-schema.out`:
  `header variants: {5: 19, 7: 13}`).
- The counterpart lane's equivalent row is `tsukuroi-shokunin/SKILL.md:2356`,
  `| self-assessment | gate | \`python3 tools/check-self-assessment.py --revision <REV>\` | … | tsukuroi |`
  — 8 cells with `OWNER=tsukuroi`. All 16 tsukuroi self-assessment rows read `OWNER=tsukuroi`.

Arm A result: **uniqueness PASS (1 registration), declared owner FAIL** (kama's row has no owner
field; the counterpart lane's row does).

## Arm B — no foreign verdict: FAILS in both directions

Commands and exact summaries (replay block below):

| Direction | Result | Exit | Receipt |
|---|---|---|---|
| tabi gate → kama tree @`8640e34c` | `SELFASSESSMENT verdict=clean … mismatches=0 could_not_evaluate=35 superseded=0`; all 35 findings are `could-not-evaluate=no 'Axes at round start:' with all six axes in the round group` | `0` | `receipts/p2.out` |
| tabi gate → revenger tree @HEAD | `SELFASSESSMENT verdict=clean … mismatches=0 could_not_evaluate=0 superseded=0` | `0` | `receipts/p5.out` |
| tabi gate → tabi tree @HEAD (owner control) | `SELFASSESSMENT verdict=clean … mismatches=0 could_not_evaluate=116 superseded=48` | `0` | `receipts/p7.out` |
| tabi gate → empty dir | `SELFASSESSMENT verdict=could-not-evaluate detail=revision does not resolve: HEAD` | `2` | `receipts/p6.out` |
| kama gate → tsukuroi tree @`f6a46fa9` | uncaught `r41c1.EvalError: no line exactly '## Axes' in SCORECARD.md` traceback; kama's own row maps `EvalError` to `2 could not evaluate`, not `1` | `1` | `receipts/p4.out` |
| tsukuroi gate → kama tree @`8640e34c` | `{"status": "CANNOT_EVALUATE", "error": "missing file", "detail": "tools/tsukuroi-census.sh"}` | `2` | `receipts/p1.out` |

Arm B result: **FAIL.** A sibling's canonical self-assessment gate emits `clean` on kama's tree
over 35 CNE findings and on a third lane over 0 CNE, so `clean` is a default rather than an
owner-scoped verdict; kama's gate reciprocally emits exit `1` (a "not met" class) on a sibling tree
with an uncaught traceback. tsukuroi's gate is the only one that refuses kama, and only because its
K13 reads its own `tools/tsukuroi-census.sh`.

## Arm C — canonical content binding: content YES, newest-heading removal NO

Fixture: local clone of the lane at `77e7f5ee` (branch HEAD; `--depth` is ignored in local clones,
so full history is carried), toplevel asserted before any mutation.

```
toplevel=/fast/scratch/hyaku/kama-r57/R57Item40OwnershipScan/case61/clone
git clone --depth 1 /home/vgpnk/Projects/shokunin/kama-shokunin clone
```

| Arm | Tree | Summary | Exit | Receipt |
|---|---|---|---|---|
| C0 control | clone @`77e7f5ee`, canonical table intact | `mismatches=0 maxN=57 met=True` | `0` | `receipts/case61-p9.out` |
| C1 row deletion | clone @`0b37020b`, last row (`live-receipt-replay`) of the round-49 canonical table deleted | `retired=1 caps=1 mismatches=2 met=False`; `detail: retired: does not state '10 capabilities'`; `detail: caps: head names [... 11 names ...] != canon (round 49) [... 10 names ...]` | `1` | `receipts/case61-p10.out` |
| C2 newest heading removed | clone @`c0449a8a`, the `**Capabilities — canonical list as of round 49**` heading deleted (round-48 heading remains) | `mismatches=0 maxN=57 met=True` | `0` | `receipts/case61-p11.out` |

C2 passes because `canon()` selects the highest *present* canonical heading; the round-48 list is
byte-identical in row names (11 rows: `sources-registry`, `ollama-offline-evidence-replay`,
`live-llamacpp-lifecycle`, `gguf-declared-identity-replay`, `context-capacity-receipt`,
`instrument-agreement`, `pin-watch`, `digest-ledger`, `hexrun-census`, `append-only-audit`,
`live-receipt-replay`), so deleting the newest list is invisible.

Arm C result: **content binding PASS for row identity, FAIL for the newest canonical list's
existence.**

## P61 verdict

- A: uniqueness PASS / declared owner FAIL.
- B: FAIL.
- C: partial FAIL (newest canonical list removable without a verdict change).

The boundary is therefore **not established**: one lane is the only name-level owner and no sibling
registry claims the gate, yet the executable plane emits cross-lane verdict classes and the newest
canonical list can be deleted without the gate noticing.

Falsifiers that would have carried the case: a sibling gate returning only CNE/refusal for kama's
tree; kama's registry row declaring `owner: kama`; and a C2 fixture where removing the newest
canonical heading produced `mismatches>0`.

## Replay

```
K=/home/vgpnk/Projects/shokunin/kama-shokunin
B=/home/vgpnk/Projects/shokunin/tabi-shokunin
T=/home/vgpnk/Projects/shokunin/tsukuroi-shokunin

# B arms
node "$B/scripts/check-selfassessment.mjs" --repo "$K"  --rev 8640e34cad02adcd247ba0862da63f6fb2aab0df
node "$B/scripts/check-selfassessment.mjs" --repo /home/vgpnk/Projects/shokunin/revenger-shokunin --rev HEAD
node "$B/scripts/check-selfassessment.mjs" --repo "$PWD/empty" --rev HEAD
python3 "$K/tools/round42-selfdesc-reconcile.py" --repo "$T" --tip f6a46fa985a653f97726db477ccd1f304c1ae816
python3 "$T/tools/check-self-assessment.py"     --repo "$K" --revision 8640e34cad02adcd247ba0862da63f6fb2aab0df

# C arms (fixture clone; assert toplevel before committing inside it)
git clone --depth 1 "$K" clone && cd clone && test "$(git rev-parse --show-toplevel)" = "$PWD"
python3 - <<'PY'   # delete the last row of the round-49 canonical table
import re
sc = open('SCORECARD.md').read().split('\n')
i = [n for n, l in enumerate(sc) if 'canonical list as of round 49' in l][0]
k = i + 1
while not sc[k].startswith('|'): k += 1
rows = []
while k < len(sc) and sc[k].startswith('|'):
    rows.append(k); k += 1
del sc[rows[-1]]
open('SCORECARD.md', 'w').write('\n'.join(sc))
PY
git -c user.email=seat@local -c user.name=seat commit -qam "case61 fixture: delete canonical capability row"
python3 "$K/tools/round42-selfdesc-reconcile.py" --repo "$PWD" --tip HEAD     # C1: met=False, exit 1
python3 - <<'PY'   # C2: remove the newest canonical heading
import re
sc = open('SCORECARD.md').read()
open('SCORECARD.md','w').write(re.sub(r'\*\*Capabilities — canonical list as of round 49\*\*',
                                      '**Capabilities (heading removed)**', sc))
PY
git -c user.email=seat@local -c user.name=seat commit -qam "case61 fixture: remove canonical heading"
python3 "$K/tools/round42-selfdesc-reconcile.py" --repo "$PWD" --tip HEAD     # C2: met=True, exit 0
```

Fixture revisions: control `77e7f5eef2b0c759b7509056c7c511255477496d`, C1
`0b37020b0a1a503f7cb4202f87b0b476b959785f`, C2 `c0449a8a3af823a66f44bee678aff8c777d5b88d`.
The fixture clone is scratch only and was deleted; no lane or sibling path was written.
