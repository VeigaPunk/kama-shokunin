VERDICT: partial — the 3.14.8 title, 301 direction, pinned hash/identity and all six quoted sentences reproduce exactly, and no delivered file cites 3.15; but the integrated row calls the redirect source "canonical" while the page's actual canonical link is the versionless `/3/` URL now serving Python 3.15.0, the build-draft hierarchy list omits `Exception`, and the source record omits `BaseExceptionGroup` from the declared escape set.

# ReopenS051 — S051 redirect, canonical title, hierarchy, receipt rationale, 3.15 provenance

Seat: KamaR18.ReopenS051. Read-only check: no production/fleet/lane edit, no jj, no ports, no installs, no mutants, no tests/gates run. Read at clone `/tmp/kama-r18-falsify-ReopenS051` = `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (switch `-c seat/ReopenS051`, `rev-parse HEAD` returned the same SHA). Live fetches were loopback-outbound HTTP only; no listener was opened. Scratch removed at finish.

## Observed facts (executed)

### 1. Actual redirect chain and titles (live, 2026-10-20 ~23:15–23:16Z)

Commands (in `/tmp/kama-r18-falsify-ReopenS051-fetch`):

```
curl -sS -D builtins.headers -o builtins.body --max-time 30 https://docs.python.org/3.14/builtins/exceptions.html
curl -sS -D library.headers -o library.body --max-time 30 https://docs.python.org/3.14/library/exceptions.html
curl -sS -L -D follow.headers -o follow.body --max-time 30 https://docs.python.org/3.14/library/exceptions.html
curl -sS -L --max-time 20 https://docs.python.org/3/builtins/exceptions.html -o tmp.html
curl -sS -L --max-time 20 https://docs.python.org/3.15/builtins/exceptions.html -o tmp.html
```

- `https://docs.python.org/3.14/builtins/exceptions.html` — **HTTP/2 200, direct, no redirect**; `content-length: 144074`; `last-modified: Tue, 20 Oct 2026 22:13:02 GMT`; `etag: "6ad7e76e-232ca"`; `sha256 7fa78d90283ad06d137b416f16c34feb29022688baf83a07b3fa3b145f42c4a3`; `<title>Built-in Exceptions &#8212; Python 3.14.8 documentation</title>`; footer `Last updated on Oct 20, 2026 (22:11 UTC).`
- `https://docs.python.org/3.14/library/exceptions.html` — **HTTP/2 301**, `location: https://docs.python.org/3.14/builtins/exceptions.html`, 162-byte body (`sha256 9e17cb15dd75bbbd5dbb984eda674863c3b10ab72613cf8a39a00c3e11a8492a`, `<title>301 Moved Permanently</title>`). With `-L`: final 200, 144074 bytes, `sha256 7fa78d90…`, and `cmp -s follow.body builtins.body` → **IDENTICAL** (exit 0).
- So the pin receipt's direction is right: library → 301 → builtins. The draft's phrase "the same bytes are served at /3.14/library/exceptions.html" is true only **after** following the 301; the direct response at that URL is a 162-byte redirect page, not 144074 bytes.
- The pinned page's own canonical link (`sources/raw/docs.python.org/3.14/library/exceptions.html:46`) is `<link rel="canonical" href="https://docs.python.org/3/builtins/exceptions.html">` — versionless. Fetched live: **HTTP 200, title `Built-in Exceptions — Python 3.15.0 documentation`**, footer `(22:07 UTC)`. `https://docs.python.org/3.15/builtins/exceptions.html` also serves the same 3.15.0 title. Thus the document's declared canonical URL currently resolves to **Python 3.15.0**, not 3.14.8.

### 2. Pinned bytes and identity (clone at lane master)

