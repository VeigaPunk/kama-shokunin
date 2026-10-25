# ReviewQuality — KQ44/KQ45 tail and the KQ46 wording (round 37, wave 1, seat L1Kama37.MobileMink)

Read-only review. `corpus/QUALITY.md` was not edited. Working-tree tail at review time: 322 lines;
KQ44 is a row appended inside the KQ43 table (line 316), KQ45 is its own block (lines 318-322,
uncommitted appendix of round 36). File ends `|\n` at line 322, so an append starts at 323.

Sources re-derived for this review (no fetch; local bytes and the read-only staged package only):
`corpus/QUALITY.md:316,318-322`, `corpus/lessons/round-36-verifier-spotcheck.md:49-199`,
`corpus/lessons/round-36.md:25-50`, `corpus/lessons/round-35.md:32`, `corpus/lessons/round-31-verifier-spotcheck.md:55`,
`considerthese/2026-10-24.md:29`, `corpus/SOURCES.md:186,204,205,213-215`,
`/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md:7-16,24,36-37,41-43,48-49,54,68,73`,
`/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/{sglang-native-api-deprecation-amendment-2026-10-23-r4.md:7,endpoint-health-probe-conventions.md:6-12,hosted-health-route-configuration-amendment-2026-10-23.md:10-14,hosted-health-route-configuration-amendment-2026-10-24-r7.md:9,kv-cache-reclamation-models.md:3-10}`,
`/home/vgpnk/Projects/shokunin/CORPUS.md` rule 2, `tools/round37-coverage-audit.py:69-99`,
`.ufo/waves/round-37/preregistration.json`, `.ufo/waves/round-37/w1/out/ScribeKQ46/derivation.md`.

---

## 1. KQ44 — re-derivable, one location gap

**Evidence holds.** The motivating cell's parenthetical "calibration improved, score held at 7"
re-derives in both cited lessons: `round-29-verifier-spotcheck.md:46` — "score stays 7→7 by the
no-self-promotion rule"; `round-30-verifier-spotcheck.md:45` — "score held 7 by the author". The
proposal it cites (`considerthese/2026-10-24.md`, proposal 1 and the round-29/30 rows of its table)
carries the same verdict-plus-score pairing. No wrong referent.

**Gap (low).** The Admit cell says the verdict "is recorded next to the numeric score that round
actually held" but does not say where. Two artifacts already do this — the `considerthese` daily
table's "Outside verdict / Axes moved" columns and the SCORECARD round row — so the obligation is
satisfiable, but a reader cannot tell which one satisfies it. "Promoter question, not a
self-promotion" also names no owner. This is a wording gap, not a defect: the row is already in
the file and QUALITY.md's head rule ("Criteria are added as new rows; supersession names the old
criterion instead of erasing it") forbids editing it. If the lane wants the fix, it is an appended
one-clause qualification naming the two locations; otherwise leave it.

**Structural defect (low, fixable only by convention for future blocks).** KQ44 is a sibling row of
KQ43, so the heading "Criterion added — round 33: gate receipts bind outputs to evaluated
revisions" governs a criterion about closure verdicts. A reader scanning headings does not find
KQ44. KQ46 must not repeat this: give it its own heading block.

## 2. KQ45 — two of three motivating arms re-derive; the third is contradicted by a committed receipt

A. **S174 arm — holds.** Row `corpus/SOURCES.md:186` quotes "Annotates each line in the file with
   information from the revision which last modified the line" labelled verbatim; the live manual
   text KQ45 cites contains "in the given file". The row drops "given". Correctly classified as drift.

