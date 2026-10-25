# KamaExecGguf — source rows for `corpus/SOURCES.md` (round 10, 2026-10-19)

Pre-assigned ids for this seat: S005, S008, S013, S014, S015. All five were
re-opened this session over the web; each Gate block carries its URL, access
date, verbatim quote, location and revision pin. All rows are `mined` by
`corpus/knowledge/gguf-runtime-compatibility-boundary.md`.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S014 | GGUF specification — https://github.com/ggml-org/ggml/blob/master/docs/gguf.md | spec | A | GGUF filename parsing and quantization-suffix meaning | §GGUF Naming Convention at commit 6af560d55df03ad92116e3c0a697779584477e85 (2026-07-09) | Naming convention is human-readable by intent and explicitly not perfectly parsable in the field | mined | 2026-10-19 | on-release | corpus/knowledge/gguf-runtime-compatibility-boundary.md |
| S015 | llama.cpp quantize README — https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md | docs | A | llama.cpp offline GGUF quantization | §Overview and §Quantize the GGUF at commit ad1b88ca0d37a2171efba1c04f1a3531c78f1b52 (2026-06-05) | Conversion to GGUF and quantization are separate offline phases; --allow-requantize warns requantizing can severely reduce quality | mined | 2026-10-19 | on-release | corpus/knowledge/gguf-runtime-compatibility-boundary.md |
| S005 | vLLM Quantization — https://docs.vllm.ai/en/stable/features/quantization/ | docs | A | vLLM quantization and GGUF load support by hardware | §Supported Hardware table; source docs/features/quantization/README.md commit d4ee7fe7a98b3012f64309e18dd425e565069a01 (2026-09-14) | GGUF row shows support on NVIDIA Volta through Hopper and AMD GPU, no support on Intel GPU, x86 CPU or Arm CPU | mined | 2026-10-19 | on-release | corpus/knowledge/gguf-runtime-compatibility-boundary.md |
| S008 | SGLang Quantization — https://docs.sglang.io/docs/advanced_features/quantization | docs | A | SGLang offline/online quantization and GGUF load support | §Quantization note and §Platform Compatibility at docs commit 50ed4c011ffb37e1c16248b99deab7d4dbdde79b (2026-07-13) | Offline and online quantization are distinct; online must not be layered on pre-quantized weights; gguf supported on NVIDIA and Ascend, not AMD | mined | 2026-10-19 | on-release | corpus/knowledge/gguf-runtime-compatibility-boundary.md |
| S013 | Ollama Importing a Model — https://docs.ollama.com/import | docs | A | Ollama GGUF import behavior | §Importing a GGUF model; page undated, live text mirrors ollama/ollama docs/import.md commit 6d02a43a75cd3364b3c230e9070f1413e60f0d02 (2025-10-28) | GGUF import consumes a prepared file and does not quantize it; shards need original filenames plus a wildcard | mined | 2026-10-19 | on-release | corpus/knowledge/gguf-runtime-compatibility-boundary.md |

## Gate — S014

- URL: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- accessed: 2026-10-19
- quote: "It is not intended to be perfectly parsable in the field due to the diversity of existing gguf filenames." (22 words)
- location: §GGUF Naming Convention, second paragraph
- revision: pinned to last file-touching commit 6af560d55df03ad92116e3c0a697779584477e85 dated 2026-07-09, via the repo's commits atom feed for docs/gguf.md; GitHub REST API was rate-limited (x-ratelimit-remaining: 0) so the atom feed supplied the SHA

## Gate — S015

- URL: https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md
- accessed: 2026-10-19
- quote: "Quantization is done in two phases: Convert the original model to GGUF format. Quantize the converted GGUF file." (18 words)
- location: §Overview, first bullet block; also opened §Quantize the GGUF and §Quantization tables
- revision: pinned to last file-touching commit ad1b88ca0d37a2171efba1c04f1a3531c78f1b52 dated 2026-06-05, via the commits atom feed for tools/quantize/README.md

## Gate — S005

- URL: https://docs.vllm.ai/en/stable/features/quantization/
- accessed: 2026-10-19
- quote: "This compatibility chart is subject to change as vLLM continues to evolve and expand its support" (15 words)
- location: note directly under the §Supported Hardware table whose GGUF row reads Volta/Hopper/Ada/Ampere/Turing and AMD GPU supported, Intel GPU, x86 CPU and Arm CPU not
- revision: page footer dates the build 2026-09-14; source file docs/features/quantization/README.md last touched at commit d4ee7fe7a98b3012f64309e18dd425e565069a01 dated 2026-09-14, via the commits atom feed

## Gate — S008

- URL: https://docs.sglang.io/docs/advanced_features/quantization
- accessed: 2026-10-19
- quote: "If you use a pre-quantized model, do not add --quantization to enable online quantization at the same time." (17 words)
- location: warning paragraph after the §Quantization intro defining offline vs online quantization; §Platform Compatibility table lists gguf Yes for NVIDIA GPUs and Ascend NPUs, No for AMD GPUs
- revision: pinned to last file-touching commit 50ed4c011ffb37e1c16248b99deab7d4dbdde79b dated 2026-07-13, via the commits atom feed for docs/advanced_features/quantization.md in sgl-project/sglang

## Gate — S013

- URL: https://docs.ollama.com/import
- accessed: 2026-10-19
- quote: "Ollama does not quantize GGUF models during import. Prepare and quantize them first with a GGUF tool" (17 words)
- location: §Importing a GGUF model, first paragraph
- revision: published page is undated (no Last-Modified; etag W/"y9xlek5liq6etl" observed); live text matches ollama/ollama docs/import.md at commit 6d02a43a75cd3364b3c230e9070f1413e60f0d02 dated 2025-10-28 per the repo's commits atom feed

## Leads (unopened)

None from this seat; all five assigned sources were opened this session.
