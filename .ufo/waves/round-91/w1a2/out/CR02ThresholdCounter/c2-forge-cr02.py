#!/usr/bin/env python3
"""CR02: round-91 C2 forgery battery against tools/round91-threshold-rows.py (bytes at F).

Builds ONE scratch fixture git repo (git init; NEVER the lane) with corpus/SOURCES.md copied
from the lane at M2 plus forged rows, and a forged SKILL.md per variant; runs the LANE counter
against each commit and prints the counter's own verdict.

    python3 c2-forge-cr02.py --lane <lane> --rev <M2> --scratch <dir> [--only V3]

All upstream bytes are fetched once from the pinned URLs named in SOURCES S593/S594/S595 and
their sha256 checked before any row is built, so every "literal" below is a true substring of
the file the row cites.
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HEAD = "## Serving timeout and limit thresholds"
TBL = ("| id | engine pin | threshold | value | source | line | literal | probe decision |\n"
       "|---|---|---|---|---|---|---|---|\n")
U = {
    "S593": "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h",
    "S594": "https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go",
    "S595": "https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py",
}
SHA = {
    "S593": "c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073",
    "S594": "0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895",
    "S595": "e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694",
}
ENG = {"S593": ("llama.cpp", "b12177"), "S594": ("ollama", "v0.40.11"), "S595": ("vllm", "v0.32.0")}
FILES = {}


def load():
    for sid, url in U.items():
        body = urllib.request.urlopen(url, timeout=60).read()
        assert hashlib.sha256(body).hexdigest() == SHA[sid], (sid, "sha drift")
        FILES[sid] = body.decode("utf-8").split("\n")


def lit(sid, n, prefer=None):
    """A literal that is an exact substring of line n and safe inside one table cell."""
    line = FILES[sid][n - 1].rstrip()
    assert "|" not in line and "`" not in line, (sid, n, line)
    if prefer and prefer in line:
        i = line.index(prefer)
        return line[i:i + len(prefer)]
    return line


def row(rid, engine, name, value, sid, n, literal, decision="forged"):
    return f"| {rid} | {engine} | {name} | {value} | {sid} | {n} | `{literal}` | {decision} |"


def src(sid, desc, url, sha, tier="A", status="mined", indent=0, extra_cells=()):
    cells = [f" S{sid} ", f" {desc} \u2014 {url} ", " code ", f" {tier} ",
             " CR02 forged provenance ", f" fixture sha256 {sha} ",
             " forged ", f" {status} ", " 2026-11-06 ", " on-release ", " fixture "]
    cells = list(cells) + list(extra_cells)
    return (" " * indent) + "|" + "|".join(cells) + "|"


def skill(rows, extra="", pre=""):
    return "# fixture SKILL\n\n" + pre + HEAD + "\n\n" + TBL + "\n".join(rows) + "\n" + extra + "\n## Next\n"


# ten numeric lines that are NOT serving thresholds: printf width, compile-time macro, commented
# enum member, prose comment, log level, bind-address comment, "Default is 5 minutes" comment,
# SPDX licence id, mkdocs fence markers.
GARBAGE = [
    ("T01", "S593", 36, "`COM_DBG` log macro", "12"),
    ("T02", "S593", 34, "`COMMON_RECURSIVE_LIMIT` recursion cap", "128"),
    ("T03", "S593", 126, "`COMMON_SAMPLER_TYPE_TFS_Z` disabled enum member", "5"),
    ("T04", "S593", 767, "`progress` value range comment", "1.0"),
    ("T05", "S594", 200, "`TRACE` log-level comment", "2"),
    ("T06", "S594", 62, "`ConnectableHost` bind-address comment", "0.0"),
    ("T07", "S594", 128, "`Default` prose comment", "5"),
    ("T08", "S595", 1, "`Apache-2.0` licence identifier", "2.0"),
    ("T09", "S595", 577, "`start` docs fence marker", "8"),
    ("T10", "S595", 2288, "`end` docs fence marker", "8"),
]


def garbage_rows(engine_override=None, sid_override=None):
    out = []
    for rid, sid, n, name, val in GARBAGE:
        eng, pin = ENG[sid]
        engine = f"{eng} {pin}" if engine_override is None else engine_override(sid)
        s = sid if sid_override is None else sid_override(sid, n)
        out.append(row(rid, engine, name, val, s, n, lit(sid, n)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    load()
    scratch = Path(a.scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    counter = str(Path(a.lane).resolve() / "tools/round91-threshold-rows.py")
    base_src = subprocess.run(["git", "-C", a.lane, "show", f"{a.rev}:corpus/SOURCES.md"],
                              capture_output=True, check=True).stdout.decode()

    D = Path(tempfile.mkdtemp(prefix="c2-cr02-", dir=scratch)).resolve()
    try:
        subprocess.run(["git", "-C", str(D), "init", "-q"], check=True, capture_output=True)
        top = subprocess.run(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert Path(top).resolve() == D, (top, D)
        (D / "corpus").mkdir()

        def commit(name, skill_text, sources_text):
            (D / "SKILL.md").write_text(skill_text)
            (D / "corpus/SOURCES.md").write_text(sources_text)
            subprocess.run(["git", "-C", str(D), "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(D), "-c", "user.name=fixture",
                            "-c", "user.email=fixture@invalid", "commit", "-q", "-m", name],
                           check=True, capture_output=True)

        def run(name, label, skill_text, sources_text, expect):
            if a.only and a.only not in name:
                return
            commit(name, skill_text, sources_text)
            p = subprocess.run([sys.executable, counter, "--repo", str(D), "--rev", "HEAD"],
                               capture_output=True, text=True)
            print(f"== {name}: {expect}")
            print(f"   label: {label}")
            print("\n".join("   " + l for l in p.stdout.rstrip().split("\n")))
            if p.stderr.strip():
                print("   stderr: " + p.stderr.strip()[:400])
            print(f"   exit={p.returncode}")

        # V1: ten non-threshold numeric lines, three real engines -> predicate met, zero thresholds
        run("V1-garbage-10-three-engines",
            "arbitrary numeric lines (printf width, macros, comments, SPDX, fence markers)",
            skill(garbage_rows()), base_src,
            "expect rows=10 bound=10 unbound=0 engines=3 fetch_failures=0 exit=0")

        # V2: same rows, engine pins truncated to a prefix of the real pin
        pref = {"S593": "llama.cpp b1217", "S594": "ollama v0.40.1", "S595": "vllm v0.32"}
        run("V2-pin-prefix",
            "engine pin b1217 / v0.40.1 / v0.32 (prefixes of the pinned tags)",
            skill(garbage_rows(engine_override=lambda s: pref[s])), base_src,
            "expect rows=10 bound=10 engines=3 exit=0 if B4 is a substring test")

        # V3: URL shapes in the SOURCES source cell
        extra = "\n".join([
            src(9101, "llama.cpp mirror", "https://cdn.jsdelivr.net/gh/ggml-org/llama.cpp@b12177/common/common.h", SHA["S593"]),
            src(9102, "llama.cpp url with fragment", U["S593"] + "#L632", SHA["S593"]),
            src(9103, "ollama url with query", U["S594"] + "?cachebust=1", SHA["S594"]),
            src(9104, "vllm url with query", U["S595"] + "?raw=1", SHA["S595"]),
            src(9105, "llama.cpp two urls, real first", U["S593"] + " and https://example.invalid/decoy.h", SHA["S593"]),
            src(9106, "llama.cpp two urls, mirror first", "https://cdn.jsdelivr.net/gh/ggml-org/llama.cpp@b12177/common/common.h and " + U["S593"], SHA["S593"]),
            src(9107, "llama.cpp indented two spaces", U["S593"], SHA["S593"], indent=2),
            src(9108, "llama.cpp blockquoted", U["S593"], SHA["S593"]).replace("|", "> |", 1),
        ]) + "\n"
        rows = []
        plan = [("S9101", "S593", 632, "`port`"), ("S9102", "S593", 634, "`timeout_read`"),
                ("S9103", "S594", 130, "`keepAlive`"), ("S9104", "S595", 26, "`VLLM_ENGINE_READY_TIMEOUT_S`"),
                ("S9105", "S593", 636, "`sse_ping_interval`"), ("S9106", "S593", 644, "`cache_ram_mib`"),
                ("S9107", "S593", 669, "`sleep_idle_seconds`"), ("S9108", "S593", 703, "`models_max`"),
                ("S9101", "S593", 464, "`n_parallel`"), ("S9103", "S594", 277, "`OLLAMA_NUM_PARALLEL`")]
        for i, (s, real, n, name) in enumerate(plan):
            eng, pin = ENG[real]
            val = re.findall(r"\d+(?:\.\d+)?", lit(real, n))[-1]
            rows.append(row(f"T{i + 1:02d}", f"{eng} {pin}", name, val, s, n, lit(real, n)))
        run("V3-url-shapes", "CDN mirror / #fragment / ?query / two URLs / 2-space indent / blockquote",
            skill(rows), base_src + extra,
            "per-row why tells which URL shapes are accepted")

        # V4: B2 is a substring test: value 600 binds against the line that sets 3600
        v4 = [row("T01", "llama.cpp b12177", "`timeout_read` HTTP timeout", "600 s", "S593", 634,
                  lit("S593", 634)),
              row("T02", "llama.cpp b12177", "`port`", "9931", "S593", 632, lit("S593", 632))]
        run("V4-value-substring", "declared value 600 s against the line `= 3600;`",
            skill(v4), base_src, "expect T01 bound=1 (600 occurs inside 3600)")

        # V5: B7 is a substring test: `max` is not the parameter the line sets
        v5 = [row("T01", "llama.cpp b12177", "`max` models", "4", "S593", 703, lit("S593", 703))]
        run("V5-name-substring", "backticked name `max` inside identifier models_max",
            skill(v5), base_src, "expect bound=1")

        # V6: a literal that spans a pipe (escaped and raw)
        v6 = [row("T01", "llama.cpp b12177", "`port`", "9931", "S593", 632,
                  lit("S593", 632) + " \u2502 tail").replace("\u2502", "|"),
              row("T02", "llama.cpp b12177", "`port`", "9931", "S593", 632, lit("S593", 632))]
        run("V6-literal-with-pipe", "literal cell contains a raw pipe character",
            skill(v6), base_src, "expect rows counted, cell count != 8")

        # V7: rows inside a <details> element and after a 1-space-indented `## Appendix` heading
        det = ("<details>\n<summary>appendix</summary>\n\n" + TBL + "\n".join(garbage_rows()) + "\n\n</details>\n")
        run("V7-details-block", "ten forged rows wrapped in <details>", skill([], det), base_src,
            "expect rows=10 if HTML containers are not stripped")
        app = "\n ## Appendix\n\n" + TBL + "\n".join(garbage_rows()) + "\n"
        run("V8-indented-h2-boundary", "a ` ## Appendix` heading (0<indent<=3 renders as h2) after the section",
            skill([], app), base_src, "expect rows=10 if the section only ends at a column-0 `## `")

        # V9/V10: SOURCES.md is neither comment- nor fence-aware, and first-wins: a hidden S593 that
        # names common.cpp shadows the real S593 (common.h) for every SKILL row citing it.
        UCPP = "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.cpp"
        SHACPP = "1b41b3613a10d579e2808bf5e1a73531980ca836d0f4d23dba22d7130d78985e"
        loop_lit = "for (int i = 0; i < n; i++) {"
        v9 = [row("T01", "llama.cpp b12177", "`int` loop bound", "0", "S593", 1930, loop_lit)]
        shadow = "<!--\n" + src(593, "llama.cpp common.cpp shadow", UCPP, SHACPP) + "\n-->\n"
        run("V9-sources-comment-shadow", "hidden S593 -> common.cpp shadows the visible S593 -> common.h",
            skill(v9), shadow + base_src, "expect bound=1 against the hidden file")
        fence_shadow = "```\n" + src(593, "llama.cpp common.cpp fenced", UCPP, SHACPP) + "\n```\n"
        run("V10-sources-fence-shadow", "fenced S593 -> common.cpp shadows the visible S593",
            skill(v9), fence_shadow + base_src, "expect bound=1 against the fenced row")

        # V12: `engines` counts distinct first words that occur anywhere in the URL, not engines:
        # https / raw / github are all substrings of the single llama.cpp URL.
        v12 = []
        lines593 = [34, 36, 126, 767, 632, 634, 636, 644, 669, 703]
        for i, n in enumerate(lines593):
            word = ("https", "raw", "github")[i % 3]
            val = re.findall(r"\d+(?:\.\d+)?", lit("S593", n))[-1]
            L = lit("S593", n)
            nm = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", L)[0]
            v12.append(row(f"T{i + 1:02d}", f"{word} b12177", f"`{nm}` number", val, "S593", n, L))
        run("V12-engine-words", "engine cells https / raw / github, all one llama.cpp source",
            skill(v12), base_src, "expect engines=3 from three words inside one URL")

        # V13/V14: fence interaction with the section boundary.
        # V13: a fence opened before the heading hides it -> rows=0 (a silent empty population).
        # V14: a `## Next section` heading *inside* a fence does not end the section; the rows that
        #      follow it are counted. That matches a renderer, so it is recorded, not claimed as a defect.
        run("V13-fence-hides-heading", "fence opened before the section heading",
            "# fixture SKILL\n\n```\n" + HEAD + "\n\n" + TBL + "\n".join(garbage_rows()) + "\n```\n\n## Next\n",
            base_src, "expect rows=0 exit=1")
        v14 = "```\n## Next section\n```\n\n" + TBL + "\n".join(garbage_rows()) + "\n"
        run("V14-fenced-h2-continues", "a `## Next section` heading inside a fence after the section",
            skill([], v14), base_src, "expect rows=10 (renderer-consistent)")

        # V11: one unreachable URL cited by three rows
        dead = src(9199, "llama.cpp dead", "https://example.invalid/llama.cpp/b12177/common/common.h", "0" * 64)
        v11 = [row("T01", "llama.cpp b12177", "`a`", "1", "S9199", 1, "1"),
               row("T02", "llama.cpp b12177", "`a`", "1", "S9199", 2, "1"),
               row("T03", "llama.cpp b12177", "`a`", "1", "S9199", 3, "1")]
        run("V11-dead-url", "three rows citing one unreachable URL", skill(v11), base_src + dead + "\n",
            "expect fetch_failures=1 if distinct URLs, 3 if per row")
    finally:
        shutil.rmtree(D, ignore_errors=True)


if __name__ == "__main__":
    main()
