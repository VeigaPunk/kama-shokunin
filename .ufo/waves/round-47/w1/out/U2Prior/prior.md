# U2Prior - prior art for C2 (kama-llamacpp-live/v4 provenance)

Verdict: the v4 provenance block meets the core of the prior-art standard (URI + content digest per input, verify before use). It lacks four things that every cited tool records: the resolved immutable revision of each mutable URL (HF `main` -> commit; release tag -> commit), a descriptor-shaped record (digest-set keyed by algorithm), a recorded member digest inside the provenance block, and the producer identity (builder) of the receipt. None of them blocks replay today; the first is the only one that makes the receipt non-reproducible by drift.

## Receipt as it stands (observed)
`.ufo/waves/round-47/c2/live/receipt-1.json:391-401`:
- `provenance.model.url` = `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` + `sha256 270cba1b...`
- `provenance.server.asset_url` = `.../releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` + `asset_sha256 bf94332a...` + `member llama-b11909/llama-server`
- Outside the block: `server.sha256` (member digest, line 475), `server.install_tree`, `tool.sha256` (570), `/props` `build_info: "b11909-caa8191df"` (lines 63, 151). No full 40-hex commit, no HF commit, no asset size, no `uname`/arch.
- Replay (`tools/kama-live-replay.py:89-95, 142-147`) verifies the archive and model sha256 before extract; the member digest is only compared after the rerun (`compare`, 114-117), which is sound because the archive digest transitively pins the member.

## Primary sources

### 1. SLSA provenance v1.1 (+ in-toto ResourceDescriptor)
- https://slsa.dev/spec/v1.1/provenance (section BuildDefinition)
  - "a build that takes a git repository URI as a parameter might record the specific git commit that the URI resolved to as a dependency."
  - "Where practical, it is valuable to record the URI and digest of artifacts that, if compromised, could impact the build."
  - The same page's example: `externalParameters.ref = refs/heads/main` alongside `resolvedDependencies[].digest.gitCommit = 7fd1a60b...` - the parameter keeps the mutable name, the resolved dependency pins it.
- https://github.com/in-toto/attestation/blob/main/spec/v1/resource_descriptor.md
  - "A descriptor that specifies a `digest` is assumed to refer to an immutable resource or artifact."
  - fields: `uri`, `digest` {algorithm: hex}, `name`, `downloadLocation`, `mediaType`.
- Gap for kama: `main` is an unresolved ref in `provenance.model.url` and nothing records what it resolved to. The release tag `b11909` is also a ref; `build_info` carries only a 9-char abbreviation (`caa8191df`), not the full SHA the lane's own SOURCES row cites.

### 2. Nix fixed-output derivations / nixpkgs fetchers
- https://nix.dev/manual/nix/latest/store/derivation/outputs/content-address (Fixed-output content-addressing)
  - "To ensure that the downloaded file has not been modified, each derivation must also specify a cryptographic hash of the file."
  - "the calculated content address must match that given in the derivation, or the build of that derivation will be deemed a failure."
  - Rationale text: the URL may change (servers reorganised) without changing identity; identity is the hash, URL is only a fetch hint.
- https://raw.githubusercontent.com/NixOS/nixpkgs/master/doc/build-helpers/fetchers.chapter.md
  - "This hash refers to the derivation output, which can be different from the remote source itself!"
- Gap for kama: kama already matches the core (hash declared before fetch, mismatch = hard refuse, `digest-mismatch` deletes the file). Differences: (a) Nix pins the unpacked output; kama pins the archive and records the member digest only outside `provenance` (receipt line 475) - fold `server.member_sha256` into the block so the declaration is complete before use; (b) kama has one URL per input and no mirror, so a moved `models-moved` repo or a deleted tag makes replay refuse (exit 2) although the digest is still verifiable from another source. Nix's `urls` list / content-addressed mirrors cover this.

