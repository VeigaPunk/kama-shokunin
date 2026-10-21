VERDICT: confirm - draft row and checklist step match `tools/report-landing-audit.py` at a29bb84; raw 9 / corrected 0 / selftest 15 reproduced; default `--rounds 10-20` omits round 21 (gap, see F1).

# SkillRowAudit — scoped draft (lane kama, round 21, SKILL-row + checklist text only)

Scope: text for SKILL.md instrument row and one Checklist step. No lane file edited. Scratch clone `/tmp/kama-r21-SkillRowAudit` (checked out a29bb84) removed at end.

## Draft row (column format of SKILL.md rows 652-656, round-20 registry table)

| Report landing audit | gate: `python3 tools/report-landing-audit.py [--rounds 10-21] [--report 21=PATH] [--errata PATH] [--no-errata] [--json]` (official run from the lane root; default `--rounds 10-20` omits round 21) | 0 clean (no uncorrected defect; no unmatched or invalid errata row); 1 failed (uncorrected defect, unmatched or invalid errata row); 2 could-not-evaluate (missing report, unusable git, unreadable or malformed errata, malformed `--rounds`); argparse usage errors also exit 2 | `--selftest`, 15 cases in temporary git repositories; prints `selftest cases=15 failed=0`, exit 0 | `registry/report-landing-errata.tsv` (9 append-only rows, sha256 `baaf4bdaf30c1ce0a08434017cc279b34aa6745450cedabb9e0c3fe144fce53d`); tool sha256 `a60acc3a2444eddb34122d84f8d88cd0bcc5c6b103c90f2ca2e9ef330c28df9d` at a29bb84; fleet `.ufo/reports/round-N/kama.md`, cutoff = first add-commit time (uncommitted `--report` draft uses current time) | stdout only (text or `--json`); selftest temporary repos removed | kama |

## Draft Checklist step (append as step 9)

9. **Audit a round report before committing it** — with the draft at `PATH`, run
   `python3 tools/report-landing-audit.py --report 21=PATH; echo "AUDIT_EXIT=$?"`
   and paste its `round=21 ...` line and final `summary ... status=...` line into the report.
   Exit `0` (`status=clean`) is required before commit; `1` means an uncorrected
   landed-omission, unresolved full hash or missing `## Landed changes` section; `2` means
   the audit could not evaluate and claims nothing. After the report is committed, rerun with
   `--rounds 10-21` (the default `10-20` does not include round 21). Do not add an errata row
   to pass the audit without naming the defect and its evidence in the append-only ledger.

## Executed evidence (cwd lane root unless noted; exit = observed `$?`)

| Command (abbrev.) | Exit | Observed |
|---|---|---|
| `python3 tools/report-landing-audit.py --selftest` (scratch @a29bb84) | 0 | 15 `ok` lines, `selftest cases=15 failed=0` |
| `... --lane-repo L --fleet-repo F --no-errata` | 1 | `summary reports=11 defects=9 corrected=0 uncorrected=9 status=failed`; 1 unresolved-full-hash (r20 0957ce61...d13d894e), 8 landed-omitted (r10 x1, r18 x3, r20 x4) |
| `... --lane-repo L --fleet-repo F` | 0 | `summary reports=11 defects=9 corrected=9 uncorrected=0 status=clean` |
| `... --rounds 10-21 --report 21=ok.md --json` | 0 | summary `reports=12 defects=9 corrected=9 required_commits=43 post_report_commits=4 status=clean`; round 21 `required=1` (a29bb84) |
| `... --report 21=ok.md` (default rounds) | 0 | prints rounds 10-20 plus `round=21 required=1 defects=0`; `status=clean` |
| `... --rounds 21 --report 21=draft-empty.md` (Landed = `- none`) | 1 | `landed-omitted a29bb84...`, status failed |
| `... --rounds 21 --report 21=nosec.md` (no section) | 1 | `landed-section-missing`, `landed-omitted a29bb84...` |
| `... --rounds 22` (no report file) | 2 | `could-not-evaluate: round 22: cannot read .../round-22/kama.md` |
| `... --lane-repo /tmp/.../nope` | 2 | `could-not-evaluate: git rev-parse ... rc=128` |
| `... --errata /tmp/.../nope.tsv` | 2 | `could-not-evaluate: cannot read errata` |
| `... --report 21=draft/absent.md` | 2 | `could-not-evaluate: cannot read ...absent.md` |
| `python3 tools/report-landing-audit.py --bogus` | 2 | argparse usage error (not could-not-evaluate) |
| run with no args from scratch clone | 2 | `could-not-evaluate: git ... in /tmp/kama-r21-SkillRowAudit: not a git repository` |
| `git -C L show a29bb84:tools/report-landing-audit.py \| sha256sum` | 0 | `a60acc3a...` equals working-tree sha256 (no diff, real lane HEAD = a29bb84) |
| `sha256sum registry/report-landing-errata.tsv` | 0 | `baaf4bda...` |
| `grep -c -v '^#' registry/report-landing-errata.tsv` | 0 | `9` rows |

L = `/home/vgpnk/Projects/shokunin/kama-shokunin`, F = `/home/vgpnk/Projects/shokunin`. Read-only git only (log, cat-file, rev-parse, show); no lane index or state touched.

## Findings

- F1 (gap in the draft row, verified by code): `rounds = sorted(set(parse_rounds(args.rounds)) | set(overrides))` with default `10-20`. Once round 21 is committed, a bare run audits 10-20 only; the row and step must pin `--rounds 10-21`. Verified by the `--rounds 10-21` run (exit 0, 12 reports).
- F2 (code-read, [INFERENCE] on timing): `report_cutoff` uses the first add-commit time of the fleet report; `pre` = lane round commits with ctime <= cutoff. A round-21 commit made after the draft audit but before the report commit becomes `required` and fails `landed-omitted` unless cited. Hence the rerun after commit in step 9. Not exercised live.
- F3: the default `--lane-repo`/`--fleet-repo` derive from the script location; run from the lane checkout (verified only at the real lane root, exit 0 for the official run). The scratch clone without explicit repo flags exits 2, so the row should say "from the lane root".
- F4: `--report` with a committed path is not supported as a commit-time audit: `audit_round` sets cutoff = now when a path override is given (code-read, lines 103-111). Use the committed path with no override after commit.
- F5: exit 2 covers argparse usage errors too; the verdict map says so explicitly in the row.

## Tooling

No tools installed or updated (Python 3.14.8 present; stdlib only). Scratch removed after report write.

## Not run

No live llama-server, no model, no network. No checks of the 77/90-mutation gates (out of scope). No modification of the lane, the fleet repo, or MANIFEST.
