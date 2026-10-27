# F13C1GpuPin — w2 falsification of the C1 GPU pin (round 60)

Seat question: does the tool's device env (CUDA/HIP/Vulkan `-1`) isolate GPU reliably,
and is GPU enumeration distinguishable from GPU execution?

## Verdict
Env isolation **held** on this host, verified live at the process level; two evidence-quality
gaps found (receipt carries no env/device attestation; the committed receipt-run's own serve
log is gone). No counter-example found where the tool's env let a GPU device execute.

## Frozen statement attacked
freeze.txt C1 limits: "one lane-owned child on one loopback port for the length of a run,
CPU only (CUDA/HIP/Vulkan device variables are set to -1 by the tool); not ... GPU placement."
Tool code: tools/kama-ollama-live.py:186-189 (`child_env`) sets exactly
`CUDA_VISIBLE_DEVICES=-1`, `HIP_VISIBLE_DEVICES=-1`, `GGML_VK_VISIBLE_DEVICES=-1` plus
PATH/HOME/OLLAMA_HOST/OLLAMA_MODELS/OLLAMA_NO_CLOUD/OLLAMA_NOPRUNE (lines 181-190).

## Host baseline (this machine can't pass vacuously)
- `nvidia-smi`: NVIDIA GeForce RTX 5070 present; devices `/dev/nvidia0`, `/dev/nvidiactl`,
  `/dev/nvidia-uvm*`, `/dev/kfd` (AMD ROCm), `/dev/dri/card0+card1`. All three backends
  (CUDA/HIP/Vulkan) have real hardware, so `-1` is load-bearing, not vacuous.
- Pre-existing compute app: pid 1806 `/usr/bin/walker` 95 MiB (unrelated; used as sentinel).

## Leg held — exact tool env, my own PID-owned v0.40.11 (port 33265, pid 3253412)
- `/proc/3253412/environ` and `/proc/3253500/environ` (llama-server child): all three vars
  `-1` (runner inherits; `held-serve-proc-environ.txt`, `held-llama-proc-environ.txt`).
- llama-server fd table: **zero** handles under `/dev/nvidia*`, `/dev/dri`, `/dev/kfd`.
- `nvidia-smi --query-compute-apps` while model loaded and generating: no llama-server row.
- `/api/ps` after generation: `size_vram: 0`, `size 6312427` (identical to committed
  receipt `.ufo/waves/round-60/live/receipt.json` ps-after: `size_vram":0`, size 6312427).
- serve.log: `discovering available GPUs...` → `user overrode visible devices` ×3 →
  `inference compute id=cpu library=cpu` → `total_vram="0 B"`; generate `done=true,
  eval_count=4` — execution happened on CPU while enumeration lines still printed.

## Legs cudaonly / nocvd — negative controls (enumeration vs execution separated)
- cudaonly (drop `CUDA_VISIBLE_DEVICES` only; port 59367): main server logs
  `inference compute id=0 ... library=CUDA ... "NVIDIA GeForce RTX 5070" total="11.6 GiB"`;
  ollama **injects** `CUDA_VISIBLE_DEVICES=0` into the runner environ
  (`cudaonly-llama-proc-environ.txt`) — runner device env is parent-set, so the `-1`s gate
  at discovery, and the runner opens 20 `/dev/nvidia*` fds; `nvidia-smi`: llama-server pid
  3253740, 264 MiB; `/api/ps` `size_vram: 40768634`; `offloaded 6/6 layers to GPU`.
  HIP=-1 and VK=-1 present but did not block CUDA: each var gates only its own backend.
- nocvd (drop all three; port 33131): same full GPU execution (264 MiB, size_vram>0).
- Therefore the held leg's CPU result is caused by the three `-1`s, not by absent hardware.
- Enumeration ("discovering available GPUs...") appears in EVERY leg including held;
  execution truth lives in: `inference compute id=`, `size_vram`, runner `/dev/nvidia*` fds,
  and nvidia-smi compute-app registration. Log enumeration lines alone would be weak evidence.

## Leg A — honest tool reproduction (my own run)
`tools/kama-ollama-live.py --work <scratch>/live-a --out receipt-a.json`: exit 0,
`MODEL_OK`, 16/16 checks, nonce `a17f164edf2a`, port 38315; serve.log: 3 override
warnings, `inference compute id=cpu library=cpu`, `total_vram="0 B"`; ps-after capture
`size_vram:0` (`receipt-a.json`). Reproduces the committed receipt's CPU fingerprint.

## Gaps (attack findings, no repair performed)
- G1 (observability): the receipt schema has no env/device field and
  `tools/round60-c1-counter.py` never inspects CUDA/HIP/VK, environ, or size_vram
  (grep: zero device-related lines). CPU-only is asserted by documentation only; the
  acceptance path cannot distinguish a CPU run from a GPU run. Incidental CPU evidence
  exists in the committed ps-after capture (`size_vram:0`) but no instrument reads it as such.
- G2 (non-reinspectable committed run): the committed receipt's `teardown.log_path`
  `/fast/scratch/hyaku/kama-r60/live1/serve.log` no longer exists; the committed run's own
  enumeration/compute lines are not re-inspectable — CPU-only for THAT receipt rests on the
  ps-after `size_vram:0` fingerprint plus W1 A08's independent held-run observation, now
  reproduced here (Leg A).
- G3 (forward-compat, residual): env is the only gate — no `--cpu`-style flag; server
  config env map shows other device knobs exist (`OLLAMA_IGPU_ENABLE`,
  `GPU_DEVICE_ORDINAL`, `HSA_OVERRIDE_GFX_VERSION`, all empty). A backend honoring a
  different variable would bypass all three `-1`s. Not observed on v0.40.11 on this host.

## Hygiene
No lane source edits; scratch `/fast/scratch/hyaku/kama-r60/F13C1GpuPin` (TMPDIR inside,
removed after artifact copy); three lane-owned servers on free ports 33265/59367/33131 plus
tool's 38315, each SIGTERM'd, ports verified closed, no SIGKILL needed; no stray ollama or
llama-server processes; no installs; no git/jj commands; disk-guard status green before runs
(591.9G free, 27% used).
