# C1RawRerun evidence log (2026-10-21)

Scratch: /tmp/kama-r21-C1RawRerun/lane @ b76727f31e522763ce24e43d6ec86d21b507a11f (rev-parse verified, porcelain clean=0).

| # | command (cwd=clone, env minus GIT_*) | rc | key stdout |
|---|---|---|---|
| 1 | git -C <lane> cat-file -e 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d:tools/report-landing-audit.py | 128 | stderr: fatal: path 'tools/report-landing-audit.py' exists on disk, but not in '7a6bc911…' |
| 2 | git -C <lane> cat-file -e b76727f3…:tools/report-landing-audit.py | 0 | (exists at measured commit) |
| 3 | /usr/bin/python3 tools/report-landing-audit.py --rounds 10-20 --no-errata --json --fleet-repo /home/vgpnk/Projects/shokunin | 1 | sha256 af2707adf5c2424ebe64b30505d33d94b0c5ca08f2d843cf6a27a4aa10651e24, stderr 0 B |
| 4 | /usr/bin/python3 tools/report-landing-audit.py --rounds 10-20 --json --fleet-repo /home/vgpnk/Projects/shokunin | 0 | sha256 6e865bd73178441f9eceb51018cffe42a513dcf1ff52cd324cf7cc4e17e4259d, stderr 0 B |
| 5 | /usr/bin/python3 tools/report-landing-audit.py --selftest | 0 | ok raw-fails / mashup-detected / checkpoint-without-colon-omission-detected / bad-abbrev-detected / exact-defect-set … |

Reference integrity: c1-audit-raw.stdout sha256 == commands.json stdout_sha256 (af2707ad…) True; c1-audit-ledger.stdout == 6e865bd7… True.
Diff (official vs rerun, clone path normalized to official lane path): 0 lines both; byte-equal even pre-normalization.
Official exit files: c1-audit-raw.exit=exit=1, c1-audit-ledger.exit=exit=0, c1-absent-at-base.exit=exit=128 (all read directly).

Raw summary (rerun): {"by_kind": {"landed-ambiguous": 0, "landed-omitted": 8, "landed-section-missing": 0, "landed-unresolved": 0, "unresolved-full-hash": 1}, "corrected": 0, "defects": 9, "errata_invalid": 0, "errata_rows": 0, "errata_unmatched": 0, "post_report_commits": 4, "reports": 11, "required_commits": 42, "rounds": [10..20], "status": "failed", "uncorrected": 9}
Ledger summary (rerun): same by_kind; corrected=9, uncorrected=0, errata_rows=9, errata_unmatched=0, errata_invalid=0, status="clean".
Per-round defects (raw == ledger): r10 landed-omitted×1; r18 ×3; r20 landed-omitted×4 + unresolved-full-hash×1; others 0. r19 post_report=4 commits; sum(required)=42.

No tools installed or upgraded (task ran on preexisting git + /usr/bin/python3 3.14.8).
