#!/usr/bin/env python3
"""round99-control-population.py - round-99 C1 (operability) frozen grader.

PREDICATE (same sentence as plans/round-99-claims.md section C1):

    `python3 tools/round99-control-population.py --repo . --rev <M1> --work <scratch>
        --counter tools/round99-router-budget.py`
    prints `CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1
    selected=6 ran=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_exit=0 positive_ok=1
    complete=1 mutant_cell_lines=5 positive_cell_lines=6 population_shaped=1 met=True` and exits 0
    at the measured commit M1 (the amendment-1 commit).

    Before (baseline, the same grader): `--rev <BASE> --counter tools/round98-router-budget.py`
    prints `... selected=- ran=5 mutant_control_exit=0 mutant_ok=1 refused=0 ... met=False` and
    exits 1: the round-98 control accepted the dropped-cell mutation.

The mutation is one byte patch, applied to a scratch copy and never to a tracked file: remove the
single line of the counter's cell list that begins `("W14-900k-nd1",`. The mutated copy is invoked
through its real `--control --cells new --expect survived --mutant none` path, where the real probe
passes all six new cells. Both copies are read from `git show <rev>:<counter>` so the graded bytes
are committed bytes.

Criteria (frozen):
  refused  = mutant copy exits nonzero (the population check fired)
  complete = unmutated copy exits 0 with ok=1 (blanket refusal is not a gain)
  population_shaped = 1 only when the mutant control line's selected_ids is exactly the six
             `new` cells, its ran_ids is exactly those six minus the dropped cell, selected=6,
             ran=5, population_ok=0, and its own _CELL stream has at least `ran` lines; the positive
             line's selected_ids and ran_ids are both the six cells and its stream has >= cells
             lines. A fabricated control line, a same-count substitution, a renamed cell, an
             injected cell or a coordinated shrink is therefore refused.
  met      = refused and complete and population_shaped. The `--counter tools/round98-router-budget.py`
             arm is a required negative control: it must print refused=0 and met=False.

Exit: 0 met | 1 not met | 2 could-not-evaluate | 64 usage.
"""

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DROP = "W14-900k-nd1"
SELECTED = 6
EXPECTED6 = {"W14-900k-nd1", "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1",
             "W18-800k-nd1", "W19-520k-nd4"}
CONTROL_RE = re.compile(r"^ROUTER_BUDGET9[89]_CONTROL (.+)$", re.M)


def parse_control(out: str):
    m = CONTROL_RE.search(out)
    if not m:
        return None
    row = {}
    for token in m.group(1).split():
        if "=" in token:
            k, v = token.split("=", 1)
            row[k] = v
    return row


def patch_drop(src: bytes, cell: str):
    text = src.decode("utf-8")
    lines = text.splitlines(keepends=True)
    hits = [i for i, ln in enumerate(lines) if ln.lstrip().startswith(f'("{cell}",')]
    if len(hits) != 1:
        raise SystemExit(f"CONTROL_POP99 could-not-evaluate: cell anchor {cell!r} matched "
                         f"{len(hits)} lines (need exactly 1)")
    del lines[hits[0]]
    out = "".join(lines).encode("utf-8")
    removed = len(src.decode("utf-8").splitlines()) - len(out.decode("utf-8").splitlines())
    return out, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--counter", default="tools/round99-router-budget.py")
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--drop", default=DROP)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    def git(*args):
        p = subprocess.run(["git", "-C", str(a.repo), *args], capture_output=True)
        if p.returncode != 0:
            raise SystemExit(f"CONTROL_POP99 could-not-evaluate: git {' '.join(args)} rc={p.returncode}")
        return p.stdout

    try:
        rev = git("rev-parse", "--verify", a.rev + "^{commit}").decode().strip()
        src = git("show", f"{rev}:{a.counter}")
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"CONTROL_POP99 could-not-evaluate: {e}")
        return 2
    try:
        broken, removed = patch_drop(src, a.drop)
    except SystemExit as e:
        print(str(e))
        return 2

    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="r99-pop-", dir=a.work)).resolve()
    try:
        def invoke(label: str, payload: bytes):
            path = work / f"counter-{label}.py"
            path.write_bytes(payload)
            cmd = [sys.executable, str(path), "--repo", str(a.repo), "--rev", rev,
                   "--work", str(work / f"run-{label}"), "--slow-files", "72",
                   "--control", "--cells", "new", "--expect", "survived", "--mutant", "none"]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout)
            text = p.stdout + p.stderr
            cell_lines = sum(1 for ln in text.splitlines()
                             if ln.startswith("ROUTER_BUDGET99_CELL ") or
                             ln.startswith("ROUTER_BUDGET98_CELL "))
            return p.returncode, text, parse_control(text), cell_lines

        m_exit, m_out, m_row, m_cell_lines = invoke("mutant", broken)
        p_exit, p_out, p_row, p_cell_lines = invoke("positive", src)
    except subprocess.TimeoutExpired:
        print(f"CONTROL_POP99 could-not-evaluate: counter control exceeded {a.timeout}s")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if m_row is None or p_row is None:
        print("CONTROL_POP99 could-not-evaluate: a control run printed no ROUTER_BUDGET99_CONTROL line")
        print(m_out[-600:])
        print(p_out[-600:])
        return 2

    refused = int(m_exit != 0)
    complete = int(p_exit == 0 and p_row.get("ok") == "1")
    population = 0
    try:
        ran = int(m_row.get("ran", m_row.get("cells", "-1")))
        positive = int(p_row.get("cells", "-1"))
    except ValueError:
        ran, positive = -1, -1
    def ids(row, key):
        raw = row.get(key, "")
        return set(x for x in raw.split(",") if x)
    m_sel, m_ran = ids(m_row, "selected_ids"), ids(m_row, "ran_ids")
    p_sel, p_ran = ids(p_row, "selected_ids"), ids(p_row, "ran_ids")
    drop = {a.drop}
    population = int(m_row.get("selected") == str(SELECTED) and
                     ran == SELECTED - removed and
                     m_row.get("population_ok") == "0" and
                     m_sel == EXPECTED6 and m_ran == EXPECTED6 - drop and
                     m_cell_lines >= ran and m_cell_lines > 0 and
                     p_sel == EXPECTED6 and p_ran == EXPECTED6 and
                     p_cell_lines >= positive and p_cell_lines > 0)
    met = int(bool(refused and complete and population))
    print(f"CONTROL_POP99 counter={a.counter} drop={a.drop} patch_removed={removed} "
          f"selected={m_row.get('selected', '-')} ran={m_row.get('ran', m_row.get('cells'))} "
          f"mutant_cells={m_row.get('cells')} mutant_cells_ok={m_row.get('cells_ok')} "
          f"mutant_control_exit={m_exit} mutant_ok={m_row.get('ok')} refused={refused} "
          f"positive_cells={p_row.get('cells')} positive_exit={p_exit} positive_ok={p_row.get('ok')} "
          f"mutant_selected_ids={','.join(sorted(m_sel))} "
          f"mutant_ran_ids={','.join(sorted(m_ran))} "
          f"complete={complete} mutant_cell_lines={m_cell_lines} "
          f"positive_cell_lines={p_cell_lines} population_shaped={population} met={bool(met)} "
          f"counter_sha256={hashlib.sha256(src).hexdigest()} rev={rev}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
