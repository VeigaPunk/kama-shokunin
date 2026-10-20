# AttackEffective — KQ16 supersession parser (round 13)

Seat: KamaR13.AttackEffective, a leaf critic. Static reads only. I executed nothing: no measure.py, no fidelity.py, no gate, no selftest. I installed no tools.

## State at review

- `corpus/QUALITY.md` is unchanged: 8619 bytes and 49 lines. `git cat-file -s 941bb32:corpus/QUALITY.md` gives 8619, and the file ends with `|\n`. No KQ16 row exists yet.
- `.ufo/waves/round-13/measure.py` does not exist yet (`ls`: no such file).
- The findings below attack the designs in spec.json (Criterion, Measure and the shared contract). None is a defect in landed code. Re-check both files after they land.

## Counterexamples

| # | Attack | Evidence | Failure if not handled | Smallest control |
|---|---|---|---|---|
| A1 | Historical contradictory prose | KQ15 at `QUALITY.md:49` keeps "distinct nonzero exits" and "fetched directly as `git show …`". Line 45 says "No earlier criterion is superseded". The old bytes must stay as a prefix. | A whole-file negative check stays red forever. A parser not tied to a row can read KQ15 or line 45 as active. | Check the prefix first: final[:len(before)] == before. Then look for the KQ16 row only in final[len(before):]. |
| A2 | Absent row | The before blob has no KQ16. | A parser that returns "no active row, nothing to check" gives 0 missing on the before revision, a false green. | No row means both assertions are missing (2, exit 1). |
| A3 | Duplicated row | The parser selects one row. | With first-match or last-match selection, one good row hides a bad sibling, and the verdict depends on order. | Require exactly one `^\| *KQ16\b` row. `\b` excludes KQ160. Zero rows means 2 missing. Two or more rows is `documentation_mismatch`. |
| A4 | Literal outside the row | Measure says "active KQ16". Criterion might explain the change in prose below the table. | Literals in a paragraph, HTML comment, fence or erratum pass a section-wide search. | Search only the single KQ16 row line. A literal anywhere else counts as missing. |
| A5 | Wrong correction with the literal still present | The planned mutants are: drop the exit literal, drop the capture literal, reintroduce "distinct nonzero exits", remove the correction (spec.json Measure item). | The controls are asymmetric: proposition 2 has no reintroduction mutant. A row containing the correct literal plus `comparison: git show`, or plus `source_unavailable=1`, still passes. | Add these mutants: KQ15's "compared byte-for-byte with the blob fetched directly as `git show`" in KQ16; `comparison: git show` or `capture: git cat-file` next to the correct literal; any `(source_mismatch\|snapshot_tampered\|source_unavailable)=N` that disagrees with the map. Each must go red. |
| A6 | The negative check blocks a legitimate supersession | KQ16 has to name what it supersedes. | If Criterion quotes "distinct nonzero exits" to name the superseded wording, the row-scoped negative check gives a false red. | Criterion refers to it as "KQ15's exit-class clause" and never quotes it verbatim. Measure then forbids the phrase anywhere in the row. |
| A7 | No supersession pointer | KQ14's precedent is `KQ14 (supersedes KQ7's sufficiency, preserves …)` (`QUALITY.md:41`). `SKILL.md:382` sends readers to every appended criterion. | Readers apply KQ15 and KQ16 together and get contradictory exit rules. Both literals pass, but nothing says KQ15's clauses are retired. | Add a new round-13 heading. The ID cell names only KQ15's two clauses as superseded. This is checked as row identity, not as a third counted assertion, so the denominator stays 2. |
| A8 | Paraphrased bad wording | — | "three different non-zero exit codes" and similar wording slips past a literal check. | Use a bounded case-insensitive regex such as `distinct\s+non-?zero\s+exit`. Any remaining paraphrase goes to human review. State this residual openly. |

## Semantic correctness of the correction (needs human/source review; the probe cannot check it)

- **The exit map is right for the three IDs, but only partly.** `fidelity.py:24-26`: "0 clean; 1 source_mismatch; 2 snapshot_tampered, source_unavailable, snapshot_unavailable, manifest_invalid, unpinned or internal_error". Line 319 sets exit 1 only when the selected finding is `source_mismatch`.
- **Precedence limits the map (corrected after `KamaR13` review).** The map is about the primary `finding` only. The actual `PRIORITY` tuple (`fidelity.py:64-72`) is `snapshot_unavailable`, `manifest_invalid`, `snapshot_tampered`, `source_unavailable`, `source_mismatch`, `unpinned`, `clean`. `fidelity.py:317-319` takes the first matching ID as `finding` and sets the exit from that. Four exit-2 IDs (`snapshot_unavailable`, `manifest_invalid`, `snapshot_tampered`, `source_unavailable`) outrank `source_mismatch`. Exit-2 `unpinned` sits below it. My earlier "every exit-2 finding outranks" came from the inaccurate code comment at `fidelity.py:55-56` and was wrong. For example, a snapshot that is both mismatched and tampered has primary finding `snapshot_tampered` and exits 2, but a mismatch reports `source_mismatch` (exit 1) ahead of `unpinned`. `source_mismatch=1` therefore describes the primary-finding mapping only when no higher-priority finding is present. KQ16 should not imply the three entries are the whole exit map. Per `KamaR13`, the round-13 lesson marks the old comment inaccurate, and the historical code stays unchanged.
- **"capture: git show" is recorded testimony, not committed mechanism.** Committed code reads only with cat-file: `reproduce.py:80` and `fidelity.py:272,443`. `frozen/expected.json` records no capture command. The snapshot SHA-256 equals the source SHA-256 (`9dc40d25…`), so the bytes cannot show which tool captured them. The `git show` capture is recorded in round-12 `advice/Fidelity.md:19-20,37`, `SKILL.md:396` ("captured byte-exactly via `git show`") and `lessons/round-12.md:14-15`. KQ16 should present it as recorded one-shot provenance, and the comparison as the command the committed code actually runs.
- **"Independent" means a separate command and code path, not separate provenance.** Both commands read the same object database.

## Post-landing re-read of KQ16 (`corpus/QUALITY.md:52-63`)

Inspected statically. I used an in-memory Python read that compared `git cat-file blob 941bb32:corpus/QUALITY.md` with the working file and did substring tests. No gate, probe or fidelity code ran.

- The prefix is preserved: the before blob is 8619 bytes and the final file is 12128 bytes. The appended suffix contains exactly 1 `| KQ16` row.
- Both literals are in that row. KQ15's "distinct nonzero" and "fetched directly as" are absent. `comparison: git show` and `capture: git cat-file` are absent.
- A1, A3, A4, A6 and A7 are satisfied. The new heading at `:51` and the ID cell scope the supersession to KQ15's two clauses.
- The precedence wording is correct: `source_mismatch` exits 1 "only when it is the selected primary finding and no higher-precedence could-not-evaluate finding is present". Capture is labeled author-recorded and not reproducible from committed code.
- **Optional nit (sent to Criterion):** "documented finding precedence" could be read as pointing to the inaccurate `fidelity.py:55-56` comment. Naming the `PRIORITY` order at `:64-72` would be more precise.
- **False-red traps for Measure (sent):** the reject column legitimately says "distinct IDs are treated as requiring different exit codes". The admit column legitimately contains "`git show <pinned-commit>:<source-path>`" as the declared capture. The negative checks must target KQ15's exact clauses or `comparison: git show`, not these phrases.
- `measure.py` was still absent at re-read. A2 and A5 (the mutation controls) remain pending.

## Messages sent

- **To `KamaR13.Measure`:** A1–A5. The message asks for exactly one row, row search limited to the appended suffix, symmetric and contradictory-literal mutants, and literals outside the row counted as missing.
- **To `KamaR13.Criterion`:** A6, A7, the precedence/partial-map caveat, and the capture-provenance label.

## Limits

- This advice is static and pre-landing. No check was executed, and counts come from the commands quoted above.
- The literal probe remains textual conformance, not semantic proof. KQ14's human/source boundary governs.
- A8 leaves residual risk that a probe cannot close.
- Applying A3 or A5 does not change the fixed denominator of 2.
