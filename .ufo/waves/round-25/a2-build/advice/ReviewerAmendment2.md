# ReviewerAmendment2: chronology and provenance review, kama round 25 attempt 2

**Verdict: not clean. No numeric registered target is narrowed, but amendment 2 has open chronology and disclosure defects, and the attempt-2 full C1 run shows the repaired M17 check surviving.**

## Scope and snapshot

- Target: commit 5388b7cf (committer 2026-10-22 09:28:44Z), `preregistration-amendment-2.json`, `build/ATTEMPT-1-DISPOSITION.md`, `count-c2.py` as committed, and file mtimes.
- The lane moved during review. At the snapshot (09:49:14Z), master was 5c95c8f. Later commits: 5ea4fc4 (09:37:28Z), c808ba0 (09:38:45Z, amendment 3), 46fb04b (09:42:31Z, amendment 4), 5c95c8f (09:42:57Z). I checked them only where they restate or change the same claims.
- Times are UTC. Git and `ls` print -0300; I converted by adding 3 hours.
- No llama-server was started. At the snapshot, `pgrep -c llama-server` printed 0, and `ss -ltn` showed no listener on 47311.
- No tools were installed or updated. No external sources were cited.
- Git was read-only (show, log, diff, merge-base, check-ignore, and status with `--no-optional-locks`). Python counters ran with `-B`.
- Command-by-command evidence with exit codes: `a2-build/out/ReviewerAmendment2/checks.txt`. Timeline: `a2-build/out/ReviewerAmendment2/timeline.txt`.

Paths below are relative to `.ufo/waves/round-25/` unless shown otherwise.

## Findings

### High

**H1. The stated attempt-1 stand-down (08:30Z) is contradicted by file times, and nothing in the repo records it.**

- Claims: `build/ATTEMPT-1-DISPOSITION.md:4-6` ("stood attempt 1 down at 08:30Z", "the other 30 were cancelled mid-run"); `preregistration-amendment-2.json:7` (same stand-down).
- Contrary evidence (mtimes, UTC):
  - `build/out/RevengerM11/M11-reanchor.stdout.json` written 08:30:50.80Z.
  - `build/out/ExecCapacityTool/kama-context-capacity.py` written 08:36:56.10Z.
  - `build/out/ExecCapacityTool/__pycache__/...pyc` written 08:37:14.62Z (the tool was imported).
  - `build/out/ExecCapacityTool/context-capacity-receipt.json`: `started_utc` 08:37:26.381Z, `ended_utc` 08:37:30.688Z, `exit_code` 0, summary 8 cells, 8 observed, `all_ports_closed` true.
- No cancellation record exists. `build/advice/swarm-registry.json:4-5` gives `createdAt` 08:23:41.107Z and `updatedAt` 08:24:15.744Z. Its 34 members carry no status field. `spawn-result.json` has 34 `"status": "pending"` entries.
- Consequence: "30 cancelled mid-run" cannot be checked from the repo. `build/ATTEMPT-1-DISPOSITION.md:19` calls `out/` "partial outputs", but the ExecCapacityTool receipt is complete, and `build/out/ExecEdgeCells/raw/summary.json` has all 19 rows.
- Fix: give the real stand-down source and time, and the true last write (08:37:30.69Z), or remove the time claim.

**H2. The not-blind disclosure does not match what the X and L predictions were written after. L2 and L3 have no source at all.**

