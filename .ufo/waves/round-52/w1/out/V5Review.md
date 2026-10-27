# V5Review — round-52 C2 counter-vs-preregistration review

Verdict: **PASS — no defect found.** `tools/round52-append-restore-check.py` (sha256 `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea`) matches its preregistration on every seat item: the PREDICATE sentence is the preregistration's C2 predicate verbatim (line-wrap only), all four predicate clauses have implementing code, nothing outside the predicate can produce `met=True` (extras are kill-only), `deleted()`/numstat agreement is enforced per event, the A-row cell split `MUT=(7,9,10)` is exact against the real SOURCES.md header, fixture identities are clean, and the exempt= simplification is precisely the preregistered limit. The frozen base control reproduces byte-identically; the build run reproduces the L1 battery verdict.

All line references are to `tools/round52-append-restore-check.py` at lane commit 8551ba7f2056f2465d20f5b50586978133212fe1 (the file is identical in the working tree; sha256 above was taken from the working tree and equals the frozen counter_sha256).

## 1. sha256 equals counter_sha256

- `sha256sum tools/round52-append-restore-check.py` → `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea`
- preregistration.json `claims[C2].counter_sha256` → `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea` — equal.

## 2. PREDICATE sentence equals the preregistration's C2 predicate

- Counter docstring lines 64–72 (`PREDICATE (same sentence in the preregistration): … corr_lost=0.`), whitespace-normalized, compares **equal** to `claims[C2].predicate` (programmatic compare; raw bytes differ only by the docstring's hard line wraps). The sentence covers all four clauses: corr_lost=0 by the counter's own section and fence logic; ledger names exactly the unheld A/A-row lines; the tip's append-only-audit exits 0 on the lane; eight constructed scenarios each get the verdict their construction fixes; `fixture=1 lane=1 corr_lost=0`.

## 3. Every clause has code

| Clause | Code |
|---|---|
| deleted graded lines held at --tip (corr_lost=0), counter's own section/fence logic | `sections()` 157–177 (fence-aware `## ` tracking: OPEN 168–172, close 163–167, unclosed runs to EOF); `region_of()` 180–190; `graded_of()` 214–247 (exempt 240–241, only 242–243, A-row permission 219–227); `recompute()` 249–302 (unheld `n - min(n, max(0, M_tip - kept))` 285–299); corr tally in `lane()` 479–485 and `return ok and corr == 0` 496 |
| ledger names exactly the unheld A/A-row lines | `lane()` 461–494: key-by-key Counter equality `un != led.get((c,f))` 474–479; A-corr ledger rows rejected 481–485; every ledger key must be a deletion event of a declared file 486–489 |
| tip's append-only-audit exits 0 on the lane | `run_tool()` 303–311 (tip's own bytes via `git show {tip}:tools/append-only-audit.py`, `--json`, no `--threshold`); `lane()` 436–447 (`code != 0` → fail; plus summary `unrestored/partial/regressed/bad_disclosures/bad_declarations == 0`, stricter than bare exit-0, kill-only) |
| eight constructed scenarios, verdicts by construction | `fixtures()` 332–433: corr-in-place 387, corr-fenced-reappend 388–391 (five-backtick fence, `fence` 384), cutoff-after-intro 426, cutoff-before-intro 427, only-outside 428, only-inside 429, exempt-inside 430, exempt-dated 431 — exactly NSCEN=8 (102); each checks tool exit **and** counter unheld/graded 371–382, 393–425; `fl = n == NSCEN` 528 |

## 4. Nothing outside the predicate decides met

