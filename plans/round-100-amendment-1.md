# Round 100 — amendment 1 (kama): both claims narrowed to what their frozen counters enforce

Written after wave 1 and before filing (Amendment 59, choice (i)). No instrument, probe, receipt or correction
block changes: the counters `tools/round100-record-audit.py` and `tools/round100-props-status.py`, the probe
`tools/kama-probe.sh`, and the measured commit M `2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6` are the freeze's,
byte for byte, and the measured receipts `.ufo/waves/round-100/measured/c1.out` / `c2.out` stand. Only the
claim **wording** is narrowed. The wider frozen sentences in `plans/round-100-claims.md` stay as filed and are
**not verified** as written; the narrowed sentences below are the claims this round files.

## Why (the wave's own artifacts)

**C1.** The frozen headline "agrees with the committed round-99 wave evidence on nine enumerated checks" claims
more than the nine checks enforce:

- presence-only checks 3, 4 and 6 (`led_s in sc`, `seat_s in b`; no left boundary, no consistency with the rest
  of the block): a block that also says "seven attack seats" in words or "two seats were dead" in prose
  (`w1/EX02RecordForge.md` G1/G14), that names the wrong seats as attack seats (`w1/EX02RecordForge.md` G2/G9,
  `w1/CR01Records.md` FA/FB/FC), or that writes `14 of 12 (33%)` / `112 seats, 0 dead` (`w1/RV01WordingC1.md` N2)
  grades `met=True`;
- check 8 grades `phrase in line`, so a substring or one character (`("e")`) resolves (`w1/EX02RecordForge.md`
  G3/G11), and a pointer bound to the commit under test resolves (G10);
- the pointer grammar sees only backticked, lowercase-hex `@<rev>` forms of `SCORECARD.md`/`LOG.md`/
  `corpus/lessons/<name>.md`: a pointer in words (`` `SCORECARD.md` line 6431 ``), `LOG.md#L4040`, a nested
  lessons path, or a non-lowercase/symbolic revision is neither bound nor unbound (`w1/RV01WordingC1.md` §2,
  `w1/SB01Lesson.md` §1.1 twin-case control); a `tools/x.py:12` pointer is ungraded (G12; frozen limit (b)).

**C2.** The frozen sentence "the probe reads the router's bare `/props` body only on a final HTTP 200" is a
behavioural universal; the nine cells grade nine answers:

- a probe that adds `-L` stays green because S6's `Location` target answers 404, never 200
  (`w1/EX01PropsForge.md` BS-1);
- a probe that treats curl's `000` as 200, or admits 204/304, stays green because no cell serves a transport
  failure or a seeded empty-body status (BS-2, BS-3);
- the stub strips the query string, so a probe that reads `/props?model=<id>` instead of bare `/props` stays
  green (`w1/SB01Lesson.md` §1.2, VERDICT C2).

The probe's code does have none of these behaviours (`tools/kama-probe.sh` at M lines 901–904: no `-L`, the
curl call is `|| return 2` so a transport failure never reaches the status test, `[ "$pcode" = 200 ] || return 2`,
bare `/props` URL) — but the counter does not prove it, so the claim may not say it.

## C1 — narrowed (filed) wording

`python3 tools/round100-record-audit.py --repo . --rev 2e27e6f1` prints `RECORD_AUDIT100 checks=9 mismatches=0
met=True` and exits 0 (base `6776c667`: `mismatches=9`, exit 1; the seven freeze-time forgeries F1–F7 exit 1).
At M: (1, 2) exactly one `## Round 100 correction — round-99 records` heading starts a block in `SCORECARD.md`
and in `LOG.md`; (3, 4) each block contains, as substrings, the counter-derived strings `4 of 12 (33%)` and
`6 of 12 (50%)`; (5) neither block, after removing the counter's bound-pointer tokens, contains a digit
percentage (`\d+(\.\d+)?\s?%`) other than `33%` and `50%`; (6) each block contains the substring `12 seats, 0 dead`;
(7) the blocks contain no `SCORECARD.md:`/`LOG.md:`/`corpus/lessons/<name>.md:` digit pointer outside the bound
grammar `` `<path>@<lowercase hex 7-40>:<line>` ("<phrase>") ``, and at least three bound tokens; (8) for every
bound token, the non-blank phrase is a substring of that line at that revision; (9) `.ufo/waves/round-100/
r99-measured.json` maps exactly C1/C2/C3 to byte copies of the first predicate line of the round-99 receipts
`measured/c{1,2,3}.out`, each ending `exit=0`.

**Not claimed:** that the blocks are otherwise consistent with the round-99 evidence (seat names, numbers in
words, prose contradictions, digit strings with extra leading digits); that a quoted phrase is the minimal or
intended quotation; that a bound revision predates the commit under test; that pointers written in words, as
`#L<n>`, with non-lowercase or symbolic revisions, under nested lessons paths, or to non-`SCORECARD`/`LOG`/
lessons files are bound.

## C2 — narrowed (filed) wording

`python3 tools/round100-props-status.py --repo . --rev 2e27e6f1 --work <scratch>` prints
`ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True` and exits 0: on nine
loopback stub answers to the probe's `/props` request (the stub ignores any query string), the probe at M
grades (verdict, reason, exit) as listed — the six router-shaped answers under 401, 500, 503, 403, 202 and 302
(a `Location` that answers 404) and the llama.cpp 401 document read `MODEL_UNLOADED`/`router-autoload-unread`/2;
200 router-off reads `MODEL_UNLOADED`/`router-unloaded`/2 and 200 router-on reads
`MODEL_OK`/`router-unloaded-autoload`/0 — where the base probe graded S1–S6 as explicit states (four of them as a
false `MODEL_OK`, exit 0).

**Not claimed:** that the counter proves the probe never follows redirects, never reads a body after a transport
failure, rejects every other non-200 status (204, 304, …), or requests the bare path; those are properties of the
probe's code at M (lines 901–904), shown by reading it, not by the counter. The killer cells are routed to round
101 (`SCORECARD.md` §Planned (round 101)): a 302 whose target answers 200, a closed port with a pre-seeded body
file, seeded 204/304, and a stub that keeps the query string.

## Kill rules re-read under the narrowed wording

K1 (instrument bytes changed after freeze) — not fired: `git diff 2e27e6f1 <filing tip> -- tools/round100-*.py
tools/kama-probe.sh` is empty. K2 (`met=False` at M) — not fired (`measured/c1.out`, `measured/c2.out`). K3 (base
green) — not fired (`controls/c1-base.out` 9, `controls/c2-base.out` 6). K4 (positive controls) — not fired (P0,
P1, P2).
