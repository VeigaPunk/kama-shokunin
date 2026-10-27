# Sc1Lesson — round-55 lesson review (`corpus/lessons/round-55.md`)

**Verdict: NOT CONFORMANT — the Gate admits/rejects and the S510 old→new record pass, but the
considerthese disposition table is materially false for three of four proposals (KQ97), the
"after" census receipt the lesson asserts does not exist, the C2 claim states the opposite BASE
from the frozen preregistration, and the Mistakes fix claims every battery receipt names a
killed leg when three of seven print `met=True`.**

Reviewed file: `corpus/lessons/round-55.md` at lane tip `9c60eae6f7ed84f7da93d219a406aadc30958c6c`
(base `3a600d2f729828419aaea34cc402c8b0d20fb720`), against `CORPUS.md` (fleet root), `corpus/QUALITY.md`
(KQ6, KQ12, KQ20, KQ22, KQ26, KQ97), kaika `mistakes.md` §5 (class vocabulary) and
`considerthese/2026-10-26.md`. All commands read-only; no lane file edited; the proposed wording is a
unified diff in the out dir (`round-55-lesson-fixes.diff`, 187 lines; full proposed text in
`round-55.proposed.md`).

## Findings

### F1 — BLOCKING (KQ97): three of four considerthese dispositions are false, and the fourth is a deferral without evidence — lesson:103-113

| Proposal | Lesson says | Evidence |
|---|---|---|
| 2 (track dispositions) | "landed round 54 as `corpus/QUALITY.md` KQ97" (105-106) | KQ97 landed in **round 53**: `git log -S 'KQ97' -- corpus/QUALITY.md` → only `e81d90e6 2026-10-27 round-53: integrate …`; `git blame -L 477,477 corpus/QUALITY.md` → `e81d90e6`; `corpus/lessons/round-53.md:37` already records the mining. |
| 1 (flag append-only deletions) | "pending; no lane instrument exists for it; the daily reflection owns it" (107-108) | Taken up **round 46**: `corpus/lessons/round-46.md:11` is titled "(capability acquisition, considerthese/2026-10-26.md proposal 1)" and lands `tools/append-only-audit.py`; `git log -1 4a2a4d55` subject names proposal 1; the tool audits the five files the proposal names (`tools/append-only-audit.py:817`); round 51 v6 grades every deletion (`:4-8`). |
| 3 (running count of shortcut-meeting counters) | "partially served by this round's battery receipts … a standing tally is still pending" (109-111) | Taken up **round 47** (seat X9Tally, `corpus/lessons/round-47.md:37`) and promoted to lane tool `tools/shortcut-tally.py` v2 in **round 48** (docstring names the proposal); its standing run is `.ufo/waves/round-48/measured/tally.out` (committed `1541a0dd`). |
| 4 (daily pin-gap line) | "pending; `tools/pin-watch.py` exists since round 41; the daily reflection owns it" (112-113) | `tools/pin-watch.py` exists (S475/S476, `corpus/lessons/round-41.md:18`), but "the daily reflection owns it" is a deferral asserted without a deferral record; KQ97 says pending work is not labelled deferred. |

KQ97 also requires the applicable outside closure verdict "when one exists": for proposal 1 it
does — `corpus/lessons/round-46-verifier-spotcheck.md:108` `| calibration | improved | C2 re-measured
on the lane leg |`. The table carries no verdict for any row.

**Proposed fix:** the replacement block in the diff (four bullets, each with round + commit + file:line,
plus the r46 closure verdict and explicit "still pending / no verdict yet" states).

### F2 — BLOCKING (landing, KQ22-adjacent): the lesson asserts a census "after" receipt that does not exist — lesson:94-96, 101

- `.ufo/waves/round-55/census/` holds `start.out` only; there is no `end.out`.
- `start.out` last line `census_start_exit=1`, with `kama E11 S510 missing used-by corpus/lessons/round-54.md` — the before state the lesson reports.
- Read-only re-run on 2026-10-27: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **exit 0**, 99 `kama` lines, no `E` rows (copied as `census-now.out`). The after state is green today, but the named artifact (mistakes row 3, line 95: "ends with census exit 0 (receipt …)") is not the observed evidence; the round-end receipt must still be written by the L1.

**Proposed fix:** state the after receipt as required-at-round-end and name its current absence (diff hunk at lesson:94-101).

