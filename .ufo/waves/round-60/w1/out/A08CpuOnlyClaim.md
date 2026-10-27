# A08CpuOnlyClaim — CPU-only falsification

Axis: operability. Attacked clause: frozen C1 limit says the child run is “CPU only (CUDA/HIP/Vulkan device variables are set to -1 by the tool).”

## Result

For the pinned Ollama v0.40.11 live-tool run and a separate lane-owned held generation on this host, model inference was CPU-only; no Ollama/llama-server compute process appeared on the NVIDIA GPU. This supports CPU-only **for these invocations**, not a general host-level absence of GPU use. The host has an NVIDIA GeForce RTX 5070 and AMD Radeon 610M; unrelated graphical/compute-capable applications were visible on NVIDIA. Ollama's own log reports only `id=cpu library=cpu`. The requested stop variables are present: `CUDA_VISIBLE_DEVICES=-1`, `HIP_VISIBLE_DEVICES=-1`, `GGML_VK_VISIBLE_DEVICES=-1`. The log specifically warns that CUDA visibility was overridden.

## Evidence

Disk guard: `/home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status` exited 0; reported `/fast/scratch/hyaku` 27% used, 593.7G free.

Pinned live-tool invocation (exit 1):

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --work /fast/scratch/hyaku/kama-r60/A08CpuOnlyClaim/live-work --nonce a08cpuonly60 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-60/w1/out/A08CpuOnlyClaim/receipt.json
```

It completed model creation/generation and teardown, but final receipt writing failed because the output directory had not yet been created: `FileNotFoundError: .../out/A08CpuOnlyClaim/receipt.json`; thus the process exit was 1, not a green tool result. The work dir/log is retained in scratch; copied relevant log to `live-serve.log`. Key lines from that log:

```text
level=INFO source=runner.go:60 msg="discovering available GPUs..."
level=WARN source=runner.go:722 msg="user overrode visible devices" CUDA_VISIBLE_DEVICES=-1
level=INFO source=types.go:50 msg="inference compute" id=cpu library=cpu compute="" name=cpu description=cpu ...
level=INFO source=sched.go:1183 msg="disabling mmap for llama-server load by default" ... reason=cpu
load_backend: loaded CPU backend ... libggml-cpu-zen4.so
cmn  common_param:   - CPU     : AMD Ryzen 9 9950X 16-Core Processor ...
```

The log's server config also included all three `*_VISIBLE_DEVICES=-1` values. No GPU inference device is listed.

Held-run command behavior: started a separate Ollama server with the assignment's isolated HOME/model store and all three visibility variables set to `-1`, imported `stories260K.gguf` as `a08held`, then POSTed `/api/generate` with `num_predict:4` while keeping that server alive. Generation returned HTTP success JSON with `"done":true` and `"eval_count":4`. The first readiness curl raced startup and failed once; subsequent create/generate succeeded. Captured server output is `held-serve.log`.

`nvidia-smi` during the held server/generation (exit 0): RTX 5070 showed 1067 MiB total used and 1% utilization. Its process table listed Hyprland, Xwayland, walker, ZCode, and alacritty/other graphics processes; no Ollama or llama-server process. `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader` (exit 0) returned only:

```text
1806, /usr/bin/walker, 95 MiB
```

This is not Ollama. Initial `nvidia-smi -L` (exit 0) confirmed the RTX 5070; `lspci` also showed AMD Radeon 610M. No host GPU settings were changed.

Artifacts: `live-serve.log`, `held-serve.log`, and `tool-run.out` accompany this report. No source files were changed and no tools were installed.

## Verification gap

The live tool did not produce its receipt because the output directory was created after that invocation. The observed server log and separate held generation still establish the placement evidence, but this is not a successful C1 lifecycle receipt. No GPU was observed executing inference under the specified environment; this does not prove unrelated processes or other env/configurations are CPU-only.