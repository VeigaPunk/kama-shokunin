# RV03SourcesGate — round 64, wave b, kama (operability)

Item: review of the sourced claim — registry rows S529–S532 (corpus/SOURCES.md) against the
SOURCES contract (CORPUS.md §SOURCES rules 1–6, 11-column table), their scope clauses, and
which sentence of tools/round64-c1-counter.py each row supports. Tip under review:
f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (export at $S/tip; no edits, no commits, no live servers
kept). Evidence: .ufo/waves/round-64/b/out/RV03SourcesGate/.

Tools: none installed or upgraded. Used `sudo -n` (passwordless) once to start and then kill a
root-owned loopback listener on 127.0.0.1:47993 that I started (probe, §3). Nothing else touched.

## 1. Census validate (required)

Command: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama --file
$S/tip/corpus/SOURCES.md`

- **exit code: 0**; stderr empty.
- E-codes: **none** (E01–E12 all absent; E-only count = 0).
- W-codes on the file: 105 lines in total, all pre-existing and none on S529–S532:
  - W04 (same URL across scopes): 103 rows (e.g. S031, S043, …, S528). Not in my item.
  - W01 (tier C mined with used-by): S481 only.
  - No W01/W02/W03/W04 line names S529, S530, S531 or S532.
- Output stored: out/RV03SourcesGate/validate.tsv.

## 2. Row-by-row contract check (CORPUS.md §SOURCES)

Checked with a Python parse of the four rows (11 cells each, no extra pipes) plus the awk census
path. The census rows are all `queued` with used-by `—`.

| row | cells | id | kind | tier | status | opened | recheck | anchor (section + revision) | retained bytes sha256 = row's sha256 |
|---|---|---|---|---|---|---|---|---|---|
| S529 | 11 ✓ | S529 ✓ | docs ✓ | A ✓ | queued ✓ | 2026-10-28 ✓ | 180d ✓ | §DESCRIPTION, man-pages 6.19 (2026-02-08) ✓ | 3a50ddef… ✓ |
| S530 | 11 ✓ | S530 ✓ | docs ✓ | A ✓ | queued ✓ | 2026-10-28 ✓ | 180d ✓ | §DESCRIPTION field (22), 6.19 (2026-02-08) ✓ | 0f04d789… ✓ |
| S531 | 11 ✓ | S531 ✓ | docs ✓ | A ✓ | queued ✓ | 2026-10-28 ✓ | 180d ✓ | §DESCRIPTION, 6.19 (2026-02-08) ✓ | 93394d9e… ✓ |
| S532 | 11 ✓ | S532 ✓ | docs ✓ | A ✓ | queued ✓ | 2026-10-28 ✓ | 180d ✓ | §DESCRIPTION, 6.19 (2026-02-08) ✓ | 1fc68168… ✓ |

Rule-by-rule:
- Rule 2 (append-only): `git diff 0c1eff3 f6a4ea9 -- corpus/SOURCES.md` = 4 insertions, 0 deletions. ✓
- Rule 3 (no second method): rows are source records only; no method text. ✓
- Rule 6 (no credentials / session URLs): URLs are public man7.org pages. ✓
- Rule 1 (gate record): **NOT MET AT TIP.** The `## Gate` block of corpus/lessons/round-64.md (URL,
  access date, ≤25-word located quote per row) does not exist at f6a4ea9 or in the lane working
  tree. The freeze (controls/freeze.txt, "Sourced:") cites it, and gen-b.py line 132 plans it as a
  wave-b draft item, so it is pending L1 integration, not an authored-and-lost record. Until it
  lands, the freeze's pointer dangles and rule 1 is unmet. Census does not check Gate blocks, so
  the validate pass does not catch this. [Action for L1: land the Gate block before the C1
  instrument is cited as sourced.]
- Anchors: each names a section (§DESCRIPTION / §DESCRIPTION field (22)) plus revision
  (man-pages 6.19, 2026-02-08). ✓ Not a bare homepage.
- Bytes: the four retained files are tracked at f6a4ea9 (`.ufo/waves/round-64/source/`); sha256s
  equal the row values (out/…/source-sha256.txt, rows-S529-S532.md).
