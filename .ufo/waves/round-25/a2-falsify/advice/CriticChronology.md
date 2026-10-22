Verdict: defect found. Most ordering claims check out: commit order, the amendment 3 and 4 stamps against their commits, both counter re-scores, the C1 docstring-only drift, and the not-blind read disclosure. Six defects remain after `errata-attempt-2.json`. Two of them are errata corrections that are themselves wrong.

Seat: KamaR25a2.CriticChronology (critic, wave 2, read-only). No llama-server was started and no port was opened. No tool was installed or upgraded. In the lane I ran only read-only git (`log`, `show`, `diff`, `status --no-optional-locks`, `reflog`, `check-ignore`, `ls-tree`) and no jj command. Git-writing work ran only in my own clone, `/fast/scratch/hyaku/kama-r25a2w2/CriticChronology/clone` at fa3b62ae6475d111eb466d79af616aeebb08bbb9, plus a worktree `wt5388` at 5388b7cf. I read the operator session logs under `~/.omp/agent/sessions/` read-only and wrote nothing there. All times are UTC; lane times print as -0300, and I added 3 hours. The full timeline is in `out/CriticChronology/timeline.md`.

## Defects

### D1 (high): one attempt-1 seat kept running for about 7 minutes after the stand-down. The errata understates this.

