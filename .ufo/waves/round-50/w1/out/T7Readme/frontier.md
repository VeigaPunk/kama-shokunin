## Frontier disposition — round 50

Two claims were built at `97c864bead3ee4a2f629574e77263d33834ec98a` (base
`26ecba64ad6fb571d09074b07202d1618a46ecd1`, the round-49 closure; counters frozen at
`601c8889f33d1797c712feb753974c20cf891264`, digests `ff6ac2ac…9c5e89` and
`925f07a4…48ca46`): operability 8 → 8 under a process-bound execution witness for
live-receipt replay (C1), and calibration 7 → 7 under append-only-audit v5's birth-DAG
origin, fence-aware sections and CRLF-normalized keys (C2). The figures below are
measured at that build commit with the frozen counters
(`.ufo/waves/round-50/measured/c1-build.out`, `c2-build.out`): C1
`bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0; C2
`fixture=1 lane=1 scenarios=12/12 met=True`, exit 0, lane `ungraded_lines 89`,
`bad_declarations 0`, `regressed 0`. Both base controls are met=False
(`.ufo/waves/round-50/controls/base.c1.out`: `bind=0 teardown=0 newrow=0 bound=0/3`;
`base.c2.out`: `fixture=0 lane=1 scenarios=9/12`). Capability rows, scorecard sections,
the instrument-registry entries and `corpus/lessons/round-50.md` are integration work and
are not pre-empted here.

**What the process-bound witness now proves.** The counter
(`tools/round50-replay-bind-audit.py`) starts each replay from a `python3 -I -c` invoker
(`:402-404`) with an environment it builds itself — PATH, LANG, the proxy variables, and
HOME/XDG_CACHE_HOME/TMPDIR under scratch (`:376-393`) — plus two canaries: a fresh
`KAMA_R50_CANARY` and a `PYTHONPATH` whose `sitecustomize.py` records every interpreter
that imports it. While `ready.json` names the server it checks from outside: the replay
runs the tip's `git archive` tree, the server pid descends from the replay's
pid through the ppid chain (`:450-453`, `:297-308`), `sha256(/proc/<pid>/exe)` is the
frozen binary (`:345`), a LISTEN inode on the port belongs to that pid (`:348-350`),
neither the server nor its parent carries the canary (`:351-358`), a mapping of that pid
hashes to the frozen model (`:359`, `:309-340`), and a fresh nonce round-trips through
`POST /tokenize` (`with_pieces`) and `POST /detokenize` against the counter's own
`tokenizer.ggml.tokens` decode (`:360-373`). After it writes `release`: the replay exits 0
with `match` true, the rerun receipt records `witness.released` true, its `child_pid`
equals the observed pid (`:470`), and its `model_mapping` sha256/dev/inode equal the
mapping the counter observed (`:473-476`); the pid is gone, the port refuses, and the
planted sitecustomize marker is empty (`:479-485`).

The isolation is the replay's own, not only the witness's. It starts the live child with
`python -I` and only `LIVE_ENV_KEYS` (PATH, HOME, LANG, LC_ALL) plus a TMPDIR under the
work dir (`tools/kama-live-replay.py:88`, `:112-115`, `:309-311`, `:319-333`); the child's
`preexec_fn` sets `PR_SET_PDEATHSIG` to SIGTERM and exits at once if the parent already
changed (`:314-318`); the replay sets the same signal on itself (`:100-108`, called at
`:587`). So killing whatever started the replay takes replay, live tool and server down.
`model_mapping()` in the live tool (`tools/kama-llamacpp-live.py:678-727`) reads
`/proc/<pid>/maps`, keeps only a mapping whose `pathname` stats to the same dev and inode
as the maps line, re-opens it `O_NOFOLLOW`, `fstat()`-checks it again and hashes that same
file; the receipt gains `model_mapping` with `mapped` true or a reason
(`:1999-2005`), and the replay refuses a rerun whose mapping is absent, unmapped or hashes
to another model (`tools/kama-live-replay.py:343-348`). At the build the counter kills the
invoker during the hold and requires every snapshotted descendant gone within 30 s with
the port refusing (`:497-521`; `KILL_WAIT` `:112`), and C1 adds source rows S496
(`proc_pid_maps(5)`, `corpus/SOURCES.md:249`), S497 (`PR_SET_PDEATHSIG(2const)`,
`:250`) and C2 S498 (CommonMark 0.31.2 §4.5, `:251`).

**What v5 now audits.** `tools/append-only-audit.py` keeps the JSON shape (`schema
append-only-audit/v3`) and declares `definition: v5` (`:573`): `key(l)` drops one trailing
carriage return (`:275-280`); `sections()` skips fences, opened by
`fence_open()`/closed by `fence_close()` per CommonMark 0.31.2 §4.5 (`:282-325`); and
`origins()` is the union, over every birth of a key among the commits reachable from
`<to>`, of the `## ` title holding it in that commit's blob — a birth being a commit whose
blob holds the key while no parent's blob does (`:480-509`). The carve-out keeps a deleted
line ungraded only when its parent section is an eligible exempt title *and* its origin
intersects the file's exempt titles (`:531-546`), so v4's dependence on rev-list order
(`F3`), on fake headings inside fences (`F4`) and on byte-exact keys (`F5`) is gone. Every
event's deleted count is pinned to `git diff --numstat` (`:520-524`), and ungraded is
defined as deleted minus graded, so `graded + ungraded == deleted` cannot drift; the C2
counter recomputes both independently for every lane event.

