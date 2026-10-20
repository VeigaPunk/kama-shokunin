VERDICT: partial — I attacked the unstated handoff premise behind C2: that the live harness's
transient `llama-server`/loopback-listener footprint can be handed to mori for corroboration, and
that `controls.txt`'s post-run zeros are a host-state claim. The premise is half wrong. mori has no
process or port surface and must not be asked to attest absence; the defensible handoff is a
window-scoped **self**-footprint block inside kama's own report, plus an explicit statement that
host-wide residue has no owner. No present-tense host negative is supportable by this wave's evidence.

## Axes this touches

| Axis | Effect | Why |
|---|---|---|
| **adjacency** (primary) | improved | Routes the evidence to its actual owner (none) instead of inventing a mori input; names the unowned residue gap without absorbing it. |
| **operability** (secondary) | improved | Makes the C2 teardown claim re-derivable from named receipt fields rather than asserted in prose. |
| depth / coverage / freshness / calibration | unchanged | No new lane artifact, no receipt-schema change, no new command in the capability row. |

## What I ran (read-only; no server started, no port bound)

| # | Command (abbrev.) | Exit |
|---|---|---|
| 1 | `read mori-shokunin/PROVINCE.md` | ok |
| 2 | `grep -rn "pgrep\|/proc/net\|ss -\|listener" mori-shokunin/tools/ SKILL.md PROVINCE.md` | 0 |
| 3 | `grep -n "/proc/" mori-shokunin/tools/mori-census.sh` | 0 |
| 4 | `sed -n '819,900p' mori-shokunin/tools/mori-census.sh` (wave settlement) | 0 |
| 5 | `grep -n "fleet_handoff\|pgid\|start_new_session\|preexec\|Popen\|killpg" tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json SKILL.md PROVINCE.md README.md` | 0 |
| 6 | `sed -n '286,340p;420,470p;572,626p;780,860p;915,985p' tools/kama-llamacpp-live.py` | 0 |
| 7 | `sed -n '200,235p;355,372p;482,500p' tests/llamacpp-live/check-receipt.py` | 0 |
| 8 | `python3 -c` enumerate `live/receipt.json` fields/window/transitions | 0 |
| 9 | `cat live/controls.txt`; `stat -c '%y %s %n' live/controls.txt` | 0 |
| 10 | `pgrep -x llama-server`; `pgrep -af llama-server` | **1 (empty)** |
| 11 | passive `ss -ltnH \| grep -E ':(8080\|34113)([[:space:]]\|$)'` | 0 (one match, below) |
| 12 | `ss -ltnpH 'sport = :34113'`; full `ss -ltnpH` | 0 (no 34113 at that instant) |
| 13 | 6 samples @0.7 s + 120 polls @0.1 s of the 8080/34113 table (13:55:02Z→13:55:18Z) | 0, **0 listeners each** |
| 14 | `grep -rn "34113\|8080" tests/ tools/ registry/` | 0 |
| 15 | `cat /proc/sys/net/ipv4/ip_local_port_range` | 0 (`32768 60999`) |
| 16 | `git log -1 --format`; `git status --porcelain` | 0 (`b8e485c`) |

I did **not** run `.ufo/waves/round-16/measure.py`, did **not** start `llama-server`, and never
connected to 8080 or 34113.

## Evidence

### 1. mori cannot be the recipient: it has no process or listener surface

Mori's Core is named exhaustively at `mori-shokunin/PROVINCE.md:22-28`: watchdog pid/log,
`.ufo/waves` settlement, journal MESSAGE_ID classes, the same-boot journal window, disk/cgroup
runway, tmux relevance, lane silence. There is no `ss`, socket, port, `/proc/<pid>`, or process
inventory in that list. Its `Refuses:` line (`PROVINCE.md:12-16`) excludes “OS package, systemd
unit, driver/firmware and boot state (→ tsukuroi)” and “endpoint and model-serving health (→ kama)”,
and closes with “Detection and report only — never remediation.”

The census source corroborates mechanism: its only process probe is
`cap "$PGREP_BIN" -af shokunin-watchdog` (`tools/mori-census.sh:669`), and its only `/proc` reads
are `diskstats`, `uptime`, `meminfo`, `boot_id` (`mori-census.sh:298-300,328`). A `llama-server`
argv cannot match that pgrep filter. The `waves` surface explicitly skips round directories:
`case "$base" in round-*|.*) continue ;;` (`mori-census.sh:837`), so `.ufo/waves/round-16/live/`
is invisible to it.

