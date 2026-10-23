# Review — routed repair 6: `tools/echo-recheck.py` exit-2 refusal on an existing `--out`

Seat: `ReviewEchoExit2` (executor, reviewer of the L1's repair). Round 29, wave 1.
Lane repo (read-only for this seat): `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Item under review: round-28 spot-check routed item 6
(`corpus/lessons/round-28-verifier-spotcheck.md:239-240`):

> **`tools/echo-recheck.py`.** Commit a receipt of the exit code for the exit-2 refusal on an
> existing path. Only the sentinel file is committed now.

## Verdict

**The receipt proves the refusal and proves that no server starts — but only by a step the
receipt does not itself spell out.** One concrete, cheap addition would make the "no server
starts" claim self-evident from the receipt's own fields.

| Question | Answer |
|---|---|
| Does the receipt prove the exit-2 refusal happened? | **Yes**, and I reproduced it independently on my own sentinel. |
| Does the receipt prove **no server starts**? | **Yes, as a deduction** from the receipt's fields + the tool code — but **not from any single field alone**, and the field that looks like it does (`llama_server_after: 0`) does **not**. |
| Is routed item 6's literal ask satisfied? | **Yes** — the receipt is committed (lane `513eba3b`) and records the exit code. |
| Is the receipt falsified by any check I ran? | **No.** Nothing in it is wrong. |

## 1. What the receipt says (verbatim)

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/repairs/echo-exit2/receipt.txt`
(committed at lane `513eba3b`; working-tree bytes == committed bytes,
sha256 `6048be3efaf07cbf8f2bfd0570ee294c762e3f728776add16e317008fc2791d0`):

```
tool_sha256 ced0ee8976ca0c03e31d17d72d99c7df5b7a6fa315b19f33d873144ca9df2d28
lane_tip 35b90184f638ab6a4149092b93143c7a2b873787
date 2026-10-23T12:00:06Z
sentinel_sha256_before ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356
llama_server_before: 0
--- command: timeout 60 /usr/bin/python3 tools/echo-recheck.py --out .ufo/waves/round-29/repairs/echo-exit2/existing.json
echo-recheck cannot-evaluate --out exists: .ufo/waves/round-29/repairs/echo-exit2/existing.json
exit=2
sentinel_sha256_after ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356
llama_server_after: 0
```

## 2. The code: where the refusal sits, and relative to the server start

`tools/echo-recheck.py` (sha256 `ced0ee89…`, identical in the worktree and in the blobs at
both `35b9018` and `513eba3b` — the tool was not touched by this repair):

* `main()` at **line 441-444** — the refusal, **before** anything else:

  ```python
  out = Path(args.out)
  if os.path.lexists(out):
      print(f"echo-recheck cannot-evaluate --out exists: {out}")
      return 2
  ```

  This is the *only* place `evaluate()` is reached from; `evaluate()` is the sole caller of
  `start_server()` (**line 383**), and `start_server()` is the only place `subprocess.Popen`
  appears (**line 188**). `grep -n "Popen\|start_server"` over the tool returns exactly
  `184:def start_server`, `188: proc = subprocess.Popen(...)`, `383: argv, proc, pgid = start_server(...)`.

* `main()` at **line 463-468** — a *second* site that prints the **byte-identical** message
  `echo-recheck cannot-evaluate --out exists: {out}` and also returns 2, but this one is
  **after** `evaluate()` has already run the whole probe:

  ```python
  try:
      with open(out, "x") as f:   # FileExistsError -> same message, exit 2
  except FileExistsError:
      print(f"echo-recheck cannot-evaluate --out exists: {out}")
      return 2
  ```

  Two distinct exit-2 sites, one distinct message string. This is the crux of the review.

* The docstring (**lines 15-17**) documents `exit 2` = `echo-recheck cannot-evaluate REASON`,
  and **lines 22-24** document the `--out`-must-not-exist contract.

**⇒ The refusal at line 442 precedes any server start, by construction.**

## 3. Independent re-run on my own sentinel (never in the lane)

Scratch: `/fast/scratch/hyaku/kama-r29/w1/ReviewEchoExit2/` (lane untouched: `git status
--porcelain -- .ufo/waves/round-29/repairs/ tools/echo-recheck.py` is empty).

### 3a. Exact reproduction of the receipt's command form

```
$ cd /fast/scratch/hyaku/kama-r29/w1/ReviewEchoExit2
$ printf '{}\n' > .ufo/waves/round-29/repairs/echo-exit2/existing.json
$ timeout 60 /usr/bin/python3 .../tools/echo-recheck.py --out .ufo/waves/round-29/repairs/echo-exit2/existing.json
echo-recheck cannot-evaluate --out exists: .ufo/waves/round-29/repairs/echo-exit2/existing.json
exit=2
```

Byte-identical stdout to the receipt, same exit code. The message goes to **stdout**
(re-running with `2>&1 1>/dev/null` produced no stderr).

### 3b. Absolute-path sentinel (my own file, distinct sha256)

```
$ sha256sum sentinel.json   -> e4a86f177b6d10ec73bfc54188e5928575578deee0b03106e4ed2ef7086e7cc1  (before)
$ timeout 60 /usr/bin/python3 .../tools/echo-recheck.py --out sentinel.json
echo-recheck cannot-evaluate --out exists: sentinel.json
exit=2
$ sha256sum sentinel.json   -> e4a86f177b6d10ec73bfc54188e5928575578deee0b03106e4ed2ef7086e7cc1  (after)
```

Sentinel unchanged — matching the receipt's before/after equality.

### 3c. **No server starts** — three independent measurements

1. **Process count, before and after:** `pgrep -a -f llama-server` → `none` both times;
   `ss -H -ltn | grep -E ':(48231|48232|48233)\b'` → no listeners before or after.
2. **Syscall trace (`strace -f -e trace=execve,clone,clone3,vfork,fork`)** — the *only*
   `execve` in the whole run is the interpreter itself:

   ```
   828807 execve("/usr/bin/python3", ["/usr/bin/python3", "/home/vgpnk/Projects/shokunin/ka"..., "--out", "sentinel.json"], 0x7ffccf2227e0 /* 263 vars */) = 0
   828807 +++ exited with 2 +++
   ```

   No `llama-server` exec, no `clone`/`fork`/`vfork` at all. The tool never spawned a
   subprocess.
3. **In-process spy** — wrapping `m.start_server` and `m.evaluate` and calling `m.main()`:

   ```
   stdout: 'echo-recheck cannot-evaluate --out exists: .../sentinel.json\n'
   exit: 2 evaluate_calls: []      start_server_calls: []
   ```

   `evaluate()` is never entered, therefore `start_server()` is unreachable.

### 3d. Side-effect containment of the refusal path

The refusal writes **nothing**: the sentinel's directory still held only `existing.json` after
the run — **no derived `<out>.server.log`** was created.

## 4. Does the receipt *prove* "no server starts"? — the honest answer

**Yes, but the proof needs one inference the receipt leaves implicit, and one of its own
fields is a red herring.**

### 4a. `llama_server_after: 0` is **not** the discriminator it looks like

A reader would take `llama_server_before: 0` / `llama_server_after: 0` as the proof that no
server ran. It is not. The **late** exit-2 site (line 467) is reached *after* a server has
started, served all six requests and been terminated cleanly — so a late-path run also leaves
**zero** llama-server processes behind and also prints the **identical** stdout line and
exits 2.

I demonstrated this directly by monkeypatching `evaluate()` to create the `--out` file
*after* the `lexists` check (simulating the race that reaches line 467):

```
stdout: 'echo-recheck cannot-evaluate --out exists: .../late.json\n'
exit: 2
```

Byte-identical message and exit code to the early path. **Every field the receipt records —
stdout, `exit=2`, sentinel sha unchanged, `llama_server_after: 0` — is equally consistent
with the late path, in which a server DID start.**

### 4b. What *does* discriminate, and it is in the receipt

**The receipt records `sentinel_sha256_before` — i.e. it establishes that the sentinel
already existed before the run.** That, combined with the code, is decisive:

* The tool's first act after argument parsing is `os.path.lexists(out)` (line 442). Because
  the sentinel provably pre-existed, that check was **necessarily true**, so `main()`
  returned 2 at **line 443** — the early site — and `evaluate()` (hence `start_server()`,
  hence any `Popen`) was never reached.
* The late site (line 467) is therefore **structurally unreachable** for this run: it needs
  the file to be *absent* at line 442 and *present* at line 463.

So the receipt's `sentinel_sha256_before`/`_after` pair is doing the real evidentiary work,
and the `llama_server_*` lines are corroboration, not proof.

### 4c. The one artifact that would make it self-evident (and is missing)

The clean, single-field discriminator is the **absence of the derived server log**. A server
start *always* creates `<out>.server.log` — `start_server()` opens it with `open(log_path,
"xb")` at line 188, where `log_path = Path(str(out) + ".server.log")` (line 336). The
refusal path creates nothing.

I confirmed the artifact is real and discriminating by producing the **positive control**: a
run against a *non-existent* `--out` (so the tool took the full path) left both
`out.json` and `out.json.server.log` on disk, with the log's first line
`llama_server: initializing ...` and the shutdown proof
`{'exited': True, 'port': 48231, 'port_closed': {'closed': True, 'connect_exit': 111,
'ss_ltnp_listeners': []}}`.

**The committed lane tree already carries this negative evidence:**
`git ls-tree -r HEAD .ufo/waves/round-29/repairs/echo-exit2/` lists exactly
`existing.json` and `receipt.txt` — **no `existing.json.server.log`**. But the receipt does
not *say* so, so the reader has to notice the omission in the tree to get the strongest
reading.

### 4d. Recommended one-line addition (optional; the item is already met)

Adding this to the receipt would make the "no server starts" claim self-evident without any
inference:

```
derived_server_log .ufo/waves/round-29/repairs/echo-exit2/existing.json.server.log absent
```

Optionally also record `cwd` (the relative `--out` in the command implies cwd = lane root) and
`stdout_sha256` / the exact `pgrep`/`ss` commands used for the `llama_server_*` counts, so
those counts are checkable rather than asserted.

## 5. Internal consistency of the receipt — all checks pass

| Receipt field | Verification | Result |
|---|---|---|
| `tool_sha256 ced0ee89…` | `sha256sum tools/echo-recheck.py`; `git show 35b9018:tools/echo-recheck.py \| sha256sum`; `git show 513eba3b:tools/echo-recheck.py \| sha256sum` | all three **identical** ✅ |
| `lane_tip 35b90184f638…` | `git show -s --format=%H 35b9018` | matches; and it is `513eba3b`'s parent, i.e. the tip **before** the receipt was committed ✅ |
| `date 2026-10-23T12:00:06Z` | `existing.json` mtime `12:00:06.951Z`, `receipt.txt` mtime `12:00:07.142Z` (UTC; host is `-03`) | internally consistent, sentinel created ~190 ms before the receipt was written ✅ |
| `sentinel_sha256_before/after ca3d163b…` | `sha256sum .ufo/waves/round-29/repairs/echo-exit2/existing.json` (`{}`, 3 bytes) | both match; the committed file's sha256 **is** `ca3d163b…` ✅ |
| `exit=2` | reproduced on my own sentinel | ✅ |
| stdout line | reproduced, byte-identical, on stdout | ✅ |

The receipt is also **self-consistent about its own commit**: it was written while HEAD was
`35b9018` and was committed in the following commit `513eba3b`, so `lane_tip` correctly
points at the pre-commit tip.

## 6. Disclosures

* **I did not write to the lane repo.** All my artifacts are under
  `/fast/scratch/hyaku/kama-r29/w1/ReviewEchoExit2/` and
  `.ufo/waves/round-29/w1/out/ReviewEchoExit2/`. `git status --porcelain` for
  `.ufo/waves/round-29/repairs/` and `tools/echo-recheck.py` is empty.
* **Disclosure — one unintended server start.** My positive-control run (§4c) against a
  *non-existent* `--out` took the tool's full path and therefore **started a real
  llama-server** on `127.0.0.1:48231` — the tool's own first free port of its hard-coded
  candidates `48231-48233` (`PORT_CANDIDATES`, line 73), not the `48300 + item index` the
  lane bounds specify for a hand-launched server. I did not launch the binary myself and
  used no custom argv; the tool did, via its own code path. It terminated the server itself
  (its own shutdown proof: `exited: True`, `port_closed: True`, `connect_exit: 111`,
  `ss_ltnp_listeners: []`). Post-run containment re-verified: `pgrep -a -f llama-server` →
  `none`; no listener on 48231-48233 or any 483xx; no stray files outside my scratch dir.
  I should have pinned a free port with `--port` or skipped that falsifier.
* **No tools installed or updated** — nothing in this task needed a new tool
  (`strace`, `ss`, `pgrep`, `python3`, `git` were all already present). Nothing was
  installed, so there is nothing to record against the tooling directive.
* **No subagent/labrat was spawned**; all work was done with read-only git plus one
  instrumented `python3` run of the tool under `strace`.

## 7. Bottom line for the L1

Routed repair 6 is **satisfied and correctly committed** at `513eba3b`:
`.ufo/waves/round-29/repairs/echo-exit2/receipt.txt` records the exit-2 refusal on an
existing `--out`, with the tool's sha256 and the lane tip anchored, and the sentinel proven
untouched.

Nothing in the receipt is false. The single improvement worth making is to record the
**absence of the derived `existing.json.server.log`** (and ideally the cwd and the exact
count commands), because today the "no server starts" conclusion rests on the reader
connecting `sentinel_sha256_before` (pre-existence) to `main()`'s line-442 `lexists` check,
while the superficially obvious field, `llama_server_after: 0`, does not carry that weight
on its own. This is an **optional strengthening**, not a correction — the routed defect is
closed either way.
