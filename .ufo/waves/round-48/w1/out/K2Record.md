# K2Record — round-48 attack on record-time verification (kama-llamacpp-live.py v5)

**Verdict:** record-time verification in `tools/kama-llamacpp-live.py` binds *local bytes to operator-supplied digests* only — it never fetches the recorded URLs — so all three forged-provenance forms record a v5 **pass** receipt (`provenance.verified.at="record"`), and `tools/kama-live-replay.py` **catches every one of them later** (refused, exit 2, no rerun); the byte-identical "copy from elsewhere" server is *not* false under the contract (it is the official round-48 recording pattern). No defect found in the frozen counter; the only item worth recording is a semantic one: `verified` at record time does not mean the URLs serve those bytes.

All runs used the scratch clone (git clone --shared of the lane at 380bcdff9c8af06997c482f6eb03db926a794a2b). No tools were installed (python3 stdlib only; a stub llama-server was written into scratch). Scratch: `/fast/scratch/hyaku/kama-r48/K2Record` (removed after this report; receipts copied to this directory). Lane read-only; the single live clone was under scratch.

## 0. Frozen context used

- Counter C2: `tools/round48-live-replay-v5-audit.py` → docstring lines 32-47 (v5 receipt contract; record-time contract = `sha256(--server-archive) == --server-asset-sha256` and member bytes == server sha256; no URL fetch at record); urlswap leg lines 90-97.
- Record tool: `tools/kama-llamacpp-live.py` — `verify_archive_member` lines 193-219; provenance gate lines 1456-1479 (`PINNED_MODEL_URL` line 71); v5 verification site lines 1556-1566 (before server launch).
- Replay tool: `tools/kama-live-replay.py` — `acquire()` lines 126-131 (digest refusal before extraction/execution), `provenance()` lines 96-123, member digest check lines 222-230.

## 1. Vector 1 — server binary is a copy of the member (same bytes) but from elsewhere

Claim tested: `--server /home/vgpnk/.local/opt/llama-b11909/llama-server` (the round-47 install copy), with the authentic b11909 asset (sha `bf94332a…`), member `llama-b11909/llama-server`, pinned model (sha `270cba1b…`). The installed copy hashes `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`; the archive member (extracted by `tar xzf asset.tar.gz -O llama-b11909/llama-server | sha256sum`) hashes the same.

```
python3 $LIVE --server /home/vgpnk/.local/opt/llama-b11909/llama-server \
  --model $S/model.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --alias kama-r48-v1 --ctx 256 --threads 1 \
  --server-asset-url <real github asset URL> --server-asset-sha256 bf94332a… \
  --server-member llama-b11909/llama-server --model-url <real pinned HF URL> \
  --server-archive $S/asset.tar.gz --out v1.json
```
- Record: **exit 0, outcome pass, schema v5**, `provenance.verified = {"at":"record","archive_sha256":"bf94332a…","member_sha256":"35ac50fb…","model_sha256":"270cba1b…"}` (v1.json). server.realpath = `/home/vgpnk/.local/opt/llama-b11909/llama-server` — a *different path* than any archive member.
- Replay (`kama-live-replay.py --receipt v1.json --work … --out p1.json`): **exit 0, match=true, mismatches=[]**, inputs archive_sha256=`bf94332a…`, model_sha256=`270cba1b…`, server=`…/work1/server/llama-b11909/llama-server`; live_exit 0 (rerun genuinely executed the extracted member). Full network re-acquisition happened.
- **Is it false? No.** The frozen contract defines the record-time check as byte equality (counter docstring lines 45-46: "the member's bytes in that archive hash to sha256(--server)"), and replay re-derives the same statement from committed bytes. The receipt never claims the *path* was extracted from the archive — it claims byte equality, which holds. The round-48 official install record uses exactly this pattern (`.ufo/waves/round-48/c2/live/install.txt`: server = round-47 install copy). No finding.

## 2. Vector 2 — pinned model URL names a commit that does not serve those bytes (record never fetches)

Record with a stub server, the real model locally (sha `270cba1b…`), and a model URL pinned to commit `22027b1ab988d9d04ec83020f28c2db533985059` — a real HF revision that serves sha `68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2` (verified by downloading it: `curl -sSL …/resolve/22027b1a…/tinyllamas/stories260K.gguf | sha256sum` → `68c694e7…`), i.e. not the recorded bytes. Asset URL also lied (stub-repack digest claimed; see §3).

- Record: **exit 0, outcome pass, schema v5**, `provenance.model.commit = "22027b1a…"`, `verified.at="record"` with model_sha256=`270cba1b…` (v2.json). Record time performed zero URL fetches — `PINNED_MODEL_URL.match()` (kama-llamacpp-live.py:1475) only checks the URL *shape*.
- Even a commit that cannot exist passes: same record with `…/resolve/0000000000000000000000000000000000000000/…` → **exit 0, outcome pass**, commit `0000…0000`, `verified.at="record"` (v2z.json).
- Replay: for v2 the asset acquire refuses first (see §3). The model-URL swap refusal is exercised by the counter's frozen urlswap leg (round48-live-replay-v5-audit.py:90-97 → `provenance-url-revision-differs-from-commit`, digest-mismatch), which passed the L1 pre-wave dry run (`urlswap=1`). Replay would also refuse v2z at model acquire (HTTP 404 → `could-not-run`) or, if the commit served other bytes, `digest-mismatch`.
- **Record passes; replay catches.**

