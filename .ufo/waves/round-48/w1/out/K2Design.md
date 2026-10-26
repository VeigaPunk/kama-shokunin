# K2Design — round 48 C2 design critic (operability)

Verdict: **C2 v5 is genuinely more operable than v4 and passes its own counter at the build tip (met=True, replayed=3/3 on my run), but the record-time "verified" provenance never ties the pinned model URL to the model bytes; the stable projection has two demonstrable blind spots; v4 receipts are still accepted against the moving `main` ref; and the b11909 prerelease / huggingface.co dependence (closure D7) remains unhardened.** Four defects + smallest corrections below. Counter/tools frozen: nothing edited in place; proposed changes are in `K2Design-proposed.patch` (this directory).

## Evidence (all run by me, 2026-10-26)

1. C2 counter at the build tip (scratch clone `git clone --shared`; `$S=/fast/scratch/hyaku/kama-r48/K2Design`):
   ```
   $ python3 tools/round48-live-replay-v5-audit.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S
   receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
   tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:34:32.333460+00:00
   ```
2. The recordcheck positive control's model URL (counter fixture, round48-...-audit.py:306-321) is `https://huggingface.co/x/y/resolve/<40×a>/m.gguf`. Live probe:
   ```
   $ curl -s -o /dev/null -w '%{http_code}\n' -I https://huggingface.co/x/y/resolve/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/m.gguf
   401
   ```
   That URL cannot serve the recorded stub digest, yet the positive control starts the stub server (marker written) — i.e. the tool records `provenance.verified.at=record` without the model URL being able to serve the model bytes.
3. The real pinned URL does serve the recorded bytes today:
   ```
   HTTP/2 302 ; x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81
   x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
   ```
4. Offline `kama-live-replay.py --compare` demos against a copy of receipt-1 (variants in this directory):
   | variant | change | exit |
   |---|---|---|
   | inst.json | port, child_pid, utc times, term_wait_ms, log_lines, models `created` | 0 (expected) |
   | stab.json | `props.fields.default_generation_settings.n_ctx` 256→513 | 1 (expected) |
   | health-body.json | `/health` body+digest | 1 (expected) |
   | **props-body.json** | **`captures.props.body_sha256`+body changed, fields untouched** | **0 — blind spot** |
   | **models-body.json** | **`captures.models.body_sha256`+body changed outside id/owned_by/name** | **0 — blind spot** |
5. v4 acceptance (static): `provenance()` in `kama-live-replay.py:96-123` checks the 40-hex commit only in the v5 branch (114-122). Loading the committed round-47 receipt (`receipt-1-r47-v4.json`): `v4 provenance ACCEPTED (no commit check): commit_key_absent=True` with model URL `.../resolve/main/tinyllamas/stories260K.gguf`. Control: flipping the v5 commit to "zz" is refused (`provenance-bad-commit`).

## Findings

