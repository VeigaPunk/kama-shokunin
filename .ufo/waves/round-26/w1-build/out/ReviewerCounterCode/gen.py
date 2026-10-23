#!/usr/bin/env python3
"""Build scratch trees (copies of the a23c0e04 extract) with falsifier row sets."""
import json
import shutil
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r26/ReviewerCounterCode")
PRISTINE = S / "pristine"
URL = "https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/"
PATHS = {
    "arg.cpp": "common/arg.cpp", "common.cpp": "common/common.cpp", "llama.cpp": "src/llama.cpp",
    "server.cpp": "tools/server/server.cpp", "server-context.cpp": "tools/server/server-context.cpp",
}


def esc_first(lit: str) -> str:
    return '{"messages":[{"role":"user","content":"Hi"}],"response_format":{"type":"' + \
        "\\u%04x" % ord(lit[0]) + lit[1:] + '"}}'


def build(name: str, rows: list[dict], extra_skill: str = "", src_override: dict | None = None):
    t = S / name
    if t.exists():
        shutil.rmtree(t)
    shutil.copytree(PRISTINE, t, symlinks=True)
    (t / "registry").mkdir(exist_ok=True)
    reg = {"signatures": [r["entry"] for r in rows]}
    (t / "registry/error-signatures-r26.json").write_text(json.dumps(reg, indent=1) + "\n")
    lines = ["", "## Round-26 live error signatures", "",
             "| Id | Signature | Source |", "|---|---|---|"]
    sub = []
    for r in rows:
        e = r["entry"]
        line = f"| {e['id']} | `{e['signature']}` | {e['source']['row']} |"
        if r.get("skill") == "backtick-id":
            line = f"| `{e['id']}` | `{e['signature']}` | {e['source']['row']} |"
        if r.get("skill") == "subheading":
            sub.append(line)
            continue
        if r.get("skill") != "none":
            lines.append(line)
    if sub:
        lines += ["", "### Rows under a subheading of the same section", "",
                  "| Id | Signature | Source |", "|---|---|---|"] + sub
    with open(t / "SKILL.md", "a") as f:
        f.write("\n".join(lines) + "\n" + extra_skill)
    src_lines = []
    seen = set()
    for r in rows:
        e = r["entry"]
        srow = e["source"]["row"]
        if srow in seen:
            continue
        seen.add(srow)
        fname = (src_override or {}).get(srow, e["source"]["file"])
        src_lines.append(f"| {srow} | {URL}{PATHS.get(fname, fname)}#L1 | scratch falsifier row, accessed 2026-10-23 |")
    with open(t / "corpus/SOURCES.md", "a") as f:
        f.write("\n" + "\n".join(src_lines) + "\n")
    return t


def startup(i, sig, args, model, src, srow, **kw):
    return {"entry": {"id": i, "channel": "startup", "signature": sig, "args": args, "model": model,
                      "occupy_port": False, "source": {"row": srow, "file": src}}, **kw}


def httpr(i, sig, body, src, srow, path="/v1/chat/completions", args=None, **kw):
    return {"entry": {"id": i, "channel": "http", "signature": sig, "args": args or [], "model": "fixture",
                      "occupy_port": False,
                      "request": {"method": "POST", "path": path, "headers": {}, "body": body},
                      "source": {"row": srow, "file": src}}, **kw}


def run_a():
    fx = S / "fixtures"
    fx.mkdir(exist_ok=True)
    t1 = fx / "tmpl-if.jinja"
    t1.write_text("{% if %}Restored prompt does not fit in the slot context\n")
    t2 = fx / "tmpl-endfor.jinja"
    t2.write_text("{{ 'a' }} No available space in KV cache or invalid slot save file {% endfor %}\n")
    rows = [
        startup("RA01", "--defrag-thold is deprecated and no longer necessary to specify",
                ["-dt", "0.1"], "missing", "arg.cpp", "S951"),
        startup("RA02", "--connect-code is ignored without --connect",
                ["--connect-code", "abc123"], "missing", "server.cpp", "S952"),
        startup("RA03", "embeddings enabled with n_batch (",
                ["--embedding", "-b", "1024", "-ub", "256"], "missing", "server.cpp", "S953"),
        startup("RA04", "failed to load model", [], "missing", "common.cpp", "S954"),
        httpr("RA05", "Cannot run multiple aLoRAs in a single request",
              esc_first("Cannot run multiple aLoRAs in a single request"), "server-context.cpp", "S955"),
        httpr("RA06", "failed to reload model after sleeping",
              esc_first("failed to reload model after sleeping"), "server-context.cpp", "S956"),
        startup("RA07", "Restored prompt does not fit in the slot context",
                ["--chat-template-file", str(t1)], "fixture", "server-context.cpp", "S957"),
        startup("RA08", "No available space in KV cache or invalid slot save file",
                ["--chat-template-file", str(t2)], "fixture", "server-context.cpp", "S958"),
        startup("RA09", "failed to load model",
                ["--log_file", str(S / "runA-log_file-bypass.txt")], "missing", "common.cpp", "S959"),
        startup("RA10", "failed to load model", ["-t", "3"], "missing", "common.cpp", "S960",
                skill="backtick-id"),
        startup("RA11", "failed to load model", ["-t", "4"], "missing", "common.cpp", "S961",
                skill="subheading"),
        startup("RA12", "error loading model vocabulary: ",
                ["-t", "5"], "missing", "llama.cpp", "S962"),
        startup("RA13", "Setting the split mode has no effect.",
                ["-sm", "none"], "missing", "arg.cpp", "S963"),
        startup("RA14", "no usable GPU found, --gpu-layers option will be ignored",
                ["-ngl", "1"], "missing", "arg.cpp", "S964"),
    ]
    # RA12: the SOURCES row names server-context.cpp only; its URL still contains "llama.cpp"
    build("runA", rows, src_override={"S962": "server-context.cpp"})


def run_b():
    rows = [startup(f"RB{i:02d}", "failed to load model", ["-t", str(i)], "missing", "common.cpp",
                    f"S{970 + i}") for i in range(1, 21)]
    build("runB", rows)


def run_c():
    rows = [startup("RC01", "failed to load model", [], "missing", "common.cpp", "S951"),
            startup("RC02", "failed to load model", ["--path", "/tmp"], "missing", "common.cpp", "S952")]
    build("runC", rows)


def run_e():
    rows = [startup("RE04", "failed to load model", [], "missing", "common.cpp", "S954"),
            startup("RE01", "--defrag-thold is deprecated and no longer necessary to specify",
                    ["-dt", "0.1"], "missing", "arg.cpp", "S951"),
            startup("RE03", "embeddings enabled with n_batch (",
                    ["--embedding", "-b", "1024", "-ub", "256"], "missing", "server.cpp", "S953")]
    build("runE", rows)


def run_f():
    rows = [startup("RF01", "--defrag-thold is deprecated and no longer necessary to specify",
                    ["-dt", "0.1"], "missing", "arg.cpp", "S951")]
    build("runF", rows)


def run_d():
    r = startup("RD01", "failed to load model", [], "missing", "common.cpp", "S951")
    del r["entry"]["channel"]
    build("runD", [r])


if __name__ == "__main__":
    for n in sys.argv[1:]:
        globals()[f"run_{n}"]()
