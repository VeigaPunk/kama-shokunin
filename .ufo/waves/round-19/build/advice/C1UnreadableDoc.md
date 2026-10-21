VERDICT: partial - an unreadable carrier exits 1 and an unreadable registry exits 2, both with no false 0; but an unreadable non-carrier scanned doc exits 0 printing the full success line (the no-false-0 claim is refuted there), and unreadable docs and non-repo lanes never exit 2 as the docstring contract states. A 2-hunk fix is verified in /tmp, not applied to the lane.

Scope: private copy /tmp/kama-r19-C1UnreadableDoc (cp -a of the lane; HEAD 8bf99ca descends from declared tip 1b85a24, `git merge-base --is-ancestor` exit 0; round-19 working tree included). Lane not modified. Running as uid 1000, so chmod 000 is enforced (each case records PermissionError). Python 3.14.8, git 2.56.0. No installs or updates.

## Results: as-is tools/citation-provenance.py
Probe: `python3 out/c1_unreadable_probe.py --tool tools/citation-provenance.py --tag as-is` exit 0 (restored=True). Receipt: out/receipt-as-is.txt, .json.

| Case | Exit | stdout | Docstring contract |
|---|---|---|---|
| all readable (baseline) | 0 | `required=3 found=3 verified=3 missing=0 mismatch=0` | ok |
| carrier corpus/lessons/round-18.md (all 3 tokens), mode 000 | 1 | `required=3 found=0 verified=0 missing=3 mismatch=0` | expected 2 |
| non-carrier SOURCES.md, SCORECARD.md, LOG.md, mode 000 | **0** | identical success line | expected 2 |
| registry, mode 000 | 2 | empty; stderr names the file | ok |
| all four scanned, mode 000 | 1 | `missing=3` | expected 2 |
| same bytes plus 0xff (decode error) | 2 | empty | ok |
| same bytes, mode 000 | 1 | `missing=3` | expected 2 |
| missing doc beside carrier (ENOENT) | 0 | success line | expected 2 |
| non-repo lane | 1 | `required=3 found=3 verified=0 missing=0 mismatch=3` | expected 2 |

## Findings
1. Medium - false green at the doc-set level. An unreadable non-carrier doc yields exit 0 and the same success line; the only signal is one stderr line. JSON has only `counts` and `results`, so nothing marks the skipped doc. No required row can pass falsely: `scan()` is the sole token source, and the carrier case shows rows going missing. The defect is a success verdict over an incomplete scan.
2. Medium - exit 2 is never produced for unreadable docs. `scan()` swallows OSError; `main()` maps ValueError (decode error) to 2. The same bytes exit 2 when undecodable, 1 when permission-denied, and 0 when missing. Exit 1 reads as "citation missing", which points operators at the wrong fix.
3. Low-Med - a non-repo lane exits 1, not 2. `git_blob` errors become `mismatch` whenever a token hit exists.
4. Low - the selftest has 5 cases and none covers an unreadable doc, so findings 1 and 2 are untested.

## Staged fix (advice, not applied to lane)
out/proposed/citation-provenance.py; diff in out/proposed-fix.diff (`diff -u` exit 1 = files differ, expected).
- Hunk 1 (`scan`): remove the try/except so OSError reaches `main()` and exits 2. Fixes 1 and 2.
- Hunk 2 (`check`): `git -C lane rev-parse --git-dir` precheck raising ValueError, so exit 2. Fixes 3; independent of hunk 1.

Verified: `python3 out/c1_unreadable_probe.py --tool out/proposed/citation-provenance.py --tag proposed` exit 0 (restored=True). Every unreadable scanned doc, the registry, ENOENT, permission-denied, decode error and non-repo lane exit 2 with empty stdout. Baseline stays 0 with the identical line; contrast-valid stays 0. `python3 out/proposed/citation-provenance.py --selftest` exit 0 (`selftest: ok (5 cases)`).

Caller impact: within the lane, grep for `citation-provenance|required-citations` across *.py, *.sh, *.yml, *.yaml, *.toml, *.json found only the tool itself, docs and agent-task JSON; no code caller depends on exit codes. A workspace-root grep also matched unrelated sibling census data naming a `citation-provenance-formats.md` file; not a caller. Behaviour change: an absent or unreadable scanned doc now fails the gate, as the documented contract says.

## Commands and exits (all in the /tmp copy)
- `python3 tools/citation-provenance.py` exit 0; `python3 tools/citation-provenance.py --selftest` exit 0.
- `python3 out/c1_unreadable_probe.py --tool tools/citation-provenance.py --tag as-is` exit 0.
- `python3 out/c1_unreadable_probe.py --tool out/proposed/citation-provenance.py --tag proposed` exit 0.
- `python3 out/proposed/citation-provenance.py --selftest` exit 0.
- `git merge-base --is-ancestor 1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e HEAD` exit 0.
- `diff -u tools/citation-provenance.py out/proposed/citation-provenance.py` exit 1 (expected; written to out/proposed-fix.diff).

## Residual risk and gaps
- Not run as root. Under root, chmod 000 is a no-op and the cases would be vacuous; the probe asserts PermissionError per case, so it would show READABLE. [INFERENCE for root behaviour]
- Not executed: a directory in place of a doc (IsADirectoryError, same OSError path) [INFERENCE]; a wrong-sha token in a doc is silently ignored by design, since only exact registry hits count [INFERENCE from code reading].
- Hunk 1 turns an absent optional doc into exit 2 in any future sparse checkout. Adopt deliberately.

Deliverables: /tmp/kama-r19-C1UnreadableDoc/out/ (c1_unreadable_probe.py, receipt-as-is.{txt,json}, receipt-proposed.{txt,json}, proposed/citation-provenance.py, proposed-fix.diff, contrast/).
