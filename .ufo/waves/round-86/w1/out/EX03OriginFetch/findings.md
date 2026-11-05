# EX03OriginFetch findings — round-86 C3 live origin leg (freshness)

Measured on this host, 2026-11-04. Instruments read at the frozen revs; no production file
touched; no commits outside the fixture repo; scratch removed after receipts were copied.

## 1. Live leg — both frozen revs

Command (run twice, once per rev):

```
TMPDIR=/fast/scratch/hyaku/kama-r86/EX03OriginFetch/tmp \
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-pin-origin.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev <REV> --rows registry/pin-recheck-rows.tsv
```

- `--rev 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` → stdout
  `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` + 5
  `PIN_ORIGIN_ROW … verdict=verified anchors=2/2` lines, stderr empty, **exit 0**.
- `--rev c07e1f909414aafb2d8de5605a81fd3bd4e3550e` → byte-identical stdout, stderr empty,
  **exit 0**.
- `git diff --stat 3ff23da3… c07e1f90… -- corpus/anchors registry/pin-recheck-rows.tsv
  tools/round86-pin-origin.py` shows only `tools/round86-pin-origin.py | 307 +` — the
  anchors and the rows register are byte-identical between the two revs, so the two runs
  measure the same committed evidence.
- `merge-base` of the two revs is `3ff23da3…`; the freeze commit sits directly on top.

**No row's upstream range failed to match. No URL needed a retry**: the instrument fetches
each URL once per run (per-URL cache, no retry logic — a transient failure would grade
`unreachable`, exit 1, fail-closed); all 8 unique URLs returned HTTP 200 on the first try in
both runs and in the independent probe.

## 2. Per-URL HTTP status and byte counts (independent probe, `probe_urls.out`)

One read-only GET per unique URL, UA `kama-shokunin-pin-origin/1 (read-only documentary check)`:

| URL (all raw.githubusercontent.com) | status | upstream bytes | upstream sha256 (prefix) |
|---|---|---|---|
| ggml-org/llama.cpp/b11755 tools/server/README.md | 200 | 119661 | 714c067bdbc4 |
| ggml-org/llama.cpp/b12111 tools/server/README.md | 200 | 136429 | eafc1b53abd7 |
| ggml-org/llama.cpp/39febd2a tools/server/README.md | 200 | 135608 | 8fd5abde2fb5 |
| ggml-org/llama.cpp/b7200 tools/server/README.md | 200 | 72181 | fb4ab6f2e4db |
| sgl-project/sglang/v0.5.22 native_api.mdx | 200 | 17359 | 209087c3d30d |
| sgl-project/sglang/v0.5.23 native_api.mdx | 200 | 18295 | 3ed171186990 |
| vllm-project/vllm/v0.32.0 prefix_caching.md | 200 | 13916 | 67ee4e2b7bc2 |
| vllm-project/vllm/v0.33.0 prefix_caching.md | 200 | 13916 | 67ee4e2b7bc2 |

All 9 anchors: declared digest == sha256(stored body), and the declared window recomputed
independently from the fetched bytes equals the stored body. The probe's upstream digests
corroborate the prefixes recorded in the rows register notes (`eafc1b53abd78761`,
`fb4ab6f2e4db180b`, `3ed171186990d6a6`, `67ee4e2b7bc23d40`).

## 3. Fabricated-but-hash-consistent pair and digest-lie (fixture repo)

Fixture: own scratch repo `/fast/scratch/hyaku/kama-r86/EX03OriginFetch/fixture`,
HEAD `108f36fbbadae2934e1f8a68e2622367958254d4`; before the commit
`git -C "$D" rev-parse --show-toplevel` printed exactly `$D` (asserted, passed). Both rows
point at the real, fetchable llama.cpp b12111 server README URL.

