Verdict: Separability fails on the C2 tree: C1 is met on tree (a) (bind=1 own=1 teardown=1 newrow=1, exit 0) and unmet on tree (b) (own=0 newrow=0, exit 1); but C2 is unmet on both tree (a) (fixture=0 lane=0, exit 1) and tree (b) (fixture=1 lane=0, exit 1) because C2's disclosure ledger at build-fix 73bf2a7a dropped row 97c864be on the assumption that C1's S499 hunk in corpus/SOURCES.md restores the blank line.

# Evidence

Two fixture trees were constructed from freeze commit `804bde75164444bdf0fe6783d7aa45774bf562bd`:
- **Tree (a)**: commit `e766fa6e5798fe6215b1272e4c46dd372ee84cf1` contains `804bde75` plus only C1 build files from `138af25b963450b6520794995605fa7dbbcd87e0` (`tools/kama-llamacpp-live.py`, `tools/kama-live-replay.py`, `corpus/SOURCES.md`).
- **Tree (b)**: commit `9ca6493511e874d79938b6623b4c799f21f0d11f` contains `804bde75` plus only C2 build files from `138af25b963450b6520794995605fa7dbbcd87e0` (`tools/append-only-audit.py`, `registry/append-only-disclosures.tsv`, `tools/digest-ledger.py`).

All four combinations of counter and tree were executed:

### 1. C1 counter on Tree (a) [MET as expected]
- Command:
  ```bash
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py \
      --repo "$S/lane" --tip e766fa6e5798fe6215b1272e4c46dd372ee84cf1 --scratch "$S/scratch_c1_a" \
      --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N2Couple/tree-a.c1.out
  ```
- Exit code: `0`
- Summary: `tip=e766fa6e5798fe6215b1272e4c46dd372ee84cf1 bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`
- Key output:
  - `detail: bind b1: pid 1143120 port 38545 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 20812420 recorded, nonce 'kama witness 5c78ef0dad71d5f3' round-tripped`
  - `detail: own b1: running image 103:05:1823055997 is the extracted member, recorded in server_exe and own_server`
  - `detail: bind b2: pid 1145370 port 39529 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 413580270 recorded, nonce 'kama witness 9045237ae1cf2b7f' round-tripped`
  - `detail: own b2: running image 103:05:1021084088 is the extracted member, recorded in server_exe and own_server`
  - `detail: bind b3: pid 1148794 port 34797 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1021100660 recorded, nonce 'kama witness 03a3faa9d9e5521e' round-tripped`
  - `detail: own b3: running image 103:05:1488608522 is the extracted member, recorded in server_exe and own_server`
  - `detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`
  - `detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']`

### 2. C2 counter on Tree (a) [UNMET as expected]
- Command:
  ```bash
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
      --repo "$S/lane" --tip e766fa6e5798fe6215b1272e4c46dd372ee84cf1 --scratch "$S/scratch_c2_a" \
      --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N2Couple/tree-a.c2.out
  ```
- Exit code: `1`
- Summary: `tip=e766fa6e5798fe6215b1272e4c46dd372ee84cf1 fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False`
- Reason: Tree (a) has only v5 `append-only-audit.py` (threshold 20, missing `--disclosures` argument) and lacks `registry/append-only-disclosures.tsv`. Both fixture leg (0/9 scenarios) and lane leg fail.

### 3. C1 counter on Tree (b) [UNMET as expected]
- Command:
  ```bash
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py \
      --repo "$S/lane" --tip 9ca6493511e874d79938b6623b4c799f21f0d11f --scratch "$S/scratch_c1_b" \
      --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N2Couple/tree-b.c1.out
  ```
- Exit code: `1`
- Summary: `tip=9ca6493511e874d79938b6623b4c799f21f0d11f bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False`
- Reason: Tree (b) has freeze-era replay and live tools without `server_exe` or `own_server` checks (`own=0`), and lacks S499 in `corpus/SOURCES.md` (`newrow=0`).

### 4. C2 counter on Tree (b) [UNMET — SEPARABILITY CONTRADICTION]
- Command:
  ```bash
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
      --repo "$S/lane" --tip 9ca6493511e874d79938b6623b4c799f21f0d11f --scratch "$S/scratch_c2_b" \
      --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N2Couple/tree-b.c2.out
  ```
