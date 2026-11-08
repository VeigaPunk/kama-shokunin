# Round 100 — frozen claims (kama)

Base revision `6776c667372a0da8635ebfbda6cbc92d8fb17304` (lane `master` at round start; round 99 closed
`admitted` — C1/C2/C3 verified at `00394f3b`, `corpus/lessons/round-99-verifier-spotcheck.md`). L1
`KamaR100` (holds the §3 planner seat). Frozen in the commit that adds this file, together with the two
counters, the probe change, the correction blocks, the source rows and every freeze-time control, so
"the graded bytes are the freeze commit's bytes" is checkable. That freeze commit is the measured
commit M for both claims unless an amendment (`plans/round-100-amendment-<n>.md`) names a later one.

Closure history read before declaring: r94 `rejected-honest-stop`, r95 `admitted`, r96
`rejected-honest-stop`, r97/r98/r99 `admitted`; the Amendment-59 autopsy class (a frozen counter green
on a property narrower than the claim's wording, falsified by the round's own wave). Each claim below
therefore states its wording as the counter's checks, lists what the counter does not grade, and is
attacked by the wave before filing.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7,
adjacency 7. Lowest non-retired: depth / calibration / adjacency (7). **C1 works calibration** (assigned
axis and lowest), **C2 works depth** (lowest). Causally separable: C1 reads only `SCORECARD.md`,
`LOG.md`, the round-99 wave files and `.ufo/waves/round-100/r99-measured.json`; C2 reads only
`tools/kama-probe.sh` (at M and at base) and its own loopback stubs. Neither counter reads the other's
surface. C2 is the round's sourced claim (S629, S630, S631, opened this round).

## Receipts

- **Freeze-time (committed with this plan):** `.ufo/waves/round-100/controls/census-start.out`,
  `c1-base.out`, `c1-forgeries.out` (+ `c1_forgeries.py`), `c2-base.out`, `c2-candidate.out`,
  `c2-mutant-blanket.out`, `c2-prefreeze-p2guess-base.out`, `c2-prefreeze-p2guess-candidate.out`;
  `.ufo/waves/round-100/sources/S629-*.txt`, `S630-*.txt`, `S631-*.txt`.
- **Measurement-time:** `.ufo/waves/round-100/measured/c1.out`, `c2.out`,
  `controls/c2-regression-r99.out`, `controls/census-end.out`.

## C1 — calibration: the round-100 correction of the round-99 records agrees with the committed round-99 wave evidence on nine enumerated checks

