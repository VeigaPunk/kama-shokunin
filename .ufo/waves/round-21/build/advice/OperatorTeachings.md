VERDICT: partial - two operator items are unreflected in QUALITY/SKILL (L0:52 closure rule; SKILL live-fixture section lacks the L0-ratification caveat); corpus/lessons/operator-*.md does not exist; all other items are reflected, resolved, superseded, or operator-owned.

Scope: corpus/lessons/operator-*.md (none, E3); considerthese/2026-10-19.md and 2026-10-20.md (every item); .ufo/l0-questions.md `kama |` lines (10). Read-only; the lane was not modified. Draft a29bb84 equals the lane tree for corpus/QUALITY.md, SKILL.md and considerthese/2026-10-20.md (E4). QUALITY.md read in full; SKILL.md by heading list, keyword sweeps and targeted ranges, so "reflected" verdicts rest on grep hits unless marked [INFERENCE]. Commands and exits: out/OperatorTeachings/evidence.txt (E1-E17). Installs/updates: none.

## A. Round 21 should ACT
A1 Operator answer on L0:52 (planner seat + closure rule), not reflected operationally. Quote: "spot-checks ≥1 admit and ≥1 reject after each landed round". Pointers: .ufo/l0-questions.md:52-53; fleet scripts/hyaku/lane-addendum.md:67-70. QUALITY.md:17-18 gives only a generic "non-author admit/reject review" sentence. ACT: the report records the planner→L1 mapping and names one admit and one reject per claim (C1: clean report vs defective-hash fixture; C2: baseline grid vs link-retarget cell). The answer's "§6.2" matches no literal in lane-addendum.md (E13).
A2 Live llama.cpp fixture: L0:58 open, no answer (E5). PROVINCE.md:61-63, 72, 82 say "pending L0 ratification"; SKILL.md:533-546 states no caveat (no "ratif" in SKILL/QUALITY). ACT: keep C2 non-live (it is); append one dated pointer line under SKILL §Round-16 (doc-only).
A3 Landed-commit completeness has no QUALITY row. Round-20 report line 7 cites 0957ce619789d13d894ef21bc863486bcb35b56c (no object, exit 128); line 10 cites 0957ce619789d13bb5779606078fa1498114d2c7 (commit, exit 0) (E10). Assignment-stated defect, verified. KQ26 (QUALITY.md:143) and KQ27 (:144) do not cover it. ACT via C1 measurement only; propose a KQ28 row after C1 is measured, since KQ27 requires counts tied to the measured revision. No row now.
A4 operator-*.md convention: lane-addendum.md:236-239 says "honor any corpus/lessons/operator-*.md teaching not yet reflected"; zero such files (E3). ACT (optional, doc only): record the L0:52 answer as a dated corpus/lessons/operator-*.md so the rule has a file to honor.
A5 C2 exit-code credit: install-links-grid.py:275 checks a bare rc == 1 ("combined-exit-1-because-frozen"); JSON checks at :264-274 corroborate it (E16). QUALITY KQ25 (:142) rejects exit-1-alone credit. ACT: C2 closure credits only JSON-graded arms. [INFERENCE: an uncaught Python exception also exits 1.]

## B. Reflected, resolved or superseded: no action
B1 L0:17 fleet .gitignore omitted kama-shokunin: now fleet .gitignore:1 is `*-shokunin/`; check-ignore exit 0 (E7). Resolved; integrator may close the L0 line.
B2 considerthese 2026-10-19:9 (interactive noise): lane .gitignore:1; commit 6978097 (E8).
B3 considerthese 2026-10-19:7 and :17 (scaffolds ≠ progress; Capabilities template): SCORECARD.md:122-128 and :621-628 hold three rows (r10, r14, r16). The :17 template is superseded.
B4 considerthese 2026-10-20:9-10 (fail-capable controls): QUALITY KQ17 :72, KQ18 :87, KQ20-21 :121-122, KQ25 :142.
B5 considerthese 2026-10-20:12-13 (provenance by appending): QUALITY KQ6-7 :28-29, KQ14 :41, KQ22 :123, KQ26 :143; SKILL.md:344.
B6 considerthese 2026-10-20:24 (stagnation tracker): already in SCORECARD.md:630-631 (also :696, :766).
B7 L0:31 axis authority: shokunin.conf:52 says "operability + calibration"; QUALITY KQ12 :39; SCORECARD.md:226-228. Only the namespace half remains (D5).
B8 L0:13, 15, 41 endpoint boundary: SKILL.md:33-48, 103-120, 130-134, 214-219; QUALITY KQ1-5 :9-13. Decisions remain operator-owned (D2).
B9 L0:21 timer: SKILL.md:231 ("No timer is installed"); QUALITY KQ5 :13. Decision remains operator-owned (D3).
B10 Round-19 routed defects #1 (register gates) and #5 (77 mutations): SKILL.md:652-654.
B11 considerthese 2026-10-19:11 (README/PR entrypoint): not QUALITY/SKILL material; no action.

