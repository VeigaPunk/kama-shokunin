# Located anchors — Ollama context length and parallelism (round 25)

Access date for every URL below: **2026-10-22**. All line numbers are lines of the
pinned source file retained under `sources/` in this directory. No Ollama runtime
was used (`command -v ollama` → exit 1).

## Source A — Ollama FAQ

- URL (rendered page): https://docs.ollama.com/faq
- URL (pinned source): https://raw.githubusercontent.com/ollama/ollama/33a3afa604b4e5c90263f006d979bc433d39c38d/docs/faq.mdx
- Pin: `ollama/ollama` commit `33a3afa604b4e5c90263f006d979bc433d39c38d`, authored/committed
  2026-10-13 10:05:39 -0700, subject "docs: changing model recs to Models page link, updating
  references to Ollamas cloud". Last commit touching `docs/faq.mdx` at the access date.
- Byte identity: the file fetched at `main` HEAD `efabf6bc450454dc856c1f799aac7ea865e3a4cf`
  (2026-10-21 22:00:18 -0400) is byte-identical to the pinned file
  (`diff` → no output, exit 0).
- sha256 of the retained file: `e3630684676a21219abc7cb6c17db53993412c194ba9c108c8dbae2f30318e0c` (18143 bytes)
- Live-page comparison: `live-faq-vs-pinned.diff` (rendering-only differences: frontmatter
  `title: FAQ`, `shell theme={"system"}` annotations, note-block syntax).

Located quotes (each ≤ 25 words, with line numbers in the pinned file):

| line | quote | words |
|---|---|---|
| 23 | `## How can I specify the context window size?` (section heading) | 9 |
| 25 | `By default, Ollama uses a context window size of 4096 tokens.` | 11 |
| 27 | `This can be overridden with the `OLLAMA_CONTEXT_LENGTH` environment variable.` | 11 |
| 36 | `/set parameter num_ctx 4096` | 4 |
| 39 | `When using the API, specify the `num_ctx` parameter:` | 9 |
| 324 | `## How does Ollama handle concurrent requests?` (section heading) | 7 |
| 330 | `Parallel request processing for a given model results in increasing the context size by the number of parallel requests.` | 19 |
| 335 | `Required RAM will scale by `OLLAMA_NUM_PARALLEL` * `OLLAMA_CONTEXT_LENGTH`.` | 11 |

Line 330 continues with the worked example: `For example, a 2K context with 4 parallel requests
will result in an 8K context and additional memory allocation.` Line 335 continues with
`OLLAMA_NUM_PARALLEL` - `The maximum number of parallel requests each model will process at the
same time, default 1.`

## Source B — Ollama Context length

- URL (rendered page): https://docs.ollama.com/context-length
- URL (pinned source): https://raw.githubusercontent.com/ollama/ollama/8583859ea6d8013c8160510e4a16fdd4c79483f7/docs/context-length.mdx
- Pin: `ollama/ollama` commit `8583859ea6d8013c8160510e4a16fdd4c79483f7`, committed
  2026-10-12 13:07:13 -0700, subject `Revert "docs: restructuring" (#18960)`. Last commit touching
  `docs/context-length.mdx` at the access date.
- Byte identity: byte-identical to the same path at `main` HEAD
  `efabf6bc450454dc856c1f799aac7ea865e3a4cf` (`diff` → no output, exit 0).
- sha256 of the retained file: `8414ca2ad9c67fbd9bd1497bf352fb60993b2b5b69531118f456f9b31af87aa7` (1413 bytes)
- Live-page comparison: `live-context-length-vs-pinned.diff` (rendering-only differences:
  frontmatter, `<Note>` → `> [!NOTE]`, image path).

Located quotes (each ≤ 25 words, with line numbers in the pinned file):

| line | quote | words |
|---|---|---|
| 5 | `Context length is the maximum number of tokens that the model has access to in memory.` | 16 |
| 8 | `Ollama defaults to the following context lengths based on VRAM:` | 10 |
| 9 | `- < 24 GiB VRAM: 4k context` | 6 |
| 10 | `- 24-48 GiB VRAM: 32k context` | 5 |
| 11 | `- >= 48 GiB VRAM: 256k context` | 6 |
| 18 | `Setting a larger context length will increase the amount of memory required to run a model.` | 16 |
| 28 | `OLLAMA_CONTEXT_LENGTH=64000 ollama serve` | 3 |

## Documentary conflict inside the same pinned repository state (both pages, Oct 2026)

Verbatim, Source A line 25:

> By default, Ollama uses a context window size of 4096 tokens.

Verbatim, Source B lines 8–11:

> Ollama defaults to the following context lengths based on VRAM:
>   - < 24 GiB VRAM: 4k context
>   - 24-48 GiB VRAM: 32k context
>   - >= 48 GiB VRAM: 256k context

Both statements are present in `ollama/ollama` at HEAD `efabf6bc450454dc856c1f799aac7ea865e3a4cf`.
The pages are not reconciled by any sentence either page contains. Nothing in either page says
which one wins at run time.
