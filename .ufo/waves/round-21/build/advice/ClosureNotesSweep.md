VERDICT: partial - 39 of 66 routed items named by kama R15–R20 closures are resolved; 16 open, 3 open only in unadmitted draft a29bb84, 5 declared-open limits, 2 fleet/operator-owned, 1 answered by seat advice only.

Scope: MANIFEST records with type closure and lane kama, rounds 15–20 (one record each; commits 20e392ea, cff9e62f, 5e9ae6e, 1b85a24, 3389513f, 7a6bc911). Each routed item in their notes/rechecks was checked against lane HEAD a29bb84 (round-21 draft; no tracked lane file changed by this sweep) and the fleet report/L0 files (read-only).
Full matrix (66 rows, file:line and commit per row): out/ClosureNotesSweep/matrix.md. Commands with exit codes: out/ClosureNotesSweep/evidence.txt (checks.sh) and evidence_extra.txt (checks_extra.sh).

## Open, with evidence (merged where one item recurs: R18-05e/f = R17-07a; R20-L0 = R16-05 L0 question; R19-08d = R20 42-run; 16 matrix rows)
1. R20-D1 [OPEN-DRAFT] fleet `.ufo/reports/round-20/kama.md:7` still cites 0957ce619789d13d894ef21bc863486bcb35b56c; `git cat-file -e` exit 1 in lane and fleet; the correct hash (:10) exits 0. Report blob unchanged since 04eb5d2. Fix exists only as errata row `registry/report-landing-errata.tsv:3` in a29bb84 (unadmitted).
2. R20-D2 [OPEN-DRAFT] report `## Landed changes` (:13–19) lists 5 of 9 round-20 commits; 33a6777, 0957ce6, 92b1462, 846e366 absent. Errata rows :4–7 (unadmitted).
3. R16-05 + R20-L0 [OPEN] fleet `.ufo/l0-questions.md:68` (retained release archive `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`) has no answer. Host facts hold: `test -e /usr/bin/llama-server` exit 1; PATH link resolves to ~/.local/opt/llama-b11755/llama-server.
4. R16-10 [OPEN] fleet `.ufo/l0-questions.md:58` (fixture ratification) unanswered; ANSWER markers only at :52–53.
5. R17-03 [OPEN] `corpus/README.md:238` still attributes exit statuses to S043 alone; no S047 pointer; correction block :230–232 covers OPTIONS only.
6. R15-01 [OPEN] session-store grep recurred (round-16.md:169–170 M6/M7; round-17.md:90 "still no mechanical guard"); no R18–R20 record of a guard.
7. R16-07 [OPEN] M3 harness `shutdown()` design gap: named next move at SCORECARD.md:706; no later record.
8. R16-09 [OPEN] matrix why-line numbers, duplicate equivalence class, frozen-manifest prior-exposure field: SCORECARD.md:707–708, :735; dropped from R18 plan (:799–807).
9. R17-07a [OPEN] deferred detector survivors: GateCaptureHashes M1–M4 and nine fresh-mutant survivors (round-18.md:288–296; SCORECARD.md:799–802); no R19–R20 closure.
10. R17-07c [OPEN] seven R17 falsify seats never re-run (corpus/lessons/round-17-verifier-spotcheck.md:255–258).
11. R17-06a [OPEN] v1/v2 receipts still self-declare; "v1/v2 unchanged" (round-18.md:93).
12. R18-04 [OPEN] residual 6 reviewer / 1 critic split: disclosed as retrospective (round-18.md:441–445), still no dispatch evidence.
13. R18-05b / TreeCap [OPEN-DRAFT] symlinked soname identity unpinned at lane tip (SCORECARD.md:921). Draft install_links() (tools/kama-llamacpp-live.py:205–226) addresses it; unadmitted.
14. R19-08h [OPEN] GridDefaults: producer silently drops unreadable members (tools/kama-llamacpp-live.py:191–199; RegReceiptSixPin.md:59 carries it).
15. R19-08i [OPEN] SentinalSecrets: `.ufo/waves/round-18/runs/run.py:5` hard-codes `/home/vgpnk/Projects/shokunin/kama-shokunin`; advice remediation (SentinalSecrets.md:11) not applied.
16. R19-08j [OPEN] SCORECARD §Planned leaves retained (SCORECARD.md:919–922: crash-as-kill leaves, receipt-header minimization, symlinked soname, K05).
17. R16-11 SHONEN [FLEET/OPERATOR] four `[~]` boxes (SHONEN.md:5,7,9,11). R17-08 route map [FLEET/OPERATOR]: MISSION.md:62–65 buckets vs orchestrator overrides at fleet L0:57; not verifiable from the lane [INFERENCE].

