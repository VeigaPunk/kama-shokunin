# Round-47 registry rows (S1Rows) — S488, S489, S490

Three rows, 11 cells each, `SOURCES-CONTRACT-v1`. Ids continue from the lane's
last row S487 (registry holds 228 rows at 3a09a1d9 and at HEAD 46a924e0); no
`S4(88|89|9x)` id exists in the lane, so the L1 may renumber on integration
without collision. Insertion point: inside `## Registry`, immediately after the
S487 line (`corpus/SOURCES.md:240` at 3a09a1d9), before the blank line at 241
and `## Paths` at 242. Cells hold no `|`, so the row keeps NF=13.

Each row carries: a located quote (release JSON fields / HTTP headers / receipt
fields), `opened 2026-10-26`, `status mined`, a recheck cadence, and `—` as the
used-by placeholder (the knowledge entry and lesson this round cites the rows
from do not exist yet; `—` costs only census warning W03, never an error).

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S488 | llama.cpp release b11909 Linux x64 CPU binary — https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz (asset record: https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11909) | docs | A | identity of the official b11909 Linux x64 CPU binary kama ran in round 47 and the commit its tag names; not runtime behaviour, not performance, not another asset flavour of the same release, not any later release | tag b11909 = caa8191df159f764fb0160e3d2fc6be008948aee (`git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11909`, 2026-10-26, exit 0); release JSON quote — `"tag_name":"b11909"`, `"target_commitish":"caa8191df159f764fb0160e3d2fc6be008948aee"`, `"published_at":"2026-10-26T21:00:58Z"`, `"prerelease":true`, `"immutable":false` — from `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` 2026-10-26, 68614 bytes, SHA-256 e41c4b75188b7b710843fc450c5ad84463a035670d481e982cebf78729c3b63c (copy `.ufo/waves/round-47/w1/out/S1Rows/release-b11909.gh.json`); asset `llama-b11909-bin-ubuntu-x64.tar.gz` size 22475032, digest sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b; downloaded 2026-10-26 and sha256sum equal to that digest and to `.ufo/waves/round-47/c2/live/install.txt`; 62 archive members, member `llama-b11909/llama-server` sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0, `--version` line `0.7.0-dev (build 11909, commit caa8191df)`; the committed copy `.ufo/waves/round-47/c2/release-b11909.json` sha256 6ad897dd84e64dcf6aff9997dc19d2e835b7a90adc37da12bb0e00b310db46d2 differs from the fresh fetch only in each asset's `download_count` (31 of 31 diffs) | Ties the round-47 live receipts to one GitHub-computed asset digest and one server binary hash; b11909 is a mutable Pre-release (`"immutable":false`), so cite the digest, not the tag alone, and expect the record's per-asset download counters to move while every identity field holds. | mined | 2026-10-26 | on-release | — |
| S489 | kama live llama.cpp lifecycle receipts at b11909 — `python3 tools/kama-llamacpp-live.py --server-asset-url ... --server-asset-sha256 ... --server-member ... --model-url ...` (raw receipts `.ufo/waves/round-47/c2/live/receipt-1.json`, `-2.json`, `-3.json`; install record `.ufo/waves/round-47/c2/live/install.txt`) | own-work | A | three lane-owned b11909 runs on unregistered loopback ports at sampled instants, schema v4 with a provenance block and a replay tool that re-acquires both inputs; not registered-consumer health, model quality, other builds or general timing | receipts kama-llamacpp-live/v4 2026-10-26T21:16:50.545Z–21:16:50.722Z, 21:16:50.774Z–21:16:50.943Z and 21:16:51.030Z–21:16:51.224Z, ports 37903, 44883, 39739, alias kama-r47-live, ctx 256, threads 1; `captures.props.fields.build_info` `b11909-caa8191df`; provenance.server `asset_url` the b11909 x64 asset (S488), `asset_sha256` bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b, `member` `llama-b11909/llama-server`; provenance.model url the stories260K resolve URL (S490) with sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d; live tool sha256 65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d, probe sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3; 11 checks each, all evaluated and passed; loading 503 body exactly `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (body sha256 baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c), one body per run with 0 dropped; teardown returncode 0, sigterm_sent true, sigkill_sent false, term_wait_ms 3, port_refuses true, `log_path` null; receipt file sha256 a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d, d36d29417ce5cf7e2f9d1424a281e54b6ec44575f2b67be1acb3d8dec349eb49, f3f961517711a18ccfce7db837d116e06b7a01ab046f404c95e83c64b2542b68; replay from committed bytes (`tools/kama-live-replay.py` sha256 39cd387a3a95b47865d81484ffe30664e653d5016c4c75d47abf6e855e43fdd0) re-acquired both inputs under an empty home, reproduced all 11 checked ids, and refused both single-hex-digit tampered digests — `tools/round47-live-replay-audit.py` at 3a09a1d9: `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`, exit 1, whose sole miss was the absent registry row (this S488) | On b11909 the S041, S046, S055 and S487 lifecycle statements hold: the exact loading 503 envelope, ready `/health` `{"status":"ok"}`, `/v1/models` id = alias `kama-r47-live` with `owned_by` `llamacpp`, `/metrics` 501, probe MODEL_OK and MODEL_MISMATCH, 11/11 checks, SIGTERM returncode 0 with no SIGKILL; each receipt now records the two URLs and digests, so a fresh session can re-run the evidence, and `teardown.log_path` is null because the temp log is always deleted. | mined | 2026-10-26 | on-release | — |
| S490 | Hugging Face ggml-org/models-moved — tinyllamas/stories260K.gguf at its resolve URL — https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf | dataset | A | identity of the model artifact a v4 receipt's provenance re-acquires from this resolve URL: byte size, LFS sha256 and what one fetch returns; artifact identity only, not model quality or behaviour, not the repo commit or `/blob/` path S039 records | quote — `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"` and `x-linked-size: 1185376` — from `curl -sSIL` 2026-10-26: 302 to a `us.aws.cdn.hf.co` xet-bridge URL, then 200 `content-length: 1185376`, `etag: "7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5"` (copy `.ufo/waves/round-47/w1/out/S1Rows/model-head.txt`); downloaded the same day, 1185376 bytes, sha256sum 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d, equal to the provenance `model.sha256` in `.ufo/waves/round-47/c2/live/receipt-1..3.json`; same digest S039 records for the `/blob/` path at repo commit 499bc882 | The resolve URL that the receipts' provenance records serves exactly the pinned 1185376 bytes and declares their sha256 as `x-linked-etag`, so a replay's digest check tests the artifact rather than the path; the fetch is served by a CDN redirect, which is why the digest, never the URL alone, names the model. | mined | 2026-10-26 | every round | — |

