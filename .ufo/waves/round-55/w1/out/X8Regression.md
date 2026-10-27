# X8Regression — round-55 regression battery at 9c60eae (lane kama)

**Verdict: two reds — both are integration defects introduced by the round-54 verifier spot-check commit `3a600d2f` (the round-55 BASE), inherited unchanged by the round-55 freeze `9c60eae`; both are repairable with two small edits (one SCORECARD figure, one hexrun-ledger row), both fixes verified green in a scratch clone, and neither touches a frozen counter, the preregistration, or the C1/C2 claims.**

Seat: X8Regression (executor; axes operability + calibration; milestone r55 attack and verification).
Lane tip under test: `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (round-55 w0 freeze). Base: `3a600d2f729828419aaea34cc402c8b0d20fb720` (round-54 lane tip).
Scratch clone used for every counter run (lane is read-only): `/fast/scratch/hyaku/kama-r55/w1/X8Regression/lane`, `git clone --shared` of the lane, checked out at the tip under test. All counters ran read-only against that clone. No lane file was edited in place; the proposed fix is a patch in this seat's out dir.

No tool was installed or upgraded for this seat, so `/home/vgpnk/.omp/agent/RULES.md`'s tooling directive has nothing to record. No pacman transaction was run (host-wide pacman is paused).

---

## 1. Battery — every named command, exit code and summary line

Run from the scratch clone at `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (`TMPDIR` = the seat scratch). Full transcript: `.ufo/waves/round-55/w1/out/X8Regression/battery-at-freeze-tip.txt`; the literal-default-argument forms: `battery-literal-defaults.txt`.

| # | command | exit | summary line |
|---|---|---|---|
| 1 | `python3 tools/round41-scorecard-reconcile.py --repo . --tip 9c60eae…` | **1** | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False` |
| 2 | `python3 tools/round42-selfdesc-reconcile.py --repo . --tip 9c60eae…` | **1** | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=53 met=False` |
| 3 | `python3 tools/capability-repertoire-audit.py --selftest` | 0 | `CAP_SELFTEST pass=2 fail=0` |
| 4 | `python3 tools/gate-registry-check.py --repo . --rev 9c60eae…` | 0 | `registered 54 unregistered 0 defective 0` |
| 5 | `python3 tools/sources-append-only.py --from 3a600d2f… --to 9c60eae…` | 0 | `added S511 (allowed)` / `no append-only violations` |
| 6 | `bash tools/test-snapshot.sh` | 0 | `RESULT pass=30 fail=0` |
| 7 | `python3 tools/seat-report-immutability.py --selftest` | 0 | `SEAT_REPORT_IMMUTABILITY_SELFTEST pass=13 fail=0` |
| 8 | `python3 tools/instrument-agreement.py --selftest` | 0 | `IA_SELFTEST pass=4 fail=0` |
| 9 | `python3 tools/hexrun-census.py scan --repo . --rev 9c60eae…` | **1** | `tokens=1962 distinct=350 lane_oid=238 md5_blob=1 upstream_ok=98 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=1` |

Seven of nine are green. Reds: **#1, #2** (one shared root cause) and **#9**. Command #9 was additionally run in its literal form (`--repo . --rev 9c60eae…`, read-only) and with `--details`; the offending token is named in §3.

Commands #1, #2, #4 were also run in their **literal default-argument form** (`python3 tools/round41-scorecard-reconcile.py`, no `--repo`/`--tip`, cwd = the clone at the freeze tip) with identical results (`battery-literal-defaults.txt` and the literal block in `battery-at-freeze-tip.txt`); command #5's default `--repo` is the live lane path and returns the same `added S511 (allowed)` / `no append-only violations`.

### Adjacent counters run for context (not in the named list; red/green recorded for the integrator)

