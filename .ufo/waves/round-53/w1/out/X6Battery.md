# X6Battery — round-53 regression battery at the build

**Verdict: no lost capability.** The whole round-52 battery reproduces at `c22602bd` — every round-52 claim counter keeps its verdict (`c1`, `c2`, `r48c2`, `r49c1`, `r50c1`, `r51c1`, `r51c2`, `cap`, `digest`, `pointer`, `aoa-selftest`, `cr-selftest` verdict-identical; only `tip=` and ephemeral detail lines move) and the two round-53 counters are `met=True` in an independent run. Of the 9 counters whose verdict lines differ, 5 carry **4 distinct harms** (2 introduced by the build, 2 inherited at the base `4229ea1b` and not fixed by it) and 4 are **supersessions**; a single 4-file patch, validated on a fixture tip, clears all four harms (`gate` `registered 52 unregistered 0`, `r41`/`r42`/`r43` `met=True`, `hexrun` `unknown=0`, `C2` still `met=True`).

## Method

1. Copied `.ufo/waves/round-52/measured/measure.sh` to `out/measure.sh` and changed only `HERE`, `BASE` (`4229ea1b`), `S` (my scratch) plus two `run` lines (`r53c1`, `r53c2`); the exact diff is `out/measure-vs-round52.diff` (28 lines, nothing else touched).
2. Ran it at `c22602bd8d83ab26349d1087e916ca537ee4f9d1` on a fresh `git clone` of the lane:

```
$ S=/fast/scratch/hyaku/kama-r53/X6Battery; TMPDIR=$S bash $S/measure.sh c22602bd8d83ab26349d1087e916ca537ee4f9d1 ""   # exit 0, 145 s
c1: bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True exit=0
c2: fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True exit=0
gate: registered 50 unregistered 2 defective 0 exit=1
r41: axes=6 facts=36 hash_bad=1 lines_bad=0 run_bad=1 ... mismatches=2 met=False exit=1
r42: r41=2 ... mismatches=2 maxN=52 met=False exit=1
r43: unreg=2 defect=0 ... selftest=1 ... spot=1 ... mismatches=4 met=False exit=1
hexrun: tokens=1951 distinct=342 ... unknown=1 exit=1
r53c1: bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True exit=0
r53c2: fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True exit=0
```
   `r51c1` exited 1 with `own=0 met=False` exactly as in round 52 (the documented memfd supersession); every other counter exited 0. Full command lines and exits are in the per-counter receipts `out/*.out`.
3. Compared against the round-52 measured receipts (`35e3b1dc`) with `out/compare.py` (drops the `$` header and `detail:` evidence lines, normalises the scratch path and timestamps), output `out/verdict-diff.txt`, classification table `out/verdicts.tsv`.
4. Re-ran the regressed counters at the base `4229ea1b` in the same clone (`out/base-status.out`) and at the build with `--details` (`out/build-diagnosis.out`) to separate build-introduced from inherited harms.

Cross-check: my battery's 23 shared counters reproduce the L1's `measured/*-build.out` values exactly (including `c1`→`r52c1` `met=True`, `c2`→`r52c2` `met=True`, `r51c1` `own=0 met=False`), and `r53c1`/`r53c2` are verdict-identical to `measured/c1-build.out`/`c2-build.out`.

## Verdict differences

| counter | class | difference |
|---|---|---|
| `gate` | **harm, build** | `unregistered 0`, exit 0 → `unregistered 2`, exit 1 (`tools/round53-cited-path-check.py`, `tools/round53-replay-code-audit.py`) |
| `r41` | **harm, build** (`hash_bad`) + **inherited** (`run_bad`) | `mismatches=0 met=True` → `hash_bad=1 run_bad=1 mismatches=2 met=False` |
| `r42` | consequence of `r41` | `mismatches=0 met=True` → `r41=2 mismatches=2 met=False` |
| `r43` | **harm, build** (`unreg`, `selftest`) + **inherited** (`spot`) | `unreg=0 … selftest=0 … spot=0 … mismatches=0 met=True` → `unreg=2 … selftest=1 … spot=1 … mismatches=4 met=False` |
| `hexrun` | **harm, inherited at base** | `unknown=0`, exit 0 → `unknown=1`, exit 1 |
| `klr-selftest` | supersession | `pass=36` → `pass=43` (+7 `pass code-*` cases, none lost) |
| `census` | supersession | +1 line `kama W04 S509 duplicate url …ggml-backend-reg.cpp across scopes`; exit 0 both (94 W04 rows already in the round-52 receipt) |
| `sao` | supersession (seat-mandated base move) | `added S500…S505` → `added S506…S509`, `no append-only violations` both |
| `aoa` | supersession | `commits=352 files=99` → `commits=357 files=101`; restored/ungraded/disclosed/bad all identical |
| `live-selftest` | volatile only | same `selftest: ok`, ephemeral listener ports differ |
| `c1`, `c2`, `cap`, `cr-selftest`, `digest`, `pointer`, `r48c2`, `r49c1`, `r50c1`, `r51c1`, `r51c2`, `tally`, `aoa-selftest` | identical | only `tip=`, `rev=`, `repo=` (scratch path) and `detail:` lines differ |

