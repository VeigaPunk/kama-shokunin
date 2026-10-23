# ReviewQualityAppend — round-28 KQ37 qualification block (repairs 2, 4, 5)

Seat: KamaR28.ReviewQualityAppend (leaf, w2 FALSIFY). Scope: the appended
`## Round 28 qualification -- KQ37` block at the end of
`corpus/QUALITY.md` (lines 264-277 at tip `e49b4cf7`), covering routed
repairs 2, 4, 5.

## Verdict: HOLDS — no actionable defect found

Every claim and quote in the block was re-opened at the tip and verified;
the block is append-only. No wrong, overstated, or harmful statement found
in scope.

## Evidence

### Append-only (repair gate)
- `git diff 4179301f e49b4cf7 -- corpus/QUALITY.md` is a single hunk
  (`@@ -260,3 +260,18 @@`) appending 18 lines at EOF after round-27 residual
  item 6; zero deleted lines. Block is the final section of the file
  (file ends at line 277 with item 4).

### Item 1 — S139 escape wording
- KQ37 row's S136 parenthetical exists verbatim at QUALITY.md:219:
  `(RFC 8259 §7 lets any character be a \uXXXX escape, S136)`; the block's
  "superseded" claim is accurate.
- S139 quote in the block is byte-exact vs `corpus/SOURCES.md:151` (read
  verbatim; identical except the blockquote `> ` prefix).
- S136 row (`SOURCES.md:148`) indeed says "any character of a JSON string
  may be written as a six-character \uXXXX escape" and names "Internet
  Standard STD 90" in its source field — so S139's teaches clause
  "(S136 said six characters for any character, and named STD 90 although
  the RFC text itself does not)" is accurate.
- Re-fetched RFC 8259 (`https://www.rfc-editor.org/rfc/rfc8259.txt`):
  sha256 `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7`
  matches S139's pinned raw hash exactly (fetched copy kept at
  `/fast/scratch/hyaku/kama-r28/w2/ReviewQualityAppend/rfc8259.txt`).
- RFC lines 433-440: "Any character may be escaped. If the character is in
  the Basic Multilingual Plane (U+0000 through U+FFFF), then it may be
  represented as a six-character sequence …" — matches "BMP six-character
  form". RFC lines 455-459: "To escape an extended character that is not
  in the Basic Multilingual Plane, the character is represented as a
  12-character sequence, encoding the UTF-16 surrogate pair." — matches
  "surrogate pair". Anchor line ranges are exact.
- RFC text contains no "STD 90" (grep: only STD 63/68 in normative
  references, lines 753/757), confirming the teaches clause.

### Item 2 — clause-(d) coverage correction
- `count-c1.py:338-340` defines `literal_texts` returning `lits` plus the
  concatenation `["".join(lits)]` when `len(lits) > 1`; `:565` tests
  `any(sig in t for t in literal_texts(lines[line-1]))`. The block's
  statement that clause (d) tests membership in candidates including the
  joined-literals concatenation, and therefore does not establish
  containment in one individual literal, is exactly correct.
- `corpus/knowledge/echo-discriminating-counters.md:121-126` indeed
  describes clause (d) as requiring a substring of "a regex-extracted
  literal on the cited line or of the concatenation of all literals on
  that line" — matches the block's citation.

### Item 3 — boundary-probe cost scope
- `boundary-leg.receipt.json:10-14`: predicate at 10; semantics at 11-18
  ("strings": JSON-decoded body keys and string values at every depth,
  length >= 4, no path/headers/argv; "comparisons": exact case-sensitive,
  no extra whitespace/case normalization). Matches the block verbatim.
- Existing cost `QUALITY.md:258-262` is round-27 residual item 6 (3/17
  genuine E26 rows), and entry `echo-discriminating-counters.md:127-132`
  states the same 3/17 cost with the same scope qualification — the block's
  "keeps the 3/17 cost qualified" claim holds.
- `CriticBoundaryLegProbe.md:41-43`: E26-14's decoded signature is the
  server-owned fixed literal, request key `prompt` occurs inside the
  signature span, and the refusal is described as an exercised offline
  counterexample, not a live run — matches item 3's open-question wording.

### Item 4 — round-26 defect-2 remainder and claim boundary
- `round-27.md:15-25`: C1 "withdrawn before data"; "No data seat was ever
  dispatched in this round"; counted < 15 reported as miss under the
  frozen kill rule.
- `a3/c1-tip.out:1-4`: line 3 `registered 0 counted 0 target 15 met False
  not-counted []` — matches the block's quote.
- `round-27-verifier-spotcheck.md:263-265`: defect 2 = "the counter has no
  F3 file-content echo leg. Commit one non-author shortcut-control receipt
  per named class before any data seat." — matches.
- `preregistration.json:10`: C1 surface is the request-field-outcomes
  table, not a signature counter — matches.
- `controls/HOLDS.md:3-20`: status column distinguishes evidential
  `receipt` rows from `HOLD — no receipt; never retried` classes (no-reader,
  object-store, all-false, echo, source-misuse at line 18); so the block's
  "those records do not establish an F3 leg" statement holds.

## Residual risk / verification gaps
- No live llama-server run was needed or performed (block is offline
  documentation/criterion text; port discipline untouched).
- The E26-14 lexical-coincidence question is intentionally left open by the
  block; that is a disclosed open question, not a resolved claim.
- Item 4's normative future requirement (F3 leg + per-class non-author
  receipts for any future signature counter) is a criterion statement — it
  is consistent with the lesson's repair-2 disposition ("closed as a
  criterion, not code") and adds no present-time F3 evidence.
- Tooling: no installs performed this seat (none required).
