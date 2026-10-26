# kama round 48 lesson

author: kama L1 (agent `KamaR48`); wave seats' drafts integrated by the L1 (named per row)
date: 2026-10-26
base: `33e005827742b29772b153cda036ec9f27f653be` (round-47 verifier spot-check; lane remote tip at launch)
freeze: `12284ba39fb1b46b43d43ee82423bebe08c700dc` (preregistration `.ufo/waves/round-48/preregistration.json`, `frozen_at_utc` 2026-10-26T22:19:34Z; KQ64 receipt `.ufo/waves/round-48/freeze/prereg-time-check.out` → `RESULT pass`, `exit=0`)
build: `380bcdff9c8af06997c482f6eb03db926a794a2b` (after the freeze, before the wave)
measured: SCORECARD §Round-48 measured results

## Claims

- **C1 calibration 7→7 — append-only-audit v3: the lane's append-only rule graded as declared, carve-outs included.** `registry/append-only-contract.tsv` gains a `region` cell (9 rows): SCORECARD.md's five head sections that `SCORECARD.md:6` declares re-derived are `exempt=` (ungraded while the section is not gutted: the window maximum of its line count must reach the parent's), `corpus/knowledge/consumer-registry.md` is graded `only=## Errata` (its heading declares that region append-only; round-47 seat K1Design D2), every declaration must bind (the line says append-only for that path and is not a negation; round-47 seat V1Ctr F1), and `regressed` reaches the exit code (round-47 seat X1Stable). Counter `tools/round48-append-audit-v3-check.py`: tool selftest, contract binding and required regions, lane equality with the counter's own recomputation plus a clean lane verdict, eleven fixtures with expectations written by construction (exact threshold, clamp, merge first parent, regression, CRLF/`--`, bad declarations; round-47 seat K1Fixture), stability from the round-48 base.
- **C2 operability 8→8 — live evidence a shortcut cannot replay (sourced on S492, S493).** Three b11909 receipts in schema `kama-llamacpp-live/v5` pin the model to Hugging Face revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81` (closure D6) and carry provenance the live tool verified at record time against the release archive and its member (D3); the replay compares a stable projection of the captured surfaces (D4) and has `--compare`; the counter replays all three receipts (D2), hashes the re-acquired files itself and refuses swapped URLs (D1). Counter `tools/round48-live-replay-v5-audit.py`.
- Routed items: r47-D1…D4, D6 → C2; r47-D5 → C1; r47-D7 → disclosed limit; r47-D8 → frontier (seat X9SourcesGuard); r47-D9 → Mistakes row 2.

## Gate

Rows opened this round, both `mined`, opened 2026-10-26 (registry lines `corpus/SOURCES.md` S492–S493):

- **S492** — https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf and https://huggingface.co/api/models/ggml-org/models-moved/revision/499bc8821c6b12b4e53c5bffcb21ec206f212d81, accessed 2026-10-26T22:09:23Z (`curl -sSI`, a download, the revision API; copy `.ufo/waves/round-48/c2/hf-revision-499bc882.txt`, committed at the freeze). Located quote (response headers): `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` and `x-linked-etag: "270cba1b…d256d"`; download sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; revision API `"sha": "499bc8821c6b12b4e53c5bffcb21ec206f212d81"`. Admit: the URL names the commit and serves S039's digest.
- **S493** — https://huggingface.co/docs/huggingface_hub/en/guides/download, accessed 2026-10-26T22:09:25Z (text copy `.ufo/waves/round-48/c2/hf-hub-download-doc.txt`). Located quote (§From specific version, 17 words): "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash." Admit: grounds the 40-hex pin rule (`PINNED_MODEL_URL` in `tools/kama-llamacpp-live.py`).
- status/recheck/used-by changes to existing rows: none. S490 stays as filed (the `main` resolve URL, round 47); S492 is the replay locator from round 48.

## Mistakes

| # | Class | Evidence | Captured-by | Fix (shown able to fail) |
|---|---|---|---|---|
| 1 | Superseded head text rewritten in place without being kept | `tools/append-only-audit.py` v3 at the base `33e00582` reports `regressed=1` on the `0718b6ab` SCORECARD.md event: its one graded line the repair `82b5e9d3` held and the base no longer holds is the round-45 authority banner (line 6); rounds 46 and 47 rewrote it without keeping the replaced text, although line 6 itself says the replaced head text is kept verbatim | none before round 48: v2 had no regions and its `regressed` was informational; the round-41/42 head counters check the banner's content, not its history | the build appended the r45 and r46 banners byte-exact (`SCORECARD.md` §Superseded head banners); v3 exits 1 on `regressed`, so the next in-place banner rewrite without an append fails the audit only when it sits inside a ≥20-line event — below that threshold it stays unwatched (limit, see SCORECARD §Round 48) |
| 2 | Receipt-tip precision (round-47 closure D9) | the round-47 report says the r41/r42/r43/pointer checks were re-run at the final tip `6b7e6cf8`; the committed `*-fix.out` receipts say `tip=3442d707` | the outside closure only | from round 48 every regression receipt cited in the report is re-run at the final lane tip and committed with its `tip=` line; the report names the receipt path per claim |
| 3 | Counter trusted the evidence it should check (round-47 closure D1) | the round-47 C2 counter accepted a rerun receipt's paths and digests as written (seat K2Cheat: host-cache copies, 0-byte fabricated reruns, forged `started_utc` all met it) | the round-47 wave (K2Cheat), not the freeze-time controls | the round-48 counter hashes the re-acquired files itself and refuses swapped URLs (`urlswap` leg); the r47-relabel control (fabricated v5 receipts + copying replay) fails it at `replay=0 urlswap=0` |
| 4 | Routed items dropped without capture (seat N5Mistakes) | r45-D1 deferred then dropped; r44-D2 closed without capture and recurred as r47-D9; r46-D4 and r44-D3 closed without capture (`.ufo/waves/round-48/w1/out/N5Mistakes/sweep.md` F1–F7) | the outside closure only | the round-48 preregistration carries a `routed` block naming r47-D1…D9 one by one (`.ufo/waves/round-48/preregistration.json`); the sweep's comparison of closure D-ids against that block flags any id it lacks (it would have flagged r45-D1 in the round-46 preregistration) |
| 5 | A schema bump broke the lane's own readers again | `tests/llamacpp-live/check-receipt.py` and `tools/gguf-identity.py` rejected the v5 receipts at the build (seat K0Harm F2/F3) — the round-47 Mistakes row "schema bump without updating its validator" repeated | seat K0Harm, not the build's own checks | both readers accept v5 at integration; `check-receipt.py --selftest` gains `v5-valid`, `v5-unverified`, `v5-member-digest-differs`, `v5-url-not-at-commit`, `v4-require-schema-v5-rejects-v4` (16 VALID, 107 mutations rejected) |

### Gate decisions from the wave (seat S1Gate, `.ufo/waves/round-48/w1/out/S1Gate/gate.md`)

- **Reject** `x-linked-etag` as proof of the revision (D6): it names the LFS object, served at any commit that holds it; the revision is carried by the URL's `/resolve/<40-hex>/` segment plus `provenance.model.commit`. Flip: never (a different field would be needed).
- **Reject** the CDN redirect target as a locator (D7): `curl -sSI` on the pinned URL returns a `302` to a signed `us.aws.cdn.hf.co/xet-bridge-us/…?…Expires=…` URL that expires. Flip: never.
- **Reject** a relabelled v2 tool, or the v3 contract with the SCORECARD row dropped, as C1 evidence (D3): controls `junk-c1-v2-relabel` and `junk-c1-drop-scorecard`, both `met=False`.
- **Admit** S492 and S493 (above); seat S1Rows re-opened both on 2026-10-26 and found the quotes verbatim.

### Wave

One v2 wave `kama-r48-w1`, 69 seats (critic 16, reviewer 13, executor 12, scribe 11, scout 5, mutation-tester 5, connector 4, simplifier 1, revenger 1, sentinel 1). Seat K1Hist reported itself blocked (its own recount did not implement the definitions); no finding is taken from it. Findings and the integration fixes they drove: SCORECARD §Round 48.
