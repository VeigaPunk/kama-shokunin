# ReportSourceCritic — round 22 report-source-fix (static critique)

Seat `KamaR22.ReportSourceCritic`, critic, read-only. Base `cc9f8d316358e13aa094cdb07714771a009805e9`.
Nothing was run except reads (`git show`/`ls-tree`/`rev-parse`, `sha256sum`, one read-only
regex scan of the committed `corpus/SOURCES.md` blob). No production edits, no installs.
The executor clone `ReportSourceFix/clone` had no candidate diff yet (its `tools/report-landing-audit.py`
still has sha256 `80a58825…9808`, the same as at `cc9f8d3`), so this critiques the **chosen design**
and states what the candidate must do to satisfy it.

## Verdict

The design is sound and narrow enough. It does no harm only if six implementation choices are
made exactly as listed below. A plausible but naive implementation breaks it in at least four
ways, each of which a finite fixture can tell apart:

1. **Exempting by token instead of by occurrence.** If the code collects "hashes that appear in
   registry URLs" and drops them from `FULL.findall(text)`, then a bare copy of the same hash
   anywhere in the report is exempted too. That breaks the "bare same hash still defect"
   acceptance criterion. The exemption has to work on character spans of URL occurrences.
2. **Harvesting hashes from the whole row or the whole source cell.** The committed registry
   proves this would be wrong. S048's source cell has a bare 40-hex outside its URL
   (`(tag commit 8d3ae59288f1e7d58d76558a6ee96d533bc5019f)`), and 24 rows carry bare 40-hex
   tokens in the anchor column. One of those is S038, whose anchor holds exactly
   `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`.
3. **Computing the scheme-stripped form with `removeprefix("https://")`.** That is not what
   sources-census prints. Census `url_of` (in `scripts/sources-census.sh`, lines 600–605) takes the
   **first** `https?://[^[:space:]|]+` in the source cell, strips `#…` and one trailing `/`, strips
   the scheme, and lowercases the host.
4. **Swallowing a registry read failure as "no exemptions".** That turns a Git fault into an
   exit-1 `failed` verdict. The docstring contract says "Errors are never verdicts", so a fault
   must give exit 2.

## Axes

| axis | what must not regress |
|---|---|
| A1 detection | every defect the old script reports, except a 40-hex whose *every occurrence* is inside a bounded, registered source-URL occurrence outside `## Landed changes` |
| A2 Landed integrity | ABBREV, `checkable_abbrev`, `landed-unresolved`/`ambiguous`/`omitted` computed on the unmodified text and section |
| A3 error≠verdict | registry fault, irregular registry → exit 2; absent registry → no exemptions |
| A4 single authority | URL identity is census's (first URL of a valid S-row); no second URL dialect, no hash/repo whitelist |
| A5 committed bytes | registry from the `--branch` blob, never the worktree; there is no `--sources PATH` override |
| A6 history | the 9 ledger rows still match (none would be exempted, see below); existing 36 selftest cases unchanged |

## Evidence

- Committed registry blob `cc9f8d3:corpus/SOURCES.md` = `14ea0501b9fae159681d2ca0a55765a7a02f357a`,
  sha256 `44ff346bf16d5c382b94775ee918b9e65f77e6ad4315542641e8697188d058a9`; the worktree copy equals it.
- Valid S-rows whose census URL contains a 40-hex: S023, S024 (rejected), S035–S037, S042, S043, S047,
  S054, S056, S058 (raw.githubusercontent), S059, S060, S063 (rejected). None has a fragment, trailing
  slash or uppercase host, so for today's data the census form is just the URL without `https://`.
  Fixtures must still exercise the full normalization, though (cases R2, R3).
- Bare 40-hex in the source cell outside its URL: S048 only. Bare 40-hex in the anchor column:
  S001, S005–S010, S013–S016, S018, S023–S026, S038 (`704366d…`), S039 (×2), S045, S055 (a *lane*
  commit `c6dc46fa…`), S062, S068, S072. No `http://` row exists.
