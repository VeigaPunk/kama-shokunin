# Proposed fixture extensions for the three survivor coverage gaps (M2C2Mut)

Proposals only — the frozen counter was NOT modified anywhere. All diffs are against
`tools/round54-cited-path-check.py` at 9c60eae6f7ed84f7da93d219a406aadc30958c6c.

## Fix A — kill m01 (superseded still-cited) inside the built-in fixture

Scenario 15's forged tip currently re-points in prose (token NOT cited at tip), so the
forged half exercises only the replacement-cited clause. Making the forged tip ALSO cite
the old token exercises still-cited; the existing `(not ok2) and c2["bad"] == 1` guard in
`hit` then fails under m01 at any tip, with no change to honest behavior.

```diff
--- a/tools/round54-cited-path-check.py
+++ b/tools/round54-cited-path-check.py
@@
-                lane2 = at("closure re-pointed away in prose\n",
+                lane2 = at("closure now `tools/live.py` and `tools/new.py`\n",
                            "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\t\n")
```

(Unmutated: still-cited fires → ok2 False, c2["bad"]==1 → scenario 15 still passes.
Under m01: why=None → ok2 True → hit False → fixture=0 → met=False. The honest half of
scenario 15 is a separate evaluate call and is unaffected.)

## Fix B — kill m04 (superseded base-cited): row whose token was never cited at base

```diff
--- a/tools/round54-cited-path-check.py
+++ b/tools/round54-cited-path-check.py
@@
             ("superseded re-pointed citation discloses, forged superseded is bad",
              None, None, "superseded", lambda ok, c: ok),
+            ("superseded row for a token never cited at base is bad",
+             "see `tools/new.py`\n",
+             "SCORECARD.md\ttools/nope.py\tsuperseded\ttools/new.py\t\n",
+             None, lambda ok, c: not ok and c["bad"] == 1),
```

Here the base surface cites nothing (`None` ledger-less base from `at()`'s base-less
shape is insufficient — the scenario must build a `scen_base` whose surface lacks the
token; the construction mirrors the superseded branch: base cites only an unrelated
path, tip cites `tools/new.py` and rows the never-cited `tools/nope.py` as superseded).
Unmutated: `base_citelines` lacks the token → bad=1; m04 → all clauses pass → met=True.

## Fix C — kill m03 (superseded replacement-resolves): replacement cited but not resolving

Three-row tree in one surface: base cites `corpus/x.md:3`; tip cites
`corpus/x.md:99` (beyond EOF, disclosed by its own `eof` row anchored at a commit where
the file had ≥99 lines) plus `tools/new.py`, and rows `corpus/x.md:3` superseded →
`corpus/x.md:99`. Unmutated: replacement-cited passes, replacement-resolves fires →
bad=1; m03 → met=True (undisclosed already covered by the eof row, dropped=0 because the
token is exempt). The scenario needs the same two-commit construction the superseded
branch already builds, plus one `w("corpus/x.md", …)` commit for the eof evidence.

## Non-fix notes

- m08 (clean_env): the load-bearing oracle is an environment attack, not a tree state —
  the counter's own contract already documents it (Sen4Fixture); a fixture scenario
  cannot reach `clean_env` because `fixture()` builds its env through the same function.
  The honest demonstration is the r18/r19 pair in `runs/`.
- m09 (served-bytes compare): reachable only via an upstream that rewrites bytes at the
  frozen pin; a fixture would need to intercept `fetch()`. Recorded as a documented
  limit, consistent with the preregistration's C2 limits sentence.
