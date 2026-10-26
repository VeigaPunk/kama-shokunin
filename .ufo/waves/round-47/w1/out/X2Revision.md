# X2Revision — pinning `stories260K.gguf` to an HF commit instead of `main`

**Verdict: the pin exists and works — `https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` serves exactly `sha256 270cba1b…` (302 `x-repo-commit: 499bc8…`, `x-linked-etag` = the frozen digest, same Xet CAS object as `resolve/main`, `cmp`-identical bytes), and the lane's existing replay tool reproduces the lifecycle from it 3/3 times (match=True, exit 0, 11/11 checks); `main` is demonstrably a moving ref — the same path served three different byte strings — so the three v4 receipts that record `resolve/main` (receipt-1/2/3.json:394) name a revision that can change under them, which the digest guard converts into a refusal (measured: exit 2), not silent drift.**

## 1. Answer: which commit serves the frozen blob

`git ls-remote https://huggingface.co/ggml-org/models-moved`:
```
499bc8821c6b12b4e53c5bffcb21ec206f212d81	HEAD
499bc8821c6b12b4e53c5bffcb21ec206f212d81	refs/heads/main
```
`/api/models/ggml-org/models-moved` → `sha 499bc88…`, `lastModified 2025-10-28T10:43:38Z`, 29 siblings.
Tree at the tip (`/api/models/ggml-org/models-moved/tree/499bc8…/tinyllamas`):
```
file 941cd12cc9e7e7b83944e83ab5887cbed28d2f0f 1185376 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d tinyllamas/stories260K.gguf
```
i.e. git blob `941cd12c…`, size `1185376`, LFS sha256 = the frozen digest.

Lineage (blobless shallow clone, parents from `git log --format='%H %P'`; evidence `X2Revision/hf-commit-chain.tsv`):
```
499bc8…  parent e2d5caf5…  2025-10-28T10:43:38Z stories15M : revert training context to 128   <- main
e2d5caf5… parent 96f460f9… 2025-10-28T09:18:28Z stories15M : bump training context to 256
96f460f9… parent 22027b1a… 2025-10-28T08:55:08Z gguf : bump training context from 256 to 2048
22027b1a… parent 688f41dd… 2025-10-28T08:07:12Z gguf : bump training context from 128 to 256
```
`git log --raw -- tinyllamas/stories260K.gguf` (`X2Revision/git-raw-stories260K.txt`):
```
96f460f9… M tinyllamas/stories260K.gguf   a8ef65a -> 941cd12   # target blob written here
22027b1ab… M tinyllamas/stories260K.gguf  3e863ed -> a8ef65a   # previous bytes
```
So **`96f460f9c1e2ca43d0adc1c682b832525a2c0ea3` is the commit that wrote the frozen bytes**, and every descendant on `main` (e2d5caf5, 499bc8) still carries them. All three serve `270cba1b…` (downloaded and hashed, `X2Revision/downloads-sha256.txt`); the two ancestors serve other bytes.

## 2. `main` is a moving ref on exactly this path (the reason to pin)

| revision fetched | x-linked-etag (sha256) | x-repo-commit |
|---|---|---|
| `main` / `499bc8…` | `270cba1b…` | `499bc8…` |
| `96f460f9…` | `270cba1b…` | `96f460f9…` |
| `22027b1a…` | `68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2` | `22027b1a…` |
| `688f41dd…` | `047bf46455a544931cff6fef14d7910154c56afbc23ab1c5e56a72e69912c04b` | `688f41dd…` |

Downloads confirm the headers: `sha256sum` gives `270cba1b…` for `resolve/main`, `270cba1b…` for `resolve/499bc8…`, `68c694e7…` for `22027b1a`, `047bf464…` for `688f41dd`; `cmp m-main.gguf m-pin.gguf` → exit 0 (`CMP_IDENTICAL`). Three byte strings on one path from 2025-09-26 to 2025-10-28, two of the moves inside 48 minutes on 2025-10-28 — this corroborates corpus/SOURCES.md:51 ("the same path held three different byte strings on 2025-10-28, so the digest, not the path, identifies it").

## 3. The pinned URL serves the same bytes

