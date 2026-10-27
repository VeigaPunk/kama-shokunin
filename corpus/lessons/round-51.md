# kama round 51 lesson

author: kama L1 (agent `KamaR51a2`, attempt 2); wave seats' findings integrated by the L1 (named per row)
date: 2026-10-27
base: `57a2e25bf702b03aa61f9265e968cf68058ecb82` (round-50 verifier spot-check; lane remote tip at launch; attempt 1 left no lane writes)
freeze: `804bde75164444bdf0fe6783d7aa45774bf562bd` (preregistration `.ufo/waves/round-51/preregistration.json`; freeze time of record 2026-10-27T03:38:24Z, the committer time — the file's `frozen_at_utc` is 6 s late, erratum `.ufo/waves/round-51/freeze/frozen-at-erratum.md`, Mistakes #1)
build: `b6bed925b032ac2c19b63ef4af358ebdd5922c26`; build-fix `73bf2a7a17104a62a3e442912c8776cbd8dedbd5` (ledger regenerated); build-fix 2 `138af25b963450b6520794995605fa7dbbcd87e0` (digest-ledger scope)
measured: SCORECARD §Round-51 measured results

## Claims

- **C1 operability 8→8 — the replay's server is the file the replay extracted, sourced on S499.** `tools/kama-llamacpp-live.py` records `server_exe`: the running server child's image opened through `/proc/<pid>/exe` (proc_pid_exe(5): opening the link opens the executable), its dev, inode, size and sha256. `tools/kama-live-replay.py` refuses a rerun whose `server_exe` is absent, of another digest, or of another dev:inode than its own extracted `<work>/server/<member>`, and records that member as `own_server`. Round-50 seat J4Decoy's decoy (exec the host's b11909 install, sanitize honestly) met the round-50 counter because a digest says which bytes run, not which file. Counter `tools/round51-replay-exe-audit.py`: the round-50 bind and teardown legs unchanged plus `own` (the counter opens `/proc/<pid>/exe` itself and compares with the extracted member, the receipt and `own_server`) and `newrow` (a proc_pid_exe(5) row). Base: `bind=1 own=0 teardown=1 newrow=0 met=False`.
- **C2 calibration 7→7 — every deletion graded, the A-row rule as declared, every loss disclosed by name.** `tools/append-only-audit.py` v6: default threshold 1 (v5 graded only events of 20+ lines: 5 of 106 events); an A-row file's deleted registry row whose id the commit still holds with every cell but status, recheck and used-by byte-equal is `permitted`, not graded (58 lines); `registry/append-only-disclosures.tsv` names every graded line not held at the tip by commit, file, key sha256, count and mechanical class (166 lines in 51 events), and a bad row exits 1. Counter `tools/round51-append-audit-v6-check.py`: nine constructed scenarios and the counter's own recomputation of lost lines from git diffs, key for key, in every whole-file-graded file. Base: `fixture=0 lane=0 met=False`. Takes `considerthese/2026-10-26.md` proposal 1 (flag deletions in append-only files) and round-50 closure R6 (the sub-20 threshold hid the real `LOG.md` loss at `ed135b3c`).

Measured values: SCORECARD §Round-51 measured results.

## Gate

| Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why |
|---|---|---|---|---|---|
| S499 | admit (tier A, mined) | https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html | 2026-10-27T03:27:36Z (text copy `.ufo/waves/round-51/c1/proc_pid_exe.5.txt`; man-pages 6.19, page dated 2026-02-08) | "This symbolic link can be dereferenced normally; attempting to open it will open the executable." (§DESCRIPTION) | grounds reading the running image itself — fstat dev/inode and hash of the opened fd — instead of a path the tool was handed |

Rejects (each grounded by a command or a control):
- **Reject an exe digest alone as proof of which file a replay runs.** Round-50 seat J4Decoy: a replay exec'ing the host's own install met the round-50 counter with the frozen digest. The own leg compares dev and inode with the replay's extracted member. Flip: never.
- **Reject `readlink(/proc/<pid>/exe)` (the path) as the identity.** The link text can name a path that now holds another file (renamed over) or carry ` (deleted)`; only the opened image's fstat is the running file. Flip: never.
- **Reject a member path's dev and inode as proof of extraction when the file has other links.** Seat J4Hardlink: a hardlink of the host install at `<work>/server/<member>` shares the host file's inode and passes the counter's own leg; the replay now refuses a member whose link count is not 1. Flip: never.
- **Reject a disclosure ledger that may disclose deletions made after it existed.** Seats K2Cheat, K2Design: a ledger accepting new rows blesses any later damage. A ledger read from the revision now discloses only commits before its own introduction; later deletions are restored by append. Flip: never.
- **Reject a disclosure ledger whose rows are not bound to real deleted lines.** The four bad-disclosure scenarios (junk key, over-count, wrong class, no event) each exit 1 in the C2 counter's fixtures. Flip: never.