- `sha256sum .ufo/waves/round-18/sources/raw/docs.python.org/3.14/library/exceptions.html` → `766d785f3da3cded889c028a75e917fedca36d969627ef21cfb08ed5e6fcdd26` (144074 bytes), matching `pins.json` `sources.python_exceptions.sha256` and `documents.python_exceptions.sha256`.
- Pinned `<title>` → `Built-in Exceptions &#8212; Python 3.14.8 documentation`; pinned footer line 1620 → `Last updated on Oct 20, 2026 (20:36 UTC).` Both match the draft's anchor cell verbatim.
- `pins.json` `documents.python_exceptions.identity` = `{"title": "Built-in Exceptions — Python 3.14.8 documentation", "version": "Python 3.14.8", "last_updated": "Oct 20, 2026 (20:36 UTC)"}` — exact match to the draft claim.
- `pins.json` `sources.python_exceptions` = `url: https://docs.python.org/3.14/library/exceptions.html`, `final_url: https://docs.python.org/3.14/builtins/exceptions.html`, `redirects: [{status:301, from: library, to: builtins}]`, `http_status: 200`, bytes 144074, `headers.Last-Modified: Tue, 20 Oct 2026 20:38:59 GMT`, `ETag "6ad7d163-232ca"`.
- The same `pins.json` appears twice, byte-identical (`sha256 6f5623975d68c95bd65dd5abb067cffdab3c296e26caba06d3915ba97161a26d` for both `.ufo/waves/round-18/sources/pins.json` and `build/out/SourcePins/pins.json`); `pin.py` likewise (`8213363b…`) — matching `build/advice/SourcePins.md`'s recorded digests.
- Today's live page differs from the pinned copy **only in the footer timestamp line**: text diff of pinned vs live (tag-stripped) is one line, `(20:36 UTC)` → `(22:11 UTC)`; byte size is unchanged at 144074 and ETag size suffix `232ca` is unchanged. Current live hash is therefore `7fa78d90…`, not the pinned `766d785f…`.

### 3. BaseException hierarchy (pinned bytes, lines 1402–1475)

Tree at `sources/raw/docs.python.org/3.14/library/exceptions.html:1405-1410`:

```
BaseException
 ├── BaseExceptionGroup
 ├── GeneratorExit
 ├── KeyboardInterrupt
 ├── SystemExit
 └── Exception
```

Five direct children, including `Exception`. The official pin `pins.python_exception_hierarchy` quotes exactly this five-child line (`"BaseException ├── BaseExceptionGroup ├── GeneratorExit ├── KeyboardInterrupt ├── SystemExit └── Exception"`, `matched: true`), so the receipt itself is complete.

The build draft's teaching cell (`build/drafts/sources-python.md:9`) says "`BaseException` has direct children `BaseExceptionGroup`, `GeneratorExit`, `KeyboardInterrupt`, `SystemExit`" — four, omitting `Exception`. As a bare hierarchy enumeration that is incomplete/false by omission, although the same cell then correctly separates `Exception` subclasses as caught. The **integrated** row (`corpus/SOURCES.md:63`) drops that enumeration and teaches only "`KeyboardInterrupt`, `SystemExit` and `GeneratorExit` derive from `BaseException`, not `Exception`" — true and sufficient for C1's three internal-fault kinds, but it omits `BaseExceptionGroup` from the row's stated scope "which built-in exceptions escape `except Exception`". The page (pinned lines 1273–1283) says `except Exception catches an ExceptionGroup but not BaseExceptionGroup`, and that the `BaseExceptionGroup` constructor returns an `ExceptionGroup` if all contained exceptions are `Exception` instances. So the complete escape set is the four non-`Exception` direct children (with the constructor caveat for `BaseExceptionGroup`), not three.

### 4. Quote verification (pinned bytes)

All six draft Gate quotes (`build/drafts/sources-python.md:17-22`) are verbatim in the pinned page after whitespace normalisation (the HTML wraps lines):

| quote (fragment) | location | draft count | my whitespace count |
|---|---|---|---|
| It inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception. | `:854-856` (§SystemExit) | 19 | 19 |
| It directly inherits from BaseException instead of Exception since it is technically not an error. | `:458-459` (§GeneratorExit) | 16 | 15 |
| The exception inherits from BaseException so as to not be accidentally caught by code that catches Exception | `:517-519` (§KeyboardInterrupt) | 18 | 17 |
| BaseExceptionGroup extends BaseException and it can wrap any exception, while ExceptionGroup extends Exception | `:1273-1275` | 13 | 13 |
| except Exception catches an ExceptionGroup but not BaseExceptionGroup. | `:1276-1277` | 9 | 8 |
| All built-in, non-system-exiting exceptions are derived from this class. | `:377` (§Exception) | 11 | 9 |

No quote exceeds 25 words under any counting; the `source-pins-selftest` quote check (official run) also passed. But three of six recorded word counts are inflated by 1–2, so the per-row counts are not literal `.split()` counts. The lesson's only used S051 quote (`corpus/lessons/round-18.md:47`, SystemExit, 19 words) is exact.

The draft's scope note labels the `BaseExceptionGroup`-constructor behaviour `[INFERENCE]` (`build/drafts/sources-python.md:32`) although the page states it directly at `:1278-1281` ("The BaseExceptionGroup constructor returns an ExceptionGroup rather than a BaseExceptionGroup if all contained exceptions are Exception instances"). Under-labelled, not wrong.

### 5. Receipt rationale / official exercise

