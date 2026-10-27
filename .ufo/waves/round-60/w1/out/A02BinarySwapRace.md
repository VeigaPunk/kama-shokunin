# A02BinarySwapRace — round 60 w1, C1 falsification (operability)

Seat: leaf member, no verdict. Attacked claim: **C1-r60** ("the lane starts the digest-pinned
official Ollama release …") — specifically the digest-then-exec gap in
`tools/kama-ollama-live.py`: the tool hashes the server file once (line 259), then execs the same
path twice — `subprocess.Popen([binary, 'serve'])` (line 283) and later
`subprocess.run([binary, 'create', …])` (line 339) — with no re-verification between hash and exec.
Question: can a file swapped into that gap end in `MODEL_OK` with a non-pinned running program, and
does the post-start `running-exe-digest` check (lines 311–314) catch it?

## Answer in one line

The race is winnable 16/16 times; the swapped exec runs an attacker script that passes **15 of 16**
graded checks, and the single check that blocks `MODEL_OK` every time is `running-exe-digest`
(verdict `FAIL`, exit 1, 16/16). `MODEL_OK` with a non-pinned **running server** was not achieved.
However a **second** unguarded exec exists: swapping the path after `running-exe-digest` has passed
yields a fully green `MODEL_OK` (6/6) during which a non-pinned script ran as the `create` client —
no receipt field records it.

## Baselines (both on scratch copies; installed binary untouched, verified)

- `ctrl-ok2`: tool on a byte-identical copy of `bin/ollama` (sha256 `b0a4becf…1b4c`, `cmp` clean) plus
  `lib/ollama` sibling → **`MODEL_OK`, exit 0, all 16 checks passed** (receipt:
  `out/A02BinarySwapRace/receipts/ctrl-ok2-MODEL_OK.json`). Proves the environment reproduces the
  committed receipt.
- `ctrl-direct`: tool pointed straight at the payload script → **`BINARY_DIGEST_MISMATCH`, exit 2**
  (`receipts/ctrl-direct-BINARY_DIGEST_MISMATCH.json`). The pre-start hash gate holds when there is
  no race.
- Environmental note (not a defect): a bare copy of `bin/ollama` **without** its `lib/ollama/`
  sibling passes 13 checks but honestly fails `generate`/`ps-lists-loaded`/`evidence-after-load`
  ("llama-server binary not found") — fail-closed, `FAIL` exit 1. Reproducibility caveat for anyone
  re-running with `--ollama-bin` copies.

## Race method (documented per assignment)

Per attempt (driver: `out/A02BinarySwapRace/method/driver.sh`):

1. Fresh dir; `target` = hardlink of the verified pinned copy; a staged payload twin sits beside it.
2. A racer process (`method/exchange.py`) is armed with the tool's pid via a flag file, then busy-polls
   `/proc/<toolpid>/fd` for `target` being opened — that open is `sha256_file(binary)` (the only open
   of the path before exec).
3. At the hash fd's **close**, the racer fires one `renameat2(RENAME_EXCHANGE)` swapping `target`
   with the payload — atomic, so the path never briefly disappears. The tool then hashes the gguf,
   picks a port (~1–3 ms) and execs the path, which now holds the payload.
4. Payload (`method/payload.py`): a `#!/usr/bin/python3` script impersonating enough of Ollama to
   satisfy every graded check — `GET /` → `Ollama is running`, `/api/version` → `0.40.11`, empty
   `tags`/`ps`, `create` argv handler that records state in `$HOME`, post-create `tags`/`v1/models`
   with a 64-hex digest, `api/generate` → `done=true`, loaded `ps`. It logs every exec
   (`method/hit-log-excerpt.txt`): `exe=/usr/bin/python3.14`.

Attempts: **1 aborted** (`SETUP_ERROR`, nonce regex — my driver bug, before any swap), then
**16/16 armed attempts won the race** (exchange fires 19.5–20.6 ms after the hash open, i.e.
immediately at close of the 40 MB read; exec lands ~1–3 ms later). The 200-attempt fallback
(code-reading proof) was not needed for winnability, but the code-reading proof is included below
because the falsifier needs it.

## Stage 1 result — does `running-exe-digest` catch a swapped exec? YES

16/16 won races produced identical receipts:

- `binary_sha256` = `b0a4becf…1b4c` (pin) — the **hash** saw the pinned file;
- hit log shows the child was `python3.14` running the payload with argv `['serve']`;
- every other graded check **passed** (ready, version, listener-owned, tags-empty, create,
  tags-lists-model, v1-models, evidence-before `available_not_loaded` exit 1, generate,
  ps-lists-loaded, evidence-after `loaded_same_digest` exit 0, teardown);
- `running-exe-digest` **passed=false** → verdict **`FAIL`, exit 1**.

Canonical receipt: `receipts/stage1-won-att-1-1-FAIL-exe-digest.json` (and `…att-1-7…`). A ~120-line
script satisfied the entire graded HTTP/evidence surface; the tool's only binding of the running
program to the pin is that one check, and it held 16/16.

### Code-reading proof of which receipt field differs (independent of any race)

`MODEL_OK` (exit 0) requires `evaluated_failed` empty (lines 427–432). The only evaluated check that
can fail for a swapped exec is `running-exe-digest` (line 314): it compares
`sha256_file(f'/proc/{proc.pid}/exe')` to `pin['bin_sha256']`. For a `#!`-script, `/proc/<pid>/exe`
resolves to the interpreter (observed: `/usr/bin/python3.14`) — hash ≠ pin → `passed=false` →
`FAIL`. If `/proc/<pid>/exe` is unreadable, `exe_sha=None` → also fails (fail-closed). Therefore the
receipt field that differs is `checks[].id='running-exe-digest'.passed` (and consequently `verdict`
`MODEL_OK`→`FAIL`, exit 0→1); no other field can distinguish a fully-cooperating fake, since
`binary_sha256` records the hash-at-hash-time and `argv_child` only the path string.

## Stage 2 result — the second exec is unguarded (new defect-shaped finding)

`running-exe-digest` runs once, right after `/api/version` (lines 311–314), but the tool execs the
same path again at line 339 for `ollama create`. Swapping the path **after** the child appears
(trigger: the tool writing `Modelfile`, the last action before that exec; racer:
`method/exchange2.py`):

- **6/6 `MODEL_OK`, exit 0, all 16 checks green** (receipt:
  `receipts/stage2-att-2-1-MODEL_OK-payload-client.json`) while `hit-log-excerpt.txt` records
  `PAYLOAD-CLIENT … exe=/usr/bin/bash argv=create kama-aa2x00Nz -f …` — a non-pinned script ran as
  the create client inside an otherwise-pinned run. In these runs the client delegated via
  `exec pinbin "$@"`, so the server stayed pinned; the honest claim is: *a `MODEL_OK` run during
  which a non-pinned program executed under the tool's digest pin*, not *a non-pinned running
  server*.
- **6/6 stage-2b** (`payload-client-exit0.sh`, log-and-exit-0 client): `create` check **passes**
  ("exited 0") but `tags-lists-model`/`v1-models`/evidence/generate/ps fail → `FAIL` exit 1. The
  model-listing checks are an incidental backstop for a *non-cooperating* client; they are not
  identity checks, and a client that speaks `/api/create` itself would be indistinguishable.

Fix-shaped suggestions (not applied, lane read-only for me): re-verify the digest immediately before
**each** exec of the path (or hold an opened fd and `fexecve`/`execveat` it, closing the TOCTOU
outright), and record the create client's identity in the receipt.

## Receipts (exact)

| file | verdict | exit | note |
|---|---|---|---|
| `receipts/ctrl-ok2-MODEL_OK.json` | `MODEL_OK` | 0 | baseline, pinned copy + lib tree |
| `receipts/ctrl-direct-BINARY_DIGEST_MISMATCH.json` | `BINARY_DIGEST_MISMATCH` | 2 | payload offered with no race |
| `receipts/stage1-won-att-1-1-FAIL-exe-digest.json` | `FAIL` | 1 | race won, only `running-exe-digest` false |
| `receipts/stage1-won-att-1-7-FAIL-exe-digest.json` | `FAIL` | 1 | second sample of 16/16 identical |
| `receipts/stage2-att-2-1-MODEL_OK-payload-client.json` | `MODEL_OK` | 0 | non-pinned create client, nothing in receipt differs |
| `receipts/stage2b-att-2b-1-FAIL-tags.json` | `FAIL` | 1 | exit-0 client passes `create`, fails model listing |

Full per-attempt ledger: `method/summary.csv` (28 rows: 1 abort, 16 stage-1 wins, 6 stage-2, 6
stage-2b — counts from attempts 1..15 batch plus the smoke win att-1-1). Method scripts and hit log:
`method/`.

## Residual risk and verification gaps

- The fake server was mine and cooperated fully; a *partially* cooperating payload (e.g. wrong
  version string) would fail earlier checks — irrelevant to the finding, which is about identity
  binding, not surface fidelity.
- I did not attempt to defeat `running-exe-digest` itself (e.g. loader tricks that change
  `/proc/pid/exe` after the check) — out of scope for "swap between hash and exec"; the check's
  single-shot placement is what stage 2 exploits.
- Attacked only Ollama v0.40.11 as pinned; the gap is in the tool's hash/exec structure, so it is
  version-independent by construction [INFERENCE from code reading, not tested on other versions].
- All scratch under `/fast/scratch/hyaku/kama-r60/A02BinarySwapRace/` with `TMPDIR` set; removed
  after copying receipts out. Installed binary and lane tree untouched (no writes, no installs; the
  pacman guard was never engaged).
