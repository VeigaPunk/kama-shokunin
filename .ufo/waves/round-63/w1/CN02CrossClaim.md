# CN02CrossClaim — round-63 cross-claim connector (kama)

Seat: CN02CrossClaim (connector, leaf, no subagents). Milestone: scan overlaps.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (= lane HEAD). Base: `7ee8cbdf160f8c945954e4737e7a2f797e3b2987`.
Scratch (removed before yield): `/fast/scratch/hyaku/kama-r63/w/CN02CrossClaim`. Receipts: `.ufo/waves/round-63/w1/out/CN02CrossClaim/`.
No commit, push, or mutating git against the lane. All mutations live in my scratch clone (`git clone --shared`, toplevel asserted).

## 0. Findings in brief (no verdict on either claim)

1. **C2 does not read C1's tool change.** C2 at a tip with C1's tool reverted to base gives a one-liner identical to the tip's. Its only shared inputs with C1 are the dependency `tools/kama-llamacpp-live.py`, the port registry, and host-wide process state.
2. **C1 does not read C2's registry.** C1 at a tip without `registry/capability-claims-r63.tsv` gives a one-liner identical to the tip's.
3. **The real C1→C2 coupling is through the reconciler, not the counter's bound rows.** Any C1 landing that touches SCORECARD head, canonical list, PROVINCE.md or the reconciler's census moves `selfdesc_mismatches` (simulated: 8→9 and 8→10). C2's population, sensitivity and controls do not move.
4. **At the tip, C2's only failing gate is `selfdesc_mismatches=8`.** The eight lines fall in seven categories (r41 coverage, banner, planned ×2, retired, saturation, caps, province). Banner and planned are the round-63 label moves the freeze assigns to the L1. The other five categories were already failing at base (`selfdesc_mismatches=8` at `7ee8cbdf`), so the L1 must fix them too, not only the labels.
5. **Operability hazards found:** (a) `checkout_tip` in C2 silently reuses a stale `work/tip` tree when `--work` is reused across tips (demonstrated); (b) the context-capacity row is host-busy on this host regardless of capability, because host-wide `pgrep -x llama-server` sees the operator's servers; (c) C1's witness subprocess inherits the full environment while C2 allowlists it.
6. **Freeze/tree mismatch:** the freeze's frontier step says a SOURCES row opened this round is cited by C1's new checks. No tip tool or counter cites any S52x id (checked: `kama-completion-live.py`, `round63-c1-counter.py`, `round63-c2-counter.py`). The S527/S528 rows and the citing doc exist only as uncommitted lane-worktree edits.

## 1. Required verification — two one-liners

Scratch tips (fixture commits on top of the tip, made in my clone):
- `TA = 7f212098773bba16183eb0901b6e5aa97a88de57` — tip with `tools/kama-completion-live.py` reverted to base bytes (C1 tool change removed; C1 counter still present).
- `TB = 1671a9c48884caa9a4308b739483f8eb31c4efdb` — tip with `registry/capability-claims-r63.tsv` deleted (C2 registry removed).

