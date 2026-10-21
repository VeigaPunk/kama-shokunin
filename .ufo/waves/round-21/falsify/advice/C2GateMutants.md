VERDICT: partial - One canonical-encoding mutant survives --selftest; an independent Unicode receipt exposes it.
Attack: C2 install_links canonical-JSON ASCII-escaping invariant in tests/llamacpp-live/check-receipt.py at a6617149722c73d90e142fbdc8154d6967055f7e.
Axes: operability 8 + calibration 7; this probe supplies detector-coverage evidence, not an axis regrade or round judgment.

## Mutant and expected detector
- Isolated scratch: /tmp/kama-r21-C2GateMutants/lane, cloned from the lane and checked out at the target commit; no lane-source edits.
- Exactly one behavior-bearing token changed at line 178: `ensure_ascii=True` -> `ensure_ascii=False`; `.encode('ascii')` retained.
- [INFERENCE] Plausible defect: a JSON-formatting cleanup accidentally disables the canonical escaping requirement.
- Expected shipped detector: `--selftest`, particularly `links-canonical-digest-valid` (lines 2015-2023), should reject a canonicalization regression.
- Primary-source quote: “sorted keys, compact separators, ASCII escapes” (gate line 175, target revision above, opened 2026-10-21).

## Executed detector and outputs
Command: `/usr/bin/python /tmp/kama-r21-C2GateMutants/lane/tests/llamacpp-live/check-receipt.py --selftest`
- Pristine exit 0; mutated exit 0; restored exit 0. Each had empty stderr and identical stdout:
  `selftest: 11 VALID and 1 NOT-EVALUATED receipts accepted; 91 mutations + unreadable case rejected`
- Verdict against the requested detector: SURVIVED. Killing selftest cases: none. Neither baseline nor restoration was inconclusive.

## Independent killing witness
A synthetic otherwise-valid receipt has `install_links={"libllama-é.so":"libllama.so"}` and an independently computed escaped canonical JSON digest.
Canonical JSON bytes: `{"libllama-\u00e9.so":"libllama.so"}`; digest: `6babb5b23da0eb42cc8f447da61aeda79cddc6a170abacc907c69f0b400a9266`.
Command: `/usr/bin/python /tmp/kama-r21-C2GateMutants/lane/tests/llamacpp-live/check-receipt.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2GateMutants/unicode-canonical-receipt.json --require-install-links --expect-install-links-sha256 6babb5b23da0eb42cc8f447da61aeda79cddc6a170abacc907c69f0b400a9266`
- Pristine exit 0 and restored exit 0: `VALID /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2GateMutants/unicode-canonical-receipt.json`; stderr empty.
- Mutated exit 1: stdout empty; stderr ends `UnicodeEncodeError: 'ascii' codec can't encode character '\xe9' in position 11: ordinal not in range(128)`.
- Verdict against this added positive-validity witness: KILLED (valid-receipt rejection/crash, not a successful INVALID verdict).
- The shipped canonical case and shared fixture use ASCII-only link names; the escaping mutation is invisible to them. This is a coverage finding, not a defect reproduced in pristine gate bytes.
- Scope: one mutant only. Chain, shadow and flag branches were not separately mutated; this witness invokes both require/expect flags.

## Restoration and durable evidence
- Pristine SHA-256: `6b8764374f1cc1059ba7520f7e7a68f37acc6a31b3e72220f4b42826e72d4a61`.
- Mutated SHA-256: `97406fc39afc3cf362868ec4986e074960d501101eb3b564e993a042a6684b52`.
- Restored SHA-256: `6b8764374f1cc1059ba7520f7e7a68f37acc6a31b3e72220f4b42826e72d4a61`; exact byte equality confirmed after both restored detector runs (107992 bytes before/after).
- Fixture SHA-256: `99c0a7d965d5a321290a0d577577657a72c1ade15654d4b230629a7553ff167c`.
- Evidence directory: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2GateMutants/.
- `evidence.json`: exact argv, cwd, exit, complete stdout/stderr and hashes for all six invocations; `ascii-escaping-mutant.patch`: sole mutation; `unicode-canonical-receipt.json`: killing fixture.
- Cleanup command `rm -rf -- /tmp/kama-r21-C2GateMutants`: exit 0, stdout/stderr empty; scratch absence true, recorded in `cleanup.json`.
- All detector subprocesses completed; no live server, daemon, model download, official measurement, integration or commit was performed. Tool installs/updates: none.