## Declared open (closure leaves unclaimed; not routed as fixes)
R18-05d mutant (b) denominator (SCORECARD.md:785–786; round-18.md:351–353). R18-06 ten dead R18 falsify seats (round-18.md:257–259). R19-08d/R20: c2-survivors whole-output agreement; 42-run counter not rerun (round-20.md:81). R20 timeout-reason precision (round-20.md:189; LOG.md:1241). R20 v3-all-scalars (round-20.md:188).

## Resolved (39; examples with commit)
- R18 residual miscount, S055 pointers, SCORECARD:755: appended errata in 7229fa9 (round-18.md:387–423; SOURCES.md:225–229; SCORECARD.md:809–813).
- R19 stale counts, falsify-label, line-42 rewrite, residual provenance, dirty-tree selftests, scratch removal: appended corrections and clean rerun in 33a6777 (SCORECARD.md:853–863; round-18.md:425–445; round-19.md:109–114; LOG.md:1176–1196).
- R19 unregistered tools (SKILL.md:652–653); 13 unregistered citations (registry 4→17; citation-provenance required=17 verified=17 exit 0); grid INVALID-only kill (install-tree-grid.py:85–91); observed-digest selftest (citation-provenance.py:301–302); S051 anchor (round-18.md:447–451).
- R17 zero-loading (controls.py:633–637; tool exit 2, gate exit 3 NOT-EVALUATED); six v2 controls (controls.py:18–21, first commit c6dc46f); exact argv (check-receipt.py:609–613); transitions (:631–690); ::1 ownership; BaseException guards; K6; /3/ docs (kama-llamacpp-live.py:59–61); refused:0 (round-18.md:91).
- R16 verdict counts (recount 34/40/0/5 matches round-17.md:100–105); OPTIONS wording (five appended corrections); S041 (round-17.md:85, guard tools/sources-append-only.py).
- R15 replay precision and S012 note (ollama-evidence-replay.md:376–381; SOURCES.md:147–151); env bindings (round-16.md:82–84).

## Draft a29bb84 notes for L1 (observed, unadmitted)
- Errata row 3 evidence text says "16 hex + 24 hex"; bytes split 15+25 (cut -c1-15 and -c16-40 match, evidence.txt splice step).
- install_links() silently skips unreadable links (tools/kama-llamacpp-live.py:222–223), the same silent-subset class as GridDefaults.
- install-links-grid.py and --expect-install-links-sha256 have no SKILL.md row (count 0, exit 1; SKILL.md not in the diffstat).
- Errata also records round-18 (3) and round-10 (1) landed omissions that no closure named.

## Method, limits, installs
- Read-only throughout (git show/cat-file/log, file reads). citation-provenance ran in scratch clone /tmp/kama-r21-ClosureNotesSweep/lane at a29bb84 (exit 0; selftest exit 0), deleted after the run.
- Not executed: lane gates, live llama.cpp, the 42-run counter. Closure-stated items R15-05/R15-06 are not re-verified [INFERENCE].
- Installs/updates: none (jq and python3 already present, exit 0). Lane writes: new files only under .ufo/waves/round-21/build/{advice,out/ClosureNotesSweep}/.
- Lane working tree (`git --no-optional-locks status --porcelain`) shows ` M tools/report-landing-audit.py`: uncommitted, not made by this sweep, left untouched. All evidence reads committed a29bb84 blobs.
- Scratch clone deleted (74 MB). citation-provenance steps in checks.sh need a fresh clone at a29bb84 to rerun.
