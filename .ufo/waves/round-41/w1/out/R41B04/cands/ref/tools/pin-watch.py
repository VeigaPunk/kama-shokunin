#!/usr/bin/env python3
"""R41B04 candidate pin-watch (ref) -- oracle by construction.

Delegates to the counter's own parse_pins/tag_names/reference (module at
$R41B04_AUDIT), so it cannot drift from the oracle the contract leg compares
against. Used as the self-consistency check for weakened fixtures: if `ref`
fails a variant, the weakening corrupted the fixture and that variant's
verdicts are inconclusive.
"""
import importlib.util
import os
import sys


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] != "check":
        print("usage: pin-watch.py check --pins FILE [--tags-dir DIR]", file=sys.stderr)
        return 2
    pins = tags_dir = None
    i = 1
    while i < len(args):
        if args[i] == "--pins" and i + 1 < len(args):
            i += 1
            pins = args[i]
        elif args[i] == "--tags-dir" and i + 1 < len(args):
            i += 1
            tags_dir = args[i]
        i += 1
    if pins is None:
        print("--pins required", file=sys.stderr)
        return 2
    spec = importlib.util.spec_from_file_location("r41b04_audit", os.environ["R41B04_AUDIT"])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open(pins, encoding="utf-8") as fh:
        rows = mod.parse_pins(fh.read())
    texts = {}
    if tags_dir is not None:
        for r in rows:
            try:
                with open(os.path.join(tags_dir, r["engine"] + ".txt"), encoding="utf-8") as fh:
                    texts[r["engine"]] = fh.read()
            except OSError:
                pass
    out, code = mod.reference(rows, texts)
    sys.stdout.write("".join(l + "\n" for l in out))
    return code


if __name__ == "__main__":
    sys.exit(main())
