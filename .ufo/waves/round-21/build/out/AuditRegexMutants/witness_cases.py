#!/usr/bin/env python3
"""Isolated token-extraction witnesses; never edits the selected audit module."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("audit_under_test", args.target)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    direct = {
        "M01": (lambda: audit.FULL.findall("f" * 39), []),
        "M02": (lambda: audit.FULL.findall("f" * 40), ["f" * 40]),
        "M03": (lambda: audit.FULL.findall("g" + "f" * 40), []),
        "M04": (lambda: audit.FULL.findall("f" * 40 + "g"), []),
        "M05": (lambda: audit.ABBREV.findall("f" * 7), ["f" * 7]),
        "M06": (lambda: audit.ABBREV.findall("f" * 6), []),
        "M07": (lambda: audit.ABBREV.findall("f" * 40), ["f" * 40]),
        "M08": (lambda: audit.ABBREV.findall("g" + "f" * 7), []),
        "M09": (lambda: audit.ABBREV.findall("f" * 7 + "g"), []),
        "M10": (lambda: audit.landed_section(
            "## Landed changes\nx\n## End\ny\n"), "x\n"),
        "M11": (lambda: audit.landed_section(
            "prefix ## Landed changes\nx\n"), None),
        "M12": (lambda: audit.landed_section(
            "## Landed changes (commits)\nx\n"), "x\n"),
    }
    if args.case in direct:
        thunk, expected = direct[args.case]
        actual = thunk()
    else:
        fixtures = {
            "M13": ("round-10: other round", "kama-shokunin", False),
            "M14": ("checkpoint(r1)", "kama-shokunin", True),
            "M15": ("round-1:work", "kama-shokunin", True),
            "M16": ("checkpoint(r1)", "kama-shokunin", True),
            "M17": ("round-1: foreign author", "someone", False),
            "M18": ("round-1: author collision", "kama-shokunin-extra", False),
        }
        subject, author, expected = fixtures[args.case]
        with tempfile.TemporaryDirectory(prefix="kama-r21-token-witness-") as tmp:
            repo = Path(tmp)
            audit._sh(repo, "init", "-q", "-b", "master")
            audit._commit(repo, subject, author, 1000)
            actual = bool(audit.round_commits(repo, "master", "kama", 1))
    ok = actual == expected
    print(json.dumps({"case": args.case, "expected": expected,
                      "actual": actual, "status": "PASS" if ok else "FAIL"},
                     sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
