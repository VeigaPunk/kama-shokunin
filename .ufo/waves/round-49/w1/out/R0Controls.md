# Round 49, w1, seat R0Controls — control strength review (C1, C2)

**Verdict:** The five committed controls rebuild bit-for-bit (only `tip=` lines differ by construction); the junk-c1 fake-witness control is killed by the exe leg alone; a stronger cheat — running the real frozen b11909 binary from a host copy — passes every witness leg (no current leg stops it; this is the declared limit L1), and the witness *hold* itself is not actually enforced (`released:true` is self-asserted, `waited_ms` never validated); on C2, a strictly cheaper origin formulation (file-birth blob, and birth∪tip) passes all 8 fixture scenarios but is stopped by the counter's own lane leg (exit 1, `regressed 1`) — the committed controls miss this class but the frozen counter does not.

## 1. Scope and method

- Lane (read-only): `/home/vgpnk/Projects/shokunin/kama-shokunin` at HEAD `122c4ee9`; build commit under test `74558c71c38ceaeace15fd4cf8aa9d84977584b1`.
- Scratch: `S=/fast/scratch/hyaku/kama-r49/R0Controls` (`TMPDIR=$S`), deleted at the end.
- Controls rebuilt from a copy of `.ufo/waves/round-49/controls/`:
  `TMPDIR=$S python3 $S/controls-copy/build_controls.py /home/vgpnk/Projects/shokunin/kama-shokunin $S/ctl`
  → receipts written beside the copy (never into the lane). Exit 0, wall 88.55 s.

### Rebuild vs committed set (diff of receipts)

| receipt | difference vs committed `.out` |
|---|---|
| `base.c1.out` | none (byte-identical) |
| `base.c2.out` | none (byte-identical) |
| `junk-c1-fake-witness.c1.out` | only line 1 `tip=` (clone commit hash; by construction) |
| `junk-c2-no-exempt.c2.out` | only `tip=` |
| `junk-c2-word-token.c2.out` | only `tip=` |

The control build is deterministic: identical outcome content, exit codes, detail lines.

## 2. C1 controls — strength

### 2.1 What the committed junk-c1 control exercises
`FAKE_REPLAY` (`build_controls.py` lines 30–84): a python HTTP stub that (a) names itself `-m <model>` (argv spoof), (b) serves `/tokenize` and `/detokenize` from the model's own GGUF vocabulary (greedy longest-match), (c) writes `D/ready.json {port, pid}`, (d) waits for `D/release`, (e) kills the stub, (f) copies the original receipt as the rerun receipt with `witness.released: true`, (g) writes `{match: true, ...}`.

Observed result (`junk-c1-fake-witness.c1.out`): `witness=0 cap=0 newrow=0 witnessed=0/3 met=False`; the ONLY witness complaints are
`exe sha256 375532... is not the frozen server` on all three witnesses.
So the control passes **every other leg** (listen inode ownership, `-m` hash, nonce round-trip, rerun receipt `released:true`, post-exit teardown). The `cap` FAIL line is inherited from BASE (the control leaves the live tool unmutated; the sparse member is still hashed unbounded at base → 30 s timeout), not a property of the fake.

Counter legs cited: `round49-replay-witness-audit.py` — exe `observe()` lines 260–262; listen 263–265; cmdline model 266–275; nonce 276–288; ready poll 300–311; release write 312–313; rerun receipt witness check 323–326; post-exit teardown 327–332; cap leg 353–391.

### 2.2 Stronger cheat designs (designed, not committed) and the leg that stops each

| # | cheat | legs it defeats | leg that still stops it |
|---|---|---|---|
| A | Run the real frozen binary `/home/vgpnk/.local/opt/llama-b11909/llama-server` from a host copy with the frozen model, real hold, honest receipt | exe (same bytes), listen, model, nonce, teardown, receipt | **none** — this is the declared residual (preregistration limits[0]: "a replay that runs the same binary from a host copy still passes the witness"); archive provenance is the round-48 replay leg's digest domain, not this witness's |
| B | Same but with a different `-m` file | exe | **model leg** (`-m` file hash, line 272–273) — also the nonce vocab leg would disagree |
| C | Real binary, correct model, but minimal hold: write ready.json, keep the server up ~2–5 s, exit 0 before ever consuming `D/release` | exe, listen, model, nonce (if the observer catches the server alive), teardown, receipt | currently **nothing reliable**: the counter polls every 0.2 s (line 305), so it usually observes inside the window; the hold is verified only by the self-asserted `released:true` (lines 324–326) — `waited_ms` is never validated. This is the substantive gap (see §2.3) |
| D | Python stub that never runs llama-server (the committed control) | — | **exe leg** (line 261–262), as observed |

So: the exe leg is the load-bearing identity leg and is a good control of the "server must be the frozen binary" property; the model leg pins the vocabulary; the hold protocol, however, is only cooperatively enforced.

### 2.3 Defect (C1 counter, witness hold not enforced)
- Location: `tools/round49-replay-witness-audit.py:306–326` (ready poll + rerun-receipt witness check) and `tools/kama-llamacpp-live.py:285–305` (`hold_for_witness`). The replay side passes `--witness-dir/--witness-timeout` at `tools/kama-live-replay.py:277–283`.
- Evidence: cheat D (committed control) already shows `released:true` with no wait and no `waited_ms` is accepted; a host-copy variant of cheat C would therefore pass all four observe legs while never holding for the observer's release.
- Proposed fix (counter side, three cheap gates):
  1. In `witness_one`, before writing `D/release`, require `p.poll() is None`; if the replay already exited, record `replay exited before release` and fail (closes cheat C deterministically — the replay must stay alive until the observer releases).
  2. In `observe()` (or before it), require `pid_alive(pid)`; if the pid is dead at observation time, fail closed (currently only the post-exit check at line 327–329 knows the pid is gone).
  3. Validate the rerun receipt's `witness.waited_ms` is present and > 0 (and optionally that `ready.json` carried `schema == "kama-live-witness/v1"`, which is currently unchecked).
