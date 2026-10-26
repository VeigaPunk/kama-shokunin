# S9Registry — round-44 SKILL.md instrument-registry rows

**Verdict: the three round-44 rows are drafted and the gate registers them — `registered 31 unregistered 2 defective 0` (exit 1) becomes `registered 33 unregistered 0 defective 0` (exit 0) with the section appended; one frozen-tool defect found (`tools/release-recheck.py` exits 0, not 2, when `--upstream` is unreadable, emitting 91 all-`TODO` rows).**

Deliverable row text: `.ufo/waves/round-44/w1/out/S9Registry/rows.md` (one `##` section, the five-column table header, three single-line rows in the shape of `SKILL.md` §Round-43 registry completion at line 1378).

## Behavior — what the rows say

| Row | Entry command (verified against `--help`) | Exit map (from source, arms measured) | Pin |
|---|---|---|---|
| Round-44 C1 release re-verification audit | `python3 tools/round44-release-recheck-audit.py --repo <clone> --tip <full-commit> --upstream <llama.cpp clone> [--out <receipt>]` | 0 met / 1 not met / 2 could-not-evaluate (`could-not-evaluate: <err>` on stderr) + argparse 2 | `sha256 87503e18e47d` |
| Round-44 C2 verdict-ledger audit | `python3 tools/round44-verdict-ledger-audit.py --repo <clone> --tip <full-commit> --fleet <fleet repo> [--out <receipt>]` | 0 met / 1 not met / 2 could-not-evaluate + argparse 2 | `sha256 1933e75b2a53` |
| Round-44 release-recheck ledger drafter (tool, not a counter) | `release-recheck.py draft --sources corpus/SOURCES.md --upstream <clone> --release-name b11889 --release-commit <40-hex> [--repo-url <owner/repo>] [--ids S001,S043]`; `release-recheck.py selftest` | draft 0 written (TODO included) / 1 uncaught input error / 2 usage; selftest 0 pass / 1 arm fail / 2 fixture not isolated | `sha256 50e77fa1a3d9` |

Pins are blobs at the freeze commit `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40`; `git diff --stat 77d1bbf5 098df344 -- tools/` is empty, so the working-tree bytes are the same blobs (`pins-and-drafts.out`). No cell names `registry/release-recheck-b11889.tsv`, `registry/verdict-ledger.tsv` or `ggml-org/llama.cpp`: see findings F4/F5 — each would be graded a `missing-path` defect today. The section prose tells the landing commit to add the two ledger paths to the self-test cells once they exist.

## Gates run (commands, outputs, exit codes)

| # | Command | Output | Exit |
|---|---|---|---|
| G1 | `python3 tools/gate-registry-check.py --repo .` (lane tree, no rows) | `registered 31 unregistered 2 defective 0`; `unregistered tools/round44-release-recheck-audit.py`, `…-verdict-ledger-audit.py` | 1 |
| G2 | same, in a scratch `git clone --shared` of the lane with `rows.md` appended to `SKILL.md` (working-tree SKILL.md) | `registered 33 unregistered 0 defective 0` | 0 |
| G3 | `gate-registry-check.py --repo <fixture> --rev 33cf76f948ef` where the fixture commits the lane subset + the three rows | `registered 2 unregistered 0 defective 0` | 0 |
| G4 | three defect arms on the same fixture (`gate-arms.out`) | B empty Exit map → `defective …: empty-exit-map`; C cites `registry/verdict-ledger.tsv` → `defective …: missing-path:registry/verdict-ledger.tsv`; D cites `ggml-org/llama.cpp` → `defective …: missing-path:ggml-org/llama.cpp` | 1 / 1 / 1 |
| G5 | `gate-registry-check.py --repo <clone> --selftest` | `GATE_SELFTEST pass=5 fail=1`, `FAIL lane-tip 098df344d977: exit=1 line='registered 31 unregistered 2 defective 0'` | 1 |
| G6 | `tools/round44-release-recheck-audit.py --repo . --tip 098df344… --upstream <llama.cpp clone>` | `pop=91 rows=0 valid=0 unverified=91 … section=0 met=False` + 91 `detail:` lines | 1 |
| G7 | same with `--repo <non-git dir>` | `could-not-evaluate: git rev-parse --verify HEAD^{commit}: fatal: not a git repository …` (stderr) | 2 |
| G8 | `tools/round44-verdict-ledger-audit.py --repo . --tip 098df344… --fleet <fleet>` | `rows=0 valid=0 missing=204 … summary=0 axes=0 met=False` | 1 |
| G9 | same with `--repo <non-git dir>` | `could-not-evaluate: git -C … rev-parse --verify HEAD^{commit}: fatal: not a git repository …` | 2 |
| G10 | `tools/release-recheck.py selftest` | five `PASS` arms, `selftest pass=5 fail=0` | 0 |
| G11 | `tools/release-recheck.py draft … --upstream <absent>` | header + 91 rows, every `pin_blob=-`, `release_blob=-`, `verdict=TODO` | **0** (see F1) |
| G12 | `tools/release-recheck.py draft --sources <absent> …` | `FileNotFoundError: [Errno 2] …` traceback | **1** (see F2) |
| G13 | `tools/release-recheck.py` (no subcommand) | `error: the following arguments are required: cmd` | 2 |

