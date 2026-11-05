# MT01SelectorBattery — C1 mutation battery for the rendered-cell selector (round 87 w1)

## Scope

- Frozen basis: freeze commit `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`; claims in
  `plans/round-87-claims.md` (C1 successor rules R1–R4, probes P-A/P-B/P-C, kill rules).
- Built `battery.py` (usage `battery.py <selector.py>`): nine mutants M1–M9 plus control C0 (sensitivity)
  and control CG (green, clean tree). Fixture API as in `controls/c1-probes.py` (`fixture`, `grade`, `A`, `B`,
  `GOOD_*`, `GOOD_ROW`, `CouldNotEvaluate`, `DictTree.ancestors`, `rev_files`). In-memory trees only: no disk
  writes, no git, no TMPDIR needed.
- Ran it against `tools/round86-rendered-cells.py` at `94e8fe7b` (copied via `git show`, read-only).
- Self-check: two scratch reference successors (not delivered) to prove the battery can kill what a correct
  selector must kill. Not a deliverable selector; not the L1 integration candidate.
- Scratch dir removed after copying receipts. No tool installed or upgraded (`python3` stdlib only).

## Commands and outputs

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659:tools/round86-rendered-cells.py > round86-rendered-cells.py`
   exit 0; sha256 `f9d36b5be0683fdc486da343f6c3aa2e140f250efc94c377ddda1a36ba6e633b`, 533 lines.
2. `python3 battery.py ./round86-rendered-cells.py` (full output, exit 0). Receipt: `battery-run-round86.out`.
```
SELECTOR_CONTROL C0 expect=red got=red pass (killed)
SELECTOR_DETAIL C0 mismatches=3 gate: declared round=84 newest terminal receipt round=85 (.ufo/waves/round-85/measured/after/gate.out); closure: row names round-84 newest committed closure is round-85 (corpus/lessons/round-85-verifier-spotcheck.md); disposition: row does not name `round85 rejected-honest-stop`
SELECTOR_CONTROL CG expect=escape got=escape pass (escaped)
SELECTOR_DETAIL CG mismatches=0
SELECTOR_MUTANT M1 expect=red got=escape escaped
SELECTOR_DETAIL M1 mismatches=0
SELECTOR_MUTANT M2 expect=red got=escape escaped
SELECTOR_DETAIL M2 mismatches=0
SELECTOR_MUTANT M3 expect=red got=red killed
SELECTOR_DETAIL M3 mismatches=3 gate: declared round=84 newest terminal receipt round=85 (...); closure: row names round-84 ...; disposition: row does not name `round85 rejected-honest-stop`
SELECTOR_MUTANT M4 expect=red got=red killed
SELECTOR_DETAIL M4 mismatches=3 (same three findings as M3)
SELECTOR_MUTANT M5 expect=red got=escape escaped
SELECTOR_DETAIL M5 mismatches=0
SELECTOR_MUTANT M6 expect=red got=escape escaped
SELECTOR_DETAIL M6 mismatches=0
SELECTOR_MUTANT M7 expect=red got=escape escaped
SELECTOR_DETAIL M7 mismatches=0
SELECTOR_MUTANT M8 expect=red got=red killed
SELECTOR_DETAIL M8 mismatches=3 (same three findings as M3)
SELECTOR_MUTANT M9 expect=red got=cne escaped
SELECTOR_DETAIL M9 could-not-evaluate: no rendered top-level Current authority cell
SELECTOR_VARIANT M7L informational got=escape (not counted)
SELECTOR_DETAIL M7L mismatches=0
SELECTOR_MUTANTS mutants=9 killed=3 escaped=6
```
   (Full DETAIL text for C0/M3/M4/M8 is in the receipt file; abbreviated here only where marked.)
3. `python3 round86-rendered-cells.py --selftest` exit 0, `RENDERED_CELLS_SELFTEST pass=17 fail=0` (`round86-selftest.out`).
4. `python3 controls/c1-probes.py round86-rendered-cells.py` exit 1: `escapes=3 control=red` (matches the frozen
   before-receipt; P-A, P-B, P-C all escape).
5. Scratch references (`selfcheck-reference-variants.py`, built from the round-86 copy):
   - `ref-r1r2` = R1 (closer without container prefix, ≤3 spaces, only space/tab after) + R2 (disposition from the
     single `verdict \`<token>\`` line; missing/ambiguous → unknown).
   - `ref-r1r2gate` = ref-r1r2 + every revision named in the gate cell must be an ancestor carrying the receipt
     with the token (new rule, see Findings F3).
   - Both use the fixture default closure bodies rewritten to `verdict \`rejected-honest-stop\`` (F4).
   - Battery on `ref-r1r2`: C0 red, CG escape, `SELECTOR_MUTANTS mutants=9 killed=7 escaped=2` (M7 escape, M9 cne).
   - Battery on `ref-r1r2gate`: C0 red, CG escape, `SELECTOR_MUTANTS mutants=9 killed=8 escaped=1` (M9 cne).
   - `c1-probes.py` on `ref-r1r2`: `C1_PROBES probes=3 escapes=1 control=red`, exit 1 (P-C escapes).
   - `c1-probes.py` on `ref-r1r2gate`: `C1_PROBES probes=3 escapes=0 control=red`, exit 0.
   Receipts: `selfcheck-reference-variants.out`, `c1-probes-vs-references.out`.