**C2 at TA (tip lacks C1's tool change), fresh `--work`:**
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
exit 1 (expected: selfdesc gate, see §4).

**C1 at TB (tip lacks C2's registry), fresh `--work`:**
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0. The receipt is a real live `REQUEST_OK` run (port 39919; child pid 4180739 gone after teardown).

Control runs at the actual tip (`03a6a1d8`, fresh `--work` each):
- C2 at tip: the same line as TA (`selfdesc_mismatches=8`, `met=False`, exit 1).
- C1 at tip: the same line as TB (`controls_targeted=44/44 eval_selftest=3/3 … met=True`, exit 0; receipt child pid 62090, port 46129).

Reading: removing C1's tool change does not change C2's output at all, and removing C2's registry does not change C1's output at all, within the counters' own observables.

## 2. Inventory — artifacts both claims depend on or change

Read-only checks against lane HEAD (`03a6a1d8`) and worktree status.

| artifact | C1 counter reads | C2 counter reads | base→tip change | lane worktree (uncommitted) |
|---|---|---|---|---|
| `tools/kama-completion-live.py` | yes (tip blob, copied to `work/tip`) | no (not in any bound run; `.py` excluded from digest/hex scanners) | yes, v1→v2 (+112/−20) | not modified |
| `tools/kama-llamacpp-live.py` | yes (blob; imported by counter and by completion tool; `REGISTRY`, `refused_ports`, `pick_port`, `port_owned_by`) | yes (bound row `live-llamacpp-lifecycle` runs it at full tip) | no | not modified |
| `registry/endpoint-consumers.tsv` | yes (blob; port refusal) | yes indirectly (refused ports for live rows, full tree) | no | not modified |
| `SCORECARD.md` | no | yes (canonical blob; reconciler; scanners read `.md`) | yes, +23 (round-63 section and 12-row canonical list) | not modified |
| `PROVINCE.md` | no | yes (reconciler: r41 Axes hash + lines, province check; scanners) | no (tip sha `a60591b7…`, 188 lines) | modified +2 (round-63 note; sha `5e8ec39c…`, 190 lines) |
| `corpus/SOURCES.md` | no | yes (reconciler census, only if Capabilities section states counts; scanners) | no | modified +2 (S527, S528) |
| `corpus/knowledge/completion-request-plane.md` | no | yes (scanners read `.md`) | no | modified (+47/−3) |
| `registry/hexrun-ledger.tsv` | no | yes (`hexrun-census` scan) | yes, +1 row (`795b7be5…`, fleet commit) | not modified |
| `registry/digest-ledger.tsv` | no | yes (`digest-ledger` scan) | no | not modified |
| `registry/capability-claims-r63.tsv` | no | yes (own; 12 rows) | new | not modified |
| `tools/round42-selfdesc-reconcile.py` | no | yes (runs at tip; imports r41) | no | not modified |
| `tools/round41-scorecard-reconcile.py` | no | yes (via reconciler; Axes HASH and run facts) | no | not modified |
| `~/.cache/kama-shokunin/models/stories260K.gguf` (host) | yes (default model path; digest checked) | yes (`live-llamacpp-lifecycle` `--model`; `context-capacity`) | host file, not tip | n/a |
| `llama-server` on PATH (`~/.local/bin/llama-server`) | yes (server digest checked) | yes (all live rows) | host binary | n/a |
| host `pgrep -x llama-server` census | no (its child is a llama-server, see P3) | yes (`context-capacity` host-idle, `pgrep_foreign` for the host-busy alternative) | host state | n/a |

Lane state observed (read-only `git status`): `M PROVINCE.md`, `M corpus/SOURCES.md`, `M corpus/knowledge/completion-request-plane.md`; untracked `.ufo/waves/round-63/{source,w1,w1.ready,w1.ready.dispatched}` and a stray untracked `kama-shokunin/.ufo/` directory inside the lane root (created 09:26). The stray directory is not in the tip tree, is not read by any counter, and is not counted by the reconciler's `readme` check (it uses `ls-tree` at the tip). It is operator noise for the L1 to clear, not a claim input.

## 3. Counters that read another claim's artifact

- **C1 counter** (`tools/round63-c1-counter.py`): reads, from the tip, `tools/kama-completion-live.py` (own), `tools/kama-llamacpp-live.py` (shared dependency), `registry/endpoint-consumers.tsv` (shared). It reads no C2 artifact. Source check: its only `blob(...)` calls are lines 642, 656, 663.
- **C2 counter** (`tools/round63-c2-counter.py`): reads `SCORECARD.md` (canonical list; where a C1 row would land) and `registry/capability-claims-r63.tsv` (own). It runs the bound tools at the tip, including `kama-llamacpp-live.py` (C1 dependency). It runs `round42-selfdesc-reconcile.py`, which reads SCORECARD, PROVINCE, README, `corpus/SOURCES.md` (census), and the tree listing. The digest and hex scanners read every tip `.md`/`.tsv` outside `.ufo/`. It never reads C1's counter or C1's tool output.
- **Bound selftests that look like they touch SCORECARD/SOURCES but do not:** `append-only-audit --selftest` and `sources-append-only --selftest` run on in-memory or scratch fixtures; the real contract (`registry/append-only-contract.tsv`) is graded only in non-selftest mode, which C2 does not run. The SCORECARD contract row exempts `## Axes|Planned|Retired|Saturation|Capabilities`, so re-deriving the head does not trip it.

## 4. Causal paths

Each path is marked **V** (verified by a run in §1 or §5) or **R** (read from code, not run).

**P1 — shared dependency `kama-llamacpp-live.py` (V for identity, R for the change path).** Both counters execute the same tip bytes (C1 via a copy in `work/tip`, C2 via the archive). Any future edit changes both C1's listener/ownership path and C2's `live-llamacpp-lifecycle` row. This commit does not touch it (not in base→tip diffstat).

**P2 — shared port registry `endpoint-consumers.tsv` (V for identity, R for the change path).** C1 copies it only `if reg:` (line 663). If absent at a tip, a stale copy in a reused `work/tip` survives (R). C2's live rows refuse the same registered ports.

**P3 — host-wide llama-server census (V for the mechanism, R for the race).** C2's `context-capacity` row waits up to 20 s for "no other llama-server" host-wide and records the others. Its alternative (host-busy) is accepted whenever `pgrep` lists a llama-server before and after the run. Evidence: `c2-tip-context-capacity-cc.json` has `ok=False`, `other_pids_seen=[242776, 1706355, 3262613, 4081218, 4147617, 177775]`, `waited_s=21.5`. Pids 242776 and 1706355 are the operator's servers on 45669 and 1234. Pid 3262613 is a sibling claim's Ollama runner: `…/ollama-v0.40.11/lib/ollama/llama-server` (cwd under `kama-r61-closure`). That shows another claim's Ollama run already creates a `llama-server` child that C2's census counts. The transient pids 4081218, 4147617 and 177775 had exited by the time I checked; their owners cannot be attributed after the fact. The C1 children seen in receipts (62090, 4180739) do not appear in those lists. Consequence: whenever C1's hold-mode child is alive during C2's `context-capacity` cell, that row records host-busy. The row's declared outcomes allow that, so C2's `met` does not change but its recorded verdict can. **On this host the operator servers guarantee host-busy**, so the row's `true` outcome has not been reachable in any run here.

**P4 — C1 verdict gates the canonical list; the canonical list feeds the reconciler (V, §5 sim-1).** The freeze says `live-completion-request-plane` enters the canonical list only if C1 verifies. Adding that row to the round-63 list, without the head re-derivation, moves `selfdesc` 8→10: `province` 1→3 (the new row cites `tools/kama-completion-live.py` and `tools/round63-c1-counter.py`, neither in PROVINCE at tip); `retired` and `saturation` wording is stale for 13 capabilities and the new first-working round 63. C2's bound population (12/12), sensitivity (12/12) and controls (12/12) are unchanged. The `canonical=63` check still passes, and the 40-line window in `canonical_rows` still reads all 13 rows (R for the window's limit).

**P5 — C1's PROVINCE.md note moves the reconciler's r41 Axes hash (V, §5 sim-2).** The Axes coverage row pins PROVINCE's sha256 and line count. Committing the lane's worktree PROVINCE.md changes the sha (`a60591b7…`→`5e8ec39c…`) and the line count (188→190). The reconciler's r41 count goes 1→3. The same edit clears one `province` mismatch (the note names `registry/ollama-live-claims-r61.tsv`, which the tip's PROVINCE lacks): `province` 1→0. Net `selfdesc` 8→9. The re-anchor has to be the final PROVINCE bytes; re-anchoring first and editing again invalidates it.

