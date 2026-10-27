# J12Hide — round 53 C2 ablation: hiding instead of disclosing

**Verdict: shortcut confirmed — all three hiding variants (fence, quotes, `./x/` prefix) meet the frozen C2 counter when applied to SKILL.md, and none meets when the same hiding is applied to SCORECARD.md, because the `dropped` leg reads `SCORECARD.md` only (tools/round53-cited-path-check.py:365-369, docstring:70). Hiding a dead citation outside SCORECARD.md, with its ledger row removed, is invisible to C2: `met=True`, `dropped=0`, and the only trace is `cited` falling 682 → 678.**

## 1. Method

Frozen C2 counter, never edited, never wrapped in a tracer:
`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py` (docstring is the contract).
Base of every ablation: the L1 build `c22602bd8d83ab26349d1087e916ca537ee4f9d1`. Scratch clone: `git clone --shared` of the lane at `/fast/scratch/hyaku/kama-r53/J12Hide/lane`; toplevel asserted before the first commit; every commit made with `-c user.name=fx -c user.email=fx@invalid` in that clone only. Nothing in the lane, the fleet repo or the counters was modified; the frozen counter was run as a subprocess against the clone.

Fleet revision pinned to `ee9f7341bd98de0fcd85f6c01f689301589b27e9` (the revision in the L1 build receipt `.ufo/waves/round-53/measured/c2-build.out`) so the comparison is against the same fleet tree; fleet HEAD moves between seats.

Reproduced the L1 build first (receipt `c2-build-repro.out`):

```
$ python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd… --fleet /home/vgpnk/Projects/shokunin \
    --fleet-rev ee9f7341… --scratch $S
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True   exit=0
```

