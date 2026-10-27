# F20C2MutationSensitivity — C2 `falsifiable()` probe
Axes: calibration (predicate relevancy to quote) and operability (counter evaluates/classifies mutations). Frozen C2 claim/population unchanged; lane source read-only. Read W1 MT04 evidence and exercised pristine counter against committed receipt (receipt_ok=True, 10 captures); no lane edits or installs.

## 15 varied predicates (expressions → evaluate / falsifiable / classification)
Classification uses frozen meaning: accepted as “sensitive” by predicate gate, but does not establish claim/quote relevance unless noted.

1. `c['version']['version'] == c['version']['version']` → True / False / correctly rejected (identical chain mutated on both sides).
2. `bool(c['version'])` → True / True / accepted but content-vacuous; only capture truthiness/emptiness.
3. `c['version']['version'] == '0.40.11'` → True / True / accepted; unrelated to a quote about tags/ps; genuine predicate but no quote linkage.
4. `c['ps-before'] == c['tags-empty']` → True / True / accepted false-positive: committed captures have equal bodies, mutation flips one path only.
5. `len(c['ps-before']['models']) == len(c['tags-empty']['models'])` → True / False / rejected; mutations keep both lengths equal.
6. `bool(c['show']['model_info'])` → True / True / accepted emptiness check; unrelated to arbitrary quoted statement.
7. `c['v1-models-empty']['data'] is None` → True / True / accepted; irrelevant field can flip by sentinel substitution.
8. `1 if c['version']['version'] == '0.40.11' else 0` → True / True / accepted constant-branch dressing, unrelated quote possible.
9. `any(m['name'] or True for m in c['tags']['models'])` → True / True / accepted; tests nonemptiness, not `name` content.
10. `c['version']['version'] == '0.40.11' and False` → False / False / rejected.
11. `not (c['version']['version'] != '0.40.11')` → True / True / accepted equivalent comparator; no quote linkage.
12. `c['show']['modelfile'][:5] != ''` → True / False / rejected silently: `chains()` does not traverse slices.
13. `c['tags']['missing'] == 'x'` → None / False / unevaluable and skipped (counter source says no errors increment).
14. `len(c['version']['version']) > 0` → True / True / accepted; generic nonempty text, not a documented claim test.
15. `c['tags']['models'][0]['name'] == 'kama-b61c98ad5747:latest'` → [W1 MT04 control] True / True / honest exact capture field control; baseline positive.

The concrete false-positive is not merely “mutation sensitivity is imperfect”: cross-capture equality passes although the committed `ps-before` and `tags-empty` bodies are identical, because `falsifiable()` mutates each syntactic chain separately. Also, the evaluator has no quote→capture/field binding: an unrelated version predicate can count against a tags/ps quote. W1's end-to-end synthetic all-vacuous registry passed `met=true`, errors=0, all 5 control families rejected (tautology 1/1, verdict flip 5/5, quote corrupt 14/14, drop line 14/14, tamper 1/1); thus these controls do not detect semantic irrelevance.

Smallest safe correction for calibration: define/enforce predicate-to-quote capture relevance (and relevant documented field/claim), then reject comparison of distinct capture chains whose committed bodies are identical; keep mutation testing as a separate necessary condition. These are findings only, not predicate/claim edits.

Evidence: W1 `.ufo/waves/round-60/w1/out/MT04FalsifiableGaming.md`, `.../probe-results.json`; frozen contract `.../controls/freeze.txt`; live exercise of `tools/round60-c2-counter.py` on committed receipt. Commands executed: `python3 -B -c '<import counter; receipt_caps; 15 safe_compile/evaluate/chains/falsifiable probes>'` exit 0; output recorded above. Disk status: `/home` 35% used / 585G free; `/fast` 27% / 592G free. No tool installed/updated.