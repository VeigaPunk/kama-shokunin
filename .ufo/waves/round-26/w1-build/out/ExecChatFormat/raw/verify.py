#!/usr/bin/env python3
import subprocess, hashlib, pathlib, sys

SRC = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/server-common.cpp")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "1560e4d83f42b04f40336357de6f9637eafa0f4b"
PINSHA = "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442"

SIGS = [
 ("A", 1386, "'messages' is required"),
 ("B", 1390, "Expected 'messages' to be an array"),
 ("C", 1395, "All non-assistant messages must contain 'content'"),
 ("D", 1399, "Assistant message must contain either 'content' or 'tool_calls'!"),
 ("E", 1411, "Expected 'content' to be a string or an array"),
 ("F", 1302, "unsupported content[].type"),
 ("H", 1375, "response_format type must be one of "),
 ("I", 1343, "tools param requires --jinja flag"),
 ("J", 1346, "tool_choice param requires --jinja flag"),
 ("K", 1360, "Cannot use both json_schema and grammar"),
 ("L", 1473, "(expected boolean, got string)"),
 ("M", 1434, "Cannot have 2 or more assistant messages at the end of the list."),
 ("N", 1440, "Cannot set both add_generation_prompt and continue_final_message to true."),
 ("O", 1446, "Cannot continue an assistant message that contains tool calls."),
 ("P", 1521, "top_logprobs requires logprobs to be set to true"),
 ("T", 1455, "Cannot use custom grammar constraints with tools."),
 ("U", 1517, "logprobs is not supported with tools + stream"),
]

src = SRC.read_bytes()
print("SRC sha256:", hashlib.sha256(src).hexdigest(), "pinned:", PINSHA)
ok = True
for tag, line, sig in SIGS:
    b = sig.encode()
    in_src = b in src
    # line presence check: source line text contains sig
    lines = src.decode("utf-8", "replace").splitlines()
    in_line = sig in (lines[line-1] if line-1 < len(lines) else "")
    r = subprocess.run(["git","-C",LANE,"grep","-F","-q","-e",sig,BASE,"--","SKILL.md","corpus"], capture_output=True)
    absent_base = r.returncode != 0
    print(f"[{tag}] len={len(b):3d} in_src={in_src} line{line}_has={in_line} absent_at_base={absent_base}")
    ok = ok and in_src and in_line and absent_base and len(b) >= 20
print("ALL_CHECKS_PASS" if ok else "SOME_CHECKS_FAILED")
