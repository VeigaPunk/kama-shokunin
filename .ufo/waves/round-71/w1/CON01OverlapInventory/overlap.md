# Cross-lane overlap scan — round 71's three purposes (read-only)

Seat CON01OverlapInventory, kama r71 w1. Scan basis: lane tip during the wave (`b43e71a8` + worktree),
read-only git only. Siblings scanned: every `*-shokunin/tools` / `corpus/instruments` / `plans` /
`verifiers` tree plus each lane's `SKILL.md` registry tables. No lane was edited.

Verdict vocabulary used below:
- **contested** — a sibling claims the *same purpose* as one of C1/C2/C3 such that a reader could
  attribute the round-71 move to the wrong lane, or the same bytes could be graded by both.
- **adjacent** — same shape or same policy, disjoint artifact and population; no attribution risk.

Each rule is one line and is meant to be quotable in a round report without further context.

## Purpose 1 — pre-report aggregation gate (C1)

| Lane | Instrument (registry home) | What it is | Relation | Overlap rule |
|---|---|---|---|---|
| souji | `tools/souji-pre-report-gate.sh` + `tools/souji-report-contract.py` (`SKILL.md:256-257`) | bash gate, arms `tip/report/shonen/clean/prereg` (+opt-in `contract`), prints `check-<arm>=FAIL`, exit 0/1/2 | **contested purpose, disjoint population** — closest sibling: aggregate pre-report gate with named failing arms | A pre-report gate aggregates the instruments of its own lane; souji grades report/registration hygiene of the souji lane, kama's C1 grades four reconciled kama instruments plus a round-wave cleanliness class, and neither may be cited as the other's evidence. |
| kasegi | `corpus/instruments/r46-landing-gate.py --pre-report / --post-report` (`SKILL.md:1163`, 30 selftest cases) | pre: tree-clean, jj-state, remote-tip, placeholders; post: report-readable, cited-hashes, resolves, ancestor, final-is-tip, date-order, shonen-heading | **contested purpose** — the only sibling gate with a *post-report* mode | Landing evidence for kasegi's commits is graded by kasegi's gate on kasegi's arm set; kama's C1 must not borrow that arm set, and its target (`failed=0 uncommitted=0`) is not kasegi's `landing-gate` line. |
| kotodama | `tools/harness/claims-freshness.py` | re-derives each claim's `before` premise from the git object store at `baseline_commit`; undeclared checks are *could-not-evaluate*, never fresh | adjacent — inverse temporal position | Premise freshness before dispatch (kotodama) and record reconciliation before report (kama) are the two ends of a round; neither subsumes the other, and both owe S052's fail-closed-on-no-verdict exit. |
| kagi | `corpus/self-counts.py` (`SKILL.md:47`) | binds current-tense doc counts to ledger commands; "binds the doc to the ledger, never the ledger to the live host" | adjacent — same target class as kama's `round42-selfdesc-reconcile.py` / `round41-scorecard-reconcile.py` | Self-stated numbers are graded in-lane: kagi binds doc text to its ledger, kama's reconciler binds SCORECARD tokens to its tree. |
| tameshi | `tools/receipt-revision-gate.py` (`SKILL.md:1547`) | binds a receipt to the revision it certifies: a `positive`/`verdict` receipt's single `rev=` must equal the certified revision, *or* name a revision byte-identical on every path listed in `--paths`; `control` receipts must be ancestors; named refusals, exit 3 | adjacent — **the closest sibling to C1's closure/receipt arms and to routed defect 3** (a receipt's tip must be the certified tip, proxy allowed only by a listed-path byte identity) | A receipt's `rev=` is bound to the revision it certifies by tameshi's gate for tameshi's receipts; kama's C1 grades pointer resolution and closure currency, not tip binding, so defect 3's class stays unadopted in kama. |
| kaidoku | `tools/round-32/freeze-integrity.py`, `tools/round-34/freeze-integrity.py` (`SKILL.md:1472,1587`) | freeze schema + claim selectability before scoring | adjacent — gates the freeze, not the report | Freeze integrity is a pre-scoring gate on the claims file; C1 is a pre-report gate on the record and the wave tree. |
| kama (in-lane) | `report-landing-audit.py`, `round67-worktree-landing-check.py`, `round68-receipt-pointer-audit.py`, `round69-newest-closure-counter.py`, `gate-registry-check.py` | C1's four arms + the registry population gate | **in-lane predecessor, not overlap** | C1 adds only two things the lane does not hold: an aggregation arm set that names failures, and a `.ufo/waves/round-<N>/`-scoped uncommitted arm (WLC byte-compares nine declared self-record paths and cannot see that class). |

## Purpose 2 — census not-evaluated / waiver boundary (C2)

| Lane | Instrument (registry home) | What it is | Relation | Overlap rule |
|---|---|---|---|---|
| mado | `quality/check-session-material.py` + `mado-session-material` (`SKILL.md:771`) | waiver registry; every honoured waiver printed (`WAIVER file=… rule=…`), waived findings counted separately, serial/real-value rules "not waivable", `.ufo/` waiver registry refused, sha-bound waiver voided on tamper | adjacent — **same policy**, different object: it *uses* waivers | Waiver policy (what may be waived, and that suppression is never silent) is owned by the gate that consumes waivers; a boundary instrument only grades whether that policy's holes are observable, never re-declares the policy. |
| tameshi | `tools/arm-liveness.py` (+ `mutate-and-run.sh`, `golden-verdict.py`) | manifest rows pin one committed input per red arm; re-executes the instrument at `instrument_rev`; `ARM_DEAD` when the tally does not move past its do-nothing baseline. **Not named anywhere in `tameshi/SKILL.md`** (`grep -c arm-liveness tameshi-shokunin/SKILL.md` → `0`; occurrences live only under `.ufo/waves/` and `.ufo/evidence/`), i.e. the sibling lane carries the same unregistered-instrument shape as kama's routed defect 4 | adjacent — **same purpose class** ("a counter that cannot fail scores 0") | Arm liveness of a lane's counters is tameshi's instrument, and a shim-kill boundary over one lane's census is that lane's; kill counts are not comparable across the two, and kama must not cite an unregistered sibling instrument as the owner of the rule. |
| kotodama | `tools/check-gate-battery.py` | isolated mirror battery over seven structural gate selftests + committed-baseline validation for ten gates; never invokes a gate on a live path; unpinned/missing baseline = exit 2 | adjacent — battery mechanics only | Isolated battery mechanics are kotodama's for its registered gates; kama's C2 battery is scoped to one census's waiver/not-evaluated boundary and kills shims of that census's own bytes. |
| kama (in-lane) | `round65-host-census.py` (object), `error-verdict-census.py`, `.ufo/waves/round-70/controls/refused-member-control.py` | the census and the pinned finite error-vs-verdict grid with a survivors arm | **in-lane predecessor** | C2 grades the waiver boundary of the lane's own census; the five shims are the frozen round-70 counterexample set, not new cross-lane cases. |

No sibling lane carries a `waiver`/`not_evaluated` token in a `tools/` instrument path outside mado and
tameshi's historical-input waiver (a different object: digest pinning of moved instrument bytes).

## Purpose 3 — host-surface claim reconciler (C3)

| Lane | Instrument (registry home) | What it is | Relation | Overlap rule |
|---|---|---|---|---|
| **kengaku** | `plans/round51_surfaces.py` + `plans/round51-surfaces.json` (`SKILL.md:661`, `round51-surfaces` gate) | every surface its PROVINCE declares is machine-checked: manifest↔probe↔prose (STALE / DRIFT / NUMBER-DRIFT), absent entries need `ABSENT <ISO date>` (UNVERDICTED 0), observed-present floor | **contested ground at mechanism level, disjoint artifact scope** — highest overlap in the fleet | Timed-absent host markers are graded by the lane that owns the manifest (kengaku r51) or by the lane that owns the marker lines (kama r71); a lane grades only its own PROVINCE and no gate may be cited as the other's evidence. |
| kagi | `corpus/surface-census.sh` + `corpus/surface-census.tsv` + `corpus/state-shape.tsv` (`SKILL.md:34,133`) | live host vs two committed TSVs; `asset` absent/muted = drift, `runtime` absent = informational, undeclared child = UNLISTED; "PROVINCE.md §Surfaces is prose; the census is its falsifiable form" | adjacent — host-vs-declaration drift, config-path population | kagi's census is the falsifiable form of its own PROVINCE §Surfaces; C3 is the falsifiable form of PROVINCE host-*claim* corrections, a different artifact class (claim lines, not declared paths). |
| kotoba | `verifiers/check_host_skill_surfaces.py` (`SKILL.md:472`) | hashes every installed `<skills-root>/*/SKILL.md`, classifies identical / drifted / lane-absent; "exit 0 means every installed surface was measured", no pinned identity | adjacent — host surface *measurement* without claim binding | Instruction-surface drift on the host is kotoba's measurement; C3 reconciles PROVINCE host claims, not installed skill bytes. |
| tsukuroi | `tools/recheck-drift-r54.sh` | re-derives a dated drift register (D1-D12) on the live host; "a drift line is honest output, not a crash: it owes an appended register correction next" | adjacent — **the dated-correction convention, left manual** | A drift register re-derives its rows and leaves the correction to the operator (tsukuroi); C3 binds the correction to a tag, dates it, and grades its verdict against a live probe. |
| kasegi | `corpus/instruments/census-freshness-check.py` | the committed census of record must be byte-identical to a fresh resolver run; fail-closed; restores the stale bytes it found | adjacent — record staleness, bytes not claims | Census-of-record byte freshness is kasegi's; host-surface *claim* freshness is kama's C3. |
| chousa | `tools/claims-audit.py` (+ `corpus/evidence/round6N/claims-erratum.md` channel) | flags frozen-claim statements that committed bytes contradict; rule TSV + erratum file; `AUDIT_STALE` on a non-matching anchor | adjacent — **the contradiction→correction structure**, minus the host probe | Claim-vs-committed-bytes contradictions are chousa's, corrected through an erratum file; claim-vs-live-host contradictions with tagged dated corrections are kama's C3. |
| mori | `mori-pressure.py`, `mori-oom-killers.py`, `mori-commit-runway.py` (`SKILL.md:664,739,1209`) | single-surface live probes, each labelled "gate (host-surface verdict; not a census or fleet-admission gate)"; exit 2 could-not-evaluate | adjacent — probe side only | A single host-surface verdict is mori's; reconciling *many* claimed surfaces against a base marker set is C3's, and C3 consumes no mori receipt as evidence. |
| kama (in-lane) | `tools/round65-province-host-audit.py` (`SKILL.md:1690-1691`) | absent PROVINCE-named surfaces must carry `province-host:<tag>`; 13 declared surfaces; no dated correction, no verdict check, no rewrite detection, no base comparison | **in-lane predecessor superseded in kind** | C3 extends the round-65/67 marker requirement into a base→tip marker-set comparison with dated, verdict-checked corrections; the round-65 tool stays the marker-presence check and is not retired by C3. |

## What the scan says about the three claims (one line each)

- C1's aggregation purpose is held as a *habit* in souji and kasegi but never as an instrument that
  reconciles **another lane's** four instruments; kama's novelty is the reconciliation, not the gate.
- C1 also lacks the one arm its own routed defect 3 needs, and the fleet already has that instrument:
  tameshi's `receipt-revision-gate.py` binds a receipt's `rev=` to the certified revision (proxy only by
  a listed-path byte identity), which is exactly the closure's proposed remedy for defect 3. Kama's C1
  neither imports nor names it, so the class stays open in-lane.
- C2's waiver policy is already enforced where waivers are *used* (mado) and its kill requirement is
  already a *different* instrument in tameshi; what no lane holds is a boundary that kills **shims of a
  census's own bytes** and proves the landed bytes stay green.
- C3 has the fleet's densest neighbourhood (kengaku r51 is a near-twin mechanism). Its distinguishing
  move is the **base-marker set + correction verdict agreement + REWRITTEN detection**, which none of the
  five neighbours does; the risk is attribution, not duplication.