### F3 — BLOCKING (conflicts with the frozen preregistration): Claims C2 reverses the BASE — lesson:20-25

Lesson: "BASE re-frozen to the round-54 tip" (21). Frozen record:
`preregistration.json` `claims.C2.counter_base = 0b75a84c56e024cac1662e8ff81802f249acb410` (round-53 tip);
`controls.base_do_nothing` measures tip `3a600d2f…`; `controls/base.c2.out:1` `tip=3a600d2f…`;
the lesson's own Mistakes row (78-86) says "C2's BASE reverted to the round-53 tip (`0b75a84c`)";
the seat spec (`w1/spec.json:9`) says "BASE deliberately stays at the round-53 tip 0b75a84c".
The parenthetical conflates the counter's internal BASE (drop horizon) with the `--tip` tree it is run on.

**Proposed fix:** diff hunk separating `counter BASE = 0b75a84c` (horizon) from control tree
`3a600d2f` and measured tree `9c60eae6`.

### F4 — MAJOR: the Mistakes fix claims every battery mutant names a killed leg; the receipts say otherwise — lesson:72-76

`.ufo/waves/round-55/c1/battery/`, line 2 of each receipt:

```
control.out            met=True
m-ldpreload.out        envnames=0/3 … met=False
m-text-flip.out        bind=0 code=0 … met=False
m-member-flip.out      rehash=3 met=False
m-ldaudit-foreign.out  met=True
m-ldaudit-writable.out met=True
m-extra-in-tree.out    met=True
```

`run-battery.py:36-40` declares `m-ldaudit-foreign` as `kind="vector"` (expects `met=True`), and
`:120-145` grades vector mutants as ok when `rc==0 and met`. The `MUTANTS` table holds only
`m-ldpreload, m-text-flip, m-ldaudit-foreign, m-member-flip`; `m-ldaudit-writable.out` (10:30) and
`m-extra-in-tree.out` (10:37) predate the runner (10:42) and are not reproducible from it.
The preregistration target says "each named mutant receipt prints `met=False` (exit 1) with its named
leg failing" and names `m-ldaudit-writable` in the code leg; the delivered code-leg kill is
`m-text-flip`. **Conflict left verbatim for the canonical judge** (I did not adjudicate it):

> prereg: `"mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]` … `"target": "… kill battery: each named mutant receipt prints met=False (exit 1) with its named leg failing …"`
> receipts: `m-ldaudit-writable.out` `met=True`; `m-ldaudit-foreign.out` `met=True`; code-leg kill delivered as `m-text-flip.out` `met=False`.

**Proposed fix:** the honest battery paragraph in the diff (three live kills named with their legs, one
declared vector analysis, two extra `met=True` receipts, and the explicit KQ26 disclosure that the
preregistration target is not met literally).

### F5 — MINOR (number-drift): the quote is 18 words, not 23 — lesson:39

`len(quote.split()) == 18` for the S511 sentence; counting the `<n>` placeholders as separate tokens
gives 20, never 23. The quote itself is exact modulo one typographic normalisation: the source renders
`process’s` (U+2019) where the lesson writes `process's`; the snapshot is 830,605 bytes as claimed
(lesson:36). **Fix:** "(18 words — `len(quote.split())`; … 830,605 bytes)".

### F6 — MINOR (reference-drift): the proc(5) rejection cites the wrong held ground and the wrong bar — lesson:47-50

- `S050` is RFC 4291 IPv6 addressing (`corpus/SOURCES.md` S050; `corpus/lessons/round-18.md:45`), not procfs decoding; `S048` is the kernel tcp6 printer.
- The lane's actual `/proc/<pid>/maps` ground is `S496` `proc_pid_maps(5)`, tier A (`corpus/SOURCES.md:249`), with `S506` (proc_pid_mem) and `S508` (proc_pid_map_files).
- `KQ6`'s reject column is about documentation claims written as runtime facts; it does not bar row growth. The applicable bars are KQ12's "row or field growth is called new knowledge without a new sourced distinction" and `CORPUS.md` SOURCES rule 4 ("Expansion is knowledge, not rows").

**Fix:** diff hunk citing S496/S506/S508, the round-18 procfs reading (S048/S049), and KQ12 + rule 4.

### F7 — MINOR (attribution): "which cites S510 in the C2 hermetic-git record" is not true of this lesson — lesson:55-56

