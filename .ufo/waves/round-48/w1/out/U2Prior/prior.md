# U2Prior: prior art for record-time provenance verification (round 48, lane kama)

**Verdict:** the v5 receipt has the SLSA `resolvedDependencies` shape (URL + digest + commit) and the Nix fixed-output rule "the hash is the pin". It lacks the three things those standards treat as the point of provenance. (1) The receipt names no verifier and carries no signature. (2) The model URL is never fetched or queried at record time. (3) The asset digest is operator-supplied rather than cross-checked against an independent publisher record. Two smaller gaps: v5 verifies 1 of 51 archive members, and replay does not read the `verified` digests. Nothing here breaks the frozen C2 counter; these are claim-strength gaps, not regressions.

Lane commit read: 380bcdff9c8af06997c482f6eb03db926a794a2b files as they stand in the lane tree. I did not run the counters (not my item).

## Primary sources (quotes <= 25 words)

1. SLSA v1.0 Provenance, https://slsa.dev/spec/v1.0/provenance (read 2026-10-26; v1.2 is current)
   - "a build that takes a git repository URI as a parameter might record the specific git commit that the URI resolved to as a dependency"
   - Builder identity: "representing the transitive closure of all entities that are trusted to faithfully run the build and record the provenance"
2. SLSA v1.0 Verifying artifacts, https://slsa.dev/spec/v1.0/verifying-artifacts
   - "Ensuring that the builder identity is one of those in the map of trusted builder id's to SLSA level."
   - "Verifying the signature on the provenance envelope."
3. in-toto ResourceDescriptor, https://github.com/in-toto/attestation/blob/main/spec/v1/resource_descriptor.md
   - "A descriptor that specifies a `digest` is assumed to refer to an immutable resource or artifact."
   - It defines `uri`, `digest` (a set, e.g. sha256 and gitCommit in SLSA), `downloadLocation`, `name` and `annotations`.
4. Nix manual, Glossary "fixed-output derivation", https://nix.dev/manual/nix/2.34/glossary
   - "a cryptographic hash of the output is determined in advance using the outputHash attribute, and where the builder executable has access to the network"
   - Reading: the declared hash is the identity and the URL is only a locator. The fetch happens inside the build, so the check runs where the bytes arrive.
5. huggingface_hub download guide, https://huggingface.co/docs/huggingface_hub/guides/download
   - "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash."
   - The `revision` parameter takes a commit hash. The library returns files under `snapshots/<commit>/`. This matches v5's `PINNED_MODEL_URL` 40-hex rule (tools/kama-llamacpp-live.py:71).

## Mapping: kama v5 receipt vs the standards

| Standard field / rule | kama v5 | Status |
|---|---|---|
| SLSA `resolvedDependencies[].uri` + `digest` | `provenance.{server.asset_url, asset_sha256, member}`, `provenance.model.{url, sha256, commit}` | present |
| SLSA "URI resolved to commit" | `model.commit`, 40-hex, equal to the `/resolve/<commit>/` segment | present (string match only, see G2) |
| in-toto `digest` of an immutable artifact | sha256 for the archive, the member and the model | present |
| Nix FOD: hash compared where the bytes arrive | archive and member hashed before server start (kama-llamacpp-live.py:193-219) | present for the local archive |
| SLSA `builder.id` + signed envelope | none | **missing** (G1) |
| Record-time fetch or resolve of the URL | none | **missing** (G2) |
| Independent digest source | none | **missing** (G3) |

## What a v5 receipt still lacks

