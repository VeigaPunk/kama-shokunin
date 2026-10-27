# Q03CorpusContract — S512/S513 review

**Verdict:** S512 and S513 conform to the SOURCES append-only and Gate requirements in fleet `CORPUS.md` (rules 1–2), with a non-blocking metadata discrepancy noted below.

## Evidence

- The frozen round-56 lesson `corpus/lessons/round-56.md` has a `## Gate` entry for each row (lines 12–15). Both give the source title and URL, access date 2026-10-27, snapshot path, quote location, a quote, disposition, and rationale. S512's Gate entry grounds the admitted LD_AUDIT claim; S513's Gate entry records why the alternative is rejected and a condition that would change the decision.
- At freeze `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`, both rows are present in `corpus/SOURCES.md` (lines 265–266); each is a well-formed 11-cell table row (`NF=13` when split on `|`). S512 is `mined`, with `corpus/lessons/round-56.md` in `used-by`; S513 is `rejected`, carries the required `REJECTED: ...; flip: ...` teaching cell, and has `—` for `used-by`.
- `git diff e10b6d39af450e8d652be9ac2986768b531fe13f efc6b3ec6fb6ea308c15855e9b8b62856f4255b7 -- corpus/SOURCES.md` shows S512 and S513 added after S511; it does not show existing rows edited. This supports append-only conformance for this base-to-freeze interval. It also shows two blank lines after the additions, a harmless formatting detail.
- The cited snapshots exist under `.ufo/waves/round-56/sources/`. S512's quote is present in `rtld-audit.7.html` lines 89–94 (HTML bold markup splits “LD_AUDIT” from “must”). The S513 quote appears in `ld.so.8.html` lines 380–385 across wrapped lines. Literal byte-for-byte quote searching returned false because the HTML markup/wrapping interrupts the strings; the relevant displayed text is present.

## Defect / caveat

The round-56 Gate labels the S513 quotation “(16 words)”, but counting the quote as written yields 18 whitespace-delimited words: “A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace”. This does not violate CORPUS.md's ≤25-word quote limit, and does not affect append-only or Gate completeness; it is a word-count metadata error. Proposed fix: correct the count to 18 in a future append-only lesson correction, rather than rewriting the frozen lesson.

## Unresolved scope

This verifies the base-to-freeze diff and Gate/source evidence. It does not establish the complete prior history of `corpus/SOURCES.md` beyond that interval or independently verify the live web access event.