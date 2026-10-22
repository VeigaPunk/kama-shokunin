# ReviewerScorecardLog: falsify review of the round-25 SCORECARD and LOG entries

Verdict: defect found. The hashes, counts and command outputs reproduce. The defects are in the capability
demonstration (it overwrites committed evidence), in the causal and prediction wording, and in several
missing qualifiers and unreconciled numbers.

## Scope and pins

- Target: `SCORECARD.md` lines 1252-1295 and `LOG.md` lines 1635-1678 at fa3b62ae6475d111eb466d79af616aeebb08bbb9.
- Lane HEAD is 46be41c. That commit adds four `a2-falsify` and report-draft files and touches neither
  SCORECARD.md nor LOG.md (`git show --stat 46be41c`, exit 0). The reviewed bytes are current.
- Git-writing checks ran only in the scratch clone `/fast/scratch/hyaku/kama-r25a2w2/ReviewerScorecardLog/clone`
  (checked out at fa3b62ae; `git rev-parse HEAD` confirmed).
- Command-by-command record with exit codes: `out/ReviewerScorecardLog/checks.md`.
- No llama-server child was started. The capability demonstration was read, not run (F1 explains why).
- Tool installs: none. No install was needed for these checks.
- Disclosure: one read-only `git status --short | head -5` ran in the lane as the first command; git may refresh
  the index stat cache. Every later lane git call was `show`, `log`, `ls-tree`, `grep` on a commit, or a
  commit-to-commit `diff`.

## What holds (checked against the repo)

1. C1 counting command (`preregistration.json` C1.command): at efe58e96 it prints `registered 27 stale 2
   ['M11-listing-surrogates', 'M17-ref-shadow']`; at 1fc41e34 and at fa3b62ae it prints `registered 28 stale 0 []`.
   All exit 0 (checks 1-3). Matches SCORECARD 1260 and LOG 1640-1648.
2. C1 full run: `.ufo/waves/round-25/final/c1/c1-tip-mutants.json` has pristine `passed`, 28 mutants, 26 killed,
   surviving `[M17-ref-shadow, M20-log-sha-shape]`, 4 retired ids. `.exit` reads `exit=0`; `.err` is empty
   (check 9). Its sha256 `75ad1e03...` equals the copy from the 1fc41e34 replicate, `ExecC1TipReplicate/mutant-run-1fc41e34...json`
   (check 10).
3. Instrument diff 1fc41e34..fa3b62ae: `tests/report-audit/isolation-mutants.py` gains 7 lines, all inside the
   module docstring (opens line 2, closes line 45). The auditor is not in the diff (check 12). "Instrument unchanged
   since, except its docstring" (SCORECARD 1260) holds.
4. M17 causal run: `ed1cc3a-tipM17-causal.json` shows the tip's M17 literal fails grid row F13 at ed1cc3a
   (`grid_exit` 1). `tip-M17-M33-run.json` (run at the tip, 2 mutants, 1 killed) shows M17 survives and M33 is
   killed by F13. The C1 full run's row for M33 also lists F13 as its failed row (check 19; check 9).
5. C2 counter at fa3b62ae: `registered 14 observed 14 bound True missing []`, exit 0. With a missing receipt
   path it exits 2 and prints no count (checks 4-5).
6. Receipt bytes: `context-capacity-receipt.json` has sha256 `78c51385...` at 5c95c8f, at fa3b62ae and in the
   lane worktree (check 6). Receipt `started_utc` 2026-10-22T09:42:42.438Z and `ended_utc` 09:42:50.502Z match
   SCORECARD 1287. `exit_code` 0, `all_ports_closed` true, 14 cells, build 11755 commit 704366d76.
7. Binding: receipt `model_sha256` 270cba1b... equals the fixture model file. Receipt `server.sha256` b6a31a8e...
   equals the realpath of `~/.local/bin/llama-server`. Receipt `tool.sha256` 589841cd... equals
   `tools/kama-context-capacity.py` at 46fb04bd and at fa3b62ae (checks 7-8).
8. Raw evidence: 70 files under `final/raw/`. `runs.json.gz` decompresses to 11141804 bytes with sha256
   `38e4ab05...`, as LOG 1674-1676 states (checks 11, count).
9. Sources: SOURCES.md has 105 rows at 147f5bdd and 113 at fa3b62ae. A rows 100 -> 108 and cells equal to `mined`
   86 -> 94. Rows S106-S113 exist (check 14). SCORECARD 1290 holds.
