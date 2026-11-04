#!/usr/bin/env python3
"""round81-late-rows.py - generate or check the round-81 late-acceptance register rows.

The rows are a deterministic function of the frozen audit's population at the round base: one row
per undisclosed deleted line of every event that no frozen register row accepts. The note names the
accepting round (the round this generator runs in) and the deletion round parsed from the event
commit's subject, `round-<M>: …`:

    round-81 accepts round-<M> <subject>; accepted historical in-place record edit superseded by
    the round that followed

Usage: round81-late-rows.py --repo DIR --round N [--base REV] [--out FILE]
       [--write | --check] [--json]

  (default)  print the generated TSV (header + rows) to stdout
  --write    write it to <repo>/registry/append-only-late.tsv (refuses an existing registry unless
             --force)
  --check    re-derive the rows and compare them, cell by cell, with the committed register at the
             audited revision; exit 1 on any missing, extra or differing row

Exit: 0 clean; 1 mismatch/findings; 2 could-not-evaluate.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
LATE = "registry/append-only-late.tsv"
PLAN = "plans/round-{round}-claims.md"
BASE_RE = re.compile(r"Base revision `([0-9a-f]{40})`")
SUBJECT_ROUND = re.compile(r"^round-([0-9]+)\b")


class CouldNotEvaluate(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          timeout=180)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git {' '.join(args)} exit={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout


def show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True, timeout=180)
    return proc.stdout if proc.returncode == 0 else None


def is_ancestor(repo: Path, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b],
                          capture_output=True, timeout=180).returncode == 0


def audit(repo: Path, path: str | None) -> dict:
    if path:
        text = Path(path).read_text(encoding="utf-8")
    else:
        proc = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                               "--repo", str(repo), "--json"], capture_output=True, text=True,
                              timeout=300)
        if proc.returncode not in (0, 1):
            raise CouldNotEvaluate(f"audit exit={proc.returncode}: {proc.stderr.strip()}")
        text = proc.stdout
    try:
        return json.loads(text)
    except ValueError as exc:
        raise CouldNotEvaluate(f"audit JSON unreadable: {exc}") from exc


def frozen_covered(repo: Path, to: str, population) -> set:
    """(commit, file, line_sha256) triples the frozen register covers, under its own rule."""
    text = show(repo, to, "registry/append-only-accepted.tsv")
    if text is None:
        raise CouldNotEvaluate(f"no registry/append-only-accepted.tsv at {to}")
    lines = text.splitlines()
    if not lines or lines[0] != HEADER:
        raise CouldNotEvaluate("frozen register header differs")
    covered = set()
    for line in lines[1:]:
        cells = line.split("\t")
        if len(cells) != 6:
            continue
        covered.add((cells[0], cells[1], cells[2]))
    return covered


def generate(repo: Path, round_number: int, to: str, base: str, population) -> list[tuple[str, ...]]:
    covered = frozen_covered(repo, to, population)
    rows = []
    for (commit, file), event in population.items():
        if not is_ancestor(repo, commit, base):
            continue
        subject = git(repo, "log", "-1", "--format=%s", commit).strip()
        match = SUBJECT_ROUND.match(subject)
        if not match:
            raise CouldNotEvaluate(f"event {commit} subject names no round: {subject!r}")
        deletion = match.group(1)
        for entry in event["undisclosed"]:
            triple = (commit, file, entry["line_sha256"])
            if triple in covered:
                continue
            classes = entry["classes"]
            if len(classes) != 1:
                raise CouldNotEvaluate(f"{commit} {file} {entry['line_sha256']}: "
                                       f"ambiguous classes {classes}")
            rest = subject[len(f"round-{deletion}:"):].strip() if subject.startswith(
                f"round-{deletion}:") else subject
            note = (f"round-{round_number} accepts round-{deletion} \"{rest}\"; "
                    f"accepted historical in-place record edit superseded by the round that followed")
            rows.append((commit, file, entry["line_sha256"], str(entry["count"]),
                         classes[0], note.replace("\t", " ")))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--round", type=int, required=True)
    parser.add_argument("--base")
    parser.add_argument("--out")
    parser.add_argument("--audit-json")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        data = audit(repo, args.audit_json)
        to = data.get("to")
        if not isinstance(to, str) or not re.fullmatch(r"[0-9a-f]{40}", to):
            raise CouldNotEvaluate("audit JSON carries no explicit `to` revision")
        plan = show(repo, to, PLAN.format(round=args.round))
        if plan is None:
            raise CouldNotEvaluate("no frozen plan at the audited revision")
        match = BASE_RE.search(plan)
        if not match:
            raise CouldNotEvaluate("the frozen plan declares no `Base revision`")
        base = match.group(1)
        if args.base and args.base != base:
            raise CouldNotEvaluate(f"--base differs from the frozen plan's {base}")
        if not is_ancestor(repo, base, to) and base != to:
            raise CouldNotEvaluate(f"base {base} is not an ancestor of {to}")
        population = {(e["commit"], e["file"]): e for e in data["events"]
                      if e["undisclosed"] and e["status"] != "restored"}
        rows = generate(repo, args.round, to, base, population)
    except (CouldNotEvaluate, OSError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    body = "\n".join("\t".join(row) for row in rows)
    text = HEADER + "\n" + (body + "\n" if body else "")
    if args.check:
        committed = show(repo, to, LATE)
        if committed is None:
            print("LATE_ROWS check=absent rows=0")
            return 1
        have = [tuple(line.split("\t")) for line in committed.splitlines()[1:] if line.strip()]
        want = rows
        missing = [r for r in want if r not in have]
        extra = [r for r in have if r not in want]
        if committed.splitlines()[:1] != [HEADER] or missing or extra:
            for row in missing:
                print(f"LATE_ROWS_FINDING missing {row[0]} {row[1]} {row[2]}")
            for row in extra[:20]:
                print(f"LATE_ROWS_FINDING extra {row[0][:40]} {row[1]} {row[2][:64]}")
            print(f"LATE_ROWS check=fail rows={len(have)} expected={len(want)} "
                  f"missing={len(missing)} extra={len(extra)}")
            return 1
        print(f"LATE_ROWS check=ok rows={len(have)}")
        return 0
    target = Path(args.out) if args.out else repo / LATE
    if args.write:
        if target.exists() and not args.force:
            print(f"refusing to overwrite {target} (use --force)", file=sys.stderr)
            return 2
        target.write_text(text, encoding="utf-8")
        print(f"LATE_ROWS wrote={target} rows={len(rows)}")
        return 0
    if args.json:
        print(json.dumps({"rows": [dict(zip(["commit", "file", "line_sha256", "count",
                                             "class", "note"], row)) for row in rows]}, indent=2))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
