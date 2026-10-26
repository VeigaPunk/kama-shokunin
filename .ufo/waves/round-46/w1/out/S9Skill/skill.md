<!-- Drafted by seat S9Skill (round 46, kama-r46-w1). Paste the block between the
     BEGIN/END markers below into /home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md
     at end of file (after the `## Round-45 instrument registry` table). Nothing else
     in this file is insertion content; the appendix is evidence, not prose for SKILL.md. -->

<!-- BEGIN kama-shokunin/SKILL.md addition -->
## Round-46 instrument registry (freshness re-verification, append-only calibration)

Rows for the round-46 counters and the append-only capability they grade (claim C2; considerthese 2026-10-26 proposal 1). Same columns as `## Local gate/probe registry`. Drafted by seat S9Skill from each tool's docstring and measured exits at lane commit 4a2a4d55, where the two counters still read `met=False`: the C1 ledger and the SCORECARD capability row land later in this wave. Re-measure every number below; only the tool contract is frozen.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-46 C1 release re-verification audit (freshness) | measurement: `python3 tools/round46-release-recheck-audit.py --repo <clone> --tip <full-commit> --upstream <llama.cpp clone holding b11906> [--out <receipt>]` | 0 met, prints `pop=P rows=R valid=V unverified=U unchanged=a holds=h reworded=w drifted=d removed=r flags_missing=F section=S newrow=N met=True` then one `detail:` line per unverified row, unflagged drifted/removed row or missing section/new row, and writes the same text to `--out`; grades `registry/release-recheck-b11906.tsv` against the population of `corpus/SOURCES.md` at base 0163fea2 and release b11906 = 4d71b42fd87db24b8b7c808c151b713aa4459cfd, so a `removed` or `drifted` verdict needs both witnesses and a >= 40-char note; 1 not met, the same line with `met=False` (measured at 4a2a4d55 before the ledger: `pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 newrow=0 met=False`, exit 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr from an EvalError raised by `git rev-parse` of `--tip`, `git cat-file -e` of the release or a population pin (measured: an `--upstream` without b11906 prints `could-not-evaluate: git cat-file -e 4d71b42f…`, exit 2) or an unreadable base SOURCES; argparse missing or unrecognized `--repo`/`--tip`/`--upstream` also exits 2, and an uncaught exception leaves exit 1 with no summary | no `--selftest`; `--help` exits 0; sha256 `502e6f57036f`; pre-ledger control `.ufo/waves/round-46/controls/base.c1.out` at tip 0163fea2 reads `pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 newrow=0 met=False`, and the same counter at 4a2a4d55 prints that identical summary line over the same 91 ids | read-only on `--repo` and `--upstream`; `--out` writes only the receipt path it is given |
| Round-46 C2 append-only calibration audit | measurement: `python3 tools/round46-append-audit-check.py --repo <clone> --tip <full-commit> [--out <receipt>] [--scratch <dir>]` | 0 met, prints `tip=<full>` then `selftest=0|1 fixture=0|1 lane=0|1 table=0|1 lane_events=E lane_unrestored=U lane_partial=P met=True`, one `detail:` line per failed leg and one `event:` line per lane event, and writes the same text to `--out`; the legs are the graded tool's `--selftest` (n >= 6, fail 0), a random-content fixture repo whose content it cannot know in advance, an independent recomputation of the lane history, and a SCORECARD table line naming `append-only-audit` whose last cell is 46; 1 not met, the same line with `met=False` (measured at 4a2a4d55: `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False`, exit 1, only the table leg failing); 2 could not evaluate, `could-not-evaluate: <err>` on stderr from an EvalError raised by `git rev-parse` of `--tip` (measured: `--tip deadbeefdeadbeef` exits 2); argparse missing or unrecognized `--repo`/`--tip` also exits 2, and an uncaught exception leaves exit 1 with no summary | no `--selftest` of its own, it runs the graded tool's (measured `AOA_SELFTEST pass=10 fail=0`, exit 0); `--help` exits 0; sha256 `4dcfbe1063d6`; pre-tool control `.ufo/waves/round-46/controls/base.c2.out` at tip 0163fea2 reads `selftest=0 fixture=0 lane=0 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False`, listing `dd9f5dc6` SCORECARD 24/31 partial and `0718b6ab` SCORECARD 2416/2417 partial; fixture bytes are random per run, so only the event counts are pinned | read-only on `--repo`; fixture repos under `--scratch` or `$TMPDIR`, removed on exit; `--out` writes only the receipt path it is given |
| Round-46 append-only self-description audit (claim C2 capability) | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--threshold <n>] [--files <a,b,...>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | 0 no event partial or unrestored, text lines `event <commit12> <file> deleted=N restored_at_tip=K status=S restored_by=<commit12 or ->` then `summary commits=C events=E restored=R partial=P unrestored=U`, and `--json` prints `to`, `threshold`, `files`, `commits`, `events` and `summary` with full commit ids; 1 at least one event partial or unrestored (measured on this lane at 4a2a4d55: 294 commits, 5 events, 3 restored, 2 partial, 0 unrestored, exit 1); 2 could not evaluate, `could-not-evaluate: <err>` on stderr for `--threshold` below 1 or a `--repo` git cannot read, both measured at exit 2 | `AOA_SELFTEST pass=10 fail=0` measured, exit 0, over no-deletion, below-threshold, exact-threshold-unrestored, restored-later, partial, undeclared-file, declared-file-removed, to-earlier-rev, merge-first-parent and threshold-flag; `--help` exits 0; sha256 `793dab9ffe0c`; the event definition is pinned by `.ufo/waves/round-46/preregistration.json`: commits in `git rev-list --topo-order --reverse`, diff against the first parent, `-` lines minus the header, >= 20 deleted lines per (commit, file), the five declared files only; `tools/sources-append-only.py` is the round-18 predecessor and does not compute `restored_by` | read-only on `--repo`; selftest fixtures under `--scratch` or `$TMPDIR`, removed on exit |
<!-- END kama-shokunin/SKILL.md addition -->

## Appendix — gate proof and measurements (not insertion content)

Scratch clone of the lane at the drafting commit, rows applied to `SKILL.md` at end of file:

```text
$ git -C /fast/scratch/hyaku/kama-r46/S9Skill/lane rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r46/S9Skill/lane
$ git -C /fast/scratch/hyaku/kama-r46/S9Skill/lane rev-parse HEAD
4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
$ cd /fast/scratch/hyaku/kama-r46/S9Skill/lane && git checkout -q 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
```

Baseline before the rows (same clone, unmodified `SKILL.md`):

```text
$ python3 tools/gate-registry-check.py
unregistered tools/round46-append-audit-check.py
unregistered tools/round46-release-recheck-audit.py
registered 36 unregistered 2 defective 0
GATE_EXIT=1
```

With the rows applied:

```text
$ python3 tools/gate-registry-check.py
registered 38 unregistered 0 defective 0
GATE_EXIT=0
```

`tools/append-only-audit.py` is not in the gate's population (its `COUNTER_RE`
admits only `.ufo/waves/round-*/count-*.py` and `tools/round<N>-*.py`), so the
row is documentation, not a population claim; 38 = the 36 pre-existing counters
plus the two round-46 counters.