10. Verbatim quote: SCORECARD 1270 equals `CriticC1Calibration.md` line 73 exactly, with the `> ` prefix removed (check 15).
11. Scores: calibration 7 and coverage 9 at SCORECARD lines 562 and 1019; line 1166 is the historical round-23
    isolation row, as the quote says. The C2 erratum (1263-1264) holds.
12. Cited rules and files: `corpus/QUALITY.md:203` (KQ36); `SKILL.md:887` (PM08 wording), `:888` (the "Retained
    isolation mutation experiment" row), `:1006` (27 then 28 literals), `:188-190` (`--kv-unified` premise);
    `corpus/lessons/round-25.md:78` (`## C1 result`); `corpus/lessons/round-24-verifier-spotcheck.md:80-81`
    (M11 zero matches, M17 two); `LOG.md:1500-1502` (old PM08 bytes kept).
13. Cells: L1 two requests, both HTTP 500 "Context size has been exceeded." (1000 + 600 tokens). The raw log shows
    `n_tokens = 1025` for both slots (`final/raw/L1.server.log`, lines 1852 and 1866). L2 and L3 have four 200s in total.
    K1 and X2 both report `/props` n_ctx 2048 and total_slots 4, with pools 2048 and 8192. X1 reports per-slot 2048
    on pool 8192. X3 reports 512 (check 16). The LOG findings at 1661-1663 hold.
14. Tool installs: `ExecC1TipReplicate.md:83-85` says "None." Other round-25 advice files say the same, and a grep found
    no install report.
15. Capability row placement: SCORECARD 1283 uses the per-round `### capabilities: append` form, which round 20
    also uses (line 909). The SCORECARD 122-128 and 619-624 notes say rows enter only through a round that
    demonstrates the capability running, so the row is not in the wrong place.
16. Plain-English mechanics: a dictionary check (50,692-word list) found no run-together words. The only hits,
    "loopback" (SCORECARD 1287) and "orchestrator" (LOG 1637), are valid words. A missing-space scan found no defects.

## Findings, by severity

### F1 HIGH: the capability demonstration overwrites the committed evidence

- SCORECARD.md:1287 demonstration: `python3 tools/kama-context-capacity.py --out .ufo/waves/round-25/final/context-capacity-receipt.json`.
- `tools/kama-context-capacity.py:769-770`: with `--out`, `raw_dir = Path(args.out).parent / 'raw'`, so the raw
  files go to `final/raw/`. `:393` and `:426` write raw bytes with `write_bytes`. `:841-843` write the receipt
  with `write_text` and no existence check.
- Effect: a re-run replaces the committed receipt (sha256 `78c51385...`) and all 70 files under `final/raw/`. The
  new bytes differ (ports, times, pids). Git keeps the old bytes, but the worktree would then show evidence that
  the row's "shown running this round" no longer describes. I did not run the command, because it starts
  llama-server children and would replace the evidence.
- Other gaps in the same row: the default server and model are host paths (`~/.local/bin/llama-server` is a
  symlink to b11755 and exists; `~/.cache/kama-shokunin/models/stories260K.gguf` exists and its sha256 matches).
  The default port range `47400-47419` (tool `:660`) is not named. "exit 0" means the receipt's `exit_code` is 0; it
  does not mean every cell passed, which is what the counter tests.
- Smallest correction: write to a scratch path and pass that path to the counter:
  `python3 tools/kama-context-capacity.py --out /fast/scratch/hyaku/kama-r25/demo/context-capacity-receipt.json`
  then `python3 .ufo/waves/round-25/count-c2.py /fast/scratch/hyaku/kama-r25/demo/context-capacity-receipt.json`
  (the counter accepts a receipt path, per its docstring). Name the port range in the row. Keep the committed
  receipt as the round's evidence.

### F2 MEDIUM: the M17 cause is stated as fact, and the instrument's own inference label is dropped

- SCORECARD.md:1278-1281: "since round-24 commit 92063cf no caller reaches the `lookup()` refusal, so M17 survives".
- LOG.md:1648-1650: "M17 survives because round-24 commit 92063cf moved the reachable path to `bare_objects()`; F13
  now kills M33. The instrument docstring says so."
- The causal part holds: `ed1cc3a-tipM17-causal.json` (check 19) and the blame in `RevengerM17Sites.md` §3-4.
- The wording does not hold. `RevengerM17Sites.md:1` says "no caller in the audit can fire the lookup() refusal",
  not "reaches". The only no-peel production call is `tools/report-landing-audit.py:538`
  (`full = lookup(stores, full_tokens)`). It runs the guard at `:275`, but it passes full 40-hex tokens.
  `probe_git_shadow.out:11-13` shows the predicate is False for a full 40-hex token with a same-named tag.
  `:5-9` shows True for an abbreviation. So the guard executes but cannot raise for production input.
- The instrument docstring (`tests/report-audit/isolation-mutants.py:33-39`) marks this reading
  "[INFERENCE from source and a probe]" and says "M17 may be unkillable". SCORECARD and LOG state the cause as
  settled and drop both the label and the hedge. LOG 1650 says the docstring "says so", which it does only in part.
- Smallest correction (SCORECARD 1278-1281): "[INFERENCE] No production caller can make the lookup() refusal raise:
  its only no-peel call (`tools/report-landing-audit.py:538`) passes full 40-hex tokens, which git resolves as object
  names (`probe_git_shadow.out:11-13`). The round-23 kill ran through the peel recursion that 92063cf replaced with
  `bare_objects()` (`:246`). M17 may be unkillable by any command-line input (instrument docstring; not observed)."
  LOG 1650: "The instrument docstring gives the same cause as an inference, not an observation."

### F3 MEDIUM: "predicted every per-slot K-cell value" conflicts with the errata

- LOG.md:1652-1653: "the attempt-1 critic CriticLearningBar showed the round-20 rule already predicted every per-slot
  K-cell value".
- `errata-attempt-2.json` correction 2: CriticLearningBar advice was written 08:28:54Z to 08:29:23Z, "after
  attempt-1 K-cell runs existed and citing them". Correction 3: the errata "withdraws the prediction credit that
  amendment 1 gave K4, K5, K7 and K8, because the author had read attempt-1 K-cell values first".
- The critic's table compares the rule with values already observed in attempt 1
  (`.ufo/waves/round-25/build/advice/CriticLearningBar.md:25-35`). Its line 40 says the rule "already predicts all
  eight preregistered per-slot values". That is replication of observed values, not prediction, and
  `preregistration.json` grades predictions only as calibration evidence.
- SCORECARD never cites the errata. LOG cites it only for the attempt-1 disposition (LOG 1638-1639).
- Smallest correction (LOG 1652-1653): "the attempt-1 critic showed that the round-20 rule reproduces the eight
  per-slot K-cell values already observed in attempt 1 (`CriticLearningBar.md:25-40`, written after those runs
  existed; `errata-attempt-2.json` corrections 2-3). This is replication, not prediction." Add the errata to SCORECARD 1254-1256.

### F4 LOW-MEDIUM: KQ36 is applied by name, but the per-mutant clause is not fully met, and the LOG gloss is broader than the text

- `corpus/QUALITY.md:203` KQ36 has two clauses. The first, re-run and paste at the landed tip, applies to "a source
  measured by a registered counting command". The auditor is what the C1 command measures, and the auditor did
  not change in round 25 (`git diff --stat 1fc41e34 fa3b62ae -- tools/report-landing-audit.py ...` shows only the
  instrument; `RevengerM17Sites.md` §1). So the first clause is not literally triggered. The second clause applies:
  "A re-anchor names, per mutant, whether its last recorded kill still holds."
- SCORECARD 1281 names M17 for that purpose. It does not name M11 (re-anchored; not among the 1fc41e34 survivors, but
  its status is not stated) or M33 (new; killed by F13 at 1fc41e34).
- LOG 1673 glosses KQ36 as "registered instruments re-run at the landed tip". That is broader than the text.
- Verified at fa3b62ae: the C1 command gives `registered 28 stale 0 []`, exit 0, so the value holds at the pinned commit.
- Smallest correction: SCORECARD 1281 add "M11: re-anchored; its round-23 kill holds (not among the 1fc41e34 survivors);
  M33: new, killed by F13 at 1fc41e34." LOG 1673 change the gloss to "KQ36: a re-anchor names each mutant's kill status,
  so a survivor caused by a moved path is not hidden." Re-run and paste at the landed commit if one is made.

### F5 LOW-MEDIUM: "operability 8 held" has no reconciling record

- SCORECARD.md:1289: "Other scores held: operability 8, freshness 8, depth 7, adjacency 7."
- The last explicit operability number is round 22: SCORECARD.md:1038 "(operability8)".
- Round 23 says "Operability is **traded, not unchanged**, on two declared states" (SCORECARD.md:1171-1172).
  The round-23 outside closure reads "calibration improved but operability harmed" (LOG.md:1413-1415),
  restated at SCORECARD.md:1192-1193.
- No section says whether that closure reading changed the operability number. Round 25 restates 8 without saying
  whether it was carried, re-read or changed. A reader sees "harmed" followed by "held".
- Smallest correction (SCORECARD 1289): state the basis, for example "operability 8: last numeric reading round 22
  (SCORECARD.md:1038); the round-23 outside closure's 'harmed' reading (1192-1193) is not a numeric change under
  <rule>." If the lane has no such rule, say the number is carried forward and the harm reading is not numeric.

### F6 LOW: the C2 measured commit names the receipt-landing commit, and the C2 "before" names no commit

- SCORECARD.md:1256: "Measured commits are lane branch tips named per row." The C2 row (1261) names
  "receipt 5c95c8f111a981e316cd4933e38fc363e51f8604".
- The receipt's `tool.sha256` 589841cd... is the tool at 46fb04bd, its last change. The receipt run started at
  2026-10-22T09:42:42Z, which is 06:42:42 -03:00. That is after 46fb04bd (06:42:31 -03:00) and before 5c95c8f
  (06:42:57 -03:00). So the measured commit is 46fb04bd; 5c95c8f landed the receipt.
- The C2 "before" cell (1261) names no commit. I reproduced the counter's exit 2 with a missing receipt (check 5),
  but the row should say where the before-state was observed.
- Smallest correction: "measured at 46fb04bd (tool sha256 589841cd...); receipt landed at 5c95c8f; before-state
  observed at <commit>."

### F7 LOW: "validate exit 0" omits the warning increase from 25 to 29

- SCORECARD.md:1290: "... validate exit 0."
- Re-run (check 13): exit 0, 0 E codes, 29 W04, stderr empty. The round-start run (`before/census-validate.out`)
  had 25 W04. New W04 warnings: S108, S109, S110, S112, all duplicate URLs across scopes with older rows.
  Copy: `out/ReviewerScorecardLog/census-validate-113-rows.out`.
- Smallest correction: "validate exit 0, 0 E codes, 29 W04 duplicate-URL warnings (25 at round start; new S108, S109, S110, S112)."

### F8 LOW: "five attack findings" cannot be traced, and "discernment" is not a scored axis

- SCORECARD.md:1291-1295: "discernment improved (five attack findings turned into stricter counters, scoped claims
  and a filed axis dispute)".
