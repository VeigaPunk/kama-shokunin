# X6Rerun — independent C2 measurement (round 52, lane kama)

**Verdict: C2 reproduces independently, exactly.** On a fresh `--shared` clone of the lane, the frozen C2 counter at the build `5dacf2c7` is `met=True` (exit 0) and at the base `9ff76b1f` is `met=False` (exit 1, `corr_lost=151`); both receipts are body-identical to `measured/c2-build.out` and `controls/base.c2.out`. `append-only-audit.py --to 5dacf2c7` exits 0 with `unrestored 0 partial 0 regressed 0 bad_disclosures 0 bad_declarations 0`. My own independent checker (not importing the counter or the tool) finds 155/155 A-corr lines the base ledger disclosed present verbatim in the tip's restored sections, and the tip ledger holds exactly the 10 rows no verbatim re-append can repair. The one numeric gap between the two graders (counter 151 vs ledger 155) is the counter's *documented* exempt simplification on two gutted `## Planned` sections; it undercounts, so it cannot mask a loss. **No defect found.**

## Calibration axes exercised
- Independent instrument: own clone (`git clone --shared`, toplevel asserted), own scratch, no hand-edited counters.
- Independent re-derivation of the C2 mechanism (a separate 100-line checker, `x6_verify_restore.py`) rather than trusting the counter's own recomputation.
- Reproducibility against the L1's build battery and against the frozen base control, byte-for-byte on the body.

## Commands and receipts (all runs: cwd = my scratch, `TMPDIR` = my scratch, then scratch deleted)

```
S=/fast/scratch/hyaku/kama-r52/X6Rerun
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane     # toplevel = $S/lane
# 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 and 9ff76b1f763512be2f554cbbfd0b2213b63b0847 both cat-file -t commit

python3 <lane>/tools/round52-append-restore-check.py --repo $S/lane \
  --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S/c2build \
  --out .ufo/waves/round-52/w1/out/X6Rerun/c2-build.out
exit=0
tip=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
detail: lane: tool v6 threshold 1 exit 0 events 109 disclosed_lines 10; own graded 5868; own unheld A-corr 0, A/A-row 10; ledger lines 10

python3 <lane>/tools/round52-append-restore-check.py --repo $S/lane \
  --tip 9ff76b1f763512be2f554cbbfd0b2213b63b0847 --scratch $S/c2base \
  --out .ufo/waves/round-52/w1/out/X6Rerun/c2-base.out
exit=1
fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False
detail: lane: tool v6 threshold 1 exit 0 events 107 disclosed_lines 165; own graded 5867; own unheld A-corr 151, A/A-row 10; ledger lines 165
detail: lane: unheld lines in A-corr files: {'LOG.md': 22, 'corpus/README.md': 20, 'SCORECARD.md': 19, ...}

python3 <lane>/tools/append-only-audit.py --repo $S/lane --to 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
exit=0
summary commits=350 files=99 events=109 restored=67 partial=0 unrestored=0 ungraded=37 disclosed=5 permitted_lines=58 disclosed_lines=10 bad_disclosures=0 ungraded_lines=210 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```

| run | receipt (mine) | reference | comparison |
|---|---|---|---|
| C2 @ build, exit 0 | `c2-build.out` | `measured/c2-build.out` | identical after stripping the L1 harness's `$ python3 …` echo line and its `exit=0` trailer |
| C2 @ base, exit 1 | `c2-base.out` | `controls/base.c2.out` | identical, same stripping |
| audit @ build, exit 0 | `aoa-build.run.log` | `measured/aoa-build.out:111` | summary line identical (event rows identical too; the L1 file is the same event listing with its own exit trailer) |

Both `--out` receipts were written by the counter itself (parent dirs created); my `.run.log` copies are the raw stdout of the same invocations, and `exit-codes.txt` records the three exit codes.

## Independent re-derivation of the restore claim (`x6_verify_restore.py`, exit 0)

Reads only `git show <rev>:<path>`; contains no lane code.

```
base ledger rows=165 a-corr rows=155 other rows=10 a-corr lines=155
tip ledger rows=10 tip ledger a-corr rows=0
restored_lines_found=155 missing=0 outside_heading=0
verdict=ok
```

