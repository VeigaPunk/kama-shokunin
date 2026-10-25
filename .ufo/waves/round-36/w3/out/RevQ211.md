# RevQ211 — quarantine row S211 token check

## Verdict
**ABSENT** — URL reachable (HTTP 200); the token `still-live` does not occur anywhere in the fetched page text (case-insensitive, 0 hits; 0 hits for `still live` / `still_live` variants too).

## Measured (single fetch, 2026-10-24)
- URL fetched (once, exactly as given): `https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md`
- HTTP status: **200** (no redirect; final URL identical to request URL)
- Body: 494,123 bytes, `text/html; charset=utf-8` (GitHub blob page)
- Page identity: `<title>llm/chapters/06-推理引擎.md at 35b83cee12ae26f10b58d4163298352384503907 · AaronYang238/llm · GitHub</title>`; the full commit SHA appears 40× in the served HTML → genuine blob page for that commit, not a soft-404/login interstitial.
- Token search over the full saved body (`still[-_ ]?live`, `-i`): **0 occurrences**; exact `still-live` `-i`: **0 occurrences**.
- Scratch copy of the fetched page: `.ufo/waves/round-36/w3/out/RevQ211/page.html` (seat dir only). No row appended; no corpus file touched.

## Inference (not measured)
GitHub blob HTML embeds the file content (raw + rendered) in the served page payload, so 0 hits over the full 494 KB body covers both chrome and embedded file text for this render.

## Residual risk / verification gaps
- I deliberately did not fetch `raw.githubusercontent.com` (task: fetch the URL once; second endpoint was not fetched). Content seen is what github.com served this client at this time; GitHub can vary served bytes per session/region, so this is a point-in-time measurement.
- Verdict "absent" is scoped to the page text read (full served HTML body); it is not a claim about the repo's history or other paths.