Mori's own boundary is decisive: “an unavailable pid probe is not absence”
(`PROVINCE.md:48`, FR5) and “mori does not infer serving health from host/resource signals”
(`PROVINCE.md:67`). Asking it to confirm “no harness process remains” would force exactly the
unbounded absence claim it refuses to make. **Do not send the footprint to mori.**

### 2. The only defensible claims are already in the receipt — and are narrower than the prose

Receipt `live/receipt.json` (`kama-llamacpp-live/v1`, run window
`2026-10-20T13:49:38.040Z → 13:49:38.170Z`, **130 ms**) carries:

- `port: 32845`, `port_refusal_set: [8080, 34113]`;
- `port_listener_ownership: "child"` — pre-teardown, the LISTEN inode on that port was an fd of the
  child (`port_owned_by`, `tools/kama-llamacpp-live.py:420-435`); the gate rejects `"foreign"`
  (`tests/llamacpp-live/check-receipt.py:362-367`);
- `teardown: {returncode: 0, sigterm_sent: true, sigkill_sent: false, port_refuses: true,
  term_wait_ms: 3}` (`tools/kama-llamacpp-live.py:572-626`; gate requires `port_refuses is True`,
  `check-receipt.py:667-672`);
- `pdeathsig: {requested: true, prctl_ok: true}` — direct child only (`tools/…:296-311`,
  `start_new_session=True` at `:817`);
- `child_env_keys` (names only, no values) and `model_sha256_post` (model unchanged).

What it does **not** contain: any pid or pgid, and any post-teardown process-group check. `killpg`
is used (`:581,:590`) and `start_new_session=True` makes pgid == child pid, but the pid is never
recorded, so no report can name the object it signalled or re-check that group. `port_refuses` is a
single instant check on **its own port**, not a process claim. The build-wave advice recommended a
`fleet_handoff` receipt field; grep shows **no** `fleet_handoff` and no `pgid` anywhere in the
harness, gate, SKILL, PROVINCE or README — the recommendation landed as advice only.

### 3. `controls.txt` is a wave-level token, not a host-state datum

`live/controls.txt` records outcomes with no command lines and no per-line timestamps:
`post_pgrep_llama_server=0` and `post_ss_8080_34113=0`. Its header `## live runs
2026-10-20T13:49:37Z` *precedes* the first live receipt (`13:49:38.040Z`), and its mtime is
`2026-10-20 10:50:49 -0300` (= 13:50:49Z, the lane commit time). So the file cannot date its own
post-run checks, and it does not record what `post_pgrep…` ran. [INFERENCE] It is a hand-run
wave-level transcript, not a receipt field and not gate-checked.

### 4. Host check: a registered-port negative is not durable — observed falsified during this wave

A single passive socket-table read during falsify returned
`LISTEN 0 5 127.0.0.1:34113 0.0.0.0:*` — a live listener on the hard-pinned consumer port that
`controls.txt` records as unserved. It did **not** reproduce: `ss -ltnpH 'sport = :34113'` was
empty, 6 samples across 13:55:02.7–13:55:05.6Z read 0, and 120 polls at 0.1 s found no further hit.

Attribution: **not** kama's harness. `pick_port` refuses a registered port before any bind
(`tools/kama-llamacpp-live.py:237-238`); the default path binds `('127.0.0.1', 0)`, whose range is
`32768 60999`, so 34113 cannot be offered; and no lane test binds it — `grep -rn "34113\|8080"`
under `tests/ tools/ registry/` hits only pins, a refusal set, and one gate mutation
(`check-receipt.py:909`). [INFERENCE] A concurrent actor (plausibly a sibling falsify seat's
control, given 16 ephemeral `python3` listeners plus 8 fixed shim ports were alive at the same
instant) bound it.

The conclusion does not depend on attribution: **the socket table flips within seconds under
concurrent work, so “nothing listens on 8080/34113” is not a fact kama can publish in the present
tense.** A report that restates it will be false at some reader's instant, as it was at mine.

### 5. Second-order effects of the handoff are nil for mori, non-nil for the report

- `round-*` skip (`mori-census.sh:837`) means the new `live/`, `build/`, `falsify/` subtrees change
  no `SURFACE waves` row.
- The only mori-visible artifact is the committed report itself, graded by lane silence
  (`mori-census.sh:2092-2094`: “report present at HEAD AND newest commit touching it in (launch,
  NOW]”). The footprint block is for L1/operator reading, **not** a mori input.
- cgroup `memory.events`/`memory.peak`/PSI are cumulative or high-watermark
  (`PROVINCE.md:26`); a snapshot after the run cannot date or attribute the harness's ~1.2 MB model
  load. Do not cite them as teardown evidence.
