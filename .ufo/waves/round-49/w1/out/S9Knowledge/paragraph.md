## Round 49 — execution witness for a replay, and a bounded archive member (appended 2026-10-26; S494, S495)
source: S494 (llama.cpp `tools/server/README.md` at caa8191df159f764fb0160e3d2fc6be008948aee = b11909: §POST `/tokenize` 686-729, `with_pieces` 696, piece type 700; §POST `/detokenize` 731; text copy `.ufo/waves/round-49/c1/server-README-caa8191d.md`); S495 (`proc_pid_exe(5)` §DESCRIPTION, text copy `.ufo/waves/round-49/c1/proc_pid_exe.5.txt:75-76`); own-work `tools/round49-replay-witness-audit.py` (frozen, sha256 `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1`), `tools/kama-llamacpp-live.py` (`hold_for_witness` 285, `verify_archive_member` 212), `tools/kama-live-replay.py` (`--witness-dir` 275-281)
verified-at: 2026-10-26 — lane measurement at the build 74558c71 (`.ufo/waves/round-49/measured/c1-build.out`) replaying `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`; three own runs at HEAD 122c4ee9 with the host b11909 install (`.ufo/waves/round-49/w1/out/S9Knowledge/`)
recheck: rerun the frozen counter after any change to the hold, the observer or the archive check; `tools/kama-llamacpp-live.py --selftest` and `tools/kama-live-replay.py --selftest` cover the stable refusal tokens and the flag plumbing

Round 48 made a receipt replayable, but the replay still reported only on
itself: a replay that copied captures without ever running a server met the
round-48 counter (seats K2Cheat, K2Urlswap; closure R5). Round 49 lets a
process outside the replay look at the server while it is up.

**Protocol.** `--witness-dir D` (an existing directory,
kama-llamacpp-live.py:1586-1587) is passed by `kama-live-replay.py` to
`kama-llamacpp-live.py` (275-281). The live tool holds the server *after* its
captures and both probe runs and *before* teardown (1860-1866), so the
witnessed process is in the ready state, not loading. It writes `D/ready.json`
atomically (`ready.json.tmp` + `os.replace`, 292-297) as
`{schema: "kama-live-witness/v1", port, pid, written_utc}`, `pid` being the
llama-server child itself, then waits until `D/release` exists, the child
exits, or `--witness-timeout` (default 120 s) passes (298-302). The receipt
gains `witness {schema, dir, port, pid, released, waited_ms}`. The tool records
only that it waited, never what the observer saw (285-291).

**What the observer checks.** The frozen counter
`tools/round49-replay-witness-audit.py` reads `ready.json` and, while the
replay is blocked in the hold, uses its own copy of the frozen constants
(`observe`, 258-289):

- *exe.* sha256 of `/proc/<pid>/exe` equals the frozen `llama-server` digest
  `35ac50fb…7ff0`. S495: opening that symbolic link opens the running
  executable, so this names the binary the process really runs, whatever path
  or wrapper started it.
- *listener.* A LISTEN row (state `0A`) for 127.0.0.1 or ::1 on the announced
  port in `/proc/net/tcp{,6}` whose socket inode is among `/proc/<pid>/fd`
  (193-232), so the announced port belongs to the announced pid.
- *model.* The `-m` value of `/proc/<pid>/cmdline`, resolved against
  `/proc/<pid>/cwd` when relative, hashes to the frozen `stories260K` digest
  `270cba1b…256d`.
- *nonce.* A fresh `kama witness <16 hex>` is POSTed to `/tokenize` with
  `with_pieces: true`; every returned piece must equal the counter's own
  decoding of `tokenizer.ggml.tokens[id]` from the GGUF it downloaded from the
  pinned URL and hashed itself (U+2581 read as a space), and `/detokenize` on
  those ids must return the nonce (one leading space allowed). S494 fixes the
  request/response shapes; a piece is a string, or a byte list for non-UTF-8
  pieces (README:700), and the counter requires a string.

Then the counter writes `D/release`, requires the replay to exit 0 with `match`
true and the rerun receipt to say `witness.released: true`, and requires the
pid gone and the port refusing afterwards (292-340).

**Observed.** At the build 74558c71 the counter reports
`witness=1 cap=1 newrow=1 witnessed=3/3 met=True`
(`.ufo/waves/round-49/measured/c1-build.out`): pids 254977/port 33749,
255370/port 45335 and 255954/port 36679, each "exe+listen+model ok" with its
nonce round-tripped; the `newrow` leg finds two rows new since the base, one of
them naming the README at caa8191d and `/tokenize` — S494
(`corpus/SOURCES.md:247`), with S495 at 248. Controls stay `met=False`: at the
round-48 closure 438127bc nothing accepts `--witness-dir`, so all three legs
fail with no `ready.json` (`.ufo/waves/round-49/controls/base.c1.out`); a
replay that answers `/tokenize` itself from a process named `-m <model>`
without running llama-server fails on the exe digest `375532f8…458b`
(`.ufo/waves/round-49/controls/junk-c1-fake-witness.c1.out`). Own runs at HEAD
122c4ee9 (the tools are unchanged since 74558c71) with the host install (v4, no
provenance flags): a held server on pid 2296697/port 36853 was announced 0.30 s
after launch, passed exe+listen+model and nonce
`kama witness b200fe1dbe63a5f5`, all 11 checks passed, `witness`
`released true` `waited_ms 100`, pid gone and port refusing after exit
(`witness-probe.out`, `witness-receipt.json`); a hold that is never released
ends `released: false` after 1003 ms and the run still exits 0 with
`outcome: pass` (`timeout-receipt.json`).

