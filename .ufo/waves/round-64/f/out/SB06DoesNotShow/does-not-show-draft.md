# Draft — SCORECARD §Round 64, `What met=True does not show`

Seat: SB06DoesNotShow (scribe, leaf). Draft only; the L1 integrates. Every bullet is one sentence and names a
survivor, an unmodelled vector, or an acknowledged limit with a `path:line`. Paths are relative to the lane root
`/home/vgpnk/Projects/shokunin/kama-shokunin`.

Grounding runs by this seat at the measured tip `23b3fdb1a925129a9961cf551f6d40bf251602cb` (scratch clone
`/fast/scratch/hyaku/kama-r64/f/SB06DoesNotShow/D`, removed at yield):

    C1: tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True
    C2: tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True

Two counter mutants of the amended C1 instrument were also run by this seat, both from the scratch clone and both
scored against the unmodified committed tool; both **SURVIVED** (each still prints `met=True`, 91/91), so they are
listed below as measured unmodelled vectors, not as wave-b reports:

    mutant m_live_status  (drop `f.add('live_status')` from probe_fails): tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 eval_selftest=8/8 errors=0 met=True
    mutant m_finish_gate  (drop `and (p.get('finish_reason') != 'length' or uc == n)` from probe_fails): tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 eval_selftest=8/8 errors=0 met=True

Both match the wave-b mutants `m06`/`m03` of `.ufo/waves/round-64/b/MT13ProbeTokens.md:131` and `:134`, so the
amendment did not close them: the checks still exist at the tip (`tools/round64-c1-counter.py:721`, `:743`) but no
control names `live_status`, `live_fp_shape`, or the finish-reason gate, so removing them changes nothing the
counter scores.

---

## C1 — operability (`live-completion-request-plane`)

- **A non-dumpable own-uid helper that predates the tool and holds a duplicate of the run-port listener is recorded
  but never graded**, because `collect` stores such pids only as the count `unreadable_old` and `grade_binding`
  reads `unreadable_own` alone (`tools/round64-c1-counter.py:455`, `:452`, `:485`; wave-b
  `.ufo/waves/round-64/b/MT01DumpableHide.md:39-40` `O3`/`O4` SURVIVED with `unreadable_old=4`, and
  `.ufo/waves/round-64/b/MT08HoldWindow.md:20` `f2` SURVIVED, `met=True` 76/76).
- **Writes into the running server's own memory through `/proc/<pid>/mem` pass**, because the counter compares
  mapped file digests but never the bytes the process actually holds (`.ufo/waves/round-64/b/MT05EnvInject.md:25`
  `F2` SURVIVED, `met=True`; `:136` "Mapped bytes are never compared with the disk file. F2 passes for that reason").
- **An in-process rewrite of a live environment value is invisible to the environment check**, because
  `/proc/<pid>/environ` holds live memory rather than the execve-time block and the tip's `bind_env` compares only
  the keys it reads (`.ufo/waves/round-64/b/MT05EnvInject.md:28` `F5` `met=True`; `:123-125`; admitted as
  "initial environment only; later in-process changes are invisible" at `corpus/lessons/round-64.md:13`, source
  `S531` at `corpus/SOURCES.md:283`).
