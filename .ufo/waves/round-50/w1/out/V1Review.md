# V1Review — code review, frozen C1 counter `tools/round50-replay-bind-audit.py`

Verdict: **no false-PASS path found on the honest route; the counter is sound as a witness — 2 Low operational findings (decoy leak in `teardown_leg`, IPv4-only `port_refuses`), 3 Info findings, 10 checked-clean function groups, each exercised by a fixture under `.ufo/waves/round-50/w1/out/V1Review/` (logs `f1_proc_helpers.log`, `f2_mapped_model.log`, `f3_teardown_leak.log`, `f4_port_newrow.log`, drivers `f1..f4*.py`, all exit 0).**

Reviewed at lane commit 97c864bead3ee4a2f629574e77263d33834ec98a content; all line numbers below refer to `tools/round50-replay-bind-audit.py` (605 lines). Findings are reports, not patches — the counter is frozen.

Method note (recorded per role): no `lsp` device is mounted in this session's tool inventory, so caller/definition checks were done by direct execution of the module's functions against live `/proc` and synthetic `/proc`-shaped inputs, plus line-pinned greps; no semantic server evidence is claimed. No tools were installed (none needed). Fixtures ran only in `/fast/scratch/hyaku/kama-r50/V1Review/`; every process a fixture started was killed by the fixture (log-confirmed); my seat added no `llama-server` and left no scratch (removed at the end). `pgrep` at finish shows only other seats' processes (`M1Ctr` mutation runs), untouched.

## Findings

### V1-F1 — Low (operational): `teardown_leg` leaves the announced-but-unowned process alive
- Where: `tools/round50-replay-bind-audit.py:505-526` — snapshot `descendants(p.pid)` (505), the not-under-invoker note (507-508), SIGKILL of the invoker (509), `ok` requiring `ready["pid"] in snap` (520), and the `finally` reaper (525) which kills **only snapshotted descendants**.
- Contract: the docstring promises "The counter kills any survivor afterwards" (`:64`). An R1-style lying replay that announces a pid it does not own is exactly what this leg exists to detect — and when it detects it, the announced process (in the real attack, a stray `llama-server` holding its port) survives the counter.
- Fixture: `f3_teardown_leak.py` (fake replay writes `ready.json` announcing an unowned `sleep 300`, sets its own `PR_SET_PDEATHSIG` like the real replay):
  ```
  teardown_leg returned False in 0.4 s
    detail: teardown: announced pid 3552308 is not under the invoker
    detail: teardown: invoker SIGKILLed with 1 descendants; after 0.10 s alive [] port refuses FAIL
  decoy pid 3552308 alive AFTER counter finished: True  <- LEAK if True
  fake replay leftovers (snapshotted, reaped by counter): []
  ```
  Fail-closed holds (leg False → met False); the defect is the leftover survivor, contradicting `:64`.
- Proposed fix: on the `ready["pid"] not in snap` path, kill the announced pid only after verifying it is actually the frozen server (`sha_file(f"/proc/{pid}/exe") == SERVER_SHA`) before SIGKILL; otherwise a lying announce could make the counter murder an unrelated live process. Alternatively keep it alive but escalate the detail line to a distinct `leftover` marker so run harnesses can reap.

### V1-F2 — Low: `port_refuses` probes IPv4 only; a `::1`-only survivor counts as "port refuses"
- Where: `tools/round50-replay-bind-audit.py:251-260`, connect target `("127.0.0.1", port)` at `:255`; used by `bind_one` `:477` and `teardown_leg` `:512,519`.
- Fixture (`f4_port_newrow.log`): with a listener bound to `::1:44717`, `port_refuses() -> True` while `socket.create_connection(("::1", 44717))` succeeds.
- Reachability: needs a server that (a) escaped the snapshot (not in `snap`) and (b) bound `::1` only. The frozen live tool binds v4 loopback, so this is not reachable on the honest path — hence Low, not High. `listen_inodes` itself does accept `::1` (`:206`), so the asymmetry is only in the refuse-probe.
- Proposed fix: `port_refuses` should try both `("127.0.0.1", port)` and `("::1", port)` and report refusal only if both fail.

