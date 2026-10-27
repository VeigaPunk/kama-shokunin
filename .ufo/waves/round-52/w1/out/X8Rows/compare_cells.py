#!/usr/bin/env python3
"""X8Rows (round 52, lane kama): for each of the 10 remaining disclosure rows,
show the row that now occupies its key at the build tip, so the duplicate-key
defect is stated cell by cell.

- corpus/SOURCES.md rows: cells split by the frozen guard's own split_cells()
  (tools/sources-append-only.py), columns from its CONTRACT_COLUMNS; the
  "current" row is the registry row with the same id at the tip.
- registry/report-landing-errata.tsv rows: TSV, key = (round, kind, token);
  the "current" rows are every tip row with that key.

Usage: compare_cells.py <repo> <tip> <rows.json> <out-json>
"""
import importlib.util
import json
import subprocess
import sys

TOOL = ("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
        "sources-append-only.py")
SOURCES = "corpus/SOURCES.md"
ERRATA = "registry/report-landing-errata.tsv"


def load_tool():
    spec = importlib.util.spec_from_file_location("sao", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def blob(repo, tip, path):
    return subprocess.run(["git", "-C", repo, "show", f"{tip}:{path}"],
                          capture_output=True, check=True).stdout.decode()


def registry_rows(mod, text):
    """{id: [cells]} for every well-formed row of the ## Registry table."""
    rows, inside, header = {}, False, None
    for line in text.split("\n"):
        if line.startswith("## "):
            inside = line.strip() == "## Registry"
            continue
        if not inside or not line.lstrip().startswith("|"):
            continue
        cells = mod.split_cells(line)
        if cells is None:
            continue
        if [c.lower() for c in cells] == [c.lower() for c in mod.CONTRACT_COLUMNS]:
            header = cells
            continue
        if header and len(cells) == len(header):
            rows.setdefault(cells[0], []).append(cells)
    return rows


def errata_rows(text):
    rows = []
    for line in text.split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) == 5:
            rows.append(p)
    return rows


def main(repo, tip, rows_json, outp):
    mod = load_tool()
    reg = registry_rows(mod, blob(repo, tip, SOURCES))
    err = errata_rows(blob(repo, tip, ERRATA))
    out = []
    for r in json.load(open(rows_json))["rows"]:
        text = r["matches"][0]["text"]
        if r["file"] == SOURCES:
            cells = mod.split_cells(text)
            if cells is None:
                out.append({"ledger_line": r["ledger_line"],
                            "commit": r["commit"], "file": r["file"],
                            "key": "(unparseable)", "key_kind": "registry id",
                            "split_cells": None,
                            "tip_rows_with_key": None,
                            "cell_diffs_vs_tip": [],
                            "note": "split_cells() returns None: the deleted "
                                    "line does not close a table row"})
                continue
            ident = cells[0]
            now = reg.get(ident, [])
            diffs = []
            for cur in now:
                diffs.append({mod.CONTRACT_COLUMNS[i]:
                              {"deleted": cells[i], "tip": cur[i]}
                              for i in range(len(cells))
                              if cells[i] != cur[i]})
            out.append({"ledger_line": r["ledger_line"],
                        "commit": r["commit"], "file": r["file"],
                        "key": ident, "key_kind": "registry id",
                        "tip_rows_with_key": len(now),
                        "cell_diffs_vs_tip": diffs,
                        "deleted_cells": dict(zip(mod.CONTRACT_COLUMNS, cells))})
        else:
            p = text.split("\t")
            key = tuple(p[:3])
            now = [e for e in err if tuple(e[:3]) == key]
            out.append({"ledger_line": r["ledger_line"],
                        "commit": r["commit"], "file": r["file"],
                        "key": "\t".join(key), "key_kind": "(round,kind,token)",
                        "tip_rows_with_key": len(now),
                        "cell_diffs_vs_tip": [
                            {("round", "kind", "token", "correction",
                              "evidence")[i]:
                             {"deleted": p[i], "tip": e[i]}
                             for i in range(5) if p[i] != e[i]}
                            for e in now]})
    with open(outp, "w") as fh:
        json.dump(out, fh, indent=1)
    for o in out:
        print(f"line={o['ledger_line']} {o['file']} key={o['key'][:70]!r} "
              f"tip_rows={o['tip_rows_with_key']} "
              f"cells_changed={sorted(set().union(*[set(d) for d in o['cell_diffs_vs_tip']]) if o['cell_diffs_vs_tip'] else [])}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