## 3. Vector 3 — re-packed archive, same member, different digest, your sha passed as --server-asset-sha256 (asset URL lies)

Server = stub (`sha b548e3e9…`); archive = `stub_repack.tar.gz` containing the *same member bytes* (`bin/llama-server`) but archive digest `80057f2d…` (the authentic asset hashes `bf94332a…`); passed `--server-asset-sha256 80057f2d…` with the **real GitHub asset URL** — so the URL does not serve the claimed bytes.

- Record: **exit 0, outcome pass, schema v5**, `verified = {"at":"record","archive_sha256":"80057f2d…","member_sha256":"b548e3e9…",…}` (v4.json). `verify_archive_member` (kama-llamacpp-live.py:193-219) only checks `sha256_file(archive) == claimed` — self-consistent by construction — plus member==server bytes. Nothing ties the claimed digest to the URL.
- Replay: **exit 2, refused `digest-mismatch:llama-b11909-bin-ubuntu-x64.tar.gz:want=80057f2d…:got=bf94332a…`**, `rerun_receipt: null` (p_v4.json). Nothing was extracted or executed.
- **Record passes; replay catches.**

## 4. Vector 4 — member path with `./` prefix

- (a) Against an **authentic archive** with real digests, member `./llama-b11909/llama-server`: record **refuses** before starting anything — exit 2, `setup_error = "provenance-member-absent"`, child_pid null, no verified block (v5.json). `tarfile.getmember("./llama-b11909/llama-server")` misses the archive's stored name `llama-b11909/llama-server` (KeyError → kama-llamacpp-live.py:213-214). Defense works.
- (b) Against a **repack whose stored member name literally is** `./bin/llama-server` (`stub_repackdot.tar.gz`, member list `['./bin/llama-server']`) with the repack's digest claimed: record passes (exit 0, outcome pass, member `./bin/llama-server` — v6.json). Replay: **exit 2, refused `digest-mismatch`** at asset acquire (p_v6.json) — same class as §3.
- Note: replay itself would tolerate a `./`-prefixed member after extraction (`os.path.join(tree, "./bin/llama-server")` resolves inside the tree; member digest check at kama-live-replay.py:222-230 still binds bytes), so `./` is not a standalone bypass — it only matters as part of a repack+claimed-digest forgery (§3), which replay still refuses.
- **Record refuses (a), passes (b); replay catches (b).**

## 5. Summary table

| vector | record (v5 pass?) | replay later |
|---|---|---|
| 1 copy-from-elsewhere (byte-equal) | pass (exit 0) | **match** (exit 0) — not false |
| 2 model URL commit not serving bytes | pass (incl. zero-commit) | refused (digest-mismatch / 404) |
| 3 repack + self-claimed digest, asset URL lies | pass | refused (digest-mismatch at acquire) |
| 4a `./` member vs authentic archive | **refused** (member-absent) | n/a |
| 4b `./` member in repack + claimed digest | pass | refused (digest-mismatch at acquire) |

## 6. Findings

- **F1 (semantic, not a counter defect):** `provenance.verified.at="record"` (kama-llamacpp-live.py:1564-1566) verifies only local bindings — `sha256(local archive) == claimed asset digest`, member bytes == server bytes, model bytes == claimed model digest — never that the recorded URLs serve those bytes. `verify_archive_member` (lines 193-219) and the model-URL gate (lines 1474-1479) perform no fetch. This is exactly what the frozen counter's contract codifies (counter docstring lines 41-47), so the counter is correct; but the word "verified" overpromises to a reader. **Proposed fix (doc-only, no behavior change):** in `kama-llamacpp-live.py` docstring lines 30-43 and `kama-live-replay.py` docstring lines 27-29, state that record-time verification binds local bytes to the *operator-supplied* digests and that URL↔bytes binding is enforced by replay (`acquire`), e.g. rename the field semantics to `verified {at:"record", local-only}` or add `"url_fetched": false`. Do not add a network fetch at record time (record would lose offline capability and the counter's recordcheck stub would need network).
- **F2 (observation):** the member guard (kama-llamacpp-live.py:1472) allows `./`-prefixed members; it is harmless alone (tarfile exact-match refuses against truthful archives, §4a) and replay normalizes the path, so no bypass exists.
- **F3 (clarification):** the "copy from elsewhere" server is byte-identical to the member and is *not* false provenance under this contract; the official round-48 receipts themselves use a round-47 install copy (install.txt). If the team ever wants origin-of-bytes provenance (that the *running binary was extracted from the recorded archive*), that would require record to extract and exec from the archive (or record the install tree digest), which is a new contract, not a fix to the current one.

## 7. Deliverables in this directory

- Receipts: `v1.json` (real, vector 1), `v2.json` (vector 2, swap commit), `v2z.json` (vector 2, zero commit), `v4.json` (vector 3), `v6.json` (vector 4b), `v5.json` (vector 4a refusal).
- Replay results: `p1.json` (match), `p_v2.json`, `p_v4.json`, `p_v6.json` (refused).
- Report: `K2Record.md` (this file).