### V1-F3 — Info: `newrow_leg` silently treats a missing/failing BASE read as "every tip row is new"
- Where: `tools/round50-replay-bind-audit.py:529-539` — `git show BASE:corpus/SOURCES.md` with `check=False` (`:531`), `return set()` on failure (`:532-533`), subtraction at `:536`, hardcoded frozen `BASE` (`:107`).
- Fixture (`f4_port_newrow.log`): in a scratch repo without the base object, the leg still returned `True` and reported `3 rows new since base` (all tip rows) where the true delta was 1; asking for `base` itself reports `2 rows new since base` (should be 0). Two consequences: (1) on a shallow/partial clone the leg can pass on a row that already existed before base but names the maps URL — a false-PASS domain; (2) a real git failure is indistinguishable from "no new rows" and yields exit 1, not the documented could-not-evaluate exit 2.
- On the real lane clone (full shared history) this does not trigger — L1's dry run measured a sane delta — but the counter is frozen and will be rerun by others; the failure mode is silent.
- Proposed fix: when the BASE `git show` fails, treat the leg as could-not-evaluate (return 2 from `main`) or at least append a distinct detail line `base unreadable`.

### V1-F4 — Info: a modified base row counts as a "new" row
- Where: `:536-537` — line-set difference, so editing an existing base row to append the maps URL counts as new. Fixture (`f4_port_newrow.log`): rewriting row `S1` at tip to cite the URL → `MODIFIED base row (no new id) counts as new: True`, hit `['| S1 | r']`. Defensible under the frozen wording "a registry row, absent at --base" (the edited line is absent at base); recorded so the scribe/verdict seats know the leg accepts edits, not only additions.

### V1-F5 — Info: `gguf_tokens` accepts ver>3 and short-reads truncated token strings
- Where: `tools/round50-replay-bind-audit.py:153-157` — only `ver < 2` is rejected, so a hypothetical GGUF v4 is decoded under v2/v3 layout (forward-compat beyond the frozen "v2/v3" contract); `rstr` at `:162-165` returns `data[o+8:o+8+n]` without a bounds check, so a declared length exceeding the buffer yields a silently short decode.
- Fixture (`f1_proc_helpers.log`): `v4 -> ['a', '▁b']`; tail-truncated file → `['a', '\ufffd']` with no exception; truncated header → `struct.error`; v1/bad-magic/empty/unknown-type-13/string-typed-tokens/int-array-tokens all raise `EvalError` (fail-closed).
- Not exploitable in the counter's own flow: `vocab` is computed only after the download hashes to the frozen `MODEL_SHA` (`:570-575`) and `struct.error` is in the catch list (`:576`). No action needed; noted for the record.

## Checked clean (each with fixture evidence)

