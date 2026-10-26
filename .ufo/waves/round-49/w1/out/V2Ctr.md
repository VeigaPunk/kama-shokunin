# V2Ctr — code review of frozen C2 counter (round49-append-audit-v4-check.py)

Verdict: **C2 is sound for what it measures at the measured commit — `fixture=1 lane=1 scenarios=8/8 met=True` at lane tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 (exit 0), counter sha256 26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945 matches preregistration — but the lane leg is not an independent oracle: the binder is a verbatim copy of the tool's, the ungraded bound omits the v3 eligibility predicate and has no term for `only=`-region files, and the per-event check is skipped whenever the tool reports `ungraded=0`. Demonstrated: a patched tool that drops eligibility still gets `met=True`; a wrapper that zeroes `ungraded` in lane events (while passing real tool output on fixtures) still gets `met=True`; a tool reporting no events fails (good).**

Counter run at tip (evidence):
```
$ python3 tools/round49-append-audit-v4-check.py --repo <clone> --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S --out $S/receipt-tip.txt; echo EXIT=$?
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
fixture=1 lane=1 scenarios=8/8 met=True
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
EXIT=0
```
Target string in preregistration (`fixture=1 lane=1 scenarios=8/8 met=True`) matches.

---

## 1. Binder independence (Q1): it is NOT independent — it is a byte-equivalent copy

The counter's `binds`/`says`/`token` (round49-append-audit-v4-check.py:107-130, constants 90-92) and the tool's `binds`/`row_token` (append-only-audit.py:202-233, constants 141, 212-213) are the same code:

| piece | counter | tool | identical? |
|---|---|---|---|
| fixed negations | `NEG3` (line 90) | `NEGATIONS` (line 141) | tuple-equal |
| 3-word window regex | `NEGW` (91-92) | `NEG_WINDOW` (212-213) | `pattern` string-equal |
| token extraction | `token()` (107-112) | `row_token()` (202-209) | line-equal |
| whole-word match | `(?<![a-z0-9_])` + `re.escape` + lookahead (130) | same (233) | string-equal |
| path match | `fnmatch.fnmatchcase(decl_path, pattern)` (128) | same (231) | same |
| control flow | `says` gate then token/path | same inline | logically equal |

Probe battery (29 texts × patterns × decl paths incl. negation windows, substring traps, wildcards, None; plus 12 token probes): **0 divergences**; constants/regex source equal.
```
NEG3 == tool.NEGATIONS: True
NEGW.pattern == NEG_WINDOW.pattern: True
binds divergence count: 0 / 29
```

Where they could diverge: only through future maintenance drift (someone edits one regex/tuple/fnmatch call without the other). There is no independent re-implementation today; a shared rule bug would appear in both and be invisible to the lane-leg binder. The genuine independence in the counter is the **fixture leg**, which drives the archived tool end-to-end and compares exit code/events/bad_declarations against hand-written expectations — that is what actually validates the rule. The lane-leg binder re-checks the contract against the same copied rule (a consistency pass, not an oracle). Finding: **the phrase "its own v4 binder" overstates independence; treat the lane-leg binder as a contract sanity check only.** No action needed if the two files are kept in lockstep; note it in maintenance.

## 2. The eight scenario expectations are written by construction (Q2) — re-derived by hand, all hold

Hand re-derivation (contract row used for the three grading scenarios: `SCORE.md A-corr NOTES.md:1 exempt=## Axes@NOTES.md:2`, NOTES.md:1 binds ("SCORE.md is append-only"), NOTES.md:2 names "Axes" + "re-derived" ✓):

| # | scenario | commits | counted deleted lines (d) | parent section | eligibility (max over window ≥ parent count) | origin | tool expectation | verified |
|---|---|---|---|---|---|---|---|---|
| 1 | launder | c1: Axes+head5+Round1+dated25; c2: dated moved into Axes; c3: Axes regrown +30, dated gone | 25 (c2→c3) | `## Axes` | Axes 31/36 ≥ 31 ✓ | {`## Round 1`} (born c1) ∩ exempt = ∅ | graded 25, ungraded 0, unrestored, exit 1 | run ok |
| 2 | native-head | c1 Axes+old25; c2 Axes+new25 | 25 | `## Axes` | 27/27 ≥ 27 ✓ | {`## Axes`} ∩ exempt | ungraded 25, exit 0 | run ok |
| 3 | dated-loss | c1 Round1+dated30; c2 keeps d25..d29 | 25 | `## Round 1` | n/a (not exempt) | n/a | graded 25, unrestored, exit 1 | run ok |
| 4 | substring | NOTES.md:1 "the catalog is append-only" | — | — | — | — | token "LOG" not whole-word in "catalog" → unbound, bad=1, exit 1 | run ok |
| 5 | word-token | "LOG.md is append-only" | — | — | — | — | bound, exit 0 | run ok |
| 6 | negated | "SCORE.md is not strictly append-only" | — | — | — | — | NEGW hits "not strictly append-only" (1 word) → unbound, exit 1 | run ok |
| 7 | wildcard-self | notes/a.md:1 "this file is append-only" | — | — | — | — | wildcard ⇒ token "notes" absent → unbound, exit 1 | run ok |
| 8 | wildcard-named | README.md:1 "files under notes/ are append-only" | — | — | — | — | token "notes" whole-word present → bound, exit 0 | run ok |

