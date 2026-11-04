# A recheck row is a byte comparison, not a prose judgement

source: S566 — https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md — §`### GET /health` — opened 2026-11-04; S567 (SGLang `native_api.mdx` at v0.5.23), S568 (the same at v0.5.22), S569 (vLLM `prefix_caching.md` at v0.33.0), S570 (the same at v0.32.0)
verified-at: 2026-11-04 — every digest below re-derives from the committed extract body under `corpus/anchors/`, and every quote occurs on its declared line of its extract.
recheck: `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` (a `behind` row is a trigger) then `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv` → `PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0`, exit 0.

## The register

`registry/engine-pin-relations.tsv` holds five data rows; `registry/pin-recheck-rows.tsv` answers each
with exactly one row keyed `(engine, ref)`, in twelve columns: `engine, ref, newest, verdict, date,
quote_pin, line_pin, quote_newest, line_newest, extract_pin, extract_newest, note`.

`newest` is the tag observed at `date`, so a moved tag changes `date` and `newest` and never the verdict
rule. Each extract is a committed file whose first line is
`# url=<https-url> sha256=<64-hex> ref=<ref> lines=<a>-<b>`; the digest is over the bytes after that
line, so an extract attests its own body and never the whole upstream document. A row's `line_pin` is a
source-document line number; the extract's `lines=a-b` header maps it to extract line `2 + (line - a)`.

## Why bytes

`holds` is re-derived mechanically: the pin quote occurs on its declared line of the newest extract and
the newest quote is the same text. Three of this lane's relations prove the shape:

| relation | ground | verdict |
|---|---|---|
| llama.cpp `b11755` → `b12111` | `corpus/anchors/llamacpp-b11755-health.txt` and `…-b12111-health.txt` are 13-line regions with the same body digest (`2b5003ed…`): the `/health` sentence is at 481 and 482 | `holds` |
| sglang `v0.5.22` → `v0.5.23` | `/health` and `/health_generate` are byte-identical; v0.5.23 adds `/ready` (line 111) and `/ping` (line 112), so the held sentences hold and the addition is new ground | `holds` |
| vllm `v0.32.0` → `v0.33.0` | the two documents are byte-identical, 13916 bytes, sha256 `67ee4e2b…3a61` | `holds` |

`reworded`, `moved` and `drifted` share one test — the pin quote is absent and the newest quote is
non-empty and different — so bytes cannot separate those three: the word is the reader's diagnosis and
`note` says where the statement went. A prose judgement ("the sentence survived") is unrunnable; a quote
with a line number is not.

## The vocabulary

- `holds` — the anchored statement occurs verbatim at the newest ref, even when its section moved.
- `reworded` — the statement is restated; the pin quote is absent from the newest extract.
- `moved` — the statement survives elsewhere; the pin quote is absent at this anchor.
- `drifted` — the statement changed in substance.
- `ungraded` — the relation names a ref the lane holds no document for; it must carry `verdict=ungraded`
  and a `note` naming the missing document, and it never counts as graded.

A row whose key names no relation row, whose extract is missing or whose header digest disagrees with
the extract bytes, whose quote exceeds 25 words, whose quote does not occur at its declared line, or
whose verdict the comparison contradicts is `bad`; the leg exits 1 naming findings and 2 when a register
is absent or unreadable.

## Limits

A recheck says nothing about model quality, served behaviour or whether an engine is running: it reads
committed documents. The relation register names three engines only; other engines' documents and a live
serving runtime stay frontier. The newest-tag cell is a dated observation — llama.cpp moved b12103 →
b12110 → b12111 on 2026-11-04 while serving one body (sha256 `eafc1b53…a137`), which is why the row's
verdict is never read off the tag distance.