Command:
```
curl -sSI https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
```
→ `HTTP/2 302`, `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`, `x-linked-size: 1185376`. Raw headers: `X2Revision/headers-499bc8….txt` (and `-main.txt`, `-96f460f9….txt`, `-22027b1a….txt`, `-688f41dd….txt`).

Independent of the headers, the bytes are the same object: `resolve/main`, `resolve/499bc8…` and `resolve/96f460f9…` all 302 to the same Xet CAS path
`…/xet-bridge-us/6580840062b6ed53c4c72d61/7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5`,
while `22027b1a` and `688f41dd` redirect to `f7cf5caa…` and `aacaa2d3…` respectively. The digest check is the load-bearing one; the shared CAS path shows why it passes.

`resolve/499bc8821c6b` (12-hex prefix) also resolves and still reports the full `x-repo-commit`, but a receipt should record the full 40-hex form — prefixes are only a fetch convenience.

## 4. End-to-end operability: the lane's replay tool accepts the pinned URL unchanged

Each of the three C2 receipts was copied with only `provenance.model.url` rewritten to the pinned URL, then replayed with the lane tool (the v4 schema is unchanged; `tools/kama-live-replay.py` records `provenance.model.url` verbatim, `fetch()` requires `https://`, and `acquire()` hashes before use — tools/kama-live-replay.py:60-66, 91-96):

```
python3 tools/kama-live-replay.py --receipt $S/receipt-1-pinned.json --work $S/replay-work --out $S/replay-pinned-1.json
replay match=True refused=None mismatches=0 exit=0      # receipt-1, exit=0
replay match=True refused=None mismatches=0 exit=0      # receipt-2, exit=0
replay match=True refused=None mismatches=0 exit=0      # receipt-3, exit=0
```
Rerun receipts (`X2Revision/rerun-receipt-{1,2,3}.json`): `outcome=pass`, 11/11 checks `passed=true evaluated=true`, ports 33681 / 38091 / 45913, server archive re-verified `bf94332a…`, model `270cba1b…` before and after (`model_sha256_post`), teardown `returncode=0`, `sigterm_sent=true`, `log_path=null`. The rerun receipts record the pinned URL in their own `provenance.model.url` — a second-generation receipt stays pinned.

Negative control (proves the pin is discriminating, and that the guard is the digest, not the URL): the same receipt with the URL pointed at `22027b1a` —
```
replay match=False refused=digest-mismatch:stories260K.gguf:want=270cba1b…:got=68c694e7… mismatches=0 exit=2
```
exit 2, refused before extraction (`X2Revision/replay-shifted.json`).

## 5. Finding (not a frozen-counter defect): v4 records a moving ref

- **Where:** `.ufo/waves/round-47/c2/live/receipt-1.json:394`, `receipt-2.json:394`, `receipt-3.json:394` — `"url": "https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf"`.
- **Tool:** `tools/kama-llamacpp-live.py:1385` writes `provenance.model.url` verbatim; `--model-url` help text (line 1130-1131) only says "URL the --model file was fetched from". No immutability requirement anywhere.
- **Frozen counter:** `tools/round47-live-replay-audit.py` accepts it — the predicate requires only `provenance.model.url` to start with `https://` (lines 46-47 docstring, line 159-160 code), so a branch ref passes. This is not a round-47 counter defect (the v4 contract + digest do answer the round-47 question, "can a fresh session re-run from committed bytes"); it is the reason a round-48 v5 should name the revision.
- **Consequence today:** if `main` moves, a replay of a committed v4 receipt exits 2 (`digest-mismatch`) instead of reproducing — safety preserved, reproducibility lost. The gap is that the receipt does not say which revision it meant, so no repair is possible without re-mining the digest.
- **Proposed fix (advisory, not applied; frozen files untouched):** `X2Revision/proposed-v5.md` — derive `provenance.model.commit` (40 hex) from the `/resolve/<commit>/` segment of `--model-url`, refuse an unpinned https model URL at setup (exit 2), and in `tools/kama-live-replay.py:68-83` require the URL revision to equal the recorded commit. No new flag, no new network call; the live tool can validate offline.
- **Zero-change interim option:** a v4 receipt whose `provenance.model.url` is already pinned replays byte-identically today (proved 3/3), so the lane can stop depending on `main` by passing the pinned URL — the v5 field is what makes it machine-checkable.

