# ReviewerSourcesContract — SOURCES row contract for C1 (read-only)

Seat: leaf reviewer, round 28 W1. Deliverable:
`.ufo/waves/round-28/w1/out/ReviewerSourcesContract/row-format.md`.
Nothing modified in the lane; no installs, no server, no scratch.

## Verdict

The row-format contract is fully derivable and internally consistent; the
worked S140 row in row-format.md satisfies counter clause (c) verbatim and
passes `sources-census.sh validate` clean (modulo unavoidable W04s). No
blocking findings. Two integration traps documented below.

## Evidence (all read at d8bf1804-era trees)

- **Column shape**: `corpus/SOURCES.md:9` header — 11 cells
  `id|source|kind|tier|scope|anchor|teaches|status|opened|recheck|used-by`,
  `NF==13` (`E01`); contract text `CORPUS.md:64-151`.
- **Clause (c) mechanics**: `count-c1.py` `sources_rows` (id → whole raw
  line, not registry-scoped) + `static_checks` line ~443: substrings
  `server-schema.cpp`, `704366d`, regex `(#L44\b|\bL44\b|line 44\b)`, id
  absent at base 4179301f. Clause (b) verified against snapshot
  `server-schema.cpp:44` = `add((new field_num("n_predict", params.n_predict))`
  (`new field_` + literal present; lines 45-48 carry limits/aliases/desc).
- **Line-citation convention**: S114-S130 (per-line `#L<n>` fragment rows,
  one error site per row — precedent for one-field-per-declaring-line);
  S137 anchor style `file lines x-y (throw at z) @ <full hash>; raw sha256`.
- **Validator**: `sources-census.sh` `url_of` strips scheme case/fragment/
  trailing slash; `scope_key=url SUBSEP scope`; `symbolic()` accepts any
  `^[A-Za-z][A-Za-z0-9 _-]*$` recheck; E11 used-by checked lane-dir relative
  for `mined` rows only; exit 0 with warnings, 1 on any E, 2 missing.

## Findings by severity

- **HIGH (integration trap, not a defect): E04 on repeated (url, scope).**
  All ~18 round-28 rows share one normalized raw URL (fragment stripped).
  Each row MUST carry a distinct `scope` (embed field name + line) or every
  later non-rejected row without `supersedes S###` in teaches is an E04
  hard error. Distinct scopes yield only harmless W04 warnings.
- **MEDIUM: E11 timing.** `mined` rows need used-by paths existing in the
  measured tree. Listing `SKILL.md, registry/request-field-outcomes-r28.json,
  corpus/lessons/round-28.md` is safe at the measured tip; integrating the
  SOURCES rows before the registry lands would leave dangling used-by —
  integrate in one commit or order registry first.
- **LOW: counter matches the raw row line, not the Registry section.** A
  `| S### |` row anywhere would satisfy `sources_rows`, but census E12
  forces `## Registry` placement anyway. Also `opened` must be ≤ the UTC
  validate date — `2026-10-23` is safe.
- **LOW: W04 noise.** ~17 rows emit `W04 duplicate url … across scopes`;
  exit stays 0. Do not "fix" by varying the URL (normalization defeats it)
  or by sharing `scope` (converts to E04).

## Residual risk / verification gaps

- Worked example traced statically only; `count-c1.py` not executed (no
  server run authorized for this seat, and the row's truth depends on the
  L1's integrated registry which does not exist yet).
- `used-by` lists `corpus/lessons/round-28.md`, which the L1 must create;
  if the lesson lands under a different path, adjust used-by or the row
  earns an E11.
- Gate entries for all ~18 rows must each carry URL + access date +
  ≤25-word quote (contract rule 1); row-format.md gives the per-row
  recipe — the Gate bulk entry is the L1's work.

Report: .ufo/waves/round-28/w1/advice/ReviewerSourcesContract.md
