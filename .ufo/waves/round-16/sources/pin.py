#!/usr/bin/env python3
"""Pin llama.cpp server sources at a fixed commit for kama-shokunin round 16.

Fetches four upstream files with read-only GETs from raw.githubusercontent.com,
saves them under ./llama.cpp-704366d/, and writes ./pins.json with per-file
url, sha256, byte count, and string-searched (never hardcoded) line ranges:

  - tools/server/README.md
      * the `### GET /health` section (heading line through the line before
        the next heading of level <= 3, or EOF)
      * the `Body: {"error": {"code": 503, "message": "Loading model",
        "type": "unavailable_error"}}` line
  - tools/server/server-http.cpp
      * the `auto middleware_server_state` block (start line through its
        closing `};` at the same indent)
  - tools/server/server-common.cpp
      * every `case ERROR_TYPE_UNAVAILABLE` line
      * every `ERROR_TYPE_UNAVAILABLE` use
  - tools/server/server-common.h
      * every `ERROR_TYPE_UNAVAILABLE` use
"""

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
SHORT = COMMIT[:7]
BASE_URL = f"https://raw.githubusercontent.com/ggml-org/llama.cpp/{COMMIT}"
ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / f"llama.cpp-{SHORT}"
PINS = ROOT / "pins.json"

FILES = [
    "tools/server/README.md",
    "tools/server/server-http.cpp",
    "tools/server/server-common.cpp",
    "tools/server/server-common.h",
]

LOADING_BODY_NEEDLE = '"code": 503, "message": "Loading model", "type": "unavailable_error"'
HEALTH_HEADING = "### GET `/health`"
MIDDLEWARE_START = "auto middleware_server_state"
CASE_UNAVAILABLE = "case ERROR_TYPE_UNAVAILABLE"
UNAVAILABLE_TOKEN = "ERROR_TYPE_UNAVAILABLE"


def fetch(path: str) -> bytes:
    url = f"{BASE_URL}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "kama-shokunin-source-pins"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        status = getattr(resp, "status", 200)
        if status != 200:
            raise RuntimeError(f"GET {url} -> HTTP {status}")
        return resp.read()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_substring_lines(lines: list, needle: str) -> list:
    """1-based line numbers of every line containing needle."""
    return [i + 1 for i, line in enumerate(lines) if needle in line]


def locate_health_section(lines: list) -> dict:
    """Heading line through line before the next level<=3 heading (or EOF)."""
    starts = [i for i, line in enumerate(lines) if line.strip().startswith(HEALTH_HEADING)]
    if not starts:
        return {"error": "heading not found"}
    start = starts[0]
    heading_re = re.compile(r"^#{1,3}\s")
    end = len(lines)  # inclusive 1-based EOF fallback, adjusted below
    for j in range(start + 1, len(lines)):
        if heading_re.match(lines[j]):
            end = j  # 0-based index of next heading == 1-based line before it
            break
    # trim trailing blank lines inside the section
    while end - 1 > start and lines[end - 1].strip() == "":
        end -= 1
    return {"start": start + 1, "end": end}


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip())


def locate_middleware_block(lines: list) -> dict:
    """`auto middleware_server_state` line through the closing `};` at same indent."""
    starts = [i for i, line in enumerate(lines) if MIDDLEWARE_START in line]
    if not starts:
        return {"error": "middleware_server_state not found"}
    start = starts[0]
    start_indent = indent_of(lines[start])
    end = None
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped in ("};", "};  // fallthrough") or (stripped.startswith("};") and indent_of(lines[j]) == start_indent):
            if indent_of(lines[j]) == start_indent or stripped == "};":
                end = j
                break
    if end is None:
        # fallback: first same-indent line ending a statement block
        for j in range(start + 1, len(lines)):
            if lines[j].strip() == "};" and indent_of(lines[j]) <= start_indent:
                end = j
                break
    if end is None:
        return {"start": start + 1, "error": "closing `};` not found"}
    return {"start": start + 1, "end": end + 1}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pins = {
        "commit": COMMIT,
        "base_url": BASE_URL,
        "output_dir": str(OUT_DIR),
        "files": {},
    }

    for path in FILES:
        url = f"{BASE_URL}/{path}"
        data = fetch(path)
        dest = OUT_DIR / Path(path).name
        dest.write_bytes(data)
        text = data.decode("utf-8")
        lines = text.split("\n")

        located = {}
        name = Path(path).name
        if name == "README.md":
            located["get_health_section"] = locate_health_section(lines)
            body_lines = find_substring_lines(lines, LOADING_BODY_NEEDLE)
            located["loading_model_body_line"] = (
                {"lines": body_lines} if body_lines else {"error": "body line not found"}
            )
        elif name == "server-http.cpp":
            located["middleware_server_state_block"] = locate_middleware_block(lines)
            uses = find_substring_lines(lines, UNAVAILABLE_TOKEN)
            if uses:
                located["error_type_unavailable_uses"] = uses
        elif name == "server-common.cpp":
            case_lines = find_substring_lines(lines, CASE_UNAVAILABLE)
            located["case_error_type_unavailable_lines"] = (
                case_lines if case_lines else {"error": "case label not found"}
            )
            uses = find_substring_lines(lines, UNAVAILABLE_TOKEN)
            located["error_type_unavailable_uses"] = (
                uses if uses else {"error": "no uses found"}
            )
        elif name == "server-common.h":
            uses = find_substring_lines(lines, UNAVAILABLE_TOKEN)
            located["error_type_unavailable_uses"] = (
                uses if uses else {"error": "no uses found"}
            )

        pins["files"][path] = {
            "url": url,
            "saved_as": str(dest),
            "sha256": sha256_hex(data),
            "bytes": len(data),
            "located": located,
        }

    PINS.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n")
    print(json.dumps(pins, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