Independent confirmation: the base control `base.c2.out` shows the same 8 expectations failing on the v3 tool exactly where v4 differs (launder, substring, negated, wildcard-self); the junk-c2-word-token control shows launder still failing when only word/negation is fixed but origin is not.

Docstring nit (not a behavior bug): the launder docstring says "the move is a held event" (lines 36-38). Observed `git diff c1 c2` is a pure reorder that deletes only the `## Round 1` heading line (numstat `2 1`), so **no event fires at c2** (deleted=1 < threshold 20); the discrimination comes entirely from the origin rule at c3. Suggest rewording to "the dated text is carried under the exempt `## Axes` without being deleted (1 heading line deletes, below threshold); it is deleted there later".

## 3. Vacuous satisfaction (Q3): partial window, demonstrated both ways

Lane leg requirements (round49-append-audit-v4-check.py:283-360): tool exit 0, `bad_declarations==0`, ≥5 events, counter binder binds every contract row, and per event with `ungraded>0`: `ungraded <= native`. Three controlled probes (each: synthetic tip in a scratch `--shared` clone of the lane, frozen counter run):

- **Tool reporting no events** → `fixture=0 lane=0 scenarios=2/8 met=False` (receipt-no-events-tool-1264f9cf.txt). The ≥5-events guard works; a no-events tool cannot pass. Good.
- **Wrapper that zeroes `ungraded` in lane events only** (passes real tool output through on fixture repos) → `fixture=1 lane=1 scenarios=8/8 met=True` (receipt-liar-zero-ungraded-3b95cd26.txt). The lane leg trusted the tool-reported `ungraded=0`; the per-event check at lines 343-344 (`if not e.get("ungraded"): continue`) is inert, and the verdict "ungrades no deleted line whose origin is not an exempt section" is vacuously true of a report that contains no ungraded lines. The only thing standing between this and a false `met=True` is the fixture leg (which forces the tool to *demonstrate* ungrading in the synthetic native-head scenario — it cannot verify the tool's honesty on lane-shaped data). Finding: **the lane leg is a monotone upper bound on tool-reported ungraded counts, not an independent measurement; a selective misreport on lane history passes.**
- **Tool with the v3 eligibility gate removed** (`if s in eligible and ...` → `if s in titles and ...`, append-only-audit.py:475) → `fixture=1 lane=1 scenarios=8/8 met=True` (receipt-eligibility-blind-tool-98f4cc5.txt; patch-eligibility-blind.txt). The tool now leaves 6 lines ungraded that the correct v4 tool grades (dd9f5dc6c0e6 ungraded 17 → 23), i.e. it hides a real loss in a gutted exempt section, and the counter still certifies `met=True` because `native` (line 353-354) counts exempt-title parent sections **without the eligibility predicate** (tool: lines 465-467, 475). Eligibility is also not exercised by any of the 8 fixtures (every fixture exempt section is eligible). Finding: **the v3 "a gutted section that never comes back is graded" rule is checked by neither leg of C2.**

So the answer to Q3: yes, the lane leg can be met vacuously past the exit-0/≥5-events/binder gates — for any deviation that keeps reported `ungraded` at or under the counter's own count. The fixture leg is the effective enforcement, and it is scenario-shaped, not lane-shaped.

## 4. `natively exempt` bounds the right quantity? (Q4): right occurrence-count, wrong predicate set

- Multiset vs count: aligned. Tool `ungraded = |D| - |G|` (D, G text multisets; append-only-audit.py:457, 478, 491) counts deleted occurrences; counter `native` counts occurrences at their parent positions (`deleted_with_pos`, line 353-354). Both are occurrence counts, and the tool's per-occurrence parent-section gate makes the two denominators coincide.
- Positions: both use parent line numbers (`psec[pos-1]` vs tool `psec[pos-1]`, same `sections()`/diff parsing). Aligned.
- Predicate mismatch (demonstrated in §3): `native` requires parent section ∈ exempt titles ∧ origin ∩ exempt, but the tool requires parent section ∈ **eligible** (⊆ exempt) ∧ origin ∩ exempt. So `native ⊇ tool.ungraded` always for a correct tool — the bound is satisfaction-safe in the over-ungrading direction but blind to eligibility removal, and it never checks the under-ungrading direction (only fixtures do).
- `only=`-region files have no term at all: `titles` only collects `exempt=` rows (lines 307-311; regex matches `exempt=` only). An event on corpus/knowledge/consumer-registry.md (contract row `only=## Errata@...`) with deletions outside the declared prefix is *supposed* to report `ungraded>0` (those lines are deliberately not graded), and the counter hard-fails it: `if not ex or par is None: ok=False` (lines 346-349). Demonstrated with a synthetic tip deleting 25 lines inside the Consumer-table section of consumer-registry.md: the tool exits 0 with 6 events, `bad_declarations=0`, and the counter fails `lane=0` solely on "ungrades lines in a file with no exempt row" (receipt-only-file-event-2a8017be.txt; patch-only-file-event.txt). Latent false-failure: any future ≥threshold deletion in the non-declared part of an only-file flips C2 to met=False on a fully correct tool. Currently unexercised (all five lane events are SCORECARD.md). Suggested fix (proposed text in out dir if wanted): for only-files, the counter should bound ungraded by deletions whose parent section **fails** the `only=` prefix (or skip files with only-regions, since C2's claim concerns exempt sections) rather than failing when `ex` is empty.

## 5. Findings summary (by severity)

1. **Med-high — lane bound is monotone, not equivalent; a zero-ungraded misreport passes `met=True`** (round49-append-audit-v4-check.py:343-344, 355-359). Demonstrated (liar probe). Residual risk: the fixture leg is the only check of grading semantics; it is scenario-shaped.
2. **Med — eligibility (v3 anti-gutting) is unverified by either leg; a tool that drops it passes `met=True`** (counter 353-354 vs tool 465-467,475; fixtures 193-229). Demonstrated (eligibility-blind probe).
3. **Med-low — binder is a copy, not an independent re-implementation; shared-rule bugs invisible to the lane leg** (counter 107-130 vs tool 202-233). 0/29 probe divergences.
4. **Low-latent — only-file events false-fail** (counter 307-311, 346-349). Demonstrated on the real lanes file with a synthetic event.
5. **Nit — launder docstring "the move is a held event" inaccurate** (counter 36-38; actual c1→c2 diff deletes 1 heading line, no event).

Verification gaps: no run of the counter against a *wrong-origin* tool with identical totals (hard to construct), and the counter's origin "first appearance" is only spot-checked via the launder fixture — the lane-native `origins()` path (317-335) is exercised by the lane runs but not independently cross-checked against a second implementation.

## Command log (all exit codes above)
```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71... --scratch $S --out $S/receipt-tip.txt   # exit 0, met=True
# synthetic tips (branches on the scratch clone):
#   98f4cc5 (eligibility-blind tool)  -> exit 0, met=True
#   1264f9cf (no-events stub)         -> exit 1, met=False
#   3b95cd26 (liar wrapper)           -> exit 0, met=True
#   2a8017be (only-file event)        -> exit 1, met=False
# binder equivalence battery: 29 binds probes + 12 token probes, 0 divergences
# launder c1->c2 diff: numstat '2 1' (1 deleted heading line)
```
Receipts and patches copied to the out directory (below); scratch removed after copy.
## Proposed fixes (per finding)
1. (liar/zero-ungraded) In the per-event loop, when the counter's own `native` is 0 but the tool reports an event with `deleted>0`, record a detail line; more strongly, require `ungraded == 0` to be justified by the counter's own `deleted_with_pos`/`origins` scan (i.e. flip the check into an equality on the counter's own count when native==0: `e["ungraded"] == 0`). This closes the skip at round49-append-audit-v4-check.py:343-344.
2. (eligibility) Add the eligibility predicate to `native`: compute `eligible` per event the way the tool does (max over window of section count >= parent count) and count only parent sections in `eligible`. This makes the bound tight and detects the eligibility-blind tool.
3. (binder copy) Keep the duplicate binder but add a short comment at round49-append-audit-v4-check.py:106 stating it must mirror append-only-audit.py:202-233 exactly, and pin a shared unit test that runs both on the 29-probe battery (it currently lives only in this review).
4. (only-file) For events on files matched by `only=` rows, bound `ungraded` by the counter's own count of deleted lines whose parent section fails the prefix instead of failing on empty `ex` (round49-append-audit-v4-check.py:346-349).