**Predicate (same sentence in `tools/round100-record-audit.py`'s docstring and in the receipt label):**
`python3 tools/round100-record-audit.py --repo . --rev <M>` prints
`RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=<resolved>` and exits 0 at M.

The nine checks, all read from `git show <M>:…`: (1) one `## Round 100 correction — round-99 records`
block in `SCORECARD.md` and (2) in `LOG.md`; (3, 4) each block contains the policy attack fraction
`4 of 12 (33%)` and the ledger attack fraction `6 of 12 (50%)`, both derived by the counter from
`.ufo/waves/round-99/w1-spec.json` roles; (5) neither block, its quoted pointer phrases removed,
contains a digit percentage other than those two; (6) both state `12 seats, 0 dead`, derived from
`.ufo/waves/round-99/w1-results.json`; (7) every `SCORECARD.md`/`LOG.md`/`corpus/lessons/*.md` line
pointer in the blocks is revision-bound and quoted (`` `<path>@<rev>:<line>` ("<phrase>") ``),
unbound = 0, bound ≥ 3; (8) every bound pointer's phrase is on that line at that revision;
(9) `.ufo/waves/round-100/r99-measured.json` maps exactly C1/C2/C3 to the round-99 measured predicate
lines, byte-equal to `.ufo/waves/round-99/measured/c{1,2,3}.out`, each of which ends `exit=0`.

- **Before (the defect).** Routed by the round-99 spot-check: defect 1, the round-99 correction blocks
  cite `SCORECARD.md:6431` unbound and the sentence had moved to line 6446 by the round-99 tip;
  defect 2, `SCORECARD.md` §Round 99 says "58% attack if the connector counts" where the derived
  value is 6 of 12 (50%); defect 4, `.ufo/waves/round-99/claims.json` still says `"measured":
  "pending"`. At base the counter prints `mismatches=9 met=False`, exit 1
  (`controls/c1-base.out`).
- **After.** `checks=9 mismatches=0 met=True` at M.
- **Do-nothing control:** `controls/c1-base.out` (base, 9 mismatches, exit 1).
- **Forgery controls (freeze-time, public path `--repo/--rev` on scratch commits):**
  `controls/c1-forgeries.out` — P0 (the lane's correction) exits 0; F1 a stray "58%", F2 an unbound
  `LOG.md:4040`, F3 a pointer one line off, F4 a one-byte edit of a measured line, F5 the old
  "7 of 12 (58%)" share in the LOG, F6 "12 seats, 2 dead", F7 an empty quoted phrase each exit 1.
- **Kill rules:** K1 the counter's bytes change after the freeze commit without an amendment; K2
  `met=False` at M; K3 the base control is green; K4 the positive P0 or any F1–F7 forgery grades
  wrongly at M.
- **Disclosed limits (what the wording does not claim).** (a) Checks 3, 4 and 6 are presence checks:
  a block that also says "seven attack seats" in words, or contradicts the share without a digit
  percentage, is not caught. (b) Check 7's pointer grammar covers `SCORECARD.md`, `LOG.md` and
  `corpus/lessons/*.md` only; a `tools/x.py:12`-style pointer is neither required to bind nor graded.
  (c) The round-99 entries and `.ufo/waves/round-99/claims.json` are not rewritten; the correction
  supersedes them by reference. (d) The fleet report `.ufo/reports/round-99/kama.md` (outside the
  lane) also says 58% and is not graded. (e) "Dead" is derived as empty output or a failure status;
  the round-99 results file carries no status field. (f) Pointers elsewhere in `SCORECARD.md` and
  `LOG.md` (outside the two blocks) are not graded; this claim does not assert the lane's other
  pointers are bound.

## C2 — depth: the probe reads the router's bare `/props` body only on a final HTTP 200

**Predicate:** `python3 tools/round100-props-status.py --repo . --rev <M> --work <scratch>` prints
`ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True` and exits 0
at M.

Nine live cells (stub router on loopback; `/v1/models` 200 with one `unloaded`, not-failed entry
whose model file exists) grade the probe's (verdict, reason, exit) per bare `/props` answer: S1 401
router-off, S2 500 router-on, S3 503 router-off, S4 403 router-on, S5 202 router-on, S6 302 router-on
(+Location) must read `MODEL_UNLOADED`/`router-autoload-unread`/2; S7 the exact llama.cpp 401
`Invalid API Key` document reads the same (stable); P1 200 router-off reads
`MODEL_UNLOADED`/`router-unloaded`/2 and P2 200 router-on reads `MODEL_OK`/`router-unloaded-autoload`/0
(positive controls, stable).

- **Before (the defect).** `router_autoload()` ran curl without reading the status (`tools/kama-probe.sh`
  at base, line 893): a router-shaped body under 401/503 read as explicit off and under 500/403/202/302
  as autoload-on — a false `MODEL_OK` cold start, exit 0. The round-99 SKILL §Round 99 limit already
  stated the gap; the round-99 spot-check routed it (RV01 F5). Base: `mismatches=6`, exit 1
  (`controls/c2-base.out`).
- **After.** `pcode=$(curl … -w '%{http_code}' …) || return 2; [ "$pcode" = 200 ] || return 2`;
  `mismatches=0 flips=6 stable=3` (candidate receipt `controls/c2-candidate.out`).
- **Grounding:** S629 (`server-http.cpp` 401/503 middleware answers), S630 (`server-common.cpp`
  `format_error_response` statuses), S631 (`tests/unit/test_router.py:20` asserts 200 before reading
  the field).
- **Do-nothing control:** `controls/c2-base.out`. **Blanket-refusal mutant:**
  `controls/c2-mutant-blanket.out` (`router_autoload` returns 2 on every answer: P1 and P2 fail,
  `mismatches=2`). **Pre-freeze correction:** the first draft expected P2 to read
  `router-model-invalid`; the base probe answered `MODEL_OK`/`router-unloaded-autoload`/0 and P2's
  expectation was set to that before freeze (`controls/c2-prefreeze-p2guess-*.out`).
- **Kill rules:** K1 counter or probe bytes change after the freeze commit without an amendment; K2
  `met=False` at M; K3 base green; K4 a positive cell (P1, P2) fails at M.
- **Regression control (not the predicate):** the round-99 counter against M
  (`tools/round99-autoload-states.py --rev <M>`) must stay `cells=8 mismatches=0`
  (`controls/c2-regression-r99.out`).
- **Disclosed limits.** (a) Stub-fed answers, not a live llama.cpp router or a real proxy. (b) A 200
  answer from a non-router intermediary that returns a router-shaped body is still read. (c) Only the
  `/props` read in `router_autoload()` changes; `/v1/models` statuses keep `classify()`'s rules. (d) The
  cells cover the nine statuses/bodies listed; other non-200 statuses follow the same `[ "$pcode" = 200 ]`
  line but are not each graded. (e) A slow 200 is still the round-99 timeout cell, not re-graded here.
