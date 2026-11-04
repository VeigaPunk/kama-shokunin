#!/usr/bin/env python3
"""Secret-shaped-string scanner for the SEN01 round-71 boundary audit.

Scope: every file under .ufo/waves/round-71 plus the 26 inherited round-70
paths listed in r70-26.txt.  Prints one line per hit (path:line, match
redacted to its first 6 chars) and a per-pattern total.  Read-only.
"""
import pathlib
import re
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = pathlib.Path(__file__).resolve().parent

STRONG = [
    ("openai-sk", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("github-ghp", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("github-gho", re.compile(r"gho_[A-Za-z0-9]{20,}")),
    ("github-pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("1password-op", re.compile(r"op://[^\s`'\"]{4,}")),
    ("aws-akia", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack-xox", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("pem-private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer-token", re.compile(r"Bearer\s+[A-Za-z0-9._-]{12,}")),
    ("authorization-header", re.compile(r"Authorization:\s*\S+")),
    ("cookie-header", re.compile(r"(?i)\bcookie\s*[:=]\s*\S+")),
    ("session-token", re.compile(r"(?i)session[ _-]?token\s*[:=]?\s*\S+")),
    ("api-key-assign", re.compile(r"(?i)api[_-]?key\s*[:=]\s*[^\s\"'`]{8,}")),
    ("secret-assign", re.compile(r"(?i)\bsecret\s*[:=]\s*[^\s\"'`]{8,}")),
    ("password-assign", re.compile(r"(?i)\bpassword\s*[:=]\s*[^\s\"'`]{6,}")),
]

r71 = []
for p in sorted((LANE / ".ufo/waves/round-71").rglob("*")):
    if p.is_file():
        r71.append(p)
files = []
files.extend(r71)
for line in (SCRATCH / "r70-26.txt").read_text().split("\n"):
    line = line.strip()
    if line:
        files.append(LANE / line)
files = sorted(set(files))

hits = 0
per = {name: 0 for name, _ in STRONG}
for f in files:
    try:
        data = f.read_bytes()
    except OSError as exc:
        print(f"UNREADABLE {f}: {exc}")
        continue
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        continue
    for i, row in enumerate(text.splitlines(), 1):
        for name, rx in STRONG:
            m = rx.search(row)
            if m:
                tok = m.group(0)
                shown = tok if len(tok) <= 6 else tok[:6] + "<redacted>"
                rel = f.relative_to(LANE) if f.is_relative_to(LANE) else f
                print(f"HIT {rel}:{i} [{name}] {shown}")
                hits += 1
                per[name] += 1

print(f"SCAN_FILES={len(files)} (round71={len(r71)} round70={len(files)-len(r71)}) PATTERNS={len(STRONG)} HITS={hits}")
for name, n in per.items():
    print(f"PATTERN {name} hits={n}")
sys.exit(0)
