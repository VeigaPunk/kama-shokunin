# EX03RecordDraft — author-side advisory

Axes: calibration + operability. No score changes, claim admission, promotion, production edits, sibling/index/jj changes, commits, installs, network requests, or tests.

## Deliverable

`record-draft.txt` contains exact single-line replacements for the first Current authority paragraph and calibration row in the first `## Axes` table. Gate revision, actual command, summary, exit and receipt occur together in the authority paragraph, not in a separate witness block. Adverse round83/round84 dispositions and author-assertion boundaries remain explicit.

The observed working-file authority and row already contain the requested round85 repair tokens; this draft does not claim to have introduced those working-tree changes. It additionally binds C2/C3 to their retained final receipt revision rather than repeating the observed head paragraph's `3e93febb...` attribution. Do not overwrite concurrent integration blindly.

## Exact retained evidence

- Full `plans/round-85-claims.md` read, including raw recovery of its truncated mutation paragraph. Frozen C1 population is exactly two committed cells, not whole-record correctness.
- `SCORECARD.md` first200 lines read; raw complete lines6 and18 retained through tool output. Both requested live cells currently contain round85 repair wording.
- `.ufo/waves/round-84/measured/after/gate-final-green.out`: header `# rev=b53cd336e0cb204cf71246e95fdf7494babeafa4`; command `python3 tools/pre-report-gate.py --repo . --round 84 --tip master`; summary `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`; recorded `EXIT=0`. Its newest-closure arm names round83 at that historical revision; do not relabel that arm as round84. The live row instead names the later outside closure.
- `.ufo/waves/round-84/measured/after/c2-final.out`: revision `65665250e58f5deec028ad53809296e08373818a`, command `python3 tools/round84-selfrecord-round83.py --repo .`, `SELFRECORD_R83 claims=8 mismatches=0 corrected=6 unbacked=0`, recorded `EXIT=0`.
- `.ufo/waves/round-84/measured/after/c3-final.out`: same full revision, command `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv`, `PIN_RECHECK rows=5 graded=5 holds=5 reworded=0 moved=0 drifted=0 ungraded=0 bad=0`, recorded `EXIT=0`.
- `corpus/lessons/round-84-verifier-spotcheck.md:32-42,63,86-92`: gate verified from committed evidence, not rerun; eight-fact calibration bound; round verdict rejected-honest-stop/admitted false; missed disclosure and source-origin/provenance limits remain open; `[~]` is not promotion review.
- Read-only command `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD master` exited0 and printed `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd` twice.
- Read-only command `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/count.py` exited0: `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`.

These receipt exits are retained historical results, not executions by this seat. File reads/searches are source inspection, not gate verification.

## Precise integration constraints

