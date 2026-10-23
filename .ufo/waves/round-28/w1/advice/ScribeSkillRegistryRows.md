# ScribeSkillRegistryRows — scoped findings

## Behavior drafted
Created a four-row table in the existing `SKILL.md` local gate/probe registry format (columns: Name, Kind / entry command, Exit map, Self-test / pinned values, Write scope):

1. Retires `.ufo/waves/round-27/count-c1.py`, including the supplied SHA-256 and the final L1 receipt's `registered 0 counted 0 target 15 met False` result. The row distinguishes a counter-threshold miss from a canonical C1 judgment, records that no data seat was dispatched, and cites the routed defect in the round-27 spot-check.
2. Registers the round-28 C1 command, `counted` label, target 18, pilot receipt, and code-declared counter/schema/server/library/model pins.
3. Records the `gate-registry-check.py --rev` contract and 0/1/2 meanings.
4. Records the `echo-recheck.py --out` fresh-path contract, 0/1/2 meanings, and code-declared round-27 server/model pins.

## Gates and execution evidence
No counter, gate, echo recheck, test, or server was run by this seat. The pilot receipt is pre-existing evidence, not a run performed here. The r27 `c1-final.out` records an L1 closure run with exit 0 and zero counted rows; it is not a data-seat run. Pin hashes in the draft are read from counter source and were not independently checked against host binaries, libraries, model, or snapshot bytes. The requested `ExecGateRegistryCheck` and `ExecEchoRecheck` output directories were not present when checked, so their implementations and execution receipts remain unchecked; rows label those details as contract-only.

## Touched surfaces and exact command
- Created `.ufo/waves/round-28/w1/out/ScribeSkillRegistryRows/rows.md` (four data rows, plus header).
- Created this report at `.ufo/waves/round-28/w1/advice/ScribeSkillRegistryRows.md`.
- No tracked lane file, product code, registry, judge, or other output was changed. No tools were installed.
- Only shell command issued: `timeout 10s mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ScribeSkillRegistryRows` (returned no output). No check command was run.

## Provenance and findings
- `SKILL.md:296-308` supplies the local gate/probe table and five-column row format. Searching `count-c1` in `SKILL.md` found the round-26 re-derivation command at lines 1073-1075, but no separate round-26 counter row; the draft follows the local registry table format.
- `.ufo/waves/round-28/preregistration.json` provides the C1 command, target, label, counter pin and pilot description; `.ufo/waves/round-28/before/pilot-receipt.json` reports registered 2, counted 2, target 18, met false, not-counted empty. `.ufo/waves/round-28/count-c1.py:64-86` provides the snapshot, server/library and model pin constants and exit description.
- `.ufo/waves/round-27/a3/c1-final.out` and `c1-final-receipt.json` record the zero-count, target-15 final L1 run and counter SHA. `.ufo/waves/round-27/a3/plan.json:6-8` says “withdrawn before data” and “No data seat of round 27 was ever dispatched.” The routed repair is `corpus/lessons/round-27-verifier-spotcheck.md:266-269`.
- The requested “C1 miss” wording conflicts with the retained disposition evidence. The round-27 review says verbatim: “This is **not** a counter run or a C1 miss verdict.” (`.ufo/waves/round-27/w1a3/advice/CriticC1Withdrawal.md:26`); the A3 plan says “withdrawn before data,” while the final L1 receipt independently shows 0/15. The draft reports the measured counter-threshold miss and preserves the canonical disposition for the judge; this seat does not resolve the conflict.
- `.ufo/waves/round-28/w1/spec.json` lines 97-104 provides the gate and echo tool contracts, including test expectations and echo ports 48231-48233. These contracts are not execution evidence.

## Out of scope / known limits
No integration into `SKILL.md`, execution of the requested tool demonstrations, live serving, or canonical C1 judgment was performed. The r28/r27 hash values in the rows are declared pins from source, not independently measured host-file digests. The gate/echo rows must be reconciled against the eventual implementation and receipts before being treated as executed registry evidence.

## Artifacts
- `.ufo/waves/round-28/w1/out/ScribeSkillRegistryRows/rows.md`
- `.ufo/waves/round-28/w1/advice/ScribeSkillRegistryRows.md`
