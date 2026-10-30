# Draft — `LOG.md` entry text for round 64 (kama)

Seat: SB05LessonAndLog (leaf, advisory). Axis: calibration. Milestone: draft lesson and LOG.
Every line is a fact I re-read in the lane at `361c620c` or in the on-disk attempt-2 receipts; each carries a pointer.
14 lines, facts only, no claim-admission language. The landed entry (`LOG.md:2530-2537`) is the attempt-1 text and
still describes wave f as "42 seats validated, 21 spawned … stopped by the operator wrap-up with no reports";
attempt 2 dispatched 42 seats on 2026-10-30 07:29:38 (`.ufo/waves/round-64/f.ready.dispatched`), so that clause and
the results it points to need replacing — see the note under the entry.

---

## Round 64 — process-bound request plane (C1) and a claim registry that proves the work was done (C2); wave b settled, wave f attempt 2 in flight (2026-10-30)

- Base `0c1eff3cb9ac4c11402ab0124c35842f06a436fc`; freeze `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a`; AMENDMENT 1, 1a and 1b (instrument only; `tools/kama-completion-live.py` byte-identical to the freeze commit) in `.ufo/waves/round-64/controls/freeze.txt:115-223`.
- C1 operability 8→8 (measured, not verified): `tools/kama-completion-live.py` v3 (`listener_holders`, `listener_holders_pinned`) and `tools/round64-c1-counter.py` — 91 controls, 30 families, 8 evaluator plants (`freeze.txt:184-195`; `EXPECT_FAMILIES` sums to 91 at `23b3fdb1`). At `9549c0b9`: `tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 eval_selftest=8/8 errors=0 met=True` (`.ufo/waves/round-64/measured/attempt2/c1.out`).
- C2 calibration 7→7 (measured, not verified): `tools/round64-c2-counter.py`, `registry/capability-claims-r64.tsv`, `registry/capability-regress-r64.tsv`, the reconciler `closure_ptr` conjunct and the `tools/shortcut-tally.py` rounds 56–63 reader. At `23b3fdb1`: `covered=12/12 pinned=13/13 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 tally_disclosed=8/8 controls_rejected=120/120 errors=0 met=True` (`.ufo/waves/round-64/controls/c2-prewave-tip.txt:14`).
- Red-before controls: the amended counter at the base tip prints `tool_present=1 live_ok=0/1 … eval_selftest=0/8 errors=1 met=False` (`.ufo/waves/round-64/controls/c1-base-final-counter.txt:2`); six mutants of the amended counter, five killed with the named control, `gone_always` survived as a near-equivalent of the port-closed observation (`.ufo/waves/round-64/controls/c1-mutants-a1.txt`).
- Wave b: 42 seats — mutation-tester 13, executor 10, scout 6, critic 4, reviewer 3, scribe 3, connector 2, sentinel 1 — all 42 returned output with `note: null`, so no dead seat is inferable (`.ufo/waves/round-64/b/b-results.json`).
- Wave b built the C2 instrument (X01), the 12-row regression table (X02–X05), the `closure_ptr` conjunct (X06), the tally reader (X07), the ledger scans (X09) and the idle-outcome study (X10), and found 10 survivor classes against the freeze-commit C1 counter plus 12 code defects (`RV02CounterCode.md` D1–D12) (`.ufo/reports/round-64/kama.md:13`).
- AMENDMENT 1/1a/1b is a rule change made **after** wave-b seats scored the freeze instrument and is disclosed as such; it names 21 of the 42 wave-b seats (20 by prefix, plus X03 inside the range "X02-X05"), and the survivors of the other 21 reach the instrument only through its generic clauses (`.ufo/waves/round-64/controls/freeze.txt:119-129, 175-179, 184-217`).
- Limits carried, not fixed: a non-dumpable own-uid helper that existed before the tool; writes through `/proc/<pid>/mem`; a holder that exists only after the counter's release; the blanket `/usr/lib` exemption in `bind_maps`; initial-environment-only visibility (`.ufo/waves/round-64/controls/freeze.txt:175-180`).
- Sources: S529–S536 added — 6 `queued`, 2 rejected; `corpus/SOURCES.md` 268 → 276 rows; `sources-census.sh validate kama` exit 0 at start and end (`.ufo/waves/round-64/census/start.out`, `end.out`). No knowledge entry admitted: `corpus/knowledge/process-bound-listener.md` does not exist at the tip (the wave-b draft is `.ufo/waves/round-64/b/out/SB01Knowledge/process-bound-listener.md`).
- QUALITY KQ107–KQ115 added (`corpus/QUALITY.md:529-537`); considerthese `2026-10-24.md:29` landed as KQ113 with the checker at `.ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.py` (27/27 quotes OK, `.ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.out`); the checker is not in `tools/`.
- Wave f attempt 2: 42 seats dispatched 2026-10-30 07:29:38 (`.ufo/waves/round-64/f.ready.dispatched`); seat reports and the attempt-2 measured receipts exist (`.ufo/waves/round-64/f/`, `.ufo/waves/round-64/measured/attempt2/`) but the wave has no results file, so no wave-f finding is landed by this entry.
- Support at `9549c0b9`: `digest-ledger` `unknown=0`, `hexrun-census` `unknown=0` (`.ufo/waves/round-64/measured/attempt2/digest-at-9549c0b9.out`, `hexrun-at-9549c0b9.out`); reconciler `closure_ptr=1 mismatches=0 maxN=64 met=True` (`.ufo/waves/round-64/measured/attempt2/recon-at-9549c0b9.out`).
- No score change, capability admission or round admission is claimed, and non-author closure is pending (`SCORECARD.md:6` "Latest measured round: 64 (honest stop …); non-author closure pending at this commit"; `SCORECARD.md:3385`).

