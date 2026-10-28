# Round 64 · wave b · SB03LessonGate — lesson Gate and Sources draft (kama, operability)

Milestone: draft lesson gate. Leaf seat, no subagents, no lane source edited, no commit, no registry edit, no live server started.

Deliverables (durable evidence):
- `.ufo/waves/round-64/b/out/SB03LessonGate/gate-draft.md` — the `## Gate` block (per-row URL, access date, located quote ≤25 words, verdict), the `### Admit/reject table` (11 candidates), and the `## Sources` block.
- `.ufo/waves/round-64/b/out/SB03LessonGate/flips.md` — planned `status`/`used-by` flips old→new, plus proposed rejected rows S533-S535. Not applied.
- `.ufo/waves/round-64/b/out/SB03LessonGate/fetch/` — the fetched HTML and text renderings (S529-S532, three extra candidates, S508 live page) and the round-53 text copy's check output.
- `.ufo/waves/round-64/b/out/SB03LessonGate/work/` — `extract.py` (tag-stripping renderer), `locate.py` (quote locator), `quotes2.json`/`quotes3.json`, `locate.out`, `probe.out`, `manifest.sha256`.

## 1. Findings

### 1.1 Located quotes (C1 rows S529-S532)

Every quote is located in the fetched bytes by `work/locate.py` against the tag-stripped rendering, after whitespace normalisation.

| Row | Quotes (line anchors in `fetch/<page>.txt`) | Words | Located |
|---|---|---|---|
| S529 proc_pid_fd(5) | 11-12, 22-23, 59-61 | 20, 18, 21 | yes, yes, yes |
| S530 proc_pid_stat(5) | 131; 133-134; 48 | 8; 10; 8 | yes ×3 |
| S531 proc_pid_environ(5) | 11-13; 19-20 | 18; 7 | yes ×2 |
| S532 proc_pid_cmdline(5) | 17-19; 23-24; 29-30 | 25; 16; 15 | yes ×3 |
| S508 proc_pid_map_files(5), live | 37-39 | 19 | yes |

Total 15/15 located, 0 NOT FOUND. Longest quote is 25 words (S532 line 17-19), at the cap. The four pages are man-pages 6.19 (2026-02-08) on their colophons (S508 too).

Hash check: the fetched bytes for S529-S532 hash equal to the sha256 pinned in the registry rows. The L1's retained copies in `.ufo/waves/round-64/source/` are the same bytes as a live fetch today.

### 1.2 Access date — discrepancy for the L1 to settle

- Local date (UTC-3) is 2026-10-28, the date the freeze and the registry rows use. I record "Accessed 2026-10-28 (local)".
- The UTC fetch times are 2026-10-29 00:14 (S529-S532 and extra candidates) and 00:16 (S508 live). I record them beside the local date, unchanged.
- I did not change the registry's `opened` cell. Either date is defensible; the L1 picks one convention for the round. The Gate states both, so neither is hidden.

### 1.3 S508 rejection — restated and re-proved

- Live quote (lines 37-39): "since Linux 5.9, the reading process must have either CAP_SYS_ADMIN or CAP_CHECKPOINT_RESTORE in the initial (i.e., root) user namespace." (19 words)
- Probe on this host (read-only, own pid, uid 1000, `CapEff` 0000000000000000): `readlink` of a `/proc/self/map_files` entry returned `/usr/bin/python3.14`; `os.open` of the same entry raised `[Errno 1] Operation not permitted`. This matches the round-53 probe. Output: `work/probe.out`.
- Reject stands. The counter reads mapped files from `/proc/<pid>/maps` (S496) and the server from `/proc/<pid>/exe` (S495).
- Flip: a counter run holding CAP_CHECKPOINT_RESTORE.

### 1.4 Admit/reject table — result

| # | Candidate | Decision |
|---|---|---|
| 1 | procfs fd table (S529) | admit |
| 2 | `/proc/<pid>/stat` fields 3, 4, 22 (S530) | admit |
| 3 | `/proc/<pid>/environ` (S531) | admit |
| 4 | `/proc/<pid>/cmdline` layout (S532) | admit, layout only |
| 5 | `/proc/<pid>/cmdline` as sole identity | reject (claim; no row) |
| 6 | `map_files` (S508) | reject, restated |
| 7 | `proc_stat(5)` btime (wall-clock start) | reject this round; opened, no check uses it |
| 8 | `proc_pid_status(5)` PPid/CapEff/Uid | reject this round; opened, no tool reads it |
| 9 | `sock_diag(7)` netlink listing | reject this round; opened, no tool uses netlink |
| 10 | `netlink(7)` | not a candidate (prerequisite read only) |
| 11 | procfs paths read by the three round-64 tools | all covered by rows |

