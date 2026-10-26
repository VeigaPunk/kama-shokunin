# S9Readme — round-46 `## Frontier` disposition draft

**Verdict: drafted, and the wave's own bytes correct its brief — the C1 population splits 73 byte-identical / 18 changed (not 71/20), and the 20-row reading list omits S479, the one changed-file row it does not name; a ledger assembled from the "71 mech + 20 read" split leaves a row unverified and C1 at `met=False`.**

Seat: S9Readme (leaf, scribe). Deliverable: `.ufo/waves/round-46/w1/out/S9Readme/frontier.md`
(the section text only, ready to append to `corpus/README.md` after `## Frontier disposition — round 45`).
No lane file was edited, no counter or preregistration touched, no service started, no git/jj
mutation, no tool installed.

## 1. What the draft says (and where each number comes from)

`frontier.md` is one `## Frontier disposition — round 46` block: the C1 re-verification at
b11906, the b11906 live re-run, then frontier bullets (S013, S022 + S002–S004, the floating
series, the 10 off-population llama.cpp rows, the next release trigger, K05, round-45 D1) and
the append-only-audit paragraph. Every figure traces to a command below or to a wave seat's
published artifact, both named in the draft.

## 2. C1 ground, independently re-derived (read-only, bare clone)

Command and receipt: `python3 c1_probe.py > probe.json` (exit 0; script and JSON copied into
this seat's out dir). It reads the 91 rows of `registry/release-recheck-b11889.tsv`, resolves
`pin_blob`, b11889 blob and b11906 blob for each path, and tests each range pair.

| fact | value | command |
|---|---|---|
| population rows | 91 | probe `rows` |
| file byte-identical b11889..b11906 | **73** | probe `b89_b06_same` |
| file changed | **18** (17 `server-context.cpp`, 1 `server-models.cpp`) | probe `b89_b06_same` |
| classes | unchanged-file 6 (S015, S059, S106, S128, S129, S131), holds 82, holds-reworded 3 (S037, S043, S108) | probe `pin_blob==b06_blob` / b11889 verdict |
| changed ids | S042 S060 S109 S114–S125 S133 S138 S479 | probe |

Release identity, in `/fast/scratch/hyaku/kama-r46/L1/llama.git`:
`git rev-parse b11906^{commit}` → `4d71b42fd87db24b8b7c808c151b713aa4459cfd`;
`git rev-list --count d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd87db24b8b7c808c151b713aa4459cfd`
→ `17` (exit 0).

Changed-file rows are machine-`holds`, not reader calls: the single commit that touches these
files, c6fb3b5be, shifts `server-context.cpp` by +3 lines with 6 hunks none inside a pinned
range (`.ufo/waves/round-46/w1/out/U1DiffCtx/map.md`, §Hunks and §Row map: every row
`text-equal at b11906`), and S479's `server-models.cpp` ranges are unshifted and text-equal
(my probe: `same_line_text_equal=true`, `pin_text_present_at_b11906=true`). Five rows
(S042, S060, S109, S133, S138) fail a *joined multi-range* substring search at b11906 because
their ranges are non-contiguous; per element every pin range is present, which is what the
counter compares.

The three `holds-reworded` rows sit on `server.cpp`, byte-identical at b11889 and b11906
(X1Rel `run.txt` step 6: pin and release blob both `b6ebf752…`), so their b11889 witnesses
carry; witness feasibility re-checked mechanically (`witness-check.txt`):
S037 3/2 candidates, S043 2/4, S108 1/1 (`witness_pin` in P not in the b11906 file,
`witness_new` in R not in the pinned file, both ≥ 12 collapsed chars, notes 348/857/378 chars).

On-release composition, using the frozen counter's own `population()`/`cells()`/`ROW` against
`corpus/SOURCES.md` (`onrelease-composition.txt`): 226 registry rows, 178 `on-release`, 96
llama.cpp-citing, 82 other (`docs` 66, `code` 9, `spec` 3, `own-work` 2, `tool` 1, `community`
1; `mined` 70, `queued` 5, `rejected` 7); the llama.cpp rows outside the rule are exactly 10
(S026, S028, S038, S041, S046, S055, S477, S482, S484, S485), matching
`.ufo/waves/round-46/w1/out/K1Pop/rows.md`.

## 3. Other frontier facts the draft uses, and their provenance

| claim in the draft | evidence (path, verbatim value) |
|---|---|
| b11907 = `4b851fbe…` highest `bN` tag, 1 above b11906, 7,461 `bN` tags | `.ufo/waves/round-46/w1/out/X1Rel/run.txt` step 2 (ls-remote 2026-10-26T19:57:59Z, exit 0) |
| `releases/tags/b11907` 404 at the sample | `.ufo/waves/round-46/w1/out/X1Rel/release-b11907.404.json`; `U9Pins/pins.md` §1 |
| pin-watch `pin=b11755 newest=b11907 newer=131 status=behind`, exit 1 | `U9Pins/pins.md` §1 (live `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv`) |
| v0.7.0 = `620d2225` = b11669, 86 commits behind b11755, 237 behind b11906 | bare clone `git rev-parse v0.7.0^{commit}` → `620d2225cc436ab0b001e3200e590e3b286ef9ab`; `rev-list --count v0.7.0..b11906` → `237`; `v0.7.0..b11755` → `86` |
| S002–S004 and S022 teaches hold today; S013 live holds but cited revision contradicts (proposed pin `98acec40…`) | `U9Floating/rows.md`; `U9Floating.md` verdict |
| b11906 live run 11/11, exact health body, exact 503 envelope, `/metrics` 501, SIGTERM-only | `X1Live.md` §§1–3; `X1Replica.md` §§1–3 (independent install, own download) |
| S477 records highest b11887 / 115 above b11755 at 2026-10-25T20:03:21Z | `corpus/SOURCES.md:230`; K1Pop F2 (re-derived 130 at b11906; 30d recheck due 2026-11-24) |
| `git grep v1/metrics` at b11906 finds nothing (S026 rejection stands) | `git -C <bare> grep -c "v1/metrics" 4d71b42f…` → no output, exit **1** |
| append-only audit 5 events, 3 restored by 82b5e9d3, 2 SCORECARD partials | `python3 tools/append-only-audit.py --repo <lane> --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --json` → exit **1**, `commits=294 events=5 restored=3 partial=2 unrestored=0` (`aoa-4a2a4d55.json`) |
| head re-derivation is the lane's own documented rule | `SCORECARD.md:6` (head sections “re-derived from the tree by `tools/round42-selfdesc-reconcile.py`”) |
| b11906 release row + live-receipts row drafted as S486/S487 | `.ufo/waves/round-46/w1/out/S1Row/rows.md` §§2–3 (ids are proposals; L1 assigns `S4NN`) |

## 4. Findings

**F1 — the brief's 71/20 split is wrong; the machine split is 73/18 (documentation premise,
not a frozen artifact).**
`.ufo/waves/round-46/w1/spec.json` items 30 (K1MechA) and 31 (K1MechB) say “of the 71
population rows whose file blob is identical at b11889 and b11906”;
`.ufo/waves/round-46/w1/out/S9Lesson/round-46.md:13` repeats “the other 71 rows' files are
byte-identical”. Machine truth (probe): 73 identical, 18 changed. The wave's own SOURCES
section already states the correct figure (`.ufo/waves/round-46/w1/out/S1Section/section.md:11`:
“73 rows' files are byte-identical between b11889 and b11906, across 14 files”).
Command:
`python3 .ufo/waves/round-46/w1/out/S9Readme/c1_probe.py | python3 -c "import json,sys;d=json.load(sys.stdin)['detail'];print(sum(r['b89_b06_same'] for r in d),sum(not r['b89_b06_same'] for r in d))"`
→ `73 18`.
Effect: `71 + 20 = 91` only if the mech set silently drops two of the 73; enumerating by
`git rev-parse` gives 73, so the two seat reports cannot both be complete *and* total 71
without an omission. Proposed fix (integration step; the contract stays frozen): build the
ledger from the counter's `population()` over the base tree (91 ids) and fill every id, and
union K1MechA/B (73 identical-file rows) with all 18 changed rows rather than trusting the
71/20 arithmetic.

**F2 — S479 is absent from the 20-row reading list though its file changed.**
`.ufo/waves/round-46/w1/out/U1DiffCtx/map.md:51`: “S479 is NOT in the brief's list of 20 rows
to read but its file is not byte-identical; the real changed-file row set is the 17
server-context.cpp rows + S479 = 18.” If the ledger is assembled from “71 identical + 20 read”,
S479 is in neither set → `unverified=1` → C1 `met=False`. It needs no reader (ranges
unshifted, text-equal; probe `same_line_text_equal=true`, `pin_text_present_at_b11906=true`),
but its row must exist. Proposed fix: file S479 as `holds` with its b11889 `pin_lines`
`2329,2378-2379` and `release_lines` `2276,2325-2326` (both text-equal at b11906), or add it
to the reading list.

**F3 — the C1 counter assumes the release commit instead of deriving it.**
`tools/round46-release-recheck-audit.py:102-103` freezes `RELEASE = "b11906"` and
`RELEASE_COMMIT = "4d71b42fd…"`; `check_row()` never runs `git rev-parse b11906^{commit}`
(K1Pop F1). Today they agree, so this round is unaffected; a tag that moved would let the
counter report `met=True` for a false “re-verified at release b11906”. Proposed fix for the
next counter (no edit this round): resolve `<RELEASE>^{commit}` from `--upstream` and exit 2
on disagreement with `RELEASE_COMMIT`. Recorded in the draft as a frontier item.

**F4 — S477 teaches a moving count and no recheck population owns it.**
`corpus/SOURCES.md:230` records “highest bN tag b11887 … 115 bN tags above b11755” at
2026-10-25T20:03:21Z; the b11906 clone re-derives 130 and the live ls-remote 131 (with b11907).
K1Pop F2; not a defect of this round's claim, and the draft lists it as frontier (30d not due
until 2026-11-24).