---

### Notes for the L1 on this draft

1. **The wave-f clause must be rewritten.** `LOG.md:2535` says wave f was "stopped by the operator wrap-up with no reports".
   That was attempt 1 (its partial files are under `.ufo/waves/round-64/f/out-attempt1/`). Attempt 2 dispatched 42 seats
   on 2026-10-30 07:29:38 and seat reports are landing under `.ufo/waves/round-64/f/`; there is no
   `.ufo/waves/round-64/f/f-results.json` yet, so the entry above says "in flight" and lands no wave-f finding.
2. **Attempt-2 receipts are untracked.** `.ufo/waves/round-64/measured/attempt2/` and the new `.ufo/waves/round-64/f/`
   reports are untracked working-tree files (`git status --porcelain`), so the pointers above resolve on disk but not in
   history. `git add -N .` must not be used to stage them — see the M-E row of the lesson draft.
3. **The landed lesson has a structural defect.** Rows 11 and 12 sit after the `## Wave results` heading
   (`corpus/lessons/round-64.md:42, 47, 48`), so they are not inside the Mistakes list.
4. **One landed statement is now false.** `corpus/lessons/round-64.md:44` says `MT06MapsLib` "wrote no report file,
   `ls b/MT06MapsLib.md` → no such file"; the file exists at the tip (landed byte-exact from the fleet root,
   `361c620c`) and is 187 lines. The sentence describes attempt 1 and should be corrected or dated.
5. **The freeze's own control count is internally inconsistent.** The amended C1 sentence inside `freeze.txt:156, 159`
   still reads "all 89 targeted controls" / "sum 89" while AMENDMENT 1a (`:192`) states the amended sentence reads
   "91 targeted controls" and `EXPECT_FAMILIES` sums to 91 — which is what the counter at `23b3fdb1` actually has
   (30 families, sum 91). One of the two texts should be corrected before closure.
6. **The freeze's C1 sentence is not byte-enforced.** `freeze.txt:21` says "the byte-pinned tools/kama-completion-live.py"
   and `freeze.txt:147` says the counter works "from procfs and its own code alone, loading nothing from the tip",
   but the counter at `23b3fdb1` carries no digest of the tool (its only sha256 constants are `MODEL_SHA` and
   `SERVER_SHA`, `tools/round64-c1-counter.py:56-57`) and still reads the tool text and both forge patches from the
   tip blob (`blob(repo, tip, 'tools/kama-completion-live.py')`, `blob(repo, tip,
   '.ufo/waves/round-64/controls/forge-A-realchild.patch')`). Wave-b CR01PredicateCode finding A ("No digest of
   `tools/kama-completion-live.py` appears in the counter") and finding I (forge patches are tip text) are not named
   in any amendment and are not closed by it. This is a claim-wording defect, not a counter defect — the instrument's
   own binding checks are unaffected, and AMENDMENT 1 did make the forge/relabel builders structural and the patch
   application fuzz-free (`freeze.txt:140-142`).
