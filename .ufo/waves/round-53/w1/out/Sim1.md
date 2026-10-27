# Sim1 — round 53 simplification pass (proposals only), lane kama

**Verdict: 5 net lines deleted across 3 files (24+/29−), the only pyflakes finding closed, both counters' receipts byte-identical below the `tip=` line and 43/43 replay + 1/1 live selftests green — and the round-53 delta turns out to carry almost no dead weight: the 590-line cross-round copy inside C1 is load-bearing for the freeze and is *not* deleted.**

Lane is READ-ONLY for this seat. Everything below was done in `git clone --shared` copies under `/fast/scratch/hyaku/kama-r53/Sim1` (scratch removed at the end; receipts copied to this directory). No lane file outside this seat's out directory was written, staged or committed; no jj operation was run.

## Axes

| Axis | What this pass touches | Move |
|---|---|---|
| operability (C1) | C1's stale constant name; three copies of the record-time digest reader in the live tool | none on the measured value; the counter and tool that produce the receipts get one reader instead of three |
| calibration (C2) | the C2 counter's only lint finding (a dead fixture binding) and an unused parameter | none on the measured value (fixture 8/8, lane 1) |

Nothing here changes a claim, a predicate, a leg, a receipt field or a reason string. Every candidate was measured against the property "same output on the same input"; candidates that failed that property are listed as rejected with their line math.

## Applied deletions (3 files, net −5 lines)

Diff: `sim1-deletions.diff` (also per file: `kama-llamacpp-live.diff`, `round53-cited-path-check.diff`, `round53-replay-code-audit.diff`). Line numbers are at the build commit `c22602bd8d83ab26349d1087e916ca537ee4f9d1` (the tree the receipts measure).

### 1. `tools/kama-llamacpp-live.py` — one descriptor reader instead of three (`+20/−24`)

`model_mapping` (`:715`), `server_exe` (`:750`) and `code_mappings` (`:817`) each carried the identical 7-line `hashlib.sha256()` read loop plus its `left != 0` short-read guard. Replaced by one `_hash_fd(fd, size)` → `(hexdigest, bytes-fell-short)` next to `sha256_file` (`:377`); each site keeps its own failure reason (`model-shrank-while-hashed`, `exe-shrank-while-hashed`, `file-shrank-while-hashed`) and its own dict shape, so no recorded value changes.

Behaviour-equivalence proof (`sim1-equivalence-probe.py`, transcript `sim1-equivalence.log`): both module versions loaded by path, driven on the same pid, outputs compared field for field:

```
same code_mappings
same model_mapping
same server_exe
same code_mappings:absent-pid
same model_mapping:absent-pid
same code_mappings:after-rename-over
same model_mapping:after-rename-over
EQ pass
```

`code_mappings` entries include their `sha256`, so "same" covers the digests. The rename-over case is the interesting one: both record `{'reason': 'mapped-file-deleted', 'opened': False}` and neither hashes the newcomer.

### 2. `tools/round53-cited-path-check.py` — dead fixture binding and an unused parameter (`+2/−3`)

`uvx pyflakes` at the build commit: `tools/round53-cited-path-check.py:433:5: local variable 'base' is assigned to but never used`. `base = Repo(D, c0)` (`:433`) is built and dropped (the fixture calls `evaluate(lane, None, None, …)`); with it gone `c0 = commit("c0")` (`:419`) has no reader, so the commit is made without binding it (the commit itself is still needed — the `deleted` scenario uses `cdel^`). `survey(lane, fleet, base_unres=None)` (`:323`) never reads `base_unres` and both call sites pass two positional arguments.

After the patch: `uvx pyflakes` over all four round-53 files exits 0 with no output.

### 3. `tools/round53-replay-code-audit.py` — stale constant name (`+2/−2`)

`MEMFD_URL` (`:99`) is round-52's name for the memfd page, repurposed in round 53 to hold `man7.org/…/proc_pid_mem.5.html` and read by `newrow_leg` (`:703`). Renamed `PROC_MEM_URL`; no other change. A stale name that says memfd while the value is the memory-page row is exactly the kind of thing that makes a later reader check the wrong row.

## Verification (all run, none inferred)

