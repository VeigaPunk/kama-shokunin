# X2Offline - round 47 replay failure modes (C2 operability)

**Verdict:** four of the five assigned failure modes fail closed (exit 2, `rerun_receipt: null`, no receipt on disk, no orphan server); the fifth, `--timeout 1`, does **not** fail closed at all - it *completes and matches* (exit 0), because the replay lifecycle measures 199 ms and a 1 s bound cannot trip it. That is the item's expectation being wrong about the tool, not a fail-open: no unverified or un-reproduced receipt was accepted. The genuine timeout path (0.05 / 0.15 / 0.18 s) does fail closed. Three residual-contract findings follow (`--timeout` does not bound acquisition; refusals leave 80.5 MB plus a *stale* `rerun-receipt.json` when `--work` is reused; extraction precedes member validation).

## Bytes under test (verified equal to the build tip, not the worktree head)

| file | sha256 |
|---|---|
| `tools/kama-live-replay.py` (ran) | `39cd387a3a95b47865d81484ffe30664e653d5016c4c75d47abf6e855e43fdd0` |
| `tools/kama-llamacpp-live.py` | `65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d` |
| receipt copy (`receipt-1.orig.json` = committed `c2/live/receipt-1.json`) | `a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d` |

`git -C kama-shokunin show 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/kama-live-replay.py | sha256sum` prints the same `39cd387a...`; same for the live tool and receipt-1. The lane worktree head during the wave was `46a924e027f05614558c45ff02bf7a94ca57d3e1`, whose copies of these three files hash identically, so no ambiguity about which bytes ran.

Command shape for every case (mutated receipt copies are in `X2Offline/receipts/`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
        --receipt <copy> --work /fast/scratch/hyaku/kama-r47/X2Offline/work/<case> \
        --out <case>.json [--timeout T]
```

## Results

| case | mutation of receipt-1 | exit | `refused` (J) | rerun receipt | left under `--work` |
|---|---|---|---|---|---|
| a | `server.asset_url` -> existing-release 404 name | **2** | `could-not-run:HTTPError:HTTP Error 404: Not Found` | no | 0 bytes; empty `download/` only |
| b | `model.url` -> `tinyllamas/stories15M-q4_0.gguf` (real sha `66967fbe...`), recorded sha kept | **2** | `digest-mismatch:stories15M-q4_0.gguf:want=270cba...:got=66967fbece6dbe97886593fdbb73589584927e29119ec31f08090732d1861739` | no | `download/llama-b11909-bin-ubuntu-x64.tar.gz` 22,475,032 B (verified asset kept); model unlinked |
| c | `model.url` -> `https://127.0.0.1:9/m.gguf` | **2** | `could-not-run:URLError:<urlopen error [Errno 111] Connection refused>` | no | same 22,475,032 B archive |
| c2 | `server.asset_url` -> `https://127.0.0.1:9/x.tar.gz` (extra, asset side) | **2** | `could-not-run:URLError:<urlopen error [Errno 111] Connection refused>` | no | 0 bytes; empty `download/` |
| d | none, `--timeout 1` | **0** | `null` (`match: true`) | **yes** | 80,539,631 B incl. `server/` tree + `rerun-receipt.json` |
| e | `server.member` -> `llama-b11909` (a directory inside the archive) | **2** | `member-absent:llama-b11909` | no | 80,510,696 B: archive 22,475,032 + model 1,185,376 + extracted `server/llama-b11909/` **56,850,288** (53 files) |

No `.part` file survived any case (`partfiles=0` for all), and `rerun-receipt-present=no` for every refusal. Raw stdout / inventory per case: `X2Offline/logs/<case>.stdout`, `.inventory`, `.summary`, `.exit`; replay JSONs: `X2Offline/out-json/`.

### (d) `--timeout 1` - measured behaviour

```
replay match=True refused=None mismatches=0 exit=0
rerun receipts: orig 21:16:50.545Z->21:16:50.722Z (177 ms), replay rerun 21:26:43.126Z->21:26:43.325Z (199 ms)
```

The flag is passed only to the lifecycle subprocess (`tools/kama-live-replay.py:157`), and the lifecycle it bounds is ~0.2 s warm. A 1 s bound therefore cannot produce a refusal on this host; the item's "each must fail closed with exit 2" is falsified for (d) by measurement. The same receipt at tighter bounds was run to exercise the real path:

| `--timeout` | exit | `refused` | rerun receipt | server launched? | residue |
|---|---|---|---|---|---|
| 0.05 | 2 | `could-not-run:TimeoutExpired:...` | no | no (killed during tool start-up) | 80,510,696 B, `tmp/` empty |
| 0.15 | 2 | `could-not-run:TimeoutExpired:...` | no | **yes** - pid 3384322 `llama-server ... --port 34731` seen by a 10 ms `pgrep` poller, gone after | 80,511,796 B + `tmp/kama-llamacpp-live-fsq21c__.log` 1100 B |
| 0.18 | 2 | `could-not-run:TimeoutExpired:...` | no | yes - pid 3765052 | 80,511,796 B + `tmp/kama-llamacpp-live-qzssbp06.log` 1100 B |
| 0.3 | 0 | `null` (`match: true`) | yes | yes | 80,539,642 B |

**No orphan llama-server.** After every killed run, `pgrep -af "kama-r47/X2Offline"` was empty; `kama-llamacpp-live.py`'s `PR_SET_PDEATHSIG` (`tools/kama-llamacpp-live.py:461-470`, `preexec_fn=_preexec_pdeathsig` at :1522) reaps the server when the replay SIGKILLs the live tool. The mid-run poller capture and the empty post-run check are in `X2Offline/logs/d-timeout0.15.poller-x2only` and `X2Offline/logs/d-timeout0.18.poller-x2only` (filtered to my scratch; the same poller caught other seats' `L2Concurrent` servers, which I left untouched).

