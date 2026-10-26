# Round 49 · seat X2SelftestPower — selftest power of `append-only-audit.py`

**Verdict: both round-49 cases fail on v3 and pass on the build, and of the four clauses named as uncovered only three are uncovered — `wildcard-named positive` is already exercised by `contract`/`vanished-and-paths`; five proposed cases close the three real gaps plus a fifth clause I found (multi-title origin), each killed by exactly its clause-reverting mutant and each red on v3.**

Axes: (A) v3-fails evidence, (B) clause-coverage census by mutation, (C) discriminating cases. Nothing else was touched: no counter run, no server started, no tool installed.

## Pins and method

| object | commit | sha256 of `tools/append-only-audit.py` |
|---|---|---|
| build (measured) | `74558c71c38ceaeace15fd4cf8aa9d84977584b1` | `3bae58a391bc7a859446c68e632d79b593cf6b286f3599c359899699427eb0ed` |
| v3 (round-48 closure) | `438127bc01ff3b99f98468549d58046f932490ef` | `0caf3c7e29579725a543450deeb4ac238565a9f9e519320065ee60d548074b59` |

Both blobs were extracted with `git -C <clone> show <commit>:tools/append-only-audit.py`; the lane worktree was **not** used as a source (see "Worktree drift"). Every run: `python3 <variant> --selftest --scratch $S/...` with `S=/fast/scratch/hyaku/kama-r49/X2SelftestPower`, `TMPDIR=$S`. Fixtures are created by the tool under `--scratch` and removed by it.

## A. The two frozen round-49 cases on v3 — both fail

Ported **verbatim** from the build blob into v3 (only the two `def` blocks and two registry entries; nothing else changed): `logs/00-port-into-v3.diff`, script `v3-ported.py`.

```
$ python3 $S/v3-ported.py --selftest --scratch $S/st-v3p     # logs/01-v3-two-frozen-cases.log
…
FAIL launder-through-head: [{'commit': 'bb0b47be…', 'file': 'score.md', 'deleted': 25, 'graded': 0,
  'ungraded': 25, 'restored_max': 0, 'status': 'ungraded'}]
FAIL binding-v4: [{'path': 'LOG.md', … 'ok': True}, {'path': 'score.md', … 'ok': True},
  {'path': 'notes/*.md', … 'ok': True}, {'path': 'LOG.md', …}]
AOA_SELFTEST pass=28 fail=2
exit=1
```

- `launder-through-head`: v3 grades 0 of 25 (the hatch: dated text parked in the exempt head at `438127bc:tools/append-only-audit.py:417` `if s in eligible:` — no origin test).
- `binding-v4`: v3 binds all four rows (expected `[False, False, False, True]`): `438127bc:tools/append-only-audit.py:199` `… or (bool(tok) and tok in low)` is substring-only, `438127bc:tools/append-only-audit.py:195` has no negation window.

## B. The two cases on the build — both pass

```
$ python3 $S/v4-74558c71.py --selftest --scratch $S/st-base    # logs/02-…: pass=30 fail=0, exit=0
```
`launder-through-head` and `binding-v4` are registry entries `74558c71:tools/append-only-audit.py:947`, bodies at `:910` and `:921`.

## C. Clause census — mutant reverts one clause, does the as-built suite notice?

`mutants.py` (one assert-guarded single-string mutation of the frozen blob per clause), full output `logs/06-mutants.log`.

| clause (frozen blob line) | mutant | as-built 30 cases | +5 proposed cases |
|---|---|---|---|
| wildcard row binds via token (`:216-240` + `row_token` `:202`) | `if wild: return False` | **caught** (`contract`, `vanished-and-paths`) | caught (+`wildcard-token-bound`) |
| origin None never exempt (`:475`) | `… or None in org.get(text)` | **survives 30/30** | caught (`origin-preamble-moved-under-head`) |
| negation window `{0,3}` (`:212`) | `{0,3}`→`{0,2}` | **survives 30/30** | caught (`negation-window-three-vs-four`) |
| `’` inside the window word class (`:212`) | `[\w'’]`→`[\w']` | **survives 30/30** | caught (`negation-curly-apostrophe`) |
| origin is a *set*, any exempt title (`:475`) — found, not on the brief | `and len(origin)==1` | **survives 30/30** | caught (`origin-multi-title`) |

Correction to the brief: **`wildcard-named positive` is not an uncovered clause.** `t_contract` (`:719`) declares `corpus/lessons/*.md` at `AGENTS.md:1` "lessons are append-only" and asserts `declarations[0]["ok"] is True`; disabling the wildcard token path breaks it. What the as-built suite does *not* do is distinguish the v4 word-bounded rule from v3's substring rule (`pass contract` in the v3 log) — `wildcard-token-bound` adds that side.

## D. Five proposed cases (`proposed-selftest-cases.diff`, 74 added lines)

