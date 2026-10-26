PROPOSED-FIXES — K1Regions (leaf seat), v3 region escape hatch
===============================================================

Frozen-tool note: the counter, the tool and the contract are FROZEN for round 48. These are
proposed corrections for a future round, NOT edits applied in place. Targeted lines in
tools/append-only-audit.py (v3): eligible set computation in audit() lines 409-411, deleted-line
classification lines 412-419, sections() lines 231-238; the C1 counter recomputes the same
definition on its own code path (round48-append-audit-v3-check.py recompute()).

Finding (from fixtures, see K1Regions.md):
  - A2/B2: dated append-only content moved/retitled under an exempt head title is deleted and
    reported `ungraded` (exit 0) when the section's line count is sustained with filler.
  - C/D2: an exempt section gutted (even deleted wholesale with its heading) at the event is
    laundered by any later regrowth of enough lines (window maximum of the count).

Proposed minimal corrections (both needed; each alone leaves one hole):

1. Window-min eligibility (kills C/D2) — audit() lines 409-411:
   replace
       eligible = {t for t in titles
                   if max(r.section_counts(wb[f"{x}:{f}"])[t] ... for x in window)
                   >= pcount[t]}
   with the window MINIMUM
       eligible = {t for t in titles
                   if min(r.section_counts(wb[f"{x}:{f}"])[t] ... for x in window)
                   >= pcount[t]}
   i.e. the section must never have dropped below its parent count at any window commit (never
   gutted), not merely have recovered by the tip. Note this changes the meaning of the contract's
   "ungraded while they are not gutted" to "never gutted in the window".

2. Provenance anchor (kills A2/B2) — audit() classification lines 412-419:
   a deleted line is graded if its text occurs at ANY window commit inside a non-exempt section,
   regardless of the parent position's section:
       anchored = {text for x in window
                   for pos, t in enumerate(sections(r.list_lines(wb[f"{x}:{f}"])))
                   if t is not None and t not in eligible and t not in titles}
       # (simpler bound: any text whose section at the parent or at any earlier window commit
       #  was a non-exempt section)
   and skip the exemption for lines in `anchored`. False-positive risk: a head that quotes dated
   lines verbatim would see those quoted copies graded on deletion; the lane's heads do not do
   this (all 89 ungraded lane lines are native head content).

Alternative to 2 that respects the "re-derived" concept: anchor by section-title history instead
of text — a deleted line's section is taken from the EARLIEST window commit at which that line
exists, so a line born in a dated section stays graded even after the heading above it is renamed
or it is moved under a head.

Scope check: changes 1 and 2 are internal to the v3 definition; the contract row text does not
need to change (the region cell and pointer stay valid). The C1 counter's recomputation would
need the same two changes to keep lane-equality.
