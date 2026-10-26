# X2Replica - independent replay of C2 receipts 2 and 3 (round 47, lane kama)

**Verdict:** operability CONFIRMED — receipts 2 and 3 re-run from their recorded provenance alone in a fresh empty home, exit 0, `match=true`, 0 mismatches, all 11 evaluated checks re-evaluated with the same value; the round-46 v3 receipt is refused (exit 2, `not-a-v4-receipt:kama-llamacpp-live/v3`) before any network use. One weakness found in the frozen replay tool: `compare()` does not compare the harness (`tool.sha256`) or probe (`probe.sha256`) digests, so a swapped harness/probe could still report `match`.

Lane tip used (read-only): `46a924e027f05614558c45ff02bf7a94ca57d3e1` ("round-47: wave spec kama-r47-w1 (65 seats, policy v2) and dispatch"). `git diff --stat 3a09a1d93dcc16799cf6c4b48786e6440af134c4 HEAD -- tools/` is **empty**, and `git hash-object tools/kama-live-replay.py` = `3773e62da07a9eaf9329be93c3c5c1f65415cc21` = the blob at 3a09a1d, so the tool bytes I exercised are the frozen build's bytes (working tree clean for the paths below: `git status --porcelain` prints nothing).

## 1. Commands (exact, one live clone = none needed; tools invoked read-only from the lane)

Scratch `S=/fast/scratch/hyaku/kama-r47/X2Replica`, `TMPDIR=$S`; per-run empty homes `$S/home-N`, `$S/xdg-N`.

```
HOME=$S/home-2 XDG_CACHE_HOME=$S/xdg-2 TMPDIR=$S timeout 900 \
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
    --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/c2/live/receipt-2.json \
    --work $S/w2 --out .ufo/waves/round-47/w1/out/X2Replica/replay-2.json
```
stdout: `replay match=True refused=None mismatches=0 exit=0` — **exit 0**, wall ~2.3 s (22.4 MB + 1.18 MB downloads included).

```
HOME=$S/home-3 XDG_CACHE_HOME=$S/xdg-3 TMPDIR=$S timeout 900 \
  python3 .../tools/kama-live-replay.py \
    --receipt .../.ufo/waves/round-47/c2/live/receipt-3.json \
    --work $S/w3 --out .../w1/out/X2Replica/replay-3.json
```
stdout: `replay match=True refused=None mismatches=0 exit=0` — **exit 0**.

```
HOME=$S/home-46 XDG_CACHE_HOME=$S/xdg-46 TMPDIR=$S timeout 120 \
  python3 .../tools/kama-live-replay.py \
    --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/c1/live/receipt-1.json \
    --work $S/w46 --out .../w1/out/X2Replica/replay-r46-v3.json
```
stdout: `replay match=False refused=not-a-v4-receipt:kama-llamacpp-live/v3 mismatches=0 exit=2` — **exit 2**.

## 2. Result surface (from replay-2.json / replay-3.json and the copied rerun receipts)

| | receipt-2 | receipt-3 |
|---|---|---|
| replay exit / match / mismatches | 0 / true / `[]` | 0 / true / `[]` |
| rerun receipt `schema` / `outcome` | kama-llamacpp-live/v4 / pass | kama-llamacpp-live/v4 / pass |
| `live_exit` | 0 | 0 |
| evaluated checks equal (11/11) | yes | yes |
| rerun window (UTC) | 21:25:40.829Z–21:25:41.003Z | 21:25:52.743Z–21:25:52.914Z |
| port (orig -> rerun) | 44883 -> 35801 | 39739 -> 42725 |
| `inputs.*` all under `$S` | yes | yes |

