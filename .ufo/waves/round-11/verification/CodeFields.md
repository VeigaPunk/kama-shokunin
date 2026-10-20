# CodeFields — advisory review of measure.py lines 130–310 (field/prefix scanner)

Author seat: `KamaR11.CodeFields` (leaf reviewer, advisory, non-author). Outside non-author review remains separate.
Subject: `kama-shokunin/.ufo/waves/round-11/measure.py` lines 130–310 (`_live_claim_re`, `_has_live_claim`, `_scan_supplement`, `_markdown_table`, `_safe_relative`, `_valid_entry`, start of `check_provenance`). Module docstring lines 36–58 and 60–69 were read as the contract the code is judged against.

## Method and scope
- Read-only inspection: file reads, `grep` of `corpus/knowledge/` for column-zero trio lines, `verified-at` values, `^~~~` and four-backtick fences, and a read-only JSON load of `legacy-baseline.json` and `verification-spec.json`.
- `measure.py` was **not executed**. Every regex and loop trace below is a hand trace of the source; the traces are marked `[HAND-TRACE]`.
- No implementation, corpus, or fleet file was modified. No endpoint, host config, network, or service was touched. No public URL was opened (this seat is not a source role).
- Installs/updates: **none** performed by this seat; no install record to report.

## Findings by severity

### F1 — medium — False negative: negation window bleeds across clauses
- Location: `measure.py:107` (`NEGATION_WINDOW = 24`), `:134–142` (`_has_live_claim`), specifically `:138–140`.
- Defect: the 24-character look-behind is not clause-bounded, so a negation in a previous sentence suppresses a real live claim.
- `[HAND-TRACE]` input `verified-at: No drift observed; live revalidated today.` → normalized match starts at index 19; the 24-char window is `"no drift observed; "`; `\bno\b` matches → `continue` → payload reports no live claim. The affirmative claim passes the gate.
- Same effect for `Not fully checked. Live revalidated today.`
- Contract tension: the docstring (`:53–55`) documents the 24-char negation check, so this is a documented-window behavior, but cross-sentence suppression is a false negative against the stated purpose ("must not claim live revalidation dated today").
- Smallest repair: reset the window at the last clause delimiter, e.g. `window = re.split(r"[.;:!?()]", normalized[:match.start()])[-1][-NEGATION_WINDOW:]`, keeping the 24-char cap. Add the same delimiter reset in the docstring.

### F2 — medium — False negatives: phrasing outside the literal claim set
- Location: `measure.py:127–129` (`_live_claim_re`).
- Defect: the guard recognises only `live revalidated|revalidation|revalidated live` followed by `today` or the date with whitespace-only separators. `[HAND-TRACE]` the following affirmative claims are NOT flagged:
  - `verified-at: live re-validated today` (hyphenated `re-validated` is not `revalidated`);
  - `verified-at: verified live today` / `checked live today` (no `live revalidat*` token);
  - `verified-at: live revalidated as of today` (`as of` between phrase and date is not allowed);
  - `verified-at: live revalidated (2026-10-20)` (`(` is not `\s`);
  - `verified-at: 2026-10-20 live revalidated` (date precedes the claim; the pattern is claim-then-date only).
- The module docstring (`:50–58`) concedes exotic rephrasings "pass unexamined", so these are known limits, but the listed forms are ordinary wording and the guard is the only freshness control in the value field.
- Smallest repair: widen the claim stem to `(?:re-?validated|verified|checked|confirmed)` paired with `live`, allow separators `\W{0,4}` and optional `(?:on|at|as of|dated)` before the date, and add the date-before-claim order `RUNDATE[^;.]{0,40}live` as a second alternative. Add fixtures for each form in `--selftest` (out of this lane region; noted for the parent).

### F3 — low — Undercount of `missing_fields` for a missing legacy file
- Location: `measure.py:259–265`.
- Defect: when a baseline-listed file is absent, the code records one `missing-file` finding and `continue`s, so its three trio fields are not added to `missing_fields`. The contract metric is "27 provenance fields → 0"; a missing file contributes 0 to that count while being 3 absent fields. `ok` is still false, so the gate verdict is correct; only the reported count is understated.
- Smallest repair: `missing_fields += len(REQUIRED_FIELDS)` in the `FileNotFoundError` branch, or document that `missing_fields` excludes absent files.

