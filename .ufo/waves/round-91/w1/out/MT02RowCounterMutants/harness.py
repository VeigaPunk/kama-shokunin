#!/usr/bin/env python3
"""Mutation harness for the frozen C2 counter tools/round91-threshold-rows.py.

Two detectors, both run against an arbitrary counter path (--counter):

  battery : the frozen forgery battery .ufo/waves/round-91/controls/c2-forgeries.py,
            copied verbatim in fixture construction and variant data, with the
            printed expectations turned into assertions.  A counter is KILLED when a
            labelled quantity mismatches, the summary line is missing (crash), or the
            exit code differs.
  m2      : the frozen predicate itself at M2=3f317ec: must print
            rows>=10, unbound=0, duplicates=0, fetch_failures=0, engines>=3, exit 0.

Usage:
  harness.py battery --lane L --scratch S --counter C [--out FILE]
  harness.py m2      --lane L --rev R --counter C [--out FILE]
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
SUMMARY = re.compile(
    r"THRESHOLD_ROWS rows=(\d+) bound=(\d+) unbound=(\d+) duplicates=(\d+) "
    r"engines=(\d+) fetch_failures=(\d+) rev=(\S+)")

# variant -> (rows, bound, unbound, duplicates, engines, exit); None = not labelled by the battery
EXPECT = {
    "V1-one-legit-row": (1, 1, 0, 0, 1, 1),
    "V2-ten-prose-rows-absent-source": (10, 0, 10, None, None, 1),
    "V3-mixed-forgeries": (11, 1, 9, 1, 1, 1),
    "V4-ten-bound-rows-one-engine": (10, 10, 0, 0, 1, 1),
}


def g(D, *args):
    subprocess.run(["git", "-C", str(D), *args], check=True, capture_output=True)


def skill(rows, extra=""):
    return "# fixture SKILL\n\n" + HEAD + "\n\n" + TABLE_HEAD + "\n".join(rows) + "\n" + extra + "\n## Next\n"


def parse(out: str):
    m = SUMMARY.search(out)
    if not m:
        return None
    rows, bound, unbound, dup, eng, fails, rev = m.groups()
    return dict(rows=int(rows), bound=int(bound), unbound=int(unbound), dup=int(dup),
                engines=int(eng), fails=int(fails))


def run_counter(counter: str, repo: str, rev: str):
    p = subprocess.run([sys.executable, counter, "--repo", repo, "--rev", rev],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def battery(args):
    Path(args.scratch).mkdir(parents=True, exist_ok=True)
    D = Path(tempfile.mkdtemp(prefix="c2-fixture-", dir=args.scratch)).resolve()
    killed_any = False
    try:
        g(D, "init", "-q")
        top = subprocess.run(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert Path(top).resolve() == D, (top, D)
        src = (Path(args.lane) / "corpus/SOURCES.md").read_text()
        extra_src = (
            "| S9001 | curl doc on a moving ref — https://raw.githubusercontent.com/curl/curl/master/docs/cmdline-opts/max-filesize.md | docs | A | fixture | sha256 " + SHA587 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n"
            "| S9002 | curl doc wrong digest curl-8_23_0 — " + U587 + " | docs | A | fixture | sha256 " + "0" * 64 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n"
            "| S9003 | curl doc queued curl-8_23_0 — " + U587 + " | docs | A | fixture | sha256 " + SHA587 + " | fixture | queued | 2026-11-06 | on-release | fixture |\n")
        (D / "corpus").mkdir()
        (D / "corpus/SOURCES.md").write_text(src + extra_src)

        variants = []
        variants.append(("V1-one-legit-row", skill([LEGIT])))
        prose = [f"| T{i:02d} | llama.cpp b12177 | prose threshold {i} | {i}0 | S999 | {i} | `{i}0` | prose only |" for i in range(1, 11)]
        variants.append(("V2-ten-prose-rows-absent-source", skill(prose)))
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
        variants.append(("V3-mixed-forgeries", skill(mixed, hidden)))
        rows = []
        for sid, url in (("S587", U587), ("S590", U590)):
            text = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace").split("\n")
            for n, line in enumerate(text, 1):
                m = re.search(r"\d+", line)
                if m and "|" not in line and "`" not in line and len(rows) < (5 if sid == "S587" else 10):
                    lit = line[max(0, m.start() - 12):m.end() + 4].strip()
                    if m.group(0) in lit and lit:
                        ident = next((w for w in re.findall(r"[A-Za-z_][\w-]{2,}", lit)), None)
                        if ident:
                            rows.append(f"| T{len(rows) + 1:02d} | curl curl-8_23_0 | `{ident}` number on line {n} | {m.group(0)} | {sid} | {n} | `{lit}` | one-engine padding |")
        variants.append(("V4-ten-bound-rows-one-engine", skill(rows)))

        for name, text in variants:
            (D / "SKILL.md").write_text(text)
            g(D, "add", "-A")
            g(D, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-q", "-m", name)
            rc, out, err = run_counter(args.counter, str(D), "HEAD")
            s = parse(out)
            exp = EXPECT[name]
            fields = ("rows", "bound", "unbound", "dup", "engines")
            bad = []
            if s is None:
                bad.append("no-summary")
            else:
                for k, e in zip(fields, exp[:5]):
                    if e is not None and s[k] != e:
                        bad.append(f"{k}={s[k]}!={e}")
            if rc != exp[5]:
                bad.append(f"exit={rc}!={exp[5]}")
            killed = bool(bad)
            killed_any = killed_any or killed
            if s is None:
                actual = "crash" + (" " + err.strip().splitlines()[-1] if err.strip() else "")
            else:
                actual = (f"rows={s['rows']} bound={s['bound']} unbound={s['unbound']} "
                          f"duplicates={s['dup']} engines={s['engines']} "
                          f"fetch_failures={s['fails']} exit={rc}")
            print(f"BATTERY {name} killed={int(killed)} "
                  f"why={','.join(bad) if bad else 'matches-expectation'} actual=[{actual}]")
            for line in out.splitlines():
                if line.startswith("THRESHOLD_ROW"):
                    print(f"  {line}")
        print(f"BATTERY_VERDICT {'killed' if killed_any else 'alive'}")
        return 0 if killed_any else 1
    finally:
        shutil.rmtree(D, ignore_errors=True)


def m2(args):
    rc, out, err = run_counter(args.counter, args.lane, args.rev)
    s = parse(out)
    if s is None:
        tail = err.strip().splitlines()[-1] if err.strip() else ""
        print(f"M2 killed=1 why=no-summary exit={rc} tail={tail!r}")
        print("M2_VERDICT killed")
        return 1
    met = (s["rows"] >= 10 and s["bound"] == s["rows"] and s["unbound"] == 0
           and s["dup"] == 0 and s["fails"] == 0 and s["engines"] >= 3 and rc == 0)
    print(f"M2 killed={int(not met)} rows={s['rows']} bound={s['bound']} unbound={s['unbound']} "
          f"duplicates={s['dup']} engines={s['engines']} fetch_failures={s['fails']} exit={rc}")
    print(f"M2_VERDICT {'killed' if not met else 'alive'}")
    return 0 if met else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    b = sub.add_parser("battery")
    b.add_argument("--lane", required=True)
    b.add_argument("--scratch", required=True)
    b.add_argument("--counter", required=True)
    m = sub.add_parser("m2")
    m.add_argument("--lane", required=True)
    m.add_argument("--rev", required=True)
    m.add_argument("--counter", required=True)
    a = ap.parse_args()
    return battery(a) if a.mode == "battery" else m2(a)


if __name__ == "__main__":
    sys.exit(main())
