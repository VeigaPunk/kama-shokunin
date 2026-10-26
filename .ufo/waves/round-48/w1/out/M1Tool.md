# M1Tool — round 48 C1 tool mutation test (`tools/append-only-audit.py` v3)

**Verdict:** 55 single-point mutants of the C1 tool: **32 killed by `--selftest`, 6 killed by the frozen C1 counter, 2 equivalent, 15 SURVIVED both** — the 15 survivors are coverage findings; the sharpest is that C1's selftest leg is self-certified: a tool that suppresses its own selftest failures (M50/M51) or hardcodes `fail=0` (M49) passes all five C1 legs with `met=True`.

## 1. Scope and method

Target: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py` (898 lines, sha256 `ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`, byte-identical to `tools/append-only-audit.py` at lane commit `380bcdff9c8af06997c482f6eb03db926a794a2b` — verified via `git show 380bcdff…:tools/append-only-audit.py | sha256sum`). Scratch `S=/fast/scratch/hyaku/kama-r48/M1Tool` (`TMPDIR=$S`); the lane was never written.

Procedure (all commands logged under `out/M1Tool/`):

1. **Baseline.** `python3 $S/pristine-append-only-audit.py --selftest --scratch $S/st-pristine` → exit 0, `AOA_SELFTEST pass=27 fail=0` (`logs/pristine-selftest.txt`). A baseline failure would have made every result inconclusive; it passed.
2. **Fixture.** `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/fixture` (the one permitted live clone), `git -C $S/fixture checkout -q 380bcdff9c8af06997c482f6eb03db926a794a2b`, toplevel asserted equal to `$S/fixture`. Baseline frozen counter on the pristine fixture: `python3 …/tools/round48-append-audit-v3-check.py --repo $S/fixture --tip 380bcdff… --scratch $S/counter/baseline` → **exit 0, `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`** (`counter/baseline.out`) — matches the pre-wave dry run, so the harness is sound before any mutant.
3. **Generation.** `gen.py` applied 55 single-point mutations to separate copies (`mutants/<id>.py`, unified diffs in `diffs/`); every `old` string was asserted to occur **exactly once** in the pristine source (the generator aborts otherwise — no mis-anchored mutant). Per-file sha256 of pristine + all 55 mutants: `hashes.txt`.
4. **Selftest.** Every mutant ran `--selftest --scratch $S/st-<id>` (8-way parallel, `runner.sh`); full stdout/stderr in `logs/<id>.txt`. Killed-by-selftest = exit ≠ 0 / `fail>0` / missing verdict line.
5. **Counter on survivors.** For each of the 23 selftest survivors (`survivors.txt`): copy mutant over `$S/fixture/tools/append-only-audit.py`, commit with fixture identity (`-c user.name=M1Tool-fixture -c user.email=m1tool-fixture@invalid -c commit.gpgsign=false`, pathspec limited to `tools/append-only-audit.py`), then the frozen counter with `--repo $S/fixture --tip <mutant tip> --scratch $S/counter/<id>` (`counter-runs.sh`; per-run output `counter/<id>.out` records the mutant tip). The counter reads the tool **from the tip** (`round48-append-audit-v3-check.py:647` `src = show(a.repo, tip, TOOL)`), so each run measured exactly that mutant.

## 2. Tally and full results table

| verdict | count |
|---|---|
| killed-by-selftest | 32 |
| killed-by-counter | 6 |
| survived (findings) | 15 |
| equivalent | 2 |

`table.tsv` (verbatim, one row per mutant; `counter` column shows the C1 legs):

```tsv
mutant	selftest	counter	verdict
M09-window-all-commits	KILLED(fail=14)	-	KILLED-BY-SELFTEST
M53-titles-overwrite	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M49-selftest-fail-hardcode	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M01-parse-region-fullmatch	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M46-expand-any-to-all	KILLED(fail=2)	-	KILLED-BY-SELFTEST
M06-sections-no-crlf-strip	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M35-decl-exempt-drop-rederived	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M52-eligible-guard-drop	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	EQUIVALENT
M29-binds-drop-negations	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M21-by-geq-equivalent	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	EQUIVALENT
M38-contract-cells-4	KILLED(fail=9)	-	KILLED-BY-SELFTEST
M14-g-double	KILLED(fail=9)	-	KILLED-BY-SELFTEST
M15-ng-distinct	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M10-only-prefix-equality	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M31-binds-drop-self	SURV	met=False(selftest=1,contract=0,lane=0,fixture=1,stable=1)	KILLED-BY-COUNTER
M17-held-ignore-k	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M18-k-no-subtract	KILLED(fail=10)	-	KILLED-BY-SELFTEST
M45-vanished-keep-present	KILLED(fail=4)	-	KILLED-BY-SELFTEST
M27-exit-drop-vanished	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M07-eligibility-strict-gt	KILLED(fail=2)	-	KILLED-BY-SELFTEST
M08-window-exclude-event	KILLED(fail=4)	-	KILLED-BY-SELFTEST
M40-threshold-leq	KILLED(fail=4)	-	KILLED-BY-SELFTEST
M55-decl-region-star-drop	KILLED(fail=4)	-	KILLED-BY-SELFTEST
M12-exempt-always	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M47-render-deleted	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M44-hunk-new-start	SURV	met=False(selftest=1,contract=1,lane=0,fixture=1,stable=1)	KILLED-BY-COUNTER
M50-selftest-fails-zero	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M23-status-swap	KILLED(fail=11)	-	KILLED-BY-SELFTEST
M22-status-ungraded-invert	KILLED(fail=19)	-	KILLED-BY-SELFTEST
M30-binds-or-to-and	KILLED(fail=6)	-	KILLED-BY-SELFTEST
M11-only-prefix-none-crash	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M13-exempt-inverted	KILLED(fail=20)	-	KILLED-BY-SELFTEST
M02-parse-region-exempt-prefix-drop	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M05-sections-no-trailing-strip	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M03-parse-region-only-prefix-drop	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M36-decl-exempt-all-to-any	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M19-by-drop-ng	SURV	met=False(selftest=1,contract=1,lane=1,fixture=0,stable=1)	KILLED-BY-COUNTER
M41-numstat-additions	KILLED(fail=18)	-	KILLED-BY-SELFTEST
M26-exit-drop-regressed	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M42-deleted-pos-plus-one	KILLED(fail=17)	-	KILLED-BY-SELFTEST
M16-held-no-clamp	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M43-psec-off-by-one	KILLED(fail=17)	-	KILLED-BY-SELFTEST
M54-sections-strict-decode	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M32-row-token-wildcard-base	KILLED(fail=2)	-	KILLED-BY-SELFTEST
M48-main-return-zero	SURV	met=False(selftest=1,contract=1,lane=1,fixture=0,stable=1)	KILLED-BY-COUNTER
M04-sections-prefix-nospace	SURV	met=False(selftest=1,contract=1,lane=0,fixture=1,stable=1)	KILLED-BY-COUNTER
M34-line-at-off-by-one	KILLED(fail=6)	-	KILLED-BY-SELFTEST
M33-row-token-keep-ext	SURV	met=False(selftest=1,contract=0,lane=0,fixture=1,stable=1)	KILLED-BY-COUNTER
M25-regressed-restored-only	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M37-decl-only-drop-prefix	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M24-regressed-leq	KILLED(fail=2)	-	KILLED-BY-SELFTEST
M20-best-last	KILLED(fail=3)	-	KILLED-BY-SELFTEST
M39-contract-drop-rule	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
M28-exit-drop-baddecl	KILLED(fail=1)	-	KILLED-BY-SELFTEST
M51-case-vacuous	SURV	met=True(selftest=1,contract=1,lane=1,fixture=1,stable=1)	SURVIVED
```

Item-target coverage map: positions M42/M43/M44/M34 · sections() prefix/strip M04/M05/M06/M54 · eligibility comparison+window M07/M08/M09/M52 · only-prefix filter M10/M11 · exempt membership M12/M13 · G counting M14/M15 · held clamp M16/M17/M18 · by condition M19/M20/M21 · status ungraded M22/M23 · regressed formula M24/M25 · exit_code terms M26/M27/M28/M48 · binds() negations/token/self M29/M30/M31 (+ row_token M32/M33) · parse_region M01/M02/M03 · declaration region checks M35/M36/M37/M55 · extras: parse_contract M38/M39, threshold M40, numstat M41, vanished M45, expand M46, file_regions union M53, render M47, main exit M48, selftest-verdict integrity M49/M50/M51.

Which selftest case killed each of the 32: `killed-cases.tsv` (e.g. M13 exempt-inverted → 20 cases; M41 numstat-additions → 18; M22 status-ungraded-invert → 19; M15 ng-distinct → `multiset`; M16 held-no-clamp → `clamp`; M26 exit-drop-regressed → `window-max`; M27 exit-drop-vanished → `vanished-and-paths`).

## 3. Findings — the 15 survivors (each with a proposed selftest case)

**F1 (M50-selftest-fails-zero) — C1's selftest leg is self-certified.** `fails = sum(1 for _, ok, _ in cases if not ok)` → `fails = 0`: the selftest prints `AOA_SELFTEST pass=27 fail=0` and exits 0 even while its per-case lines print `FAIL …`. The counter's sel leg (`round48-append-audit-v3-check.py:658-663`) regexes only the verdict line, so `selftest=1`; every other leg passes because the audit logic is intact → **`met=True` on all five legs** (`counter/M50-selftest-fails-zero.out`). Any tool defect that only the tool's own cases catch (parse_contract edge cases, render format, …) becomes invisible to C1. No tool-side selftest case can detect its own falsified printer — the remedy is counter-side (counter frozen → finding, not an in-place fix): cross-check the per-case lines, e.g. require `count of ^FAIL lines == fail=` and `pass= + fail= == count of ^(pass|FAIL) lines`, or pin the frozen tool's exact verdict `AOA_SELFTEST pass=27 fail=0`.

**F2 (M51-case-vacuous) — same class.** `ok, why = fn()` → `ok, why = True, ""`: all 27 cases "pass" without running; identical `met=True` (`counter/M51-case-vacuous.out`). Same counter-side remedy as F1.

**F3 (M49-selftest-fail-hardcode) — same class, stdout-only.** `fail={fails}` → `fail=0`: observable only in a failing run's stdout, which C1 never reads because the exit gate (`return 0 if fails == 0 else 1`, unmutated) fires first. Counter-blind; same remedy as F1.

**F4 (M47-render-deleted) — the documented text output is unchecked.** `deleted={e['deleted']}` → `deleted={e['graded']}` in `render()`: the text mode the tool docstring documents (`event <c12> <file> deleted=N graded=G …`) reports the wrong number, and no frozen check looks at it — the counter always runs `--json` (`run_tool`, counter line 394) and the selftest never calls `render()`. Proposed selftest case: on the `t_exact_unrestored` fixture assert `render(res).splitlines()[0] == f"event {c[:12]} corpus/QUALITY.md deleted=20 graded=20 ungraded=0 restored_max=0 held_at_to=0 status=unrestored restored_best=- restored_by=-"`.

**F5 (M01-parse-region-fullmatch) — malformed region cells accepted.** `REGION.fullmatch(cell)` → `REGION.match(cell)`: a region like `only=## Errata@NOTES.md:4junk` parses (trailing junk ignored) where the contract says such a cell must exit 2. No selftest case and no fixture uses a suffixed region cell. Proposed case: add to `t_contract`'s bad list `HEADER + "\nLOG.md\tA\tAGENTS.md:1\tonly=## E@AGENTS.md:1junk\tx\n"` → must raise `AuditError`.

