# ReviewerCounterCode — C1 counter vs its predicate sentence (round 28, wave 1)

Reviewed: `.ufo/waves/round-28/count-c1.py` as it exists now — **amendment A1**, sha256
`a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5`, 653 lines, commit `75b78bb`
("C1 amendment A1 (generic-conversion refusal in clause e) before any data row lands").
The preregistration was amended in the same commit: `counter_sha256` = a38faefe…, `counter_sha256_A0`
= e6a706bb… (the sha my ticket named), `predicate_A0` preserved, kill_rule rewritten (prereg line 17)
to declare A1 "the last amendment". All line numbers below are **A1 numbering (653-line file)** —
not A0's 619-line numbering.

Method: full static read; the counter module was imported in a bare Python process and its own
`same()`, `canon()`, `outcome_text()`, `conversions()`, `lookup()` were executed to demonstrate each
falsifier. The pinned llama-server was **not** run (bound). Two receipts under
`.ufo/waves/round-28/before/` (`pilot-A1-receipt.json`, `pilot-A1-xtc1.5-receipt.json`) are cited as
runtime evidence produced by others.

No tool installs were performed.

---

## HIGH

### H1. Clause (a) "verbatim" is enforced as substring containment — counted rows may display unverified text
- Code: `count-c1.py:468-471` — `field in cells[1]`, `value_text in cells[2]`, `otext in cells[3]`.
- Sentence (a): cells must hold the field "verbatim", the value cell "the canonical JSON … verbatim",
  the outcome cell "the row's canonical outcome text verbatim".
- Demonstrated with the counter's own functions: `canon(0) == "0"` and `"0" in "[0.0, 1.0] (server default)"`
  → True; canonical outcome `"reject 400, bounds 0 to 4294967295"` is contained in the padded cell
  `"reject 400, bounds 0 to 4294967295 (hard uint32 limit)"`; `"n_predict" in "n_predict (int32)"` → True.
- Impact: the SKILL.md table is the claim surface, but only the **registry** object is live-verified
  (`:598-626`). A row whose table cell misstates the value/outcome (the verified text merely embedded
  inside other text) still counts. Short canonical texts (`"0"`, `"1"`, `"true"`) are substrings of
  almost any cell, so clause (a) is effectively unenforced for the value/outcome columns.

### H2. No duplicate-id or shared-SKILL-row rule: one table row can produce two counts
- Code: `:464-473` — for each registry entry the matcher takes the **first** SKILL row whose `cells[0] == rid`
  (`break` at `:473`); the duplicate void (`:553-566`) keys only on exact `(source.file, source.line)`
  and exact `field`. Nothing voids two entries sharing an id, and nothing requires distinct SKILL rows.
- Attack shape: registry entries `F28-05` (field `n`, reject) and `F28-05` (field `n_probs`, effective)
  both match the same single table row whose cells contain both fields' substrings (trivial given H1),
  both values, both outcome texts, one ≥6-word meaning cell, and both S### tokens in the source cell
  (`:471` accepts any `\b`-bounded token list). Both entries count; the table displays one row.
- Sentence: (a) speaks of "one of its rows" per registry row and the claim says "One row per field and
  per declaring line"; two counted entries off one displayed row satisfy the code but not the sentence's
  table shape. (Distinct-line/distinct-field aliasing like `n` vs `max_tokens` is *not* voided either —
  see M6.)

### H3. Reject rows have no source-blindness guard, and the canonical guess IS a real bound
- Code: `:598-610` — a reject row needs only status 400, `REJECT_RE` group(1) == field, and bounds equal
  under `same()`. Clause (e) (`:611-626`) refuses source-blind outcomes **only** for `effective` rows;
  the sentence scopes (e) the same way.
- Evidence: `before/pilot-A1-receipt.json` row F28-90 — server message
  `Field 'n_cache_reuse': Value must be between 0 <= value <= 2147483647, but got -1`.
  `0..2147483647` is exactly the modal source-blind guess named in the prereg's own `source-blind`
  control ("reject with guessed bounds such as 0..INT32_MAX"). A writer who never opens
  `server-schema.cpp` can send `-1` (or any negative) to every integer field and, wherever the guess
  coincides with the real bound — as it does here — the row counts.
- The prereg control promises "counted < 18" for such a tree, but **no code mechanism** implements that
  promise; enforcement is by luck of the guess, not by the counter. Bounds like `0..2147483647` and
  `0..4294967295` are simultaneously the most guessable and (per the receipt) the most common real ones.

### H4. A1's clause (e) closed enumeration still counts clamp-to-semantic-bound rows — the pilot receipt itself is one
- Code: `:283-303` `conversions()` returns exactly {truthiness, ±FLT_MAX saturation, ±inf saturation,
  float32 rounding, truncation toward zero, wrap mod 2^32/2^64 signed/unsigned}; `:620-624` refuses
  `e:identity` and those conversions only.