| command | exit | summary line |
|---|---|---|
| `python3 tools/round43-registry-audit.py --repo . --tip 9c60eae…` | **1** | `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=1 hidden=0 pop=54 registered=54 mismatches=1 met=False` — `detail: spot: calibration row states 40, tree holds 41` |
| `python3 tools/round43-hexrun-audit.py --repo . --tip 9c60eae…` | **1** | `tool=1 contract=1 live=0 hygiene=1 capability=1 met=False` — `detail: live reference census … '… unknown=1'` |
| `python3 tools/digest-ledger.py scan --repo . --rev 9c60eae…` | 0 | `tokens=137 blob=122 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` |
| `python3 tools/capability-repertoire-audit.py --repo . --tip 9c60eae…` (census, not selftest) | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` |
| `python3 tools/append-only-audit.py --repo . --to 9c60eae…` | 1 | `summary commits=368 files=104 events=114 restored=68 partial=0 unrestored=1 ungraded=40 disclosed=5 permitted_lines=59 disclosed_lines=10 bad_declarations=0 regressed=0` — **pre-existing, not a round-55 regression**: `unrestored=1` is identical at `0b75a84c`, `9a3104c7`, `1406a91e` and `9c60eae` (the unrestored event is `e81d90e6 SCORECARD.md deleted=3 graded=1 ungraded=2 status=unrestored`, a round-53 event). Not in the named battery; recorded, not charged to round 55. |

The round-43 registry audit's `spot` leg and the round-43 hexrun audit's `live` leg are **the same two defects** seen through the lane's own frozen instruments — independent confirmation that the two reds are real and not artifacts of one counter.

---

## 2. Defect A (reds #1 and #2 — one root cause)

**File and line:** `kama-shokunin/SCORECARD.md:18`, the `| calibration | **7** |` row of the `## Axes` head table.

**Defect:** the row's run fact states the outside-closure count as `40`:

```
run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `40` (outside closures on record)
```

but the tree at the measured commit holds **41** `corpus/lessons/*verifier-spotcheck.md` blobs, so the fact is false and the counter's `run_bad` leg fires.

**Command that shows it:**

```
$ git -C $S/lane ls-tree --name-only 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/lessons/ | grep -c 'verifier-spotcheck\.md'
41
$ python3 tools/round41-scorecard-reconcile.py --repo . --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False
detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '40' (exit 0)
exit=1
```

**Provenance — the defect is inherited from the round-54 closure, not introduced by round 55.** `corpus/lessons/round-54-verifier-spotcheck.md` was added by `3a600d2f` ("round-54 verifier spot-check (integrator, hyaku): non-author admit/reject"), which is the round-55 **BASE**. That commit added one lesson file and nothing else, so the closure count went 40 → 41 while the calibration row was never re-anchored. The count of `*verifier-spotcheck.md` blobs by tip:

```
1406a91e (round-54 lane tip) : 40
3a600d2f (round-55 base)      : 41
9c60eae (round-55 freeze)     : 41
8abadfed (round-55 build)     : 41
```

and the counter's behaviour across the same tips:

| tip | r41 | r42 | r43-registry |
|---|---|---|---|
| `1406a91e` | `mismatches=0 met=True` exit 0 | `mismatches=0 maxN=53 met=True` exit 0 | `spot=0 mismatches=0 met=True` exit 0 |
| `3a600d2f` | `run_bad=1 met=False` exit 1 | `r41=1 met=False` exit 1 | `spot=1 mismatches=1 met=False` exit 1 |
| `9c60eae` | `run_bad=1 met=False` exit 1 | `r41=1 met=False` exit 1 | `spot=1 mismatches=1 met=False` exit 1 |

So the regression was born at the round-54 closure and was carried, unnoticed, into the round-55 freeze and the round-55 build commit (`8abadfed` — the same two reds reproduce there).

