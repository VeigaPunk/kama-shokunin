VERDICT: partial - the three round-19 cite tokens and registry rows verify, but lesson:419 (and registry gate-live-1) pins pre-run bytes that contradict its own claim, and bare pointers into replaced runs/ and docs remain.

Scope: 101f3991 -> 1b85a24 (commits 0c75c61, 888cd38, eb78788, 1b85a24). Lane untouched except this file. Full findings and receipts: /tmp/kama-r19-RevOverwrites/out/ (REPORT.md, RECEIPT.md, classified-inventory.tsv).

Overwritten in place
- 44 changed paths: 31 M, 13 A; no D/R/T/C. 26 M lose lines: 20 written by runs/run.py, 1 by a non-run.py writer (runs/c2-survivors.json), 5 code/harness files. 5 M are pure appends.
- 80 more run.py targets were rewritten with identical bytes (invisible to the diff).
- Not overwritten: live/receipt-{1,2,3}.json (run.py writes live-recovery/). The only in-tree pre-run copy is runs/pre-repair/c2-survivors.json.
- Exit flips: c1-measure.exit and c2-survivors.exit go 2 -> 0.

Citations still pointing at a replaced path
1. corpus/lessons/round-18.md:419 (uncommitted) and registry gate-live-1: cite(eb78788, runs/live-gate-1.stdout, b2043ba8...) is attached to "the recovery output describes live-recovery/". WRONG-REV: eb78788 bytes name live/receipt-1.json. Use cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7).
2. corpus/lessons/round-18.md:53 (bare): runs/live-gate-1.stdout cited as the gate for live/receipt-1.json. STALE: the file now names live-recovery/. Not fixed in round 19.
3. corpus/lessons/round-18.md:156-160 (bare): "30 met their declared exits ... retained under runs/". STALE: runs/commands.json at 1b85a24 is 32/32. Not fixed in round 19.
4. corpus/SOURCES.md:67 S055 cell (bare): commands at measured c6dc46f in round-18/runs/commands.json. STALE: that file is absent at c6dc46f (exit 128); the tip measured eb78788. The appended note at :217-221 says "No cell rewritten".
5. corpus/knowledge/llamacpp-loading-lifecycle.md:266-268 (bare, appended 0c75c61): runs/commands.json, measured production commit c6dc46f. STALE: tip measured_commit is eb78788.
6. LOG.md:1087-1090 (bare, c6dc46f-era entry): 30 expected outputs "in runs/". STALE: runs/ is the eb78788 run.
7. SKILL.md:630-631 (bare): 61 mutations (runs/gate-selftest.stdout). STALE: the file now says 72 (61 at 101f3991).
8. SCORECARD.md:790-791 (bare): the exit-2 pass is "historical and not overwritten". PARTLY FALSE: its exit, stdout and stderr were overwritten; only the JSON survives under runs/pre-repair/.
9. SCORECARD.md:809-813 (round-19 erratum), corpus/lessons/round-18.md:407-408, round-18-verifier-spotcheck.md:141-142: runs/c2-survivors.json "they agree". TRUE on outcomes (counts and all results equal), FALSE on bytes (sha 8cc59a65 vs ea2e3e02; started 04:08:39Z vs 05:11:40Z; byte-identical at 101f3991). Qualify the wording.

Historical, not routed: 67 files under .ufo/waves/round-18/{build,falsify,residual}/advice cite replaced basenames. Examples: residual/advice/ResidClaims.md:8 (E1 pair 32/32 + measured 101f3991 matches no committed revision) and :16 (line 1420 exists only at 101f3991).

Checked, not stale: cite tokens at lesson:417 (1c325b2) and :421 (1b85a24); registry s055-commands and c2-official-stdout (all match); loopback-listener-ownership.md:107 (tools lines 311-321 unchanged); lesson:308 (rev named in prose, exit=2 at 101f3991); eb78788-era SCORECARD 774-782 pointers resolve to the 1b85a24 run (C1 5->0, 1->0, 1->0, 0->0; gate 16->17; faults []; exit 0; live-gate-1..3 VALID on live-recovery).

Not fixed in the round-19 working tree (confirmed by git diff -U0 HEAD, hunks only at SCORECARD 808+, SOURCES 69 and 216+, lesson 386+): lesson 53, lesson 156-160, SOURCES 67, knowledge 266-268, LOG 1087-1090, SKILL 630-631.

Installs: none. Listeners started: none. Limits: commit-level scope as assigned; round-19 seat advice only grep-checked for cite tokens; upstream URL sha pins not checked (offline).
