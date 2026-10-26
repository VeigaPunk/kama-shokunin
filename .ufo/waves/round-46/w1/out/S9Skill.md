# S9Skill — round-46 SKILL.md instrument-registry rows

**Verdict: PASS.** The three rows are drafted from each tool's docstring and measured exits, and on a scratch clone at `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` with the delivered block applied, `python3 tools/gate-registry-check.py` prints `registered 38 unregistered 0 defective 0` and exits `0` (baseline at the same commit without the rows: `registered 36 unregistered 2 defective 0`, exit `1`). One frozen-tool defect was found and reported, not fixed (`tools/append-only-audit.py:306`, `--scratch` on a nonexistent directory exits 1 with a traceback instead of the contract's exit 2).

## Deliverable

`.ufo/waves/round-46/w1/out/S9Skill/skill.md` — a paste-ready `## Round-46 instrument registry (freshness re-verification, append-only calibration)` section between two HTML-comment markers: heading + one intro sentence + the five-column table with three rows (`Round-46 C1 release re-verification audit`, `Round-46 C2 append-only calibration audit`, `Round-46 append-only self-description audit`). The text between the markers is byte-identical to the block that was applied to the clone (`diff -u` of the extracted block against the applied file: empty, `BLOCK_EQ_SECTION_EXACT`); the rest of that file is an evidence appendix that is not insertion content.

Each row carries what the gate grades: the counter path in the Kind/entry cell, a non-empty Exit map, a Self-test / pinned-values cell with measured values, and a write scope. Exit maps state 0/1/2 plus the argparse exit 2 and the uncaught-exception behaviour (`main` catches only `EvalError`, so any other exception leaves exit 1 with no summary).

## Gate proof (exact invocation and output)

```text
$ git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r46/S9Skill/lane
$ cd /fast/scratch/hyaku/kama-r46/S9Skill/lane && git checkout -q 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
$ git rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r46/S9Skill/lane
$ git rev-parse HEAD
4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050

# baseline, unmodified SKILL.md
$ python3 tools/gate-registry-check.py
unregistered tools/round46-append-audit-check.py
unregistered tools/round46-release-recheck-audit.py
registered 36 unregistered 2 defective 0
GATE_EXIT=1

# rows applied at end of file (block extracted from the deliverable itself)
$ python3 tools/gate-registry-check.py
registered 38 unregistered 0 defective 0
GATE_EXIT=0
```

Receipts: `out/S9Skill/gate.out`, `out/S9Skill/gate-from-deliverable.out`, `out/S9Skill/gate.exit`.

Why `registered 38` and not 39: `tools/append-only-audit.py` is outside the gate's `COUNTER_RE` (`tools/gate-registry-check.py:57-59` admits only `.ufo/waves/round-*/count-*.py` and `tools/round<N>-*.py`), so its row is documentation the gate ignores; 38 = the 36 pre-existing counters + the two round-46 counters. Registering it is still correct for a reader, which is how the mission item phrased it.

## Path-token safety for the gate's `missing-path` rule

The gate scans only the Kind/entry, Self-test and Write-scope cells (`tools/gate-registry-check.py:246`), and every scanned token must exist at the evaluated revision. Tokens used and verified present at `4a2a4d55`: `tools/round46-release-recheck-audit.py`, `tools/round46-append-audit-check.py`, `tools/append-only-audit.py`, `tools/sources-append-only.py`, `corpus/SOURCES.md`, `.ufo/waves/round-46/preregistration.json`, `.ufo/waves/round-46/controls/base.c1.out`, `.ufo/waves/round-46/controls/base.c2.out`.

`registry/release-recheck-b11906.tsv` is **absent** at `4a2a4d55` (measured: `git cat-file -e HEAD:registry/release-recheck-b11906.tsv` fails, while `registry/release-recheck-b11889.tsv` succeeds), so it is named only in the Exit-map cell, which the gate does not scan. If a later round tightens the scan to every cell, that row must be revisited once the ledger exists — it will exist at the round-46 measured tip, so this is a drafting-commit-only constraint, not a permanent wart.

## Measurements behind the rows (all re-run in the clone, receipts in the out dir)

