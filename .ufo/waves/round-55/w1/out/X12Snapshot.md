# X12Snapshot — round 55, lane kama: snapshot-harness regression at the landed tip

**Verdict: PASS on both assigned instruments (freshness axis holds) — but the KQ36 re-run surfaces a REAL, LIVE staleness defect in the SCORECARD head table: the calibration row's closure-count run fact states `40` while the tree holds `41`, which turns all three head-table counters red at the landed tip (`r41`/`r42`/`r43` all exit 1, `met=False`). The defect is inherited from the round-54 base commit `3a600d2f`, not introduced by round 55; a verified one-line fix is delivered in my out directory.**

---

## 1. Assigned instruments — both green at the landed tip

Frozen tip: `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (the round-55 w0 freeze commit named in the seat spec).
Clone used (lane is read-only to me): `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` with `$S=/fast/scratch/hyaku/kama-r55/w1/X12Snapshot`, `git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r55/w1/X12Snapshot/lane` (verified before any commit). `TMPDIR=$S`.

### 1a. `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0`, exit 0

```
$ cd $S/lane && bash tools/test-snapshot.sh
...
PASS symlinked history dir refused
RESULT pass=30 fail=0
exit=0
```
Receipt: `.ufo/waves/round-55/w1/out/X12Snapshot/test-snapshot.out` (full PASS/FAIL transcript, 30 PASS lines, 0 FAIL, exit 0).

Matches the registered expectation exactly: the freshness head row (`SCORECARD.md:15`) declares `run \`bash tools/test-snapshot.sh\` → \`RESULT pass=30 fail=0\``, and the harness prints that byte-for-byte.

### 1b. `python3 tools/sources-append-only.py --selftest` → `45/45 selftest cases passed`, exit 0

```
$ cd $S/lane && python3 tools/sources-append-only.py --selftest
...
ok: oracle covers every fixture column
ok: compared set without `opened` is refused
ok: non-UTF-8 blob is a parse error
45/45 selftest cases passed
exit=0
```
Receipt: `.ufo/waves/round-55/w1/out/X12Snapshot/sources-append-only-selftest.out`.

Matches the registered expectation exactly: `SCORECARD.md:14` (operability row) declares `run \`python3 tools/sources-append-only.py --selftest\` → \`45/45 selftest cases passed\``.

### 1c. KQ36 "landed tip" byte-identity qualification (`corpus/QUALITY.md:205-210`)

KQ36 (round-26 qualification) requires that the *measured source bytes* and the *instrument bytes* each match the corresponding bytes in the landing commit. Verified:

| artifact | sha256 | matches tip blob | matches lane HEAD `8abadfed` |
|---|---|---|---|
| `tools/test-snapshot.sh` | `236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646` (194 lines) | yes | yes (unchanged `9c60eae6..8abadfed`) |
| `tools/sources-append-only.py` | `2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d` (704 lines) | yes | yes (unchanged) |

`git diff 9c60eae6 8abadfed -- corpus/SOURCES.md tools/test-snapshot.sh tools/sources-append-only.py` → empty. So both runs are landed-tip measurements at the freeze commit and remain so at the lane's current tip; the freshness row's cited `test-snapshot.sh` sha256 (`236c23c1…`) re-derives exactly.

### 1d. Related registered facts re-derived at the tip (supporting, not assigned)

- `python3 tools/citation-provenance.py --selftest` → `selftest: ok (24 cases)`, exit 0 (freshness row, `SCORECARD.md:15`).
- `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0`, exit 0 (operability row, `SCORECARD.md:14`).
- `python3 tools/report-landing-audit.py --selftest` → `selftest cases=79 failed=0`, exit 0 (operability row).
- `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`, exit 0 (calibration row).
- `python3 tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0`, exit 0 (calibration row).
- `python3 tools/sources-append-only.py --from 3a600d2f --to 9c60eae6` → `added S511 (allowed)` / `no append-only violations`, exit 0 (KQ22 pair for the only commit touching `corpus/SOURCES.md` this round). Receipt: `sources-append-only-base-to-tip.out`.
- Freshness row's recheck-cadence figure → `218` (rows S001–S477 with a `recheck` cell). Matches `SCORECARD.md:15`.
- `tools/kama-probe.sh` sha256 `4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4` (1138 lines) — matches the operability row exactly.