**P6 — SOURCES census into the reconciler (V, §5 sim-2 `caps=1` unchanged).** The census check fires only on counts stated in the Capabilities section. That section states none, so S527/S528 add no mismatch. A later edit that states counts there would couple C1's SOURCES rows to C2's `caps` check.

**P7 — digest/hex scanners into C2's bound rows (V).** Both scanners read `.md` and `.tsv` only, outside `.ufo/`; `.py` files are excluded (`digest-ledger.py` lines 80–81 and 247–257; `hexrun-census.py` lines 96–99). So C1's tool edits (which contain 64-hex literals) cannot change `digest-ledger` or `hexrun-census`. The lane's C1 doc change is in scope of the scanners. In sim-2 (lane docs landed as-is) both scanners stayed `unknown=0`, and C2's bound rows all stayed `true`/sensitive.

**P8 — procedural gate (R).** C1's landing and C2's reconciler are coupled only through the L1's decision to add the row and re-derive the head. If C1 fails and the row is not added, the reconciler is untouched by C1. If C1 verifies and the row is added without the head work, the reconciler moves (P4).

**P9 — stale work trees (V for C2, R for C1).** `checkout_tip` returns `work/tip` whenever it exists, without checking the revision. Demonstrated: with `work/c2-tip` already holding the 03a6 tree, `checkout_tip(TB)` returned that tree; it still carried `kama-completion-live.py` v2 (`SCHEMA = 'kama-completion-live/v2'`) and `registry/capability-claims-r63.tsv`, which `TB` does not have (`git cat-file -e` reports absent). So a reused `--work` across tips silently scores the wrong tree in C2. C1 has the same shape (R): tool and dependency are overwritten each run, but the registry copy is written only `if reg:`, so a stale copy survives a tip that lacks it. Freeze's `--work <scratch>` is safe only with a fresh directory per tip.

