# Diff table: re-run at fa3b62ae vs committed c1-tip-mutants.json


| item | committed | re-run | same |
|---|---|---|---|
| pristine | passed | passed | yes |
| mutants | 28 | 28 | yes |
| killed | 26 | 26 | yes |
| surviving | ['M17-ref-shadow', 'M20-log-sha-shape'] | ['M17-ref-shadow', 'M20-log-sha-shape'] | yes |
| retired | ['M14-promisor-config', 'M22-promisor-pack', 'M27-promisor-boolean', 'M29-promisor-pack-pairing'] | ['M14-promisor-config', 'M22-promisor-pack', 'M27-promisor-boolean', 'M29-promisor-pack-pairing'] | yes |
| retired_detail | [{"id": "M14-promisor-config", "literal": "raise EvalError(f\"{repo}: partial clone ({key})\")", "replaced_by": "PM01-blanket-metadata-refusal: the mutant reintroduces the blanket refusal and is killed by the complete/marker/hydrated rows", "why": "the metadata refusal is gone from the auditor"}, {"id": "M22-promisor-pack", "literal": "raise EvalError(f\"{repo}: partial clone (promisor pack)\")", "replaced_by": "PM01-blanket-metadata-refusal: the same blanket refusal, reached through the paired .promisor marker", "why": "the metadata refusal is gone from the auditor"}, {"id": "M27-promisor-boolean", "literal": "and git_bool(value)", "replaced_by": "PM01-blanket-metadata-refusal: a remote.*.promisor=true repository must keep the verdict of its full-clone twin", "why": "no promisor boolean is classified any more"}, {"id": "M29-promisor-pack-pairing", "literal": "p.with_suffix(\".pack\").exists()", "replaced_by": "PM01-blanket-metadata-refusal: a paired .promisor+.pack marker alone must not refuse the repository", "why": "the paired-marker classifier is gone from the auditor"}] | [{"id": "M14-promisor-config", "literal": "raise EvalError(f\"{repo}: partial clone ({key})\")", "replaced_by": "PM01-blanket-metadata-refusal: the mutant reintroduces the blanket refusal and is killed by the complete/marker/hydrated rows", "why": "the metadata refusal is gone from the auditor"}, {"id": "M22-promisor-pack", "literal": "raise EvalError(f\"{repo}: partial clone (promisor pack)\")", "replaced_by": "PM01-blanket-metadata-refusal: the same blanket refusal, reached through the paired .promisor marker", "why": "the metadata refusal is gone from the auditor"}, {"id": "M27-promisor-boolean", "literal": "and git_bool(value)", "replaced_by": "PM01-blanket-metadata-refusal: a remote.*.promisor=true repository must keep the verdict of its full-clone twin", "why": "no promisor boolean is classified any more"}, {"id": "M29-promisor-pack-pairing", "literal": "p.with_suffix(\".pack\").exists()", "replaced_by": "PM01-blanket-metadata-refusal: a paired .promisor+.pack marker alone must not refuse the repository", "why": "the paired-marker classifier is gone from the auditor"}] | yes |

## Per-mutant rows


