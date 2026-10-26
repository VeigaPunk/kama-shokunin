# S8Considerthese — round 48, lane kama

**Verdict: delivered.** Round 48 takes up two proposals — `considerthese/2026-10-26.md:33` (proposal 3, shortcut tally promoted to `tools/`, seat `X9Tally`) and `considerthese/2026-10-26.md:35` (proposal 4, the pin gap, seat `U2Pins`) — and the 20-proposal table of `considerthese/2026-10-22 … 2026-10-26` now carries a round-47 and a round-48 cell per proposal, each with file:line. One correction to the round-47 table came out of it: its row 20 said the pin gap got "no round", but round 47's own seat `U2Pins` had already run it (unnamed, and carried into no round-47 artifact) 10m37s before the tracker was written.

Snapshot: 2026-10-26T22:38Z (19:38 BRT), lane tip `b85783e8` (`git log --oneline -3 master` → `b85783e8 round-48: wave spec kama-r48-w1 (69 seats, policy v2) and dispatch`, `380bcdff round-48: build …`, `12284ba3 round-48: freeze …`). The round-48 wave is in flight: `git status --porcelain` shows `?? .ufo/waves/round-48/w1/out/` and `?? corpus/lessons/round-48.md`, and `ls .ufo/reports/round-48/` has no `kama.md`; there is no `corpus/lessons/round-48-verifier-spotcheck.md`. Round-48 cells therefore describe the round's named and built uptake, not a closure.