- These do not weaken the declared host-copy residual (A), which is accepted by design.

## 3. C2 controls — strength, and the "cheaper than origin" question

### 3.1 Control behavior
- `junk-c2-no-exempt.c2.out` (carve-out dropped): `fixture=0 scenarios=4/8`, broken launder/substring/negated/wildcard-self — correct kill.
- `junk-c2-word-token.c2.out` (word-bound + negation window, no origin rule): `fixture=0 scenarios=7/8` — launder FAIL (exit 0, want 1) **and** lane leg fails (`0718b6ab ungraded 72 > natively exempt 65`) — correct kill on two independent legs.

### 3.2 Candidate cheap tool: file-birth origin (strictly cheaper than rev-list walk)
Mutation: `tools/append-only-audit.py` `origins()` (lines 431–449 of the v4 tool) replaced by reading only the **first blob of the file** (birth) instead of walking `rev-list --topo-order --reverse` over all unique blobs; all other v4 definitions unchanged (diff in `out/R0Controls/cheap-origin.diff`).

Evidence (counter runs on a scratch clone at tip `74558c71`):

```
# baseline (unmutated v4 tool)
$ python3 tools/round49-append-audit-v4-check.py --repo $S/mutclone --tip 74558c71... --scratch $S --out ...
fixture=1 lane=1 scenarios=8/8 met=True          (exit 0)
# birth-only origin (V1)
tip=62a56de9...  fixture=1 lane=0 scenarios=8/8 met=False   (exit 1)
detail: lane: tool exit 1 events 5 bad_declarations 0 regressed 1 ungraded_lines 25
detail: lane: event dd9f5dc6... ungraded 1 <= natively exempt 23
detail: lane: event 0718b6ab... ungraded 24 <= natively exempt 65
# birth ∪ tip-exempt presence (V2)
tip=695c2fb1...  fixture=1 lane=0 scenarios=8/8 met=False   (exit 1)
detail: lane: tool exit 1 events 5 bad_declarations 0 regressed 1 ungraded_lines 66
detail: lane: event dd9f5dc6... ungraded 2 <= natively exempt 23
detail: lane: event 0718b6ab... ungraded 64 <= natively exempt 65
```

Findings:
- Both cheap variants pass **all 8 fixture scenarios** (including launder) — so the fixture set alone does not discriminate them (the launder fixture's text sits under `## Axes` at deletion time, so any birth/parent-state rule grades it "). The **lane leg catches both** through the tool's own exit code: the extra lines they grade (16 of 17 on `dd9f5dc6`, 41 of 65 on `0718b6ab` under V1) turn a held SCORECARD.md event into `regressed` → exit 1. The event-level bound (`ungraded <= natively exempt`) is satisfied, but exit 0 is not.
- Conclusion: no cheaper-than-origin implementation that skips the history walk escapes the frozen counter on this lane; the counter's lane leg is the load-bearing guard against origin approximations. The committed control set does not cover this class (both junk-c2 controls alter the definitions wholesale, not the origin computation), so I recommend adding a `junk-c2-cheap-origin.c2.out` control using the V1 mutation (deterministic `met=False`, `scenarios=8/8`) — the unified diff is in `out/R0Controls/cheap-origin.diff`.

### 3.3 Secondary cheap candidate: negation-window widening (any negation token anywhere) — also defeated
A tool replacing the 3-word window (`NEG_WINDOW`, tool line 220–221) with any-token-anywhere is cheaper (no window bookkeeping). It passes all 8 fixtures (the `negated` fixture expects unbound and still is), but on the lane the declaring line `SKILL.md:578` contains `... 0 no violation, ...` — the token `no` is a negation — so the `corpus/SOURCES.md` row would unbind → `bad_declarations >= 1` → lane leg fails. So widening is pinned by the lane leg's declarations check; narrowing is pinned by the `negated` fixture. The window is thus defended from both sides.

## 4. Residual risk and verification gaps
- C1: declared host-copy residual (cheat A) remains by design; the only *new* gap found is the unenforced hold (cheat C; §2.3), which the proposed gates close.
- C2: origin is first-appearance-based; the counter's own lane bound recomputes full origin, so the honest tool and the counter pay the same cost; no cheaper semantic shortcut was found that passes (V1/V2 both fail).
- Leftover processes: `pgrep -f llama-server` shows two llama-server process groups under `/fast/scratch/hyaku/kama-r49/M1Ctr/` (sibling seat, C1 envelope runs) — not started by this seat, left untouched. This seat started no llama-server; no teardown owed.

## 5. Tools installed
None (no pacman, uv, npx, or binary installs were needed or performed).

## 6. Deliverables
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/R0Controls.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/R0Controls/`:
  - `base.c1.out`, `base.c2.out`, `junk-c1-fake-witness.c1.out`, `junk-c2-no-exempt.c2.out`, `junk-c2-word-token.c2.out` (rebuilt receipts)
  - `mutclone-baseline.c2.out` (C2 at 74558c71: met=True)
  - `mutclone-birth-origin.c2.out` (V1: fixture=1 lane=0)
  - `mutclone-birth-tip.c2.out` (V2: fixture=1 lane=0)
  - `cheap-origin.diff` (proposed junk-c2-cheap-origin control mutation)