- `met = bool(fl and ll)` 529; `ll = ok and corr == 0` 496. Every failure site only ANDs False into `ok`/`fl` (no site can set them True): tool exit/summary 437–447, base-contract-row presence 448–457, recompute numstat+tool-event agreement 272–278 (`ok = ok and rok` 467), rowfile ledger equality 474–479, A-corr ledger rejection 481–485, ledger-key-is-event 486–489.
- The base-contract leg (448–457) and numstat/tev agreement (263–278) are stricter than the predicate sentence but kill-only: they can force met=False, never met=True. They are pre-declared in the frozen docstring Legs (50–62) and consistent with the preregistration's separability note ("its counter reads the tool, the contract, the ledger and git history").
- Exit contract honored: met → 0, not met → 1, could-not-evaluate → 2 (511–513, 517–519, 538); observed exit=1 at base, exit=0 at build, exit=1 on my deletion probe.

## 5. deleted()/numstat agreement

- `recompute()` walks `rev-list --topo-order --reverse --parents` first-parent diffs (253–260; root commits skipped 262), runs `git diff --no-renames --numstat -z` (263) and independently re-derives deletions with `deleted()` (`-U0 --text`, hunk-header counts, 192–212); any count mismatch appends a detail line and clears `ok` (272–275). The tool's own event deleted-counts are cross-checked too (277–282). Both runs (base, build, probe) produced zero mismatch details. Header-count slicing and position bookkeeping (`start + gd`, 203) are self-consistent with -U0 output; `\ No newline` markers are skipped by the elif chain (199–208).

## 6. A-row cell split

- `ROW` (97) matches `^ {0,3}\| *S[0-9]{3,} *\|`; `cells()` 138–155 splits on `|` outside backtick spans and requires the row to end at the last cell (154).
- `MUT = (7, 9, 10)` (98) = 1-based cells 8/10/11 = **status / recheck / used-by**, exactly the docstring's "cells other than 8, 10, 11" (36) and the contract note for corpus/SOURCES.md ("only status, recheck and used-by change in place"). Real header verified at the build tip, `corpus/SOURCES.md:11`: `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |` — 11 cells.
- Permission direction is correct: a deleted row is permitted only if the **commit's** blob still holds an equal-id row with all immutable cells byte-equal (219–228); only exact rule `A-row` gets it (232, `any(r == "A-row")`), while the lane ledger comparison treats `A` and `A-row` as rowfiles (472) — so the rule-`A` errata file's in-place row edits stay graded, matching the build's 3 kept errata rows; SOURCES.md's 7 kept rows are the immutably-edited ones. Ledger shape matches DHEADER (95); build-tip ledger = header + 10 rows (7 SOURCES + 3 errata) = the preregistration's "keeps only the A/A-row rows".

## 7. Fixture identities

- Fixtures live under `S = tempfile.mkdtemp(prefix="r52c2-", dir=root)` (510) with `root = a.scratch or TMPDIR` (508) — under `--scratch` as required.
- Both repo builders init and **assert toplevel before any commit**: 358–361 and 397–400 (`rev-parse --show-toplevel` realpath must equal the fixture dir), and every commit uses `IDENT` (99: `user.name=r52c2-fixture`, `user.email=r52c2@invalid`, `commit.gpgsign=false`) via the `git()` helper that always passes `-C repo` (109–113). No throwaway identity outside scratch fixtures; `--repo` is only read.
- Expectations are by construction and both verdict sources are checked (tool exit + counter recomputation on the same repo, 374–381); the fenced-reappend fixture proves the exact build mechanism (deletion graded but held → unheld 0, tool exit 0, observed in both runs).

## 8. exempt= simplification vs the preregistered limit

- Limit: "the counter's exempt= rule is simpler than the tool's (a deleted line in an exempt-titled parent section is ungraded; the tool also requires the line's origin to hold an exempt title and the section not to be gutted), so in SCORECARD.md the counter may grade fewer lines than the tool; the tool leg holds the stricter rule."
- Code: `graded_of()` grades a deleted line iff its **parent-blob** section title is not in the exempt set (218, 233–241); no origin check, no gutted check — exactly the stated simplification. `region_of()` strips the `@p:n` provenance and splits titles on `|` (183–186); the build contract gives SCORECARD.md `exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities` (verified at 5dacf2c7), and the fixture pair exempt-inside/exempt-dated exercises both sides (430–431).
- Quantitatively confirmed: at the base the counter's own unheld A-corr = **151** while the tool/ledger side disclosed 155 A-corr lines (165 − 10 A/A-row) — the 4-line gap is the SCORECARD exempt simplification, as the limit says. `base.c2.repro.out` tail: `own graded 5867; own unheld A-corr 151, A/A-row 10; ledger lines 165`.

