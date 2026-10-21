VERDICT: confirm — duplicate-token and short-revision selftest cases are covered; all eight assertions passed.

Axes: calibration (the assigned lowest axis) improved through explicit boundary cases; operability unchanged (no serving or endpoint code was touched).

Implementation is in the isolated copy only: `/tmp/kama-r19-CitationDupCase/tools/citation-provenance.py`. The selftest now asserts that repeating an identical valid token passes; a 7-character revision passes when the registry uses the same abbreviation; and a 6-character revision is excluded by the token grammar and reports `missing=1, mismatch=0`. The new cases assert their exact missing/mismatch counts. Existing selftest cases remain, and the success summary counts all eight cases.

Retained execution evidence: `out/citation-selftest.txt` in the isolated copy records the exact command, working directory, exit and output. Executed `python3 tools/citation-provenance.py --selftest` from `/tmp/kama-r19-CitationDupCase`; exit 0; stdout `selftest: ok (8 cases)`; stderr empty. The command exercises only the selftest's temporary Git fixture.

Files: isolated implementation copy above; receipt `/tmp/kama-r19-CitationDupCase/out/citation-selftest.txt`; this advisory report. No lane implementation file was edited. No checks beyond the explicitly requested selftest were run; no tools were installed or updated. Blockers: none.