Checks re-evaluated, all `passed=true`, identical to the originals: `health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`, `model_unchanged` (11 evaluated in both reruns — matches the L1 dry run's `rerun_checks=11`).

### Digests

| artifact | sha256 | source |
|---|---|---|
| release archive `llama-b11909-bin-ubuntu-x64.tar.gz` (22,475,032 B) | `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` | re-downloaded at 21:25:39Z / 21:25:51Z, re-hashed, equals frozen asset digest and `install.txt` |
| model `stories260K.gguf` (1,185,376 B) | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | re-downloaded, re-hashed, equals `provenance.model.sha256` and receipt `model.sha256` |
| server binary `llama-b11909/llama-server` (extracted in scratch) | `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | `rerun-N.json` `server.sha256`, equals `install.txt` line 6 and both originals |

`rerun-N.json` `model_sha256_post` = `270cba1b…` (unchanged after the lifecycle).

### Inputs lie under scratch (proved, not asserted)

`realpath -e` of archive, model and server for both runs:
- `/fast/scratch/hyaku/kama-r47/X2Replica/w2/download/llama-b11909-bin-ubuntu-x64.tar.gz`
- `/fast/scratch/hyaku/kama-r47/X2Replica/w2/download/stories260K.gguf`
- `/fast/scratch/hyaku/kama-r47/X2Replica/w2/server/llama-b11909/llama-server`
- same three under `w3/`

`replay-N.json` records exactly these paths in `inputs.{archive,model,server}`. The original receipts' `model.path` is `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` and `server.realpath` is `/home/vgpnk/.local/opt/llama-b11909/llama-server` — the reruns never touch either host path (the model was re-fetched, see §1). Host-independence of the lifecycle: `$S/home-N` and `$S/xdg-N` are **still empty** after both runs (`ls -A` prints nothing); child env whitelist recorded by the live tool is `['HOME','LANG','PATH','TMPDIR']` (so `XDG_CACHE_HOME` reached the replay parent only; the independence evidence is the re-download, not an absent cache).

### Behaviour observed in the reruns (server side)

`teardown.log_lines`: rerun-2 `… load_model: loading model '/fast/…/w2/download/stories260K.gguf'` / `… listening on http://127.0.0.1:35801`; rerun-3 the same on `127.0.0.1:42725` — loopback only, tool-picked port. `teardown`: `sigterm_sent=true`, `sigkill_sent=false`, `returncode=0`, `term_wait_ms=3`, `port_refuses=true`, `log_path=null` (the v4 contract line). `loading_observed=true`, `loading_envelope_exact=true`, 503 body sha `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c` identical to both originals. After both runs: no `llama-server` process (`pgrep -af llama-server` empty) and no listener on 35801/42725 (`ss -ltnp`).

## 3. Beyond `compare()` — I checked the fields the tool does not compare

Equal between original and rerun (so the 0-mismatch verdict is not hiding drift):

- `server.install_tree_sha256` `9f1198f4e2d64495ea6e6c6dece9f95a34ab2e4e2a11f72fd7debd1024d5542e` (51 members) — equal in all three receipts and both reruns;
- `server.install_links_sha256` `5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060` (10 links); `install_unpinned=[]`;
- `tool.sha256` `65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d`, equal to `sha256sum tools/kama-llamacpp-live.py` at the lane tip (harness that produced the receipts = harness I replayed);
- `probe.sha256` `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` (`tools/kama-probe.sh`);
- `source_binding`, `child_env_keys`, `port_listener_ownership` (`child`), probe count (2) and transition count (4), `loading_503.body_sha256`.

Expected, benign differences (all path/clock dependent, none semantic):

- `port`, `child_pid`, `started_utc`/`ended_utc`, `argv` (absolute `--server`/`--model`), `server.arg`/`server.realpath`, `model.arg`/`model.path`;
- `captures.models` body: only `data[0].created` (server start epoch 1793049410 -> 1793049940), hence its body sha differs;
- `captures.props` body: `Content-Length` 2067 -> 2078 (+11 bytes) in **both** reruns, and the model path grew 56 -> 67 chars (+11); `/props` echoes the model path, so the whole delta is the echoed path, not a settings drift. (`fields` — `build_info`, `default_generation_settings.n_ctx`, `is_sleeping`, `model_alias`, `total_slots` — are identical.)
- `loading_503.t_ms`, transition `t_ms`.

## 4. Finding (frozen tool — reporting, not fixing in place)

`tools/kama-live-replay.py:108-124` `compare()` compares only `schema`, `outcome`, `server.sha256`, `model.sha256` and the evaluated-check map. It does **not** compare the receipt's `tool.sha256`, `probe.sha256`, `server.install_links_sha256`/`install_tree_sha256`, or the capture bodies. Consequence: replay can print `match=True` for a rerun produced by a different `kama-llamacpp-live.py` (or a different `kama-probe.sh`) as long as the 11 check ids happen to pass; and `--probe` is never forwarded from the receipt (`replay()`, `kama-live-replay.py:152-155`: `argv` passes alias/ctx/threads and provenance but not `--probe`), so the probe a rerun uses is whatever the live tool's built-in default names at its own tree (`kama-llamacpp-live.py:58` `DEFAULT_PROBE = LANE / 'tools' / 'kama-probe.sh'`). For this wave it is harmless — I verified all four digests are equal — but it weakens the "re-runnable evidence" claim that C2 exists to make.

Demonstrated (not argued): a copy of `rerun-2.json` with `tool.sha256`, `probe.sha256` and `server.install_links_sha256` replaced by `'0'*64`/`'1'*64`/`'2'*64` gives `compare() -> []` (frozen tool: a swapped harness reads as `match=True`), while the patched `compare()` returns three mismatches naming `server.install_links_sha256`, `tool.sha256`, `probe.sha256`.

Proposed fix (unified diff saved as `proposed-compare.patch` beside this report; validated in scratch: `patch --dry-run -p1` OK, applied copy `py_compile` OK, patched `compare()` still returns `[]` for rerun-2 and rerun-3, so this wave's `match=True` is preserved because all four digests already agree):

```
--- a/tools/kama-live-replay.py
+++ b/tools/kama-live-replay.py
@@ -115,6 +115,14 @@
         a, b = (orig.get(side) or {}).get("sha256"), (rerun.get(side) or {}).get("sha256")
         if a != b:
             out.append(f"{side}.sha256:{a}->{b}")
+    for k in ("install_links_sha256", "install_tree_sha256"):
+        a, b = (orig.get("server") or {}).get(k), (rerun.get("server") or {}).get(k)
+        if a != b:
+            out.append(f"server.{k}:{a}->{b}")
+    for side in ("tool", "probe"):
+        a, b = (orig.get(side) or {}).get("sha256"), (rerun.get(side) or {}).get("sha256")
+        if a != b:
+            out.append(f"{side}.sha256:{a}->{b}")
     eo, er = evaluated(orig), evaluated(rerun)
     for cid, passed in sorted(eo.items(), key=lambda kv: str(kv[0])):
         if cid not in er:
```
and in `replay()`, forward the receipt's probe path when the rerun receipt records one (`--probe str(rec.get("probe",{}).get("path"))`) so `probe.sha256` comparison is meaningful on trees where the probe moved.

Severity: low for this wave (digests agree), medium for the contract — a future receipt produced by a modified harness would replay "green".

## 5. Round-46 v3 receipt: refused as expected

`replay-r46-v3.json`: `match=false`, `refused="not-a-v4-receipt:kama-llamacpp-live/v3"`, `mismatches=[]`, `inputs={}`, `rerun_receipt=null`, exit **2**.

Reason chain: the receipt's `schema` is `kama-llamacpp-live/v3` and its `provenance` is `null` (round 46 recorded only host paths: `server.arg=/home/vgpnk/.local/opt/llama-b11906/llama-server`, model under `~/.cache`); `provenance()` (`kama-live-replay.py:68-71`) raises `not-a-v4-receipt:<schema>` before any URL is read. Refusal is side-effect free: `--work $S/w46` was **never created** (`ls -d $S/w46` -> No such file or directory) and no download occurred, consistent with the docstring's "refused ... or could not run" and with the tool's own `http-refused`/`missing-url` self-test shape. The registered digest-vs-receipt-model gate (`provenance-model-digest-differs-from-receipt-model`) is not reached here, which is correct for a v3 receipt.

## 6. Scope, limits, hygiene

- Not run by me: receipt 1 (the C2 counter's `replay` leg replays receipt-1 and checks the rerun itself), the `tamper` leg, and the counter as a whole — out of this seat's item.
- My runs invoked the lane tools in place (read-only) rather than from `git archive <tip>`; the blobs prove the bytes are 3a09a1d's (`3773e62d…`, `203854f8…`) and the receipts are the committed blobs (`3f7ef92a…`, `1e60660c…`).
- Lane writes: none. `git status --porcelain` for `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, `.ufo/waves/round-47/c2/live` is empty (only untracked `w1/out/` and sibling wave files appear elsewhere); the receipts and `install.txt` mtimes are still 18:16 local, i.e. the build's own write time — my runs (21:25Z) did not touch them. Receipt digests unchanged: `a4caf311…`, `d36d2941…`, `f3f96151…`.
- No tool installs or upgrades were needed (`python3`, stdlib only, plus the lane tools); no pacman, no `~/.local/bin` writes. No services started outside the lane live tool's own loopback server; both torn down (see §2). At 21:29Z `pgrep -af llama-server` shows four processes belonging to the sibling seat `L2Concurrent`'s stress run under `/fast/scratch/hyaku/kama-r47/L2Concurrent/` — not mine (my scratch is already removed, `pgrep -af kama-r47/X2Replica` is empty, and `ss -ltnp` shows no listener on my rerun ports 35801/42725). A reviewer grepping for leftovers should attribute those to L2Concurrent.
- Scratch `$S` removed after copying evidence; every cited artifact is in `w1/out/X2Replica/`. The copied JSONs name scratch paths by design (the counter's contract requires `realpath` inside `--scratch`); the re-acquirable anchors are `inputs.*_sha256` plus the two https URLs in the receipts.

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica/replay-2.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica/rerun-2.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica/replay-3.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica/rerun-3.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica/replay-r46-v3.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X2Replica/proposed-compare.patch`
