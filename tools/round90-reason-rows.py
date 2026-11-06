#!/usr/bin/env python3
"""round90-reason-rows.py - round-90 C2 (depth) frozen counter.

PREDICATE (frozen: plans/round-90-claims.md section C2):

    `python3 tools/round90-reason-rows.py --repo <lane> --rev <R>` prints
    `REASON_ROWS population=23 documented=23 ... unbound=0 missing=0 duplicates=0` and exits 0:
    every reason code of the frozen population below has a row in the `SKILL.md` table under the
    exact heading `## Probe reason codes`, and every row of that table is bound to a captured
    probe answer.

Population (frozen; every reason `tools/kama-probe.sh` can print at the round-90 base
99cdb4d6, read from its `C_REASON=` / `RT_REASON=` assignments, lines 770-911):
  connection-refused timeout empty-reply connection-reset no-http-response http-401 http-403
  llamacpp-loading expected-wildcard matched unresolvable-id served-id-mismatch html-non-model
  schema-unrecognized non-model-2xx non-2xx-non-model-http router-sleeping router-unloaded-autoload
  router-loading router-downloading router-model-missing router-model-invalid router-unloaded
Excluded: `dns-failure` (curl rc 6) - `fetch` always targets the literal 127.0.0.1, so no answer
can produce it; `router-<value>` / `router-<value>-failed` for status values outside the router's
vocabulary (open set; `router-unloaded` is the population's representative of the `down` branch).

Rows: column-0 lines starting with `|` inside the section (from the heading line to the next
line starting with `## `), outside backtick/tilde fences, skipping the header row and the
separator row. Columns: `reason` | `verdict` | trigger (prose) | `cell`. The reason, verdict and
cell cells must each be exactly one backticked token.

Binding: a row is bound when the receipt `.ufo/waves/round-90/measured/reason-cells.jsonl` at <R>
exists, EVERY receipt line's `probe_sha256` equals sha256(`git show <R>:tools/kama-probe.sh`), and
one receipt line has `cell` == the row's cell, `reason` == the row's reason and `verdict` == the
row's verdict. A stale receipt (any other probe hash) binds nothing.

Counts: rows; documented = population reasons with at least one row; missing = population minus
documented; bound / unbound over rows; duplicates = rows whose reason already had a row above;
additional = bound rows whose reason is outside the population (reported, not a failure).
Exit: 0 when missing=0 unbound=0 duplicates=0 | 1 otherwise | 2 could-not-evaluate (bad --rev).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys


POPULATION = (
    "connection-refused timeout empty-reply connection-reset no-http-response http-401 http-403 "
    "llamacpp-loading expected-wildcard matched unresolvable-id served-id-mismatch html-non-model "
    "schema-unrecognized non-model-2xx non-2xx-non-model-http router-sleeping router-unloaded-autoload "
    "router-loading router-downloading router-model-missing router-model-invalid router-unloaded"
).split()
assert len(POPULATION) == 23 and len(set(POPULATION)) == 23
HEADING = "## Probe reason codes"
RECEIPT = ".ufo/waves/round-90/measured/reason-cells.jsonl"
TOKEN = re.compile(r"^`([^`\s]+)`$")


def show(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def rows_of(skill: str):
    out, inside, fence = [], False, None
    for line in skill.split("\n"):
        if not inside:
            if line.rstrip() == HEADING:
                inside = True
            continue
        if line.startswith("## "):
            break
        m = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if m:
            mark = m.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not line.strip()[len(mark):].strip():
                fence = None
            continue
        if fence is not None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            continue
        out.append(cells)
    if out and out[0] and out[0][0].lower() == "reason":
        out = out[1:]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    rv = subprocess.run(["git", "-C", a.repo, "rev-parse", "--verify", a.rev + "^{commit}"],
                        capture_output=True, text=True)
    if rv.returncode != 0:
        print(f"REASON_ROWS could-not-evaluate: unresolvable --rev {a.rev}")
        return 2
    rev = rv.stdout.strip()
    skill = (show(a.repo, rev, "SKILL.md") or b"").decode("utf-8", "replace")
    probe = show(a.repo, rev, "tools/kama-probe.sh") or b""
    probe_sha = hashlib.sha256(probe).hexdigest()
    rec_raw = show(a.repo, rev, RECEIPT)
    receipt, stale = [], False
    if rec_raw is not None:
        for line in rec_raw.decode("utf-8", "replace").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except Exception:
                stale = True
                continue
            if d.get("probe_sha256") != probe_sha:
                stale = True
            receipt.append(d)
    keys = set() if (stale or rec_raw is None) else {(d.get("cell"), d.get("reason"), d.get("verdict")) for d in receipt}

    rows = rows_of(skill)
    seen, bound, unbound, dup, additional = set(), 0, 0, 0, 0
    for cells in rows:
        toks = [TOKEN.match(c) for c in cells]
        ok = len(cells) == 4 and toks[0] and toks[1] and toks[3]
        reason = toks[0].group(1) if len(cells) >= 1 and toks[0] else (cells[0] if cells else "")
        if reason in seen:
            dup += 1
        seen.add(reason)
        if ok and (toks[3].group(1), reason, toks[1].group(1)) in keys:
            bound += 1
            additional += reason not in POPULATION
            print(f"REASON_ROW {reason} bound=1")
        else:
            unbound += 1
            print(f"REASON_ROW {reason} bound=0")
    documented = sum(1 for r in POPULATION if r in seen)
    missing = 23 - documented
    for r in POPULATION:
        if r not in seen:
            print(f"REASON_MISSING {r}")
    print(f"REASON_ROWS population=23 documented={documented} rows={len(rows)} bound={bound} "
          f"unbound={unbound} missing={missing} duplicates={dup} additional={additional} "
          f"receipt={'absent' if rec_raw is None else ('stale' if stale else 'current')} "
          f"probe_sha256={probe_sha} rev={rev}")
    return 0 if (missing == 0 and unbound == 0 and dup == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
