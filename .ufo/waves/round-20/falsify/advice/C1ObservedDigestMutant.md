VERDICT: confirm - the isolated comparison-removal mutant is killed specifically by the observed-digest selftest; pristine/restored controls pass.

## Mutant and expected detector
- Probe axes: behavioral sensitivity, scratch isolation, byte-exact restoration.
- Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py:102.
- Sole mutation in /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance.py:102: `elif error is not None or observed != want:` -> `elif error is not None:`.
- Blob lookup and lookup-error rejection remain intact; only the observed-versus-expected digest comparison is removed.
- Detector source: /home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py:292-307. Registry and citation agree on the SHA-256 of `different payload\n`, but the resolved blob contains `payload\n`; expected (missing, mismatch, verified) = (0, 1, 0).

## Exact bounded behavioral command
The following identical command ran on pristine, mutated and restored bytes, with cwd /tmp/kama-r20-C1ObservedDigestMutant and a 60-second tool deadline:
```sh
/usr/bin/env -i PATH=/usr/bin:/bin HOME=/tmp/kama-r20-C1ObservedDigestMutant TMPDIR=/tmp/kama-r20-C1ObservedDigestMutant GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance.py --selftest
```
Pristine positive control: exit 0; stdout:
```text
selftest: ok (24 cases)
```
Pristine stderr:
```text
citation-provenance: cannot read /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance-v6m2pzcf/lane/absent.md: [Errno 2] No such file or directory: '/tmp/kama-r20-C1ObservedDigestMutant/citation-provenance-v6m2pzcf/lane/absent.md'
```
Mutant: exit 1; stdout empty; stderr:
```text
citation-provenance: cannot read /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance-6bcasera/lane/absent.md: [Errno 2] No such file or directory: '/tmp/kama-r20-C1ObservedDigestMutant/citation-provenance-6bcasera/lane/absent.md'
SELFTEST FAIL observed-digest: {'required': 1, 'docs_unreadable': 0, 'found': 1, 'verified': 1, 'missing': 0, 'mismatch': 0, 'off_ref': 0}
```
Restored positive control: exit 0; stdout:
```text
selftest: ok (24 cases)
```
Restored stderr:
```text
citation-provenance: cannot read /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance-5jez0e4z/lane/absent.md: [Errno 2] No such file or directory: '/tmp/kama-r20-C1ObservedDigestMutant/citation-provenance-5jez0e4z/lane/absent.md'
```
The unreadable-document diagnostic occurs in all three runs; the mutant's only SELFTEST FAIL is observed-digest. Mutation verdict: **killed**, not a baseline failure or crash-as-rejection.

## Hashes, restoration and cleanup
- SHA-256, production source before/after restoration and pristine/restored scratch checker: `414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0`.
- SHA-256, mutated scratch checker: `66a359370449b443532702e3cf00829c869d02b47edeec73b92164e706d416a1`.
- Exact restoration: `cp -- /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance.pristine.py /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance.py`; then `cmp -s /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance.pristine.py /tmp/kama-r20-C1ObservedDigestMutant/citation-provenance.py` succeeded (exit 0), followed by matching SHA-256 outputs for production, pristine backup and restored copy.
- Cleanup command: `rm -rf -- /tmp/kama-r20-C1ObservedDigestMutant && test ! -e /tmp/kama-r20-C1ObservedDigestMutant && printf '%s\n' 'scratch_removed=yes'`; exit 0, stdout `scratch_removed=yes`.
- Only the private scratch and this report were written. No lane source, committed evidence or registry was modified; no tools installed.
- Scope: confirms this one selftest detects this one plausible defect; no exhaustive citation or C1 regression-coverage claim.

Report: .ufo/waves/round-20/falsify/advice/C1ObservedDigestMutant.md