| mutant | committed killed | re-run killed | committed grid_exit | re-run grid_exit | committed failed_rows | re-run failed_rows | same |
|---|---|---|---|---|---|---|---|
| M01-replace-objects | True | True | 1 | 1 | ['F03-replace-hides-omission', 'F04-replace-fabricated-citation', 'F05-replace-fleet-report'] | ['F03-replace-hides-omission', 'F04-replace-fabricated-citation', 'F05-replace-fleet-report'] | yes |
| M02-lazy-fetch | True | True | 1 | 1 | ['F06-lazy-fetch-command', 'F27-filter-only-promisor-remote'] | ['F06-lazy-fetch-command', 'F27-filter-only-promisor-remote'] | yes |
| M03-log-encoding | True | True | 1 | 1 | ['F22-utf16-log-cutoff'] | ['F22-utf16-log-cutoff'] | yes |
| M04-log-follow | True | True | 1 | 1 | ['F07-log-follow-cutoff'] | ['F07-log-follow-cutoff'] | yes |
| M05-log-showroot | True | True | 1 | 1 | ['F08-log-showroot-cutoff'] | ['F08-log-showroot-cutoff'] | yes |
| M06-log-signature | True | True | 1 | 1 | ['F09-signature-program'] | ['F09-signature-program'] | yes |
| M07-log-mailmap | True | True | 1 | 1 | ['F14-mailmap-fifo'] | ['F14-mailmap-fifo'] | yes |
| M09-strict-default | True | True | 1 | 1 | ['F02-report-invalid-utf8', 'F16-errata-invalid-utf8'] | ['F02-report-invalid-utf8', 'F16-errata-invalid-utf8'] | yes |
| M10-log-surrogates | True | True | 1 | 1 | ['F18-bad-byte-unrelated-subject', 'F19-bad-byte-round-subject'] | ['F18-bad-byte-unrelated-subject', 'F19-bad-byte-round-subject'] | yes |
| M11-listing-surrogates | True | True | 1 | 1 | ['F20-quotepath-open-range'] | ['F20-quotepath-open-range'] | yes |
| M12-shallow-check | True | True | 1 | 1 | ['F10-shallow-lane', 'F28-shallow-fleet'] | ['F10-shallow-lane', 'F28-shallow-fleet'] | yes |
| M13-grafts-check | True | True | 1 | 1 | ['F11-grafts-lane'] | ['F11-grafts-lane'] | yes |
| M15-object-format | True | True | 1 | 1 | ['F15-sha256-lane'] | ['F15-sha256-lane'] | yes |
| M16-top-level | True | True | 1 | 1 | ['F21-nested-subdirectory-lane'] | ['F21-nested-subdirectory-lane'] | yes |
| M17-ref-shadow | False | False | 0 | 0 | [] | [] | yes |
| M18-branch-heads | True | True | 1 | 1 | ['F12-tag-shadows-branch', 'F29-broken-branch-same-named-tag'] | ['F12-tag-shadows-branch', 'F29-broken-branch-same-named-tag'] | yes |
| M19-errata-hex | True | True | 1 | 1 | ['F17-errata-revision-correction'] | ['F17-errata-revision-correction'] | yes |
| M20-log-sha-shape | False | False | 0 | 0 | [] | [] | yes |
| M21-newlines | True | True | 1 | 1 | ['C08-cr-only-report'] | ['C08-cr-only-report'] | yes |
| M23-strict-decode-catch | True | True | 1 | 1 | ['F02-report-invalid-utf8', 'F16-errata-invalid-utf8'] | ['F02-report-invalid-utf8', 'F16-errata-invalid-utf8'] | yes |
| M24-catch-all | True | True | 1 | 1 | ['F24-huge-round-number'] | ['F24-huge-round-number'] | yes |
| M25-timestamp-shape | True | True | 1 | 1 | ['F26-huge-author-timestamp'] | ['F26-huge-author-timestamp'] | yes |
| M26-record-separators | True | True | 1 | 1 | ['F25-subject-record-injection'] | ['F25-subject-record-injection'] | yes |
| M28-correction-casefold | True | True | 1 | 1 | ['C11-uppercase-errata-correction'] | ['C11-uppercase-errata-correction'] | yes |
| M30-fleet-history-check | True | True | 1 | 1 | ['F28-shallow-fleet'] | ['F28-shallow-fleet'] | yes |
| M31-git-timeout | True | True | 1 | 1 | ['F30-config-include-fifo'] | ['F30-config-include-fifo'] | yes |
| M32-grafts-content | True | True | 1 | 1 | ['C13-comment-only-grafts'] | ['C13-comment-only-grafts'] | yes |
| M33-ref-shadow-bare-objects | True | True | 1 | 1 | ['F13-ref-named-abbreviation'] | ['F13-ref-named-abbreviation'] | yes |

## Verdict

differences: 0

## sha256

- committed /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/final/c1/c1-tip-mutants.json: 75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1
- re-run    run.json: 75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1
