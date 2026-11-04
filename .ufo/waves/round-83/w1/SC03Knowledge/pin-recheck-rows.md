source: S566 (llama.cpp `tools/server/README.md` at b12110), S567 (SGLang `native_api.mdx` at v0.5.23), S568 (the same at v0.5.22), S569 (vLLM `prefix_caching.md` at v0.33.0), S570 (the same at v0.32.0) — SK01SourceOpen's five anchor extracts, fetched 2026-11-04; the register is `registry/pin-recheck-rows.tsv`.
verified-at: 2026-11-04 — the five rows read against `registry/engine-pin-relations.tsv` and its eight committed extracts under `corpus/anchors/`: every header digest re-derives from its own extract body and every quote occurs on its declared upstream line (8/8 quote cells).
recheck: `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` — first line `engine=sglang pin=v0.5.22 newest=v0.5.23 newer=1 status=behind`, exit 1 (three `behind` rows: a trigger, not a failure). Then `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv`.

# A recheck row is a byte comparison, not a prose judgement

## The register

`registry/engine-pin-relations.tsv` holds five data rows; `registry/pin-recheck-rows.tsv` answers each
`behind` row with exactly one row keyed by `(engine, ref)`, in twelve columns:

`engine, ref, newest, verdict, date, quote_pin, line_pin, quote_newest, line_newest, extract_pin, extract_newest, note`

`newest` is the tag observed at `date`, so a moved tag changes `date` and `newest`, never the verdict rule.
`extract_pin`/`extract_newest` are repo-relative paths to committed anchors, each whose first line is
`# url=<https-url> sha256=<64-hex> ref=<ref> lines=<a>-<b>`; the digest is over the file's bytes after that
line, and the header's `ref` is compared with the row's own `ref`/`newest` cell. The `lines` range is
upstream, so a quote declared at line L must sit on body line L − a + 1 (S566–S570).

## Why bytes

`holds` is re-derived mechanically: the pin quote occurs verbatim in the newest extract's body, and each
declared quote sits on its declared line. The llama.cpp `/health` statement does that — eleven words at
`b11755` line 481 and at `b12111` line 482; S566's `b12110` body is byte-identical to the b12103 artifact's
lines 480–492 (sha256 `71b580d0a0ff…`). `reworded`/`moved`/`drifted` share one test — pin quote absent,
newest quote non-empty and different — so bytes cannot tell those three apart: the word is the reader's
diagnosis and `note` says where the statement went. A prose judgement ("the sentence survived") is
unrunnable; a quote with a line number is not. A row whose key names no relation row, whose extract is
missing or whose header digest disagrees with the extract bytes, whose quote exceeds 25 words, whose quote
does not occur at its declared line, or whose verdict the comparison contradicts is `bad`; the leg exits 1
naming every finding and 2 when a register is absent or unreadable.

## The vocabulary

- `holds` — the anchored statement occurs verbatim at the newest ref, even when its section moved.
- `reworded` — the statement is restated; the pin quote is absent from the newest extract.
- `moved` — the statement survives elsewhere; the pin quote is absent at this anchor.
- `drifted` — the statement changed in substance.
- `ungraded` — the relation names a ref the lane holds no document for; it must carry `verdict=ungraded`
  and a `note` naming the missing document, and never counts as graded.

## Round-83 verdicts

| row | engine, ref | verdict | ground |
|---|---|---|---|
| 1 | llama.cpp `b11755` | holds | newest `b12111`; S566's `b12110` body = b12103's 480–492, `/health` 479→480, quote 481→482 |
| 2 | llama.cpp `39febd2a…` | holds | `/models` listing sentence byte-identical, 2199→2203 |
| 3 | llama.cpp `b7200` | ungraded | no lane-held document at that ref (role `cross-lane kengaku S178`) |
| 4 | sglang `v0.5.22` | holds | S567/S568: `/health`, `/health_generate` verbatim; `/ready`, `/ping` added at 111–112 |
| 5 | vllm `v0.32.0` | holds | S569/S570 extract bodies byte-identical, sha256 `d1498873…`; quote line 3 in both |

## Limits

- The counter prints the target `PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0
  ungraded=1 bad=0`, exit 0, only when each extract header's `ref` names the row's own ref: an abbreviated
  `ref=39febd2a` printed `graded=3 … bad=1` (`ref-mismatch`) until the header was reconciled at 11:04.
- The digest binds the committed extract, not the fetch: a reader re-derives extract integrity, never that
  the bytes were served at the named URL — only a re-fetch checks the URL/ref cell.
- `ungraded` is a gap named, not a verdict; `newest` is a dated observation and upstream can move.
