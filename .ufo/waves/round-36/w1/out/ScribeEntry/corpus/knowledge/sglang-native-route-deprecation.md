source: S328 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx — native route list and Get Model Info example — opened 2026-10-24; S329 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — `/get_model_info` deprecation warning — opened 2026-10-24
verified-at: 2026-10-24 — both raw tag URLs re-opened, HTTP 200, final URL equal to the requested URL; no local SGLang process contacted
recheck: 90d — re-fetch the two raw tag URLs below and confirm the docs page still has zero occurrences of `/model_info` while the engine warning still names that path as the replacement

# A published SGLang native route name is not the engine's current route

At tag v0.5.22 the native-API page still teaches `/get_model_info` as one of the runtime's native server routes. The engine file at that same tag still registers the path, but the warning on that handler says the path is deprecated and names `/model_info` as the path to use. The name on the published page is not the name the engine asks callers to use.

## What the docs page publishes

S328 is the raw file `docs/docs/basic_usage/native_api.mdx` at tag v0.5.22, 17359 bytes, sha256 `209087c3d30dc25cbcdb3b8a31b0453089d83e0fdfa39d317ab54646787e11eb`. The first sentence of line 6 says the runtime provides native server APIs in addition to the OpenAI-compatible ones. The route list that follows includes `` `/get_model_info` `` at line 9. The Get Model Info example requests that same path at line 71. The string `/model_info` does not occur on the page. The token `get_model_info` occurs twice, both times as that old path. The page's only use of "deprecated" is a note that `get_server_info` folds in older server-info helpers; the server-info example on the same page already calls `/server_info`. That note is not a deprecation of the model-info route.

## What the engine file says about this route

S329 is the deprecation sentence in `python/sglang/srt/entrypoints/http_server.py` at the same tag. The file is 110718 bytes, sha256 `a89d20bb2fa8a86c511ab4d9d054f74d707423ab220f733ff25e62fcc0e49979`. A column-zero `@app.get("/get_model_info")` is at line 786. Its handler logs a warning. The two adjacent string literals on lines 790-791 join, with the space already present at the end of line 790, to: Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead. The handler's next statement returns the result of `model_info()`, and a column-zero `@app.get("/model_info")` is at line 796. At this tag the old path still answers by calling the new handler. The warning is a log call, not an HTTP error status, and the sentence places removal in a future version rather than in this file.

## What this does not establish

No process on this host was contacted, so this entry does not say that either route is listening, refused, or returning a body here. The docs page points its "full list" link at the `main` branch of the same engine path; that URL was not opened, and this entry does not say what `main` contains. The same engine file also warns that `/get_server_info` is deprecated in favour of `/server_info`. That sentence is a different aspect of the file and is not S329. Differences between the fields the docs example expects and the fields `model_info()` builds are not admitted here. This note does not rewrite the health-surface matrix, and it does not authorize a generation request or a live probe of either route.

## Cited sources

S328, opened 2026-10-24: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx — route list line 9 and Get Model Info example line 71.
S329, opened 2026-10-24: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — deprecation warning, lines 790-791.