**F6 (M03-parse-region-only-prefix-drop) — `only=` prefix need not start with `## `.** `if not body.startswith("## ")` → `if False`: `only=Errata@p:1` is accepted; since no section title starts with `Errata`, every line of that file becomes ungraded — a vacuous audit. The bad `only=## E` case in `t_contract` fails on the missing `@pointer`, never on the prefix. Proposed case: `parse_contract(HEADER + "\nknow.md\tA-corr\tNOTES.md:4\tonly=Errata@NOTES.md:4\tx\n")` must raise.

**F7 (M39-contract-drop-rule) — the rule cell is never validated.** Dropping `rule not in RULES` accepts rule `B`; the rule is otherwise unused by v3 logic, so nothing downstream notices. Proposed case: `parse_contract(HEADER + "\nLOG.md\tB\tAGENTS.md:1\t*\tx\n")` must raise.

**F8 (M35-decl-exempt-drop-rederived) — the `re-derived` requirement is untested.** An exempt pointer that names every title but omits "re-derived" binds. The lane's pointer (SCORECARD.md:6) contains "re-derived", so the lane run cannot distinguish. Proposed case: NOTES line "The ## Axes and ## Plan heads of score.md are rewritten in place." (no "re-derived") with the SCORE row → `declarations[0]["ok"] is False` and exit 1.

