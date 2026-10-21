# SrcPartial — promisor objects, promises, and metadata-independent local completeness

## Verdict

**SUPPORTS the round-24 narrowing, and supplies no authority for a repository-level refusal
on promisor metadata alone.** The page distinguishes the *promise* (a promisor remote's
undertaking) from the *promisor object* (a local belief inferred from pack provenance and
references), and states that the client keeps **no list of missing objects**. Therefore a
`.promisor` marker, `extensions.partialClone`, or promisor remote configuration cannot by
itself establish that any *required* object is locally absent. Equally, the same page says
filtered packfiles are "incomplete in the traditional sense", so it also cannot establish
completeness: the verdict must come from a local lookup of each required object. That is
exactly the preregistration's metadata-neutral, per-object rule (expected_after 1–4 and 6).

**Source status: reopened used source, not new scope.** The URL is already registered three
times in the working tree observed 2026-10-21: `corpus/SOURCES.md:104` (S092),
`corpus/SOURCES.md:111` (S099, which supersedes S092 and anchors the same §Handling Missing
Objects for the lazy-fetch sentence), and `corpus/SOURCES.md:115` (S103, added this round by a
sibling lane and still uncommitted). S103 already covers the marker-representation half; my
claim adds the exact "arbitrary contents" and "no missing-object list" sentences. S099's
sentence remains true and is still needed for the "failed lookup is not absence" half, so this
claim must **complement, not supersede** S099 or S103. No registry edit was made; the preferred
and fallback representations are in `.ufo/waves/round-24/build/out/SrcPartial/proposed-row.md`.

## Source identity — exact

| field | observed value |
|---|---|
| URL | https://git-scm.com/docs/partial-clone#_handling_missing_objects |
| page version marker | `partial-clone last updated in 2.56.0` (`partial-clone.html:1300`) |
| versioned URL | https://git-scm.com/docs/partial-clone/2.56.0 — HTTP 200; definition and no-list sentences compared equal to the unversioned page |
| upstream source | git.git tag **v2.56.0**, `Documentation/technical/partial-clone.adoc`, sha256 `9512d7ee0b79680f61d3f98c9eae42cc1dbaeef63535c5502cff66d7bce19264` |
| page HTML | sha256 `8a6493225f76dba8e5b1eb75234f7370e057ee87c11e07a2681dbf522b16c9ad`, 51719 bytes, HTTP/2 200 |
| access date | **2026-10-21** (UTC fetch 17:58); server `last-modified: Wed, 21 Oct 2026 15:55:46 GMT` is generation time, not a source revision date |
| anchor | §**Handling Missing Objects** (`id="_handling_missing_objects"`, `partial-clone.html:1922`); adoc lines 108–168 and footnote [a] lines 323–337 |
| host git | `git version 2.56.0` — matches the page's version |

### Primary quote (19 words, exact rendered sentence; footnote marker stripped)

> This means that there is no need for the client to explicitly maintain an expensive-to-modify list of missing objects.

adoc lines 128–129 (sentence continues to footnote `[a]`).

### Adjacent exact sentences used for the distinction (each ≤25 words)

| role | exact text | adoc lines |
|---|---|---|
| promise side | `A remote that can later provide the missing objects is called a promisor remote, as it promises to send the objects when requested.` (23 words) | 33–35 |
| object side (fragment, sentence subject omitted) | `objects that it knows (to the best of its ability) that promisor remotes have promised that they have` (18 words) | 120–122 |
| membership basis | `either because the local repository has that object in one of its promisor packfiles, or because another promisor object refers to it` (22 words) | 122–123 |
| marker contents | `These promisor packfiles consist of a "<name>.promisor" file with arbitrary contents` (11 words) | 116–117 |
| footnote mechanism | `With the "promisor" concept, we infer a missing object based upon the type of packfile that references it.` (18 words; emphasis removed) | 336–337 |
| incompleteness limit | `These filtered packfiles are incomplete in the traditional sense` (9 words) | 93 |

## What the page establishes (observed, with locations)

1. **The promise is a remote capability.** A promisor remote "promises to send the objects when
   requested" (adoc 33–35). Nothing here says the promise has already been exercised or that
   any object is locally absent.
2. **Promisor packfiles are labelled by a sidecar with arbitrary contents.** `.promisor` is
   described as analogous to `.keep` and as having arbitrary contents (adoc 116–118). The
   sidecar therefore cannot be parsed as an omission list.
3. **The promisor-object class is not an absence class.** A promisor object is one the local
   repository knows the remote promised, *either because the object is in a promisor packfile
   or because another promisor object refers to it* (adoc 120–123). The class is defined by
   promise/provenance, so it contains both locally present objects and locally absent ones.
4. **Missing-ness is observed at lookup, not read from metadata.** "When Git encounters a
   missing object, Git can see if it is a promisor object and handle it appropriately"
   (adoc 125–127). There is no prior enumeration step.
