# V1Code — code review: tools/release-recheck.py + tools/round44-release-recheck-audit.py (round 44 w1)

**Verdict: the counter (round44-release-recheck-audit.py) is docstring-conformant on every rule I could exercise, with two minor doc/leniency gaps; the drafter (release-recheck.py) has two major defects — its documented exit 2 is unreachable and a broken/unreadable upstream or pin silently emits plausible-looking TODO rows with a false reason (changed=0). Selftest 5/5; counter on the freeze commit is well-formed exit 1 (ledger not yet at tip); draft regeneration reproduces the frozen C1 draft byte-identically.**

Evidence receipt: `.ufo/waves/round-44/w1/out/V1Code/receipts.txt` (R0–R5, cited below as R#).

## Method
- Read both tools in full; AST-compared shared functions (`cited` identical; `population` differs only by `repo_url` parameterization; URL regexes equivalent; HEADER identical).
- `python3 tools/release-recheck.py selftest` → 5/5 PASS, exit 0 (R0).
- `python3 tools/round44-release-recheck-audit.py --repo <lane> --tip 77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40 --upstream /fast/scratch/hyaku/kama-r44/shared/llama.cpp` → `pop=91 rows=0 valid=0 unverified=91 … section=0 met=False`, exit 1, all 91 ids in `detail:` (R1). Correct pre-integration state and matching the frozen 91-row population.
- Regenerated the C1 draft from upstream bytes: exit 0, 92 lines (81 holds / 6 TODO / 4 unchanged-file), byte-identical to `.ufo/waves/round-44/c1/draft-ledger.tsv` (R2).
- Fixture matrices in a scratch clone/upstream (never touching the lane): drafter T1–T4/T1b (R3); counter with lane BASE 9d9cc93ec507 replaced via `git replace` inside a scratch shared clone, exercising met/not-met/exit-2 paths with real upstream bytes incl. a real file deleted at b11889 (`tools/ui/src/lib/components/app/dialogs/DialogManageModels.svelte`) (R4).

## Defects (severity first)

**F1 MAJOR — `tools/release-recheck.py:21,43,190`: documented exit 2 unreachable; input failure exits 1 with a traceback.**
Docstring line 21: "Exit 0 written (TODO rows included), 2 a git or input failure." Neither fires: line 43 `raise SystemExit(f"git …")` exits **1** (not 2), and in the `draft` path `git()` is never called with `check=True` (`blob` :48-51 and `show` :54-57 both `check=False`), so upstream git failures are swallowed entirely; line 190 `open(a.sources).read()` raises uncaught `FileNotFoundError` → exit **1** + raw traceback (R3 T2). Show with: `python3 tools/release-recheck.py draft --sources /no/such.md --upstream <clone> …; echo $?` → 1. Fix: wrap `cmd_draft` in try/except mapping `OSError`/git failures to stderr `could-not-evaluate: …` and `return 2`.

**F2 MAJOR — `tools/release-recheck.py:48-57,167-175`: unresolvable pin/upstream emits plausible TODO rows with a false reason and `changed=0`, exit 0.**
Failed lookups return `-`/`[]` silently, so a pin commit missing upstream (T1) or a `--upstream` that is not a git repo (T3) produces `pin_blob=- release_blob=- changed=0 … TODO no cited line: pick the anchored section by reading`, exit 0 (R3). The docstring (:10-12) reserves TODO for "cannot relocate" / "no cited line" — an unreadable pin is neither, the note misdirects the reader, and `changed=0` is derived from two failed lookups; the counter in fact rejects any such row outright (`tools/round44-release-recheck-audit.py:195` "path absent at pin upstream"). Fix: verify `git cat-file -e <pin>^{commit}` (and the release commit) once in `cmd_draft` and exit 2, or emit a distinct reason ("pin commit unreadable upstream"); never report `changed=0` from double-failure.

**F3 MINOR — `tools/release-recheck.py` (`cmd_draft`, no validation): a nonexistent `--release-commit` exits 0 with rows indistinguishable from genuine drift.**
T1b (`--release-commit 1111…1111`): `release_blob=- changed=1 … TODO pin ranges 5-7 not found verbatim at the release: read and judge drifted/removed/holds`, exit 0 (R3). The counter validates the release commit (`round44-release-recheck-audit.py:266`); the drafter should too (one `cat-file -e`, exit 2), else a typo'd commit sends readers to judge "drift" that is operator error.

**F4 MINOR — `tools/round44-release-recheck-audit.py:279-295`: ledger rows for ids outside the population are silently ignored.**
Fixture: 3-row ledger vs 2-row population; the extra row was a false `removed` claim for a non-population id and the run finished `met=True` with no detail (R4 tail). The docstring's validity rule is per-population-row, so this is within the letter, but junk verdict rows cannot fail the counter and `rows=R` counts them. Fix: append a `detail:` note for non-population ids (symmetric to the duplicate handling at :285-287), or state the leniency in the docstring.

**F5 INFO — `tools/round44-release-recheck-audit.py:341,60`: output/doc mismatches.** The `tip=<sha>` line is printed but absent from the docstring's Output spec; `rows=R` is undefined (it is `len(ledger)` after parsing: unique ids, malformed lines excluded at :282).

**F6 INFO — `tools/round44-release-recheck-audit.py:229`:** `unchanged-file` accepts whitespace differences (`…replace(" ", "")…`), more lenient than the docstring's `release_lines == pin_lines`; harmless.

**F7 INFO — `tools/release-recheck.py:148,171-174,183`:** implemented beyond its own docstring: relocation candidates spanning > 80 lines are skipped (:148), and the weak-number fallback picks `min(weak)` while the note says "first" (:171-174,:183). Both conform to the ledger contract the counter documents; drafter docstring is silent. Doc-only.

## Verified conformant (counter — every docstring rule exercised)
- Population rule on the real BASE: pop=91 (R1). Blobs/changed re-derivation; ranges parse (< 80 lines, in-file, counts equal); ≥ 20 non-ws per pin range; STRONG/WEAK cited-line rule.
- All five verdicts positively and negatively: unchanged-file/holds/holds-reworded/drifted/removed → met=True exit 0 (R4 tip1, tipC, tipD, tipE, t9); false removed → "removed: pin text still present"; text-equal pair as holds-reworded → "holds-reworded rule"; wrong changed flag → "changed flag"; duplicate ids → invalid; malformed row → "bad ledger line", uncounted; header mismatch → rows=0, all unverified.
- Flags rule: missing in SOURCES section and/or knowledge file → flags_missing 2/1 with details; present → met=True (t7/t8/tip1).
- Exit codes: 0 met / 1 not met / 2 could-not-evaluate (missing upstream, bogus tip) all reachable and correct; "path absent at the release" ledgered `removed` validates end-to-end; duplicate ids, CRLF ledger (silently accepted via universal-newline translation in `show()`), and unknown/absent tip all behave as recorded in R4.
- Read-only on `--repo`/`--upstream`; no `/tmp` hardcoding anywhere (drafter honors `TMPDIR`, :204).

## Residual risks / gaps
- The counter cannot verify the reader-judgment clauses ("the statement still true") — inherent, consistent with its re-derivation philosophy, worth one docstring sentence.
- `--ids` on the drafter verified for one id (R3); multi-id parsing is the same `split(",")` path.
- No tooling was installed or upgraded; no pacman use.
- Scratch `/fast/scratch/hyaku/kama-r44/V1Code` removed after receipt copy; lane/fleet untouched (read-only git only).
