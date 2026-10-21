VERDICT: partial - implementation and selftest delivered; runtime gate deferred

Axes: calibration (targeted); operability (unchanged).

Changed in the isolated copy: `tools/citation-provenance.py`. Adds `--sources`, which counts exact required `(rev, path, sha256)` tokens in Markdown table cells of `corpus/SOURCES.md`, reports found/missing rows and locations in text or JSON, and does not run Git blob verification. The embedded `--selftest` fixture covers table-only matching, outside-table exclusion, duplicate-token row counting, and a code-span pipe.

Retained evidence: `/tmp/kama-r19-CitationSourcesScan/out/citation-provenance.patch` and `receipt.md`. Patch generation command recorded in the receipt; observed `diff_exit=1` (changed files).

Verification: selftest and CLI mode were not run under the editing-wave no-tests rule; parent should run `python3 tools/citation-provenance.py --selftest` and `python3 tools/citation-provenance.py --sources --json` after integration. [INFERENCE] Runtime results remain unknown. LSP was unavailable in the exposed tool inventory [INFERENCE]. No installs or other blockers.
