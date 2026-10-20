# Round 12 — SourceCorrections (D2/D4 registry prose)

Seat: `KamaR12.SourceCorrections` (leaf executor). Date: 2026-10-20 UTC.
Claim lane: C1 calibration historical-evidence repair only. No scalar increase,
capability, serving-readiness, live-host or upstream-behavior claim is made.

## Files changed

| Path | Change |
|---|---|
| `corpus/SOURCES.md` | This seat appended +4 lines, 0 deletions (blank separators plus the D2 and D4 paragraphs, now lines 65–68). No registry row, cell, heading or pre-existing line was edited by this seat. Concurrent sibling work added a `S032` row (line 44), a round-12 search-log bullet (line 59) and a closing quote note (line 70); total working diff is +8, 0 deletions. |

No other file was written. This seat added no source row: the `S032` row at line 44
is sibling/L1 work (row addition stays L1-owned), and the appended D2/D4 prose
does not depend on it. No verifier file, MANIFEST, fleet file, tool, registry or
host configuration was touched. No delegation, background job, commit, or
endpoint call was performed. Tools installed/updated: none.

## Behavior of the appended prose

The correction is dated `2026-10-20 (UTC)`, identified as verifier D2/D4 registry
prose, and opens by stating that no row/cell/line above changes and that it is
not an open lead.

- **D2 — registry scope and navigation.** States that the introduction's
  "every row was opened in round 10 (2026-10-19)" (lines 6–7) covers S001–S030
  only; S031 was opened 2026-10-20 (UTC), the actual review date of the steered
  round labelled 2026-10-19, and its `opened` cell carries that date. States that
  the Paths bullet "Served identity (next entry, K02)" is retained navigation
  text and that the K02 crosswalk has landed at
  `corpus/knowledge/served-identity-crosswalk.md`, so it is a present entry, not
  a pending one. The immutable header and Paths lines are untouched; the
  correction points at them without rewriting them.
