# CR01 — C2 falsification report (kama r77 w1, freshness)

Full commands + verbatim output: `.ufo/waves/round-77/w1/CR01Critic/critique.md` (receipts and
driver scripts beside it). Freeze `7d60e2ab`, base `cc6e1d3c…`; the C2 counter landed mid-seat
(`d86ce85b`, blob `a3b3ec41…`, byte-identical through `master`=`3442cb6a` at test time), so
findings are split plan-level vs landed-bytes. No tools installed. All git writes were fixture
plumbing in `$S` (toplevel-asserted); the lane was only read; `$S` deleted after receipts were
copied.

**F1 — frozen-plan incoherence (load-bearing).** The nine strict rows the round must append name
9 SCORECARD.md events, all younger than the accepted register's introduction `10f37171`; FOUR are
younger than even the exempt register's own introduction `c2aa7fb2` (`417bbf81`, `461d2adb`,
`661622b5`, `c1ae92d5`). Under the predicate's literal "under that register's own introduction
cutoff", `exempt` caps at 52 and `unaccounted >= 36`: the frozen after-line `exempt=56 …
unaccounted=0` is unreachable. Only scope ruling (a) ("ancestor of the audit revision") reaches
the target, and the landed counter implements exactly that. Predicate sentence vs ruling (a) are
different semantics, not paraphrase — freeze divergence (already routed to SC02Lesson).

**F2 — growth hole, executed by the landed bytes.** Ruling (a) leaves no temporal bound on rows:
the landed counter exits **0** (`exempt=57, unaccounted=0, rotation_safe=1`) on a fixture tip
whose SCORECARD `## Retired` re-derivation is made **in the audited commit itself** and blessed
by an **uncommitted worktree exempt-head row naming that tip commit**; the accepted register
likewise moved 53→54 blessing a fresh graded `corpus/README.md` deletion at the tip via an
uncommitted row. Every kill arm stays green (row present, counts right, not inside an `only=`
region, no re-introduction). This contradicts the round-51 disclosure doctrine ("a ledger that
accepts new rows would bless any later damage") and the round-75 tool's own default cutoff
(which exits 1 `post-introduction` on the same fixture). Smallest safe correction keeping the
target reachable: a row may only name an event that is a **proper ancestor of the commit that
first carries the row**; 9/9 target rows pass, same-commit rows fail. Judge must decide
intended-tradeoff vs defect; the kill-rule list should say so either way.

**F3 — defect: receipt rot.** Registers are read from the working tree, inverting the round-76
discipline ("committed at the audit's explicit `to` revision, never worktree TSVs"). One row
naming an event outside the `--to` audit — precisely what round 78's legitimate growth adds —
flips the frozen counting command to exit 1 (`wrong-class … not a class-bound exempt-head event`)
while every bucket stays green. The round-77 C2 receipt cannot survive the next round's append;
blessing rows need no commit at all; the summary prints no register blob shas. Root cause is a
frozen-text bind (counting command pins `--to` base while growth needs newer rows). Correction:
read registers at `--to`, run the counting command at the round tip, record the divergence (or
minimally print both register blob shas).

**F4 — clean.** `out_of_region` does not swallow a real head edit: a deletion inside the declared
`## Errata` region grades (`graded=1, status=unrestored`) and stays a finding (`out_of_region`
stays 4, exit 1); a deletion outside classes `out_of_region` (5) as declared.

**F5 — clean.** `permitted` cannot swallow a one-graded-line event: the declared condition
(`permitted==deleted ∧ graded==0 ∧ ungraded==0`) is satisfied by exactly the 28 SOURCES.md events
and excludes the 3 real mixed events (e.g. `5890d1a0`: deleted=7, permitted=6, graded=1); a
laxer `permitted>0` rule would double-bucket all three (all also `restored`) and break
exactly-once. Landed `permitted-overclaim` selftest arm PASS.

**F6 — clean.** Rotation: re-add with new rows → flagged (`rotation … re-introduction carries new
rows`, `introductions=1/2`, `rotation_safe=0`, exit 1); normal append → not flagged
(`rotation_safe=1`, row valid); unchanged re-add → subset, not flagged (last-extant-version
reading, resolving the absent-version ambiguity). The round-76 counter, by contrast, mislabels a
normal append's young row as class `rotation`. Landed selftest 7/7 PASS; old selftest 6/6 PASS.

**F7 — control.** Do-nothing: 41 unaccounted (round-76 counter) / 9 (landed counter — exactly
the 9 SCORECARD rows). Appending only the nine rows helps nothing under the old counter (41
unaccounted + 18 rotation findings) and cannot ever cover the 28 permitted + 4 out-of-region
events (accepted rows require undisclosed graded lines; exempt rows require `ungraded==deleted`);
with the landed counter-side classes the nine rows reach the frozen target line, exit 0.

**Target arithmetic verified independently:** 95+5+53+56+28+4 = 241 = events; buckets pairwise
disjoint; base remainder is exactly the nine strict rows; `accepted=53` identical with and
without the temporal bound (ruling (a) does not inflate it at base); `restored=95` all
`held_at_to==graded`; `permitted=28` all SOURCES.md; `out_of_region=4` all consumer-registry.md.

Main checks: re-run the frozen counting command at the lane (expect target line, exit 0 — and
expect exit 1 after any future register append, per F3) and `--selftest` (7/7, exit 0).