```text
$ python3 tools/round46-release-recheck-audit.py --repo . --tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 \
    --upstream /fast/scratch/hyaku/kama-r46/L1/llama.git --out out/S9Skill/c1-at-4a2a.out
tip=4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 newrow=0 met=False
exit 1                       (91 `detail: S### no ledger row` lines; receipt == stdout)

$ python3 tools/round46-release-recheck-audit.py --repo . --tip 4a2a4d55 --upstream <lane clone, no b11906>
could-not-evaluate: git cat-file -e 4d71b42fd87db24b8b7c808c151b713aa4459cfd^{commit}: fatal: Not a valid object name …
exit 2                       (c1-could-not-evaluate.err)
$ python3 tools/round46-release-recheck-audit.py --repo . --tip HEAD     # --upstream omitted
exit 2                       (argparse)

$ python3 tools/round46-append-audit-check.py --repo . --tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 \
    --out out/S9Skill/c2-at-4a2a.out --scratch <existing dir>
tip=4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False
detail: no SCORECARD table line naming append-only-audit with last cell 46
event: dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 status=partial restored_by=-
event: 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial restored_by=-
event: 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored restored_by=82b5e9d33a19
event: 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_at_tip=375 status=restored restored_by=82b5e9d33a19
event: 0718b6abbda6 corpus/README.md deleted=663 restored_at_tip=663 status=restored restored_by=82b5e9d33a19
exit 1                       (receipt == stdout)

$ python3 tools/round46-append-audit-check.py --repo . --tip deadbeefdeadbeef
could-not-evaluate: git rev-parse --verify deadbeefdeadbeef^{commit}: fatal: Needed a single revision
exit 2
$ python3 tools/round46-append-audit-check.py --tip HEAD                # --repo omitted
exit 2                       (argparse)

$ python3 tools/append-only-audit.py --selftest --scratch <existing dir>
pass no-deletion / below-threshold / exact-threshold-unrestored / restored-later / partial /
     undeclared-file / declared-file-removed / to-earlier-rev / merge-first-parent / threshold-flag
AOA_SELFTEST pass=10 fail=0
exit 0

$ python3 tools/append-only-audit.py --repo . --to HEAD
event … (the five events above)  summary commits=294 events=5 restored=3 partial=2 unrestored=0
exit 1

$ python3 tools/append-only-audit.py --threshold 0
could-not-evaluate: --threshold must be >= 1
exit 2
$ python3 tools/append-only-audit.py --repo <missing> --to HEAD
could-not-evaluate: git rev-parse --verify HEAD^{commit}: fatal: cannot change to '<missing>': No such file or directory
exit 2

$ python3 <each of the three tools> --help
exit 0
```

sha256 (first 12 hex, at `4a2a4d55`): `tools/append-only-audit.py` `793dab9ffe0c`, `tools/round46-release-recheck-audit.py` `502e6f57036f`, `tools/round46-append-audit-check.py` `4dcfbe1063d6` (`tool-sha256.out` has the full digests).

The two lane counts in the rows are the mission's own numbers, re-derived rather than copied: the `deleted=31 restored_at_tip=24` and `deleted=2417 restored_at_tip=2416` pairs match the assignment's `24/31` and `2416/2417` readings, and the three restored events are `LOG.md` 2290/2290, `corpus/QUALITY.md` 375/375, `corpus/README.md` 663/663, all restored by `82b5e9d3`.

## Findings

### D1 — `append-only-audit.py` `--scratch` on a missing directory exits 1 with a traceback, not the contract's exit 2

- Where: `tools/append-only-audit.py:306` — `root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())` runs before any `try`; `--selftest` is the documented path and the C2 counter's `selftest` leg drives it.
- Command that shows it:
  `python3 tools/append-only-audit.py --selftest --scratch /fast/scratch/hyaku/kama-r46/S9Skill/no-such-scratch`
- Observed: `FileNotFoundError: [Errno 2] No such file or directory: '…/no-such-scratch/aoa-cvg2wrgg'`, traceback, **exit 1** (`aoa-selftest-badscratch.out`). The tool's own contract says exit 2 means "could not evaluate"; exit 1 instead asserts "at least one event partial or unrestored", which is a different and wrong claim. `mkdir -p` of the same path makes it exit 0 with `AOA_SELFTEST pass=10 fail=0`.
- Impact on claim C2: none at the measured tip — the counter passes its own `--scratch` (`tools/round46-append-audit-check.py:197` does `os.makedirs(root, exist_ok=True)`) and defaults to `$TMPDIR`, which exists. It bites only a caller who names a nonexistent scratch dir, and it would make a future wrapper misread a path typo as a restoration failure.
- Proposed fix (not applied; frozen file): create the root and map the failure onto the declared exit 2, mirroring the counter:

```python
if a.selftest:
    try:
        asroot = Path(a.scratch or tempfile.gettempdir())
        asroot.mkdir(parents=True, exist_ok=True)
        root = tempfile.mkdtemp(prefix="aoa-", dir=str(asroot))
    except OSError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