## Mistakes

| # | Class | Evidence | Captured-by | Fix (shown able to fail) |
|---|---|---|---|---|
| 1 | Anticipated timestamp written into a frozen file (false timestamp, 6 s ahead) | `.ufo/waves/round-51/preregistration.json` line 6 `2026-10-27T03:38:30Z`; freeze commit time 03:38:24Z; `.ufo/waves/round-51/freeze/prereg-time-check.out` → `FLAG line 6 ... later than commit by 6s`, `RESULT fail`, exit 1 | KQ64 `tools/prereg-time-check.py` (it fired) | appended erratum `.ufo/waves/round-51/freeze/frozen-at-erratum.md`; procedure: write `frozen_at` from `date -u` at write time, never a planned time; the KQ64 receipt is itself the failing check |
| 2 | Loop variable shadowing: the disclosure loop reused the commit index `i`, so a later file of the same commit graded against the wrong window | build run with vs without the ledger: event `ccc4bb31` `corpus/lessons/round-16.md` `restored_max` 0 → 11 (`restored_best` b8e485cc, a commit before the event) | none in the selftest at the time; the L1's with/without-ledger diff of the summary (restored 18 → 26, regressed 0 → 8) | renamed to `di`; selftest `v6-two-files-one-commit` fails on the buggy copy (`.ufo/waves/round-51/c2/shadow-index-proof.out`: `AOA_SELFTEST pass=46 fail=1`) and passes on the tool (47/47) |
| 3 | A same-round restoration made a disclosure row an over-count | the build added the blank separator line `97c864be` had removed from `corpus/SOURCES.md`; C2 at `b6bed925`: `lane=0`, `bad_disclosures 1` (`.ufo/waves/round-51/measured/c2-build.out` history, build-fix `73bf2a7a`) | the tool's over-count rule (a disclosure must name an unheld line) | the ledger is regenerated after every build that touches a declared file; the over-count rule is the check that fails |
| 4 | A self-description sentence false for one round: the SCORECARD banner says every replaced authority banner is appended byte-exact under §Superseded head banners; round-50 integration `1c030f18` replaced the round-49 banner and appended nothing | v6 at threshold 1: event `1c030f18` `SCORECARD.md` graded 1, unrestored (ledger row at `73bf2a7a`); v5 at threshold 20 never saw it | append-only-audit v6 (threshold 1); nothing before | the round-49 banner is appended byte-exact this round, the ledger row becomes an over-count and is removed; the over-count rule is the check that fails if the banner is dropped again |
| 5 | Report figure off by one (round-50 closure R1) | round-50 report: rows `237 → 240`; the cited command prints 236 → 239 at `26ecba64`/`5a1e29a1` | the closure's re-run of the command | the round-51 report computes both endpoints from `git show <rev>:corpus/SOURCES.md` with the cited command and pastes the outputs |

## Errata (round-50 closure routed defects)

- **R1:** the round-50 report's `Row count` line should read **236 → 239** (`git show 26ecba64:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 236; at `5a1e29a1` → 239).
- **R4:** `corpus/lessons/round-50.md` Gate reject 2 says "the counter re-opens the pathname O_NOFOLLOW, fstat-checks dev/inode, then hashes". That is what `tools/kama-llamacpp-live.py` `model_mapping()` does. The counter `tools/round50-replay-bind-audit.py` `mapped_model()` uses `os.stat(path)` (follows symlinks) and then hashes by path in a second open. The reject stands; its reason belonged to the live tool.
- **R5:** S498's `teaches` cell quotes §4.5 as "A code fence is a sequence of at least three consecutive backtick characters or tildes." The source reads "... backtick characters (`) or tildes (~)."; the two parentheticals were dropped without an ellipsis. The row is immutable outside status/recheck/used-by (A-row), so the correction lives here. The blank separator before `## Paths` that the S498 build removed is back since `b6bed925`.
