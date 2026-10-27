# K4Sizing — round-55 C2 claim-sizing audit and superseded-row attack

Verdict: C2's round-55 target is correctly sized — unreachable by a do-nothing control (pre-freeze catch re-derived) and reachable in one round (build measurement reproduced); the `superseded` ledger row is accurate and the flagged drop is genuinely the round-52→round-53 re-point — but the frozen counter's `superseded` branch under-enforces its own contract (cited-at-base, not resolved-at-base), a fixable latent defect that does not affect round-55's verdicts.

Scope: C2 (`tools/round54-cited-path-check.py`) per seat spec. C1's claim-sizing rests on its own frozen base control and kill battery (not re-run here; its counter spawns llama-servers).

## 1. Frozen-counter integrity

```
$ sha256sum lane/tools/round54-cited-path-check.py
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c
```
equals preregistration `claims.C2.counter_sha256`. All runs below used a `--shared` clone of the lane; fixture upstream rows fetched normally.

## 2. Do-nothing catch re-derived (BASE patch experiment)

Scratch copy of the counter with `BASE` patched from `0b75a84c…` (round-53 tip, frozen) to `3a600d2f…` (round-54 tip, the pre-freeze wrong BASE), run against the base tree `tip=3a600d2f`:

```
$ python3 cited-check-patched.py --repo $S/lane --tip 3a600d2f… --scratch $S   # exit=0
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```
The do-nothing control passes with a same-tip BASE — exactly the pre-freeze failure `corpus/lessons/round-55.md:77-87` records (`fixture=1 lane=1 scenarios=15/15 dropped=0 met=True`).

Reverted (frozen) BASE at the same tip:
```
$ python3 lane/tools/round54-cited-path-check.py --repo $S/lane --tip 3a600d2f… --scratch $S   # exit=1
fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=1 met=False
detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)
```
Lane-side numbers are byte-identical to the frozen receipt `.ufo/waves/round-55/controls/base.c2.out` (fleet hash differs only because fleet HEAD has since moved). The BASE=0b75a84c choice is load-bearing: the drop horizon must include the round-54 re-anchor, and it does.

## 3. Reachable in one round (build measurement reproduced)

```
$ python3 lane/tools/round54-cited-path-check.py --repo $S/lane --tip 9c60eae6… --scratch $S   # exit=0
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```
Matches `.ufo/waves/round-55/measured/c2-build.out` exactly. Single build commit `9c60eae6` on top of base `3a600d2f` lands freeze + counters + ledger row + lesson.

## 4. Superseded-row attack — the drop is the round-52→round-53 re-point

`git log 0b75a84c..3a600d2f -- SCORECARD.md` names two commits; the line-18 diff is entirely in `9a3104c771509df2dad6b6fe13c023bd3c472c35` ("round-54 honest stop (run wrap-up)" — the round-54 evidence re-anchor; it also re-anchored the SKILL.md/depth rows with "evidence re-anchored round 54" markers):

```
-| calibration | **7** | … `corpus/lessons/*verifier-spotcheck.md` blobs … → `39` … latest outside closure `corpus/lessons/round-52-verifier-spotcheck.md` (admitted; re-anchored round 53) …
+| calibration | **7** | … `40` … latest outside closure `corpus/lessons/round-53-verifier-spotcheck.md` (rejected; re-anchored round 54) …
```
`1406a91` did not touch this line; `3a600d2f` (the non-author spot-check) did not touch SCORECARD.md at all.

Row facts, each verified against the lane clone:
- Token `corpus/lessons/round-52-verifier-spotcheck.md` cited exactly once at base (`SCORECARD.md:18`, backticked) and resolves at base (`git cat-file -e 0b75a84c:corpus/lessons/round-52-verifier-spotcheck.md` → exists) → a genuinely LIVE base citation, matching the class semantics.
- Token cited 0 times at `3a600d2f` and at `9c60eae6`.
- Replacement `corpus/lessons/round-53-verifier-spotcheck.md` cited at `SCORECARD.md:18` (backticked) at both `3a600d2f` and `9c60eae6`, and resolves at both.
- `dropped=1` at the base control is exactly this one citation; no other surface dropped anything.

`registry/cited-path-corrections.tsv:46`'s note ("the round-54 re-anchor's closure pointer; the replacement is cited in SCORECARD.md at tip and resolves") is accurate in every part. The round-52→round-53 re-point really is the drop the counter flags, and the row is the correct disclosure for it.

## 5. Defect: `superseded` checks cited-at-base, not resolved-at-base (fixable, latent)

Contract (frozen, same round): docstring lines 96-99 — "the original token was cited in that surface at --base **and resolved there** (unlike `fixed`, which corrects an UNRESOLVED citation, `superseded` discloses a **live** citation re-pointed to a different file)"; preregistration C2 predicate — "`superseded` rows disclosing a **live base citation** re-pointed to a cited, resolving replacement".

Code: `tools/round54-cited-path-check.py:477-478` checks only `tok in base_citelines` (cited at base). No resolution-at-base check exists in the branch (lines 461-479), though `base_unres` is already a parameter.

Demonstration (scratch fixture repo driven against the unmodified frozen counter; same construction style as the counter's own fixture):

```
--- row class=superseded ---   # base: SCORECARD.md line 1 cites broken `tools/broken.py`; tip: line 3 cites resolving `tools/new.py` elsewhere
  met contribution: True {'cited': 1, 'unresolved': 0, 'disclosed': 0, 'undisclosed': 0, 'bad': 0, 'stale': 0, 'dropped': 0}
--- row class=fixed ---        # identical tree, row classed `fixed`
  met contribution: False {'cited': 1, 'unresolved': 0, 'disclosed': 0, 'undisclosed': 0, 'bad': 1, 'stale': 0, 'dropped': 0}
```

A citation that was BROKEN at base can be re-pointed to any resolving file, at any line, and rowed `superseded` — escaping `fixed`'s same-line/stem binding (the M15 guard: "a resolving replacement cited elsewhere is not the correction"). Class choice launders around the line-binding. This is an under-enforcement of the counter's own frozen contract, not a tradeoff.

Why it does not touch round 55: the landed row's token resolved at base (§4); the fixture's honest superseded base token resolves; the forged-superseded fixture fails earlier (replacement not cited). All frozen receipts reproduce (§2, §3).

Proposed minimal correction (full diff in out dir as `superseded-base-resolution-fix.diff`):

```diff
@@ -476,6 +476,8 @@ def check_row(...):
         if base_citelines is not None and tok not in (base_citelines.get(surf) or {}):
             return "superseded token was not cited in this surface at the base"
+        if base_unres is not None and tok in (base_unres.get(surf) or set()):
+            return "superseded token was unresolved at base; a `fixed` row, not `superseded`"
         return None
```

Validated on the scratch copy: the §5 demo flips to `bad=1`; the 15-scenario fixture still passes `15/15`; the landed tip still prints `met=True` (`landed-tip-fixed.out`); the base control still prints `dropped=1 met=False` (`base-tip-fixed.out`). The counter is frozen, so this belongs to a future freeze (round 56); applying it in round 55 would itself violate the counter_sha256 kill rule. Round-55 C2 measurements stand either way.

## 6. Paths written

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/K4Sizing.md`
- Evidence dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/K4Sizing/`
  - `base-tip-orig.out`, `base-tip-patched.out`, `landed-tip-orig.out` (reruns, §2-§3)
  - `gap-demo-frozen.out`, `gap-demo-fixed.out` (§5 demonstration)
  - `base-tip-fixed.out`, `landed-tip-fixed.out` (fix validation)
  - `superseded-base-resolution-fix.diff` (proposed fix)
