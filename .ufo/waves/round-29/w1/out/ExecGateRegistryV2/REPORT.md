# ExecGateRegistryV2 — proposed `gate-registry-check.py` v2 (round-29 routed repair 4)

Status: implemented, self-tested and measured. No lane file was edited; every
output lives in this directory (untracked `.ufo/waves/round-29/w1/`), plus the
advice file `.ufo/waves/round-29/w1/advice/ExecGateRegistryV2.md`. Scratch
fixtures and a pass-state repo live under
`/fast/scratch/hyaku/kama-r29/w1/ExecGateRegistryV2/`.

Routed defect served: `corpus/lessons/round-28-verifier-spotcheck.md:233-236`
(item 4): v1 is occurrence-only, has no fixture self-test, and does not print
the revision it measured. Item 5's registry defect (map `measurement:` rows to
`gate|probe`; give the retired round-27 row a kind and entry command, or mark
it explicitly non-runnable) is the class this tool now detects — see
§Findings, group A.

## Deliverable

- `gate-registry-check.py` (proposed replacement for `tools/gate-registry-check.py`;
  sha256 `29a83d648f615f2d78a69d182d2204277162e13423bb4e082d5ccd25e87346a6`).
- `fixtures/` — 8 committed fixture cases (`cases/<id>/SKILL.md` +
  `cases/<id>/tracked.txt`) and `fixtures/expected.json` with the expected
  finding-ids **and the sha256 of every fixture input file**
  (`expected.json` sha256 `102754478ecfa33387260460d36d460b387ebd07bc1dedc3df39a825999764fd`).
- `commands.sh` — the exact commands behind every `.out`/`.err`/`.exit` trio.
- `evidence.sha256` — tool, manifest, commands and every fixture file.

### Contract (what v2 checks that v1 did not)

1. **Parses registry tables, not prose.** Every `## ` section of `SKILL.md` is
   read, so every `## Round-NN ... instrument registry` section and the
   `## Local gate/probe registry` home table are covered. A table is a
   registry table iff its header has `Name`, `Kind / entry command`, a
   `Verdict map`/`Exit map` column and a `Self-test` column. At lane master
   `513eba3` this is **16 tables / 45 rows** (decision, error-signature and
   error-code tables are not registry tables and are skipped).
2. **Coverage by row, not occurrence.** Population: every tracked
   `.ufo/waves/round-*/count-*.py` (6 at master) plus every tracked
   `tools/*.py|*.sh` (13 at master). An instrument is covered only when a
   registry row names its path in the `Kind / entry command`, `Name` or
   `Self-test` cell. A prose mention is **not** coverage — that is exactly
   the v1 defect.