The 14 unresolved citations (exact, from the counter's own `survey()`), which the ledger's 15 rows disclosed:

| surface | token | cited at line(s) |
|---|---|---|
| SCORECARD.md | `.ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py` | 491 |
| SCORECARD.md | `tools/server/server-schema.cpp` | 1471, 3029 |
| SCORECARD.md | `.ufo/waves/round-29/w1/out/ConfirmM01..11/` | 1503 |
| SCORECARD.md | `.ufo/waves/round-31/c2/c2-tip.json` | 1635, 1732 |
| SCORECARD.md | `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` | 1741 |
| SCORECARD.md | `.ufo/waves/round-999/count-c999.py` | 1844 |
| SCORECARD.md | `.ufo/waves/round-38/w1/out/FetchS352/` | 2136 |
| SCORECARD.md | `.ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt` | 2136 |
| SCORECARD.md | `.ufo/waves/round-40/c2/{base,after}.out` | 2184, 2228 |
| SCORECARD.md | `.ufo/watchdog.log` | 2904 |
| SKILL.md | `tools/server/server-schema.cpp` | 1143, 1246 |
| SKILL.md | `tools/server/server-common.cpp` | 1245 |
| SKILL.md | `tools/server/server-task.cpp` | 1247 |
| SKILL.md | `tools/server/server-chat.cpp` | 1248 |

Ablation driver `ablate.py` (out dir) applies, on the build tree: variant **a** = insert a ```` ``` ```` fence pair around each line carrying a dead citation; variant **b** = replace the dead span's backticks with double quotes; variant **c** = prefix the dead token with `./x/` inside the backticks. Two scopes:

- `all` — the literal seat control: **every ledger row deleted** (`registry/cited-path-corrections.tsv`, all 15 rows) and all 14 dead citations hidden.
- `skill` — the same three hiding edits restricted to the only surface outside SCORECARD.md that carries dead citations; the 10 SCORECARD.md rows are kept, the 4 SKILL.md `upstream` rows are deleted (they would otherwise be `stale`).

## 2. Measurements (frozen counter, fleet rev ee9f7341)

Command for each row: `python3 tools/round53-cited-path-check.py --repo $S/lane --tip <commit> --fleet /home/vgpnk/Projects/shokunin --fleet-rev ee9f7341bd98de0fcd85f6c01f689301589b27e9 --scratch $S`

| variant | scope | commit | cited | unresolved | undisclosed | dropped | met | exit |
|---|---|---|---|---|---|---|---|---|
| a fence | all | 8b97a62b5d3bfaa162a4e327b06e848ea841e31c | 648 | 0 | 0 | **26** | False | 1 |
| b quotes | all | 922278b0fc4cb73f9a925393aa17431b783a150a | 668 | 0 | 0 | **10** | False | 1 |
| c `./x/` | all | c1fbf24124244c50a857cf1c630b68baa0304cdc | 668 | 0 | 0 | **10** | False | 1 |
| a fence | skill | e7b1b2a2192af378a3487f2c3c2a71609bf9cb53 | 678 | 10 | 0 | 0 | **True** | 0 |
| b quotes | skill | 5db46b56394e1d94a2aee5c262736970aa1bed85 | 678 | 10 | 0 | 0 | **True** | 0 |
| c `./x/` | skill | 54ec85bd9abb5ac06c147b9eafe4c2aa3f0736ec | 678 | 10 | 0 | 0 | **True** | 0 |

Receipts: `c2-frozen-v_{a,b,c}_{all,skill}.out`; diffs: `diff-v_{a,b,c}_{all,skill}.patch`; commit ids: `commits.txt`. Fixture leg stayed 8/8 in all six runs, so the shortcut is in the lane leg only.

Reading of the table:

1. **`dropped` is the whole defence, and it is SCORECARD-only.** In the `all` runs `undisclosed=0` and `unresolved=0` — the hiding worked perfectly as hiding; the only failing leg is `dropped`, and it fires only because the hidden tokens were in SCORECARD.md. Variant a fences whole lines and so also drops 16 resolving SCORECARD tokens (26 = 10 dead + 16 collateral); variants b and c are surgical and drop exactly the 10 dead SCORECARD tokens.
2. **Outside SCORECARD.md nothing fires.** In the `skill` runs the 4 dead llama.cpp citations disappear from the parse, their 4 ledger rows are deleted, and the counter reports `met=True` with every other leg clean. `cited` 682 → 678 is the sole trace, and no leg bounds `cited`.
3. **The three mechanisms are equally effective and plausible.** A fence is already a sanctioned idiom in this counter (docstring: "the restored blocks of round 52 are fenced, so history kept verbatim is not a standing citation"); quoting a path is a typographic edit; `./x/` is stripped by citations():158 before the root test and therefore never a citation. Only SCORECARD.md is protected against all three.

### 2.1 The build already exercises this gap benignly

At base, SKILL.md cited 203 tokens; at the build tip, 202. Two base-cited tokens left the surface and the frozen counter reported `dropped=0`:

```
gone from SKILL.md base→tip: ['scripts/local-helper.mjs', 'tests/report-audit/…']
```

(`scripts/local-helper.mjs` was corrected in place to an absolute path, `tests/report-audit/…` to the directory; ledger comment lines 8-12 states the first deliberately has no row.) These are legitimate corrections, but they are byte-for-byte the same shape as hiding: a base-cited token is no longer a citation at tip, and C2 cannot tell the two apart outside SCORECARD.md. The round-53 exposure is exactly the 4 `upstream` SKILL.md pins; SHONEN.md (9 base tokens, no dead ones) is equally unprotected but latent.

## 3. Proposed fix (in the out dir, not applied)

`proposed-c2-dropped-all-surfaces.diff` — extends `dropped` to all three surfaces and exempts only tokens named by a `fixed` row or by a new `externalized` class (evidence = the in-place replacement text, which must appear in that surface at tip and must not itself be a citation; `externalized` is also exempt from `stale`, like `fixed`).

Measured with the patched copy (`counter-fixed.py`, scratch only, run against the same clone):

| tree | frozen counter | proposed counter |
|---|---|---|
| build c22602bd | met=True, dropped=0 | met=False, **dropped=1** (`SKILL.md:scripts/local-helper.mjs`) |
| v_a_skill e7b1b2a2 | met=True, dropped=0 | met=False, **dropped=5** (the 4 hidden + the unrowed correction) |
| v_b_skill 5db46b56 | met=True, dropped=0 | met=False, **dropped=5** |
| v_c_skill 54ec85bd | met=True, dropped=0 | met=False, **dropped=5** |
| build + one `externalized` row (v_fix 62e8fd3a) | met=False, bad=1 (unknown class) | **met=True, dropped=0, fixture 8/8** |

So the proposal closes the shortcut and is satisfiable by the build with one added ledger row (`SKILL.md  scripts/local-helper.mjs  externalized  ~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`, SKILL.md:113). Receipts: `c2-proposed-*.out`.

## 4. Risks and limits of the finding

- The fix is a **predicate change**, not a counter patch: it must be refrozen with a new preregistration, and the build needs the one extra ledger row to keep meeting. It cannot be slipped into round 53 after the fact.
- `externalized` residual hole: it accepts arbitrary non-citation text as evidence, so a determined lane can excuse a hidden token by writing some non-citation string into the surface. It raises the bar from "invisible" to "must fabricate a checkable replacement", not to "impossible".
- The `upstream` class needs a live `raw.githubusercontent.com` fetch; a lane without network cannot disclose a llama.cpp path and is pushed toward hiding — the shortcut is exactly the offline path.
- Ablation was run with fleet rev pinned to the build's `ee9f7341`; results are relative to that tree.

## 5. Blockers

None. No lane file, counter, preregistration or control was modified; probes ran only in `/fast/scratch/hyaku/kama-r53/J12Hide` and its single `--shared` clone, which was removed at the end. I started no `llama-server`; the two `llama-server` processes visible during the run belong to seat K2Design's scratch (ports on loopback, `/fast/scratch/hyaku/kama-r53/K2Design/...`) and were left untouched.

## 6. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J12Hide.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J12Hide/` — `c2-build-repro.out`, `c2-frozen-v_{a,b,c}_{all,skill}.out`, `diff-v_{a,b,c}_{all,skill}.patch`, `build-v_{a,b,c}_{all,skill}.log`, `c2-proposed-build.out`, `c2-proposed-v_{a,b,c}_skill.out`, `c2-proposed-build-plus-externalized-row.out`, `c2-proposed-build-plus-externalized-row.first-attempt-stale.out`, `ablate.py`, `proposed-c2-dropped-all-surfaces.diff`, `commits.txt`
