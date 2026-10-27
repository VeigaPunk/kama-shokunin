VERDICT: deterministic — 3 runs on one clone produce byte-identical receipts (sha256 5a97b51a…0aacb), and a 4th run with --scratch on /home (btrfs) is byte-identical to the xfs runs; not even the tip= line differs, and the counter emits no wall= line. C2 at 97c864be met=True on every run.

Seat item: determinism of tools/round50-append-audit-v5-check.py at tip 97c864bead3ee4a2f629574e77263d33834ec98a — 3 runs same clone, receipt diffs; 1 run with --scratch on /home (btrfs) for filesystem independence.

# Commands

    S=/fast/scratch/hyaku/kama-r50/V4Determinism; export TMPDIR=$S
    git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
    git -C $S/lane rev-parse --verify "97c864bead3ee4a2f629574e77263d33834ec98a^{commit}"  # -> 97c864bead3ee4a2f629574e77263d33834ec98a
    CTR=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py
    # runs 1-3 (xfs): --scratch $S/scr1|scr2|scr3, --out receipt-runN.txt   (sequential)
    # run 4 (btrfs): TMPDIR=$BS python3 $CTR --repo $S/lane --tip $TIP --scratch $BS
    #   $BS = .ufo/waves/round-50/w1/out/V4Determinism/tmp-btrfs-scratch (removed after run)

# Outputs

| run | --scratch filesystem | TMPDIR | exit | receipt sha256 |
|-----|----------------------|--------|------|----------------|
| 1   | /fast xfs (/dev/nvme1n1p2) | $S (xfs) | 0 | 5a97b51a7ec9e0ce99e0f09a414ed7f78499fdd0a2b33dd08798b6294bf0aacb |
| 2   | /fast xfs            | $S (xfs) | 0 | identical |
| 3   | /fast xfs            | $S (xfs) | 0 | identical |
| 4   | /home btrfs (/dev/mapper/root[/@home]) | $BS (btrfs) | 0 | identical |

Receipts: receipt-run1.txt, receipt-run2.txt, receipt-run3.txt, receipt-run4-btrfs.txt (this directory). All four identical:

    tip=97c864bead3ee4a2f629574e77263d33834ec98a
    fixture=1 lane=1 scenarios=12/12 met=True
    detail: scenario launder … ok ; native-head ok ; dated-loss ok ; substring ok ; word-token ok ;
            negated ok ; wildcard-self ok ; wildcard-named ok ; order-a ok ; order-b ok ; fence ok ;
            crlf-launder ok   (12/12, lines 3–14)
    detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
    detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
    detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72

Line-by-line diffs (`diff -u`):

    run1 vs run2            -> no output (identical)
    run1 vs run3            -> no output (identical)
    run2 vs run3            -> no output (identical)
    run1 vs run4 (btrfs)    -> no output (identical)

Line census of the receipt: 1 `tip=` line, 0 `wall=` lines, 15 `detail:` lines, 1 summary line.
The counter emits no `wall=` line at all (grep -c '^wall' = 0; emission site
tools/round50-append-audit-v5-check.py:532 builds only `tip=`, summary, `detail:`), so the
permitted "tip=/wall may differ" allowance is moot: even tip= was identical (it is the resolved
input commit, not a timestamp).

# Filesystem independence proof

findmnt -T (fs-evidence.txt): runs 1–3 scratch on /fast = xfs /dev/nvme1n1p2; run 4 scratch +
TMPDIR on /home = btrfs /dev/mapper/root[/@home]. Fixture repos live under --scratch
(counter docstring line 41: "each a fresh repo under --scratch"; main() line 508
`tempfile.mkdtemp(prefix="r50c2-", dir=root)`, removed in the `finally` at line 541 — verified:
$BS empty after run, rmdir succeeded). Identical receipt across xfs and btrfs ⇒ fixture
behavior is filesystem-independent at this level.

# Determinism notes (where variance could hide — checked, none observed)

- Fixture commit hashes: Fx.commit uses `git commit-tree` with ambient wall time, so fixture
  OIDs differ run to run — but no receipt line prints a fixture hash; `check()` detail lines
  embed only scenario name, exit code, and the stable event field dicts (counter lines 209–228).
- Lane-leg hashes in detail lines (dd9f5dc6c0e6, 0718b6abbda6) are real lane commits — stable
  for a fixed tip.
- Iteration orders that feed origin() are set unions over graph births (counter lines 437–462)
  and only ever surface as counts, not ordered output.
- No defect: receipts identical at a stricter-than-required level.

# Defects

None found in this scope.

# Environment / installs

No tools installed or upgraded; python3 + git system binaries used (bc absent — timing prints
used it, cosmetic only; per-run wall ~5–6 s). Scratch $S and the shared clone were removed on
completion; receipts and fs-evidence.txt copied here first. pgrep llama-server showed PIDs at
report time — pre-existing/other seats' servers; this counter starts no servers.
