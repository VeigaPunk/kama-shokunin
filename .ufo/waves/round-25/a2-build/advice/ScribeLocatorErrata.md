# Advice — ScribeLocatorErrata (round 25, attempt 2, routed defect 3)

**Verdict:** Round-24's only ScribeLesson/ConnSources mention is `kama.md:16`,
narrative with no on-disk locator; actual artifacts verified at
`fixes/docs/ScribeLesson/` and `falsify/out/ConnSources/verify.txt` under the
round-24 wave root; erratum draft written, original report bytes untouched.

## Scope and behavior

- Seat: `KamaR25a2.ScribeLocatorErrata`, leaf member; no subagent dispatch; no
  llama-server child started; no tools installed/updated; no production edits.
- Read the round-25 binding files (preregistration.json, amendments 1 and 2,
  count-c2.py, pilot.md, ATTEMPT-1-DISPOSITION.md) as required; this seat's
  claim is the locator erratum only, not C1/C2.

## Observations

1. Spot-check finding (the routed defect source):
   `kama-shokunin/corpus/lessons/round-24-verifier-spotcheck.md:109-111`:
   "The Root report's ScribeLesson/ConnSources evidence pointer is imprecise;
   the actual sources are `fixes/docs/ScribeLesson/` and
   `falsify/out/ConnSources/verify.txt`."
2. The round-24 report `.ufo/reports/round-24/kama.md` was searched in full
   (case-sensitive and case-insensitive `grep -n` over all 256 lines plus raw
   line reads). Only one text names ScribeLesson/ConnSources: `kama.md:16`,
   which describes the supersession headers and recovered guess patch
   narratively and cites `postfix/findings-disposition-01.json`,
   `evidence-qualification-02.json`, `hydration-qualification.json` and
   "final lesson" — no on-disk path to either artifact. That is the imprecise
   pointer; a reader cannot locate the evidence from it.
3. Corrected paths verified to exist (relative to the round-24 wave root
   `kama-shokunin/.ufo/waves/round-24/`):
   - `fixes/docs/ScribeLesson/` — 6 files: append-v1-labelled.txt,
     append-v2-labelled.txt, append-v2.txt, append-v3.txt, append.txt,
     supersession-index.json.
   - `falsify/out/ConnSources/verify.txt` — 7052 bytes, mtime 2026-10-21
     19:34.
4. Candidate wrong locations verified NOT to exist:
   - `sources/fixes/docs/ScribeLesson/` (there is no `sources/fixes/`; the
     `sources/` directory holds only S105.json and python-bytes-decode-reader.txt).
   - `build/out/ConnSources/verify.txt` (there is no `build/out/ConnSources/`
     directory; `build/out/ScribeLesson/` holds only the lesson draft).
5. Round-24 report bytes untouched (read-only seat); the erratum is a draft
   for the round-25 lesson, to be placed by the L1.

## Artifacts written

- `.ufo/waves/round-25/a2-build/out/ScribeLocatorErrata/erratum-draft.md` —
  proposed erratum paragraph plus the ls evidence with exit codes.
- `.ufo/waves/round-25/a2-build/advice/ScribeLocatorErrata.md` — this report.

No other files were written or modified.