- **D4 — inference and supersession.** Labels S031's consequence (that
  `/api/tags` membership does not prove local residency) as an inference from
  documented `ModelSummary` fields — `remote_model` ("Name of the upstream
  model, if the model is remote") and `remote_host` (the upstream Ollama URL) —
  so the quoted description is attributed to `remote_model` alone; records that
  the page's own summary still says "locally available" and that wording is not
  erased.
  States that the crosswalk remote-entry conclusion citing S031 carries the same
  inference status. States that `supersedes S011` is lane-registry supersession
  under `SOURCES-CONTRACT-v1`, confined to the local-residency implication, and
  is not a claim that upstream changed its documentation or withdrew S011's
  text; S011's non-status cells stay as written.

Four-section shape (`## Registry`, `## Paths`, `## Search log`,
`## Leads (unopened)`) is preserved; the appended prose adds no `##` heading and
sits after the existing leads exactly as assigned.

## Retained evidence (static, observed this session)

- `git diff --numstat -- corpus/SOURCES.md` → `8	0	corpus/SOURCES.md`
  (4 lines this seat: blank separators plus D2/D4; 4 sibling lines: `S032` row,
  round-12 search-log bullet, closing note plus its separator).
- `git diff -U0 -- corpus/SOURCES.md | grep -c '^-[^-]'` → `0` (insertions only;
  every pre-existing byte survives).
- `git diff -- corpus/SOURCES.md | grep '^+' | grep -c '^+## '` → `0` (no new
  heading).
- Original-byte preservation: `cmp` of HEAD lines 1–43 against current lines
  1–43 → identical. The sibling `S032` row is appended **after** `S031` at line
  44, so `S031` stays at line 43 and line 45 is blank; content below moves by
  one line (the Paths bullet moved 48→49). The sibling search-log bullet inserts
  later still, before this seat's append. No removed-line elements exist in the
  diff.
- `grep -n ' $' corpus/SOURCES.md` → no trailing-space lines.
- File state after sibling additions: 70 lines; 32 registry rows (static
  `awk` count: A=29/C=3; mined=22/queued=5/rejected=5); SHA-256
  `1f25e0022aaa037228c29e6abd572092934ed8a9da2a89eeafe185b059fd07d1`.
- Grounding read in-repo: header lines 6–7 and Paths line 49 (source of the two
  D2 statements; the Paths bullet was line 48 before the sibling row insertion
  and is identified in prose by text, not by number); S031 row `opened` cell
  `2026-10-20` and its `supersedes S011` text; `corpus/README.md:123` naming
  "K02's documented served-identity crosswalk"; presence of
  `corpus/knowledge/served-identity-crosswalk.md`; `round-11-verifier-spotcheck.md`
  D2/D4 routing and its verbatim `remote_model` description ("Name of the
  upstream model, if the model is remote") and its note that the upstream
  summary still says "locally available". The sibling closing note at line 70
  records the same `remote_model`-only quote attribution.
- Parser compatibility (static read): `scripts/sources-census.sh:611-621`
  ignores non-table lines outside `## Registry` and only flags row-shaped `|`
  lines there as E12. The appended lines do not begin with `|` and sit outside
  Registry, so they are inert to the census while remaining human-visible.

## Unrun checks (unrun ≠ pass)

I ran no validation, census, build, test, lint, formatter, smoke run, or
fidelity/reproduce invocation, per the lane's no-verification rule. L1 should
run once after integration:

1. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
   — expect `ok` plus the known scoped `W04 duplicate url docs.ollama.com/api/tags`
   warning; no `E01/E12`. Static row shape for `S032` is 11 columns and outside
   no section, so no new row finding is anticipated.
2. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`
   — expect 32 rows, A=29/B=0/C=3, mined=22/queued=5/rejected=5, per the static
   count above; this seat's append changes no count, and the one-row increase is
   the sibling `S032` addition.
3. Confirm the `S032` row (line 44) and the round-12 search-log bullet and closing
   note are sibling/L1 additions this seat did not author or alter, and that the
   round-11 frozen SOURCES snapshot (D1 artifact) was not touched. `S031` remains
   at line 43 because `S032` was appended after it, so a `SOURCES.md:43` citation
   for S031 is still correct; the crosswalk now cites rows by id regardless.

## Risks and boundaries

- The correction prose is intentionally inside `## Leads (unopened)` because the
  assignment required appending after the existing leads without a new heading.
  It is the section's first non-lead prose; the "not open leads" sentence and
  bold date tag mitigate misreading, but a future re-sectioning could relocate
  it without altering its content.
- D4's crosswalk half (explicit inference labeling inside
  `corpus/knowledge/served-identity-crosswalk.md`, grounded failure case 6) is
  outside this seat's write scope and was not edited by this seat. Peer
  `KamaR12.InferenceClarify` reports it landed at crosswalk lines 87–134 as
  "## Correction — round 12 D4 (authored 2026-10-20 UTC)"; a static read
  confirms the section labels line 29 and failure case 6 as [INFERENCE], labels
  S011's "locally available" implication the same, and states the line 1/line 84
  "supersedes S011's local-residency implication" phrases are
  `SOURCES-CONTRACT-v1` registry supersession only. Its wording agrees with this
  seat's appended SOURCES tail (inference from `remote_model`/`remote_host`;
  registry-only supersession; upstream wording not erased). A crosswalk line-offset
  concern this seat raised mid-wave is **not sustained**: `S032` was appended
  after `S031`, so `S031` remains at `corpus/SOURCES.md:43` (blank line 45) and
  `:43` never pointed at `S032`; the peer had already replaced line offsets with
  `§Registry row S031` / `§Registry rows S011 and S031` citations (crosswalk
  lines 100–101 and 115–116), retiring the drift class. No re-point is required.
  My D4 prose uses row ids and the stable header lines 6–7, so it has no
  shifting numeric anchor.
- No upstream page was fetched this round; the quoted remote-field description
  and "locally available" summary wording are taken from the committed round-11
  verifier spot-check and the crosswalk's own quoted row, both in-repo.
- This is advisory author evidence, not independent closure.
