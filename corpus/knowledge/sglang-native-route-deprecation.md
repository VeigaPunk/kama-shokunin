# Published native route name is not the engine's current route

source: S328 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx — line 6 and route-list line 9 — tag v0.5.22
source: S329 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — lines 786, 790–791 and 796 — tag v0.5.22
verified-at: 2026-10-24
recheck: 90d

## What the published page still says

At tag v0.5.22 the SGLang native-API page opens with one sentence: "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." Its route list, on line 9, still names `/get_model_info`. The string `/model_info` does not occur anywhere in that file — the count is zero. The worked example on line 71 still asks for `http://localhost:{port}/get_model_info`.

A reader who takes that page as the contract for the release reads one model-info route out of it. The page does not say that route is on its way out.

## What the same tag's server source says

In `http_server.py` at the same tag, the route `/get_model_info` is still registered, at line 786. Its handler warns the caller: "Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead." The replacement route `/model_info` is registered at line 796, and the old handler still returns the result of `model_info()`.

Both statements are true of this tag. A published route list is a statement about the documentation; a deprecation warning inside the handler is a statement about the engine. They are not the same claim, and a client that reads only the first one will call a route the server asks callers to leave.

## What this entry does not establish

It does not show that `/get_model_info` is already unreachable at v0.5.22 — the handler is still registered and still answers. It does not sample any server on this host, and it does not say when the published page catches up. It does not claim that the documentation is wrong; it records that the page and the engine disagree about the same tag, and that the engine is the one that says so out loud.

## Why this is its own ground

The lane's runtime-health surface matrix records which route answers what, and the served-model-identity entries record which id a listing returns. Neither records that a route the documentation still advertises is one the engine marks deprecated in its own response. A health or identity probe that treats the published route list as current will probe the wrong route, and a client that reads the engine's warning as an error will see a deprecation notice where a successful answer was expected. Both failure modes come from the same gap: the published name and the engine's current name are not the same fact.
