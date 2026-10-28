# CN02SiblingOverlap — sibling overlap scan (round 64, kama, wave b)

Seat: CN02SiblingOverlap (leaf; no subagents). Item: connector sibling-overlap scan, judged on operability.
Mode: read-only. No commit, no edit outside this report and `out/CN02SiblingOverlap/`, no scratch clone, no live run, no installs. Tool/version/channel record: none installed.
Evidence: `out/CN02SiblingOverlap/grep-receipt.txt` (the exact grep commands and their output, 297 lines), `out/CN02SiblingOverlap/hits.tsv` (25 classified rows).

## 1. Scope and method

- Lanes scanned: every `*-shokunin/tools/` and `*-shokunin/corpus/knowledge/` tree except `kama-shokunin` (kama's own hits are in-lane, section 5).
- Pattern 1 (`grep -rIl '/proc/'`): 105 non-kama files across 13 lanes.
- Pattern 2 (binding-shaped: `/proc/<x>/{exe,fd,net,maps,environ,cmdline,stat,mem,cwd}`, `/proc/net`, `pidfd`, `starttime`, `/proc/self/fd`, `/proc/$$/fd`): 52 files by regex. Most are prose or host-metric reads (`/proc/meminfo`, `/proc/pressure`, `/proc/diskstats`, `/proc/self/mounts`). I read every candidate that could bind a pid or socket to an identity and classified it by hand.
- Pattern 3 (`ss -ltn/-ltnp/-xpa`, `lsof`, `fuser`, `SO_PEERCRED`, "served endpoint", "pinned server/binary/digest"): used to find non-procfs socket-to-pid routes.
- Excluded: `.ufo/waves/*` strace logs, fixtures and receipts (other lanes' evidence, not tools or knowledge). Their hit counts are inflated (e.g. tabi round-25 strace logs, tsukuroi round-51 fixtures); none is a tool a sibling would reuse.

Kama's own surface for comparison, from reading: `tools/kama-llamacpp-live.py` (`_listen_inodes` :628, `_proc_listener_inode` :599, `_tcp6_is_loopback` :580, `port_owned_by` :650, exe/maps/fd reads :682-786), `tools/kama-completion-live.py` (`_proc_holders` :190), `tools/kama-probe.sh` (`ss -ltn` listeners), `tools/round64-c1-counter.py` (`listeners` :238, `holder_pids` :258, `stat_fields` :289, `read_maps` :311, `holder_record` :339, `pid_gone` :843). Kama's cross-lane scope (`corpus/knowledge/cross-lane-scope.md` row 17, `PROVINCE.md` "Owns") assigns process/port/served-model identity to kama.

## 2. Headline

1. **No sibling ships a pinned-binary verifier for a served process.** The nearest things are: tabi's round-39 egress driver (procfs fd-inode join, same primitive, different purpose), tabi's `/proc/<pid>/exe` launcher-vs-engine check (concept only, precedent), and tsukuroi's `census-identity` (hash the running script through `/proc/$$/fd/<n>`, a different target). Kama's exe re-hash + listener-holder + argv/maps/environ-key binding is not duplicated elsewhere in the fleet.
2. **Two sibling notes contest kama's province and must be reported, not absorbed:** kengaku's `served-endpoint-identity-pin` (its "owning process" row reads `/proc/<pid>/cmdline`) and kumitate's `enqueue-admission` (`lockPidOwnsQueue` treats a cmdline substring as process identity, and counts an empty cmdline as owner). Both sit against the identity rules mori recorded (`watchdog-identity-r31`, `pid-probe-conclusion-r44`).
3. **Reusable control ideas exist** and are the main value of this scan: tameshi's pidfd + starttime + subreaper signal discipline, tabi's endian fixture for `/proc/net/tcp` decoding, tabi's environ-is-exec-time-only caveat, mori's identity rules (comm truncation, empty cmdline is not absence, `(pid, starttime)` is the only identity), tsukuroi's fd-provenance (`O_CLOEXEC` in `fdinfo`), and tabi's `ss` versus `/proc` two-channel agreement.
4. **Host facts seen by the scan** (fixture facts for kama's controls, not kama findings): at 2026-10-28 kengaku's receipt records a foreign llama-server (pid 242776, LFM3-1.7B, `127.0.0.1:45669`) and a router on `127.0.0.1:1234`; game-dev-3d recorded a sibling seat's transient capture server on `:8000`. Kama's listener-holder rule must keep rejecting holders that are not the pinned server, and a single listener sample flakes.

## 3. Hit table (decision per hit; full rows in `hits.tsv`)

Decision vocabulary: DUPLICATE = same primitive, same job (or a sibling already does what kama built); REUSABLE = method to cite or adopt, not absorb; CONTESTED = conflicts with kama's province or identity rules, report to owner; OUT = not kama's province; NOISE = not a binding use.

### 3a. Duplicates (primitive or job overlaps kama's round-64 build) — 6 rows

| # | Lane / path | Procfs or socket use | Decision | Note |
|---|---|---|---|---|
| D1 | tabi `corpus/knowledge/playwright-firefox-session-bound-tcp-round-39.md` + `scripts/playwright-firefox-egress-round39.mjs` (round-41 variant also present) | socket inodes from `/proc/<pid>/fd` joined to `/proc/net/tcp{,6}` for an owned pid tree | DUPLICATE (primitive), different job | Same join as kama's `listener_holders`. Tabi measures browser egress over loopback, kama measures serving identity. Cite; do not merge. |
| D2 | tabi `corpus/knowledge/webmcp-chromium-loopback-round-16.md:35`, `webmcp-invocation-round-17.md` | `/proc/<pid>/exe` to tell a launcher shell from the engine image (`/usr/bin/chromium` is a 14 KB launcher that execs `/usr/lib/chromium/chromium`) | DUPLICATE (concept), precedent | Kama's exe re-hash already rejects a wrapper, because the wrapper's digest is not the pinned digest. Cite the launcher case as a fixture idea (wrapper script as `exe`). |
| D3 | mado `tools/mado-eventq.py` | `ss -xpa` `users:((comm,pid,fd))` maps unix sockets to pids (Hyprland socket2 subscribers) | DUPLICATE (technique), OUT (compositor) | Route is `ss -p` (netlink plus `/proc/<pid>/fd`), a second channel. Kama already has `ss -ltn` in `tools/kama-probe.sh listeners`. |
| D4 | souji `tools/souji-proc-census.sh`, `tools/souji-census.sh:1547,1587,1989-1998` | `/proc/<pid>/stat` starttime and ppid, `fd/1` readlink, `(deleted)` scratch retention | DUPLICATE (partial: `(deleted)` link reading), OUT (repo/process residue) | Kama's "(deleted) means no on-disk file ran" check overlaps. Report to souji; keep kama's own check. |
| D5 | tsukuroi `tools/probe-child-env-allowlist-r33..r37.py`; tabi `environment-injection-measurement-integrity-round-41.md` | `/proc/self/environ` and `/proc/<ppid>/environ` to detect injected names in traced execs | DUPLICATE (partial: canary-in-environ, kama round-50/56), OUT (child-env allowlist is tsukuroi/kumitate) | Kama's `KAMA_R50_CANARY` check already does the canary half. |
| D6 | game-dev-3d `corpus/knowledge/unreal-mcp/executability/*.md` (`ss -ltnp` on :8000-8009) | port-listener presence by `ss` | DUPLICATE (port-listener presence), OUT (Unreal) | `gameplay-gas.md:177` records one `ss` sample showing 127.0.0.1:8000 LISTEN with curl exit 0. Five re-samples minutes later showed no listener and curl exit 7. The listener was a sibling seat's short-lived capture server, not Unreal. A single listener sample is not evidence; kama's controls must repeat samples and keep the flake as data. |

### 3b. Reusable control ideas (adopt the method, cite the owner) — 8 rows

| # | Lane / path | Idea | Owner | Use for kama |
|---|---|---|---|---|
| R1 | tameshi `tools/registry-check.py` (header :30-40; `_row_identity_is_owned` :468; `_signal_process_identity` :503-524; subreaper and pidfd gate :392-399) | Mark the runner a subreaper; signal only through `pidfd_open`, recheck `(pid, starttime)` and ancestry immediately before signalling. Residual, documented by tameshi: same-tick PID reuse. | tameshi (verification-fixture method) | Kama's counter does not signal a pid in its measured path. Its `pid_gone` compares ticks only (round64 counter :843-855). If kama's teardown ever signals the server by pid, use a pidfd instead. |
| R2 | tabi `corpus/knowledge/playwright-firefox-session-bound-tcp-round-39.md:16`; `corpus/evidence/round-39/measure/proc-endian-raw-row.txt` | The first `/proc/net/tcp` parser tested a `7F` prefix on displayed hex. It counted 12 false non-loopback rows; the raw row `0100007F:8AEF` shows the bytes are little-endian. | tabi | Kama's `_proc_listener_inode` is correct on re-read: IPv4 checks the last two hex digits are `7F`, and tcp6 reverses each 32-bit word (`_tcp6_is_loopback` :580-594). Add the raw row as a fixture for both `/proc/net/tcp` and `tcp6`. |
| R3 | tabi `environment-injection-measurement-integrity-round-41.md:25-30,52,68`; `mori-silence-cases.sh:240` | `/proc/<pid>/environ` is the exec-time environment only. A runtime `unset` or in-process setenv does not change it. | tabi, mori | Kama's environ checks (`environ_keys`, round64 counter :354-359) record initial names only. A preload verdict must rest on `/proc/<pid>/maps`, not on environ. Keep the caveat in kama's receipt text. |
| R4 | tsukuroi `corpus/knowledge/census-identity-r46.md:28-40`; `tools/tsukuroi-census.sh --identity` | Hash a running script through `/proc/$$/fd/<n>`; require `O_CLOEXEC` in `/proc/$$/fdinfo/<n>` and exactly one qualifying fd, else print `unverifiable`. | tsukuroi (host census) | Descriptor provenance. It does not on its own kill MT15 forge A (a canned answerer behind the real child's inherited listener fd), because the listener is genuinely the child's. What kills forge A is kama's exe digest and maps check. Adopt the fdinfo idea only for the exe fd, if at all. |
| R5 | mori `corpus/knowledge/watchdog-identity-r31.md:24-31`; `pid-probe-conclusion-r44.md` | Identity rules: `comm` is truncated to 15 bytes and rewritten by a `#!` shebang (`bash`), so it is never identity. An empty `cmdline` is a zombie or an mm-less kernel thread, not absence (`maps` empty). `ENOENT` is absence. `(pid, starttime)` within one boot is the only identity over time. | mori (fleet observability) | Kama must not identify the server by `comm` or `pgrep`; I found no `pgrep` in the round-64 counter. An empty `cmdline` or `maps` must fail closed, not pass as "no argv". Confirm in the C1 falsifier set. |
| R6 | tsukuroi `corpus/knowledge/kill-event-deep-r8.md:213-216` | Process start time to the second from `/proc/<pid>/stat` starttime ticks plus `/proc/uptime`, self-validated against the journal. | tsukuroi | Optional for kama's identity receipts (`starttime_ticks` is already captured). |
| R7 | kumitate `corpus/knowledge/agent-isolation-substrates.md:113-131,164,246`; `mount-order-and-bind-scope.md:11` | `/proc/1/environ` shows the bwrap exec environment, not `--setenv` values; `/proc/self/mountinfo` is the mount truth in the child namespace. | kumitate (child isolation) | Relevant only if kama's serving runs sandboxed. Kumitate already owns the runner (cross-lane-scope row). |
| R8 | chousa `tools/research-gate.sh:507` (`sha256_pin_bin`), `:3300-3312`, `:3532-3540`, `:3988-3992`; `corpus/knowledge/claim-pin-provenance-r37.md` | Absolute `sha256sum` path, never `PATH`; registry re-open through `/proc/$$/fd/N` with a denylist check on the resolved path. | chousa (claims gate) | Kama's counter hashes in Python (`sha256_path`, :166) and resolves no binary through `PATH`. No action beyond citation. |

### 3c. Contested (kama's province or identity rule, report to owner) — 2 rows

| # | Lane / path | Conflict | Where it must be reported |
|---|---|---|---|
| C1 | kengaku `corpus/knowledge/served-endpoint-identity-pin.md` (rows "owning process", decision rule 3, measured pin table) | Kengaku builds its own served-endpoint pin from tokenised `/proc/<pid>/cmdline`, the same identity fact kama's C1 binds. Kengaku's rule 3 defers flag authority to kama, so the overlap is in the record, not in the claim. The measured pin lists a foreign server (pid 242776, `:45669`) and router `:1234` at 2026-10-28. | Report to kengaku: cite kama's binding output rather than carry its own argv read, and keep kengaku's evaluation fields. Note in kama's cross-lane scope. Not absorbed. |
| C2 | kumitate `corpus/knowledge/enqueue-admission.md:26-33` (`lockPidOwnsQueue`, L5813-5822) | A live pid whose `/proc/<pid>/cmdline` lacks `fleet-dispatcher.mjs` is treated as abandoned; an empty `cmdline` counts as owner. This is a cmdline-substring identity rule, the pattern mori's FR5 says is not identity. The empty-counts-as-owner arm is conservative toward ownership, but still substring-based. | Report to kumitate (queue owner) and mori (identity rule). Kama is not involved in the queue. |

### 3d. Out of province or noise, no action for kama — 4 rows

| # | Lane / path | Use | Note |
|---|---|---|---|
| O1 | kagi `corpus/knowledge/control-plane-hardening.md:128` | A secret read from `/proc/<pid>/environ` in a repro | Credential hygiene is kagi's. Kama's constraint: environ reads record key names only, never values. Kama's counter already does (`environ_keys`, round64 counter :354-355). |
| O2 | tsukuroi `tools/tsukuroi-census.sh` (:365,413,437,494), `check-fd-band-r49.py`, `score-selftest-tmpdir-r48.py` | `/proc/self/mounts`, `/proc/self/fd` TMPDIR alias for selftests | Host substrate and selftest plumbing, not binding. |
| O3 | mori `tools/mori-census.sh`, `mori-pressure.py`, `mori-disk-rate.py`, `mori-commit-runway.py`; knowledge notes on `/proc/pressure`, `/proc/diskstats`, `/proc/meminfo`, `/proc/vmstat` | Host metrics | Not binding. |
| O4 | kaidoku `tools/round-40/mk-l-carriers.py:47` (`/proc/mounts` string in a re-rooting map), `corpus/knowledge/*` and round-44/49 fixture JSON with `/proc/` strings; kumitate `native-judge-pipeline.md:13` (refuse `/proc/self/fd/0` as stdin-shaped input); kasegi `corpus/knowledge/source-tree-loss-2026-09-28.md:36` (`grep ... /proc/mounts` in an incident note) | String mapping, input refusal, incident-note command | Noise for this scan. |

## 4. Where to report (contested scope)

- kengaku (C1): cite kama's binding for the served-endpoint identity; kengaku keeps its battery and pin fields.
- kumitate and mori (C2): the queue lock's cmdline-substring identity conflicts with mori's FR5 rule; kumitate owns the fix.
- tameshi (R1), tabi (R2, R3), tsukuroi (R4, R6), mori (R5), kumitate (R7), chousa (R8): cite the method; do not copy code into kama's tools without a kama-owned test.
- mado (D3), souji (D4), tsukuroi (D5), game-dev-3d (D6), tabi (D1, D2): duplicates in primitive only; these lanes own their jobs.
- The L1 integrates nothing from this scan. Nothing here is an edit to a sibling lane.

## 5. In-lane notes (kama, not sibling overlap; not scored by this item)

- Kama's own procfs surface is already large: 18 kama files under `tools/` and `corpus/knowledge` contain `/proc/`; the round-49..56 replay audits (`round49-replay-witness-audit.py` through `round56-replay-code-audit.py`) repeat the same listener/fd/maps/environ/exe reader. The round-64 counter is a further copy, not a shared helper. The L1 should decide whether the C2 instrument reuses one reader or keeps its own. Nothing here is a sibling duplicate.
- `round64-c1-counter.py` `stat_fields` (:289-297) returns `(None, None)` on any `OSError`/`ValueError`, and `pid_gone` (:843-855) reads `None` as "gone". An unreadable `/proc/<pid>/stat` (for example a hidepid mount or a permission change) therefore reports teardown as observed. This is a fail-open in the teardown observation. It is benign for same-uid processes, which is what the counter runs, but the rule should be fail-closed: distinguish ENOENT (gone) from other errors (unknown). Route to the L1; not my edit.
- Round-64 counter defines `free_port` twice (:739 and :956), but the second copy sits inside the fake-server template string, so it is not a live shadow. Checked; not a defect.
- Kama's IPv4 loopback test (`addr_hex[-2:] == '7F'`, `kama-llamacpp-live.py` :613-616) and tcp6 per-word reversal match tabi's measured fixture (R2). Recommend adding `0100007F:8AEF` as a fixture row in both kama parsers.

## 6. Verification performed

- All greps ran from `/home/vgpnk/Projects/shokunin` against `*-shokunin/tools` and `*-shokunin/corpus/knowledge`; output is in `out/CN02SiblingOverlap/grep-receipt.txt`.
- Lanes with hits (13): chousa 4, game-dev-3d 2, kagi 1, kaidoku 6, kasegi 1, kengaku 1, kumitate 5, mado 6, mori 25, souji 3, tabi 5, tameshi 3, tsukuroi 43 (file counts from the receipt; `.ufo` excluded).
- Each decision cites a file and line read in this seat: tabi round-39 knowledge (:11-20), webmcp round-16 (:35), environment round-41 (:25-68), kengaku served pin (full), kumitate enqueue-admission (:26-33), tameshi registry-check (:1-60, :392-605), tsukuroi census-identity-r46 (:1-40), kill-event-deep-r8 (:213-216), mori watchdog-identity-r31 (:24-31), pid-probe-conclusion-r44 (:19-40), chousa research-gate (:500-520, :3296-3312), chousa claim-pin-provenance-r37 (:1-14), game-dev gameplay-gas (:177), kasegi source-tree-loss (:36), kama cross-lane-scope (rows 9-17), kama llamacpp-live (:580-660), round64 counter (:289-297, :354-355, :739-745, :843-855, :956-958).
- Not run: no live probe, no tool execution, no counter run. The duplicate calls are primitive-level, not behavioural equivalence.

## 7. Tally

`CN02 sibling-overlap: lanes_with_hits=13 files_procfs=105 binding_shaped_by_regex=52 tsv_rows=25 table_rows=20 duplicate_rows=6 reusable_rows=8 contested_rows=2 out_of_province_rows=4 counter=none`
