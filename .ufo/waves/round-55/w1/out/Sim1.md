# Sim1 — dead-weight review of the two frozen round-55 counters (findings only)

**Verdict: one calibration-relevant docstring/code gap (the `superseded` class checks only that the token was *cited* at base, not that it resolved there, so it can absorb a `fixed` correction and skip the M15 stem/line binding) plus nine further dead-weight items (eight LOW, one INFO): a stale scenario count, a coverage overclaim, a dead parameter, an unreachable sentinel, a dead store, one duplicated parser, one inert constant element, one docstring vector that belongs to the other counter, and one pre-existing docstring gap. No unused constant and no unreferenced function in either file, and no lane file was edited.**

Files reviewed (byte-identical to the lane tip, so the review target is exactly the frozen counter):

```
$ sha256sum tools/round54-replay-code-audit.py tools/round54-cited-path-check.py
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  tools/round54-replay-code-audit.py
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  tools/round54-cited-path-check.py
$ git -C <lane> show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-replay-code-audit.py | sha256sum
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  -
$ git -C <lane> show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-cited-path-check.py | sha256sum
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  -
$ python3 -c "compile(...)  # both files"   # compile-ok, exit 0
```

All line numbers below are the frozen files as committed at `9c60eae`; the counters were never edited in place.

---

## F1 — MEDIUM (calibration): `superseded` docstring claims "resolved there"; code only checks "cited there"

- Docstring, `tools/round54-cited-path-check.py:96-99`: "…the original token was cited in that surface at `--base` **and resolved there** (unlike `fixed`, which corrects an UNRESOLVED citation…)".
- Inline comment, same file `:466-467`: "…it WAS cited at base (unlike `fixed`, whose token was unresolved at base)…".
- Code, same file `:477-479`: `superseded` only tests `tok not in (base_citelines.get(surf) or {})` — `base_citelines` is built by `citation_lines()` (`:289-294`), which records *all* citations, resolved or not. There is no `base_unres` test (unlike `fixed` at `:428`).

Consequence: a token that was an **unresolved** base citation can be rowed `superseded`, which skips `fixed`'s stem-extension and same-base-line binding (`:414-442`, the M15 gate) yet is still exempt from `dropped`/`stale` (`:637-656`). The two classes are indistinguishable for that input.

Evidence — the frozen counter accepts exactly the row its docstring says belongs to `fixed` (`repro-superseded-unresolved-base.out`, produced by `repro-superseded-unresolved-base.sh`, which copies the frozen counter into scratch, builds a two-commit fixture in scratch, and calls the frozen `evaluate`):

```
base unresolved: {'tools/nope.py': [('tools/nope.py', 'missing')]}
evaluate met: True {'cited': 1, 'unresolved': 0, 'disclosed': 0, 'undisclosed': 0, 'bad': 0, 'stale': 0, 'dropped': 0}
```

The lane's own row is *not* affected: `registry/cited-path-corrections.tsv:46` rows `SCORECARD.md | corpus/lessons/round-52-verifier-spotcheck.md | superseded | corpus/lessons/round-53-verifier-spotcheck.md`, and at BASE `0b75a84c` the token is cited at `SCORECARD.md:18` **and resolves** (checked with the frozen module's own `survey`/`citation_lines` on a `git clone --shared` of the lane):

```
BASE tree has token: True
BASE surface cites token at lines: {18}
token unresolved at BASE: False
```

Proposed fixes (both in `alt-enforce-superseded-resolved.diff`; frozen, therefore a report not an edit):
1. Enforcement for the next freeze: two lines after `:478` —
   `if tok in base_unres.get(surf, set()): return "superseded token was an unresolved citation at the base; that is a `fixed` correction, not a re-point"`.
   Validated: the lane at `9c60eae` still prints the identical verdict line (`met=True … dropped=0`, exit 0, `alt-run.out`), and the synthetic row above now yields `met=False bad=1` (`alt-rejects-unresolved-base-row.out`).
2. Doc-only alignment (included in `fix-c2-docs-and-dead-code.diff`): drop "and resolved there" and state that the class checks citation only.

## F2 — LOW (stale doc after the round-55 delta): "plus six" is now seven bullets

`tools/round54-cited-path-check.py:109-121` says "fifteen constructed scenarios … the round-53 eight (…) **plus six:**" but the list that follows has **seven** items (M10; M11 bytes; M11/M12 contrast; M13; M15; honest `fixed`; `superseded`), and `SCENARIOS = 15` (`:168`) with the `cases` literal holding 15 entries (AST count; frozen run prints `scenarios=15/15`). Round 54's "fourteen … plus six" was updated to "fifteen" but the "six" was not. Fix in `fix-c2-docs-and-dead-code.diff` (`plus six:` → `plus seven:`).