### F4 — low — False positive: post-match negation ignored
- Location: `measure.py:138–141`.
- `[HAND-TRACE]` `verified-at: live revalidated today — not performed` → window before the match is empty → flagged. An honest, disavowing sentence is reported as a live claim. The docstring's honest-negation examples (`:55–57`) are all pre-claim negations, so this is a gap between documentation and behavior.
- Smallest repair: also inspect a short post-match window for a negation, or document that post-match negation is flagged.

### F5 — low — Negation token gaps
- Location: `measure.py:108` (`NEGATION_RE`).
- `cannot` is not matched: `\bnot\b` cannot match inside `cannot` (no boundary between the two `n`s), so `cannot claim live revalidated today` is flagged (false positive).
- Curly apostrophe `n’t` (U+2019) is not matched because `normalized` does not fold apostrophes, so `isn’t live revalidated today` is flagged (false positive).
- Smallest repair: `NEGATION_RE = re.compile(r"n['’]t|\bcannot\b|\b(?:not|no|never|without|non)\b")` with `normalized` folding `’` to `'`.

### F6 — low — Fence state is not derived from the original file; fence toggles are fragile
- Location: `measure.py:156–164` (`in_fence` starts `False` and toggles on any line whose `strip()` begins with three backticks), `:279–282` (scan of `region` only).
- Defects:
  1. `in_fence` always starts `False` at the appended boundary. If an original legacy file ends inside an open fence, the appended supplement is rendered as code by Markdown, but the scanner counts its column-zero trio lines (false negative on the gate).
  2. A four-backtick fence containing a three-backtick line is toggled closed early, so later lines inside the block are counted.
  3. `line.strip()` makes indented (4+ space) backtick lines toggle state, though those are code-block text under Markdown.
  4. Tilde fences `~~~` are not recognised. The contract text (`measure.py:43`) says "outside triple-backtick fences", so tildes are literal-contract-conformant; they are flagged for completeness only.
- Corpus evidence (read-only grep): `^~~~` and `^````` returned no matches under `corpus/knowledge/`, and no legacy supplement contains a fence line. These defects are latent, not present, on the current 9 files.
- Smallest repair: derive the boundary fence state by running the same toggle over the original bytes (or `data[:original_bytes]`), pass it into `_scan_supplement` as a parameter, and use a fence-length-aware closer rule (closer has ≥ opener backticks, no info string). Keep the glued-line skip as is.

### F7 — low — Only the first `verified-at` occurrence is checked for live claims
- Location: `measure.py:168` (`values.setdefault`), `:299–300`.
- Defect: a supplement with an empty or neutral first `verified-at:` and a second `verified-at:` containing a live claim is reported only as `duplicate-field`; the second line's live claim is never evaluated. Duplicates already fail the gate, so the verdict is unaffected, but the `verified_at_live_claims` count is incomplete.
- Smallest repair: collect all `verified-at` values into a list and run `_has_live_claim` over each.

### F8 — low — Ambiguity: column-zero prose lines count as trio fields
- Location: `measure.py:165–169` against the contract text at `:41–44` ("Body occurrences are not part of the trio").
- The scanner counts every column-zero `source:`/`verified-at:`/`recheck:` in the appended region, including a soft-wrapped prose line that happens to start with one of those words. The contract's "body occurrences" wording could be read as excluding such lines.
- Corpus evidence: none of the 9 supplements has a prose line starting with these words (the column-zero trio lines are exactly the three field lines per file, located at the supplement tail).
- Smallest repair: decide the contract meaning. If body lines must be excluded, count only the first contiguous block of field lines after the heading. Otherwise leave the code and document the rule in the docstring.

### F9 — low — Dead clause in `_safe_relative`
- Location: `measure.py:192–196`.
- `Path(rel).parts` drops `""` and `"."` components, so `all(part not in ("", "."))` never fails. `./corpus/x.md` and `corpus//x.md` are accepted. The `..` rejection (`:196`) works, so no traversal escape is opened by this clause.
- Smallest repair: test the raw string: `if any(seg in ("", ".") for seg in rel.split("/")): return False`.
- Related note (outside this region, check_provenance `:260`): `root / rel` follows symlinks; `_safe_relative` does not check that the resolved path stays under `root`. The baseline is pinned, so exposure is limited to repo-owned symlinks.

