# SC01 — six `corpus/SOURCES.md` rows for round 83 (scribe)

Seat `SC01Sources`, kama r83 w1: rows `S566`–`S571` plus the single `corpus/README.md`
`## Coverage map` row for the recheck-register ground. No production file touched — `SOURCES.md`,
`README.md`, `QUALITY.md`, `LOG.md`, `SCORECARD.md`, `tools/`, `registry/` are unmodified by this
seat (`git status --porcelain` lists only sibling round-83 artifacts).

## Delivered (relative to this seat dir)

| path | contents | lines |
|---|---|---|
| `rows.md` | the six registry rows, rows only — insert at the end of the `## Registry` table, immediately before `## Paths` | 6 |
| `coverage-row.md` | the one `## Coverage map` row (`Entry / Covers / Round`) | 1 |

`rows.md` holds no fence and no prose, so a paste or a `python3 - <<` insertion lands clean.
It must not go at EOF (F5).

## Rows and opening evidence

| id | source (tail) | sha256 | bytes | lines | quote line | words |
|---|---|---|---|---|---|---|
| S566 | llama.cpp `tools/server/README.md` @ b12110 | `eafc1b53abd7…` | 136429 | 2620 | 482 | 11 |
| S567 | SGLang `native_api.mdx` @ v0.5.23 | `3ed171186990…` | 18295 | 471 | 111 | 18 |
| S568 | SGLang `native_api.mdx` @ v0.5.22 | `209087c3d30d…` | 17359 | 467 | 109 | 8 |
| S569 | vLLM `prefix_caching.md` @ v0.33.0 | `67ee4e2b7bc2…` | 13916 | 236 | 3 | 16 |
| S570 | vLLM `prefix_caching.md` @ v0.32.0 | `67ee4e2b7bc2…` | 13916 | 236 | 3 | 16 |
| S571 | `https://git-scm.com/docs/git-blame` (latest build) | `cc28e3b8008d…` | 82763 | 2847 | 2146 | 17 |

All six are `mined`, `opened=2026-11-04`, tier A, kind `docs`. `recheck`: `45d` on the
newest-side rows (S566, S567, S569), `90d` on the pinned-side rows (S568, S570), `180d` on
the git manual — the S563/S564 split. `used-by`: S566–S570 →
`corpus/knowledge/pin-recheck-rows.md`; S571 → `corpus/knowledge/register-row-introduction.md`.

Opening receipt `.ufo/waves/round-83/w1/SK01SourceOpen/sources.json` landed mid-seat; all six
sha256 values agree with this seat's own `curl -sS -o file -w '%{http_code} %{size_download}'`
fetches (HTTP 200), as do the quotes and their lines. Bytes retained at `source/S566.md`…
`source/S571.md`.

## Gates run (command, then real exit code)

1. `python3 .ufo/waves/round-83/w1/SC01Sources/quote-check.py` → `CHECK rows=6 failures=0`,
   **exit 0**; re-run after the scratch tree was deleted, so it is reproducible from the seat
   dir alone (`quote-check.out`). It imports the corpus's own `split_cells` from
   `tools/sources-append-only.py`.
2. Append-only guard, scratch fixture (base = current `corpus/SOURCES.md`, tip = same file with
   `rows.md` inserted before `## Paths`): `python3 tools/sources-append-only.py --from
   73c2e578e5d3… --to 5925307bfe74… --repo <fixture> --path corpus/SOURCES.md` → six
   `added S5NN (allowed)`, `no append-only violations`, **exit 0** (`append-only-gate.out`).
3. Control: same rows appended at EOF → `error: …:668: row-like line outside the parsed
   registry table: … refusing to drop it`, **exit 2** (`append-only-eof-control.out`).
4. Structural parse of the real file with `rows.md` inserted: 305 → 311 rows, six added, none
   removed, zero changed existing cells, contract header intact.
5. Alignment with the landed `registry/pin-recheck-rows.tsv`: `llama.cpp b11755 → line 481 pin
   / 482 newest` matches S566 (482); `sglang v0.5.22 → 109 / 109` matches S568 (109) and S567
   (109 unchanged); `vllm v0.32.0 → 3 / 3` matches S569/S570 (3). Three `holds`,
   `llama.cpp b7200` `ungraded` as planned.

## Findings

- **F1 — the register's `newest` moved a tag, not a byte.** The register names `b12111`; S566
  is fixed by the dispatch at `b12110`. Fetched b12111 is byte-identical to b12110, to b12103
  and to the round-82 `SK01PinRecon` artifact: one sha256 `eafc1b53abd7…`, 136429 B, 2620
  lines. S566's digest is the register's newest-side bytes.
- **F2 — relation 4 is anchor-stable.** v0.5.22 → v0.5.23 differs by exactly 936 bytes:
  `/ready` and `/ping` added at lines 111-112 (plus one `/tokenize` paragraph at EOF); lines
  109-110 are byte-identical at the same line numbers.
- **F3 — relation 5 is one blob.** vLLM `prefix_caching.md` is `67ee4e2b7bc2…`, 13916 B, 236
  lines at both v0.32.0 and v0.33.0 — 0 bytes differ.
- **F4 — S571's sentence crosses a line break** (HTML 2146 → 2147); verbatim only after
  whitespace normalization. The receipt marks it `quote_match=line-span-normalized`,
  `quote_line=2146`; the row records `retained lines 2146-2147`.
- **F5 — placement matters.** An EOF append makes the guard refuse the whole file (control 3),
  so the rows belong at the end of the `## Registry` table and `rows.md` carries rows only.

## Out of scope and limits

- No `git` mutation ran in the lane; every fixture was a scratch `git init` asserted with
  `rev-parse --show-toplevel`, and the scratch root was deleted before this report
  (`test -e` → gone).
- The two `used-by` targets did **not exist** at this seat's last check (sibling seats still
  running). Until they land, those cells point at absent files and the loop is open.
- `SK01SourceOpen` also opened `S571b` (git-blame anchor at line 2579); not rowed — the item
  fixes six rows, one per listed source.
- No tool was installed or upgraded; the named items required none.

## Artifacts

`.ufo/waves/round-83/w1/SC01Sources/{rows.md,coverage-row.md,quote-check.py,quote-check.out,`
`append-only-gate.out,append-only-eof-control.out,source/}`