3. **Full row fields.** For a row that names a path: kind phrase must start
   with `gate` or `probe` (PROTOCOL §Gate standard, Registry: "Row fields:
   name, `gate|probe`, ..."); the same cell must carry an interpreter-invoked
   entry command; the `Verdict map`/`Exit map` cell must name an exit code
   (or explicitly defer to another row); the `Self-test` cell must name a
   self-test spelling, a fixture spelling, or an explicit absence
   (`none`/`non-runnable`/`no ... self-test`).
4. **`--selftest`** runs the committed fixtures, verifies their pinned
   digests, compares finding-ids with `expected.json` and fails on any
   difference (exit 1) or on a tampered snapshot (exit 2, `snapshot_tampered`).
5. **Prints the revision it measured**: `rev <full 40-hex>` is the first line
   of every verdict (working-tree mode also prints `tree worktree`).

Exit codes: `0` clean, `1` findings, `2` could-not-evaluate. Read-only git:
`rev-parse`, `ls-tree`, `ls-files`, `show` only.

## Evidence (exact)

All runs: `timeout 60 /usr/bin/python3 .ufo/waves/round-29/w1/out/ExecGateRegistryV2/gate-registry-check.py …`.

1. **Self-test — exit 0.**

```
$ … --selftest
selftest: ok (8 committed fixture cases; digests verified)
exit 0                                          (selftest.out/.err/.exit)
```
   Per-case finding-ids (got == want for all 8; `fixtures-cases.out`): a
   complete row produces nothing; `measurement:` produces
   `kind-not-conforming`; the retired row produces `kind-not-conforming` +
   `entry-command-missing`; a prose-only mention produces `no-registry-row`;
   the missing-self-test and missing-verdict cases produce their class; the
   `none` self-test case and the `non-runnable` kind case produce nothing.

2. **Lane master `refs/heads/master` = `513eba3ba51a142c9936553e3a85918345eb5c4c` — exit 1, 21 findings**
   (`lane-master.out`, stderr empty). Working-tree mode gives the same 21
   findings and prints `rev 513eba3…` + `tree worktree` (`lane-worktree.out`).

3. **Could-not-evaluate — exit 2, both measured:** unresolvable revision
   (`bad-rev.err`: `cannot resolve revision '0000…'`) and a non-git directory
   (`notgit-existing.err`: `not a git working tree … fatal: not a git repository`).

4. **Pass state is reachable — exit 0.** Scratch repo
   `/fast/scratch/hyaku/kama-r29/w1/ExecGateRegistryV2/clean-repo` (git commit
   `9e0738795d025b04fad0c44cd76b56877924c214`) with two complete rows:

```
$ … --repo …/clean-repo --rev HEAD
rev 9e0738795d025b04fad0c44cd76b56877924c214
tables 1 rows 2 findings 0
exit 0                                          (clean-repo.out/.exit)
```

5. **A mutated fixture makes the self-test fail — three measured variants**
   (scratch copies, committed fixtures untouched):

| variant | mutation | result |
|---|---|---|
| `mutated-fix-a` | `full-row` SKILL.md kind `gate:`→`measurement:`, digests untouched | `selftest: FAIL snapshot_tampered full-row: … (want bf75afc5…, got 5de8fe27…)`, **exit 2** |
| `mutated-fix-b` | `expected.json` expected id added for `full-row`, digests intact | `finding ids differ; missing=['kind-not-conforming:tools/ok.py#Complete gate']`, **exit 1** |
| `mutated-fix-c` | SKILL.md kind mutated **and** its digest re-pinned | `finding ids differ; … unexpected=['kind-not-conforming:tools/ok.py#Complete gate']`, **exit 1** |

   (a) proves the snapshot-digest gate, (b)/(c) prove the id comparison is
   live rather than digest-only.

6. **Fixture-directory resolution measured**: `--fixtures`, `$GATE_REGISTRY_FIXTURES`,
   `<script dir>/fixtures`, and the repo-root fallback
   `<repo>/tests/gate-registry-check/fixtures` all return
   `selftest: ok (8 … )`, exit 0 (`selftest-repo-fallback.out/.exit`).

## Findings at lane master (exit 1, 21)

`rev 513eba3ba51a142c9936553e3a85918345eb5c4c`; full text in `lane-master.out`.

**A. Routed class (round-28 spot-check item 5) — the expected flags.**
1. `kind-not-conforming:.ufo/waves/round-28/count-c1.py#Round-28 C1 request-field outcomes` — kind `measurement:`.
2. `kind-not-conforming:.ufo/waves/round-25/count-c2.py#Round-25 C2 context-capacity binding (repaired round 28)` — kind `measurement:`.
3. `kind-not-conforming:.ufo/waves/round-27/count-c1.py#Round-27 C1 counter (retired)` — the kind cell holds a path + sha256 + "do not use", no kind.
4. `entry-command-missing:.ufo/waves/round-27/count-c1.py#Round-27 C1 counter (retired)` — no command in that cell.

**B. Same kind rule, older registry sections** (PROTOCOL allows only `gate|probe`):
`…round-16/measure.py#C1 counting command` and `…round-17/c1/mutants.py#C1 mutant grid` and `tests/llamacpp-live/controls.py#C2 live controls` (`measurement:`); `tools/kama-llamacpp-live.py#Live llama.cpp lifecycle` and `#Live llama.cpp lifecycle v2` (`capability:`).

**C. Self-test spelling absent from the row.**
`tools/gate-registry-check.py#Gate registry completeness` (its own row: "occurrence check only" — this is routed defect 4's "record its spelling in the registry row"), `tools/kama-llamacpp-live.py#Live llama.cpp lifecycle` ("receipt gate below"), `tests/probe-verdicts/fault-controls.py#C1 fault controls` (cell says `--list`, though the round-17 correction note names `--selftest`), `tests/llamacpp-live/controls.py#C2 live controls` (`—`), `tests/report-audit/repo-state-grid.py#Repository-state fault grid`, `tests/report-audit/isolation-mutants.py#Isolation mutants`.

**D. Verdict map absent.** `.ufo/waves/round-25/count-c2.py#Round-25 C2 …` — its Exit-map cell prints a summary line and declares no exit codes.

**E. No registry row at all** (tracked instrument, no row anywhere in SKILL.md; prose mentions do not count):
`.ufo/waves/round-17/count-verdicts.py` (prose at SKILL.md:582 — the exact v1 blind spot), `.ufo/waves/round-26/count-c1.py` (prose at :1073), `.ufo/waves/round-29/count-c1.py` (this round's frozen counter; no round-29 registry section exists at master), `tools/kama-context-capacity.py` and `tools/prereg-time-check.py` (absent from SKILL.md entirely).

Rows that pass include every row of the Local gate/probe registry (including
the `none`/`no standalone … self-test claimed` probes), all Round-20 and
Round-21 rows, and the Round-28 echo-recheck row (its self-test cell names the
committed replay fixture).

## Boundary of the verdict

- Population is counters plus `tools/`; scripts under `tests/` are not
  required to have a row, but a row that names any tracked path is checked,
  which is why `tests/*` rows appear in group C.
- Retirement: the kind/entry/self-test rules are waived only when the
  **kind cell** says `retired`/`non-runnable` (spot-check item 5's repair
  option). A `none (retired)` write-scope cell or a prose "retired" does not
  waive them. `RETIRED_ROW_RE` (any cell) waives the self-test rule only.
- Checked fields are the five the routed item names (path, kind, entry
  command, verdict/exit map, self-test/fixture spelling). Pinned-value path,
  write scope and owner are **not** validated. The tool does not verify that
  a named path is tracked, nor that a row's claim about its instrument is true.
- Cycle: the tool grades the registry rows of the instrument that is itself
  `gate-registry-check.py`; it does not run that instrument.
- Finding-ids embed the row `Name` cell (`<class>:<path>#<row name>`), so
  renaming a row changes the id of a row-specific finding. The fixture
  baseline is self-contained, so only human-readable reports are affected.
- v1 contract changes for the integrator: default `--rev` is now `HEAD`
  (`--worktree` restores index+filesystem evaluation); the summary line is
  `tables T rows R findings F` (v1 printed `registered R unregistered U`), and
  exit 1 now means "any finding", not "some counter not named".

## Integration notes

- Lane home: `tools/gate-registry-check.py`; fixtures at
  `tests/gate-registry-check/fixtures/` (found by the resolver, so the row can
  record plain `--selftest`). `tools/` was not touched by this seat.
- Suggested registry row (Round-29 section, 5-column shape):
  `| Gate registry completeness | gate: `python3 tools/gate-registry-check.py [--rev REV] [--worktree]` | 0 clean (no finding); 1 failed (`finding <class>:<subject>` lines); 2 could-not-evaluate (git, revision, SKILL.md, snapshot_tampered) | `--selftest` over 8 committed fixture cases with digests pinned in `fixtures/expected.json`; prints `rev <full hash>` | read-only git |`
- Group E's round-29 counter needs its own row once the Round-29 registry
  section lands (the Scribe seat is drafting it; asked to confirm field text).

## Installs / processes

No tool was installed or updated (channel: none). No `llama-server` was
started, so no port was bound (`ss -ltnp` shows no 48300 listener). The only
writes are this output directory, the advice file and `/fast/scratch/…`.
