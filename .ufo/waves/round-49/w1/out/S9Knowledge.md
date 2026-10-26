# S9Knowledge — round 49, kama lane: execution-witness paragraph

**Verdict: the paragraph is drafted and grounded** — the witness protocol was exercised at HEAD 122c4ee9 against a live b11909 server with an outside observer and all four observer legs passed, while two operational findings (a stale `release` silently skips the hold; the receipt gate does not read `witness`) and one frozen-counter limit (it does not tie the receipt's captures to the observed pid) bound what the round-49 C1 evidence shows. The lane measurement at the build is cited, not re-run.

## Delivered

- `.ufo/waves/round-49/w1/out/S9Knowledge/paragraph.md` — the exact text to append to `corpus/knowledge/llamacpp-loading-lifecycle.md` after the round-48 section (heading, source line, protocol, the four observer checks, observed runs, eight limits bullets, bounded archive-member section, scope). Not applied: the lane is read-only for this seat.
- Probes and receipts in the same directory (list at the end).

## What I read (the contract, not re-run)

| Source | What it fixes |
|---|---|
| `.ufo/waves/round-49/preregistration.json` | C1 predicate, counter sha256, the four limits I restate |
| `tools/round49-replay-witness-audit.py` docstring (1-101) | observer contract: exe, listen inode, `-m`, nonce, release, cap, newrow |
| `tools/kama-llamacpp-live.py:212-279, 285-305, 1860-1866` | `verify_archive_member`, `hold_for_witness`, the after-probes/before-teardown call site |
| `tools/kama-live-replay.py:42-45, 275-281` | `--witness-dir` plumbing; "the witness is not compared" |
| `corpus/SOURCES.md:247-248` | S494 (README at caa8191d, `/tokenize` `with_pieces` + `/detokenize`), S495 (`proc_pid_exe(5)`) |
| `.ufo/waves/round-49/c1/server-README-caa8191d.md:686-731` | documented request/response shapes, piece type (700) |
| `.ufo/waves/round-49/c1/proc_pid_exe.5.txt:75-76` | "attempting to open it will open the executable" |
| `.ufo/waves/round-49/measured/c1-build.out`, `controls/*.c1.out` | the lane's frozen-counter measurement and controls |

`sha256sum tools/round49-replay-witness-audit.py` = `86b4a40d…f0d6c1`, the preregistration's `counter_sha256`. `git diff --stat 74558c71 HEAD` lists only four `.ufo/waves/round-49/` files, so the tools and corpus I read at HEAD are the build's bytes.

## Evidence (commands, outputs, exit codes)

All runs at HEAD 122c4ee9, host b11909 install, loopback ports picked by the tool, each torn down by the tool; `pgrep -af kama-witness-s9k` → no match after every run (exit 1).

1. **Witnessed live run + outside observation** — `python3 .ufo/waves/round-49/w1/out/S9Knowledge/witness-probe.py $S $O` → exit 0 (`witness-probe.out`):

   ```
   ready.json: {'schema': 'kama-live-witness/v1', 'port': 36853, 'pid': 2296697, ...} after 0.30s
   observer nonce: 'kama witness b200fe1dbe63a5f5'
   observer problems: 'none'
   readlink /proc/2296697/exe -> /home/vgpnk/.local/opt/llama-b11909/llama-server
   live exit: 0 total 0.38s
   receipt schema: kama-llamacpp-live/v4 outcome: pass
   receipt witness: {'pid': 2296697, 'port': 36853, 'released': True, 'waited_ms': 100, ...}
   checks: all 11 true
   pid alive after exit: False port refuses: True
   ```

   The observer is the frozen counter's own `observe()` (counter:258-289), so this is the counter's check applied to a real lane-tool-held server, without the 75 MB replay downloads.

2. **Timeout path** (`timeout-probe.out`, `timeout-receipt.json`) — exit 0, 1.29 s, `outcome: pass`, `witness.released False`, `waited_ms 1003`, teardown returncode 0, port refuses, pid dead. A missing release does not fail the run and is not compared.

3. **Stale release** (`stale-release-probe.out`, `stale-release-receipt.json`) — exit 0, 0.26 s, `outcome: pass`, `witness.released True`, `waited_ms 0`, pid 2337314 / port 38835, `ready.json` written. The hold was skipped by a pre-seeded `release`.

4. **Archive-member bound** (`archive-bound-probe.out`) — direct calls to `verify_archive_member`, no server:

   ```
   good                 ok member bb6220bfa599 == server bb6220bfa599    0.000s
   sparse-1e15          SetupError provenance-member-sparse              0.000s
   size-mismatch        SetupError provenance-member-size-mismatch       0.000s
   archive-too-large    SetupError provenance-archive-too-large          0.000s
   too-many-members     SetupError provenance-archive-too-many-members   0.042s
   not-regular          SetupError provenance-archive-not-regular        0.000s
   duplicate-last-wins  ok member bb6220bfa599 == server bb6220bfa599    0.000s
   sizes: bomb 205 bytes (declares 10^15), big 1073741825 bytes allocated 0, many 4100 entries
   ```

5. **Receipt gate** (`gate-probe.out`) — `python3 tests/llamacpp-live/check-receipt.py --require-schema v4 …/witness-receipt.json` → `VALID`, exit 0; `--require-schema v5 …/receipt-1-fake-witness.json` (round-48 receipt-1 plus `witness {port 1, pid 1, released true}`) → `VALID`, exit 0.

6. **Lane measurement cited** (not re-run by me): `measured/c1-build.out` → `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` with pids 254977/255370/255954 and ports 33749/45335/36679; `controls/base.c1.out` → `met=False`, witness legs have no `ready.json`, cap sparse leg times out at 30 s; `controls/junk-c1-fake-witness.c1.out` → `met=False`, exe `375532f8…`.

## Findings

**F1 — a reused witness directory skips the hold (defect, minor; operational).** `tools/kama-llamacpp-live.py:298-302`: `release` is computed and tested inside the wait loop without checking whether it already exists, so a leftover `release` ends the hold immediately while the receipt still says `released: true` (measured: `waited_ms 0`, `stale-release-receipt.json`). A stale `ready.json` is likewise overwritten rather than refused, so an observer polling the directory can read a previous run's (dead) pid. Two live tools sharing one directory also clobber each other's `ready.json` — same root cause. The frozen counter is immune (fresh `makedirs` per receipt, counter:294), so C1's measurement is unaffected. Proposed fix (full diff at `proposed-hold-release-guard.diff`): before writing `ready.json`, `if os.path.exists(release) or os.path.exists(os.path.join(wdir, 'ready.json')): raise SetupError('witness-dir-not-fresh')` — the call site's `SetupError` handler already turns that into a `setup-error` receipt with the server torn down, fail-closed. Verified: the diff applies to an unmodified HEAD tree, and the patched copy refuses the pre-seeded directory (exit 2, `setup_error witness-dir-not-fresh`, teardown returncode 0) while a fresh directory still passes (`proposed-fix-probe.out`). A selftest case (fresh directory vs pre-seeded `release`) would keep it.

**F2 — the receipt's `witness` block is not evidence on its own (limit, by design).** `tests/llamacpp-live/check-receipt.py` contains no occurrence of `witness` (`grep -c witness` → 0), and a fabricated block validates: `receipt-1-fake-witness.json` → `VALID`, exit 0 with `--require-schema v5` (`gate-probe.out`). This is consistent with the claim, which rests on the counter's own observation, and the paragraph says so. If the lane wants receipt-level evidence, the minimal move is: when `witness` is present, require `schema == "kama-live-witness/v1"`, an integer `port`/`pid` and a boolean `released`; add `--require-witness` for runners that want the hold mandatory, default off so every recorded receipt still validates.

**F3 — the counter does not tie the receipt's captures to the observed pid (limit of the frozen counter).** `witness_one` (counter:292-340) accepts `match is true` plus `witness.released is true`; it never compares the rerun receipt's capture fields with what it observed. The hold therefore raises a fake from "copy the captures" to "execute the frozen binary with the frozen model and answer a fresh tokenizer nonce", but does not prove the compared captures came from that execution. No fix proposed: the counter is frozen; the paragraph states the limit.

Minor limit, recorded in the paragraph rather than as a finding: the counter requires each `piece` to be a `str`, while S494 says non-UTF-8 pieces arrive as byte lists — such a reply is graded a disagreement (fail closed, never a false pass), and the ASCII nonce avoids it on this fixture.

## Scope and known integration items (not re-reported)

- One build (b11909), CPU, fixture `stories260K`, single-model mode, unregistered loopback ports; not generation, quality, GPU, router mode, sleep or consumer health.
- The round-49 counters' SKILL.md registry rows, SCORECARD/LOG/lesson/QUALITY/README entries and `corpus/lessons/round-49.md` (S494/S495 `used-by`) are the integrator's items, unchanged by this seat.
- No counter run and no replay of the round-48 receipts by this seat; the build's own measurement is cited. No tool installs or upgrades were made (python3 3.14 stdlib only; no pacman).
- Nothing outside my out directory was written; the lane, fleet repo and sibling lanes were read-only. My scratch `/fast/scratch/hyaku/kama-r49/S9Knowledge` was removed after the receipts were copied here.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/paragraph.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/witness-probe.py` / `witness-probe.out` / `witness-receipt.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/timeout-probe.out` / `timeout-receipt.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/stale-release-probe.py` / `stale-release-probe.out` / `stale-release-receipt.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/archive-bound-probe.py` / `archive-bound-probe.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/gate-probe.out` / `receipt-1-fake-witness.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Knowledge/proposed-hold-release-guard.diff` / `proposed-fix-probe.out`