**P10 — environment asymmetry (R).** C1's witness `subprocess.Popen` (line 381) passes no `env`, so the completion tool inherits the host environment including `TMPDIR`. C2 builds its child environment from `ENV_KEYS` (`PATH HOME LANG LC_ALL`, line 42) and forces `TMPDIR` to its scratch dir (line 505). The llama-server child is restricted by `CHILD_ENV_KEYS` in both paths. This does not change either counter's observables here, but it is not symmetric hermeticity.

**P11 — concurrent bind-0 port picks (R).** Both live paths choose ports by `bind(127.0.0.1:0)` then release (`pick_port`, documented race). Two concurrent live runs can offer the same port. Expected failure mode is closed (listener ownership and pid checks), but I did not provoke it.

## 5. Simulations (scratch only; each committed in my clone on top of the tip)

| scenario | commit | reconciler line (selfdesc) | r41 | banner | planned | retired | saturation | caps | province | C2 bound rows | C2 selfdesc |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base 7ee8cbdf | — | 8 (maxN 62) | 1 | 1 | 2 | 1 | 1 | 1 | 1 | — | 8 |
| tip 03a6a1d8 | — | 8 (maxN 63) | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 12/12 sensitive 12/12 | 8 |
| sim-2: lane worktree C1 docs landed as-is | `ed874656…` | 9 | 3 | 1 | 2 | 1 | 1 | 1 | 0 | 12/12 sensitive 12/12 | 9 |
| sim-1: C1 verifies; row added to round-63 canonical list, head untouched | `52f5eec2…` | 10 | 1 | 1 | 2 | 1 | 1 | 1 | 3 | 12/12 sensitive 12/12 | 10 |