- The mandatory census stdout `.ufo/waves/round-22/runs/6433390a/fr-sources-validate.stdout`
  (sha256 `cf5f3cb576ab68a45f415e62c6a45b784bbf81ae2071edd380b545de900347b3`, committed at `cc9f8d3`)
  carries the hash only on its three W04 lines (S043, S056, S060). Each time it sits inside a census-form URL
  preceded by a space and followed by ` across scopes`.
- Errata ledger `cc9f8d3:registry/report-landing-errata.tsv` (`90d84c9d…`) has one
  `unresolved-full-hash` row: the round-20 splice `0957ce61…b56c`, which is not a registry URL hash.
  The other 8 rows are `landed-omitted`, which the exemption cannot touch. So the full-audit
  result (9 defects, all corrected) is unaffected, **provided nobody adds an interim errata row
  for `704366d…`**. After the fix, such a row would come back as `errata-unmatched` and exit 1
  (case E1).
- Old script pin: `cc9f8d3:tools/report-landing-audit.py` = blob `d8af6b38036905670cd7eb64ffcb7669ff1b5c50`,
  sha256 `80a588257fce8e436f39bcf0b59a473f4537eaeb4f06442a14b027dd7bed9808`.

## Counterexamples and corrections

**C1 — the exemption must be per occurrence (A1).** `lookup(repos, FULL.findall(text))` is
set-based. Filtering the *token* set lets bare `704366d…` text through.
Correction: find the URL-occurrence spans first, then keep a `FULL.finditer(text)` match unless
its span lies inside one of them. Never edit the token set.

