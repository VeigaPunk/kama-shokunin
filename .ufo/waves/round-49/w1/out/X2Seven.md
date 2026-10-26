**Verdict:** the seven lines v4 grades that v3 did not are the seven `## Capabilities` head rows at `SCORECARD.md:121-127` (sources-registry, ollama-offline-evidence-replay, live-llamacpp-lifecycle, gguf-declared-identity-replay, context-capacity-receipt, instrument-agreement, pin-watch); each was first written in a dated round section (six in the round-34 table at `29f9d1e1:SCORECARD.md:1911-1916`, pin-watch in the round-41 table at `24aa1d34:SCORECARD.md:2184`) and carried byte-identically into the re-derived head at `dd9f5dc6` — so they are **dated text carried into the head, not an origin artefact**, and the deletion is real (all five/four occurrences, head copy included, were deleted at `0718b6ab` and restored byte-exactly at `82b5e9d3`, so the event stays *restored* under v4). `dd9f5dc6`'s 23 vs 17 is unrelated to v4: the counter's natively-exempt bound omits the gutting term, and the six-line gap is the `## Retired` block (`SCORECARD.md:72-77` at the parent) whose section is gutted (9 lines → window max 4), so v3 and v4 both grade it (and it is held, because the same six lines were re-emitted under `## Historical head sections`).

Seat X2Seven, lane kama, round 49. Measured commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (build), base `438127bc01ff3b99f98468549d58046f932490ef` (round-48 closure). Read-only `git clone --shared` of the lane in my scratch; every number below is re-derived from that clone at the named revision. No tool was installed. No `llama-server` was started (this seat runs no C1 leg).

# 1. Container and contract

- Lane counter (frozen, sha256 matches the preregistration): `tools/round49-append-audit-v4-check.py` = `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945` (prereg C2 `counter_sha256`, verified with `sha256sum`).
- Tool under audit: `tools/append-only-audit.py` at `74558c71` = `5d6c33c0274a886af090e4e5b3310f1530ff185d0f99ed2770a5880faa9eac28`; at `438127bc` = the v3 blob (`git diff` of the two is the v4 delta only).
- Contract row: `registry/append-only-contract.tsv:3` — `SCORECARD.md … exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`; the pointer line `SCORECARD.md:6` carries `re-derived` and names all five titles, so the declaration binds at both commits.
- The v4 delta in the audit path is one condition (`tools/append-only-audit.py:483` at the tip):
  `if s in eligible and org.get(text, frozenset()) & titles:` (v3: `if s in eligible:`), plus the `origins()` helper at `tools/append-only-audit.py:429-449`.
- Counter bound (`tools/round49-append-audit-v4-check.py:353-354`):
  `native = sum(1 for pos, text in deleted_with_pos(...) if psec[pos-1] in ex and org.get(text,set()) & ex)` — the same origin test, but with **no eligibility/gutting term**.

# 2. Definition isolation: the delta is the definition, not the tip

Four runs of the two tool blobs against the same clone (the tool tree comes from `git archive <rev> tools/append-only-audit.py`; see `run-all.sh`):

| tool | `--to` | 0718b6ab SCORECARD.md ungraded | dd9f5dc6 SCORECARD.md ungraded | `summary.ungraded_lines` | exit |
|---|---|---|---|---|---|
| v3 (`438127bc`) | `438127bc` | 72 | 17 | 89 | 0 |
| v3 (`438127bc`) | `74558c71` | 72 | 17 | 89 | 0 |
| v4 (`74558c71`) | `438127bc` | **65** | 17 | 82 | 0 |
| v4 (`74558c71`) | `74558c71` | **65** | 17 | 82 | 0 |

`v3-at-base.json`, `v3-at-build.json`, `v4-at-base.json`, `v4-at-build.json` (events identical across the two tips; only ungraded 72→65, `ungraded_lines` 89→82). The 7 is therefore definition-only, and v4 never ungrades a line v3 did not (the added conjunct can only grade more).

