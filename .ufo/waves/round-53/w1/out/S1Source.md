AGREE — S506–S508 citations, scope claims, live text copies, and the S508 probe are supported.

## Evidence

Commands run:
- `curl -sSL` each of the three man7.org URLs named in `corpus/SOURCES.md` rows S506–S508 (lane lines 259–261); downloaded HTML sizes and per-page comparison output are preserved in `w1/out/S1Source/evidence.txt`.
- `python3 strip_compare.py`: stripped HTML text with Python `HTMLParser` and compared whitespace-token streams to the three `.ufo/waves/round-53/c1/` copies.
- `cat /proc/sys/kernel/yama/ptrace_scope` → `1`; `/proc/self/status` `CapEff` → `0x0`.
- `python3 probe_map_files.py` → exit 0; readlink succeeded for two `/proc/<child>/map_files/<range>` entries, open failed with errno 1 (`EPERM`), while opening `/usr/bin/sleep` by path succeeded; child was reaped. Full stdout is in `w1/out/S1Source/evidence.txt`.

### Per-cell verdicts

- **S506 — AGREE.** At `corpus/SOURCES.md:259`, the §DESCRIPTION quote is verbatim and 18 words: “This file can be used to access the pages of a process's memory through open(2), read(2), and lseek(2).” The live page immediately states that access is governed by a ptrace access mode `PTRACE_MODE_ATTACH_FSCREDS` check. Copy lines 52–57 contain the quote and check; line 79 records Linux man-pages 6.19, dated 2026-02-08.
- **S507 — AGREE.** At `corpus/SOURCES.md:260`, the value-1 Yama quote is verbatim and 17 words: “By default, the predefined relationship is that the target process must be a descendant of the caller.” The live §`/proc/sys/kernel/yama/ptrace_scope` says scope 1 requires either `CAP_SYS_PTRACE` or the predefined relationship (default: descendant); it also describes `PR_SET_PTRACER` as a way to declare an additional allowed PID. Scope 2 permits attach only with `CAP_SYS_PTRACE`; scope 3 permits no `PTRACE_MODE_ATTACH` operations. The claim is accurate for the stated default descendant relationship and privileged override. Copy lines 1580–1605 contain these scope rules; line 1713 records Linux man-pages 6.19, dated 2026-06-05. Host scope is 1.
- **S508 — AGREE.** At `corpus/SOURCES.md:261`, the §DESCRIPTION capability fragment is verbatim and 12 words: “since Linux 5.9, the reading process must have either CAP_SYS_ADMIN or CAP_CHECKPOINT_RESTORE”; the page continues that the capability must be in the initial (root) user namespace. Copy lines 84–86 state this; line 108 records Linux man-pages 6.19, dated 2026-02-08. Probe against my own child reproduced readlink success/open `EPERM`; host `CapEff=0`, with both named capability bits clear. Direct open of the mapped file by pathname succeeded, confirming the observed EPERM was specific to the `map_files` entry.

### Text-copy comparison

For each page, the live page's stripped, whitespace-normalized token stream is an exact prefix of its c1 text copy: proc_pid_mem 227/272 tokens, ptrace 10634/10679, map_files 407/452. The extra copy tail is the man7.org analytics script text: the raw live HTML contains `sc_project`, while the comparison intentionally skipped script/style bodies. Thus the copies preserve all live page prose and also contain the page's embedded analytics-script text; no prose mismatch was found.

No server was started by this seat. A `pgrep -af llama-server` observation showed processes under another seat's K2Design scratch; they were not touched. No tool was installed.
