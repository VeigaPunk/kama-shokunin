# F16C1ToolAcquisition — C1 tool-acquisition integrity chain, attack findings (w2, 2026-10-27)

Seat: F16C1ToolAcquisition (advisory leaf, attack-only). Lane read-only except this out dir.
Frozen refs verified as commits in the lane repo: freeze `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`,
controls `8b9f3060966c22bede3094d748974caf041b4c33` (both `git rev-parse --verify …^{commit}` → rc 0).
Blob identity across freeze commit / controls commit / working tree (`git show <rev>:<f> | sha256sum`):
`tools/kama-ollama-live.py` 9d1c688bd2951485fa5701ca2273b98e7333ec95060c34bbdb76942050472aaf,
`registry/ollama-live-pin.tsv` da0948f76b09375cc5823cfe71c0383fe52a4280a495c3678be2a0b47405f66e,
`tools/round60-c1-counter.py` 175c291674fc53e71d415fa22e31b3665bcb52f4501ea56b638c405aef677d86 —
identical in all three states, so the code quoted below is exactly the measured artifact.
Disk guard before heavy tests: /fast 593G avail, /home 585G avail. Tool installs: none.
Scratch `/fast/scratch/hyaku/kama-r60/F16C1ToolAcquisition` (TMPDIR explicit) removed on exit.

## 1. Pin vs official release — VERIFIED end to end today

- GitHub API release `v0.40.11` asset `ollama-linux-amd64.tar.zst`: size 1508659610, digest
  `sha256:7bedab90dd122661be78798e9f0edf37fccf0cccf2699d2c58ea1a3afdc04b6d` — equals pin `archive_sha256`.
- Release asset `sha256sum.txt` (1472 B, sha256 `c020ec823b5652daf0d4dfc2b35a2365d9bb0fe4318debe6eb8a64ab2d147889`,
  equal to its GitHub asset digest) line 6:
  `7bedab90dd122661be78798e9f0edf37fccf0cccf2699d2c58ea1a3afdc04b6d  ./ollama-linux-amd64.tar.zst` — pin comment holds.
- Downloaded archive re-hashed: 1508659610 B, `7bedab90…4b6d` — matches pin and checksum file.
- Extracted `bin/ollama`: 40779408 B, sha256 `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c`
  — matches pin `bin_sha256` and is `cmp`-identical to the installed `~/.local/opt/ollama-v0.40.11/bin/ollama`.
- Archive also ships the inference runner `lib/ollama/llama-server`, sha256
  `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`, `cmp`-identical to the installed copy.

## 2. FINDING (reproduced): the digest chain pins only `bin/ollama`; the runner is unpinned at run time

Attack: take an archive-faithful tree, append one byte to `lib/ollama/llama-server`
(`234b05b2…696b` → `8dc54bbd2905d9ede11b617b3213c1a24396e4e0fa9c98c8e02eec90784b16e7`), run the tool
against it. Same mutation the counter itself uses as a control on `bin/ollama`.

| run | tree | verdict | checks | exit | port |
|---|---|---|---|---|---|
| partial (bin/ollama only) | hash-valid, no lib/ | FAIL | 13/16 (generate 500, llama-server not found) | 1 | 44975 |
| full archive extract | pinned runner | MODEL_OK | 16/16 | 0 | 58393 |
| tampered runner | byte-appended `llama-server` | MODEL_OK | 16/16 | 0 | 40679 |

The tampered run's `generate` check passed ("returned done=true with a response string"): generation was
performed by the modified runner while `binary-digest` and `running-exe-digest` (both hash only the
`ollama` entry binary and its `/proc/<pid>/exe`) were green. Receipts preserved beside this file:
`receipt-partial-runner.json`, `receipt-full-archive.json`, `receipt-tampered-runner.json` (nonces
`f16a1c2e3b4d` / `f16b5c7d9e01` / `f16c0ffee123`). `ollama create` does not need the runner (passed in the
partial run), so even the create→tags→v1 surfaces run against a runner-less tree before generate fails on
outcome, not on digest. No listener survived any run (0 entries in /proc/net/tcp{,6}); no stray processes.

Consequences for the counter's guarantee: `round60-c1-counter.py` freezes `FROZEN_BIN_SHA` and re-hashes
the imported blob, but it inherits the same blind spot — a receipt from the tampered tree would be accepted
(`binary_sha256 == FROZEN_BIN_SHA` holds; every other artifact is genuine). The 7 controls catch a patched
entry binary and miss a patched runner. The runner hash appears nowhere in registry/, tools/, or corpus/
(grep for `234b05b2…` → absent), so no instrument can notice a swap of `lib/ollama/*` (runner, ggml/llama
shared objects, cuda/vulkan libs) after install.

## 3. FINDING: counter proves file hash only, never archive provenance

- `kama-ollama-live.py` requires `archive_sha256` in the pin (`load_pin` line 81) and echoes it into
  `receipt['pin']` (line 246), but no code path downloads, opens, or hashes any archive. The tool's entire
  acquisition check is `sha256_file(binary) == pin['bin_sha256']` plus the `/proc/exe` re-hash.
- `round60-c1-counter.py` never references the archive either; its constants are the version, entry-binary
  hash, and model hash only.
- `verify()` does not inspect `receipt['pin']` at all — that block is decorative.
- Therefore the archive→binary link rests on (a) the one-time operator install recorded in the pin comment
  and (b) manual re-derivations like §1 (this seat; K01's sha256sum.txt re-fetch). Upstream publishes no
  signature for these assets, so "official" reduces to TLS + the frozen digests; within that model §1 holds
  today, and the per-run guarantee covers exactly the entry binary's file bytes.

## 4. Minor findings

- `free_port()` excludes REGISTERED_PORTS {8080, 34113} and listening ports but not 11434; safe on this
  host only because `ip_local_port_range` = 32768–60999 cannot yield 11434. Host-dependent, latent.
- `verify()` re-hashes `cap["body"].encode("utf-8")` while the tool hashed the raw response bytes
  (`raw.decode('utf-8','replace')`); a capture containing invalid UTF-8 would make an honest receipt
  unverifiable. Not triggerable by this server's ASCII/JSON bodies; latent calibration asymmetry.
- The freeze's own sentence scopes the pin to "bin/ollama sha256 …, archive sha256 …" — the claim text is
  honest; the gap is that "runs the digest-pinned official release" silently excludes the runner that
  actually executes generation.

## 5. Not attacked / residual

Did not re-run the full 7-control counter (W1 A01/A07/MT01 exercised it at this tip; my tampered-tree
acceptance argument is derived from `verify()`'s frozen constants, all of which the tampered receipt
satisfies by construction). No claim verdicts altered; attack-only.