```
$ python3 tools/kama-live-replay.py --selftest --scratch $S/st      # patched tree 65c11b2f
KLR_SELFTEST pass=43 fail=0                                          # baseline c22602b: pass=43 fail=0
$ python3 tools/kama-llamacpp-live.py --selftest                    # patched: selftest: ok, exit 0
$ python3 tools/round53-cited-path-check.py --repo <clone> --tip c22602b…
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
$ python3 tools/round53-cited-path-check.py --repo <patched clone> --tip 65c11b2f…
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
$ python3 tools/round53-replay-code-audit.py --repo <clone> --tip c22602b…
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
$ python3 tools/round53-replay-code-audit.py --repo <patched clone> --tip 65c11b2f…
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
```

* Baseline C1 at `c22602b` reproduces the lane's `.ufo/waves/round-53/measured/c1-build.out` exactly, after normalising pids/ports/inodes: the only differing lines are the `$ python3 …` header and the `exit=0` trailer the lane's measure script adds (`sim1-lane-c1-build.out` vs `sim1-c1-baseline-build.out`). So the clone is faithful and the comparison below is meaningful.
* Baseline vs patched C1: `diff` of the two receipts after normalising pids/ports/inodes/nonces shows **only the `tip=` line** differing — all 13 `detail:` lines, the 8 archive libraries, 13 host files and every leg verdict are equal (`sim1-c1-baseline-build.out`, `sim1-c1-patched.out`).
* Baseline vs patched C2: `diff` below the `tip=`/`fleet=` line is empty, including all eight fixture verdicts (`sim1-c2-baseline-build.out`, `sim1-c2-patched.out`). The fleet rev moved between the two runs (`d2a6c59a…` → `33540c6e…`, the fleet repo's own HEAD, not mine); the counts did not move.

Patched runs exercise the patched live tool end to end: each of the three replays extracts the *tip's* tools, so `code=1`, `coderuns=3/3` and "8 archive files … byte-equal in `/proc/<pid>/mem`" are produced by the deduplicated reader.

## Rejected candidates (measured, not judged)

| Candidate | Weight if deleted | Why it stays |
|---|---|---|
| C1 imports round-52's legs instead of carrying them | **590 of C1's 794 lines are identical to `tools/round52-replay-memfd-audit.py`** (`difflib.SequenceMatcher`, autojunk=False; 74.3%); new in round 53: `Archive` 16, `code_observe` 67, `bind_one` 72→101, `main` 66→82, i.e. ~128 lines of new logic | The lane *already* imports sibling tools by path (`tools/round42-selfdesc-reconcile.py:131` loads `round41-scorecard-reconcile.py` from `here`; `tools/kama-context-capacity.py:188` loads the live tool), so this is not a new convention — but both precedents resolve the module from the **running** tree, while C1 deliberately takes the replay from the **measured** tree (`git archive --format=tar <tip>` → `<scratch>/tree`, `main`), and the preregistration freezes exactly *one* digest per claim (`claims[*].counter_sha256` = `1a7a1442…d8f`, equal to `sha256sum tools/round53-replay-code-audit.py` now). An import would move 74% of the counter outside the bytes that digest pins, so a later edit to the round-52 file would silently redefine what round 53 measured at a fixed tip. Deletion of the copy is only safe together with a second frozen digest for the legs — a round-54 decision (see "where I stopped"). |
| One `/proc/<pid>/maps` parser in the live tool | The premise names three functions; `server_exe` (`:731`) reads `/proc/<pid>/exe`, not maps (`:739`). There are **two** maps parsers (`model_mapping` `:690`, `code_mappings` `:785`) | A shared `_maps(pid)` (8 lines with its docstring) replaces 2×5 lines and forces the two `maps-unreadable:` detail strings to differ from what they are today (`{exc}` vs `{exc.strerror}`) — net +2 lines *and* a behaviour change. Rejected on both counts. |
| One maps parser inside C1 (`mapped_model` `:307`, `code_observe` `:393`) | same shape, 2 sites | Same math: net +2, and the two failure strings (`maps unreadable: {exc}` vs `code: maps unreadable: {exc.strerror}`) are receipt text. |
| One open+fstat+verify helper for `model_mapping` and `code_mappings` | ~8 lines at each site | The two policies genuinely differ (the model is user-owned, so dev must match; a root-owned library may report a different `st_dev` — the round-53 reason `path-is-not-the-mapped-file`/`path_dev` records it), and the four failure reason strings are part of the frozen docstring's receipts. Unifying them needs a policy flag — the needless abstraction this seat exists to prevent. |
| `_devstr(st)` for the `'%02x:%02x'` maps dev format | 4 sites in the live tool (`:711`, `:769`, `:811`, `:889`), 2 in C1 (`:443`, `:484`) | A two-line def against four one-line uses: net +1 line, no duplicated *knowledge* removed (the format is the maps format, documented once in each docstring). |
| `.ufo/waves/round-53/c1/*.txt` source copies (4 files, 2,718 lines, `ptrace.2.txt` 1,845 of them) | large | Provenance for S506–S509, cited by C1's `newrow` leg and the lesson. Marked historical/evidence; out of scope by the seat's own rule. |

The one-line summary of the rejected table: at this delta, every remaining duplication is either *deliberate independence* (counter vs tool, counter vs counter), *different policy behind the same shape*, or *frozen receipt text* — the next deletion would remove a property, not weight.

## Frozen-instrument constraint (why none of this lands in round 53)

`sha256sum tools/round53-replay-code-audit.py` = `1a7a1442…d8f` and `…-cited-path-check.py` = `1afb8b9d…080` equal `claims[0].counter_sha256` / `claims[1].counter_sha256` in `.ufo/waves/round-53/preregistration.json`, so **any** edit to either counter — including the 2-line rename — breaks the preregistration's freeze check at the build. Both counter diffs here are therefore round-54 material (or L1 re-freeze material for a *future* wave, before its freeze, never after it).

The live tool is not digest-pinned by the preregistration, but it is the tool each replay runs from the tip, so it can only be changed in a commit *after* the measured one; the equivalence probe is what makes that safe: no receipt field, digest or reason string changes.

Note on the tree I diffed: the lane working tree currently carries uncommitted edits to `tools/kama-live-replay.py` (+41/−16 region) and `tools/kama-llamacpp-live.py` (+16/−5) by the wave's own seats (a `/memfd:` branch inside `code_mappings`, and `verify_code(…, own)`), plus `SKILL.md`, `corpus/QUALITY.md`, `registry/hexrun-ledger.tsv` and `.ufo/waves/round-53/measured/*`. My diff is against the committed build (`c22602b`), where both counters and the replay are clean; the in-flight `code_mappings` hunk sits *above* the hash loop I replaced (separate hunk, same function), so a rebase is mechanical.

## Where I stopped

The next deletion on this axis is the 590-line copy in C1, and it repairs nothing until the legs are pinned the way the counter is. The concrete, named move for round 54, in the lane's existing shape: land `tools/kama-replay-legs.py` (the round-50 bind, round-52 sealed and round-53 code legs, plus `prepare_env`/`start_replay`/`reap`), have C1 extract it from the measured `git archive` tree and `importlib`-load it from `<scratch>/tree/tools/`, and freeze **two** digests in the preregistration (`counter_sha256`, `legs_sha256`). That keeps the freeze as tight as it is today while deleting 74% of every future C1, and it also removes the `here`-vs-`--tip` hazard already latent in `round42-selfdesc-reconcile.py:130`. I did not propose it as a round-53 patch: it changes what a frozen counter's digest covers, which is a design decision above this seat.

No further deletion was attempted: the next one would remove independence (counter vs tool), a distinct policy, or a frozen receipt string.

## Tooling

No tool installed or upgraded. `uvx pyflakes` (pyflakes 4.0.3, uv ephemeral env from the uv cache, official channel) ran once to locate the dead binding; `/usr/bin/python3` 3.14.8, `git`, coreutils only otherwise. No pacman transaction (host guard), no service started or stopped, no tracer wrapped around a counter.

## Files written

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/`:

- `Sim1.md` — this report
- `Sim1/sim1-deletions.diff` — combined patch (three files, against `c22602b`)
- `Sim1/kama-llamacpp-live.diff`, `Sim1/round53-cited-path-check.diff`, `Sim1/round53-replay-code-audit.diff` — per-file
- `Sim1/sim1-equivalence-probe.py` — the field-for-field probe (rerun: `python3 sim1-equivalence-probe.py <scratch with lane/ and patch/ clones>`)
- `Sim1/sim1-equivalence.log`, `Sim1/sim1-live-selftest-patched.log`, `Sim1/sim1-replay-selftest-{baseline,patched}.log`
- `Sim1/sim1-c1-{baseline-build,patched}.out`, `Sim1/sim1-c2-{baseline-build,patched}.out` — this seat's counter receipts
- `Sim1/sim1-lane-{c1,c2}-build.out` — copies of the lane's measured build receipts cited above