S510 appears in the lesson only at lines 7, 52-56, 89 and 100; the C2 claim (20-25) cites no source.
The citing record is `preregistration.json` `claims.C2.sourced` and both counters' `clean_env` strips.
**Fix:** the corrected justification in the diff (which also records the verification that column 11 is
the only changed cell).

### F8 — MINOR (KQ26): the retrospective label omits what the reconstruction cannot prove — lesson:8-10, 79-80

The intro labels the creation round (55) and the absence of a round-54 lesson, but KQ26 also requires
saying what a reconstruction cannot prove. The concrete instance: Mistakes row 2 quotes a pre-freeze
run (`fixture=1 lane=1 scenarios=15/15 dropped=0 met=True`, line 80) for which **no receipt exists**
anywhere under `.ufo/waves/round-55/` — the only base-tip receipts (`w1/out/X2C2Rerun/C-…`,
`E-…`) print `dropped=1 met=False` with the current counter, and the run cannot be replayed because the
frozen counter now carries BASE `0b75a84c`. **Fix:** the two diff hunks (intro limit; row-2 receipt
disclosure).

### F9 — MINOR (captured-by vocabulary): row 2's captured-by cites a seat-spec rule, not a standing criterion — lesson:82-84

`CORPUS.md` requires "the `QUALITY.md` criterion or protocol rule that should have caught it, or `none`".
The round prompt's §9 claim-sizing rule is neither; keep it as prose and mark the field `none standing`.
**Fix:** diff hunk in row 2.

### F10 — NOTE (thin provenance): exit codes are not in the receipts — lesson:18-19, 24-25

`controls/*.out` and `measured/*.out` carry the `met=` line and `detail:` lines only; no `exit=` field.
The exit mapping is in code: `tools/round54-replay-code-audit.py:966` (docstring:97 "Exit 0 met, 1 not met,
2 could not evaluate") and `tools/round54-cited-path-check.py:856`. **Fix:** cite the code lines (diff).

## Checks that pass

- **Gate completeness for the new row (SOURCES rule 1):** S511 records title+URL (lesson:33), access date
  `2026-10-27` (35), a located quote (37-39) that is faithful and ≤25 words, and the tier/status match the
  row (`corpus/SOURCES.md:264`, tier B, mined, used-by `corpus/lessons/round-55.md` which exists).
- **Reject recorded with reason and flip:** lesson:44-51 (reason and flip present; only the citations/bar need F6).
- **S510 old→new logged:** lesson:52-56. Verified old value at base: `git show 3a600d2f:corpus/SOURCES.md`
  S510 used-by = `corpus/lessons/round-54.md`; new = `corpus/lessons/round-55.md`; the old file does not exist
  (`ls corpus/lessons/round-54.md` → absent). Column diff (11 columns) changes column 11 only — the in-place
  change KQ22 permits. Round diff: `corpus/SOURCES.md | 3 ++-`, 2 insertions (S511 row) + 1 deletion (S510 row).
- **Mistakes row shape:** all three rows carry class · evidence · captured-by · fix; classes `vacuous`,
  `vacuous`, `landing` are all in the kaika `mistakes.md` §5 vocabulary.
- **Census before receipt:** exists (`.ufo/waves/round-55/census/start.out`), `census_start_exit=1`,
  `E11 S510 …` plus standing W01/W04 — exactly what lesson:100 reports.
- **Claims C1:** base control receipt `controls/base.c1.out` (tip 3a600d2f, `newrow=0 met=False`) and build
  `measured/c1-build.out` (tip 9c60eae6, `met=True`, `newrow=1`, `['| S511 |']`) match lesson:14-19.

## Out of scope / not performed

- No lane, fleet, counts or measured files were written; the battery, counter and preregistration were not
  re-run (another seat owns replay); I ran only the read-only census to date the after state.
- I did not adjudicate the F4 prereg-vs-receipt conflict, score the claims, or grade the wave; the conflict is
  quoted for the canonical judge.
- KQ22's round-end `tools/sources-append-only.py` receipt and the round-55 LOG entry are outside this
  lesson's scope; no `append-only` receipt exists under `.ufo/waves/round-55/` at this tip.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc1Lesson.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc1Lesson/round-55-lesson-fixes.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc1Lesson/round-55.proposed.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc1Lesson/evidence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc1Lesson/census-now.out`
