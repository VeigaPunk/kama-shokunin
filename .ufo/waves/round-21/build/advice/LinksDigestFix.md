VERDICT: partial - digest ambiguity confirmed and patch packaged; requested selftests deferred by seat rule

Axes
- Calibration: demonstrated two distinct link maps with identical preimage bytes and SHA-256 under the current `name -> text\n` framing.
- Operability: producer now rejects ambiguous symlink names/targets; the receipt gate mirrors the rule.

Finding
- `install_links_sha256` is ambiguous: `{"x -> y":"z"}` and `{"x":"y -> z"}` collide; line feeds can also merge adjacent records (`{"a":"b\nc -> d"}` versus `{"a":"b","c":"d"}`).
- The exact witness command, exit 0, both hashes, and stdout are retained in `build/out/LinksDigestFix/collision-witness.txt`.

Patch
- Producer `install_links()` rejects LF in a symlink basename or link text and the literal ` -> ` in a basename, raising `SetupError('install-link-digest-ambiguous-input')` before hashing.
- Gate validation rejects the same fields. Gate selftest adds newline-name, delimiter-name, and newline-target receipt mutations; producer selftest exercises all three rejection paths.
- `install_tree()` and `install_tree_sha256` were not changed. Ordinary accepted link records keep the existing digest format.
- Patch: `build/out/LinksDigestFix/patch.diff` (generated from the scratch clone; generation command exit 0).

Verification
- Collision witness: command completed, exit 0; stdout is recorded verbatim in `collision-witness.txt`.
- `check-receipt.py --selftest`, `install-links-grid.py --selftest`, and producer `--selftest`: NOT RUN; no exit/stdout. [INFERENCE] The active editing-wave seat rule assigns tests to the parent post-integration and prohibits leaf verification. Requested commands are listed in `build/out/LinksDigestFix/selftest-status.txt` for the parent.
- LSP was unavailable in the mounted tool inventory; no LSP-backed operations were possible.
- No tools were installed or updated.

Risk and scope
- A real install containing a symlink whose basename has LF or ` -> `, or whose link text has LF, now fails setup rather than emitting a non-unique digest. This is intentional; ordinary soname names and targets remain unchanged.
- An early edit used a relative path and briefly touched the lane producer/gate excerpts; I immediately restored those blocks. Readback shows those excerpts match the original scratch baseline. The delivered patch was generated only from `/tmp/kama-r21-LinksDigestFix-6/lane`.
- No lane source change is intended. Main should run the three listed selftests after integration.