- `sources/pin.py:468-488` follows redirects, records the chain, and hashes the final body; `pin.py:612-700` `verify_record` compares source SHA-256, document SHA-256, identity (title/version/last_updated) and excerpt pins on a re-fetch.
- Official run command list (`runs/commands.json`, 32 commands) includes only `source-pins-selftest` (`pin.py --selftest`, exit 0, expected 0, started 2026-10-20T22:36:27Z). Its stdout: 7 PASS lines including `PASS citation quotes stay within 25 words` and `PASS saved artifact re-derivation: artifact check passed (9 raw documents re-derived)`. **The live re-fetch path (`--verify`) was never run**; `build/advice/SourcePins.md` discloses this and that the initial capture exited 2 only on the GNU HTML timeout. So the receipt rationale is: pinned bytes + identity are verified offline against the saved artifact; live-network verification is unexercised in this wave.
- Consequence of §1: a `--verify` today would compare fresh `sha256 7fa78d90…` against recorded `766d785f…` and fresh identity `last_updated 22:11 UTC` against recorded `20:36 UTC`, i.e. report a digest/identity change caused by a docs rebuild whose only text difference is the footer timestamp. The saved artifact is still self-consistent (`--selftest` passed at 22:36Z, after the 22:11Z rebuild).
- `saved_as` names the **requested** URL (`raw/docs.python.org/3.14/library/exceptions.html`) while the saved bytes are the redirect target; the receipt records `final_url` and the 301, and the advice says so, but re-opening `saved_as` as a URL without redirect-following yields the 162-byte 301 page, not the saved document.

### 6. 3.15 provenance

- Delivered citations are all `/3.14/`: `corpus/SOURCES.md:63` (S051 URL), `corpus/lessons/round-18.md:18,47`, `corpus/knowledge/llamacpp-loading-lifecycle.md:254`, `tools/kama-llamacpp-live.py:60` (`https://docs.python.org/3.14/library/subprocess.html`). Grep for `3\.15` over `corpus/SOURCES.md`, `round-18.md`, `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/`, `.ufo/waves/round-18/c1/`, `.ufo/waves/round-18/c2/`, `corpus/knowledge/` found no 3.15 citation: only S044's note (`corpus/SOURCES.md:56`) that `/3/` now serves 3.15, and the capture-scope prose at `:172,175`.
- Official evidence records `"python": "3.14.8 (main, Oct  2 2026…) [GCC 16.2.1]"` (`runs/commands.json`).
- However, `corpus/SOURCES.md:63` calls `/3.14/library/exceptions.html` "the canonical" URL; the page's actual canonical link is `/3/builtins/exceptions.html`, verified today serving **Python 3.15.0**. The row's URL/title are 3.14.8, so the claim is not built on 3.15 bytes, but the word "canonical" is wrong and the document's own canonical pointer is a live 3.15 drift hazard.

### 7. C1 BaseException receipts (spot support, not an admission)

- `tools/kama-llamacpp-live.py:888-891` `_record_internal` sets `internal:<type>` into both `internal_fault` and `setup_error`; lifecycle guards at `:1401,1451,1524` catch `BaseException`.
- `tests/llamacpp-live/controls.py:649-656` defines k18: inject `KeyboardInterrupt` into `teardown_graceful`; receipt must carry `internal:KeyboardInterrupt` and exit exactly 2. `tests/llamacpp-live/check-receipt.py:279-285` requires `internal_fault == setup_error`, `:1351-1355` requires the `internal:<ExcType>` prefix, and `:1913-1914` mutates the mirror away (`v3-internal-fault-not-mirrored`).
- `runs/c1-measure.json` k18: `before: accepted`, `after: rejected-targeted`, `after_failed_checks: [teardown_graceful]`, `targeted_hit: true`, `changed: true`; raw per-control detail shows `tool_exit: 2, gate_exit: 1`. Overall `c1-measure` exit is **2** (`counts.misclassified.before=1`), as the lesson discloses; k18 is raw arm evidence, not an admitted overall pass.

## Findings