**C2 — classify by census URL, not by cell (A4, A1).** S048 and S038 above show the failure.
Correction: per valid row, take only `re.search(r"https?://[^ \t\n\r\f\v|]+", source_cell)`, i.e.
census's first URL. Use an explicit ASCII class, because Python `\s` also matches NBSP while gawk
`[:space:]` in a UTF-8 locale may not. A second URL in the cell (S038's parenthetical asset API
URL, S053's tar URL) is not classified. Census never prints it, and it carries no hash.

**C3 — valid S-row means census row shape, not "any pipe line" (A4).** Mirror `row_pass`:
- A `^ {0,3}##[ \t]` heading sets `registry = trim(rest) == "Registry"`.
- A `^ {0,3}#[ \t]` heading clears it. `###` lines change nothing.
- A row line matches `^ {0,3}\|`, has the leading spaces removed, and gives `len(line.split("|")) == 13`.
- The id cell, stripped of spaces and tabs, must fullmatch `S[0-9]{3,}`.

Do not require the census E-checks (status enum, used-by on disk, and so on). Those are census's
authority. Duplicating them creates a second validator, and a classification must not depend on
them. Rejected rows (S024, S063) still classify: "curated source URL" is a type, not an
endorsement. Rows under `## Leads`/`## Paths`, prose URLs in the Search log, header and separator
rows, 10- or 12-cell rows, and non-`S` ids never classify.

**C4 — occurrence boundaries (A1).** Exact substring matching is not enough:
`notgithub.com/ggml-org/…/<H>/f.cpp` contains the census form, and so do
`https://…/<H>/f.cpp.bak` and `…/f.cpp/x`. Correction: compile one alternation, longest first,
with explicit boundaries:
- full form (as written in the cell) with left guard `(?<![A-Za-z0-9+.-])`;
- census form with left guard `(?<![A-Za-z0-9._~%+@:/-])`. Because `/` is in the guard, the
  census form cannot match after `http://` or `ftp://`, so an unrecorded scheme is not
  exempted. `https://X` is caught by its full-form alternative.
- shared right guard `(?=[\s`'"<>()\[\]|,;*]|\Z)`.

A trailing sentence `.`, a `#L10` fragment, or a line-wrapped URL is therefore **not** exempted.
That is a deliberate false positive in the safe direction: the author can write the exact URL or
add errata. It is a tradeoff to accept, not a defect to fix.

**C5 — Landed region gets no exemption (A2).** The contract says "Do NOT exempt … anything inside
Landed commit checking". The minimal reading that fully preserves old behavior there is:
- ABBREV and `cited` run on the original `section`, unchanged;
- the FULL scan also gives **no** exemption to occurrences inside the `## Landed changes` span.

So a registered source URL with a foreign hash in Landed yields both `unresolved-full-hash` and
`landed-unresolved` (exactly what the old script gives), and the round's lane commits are still
`landed-omitted`. This needs `landed_section` to expose its span, i.e. a `landed_match()` helper.
Keep `landed_section()`'s return value, since the `heading-anchor` selftest calls it.

Residual conflict to state, not to fix: a registered URL whose hash is a *lane round commit*,
placed in Landed, still counts as a citation under the unchanged ABBREV rule. The old script
behaves the same. "Source URL in Landed does not satisfy landed commit reference" can only be
pinned with a **foreign** hash (case L1). A fixture using a lane-commit hash would contradict
"ABBREV/Landed rules stay unchanged". Do not build it.

**C6 — absent registry vs Git fault (A3, A5).** `git show B:corpus/SOURCES.md` returns rc 128
both for "path absent" and for a real fault, and `cat-file -e` cannot tell them apart either.
Correction: reuse the existing `ls-tree` pattern from `parse_rounds`:
- `git(lane, "ls-tree", branch, "--", "corpus/SOURCES.md")`. rc≠0 raises `EvalError`.
- Empty output means absent: return no forms. This is the old selftest lanes' path.
- Exactly one line `100644|100755 blob <oid>\tcorpus/SOURCES.md` → `git(lane, "cat-file", "blob", oid)`.
  The `blob` type gives raw bytes with no textconv or filters (S033). rc≠0 → `EvalError`.
- Any other entry (`120000` symlink, `tree`, `160000` commit) → `EvalError`, mirroring
  `read_report`'s irregular-file refusal.

Read the registry once in `run()`, after the existing `rev-parse --verify` of the branch, and pass
the forms into `audit_round`. Never read `Path(lane_repo)/corpus/SOURCES.md`.

**C7 — make the classification visible (A4, false-provenance guard).** The exemption makes the
committed registry an input to the FULL verdict. Under the trusted-lane scope that is accepted (it
is not D4), but it must not be silent. Add a per-round `source_url_hashes` list to the JSON result
(sorted tokens that had at least one exempted occurrence) and leave status unaffected. Update the
docstring: `unresolved-full-hash` becomes "a 40-hex token … no git object in either repo, except an
occurrence inside a `corpus/SOURCES.md` Registry source URL (committed `--branch` blob; full or
census form) outside `## Landed changes`; type classification, not provenance". Without this,
the next reader cannot tell why a missing object passed.

## Minimum implementation remedy

Assumes `SOURCES = "corpus/SOURCES.md"` is defined next to `ERRATA`.

```python
CENSUS_URL = re.compile(r"https?://[^ \t\n\r\f\v|]+")
URL_END = r"(?=[\s`'\"<>()\[\]|,;*]|\Z)"


def source_url_forms(text):
    """(full, census) URL forms of each Registry S-row source cell, as
    sources-census row_pass/url_of reads it: the first URL only."""
    forms, registry = set(), False
    for line in text.split("\n"):
        if re.match(r" {0,3}##[ \t]", line):
            registry = line.lstrip(" ")[2:].strip(" \t") == "Registry"
            continue
        if re.match(r" {0,3}#[ \t]", line):
            registry = False
            continue
        if not registry or not re.match(r" {0,3}\|", line):
            continue
        cells = line.lstrip(" ").split("|")
        if len(cells) != 13 or not re.fullmatch(r"S[0-9]{3,}", cells[1].strip(" \t")):
            continue
        m = CENSUS_URL.search(cells[2])
        if m is None:
            continue
        u = re.sub(r"#[^ ]*$", "", m.group(0))
        u = re.sub(r"^[A-Za-z]+://", "", re.sub(r"/$", "", u))
        host, sep, rest = u.partition("/")
        forms.add((m.group(0), host.lower() + sep + rest))
    return forms


def load_source_urls(lane_repo, branch):
    entry = git(lane_repo, "ls-tree", branch, "--", SOURCES).rstrip("\n")
    if not entry:
        return None
    meta, _, path = entry.partition("\t")
    mode, kind, oid = (meta.split(" ") + ["", "", ""])[:3]
    if "\n" in entry or path != SOURCES or kind != "blob" \
            or mode not in ("100644", "100755"):
        raise EvalError(f"{branch}:{SOURCES}: not a regular blob")
    forms = source_url_forms(git(lane_repo, "cat-file", "blob", oid))
    if not forms:
        return None
    alt = lambda xs: "|".join(map(re.escape, sorted(xs, key=len, reverse=True)))
    return re.compile(
        rf"(?:(?<![A-Za-z0-9+.-])(?:{alt(f for f, _ in forms)})"
        rf"|(?<![A-Za-z0-9._~%+@:/-])(?:{alt(c for _, c in forms)})){URL_END}")
```

In `audit_round(…, source_urls)`, replace the FULL line:

```python
    landed = landed_match(text)          # re.Match of the section, or None
    lo, hi = landed.span(1) if landed else (-1, -1)
    spans = [m.span() for m in source_urls.finditer(text)] if source_urls else []
    tokens, classified = [], set()
    for m in FULL.finditer(text):
        a, b = m.span()
        if not (lo <= a < hi) and any(s <= a and b <= e for s, e in spans):
            classified.add(m.group(0))
        else:
            tokens.append(m.group(0))
    full = lookup(repos, tokens)
```

`source_url_hashes = sorted(classified - set(tokens))`: a token that also has a bare occurrence is
reported as a defect, not as classified. `section`, `cited` and `cited_anywhere` stay computed on
the original text. No other function changes.

## Finite discriminating fixtures (isolated CLI selftest, temp repos only)

Registry committed on the fixture lane `master` at `corpus/SOURCES.md`. Use synthetic non-object
hashes `Hn = f"{n:x}" * 40` (n = 1…9 gives distinct lowercase hex, checked `missing` via `lookup`).

```
## Registry
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S001 | Up — https://up.example/o/r/blob/H1/a.cpp | code | A | s1 | @ H6 | t | mined | 2026-10-01 | 90d | — |
| S002 | Up2 @ H7 — https://Up.Example/o/r/tree/H2/ | code | A | s2 | a | t | rejected | 2026-10-01 | 90d | — |
| S003 | Up3 — https://up.example/x/H3/f.md#sec | docs | A | s3 | a | t | mined | 2026-10-01 | 90d | — |
| S004 | ten cells — https://up.example/m/H4/f | code | A | s4 | a | t | mined | 2026-10-01 | 90d |
| X005 | bad id — https://up.example/m/H5/f | code | A | s5 | a | t | mined | 2026-10-01 | 90d | — |
## Leads
| S008 | lead row — https://up.example/l/H8/f | code | A | s8 | a | t | queued | 2026-10-01 | 90d | — |
- https://up.example/l/H8/g
```

After committing, append `| S009 | wt — https://up.example/w/H9/f | … 11 cells … |` to the
**worktree** copy only.

Each case is a `--report N=draft` body with `--no-errata` and the expected `unresolved-full-hash`
token set (U). Every draft also has a `## Landed changes` section citing the fixture round commits,
so no other kind appears unless the case says so.

| case | report text (outside Landed unless stated) | expected U |
|---|---|---|
| R1 full | `see https://up.example/o/r/blob/H1/a.cpp now` | ∅, `source_url_hashes=[H1]` |
| R2 census | `kama\tW04\tS001 duplicate url up.example/o/r/blob/H1/a.cpp across scopes` | ∅ |
| R3 census-normalized | `up.example/o/r/tree/H2` and `https://Up.Example/o/r/tree/H2/` | ∅ (fails if stripped with `removeprefix`) |
| R4 fragment | `up.example/x/H3/f.md` and `https://up.example/x/H3/f.md#sec` | ∅ |
| B1 bare same hash | R1 text plus a bare `H1` line | {H1}, `source_url_hashes=[]` |
| B2 source-cell bare | `@ H7` (S002 source text outside its URL) | {H7} |
| B3 anchor bare | `@ H6` | {H6} |
| N1 unregistered path | `https://up.example/o/r/blob/H1/b.cpp` | {H1} |
| N2 left boundary | `notup.example/o/r/blob/H1/a.cpp` | {H1} |
| N3 right boundary | `https://up.example/o/r/blob/H1/a.cpp.bak`, `…/a.cpp/x`, `…/a.cpp#L5`, `…/a.cpp.` | {H1} |
| N4 scheme | `http://up.example/o/r/blob/H1/a.cpp` | {H1} |
| M1 malformed rows | URLs of S004 (H4), X005 (H5) | {H4, H5} |
| M2 outside Registry | `https://up.example/l/H8/f`, `…/H8/g` | {H8} |
| W1 worktree registry | `https://up.example/w/H9/f` | {H9} |
| L1 Landed | Landed contains only `- https://up.example/o/r/blob/H1/a.cpp`; R1 text not elsewhere | {H1}, plus `landed-unresolved H1` and `landed-omitted` for every required round commit |
| E1 errata interplay | R1 text, errata row `N unresolved-full-hash H1 <lane commit> x` | exit 1, `errata_unmatched=1` |
| G0 absent | existing selftest lane (no `corpus/SOURCES.md`) | the existing 36 cases unchanged by name and result |
| G1 irregular | `corpus/SOURCES.md` committed as a symlink, or `corpus/SOURCES.md/` as a tree | `EvalError`, CLI exit 2 |
| G2 Git fault | registry blob's loose object deleted in the fixture repo | `EvalError`, CLI exit 2, never 1 |

Cases R1, R2, B1, N1 and L1 are the five acceptance criteria. The others are the cheapest ones that
kill each naive variant (C1–C6).

## Red-before / green-after demonstration (prepared for L1; not run)

- Old script: `git show cc9f8d3:tools/report-landing-audit.py` (blob `d8af6b38…5c50`,
  sha256 `80a58825…9808`), written to a temp path. Candidate: the executor's script, pinned by sha256 at run time.
- Fixture (temp dir, `git init -b master` ×2, `git_env()`-style isolated config):
  - lane: one commit `round-22: work` by `kama-shokunin`, plus `corpus/SOURCES.md` = the exact
    `cc9f8d3` registry blob (sha256 `44ff346b…58a9`);
  - fleet: empty initial commit;
  - draft: `## Work performed`, then a fenced block holding the exact bytes of `fr-sources-validate.stdout`
    (sha256 `cf5f3cb5…347b3`), then `## Landed changes` citing the lane commit's 12-hex prefix.
  Record the draft's sha256 too.
- Command for each script: `python3 <script> --lane-repo T/lane --fleet-repo T/fleet --rounds 22 --report 22=T/draft.md --no-errata --json`.
- Expected verdicts:
  - old: exit 1, defects exactly `[unresolved-full-hash 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad]`;
  - candidate: exit 0, no defects, `source_url_hashes=["704366d…"]`.
- Control draft (same bytes plus one bare `704366d…` line): both scripts give exit 1 with that one
  defect. This shows the fix adds no blind spot.
- No step touches the actual lane, the fleet report, or Git state outside `T/`.

## Checks for L1 (not run by this seat)

1. `python3 tools/report-landing-audit.py --selftest`: 36 existing names plus the new cases, all `ok`.
2. The red/green demo above, both scripts, plus the control draft.
3. A read-only full audit over the real repos (`--rounds 10-`): still 9 defects, 9 corrected,
   0 unmatched/invalid, exit 0.
4. A read-only draft audit of the round-22 report: exit 0, with only `704366d…` in `source_url_hashes`.

Installs/updates: none.
