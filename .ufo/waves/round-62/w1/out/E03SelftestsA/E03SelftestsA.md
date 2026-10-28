# E03SelftestsA — cheap bound selftests at the round-62 tip

Seat: advisory leaf (operability axis, build & verify milestone). No commit, no lane-source edit,
no verdict on C1/C2. Frozen claim/control context read from
`.ufo/waves/round-62/controls/freeze.txt` (base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`).

## Environment

- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`; tip `git rev-parse master` =
  `65d7cad0fce90e34de37527cde22e97b63b118bf` (unchanged across both passes).
- Every tool was verified byte-identical to the tip tree before running
  (`git diff --quiet HEAD -- <path>` → clean, and `git rev-parse HEAD:<path>` blobs recorded below),
  so the working-tree edits in flight in the lane (`corpus/SOURCES.md`,
  `tools/round62-c1-counter.py`) are not in any measured byte.
- Python 3.14.8.
- `TMPDIR=/fast/scratch/hyaku/kama-r62/w/E03SelftestsA/tmp` passed explicitly to every invocation
  (never an inherited TMPDIR). Scratch root created with `mkdir -p` and removed at the end
  (receipts copied to `.ufo/waves/round-62/w1/out/E03SelftestsA/` first).
- Tool installs: **none needed**; no pacman transaction attempted (host-wide pause honoured);
  nothing installed or upgraded, so there is no tool/version/channel record to make.

## Result — 5/5 selftests pass, exit 0

Commands run from the lane root, receipts in `out/E03SelftestsA/pass1/` and `pass2/`.

| # | command | tip blob (`HEAD:path`) | exit | pass line (verbatim, final line) | frozen pattern from `registry/capability-claims-r62.tsv` |
|---|---|---|---|---|---|
| 1 | `python3 tools/sources-append-only.py --selftest` | `f269ef0d5dfa15a3bef4e63a1cdecef33ad43be2` | **0** | `45/45 selftest cases passed` | `45/45 selftest cases passed` (row 2, `sources-registry`) |
| 2 | `python3 tools/kama-ollama-evidence.py --selftest` | `d38e2ae6e27f4a8a85e5373f86ceeb5009ace24c` | **0** | `{"schema": "kama-ollama-evidence-selftest/v1", "finding_id": "clean", "verdict_exit": 0, … "passed": 51, "failed": 0, "total": 51, …}` | `"failed": 0` (row 3, `ollama-offline-evidence-replay`) |
| 3 | `python3 tools/gguf-identity.py --selftest` | `ad434b805d36194faf13936df93def0bb5030df5` | **0** | `"status": "passed"` (case_count 30, failed []) | `"status": "passed"` (row 5, `gguf-declared-identity-replay`) |
| 4 | `python3 tools/instrument-agreement.py --selftest` | `b8a3aed4b9a59f0361f5c6f025f37ab45707305f` | **0** | `IA_SELFTEST pass=4 fail=0` | `IA_SELFTEST pass=` (row 7, `instrument-agreement`) |
| 5 | `python3 tools/pin-watch.py selftest` | `2272273ed64a2022cf87dbda100ef5e016cac71e` | **0** | `selftest pass=9 fail=0` | `selftest pass=9 fail=0` (row 8, `pin-watch`) |

Per-invocation pass lines actually emitted:

1. `45/45 selftest cases passed` — 45 `ok:` case lines (identical/status-only/teaches/removed/added/
   reordered/backtick-pipe/escaped-pipe/recheck+used-by/anchor/malformed-width/duplicate-id/
   missing-registry/per-column edits/segment-and-heading variants/refusals), plus the three oracle
   lines (`oracle covers every fixture column`, `compared set without \`opened\` is refused`,
   `non-UTF-8 blob is a parse error`).
2. `"finding_id": "clean"`, `"verdict_exit": 0`, `"scope": "offline-captures-not-runtime"`,
   `"reasons": ["all_cases_matched_expected_exit_and_finding"]`, `"passed": 51`, `"failed": 0`,
   `"total": 51`.
3. `"schema": "gguf-identity-selftest/v2"`, `"status": "passed"`, `"case_count": 30`, `"passed": 30`,
   `"failed": []`.
4. `[PASS] deterministic: agree=3 disagree=0` / `[PASS] nondeterministic: agree=2 disagree=1` /
   `[PASS] declared-volatile: agree=3 disagree=0` / `[PASS] exit-disagreement: agree=2 disagree=1` /
   `IA_SELFTEST pass=4 fail=0`.
5. `PASS numeric-order: exit 1 [...]` / `PASS current: exit 0 [...]` / `PASS build-numbers: exit 1 [...]`
   / `PASS missing-pin: exit 2 [...]` / `PASS unreadable: exit 2 [...]` / `PASS bad-header refused` /
   `PASS option-repo refused` / `PASS traversal-engine refused` / `PASS quantified-group refused` /
   `selftest pass=9 fail=0`.

All five stderr streams were empty (0 bytes; `receipts.tsv` + per-tool `.err` in `pass1/`).

## Retained evidence

- `out/E03SelftestsA/receipts.tsv` — machine table `name · tip_blob · cmd · exit · pattern_expected · pattern_found`;
  all five rows `exit=0` and `pattern_found=1`.
- `out/E03SelftestsA/pass1/*.out` / `*.err` — first pass stdout/stderr per tool.
- `out/E03SelftestsA/pass2/*.out` / `*.err` — independent second pass.
- `out/E03SelftestsA/pass1/status.before` / `status.after` — `git status --porcelain` snapshots around
  the second pass.

Determinism (two independent passes, 10 invocations total):

- every tool `rc=0` in both passes (5/5, twice);
- `cmp` of pass1 vs pass2 stdout: **byte-identical for all five** (no flapping output, so these pass
  lines are re-runnable evidence, not a one-shot sample).

Operation hygiene:

- `diff status.before status.after` → **empty**: the selftests wrote nothing into the lane tree, left no
  `__pycache__`/temp residue, and staged nothing. (Read-only git only; no mutating git/jj command run.)
- scratch `tmp/` directory was empty after both passes — every `tempfile.mkdtemp`/`TemporaryDirectory`
  honoured the explicit scratch TMPDIR and cleaned up.
- Offline/dependency surface checked in source, not assumed:
  `sources-append-only.run_selftest` builds in-memory tables only (its `subprocess` path is the
  real `--from/--to` checker, unreached); `gguf-identity.run_selftest` feeds `io.BytesIO` fixtures;
  `instrument-agreement.selftest` spawns local `sys.executable` fixture scripts under its tempdir;
  `kama-ollama-evidence.run_selftest` spawns `sys.executable -I -B <itself>` over the committed
  `tests/ollama-evidence/cases.json`; `pin-watch` selftest always calls `check(..., tags_dir)` so
  `read_tags` never reaches its `git ls-remote` branch — no network, no live server, no loopback port
  used by any of the five.

## Observations (reported, not judged)

- Across the whole seat the only `git status --porcelain` delta is two untracked sibling-owned paths that
  appeared in the lane during my first pass (`corpus/lessons/round-62.md`, a nested `kama-shokunin/`
  directory, mtime 09:26). They are not mine — the before/after snapshots bracketing the second,
  receipted pass (`status.before`/`status.after`) are byte-identical — and I did not read, write or
  delete them.
- These are the cheap bound selftests only. They exercise parsers/comparators on fixtures; a green run
  is fixture self-consistency, never runtime evidence for C1 or C2, and I make no claim about either
  predicate. (The `finding_id: clean` / `scope: offline-captures-not-runtime` output of item 2 says the
  same thing in its own words.)

## Blockers

None.

E03 tally: selftests 5/5 exit 0 · frozen patterns present 5/5 · invocations 10/10 exit 0 · passes byte-identical 2/2 · lane-tree writes 0 · errors 0

Report: .ufo/waves/round-62/w1/E03SelftestsA.md
