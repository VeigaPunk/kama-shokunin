VERDICT: partial - canonical-order mutant survives stock --selftest; an independent fixed-vector case kills it.
Axes: operability 8 (C2 receipt gate), calibration 7 (detector coverage); advisory evidence, not a round/score judgment.
Scope: exactly one plausible defect, confined to scratch `install_links_sha()` line 177. No other mutant tested.
Revision: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`.
Setup: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r21-LinksGateMutants/lane && git -C /tmp/kama-r21-LinksGateMutants/lane checkout -q a29bb84abbb8b4d328f5970a89e448330a3a42ac` → exit 0, no output.

## Mutant and expected detector
`for n in sorted(links)` → `for n in links`: digest follows insertion order instead of canonical basename order; see `mutant.patch`.
Detector D: `python3 /tmp/kama-r21-LinksGateMutants/lane/tests/llamacpp-live/check-receipt.py --selftest` (each invocation bounded by subprocess timeout 120 seconds).
[INFERENCE] A canonical-digest positive fixture should reject this gate mutation because the fixture's recorded digest must remain valid regardless of dictionary insertion order.
Source observation: `_selftest_receipt()` line 1645, the pin at line 1855, and `relink()` line 1974 derive their digest/expectation from the same helper under test.
[INFERENCE] This shared oracle masks the ordering defect; a survivor is a coverage finding, not a reason to change the digest contract.

## Executed detector outputs
| Detector/test bytes | Pristine exit | Mutated exit | Restored exit | Verdict |
|---|---:|---:|---:|---|
| Stock D | 0 | 0 | 0 | SURVIVED |
| D with only `killing-selftest.patch` added | 0 | 1 | 0 | KILLED |
Stock stdout, identical in all three arms (stderr empty):
`selftest: 9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected`
Augmented pristine/restored stdout (stderr empty):
`selftest: 10 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected`
Augmented mutated stdout empty; stderr:
`SELFTEST FAIL links-canonical-digest-valid: exit 1, want 0; stdout='INVALID /tmp/check-receipt-6rb3i57s/case-3-links-canonical-digest-valid.json: 1 problem(s)\n  - server.install_links_sha256 != recomputation over install_links'`

## Killing case for the survivor
`killing-selftest.patch` adds `links-canonical-digest-valid`: copy the valid receipt and replace only its links digest with an independent literal, expected CLI exit 0.
The existing fixture inserts `libllama.so.0` before `libllama-alias.so`, opposite canonical order.
Independent oracle command: `printf 'libllama-alias.so -> libllama.so.0\nlibllama.so.0 -> libllama.so\n' | sha256sum` → exit 0; stdout `5e1129f24f3c3b6f3d0cca22876663fc7ac39810b8b7287e7a9c0b350ff64bcf  -`.
Both augmented baseline arms pass and the same one-line mutant fails this named case. The patch changes no production contract.

## Hashes and exact restoration
Hash command H: `sha256sum /tmp/kama-r21-LinksGateMutants/lane/tests/llamacpp-live/check-receipt.py`; every H invocation exited 0, stderr empty.
Stock pristine/restored SHA-256: `01fbf81387f1a72bebf0b3ca76b9c50d9850300c5776ee49bcfcba709d46a121`.
Stock mutated SHA-256: `ad401ce7101f494aff7f90080f7d6b658c780bb56583c865a183f08392e1ba37`.
Augmented pristine/restored SHA-256: `a0a653dbd751b3448f55921929ae6aa61e4ddcd87b35dbb44e75af3c758bd121`.
Augmented mutated SHA-256: `e1197cbe6fb0e7ba1b37f596fa3e33073e54ebdc1ddfd92bfe9e2049df98c806`.
After removing the temporary case, H again returned the exact stock pristine hash.
`rm -rf /tmp/kama-r21-LinksGateMutants` → exit 0, no output; `test ! -e /tmp/kama-r21-LinksGateMutants` → exit 0, no output.
The absence check's first orchestration attempt did not start because its cwd had just been deleted; it was then executed from the out directory. Raw details are in `commands.json`.
No lane source/index, sibling source, live install, service, or official measurement changed; no persistent process started. No tools installed/updated.
Artifacts: this report, `commands.json` (actual argv/exit/stdout/stderr), `mutant.patch`, `killing-selftest.patch`; all are under this out directory.
Requested `build/advice/LinksGateMutants.md` was not written because the binding seat scope permits deliverables only under `build/out/LinksGateMutants/`; L1 owns placement/integration.
