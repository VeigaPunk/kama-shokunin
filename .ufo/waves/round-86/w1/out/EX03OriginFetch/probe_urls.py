#!/usr/bin/env python3
"""Per-URL receipt probe for round-86 C3: one read-only GET per unique anchor URL,
recording HTTP status, byte count, sha256, and an independent window comparison
against each anchor's stored body. URLs are exactly those named by the committed
anchor headers at the frozen base rev."""
import hashlib
import json
import re
import subprocess
import urllib.request

REPO = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = "3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d"
ANCHORS = [
    "llamacpp-b11755-health", "llamacpp-b12111-health", "llamacpp-39febd2a-router",
    "llamacpp-b12111-router", "llamacpp-b7200-health", "sglang-v0.5.22-health",
    "sglang-v0.5.23-health", "vllm-v0.32.0-prefix-caching", "vllm-v0.33.0-prefix-caching",
]
ANCHOR_RE = re.compile(r"^# url=(\S+) sha256=([0-9a-f]{64}) ref=(\S+) lines=([0-9]+)-([0-9]+)$")
UA = "kama-shokunin-pin-origin/1 (read-only documentary check)"

fetched = {}

out = []
for name in ANCHORS:
    text = subprocess.check_output(
        ["git", "-C", REPO, "show", f"{REV}:corpus/anchors/{name}.txt"],
        text=True, errors="surrogateescape")
    header, body = text.split("\n", 1)
    m = ANCHOR_RE.match(header)
    assert m, name
    url, digest, ref, start, end = m.group(1), m.group(2), m.group(3), int(m.group(4)), int(m.group(5))
    stored = body.encode("utf-8", errors="surrogateescape")
    rec = {
        "anchor": f"corpus/anchors/{name}.txt", "url": url, "ref": ref,
        "declared_lines": f"{start}-{end}",
        "declared_sha256": digest,
        "stored_body_bytes": len(stored),
        "stored_body_sha256": hashlib.sha256(stored).hexdigest(),
        "digest_matches_stored": hashlib.sha256(stored).hexdigest() == digest,
    }
    if url not in fetched:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                fetched[url] = {"http_status": resp.status, "upstream_bytes": len(data),
                                "upstream_sha256": hashlib.sha256(data).hexdigest(),
                                "_data": data}
        except Exception as exc:  # noqa: BLE001 - receipt records the failure
            fetched[url] = {"http_status": None, "error": repr(exc), "_data": None}
    rec.update({k: v for k, v in fetched[url].items() if k != "_data"})
    data = fetched[url]["_data"]
    if data is not None:
        lines = data.decode("utf-8", errors="surrogateescape").splitlines()
        if end > len(lines) or start < 1:
            rec["window_matches_stored"] = False
            rec["window_note"] = "range outside upstream"
        else:
            window = ("\n".join(lines[start - 1:end]) + "\n").encode("utf-8", errors="surrogateescape")
            rec["window_matches_stored"] = window == stored
    out.append(rec)

print(json.dumps(out, indent=2))
