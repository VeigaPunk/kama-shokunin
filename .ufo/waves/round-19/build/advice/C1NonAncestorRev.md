VERDICT: partial - bytes verify at off-master revs (confirmed); the checker never tests ancestry, and ancestry should gate publication-grade rows, not byte verification.

Scope: C1NonAncestorRev, probe in `/tmp/kama-r19-C1NonAncestorRev` (snapshot 8bf99cae, detached). The lane moved to 7229fa95 during the run; its committed checker adds stale-token detection, `round-19.md` to the default docs and 7 selftest cases, but no ancestry check. Every verdict below was re-run against the committed checker and matches the snapshot. Commands, exits and receipts: `/tmp/kama-r19-C1NonAncestorRev/out/RECEIPTS.md`.

## Executed matrix (exit codes; committed checker 7229fa95)

| Case | Rev | Bytes in row | Exit | Result |
|---|---|---|---|---|
| A1 | 519fea74 (local branch, parent = master) | its own | 0 | verified |
| A2 | ccdb0755 (orphan, no ref) | its own | 0 | verified (before gc) |
| P1 | ccdb0755 after `reflog expire` + `gc --prune=now` | its own | 1 | mismatch, observed absent |
| A3 | 519fea74 | master's bytes | 1 | mismatch, observed = rev's own digest |
| A4 | 8bf99cae (master) | off-branch bytes | 1 | mismatch |
| A5 | 1b85a24e (ancestor) | off-branch bytes | 1 | mismatch |
| B1 | eaf40f86 (origin/cursor/amazing-readme-a57c, not on master) | its own | 0 | verified |
| B2 | eaf40f86 | master's bytes | 1 | mismatch |
| B3 | eaf40f86 | path absent | 1 | mismatch |
| C0 | 1b85a24e | its own | 0 | verified |
| R0 | real registry, 3 rows, copy | | 0 | 3/3 verified |
| O-A1 | A1 rev, fresh clone of origin | | 1 | absent on origin |
| O-B1 | B1 rev, fresh clone of origin | | 0 | verified |
| O0 | real registry vs fresh clone of origin | | 0 | 3/3 verified |

Gated prototype (`--require-ancestor-of master`, same matrix): A1, A2, B1 and O-B1 return exit 1 `off-ref` although their bytes match; C0, R0 and O0 stay 3/3 or exit 0. The prototype is a diff in `out/proto/ancestry-gate.diff`, not landed.

## Answers

1. **Bytes still verify off-master.** `observed_sha256` equals the digest of the rev's own blob (A1, B1). The digest is rev-specific: the same path with another rev's bytes fails (A3, A4, A5, B2). The checker reads `rev:path` and never falls back to master.
2. **Ancestry should matter, as a gate on publication.** Three observed reasons:
   - *Verdict depends on local object presence.* A1 verifies in the lane and fails on a fresh clone of origin (O-A1). A reviewer cannot reproduce it.
   - *Verdict flips under gc with no change to registry or docs.* A2 passes, then P1 fails after gc. `git-gc(1)` on this host gives the prune default as "2 weeks ago". I simulated it with `--prune=now`.
   - *The lane's convention checks ancestry; the new checker drops it without a recorded decision.* Committed at 7229fa9: `corpus/lessons/round-18-verifier-spotcheck.md:26` (`merge-base --is-ancestor <h> refs/heads/master`); also round-11:43, round-12:32-34, round-16:26, round-17:43.
   - *Current rows are unaffected.* `1c325b2e`, `eb78788b` and `1b85a24e` are ancestors of master and of 7229fa9 (exit 0 each). The gate changes nothing today.
3. **Recommended shape (L1 decides; not landed):**
   - Default-on gate: `git merge-base --is-ancestor <rev> refs/remotes/origin/master`, status `off-ref`, counted as failing. One git call per row. The prototype's selftest passes (12/12), but I did not add an off-ref selftest case, so the probe matrix is the only evidence for it.
   - Published side branches (B1) are reproducible from origin. If the lane wants them, use an explicit per-row ref rather than dropping the gate. "Reachable from any origin head" would admit B1 and still reject A1 and A2 (A1 is contained only by the local branch `c1probe/side`).
   - Split `observed=absent`. An absent rev and an absent path print the same git text here (P1 and B3: `path … exists on disk, but not in <rev>`). Running `git cat-file -t <rev>` first would separate them.
4. **Not tested:** short-rev tokens (the committed selftest covers them); the `master` vs `origin/master` distinction (they were equal in every run); a fetch-freshness failure mode, which I expect from the design but did not run [INFERENCE].

## Lane state and disclosures

- Lane writes: none, apart from this report. Lane reads are listed in RECEIPTS. Two `git status --short` runs were made without `GIT_OPTIONAL_LOCKS=0`; git may refresh the index stat cache, and no content change was intended.
- Origin moved during my session: `origin/master` was `7229fa95` at my final clone.
- The stated round-start tip `1b85a24e` is 5 commits behind the snapshot tip `8bf99cae`. The registry is consistent with both.
- Installs or updates: none.