Why each path token in the rows is safe for the gate's `missing-path` rule at
4a2a4d55: the cited tokens are `tools/round46-release-recheck-audit.py`,
`tools/round46-append-audit-check.py`, `tools/append-only-audit.py`,
`tools/sources-append-only.py`, `corpus/SOURCES.md`,
`.ufo/waves/round-46/preregistration.json`,
`.ufo/waves/round-46/controls/base.c1.out`, `.ufo/waves/round-46/controls/base.c2.out`
— all exist at that revision. `registry/release-recheck-b11906.tsv` does **not**
exist there yet, so it is named only in the Exit-map cell, which the gate does
not scan for paths; it will exist at the round-46 measured tip.

Measured exits used by the rows (all re-run in the clone above):

| command | exit | first output line |
|---|---|---|
| `python3 tools/round46-release-recheck-audit.py --repo . --tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --upstream /fast/scratch/hyaku/kama-r46/L1/llama.git --out c1.out` | 1 | `pop=91 rows=0 valid=0 unverified=91 … section=0 newrow=0 met=False` |
| same, `--upstream` = lane clone (no b11906) | 2 | stderr `could-not-evaluate: git cat-file -e 4d71b42f…` |
| same, `--upstream` omitted | 2 | argparse |
| `python3 tools/round46-append-audit-check.py --repo . --tip 4a2a4d55…` | 1 | `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False` |
| same, `--tip deadbeefdeadbeef` | 2 | stderr `could-not-evaluate: git rev-parse --verify deadbeefdeadbeef^{commit}` |
| same, `--repo` omitted | 2 | argparse |
| `python3 tools/append-only-audit.py --selftest` | 0 | `AOA_SELFTEST pass=10 fail=0` |
| `python3 tools/append-only-audit.py --repo . --to HEAD` | 1 | 5 `event` lines, `summary commits=294 events=5 restored=3 partial=2 unrestored=0` |
| `python3 tools/append-only-audit.py --threshold 0` | 2 | stderr `could-not-evaluate: --threshold must be >= 1` |
| `python3 tools/append-only-audit.py --repo <missing> --to HEAD` | 2 | stderr `could-not-evaluate: git rev-parse --verify HEAD^{commit}: fatal: cannot change to …` |
| `--help` on all three tools | 0 | — |

Both counters write byte-identical text to `--out` and stdout
(`diff -q c1.out c1-stdout.out` and the same for C2 → no output).

Defect found while measuring (report, not fixed — counters and tools are frozen):
`tools/append-only-audit.py:306` passes `--scratch` straight to
`tempfile.mkdtemp(dir=…)`, so a nonexistent scratch directory raises
`FileNotFoundError` and exits 1 with a traceback instead of the contract's
`could-not-evaluate` exit 2:

```text
$ python3 tools/append-only-audit.py --selftest --scratch /fast/scratch/hyaku/kama-r46/S9Skill/sft
… FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/kama-r46/S9Skill/sft/aoa-dimami0s'
exit 1
$ mkdir -p /fast/scratch/hyaku/kama-r46/S9Skill/sft && python3 tools/append-only-audit.py --selftest --scratch …/sft
AOA_SELFTEST pass=10 fail=0
exit 0
```

Proposed fix (not applied): create the root first and map the failure onto the
declared exit 2, mirroring `tools/round46-append-audit-check.py:197`
(`os.makedirs(root, exist_ok=True)`):

```python
if a.selftest:
    try:
        root = Path(a.scratch or tempfile.gettempdir()).resolve(strict=False)
        root.mkdir(parents=True, exist_ok=True)
        work = tempfile.mkdtemp(prefix="aoa-", dir=str(root))
    except OSError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
```