- **F1 (source-wording, medium)** — `corpus/SOURCES.md:63` calls `/3.14/library/exceptions.html` "the canonical" URL. Verified: that URL is a 301 alias; the document's `<link rel="canonical">` is `/3/builtins/exceptions.html` (`pinned:46`), which today serves Python 3.15.0. The rows/lesson/tool all cite `/3.14/`, so no 3.15 bytes ground the claim; only the label is wrong. Fix: say "the legacy `/3.14/library/exceptions.html` path 301s to it" and never use `/3/`.
- **F2 (hierarchy, low–medium)** — the build-draft enumeration (`drafts/sources-python.md:9`) omits `Exception` from `BaseException`'s direct children (actual tree: five, including `Exception`). The integrated row (`SOURCES.md:63`) avoids that false list but under-enumerates the scope's escape set by omitting `BaseExceptionGroup` (which escapes `except Exception` unless constructed as `ExceptionGroup`). The official `pins.python_exception_hierarchy` receipt contains the correct five-child line; C1's three internal-fault kinds are unaffected.
- **F3 (receipt, low)** — the pin's saved copy is honest and hash-verified offline, but the live `--verify` path is unexercised in the official run (only `--selftest`), and today's live 3.14 page differs from the pin by its footer timestamp alone, so a strict verify would now fail on `766d785f…` → `7fa78d90…`. This is snapshot-vs-mutable-doc behaviour, not a false claim, but the `on-release` recheck must repin rather than assume the hash.
- **F4 (quote counts, low)** — three of six Gate word counts are off by 1–2 (15/16, 17/18, 8/9, 9/11); all remain ≤25 so the gate rule holds, but the counts are not reproducible as `len(q.split())`.
- **F5 (under-labelled inference, low)** — the `BaseExceptionGroup` constructor return rule is stated verbatim on the pinned page (`:1278-1281`) but the draft marks it `[INFERENCE]`; a reader could think the page is silent.
- **F6 (no 3.15 provenance, confirmed)** — every delivered citation is `/3.14/` (paths in §6); the only 3.15 mentions are explicit warnings/precedent notes. No 3.15 bytes are used as evidence.

## Confidence

- High: redirect direction (301 library→builtins), 200 direct at builtins, 3.14.8 title, pinned hash `766d785f…`/144074 bytes, identity title/version/footer, all six quotes verbatim, five-child hierarchy, `/3/` title 3.15.0.
- Medium: live-hash drift cause (text diff is footer-only; tag attributes were compared only for the canonical line, not exhaustively; ETag/size unchanged).
- Interpretation-level: whether "canonical" in `SOURCES.md:63` means legacy path or HTML canonical; no author note found either way.

## Remaining unknowns

- Whether `docs.python.org/3/builtins/exceptions.html` will stay on 3.15.0/change again; today's probe was a single fetch (Varnish `age: 0`, `x-cache: MISS, MISS`), so CDN staleness is unlikely but not excluded.
- Whether the wave's `on-release` recheck expects byte-exact stability; if so, the same-day 20:36→22:11 rebuild already breaks it for S051.
- No runtime hierarchy experiment was performed (docs-only per assignment); the host's actual `BaseException.__subclasses__()` was not enumerated.
- The 3.15 pages were opened only for title/footer/canonical provenance probes, not as sources.

## Exact experiment source

```
cd /tmp/kama-r18-falsify-ReopenS051-fetch
curl -sS -D builtins.headers -o builtins.body --max-time 30 https://docs.python.org/3.14/builtins/exceptions.html
curl -sS -D library.headers -o library.body --max-time 30 https://docs.python.org/3.14/library/exceptions.html
curl -sS -L -D follow.headers -o follow.body --max-time 30 https://docs.python.org/3.14/library/exceptions.html
sha256sum builtins.body library.body follow.body
cmp -s follow.body builtins.body && echo IDENTICAL
grep -o '<title>[^<]*</title>' builtins.body library.body
grep -n "Last updated" builtins.body
grep -o '<link[^>]*canonical[^>]*>' builtins.body
curl -sS -L --max-time 20 https://docs.python.org/3/builtins/exceptions.html -o tmp.html   # title 3.15.0
curl -sS -L --max-time 20 https://docs.python.org/3.15/builtins/exceptions.html -o tmp.html # title 3.15.0
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-ReopenS051
git -C /tmp/kama-r18-falsify-ReopenS051 switch -q -c seat/ReopenS051 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
sha256sum .ufo/waves/round-18/sources/raw/docs.python.org/3.14/library/exceptions.html
python3 - <<'EOF'  # quote/hierarchy extraction from the pinned copy
import re, html
b = open('.ufo/waves/round-18/sources/raw/docs.python.org/3.14/library/exceptions.html', encoding='utf-8').read()
t = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', b)).split())
EOF
python3 -c "import json; ... pins.json fields ..."
```

## Limits

- Single live fetch per URL at ~23:15–23:16Z; the docs site rebuilds (20:36Z pin, 22:11Z live footer) and may change again.
- No build/test/gate/mutant run, no ports, no installs, no tool upgrades; only read-only filesystem/network checks. `pin.py --verify` was not run (it re-fetches all pinned sources, including the GNU host the parent directed not to retry).
- The C1 score is not evaluated here; `c1-measure` exit 2 is reported as disclosed, and k18 is cited only as raw per-control evidence.
