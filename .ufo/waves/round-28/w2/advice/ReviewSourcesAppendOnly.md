# ReviewSourcesAppendOnly — frontier step 1 conformance (C1 SOURCES chain)

Verdict: **HOLDS.** No defect found in the sources append-only step; all
S140–S173 conformance criteria verified.

## Commands (both run; both exit 0)

1. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
   → exit 0. No E-class errors. Only `W04 duplicate url … across scopes`
   warnings for S141–S173 (and pre-existing rows S031, S043, … — same class).
2. `python3 tools/sources-append-only.py --from 4179301f --to e49b4cf77046024551ba83d490ef83d9dee061ed`
   (run from lane root) → exit 0, `added S140 … S173 (allowed)`, `no
   append-only violations`. Exactly the 34 claimed rows were added; no row
   removed, none mutated, no unexpected additions.

## Checks (S140–S173, all 34)

- **Each SOURCES row names server-schema.cpp and 704366d** — source cell
  exactly `llama.cpp tools/server/server-schema.cpp @ 704366d (b11755) — <url>`; anchor cell cites `server-schema.cpp line N (declaration `field`) @ 704366d76…`.
- **Own line** — anchor line N equals the Gate table line L for every row,
  and the pinned snapshot line L literally declares the field
  (`new field_num/field_json/field_bool("field"`), confirmed at
  `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`
  (603 lines; sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`,
  matches the claim pin). Spot-checked the cited limits/handler lines
  (L41/45/63 set_hard_limits; L231/319/414/445/460 handlers) all exist and
  belong to the field.
- **Scopes distinct** — 34 rows, 34 unique scope strings (each names its own
  field); census `E04 duplicate url within scope` absent.
- **Lesson Gate** — all 34 rows have: URL with full commit
  `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` and the row's own `#L<N>`
  anchor; access timestamp `2026-10-23T08:32:44Z…08:34:35Z` (ISO-8601);
  verbatim quote that equals the first ≤25 words of the whitespace-joined
  snapshot lines L and L+1 (word counts in the table match, max 25; the four
  seat-supplied non-verbatim quotes reported in the lesson were indeed
  replaced — quote text verified against the pinned file, not the seat
  drafts); opened-by `DataG##`; fetched sha256 prefixes `1f9d7b73b436…`.
- **Registry cross-check** — all 34 `request-field-outcomes-r28.json` rows
  cite `server-schema.cpp` and the line/field that matches their Gate row,
  and the `set` key equals the row field.

## Notes

- `W04 duplicate url … across scopes` on S141–S173 is expected, not a
  defect: 34 rows intentionally cite the same pinned file URL at the same
  commit, differing only in the `#L` anchor and scope (per-declaring-line
  design). S140 is the first-seen URL and is therefore not re-flagged. W04
  is a warning class ("warnings do not affect clean lanes") and the census
  exits 0.
- No tool installs were needed (no tooling directive record).

## Residual risk / verification gaps

- Quote verification uses the pinned local snapshot (sha256-matching the
  claim); the live GitHub fetch at 704366d76 is attested by the seat-recorded
  fetch sha in the Gate, not re-fetched here (network not needed).
- Census W04 exits 0; if a future rule promoted W04 to a failure, the
  one-file-per-line S-row design would trip it (pre-existing for
  server-context.cpp rows as well).
