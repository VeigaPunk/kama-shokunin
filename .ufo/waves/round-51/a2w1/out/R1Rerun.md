# R1Rerun — C1 independent remeasurement

**Verdict: C1 remeasurement agrees with the frozen claim at the build tip; the base run remains a negative control.** Both build-tip runs passed (`bind=1 own=1 teardown=1 newrow=1`, exit 0); the base run failed the claimed new ownership/source-row legs and met no claim (`bind=1 own=0 teardown=1 newrow=0`, exit 1), matching the frozen base control.

## Evidence

- Full clone command: `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r51/R1Rerun/lane`. Clone completed; clone top-level reported `/fast/scratch/hyaku/kama-r51/R1Rerun/lane`, HEAD `4eca4892acca6ca4072a0a6fad577d0dd78a5dda`.
- Frozen hash: preregistration `counter_sha256` at `.ufo/waves/round-51/preregistration.json:20` is `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155`. `sha256sum` of the counter at build commit `138af25b963450b6520794995605fa7dbbcd87e0`, the clone's working-tree counter, and the lane working-tree counter all returned exactly that digest. Counter contract/output is documented at `tools/round51-replay-exe-audit.py:1-56`; target is also frozen at preregistration line 22.
- The counter path is absent at base commit `57a2e25bf702b03aa61f9265e968cf68058ecb82` (the `git show <base>:tools/round51-replay-exe-audit.py` check returned path-absent); the required frozen counter from the clone working tree was therefore run with `--tip` set to base, exactly as the base control uses the frozen bytes.
- Commands (each used `S=/fast/scratch/hyaku/kama-r51/R1Rerun`, `export TMPDIR="$S"`, counter `$S/lane/tools/round51-replay-exe-audit.py`, and `--repo "$S/lane" --scratch "$S"`):
  1. `python3 ... --tip 138af25b963450b6520794995605fa7dbbcd87e0 --out .../R1Rerun/c1-build-1.out` — exit 0.
  2. `python3 ... --tip 138af25b963450b6520794995605fa7dbbcd87e0 --out .../R1Rerun/c1-build-2.out` — exit 0.
  3. `python3 ... --tip 57a2e25bf702b03aa61f9265e968cf68058ecb82 --out .../R1Rerun/c1-base-1.out` — exit 1.
- Across the two build receipts, all nonvolatile behavior/results match: same tip, summary, 512-token vocabulary, all three bind/own successes, teardown success after 0.10s with no descendants and closed port, and the same single S499 `proc_pid_exe(5)` row. No difference beyond expected process IDs, ports, mapping/executable inode values, and nonces. At base, bind/teardown remain successful, while `server_exe`/`own_server` are absent and the row is absent; this matches `.ufo/waves/round-51/controls/base.c1.out:1-14` (its recorded pids/nonces/inodes differ, as expected).

## Complete captured receipt lines

`c1-build-1.out` (exit 0):
```text
tip=138af25b963450b6520794995605fa7dbbcd87e0
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 1016574 port 35465 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 2025338689 recorded, nonce 'kama witness 16d3fd2ebba613b4' round-tripped
detail: own b1: running image 103:05:1693185688 is the extracted member, recorded in server_exe and own_server
detail: bind b2: pid 1024369 port 36849 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1692437301 recorded, nonce 'kama witness ac429b1f63da4ee3' round-tripped
detail: own b2: running image 103:05:1753114025 is the extracted member, recorded in server_exe and own_server
detail: bind b3: pid 1031868 port 44495 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1219173467 recorded, nonce 'kama witness 9ef9ce638d78cc8d' round-tripped
detail: own b3: running image 103:05:76413742 is the extracted member, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

`c1-build-2.out` (exit 0):
```text
tip=138af25b963450b6520794995605fa7dbbcd87e0
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 1055164 port 35173 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1488124760 recorded, nonce 'kama witness 67caf888221ff779' round-tripped
detail: own b1: running image 103:05:413323379 is the extracted member, recorded in server_exe and own_server
detail: bind b2: pid 1057126 port 36933 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1621239351 recorded, nonce 'kama witness 8e92e969dc67b5b6' round-tripped
detail: own b2: running image 103:05:1151511853 is the extracted member, recorded in server_exe and own_server
detail: bind b3: pid 1060370 port 33227 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 752129985 recorded, nonce 'kama witness 999aa979c872636b' round-tripped
detail: own b3: running image 103:05:1694094840 is the extracted member, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

`c1-base-1.out` (exit 1):
```text
tip=57a2e25bf702b03aa61f9265e968cf68058ecb82
bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 1076581 port 43523 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1219162579 recorded, nonce 'kama witness 1f8708204477d9e8' round-tripped
detail: own b1: own: rerun server_exe None does not record the observed image ('103:05', '1151677848')
detail: own b1: own: replay own_server None does not name the observed member file
detail: bind b2: pid 1081266 port 45855 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1284281181 recorded, nonce 'kama witness 3d6473e815b004a9' round-tripped
detail: own b2: own: rerun server_exe None does not record the observed image ('103:05', '1553933373')
detail: own b2: own: replay own_server None does not name the observed member file
detail: bind b3: pid 1087523 port 44827 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 683892832 recorded, nonce 'kama witness 916f04b8e4dfa8b2' round-tripped
detail: own b3: own: rerun server_exe None does not record the observed image ('103:05', '750735921')
detail: own b3: own: replay own_server None does not name the observed member file
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 0 rows new since base; 0 name proc_pid_exe(5): []
```
