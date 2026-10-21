VERDICT: partial - four mutants killed by the assigned detector trio; canonical-JSON mutant survived all three.
Attack: C2 producer install_links/links_digest and grid detection/summary at a6617149722c73d90e142fbdc8154d6967055f7e; advisory mutation results only, not round admission.
Axes: operability (fail-closed install identity) and calibration (detector sensitivity and honest survivor accounting).
Write scope: this report is in the mandatory out-only directory; the requested falsify/advice destination is left to L1 integration.

## Scope and executed commands
Lane source P = /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py; G = /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-links-grid.py. All tested bytes came from the pinned commit, not the live checkout.
OUT = /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2ProducerGridMutants; isolated copies were /tmp/kama-r21-C2ProducerGridMutants/M1-drop-directory-problems through the five named cases in probe.py.
Executed `python3 -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2ProducerGridMutants/probe.py prepare` — exit 0; five clones/checkouts each exit 0; revision command prints a6617149722c73d90e142fbdc8154d6967055f7e, exit 0.
Executed `python3 -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2ProducerGridMutants/probe.py baseline` — harness exit 0.
Executed `python3 -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2ProducerGridMutants/probe.py mutated` — harness exit 0; individual detector exits below.
Executed `python3 -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2ProducerGridMutants/probe.py restored` — harness exit 0.
Detectors: P = producer --selftest; G = grid --selftest; C = grid --tree /home/vgpnk/.local/opt/llama-b11755 --arm current. Each uses python3 -B and an absolute scratch source path; every concrete argv/cwd/exit/stdout/stderr is retained in the phase JSON files.
Every case ran P/G/C on pristine, singly mutated, and exactly restored bytes: 45 assigned-detector executions, plus three canonical-order witnesses. Four subprocesses maximum, 120-second per-command bound, no timeouts. Python 3.14.8 and UID 1000 were observed, both commands exit 0. No tools installed or updated.

## Mutants and expected detectors
Exit tuples are P/G/C. Killed means pristine/restored pass and a mutated assigned detector exits 1; zero inconclusive cases.
| Mutant / smallest edit (original pinned line) | Expected detector | Pristine | Mutated | Restored | Result |
|---|---|---|---|---|---|
| M1 readable directories accepted: P:239 adds `and not stat.S_ISDIR(mode)` | P/G/C: fail-closed subdirectory | 0/0/0 | 1/1/1 | 0/0/0 | killed |
| M2 remove os.access branch and unreadable problem: P:241-242 | P: unreadable-member assertion | 0/0/0 | 1/0/0 | 0/0/0 | killed by P; survives both grid detectors |
| M3 remove sort_keys=True in links_digest: P:209 | P: canonical digest | 0/0/0 | 0/0/0 | 0/0/0 | survived assigned trio |
| M4 ignore problems in identity: G:178 replaces problems with [] (key preserved) | G/C: subdir must change identity/refuse | 0/0/0 | 0/1/1 | 0/0/0 | killed |
| M5 null cell expect_change becomes True: G:224 | G/C: unchanged null must pass | 0/0/0 | 0/1/1 | 0/0/0 | killed |

## Actual outputs and coverage findings
All pristine/restored P runs print `selftest: ok; closed tcp6 listeners ...`; G prints `selftest cases=13 failed=0`; C prints `summary arm=current link=13/13 subdir=1/1 regular=3/3 type=1/1 null=0/1 wrong=0 real_tree_gate_clean=True status=pass`, each exit 0.
M1/M2 P stderr is `kama-llamacpp-live selftest: AssertionError`, exit 1. M1/M4 G prints FAIL for current-catches-all-via-symlinked-tree, subdir-refused, current-only-exit-0; `selftest cases=13 failed=3`, exit 1.
M1/M4 C prints `subdir-hwcaps-shadow ... current=same` and summary `subdir=0/1 ... wrong=1 ... status=fail`, exit 1; all other class counts match pristine.
M5 G fails current-catches-all-via-symlinked-tree and current-only-exit-0; `selftest cases=13 failed=2`, exit 1. C retains pristine class counts but `wrong=1 ... status=fail`, exit 1; null-unchanged remains current=same.
M2 C still passes, exit 0, with `regular-unreadable ... current=changed` instead of pristine `current=changed+refused`; G passes all 13, exit 0. [INFERENCE] The grid's changed-identity condition does not independently enforce unreadable-member refusal; install_tree's omission can still change its digest.
M3 passes P/G/C, exits 0/0/0. Separate executed canonical-order witness (exact -c argv in JSON) compares {'z':'target-z','a':'target-a'} with the same map inserted a-first: pristine/restored `insertion_order_invariant=True`, exit 0; mutant False, exit 1.
M3 witness mutant reverse SHA256 = 5b8b894e71a5b32178ac651bfbc06c89f4bb1e23aa5568d18ef8d18ef4dbcfc9; sorted SHA256 = 656f31ea64cce8abf164bfbd86ef185620a05a0e6120573117c2b414fe699869. Pristine/restored both equal the latter.
P:206 at the pinned revision says "sha256 over canonical JSON (sorted keys, ASCII escapes)". The witness demonstrates a standalone helper-contract coverage gap, not an observed live receipt failure. [INFERENCE] Sorted enumeration at P:226 masks this particular mutant for install_links-generated maps; the existing selftest also supplies its multi-key map in sorted order.

## Before / mutant / restored SHA256
P pristine = restored = e4cc6d8885c7755717157fd23bfce3be39288990a9cf5985cb1c56a4b11cf68f.
G pristine = restored = 4f091523d43b9dc1b4e7f4557b5a6f2050cbb01fbd6496762089102d1e7c2809.
| Case | Changed file | Mutant SHA256 (before/after hashes of each detector phase are in JSON) |
|---|---|---|
| M1 | P | b58072e2e885d1151d380b2edc86371a6ab128e4ac9e7b88eb70d614942ef640 |
| M2 | P | 7e1d3cb988ccba71cabc8615605684880b94d1e76c62645217968e781c3cca3c |
| M3 | P | 7251732c351026b5ad0fcbb3a8c3461d7bd0ef54315b372268c075523f7a02cc |
| M4 | G | 9abfaf6c41e803f5c3706d9b3378535c2f29717bbfe04b0534442b9a24301e91 |
| M5 | G | 0331bc1643d84c4d9c5bd7f7a32287de9ed74c9270d7e4038f46fce7018d4c7c |
Gate SHA256 stayed 6b8764374f1cc1059ba7520f7e7a68f37acc6a31b3e72220f4b42826e72d4a61 in all five copies/all phases. All phase logs record source_bytes_unchanged_during_detectors=true; restored.json records restoration_exact_all_sources=true for producer/grid/gate across all five copies.

## Restoration, isolation and evidence
Exact source bytes were restored with inverse surgical edits before rerunning the same detectors; all 15 restored assigned detectors and the restored witness exited 0. No lane source, Git/jj state/index, fleet files, services or real install bytes were changed; no llama-server or live producer invocation occurred.
Executed `rm -rf -- /tmp/kama-r21-C2ProducerGridMutants && test ! -e /tmp/kama-r21-C2ProducerGridMutants && printf 'cleanup: scratch absent; exit=0\n'` — exit 0; stdout `cleanup: scratch absent; exit=0`. All detector processes were waited to exit; producer selftest's temporary sockets closed.
Evidence under OUT: prepare.json (setup argv/exits), baseline.json, mutated.json, restored.json (complete command streams and hashes), cleanup.json, probe.py (bounded harness). Each file is under 1 MiB. Existing checks were not changed to hide survivors; no fix/integration or official measurement was attempted.