Gate exit codes for G1–G4 were read as `$?` after the unpiped invocation; the "must be able to fail" legs are B/C/D, so G2's clean line is not vacuous. `registered 33` = the 31 pre-existing rows plus the two `tools/round44-*.py` counters; `tools/release-recheck.py` is outside the gate population (`tools/round<N>-*.py`), which is why the fixture arm counts 2.

Row shape was copied from `SKILL.md:1380-1382` (header + separator) and `SKILL.md:1386` (cell style), with `grep -n 'Round-43 registry completion' SKILL.md` → `1378`.

## Findings

**F1 (defect, medium) — `tools/release-recheck.py` reports an unreadable clone as success.**
`tools/release-recheck.py:23` says `Exit 0 written (TODO rows included), 2 a git or input failure.` but `blob()` (`:47-49`) and `show()` (`:52-54`) pass `check=False`, so `cmd_draft` (`:189`) cannot see a git failure: every blob reads `-`. Repro (G11): `python3 tools/release-recheck.py draft --sources corpus/SOURCES.md --upstream /nonexistent --release-name b11889 --release-commit d854d98b…` → exit **0**, 91 rows, 91 `TODO`. A mistyped `--upstream` therefore produces a full draft that looks like "nothing could be relocated" rather than "the clone is wrong". Proposed fix (do not apply in place — frozen):
```python
def cmd_draft(a):
    try:
        git(a.upstream, "rev-parse", "--git-dir")
        git(a.upstream, "cat-file", "-e", a.release_commit + "^{commit}")
    except (SystemExit, EvalError) as e:
        sys.stderr.write(f"input failure: {e}\n"); return 2
    try:
        text = open(a.sources).read()
    except OSError as e:
        sys.stderr.write(f"input failure: {e}\n"); return 2
```
**F2 (defect, low) — same docstring, other direction.** An absent `--sources` is an uncaught `FileNotFoundError` (`:190`) and exits **1**, not the documented 2 (G12). Same fix as F1.

**F3 (operability note, no defect) — the gate's `--selftest` lane arm cannot go green before the rows commit.** `tools/gate-registry-check.py:334-335` derives `lane_root` from `__file__` and evaluates `master`, ignoring `--repo`; measured `FAIL lane-tip 098df344d977` (G5) with the rows only in a working tree. Expect `GATE_SELFTEST pass=6 fail=0` only after the landing commit puts the section on the lane's `master`. The five fixture arms pass.

**F4 (gate behaviour to design around) — an owner/repo token in a cell is graded as a repo path.** `gate-arms.out` arm D: `ggml-org/llama.cpp` → `missing-path:ggml-org/llama.cpp`. The drafted rows therefore write `<owner/repo>` and `<llama.cpp clone>`.

**F5 (gate behaviour to design around) — rows must not cite a ledger before it exists.** Arm C: `registry/verdict-ledger.tsv` → `missing-path`. Add `registry/release-recheck-b11889.tsv` and `registry/verdict-ledger.tsv` to the self-test cells in the commit that lands them (instructions in the section prose), mirroring the round-43 rows' control-receipt citations.

## Touched surfaces

- Written (all inside the lane's out directory, all new): `rows.md` and the ten receipts listed below.
- Not written: lane tree, lane git index/jj state, fleet repo, sibling lanes, `/fast/scratch/hyaku/kama-r44/shared/llama.cpp`. No `git add`/`commit`/`checkout` in any real repo; the only commits were made in a `mktemp -d` fixture whose `rev-parse --show-toplevel` was checked equal to itself before the first commit. Scratch (`/fast/scratch/hyaku/kama-r44/S9Registry`) removed. No pacman, no tool installs. No services, no subagents.

## Out of scope / not done

- Rows were not appended to `SKILL.md` (read-only lane); the L1 must paste `rows.md` at the end of the file.
- No base/measured receipt paths in the rows for the C1/C2 counters (no committed `controls/` output exists for round 44 yet). The measured values are quoted inline instead, as round-43 rows do for their base receipts; add the paths once `X1R*` seats land receipts.

## Artifacts

- `.ufo/waves/round-44/w1/out/S9Registry/rows.md` — the three rows (deliverable)
- `.ufo/waves/round-44/w1/out/S9Registry/help.out` — `--help` of all three tools
- `.ufo/waves/round-44/w1/out/S9Registry/c1-exitmap.out` — G6, G7
- `.ufo/waves/round-44/w1/out/S9Registry/c2-exitmap.out` — G8, G9
- `.ufo/waves/round-44/w1/out/S9Registry/drafter-exitmap.out` — G10, G11, G12, G13
- `.ufo/waves/round-44/w1/out/S9Registry/gate-arms.out` — G1, G2, and defect arms B/C/D
- `.ufo/waves/round-44/w1/out/S9Registry/gate-fixture-committed.out` — G3
- `.ufo/waves/round-44/w1/out/S9Registry/gate-selftest-fixture.out` — G5
- `.ufo/waves/round-44/w1/out/S9Registry/gate-baseline-lane.out` — G1 alone
- `.ufo/waves/round-44/w1/out/S9Registry/gate-rows-appended-lane-clone.out` — G2 alone
- `.ufo/waves/round-44/w1/out/S9Registry/pins-and-drafts.out` — blob sha256 pins, empty tools diff, draft tallies (C1 91 rows: 81 holds / 4 unchanged-file / 6 TODO; C2 204 rows: 102 self / 102 outside)
