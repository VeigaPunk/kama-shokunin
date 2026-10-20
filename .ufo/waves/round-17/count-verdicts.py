#!/usr/bin/env python3
"""count-verdicts.py — count VERDICT tokens across a directory of advice reports.

Usage:
    count-verdicts.py ADVICE_DIR [--expect-names FILE.json] [--json]
    count-verdicts.py --selftest
    count-verdicts.py --help

For every *.md file in ADVICE_DIR (non-recursive; basenames matching
`swarm-registry*` are excluded), the first non-empty line is read and
classified:

    VERDICT: confirm|partial|refute|n/a [<sep><free text>]

* `VERDICT:` must start the raw line (no leading whitespace) and is
  case-sensitive.
* The token is lowercase, exactly one of confirm, partial, refute, n/a.
* After the token the line must end, or continue with a separator —
  one of U+2014 EM DASH, -, : (optional surrounding spaces) — followed by
  any free text. `VERDICT: confirm words…` with no separator is
  nonconformant.
* Any other first non-empty line, and any file with no non-empty line at
  all, classifies the file as `nonconformant`.

`--expect-names FILE.json` loads a wave spec.json and compares
`items[].name` against the *.md stems present: expected names with no file
are reported as `missing`; present files with no expected name are
reported as `unexpected` (informational only).

Exit codes: 0 when counting completed (any verdict mix); 2 when the advice
directory or the expected-names file cannot be read/parsed, or when any
scanned *.md file is unreadable (unreadable files are listed and counting
still completes).

`--json` emits one JSON object on stdout; otherwise a human-readable
summary is printed. `--selftest` exercises the classifier and
expected-name logic in a temporary directory and exits 0 on pass.

Design notes / limitations:
* Only the FIRST non-empty line is considered. A `VERDICT:` appearing
  later in the file does not classify the file (round-16 build advice put
  verdicts on line 3; this tool deliberately reports those as
  nonconformant so the misplaced line is visible, not silently counted).
* Separators other than —, -, : (e.g. `(`, `—` variants like `‒`/`–`)
  are not accepted; a file using one is nonconformant.
* Blank/whitespace-only lines before the verdict are skipped; a BOM is
  NOT stripped, so a BOM-prefixed file is nonconformant.
* stdlib only; no third-party dependencies.
"""

import argparse
import json
import os
import re
import sys
import tempfile

VERDICT_RE = re.compile(
    r"^VERDICT:[ \t]+(confirm|partial|refute|n/a)(?:[ \t]*[\u2014\-:].*)?$"
)
VERDICTS = ("confirm", "partial", "refute", "n/a")


def classify_line(line):
    """Return a verdict token or None for a raw first-non-empty line."""
    m = VERDICT_RE.match(line.rstrip("\r\n"))
    return m.group(1) if m else None


def classify_file(path):
    """Return (category, detail). category in VERDICTS + nonconformant.

    Raises OSError if the file cannot be read.
    """
    first = None
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if raw.strip():
                first = raw.rstrip("\r\n")
                break
    if first is None:
        return "nonconformant", "(empty file)"
    token = classify_line(first)
    if token is None:
        return "nonconformant", first[:80]
    return token, first[:80]


