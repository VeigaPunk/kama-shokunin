# J10Drop — round 53 ablation control C2 (correct by deleting)

**Verdict:** the frozen C2 counter is correct for the ablation it was assigned (deleting SCORECARD line 491 plus its
ledger row is caught: `dropped=1 met=False`, exit 1), but the same move on SKILL.md is **not** caught
(`met=True`, exit 0): the `dropped` leg is scoped to `SCORECARD.md` only and to distinct tokens, so deleting a
citation from either non-append-only surface — or deleting one of several occurrences of a SCORECARD token, or
fencing it — is scored as a satisfied claim. The build itself already contains one such undeclared deletion
(`SKILL.md` `scripts/local-helper.mjs`, base 113 → build 113) that the frozen counter reports as `met=True`.
A revised dropped leg (`proposed-c2-drop-leg.patch`, validated below) catches all five ablation trees while
keeping the build green once one declared `external` row is added.

## Setup (environment, no writes outside out dir and scratch)

```
S=/fast/scratch/hyaku/kama-r53/J10Drop; mkdir -p "$S"; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane      # 2026-10-27
git -C $S/lane rev-parse --show-toplevel   -> /fast/scratch/hyaku/kama-r53/J10Drop/lane
```
No tool installs, no pacman, no services started by me (`pgrep -af llama-server` shows only K2Design's hold server
on 127.0.0.1:35203, another seat's; nothing of mine, so nothing to tear down). Every fixture commit was made with
`git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit` after `[ "$(git -C $S/lane rev-parse --show-toplevel)" = "$S/lane" ]`
printed `toplevel-ok`. The lane itself was never written: my only mutations are the six fixture commits below.

## Baseline (my own run, reproduces the L1 receipt `measured/c2-build.out`)

```
$ python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 \
      --scratch $S/runBase --out $S/runBase/c2-build.repro.out
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
exit=0
```
=> `c2-build.repro.out` (identical legs to the L1's `c2-build.out`; only `fleet=` HEAD hash differs).

## The five measured ablations (frozen counter, unmodified)

| # | tree delta vs build `c22602bd` | fixture commit | legs | exit |
|---|---|---|---|---|
| A | SCORECARD.md: line 491 (`Use absent \`.ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py\``) removed **and** its `never` ledger row removed | `278c80cc9dccf3e7d7d16212cd7da6eea907202c` | `cited=681 unresolved=13 disclosed=13 undisclosed=0 bad=0 stale=0 **dropped=1** met=False` | **1** |
| B | SKILL.md: line 1245 (`- \`tools/server/server-common.cpp\` — SHA-256 …`) removed **and** its `upstream` row removed | `75ee1c93b3842ef3437eae4387ed7fe8d40b906f` | `cited=681 unresolved=13 disclosed=13 undisclosed=0 bad=0 stale=0 dropped=0 **met=True**` | **0** |
| B2 | same SKILL.md deletion, ledger row **kept** (discriminating control for B) | `55a70b8c8d1077a93cf579100e0ea812d080db4a` | `undisclosed=0 **stale=1** dropped=0 met=False` | 1 |
| C | SCORECARD.md: `## Saturation` paragraph (line 137, 578 chars, cites `tools/round42-selfdesc-reconcile.py`, 14 occurrences of that token) removed; token still cited elsewhere | `1816af4aa8b5244f415a5b55566b44490d6a662d` | `cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 **dropped=0 met=True**` | **0** |
| D | SKILL.md: line 1245 kept verbatim but wrapped in a ```` ``` ```` fence ("kept verbatim as history"), row removed | `6eceaaf503cc0530c146366b7629de736c048dc1` | `cited=681 unresolved=13 undisclosed=0 bad=0 stale=0 dropped=0 **met=True**` | **0** |

Commands (identical form for each, receipts in this directory):

```
$ python3 tools/round53-cited-path-check.py --repo $S/lane --tip <commit> --scratch $S/run<X> --out $S/run<X>/c2-abl-<x>.out
```
`c2-abl-a.out`, `c2-abl-b.out`, `c2-abl-b2.out`, `c2-abl-c.out`, `c2-abl-d.out`.

### A answers the assigned ablation (correct by deleting, SCORECARD)
Diff of the fixture commit: `SCORECARD.md | 1 -` and `registry/cited-path-corrections.tsv | 1 -`. The `dropped`
leg fires once and `met=False`. Mechanism: `tools/round53-cited-path-check.py:363-369` compares the **set of
tokens** cited in `SCORECARD.md` at `BASE` with the set at `--tip`; the removed token is unique to line 491, so it
disappears from the tip set. Removing the row too leaves nothing stale (`stale` leg, line 354, only fires for rows
whose token is still cited but resolves) — with the row kept, A would have been `stale=1` as well, so the *ledger
row* is not what protects A; the token-set leg is.

### B answers the SKILL.md question: **yes, the counter allows it, and it is a loophole**
- SKILL.md is not append-only (the ledger header itself says so: `registry/cited-path-corrections.tsv:9-11`), so
  deleting the line is a legal edit; the counter then has nothing to resolve, nothing undisclosed, nothing stale
  (row also deleted), and `dropped` is computed only for `SCORECARD.md` (`:365-366` hard-codes the file name).
  Result `met=True`, exit 0: a *deleted* claim is scored exactly like a *corrected* one.
- B2 shows the only guard on that surface is the surviving ledger row, and the row is itself a file the same
  author edits: delete both and the act is free (B). The `fixed` class cannot help either — it requires the
  replacement to be cited at tip, so an author who wants a miss gone can simply remove the citation instead.
- D shows the second free channel: the fence. `citations()` (`:151`) treats any line inside a fence as
  non-citation and the docstring blesses that ("the restored blocks of round 52 are fenced, so history kept
  verbatim is not a standing citation"), but nothing verifies the fence existed at `BASE` or that the fenced text
  is the same claim — a one-round "history" fence is a deletion the counter reports as `met=True`.
- C shows the SCORECARD guard is token-level, not occurrence-level: `dropped` is a set difference, so deleting an
  occurrence of a token cited more than once is invisible. At the build, 471 distinct SCORECARD tokens cover 808
  occurrences: 355 tokens are cited once (deleting them is caught), 116 tokens are cited more than once (453
  occurrences, of which up to 337 can be removed one at a time without any leg moving). C removes a substantive
  578-char paragraph and the counter prints `met=True`.

Exposure at the build (own count with the frozen parser): SCORECARD.md 808 occurrences / 471 tokens (355 unique),
SHONEN.md 11 / 9, SKILL.md 263 / 202. Of 1082 citation occurrences, 355 (32.8%) are protected against deletion in
full, 274 (SHONEN + SKILL) are deletable at will, and 337 are deletable partially — i.e. the predicate's "no
SCORECARD.md citation dropped since the base" leg covers at most a third of the citation surface, and the two
surfaces the round-53 claim edits in place are the uncovered ones.

### The hole is present in the build, not only in my fixtures
Occurrence-level base→build comparison with the frozen parser: SCORECARD 800→808 (no token loses an occurrence),
SHONEN 11→11, SKILL.md 264→263 — `scripts/local-helper.mjs` (base SKILL.md:113, a fleet-root citation that never
resolved) is gone at the build with **no row** (the ledger header, `registry/cited-path-corrections.tsv:9-11`,
says so on purpose: "an absolute path is not a lane citation"), and `tests/report-audit/…` is excused by its
`fixed` row. So `met=True` at `c22602bd` already rests on one undeclared citation removal.

## Proposed fix (round-54 instrument revision; not applied to the frozen round-53 counter)

`proposed-c2-drop-leg.patch` (unified diff against `tools/round53-cited-path-check.py`, 94 lines) does three things:

1. `dropped` is computed for **all three surfaces** and over **occurrences**, not token sets (`Counter` of
   citations at base vs tip; a token losing k occurrences contributes k), so SKILL.md, SHONEN.md and partial
   SCORECARD deletions move the leg.
2. A drop is excused only by a row the counter re-derives: the existing `fixed`, plus `external <absolute path>`
   (the cited text moved to another checkout; the path must exist on disk) and `withdrawn <token>` (the claim is
   restated by a token cited and resolving at tip). `upstream`/`deleted`/`never`/`moved`/`eof`/`untracked` stay
   what they are — disclosures of a *present* miss — so a surviving row for a removed citation is still `stale`.
3. Rows of the three removal classes are excluded from the `stale` and `disclosed` bookkeeping.

Validation of the proposed counter on the same trees (receipts `c2-proposed-*.out`, run from a scratch copy at
`$S/c2proposed.py`, never from the lane):

| tree | legs | exit |
|---|---|---|
| build `c22602bd` | `dropped=1 met=False` — `SKILL.md` `scripts/local-helper.mjs` (the undeclared build removal) | 1 |
| build + one `external` row (`4a2df8c0…`: `SKILL.md\tscripts/local-helper.mjs\texternal\t~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`) | `fixture=1 lane=1 dropped=0 met=True` | 0 |
| A `278c80cc…` | `dropped=2` (round-14 token + line-113) `met=False` | 1 |
| B `75ee1c93…` | `dropped=2` (`server-common.cpp` + line-113) `met=False` | 1 |
| B2 `55a70b8c…` | `stale=1 dropped=2 met=False` | 1 |
| C `1816af4a…` | `dropped=2` (incl. `tools/round42-selfdesc-reconcile.py` x1) `met=False` | 1 |
| D `6eceaaf5…` | `dropped=2` (fenced line counted as removed) `met=False` | 1 |

So with the patch, "correct by deleting" fails on every surface and on occurrence granularity, and the build stays
`met=True` once its one undeclared removal is declared (the row text is in the `4a2df8c0…` commit; the evidence
path exists: `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`, 15065 bytes).

## Risks and limits of my own measurements
- `external` is host-dependent (it checks a path outside both trees on this host); a fleet-wide counter would need
  a URL or a committed copy instead. Stated as a limit, not solved here.
- C and D delete substantive text from a *fixture* clone only; they are evidence about the counter, not proposed
  lane edits.
- The lane's working tree at the time of my run showed 34 modified paths (e.g. `SKILL.md`,
  `.ufo/waves/round-53/measured/c2-build.out`) from the in-flight L1 integration; I read only committed revisions
  (`c22602bd`, `4229ea1b`) and wrote nothing there.
- Limits of the frozen counter that this seat did not change and that remain true after the patch: a citation is
  only checked to exist (not to say what the citing sentence claims, not that an anchor points at the right line),
  and `LOG.md`/lessons/`corpus/README.md` citations stay out of scope — a dead claim can still be relocated to
  `LOG.md` instead of being corrected.

## Files
Written: this report, `c2-build.repro.out`, `c2-abl-{a,b,b2,c,d}.out`, `c2-proposed-{build,build+row,A,B,B2,C,D}.out`,
`proposed-c2-drop-leg.patch` — all under `.ufo/waves/round-53/w1/out/J10Drop/`. Scratch `$S` removed after copying;
no receipt here cites a `/tmp` path.