**Why the round-55 freeze did not catch it:** the round-55 freeze commit `9c60eae` touched `tools/round54-replay-code-audit.py`, `tools/round54-cited-path-check.py`, `registry/cited-path-corrections.tsv`, `corpus/SOURCES.md`, `corpus/lessons/round-55.md` and the receipts — **it did not touch `SCORECARD.md` at all** (`git diff 3a600d2f 9c60eae -- SCORECARD.md` is empty), so the stale `40` survived the freeze unchanged. The round-55 build measurement (`.ufo/waves/round-55/measured/c1-build.out`, `c2-build.out`) exercises only the two frozen round-54 claim counters, neither of which reads the calibration row's closure figure; the standing regression counters were not part of that measurement, which is how the red survived to the build.

**Proposed fix** (in `.ufo/waves/round-55/w1/out/X8Regression/proposed-fix.patch`, applied and verified in the scratch clone):

```diff
-| calibration | **7** | … `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `40` (outside closures on record); …
+| calibration | **7** | … `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `41` (outside closures on record); …
```

One character in one cell. `SCORECARD.md:6` declares the `## Axes` table (and §Planned, §Retired, §Saturation, §Capabilities) as **re-derived in place**, and `registry/append-only-contract.tsv` exempts exactly those five head sections (`region exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`), so this in-place re-anchor is exactly the mechanism the lane's own contract prescribes — the same one the round-53 commit `e81d90e6` used when it moved `38` → `39`.

**Verification of the fix** (scratch clone, fixture identity `fx <fx@invalid>`, `git -C $S/lane rev-parse --show-toplevel` = `$S/lane` asserted before the commit):

```
$ python3 tools/round41-scorecard-reconcile.py --repo . --tip 43f99cb9…
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=1→0 met=True   exit=0
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip 43f99cb9…
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=53 met=True   exit=0
$ python3 tools/round43-registry-audit.py --repo . --tip 43f99cb9…
unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=54 registered=54 mismatches=0 met=True   exit=0
```

(The fix commit is `43f99cb913d9c3cafe69c6c6b2699334e6db3cde` in the scratch clone; the clone is scratch and is deleted at the end of the seat.)

**Note on the adjacent pointer.** The same row names `latest outside closure `corpus/lessons/round-53-verifier-spotcheck.md``, while the tree now also holds `corpus/lessons/round-54-verifier-spotcheck.md`. I tested moving that pointer to round-54 in the scratch clone and it **breaks the frozen C2 counter** — `fixture=1 lane=0 scenarios=15/15 … bad=1 stale=0 dropped=0 met=False` exit 1 — because the round-55 `superseded` ledger row in `registry/cited-path-corrections.tsv` binds the round-52 → round-53 re-point, and re-pointing again would need a new ledger row the frozen counter does not have. **The pointer must not be moved as part of this repair.** The `40` → `41` figure change is the only SCORECARD edit needed, and it leaves the `superseded` row's contract intact. This was measured, not assumed.

---

## 3. Defect B (red #9)

**File and line:** `kama-shokunin/corpus/lessons/round-54-verifier-spotcheck.md:6` — the lesson's header line

```
report: .ufo/reports/round-54/kama.md (fleet commit e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0, author kama-shokunin)
```

**Defect:** the 40-hex fleet-repo commit `e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0` has no row in `registry/hexrun-ledger.tsv`, so `tools/hexrun-census.py` classifies it `unknown` and exits 1 (the tool exits 1 when `ledger_bad + unknown != 0`).

**Command that shows it:**

```
$ python3 tools/hexrun-census.py scan --repo . --rev 9c60eae6f7ed84f7da93d219a406aadc30958c6c --details
tokens=1962 distinct=350 lane_oid=238 md5_blob=1 upstream_ok=98 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=1
detail: e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0 len=40 occurrences=1 class=unknown
exit=1
```

**Provenance:** the same commit `3a600d2f` added the lesson and, with it, the first citation of that fleet commit. The lane's own standing instrument for such citations is `registry/hexrun-ledger.tsv` plus a committed evidence blob under `.ufo/waves/round-NN/hexrun-evidence/<sha>.txt`; the round-54 lesson cites a fleet commit without either. The census history confirms the red was born there:

