
# Where the Chinese and Japanese literatures decide the same endpoint questions

source: S341 — https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ — §调用示例 → 模型名称获取方式 — Alibaba Cloud 文档中心 (zh), retrieved 2026-10-23
source: S342 — https://help.aliyun.com/zh/model-studio/what-is-model-studio — §什么是阿里云百炼 — Alibaba Cloud 文档中心 (zh), retrieved 2026-10-23
source: S343 — https://www.alibabacloud.com/help/ja/arms/application-monitoring/use-cases/observe-the-vllm-and-sglang-inference-engine/ — §ステップ 2 — Alibaba Cloud ドキュメントセンター (ja), retrieved 2026-10-23
source: S344 — https://www.alibabacloud.com/help/ja/ack/cloud-native-ai-suite/user-guide/deploy-standalone-llm-inference-services — §ステップ 3 — Alibaba Cloud ドキュメントセンター (ja), retrieved 2026-10-23
source: S345 — https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide — §SGLang の起動 — retrieved 2026-10-23
source: S346 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md — §6.4 — commit 35b83cee12ae26f10b58d4163298352384503907 (2026-06-16)
verified-at: 2026-10-23
recheck: 90d — re-run the row recheck commands for S341, S342, S343, S344, S345 and S346 in SOURCES-PROPOSED.md (ran 2026-10-23)
ground: frontier item "the same sub-questions decided in the Chinese and Japanese literatures" — the lane's registry held **zero** Chinese- and zero Japanese-language rows across all 179 entries, so this is the first Eastern spine for the lane.

### The finding

The Eastern literature is not a translation of the Western one. The same endpoint
questions are decided in three different venues with three different authorities:

- **Western** — the upstream project's own versioned documentation (vLLM docs at
  pinned versions, SGLang docs pinned to repository commits, the arXiv paper).
  Authority: the engine's maintainers.
- **Chinese** — a cloud vendor's own help centre (Alibaba Cloud 文档中心, `zh`
  path), which states the *operator's* contract: the model name comes from the
  served endpoint's `/v1/models`; the OpenAI-compatible contract is a three-part
  adjustment of API key, `base_url` and model name; and "不同地域的base_url不通用" —
  base URLs are region-scoped and not interchangeable. A Chinese reverse-engineering
  write-up (S346) supplies the file-level map the upstream docs do not present.
- **Japanese** — a cloud vendor's Japanese help centre and a company's Japanese
  engineering guide. The ARMS page distinguishes `vLLM-v0`, `vLLM-v1` and `SGLang`
  at the *launch-command* level, which is a finer discrimination than the Western
  docs make in the same place, and it records the SGLang server argv. The ACK
  page shows the served model name being the mounted model path.

### Why this matters for the lane's own method

A translated mirror of an upstream English document would add nothing the Western
row does not already carry. These rows add three things the Western spine cannot:
a **region-scoped base-URL rule** (Chinese), a **launch-command-level vLLM-v0 vs
vLLM-v1 discriminator** (Japanese), and a **path-shaped served model name in an
official deployment procedure** (Japanese). Those are facts about operating
endpoints, which is precisely the lane's subject.

### Channel limitation found while searching

The provider's web index answered the Chinese-language query
`vLLM SGLang 部署 健康检查 探针 /health 就绪 文档` with **English-language results
only**. The Chinese-native pages in this round were reached by re-phrasing the
query around a Chinese vendor's own product surface and by direct fetches of
known Chinese URLs. The Japanese query did surface Japanese-native pages
immediately. Future rounds should expect Chinese-language discovery to need
vendor-anchored phrasing, and should record that cost rather than treat a quiet
English result as an absence of Chinese material.

### What this entry does not establish

Every Eastern row is a vendor's documentation for *that vendor's* service. They
are authoritative for their own contract and are tier B for everything else: they
do not describe a local server's behaviour, and they do not outrank the upstream
project on engine internals.