**F9 (M37-decl-only-drop-prefix) — the only-pointer's prefix naming is untested.** `elif not binds(text, pat, pp) or region[1][3:]…` → dropping the second term: a pointer that binds as append-only but never names `## Errata` binds. The lane's pointer (consumer-registry.md:30) names it, so the lane cannot distinguish. Proposed case: NOTES line 4 replaced by "know.md is append-only." with the KNOW row → declaration `ok is False`.

**F10 (M53-titles-overwrite) — multi-row exempt union untested.** `titles |= set(region[1])` → `titles = set(region[1])`: when several rows match one file only the last row's exempt titles apply, contradicting the documented union ("a file matched by several rows takes the union of their exempt titles"). Every fixture and every lane file is matched by at most one exempt row. Proposed case: two rows both matching `score.md` with `exempt=## Axes@NOTES.md:3` and `exempt=## Plan@NOTES.md:3`; a deletion in the `## Plan` section must be ungraded (exit 0) — the mutant grades it.

**F11 (M05-sections-no-trailing-strip) — trailing blanks on a heading break the carve-out.** Dropping `.rstrip()`: a heading written `## Axes␠␠` titles its section `## Axes␠␠` ≠ `## Axes`, so the exempt carve-out silently stops applying (ungraded lines flip to graded). No fixture has a trailing-blank heading; the lane's headings happen to be clean. Proposed case: `scored([SCORE], head_with_trailing_blank_Axes + tail)`, rewrite the head → must still be `graded=0 ungraded=24`, exit 0.

