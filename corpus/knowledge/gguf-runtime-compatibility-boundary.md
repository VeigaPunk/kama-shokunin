# GGUF filename and quantization suffix are not a support certificate
source: S014 https://github.com/ggml-org/ggml/blob/master/docs/gguf.md §GGUF Naming Convention; S015 https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md §Overview; S005 https://docs.vllm.ai/en/stable/features/quantization/ §Supported Hardware; S008 https://docs.sglang.io/docs/advanced_features/quantization §Platform Compatibility; S013 https://docs.ollama.com/import §Importing a GGUF model
verified-at: 2026-10-19 — vendor/spec docs opened; no local runtime contacted
recheck: on-release — recheck the GGUF naming-convention note, both runtime support tables (S005 GGUF row, S008 gguf row), the S008 online-on-pre-quantized warning, and the S013 import paragraph

## Claim

A GGUF filename or quantization suffix (e.g. `Q4_K_M`, `IQ2_XXS`) is neither a
canonical model-identity parser nor a cross-runtime support certificate: the
spec's own naming convention "is not intended to be perfectly parsable in the
field" (S014), and whether a GGUF file loads, and how it was produced, is a
per-engine, per-hardware fact documented differently by vLLM, SGLang, Ollama
and llama.cpp (S005, S008, S013, S015).

## Crosswalk

| Engine | Documented revision | GGUF load support as documented | Quantization path | Caveat | S-id |
|---|---|---|---|---|---|
| llama.cpp | `tools/quantize/README.md` at commit `ad1b88ca` (2026-06-05) | Native format; GGUF is the llama.cpp serving file format | Offline: `convert_hf_to_gguf.py` then `llama-quantize`; the README states "Quantization is done in two phases" | `--allow-requantize` warns it "can severely reduce quality compared to quantizing from 16bit or 32bit"; example speed/size tables are model- and setup-specific | S015 |
| vLLM | stable docs; source `docs/features/quantization/README.md` at commit `d4ee7fe7` (2026-09-14) | §Supported Hardware GGUF row: supported on NVIDIA Volta–Hopper and AMD GPU; not supported on Intel GPU, x86 CPU or Arm CPU | Mostly offline via pre-quantized checkpoints (AutoAWQ, GPTQModel, llm-compressor, bitsandbytes); a separate online-quantization page exists | The page itself warns "This compatibility chart is subject to change as vLLM continues to evolve" | S005 |
| SGLang | `docs/advanced_features/quantization.md` at commit `50ed4c01` (2026-07-13) | §Platform Compatibility `gguf` row: yes on NVIDIA GPUs and Ascend NPUs, no on AMD GPUs | Offline loads pre-quantized weights; online computes scaling at runtime; docs recommend offline over online | "If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time" | S008 |
| Ollama | undated page; text mirrors `ollama/ollama` `docs/import.md` at commit `6d02a43a` (2025-10-28) | Imports single-file or sharded GGUF via `Modelfile` `FROM`; shards keep original filenames under a wildcard | Import only: "Ollama does not quantize GGUF models during import"; quantize beforehand with an external GGUF tool | Import consumes the file as prepared; the suffix on disk is not re-derived or verified by Ollama | S013 |

## What this does not establish

- That any local runtime exists, loads GGUF, or serves any model: no endpoint,
  process or file was contacted; these are documentation facts only.
- That a named quantization is good or bad: ranking quants or judging quality
  is kengaku's province (model eval); kama records compatibility facts only.
- That every `.gguf` filename follows the convention: S014 supplies a stricter
  validation regex and states the convention is not perfectly parsable.
- That a GGUF file accepted by one engine loads on another: support differs
  per hardware and backend in both published tables.

## kama use

- `/v1/models` may return a path-shaped GGUF id (e.g. `…-UD-IQ2_XXS.gguf`);
  record it verbatim. The served-id normalization rule in `SKILL.md` stays
  unchanged: basename, strip a trailing `.gguf`, compare case-sensitively —
  never parse quant, size or version components out of the name.
- A quant suffix in an expected or served id is a string to match, not a
  provenance claim; the README confirms suffixes are by convention only.
- For "can engine X load this file" questions, cite the engine plus its
  documented revision and hardware row, not the filename.
- A filename that violates the convention is an observation, not a verdict.

## QUALITY clearance

- KQ1: no current endpoint claim is made; no probe was run and none was needed.
- KQ2: no pin provenance is touched; served-id normalization is preserved verbatim.
- KQ3: every source is re-anchored to a dated revision (commit or dated page) opened 2026-10-19.
- KQ4: freshness scope is explicit — vendor/spec docs opened; no local runtime contacted.
- KQ5: documentation-only admission; no service, config or import action performed.
- KQ6: every engine statement names engine + documented revision (commit, release or dated page) + section and cites an opened `SOURCES.md` row (tier A for its scope; no C-tier row supports this entry); never asserted as local runtime fact.
- KQ7–KQ10: not a correction entry (KQ7); no privilege-bounded verdict (KQ8); no negative claim — absences are stated as 'not documented in the opened page', not as non-existence (KQ9); no census or probe run by the entry's author (KQ10).

## Cited sources

- S014 GGUF specification, §GGUF Naming Convention — https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- S015 llama.cpp quantize README, §Overview / §Quantize the GGUF — https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md
- S005 vLLM Quantization, §Supported Hardware — https://docs.vllm.ai/en/stable/features/quantization/
- S008 SGLang Quantization, §Quantization and §Platform Compatibility — https://docs.sglang.io/docs/advanced_features/quantization
- S013 Ollama Importing a Model, §Importing a GGUF model — https://docs.ollama.com/import