## 6. Drafts

**Pinned URL** (`X2Revision/pinned-url.txt`):
```
https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
```
v5 provenance: `{"url": <that>, "sha256": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d", "commit": "499bc8821c6b12b4e53c5bffcb21ec206f212d81"}`.
`499bc8` is what `main` resolved to (`x-repo-commit`) at receipt time, so the pinned URL stays a true statement of what those receipts downloaded; `96f460f9` (the blob-writing commit) is the tighter anchor and serves the same bytes if the lane prefers a revision-independent pin.

**One-line SOURCES anchor** (`X2Revision/SOURCES-anchor.md`, one line):
> `resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` answers 302 with `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` and `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"` (`x-linked-size: 1185376`), and the downloaded bytes are sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` and `cmp`-identical to `resolve/main` and to `resolve/96f460f9c1e2ca43d0adc1c682b832525a2c0ea3` on 2026-10-26; the blob (git `941cd12cc9e7e7b83944e83ab5887cbed28d2f0f`) was written by `96f460f9`, whose parent `22027b1a` served `68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2`, and `688f41dd` before it served `047bf46455a544931cff6fef14d7910154c56afbc23ab1c5e56a72e69912c04b` — the same path moved through three byte strings, 2025-09-26 to 2025-10-28.

S039 (`corpus/SOURCES.md:51`) already records repo commit `499bc8…`, file commit `96f460f9…`, size and digest, so the row above adds only the URL form; appending `; deliverable URL: <pinned>` to S039's anchor cell is the one-row alternative (given in `SOURCES-anchor.md`).

## 7. Risks / residuals

- A commit pin is retrievability, not integrity: HF could rewrite history, delete the repo, or drop an object. The sha256 stays the integrity check and keeps refusing wrong bytes (measured exit 2); recording both (URL + commit + sha256) is what makes the receipt both repairable and safe.
- `resolve/<commit>` redirects to signed CDN URLs (`Expires` ~1 day) — this matters only per request; both `curl -L` and the replay tool's `urllib` follow them (proved by the 3/3 replays).
- The measured replays used the seat's scratch as `--work`, on ports 33681/38091/45913; this seat wrote nothing into the lane (receipts were copied out and edited in scratch, `--out`/`--work` in scratch) and touched no registry row or service. Concurrent sibling edits did appear in the lane working tree during this seat: `M tools/kama-live-replay.py`, `M tools/append-only-audit.py`, `M tools/gguf-identity.py`, `M tests/llamacpp-live/check-receipt.py`, untracked `.ufo/waves/round-47/c2/x0-digest-rehash.txt`. My replays ran at 18:31 against the then-clean working tree (HEAD `46a924e…`, a child of the build commit) and are unaffected; the line citations in §4/§5 are keyed to the committed text, where `fetch`/`provenance`/`acquire` sit at the same lines in both `3a09a1d…` and `46a924e…`.
- Lane HEAD observed `46a924e027f05614558c45ff02bf7a94ca57d3e1` (not the build commit `3a09a1d…`); this item's evidence is revision-pinned by URL/digest, so it is independent of that.

## 8. Evidence files (all under `X2Revision/`)

`pinned-url.txt`, `SOURCES-anchor.md`, `proposed-v5.md`, `commands.sh` (re-runnable),
`model-api.json`, `tree-main.json`, `commits-main.json`, `hf-commit-chain.tsv`,
`git-raw-stories260K.txt`, `headers-{main,499bc8…,96f460f9…,22027b1a…,688f41dd…}.txt`,
`downloads-sha256.txt`, `receipt-{1,2,3}-pinned.json`, `replay-pinned-{1,2,3}.json`,
`rerun-receipt-{1,2,3}.json`, `replay-shifted.json`, `replay-summary.txt`, `manifest.sha256`.

Reproduction: `bash X2Revision/commands.sh` (scratch root `$S=/fast/scratch/hyaku/kama-r47/X2Revision`, recreated by the script).

Tooling: no installs, no pacman (host-wide pause respected); only `curl`, `git`, `sha256sum`, `cmp` and the lane's own Python tools were used.