B. **S193 arm — holds.** Row `corpus/SOURCES.md:205` quotes "`A path is registered iff it occurs in
   a cell of a row of such a table.`" with the RST markup stripped; KQ45 says the committed docstring
   at `c4c46ad5` reads "``registered``". Corrections may not rewrite the cell (CORPUS.md rule 2),
   so the append-only remedy is the right one. (Minor: `considerthese/2026-10-24.md:29` also reports
   S193 "citing line 22 for text at line 15"; KQ45's cell names only the markup. Incomplete, not wrong.)

C. **S192 arm — does not hold; this is the finding.** KQ45 claims "the quoted sentence is absent
   from the fetched bytes of the cited URL, whose body renders client-side, so it is
   unverifiable-by-fetch rather than drift". Three independent local records say otherwise:
   - `corpus/lessons/round-31-verifier-spotcheck.md:55` — the S192 row was re-opened by fetch on
     2026-10-24: "located quote present verbatim at the `response_format` body parameter (fetched
     md lines 1010-1012; lesson cites line 1008 — content moved by ~2 lines between fetches, quote
     itself exact)". The source is reachable and the quote is present.
   - `considerthese/2026-10-24.md:29` classifies S192 as "cited two lines off after the page moved".
   - The exact token `unverifiable-by-fetch` exists nowhere in the repository except KQ45's own row
     (`grep -rn 'unverifiable-by-fetch'` over `corpus/` and `.ufo/waves/round-36/` → only
     `corpus/QUALITY.md:322`). The nearest existing vocabulary is the quarantine verdict cell
     `unverifiable` (`lessons/round-35.md:38`), which is a class label for a quote that is not a
     page sentence, not a fetch-blocked-source marker. S192's row
     (`SOURCES.md:204`) records an anchor "Body Parameters → response_format, accessed 2026-10-24"
     and no access route, no marker; no round-36 lesson mentions S192 at all.

   So the one arm that introduces KQ45's new class mislabels drift as unreachable. Under KQ45's own
   standard ("a row whose quote drops a word… is a defect, corrected by an appended superseding
   row"), S192 is a line-span defect with a reachable artefact, not a fetch-blocked source.

**Wording defect in the same clause (medium).** "is marked `unverifiable-by-fetch`" does not say
where the mark goes, and the registry has no such value: the status column is exactly
`{mined 184, queued 8, rejected 11}` (`corpus/SOURCES.md`, status field of all 203 rows), and the
census validator compares registries by row. A counter cannot implement the clause without guessing;
putting the token in `status` would create a fourth value no instrument knows. Recommend an appended
qualification: the route and the words `unverifiable-by-fetch` go in the **anchor cell**, and the
status column is left alone.

**Internal reference (low).** "CORPUS.md rule 2" is bare. No `CORPUS.md` exists in the lane repo;
the only one is the fleet root `/home/vgpnk/Projects/shokunin/CORPUS.md`, whose rule 2 is indeed
"Append-only … A correction is a new row whose `teaches` opens `supersedes S0NN —`". Every other
bare path in QUALITY.md resolves lane-relative (`SOURCES.md`, `lessons/…`, `considerthese/…`), so
this one reference does not resolve as written. Content is correct; path is not.

---

## 3. KQ46 — verdict on the proposed wording

Proposed: *"a foreign or staged id range cited in a lesson is a claim: re-derive every id against
the named artifact before citing it; a copied range that misnames ids is a correction target, never
a citation"*.

The framing ("an id is a claim") is right and matches the r36 verifier's own diagnosis. Five
changes are needed before it is implementable. Objections are ordered by how much each one would
let through.

### O1 (blocking) — the discriminator is provenance, but the failure is referent.

"Foreign or staged" does not separate right from wrong even in its own motivating defect. At
`round-36.md:39` the wrong ids `S366`/`S391` are **staged** ids — of two *other* staged files
(`hosted-health-route-configuration-amendment-2026-10-23.md:10` and `…-r7.md:9`, both AWS/Azure
rows) quoted in a sentence about `sglang-native-api-deprecation-amendment-2026-10-23-r4.md`, whose
own `source:` line 7 is `S371`. Conversely the *corrected* id `S371` is equally staged and equally
foreign. What differs is only whether the id's row names the artifact the sentence names. The
criterion must test reference, not origin.

### O2 (blocking) — "re-derive" has no observable, and the obvious observable passes every wrong id.

"Re-derive every id against the named artifact" is satisfied by asking that the id resolve, and
**all five wrong ids resolve**: S366 = AWS SageMaker zh_cn (`SOURCES.append.md:43`), S359 = vLLM
health API (`:36`), S360 = sglang release tags (`:37`), S372 = a kama round-4 evidence file (`:49`),
S391 = Azure ML BYOC (`:68`). The check that catches them is a print of the row's own title and pin
beside the artifact the sentence names, refusing the mismatch. Without that print the criterion is
shape-only — the same defect KQ14 already names for pointers ("in-bounds pointer alone proves the
old claim true").

### O3 (blocking) — "in a lesson" is narrower than the pattern, including in this round.

The r36 defect happened in a lesson's Gate section, so "lesson" happens to cover that instance, but
ids are cited in knowledge-entry `source:`/`recheck:` lines, report tables and SCORECARD claim text.
This round's own C2 requires three *entries* to "cite an S-id present in `corpus/SOURCES.md` at the
tip" — so entry-level citations are the live surface, and a criterion scoped to lessons would be
born missing the prose its own round is writing.

### O4 (blocking) — "never a citation" does not cover repetition inside the repair, which is the part round 37 has already frozen.

`preregistration.json` R36-D2B reads: "the row must not restate the wrong ids S359, S360, S372 or
S391". A correction row is not a citation, so "never a citation" would permit exactly what the
frozen claim forbids. KQ46 must say the repair restates a wrong id only in the replaced position.
It must also say the **disposition stands** — D2 is explicit ("Every decision stands; only the id
evidence is wrong"), and a criterion read the other way would invalidate r36's two admits and this
round's C1, which corrects the ids while keeping the decisions.

### O5 (tightening) — "correction target" is the wrong noun, and registry naming is missing.

In this corpus a "correction" is an appended row carrying `supersedes S0NN —` (CORPUS.md rule 2).
Calling a misnaming range a "correction target" invites appending a correction *of the range* as if
the range were a registry fact. The defect is in the citing sentence; the repair is an appended row
that carries wrong→right. Separately, the id space is genuinely ambiguous and the criterion has to
say so: lane `S327` and staged `S332` are the **same page** (vLLM Engine Arguments, same v0.32.0
URL), lane `S328` is staged `S371` (native_api.mdx), lane `S329` is staged `S364`/`S365`/`S377`/`S396`
(http_server.py). The lane's highest id at the tip is `S329`; the staged append starts at `S330`. So
this round's new lane rows will occupy the staged numbering, and an unresolvable bare "S333" will
soon mean two different documents. A cited id must name its registry, and a document this lane has
appended must be cited by its lane id.

### O6 (addition) — absent is not unverifiable.

KQ45 had to separate "unreachable" from "drift"; KQ46 must separate "not in the registry" from
"unreachable". Otherwise the next round marks five wrong ids "unverifiable" and closes the thread.
Also add the r36 defect's own tell: `S372` is an `own-work` row (`SOURCES.append.md:49`), so it can
never be "this document" for a published page — a row's kind is a second cheap discriminator.

### Drop-in row (recommended), one physical line, four cells

```
## Criterion added — round 37: a cited id is re-derived against the artifact it names, in the registry that holds it

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ46 | A sentence in a lesson, report, gate, knowledge entry or registry row that cites an id whose referent is not in this lane's `SOURCES.md` at the tip — a staged-package id, a sibling lane's id, or a set reproduced from an earlier lesson — names the registry that id belongs to and re-derives each id there in the round that writes the sentence: for every cited id the check prints the row's own source title and pinned URL or path beside the artifact the sentence names, the citation is admitted only when the two are the same artifact, and that print is committed in the round's wave directory. A range is expanded to its members and every member is checked; a document this lane has already appended is cited by its lane id, with any foreign id quoted only as provenance; a row's kind counts, so an `own-work` row never stands for a published page. | An id that exists but names another artifact is credited because the check asked only that the id resolve — the r36 defect's five wrong ids all resolve; a range's endpoints are checked and its interior is not; a staged id is looked up in `corpus/SOURCES.md`, or a lane id in the staged append, where the two number spaces are independent and one document sits under a different id in each; a foreign id is copied into a knowledge entry's `source:` line in place of the lane id naming the same document; an id absent from the registry is written off as unverifiable instead of absent; or the repair for a misnaming id flips the admit-or-reject disposition the id merely evidenced, reintroduces a wrong id as if it still stood, or corrects the ranges instead of the sentence that copies one. | `lessons/round-36-verifier-spotcheck.md` §6 item 2 (D2): five distinct staged ids misnamed across `lessons/round-36.md` lines 33, 35, 39 and 41, plus the range "S331 to S334" at line 43 that no row of the cited file carries (the file cites S332, S336, S337, S338, S339 at `amendments/corpus/knowledge/endpoint-health-probe-conventions.md:6-10`); referents re-derived in `.ufo/waves/round-37/w1/out/ScribeKQ46/derivation.md`; already colliding: lane S327 ≡ staged S332, lane S328 ≡ staged S371, lane S329 ≡ staged S364/S365/S377/S396 |
```

If the lane prefers a shorter row, this is the minimum that still falsifies (drops registry naming
and the kind check, keeps referent + range + repair):

```
| KQ46 | An id cited from outside this lane's registry, or a set copied from an earlier lesson, is re-derived in the registry that holds it in the round that cites it: the check prints the cited row's own title and pin beside the artifact the sentence names and credits the citation only if they are the same artifact; ranges are expanded and every member checked, and a document already appended here is cited by its lane id. | An id that resolves to another artifact passes because only resolution was asked; a staged id is resolved in the wrong registry; a foreign id replaces the lane id naming the same document in an entry's `source:` line; a missing id is called unverifiable; or the repair flips a disposition or restates a wrong id as still standing. | `lessons/round-36-verifier-spotcheck.md` §6 item 2; `lessons/round-36.md` lines 33, 35, 39, 41, 43 |
```

### What I keep from the proposal

- "is a claim" — keep. It is the right framing and matches D2's own sentence.
- "re-derive every id" — keep as the requirement, with O2's observable attached.
- "a copied range … misnames ids" — keep the range case, but as one member of a larger class (O1).

### What the objections cost if adopted unchanged

Read literally, the proposal would (a) admit `S366` in a sentence about the SGLang amendment because
the id is staged and resolves, (b) pass `S331 to S334` because both endpoints exist and the range is
copied, (c) leave every knowledge-entry `source:` line ungoverned, and (d) permit a correction row to
restate the five wrong ids, which is the exact clause round 37's frozen C1 kills the claim on.

---

## 4. Findings outside KQ46 that the L1 can act on now

**F1 (medium) — D2 undercounts occurrences; `round-36.md:39` is unrouted.** D2 lists the S366→S371
swap at line 33 and the four-id list at line 35, but a third use of the same wrong ids sits at line
39: "its rows (S366, S391) cite campaign-provisional ids". The file it names
(`sglang-native-api-deprecation-amendment-2026-10-23-r4.md`) has exactly one `source:` line, `S371`
(line 7). `S366` belongs to `hosted-health-route-configuration-amendment-2026-10-23.md:10` and `S391`
to `…-2026-10-24-r7.md:9`. So the Gate swapped ids between two staged files in the same package —
the most plausible-looking form of the defect, because every id exists and every id is "staged".
`ScribeKQ46/derivation.md` maps the D2 corrections onto "lines 39, 41, 43"; the committed bytes put
them at 33, 35 and 43, with 39 a fourth, uncorrected occurrence. This does **not** touch C1: the
frozen statement set is D1, D2A, D2B, D3 and line 39 is outside it. It does mean KQ46's motivating
cell must say "lines 33, 35, 39 and 41" (as drafted above) or the criterion inherits the same
undercount.

**F2 (medium) — every staged entry's `recheck:` line names a registry that does not exist.**
`SOURCES-PROPOSED.md` is cited by `endpoint-health-probe-conventions.md:12`,
`kv-cache-reclamation-models.md:10`, `hosted-health-route-configuration.md:8`,
`sglang-docs-version-pinning.md:7` and others; the staged package ships only
`/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (no `SOURCES-PROPOSED.md` anywhere
under `merge/kama`). `kv-cache-reclamation-models.md` is one of the three frozen C2 entries, so if it
is adapted with its `recheck:` line intact the lane lands a dangling registry pointer in a file a
counter will then certify. KQ46's registry-naming clause catches this; the integration should
rewrite that line to `corpus/SOURCES.md` and the lane ids.

