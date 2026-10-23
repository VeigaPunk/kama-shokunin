#!/usr/bin/env bash
# Exact commands behind REPORT.md. Every run is read-only over the lane repo.
set -u
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ExecGateRegistryV2
L=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r29/w1/ExecGateRegistryV2
T="timeout 60 /usr/bin/python3 $O/gate-registry-check.py"

# 1. committed-fixture self-test (expected exit 0)
$T --selftest > $O/selftest.out 2> $O/selftest.err; echo $? > $O/selftest.exit

# 2. lane master, committed tree (expected exit 1; findings listed in REPORT.md)
$T --repo $L --rev refs/heads/master > $O/lane-master.out 2> $O/lane-master.err; echo $? > $O/lane-master.exit

# 3. lane working tree (same findings; prints "rev <HEAD>" + "tree worktree")
$T --repo $L --worktree > $O/lane-worktree.out 2> $O/lane-worktree.err; echo $? > $O/lane-worktree.exit

# 4. could-not-evaluate paths (both expected exit 2)
$T --repo $L --rev 0000000000000000000000000000000000000000 > $O/bad-rev.out 2> $O/bad-rev.err; echo $? > $O/bad-rev.exit
$T --repo $S/plain > $O/notgit-existing.out 2> $O/notgit-existing.err; echo $? > $O/notgit-existing.exit

# 5. pass state is reachable: a scratch repo whose rows are complete (exit 0)
$T --repo $S/clean-repo --rev HEAD > $O/clean-repo.out 2> $O/clean-repo.err; echo $? > $O/clean-repo.exit

# 6. mutated fixtures make the self-test fail
$T --selftest --fixtures $S/fix-a > $O/mutated-fix-a.out 2> $O/mutated-fix-a.err; echo $? > $O/mutated-fix-a.exit  # tampered input, exit 2
$T --selftest --fixtures $S/fix-b > $O/mutated-fix-b.out 2> $O/mutated-fix-b.err; echo $? > $O/mutated-fix-b.exit  # expectation edited, exit 1
$T --selftest --fixtures $S/fix-c > $O/mutated-fix-c.out 2> $O/mutated-fix-c.err; echo $? > $O/mutated-fix-c.exit  # content edited + digest re-pinned, exit 1
