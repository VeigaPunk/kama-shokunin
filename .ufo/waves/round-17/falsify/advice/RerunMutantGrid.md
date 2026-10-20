VERDICT: confirm — rerun matched all four committed C1 cells and every mutant outcome.

Axes attacked: grid repeatability; per-cell detector sensitivity across the frozen/current checks and pair/full detectors.

## Findings (severity-ranked)

- None. The normalized full JSON comparison was identical (exit 0); all four rerun baselines were valid. Rerun totals were frozen/pair 1/8 applicable killed, frozen/full 7/8, current/pair 1/10, and current/full 10/10, with no invalid or inconclusive mutants. These match the recorded claim at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:160-165`: “current/pair 1 of 10, current/full **10 of 10**.” The same lines say “frozen/full 7 of 8 (M8 survives: the frozen gate crashes on that input either way).”

Every mutant status matched, in cell order frozen/pair, frozen/full, current/pair, current/full (`K` = killed, `S` = survived, `SM` = site missing):

| Mutant | frozen/pair | frozen/full | current/pair | current/full |
|---|---:|---:|---:|---:|
| M0 ignore-verdict | S | K | S | K |
| M1 ignore-reason | S | K | S | K |
| M2 ignore-exit | S | K | S | K |
| M3 ignore-drift | S | K | S | K |
| M4 casefold-verdict | S | K | S | K |
| M5 timeout-pass | S | K | S | K |
| M6 ignore-served_model | SM | SM | S | K |
| M7 ignore-route-match | SM | SM | S | K |
| M8 malformed-output-passes | S | S | S | K |
| M9 reject-all | K | K | K | K |

## Runtime and commands

- Clone/checkout: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RerunMutantGrid-clone && git -C /tmp/KamaR17.RerunMutantGrid-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.RerunMutantGrid-clone rev-parse HEAD` — exit 0; checked out the requested commit.
- First runner attempt: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'elapsed_seconds=%e' python3 .ufo/waves/round-17/c1/mutants.py --grid --out /tmp/KamaR17.RerunMutantGrid-grid.json` (cwd `/tmp/KamaR17.RerunMutantGrid-clone`) — exit 127 because `/usr/bin/time` was absent; the runner did not start.
- Successful rerun: `TIMEFORMAT='elapsed_seconds=%3R'; time PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/c1/mutants.py --grid --out /tmp/KamaR17.RerunMutantGrid-grid.json` (same cwd) — exit 0; real time **22m11.630s** (user 113m6.361s, sys 13m12.487s). The runner wrote the JSON and all four cells report `baseline_valid: true`.
- Reference grid SHA-256: `ba0b3e2542e45279a9d9e41c58ebcdcb1143ead3947511d5606cfe4764018132` (`sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/mutants-grid.json`, exit 0).
- Full-document comparison normalized only the clone-root path back to the lane root and removed the volatile `.scratch` object. Reference normalization command plus byte count: `jq -S 'del(.scratch) | walk(if type == "string" then gsub("/tmp/KamaR17[.]RerunMutantGrid-clone"; "/home/vgpnk/Projects/shokunin/kama-shokunin") else . end)' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/mutants-grid.json > /tmp/KamaR17.RerunMutantGrid-baseline.normalized.json && wc -c /tmp/KamaR17.RerunMutantGrid-baseline.normalized.json` — exit 0, 233711 bytes. Current normalization and exact diff: `jq -S 'del(.scratch) | walk(if type == "string" then gsub("/tmp/KamaR17[.]RerunMutantGrid-clone"; "/home/vgpnk/Projects/shokunin/kama-shokunin") else . end)' /tmp/KamaR17.RerunMutantGrid-grid.json > /tmp/KamaR17.RerunMutantGrid-current.normalized.json && diff -u /tmp/KamaR17.RerunMutantGrid-baseline.normalized.json /tmp/KamaR17.RerunMutantGrid-current.normalized.json && printf 'normalized_json=identical\n'` — exit 0; no diff. `jq` availability/version check (`command -v jq && jq --version`) exited 0; jq was jaq 3.1.1.
- Post-run listener snapshot: `ss -ltnp` — exit 0; no listener on 8080 or 34113 and no grid/llama-server listener. The listed Python listeners were resident services (PIDs 1511–1518, started 09:57); `ps -p 1511,1512,1513,1514,1515,1516,1517,1518,2082972,3092 -o pid,ppid,lstart,comm` exited 0.
- Scratch cleanup command — `test ! -e /tmp/kama-r17-c1mutants-l0k21fdn && rm -f /tmp/KamaR17.RerunMutantGrid-grid.json /tmp/KamaR17.RerunMutantGrid-baseline.normalized.json /tmp/KamaR17.RerunMutantGrid-current.normalized.json && rm -rf /tmp/KamaR17.RerunMutantGrid-clone && test ! -e /tmp/KamaR17.RerunMutantGrid-clone && test ! -e /tmp/KamaR17.RerunMutantGrid-grid.json && test ! -e /tmp/KamaR17.RerunMutantGrid-baseline.normalized.json && test ! -e /tmp/KamaR17.RerunMutantGrid-current.normalized.json && printf 'owned scratch removed; runner scratch already absent\n'` — exit 0. Runner reported its temp scratch `kept: false`; it was absent before cleanup. No installs or updates.

## Residual risk

The pair detector still kills only M9 in both checks; its limited sensitivity is visible in the matrix, while full-detector outcomes match the claim. The run only supports these enumerated mutants and fixtures; it does not establish detection of unmodeled faults. [INFERENCE]

## Verification gaps

None for the assigned rerun and cell/mutant comparison. This report is a FALSIFY recommendation only; no admission, integration, or other C1/C2 claim review was performed.