| tip | hexrun-census | exit |
|---|---|---|
| `1406a91e` | `… upstream_ok=98 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0` | 0 |
| `3a600d2f` (base) | `… unknown=1` | 1 |
| `9c60eae` (freeze) | `… unknown=1` | 1 |

**The token is a real fleet object, not garbage** — verified read-only against the fleet repo:

```
$ git -C /home/vgpnk/Projects/shokunin cat-file -t e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0
commit
$ git -C /home/vgpnk/Projects/shokunin show -s --format='%H %an %cI %s' e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0
e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0 kama-shokunin 2026-10-27T04:27:30-03:00 round-54: kama honest-stop report + ed135b3c L0 forward
$ git -C /home/vgpnk/Projects/shokunin branch -r --contains e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0
  origin/HEAD -> origin/main
  origin/main
  origin/master
$ git -C $S/lane cat-file -t e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0
fatal: git cat-file: could not get object info
```

i.e. an upstream `VeigaPunk/shokunin` commit that is absent from the lane — the exact shape the ledger's `upstream` class covers, and the exact shape of the round-52 and round-53 lesson citations already in the ledger (`3945011969…` → `.ufo/waves/round-53/hexrun-evidence/…`).

**Proposed fix** (also in `proposed-fix.patch`): append one row to `registry/hexrun-ledger.tsv` and add its evidence blob, following the round-53 precedent exactly.

```diff
--- a/registry/hexrun-ledger.tsv
+++ b/registry/hexrun-ledger.tsv
@@ -112,3 +112,4 @@
 3945011969fbc4b0bdcf4c856626d016068558ec	upstream	vgpnk/shokunin (fleet)	.ufo/waves/round-53/hexrun-evidence/3945011969fbc4b0bdcf4c856626d016068558ec.txt		2026-10-27	commit not blob: round-52 kama report fleet commit (kama-shokunin, 2026-10-27T02:40:15-03:00); cited at corpus/lessons/round-52-verifier-spotcheck.md:23; on fleet main, absent from the lane
+e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0	upstream	vgpnk/shokunin (fleet)	.ufo/waves/round-55/hexrun-evidence/e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0.txt		2026-10-27	commit not blob: round-54 kama honest-stop report fleet commit (kama-shokunin, 2026-10-27T04:27:30-03:00); cited at corpus/lessons/round-54-verifier-spotcheck.md:6; on fleet main, absent from the lane
```

plus the new file `.ufo/waves/round-55/hexrun-evidence/e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0.txt` (full text in the patch and standalone as `proposed-hexrun-evidence.txt`): the four read-only fleet-repo commands above and their outputs, in the round-53 evidence file's format.

`registry/hexrun-ledger.tsv` is **not** a declared append-only file (`registry/append-only-contract.tsv` has no row for it), so appending a row is the sanctioned mechanism; the evidence blob lives under `.ufo/`, which the census excludes from the document population, so the file itself contributes no new tokens (`tokens` stays 1962).

**Verification of the fix** (scratch clone, second fixture commit `b3b42f09f2b66ab88c39582003c5079913b2787a`):

```
$ python3 tools/hexrun-census.py scan --repo . --rev b3b42f09…
tokens=1962 distinct=350 lane_oid=238 md5_blob=1 upstream_ok=99 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0
exit=0
$ python3 tools/round43-hexrun-audit.py --repo . --tip b3b42f09…
tool=1 contract=1 live=1 hygiene=1 capability=1 met=True seed=1088346838
exit=0
```

---

## 4. Both fixes together — full battery re-run on the repaired tree

On the scratch clone with both fixes applied (`b3b42f09f2b66ab88c39582003c5079913b2787a`):

