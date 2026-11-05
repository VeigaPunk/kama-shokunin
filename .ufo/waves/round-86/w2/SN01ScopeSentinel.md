# SN01ScopeSentinel — write scope and receipt hygiene (kama r86 w2)

Measured revision: `67eddac89f44e768b670301ea0feff06e766f32d` (lane HEAD, `git -C …/kama-shokunin
rev-parse HEAD` → exit 0). Fleet root HEAD at measurement: `e9e165cb5de07c40c50ef0b63ad092427af8c68e`.
Frozen base `3ff23da3…`, freeze `c07e1f90…`. Author-side advisory only; nothing here admits a claim.
No production file was edited, no git/jj mutation ran anywhere; the only repo-mutating commands were
`git checkout -- tools/round86-rendered-cells.py` **inside my own scratch clone**
(`/fast/scratch/hyaku/kama-r86/SN01ScopeSentinel/fixture`, `rev-parse --show-toplevel` asserted to
equal it before the first command).

Verdict summary: **write scope holds for the three instruments (F8, PASS)**; scope and receipt
hygiene fail on four independent surfaces (F1, F3, F4, F5) and warn on three (F2, F6, F7).

Placement note (this seat): the Report trailer names `.ufo/waves/round-86/w2/SN01ScopeSentinel.md`
while the contract bounds writes to `w2/out/SN01ScopeSentinel/`. This file is at the Report path;
`out/SN01ScopeSentinel/` holds the receipts and a pointer stub, so there is one record and no
byte-identical duplicate (the F3 defect).

---

## Item 1 — fleet-root status and misroot candidates

Command (exit 0, 27 lines at 21:58; 26 lines at 22:05 — the fleet root is being written concurrently):

```
git -C /home/vgpnk/Projects/shokunin status --porcelain
```

Content scan of every changed path (`grep -qiE 'kama|round-86|round86' <path>` over all 27 paths)
yields 6 content matches, none of which is a kama-r86 wave artifact written from the lane:

| path | status | what matches | classification |
|---|---|---|---|
| `.ufo/reports/round-84/kama.md` | ` M` | `kama`, `CloseKamaR84.KamaC1Review` | **MISROOT — destructive (F1)** |
| `.scratch/run15-state.json` | ` M` | `kama`, `KamaR86a2` | fleet run-state, orchestrator-owned (expected) |
| `.ufo/l0-questions.md` | ` M` (clean again by 22:05) | `kama` | fleet L0 question log (expected, churning) |
| `.scratch/closure-kotoba-r86-entry.json` | `??` | `round-86/kotoba.md`, `round-86-verifier-spotcheck.md` | **kotoba** lane r86, not kama (not a misroot) |
| `.scratch/closure-tabi-r63-entry.json` | `??` | `kama.md` (cross-lane pointer) | tabi lane closure entry (not a misroot) |
| `.scratch/run13-state.json` | `??` | `kama` | stale fleet run-state, 2026-10-30 |

### F1 — MEDIUM (destructive): a kama review overwrote the fleet-root round-84 kama report

```
git -C /home/vgpnk/Projects/shokunin diff -- .ufo/reports/round-84/kama.md   # exit 0
-  # kama — round 84 (2026-11-04)            (HEAD, 69 lines)
+  # kama round-84 C1 independent review — CloseKamaR84.KamaC1Review   (worktree, 41 lines)
```

