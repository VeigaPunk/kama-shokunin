#!/usr/bin/env python3
"""Witness fixtures for C2 counter mutants that survive the frozen forgery battery.

Each case is a minimal scratch fixture repo holding a SKILL.md section plus the lane's
corpus/SOURCES.md and four synthetic source rows.  A case is valid only when the PRISTINE
counter returns the documented verdict; the mutant is then run on the same repo to show
that the mutated rule flips the row (or crashes), i.e. the battery lacks the row.

Usage: witness.py --lane L --scratch S --case NAME --counters PRISTINE,MUTANT
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HEAD = "## Serving timeout and limit thresholds"
TABLE_HEAD = ("| id | engine pin | threshold | value | source | line | literal | probe decision |\n"
              "|---|---|---|---|---|---|---|---|\n")
U587 = "https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/max-filesize.md"
SHA587 = "4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f"
EXTRA_SRC = (
    "| S9001 | curl doc on a moving ref — https://raw.githubusercontent.com/curl/curl/master/docs/cmdline-opts/max-filesize.md | docs | A | fixture | sha256 " + SHA587 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n"
    "| S9002 | curl doc wrong digest curl-8_23_0 — " + U587 + " | docs | A | fixture | sha256 " + "0" * 64 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n"
    "| S9003 | curl doc queued curl-8_23_0 — " + U587 + " | docs | A | fixture | sha256 " + SHA587 + " | fixture | queued | 2026-11-06 | on-release | fixture |\n"
    "| S9101 | curl doc absent path curl-8_23_0 — https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/absent-r91-witness.md | docs | A | fixture | sha256 " + SHA587 + " | fixture | mined | 2026-11-06 | on-release | fixture |\n")

BASE = ("| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |")
CASES = {
    # name: (rows, expected pristine probe)
    "M01-b2-value": ([
        "| T01 | curl curl-8_23_0 | `threshold` prose | 9.9 | S587 | 35 | `threshold during` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="value-not-in-literal")),
    "M02-b4-moving": ([
        "| T01 | curl master | `Starting` marker | 8.4.0 | S9001 | 34 | `Starting with curl 8.4.0` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="moving-ref")),
    "M03-b4-pin": ([
        "| T01 | curl curl-8_3_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="pin-not-in-url")),
    "M04-b4-engine": ([
        "| T01 | vllm curl-8_23_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="engine-not-in-url")),
    "M05-b5-sha": ([
        "| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S9002 | 34 | `Starting with curl 8.4.0` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="sha-mismatch")),
    "M12-min-rows": ("LANE3", dict(summary=dict(rows=3, bound=3, unbound=0, engines=3), exit=1)),
    "M13-arity": ([
        "| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x | extra |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="cells=9")),
    "M14-fetch": ([
        "| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S9101 | 34 | `Starting with curl 8.4.0` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1, fails=1), row="T01", why="fetch-failed")),
    "M15-empty-dash": ([
        "| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | - |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="empty-cell")),
    "M16-source-status": ([
        "| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S9003 | 34 | `Starting with curl 8.4.0` | x |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="source-status=queued/tier=A")),
    "M17-section-prefix": ([BASE],
                           dict(summary=dict(rows=1, bound=1, unbound=0), extra_section=True)),
    "M18-dup-id": ([BASE,
                    "| T01 | curl curl-8_23_0 | `curl` bump | 8.4.0 | S587 | 30 | `before curl 8.4.0` | x |"],
                   dict(summary=dict(rows=2, bound=1, unbound=0, dup=1))),
    "M22-empty-string": ([
        "| T01 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` |  |"],
        dict(summary=dict(rows=1, bound=0, unbound=1), row="T01", why="empty-cell")),
}
SUMMARY = re.compile(r"THRESHOLD_ROWS rows=(\d+) bound=(\d+) unbound=(\d+) duplicates=(\d+) "
                     r"engines=(\d+) fetch_failures=(\d+) rev=(\S+)")


def g(D, *args):
    subprocess.run(["git", "-C", str(D), *args], check=True, capture_output=True)


def lane_rows(lane, rev):
    text = subprocess.run(["git", "-C", lane, "show", f"{rev}:SKILL.md"],
                          capture_output=True, text=True, check=True).stdout
    keep = {}
    for line in text.split("\n"):
        for rid in ("T01", "T08"):
            if line.startswith(f"| {rid} |"):
                keep[rid] = line
    return [keep["T01"], keep["T08"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--rev", default="3f317ecd211e80929c673e306e3230be287fdf20")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--counters", required=True, help="comma-separated counter paths")
    a = ap.parse_args()
    rows, expect = CASES[a.case]
    if rows == "LANE3":
        rows = lane_rows(a.lane, a.rev) + [
            "| T15 | curl curl-8_23_0 | `Starting` marker | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |"]
    D = Path(tempfile.mkdtemp(prefix=f"witness-{a.case}-", dir=a.scratch)).resolve()
    try:
        g(D, "init", "-q")
        top = subprocess.run(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert Path(top).resolve() == D, (top, D)
        (D / "corpus").mkdir()
        (D / "corpus/SOURCES.md").write_text(
            (Path(a.lane) / "corpus/SOURCES.md").read_text() + EXTRA_SRC)
        text = "# fixture SKILL\n\n" + HEAD + "\n\n" + TABLE_HEAD + "\n".join(rows) + "\n"
        if expect.get("extra_section"):
            text += ("\n## Serving timeout and limit thresholds (extended)\n\n" + TABLE_HEAD
                     + "| T09 | curl curl-8_23_0 | `curl` bump | 8.4.0 | S587 | 30 | "
                       "`before curl 8.4.0` | x |\n")
        (D / "SKILL.md").write_text(text + "\n## Next\n")
        g(D, "add", "-A")
        g(D, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-q", "-m", a.case)
        for c in a.counters.split(","):
            p = subprocess.run([sys.executable, c, "--repo", str(D), "--rev", "HEAD"],
                               capture_output=True, text=True)
            s = SUMMARY.search(p.stdout)
            got = (dict(rows=int(s.group(1)), bound=int(s.group(2)), unbound=int(s.group(3)),
                        dup=int(s.group(4)), engines=int(s.group(5)), fails=int(s.group(6)))
                   if s else None)
            ok = True
            why_bad = []
            if got is None:
                ok = False
                why_bad.append("no-summary")
            else:
                for k, v in expect.get("summary", {}).items():
                    if got[k] != v:
                        ok = False
                        why_bad.append(f"{k}={got[k]}!={v}")
                if "exit" in expect and p.returncode != expect["exit"]:
                    ok = False
                    why_bad.append(f"exit={p.returncode}!={expect['exit']}")
            probe = ""
            if got is not None and "row" in expect:
                m = re.search(rf"THRESHOLD_ROW {expect['row']} bound=(\d+) why=(\S+)", p.stdout)
                probe = f"probe={m.group(0)}" if m else "probe=missing"
                if not m or m.group(2) != expect["why"]:
                    ok = False
                    why_bad.append(f"probe-why={m.group(2) if m else 'missing'}!={expect['why']}")
            if got is None:
                tail = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
                print(f"WITNESS case={a.case} counter={Path(c).name} matches_pristine_expect={ok} "
                      f"crash exit={p.returncode} tail={tail!r}")
            else:
                print(f"WITNESS case={a.case} counter={Path(c).name} matches_pristine_expect={ok} "
                      f"rows={got['rows']} bound={got['bound']} unbound={got['unbound']} dup={got['dup']} "
                      f"engines={got['engines']} fails={got['fails']} exit={p.returncode} {probe} "
                      f"{'why=' + ','.join(why_bad) if why_bad else ''}")
            for line in p.stdout.splitlines():
                if line.startswith("THRESHOLD_ROW"):
                    print(f"  {line}")
        return 0
    finally:
        shutil.rmtree(D, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
