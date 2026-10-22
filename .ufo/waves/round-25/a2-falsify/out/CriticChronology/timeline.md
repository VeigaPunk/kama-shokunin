# CriticChronology timeline (UTC; lane mtimes are -0300 and converted by adding 3 h)

Sources: lane file mtimes and birth times (`stat`), git committer times, the
orchestrator session `~/.omp/agent/sessions/-Projects-shokunin/2026-10-22T07-55-56-355Z_01a1629c-0c43-7754-9701-07270d148a3a.jsonl`
(read only), the attempt-1 seat sessions under its `KamaR25/` folder and the
attempt-2 author session `KamaR25a2.jsonl` (read only).

| time (UTC) | event | evidence |
|---|---|---|
| 08:23:56.96 | attempt-1 wave dispatched, 34 seats | build/dispatch-attempts.json |
| 08:26:24-08:27:33 | peer K1 trial in scratch | /fast/scratch/hyaku/kama-r25/ExecRawReplicate/trial.health, k1-trial.log mtimes |
| 08:27:26 | ExecEdgeCells cells.json (scratch) | /fast/scratch/hyaku/kama-r25/ExecEdgeCells/cells.json mtime |
| 08:27:35.88-08:27:38 | ExecEdgeCells raw E01-E19 written, incl. E09 (`-np 2`, no `-c`: n_ctx_slot 2048, kv_unified false) | build/out/ExecEdgeCells birth; E09-np2-noc/server.log:10 |
| 08:28:03-08:28:05.77 | CriticLearningBar cell-predictions.py/.out (first X1, X2 predictions) | birth times |
| 08:28:36.81-08:28:56 | ExecRawReplicate K1-K8 outputs | mtimes |
| 08:28:54.91 | CriticC2Sizing.md written (single write, birth = mtime) | stat |
| 08:29:23.24 | CriticLearningBar.md written (single write, birth = mtime) | stat |
| 08:30:46.216 | Main to KamaR25: "stand down now ... stop all work" | orchestrator session |
| 08:30:48.89 | out/ScoutR23Harms folder created | birth |
| 08:30:50.80 | RevengerM11 M11-reanchor.stdout.json | mtime |
| 08:30:52.46-.55 | 30 seat sessions show an aborted assistant message; 29 of them start no tool call after it (ExecCapacityTool is the exception) | attempt1-seat-session-ends.tsv |
| 08:31:14.578 | KamaR25 returns "I cancelled the 30 seats still running, by id, through proc://…/kill" | orchestrator session |
| 08:31:20.944 | Main records "stood down at 2026-10-22T08:30Z" via inline.sh | orchestrator session |
| 08:34:45.14 | ExecCapacityTool writes kama-context-capacity.py (folder born) | seat session; folder birth |
| 08:37:26.35-08:37:30.69 | ExecCapacityTool runs 8 live llama-server cells, ports 47400-47407, exit 0 | seat session; receipt started/ended_utc |
| 08:37:47.85 | ExecCapacityTool last tool call | seat session |
| 08:37:52.45-.55 | all remaining attempt-1 seat sessions disposed | session_exit records |
| 09:19:50 | kama attempt 2 dispatched (inline.sh `dispatched=2026-10-22T06:19:50-03:00`; fleet commit e4cd8af 06:19:50 -0300) | orchestrator session |
| 09:20:27.56 | KamaR25a2 session created | KamaR25a2.jsonl header |
| 09:22:39.94 | C1 before count `registered 27 stale 2` (exit 0) | author session |
| 09:25:25-09:25:55.54 | C1 re-anchor edits to isolation-mutants.py | author session; ReviewerAmendment2 timeline |
| 09:26:00.48 | C1 after count `registered 28 stale 0 []` printed (date 09:26:00Z) | author session |
| 09:26:28 | `-lv 3` walk shows `rounding down to 1536` (pool value at -lv 3) | author session; pilot-lv3.log:9 |
| 09:28:09.15 | amendment 2 written (repair_design, denominator 27 -> 28) | author session write call; mtime 09:28:17.59 |
| 09:28:44 / 09:28:54 | commits 5388b7cf / 1fc41e34 | git |
| 09:29:09-09:45:35 | full C1 run in scratch clone at 1fc41e34 (clean), exit 0, 26/28 killed | /fast/scratch/hyaku/kama25-a2/c1-tip* |
| 09:37:28 | 5ea4fc44 first final receipt | git |
| 09:37:49.89 | MutationC2Counter result reaches author | author session |
| 09:38:45.30 | amendment 3 committed (c808ba07) with order_disclosure | git; mtime |
| 09:39:59.53 | CriticC2SizingA2.md written | birth |
| 09:40:27.01 | CriticC2SizingA2 result reaches author | author session |
| 09:42:31 / 09:42:42-50 / 09:42:57 | amendment 4 commit / receipt re-run / receipt commit | git; receipt |
| 09:46:27.89 | isolation-mutants.py docstring edit (lands in fa3b62ae) | mtime |
| 09:53:45.86 | errata-attempt-2.json written | author session write call; mtime |
| 09:54:34 | landing commit fa3b62ae | git |
| 09:45:54-10:02:18 | ReviewerC1Patch full run still writing; committed copy at fa3b62ae is 0 bytes | stat; `git show fa3b62ae:…/full-mutants.json | wc -c` = 0 |
| 10:02:57 | ReviewerC1Patch.md final (committed copy says FULL_RUN_RESULT_PENDING) | mtime; git diff |
| 10:05:52 | ScribeQualityCriterion.md written (not in fa3b62ae) | mtime; git status `??` |
