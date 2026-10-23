# ExecGateRegistryV2 — round-29 W1, routed repair 4 (not a claim)

## Behavior delivered

Proposed replacement for `tools/gate-registry-check.py` (lane `tools/` untouched):
`.ufo/waves/round-29/w1/out/ExecGateRegistryV2/gate-registry-check.py`
(sha256 `29a83d648f615f2d78a69d182d2204277162e13423bb4e082d5ccd25e87346a6`).

1. Parses every registry-shaped table in `SKILL.md` (header has `Name`,
   `Kind / entry command`, `Verdict map`/`Exit map`, `Self-test`), so every
   `## Round-NN … instrument registry` section plus `## Local gate/probe
   registry` is read. Coverage is by **row**, not occurrence: a tracked
   counter/tool is covered only when a row names its path (kind, name or
   self-test cell). Prose mentions no longer count — the v1 defect.
2. Row rules: kind must start with `gate` or `probe` (PROTOCOL §Gate standard,
   Registry); the kind cell must carry an interpreter-invoked entry command;
   the Exit/Verdict cell must name an exit code; the Self-test cell must name a
   self-test spelling, a fixture spelling, or an explicit `none`/`non-runnable`.
   A row whose **kind cell** says `retired`/`non-runnable` is exempt (spot-check
   item 5's second repair option).
3. `--selftest` over 8 committed fixture cases with `fixtures/expected.json`
   pinning every input file's sha256; tampered input = `snapshot_tampered`
   (exit 2), id difference = exit 1.
4. Prints `rev <full 40-hex>` first on every verdict; `--worktree` also prints
   `tree worktree`.

## Evidence (all files in the out dir; `commands.sh` reproduces)

- Self-test: **exit 0** — `selftest: ok (8 committed fixture cases; digests verified)`.
- Lane master `513eba3ba51a142c9936553e3a85918345eb5c4c`: **exit 1, 21 findings**
  (`lane-master.out`); 16 tables / 45 rows parsed. Worktree mode identical
  (`lane-worktree.out`).
- Exit 2 measured twice: unresolvable revision; non-git directory.
- Pass state reachable: scratch repo commit `9e0738795d025b04fad0c44cd76b56877924c214`
  with complete rows → `rev 9e0738…`, `findings 0`, **exit 0**.
- Mutated fixture fails the self-test: tampered input → exit 2
  (`snapshot_tampered`, wanted vs got digest printed); edited expectation →
  exit 1; edited input with re-pinned digest → exit 1 (`finding ids differ`).

## Findings at master (the L1's decision list)

Expected per round-28 spot-check item 5 (present):
- `.ufo/waves/round-28/count-c1.py#Round-28 C1 request-field outcomes` — `kind-not-conforming` (`measurement:`)
- `.ufo/waves/round-25/count-c2.py#Round-25 C2 context-capacity binding (repaired round 28)` — `kind-not-conforming` (`measurement:`) + `verdict-map-missing` (no exit codes in its Exit-cell)
- `.ufo/waves/round-27/count-c1.py#Round-27 C1 counter (retired)` — `kind-not-conforming` + `entry-command-missing`

Same class, other sections (not routed by items 4/5):
- `measurement:` kinds: `.ufo/waves/round-16/measure.py#C1 counting command`,
  `.ufo/waves/round-17/c1/mutants.py#C1 mutant grid`,
  `tests/llamacpp-live/controls.py#C2 live controls`.
- `capability:` kinds: `tools/kama-llamacpp-live.py#Live llama.cpp lifecycle`,
  `… #Live llama.cpp lifecycle v2`.
- Self-test spelling absent: `tools/gate-registry-check.py#Gate registry
  completeness` (its own row — routed defect 4's "record its spelling in the
  registry row"), `tools/kama-llamacpp-live.py#Live llama.cpp lifecycle`,
  `tests/probe-verdicts/fault-controls.py#C1 fault controls` (cell says
  `--list`, though the round-17 correction names `--selftest`),
  `tests/llamacpp-live/controls.py#C2 live controls`,
  `tests/report-audit/repo-state-grid.py#Repository-state fault grid`,
  `tests/report-audit/isolation-mutants.py#Isolation mutants`.
- No row at all: `.ufo/waves/round-17/count-verdicts.py` (prose only),
  `.ufo/waves/round-26/count-c1.py` (prose only),
  `.ufo/waves/round-29/count-c1.py` (no round-29 registry section yet),
  `tools/kama-context-capacity.py`, `tools/prereg-time-check.py`.

## Integration decisions the L1 owns

1. Where the fixtures live: resolver order is `--fixtures`,
   `$GATE_REGISTRY_FIXTURES`, `<script dir>/fixtures`,
   `<repo>/tests/gate-registry-check/fixtures` (all four measured, exit 0).
   Putting them under `tests/gate-registry-check/fixtures` lets the registry
   row record plain `--selftest`.
2. Contract changes vs v1: default `--rev` is now `HEAD` (`--worktree` for the
   old behaviour); summary line is `tables T rows R findings F` (v1:
   `registered R unregistered U`); exit 1 now means "any finding". Any v1
   consumer that greps the old line must be updated.
3. Whether to repair groups B/C (historical sections) or narrow the population;
   and whether `tools/kama-context-capacity.py` / `tools/prereg-time-check.py`
   get rows or an explicit non-runnable row.

## Risks / limits

- Finding-ids embed the row `Name` cell for row-specific findings; renaming a
  row changes that id (the fixture baseline is self-contained).
- Not validated: pinned-value path, write scope, owner; that a named path is
  tracked; that a row's claims are true. Cycle: the tool grades its own row but
  does not run itself.
- `RETIRED_ROW_RE` waives the self-test rule when any cell says
  `retired`/`non-runnable`/`do not use` — deliberate, but it can excuse a row
  that would otherwise need a spelling.

## Installs / processes

No installs or updates (channel: none). No server started; no port bound
(`ss -ltnp` shows no 48300 listener). Writes: this out dir, this advice file,
`/fast/scratch/hyaku/kama-r29/w1/ExecGateRegistryV2/`.

Coordination: messaged `KamaR29.ScribeInstrumentRegistry` with the exact field
contract and asked for the round-29 row text (round-29 counter row + the v2
gate row) so it can be checked before integration.
