# Defect 2 — KQ36 qualification and lesson erratum

## Frozen line evidence

Revision: `a23c0e042114016a909eb15173aa6df74b5b7eb0`.

`corpus/QUALITY.md:203`:

> | KQ36 | A round that changes a source measured by a registered counting command (one cited by a SCORECARD row, or a claim's registered command) re-runs that command at the round's landed tip and pastes the output. An instrument that cannot evaluate there (its unique-match guard fails, exit 2) is reported as stale, and the value it supports is unverified at that tip. A re-anchor names, per mutant, whether its last recorded kill still holds, so a survivor caused by a moved code path is not hidden by a same-line literal. | A registered command is left stale after its source changes; a could-not-evaluate run is recorded as a pass, hidden, or counted as zero defects; the re-run uses a revision other than the landed tip; a re-anchored mutant's change from killed to surviving is not reported. | `lessons/round-25.md` §Mistakes rows 1-2; `round-24-verifier-spotcheck.md:80-82`. Shown able to fail: the C1 command prints `registered 27 stale 2` at efe58e96 and `registered 28 stale 0` at 1fc41e34; the full instrument exits 2 at efe58e96 (after ten mutants) and 0 at 1fc41e34 with survivors M17 and M20 (`.ufo/waves/round-25/a2-build/advice/ExecC1BaseRun.md`, `.ufo/waves/round-25/final/c1/`). |

`corpus/lessons/round-25.md:49`:

> | survival hidden by a same-line re-anchor | M17's re-anchored literal is the round-23 line, but since 92063cf no caller reaches it; F13's kill moved to the new M33 (`a2-build/advice/RevengerM17Sites.md`, causal run on ed1cc3a; `CriticC1NoHarm.md`) | CriticC1NoHarm and MutationM17M33Kill (wave-1 attack seats) | the instrument docstring and SKILL registry row now say M17 survives and why; the full run lists it (`final/c1/c1-tip-mutants.json`: 28 mutants, 26 killed, survivors M17 and M20) |

Frozen `SKILL.md` search for `M17` returned these two lines only:

> 883: M14/M22/M27/M29 are explicitly retired because their metadata-classifier component was deleted; M17 follows the current local-store spelling.
>
> 889: | Retained isolation mutation experiment | probe: `python3 tests/report-audit/isolation-mutants.py [--only NAME] [--json]` | 0 pristine passed and selected inventory evaluated, survivors reported; 2 fail-fast could-not-evaluate | pristine grid positive control; existing literal inventory and retirement output |28 retained literals since round 25 (M11 and M17 re-anchored; M33 is the second call site of the M17 refusal), 4 retired IDs without reuse; `RETIRED` explains their removed component; unchanged isolation elements remain explicit | temporary source copies and grid fixtures | kama |

Neither SKILL line says that M17 survives. The lesson's attribution to the SKILL registry row is false; the lesson's full-run receipt attribution is separate.

## Exact text to append to `corpus/QUALITY.md`

```markdown
## Round 26 qualification — KQ36 “landed tip” (2026-10-23)

For KQ36, “landed tip” means the measured source and instrument bytes each match the corresponding bytes in the landing commit. Disclose any later change to either; a run against different bytes is not a landed-tip measurement.
```

## Exact text to append to `corpus/lessons/round-25.md`

```markdown
## Erratum — round 26 (2026-10-23): §Mistakes row 2

The Fix cell's clause “the instrument docstring and SKILL registry row now say M17 survives and why” is corrected. The full-run receipt named in the row lists M17 and M20 as survivors, but the SKILL registry row does not say M17 survives: at `a23c0e042114016a909eb15173aa6df74b5b7eb0`, `SKILL.md:883` says M17 follows the current local-store spelling, and `SKILL.md:889` records the M17 re-anchor and M33's second call site. Correct attribution: the full-run receipt lists M17 and M20 as survivors; the SKILL registry records the re-anchor and second call site, not M17's survivor status.
```

## Check performed

A search for `M17` in the `SKILL.md` extracted from the frozen `a23c0e042114016a909eb15173aa6df74b5b7eb0` archive returned only lines 883 and 889, quoted above. This is a proposed append-only correction, not an applied corpus edit.