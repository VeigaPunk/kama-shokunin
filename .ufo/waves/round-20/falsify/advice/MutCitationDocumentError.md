VERDICT: confirm - unreadable-document error boundary retained on pristine/restored bytes; verdict-exit mutant killed.

Scope: C1 calibration, only citation-document-unreadable and citation-valid-token positive control; no full 15-cell or exhaustive-error claim.
Source evidence: tools/citation-provenance.py:53-68 catches document OSError; :344-347 reserves exit 2 for docs_unreadable.
Pinned expectations: registry/error-injection-cells.json:11,14; tools/error-verdict-census.py:184-205 classifies unreadable+exit2 as error, unreadable+exit1 as could-not-evaluate.
Mutant: only /tmp/kama-r20-MutCitationDocumentError/citation-provenance.py:345 changed `return 2` to `return 1`, mapping unreadable documentation to the citation-failure exit.
No lane, committed evidence, production code or registry was modified.

Detector: unchanged census.child (30-second child bound) and census.classify_citation, with explicit expected exit/class checks; real CLI subprocesses, not mocked Git.
Fixture: unchanged census.git_fixture (:243-255), entirely private scratch; parent expressly permitted these fixture Git operations.
Fixture revision efddec83829db72f25cd69707b873464aa94404a; payload `census evidence\n`; SHA-256 846025bcb24be004c3953fb9c2ae1b38ad024a294294986b5c58a4f451e5769b.
Fixture registry contains one `fixture` row for that revision/evidence.txt/digest; doc.md contains its exact citation; absent.md does not exist (matching pinned :277 control).
Same bounded detector command on pristine, mutant and restored bytes:
`timeout 90s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 /tmp/kama-r20-MutCitationDocumentError/probe.py`
Exact unreadable-document child command:
`/usr/bin/python3 /tmp/kama-r20-MutCitationDocumentError/citation-provenance.py --lane /tmp/kama-r20-MutCitationDocumentError/fixture --registry /tmp/kama-r20-MutCitationDocumentError/required.json --docs /tmp/kama-r20-MutCitationDocumentError/absent.md --allow-off-ref --json`
Exact positive-control child command:
`/usr/bin/python3 /tmp/kama-r20-MutCitationDocumentError/citation-provenance.py --lane /tmp/kama-r20-MutCitationDocumentError/fixture --registry /tmp/kama-r20-MutCitationDocumentError/required.json --docs /tmp/kama-r20-MutCitationDocumentError/doc.md --allow-off-ref --json`

Observed output/exit:
| Bytes | Unreadable CLI exit / class | Positive CLI exit / class | Detector output / exit |
|---|---|---|---|
| pristine | 2 / error | 0 / accepted | detector: PASS / 0 |
| mutant | 1 / could-not-evaluate | 0 / accepted | detector: FAIL / 1 |
| restored | 2 / error | 0 / accepted | detector: PASS / 0 |
All children ran without timeout; detector-command stderr was empty.
Unreadable stdout counts in all three runs: {"required":1,"docs_unreadable":1,"found":0,"verified":0,"missing":1,"mismatch":0,"off_ref":0}; row status=missing, error=null, observed_sha256 equals the payload digest.
Unreadable stderr in all three runs: `citation-provenance: cannot read /tmp/kama-r20-MutCitationDocumentError/absent.md: [Errno 2] No such file or directory: '/tmp/kama-r20-MutCitationDocumentError/absent.md'` followed by newline.
Positive stdout counts in all three runs: {"required":1,"docs_unreadable":0,"found":1,"verified":1,"missing":0,"mismatch":0,"off_ref":0}; row status=ok, observed digest matches; stderr empty.
Verdict: KILLED, not baseline-inconclusive. The classifier rejects the mutant's exit/status disagreement rather than laundering it into a failed citation verdict.

SHA-256 restoration evidence:
- Before/pristine: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0
- Mutated: 4e6091f3301093cef20c890a2e306b58fb001d5902be4a5122046db3acf3f53c
- Restored and unchanged live source: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0
- Unchanged detector wrapper: 5c247ecbb2d3decdab637a2a5fe4a6f032bc61d55e5981b2dc0a6efcaf1dba83
- Unchanged census source copy: f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7
Restoration ran in finally: `cp -- /tmp/kama-r20-MutCitationDocumentError/pristine.py /tmp/kama-r20-MutCitationDocumentError/citation-provenance.py`, exit 0; subsequent cmp exit 0 and restored detector exit 0.
Cleanup: `rm -rf -- /tmp/kama-r20-MutCitationDocumentError && test ! -e /tmp/kama-r20-MutCitationDocumentError`, exit 0, no output.
No installations, services, model loads, fleet writes or sibling writes.
