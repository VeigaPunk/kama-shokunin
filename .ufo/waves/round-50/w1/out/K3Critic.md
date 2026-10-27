# K3Critic — round-50 attack: append-only-audit v5 fence parser

**Verdict: NO DEFECT found in `sections()`/`fence_open()`/`fence_close()` at
97c864be — the parser is CommonMark 0.31.2 §4.5-exact on every assigned vector
(16/16 discriminating end-to-end fixtures match hand expectations; 0 fenced-state
divergences vs `cmark` 0.31.2 over ~50k fuzzed lines). Five non-blocking
findings F1-F5 below, of which only F2 is a fixable counter gap: the
counter's fixture leg covers only a backtick fence, so a tilde-blind tool
passes 12/12 (proven by mutation) and escapes the lane leg too (zero tilde
fences in contract-covered files at tip).**

Claim: C2 (calibration, tool `tools/append-only-audit.py`, counter
`tools/round50-append-audit-v5-check.py`). Method: hand-derived expectations
first (they appear as literals in the `FIXTURES`/`PROBES` tables of
`out/K3Critic/driver-run.log` before any tool run), then `append-only-audit.py
--json` on 16 purpose-built git repos, plus unit probing of the extracted tool
against a `cmark --to xml --sourcepos` oracle (cmark 0.31.2 = the sourced spec
version), plus differential fuzzing, plus mutation testing of both the parser
and the counter.

Tool under test extracted by `git archive` from the shared clone at
`97c864bead3ee4a2f629574e77263d33834ec98a`; sha256 `a3170a6fcbded95...` ==
the live copy. Counter run on the same clone: `fixture=1 lane=1 scenarios=12/12
met=True` (receipt: `out/K3Critic/c2-receipt.txt`), matching the L1 dry run.

## Assigned vectors — results (all match expectation)

| # | Vector | Hand expectation (v5 contract + CommonMark) | Got (tool --json / sections) |
|---|--------|----------------------------------------------|------------------------------|
| 1 | tilde fence inside a `## ` section | `~~~` opens; `## ` inside invisible → graded | f1: graded=25 unrestored exit 1 ✓; tilde-fence-with-backtick-info also opens (f2 ✓) |
| 2 | 4-space-indented `## ` line | NOT a heading (all three readings: contract literal-`## `, CommonMark indented-code, tool) → graded | f5: graded=25 unrestored ✓. NOTE: the seat brief said "must still count as a heading"; that reading disagrees with the contract, CommonMark §4.1 and the tool — see F3 |
| 3 | ```` ```` ```` at 3 spaces, closer ` ````` ` (5 ticks) | closes (≥n, same char) → fence holds → graded | f6 graded=25 ✓; under-close ` ``` ` (3 ticks) does NOT close → f8 graded=25 ✓; 4-space-indented opener is not a fence → f7 ungraded=25 exit 0 ✓ |
| 4 | backtick in info string | ` ```x`y ` is not a fence → `## Axes` visible → ungraded | f9 ungraded=25 exit 0 ✓ |
| 5 | unclosed fence to EOF | all later `## ` invisible; `## Axes` inside → graded | f10 graded=25 ✓; and the launder-direction case f11 ungraded=25 — by contract design, see F2 |
| 6 | ` ``` ` + trailing spaces | still a fence (info = blanks) → graded | f12 graded=25 ✓ (trailing-tab variant also fence, probe v6b) |
| 7 | CRLF fence lines | CR stripped; open/close/heading all fire | f13 graded=25, f14 graded=25 (close ` ```  \r` OK) ✓ |
| 8 | `## ` line that is a close candidate | `## ` inside a fence never closes it; `## ````/`## ~~~` outside are headings | f15 graded=25 ✓ (fake `## Axes` inside a live fence does not close it; real ` ``` ` does); f16 heading right after close → ungraded=25 ✓ |

Full per-line evidence: `out/K3Critic/results.json` + `driver-run.log`. Unit
probes (30 docs): tool == cmark on all fence-sensitive lines; the only diffs are
heading-semantics (F3) and CR line-ending numbering (F4 note).

## Findings

### F1 — the counter's "independent" v5 reference is a copy of the tool's parser (duplicate authority; informational)

`round50-append-audit-v5-check.py` lines 305–351 (`fence_open`/`fence_close`/
`sections`/`key`/`split_lines`) are the tool's lines 282–353 modulo cosmetics
(variable names `t`↔`title`, `FENCE_OPEN.match` ↔ `re.match`). Differential
fuzzing: **0 mismatches** between the two over 60k random lines for
`fence_open`/`fence_close`/`key` and 8k random docs for `sections`.

