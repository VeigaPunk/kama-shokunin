#!/usr/bin/env python3
r"""Enforce SOURCES-CONTRACT-v1 rule 2 (append-only) between two revisions.

Usage:
  python3 tools/sources-append-only.py --from REV --to REV \
      [--repo /home/vgpnk/Projects/shokunin/kama-shokunin] \
      [--path corpus/SOURCES.md] [--json]
  python3 tools/sources-append-only.py --selftest

Reads both blobs with `git -C REPO show REV:PATH` (read-only; never touches
the working tree or index), parses the `## Registry` table in each, and
diffs rows by `id`:

  - a row present in --from but absent in --to is a violation (removed row)
  - a row present in both whose cells differ outside the contract's mutable
    set {status, recheck, used-by} is a violation, reported per cell old->new;
    the compared set must be exactly the seven immutable contract cells
    {source, kind, tier, scope, anchor, teaches, opened}, else exit 2
  - a row present only in --to is allowed and reported as added
  - row re-ordering is ignored (rows are compared by id, not position)

The registry section runs from the one `Registry` heading to the next heading
of the same or a higher level. Blank lines, prose and deeper subheadings do
not end it: every table segment in it is read with the first header, and a
later repeat of that header or of a separator line is skipped. No row is
lost by parsing: a table line that is not a well-formed `S0NN` row, a table
line without a leading pipe, and a row-like line (`| S0NN |`, also with
markup around the id or without the leading pipe) that was not read as a
registry row are parse errors, never skipped. Outside the section the blob
may hold other tables — the corpus appends re-verification sections whose
tables are keyed by S-id — so there a row-like line is refused only when it
cannot belong to such a table: it sits in no `|`-led run at all, its run's
header is exactly the contract header (a copy of the registry table outside
the section), or the line itself has the registry's eleven cells and an
`S0NN` first cell (a registry row or a truncated registry table). A
non-registry table whose own header is the contract header, or that carries
an eleven-cell `S0NN` row, is refused rather than guessed at. Fenced code,
HTML comments and setext headings are not modelled; they can only add rows
to the section or end in exit 2, never hide a row.

Exit codes:
  0  no violations (added rows and mutable-cell changes are fine)
  1  at least one append-only violation
  2  unreadable blob (git failure, not UTF-8) or unparseable registry
     (missing or repeated `Registry` heading, header column names not exactly
     the contract's eleven in any order, missing or misfit separator,
     malformed row width, unrecognised table line, row-like line outside the
     parsed registry, duplicate id) — the guard refuses to grade a table it
     cannot fully parse; an internal fault also exits 2, never 1

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

CONTRACT_COLUMNS = (
    "id", "source", "kind", "tier", "scope", "anchor", "teaches",
    "status", "opened", "recheck", "used-by",
)
MUTABLE_CELLS = frozenset({"status", "recheck", "used-by"})
# Pinned independently of MUTABLE_CELLS: editing either set, or deriving the
# compared columns by slice, becomes a guard fault (exit 2) on every run
# instead of a quietly narrower comparison.
IMMUTABLE_CELLS = frozenset(
    {"source", "kind", "tier", "scope", "anchor", "teaches", "opened"}
)
ID_RE = re.compile(r"^S[0-9]{3,}$")
ROW_RE = re.compile(r"^ {0,3}\|")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]|$)")
REGISTRY_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+Registry(?:[ \t]+#+)?[ \t]*$")
# What a reader takes for a registry row: an S-number first cell, optionally
# wrapped in markup, with or without the leading pipe.
ROWLIKE_RE = re.compile(r"^\s*\|?\s*[`*_\[]*[Ss][0-9]+[`*_\]]*\s*\|")


class ParseError(Exception):
    """A registry the guard cannot fully parse or grade; maps to exit 2."""


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


def has_bare_pipe(line):
    r"""True if `line` holds a `|` that split_cells would treat as a delimiter."""
    in_code = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and not in_code and line[i + 1:i + 2] == "|":
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        elif ch == "|" and not in_code:
            return True
        i += 1
    return False


def is_separator(cells):
    return bool(cells) and all(re.fullmatch(r":?-+:?", c) for c in cells)


def markup_free_id(cell):
    """The id a reader sees in `cell`, with backtick/italic/bold markup off."""
    return cell.strip().strip("`*_[]")


def scan_row_like(lines, start, end, label):
    r"""Refuse every row-shaped line outside the graded registry section.

    Lines [start, end) are the `## Registry` section the caller already
    graded line by line. Beyond it, a `|`-led run is another table (the
    corpus appends re-verification sections keyed by S-id), so a line in one
    is a fault only when it cannot belong to such a table: the run's header
    is exactly the contract header (a copy of the registry table outside the
    section), or the line itself is registry-shaped — eleven cells with an
    `S0NN` first cell. A row-like line in no `|`-led run is always a fault.
    Raises ParseError; a line is never dropped.
    """
    def refuse(segment):
        header = split_cells(segment[0][1])
        if header is not None and sorted(header) == sorted(CONTRACT_COLUMNS):
            raise ParseError(
                f"{label}:{segment[0][0] + 1}: a copy of the registry table "
                "outside the `## Registry` section; refusing to drop its rows"
            )
        for idx, line in segment:
            cells = split_cells(line)
            if (
                cells is not None
                and len(cells) == len(CONTRACT_COLUMNS)
                and ID_RE.match(markup_free_id(cells[0]))
            ):
                raise ParseError(
                    f"{label}:{idx + 1}: row-like line outside the parsed "
                    "registry table: registry-shaped row in a table outside "
                    "the `## Registry` section; refusing to drop it"
                )

    segment = []
    for idx, line in enumerate(lines):
        if start <= idx < end:
            if segment:
                refuse(segment)
                segment = []
            continue
        if ROW_RE.match(line):
            segment.append((idx, line))
            continue
        if segment:
            refuse(segment)
            segment = []
        if ROWLIKE_RE.match(line):
            raise ParseError(
                f"{label}:{idx + 1}: row-like line outside the parsed registry "
                "table; refusing to drop it"
            )
    if segment:
        refuse(segment)


def parse_registry(text, label):
    """Parse every table segment of the `## Registry` section.

    Returns ({id: {col: value}}, header). Raises ParseError instead of
    dropping a row (see the module docstring for what counts as one).
    """
    lines = text.splitlines()
    headings = [idx for idx, line in enumerate(lines) if REGISTRY_RE.match(line)]
    if not headings:
        raise ParseError(f"{label}: no `## Registry` heading found")
    if len(headings) > 1:
        raise ParseError(
            f"{label}: {len(headings)} `Registry` headings (lines "
            + ", ".join(str(h + 1) for h in headings)
            + "); refusing to pick one"
        )
    level = len(REGISTRY_RE.match(lines[headings[0]]).group(1))
    start = headings[0] + 1

    rows_by_id = {}
    row_lines = set()
    header = None
    seen_separator = False
    section_end = len(lines)
    for idx in range(start, len(lines)):
        line = lines[idx]
        heading = HEADING_RE.match(line)
        if heading:
            if len(heading.group(1)) <= level:
                section_end = idx
                break
            continue  # a deeper subheading stays inside the registry section
        if not ROW_RE.match(line):
            if has_bare_pipe(line):
                raise ParseError(
                    f"{label}:{idx + 1}: table line without a leading pipe "
                    "in the registry section; refusing to drop it"
                )
            continue  # blank line or prose; later table segments still count
        cells = split_cells(line)
        if cells is None:
            raise ParseError(
                f"{label}:{idx + 1}: unterminated table row (no closing pipe)"
            )
        if header is None:
            if sorted(cells) != sorted(CONTRACT_COLUMNS):
                raise ParseError(
                    f"{label}:{idx + 1}: header columns {cells} are not exactly "
                    f"the contract's {list(CONTRACT_COLUMNS)}"
                )
            header = cells
            continue
        if not seen_separator:
            if not is_separator(cells) or len(cells) != len(header):
                raise ParseError(
                    f"{label}:{idx + 1}: expected a {len(header)}-column "
                    "`|---|...` separator after header"
                )
            seen_separator = True
            continue
        if cells == header or is_separator(cells):
            continue  # a later table segment repeats the header and separator
        if len(cells) != len(header):
            raise ParseError(
                f"{label}:{idx + 1}: row has {len(cells)} cells, "
                f"header has {len(header)}"
            )
        row = dict(zip(header, cells))
        rid = row["id"]
        if not ID_RE.match(rid):
            raise ParseError(
                f"{label}:{idx + 1}: table line with id cell `{rid}` is not a "
                "registry row; refusing to drop it"
            )
        if rid in rows_by_id:
            raise ParseError(f"{label}:{idx + 1}: duplicate id {rid}")
        rows_by_id[rid] = row
        row_lines.add(idx)

    if header is None or not seen_separator:
        raise ParseError(f"{label}: registry section has no complete table header")
    scan_row_like(lines, start, section_end, label)
    if not rows_by_id:
        raise ParseError(f"{label}: registry table has no data rows")
    return rows_by_id, header


def diff_registries(from_rows, to_rows, header):
    """Compare two parsed registries. Returns (violations, added_ids).

    violations: list of dicts, each {id, kind, details}
      kind == "removed"      -> details is None
      kind == "cell-changed" -> details is [{cell, from, to}] for non-mutable cells
    added_ids: ids present only in --to (allowed).
    Raises ParseError if the compared columns are not exactly IMMUTABLE_CELLS.
    """
    immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]
    if sorted(immutable_cols) != sorted(IMMUTABLE_CELLS):
        raise ParseError(
            f"compared cells {immutable_cols} are not exactly the contract's "
            f"immutable cells {sorted(IMMUTABLE_CELLS)}"
        )
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


def decode_blob(raw, label):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ParseError(f"{label}: blob is not UTF-8 ({e})") from None


def git_show(repo, rev, path):
    # A rev beginning with '-' would be parsed by git-show as an option
    # (e.g. --output=FILE writes a file); a ':' would corrupt the REV:PATH
    # spec. Reject both before reaching the subprocess.
    if rev.startswith("-") or ":" in rev:
        raise ParseError(f"invalid revision selector {rev!r}")
    try:
        proc = subprocess.run(
            ["git", "-C", repo, "show", f"{rev}:{path}"],
            capture_output=True,
        )
    except OSError as e:
        raise ParseError(f"cannot run git: {e}") from None
    if proc.returncode != 0:
        raise ParseError(
            f"git show {rev}:{path} failed (rc={proc.returncode}): "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return decode_blob(proc.stdout, f"{rev}:{path}")


def run_check(args):
    try:
        from_text = git_show(args.repo, args.from_rev, args.path)
        to_text = git_show(args.repo, args.to_rev, args.path)
        from_rows, header = parse_registry(from_text, f"{args.from_rev}:{args.path}")
        to_rows, _ = parse_registry(to_text, f"{args.to_rev}:{args.path}")
        violations, added = diff_registries(from_rows, to_rows, header)
    except Exception as e:  # a traceback would exit 1, the violation code
        if isinstance(e, ParseError):
            error = str(e)
        else:
            error = f"internal error: {type(e).__name__}: {e}"
        if args.json:
            print(json.dumps({"error": error, "violations": None}))
        else:
            print(f"error: {error}", file=sys.stderr)
        return 2

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
_DEFAULTS = {
    "source": "src-x", "kind": "docs", "tier": "A", "scope": "scope-x",
    "anchor": "anchor-x", "teaches": "teaches-x", "status": "queued",
    "opened": "2026-10-20", "recheck": "90d", "used-by": "—",
}
# The contract's verdict on an in-place edit of each cell (CORPUS.md
# SOURCES-CONTRACT-v1 rule 2), written out rather than derived from the
# constants under test so that a narrowed comparison cannot also narrow it.
_CELL_EDIT_EXIT = {
    "source": 1, "kind": 1, "tier": 1, "scope": 1, "anchor": 1, "teaches": 1,
    "status": 0, "opened": 1, "recheck": 0, "used-by": 0,
}


def _row(rid, **cells):
    vals = dict(_DEFAULTS)
    for key, value in cells.items():
        col = key.replace("_", "-")
        if col not in vals:
            raise ValueError(f"_row: unknown column {key!r}")
        vals[col] = value
    return "| " + " | ".join([rid, *vals.values()]) + " |"


def _doc(*rows):
    return _REGISTRY + "\n".join(rows) + _TAIL


def _drop_opened(text):
    """The same document with the `opened` column deleted (10 columns)."""
    return (
        text.replace("| opened |", "|", 1)
        .replace("|---" * 11 + "|", "|---" * 10 + "|", 1)
        .replace("| 2026-10-20 |", "|")
    )


def run_selftest():
    s001 = _row("S001")
    s002 = _row("S002", teaches="teaches-y")
    segment = _HDR.rstrip("\n")  # a later table segment's header + separator
    cases = []

    def case(name, from_text, to_text, want_exit, want=(), added=(), error=""):
        cases.append((name, from_text, to_text, want_exit, set(want), list(added), error))

    # 1. identical tables -> clean
    case("identical", _doc(s001, s002), _doc(s001, s002), 0)

    # 2. status-only change -> allowed
    case(
        "status-only change",
        _doc(s001),
        _doc(_row("S001", status="mined", used_by="corpus/knowledge/x.md")),
        0,
    )

    # 3. teaches change -> violation on S001
    case("teaches change", _doc(s001), _doc(_row("S001", teaches="rewritten")), 1,
         {"S001:teaches"})

    # 4. removed row -> violation on S002
    case("removed row", _doc(s001, s002), _doc(s001), 1, {"S002:removed"})

    # 5. added row -> clean, and reported as added
    case("added row", _doc(s001), _doc(s001, _row("S003", teaches="new")), 0,
         added=["S003"])

    # 6. row re-ordering -> ignored
    case("reordered rows", _doc(s001, s002), _doc(s002, s001), 0)

    # 7. pipe inside backticks is literal cell content, not a delimiter
    bt = _row("S001", teaches="shows `a | b` split")
    case("pipe inside backticks", _doc(bt), _doc(bt), 0)

    # 8. escaped \| is literal cell content
    esc = _row("S001", teaches="a \\| b literal")
    case("escaped pipe", _doc(esc), _doc(esc), 0)

    # 9. recheck + used-by change -> allowed
    case(
        "recheck and used-by change",
        _doc(s001),
        _doc(_row("S001", recheck="on-release", used_by="corpus/lessons/r.md")),
        0,
    )

    # 10. anchor change -> violation (the S041 failure mode)
    case("anchor change", _doc(s001), _doc(_row("S001", anchor="receipt v2")), 1,
         {"S001:anchor"})

    # 11. malformed row width -> parse error
    bad = _doc(s001).replace(s001, "| S001 | only | three | cells |")
    case("malformed row width", bad, _doc(s001), 2, error="row has 4 cells")

    # 12. duplicate id -> parse error
    case("duplicate id", _doc(s001, s001), _doc(s001), 2, error="duplicate id S001")

    # 13. missing registry section -> parse error
    case("missing registry", "# no table\n", _doc(s001), 2, error="no `## Registry`")

    # 14. source cell change -> violation (mutable set is exactly 3 cells)
    case("source change", _doc(s001), _doc(_row("S001", source="edited-url")), 1,
         {"S001:source"})

    # 15-24. one in-place edit per contract cell, graded by the written-out
    # oracle: `opened`, `kind`, `tier` and `scope` had no case before
    for cell, want_exit in _CELL_EDIT_EXIT.items():
        edited = _row("S001", **{cell.replace("-", "_"): f"edited-{cell}"})
        case(f"only `{cell}` changes", _doc(s001, s002), _doc(edited, s002),
             want_exit, {f"S001:{cell}"} if want_exit else ())

    # 25-29. rows after a blank line, in a later table segment or under a
    # deeper subheading are registry rows, never dropped
    case("edit after a blank line", _doc(s001, "", s002),
         _doc(s001, "", _row("S002", teaches="rewritten")), 1, {"S002:teaches"})
    case("row added after a blank line", _doc(s001), _doc(s001, "", _row("S003")),
         0, added=["S003"])
    case("row removed from a later table segment", _doc(s001, "", segment, s002),
         _doc(s001, "", segment), 1, {"S002:removed"})
    case("edit in a later table segment", _doc(s001, "", segment, s002),
         _doc(s001, "", segment, _row("S002", teaches="teaches-y", opened="2026-10-21")),
         1, {"S002:opened"})
    sub = "### Later rows"
    case("edit under a deeper subheading", _doc(s001, "", sub, "", s002),
         _doc(s001, "", sub, "", _row("S002", teaches="teaches-y", scope="widened")),
         1, {"S002:scope"})

    # 30-38. a row the parser cannot read, or a table it cannot read
    # consistently, is reported (exit 2), never silently skipped
    case("row-like line outside the registry", _doc(s001), _doc(s001) + s002 + "\n",
         2, error="row-like line outside")
    case("row without a leading pipe", _doc(s001, s002),
         _doc(s001, s002.lstrip("| ")), 2, error="without a leading pipe")
    case("row with a marked-up id", _doc(s001, _row("`S002`")),
         _doc(s001, _row("`S002`", teaches="rewritten")), 2,
         error="id cell ``S002`` is not")
    case("row with a lower-case id", _doc(s001, _row("s002")),
         _doc(s001, _row("s002", teaches="rewritten")), 2,
         error="id cell `s002` is not")
    case("later segment with another header",
         _doc(s001, "", segment.replace("| source | kind |", "| kind | source |", 1),
              s002),
         _doc(s001), 2, error="id cell `id` is not")
    case("two Registry headings", _doc(s001) + "\n## Registry\n\n" + _HDR + s002 + "\n",
         _doc(s001), 2, error="2 `Registry` headings")
    case("header repeats a column",
         _doc(s001).replace("| opened |", "| teaches |", 1),
         _doc(_row("S001", teaches="rewritten")).replace("| opened |", "| teaches |", 1),
         2, error="header columns")
    case("--to drops the opened column", _doc(s001), _drop_opened(_doc(s001)), 2,
         error="header columns")
    case("separator narrower than the header",
         _doc(s001).replace("|---" * 11 + "|", "|---|---|", 1), _doc(s001), 2,
         error="11-column `|---|...` separator")
    # 39. an ATX closing sequence still names the Registry heading
    case("closing hashes on the Registry heading",
         _doc(s001).replace("## Registry", "## Registry ##", 1),
         _doc(_row("S001", tier="B")).replace("## Registry", "## Registry ##", 1),
         1, {"S001:tier"})

    # 40-42. outside the section, an S-keyed table is another table (the
    # corpus appends re-verification sections keyed by S-id), while a copy of
    # the registry header or a registry-shaped row is still a fault
    keyed = (
        "\n## Round-45 re-verification\n\n"
        "| key | pin to current | class | what the witness shows |\n"
        "|---|---|---|---|\n"
        "| `S001` | ollama `c1` to main `c2` | holds | unchanged |\n"
        "| `S002` | ggml `a` to master `b` | unchanged-file | identical |\n"
        "\n| id | pin verdict | release verdict | lines | read by |\n"
        "|---|---|---|---|---|\n"
        "| `S001` | holds | holds | 4-6 to 9-11 | X1 (built) |\n"
    )
    case("S-keyed table outside the registry section", _doc(s001, s002),
         _doc(s001, s002) + keyed, 0)
    case("registry header copied outside the section", _doc(s001),
         _doc(s001) + "\n## Copy\n\n" + _HDR + s002 + "\n", 2,
         error="copy of the registry table outside")
    case("registry-shaped row outside any table", _doc(s001),
         _doc(s001) + "\n" + s002 + "\n", 2, error="registry-shaped row")

    failures = 0
    for name, from_text, to_text, want_exit, want, want_added, want_error in cases:
        got, got_added, got_error = set(), [], ""
        try:
            from_rows, header = parse_registry(from_text, "from")
            to_rows, _ = parse_registry(to_text, "to")
            violations, got_added = diff_registries(from_rows, to_rows, header)
            got_exit = 1 if violations else 0
            for v in violations:
                if v["kind"] == "removed":
                    got.add(f"{v['id']}:removed")
                else:
                    got.update(f"{v['id']}:{d['cell']}" for d in v["details"])
        except ParseError as e:
            got_exit, got_error = 2, str(e)
        except Exception as e:  # a crashing case is a FAIL line, not an abort
            got_exit, got_error = "crash", f"{type(e).__name__}: {e}"
        ok = (
            got_exit == want_exit
            and got == want
            and got_added == want_added
            and want_error in got_error
        )
        if not ok:
            failures += 1
        print(
            f"{'ok' if ok else 'FAIL'}: {name} (want exit {want_exit}"
            + (f" {sorted(want)}" if want else "")
            + (f" added {want_added}" if want_added else "")
            + (f" error ~{want_error!r}" if want_error else "")
            + f", got exit {got_exit}"
            + (f" {sorted(got)}" if got else "")
            + (f" added {got_added}" if got_added else "")
            + (f" error {got_error!r}" if got_error else "")
            + ")"
        )

    # detectors of the detector: the oracle covers every fixture column, the
    # pinned compared set rejects a header without `opened`, and a non-UTF-8
    # blob is a parse error (exit 2), not a traceback (exit 1)
    fixture_cols = [c.strip() for c in _HDR.splitlines()[0].strip().strip("|").split("|")]
    checks = [
        ("oracle covers every fixture column",
         fixture_cols[1:] == list(_CELL_EDIT_EXIT) == list(_DEFAULTS)),
    ]
    for name, call in (
        ("compared set without `opened` is refused",
         lambda: diff_registries({}, {}, [c for c in fixture_cols if c != "opened"])),
        ("non-UTF-8 blob is a parse error",
         lambda: decode_blob(b"## Registry \xff\n", "blob")),
    ):
        try:
            call()
            checks.append((name, False))
        except ParseError:
            checks.append((name, True))
    for name, ok in checks:
        if not ok:
            failures += 1
        print(f"{'ok' if ok else 'FAIL'}: {name}")

    total = len(cases) + len(checks)
    print(f"{total - failures}/{total} selftest cases passed")
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
