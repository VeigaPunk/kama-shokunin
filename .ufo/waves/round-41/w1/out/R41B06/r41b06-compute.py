#!/usr/bin/env python3
"""R41B06 independent pin-watch reference.

Compute, from a `git ls-remote --tags` capture, for each pinned engine:
  - the newest release tag (greatest numeric version key; ties broken by
    lexicographic tag name, so the maximum is deterministic),
  - how many release tags have a key strictly greater than the lane's pin.
Only `refs/tags/<name>` refs count; peeled `^{}` lines and non-fullmatch
tags (post1/rc/heads/…) are ignored. Regexes are taken verbatim from
registry/engine-pins.tsv (vX.Y.Z fullmatch / bN fullmatch).

Usage: python3 r41b06-compute.py <engine> <regex> <pin> <ls-remote-file> [...]
"""
import re
import sys
from datetime import datetime, timezone


def release_tags(path: str, rx: re.Pattern) -> dict[str, tuple[int, ...]]:
    tags: dict[str, tuple[int, ...]] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            _oid, ref = line.split("\t", 1)
            if not ref.startswith("refs/tags/") or ref.endswith("^{}"):
                continue
            name = ref[len("refs/tags/"):]
            m = rx.fullmatch(name)
            if m:
                tags[name] = tuple(int(g) for g in m.groups())
    return tags


def main() -> int:
    print(f"utc={datetime.now(timezone.utc).strftime('%FT%TZ')}")
    for i in range(0, len(sys.argv) - 1, 4):
        engine, rxsrc, pin, path = sys.argv[1 + i:5 + i]
        rx = re.compile(rxsrc)
        tags = release_tags(path, rx)
        key = tags.get(pin)
        if key is None:
            newest = max(tags, key=lambda t: (tags[t], t)) if tags else "-"
            print(f"{engine}: pin={pin} missing=1 tags_total={len(tags)} "
                  f"newest={newest} newer=-")
            continue
        newer = sum(1 for k in tags.values() if k > key)
        newest = max(tags, key=lambda t: (tags[t], t))
        ordered = sorted(tags.items(), key=lambda kv: (kv[1], kv[0]))
        print(f"{engine}: pin={pin} newest={newest} newer={newer} "
              f"tags_total={len(tags)} status={'current' if newer == 0 else 'behind'} "
              f"top6={[t for t, _ in ordered[-6:]]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
