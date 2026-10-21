VERDICT: confirm - C1 report-landing-audit is a distinct population from citation-provenance and sources-append-only; no code/registry overlap; fleet has no existing validator

## Overlap Scan & Population Classification
- **tools/report-landing-audit.py (C1)**: Audits fleet reports `.ufo/reports/round-N/kama.md` (rounds 10–20 + draft) for 4 mechanical defects: unresolved 40-hex object hashes, unresolved 7..40-hex commits in `## Landed changes`, omitted round commits (`round-N:`/`checkpoint(rN)`), and missing Landed sections. Uses append-only `registry/report-landing-errata.tsv` for past defects.
- **tools/citation-provenance.py (R19 C1)**: Audits lane repo docs (`corpus/lessons/*.md`, `SCORECARD.md`, etc.) for exact `cite(rev, path, sha256=...)` micro-syntax against `registry/required-citations.json` (17 rows), verifying git blob bytes via `git cat-file blob`.
- **tools/sources-append-only.py (R18/R19)**: Audits `corpus/SOURCES.md` markdown table between revisions for row retention and 7 immutable contract columns.
- **Classification**: **DISTINCT POPULATION**. Targets are completely disjoint (fleet markdown reports vs. lane documentation blobs vs. SOURCES table diffs). C1 is neither duplicate nor an extension.
- **Reuse**: NO code or registry reuse. `required-citations.json` defines forward blob-hash requirements; `report-landing-errata.tsv` is an append-only historical errata ledger. Merging them or coupling the tools creates cross-schema pollution and artificial fragility.

## Fleet Scripts Scan (/home/vgpnk/Projects/shokunin/scripts/)
- `scripts/shokunin-watchdog.sh`: `report_of()` checks only file presence, baseline digest change, `# SHONEN` heading, and size >= 400B. `report_sources_conformance()` checks only `## Sources & frontier` heading. Does NOT inspect commit hashes or Landed changes.
- `scripts/hyaku/inline.sh`: Calls `report_of` and sweeps uncommitted report files. Does NOT inspect commit hashes.
- `scripts/hyaku/closure-prompt.md`: Contains LLM prompt instructions for non-author closure reviewers to check commit ancestry; NOT an automated mechanical tool (R20 closure missed defects D1/D2).
- `scripts/hyaku/append-closure.py`: Validates JSON schema and report file presence; does not inspect report content.
- **Conclusion**: The fleet has no mechanical report commit or Landed validator. C1 does not duplicate or reinvent any fleet tool.

## UFO-FSD Connector Move: Strict Citation Decoupling & Clean Landed Boundary
- **Evidence**: `ABBREV` regex `[0-9a-f]{7,40}` in `report-landing-audit.py` treats any 7..40-hex token in `## Landed changes` as a commit (failing on bare 7+ digit numbers or hex words like `effaced`, N2/N3 in ReportFormatDraft). 64-hex SHA-256 tokens from `citation-provenance.py` do not match `ABBREV` or `FULL`. Errata corrections (9/9) are valid commits and ancestors of `master`.
- **Affected axes**: Calibration (7 -> 7/8, unblocked by false positives; report verified) and Operability (8 -> 8, zero coupling).
- **Proposed move**: Maintain strict decoupling between C1 and `citation-provenance.py`. In the round-21 `## Landed changes`, use only full 40-hex hashes from `git log` and avoid uncomma'd >=7 digit counts or hex words in prose. Adopt SimplifyAudit's dead-code removals.
- **Risks**: Commits landed after report drafting trigger `landed-omitted`; mitigate by generating the Landed section immediately before final commit.
- **Verification (all executed)**:
  - `python3 tools/report-landing-audit.py --selftest` -> exit 0 (15 cases)
  - `python3 tools/citation-provenance.py --selftest` -> exit 0 (24 cases)
  - `python3 tools/citation-provenance.py` -> exit 0 (`required=17 verified=17 missing=0 mismatch=0`)
  - `python3 tools/report-landing-audit.py --no-errata` -> exit 1 (9 defects uncorrected)
  - `python3 tools/report-landing-audit.py` -> exit 0 (`defects=9 corrected=9 status=clean`)
  - `python3 tools/sources-append-only.py --selftest` -> exit 0 (42 cases)
