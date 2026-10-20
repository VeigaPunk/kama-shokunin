VERDICT: partial — boxes 2 and 3 can gain genuinely new resolvable pointers from this round's work; box 1 gains content but not its named verifier; box 4 gains only a scope statement; no box reaches `[x]`.

# Rubric applied

- `templates/round-prompt.md:118-119`: "`[x]` only with a named non-author verifier, `[~]` with a resolvable evidence pointer, `[ ]` if untouched."
- `corpus/lessons/round-16-verifier-spotcheck.md:178`: "Do not promote and do not write `[x]` from these receipts; promotion is operator-owned."
- Consequence: all four boxes stay `[~]`. Only the `→` line changes, and only to text whose every anchor opens after L1 commits. No line below says `[x]` or implies promotion.

# What this round actually adds

| Artifact | Evidence class | At this seat's last check, 15:24Z |
|---|---|---|
| `tests/probe-verdicts/check.py` new `served_model_ok` / route keys | code, grader widens | ` M`, sha `0354b632…`; mid-edit, not committed |
| `tests/probe-verdicts/fault-controls.py` (F1–F8) | counting command | present, sha `b4c7b7ca…`, uncommitted |
| `.ufo/waves/round-17/c1/mutants.py` | counting command | absent; `c1/` empty |
| `tests/llamacpp-live/controls.py` (K0–K7) | counting command | absent; `tests/llamacpp-live/` holds only `check-receipt.py` |
| `tools/kama-llamacpp-live.py` v2, `check-receipt.py` v2 path | code | tool unmodified (`b8c5e8d4…`); gate ` M`, sha `a3f939ac…` |
| `tools/sources-append-only.py` | guard | present, uncommitted |
| `SKILL.md` §Round-17, `LOG.md` §round 17, `SOURCES.md` S042–S045 | docs | drafts only; section/rows not in the docs |

Current gap quoted for reference. `SHONEN.md:6`: "no named non-author verifier."; `SHONEN.md:8`: "10/10 `kama-llamacpp-live/v1` checks"; `SHONEN.md:10`: "independent execution review remains open."; `SHONEN.md:12`: "service repair, routing and credentials remain operator/sibling-owned."

# Box-by-box

## Box 1 (`SHONEN.md:5-6`) — content pointer, verifier unchanged

The round's artifacts add the content this box names, if L1 integrates the drafts. The grader gap it closes is real now: `tests/probe-verdicts/check.py:337` copies `served_model` and then never grades it — "for key in (\"verdict\", \"reason\", \"drift\", \"served_model\", \"evidence\"):" — and the pass predicate at `:341-346` ends "and record[\"drift\"] == (record[\"verdict\"] != \"MODEL_OK\")" with no route assertion. Round 16 measured the result: `.ufo/waves/round-16/falsify/advice/MutateHarness.md:20` — "Result: survived 5; killed 0; inconclusive 0."

Two precision traps for the pointer text:

- The new `SKILL.md` section is a registry table plus a proves/does-not-prove table plus an order-of-operations paragraph (`.ufo/waves/round-17/build/drafts/skill-round17.md:1-30`; the table header at `:7` is "| Name | Kind / entry command | Verdict map |"), not a decision table. Do not call it one.
- The new source ids are not settled. `drafts/knowledge-teardown.md:4` says "Provisional sources (L1 assigns final ids and registry rows): S042, S043, S044." and maps S042 to `server.cpp` (`:97`), while `drafts/sources-rows.md:11` maps S042 to "llama.cpp `/health` route handler @ 704366d76" and `:12` maps S043 to the shutdown path. Citing "S042–S045" before L1 assigns ids would resolve to contradictory rows. Verified source content itself is sound: `server-context.cpp:5297` `res->ok({{"status", "ok"}});`, `server.cpp:534` `sigaction(SIGTERM, &sigint_action, NULL);`, `server.cpp:590` `return 0;` in the round-17 pins (`sources/pins.json`).

## Box 2 (`SHONEN.md:7-8`) — strongest pointer, conditional on the live run

The v1 receipt was re-derived by a non-author: `corpus/lessons/round-16-verifier-spotcheck.md:100` "`receipt.json`: 10 checks, all passed." and `:112` "Verdict: operability improved". That is a non-author mark of the *evidence*, not of the box, and the closure forbids promotion.