```

### D2 — the two round-46 counters have no `--selftest` of their own (informational)

`tools/round46-release-recheck-audit.py` and `tools/round46-append-audit-check.py` both accept `--repo --tip --out` (+ `--upstream` for C1, `--scratch` for C2) and offer no self-verification arm, so the rows say `no --selftest` and pin the frozen control receipts and tool sha256 instead. C2 at least exercises the graded tool's `--selftest`; C1's only non-data check is `--help` exit 0 plus the pre-ledger control. This is a property of the frozen contract, recorded for the closure, not a request to change it.

### D3 — `--out` is not a receipt on failure paths (informational)

Both counters write `--out` only on the met/not-met path (`sys.stdout.write(text)` then `open(a.out,"w").write(text)`); on exit 2 (could-not-evaluate) nothing is written, so a stale receipt from a previous run survives at that path. The rows say "`--out` writes only the receipt path it is given" and do not claim a receipt exists on exit 2. A wrapper that reads a receipt without checking the exit code would read stale bytes; recorded for the closure.

## Touched surfaces

- Written (mine): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/` (skill.md + receipts) and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill.md` (this report).
- Read-only: lane working tree at `4a2a4d55` (`SKILL.md`, `tools/`, `.ufo/waves/round-46/`), the bare upstream clone `/fast/scratch/hyaku/kama-r46/L1/llama.git`.
- Mutated only in scratch: `/fast/scratch/hyaku/kama-r46/S9Skill/lane` (a `--shared` clone; `SKILL.md` edited there, never in the lane). `git status --porcelain` in the lane shows only pre-existing untracked wave dirs plus my two out paths; no lane file was edited, no `git add/commit/checkout/stash/reset`, no jj command, no service touched.
- No tool installed or upgraded this seat (Python 3.14.8, git 2.56.0 as found); no pacman invocation.

## Out of scope (deliberately not done)

- No C1 ledger row was drafted or verified (`registry/release-recheck-b11906.tsv` is another seat's surface); the C1 row pins only the counter's contract and the pre-ledger control.
- No SCORECARD capability row for `append-only-audit` (C2's `table` leg): that is the C2 data seat's edit, and at `4a2a4d55` the leg is legitimately 0.
- The frozen tools, counters, preregistration and controls were not edited; D1-D3 are findings with proposed text, not patches.
- Scratch clone and all `$TMPDIR` fixtures removed after the runs (`rm -rf /fast/scratch/hyaku/kama-r46/S9Skill`).

## Reproduction in one block

```bash
S=/fast/scratch/hyaku/kama-r46/S9Skill; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
cd "$S/lane" && git checkout -q 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
git rev-parse --show-toplevel     # must print $S/lane before anything writes
awk '/<!-- BEGIN kama-shokunin\/SKILL.md addition -->/{f=1;next} /<!-- END kama-shokunin\/SKILL.md addition -->/{f=0} f' \
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/skill.md > "$S/block.md"
printf '\n' >> SKILL.md && cat "$S/block.md" >> SKILL.md
python3 tools/gate-registry-check.py   # registered 38 unregistered 0 defective 0, exit 0
rm -rf "$S"
```

## Artifacts

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/skill.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/gate.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/gate-from-deliverable.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/gate.exit
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/c1-at-4a2a.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/c1-stdout.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/c1-could-not-evaluate.err
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/c2-at-4a2a.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/c2-stdout.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/c2-could-not-evaluate.err
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/aoa-selftest.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/aoa-selftest-badscratch.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/aoa-lane.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/aoa-lane.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/aoa-threshold0.err
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/tool-sha256.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Skill/gate-help.out