- Exit code: `1`
- Summary: `tip=9ca6493511e874d79938b6623b4c799f21f0d11f fixture=1 lane=0 scenarios=9/9 lost=143 disclosed=166 met=False`
- Failure detail:
  - `detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 1, 'partial': 0, 'regressed': 0, 'bad_disclosures': 0, 'bad_declarations': 0}`
  - `detail: lane: 97c864bead3e corpus/SOURCES.md: own lost 1 ledger 0 (1 keys differ)`
  - `detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 143; ledger lines 166`

# Defect and Root Cause

- Defect location:
  - `registry/append-only-disclosures.tsv:162-167`
  - `corpus/SOURCES.md:251-254`
- Mechanism:
  1. In round 50, commit `97c864bead3ee4a2f629574e77263d33834ec98a` modified `corpus/SOURCES.md` to add S496–S498 and deleted the blank separator line preceding `## Paths`.
  2. At the round-51 freeze (`804bde75164444bdf0fe6783d7aa45774bf562bd`), `corpus/SOURCES.md` remained without that blank line.
  3. In round 51 build commit `b6bed925`, C1 added row `S499` to `corpus/SOURCES.md`, followed by an extra blank line before `## Paths`.
  4. In `tools/append-only-audit.py` (lines 356–360), multiset line holding is computed as `held = min(D, max(0, tip - kept))`. Adding an extra blank line in `corpus/SOURCES.md` caused `97c864be`'s deleted blank line to be counted as restored at tip.
  5. The initial disclosure ledger included a disclosure row for `97c864be` in `corpus/SOURCES.md`. Because S499 added the blank line, having this disclosure row at the build was flagged as an over-count.
  6. Commit `73bf2a7a` ("disclosure ledger regenerated at the build (the S499 build restored the blank separator 97c864be removed, so its row was an over-count)") removed the `97c864be` row from `registry/append-only-disclosures.tsv`.
  7. When evaluating Tree (b) (C2-only), `corpus/SOURCES.md` is at freeze `804bde75` (no S499, no restored blank line). The deleted line in `97c864be` is unheld (`lost=143`), but `registry/append-only-disclosures.tsv` at `138af25b` has 0 disclosures for `97c864be`. Thus C2 exits 1 with `unrestored: 1`.
  8. Therefore, C2 cannot pass on its own files without C1's modification to `corpus/SOURCES.md`. The claims are not separable.

# Affected Axes

- **calibration**: The append-only disclosure ledger's validity was made conditionally dependent on an unannounced whitespace restoration inside a file modified by an unrelated claim (C1). Furthermore, `append-only-audit.py` grades blank line whitespace inside `A-row` files despite `registry/append-only-contract.tsv` defining `A-row` for registry rows (`KQ22`, `tools/sources-append-only.py`).
- **operability**: Verification modularity and claim independence are compromised when claim B cannot be evaluated or reproduced without the build artifacts of claim A.

# Proposed Move

Decouple C1 and C2 cleanly by restoring explicit separability:
1. In `corpus/SOURCES.md`, keep S499 without adding an extra trailing blank line before `## Paths` (leaving the inter-section spacing as it stood at the freeze).
2. In `registry/append-only-disclosures.tsv`, retain the explicit disclosure row for commit `97c864bead3ee4a2f629574e77263d33834ec98a` on `corpus/SOURCES.md` (`e3b0c442...`, count 1, class `in-place-edit`).
3. Alternatively for subsequent rounds: update `tools/append-only-audit.py` to only grade row lines (`^ {0,3}\| *S[0-9]{3,}`) in files declared with rule `A-row`, consistent with `tools/sources-append-only.py`.

The unified diff for the direct decoupling move is provided at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N2Couple/separability-fix.patch`.

# Risks

- The round-51 counters and preregistration are frozen; changing `append-only-audit.py` or the contract TSV directly in this round is out of scope.
- Applying a diff to `corpus/SOURCES.md` post-build would introduce a new commit whose diff must not delete lines. The clean place to reconcile this is during the round-51 integration pass by the lane integrator (KamaR51a2), or by recording an explicit erratum acknowledging the cross-claim dependency in `frozen-at-erratum.md`.

# Verification

- **Tree (b) with fix applied**: Re-inserting the `97c864be` disclosure row into `registry/append-only-disclosures.tsv` on Tree (b) (commit `3add969d5fb8614450cdad41870d13c3e021d6cc`) resulted in:
  ```
  fixture=1 lane=1 scenarios=9/9 lost=143 disclosed=167 met=True
  exit=0
  ```
- All four empirical counter run receipts are saved in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N2Couple/`:
  - `tree-a.c1.out`
  - `tree-a.c2.out`
  - `tree-b.c1.out`
  - `tree-b.c2.out`
