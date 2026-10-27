# Sc1Freeze — round 53 freeze ordering and receipts

Verdict: PASS — freeze ordering, counter digests, control commit state and preregistration time check are all consistent; no defects found (two non-blocking observations below).

Lane kama, base 4229ea1b9a789148dded1f159c20967d9a01373f, freeze d01b2b6d48a54ffe0e475000737d3e302c62e28e, build c22602bd8d83ab26349d1087e916ca537ee4f9d1. All git commands run read-only against /home/vgpnk/Projects/shokunin/kama-shokunin; full transcript in out/Sc1Freeze/evidence-freeze-checks.txt.

## 1. Freeze ordering

Command (exactly as seated):

    git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %cI %s' 4229ea1b9a789148dded1f159c20967d9a01373f..c22602bd8d83ab26349d1087e916ca537ee4f9d1

Output (exit=0):

    c22602bd8d83ab26349d1087e916ca537ee4f9d1 2026-10-27T03:07:23-03:00 round-53: build - per-mapping code identity (C1), cited-path corrections (C2), S506-S509, lesson
    d01b2b6d48a54ffe0e475000737d3e302c62e28e 2026-10-27T03:02:49-03:00 round-53: freeze - preregistration, C1/C2 counters, base controls, start census

Exactly two commits; committer times increase freeze -> build. Ancestry asserted:

    git merge-base --is-ancestor 4229ea1b d01b2b6d  -> true (base is ancestor of freeze)
    git merge-base --is-ancestor d01b2b6d c22602bd -> true (freeze is ancestor of build)

Counters are absent from the base commit (`git cat-file -t 4229ea1b:tools/round53-*.py` -> "not in '4229ea1b...'"), i.e. they landed at the freeze, not before it.

## 2. Counter sha256 at the build == preregistration

    $ git show c22602bd8d83ab26349d1087e916ca537ee4f9d1:tools/round53-replay-code-audit.py | sha256sum
    1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f  -
    $ git show c22602bd8d83ab26349d1087e916ca537ee4f9d1:tools/round53-cited-path-check.py | sha256sum
    1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080  -

Both equal preregistration.json `claims[*].counter_sha256` (C1 1a7a1442…, C2 1afb8b9d…). The same digests hold at the freeze commit and in the current working tree (sha256sum tools/round53-*.py -> identical).

## 3. diff freeze..build on tools/round53-* is empty

    $ git diff --stat d01b2b6d48a54ffe0e475000737d3e302c62e28e c22602bd8d83ab26349d1087e916ca537ee4f9d1 -- tools/round53-
    (no output)
    $ git diff d01b2b6d48a54ffe0e475000737d3e302c62e28e c22602bd8d83ab26349d1087e916ca537ee4f9d1 -- tools/round53- | wc -l
    0

The build commit did not touch either counter. `git ls-tree c22602bd -- tools/` shows exactly the two round53-* blobs (a81a629…, 790cdd7…).

## 4. Base controls committed at the freeze

    $ git ls-tree -r d01b2b6d48a54ffe0e475000737d3e302c62e28e -- .ufo/waves/round-53/controls/
    100644 blob e8f90123d08192ad227a553ede1e321715497a3b	.ufo/waves/round-53/controls/base.c1.out
    100644 blob 6edeaede154193c029af1191390bbc04cd15b60a	.ufo/waves/round-53/controls/base.c2.out

Committed base.c1.out verdict line: `bind=1 sealed=1 code=0 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False`, trailer `exit=1` — matches the seated spec (bind=1 sealed=1 code=0 teardown=1 newrow=0 met=False). Committed base.c2.out verdict line: `fixture=1 lane=0 scenarios=8/8 cited=679 unresolved=16 disclosed=0 undisclosed=16 bad=0 stale=0 dropped=0 met=False`, trailer `exit=1` — matches spec (fixture=1 lane=0 unresolved=16 undisclosed=16 met=False). Both controls fail closed as required. Copies: out/Sc1Freeze/base.c1-committed.out, base.c2-committed.out. Working-tree controls are byte-identical to the committed blobs (sha256sum verified).

## 5. prereg-time-check says pass and re-runs the same

Committed .ufo/waves/round-53/freeze/prereg-time-check.out (at the build commit) says `RESULT pass: no timestamp later than the committer time`, exit=0. My re-run:

    $ python3 tools/prereg-time-check.py --repo . --path .ufo/waves/round-53/preregistration.json --rev d01b2b6d48a54ffe0e475000737d3e302c62e28e
    rev=d01b2b6d48a54ffe0e475000737d3e302c62e28e path=.ufo/waves/round-53/preregistration.json
    committer_time=2026-10-27T03:02:49-03:00 max_future=86400
      ok   line 6: 2026-10-27T06:02:12Z (at/before commit)
    RESULT pass: no timestamp later than the committer time
    exit=0

Byte-identical to the committed output apart from the appended `exit=$?` line I added (out/Sc1Freeze/prereg-time-check-rerun.out; committed and worktree copies also saved). The preregistration working tree is byte-identical to the blob at the freeze commit (sha256 6a7711e1… both).

## 6. Receipts at the build

The committed build receipts (in follow-up commit bc8e6e7f1c53ea6f557001cea1e4d1e8b586c18e "round-53: wave kama-r53-w1 spec (66 seats, v2) and build receipts", which the lane log shows directly on top of c22602bd) carry the claimed verdicts:

- c1-build.out: `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`, each of the 3 replay legs reporting "8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem … 13 root-owned host files" naming libllama-server-impl.so, libggml.so.0.27.0, libggml-base.so.0.27.0, libggml-cpu-zen4.so (and 4 more) — matching the assignment's "8 archive libraries byte-equal, 13 root-owned host files".
- c2-build.out: `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` — matching the assignment.

The current working tree holds uncommitted re-runs of both receipts; their verdict lines are identical to the committed ones (only pids/ports/nonces/inodes and the fleet hash in c2 differ — the fleet repo advanced between runs; both name tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1). Copies of all four variants saved under out/Sc1Freeze/.

## Observations (not defects against the seated checks)

1. The measured receipts are committed one commit after the build (bc8e6e7f), not in the build commit c22602bd itself; the preregistration only pins controls at the freeze, so this is consistent, but the L1 should be aware the "receipts at the build" live in the wave-spec commit.
2. The lane working tree is dirty in .ufo/waves/round-53/measured/ (modified c1-build.out, c2-build.out plus many untracked *-build.out re-runs and measure.sh). Contents still agree with the committed verdicts; flagging so integration does not mistake the uncommitted re-runs for the canonical receipts.

No tools were installed or upgraded (nothing needed; pacman untouched per ruling).

Report written once; artifacts: this file plus out/Sc1Freeze/{evidence-freeze-checks.txt, prereg-time-check-committed.out, prereg-time-check-worktree.out, prereg-time-check-rerun.out, base.c1-committed.out, base.c2-committed.out, c1-build-committed-bc8e6e7f.out, c2-build-committed-bc8e6e7f.out, c1-build-worktree-rerun.out, c2-build-worktree-rerun.out}.
