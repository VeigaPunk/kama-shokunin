VERDICT: partial — append-ready §Round-18 draft written for every named row; all v3 behaviour is contract-only at lane tip e75cf68, so every v3 count is `[L1 fills]`.

# ScribeSkillRound18 — scoped findings

Seat: `KamaR18.ScribeSkillRound18-2`, leaf scribe. Owned output: `.ufo/waves/round-18/build/drafts/skill-round18.md` (sha256 `d4219416ad1e8481e7bcac2cb7e6f26db3039ede189c9e1393b079f321bb9a5f`, 21 `[L1 fills]` markers). No lane doc, tracked file, frozen copy, measurement or gate was run or edited. No tools were installed or updated.

## Behaviour

- Drafted `## Round-18 receipt v3, not-evaluated outcomes and detector self-checks (owner: kama)` in the seven-column table style of §Round-17 (`SKILL.md:557-599`). It holds an exit legend for tool and gate, a main table with one row per named item, and a §Corrections table for round-17 cells.
- Each v3 claim is labelled as contract. Current-code facts cite lane file and line.

## Lane state observed (read-only, 2026-10-20)

- `git rev-parse master` = `e75cf680b53484a61709ee1b2787d8dbc6419f74`.
- `.ufo/waves/round-18/c1/`, `c2/`, `build/out/` are empty. `c1/measure.py`, `c2/survivors.py` and `.ufo/waves/round-18/dispatch-provenance.py` do not exist in the lane checkout.
- The frozen copies and `SHA256SUMS` exist under `.ufo/waves/round-18/frozen/`.
- Consequence: no v3 receipt, gate, controls or survivor count exists to quote. Every such number is `[L1 fills]`.

## Findings that change the lane text

1. **Exit 3 is not in the v3 contract text.** The tool returns 3 for a pre-launch model digest mismatch (`tools/kama-llamacpp-live.py:1019-1023`). The contract lists only 0, 1, 2. The draft flags this for L1 rather than choosing (see Quote 1).
2. **Zero-loading run exits 1 today.** `loading_envelope_graded` requires `loading_observed is True` (`:1347`); the exit becomes 1 at `:1376-1378`. The round-18 change to `passed: null` / exit 2 is contract only.
3. **`--require-schema` does not exist at lane tip.** The gate argparse has only the receipt path, `--expect-*` pins and `--selftest` (`tests/llamacpp-live/check-receipt.py:1361-1371`).
4. **Round-17 row defects confirmed at lane tip** (advisory `SkillRound17Rows` listed seven; the six bullets below were re-verified here against code and all matched; its write-scope finding was not re-verified and is cited as advisory in the draft):
   - Controls exit predicate omits `gate_flip_bad` and `inconclusive` (`controls.py:688-689`, `:696`).
   - Fault-controls `--list` does not validate the matrix; `--selftest` does (`fault-controls.py:633`, `:635`, `:656`).
   - Live v2 entry command omits `--server`; the tool then uses `shutil.which` (`kama-llamacpp-live.py:998`).
   - `source_binding` row is `None` for `health_ready` (`:871`) and `teardown_graceful` (`:902`).
   - Bare `mutants.py --dry-run` returns usage error (`.ufo/waves/round-17/c1/mutants.py:1325`).
   - Preflight setup errors return 2 before the receipt object exists (`:1010-1041`, receipt at `:1042`), so "receipt still written" is not universal.
5. **Dispatch provenance undercount.** Round-17 tool counts refusals only from literal `refused` keys or status strings (`.ufo/waves/round-17/dispatch-provenance.py:357-372`). The advisory reran it and got `refused: 0` for 82 refused tasks (`ProvenanceRerun`). The draft records this as a target.
6. **Probe decoder escape.** `tests/probe-verdicts/check.py:390` catches only `json.JSONDecodeError`. Advisory `MalformedNonUtf8` reports `RecursionError` and a 4300-digit-limit `ValueError` escaping, exit 1 with no JSON. Not re-run by this seat.
7. **Timeout topology gap.** Advisory `TimeoutPath` shows a shell probe's external `sleep` survives the checker (31.023 s observed there). F7 uses `exec` and has no external child.
8. **Append-only guard gaps.** Advisory `MutAppendOnlyGuard`: M3a drops the `opened` cell and survives; M4b drops rows after the blank line following `## Registry` and survives. `MUTABLE_CELLS` is at `tools/sources-append-only.py:43`.

