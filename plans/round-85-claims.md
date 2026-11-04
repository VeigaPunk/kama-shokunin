# Round 85 — frozen claims

Base revision `4401b72f64a2202fd30f26479c463e9b9d9cabad` (master, clean and pushed at start). Freeze date 2026-11-04. Two distinct, causally separable claims: calibration and operability. Assigned axes operability8/calibration7; calibration is lowest assigned, below saturation8; no stagnation waiver or score increase. L1 KamaR85 holds planner seat.

## C1 — calibration: actual live authority cells agree with terminal evidence

Predicate: `python3 .ufo/waves/round-85/count.py c1 --repo . --rev master --work /fast/scratch/hyaku/kama-r85/L1` prints `AUTHORITY_CELLS facts=2 mismatches=0 gate=1 closure=1 newest=round-84-verifier-spotcheck.md` and exits0.

Frozen population exactly two live SCORECARD cells, not a whole-record census:
1. First **Current authority** paragraph: replace stale under-terminal-measurement wording with the actual terminal `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0` and full measured revision `b53cd336e0cb204cf71246e95fdf7494babeafa4`, receipt and command. This is not a run at the round84 publication tip and not retrospective admission.
2. Calibration row inside first `## Axes`: latest outside closure names round84, not round83. Preserve round83's rejected history and round84's rejected-honest-stop disposition.

Counter reads committed cells, not arbitrary witness-token occurrence. CommonMark ATX 0–3-space heading exclusion grounds sourced claim C1; open spec this round and cite new SOURCES id. Demonstrate controls placing correct witnesses only in unrelated text and 0/1/2/3-space correction blocks cannot turn stale authority cells green; genuine repaired-cell positive control passes. Four-space code is not an ATX heading. Counter and predicate freeze before seats score; no later weakening.

Before/no-work control: measured/before/c1.out at base prints facts2/mismatches2/gate0/closure0 exit1. Work edits only live authority cells in place (round42 convention); dated sections receive appended corrections. Kill: either mismatch, a falsely passing stale-cell control, or missing witness source means C1 fails.

## C2 — operability: delivered subject-binding selftest catches three surviving mutants

Predicate: `python3 .ufo/waves/round-85/count.py c2 --repo . --rev master --work /fast/scratch/hyaku/kama-r85/L1` prints `DEBT_MUTANTS mutants=3 killed=3 escaped=0 invalid=0` and exits0; pristine `python3 tools/round81-append-debt.py --selftest` exits0.

Exact frozen mutations are in count.py: M2 comparison deletion!=accepting instead of subject; M3 != replaced with <; M4 removes only continue after note-wrong-deletion-round. Each mutant must produce a completed semantic selftest failure on a named note-* owning arm, exit1 with a valid summary; crashes/errors/site-missing earn no kill. Add equality (correct deletion==subject with accepting>deletion), direction (deletion>subject), and exact-summary coverage controls. Correct code retains existing grade behavior; do not change grade rules to kill mutants. Existing wrong-subject and unresolvable arms remain. Real-register runs/round84 fixture are reverified and reported, but numeric claim targets mutation detection, not eliminating all historical audit debt. No new gate-arm target.

Before/no-work control: measured/before/c2.out against actual delivered base file has M2/M3/M4 each exit0, pass31/fail0: killed0/escaped3/invalid0 exit1. Spec-only round84 study is historical, not substituted for this delivered-file measurement. Kill: any survivor, invalid execution or pristine regression fails C2.

## Frontier and routed corrections

Run start census validate exit0 (pre-existing W01/W04 warnings),315 rows. Reopen CommonMark ATX spec and rejected b7200 examples/server README this round; schema-valid scratch-gated new rows only. Add missing rejected row R84V2. R84V1 disclosure miss remains an honest miss: no fabricated disclosure. R84V3 source-origin escape remains open; hash integrity proves no remote acquisition. R84V4 becomes C1. R84V5 receives append-only citation/provenance erratum in round85 lesson, never rewrite frozen round84 plan. Mine backing-token/heading escapes and reference-drift into Mistakes and criterion. Assimilation examined; none permitted if no fitting theme.

## Shape and evidence

ONE v1 wave w1,10 seats:3 executor,1 scribe,1 scout,1 connector,1 reviewer,1 critic,1 mutation-tester,1 sentinel. Attack4/10, connector1. Each writes only unique out dir; L1 sole integrator, no seat production edits/commits. Scratch /fast/scratch/hyaku/kama-r85/<seat>. Inline validated dispatch ready JSON names KamaR85; never call task. Wait WAVE-DONE before report. Commit controls/counter/plan before data; final measurements on committed master, publication commits separate. Scores unchanged; trends judged by actual work, rows alone not expansion. Both claims must verify, no harm; otherwise honest stop.
