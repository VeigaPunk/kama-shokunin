# V3Stable — C2 verdict stability across lane tips

**Verdict: the frozen round-50 C2 counter is monotone in tool vintage — `met=True` only at the build tip `97c864be`, `met=False` at every earlier tip — but it exits 2 (`EvalError`) on the round-47 tip because that tip's contract is the pre-`region` 4-column schema, and the abort silently discards the fixture-leg results it had already computed.**

## Method

Frozen counter `tools/round50-append-audit-v5-check.py` run against a `--shared` clone of the lane at six commits. "Round-N tip" = the commit the round measured (from each round's recorded receipts, not the last commit whose subject starts `round-N`; e.g. round 49's last subject commit is the closure `26ecba64`, its measured tip is `24e906f0`):

```
python3 tools/round50-append-audit-v5-check.py --repo $S/lane --tip <full commit> --scratch $S --out <receipt>
```

- r44 `ef76777e5fbdc39a80ec7a93e41dc177366168db` (`.ufo/waves/round-44/c1/after.out` `tip=` line)
- r47 `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` (`.ufo/waves/round-47/measured/c1-after.out`)
- r48 `c4b2175d2ff9466beaed039dc8330176362e7d82` (`.ufo/waves/round-48/measured/c1-after.out`)
- r49 `24e906f034bc5635ee46d9743b1aa9ff93707362` (`.ufo/waves/round-49/measured/c2.out`)
- base `26ecba64ad6fb571d09074b07202d1618a46ecd1` (round-50 frozen base)
- build `97c864bead3ee4a2f629574e77263d33834ec98a` (round-50 build)

All six runs: zero stderr, no traceback, all receipts in this directory (`c2-*.out/.stdout/.exit`). `--out` receipts were written for every run except r47 (the exit-2 path returns before `--out` is written, counter `main` lines 527-529 vs 536-538).

## Results

| tip | exit | headline | lane leg: tool exit / bad_decl / regressed / ungraded_lines | event `dd9f5dc6c0e6` | event `0718b6abbda6` |
|---|---|---|---|---|---|
| r44 `ef76777e` | 1 | `fixture=0 lane=0 scenarios=0/12 met=False` | tool absent at tip (landed round 46); no lane leg | — | — |
| r47 `383f1fc7` | **2** | `could-not-evaluate: contract row with 4 cells` | aborted before reporting (see F1) | — | — |
| r48 `c4b2175d` | 1 | `fixture=0 lane=1 scenarios=6/12 met=False` | 0 / 0 / 0 / **89** | `ungraded 17 <= v5 natively exempt 23` | `ungraded 72 <= v5 natively exempt 72` |
| r49 `24e906f0` | 1 | `fixture=0 lane=1 scenarios=9/12 met=False` | 0 / 0 / 0 / **82** | `ungraded 17 <= v5 natively exempt 23` | `ungraded 65 <= v5 natively exempt 72` |
| base `26ecba64` | 1 | `fixture=0 lane=1 scenarios=9/12 met=False` | 0 / 0 / 0 / **82** | `ungraded 17 <= v5 natively exempt 23` | `ungraded 65 <= v5 natively exempt 72` |
| build `97c864be` | 0 | `fixture=1 lane=1 scenarios=12/12 met=True` | 0 / 0 / 0 / **89** | `ungraded 17 <= v5 natively exempt 23` | `ungraded 72 <= v5 natively exempt 72` |