- Claim: `preregistration-amendment-2.json:10`: X1-X3 and L1-L3 are "source-derived by the attempt-1 critic seats ... each says which."
- Facts:
  - L2 (line 32) and L3 (line 33) name no seat and no source. L1 (line 31) cites `server-context.cpp` 4301 and 4318-4320 but names no seat.
  - The only L source in the repo is `build/advice/CriticLearningBar.md:69`. That advice was written at 08:29:23.24Z. No L-cell appears in any `out/` prediction file (grep for L1-L3 under `out/CriticC2Sizing` and `out/CriticLearningBar`: no match).
  - That advice is not blind to attempt-1 K-run output. It cites a peer's K1 trial files (line 42), the K6 change from 1024 to 1536 (line 76), and "the K6 warning text and the K5 two warnings" (line 94). Those K-run files were written 08:28:36-08:28:56Z.
  - The X1, X2 and K6 predictions are blind at source. They sit in `out/CriticC2Sizing/source-model.out` (08:27:29.12Z) and `out/CriticLearningBar/cell-predictions.out` (08:28:05.77Z), both before the first K-cell output (08:28:36.81Z). The critic's X3 (`-c 2048`, auto slots) is a different cell from the amendment's X3 (`-np 4 --no-kv-unified --fit off`). The amendment labels its X3 as author-derived, which is honest.
  - E17, E18 and E19 (`out/ExecEdgeCells/raw/E17-*`, `E18-*`, `E19-*/record.json`, written 08:27:37-08:27:38Z) record HTTP 400 "exceeds the available context size" for an 11,602-token prompt. These bear directly on L3's premise ("the failure in L1 is concurrency, not request size", amendment line 33). Neither document mentions them.
  - The disposition's not-blind paragraph (`build/ATTEMPT-1-DISPOSITION.md:21-24`) omits the "critic source models" that amendment line 9 says were read.
  - `build/advice/CriticC2Sizing.md:64` says the K6 values are unobserved "until ExecEdgeCells or the capacity tool runs K6". K6 had already run at 08:28:49Z.
- Effect: the claim value (observed count) is unchanged, and prediction matches are already calibration-only. The statements "source-derived, not observed" for L1-L3 and "X2 equals K1" are not supported as written.
- Fix: name a source for every X and L prediction, state that the advice files postdate attempt-1 K outputs, and list E17-E19 as on disk and not used.

**H3. C1: the repaired M17 check survives the full isolation run at the tip. The registry bookkeeping is non-narrowing, but kill coverage is not.**

- Registry, verified. The registered C1 command prints `registered 28 stale 0 []`, exit 0, at the working tree.
  - efe58e96 and 5388b7cf: 27 registered, stale 2 (M11 with 0 matches, M17 with 2), as amendment line 16 says.
  - 1fc41e34: 28 registered, stale 0. No id removed. M33 added. Only the M11 and M17 literals changed. The auditor bytes are identical across the repair.
  - M11 matches once at auditor line 682. M17 matches once at line 275, inside `lookup()`. M33 matches once at line 212, in `bare_objects()`. The round-23 guard is at e876b95 lines 170-172, inside `lookup()`.
  - The four RETIRED ids (M14, M22, M27, M29) were already in the RETIRED list at efe58e96 (line 106). Attempt 2 retired nothing.
- Kill coverage (attempt-2 outputs; I did not re-run the grid):
  - Round 23 killed M17: `.ufo/waves/round-23/final/mutants.json` lines 147-153 (`killed` true, `failed_rows` F13-ref-named-abbreviation).
  - At the tip, the M17-mutated auditor passes F13. `a2-build/out/MutationM17M33Kill/m17.json`: F13 met true, `faults_met` 26 of 26, `m17.rc` 0. The M33-mutated copy fails F13 (`m33.json` met false; `m33.rc` 1).
  - Full run in scratch, `/fast/scratch/hyaku/kama25-a2/c1-tip-mutants.json` (written 09:45:35Z): mutants 28, killed 26, surviving `["M17-ref-shadow", "M20-log-sha-shape"]`. The exit code is not recorded; the `.time` file holds timings only.
- Amendment 2 does not say this. Its supporting-evidence rule (line 18) says a survivor must be "reported, not hidden." The SCORECARD row at `SCORECARD.md:1166` claims "30/31 killed on a named row"; with M17 surviving, that claim no longer holds.
- The repair text did not cause the loss, because the auditor is byte-identical across it. Commits 92063cf and ed1cc3a (round 24) touch the auditor or the grid between round 23 and the tip.
- Fix: report M17 as a survivor, with the exit code, in the C1 closure. Do not claim "both call sites covered" as a kill result.

### Medium

**M1. Amendment 3 has the same false stamp, and no errata covers it.** `preregistration-amendment-3.json`, field `written_utc`: "2026-10-22T09:40Z (date -u read at 09:36:59Z ...)". Its commit c808ba0 is 09:38:45Z, file mtime 09:38:45.30Z. The stamp falls after the commit that the amendment names as authoritative. Amendment 4's errata covers only amendment 2.

