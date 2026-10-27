# kama round 50 lesson

author: kama L1 (agent `KamaR50`); wave seats' drafts integrated by the L1 (named per row)
date: 2026-10-27
base: `26ecba64ad6fb571d09074b07202d1618a46ecd1` (round-49 verifier spot-check; lane remote tip at launch)
freeze: `601c8889f33d1797c712feb753974c20cf891264` (preregistration `.ufo/waves/round-50/preregistration.json`, `frozen_at_utc` 2026-10-27T00:20:47Z; KQ64 receipt `.ufo/waves/round-50/freeze/prereg-time-check.out` → `RESULT pass`, `exit=0`)
build: `97c864bead3ee4a2f629574e77263d33834ec98a` (after the freeze, before the wave); build-fix `3d42897b65294ad963cd3686ced4666822e0ec73`; battery receipts `3b79eaddf38246c637cc7ba1a94ab363422876b6`
measured: SCORECARD §Round-50 measured results

## Claims

- **C1 operability 8→8 — the process-bound replay witness, sourced on S496 and S497.** `tools/kama-live-replay.py` starts the live tool isolated (`python -I`, environment allow-list PATH/HOME/LANG/LC_ALL/TMPDIR) with a parent-death signal (SIGTERM, preexec_fn prctl), and sets its own parent-death signal, so killing whatever started a replay takes replay, live tool and server down (round-49 closure R2); `tools/kama-llamacpp-live.py` records `model_mapping` in the receipt — the file the server maps per `/proc/<pid>/maps` (dev, inode, pathname), re-opened O_NOFOLLOW, fstat-checked, hashed (round-49 closure R1) — and the replay refuses a rerun whose mapping does not hash to the receipt's model. The frozen counter `tools/round50-replay-bind-audit.py` runs each replay from a `python3 -I -c` invoker with planted canaries (KAMA_R50_CANARY environment + PYTHONPATH sitecustomize marker), and checks bind = for each receipt: exe digest (S495), listener ownership, a fresh nonce round-trip against the counter's own GGUF vocabulary (S494), the server descending from the replay process, canary absence, the mapped file (dev/inode/sha256) matching the rerun receipt's `child_pid` == observed pid == ready.json pid; teardown = SIGKILL of the invoker during the hold removes every descendant within 30 s and the port refuses. Base `26ecba64`: `bind=0 teardown=0 newrow=0 bound=0/3 met=False`; build `97c864be`: `bind=1 teardown=1 newrow=1 bound=3/3 met=True`.
- **C2 calibration 7→7 — append-only-audit v5 definitions, sourced on S498.** A deleted line in an eligible exempt section stays ungraded only when the union of section titles at every birth of its key — a commit whose blob holds the key while no parent's blob does — contains an exempt title (order-independent: same final trees give the same verdict under either merge-parent order); sections ignore `## ` lines inside CommonMark fenced code blocks; origin keys drop one trailing CR; graded + ungraded equals deleted for every event. Counter `tools/round50-append-audit-v5-check.py`: twelve constructed fixtures plus the lane (exit 0, all rows bound under the v4 binder, tool ungraded <= the counter's v5 native count). Base: `fixture=0 lane=1 scenarios=9/12 met=False`; build: `fixture=1 lane=1 scenarios=12/12 met=True`; lane `ungraded_lines 89` (v4: 82) — the seven `## Capabilities` mirror rows of `0718b6abbda6` have a head birth under v5 and are now ungraded (round-49 seat K2Origin F6 resolved).

Measured values: SCORECARD §Round-50 measured results.

## Gate

| Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why |
|---|---|---|---|---|---|
| S496 | admit (tier A, mined) | https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html | 2026-10-27T00:14:13Z (text copy `.ufo/waves/round-50/c1/proc_pid_maps.5.txt`; man-pages 6.19, page dated 2026-02-08) | "dev is the device (major:minor); inode is the inode on that device" and "The pathname field will usually be the file that is backing the mapping." (§DESCRIPTION) | grounds reading which file a running server maps from `/proc/<pid>/maps` and hashing that same file through its pathname |
| S497 | admit (tier A, mined) | https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html | 2026-10-27T00:14:13Z (text copy `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt`; man-pages 6.19, page dated 2026-02-08) | "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process ... to which the caller is subsequently reparented." (§DESCRIPTION) | grounds the replay and live child dying with the process that started them, so killing the invoker takes the whole tree down |
| S498 | admit (tier A, mined) | https://spec.commonmark.org/0.31.2/#fenced-code-blocks | 2026-10-27T00:14:13Z (text copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`, section 4.5 only) | "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~)." (§4.5) | grounds the fence-aware section scanner: a `## ` line inside a fence is content, not a heading |

Rejects (each grounded by a command; the ablation controls are `.ufo/waves/round-50/controls/`):
- **Reject `/proc/<pid>/environ` alone as proof of interpreter cleanliness.** The marker file is the check (a planted sitecustomize import stamps it); environ may be unreadable for other uids (fails closed). Flip: never — the marker tree.
- **Reject a maps inode without the file hash.** A host copy of the model path would match the inode but not `MODEL_SHA`; the counter re-opens the pathname O_NOFOLLOW, fstat-checks dev/inode, then hashes. Flip: never.
- **Reject `pdeathsig` alone as proof of teardown.** The counter kills the invoker and observes the port; a host that reparents without delivering the signal fails the leg. Flip: never.

## Mistakes

| # | Class | Evidence | Captured-by | Fix (shown able to fail) |
|---|---|---|---|---|
| 1 | Source row with an odd number of backticks breaks the sources-append-only parser | S498 as first drafted at the build had 7 backticks; `sources-append-only.py --from 26ecba64 --to 97c864be` → `error: ...:251: unterminated table row (no closing pipe)`, exit 2 | `split_cells()` treats backticks as code-span toggles, so a closing pipe inside a still-open span is ignored | build-fix commit `3d42897b` re-balanced the ticks (4); sao then exits 0 and prints `added S498 (allowed)`; the row-parser check can fail on the old row |
| 2 | Wave state markers landed untracked | `w1.ready` / `w1.ready.dispatched` are untracked at the lane (seat X17Cleanup observation; round-49's pair is tracked) | seat X17Cleanup | name the markers in the wave-commit path list, as this round does |
| 3 | The regression battery at the build reads `35` spot-checks while the tree holds 36 | `round41-scorecard-reconcile.py` → `run_bad=1 mismatches=1`, `round42-selfdesc-reconcile.py` → `r41=1`, `round43-registry-audit.py` → `spot=1` (all at `97c864be`; identical at base — a carried staleness) | seat X15NoHarm2 / X2HeadSim2 | the round-50 integration re-anchors the calibration row to 36; the reconciles then pass at the measured tip |
| 4 | C1's `--out` write happens after printing without creating parent dirs | seat S2Gate2: a counter run with `--out <missing-dir>/x` prints the met line then exits 1 | seat S2Gate2 (frozen counters: finding, not patch) | the round-51 counter creates `--out` parents before writing; routed |
