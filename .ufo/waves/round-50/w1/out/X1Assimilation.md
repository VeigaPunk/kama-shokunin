# Round 50 · X1Assimilation — shokuknow assimilation pre-checks (kama)

**Verdict:** the id-collision guard is sound but the merge package is **not appendable as shipped** — the kama slice collides on **9 ids** (every one a document the lane already holds, so: drop, do not renumber), 90 of 142 staged rows are census `E01` and 24 more re-cite documents already adopted under another id; the seven-row quarantine slice carries **no fabrication** (3 cells are not quotes at all, 3 are folding artifacts, 1 is half lane-summary), and the census gate on a scratch mirror + 119-row normalized block is **exit 0** once the known round-50 lesson exists (exit 1 today, from exactly the three pre-existing `S496–S498` `used-by` misses).

Seat: leaf, calibration axis. Nothing in the lane, fleet repo, shokuknow or PATH was written; the counters/preregistration/controls were not touched.

---

## 1. Id collision — NON-EMPTY (9)

Recipe exactly as in `scripts/hyaku/lane-addendum.md` lines 388-394, `LC_ALL=C`,
`A=<lane>/.ufo/waves/round-50/X1Assimilation`:

```
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <lane>/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' shokuknow/merge/kama/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
$ comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"
reg=239 staged=142 collisions=9
S330 S333 S334 S335 S346 S347 S352 S353 S363
```
(exit 0; files: `.ufo/waves/round-50/X1Assimilation/{reg-ids,staged-ids,collisions}`
plus the write-up `collision-report.md`.)

**All 9 are already-adopted documents, not open work.** Each lane row exists,
is `mined`, and carries the same URL: `corpus/SOURCES.md:216` S330, `:217` S333,
`:218` S334, `:219` S335, `:220` S346, `:221` S347, `:222` S363, `:223` S352,
`:224` S353. The lane's rows are the re-anchored adoptions (S330 lane
`§Feature Support (admonition note)` vs staged `§Scheduler`), and
`corpus/lessons/round-37.md:59-70` records adopting S330/S333/S334/S335/S346/
S347/S363 from this same package "by the staged ids carried by the same
documents". The staged package was simply never pruned.

Action: adopt nothing for these ids; **no renumber** (an id shifted by arithmetic
repairs one citation and breaks the next — lane-addendum line 399).

**A second collision surface the id check cannot see.** Of 108 URL-bearing staged
rows (34 carry no URL — own-work evidence artifacts), 33 cite a document the lane
already holds: the 9 above plus 24 adopted under a *different* id
(`S331→S196 S332→S327 S340→S205 S341→S206 S344→S209 S358→S223 S364/S365/S377/S396→S329
S371→S328 S378→S478 S394→S479 S420/S440/S454/S462→S004 S421→S029 S430→S480
S431/S441/S463→S481 S460/S471→S016`). Four of those (S331, S340, S341, S344)
repeat the lane row's `scope` cell **verbatim** → census `E04` on append.

## 2. Guard proof — indented collision is caught; column-zero-only false-greens

Scratch registry with a `  | S002 |` row (2 leading spaces), staged set `S002, S999`:

```
$ bash scripts/sources-census.sh validate --file $S/guard/corpus/SOURCES.md
file	W03	S001 mined but unused
file	W03	S002 mined but unused
file	ok	$S/guard/corpus/SOURCES.md
exit=0                       # the indented row is census-valid, and counted
$ bash scripts/sources-census.sh census --file $S/guard/corpus/SOURCES.md | head -1
file	rows	2

$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' … | grep -oE 'S[0-9]+' | sort   # S001 S002
$ comm -12 reg-ids-maintained staged.ids        -> S002        (1 line, non-empty)
$ grep -oE '^\|[[:space:]]*S[0-9]{3,}' … | …                            # S001 only
$ comm -12 reg-ids-zero staged.ids             -> (empty)     (0 lines)
```
Second layer: appending a second indented `| S002 |` row gives
`file E03 S002 duplicate id`, exit 1. Guard not broken; the failure mode the
maintained pattern exists to prevent is reproduced. Full transcript:
`.ufo/waves/round-50/X1Assimilation/guard-proof.md`; fixtures
`w1/out/X1Assimilation/guard-fixture-{ordinary,indented-duplicate}.md`,
`guard-collisions-{maintained,column-zero}.txt` (1 and 0 lines).

## 3. Quarantine slice — 7 rows, hand-checked against today's fetches