## Sources (opened this session; access 2026-10-20)

Quotes are verbatim and at most 25 words.

| # | URL or path:line | Located quote |
|---|---|---|
| 1 | `tools/kama-llamacpp-live.py:1019` | "kama-llamacpp-live: model digest mismatch" (line 1019; `return 3` at 1023) |
| 2 | `tools/kama-llamacpp-live.py:1347` | "receipt.get('loading_observed') is True" |
| 3 | `tools/kama-llamacpp-live.py:998` | "server_arg = args.server or shutil.which('llama-server')" |
| 4 | `tests/llamacpp-live/controls.py:688` | "and result['gate_flip_bad'] == 0" |
| 5 | `tests/llamacpp-live/controls.py:696` | "return 0 if (clean and good_ok) else 1" |
| 6 | `tests/llamacpp-live/check-receipt.py:44` | "Exit: 0 receipt valid, 1 receipt invalid (every problem listed)," |
| 7 | `tests/probe-verdicts/fault-controls.py:633` | "parser.add_argument("--list", action="store_true"," |
| 8 | `.ufo/waves/round-17/c1/mutants.py:1325` | "error: --check (or --grid) is required" |
| 9 | `tests/probe-verdicts/check.py:390` | "except json.JSONDecodeError as exc:" |
| 10 | `tools/sources-append-only.py:43` | "MUTABLE_CELLS = frozenset({"status", "recheck", "used-by"})" |
| 11 | `.ufo/waves/round-17/dispatch-provenance.py:357` | "`refused` keeps the round-16 legacy tally: any dict key literally" |
| 12 | `SKILL.md:575` | "0 accepted_bad 0 and good_ok, 1 otherwise, 2 own fault" |
| 13 | `corpus/lessons/round-17-verifier-spotcheck.md:235` | "It should be could-not-evaluate (exit 2)." |
| 14 | `corpus/lessons/round-17-verifier-spotcheck.md:245` | "K6 accepts any nonzero exit;" |
| 15 | `.ufo/waves/round-17/falsify/advice/ProvenanceRerun.md` (Medium finding, no line) | "again appended `parseable: true, refused: 0` (exit 0)" |
| 16 | `.ufo/waves/round-17/falsify/advice/MutAppendOnlyGuard.md` (header, no line) | "M3a silently drops the `opened` cell from comparison" |
| 17 | `.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md` (results table, no line) | "Pristine | 5/3; 1 | 8/0; 0" |
| 18 | `tests/llamacpp-live/controls.py:60` | "Ports: none are bound by this script" |
| 19 | `tests/llamacpp-live/check-receipt.py:55` | "import tempfile" |
| 20 | `corpus/lessons/round-17.md:250` (heading "Kept as debt") | "Kept as debt (not repaired this round; each named so the next round can take it):" |
| 21 | `.ufo/waves/round-17/falsify/advice/TimeoutPath.md` (header, no line) | "a shell probe's external sleep survives the checker" |

Not opened or quoted: any external URL. The `https://docs.python.org/3.14/` citation form is recorded as a requirement only; this seat did not fetch it.

## Limitations

- Advisory numbers (frozen/current controls, fault detectors, survivor sets) come from round-17 advice files, not round-18 measurements. The draft labels them as such.
- Measurement row values, pinned hashes of new builds, and selftest counts are unknown until L1 integrates C1/C2 and runs the official commands. Each is marked `[L1 fills: …]`.
- The `loading_observed` quote gives code location only. The live zero-loading exit (1 today) was not run.
- Whether v3 keeps tool exit 3 is unresolved in the contract text.
- Not verified here: the `check.py` self-test temporary-file claim and the `ScribeS047Gate`, `ScribeQualityKQ23`/`KQ24`, `ScribeReadmeAppend`, `ScribeSourcesKernel` outputs (owned by sibling seats).

## Installs and writes

- Installs or updates: none.
- Writes: `.ufo/waves/round-18/build/drafts/skill-round18.md` and this report only. No git write, no `jj`, no port binding, no server started.
