# CritC2Junk — C2 counter soundness under junk bytes (round 36, wave 3)

Axis attacked: coverage (C2 counter). Scope: sandbox-only git-writing check. The real lane repo was only read and cloned; every git write happened in a fresh `--no-hardlinks` clone at `.ufo/waves/round-36/w3/out/CritC2Junk/sandbox/` (seeded at lane tip `9014843cb7de8fbe87a97954c13832b67d55f046`; the L1's drafts are uncommitted working-tree bytes, so the sandbox starts clean of them).

## Counterexample planted

Commit `0b43926710eab3f7d76a99815ac8c0d52372647a` in the sandbox carries both:

- `corpus/knowledge/sglang-native-route-deprecation.md` — junk entry whose only citation is `source: S999`, an id present in **neither** the tip registry nor the base `e5a8ece` registry (verified 0 grep hits at both revisions before committing).
- `corpus/README.md` — appended block under the exact heading `## Coverage map — round 36 addition` (em dash copied from the tool's `HEADING` constant) naming `knowledge/sglang-native-route-deprecation.md` exactly once, in one table row.

## Command and measured output

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py \
  --repo <seat>/sandbox --tip 0b43926710eab3f7d76a99815ac8c0d52372647a
```

```
named 1 file_exists 1 cited_new 0 met False
exit=1
```

Answer to the assigned question: **cited_new stays 0 and named is 1.** The counter rejects the junk citation while the naming machinery still counts the block.

Supporting measurements, same tool bytes, same sandbox:

- Selftest at the clean lane tip `9014843`: `SELFTEST base_met=False outside_met=False old_id_met=False pass=1` / `base named 0 file_exists 0 cited_new 0 met False`, exit 0. The do-nothing control reproduces outside the lane.
- Non-vacuity complement, tip `93c6b120a73bc463a23d3caea6dbc8bc2052c9de` (same tree plus one registry row `| S999 | … |`): `named 1 file_exists 1 cited_new 1 met True`, exit 0. `cited_new` flips only when the cited id becomes a registry row absent at base, so the 0 above is semantic rejection, not dead plumbing. `file_exists 1` on the junk run separately confirms the entry bytes were actually read.

## Mechanism (read from `tools/round36-coverage-audit.py`, not inferred)

- `named` = substring count of the entry path inside the block under the exact heading, and `met` requires exactly 1 (line 51, 76).
- `cited_new` requires `any(sid in tip_ids and sid not in base_ids)` over ids matched by `\bS[0-9]{3,}\b` in the entry (lines 54–75); a junk id in neither registry can never satisfy it.
- Base is hardcoded `e5a8ece…`, so the old-id path (present at tip and base) also stays 0 — consistent with the selftest's `old_id_met=False`.

## Verdict and smallest safe correction

No defect found on the attacked axis: junk bytes cannot move `cited_new`, and a junk README block alone cannot reach `met True` because `met` is the conjunction with `cited_new`. No correction needed; no predicate touched (C1/C2 predicates and counting commands untouched, per the frozen claims).

Non-blocking residuals (observation only, no change proposed): `named` is a raw substring count, so a block naming the path twice yields `named 2` → `met False` (fails safe), and a near-path string like `…deprecation.md.bak` inside the block would still count as naming — harmless only because `met` still requires `cited_new` on the real entry citation. Both directions are conservative; neither justifies touching the frozen predicate.

All results above are measured; mechanism lines are read from the tool source. Sandbox state left in the seat directory for re-inspection: commits `0b43926…` (junk) and `93c6b12…` (complement) on top of `9014843…`.
