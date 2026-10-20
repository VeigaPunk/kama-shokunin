# Sources — round 13 (S033 direct object-content comparison)

Lane owner: KamaR13.Sources. Write set used: `corpus/SOURCES.md` and this report.
No validator, gate, lane script, build, test, formatter or smoke command was run;
the only commands executed were a version query and read-only file/diff inspection.

## Files changed

`corpus/SOURCES.md` — three append-only additions:

1. Registry row **S033** immediately after S032, inside `## Registry`.
2. One **Search log** entry for the round-13 open.
3. One closing correction paragraph recording quote location, version facts, scope
   limits and the S032 recheck outcome.

Observed with `git diff --numstat -- corpus/SOURCES.md`: **4 insertions, 0 deletions**.
Row-shaped line count by `grep -c '^| S[0-9]'` moved **32 → 33**; the S033 row has
**11 cells** by pipe-field count. S001–S032 rows, Paths, and all earlier Search-log
entries are byte-unchanged.

## Opened sources — 2026-10-20 (UTC)

| Source | URL | Version evidence | Located exact quote (≤25 words) | Words |
|---|---|---|---|---|
| Git git-cat-file manual (new S033) | https://git-scm.com/docs/git-cat-file | Page selector: “git-cat-file last updated in 2.56.0”; 2.56.0 dated 2026-09-28 | §OUTPUT: “If `<type>` is specified, the raw (though uncompressed) contents of the `<object>` will be returned.” | 15 |
| Git git-cat-file manual, versioned page (cross-check, no new row) | https://git-scm.com/docs/git-cat-file/2.55.0 | Version 2.55.0 selector; page still shows “last updated in 2.56.0” | Same §OUTPUT sentence, verbatim | 15 |
| Git git-show manual (existing S032, reopened) | https://git-scm.com/docs/git-show | Page selector: “git-show last updated in 2.56.0”; 2.56.0 dated 2026-09-28 | §DESCRIPTION: “For plain blobs, it shows the plain contents.” | 8 |

Quote location matters: raw-object output is stated in **§OUTPUT**, not in
OPTIONS `<type>`. OPTIONS `<type>` states only that asking for a type that
“can trivially be dereferenced” is permitted (e.g. blob from a tag); it is not
raw-byte authority. The transformation caveat is documented under OPTIONS:
`--textconv` shows content “as transformed by a textconv filter”, and
`--filters` shows it “as converted by the filters configured in the current
working tree” (including smudge and end-of-line conversion), so neither may be
used for byte-exact object-content comparison.

Version facts: the host binary reports `git version 2.55.0` at `/usr/bin/git`
(`git --version`); the identical OUTPUT sentence is present on the 2.55.0 page.
This is a version fact only — no comparison of object bytes was executed.

## S033 row as landed (verbatim)

```
| S033 | Git git-cat-file manual — https://git-scm.com/docs/git-cat-file | docs | A | Direct object-content comparison mechanics for kama evidence: explicit-type raw output, not endpoint truth | OUTPUT “If `<type>` is specified” raw-contents clause; OPTIONS `<type>`, `--textconv`, `--filters`; manual last updated in Git 2.56.0 (2026-09-28), same sentence in 2.55.0, opened 2026-10-20 | An explicit `<type>` returns the raw, though uncompressed, object contents; `--textconv` and `--filters` transform content. [INFERENCE] Byte comparison must avoid both. The page documents command mechanics only; it is not evidence that any comparison ran and not endpoint truth. | mined | 2026-10-20 | on-release | corpus/lessons/round-13.md |
```

- id S033; kind docs; tier A; status mined; opened 2026-10-20; recheck on-release.
- scope: direct object-content comparison mechanics for kama evidence, not endpoint truth.
- anchor: OUTPUT “If `<type>` is specified” raw-contents clause; OPTIONS `<type>`,
  `--textconv`, `--filters`; manual 2.56.0 (2026-09-28), same sentence in 2.55.0.
- teaches: raw contents for an explicit `<type>`; transformation options documented;
  the avoid-both requirement is tagged `[INFERENCE]`; mechanics only, no run evidence.
- used-by: `corpus/lessons/round-13.md`.

The `[INFERENCE]` tag resolves ReviewRegistry F2: the page states that `--textconv`
and `--filters` transform content, not that a byte comparison must avoid them; that
consequence is lane method inference. The same inference status is now stated in the
closing correction prose for S032's “independently of a snapshot manifest” wording
(DESCRIPTION supports plain blob contents; DISCUSSION supports uninterpreted bytes;
neither attests an outcome, independence or correspondence). S032 row cells remain
untouched; no new row or claim was added.

## Scope and non-claims

- This row is **method support only**. Neither page states that a comparison is
  independent, that two retrievals occurred, or that any measured count moved
  1 → 0. Independence in round 12 is code/own-work evidence, not this document.
- No endpoint, runtime, serving, readiness, freshness or capability claim is made;
  no knowledge entry or frontier ground is added.
- Quality attribution is untouched: round-12 quality remains grounded in the D4
  `served-identity-crosswalk.md` interpretation, not in gate machinery; this row
  adds no quality delta.
- The S032 row was reopened but **no cell changed**: used-by old → new is
  `corpus/lessons/round-12.md` → same. The conditional permission to alter it was
  not exercised.
- S033's URL differs from S032's URL, so no duplicate-URL condition was added.

## Registry-validator dependencies (not executed here)

- E11: used-by `corpus/lessons/round-13.md` must exist at validation time.
  `test -e corpus/lessons/round-13.md` reported present after the lesson writer
  landed it; if L1 runs validation before that file exists, E11 fires. I cannot
  write the lesson (outside my write set).
- The round-13 lesson already cites S033 and reproduces the same 15-word quote in
  its Source-access section; this report supplies the curation record that lesson
  defers to `.ufo/waves/round-13/advice/Sources.md`.
- No `sources-census.sh validate` or `census` invocation was made by this seat.

## Search log effect

New entry (3 pages identified/screened, 1 new row included, 0 excluded, S032
retained unchanged): question was which documented Git command yields raw object
bytes for independent object-content comparison, as distinct from the `git show`
capture already registered as S032. Stop condition: raw-output semantics plus the
textconv/filters transformation caveat located; no broader Git or runtime claim
sought.

## Coordination

`KamaR13.AttackSource` objected before the row landed: (1) quote belongs to
§OUTPUT, not OPTIONS `<type>`; (2) teaches must stay method-only; (3) version
2.55.0 exists and host binary is 2.55.0. All three are incorporated above and in
the row; the versioned 2.55.0 page was opened and its OUTPUT sentence checked.

## Tools

Installed/updated: **none** (no installation was needed).
