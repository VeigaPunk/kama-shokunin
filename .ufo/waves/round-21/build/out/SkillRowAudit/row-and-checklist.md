Draft SKILL.md row (round-20 registry table format; verified against a29bb84, see ../../advice/SkillRowAudit.md):

| Report landing audit | gate: `python3 tools/report-landing-audit.py [--rounds 10-21] [--report 21=PATH] [--errata PATH] [--no-errata] [--json]` (official run from the lane root; default `--rounds 10-20` omits round 21) | 0 clean (no uncorrected defect; no unmatched or invalid errata row); 1 failed (uncorrected defect, unmatched or invalid errata row); 2 could-not-evaluate (missing report, unusable git, unreadable or malformed errata, malformed `--rounds`); argparse usage errors also exit 2 | `--selftest`, 15 cases in temporary git repositories; prints `selftest cases=15 failed=0`, exit 0 | `registry/report-landing-errata.tsv` (9 append-only rows, sha256 `baaf4bdaf30c1ce0a08434017cc279b34aa6745450cedabb9e0c3fe144fce53d`); tool sha256 `a60acc3a2444eddb34122d84f8d88cd0bcc5c6b103c90f2ca2e9ef330c28df9d` at a29bb84; fleet `.ufo/reports/round-N/kama.md`, cutoff = first add-commit time (uncommitted `--report` draft uses current time) | stdout only (text or `--json`); selftest temporary repos removed | kama |

Draft Checklist step (append as step 9):

9. **Audit a round report before committing it** — with the draft at `PATH`, run
   `python3 tools/report-landing-audit.py --report 21=PATH; echo "AUDIT_EXIT=$?"`
   and paste its `round=21 ...` line and final `summary ... status=...` line into the report.
   Exit `0` (`status=clean`) is required before commit; `1` means an uncorrected
   landed-omission, unresolved full hash or missing `## Landed changes` section; `2` means
   the audit could not evaluate and claims nothing. After the report is committed, rerun with
   `--rounds 10-21` (the default `10-20` does not include round 21). Do not add an errata row
   to pass the audit without naming the defect and its evidence in the append-only ledger.
