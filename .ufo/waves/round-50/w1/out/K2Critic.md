# K2Critic — round-50 attack on append-only-audit v5 origin semantics

VERDICT: v5 origin semantics is broken at merges — `origins()` unions keys over the FIRST PARENT ONLY (`parents[x]` keeps only `parts[1]`), so any line held only by a non-first parent is "re-born" at the merge under the merge blob's title; merge-laundering into an exempt section succeeds whenever the dated branch is not the first parent (observed f1a exit 0 vs spec exit 1, f4 octopus exit 0 vs spec exit 1) — plus a second, order-only channel: `window = commits[i:]` of `rev-list --topo-order` makes exempt-title eligibility and restoration measures depend on merge parent order (observed exit 0 vs exit 1 on identical abstract DAGs).

Tool audited: `tools/append-only-audit.py` at measured tip `97c864bead3ee4a2f629574e77263d33834ec98a` (file byte-identical to worktree copy, md5 320ee3dc…; run from a `git show` extract). Harness: `drive.py` (commit-tree fixtures under scratch, contract outside the repo, fixed GIT_AUTHOR_DATE/GIT_COMMITTER_DATE for determinism). git version 2.56.0. Raw tool JSON per fixture: `out/K2Critic/receipts/<fixture>.json`.

## Finding 1 (DEFECT, counter-exceedable): `origins()` sees only the first parent

`append-only-audit.py:465-470` — `parents[parts[0]] = parts[1]` stores only the FIRST parent hash; `:494-501` then computes `pkeys` from `(parents[x] or "").split()`. The v5 definition (counter docstring line 30; tool docstring line 15) says a birth is a commit whose blob holds k "while NO parent of it holds k". The counter's own reference (`round50-append-audit-v5-check.py:449-455`) unions `allpar[c]` = ALL parents. For merges the tool drops every parent but the first.

Consequence: at a merge M whose blob differs from the first parent's blob, every key the merge carries that the first parent lacks is registered as born AT M under M's `## ` title — even when a second/third parent already held the key (under a different, non-exempt title). That adds a bogus exempt title to `origin(l)`, and the carve-out at `:544` (`s in eligible and org.get(key(text)) & titles`) then ungrades lines the spec grades: merge-time laundering of dated lines into the exempt head.

Fixture f1a (receipt `receipts/f1a-p12.json`): base c1 (`## Axes` 5h, `## Round 1` 3r); branch cB adds 25 `d line i` under `## Round 1` (born there); sibling cA keeps the base SCORE blob; merge cM (parents `[cA, cB]`) places the d-lines under `## Axes`; cE rewrites Axes deleting 5h+25d.

- Hand expectation (v5 spec): d-lines are held by parent cB → not born at cM → origin `{## Round 1}` → cE deleted=30 graded=25 ungraded=5 status=unrestored, exit 1.
- Tool: `deleted=30 graded=0 ungraded=30 status=ungraded`, exit 0 — DISAGREE. The d-lines got a spurious `## Axes` birth at cM. Counter-style all-parents origin computed on the same repo: `origin(d line 0) = {## Round 1}` (see `counter_origins` run below), so `native = 5` and the tool's `ungraded 30 > native 5` — the lane-leg check `ungraded <= native` would flag this event were such a DAG in the audited history.
- f1b (same trees, parents swapped `[cB, cA]`): exit 1, `graded=25 ungraded=5` — spec-conformant. So the SAME abstract history flips exit 0↔1 purely on merge parent order, on top of Finding 2: an attacker (or an unlucky history) launders exempt-section rewrites by making the "dirty" branch the non-first parent.

Fixture f4 (octopus, receipt `receipts/f4-octopus.json`): three-parent merge `cM` (parents `[p1, p2, p3]`); `twin` held ONLY by p3 (born under `## Round 1`); merge blob moves `twin` under `## Axes`; cE deletes 24h+twin under Axes.

- Spec: origin `{## Round 1}` → deleted=25 graded=1 ungraded=24, exit 1.
- Tool: `deleted=25 graded=0 ungraded=25`, exit 0 — DISAGREE. Instrumented `origins()` shows `258882a7 births 1: (b'twin', '## Axes')`; counter-style origin: `{## Round 1}`.

