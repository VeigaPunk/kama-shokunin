# F09C1PortRace — C1 port race (round 60, w2 falsification)

Seat: F09C1PortRace (advisory leaf, no lane edits). Axes: operability (judged), calibration (7, lowest assigned, not attacked here).
Attacked artifact/predicate: **C1-r60** / `tools/kama-ollama-live.py` @ freeze commit `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`; verifier `tools/round60-c1-counter.py`; committed receipt `.ufo/waves/round-60/live/receipt.json`.
W1 evidence attacked: `.ufo/waves/round-60/w1/out/A07ConcurrentRuns.md` — its TOCTOU probe left the port-race branch **untriggered** ("a loser of the port race would pass `ready` against a foreign server and then fail `listener-owned` … Not triggered here", w1 A07 report:73,79); A02BinarySwapRace raced the binary, never the port.

## Method (synchronized patched copy; no unrelated ports touched)

- Synchronized copies: `tools/kama-ollama-live.py`, `tools/kama-ollama-evidence.py`, `registry/ollama-live-pin.tsv` copied from the lane working tree into per-variant scratch trees. Byte-identity to the frozen tip proven before use: working-tree sha256 `9d1c688b…72aaf` (tool) and `175c2916…77d86` (counter) == `git cat-file blob e0b5b1ea…:{tools/kama-ollama-live.py, tools/round60-c1-counter.py}`.
- Injection (race trees only; unified diffs in `artifacts/{racea,raceb,racec}.patch`, `ctrl.patch` is empty): one guarded call `_f09_competitor_start(port)` between `port = free_port()` and the `port-unregistered` check; the helper spawns a competitor bound to that same port and returns only after the tool's own `listening_ports()` (/proc) view sees it — i.e. the port is occupied **before the child is ever spawned**, a deterministic worst case strictly earlier than the natural close→bind window.
- Competitors: **racea** bind-and-hold listener (accept/close, silent); **raceb** fake Ollama (`GET /` → 200 `Ollama is running`, `GET /api/version` → `{"version":"0.40.11"}`, all else 404) — maximal impersonation of the tool's identity-blind ready/version probes; **racec** = racea + `SO_REUSEPORT` (tests whether Ollama would co-listen). Baseline **ctrl** = pristine synchronized copy, no competitor.
- Environment: scratch `/fast/scratch/hyaku/kama-r60/F09C1PortRace`, `TMPDIR=$SCRATCH/tmp` explicit, removed after hand-off; disk-guard checked before heavy tests (`/fast` 589G free); live probe used the tool's own pinned Ollama v0.40.11 child (bin sha `b0a4becf…1b4c`, fixture sha `270cba1b…56d` verified before runs); every run's port asserted ∉ {8080, 34113, 11434}; competitors and trap killed **only recorded PIDs** (pidfiles), no process-name kill, no /tmp writes, no fixture git; no leftovers (`/proc/*/cwd` sweep clean).

## Results (exact; receipts + serve.logs in `artifacts/`)

| run | competitor | tool exit | verdict | elapsed | attacker-influenced true checks | counter `verify()` |
|---|---|---|---|---|---|---|
| ctrl | none | 0 | `MODEL_OK` | 1.42 s | — (16/16 honest) | `[]` (accepted) |
| racea | bind-hold | 1 | `FAIL` | 0.88 s | none (binary/model digest only) | 21 reasons, rejected |
| raceb | fake Ollama | 1 | `FAIL` | 0.68 s | `ready`, `version`, `running-exe-digest` | 18 reasons, rejected |
| racec | bind-hold + SO_REUSEPORT | 1 | `FAIL` | 0.84 s | none | 21 reasons, rejected |

All three race serve.logs end with the same line: `Error: listen tcp 127.0.0.1:<port>: bind: address already in use` — Ollama v0.40.11 does not retry, does not fall back to another port, and does not set `SO_REUSEPORT` (racec proved no co-listen). The counter additionally rejects every race receipt on `log-listening` (no `Listening on 127.0.0.1:<port> (version 0.40.11)` line exists) plus `verdict`, 12–14 `check:*`, `capture-parse`, `teardown`, `manifest`, `blob-missing` (`artifacts/verify.txt`).

## Findings

**Answer: fail-closed — no false-green.** In every triggered race the tool exited 1 with verdict `FAIL`, wrote an honestly-failing receipt, and the frozen counter's independent `verify()` rejected it. W1 A07's structural prediction is confirmed by execution, with one refinement below.

**F1 (MEDIUM, defect-shaped, bounded impact): three identity-adjacent checks are attacker-satisfiable during a lost port race.** In raceb the receipt records `ready=True` (impostor's exact body), `version=True` (impostor echoes the pin), and `running-exe-digest=True` — the last because that check hashes `/proc/<child>/exe` (tool :311–314) and pins the child *process*, not the *responder*; the bind-losing child was still alive at check time. So the graded receipt of an entangled run can contain three true checks whose semantics read as "the pinned server answered"; only `listener-owned` (inode↔child fd match, tool :107–133, :317) actually binds port↔child, plus `teardown.port_closed`. A07 named only `ready`; `version` and `running-exe-digest` are newly demonstrated attacker-true.

**F2 (LOW, accidental tripwire, window-dependent): `port-unregistered` detected every injected competitor** (evaluated False in all race runs) because its /proc snapshot runs after my synchronized injection — but in the *natural* race (competitor binds after that snapshot, before `Popen` :283) this tripwire does not fire and detection rests solely on `ready`/`listener-owned`/`teardown`. My injection is strictly earlier/stronger; the natural sub-millisecond window remains untested (W1 probed it empirically 0/80 at a 0.25 s gap).

**F3 (INFO, operability positive): race failure is fast, not a hang.** The ready loop exits on `proc.poll()` as soon as the bind-failed child dies; all race runs failed in ≤ 0.9 s against `READY_TIMEOUT = 90`. `port_closed` in `teardown` honestly read False while the competitor held the port (conflation of "child gone" with "port free" is inherent to that check but did not produce a wrong true here).

**F4 (LOW, pre-flagged by W1, unchanged): `free_port()` excludes only {8080, 34113}** (tool :64) — not 11434, the system Ollama default the host guard reserves; when no system Ollama is listening the tool may legitimately pick 11434 (observed free this session). Also per W1: the child env carries no `TMPDIR`, so Ollama may transiently write /tmp — observed configuration unchanged here (the synchronized copy must differ only in the race injection).

**F5 (bound of this attack):** a competitor that takes the port and *releases* it before the child's bind was not attempted — unreproducible timing; if the child then wins, the receipt legitimately describes the child and no false-green exists by construction. Partial-impersonation competitors (wrong version string) fail `version` earlier — irrelevant to F1.

## Residual risk and verification gaps

- The port race is **closed for MODEL_OK outcomes** under deterministic injection on this host/version; the open residual is the untested natural-window variant (F2) and any non-Linux /proc absence (tool degrades: `listening_ports()` swallows OSError — on a host without /proc/net/tcp the `port-unregistered` and `listener-owned` tripwires silently weaken; out of threat model here).
- `running-exe-digest`'s single-shot placement (already exploited by A02's stage-2) compounds with F1: it is a process check, never a port-identity check.
- Not attacked: IPv6-only competitors (child binds 127.0.0.1 → no race), competitive bind via abstract sockets, kernel-level spoofing.
- Lane untouched except this seat's out dir; scratch removed after copying artifacts.
