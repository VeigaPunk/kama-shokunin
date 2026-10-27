# Q01Source512 — S512 live-source verification

**Item:** Live-fetch `https://man7.org/linux/man-pages/man7/rtld-audit.7.html` and verify S512's quote, anchor and revision against the committed snapshot.
**Axis:** calibration. **Seat:** scout (advisory). **Run date:** 2026-10-27.

## Command and exit evidence

```
$ cd /fast/scratch/hyaku/kama-r56/Q01Source512
$ curl -sSL -D live.headers -o live.html -w 'http_code=%{http_code} ...' \
    --max-time 30 https://man7.org/linux/man-pages/man7/rtld-audit.7.html
http_code=200 url=https://man7.org/linux/man-pages/man7/rtld-audit.7.html size=26769   (exit 0)

$ sha256sum live.html .../sources/rtld-audit.7.html
a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153  live.html
a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153  rtld-audit.7.html
```

Response headers (receipt `out/Q01Source512/live.headers`): `HTTP/1.1 200 OK`,
`Content-Length: 26769`, `Last-Modified: Thu, 08 Oct 2026 17:39:35 GMT`,
`ETag: "6891-65d57b70ec3c0"`.

## Findings — all three registry claims verify

S512 row under audit: `corpus/SOURCES.md:265`; lesson statement `corpus/lessons/round-56.md:14`.
Committed snapshot: `.ufo/waves/round-56/sources/rtld-audit.7.html`.

| Claimed | Observed | Verdict |
|---|---|---|
| Snapshot represents the live page | Live fetch (200, 26769 bytes) is **byte-identical** to the committed snapshot: sha256 `a95aa3fb…153` for both | PASS — snapshot is exact, no drift |
| Quote: "the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries" (15 words) | Present verbatim in the live page after tag-strip/entity-decode/whitespace-collapse: `To employ the auditing interface, the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries, each of which can implement (parts of) the auditing API.` Word count = 15 | PASS |
| Anchor §DESCRIPTION | The quoted sentence sits inside `<h2><a id="DESCRIPTION">`…`<pre>` (live lines 75–90; snapshot identical). §DESCRIPTION exists and contains the quote | PASS |
| Revision "Linux man-pages 6.19 (2025-05-17)" | Footline: `Linux man-pages 6.19            2025-05-17                  RTLD-AUDIT(7)`; colophon: tarball `man-pages-6.19.tar.gz` fetched 2026-09-09 | PASS |

No defects found. The grounding claim is conservative: the man page states LD_AUDIT *names* auditor shared libraries; it does not itself assert the linker refuses a non-audit DSO — the lesson's use ("grounds classifying LD_AUDIT by variable name") does not overreach the text.

## Notes

- `Last-Modified: 2026-10-08` post-dates the snapshot's file mtime (13:02 today); irrelevant — the bytes are identical, so the snapshot faithfully records the currently served revision.
- Fetch method: `curl` to `man7.org` over HTTPS, no cache-busting needed; single request.

## Receipts

- `out/Q01Source512/live.html` — live response body (sha256 `a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153`, 26769 B)
- `out/Q01Source512/live.headers` — live response headers

## Tooling

No installs; `curl` and `python3` (stdlib `re`, `html`) already present.