**What the witness still cannot show.**

- *That the receipt came from the witnessed process.* The counter checks
  `match` and `witness.released`, not that the rerun receipt's capture fields
  were taken from the pid it observed. The hold raises a fake from "copy the
  captures" to "execute the frozen binary with the frozen model and answer a
  fresh tokenizer nonce"; it is not proof that the compared captures came from
  that execution.
- *Where the binary came from.* It does not show the binary was extracted from
  the recorded archive at replay time; the replay's record-time digest checks
  carry that, and a host copy of the same bytes passes (preregistration C1
  limit 1).
- *More than the launcher file.* `/proc/<pid>/exe` is the 17,864-byte
  `llama-server` launcher on this host; `libllama-server-impl.so`, the rest of
  the install tree, the soname links and system libraries are outside the hash,
  so the round-18/19/21 pin limits apply to the witnessed process too.
- *Which weights.* The `-m` file is hashed as it stands during the hold: that
  is not what the process mapped at load time, and the nonce shows only that
  the tokenizer agrees with this GGUF's token array — not inference, weights or
  quality.
- *Timing and opt-in.* One hold per receipt, one instant in the ready state;
  the loading window is not witnessed. `--witness-dir` is optional and a
  witnessed replay "matches exactly as an unwitnessed one: the witness is not
  compared" (`kama-live-replay.py:45`), so only the counter demands it; a
  replay run by hand without the flag yields no `witness` block.
- *The block is bookkeeping.* `tests/llamacpp-live/check-receipt.py` never
  reads `witness` (no occurrence at 122c4ee9); a copy of round-48 receipt-1
  carrying a fabricated `witness {port 1, pid 1, released true}` still
  validates `VALID` exit 0 with `--require-schema v5` (`gate-probe.out`,
  `receipt-1-fake-witness.json`). Only the counter's detail lines carry
  execution evidence.
- *A reused witness directory is not refused.* A pre-existing `release` ends
  the hold at once — own receipt `stale-release-receipt.json`:
  `released: true`, `waited_ms: 0`, `outcome: pass` — and an observer reading
  `ready.json` before the tool rewrites it can see a previous run's
  announcement. The counter avoids this by creating a fresh directory per
  receipt (`makedirs`, 294), which raises on reuse; a hand-run witness should
  do the same.

- *Linux and one uid.* Another uid's `/proc/<pid>/exe` is unreadable, the
  digest is `None` and the leg fails closed; the counter's port-refusal probe
  is 127.0.0.1 only, and teardown gracefulness stays the receipt's own teardown
  fields.

**The bounded archive-member check.** `verify_archive_member()`
(kama-llamacpp-live.py:212-279) now refuses, before hashing any member byte: an
archive that is not a regular file (`provenance-archive-not-regular`), exceeds
1 GiB (`-archive-too-large`, `ARCHIVE_MAX_BYTES` 208) or holds more than 4096
index entries (`-archive-too-many-members`, `MEMBER_MAX_COUNT` 209); and a
missing member, a member that is not a file, a sparse member
(`provenance-member-sparse`, 261) or a declared member size that differs from
the `--server` file's size (`-member-size-mismatch`, 259-263). The archive is
opened once and that descriptor is both hashed and parsed; the index is walked
streaming, and the last occurrence of a duplicated name wins, as extraction
does. The closed hole (round-48 seat Sen2Live F1): a 205-byte PAX archive
declaring a GNU sparse member of 10^15 bytes made the old loop hash 10^15
bytes. At the build the counter's cap leg reports the same archive exiting 2
with `provenance-member-sparse`, server never executed, in 0.1 s, while the
positive control — an archive holding the stub's own bytes — passes
verification and executes the stub (c1-build.out `cap` lines); at 438127bc that
leg timed out at 30 s (base.c1.out). Own direct probes at HEAD
(`archive-bound-probe.out`): sparse 10^15 → `-member-sparse` in 0.000 s; 4100
index entries → `-too-many-members` in 0.04 s; a 1 GiB+1 sparse file →
`-archive-too-large` without a read; a member shorter than the `--server` file
→ `-member-size-mismatch`; `/dev/null` → `-archive-not-regular`; a duplicated
name resolves to its last member; the matching archive returns both digests.
The bounds are policy constants — a legitimate larger archive is refused (fail
closed). This is a bound and a digest comparison, not atomicity: an in-place
rewrite of the archive between the hashing pass and the index parse is not
excluded, and nothing is shown about the archive's origin beyond the caller's
expected digest.

**Scope.** As round 48: one build (b11909), CPU, fixture `stories260K`,
single-model mode, unregistered loopback ports; not generation, quality,
performance, GPU, router mode, sleep, or registered-consumer health.
