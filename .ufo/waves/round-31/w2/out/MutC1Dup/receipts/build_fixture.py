#!/usr/bin/env python3
"""Build a twelve-row no-op registry fixture in a scratch clone (MutC1Dup, round 31 w2).

mode distinct : 12 rows, distinct ids K31-N01..K31-N12, every row asserts the base request's own
                max_tokens=1 / n_predict=1 (the no-op shortcut named in C1's open attack).
mode sameid   : 12 rows, one shared id K31-X, same no-op content (control that exercises the
                frozen counter's per-id uniqueness rule).

Only registry/chat-param-outcomes-r31.json and the round-31 SKILL.md table are changed.
corpus/SOURCES.md is untouched; every row cites the existing S189 row.
"""
import json
import sys
from pathlib import Path

HEADING = "## Round-31 chat-completions parameter outcomes"
HEADER = "| id | param | sent | outcome | meaning | source |"
MEANING = ("Alias of the base token budget; this row asserts the value the base "
           "request already sent, not an observed parameter effect.")
ROW_SOURCE = {
    "row": "S189",
    "file": "server-common.cpp",
    "line": 1530,
    "contains": "llama_params[item.key()] = item.value();",
}


def rows_for(mode):
    ids = [f"K31-N{i:02d}" for i in range(1, 13)] if mode == "distinct" else ["K31-X"] * 12
    out = []
    for rid in ids:
        out.append({
            "id": rid,
            "param": "max_tokens",
            "sent": 1,
            "outcome": {"kind": "slot", "set": {"max_tokens": 1, "n_predict": 1}},
            "source": dict(ROW_SOURCE),
        })
    return out


def skill_cell(rid):
    return (f"| {rid} | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | "
            f"{MEANING} | S189 |")


def rewrite_skill(text, mode):
    lines = text.split("\n")
    h = next(i for i, ln in enumerate(lines) if ln.startswith(HEADING))
    j = next(i for i in range(h + 1, len(lines)) if lines[i].strip() == HEADER)
    k = j + 1
    assert lines[k].replace("|", "").replace(" ", "").strip("-:") == ""
    k += 1
    start = k
    while k < len(lines) and lines[k].startswith("|"):
        k += 1
    ids = [f"K31-N{i:02d}" for i in range(1, 13)] if mode == "distinct" else ["K31-X"]
    new_body = [skill_cell(rid) for rid in ids]
    assert k > start, "empty table body"
    return "\n".join(lines[:start] + new_body + lines[k:])


def main():
    mode, repo = sys.argv[1], Path(sys.argv[2])
    assert mode in ("distinct", "sameid"), mode
    reg_path = repo / "registry/chat-param-outcomes-r31.json"
    reg = json.loads(reg_path.read_text())
    reg["rows"] = rows_for(mode)
    reg_path.write_text(json.dumps(reg, indent=1) + "\n")
    skill_path = repo / "SKILL.md"
    skill_path.write_text(rewrite_skill(skill_path.read_text(), mode))
    print(f"fixture {mode}: {len(reg['rows'])} rows, skill rows "
          f"{len({r['id'] for r in reg['rows']})}")


if __name__ == "__main__":
    main()