**F12 (M06-sections-no-crlf-strip) — CRLF heading breaks the carve-out.** Dropping `rstrip(b"\r")`: a `## Axes\r\n` heading titles the section `## Axes\r`. `t_crlf_and_eof` exercises CRLF body lines but never a CRLF heading. Proposed case: raw CRLF file whose exempt heading ends `\r\n` → head rewrite must still be ungraded.

**F13 (M54-sections-strict-decode) — non-UTF-8 heading crashes the audit.** `decode("utf-8", "replace")` → `decode("utf-8")`: one invalid byte in any `## ` heading of any audited blob raises `UnicodeDecodeError` (exit 1 traceback) instead of decoding with replacement. Lane headings are ASCII, so the lane cannot distinguish. Proposed case: `sections([b"## Caf\xe9 x"]) == ["## Caf\ufffd x"]` without raising.

**F14 (M11-only-prefix-none-crash) — deleted line before the first `## ` heading crashes an only= file's audit.** Dropping `s is not None` from the only-filter: `None.startswith` raises `AttributeError` when a deleted line's parent position precedes the file's first heading. No fixture deletes pre-heading lines of an only= file, and no lane event at 380bcdff does either. Proposed case: `know.md` = 25 pre-heading lines + `["# know", "## Body"]` + body + errata; delete the 25 pre-heading lines → event must be `graded=0 … status=ungraded`, exit 0 — not a crash.

