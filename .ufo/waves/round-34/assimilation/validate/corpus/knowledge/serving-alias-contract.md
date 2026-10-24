# Served-name and alias resolution contract across local serving stacks

source: S196 — https://docs.vllm.ai/en/v0.17.0/cli/serve/ — §Named Arguments → `--served-model-name` — quote located 2026-10-24: "The model name in the model field of a response will be the first name in this list."
source: S205 — https://docs.sglang.io/docs/developer_guide/bench_serving — §Fair embedding comparison — quote located 2026-10-24: "`--flush-cache` calls `/flush_cache` for SGLang and `/reset_prefix_cache` for vLLM after warmup."
source: S206 — https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ — §调用示例 → 模型名称获取方式 — quote located 2026-10-24: "对于vLLM/SGLang，可通过模型列表接口`<EAS_ENDPOINT>/v1/models`获取。"
source: S209 — https://www.alibabacloud.com/help/ja/ack/cloud-native-ai-suite/user-guide/deploy-standalone-llm-inference-services — §ステップ 3：推論サービスを検証する — quote located 2026-10-24: `curl http://localhost:8000/v1/chat/completions ... -d '{"model": "/models/Qwen3-32B", "messages": ...}'`
verified-at: 2026-10-24
recheck: 90d — re-run the four row recheck commands (S196 `first name in this list` count=1; S205 `reset_prefix_cache` count=2; S206 `v1/models` count=4; S209 `chat/completions` count=1) (re-ran 2026-10-24)

### The rule

A local serving stack's *served name* is a string the client sends in the `model`
field and the server echoes back. It is not the checkpoint path, and it is not a
proof that a particular set of weights is resident.

### Four documented shapes, in four literatures

- **vLLM (Western, upstream project).** `--served-model-name` may be given more
  than once. The server answers to any of the accepted names, but "the model name
  in the model field of a response will be the first name in this list", and the
  same first name becomes the Prometheus `model_name` tag value. If the flag is
  absent, the served name defaults to the `--model` argument. Consequence for
  kama: with multiple aliases, the `model` field and the metrics tag are the
  *first* alias, not the one the client sent and not necessarily the checkpoint
  path. An alias reconciliation that compares the client's requested name against
  the response `model` field will report a mismatch for every non-first alias.
- **Cross-engine cache-management endpoints (Western, upstream project).** The two
  engines do not even name their cache-reset route the same way: `--flush-cache`
  calls `/flush_cache` for SGLang and `/reset_prefix_cache` for vLLM, and vLLM's
  route requires the server to have been started with `VLLM_SERVER_DEV_MODE=1`.
  Consequence for kama: a probe script that assumes a single canonical
  "reset the cache" route is engine-specific and will 404 on the other engine.
- **Chinese vendor contract (Alibaba Cloud PAI-EAS, zh).** For a vLLM or SGLang
  deployment, the `model` value to send is not chosen by the client at all: it is
  read from the served endpoint's own model list, `<EAS_ENDPOINT>/v1/models`. The
  Chinese documentation states this as the way to obtain the model name. This is
  the same discipline the lane already applies locally — ask the server what it
  serves — expressed by the vendor that operates the endpoint.
- **Japanese vendor contract (Alibaba Cloud ACK, ja).** The verification request in
  the Japanese deployment guide sends `"model": "/models/Qwen3-32B"` — the served
  name is the mounted model *path*. Consequence for kama: a path-shaped served name
  is a legitimate served name, and a name-normalisation rule that assumes
  basename-style names would mangle it.

### What this entry does not establish

None of these rows was observed against a running server in this round; they are
documentation-level contracts. They also do not license a claim that any particular
engine currently on this host resolves a given alias, and they do not cover Ollama's
`/api/tags` behaviour, which the lane already holds from its own observation.