## C. Defer or operator-owned: no round-21 action
D1 L0:68 release-archive keep/remove: open; PROVINCE.md:78-80 records it as operator-owned. Do not touch ~/.local/opt.
D2 L0:13, 15, 41 repoint, restore or retire endpoints: open; KQ5 (:13) makes it an operator handoff. SKILL.md:44-48 says no restoration implied.
D3 L0:21 systemd timer decision: open; operator-owned.
D4 L0:15 item (2), declared-vs-served context (janitor 32768 vs served 16384): not a reflected check; SKILL.md:188-189 documents only 16384 as normal. Candidate for a future claim; config reads sit inside KQ5.
D5 L0:31 relaunch counter and round namespace: operator-side.
D6 L0:48 glm wire id absent from host catalog: open; host-owned routing; never name models (round bounds).
D7 considerthese 2026-10-19:19 (served-id empty-normalization fixtures): the rule exists (kama-probe.sh:46-48, 382, 540; SKILL.md:150), but 0 of 72 matrix rows expect unresolvable-id (E12). Adding rows changes the pinned matrix (SCORECARD.md:610; SKILL.md:534) [INFERENCE: changes the set digest], so it needs a claim-bearing round and a re-pin.
D8 considerthese 2026-10-19:21 (FOREIGN fingerprints): largely reflected (tests/probe-verdicts/ForeignControls.json; SKILL.md:169-182). Connection-reset absent from the matrix (E12). Defer.
D9 considerthese 2026-10-19:23 (inherited vs effective URL probe): conflicts with QUALITY KQ2 (:10) "Never inspect environment values to fill that gap in this run" and SKILL.md:44. Needs an operator amendment first; do not act.
D10 considerthese 2026-10-20:26 (promise-vs-test scan): KQ18 (:87) covers one runner only; no fleet scan. Defer.
D11 considerthese 2026-10-20:28 (routed-defect and seat-budget ledger): not in QUALITY/SKILL. Defer.
D12 considerthese 2026-10-20:15-16 (dispatch stop: probe one seat, identical failure = stop): not in QUALITY/SKILL; the note says it lives in lessons/round-10. Comply (no identical re-dispatch); no doc change required.
D13 considerthese 2026-10-20:22 (reflection window receipt): reflection process only.
D14 Round-19 spot-check item 7 (lines ~193-205): crash-as-rejection (install-tree-grid.py:110, per the note, not re-verified) and TreeCap follow-ups. C2 adds install-links-grid.py and does not touch install-tree-grid.py. Carried; name it in the closure.

## Not assessed
Non-`kama |` L0 lines (e.g., tsukuroi:54-61, mado:74) and round-19 spot-check items 2-6, 8-9.

## Evidence and tooling
E1-E17 in out/OperatorTeachings/evidence.txt. Key exits: ls operator-*.md 2; cmp x3 0; L0 scan 0 (10 kama lines); cat-file bad hash 128 / good hash 0; 17 of 17 considerthese citations 0; fleet check-ignore 0; probe matrix 72 rows, 0 unresolvable-id, exit 0; scratch removed (rm 0; test -d 1).
Tools installed or updated: none. Scratch /tmp/kama-r21-OperatorTeachings removed.