**F15 (M25-regressed-restored-only) — regressed ignores partial events.** `e["status"] in ("restored", "partial")` → `== "restored"`: a partial event whose `held_at_to < restored_max` is not counted in `summary.regressed` (exit unaffected — partial already exits 1 — but the count is a C1-compared summary key and the X1Stable semantics say "events whose file holds fewer…"). No fixture has a regressing partial (S6's partial has `held_at_to == restored_max`), and all 5 lane events are restored. Proposed case: 60-line file; delete 40 (event), restore 20 (partial, best=20), re-delete 5 (`held_at_to=15`) → `summary["regressed"] == 1`.

## 4. Equivalents (verified, not findings)

- **M21-by-geq-equivalent:** `h == ng` → `h >= ng` in the `restored_by` condition. `held(x) = Σ_l min(G[l], max(0, M_x[l] − K[l])) ≤ Σ_l G[l] = ng` for every x, so `h >= ng ⟺ h == ng` on every input. Counter agrees (`met=True`).
- **M52-eligible-guard-drop:** removing `if wb[f"{x}:{f}"] else 0` is behavior-preserving: `section_counts(None)` caches `Counter(sections([])) = Counter()` and `Counter()[t]` is 0 — identical to the guarded 0; the `None` cache key cannot collide with 40-hex blob ids. Counter agrees (`met=True`).

## 5. Killed-by-counter notes (what the frozen C1 caught that the selftest missed)

- **M04 sections-prefix-nospace** (`startswith(b"## ")` → `startswith(b"##")`): lane leg — SCORECARD.md event `0718b6ab` graded tool=2379 vs counter=2349, ungraded 42 vs 72, `ungraded_lines` 59 vs 89. The lane's SCORECARD.md contains `##`-without-space / `###` lines (e.g. the `### Superseded head banners` sub-headings) which the mutant promotes to section titles.
- **M44 hunk-new-start** (`start = group(1)` → `group(3)`): lane leg — both SCORECARD events mislocated (`0718b6ab` graded 2294 vs 2349; `dd9f5dc6` status partial vs restored, `restored_by` None vs `dd9f5dc6…`), exit 1 vs 0.
- **M19 by-drop-ng** (drops the `ng` guard): fixture leg S2 — `restored_by=55e6f543…` want `None` (an ungraded event must not name a restorer).
- **M31 binds-drop-self** (drops the self-declaration arm): contract+lane legs — 4 lane rows bind **only** via self-declaration (`corpus/lessons/*.md` at `corpus/lessons/round-23.md:100`, `registry/history/DELTA.md:3`, `registry/report-landing-errata.tsv:1`, `corpus/knowledge/consumer-registry.md:30`) → tool `bad_declarations` 4 vs 0, exit 1 vs 0.
- **M33 row-token-keep-ext** (token keeps the extension): contract+lane legs — `corpus/SOURCES.md` (declared at `SKILL.md:578`) names its token without the extension → `bad_declarations` 1 vs 0, exit 1 vs 0.
- **M48 main-return-zero** (`return exit_code(res)` → `return 0`): fixture leg — 9 of 11 scenarios expect exit 1 (`fixture_fail=9`).

Positive note surfaced by M27: a vanished declared file is absent at `<to>`, hence never in `files`, so its deletion never becomes an event — the `vanished` exit term is the only thing that flags it, and selftest case `vanished-and-paths` does exercise exactly that path (M27 killed there, exit 0 vs 1).

## 6. Restoration and hygiene evidence

- Lane file untouched throughout: `sha256sum …/kama-shokunin/tools/append-only-audit.py` = `ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72` before and after all work; no lane path was ever written (all writes went to `$S` and `out/M1Tool/`).
- Per-mutant before/after hashes: `hashes.txt` (pristine + 55 mutants; each mutant differs from pristine by exactly the one replacement shown in its `diffs/<id>.diff`).
- The scratch copy is disposable per the operator directive: fixture clone, mutant copies and counter scratch live only under `/fast/scratch/hyaku/kama-r48/M1Tool` and were removed (`rm -rf`) after the evidence was copied out; `/tmp` was never used as evidence. The 23 mutant tips are recorded in `counter/<id>.out` (`tip=` lines).
- No tooling installs were needed or made (python3 + git only; no pacman transaction, per the 2026-10-20 pause).
- None of the findings above restate the three known integration items (unregistered round-48 counters; round-41/42/43 spot-check count 33 vs 34; hexrun-census d0012618).
