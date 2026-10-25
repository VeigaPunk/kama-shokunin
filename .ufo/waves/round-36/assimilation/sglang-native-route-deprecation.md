# Published native route name is not the engine route

source: S328 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx — line 6 and route-list line 9 — tag v0.5.22
source: S329 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — lines 790-791 — tag v0.5.22
verified-at: 2026-10-24
recheck: 90d

### What the published page still says

The v0.5.22 native-API page introduces the native server APIs in one sentence: "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." The route list on line 9 still names `/get_model_info`. A count of the string `/model_info` on that file is 0. The worked example still requests `http://localhost:{port}/get_model_info`.

S006 and the runtime-health matrix record that published route. S006 teaches that model metadata lives on `/get_model_info`. The matrix identity cell lists `GET /get_model_info`. Neither record says the engine has marked that route deprecated. This entry does not rewrite them.

### What the same tag's server source says

`http_server.py` at tag v0.5.22 still registers `/get_model_info`, then warns: "Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead." The handler returns the result of `model_info()`.

A client that treats the published route list as the current engine contract will call a route the server itself tells callers to leave. The page and the warning are both true of this tag. They are not the same fact.

### What this entry does not establish

It does not show that `/get_model_info` is already unreachable at v0.5.22. The handler is still registered. It does not sample any server on this host. It does not say when the published page will catch up. Other staged readings of the same `http_server.py` URL — readiness, model-card fields, the OpenAI-compatible list — are not adopted here, because a second row for that URL would duplicate it.
