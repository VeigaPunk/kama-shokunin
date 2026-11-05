# SB01SectionDraft — kama r86 w3 terminal falsification (scoped findings)

Pinned revision: `bafae7afb41843564ac2468d28beb8e0bb98e8e6` (read via `git show`; scratch archive of that tip).
Lane master moved during this seat (`84e6f457…` at the last read). `239a8f39` and `ec541687` are descendants of
`bafae7af` and were **not** graded here. Drafted sections: `.ufo/waves/round-86/w3/out/SB01SectionDraft/sections.md`.
Probe evidence: `.ufo/waves/round-86/w3/out/SB01SectionDraft/probes/`. Each `*.out` is the saved stdout of its script at `bafae7af`. `probe_c1.py` and `diff_cal.py` hard-code `COPY` to the scratch `git archive` that was removed; point `COPY` at a fresh `git -C <lane> archive bafae7af… | tar -x -C <dir>` to re-run. `probe_c2.py` and `probe_c3.py` take the root as `argv[1]`. Pin probes do not touch the network.

## Verdicts (per claim, at `bafae7af`)

| Item | Verdict | Basis |
|---|---|---|
| C1 calibration (counter) | **Counter green reproduces; instrument falsified against its own predicate** | `count.py c1` → `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`, exit 0. But P-A grades exit 0 while the CommonMark reference renders the stale cells (F1); P-B and P-C are green on wrong input (F2, F3). |
| C2 operability | **Verified; no false green found** | `count.py c2` → `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`, exit 0. Classifier probes fail closed (F6). One stale lesson number (F8). |
| C3 freshness (counter) | **Offline legs verified; live leg NOT-RE-DERIVABLE; origin binding falsified** | Live fetch not run (bounds). Offline: digests and line counts match for 10 anchors. P-G (row refs unbound) and P-H (self-declared header URL → `verified`) (F7). |
| Sources census | **Verified** | base `validate` exit 0, 317 rows; tip `validate` exit 0, 319 rows (sections B). |

## Findings

**F1 — C1 false green: a list-marked fence line closes a top-level fence (high).**
- Pointer: `tools/round86-rendered-cells.py:66-68` — `CONTAINER`, `FENCE` and `FENCE_CLOSE` all accept list or blockquote prefixes. The close test at `:180-184` therefore closes a top-level fence on a `- ```` line. CommonMark 0.31.2 §4.5 defines the closing fence as a fence line with at most three spaces of indentation; a `- ` marker makes the line content, not a closer.
- Fixture `probes/P-A-list-marker-fence.md`: shadow `` ```markdown `` / `- ```` / correct cell / `## Axes` / good row / `` ``` ``, then the stale live cells. `grade()` → `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1`, exit 0 (`probes/probe_c1.py`).
- Reference: `cmark 0.31.2 --sourcepos -t xml` (system `/usr/bin/cmark`) → `<code_block sourcepos="3:1-9:3">` covers the shadow; `<heading sourcepos="11:1-11:7" level="2">` is the live `## Axes`; `<paragraph sourcepos="13:1-14:215">` is the **stale round-84** authority and row. The rendered head is stale and the instrument's green is wrong.
- Coverage gap: `measured/after/c1-mutants.py` mutates only `FENCE` (`h-container-off`, `f-tilde-off`), never `FENCE_CLOSE`; no selftest arm holds a list-marked closer. The red set of the counter cannot see this class.

**F2 — C1 disposition oracle reads the first fixed-order word anywhere in the closure body (medium).**
- Pointer: `tools/round86-rendered-cells.py:83` (`DISPOSITIONS` order) and `:265-269` (`disposition_of`), used at `:331-338`.
- Probe P-B: closure body `Verdict: rejected-honest-stop … round 83 was rejected-harmed`, row `(round85 rejected-harmed; …)` → exit 0. The predicate says "the word must occur in the closure body"; it does not say which occurrence. Tip data is not affected: the round-85 closure contains no `rejected-harmed` (count 0) and its verdict is `rejected-honest-stop` (`corpus/lessons/round-85-verifier-spotcheck.md:66`). The oracle can still green a wrong row.

**F3 — C1 coupling accepts any of several cited revisions (low).**
- Pointer: `round86-rendered-cells.py:308-317` (loop over all revisions; the clause fails only when none carries the token).
- Probe P-C: the cell cites `B` (an ancestor without the receipt) and `A` (carries it) → exit 0. The predicate says "a 40-hex revision `R`" (singular).

