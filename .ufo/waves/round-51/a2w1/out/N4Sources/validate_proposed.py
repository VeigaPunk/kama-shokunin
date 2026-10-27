#!/usr/bin/env python3
"""Validate proposed SOURCES rows for unbacked /proc interfaces.

Checks:
1. Every proposed quote exists verbatim in the corresponding fetched man page text.
2. Every proposed quote is strictly <= 25 words.
3. Every proposed row adheres to the 11-column SOURCES-CONTRACT-v1 schema.
4. Parsing and diffing via tools/sources-append-only.py passes cleanly with 0 violations.
"""

import os
import re
import sys

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LANE_DIR = os.path.abspath(os.path.join(OUT_DIR, "../../../../../../"))
import importlib.util
spec = importlib.util.spec_from_file_location("sao", os.path.join(LANE_DIR, "tools/sources-append-only.py"))
sao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sao)

PROPOSED_ROWS = [
    '| S500 | Linux proc_pid_stat(5) — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | what `/proc/<pid>/stat` fields report: (3) `state`, (4) `ppid` and (22) `starttime` (clock ticks after boot); Linux only; not other platforms, not thread stat | §DESCRIPTION, paragraphs (3),(4),(22); man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_stat.5.txt`) | "The PID of the parent of this process." and "The time the process started after system boot." — so tools can trace descendant process trees and detect process exit without PID-reuse races | mined | 2026-10-27 | 360d | tools/kama-context-capacity.py, tools/round49-replay-witness-audit.py, tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |',
    '| S501 | Linux proc_pid_fd(5) — https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html | docs | A | what `/proc/<pid>/fd/` entries are: symbolic links named by file descriptor, resolving for sockets to `socket:[<inode>]`; Linux only; not other platforms, not fd permissions | §DESCRIPTION ¶2; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_fd.5.txt`) | "For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode." — so the live tool and audit counters can match open socket inodes against `/proc/net/tcp{,6}` listeners | mined | 2026-10-27 | 360d | tools/kama-llamacpp-live.py, tools/round49-replay-witness-audit.py, tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |',
    '| S502 | Linux proc_pid_environ(5) — https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html | docs | A | what `/proc/<pid>/environ` contains: initial environment set when the program was started via execve(2), with null-byte-separated entries; Linux only; not post-exec modifications | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_environ.5.txt`) | "This file contains the initial environment that was set when the currently executing program was started via execve(2)." — so audit counters can check for canary environment leakage in child processes | mined | 2026-10-27 | 360d | tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |',
    '| S503 | Linux proc_pid_cmdline(5) — https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html | docs | A | what `/proc/<pid>/cmdline` holds: complete command line for the process as null-byte-separated strings; Linux only; not zombie processes | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cmdline.5.txt`) | "This read-only file holds the complete command line for the process, unless the process is a zombie." — so audit counters can extract command-line arguments like `-m <model>` from a running server | mined | 2026-10-27 | 360d | tools/round49-replay-witness-audit.py |',
    '| S504 | Linux proc_pid_cwd(5) — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html | docs | A | what `/proc/<pid>/cwd` is: a symbolic link to the current working directory of the process; Linux only; not terminated main thread | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cwd.5.txt`) | "This is a symbolic link to the current working directory of the process." — so audit counters can resolve relative path arguments against the server process working directory | mined | 2026-10-27 | 360d | tools/round49-replay-witness-audit.py |',
    '| S505 | Linux proc_pid(5) — https://man7.org/linux/man-pages/man5/proc_pid.5.html | docs | A | what numerical subdirectories under `/proc` are: per-process directories named by process ID; Linux only; not thread subdirectories | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid.5.txt`) | "There is a numerical subdirectory for each running process; the subdirectory is named by the process ID." — so descendant scanning can enumerate active host processes via `/proc` directory listing | mined | 2026-10-27 | 360d | tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |',
]

def clean_html(raw_html):
    txt = re.sub(r'<[^>]+>', '', raw_html)
    return txt.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

def main():
    print("--- 1. Checking Quote Word Counts and Verbatim Presence ---")
    file_map = {
        "S500": "proc_pid_stat.5.txt",
        "S501": "proc_pid_fd.5.txt",
        "S502": "proc_pid_environ.5.txt",
        "S503": "proc_pid_cmdline.5.txt",
        "S504": "proc_pid_cwd.5.txt",
        "S505": "proc_pid.5.txt",
    }

    for row in PROPOSED_ROWS:
        cols = [c.strip() for c in row.split('|')]
        rid = cols[1]
        teaches = cols[7]
        quotes = re.findall(r'"([^"]+)"', teaches)
        assert quotes, f"{rid} has no quotes in teaches cell"

        man_path = os.path.join(OUT_DIR, file_map[rid])
        assert os.path.isfile(man_path), f"Missing man page file: {man_path}"
        with open(man_path, "r", encoding="utf-8", errors="replace") as fh:
            man_text = clean_html(fh.read())

        print(f"[{rid}] ({file_map[rid]}):")
        for q in quotes:
            words = q.split()
            print(f"  Quote ({len(words)} words): {q}")
            if len(words) > 25:
                print(f"  FAILED: Quote exceeds 25 words ({len(words)})", file=sys.stderr)
                return 1
            # Check presence
            # Normalize whitespace for multi-line quotes
            norm_q = re.sub(r'\s+', ' ', q).strip()
            norm_man = re.sub(r'\s+', ' ', man_text).strip()
            if norm_q not in norm_man:
                print(f"  FAILED: Quote not found verbatim in {file_map[rid]}", file=sys.stderr)
                return 1
            print("    -> Verbatim match confirmed in man page.")

    print("\n--- 2. Checking SOURCES-CONTRACT-v1 Append-Only Compliance ---")
    sources_path = os.path.join(LANE_DIR, "corpus/SOURCES.md")
    with open(sources_path, "r", encoding="utf-8") as fh:
        orig_text = fh.read()

    lines = orig_text.splitlines()
    s499_idx = next(i for i, l in enumerate(lines) if l.startswith("| S499 |"))
    new_lines = lines[:s499_idx+1] + PROPOSED_ROWS + lines[s499_idx+1:]
    new_text = "\n".join(new_lines) + "\n"

    from_rows, header = sao.parse_registry(orig_text, "orig")
    to_rows, _ = sao.parse_registry(new_text, "proposed")
    violations, added = sao.diff_registries(from_rows, to_rows, header)

    if violations:
        print(f"FAILED: Append-only violations detected: {violations}", file=sys.stderr)
        return 1

    print(f"Clean append-only diff: {len(added)} rows added ({added}), 0 violations.")
    print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
