# SC02ProcStat — reopen S530: proc_pid_stat(5) starttime vs counter `rest[19]`

Seat SC02ProcStat · round 64 wave b (kama) · axes: operability + calibration · 2026-10-28.
Read-only seat: no counter run, no live server, no installs (curl/coreutils already present), no writes outside this report and scratch (scratch removed; hash recorded here).

## 1. Source re-opened

- URL: https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
- Page version: Linux man-pages 6.19, dated 2026-02-08 (footer "Linux man-pages 6.19 2026-02-08 proc_pid_stat(5)"; §COLOPHON names man-pages-6.19.tar.gz); HTML rendering created 2026-09-09.
- Access date: 2026-10-28 (full-HTML fetch today).
- Byte identity: today's fetch sha256 `0f04d78946538fd84db1536845abeb236da51a04844989f34ea7ee7cb0b6700f` == retained copy `.ufo/waves/round-64/source/proc_pid_stat.html` == the sha256 recorded in S530's anchor cell. Page unchanged since the row was opened.

Lane state: HEAD = freeze commit `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a`; working tree identical to it, so all line numbers below are frozen-tree lines.

## 2. Row under verification

`corpus/SOURCES.md` line 282 (S530, tier A, status queued, opened 2026-10-28, recheck 180d):

> scope: "field 22 `starttime` (ticks after boot) as a same-clock ordering of two processes' creation, and fields 3-4 state and ppid; Linux only; not wall-clock start time without btime"

used-by: "Two start times from one boot clock order the holder after the tool, which refuses a stale hold.json naming an older live pid".

## 3. Field numbering — page vs code

Page §DESCRIPTION: `(22) starttime %llu`; also `(3) state %c`, `(4) ppid %d`; 52 fields total.

Code `tools/round64-c1-counter.py:288-296` (`stat_fields`, frozen bytes):

```python
s = open(f'/proc/{pid}/stat', encoding='ascii').read()
rest = s[s.rindex(')') + 2:].split()
return int(rest[1]), int(rest[19])
```

Mapping: `rest` starts at field 3, so field N ↔ `rest[N-3]`. ppid: 4−3=1 → `rest[1]` ✓. starttime: 22−3=19 → `rest[19]` ✓.

Empirical check on this host (2026-10-28, live `/proc/self/stat`): 50 fields after comm (= fields 3..52), `rest[0]='R'`, `rest[1]` == `os.getppid()` (923625), `rest[19]`=20562805, and `uptime − rest[19]/CLK_TCK` = 0.01 s for a just-spawned process — `rest[19]` is field 22 in ticks.

## 4. Units — clock ticks, sysconf(_SC_CLK_TCK)

Page §DESCRIPTION field (22): "the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))" (10 words, field (22) starttime). Host CLK_TCK here = 100.

Code: the counter contains **no** sysconf/CLK_TCK conversion (0 grep hits). It stores and compares raw ticks only: `hold_fresh` requires every holder `start_ticks >= tool_start_ticks` (lines 467-473, recorded at 379, taken via `start_ticks_of` 747-748); `pid_gone` uses tick equality for identity against PID reuse (845-849, consumed at 921-923); `holders_signature` includes ticks (482-484); `unreadable_own` buckets by `start_ticks >= tool_ticks` (384). Nanosecond quantities (`t0_ns`, `hold_mtime_ns`, line 468-471) are compared only to each other. No tick value is ever compared against a seconds value, so the absent division is sound for every use made (ordering + identity); no seconds interpretation is claimed — consistent with S530's boundary "not wall-clock start time without btime".

## 5. comm may contain spaces/parentheses — page wording vs code defense

Page §DESCRIPTION field (2) comm, verbatim: "The filename of the executable, in parentheses." (7 words) and "Strings longer than TASK_COMM_LEN (16) characters (including the terminating null byte) are silently truncated." (15 words).

Scope finding: this man-pages 6.19 page does **not** literally state the parsing hazard that comm may contain spaces and parentheses — a grep over the fetched bytes finds no such sentence; the page gives only "in parentheses" and the 16-char truncation. The hazard is real at kernel level [INFERENCE from comm being an arbitrary executable filename / settable name — not from this page's text], and the code defends against it regardless: `s.rindex(')')` skips to the **last** `)`, which is comm's true terminator because no numeric field 3..52 can contain `)` (e.g. comm `(a)b c)` still parses correctly; a first-paren split would not). The `+ 2` crosses the single space the kernel emits after comm, and `.split()` absorbs further spacing. So: the code is correct, and its robustness exceeds what its cited page literally asserts. S530 itself claims only fields 3/4/22 and does not depend on the unstated rule — but any future citation of the spaces/parentheses rule to this page would overreach.

## 6. Soundness of comparing two processes' starttime from one boot

Yes — sound within one boot. Page field (22): "The time the process started after system boot" (8 words, §DESCRIPTION field (22) starttime): every process's value shares one zero point (the current boot) and one unit (clock ticks, constant per boot). Within a single boot, differences order the two creations, and equality pins identity — a PID reused by a later process carries a strictly later tick count. Across boots the zero point differs and the comparison is meaningless, which is exactly S530's boundary "not wall-clock start time without btime" (btime lives in `/proc/stat`, proc(5), not in this file).

The counter's uses are inside one boot by construction (local procfs read during one run): holder-after-tool ordering (`hold_fresh`, 467-473) and holder identity at teardown (921-923). The counter-owned control at 1408-1409 plants holder `start_ticks := tool_start_ticks - 1` to force `hold_fresh` false — the ordering comparison is load-bearing and falsifiable.

## 7. Findings (advisory leaves; not a verdict)

1. S530's cells match page and code: field 22/3/4 numbering, tick units, same-boot ordering scope, no-wall-clock boundary; quote locations verified verbatim; sha256 pin re-confirmed live 2026-10-28.
2. `rest[19]` is the correct index for field 22 given the split-past-last-`)` (field N ↔ `rest[N-3]`); empirically confirmed on a live process.
3. Raw-tick comparison without CLK_TCK division is correct for the ordering/identity uses; no unit mixing exists in the counter.
4. Only gap: the "comm may contain spaces and parentheses" rule is absent from this page version; the code's `rindex` defense rests on kernel behavior beyond the cited text (see §5).
5. `stat_fields` failure path returns `(None, None)` on OSError/ValueError/IndexError (295-296), matching callers' None checks (303-305, 846-848).

Evidence: code reads at `tools/round64-c1-counter.py:288-296,303,361-365,378-386,466-474,482-484,747-748,845-849,879,921-923,1408-1409`; S530 at `corpus/SOURCES.md:282`; retained source copy `.ufo/waves/round-64/source/proc_pid_stat.html` (byte-identical to today's fetch, hash in §1).
