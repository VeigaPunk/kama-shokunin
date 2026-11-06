#!/usr/bin/env python3
"""round89-signature-rows.py - round-89 C2 (depth) frozen counter.

PREDICATE (frozen: plans/round-89-claims.md section C2):

    `python3 tools/round89-signature-rows.py --repo <lane> --rev <R>` prints
    `SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0 ...` and exits 0.

Population: the Markdown table rows (lines starting `|`, header and separator excluded) under the
heading line `## Router error signatures (llama.cpp router mode)` of `SKILL.md` at <R>, up to the
next heading. Columns: endpoint | HTTP | message | trigger | probe verdict / action | receipt.
Cells may be wrapped in backticks. A row is BOUND when its receipt (a lane path, read from <R>,
never the worktree) is a JSON-lines file holding a line L with
    L.server_sha256 == the pinned b12177 llama-server sha256,
    L.endpoint == the row endpoint, L.http == the row HTTP code, and
    json(L.body).error.message == the row message with `<id>` replaced by L.request.model
(exact string equality). Every other row is UNBOUND (missing receipt, wrong build, no matching
line, unparseable cells). A row repeating an earlier row's (endpoint, HTTP, message) is a
DUPLICATE and is not counted as bound.

Usage: round89-signature-rows.py --repo DIR --rev REV
Exit: 0 unbound=0 and duplicates=0 and bound>=1 | 1 otherwise | 2 could-not-evaluate.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

HEADING = "## Router error signatures (llama.cpp router mode)"
SERVER_PIN = "ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0"


def show(repo: str, rev: str, path: str):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def cell(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "`" and s[-1] == "`":
        s = s[1:-1]
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    r = subprocess.run(["git", "-C", a.repo, "rev-parse", "--verify", a.rev + "^{commit}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"SIGNATURE_ROWS could-not-evaluate: unresolvable --rev {a.rev}")
        return 2
    rev = r.stdout.strip()
    skill = show(a.repo, rev, "SKILL.md")
    if skill is None:
        print("SIGNATURE_ROWS could-not-evaluate: SKILL.md absent at rev")
        return 2
    lines = skill.splitlines()
    rows, inside = [], False
    for ln in lines:
        if ln.startswith("#"):
            inside = ln.rstrip() == HEADING
            continue
        if inside and ln.startswith("|"):
            parts = ln.strip().strip("|").split("|")
            if all(re.fullmatch(r"\s*:?-+:?\s*", p) for p in parts):
                continue
            if parts and parts[0].strip().lower() == "endpoint":
                continue
            rows.append(parts)
    bound = unbound = dup = 0
    seen = set()
    receipts: dict[str, list] = {}
    for parts in rows:
        verdict = "unbound"
        try:
            endpoint, code, message, receipt = cell(parts[0]), int(cell(parts[1])), cell(parts[2]), cell(parts[5])
        except (IndexError, ValueError):
            print(f"SIGNATURE_ROW unbound unparseable {'|'.join(parts)[:120]!r}")
            unbound += 1
            continue
        key = (endpoint, code, message)
        if key in seen:
            dup += 1
            print(f"SIGNATURE_ROW duplicate {endpoint} {code} {message!r}")
            continue
        seen.add(key)
        if receipt not in receipts:
            txt = show(a.repo, rev, receipt)
            recs = []
            for l in (txt or "").splitlines():
                try:
                    recs.append(json.loads(l))
                except ValueError:
                    pass
            receipts[receipt] = recs
        for L in receipts[receipt]:
            try:
                if L.get("server_sha256") != SERVER_PIN or L.get("endpoint") != endpoint or L.get("http") != code:
                    continue
                got = json.loads(L["body"])["error"]["message"]
                want = message.replace("<id>", str((L.get("request") or {}).get("model", "")))
                if got == want:
                    verdict = "bound"
                    break
            except (ValueError, KeyError, TypeError):
                continue
        if verdict == "bound":
            bound += 1
        else:
            unbound += 1
        print(f"SIGNATURE_ROW {verdict} {endpoint} {code} {message!r} receipt={receipt}")
    print(f"SIGNATURE_ROWS rows={len(rows)} bound={bound} unbound={unbound} duplicates={dup} rev={rev}")
    return 0 if unbound == 0 and dup == 0 and bound >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