5. **No missing-object list exists.** The client need not "explicitly maintain an
   expensive-to-modify list of missing objects" (adoc 128–129). Footnote [a] records that such
   a sorted OID list of server-omitted objects was considered and rejected on cost, and that
   Git instead *infers* a missing object from packfile type (adoc 323–337).
6. **A promisor repository can be locally complete for the needed subset.** A user who stays
   within the pre-selected subtree "may not encounter any missing objects" (adoc 43–44).
7. **Lookup failure is not absence.** A failed normal lookup invokes
   `promisor_remote_get_direct()` and retries; "no check as to whether the missing object is
   actually a promisor object is performed" (adoc 136–142). S099 already registers this
   sentence; it is cited here only to delimit what my claim does not cover.
8. **Fetching vs error is controlled by `fetch_if_missing`** (adoc 162–164), a per-repository
   flag the document itself wants to remove (adoc 166–168).

## Claim versus source — supported / not supported

**Supported by this page (claim may cite it):**
- A `.promisor` marker's *contents* carry no meaning; promisor status follows packfile
  provenance and promisor-object references (adoc 116–118, 120–123, 336–337).
- Promisor metadata does not enumerate omissions; no missing-object inventory is maintained
  (adoc 128–129 and footnote [a]).
- Promisor-object status includes objects that are locally present (adoc 120–123), so marker
  presence does not imply the required object is missing.
- A locally absent promisor object is, by the page's own definition, an object the promisor
  remote promised to have (adoc 120–123); local absence therefore cannot be read as proof the
  object never existed, which is why the audit outcome is unknown, not a defect.
- Filtered packfiles can legitimately lack objects and that is not corruption (adoc 108–118),
  so a missing object in a promisor repo has an innocent explanation and cannot be read as
  report omission.

**Not supported by this page (do not cite it):**
- **"Promisor-marked repositories are complete."** The page says the opposite about filtered
  packs: "incomplete in the traditional sense" (adoc 93–97), and partial clone exists so Git
  can "function without having a complete copy of the repository" (adoc 5).
- **Any exact verdict/exit/citation policy.** It is `Documentation/technical/`, a design note;
  it defines no auditor behavior, no exit status, no clean/omitted/failed taxonomy.
- **`remote.<name>.promisor` key semantics or boolean parsing.** The page never names that key.
  It names `extensions.partialClone` as the origin remote's config option (adoc 36–38) and as
  the compatibility extension for missing objects (adoc 102–106), but defines neither key's
  value grammar. The filter-only-promisor rule needs the code lane (`promisor-remote.c`)
  and/or git-config(1).
- **`--no-lazy-fetch` placement or behavior.** The page mentions only the per-repository
  `fetch_if_missing` flag (adoc 162–164), which it plans to remove; the global option is
  S089's scope (git(1)).
- **`git cat-file --batch-check` "missing" output, `git rev-list --missing=print`, or any
  command's machine-readable output.** `rev-list --missing=print` appears only as an
  illustrative "may internally want to" (adoc 152–155).
- **`fsck` as a completeness oracle.** The page says only that fsck is "fully aware of
  promisor objects" (adoc 157); it does not say what fsck tolerates. That belongs to SrcFsck.
- **Alternates, grafts, shallow, replace refs, object format.** Absent from this page;
  gitrepository-layout(5) (S094) covers those.
- **The `.promisor`-without-`.pack` case (grid C10) or pack/idx placement.** The page names the
  sidecar "in addition to" `.pack`/`.idx` (adoc 116–118) but sets no detection rule;
  SrcRepoLayout owns on-disk layout.

**Inference explicitly marked [INFERENCE]:** because no omission list exists and marker
contents are arbitrary, no metadata inspection can decide whether a *specific* required object
is absent; that decision requires an actual local object lookup. The page supplies the
mechanism; the audit consequence is the lane's policy, not a sentence of the page.

## Consequence for the r23 harm and the candidate

- The harm is visible in the frozen code: `tools/report-landing-audit.py:454-457` refuses on any
  paired `.promisor`/`.pack`, and `:458-465` refuses on `extensions.partialclone` or any true
  `remote.*.promisor` — before any cited object is examined. The round-23 lesson already
  declared this trade: "a complete blobless partial clone (T01) and a paired promisor pack
  without promisor config (F23) are refused (exit 2) where frozen gave a verdict"
  (`corpus/lessons/round-23.md:206-208`).
- What the source licenses, per outcome:

  | repository metadata | required object found locally | required object not resolvable locally |
  |---|---|---|
  | promisor marker/config present | normal verdict; metadata is not evidence either way | exit 2 could-not-evaluate; the failed lookup is unknown, not absence |
  | no promisor metadata | normal verdict | existing absence/omission rule |
  | `promisor=false` config (C09) / orphan marker without pack (C10) | normal verdict (no source conflict) | existing rule |
