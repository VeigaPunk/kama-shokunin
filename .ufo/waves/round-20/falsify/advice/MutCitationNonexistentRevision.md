VERDICT: confirm - the named nonexistent-revision mismatch verdict is distinct from infrastructure error; the assigned mutant was killed.
Mutation result: KILLED (pristine detector exit 0, mutated exit 1, restored exit 0).
Scope: only citation-nonexistent-revision and its citation-valid-token positive control; no full census or full selftest was run.
Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py:96-104,327-332.
Named binding: /home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-cells.json:12 expects failed; :14 expects accepted.
Detector: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/error-verdict-census.py:184-205,243-284.
The pinned run_citation builds a real isolated Git fixture; classify_citation requires exit 1 for a row mismatch, not exit 2.
Mutant: replace `elif error is not None or observed != want:` with `elif error is not None: raise ValueError(f"unusable Git: {error}")`, followed by `elif observed != want:` (formatted as normal Python blocks).
Only that behavior-bearing branch changed in /tmp/kama-r20-MutCitationNonexistentRevision/citation-provenance.py; production code and committed registry were not edited.
Expected detector: reject the mutant because a correctly tokenized all-f 40-hex revision must yield found=1, mismatch=1, row status=mismatch, exit=1 and class=failed.
Same bounded detector command, all three phases: /usr/bin/python3 -B /tmp/kama-r20-MutCitationNonexistentRevision/detector.py
The wrapper calls the unchanged pinned run_citation/classify_citation for exactly the two named cells; each child has a 30-second bound and the wrapper had a 100-second bound.
All fixture Git command cwd/TMPDIR paths were checked under the assigned scratch; each phase executed eight fixture Git commands there. No live-lane Git operation or install occurred.
Actual outputs (JSON field excerpts below are summaries, not full-output equality claims):
Pristine: detector exit=0, DETECTOR PASS; target child exit=1, stderr="", class=failed expected=failed.
Pristine target stdout: counts={required:1,docs_unreadable:0,found:1,verified:0,missing:0,mismatch:1,off_ref:0}; row status="mismatch", observed_sha256=null.
Target row error: "fatal: path 'evidence.txt' exists on disk, but not in 'ffffffffffffffffffffffffffffffffffffffff'".
Mutated: detector exit=1; target child exit=2, stdout="", class=error expected=failed.
Mutated target stderr: "citation-provenance: unusable Git: fatal: path 'evidence.txt' exists on disk, but not in 'ffffffffffffffffffffffffffffffffffffffff'\n".
Mutated detector stdout: DETECTOR FAIL citation-nonexistent-revision:classification,citation-nonexistent-revision:named-mismatch-witness.
Restored: detector exit=0, DETECTOR PASS; target child exit=1, stderr="", class=failed; same counts and mismatch row fields as pristine.
Positive control in all three phases: citation-valid-token child exit=0, stderr="", class=accepted; found=1, verified=1, mismatch=0, status="ok".
Positive control revision: efddec83829db72f25cd69707b873464aa94404a; claimed and observed SHA-256: 846025bcb24be004c3953fb9c2ae1b38ad024a294294986b5c58a4f451e5769b.
Exact recorded instrument commands (each followed by its observed exit):
pristine / citation-nonexistent-revision: /usr/bin/python3 /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-vqfniecn/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-vqfniecn --registry /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-vqfniecn/registry.json --docs /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-vqfniecn/doc.md --allow-off-ref --json ; observed exit=1 ran=true
pristine / citation-valid-token: /usr/bin/python3 /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-cxr2am8z/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-cxr2am8z --registry /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-cxr2am8z/registry.json --docs /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-cxr2am8z/doc.md --allow-off-ref --json ; observed exit=0 ran=true
mutated / citation-nonexistent-revision: /usr/bin/python3 /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-n9z3elwl/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-n9z3elwl --registry /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-n9z3elwl/registry.json --docs /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-n9z3elwl/doc.md --allow-off-ref --json ; observed exit=2 ran=true
mutated / citation-valid-token: /usr/bin/python3 /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-kno859pf/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-kno859pf --registry /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-kno859pf/registry.json --docs /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-kno859pf/doc.md --allow-off-ref --json ; observed exit=0 ran=true
restored / citation-nonexistent-revision: /usr/bin/python3 /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-m6dpdtzx/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-m6dpdtzx --registry /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-m6dpdtzx/registry.json --docs /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-m6dpdtzx/doc.md --allow-off-ref --json ; observed exit=1 ran=true
restored / citation-valid-token: /usr/bin/python3 /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-jxhyviox/tools/citation-provenance.py --lane /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-jxhyviox --registry /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-jxhyviox/registry.json --docs /tmp/kama-r20-MutCitationNonexistentRevision/error-verdict-citation-jxhyviox/doc.md --allow-off-ref --json ; observed exit=0 ran=true
SHA-256 and restoration evidence:
Pristine scratch/source before: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0.
Mutated scratch: 19958a217bb8171da4f4ae6f852acd1a5133c41ced73ee39bb3a97134784db25.
Restored scratch: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0; exact byte comparison with original=true; restoration used a finally block.
Live source after: 414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0; byte-equal to before=true.
Live registry before/after: ff3b7da9c060a7f12a7ca081c79db06899a4f5c9418d26ffe4a88bc6c607f469; byte-equal=true.
Pinned census SHA-256: f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7.
Bounded wrapper SHA-256: 6f50299febe7cd97f450a6ae9ea4a44e13f0d690d904bf9bf5223e7cb6484e33.
Cleanup command: rm -rf -- /tmp/kama-r20-MutCitationNonexistentRevision; observed exit=0, no output.
Cleanup observation: scratch_exists_after_cleanup=false; scratch_cleanup_confirmed=true. Scratch detector, copied source and all fixtures removed before return.
Limitation: this kills only the assigned plausible defect in the finite named detector; it does not establish exhaustive error-versus-verdict coverage.
Report: .ufo/waves/round-20/falsify/advice/MutCitationNonexistentRevision.md
