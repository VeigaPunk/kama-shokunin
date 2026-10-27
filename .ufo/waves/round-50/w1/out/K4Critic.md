VERDICT: The five assigned CRLF probes all behave per the frozen v5 contract — one real defect found adjacent to them: `origins()` checks only the FIRST parent of a merge, so a merge that seats an LF copy of a foreign (CRLF-born) key inside an exempt section fabricates a birth, ungrading a line the spec grades (exit 0 instead of 1); the frozen counter's own oracle uses all parents, so the tool diverges from the contract it is judged against.

Scope: `tools/append-only-audit.py` at lane commit 97c864bead3ee4a2f629574e77263d33834ec98a (working copy verified `git diff`-clean against that commit). Hand expectations were written before any run; fixtures are byte-exact repos built via `git write-tree`/`commit-tree` under my scratch. Driver and raw JSON receipts are in `w1/out/K4Critic/`. Every reported event was cross-checked `graded+ungraded==deleted` and `deleted==git diff --numstat` — no violations.

## Probe results (contract: `SCORE.md A-corr exempt=## Axes`, threshold 20)

| probe | construction | expect (v5 spec) | observed | verdict |
|---|---|---|---|---|
| (1) carry LF→CRLF | `victim line` born LF under `## Axes`; CRLF twin lands in `## Round 1` next commit (key already held → no birth); Axes block (24 head + victim) deleted while Axes regrows | origin stays {Axes} → all 25 ungraded, `status=ungraded`, exit 0 | del=25 g=0 u=25 ungraded, exit 0 | per spec |
| (2) born CRLF in R1 | `cvictim line\r` born under `## Round 1`; LF twin lands under `## Axes`; Axes block deleted | origin {Round 1} → the LF twin graded; del=25 g=1 u=24 unrestored, exit 1 | exact | per spec |
| (3) mixed endings | 12 LF + 12 CRLF dated lines deleted, then restored with flipped endings (separate repo) | held is byte-exact on raw bytes → `restored_max=0` unrestored, exit 1; byte-exact restore in a second repo → `restored_max=24 restored` exit 0 | exact both | per spec (origin keys normalized, restore measure raw — consistent with docstring "the byte-exact restore measure below still uses the raw bytes") |
| (4) key collision | `dup line\r` and `deep line\r\r` born in `## Round 1`; then `dup line` (LF) and `deep line\r` land under `## Axes`; Axes block (24 head + both) deleted | `key()` strips ONE trailing `\r`: `dup line\r`→`dup line` collides (Axe copy = no birth, org stays {Round 1} → GRADED); `deep line\r`→`deep line` vs `deep line\r\r`→`deep line\r` → no collision → ungraded birth. del=26 g=1 u=25 exit 1 | exact | per spec — but see note A |
| (5) only= region | `only=## Errata` row; Errata holds 12 LF + 12 CRLF lines; delete all 24 Errata + 4 `## Main` lines | inside-prefix lines graded incl. CRLF (g=24); outside-prefix lines are `continue`d → counted as ungraded (u=4); exit 1 | del=28 g=24 u=4 unrestored, exit 1 | per spec — see note B |
| (extra) fully-CRLF file | every line CRLF incl. `## ` headings | `sections()` rstrips `\r` → headings parse; Axes deletions ungraded (24), Round-1 deletions graded (25) | exact | per spec |
| F6 merge-birth | `ml victim\r` born under `## Round 1` on second-parent branch; merge blob seats `ml victim` (LF) under `## Axes`; Axes block deleted | spec (counter docstring: birth = NO parent holds the key): merge is not a birth (2nd parent holds `ml victim`) → org={Round 1} → g=1 u=24 unrestored, **exit 1** | tool: g=0 u=25 ungraded, **exit 0** | **DEFECT** |

## The defect: `origins()` is first-parent-only

`tools/append-only-audit.py`:

- line 470: `parents[parts[0]] = parts[1] if len(parts) > 1 else None` — the parents map keeps only the first parent of every commit;
- line 495: `for q in (parents[x] or "").split():` — the origin/birth scan iterates that single parent, so a merge's pkeys never include second-parent keys;
- line 512 uses `parents[c]` for the first-parent diff, which is correct (the spec diffs against the first parent) — the bug is only reuse of the map for ALL parents.