1. Frozen counter `count.py:10-33` reads committed `SCORECARD.md` at `--rev`; uncommitted replacements cannot establish C1. It removes correction-heading regions whose ATX headings have 0–3 leading spaces and titles matching `round-<digits> correction`, through an equal-or-shallower heading; excludes individual `LOG-CORRECTION` lines. It then takes the first column-zero `**Current authority...` physical line and the calibration row under the first column-zero `## Axes`. Keep each replacement on one physical line, outside correction blocks. Do not satisfy this via unrelated or historical witness tokens. Four-space code is not matched as an ATX heading by this counter.
2. Gate cell requires the full b53 revision and exact PRE_REPORT summary and must not contain `under terminal measurement`. The frozen counter does not itself require command/receipt tokens, but the assignment does; the replacement carries both. Closure cell requires exact `latest outside closure ` plus the backticked full corpus path naming the numerically newest committed spotcheck file, currently round84.
3. `round42-selfdesc-reconcile.py:116-128,265-318` recognizes only column-zero `## ` section delimiters; first exact `## Planned` section is live. The head ends before the first such delimiter. Its banner requires `operability + calibration` and `Latest measured round: N`, where N is the maximum column-zero `## Round <digits>` heading anywhere in the record. A correction subheading is not a new measured round. With maxN84 retain latest84 and `### Planned (round 85)`. If L1 appends `## Round 85`, change head latest to85 and first Planned to `### Planned (round 86)` in the same integration. The next nonblank line after that planned subheading must match a numbered `1.` item. Do not carry the old round5 continuation path or the phrase `freshness move` in the live Planned section.
4. Inherited `round41-scorecard-reconcile.py:114-133` requires a line exactly `## Axes`, column-zero pipe table rows, then stops at the first non-pipe after table entry. Preserve table header/separator and row order. Embedded literal pipes split evidence into extra cells; the proposed row contains none. Round42 takes axis evidence from cell3.
5. `round42-selfdesc-reconcile.py:325-340` compares the first exact Saturation section against the axis vector in table order: `operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7`; also requires `first-working rounds ` followed by sorted distinct fourth-column rounds from the highest-numbered canonical list. That list must match `canonical list as of round N**`; a plain heading alone is insufficient. Preserve the existing 49-name repertoire/mirror and retired count unless actual integration changes it. Assigned minimum calibration7 is below8, so require `nudge inactive` and forbid `nudge active`. A new measured round does not itself create a new capability or first-working round.
6. Closure reconciliation (`round42:170-186`) requires exactly one latest-outside-closure pointer in calibration evidence; any `including round K` phrase must also name the newest closure. Keep round83 history, but never give it a second latest pointer.
7. IMPORTANT inherited compatibility risk: `round42:380-384` also requires a `run <backticked command> → <backticked output>` fact in every axis evidence cell, with the axis needle in the COMMAND, not its output. For calibration the needle is `verifier-spotcheck`. Inherited `round41:68,136-144` executes recognized run commands and matches an exact stdout line plus optional `(exit N)`. The observed calibration row, and this conservatively retained proposed row, have no recognized run fact; `Re-derive with ...` is not one, and the ordinary newest-closure command lacks the command needle. Therefore a green frozen two-cell C1 would not establish a green full self-description gate. L1 must supply genuinely measured, compatible run evidence during integration rather than inventing an output or weakening the rule. This seat was not assigned command execution and has not manufactured that evidence.
8. Keep dated sections append-only. Do not change frozen round84 claims/closure to erase the honest disclosure miss, or attribute any b53 measurement to a later publication tip. Receipt/source evidence does not establish runtime readiness or whole-record correctness.

## Commands and execution boundary

Only non-gate shell operations: explicit `mkdir -p` for owned scratch (exit0), explicit `env TMPDIR=/fast/scratch/hyaku/kama-r85/EX03RecordDraft mkdir -p` for owned output (exit0), the two read-only identity commands above (exit0), and cleanup of the empty owned scratch directory. No clone or fixture repository was needed. No build, lint, test, formatter, counter, selftest or live endpoint sampling was run. Parent owns post-integration checks. No LSP tool is exposed in this seat's tool inventory; definitions were inspected through source reads, not an empty cold symbol response. No tools installed or updated.

## Risks and handoff

- Full selfdesc run-fact compatibility needs parent integration evidence, not a fabricated success claim.
- Publishing a new round heading changes banner/Planned expectations even though the two frozen authority cells remain the C1 population.
- Report requested at `.ufo/waves/round-85/w1/EX03RecordDraft.md` conflicts with the stricter explicit output-only directory bound. This report is retained inside the exclusive directory instead; L1 can publish it at the requested aggregate location.
- Parent should run the committed C1 predicate and full self-description/pre-report gate after integration; none was exercised here.

Self-evaluation (author advisory): accuracy4 (source-backed, runtime checks intentionally unexercised); completeness4 (exact replacements and parser constraints delivered, parent run-fact integration remains); clarity4 (parser detail necessarily dense); actionability4 (pasteable cells, but existing full-gate compatibility requires genuine evidence); conciseness4 (retained command/evidence detail dominates). Mean4.0. Highest-impact action: obtain truthful run-fact evidence before final gate; preserve updated heading/plan consistency. User-agreement self-check: deliverable and execution limits are explicit, with no admission claim.

Report: .ufo/waves/round-85/w1/out/EX03RecordDraft/EX03RecordDraft.md
