VERDICT: confirm - The no-Git control kills the preflight-removal mutant; pristine and restored bytes return error, not an ordinary failed citation.

Scope: one isolated mutation of tools/citation-provenance.py; no lane/registry/evidence edits. This is a bounded control, not an exhaustive error census.
Mutant: delete the Git-availability preflight at tools/citation-provenance.py:72-75. Plausible defect: treating the preflight as redundant allows git_blob's caught OSError (lines 45-49) to become a row mismatch (lines 96-103).
Expected detector: registry/error-injection-cells.json:10 pins citation-git-unavailable to error; tools/error-verdict-census.py:184-205 supplies the unmodified classifier.
Detector used the pinned env_for/child/classify_citation helpers directly, with a 10-second child timeout. Assertion: child ran, exit=2, class in {error,could-not-evaluate}; failed is forbidden.

Exact child argv, identical for pristine/mutated/restored and both positive controls:
/usr/bin/python /tmp/kama-r20-MutCitationGitError/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationGitError --registry /tmp/kama-r20-MutCitationGitError/registry.json --docs /tmp/kama-r20-MutCitationGitError/doc.md --allow-off-ref --json
Cwd: /tmp/kama-r20-MutCitationGitError
No-Git environment: PATH=''; HOME=TMPDIR=/tmp/kama-r20-MutCitationGitError; LANG=LC_ALL=C.UTF-8; GIT_CONFIG_NOSYSTEM=1; GIT_CONFIG_GLOBAL=/dev/null; GIT_OPTIONAL_LOCKS=0; PYTHONDONTWRITEBYTECODE=1.
Fixture: one row id=fixture, rev=ffffffffffffffffffffffffffffffffffffffff, path=evidence.txt, sha256=846025bcb24be004c3953fb9c2ae1b38ad024a294294986b5c58a4f451e5769b; doc contains its exact cite token.

Observed no-Git outputs:
- Pristine: child exit=2; class=error; assertion PASS; stdout=''; stderr="citation-provenance: [Errno 2] No such file or directory: 'git'\n".
- Mutated: child exit=1; class=failed; assertion FAIL; stderr=''. JSON stdout follows (whitespace compacted only):
{"counts":{"required":1,"docs_unreadable":0,"found":1,"verified":0,"missing":0,"mismatch":1,"off_ref":0},"results":[{"id":"fixture","rev":"ffffffffffffffffffffffffffffffffffffffff","path":"evidence.txt","sha256":"846025bcb24be004c3953fb9c2ae1b38ad024a294294986b5c58a4f451e5769b","documents":["/tmp/kama-r20-MutCitationGitError/doc.md"],"observed_sha256":null,"error":"FileNotFoundError","status":"mismatch"}]}
- Restored: child exit=2; class=error; assertion PASS; stdout=''; stderr identical to pristine.
Mutation verdict: KILLED, not a baseline-failure inference. The mutant actually emitted the prohibited ordinary failed-citation result.

Positive controls, after exact source restoration, same argv/timeout with PATH=/usr/bin:/bin and GIT_AUTHOR_DATE=GIT_COMMITTER_DATE=2000-01-01T00:00:00Z:
- Existing fixture above, Git available: exit=1, class=failed, stderr=''; counts={required:1,docs_unreadable:0,found:1,verified:0,missing:0,mismatch:1,off_ref:0}; row error="fatal: path 'evidence.txt' exists on disk, but not in 'ffffffffffffffffffffffffffffffffffffffff'". PASS: genuine unresolved revision stays an ordinary failed citation.
- Registry/doc changed only in scratch to valid fixture revision efddec83829db72f25cd69707b873464aa94404a: exit=0, class=accepted, stderr=''; counts={required:1,docs_unreadable:0,found:1,verified:1,missing:0,mismatch:0,off_ref:0}; observed_sha256=846025bcb24be004c3953fb9c2ae1b38ad024a294294986b5c58a4f451e5769b; row status=ok,error=null. PASS.
Fixture creation used the existing census git_fixture helper (tools/error-verdict-census.py:243-255), only inside the private scratch, after coordinator explicitly permitted scratch Git operations.
Its argv sequence was: git init -q --template=; git add -- evidence.txt; git -c 'user.name=census fixture' -c user.email=fixture@example.invalid commit -q -m fixture; git rev-parse HEAD. All exited 0; helper returned efddec83829db72f25cd69707b873464aa94404a.

SHA-256 evidence:
- Pristine source/copy: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0
- Mutated copy: a0f5d497f1307a173e5f39a11440f05c68b909bc6efa134370fe434402b7fbe2
- Restored copy: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0
- Unmodified detector source: f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7
Restoration ran in finally; byte-for-byte comparison to the original returned True. After controls, source_unchanged=True and scratch_restored_exact=True.
Cleanup: shutil.rmtree('/tmp/kama-r20-MutCitationGitError'); observed scratch_removed=True. No tools installed; no production changes.