Evidence: `git show HEAD:.ufo/reports/round-84/kama.md | wc -l` → 69; worktree file → 41 lines,
mtime `2026-11-04 12:28:42`. `git grep -l 'CloseKamaR84.KamaC1Review' HEAD` (fleet) → no hit;
`sha256sum` of the worktree file (`c1a41738…`) matches no file in the kama lane
(`grep -rl 'kama round-84 C1 independent review' …/kama-shokunin` → empty), so the review was
written straight onto the fleet path, not copied from a lane out dir. The reviewer id does exist in
lane provenance (`kama-shokunin/.ufo/waves/round-85/w1/out/SN01Scope/receipts/provenance.json`).
Impact: the fleet root's per-lane round-84 report is destroyed and a lane artifact sits in its place —
exactly the "review belongs in the lane out dir" boundary the round's contract draws. Smallest
remediation: restore the tracked bytes (`git -C /home/vgpnk/Projects/shokunin checkout --
.ufo/reports/round-84/kama.md`, owner's call — I did not run it) and land the review under the lane's
own out dir.

### F2 — LOW: stray redirect artifact at fleet root, kama-unrelated

`after` (24 bytes, `2026-11-03 20:05:14`) contains `== SCORECARD diff base-`. Content names neither
kama nor round-86, so it is not a kama-r86 misroot, but it is the same defect class (a shell redirect
resolved against the fleet root). No action taken.

Fleet-root churn observed during my window (same commands, 21:58 → 22:05): `.ufo/l0-questions.md`
went ` M` → clean, `?? .ufo/reports/round-70/kasegi.md` disappeared, `?? .ufo/reports/round-36/kagi.md`
appeared. Any fleet-root receipt taken across a wave is therefore a moving target; snapshot-and-diff
must be inside one window.

## Item 2 — lane status classification

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain   # exit 0, 14 lines at 21:59
```

| path | classification |
|---|---|
| ` M LOG.md` | round-86 publication text, uncommitted (F4b) — not seat evidence |
| ` M SCORECARD.md` | round-86 capability rows, uncommitted (F4b) |
| `?? .ufo/waves/round-86/measured/after/` | **premature** after-measurement receipts (F4) |
| `?? .ufo/waves/round-86/w1-run.err`, `w1.ready.dispatched` | runner/dispatch artifacts (expected) |
| `?? .ufo/waves/round-86/w1/EX02CoupledBinding.md`, `w1/CR01PredicateCritic.md` | report copies at the wave root (convention) but **duplicated inside `out/<seat>/` (F3)** |
| `?? .ufo/waves/round-86/w1/out/` | declared seat outputs (expected) |
| `?? .ufo/waves/round-86/w2-{dispatch,spec}.json`, `w2-run.{out,err}`, `w2.ready{,.dispatched}` | this wave's dispatch artifacts (expected) |
| `?? .ufo/waves/round-86/w2/` | this wave's tree: `out/` + `swarm-registry.json` (expected) |

`.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`:
`git status --porcelain .ufo/state .ufo/watchdog.log MANIFEST.json` → empty, exit 0 (untouched).

### F3 — MEDIUM: two w1 seat reports are stored twice (root + `out/<seat>/`), byte-identically

The wave convention (this seat's own Report trailer and every w2 seat) is: **report at `w2/<seat>.md`,
receipts under `w2/out/<seat>/`**. w2 peers follow it with no duplication
(`ls .ufo/waves/round-86/w2/` → `EX01OriginFixtures.md`, `MT01SelectorMutants.md`, … at the root;
`out/EX01OriginFixtures/` holds `a-identical.out`, `drive.py`, … only). Two w1 seats break it by
keeping the report in both places:

```
sha256sum .ufo/waves/round-86/w1/EX02CoupledBinding.md .ufo/waves/round-86/w1/out/EX02CoupledBinding/findings-note.md
133279b4…  both
sha256sum .ufo/waves/round-86/w1/CR01PredicateCritic.md .ufo/waves/round-86/w1/out/CR01PredicateCritic/CR01PredicateCritic.md
c439b416…  both
```

`w1/CR01PredicateCritic.md` mtime `22:04:00` postdates the `w1/out/CR01PredicateCritic/` directory
(22:03), so the second copy was written after the first. Impact: two byte-identical records with no
pointer naming the authoritative one; both sit in the tree the integration commit will sweep, so a
later edit to one copy silently desynchronises the record. Smallest remediation: keep the root report
(wave convention) and replace the `out/<seat>/` copy with a one-line pointer, or vice versa — either
way one record, one pointer.

### F4 — MEDIUM: `measured/after/*.out` are unbound to a revision, an exit code and a commit

- Bytes: `cat .ufo/waves/round-86/measured/after/c1.out` → single verdict line, **no `exit=` trailer**
  and **no revision**; same for `c2.out`, `c3.out`. The before receipts do carry it
  (`before/c1.out` ends `exit=1`, `before/c3.out` ends `exit=2`, `before/c2.out` ends `exit=1`).
- Provenance: `stat -c '%y' measured/after/c1.out` → `21:57:24`; `LOG.md` → `21:49:02`,
  `SCORECARD.md` → `21:50:25` (both still ` M`, i.e. uncommitted). The plan puts final measurements
  "on committed master after integration"; these were taken mid-wave (w1 seats were still writing at
  22:04) on a dirty tree, and they are untracked.
- Content reproduces: my independent run at `67eddac8` is byte-identical
  (`diff lane-c1.out measured/after/c1.out` → identical for all three legs, receipts in
  `receipts/lane-c*.out`), so the numbers are not in doubt — the *receipt* is.

Smallest remediation: re-capture after integration on the committed tip and append `exit=<code>` plus
`rev=<40-hex>` (or a companion `after/rev` file) to each receipt.

### F5 — MEDIUM: the frozen counter grades the worktree instrument, not the bytes at `--rev`

`.ufo/waves/round-86/count.py:8` claims "Every leg reads committed bytes at `--rev` and delegates to
the committed instrument"; `count.py:46-49` instead runs
`sys.executable, pathlib.Path(args.repo).resolve() / script` — the file on disk. Demonstrated in my
scratch clone at the graded revision (receipt `receipts/forged-worktree-counter.txt`):

```
# append to clone tools/round86-rendered-cells.py:
print("RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85"); raise SystemExit(0)
python3 <lane>/.ufo/waves/round-86/count.py c1 --repo <clone> --rev 67eddac8… --work <scratch>/work3/c1
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
EXIT=0
```

The `REQUIRES_AT_REV` guard (`count.py:38-43`) checks `git cat-file -e rev:path` but the executed
program is the worktree copy, so the guard proves presence, not provenance. Latent today: the
instrument bytes are clean at HEAD (`git -C …/kama-shokunin diff --stat HEAD --
tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py
tools/round81-append-debt.py .ufo/waves/round-86/count.py` → empty, exit 0). Impact: any uncommitted
edit to an instrument forges a green counter receipt with exit 0 and no trace in the receipt.
Smallest remediation: have `count.py` materialize the instrument from `git show <rev>:<script>` into
`--work` and execute that copy (one function, ~5 lines).

## Item 3 — hardcoded `/tmp` and out-of-lane absolute paths

Instruments (no `/tmp` root anywhere; all scratch via `$TMPDIR`/`tempfile`):

```
grep -n -E '/tmp/|/tmp\b|TMPDIR' tools/round86-rendered-cells.py tools/round86-mutant-owners.py \
  tools/round86-pin-origin.py tools/round81-append-debt.py .ufo/waves/round-86/count.py   # exit 0
round86-rendered-cells.py:40  selftest builds fixture trees in $TMPDIR (no git)
round86-mutant-owners.py:41   selftest ... synthetic outputs in $TMPDIR
round86-mutant-owners.py:136  env={**os.environ, "TMPDIR": str(work)}
round86-mutant-owners.py:238  "could-not-evaluate: --work is required (no hardcoded /tmp)"
round86-pin-origin.py:26      selftest builds fixture registers and anchors in $TMPDIR
count.py:50                   env={"TMPDIR": args.work, "PATH": "/usr/local/bin:/usr/bin:/bin"}
```

Committed receipts carry `/tmp` only as prohibition prose:

```
git grep -n '/tmp' HEAD -- .ufo/waves/round-86   # 6 hits, all inside w1-dispatch.json / w1-run.out / w1-spec.json prompts
```

Out-of-lane absolute paths in the instruments: none (`grep -n -E '/home/|/fast/|/opt/|/Users/'
<the four scripts>` → only shebangs).

### F6 — LOW: a wave receipt publishes hardcoded `/tmp` commands

`w1/out/CN01OverlapScan/CN01OverlapScan.md:151-153`:

```
4. `python3 .ufo/waves/round-86/count.py c1 --repo . --rev master --work /tmp/c1`
5. `python3 .ufo/waves/round-86/count.py c2 --repo . --rev master --work /tmp/c2`
6. `python3 .ufo/waves/round-86/count.py c3 --repo . --rev master --work /tmp/c3`
```

That is the defect class the round contract forbids ("No hardcoded /tmp"), published as the
reproduction recipe for all three legs; `--rev master` is also unpinned. Untracked today, so it enters
the tree only if integration copies it. Smallest remediation: replace with `--work
/fast/scratch/hyaku/kama-r86/<seat>/…` and `--rev 67eddac8…` (or drop the block; the instrument
receipts already exist).

### F7 — LOW: the counter replaces the child environment

`count.py:50` passes `env={"TMPDIR": …, "PATH": "/usr/local/bin:/usr/bin:/bin"}` — `HOME`, locale and
proxy variables are dropped. C3 fetches with `urllib.request.urlopen` (`round86-pin-origin.py:63`), so
on any host that needs `HTTPS_PROXY` the leg degrades to `unreachable` for environmental reasons, and
`git`/`python3` resolution depends on that fixed PATH. Works on this host (`command -v git` →
`/usr/bin/git`, `command -v python3` → `/usr/bin/python3`; all three legs green). Smallest
remediation: `env={**os.environ, "TMPDIR": args.work}`.

## Item 4 / F8 — instruments never write into the lane tree (PASS)

Isolated proof (scratch clone at the graded revision; `find -newer` marker taken *after* the status
refresh so the check itself cannot mask a write):

```
git -C <clone> status --porcelain > /dev/null; touch marker2.t0
for leg in c1 c2 c3; do python3 <lane>/.ufo/waves/round-86/count.py $leg --repo <clone> \
  --rev 67eddac8… --work <scratch>/work2/$leg; done          # EXIT=0 0 0
find <clone> -newer marker2.t0 -not -path '*/.git/*' -print   # (empty)
find <clone>/.git -newer marker2.t0 -print                    # (empty)
git -C <clone> status --porcelain                             # (empty)
```

Lane proof, tight window (start `2026-11-04T22:05:27-03:00`, end `22:05:28`):

```
git -C <lane> status --porcelain > tight-before.txt
python3 <lane>/.ufo/waves/round-86/count.py {c1,c2,c3} --repo <lane> --rev 67eddac8… --work <scratch>/work5/{c1,c2,c3}
git -C <lane> status --porcelain > tight-after.txt ; diff tight-before.txt tight-after.txt   # identical
```

Leg exits and verdicts at `67eddac8` (lane and clone identical):
`c1` exit 0 `RENDERED_CELLS facts=3 mismatches=0 … newest_gate=85 newest_closure=85`;
`c2` exit 0 `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`;
`c3` exit 0 `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0`. All three byte-identical to
`measured/after/*.out`.

Hardest cwd case (subject selftest executed with the repo root as cwd, which is how a seat would run
it from the lane): `cd <clone> && … count.py c2 --repo <clone> --work <scratch>/work4/c2` → exit 0,
`find <clone> -newer marker3.t0 -not -path '*/.git/*'` empty, `git status` empty. Writes land only
under `--work`: `work/c2/mutants/{pristine,M2,M3,M4,M5,M6}.py` plus the counter's own
`mkdir(parents=True)` of the `--work` argument. `round86-rendered-cells.py` has **no** write call at
all (`grep -nE 'write_text|open\(|mkdir|unlink|rmtree'` → empty); `round86-pin-origin.py` writes only
inside `tempfile.TemporaryDirectory` (`:184-246`); `round86-mutant-owners.py` writes only
`work/<name>.py` (`:134`).

## F9 — LOW (observation): empty and missing seat outputs at report time

`find .ufo/waves/round-86/w1/out -maxdepth 1 -mindepth 1 -type d` → 8 dirs, of which
`MT02SummaryForgery/` and `SN01MisrootSentinel/` contain 0 files. `w2-spec.json` names 12 seats;
`w2/out/` has 11 dirs — `SC01SourcesCensus` is absent. The plan requires per-seat status "reported
verbatim, including any empty seat output"; that obligation is unmet for these three seats as of
22:05.

## Receipts in this directory

`receipts/fleet-status.txt`, `receipts/before-lane-status.txt`, `receipts/after-lane-status.txt`,
`receipts/clone-before.txt`, `receipts/clone-after.txt`, `receipts/fx-c{1,2,3}.out` (clone runs),
`receipts/lane-c{1,2,3}.out` (lane runs), `receipts/forged-worktree-counter.txt` (F5).

Scratch `/fast/scratch/hyaku/kama-r86/SN01ScopeSentinel/` (one clone) removed after copying.
Tool installs: none — no tool was installed or upgraded for this seat.