```
python3 tools/round86-pin-origin.py --repo "$D" --rev 108f36fb… --rows registry/pin-recheck-rows.tsv
→ exit 1
PIN_ORIGIN rows=2 verified=0 mismatch=1 unreachable=0 bad=1
PIN_ORIGIN_ROW fixture/fab verdict=mismatch anchors=0/2
  fab-pin.txt: stored body differs from upstream 479-491; fab-newest.txt: stored body differs from upstream 479-491
PIN_ORIGIN_ROW fixture/lie verdict=bad anchors=0/2
  lie-pin.txt: declared digest does not match the stored body; lie-newest.txt: stored body differs from upstream 479-491
```

- The hash-consistent fabricated pair (header digest correctly computed over a body that
  differs from upstream) grades **`mismatch`, never `verified`** — the digest alone cannot
  buy a `verified`.
- The digest-lie anchor grades **`bad`**; the row takes the worst of its anchors (`bad`
  outranks `mismatch`).
- Instrument `--selftest` on this host: 7/7 arms PASS, exit 0, including
  `fabricated-hash-consistent → mismatch` and `digest-lie → bad`.

## 4. Newline-exactness of the byte comparison (injected-fetcher probe, `newline_probe.out`)

Driven through the instrument's own `grade()`/`check_anchor()` with a recorded fetcher,
exactly like `--selftest`:

| arm | upstream | stored body | verdict |
|---|---|---|---|
| blank-line-end-verified | `line-one\n\nline-three\n`, range 1-2 (ends on blank line) | `line-one\n\n` | **verified** |
| blank-line-end-extra | same | `line-one\n\n\n` (one extra blank) | **mismatch** |
| crlf-upstream-lf-stored | `line-one\r\nline-two\r\n` | `line-one\nline-two\n` | **verified** |
| crlf-upstream-crlf-stored | same | `line-one\r\nline-two\r\n` | **bad** (digest mismatch) |
| formfeed-upstream | `line-one\n\x0cline-two\n` | byte-identical copy | **mismatch** |

Findings:

1. **The asked case is exact**: a range ending on a blank line verifies when the stored body
   keeps that blank line, and an extra trailing blank line is caught as `mismatch`. Trailing
   blank lines are not silently trimmed on either side.
2. **Not byte-exact for carriage returns**: `splitlines()` erases `\r`, so a CRLF upstream
   grades `verified` against an LF-only stored body. A CRLF-only upstream edit inside a
   declared range would be invisible to this instrument.
3. **A CRLF stored body cannot be represented at all**: both read paths
   (`pathlib.Path.read_text` and `subprocess … text=True`) apply universal-newline
   translation, rewriting `\r\n` to `\n` before the digest is recomputed, so the declared
   digest no longer matches and the anchor grades `bad`. Fail-closed, but it means the
   "byte for byte" property holds only for LF-terminated content.
4. **Exotic separators shift phantom line numbers**: `\x0c` (and per Python semantics
   `\x0b`, `\u2028`, `\u0085`) inside a declared range act as `splitlines()` boundaries, so
   a byte-faithful copy of such a range grades `mismatch`. Fail-closed.

None of these boundary conditions is exercised by the five committed rows (all LF-only
markdown/mdx, all verified byte-identical), so the target line
`PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` stands on this host at both
frozen revs. Items 2–4 are boundary notes for future rows, not defects in this round's
evidence.

## 5. Tooling

No tools installed or upgraded; none needed beyond the preinstalled python3/git
(python3 via system, git via system). No pacman transaction performed (host-wide pause
respected).

## Receipts

All under `.ufo/waves/round-86/w1/out/EX03OriginFetch/`:
`run-base.{stdout,stderr,exit}`, `run-freeze.{stdout,stderr,exit}`, `probe_urls.out`,
`selftest.{out,exit}`, `fab-run.{stdout,stderr,exit}`, `newline_probe.{out,exit}`,
`fixture-receipt/` (rows register, four fabricated anchors, COMMIT.txt).
