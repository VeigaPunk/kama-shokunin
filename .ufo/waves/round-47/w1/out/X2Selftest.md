# X2Selftest — round 47 / kama / operability (C2, kama-live-replay)

**Verdict:** the additional offline selftest case is implemented, applied to the tip blob in a
scratch clone and run green — the REAL `tools/kama-llamacpp-live.py` is driven end to end through
`replay()` over a `file://` archive built from the local llama.cpp b11909 install and the pinned
stories260K GGUF: `KLR_SELFTEST pass=11 fail=0 not-evaluated=0`, exit 0, the rerun receipt
reproducing the lane's install-tree and link digests exactly, and both skip paths printing a
`not-evaluated` line with exit 0.

## Delivered

Artifacts sit next to this file in `.ufo/waves/round-47/w1/out/X2Selftest/`:

| File | What |
|---|---|
| `kama-live-replay.add-real-live-case.diff` | unified diff (a/tools/… b/tools/…) against the tip blob `3773e62da07a9eaf9329be93c3c5c1f65415cc21`; sha256 `339928b8a7e664f23e9182e3e3300e887588fdd728724f46247c1857db3985d1` |
| `kama-live-replay.py.patched` | full proposed text of `tools/kama-live-replay.py`; sha256 `89906dfe224391f783b3baa6078dc1726767b036494b98f9edfae0de60f1efce` |
| `selftest.log` | `--selftest` of the patched copy, live tool = lane path (via `KLR_SELFTEST_LIVE`) |
| `selftest-applied-clone.log`, `selftest-applied-clone-2.log` | `--selftest` after `git apply` in a scratch clone, **no env override** (DEFAULT_LIVE = the real tool), run twice: identical archive digest |
| `selftest-skip-server-absent.log`, `selftest-skip-model-digest.log` | the two not-evaluated paths |
| `driver.log` | discrimination proof: honest / mutated-check / mutated-outcome receipts through `replay()` |
| `real-live-rerun-receipt.json` | the v4 receipt the real live tool produced under `--work` (sha256 `1cdfa6e8…`) |

## The case (file:line in the patched text)

* `REAL_MODEL_SHA` — the pinned stories260K digest (`kama-live-replay.py.patched:48`).
* `REAL_REQUIRED_CHECKS` (`:52`) — every v4 check whose verdict is deterministic for a fixed server
  and model; `loading_envelope_graded` is deliberately absent because a fast model can legitimately
  leave the 503 window unobserved (the live tool then records not-evaluated, not a failure).
* `_real_live_case(root)` (`:187`):
  * inputs env-first (`KLR_SELFTEST_LIVE` / `_SERVER` / `_MODEL`), defaults = the lane live tool
    (`DEFAULT_LIVE`), `~/.local/opt/llama-b11909`, `~/.cache/kama-shokunin/models/stories260K.gguf`;
  * any absent input, or a model whose digest is not the pinned one → `(None, reason)`, i.e.
    **not-evaluated, never a pass and never a fail**;
  * builds `<scratch>/llama-b11909.tar.gz` from the install with `gzip … mtime=0`
    (`:228-230`), so a fixed install yields a fixed archive digest;
  * writes a minimal v4 receipt whose provenance carries `file://` URLs, the measured archive
    sha256, member `llama-b11909/llama-server`, and the pinned model sha256;
  * calls the real `replay()` with `timeout=900` and then asserts, on the rerun:
    exit 0, `live_exit` 0, `match` true, both `inputs` digests, schema v4 + `outcome: pass`,
    server/model digests, **server.realpath == `work/server/<member>`** and model path under
    `--work` (inputs were re-acquired, not reused), `teardown.log_path is None`,
    `alive_at_teardown_start is True`, `sigterm_sent`/`returncode 0`/`port_refuses` and
    `sigkill_sent False`, all `REAL_REQUIRED_CHECKS` evaluated `true`, and the provenance block
    echoing the receipt's exactly.
* Wiring (`:376`) appends the case to `cases` and the summary (`:382`) distinguishes
  `not-evaluated=N` from `fail=N`; exit code is still `0` unless a case actually failed.

## Evidence (commands, exit codes)

Base is the commit, not the working tree:

```
$ git -C kama-shokunin rev-parse 3a09a1d9:tools/kama-live-replay.py
3773e62da07a9eaf9329be93c3c5c1f65415cc21     # 267 lines, sha256 39cd387a3a95…
$ git show 3a09a1d9:tools/kama-live-replay.py > $S/base.py && diff -u … > kama-live-replay.add-real-live-case.diff
$ grep -c '^-[^-]' kama-live-replay.add-real-live-case.diff
4            # only the docstring line + the three old summary lines; no collateral removals
```

Patch application and identity (scratch clone `git clone --shared … $S/lane`, `rev-parse
--show-toplevel` = the clone):

```
$ git -C $S/lane apply --check  $S/kama-live-replay.add-real-live-case.diff ; echo $?   # 0
$ git -C $S/lane apply         $S/kama-live-replay.add-real-live-case.diff ; echo $?   # 0
$ cmp $S/lane/tools/kama-live-replay.py $S/kama-live-replay.py ; echo $?                # 0 (byte-identical)
$ python3 -m py_compile $S/kama-live-replay.py ; echo $?                                # 0
```

Run of the patched copy in the clone (`--scratch` = my scratch, no env override, so
`DEFAULT_LIVE` = the clone's real `tools/kama-llamacpp-live.py`, sha256 `65301a3c76f9…`, the same
bytes as the lane file):

```
$ cd $S/lane && python3 tools/kama-live-replay.py --selftest --scratch $S ; echo $?     # 0
pass match: exit=0 refused=None mism=[]
pass check-differs: exit=1 refused=None mism=['check:health_ready:False->True']
pass model-digest-wrong: exit=2 refused=digest-mismatch:m.gguf:want=000…000:got=118b0a5faf18…
pass asset-digest-wrong: exit=2 refused=digest-mismatch:srv.tar.gz:want=111…111:got=081eca8ff60d…
pass model-digest-differs-from-receipt: exit=2 refused=provenance-model-digest-differs-from-receipt-model mism=[]
pass v3-receipt: exit=2 refused=not-a-v4-receipt:kama-llamacpp-live/v3 mism=[]
pass missing-url: exit=2 refused=provenance-missing:model.url mism=[]
pass unsafe-member: exit=2 refused=unsafe-member:../x mism=[]
pass absent-member: exit=2 refused=member-absent:build/bin/nope mism=[]
pass http-refused: exit=2 refused=url-scheme:http://example.invalid/m mism=[]
pass real-live-e2e: live=…/lane/tools/kama-llamacpp-live.py live-sha256=65301a3c76f9 member=llama-b11909/llama-server archive-sha256=8784c151144d checks=11 teardown=rc0/port-refuses/term-only provenance-echo=ok (--work was a fresh re-extraction)
KLR_SELFTEST pass=11 fail=0 not-evaluated=0
```

Second identical run printed `archive-sha256=8784c151144d` again → the built archive is byte-stable
(24,559,647 bytes; full sha256 `8784c151144d4cf7d1dcd4c4220c34ed4436a7683be26aff5ffac04a20916481`).
Wall time per run ≈ 1.0 s (55 MB install tarred at level 1, ~55 MB re-extracted and hashed).

Skip paths (exit 0, one `not-evaluated` case, `fail=0`):

```
$ KLR_SELFTEST_LIVE=…/tools/kama-llamacpp-live.py KLR_SELFTEST_SERVER=$S/absent-llama \
    python3 kama-live-replay.py --selftest --scratch $S                                # 0
not-evaluated real-live-e2e: server-absent:$S/absent-llama/llama-server
KLR_SELFTEST pass=10 fail=0 not-evaluated=1

$ KLR_SELFTEST_MODEL=/etc/hostname … --selftest --scratch $S                           # 0
not-evaluated real-live-e2e: model-digest-differs:694cd433b421…:want=270cba1bd510…
KLR_SELFTEST pass=10 fail=0 not-evaluated=1
```

The rerun receipt the real tool wrote under `--work` (`real-live-rerun-receipt.json`):

