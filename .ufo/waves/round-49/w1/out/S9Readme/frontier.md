## Frontier disposition — round 49

Two claims were built at `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (base
`438127bc01ff3b99f98468549d58046f932490ef`, the round-48 closure; counters frozen at
`36d5ed2681111b68c180f8ab1646d8dc9beaedee`, digests `86b4a40d…f0d6c1` and
`26c465a9…066945`): operability 8 → 8 under an execution witness for live-receipt replay
plus a bounded archive-member verification (C1), and calibration 7 → 7 under
append-only-audit v4's line origin and binding (C2). The figures below are measured at
that build commit with the frozen counters (`.ufo/waves/round-49/measured/c1-build.out`,
`c2-build.out`): C1 `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0; C2
`fixture=1 lane=1 scenarios=8/8 met=True`, exit 0. Capability rows, scorecard sections,
the instrument-registry entries and `corpus/lessons/round-49.md` are integration work and
are not pre-empted here.

**What the witness now proves.** `tools/kama-live-replay.py --witness-dir D` passes
`--witness-dir`/`--witness-timeout` to the live child (`tools/kama-live-replay.py:275-281`;
the child's bound grows by the witness timeout). Once the rerun server is ready and its
checks have run, `hold_for_witness()` (`tools/kama-llamacpp-live.py:280-296`) writes
`D/ready.json` {schema `kama-live-witness/v1`, port, the llama-server child's pid,
`written_utc`} atomically and holds the server until `D/release` exists, the child exits
or `--witness-timeout` (default 120 s) passes; the rerun receipt gains `witness`
{schema, dir, port, pid, released, waited_ms} (`:1860-1867`).

For each of the three committed round-48 v5 receipts the counter
(`tools/round49-replay-witness-audit.py`) runs that replay from the tip's `git archive`
with HOME/XDG_CACHE_HOME/TMPDIR under scratch and a witness dir, and while the replay
waits it checks from outside, with a model it downloaded and hashed itself:
`sha256(/proc/<pid>/exe)` equals the frozen server member digest `35ac50fb…d7ff0`
(`:258-262`); a LISTEN socket on `127.0.0.1`/`::1:<port>` has an inode among
`/proc/<pid>/fd` (`:193-228`, `:263-265`); the `-m` argument hashes to the frozen model
`270cba1b…bd256d` (`:266-275`); and a fresh `kama witness <16 hex>` nonce posted to
`POST /tokenize` (`with_pieces`) and `POST /detokenize` comes back with every piece equal
to the counter's own decode of `tokenizer.ggml.tokens[id]` (U+2581 read as a space) and
the detokenized text equal to the nonce, one leading space allowed (`:276-289`). It then
writes `release`; the replay must exit 0 with `match` true and the rerun receipt must
record `witness.released` true; afterwards the pid is gone and the port refuses
(`:292-339`). At the build, 3/3. A replay that starts no server at all — the round-48
K2Cheat/K2Urlswap class — can no longer reach `met=True`.

Both surfaces are sourced rows: S494, the llama.cpp server README at `caa8191d`
(§POST `/tokenize` … §POST `/detokenize`, `corpus/SOURCES.md:247`; lines 686–735 of the
committed copy `.ufo/waves/round-49/c1/server-README-caa8191d.md`), and S495,
`proc_pid_exe(5)` (`corpus/SOURCES.md:248`). Neither row exists at the base, and the
counter's `newrow` leg sees S494.

**What the archive bound now refuses.** `verify_archive_member()`
(`tools/kama-llamacpp-live.py:212-272`) refuses, before hashing a member byte: an archive
that is not a regular file (`provenance-archive-not-regular`), larger than 1 GiB
(`provenance-archive-too-large`, `:208`), or holding more than 4096 index entries walked
streaming (`provenance-archive-too-many-members`, `:209`); and a member that is absent,
not a regular file, sparse (`provenance-member-sparse`) or whose declared size differs
from the `--server` file's size (`provenance-member-size-mismatch`) (`:258-267`; called
with `os.path.getsize(server_real)` at `:1664-1666`). The counter's `cap` leg
(`:343-390`) builds a one-byte-member archive whose PAX header declares a 10^15-byte GNU
sparse member: the tool exits 2 in 0.1 s with `provenance-member-sparse` and a marker
proving the stub never ran, while the positive control, whose member is the stub's own
bytes, executes it. The live tool's own selftest exercises the same refusal.

