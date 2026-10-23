ATTACK lesson round-26 Gate rows S114-S130 and the census: holds (two low-severity presentation findings, no correctness defect)

Seat: KamaR26.ReviewerGateQuotes (wave 2, FALSIFY). Date 2026-10-23. Lane tip read: f4066979096e3452ae731c0e09e50155c6d8258a (working copy, read-only).
No llama-server started (no port block assigned). No tool installs or updates.

## Fresh fetch (commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, accessed 2026-10-23)

Command: `curl -fsSL -o <f> https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>` into `/fast/scratch/hyaku/kama-r26w2/ReviewerGateQuotes/fresh/`; every curl exit 0.

| file | fresh sha256 | lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/` | SOURCES anchor cell |
|---|---|---|---|
| tools/server/server-context.cpp | dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | MATCH | MATCH (S114-S125) |
| tools/server/server-common.cpp | b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442 | MATCH | MATCH (S126-S127) |
| ggml/src/gguf.cpp | 7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5 | MATCH | MATCH (S128-S129) |
| src/llama-context.cpp | 2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5 | MATCH | MATCH (S130) |

## Per-row table

Checker: `out/ReviewerGateQuotes/check_gate.py` (run `timeout 60 python3 check_gate.py`, exit 0; output `out/ReviewerGateQuotes/check_gate.out`). Columns:
- anchor: the URL `#L` number equals the "line N:" number in the quote cell, and equals the line number in the SOURCES.md anchor cell. The SOURCES.md URL is identical to the lesson URL.
- sig@L: the `registry/error-signatures-r26.json` signature for the row is a substring of the fresh source line at the URL anchor. It occurs on that line only in the file, and in no other snapshot file.
- words: whitespace-split count / count of alphanumeric tokens.
- verbatim: the quote is a substring of the fresh line at the anchor ("whole" means it equals the stripped line).
- span: whether the markdown code span renders correctly.

| row | sig | file:line (lesson line) | anchor | sig@L | words | verbatim | span |
|---|---|---|---|---|---|---|---|
| S114 | E26-01 | server-context.cpp:5366 (27) | ok | ok | 12 / 15 | whole | BROKEN (inner backticks) |
| S115 | E26-02 | server-context.cpp:5408 (28) | ok | ok | 12 / 17 | whole | BROKEN (inner backticks) |
| S116 | E26-03 | server-context.cpp:3084 (29) | ok | ok | 12 / 14 | whole | ok |
| S117 | E26-04 | server-context.cpp:5453 (30) | ok | ok | 13 / 16 | whole | BROKEN (inner backticks) |
| S118 | E26-05 | server-context.cpp:6132 (31) | ok | ok | 11 / 14 | whole | BROKEN (inner backticks) |
| S119 | E26-06 | server-context.cpp:6137 (32) | ok | ok | 14 / 17 | whole | ok |
| S120 | E26-07 | server-context.cpp:6151 (33) | ok | ok | 7 / 10 | whole | ok |
| S121 | E26-08 | server-context.cpp:5803 (34) | ok | ok | 11 / 14 | whole | BROKEN (inner backticks) |
| S122 | E26-09 | server-context.cpp:5476 (35) | ok | ok | 10 / 15 | whole | ok |
| S123 | E26-10 | server-context.cpp:3657 (36) | ok | ok | 13 / 12 | whole | ok |
| S124 | E26-11 | server-context.cpp:5998 (37) | ok | ok | 7 / 10 | whole | ok |
| S125 | E26-12 | server-context.cpp:5655 (38) | ok | ok | 9 / 12 | whole | ok |
| S126 | E26-13 | server-common.cpp:1272 (39) | ok | ok | 19 / 20 | whole | ok |
| S127 | E26-14 | server-common.cpp:1114 (40) | ok | ok | 25 / 26 | prefix, cut at `&` | ok |
| S128 | E26-15 | gguf.cpp:1021 (41) | ok | ok | 11 / 15 | whole | ok |
| S129 | E26-16 | gguf.cpp:482 (42) | ok | ok | 12 / 18 | whole | ok |
| S130 | E26-17 | llama-context.cpp:2624 (43) | ok | ok | 3 / 3 | whole | ok |

Summary: the anchor, signature-at-anchor and verbatim checks pass 17/17. All 17 quotes are at most 25 words when split on whitespace. Every SKILL.md guard range (for example `server-context.cpp:5365-5367` for E26-01, read at SKILL.md:1083-1100) contains its row's anchor line.

## Census