### 3. Hugging Face `huggingface_hub` revision pinning
- https://huggingface.co/docs/huggingface_hub/guides/download
  - "By default, the latest version from the `main` branch is downloaded."
  - "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash."
  - `hf_hub_download(..., revision="877b84a8f93f2d619faa2a6e514a32beef88ab0a")` and cached under `snapshots/<commit>/`; the dry-run result reports "their commit hash, file name and file size".
- Observed today (curl, 2026-10-26): `HEAD https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` -> `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `x-linked-etag: "270cba1b...bd256d"` (equal to the receipt's model sha256), `x-linked-size: 1185376`. `/api/models/ggml-org/models-moved` -> `sha 499bc882...`, lastModified 2025-10-28.
- Gap for kama: the URL is `resolve/main/`, i.e. the branch, not `resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/`. The sha256 still pins the bytes, so replay stays safe, but the receipt cannot say which repo state it was acquired from, and a future force-push of `main` turns a verifiable receipt into a dead URL with no way to find the old revision. Fix: record `model.revision` (40-hex from `x-repo-commit`) and have the URL use it (or keep both: `url` = pinned, `ref` = `main`).

### Supplementary: llama.cpp itself (not a provenance standard, but the identity the server reports)
- https://raw.githubusercontent.com/ggml-org/llama.cpp/master/common/build-info.cpp.in : `LLAMA_BUILD_NUMBER`, `LLAMA_COMMIT = "@LLAMA_BUILD_COMMIT@"`, `LLAMA_COMPILER`, `LLAMA_BUILD_TARGET`.
- https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md:1010 : `"build_info": "b(build number)-(build commit hash)"`.
- kama already captures `build_info` from `/props`; it does not cross-check it against `provenance.server.asset_url` (tag `b11909`) - a one-line consistency check (`build_info` startswith `b11909-` and the commit prefix equals the SOURCES row commit) would bind the running binary to the claimed release independent of the tarball digest.
- GitHub publishes an asset digest: `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` -> asset `llama-b11909-bin-ubuntu-x64.tar.gz` `digest: sha256:bf94332a...e695b`, size 22475032, `target_commitish: caa8191df159f764fb0160e3d2fc6be008948aee` - identical to the receipt's `asset_sha256`. So the receipt's digest is independently attestable from the publisher; the receipt does not say that it was, nor record the size.

## What a v4 receipt lacks by these standards (ranked by operability value)
1. Resolved revision of mutable refs: `provenance.model.revision` (HF commit `499bc882...`) and `provenance.server.release_commit` (`caa8191df159f764fb0160e3d2fc6be008948aee`). SLSA `resolvedDependencies`, HF full-length `revision`.
2. Member digest inside the block: `provenance.server.member_sha256` (currently `server.sha256`, line 475) so the declaration the replay tool validates before use is complete (Nix: the output hash is declared, not discovered).
3. Size per input (`asset_size` 22475032, `model_size` 1185376): cheap pre-download refuse on truncation and the HF dry-run shape; both are observable from headers.
4. Digest-set shape `{"sha256": hex}` and a per-input descriptor list (in-toto ResourceDescriptor) so a second algorithm or mirror `urls` can be added without a schema bump; v4's flat `asset_sha256` / `sha256` keys force a v5 for that.
5. Builder identity for the receipt itself: platform (`uname -m`, libc), llama.cpp `build_info` cross-check, and `tool.sha256` are present only partly (tool sha is, platform is not); SLSA `runDetails.builder` / `metadata.invocationId`.

Not a gap: digest-before-use, hard refusal on mismatch, https-only (`fetch`, line 59), unsafe member refusal, `filter="data"` extraction - all consistent with or stricter than the cited tools.

## Method / evidence
Commands run (all read-only; no installs): `read` of the three spec URLs; `curl -sI` and `curl -s` against huggingface.co; `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` (one request); `curl -sL` of raw.githubusercontent.com build-info.cpp.in, server README, in-toto resource_descriptor.md, nixpkgs fetchers chapter. No lane tool was run, no scratch was created. The HF commit/etag and the GitHub digest are observed at 2026-10-26 and can change independently of the receipt.
