# U2Prior report (round 48, kama)

**Verdict:** kama v5 matches the SLSA resolvedDependencies/in-toto digest shape and the Nix fixed-output "hash is the pin" rule. It lacks a verifier identity or signature, any record-time fetch or query of the model URL, and an independent source for the asset digest.

Full note: .ufo/waves/round-48/w1/out/U2Prior/prior.md. Evidence: .ufo/waves/round-48/w1/out/U2Prior/evidence.txt.

## Sources (quotes in prior.md)
- SLSA provenance v1.0: https://slsa.dev/spec/v1.0/provenance
- SLSA verifying artifacts: https://slsa.dev/spec/v1.0/verifying-artifacts
- in-toto ResourceDescriptor: https://github.com/in-toto/attestation/blob/main/spec/v1/resource_descriptor.md
- Nix glossary (fixed-output derivation): https://nix.dev/manual/nix/2.34/glossary
- huggingface_hub download guide (revision = full 40-hex commit): https://huggingface.co/docs/huggingface_hub/guides/download

## Findings (what v5 still lacks)
- G1 No verifier identity or signature. tools/kama-live-replay.py:120-122 accepts `verified={"at":"record"}` alone (the selftest fixture at :318 does exactly this). It never compares `verified.{archive,member,model}_sha256` to anything. Fix: replay checks them against `provenance.server.asset_sha256`, `server.sha256`, `model.sha256`; add `verified.by`.
- G2 The model URL is never fetched or queried at record time. tools/kama-llamacpp-live.py:71 and :1476-1479 check only the URL shape. A single HEAD on the pinned URL returns `x-repo-commit` and `x-linked-etag` equal to the receipt (evidence.txt); resolve/main returns the same values today. Fix: HEAD with redirects off, require both to match, record them in `verified.model_remote`.
- G3 The asset sha is operator-supplied. GitHub's release API publishes a `digest` for the asset (`sha256:bf94332a…`, matches); the tool does not consult it. The archive path used is not recorded.
- G4 Only 1 of 51 archive members is verified at record (kama-llamacpp-live.py:193-219). I compared receipt-1 `server.install_tree` to the archive offline: all 51 match.

Did not run the C1/C2 counters (not in this item). No lane edits; scratch removed.

Tooling installs: none.
