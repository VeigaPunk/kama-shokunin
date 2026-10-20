VERDICT: n/a — report extras drafted from read-only lane, fleet-log, registry and host evidence; no claim graded, one install-record contradiction reported.

# ScribeReportExtras — round 17, falsify wave, report extras

Scope: the five extras named in the falsify assignment (stale-lane line, tool installs, wave table, planner-seat mapping, open L0 questions). Attacked: the assignment's premise "tool installs: none this round" (contradicted, §3) and "falsify TBD" (partly landed, §4). Reads only; no lane file other than this report was written; no port contacted; no llama-server started; no install or update performed by this seat. Scratch: none created, nothing to remove.

## 1. Lane state (read-only)

- Lane HEAD is `54a2926` = `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, the build commit (`git rev-parse HEAD`). Round start was `cff9e62` (`corpus/lessons/round-17.md:3-4`).
- `git status --porcelain` shows one untracked path: `?? .ufo/waves/round-17/falsify/`. This is the in-flight falsify tree; L1 integrates it.

## 2. Stale-lane line

STALE-LANE (open launch, no close record): `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:484` reads `launch kama round=17 pgid=3049098 driver=hyaku-inline attempt=1` at 2026-10-20T11:52:26-03:00. Counts over the whole log at read time (15:37 -03): `lane-dead-no-report kama round=17` → 0; `complete kama round=17` → 0. The log's last line is 501 (`15:36:24-03:00`). `ps -o pid,pgid,etime,cmd -p 3049098` prints no process.
- Round-16 precedent for a closed pair: `watchdog.log:475` launch, `:481` `complete kama round=16; hyaku-inline attempt=1`.
- [INFERENCE] The pgid is not a liveness signal here: the round runs in-session (`hyaku-inline`), so no completion line exists until L1 closes the round. L1 should append `complete kama round=17` (or the lane-dead line) at close. The fleet log is outside this lane and was not written.

## 3. Tool installs (round 17 and the round-16 llama.cpp disclosure)

Assignment premise: "none this round". Observed: two installs fall inside round 17 (launched 11:52:26 -03, `watchdog.log:484`).

| Tool | Version observed | Channel (evidence) | Installed (local time -03) | Reason |
|---|---|---|---|---|
| ruff | 0.17.1 (`ruff --version`) | `uv tool install` — `~/.local/share/uv/tools/ruff/uv-receipt.toml` `requirements = [{ name = "ruff" }]` (unpinned); dir mtime `2026-10-20 13:14:22` | 2026-10-20 13:14:22 | **not recorded** in any round-17 artifact (`grep -rIl -i "ruff\|vulture\|uv tool install" .ufo/waves/round-17` → no output) |
| vulture | 2.16 (`vulture --version`) | `uv tool install` — `~/.local/share/uv/tools/vulture/uv-receipt.toml` `requirements = [{ name = "vulture" }]`; dir mtime `2026-10-20 13:14:53` | 2026-10-20 13:14:53 | **not recorded** (same grep) |

- Attribution: [unknown] which seat or actor ran these. The host is shared; the receipts do not name a caller. Reason: [unknown]. Both channels are permitted under the 2026-10-19 tooling directive (`/home/vgpnk/.omp/agent/RULES.md`, channel order starts with `uv tool install`).
- Earlier uv tools, not this round (`ls -ld` mtimes on `~/.local/share/uv/tools/*`; receipts for versions): `check-jsonschema` 0.38.2 (2026-10-19 18:31:23), `trafilatura` 2.3.1 (2026-10-19 18:01:32), `unblob` 26.6.4 (2026-10-13 13:53:07).
- Host pacman (lane performs none): `/var/log/pacman.log` latest 2026-10-20 entry is `[2026-10-20T13:23:08-0300] [ALPM] installed zcode (3.16.2-1)`, transaction completed 13:23:09 -0300. [unknown] whether this predates the 2026-10-20 host-wide pacman pause; the pause's time is not recorded in the lane. L1 should compare the two times.

Round-16 llama.cpp install disclosure (routed defect 5, `corpus/lessons/round-17.md:116-120`):
- Retained archive: `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`, 22,240,468 bytes, mtime 2026-10-20 10:17:48 -03. `sha256sum` re-run this round: `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, equal to the upstream asset digest per `build/advice/ScoutInstallFootprint.md` §3 and `corpus/SOURCES.md:50` (S038).
- Extracted tree: `~/.local/opt/llama-b11755/` (`du -sb` 56,288,736 bytes, dir mtime 2026-10-20 08:10:36 -03, per `build/advice/ScoutInstallFootprint.md` §2).
- PATH link: `~/.local/bin/llama-server` → `~/.local/opt/llama-b11755/llama-server`, mtime 10:17:53 -03. `~/.local/bin/llama-server --version` (exit 0, no server started): `version: 0.7.0-dev (build 11755, commit 704366d76)`. `/usr/bin/llama-server` absent (`build/advice/ScribeInstallDisclosure.md`, read-only `ls`).
- Date discrepancy: `.ufo/l0-questions.md:58` says the install was "installed under the 2026-10-19 tooling directive"; every mtime above is dated 2026-10-20. Recorded as observed. [INFERENCE] the directive authorized the install and the install ran on 10-20.
- Retained archive is not named in L0 question (b): `.ufo/l0-questions.md:58` ends "(b) keep, or remove, the persistent install, the PATH link and the model cache." The follow-up line drafted at `build/drafts/install-disclosure.md` is not appended (line 58 contains no `tar.gz`). Operator decision: none recorded.
- Model cache `~/.cache/kama-shokunin`: not measured this round.

## 4. Wave table

| Wave | Spec / registry | Seats | Role mix (registry recount; `build/completion-summary.json` role_mix matches) | Dispatch record | Verdict first lines (strict) |
|---|---|---|---|---|---|
| build | `build/spec.json`; `build/advice/swarm-registry.json` (82 members, all `kind: spawn`) | **82** | executor 15, scout 19, reviewer 14, critic 6, sentinel 2, connector 8, revenger 4, scribe 10, simplifier 2, mutation-tester 2 = 82 | 1 task call refused 82 (`Background job limit reached (100)`) at 15:03:50Z; 4 capacity checks; spawned 82 at 15:15:50Z (`build/attempts.json`, `build/refused-result-1.json`) | confirm 34, partial 32, n/a 15, refute 1, nonconformant 0 (`build/verdict-counts.json`; `build/completion-summary.json`: 82 advice files, 0 missing, terminal completed 82 failed 0) |
| falsify | `falsify/spec.json`; `falsify/advice/swarm-registry.json` (80 members) | **80** | reviewer 34, scout 8, critic 7, executor 6, connector 6, scribe 6, revenger 5, mutation-tester 4, sentinel 2, simplifier 2 = 80 | task call at 18:35:33Z spawned 80 (`falsify/attempts.json`); `falsify/provenance-ledger.json` wave_run `counts.dispatch.spawn` 80, spawned entry `bound_run_index` 0. Before that: 25 timestamped capacity checks (17:29:08Z–18:33:33Z) and one note reconstructing "20 capacity checks" in 16:28–17:28Z (kernel state lost; reconstructed) | [L1 fills after falsify] — at read time 5 of 80 report files exist (below) |

Falsify reports landed at read time (`falsify/advice/`, first line only): `LiveRerun.md` confirm; `MisrootSweep.md` partial; `ScribeLessonFalsify.md` n/a; `ScribeReportSources.md` confirm; `ScribeReportWork.md` n/a. [L1 fills after falsify] for the remaining 75 seats and the strict count.

Sum checks: build 19+15+14+10+8+6+4+2+2+2 = 82; falsify 34+8+7+6+6+6+5+4+2+2 = 80.

## 5. Planner-seat mapping

- Rule: the validator rejects a planner role by design; "the L1 holds the canonical §3 planner seat and a planning data-walk may ride a scout/connector/revenger item — the mapping is recorded in the report, validation is never bypassed" (`.ufo/l0-questions.md:52`, L0 ANSWER dated 2026-10-19). The answer says it is "now binding in scripts/hyaku/lane-addendum.md §6.2". A grep of `/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md` for `6.2` printed no match, so §6.2 is cited from the L0 answer only [unverified].
- Build mapping: planning data-walk seat = `RevengerPlannerWalk` (role `revenger`; agentId `KamaR17.RevengerPlannerWalk-2`, `build/advice/swarm-registry.json:392-394`). Output `build/advice/RevengerPlannerWalk.md`, first line `VERDICT: confirm`. The canonical planner seat is L1 (`build/make_spec.py:15`).
- Falsify mapping: no planner-walk seat. `grep -i planner falsify/advice/swarm-registry.json` printed no match. [L1 fills after falsify] if L1 adds one.

## 6. Open L0 questions (kama rows in `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md`, 9 rows)

| Line | Round | Question (short) | Status in file |
|---|---|---|---|
| 13 | round-1 | Repoint 8080→34113 for stale model pins / restore serving unit | open — no ruling line |
| 15 | round-1 | Addendum to 13 (janitor failover, declared vs served context) | open — no ruling line |
| 17 | round-1 | Add `kama-shokunin/` to fleet `.gitignore` | no ruling line; fact now holds: `.gitignore:1` is `*-shokunin/`, and `git check-ignore -v kama-shokunin` → `.gitignore:1:*-shokunin/` (exit 0). L1 decides closure |
| 21 | round-2 | Systemd user timer for `kama-probe.sh snapshot` | open — no ruling line |
| 31 | round-1 | Reconcile relaunched round counter and dispatch contract | open — no ruling line |
| 41 | round-1 | 2026-10-15 freshness addendum to 13 | open — no ruling line |
| 48 | round-8 | `opencode-go/glm-5.3-flash-free` missing from host catalog (blocks rounds 9,12,13,16,17) | open — no ruling line |
| 52 | round-11 | Planner taxonomy vs validator | ANSWERED 2026-10-19 (see §5) |
| 58 | round-16 | Ratify/reject the live llama.cpp fixture; keep/remove install, PATH link, model cache | open — no ruling; tarball follow-up not appended (§3) |

Other-lane rows naming kama: `.ufo/l0-questions.md:65` (tabi, round-17) asks whether the round-16 CDP ruling covers kama's `corpus/knowledge/listener-census.md:355`; no ruling line. Not kama: `:53` (tsukuroi, round-12) carries the same planner ANSWER as line 52; `:62` (tabi, round-17) concerns kagi/kake.

## 7. Commands run (read-only unless stated)

- `git rev-parse HEAD`, `git log --oneline -n 12`, `git status --porcelain`, `git check-ignore -v kama-shokunin` (exit 0 for check-ignore; others printed output).
- `grep -c` over `.ufo/watchdog.log` for the kama round-17 `lane-dead-no-report` and `complete` lines (both 0); `grep -n "kama round=1[67]"` for lines 475/481/484; `tail` of the log (last line 501).
- `ps -o pid,pgid,etime,cmd -p 3049098` (no process).
- `python3` JSON recounts of `build/advice/swarm-registry.json`, `falsify/advice/swarm-registry.json`, `build/completion-summary.json`, `build/verdict-counts.json`, `falsify/attempts.json`, `build/attempts.json`, `falsify/provenance-ledger.json`. One KeyError on `build/spawn-result.json` `counts` (no such top-level key); not used.
- `uv tool list` (printed); `ls -lt` on `~/.local/bin`; `ls -l ~/.local/opt | grep -i llama`; `ls -ld ~/.local/share/uv/tools/*`; `cat .../uv-receipt.toml` for ruff, vulture, check-jsonschema, trafilatura, unblob (all printed).
- `ruff --version`, `vulture --version`, `timeout 10 ~/.local/bin/llama-server --version` (exit 0 recorded for llama-server; no server started).
- `sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (printed digest).
- `grep -rIl -i "ruff\|vulture\|uv tool install" .ufo/waves/round-17 --exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj` (no output).
- `grep "2026-10-2" /var/log/pacman.log | tail -n 6` (printed).
- `ss -ltnp` (listing only; no connection made).
- `grep` over `.ufo/l0-questions.md` and fleet `scripts/hyaku/lane-addendum.md` for `6.2` (no match). Exit codes are recorded only where stated above; elsewhere success is inferred from printed output.

## 8. Limitations and inferences

- [INFERENCE] The two uv installs are probably round-17 lane activity given their timestamps, but no receipt, log or artifact names a caller. Reported as unattributed.
- Falsify figures are a snapshot at read time (5 of 80 reports); verdicts for the rest are [L1 fills after falsify].
- The "20 capacity checks" note in `falsify/attempts.json` is reconstructed and cannot be checked per entry; I used the 25 timestamped entries and did not reconcile the two.
- The installed tree was not re-hashed here; the tarball digest was re-run. Tree digest was re-derived in `build/advice/ScoutInstallFootprint.md` §4.
- No pacman transaction, service action, port contact or install was performed by this seat.