```
schema kama-llamacpp-live/v4  outcome pass  alias klr-real  ctx 256  threads 1  port 39545
server.sha256            35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
install_tree_sha256      9f1198f4e2d64495ea6e6c6dece9f95a34ab2e4e2a11f72fd7debd1024d5542e
install_links_sha256     5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060
model.sha256             270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
teardown                 log_path=None, returncode=0, sigterm_sent=True, sigkill_sent=False,
                         alive_at_teardown_start=True, port_refuses=True, term_wait_ms=3
checks                   11/11 evaluated true
argv[0]                  …/work-honest/server/llama-b11909/llama-server   (extracted copy, not ~/.local)
provenance               {"server":{"asset_url":"file://…/llama-b11909.tar.gz",
                                    "asset_sha256":"8784c151…","member":"llama-b11909/llama-server"},
                          "model":{"url":"file://…/stories260K.gguf","sha256":"270cba1b…"}}
```

Both digests equal `kama-shokunin/.ufo/waves/round-47/c2/live/receipt-1.json`
(`install_tree_sha256` 9f1198f4…, `install_links_sha256` 5cb9f486…) — the archive → extract →
hash round trip reproduces the lane receipt's install identity exactly, so the case exercises the
same object C2 measures rather than a stand-in.

## Discrimination proof (`driver.log`)

Same `file://` archive and real live tool, three receipts through `replay()`:

```
honest                     exit 0  match true   mismatches []
mutated-health-ready-false exit 1  match false  ["check:health_ready:False->True"]
mutated-outcome-fail       exit 1  match false  ["outcome:fail->pass"]
```

The comparator fires on a real rerun receipt (11 evaluated checks, real digests, real teardown), so
the green case above is not vacuous. The driver itself was scratch-only (it imports the patched
module and calls `replay()` three times); `driver.log` is its complete output, including the
archive/model/live digests it used.

## Findings / risks

1. **Lane working tree is dirty on the very file this patch targets** (not my change; I wrote
   nothing in the lane). At 18:32 local `tools/kama-live-replay.py` in the lane matched
   `3a09a1d9` (267 lines, `39cd387a…`); at 18:35 local it read 288 lines, `80149f01…`,
   `git diff --stat` = `26 insertions(+), 5 deletions(-)` (adds `fetch()` `.part` cleanup, a `compare()` guard for an
   original with no evaluated check, `live-exit:` mismatches and `notes`). Reproduce with
   `git -C kama-shokunin status --porcelain tools/kama-live-replay.py`. My diff is against the
   commit blob `3773e62d`; whoever lands it must rebase on the committed tip, and the only conflict
   candidate is the `_selftest` tail (docstring + summary lines), not the new function.
2. Host-conditional by design: without `~/.local/opt/llama-b11909` (or `KLR_SELFTEST_SERVER`) and
   the pinned GGUF the case is `not-evaluated`, so a clean host gets no real-binary coverage — the
   item asked for exactly this, but it means the case cannot be the sole guard for C2.
3. Cost: ~1.0 s and ~80 MB of scratch I/O per `--selftest` run (24.6 MB archive + extraction). The
   frozen C2 counter `tools/round47-live-replay-audit.py` never invokes `--selftest`
   (`grep -n selftest` → no match), so the measurement lane pays nothing.
4. `KLR_SELFTEST_LIVE` is a seam: a fake live tool could be pointed at. Mitigated by printing the
   tool's absolute path and sha256 in the case line and by requiring the rerun receipt to show
   11 evaluated checks, the exact provenance echo, the teardown proof and `--work`-local inputs.
   Residual [INFERENCE]: a fake that reproduces all of that would pass; nothing cheaper proves the
   binary is the release.
5. The summary line gains `not-evaluated=N` (`:382`). Nothing parses `KLR_SELFTEST` — C2's counter
   reads none of it; C1's `AOA_SELFTEST` parser is a different tool.
6. Loopback hygiene: every run used a port the tool picked, tore the server down (SIGTERM, returncode
   0, port refuses) and left nothing behind — `pgrep -a llama-server` → no match, `ss -ltnp | grep
   -c llama` → 0 after the runs.

## Tooling

No installs or upgrades (no pacman, no uv/npm). Inputs were already present: llama.cpp release
install `~/.local/opt/llama-b11909` (from the lane's `c2/live/install.txt`, asset sha256
`bf94332a…`), model `stories260K.gguf` sha256 `270cba1b…`.

## Blockers

None. Scratch (`/fast/scratch/hyaku/kama-r47/X2Selftest`) held one `git clone --shared` of the lane
(+ one `git apply`/`checkout` inside it) and was removed after the evidence above was copied here.