Slice (`awk -F'|' -v l='kama' …`, register lines 92-98): `S200 S202 S206 S210 S211
S224 S230`, all classed `payload-absent`. Every cited source was fetched live
2026-10-26 (`curl -sSL --max-time 60`), all HTTP 200. Verdicts (full evidence in
`.ufo/waves/round-50/X1Assimilation/quarantine-verdicts.md`):

| id | fetch | verdict |
|---|---|---|
| S200 | arXiv abs, 43 012 B | cell `DOI not in Semantic Scholar` ×0 on the page (only a `api.semanticscholar.org` sidebar link); it is an `s2` error string from a lane **note** (`quote-lint-full-v5.json` findings[574], `binding: id`). **Cell is not a quote** — refuse the cell, not fabrication |
| S202 | Docker Compose services, 887 026 B | **present**: `service_healthy: Specifies that a dependency is expected to be "healthy" …`; registry cell writes `'healthy'` (single quotes) across a wrapped line → fold gap. Adoptable with a fidelity fix |
| S206 | Alibaba PAI (zh), 40 874 B | **present**: `…可通过模型列表接口<EAS_ENDPOINT>/v1/models获取。` with the endpoint as `<code>`; cell uses backticks → inline-code fold gap. Already adopted as `S206` (`corpus/SOURCES.md:209`, mined) |
| S210 | Unsloth (ja), 1 308 985 B | `Page Not Found` ×0; page live and carries the SGLang argv (`sglang.launch_server` ×7). Cell is a **search-snippet conflict note** (findings[580]). Refuse the cell |
| S211 | AaronYang238 ch.6, 494 370 B | `still-live` ×0 (`RadixCache` ×8); cell is lane prose (findings[582]); the id's real quote already matched under the `markdown` fold (findings[581]). Refuse the cell |
| S224 | vLLM v0.17.0 health page, 386 143 B | half located (`await engine_client(raw_request).check_health()`, `except EngineDeadError:` → 503); `render-only` ×0 — the second clause is the lane's own S004 summary. **Compound cell**: split and re-quote each half |
| S230 | sglang v0.5.22 `http_server.py`, 110 718 B | **present at message level**: lines 790-791 carry the sentence as two adjacent Python string literals; concatenation reproduces the quote exactly. Needs a two-literal anchor |

No slice row is fabricated source text. Id join caveat: 6 of the 7 slice ids are no
longer registry rows (they survive only in the lessons of rounds 35-37); `S206` is
the only one still in `corpus/SOURCES.md`.

## 4. Census gate on a scratch mirror + append block

Mirror = `git clone --shared` of the lane at the build tip
`97c864bead3ee4a2f629574e77263d33834ec98a` (full tree so `used-by` resolves as the
census resolves it), merge knowledge tree copied in, 119-row normalized block
inserted at the end of `## Registry`. Block built by
`w1/out/X1Assimilation/build-append-block.py` (142 in → 119 adopted, 10 `R1`
unparseable, 9 `R2` id collision, 4 `R3` url+scope; every decision in
`append-decisions.json`).

```
$ bash scripts/sources-census.sh validate "$S/lane"                       # lane tip, no block
exit=1     3 E11 · 1 W01 · 93 W04
           E11 S496/S497/S498 missing used-by corpus/lessons/round-50.md

$ bash scripts/sources-census.sh validate --file "$S/lane/corpus/SOURCES.md"   # + 119-row block
exit=1     3 E11 · 12 W01 · 123 W04        # identical E-set: the block adds 0 E-codes
$ bash scripts/sources-census.sh census --file "$S/lane/corpus/SOURCES.md"
file	rows	358   (239 registry + 119 appended; no duplicate id)
file	tier.A 313  tier.B 30  tier.C 15
file	status.mined 337  status.queued 10  status.rejected 11

$ bash scripts/sources-census.sh validate --file "$S/sim/corpus/SOURCES.md"    # + empty round-50.md placeholder (simulation, scratch clone only)
exit=0
file	ok	$S/sim/corpus/SOURCES.md   12 W01 · 123 W04
```

**Exit code 0 with the append block** once the known-missing `corpus/lessons/round-50.md`
exists; today's exit 1 is fully attributable to the three pre-existing E11s
(S496/S497/S498 — the documented integration item) and to nothing the block adds.
New warnings only: 11 new W01 (tier-C mined, `S407 S421 S423 S427 S429 S431 S438
S439 S441 S463 S469`) and 30 new W04 (same URL, different scope). Full record:
`w1/out/X1Assimilation/validate-report.md` with the three raw outputs.

---

## Defects found (not patched — the package, register and counters are read-only)

