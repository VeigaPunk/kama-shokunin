# Proposed fixes for tools/append-only-audit.py (v6 @ 138af25b) — V3Review, round 51

Both functions below are full replacements. The tool is FROZEN for round 51: these are
report artifacts, not in-place edits. Either fix changes tool verdicts, so it belongs in
a future round with its own fixtures (and the same two fixes applied to the frozen
counter's `cells()` / lane-leg permit loop in tools/round51-append-audit-v6-check.py,
which shares both blind spots).

## Fix 1 — row_cells: honour `\|` escapes (finding V3R-1)

`tools/sources-append-only.py` split_cells (lines 91-133 @ 138af25b) — the tool the A-row
contract row cites as the rule's definition — treats a `\|` escape outside a code span as
cell content and keeps it verbatim in the cell. v6 row_cells splits on it, so a row using
GFM-escaped pipes reads as 12+ cells and every status/recheck/used-by edit of it is
graded as a loss. Escape-aware version, byte-identical cell contents otherwise:

```python
def row_cells(text):
    """v6.1: the cells of a registry row line (bytes) split on `|` outside backtick code
    spans and outside a `\\|` escape, without the outer pipes; None when the line is not
    a row or does not close. Matches tools/sources-append-only.py split_cells: a `\\|`
    escape outside a code span is cell content, kept verbatim in the cell."""
    try:
        s = text.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not ROW.match(s):
        return None
    s = s.rstrip("\r").strip()
    cells, buf, code = [], [], False
    j, n = 1, len(s)          # skip the leading pipe
    while j < n:
        ch = s[j]
        if ch == "\\" and not code and j + 1 < n and s[j + 1] == "|":
            buf.append(ch)
            buf.append("|")
            j += 2
            continue
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        j += 1
    return cells if not "".join(buf).strip() else None
```

## Fix 2 — permitted_edits: a duplicated row id permits nothing (finding V3R-2)

v6 matches a deleted row against ANY 11-cell row with the same id anywhere in the
commit's whole blob. A commit that mutates an immutable cell in place and re-adds a copy
of the old row therefore passes with exit 0, while sources-append-only.py refuses the
same state (exit 2, duplicate id). Require the id to be held exactly once:

```python
def permitted_edits(dl, new_body):
    """v6.1 A-row: positions in dl of deleted rows whose id the new blob still holds
    exactly once, with every immutable cell byte-equal (only status, recheck and used-by
    changed). A blob holding the id more than once permits nothing: the lane's registry
    guard refuses duplicate ids (tools/sources-append-only.py exit 2), so a duplicated id
    is not a state the A-row rule's in-place allowance can be read against."""
    rows = collections.defaultdict(list)
    for ln in new_body:
        c = row_cells(ln)
        if c is not None and len(c) == 11:
            rows[c[0]].append(c)
    keep = lambda c: [x for j, x in enumerate(c) if j not in MUTABLE_COLS]
    out = set()
    for pos, text, _na in dl:
        c = row_cells(text)
        cands = rows.get(c[0], ()) if c is not None and len(c) == 11 else ()
        if len(cands) == 1 and keep(cands[0]) == keep(c):
            out.add(pos)
    return out
```

With fix 2 the decoy commit of probe F2y is graded (the mutated row's old line becomes a
loss that a disclosure must name) instead of silently permitted; the fail direction
matches the guard's refusal instead of contradicting it.
