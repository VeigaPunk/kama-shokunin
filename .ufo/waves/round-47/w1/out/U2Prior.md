# U2Prior report

Verdict: kama v4 provenance meets the core of SLSA / in-toto / Nix / huggingface_hub practice (URI + sha256 per input, verify before use, refuse on mismatch). It lacks resolved revisions of its two mutable refs, the member digest inside the block, input sizes, a descriptor/digest-set shape, and builder identity.

Key findings (detail and quotes: `.ufo/waves/round-47/w1/out/U2Prior/prior.md`):
- Model URL is `resolve/main/...` (receipt-1.json:394). Today `main` resolves to HF commit `499bc8821c6b12b4e53c5bffcb21ec206f212d81` (`x-repo-commit`, curl HEAD); `x-linked-etag` equals the receipt model sha256. huggingface_hub: "By default, the latest version from the `main` branch is downloaded." - pin by full 40-hex revision.
- Release tag `b11909` has no full commit in the receipt (`build_info` is the abbreviation `b11909-caa8191df`); GitHub's API gives `target_commitish caa8191df159f764fb0160e3d2fc6be008948aee`, asset `digest sha256:bf94332a...` size 22475032 - matches the receipt, but the receipt records neither size nor commit. SLSA: record "the specific git commit that the URI resolved to as a dependency."
- Member digest is at `server.sha256` (line 475), outside `provenance`; replay compares it only after the run (kama-live-replay.py:114-117). Safe via the archive digest, but not declared up front as Nix fixed-output does.
- Replay already refuses on digest mismatch, non-https, unsafe member; no gap there.

Proposed v4.1 fields: `provenance.model.revision`, `provenance.server.release_commit`, `provenance.server.member_sha256`, `*_size`, optional `urls[]` mirrors; plus a `build_info` vs. asset-tag consistency check.

No lane tool run, no scratch created, no tools installed.

Written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Prior/prior.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Prior.md
