# Draft text for corpus/lessons/round-21.md (LessonDraftC1; not filed)

## Mistakes

| ID | Class | Evidence | Captured-by | Fix / fail-capable evidence |
|---|---|---|---|---|
| M1 | Spliced full-hash citation: a 40-hex token assembled from two commits resolves to no object | `.ufo/reports/round-20/kama.md:7` token `0957ce619789d13d894ef21bc863486bcb35b56c`; `git cat-file -e <token>^{commit}` rc 128. The measured commit `0957ce619789d13bb5779606078fa1498114d2c7` is cited correctly at line 10 (rc 0). Errata row `registry/report-landing-errata.tsv:3` | non-author closure CloseKama20 (fleet `221707d`, defect D1), manual recheck; no mechanical object check before R21 | `tools/report-landing-audit.py` kind `unresolved-full-hash`: raw run names the token, exit 1 (`raw-run.txt`); selftest `mashup-detected`; correction recorded in the errata ledger, report not rewritten |
| M2 | Landed changes omits round commits that the lane log holds | `.ufo/reports/round-20/kama.md:13-19` lists five commits. Omitted: `33a6777866d0f63d894ef21bc863486bcb35b56c`, `0957ce619789d13bb5779606078fa1498114d2c7` (cited only at line 10 and the measurement table), `92b146253fd3a8c4bfade94c909dc63b13d6f4a8`, `846e366dc9dbac58463494a7e05ad060ae3ed3b0`. Rule: `templates/round-prompt.md:107-108` ("every change ... the commit hash that carries it") | non-author closure CloseKama20 (defect D2), manual; no mechanical coverage check before R21 | `landed-omitted`: raw run `round=20 required=9 defects=5` (one hash, four omitted); `cited_elsewhere` marks `0957ce6`; selftest `checkpoint-omission-detected` and `exact-defect-count` |
| M3 | Same omission class in earlier reports | r18: `101f3991d3570bc9350fbf9c5561f4be1185699d` (report line 19), `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` and `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (lines 26-27) are absent from `## Landed changes` (`.ufo/reports/round-18/kama.md:73-87`). r10: `40660352d4a9eb00a5d6195f0f064f5c64618143` is cited only in `## Post-review fixes` (`.ufo/reports/round-10/kama.md:114`), absent from `## Landed changes` (`:28-39`) | none: earlier closures checked report identity and that cited commits exist and are ancestors (e.g. `corpus/lessons/round-19-verifier-spotcheck.md`, table row "Cited commits exist"); no check tested Landed coverage | raw run `round=18 required=7 defects=3`, `round=10 required=2 defects=1`; errata rows `registry/report-landing-errata.tsv:8-11`; corrected run exit 0 |

## Round-20 report landing defects (narrative)

Round 20 was admitted by the non-author closure CloseKama20 (`221707d`). That closure
found two status-neutral defects and routed them to round 21: D1, the spliced hash at
report line 7, and D2, the four omitted round commits. Its existence and ancestry checks
passed, because every hash the report cited was a real commit. The defects were a
splice and an incomplete list, and no check tested either. Round 21 adds
`tools/report-landing-audit.py`, a stdlib audit of the fleet reports for rounds 10-20 with
four mechanical kinds. Raw run: exit 1, 9 defects (r10 1, r18 3, r20 5). Corrected run:
exit 0, with the 9 defects matched one-to-one by the append-only errata ledger
(`registry/report-landing-errata.tsv`, 9 rows). The fleet reports are not rewritten. The
audit does not judge prose. Its unresolved-full-hash check accepts any object of any type
for a full hash (code read, `is_object` called without a kind, not executed). It checks
coverage only for `kama-shokunin` commits whose subjects start `round-N:` or
`checkpoint(rN)`.
