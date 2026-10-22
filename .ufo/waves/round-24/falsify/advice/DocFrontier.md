# DocFrontier — falsification of `corpus/README.md` "Frontier correction — round24"

Scope (assigned): attack the latest frontier correction in `corpus/README.md` at the pinned
integrated commit for four claims only — **D4 partial**, **F23 vs T01 distinct**, **no new
knowledge entry / serving capability**, **no silent retirement / scope expansion**. Read-only
production; no full suite; no network payload; one bounded offline grid measurement plus
static source checks.

## Verdict

| Claim | Verdict | Basis |
|---|---|---|
| D4 remains partial | **HOLDS** | Observed: the tool still refuses/does not claim alternates and gitfile channels (`tools/report-landing-audit.py:50-56`); the r23 open-channel list is untouched; no closure claim appears in the round-24 section |
| F23 (genuinely incomplete `--no-checkout`) is distinct from T01 (complete blobless clone) | **HOLDS** | Observed statically **and** measured: F23 → exit 2 naming the absent blob OID; T01 → exit 0 clean, in the current arm and in the frozen arm |
| No new knowledge entry, no new serving capability | **HOLDS** | Observed: `corpus/knowledge/` gained no file; only `corpus/knowledge/error-is-not-a-verdict.md` was appended to (§Round24 exists at line 82); no endpoint/probe sample exists in the round-24 wave; SOURCES ledger has exactly 105 rows |
| No silent retirement / no scope expansion | **PARTIAL** | No frontier item was retired and no numeric promotion or capability was added; **but** two stale r23 corpus statements about F06/F23 "refusals" remain uncorrected in an append-only corpus, and one grid fault row's expected exit moved without any corpus narration (Finding F2). One documentation-precision defect: an incorrect cross-reference antecedent (Finding F1) |

Nothing in the round-24 frontier correction was falsified on substance. The two findings below are
low-severity record-accuracy / disclosure defects, not contract defects.

## Snapshot

- Reviewed commit (detached, scratch clone only): `2e254a1763a9c08aa07fc53081287f506c447d84`
  ("round-24: land completed 64-seat build evidence and explicitly carry residual closure debt")