Candidate 5 is the important refusal. S532's own text says the process may rewrite its argv ("If, after an execve(2), the process modifies its argv strings, those changes will show up here."). The counter uses argv only beside the exe re-hash, the maps, the environment, ancestry and freshness (`argv_ok`, counter lines 421-433). So argv is never identity on its own, and round 63's MT15 forgeries show why.

### 1.5 Calibration notes on the rows' own cells (for the L1, not a verdict on the claims)

These are wording issues in the candidate rows. They do not change any admit verdict.

a. S529 scope cell says "not an access-control model". The page (lines 59-61) says reading the fd links "is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check". The cell should say the page does not describe a policy, not that no access check exists. KQ22 freezes that cell at first commit, so the fix is a superseding row or a knowledge-entry note, not an edit.

b. S529 teaches says a listener inode "can be joined to every process that holds it". The page's own limit (lines 59-66) is that an unreadable fd table is possible. The row's limit text covers this; the teaches cell reads wider than the source.

c. S530 teaches says two starttimes "order the holder after the tool". The page says starttime is in clock ticks (lines 133-134), and the counter's freshness check is `start_ticks >= tool_start_ticks` (counter lines 470-472). Equal ticks pass that non-strict check, so a holder started in the same tick is not strictly after the tool. The descendant check (`bind_ancestry`, tool pid in `ppids`) still binds the tool, so this is a narrow residue. I report it as a falsifier target: a holder created in the same tick as the tool. I do not claim it breaks C1.

### 1.6 Registry plan (not applied)

- S529-S532: `queued → mined`; `used-by` `— → corpus/knowledge/process-bound-listener.md, corpus/lessons/round-64.md`. Only once that knowledge file exists (checked: it does not exist yet).
- S508: status stays `rejected`; `used-by` gains `corpus/lessons/round-64.md`.
- S049, S495, S496: `used-by` gains the knowledge file only if that file cites them.
- Proposed rejected rows S533 (proc_stat), S534 (proc_pid_status), S535 (sock_diag), ids the first free after S532. Round-53 precedent records rejections as rows (S503-S509). The L1 decides.
- Candidate 5 gets no row (a claim, not a source).
- `registry/staged-refusals.tsv` does not apply: these are source candidates, not staged items.

## 2. Constraints met, and what I did not do

- Nothing in `corpus/` was written. The lesson file `corpus/lessons/round-64.md` does not exist at draft time; the blocks are drafted in my out dir for the L1 to integrate.
- No edit to `corpus/SOURCES.md`, `registry/`, or the knowledge directory. No commit, push, or git mutation of any kind.
- No live llama-server started. No loopback port touched. The one host probe is read-only, on this seat's own process.
- Fetches used `curl -sSL` with the seat name as User-Agent. Renderings use stdlib `html.parser` only.
- Tools installed or upgraded by this seat: none. Only `curl`, `python3` (stdlib) and `coreutils` were used.
- The sha256 of each fetched page is recorded in `work/manifest.sha256`.
- Scratch `/fast/scratch/hyaku/kama-r64/b/SB03LessonGate/` removed after its receipts were copied into the out dir.

## 3. Hand-off checks for the main agent

1. When the L1 creates `corpus/lessons/round-64.md`, paste the `## Gate` and `## Sources` blocks from `gate-draft.md`, and settle the access-date convention (§1.2).
2. Decide the S529 scope-cell wording and the S530 "order" wording (§1.5) through a superseding row or a knowledge-entry note, per KQ22.
3. Create `corpus/knowledge/process-bound-listener.md` before applying any flip in `flips.md`. Then run `python3 tools/sources-append-only.py` over the round's commits touching `corpus/SOURCES.md` (exit 0).
4. Route §1.5(c) (same-tick freshness) to the falsify seats as a test target, not as a finding against the frozen counter.

Tally: `gate_tally located=15/15 max_words=25 admit=4 reject_restated=1 reject_candidates=3 reject_claim=1 flips_applied=0 errors=0`
