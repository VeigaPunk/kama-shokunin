# R39 Attack04 — S472 11-column shape and used-by path (executor, read-only)

Inspect of committed/working evidence only; no source byte was written or
mutated. All observations below are from the lane scratch working copy
`/fast/scratch/hyaku/kama-r39` (git base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`)
and the read-only source repo `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## 1. S472 row exists with the 11-column shape

`corpus/SOURCES.md:216` carries the S472 registry row:

```
| S472 | OpenAI List models — https://developers.openai.com/api/reference/resources/models/methods/list/index.md | docs | A | OpenAI model-card field semantics: creation metadata versus endpoint identifier; not local endpoint identity or readiness | §List models → Returns → `created`, line 17 (Markdown source fetched 2026-10-25) | `The Unix timestamp (in seconds) when the model was created.` | mined | 2026-10-25 | 90d | corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md |
```

- Header at `corpus/SOURCES.md:11` is `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |` — the row has exactly 11 content cells (12 pipe separators; awk cell-split yields 13 fields with empty leading/trailing cells). Column order matches the header: id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by.
- No literal pipe inside any cell (each of the 11 cells is a single field; the only pipe inside the row is the one in the source URL, which is a delimiter).
- `opened` is ISO `2026-10-25`; `recheck` is `90d`; `status` is `mined` — all consistent with the contract vocabulary used by prior rows.

## 2. Used-by path exactness

- used-by cell = `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`.
- That relative path resolves inside the repo: the file exists at
  `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`
  (working tree, untracked; `ls` confirms, 3994 bytes). The path starts with
  `corpus/` and is not a bare repo-root path.
- The file's `source:` header (line 1) names S472 and the same URL, and its
  line 25 section `## Round 39 opened-source correction — 2026-10-25` records
  that the API reference was re-opened as its Markdown rendition this round,
  with the located `created` description recorded in the round-39 lesson Gate.
- The full-repository validation mirror run is recorded in
  `.ufo/waves/round-39/assimilation/validate.out`: it printed `file ok
  /fast/scratch/hyaku/kama-r39/.ufo/waves/round-39/assimilation/validate/corpus/SOURCES.md`
  with exit 0 (only pre-existing W04 duplicate-URL warnings from other rows).
  The lesson Gate row 27 records the E11 incident: the first corpus-only mirror
  reported E11 for registry `used-by` paths living at repository root; the
  fix was to mirror full repository bytes (excluding only the mirror output
  subtree), place the candidate row in the Registry table, then validate.

## 3. Base-vs-tip presence

- At base `6a4afdfe…`: `git show 6a4afdfe…:corpus/SOURCES.md | grep -c S472`
  → `0`; `git grep S472 6a4afdfe… -- corpus/` → no hits (S472 absent).
- Working tree vs base: `git diff 6a4afdfe… -- corpus/SOURCES.md` = exactly
  **3 insertions** (the S472 row, the `Paths` bullet line `Served-card field
  semantics — S472: …`, and one blank separator line). `claim-after.out` line 3
  records the registry row count `203 → 204` (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`).
- The amendment file is new (untracked at tip); base had no tracked copy.

## 4. Claim posture

- C1 (calibration): the Gate in `corpus/lessons/round-39.md` (lines 17–29)
  contains one admit (the S472-sourced amendment, with the located 10-word
  quote) and two rejects (`staged runtime-health-surface-matrix-amendment-2026-10-24-r16.md`,
  `hosted-health-route-configuration.md`), each with a reason and flip. S472 is
  a newly opened source row this round and is cited by the admitted amendment.
- C2 (coverage): the coverage map in `corpus/README.md` names the amendment
  file; the file exists at tip and cites S472, which is absent at base.
- No falsification of the S472 row shape, used-by path, or Gate record was
  found on committed/working evidence.

## Evidence pointers

- `corpus/SOURCES.md:11` (header), `:216` (S472 row), `:220` (Paths bullet)
- `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md:1,25-27`
- `corpus/lessons/round-39.md:17-29` (Gate admit/reject, E11 mirror note)
- `.ufo/waves/round-39/assimilation/validate.out` (exit 0, W04 only),
  `claim-after.out` (rows 203→204), `census-end.out`, `preregistration.json`
- Independent base reads: `git show 6a4afdfe…:corpus/SOURCES.md`,
  `git grep S472 6a4afdfe… -- corpus/`, `git diff 6a4afdfe… -- corpus/SOURCES.md`