## F3 — LOW (docstring overclaims fixture coverage): the `superseded` scenario exercises only one of its two rejection modes

`tools/round54-cited-path-check.py:119-121` promises "a `superseded` row whose token is still cited, **or** whose replacement is not cited at tip, is bad". The fixture (`:778-796`) only builds the second: the forged tip text is `closure re-pointed away in prose`, so neither `tools/live.py` (token) nor `tools/new.py` (replacement) is cited. Instrumenting the frozen `check_row` on a scratch copy and running the frozen fixture shows the two calls:

```
SUPERSEDED row token='tools/live.py' ev='tools/new.py' -> None
SUPERSEDED row token='tools/live.py' ev='tools/new.py' -> "replacement 'tools/new.py' is not cited in SCORECARD.md at tip"
fixture scenarios passed: 15 / 15
```

So three rejection exits of the branch are unexercised: `:471` ("still cited at tip"), `:475` ("does not resolve at tip"), `:478` ("not cited at base"). Fold a third/fourth tip into the same scenario (keeps `SCENARIOS = 15`); not proposed as a frozen edit. Evidence: `superseded-branch-coverage.out`.

## F4 — LOW (dead parameter): `survey(..., base_unres=None, ...)` is never read

`tools/round54-cited-path-check.py:585`. Body (`:586-610`) never loads `base_unres`; neither caller passes it (`:612` `survey(base_lane, fleet)`, `:634` `survey(lane, fleet, detail=detail)`). AST scan over both files reports exactly one unused parameter, this one:

```
UNUSED-PARAM survey(base_unres) line 585
```

Removal is behavior-identical (shown in `fix-c2-docs-and-dead-code.diff`; patched copy reproduces the frozen output byte-for-byte, `fixed-run.out` vs `c2-frozen-run.out`, `diff` exit 0).

## F5 — LOW (unreachable code): `return "unreachable"`

`tools/round54-cited-path-check.py:582`. `CLASSES` has nine members (`:167`); every one is branched before the `if not bad_exp` early return or after it, and each branch returns: `fixed :411`, `externalized :444`, `superseded :461`, `deleted :482`, `never :494`, `moved :501`, `eof :515`, `upstream :529`, `untracked :574` — so `:582` cannot be reached while `CLASSES` is unchanged. Do **not** simply delete it: if it ever were reached it currently marks the row `bad`, which is fail-safe; deletion would make `check_row` fall off the end (`None` = good row). Keep it as a documented sentinel (comment-only change in `fix-c2-docs-and-dead-code.diff`), or replace with `raise EvalError(...)` in a future freeze.

## F6 — LOW (dead store): `got = 0` at `:681` is overwritten before any read

`tools/round54-cited-path-check.py:681` (`got = 0` before `try:`), reassigned at `:731` before `cases = [`; the intervening body only defines helpers and commits, and the only read is `return got` after the `try/finally` (an exception in the `try` propagates, so the first value is never observed). Removed in `fix-c2-docs-and-dead-code.diff`; output unchanged (see F4's run).

## F7 — LOW (duplicated helper): the citation-span parser exists twice

`tools/round54-cited-path-check.py:270-286` (`citations_line`) duplicates the span→`(tok, core, lo, hi)` parsing at `:324-338` (inside `citations`), 15 lines identical except the fence scan. Proposed extraction of a shared `_spans(line)` generator used by both (in `fix-c2-docs-and-dead-code.diff`). Behavior is preserved exactly — including `stated_digests`' deliberate fence-blindness (`:251-267` calls `citations_line`, not `citations`) — and the patched copy reproduces the frozen output on the lane tip (`fixed-run.out`, diff exit 0). `citation_lines` (`:289-294`) is not duplicated; it wraps `citations`, which is why it must keep using it after the extraction (the diff does).

## F8 — LOW (inert constant element): `KERNEL_MAPS` entry `"[vvar_boot"`

`tools/round54-replay-code-audit.py:144` includes `"[vvar_boot"`, but the admission test is exact membership (`:503` `if name in KERNEL_MAPS`), and `name` is the complete bracketed token from a maps row (`:502`). No row can equal a truncated prefix: this host's maps expose whole bracketed names only (`grep -ho '\[[^]]*\]' /proc/self/maps | sort -u` → `[vdso] [vsyscall] [vvar] [vvar_vclock]`, plus `[heap] [stack] [anon:…]`), never a `[vvar_boot` token. The entry is dead as written; removal (`fix-c1-docs-and-dead-code.diff`) cannot change a verdict, and `fixed-c1.py` still reports `KERNEL_MAPS` length 5, `HOST_LIBS` 13, `RECEIPTS` 3, and a green `newrow` leg (`| S511 |`, `fixed-c1-validation.out`). If a prefix was intended, that would be a comparison change, not a cleanup — not proposed.

## F9 — LOW (docstring vector belongs to the other counter): `core.hooksPath` in the C1 `clean_env` docstring

