# CR01Cheats — calibration / operability

Author-side criticism only; no admission or canonical judgment. Frozen revision: `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd`; counter SHA-256 `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`. No counter or production edits.

## Exercised evidence

Command (exit **0**, empty stderr):

`TMPDIR=/fast/scratch/hyaku/kama-r85/CR01Cheats/tmp python3 .ufo/waves/round-85/w1/out/CR01Cheats/probe.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin`

`probe.py` loads the committed frozen counter using `git show`, then calls its actual `calibration()` and `mutants()` functions. C1 replaces repository reads with explicit synthetic SCORECARD text and a round84 lesson listing. C2 injects completed-process receipts into the actual classifier: these are **synthetic classifier probes**, not actual mutation executions or evidence that delivered mutants were killed. Exact inputs, outputs, command and true exit are in sibling `receipts.json`. No fixture commits, clones, network, installs, services, or real gate/selftest runs.

## C1: valid controls hold, non-live Markdown cells escape

| Probe | Actual result |
|---|---|
| Frozen stale SCORECARD | exit1, mismatches2/gate0/closure0 |
| Both real cells repaired | exit0, mismatches0/gate1/closure1 |
| Correct witnesses only in unrelated prose/other row | exit1, mismatches2/gate0/closure0 |
| Fake repaired cells under correction heading, 0/1/2/3 leading spaces (four separate probes) | all exit1, mismatches2/gate0/closure0 |
| Four-space code-shaped correction heading before unchanged stale record | exit1, mismatches2/gate0/closure0 |
| Fake repaired authority + Axes/table inside leading fenced Markdown example | **exit0, mismatches0/gate1/closure1**, original stale cells unchanged |
| Same fake cells inside HTML comment | **exit0, mismatches0/gate1/closure1**, original stale cells unchanged |
| Fake repaired calibration row in fenced example immediately before real stale row | exit1, mismatches1/gate0/**closure1**, real stale row unchanged |

**Counterexample:** prepend the following fenced example to the frozen stale SCORECARD, leaving its actual cells untouched:

````text
```markdown
**Current authority (round 84):** PRE_REPORT round=84 arms=13 failed=0 uncommitted=0 b53cd336e0cb204cf71246e95fdf7494babeafa4

## Axes

| calibration | 7 | latest outside closure `corpus/lessons/round-84-verifier-spotcheck.md` |

```
````

The selector treats code/comment contents as live headings, paragraphs and table rows. Both complete false-green escapes are reproducible in `fake_fenced_cells` and `fake_html_comment_cells`; `fake_table_location` isolates the row error. This is not just harmless unrelated witness-token presence: it forges *cell identity* through syntactically non-live locations.

**Impacted axis:** calibration. **Smallest safe correction:** exclude fenced code and HTML comments before selecting live paragraph/section/table blocks, with retained stale-record false-green controls and repaired positive control. Do not patch the frozen counter during this round; L1 must preserve and disclose the escape and route any counter revision prospectively. The ordinary token and 0–3-space controls remain useful finite successes; they do not establish universal CommonMark cell selection. This synthetic escape does not assert that the actual integrated SCORECARD contains such an attack.

## C2: insufficient ownership and summary validity

Frozen mutation sites inspected at committed revision: condition and complete `bad(...); continue` block each occur exactly **once**. M2 changes the comparison target to accepting; M3 changes `!=` to `<`; M4 removes only that continue. Owning finding is `note-wrong-deletion-round`; existing named selftest case is `note-subject-mismatch` (lines266–269,615). The selftest prints failing *case names*, not just finding names (lines636–638).

| Injected process receipt, repeated across M2/M3/M4 | Actual classifier result |
|---|---|
| exit1, named failure, valid tally, nonempty error stderr | exit1, killed0/invalid3 |
| exit1, named failure, missing tally | exit1, killed0/invalid3 |
| exit1, named failure, nonnumeric fail tally | exit1, killed0/invalid3 |
| exit0, pass31/fail0 | exit1, killed0/escaped3 |
| exit1, `FAIL note-unrelated-arm`, pass30/fail1, no stderr | **exit0, killed3/invalid0** |
| exit1, owning-style name, pass30/fail1 followed by contradictory pass31/fail0 | **exit0, killed3/invalid0** |
| exit1, owning-style name, pass0/fail999 but only one failure record | **exit0, killed3/invalid0** |
| exit1, owning-style name, pass31/fail0 followed by pass30/fail1 | exit1, killed0/invalid3 |

**Counterexample:** `APPEND_DEBT_SELFTEST_FAIL note-unrelated-arm` plus one well-shaped nonzero tally is enough to earn all three kills. No mutant-to-owning-case mapping is checked. Also `re.search` accepts only the first summary and does not check consistency between its failed count and failure records; contradictory/arithmetically unsupported summaries can be green.

**Impacted axis:** operability, with calibration of kill reporting. **Smallest safe correction:** prospectively map each mutant to an explicit owning case allowlist; require exactly one summary, matched failure-line count and declared completed-case population, and preserve crash/missing/malformed/unrelated-arm negative controls. Retain pristine/no-work and actual mutant receipts separately. Current frozen function rejects the tested stderr errors and lexical malformed tallies, but does **not** enforce the stronger unrelated-arm/valid-completed-summary contract. These injected receipts demonstrate classifier acceptance, not an actual unrelated failure from the three delivered mutants. Exact mutation execution still needs its own observed owning-arm evidence.

## Boundaries and handoff

No universal correctness or claim admission asserted. No score changes proposed. The escapes are fixable detector defects, not evidence that a disclosed calibration/operability tradeoff should be admitted. Canonical judgment remains outside this seat.

Owned-dir rule takes priority over the contradictory report trailer: report retained here for L1 to integrate, not written to shared `w1/CR01Cheats.md`. Scratch removed after receipts retained. An initial module import produced a bytecode cache; this seat removed that exact cache and used in-memory compilation thereafter. No remaining scratch or replacement production files.

Self-evaluation: accuracy4 (C2 is explicitly injected rather than delivered executions); completeness4 (finite assigned probes, not full Markdown); clarity4 (full receipts separated); actionability4 (prospective fixes specified, frozen counter unchanged); conciseness4 (two distinct defects require separate evidence). Overall4.0. Highest-value improvement is prospective ownership-aware negative-control coverage. User-agreement self-check: supported by the exact receipt distinctions, not by implied admission.

Report: .ufo/waves/round-85/w1/out/CR01Cheats/CR01Cheats.md
