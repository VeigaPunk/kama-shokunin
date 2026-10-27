# X6C2Smoke — C2 fixture-smoke receipt (round-55 wave 1)

Verdict: PASS — the frozen C2 counter at 9c60eae6f7ed84f7da93d219a406aadc30958c6c prints `fixture=1 lane=1 scenarios=15/15 … met=True` (exit 0) and reproduces the committed build receipt byte-for-byte once the fleet rev is pinned; one low-severity receipt-transparency finding (the scenario-15 forged branch is verified but not printed).

Seat: X6C2Smoke (leaf, no subagents dispatched). Axis judged: calibration. Milestone: r55 attack and verification.

## 1. Environment and provenance

```
$ sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  …/tools/round54-cited-path-check.py

$ git -C $S/lane show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-cited-path-check.py | sha256sum
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  -
```

The counter bytes at the freeze tip are byte-identical to the working-tree file and to the preregistration's `claims.C2.counter_sha256` (`d70a1729…650c`, preregistration.json line 34). The kill rule's "counter bytes at measurement differ from counter_sha256" clause is therefore satisfied.

Scratch: `S=/fast/scratch/hyaku/kama-r55/w1/X6C2Smoke`, `TMPDIR=$S`. One clone:
```
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
$ git -C "$S/lane" rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r55/w1/X6C2Smoke/lane
```
No lane/fleet write occurred: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` and `git -C /home/vgpnk/Projects/shokunin status --porcelain` show only pre-existing untracked wave files, none written by me. No tools installed (nothing needed; `pacman` not invoked).

## 2. The requested smoke run

```
$ export S=/fast/scratch/hyaku/kama-r55/w1/X6C2Smoke; export TMPDIR="$S"; cd "$S"
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py \
    --repo "$S/lane" \
    --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
    --scratch "$S" \
    --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/c2-smoke.out
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c fleet=4dd6935ec32d3d25a313c56c1e480437bd687c65
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
… 15 "detail: fixture ok: …" lines + 4 "detail: advisory: …" lines
EXIT=0
```

The requested predicate fields are confirmed: `fixture=1`, `scenarios=15/15`, `met=True`, exit code 0.
Receipt: `…/w1/out/X6C2Smoke/c2-smoke.out` (sha256 `520875e8…982b`).

## 3. Byte-comparison with the committed build measurement

The committed build receipt `.ufo/waves/round-55/measured/c2-build.out` was produced against fleet rev `6c4aba34c2a22519152d8c6f32e1039eecb1381b`; the fleet repo HEAD has since advanced (concurrent rounds), so the `fleet=` field of a default-HEAD run drifts. Pinning the fleet rev to the committed one reproduces the receipt exactly:

```
$ python3 …/tools/round54-cited-path-check.py --repo "$S/lane" \
    --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
    --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b \
    --scratch "$S" --out "$S/c2-smoke-fleetpinned.out"
EXIT=0
$ diff "$S/c2-smoke-fleetpinned.out" .ufo/waves/round-55/measured/c2-build.out
BYTE-IDENTICAL-TO-COMMITTED-BUILD     (diff exit 0, no output)
```
Copy: `…/w1/out/X6C2Smoke/c2-smoke-fleet-pinned.out` (sha256 `bc59e5e1…d3bc`).

Unpinned, the only difference from the committed receipt is the `fleet=` field:
```
$ diff …/w1/out/X6C2Smoke/c2-smoke.out .ufo/waves/round-55/measured/c2-build.out
1c1
< tip=9c60eae… fleet=4dd6935ec32d3d25a313c56c1e480437bd687c65
---
> tip=9c60eae… fleet=6c4aba34c2a22519152d8c6f32e1039eecb1381b
```
Every other line (the leg line's 9 counters, all 15 fixture lines, all 4 advisory lines) is identical. `fleet` is a read-only input of the fleet repo's HEAD, not of the lane tree, so this is expected drift, not a counter defect.

## 4. The 15 per-scenario fixture detail lines

Extracted verbatim (`grep '^detail: fixture '`) into `…/w1/out/X6C2Smoke/c2-smoke-fixture-scenarios-raw.out` (15 lines, sha256 `e10d0a44…3ec4`), and an annotated version with the counter source line of each scenario's `cases`-list entry into `…/w1/out/X6C2Smoke/c2-smoke-fixture-scenarios.out` (sha256 `16f30eaf…adf8`).

| # | scenario | counter verdict | counters line | source |
|---|---|---|---|---|
| 1 | unresolved path is counted | ok | met=False, undisclosed=1 | tools/round54-cited-path-check.py:733 |
| 2 | fenced path is not cited | ok | met=True, cited=0 | :735 |
| 3 | brace group with one dead member | ok | met=False, undisclosed=1 | :737 |
| 4 | forged deleted row is bad | ok | met=False, bad=1 | :739 |
| 5 | true deleted row discloses | ok | met=True, disclosed=1 | :741 |
| 6 | forged never row is bad | ok | met=False, bad=1 | :743 |
| 7 | line anchor past EOF is counted | ok | met=False, undisclosed=1 | :745 |
| 8 | row for a resolving token is stale | ok | met=False, stale=1 | :747 |
| 9 | upstream at a mutable ref is bad (M10) | ok | met=False, bad=1 | :750 |
| 10 | upstream serving unpinned bytes is bad (M11) | ok | met=False, bad=1 | :754 |
| 11 | upstream at the pinned revision with pinned bytes discloses (M12 contrast) | ok | met=True, disclosed=1 | :757 |
| 12 | never row on an upstream-inventory token is bad (M13) | ok | met=False, bad=1 | :760 |
| 13 | fixed replacement cited away from the base line is bad (M15) | ok | met=False, bad=1 | :764 |
| 14 | fixed replacement at the base line with the original stem discloses | ok | met=True, bad=0, stale=0 | :768 |
| 15 | superseded re-pointed citation discloses, forged superseded is bad | ok | met=True, bad=0, dropped=0 | :773 |

The `cases` list has exactly 15 entries and `SCENARIOS = 15` (tools/round54-cited-path-check.py:168), so `scenarios=15/15` means every constructed scenario got its fixed verdict — none fell through to the default.

## 5. Corroborating runs

**Base-tree control (red).** Running the same frozen counter at the round-54 base tip on my clone:
```
$ python3 …/tools/round54-cited-path-check.py --repo "$S/lane" \
    --tip 3a600d2f729828419aaea34cc402c8b0d20fb720 \
    --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S" --out "$S/c2-base.out"
