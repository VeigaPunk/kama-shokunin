# F03C1ModelSwap — C1 A09 H2 counter attack

## Scope and method
Reproduced the W1 A09 H2 post-source-hash swap in a scratch copy of `A09FalseGreenReading/repro/p2.py` (lane source remained read-only). The copy redirected `gguf` to a same-fixture file with `A09` appended after the pinned digest check. Ran against the pinned Ollama v0.40.11 binary, with `TMPDIR=/fast/scratch/hyaku/kama-r60/F03C1ModelSwap/tmp`, scratch run/model store under `/fast/scratch/hyaku/kama-r60/F03C1ModelSwap/run`, and nonce `f03c1model01`.

Exact run:
`A09_WRONG_GGUF=/fast/scratch/hyaku/kama-r60/F03C1ModelSwap/mymod.gguf TMPDIR=/fast/scratch/hyaku/kama-r60/F03C1ModelSwap/tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/A09FalseGreenReading/repro/p2.py --work /fast/scratch/hyaku/kama-r60/F03C1ModelSwap/run --nonce f03c1model01 --out /fast/scratch/hyaku/kama-r60/F03C1ModelSwap/receipt.json`
Observed: tool exit 0; receipt verdict `MODEL_OK`; pinned source SHA-256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; swapped source SHA-256 `9c5241b4ff65a63eca4e8cf6c530a44f14fd2819c576c1a69298ef1158efbc53`. Imported manifest's model layer is `sha256:9c5241b4ff65a63eca4e8cf6c530a44f14fd2819c576c1a69298ef1158efbc53` (`from: mymod.gguf`); imported manifest digest reported by `/api/tags` is `584bcf43c49cab3c02e55c786fa89357d0f2c472de333e4eba59631ecff25dd5`. Thus tool-level green does not establish imported identity.

## Counter result
Invoked the frozen `round60-c1-counter.py::verify` on the reproduced receipt and its unchanged work directory (read-only). Exact result: `verify_bad=["manifest-layer", "blob-missing"]`. The wrong model blob exists under its content digest; the required `models/blobs/sha256-270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` is absent. The verifier separately requires the nonce manifest to mention the frozen model digest and hashes the frozen-digest blob against that pin. This falsifier did not make the counter accept the swapped import.

## Verdict / limitations
No actionable counter false-accept found for this model-swap case. Reproduction matches W1's deterministic post-check reassignment model; it did not instrument an unsynchronized same-inode replacement race against the unmodified executable. No lane files changed and no tools installed/updated. Disk guard had been running; `/fast` had 592G free before the probe. Ollama child teardown recorded returncode 0, `sigkill_needed=false`, `port_closed=true`. Scratch is removed after recording this report.