- `gguf_tokens` types/`fixed` table (`:160`), v2/v3 layout, `et != 8` guard (`:186`): 11 synthetic GGUF cases in `f1_proc_helpers.log`, all as designed; the `nkv`/`<QQ>` header unpack at `:158` reads n_tensors+n_kv correctly.
- `listen_inodes` (`:198-217`): state `0A` filter (ESTABLISHED inode excluded), loopback address set exactly `0100007F`/`::1` (both found; `0.0.0.0` correctly excluded as outside the claim's "127.0.0.1/::1"), wrong port empty; inode joins `/proc/<pid>/fd` `socket:[…]` readlink exactly.
- `stat_fields` (`:234-242`): `rsplit(")", 1)` survives comm `a)b c)d` (set via `PR_SET_NAME`); ppid/starttime indices correct (`rest[19]` = field 22).
- `pid_alive` (`:244-248`): zombie → False; wrong `start` → False; matching start → True (starttime guard defeats pid reuse where a start is known).
- `environ_keys` (`:271-276`): readable for same-uid children, `None` for nonexistent pid (→ "environ unreadable" probe, fail-closed); empty environ decodes to empty set (not None).
- `descendants`/`descends_from` (`:279-306`): root excluded, multi-child fan-out returns both grandchildren, `descends_from` directional and depth-3 correct; the 64-hop cap (`:299`) is far above the real tree depth (invoker→replay→live tool→server). A reused pid in the chain can only break descent (fail-closed), never fake it.
- `mapped_model` (`:309-341`): kernel `%02x:%02x` dev format equals `f"{os.major:02x}:{os.minor:02x}"` on this host (xfs, `103:05`); stat-vs-maps join rejects a different-inode file placed at the old path; hash gate rejects same-inode rewritten content; size gate `:335` proven by forcing `sha_file` to always pass — 768 B mapping skipped, 2048 B control found; deleted mapping (`… (deleted)` suffix) fails `stat` → fail-closed; unreadable maps → probe.
- `reap`/teardown cleanup (`:425-437`): the snapshotted fake replay was reaped with no leftovers (`f3_teardown_leak.log`), and the `start_new_session` process group (`:404`) plus explicit pid kills cover both live and dead-invoker paths.
- `start_replay`/`prepare_env` (`:376-405`): `INVOKER` (`:114-115`) plus `-I` verified end-to-end — with a planted `sitecustomize` on `PYTHONPATH` and `KAMA_R50_CANARY` in the env, a non-isolated `-c` child imports the module (marker line written, canary readable in its environ) while the counter's exact `-I -c INVOKER → -I` chain leaves the marker empty and rc 0.
- `observe` ordering (`:343-374`) — the assignment's "witness_one() ordering": there is no `witness_one` in this file; the witness is `observe()` inside `bind_one` (`:440-495`), and the ordering is correct: exe → listen → tree → env(server, parent) → mapped → fresh nonce, all before the release file is written (`:461-463`), then exit/join/marker checks after. The tokenize piece comparison (`:361-363`) short-circuits the range check before `vocab[...]`, and the whole block is inside the `(OSError, ValueError, KeyError, TypeError)` catch (`:369`), so a malformed server reply becomes a probe, not a crash.
- `wait_ready` (`:408-416`) type-checks `pid`/`port` as ints; a stringly-typed announce yields `None` → fail-closed.
- `newrow_leg` row filter (`:535`): `| S` prefix + digit; `ln[:8]` detail truncation works; identical lines at base and tip cancel in the set difference (see V1-F3/F4 for the two edge behaviors).
- `main` (`:542-605`): `git`/archive failures → exit 2 with `could-not-evaluate` (`:547-550`); tar extraction drops symlinks/hardlinks by design; vocabulary gated on the download digest; `met` requires all three legs.

## Residual risk and verification gaps

- I did not run the full counter end-to-end (it downloads ~75 MB, starts `llama-server`, ~46 s; other seats already hold live runs); the L1 dry-run receipts at 97c864b (`bind=1 teardown=1 newrow=1 bound=3/3 met=True`) remain the end-to-end evidence. My findings are unit-level by design of this seat.
- V1-F1/V1-F2 are unreachable while the live tool keeps its frozen contract (v4-loopback bind, no daemonization, no lying announce); they matter exactly when a replay under test cheats — the moments the counter exists for.
- The `▁`→space piece comparison (`:363`) was verified only against the dry-run outcome (3/3 passed) and code-read of the server contract, not against a live server in this seat.

## Artifacts

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/V1Review.md`
- Drivers: `f1_proc_helpers.py`, `f2_mapped_model.py`, `f3_teardown_leak.py`, `f4_port_newrow.py`
- Logs: `f1_proc_helpers.log`, `f2_mapped_model.log`, `f3_teardown_leak.log`, `f4_port_newrow.log`
- All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/V1Review/`; scratch `/fast/scratch/hyaku/kama-r50/V1Review` removed on completion.