- Live re-open (rule 1, non-author sample): re-read https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html
  today. The §DESCRIPTION text ("initial environment … started via execve(2) … will not reflect those
  changes") matches the retained bytes verbatim. ✓
- Colophon date note: the retained pages say "fetched … on 2026-09-09" (man7 mirror date); the row
  says `opened 2026-10-28` (our open date). Not a contradiction; the row's revision is the man-pages
  version and date, which is what the anchor records. [INFERENCE: no change needed.]

## 3. Scope-clause check and the counter's use of each row

Row → counter sentence mapping (predicate sentences from the round64-c1-counter.py docstring, which
repeats freeze.txt "C1-r64"):

**S529 (proc_pid_fd(5)) — "every holder of the run-port listener is the hold pid".**
- Supports: `holder_pids` (round64-c1-counter.py L258–286) joins `socket:[inode]` readlinks to
  /proc/net/tcp listener inodes; `bind_holders` (L413–417).
- Scope clause: "an unreadable fd table is an observation limit, not an absence." **Overreach in the code.**
  In `holder_pids`, a PermissionError on /proc/<pid>/fd adds the pid to `unreadable` only when
  `st_uid == me`. A foreign-uid (or non-dumpable, foreign-owned) holder is dropped silently and is
  never recorded. The snapshot field `unreadable_old` (L385) counts only the own-uid set, and
  `grade_binding` never reads it (grep: one hit in the file, the assignment at L385). So an
  unreadable holder is graded as absence, which S529's own scope clause forbids.
- **Probe (executed, receipt out/…/probe_root_holder.out):** I started a root-owned listener on
  127.0.0.1:47993 (`sudo -n`, pid 1057531). Its fd 3 reads `socket:[1859020742]` (sudo ls). Calling
  the tip counter's own `listeners()` and `holder_pids()` on that port gave:
  `listeners [(1859020742, True)]`, `holder_pids [] unreadable [1500, 2911361]`. The root holder is
  invisible to the snapshot; `unreadable` lists only the own-uid pids. Killed my listener afterward.
- Consequence: a root-owned or non-dumpable foreign-owned process holding the listener fd would
  leave `holders` = {hold pid} and pass `bind_holders`. The freeze's control families (76) do not
  include a foreign-uid holder, so no control rejects it. The counter's threat model is own-uid
  forgeries, which narrows the impact, but the row's teaching ("the counter can list every holder
  … from procfs") and the predicate's "every holder" are both broader than the code. Severity:
  medium for C1 claim wording; not a forged-tool bypass under the stated threat model.
  [Action: either count unreadable foreign holders as a fail (no counter can then say "every holder"
  on a shared host), or narrow the predicate to "every readable holder" and record the limit; add a
  control for a non-readable holder. This is an AMENDMENT-class change before wave f.]

**S530 (proc_pid_stat(5)) — the holder "started after the tool did", "the hold.json is fresh".**
- Supports: `stat_fields` (L289–298): `rest[1]` = field 4 ppid and `rest[19]` = field 22 starttime
  (index check: rest[0] is field 3, so field 22 is rest[19]) ✓; `ppid_chain` (ancestry);
  `hold_fresh` (L467–476) compares holder start_ticks with the tool's.
- Scope clause "same-clock ordering, not wall-clock without btime" is respected (the counter uses
  ticks only for ordering; the hold.json mtime vs t0 comparison is wall clock, which is not S530's
  claim). ✓
- Minor: `hold_fresh` uses `>=` (L471–472). Ticks are 1/100 s (sysconf CLK_TCK), so a holder
  started in the same tick as the tool passes "started after". The row says the start times "order
  the holder after the tool"; that is non-strict ordering. [Minor; wording or `>` change.]
- Minor: the row's teaches lists "fields 3-4 state and ppid". The counter reads ppid (field 4) and
  starttime (field 22) only; `state` (field 3) is never graded. The teaches is broader than use.
  [Minor; trim the row's teaches or add a zombie check — not required by the predicate.]

**S531 (proc_pid_environ(5)) — "its … initial environment … are the pinned set".**
- Supports: `holder_record` reads `/proc/<pid>/environ` keys (L354–359); `bind_env` (L434–437)
  refuses any key starting with `LD_` or `GLIBC_TUNABLES`.
- The row's teaches ("refuse a held server started under an injected LD_* variable") matches the
  code exactly, and its scope ("initial environment at execve, not later modification") is correct.
  The row is not overreaching.
- **Predicate overreach (not the row):** the freeze/docstring sentence "its argv, initial
  environment and mapped files are the pinned set" is not what `bind_env` checks. It checks
  absence of two prefixes, not equality with a pinned environment. The sentence should read
  "initial environment carries no LD_*/GLIBC_TUNABLES key". [Action: amend the docstring sentence
  or add a pinned-key check. Recorded as a predicate/code mismatch, not a row error.]

**S532 (proc_pid_cmdline(5)) — "its … argv … [is] the pinned set".**
- Supports: `holder_record` splits cmdline on NUL (L348–352); `_flag_values` (L390–398);
  `argv_ok` (L421–431) checks `--port`, `--host`, `--alias`, `--model` (each once for --model; port,
  alias, host compare to exact lists) and `realpath(argv[0])` against the server path.
- The row's teaches ("checks --port, --alias, --model once each against the run it started") is a
  correct subset of the code, and its scope ("a process may rewrite its own argv") is correct; the
  row does not overreach.
- **Predicate overreach (not the row):** "argv … are the pinned set" overstates a four-flag check.
  Argv beyond those flags is not graded. [Action: same as S531 — narrow the sentence to the flags
  checked, or add full-argv equality. The exe check (`bind_exe`, S495) is what actually resists
  argv spoofing, and the row says so only implicitly.]

**Sentences with no S529–S532 support** (do not cite these rows for them): the exe re-hash
(S495/S499), maps (S496), teardown and listener-closed observation, the reference-server agreement,
and the proc_net_tcp listener join (S049). The counter's own comment (L223–224) names these man
pages but cites no S-ids; that is an omission in the comment, not a row error.

## 4. Findings (by severity)

1. **Medium — S529 scope clause vs. the code.** Unreadable foreign-uid fd tables are dropped, not
   failed; `unreadable_old` is recorded and never graded. Probe reproduces it (root listener →
   holders empty). The "every holder" sentence in the C1 predicate is not supported as written.
   Fix options as in §3, S529. Not a forged-tool bypass under the own-uid threat model.
2. **Medium — rule 1 gate missing at tip.** corpus/lessons/round-64.md `## Gate` (URL, date, quote for
   S529–S532) is absent; the freeze cites it. Pending L1 (gen-b.py L132), not authored here.
3. **Low — predicate overstates S531/S532 use.** "argv, initial environment … are the pinned set"
   vs. checks for four argv flags and absence of two env prefixes. Rows are correctly scoped.
4. **Low — S530 `>=` and teaches breadth.** Non-strict ordering at tick granularity; teaches lists
   `state`, which is never graded.
5. **Info — rows conform to the contract**: 11 cells, no pipes, valid enums, section+revision
   anchors, retained-bytes sha256 match, append-only diff, live re-open of S531 matches the quote.
6. **Info — census**: exit 0, no E-codes, no W on S529–S532.

## 5. Residual risk and verification gaps

- Not run: the full C1 counter (out of this item's scope; the wave-b C1 seats cover it).
- The root-listener probe exercised only `listeners()` and `holder_pids()`. I did not run
  `collect()`/`grade_binding()` end to end with a root holder; the static claim that `unreadable_old`
  is ungraded rests on grep (one hit at L385) and on reading `grade_binding` (L398–480).
- The own-uid non-dumpable case (a dumpable=0 own-uid process started before the tool holding the
  listener) is inferred from the same code path, not executed.
- I re-opened one of four source URLs live (S531). The other three rely on the retained bytes and
  the matching sha256; the retained bytes match the row values.

## 6. Checks for the main agent to run once

- `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama --file <tip>/corpus/SOURCES.md`
  (done here: exit 0, no E).
- Land the round-64 `## Gate` block for S529–S532 (rule 1) before wave f cites the rows.
- Decide the S529 holder-visibility wording (narrow to "readable holders" or fail on unreadable
  foreign fd tables) and add a control for it; then amend the C1 docstring sentences for argv/env.

## Receipts (out/RV03SourcesGate/)

- validate.tsv (105 W-lines, 0 E), validate.err (empty)
- probe_holders.py, root_listen.py, probe_root_holder.out (the root-holder probe, executed)
- rows-S529-S532.md (verbatim rows), source-sha256.txt, tip-SOURCES.sha256, rowcheck.py, man-text/

## Verdict-free summary line (tally)

`validate kama(--file tip): exit=0 E=0 W(S529-S532)=0 rows=4 contract_ok=4/4 gate_present=0/4 (rule 1 pending)`
