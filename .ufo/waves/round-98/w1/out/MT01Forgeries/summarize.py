#!/usr/bin/env python3
"""MT01Forgeries: authoritative survive/catch matrix from the receipt files."""
import json
import re
import sys
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-98/w1/out/"
           "MT01Forgeries")
CTRL = re.compile(r"^ROUTER_BUDGET98_CONTROL cells=(\d+) cells_ok=(\d+) mutant=(\S+) "
                  r"slow_files=\d+ runs=\d+ expect=(\S+) expect_cell=(\S+) cell_ok=(\S+) "
                  r"survived=(\d+) caught=(\d+) probe=(\S+) probe_sha256=(\w+) rev=(\w+) ok=(\d+)")
CELL = re.compile(r"^ROUTER_BUDGET98_CELL (\S+) (\S+) ok=(\d+) want=(\S+) (.*)$")
SETS = {"legacy": 13, "r97set": 17, "new": 6}


def parse(path: Path):
    txt = path.read_text()
    m = None
    for ln in txt.splitlines():
        mm = CTRL.match(ln)
        if mm:
            m = mm
    if not m:
        return None
    cells = {}
    for ln in txt.splitlines():
        mm = CELL.match(ln)
        if mm:
            cells[mm.group(2)] = {"ok": int(mm.group(3)), "want": mm.group(4),
                                  "detail": mm.group(5)}
    exit_m = re.search(r"^# exit=(\d+)", txt, re.M)
    return {"cells": int(m.group(1)), "cells_ok": int(m.group(2)), "mutant": m.group(3),
            "expect": m.group(4), "expect_cell": m.group(5), "cell_ok": m.group(6),
            "survived": int(m.group(7)), "caught": int(m.group(8)), "probe": m.group(9),
            "probe_sha256": m.group(10), "rev": m.group(11), "ok": int(m.group(12)),
            "exit": int(exit_m.group(1)) if exit_m else None,
            "red": sorted(c for c, v in cells.items() if v["ok"] == 0),
            "cells_seen": len(cells)}


def main() -> int:
    recs = {}
    for p in sorted((OUT / "receipts").glob("*.out")):
        name = p.name[:-4]
        if name.endswith(".survived-mode"):
            name = name[:-len(".survived-mode")]
        d = parse(p)
        if d:
            d["receipt"] = str(p.relative_to(OUT))
            recs.setdefault(name, []).append(d)
    prefer = {}
    matrix = {"probes": {}, "sets": {}}
    for name, runs in sorted(recs.items()):
        # prefer the final (largest sha-independent) run: the survived-mode receipt when
        # the plain one is an exit-64 refusal
        runs = [r for r in runs if r["exit"] != 64]
        if not runs:
            matrix["sets"][name] = {"refused": True,
                                    "receipts": [r["receipt"] for r in recs[name]]}
            continue
        r = runs[-1]
        prefer[name] = r
        matrix["sets"][name] = r
        print(f"{name:32s} cells={r['cells']:2d} ok={r['cells_ok']:2d} "
              f"survived={r['survived']} caught={r['caught']} "
              f"cell={r['expect_cell']} cell_ok={r['cell_ok']} sha={r['probe_sha256'][:12]}")
        if r["red"]:
            print(f"{'':32s} red={r['red']}")
    (OUT / "matrix_final.json").write_text(json.dumps(matrix, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
