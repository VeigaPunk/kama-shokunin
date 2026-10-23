# Advice — ReviewEchoExit2 (round 29 wave 1, routed repair 6 review)

**Verdict: the L1's repair is CORRECT and already committed at lane `513eba3b`
(`.ufo/waves/round-29/repairs/echo-exit2/receipt.txt`). Nothing in it is false. Optional
strengthening only — the routed defect is closed.**

## Findings

1. **Refusal is before any server start (code).** `tools/echo-recheck.py:441-444` refuses
   with `os.path.lexists(out)` → prints `echo-recheck cannot-evaluate --out exists: {out}`
   → `return 2`, **before** `evaluate()` (the only caller of `start_server()` at line 383,
   the only `subprocess.Popen` at line 188). `sha256(c) = ced0ee89…` identical in worktree
   and in blobs at `35b9018` and `513eba3b` — the tool was not touched by this repair.

2. **Reproduced independently on my own sentinel** (`/fast/scratch/hyaku/kama-r29/w1/ReviewEchoExit2/`,
   never in the lane): same byte-identical stdout, `exit=2`, sentinel sha256 unchanged
   before/after. Also reproduced the receipt's exact relative-`--out` command form.

3. **No server starts — three independent measurements.** (a) `pgrep -a -f llama-server` →
   none before/after, no listener on 48231-48233; (b) `strace -f -e
   trace=execve,clone,clone3,vfork,fork` shows the **only** `execve` is `/usr/bin/python3`
   itself — no `llama-server` exec, no clone/fork at all; (c) in-process spy:
   `evaluate_calls: []`, `start_server_calls: []`.

4. **Receipt internal consistency — all pass.** `lane_tip 35b90184f638…` = `513eba3b`'s
   parent (the pre-commit tip, correct for a self-referential receipt); `date
   2026-10-23T12:00:06Z` matches `existing.json` mtime `12:00:06.951Z` / `receipt.txt`
   mtime `12:00:07.142Z`; `sentinel_sha256_before/after ca3d163b…` = the sha256 of the
   committed `existing.json` (`{}`, 3 bytes); working-tree bytes == committed bytes
   (`6048be3e…`).

5. **The one gap: `llama_server_after: 0` is NOT the discriminator it appears to be.**
   `main()` has a **second** site (line 463-468) that prints the **byte-identical** message
   and returns 2 — but only *after* a server has started, served all six requests and been
   terminated. I forced that late path by monkeypatching `evaluate()` to create the file
   after the `lexists` check: identical stdout, identical exit 2. So **every** field the
   receipt records is equally consistent with a run in which a server DID start.

   What actually carries the proof is `sentinel_sha256_before`: it establishes the sentinel
   **pre-existed**, so line 442's `lexists` was necessarily true, so `main()` returned at
   line 443 and the late site was structurally unreachable.

6. **The clean, missing discriminator is the derived server log.** Any server start creates
   `<out>.server.log` (`start_server()` opens it `open(log_path,"xb")`, line 188;
   `log_path = Path(str(out) + ".server.log")`, line 336). The refusal path creates nothing.
   The committed lane tree already carries this negative evidence —
   `git ls-tree -r HEAD .ufo/waves/round-29/repairs/echo-exit2/` lists exactly
   `existing.json` and `receipt.txt`, **no `existing.json.server.log`** — but the receipt does
   not *say* so.

## Recommended (optional) receipt addition

```
derived_server_log .ufo/waves/round-29/repairs/echo-exit2/existing.json.server.log absent
```

Optionally also record `cwd` (the relative `--out` implies cwd = lane root) and the exact
`pgrep`/`ss` commands behind the `llama_server_*` counts, so those counts are checkable
rather than asserted. This is a strengthening, **not** a correction — the receipt already
proves the routed item's literal ask ("a receipt of the exit code for the exit-2 refusal on
an existing path") and is correctly committed.

## Disclosures

- Lane repo **not** written by me; all artifacts under my scratch dir and
  `.ufo/waves/round-29/w1/out/ReviewEchoExit2/`. `git status --porcelain` for
  `.ufo/waves/round-29/repairs/` and `tools/echo-recheck.py` is empty.
- **One unintended server start:** my positive-control run (falsifier for finding 6) against a
  *non-existent* `--out` took the tool's full path and started a real llama-server on
  `127.0.0.1:48231` — the tool's own hard-coded candidate, not the `48300 + item index` the
  lane bounds specify for a hand-launched server. The tool terminated it itself (shutdown
  proof: `exited: True`, `port_closed: True`, `connect_exit: 111`, `ss_ltnp_listeners: []`).
  Post-run containment re-verified: no llama-server process, no listener on 48231-48233 or
  any 483xx, no files outside my scratch dir. I should have pinned a free `--port` or
  skipped that falsifier.
- **No tools installed or updated** — `strace`, `ss`, `pgrep`, `python3`, `git` were already
  present; nothing to record against the tooling directive.
- No subagent/labrat spawned; read-only git plus one instrumented `python3` run under
  `strace`.

## Evidence

- `.ufo/waves/round-29/w1/out/ReviewEchoExit2/review.md` (full review)
- Scratch evidence: `/fast/scratch/hyaku/kama-r29/w1/ReviewEchoExit2/`
  (`strace.out`, `strace2.out`, `order.py`, `spy2.py`, `latepath.py`, `sentinel.json`)