The frozen contract (counter docstring, mirrored in the tool's own header): `birth = a commit c whose blob of the file holds key k while no parent of c holds k`. The counter's independent oracle implements it with `allpar[c]` = `ln.split()[1:]` (round50-append-audit-v5-check.py:418,449) — all parents. The tool implements it with one.

Demonstration (fixture `fx-f6-merge`, receipts `f6-unpatched.json` / `f6-patched.json` in my out dir):

```
c1 base: Axes head24 | Round 1 r×3
cB (2nd parent): adds "ml victim line\r" under ## Round 1   <- the key's only true birth
cA (1st parent): base tree
cm merge parents=[cA,cB]: blob seats "ml victim line" LF under ## Axes too
ce: Axes block deleted (head24 + "ml victim line"), Axes regrows, Round 1 untouched

tool (unpatched): event ce deleted=25 graded=0 ungraded=25 status=ungraded  exit 0
spec / counter oracle:                deleted=25 graded=1 ungraded=24 status=unrestored exit 1
```

The CRLF normalization amplifies it: under v4 byte-exact keys the Axes copy `ml victim line` would have keyed as a new blob line anyway; under v5 keys the planted `…\r` variant on the other branch makes the merge's placement look like native Axes birth even though the byte variant differs — a launder that survives exactly because the second parent is invisible to `origins()`.

Reachability on the lane: `git rev-list --min-parents=2 97c864be…` = 2 merges (2f7303c2, 5396a876); neither touches any contract-matched path (`git diff-tree --name-only`), and no contract file currently contains a CR byte — so the defect is latent on this lane's history, not live. But the frozen C2 counter DOES catch it where it occurs: its `native` bound counts deleted lines whose parent section is exempt AND whose all-parents origin contains an exempt title — native=24 < tool ungraded=25 → `lane: event … ungraded 25 > v5 natively exempt 24` → `met=False`. The gap is that the counter's 12 fixtures never construct a merge whose blob seats a second-parent key inside an exempt section (order-a/order-b hold the key in both parents), so fixture=1 cannot exclude this tool.

Smallest safe correction (verified): keep all parents for origin, keep first parent for the diff. Diff in `w1/out/K4Critic/append-only-audit.py.all-parents.diff`:

```diff
-            parents[parts[0]] = parts[1] if len(parts) > 1 else None
+            parents[parts[0]] = parts[1:]
@@
-            for q in (parents[x] or "").split():
+            for q in parents[x]:
@@
-        p = parents[c]
+        p = parents[c][0] if parents[c] else None
```

Verification of the fix (patched copy under my scratch, lane file untouched): F6 now reports `graded=1 ungraded=24 status=unrestored exit=1` (spec verdict); all seven of my fixtures keep their spec verdicts; and the frozen counter's own `scenarios()` run against the patched tool gives 12/12 (`ctrun` run, detail lines in out dir log) — the fix is strictly a correction, no regression on any frozen expectation.

## Notes (not defects)

A. Collision asymmetry (probe 4): because origin is a set keyed by the CR-stripped line, an attacker who plants `x\r` in a graded section first makes every later `x` twin foreign — including one genuinely born under `## Axes`. Mirrored, a planted LF `x` first makes a later `x\r` Axes copy native. The spec accepts this (origin is a property of the key, not the line instance); the frozen counter's `key()` is identical, so the tool and counter agree — flagging it only as a contract property worth naming: *first birth wins; multiplicity and byte-variant births are invisible to origin*. `x\r\r` keys to `x\r` (one CR stripped), so CRCRLF twins escape the LF/CRLF collision class — also per spec.

B. `only=` files and the counter's ungraded bound (probe 5): the tool counts skipped outside-prefix deletions as `ungraded` (they are in `deleted` but never reach `G`). The frozen counter's lane leg bounds `ungraded ≤` lines that are BOTH parent-exempt-sectioned AND origin-native; for an `only=` file the exempt set is empty, so ANY deletion outside the `only` region (≥ threshold) fails `lane` — even though the tool's accounting is spec-correct. The lane's single `only=` file (`corpus/knowledge/consumer-registry.md`) has no such event at tip, so nothing fires; worth a sentence in the lesson so a future edit of that file's `## Main` body isn't misread as a tool regression. Report only — not counter-fixable here (frozen).

## Artifacts

- `w1/out/K4Critic/drive.py` — fixture driver (all fixtures, byte-exact CRLF control, expectations inline)
- `w1/out/K4Critic/run1.log` — full PASS/FAIL run (6 spec-probes pass, F6 fails as predicted)
- `w1/out/K4Critic/f6-unpatched.json`, `f6-patched.json` — tool JSON on the merge-birth fixture before/after the fix
- `w1/out/K4Critic/append-only-audit.py.all-parents.diff` — proposed minimal fix
- `w1/out/K4Critic/counter-scenarios-patched.log` — frozen counter's `scenarios()` against the patched tool: 12/12

No installs. No writes outside my report path and `w1/out/K4Critic/`. Fixture repos live only in my scratch and are removed on cleanup.