**G1. No verifier identity, no signature.** SLSA requires an identity ("builder.id") that a verifier maps to a trust level, plus a signed envelope. `provenance.verified` is `{at:"record", archive_sha256, member_sha256, model_sha256}`: a literal string and three digests, with no `by`/`verifier` field and no signature.
- The receipt has `tool:{path, sha256}`. The path is an absolute host path (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`), and the lane commit of the tool is not recorded.
- Replay accepts a v5 receipt whose `verified` is exactly `{"at":"record"}`. The check is `ver.get("at") != "record"` at tools/kama-live-replay.py:120-122, and the selftest fixture at :318 uses that stub.
- Replay never reads `archive_sha256`/`member_sha256`/`model_sha256` from `verified` (grep over the file finds them only in selftest and docs). So `verified` is an uncorroborated claim from whoever wrote the JSON. Replay's real defence is that it re-acquires and re-verifies everything.
- Fix: add `verified.by` = {tool sha256, lane commit, hostname-free verifier id}. Make replay require the three `verified` digests to equal `provenance.server.asset_sha256`, `server.sha256` and `model.sha256`. Optionally wrap the receipt in a DSSE envelope. Cheap and honest alternative: state in the schema doc that v5 is self-attested and signature-free.

**G2. The model URL is never fetched or queried at record time.** v5 hashes a caller-supplied local file (`--model`) against a caller-supplied `--model-sha256`. For the URL, `PINNED_MODEL_URL.match` only checks shape (kama-llamacpp-live.py:71, :1476-1479). Nothing establishes that the commit exists, that the file at that path in that commit has that digest, or that the local file came from that URL. install.txt says the file was fetched from the URL, but that is prose, not a field.
- Cheap record-time check, observed today: one HEAD on the pinned URL returns `x-repo-commit: 499bc882…` and `x-linked-etag: "270cba1b…"`. Both equal the receipt (evidence.txt).
- HEAD on `resolve/main` returns the same two values today, so a pinned URL carries no extra information until its response is compared with the declared values. That comparison is what makes a record-time check matter.
- Following the Nix FOD model, the sha256 is the pin and the commit is a locator. v5 treats the commit as verified-looking metadata. It is just the URL substring, copied to `model.commit`.
- Fix: before start, HEAD the URL with redirects off. Require `x-repo-commit` == `model.commit` and `x-linked-etag` == `--model-sha256`. Record both as `verified.model_remote = {x_repo_commit, x_linked_etag}`. Fail with a stable `setup-error` token otherwise. Alternatively fetch the model inside the tool (the FOD shape).

**G3. The asset digest is operator-supplied, with no independent source.** `--server-asset-sha256` is accepted as given. GitHub publishes a per-asset `digest` field on the release (`gh api repos/ggml-org/llama.cpp/releases/tags/b11909` returns `sha256:bf94332a…`, equal to the receipt value; evidence.txt). The tool never consults it. Hashing a local archive against a number the same operator typed is a self-consistency check, which is trust-on-first-use in SLSA's words (verifying-artifacts, "Forming Expectations": "Trust on first use"). The archive path used for verification is also not recorded.

**G4. Only 1 of 51 archive members is verified at record.** `verify_archive_member` checks the archive hash plus the single `llama-b11909/llama-server` member. The server executes the sibling `.so` files, and `server.install_tree` hashes all 51.
- I compared receipt-1's `server.install_tree` to the archive offline. All 51 entries equal the archive members, with none missing or extra, so this install is clean.
- The tool does not assert it. The other 50 files are covered only by the archive-level digest on the local copy, not by a per-file comparison of the running install against the archive.
- Fix: compare `install_tree` against the archive's member digests (same shape as `verified`), or record `verified.install_tree_matches_archive` with the count.

## Frontier: smallest moves that raise the claim strength

Ordered by cost:
1. Make replay compare the `verified` digests to the provenance and receipt fields (G1, a few lines).
2. HEAD the model URL at record time and record `x-repo-commit` and `x-linked-etag` (G2, no body download).
3. Optionally cross-check the asset sha against the GitHub release `digest` (G3).
4. Install-tree-vs-archive comparison (G4).
5. Add `verified.by` and sign the receipt (G1, largest).

Evidence: evidence.txt in this directory (HEAD headers and release digest, 2026-10-26T22:35Z).
