# SOURCES row candidate — S058 (draft for L1 integration)

Status: validated draft; the lane registry was not touched. Byte-verified against
the census-validated scratch copy (see the Report, `SrcGateStandard.md`, §3).

## Row as appended (single line, validated)

| S058 | shokunin fleet protocol, PROTOCOL.md §Gate standard — https://github.com/VeigaPunk/kimi-shokunin/blob/e737d2ea97f6b0198503e077676c3f2ea07974a9/skills/shokunin/protocol/PROTOCOL.md | spec | A | own-protocol: the fleet's outer gate-exit interface (which codes read clean, failed or could-not-evaluate); fleet conformance only, not an external convention, not a gate's lane-owned finding vocabulary, not crash detection | §Gate standard (heading line 388), bullet **Verdict.** lines 393-397 @ VeigaPunk/kimi-shokunin commit e737d2ea97f6b0198503e077676c3f2ea07974a9 (2026-10-19), blob 2a50081f, raw sha256 622b29a0…1739fd0; same blob on remote main e5eccc0c (2026-10-21) | Exit 0 is clean and 1 is failed fleet-wide; only other codes are declared and mapped per registry row, and an undeclared nonzero code reads as could-not-evaluate. | queued | 2026-10-21 | every round | — |

## Insertion point

New last row of `## Registry`, directly after the current S057 line (SOURCES.md
line 69 at round start `37bd4c5bd456a2f8a54d3312c28495c321715856`). Census
baseline was 57 rows; with this row: 58 rows, tier.A 55, tier.C 3, queued 6,
mined 46, rejected 6 (`exit=0`, no new warnings).

## If integrated and cited later (only when a citing file exists on disk)

Flip in place (allowed cells only, logged old→new in the round lesson):
`queued` → `mined`, `—` → e.g. `corpus/lessons/round-20.md`. Do not ship the
`mined` form before the citing path exists — the census's E11 check fails a
mined row whose used-by paths are missing on disk.

## Gate-section quote for corpus/lessons/round-20.md (rule 1, ≤25 words)

Located quote (2 fragments, 15 words total, verbatim, kimi-shokunin copy,
commit `e737d2ea97f6b0198503e077676c3f2ea07974a9`):

- "`0` = `clean` and `1` = `failed` fleet-wide" (8 words, line 393, bullet **Verdict.**)
- "an undeclared nonzero code reads as `could-not-evaluate`" (7 words, line 395)

Note for the row author: the bullet's middle clause maps other codes onto
`clean | failed | could-not-evaluate` (lines 393-394) and is quoted in the
Report; it contains literal pipe characters, which may not appear inside a
registry cell.