- **The tool's own holder bookkeeping is not graded as provenance, only for agreement with the counter's own
  snapshot**, so a v2 tool with the schema string relabelled and a hand-written holder block (K1c), a v3 tool whose
  `listener_holders_pinned` check argument is `True` (K2), and a v3 tool whose enumeration is a child-only literal
  (K3) are all accepted with `met=True` (`.ufo/waves/round-64/b/CR03DoNothing.md:27-29` and `:128-130`; the
  amendment's own honest disclosure in `.ufo/waves/round-64/controls/freeze.txt:174`, AMENDMENT 1, "the new instrument
  rejects forgeries the round-63 instrument accepted; it does not make the tool-side bookkeeping a graded
  artifact").
- **A holder that exists only after the counter's release is never observed**, because the counter takes both
  holder snapshots strictly before the release and grades teardown only as "the recorded holders are gone and the
  port closes" (`.ufo/waves/round-64/b/CR03DoNothing.md:31` `K5` `met=True`; `:92-99`).
- **`argv` is what the process says, never identity alone**, so a process that rewrites its own argv area passes
  `bind_argv` and is caught only by `bind_exe`/`bind_maps`
  (`corpus/lessons/round-64.md:19`; `corpus/SOURCES.md:284` source `S532`, admitted "layout only"; wave-b
  `.ufo/waves/round-64/b/MT04ArgvSpoof.md:44-45`).
- **The `bind_maps` check still exempts everything under `/usr/lib/`, `/lib/`, `/usr/lib64/` and `/lib64/` from
  hashing**, so a dlopen'd plugin placed in a root-writable system directory is not compared byte-for-byte
  (`.ufo/waves/round-64/b/RV02CounterCode.md:57` D7; `tools/round64-c1-counter.py:150` `SYSTEM_PREFIXES`, used at
  `:524`), and the wave-f reviewer records D7 as "Not fixed as a hashing defect; substantially mitigated"
  (`.ufo/waves/round-64/f/RV08C1CounterAmended.md:41`).
- **The 91 controls are 30 families with repeats, not 91 independent attack vectors**: `EXPECT_FAMILIES` lists 30
  families summing to 91 (`tools/round64-c1-counter.py:66-76`), of which the single `bind` family is 30 and
  `tamper` is 8; 79 of the 91 are in-memory mutations of the counter's own captured snapshot and witness, and only
  the remaining 12 are live forged tools (7 `scenario` fakes plus `replay`, 3 `forge` and 1 `relabel`, at
  `tools/round64-c1-counter.py:1989-2054`).
- **Five of the probe-level checks are unmodelled and can be deleted without changing the verdict** — `live_status`,
  `live_ctype`, `live_model`, `live_created` and `live_fp_shape` exist at `tools/round64-c1-counter.py:721`, `:723`,
  `:727`, `:732`, `:735` but no control names any of them (none of the five appears among the 79 `add()` calls in
  `build_controls`), which is why wave-b mutants `m03`/`m06`/`m07` survived
  (`.ufo/waves/round-64/b/MT13ProbeTokens.md:131`, `:134`, `:135`) and why this seat's own mutants
  `m_live_status` and `m_finish_gate` still print `met=True` 91/91 at the tip; the finish-reason gate
  (`tools/round64-c1-counter.py:743`) is likewise a sub-clause of the graded `live_run_field` check that no
  control isolates, so dropping it alone leaves the family's own witness failing on a different sub-clause.
- **The per-run draw is not itself graded**, so a counter that fixed `n_predict` at a constant would still meet
  (`.ufo/waves/round-64/b/MT13ProbeTokens.md:38` and `:136` mutant `m08` SURVIVED; the draw is at
  `tools/round64-c1-counter.py:875-889`).
- **The reference-agreement leg is proved against a model whose genuine traffic never exercised the `stop` branch
  of the finish gate**, so for this model that branch is absence of evidence rather than evidence
  (`.ufo/waves/round-64/b/MT13ProbeTokens.md:32-34`).
- **Neither instrument was attacked by a non-author seat at its final bytes**: the honest-stop note records that
  wave b ran against the freeze-commit instrument `f6a4ea9a`, and AMENDMENT 1/1a/1b changed the C1 instrument
  after those seats scored (`.ufo/waves/round-64/controls/freeze.txt`, AMENDMENT 1 preamble and AMENDMENT 1b;
  `SCORECARD.md:3378`).

## C2 — calibration (the claim registry)

- **A pin fixes bytes, not behaviour on another host**: the counter compares the sha256 of the twelve bound tools
  and the reconciler as blobs at the tip (`tools/round64-c2-counter.py:79-115`, `check_pins` at `:338-354`), which
  says nothing about how those same bytes behave on a host with a different `HOME`, a different pinned install, or
  no model (`.ufo/waves/round-64/b/X01C2Counter.md:118` "Live rows depend on host state"; and the reviewer records
  the registry's own `llamacpp` command as carrying the absolute path
  `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`, `.ufo/waves/round-64/f/RV04C2CounterCode.md:38`).
- **The tally statuses rest on lane-authored text read by regular expressions**, so `tally_disclosed=8/8` proves
  only that the lane wrote a sentence the reader's patterns match, not that any shortcut or survivor occurred
  (`.ufo/waves/round-64/b/X07Tally.md:92` "The reader is regex-based over wording; each hit is cited so a human can
  verify it, but it does not prove a statement is *true* - only that the lane wrote it"; the reader's patterns are
  `STATEMENT_PATTERNS` at `tools/shortcut-tally.py:236`).
- **The tally reader crosses section boundaries and attributes statements by file, not by round**, so a status can
  be earned by a sentence in an unrelated section (`.ufo/waves/round-64/f/RV05TallyDiff.md:9` P2 and `:33` P3;
  the reader's section terminator at `tools/shortcut-tally.py:625-634`).
- **The regression table holds exactly one regression per row**, so a second, independent behaviour change in the
  same tool is not tested and only the one planted line stands between the counter and a hollow tool
  (`registry/capability-regress-r64.tsv:2-13`, twelve rows for twelve capabilities; the lane already records this
  as the round-65 item at `SCORECARD.md:3374` "add a second independent regression per row, since the round-64 table
  holds one regression per row"; the executors' own report notes the regressions they could not make flip, so the
  table under-uses the available mutations, `.ufo/waves/round-64/b/X02Regress1.md:19-22`).
- **A regression only has to flip the row's verdict, not to be the semantically relevant line** — the counter
  proves the row turns false, and the authors concede that `if new is None and False:` "is a real behaviour change
  but the counter only proves it flips the row's verdict, not that it is the semantically most relevant line"
  (`.ufo/waves/round-64/b/X01C2Counter.md:113`).
- **The tally tool is not in the frozen 13-file pin table**, so a hollow tally that prints `disclosed:*` for rounds
  56-63 while keeping the `no-disclosure` fixture right is not caught (`.ufo/waves/round-64/b/X01C2Counter.md:112`;
  the pin table is `tools/round64-c2-counter.py:79-115`, `N_PINS = 13` at `:115`, and `tools/shortcut-tally.py` is
  absent from it).
- **`work_reuse_refused=1` is a property of the counter, not of the tip**, so it shows the counter's own guard
  works and says nothing about the tip's contents (`.ufo/waves/round-64/b/X01C2Counter.md:50`).
- **The idle outcome was proved only through a fake-`pgrep` fixture, never on a truly idle host**, because the
  context-capacity row's host test is a host-global `pgrep -x llama-server` and this host never goes idle
  (`.ufo/waves/round-64/b/X01C2Counter.md:120` "Not exercised: a truly idle host"; `.ufo/waves/round-64/b/X10EnvIdleProbe.md:29`;
  the wave-f stability runs show the row scored `host-busy` in all six, `.ufo/waves/round-64/f/X12StabilityC2Final.md:5`).
- **The `all_ports_closed: true` pattern is printed in both declared outcomes**, so the registry row's own pattern
  cannot by itself distinguish "ran and closed" from "never ran"
  (`.ufo/waves/round-64/b/X10EnvIdleProbe.md:26`, and `.ufo/waves/round-64/b/X03Regress2.md:17` "the pattern
  `"all_ports_closed": true` therefore does NOT distinguish refusal from idle-pass").
- **The busy-outcome rule admits a superset-invented `other_pids_seen`**, because the amended rule asks only that
  the pids in both snapshots are inside the printed set (`.ufo/waves/round-64/b/X01C2Counter.md:115`; the reviewer
  records that a focused call accepted an invented nonempty set, `.ufo/waves/round-64/f/RV04C2CounterCode.md:46`).
- **Printer rejection credits only the `regress-inapplicable` reason**, so a printer carrying the original source
  in a never-executed live branch is covered only in the commented-out decoy form
  (`.ufo/waves/round-64/b/X01C2Counter.md:114`).
- **The closure-pointer conjunct and the reconciler's pointer clause are coupled to one builder's exact wording**,
  so a reworded reconciler needs the planted-verdict table updated (`.ufo/waves/round-64/b/X01C2Counter.md:116`),
  and the pointer is stale by construction once the next closure file lands
  (`.ufo/waves/round-64/b/X06Reconciler.md:40` "the next closure (round 64) will make the pointer stale again
  unless the closing integrator updates the row - the conjunct will then fail, by design"; the same coupling is
  repeated for the tally selftest at `.ufo/waves/round-64/b/X01C2Counter.md:117`).
- **Regression-table errors are printed but do not enter the gate**, so extra invalid rows can sit in the table
  without turning `errors` non-zero (`.ufo/waves/round-64/f/RV04C2CounterCode.md:20-24` D2: `rerrs` reaches
  stderr only, at `tools/round64-c2-counter.py:1689-1690`).
- **The tally subprocess's exit code is not checked**, so a tally that prints complete records and then exits
  non-zero still supplies `tally_disclosed=8/8` (`.ufo/waves/round-64/f/RV04C2CounterCode.md:30` D3).
- **The registry's twelve rows are the round-62/63 rows carried forward unchanged**, so `covered=12/12` shows the
  same twelve capabilities are still bound, not that the lane's serving surface grew
  (`SCORECARD.md:3354` "The rows are unchanged because round 64 enters no capability"; the request plane itself is
  absent from the registry — `live-completion-request-plane` appears in no `registry/capability-claims-r6*.tsv` row,
  and `SCORECARD.md:3306` records that it "is not in this twelve-row frozen population").

---

## Draft text for the SCORECARD paragraph

The following is prose-ready, one clause per limit, in the style of the round-52/53 sections
(`SCORECARD.md:3016`, `:3047`):

> ### What `met=True` does not show (round-64 wave attacks)
>
> - **C1**: the amended counter binds the process that answers to the pinned llama-server, but it does not show that
>   *every* holder is the hold pid — a non-dumpable own-uid helper that predates the tool and holds a duplicate of
>   the listener is counted in `unreadable_old` and never graded (MT01 O3/O4, MT08 f2); nor that the mapped bytes
>   are the file's bytes — a write into the running server's memory through `/proc/<pid>/mem` passes (MT05 F2),
>   and an in-process environment-value rewrite is invisible (MT05 F5, S531); nor that the tool's holder
>   bookkeeping is provenance — a schema-relabelled v2 tool with a hand-written holder block, a v3 tool whose
>   `listener_holders_pinned` check is `True`, and a v3 tool with a child-only enumeration all meet (CR03
>   K1c/K2/K3); nor that the hold window covers the teardown — a holder spawned only after the counter's release
>   is never observed (CR03 K5); `argv` is what the process says, never identity alone (S532); `/usr/lib` and
>   friends are still exempt from hashing in `bind_maps` (RV02 D7); the 91 controls are 30 families with repeats,
>   not 91 independent vectors; and five probe-level checks (`live_status`, `live_ctype`, `live_model`,
>   `live_created`, `live_fp_shape`) plus the finish-reason gate are named by no control, so deleting them still
>   meets (MT13 m03/m06/m07; this seat's `m_live_status` and `m_finish_gate` mutants both print `met=True` 91/91).
>   Neither instrument was attacked by a non-author seat at its final bytes.
> - **C2**: the registry proves each of the twelve capabilities still runs, not that the lane's serving surface
>   grew — the twelve rows are the round-63 rows carried forward unchanged and the request plane is in no registry
>   row; a pin fixes bytes, not behaviour on another host (X01 §Residual risks; the registry's own command carries
>   an absolute `HOME`-dependent model path, RV04 D4); the regression table holds one regression per row and only
>   has to flip that row's verdict, not to be the semantically relevant line (X01:113, X02:19-22, SCORECARD
>   round-65 item 2); the tally tool is not in the 13-file pin table, so a hollow tally that keeps the
>   `no-disclosure` fixture right is not caught (X01:112); the tally statuses rest on lane-authored text read by
>   regular expressions that also cross section boundaries (X07:92, RV05 P2/P3); `work_reuse_refused=1` is a
>   property of the counter, not of the tip (X01:50); the idle outcome was proved only through a fake-`pgrep`
>   fixture, never on a truly idle host, and the `all_ports_closed: true` pattern is printed in both declared
>   outcomes (X01:120, X10:26); the busy-outcome rule admits a superset-invented `other_pids_seen` (X01:115, RV04);
>   printer rejection credits only `regress-inapplicable` (X01:114); the closure pointer and the reconciler's
>   pointer clause are coupled to one builder's wording and go stale by construction once the next closure files
>   (X01:116-117, X06:40); and regression-table errors and the tally's exit code do not enter the gate (RV04 D2, D3).

---

## Provenance

- Read only: `/home/vgpnk/Projects/shokunin/kama-shokunin` (lane), including `.ufo/waves/round-64/b/*.md`,
  `.ufo/waves/round-64/f/*.md`, `.ufo/waves/round-64/controls/freeze.txt`, `SCORECARD.md`, `corpus/lessons/round-64.md`,
  `corpus/SOURCES.md`, and the tip blobs of `tools/` and `registry/`.
- Scratch: `/fast/scratch/hyaku/kama-r64/f/SB06DoesNotShow/` (clone at `23b3fdb1`, two committed counter mutants,
  one genuine C1 run, one C2 run, two mutant runs). Removed at yield; receipts copied into this out dir first.
- No lane file, index, jj state or commit was touched; no install or upgrade was performed; no pacman transaction.
- No live server of mine was left running; no registered port was touched; no foreign process was signalled.