Fixture f8 (file absent in first parent, receipt `receipts/f8-absentp1.json`): `SCORE.md` deleted on branch pA, held on pB (`twin` under R1); merge re-adds it with `twin` under `## Axes`. `pkeys` is empty (first parent has no blob) → every key "born" at cM under its titles: `twin` gets `## Axes`; cE ungraded=25 vs spec graded=1 ungraded=24 — DISAGREE (same root cause, distinct code path `bl.get(q) is None`).

Minimal fix (proposed, not applied — counters/tools are frozen; the loop must see all parents while the event diff keeps the first parent):

```diff
--- a/tools/append-only-audit.py
+++ b/tools/append-only-audit.py
@@ -465,7 +465,7 @@
-    commits, parents = [], {}
+    commits, parents, allpar = [], {}, {}
     for line in _text(repo_path, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
         parts = line.split()
         if parts:
             commits.append(parts[0])
             parents[parts[0]] = parts[1] if len(parts) > 1 else None
+            allpar[parts[0]] = parts[1:]
@@ -495,7 +495,7 @@
-            for q in (parents[x] or "").split():
+            for q in allpar[x]:
```

(`parents[c]` stays first-parent for `numstat`/`deleted_lines`/`psec`, per the v3 "diffs against the first parent" rule.) The same one-line-shaped fix applies to the counter's spec-checker only if it shared the bug — it does not (`allpar` at counter:418,449).

Coverage note for the counter: every merge in the 12 scenario fixtures holds the audited key in BOTH parents (order-a/order-b twin is born independently on both branches), the exact shape where first-parent-only union coincides with all-parents union; `pkeys is keys` also hides it. Nothing in the fixture leg exercises "key held only by a non-first parent" or a file absent from the first parent — f1/f4/f8 would each catch Finding 1 if adopted as scenarios (e.g. expect f1a exit 1).

## Finding 2 (order-dependence survives v5): `window = commits[i:]` is rev-list-order dependent

`append-only-audit.py:528` — `window = commits[i:]` over `rev-list --topo-order --reverse`; it feeds `eligible` (`:533-535`: exempt title eligible iff some window blob's section count ≥ parent's) and `restored_max`/`held_at_to` (`:549-551`). v5 made *origin* order-free but left the window as a listing slice, so eligibility and the restored measures still depend on which sibling lands "later" in the list — and in a diamond merge git emits the first parent's line before the second's. Observed empirically on git 2.56.0: in ALL four f6/f7 diamonds (equal dates, swapped dates, either way), `rev-list --topo-order` printed the second parent's commit first; dates did not override parent-list order.