tip=3a600d2f… fleet=6c4aba34…
fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=1 met=False
EXIT=1
$ cmp -s "$S/c2-base.out" .ufo/waves/round-55/controls/base.c2.out && echo IDENTICAL
BASE-RUN-BYTE-IDENTICAL-TO-COMMITTED-CONTROL
```
Copy: `…/w1/out/X6C2Smoke/c2-base-replica.out` (sha256 `d6a6f550…3828`). So the fixture leg (`fixture=1`, 15/15) is green at both tips, and only the lane leg flips (lane=1/dropped=0 at the freeze, lane=0/dropped=1 at the base) — the C2 measurement is discriminating, and the drop the base control flags is exactly the round-54 re-anchor that the `superseded` class now covers.

**Verdict stability.** Three consecutive runs with the fleet rev pinned:
```
pin1 exit=0 wall_ms=1341  pin1 byte-identical-to-pinned-run
pin2 exit=0 wall_ms=1441  pin2 byte-identical-to-pinned-run
pin3 exit=0 wall_ms=1353  pin3 byte-identical-to-pinned-run
```
Three runs at default fleet HEAD were also identical to each other apart from the `fleet=` field (the fleet HEAD advanced once mid-sequence, 4dd6935e → 666bc1ef).

**Inherited-GIT hostility (Sen4Fixture regression).** The counter was re-run with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` all poisoned in the environment:
```
GIT_DIR=/tmp/does-not-exist GIT_WORK_TREE=/tmp GIT_CONFIG_COUNT=1 \
GIT_CONFIG_KEY_0=user.name GIT_CONFIG_VALUE_0=evil GIT_INDEX_FILE=/tmp/nope-index \
python3 …/tools/round54-cited-path-check.py --repo "$S/lane" --tip 9c60eae… --scratch "$S" …
EXIT=0
$ diff <(grep '^detail: fixture ' hostile.out) c2-smoke-fixture-scenarios-raw.out
HOSTILE-FIXTURE-LINES-IDENTICAL
```
All 15 fixture lines are unchanged under a hostile inherited `GIT_*` environment, so the fixture's `clean_env` stripping (tools/round54-cited-path-check.py:678-680, 698) holds.