- Tree: `90d19f20e02caf0c7a52e152f020e98e3c416af3`
- Scratch clone: `/fast/scratch/hyaku/kama-r24/falsify/DocFrontier/repo` (cloned with
  `--no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached at the pinned
  revision; production `.jj/index`, fleet, siblings, operator config untouched)
- `sha256 tools/report-landing-audit.py` = `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`
  (matches the lane's declared source tool digest)
- `sha256 corpus/README.md` = `972f321692895632b03abffbdc1074d7980039ad66ee09c0e352fc16de6ea3dc`
- Grid pinned frozen arm: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`; grid population
  `sha256 46d66867ad5c68a1aceece646228e9c24e2e75c03526ca33bf6db901ba03da81`
- Round-24 ledger rows: `grep -c '^| S[0-9]' corpus/SOURCES.md` = **105** (S102–S105 added;
  S001–S101 changed only in the mutable used-by column; S095 keeps status `rejected` and its
  original `teaches` text — verified against `git diff 0df800e8 2e254a1 -- corpus/SOURCES.md`)

## Measurements (exact commands, exits, token pairs)

All runs are offline fixtures under
`TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/DocFrontier/tmp` in the scratch clone.

1. Bounded two-case grid, both arms — the falsification of the F23/T01 wording:

```
cd /fast/scratch/hyaku/kama-r24/falsify/DocFrontier/repo
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/DocFrontier/tmp \
  python3 tests/report-audit/repo-state-grid.py --arm both \
  --case T01-blobless-partial-clone \
  --case F23-promisor-pack-without-config --json
```
   exit **1** (the exit is the frozen arm's *expected* divergence, not a current-arm failure:
   `arms.current.violations = 0`, `arms.frozen.violations = 1`).
   Token pairs observed:
   - `F23-promisor-pack-without-config` — current arm: exit **2**, reason pin met,
     `stderr_tail`: `181389d343031fd578c6a775ce0889a8b0d is referenced by the history of
     …/blobless but the repository cannot serve it` (content-derived refusal naming the absent
     blob). Frozen arm (4fe9339f): exit **1**, kinds `["unresolved-full-hash"]` — i.e. the
     pre-round-24 auditor treated the same absent cited blob as a *proved absence* (a verdict).
   - `T01-blobless-partial-clone` — current arm: exit **0**, kinds `[]` (clean); frozen arm:
     exit **0**, kinds `[]`. The complete blobless partial clone keeps its correct clean verdict
     in both arms; the round-23 refusal of it was the loss that round 24 restored.

2. Same two cases, current arm only (exit-code evidence for the restored verdict):

```
TMPDIR=… python3 tests/report-audit/repo-state-grid.py --arm current \
  --case T01-blobless-partial-clone --case F23-promisor-pack-without-config --json
```
   exit **0**; `violations 0, contracts_met 1, controls_met 1, faults_met 0, timeouts 0,
   tracebacks 0`.

3. Fixture identity (static, decisive for "F23 vs T01 distinct"):
   - `tests/report-audit/repo-state-grid.py:195-213` (`f_promisor_pack`): clone
     `--no-checkout --filter=blob:none --no-local`, then unsets
     `remote.origin.promisor` / `remote.origin.partialclonefilter` /
     `extensions.partialclone`, and `require(packs and missing != 0, "promisor pack/missing blob
     not observed")` — the cited blob is genuinely absent, asserted by the fixture itself.
   - `tests/report-audit/repo-state-grid.py:596-604` (`t_blobless`): clone
     `--filter=blob:none --no-local` **with checkout** (no `--no-checkout`), so the single blob is
     hydrated → complete.
   - Row kinds: `("T01-blobless-partial-clone", "control", t_blobless, 0, [])` at line 692;
     `("F23-promisor-pack-without-config", "contract", f_promisor_pack, 2, None)` at line 673;
     reason pin `"F23-promisor-pack-without-config": "unavailable required object"` at line 706.
   - Base comparison (`git show 0df800e8:tests/report-audit/repo-state-grid.py`): T01 was
     `("…", "tradeoff", t_blobless, 0, [])` — a declared, ungraded trade — and F23's refusal reason
     was the metadata-derived string `"promisor pack"`. Round 24 changed exactly two rows:
     `T01 tradeoff→control` and `F06` expected exit `2→1` (see Finding F2); every other row is
     byte-identical (verified by diffing the `CASES`/`REASONS` tables base→pinned).

4. "Metadata alone does not refuse / unrelated hole does not block" (static, implementation-level):
   `tools/report-landing-audit.py:429-447` and `:566-582` show the unavailable-evidence refusal is
   reached **only** on the unresolved-token path (`state == "absent"`), and
   `opaque_hole()` (`:705-717`) is consulted only there; `unknown_citation()` (`:689-702`) matches
   only a token that names an object the store references but cannot serve. Tokens that are
   `found`/`ambiguous`/`wrongtype` skip the refusal (`:430-431`), so a known wrong-type object
   keeps the ordinary finding. No blanket completeness precondition exists on any path.

5. Git floor (falsifiable sub-claim "The Git>=2.45 prerequisite remains open … (R23-H2)"):
   - The floor is **inherited, not introduced by round 24**: `git show 0df800e8:tools/report-landing-audit.py`
     line 55 already read `… git >= 2.45 is required.`; the pinned tool keeps it (line 55) and
     `git diff 0df800e8 2e254a1 -- tools/report-landing-audit.py` shows only that line's context
     moved, not the requirement.
   - The floor is real and backed by the ledger's own source: official Git docs read (plain
     HTTPS, no payload): `Documentation/git.txt` at tag `v2.44.0` contains **0** occurrences of
     `--no-lazy-fetch`, at `v2.45.0` **1** occurrence → `--no-lazy-fetch` is the 2.45 feature the
     isolation depends on. `Documentation/rev-list-options.txt` contains `--missing` already at
     `v2.43.0` (6 hits), so the `--missing=print` primitive the repair uses does **not** raise the
     floor above 2.45, and `--missing=print-info` / `--missing=only` are not used anywhere
     (`grep -n "print-info\|--missing=" tools/ tests/ SKILL.md` → only `--missing=print`), which
     satisfies `oracle-supplement-2.json` `version_constraint`.
   - R23-H2 is recorded as carried, not discharged: `corpus/lessons/round-24.md:84,144`,
     `SKILL.md:852-853`, `SCORECARD.md:1212-1214` ("remains an unresolved R23-H2 operator
     decision, not older-Git restoration").

6. "No new knowledge entry / no new serving capability / no numeric promotion":
   `git diff --name-only 0df800e8 2e254a1 -- corpus/` → `corpus/QUALITY.md`, `corpus/README.md`,
   `corpus/SOURCES.md`, `corpus/knowledge/error-is-not-a-verdict.md`, `corpus/lessons/round-24.md`
   (all modifications; no new `corpus/knowledge/*` file). `git ls-tree -r 2e254a1 corpus/knowledge/`
   → 18 files, identical to base. `grep -rl "kama-probe\|MODEL_OK\|/v1/models\|served-model"
   .ufo/waves/round-24/` → only two files, and both matches are prose text (no endpoint sample,
   no probe run). `SCORECARD.md` round-24 block states "No numeric promotion or new capability".

7. "No silent retirement": `git diff 0df800e8 2e254a1 -- corpus/README.md` is **+22 / −0** — no
   existing line of any frontier section was deleted or rewritten; the round-23 declared trade
   (line 330-331) and its open-channel list (lines 326-329) remain filed verbatim, and the
   round-24 lesson carries them forward as named residual debt (`corpus/lessons/round-24.md`
   §"Named residual debt carried, not discharged": RowF12/RowF21/RowF22/RowF23/RowF26/RowC04,
   ExecSecondLanded, ExecAmbiguityFixture, RevengeGitfile, CritTradeoffHarm H2, SentinelDoSW2,
   ConnSiblingTools, N01/N02/N03/D02/D03). The r23 open D4 channels (O01/O02 alternates and
   gitfile, `--shared`-of-partial bypass, prefix-ambiguity overwrite, duplicate Landed sections,
   errata CR splitting, `--errata` FIFO, memory ceilings, sibling tools) are still listed at
   `corpus/README.md:326-329` and are still true of the pinned tool (docstring
   `tools/report-landing-audit.py:50-53`: "Objects borrowed through objects/info/alternates or a
   .git gitfile still resolve as local, and other repository-local channels are not claimed").
   The amended-oracle discipline is honoured: `preregistration.json` `expected_after[3]` stays
   filed and is recorded as withdrawn/not-achieved in `corpus/lessons/round-24.md` §Mistakes and
   `corpus/knowledge/error-is-not-a-verdict.md` §Round24 (lines 109-113) — never relabelled
   passed.

## Findings

### F1 — LOW (documentation precision): the correction's antecedent is wrong/ambiguous

`corpus/README.md:351` — "Correction to **the previous paragraph's** paired-marker wording: F23 is
a genuinely incomplete `--no-checkout` fixture, not the complete T01 witness."

Observed: the immediately preceding paragraph in the same section (`corpus/README.md:343-349`)
contains no paired-marker wording and never mentions F23 or T01. The paired wording the sentence
corrects lives 21 lines earlier in the round-23 section (`corpus/README.md:330-331`: "Declared
trade: a complete blobless partial clone or paired promisor pack is refused where frozen gave a
verdict") and in `corpus/lessons/round-23.md:206-209` ("a complete blobless partial clone (T01)
and a paired promisor pack without promisor config (F23) are refused (exit 2) where frozen gave
a verdict"). As written, a reader following "the previous paragraph" lands on text that does not
contain what is being corrected.

Minimal correction (append-only, one line, no rewrite of filed bytes):

> `corpus/README.md:351` — replace "the previous paragraph's" with
> "the round-23 frontier disposition's declared-trade wording
> (`corpus/README.md:330-331`; `corpus/lessons/round-23.md:206-209`)".

Optional second half of the same line (makes the correction self-contained, since the sentence
currently states only F23's identity and never says what happened to T01):

> append: "; T01 is the complete blobless partial clone and is now a graded control whose clean
> verdict is restored (`tests/report-audit/repo-state-grid.py:692`)."

### F2 — LOW (record accuracy / disclosure): the F06 fault row's expected exit moved from 2 to 1
with no corpus narration, leaving two stale r23 statements

Observed:
- `git diff 0df800e8 2e254a1 -- tests/report-audit/repo-state-grid.py`:
  `("F06-lazy-fetch-command", "fault", f_lazy_fetch, 2, None)` → `(…, 1, […])`, and the reason pin
  `"F06-lazy-fetch-command": "partial clone"` was dropped (F06 no longer refuses).
- The only narration of that change is the test file's own docstring
  (`tests/report-audit/repo-state-grid.py:14`: "gives F06 the ordinary local missing-citation
  findings"). `corpus/README.md` and `corpus/lessons/round-24.md` do not mention F06.
- Consequently two filed r23 statements no longer describe the pinned rows:
  `corpus/lessons/round-23.md:40` ("Supports F06/F23 refusals.") and
  `corpus/lessons/round-23.md:135` ("F06, F13, F16, F26 pin current's own refusal wording").
  F23 still refuses (exit 2) but with a content-derived reason, and F06 no longer refuses at all.

This is a disclosure/record-accuracy gap, not a contract defect: the F06 row's fault premise is
unchanged (`f_lazy_fetch`, `tests/report-audit/repo-state-grid.py:274-289`, still asserts the
configured `core.sshCommand` marker ran during premise setup) and the row kind is still `fault`;
the exit change follows the announced local-evidence rule ("metadata alone does not refuse").
Because r23 bytes are immutable, the corpus currently reads as if F06 is still a refusal row.

Minimal correction (append-only; do not edit the r23 lesson):

> append one line to `corpus/lessons/round-24.md` (e.g. in §"Named residual debt carried, not
> discharged" or a new one-line correction subsection): "Grid row F06's expected exit moved 2
> (partial-clone refusal) → 1 (ordinary local missing-citation finding) under the round-24
> local-evidence rule; the r23 characterisations at `corpus/lessons/round-23.md:40` and `:135`
> ('Supports F06/F23 refusals', 'F06 … pin current's own refusal wording') no longer describe the
> current rows. The fault premise and row kind are unchanged."

### F3 — INFORMATIONAL (frontier index completeness, no correction required)

`corpus/README.md:343` "D4 remains partial." is accurate, but the round-24 frontier paragraph's
"Other frontier unchanged" list (lines 354-356) is the same short list as round 23 and does not
enumerate the remaining round-23 D4 channels (O01/O02 alternates/gitfile, `--shared`-of-partial
bypass, prefix-ambiguity overwrite, duplicate Landed sections, errata CR splitting, `--errata`
FIFO, memory ceilings, unisolated sibling tools `citation-provenance.py` /
`sources-append-only.py`). Nothing was retired — they remain at `corpus/README.md:326-329` and in
the round-24 lesson's residual-debt list — but a reader of the newest frontier paragraph alone
under-reads the open D4 debt. Optional one-clause addition to line 343: "…remains partial; the
round-23 D4 channels listed above (lines 326-329) stay open."

## Observed vs inferred

Observed (directly executed / read at the pinned revision):
- All grid exits, kinds, reason strings and the named blob OID in §Measurements 1-2.
- The fixture identities and the two changed grid rows (§Measurement 3).
- The refusal call sites and their guarding conditions (§Measurement 4).
- The 2.45 floor inheritance and the official `--no-lazy-fetch` / `--missing` version facts
  (§Measurement 5; official Git documentation read over plain HTTPS, no payload, no ledger row
  added — this review is read-only, so no `corpus/SOURCES.md` row was created for these reads;
  the facts are already covered by filed rows S089 and S102).
- Corpus file-level facts: no new knowledge file, 105 ledger rows, README diff +22/−0,
  S095 still `rejected` with unchanged `teaches`, no endpoint sample in the wave.

Inferred (reasoned, not executed here):
- That the round-23 "declared trade" sentences are the intended referent of the round-24
  "correction" wording (F1) — the content match is exact, but the reference as written points at
  the wrong paragraph.
- That the F06 exit change is a consequence of the announced rule rather than a silent weakening
  (F2): the row kind and premise are unchanged and the exit moves *toward* an ordinary verdict,
  but I did not re-run the F06 row (out of my assigned measurement scope), so I have not observed
  the F06 row's current-arm behaviour itself.

## Unverified items (not claimed either way)

- The outside-closure MANIFEST `rounds[428]` content itself ("operability and quality were
  harmed", `rejected-harmed`) is outside-lane and not present in this repository; the README's
  first sentence of the round-24 section rests on it. I verified only that the corpus records the
  judgement consistently (`corpus/lessons/round-24.md:4-7`, `SCORECARD.md` round-24 block,
  `LOG.md` round-24 entry), not the outside artefact itself.
- The opaque-dependency half of the README claim ("hidden behind an opaque dependency, is not a
  proved absence"): implementation evidence only (static, §Measurement 4). The graded
  opaque-tree cells live in the 47-cell promisor grid (`oracle-supplement-2.json`), which I did not
  run — out of my assigned scope, and PM08 was not executed at any point (static only).
- The strong `names_any_of` grader and the fixed-47 expectations (original 44 + 3 independent
  opaque cells): not re-run here; other falsify lanes own them.
- The 69-report / 40-of-56 FIFO-identity corrections recorded in `LOG.md` are outside this
  assignment's claim set.
- F06's current-arm exit (see above) and the other 40+ grid rows were not executed; the full
  grid was deliberately not run.
- Fixture-hazard caveat (peer-reported, PG43 lane, `KamaR23-2.CaseFleetBlobless`): a kept
  blobless clone whose `remote.origin.url` still points at a reachable local `file://` origin can
  be laundered into a false "clean" by any git probe issued **without** `--no-lazy-fetch` (one
  stray `git cat-file -e HEAD:<path>` materialises the missing blob). My measurement is not
  exposed to it: I drove only the grid's own harness (whose helpers are `--no-lazy-fetch`), the
  auditor under test runs every git call with `--no-lazy-fetch`, the temp root is deleted by the
  harness, and I issued no manual git probe against a blobless fixture. Recorded here so no one
  re-uses a kept blobless fixture without `--no-lazy-fetch`.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/DocFrontier.md`
  (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocFrontier/`
  — measurement artefacts copied from scratch:
  - `grid-T01-F23-both-arms.json` (exit 1; frozen-arm divergence only)
  - `grid-T01-F23-current-arm.json` (exit 0; violations 0)
  - `official-git-floor-readings.txt` (the plain-HTTPS doc extracts behind §Measurement 5)
- Scratch (not part of the report): `/fast/scratch/hyaku/kama-r24/falsify/DocFrontier/{repo,tmp,*.json,rev-list-*.txt,rlo-*.txt,git-*.txt}`.

No production file was modified: `git status` in `/home/vgpnk/Projects/shokunin/kama-shokunin`
shows only the untracked `.ufo/waves/round-24/falsify/` wave directory (created by the wave
harness), and no `.jj/index`, fleet, sibling, operator-config, routing or service state was
touched. No installs were performed in this lane (no tool was needed beyond `git`, `python3`,
`curl`, `grep`).

Report: .ufo/waves/round-24/falsify/advice/DocFrontier.md