v4 event detail at the build tip (`v4-at-build.json`): `0718b6abbda6 SCORECARD.md deleted 2421 graded 2356 ungraded 65 restored_max 2356 restored_best 82b5e9d3 restored_by 82b5e9d3 held_at_to 2356 status restored`; `dd9f5dc6 SCORECARD.md deleted 31 graded 14 ungraded 17 … status restored`.

# 3. Per-line recomputation (own code, `recompute.py`)

`recompute.py` does not import the tool: it reads blobs with `git cat-file`, computes each line's `## ` section from the parent blob, computes origin as the first blob in `rev-list --topo-order --reverse <tip>` holding the exact byte line (all titles that line holds in that first blob, matching the v4 same-blob rule), and evaluates both predicates per deleted line. It emits `recompute.json` (2421 + 31 line records, each with parent position, parent section, origin commit, origin sections, and occurrence counts at `82b5e9d3` and `74558c71`).

Recomputation reproduces the tool and the counter exactly:

- `0718b6ab` (parent `21945c6125c2`): deleted 2421; deleted lines under an eligible exempt title 72; of those, origin ∩ exempt titles 65; origin non-exempt **7**. All five titles are eligible at this event (`## Axes` 43→max 43, `## Capabilities` 18→max 20, `## Planned` 4→max 17, `## Retired` 4→max 4, `## Saturation` 4→max 4).
- Composition of the 72: `## Axes` 42 exempt-born, `## Capabilities` 18 (= 11 exempt-born + 7 dated-born), `## Planned` 4, `## Retired` 4, `## Saturation` 4. **Preamble-born line count among the 72: 0** — no heading-shift artefact is involved.
- `dd9f5dc6` (parent `0bfd47abdda1`): deleted 31; ungraded 17 = `## Axes` 7 + `## Planned` 9 + `## Saturation` 1; graded 14 = 8 preamble (`None` parent section) + 6 `## Retired`; natively-exempt (no gutting term) 23.

# 4. The seven lines