**F3 (medium) — the frozen C2 counter cannot tell a lane id from a staged id.**
`tools/round37-coverage-audit.py:69-70` extracts ids with `re.findall(r"\bS[0-9]{3,}\b", entry)` over
the whole file and credits the file if **any** extracted id is new at the tip (`:92-98`). The staged
entries carry `S330, S333, S334, S335, S346` (kv-cache), `S347` (prefix-cache) and `S363`
(amendment) — the same numeric block the lane's next rows will occupy. Two consequences: an entry can
carry the correct lane id in `source:` and a *wrong* staged id in prose and still pass, and an entry
that copies a staged id passes as long as some lane row with that number exists at the tip. This is
not a defect in the frozen predicate (it requires only "names an S-id present at tip and absent at
base") and C2 stands as frozen; it is the reason KQ46 is needed alongside it, and a review note for
the round-37 report so the coverage claim is not read as an id-correctness claim.

**F4 (low) — `ScribeKQ46/derivation.md` self-check overstates.** It says "the range correction matches
the staged file's own `source:` lines, not its filename" — correct — but its "Defect source" line
maps the corrections to lines 39/41/43 and its self-check counts "five misattributed ids" without
noting that line 39 is a distinct, unrouted occurrence. The referent table in that file is accurate
(verified row by row against `SOURCES.append.md`); only the line mapping and the occurrence count
need the correction above.

**F5 (low) — qualitative observation, not a defect.** Both newest criteria and the r36 defect share
one shape: a pointer that resolves, attached to a claim about a different thing. KQ44 fixed the
score-verdict pairing, KQ45 fixed the quote-at-anchor check, and both left the id alone; KQ46 closes
the remaining leg. That ordering argues for KQ46 as its own block rather than folded into KQ45.

---

## 5. Integration notes

1. Append after line 322: blank line, then the heading block (`## Criterion added — round 37: …`),
   then the four-column header, the separator, and the single row. Own heading, not a row in the
   KQ45 table — the KQ44/KQ43 arrangement is the counter-example.
2. Do not edit KQ44 or KQ45 rows. KQ45's two wording defects (marker site, bare `CORPUS.md`) and
   the S192 misclassification are appended qualifications, per CORPUS.md rule 2 and QUALITY.md's
   head rule.
3. KQ46 adds an obligation, no counter; it changes neither C1 nor C2 and is compatible with both.
   C1's kill rule is untouched: KQ46 only reinforces D2B's no-restatement clause.
4. Under KQ46 the three C2 entries must cite lane ids (they will be `S330` and above once appended);
   staged ids `S330/S333/S334/S335/S346/S347/S363` may appear only in the Gate as provenance, in the
   form round 36 used correctly for the URL ("The staged package carried this document as …") but
   with the id swapped for the lane id.
5. Nothing here authorises a rewrite of `round-36.md`; its four affected lines stay as written and
   any id repair is an appended correction row in `round-37.md`, which is what C1 already measures.

## 6. Residual risk and verification gaps

- I did not fetch any URL: my item names none, and the S192/S174/S193 sources are outside that
  authorisation. The S192 finding rests on local committed receipts
  (`round-31-verifier-spotcheck.md:55`, `considerthese/2026-10-24.md:29`) and on the absence of any
  `unverifiable-by-fetch` record in the tree. If the r36 verifier's fetch receipt exists outside the
  lane repo, the classification question reopens; the marker-site defect does not.
- KQ46 as drafted still does not cover an id that appears inside a quoted sentence (a source's own
  text mentioning an id), nor ids in `.ufo` seat outputs. Both are deliberate exclusions: the first
  is a quote, governed by KQ45; the second is scratch, not corpus prose.
- No tool was installed or upgraded; no `pacman` transaction was run. The two read-only checks used
  existing `python3`, `git diff/status` and `grep`.
