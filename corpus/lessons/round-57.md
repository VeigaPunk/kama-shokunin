# Round 57 — counter control and calibration count

Author: KamaR57a2. Base: `b89bdab2cc114735ec5d331c6c610134258f7864`. Pre-data freeze: `89dc4f5239fe1f875adda4613812e77fb9bbc7cc`; pre-data claim correction: `7c873d7b4e3839489a93d6334cdf93fe5d34d19f`.

## Claims

- C1 — operability: make `tools/round56-prereg-check.py` bind declared roster members to calls in the battery's `main`, so a no-op harness cannot satisfy the counter.
- C2 — calibration 7→7: correct the stale self-description verifier-spotcheck count in the SCORECARD calibration row from 42 to the observed 43 at base; require `tools/round42-selfdesc-reconcile.py` to report zero mismatches.

## Gate

S515 was reopened 2026-10-27 at https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT, section `GIT_CONFIG_COUNT`, Git 2.56.0 documentation. Located quote: “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration” (18 words). This is an existing lane-owned source row; no row cell was changed. C1's own-work evidence is the committed round-56 battery source and its frozen prereg checker; S515 is not claimed as support for C1.

Discernment spot-check: no independent verifier of this round is available before filing; dispatched members are lane authors. S515 is a scoped source citation, not an admit/reject verdict.

Assimilation: none. `considerthese/2026-10-26.md` proposal 3 (counter-shortcut tally) was opened; this round addresses a concrete counter no-op defect but does not implement a multi-round tally.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| calibration-staleness | `tools/round42-selfdesc-reconcile.py --repo <lane> --tip b89bdab2cc114735ec5d331c6c610134258f7864` printed `mismatches=1` and identified the SCORECARD run expectation `42`; exact file census printed `43`. | The counter's own frozen round-42 expected literal was stale; no gate required re-deriving the calibration row count at the declared base. | SCORECARD calibration row re-anchors the count to a reproducible command and latest outside closure. |
| no-op-counter | `corpus/lessons/round-56-verifier-spotcheck.md:14` records a no-op harness passing `met=True` because only the roster literal was inspected. | Round-56 counter did not inspect executed battery call sites; captured by round-56 closure defect and §9 do-nothing-control rule. | Round 57 adds AST call-site binding to `tools/round56-prereg-check.py`; retains no-op receipt as a negative control. |

## Census before → after

Before: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`; full output `.ufo/waves/round-57/census/start.out`, exit `.ufo/waves/round-57/census/start.exit`.