Mechanism, checked structurally at the build commit:
- 18 files carry an exact `## Restored lines (round 52)` heading (`###` in `SCORECARD.md`, at line 2929 of 2994). Twenty files match the *phrase*; `corpus/lessons/round-52.md` and `SKILL.md` only mention it in prose/registry text, which is why a naive grep count is 20.
- Tip ledger: 10 rows, by file `corpus/SOURCES.md` 7 and `registry/report-landing-errata.tsv` 3 — the A/A-row rows the wave description names — and **zero** A-corr rows.
- All 155 restored lines sit at or after the heading (`outside_heading=0`), so every re-append is inside the declared `## Restored lines (round 52)` region rather than smeared into the body.
- Counter integrity: the counter materialises the audit tool from the tip's own blob (`tools/round52-append-restore-check.py:515`, `git show {tip}:tools/append-only-audit.py`), so the fixtures and the lane leg run the frozen tip bytes. Those bytes are `sha256 343e8c18cab1…c97d459`, byte-equal to the lane's on-disk `tools/append-only-audit.py`, i.e. no drift between the copy I read and the copy the counter ran.

## The 151-vs-155 delta is the documented exempt simplification, not a hole

Base receipts disagree by 4 lines (counter `corr_lost=151`, ledger `disclosed` A-corr lines 155). Per-file, the delta is entirely `SCORECARD.md`: counter 19, ledger 23; every other file matches exactly (LOG 22, README 20, r26 17, r27 13, r38 11, r16 11, r25 10, r28 6, r19 6, r42 4, r18 4, r1 2, QUALITY 2, r43/r40/r4-recensus/r32-verifier 1 each).

Diagnostic (one print added to a **scratch copy** of the frozen counter; patch and output in `x6-scorcard-delta-diagnostic.out`): the counter's own unheld is 0 at two events where the ledger discloses 2 lines each —

- `ef76777e5fbd` SCORECARD.md own_unheld 0, ledger 2 (`b28cbdd7…`, `bb901994…`)
- `42ea1204aef3` SCORECARD.md own_unheld 0, ledger 2 (`bf586982…`, `ed5ff78e…`)

At the deleting commits' parents those four lines live under `## Planned` (lines 53 and 67 / 53 and 66), an exempt title in the file's own region — `registry/append-only-contract.tsv:3`: `exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`. The section was gutted by the same commit (`## Planned` 17 → 3 lines at `ef76777e`, 16 → 3 at `42ea1204`), so the tip's v6 tool grades them (`ef76777e` SCORECARD deleted=18 graded=15; `42ea1204` deleted=14 graded=14), while the counter's *simplified* exempt rule — "a deleted line whose parent section is an exempt title is ungraded", stated in its docstring as a preregistered limit — ungrades them. That is exactly the deferral the docstring declares. Direction matters: the counter can only undercount, so `corr_lost=0` at the build cannot hide a loss, and the round-52 restoration re-appended those four lines anyway (my 155/155 check includes them; tip `SCORECARD.md:2979-2987`).

## Files changed
None in the lane, none in the fleet repo. The lane was read-only throughout (all `git` calls were `show`/`rev-parse`/`cat-file` in my own clone); the only writes are the nine files in this out directory.

## Risks / notes
- No `llama-server` was started by me; the C2 counter starts no server. `pgrep -af llama-server` matched a `sha256sum` invocation whose argv merely lists `./llama-server` — unrelated, and nothing was left behind by this seat.
- My clone's HEAD is the lane's current `34d8260051bb`; both frozen commits resolve there, and no lane mutation was performed.
- Tool installs: none needed (python3 sufficient); no pacman was run.
- Out-of-scope observation for the L1 (not a defect, no action requested): the base counter's `own graded 5867` vs build `5868` moves by exactly one graded line, the build's `corpus/lessons/round-1.md` re-append event at `5dacf2c7` — consistent with the audit's `events 107 → 109`.

## Absolute paths written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/c2-build.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/c2-base.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/c2-build.run.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/c2-base.run.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/aoa-build.run.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/exit-codes.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/independent-restore-check.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/x6_verify_restore.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X6Rerun/x6-scorcard-delta-diagnostic.out