---

## 2. DEFECT D1 (head-table staleness — LIVE, three counters red at the landed tip)

### 2.1 Exact file and line

`/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:18` — the `| calibration | **7** |` row of the `## Axes` table:

```
run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `40` (outside closures on record); that figure is the number of `corpus/lessons/*verifier-spotcheck.md` blobs at the measured commit;
```

The row's own clause — *"that figure is the number of `corpus/lessons/*verifier-spotcheck.md` blobs at the measured commit"* — is false at the landed tip: the tree holds **41**.

### 2.2 The command that shows it

```
$ git ls-tree --name-only 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/lessons/ | grep -c 'verifier-spotcheck'
41

$ git show 9c60eae6:SCORECARD.md | sed -n '18p' | grep -o '`[0-9]*` (outside closures on record)'
`40` (outside closures on record)
```

Three registered head-table counters go **red (exit 1, `met=False`)** at the landed tip:

```
$ python3 tools/round41-scorecard-reconcile.py --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --out ...
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False
detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '40' (exit 0)
exit=1

$ python3 tools/round42-selfdesc-reconcile.py --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --out ...
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=53 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '40' (exit 0)
exit=1

$ python3 tools/round43-registry-audit.py --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --out ...
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c
unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=1 hidden=0 pop=54 registered=54 mismatches=1 met=False
detail: spot: calibration row states 40, tree holds 41
exit=1
```

Full receipt: `.ufo/waves/round-55/w1/out/X12Snapshot/defect-d1-calibration-count-stale.out`.

### 2.3 Provenance — inherited from the round-54 base, NOT introduced by round 55

```
$ for c in 9a3104c7 1406a91e 3a600d2f 9c60eae6; do ... done
9a3104c7 count=40 row=`40` (outside closures on record)
1406a91e count=40 row=`40` (outside closures on record)
3a600d2f count=41 row=`40` (outside closures on record)   <-- row goes stale here
9c60eae6 count=41 row=`40` (outside closures on record)

$ git log --oneline --diff-filter=A -- corpus/lessons/round-54-verifier-spotcheck.md
3a600d2f round-54 verifier spot-check (integrator, hyaku): non-author admit/reject
```

Commit `3a600d2f` (the round-55 **base**) added the 41st `corpus/lessons/round-54-verifier-spotcheck.md` blob without re-deriving the head row that counts them. Round 55's freeze commit `9c60eae6` changed nothing in `SCORECARD.md`, so the red is inherited and still live at the landed tip.

This is exactly the failure the lane already mined once — `corpus/lessons/round-43.md:71` ("**(3) A run fact in the calibration row is false at the commit that landed it.** … the outside closure that produced the 29th blob did not re-derive the row it was recorded in"), and `corpus/lessons/round-46.md:41` (the re-anchor broke the round-43 counter's `spot` leg). The lane has re-landed this same defect a second time. The lane's own round-54 verifier spot-check (`corpus/lessons/round-54-verifier-spotcheck.md:34`) even re-derived the count as `40` — correct at its own tip `1406a91e`, but it is the very commit that then added the 41st blob.

**Not disclosed anywhere**: `grep -rn "mismatches=1\|run_bad=1" corpus/lessons/round-54*.md .ufo/waves/round-54/` → no hits; `corpus/lessons/round-55.md` does not mention the head counters at all; the round-55 wave carries no r41/r42/r43 regression receipt (`.ufo/waves/round-55/measured/` holds only `c1-build.out`, `c2-build.out`).

### 2.4 Proposed fix (D1 only) — verified

Patch: `.ufo/waves/round-55/w1/out/X12Snapshot/proposed-fix-scoredcard-calibration-count.patch` (applies cleanly to `9c60eae6`; verified with `git apply --check`).

```diff
-| calibration | **7** | run `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`; run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `40` (outside closures on record); …
+| calibration | **7** | run `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`; run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `41` (outside closures on record); …
```

Applied in my fixture clone as commit `fa8da29f2217357d15f3b71ffe8833d96dd2f092` (identity `fx <fx@invalid>`, `git -C $S/lane rev-parse --show-toplevel` verified = `$S/lane`):

| counter | before fix | after fix |
|---|---|---|
| `round41-scorecard-reconcile` | `mismatches=1 met=False`, exit 1 | `mismatches=0 met=True`, exit 0 |
| `round42-selfdesc-reconcile` | `mismatches=1 met=False`, exit 1 | `mismatches=0 met=True`, exit 0 |
| `round43-registry-audit` | `spot=1 mismatches=1 met=False`, exit 1 | `spot=0 mismatches=0 met=True`, exit 0 |
| frozen C2 `round54-cited-path-check` | `met=True`, exit 0 | `fixture=1 lane=1 scenarios=15/15 … dropped=0 met=True`, exit 0 (unchanged) |

Receipt: `.ufo/waves/round-55/w1/out/X12Snapshot/fix-verification.out`.

The fix keeps the `(outside closures on record)` parenthetical byte-intact, which is what `round43-registry-audit.py:207` (`re.search(r"`(\d+)` \(outside closures on record\)", l)`) and the round-46 lesson require — round 46 broke that counter by re-anchoring the parenthetical itself.

---

## 3. DEFECT D2 (same row — the closure *pointer* is stale, and the naive fix breaks the frozen C2 counter)

### 3.1 Exact file and line

`SCORECARD.md:18` also states `latest outside closure \`corpus/lessons/round-53-verifier-spotcheck.md\` (rejected; re-anchored round 54)`. The newest outside closure in the tree is `corpus/lessons/round-54-verifier-spotcheck.md` (verdict `rejected-honest-stop, admitted=false`, `corpus/lessons/round-54-verifier-spotcheck.md:6`), so the "latest" pointer names a file that is no longer the latest.

No counter instruments this pointer directly, so it is a self-description defect, not a counter red.

### 3.2 The naive fix breaks the frozen C2 counter — a trap for the integrator

Re-pointing the pointer to round-54 and dropping the round-53 citation makes the frozen C2 counter read **`bad=1 met=False`, exit 1**:

```
$ python3 tools/round54-cited-path-check.py --repo $S/lane --tip 6df9723e --scratch $S
fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=1 stale=0 dropped=0 met=False
detail: bad ledger line 46 (SCORECARD.md `corpus/lessons/round-52-verifier-spotcheck.md` superseded): replacement 'corpus/lessons/round-53-verifier-spotcheck.md' is not cited in SCORECARD.md at tip
```

Cause: the round-55 `superseded` ledger row (`registry/cited-path-corrections.tsv:46`) declares the round-52→round-53 re-point, and its `superseded` check requires the *replacement* token (`corpus/lessons/round-53-verifier-spotcheck.md`) to still be cited in SCORECARD.md at tip (`tools/round54-cited-path-check.py:463-470`). Removing the round-53 citation invalidates the row that C2 depends on.

### 3.3 A pointer fix that keeps C2 green (verified)

Keeping the round-53 token cited *and* naming round-54 as the latest satisfies both the pointer's truth and the ledger row:

```
| latest outside closure `corpus/lessons/round-54-verifier-spotcheck.md` (rejected-honest-stop); previous `corpus/lessons/round-53-verifier-spotcheck.md` (rejected; re-anchored round 54);
```
→ C2 at fixture `e4e9638d`: `fixture=1 lane=1 scenarios=15/15 cited=694 … dropped=0 met=True`, exit 0.

### 3.4 Combined D1+D2 fix (recommended) — verified against all four counters

Patch: `.ufo/waves/round-55/w1/out/X12Snapshot/proposed-fix-combined.patch`. Applied as fixture commit `eb976605dfde838af3771b0cf318a114b050a472`:

| counter | result | exit |
|---|---|---|
| `round41-scorecard-reconcile` | `axes=6 facts=37 hash_bad=0 lines_bad=0 run_bad=0 … mismatches=0 met=True` | 0 |
| `round42-selfdesc-reconcile` | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=53 met=True` | 0 |
| `round43-registry-audit` | `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=54 registered=54 mismatches=0 met=True` | 0 |
| frozen C2 `round54-cited-path-check` | `fixture=1 lane=1 scenarios=15/15 cited=694 … dropped=0 met=True` | 0 |

---

## 4. Scope note on C1 (measured, not assigned)

For completeness, the frozen C1 counter was run once at the landed tip: `python3 tools/round54-replay-code-audit.py --repo $S/lane --tip 9c60eae6 --scratch $S --out $S/c1-at-tip.out` → **exit 0**, `newrow: 2 rows new since base; 1 name the git environment doc: ['| S511 |']`, `twopass b3: both observation passes byte-identical over 16 range reads`, `rehash b3: 8 observed archive paths re-stat'ed and re-hashed after the replay exited, inode and digest unchanged`, `sealed b3: … is a sealed memfd with the frozen digest`, `teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`. Receipt copied to `c1-counter-at-tip.out`. C1 is unaffected by D1/D2 (it reads `corpus/SOURCES.md`, not the head table).

---

## 5. Risks, blockers, and limits

- **The integrator's call, not mine.** D1 and D2 are lane files; I did not edit the lane. The patches are proposals in my out directory, per the "never edit lane files in place" constraint.
- **D1 is a base-inherited red.** It exists at the round-55 base `3a600d2f` and at the freeze tip `9c60eae6`; round 55 did not cause it and cannot be said to have regressed the head table. But it is live at the landed tip, and KQ36's re-run is precisely the mechanism that surfaces it.
- **D2's pointer change is coupled to the frozen C2 counter.** Any integrator who re-points the closure pointer must keep the round-53 token cited (or amend the `superseded` ledger row and re-freeze C2). The combined patch does this and is verified green on C2.
- **Coverage of my own re-run.** `test-snapshot.sh` is a hermetic loopback-fixture harness (it does not contact live endpoints) and `sources-append-only.py --selftest` is in-memory only (its own docstring says it "never runs git and is fixture self-consistency, never corpus evidence"). Neither is live-endpoint evidence; the registered live drift evidence for the freshness row remains `.ufo/waves/round-41/c2/ls-remote-vllm.txt`, whose sha256 `13388e48…` I confirmed still matches at the tip.
- **No leftover processes.** `pgrep -af llama-server` after my runs shows only peer seat `J5EnvNames`' two processes (`/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/…`); zero processes under my own scratch. I did not start any service and killed none of a peer's.
- **No tooling installed.** Nothing needed installing; no pacman/uv/npm action taken this seat.
- **Scope boundary.** I did not run the C1 kill battery (the L1's `run-battery.py` owns those receipts, per the wave spec's explicit instruction to X7BatteryReplay) and did not modify any frozen counter.

---

## 6. Files written (all under my out directory)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot.md` — this report
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/test-snapshot.out` — `RESULT pass=30 fail=0`, exit 0
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/sources-append-only-selftest.out` — `45/45 selftest cases passed`, exit 0
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/sources-append-only-base-to-tip.out` — `--from 3a600d2f --to 9c60eae6` → `added S511 (allowed)`, exit 0
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/defect-d1-calibration-count-stale.out` — D1 evidence + three red counters at the tip
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/round41-scorecard-reconcile-at-tip.out` — r41 red receipt
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/round43-registry-audit-at-tip.out` — r43 red receipt
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/proposed-fix-scoredcard-calibration-count.patch` — D1-only fix
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/proposed-fix-combined.patch` — recommended D1+D2 fix
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/fix-verification.out` — all counters green after the fix
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/c2-counter-at-fixture-fix.out` — frozen C2 green at the fixed fixture
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X12Snapshot/c1-counter-at-tip.out` — frozen C1 green at the landed tip

Scratch `/fast/scratch/hyaku/kama-r55/w1/X12Snapshot` removed on completion.
