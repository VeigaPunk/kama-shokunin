VERDICT: partial - both digests collide by construction and the gate accepts soname- and impl-dropping decoys under both pins; retarget detection still holds

Scope: C2 install-identity digests at committed a29bb84 (tools/kama-llamacpp-live.py:178-226; tests/llamacpp-live/check-receipt.py:165-198, 441-477). Producer and gate executed from a scratch clone of that commit. Receipts are the gate selftest scaffold with only the server block replaced by real-tree maps. I did not modify the lane. Its working tree has uncommitted edits by others (check-receipt.py +19/-, kama-llamacpp-live.py +48/-, errata.tsv, report-landing-audit.py); those are not analyzed. Read-only git commands ran in the real checkout; git may refresh the .git/index stat cache. No staging, no commits.

## 1. Answer: yes, both encodings are ambiguous (executed, probe-run2 exit 0)
- P1 tree, real files: {"notes-1.txt": sha(b"one"), "notes-2.txt": sha(b"two")} and {"notes-1.txt <sha(b"one")>\nnotes-2.txt": sha(b"two")} -> install_tree digest 18f9055c...2882 both (E1).
- P2 links, no newline: {"x -> y": "z"} and {"x": "y -> z"} -> install_links digest 356b43ee...07a2 both (E2).
- P3 links, soname shape: {"libllama-alias.so": "libllama.so.0", "libllama.so.0": "libllama.so"} and {"libllama-alias.so -> libllama.so.0\nlibllama.so.0": "libllama.so"} -> 5e1129f2...64cf both (E3).
- Cause: tree line `name + " " + sha + "\n"` admits "\n" in names. Links line `name + " -> " + text + "\n"` is ambiguous for " -> " or "\n" in a name or target. Linux creates all of these names.

## 2. Gate and real-tree results
- Minimal witness (minimal_witness-run2 exit 0): replace {"libggml-base.so": "libggml-base.so.0", "libggml-base.so.0": "libggml-base.so.0.27.0"} with {"libggml-base.so -> libggml-base.so.0\nlibggml-base.so.0": "libggml-base.so.0.27.0"}. Links digest b58f1b4d...9e10 is unchanged. The producer emits it for a directory with these symlinks. `check-receipt.py` with both pins prints VALID, exit 0.
- Links, exhaustive (needed_check-run3 exit 0): 6765 parses share the digest; the gate accepts 162 (1 identity + 161 decoys). All 161 decoys drop a DT_NEEDED soname of libllama-server-impl.so (readelf -d exit 0: libllama.so.0, libggml.so.0, libggml-base.so.0, libllama-common.so.0, libmtmd.so.0). None drops only other names. 503 surviving standalone names keep their target: 0 retargets.
- Tree, exhaustive contiguous runs (minimal_witness-run2 exit 0): 1275 tried, 273 accepted. 45 of 51 regular members are removable, including libllama-server-impl.so, the 14 libggml-cpu-*.so, LICENSE and llama-* tools. Never removable: llama-server and the 5 soname targets.
- Impl removed as a run successor, with tree and links pins: CLI exit 0. Adding --expect-server-impl-sha256: exit 1. Only that optional pin rejects it.
- Surviving names keep their content hash and target. Decoys are removal-only: no addition, no substitution, no retarget.

## 3. Exploitability on a release tree
- Precondition: write access to the install dir (drwxr-xr-x vgpnk; ls exit 0). A same-user process qualifies. No privilege gain.
- Effect: both pins pass while DT_NEEDED sonames are gone. llama-server start fails [INFERENCE: glibc lookup; server not launched]. No system libllama.so.0 exists here (ldconfig -p | grep -i llama, exit 1), so no fallback on this host. A host with a system copy could load another library [INFERENCE].
- No code injection, content swap or retarget found. A tarball with such names gives the same removal-only power.
- Severity: low for exploitation. Medium for the C2 claim: the pin does not identify the namespace.

## 4. Adjacent defects (executed unless marked)
- E6: a receipt may carry server_impl_sha256 while libllama-server-impl.so is absent from install_tree. Gate accepts without the impl pin.
- E7: a non-UTF-8 member name makes draft install_tree, install_links and both gate encoders raise UnicodeEncodeError. CLI exits 1, which reads as INVALID. Producer body catches it as internal:UnicodeEncodeError (code read at :1480-1481 and :1642-1658; not run).
- E8: subdirectories and FIFOs are invisible to both digests (lib/evil.so ignored).
- E14: json.load keeps the last duplicate key, so one receipt text can show two maps.
- tests/llamacpp-live/install-tree-grid.py:39-41 is a third copy of the tree encoding.

## 5. Proposed unambiguous encoding (out/proposal.py exit 0; checks C1-C6 PASS)
- install_tree_sha256: keep the bytes. Admit only names without "\n", strict UTF-8, digests of 64 lowercase hex (producer and gate; refuse otherwise). Injective on the admitted domain: split on "\n"; the last 64 bytes are the digest, preceded by " " (3000 random maps round-trip, 0 failures). Back-compat: real tree stays 6c216313...a2, pinned in 11 committed receipts (rounds 16-18), so this encoding must not change.
- install_links_sha256 (new this round; draft value b58f1b4d...9e10 appears in no committed file, git grep exit 1): sha256 of json.dumps(links, sort_keys=True, separators=(",",":"), ensure_ascii=True, allow_nan=False). The 6765-member class gets 6765 digests (legacy: 1). Real-tree golden 5cb9f486...6470060.
- Gate: refuse newline or non-UTF-8 tree keys. Require server_impl_sha256 null iff libllama-server-impl.so is absent. Reject duplicate JSON keys. Exit 2 for unencodable names. Add P1-P3, the minimal witness and the impl-successor receipt as mutations, with golden vectors in producer and gate.
- Optional policy: require DT_NEEDED soname presence. Digest equality is not completeness.

## 6. Not executed
- Loader and CPU-backend dlopen behavior, and a TOCTOU between lstat and open in install_tree: [INFERENCE].

## 7. Artifacts and reproduction
- out/LinksDigestEncoding/: probe.py (run2 exit 0; run1 exit 1 from my own wrong expectations, kept), proposal.py (exit 0), needed_check.py (run3 exit 0), extra_checks.py (exit 0), minimal_witness.py (run2 exit 0), gate-selftest.out (exit 0: 9 VALID + 1 NOT-EVALUATED, 90 mutations), receipts/*.json, JSON summaries.
- Reproduce: clone the lane to /tmp/kama-r21-LinksDigestEncoding/lane, checkout a29bb84, run the scripts (paths are hard-coded there).
- Tooling: none installed. python3 3.14.8 and /usr/bin/readelf were already present. Scratch removed after archiving.