### F1 — Record-time verification does not bind the model URL to the model bytes (defect)
`tools/kama-llamacpp-live.py`:
- `--model-url` is used only for shape checks (`parser.error` at 1467-1479, `PINNED_MODEL_URL.match` at 1475) and for the provenance record (1497). Grep: no fetch/call to the URL anywhere in the tool.
- The v5 `provenance.verified` block is computed from **local files**: archive+member via `verify_archive_member(..., 1559-1566)` and `model_sha256 = sha256_file(args.model)` (1548-1554, 1566), where `--model` is a local path argument (1148-1151, required at 1447-1449).
- So "verified at record time against … the model" means "hashed the local model file"; the URL↔bytes binding only happens at replay (replay `acquire()` at `kama-live-replay.py:126-132` refuses with `digest-mismatch`, exit 2). A typo in the commit (401/404 revision) or a well-formed pinned URL serving different bytes records as "verified" and shows up only when a fresh session replays. The record-47 install note (`.ufo/waves/round-48/c2/live/install.txt:6`) shows the binding was actually done out-of-band by the L1's own fetch, not by the tool.
- Impact: the C2 claim "carry provenance the live tool verified at record time against … the model" overstates what the tool verifies; the counter's `recordcheck` leg itself encodes the gap (positive control uses a URL that cannot serve the digest).
- **Smallest correction** (proposed patch §1): in v5 (`--server-archive` given), the live tool fetches `--model-url` itself before starting the server, refuses (`provenance-model-url-digest-mismatch`, exit 2, no server) unless sha256(fetched) == `--model-sha256`, and runs the server against the fetched bytes. Effect: `provenance.verified.model_sha256` becomes a genuine attestation that the URL serves those bytes. Fixture ripple: the recordcheck positive control must then serve the stub model over a local https endpoint (stdlib `http.server`+`ssl` with a self-signed CA and `SSL_CERT_FILE` in the counter env — urllib's default context honors it) and new negative cases (URL serves wrong bytes → refuse; URL unreachable → refuse before server start).

### F2 — Stable projection drops already-captured body digests for props and models (blind spot)
`kama-live-replay.py` `projection()` (154-174) and the counter's `projection()` (`round48-live-replay-v5-audit.py:206-226`) compare `props.fields` (the five selected fields, 823-830) and the parsed models body (id|owned_by, models[].name), but **not** `captures.props.body_sha256` / `captures.models.body_sha256`, even though the live tool captures and hashes both bodies (`ready_captures`, 802-850). Demonstrated: `props-body.json` and `models-body.json` compare exit 0 (match) while `health-body.json` and `stab.json` exit 1. Drift in any stable-but-unselected content of `/props` or `/v1/models` passes a replay.
- **Smallest correction** (patch §2): add `"props_body": _get(rec,"captures","props","body_sha256")`, `"models_body": _get(rec,"captures","models","body_sha256")` and `"loading_bodies": [len(loading_503_bodies or []), loading_bodies_dropped]` to both projection functions; extend the compare leg with the two new stable-surface variants. Cost ≈ 0 (bytes are already captured and hashed).

### F3 — v4 receipts still accepted: accepted against the moving `main` ref, and unexercised by the counter
- What a v4 replay now verifies that it did not in round 47: (i) the equal stable projection of captured surfaces (D4) — round 47 compared only schema/outcome/digests/checks; (ii) the instance-vs-stable separation exposed as `--compare`. The member-binary pre-check predates this round (round-47 seat Sen2Replay). Note v4 reruns are still *not* record-verified (no `--server-archive` → live tool emits v4, no `verified` block), so v4 evidence relies solely on replay-time download proof.
- Hazard: `provenance()` accepts a v4 receipt without any commit check (demonstrated with `receipt-1-r47-v4.json`, URL `resolve/main`). The r46/r47 receipts' model locator is the moving `main` ref (S490); if HF moves `main`, those receipts permanently refuse at replay — not because evidence changed but because the locator moved. The r48 counter never exercises a v4 replay (the replay leg loops only the three v5 receipts, `round48-...-audit.py:398-434`), so a break would be silent until someone replays by hand.
- **Smallest correction** (patch §3): move the 40-hex `/resolve/<commit>/` check from the v5 branch to common `provenance()` code (runs before any `acquire`), so an unpinned v4 receipt is refused with `provenance-unpinned-model-url` before any network. This retires the S490 receipts by design (document it); add a cheap offline counter leg: copy the committed r47 receipt, assert exit 2 + token and that no download directory was created.

### F4 — External dependence on the GitHub prerelease b11909 and huggingface.co (closure D7, unhardened)
`kama-live-replay.py` acquires both inputs from the network (`acquire`, 126-132). D7 (round-47 closure) disclosed the prerelease cliff and deferred cache hardening; this round shipped without it. If the b11909 prerelease tag/assets are pruned, all three v5 receipts permanently refuse at replay (fetch fails → `could-not-run`, exit 2). The HF side is less fragile (revision-pinned, S492) but a repo deletion would break it too. A local digest-keyed cache does not cross machine boundaries, so it does not serve a "fresh session".
- **Smallest correction** (patch §4): vendor the two pinned inputs in the lane (`tools/vendor/kama-live/llama-b11909-bin-ubuntu-x64.tar.gz`, 22 475 032 B, sha256 bf94332a…; `stories260K.gguf`, 1 185 376 B, sha256 270cba1b…), record them in SOURCES, and give replay a fallback: try remote first; on fetch failure (URLError/HTTPError/timeout — **not** digest mismatch) fall back to the vendored copy and verify the same receipt digest; record `inputs.source=remote|vendor` and note remote drift when observed. A remote that responds with different bytes must still refuse (that is the tamper/urlswap signal), so the fallback never masks drift. Keeps D1 semantics (the counter hashes the rerun's files itself under scratch regardless of source).

## Files written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Design.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Design/K2Design-proposed.patch` (proposed diffs for F1-F4)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Design/receipt-1-r48.json`, `receipt-1-r47-v4.json` (cited receipts)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Design/{base,inst,stab,props-body,models-body,health-body}.json` (compare-demo variants)