## Relationship to existing rows (for the L1)

- S488 and S486 are the same kind of row one release apart (b11909 vs b11906):
  different asset URL, different commit, different digest, different server
  binary hash. No cell of S486 is contradicted.
- S489 does not supersede S487: it is the next build's receipt set, and its new
  cell content is the `kama-llamacpp-live/v4` provenance block plus the replay
  observation. S487's b11906 statements stay as written.
- S490 overlaps S039 in subject but not in URL (`/resolve/` vs `/blob/`) or in
  scope (what a provenance-driven re-acquisition returns vs the file at one repo
  commit). It carries the same LFS sha256, so the two rows agree; it does not
  supersede S039, whose commit anchor is what a repo-history claim needs. The
  census E04 test is URL+scope, so this pair raises no E04; W04 (same URL across
  scopes) is also not raised, the URLs being different paths.

## Proposed search-log supplement (optional, at the L1's discretion)

> **2026-10-26 — round-47 b11909 live provenance rows.** Question: what exactly
> did kama run at llama.cpp b11909, and can the evidence be re-acquired?
> Where: the b11909 release record (`gh api .../releases/tags/b11909`), the
> `llama-b11909-bin-ubuntu-x64.tar.gz` asset, the three `kama-llamacpp-live/v4`
> receipts with their provenance block, and the stories260K resolve URL the
> receipts name. Identified 3, screened 3, included 3 (S488–S490), excluded 0.
> Quote: `"target_commitish":"caa8191df159f764fb0160e3d2fc6be008948aee"`.
> Stop: each row's identity cell measured on 2026-10-26 and each quote located
> in the bytes cited; no runtime statement beyond the receipts' own checks.

## Gate

Run on a scratch copy only (`<scratch>/lane/corpus/SOURCES.proposed.md`, a
`git clone --shared` of the lane at 46a924e0 with the three rows inserted after
S487; the lane itself was never written to).

1. `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate
   --file <copy> --today 2026-10-26` → exit **0**, last line `file ok`, no
   `E`-code. The output is identical to the same command on the unmodified copy
   except the three expected `W03 S488/S489/S490 mined but unused` lines.
   Transcript: `census-validate.txt`.
2. `sources-census.sh census --file <copy>` → `rows 231` (baseline 228),
   `tier.A 220` (217), `tier.B 7` (7), `tier.C 4` (4), `status.mined 212`
   (209), `invalid 0`, `missing 0`. The three rows are the only delta.
3. Field width: `awk -F'|' '{print NF}'` on each new line → **13** for all
   three (11 cells, no stray `|`, no empty cell).
4. `git diff --numstat 46a924e0 <copy commit>` → `3 0 corpus/SOURCES.md`:
   additions only, no existing row touched.
5. `tools/round47-live-replay-audit.py --repo <clone> --tip <copy commit>` →
   `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`, exit **0**
   (the same counter on 3a09a1d9 without the rows → `newrow=0 met=False`, exit
   1). Transcripts: `c2-counter.out` (before) and `c2-counter-with-rows.out`
   (after).
6. `tools/sources-append-only.py --from <base> --to <copy commit>` → exit **2**,
   `corpus/SOURCES.md:516: row-like line outside the parsed registry table`, a
   pre-existing condition of the lane file (see the round-47 S1Rows report).
   With those 27 pre-existing prose lines neutralised in the scratch copy only,
   the same guard reports `added S488 (allowed)`, `added S489 (allowed)`,
   `added S490 (allowed)`, `no append-only violations`, exit **0** —
   `append-only-neutralised.txt`.

Measurements the cells cite: `downloads.txt` (release record diff, asset and
model hashes, extracted server hash and `--version`), `model-head.txt` (the
`curl -sSIL` headers), `release-b11909.gh.json` (fresh API copy),
`ls-remote-tags.txt`, `c2-counter.out`.