### F10 — low — `_markdown_table` counts table-looking lines inside fences and loosely detects separators
- Location: `measure.py:179–189`, used by `check_crosswalk` at `:362`.
- Defects: (a) no fence awareness, so a pipe table inside a code block counts as `table=1` (false positive); (b) separator detection requires only a `-` and characters in `|-: ` (`:187`), so a data row of dashes or a row with a tab inside the separator (`|\t---|`, tab not in the charset) is classified differently than intended; (c) the separator itself is counted in `rows` (`:185–186`), so `table_rows` overstates data rows; the docstring's "a separator line plus at least one pipe row" is satisfied by a header+separator pair with no data row.
- Smallest repair: skip fenced lines, require a header row immediately above the separator, exclude the separator from `rows`, and use `re.fullmatch(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?", stripped)` for separators.

### F11 — info — Documentation/implementation wording mismatch on the claim pattern
- Location: docstring `measure.py:52–53` ("immediately followed by `today` or the run date") versus pattern `:129` (`\s+(?:on\s+)?<date>`).
- The pattern allows an optional `on`, which is a harmless broadening, but the docstring says "immediately followed". Update the docstring to list the accepted forms, or narrow the pattern. `re.IGNORECASE` at `:130` is redundant because `normalized` is already lowercased (harmless).

## What is already correct (verified by hand trace)
- Glued-first-line handling: `_scan_supplement` skips index 0 when the original does not end in `\n` (`:158–159`, `:279–280`); this matches docstring `:45–49` for the heading and for trio lines. A glued `## Provenance supplement` is correctly not a heading.
- Indented `source:`/`verified-at:`/`recheck:` are excluded from counts (`:170–173`) and only produce a hint (`:288`), as the contract says.
- Fenced trio lines and fenced heading lines are excluded for triple-backtick fences (`:160–164`, `:163–164`).
- Prefix guard: `prefix_ok` requires `len(data) >= original_bytes` and an exact sha256 over the original extent (`:271`); region is taken only after that extent (`:278`).
- Date boundary: `(?![0-9])` (`:129`) correctly lets `2026-10-20T02:14Z` match and blocks `2026-10-200`.
- Negation token `n't` and `\b`-bounded `not|no|never|without|non` correctly avoid matching inside `note` (`:108`).
- `_valid_entry` rejects bool (`type(size) is int`, `:206`), non-hex digests (`:204`), and negative sizes.
- `..` traversal is rejected by `_safe_relative` (`:196`); backslashes and absolute paths are rejected (`:193`).
- Corpus state (read-only grep): all nine legacy supplements carry exactly one column-zero `source:`, `verified-at:`, and `recheck:` each (served-model-identity at lines 40–42; listener-census at 385–387; the rest at the supplement tail). No `verified-at` on the nine files contains an affirmative live claim (every `live revalidation` mention is followed by `claimed`, `is claimed`, `, no ...`, or similar, so the regex does not match). The current result of zero live-claim findings on these bytes is consistent with the contract.

## Residual risk and verification gaps
- The live-claim negation branch (`:139–140`) is **not exercised** by any current corpus line: none of the nine `verified-at` values contains a `live revalidat*` phrase followed by `today` or the run date. A zero result on these bytes therefore does not show the negation logic works. Coverage must come from `--selftest` fixtures; this seat did not inspect selftest (outside region) and did not run it.
- No trace was executed; hand-trace results above are `[HAND-TRACE]` and should be confirmed by the parent's acceptance run, not by this seat.
- Crosswalk parity (`check_crosswalk` at `:326+`) is outside this region; F10 touches it only through `_markdown_table`.

## Suggested next steps for the parent (not performed here)
1. Decide F2 and F8 wording against the contract before editing; F1, F3, F4, F7 have unambiguous smallest repairs.
2. Add selftest fixtures for the F1, F2, F4, F5 traces above.
3. Rerun the provenance acceptance after any change; this seat did not and will not run it.
