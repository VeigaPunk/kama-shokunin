VERDICT: partial — The contract is explicit; the census validator only partially enforces supersession formatting.

## Findings by severity

### Low — E04 accepts a supersession marker that is not at the start of `teaches`

The contract requires a correction's new row to open `teaches` with `supersedes S0NN —`, while the duplicate-URL/scope exception in E04 only searches for that marker anywhere in the cell. A row can therefore evade E04 with preceding prose. [INFERENCE]

- Contract: `/home/vgpnk/Projects/shokunin/CORPUS.md:116-118` — “a correction is a new row whose `teaches` opens `supersedes S0NN —`.”
- Validator: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:646-649` — `teaches !~ /supersedes S[0-9]{3}/`.

## Contract readout for new rows and lesson Gate entries

- The lane header names `SOURCES-CONTRACT-v1`, the one Registry table, and the table's 11 fields: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by` (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:1-12`; contract shape `/home/vgpnk/Projects/shokunin/CORPUS.md:78-108`).
- A new row is written only after opening that source in the round that writes it. Use the next unused `S` ID with at least three digits (S048 is next after the reviewed S047); no `|` inside cells. `source` is title plus canonical URL/DOI, or a repo path/command for `own-work`; `kind` must be one of `spec`, `docs`, `paper`, `code`, `tool`, `dataset`, `talk`, `book`, `community`, `own-work`; set a scoped claim in `scope`; pin `anchor` to exact section/heading/page/line and revision (version, commit, or publication date), never just a homepage; make `teaches` one grounded learner benefit; select `queued`, `mined`, or `rejected`; record the author's ISO opening date and a recheck date/cadence; and set `used-by` to repo-relative citing knowledge/lesson paths or `—`. Rejected `teaches` must use `REJECTED: <reason>; flip: <what would change the verdict>`. Evidence: `/home/vgpnk/Projects/shokunin/CORPUS.md:89-108` — “anchor — exact section / heading / page / line plus revision”.
- For each new row, its round lesson's `## Gate` records the URL, access date, and a located quote of at most 25 words that grounds `teaches`; non-author verification reopens a sample. Evidence: `/home/vgpnk/Projects/shokunin/CORPUS.md:112-115` — “URL, the access date, and a ≤25-word quote with its location grounding `teaches`.”

## Tiers: code, docs, and RFC/spec

`kind` and `tier` are separate: `code`, `docs`, and `spec` are allowed kinds. Tier is assigned per `scope`, not globally. Tier A is only for a primary or authoritative source for that scope, with the contract's examples including a spec/RFC, official docs, and source code; B is strong secondary evidence (expert reproducible write-up, survey, textbook); C is a lead only and cannot be sole support for an admitted entry. Community sources are never A; tiers are curation, not truth grades. An RFC is represented as `kind=spec`; the contract does not give an RFC-status shortcut, so its authority must be judged for the stated scope. [INFERENCE]

Evidence: `/home/vgpnk/Projects/shokunin/CORPUS.md:91-97` — “A: primary or authoritative for that scope (spec, official docs, source code...)”. Current examples distinguish `docs` (S040), `code` (S042, S043, S047), and `own-work` (S041, S046), all tier A but narrowly scoped: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:52-59` — “not router mode” (S047).

## Supersession discipline and current examples

Only `status`, `recheck`, and `used-by` may change in place, and each such change is logged old→new in the round lesson. A correction is a new row whose `teaches` starts with `supersedes S0NN —`; do not rewrite the old row. Evidence: `/home/vgpnk/Projects/shokunin/CORPUS.md:116-118` — “Only `status`, `recheck` and `used-by` change in place”.

The reviewed rows illustrate the intended scope: S040 replaces S021 after its recorded page returns 404; S041 and S046 are pinned lane-run receipts; S042 and S043 are code-derived claims at llama.cpp commit 704366d76; S044 covers Python 3.14 child return-code interpretation; S045 records PIT's mutation vocabulary; S047 narrows/corrects S043 for the interval after signal-handler installation but before task-loop start. S047 retains a distinct source URL (`server-queue.cpp`) and pins the server-side ordering too. Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:52-59` — S040 “supersedes S021”; S047 “supersedes S043”. A round-18 Gate entry for S047, as well as Gate entries for any new S048+ row, still needs the URL, access date, and located ≤25-word quote.

## Census validator coverage

`validate` checks: E01 malformed row/column count; E02 ID shape; E03 duplicate IDs; E04 duplicate URL+scope without a supersedes marker; E05 kind enum; E06 tier enum; E07 status enum; E08 opened date invalid or in the future; E09 invalid recheck; E10 community at tier A; E11 missing used-by paths for mined rows; E12 source-shaped rows outside `## Registry`. Warnings are W01 tier-C mined with non-dash used-by; W02 a rejected row with a thin `teaches` (<8 characters); W03 mined with `used-by=—`; W04 same URL across scopes. Evidence: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:24-33` — “E01 malformed row (NF!=13)”.

Other modes: `census` reports row, tier, status and missing-registry counts; `overdue` reports date/`NNd` rechecks due on or before today and reports symbolic cadences without judging them overdue; `shared` reports normalized URLs present in at least two lanes. The parser accepts 0–3 leading ASCII spaces before rows/headings; 4+ spaces are treated as indented code. Exit contract: 0 clean or warning-only, 1 E/overdue findings or census missing, 2 usage/environment/missing-registry error, 3 selftest failure; W findings do not fail validation. Evidence: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:12-18` — “W-codes and unlisted lanes never change status”; `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:34-42` — “symbolic cadences ... are reported, never judged overdue.”

## Residual risks and verification gaps

- The validator checks the `opened` cell's date format and that it is not future-dated, but cannot establish that the author actually opened the source in this round. It also does not inspect lesson `## Gate` content or validate that its quote is located and supports `teaches`. Those are contract requirements and require content review. [INFERENCE] Contract evidence: `/home/vgpnk/Projects/shokunin/CORPUS.md:112-115` — “Write it only after opening the source in the round that writes the row.” Validator evidence: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:626-629,660-668` — `opened_epoch=epoch(opened)`.
- E04's supersession exception only recognizes the marker substring and does not verify the exact prefix or that its referenced prior row is the intended correction. The prefix gap is the Low finding above; target correspondence is not checked by this predicate. [INFERENCE]
- No validator, test, or lane measurement was run; this is a read-only contract/script review. No tools were installed.