The errata (correction 1) says that "30 cancelled mid-run" "is not verified from the folder". The orchestrator session settles it, and it is partly false.
- 08:30:46.216Z: Main tells KamaR25 "stand down now ... stop all work".
- 08:31:14.578Z: KamaR25 returns "I cancelled the 30 seats still running, by id, through proc://…/kill". The source of the "30 cancelled" claim is this return from the attempt-1 L1, not an orchestrator note.
- Per-seat sessions (`out/CriticChronology/attempt1-seat-session-ends.tsv`): 30 sessions show an aborted assistant message at 08:30:52.46-08:30:52.55Z. Twenty-nine of them start no tool call after that.
- `KamaR25.ExecCapacityTool.jsonl` is the exception. It started 13 tool calls between 08:34:45.143Z (write of `kama-context-capacity.py`; the folder's birth time is 08:34:45.14Z) and 08:37:47.849Z. These include a run at 08:37:26.348Z that launched 8 live llama-server children on ports 47400-47407 (`run-exit=0`). The session was disposed at 08:37:52.479Z.
- The errata gives the ExecCapacityTool writes as "between 08:36:56Z and 08:37:30Z". The first write was at 08:34:45Z. 08:36:56Z is only the tool file's last edit.

Smallest correction (errata to the errata): "Stand-down order delivered 08:30:46Z. Twenty-nine of the 30 running seats aborted at 08:30:52Z. ExecCapacityTool did not stop: it wrote files from 08:34:45Z, ran 8 live llama-server cells (ports 47400-47407) at 08:37:26-08:37:30Z, and was disposed at 08:37:52Z. Source: KamaR25's return at 08:31:14Z and the seat session logs." Impacted axes: provenance, and fixture-scope honesty (live serving after the stop order).

### D2 (medium): the errata's write window for CriticLearningBar is wrong, and E09 is left out of the X1 provenance.

Errata correction 2 says "CriticLearningBar (advice written 08:28:54Z to 08:29:23Z ...)".
- `build/advice/CriticLearningBar.md` was written once: birth = mtime = 08:29:23.24Z. 08:28:54.91Z is the time of `CriticC2Sizing.md` (also a single write).
- CriticLearningBar's X1 and X2 values first appear in `out/CriticLearningBar/cell-predictions.out` at 08:28:05.77Z. `CriticC2Sizing/source-model.out` holds only K1-K8, not X cells.
- `out/ExecEdgeCells/raw/E09-np2-noc/server.log` was written at 08:27:36Z, 29 s before that prediction file. E09 (`-np 2`, no `-c`) logs `n_ctx_slot = 2048, kv_unified = 'false'`, which is the fit-raising behavior X1 tests. The errata names only E17-E19 (bearing on L). It does not name E09 as an earlier observation of the X1 mechanism.
- I found no evidence that CriticLearningBar read E09: its advice does not cite it. Whether it was read is [INFERENCE: unknown].

Smallest correction: replace "08:28:54Z to 08:29:23Z" with "predictions 08:28:05Z, advice 08:29:23Z". Add: "Edge cell E09, already on disk at 08:27:36Z, showed the X1 mechanism before the X1 prediction was computed. The X1 prediction is source-derived but not provably blind." The entry's sentence at `corpus/knowledge/context-capacity.md:33-38` ("X and L predictions ... were written from source before the attempt-2 runs") needs the same qualifier. Impacted axes: provenance, learning-claim discernment.

### D3 (medium): the repair design and the 27 -> 28 change were registered after they had been measured. The errata says only "before amendment 2 was committed".

Errata correction 9 says "The C1 re-anchor edit was made in the working copy before amendment 2 was committed". From the author session:
- 09:22:39.94Z: before count `registered 27 stale 2` (amendment 2 says "about 09:24Z").
- 09:25:25-09:25:55Z: edits to `tests/report-audit/isolation-mutants.py` (mtime 09:25:55.54Z).
- 09:26:00.48Z: after count `registered 28 stale 0 []` printed.
- 09:28:09.15Z: amendment 2 written, with `repair_design` and "Denominator 27 -> 28".

So amendment 2's C1 repair design describes a change whose result had already been observed 2 minutes earlier. The stale-0 target was preregistered at efe58e96, which is true. But the denominator change (M33 added) was not registered before it was measured. Smallest correction: "The repair edit (09:25:25-09:25:55Z) and its after-count `registered 28 stale 0 []` (09:26:00Z) both preceded the writing of amendment 2 (09:28:09Z). Amendment 2's repair_design and the 27 -> 28 denominator record a measured change; they are not a preregistration. The before run was at 09:22:40Z, not about 09:24Z." Impacted axes: calibration-claim provenance, premature saturation.

### D4 (medium): the landing commit froze a wave-1 seat that was still running, and dropped one finished seat.

- `git show fa3b62ae:.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/full-mutants.json | wc -c` prints 0. The committed `advice/ReviewerC1Patch.md` contains the placeholder `FULL_RUN_RESULT_PENDING`, and the committed `evidence.md` says "running as background job bg_2008".
- The seat's full run wrote from 09:45:54Z to 10:02:18Z (birth and mtime). The report was final at 10:02:57Z, about 8 minutes after the 09:54:34Z commit. `git status` shows all three files modified against fa3b62ae.
- `advice/ScribeQualityCriterion.md` (10:05:52Z) is untracked, yet KQ36 landed in fa3b62ae, drafted from `out/ScribeQualityCriterion/KQ36-draft.md`.
- The commit subject calls this "the attempt-2 build wave record".

Smallest correction: in the wave-2 integration, commit the final ReviewerC1Patch bytes and `ScribeQualityCriterion.md`. Add one LOG or errata line saying the fa3b62ae copy of ReviewerC1Patch is a mid-run snapshot (0-byte JSON, placeholder text). Impacted axes: provenance; the wave record presented as complete.

### D5 (low): the lesson's "captured-by" for the amendment-after-receipt mistake is chronologically impossible.

Committed `corpus/lessons/round-25.md:51` says the mistake was captured by "the author, on reading CriticC2SizingA2". But amendment 3, committed at 09:38:45Z (c808ba07), already carries its own `order_disclosure` ("Written after the final receipt ... was committed at 5ea4fc44"). `CriticC2SizingA2.md` was born at 09:39:59.53Z, and its result reached the author at 09:40:27.01Z (author session `async-result`). Smallest correction: Captured-by should read "the author, in amendment 3's order_disclosure (c808ba07). CriticC2SizingA2 (09:40Z) then prompted re-running the receipt after amendment 4."

### D6 (low): carried-over wave-1 findings that no errata covers.

- `build/ATTEMPT-1-DISPOSITION.md:19` says "19 folders, 5 empty". There are 19 folders and 3 empty ones (`ExecDeclaredSurfaces`, `ScoutR23Harms`, `SrcVllmMaxModelLen`; `find -type f` counts 0). This is ReviewerAmendment2 L2, not carried into the errata.
- `ATTEMPT-1-DISPOSITION.md:9-10` says "Everything in this folder is committed ... byte for byte". Two things are not committed: `out/ExecCapacityTool/__pycache__/kama-context-capacity.cpython-314.pyc` (ignored by `.gitignore:3`) and the 3 empty folders (git cannot store them). The tracked files do match: `git diff fa3b62ae -- .ufo/waves/round-25/build` is empty. This is ReviewerAmendment2 L3, not carried.
- `pilot.md:3-4` says "about 08:22 UTC, before the preregistration". The pilot's srv.log was last written at 08:18:50.79Z (ReviewerAmendment2 L4). Not carried.
- Committed lesson line 52 says "later amendments name the observed `date -u` output and defer to the commit time". Amendment 3 still stamps 09:40Z, after its 09:38:45Z commit. The working copy already fixes this line (uncommitted, mtime 10:06:27Z); it must land.
- Errata correction 6 points at "C1.measure note". The quoted text is in `preregistration.json` C1 `repairs` (line 14), and it names "the registered counting command". That command exits 0 at efe58e96; only the instrument exits 2 (`a2-build/out/ExecC1BaseRun/efe58e96-instrument.exit`). The correction switches subject without saying so.
- `report-draft.md:4` says attempt 2 was "dispatched 2026-10-22T09:19:49Z". The dispatch record says `dispatched=2026-10-22T06:19:50-03:00` (09:19:50Z; fleet commit e4cd8af at 06:19:50 -0300). The KamaR25a2 session starts at 09:20:27.564Z. The draft is 1 s early.
- The committed `final/c1/` files (`.json`, `.exit`, `.time`) do not name the commit they ran at. I confirmed the scratch clone `/fast/scratch/hyaku/kama25-a2/c1-tip` is at 1fc41e34 with a clean status (now). That it was clean at run time is [INFERENCE].

## Checked and holding (command, output, exit code)

- Commit order and committer times: `git log --format='%H %ci | %ai | %s' efe58e96^..fa3b62ae` lists efe58e96 05:29:44, 5388b7cf 06:28:44, 1fc41e34 06:28:54, 5ea4fc44 06:37:28, c808ba07 06:38:45, 46fb04bd 06:42:31, 5c95c8f1 06:42:57, fa3b62ae 06:54:34 (all -0300), exit 0. `git reflog show master` shows each as a master tip at the same times.
- Author dates are jj change-creation times, not write times. For example fa3b62ae has author time 06:42:57 but contains errata written at 06:53:45. No lane text relies on author dates.
- Amendment 4 errata: `git cat-file -e efe58e96:.ufo/waves/round-25/count-c2.py` reports absent. The file was added in 5388b7cf. Run at 5388b7cf (worktree): `cannot read receipt: [Errno 2] ...`, rc=2.
- Counter re-scores (my clone):

  | counter | receipt 5ea4fc44 | receipt 5c95c8f1 |
  |---|---|---|
  | 5388b7cf | 14/14 | 14/14 |
  | c808ba07 | 14/14 | 14/14 |
  | 46fb04bd | `observed 11 ... missing ['L1', 'L2', 'L3']` | 14/14 |

  All rc=0. Amendment 4's "11 of 14" holds.
- Amendment 4's "replaced by the critic's proposed counter with a rewritten docstring": the ASTs of `a2-build/out/CriticC2SizingA2/count-c2-proposed.py` and the 46fb04bd counter are equal once the module docstring is removed.
- Errata correction 5: amendment-3.json mtime 09:38:45.30Z equals commit c808ba07 at 09:38:45Z. The `date -u` reading 09:36:59Z is in the author session. Amendment 4's "09:38:47Z" was printed by the c808ba07 landing command.
- Amendment 2's "date -u at 09:26:28Z and 09:26:00Z": both printed values are in the author session (09:26:00Z by the after-count command).
- Not-blind disclosure: before 09:28:45Z the author session reads `CriticLearningBar.md` from "Counterexample 2" onward (09:21:07Z) and the ExecCapacityTool K1-K8 receipt (09:21:56Z). It prints about 400 characters per ExecEdgeCells summary row (09:23:32Z, cut inside the `log` path). This matches amendment 2's honesty note 1.
- Errata correction 4: the author's own `-lv 3` output at 09:26:28Z printed "rounding down to 1536", so the correction is right.
- Errata correction 6, timing part: ExecC1BaseRun reports efe58e96 349.20 s and 147f5bdd 349.46 s / 349.54 s, `instrument exit=2`, stderr `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`.
- C1 drift chronology: tracing the literals with `git show <c>:tools/report-landing-audit.py | grep -cF` gives

  | commit | M11 matches | M17 matches |
  |---|---|---|
  | e876b95 | 1 | 0 |
  | ed1cc3a | 1 | 1 |
  | 92063cf | 0 | 2 (`bare_objects` line 214, `lookup` line 277) |

  So "M11 stopped matching at round-24 commit 92063cf" and "second call site added in round 24" hold. 92063cf is dated 2026-10-21 21:50:33 -0300, subject "round-24: ...".
- SCORECARD "1fc41e34 (instrument unchanged since, except its docstring)": `git diff 1fc41e34 fa3b62ae -- tests/report-audit/isolation-mutants.py` adds 7 docstring lines only. The edit (mtime 09:46:27.89Z) came after the full run ended (09:45:35Z), and the docstring itself says "full run at 1fc41e34".
- Full C1 run: scratch `c1-tip-mutants.time` `real 16m25.987s`, `.exit` `exit=0`. `cmp` against the committed `final/c1/c1-tip-mutants.json` returns 0. Clone HEAD is 1fc41e34, status clean.
- SCORECARD capability window "09:42:42Z to 09:42:50Z" equals the receipt `started_utc` 09:42:42.438Z and `ended_utc` 09:42:50.502Z.
- LOG "K05 ... deferred since round 10": `corpus/lessons/round-10.md:101` reads "K05 context capacity | deferred (not rejected)".
- LOG "LOG.md:1501-1502 ('PM08 remains static-only')": the phrase spans exactly those lines at fa3b62ae.
- LOG runs.json.gz: `zcat runs.json.gz | sha256sum` gives 38e4ab053e5cc7bfc53bdd8d9479a206d29dd37ccbc36f7f352582f42d766a09, and `wc -c` gives 11141804. Both match the LOG.
- Attempt-1 dispatch at 08:23:56.960Z (`dispatch-attempts.json`). The four completed seats (CriticC2Sizing, CriticLearningBar, ExecPromisorAnchorCount, SrcServerSlotsAuto) show no aborted message. The registry has no status field, so errata correction 1's "no cancellation field" holds.
- Errata correction 9's last sentence: `preregistration.json` C1 `after_target` is "stale 0" at efe58e96, so the target was preregistered there.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/CriticChronology.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/CriticChronology/timeline.md`
- `.ufo/waves/round-25/a2-falsify/out/CriticChronology/attempt1-seat-session-ends.tsv`
- Scratch only: `/fast/scratch/hyaku/kama-r25a2w2/CriticChronology/` (`clone/`, `wt5388/`, `count-*.py`, `receipt-*.json`, `im-efe.py`)