The lane reports five events at every tip where the leg ran; the two above are the only ones with non-zero `ungraded` (the counter's own v5 bound is printed only for those). `ungraded_lines` is the tool's self-report: v3 and v5 both total 89 (17+72); v4 totals 82 (17+65). The counter's v5 bound `native` is tip-stable (23 / 72) across all four post-v3 tips — v5's birth-DAG origin is deterministic over the same commit set.

r49 tip and base produce byte-identical detail lines (diff of `c2-r49-24e906f0.out` and `c2-base-26ecba64.out` differs only in the `tip=` line) — the v4 tool is unchanged between them, and the base failure `scenarios=9/12` matches L1's dry run exactly (order-b, fence, crlf-launder fail; F3/F4/F5 defects).

## Findings

### F1 (new): `EvalError` on the round-47 tip — exit 2, and the abort discards computed fixture results

`python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip 383f1fc7… --scratch $S` → stdout `could-not-evaluate: contract row with 4 cells`, exit 2, empty stderr.

Cause: the round-47 `registry/append-only-contract.tsv` is the v2 schema `path\trule\tdeclared_at\tnote` — 4 columns, no `region` (that column landed with the v3 contract in round 48; `git show c4b2175d:registry/append-only-contract.tsv` header is `path\trule\tdeclared_at\tregion\tnote`). The counter's `parse_contract` (`tools/round50-append-audit-v5-check.py:359-360`) raises `EvalError` on any row whose cell count ≠ 5, and `main` (line 527-529) maps it to exit 2.

This is a handled exit, not a crash — but two consequences are worth recording:

1. **The counter cannot evaluate any lane tip older than the `region` column.** Any `--tip` in `[3a09a1d9 … c4b2175d)` (v2 contract era) or earlier (no contract at all — `git show` then fails inside `git()` → same `EvalError` path) exits 2 rather than grading `met=False`. By contrast a missing *tool* degrades gracefully to `fixture=0 lane=0 met=False` (the r44 row above, via the `os.path.isfile` check at line 521). The asymmetry is inconsistent: pre-tool tips get a verdict; pre-region-contract tips get "could not evaluate".
2. **The abort throws away the fixture leg.** `main` computes `res = scenarios(tree, fx, detail)` (line 525) *before* `lane_leg` (line 526) raises. The exit-2 return prints only `could-not-evaluate: …` — the 12 fixture outcomes and the tool's own exit/summary (already collected in `detail`) are never emitted. At r47 the v2 tool did in fact run (see F2); its evidence is lost.

Proposed fix (report only — counter is frozen): catch the contract-parse failure inside `lane_leg`, append a `detail:` line naming the schema gap, and return `False`, so a pre-region contract reads `fixture=N/12 lane=0 met=False` exit 1 instead of exit 2 with no detail. Minimal change at `tools/round50-append-audit-v5-check.py:401`: wrap `parse_contract(...)` in `try/except EvalError` → `detail.append(f"lane: contract unreadable at tip ({exc})")` and `return False`.

### F2 (supporting): the r47 tip's own tool genuinely fails — no false `met` is masked

To confirm exit 2 hides no pass, the tip's tool was run directly:

```
git -C $S/lane archive 383f1fc7… tools/append-only-audit.py | tar -x -C $S/tool47
python3 $S/tool47/tools/append-only-audit.py --repo $S/lane --to 383f1fc7… --json
```

→ exit 1, `summary {'commits': 305, 'files': 86, 'events': 5, 'restored': 3, 'partial': 2, 'regressed': 1}` (receipt `r47-append-only-audit-direct.json`). This is the recorded round-48 build finding: v3 (and v2) regress on the `0718b6ab` SCORECARD.md event because the round-45 authority banner line was rewritten in place. The v2 JSON has no `ungraded_lines`/`ungraded` keys (pre-v3 concept), so "lane ungraded_lines" at r47 is N/A by definition, not merely unreported. The counter's exit 2 coincides with a real failure.

### F3: at the r48 tip the lane leg cannot distinguish v3 from v5

`lane=1` at r48: the v3 tool's self-reported `ungraded` (17, 72) never exceeds the counter's v5 `native` bound (23, 72), all rows bind, tool exits 0 — `graded + ungraded == deleted` and numstat equality hold too. v3/v5 separation is carried entirely by the fixture leg (v3 fails 6/12: `launder`, `substring`, `negated`, `wildcard-self` — v4 binding rules absent; `fence`, `crlf-launder` — v5 rules absent). Coincidence worth noting: v3's `ungraded 72` for `0718b6ab` equals the v5 bound 72 (v3 ungrades everything under the exempt title; v5's bound happens to equal it at this event), and v3's `ungraded_lines 89` equals the v5 tool's 89 at the build tip. Not a defect — the lane history simply exercises none of the v4/v5 distinctions — but it means the lane leg alone would accept v3 as v5.

### F4: `order-b` reproduces the F3 (rev-list order) defect on exactly the v4 tips

v3 tool (r48 tip): `order-a` and `order-b` both pass — v3 has no origin concept to be order-sensitive. v4 tool (r49, base): `order-a` passes, `order-b` fails `exit 1 (want 0)` — the traversal-order defect F3 reproduced on both commits the v4 tool occupied. v5 (build tip): both pass. This is the counter working as designed; recorded here as the stability signature of the fix.

## Reproduction

```
S=/fast/scratch/hyaku/kama-r50/V3Stable; mkdir -p "$S"; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
for t in ef76777e5fbdc39a80ec7a93e41dc177366168db 383f1fc780573d46b6ea8bc1044b21f604e6ba3e \
         c4b2175d2ff9466beaed039dc8330176362e7d82 24e906f034bc5635ee46d9743b1aa9ff93707362 \
         26ecba64ad6fb571d09074b07202d1618a46ecd1 97c864bead3ee4a2f629574e77263d33834ec98a; do
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py \
    --repo "$S/lane" --tip "$t" --scratch "$S"; echo "exit=$?"
done
```

~5 s per run; no network, no servers. No installs performed (no tools needed beyond system `git`/`python3`); pacman untouched; `pgrep -f llama-server` — no llama-server processes started by this seat (C2 spawns only git/python).

Report: .ufo/waves/round-50/w1/out/V3Stable.md