| command | exit | summary line |
|---|---|---|
| `round41-scorecard-reconcile.py --repo . --tip b3b42f09…` | 0 | `axes=6 facts=36 … mismatches=0 met=True` |
| `round42-selfdesc-reconcile.py --repo . --tip b3b42f09…` | 0 | `r41=0 … mismatches=0 maxN=53 met=True` |
| `capability-repertoire-audit.py --repo . --tip b3b42f09…` | 0 | `listed 11 observed 11 missing 0 unsubstantiated=0 met True` |
| `gate-registry-check.py --repo . --rev b3b42f09…` | 0 | `registered 54 unregistered 0 defective 0` |
| `sources-append-only.py --repo . --from 3a600d2f… --to b3b42f09…` | 0 | `added S511 (allowed)` / `no append-only violations` |
| `digest-ledger.py scan --repo . --rev b3b42f09…` | 0 | `tokens=137 … ledger_bad=0 wrong_unflagged=0 unknown=0` |
| `hexrun-census.py scan --repo . --rev b3b42f09…` | 0 | `… upstream_ok=99 … ledger_bad=0 unknown=0` |
| `round43-registry-audit.py --repo . --tip b3b42f09…` | 0 | `… spot=0 … mismatches=0 met=True` |
| `round43-hexrun-audit.py --repo . --tip b3b42f09…` | 0 | `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True` |
| `append-only-audit.py --repo . --to b3b42f09…` | 1 | `… unrestored=1 ungraded=41 … regressed=0` — identical to the pre-existing round-53 unrestored event; **the fix adds no new append-only harm** (the SCORECARD edit lands inside the contract-exempt `## Axes` head region and grades as `ungraded=1`) |

**The frozen round-55 claim counters are unaffected by both fixes.** `tools/round54-cited-path-check.py` on the repaired tree:

```
$ python3 tools/round54-cited-path-check.py --repo . --tip b3b42f09… --scratch $S/scratch-c2
tip=b3b42f09… fleet=666bc1ef…
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
exit=0
```

identical to the committed build measurement `.ufo/waves/round-55/measured/c2-build.out` (`fixture=1 lane=1 scenarios=15/15 … met=True`). C1 was not re-run: `tools/round54-replay-code-audit.py` is a network+live-process instrument (downloads the ~30 MB b11909 archive, starts llama-server on loopback) and no round-55 file it reads (`tools/round54-replay-code-audit.py`, `corpus/SOURCES.md`, the three committed round-48 v5 receipts, the archive) is touched by either fix. The C1 measurement and its kill battery are therefore untouched by construction, and the preregistration, the frozen counter bytes, the base controls and the kill battery are all unmodified.

### 4a. End-to-end verification of the delivered patch

The table above was measured on the seat's scratch branch. To prove the **delivered artefact itself** works, `proposed-fix.patch` was applied with `git apply` to a **fresh clone** of the lane checked out at `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (`git -C <clone> rev-parse --show-toplevel` asserted), committed with the fixture identity, and every counter re-run at the resulting tip. Receipt: `.ufo/waves/round-55/w1/out/X8Regression/verification-patch-applies-clean.txt`.

```
$ git -C <fresh clone> apply --check <out>/proposed-fix.patch
PATCH APPLIES CLEANLY
$ git -C <fresh clone> apply <out>/proposed-fix.patch && git -C <fresh clone> add -A && git -C <fresh clone> -c user.name=fx -c user.email=fx@invalid commit -m "verify"
verify tip=a2f44773d7472f68d76218651c727b499fe02bbc
 SCORECARD.md               | 2 +-
 registry/hexrun-ledger.tsv | 1 +
 .../e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0.txt | 17 +++++++++++++
```

| command at `a2f44773…` | exit | summary line |
|---|---|---|
| `round41-scorecard-reconcile.py` | 0 | `axes=6 facts=36 … mismatches=0 met=True` |
| `round42-selfdesc-reconcile.py` | 0 | `r41=0 … mismatches=0 maxN=53 met=True` |
| `hexrun-census.py scan` | 0 | `tokens=1962 distinct=350 … upstream_ok=99 … ledger_bad=0 unknown=0` |
| `round43-registry-audit.py` | 0 | `… spot=0 … mismatches=0 met=True` |
| `round43-hexrun-audit.py` | 0 | `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True` |
| `gate-registry-check.py` | 0 | `registered 54 unregistered 0 defective 0` |
| `sources-append-only.py --from 3a600d2f…` | 0 | `no append-only violations` |
| `digest-ledger.py scan` | 0 | `tokens=137 … ledger_bad=0 wrong_unflagged=0 unknown=0` |
| `round54-cited-path-check.py` (frozen C2) | 0 | `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` |