Round 17's v2 tightens exactly the checks the pointer currently calls "teardown proven":

- v2 has **11** check ids, not ten: `.ufo/waves/round-17/build/make_spec.py:85` "Required v2 check ids exactly: health_ready, models_alias_id, models_owned_by_llamacpp," … `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`, `model_unchanged`; the scout independently states "11 check ids" (`advice/ScoutReceiptSchemaConsumers.md:31`). Do not copy "10/10" into a v2 clause.
- `teardown_graceful` grades harness-initiated SIGTERM plus rc 0 and no SIGKILL. It still does not prove the signal caused the exit: `advice/ProbeSigtermExit.md:40` "rc 0 does NOT distinguish SIGTERM vs SIGINT vs spontaneous exit". Write "graded", not "proven".
- No registered consumer was contacted in either round: `PROVINCE.md:55` "Round-16 note — lane-owned live fixture (2026-10-20)." and `:66` "the three consumers stay `DEAD`". Keep that clause in the pointer.
- [INFERENCE] The v2 live receipt path is not owned by any round-17 item (`spec.json` contains no `round-17/live` path; grep, not semantic search). Use the live variant only if L1 actually writes it; otherwise use the base variant.

## Box 3 (`SHONEN.md:9-10`) — resolvable, execution review still the gap

This is the box the round most improves: a cold reader gets argv, exit map, self-test/list mode and limits per command. But the text must not outrun the drafts. `drafts/skill-round17.md:10` says "Exit codes are NOT SPECIFIED by the wave specification." for `mutants.py`, and `:9` calls one row "gate, PROVISIONAL (file not yet written)"; five rows carry that mark (`:9-14`). Self-description is per tool, not uniform: `:9` "`--list` names the faults", `:10` "`--dry-run` only locates sites", and `--selftest` only on `sources-append-only.py` and `check-receipt.py`.

The box's own gap is an execution review, and the falsify wave is the only place this round can produce it. If a falsify seat runs the documented commands from `SKILL.md` alone, name that advice file in the pointer; if not, the line must say the review is unrecorded. Do not pre-name a falsify file.

## Box 4 (`SHONEN.md:11-12`) — scope statement, not a verification

What is checkable: `PROVINCE.md:45` "kama never writes to `~/.config`, `~/.omp`, or systemd units."; the live tool still refuses registered ports, `.ufo/waves/round-16/live/controls.txt` records `port_34113_exit=2` and `port_8080_exit=2`; the new commands' scopes are stdout / a TemporaryDirectory / a named receipt (`drafts/skill-round17.md:9-14`).

What is not checkable yet, and can falsify a careless line: the landing commit may sweep third-party worktree edits. `advice/ConnectSouji.md:22` calls the `.ufo/state/` ignore "an **uncommitted third-party edit**", and `tools/__pycache__/` is untracked right now (`git status --porcelain`). A pointer that says "the round's commit touches only lane-owned files" is false if L1 stages broadly; the evidence must be the named-path stage (`commit -- <paths>`). Even then this is a scope statement about this round, not a re-verification of PROVINCE's accuracy.

# Exact pointer text L1 can paste

Keep the `[~]` markers and the existing indentation; replace only the `→` lines. Box 2 has two variants; use the live one only if `.ufo/waves/round-17/live/receipt.json` exists at commit time.

