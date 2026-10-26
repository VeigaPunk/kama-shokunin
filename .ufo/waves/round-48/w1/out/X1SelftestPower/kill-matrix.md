# Selftest kill matrix (round 48, seat X1SelftestPower)

Baseline at the build (380bcdff, tools/append-only-audit.py v3): `AOA_SELFTEST pass=27 fail=0`, exit 0.
Baseline at the base (33e0058, v2): `AOA_SELFTEST pass=19 fail=0`, exit 0.
Each mutant is a copy of the v3 tool in scratch with one edit; `--selftest` run per mutant.

| mutant | one-line edit | cases killed | killed by | exit |
|---|---|---|---|---|
| M1 no-exemption | `if s in eligible:` -> `if False:` (line 417) | 3/27 | `exempt-rewritten`, `exempt-gutted-then-regrown`, `clean` | 1 |
| M2 pre-heading-exempt | `eligible.add(None)` when titles (after line 419) | **0/27** | — (survives) | 0 |
| M3 exit-ignores-regressed | drop `s["regressed"]` from `exit_code` (line 473) | 1/27 | `window-max` | 1 |
| M4 no-clamp | `max(0, M[l] - K[l])` -> `M[l] - K[l]` (line 424) | 1/27 | `clamp` | 1 |
| M2 + proposed case | M2 plus `pre-heading-graded` | 1/28 | `pre-heading-graded` | 1 |

M2 is the shape of the defect round 48 fixed: the round-45 authority banner sits at SCORECARD.md:6,
before any `## ` heading, and it was rewritten in place by rounds 46-47. A tool that treats the
pre-heading region as exempt reports `graded=0 status=ungraded exit=0` on that shape (probe-M2.json)
where v3 reports `graded=24 status=unrestored exit=1` (probe-v3.json), and no case in the 27 notices.
