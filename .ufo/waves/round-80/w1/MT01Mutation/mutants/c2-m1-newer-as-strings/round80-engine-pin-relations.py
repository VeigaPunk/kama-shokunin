#!/usr/bin/env python3
"""round80-engine-pin-relations.py - round-80 C2 (freshness): every pinned engine ref related.

PREDICATE (frozen: plans/round-80-claims.md section C2):

    `python3 tools/round80-engine-pin-relations.py --repo <lane>` prints one
    `PIN_RELATIONS engines=3 refs=5 unexplained=0` line and exits 0 only when
    `registry/engine-pin-relations.tsv` carries one dated row for every engine in
    `registry/engine-pins.tsv` and for the two llama.cpp references the lane cites from other
    rows (S553's commit anchor and kengaku's S178 tag b7200), each row's `newest`/`newer`/
    `relation` cells equal the live `git ls-remote --tags` computation over that engine's
    repository (or its committed tag list under `--tags-dir`), a tag row names a release tag
    that exists upstream, a commit row's 40-hex anchor is not any upstream tag's peeled oid,
    and every row's receipt path exists and is committed.

Grading note (freeze divergence 2, recorded in corpus/lessons/round-80.md): the plan's last
clause is graded as a label rule, not as a fixed verdict. A commit row labelled
`not-a-release-tag` must not equal any tag's peeled oid; a commit row labelled `tag:<name>`
must re-derive that tag's peeled oid. Reconnaissance before the freeze measurement found
39febd2adb947b70da35e95f9351b3bf58ad170a is tag b11963's peeled commit, so its row is
labelled `tag:b11963`; a row that silently mislabels the anchor fails either way.

Register (`registry/engine-pin-relations.tsv`, tab-separated, header then rows):

    engine  ref  kind  role  relation  newer  newest  receipt  dated

  engine    an engine named by registry/engine-pins.tsv
  ref       the pinned tag, or a 40-hex commit anchor
  kind      tag | commit
  role      where the ref is held (engine-pins.tsv, a source row, a cross-lane row)
  relation  current | behind | tag:<name> | not-a-release-tag
  newer     release tags with a greater version key than the ref, or `-`
  newest    the engine's newest release tag, or `-`
  receipt   repo-relative committed tag list this row was computed from
  dated     ISO date of that computation

Usage: round80-engine-pin-relations.py --repo DIR [--tags-dir DIR] [--pins FILE]
       [--register FILE] [--tip REV] [--json] | --selftest

Exit: 0 every row and the coverage set re-derive; 1 at least one unexplained row or a missing
required ref; 2 could-not-evaluate (register or tag list unreadable) -- never silently 0.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PINS = "registry/engine-pins.tsv"
REGISTER = "registry/engine-pin-relations.tsv"
HEADER = "engine\tref\tkind\trole\trelation\tnewer\tnewest\treceipt\tdated"
CROSS_REFS = (
    ("llama.cpp", "39febd2adb947b70da35e95f9351b3bf58ad170a"),
    ("llama.cpp", "b7200"),
)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
HEX40 = re.compile(r"[0-9a-f]{40}")


class CouldNotEvaluate(Exception):
    pass


def read_tsv(path: Path, header: str) -> list[list[str]]:
    if not path.is_file():
        raise CouldNotEvaluate(f"missing {path}")
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or lines[0].rstrip("\r") != header:
        raise CouldNotEvaluate(f"{path}: header is not {header!r}")
    rows = []
    for number, line in enumerate(lines[1:], 2):
        cells = line.split("\t")
        if len(cells) != len(header.split("\t")):
            raise CouldNotEvaluate(f"{path}:{number}: expected {len(header.split(chr(9)))} cells")
        rows.append(cells)
    return rows


def load_pins(repo: Path, pins: str) -> list[dict[str, str]]:
    rows = read_tsv(repo / pins, "engine\trepo\ttag_regex\tpin\tsource")
    return [{"engine": r[0].strip(), "repo": r[1].strip(), "regex": r[2].strip(),
             "pin": r[3].strip(), "source": r[4].strip()} for r in rows]


def tag_text(repo: Path, engine: str, url: str, tags_dir: str | None) -> str:
    if tags_dir:
        path = Path(tags_dir) / f"{engine}.txt"
        if not path.is_file():
            raise CouldNotEvaluate(f"missing committed tag list {path}")
        return path.read_text(encoding="utf-8")
    if url.startswith("-"):
        raise CouldNotEvaluate(f"refused tag source {url!r}")
    proc = subprocess.run(["git", "ls-remote", "--tags", url], capture_output=True, text=True,
                          timeout=300)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git ls-remote --tags {url} exit={proc.returncode}: "
                               f"{proc.stderr.strip()}")
    return proc.stdout


def tag_index(text: str) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        oid, ref = line.split("\t", 1)
        if not ref.startswith("refs/tags/"):
            continue
        name = ref[len("refs/tags/"):]
        if name.endswith("^{}"):
            index.setdefault(name[:-3], {})["peeled"] = oid
        else:
            index.setdefault(name, {})["oid"] = oid
    return index


def release_tags(index: dict[str, dict[str, str]], regex: str) -> dict[str, tuple[tuple[int, ...], str]]:
    pattern = re.compile(regex)
    out = {}
    for name, info in index.items():
        m = pattern.fullmatch(name)
        if not m:
            continue
        groups = [g for g in m.groups() if g is not None]
        if not groups or not all(g.isdigit() for g in groups):
            continue
        out[name] = (".".join(groups), info.get("peeled") or info.get("oid", ""))
    return out


def receipt_committed(repo: Path, path: str, tip: str) -> bool:
    proc = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{tip}:{path}"],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        return True
    return (repo / path).is_file()


def grade(pins: list[dict[str, str]], rows: list[list[str]], releases: dict[str, dict],
          repo: Path | None, tip: str, cross_refs=CROSS_REFS) -> dict:
    findings: list[str] = []
    by_engine = {p["engine"]: p for p in pins}
    seen: dict[tuple[str, str], int] = {}
    for number, row in enumerate(rows, 2):
        engine, ref, kind, role, relation, newer, newest, receipt, dated = (c.strip() for c in row)
        detail = f"line {number} {engine} {ref}"
        if engine not in by_engine:
            findings.append(f"PIN_RELATIONS_FINDING unknown-engine {detail}")
            continue
        if not role:
            findings.append(f"PIN_RELATIONS_FINDING empty-role {detail}")
            continue
        if not DATE.fullmatch(dated):
            findings.append(f"PIN_RELATIONS_FINDING bad-date {detail} dated={dated}")
            continue
        if repo is not None and not receipt_committed(repo, receipt, tip):
            findings.append(f"PIN_RELATIONS_FINDING missing-receipt {detail} receipt={receipt}")
            continue
        table = releases.get(engine)
        if table is None:
            raise CouldNotEvaluate(f"no tag table for engine {engine}")
        seen[(engine, ref)] = seen.get((engine, ref), 0) + 1
        keys = {name: key for name, (key, _peeled) in table.items()}
        newest_name = max(keys, key=lambda n: keys[n]) if keys else "-"
        if kind == "tag":
            if ref not in table:
                findings.append(f"PIN_RELATIONS_FINDING tag-not-upstream {detail}")
                continue
            key = table[ref][0]
            want_newer = str(sum(1 for k in keys.values() if k > key))
            want_relation = "behind" if int(want_newer) else "current"
            if (newer, newest, relation) != (want_newer, newest_name, want_relation):
                findings.append(
                    f"PIN_RELATIONS_FINDING stale-tag {detail} register="
                    f"{relation}/{newer}/{newest} derived={want_relation}/{want_newer}/{newest_name}")
        elif kind == "commit":
            if not HEX40.fullmatch(ref):
                findings.append(f"PIN_RELATIONS_FINDING bad-anchor {detail}")
                continue
            tips = {peeled: name for name, (_key, peeled) in table.items() if peeled == ref}
            if relation == "not-a-release-tag":
                if tips:
                    findings.append(f"PIN_RELATIONS_FINDING anchor-is-tag-tip {detail} "
                                    f"tag={sorted(tips)[0]}")
                elif (newer, newest) != ("-", "-"):
                    findings.append(f"PIN_RELATIONS_FINDING stale-commit {detail} "
                                    f"register={newer}/{newest} derived=-/-")
            elif relation.startswith("tag:"):
                name = relation[4:]
                if name not in table or table[name][1] != ref:
                    findings.append(f"PIN_RELATIONS_FINDING tag-label-mismatch {detail} "
                                    f"label={relation}")
                    continue
                key = table[name][0]
                want_newer = str(sum(1 for k in keys.values() if k > key))
                want_relation = f"tag:{name}"
                if (newer, newest, relation) != (want_newer, newest_name, want_relation):
                    findings.append(
                        f"PIN_RELATIONS_FINDING stale-commit {detail} register="
                        f"{relation}/{newer}/{newest} derived={want_relation}/{want_newer}/{newest_name}")
            else:
                findings.append(f"PIN_RELATIONS_FINDING bad-relation {detail} relation={relation}")
        else:
            findings.append(f"PIN_RELATIONS_FINDING bad-kind {detail} kind={kind}")
    required = [(p["engine"], p["pin"]) for p in pins] + list(cross_refs)
    for engine, ref in required:
        if (engine, ref) not in seen:
            findings.append(f"PIN_RELATIONS_FINDING missing-ref engine={engine} ref={ref}")
    for pair, count in seen.items():
        if count > 1:
            findings.append(f"PIN_RELATIONS_FINDING duplicate-row engine={pair[0]} ref={pair[1]}")
    engines = sorted({engine for engine, _ in seen})
    summary = {"engines": len(engines), "refs": len(rows), "unexplained": len(findings)}
    return {"summary": summary, "findings": findings, "required": required}


def render(result: dict) -> str:
    s = result["summary"]
    lines = ["PIN_RELATIONS " + " ".join(f"{k}={v}" for k, v in s.items())]
    lines.extend(result["findings"])
    return "\n".join(lines)


def evaluate(repo: Path, tags_dir: str | None, pins_path: str, register_path: str,
             tip: str) -> dict:
    pins = load_pins(repo, pins_path)
    rows = read_tsv(repo / register_path, HEADER)
    releases = {}
    for pin in pins:
        text = tag_text(repo, pin["engine"], pin["repo"], tags_dir)
        releases[pin["engine"]] = release_tags(tag_index(text), pin["regex"])
    return grade(pins, rows, releases, repo, tip)


def selftest() -> int:
    pins = [
        {"engine": "alpha", "repo": "https://example.invalid/alpha.git", "regex": r"v(\d+)\.(\d+)",
         "pin": "v1.0", "source": "S1"},
        {"engine": "beta", "repo": "https://example.invalid/beta.git", "regex": r"b(\d+)",
         "pin": "b10", "source": "S2"},
        {"engine": "gamma", "repo": "https://example.invalid/gamma.git", "regex": r"g(\d+)",
         "pin": "g1", "source": "S3"},
    ]
    gamma_tip = "e" * 40
    results = []

    def tags(pairs: list[tuple[str, str]]) -> str:
        return "\n".join(f"{oid}\trefs/tags/{name}" for name, oid in pairs) + "\n"

    def row(engine, ref, kind, relation, newer, newest, receipt="r.txt", dated="2026-11-04"):
        return [engine, ref, kind, "role", relation, newer, newest, receipt, dated]

    def fixtures(root: Path) -> dict[str, dict]:
        (root / "r.txt").write_text("tags\n")
        (root / "alpha.txt").write_text(tags([("v1.0", "a" * 40), ("v1.1", "b" * 40)]))
        (root / "beta.txt").write_text(tags([("b10", "c" * 40), ("b11", "d" * 40)]))
        (root / "gamma.txt").write_text(
            tags([("g1", "f" * 40)]) + f"{gamma_tip}\trefs/tags/g2^{{}}\n")
        return {
            "alpha": release_tags(tag_index((root / "alpha.txt").read_text()), r"v(\d+)\.(\d+)"),
            "beta": release_tags(tag_index((root / "beta.txt").read_text()), r"b(\d+)"),
            "gamma": release_tags(tag_index((root / "gamma.txt").read_text()), r"g(\d+)"),
        }

    def case(name: str, rows: list[list[str]], want: int, finding: str | None = None,
             cross=()) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            releases = fixtures(root)
            result = grade(pins, rows, releases, root, "HEAD", cross_refs=cross)
            got = 0 if not result["findings"] else 1
            ok = got == want and (finding is None or any(finding in f for f in result["findings"]))
            results.append((name, ok, got, want, result["findings"][:2]))

    green = [row("alpha", "v1.0", "tag", "behind", "1", "v1.1"),
             row("beta", "b10", "tag", "behind", "1", "b11"),
             row("gamma", "g1", "tag", "behind", "1", "g2")]
    case("green", green, 0)
    case("missing-engine", green[:2], 1, "missing-ref engine=gamma")
    case("missing-crossref", green, 1, "missing-ref engine=llama.cpp", cross=CROSS_REFS)
    case("stale-newer", [row("alpha", "v1.0", "tag", "behind", "0", "v1.1")] + green[1:], 1,
         "stale-tag")
    case("stale-relation", [row("alpha", "v1.0", "tag", "current", "1", "v1.1")] + green[1:], 1,
         "stale-tag")
    case("tag-not-upstream", [row("alpha", "v9.9", "tag", "current", "0", "v1.1")] + green[1:], 1,
         "tag-not-upstream")
    case("anchor-is-tag-tip",
         green[:2] + [row("gamma", gamma_tip, "commit", "not-a-release-tag", "-", "-")], 1,
         "anchor-is-tag-tip")
    case("commit-green",
         green + [row("gamma", gamma_tip, "commit", "tag:g2", "0", "g2")], 0)
    case("tag-label-mismatch",
         green + [row("gamma", gamma_tip, "commit", "tag:g1", "1", "g2")], 1,
         "tag-label-mismatch")
    case("missing-receipt", [row("alpha", "v1.0", "tag", "behind", "1", "v1.1", receipt="nope.txt")]
         + green[1:], 1, "missing-receipt")
    case("bad-date", [row("alpha", "v1.0", "tag", "behind", "1", "v1.1", dated="04.11.2026")]
         + green[1:], 1, "bad-date")
    case("duplicate-row", green + [green[0]], 1, "duplicate-row")
    failed = 0
    for name, ok, got, want, findings in results:
        failed += not ok
        print(f"PIN_RELATIONS_SELFTEST {name} {'PASS' if ok else 'FAIL'} exit={got} expected={want}")
        if not ok:
            print("  findings", findings)
    print(f"PIN_RELATIONS_SELFTEST pass={len(results) - failed} fail={failed}")
    return int(bool(failed))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--tags-dir")
    parser.add_argument("--pins", default=PINS)
    parser.add_argument("--register", default=REGISTER)
    parser.add_argument("--tip", default="master")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = Path(args.repo).resolve()
    try:
        result = evaluate(repo, args.tags_dir, args.pins, args.register, args.tip)
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