Command: `cd /home/vgpnk/Projects/shokunin && timeout 300 ./scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
Exit code: 0. The last line is `kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. The other lines are W04 warnings ("duplicate url ... across scopes"). They come from rows that share a file URL, because the census compares URLs without their `#L` fragment. The script says warnings "do not affect clean lanes" (`scripts/sources-census.sh:33`; test `W04-does-not-fail-validation` at :364). Output: `out/ReviewerGateQuotes/census.out`.
`diff .ufo/waves/round-26/final/census-validate.out <mine>` shows one difference, the receipt's trailing `exit=0` line (`51d50 < exit=0`); the other 50 lines are byte-identical. The landed `census-validate.err` is empty.

## Row recount

Command: `git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`
- 1560e4d8 (resolves to 1560e4d83f42b04f40336357de6f9637eafa0f4b): **113**, exit 0
- f4066979096e3452ae731c0e09e50155c6d8258a: **135**, exit 0
- There are no duplicate ids at the tip. The id-set diff 1560e4d8 → tip adds exactly S114-S135 (22 rows: 17 mined rows S114-S130 plus 5 supersession rows S131-S135) and removes none.
- `git diff --stat 7e5ff9b5 f4066979 -- SKILL.md corpus/SOURCES.md corpus/lessons/round-26.md registry/ .ufo/waves/round-26/sources/` is empty (exit 0). The `c1-tip.out` receipt at 7e5ff9b5 (`registered 17 counted 17 target 12 met True`) therefore covers the same gate files as the tip.

## Findings (by severity)

1. LOW: broken markdown code spans in 5 Gate rows. Rows S114, S115, S117, S118 and S121 (corpus/lessons/round-26.md:27, 28, 30, 31, 34) wrap a quote that contains backticks (`` `--slots` ``, `` `--slot-save-path` ``, `` `--props` ``, `` `--embeddings` ``, `` `--reranking` ``) in single-backtick spans. CommonMark closes the span at the first inner backtick. The rendered quote loses two backtick characters and splits into code / plain / code, so the rendered text is not verbatim even though the raw bytes are. SKILL.md:1083, 1084, 1086, 1087 and 1091 already use the correct double-backtick form for the same strings.
   Smallest correction: in those 5 cells, change `` `res->error(...)` `` to ``` `` res->error(...) `` ``` (double backticks with one inner space each side).
2. LOW / residual: S127 is exactly at the limit. The quote (round-26.md:40) is 25 words split on whitespace, but 26 if `std::invalid_argument` and `&` are counted by alphanumeric token. The fleet rule ("≤25-word located quote", CORPUS.md:114, templates/round-prompt.md:51) does not define a word, so it passes as written. Smallest hardening: cut the quote before `or a list of mixed strings &` so it is ≤25 under either count.
3. INFO: the Gate prose (round-26.md:14-15) says the sha256 is "in each row's anchor cell", but the Gate table has no anchor column. The sha256 values live in the SOURCES.md anchor cells, where all 17 match the fresh fetch. Optional wording fix: "sha256 in each row's SOURCES.md anchor cell".

No finding breaks C1's source grounding. Every anchor names the line that holds the signature, every quote is verbatim at that line in a fresh fetch, and the fresh bytes equal the snapshot.

## Residual risk and verification gaps

- E26-10 (S123): the anchored line 3657 holds the signature `is too large to process. increase the physical batch `. The emitted message continues on line 3658 (`"size (current batch size: %d)"`), so the URL names the first line of a two-line string literal. This is correct for the substring the counter matches, but the line anchor does not cover the whole message.
- I did not re-run the frozen counter or any live trigger; I had no port block. The live reproduction of E26-01..17 is unverified by this seat.
- The signature-uniqueness check covered only the 13 snapshot files, not the whole llama.cpp tree.
- `pgrep -af llama-server` at the end shows PIDs 1454822 (port 47734) and 1465723 (port 47740), both started by other seats. I started none.

## Files written

- .ufo/waves/round-26/w2-falsify/advice/ReviewerGateQuotes.md (this report)
- .ufo/waves/round-26/w2-falsify/out/ReviewerGateQuotes/check_gate.py (sha256 0ef32aae1476b0aae16ae1f7806f487d147802602f6a4499880ae6aae550bce9)
- .ufo/waves/round-26/w2-falsify/out/ReviewerGateQuotes/check_gate.out (sha256 a3c12180640e77d89b889df3604a91a3c7fb196653c71f99b77a69783d028509)
- .ufo/waves/round-26/w2-falsify/out/ReviewerGateQuotes/census.out (sha256 45c8037a0e02fed3bdb8f183d5bf3521236f9c7247044defc35bae0911ccc41d)
- Scratch: /fast/scratch/hyaku/kama-r26w2/ReviewerGateQuotes/ (fresh/ fetches, check_gate.py, check_gate.out, census.out)
