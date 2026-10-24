# Revenger quarantine review — kama

Reviewed: 2026-10-24T23:48:48Z  
Axes: class-cell fidelity, row completeness, ID/lane integrity, provenance freshness.

## Outcome

**7 rows reviewed: 7 `specific-class-needs-hand-check`; 0 `prose-unverifiable`.** Every observed class cell is the specific class `` `payload-absent` ``, not prose such as “could not be fetched” or “named no locator”. This is a fabrication-risk triage verdict, **not** a finding that any quote is fabricated.

| Register line | ID | Lane cell (verbatim) | Class cell (verbatim) | Verdict |
|---:|---|---|---|---|
| 92 | S200 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |
| 93 | S202 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |
| 94 | S206 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |
| 95 | S210 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |
| 96 | S211 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |
| 97 | S224 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |
| 98 | S230 | `` `kama` `` | `` `payload-absent` `` | `specific-class-needs-hand-check` |

Integrity checks: **no missing IDs; no lane-cell deviations**. All seven source-register lane cells have the value exactly `kama`. No row has a prose class cell, so no row receives `prose-unverifiable`.

## Reconstructed classification contract

The register distinguishes a checked payload absence from an unchecked source. At lines 11–14, `` `payload-absent` `` is “the fabrication class” and requires hand verification, correction, or refusal; `` `unreachable` `` instead means the quote was never checked and must not be called fabrication. Lines 6–9 also make an ABSENT match a candidate, not a verdict. Accordingly, each `` `payload-absent` `` row above remains quarantined pending a hand-check before any append.

## Evidence chain

1. Read-only source: `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`.
   - Lines 92–98 contain the seven kama data rows enumerated above; every class cell is `` `payload-absent` ``.
   - Line 245 independently reports seven kama rows; that summary was not counted as a data row.
   - The “Rows whose quotes were NEVER CHECKED” section (lines 256–375) contains no kama row.
2. Scout provenance: `.ufo/waves/round-34/w1/out/ScoutAbsenceRegister/seat.log`, lines 64–99, contains the scout's completed report. Its raw slice at lines 85–93 has the same seven IDs, each paired with `` `payload-absent` ``; lines 69–79 enumerate the same ID/class pairs.
3. The verdicts above are direct applications of the register's class contract to those observed cells. No external source or quoted payload was fetched or hand-checked.

## Divergence and artifact status

The requested artifact `.ufo/waves/round-34/w1/out/ScoutAbsenceRegister/quarantine-slice` **did not exist** on repeated reads, including the final check at the review timestamp. A directory glob found only `seat.log`; therefore this report does **not** claim that the requested slice artifact was returned or directly verifies that absent file's contents.

**Inference, limited to artifact identity:** the intended slice is the seven-pair raw slice preserved in the scout log. That reconstruction is corroborated row-for-row by the source register. There is no class-cell disagreement between the two observed sources.

## Confidence and bounds

**High confidence** in the seven source-based verdicts and ID/lane checks; the missing-artifact limitation is explicit above. The register was not edited, no row was appended, no quarantine row was released, and no service/model-health claim is made.
