# CON01OverlapInventory — cross-lane overlap scan + inherited-defect inventory (kama r71 w1)

Seat: connector, leaf. Read-only; no lane edited, no subagent, no git mutation. Scan tip `b43e71a8`
(round-71 freeze), worktree read only through `git show` / `git ls-tree` / `git grep` / `git status`.
Lane-under-scan: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Siblings read-only:
`/home/vgpnk/Projects/shokunin/*-shokunin`.

Artifacts written (both under this seat's report dir):
- `.ufo/waves/round-71/w1/CON01OverlapInventory/overlap.md`
- `.ufo/waves/round-71/w1/CON01OverlapInventory/defects.md`

## 1. What was scanned and how

```
$ ls -d /home/vgpnk/Projects/shokunin/*-shokunin | wc -l
21
$ for d in *-shokunin; do n=$(ls "$d/tools"/*.py "$d/tools"/*.sh 2>/dev/null | wc -l); echo "$n $d"; done | sort -rn
149 souji-shokunin / 103 tsukuroi-shokunin / 99 kama-shokunin / 54 mori-shokunin /
46 tameshi-shokunin / 27 kotodama-shokunin / 25 mado-shokunin / 19 chousa-shokunin / 0 for 13 lanes
```

Caveat on that count: it covers `tools/*.py|*.sh` only. Six of the "0" lanes keep instruments elsewhere
and were still scanned through the purpose greps: kasegi `corpus/instruments/`, kaidoku
`tools/round-*/`, kengaku `plans/`, kotoba `verifiers/`, kagi `corpus/*.sh|*.py`, kumitate/kotoba
`tools/gates/`.

Method: (i) purpose-token greps over every lane's `tools/`, `corpus/instruments/`, `plans/`, `verifiers/`
(`waive|not_evaluated|fail-open|silent pass`, `pre-report|pre_report`, `province|host-surface|drift
register|re-derive`, `shim|mutant`); (ii) filename sweep (`*pre-report*`, `*waiver*`, `*province*`,
`*host-claim*`, `*boundary*`, `*surfaces*`); (iii) each hit's header read and its `SKILL.md` registry row
read, so "registered" is the lane's own claim, not a filename guess. Ground truth for kama is
`SKILL.md`'s registry tables (`| Name | Kind / entry command | Exit map | … |`).

## 2. Closest instruments per purpose (full table + one-line rules in `overlap.md`)

### C1 — pre-report aggregation gate

| Lane | Instrument | Relation |
|---|---|---|
| souji | `tools/souji-pre-report-gate.sh` + `tools/souji-report-contract.py`, `SKILL.md:256-257` | **contested purpose, disjoint population** — same shape (aggregate gate, `check-<arm>=FAIL`, exit 0/1/2); clean arm is whole-lane `status -uall`, no instrument reconciliation, no round-dir scope |
| kasegi | `corpus/instruments/r46-landing-gate.py --pre-report/--post-report`, `SKILL.md:1163` | **contested purpose** — the only sibling with a post-report mode (cited-hashes, ancestor, final-is-tip); no four-instrument arm set, no `.ufo/waves/round-N/` class |
| kotodama | `tools/harness/claims-freshness.py` | adjacent — pre-**dispatch** premise re-derivation at `baseline_commit`; already embodies "no declared verdict is never fresh" (C1's S052 rule) |
| kagi | `corpus/self-counts.py`, `SKILL.md:47` | adjacent — doc counts ↔ ledger rows; same target class as kama's `round42-selfdesc-reconcile.py` |
| tameshi | `tools/receipt-revision-gate.py`, `SKILL.md:1547` | adjacent — binds a receipt's `rev=` to the certified revision (or to a revision byte-identical on the `--paths` list); **exactly defect 3's remedy, already registered** |
| kaidoku | `tools/round-32/freeze-integrity.py`, `tools/round-34/freeze-integrity.py`, `SKILL.md:1472,1587` | adjacent — gates the freeze, not the report |

Overlap rule (one line): a pre-report gate aggregates the instruments **of its own lane** — souji grades
report hygiene, kasegi grades landing evidence, kama's C1 grades four reconciled kama instruments plus a
round-wave cleanliness class, and no gate may be cited as another's evidence.

In-lane predecessors C1 builds on (not overlap): `round67-worktree-landing-check.py` (byte compare of 9
declared self-record paths — cannot see the wave-tree class), `round68-receipt-pointer-audit.py`,
`round69-newest-closure-counter.py`, `report-landing-audit.py`, `gate-registry-check.py` (population:
`.ufo/waves/round-*/count-*.py` or `tools/round<N>-*.py`).

### C2 — census not-evaluated / waiver boundary

| Lane | Instrument | Relation |
|---|---|---|
| mado | `quality/check-session-material.py` + `mado-session-material`, `SKILL.md:771` | adjacent — **the same waiver policy** already enforced where waivers are consumed: every honoured waiver printed, `SESSION_MATERIAL_WAIVED` counted separately, real/serial values "not waivable", `.ufo/` registry refused, sha-bound waiver voided on tamper |
| tameshi | `tools/arm-liveness.py` (+ `mutate-and-run.sh`, `golden-verdict.py`) | adjacent — **same purpose class** (a red arm that cannot move is dead): manifest-pinned re-execution at `instrument_rev`, `ARM_DEAD` vs do-nothing baseline. **Not named in tameshi's own `SKILL.md`** (`grep -c arm-liveness tameshi-shokunin/SKILL.md` → `0`) — the sibling carries defect 4's shape too |
| kotodama | `tools/check-gate-battery.py` | adjacent — isolated mirror battery, originals-preserved by hash, unpinned baseline = exit 2; grades pin presence, not hole semantics |

Overlap rule: waiver **policy** belongs to the gate that consumes waivers (mado); arm **liveness** belongs
to tameshi; what no lane holds is a boundary that kills shims of a census's own bytes and keeps the landed
bytes green — that is C2, and its `killed=5` is not comparable to tameshi's `ARM_LIVE` counts.

### C3 — host-surface claim reconciler

| Lane | Instrument | Relation |
|---|---|---|
| **kengaku** | `plans/round51_surfaces.py` + `plans/round51-surfaces.json`, `SKILL.md:661` | **contested at mechanism level, disjoint artifact scope — highest overlap found**: every PROVINCE-declared surface machine-checked, manifest↔probe↔prose (`STALE`/`DRIFT`/`NUMBER-DRIFT`), absent rows need `ABSENT <ISO date>` (`UNVERDICTED 0`), observed-present floor. Differs: manifest-driven, no base→tip marker-set, no correction-verdict agreement, no `REWRITTEN` detection |
| kagi | `corpus/surface-census.sh` + `surface-census.tsv`/`state-shape.tsv`, `SKILL.md:34,133` | adjacent — live host vs committed TSVs, `asset`/`runtime` absent classes, `UNLISTED` children |
| kotoba | `verifiers/check_host_skill_surfaces.py`, `SKILL.md:472` | adjacent — host *instruction-surface* hashing vs fleet `SKILL.md`; "exit 0 means every installed surface was measured", no pinned identity |
| tsukuroi | `tools/recheck-drift-r54.sh` | adjacent — dated drift register re-derived on the live host; "a drift line … owes an appended register correction next" — the convention, left manual |
| chousa | `tools/claims-audit.py` + `claims-erratum.md` | adjacent — frozen-claim vs committed-bytes contradiction with an erratum channel; **no host probe** |
| kasegi | `corpus/instruments/census-freshness-check.py` | adjacent — census-of-record bytes vs a fresh resolver run, fail-closed |
| mori | `mori-pressure.py`, `mori-oom-killers.py`, `mori-commit-runway.py`, `SKILL.md:664,739,1209` | adjacent — single-surface live verdicts, each self-labelled "not a census" |

Overlap rule: timed-absent host markers are graded by the lane that owns the manifest (kengaku r51) or by
the lane that owns the marker lines (kama r71); a lane grades only its own PROVINCE and neither gate may
be cited as the other's evidence.

In-lane predecessor: `tools/round65-province-host-audit.py` (`SKILL.md:1690-1691`, 13 surfaces) requires
`province-host:<tag>` on absent surfaces but has no date, no verdict agreement, no rewrite detection, no
base comparison — C3 supersedes it in kind without retiring it.

## 3. Adjacency conclusions the scanner can defend

1. C1's genuinely new content is **reconciliation of four other instruments + a round-scoped uncommitted
   class**, not "a pre-report gate": two siblings already have one. Attribution risk is real (souji,
   kasegi) and should be named in the round report's adjacency row.
2. C2's rule set is **already a convention** in the fleet in two different places (mado: waiver scope;
   tameshi: arm liveness). The round's novelty is narrower than it reads: shim-level boundary over one
   census's bytes. Naming mado/tameshi as adjacent keeps the claim honest.
3. C3 sits in the **densest instrument neighbourhood** in the fleet. kengaku r51 is a near-twin; the
   distinguishing move is base-marker set + dated correction whose verdict is re-probed + `REWRITTEN`
   detection. Without that trio stated, C3 reads as a re-derivation of kengaku's gate in another lane.
4. kama's `SKILL.md`/`PROVINCE.md` name **no sibling instrument** (`grep -niE
   'kengaku|round51_surfaces|surface-census|census-freshness|self-counts|r46-landing|souji-pre-report'
   SKILL.md PROVINCE.md` → only domain refusals, no instrument rows). Every overlap rule above is
   currently unrecorded in-lane.
5. The one arm C1 does not hold and the fleet already has is **receipt-tip binding** (tameshi
   `receipt-revision-gate.py`, registered): routed defect 3 is a missing arm in kama, not an open problem
   in the fleet. If a future round adopts it, the round report should name tameshi's gate as the prior art
   rather than present the arm as new.

## 4. Inherited defects (§7 of the round-70 spot-check) at `b43e71a8`

Full commands/outputs in `defects.md`. Summary (status judged at the freeze tip):

| # | Defect | Status at `b43e71a8` | Closed by |
|---|---|---|---|
| 1 | Uncommitted round-70 work | **CLOSED** — `git status --porcelain -uall -- .ufo/waves/round-70 \| wc -l` → `0`; `git show --numstat --format= b43e71a8 -- .ufo/waves/round-70 \| wc -l` → `26` | freeze commit `b43e71a8`; **C1** keeps it closed |
| 2 | Stale "final" receipt in the round-70 lesson | **OPEN** — lesson:75 still cites `measured/after/census-at-tip.out` (`waived=0`); `census-at-af6eb6c2.out` (no `waived=`) exists; `grep -ci correction` on the lesson → `0`; only one commit ever touched the file (`910e6747`) | **no claim** — C1's receipt audit resolves the pointer (file exists), so it is green on the defect |
| 3 | Unreceipted re-run at `61f3ec42`/`380ac279` | **OPEN** — report line 40 says "re-run by the L1 at `61f3ec42` and `380ac279`"; `git grep -l '380ac279\|61f3ec42' b43e71a8 -- '.ufo/waves/round-70/measured/*'` → empty; `measured/final/reconciler.out` header `tip=a8df1af5…`; `grep -c 'invariance\|diff 61f3ec42'` on the report → `0` | **no claim** |
| 4 | Boundary control unregistered | **OPEN at freeze** — `git show b43e71a8:SKILL.md \| grep -c refused-member-control` → `0`; file committed at `.ufo/waves/round-70/controls/refused-member-control.py`; the three round-71 tool names → `0` at this tip | **C2 in kind** (registers `census-waiver-boundary`); the round-70 file itself stays out of the registry population |
| 5 | Receipts cite scratch tips | **OPEN** — `git cat-file -t af6e1c84` / `a7ae13ab` → `fatal: Not a valid object name`; `git grep -c` finds them only inside the three receipts themselves | **no claim** — C1 audits self-record citations, not in-receipt `tip=` fields |

Cross-read: the three claims close **one** inherited defect outright (#1, already closed by the freeze)
and **one in kind** (#4, via C2's registered replacement). #2, #3, #5 stay open with **no round-71
counter able to grade them**; the wave's scribe (lessons/corrections) item is the only planned carrier.
Stating this keeps the round from reading as "all routed defects closed".

Observed while scanning (worktree, not tip status): `corpus/lessons/round-70.md` already carries a
22-line append naming `measured/after/census-at-af6eb6c2.out` / `measured/final/census.out`, and
`tools/pre-report-gate.py` + `tools/round71-province-host-claims.py` exist uncommitted — the wave is
closing #2 and building C1/C3 as this inventory is written. No file was edited by this seat; the tip
status table above is judged at `b43e71a8` as instructed.

One scope disagreement worth flagging without editing the freeze: `controls/refused-member-control.py` is
*outside* `gate-registry-check.py`'s declared population (`.ufo/waves/round-*/count-*.py`,
`tools/round<N>-*.py`), so defect 4 is a Gate-standard §Delivery defect and not a gate-registry one — the
freeze's "registered rows 79 → 82" measures C2's new instrument, not a row for the round-70 file.

## 5. C1's before-state is already empty at the round's own tip

The freeze's before-receipt `.ufo/waves/round-71/measured/before/git-status.out` (14 entries) ends with
`?? .ufo/waves/round-71/` — the wave dir the freeze then committed. At `b43e71a8` the round-70 class is
empty, so `uncommitted=0` is green by construction unless a round-71 path is left uncommitted. The claim is
only non-vacuous with (a) a kill-rule fixture planting a *fresh* uncommitted file under
`.ufo/waves/round-71/`, and (b) the shortcut control reproducing `uncommitted=26` on a fixture at
`af6eb6c2` (the freeze's design). Worth one sentence in the round report so the `before` number is not
misread as still live.

## 6. What I could not verify (read-only seat, no sibling gate executed)

- I ran **no** sibling lane gate or selftest (kengaku r51, kagi surface-census, kasegi r46-landing, souji
  pre-report, tameshi arm-liveness, mado session-material). Their descriptions here are read from headers
  and registry rows; current green/red state is unknown and not claimed.
- I did not run kama's own `gate-registry-check.py`; the frozen `79 → 82` row count is quoted from
  `plans/round-71-claims.md`, not re-measured (my own shape-grep gives 123 `| … | kind |` rows, a
  different counting rule, so it neither confirms nor refutes 79).
- The filename sweep cannot prove the absence of a same-purpose instrument that is *named* something else
  in a lane whose registry I only token-grepped (kengaku 74 gate rows, tsukuroi 1311, souji 99 — read by
  token, not exhaustively). Declared limit, not hidden.
- No tool was installed or upgraded this seat; no package channel was touched. Scratch dir
  `/fast/scratch/hyaku/kama-r71/con01-overlap-inventory/` was not created because the scan produced no
  fixtures (nothing to delete).

## 7. Report-to-path check

`Report:` trailer → `.ufo/waves/round-71/w1/CON01OverlapInventory.md` (this file). Companion artifacts:
`.ufo/waves/round-71/w1/CON01OverlapInventory/overlap.md`, `…/defects.md`.
