# RevS328 — falsify attempt on drafted row S328 (native_api.mdx @ tag v0.5.22)

Role: wave-2 falsifier, leaf. Axis judged: coverage (C2). Surface: the S328 URL only
(https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx).
S329 (http_server.py lines 790-791) is out of my assigned surface and was not checked here.
No source row appended, no lane corpus file edited; the only writes are this report and
native_api.mdx (verbatim fetch copy) under .ufo/waves/round-36/w2/out/RevS328/.

## 1. Measurement (independent re-fetch, not taken from wave 1)

- URL: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx
- HTTP status: 200 (curl -w %{http_code}); response body saved verbatim, 17359 bytes, 467 lines,
  sha256 209087c3d30dc25cbcdb3b8a31b0453089d83e0fdfa39d317ab54646787e11eb
- Access date: 2026-10-24 (host local time 2026-10-24 22:36 -03; UTC host clock had already
  rolled to 2026-10-25T01:36Z at fetch time — same fetch, both timestamps recorded)

Counts (grep -o on the saved body; non-overlapping substring counts):
- `get_model_info`: **2** occurrences — line 9 (`- \`/get_model_info\``) and line 71
  (`url = f"http://localhost:{port}/get_model_info"`). Both hits are inside the full
  `/get_model_info` route string (`/get_model_info` also counts 2); there is no bare token.
- `/model_info`: **0** occurrences (grep -nF finds no line). Correct that `/get_model_info`
  does not contain `/model_info` as a substring (the char after `/` is `g`), so the 0 is a
  true zero, not a masking artifact.

Route-list line: the native-route list begins at line 8 (`- \`/generate\``) and the
`/get_model_info` entry is **line 9**: `- \`/get_model_info\``.

Quote (line 6, first sentence, 15 words): "Apart from the OpenAI compatible APIs, the SGLang
Runtime also provides its native server APIs."

Cross-check vs the L1's stated facts: HTTP 200 — match; get_model_info × 2 — match;
/model_info × 0 — match; line 9 route-list entry — match.

## 2. Comparison against drafted S328 (append-block.md line 1)

| S328 cell | Drafted content | Measured | Verdict |
|---|---|---|---|
| URL | raw native_api.mdx at tag v0.5.22 | fetches HTTP 200 today | match |
| Scope (col 5) | "published SGLang native route list at tag v0.5.22; not a live local server" | page is the published docs route list (lines 8-24); no server sampled | match |
| Anchor (col 6) | "line 6 and route-list line 9" | line 6 = the intro sentence quoted above; line 9 = `- \`/get_model_info\`` in the route list | match |
| Scope cell (col 7) | "page still introduces native APIs and lists /get_model_info; /model_info occurs zero times" | intro on line 6; /get_model_info listed at line 9; /model_info count 0 | match |
| Date / recheck | 2026-10-24 / 90d | re-fetched 2026-10-24, content identical in all checked facts | consistent |

The drafted knowledge entry (sglang-native-route-deprecation.md) makes the same mdx claims —
route list line 9 names /get_model_info, /model_info count 0, worked example still requests
http://localhost:{port}/get_model_info (line 71) — all independently confirmed.

## 3. Divergences found

None on the assigned surface. The falsify attempt failed to break S328: every clause of the
drafted anchor and scope cell reproduces under independent measurement. Minor precision notes,
not defects: (a) "route-list line 9" is accurate — line 9 is the /get_model_info item; the
list itself starts one line earlier at line 8; (b) the knowledge entry's line-6 quote matches
the file verbatim; (c) the /model_info = 0 claim is a genuine zero, not a substring shadow of
/get_model_info. C2's S-id/absent-at-base mechanics were not re-audited here (out of seat);
this report only certifies the committed-byte facts S328 cites on the docs URL.

## 4. Confidence

High. Counts and line numbers were taken with grep -o / grep -nF on a byte-exact saved copy
whose sha256 and size are recorded above, at two independent layers (FetchURL body + curl
download), and both agree with the drafted row and with the L1's stated curl facts.
