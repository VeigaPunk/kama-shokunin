# N5Mistakes — round 49 frontier sweep (closures 45–48 vs lesson Mistakes rows and QUALITY criteria)

**Verdict: 10 routed items from closures 45–48 have never (or not yet) become a lesson Mistakes row or a QUALITY criterion — 6 still open (F1 r45-D1, F2 r46-D3 sub-gaps, F3 r46-D4, F5 carried frontier, F6 r44-D3, F8 r47-D7), 3 closed by implementation without capture (F7 r47-D2, R1, R5 witness/binding — capture pending at round-49 integration), 1 unfixed unbounded deferral (F9 r47-D8); the round-48 closure's R2/R3/R4 are captured in the round-49 lesson draft rows 1–3; no spot-check disagreement went uncaptured.**

## Evidence (read-only; no counter run, no scratch, no installs)

- `read corpus/lessons/round-{45,46,47,48}-verifier-spotcheck.md` — routed-defect lists at:
  - round-45: `round-45-verifier-spotcheck.md:146-150` (D1–D3, carried #4, operator #5)
  - round-46: `round-46-verifier-spotcheck.md:137-143` (D1–D6, operator)
  - round-47: `round-47-verifier-spotcheck.md:97-107` (D1–D9, operator)
  - round-48: `round-48-verifier-spotcheck.md:110-127` (R1–R5, operator/promotion)
- `read corpus/lessons/round-{45,46,47,48}.md` Mistakes rows:
  - round-45: `round-45.md:27-31` (5 rows); round-46: `round-46.md:35-42` (8 rows + sweep findings at :87-88); round-47: `round-47.md:45-50` (6 rows); round-48: `round-48.md:28-32` (5 rows).
- `read corpus/QUALITY.md` KQ62–KQ75 (`:377-413`); `grep -n 'sparse|GiB|member size' corpus/QUALITY.md` → 0 matches.
- `read corpus/lessons/round-49.md` — draft rows 1–3 already capture R2/R3/R4 (`round-49.md:33-35`).
- `read .ufo/waves/round-49/preregistration.json` — claims carry `cap=1` (R1) and v4 origin/binding (R5 halves); **no `routed` block**; `grep -n 'prerelease' .ufo/waves/round-49/preregistration.json corpus/lessons/round-49.md` → 0 matches.
- `grep -n 'r45-D1' -R corpus/lessons/ .ufo/waves/round-49/` → 0 matches (F1 drop confirmed).
- `grep -n 'floating-series|base-unresolved|rerank' -R corpus/lessons registry/` → only closures 43–45 and the round-46 sweep transcript (F5).
- `grep -n 'V1Code|reworded witness|auto-picked' -R corpus/lessons/` → only `round-44.md`, `round-46.md`, `round-46-verifier-spotcheck.md` (F2).
- `read .ufo/waves/round-48/w1/out/K0Harm.md:54` — `tools/sources-append-only.py` exit 2 on every revision since round 45; `read …/K0Harm/evidence/commands.out` → `exit=2` (F9).
- `read .ufo/waves/round-48/w1/out/K2Record.md` — record-time verification binds local bytes only; no URL fetch; recommended against (F11b).
- `read .ufo/waves/round-48/w1/out/N5Mistakes/sweep.md` — prior sweep F1–F8; this round re-verifies its 45–47 findings and adds the round-48 closure items.

## Findings needing a fix (proposed rows in `sweep.md`)

| # | Item | Source (file:line) | Gap |
|---|---|---|---|
| F1 | r45-D1 claim-outcome reader re-freeze | `round-45-verifier-spotcheck.md:146`; deferral `round-46.md:12` | KQ65 lacks the known-data constraint + recomputation citation; absent from all later routing |
| F2 | r46-D3 sub-gaps: reworded witnesses auto-picked; V1Code F1–F4 | `round-46-verifier-spotcheck.md:139` | r47 row 1 captures the family, not these two named items |
| F3 | r46-D4 hexrun red gate | `round-46-verifier-spotcheck.md:140` | closed at r47 (`unknown=0`) without a row/criterion |
| F5 | carried frontier rows S013/S022/floating-series/S002–S004/rerank | `round-45-verifier-spotcheck.md:149`, `round-44-verifier-spotcheck.md:112` | never tracked; `release-recheck-*.tsv` lack them |
| F6 | r44-D3 registry hygiene | `round-44-verifier-spotcheck.md:110` | closed without capture; no recurrence |
| F7 | r47-D2 replay loop over all 3 receipts | `round-47-verifier-spotcheck.md:98` | implemented in r48 C2 (`replayed=3/3`); no row/criterion |
| F8 | r47-D7 prerelease cliff | `round-47-verifier-spotcheck.md:103` → `round-48-verifier-spotcheck.md:120` | absent from round-49 planning (0 matches) |
| F9 | r47-D8 sources guard parser | `round-47-verifier-spotcheck.md:104`; class `round-47.md:49` | unfixed (exit 2), unbounded deferral |
| F10 | R1 verify_archive_member size bound | `round-48-verifier-spotcheck.md:110` | fixed in round-49 C1 (`cap=1`), no KQ yet |
| F11 | R5 sub-items | `round-48-verifier-spotcheck.md:115-119` | witness/binding in-flight (capture pending); record-time fetch and sub-20 threshold open, disclosed only |

Operator/L0 items (F12) stay open by design: planner seat (`kama|round-39`), MISSION axes pair (`kama|round-35`), parked worktree (`kama|round-41..43`), N3Fleet adjacency (r46-D6), r45 closure N-A salvage commit, and the round-47 closure "quoted map matches" row correction (R4).

## Proposed fixes (highest leverage)

1. **KQ row for the carried-item rule** (from round-46 sweep finding 1): a carried item surviving three closures without a lesson row must become one or be dropped with a stated reason — this single rule would have forced F1/F5/F8 into rows.
2. **Restore the `routed` block mechanism** in the round-49 preregistration (present in round-48, absent in round-49); the r48 lesson row 4's fix depends on it.
3. **Capture R1 and the R5 fixes at round-49 integration** as KQ rows (archive-member bounds; witness leg; v4 origin/binding) with the counter legs as shown-able-to-fail checks — the KQ74/KQ75 pattern.
4. **r47-D7**: carry the prerelease limit in the round-49 `limits` or name a cache hardening round.
5. **r47-D8**: bind the sources-guard parser repair to a round (K0Harm's patch is ready in wave evidence) or retire the guard with a stated replacement.
6. **F1**: if the claim-outcome ledger is ever re-claimed, the KQ65 sample sets must be pre-scored before the reader sees the ledger, citing the 58/61 recomputation.

Files written:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/N5Mistakes/sweep.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/N5Mistakes.md`