## Findings

### F1 - `--timeout` bounds only the lifecycle, never acquisition (medium)

`tools/kama-live-replay.py:57` `def fetch(url, dest, timeout=120)` hardcodes 120 s; `tools/kama-live-replay.py:89` `def acquire(url, sha, dest)` calls `fetch(url, dest)` without a timeout; the flag reaches only `subprocess.run(..., timeout=timeout)` at `:157`. Proof by observation: `--timeout 0.05` still downloaded and hashed 22,475,032 B + 1,185,376 B before refusing (`X2Offline/out-json/d-timeout0.05.json` has `archive_sha256` and `model_sha256` populated; the run took ~2 s of network). Consequence: a connected-but-stalled host can hold a replay for up to 2x120 s regardless of `--timeout`, and a harness that treats `--timeout` as the replay's bound is wrong.

Proposed fix (full diff, not applied):

```diff
-def acquire(url, sha, dest):
-    fetch(url, dest)
+def acquire(url, sha, dest, timeout=120):
+    fetch(url, dest, timeout)
@@
-        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"], archive)
-        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"], model)
+        deadline = time.monotonic() + timeout
+        left = lambda: max(1.0, deadline - time.monotonic())
+        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"], archive, left())
+        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"], model, left())
```

plus `import time` and a docstring line "`--timeout` bounds acquisition and the lifecycle together".

### F2 - a failed body copy leaves `<dest>.part` under `--work` (low, code-read)

`tools/kama-live-replay.py:59-62`: the download streams into `dest + ".part"` and `os.replace`s it only on success; there is no `try/except` unlink. Not observed in these six refusals, because every failure here happened either before the temp file was opened (404 at `urlopen`, refused connection at `urlopen`) or after the rename (digest mismatch, where `acquire` at `:92` unlinks `dest` itself). A mid-stream timeout or ENOSPC would leave the partial file. Proposed fix: wrap the copy in `try: ... except BaseException: os.unlink(tmp)` then re-raise.

### F3 - refusals after acquisition leave 80.5 MB, and a stale `rerun-receipt.json` survives a reused `--work` (medium, operability of the tool)

`tools/kama-live-replay.py:136-149` creates/uses `--work` without clearing it and always writes the rerun receipt to the fixed name `work/rerun-receipt.json` (`:149`). Case e leaves 80,510,696 B; cases d*/b/c leave 80.5 MB / 22.5 MB.

The sharper half: a refused replay into a `--work` that already holds a previous run's receipt leaves that receipt byte-identical while J says `rerun_receipt: null`:

```
$ ls -l work/d-timeout1/rerun-receipt.json      # from the earlier --timeout 1 run
-rw------- 1 vgpnk vgpnk 28935 ... rerun-receipt.json   sha256 b54e84a5fda35aa330e7f744bb1d164e8aec049c95a0fda2ad47dc856dbbf0ee
$ python3 .../kama-live-replay.py --receipt receipt-a-asset404.json --work work/d-timeout1 --out stale-reuse.json
replay match=False refused=could-not-run:HTTPError:HTTP Error 404: Not Found mismatches=0 exit=2
$ sha256sum work/d-timeout1/rerun-receipt.json                 # unchanged
b54e84a5fda35aa330e7f744bb1d164e8aec049c95a0fda2ad47dc856dbbf0ee
$ jq .rerun_receipt stale-reuse.json
null
```

The tool's own contract is intact (J points at nothing), but "leaves no rerun receipt" is only true for a fresh `--work`; a consumer that reads `work/rerun-receipt.json` by path would take the stale pass receipt as this run's. The frozen C2 counter is **not** exposed: it uses a distinct fresh work dir per leg (`tools/round47-live-replay-audit.py:262` `work-replay`, `:313-314` `work-model` / `work-asset`) and reads the rerun receipt through `j.get("rerun_receipt")`, so this does not change any C2 leg's verdict. Proposed fix: at the top of `replay()`, unlink a pre-existing `work/rerun-receipt.json` (or write rerun receipts under `work/<run-id>/`) and record `"residue_bytes"` in J so a caller can see what a refusal cost.

### F4 - member validation happens after full extraction (low)

`tools/kama-live-replay.py:143-147`: `extract(archive, tree)` runs, then `os.path.isfile(server)` refuses case e. Correct and fail-closed, but the invalid-member refusal pays the full 56.85 MB extraction and leaves it behind (see the e row). Proposed fix: validate first, e.g.

```diff
+        with tarfile.open(archive) as tf:
+            names = {m.name for m in tf.getmembers() if m.isreg()}
+        if need["server.member"] not in names:
+            raise Refused(f"member-absent:{need['server.member']}")
         tree = os.path.join(work, "server")
         extract(archive, tree)
```

## Additional probes (beyond the item's five)

- **a2 - asset URL returns 200 with an HTML body** (`releases/tag/b11909` instead of the asset): exit **2**, `digest-mismatch:b11909:want=bf94332a...:got=87aff91c...`, **0 bytes** left - the digest is checked before any extraction, and `acquire` removes the bad file. Good.
- **b2 - receipt rewritten self-consistently** (`model.url` -> `stories260K-infill.gguf`, *both* `provenance.model.sha256` and `model.sha256` set to its real digest `102f2a00a5bfc56d0706467830bda9e39fa5d7df1cd55e47291dd25b4b509140`): exit **0**, `match: true`. Expected by design - replay proves reproducibility from the recorded provenance, not authenticity; the only anchor is the committed receipt's own bytes. This is the boundary of the C2 claim's "refuses a receipt whose recorded digest is wrong": it refuses a *wrong* digest (b, and the counter's tamper leg), it cannot refuse a *rewritten* one.

## Limits of this seat's evidence

- One host, one network path, one 260K model, llama.cpp b11909 only; downloads ran at ~10-20 MB/s (github/HF), so the acquisition-time claims in F1 are structural (code + the 0.05 s run), not timing measurements under load.
- I did not run the frozen counters (`round47-append-audit-v2-check.py`, `round47-live-replay-audit.py`); the L1 owns the measurement. I did read the counter's replay/tamper/newrow legs to check that F3 cannot leak into C2.
- No lane file, no counter, no preregistration was modified; no tool was installed (nothing needed); no `pacman`; no service started or stopped by me. The only llama-server processes I caused ran under my scratch and are all gone (`pgrep -af kama-r47/X2Offline` empty after each run).
- Other seats' live servers were visible while my poller ran; they are not mine and are cited nowhere as my evidence.

## Artifacts (base: `.ufo/waves/round-47/w1/out/`)

- `X2Offline/receipts/` - `receipt-1-copy.json` (unmutated copy, sha in `X2Offline/logs/receipt-1-copy.sha256`) and the seven mutated receipts (`receipt-a-asset404`, `-a2-html`, `-b-modelother`, `-b2-selfconsistent-forge`, `-c-model-unreachable`, `-c2-asset-unreachable`, `-e-member-dir`).
- `X2Offline/out-json/` - all 13 replay JSONs (the 12 cases plus `stale-reuse.json`).
- `X2Offline/logs/` - per-case `stdout`, `summary`, `inventory`, `exit`; the two filtered orphan pollers.