**F5 — S125's b11889 note quotes a pre-refactor expression.**
`.ufo/waves/round-46/w1/out/U1DiffCtx/map.md` §Row map, S125 row: the note says
`chat_params.allow_audio` is `mctx ? mtmd_support_audio(mctx) : false (release 1709)`; at
b11906 line 1712 is `mtmd_cap.audio` filled at 1401 by `mtmd_helper_get_capabilities`. The row
still holds; the b11906 note must cite 1712/1401. Wording, not claim — no flag is owed.

**F6 — the draft's histogram depends on a ledger that did not exist at draft time.**
`registry/release-recheck-b11906.tsv` was absent for the whole seat (checked at start and
again at write time; `ls` exit 2). The draft's “unchanged-file 6, holds 82, holds-reworded 3,
drifted 0, removed 0” is machine-derived (probe) and must equal the integrated ledger's
counts before commit. If a seat files any changed row conservatively as `holds-reworded`, the
README sentence and the no-flag sentence need updating with it. This is a sequencing note for
the L1, not a claim that the counter ran.

## 5. Not run / limits (honest boundary)

- `tools/round46-release-recheck-audit.py` was **not** run by this seat: it requires the
  ledger, which does not exist yet. No `valid/unverified/met` line is claimed here.
- `.ufo/waves/round-46/tools/check-fragment.py` was not run (this seat produced no ledger
  fragment).
- No endpoint was sampled and no serving runtime was started or stopped by this seat; the live
  facts cited are seats X1Live/X1Replica's receipts, read only.
- No file in the lane, fleet root, sibling lanes or `shokuknow` was written; no pacman, no
  package manager, no tool installed. Scratch `/fast/scratch/hyaku/kama-r46/S9Readme` removed
  after the receipts were copied out.
- Out of scope (other seats): the ledger itself, the SOURCES section, the SCORECARD capability
  row, the lesson, the sample control, the C2 counter run.

## 6. Artifacts written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/probe.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/c1_probe.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/witness_check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/witness-check.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/onrelease-composition.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme/aoa-4a2a4d55.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Readme.md` (this report)