**What v4 now audits.** `origin(l)` (`tools/append-only-audit.py:423-441`) is the set of
`## ` titles (`None` before the first heading) holding the line text at its first
appearance in the file's blob over `git rev-list --topo-order --reverse`; a deleted line
in an eligible exempt section stays ungraded only when its parent section is eligible
*and* its origin includes one of the file's exempt titles (`:465-478`). Binding
(`:216-233`) needs the row token as a whole word (`[a-z0-9_]` excluded on both sides),
treats a negation within three words before `append-only`/`append only` as unbinding
(`not|never|no|nor|neither|non|isn't|aren't|no longer`; v3's four fixed strings still
apply), and never lets a wildcard row bind through a line of a covered file merely saying
append-only. The JSON keeps `"schema": "append-only-audit/v3"` and adds
`"definition": "v4"`.

On the lane at the build the tool exits 0: the ten contract rows expand to 92 files over
319 commits, 5 events all restored, `regressed=0 vanished=0 bad_declarations=0`, and
`ungraded_lines` 82 (round 48: 89). The `0718b6ab` SCORECARD event grades 2356 of 2421
deleted lines and holds 2356 — ungraded 72 → 65 — and stays restored; the `dd9f5dc6`
event is 14/31 with 17 ungraded. The seven newly graded lines are the six round-34
capability rows and the round-41 `pin-watch` row of the head `## Capabilities` table
(`SCORECARD.md` parent lines 121–127 at `21945c61`): born under dated round headings,
carried into the head and deleted there in that rewrite, so v3's title carve-out hid
them; they are held at the tip. All eight fixtures hold: `launder` graded
25/unrestored/exit 1 (v3: ungraded/exit 0), `native-head` 25 ungraded/exit 0,
`dated-loss` unrestored, `substring`/`negated`/`wildcard-self` unbound exit 1,
`word-token`/`wildcard-named` bound exit 0.

The round-48 v3 counter is frozen at its old expectation and now disagrees by
construction: at the build its lane leg reads the v4 tool's 2356 graded / 65 ungraded
against its 2349 / 72 and exits 1 (`.ufo/waves/round-49/measured/r48c1-build.out`). It is
superseded, not regressed.

**What they still do not prove.**

- *That the observed server is the replay's server, or the source of its captures.* The
  counter observes `ready.json`'s pid and never joins it to the rerun receipt's
  `child_pid` (no `child_pid` in the counter; the acceptance at `:306-329` checks only
  `witness.released`), and `--compare` deliberately treats `child_pid`/`port` as instance
  facts (`tools/kama-live-replay.py:198`, `:291`). A harness can run the capture session,
  stop it and start a fresh b11909 server for the witness window, or skip the capture
  session and copy the original captures; every leg passes (round-49 seat K1Design F1).
  Round-49 seat K1Cheat built both a decoy replay that never executes the live tool and a
  `PYTHONPATH`/`sitecustomize` hijack of the pristine tree, each reaching
  `witness=1 cap=1 newrow=1 met=True` at this build; the counter builds the child
  environment from `os.environ` and overrides only HOME/XDG_CACHE_HOME/TMPDIR
  (`:431-434`).
- *That the binary came from the downloaded archive at replay time.* The witness hashes
  the running image, not where it was extracted from; a replay that runs the host copy
  `~/.local/opt/llama-b11909/llama-server` passes (preregistration limits[0]; K1Cheat).
