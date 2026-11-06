#!/usr/bin/env python3
"""MT02 killing fixtures — round 91 wave w1a2.

For every mutant that survived the frozen forgery battery (V1-V4), this script builds the fixture
row that its rule removes and shows the aggregate flip; for the five mutants the battery killed
only through the printed per-row `why` (B2, B4 moving-ref, pin, engine, sha256, empty-cell), it
shows a row that flips the FINAL predicate, i.e. the aggregate-level fixture the battery lacks.

Fixtures are a scratch git repo built the same way as controls/c2-forgeries.py: SOURCES.md from
--lane plus fixture rows, one commit per variant. Every pristine row binds or fails exactly as the
`expect` string says; the target mutant must change the final THRESHOLD_ROWS numbers.

Usage: mt02-killers.py --lane <scratch checkout> --frozen <counter> --mutants <dir> \
                       --scratch <dir> --out <dir>
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HEAD = "## Serving timeout and limit thresholds"
U587 = "https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/max-filesize.md"
UMASTER = "https://raw.githubusercontent.com/curl/curl/master/docs/cmdline-opts/max-filesize.md"
SHA587 = "4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f"
LEGIT = ("| T01 | curl curl-8_23_0 | `curl` `--max-filesize` aborts unknown-length bodies from "
         "| 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | keep the written-size re-check for older curl |")
TABLE_HEAD = ("| id | engine pin | threshold | value | source | line | literal | probe decision |\n"
              "|---|---|---|---|---|---|---|---|\n")
SRC_HEAD = ("| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|\n")


def g(D, *args):
    subprocess.run(["git", "-C", str(D), *args], check=True, capture_output=True)


def skill(rows, heading=HEAD):
    return "# fixture SKILL\n\n" + heading + "\n\n" + TABLE_HEAD + "\n".join(rows) + "\n## Next\n"


def srcrow(sid, desc, url, tier="A", digest=SHA587, indent=""):
    return (f"{indent}| {sid} | {desc} — {url} | docs | {tier} | fixture | sha256 {digest} "
            f"| fixture | mined | 2026-11-06 | on-release | fixture |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--frozen", required=True)
    ap.add_argument("--mutants", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    D = Path(tempfile.mkdtemp(prefix="mt02-kill-", dir=a.scratch)).resolve()
    out = Path(a.out)
    extra = "\n".join([
        srcrow("S9002", "curl doc wrong digest", U587, digest="0" * 64),
        srcrow("S9101", "curl doc at tag curl-8_23_0", U587, indent="    "),   # 4 spaces: not a sources row
        srcrow("S9102", "curl doc at tag curl-8_23_0", U587, tier="C"),
        srcrow("S9103", "curl doc at tag curl-8_23_0", "(" + U587 + ")"),      # URL inside parentheses
        srcrow("S9104", "curl doc on master (moving ref)", UMASTER),
    ]) + "\n"
    # (name, rows, heading, expect-on-pristine, target mutant stem, why the row isolates the rule)
    variants = [
        ("K01-min-rows",
         [LEGIT,
          "| T02 | llama.cpp b12177 | `timeout_read` read timeout | 3600 | S593 | 634 | `int32_t timeout_read        = 3600;` | x |",
          "| T03 | ollama v0.40.11 | `keepAlive` idle unload | 5 | S594 | 130 | `keepAlive = 5 * time.Minute` | x |"],
         HEAD, "rows=3 bound=3 engines=3 exit=1 (rows<10)", "M12-MIN_ROWS-10-to-0",
         "three genuinely bound rows from three engines isolate the n>=10 floor (V1 cannot: engines=1 also fails)"),
        ("K02-heading-suffix",
         [LEGIT], HEAD + " (draft)", "rows=0 exit=1 (heading is not exact)", "M14-heading-prefix-match",
         "a heading with a suffix must not open the section"),
        ("K03-indented-source",
         ["| T01 | curl curl-8_23_0 | `curl` `--max-filesize` | 8.4.0 | S9101 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=0 why=source-absent (4-space SOURCES row is not a source row)", "M15-src-re-any-indent",
         "a SOURCES row indented 4 spaces is not a data row"),
        ("K04-url-in-parens",
         ["| T01 | curl curl-8_23_0 | `curl` `--max-filesize` | 8.4.0 | S9103 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=1 (closing paren stripped from the URL)", "M17-url-rstrip-dropped",
         "the URL token inside a SOURCES cell ends with `)`"),
        ("K05-tier-c-source",
         ["| T01 | curl curl-8_23_0 | `curl` `--max-filesize` | 8.4.0 | S9102 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=0 why=source-status=mined/tier=C", "M18-tier-check-dropped",
         "a mined tier-C row is not a tier-A/B source"),
        ("K06-B2-value",
         ["| T01 | curl curl-8_23_0 | `threshold` transfer threshold | 9.9 | S587 | 35 | `threshold during transfer.` | x |"],
         HEAD, "bound=0 why=value-not-in-literal", "M01-drop-B2-value-in-literal",
         "value 9.9 is not in line 35 while B7's `threshold` is: the battery's T03 also fails B7"),
        ("K07-B4-moving-ref",
         ["| T01 | curl master | `curl` `--max-filesize` | 8.4.0 | S9104 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=0 why=moving-ref", "M02-drop-B4-moving-ref",
         "master URL whose live bytes currently equal the tag digest; the battery's T04 also fails B7"),
        ("K08-B4-pin",
         ["| T01 | curl curl-8_3_0 | `curl` `--max-filesize` | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=0 why=pin-not-in-url", "M03-drop-pin-check",
         "engine pin curl-8_3_0 absent from the curl-8_23_0 URL; the battery's T06 also fails B7"),
        ("K09-B4-engine",
         ["| T01 | vllm curl-8_23_0 | `curl` `--max-filesize` | 8.4.0 | S587 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=0 why=engine-not-in-url", "M04-drop-engine-check",
         "engine vllm absent from a curl URL; the battery's T07 also fails B6"),
        ("K10-B5-sha",
         ["| T01 | curl curl-8_23_0 | `curl` `--max-filesize` | 8.4.0 | S9002 | 34 | `Starting with curl 8.4.0` | x |"],
         HEAD, "bound=0 why=sha-mismatch", "M05-sha-compare-removed",
         "SOURCES digest is all zeros for the real URL; the battery's T05 also fails B7"),
        ("K11-B1-empty-decision",
         [LEGIT.rsplit("|", 2)[0] + "| - |"], HEAD, "bound=0 why=empty-cell", "M19-empty-cell-check-removed",
         "otherwise-legit row with a `-` decision; the battery's T10 also fails B2/B7"),
    ]
    try:
        g(D, "init", "-q")
        top = subprocess.run(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert Path(top).resolve() == D, (top, D)
        (D / "corpus").mkdir()
        (D / "corpus/SOURCES.md").write_text(
            (Path(a.lane) / "corpus/SOURCES.md").read_text() + extra)
        g(D, "add", "-A")
        g(D, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-q", "-m", "sources")
        lines, ok_all = [], True
        for name, rows, heading, expect, target, why in variants:
            (D / "SKILL.md").write_text(skill(rows, heading))
            g(D, "add", "-A")
            g(D, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-q", "-m", name)
            mp = Path(a.mutants) / f"{target}.py"
            outs = {}
            for tag, counter in (("pristine", Path(a.frozen)), (target, mp)):
                p = subprocess.run([sys.executable, str(counter), "--repo", str(D), "--rev", "HEAD"],
                                   capture_output=True, text=True)
                outs[tag] = p
            def agg(p):
                m = re.search(r"^THRESHOLD_ROWS rows=(\d+) bound=(\d+) unbound=(\d+) duplicates=(\d+) "
                              r"engines=(\d+) fetch_failures=(\d+)", p.stdout, re.M)
                return tuple(int(x) for x in m.groups()) if m else None
            def whys(p):
                return re.findall(r"^THRESHOLD_ROW (\S+) bound=(\d+) why=(\S+)$", p.stdout, re.M)
            pa, ma = agg(outs["pristine"]), agg(outs[target])
            killed = pa != ma or outs["pristine"].returncode != outs[target].returncode
            ok_all &= killed
            lines.append(f"== {name} (target {target})")
            lines.append(f"   rule: {why}")
            lines.append(f"   expect pristine: {expect}")
            lines.append(f"   pristine: agg={pa} exit={outs['pristine'].returncode} rows={whys(outs['pristine'])}")
            lines.append(f"   mutant  : agg={ma} exit={outs[target].returncode} rows={whys(outs[target])}")
            lines.append(f"   VERDICT: {'KILLED-aggregate' if killed else 'SURVIVED'}")
        txt = "\n".join(lines) + "\n"
        (out / "killers.out").write_text(txt)
        print(txt)
        print("all_killer_fixtures_flip=%s" % ("yes" if ok_all else "no"))
        return 0 if ok_all else 1
    finally:
        shutil.rmtree(D, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
