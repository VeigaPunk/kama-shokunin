# ExecC1TipReplicate — C1 supporting evidence (independent replicate) — round 25 attempt 2

Verdict: full mutant run at 1fc41e346853afd98cbd7010af5db4e54dc877f7 passes pristine with ` 0; 28 registered mutants, 26 killed, 2 survivors (M17-ref-shadow, M20-log-sha-shape); M11 and M33 killed, M17 survives.

## What ran

- Own clone at `/fast/scratch/hyaku/kama-r25a2/ExecC1TipReplicate/clone`, `git clone --no-hardlinks` from the lane repo, checked out `1fc41e346853afd98cbd7010af5db4e54dc877f7` (confirmed by `git rev-parse HEAD`; working tree clean).
- Command (once, from the clone root):

  ```
  python3 tests/report-audit/isolation-mutants.py --json
  ```

  stdout saved to `mutant-run.json` (5959 bytes), stderr saved to `mutant-run.stderr` (empty). Exit code **0** (printed `EXIT=0`). Wall time 984.73 s.

## Result summary (from the saved JSON)

- `pristine`: "passed"
- `mutants`: 28, `killed`: 26, `surviving`: ["M17-ref-shadow", "M20-log-sha-shape"]
- `retired`: M14-promisor-config, M22-promisor-pack, M27-promisor-boolean, M29-promisor-pack-pairing (with attribution detail in JSON)
- Every mutant ran (no could-not-evaluate; exit 0 confirms it)

### Killed (26) — each with the failed grid rows its weakened auditor tripped
| mutant | failed rows |
|---|---|
| M01-replace-objects | F03-replace-hides-omission, F04-replace-fabricated-citation, F05-replace-fleet-report |
| M02-lazy-fetch | F06-lazy-fetch-command, F27-filter-only-promisor-remote |
| M03-log-encoding | F22-utf16-log-cutoff |
| M04-log-follow | F07-log-follow-cutoff |
| M05-log-showroot | F08-log-showroot-cutoff |
| M06-log-signature | F09-signature-program |
| M07-log-mailmap | F14-mailmap-fifo |
| M09-strict-default | F02-report-invalid-utf8, F16-errata-invalid-utf8 |
| M10-log-surrogates | F18-bad-byte-unrelated-subject, F19-bad-byte-round-subject |
| M11-listing-surrogates | F20-quotepath-open-range |
| M12-shallow-check | F10-shallow-lane, F28-shallow-fleet |
| M13-grafts-check | F11-grafts-lane |
| M15-object-format | F15-sha256-lane |
| M16-top-level | F21-nested-subdirectory-lane |
| M18-branch-heads | F12-tag-shadows-branch, F29-broken-branch-same-named-tag |
| M19-errata-hex | F17-errata-revision-correction |
| M21-newlines | C08-cr-only-report |
| M23-strict-decode-catch | F02-report-invalid-utf8, F16-errata-invalid-utf8 |
| M24-catch-all | F24-huge-round-number |
| M25-timestamp-shape | F26-huge-author-timestamp |
| M26-record-separators | F25-subject-record-injection |
| M28-correction-casefold | C11-uppercase-errata-correction |
| M30-fleet-history-check | F28-shallow-fleet |
| M31-git-timeout | F30-config-include-fifo |
| M32-grafts-content | C13-comment-only-grafts |
| M33-ref-shadow-bare-objects | F13-ref-named-abbreviation |

### Survivors (2)

| mutant | grid exit | failed rows | note |
|---|---|---|
| M17-ref-shadow | 0 | none | weakened auditor passed every row; the peel-guarded lookup() refusal is exercised by no current row (the bare_objects() site is M33) |
| M20-log-sha-shape | 0 | none | no grid row feeds a non-40-hex sha (F26 checks author timestamp, not sha shape) |

Survival is reported as observed; per the instrument's contract it carries no necessity claim.

## M11 / M17 / M33 specifics

- **M11-listing-surrogates — KILLED** by F20-quotepath-open-range. The re-anchored literal (spanning the wrapped `git ... log -- .ufo/reports` call, `tools/report-landing-audit.py:682-683`) matched exactly once; weakening it trips the fleet-report-listing surrogateescape row. This independently reproduces the attempt-1 RevengerM11 finding (F20) cited in ATTEMPT-1-DISPOSITION.md.
- **M17-ref-shadow — SURVIVED** (grid exit 0). Its literal (the peel-guarded citation refusal in `lookup()`, `tools/report-landing-audit.py:213-214`) matched exactly once and was applied; the weakened auditor passed every grid row (exit 0), so no current row detects that weakening. The bare_objects() refusal is covered by the separate M33 row.
- **M33-ref-shadow-bare-objects — KILLED** by F13-ref-named-abbreviation. The new id's literal (`tools/report-landing-audit.py:276-277`) matched exactly once; weakening it trips the row the second call site guards. No id reused or retired; denominator 28 as registered.

## Registered-count cross-check (independent of the run)

Reran the registered counting command's logic on the same checkout:

```
python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"
```

Output: `registered 28 stale 0 []`; M11, M17 and M33 each count exactly 1. Matches the C1 target (stale 0, denominator 28).

## Artifacts written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecC1TipReplicate/mutant-run-1fc41e346853afd98cbd7010af5db4e54dc877f7.json` (copy of the run output; sha256 `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`). Source run JSON and empty stderr also under `/fast/scratch/hyaku/kama-r25a2/ExecC1TipReplicate/`.
- This advice report: `.ufo/waves/round-25/a2-build/advice/ExecC1TipReplicate.md`.

## Tools installed

None. No new tool or upgrade was needed (system `python3` was sufficient).

## Risks / notes

- M17 surviving is a recorded observation, not a claim of correctness; the report is a replicate of the instrument's verdict at this tip.
- Only the registered instrument was run; no llama-server child was started.