- The round text does not list five findings. The repo supports these: counter amendments 3 and 4 (c808ba07,
  46fb04bd); the `not_claimed` scoping in `preregistration.json`; the axis dispute at SCORECARD 1267-1270; and
  `errata-attempt-2.json`, which has nine corrections. I cannot reproduce a count of five. [INFERENCE on the author's intent]
- "discernment" is not one of the six scored axes (operability, calibration, freshness, coverage, depth, adjacency;
  SCORECARD 562). The sentence is an unscored self-reading.
- Smallest correction: list the five by commit or file, or drop the number. Label the trend sentence as the author's reading.

### F9 LOW: the reading that the SKILL row "promised an evaluated inventory" needs the row's text

- SCORECARD.md:1272-1276: the SKILL row "promised an evaluated inventory the command could not deliver".
- `SKILL.md:888` verdict column: "0 pristine passed and selected inventory evaluated, survivors reported; 2 fail-fast
  could-not-evaluate". The stale instrument exited 2 (`ExecC1BaseRun` efe58e96-instrument.exit "instrument exit=2";
  `ExecC1BaseRun.md:53` fail-fast). Exit 2 is the class the row names. The row says what 0 means. It does not
  promise 0 under drift.
- The author calls this "a reading, not a proof", which is fair. The sentence should quote the row or drop "promised".
- Smallest correction: quote `SKILL.md:888`. Say the stale state returned the declared exit 2, and that the gap is
  that drift was not caught before landing (KQ36).