Twelve fixtures hold (`c2-build.out`): `order-a`/`order-b` build the same trees with the
merge parents swapped and both read `deleted 25 graded 0 ungraded 25`, exit 0; `fence`
(`## Axes` inside a fenced block, then 25 dated lines deleted) reads 25 graded,
unrestored, exit 1 — v4 read it ungraded, exit 0; `crlf-launder` (25 dated LF lines moved
under `## Axes` as CRLF, then deleted there) reads 25 graded, unrestored, exit 1 — v4
read it ungraded. The round-49 eight are kept unchanged: `launder` 25 graded unrestored
exit 1, `native-head` 25 ungraded exit 0, `dated-loss` unrestored, and
`substring`/`negated`/`wildcard-self` unbound versus `word-token`/`wildcard-named` bound.
A move never re-births a key — `launder` moves the dated lines under `## Axes` without the
key ever leaving the parent blob (`tools/round50-append-audit-v5-check.py:230-237`) —
which is why the laundering direction stays graded.

On the lane the tool exits 0: five events, `bad_declarations 0`, `regressed 0`,
`vanished 0`, `ungraded_lines 89` (v4: 82). The `0718b6abbda6` SCORECARD event keeps 2349
graded of 2421 deleted and 72 ungraded (v4: 65); `dd9f5dc6c0e6` is 14/31 with 17 ungraded
against the counter's own v5 count of 23; the LOG, QUALITY and README events grade
everything. The seven extra ungraded lines are the `## Capabilities` mirror rows of
`SCORECARD.md:121-127` at `21945c61` (six round-34 rows and the round-41 `pin-watch`
row): under v5 each has a birth at `82b5e9d3` — the round-45 restore of the truncated
SCORECARD, whose blob holds all seven under `## Capabilities` while the truncated parent
held none — so their origin intersects the exempt head title and they are ungraded; v4
took only the first blob in rev-list order (`29f9d1e1` for the six, `24aa1d34` for
`pin-watch`) and graded them. That is round-49 seat K2Origin's F6 (mirror rows falsely
graded) closed by origin, not by the "text still present in a dated section" rule that
seat proposed; the counter's own v5 count and the tool's now agree exactly (72 = 72).

**What they still do not prove.**

- *That the server's mapped pages are the bytes the check hashed.* `model_mapping()` and
  the counter both hash the file through its pathname now and compare that path's
  `stat()` dev/inode with the maps line; neither reads `/proc/<pid>/pagemap`, smaps or the
  resident pages, so a rewrite after the mapping is invisible whenever the file hashes
  the same at check time (identical content, or the original bytes restored)
  (preregistration limits[0]). On a filesystem whose maps `dev` differs from
  `stat.st_dev` (btrfs subvolumes) both checks fail closed: the tool's own compare
  (`tools/kama-llamacpp-live.py:710-713`) and the counter's (`:333`); the counter's
  scratch is xfs (`dev 103:05` in `c1-build.out`).
- *That the binary came from the downloaded archive at replay time.* The witness hashes
  the running image (`:345`) and never requires the exe path to lie under the replay's
  work dir or match the archive member, so a replay executing the host copy
  `~/.local/opt/llama-b11909/llama-server` still passes (limits[0]; the round-49 K1Cheat
  class).
- *Environment cleanliness beyond two channels.* The canaries are one environment
  variable and one `PYTHONPATH` sitecustomize (limits[1]); `LD_PRELOAD` into the server or
  a modified `python` on PATH are not planted, and the replay→live edge is protected by
  `-I`, not by a measured environment.
