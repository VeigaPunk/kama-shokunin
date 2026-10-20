#!/usr/bin/env python3
r"""Enforce SOURCES-CONTRACT-v1 rule 2 (append-only) between two revisions.

Usage:
  python3 tools/sources-append-only.py --from REV --to REV \
      [--repo /home/vgpnk/Projects/shokunin/kama-shokunin] \
      [--path corpus/SOURCES.md] [--json]
  python3 tools/sources-append-only.py --selftest

Reads both blobs with `git -C REPO show REV:PATH` (read-only; never touches
the working tree or index), parses the `## Registry` markdown table in each,
and diffs rows by `id`:

  - a row present in --from but absent in --to is a violation (removed row)
  - a row present in both whose cells differ outside the contract's mutable
    set {status, recheck, used-by} is a violation, reported per cell old->new
  - a row present only in --to is allowed and reported as added
  - row re-ordering is ignored (rows are compared by id, not position)

Exit codes:
  0  no violations (added rows and mutable-cell changes are fine)
  1  at least one append-only violation
  2  unreadable blob or unparseable registry (missing section/header, missing
     required columns, malformed row width, duplicate id) — the guard refuses
     to grade a table it cannot fully parse

Cell-splitting note: GFM technically requires `\|` inside code spans in table
cells; this parser is deliberately more forgiving — a `|` inside a backtick
code span, or a `\|` escape anywhere, is cell content, not a delimiter. Cells
are compared verbatim after leading/trailing whitespace strip, so `\|` stays
`\|`; a cell that rewrites escaping registers as a change in that cell.

`--selftest` exercises the parser and comparator on in-memory tables only;
it never runs git and is fixture self-consistency, never corpus evidence.
"""

import argparse
import json
import re
import subprocess
import sys

MUTABLE_CELLS = frozenset({"status", "recheck", "used-by"})
ID_RE = re.compile(r"^S[0-9]{3,}$")
ROW_RE = re.compile(r"^ {0,3}\|")
HEADING_RE = re.compile(r"^ {0,3}#{1,6} ")
REGISTRY_RE = re.compile(r"^ {0,3}#{1,6}\s+Registry\s*$")


class ParseError(Exception):
    """A registry blob the guard cannot fully parse; maps to exit 2."""


def split_cells(line):
    r"""Split one markdown table line into cells.

    Honors `\|` escapes and treats `|` inside backtick code spans as literal.
    Returns the cell list excluding the outer pipes, or None if the line does
    not end its row (no closing unescaped pipe).
    """
    s = line.strip()
    if not s.startswith("|"):
        return None
    cells = []
    buf = []
    in_code = False
    i = 1  # skip leading pipe
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|" and not in_code:
            buf.append("\\")
            buf.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
            i += 1
            continue
        if ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    # a well-formed row ends with the outer pipe already consumed above;
    # anything left in buf means the line's last pipe was not the closer
    # only when we never saw a closing delimiter.
    if buf:
        trailing = "".join(buf).strip()
        if trailing:
            # content after the last pipe -> not a table row ending in |
            return None
    return cells


def is_separator(cells):
    return bool(cells) and all(re.fullmatch(r":?-+:?", c) for c in cells)


def parse_registry(text, label):
    """Parse the `## Registry` table. Returns {id: {col: value}} and column order."""
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if REGISTRY_RE.match(line):
            start = idx + 1
            break
    if start is None:
        raise ParseError(f"{label}: no `## Registry` heading found")

    rows_by_id = {}
    header = None
    seen_separator = False
    for idx in range(start, len(lines)):
        line = lines[idx]
        if HEADING_RE.match(line):
            break
        if not ROW_RE.match(line):
            continue
        cells = split_cells(line)
        if cells is None:
            raise ParseError(
                f"{label}:{idx + 1}: unterminated table row (no closing pipe)"
            )
        if header is None:
            header = cells
            continue
        if not seen_separator:
            if not is_separator(cells):
                raise ParseError(
                    f"{label}:{idx + 1}: expected `|---|...` separator after header"
                )
            seen_separator = True
            continue
        if len(cells) != len(header):
            raise ParseError(
                f"{label}:{idx + 1}: row has {len(cells)} cells, "
                f"header has {len(header)}"
            )
        row = dict(zip(header, cells))
        rid = row.get("id", "")
        if not ID_RE.match(rid):
            # non-id pipe lines inside the registry section are not rows;
            # tolerate them only if they do not look like a mangled data row
            if rid.startswith("S"):
                raise ParseError(f"{label}:{idx + 1}: malformed id `{rid}`")
            continue
        if rid in rows_by_id:
            raise ParseError(f"{label}:{idx + 1}: duplicate id {rid}")
        rows_by_id[rid] = row

    if header is None or not seen_separator:
        raise ParseError(f"{label}: registry section has no complete table header")
    for needed in {"id"} | MUTABLE_CELLS:
        if needed not in header:
            raise ParseError(f"{label}: header missing required column `{needed}`")
    if not rows_by_id:
        raise ParseError(f"{label}: registry table has no data rows")
    return rows_by_id, header


