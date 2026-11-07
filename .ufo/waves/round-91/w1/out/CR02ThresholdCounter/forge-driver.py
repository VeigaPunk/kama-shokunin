#!/usr/bin/env python3
"""CR02 C2 forgery battery: binds that are not honest thresholds.

Builds one fixture git repo (scratch only) with corpus/SOURCES.md copied from M2 and a
forged SKILL.md per variant, then runs the frozen counter bytes (F, fc304abd...) against
each commit. Every variant prints its label, the counter stdout and the exit code.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HEAD = "## Serving timeout and limit thresholds"
TABLE_HEAD = ("| id | engine pin | threshold | value | source | line | literal | probe decision |\n"
              "|---|---|---|---|---|---|---|---|\n")
LLAMA_URL = "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h"
OLLAMA_URL = "https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go"
VLLM_URL = "https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py"
SHA_LLAMA = "c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073"
SHA_OLLAMA = "0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895"
SHA_VLLM = "e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694"

# exact upstream line text (1-based numbers verified against the fetched bytes)
L126 = "  //COMMON_SAMPLER_TYPE_TFS_Z       = 5,"
L435 = "    // see: https://github.com/ggml-org/llama.cpp/pull/15408"
L884 = "        for (size_t len = max_len; len > 0; --len) {"
L632 = "    int32_t port                = 9931;          // server listens on this network port"
L634 = "    int32_t timeout_read        = 3600;          // http read timeout in seconds"
L636 = "    int32_t sse_ping_interval   = 30;            // SSE ping interval in seconds"
L644 = "    int32_t cache_ram_mib       = 8192;  // -1 = no limit, 0 - disable, 1 = 1 MiB, etc."
L669 = "    int sleep_idle_seconds = -1;"
L703 = "    int models_max = 4;"
L464 = "    int32_t n_parallel            =     1; // number of parallel sequences to decode"
O21 = '// Default is scheme "http" and host "127.0.0.1:11434"'
O128 = "// Default is 5 minutes."
V382 = '        if is_torch_equal_or_newer("2.10.0") and not disable_compile_cache()'


def g(D, *args):
    subprocess.run(["git", "-C", str(D), *args], check=True, capture_output=True)


def skill(rows, extra=""):
    return ("# fixture SKILL\n\n" + HEAD + "\n\n" + TABLE_HEAD + "\n".join(rows) + "\n"
            + extra + "\n## Next\n")


def src_row(sid, cell, sha, tier="A", status="mined"):
    return (f"| {sid} | {cell} | code | {tier} | fixture | sha256 {sha} | fixture | "
            f"{status} | 2026-11-06 | on-release | fixture |")


def llama_row(rid, pin, name, value, line, literal, decision="forged"):
    return (f"| {rid} | {pin} | {name} | {value} | S593 | {line} | `{literal}` | {decision} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--sources", required=True)
    ap.add_argument("--counter", required=True)
    a = ap.parse_args()
    base = Path(a.scratch)
    base.mkdir(parents=True, exist_ok=True)
    D = Path(tempfile.mkdtemp(prefix="c2-forge-", dir=base)).resolve()
    try:
        g(D, "init", "-q")
        top = subprocess.run(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert Path(top).resolve() == D, (top, D)
        (D / "corpus").mkdir()
        src = Path(a.sources).read_text()
        (D / "corpus/SOURCES.md").write_text(src)

        decoy_c = src_row("S593", f"llama.cpp common/common.h decoy — {LLAMA_URL}", SHA_LLAMA,
                          tier="C") + "\n"
        extras = {
            "frag": src_row("S9101", f"llama.cpp common/common.h at b12177 — {LLAMA_URL}#L632",
                            SHA_LLAMA),
            "query": src_row("S9102", f"llama.cpp common/common.h at b12177 — {LLAMA_URL}?x=1",
                             SHA_LLAMA),
            "two1": src_row("S9103", f"llama.cpp common/common.h b12177 — {LLAMA_URL} "
                                      "https://raw.githubusercontent.com/ggml-org/llama.cpp/master/common/common.h",
                            SHA_LLAMA),
            "two2": src_row("S9104", "llama.cpp common/common.h b12177 — "
                                      "https://raw.githubusercontent.com/ggml-org/llama.cpp/master/common/common.h "
                                      + LLAMA_URL, SHA_LLAMA),
            "absent": src_row("S9105", "llama.cpp common/common.h b12177 — "
                                       "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/no-such-file.h",
                              SHA_LLAMA),
        }
        variants = []

        def legit():
            return llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632)

        variants.append(("G0-legit-control", "expect rows=1 bound=1", skill([legit()])))
        variants.append(("G1-commented-enum-line", "line 126 is commented-out code, not a default",
                         skill([llama_row("T01", "llama.cpp b12177",
                                          "`COMMON_SAMPLER_TYPE_TFS_Z`", "5", 126, L126)])))
        variants.append(("G2-loop-bound", "line 884 is a loop condition, not a default",
                         skill([llama_row("T01", "llama.cpp b12177", "`max_len`", "0", 884, L884)])))
        variants.append(("G3-pr-number-comment", "line 435 is a PR-link comment, value is an issue id",
                         skill([llama_row("T01", "llama.cpp b12177", "`pull`", "15408", 435, L435)])))
        variants.append(("G4-ollama-host-comment", "ollama line 21 comment: host string, not a threshold",
                         skill([f"| T01 | ollama v0.40.11 | `Default` | 11434 | S594 | 21 | `{O21}` | forged |"])))
        variants.append(("G5-ollama-doc-comment", "ollama line 128 is the doc comment, not the assignment",
                         skill([f"| T01 | ollama v0.40.11 | `Default` | 5 | S594 | 128 | `{O128}` | forged |"])))
        variants.append(("G6-version-string", "vllm line 382 is a torch version test, not a default",
                         skill([f"| T01 | vllm v0.32.0 | `is_torch_equal_or_newer` | 2.10 | S595 | 382 | `{V382}` | forged |"])))
        variants.append(("G7-name-is-type", "backticked name is the C type, not the parameter",
                         skill([llama_row("T01", "llama.cpp b12177", "`int32_t`", "9931", 632, L632)])))
        variants.append(("G8-name-is-value", "backticked name is the value itself",
                         skill([llama_row("T01", "llama.cpp b12177", "`9931`", "9931", 632, L632)])))
        variants.append(("G9-value-substring", "value 99 is only a substring of 9931",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "99", 632, L632)])))
        variants.append(("G10-pin-prefix-b1217", "engine pin b1217 is a prefix of b12177",
                         skill([llama_row("T01", "llama.cpp b1217", "`port`", "9931", 632, L632)])))
        variants.append(("G11-pin-degenerate-1", "engine pin 1 is any digit in the URL",
                         skill([llama_row("T01", "llama.cpp 1", "`port`", "9931", 632, L632)])))
        variants.append(("G12-url-fragment", "S9101 URL carries #L632 fragment",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632)
                                .replace("| S593 |", "| S9101 |")])))
        variants.append(("G13-url-query", "S9102 URL carries a query string",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632)
                                .replace("| S593 |", "| S9102 |")])))
        variants.append(("G14-two-urls-first-pinned", "S9103 names pinned then master URL; second unchecked",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632)
                                .replace("| S593 |", "| S9103 |")])))
        variants.append(("G15-two-urls-first-moving", "S9104 first URL is master (expect moving-ref)",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632)
                                .replace("| S593 |", "| S9104 |")])))
        variants.append(("G16-literal-spans-pipe", "literal contains a pipe (row splits to 9 cells)",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632,
                                          L632 + " a|b")])))
        variants.append(("G17-details-block", "row inside <details> counted?",
                         skill([legit()], "<details>\n<summary>x</summary>\n\n"
                          + llama_row("T02", "llama.cpp b12177", "`timeout_read`", "3600", 634, L634)
                          + "\n\n</details>\n")))
        variants.append(("G18-fenced-heading", "T90 in fence, T91 after fence, T92 after real ## Next",
                         skill([legit()], "```\n## Fake heading\n"
                          + llama_row("T90", "llama.cpp b12177", "`port`", "9931", 632, L632)
                          + "\n```\n"
                          + llama_row("T91", "llama.cpp b12177", "`timeout_read`", "3600", 634, L634)
                          + "\n\n## Next\n\n"
                          + llama_row("T92", "llama.cpp b12177", "`port`", "9931", 632, L632))))
        variants.append(("G19-indented-quoted", "1-3 leading spaces and blockquote rows",
                         skill([legit(),
                                " " + llama_row("T02", "llama.cpp b12177", "`timeout_read`", "3600", 634, L634),
                                "  " + llama_row("T03", "llama.cpp b12177", "`port`", "9931", 632, L632),
                                "   " + llama_row("T04", "llama.cpp b12177", "`port`", "9931", 632, L632),
                                "> " + llama_row("T05", "llama.cpp b12177", "`port`", "9931", 632, L632)])))
        variants.append(("G20-fetch-absent", "S9105 URL 404: expect fetch_failures=1",
                         skill([llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632)
                                .replace("| S593 |", "| S9105 |")])))
        variants.append(("G21-duplicate-source-decoy-first",
                         "decoy S593 (tier C, real URL) prepended: legitimate rows shadowed",
                         skill([legit()])))
        ten = [
            llama_row("T01", "llama.cpp b12177", "`port`", "9931", 632, L632),
            llama_row("T02", "llama.cpp b12177", "`timeout_read`", "3600", 634, L634),
            llama_row("T03", "llama.cpp b12177", "`sse_ping_interval`", "30", 636, L636),
            llama_row("T04", "llama.cpp b12177", "`cache_ram_mib`", "8192", 644, L644),
            llama_row("T05", "llama.cpp b12177", "`sleep_idle_seconds`", "1", 669, L669),
            llama_row("T06", "llama.cpp b12177", "`models_max`", "4", 703, L703),
            llama_row("T07", "llama.cpp b12177", "`n_parallel`", "1", 464, L464),
            llama_row("T08", "raw.githubusercontent.com b12177", "`COMMON_SAMPLER_TYPE_TFS_Z`", "5", 126, L126),
            llama_row("T09", "raw.githubusercontent.com b12177", "`max_len`", "0", 884, L884),
            llama_row("T10", "githubusercontent.com b12177", "`pull`", "15408", 435, L435),
        ]
        variants.append(("G22-engine-diversity-forgery",
                         "10 rows, one file, three URL-substring engine labels: expect exit 0",
                         skill(ten)))
        for name, label, text in variants:
            (D / "SKILL.md").write_text(text)
            (D / "corpus/SOURCES.md").write_text(src + "\n".join(extras.values()) + "\n")
            if name == "G21-duplicate-source-decoy-first":
                (D / "corpus/SOURCES.md").write_text(decoy_c + src + "\n".join(extras.values()) + "\n")
            g(D, "add", "-A")
            g(D, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-q", "-m", name)
            p = subprocess.run([sys.executable, a.counter, "--repo", str(D), "--rev", "HEAD"],
                               capture_output=True, text=True)
            print(f"== {name}: {label}")
            print(p.stdout.rstrip())
            print(f"exit={p.returncode}")
    finally:
        shutil.rmtree(D, ignore_errors=True)


if __name__ == "__main__":
    main()
