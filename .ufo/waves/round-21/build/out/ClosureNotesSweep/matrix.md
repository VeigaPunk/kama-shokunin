# ClosureNotesSweep — routed items named by kama closures R15–R20 vs lane

Lane tip checked: `a29bb84` (round-21 draft; lane HEAD unchanged since round-20 tip `7a6bc91`).
Fleet files read: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-20/kama.md`, `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md`, `/home/vgpnk/Projects/shokunin/MISSION.md`.
Evidence commands with exit codes: `checks.sh` → `evidence.txt` (same directory).
Status legend: RESOLVED (later artifact fixes it) · RESOLVED-BY-DISCLOSURE (append-only correction; original text kept by design) · OPEN · OPEN-DRAFT (fix exists only in unadmitted draft a29bb84) · DECLARED-OPEN (closure itself leaves it unclaimed/unrouted) · FLEET/OPERATOR (not lane-actionable) · PROBE-ANSWERED (seat advice only).

| ID | Closure | Routed item (short) | Status | Evidence (file:line / commit) |
|---|---|---|---|---|
| R15-01 | R15 | Search/execution discipline; process incidents (historical-session grep, scribe guard eval, AST parse) | OPEN | Recurred: round-16.md:169-170 (M6/M7); round-17.md:90 "still no mechanical guard"; no R18–R20 lesson/SCORECARD/LOG record of a mechanical guard (evidence.txt: round-16/17 lesson rows) |
| R15-02 | R15 | Dispatch provenance: environment bindings; refused-attempt payload identity/timing | RESOLVED | Env bindings: round-16.md:82-84 (validation.json records argv, cwd, 3 env bindings, taskCall digest; b8e485c). Refusal prose: round-18.md:91 (M5, provenance selftest 30/30). Historical R15 refused payload stays uncertified (round-15-verifier-spotcheck.md:168) |
| R15-03 | R15 | Replay prose "before the minimum-unique check" precision | RESOLVED | corpus/knowledge/ollama-evidence-replay.md:376-381 (appended round 16; b8e485c) |
| R15-04 | R15 | S012 cross-source synthesis wording | RESOLVED | corpus/SOURCES.md:147-151 (synthesis note; b8e485c) |
| R15-05 | R15 | Prior R1 duplicate-corpus guard (closure says resolved at R15) | RESOLVED | QUALITY.md:87-90 (KQ18); README.md:188-192 (runnable check named). [INFERENCE: check not re-executed here] |
| R15-06 | R15 | Prior R2 partial-output attribution (closure says resolved) | RESOLVED | round-15-verifier-spotcheck.md:166 (closure-stated). [INFERENCE: not re-verified] |
| R15-07 | R15 | Validation argv lacks environment bindings (R15 caveat) | RESOLVED | Same artifact as R15-02: round-16.md:82-84 |
| R16-01 | R16 | Wave provenance: policy block in validation.json; taskCall canonicalization; falsify spawned:0 for 79 | RESOLVED | round-17.md:95-99 (every R17 wave has validation.json with policy; ensure_ascii=False); round-17.md:88 (M4 dispatch-provenance.py). R16 digest cdf02ba7 declared "as recorded" (round-17.md:98-99) |
| R16-02 | R16 | Falsify verdict_first_lines 36/41/2 vs committed | RESOLVED | round-17.md:100-105 corrected to 34/40/0/5. Recount this round: 34 confirm / 40 partial / 0 refute / 5 NONCONFORMANT (evidence.txt "R16 falsify first-line VERDICT distribution") |
| R16-03 | R16 | S041 anchor/teaches amended in place after b8e485c (SOURCES rule 2) | RESOLVED-BY-DISCLOSURE | round-17.md:85 (M1; old values recorded), :106-107 ("S041 is left as committed"); tools/sources-append-only.py tracked (evidence.txt) |
| R16-04 | R16 | "every non-frontend path" overstates (OPTIONS bypasses gate, server-http.cpp:347-352); S036 cell | RESOLVED | Appended corrections: corpus/README.md:230-232; SKILL.md:555-556; knowledge/endpoint-identity.md:218; knowledge/runtime-health-surface-matrix.md:77; knowledge/llamacpp-loading-lifecycle.md:204-207; SOURCES.md:153-160 |
| R16-05 | R16 | Retained tarball unnamed in L0 (b); PATH link shadows nothing | OPEN | Fleet .ufo/l0-questions.md:68 raw line has no ANSWER (ANSWER markers only at :52-53). Host facts verified: archive present 22,240,468 B (exit 0); /usr/bin/llama-server absent (exit 1); ~/.local/bin/llama-server -> ~/.local/opt/llama-b11755/llama-server |
| R16-06 | R16 | Carried check.py mutants, served_model, route match, weak live checks, teardown escape | RESOLVED | SCORECARD.md:680-681 (fixed-detector accepted 0/8; mutant grid 10/10). [INFERENCE: closure-stated, not re-run] |
| R16-07 | R16 | M3 harness shutdown() design gap (round-16 M3) | OPEN | SCORECARD.md:705-706 names it as next move (R17); no R18–R20 record (grep "shutdown()" finds only that line) |
| R16-09 | R16 | Matrix why-line numbers; one duplicate equivalence class; frozen-manifest prior-exposure field | OPEN | SCORECARD.md:707-708 ("wait for a round that re-pins the matrix digest"), :735 (prior-exposure field); dropped from R18 plan at SCORECARD.md:799-807 |
| R16-10 | R16 | Open L0: round-16 fixture ratification (fleet .ufo/l0-questions.md:58) | OPEN | Fleet L0 :58 raw has no answer; ANSWER markers only :52-53 (evidence.txt) |
| R16-11 | R16 | SHONEN four [~] remain author assertions | FLEET/OPERATOR | SHONEN.md:5,7,9,11 `[~]` (4 counted, evidence.txt); promotion operator-owned |
| R17-01 | R17 | S047 lacks Gate row (CORPUS SOURCES rule 1) | RESOLVED | corpus/lessons/round-18.md:35-37 ("Existing S047 receives its missing Gate row here"); row at round-18.md:41-42 |
| R17-02 | R17 | M8 has no QUALITY criterion | RESOLVED | corpus/QUALITY.md:127-128 (KQ23; first commit c6dc46f) |
| R17-03 | R17 | corpus/README.md:238 attributes exit statuses to S043 only | OPEN | README.md:238 unchanged ("exit statuses (S043)", no S047); correction block README.md:230-232 covers OPTIONS only (evidence.txt) |
| R17-04 | R17 | Zero-observation loading should be could-not-evaluate exit 2 (C2 exit classification) | RESOLVED | tests/llamacpp-live/controls.py:633-637 (zero-loading expects tool exit 2 / gate exit 3 NOT-EVALUATED); check-receipt.py:33-34 exit map; first commit c6dc46f. Routed text said gate exit 2; implemented gate exit 3 (KQ24) |
| R17-05 | R17 | Six v2 checks lack retained bad controls | RESOLVED | tests/llamacpp-live/controls.py:18-21 (k9–k14: models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch); first commit c6dc46f |
| R17-06a | R17 | Receipt gate: v1 self-declare | OPEN | round-18.md:93 (M7: "v1/v2 unchanged"); v3 schema floor only |
| R17-06b | R17 | Receipt gate: extra argv flags validate | RESOLVED | tests/llamacpp-live/check-receipt.py:609-613 (exact argv re-derivation for v3) |
| R17-06c | R17 | Receipt gate: non-exact 503 in transitions | RESOLVED | check-receipt.py:631-690 (transition-body grading, producer routes only) |
| R17-06d | R17 | ::1 / IPv4-mapped loopback listener ownership | RESOLVED | tools/kama-llamacpp-live.py:376-378 (native ::1 and mapped 127/8); knowledge/loopback-listener-ownership.md:41-43 (v3 parser corrects false negative) |
| R17-06e | R17 | BaseException / epilogue faults escape without receipt | RESOLVED | tools/kama-llamacpp-live.py: 20 `except BaseException` sites (e.g. :929, :1480-1527); controls.py:652-656 (k18); first commit c6dc46f |
| R17-06f | R17 | K6 accepts any nonzero exit | RESOLVED | controls.py:18 ("k6 now needs tool exit 2") |
| R17-06g | R17 | Python docs citation /3/ | RESOLVED | tools/kama-llamacpp-live.py:59-61 now docs.python.org/3.14/...; count of "docs.python.org/3/" = 0 (evidence.txt) |
| R17-07a | R17 | Detector-of-detector survivors: GateCaptureHashes M1–M4 and fresh mutants | OPEN | round-18.md:288-296 ("deferred as named debt"); SCORECARD.md:799-802 (planned); no R19–R20 closure (grep) |
| R17-07b | R17 | refused:0 provenance | RESOLVED | round-18.md:91 (M5: frozen refused 0 -> repaired 82) |
| R17-07c | R17 | Seven dead falsify seats not respawned | OPEN | corpus/lessons/round-17-verifier-spotcheck.md:255-258 names C1AdmissionCritic, C2AdmissionCritic, C2SourcedClaim, ControlsSafety, MistakesFailCapable, SeparabilityNoHarm, TrendVerdicts ("attacks remain undone"); no re-run record in R18–R20 |
| R17-08 | R17 | Prompt role->alias route map vs MISSION.md buckets (connector, critic/sentinel) | FLEET/OPERATOR | MISSION.md:62-65 (planner/connector heavy-reasoning; reviewer/critic/sentinel economy); fleet .ufo/l0-questions.md:57 records orchestrator-supplied overrides (connector->m_haiku, critic->m_opus); no lane-side reconciliation. [INFERENCE: mapping not verifiable from lane] |
| R18-01 | R18 | Residual verdict miscount: "five confirm, two partial" (round-18.md:316-318; LOG.md:1122) | RESOLVED-BY-DISCLOSURE | corpus/lessons/round-18.md:387-394 (erratum: 4 confirm / 3 partial); LOG.md:1167-1169; commit 7229fa9. Original text kept |
| R18-02 | R18 | S055 anchor / Gate-row pointers drift (round-18.md:53) | RESOLVED-BY-DISCLOSURE | corpus/SOURCES.md:225-229 (S055 qualification); round-18.md:395-423 (erratum, cite() tokens); registry check 17/17 verified (evidence.txt); commit 7229fa9 |
| R18-03 | R18 | SCORECARD:755 `--out PATH` vs official `--json` | RESOLVED-BY-DISCLOSURE | SCORECARD.md:809-813 (append-only erratum); round-18.md:403-408; commit 7229fa9 |
| R18-04 | R18 | Residual 6 reviewer / 1 critic split ungrounded | OPEN | round-18.md:441-445 (retrospective roster; "asserted 6/1 role split still lacks independent dispatch evidence"); assignments.PROVENANCE.md tracked (33a6777) |
| R18-05a | R18 | Install-tree residual ("1 of 51" unpinned) | RESOLVED | Sixth pin `--expect-install-tree-sha256`: SKILL.md:654; commit 7229fa9; R19 closure rechecks 51 members = 6c216313 |
| R18-05b | R18 | TreeCap: symlinked soname identity not pinned | OPEN-DRAFT | Lane tip: SCORECARD.md:921 retains it as frontier. Draft a29bb84 adds install_links() at tools/kama-llamacpp-live.py:205-226 (unadmitted). Its own `except OSError: continue` (:222-223) silently skips unreadable links |
| R18-05c | R18 | C2 selftest-arm enumeration | RESOLVED | SKILL.md:656 (round20 arm fixtures isolate early abort vs complete target failure); round-20.md:76 (M2) |
| R18-05d | R18 | Detector-self mutant (b) denominator | DECLARED-OPEN | SCORECARD.md:785-786 (named and excluded with reason); round-18.md:351-353 (counter does not implement comparison shape) |
| R18-05e | R18 | GateCaptureHashes M1–M4 (named gate leaves) | OPEN | round-18.md:288-291; SCORECARD.md:800 (planned); no closure in R19–R20 |
| R18-05f | R18 | Fresh-mutant survivors: FreshGate, FreshControls, FreshAppend, FaultF0, FaultTarget, GateLoadingTransitions, GateModelsStatus, GateNullLicense, AppendCells | OPEN | round-18.md:291-296; SCORECARD.md:800-802; no R19–R20 closure (grep) |
| R18-06 | R18 | 10 dead falsify seats not respawned (R18 wave) | DECLARED-OPEN | round-18.md:257-259 ("stay dead — not respawned") |
| R19-01 | R19 | citation-provenance.py and install-tree-grid.py unregistered in SKILL.md | RESOLVED | SKILL.md:652-653 (commit 33a6777) |
| R19-02 | R19 | r19 census receipts uncommitted (report cites r18 paths) | RESOLVED | .ufo/waves/round-19/sources/census-{before,after}.txt tracked, first commit 33a6777; LOG.md:1190-1192 labels them retrospective |
| R19-03 | R19 | Stale C1 counts (required=3 / three rows) in SCORECARD, LOG, errata, lesson-19 | RESOLVED-BY-DISCLOSURE | SCORECARD.md:853-859 and LOG.md:1176-1181 (appended corrections, commit 33a6777). Stale lines kept; original evidence file .ufo/waves/round-19/evidence/final-selftests.txt still prints required=3 |
| R19-04 | R19 | "falsify-wave refutation" mislabel (falsify spawned 0/66) | RESOLVED-BY-DISCLOSURE | corpus/lessons/round-19.md:109-114 (appended); SCORECARD.md:860-861 (33a6777) |
| R19-05 | R19 | round-18.md:42 rewritten in place (30ed378) | RESOLVED-BY-DISCLOSURE | corpus/lessons/round-18.md:425-441 (named correction quoting original wording; 33a6777); LOG.md:1188-1189 |
| R19-06 | R19 | final-selftests on dirty worktree 5b108c1a; 76 vs 77 mutations | RESOLVED | Clean-commit rerun .ufo/waves/round-20/build/out/SelftestsAtCommit/final-selftests-37bd4c5b.txt (tracked); SKILL.md:654 ("77 ... not 76"); LOG.md:1190-1192. Original file kept (f1790e2) |
| R19-07 | R19 | residual/assignments.json retrospective unlabeled | RESOLVED | .ufo/waves/round-18/residual/assignments.PROVENANCE.md (33a6777); round-18.md:441-445 |
| R19-08a | R19 | grid: exit 1 without INVALID line still counts as rejected (install-tree-grid.py:110) | RESOLVED | tests/llamacpp-live/install-tree-grid.py:85-91 (rejected only on exit 1 + stdout "INVALID "); selftest cases :266-280; commit 33a6777 |
| R19-08b | R19 | Checker observed-branch selftest gap | RESOLVED | tools/citation-provenance.py:301-302 (observed-digest branch); `--selftest` printed "ok (24 cases)" exit 0 (evidence.txt); commit 33a6777 |
| R19-08c | R19 | 13 unregistered round-18 citations | RESOLVED | registry/required-citations.json: 17 rows, 13 r18-*; `citation-provenance.py` required=17 verified=17 exit 0 (evidence.txt); commit 33a6777 |
| R19-08d | R19 | c2-survivors verdict-level-only agreement (whole output not compared) | DECLARED-OPEN | corpus/lessons/round-20.md:81 (R20 did not rerun the full 42-run counter; routed to R18 comparison) |
| R19-08e | R19 | S051 line anchor after S057 insertion | RESOLVED | round-18.md:447-451 (heading-based qualification); SOURCES.md:218-223 (current clarification); round-20.md:206-209 |
| R19-08g | R19 | TreeDeterminism (install_tree digest determinism) | PROBE-ANSWERED | .ufo/waves/round-19/build/advice/TreeDeterminism.md:1 "VERDICT: confirm" (deterministic over 20 repeats). Advice file only; not recorded in lane SCORECARD |
| R19-08h | R19 | GridDefaults: producer silently drops unreadable members | OPEN | tools/kama-llamacpp-live.py:191-199 (`except OSError: continue`); carried in .ufo/waves/round-20/build/advice/RegReceiptSixPin.md:59 |
| R19-08i | R19 | SentinalSecrets: round-18 runner hard-codes lane root and writes into the lane | OPEN | .ufo/waves/round-18/runs/run.py:5 (`L=Path('/home/vgpnk/Projects/shokunin/kama-shokunin')`); remediation in .ufo/waves/round-19/build/advice/SentinalSecrets.md:11 not applied; R20 plan row 7f (SpotcheckR19Map.md:18) names it with no completion record |
| R19-08j | R19 | SCORECARD §Planned leaves (carried) | OPEN | SCORECARD.md:919-922 retains: crash-as-kill leaves outside 15-cell set; receipt-header minimization; symlinked soname identity; K05/other-engine serving evidence |
| R19-09 | R19 | Operator housekeeping: ~5.95 GiB /tmp/kama-r19-* scratch | RESOLVED | LOG.md:1193-1196 (removed); `compgen -G '/tmp/kama-r19-*'` exit 1 = none (evidence.txt) |
| R20-D1 | R20 | Report :7 cites unresolvable full hash 0957ce619789d13d894ef21bc863486bcb35b56c (correct one at :10) | OPEN-DRAFT | Fleet report line 7 still has the bad hash; `git cat-file -e` exit 1 in lane and fleet; correct hash exit 0; report blob sha256 = working tree; fleet log: one commit (04eb5d2). Draft errata row registry/report-landing-errata.tsv:3 (unadmitted). Byte split of the bad hash is 15+25 (errata text says 16+24) |
| R20-D2 | R20 | Landed changes lists 5 commits, omits 33a6777, 0957ce6, 92b1462, 846e366 | OPEN-DRAFT | Fleet report lines 13-19 list 5 commits (c7311039, 04de7a8, 9add96e, 3ec5ea6, 7a6bc91); draft errata rows :4-7 (unadmitted); report unchanged |
| R20-L0 | R20 | L0 kama round-17 llama archive question still open | OPEN | Fleet .ufo/l0-questions.md:68 raw line, no ANSWER (same question as R16-05) |
| R20-timeout | R20 | Timeout-reason precision unclaimed (2 diagnostic survivors; class boundary intact) | DECLARED-OPEN | corpus/lessons/round-20.md:189 ("No claim about diagnostic-reason equivalence is made"); LOG.md:1241 |
| R20-v3 | R20 | v3-all-scalars 12 test.* values not individually compared | DECLARED-OPEN | corpus/lessons/round-20.md:188 (outside declared selected-key claim) |

Totals (66 rows, recounted by grep in this round): RESOLVED 32 + RESOLVED-BY-DISCLOSURE 7 = 39 resolved; OPEN 16; OPEN-DRAFT 3; DECLARED-OPEN 5; FLEET/OPERATOR 2; PROBE-ANSWERED 1.
Counting: `checks_extra.sh` (grep -c over the status cells; output in `evidence_extra.txt`). Lane evidence: `checks.sh` -> `evidence.txt`.

Observed in draft a29bb84 (not closure-named; for L1 integration; unadmitted):
- O1: install_links() silent skip (tools/kama-llamacpp-live.py:222-223) — same silent-subset class as GridDefaults.
- O2: tests/llamacpp-live/install-links-grid.py and --expect-install-links-sha256 have no SKILL.md row (`git show a29bb84:SKILL.md | grep -c install-links` = 0, exit 1); SKILL.md is not in the draft's diffstat.
- O3: errata row 3 text splits the bad hash as "first 16 hex of 0957ce61 + last 24 hex of 33a67778"; bytes split 15+25 (evidence.txt splice step).
- O4: draft errata also adds landed omissions for round-18 (3 rows) and round-10 (1 row), which no closure named.
