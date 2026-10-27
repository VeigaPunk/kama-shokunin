# S523 own-work gate — Rule 1 re-run of `tools/kama-ollama-live.py`

Row under gate: `row.md` beside this file (id S523, kind `own-work`, tier A, scope = the lane's own
re-runnable gate output). Lane commits named by the row: tool `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`,
receipt `8b9f3060966c22bede3094d748974caf041b4c33`; base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`.

Rule 1 for own-work replaces a URL quote with a re-run recorded here. Everything below was executed
in this seat's own scratch; nothing in the lane tree, the fleet root or `shokuknow` was written.

## 1. The re-run (the gate)

Scratch: `/fast/scratch/hyaku/kama-r60/S05OwnWorkLiveOllama`, `TMPDIR` exported to it.

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py \
        --work /fast/scratch/hyaku/kama-r60/S05OwnWorkLiveOllama/run \
        --out  /fast/scratch/hyaku/kama-r60/S05OwnWorkLiveOllama/r.json
```

| field | observed |
|---|---|
| exit code | **0** |
| wall elapsed (`date +%s.%N` around the call) | **1.63 s** |
| receipt `elapsed_s` (self-reported, run body only) | 1.59 |
| `verdict` | **MODEL_OK** |
| `schema` | `kama-ollama-live/v1` |
| `nonce` (fresh, tool-generated) | 2270754199cd |
| `port` (free, unregistered) | 41185 |
| `checks` | **16, all `passed: true` and `evaluated: true`** |
| `binary_sha256` | `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c` |
| `teardown` | `returncode` 0, `port_closed` true, `sigkill_needed` false |
| receipt sha256 | `2381c603cca2d2d1958aafb1f0ddb08113f6330c701f7feda0990c178a324c65` |
| receipt copy in this dir | `rerun-receipt.json` |

The 16 check ids, in receipt order: `binary-digest`, `model-digest`, `port-unregistered`, `ready`,
`version`, `running-exe-digest`, `listener-owned`, `tags-empty-before-create`, `create`,
`tags-lists-model`, `v1-models-lists-model`, `evidence-before-load`, `generate`, `ps-lists-loaded`,
`evidence-after-load`, `teardown` — the same 16 the C1 counter's `REQUIRED` list names, so the row's
`checks` cell is enumerable, not a count alone.

Inputs hashed before the run:

- server binary `~/.local/opt/ollama-v0.40.11/bin/ollama` = `b0a4becf…1b4c` (equals the row's `binary_sha256` and the pin's `bin_sha256`)
- fixture GGUF `~/.cache/kama-shokunin/models/stories260K.gguf` = `270cba1b…256d` (pin's `model_sha256`)
- tool `tools/kama-ollama-live.py` = `9d1c688bd2951485fa5701ca2273b98e7333ec95060c34bbdb76942050472aaf`, byte-identical to `git show e0b5b1ea:tools/kama-ollama-live.py`, so the re-run exercised the committed tool

The child was this seat's own: the tool chose the port, wrote `HOME`, the model store and `serve.log`
under `--work`, and killed only the PID it started. No registered port (8080, 34113, 11434) was used
or probed; no process was killed by name.

## 2. The committed anchor (what the row cites)

`git show 8b9f3060:.ufo/waves/round-60/live/receipt.json` is byte-identical to the worktree copy
(sha256 `49d06600521ce766488f4941b24a3f245883bf6744d0b214c21201f24090c2a6`) and carries:
`verdict` MODEL_OK, `nonce` b61c98ad5747, `binary_sha256` `b0a4becf…1b4c`, 16 `checks` all passed and
evaluated, `port` 58921, `elapsed_s` 1.35, `teardown` returncode 0 / `port_closed` true /
`sigkill_needed` false. Pin file at `e0b5b1ea` = `da0948f76b09375cc5823cfe71c0383fe52a4280a495c3678be2a0b47405f66e`.

## 3. The row's own gate (census + validate, run on a scratch mirror)

`bash scripts/sources-census.sh` (fleet root, read-only) over a `/fast/scratch` mirror whose `corpus/`
is this lane's `corpus/` with the candidate row inserted after S518:

| check | command | output | exit |
|---|---|---|---|
| baseline | `census --file <lane>/corpus/SOURCES.md` | `FLEET rows 259`, tier.A 245, status.mined 234 | 0 |
| with row | `census --file <mirror>/corpus/SOURCES.md` | `FLEET rows 260`, tier.A 246, status.mined 235 | 0 |
| with row | `validate --file <mirror>/corpus/SOURCES.md --today 2026-10-27` | `file ok`, no `E`-code mentioning S523 | 0 |

Exactly one row and one tier-A mined row were added, so the row parses as intended; the pre-existing
W04 duplicate-URL warnings and the S481 `W01` are unchanged by it.

Falsification of that gate (same mirror, mutated rows; each mutation is caught and names S523):

| mutation | observed |
|---|---|
| tier `A` → `Z` | `file E06 S523 tier=Z` |
| used-by → `tools/does-not-exist.py` | `file E11 S523 missing used-by tools/does-not-exist.py` |
| drop the `recheck` cell (11 → 10 cells) | `file E01 S523 fields=10` |

## 4. The row's `used-by` citation, exercised

The row cites `tools/round60-c1-counter.py` because that counter is the independent verifier of this
tool and receipt. Run at the receipt's tip:

```
python3 tools/round60-c1-counter.py --repo <lane> --tip 8b9f3060966c22bede3094d748974caf041b4c33 --work <scratch>/c1work
```

observed (exit 0, 2 s wall), exactly the freeze's expected line:

```
tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True
```

So the cited consumer exists, runs at that tip and accepts a fresh-nonce run; the citation is not
merely a path that happens to exist.

## 5. Integration notes (constraints the L1 inherits)

- Placement: append as the last Registry row (after S522), keeping ascending id order; the row must
  stay above the blank lines that precede `## Paths`, or validate raises E12.
- `used-by` cites only `tools/round60-c1-counter.py`. `validate`'s E11 resolves every used-by path on
  disk, and `corpus/knowledge/ollama-live-lifecycle.md` (the K01 draft) does not exist yet; append it
  to this cell once that file lands (the nonexistent-path mutation above is the exact failure mode).
- Observed, not caused here: `python3 tools/gate-registry-check.py --repo <lane> --rev 8b9f3060…`
  exits 1 with `registered 54 unregistered 12 defective 0`, and the two new instruments
  `tools/round60-c1-counter.py` and `tools/round60-c2-counter.py` are among the 12. At base
  (`ec3b0d58`) the same gate exits 1 with `unregistered 10`; the freeze commit added two unregistered
  instruments and no SKILL.md rows. `tools/kama-ollama-live.py` is outside that gate's population
  (`tools/round<N>-*.py` / `count-*.py`), so it is not a registration defect, but SKILL.md currently
  mentions it zero times.

## 6. Limits (stated before data)

One run, one host, one fixture GGUF, one loopback port; CPU only (the tool sets CUDA, HIP and Vulkan
visible-device variables to -1 in the child environment). The re-run establishes that the pinned
binary can be started, import the pinned GGUF under a nonce, serve the captured surfaces and be torn
down at this tip — nothing about registered-consumer health, model quality, other Ollama versions,
GPU placement or timing as a benchmark. `1.63 s` is one wall-clock observation, not a performance
claim. The committed receipt's bytes were compared by sha256, not re-derived from the scratch dir of
another seat.
