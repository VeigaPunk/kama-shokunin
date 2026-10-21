# SHONEN.md — round-21 draft lines (ScribeTrends, advisory; L1 applies)

All four boxes stay `[~]`. Round 21 adds author-side pointers only. No `[x]` is justified: `LEARNING.md` §Discernment has no outside spot-check, and every pointer below is lane-authored. Pointers are appended under each box's existing `→ Author assertion:` line; existing text is not rewritten (`CORPUS.md` corrections rule).

## Box 1 — SKILL.md decision tables, error patterns, checklists, cited sources

```
- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
      → Author assertion: `SKILL.md` §§Decision table, Error signatures, Checklist; no named non-author verifier.
      → Round 21: `SKILL.md` §"Round-21 instrument registry" (lines ~674–696): one decision row (soname retarget / glibc-hwcaps copy → `install_tree_sha256` unchanged, `install_links_sha256` moves; cites S066, S067) and one checklist addition (run `tools/report-landing-audit.py --report N=<draft>` before a fleet commit). Author assertion; no non-author verifier.
```

## Box 2 — end-to-end domain task executed and logged in LOG.md

```
- [~] At least one end-to-end domain task executed and logged in LOG.md
      → Author assertion: (unchanged prefix) ...
      → Round 21 live (not yet in LOG.md): `.ufo/waves/round-21/runs/b76727f3/live-receipt.json`, ephemeral loopback llama-server b11755, alias `kama-r21-live`, 11 checks; `check-receipt.py --require-schema v3 --require-install-links` with three pins exits 0 (`c2-live-gate-pinned.exit`), wrong links pin exits 1 (`c2-live-gate-wrong-links-pin.exit`). Lane-owned control; no non-author mark.
      → LOG.md has no round-21 entry at b76727f (last round heading: round 20, LOG.md:1199). The L1 writes the LOG entry; until then this box's pointer is the receipt path only.
```

## Box 3 — instructions executable by an agent without oral context

```
- [~] Instructions executable by an agent without oral context
      → Author assertion: `SKILL.md` §Checklist and `corpus/knowledge/snapshot-history.md` §Run it; independent execution review remains open.
      → Round 21: `.ufo/waves/round-21/recipe.json` + `run.py` reproduce the 28-command measurement from the file alone (recipe sha256 `9d68997d…` per `runs/b76727f3/commands.json`). Declared exits recounted 28/28 by a scribe-side script (exit 0). Independent re-execution by a non-author not performed; box stays `[~]`.
```

## Box 4 — no cross-domain bleed (PROVINCE.md still accurate)

```
- [~] No cross-domain bleed (PROVINCE.md still accurate)
      → Author assertion: `PROVINCE.md` §Write boundary and `corpus/knowledge/cross-lane-scope.md`; service repair, routing and credentials remain operator/sibling-owned.
      → Round 21 caveat: `tools/report-landing-audit.py` reads fleet-root reports (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-N/kama.md`) and fleet and lane git objects; stdout only (SKILL.md row "Report landing audit"). `PROVINCE.md` was not changed in round 21 and does not name fleet-report or fleet-object reading (grep for fleet / .ufo/reports / git log / landing: no match). Province must either name this surface or the claim "PROVINCE.md still accurate" is not re-established for round 21.
```

## Lines not drafted

- No `[x]` on any box. No new box. The round did not move SHONEN's promotion gate; it adds pointers and one open item (box 4) for the L1.