### F10 LOW: the attempt-1 wording omits the errata's correction 1

- LOG.md:1637-1639: "Attempt 1 was stood down by the orchestrator for capacity."
- `errata-attempt-2.json` correction 1: attempt-1 files were still written after the stand-down time, including a
  complete 8-cell receipt (tool exit 0). The "cancelled mid-run" wording is unverified. The receipt is record-only.
  LOG does not mention the complete receipt.
- Smallest correction: add the errata's sentence to LOG 1637-1639.

### F11 LOW: "M17 kept on its round-23 line" reads as a line number

- LOG.md:1646: "M17 kept on its round-23 line". The docstring (`isolation-mutants.py:33`) says "keeps its round-23 line,
  not its round-23 kill".
- The anchor changed. The round-23 refusal was a one-line raise at `tools/report-landing-audit.py:170-172`. The
  tip guard is three lines at `:275-277` (`RevengerM17Sites.md` §4.1). "Line" means "check", but a reader will take
  it as a line number, and the number changed.
- Smallest correction: "M17 keeps the same refusal check; its anchor text was updated (the lookup() guard is now at :275-277)."

### F12 LOW: plain-English and private terms

Run-together words: none found (see holds item 16). Private terms, with the smallest plain replacement:

| Where | Term | Plain replacement |
|---|---|---|
| SCORECARD 1256 | lane branch tips | the commit each measurement ran at |
| SCORECARD 1260 | repair-first; stale 2; no promotion | fix-first; 2 entries no longer match; no score increase |
| SCORECARD 1261 | frontier K05; bound True | open question K05 (declared versus served context size); binding check True |
| SCORECARD 1267 | non-author critic seat | a reviewer who did not write the round |
| SCORECARD 1270 | SCORECARD/SHONEN (inside the verbatim quote) | keep the quote; gloss it outside: SHONEN.md is the file of inherited author assertions (`.ufo/reports/round-5/kama.md:53`) |
| SCORECARD 1272-1276 | re-derivation path; live SKILL registry row; closure decides the axis fit; relabel the axis | the command the row cites; the SKILL.md row; an outside review decides the axis; change the axis label |
| SCORECARD 1278-1281 | grid row F13; causal run; KQ36 | test case F13; a run at ed1cc3a that restores the old check; quality rule KQ36 |
| SCORECARD 1287 | lane-owned llama.cpp fixture (b11755); unregistered loopback ports; reaped; registered-consumer serving | test server built from llama.cpp release b11755 (commit 704366d76); free local ports not in the consumer registry; stopped and collected; serving for registered consumers |
| SCORECARD 1291-1295 | routed wording; unchanged-to-improved; discernment; closure; admission; stricter counters | wording fixes sent back by review; not changed or better; define or drop; outside review; accepted; stricter counting scripts |
| LOG 1637 | stood down | stopped |
| LOG 1646 | re-anchored; kept on its round-23 line | anchor text updated; same check kept |
| LOG 1652-1653 | K-cell; X1-X3 (fit); L1-L3 (concurrency) | define once: K1-K8 (one setting each), X1-X3 (fit tests), L1-L3 (two-request tests) |
| LOG 1661-1663 | round-20 wave rule; shared 2048 pool | round-20 sizing rule; one shared cache of 2048 tokens |
| LOG 1667 | Routed repairs | fixes from the round-24 spot-check |
| LOG 1674-1676 | seat file; zcat \| cmp | a helper agent's output file; decompress and compare |

