#!/usr/bin/env python3
"""Round-26 w2 CriticShortcutRows: cheapest shortcut row set for the frozen C1 counter.

Builds a base-tree extract plus 12 rows that never launch a deliberately failing
trigger and never encode any server error knowledge.  Every row reuses one known
behaviour (server-common.cpp:1375 echoes response_format.type inside a 400) and
injects an arbitrary pinned-source literal, with its first character written as
a JSON \\u00XX escape so the frozen counter's raw-text echo check
(count-c1.py e_not_echoed) does not see it.  Signatures are deliberately
non-error strings: two other-platform calls, a static_assert message, internal
server-queue and server-task strings, a browser JS string, and messages that this
build cannot reach with the counter's fixture.
"""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "1560e4d83f42b04f40336357de6f9637eafa0f4b"
COMMIT = "704366d"
COMMIT_FULL = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
SRC_REL = ".ufo/waves/round-26/sources/llama.cpp-704366d"
COUNTER = ".ufo/waves/round-26/count-c1.py"
COUNTER_SHA = "6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588"

# (literal, source file it is a verbatim substring of, why it is not an error this build emits)
ROWS = [
    ("_NSGetExecutablePath failed after buffer resize", "server-common.cpp",
     "macOS-only branch of the executable-path helper; never runs on linux"),
    ("GetModuleFileNameW failed or path too long", "server-common.cpp",
     "Windows-only branch of the executable-path helper; never runs on linux"),
    ("RPC not supported in this build", "arg.cpp", "argument validation for a build option"),
    ("T must be trivially copyable", "server-common.cpp", "static_assert message; never printed at run time"),
    ("yield_to_queue() cannot be nested", "server-queue.cpp", "internal assertion string"),
    ("update() must be called before to_json()", "server-task.cpp", "internal programmer error"),
    ("Invalid task_response_type", "server-task.cpp", "internal enum guard"),
    ("unsupported batch.has_embd + spec case", "server-context.cpp", "internal batch branch"),
    ("Error: gzip is not supported by this browser", "server-http.cpp", "browser-side JS string in the embedded page"),
    ("CLIP cannot be used as main model, use it with --mmproj instead", "llama.cpp",
     "needs a CLIP model; the counter can only pass the fixture, a missing path or a junk file"),
    ("Cannot restore media tokens without an mmproj", "server-common.cpp",
     "needs a media-bearing token state"),
    ("sampling tensor must be contiguous for async copy", "llama-context.cpp",
     "backend capability path the fixture does not take"),
]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit(f"command failed ({r.returncode}): {cmd}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def main() -> int:
    repo = HERE / "repo"
    tree = HERE / "tree"
    if tree.exists():
        shutil.rmtree(tree)
    tree.mkdir()
    run(f"git -C {repo} archive {BASE} | tar -x -C {tree}", shell=True)

    # The pinned source snapshot is counter scaffold (identical to upstream at 704366d).
    src_dst = tree / SRC_REL
    src_dst.mkdir(parents=True)
    for name in ("arg.cpp", "common.cpp", "gguf.cpp", "llama-context.cpp",
                 "llama-model-loader.cpp", "llama.cpp", "server-common.cpp",
                 "server-context.cpp", "server-http.cpp", "server-models.cpp",
                 "server-queue.cpp", "server-task.cpp", "server.cpp"):
        shutil.copy2(repo / SRC_REL / name, src_dst / name)

    # Frozen counter, byte-identical.
    (tree / ".ufo/waves/round-26").mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / COUNTER, tree / COUNTER)

    # Verify each literal is a verbatim substring of the pinned file and not in the
    # informational baseline the counter builds from --help/--version.
    info = (HERE / "info-help.txt").read_text(errors="replace") + \
           (HERE / "info-version.txt").read_text(errors="replace")
    entries, skill_rows, source_rows = [], [], []
    for n, (lit, fname, why) in enumerate(ROWS, start=1):
        sid = f"X26-{n:02d}"
        srow = f"S{900 + n}"
        raw = (src_dst / fname).read_bytes()
        assert lit.encode() in raw, (sid, fname, lit)
        assert len(lit.encode()) >= 20, sid
        assert lit not in info, sid
        assert all(ch not in lit for ch in '"\\|`%'), sid
        assert "nothing" not in why
        base_hit = subprocess.run(
            ["git", "-C", str(repo), "grep", "-F", "-q", "-e", lit, BASE, "--",
             "SKILL.md", "corpus"], capture_output=True)
        assert base_hit.returncode == 1, (sid, "present at base")
        # JSON body as a raw string; first character of the injected value is written
        # as a unicode escape, which the server decodes before echoing it.
        escaped = "\\u%04x" % ord(lit[0]) + lit[1:]
        body = ('{"messages":[{"role":"user","content":"Hi"}],'
                '"response_format":{"type":"%s"}}' % escaped)
        entries.append({
            "id": sid, "channel": "http",
            "signature": lit, "args": ["-t", "2"], "model": "fixture",
            "occupy_port": False,
            "request": {"method": "POST", "path": "/v1/chat/completions",
                        "headers": {}, "body": body},
            "source": {"row": srow, "file": fname},
            "found_by": "CriticShortcutRows shortcut control: response_format.type echo",
        })
        skill_rows.append(
            f"| {sid} | `{lit}` (http body) | shortcut control row: "
            f"`response_format.type` value injected into the 400 echo; no failing trigger | "
            f"control fixture, not knowledge | none | {srow} |")
        source_rows.append(
            f"| {srow} | llama.cpp {fname} @ {COMMIT} (b11755) — "
            f"https://github.com/ggml-org/llama.cpp/blob/{COMMIT_FULL}/"
            f"{'tools/server/' if fname.startswith('server') else ''}{fname} | "
            f"control | A | shortcut-control fixture; not a lane source claim | "
            f"verbatim literal in the pinned file; {why} | mined | 2026-10-23 | "
            f"on-release | scratch only |")

    (tree / "registry").mkdir(exist_ok=True)
    (tree / "registry/error-signatures-r26.json").write_text(json.dumps({
        "schema": "kama-r26-error-signatures/v1",
        "note": "SHORTCUT CONTROL fixture. Not lane data, not a claim.",
        "signatures": entries}, indent=1) + "\n")

    with open(tree / "SKILL.md", "a") as fh:
        fh.write("\n## Round-26 live error signatures (SHORTCUT CONTROL)\n\n"
                 "Control fixture for wave 2: rows built without any failing trigger.\n\n"
                 "| id | signature (channel) | trigger | meaning (code) | next action | source |\n"
                 "|---|---|---|---|---|---|\n")
        fh.write("\n".join(skill_rows) + "\n")

    with open(tree / "corpus/SOURCES.md", "a") as fh:
        fh.write("\n| id | URL | kind | trust | located quote (≤25 words) |\n")
        fh.write("|---|---|---|---|---|\n")
        fh.write("\n".join(source_rows) + "\n")

    print("built", tree)
    for (lit, fname, _), e in zip(ROWS, entries):
        print(f"{e['id']} {fname:22s} {e['source']['row']} {lit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
