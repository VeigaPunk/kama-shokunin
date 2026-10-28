# SB01Knowledge — round 64, wave b (kama), item: draft knowledge entry `process-bound-listener`

Seat: SB01Knowledge (leaf; no subagent dispatch). Judged axis: operability. Milestone: draft knowledge entry.
Frozen base: 0c1eff3cb9ac4c11402ab0124c35842f06a436fc; freeze f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (read with `git show` only; no clone, no commit, no lane edit).

## Deliverable

- Draft: `.ufo/waves/round-64/b/out/SB01Knowledge/process-bound-listener.md` (21,171 bytes). Not written into `corpus/knowledge/`; the L1 integrates.
- Frontmatter: `source:` cites S529, S530, S531, S532 (held-queued rows) and held S049, S495, S496, S499 by id and URL; `verified-at:` is f6a4ea9a8b5a876d685b08e7e582ec0723412a4a; `recheck:` is a command.
- Structure: Claim; round-63 failure (MT15 evidence); steps 1-7 (listener inode, holders, executable, argv/environ/maps, parentage and starttime, teardown, reference agreement), each with *Procfs* (quote + location), *Kama reading* (counter line anchors at the freeze), *Observed* (demo output), and *Limits*; what the join cannot establish; numbers with commands; marked opinions.
- Every quoted sentence was re-opened: man pages fetched with curl on 2026-10-28 (man-pages 6.19, footer 2026-02-08), the S049 raw kernel doc, and the held text copies in the lane at f6a4. Result: `quotes OK=27/27`.

## Checks run (all read-only or in my own scratch)

| Check | Result | Evidence |
|---|---|---|
| Man-page quotes (21) | 21/21 OK | `out/SB01Knowledge/recheck-quotes.out` |
| S049 raw kernel doc quotes (2) and anchors | OK; `deprecated in favor` line 8, `tcp6_seq_show()` line 12, `46: 010310AC:9C4C` line 18 | same |
| Held text copies (S495 round-49/51, S496 round-50) (4) | 4/4 OK | same |
| S049 raw digest | `a4da3f43…` = row's raw sha256 | same |
| Counter controls at f6a4 | `controls=76 families=28` (sum of `EXPECT_FAMILIES`, counter lines 58-66) | same |
| Four man pages' digests vs the freeze's retained bytes (S529 `3a50ddef…`, S530 `0f04d789…`, S531 `93394d9e…`, S532 `1fc68168…`) | all four match | `out/SB01Knowledge/source/SHA256SUMS` |

Digests of my fetch, for the L1's record: fd `3a50ddef…`, stat `0f04d789…`, environ `93394d9e…`, cmdline `1fc68168…`, exe `8c9bf02f…`, maps `3a339496…`, S049 raw `a4da3f43…`.

## Findings for the L1 (advisory; not edits)

