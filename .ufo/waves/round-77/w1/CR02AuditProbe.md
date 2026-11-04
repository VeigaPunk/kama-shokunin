# CR02 adversarial audit probe

Axis impacted: freshness (C2). Frozen plan read in full, predicates unchanged. Base `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`; observed master/freeze commit `7d60e2ab58866a0366937d61c9712483be57b36e`.

## Counterexample and evidence

A single event can contain both a permitted SOURCES status-row replacement and an exempt-head replacement: `deleted=2 graded=0 ungraded=1 permitted=1 status=ungraded`. Therefore neither `permitted > 0` nor `status == ungraded` identifies a fully permitted event. This is an implementation trap, not evidence against the frozen conjunction.

The assigned fixture also demonstrated pure permitted (`1/0/0/1`), outside-only-region (`1/0/1/0`), inside-only-region (`1/1/0/0`, unrestored), and SCORECARD exempt-head (`1/0/1/0`) events; tuple order is deleted/graded/ungraded/permitted. `file_regions` returned empty titles and `['## Errata']` prefixes. `round76-append-exempt.py:58-73` reads only titles when deciding exempt-head eligibility, so that old helper alone cannot classify only-regions.

## Exact answers

- Yes, under the audit's mechanical A-row definition: `permitted == deleted` holds only if every deleted line is recognized as a permitted row edit. Pure status edit: deleted=1, graded=0, ungraded=0, permitted=1. The check compares immutable parsed cells, not whole-row byte identity.
- Yes. `file_regions` returns `(set(), ['## Errata'])`: empty exempt titles and the Errata prefix. Parent sections distinguish outside (`## Body`, graded=0, ungraded=1) from inside (`## Errata`, graded=1, ungraded=0). Do not reverse the tuple or treat empty exempt titles as absence of an only-region.
- Yes, on a mixed event: deleted=2, graded=0, ungraded=1, permitted=1, status=ungraded. This disproves treating any positive permitted count as sufficient. It does not break the frozen C2 condition: `permitted == deleted and graded == 0 and ungraded == 0` correctly excludes this event.

## Smallest safe correction

Keep the frozen permitted conjunction exactly; reconstruct parent sections for every deleted line and test each against all only-prefixes before assigning out_of_region. Mixed events must fall through to register coverage, not be split into multiple event buckets or granted a blanket exemption. No production edit made; no canonical judgment offered.

## Receipt and exercised command

- Absolute receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/LB01Labrat/probe.md`.
- Command: Python module import of `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py`, then `audit('/fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT')` and `exit_code(data)`; audit exit **1**, expected due to inside-region deletion. Fixture driver exit **0**; every fixture git command exit **0**, recorded verbatim in the receipt.
- Read-only revision commands: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` and `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log master --diff-filter=A --format=%H -- plans/round-77-claims.md`; each exit **0**.
- Cleanup: `/fast/scratch/hyaku/kama-r77/CR02AuditProbe` removed in `finally`, existence false. No installs/updates; no lane git writes; no delegation.

Bounded limitation: this probes the audit API semantics, not the not-yet-reviewed round77 counter implementation. Any inference that its current implementation misclassifies the mixed event would be unsupported.

Self-evaluation: accuracy 5 (literal event output and bound declarations); completeness 5 (all three questions, mandatory fixture and cleanup); clarity 4 (full receipt is necessarily lengthy); actionability 5 (exact conjunction and region test named); conciseness 4 (receipt duplicates core event evidence). Overall 4.6. Improvement: downstream readers can use this summary while preserving the verbatim receipt. User-agreement self-check: scope and limitations are explicit.