## Deliverable

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S8Considerthese/table.md` — the round-47 table (`.ufo/waves/round-47/w1/out/S8Proposals/table.md`) updated:
- §0 states what round 48 takes up, with the pointer for each: proposal 3 at `.ufo/waves/round-48/preregistration.json:55`, `.ufo/waves/round-48/w1/build_spec.py:171-172`, `SCORECARD.md:2733`; proposal 4 at `.ufo/waves/round-48/w1/build_spec.py:179-180` and `:198`.
- §1 is the 20-row table with the inherited columns plus **R47** and **R48** columns. Inherited cells are labelled as inherited and were not re-opened (exceptions: rows 18, 19, 20, where a new cell contradicts them).
- §2 the counts, §3 six findings, §4 the known integration items that were not re-reported.

Rows with a real round-47 footprint: 14, 16, 18, 19, 20. The other 15 saw only the tracker's own files (or one unrelated diff line), i.e. the round did not take them up. Rows with a round-48 pointer: 18 (this seat), 19 (preregistration line 55), 20 (build spec seats). No other 2026-10-22 … 26 proposal is named in any round-48 artifact.

## Evidence

Generated evidence, all cited by `file:line` in `table.md`; commands and exit codes in `commands.txt`, full hit lists in `refs-matrix.txt` and `refs-files.txt` (same directory):

1. **Proposal inventory.** `grep -n "^[0-9]\+\. \*\*" considerthese/2026-10-2{2,3,4,5,6}.md`, exit 0 → the 20 proposal lines (4 per file) at the same lines the round-47 table cites; no drift.
2. **Phrase matrix, 20 probes × 2 artifact sets.** `grep -rnF` per proposal over the round-47 set (prereg, build spec, `w1/out/**`, lesson, closure, `LOG.md` round slice, `SCORECARD.md` round slice, fleet `.ufo/reports/round-47/kama.md`) and the round-48 set (prereg, build spec, `w1/out/**` minus this seat, in-flight lesson, `SCORECARD.md` §Planned(48)). Round-48 named pointers exist only for P18/P19/P20 (P19 through prereg + build spec, P20 through build spec only).
3. **File-path matrix.** Round-48 hits for `considerthese/2026-10-25.md` and `…/2026-10-24.md` are all historical `SCORECARD.md` text quoted into wave diffs (`.ufo/waves/round-48/w1/out/S9Cap/SCORECARD.md.proposed:2338`, `…/X1Banner/08-SCORECARD.at-380bcdff.md:2338`, `…/L1Lowthr/sub20-diffs.txt:1687`); 0 hits for `2026-10-22.md` and `2026-10-23.md`.
4. **Full-range counts** (preregs + lessons, rounds through 48): 10-22 **0**, 10-23 **4**, 10-24 **7**, 10-25 **16**, 10-26 **8** (was 4 at the round-47 table; +3 in `corpus/lessons/round-47.md`, +1 `.ufo/waves/round-47/preregistration.json:56`, +1 `.ufo/waves/round-48/preregistration.json:55`). No older proposal gained a prereg/lesson pointer in round 47 or 48.
5. **Pin-gap negative check.** `grep -nE 'U2Pins|pin gap|b11910'` → exit 1, 0 hits on `LOG.md:2310-2318`, `corpus/lessons/round-47.md`, `corpus/lessons/round-47-verifier-spotcheck.md`, `.ufo/reports/round-47/kama.md`, `SCORECARD.md:2701-2730`; positive side `.ufo/waves/round-47/w1/out/U2Pins/pins.md:10,16,25`.
6. **Ordering.** `ls -la --time-style=full-iso`: `pins.md` 18:26:11 -0300 vs `S8Proposals/table.md` 18:36:48 -0300.
7. **Closure silent on proposal products.** `grep -nE 'S8Proposals|X9Tally|considerthese|proposal|tally' corpus/lessons/round-47-verifier-spotcheck.md` → exit 1, no output, while `:12` admits the round.

## Findings (each with the command that shows it and a proposed fix)

**F1 — round 48 names proposal 4 in the build but not in the preregistration.** `.ufo/waves/round-48/preregistration.json:55` names proposal 3 only; `.ufo/waves/round-48/w1/build_spec.py:179-180` builds proposal 4. Command: `grep -n 'considerthese' .ufo/waves/round-48/preregistration.json` → one line, 55. Effect: the lane's own tracker query over preregs (the round-47 table's method) cannot see proposal 4's round-48 uptake. Fix: make `considerthese` a list or append "proposal 4 (pin gap) built as seat U2Pins (frontier, not a claim)" to that string, and add the same to `SCORECARD.md:2731-2734`.

**F2 — the round-47 tracker's method cannot see seat-level uptake, and it missed a sibling seat in its own wave.** `.ufo/waves/round-47/w1/out/S8Proposals/table.md:30` records the pin gap as "no round… 0 occurrences"; seat `U2Pins` is in the same build spec (`.ufo/waves/round-47/w1/build_spec.py:113-114`) and its output predates the table by 10m37s (`pins.md` 18:26:11, `table.md` 18:36:48). The tracker's own negative-check method searched `preregistration.json` + `corpus/lessons/*.md` only (`table.md:37-41`) — where claims are declared, not where frontier proposals are mined. Fix: add `.ufo/waves/round-*/w1/build_spec.py` to the tracked set and read the current wave's seat items for proposal names.

**F3 — proposal 4's literal ask is unsatisfiable by a round.** `considerthese/2026-10-26.md:35` asks for one line per pinned engine in *each daily file*; `.ufo/waves/round-48/w1/build_spec.py:43` forbids rounds to edit `considerthese/`, so rounds 47/48 deliver it as a wave artifact (`.ufo/waves/round-47/w1/out/U2Pins/pins.md:16,25`; `.ufo/waves/round-48/w1/out/U2Pins.md:3`). Fix: restate the proposal as a round-report line or have the daily pass consume `pins.md`.

**F4 — carried forward, still open: the reflection undercounts its own 2026-10-25 uptake.** `considerthese/2026-10-26.md:31` says "three of the four 2026-10-25 proposals became rounds 41 to 43"; proposal 4 landed in round 45 (`.ufo/waves/round-45/preregistration.json:65`, `corpus/lessons/round-45.md:21`) — four of four. Rounds 47/48 changed nothing here.

**F5 — a round closure can admit a round and leave its frontier artifacts unruled.** `corpus/lessons/round-47-verifier-spotcheck.md:12` admits round 47; the file has 0 hits for `S8Proposals|X9Tally|considerthese|proposal|tally` (command in Evidence 7), so rows 18 and 19 have no verdict and this tracker's closure column stays empty — although round 46's closure did rule a proposal product (`corpus/lessons/round-46-verifier-spotcheck.md:13`, row 17). Fix: closures add one "frontier, not ruled" line per artifact they do not rule.

**F6 — the round-48 lesson carries no proposal line (in flight).** `grep -c 'considerthese\|proposal' corpus/lessons/round-48.md` → 0. Round 47's lesson has one (`corpus/lessons/round-47.md:37`), so the convention exists; until it is written, round 48's uptake lives only in the prereg field and the untracked wave dir. Fix: keep the §Assimilation/considerthese line in the lesson template and make it list every proposal whose substance ran, named or not (F2).

## Scope and limits

- Read-only on the lane and the fleet repo: no `git add/commit/checkout/stash/reset`, no jj, no writes outside `.ufo/waves/round-48/w1/out/S8Considerthese/` and this report; `considerthese/`, counters, preregistration and controls untouched.
- No counters or lane tools were run: this seat's evidence is grep over committed/working-tree bytes, and nothing here restates a claim measurement. The round-48 wave's own outputs are a snapshot; peers were still writing (`out/U2Pins.md` is cited as in flight).
- The negative cells are phrase-based: a round could take a proposal up in wording that shares no phrase with it. The file-path matrix (§2.1) is the guard — no day except 2026-10-26 gained a prereg/lesson pointer in rounds 47–48.
- Columns 3/4 for rows 1–17 are inherited from the round-47 seat and were not re-verified; `table.md` says so per section.
- No tools installed or upgraded; no pacman (host-wide pause).
- Scratch `/fast/scratch/hyaku/kama-r48/S8Considerthese` removed at the end of this seat, after the evidence files were copied into the out directory.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S8Considerthese/table.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S8Considerthese/commands.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S8Considerthese/refs-matrix.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S8Considerthese/refs-files.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S8Considerthese.md` (this file)
