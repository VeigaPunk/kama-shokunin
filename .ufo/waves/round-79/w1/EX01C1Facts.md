# EX01C1Facts — independent re-derivation of the six round-78 facts (kama round 79, wave 1)

Seat: EX01C1Facts (executor, calibration). Item: build an independent derivation harness that
does NOT import the lane counter, re-derive the six facts frozen in `plans/round-79-claims.md`
§C1 from the record at the sealed revision `7a3cd98243b69fcbee0cc9e31878782bd8459320`, print
per-fact `EX01 <Fk> declared=<value> observed=<value> match=yes|no`, then cross-check the lane
counter's stale set. No edits under `tools/`; no commits (L1-only); no subagents.

## Harness

- Path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/EX01C1Facts/rederive.py`
- Independence: pure-stdlib script; reads only git objects at the sealed revision via
  `git show` / `git ls-tree` / `git rev-parse`; never imports, execs, or subprocesses
  `tools/round79-selfrecord-round78.py`.
- Derivation notes: the round-78 record is the `## Round 78` section of
  `git show <sealed>:SCORECARD.md`; the assigned axis pair is parsed from the record's own
  banner ("assigned axes are operability + calibration"); F1 observed = lowest of that pair in
  the first `## Axes` table; F2 observed = SOURCES row count (`| S<digits>` rows), filtered
  `corpus/knowledge/*.md` count (excluding `engine-sides`/`processes`), blob sha256-8 + newline
  counts of `SKILL.md`/`PROVINCE.md` at sealed; F3/F4 observed from
  `.ufo/waves/round-78/w1-{spec,results}.json` at sealed; F5 observed = the record's named
  `rev=22cce544…` resolved and compared to the sealed tip; F6 observed = scan of all 76 blobs
  under `.ufo/waves/round-78/` at sealed for `mismatches=1`.

## Receipts (absolute path — command — exit code)

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/EX01C1Facts/rederive.out` —
   `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/EX01C1Facts/rederive.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin` — **exit 1** (two stale facts; expected).
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/EX01C1Facts/counter-enum.out` —
   `python3 tools/round79-selfrecord-round78.py --repo . --enumerate` (cwd: `/home/vgpnk/Projects/shokunin/kama-shokunin`) — **exit 1**, line: `SELFRECORD_R78_ENUM claims=6 stale=2 corrected=0 | sealed=7a3cd98243b69fcbee0cc9e31878782bd8459320 tip=d6408a63f4ac4efd1d7161180aa62bf10f6f591a`.
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/EX01C1Facts/counter-facts.out` —
   `python3 tools/round79-selfrecord-round78.py --repo . --json` (cwd: `/home/vgpnk/Projects/shokunin/kama-shokunin`) — **exit 0**, frozen C1 line printed: `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0` at tip `d6408a63f4ac4efd1d7161180aa62bf10f6f591a`.

## Independent result (rederive.out, exit 1)

```
EX01 F1 declared=lowest-axis=calibration:7 observed=lowest-axis=calibration:7 match=yes
EX01 F2 declared=population=sources:292,knowledge:51,skill:a50f6f74/1736,province:6b8c604f/331 observed=population=sources:292,knowledge:51,skill:a50f6f74/1736,province:6b8c604f/331 match=yes
EX01 F3 declared=wave=seats:12,executor:3,scribe:3,scout:1,connector:1,reviewer:1,critic:2,mutation-tester:1,attack:4/12 observed=wave=seats:12,executor:3,scribe:3,scout:1,connector:1,reviewer:1,critic:2,mutation-tester:1,attack:4/12 match=yes
EX01 F4 declared=wave-dead=returned:3(EX01C1Selfrecord,SC02Lesson,SCT01Recon)/empty:9 observed=wave-dead=returned:3(EX01C1Selfrecord,SC02Lesson,SCT01Recon)/empty:9 match=yes
EX01 F5 declared=tip-accounting=rev:22cce544/is-tip:true observed=tip-accounting=rev:22cce544/is-tip:false match=no
EX01 F6 declared=c1-pre-correction-run=committed observed=c1-pre-correction-run=absent match=no
EX01 summary claims=6 mismatches=2 stale=F5,F6
```

F5 evidence: `rev=22cce544` resolves to `22cce544b23670984fa9e42bea673d603881aae7`, which
`git merge-base --is-ancestor` confirms is an ancestor of the sealed tip, not the tip.
F6 evidence: independent `git grep -l 'mismatches=1' <sealed> -- .ufo/waves/round-78/` exits 1
(no hits across the 76 blobs); the pre-correction run exists only as lesson prose.

## Stale-set cross-check vs the lane counter — AGREE, no finding

- EX01 stale set (match=no): **{F5, F6}**.
- Counter stale set (`counter-facts.out` JSON rows, `stale:true`): **{F5, F6}**.
- All six declared and all six observed value strings are byte-identical between the two
  independent derivations. No disagreement to file.
- The counter's `--enumerate` line reproduces the frozen pre-freeze receipt
  (`SELFRECORD_R78_ENUM claims=6 stale=2 corrected=0`, exit 1) at the current tip; in enumerate
  mode the exit reflects record staleness only (`ok = stale == 0`, corrections not counted), so
  exit 1 there is the expected pre-answer state, not a gate failure. The scored run at tip
  `d6408a63f4ac4efd1d7161180aa62bf10f6f591a` already prints the frozen C1 target
  `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0`, exit 0 — the two corrections
  (`corrected F5 … at=7a3cd98243b69fcbee0cc9e31878782bd8459320`, `corrected F6 … at=7a3cd982…`,
  both in `corpus/lessons/round-79.md` §Corrections, committed in `d6408a63`) carry the declared
  `old` values and their `new` values re-derive at the tip.

## Observations (non-blocking; no seat action taken)

- The counter's docstring "Facts" list still describes round-77-style F1 ("Scores hold" axes
  sentence) and F2 (capability rows), while its code implements §C1's F1 lowest-axis and F2
  population. Value strings on the real tree agree with my independent derivation for all six
  facts, so there is no calibration impact — documentation debt for the counter owner.
- The counter's `f6` computes the blob scan but hardcodes the observed state to `absent`; on the
  real tree the scan is empty (verified independently), so the emitted value string is correct
  either way.
- Lane tip moved during this seat: `f7442dea` (at seat start) → `d6408a63` (lesson, two
  corrections, S553, census entry, pre-correction receipt landed by sibling seats). This seat's
  derivation is sealed-revision-only and unaffected; receipts 2–3 above were run at `d6408a63`.

## Risks / blockers

- None for this item. Attack seats re-grading C1 later should use the scored (non-enumerate)
  counter mode at the then-tip; enumerate is the stale-fact census, not the claim gate.
- Scratch (`/fast/scratch/hyaku/kama-r79/EX01C1Facts/`) created empty per policy and deleted at
  seat end; all receipts live in the wave dir.