6. Battery sha256 after copy: `144f24d9b6d80d1b8025b0e2df804a59b3b965cecb4b903b0208615550d4c689`
   (`out/MT01SelectorBattery/battery.py`); rerun from the out-dir copy reproduces the round-86 output, exit 0.

## Findings

F1 — Battery sees the frozen probe escapes on round 86. M1 (list-marker closer, same construct as P-A), M5
(disposition word before verdict, P-B shape) and M7 (extra revision without receipt, P-C code) escape; these are
the three expected classes. M3 (four-space closer), M4 (`` ```x `` closer) and M8 (tab closer) are killed.
M9 is cne. Evidence: command 2 above; `c1-probes-before` agrees (command 4).

F2 — P-C prose and code disagree. `controls/c1-probes.py` builds P-C with `rev_files={A: {receipt: token}, B: {}}`:
the second revision B does NOT carry the receipt (name "without-receipt"). The probe docstring and
`plans/round-87-claims.md` say B "carries the same receipt token". The battery's M7 follows the executable
code (B lacks the receipt). The literal prose variant is M7L (informational, not counted): B carries the token.
M7L escapes on round 86 and on both references, and that is correct: a second revision that truly carries the
receipt is a coupled claim, not a false green. So the "second revision carrying the same token" class cannot be
a red-expected mutant; it is not expressible as a kill test. The L1 should decide which P-C the frozen artifacts
mean; the battery kills the code version.

F3 — Frozen R1–R4 do NOT close P-C. The gate fact checks only that SOME named revision is an ancestor carrying the
token (`round86-rendered-cells.py:309-317`). A successor implementing R1 and R2 exactly (`ref-r1r2`) leaves P-C
escaping (`escapes=1`), which trips the C1 kill rule. Closing it needs a rule outside R1–R4: every revision the
gate cell names must carry the receipt with the token (`ref-r1r2gate`, P-C red, escapes=0). R4 says "population
unchanged; any other change is a new claim", so this is a scope question for the L1, not something the battery can
decide.

F4 — R2 literal breaks the round-86 fixture defaults. Fixture default closure bodies are
`Verdict: rejected-honest-stop.` (no backticked token; `round86-rendered-cells.py:416,418`). A correct R2 selector
reads that as "carries no disposition word" and fails its own green arm (CG red) before any mutant runs. The
battery's CG control caught this on the first reference run. Any successor implementing R2 must change these
fixture defaults; that is a change to fixture meanings (R3 keeps names only).

F5 — Frozen P-B is red under R2 for the wrong reason. `c1-probes.py` P-B body is
`Verdict: rejected-honest-stop. Earlier round 83 was rejected-harmed.` (no backticked verdict). Under R2 it is red
because the verdict token is missing (`closure ... carries no disposition word`), not because a fixed-order word
appears before the verdict. M5 uses `verdict \`rejected-honest-stop\`` after the harmed word; that is the
discriminating form. Recommend the L1 treat M5, not P-B, as the disposition-order kill evidence.

F6 — M9 is fail-closed, not a false green. An unclosed `- ```markdown` opener swallows the live cell, the selector
returns could-not-evaluate (exit 2) on every variant. The battery records it as `got=cne`, status `escaped` (not
killed), because the spec counts only red as killed. It is not a green; the expect=red label does not fit it.

F7 — Construction choices (for the L1 to check against intent):
- "Stale-live" for M5–M7 means the calibration row / closure / revision is wrong while the authority cell is
  correct (`stale_live=False`). A stale authority would be red regardless of the mutant, so it could not show escape.
- M8 is the outer fence's own closer `` ```<TAB> ``. A tab-closer followed by correct tokens would make those tokens
  genuinely live (correct rendering, not a mutant), so the correct tokens sit inside the fence.
- M1 reproduces P-A byte-for-byte; M7 reproduces P-C byte-for-byte (code version).
- The battery reads `DictTree.ancestors` and `rev_files` as `c1-probes.py` does; a successor that drops those
  attributes breaks the battery and the frozen probe alike.

F8 — No tool installed or upgraded; no lane file, git state or fleet file touched; nothing written outside the
out dir and this report.

## Deliverables

Out dir `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-87/w1/out/MT01SelectorBattery/`:
- `battery.py` — the battery (usage `battery.py <selector.py>`, exit 0 always).
- `battery-run-round86.out` — full run on round 86 at 94e8fe7b (command 2).
- `battery-run-round86-first.out` — first run, identical content (kept as a receipt).
- `round86-selftest.out` — round-86 `--selftest` (command 3).
- `c1-probes-vs-references.out` — frozen probes against round 86 and both scratch references.
- `selfcheck-reference-variants.out` / `selfcheck-reference-variants.py` — battery on the two scratch references
  and the generator for them (scratch self-check only, not a selector deliverable).

## Mutant classes not expressed as red-expected

- M7L (a second revision that truly carries the token): correct behavior is escape. Informational only.
- M9 expect=red: correct behavior is cne (fail-closed). Counted as escaped under the spec's two-value status.

VERDICT: battery delivered (9 mutants + C0/CG); on round 86 it reports killed=3 escaped=6 with C0 red and CG
escape, matching the frozen P-A/P-B/P-C escapes; R1+R2 alone leave P-C (M7) escaping, so C1 needs a
gate all-revisions rule (F3) to close.
