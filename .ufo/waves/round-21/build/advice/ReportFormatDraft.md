# ReportFormatDraft — round-21 `## Landed changes` template

VERDICT: partial - the generated Landed template reproduces the audit's required set (r20 9/9, r21 1/1) and passes the round-21 gate with 0 defects, but the audit does not catch unfilled placeholders or prose that trips its hex/digit rule.

Scope: template block only, plus audit command lines and pasted summaries. Lane not modified; the only writes are this file and `build/out/ReportFormatDraft/`.

## Findings (each command executed; exit codes observed)

1. **Generator (subject + author, matches the audit's own rule).** `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='- `%H` — %s' --author='kama-shokunin' --grep='^round-21:' --grep='^checkpoint(r21)' master` → exit 0, 1 line (`a29bb84abbb8b4d328f5970a89e448330a3a42ac`). Same generator with `round-20:` → exit 0, count=9, equal to the audit's `round=20 required=9`.
2. **Range-only generator is weaker.** `git log --format='%h' 0957ce619789d13bb5779606078fa1498114d2c7..7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d | wc -l` → exit 0, 7. Two round-20 commits (`33a6777866d0f63d894ef21bc863486bcb35b56c`, `0957ce619789d13bb5779606078fa1498114d2c7`) sit outside that range, so a range-only list would have omitted them again. Subject+author generation is preferred.
3. **Audit, raw (`--no-errata`)**: `summary reports=11 defects=9 corrected=0 uncorrected=9 errata_unmatched=0 errata_invalid=0 status=failed`, exit 1. Defects: unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c (r20); landed-omitted r10 ×1, r18 ×3, r20 ×4 (`846e366d…`, `92b14625…`, `0957ce61…bb5779…`, `33a67778…`).
4. **Audit, corrected (default ledger)**: `summary reports=11 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean`, exit 0. Plain invocation from the lane (no flags) gives the same result (exit 1 raw, exit 0 corrected).
5. **Round-21 gate on a draft (`--rounds 10-21 --report 21=<draft>`, errata on)**: `round=21 required=1 post_report=0 defects=0`; `summary reports=12 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean`, exit 0.
6. **Selftest** `python3 tools/report-landing-audit.py --selftest` → 15 ok, `selftest cases=15 failed=0`, exit 0.
7. **Negative controls** on a Landed section (`--rounds 21 --report 21=<file> --no-errata`), all exit 1 as required:
   - N1 empty section → `landed-omitted a29bb84…`.
   - N2 bare `22240468` → `landed-unresolved 22240468`.
   - N3 `effaced` → `landed-unresolved effaced` (7 letters, all hex digits/letters a–f).
   - N4 fake 40-hex `0957ce619789d13d894ef21bc863486bcb35b56c` in Work performed → `unresolved-full-hash`.
8. **Gap (observed):** the round-21 draft still containing the placeholder `LOG.md:<LINE>` gives `round=21 defects=0`. The audit does not check the LOG pointer. Sweep before commit: `grep -nE '<(LINE|line|FULL|SUBJECT)' <draft>` must print nothing (observed: it currently prints the placeholder line, exit 0 — the sweep is the control).
9. **Gap [INFERENCE, not run]:** a commit landing after the report commit is excluded (`post_report`, observed for r19 = 4). Commit the report after the last lane commit, or re-run the generator and gate.

## Round-20 defect classes vs. this template

| r20 defect | Template control | Status |
|---|---|---|
| unresolved full hash `0957ce619789d13d894ef…` | hashes come only from `%H`; audit N4 rejects a fake one | blocked by construction + gate |
| landed-omitted (4 in r20, 3 in r18, 1 in r10) | generator lists all subject+author matches (r20: 9 = audit required) | blocked by generator + gate |
| landed-section hand-typed | template bullet is one per generator line | blocked by construction |
| placeholder left in bullet | not checked by audit; grep sweep above | **open** — needs the sweep |

## Template block (paste into `## Landed changes`; one bullet per generator line)

```
## Landed changes

- `<FULL-40-HEX from generator>` — <SUBJECT from generator> — LOG.md:<LINE> — <effect in at most 25 words>
```

Rules: keep the full 40-hex; replace every `<…>`; no word of 7+ chars made only of 0–9/a–f and no bare run of 7+ digits in the section (use `22,240,468`, not `22240468`); one bullet per generator line, none dropped.

## Audit command block

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 tools/report-landing-audit.py --no-errata                          # raw: expect exit 1, 9 defects
python3 tools/report-landing-audit.py                                      # corrected: expect exit 0
python3 tools/report-landing-audit.py --rounds 10-21 --report 21=<draft>   # pre-commit round-21 gate
python3 tools/report-landing-audit.py --rounds 10-21                       # post-commit gate
grep -nE '<(LINE|line|FULL|SUBJECT)' <draft>                               # placeholder sweep: must print nothing
```

## Tools

None installed or updated. Scratch `/tmp/kama-r21-ReportFormatDraft` (clone at a29bb84) deleted after the run; the audit only reads git and writes nothing.
