#!/usr/bin/env python3
"""Independently census Claim tables in committed SCORECARD.md at the round-31 tip.

This deliberately does not import or inspect count-c2.py. It records each claim row's
commit-token resolution/ancestry and named-path existence using committed Git objects.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

TIP_DEFAULT = "0e6f8ed6891c09d5208ac1fdcb294ed9a842832e"
REPO_DEFAULT = "/tmp/r31w1-ExecC2CrossCheck"
OUT_DEFAULT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecC2CrossCheck/census.tsv"
GIT = "/usr/bin/git"
SECTION = re.compile(r"^##\s+Round\s+(\d+)\b", re.IGNORECASE)
HEX = re.compile(r"(?<![0-9A-Za-z])([0-9a-fA-F]{7,40})(?![0-9A-Za-z])")
# A broad filename-token recognizer, intentionally independent of the frozen counter.
PATH = re.compile(r"(?<![\w/~:-])((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,12})(?![\w])")


def git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [GIT, "--no-replace-objects", "-C", repo, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def split_cells(line: str) -> list[str] | None:
    text = line.strip()
    if not text.startswith("|"):
        return None
    cells: list[str] = []
    part: list[str] = []
    code_delim = 0
    i = 1
    while i < len(text):
        if text[i] == "`":
            j = i
            while j < len(text) and text[j] == "`":
                j += 1
            run = j - i
            if not code_delim:
                code_delim = run
            elif run == code_delim:
                code_delim = 0
            part.append(text[i:j])
            i = j
            continue
        if text[i] == "|" and not code_delim and (i == 0 or text[i - 1] != "\\"):
            cells.append("".join(part).strip())
            part.clear()
            i += 1
            continue
        part.append(text[i])
        i += 1
    if part or not text.endswith("|"):
        cells.append("".join(part).strip())
    elif text.endswith("|") and cells:
        # The final delimiter closes the last cell; no extra empty cell is needed.
        pass
    return cells


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def claim_rows(scorecard: str) -> list[dict[str, object]]:
    lines = scorecard.splitlines()
    rows: list[dict[str, object]] = []
    current_round = ""
    i = 0
    while i < len(lines):
        section = SECTION.match(lines[i])
        if section:
            current_round = section.group(1)
        header = split_cells(lines[i])
        if header and header[0].strip().casefold() == "claim":
            command_columns = [
                index for index, cell in enumerate(header)
                if cell.strip().casefold().startswith("counting command")
            ]
            j = i + 1
            while j < len(lines):
                cells = split_cells(lines[j])
                if cells is None:
                    break
                if not is_separator(cells) and cells[0].strip():
                    command = cells[command_columns[0]].strip() if command_columns and command_columns[0] < len(cells) else ""
                    exempt = "(exploratory)" in cells[0].casefold() and (
                        not command_columns or command.casefold().startswith("none")
                    )
                    rows.append({
                        "round": current_round,
                        "claim_id": cells[0].strip(),
                        "text": " | ".join(cells),
                        "source_line": j + 1,
                        "exempt": exempt,
                    })
                j += 1
            i = j
            continue
        i += 1
    return rows


def path_variants(path: str, round_number: str) -> list[str]:
    variants = [path]
    if round_number:
        variants.append(f".ufo/waves/round-{round_number}/{path}")
    # Preserve order while avoiding duplicate Git object queries.
    return list(dict.fromkeys(variants))


def safe_cell(value: str) -> str:
    return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=REPO_DEFAULT)
    parser.add_argument("--tip", default=TIP_DEFAULT)
    parser.add_argument("--out", default=OUT_DEFAULT)
    args = parser.parse_args()

    shown = git(args.repo, "show", f"{args.tip}:SCORECARD.md")
    if shown.returncode:
        sys.stderr.write(shown.stderr)
        return 2
    population = claim_rows(shown.stdout)
    token_cache: dict[str, tuple[str, bool, bool]] = {}
    path_cache: dict[str, bool] = {}
    output_rows: list[dict[str, str]] = []

    for number, row in enumerate(population, 1):
        tokens = list(dict.fromkeys(match.group(1).lower() for match in HEX.finditer(row["text"])))
        checks: list[str] = []
        resolved_tokens: list[str] = []
        ancestor_tokens: list[str] = []
        for token in tokens:
            if token not in token_cache:
                resolved = git(args.repo, "rev-parse", "--verify", "--quiet", f"{token}^{{commit}}")
                commit = resolved.stdout.strip() if resolved.returncode == 0 else ""
                ancestor = False
                if commit:
                    anc = git(args.repo, "merge-base", "--is-ancestor", commit, args.tip)
                    if anc.returncode not in (0, 1):
                        raise RuntimeError(f"merge-base failed for {token}: {anc.stderr.strip()}")
                    ancestor = anc.returncode == 0
                token_cache[token] = (commit, bool(commit), ancestor)
            commit, resolves, ancestor = token_cache[token]
            checks.append(f"{token}={commit or 'unresolved'}:{'ancestor' if ancestor else 'not-ancestor' if resolves else 'unresolved'}")
            if resolves:
                resolved_tokens.append(token)
            if ancestor:
                ancestor_tokens.append(token)

        named_paths: list[str] = []
        for match in PATH.finditer(row["text"]):
            path = match.group(1).rstrip(".,;:)")
            stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            if "/" not in path and not any(char.isalpha() or char == "_" for char in stem):
                continue
            if path not in named_paths:
                named_paths.append(path)
        existing: list[str] = []
        path_checks: list[str] = []
        for path in named_paths:
            for candidate in path_variants(path, row["round"]):
                if candidate not in path_cache:
                    checked = git(args.repo, "cat-file", "-e", f"{args.tip}:{candidate}")
                    path_cache[candidate] = checked.returncode == 0
                if path_cache[candidate]:
                    existing.append(f"{path}=>{candidate}")
                    break
            else:
                path_checks.append(f"{path}=missing")
        p1_ok = bool(ancestor_tokens)
        p2_ok = bool(existing)
        failures = []
        if not p1_ok:
            failures.append("p1:no-revision")
        if not p2_ok:
            failures.append("p2:no-evidence-path")
        output_rows.append({
            "row": str(number),
            "source_line": str(row["source_line"]),
            "round": str(row["round"]),
            "claim_id": str(row["claim_id"]),
            "exempt": str(bool(row["exempt"])).lower(),
            "commit_tokens": ";".join(tokens),
            "resolved_tokens": ";".join(resolved_tokens),
            "ancestor_tokens": ";".join(ancestor_tokens),
            "commit_checks": ";".join(checks),
            "named_paths": ";".join(named_paths),
            "existing_paths": ";".join(existing),
            "missing_paths": ";".join(path_checks),
            "p1_ok": str(p1_ok).lower(),
            "p2_ok": str(p2_ok).lower(),
            "own_failures": ";".join(failures) or "none",
            "counter_scope_failures": "none" if row["exempt"] else ";".join(failures) or "none",
        })

    fields = [
        "row", "source_line", "round", "claim_id", "exempt", "commit_tokens", "resolved_tokens",
        "ancestor_tokens", "commit_checks", "named_paths", "existing_paths", "missing_paths",
        "p1_ok", "p2_ok", "own_failures", "counter_scope_failures",
    ]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in output_rows:
            writer.writerow({key: safe_cell(row[key]) for key in fields})

    p1_fail = [row for row in output_rows if row["p1_ok"] == "false" and row["exempt"] != "true"]
    p2_fail = [row for row in output_rows if row["p2_ok"] == "false" and row["exempt"] != "true"]
    both_fail = [row for row in output_rows if row["counter_scope_failures"] == "p1:no-revision;p2:no-evidence-path"]
    print(f"population={len(output_rows)} exempt={sum(row['exempt'] == 'true' for row in output_rows)} "
          f"p1_fail={len(p1_fail)} p2_fail={len(p2_fail)} both_fail={len(both_fail)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
