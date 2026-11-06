#!/usr/bin/env python3
"""Round-91 C2 pre-freeze forgery battery for tools/round91-threshold-rows.py.

Builds a scratch fixture git repo (never the lane), one commit per variant, and runs the counter
named by --counter against each commit. Usage:
    python3 c2-forgeries-path.py --lane <lane> --counter <counter.py> --scratch <dir>
Every variant prints its expectation label first, then the counter's output and exit code.
MT02 adaptation: the ONLY change from controls/c2-forgeries.py is the --counter argument; the
fixture construction and expectations are byte-identical.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HEAD = "## Serving timeout and limit thresholds"
U587 = "https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/max-filesize.md"
U590 = "https://raw.githubusercontent.com/curl/curl/curl-8_23_0/lib/sendf.c"
SHA587 = "4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f"
LEGIT = "| T01 | curl curl-8_23_0 | `curl` `--max-filesize` aborts unknown-length bodies from | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | keep the written-size re-check for older curl |"
TABLE_HEAD = ("| id | engine pin | threshold | value | source | line | literal | probe decision |\n"
              "|---|---|---|---|---|---|---|---|\n")


def g(D, *args):
    subprocess.run(["git", "-C", str(D), *args], check=True, capture_output=True)


def skill(rows, extra=""):
    return "# fixture SKILL\n\n" + HEAD + "\n\n" + TABLE_HEAD + "\n".join(rows) + "\n" + extra + "\n## Next\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--counter", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    D = Path(tempfile.mkdtemp(prefix="c2-fixture-", dir=a.scratch)).resolve()
    try:
        g(D, "init", "-q")
        top = subprocess.run(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert Path(top).resolve() == D, (top, D)
        src = (Path(a.lane) / "corpus/SOURCES.md").read_text()
        extra_src = (
            "| S9001 | curl doc on a moving ref — https://raw.githubusercontent.com/curl/curl/master/docs/cmdline-opts/max-filesize.md | docs | A | fixture | sha256 " + SHA587 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n"
            "| S9002 | curl doc wrong digest curl-8_23_0 — " + U587 + " | docs | A | fixture | sha256 " + "0" * 64 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n"
            "| S9003 | curl doc queued curl-8_23_0 — " + U587 + " | docs | A | fixture | sha256 " + SHA587 + " | fixture | queued | 2026-11-06 | on-release | fixture |\n")
        (D / "corpus").mkdir()
        (D / "corpus/SOURCES.md").write_text(src + extra_src)

        variants = []
        variants.append(("V1-one-legit-row", "expect rows=1 bound=1 unbound=0 duplicates=0 engines=1 exit=1 (below 10 rows)",
                         skill([LEGIT])))
        prose = [f"| T{i:02d} | llama.cpp b12177 | prose threshold {i} | {i}0 | S999 | {i} | `{i}0` | prose only |" for i in range(1, 11)]
        variants.append(("V2-ten-prose-rows-absent-source", "expect rows=10 bound=0 unbound=10 exit=1", skill(prose)))
        mixed = [
            LEGIT,
            "| T02 | curl curl-8_23_0 | wrong line | 8.4.0 | S587 | 10 | `Starting with curl 8.4.0` | x |",
            "| T03 | curl curl-8_23_0 | value not in literal | 9.9 | S587 | 35 | `threshold during` | x |",
            "| T04 | curl master | moving ref | 8.4.0 | S9001 | 34 | `Starting with curl 8.4.0` | x |",
            "| T05 | curl curl-8_23_0 | digest mismatch | 8.4.0 | S9002 | 34 | `Starting with curl 8.4.0` | x |",
            "| T06 | curl curl-8_3_0 | pin not in url | 8.4.0 | S587 | 30 | `before curl 8.4.0` | x |",
            "| T07 | vllm curl-8_23_0 | engine not in url | 8.4.0 | S587 | 31 | `8.4.0` | x |",
            "| T08 | curl curl-8_23_0 | queued source | 8.4.0 | S9003 | 34 | `Starting with curl 8.4.0` | x |",
            "| T09 | curl curl-8_23_0 | duplicate of T01 | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |",
            "| T10 | curl curl-8_23_0 | empty decision | 8.4.0 | S587 | 33 | `threshold` | - |",
            "| T14 | curl curl-8_23_0 | names no parameter of the line | 0 | S590 | 179 | `excess_len = 0` | x |",
        ]
        hidden = ("<!--\n| T11 | curl curl-8_23_0 | hidden in comment | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |\n-->\n"
                  "```\n| T12 | curl curl-8_23_0 | fenced | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |\n```\n"
                  " | T13 | curl curl-8_23_0 | indented | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |\n")
        variants.append(("V3-mixed-forgeries",
                         "expect rows=11 bound=1 unbound=9 duplicates=1 exit=1 (T11 comment, T12 fence, T13 indented not counted; T14 name-not-in-literal; "
                         "T02 literal-not-at-line, T03 value-not-in-literal, T04 moving-ref, T05 sha-mismatch, T06 pin-not-in-url, "
                         "T07 engine-not-in-url, T08 source-status, T10 empty-cell)",
                         skill(mixed, hidden)))
        # V4: ten genuinely bound rows from one engine (curl): engines=1 < 3
        rows = []
        for sid, url, pin_ok in (("S587", U587, True), ("S590", U590, True)):
            text = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace").split("\n")
            for n, line in enumerate(text, 1):
                m = re.search(r"\d+", line)
                if m and "|" not in line and "`" not in line and len(rows) < (5 if sid == "S587" else 10):
                    lit = line[max(0, m.start() - 12):m.end() + 4].strip()
                    if m.group(0) in lit and lit:
                        ident = next((w for w in re.findall(r"[A-Za-z_][\w-]{2,}", lit)), None)
                        if ident:
                            rows.append(f"| T{len(rows) + 1:02d} | curl curl-8_23_0 | `{ident}` number on line {n} | {m.group(0)} | {sid} | {n} | `{lit}` | one-engine padding |")
        variants.append(("V4-ten-bound-rows-one-engine", "expect rows=10 bound=10 unbound=0 engines=1 exit=1 (engines < 3)",
                         skill(rows)))
        for name, label, text in variants:
            (D / "SKILL.md").write_text(text)
            g(D, "add", "-A")
            g(D, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-q", "-m", name)
            p = subprocess.run([sys.executable, str(Path(a.counter)),
                                "--repo", str(D), "--rev", "HEAD"], capture_output=True, text=True)
            print(f"== {name}: {label}")
            print(p.stdout.rstrip())
            print(f"exit={p.returncode}")
    finally:
        shutil.rmtree(D, ignore_errors=True)


if __name__ == "__main__":
    main()
