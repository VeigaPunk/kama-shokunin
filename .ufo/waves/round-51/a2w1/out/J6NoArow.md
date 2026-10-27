# Round 51 / a2w1 — C2 ablation control (seat J6NoArow)

**Verdict:** the A-row `permitted` rule is load-bearing — removing it alone (`permitted_edits()` → `set()`, ledger untouched) flips the frozen C2 counter from `fixture=1 lane=1 scenarios=9/9 met=True` (build commit 138af25b) to **`fixture=0 lane=0 scenarios=8/9 lost=142 disclosed=166 met=False`, exit 1** on the ablated commit e28d12d7. Control requirement (every ablation `met=False`) is satisfied; no defect found in the counter.

Build commit under test: `138af25b963450b6520794995605fa7dbbcd87e0` (build b6bed925 / build-fix 73bf2a7a / build-fix 2 138af25b), lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only; never written).

## 1. Fixture clone and ablation

```
S=/fast/scratch/hyaku/kama-r51/J6NoArow; export TMPDIR=$S
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane      # → $S/lane
git -C $S/lane rev-parse --show-toplevel                                    # → $S/lane   (asserted TOPLEVEL_OK before any commit)
git -C $S/lane checkout -q 138af25b963450b6520794995605fa7dbbcd87e0
```

Patch (single mechanism removed, nothing else touched; ledger **not** regenerated — the frozen `registry/append-only-disclosures.tsv` at 138af25b is kept as is):

```diff
@@ -507,7 +507,13 @@ def row_cells(text):
 def permitted_edits(dl, new_body):
     """v6 A-row: positions in dl of deleted rows whose id the new blob still holds with
-    every immutable cell byte-equal (only status, recheck and used-by changed)."""
+    every immutable cell byte-equal (only status, recheck and used-by changed).
+
+    ROUND-51 ABLATION CONTROL (seat J6NoArow): the A-row permitted rule is removed - this
+    always returns the empty set, so every deleted A-row is graded like a plain loss. The
+    ledger is NOT regenerated; the control measures the frozen C2 counter against a build
+    that lacks only this one mechanism."""
+    return set()
     rows = collections.defaultdict(list)
```

Full diff: `a2w1/out/J6NoArow/ablation-permitted-edits.diff` (932 B, 1 file, +6/−1).

Commit (fixture identity, in the clone only):

```
git -C $S/lane -c user.name=fx -c user.email=fx@invalid -c commit.gpgsign=false commit -q -am "r51 C2 ablation control (J6NoArow): permitted_edits returns the empty set; ledger not regenerated"
→ e28d12d78bb2e5daa1ce6574bc7b74f25fd19f18
```

## 2. Baseline (unablated build commit) — counter met=True

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
  --repo $S/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch $S/c2base \
  --out $S/receipts/j6noarow-c2-baseline-138af25b.out
```
```
tip=138af25b963450b6520794995605fa7dbbcd87e0
fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True
detail: fixture arow-mutable: exit 0 (want 0) ok events=[('SRC.md', 'ungraded', 1, 0)]
detail: lane: tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 166
exit=0
```
(Receipt: `a2w1/out/J6NoArow/j6noarow-c2-baseline-138af25b.out`. It reproduces the build receipt shape at `measured/c2-build.out` — that one was taken at 73bf2a7a, this one at the lane's build tip 138af25b: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, same `permitted_lines 58`.)

## 3. Ablation — frozen counter, exit 1, met=False

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
  --repo $S/lane --tip e28d12d78bb2e5daa1ce6574bc7b74f25fd19f18 --scratch $S/c2 \
  --out $S/receipts/j6noarow-c2-ablation.out
```
```
tip=e28d12d78bb2e5daa1ce6574bc7b74f25fd19f18
fixture=0 lane=0 scenarios=8/9 lost=142 disclosed=166 met=False
detail: fixture default-threshold: exit 1 (want 1) ok
detail: fixture arow-mutable: exit 1 (want 0) FAIL events=[('SRC.md', 'unrestored', 0, 0)]
detail: fixture arow-immutable: exit 1 (want 1) ok
detail: fixture code-span-pipe: exit 1 (want 1) ok
detail: fixture row-dropped: exit 1 (want 1) ok
detail: fixture disclosed: exit 0 (want 0) ok
detail: fixture bad-disclosure-1..4: exit 1 (want 1) ok  (4/4)
detail: fixture partial-disclosure: exit 1 (want 1) ok
detail: fixture two-files-one-commit: exit 1 (want 1) ok
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 15, 'partial': 0, 'regressed': 0, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: 3285cdf7a504 corpus/SOURCES.md: tool permitted 0 own 5   (… 17 such lines, 58 lines total …)
detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 166 permitted_lines 0; own lost lines in whole-file-graded files 142; ledger lines 166
exit=1
```
Receipt: `a2w1/out/J6NoArow/j6noarow-c2-ablation.out` (2 720 B, 30 detail lines).