**M2. Amendment 2's `written_utc` of 09:30Z is false. Acknowledged by amendment 4.** `preregistration-amendment-2.json:6` says 09:30Z, "read from date -u at 09:26:28Z and 09:26:00Z." The file mtime is 09:28:17.59Z and the commit is 09:28:44Z. Amendment 4's `errata_to_amendment_2` acknowledges it. Amendment 2's bytes were left unedited, which the rules require. Status: corrected by errata.

**M3. The sourcing requirement for the learning entry was dropped without saying so.** `preregistration.json:48` says the entry is "new entry on K05 ground, sourced on S rows opened this round." `preregistration.json:59` says "C2 rests on SOURCES rows opened this round." Amendment 2 line 37 lists the same entry with "(CriticC2Sizing section 6)" and no sourcing condition. The same critic (`build/advice/CriticLearningBar.md:79`) reports that no admitted SOURCES row cites `src/llama-context.cpp` or `common/fit.cpp`. This is a registered evidence condition, not a numeric target. Restate it or withdraw it explicitly.

**M4. "Stays replication-level for every cell" misstates the baseline.** `preregistration-amendment-2.json:9` says K-cell prediction grading "stays replication-level for every cell." Amendment 1 (`preregistration-amendment-1.json:14`) grades K4, K5, K7 and K8 as predictions. Amendment 2 withdraws that grading. The reason (the author had read the K1-K8 observed rows) is given, but the word should be "withdrawn."

**M5. The advice-file write window is wrong.** Amendment line 10 says "advice files, written about 08:27Z to 08:28Z." The actual advice mtimes are: `CriticC2Sizing.md` 08:28:54.91Z, `ExecPromisorAnchorCount.md` 08:29:08.39Z, `SrcServerSlotsAuto.md` 08:29:22.07Z, `CriticLearningBar.md` 08:29:23.24Z. The 08:27-08:28 window matches the `out/` prediction files, not the advice.

**M6. The claim that the KV pool prints only at `-v` is too broad.** Amendment line 11 says the pool is printed only at full verbosity and is "absent" at `-lv 3`. The info line `llama_context: n_ctx = N` is indeed absent at `-lv 3` (`pilot-lv3.log` has none). But the warning "n_ctx is not divisible by n_seq_max - rounding down to 1536" is printed at `-lv 3` (`pilot-lv3.log:9`, 09:26:28Z) and at default verbosity 3 in attempt 1 (`build/out/ExecRawReplicate/K6/server.log:7`; verbosity 3 at line 2). `build/advice/CriticLearningBar.md:94` repeats the broad claim. The `-v` choice still holds for the info line the counter requires.

### Low

**L1.** Amendment line 9 calls the attempt-1 outputs "uncommitted." They are committed in 5388b7cf (51 tracked paths, including `ExecRawReplicate/K*`, `ExecEdgeCells/raw/E*` and `ExecCapacityTool/context-capacity-receipt.json`). This was true when drafted and is stale at commit.

**L2.** Disposition line 19 says "out/* (19 folders, 5 empty)." There are 19 folders, but only 3 are empty (`ExecDeclaredSurfaces`, `SrcVllmMaxModelLen`, `ScoutR23Harms`). There are also 2 zero-byte files (`RevengerM11/M11-unmodified.stdout.txt`, `RevengerM11/M11-reanchor.stderr.txt`). The count of 5 holds only if files are counted.

**L3.** Disposition lines 9-10 say the folder is "committed ... byte for byte." All 143 tracked round-25 files match the working tree. Not committed: `build/out/ExecCapacityTool/__pycache__/kama-context-capacity.cpython-314.pyc` (08:37:14.62Z, ignored by `.gitignore:3`), and three empty folders, which git cannot store. The `.pyc` also shows the tool ran after the stated stand-down.

**L4.** `pilot.md:3-4` says the run was "about 08:22 UTC, before the preregistration." The attempt-1 `srv.log` was last written at 08:18:50.79Z, `preregistration.json` at 08:21:12.47Z, and `pilot.md` at 08:21:54.97Z. "About 08:22" is wrong. Amendment 1 corrects the preregistration's stamp but not this line.

**L5.** Amendment line 25's "before" value ("count-c2.py exit 2 ... registered 14, observed 0") was corrected by amendment 4's errata. Checked: on a missing path the script prints only "cannot read receipt" and exits 2. It never prints "registered 14, observed 0."