- *Teardown beyond one instant.* The invoker is killed once, during the witness hold
  (limits[2]), against a descendant snapshot taken at that moment; a child spawned after
  the snapshot is not tracked, and a kill during download or before readiness is not
  exercised.
- *The pid join's edges.* Both joined records are written by the live tool for the same
  process: the join is `ready.json`'s pid against the rerun receipt's `child_pid`, read
  after release (`:470`), with descent checked at hold time only and no start time bound
  to `child_pid`. It proves the observed pid is the server the receipt describes, not that
  the receipt's captured check outputs were re-derived at the witnessed instant — the
  counter observes the server live, it does not replay the captures.
- *Anything signed, or with build provenance.* Still local `/proc` observation and a
  counter-chosen nonce: no IMA exec measurement, no signed evidence, no SLSA/in-toto
  provenance; a process it cannot read fails closed.
- *Content-aware eligibility, and what a restore does to origin.* v5 still exempts a
  deletion purely by section and origin: the five head sections the contract exempts
  (`registry/append-only-contract.tsv:3`: `## Axes`, `## Planned`, `## Retired`,
  `## Saturation`, `## Capabilities`) leave 25 head-born lines ungraded in `native-head`,
  exit 0, and a same-length replacement of exempt-born text stays invisible. Birth is
  first appearance in the graph, not history: a truncation-and-restore re-births every
  line of the file, so text that sits in an exempt section at the restore keeps an exempt
  origin afterwards — the lane's own seven rows are exactly this case, and no fixture
  covers "delete a dated line, restore it into the head, delete it from the head".
- *The lexical binder.* The binding rule is v5's v4 copy unchanged (preregistration
  limits[3]): the negation window looks only before `append-only`, accepts only dashes as
  separators, and the whole-word class excludes only `[a-z0-9_]`, so `co-log`, `log's`,
  `a/b/log` and non-ASCII neighbours bind. The counter re-implements the binder rather
  than calling the tool. The lane's flagged lines are all judged correctly, so no contract
  row is mis-bound today.
- *The sub-20 boundary.* The threshold is still 20 deleted lines per (commit, file)
  (`tools/append-only-audit.py:448`), a policy constant the contract does not derive; the
  66 graded sub-threshold events and the real `LOG.md` loss at `ed135b3c` predate this
  window and round 50 did not decide them. Restoration is still a multiset over the whole
  file, not by position.
- *Anything beyond the sample.* Three sampled instants, one 1,185,376-byte tiny model,
  `--ctx 256`, `-t 1`, one ubuntu-x64 asset, an ephemeral unregistered loopback port, and
  a replay that needs github.com and huggingface.co.

**Still frontier:**

- An archive-origin binding at witness time (the exe under the replay's work dir, or the
  archive member hash compared at exec), or an explicit statement that the record-time
  digest carries binary origin and the witness does not.
- The mapping the server actually holds — pagemap/smaps or a resident-page digest — and a
  dev comparison that survives a filesystem whose maps dev differs from `stat.st_dev`.
- Exec-time measurement and build provenance for the witness, or honest naming of it as a
  local, unsigned observer-nonce check.
- Injection channels beyond the two canaries, and a `child_pid` record bound to a pid start
  time so the join cannot alias.
- Content-aware eligibility for the five exempt head sections; a fixture for
  delete-restore-into-head laundering (today ungraded by the birth rule); position-aware
  restoration; the negation window's punctuation and trailing forms; the whole-word
  class' apostrophe/hyphen/slash/non-ASCII edges; and a binding test a denial cannot pass.
- A derived rather than constant sub-20 threshold, and a disposition of the 66 graded
  sub-threshold events.
- The prerelease cliff: b11909 is a GitHub prerelease the replay refetches from
  github.com each run; a deleted or re-uploaded asset makes the replay fail closed rather
  than wrong.
- Carried over unchanged and not re-measured here: the b11906 ledger population at
  b11909+ (at least S107, S130, S132, S113, S135), S013's re-pin, S022 and the unpinned
  vLLM stable pages S002–S004, the `hexrun-census` unknowns, K05 (declared versus served
  context), and the registered consumers (last admitted sample 2026-10-15, all `DEAD`).

Integration (round 50, L1): drafted by wave-1 scribe T7Readme
(`.ufo/waves/round-50/w1/out/T7Readme/frontier.md`) at the build; the measured values are
in SCORECARD §Round-50 measured results. S496/S497 name `corpus/lessons/round-50.md` as a
consumer, and S498 names it alone; that lesson lands at integration.
