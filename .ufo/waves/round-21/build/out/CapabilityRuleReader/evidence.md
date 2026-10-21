# CapabilityRuleReader — evidence log (kama round 21)

Lane: /home/vgpnk/Projects/shokunin/kama-shokunin (never written).
Scratch: /tmp/kama-r21-CapabilityRuleReader (removed at end).
Draft under review: a29bb84abbb8b4d328f5970a89e448330a3a42ac (parent 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d).

## Executed bash commands (exit as observed)

| # | Command | Exit | Observed |
|---|---|---|---|
| B1 | mkdir -p scratch; git clone -q LANE scratch/lane; git checkout -q a29bb84; git rev-parse HEAD | 0 | a29bb84abbb8b4d328f5970a89e448330a3a42ac |
| B2 | git log --format=... -n 4 a29bb84 | 0 | subject "round-21: report landing audit with errata ledger; symlink-aware install-links pin, gate checks and grid"; empty body, so no Report: trailer |
| B3 | git diff --stat 7a6bc91 a29bb84 | 0 | 7 files: .ufo/waves/round-21/sources/{census-before,validate-before}.txt; registry/report-landing-errata.tsv; tests/llamacpp-live/{check-receipt.py,install-links-grid.py}; tools/{kama-llamacpp-live.py,report-landing-audit.py}; 921 insertions, 2 deletions |
| B4 | git show 7a6bc91:SCORECARD.md | 0 | round-start SCORECARD, 1018 lines (draft does not touch it) |
| B5 | git diff --stat 7a6bc91 a29bb84 -- SCORECARD.md LOG.md SKILL.md corpus | 0 | empty output: none of these changed |
| B6 | git rev-parse master a29bb84 | 0 | both a29bb84abbb8b4d328f5970a89e448330a3a42ac |
| B7 | python3 tools/report-landing-audit.py --no-errata (cwd scratch lane) | 2 | could-not-evaluate: git rev-parse in /tmp/kama-r21-CapabilityRuleReader; default --fleet-repo is lane parent (audit.py:381), scratch is outside fleet layout. Disclosed, not a defect in the real layout |
| B8 | python3 tools/report-landing-audit.py --no-errata --fleet-repo /home/vgpnk/Projects/shokunin | 1 | defects by round: r10 1, r18 3, r20 5. summary: reports=11 defects=9 corrected=0 uncorrected=9 errata_unmatched=0 errata_invalid=0 status=failed |
| B9 | python3 tools/report-landing-audit.py --fleet-repo /home/vgpnk/Projects/shokunin | 0 | summary: reports=11 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean |
| B10 | python3 tools/report-landing-audit.py --selftest | 0 | selftest cases=15 failed=0 |
| B11 | python3 tools/report-landing-audit.py --no-errata --fleet-repo ... --json > audit-raw.json; then python3 json load | 1; 0 | top keys errata_invalid, errata_unmatched, results, summary. summary by_kind: landed-omitted 8, unresolved-full-hash 1, landed-section-missing 0, landed-unresolved 0. required_commits 42, post_report_commits 4, rounds 10..20. No revision field |
| B12 | find /home/vgpnk/.local/opt/llama-b11755 -maxdepth 1 -printf '%y %f -> %l\n' \| sort (read-only) | 0 | 10 symlinks: libggml-base.so->libggml-base.so.0; libggml-base.so.0->libggml-base.so.0.27.0; libggml.so->libggml.so.0; libggml.so.0->libggml.so.0.27.0; libllama-common.so->libllama-common.so.0; libllama-common.so.0->libllama-common.so.0.7.0; libllama.so->libllama.so.0; libllama.so.0->libllama.so.0.7.0; libmtmd.so->libmtmd.so.0; libmtmd.so.0->libmtmd.so.0.7.0 |

## Tool reads and greps (no exit code; results cited in report)

- read: skill://godspeed; AXES.md (full); MISSION.md (full); shokunin.conf (full); PROTOCOL.md:340-400, 398-425, 495-525; templates/round-prompt.md:1-60; lane .ufo/waves/round-21/build (listing).
- grep "capabilit|stagnation|exploratory|saturation" over templates, PROTOCOL.md, CORPUS.md, LEARNING.md.
- grep "hardening|hardened|acquisition|repertoire|newly acquired|pre-claim|capability-shaped|debt" over AXES, MISSION, PROTOCOL, LEARNING, templates: no fleet rule defines hardening; only generic "generic hardening advice" at templates/agents/ufo-sentinel.md:22.
- grep SCORECARD (scratch lane at a29bb84; SCORECARD unchanged from 7a6bc91): headings, capability rows, saturation, symlink/soname, install-tree lines (cited in report).
- grep "ties depth|lowest assigned|Calibration 7 is ..." SCORECARD: lines 226-228, 342-343, 400-402, 563-565, 630-632, 649, 817-818.
- grep "calibration ... 7 → 8 | 7 → 8, sourced": only SCORECARD:821 (R19 declaration, corrected to 7→7 at :844-845).
- grep audit script for snapshot|frozen|add_argument|main|--report|--selftest: no snapshot or frozen token; options at 377-390.
- grep audit script for read/git sites: read_text at 107 from Path(fleet_repo)/rel (line 105); round_commits branch at 85-87; cutoff at 97-99; rev-parse at 203-204; --fleet-repo default 381; --branch default 382.
- grep install-links-grid.py and kama-llamacpp-live.py: DEFAULT_TREE 44 (live host tree); mirror() 83-91; install_links() 205-224; receipt fields 1294, 1308-1309.
- grep shokunin.conf and MISSION.md kama rows: shokunin.conf:52; MISSION.md:29.
- grep SKILL.md "report-landing|landing-audit|install-links|install_links|install-links-grid": No matches found.
- grep "TreeCap" in SCORECARD.md and LOG.md: LOG.md:1182 "CritC1Inflation/CritAxisHarm/TreeCap were build seats, not falsify seats".

## Not executed by me (claimed in the assignment only; outside the rulings)

- install-links-grid.py cell counts (frozen 0/9, current 9/9, controls, null): not re-run.
- check-receipt.py selftest "9 VALID + 1 NOT-EVALUATED, 90 mutations": not re-run.
- tools/kama-llamacpp-live.py live run: not run (bounds forbid it).

## Installs and updates

- None. No package installed, upgraded or removed.
