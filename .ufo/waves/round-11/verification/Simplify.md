# KamaR11.Simplify — advisory: served-identity crosswalk and measure.py

Status: advisory, non-author. No checks run (no `measure.py` execution, no selftest, no hashing). No implementation or corpus edits. Installs/updates: none. Reads and glob/grep only.

Scope read: `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md` (78 lines, tag #3826, unchanged during this review) and `kama-shokunin/.ufo/waves/round-11/measure.py`. The script changed while I was reading (tag #F616 → #B749, now 621 lines; new subprocess CLI cases, corrected case 5, new truncation and missing-file cases, reworded baseline-pin docstring). Everything below refers to the #B749 bytes.

## Findings (ranked)

1. **Medium — false-clean path in the live-claim wording guard.** `measure.py:108-109` (`NEGATION_WINDOW=24`, `NEGATION_RE`), `:135-143` (`_has_live_claim`), docstring `:53-55`.
   The negation exemption looks at the 24 characters before the match regardless of clause. Derived by hand from the code (not executed): `verified-at: 2026-10-20 — docs not changed; live revalidated today` matches `live revalidated today`, the window contains `not`, the match is skipped, and no `verified-at-live-claim` finding is emitted. The selftest never exercises the exemption branch: the default `verified-at` ("...no live revalidation") is not matched by the regex at all, and no case expects a negated-but-live-claim to pass or fail.
   Smallest repair: bound the window to the current clause (text after the last `;`, `,`, `.`, `—` or `(` before the match), or require the negation token immediately before the claim. Add two selftest cases: `docs not changed; live revalidated today` must fail with `verified-at-live-claim`; `not live revalidated today` must fail too (negation directly before is the only honest pass, and it should be the only pass).

2. **Low — duplicated finding logic that already diverges.** `check_provenance` `:286-304` and `check_crosswalk` `:348-370` each re-implement the trio missing/duplicate emission, the indented-hint, and the `verified-at` live-claim finding. Divergence today: only the provenance path increments `duplicate_fields` (`:293`); detail strings differ.
   Smallest repair: one `_trio_findings(rel, counts, indented)` helper returning `(missing, duplicate, findings)` and one `_live_claim_finding(rel, values, claim_re)`. Selftest asserts finding names and exit codes only, so unifying the detail text is safe. Net deletion is roughly 25 lines.

3. **Low — unverified output key.** `BASELINE_REVISION` (`:101`) is documented in-source as "informational only" and is emitted as payload `baseline_revision` (`:312`). No code checks it, and the module docstring payload description (`:30-34`) does not list it. A grep of `kama-shokunin` finds no consumer besides `measure.py`.
   Smallest deletion: drop the constant and the payload key; the revision is already stated in the docstring (`:62-64`). This changes payload shape, so note it in the handoff.

4. **Low — undocumented, miscounting payload key.** Crosswalk `table_rows` (`:342`, `:363`, `:373`) counts the separator row as a row and is not in the crosswalk payload list (`:33-34`). Smallest deletion: remove `table_rows`; keep `table` (0/1). Grep shows no other consumer.

5. **Low — docstring/code mismatch in table detection.** `_markdown_table` (`:180-190`) requires a leading `|` on both the row and the separator. The crosswalk docstring (`:75-76`) says "a separator line plus at least one pipe row". GFM tables without outer pipes fail closed as `missing-table`; this is a false alarm, not a false clean. Smallest repair: reword the docstring to "leading-pipe tables" (no behaviour change), or accept a non-leading separator regex and add one selftest case.

6. **Low — silently ignored flag.** `main` (`:597`, `:611-615`): `--baseline` is accepted and ignored in `crosswalk` mode. Smallest repair: `parser.error` when `--baseline` is given with `crosswalk`.

7. **Informational — claims the gate does not measure.** `REQUIRED_SOURCE_IDS` (`:112`, `:357-362`) only checks that each id appears anywhere in the text, including the body; it does not check the `source:` line, and nothing checks `SOURCES.md` rows. The crosswalk's KQ6 clearance (`served-identity-crosswalk.md:67`) asserts that every row "cites an opened `SOURCES.md` row". S031 (cited at crosswalk lines 1, 22, 77) is not a required id. No code change recommended for this wave; the report and handoff should state these as not measured, or the KQ6 clause should be attested by the reviewer rather than implied by the gate.

8. **Low — crosswalk repetition with a deletable subset.** The "not loaded / not readiness" caveat is restated in Claim (`:9`), the table cells (`:19-22`), Grounded failure cases 1–7 (`:26-33`), What cannot be concluded (`:43-46`) and kama use (`:56-58`). Cases 1, 2 and 5 of "Grounded failure cases" repeat table cells on lines 20, 21 and 22 (`[INFERENCE]` identifier-listing, router sleep/health, `ollama cp` name matching) and can be deleted without losing a distinct claim. Case 3 (tag without ps entry; absence at one sample is not conclusive) is not in the table and should stay. "What cannot be concluded" bullet 1 (`:43`) restates `:9`. The "Prior coverage" paragraph (`:13`) is the C2 credit claim and should stay.

## What is already correct (checked by reading)

- Crosswalk trio sits at column zero on lines 1–3, so the first-line flag (`True`) scans it.
- Cross-reference: `runtime-health-surface-matrix.md:42-57` (round-11 correction) exists and matches the crosswalk's claim that the S009/S010 cell is superseded by S011/S012 for native inventory semantics.
- "Five public documentation pages" (`:2`) is consistent with the S-list: S031 is the same page as S011, leaving OpenAI, llama.cpp README, Ollama OpenAI-compat, Ollama tags, Ollama ps.
- `measure.py` fence handling (`:161-163`), glued-first-line handling (`:157-160`), pinned-digest-before-measure ordering (`:235-240`), and `_safe_relative` (`:193-197`) behave as the docstring describes.
- Selftest case 5 now matches its label (mutated bytes on disk, original recorded in the baseline, `:462-469`); the earlier sibling critique (CodeSelftest) is resolved in this version.
- Exit codes `0/1/2` match the docstring across both modes.

## Gaps not addressed by any deletion

- Selftest exercises the CLI for only two paths (`:558-561`): crosswalk clean and provenance missing-baseline. The provenance success path through `main` is not covered.
- `advice/Simplify.md` (earlier advice, not this report) recommends deleting `measure.py` as a duplicate of a one-line grep. I do not recommend that: the C1 contract (`advice/ReviewContract.md:45,67`) requires the gate. Deletion is a scope decision for the parent, not a simplification.

## Smallest verification the parent should run after edits (not run by me)

- `python3 kama-shokunin/.ufo/waves/round-11/measure.py --selftest` (covers findings 1–2 and 5–6 once the new cases exist).
- Confirm the `BASELINE_SHA256` pin still matches the baseline bytes if the baseline or pin changes (not checked here).