Sim-1 detail lines (verbatim, from `selfdesc-sim1.out`): `retired: does not state '13 capabilities'`; `saturation: does not state 'first-working rounds … 61, 63'`; `province: PROVINCE.md lacks tools/kama-completion-live.py (capability live-completion-request-plane)`; `province: PROVINCE.md lacks tools/round63-c1-counter.py (…)`; `province: PROVINCE.md lacks registry/ollama-live-claims-r61.tsv (capability live-ollama-lifecycle)`.

C2 one-liners for the simulations (verbatim): sim-2 `… canonical=63 selfdesc_mismatches=9 …  controls_rejected=12/12 errors=0 met=False`; sim-1 `… canonical=63 selfdesc_mismatches=10 … controls_rejected=12/12 errors=0 met=False`.

## 6. The eight tip mismatches, mapped to what must change before selfdesc=0

Read from `selfdesc-tip.out` (identical categories at base; only the round label differs):

1. `r41 coverage`: the Axes coverage run counts 38 `corpus/knowledge/*.md` files (excl. engine-sides/processes); the row states 36. Pre-existing at base. Axes count re-derivation.
2. `banner`: head lacks `Latest measured round: 63`.
3. `planned`: no `### Planned (round 64)` heading followed by a numbered item (base: round 63). The freeze's Planned (round 64) work.
4. `retired`: does not state `12 capabilities` (pre-existing wording).
5. `saturation`: does not state `first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61` (the list in head text ends at 47; pre-existing).
6. `caps`: head Capabilities mirror has 11 names and lacks `live-ollama-lifecycle`, which the canonical list has (pre-existing).
7. `province`: PROVINCE.md lacks `registry/ollama-live-claims-r61.tsv` (pre-existing; the lane worktree note clears it, see P5).

Item 7 is the only one the lane worktree already fixes, and fixing it moves item 1 (P5). The L1's post-measure re-derivation has to take all of 1–7 together at the final PROVINCE bytes.

## 7. Items for the L1 (operability and calibration, not verdicts)

- Commit the PROVINCE note and the Axes re-anchor in the same final tip, then recompute the PROVINCE sha and line count, and rerun the reconciler and both counters at that final tip. The sha must be the final bytes.
- If C1 verifies and the row is added, change the head in the same commit: the Capabilities mirror (13 names), `retired` (13), `saturation` (first-working list with 63), and the PROVINCE tokens for the row's evidence cell.
- Freeze text vs tree: the freeze's "S527/S528 cited by C1's new checks" is not true at tip (zero S52x citations in `kama-completion-live.py`, `round63-c1-counter.py` or `round63-c2-counter.py`). Either cite them in the tool or correct the freeze text; I have not changed either.
- Give each counter run its own `--work` per tip (P9). Consider keying `checkout_tip` by revision.
- Decide what the context-capacity row proves on a host with operator llama-servers up (P3). Its `true` outcome is not reachable there.
- Clear the stray untracked `kama-shokunin/.ufo/` in the lane root (lane-owner action; not touched by me).

## 8. Bounds and tools

- Tools installed: none. No pacman, no `~/.local/bin` writes. Tools used: `git` (read-only on the lane; clone, commit and checkout only in my scratch clone), `python3`, the counters, the reconciler, the lane's live tools via the counters.
- Live runs: C1 and C2 counters launched llama-server children on unregistered loopback ports. No registered consumer port was contacted. Operator servers (ports 1234, 45669) and sibling pid 3262613 were observed, not signalled. No child from my runs survived (checked via `/proc`).
- No lane file edited. No commit, push, or mutating git against the lane. Receipts copied to `.ufo/waves/round-63/w1/out/CN02CrossClaim/` (outputs, two C1 receipts, context-capacity cc.json, the four scratch SHAs). Scratch removed.

## 9. Counter one-liners (for the L1 record)

C2 at TA (tip minus C1 tool change; `7f212098…`), exit 1:
`population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False`

C1 at TB (tip minus C2 registry; `1671a9c4…`), exit 0:
`tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]`