- The same page is the reason the isolation must stay: lookup failure triggers a fetch for any
  missing object, with no promisor-object check (adoc 136–142). Keep `GIT_ISOLATION`
  (`tools/report-landing-audit.py:93-96`) including `--no-lazy-fetch`, `--no-replace-objects`,
  log/signature suppression and `GIT_TIMEOUT`, so probes remain local and bounded. The page
  does not define that option; S089 does.
- Grid rows implied by the preregistration plus this source (derived, **not measured here**):
  F23 `tests/report-audit/repo-state-grid.py:670` stays **exit 2**, but the reason changes from
  the blanket repository refusal to unknown evidence. The fixture deliberately requires the
  blob to be locally missing (`require(... missing != 0 ...)`, `:212`), and the report prints
  that 40-hex blob in `## Notes`; `unresolved-full-hash` scans every 40-hex token in the
  report, exempting only an exact Registry source URL outside `## Landed changes`
  (`tools/report-landing-audit.py:12-18,283-326`), so a missing token there is unknown in a
  promisor context, not provable absence. F27 `:674-675` (fault, expected 1
  with `landed-unresolved`) becomes **exit 2** because the fake Landed token is unknown in a
  filter-promisor repo; its kind may need reclassification from fault to contract. C09/C10
  `:679-680` unchanged. The clean/full-clone-equivalence the preregistration requires applies
  to fixtures where every scanned token resolves locally, not to F23's deliberately missing
  blob. The oracle lane owns the frozen numbers; treat these as the policy-row changes the
  preregistration requires to be documented.
- The page supports keeping the paired `.promisor`/`.pack` marker itself as promisor context
  (adoc 116-118) even after config is removed (the F23 shape), and
  `extensions.partialClone` as a declaration that missing objects may exist (adoc 102-106).
  It does not define `remote.*.promisor` or `remote.*.partialclonefilter`; those need the code
  lane. C10's orphan marker is not described as a promisor packfile because the sidecar is
  described "in addition to" `.pack`/`.idx`; detection remains SrcRepoLayout's scope.

## Existing SOURCES accounting

- `corpus/SOURCES.md:104` S092 — same URL, anchor "section on fetching missing objects"
  (incorrect), teaches the lazy-fetch sentence. Still superseded by S099.
- `corpus/SOURCES.md:111` S099 — same URL + `#_handling_missing_objects`, teaches the
  "no check ... actually a promisor object" sentence, used by round-23. **Remains valid.**
- `corpus/SOURCES.md:115` S103 — same URL/section, added this round by a sibling lane
  (uncommitted at observation). Scope: paired `.promisor` marker representation, "not
  completeness of locally required audit evidence". This already registers the
  provenance-versus-completeness half; my sentences (arbitrary contents; no missing-object
  list) are not in its `teaches`.
- Preferred representation: **amend S103 before it is committed**. Because S103 is absent from
  base `0df800e`, it is an added row under `tools/sources-append-only.py:19`, so its cells can
  still change without an append-only violation; I validated the amended 11-cell row in memory
  with the tool's own parser against base (0 violations, S103 reported added). Fallback if S103 is
  frozen: append **S105** after S104 (S102-S104 are now taken; the earlier S102 draft must not
  be applied). Both variants are in `out/SrcPartial/proposed-row.md`.
- This is a **reopened used source**: the same URL/section opened again for a different
  sentence, not a new source discovery. It does not claim upstream changed or withdrew
  S092/S099/S103 (the convention at `corpus/SOURCES.md:141`).

## Artifacts

- `.ufo/waves/round-24/build/out/SrcPartial/receipt.txt` — URLs, HTTP headers, byte counts, sha256, fetch UTC, version markers.
- `.ufo/waves/round-24/build/out/SrcPartial/partial-clone.adoc` — official upstream v2.56.0 source (sha256 above).
- `.ufo/waves/round-24/build/out/SrcPartial/excerpt.txt` — line-numbered exact excerpts for every sentence cited.
- `.ufo/waves/round-24/build/out/SrcPartial/handling-section.txt` — rendered §Handling Missing Objects extraction.
- `.ufo/waves/round-24/build/out/SrcPartial/proposed-row.md` — candidate representation: preferred amended S103 and fallback S105 (not applied).

No tools installed. No registry or production edits. Only official HTTPS documentation fetched.

## Unverified / out of lane

- No grid, fixture, selftest, or audit run (contract says no routine suite checks).
- F23's changed rationale (still exit 2) and F27's expectation change (1→2) are derived from
  `preregistration.json` + this source, not measured.
- Behavior of `cat-file --batch-check`/`rev-list --missing=print` under `--no-lazy-fetch` in a
  promisor repo is not established here (SrcCatFile/SrcRevList lanes).
- `promisor-remote.c` config-to-promisor-remote initialization is SrcPromisorCode's lane; this
  page does not define `remote.*.promisor`.
- Registry rows S102-S104 appeared in the working tree while this lane ran (uncommitted).
  Line numbers and row availability were observed 2026-10-21 and can change again; L1 must
  re-check before applying either representation.