### Info

**I1.** C1 ordering. `tests/report-audit/isolation-mutants.py` was edited at 09:25:55.54Z. The "before" run is stated as about 09:24Z (amendment line 16), which is consistent. But the design was written into the amendment (09:28:17Z) after the edit. The closure should say so.

**I2.** The first committed final receipt (5ea4fc4, 09:37:28Z) came before amendment 3 (09:38:45Z) and amendment 4 (09:42:31Z). The critic's rule "committed before any receipt" (`a2-build/advice/CriticC2SizingA2.md`, section 6, item 1) was not kept for that receipt. Amendment 3 discloses the order. That receipt scores v1 14/14, v3 14/14, v4 11/14 (L1-L3 lack request times). The final re-run (09:42:42-09:42:50Z) came after amendment 4's commit.

## Checks that passed

- Commit 5388b7cf: committer 09:28:44Z. Amendment mtime 09:28:17.59Z, `count-c2.py` mtime 09:27:32.57Z, disposition mtime 09:28:35.71Z. Ancestry: efe58e96, then 5388b7cf, then 1fc41e34, then 5c95c8f.
- `preregistration.json`, `preregistration-amendment-1.json` and `pilot.md` are byte-identical at efe58e96, 5388b7cf and the working tree.
- Amendment 1's stamps: srv.log 08:18:50.79Z; census 08:20:23.34Z; preregistration.json 08:21:12.47Z; pilot.md 08:21:54.97Z (42 s after); dispatch 08:23:56.96Z; amendment 1 mtime 08:29:40.93Z.
- Attempt-1 dispatch: 34 spawned; `spec.json` has 34 items; `dispatch.json` counts 34; registry has 34 members; 4 advice reports; 19 `out/` folders; RevengerM11 killed by F20 (`M11-reanchor.stdout.json:41`).
- K1-K8 args: `run-cells.sh` lines 17-24 match `preregistration.json` K1-K8 and `count-c2.py` CELLS. X1-X3 and L1-L3 args in the counter match amendment lines 28-33.
- C1: stale counts and literal positions as above. No retirement by attempt 2.
- C2 counter: the v1-to-v4 diff (`a2-build/out/ReviewerAmendment2/count-c2-v1-to-v4.diff`) only adds or tightens checks. CELLS, args, MODEL_SHA and LOAD_REQUEST are unchanged. Amendment 4's claim that the first receipt scores 11/14 under v4 is confirmed.
- Pilot: `pilot-v.log:284` shows `n_ctx = 1536`. Both pilot logs list port 47311 and were written 09:26:28-09:26:34Z, before amendment 2 (09:28:17Z).
- The first 400 raw characters of each of the 19 E-rows contain `cell_id`, `label`, `args`, `env`, `port` and `argv`, with no status, body or observed field. This is consistent with amendment line 9.
- K6 pool 1536 was predicted before any K6 output (`source-model.out` at 08:27:29Z), as amendment 1 says.
- No llama-server was running at the snapshot, and nothing listened on 47311.

## Residual risk and verification gaps

- The lane moved during review. The C2 target is now measured on the 09:42:50Z receipt. I checked only the counter scores for that receipt, not its raw bytes against the server logs.
- The C1 full run's exit code is not recorded. I did not re-run the grid; the M17 survivor comes from attempt-2 outputs I read.
- "Stricter only" for v3 and v4 rests on reading the diffs and scoring two receipts. I did not run a differential test over generated receipts.
- Who read what is self-reported in the amendment. I could not check what the author opened.
- The 08:30Z stand-down source is not in the repo.

## Files written

- `kama-shokunin/.ufo/waves/round-25/a2-build/advice/ReviewerAmendment2.md` (this report)
- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ReviewerAmendment2/checks.txt`
- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ReviewerAmendment2/timeline.txt`
- `kama-shokunin/.ufo/waves/round-25/a2-build/out/ReviewerAmendment2/count-c2-v1-to-v4.diff`
- Scratch, `/fast/scratch/hyaku/kama-r25a2/ReviewerAmendment2/`: `count-c2.committed.py`, `count-v1.py`, `count-v3.py`, `count-v4.py`, `receipt-5ea4fc4.json`, `count-c2-v1-to-v3.diff`