**F4 — C1 gate fact is satisfied by a red, previous-round receipt (medium; scope of the record).**
- At `bafae7af` the newest committed PRE_REPORT is round 85: `.ufo/waves/round-85/measured/after/gate.out` → `PRE_REPORT round=85 arms=13 failed=1 uncommitted=0`. No round-86 gate receipt is committed (`git ls-tree -r --name-only bafae7af .ufo/waves/round-86/measured/` lists only `before/` and `after/` c1–c3 files). Yet the head reads `**Current authority (round 86):** … Latest measured round: 86` (`SCORECARD.md:6`). C1 has no `failed=0` clause and no current-round clause, so it certifies that the head names the newest receipt, red or stale.
- Lane status context (read-only, not graded): the worktree holds an uncommitted `measured/terminal/gate.out` with `PRE_REPORT round=86 arms=13 failed=0 uncommitted=0`.

**F5 — C1 mutation coverage (informational).** The C1 selftest has 17 arms at `bafae7af` (re-run here: `pass=17 fail=0`) and the mutant driver has 10 mutants (re-run here: `mutants=10 killed=10 escaped=0`). The arms cover the opener, correction, column-0 and receipt legs. None covers the closer (F1).

**F6 — C2 classifier: no false green found; survivors fail closed (verified).**
- `probes/probe_c2.py` (output `probes/probe_c2.out`) on `classify()` (`tools/round86-mutant-owners.py:98-146`):
  - consistent forged green (`arms=34` hard-coded, a dropped arm) → `verdict=escaped` → grade red (exit 1);
  - a subject that lowers its own `EXPECTED_ARMS` to 33 to match a dropped arm → `escaped` → red;
  - an owned FAIL line with a lying `fail_lines=0` → `killed` under the label `summary-cardinality`, which does not count as owning → `owners` falls, exit 1.
- `DECLARED_POPULATION = 34` (`:91`) is compared only for the pristine run (`grade()` takes `arms_value` from the pristine output, `:173-174,194-195`). A mutant that claims a different population is `escaped` and so red. This matches the lesson's disclosed limit (`corpus/lessons/round-86.md`, M6); the limit is red, not silent.

**F7 — C3 origin is self-declared; the row's refs are not bound (high for the "origin" claim, low for the committed data).**
- Pointer: `tools/round86-pin-origin.py:102-117` fetches `info["url"]`, taken from the anchor's own header. `grade()` (`:136-160`) reads only `extract_pin` and `extract_newest` from the row, never `ref`, `newest` or `engine`.
- P-H (`probes/probe_c3.py`): both anchor headers name `https://example.invalid/fabricated/README.md`, the injected fetch serves the same fabricated body → `verified`. The "mismatch" clause (bytes differ from upstream) is not triggered, because the declared upstream is the one the file chose. The instrument corroborates bytes against a URL the file names, not against the row's engine and ref.
- P-G (same probe file): row `ref=b11755 newest=b12111`, both headers naming `…/b7200/…`, bytes matching → `verified`. Committed data is consistent (all ten header `ref=` values match the row columns in `registry/pin-recheck-rows.tsv`, checked by hand), so the tip verdict is not affected.
- Live leg: `measured/after/c3.out` (`PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0`) is **NOT-RE-DERIVABLE** here (no network beyond the named bounds). Offline legs re-derived: 10/10 `digest_ok=True`; `stored_newlines == declared` 10/10.