`t_wildcard_token_bound` (positive `the logs directory is append-only` binds `corpus/logs/*.md`, `our catalogs are append-only` does not), `t_origin_preamble_moved_under_head` (preamble-born text moved under the head, head regrown 55≥50 so it is eligible, dropped there: `deleted=25 graded=25 ungraded=0`), `t_negation_window_three_vs_four` (`not yet considered strictly append-only` unbinds; `not yet really considered strictly append-only` binds), `t_negation_curly_apostrophe` (`not the round’s append-only log` unbinds), `t_origin_multi_title` (a line born under both the head and `## Round 1`, `threshold=1`, stays ungraded).

```
$ python3 $S/v4-newcases.py --selftest --scratch $S/st-new       # logs/03-…: pass=35 fail=0, exit=0
$ python3 $S/v3-newcases.py --selftest --scratch $S/st-v3new     # logs/04-…: pass=29 fail=5, exit=1
   FAIL wildcard-token-bound / origin-preamble-moved-under-head / negation-window-three-vs-four
   / negation-curly-apostrophe / negation-typographic-isnt
$ python3 $S/v4-worktree-newcases.py --selftest …                # logs/08-…: pass=35 fail=0 (no collision
   with the uncommitted K2Negation edit)
```

Every proposed case is killed by its mutant and passes on the build; `origin-multi-title` also passes on v3 (v3 preserves the exemption), so its only discriminator is the M5 mutant — stated so nobody mistakes it for a v3 regression check.

**Trap for whoever lands the diff:** each case must call `lines()` **once** and reuse the list. My first drafts called `lines("p", 25)`/`lines("h", 24)` twice; the two calls emit different random text, which turns the case into a relocation test and the failure reads like a tool bug (`graded=0 ungraded=25` on v4). Verified fix: bind the list to a local (`p = lines("p", 25)`, `head[2:]` for the module-level head).

## E. Defect: typographic apostrophes bypass the documented negation set

- `74558c71:tools/append-only-audit.py:141` `NEGATIONS = ("not append-only", …)` and `:212` `NEG_WINDOW` alternation `isn't|aren't` are ASCII-only, while the docstring at `:16` promises "isn't, aren't" as negations; `binds()` (`:216`) lowercases only (`:225`).
- Command: `python3 -c 'import importlib.util as u; s=u.spec_from_file_location("m","$S/v4-74558c71.py"); m=u.module_from_spec(s); s.loader.exec_module(m); print(m.binds("LOG.md isn’t append-only","LOG.md","NOTES.md"))'` → `True` (row binds although the line denies it). Same for `aren’t`.
- Case `t_negation_typographic_isnt` (`defect-case.diff`) is red on the build: `logs/05-v4-plus-defect-case.log` `pass=35 fail=1`.
- Proposed fix (either): normalize in `binds` — `low = text.lower().replace("\u2018", "'").replace("\u2019", "'")` — or extend the two spellings, which is what the uncommitted worktree edit does.
- **Already closed outside the measured commit**: `kama-shokunin/tools/append-only-audit.py` currently differs from `74558c71` (19 insertions, 6 deletions, `logs/07-worktree-drift.diff`) adding `cannot|can['’]t|isn['’]t|aren['’]t` and en/em dashes per "seat K2Negation F1". Probe on that file returns `False` for both lines, and `08-worktree-plus-cases.log` is 35/35. Reported because the measured build still binds them; not claimed as novel.

## F. Findings, risks, limits

1. **Worktree drift noticed mid-seat** (not mine, not written by me): `git -C kama-shokunin status` → `M tools/append-only-audit.py` while HEAD stayed `122c4ee9`; sha of the worktree file in `logs/07-worktree-sha256.txt`. All my results are against the `74558c71` blob.
2. Residual behaviour now **pinned** by `origin-multi-title` rather than silently allowed: a line whose first appearance is *simultaneously* in the exempt head and a dated section is ungraded forever (dup-at-birth laundering). The clause says "contains one of", so this is the declared rule, not a defect; if the lane wants it closed, the definition has to say "every origin title exempt".
3. Negation window limits (dashes only as separators, no trailing negations, `no edits append-only` read as a negation) are already documented in the uncommitted integration text; my `negation-window-three-vs-four` pins the boundary itself and would fail if the window widened to 4.
4. Not run, by scope: the two round-49 counters, any network fetch, any llama-server. `pgrep -af llama-server` shows only other seats' scratch trees; I started none. No packages installed. Scratch `$S` removed after copying.

## Artifacts (`…/round-49/w1/out/X2SelftestPower/`)

`reproduce.sh` (re-extracts both blobs, `cmp`s them against the copies, reruns 01–05), `proposed-selftest-cases.diff`, `defect-case.diff`, `v4-74558c71.py`, `v3.py`, `v4-newcases.py`, `v3-newcases.py`, `v4-newcases-defect.py`, `v4-worktree-newcases.py`, `v3-ported.py`, builders `build_variants.py`/`port_v3.py`/`mutants.py`, `logs/00…09` (00 port diff, 01 v3+2, 02 as-built, 03 +5, 04 v3+6, 05 defect red, 06 mutants, 07 drift, 08 worktree+5, 09 reproduce).

`$ .../X2SelftestPower/reproduce.sh <scratch>` reproduces: 30/30, 35/35, v3 28/2 and 29/5, and the red defect case.