**No leftovers from this seat.** `pgrep -af llama-server` run at the end of my run → no match (exit 1). This counter starts no server, downloads no model, and fetches only raw.githubusercontent.com URLs. (A later `pgrep` during session teardown matches two processes belonging to the sibling seat J5EnvNames, under that seat's own scratch `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/`; they are not mine and I did not touch them.) My scratch tree `/fast/scratch/hyaku/kama-r55/w1/X6C2Smoke` was removed at the end of the session.

## 6. Finding (severity: low — receipt transparency, not a verdict defect)

**File/line:** `tools/round54-cited-path-check.py:791-796` (the `shape == "superseded"` branch of the fixture loop), surfacing at `tools/round54-cited-path-check.py:812` where the per-scenario detail line is emitted.

**What the code does.** The round-55 superseded scenario is a two-branch scenario: the *honest* tip (base citation re-pointed to a cited, resolving replacement, with a `superseded` ledger row) must evaluate met=True, and the *forged* tip (same row, replacement not cited at tip) must evaluate met=False with `bad=1`. The `hit` predicate at line 795-796 requires both:

```python
hit = bool(want(ok, c)) and ok and c["dropped"] == 0 and c["bad"] == 0 \
    and (not ok2) and c2["bad"] == 1
```

**The defect.** The emitted detail line (line 812) prints only the *honest* branch's counters:
```
detail: fixture ok: superseded re-pointed citation discloses, forged superseded is bad (met=True {'cited': 1, 'unresolved': 0, 'disclosed': 0, 'undisclosed': 0, 'bad': 0, 'stale': 0, 'dropped': 0})
```
The forged branch's verdict (`ok2=False`, `c2['bad']=1`) is computed and enforced but never appears in the receipt. A reader of the committed receipt therefore sees a scenario named "forged superseded is bad" whose own recorded counters show `bad=0` — the receipt does not evidence the half of the scenario that gives the scenario its name. This is the same class of gap as the round-54 externalized doc/code gap the closure flagged: the receipt under-states what was checked.

**Why it is not a verdict defect.** The forged branch is genuinely enforced: I re-derived it independently by importing the counter module and replaying the fixture's superseded branch by hand:
```
HONEST branch: met= True  {'cited': 1, 'unresolved': 0, 'disclosed': 0, 'undisclosed': 0, 'bad': 0, 'stale': 0, 'dropped': 0}
FORGED branch: met= False {'cited': 0, 'unresolved': 0, 'disclosed': 0, 'undisclosed': 0, 'bad': 1, 'stale': 0, 'dropped': 0}
```
`ok2=False` and `c2['bad']=1` are exactly what line 795-796 requires, so the scenario's `ok` verdict is earned, not vacuous. The counters are also consistent with the `superseded` class implementation at tools/round54-cited-path-check.py:461-479 (token not cited at tip; replacement cited and resolving; token cited at base).

**Proposed fix** (in my out dir; the counter is frozen — not applied in place). Two added detail lines inside the `shape == "superseded"` branch, so the receipt carries both halves of the two-branch scenario:

```diff
--- tools/round54-cited-path-check.py
+++ tools/round54-cited-path-check.py
@@ -794,6 +794,8 @@
                 ok2, c2 = evaluate(lane2, None, scen_base, sub, verbose=False)
                 hit = bool(want(ok, c)) and ok and c["dropped"] == 0 and c["bad"] == 0 \
                     and (not ok2) and c2["bad"] == 1
+                detail.append(f"fixture branch: superseded honest (met={ok} {c})")
+                detail.append(f"fixture branch: superseded forged (met={ok2} {c2})")
             elif shape in ("m15", "fixed-honest"):
                 # base cites the ellipsis token at line 2; the m15 tip cites the
                 # replacement at line 6 (away from the base line -> bad), the honest tip
```
Files: `…/w1/out/X6C2Smoke/proposed-superseded-branch-detail.diff` (the unified diff) and `…/w1/out/X6C2Smoke/proposed-round54-cited-path-check-patched.py` (the full patched copy, sha256 `ec4c5946…7623`).

**Verification of the proposal** (run on a scratch copy only; the frozen counter was not modified):
```
$ python3 "$S/c2-counter-copy.py" --repo "$S/lane" --tip 9c60eae… --fleet-rev 6c4aba34… --scratch "$S" --out "$S/patched.out"
EXIT=0
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
detail: fixture branch: superseded honest (met=True {'cited': 1, … 'bad': 0, … 'dropped': 0})
detail: fixture branch: superseded forged (met=False {'cited': 0, … 'bad': 1, … 'dropped': 0})
detail: fixture ok: superseded re-pointed citation discloses, forged superseded is bad (met=True {…})
```
The patched copy keeps `scenarios=15/15` and `met=True` — the fix is additive and verdict-preserving. (It also adds two extra `detail:` lines to the receipt body; a downstream parser that counts `detail:` lines would see 21 instead of 19 — the leg line and all counters are unchanged.)

## 7. Scope note

This seat's assignment is the C2 fixture-smoke receipt only. I did not run the C1 counter, did not build a kill battery, and did not touch any lane file. The counters, preregistration and controls were treated as frozen: nothing was edited in place, and the only patch I produced is a proposed diff in my own out directory.

## 8. Paths written

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/c2-smoke.out` (the requested receipt)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/c2-smoke-fixture-scenarios.out` (annotated 15 scenario lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/c2-smoke-fixture-scenarios-raw.out` (verbatim 15 scenario lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/c2-smoke-fleet-pinned.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/c2-base-replica.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/proposed-superseded-branch-detail.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X6C2Smoke/proposed-round54-cited-path-check-patched.py`

Scratch `/fast/scratch/hyaku/kama-r55/w1/X6C2Smoke` removed at session end.