- Evidence: `before/pilot-A1-receipt.json` row F28-91 — `xtc_threshold` sent **2.5**, live
  `effective = 1.0`, `base_effective = 0.10000000149011612`, `why: []` → **counted**.
  `1.0 ∉ conversions(2.5) = [True, 2.5, 2, 2, 2, 2, 2]` (verified by execution). 2.5→1.0 is a
  field-semantic clamp (xtc_threshold's max), i.e. precisely a "clamp-to-semantic-bound" outcome the
  prereg lists under source-blind strategies — and the A1 note (prereg line 41) says A1 exists because
  data seats found generic-conversion rows, yet the clamp channel survived.
- The sentence's stated purpose ("source-blind outcomes are not counted") is broader than its mechanism
  (the closed conversion list). A uniform "send 2.5 to every float field" policy still counts every
  clamp-type field: value ≠ sent, ≠ default, ∉ generic conversions. Note the prereg's own `pilot_A1`
  line cites `counted 2` as counter-validity evidence — the second count is a clamp row.

## MEDIUM

### M1. `same()` tolerance admits near-miss integer bounds/values far beyond float32 round-trip
- Code: `:253-258` — `abs(a-b) <= 1e-6 * max(1.0, abs(a), abs(b))` for all numbers, including JSON
  integers; reject-bounds comparison coerces the message's `\S+` via `float()` at `:605`.
- Demonstrated: `same(2**63, 2**63 - 4096) == True`; `same(float("18446744073709551615"),
  18446744073709550000) == True` (off by 2048 — both coerce to the same float64);
  `same(1000000, 1000001) == True`.
- Sentence (d): bounds "numerically equal (float32 tolerance) to the row's bounds"; (d)/(e) "float32
  tolerance for numbers". At int64/uint64 magnitudes the implemented tolerance is ~16 float32 ULP
  (float64-coerced), so a wrong 64-bit bound off by ~9e12 still counts. Directions: for reject rows the
  row's claimed bound need not be the server's printed text — just within 1e-6 relative.

### M2. The pilot exclusion is not enforced anywhere in the counter
- Prereg lines 21-24: `excluded_fields: [n_cache_reuse, xtc_threshold]`; claim text: excluded "so the
  pilot is not claim data".
- Code: `grep -i 'cache_reuse|xtc|excluded'` over the counter → **no matches**. A registry row for
  either field with fresh ids/S### rows is counted toward 18 (`before/pilot-A1-receipt.json` proves
  both fields produce counting rows). The counted set is therefore wider than the sentence's declared
  field set; `met` can flip on fields the round excluded.

### M3. `skill_rows` over- and under-collects relative to "the first table of the section"
- Code: `:209-224`. (i) After the header latches (`:219-220`), **every** later pipe-row under the same
  heading is collected (`:222-223`) — rows of a second table, or pipe-delimited prose, are all eligible
  for `static_checks` matches; sentence (a) restricts matches to rows *of the first table*.
  (ii) `inside` is toggled by any line starting with `#` (`:213-214`), including such a line inside a
  fenced code block — a table inside a code fence under the heading counts.
  (iii) Header comparison is case-insensitive (`:218-220`) while the sentence quotes an exact header.
  (iv) A row lacking its trailing pipe still yields 6 cells (`:465`) and matches.
  (v) Safe direction: a first table with a wrong header permanently disables collection (no reset).

### M4. Registry/`set`–field consistency has an ordering wrinkle, and malformed registries exit 1, not 0/2
- `:453` — `list(st) == [field]` requires the single key to be first **in insertion order**; JSON
  object key order is preserved by `json.loads`, so a valid single-key object always passes — no defect,
  noted for completeness.
- `:531` — `json.loads` on a malformed `registry/request-field-outcomes-r28.json`, or non-UTF-8
  SKILL.md/SOURCES.md (`:541-544`), raises an uncaught exception: exit code 1 with traceback and **no
  receipt**. The command contract (docstring `:42-44`) documents only exits 0 and 2; the `no-reader`
  control expects "exit 2 or counted < 18" — exit 1 is neither documented path.

### M5. SOURCES-row token checks are substring-only (sentence-strength, but weaker than it reads)
- Code: `:477-479` — `SCHEMA_FILE not in srow`, `COMMIT not in srow`,
  `re.search(rf"(#L{line}\b|\bL{line}\b|line {line}\b)", srow)`.
- `"server-schema.cpp"` is satisfied by `old-server-schema.cpp`; `"704366d"` by any longer hex string
  containing it. The line regex also accepts GitHub's `#L123` form, which the sentence's "(as \"L<line>\"
  or \"line <line>\")" does not literally name. The declaration check itself (`:484-490`) is exact and
  strong. Rank MEDIUM-LOW: the sentence says "names", which substring arguably implements.

### M6. The `duplicate-field` control's alias promise is not encoded
- Prereg control: "aliases (max_tokens, n) and several rows per field fishing for a hit -> every row of
  the field voided".
- Code `:553-566` voids only rows sharing the exact field string or the exact `(file,line)`. `n` and
  `max_tokens` are different fields on different declaring lines: both countable. The sentence's "one
  row per field and per declaring line" is satisfied (they are distinct fields), so this is a
  control↔code disagreement, not a sentence violation — but a falsify seat replaying the control's
  wording against the counter will find rows it expects voided.