Every counter green on a pristine application of the delivered patch, and the frozen C2 claim counter is byte-for-byte in the state its committed build measurement records.

**One correction to my own first cut of the patch, recorded because the integrator will hit it:** my initial `proposed-fix.patch` was generated with a pathspec (`-- SCORECARD.md registry/hexrun-ledger.tsv`) that silently excluded the new evidence file, and a `git commit -am` of the applied patch then left that file untracked. The result was a *different* red — `hexrun-census` printed `ledger_bad=1 unknown=0` (the ledger row present, its evidence blob absent) and `round43-hexrun-audit` printed `live=0 met=False`. The delivered patch now contains all three files and the verification above uses `git add -A`. The lane's `registry/hexrun-ledger.tsv` is **not** append-only-declared, so the row append is fine, but the evidence blob must be committed with it or the census reads the row as `ledger_bad`.

---

## 5. Scope, integrity and what this seat did not do

- **No lane file was edited in place.** The lane working tree is untouched; `git status --porcelain` in the lane shows only the pre-existing untracked wave files (`.ufo/waves/round-55/w1.ready.partial`, `.ufo/waves/round-55/w1/out/*`) that other seats and the dispatcher created — nothing this seat wrote. The proposed fix lives only as `proposed-fix.patch` in this seat's out dir and as two commits on a throwaway branch of the scratch clone.
- **No frozen artifact was modified.** `tools/round54-replay-code-audit.py`, `tools/round54-cited-path-check.py`, `.ufo/waves/round-55/preregistration.json`, `.ufo/waves/round-55/controls/*`, `.ufo/waves/round-55/c1/battery/*` and `.ufo/waves/round-55/measured/*` are byte-identical to their committed state; the two defects are in `SCORECARD.md` and `registry/hexrun-ledger.tsv`, neither of which the preregistration freezes.
- **No counter was wrapped in a tracer**; no `strace`/`ltrace`; no network fetch beyond the counters' own read-only fleet/GitHub reads.
- **No service was started or stopped.** `bash tools/test-snapshot.sh` starts and tears down its own loopback fixture server inside the test script (`mktemp` work dir, `trap cleanup EXIT`); it left no listener behind. `pgrep -af llama-server` was checked — see §6 — and this seat started no llama-server.
- **The fleet repo, `/home/vgpnk/Projects/shokunin/shokuknow`, sibling lanes and the fleet root were read only.** Nothing was written at the fleet root.
- **Both defects are inherited from the round-55 BASE commit `3a600d2f`,** i.e. the round-54 outside closure. They are not caused by the round-55 freeze's own edits — but they are live at the round-55 freeze tip `9c60eae` and at the round-55 build commit `8abadfed`, and the round-55 build measurement does not cover either standing counter. The integrator should treat them as round-55 integration reds to repair before the wave closes, and should consider whether the round-55 build gate should run the standing regression counters (`round41-scorecard-reconcile.py`, `round42-selfdesc-reconcile.py`, `round43-registry-audit.py`, `round43-hexrun-audit.py`) — the gap that let a round-54 closure defect survive a freeze and a build.

## 6. Leftovers

- Scratch: `rm -rf /fast/scratch/hyaku/kama-r55/w1/X8Regression` after the receipts were copied into this seat's out dir (the operator directive requires the scratch to be removed before the seat finishes). The two fixture commits live only in that scratch clone and disappear with it; the patch file is the durable record.
- `pgrep -af llama-server`: no process was started by this seat (the C1 counter was not run). Recorded in the receipt `leftover-processes.txt`.
