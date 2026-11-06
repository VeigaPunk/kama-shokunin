#!/usr/bin/env python3
"""MT02 mutant generator — round 91 wave w1a2.

Applies single-point textual mutants to the frozen C2 counter
(tools/round91-threshold-rows.py, sha256 fc304abd51135d464c402672c4c894bcff9b1bbe6b7c1565e7d6cf833f109661)
and writes one file per mutant plus a hash manifest.

Usage: mt02-mutants.py --counter <frozen counter> --out <mutants dir>

Every mutant is one rule removed or one literal changed; no mutant touches more than one rule.
The generator asserts each (old, new) occurs exactly once in the frozen bytes, so a drifted
counter fails loudly instead of silently producing a no-op mutant.
"""
import argparse
import hashlib
from pathlib import Path

FROZEN_SHA = "fc304abd51135d464c402672c4c894bcff9b1bbe6b7c1565e7d6cf833f109661"

# label -> (required_by_ticket, old, new)
MUTANTS = {
    "M01-drop-B2-value-in-literal": (True,
        '    nums = NUM_RE.findall(value)\n'
        '    if not nums or not any(n in lit for n in nums):\n'
        '        return False, "value-not-in-literal", None\n',
        '    nums = NUM_RE.findall(value)\n'),
    "M02-drop-B4-moving-ref": (True,
        '    if any(x in url for x in MOVING):\n'
        '        return False, "moving-ref", None\n',
        '    pass\n'),
    "M03-drop-pin-check": (True,
        '    pin = engine.split()[-1]\n'
        '    if pin not in url:\n'
        '        return False, "pin-not-in-url", None\n',
        '    pass\n'),
    "M04-drop-engine-check": (True,
        '    if engine.split()[0].lower() not in url.lower():\n'
        '        return False, "engine-not-in-url", None\n',
        '    pass\n'),
    "M05-sha-compare-removed": (True,
        '    if hashlib.sha256(body).hexdigest() != h.group(1):\n'
        '        return False, "sha-mismatch", None\n',
        '    pass\n'),
    "M06-line-off-by-one": (True,
        '    if not 1 <= n <= len(lines) or lit not in lines[n - 1]:\n',
        '    if not 1 <= n <= len(lines) or lit not in lines[n - 2]:\n'),
    "M07-comment-stripping-disabled": (True,
        '        while "<!--" in line:\n',
        '        while False:\n'),
    "M08-fence-detection-disabled": (True,
        '        if s.startswith("```") or s.startswith("~~~"):\n',
        '        if False:\n'),
    "M09-duplicate-rule-removed": (True,
        '        if rid in seen_id or (pair and pair in seen_pair):\n'
        '            dup += 1\n'
        '            print(f"THRESHOLD_ROW {rid} bound=0 why=duplicate")\n'
        '            continue\n',
        '        pass\n'),
    "M10-B7-removed": (True,
        '    names = [t for t in re.findall(r"`([^`]+)`", _name) if len(t) >= 3]\n'
        '    if not any(t in lit for t in names):\n'
        '        return False, "name-not-in-literal", None\n',
        '    pass\n'),
    "M11-MIN_ENGINES-3-to-1": (True,
        'MIN_ENGINES = 3\n',
        'MIN_ENGINES = 1\n'),
    "M12-MIN_ROWS-10-to-0": (False,
        'MIN_ROWS = 10\n',
        'MIN_ROWS = 0\n'),
    "M13-row-re-allows-indent": (False,
        'ROW_RE = re.compile(r"^\\| *(T\\d+) *\\|")\n',
        'ROW_RE = re.compile(r"^ *\\| *(T\\d+) *\\|")\n'),
    "M14-heading-prefix-match": (False,
        '            inside = line.rstrip() == HEAD\n',
        '            inside = line.startswith(HEAD)\n'),
    "M15-src-re-any-indent": (False,
        'SRC_RE = re.compile(r"^ {0,3}\\| *(S\\d{3,}) *\\|")\n',
        'SRC_RE = re.compile(r"^ *\\| *(S\\d{3,}) *\\|")\n'),
    "M16-duplicate-pair-check-dropped": (False,
        '        if rid in seen_id or (pair and pair in seen_pair):\n',
        '        if rid in seen_id:\n'),
    "M17-url-rstrip-dropped": (False,
        '    url = m.group(0).rstrip(").,;")\n',
        '    url = m.group(0)\n'),
    "M18-tier-check-dropped": (False,
        '    if status != "mined" or tier not in ("A", "B"):\n',
        '    if status != "mined":\n'),
    "M19-empty-cell-check-removed": (False,
        '    if any(not c or c == "-" for c in cells):\n',
        '    if False:\n'),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src_path = Path(a.counter)
    src = src_path.read_text()
    digest = hashlib.sha256(src_path.read_bytes()).hexdigest()
    if digest != FROZEN_SHA:
        raise SystemExit(f"counter drifted: {digest} != frozen {FROZEN_SHA}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for label, (_req, old, new) in MUTANTS.items():
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: old snippet occurs {n} times, expected 1")
        mutated = src.replace(old, new, 1)
        if mutated == src:
            raise SystemExit(f"{label}: mutation is a no-op")
        p = out / f"{label}.py"
        p.write_text(mutated)
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest.append(f"{label}\t{h}\t{'ticket-required' if _req else 'extra-depth'}")
        print(f"{label}\t{h}\t{'ticket-required' if _req else 'extra-depth'}")
    (out / "MUTANTS.sha256").write_text("\n".join(manifest) + "\n")
    print(f"wrote {len(MUTANTS)} mutants to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
