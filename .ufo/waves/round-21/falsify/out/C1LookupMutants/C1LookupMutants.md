VERDICT: partial - existing selftest/raw detectors kill 2/5 mutants; three survivors have executed killing cases.
Attack: C1 `lookup()` and `checkable_abbrev()` in `tools/report-landing-audit.py` at a6617149722c73d90e142fbdc8154d6967055f7e.
Axes: calibration 7 (coverage of the detector's self-assessment); operability 8 (repeatable bounded probes and exact restoration).
Only the isolated /tmp/kama-r21-C1LookupMutants/lane source was mutated, one mutant at a time; no lane source/index or fleet files were edited.
Evidence home O = /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C1LookupMutants.
The requested advice/C1LookupMutants.md is outside the binding out-only write scope; this report is left in O for L1 placement.

## Executed detectors and expected results
S: `/usr/bin/python3 /tmp/kama-r21-C1LookupMutants/lane/tools/report-landing-audit.py --selftest`; expected exit 0 and `selftest cases=32 failed=0`.
P: `/usr/bin/python3 /tmp/kama-r21-C1LookupMutants/lane/tools/report-landing-audit.py --lane-repo /tmp/kama-r21-C1LookupMutants/lane --fleet-repo /home/vgpnk/Projects/shokunin --branch a6617149722c73d90e142fbdc8154d6967055f7e --rounds 10-20 --no-errata --json`; expected exit 1 and the baseline exact JSON.
K: `/usr/bin/python3 O/probe.py focused` (O expanded to the absolute evidence home); expected exit 0 for all helper/CLI assertions.
Executed `/usr/bin/python3 O/probe.py prepare` (exit 0), then `/usr/bin/python3 O/probe.py suite PHASE` for every phase below (each suite wrapper exit 0; child exits are reported separately).
The suite concurrently runs S/P/K, with a 25-second timeout per subprocess; no subagents or serving runtime were started.
All expanded argv, actual exits, stdout and stderr are retained in O/{PHASE}.json and O/{PHASE}.{selftest,raw,focused}.{stdout,stderr}; fixture-generation commands/exits are in O/prepare.json.

## Actual outcomes
Pristine and each of restored-m1, restored-m2, restored-m3, restored-m4, restored-m5: S=0 (32/32), P=1 (9 defects), K=0. No baseline was inconclusive.
| Mutant / phase | Smallest behavior changed | S exit / failed cases | P exit | Existing S+P verdict | K exit / augmented verdict |
|---|---|---|---|---|---|
| M1 / m1-ambiguous-found | L111 ambiguous status becomes found | 0 / 0 | 1 | survived | 1 / killed |
| M2 / m2-ignore-batch-rc | L101-102 batch-check call discards subprocess return code | 0 / 0 | 1 | survived | 1 / killed |
| M3 / m3-drop-peel | L102 removes `{peel}` from batch input | 1 / 1 | 1 | killed | 1 / killed |
| M4 / m4-invert-digitletter | L129-130 negates the short-token digit-and-letter requirement | 1 / 9 | 1 | killed | 1 / killed |
| M5 / m5-skip-fortyhex | L129-130 removes the length-40 exemption | 0 / 0 | 1 | survived | 1 / killed |
P stdout was byte-identical across all 11 phases: SHA-256 af2707adf5c2424ebe64b30505d33d94b0c5ca08f2d843cf6a27a4aa10651e24, also matching the previously recorded raw stream hash.
Every P result had 11 reports, 9 uncorrected defects (1 unresolved-full-hash + 8 landed-omitted), 42 required commits and 4 post-report commits. Thus P alone killed none of these five mutants.
M3 printed `FAIL blob-is-not-a-correction` and `selftest cases=32 failed=1`.
M4 printed `selftest cases=32 failed=9`; failures: bad-abbrev-detected, exact-defect-set, hex-words-not-citations, errata-clean, unmatched-errata-fails, unselected-round-row-ignored, round-must-equal, kind-must-equal, token-must-equal.

## Executed killing cases for every survivor
M1: real Git commit objects 51e8248c28ccfe5063253134fbbdd5e039354ed7 and 51e8248b5fe6539809858e54d44d02a2181c0296 share `51e8248` (deterministic collision found after 3655 candidates; only the two objects were written).
K's unpeeled `lookup(repos, ['51e8248'])` observed ambiguous on pristine/restored bytes, found on M1; assertion `lookup-ambiguous-not-found` killed M1. This is a helper-level ambiguity case, not a claimed CLI ambiguity demonstration.
M2: a scratch PATH wrapper runs /usr/bin/git, preserves its valid batch stdout, then injects exit 70 with stderr `injected batch-check failure after valid stdout` (fault injection, not an observed natural Git failure).
K observed EvalError and CLI exit 2 on pristine/restored bytes, but found and a clean CLI exit 0 on M2. Both `batch-check-nonzero-is-evaluation-error` and `cli-batch-check-nonzero-is-exit-2` killed it.
M5: K checked the two full tokens `ffffffffffffffffffffffffffffffffffffffff` and `1111111111111111111111111111111111111111`; checkable results were [true,true] pristine/restored versus [false,false] mutated.
The CLI report containing those tokens had four exact defects pristine/restored (both unresolved-full-hash and landed-unresolved for each), but only the two unresolved-full-hash defects under M5. CLI exit remained 1; exact defect-identity assertions, not an exit-only test, killed it.
K also exercised M3 with real blob a14c7fd1bfa22ef773edc481151cbad6b21abc57 (CLI invalid exit 1 -> clean exit 0), and M4 with defaced/1234567/deadbee1 (expected short-token checks [false,false,true] -> [true,true,false]).

## Before/after hashes and restoration
H = bd671a1e1e79a76a5c644d4efccd5baf0ce1121e9f308987ca816a5645520d69: pristine source and every restored source, before and after each detector suite.
Each mutant began from H, had the following identical before-suite/after-suite source hash, and was restored to H before proceeding:
M1: 86097f9b14b2e8077f0012c9a7a48631bd02a0c3b647b501c080bd40eb3d4209
M2: 109408b5766ca21d12d220cd9d3ad3fd859013f58d8b5eb7444e3f147ce80e02
M3: b36b2080f1a7bf16cb0b1915be09125f31ff153195f97bf29daf6a45c3c8a3ab
M4: 61894f656f94c57e40b5c94ca33be1dd3e32ab1c77fa522efbc43822dbbd3ec8
M5: 3544512a5153d185b7f0f98e11b36ea04bfcf4962db69e3edb3b4853442f5892
O/summary.json records all phase hashes, raw-byte equality and `final_exact_bytes_restored: true` from comparison against the saved pristine bytes. O/m1-*.patch through O/m5-*.patch reproduce the executed mutations and were checked against the observed mutant hashes.
Cleanup executed `rm -rf -- /tmp/kama-r21-C1LookupMutants && test ! -e /tmp/kama-r21-C1LookupMutants && printf 'scratch_removed=1; exit=0\n'`: exit 0, stdout `scratch_removed=1; exit=0`.
Tool versions: `git --version` exit 0 -> git version 2.56.0; `python3 --version` exit 0 -> Python 3.14.8. No tools installed or updated.
This is a coverage finding in the existing measurement pair, not evidence that the pristine implementation violates these five contracts. No production patch, integration, commit or official measurement was performed.