- A later journal correlation needs a `mori-journal-anchor-v1` cursor (`PROVINCE.md:25`); the
  receipt's UTC window is not one. Any join is a manual operator query, not an automatic handoff.

## Proposed move

Put exactly one block in the round report, copied verbatim from the receipt, and keep it there.
Nothing goes to mori; no receipt-schema change; no re-run.

```md
### Transient footprint (harness-owned; not a fleet surface)
- run window: `2026-10-20T13:49:38.040Z` → `2026-10-20T13:49:38.170Z` (130 ms; receipt
  `started_utc`/`ended_utc`, `schema: kama-llamacpp-live/v1`)
- listener: `127.0.0.1:32845`, unregistered ephemeral, `port_refusal_set: [8080, 34113]`
- pre-teardown ownership: `port_listener_ownership: child` (LISTEN inode was a child fd; the
  receipt gate rejects `foreign`)
- teardown: `returncode: 0`, `sigterm_sent: true`, `sigkill_sent: false`, `term_wait_ms: 3`,
  `port_refuses: true` at the port check that follows the child wait
- parent-death mitigation: `pdeathsig.prctl_ok: true` (direct child only)
- scope: own child process group and own port, at the instants recorded. This is **not** a
  host-wide absence claim, **not** a registered-port negative, and **not** fleet or host health.
- residue gap (no owner): no census surface inventories host-wide processes or listeners.
  mori has no process/port probe (`../mori-shokunin/PROVINCE.md:22-28`,
  `mori-census.sh:669,298-328`); tsukuroi owns units/boot, not bare children; souji owns
  artifacts, not processes (`PROVINCE.md:69`). Reported, not absorbed.
```

And four prohibitions for the report prose:

1. **Do not** write “nothing listens on 8080/34113” or “no llama-server remains” as present-tense
   host facts. If `controls.txt` is cited, cite the token and its provenance: “wave-level hand check
   recorded `post_pgrep_llama_server=0` / `post_ss_8080_34113=0`; the command lines and check times
   are not retained.”
2. **Do not** claim a pgid or process-group emptiness: neither is recorded; `port_refuses` proves
   the port, not the group.
3. **Do not** ask mori to corroborate. It cannot, and its `unavailable` means “could not observe”,
   never “not present” (`PROVINCE.md:48`).
4. Keep the vocabularies apart: mori `unavailable` ≠ llama.cpp `unavailable_error` ≠
   `loading_observed: false` (not observed in this run, not “never”).

If L1 later wants a group-empty proof, it is a **new** capability change, not this wave's: record
`pid`/`pgid` in the receipt, add a post-teardown group check, extend the gate, and accept that the
claim remains own-group-scoped with a pid-reuse caveat. Not justified now: the reaped child
(`returncode: 0` after TERM) plus own-port refusal already bounds every claim the report needs.

## Risks of this move

- **Block drift.** Duplicating receipt values can go stale if the receipt is regenerated. Mitigate
  by naming the source path/schema in the block and treating it as a quotation.
- **Vocabulary mismatch at the boundary.** The gate accepts `port_listener_ownership` in
  `child|foreign|unknown` (`check-receipt.py:362`), while the harness maps `None` to `unproven`
  (`tools/…:850`). A successful receipt can only be `child`, so the block must quote `child` and
  never introduce `unproven`/`unknown`. (Adjacent defect, better routed to `ReviewReceiptGateCode`.)
- **Over-reading the window.** 130 ms is shorter than any census cadence; external sampling cannot
  corroborate it even if a surface existed. Say “at the instants recorded”, not “during the wave”.
- **Falsification by a later run.** Any post-publication `pgrep`/`ss` check can see a concurrent
  falsify re-run rather than residue; a restated host negative would then fail against an innocent
  cause. The window+port scope prevents that misread.
- **Prose creep into a capability row.** The SKILL cell already says “one child process on
  127.0.0.1, torn down” (`SKILL.md:532`). That is correct and sufficient; do not upgrade it to a
  host statement.

## Limitations

- I read mori's `PROVINCE.md` as instructed and read `tools/mori-census.sh` only to corroborate
  mechanism; I did not run the mori census (sibling lane, and my item is read-and-advise).
- The 34113 listener's owning pid was never sampled, so the observation is a positive listener
  sighting with no attribution; the advice does not rely on who bound it.
- I did not re-run the live harness, so no second receipt exists to compare windows; the 130 ms
  window and teardown values are read from the committed `live/receipt.json`.
- `[INFERENCE]` markers above are the only unobserved links (seat attribution of the 34113
  listener; `controls.txt` provenance).

## Installs

None. No package, tool, or binary was installed or upgraded.