```text
- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
      → Content pointer, no named non-author verifier: `SKILL.md` §Round-17 registry and proves/does-not tables; `tests/probe-verdicts/fault-controls.py` and `.ufo/waves/round-17/c1/mutants.py` instrument the grader the Round-16 pair detector left blind; new cited sources are the round-17 rows in `corpus/SOURCES.md` (ids per L1). The verifier gap is unchanged.
- [~] At least one end-to-end domain task executed and logged in LOG.md
      → Evidence pointer: `.ufo/waves/round-17/live/receipt.json` (`kama-llamacpp-live/v2`, 11 check ids) re-derived by `tests/llamacpp-live/check-receipt.py`; `tests/llamacpp-live/controls.py` scores K0 good against K1–K7 bad; `LOG.md` §round 17 records the run and counts. `corpus/lessons/round-16-verifier-spotcheck.md` §C2 re-derived the v1 receipt 10/10. A lane-owned fixture, not registered-consumer reconciliation: the three consumers stay `DEAD`. No non-author mark of the box itself.
- [~] Instructions executable by an agent without oral context
      → Evidence pointer: `SKILL.md` §Round-17 gives each new command's argv and limits, with exits where observed; self-description is per tool (`fault-controls.py --list`, `controls.py --list`, `mutants.py --dry-run`, `sources-append-only.py --selftest`). `mutants.py`'s exit code is not specified and several rows stay PROVISIONAL until L1 observes them; no non-author execution review is recorded.
- [~] No cross-domain bleed (PROVINCE.md still accurate)
      → Scope pointer, not a verification: `PROVINCE.md` §Write boundary is unchanged; `SKILL.md` §Round-17's write-scope column keeps the new commands on stdout, a TemporaryDirectory or a named receipt; `tests/llamacpp-live/controls.py` uses only 127.0.0.1 ephemeral ports and the tool still refuses 8080/34113/registry ports (`.ufo/waves/round-16/live/controls.txt`). The worktree also holds uncommitted `.gitignore`/`AGENTS.md` edits and untracked `tools/__pycache__/`; none is a round artifact. PROVINCE accuracy remains author-asserted.
```

Box 2 base variant (no v2 live receipt): replace the first two clauses with:

```text
      → Evidence pointer: `LOG.md` §round 17 records the C2 work; `tests/llamacpp-live/controls.py` scores K0 good against K1–K7 bad under the frozen and current tool/gate; `.ufo/waves/round-16/live/receipt.json` still re-derives 10/10, a non-author check (`corpus/lessons/round-16-verifier-spotcheck.md` §C2). A lane-owned fixture, not registered-consumer reconciliation: the three consumers stay `DEAD`.
```

# Do not write these

- "10/10 `kama-llamacpp-live/v2`": v2 has eleven ids (`make_spec.py:85`). Read the count from the receipt if a number is used.
- "teardown proven": v2 grades the harness's own SIGTERM record plus rc 0/no SIGKILL; `ProbeSigtermExit.md:40` says rc 0 does not distinguish SIGTERM from self-exit.
- "S042–S045" as final ids: the two drafts disagree (`knowledge-teardown.md:97` vs `sources-rows.md:11-12`); substitute the committed ids.
- "every new command has `--selftest`": only two do; the rest have `--list` or `--dry-run`.
- "check.py grades the whole probe contract": out of C1's scope; `advice/ReviewProbeContractDrift.md:122` "check.py verifies neither the document identity nor `summary.exit`".
- "fault-controls proves no other corruption survives": the draft's own proves/does-not table limits it to the listed faults (`drafts/skill-round17.md`, "does not prove" column).
- Any `[x]`, and any "promoted": the round-16 closure forbids it (`round-16-verifier-spotcheck.md:178`).

# Limitations

- No `lsp` device is mounted: `read xd://lsp` returned "No such tool". Caller/definition/diagnostics checks used literal `grep` + reads only; treat those as textual, not semantic proof.
- The build wave is in flight. `git status --porcelain` at 15:24Z shows ` M tests/probe-verdicts/check.py` (sha `0354b632…`, frozen `b853576e…`), ` M tests/llamacpp-live/check-receipt.py` (sha `a3f939ac…`), ` M .ufo/waves/round-13/measure.py`, `?? tests/probe-verdicts/fault-controls.py` (sha `b4c7b7ca…`), `?? tools/sources-append-only.py`, `?? tools/__pycache__/`, `?? tests/probe-verdicts/__pycache__/`; `tests/llamacpp-live/controls.py` and `.ufo/waves/round-17/c1/mutants.py` do not exist. Every statement about their behaviour is [INFERENCE] from `.ufo/waves/round-17/build/make_spec.py` and the drafts, not from executed code.
- I ran no lane gate, `measure.py`, `mutants.py`, `controls.py`, live tool, or port bind. The v1 grading quotes are read from committed bytes (`git show master:…`, tip `cff9e62`), not from the in-flight worktree.
- Recursive greps carried `--exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj`; no session, credential, `~/.omp` or `~/.config` content was read.

# Installs

None.