## Residual risk and verification gaps

- The capability demonstration's first command was not run (F1). Its receipt was checked against the committed
  copy, not regenerated. The second command (the counter) was run.
- The C2 receipt was not regenerated. That needs a live llama-server, which this seat must not start.
- The C1 full run was not repeated (about 16 minutes). Byte identity with the 1fc41e34 replicate was checked instead.
- The `zcat | cmp` step in LOG 1674-1676 was not repeated, because the original file was removed. Decompressed size
  and sha256 were verified instead.
- "K05 deferred since round 10" (LOG 1652) was not traced beyond SCORECARD 254.
- The operability basis (F5) rests on a lane convention I could not find written down in the round text.
- The attempt-1 stand-down time comes from a session note (errata correction 1), not from the folder.

## Files written by this seat

Lane (allowed paths):
- `.ufo/waves/round-25/a2-falsify/advice/ReviewerScorecardLog.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerScorecardLog/checks.md`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerScorecardLog/census-validate-113-rows.out`
- Directories `.ufo/waves/round-25/a2-falsify/out/ReviewerScorecardLog/` and `advice/` (created if absent)

Scratch (`/fast/scratch/hyaku/kama-r25a2w2/ReviewerScorecardLog/`):
- `SCORECARD.md`, `LOG.md` (extracted from fa3b62ae)
- `receipt-fa3b62ae.json` (extracted from fa3b62ae)
- `census-validate.out` (first attempt; the script path was wrong, so the file holds a "command not found" error)
- `census-validate-now.out`, `census-validate-now.err` (read-only validate run)
- `clone/` (git clone at fa3b62ae; checkouts at efe58e96 and 1fc41e34 for the counting command)

Nothing was committed, pushed, or staged. No git write ran in the lane. No llama-server child was started.
No tools were installed or upgraded.
