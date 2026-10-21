VERDICT: confirm - malformed [1] fails closed as registry error; removing the row guard is killed, and exact restoration restores passing behavior.

Scope: one defect, private /tmp/kama-r20-MutCitationMalformedRegistry only; final evidence uses real CLI subprocesses and real scratch-only Git, without mocks.
Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py:79-80 guards non-object rows with ValueError("registry rows must be JSON objects").
Mutant: delete only those two lines; malformed integer then reaches row.get at original :84 (mutant :82).
Expected detector: malformed [1] must return exit 2, empty stdout, and stderr exactly 'citation-provenance: registry rows must be JSON objects\n'.
Source support: original :330-332 converts ValueError into exit 2; original :208-213 already pins this malformed-row CLI selftest.

All probe children used PATH=/usr/bin:/bin, HOME=/tmp/kama-r20-MutCitationMalformedRegistry, LC_ALL=C, TMPDIR=/tmp/kama-r20-MutCitationMalformedRegistry, GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_SYSTEM=/dev/null.
Fixture: /tmp/kama-r20-MutCitationMalformedRegistry/fixture/evidence.txt contained bytes b'payload\n'.
Fixture revision: cc0c7c8282afbb52b525d8ae87cd80f2f588f800; payload SHA256: d4e4877bac978b7952f0d544fc52ebff5411d351d129f1f056fa43f11da9af2b.
Fixture creation (each exit 0; author/committer date 2000-01-01T00:00:00+0000):
/usr/bin/git -c core.hooksPath=/dev/null -C /tmp/kama-r20-MutCitationMalformedRegistry/fixture init -q --template=
/usr/bin/git -c core.hooksPath=/dev/null -C /tmp/kama-r20-MutCitationMalformedRegistry/fixture add -- evidence.txt
/usr/bin/git -c core.hooksPath=/dev/null -C /tmp/kama-r20-MutCitationMalformedRegistry/fixture -c user.name=t -c user.email=t@example.invalid commit -q -m fixture
Malformed fixture: /tmp/kama-r20-MutCitationMalformedRegistry/malformed.json contained '[1]\n'.
Positive fixture: /tmp/kama-r20-MutCitationMalformedRegistry/valid.json contained one object with id=positive, the revision/digest above, path=evidence.txt; /tmp/kama-r20-MutCitationMalformedRegistry/doc.md contained the exact matching cite(rev, evidence.txt, sha256=digest) token.

Exact bounded detector command, unchanged for pristine/mutated/restored:
timeout 75s /usr/bin/python3 -B /tmp/kama-r20-MutCitationMalformedRegistry/probe.py
It ran the following exact commands, with 15s/15s/30s subprocess timeouts respectively:
/usr/bin/python3 -B /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.py --lane /tmp/kama-r20-MutCitationMalformedRegistry/fixture --docs /tmp/kama-r20-MutCitationMalformedRegistry/doc.md --allow-off-ref --registry /tmp/kama-r20-MutCitationMalformedRegistry/malformed.json
/usr/bin/python3 -B /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.py --lane /tmp/kama-r20-MutCitationMalformedRegistry/fixture --docs /tmp/kama-r20-MutCitationMalformedRegistry/doc.md --allow-off-ref --registry /tmp/kama-r20-MutCitationMalformedRegistry/valid.json
/usr/bin/python3 -B /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.py --selftest
The detector required the exact malformed error, exact positive counts below, and passing built-in selftest.

Observed exits:                   pristine   mutated   restored
Bounded detector                      0         1          0
Malformed [1] CLI                     2         1          2
Valid positive-control CLI            0         0          0
Built-in --selftest                   0         1          0
Pristine/restored malformed stdout=''; stderr='citation-provenance: registry rows must be JSON objects\n'.
Mutant malformed stdout=''; stderr was a traceback ending "AttributeError: 'int' object has no attribute 'get'" at mutant :82.
Positive stdout in all three runs: 'required=1 docs_unreadable=0 found=1 verified=1 missing=0 mismatch=0 off_ref=0\n'; positive stderr=''.
Pristine/restored selftest stdout='selftest: ok (24 cases)\n'.
Mutant selftest stdout=''; actual failure prefix:
SELFTEST FAIL cli-malformed-registry-row: expected exit=2 stdout~=None stderr~='registry rows must be JSON objects'; got exit=1 stdout=''
All selftest runs also emitted the expected missing-doc fixture diagnostic; baseline/restored nevertheless exited 0.
Verdict: KILLED, not an inconclusive baseline failure. A crash/nonzero alone was not counted as registry rejection.

SHA256 pristine source, untouched lane before/after, and restored scratch:
414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0
SHA256 mutated scratch:
efaf254537fc879ae20d4ff50e9583d1efc04519cacd6528638ccda2f415ff35
Restoration: cp /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.pristine.py /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.py executed in finally; exit 0.
Exact-byte comparison: cmp --silent /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.pristine.py /tmp/kama-r20-MutCitationMalformedRegistry/citation-provenance.py exited 0; final sha256sum exited 0 and matched lane/pristine/restored.
Cleanup: rm -rf -- /tmp/kama-r20-MutCitationMalformedRegistry exited 0; subsequent existence check printed FINAL SCRATCH ABSENT: True.
No live lane/index, committed evidence, registry, sibling, or production bytes were modified. No tools installed.
Report: .ufo/waves/round-20/falsify/advice/MutCitationMalformedRegistry.md