`pointer-results.out` (round-52 D3 receipt at `ade21a45`) was not re-run: it is the same `planned-pointer-check.py SCORECARD.md` instrument, and `pointer.out` is verdict-identical at the build, so there is nothing to compare there.

## Harms

### H1 (build) — the two round-53 counters are unregistered, and that alone fails `r43.selftest`

`tools/gate-registry-check.py --rev c22602bd…` → `registered 50 unregistered 2 defective 0`, exit 1. `SKILL.md` has no `## Round-53 instrument registry` section (round-52 rows end at `SKILL.md:1550`). Two consequences beyond the gate line: `round43-registry-audit.py` reports `unreg=2` **and** `selftest=1`, because `gate-registry-check.py --selftest` arm 6 (`tools/gate-registry-check.py:331-349`) evaluates the lane's `master` branch — not `--rev` — so it fails on the same two tools (`FAIL lane-tip bc8e6e7f1c53: exit=1 line='registered 50 unregistered 2 defective 0'`, `out/build-diagnosis.out`). Registering the tools clears both legs; no separate fix is needed.

Proposed fix (full text `out/proposed-skill-round53-registry.md`): a `## Round-53 instrument registry` section with one five-column row per counter (exit maps, pinned digests, write scope) appended after the round-52 rows. Validated: `gate` → `registered 52 unregistered 0 defective 0`, exit 0.

Note for the integrator: the section must **not** cite `.ufo/waves/round-53/w1/out/…` or the uncommitted `measured/*.out` — my first draft did, and C2 caught it (`cited=687 unresolved=16 undisclosed=2 met=False`). The wording I ship cites no uncommitted path and C2 stays `met=True` (`cited=685 unresolved=14 disclosed=14`).

### H2 (build) — `SCORECARD.md:16` cites a `SKILL.md` digest the build invalidated in place

`round41-scorecard-reconcile.py` detail: `depth sha256 SKILL.md cited cfcc4291… observed a6a19d13…`. The build's in-place `SKILL.md` corrections (`SKILL.md:113`, `SKILL.md:895`) changed the file's bytes; the depth axis row still pins the pre-build digest. Command: `cd <clone at c22602bd> && python3 tools/round41-scorecard-reconcile.py` → `hash_bad=1 … met=False`, exit 1 (also `r42` `r41=2`).

Proposed fix (`out/proposed-fixes.diff`, validated in `out/proposed-fixes-validation.out`): re-anchor the digest, line count and `grep -c '^## '` count in that one row. **Re-anchor last**: adding H1's registry section changes all three values again — with my proposed section the row becomes sha256 `fd22c452…935c`, `(1568 lines)`, `→ 41`. Without any `SKILL.md` change the correct values are the build's: `a6a19d13…add`, `1559`, `40`.

### H3 (inherited at base) — `hexrun unknown=1`

Token `3945011969fbc4b0bdcf4c856626d016068558ec` (a fleet-repo commit) cited at `corpus/lessons/round-52-verifier-spotcheck.md:23` is `class=unknown`; `hexrun-census.py` exits 1. It is **not** build-introduced: at `4229ea1b` the same token is already `unknown=1`, exit 1, `tokens=1943 distinct=339` (`out/base-status.out`); the build only adds 8 token occurrences (`1951/342`) with no new unknown.

Fix already staged in the lane worktree but not at `c22602bd`: `registry/hexrun-ledger.tsv` (working-copy line 114, `upstream` row) and `.ufo/waves/round-53/hexrun-evidence/3945011969fbc4b0bdcf4c856626d016068558ec.txt` are untracked/uncommitted in the lane at report time (`git cat-file -e c22602bd:…` → exit 128, `git grep -c … -- registry/hexrun-ledger.tsv` at the build → no match, `out/build-diagnosis.out`). Committing them clears the leg: validated → `upstream_ok=98 unknown=0`, exit 0 (`out/hexrun-fix-validation.out`). The evidence file contains both the token and the row's `repo` cell text (`vgpnk/shokunin (fleet)`), which is what the frozen `upstream` rule re-checks.