`tools/round54-replay-code-audit.py:163-169` says GIT_CONFIG_COUNT "…would redirect the read, not only writes" with `core.hooksPath` as the example. This counter's only git subcommands are `show` (`:865`), `rev-parse` (`:891`) and `archive` (`:892`); none runs a hook, so the Sen4Fixture hooksPath mechanism applies to the C2 fixture's commits, not here. Stripping is still correct (GIT_DIR and injected config keys can change what these reads return). Reworded in `fix-c1-docs-and-dead-code.diff`; doc-only.

## F10 — INFO (pre-existing, not a round-55 delta): two other docstring/behaviour gaps in the same file

- `externalized` docstring says the token "was unresolved at `--base`" (`:91-94`), but the branch (`:444-460`) never consults base state — `base_unres`/`base_citelines` are unused there. Since `externalized` is exempt from `dropped`, a live base citation can be classed `externalized` as well as `superseded`.
- The `fixed` paragraph (`:85-90`) does not disclose the inherited-row exemption implemented at `:413` and commented at `:406-407` ("an append-only ledger's inherited rows were verified when introduced"), which skips the base-citation and same-line checks.

Both predate round 55; recorded because `superseded` was modeled on them and because F1's fix should settle the base-resolution question for all three classes at once. No diff.

---

## Checked and clean (so the next reviewer need not redo it)

- **Module-level constants:** none unused in either file (AST scan: every module-level `Assign` name is loaded; `HOST_LIBS` 13 / `RECEIPTS` 3 / `UPSTREAM_INVENTORY` 4 / `UPSTREAM_DIGESTS` 4 / `SCENARIOS` 15 / `CLASSES` 9 all match their docstring counts except the `plus six` wording of F2).
- **Functions:** none unreferenced in either file (AST scan including attribute calls; `Repo.hist`/`Repo.nlines` are method-only and used).
- **Imports:** none unused (`__future__.annotations` is a compiler directive, not a use).
- **Dead literal branches:** none (`if False`/`if 0` scan).
- **Duplicated helpers across the two files:** `clean_env` and `git` are byte-identical bodies (declared fine for `clean_env`; `git` is the same and likewise harmless). `citations_line`/`citations` duplication within C2 is F7; no other duplicated helper.
- **Frozen predicates:** both files' `PREDICATE` sentences match `preregistration.json` claims (`C2.predicate`, including "fifteen constructed scenarios"), so the C2 `plus six` is prose-only drift, not predicate drift.
- **S501/S511 provenance:** `corpus/SOURCES.md` S510 is git(1) env vars (GIT_DIR, and it also names GIT_CONFIG_COUNT) and S511 is git-config(1) GIT_CONFIG_COUNT; the C1 docstring's split ("S511 … (S510 names GIT_DIR)") and `GITDOC_URL` match the rows.

## Retained behavior / narrow checks run

- Frozen C2 counter on a `git clone --shared` of the lane at the measured commit: `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`, exit 0, 1.39 s (`c2-frozen-run.out`). So all findings above are latent/dormant, not a live false pass at this tip.
- The doc/dead-code patch reproduces that output byte-for-byte (`fixed-run.out`; `diff` exit 0).
- The enforcement patch keeps the lane green with identical counts (`alt-run.out`, exit 0) and rejects F1's synthetic row (`alt-rejects-unresolved-base-row.out`).
- C1 was **not** run end-to-end by this seat (it starts `llama-server` on loopback and downloads ~30 MB + a model per replay); its two findings are a docstring and an inert tuple element, and the only behaviour-adjacent function touched by the patch suite (`newrow_leg`) was exercised on the clone (`newrow ok= True`, row `| S511 |`). No `llama-server` was started by this seat, so no teardown was needed; `pgrep -af llama-server` before finishing shows only a peer's two processes under `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/` (pids 3521908, 3523374), left untouched.

## Method

- `ast` scan for unused constants, unused function parameters, unreferenced functions, post-terminal statements and dead literal branches; frozen compiled with `compile()` (no bytecode written into the lane).
- All fixture repositories and copies lived under `/fast/scratch/hyaku/kama-r55/w1/Sim1/`; the single `git clone --shared` was read-only usage; every fixture commit named `-C "$D"` after `rev-parse --show-toplevel` matched; scratch removed before yielding.
- No tool installs or upgrades were needed; no `pacman` transaction was made.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/fix-c2-docs-and-dead-code.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/fix-c1-docs-and-dead-code.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/alt-enforce-superseded-resolved.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/repro-superseded-unresolved-base.sh`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/repro-superseded-unresolved-base.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/superseded-branch-coverage.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/c2-frozen-run.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/fixed-run.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/alt-run.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/alt-rejects-unresolved-base-row.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim1/fixed-c1-validation.out`