Fixture f7a vs f7b — IDENTICAL abstract DAG (root c0; cE guts `## Axes` deleting its 24 lines; sibling cS regrows Axes to 30s lines; merge cT resolves to cE's gutted tree), only cT's parent order swapped (`[cE,cS]` vs `[cS,cE]`), all commit dates equal:

- f7a `rev-list --reverse`: `[c0, cE, cS, cT]` → `window(cE)` contains cS (31 Axes lines) → `## Axes` eligible → cE event `deleted=24 graded=0 ungraded=24`, exit 0 (receipt `f7a-eq-ES.json`).
- f7b `rev-list --reverse`: `[c0, cS, cE, cT]` → cS precedes cE → `window(cE)` lacks it → cE `deleted=24 graded=24 status=unrestored`, plus a cT event (30s deleted vs first parent cS, graded), exit 1 (receipt `f7b-eq-SE.json`).

So "the same verdict under either merge-parent order" (C2 predicate) fails even for a fully spec-conformant origins fix: an identical abstract history exits 0 or 1 on parent order alone — both through the new event-set asymmetry (first-parent diff) and, independently, through `window` membership. f7c/f7d (parents fixed `[cE,cS]`, dates varied both ways) show the same listing `[c0, cE, cS, cT]`, confirming the tie-break is parent-order, not dates — and even where dates do order a listing, `window` still varies with them. Structural consequence: an event on a FIRST-parent line always sees all merged sibling lines in its window; an event on a non-first line never sees the first-parent line. This is a spec-layer carry-over of the F3 class the round set out to kill; whether the canonical judge treats it as a defect or a v3-frozen tradeoff is above my seat — I report the observed order-only verdict flip.

## Assigned probes — agree/disagree per case

| Probe | Hand expectation | Tool result | Verdict |
|---|---|---|---|
| (1) multi-birth: twinA Axes→(deleted)→reborn R1; twinB R1→reborn Axes; deleted under Axes (f2) | union origin → both exempt → ungraded=25 exit 0 (single-birth rules give 24) | `deleted=25 graded=0 ungraded=25` exit 0 | AGREE — union over all births confirmed |
| (2) merge, both parents same blob, key held by both; merge blob re-titles it (f3) | `pkeys is keys` skip → no birth at merge → twin origin `{R1}` → graded=1 | `deleted=25 graded=1 ungraded=24` exit 1 | AGREE — also verified equal-blob commits skipped wholesale |
| (3) three-parent merge, key only in parent 3 (f4) | spec: not a birth → graded=1 ungraded=24 | `ungraded=25` exit 0 | DISAGREE — Finding 1 |
| merge, key only in parent 2, merge re-titles (f1a/f1b) | spec: graded both orders | f1a exit 0 ungraded=30; f1b exit 1 | DISAGREE in order (cA,cB) — Finding 1 |
| file absent in first parent, held in second (f8) | spec: twin graded | `ungraded=25` exit 0 | DISAGREE — Finding 1 |
| (4) CRLF: `x` born under R1 LF, moved under Axes CRLF, deleted as `x\r` (f5) | `key(x\r)=x` in pkeys → not born at move; origin `{R1}` → graded=1 | `deleted=25 graded=1 ungraded=24` exit 1 | AGREE — birth is keyed right; deleted raw bytes keyed before lookup |
| (5) order-independence: order-a/order-b twin-in-both-parents, equal dates, swapped parents (f6a/f6b) | same verdict both; rev-list sibling order should flip | rev-list flipped `[c1,cA,cB,…]` vs `[c1,cB,cA,…]`; tool `ungraded=25` exit 0 BOTH | AGREE — origin union is order-free here |
| (5b) window channel: same abstract DAG, swapped merge parents (f7a/f7b) | predicate: same verdict | exit 0 vs exit 1 | DISAGREE — Finding 2 |

Reproduce (any scratch dir): `python3 drive.py` after placing `tool-at-tip.py` beside it (`git -C <lane> show 97c864be…:tools/append-only-audit.py > tool-at-tip.py`); contracts are written next to the fixtures, outside each fixture repo. Every fixture asserts `git rev-parse --show-toplevel` equals its own dir before the first `commit-tree`.

## Cross-checks performed

- Counter-style (all-parents) `origins()` recomputed on f1a/f4/f8 repos: `d line 0`/`twin` origins = `{## Round 1}` — the tool's first-parent-only union is the sole divergence; with the fix all observed tool/spec disagreements vanish.
- `pkeys is keys` skip audited for corner cases: root commits still birth everything (parents empty → `pkeys=set()` never `is` the non-empty keys); equal-blob parent present anywhere in the parent list correctly suppresses births; scan-on-inequality degrades to the same verdict the fast path gives.
- No hunk/numstat mismatch, no crash, `graded+ungraded==deleted` in every event of all 13 runs; `bad_declarations=0`, `unmatched=0`, `vanished=0` everywhere.
- f1b's expected extra merge event (25 d-lines moved) did not materialize — `git diff -U0` merges the relocation into a small hunk under the 20-line threshold; consistent, not a defect.

## Evidence files

- `out/K2Critic/drive.py` — fixture builder/runner (commit-tree plumbing; all mutations confined to `fx/<name>` with toplevel assertion).
- `out/K2Critic/receipts/*.json` — raw `--json` tool output + exit code per fixture.
- Key lines: tool `tools/append-only-audit.py:466-470` (first-parent-only `parents` map), `:494-501` (`pkeys` loop), `:528` (`window = commits[i:]`), `:537-545` (origin carve-out); counter `tools/round50-append-audit-v5-check.py:418,449-455` (the all-parents reference the tool must match).

Tooling: no installs or upgrades were needed (python3 + git 2.56.0 only).
