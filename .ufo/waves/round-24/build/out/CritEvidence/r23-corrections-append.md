Candidate append (L1 decides placement: LOG.md §round 24 and/or
corpus/lessons/round-24.md). Append-only: it supersedes the wording of
LOG.md:1417-1420 (d1b9d95) and the prereg expected_after[6] gloss without
editing them; filed `.ufo/reports/round-23/kama.md` (fleet 410b511) and
`corpus/lessons/round-23.md` (lane 0df800e) stay byte-unchanged.

```text
- Correction to the round-24 correction (LOG.md:1417-1420, d1b9d95):
  (a) "68 reports" is not in filed `.ufo/reports/round-23/kama.md`
  (410b511); that report gives falsify 73 seats, 4 dead (:148-155), which
  is 69. The stale count is in `corpus/lessons/round-23.md:178` ("73 seats
  dispatched (68 reports; dead: <4 names>"), internally 73-4≠68. Durable
  falsify reports: 69 = 73 spec items minus RowC01Clean, RowF07LogFollow,
  RowF09SignatureProgram, CritOpenHonesty; RowC03FabricatedFull.md is
  6618 bytes, mtime 16:10:15Z. Round total 141 seats, 5 without a report
  (build RevClaimScope + those 4).
  (b) The "56" (report :34-35; lesson :109-110, :174 M7) is a
  `grep -E 'repo-state-grid-|/tmp/kama-r23' | wc -l` count at 16:33:38Z
  in the KamaR23-2 session transcript, not an inventory of FIFO-blocked
  git processes. The same call kept 40 rows (pid, start, argv cut at 200
  columns) from a different pattern ('repo-state-grid-|kama-r23|refusal'),
  head -40. Those 40: 38 git, 1 gpg-agent and 1 scdaemon (homedir
  /tmp/kama-r23w2/ExecOldGitRun/gnupg); started 12:18:54-13:29:37 -03; 37
  provably match the counting pattern, 3 are truncated before the path.
  From retained bytes, 19 tie to FIFO fixtures (grid rows 21=F14 mailmap-fifo x17,
  37=F30 include-fifo x1, one .../variants/fifo path); 5 sit at rows 20
  (F13) and 00 (C01), which are not FIFO rows and did not time out in the
  final frozen grid; 14 are truncated. The other 16 counted processes
  have no retained identity. pkill on '-C /tmp/repo-state-grid-' and
  '/tmp/kama-r23w2/' at 16:33:46Z left that count at 0. Retained copy of
  the 40 rows: `.ufo/waves/round-24/build/out/CritEvidence/`.
  Corrected reading: 56 round-owned fixture processes (git plus at least
  two gpg daemons) were killed; 40 identities retained in the session
  transcript, only partly shown to be FIFO-blocked.
```