1. **S049 URL.** The row's URL is the GitHub blob page, which returns HTML (205,095 bytes on the last fetch; 202,667 on an earlier one, so the page renders dynamically). The row's digest is of the raw bytes at `raw.githubusercontent.com`. Suggest the row cite the raw URL. Not edited.
2. **S495 and S499 are two rows for one man page** with the same quoted sentence (S499 recheck 360d, S495 on-release). Possible duplicate; not edited.
3. **S496 row** paraphrases "an inode of 0 means a memory region has no file". The man page's own words are "0 indicates that no inode is associated with the memory region" (proc_pid_maps(5), DESCRIPTION). The draft quotes the man page, not the row.
4. **Quoted `[PT]` rule (S530).** The page marks fields 26-30, 35, 45-52 with `[PT]`; fields 4 (ppid) and 22 (starttime), which the counter reads, are not marked. Confirmed in `out/SB01Knowledge/source/proc_pid_stat.txt`.
5. **Counter-reading observations** (from reading `tools/round64-c1-counter.py` at f6a4; **not run, not exercised by any control**). Candidate targets for the falsify wave:
   - a. `unreadable_old` is recorded (counter line 385) but `grade_binding()` never reads it; `unreadable_own` only covers own-uid tables of processes started at or after the tool (lines 382-384). An older, unreadable same-uid process holding the listener would not fail `bind_holders`. Other-uid unreadable tables are skipped without any record (lines 270-276).
   - b. `maps_ok` accepts any mapping under `/usr/lib/`, `/lib/`, `/usr/lib64/`, `/lib64/` or `/etc/ld.so.cache` by path, without a digest (lines 140-141, 451). `bind_env` checks only environment key names (`LD_*`, `GLIBC_TUNABLES`, lines 434-437), so a system-wide `/etc/ld.so.preload` naming a library under those prefixes is outside both checks.
   - c. The mapped-file digest is taken from the path at check time (`sha256_path(os.path.realpath(real))`, line 334), not from the maps line's `dev:inode`. A file replaced at the same path after load would be hashed as the new file.
   - d. `hold_fresh` uses `>=` on starttime ticks (line 472). Measured: 60 `sleep` spawns gave 2, 1, 2 distinct starttime values in the saved runs (3, 2, 3 in unsaved runs), so ticks are coarse at CLK_TCK=100 and equal starttimes are common. The ancestry check is the ordering that does not depend on ticks.
   - e. The tool-side holder check `_proc_holders()` (`tools/kama-completion-live.py:190-223`) silently skips unreadable fd tables (`except OSError: continue`). The counter's `bind_claim` (line 730) compares the tool's list with the counter's own, which catches a disagreement but not a table the counter itself cannot read (see a).
   - f. Two address policies: the tool's `_listen_inodes()` (`tools/kama-llamacpp-live.py:619-638`) drops wildcard listeners by design; the counter keeps them and fails `bind_listener` (line 410). The verdict is the counter's, so the outcome is safe, but the two readers disagree on the same socket.
6. **Forgery A mechanism confirmed in procfs.** In the demo a forked child inherits the listening fd and appears as a second holder with the same executable digest (`procfs-demo.run1.out`). The holder set must be exactly `{hold pid}`; that rules out this form of sharing.

## Method and bounds

- Did not run the counter, the tool, or any llama-server. No loopback ports were opened by this seat except the demo's own test listener on a random loopback port (run in scratch, which is now removed). Ports 8080 and 34113 untouched.
- The demo (`out/SB01Knowledge/procfs-demo.py`) reads /proc for its own children only; it kills nothing it did not start.
- Read-only git only (`git show`, `git cat-file`) against the lane at f6a4; nothing committed; no lane file written except the draft, the checker, its receipts and this report, all under my own paths.
- Tools: none installed or upgraded. Used the existing `curl`, `python3` 3.14.8 (stdlib only), `getconf`, `sha256sum`. Pacman not touched.
- Scratch `/fast/scratch/hyaku/kama-r64/b/SB01Knowledge` removed after copying the fetched bytes and demo outputs into the out dir.

## Receipts (out dir `.ufo/waves/round-64/b/out/SB01Knowledge/`)

- `process-bound-listener.md` — the draft.
- `recheck-quotes.py` / `recheck-quotes.out` — re-opens sources, checks 27 quotes, prints anchors and counter control count. Re-run it with `python3 .ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.py`. If the L1 moves the entry into `corpus/`, the recheck path in the frontmatter must move with it.
- `procfs-demo.py` / `procfs-demo.run{1,2,3}.out` — procfs join demo (listener inode, holders before and after fork, exe digest, ppid and starttime, runtime-set environment variable, 60-spawn starttime ties).
- `source/` — the fetched bytes (six man-page HTML files and the S049 raw .rst), their `SHA256SUMS`, and the text extractions used for the quote checks.

## Tally

`recheck-quotes: quotes OK=27/27 (exit 0)`; `procfs-demo: 60-spawn starttime distinct values 2, 1, 2 (saved runs)`.