Consequence: the lane leg's `tool.ungraded <= reference.ungraded` can only
catch *over*-ungrading on today's lane blobs; any parser bug that
*under*-ungrades (hides a heading the reference also can't see, i.e. any
shared bug) is invisible to that leg because the oracle has the bug too.
Load-bearing for met is therefore the fixture leg alone. This is the V2Ctr
class of limit already named in the counter docstring ("this counter's own
binder ... still true here: limit") — confirming, not re-reporting; the new
fact is that the parser half is an exact behavioral copy, not just the binder.

### F2 — counter fixture coverage: a tilde-blind parser passes 12/12 (gap, fixable)

The counter's sole fence scenario uses a backtick fence
(`round50-append-audit-v5-check.py:283-286`). Mutation test: a tool whose
`fence_open` regex drops `~{3,}` passes the counter's fixture leg
**12/12** (`ctr.scenarios("tree-mut", ...) → [True]*12`, evidence in
`results.json` run log). On the lane leg the mutant also escapes: contract-
covered files at tip contain **zero** tilde fences (`git grep -cE '^\s*~{3,}'
97c864be -- <all contract paths>` → 0; 51 tilde-fence files exist only under
`.ufo/`). Net: a spec-violating tool (tilde fences treated as text → fenced
`## ` headings mis-parsed) would be measured `fixture=1 lane=1 met=True`.
My f1/f2 fixtures do catch this mutant (ungraded instead of graded).
Smallest safe correction: add one tilde-fence fixture mirroring the `fence`
scenario — my f1 recipe is drop-in (change ` ```text ` → `~~~text`,
` ``` ` → `~~~`).

### F3 — heading rule contract ambiguity: `## ` is literal column-0, not CommonMark ATX (ambiguity; lane-safe today)

The contract says "`## ` line"; the tool requires `b.startswith(b"## ")`
(`append-only-audit.py:318`). CommonMark ATX headings allow 1–3 leading
spaces; `##`, `##\t` are empty headings; setext `---`/`===` also makes
headings. Divergences proven vs cmark (probes v2a, v9b, v9f; ~420 heading-
class diffs in fuzz, none fence-related): a 1–3-space-indented `## Round 1`
is a heading per CommonMark but invisible to the tool, so lines under it
keep the previous title (f3: tool reports ungraded=25 where an ATX reading
would grade). Both directions of abuse exist — an indented *exempt* title
typed `   ## Axes` is not exempt (`startswith` in `parse_region:177-179`
requires `## ` exactly), while an indented *non-exempt* heading inside an
exempt section fails to shield (f3). Lane today: `git grep -nE '^ {1,9}## '`
over all contract-covered paths at tip → **zero hits**, so no live
miscalibration. The seat item's own expectation (vector 2 "must still count
as a heading") is a third reading neither the contract nor CommonMark nor
the tool implements — flagging the brief's wording as the ambiguity's
source. Smallest correction: document in the tool/counter docstring that
"`## ` line" means bytes starting `## ` at column 0 (it already does in
practice; say it) or switch to the ATX rule and re-derive contract titles.

### F4 — unclosed fence inside an exempt section silently retitles the tail (contract exposure, spec-correct)

Per §4.5 an unclosed fence runs to EOF; f11 demonstrates the consequence: a
stray ` ``` ` under `## Axes` makes every later `## ` heading invisible, so
text born under `## Round 1` is attributed to `## Axes` at both parent-section
and origin checks → deleted lines ungraded by design, exit 0. The tool does
exactly what the contract specifies; this is the price of F4-compliance (the
fence-blind alternative was worse, per round-49 K2Origin). Worth one clause
in the lesson: exempt sections now also absorb "everything below an unclosed
fence". No fix proposed — contract tradeoff, judge-level accept.

### F5 — LF-only line model vs CommonMark (consistent-with-git; note only)

`split_lines` splits on LF only; a mid-line `\r` keeps `## X` invisible
(probe v7c) and `rstrip(b"\r")` strips *all* trailing CRs where `key()`
strips one (contract-matching asymmetry). Immaterial: `git diff`/`numstat`
also treat `\r` as content, so the tool's line model equals the deletion
oracle's. Note only.

## Evidence inventory

- `out/K3Critic/results.json` — all probe/fixture records with tool and cmark outputs.
- `out/K3Critic/driver-run.log` — driver stdout: expectations printed with results, PASS/FAIL per fixture.
- `out/K3Critic/c2-receipt.txt` — counter run on my clone at 97c864be: `fixture=1 lane=1 scenarios=12/12 met=True` (7 s).
- Negative controls: v4-style fence-blind tool (unrelated to measurement) reports ungraded=25 on f1/f15/f16 → fixtures discriminate; tilde-blind mutant passes counter scenarios 12/12 → F2.
- `--selftest` at tip: `AOA_SELFTEST pass=36 fail=0`.
- Lane greps: 180 fence-like lines across contract files at tip (SCORECARD.md:4 incl. ` ```diff ` blocks at 2487/2615, plus lessons); 0 indented `## `; 0 tilde fences.

Report: `.ufo/waves/round-50/w1/out/K3Critic.md`