- *That the bytes the server loaded are the hashed bytes.* The `-m` path's on-disk
  contents are hashed after start (`:266-275`); nothing binds the mapping the process
  actually holds.
- *Anything signed, or with build provenance.* The check is local kernel observation
  only: no signed Evidence, no exec-time measurement log (IMA), no SLSA/in-toto
  provenance; it is Linux `/proc` only and fails closed for a process it cannot read
  (round-49 seat U1Prior, reading RFC 9334 §10.2).
- *Content-aware eligibility.* v4 narrows the carve-out by origin, but 25 lines born in
  `## Axes` and rewritten in place are still 25 ungraded lines, exit 0 (`native-head`);
  a same-length replacement of exempt-born text stays invisible.
- *Binding beyond a lexical tripwire.* The window looks only before `append-only` and
  accepts only dashes as separators, so `append-only? No.` and `not, as of round 40,
  append-only` bind, while a rule-declaring `no edits append-only` is unbound (round-49
  seat K2Negation F1/F2; the `cannot`/`can't`/curly-apostrophe/em-dash escapes it also
  found are routed and narrowed by an integration edit). The whole-word class excludes
  only `[a-z0-9_]`, so `co-log`, `log's`, `a/b/log` and non-ASCII neighbours bind
  (K2Negation F3). The lane's 384 flagged lines are all judged correctly, so no contract
  row is mis-bound today.
- *Origin as provenance.* Origin is first appearance, not history: text born in the head,
  carried in a dated section and deleted from the head again stays ungraded, and identical
  text born in both places counts as exempt-born (preregistration limits[2]). Held text is
  still a multiset over the whole file, not by position.
- *The sub-20 boundary.* The threshold is still 20 deleted lines per (commit, file)
  (`tools/append-only-audit.py:452`), a policy constant the contract does not derive; the
  round-48 count of 66 graded sub-threshold events and the real `LOG.md` loss at
  `ed135b3c` predate this window, and round 49 did not decide it. Coverage is still only
  as good as the rows, and a `## ` inside a fenced block is a section boundary.
- *Anything beyond the sample.* Three sampled instants, one 1,185,376-byte tiny model,
  `--ctx 256`, `-t 1`, one ubuntu-x64 asset, unregistered loopback ports, and a replay
  that needs github.com and huggingface.co.

**Still frontier:**

- A pid-continuity join in the witness (ready.json's pid equals the rerun receipt's
  `child_pid`, or the exe lies under the replay's work dir) and a child environment that
  is not inherited, so "witnessed" also means the replay's own lifecycle ran.
- An archive-origin binding at witness time, or an explicit statement that the record-time
  digest checks carry binary origin rather than the witness.
- A binding of the model the server actually loaded, not the file named at `-m`.
- Exec-time measurement and build provenance for the witness, or honest naming of it as a
  local, unsigned observer-nonce check.
- Content-aware eligibility for the five exempt head sections, and a region for the
  SCORECARD preamble (the grammar is still `## `-only, so the line-6 banner stays graded —
  selftest case `preamble-graded`), the `A-row` mutable cells, and position-aware
  restoration; v4 changes none of them.
- The negation window's punctuation and trailing forms and the whole-word class'
  apostrophe/hyphen/slash/non-ASCII edges, and a binding test a denial cannot pass.
- A derived rather than constant sub-20 threshold, and a disposition of the 66 graded
  sub-threshold events.
- The prerelease cliff: b11909 is a GitHub prerelease, the only retained copy is
  host-local, and a deleted or re-uploaded asset makes the replay fail closed rather than
  wrong.
- Carried over unchanged and not re-measured here: the b11906 ledger population at
  b11909+ (at least S107, S130, S132, S113, S135), S013's re-pin, S022 and the unpinned
  vLLM stable pages S002–S004, the `hexrun-census` unknowns, K05 (declared versus served
  context), and the registered consumers (last admitted sample 2026-10-15, all `DEAD`).