## LOW

- L1. `lookup()` dotted traversal (`:306-317`): sentence says `generation_settings[<key>]`; code also
  accepts `"a.b"` nested paths (demonstrated: `lookup({"sampl":{"temp":0.7}}, "sampl.temp") → True`).
  A counted row's key need not itself be a `generation_settings` key. Flat key takes precedence;
  the clause-(e) default check uses the same lookup, so it stays self-consistent.
- L2. `e:default` is skipped when the key is absent from base `generation_settings` (`:618-625`,
  `if bfound and …`): an effective row whose key does not exist when the field is omitted counts without
  that half of clause (e) ever evaluating. A vacuous-truth reading of the sentence permits it; the
  sentence is underspecified here.
- L3. Canonical outcome text is code-invented (`:270`, `:275`: `reject 400, bounds A to B` /
  `200, key = V`); the sentence says "the row's canonical outcome text" without defining canonical.
  Combined with H1's substring rule the outcome-cell requirement is weak.
- L4. Live stringification is a counting transform: `same("8", 8) == False` and `"8" ∉ conversions(8)`,
  so an effective row whose key stores the request value as a **string** counts. Consistent with A1's
  closed enumeration; listed as residual risk, not a code defect.
- L5. `ID_RE = ^F28-\d{2}$` (`:94`) imposes an id format the sentence never states (safe direction:
  voids `F28-100`, `f28-1`). Ids are not required unique — see H2.
- L6. `REJECT_RE` (`:96-97`) uses `search` (prefix-of-longer-message OK) and `\S+` bounds; `float()`
  accepts `inf`/`nan` so `same(inf, inf)` could match an `inf` bound. Message-format drift fails safe
  (undercount). No `$` anchor needed given the sentence's trailing ellipsis.

## Amendment / process facts (no judgment encoded)
- During this review the counter changed under me: sha e6a706bb… (619 lines, commit `d8bf180`) →
  a38faefe… (653 lines, commit `75b78bb`, mtime 2026-10-23 05:37:36 -0300). The prereg was amended in
  the same commit (predicate, kill_rule, `counter_sha256`, `counter_sha256_A0`, `pre_data_amendment_A1`,
  `pilot_A1`). Per prereg line 41, A1 was written after the pre-freeze control call (`5ebe7b1b`) and
  after wave-1 data seats returned uncommitted drafts, before any data row was committed or scored.
- A1's code delta is refusal-only (adds `e:generic-conversion`, `:620-624`, plus the `conversions()`
  helper and receipt schema tag `v1-A1`); TARGET 18, `BASE_BODY`, `REJECT_RE`, `same()` tolerance, and
  all pins are byte-identical to A0 — the amendment cannot inflate the count. H4 shows what it does
  **not** refuse.
- This review targets A1. Any seat still quoting A0 line numbers (e.g. `counted` at A0:597 vs A1:631)
  should re-base.

## Positive verification (checked, holds)
- Base reads: `--no-replace-objects` on every git call (`:123-126`), `cat-file --batch` objects
  re-hashed (`:142-143`), `BASE` used as a full oid (`:151`), `row in src_base` voids reused S### ids
  (`:477`) — forged object stores and ref replacements are defeated.
- Process identity: pinned interpreter re-exec `-I -S` (`:495-500`), env equality (`:513-514`),
  `/etc/ld.so.preload` and mapped-file strays (`:184-197`); server identity: exe hash, impl.so mapping,
  environ equality, `/props` model path (`:375-399`); fixed port range 47600-47619 only (`:99`,
  `:326-330`); port-closed confirmation before exit (`:628-630`).
- `set`-single-key-equals-field (`:452-457`), per-line declaration check against the sha-pinned
  snapshot verified earlier in the same run (`:521-524`, `:484-490`), clause (c) newness
  (`:476-480`), duplicate line/field void (`:553-566`), live filter cannot promote a voided row to
  counted (`:567-569` + `:631` — every skipped row carries a non-empty `why`).

## Residual risk and verification gaps
- Reject-kind source-blindness (H3) and clamp outcomes (H4) are **structural**: no counter that only
  re-runs the server can distinguish a lucky canonical guess from schema knowledge. If falsify seats
  weigh these, the fix is predicate-level (e.g. refuse reject rows whose bounds equal the modal
  int32/uint32 constants, or require the row's value cell to name the bound literal from the pinned
  snapshot line), not code-level.
- H1+H2 mean `counted >= 18` certifies the registry + live server agreement, **not** that the SKILL.md
  table reads correctly. Falsify/review seats should diff SKILL cells against registry canon themselves.
- I did not run the server (bound), so reject-message-shape assumptions in `REJECT_RE` are verified only
  against the pilot receipts' captured messages (two samples, both matching).
- The two pilot receipts come from the scratch clone `/fast/scratch/hyaku/kama-r28/pilot`; I did not
  audit the clone's SKILL/SOURCES fixtures, only the receipts' live blocks and `why` arrays.