`seven-lines.tsv` (full text included there; parent positions are `0718b6ab^` = `21945c61`; `held` is the tool's measure `min(deleted_occ, max(0, occ(rev) − K))` with `K = parent_occ − deleted_occ = 0`):

| # | capability | parent pos / section | origin commit | origin section : line | deleted occ | held @82b5e9d3 (lines) | held @74558c71 (occ / lines) |
|---|---|---|---|---|---|---|---|
| 1 | sources-registry | 121 `## Capabilities` | `29f9d1e1b20e` | `## Round 34 — capability repertoire and instrument-registry coverage (2026-10-24)` : 1911 | 5 | 5 (121, 1962, 2216, 2263, 2310) | 5 (8 occ; +2455, 2689, 2781) |
| 2 | ollama-offline-evidence-replay | 122 | `29f9d1e1b20e` | same : 1912 | 5 | 5 (122, 1963, 2217, 2264, 2311) | 5 (8 occ) |
| 3 | live-llamacpp-lifecycle | 123 | `29f9d1e1b20e` | same : 1913 | 5 | 5 (123, 1964, 2218, 2265, 2312) | 5 (8 occ) |
| 4 | gguf-declared-identity-replay | 124 | `29f9d1e1b20e` | same : 1914 | 5 | 5 (124, 1965, 2219, 2266, 2313) | 5 (8 occ) |
| 5 | context-capacity-receipt | 125 | `29f9d1e1b20e` | same : 1915 | 5 | 5 (125, 1966, 2220, 2267, 2314) | 5 (8 occ) |
| 6 | instrument-agreement | 126 | `29f9d1e1b20e` | same : 1916 | 5 | 5 (126, 1967, 2221, 2268, 2315) | 5 (8 occ) |
| 7 | pin-watch | 127 | `24aa1d3485c1` | `## Round 41 — head axes table reconciled to the tree (calibration) and the pin-watch capability (operability) (2026-10-25)` : 2184 | 4 | 4 (127, 2222, 2269, 2316) | 4 (7 occ; +2461, 2695, 2787) |

Facts behind the table (all from `recompute.json` and direct `git cat-file`/`git show` on the clone):

- **First commit holding each text under an exempt title: `dd9f5dc6` for all seven** — the round-42 head reconciliation that created `## Capabilities` by copying the dated capability table. At the parent each text exists in the head **and** in 3-4 dated sections (round 34/41/42/43); at `0718b6ab` **all** occurrences are deleted (occ = 0), so the head copy is not a lone duplicate at deletion time.
- **Where held.** At `82b5e9d3` every occurrence is back at the same line number it had at the parent (`121/1962/2216/2263/2310` … for #1, `127/2222/2269/2316` for #7) and the line at each of those positions is byte-equal to the deleted text — the round-45 restore put each text back where it had been. At `74558c71` those occurrences remain (the head copy stays at `121`; the dated copies shift by +2 to `1964/2218/2265/2312`) and later dated sections (round 45, round 48) hold further copies, which is why the occurrence count rises to 8/7 while the held measure stays at 5/4.
- **Restore arithmetic.** `K = parent_occ − deleted_occ = 0` for each text, so every deleted occurrence must come back for the event to be restored; v4's `restored_max = graded = 2356 = held_at_to` at `82b5e9d3` shows all 65 v4-ungraded + 2356 graded lines are held. The event's status is unchanged by the v4 grading (restored, exit 0).

# 5. Laundering instance or origin artefact?

**Real instance of the origin rule firing on dated text carried into the head; not a laundering attack, not an artefact, and not a false alarm.**

- *Not an artefact.* An artefact would be a line born in the preamble (`None` section — never exempt under `org & titles`) that later fell under a heading, or a section renamed so that old text became exempt. Neither occurs: 0 of the 72 are preamble-born, all 7 origins are dated round sections, and the dated copies still hold the same byte line in the parent.
- *Dated text carried into the head.* The `## Capabilities` head was created at `dd9f5dc6` as a reconciliation copy of the round-34 table (plus the round-41 pin-watch row); every one of its dated-born rows therefore fails `origin ∩ exempt` by construction. The v3 carve-out excused their head deletion; v4 grades it, which is what the docstring's `laundering` clause wants ("dated text moved under an exempt heading and dropped there is graded").
- *What it is not.* This event is the round-45 truncation bug (`0718b6ab`), not a move-and-drop: the dated copies were deleted in the same commit and all copies returned at `82b5e9d3`. So the seven graded lines could not launder a loss past the measure, and no adversary gains anything from the 7-line difference here — grading them only tightens the event by 7 lines that the restore holds.

# 6. Why `dd9f5dc6` is 23 vs 17

The counter's `native` and the tool's `ungraded` differ by exactly the **eligibility (gutted-section) term** the counter deliberately does not recompute (prereg limit: "does not recompute eligibility or the held measures"):

- The 23 = every deleted line whose parent section is one of the five exempt titles the contract names (four occur at this rev) **and** whose origin intersects them: `## Axes` 7, `## Planned` 9, `## Retired` 6, `## Saturation` 1.
- The 17 = the same set minus the six `## Retired` lines, because `## Retired` at the parent has 9 lines and never reaches 9 again in the window (max 4) → ineligible → graded by **both** v3 and v4 (`v3-at-base.json` and `v4-at-base.json` both report 17 for this event).
- The six lines (`six-retired-lines.tsv`): `SCORECARD.md:72-77` at the parent, origin `## Retired` at `ea72c3eae4ec`, text "None. Both assigned axes remain active … context drift have saturated (not observed).". They are graded *and held*: the round-42 rewrite re-emitted them byte-identically under `## Historical head sections (superseded in round 42)` (event lines 165-170, tip lines 168-173), which is why `restored_best = dd9f5dc6` itself and `held_at_to = 14`.
- Consequence for the counter: `native` is a **sound upper bound, tight only when no exempt section is gutted**. At `0718b6ab` it is tight (65 = 65, base control failed at 72 > 65); at `dd9f5dc6` it is loose by exactly the gutting term (6). It cannot distinguish "v4 ungraded exactly the natively exempt lines" from "v4 ungraded fewer lines for some other reason" — my per-line classifier is what closes that gap for this measurement (65 with the identity above).

# 7. My runs of the frozen C2 counter

`c2-counter-build.out` (my clone, tip `74558c71`, exit 0):
```
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
fixture=1 lane=1 scenarios=8/8 met=True
detail: … scenario launder: ok exit 1 (want 1) … native-head: ok … dated-loss: ok … substring: ok … word-token: ok … negated: ok … wildcard-self: ok … wildcard-named: ok
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
```
`c2-counter-base.out` (same clone, tip `438127bc`, exit 1) is identical to the committed `.ufo/waves/round-49/controls/base.c2.out` apart from that file's appended `exit=1` trailer line (`diff` shows only `14d13 < exit=1`): `fixture=0 lane=0 scenarios=4/8 met=False`, `ungraded_lines 89`, `0718b6abbda6 ungraded 72 > natively exempt 65`. So the base control is reproducible from a fresh clone.

# 8. Findings

**F1 (behaviour, measured; calibration-relevant, not a defect).** v4 grades a head copy whose every dated copy survives, and reports the event unrestored. Measured fixture: `fixture-dupe3.sh` (three commits; a line born in a dated section, copied into an exempt `## Capabilities` head, then dropped from the head while the dated copy stays and the section keeps its size): v3 → `exit 0 … ungraded 25 status ungraded`; v4 → `exit 1 … graded 25 status unrestored`, declarations bound under both. This is the semantics class of the lane's seven rows; the lane escapes only because `0718b6ab` deleted the dated copies too. The prereg's limits define origin as the text's first appearance (and name only the born-in-both-places case), and the tool docstring grades moved-and-dropped dated text; neither states that a surviving dated copy leaves a dropped head copy graded *and* unheld. Proposal: add to the C2 limits "a head copy of dated text that also survives in its dated section is still graded, and the surviving copies do not make the deletion restored (measured, `fixture-dupe3.sh`)". This is a calibration statement for the L1, not an edit to the frozen prereg.

**F2 (stale declaration text, proposed diff only).** `registry/append-only-contract.tsv:3` still describes the v3 carve-out: "…are ungraded while they are not gutted (round 48, v3 region)". At `74558c71` that is false for head lines born in a dated section (7 of the 75 lines under the five exempt titles at the tip; all 7 are `## Capabilities` rows at `SCORECARD.md:121-127`, and 0 elsewhere). The note is inert for binding, so nothing fails; it misdescribes the measured rule in the file a reader checks first. Proposed replacement note (full text, tab-5 cells, parses under the v4 tool, verified): `proposed-contract-note.diff`. The round-48 narrative in `corpus/README.md:916-930` is dated text describing v3 at `380bcdff` and needs no change.

**F3 (state, not a defect).** The lane working tree at `122c4ee9` is dirty (`M tools/append-only-audit.py`, `M tools/kama-llamacpp-live.py`, `M SKILL.md`, `M corpus/QUALITY.md`, `M corpus/knowledge/llamacpp-loading-lifecycle.md`, plus untracked round-49 files). The `append-only-audit.py` edit (integration note: round-49 seat K2Negation F1) widens `NEG_WINDOW` with `cannot`, `can't`, curly apostrophes and en/em dashes. It touches `binds`/`selftest` only, so it changes no number in this report (ungraded counts do not read declarations), but every figure here is against the committed blob at `74558c71`, not the working tree.

# 9. Evidence inventory

Everything cited is in `.ufo/waves/round-49/w1/out/X2Seven/`: `recompute.py` (my per-line classifier), `recompute.json` (per-line records for both events), `v3-at-base.json`, `v3-at-build.json`, `v4-at-base.json`, `v4-at-build.json` (definition/tip matrix), `c2-counter-build.out`, `c2-counter-base.out` (frozen counter receipts from my clone), `seven-lines.tsv`, `six-retired-lines.tsv`, `fixture-dupe3.sh` + `fixture-dupe3-c3.diff` (F1, reproducible), `proposed-contract-note.diff` (F2), `run-all.sh` (exact commands), `SHA256SUMS`.

Scratch `/fast/scratch/hyaku/kama-r49/X2Seven` was removed after copying; the clone was `git clone --shared` and the lane's index/jj state was never touched (`git status` above is read-only). Nothing was installed. No services were started or stopped; no `llama-server` process of mine exists.
