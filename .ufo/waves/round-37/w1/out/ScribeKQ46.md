# ScribeKQ46 — final text for QUALITY.md criterion KQ46

Round 37, wave 1, seat ScribeKQ46. Deliverable is draft text only; `corpus/QUALITY.md` was not
edited by this seat (observed mtime 2026-10-24 22:42, before this seat started).

## Behavior

Read `corpus/QUALITY.md` (322 lines; KQ44 at line 316, KQ45 block at 318-322), the routed
defect `corpus/lessons/round-36-verifier-spotcheck.md` §6 item 2 (lines 179-190), and the three
wrong citations it corrects at `corpus/lessons/round-36.md` lines 39, 41, 43. Re-derived every
id the draft cites against the staged artifact, read-only:
`/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` and
`/home/vgpnk/Projects/shokuknow/merge/kama/amendments/corpus/knowledge/endpoint-health-probe-conventions.md`.
Receipt: `.ufo/waves/round-37/w1/out/ScribeKQ46/derivation.md`.

Dependency gap: `ReviewQuality`'s draft (`.ufo/waves/round-37/w1/out/ReviewQuality.md`) does not
exist — the seat is still `"agentId": null` in `w1/run.json:152-160` and was never spawned, so no
draft was available to reconcile against. This row is derived independently from the spotcheck
item and the artifact; if `ReviewQuality` later lands a tightening, the L1 should compare, not
assume agreement.

## Deliverable — paste block (heading + table row, QUALITY.md style)

```markdown
## Criterion added — round 37: a cited id range is a claim, re-derived at its artifact

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ46 | An id, id list or id range copied from a staged artifact, a foreign campaign, or a previous lesson is a claim: it is re-derived against the artifact that carries it before it is cited — each id resolved to that artifact's row for the document the sentence names (a knowledge entry's own `source:` lines count as that artifact), a range expanded to the ids the artifact actually carries rather than transcribed by its endpoints, and the artifact path and the read recorded in the round. An id the artifact does not carry is recorded as unresolved/foreign; an id adopted into the lane registry is cited only after its lane row exists. | A range copied from a previous lesson or from an earlier draft of the same sentence and never re-derived; an id that resolves at the artifact to a different document than the sentence cites (`S366` is the AWS SageMaker inference-code page, `S372` a kama round-4 evidence artifact, `S391` the Azure ML BYOC contract — none is `native_api.mdx` or `http_server.py`); a range whose endpoints exist while its interior ids name unrelated documents (`cites S331-S334` for the rows the staged file lists as `S332`, `S336`, `S337`, `S338`, `S339`); or repairing the citation by rewriting the original lesson instead of appending a correction row that names each wrong id. Limit: this criterion requires id-level re-derivation at the artifact, not a fresh fetch of the cited URL (quote fidelity at the cited anchor stays under KQ45), and an id absent from the lane's own `SOURCES.md` is marked staged with its artifact path, never rejected for that absence alone. | `lessons/round-36-verifier-spotcheck.md` §6 item 2 (D2): the round-36 Gate cited five staged ids from an earlier campaign (`S366`→`S371`; `S359`, `S360`, `S372`, `S391`→`S364`, `S365`, `S377`, `S396`) and one copied range (`cites S331-S334` → `S332`, `S336`, `S337`, `S338`, `S339`); every reject decision stood, only the id evidence was wrong, and the fix was an appended correction, never a rewrite of `lessons/round-36.md`. |
```

## Gates / checks performed

- Style conformance: heading matches the last two blocks (`## Criterion added — round 36: ...`,
  `## Criterion added — round 33: ...`); four-column header and separator reused verbatim;
  one physical line per row; no `|` inside any cell; ids backticked; em dash used as in the corpus.
- Id truth: each id in the reject and motivating-lesson cells was resolved at the staged
  registry — S332 (vLLM engine args), S336 (SGLang in llm-d), S337 (Compose reference),
  S338 (Dockerfile reference), S339 (blackbox_exporter README), S359 (vLLM health API),
  S364/S365/S377/S396 (`http_server.py`), S366 (AWS SageMaker inference code),
  S371 (`native_api.mdx`), S372 (kama round-4 evidence artifact), S391 (Azure ML BYOC).
- Range truth: the staged `endpoint-health-probe-conventions.md` `source:` lines 6-10 cite
  `S332`, `S336`, `S337`, `S338`, `S339`, so the corrected range in the row matches the file,
  not its filename.
- Registry bound: the lane's `corpus/SOURCES.md` currently ends at S329, so none of these ids is
  lane-resolvable at this revision; the row's "unresolved/foreign" clause and its limit clause
  state that, and the row does not claim the lane registry already carries them.
- Counting: the "five staged ids" in the motivating cell are exactly S366, S359, S360, S372,
  S391 — the five D2 corrects on that line; the range correction is counted separately and is
  not folded into the five.
- No predicate touched: C1/C2 text, `tools/round37-statement-audit.py`,
  `tools/round37-coverage-audit.py`, `SCORECARD.md` and the controls were not read-for-edit or run.

## Touched surfaces

- Wrote: `.ufo/waves/round-37/w1/out/ScribeKQ46.md` (this report).
- Wrote: `.ufo/waves/round-37/w1/out/ScribeKQ46/derivation.md` (seat scratch).
- Read only: `corpus/QUALITY.md`, `corpus/lessons/round-36-verifier-spotcheck.md`,
  `corpus/lessons/round-36.md`, `corpus/SOURCES.md`, `w1/run.json`, `w1/spec.json`,
  and the two staged files named above.
- Not touched: `corpus/QUALITY.md`, `corpus/lessons/round-37.md`, `corpus/SOURCES.md`,
  `MISSION.md`, `SCORECARD.md`, `LOG.md`, `considerthese/`, the jj/Git state, sibling lanes.
- No tool installed or upgraded this seat.

## Findings

1. The criterion the spotcheck asks for is narrower than "verify every citation": it is
   *resolvability at the named artifact* — an id that the artifact carries for the named
   document, or an explicit unresolved/foreign mark. The row keeps that boundary and hands
   quote-level fidelity back to KQ45, so the two criteria do not double-count one defect.
2. The round-36 defect has two shapes, not one: a copied **list** whose ids resolve to the wrong
   documents (S366/S359/S360/S372/S391) and a copied **range** whose endpoints alone are
   plausible while the interior ids are unrelated (`S331-S334` vs the file's
   `S332, S336, S337, S338, S339`). The row rejects both explicitly; a range-only criterion
   would have missed the five-id list, and a list-only criterion would have missed the range.
3. The lane registry bound (S329) is why "absent from `SOURCES.md`" cannot be the test: at this
   revision every staged id is absent by construction. Treating that absence as the defect would
   reject the correct staged citations too, which is why the row keys on the artifact instead.
4. `ReviewQuality` never ran, so its intended tightening/objection was not available; the row's
   limit clause (id-level only, no URL re-fetch) is this seat's own attempt at the same
   guardrail. Reconciliation against that draft is open for the L1.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-37/w1/out/ScribeKQ46.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-37/w1/out/ScribeKQ46/derivation.md`