def load_expected_names(path):
    """Return the ordered list of items[].name from a spec.json.

    Accepts {"items": [{"name": ...}, ...]} or a bare list whose elements
    are strings or {"name": ...} objects.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("expected-names JSON has no items[] list")
    names = []
    for i, it in enumerate(items):
        if isinstance(it, str):
            names.append(it)
        elif isinstance(it, dict) and isinstance(it.get("name"), str):
            names.append(it["name"])
        else:
            raise ValueError("items[%d] has no string name" % i)
    return names


def run(advice_dir, expect_path):
    """Scan and return the result dict plus the exit code."""
    if not os.path.isdir(advice_dir):
        return {"error": "advice directory not found: %s" % advice_dir}, 2

    counts = {v: 0 for v in VERDICTS}
    counts["nonconformant"] = 0
    nonconformant = []
    unreadable = []
    stems = set()
    md_files = []

    try:
        entries = sorted(os.listdir(advice_dir))
    except OSError as exc:
        return {"error": "advice directory unreadable: %s" % exc}, 2

    for base in entries:
        if not base.endswith(".md"):
            continue
        if base.startswith("swarm-registry"):
            continue
        path = os.path.join(advice_dir, base)
        if not os.path.isfile(path):
            continue
        md_files.append(base)
        stems.add(base[:-3])
        try:
            cat, detail = classify_file(path)
        except OSError as exc:
            unreadable.append({"file": base, "error": str(exc)})
            continue
        counts[cat] += 1
        if cat == "nonconformant":
            nonconformant.append({"file": base, "first_line": detail})

    result = {
        "advice_dir": advice_dir,
        "files": len(md_files),
        "counts": counts,
        "nonconformant": nonconformant,
        "unreadable": unreadable,
    }

    if expect_path is not None:
        try:
            names = load_expected_names(expect_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            result["error"] = "expected-names file unusable: %s" % exc
            return result, 2
        expected = set(names)
        result["expected_names"] = len(names)
        result["missing"] = sorted(expected - stems)
        result["unexpected"] = sorted(stems - expected)
        dup = sorted(n for n in expected if names.count(n) > 1)
        if dup:
            result["duplicate_expected_names"] = dup

    return result, (2 if unreadable else 0)


def print_human(result):
    if "error" in result:
        print("ERROR: %s" % result["error"], file=sys.stderr)
        return
    print("advice_dir: %s" % result["advice_dir"])
    print("files: %d" % result["files"])
    c = result["counts"]
    print("counts: " + " ".join("%s=%d" % (k, c[k]) for k in (*VERDICTS, "nonconformant")))
    if result["nonconformant"]:
        print("nonconformant:")
        for n in result["nonconformant"]:
            print("  %s — first line: %s" % (n["file"], n["first_line"]))
    if result["unreadable"]:
        print("unreadable:")
        for u in result["unreadable"]:
            print("  %s — %s" % (u["file"], u["error"]))
    if "missing" in result:
        print("missing vs expected (%d names): %s"
              % (result["expected_names"],
                 ", ".join(result["missing"]) or "(none)"))
        print("unexpected (present, not in expected): %s"
              % (", ".join(result["unexpected"]) or "(none)"))


def selftest():
    cases = [
        ("VERDICT: confirm — ok", "confirm"),
        ("VERDICT: partial - ok", "partial"),
        ("VERDICT: refute: nope", "refute"),
        ("VERDICT: n/a — nothing", "n/a"),
        ("VERDICT: n/a", "n/a"),
        ("VERDICT: confirm", "confirm"),
        ("VERDICT: confirm —", "confirm"),
        ("verdict: confirm — lower v", None),
        ("VERDICT: CONFIRM — upper token", None),
        ("VERDICT: confirmx — glued", None),
        (" VERDICT: confirm — leading space", None),
        ("VERDICT:confirm — no space", None),
        ("VERDICT: confirm (paren)", None),
        ("VERDICT: confirm – en dash", None),
        ("# Heading — not a verdict", None),
        ("VERDICT: bogus — bad token", None),
    ]
    fails = []
    for line, want in cases:
        got = classify_line(line)
        if got != want:
            fails.append("classify_line(%r): got %r want %r" % (line, got, want))

    with tempfile.TemporaryDirectory(prefix="count-verdicts-selftest-") as td:
        def put(name, text):
            with open(os.path.join(td, name), "w", encoding="utf-8") as fh:
                fh.write(text)

        put("Good.md", "VERDICT: confirm — fine\nrest\n")
        put("Blank.md", "\n\nVERDICT: refute — late but first non-empty\n")
        put("Head.md", "# Head\nVERDICT: confirm — on line 2\n")
        put("Empty.md", "   \n\n")
        put("swarm-registry.md", "VERDICT: confirm — excluded\n")
        put("swarm-registry.json", "{}\n")
        with open(os.path.join(td, "spec.json"), "w", encoding="utf-8") as fh:
            json.dump({"items": [{"name": "Good"}, {"name": "Blank"},
                                 {"name": "Head"}, {"name": "Empty"},
                                 {"name": "Ghost"}]}, fh)
        res, code = run(td, os.path.join(td, "spec.json"))
        want_counts = {"confirm": 1, "partial": 0, "refute": 1,
                       "n/a": 0, "nonconformant": 2}
        if code != 0:
            fails.append("selftest exit code %r want 0" % code)
        if res["counts"] != want_counts:
            fails.append("counts %r want %r" % (res["counts"], want_counts))
        if res["files"] != 4:
            fails.append("files %r want 4 (swarm-registry excluded)" % res["files"])
        if res["missing"] != ["Ghost"]:
            fails.append("missing %r want ['Ghost']" % res["missing"])
        if res["unexpected"] != []:
            fails.append("unexpected %r want []" % res["unexpected"])
        nc = sorted(n["file"] for n in res["nonconformant"])
        if nc != ["Empty.md", "Head.md"]:
            fails.append("nonconformant files %r" % nc)

    if fails:
        print("SELFTEST FAIL")
        for f in fails:
            print("  " + f)
        return 1
    print("SELFTEST PASS: %d classifier cases + directory scan" % len(cases))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="count-verdicts.py",
        description="Count VERDICT: confirm|partial|refute|n/a first non-empty "
                    "lines across *.md advice reports.")
    ap.add_argument("advice_dir", nargs="?", help="directory containing *.md advice reports")
    ap.add_argument("--expect-names", metavar="FILE.json",
                    help="spec.json; its items[].name list is compared to the *.md stems")
    ap.add_argument("--json", action="store_true", help="emit JSON on stdout")
    ap.add_argument("--selftest", action="store_true", help="run self-test and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.advice_dir:
        ap.error("advice_dir is required (or use --selftest)")

    result, code = run(args.advice_dir, args.expect_names)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print_human(result)
    return code


if __name__ == "__main__":
    sys.exit(main())