**F8 — record numbers against committed bytes.**
- Lesson M3 says `7/7 … mutants=7 killed=7` (`corpus/lessons/round-86.md:59`) and cites `measured/after/c1-mutants.out`. The receipt says `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`, and the SCORECARD says 10. **Stale lesson number.**
- Only the `before/` receipts carry `exit=` lines; `after/c1.out`, `after/c2.out` and `after/c3.out` do not. The SCORECARD's `exit0` for the after measurements is therefore not receipt-backed. Re-derived here: c1 exit 0, c2 exit 0; c3 not run.
- No `after/` receipt names its measurement revision (no 40-hex in `after/c1.out` or `after/c2.out`; `c3.out` has one, the upstream commit inside a URL). SCORECARD rows 5271–5273 write `--rev <measured>` as a placeholder. Only the c3 before-receipt names its revision (`3ff23da3…`).
- Frontier arithmetic (317→319, A 302→304, mined 284→286) re-derived exactly (sections B).
- `APPEND_DEBT round=86 … unaccepted=0 bad_rows=0` re-derived, exit 0 (`events=80 accepted=53 late=27 pending=3`). `pending=3` is printed by the counter and appears in neither the round-86 SCORECARD section nor the round-86 LOG entry (0 hits in either).
- The SCORECARD says S578/S579 were "admitted this round" (`SCORECARD.md:5299`); their registry status is `mined` (`corpus/SOURCES.md:333-334`). The decision lives in the lesson's gate table; the wording conflates decision with status.
- Assimilation: the SCORECARD says `Assimilation: none` (`SCORECARD.md:5299`), but the tip `corpus/QUALITY.md` carries criterion `KQ139` (`QUALITY.md:669`, "mined from `considerthese/2026-10-26.md` proposal 3"). The tip lesson has no Assimilation or considerthese text. The mining is committed in QUALITY and unrecorded in the lesson.
- Terminal-record status: the tip commit subject is `kama r86: preserve in-flight work at hyaku run-15 wrap-up (L1 died on provider failure; not a landed round)`. The SCORECARD and LOG both present round 86 as landed.

## Commands this seat ran (scratch: `/fast/scratch/hyaku/kama-r86/SB01SectionDraft/`)
- `python3 .ufo/waves/round-86/count.py c1 --repo <lane> --rev bafae7af… --work <scratch>/w/c1` → `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`, exit 0.
- `python3 .ufo/waves/round-86/count.py c2 --repo <lane> --rev bafae7af… --work <scratch>/w/c2` → `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`, exit 0.
- `count.py c3` NOT run (live fetch).
- `tools/round86-rendered-cells.py --selftest` → `RENDERED_CELLS_SELFTEST pass=17 fail=0`, exit 0.
- `tools/round86-mutant-owners.py --selftest` → `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`, exit 0.
- `tools/round86-pin-origin.py --selftest` → `PIN_ORIGIN_SELFTEST pass=7 fail=0`, exit 0.
- `tools/round81-append-debt.py --selftest` → `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0`, `APPEND_DEBT_SELFTEST pass=34 fail=0`, exit 0, stderr 0 bytes.
- `measured/after/c1-mutants.py <copy>` → `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`, exit 0.
- `scripts/sources-census.sh validate` for the base scratch root, the tip scratch root and the lane run-start form → exit 0 each; `census` counts as in sections B.
- `tools/round81-append-debt.py --repo <clone> --round 86` on a `git clone --shared` checked out at `bafae7af` → `APPEND_DEBT round=86 base=3ff23da3f291 events=80 accepted=53 late=27 pending=3 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0.
- Reference parser: `cmark --sourcepos -t xml` on `P-A-list-marker-fence.md` and on the tip SCORECARD. Count differential: 19 of 19 non-code authority lines agree with the instrument; column-0 calibration rows: cmark 3 non-code of 4, instrument 3.
- Offline anchor check (10 headers: digests, line counts): inline script; summarised in F7 and in `probes/diff_cal.out` (first line: `P-H verdict: verified`).
- NOT run: `count.py c3` (live fetch); `pre-report-gate.py` (runs live llama.cpp arms; not needed to grade `bafae7af`).

## Tools
- Installed: none. Existing system binary used: `/usr/bin/cmark` (cmark 0.31.2, CommonMark reference); `python3` 3.14.8 stdlib; `git`.
- No `pacman`, no change under `~/.local/bin`, no network calls.

## Repo and scratch hygiene
- Git commands were reads only (`show`, `ls-tree`, `diff`, `cat-file`, `merge-base`, `archive`, `status`), plus `clone --shared` into scratch. The clone was checked out in scratch and asserted by `rev-parse --show-toplevel` (`…/SB01SectionDraft/clone`).
- Lane writes: only `.ufo/waves/round-86/w3/out/SB01SectionDraft/` and this report.
- Not mine, observed in the lane: untracked `abs.err`, `abs.out`, and sibling `w3/*.md` files. Left untouched.
- Scratch removed before yield.
- Disclosure: my own `/tmp/sb01-*` fixtures (2 dirs) were removed, and so were `/tmp/r86-origin-*` directories (the pin-origin selftest's `TemporaryDirectory` prefix). Those may have included a concurrent sibling's in-flight selftest tempdir; I did not inspect them and cannot restore them. No other `/tmp` content was touched.
