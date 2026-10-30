# SB04KnowledgeRevise — round 64, wave f (kama): revised knowledge entry `process-bound-listener`

Seat: SB04KnowledgeRevise (leaf, advisory; no subagent dispatch). Axis: operability. Milestone: revise knowledge entry.
Read first: `.ufo/waves/round-64/controls/freeze.txt` (base `0c1eff3c`, freeze `f6a4ea9a`, AMENDMENT 1 / 1a / 1b, measured tip `23b3fdb1`).

## Deliverable

- **Revised entry**: `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/process-bound-listener.md` (208 lines) — the revision of the wave-b draft `.ufo/waves/round-64/b/out/SB01Knowledge/process-bound-listener.md` to the amended counter at `23b3fdb1a925129a9961cf551f6d40bf251602cb`.
- **Checker + receipts**: `out/SB04KnowledgeRevise/recheck-quotes.py`, `recheck-quotes.out` (31/31 quotes OK), `procfs-demo.py`, `procfs-demo.run{1,2,3}.out`, `counter-run1.out` / `counter-run1.err`, `citation-audit.txt` / `citation-ranges.txt` (every counter line the entry cites, printed with the source line it points at), `source/` (the fetched bytes + `SHA256SUMS`).
- **Shared source dir**: `.ufo/waves/round-64/source/` gained `proc_pid_exe.5.html`, `proc_pid_maps.5.html`, `proc_net_tcp.v7.2.rst` and `SB04KnowledgeRevise-fetch.sha256` (new files only; the six files already there are byte-identical to my fetch — digests match).
- Nothing else was written in the lane; nothing was committed; no lane source file was edited.

## What changed against the wave-b draft

