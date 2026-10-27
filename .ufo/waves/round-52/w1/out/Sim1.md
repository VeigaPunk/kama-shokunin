# Sim1 — round 52 simplification pass (proposals only)

**Verdict: one of the three named candidates is a real deletion and is proved (the counter's two fixture builders collapse to one authority; C2's output is byte-identical at +13/-17), two named candidates are rejected with evidence (the seal constants cannot be deduplicated under the live child's `python -I`; no round-51 member-path *code* survives in the replay — only false docstring claims, which are corrected), plus two dead-value deletions in the same counter. Net +28/-35 over two files, no measured leg changes.**

Axes: operability (no contract surface touched, nothing that runs changes) and calibration (the C2 counter's own verdict reproduced exactly).

## Method

* Read the full tools diff (`git -C <lane> diff 9ff76b1f763512be2f554cbbfd0b2213b63b0847 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 -- tools/`, 205 + 118 diff lines) and the whole new counter `tools/round52-append-restore-check.py` (544 lines).
* Every edit was made in one `git clone --shared` at `/fast/scratch/hyaku/kama-r52/Sim1/lane` and committed there as fixture identity `fx <fx@invalid>` (three commits on top of lane HEAD 34d82600). Toplevel asserted equal to the clone before the first commit. Nothing was written to the lane; the lane stayed at HEAD 34d82600 through the whole seat.
* Baselines and proposals were measured with the **frozen counters, unmodified in the lane**, pointed at the clone:
  `python3 <lane>/tools/round52-append-restore-check.py --repo <clone> --tip <commit> --scratch <S>/… --out …`
* Tips: base/build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`; proposal tree `6befef2c16ba7f145e0e1b5b988ba45fd5fdbfeb`.

Line references below are to the build commit 5dacf2c7 unless a proposal line is named (those are the proposal tree's lines).

## D1 — the counter's two fixture builders → one (APPLIED, +13/-17)

At the build the C2 counter builds its scratch repos twice: `repo()` (`tools/round52-append-restore-check.py:356-369`: `makedirs`, `git init`, the toplevel assertion, the write/`add -A`/`IDENT` commit loop, `rev-parse HEAD`) and, inside `ledger_case()` (`:393-411`), the same `makedirs`/`init`/toplevel assertion plus a local `commit(files)` that repeats the same loop verbatim. The only reason for the second copy is that `ledger_case` needs each commit's sha, which `repo()` computed but discarded.

Proposal (`Sim1/c2-fixture-merge.diff`): one `fixture(name)` (`:356`) that returns `(d, commit)`; `repo()` (`:374`) loops it; `ledger_case` (`:402-405`) takes `d, commit = fixture(name)`. One authority for "make a fixture repo and commit a snapshot", one toplevel assertion, one commit identity.

Evidence — C2 at both tips, exit 0 both:

```
base  tip=5dacf2c7…  fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
final tip=6befef2c…  fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
$ diff <(tail -n +2 base.out) <(tail -n +2 final.out)   # detail lines, tip= excluded
(no output; diff exit 0)                                
```

`Sim1/proof-c2-output-identical.txt`, `Sim1/proof-c2-base.out`, `Sim1/proof-c2-final.out`. The base line is exactly the build battery's `.ufo/waves/round-52/measured/c2-build.out:3`.

Unreachable difference (stated, not hidden): `repo()` with an empty `steps` list would now raise `UnboundLocalError` where the old code raised the `git rev-parse HEAD` `EvalError`. Every call site is `repo(name, [base] + steps)` (`:381`), i.e. at least one commit; the counter cannot reach the empty case.

## D2 — dead return value and dead tuple field in the same counter (APPLIED, +7/-7)

Two values are computed and never read:

* `graded_of()` returns `out, len(perm)` (`:246`) but its only caller discards the second element (`:277`, `G, _perm = graded_of(...)`; `grep -n "_perm"` finds the binding and nothing else). `perm` itself is still needed *inside* to skip A-row rows re-added in place; only the return is dead.
* `deleted()` appends `(pos, bytes, hunk adds)` (`:206`, docstring `:193`), and the third element is only ever unpacked into throwaway names (`:226`, `:231` `_na`; `:289` `_n`). The add count never leaves the hunk walk; the numstat cross-check uses `len(dl)` (`:272-273`), which is unaffected.

Proposal (`Sim1/c2-dead-field-return.diff`): `return out`; append `(start + gd, ls[i][1:])`; unpack 2-tuples. `pyflakes` clean; C2 output identical at the final tip (same receipt as D1, `met=True`, exit 0).

## D3 — stale round-51 docstring claims in the replay (APPLIED, +8/-11)

The replay's round-51 paragraph (`tools/kama-live-replay.py:54-65`) still described, in the present tense, behaviour the build deleted: `own_server` holding the **extracted member's** dev and inode (`:57`), the member being opened `O_NOFOLLOW` before the live child (`:59`), a multi-link member being `server-exe:member-links:<n>` (`:63`), and "a byte-identical copy put at the member path before exec still matches". After 5dacf2c7 `own_server` is the memfd identity, and the two refusals no longer exist:

```
$ git grep -n "member-links\|own_id" 5dacf2c7 -- tools/     → kama-live-replay.py:63 (docstring only)
$ grep -n "O_NOFOLLOW" tools/kama-live-replay.py             → :59 (docstring only)
```

The paragraph is read as the contract of the check, so this is a documentation defect, not just history: the round-52 paragraph right below (`:62-77`) says the binding is superseded while the paragraph above still asserts it.

Proposal (`Sim1/replay-docstring.diff`): keep the round-51 attribution (closure R6, seat J4Decoy) and the seat record, move its claims to the past tense, and state explicitly that `server-exe:member-links` and `server-exe:not-own-member` are gone and `own_server` now names the memfd. Prose only — no statement that runs changes.

```
$ python3 tools/kama-live-replay.py --selftest --scratch <S>/st-doc   # before the edit
KLR_SELFTEST pass=31 fail=0                                           exit 0
$ python3 tools/kama-live-replay.py --selftest --scratch <S>/st-doc2  # after
KLR_SELFTEST pass=31 fail=0                                           exit 0
```

(`Sim1/proof-klr-selftest-base.out`, `Sim1/proof-klr-selftest-final.out`; matches `.ufo/waves/round-52/measured/klr-selftest-build.out`.)

## R1 — duplicated seal constants: REJECTED

Sites: replay `:218-219` (`F_ADD_SEALS, F_GET_SEALS = 1033, 1034`; `SEALS_ALL = 15`), live `:774-775` (`F_GET_SEALS`, `SEALS_ALL`), C1 counter `:91-92` (`SEALS = 15`, `F_GET_SEALS = 1034`).

Deduplicating means a shared module, and that cannot work here:

* The replay always starts the live tool isolated: `tools/kama-live-replay.py:384` `argv = [sys.executable, "-I", live, --server …]`.
* The C1 counter starts the *replay* the same way: `tools/round52-replay-memfd-audit.py:421` `argv = [sys.executable, "-I", "-c", INVOKER, sys.executable, "-I", os.path.join(tree, REPLAY), …]`.
* Under `-I` the script's own directory is not on `sys.path`, so a sibling `tools/kama_memfd.py` is unimportable. Probe, tools-like layout (`Sim1/proof-isolation-probe.out`):

```
$ python3 probe.py          → sibling import ok 15     exit 0
$ python3 -I probe.py       → ModuleNotFoundError: No module named 'kama_memfd'   exit 1
```

* The counters are single-file instruments by convention: C2 copies `tools/append-only-audit.py` **alone** into its scratch dir and runs the copy (`tools/round52-append-restore-check.py:519-521`), and C1 extracts the tip's whole tree but still runs both tools under `-I`.

Making the import work would need an explicit `sys.path` insert inside a tool that is deliberately isolated — a third convention plus a coupling between a child process and a sibling file, to remove six constant lines that are cited ABI values (`fcntl(2)`). Not a behaviour-preserving deletion; no diff proposed.

## R2 — "round-51 member-path code now dead in the replay": NOT FOUND; the pre-execution guard is load-bearing

The build already removed that code — there is nothing left to delete: `own_id`, `os.fstat(own_fd).st_nlink`, and the `O_NOFOLLOW` open of the member are absent from `tools/` at 5dacf2c7 (`git grep` above; `member-links` survives only in the docstring, handled by D3).

The block that *looks* redundant is the extraction-time member check (`tools/kama-live-replay.py:363-369`): it re-hashes the extracted member, which `sealed_member()` re-checks from the tar stream. It is not dead. Removing it changes the refusal string (`member-digest-mismatch` → `memfd-digest-mismatch`) and fails the existing narrow check:

```
$ python3 <variant without the block> --selftest --scratch <S>/st-exp
FAIL member-digest-differs: exit=2 refused=memfd-digest-mismatch:want=3333…:got=306c… mism=[]
KLR_SELFTEST pass=30 fail=1                                    exit 1
```

(`Sim1/proof-noprecheck-variant-selftest.out`; the variant is a throwaway copy, the lane tool was not edited.) The block also guards the `--server` path that the live tool hashes before exec (`sealed_fd(args.server_fd, server_sha, os.path.getsize(server_real))`).

## R3 — C1 is a near-copy of the round-51 counter: NOTED, NOT PROPOSED

`tools/round52-replay-memfd-audit.py` (647 lines) is `tools/round51-replay-exe-audit.py` (638 lines) with the sealed legs added; the helper block (`git`, `sha_file`, `gguf_tokens`, `listen_inodes`, `pid_socket_inodes`, `stat_fields`, `pid_alive`, `port_refuses`, `post`, `environ_keys`, `descendants`, `descends_from`, `mapped_model`, `prepare_env`, `start_replay`, `wait_ready`, `replay_pid`, `reap`) is common. This is the lane's deliberate shape — one frozen counter per round, frozen names before data — and the round-51 counter is the instrument a round-51 measurement was taken with. Deduplicating would edit a frozen instrument after its measurement and make two rounds share one code path. No deletion.

## Preserved contract (what the proposals must not move)

* C1 and the live tool are untouched; the replay's executable path is untouched (docstring bytes only).
* C2's declared output at the proposal tip: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0 — identical to the build battery.
* Replay selftest 31/31, live selftest `selftest: ok` (file unchanged, rerun for completeness: `Sim1/proof-live-selftest-base.out`).
* The three diffs were replayed onto the build's own bytes and reproduce the proposal files byte for byte:
  `git apply` of `c2-fixture-merge.diff` + `c2-dead-field-return.diff` + `replay-docstring.diff` onto `git show 5dacf2c7:tools/*` → sha256 prefixes match the proposal tree (`5f97ccd9…`, `b674a03e…`).

## Limits and tradeoffs

* Proposals only: nothing is applied to the lane. The lane worktree carried five uncommitted modifications from other seats when I checked (`git -C <lane> status --porcelain` → `corpus/QUALITY.md`, `corpus/SOURCES.md`, `tests/llamacpp-live/check-receipt.py`, `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`); none are mine — every write of this seat is under `/fast/scratch/hyaku/kama-r52/Sim1` and `.ufo/waves/round-52/w1/out/Sim1/`. Lane HEAD stayed 34d82600 and no lane git/jj state was touched.
* I did not run C1 (it downloads ~75 MB per replay and starts llama-server processes). D1-D3 cannot change its verdict: two of them are inside C2, and the third is prose in a file C1 executes but whose behaviour is unchanged.
* D3 edits prose in place, which this repo treats as preservation-grade material. The tradeoff is deliberate: the round-51 attribution, seats and closure are kept, only present-tense claims that are now false are removed, because the same paragraph is the contract text a reader (and the next seat) uses.
* D1 carries the unreachable empty-`steps` difference above; nothing else in the counter's behaviour changes (its own recompute, fence/section logic, ledger comparison and eight constructed scenarios are untouched).
* No tools were installed or upgraded (pacman is paused host-wide; nothing was needed).

## Files

* `Sim1/c2-fixture-merge.diff` — D1, unified diff (applies to 5dacf2c7's counter)
* `Sim1/c2-dead-field-return.diff` — D2, unified diff (applies on top of D1)
* `Sim1/replay-docstring.diff` — D3, unified diff (applies to 5dacf2c7's replay)
* `Sim1/proof-c2-base.out`, `Sim1/proof-c2-final.out`, `Sim1/proof-c2-output-identical.txt`
* `Sim1/proof-klr-selftest-base.out`, `Sim1/proof-klr-selftest-final.out`, `Sim1/proof-live-selftest-base.out`
* `Sim1/proof-noprecheck-variant-selftest.out`, `Sim1/proof-isolation-probe.out`