### H4 (inherited at base) — calibration row states 38 spot-check files, the tree holds 39

`round41-scorecard-reconcile.py` detail: `calibration run … no stdout line == '38'`; `round43-registry-audit.py` detail: `spot: calibration row states 38, tree holds 39`. `corpus/lessons/round-52-verifier-spotcheck.md` landed at the **base** `4229ea1b`, after the round-52 receipts were taken at `35e3b1dc`; at `4229ea1b` alone: `r41 run_bad=1 met=False`, `r43 spot=1 met=False` (`out/base-status.out`), so no round-52 receipt could have shown it. The build neither causes nor fixes it.

Fix: `SCORECARD.md:18` `→ `38`` → `→ `39`` (included in `out/proposed-fixes.diff`). Validated: `r41`/`r42` `met=True`, `r43 spot=0`.

## Validated patch set

`out/proposed-fixes-full.diff` = 4 files against `c22602bd` (2 SCORECARD rows, the SKILL registry section with its re-anchored digest, the hexrun ledger row, the 17-line evidence file). Applied on a detached fixture commit in my scratch clone with a fixture identity and `master` moved to it, all six affected counters are clean (`out/proposed-fixes-full-validation.out`):

```
gate:  registered 52 unregistered 0 defective 0   exit 0
r41:   axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 mismatches=0 met=True  exit 0
r42:   r41=0 … mismatches=0 maxN=52 met=True  exit 0
r43:   unreg=0 … selftest=0 … spot=0 … pop=52 registered=52 mismatches=0 met=True  exit 0
hexrun: tokens=1951 … upstream_ok=98 … unknown=0  exit 0
r53c2: fixture=1 lane=1 scenarios=8/8 cited=685 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True  exit 0
```

The fixture commits (`580fab19`, `606f4ffa`, `d8d8eecd`) exist only in `/fast/scratch/…`, which is deleted; they are not lane objects and must not be cited as evidence.

## Round-53 claims at the build (independent run)

| counter | verdict at `c22602bd` | vs L1 receipt |
|---|---|---|
| `r53c1` (C1 operability 8→8) | `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`, exit 0; each leg `8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem …, 13 root-owned host files` | verdict-identical to `measured/c1-build.out` |
| `r53c2` (C2 calibration 7→7) | `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`, exit 0 | verdict-identical to `measured/c2-build.out` (`fleet=` rev differed: `d2a6c59a` mine vs `ee9f7341` theirs) |

## Limits / risks

- `detail:` lines carry pids, ports, dev:inode and nonces and are not reproducible; all verdict lines reproduced across two independent full runs (mine and the L1's).
- The fleet repo is moving under the C2 counter: three C2 runs in this seat saw `fleet=d2a6c59a`, `70df4d76`, `305a7cac`. The verdict never moved, but a receipt's `fleet=` value is a moving anchor and should not be quoted as a fixed rev in SCORECARD prose.
- The lane worktree is **not** the build commit at report time (`HEAD` `bc8e6e7f`, plus modified `SKILL.md`, `corpus/QUALITY.md`, `registry/hexrun-ledger.tsv`, `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py` and untracked receipts/evidence). I measured `c22602bd` from a clone and classify against that commit only; in particular the H3 ledger row exists in the worktree but is invisible at the build.
- `census` (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin`) reads the lane working tree, not the clone; the S509 row it flags is committed at the build, so the flag is not a worktree artefact.
- Not run: `pointer-results` (see above); no `sha256` re-check of the round-48 receipts beyond what the counters do.
- Tooling: nothing installed or upgraded; no `pacman`; no service started or stopped by hand (all live counters start and tear down their own loopback servers — `pgrep -c llama-server` → 0 after the battery). The two fixture commits used `-c user.name=fx -c user.email=fx@invalid` only after `git rev-parse --show-toplevel` printed the scratch clone.

## Files written

- `.ufo/waves/round-53/w1/out/X6Battery.md` (this report)
- `.ufo/waves/round-53/w1/out/X6Battery/` — `measure.sh`, `measure-vs-round52.diff`, `compare.py`, `verdict-diff.txt`, `verdicts.tsv`, the 25 battery receipts (`c1.out` … `r53c2.out`, `census.out`), `base-status.out`, `build-diagnosis.out`, `proposed-fixes.diff`, `hexrun-fix-validation.out`, `proposed-fixes-validation.out`, `proposed-skill-round53-registry.md`, `proposed-fixes-full.diff`, `proposed-fixes-full-validation.out`