## 9. Reproduction runs (clone `git clone --shared`, scratch `/fast/scratch/hyaku/kama-r52/V5Review`)

- Base `9ff76b1f`: `python3 tools/round52-append-restore-check.py --repo $S/lane --tip 9ff76b1f… --scratch $S --out $S/base.c2.repro.out` → exit 1, `fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False` — **byte-identical** to the frozen control `.ufo/waves/round-52/controls/base.c2.out` (all 48 detail lines match).
- Build `5dacf2c7`: same command → exit 0, `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` — matches `claims[C2].target` and reproduces `.ufo/waves/round-52/measured/c2-build.out` exactly except that receipt's invocation banner and trailing `exit=0` line (diff shown; all verdict/detail lines identical).
- Deletion probe (my own clone; fixture identity `fx <fx@invalid>`, toplevel asserted before commit): at tip `60b092cd0bcbbe797308e653742cb7a33feec212` = build tree minus declared A-corr file `corpus/knowledge/error-is-not-a-verdict.md` → exit 1, `corr_lost=0` but `bad_declarations: 1` → `met=False` (probe-remove.out).

## Findings by severity

**Blocking defects: none.**

**Minor / defense-in-depth observations (kill-only or covered; counter is FROZEN — report only):**
1. The counter's own recomputation is blind to whole-file removal of a declared A-corr file: `files_of()` (317–323) expands contract rows over the **tip tree only**, so a `git rm` of e.g. `corpus/knowledge/error-is-not-a-verdict.md` yields no unheld event (`corr_lost=0`, graded unchanged at 5868 in my probe). The verdict still lands met=False because the predicate's tool clause catches it (`bad_declarations: 1`, tool exit 1 — probe evidence in probe-remove.out). Residual exposure: only if a future tool version stopped flagging missing declared files would this gap become a false-met. Hardening sketch (not applied): fail when a declared path is absent at tip, or union base and tip trees in `files_of`.
2. Binary intermediate states of a graded file are skipped (`parts[1] in ("-", "0")`, 264–266): deletions made while a file was binary escape both legs. Contrived for markdown A-corr files; noted for completeness.
3. `cells()` treats backticks as a toggle (146–147), so an odd backtick count flips "code" for the rest of the row. The same parser reads both the deleted row and the commit's blob rows, so any misparse is symmetric; low risk to the A-row permission's fidelity vs "outside backtick spans".
4. A malformed ledger row (non-integer count, `int(c[3])` 464) raises uncaught ValueError → traceback with exit 1 instead of the documented exit-2 "could-not-evaluate". Cosmetic; the operator sees the traceback, and no verdict is produced.

## Residual risk and verification gaps

- I did not fuzz `deleted()` against adversarial diff bodies; agreement with numstat is enforced per event (272–275) and held on every run, which bounds the exposure to header-count slice errors that numstat would not see (both derive from the same git diff machinery).
- The tool's (`append-only-audit.py`) internal exempt/origin/gutted logic was not re-derived here; per the preregistered limit the counter is intentionally simpler and the tool leg carries the stricter rule — the counter side is what this seat was scoped to verify.
- No llama-server processes were started by this seat (C2 counter makes no network calls; `pgrep -af llama-server` clean). Scratch removed at cleanup; receipts cited above copied to the out dir.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/V5Review.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/V5Review/base.c2.repro.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/V5Review/build.c2.repro.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/V5Review/probe-remove.out`