**D1 · `shokuknow/merge/kama/SOURCES.append.md` is not in census shape.**
90 of 142 rows split into >11 cells because the `recheck` cell carries
`90d — re-run \`curl … \| grep -c …\` (ran …)` prose with escaped pipes
(e.g. row `S330` at line 7; `S331` line 8; 52 rows are 11 cells, 81 are 12, 2 are
13, 1 is 14, 2 are 15, 4 are 17).
Show it:
```
$ awk -F'|' 'NF>=3 && $2 ~ /S[0-9]/ {print NF}' shokuknow/merge/kama/SOURCES.append.md | sort -n | uniq -c
     52 13        # 13 NF = 11 cells (valid)
     81 14
      2 15
      1 16
      2 17
      4 19
```
Ten of them cannot even be resolved by an anchored parser (8-13 cells before the
`status` cell): `S368` (line 45), `S406` (83), `S409` (86), `S410` (87), `S415`
(92), `S419` (96), `S454` (131), `S455` (132), `S459` (136), `S468` (145).
**Proposed fix (merge side, not applied):** regenerate the block from the current
registry — prune the 9 id-collision rows and the 24 same-document rows, rewrite
each `recheck` to a cadence (`90d`/ISO/symbolic) and move the stripped re-verify
prose into the round lesson's Gate block; hand-rewrite the 10 unresolvable rows'
`anchor`/`teaches` so no cell holds a literal or escaped `|`.

**D2 · Quote census fold gaps (campaign-side instrument).** `quote-lint-full-v5.json`
grades ABSENT for text that is present modulo one markup class:
`findings[575]` S202 (single vs double quotes + wrapped line), `findings[579]`
S206 (`<code>` vs backticks), S230 (adjacent Python string literals, one sentence
over two source lines), and `findings[574/580/582/585]` S200/S210/S211/S224 quote
**note prose**, not the row's anchor (all carry `binding: id`).
Show it: `python3 -c "import json;d=json.load(open('/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/quote-lint-full-v5.json'));print(d['findings'][574])"`.
**Proposed fix:** add three folds (straight-single↔straight-double quote marks,
inline-code delimiter normalization, adjacent string-literal concatenation) and
restrict quote extraction to the row's own quote spans so a `- Note:`/`- Conflict
note:`/`- Relation to …` prose line cannot be graded as a source quote.

**D3 · The register's `id` column no longer joins to the kama registry.**
6 of 7 slice ids (`S200 S202 S210 S211 S224 S230`) have 0 rows in
`corpus/SOURCES.md` and appear only in `corpus/lessons/round-{35,36,37}*.md`
(`grep -cE "^\s*\|\s*S200\s*\|" corpus/SOURCES.md` → 0). A consumer that resolves
ids against the registry will silently drop the slice; hand-checks must be
per-document (as done in §3). **Proposed fix:** the register (or its next
generation) records the cited URL as the join key alongside the id.

## Limits / risks

- My URL comparison normalizes only scheme/host-case/trailing slash/`#…`; two rows
  differing in path case or query would be counted as distinct.
- A green census says nothing about faithfulness — §3 is the only faithfulness
  evidence, and it is 7 rows, not the register's 194.
- Fetches are 2026-10-26 HTML; docs pages are JS-rendered in part, so "present"
  means present in the served HTML I stored, not necessarily in the rendered DOM.
- The census cannot see jj state; the lane clone was read at
  `97c864bead3ee4a2f629574e77263d33834ec98a` and the lane working tree for the
  registry id list (read-only `grep`).
- `git clone --shared` and the simulation placeholder exist only under
  `/fast/scratch/hyaku/kama-r50/X1Assimilation`, **removed** at the end
  (`rm -rf`, verified gone); no `/tmp` path is cited anywhere.
- No tool was installed or upgraded; no service started or stopped. `pgrep -af
  llama-server` shows two live servers owned by peer seats (`X8WitnessPort`,
  `X1Observe2`) — not mine, left untouched.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/reg-ids`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/staged-ids`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/collisions`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/quarantine-slice`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/collision-report.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/guard-proof.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/X1Assimilation/quarantine-verdicts.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/build-append-block.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/append-block.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/append-decisions.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/validate-report.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/validate-1-lane-tip.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/validate-2-mirror-plus-append-block.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/validate-3-sim-round50-lesson-present.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/guard-fixture-ordinary.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/guard-fixture-indented-duplicate.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/guard-collisions-maintained.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/guard-collisions-column-zero.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X1Assimilation/url-overlap.txt`
