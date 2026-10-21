VERDICT: refute - "uncorrected 9 -> 0" is ledger bookkeeping (a ledger generated from the gate's own output exits 0); calibration 7->8 unsupported; detector-only claim survives
Scope: kama r21 C1; draft a29bb84 = lane HEAD = master; gate and ledger byte-identical to it. Read-only on lane and fleet; new files only under build/advice and build/out/C1ClaimCritic. Installs: none (python 3.14.8, git 2.56.0). Scratch removed. Gitignored tools/__pycache__ .pyc files (07:45-07:47) are not from this critic (scripts run, no lane imports).
Reproduce: `python3 .ufo/waves/round-21/build/out/C1ClaimCritic/c1_probes.py` exit 0, 25/25 expectations (probe-transcript.txt). Direct command exits: section 6.
## 1 What is real
- Raw reproduction: `--no-errata` exit 1, defects=9 over r10-r20 (r10 x1, r18 x3, r20 x5); 8 of 11 reports clean (P0).
- Five corroborated: non-author r20 closure D1 (hash at :7) and D2 (four omitted), "status-neutral, routed to kama r21" (MANIFEST.json:10112).
- Four template-backed, not closure-recorded: r10 4066035; r18 101f3991, 1c325b2, c6dc46f. The kama round prompt defines Landed changes as "every change tied to a LOG.md entry and to the commit hash that carries it" (kama-round-21.md:107-108); the gate checks only the hash half. r18 closure routed defects 1-5, none Landed (MANIFEST.json:9236); r10 closure notes silent (:5928). [INFERENCE: silence = omission]
- Controls fail as intended: lowercase bogus hash P7b; omitted commit P6; missing Landed heading P12a; unmatched ledger row P5a.
## 2 What is bookkeeping
- Ledger generated from `--json` (11 rows; correction = token or any commit) exits 0 (P12b). The match rule only requires copying detector output.
- Correction check = object exists: retargeting the r20 hash correction to unrelated commit 7a6bc91 exits 0 (P13). apply_errata checks only `is_object(...,"commit")` (tools/report-landing-audit.py:178-179); landed-section-missing is never checked (:54).
- Row 1 evidence is wrong: it says the token splices the first 16 hex of 0957ce61; they differ at hex position 16 (token ...d13d, commit ...d13b). Last 24 hex and SCORECARD.md:891 verify.
- Append-only unchecked: rewriting row evidence exits 0 (P14). Ledger and 404-line tool landed together in a29bb84; no baseline exists.
- Nothing repaired: r10, r18, r20 each have one commit in fleet history. The r20 bad hash and omissions remain in the fleet report, with no pointer to the ledger.
- Lane precedent: r10 report :119 "'uncorrected 0' only means every row has a correction appended"; :123 "Content correspondence is still checked by sampling, not by the script."
## 3 Falsifiability map
| Part | Status | Probe |
|---|---|---|
| Lowercase bad hash, missing section, omitted pre-report round commit | falsifiable | P6 P7b P12a P18a |
| Uppercase hash; `# Addendum` in Landed; amended commit; non-ancestor commit; tree object in prose | false negatives | P7a P9 P10 P18b P19 P17 |
| "NOT landed" mention inside Landed | presence-only (passes) | P11 |
| Numeric 7+ digit token; hex-letter prose word | false positives | P16 P8 |
| r21 pass | citations only; passes unsupported "7 -> 9" claim | P6 P5b |
| Population 10-20 | unjustified in code; r1-r9 add 10 raw (19 total) | P4 |
| Narrowed run, default ledger | exit 1; invites row deletion (breaks append-only) | P5a |
| Post-report exemption | r19 committed 0; same text as draft 4 (3389513, 464ea5a, 60e8fd8, 8d9191f; absent from r19 report) | P15a/b |
## 4 Calibration reading
- AXES.md:15: calibration = "SHONEN.md/SCORECARD entries match observed repo state." The gate reads fleet reports instead (scope mismatch; nearest on-axis artifact [INFERENCE]).
- Same instrument, same population: before→after 9→9 raw; reports unchanged; only ledger coverage moved. Lane precedent (r20 "improved 7->7", two-arm re-measure at MANIFEST.json:10107) needs a measured before→after; none here.
- n=1. With 8/11 clean reports, a clean r21 is expected (~73%) without improvement [INFERENCE]; likelihood ratio ~1.4.
- Calibration 8 = saturation line (SCORECARD.md:132), opening retire/split (AXES.md:37-38).
## 5 Strongest honest wording (calibration held at 7)
"C1 adds a citation-integrity detector for kama round reports (tools/report-landing-audit.py; selftest 15/15). Rounds 10-20: 9 raw findings reproduced (exit 1; 5 closure-corroborated, 4 template-backed and unrecorded by closures). All 9 are annotated in registry/report-landing-errata.tsv; no report was corrected, so the annotation is not a repair. Calibration stays 7 (delta 0). Not checked: claim content, SCORECARD/SHONEN entries, correction semantics, rounds 1-9 (10 further raw), post-report commits (r19: 4), ancestry, uppercase citations. Round 21: one draft passes the default population (n=1), not a trend."
## 6 Counting commands (exits observed)
- `python3 tools/report-landing-audit.py --no-errata` → 1, defects=9 (baseline, not 9→0)
- `python3 tools/report-landing-audit.py` → 0, corrected=9 (annotation coverage only)
- `python3 tools/report-landing-audit.py --rounds 1,2,4,6-20 --no-errata` → 1, defects=19 (disclose window)
- `python3 tools/report-landing-audit.py --selftest` → 0, cases=15 failed=0
- `python3 tools/report-landing-audit.py --rounds 10-21 --no-errata` → 2 (r21 absent)
- `python3 tools/report-landing-audit.py --rounds 21 --report 21=<draft>` → 1 with default ledger (errata_unmatched=9); `--no-errata` → 0
- `python3 tools/report-landing-audit.py --report 21=<draft>` → 0 (documented r21 gate)
- `git log --oneline -- .ufo/reports/round-{10,18,20}/kama.md | wc -l` → 1 each
- `python3 .ufo/waves/round-21/build/out/C1ClaimCritic/c1_probes.py` → 0 (25/25; known false negatives encoded as expectations)
- Next round, outside the tool: `git diff <prev-tip>..HEAD -- registry/report-landing-errata.tsv` shows only `+` lines.
## 7 Inadmissible if
- A 7→8 or "improved" cites exit 0, "uncorrected 0", 9→0, or the r21 pass as before→after.
- Ledger rows are authored from gate output without non-author checking of each correction and evidence (P12b, P13).
- The claim omits the window, the 10 out-of-window findings, the r19 post-report 4, or §3 false negatives; or claims SCORECARD/SHONEN coverage.
- Append-only is asserted without a base-revision diff (P14), or row 1's splice claim is repeated as accurate.
## 8 Smallest safe correction
(a) Reword per §5; hold 7; verdict "instrument added; findings annotated, not repaired". (b) Before any calibration move: default `--rounds` = all committed kama reports; ancestry check on cited Landed commits; case-insensitive citations, section boundary `^#{1,2} `; landed-section-missing not errata-able; base-revision append-only check; amended or re-dated round commits must not lapse the requirement. (c) Append a row documenting the splice error; non-author sampling of corrections (as r10 does for pointers).
Limits: closure not re-executed (corroboration from its text); LOG.md tie unchecked; [INFERENCE] items marked.
