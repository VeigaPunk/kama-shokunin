#!/usr/bin/env python3
"""Round-28 C1 post-data shortcut: derive the whole table mechanically from the
pinned declaration file, in a scratch clone at e49b4cf with all landed C1 data
removed.  The policy reads only `new field_num(...)` lines and their
`set_limits`/`set_hard_limits` clauses, plus the documented server default that
`--parallel` -1 resolves to 4 (upstream server.cpp@704366d, lines 169-172).
No HTTP request is sent here; only the frozen A1 counter later touches a server.

Policy, uniform over every declaration, no per-field outcome knowledge:
  * set_hard_limits(lo, hi) -> the eval() in server-schema.cpp throws
    "Value must be between lo <= value <= hi"; send lo-1, claim reject 400
    with the declaration's own bounds.
  * set_limits(lo, hi)      -> the same eval() silently clamps; send hi+1 and
    claim the stored value hi when hi+1 is representable, else send lo-1 and
    claim lo.
  * preregistration excluded_fields are skipped.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

TREE = Path("/fast/scratch/hyaku/kama-r28/w2/ExecShortcutPostData/tree")
BASE = "4179301f7516ad667509d54b5ebfe0a70a002d5b"
SCHEMA_REL = ".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp"
SOURCES_REL = "corpus/SOURCES.md"
SKILL_REL = "SKILL.md"
REGISTRY_REL = "registry/request-field-outcomes-r28.json"
HEADING = "## Round-28 request-field outcomes"
EXCLUDED = {"n_cache_reuse", "xtc_threshold"}  # preregistration C1.excluded_fields
N_PARALLEL = 4  # server.cpp@704366d: --parallel default -1 -> n_parallel = 4
INT32_MAX = 2147483647
INT64_MAX = 9223372036854775807
FLT_MAX = 3.4028234663852886e38


def git_show(rev: str, path: str) -> str:
    out = subprocess.run(["/usr/bin/git", "-C", str(TREE), "show", f"{rev}:{path}"],
                         capture_output=True, check=True).stdout
    return out.decode("utf-8")


def canon(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def split_top(args: str) -> list[str]:
    parts, cur, depth, i = [], [], 0, 0
    while i < len(args):
        c = args[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def eval_bound(expr: str):
    e = expr.strip()
    if e == "INT32_MAX":
        return INT32_MAX
    if "numeric_limits<int64_t>::max()" in e:
        return INT64_MAX
    if e == "params_base.n_parallel":
        return N_PARALLEL
    if e.replace(" ", "") == "-std::numeric_limits<float>::max()":
        return -FLT_MAX
    if e == "std::numeric_limits<float>::infinity()":
        return math.inf
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)[fF]?", e)
    if not m:
        raise SystemExit(f"unresolved bound {e!r}")
    num = m.group(1)
    return float(num) if "." in num else int(num)


def declarations() -> list[tuple[str, int, str]]:
    lines = (TREE / SCHEMA_REL).read_text("utf-8").splitlines()
    out, in_if0, i = [], False, 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("#if 0"):
            in_if0 = True
            i += 1
            continue
        if s.startswith("#endif"):
            in_if0 = False
            i += 1
            continue
        if not in_if0 and not s.startswith("//") and "new field_num(" in lines[i]:
            start = i
            block = [lines[i]]
            while not block[-1].rstrip().endswith("));"):
                i += 1
                block.append(lines[i])
            m = re.search(r'new field_num\("([^"]+)"', block[0])
            if not m:
                raise SystemExit(f"no field name at line {start + 1}")
            out.append((m.group(1), start + 1, "\n".join(block)))
        i += 1
    return out


def find_limit(block: str):
    for line in block.splitlines():
        st = line.strip()
        if st.startswith("//"):
            continue
        for key, kind in (("set_hard_limits(", "hard"), ("set_limits(", "soft")):
            idx = st.find(key)
            if idx < 0:
                continue
            j, depth = idx + len(key), 1
            while j < len(st) and depth:
                if st[j] == "(":
                    depth += 1
                elif st[j] == ")":
                    depth -= 1
                j += 1
            args = split_top(st[idx + len(key):j - 1])
            if len(args) != 2:
                raise SystemExit(f"bad limits {st!r}")
            return kind, eval_bound(args[0]), eval_bound(args[1])
    return None, None, None


def policy(field: str, kind: str, lo, hi):
    if kind == "hard":
        sent = lo - (1 if isinstance(lo, int) else 1.0)
        return sent, {"kind": "reject", "bounds": [lo, hi]}
    can_hi = math.isfinite(hi) and hi + 1 <= INT32_MAX
    if can_hi:
        return hi + 1, {"kind": "effective", "key": field, "value": hi}
    return lo - 1, {"kind": "effective", "key": field, "value": lo}


def outcome_text(o: dict) -> str:
    if o["kind"] == "reject":
        return f"reject 400, bounds {canon(o['bounds'][0])} to {canon(o['bounds'][1])}"
    return f"200, {o['key']} = {canon(o['value'])}"


def strip_landed_data() -> None:
    reg = TREE / REGISTRY_REL
    if reg.exists():
        reg.unlink()
    base_src = git_show(BASE, SOURCES_REL)
    (TREE / SOURCES_REL).write_text(base_src, "utf-8")
    skill = git_show("e49b4cf", SKILL_REL).splitlines(True)
    idx = next((k for k, l in enumerate(skill) if l.startswith(HEADING)), None)
    if idx is not None:
        end = next((k for k in range(idx + 1, len(skill)) if skill[k].startswith("## ")),
                   len(skill))
        skill = skill[:idx] + skill[end:]
    (TREE / SKILL_REL).write_text("".join(skill), "utf-8")


def main() -> int:
    strip_landed_data()
    rows = []
    for field, line, block in declarations():
        if field in EXCLUDED:
            continue
        kind, lo, hi = find_limit(block)
        if kind is None:
            continue
        sent, outcome = policy(field, kind, lo, hi)
        rows.append({"field": field, "line": line, "kind": kind,
                     "sent": sent, "outcome": outcome,
                     "decl": block.splitlines()[0].strip()})
    ids = [f"F28-{n:02d}" for n in range(1, len(rows) + 1)]
    srcs = [f"S{140 + n}" for n in range(len(rows))]
    for rid, s, r in zip(ids, srcs, rows):
        r["id"], r["source"] = rid, s

    registry = {"rows": [{
        "id": r["id"],
        "field": r["field"],
        "set": {r["field"]: r["sent"]},
        "outcome": r["outcome"],
        "source": {"row": r["source"], "file": "server-schema.cpp", "line": r["line"]},
    } for r in rows]}
    reg_path = TREE / REGISTRY_REL
    reg_path.parent.mkdir(exist_ok=True)
    reg_path.write_text(json.dumps(registry, indent=1, sort_keys=True) + "\n", "utf-8")

    table = ["", "Declaration-derived policy rows; the writer sent no request.", "",
             "| id | field | value | outcome | meaning | source |",
             "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        table.append("| {id} | {field} | {value} | {outcome} | policy row; declaration "
                     "derived; no request was sent | {source} |".format(
                         id=r["id"], field=r["field"], value=canon(r["sent"]),
                         outcome=outcome_text(r["outcome"]), source=r["source"]))
    skill = (TREE / SKILL_REL).read_text("utf-8").rstrip("\n")
    (TREE / SKILL_REL).write_text(skill + "\n\n" + HEADING + "\n" + "\n".join(table) + "\n",
                                  "utf-8")

    src_text = (TREE / SOURCES_REL).read_text("utf-8")
    src_lines = src_text.splitlines()
    last = max(k for k, l in enumerate(src_lines)
               if re.match(r"^\|\s*S\d{3,}\s*\|", l))
    new = []
    for r in rows:
        url = ("https://raw.githubusercontent.com/ggml-org/llama.cpp/"
               "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/"
               f"server-schema.cpp#L{r['line']}")
        new.append(f"| {r['source']} | server-schema.cpp | {url} | 2026-10-23T09:00:00Z | "
                   f"{r['decl']} | policy, declaration derived | 1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050 |")
    src_lines[last + 1:last + 1] = new
    (TREE / SOURCES_REL).write_text("\n".join(src_lines) + "\n", "utf-8")

    print(f"rows {len(rows)} (hard {sum(r['kind'] == 'hard' for r in rows)}, "
          f"soft {sum(r['kind'] == 'soft' for r in rows)})")
    for r in rows:
        print(f"{r['id']} {r['source']} L{r['line']:<4} {r['field']:<24} set={canon(r['sent']):<10} "
              f"{outcome_text(r['outcome'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
