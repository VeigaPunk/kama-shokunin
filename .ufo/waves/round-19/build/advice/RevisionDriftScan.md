VERDICT: partial - the revision check is real (3/3 registry rows verified, selftest ok 5 cases), but 609 of 635 lane-path citations in the four docs carry no revision, and 10 verified-ambiguous sites remain, including the round-18 defect-2 restatement sites.

Scope. Read-only scan of corpus/lessons/round-18.md, corpus/SOURCES.md, SCORECARD.md, LOG.md in /tmp/kama-r19-RevisionDriftScan (copy HEAD 8bf99ca; round-start tip 1b85a24 is an ancestor, so the tip moved one commit in-round). Copy status at copy time: 5 M and 6 untracked lane entries. This report is the only file written into the lane. Receipts: /tmp/kama-r19-RevisionDriftScan/out/ (top10.md, receipt.txt, verify2.txt, wt-summary.txt, suggested-check.json).

Counts (working tree). Lane-path occurrences 635 (anchored 416, resolved relative 203, glob 16). Revision within 40 characters: 26, of which 3 are machine-checked cite tokens. The 40-character test is a heuristic that over-counts in places. `python3 tools/citation-provenance.py --json` gives required=3 found=3 verified=3 missing=0 mismatch=0 (exit 0).

Top 10 ambiguous citations (line numbers; detail in out/top10.md)
1. SCORECARD.md:19, LOG.md:13, LOG.md:113-114, SOURCES.md:42 - tools/kama-probe.sh md5 1f81e859 / 932ea3dc / 61e82ee2 resolve to blobs ea72c3e / c6199a2 / 83bee7f. Current bytes (726f737, 1138 lines) match none of them. Verified by sha256/md5 over git show.
2. LOG.md:14 vs SCORECARD.md:19 - registry/endpoint-consumers.tsv: digest 87eb156b resolves to c6199a2 (42 lines); current 36 lines; the sites say "11 rows" and "3 rows".
3. SCORECARD.md:20; LOG.md:117-118 - tools/test-snapshot.sh md5 860f26ac resolves to 83bee7f (171 lines); current 194 lines; "RESULT pass=24" is unpinned.
4. SOURCES.md:53, :58; LOG.md:937, :1013, :1059; SCORECARD.md:611, :781 - tools/kama-llamacpp-live.py has six blobs; the cited tool digests resolve to 726f737 (b8c5e8d4) and 54a2926 (0efd1723). No path-only site names a commit.
5. round-18.md:362-363; SCORECARD.md:773-775; LOG.md:1126-1128 - "measured tree" / "that tip": runs/commands.json measured_commit is c6dc46f at 1c325b2, 101f3991 and eb78788b, and eb78788b only at HEAD. [INFERENCE] The lesson's harness commit and the field's implementation commit are conflated under one phrase.
6. round-18.md:396-401; SOURCES.md:217-221; SCORECARD.md:832 - runs/commands.json, live/ and live-recovery/ have revision-dependent existence: commands.json absent at c6dc46f (rc 128); live-recovery/receipt-1.json absent at 1c325b2 and eb78788b (rc 128), present at HEAD (rc 0).
7. SCORECARD.md:611, :781, :831; LOG.md:938, :1014, :1060 - tests/llamacpp-live/check-receipt.py: working tree M, 6 commits; the measured counts sit on bytes no commit holds.
8. SCORECARD.md:822-825; round-18.md:412-413; SOURCES.md:69 - tools/citation-provenance.py (ls-files --error-unmatch rc 1) and registry/required-citations.json are untracked (status ??). The C1 counter cannot be pinned to a commit.
9. SCORECARD.md:774-775; LOG.md:1087, :1126; SOURCES.md:67; round-18.md:156 - .ufo/waves/round-18/runs/run.py: working tree M, 3 commits; "32 commands, all expected exits" is tied to uncommitted driver bytes.
10. SCORECARD.md:126, :626; LOG.md:521, :559 - corpus/SOURCES.md: "30 opened" / "30 rows" vs "41 opened", no revision; file M with 14 commits.

Advice (not applied).
- Items 1-4: use the revision-qualified tokens in out/suggested-cites.md. All 9 verify (provenance on that registry: required 9, verified 9, exit 0). LOG.md:961 already has the right form: `20e392e:tools/kama-probe.sh`, sha256 93ee4302...cd64, which is the same blob as ea72c3e.
- Items 7-9: commit the files before citing their counts, and cite the commit that holds the bytes.
- Items 5-6: replace "tip" and "measured tree" with the explicit revision. Restate live/ vs live-recovery/ with cite tokens at round-18.md:396-401, SOURCES.md:217-221 and SCORECARD.md:832.
- Keep the 3-row registry scope for C1. Widening it to these sites is the next step and is not part of this claim.

Limits. Qualification is a 40-character heuristic. Digest-to-path attribution is line-local and misattributes on multi-path rows (SOURCES.md:42, :55, :59-60; SCORECARD.md:610); those rows are excluded from the list. tools/server/*, server.cpp and net/ipv6/* are upstream paths pinned by row URLs and are counted as lane paths by the scan. Only the copy was verified; the lane may have moved since the copy.

Commands (copy, exits observed). cp -a lane -> copy: 0. python3 out/scan.py --source wt: 0. --source head: 0. python3 out/verify.py: 0. python3 out/verify2.py: 0. python3 tools/citation-provenance.py --json: 0. --selftest: 0. python3 out/suggest_cites.py + provenance on out/suggested-registry.json: 0. wc -l on the four docs: 0. sha256sum on the four docs: 0. Installs: none.