1. **Every counter line number re-derived at `23b3fdb1`** (the draft's numbers were from the freeze commit `f6a4ea9a`). The draft's `recheck:` command is kept, with the new numbers.
2. **The provenance trio is kept** — `source:` (S529-S532 plus held S049/S495/S496/S499), `verified-at: 23b3fdb1a925129a9961cf551f6d40bf251602cb`, `recheck:` (a command that must print `quotes OK=31/31`). Two already-registered sources are added to the `source:` line because two of the new observations rest on them: **S533** (`proc_pid_status(5)`, `TracerPid`/`State`) and **S534** (`namespaces(7)`, `/proc/pid/ns/`), both admitted in `corpus/lessons/round-64.md` §Gate and both already fetched in `.ufo/waves/round-64/source/`.
3. **New observations added**, each with its limit: exact argv; environ allowlist **with values**; namespaces; `TracerPid`; run state; reference-file identity set from the counter's own reference server; the receipt's own request/answer binding; unreadable fd tables of **any uid**; kill-on-exit.
4. **Wave-b / acknowledged survivors carried as limits**: non-dumpable pre-existing helper; `/proc/<pid>/mem` writes; post-release holder; `/usr/lib` blanket exemption; initial-environment visibility.
5. **Counts re-derived with their commands** (91 controls / 30 families / 8 evaluator plants / 31 quotes / start-tick ties / digests), each with the command that prints it.
6. **Quotes re-opened by this seat**: every man page re-fetched with `curl` on 2026-10-30, the S049 raw kernel doc re-fetched, the held text copies of S495/S496 read at `23b3fdb1`; 31/31 quotes OK (the draft's 27 plus the four new ones).
7. **Claim wording tightened** to the readable holder set, with the pre-tool unreadable exclusion named beside the claim; the numbered observations now match the step headings (1–8), and the "binding" sentence says steps 1–6.
8. **The MT06 evidence is cited from where it exists**: seat MT06MapsLib wrote no report file (recorded in `corpus/lessons/round-64.md`), so its six-of-nine result is cited from `.ufo/waves/round-64/b/b-results.json`, with each of the nine cases named.

## Line-number re-derivation (all at `23b3fdb1`)

Command: `git show 23b3fdb1a925129a9961cf551f6d40bf251602cb:tools/round64-c1-counter.py | grep -n …` (the checker's own output, `recheck-quotes.out`, prints the whole table).

| Function | line | | Function | line | | check | line |
|---|---|---|---|---|---|---|---|
| `listeners` | 250 | | `file_set` | 373 | | `bind_listener` | 480 |
| `holder_pids` | 270 | | `ns_of` | 382 | | `bind_holders` | 483 |
| `stat_fields` | 319 | | `holder_record` | 391 | | `bind_exe` | 487 |
| `ppid_chain` | 329 | | `collect` | 434 | | `bind_argv` | 496 |
| `read_maps` | 341 | | `grade_binding` | 470 | | `bind_env` | 503 |
| `expected_argv` | 553 | | `holders_signature` | 565 | | `bind_ns` | 505 |
| `probe_fails` | 714 | | `score` | 760 | | `bind_trace` | 507 |
| `free_port` | 863 | | `draw_requests` | 875 | | `bind_state` | 509 |
| `probe` | 892 | | `reference_run` | 932 | | `bind_maps` | 536 |
| `pid_gone` | 971 | | `kill_if_same` | 989 | | `bind_ancestry` | 538 |
| `witness_run` | 999 | | `main` | 1781 | | `hold_fresh` | 544 |
| `receipt_req` | 815 | | `receipt_ref_text` | 821 | | `receipt_ref_usage` | 826 |
| `bind_ref_files` | 840 | | `bind_stable` | 846 | | `bind_claim` | 854 |
| `teardown_observed` | 857 | | `EXPECT_FAMILIES` | 66 | | `EXPECT_CONTROLS` | 76 |

Constants at the same commit: `MODEL_SHA` 56, `SERVER_SHA` 57, `EXPECT_EVAL_SELFTEST` 62, `MAX_COLLATERAL` 63, `ENVELOPE_CAP` 64, `SCENARIO_CAP` 65, `LIBS` 91, `RECEIPT_BIND` 88, `SYSTEM_PREFIXES` 150, `SYSTEM_FILES` 151, `_TOOL_ENV_KEYS` 159, `TOOL_CHILD_ENV` 162, `REF_FILES` 370, `NS_NAMES` 379.

Tool-side anchors (the tool is byte-identical to the freeze commit, sha256 `a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c` at both commits): `tools/kama-completion-live.py` `_proc_holders` 190-223, child argv 301-304, child env filter 322-323, `--ctx`/`--threads` defaults 646-647; `tools/kama-llamacpp-live.py` `_listen_inodes` 619-639.

## The nine new observations, each with its limit

| # | Observation | Where | Limit recorded in the entry |
|---|---|---|---|
| 1 | **exact argv**: the holder's whole `cmdline` list must equal `expected_argv()` | `bind_argv` 491-496, `expected_argv` 553-558 | it is compared against the list the counter believes the tool used, so a tool with different default flags fails (false reject); a self-rewriting argv area still passes it — `bind_exe`/`bind_maps` decide identity |
| 2 | **environ allowlist with values**: every key the holder shows must be one of the counter's own `PATH`/`HOME`/`LANG`/`LC_ALL` **with the same value** | `env_ok` 498-503, `expect_env` 449-450 | only the *initial* environment is visible (S531): a runtime `putenv` is outside the check; an in-place same-length rewrite of the env block *is* visible (wave-b MT05 F4/F5); an empty environment passes vacuously [inference from code] |
| 3 | **namespaces**: the holder's `mnt`/`pid`/`net`/`user`/`ipc`/`uts` links must equal the counter's | `ns_of` 382-389, `self_ns` 448, `bind_ns` 505-506 | it is "same as the counter", not "the pinned namespace"; a copy of the counter's namespaces is equal to it; namespace *contents* are not seen |
| 4 | **TracerPid**: must be 0 | 421-422, `bind_trace` 507-508 | a tracer that detached, or a process resumed between the two snapshots, is not seen |
| 5 | **run state**: the state letter must be `S`, `R` or `D` | 419-420, `bind_state` 509-510 | a letter at two instants, not a history; `T` (stopped) and `t` (tracing stop) fail |
| 6 | **reference-file identity**: the holder's `(path, dev, inode)` set must equal the counter's own reference server's | `file_set` 373-377, `REF_FILES` 957, `bind_ref_files` 835-840 | it pins file identities of the pinned build, not the bytes the process runs from memory; set equality is strict (a lazily loaded library would fail a genuine run — not seen in three honest runs) |
| 7 | **receipt request/answer binding**: the receipt's captured request must equal the request the counter drew, and its answer/usage the reference server's | 811-826 (`receipt_req`, `receipt_ref_text`, `receipt_ref_usage`) | the reference answers the counter's request, not the receipt's; a tool that altered the request on the wire fails `receipt_req` (intended) |
| 8 | **unreadable fd tables of any uid** are recorded, re-read 4×50 ms, and fail the run when the process started at or after the tool | `holder_pids` 270-317, `collect` 452-455, `bind_holders` 483-486 | `unreadable_own` is filtered by **start time**, not by uid (the name is a leftover); a pre-existing helper of any uid lands in `unreadable_old` (a count) and is never graded |
| 9 | **kill-on-exit**: every holder the counter saw is SIGKILLed while it still carries the observed start ticks, and the tool's process group is killed; the tool runs in its own session | `kill_if_same` 989-997, `witness_run` 1027, 1095, 1097 | a holder that appears only after the counter's release is not seen (see survivors) |

## The five survivors carried as limits

Each is stated in the entry next to the check it weakens, with its wave-b evidence and the freeze's disposition.

1. **Non-dumpable pre-existing helper** — wave-b MT01 O3/O4 and MT08 f2 were accepted at the freeze tip; the amended counter still grades only tables of processes that started at/after the tool (`unreadable_own`). *Inference from the code at this commit:* the amendment widened the recording to any uid but kept the start-time filter, so the case is not closed. Acknowledged, not fixed (`controls/freeze.txt` AMENDMENT 1).
2. **`/proc/<pid>/mem` writes** — wave-b MT05 F2 patched 9 bytes into the live server's own mapping and changed the served fingerprint with no file on disk changed; no check reads the process's memory. Acknowledged, not fixed.
3. **Post-release holder** — wave-b CR03 §3.4 (K5): the two binding snapshots are taken before the release and the teardown check is "recorded holders gone + port closed", so a holder that exists only after the release is invisible. *Inference from the code at this commit:* the release/teardown ordering is unchanged, so the coverage boundary is the same. Acknowledged, not fixed.
4. **`/usr/lib` blanket exemption** — wave-b RV02 D7: `SYSTEM_PREFIXES` 150-151 are trusted by path, not by digest, in `maps_ok` (524-525). Acknowledged, not fixed. *Narrowing recorded in the entry:* at this commit the *shadowing* case wave-b MT06 d measured is caught instead by `bind_ref_files` (the shadowed `/usr/lib` mapping differs from the reference's in `dev`/`inode`); what the exemption still leaves open is an **in-place content change** of a system-prefixed file, because such a file is neither hashed nor identity-changed.
5. **Initial-environment visibility** — S531's own words; the allowlist check is only as good as that view (see observation 2 above). Acknowledged, not fixed.

Wave-f peer reports were not used: no wave-f *report* for this item's subject was published when this seat ran (`corpus/lessons/round-64.md` records the earlier wave-f stop with zero reports), so every survivor above is wave-b measured or the freeze's own acknowledged list. One wave-f seat's raw counter output that was already in the shared evidence dir (`.ufo/waves/round-64/f/out/RV08C1CounterAmended/run.stdout`) prints the identical line to this seat's run, which corroborates the run but is not a report and is not cited as one.

## Checks run (all in my own scratch or read-only in the lane)

| Check | Result | Evidence |
|---|---|---|
| Man-page, namespaces(7) and S049 quotes re-opened by this seat (curl, 2026-10-30) | 31/31 OK | `out/SB04KnowledgeRevise/recheck-quotes.out` |
| Digests of the fetch vs the freeze's retained bytes | fd `3a50ddef…`, stat `0f04d789…`, environ `93394d9e…`, cmdline `1fc68168…`, status `1596cd27…`, exe `8c9bf02f…`, maps `3a339496…`, namespaces.7 `f8e08716…`, S049 raw `a4da3f43…` (matches the S049 row) | same |
| Held text copies of S495/S496 at `23b3fdb1` (round-49/50/51 copies) | 4/4 OK | same |
| Counter line anchors re-derived at `23b3fdb1` | 30 families, 91 controls; every cited line printed | same |
| Tool byte-identity across the freeze and the tip | `a0c26e14…` at both | same |
| Procfs demo re-run on this host | 60-spawn start-tick ties 2, 2, 1; runtime-set env var not visible in `/proc/self/environ` | `procfs-demo.run{1,2,3}.out` |
| Unmutated C1 counter at the tip, fresh `--work` | `met=True`, 91/91 controls, `eval_selftest=8/8`, `errors=0`, exit 0, 75.52 s, empty stderr | `counter-run1.out` / `.err` |

## Bounds, method, hygiene

- Scratch root `/fast/scratch/hyaku/kama-r64/f/SB04KnowledgeRevise` (clone + `work-1` + `source/`); removed before this report is finalised except the receipts copied into the out dir.
- Clone recipe exactly as briefed: `git clone -q --shared` of the lane, `git rev-parse --show-toplevel` asserted equal to the clone, checked out `23b3fdb1`. The clone is unmodified (no commit, no patch, no mutant) — this seat's item is a revision, not a falsification.
- Read-only git in the lane (`show`, `rev-parse`, `cat-file`); no `git add`, no commit, no jj, no push. No lane source file outside my report/out paths was touched; the three files added to `.ufo/waves/round-64/source/` are new names, no existing file overwritten.
- One live run: the unmodified counter from the clone's `tools/`, `--repo <clone> --tip 23b3fdb1 --work <fresh>`; it started its own llama-servers on unregistered loopback ports and killed every holder and the tool's process group on exit. No port 8080/34113 was touched and no process this seat did not start was killed.
- Tools: none installed or upgraded (curl 8.23.0, python3 3.14.8, git, coreutils were already present). **No pacman transaction.** Nothing written to `~/.local/bin` or any PATH directory.

## Findings for the L1 (advisory; not a verdict on C1)

1. `unreadable_own` is a **misnomer** in the amended counter: the filter is the holder's start time, not its uid, so the name now understates the set (any uid, started after the tool). Renaming it to `unreadable_new` would make the survivor in limit 1 above readable at a glance. Not edited (instrument file, outside this seat's bounds).
2. `bind_ref_files` compares the holder's file set with the **reference server's** file set. It is an equality of two different processes' mappings, so it is strict by construction; a future lazy load in one process and not the other would fail a genuine run. No such case was observed in three honest runs, but the check is sharper than "the pinned set" in the predicate.
3. `bind_env` is vacuous over an empty environment, and it reads only the initial environment, so the allowlist is a statement about the environment *at execve*.
4. The entry's `recheck:` command still prints `score_run` (1869) because the pattern's `score` is a prefix of it; the entry says so explicitly instead of hiding it.
5. The wave-b draft's `corpus/knowledge/` landing is still the L1's: the entry is delivered in the out dir, `corpus/knowledge/process-bound-listener.md` was not created by this seat, and `corpus/SOURCES.md`'s planned `queued → mined` flip for S529-S534 still waits for that file to exist (`corpus/lessons/round-64.md` §Gate, "Status of the planned flips").
6. **Overlap with the wave-f peer review.** `.ufo/waves/round-64/f/RV07KnowledgeEntry.md` (published while this seat was running) reviews the same wave-b draft and asks for the same repairs the revision makes: say "every observed/readable holder" with the old-unreadable exclusion beside the claim (done, claim item 2), teach the receipt-replay binding (done, step 8), replace the flag-pair/denylist/maps descriptions with the amended candidate's behaviour (done, step 4), separate the historical freeze-era numbers from the current ones (done: every count is labelled `23b3fdb1`), keep the finite-sample limit on reference agreement (done, step 7), and keep the stat-based maps comparison as an opinion with the btrfs caveat (done, Opinion). The two artifacts are complementary: RV07 reviews the draft, this seat delivers the revised entry. This seat did not edit RV07 and did not use it as a source of truth for the counter's behaviour — every counter claim in the entry was re-derived from the blob at `23b3fdb1`.
7. **One citation corrected from the draft.** The draft's evidence paragraph cited only `forge.out`; the revised entry gives the command for `sleeper.out` as well.

## Artifact paths

- Entry: `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/process-bound-listener.md`
- Checker: `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/recheck-quotes.py` → `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/recheck-quotes.out`
- Demo: `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/procfs-demo.py`, `procfs-demo.run{1,2,3}.out`
- Counter run: `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/counter-run1.out`, `counter-run1.err`
- Fetched bytes: `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/source/` (+ `SHA256SUMS`) and `.ufo/waves/round-64/source/{proc_pid_exe.5.html,proc_pid_maps.5.html,proc_net_tcp.v7.2.rst,SB04KnowledgeRevise-fetch.sha256}`
- This report: `.ufo/waves/round-64/f/SB04KnowledgeRevise.md`

## One-line counter output (the unmodified C1 counter at `23b3fdb1`, this seat's single run)

`tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]` (exit 0; `recheck-quotes: quotes OK=31/31`)