def diff_registries(from_rows, to_rows, header):
    """Compare two parsed registries. Returns (violations, added_ids).

    violations: list of dicts, each {id, kind, details}
      kind == "removed"      -> details is None
      kind == "cell-changed" -> details is [{cell, from, to}] for non-mutable cells
    added_ids: ids present only in --to (allowed).
    """
    immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]
    violations = []
    for rid in sorted(set(from_rows) | set(to_rows)):
        old = from_rows.get(rid)
        new = to_rows.get(rid)
        if new is None:
            violations.append({"id": rid, "kind": "removed", "details": None})
            continue
        if old is None:
            continue
        changed = [
            {"cell": c, "from": old[c], "to": new[c]}
            for c in immutable_cols
            if old[c] != new[c]
        ]
        if changed:
            violations.append({"id": rid, "kind": "cell-changed", "details": changed})
    added = sorted(rid for rid in to_rows if rid not in from_rows)
    return violations, added


def git_show(repo, rev, path):
    # A rev beginning with '-' would be parsed by git-show as an option
    # (e.g. --output=FILE writes a file); a ':' would corrupt the REV:PATH
    # spec. Reject both before reaching the subprocess.
    if rev.startswith("-") or ":" in rev:
        raise ParseError(f"invalid revision selector {rev!r}")
    proc = subprocess.run(
        ["git", "-C", repo, "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ParseError(
            f"git show {rev}:{path} failed (rc={proc.returncode}): "
            f"{proc.stderr.strip()}"
        )
    return proc.stdout


def run_check(args):
    try:
        from_text = git_show(args.repo, args.from_rev, args.path)
        to_text = git_show(args.repo, args.to_rev, args.path)
        from_rows, header = parse_registry(from_text, f"{args.from_rev}:{args.path}")
        to_rows, _ = parse_registry(to_text, f"{args.to_rev}:{args.path}")
    except ParseError as e:
        if args.json:
            print(json.dumps({"error": str(e), "violations": None}))
        else:
            print(f"error: {e}", file=sys.stderr)
        return 2

    violations, added = diff_registries(from_rows, to_rows, header)
    if args.json:
        print(
            json.dumps(
                {
                    "from": args.from_rev,
                    "to": args.to_rev,
                    "path": args.path,
                    "violations": violations,
                    "added": added,
                    "ok": not violations,
                },
                indent=2,
            )
        )
    else:
        for v in violations:
            if v["kind"] == "removed":
                print(f"VIOLATION {v['id']}: row removed")
            else:
                for d in v["details"]:
                    print(
                        f"VIOLATION {v['id']}: cell `{d['cell']}` changed in place\n"
                        f"  old: {d['from']}\n"
                        f"  new: {d['to']}"
                    )
        for rid in added:
            print(f"added {rid} (allowed)")
        if violations:
            print(f"{len(violations)} append-only violation(s)")
        else:
            print("no append-only violations")
    return 1 if violations else 0


# --------------------------------------------------------------------------
# selftest — in-memory tables only, never touches git
# --------------------------------------------------------------------------

_HDR = (
    "| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|\n"
)
_REGISTRY = "# SOURCES — where t learns\n\n## Registry\n\n" + _HDR
_TAIL = "\n## Paths\n\n- x — S001: why\n"


def _row(rid, teaches="teaches-x", status="queued", recheck="90d", used_by="—",
         anchor="anchor-x", source="src-x", kind="docs", tier="A",
         scope="scope-x", opened="2026-10-20"):
    return (
        f"| {rid} | {source} | {kind} | {tier} | {scope} | {anchor} | {teaches} "
        f"| {status} | {opened} | {recheck} | {used_by} |"
    )


def _doc(*rows):
    return _REGISTRY + "\n".join(rows) + _TAIL


def run_selftest():
    base_s001 = _row("S001")
    base_s002 = _row("S002", teaches="teaches-y")

    cases = []

    def case(name, from_text, to_text, want_exit, want_ids=None):
        cases.append((name, from_text, to_text, want_exit, want_ids or set()))

    # 1. identical tables -> clean
    case("identical", _doc(base_s001, base_s002), _doc(base_s001, base_s002), 0)

    # 2. status-only change -> allowed
    case(
        "status-only change",
        _doc(base_s001),
        _doc(_row("S001", status="mined", used_by="corpus/knowledge/x.md")),
        0,
    )

    # 3. teaches change -> violation on S001
    case(
        "teaches change",
        _doc(base_s001),
        _doc(_row("S001", teaches="rewritten")),
        1,
        {"S001"},
    )

    # 4. removed row -> violation on S002
    case("removed row", _doc(base_s001, base_s002), _doc(base_s001), 1, {"S002"})

    # 5. added row -> clean
    case(
        "added row",
        _doc(base_s001),
        _doc(base_s001, _row("S003", teaches="new")),
        0,
    )

    # 6. row re-ordering -> ignored
    case(
        "reordered rows",
        _doc(base_s001, base_s002),
        _doc(base_s002, base_s001),
        0,
    )

    # 7. pipe inside backticks is literal cell content, not a delimiter
    bt = _row("S001", teaches="shows `a | b` split")
    case("pipe inside backticks", _doc(bt), _doc(bt), 0)

    # 8. escaped \| is literal cell content
    esc = _row("S001", teaches="a \\| b literal")
    case("escaped pipe", _doc(esc), _doc(esc), 0)

    # 9. recheck + used-by change -> allowed
    case(
        "recheck and used-by change",
        _doc(base_s001),
        _doc(_row("S001", recheck="on-release", used_by="corpus/lessons/r.md")),
        0,
    )

    # 10. anchor change -> violation (the S041 failure mode)
    case(
        "anchor change",
        _doc(base_s001),
        _doc(_row("S001", anchor="receipt v2")),
        1,
        {"S001"},
    )

    # 11. malformed row width -> parse error
    bad = _doc(base_s001).replace(
        base_s001, "| S001 | only | three | cells |"
    )
    case("malformed row width", bad, _doc(base_s001), 2)

    # 12. duplicate id -> parse error
    case("duplicate id", _doc(base_s001, base_s001), _doc(base_s001), 2)

    # 13. missing registry section -> parse error
    case("missing registry", "# no table\n", _doc(base_s001), 2)

    # 14. source cell change -> violation (mutable set is exactly 3 cells)
    case(
        "source change",
        _doc(base_s001),
        _doc(_row("S001", source="edited-url")),
        1,
        {"S001"},
    )

    failures = 0
    for name, from_text, to_text, want_exit, want_ids in cases:
        try:
            from_rows, header = parse_registry(from_text, "from")
            to_rows, _ = parse_registry(to_text, "to")
            violations, _ = diff_registries(from_rows, to_rows, header)
            got_exit = 1 if violations else 0
            got_ids = {v["id"] for v in violations}
        except ParseError:
            got_exit, got_ids = 2, set()
        ok = got_exit == want_exit and (want_exit != 1 or got_ids == want_ids)
        status = "ok" if ok else "FAIL"
        if not ok:
            failures += 1
        print(
            f"{status}: {name} (want exit {want_exit}"
            + (f" ids {sorted(want_ids)}" if want_ids else "")
            + f", got exit {got_exit}"
            + (f" ids {sorted(got_ids)}" if got_ids else "")
            + ")"
        )
    print(f"{len(cases) - failures}/{len(cases)} selftest cases passed")
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Enforce SOURCES-CONTRACT-v1 rule 2 (append-only) "
        "between two revisions of corpus/SOURCES.md."
    )
    ap.add_argument("--from", dest="from_rev", help="base revision (older)")
    ap.add_argument("--to", dest="to_rev", help="target revision (newer)")
    ap.add_argument(
        "--repo",
        default="/home/vgpnk/Projects/shokunin/kama-shokunin",
        help="repository containing the file (default: kama-shokunin lane)",
    )
    ap.add_argument("--path", default="corpus/SOURCES.md", help="blob path in repo")
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    ap.add_argument(
        "--selftest",
        action="store_true",
        help="run in-memory parser/diff cases (no git, no repo access)",
    )
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest()
    if not args.from_rev or not args.to_rev:
        ap.error("--from and --to are required unless --selftest")
    return run_check(args)


if __name__ == "__main__":
    sys.exit(main())