Exactly one fixture scenario fails — `arow-mutable`, the scenario that *is* the ablated rule (A-row status+recheck edit must be `permitted`, exit 0; ablated: graded, `unrestored`, exit 1). The other eight (incl. all four bad-disclosure sub-cases) still get their constructed verdicts. Confirms the counter isolates this mechanism rather than failing globally.

## 4. Tool-level A/B (same tip, only the rule differs)

```
git -C $S/lane show 138af25b:tools/append-only-audit.py > $S/base-tool.py
python3 $S/base-tool.py                     --repo $S/lane --to 138af25b… --json   # exit 0
python3 $S/lane/tools/append-only-audit.py  --repo $S/lane --to e28d12d7… --json   # exit 1
```
| | baseline 138af25b | ablation e28d12d7 |
|---|---|---|
| summary.events | 106 | 106 |
| restored | 19 | 20 |
| unrestored | **0** | **15** |
| partial | 0 | 0 |
| disclosed | 51 | 51 |
| ungraded | 36 | 20 |
| permitted_lines | **58** | **0** |
| disclosed_lines | 166 | 166 |
| bad_disclosures | 0 | 0 |
| exit | 0 | 1 |

Event-key sets identical (106/106). Changed events: 17, **all `corpus/SOURCES.md`** — the only A-row file in the contract. Status transitions: `ungraded→unrestored` ×15, `ungraded→restored` ×1 (5890d1a0e20c, deleted 7 / permitted 6, still restored because its lines are re-held), `restored→restored` ×1 with only `permitted` changing. `disclosed_lines` and `bad_disclosures` untouched: the ledger is exactly as built, and the ablation adds undisclosed losses rather than disturbing disclosed ones.

Lines: 58 permitted lines across 17 events; of these **40 are not held at the ablated tip** (sum of per-event `undisclosed` on SOURCES events) and 18 are re-held later, hence 15 unrestored events rather than 17. Per-event table: `a2w1/out/J6NoArow/j6noarow-sources-events.txt`.

## 5. Refinement of the expected failure mode (reporting only)

The wave expectation was "lane=0 because the lost lines now exceed the ledger". Measured, the failure is narrower and the counter is *not* fooled by the missing rule:

- `lost` stays **142** and `disclosed` **166**: the counter recomputes `lost` with its own `permitted` set (`round51-append-audit-v6-check.py:349-361`), independently of the tool's, so the ablation cannot move that number. (Same reason `lane`'s whole-file `un != led` check does not fire: the counter still excludes the 58 permitted lines from `D`.)
- `lane=0` is carried instead by (a) the tool-summary gate — `definition v6 threshold 1 exit 1 {'unrestored': 15, …}` ≠ the `want` all-zero dict at `round51-append-audit-v6-check.py:267-271` — and (b) the permitted-equality check at `round51-append-audit-v6-check.py:336-338`, which fires 17× (`tool permitted 0 own N`).

This is the correct design (the counter's own leg must not inherit the tool's rule it is auditing), and the control confirms both independent paths catch the removal. Nothing to fix; recorded so the calibration reading does not attribute the lane failure to a lost-line/ledger delta that does not exist.

Counter bytes used are the frozen ones from the lane (`tools/round51-append-audit-v6-check.py`, untouched); the tool bytes are the tip's own (`git show <tip>:tools/append-only-audit.py`, extracted by the counter at `round51-append-audit-v6-check.py:398-405`), so the run is exactly the frozen procedure against a modified tree.

## 6. Compliance and cleanup

- Lane repo read-only from this seat: no write, no git/jj mutation, no index change. Only `git clone --shared` out of it and read-only `git` in it. (Lane HEAD moved to 4eca4892 during the wave — that is the L1's integration, not this seat.)
- No pacman (host-wide pause), no installs, no services started or stopped; `pgrep -af llama-server` → no match (exit 1). C2 runs no network and no server.
- Fixture commits only inside `$S/lane` with identity `fx`/`fx@invalid` after asserting `rev-parse --show-toplevel` == `$S/lane`.
- Scratch `/fast/scratch/hyaku/kama-r51/J6NoArow` removed after the receipts were copied into the lane out dir; no `/tmp` evidence.

## Files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow/j6noarow-c2-ablation.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow/j6noarow-c2-baseline-138af25b.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow/ablation-permitted-edits.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow/j6noarow-tool-baseline.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow/j6noarow-tool-ablation.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J6NoArow/j6noarow-sources-events.txt`
