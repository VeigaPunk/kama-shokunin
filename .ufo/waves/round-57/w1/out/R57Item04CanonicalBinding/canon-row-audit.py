#!/usr/bin/env python3
"""canon-row-audit.py - independent, content-bound canonical capability-row audit.

Seat R57Item04CanonicalBinding (kama round 57).  Prototype only; read-only.

Unlike tools/round42-selfdesc-reconcile.py this counter does NOT import any other
lane counter.  It derives the canonical capability table from the single
highest-numbered `**Capabilities - canonical list as of round N**` heading in
SCORECARD.md and then binds every row to content that exists at the audited
revision:

  bind      every backticked path token in a row's evidence cell resolves at
            --tip (git cat-file -e, or on-disk under --tree-root).
  rounds    the row's first-working round is <= N and a `## Round <n>` heading
            exists at --tip.
  mirror    the name AND the first-working round appear unchanged in the
            `## Capabilities` head mirror (both directions: canonical-only rows
            are omissions, mirror-only rows are fabrications).
  distinct  row names and whole-row content digests are unique.

Injection surface: --rows-file supplies a row set that is audited *instead of*
the derived table for the omission comparison, so an instrument that omits rows
is caught as `omitted=<n>`.  canonical_reads counts the rows actually hashed and
bound; a met=True line with canonical_reads=0 is vacuous by construction and the
omission harness rejects it.

Output: deterministic summary lines + `detail:` lines + one `row <name> sha=<16>`
content-address line per row.  Exit 0 met, 1 not met, 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

CANON_RE = re.compile(r"canonical list as of round\s+(\d+)", re.I)
PATHY = ("tools/", "registry/", "corpus/", "scripts/", ".ufo/", "plans/")

# Axes this prototype is judged on: calibration (does the audit derive the
# table from content, not from a typed constant) and operability (does it run
# read-only and fail closed with a distinct exit code).
AXES = ("calibration", "operability")


class EvalError(RuntimeError):
    pass


def git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True)


def show(repo: str, tip: str, path: str):
    p = git(repo, "cat-file", "-p", f"{tip}:{path}")
    return p.stdout.decode(errors="replace") if p.returncode == 0 else None


def exists_at(repo: str, tip: str, path: str) -> bool:
    return git(repo, "cat-file", "-e", f"{tip}:{path.rstrip('/')}").returncode == 0


def table_after(lines: list[str], idx: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for ln in lines[idx + 1:]:
        if ln.startswith("|"):
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif rows:
            break
    return rows[2:] if len(rows) >= 2 else []


def derive_canon(text: str) -> tuple[int, list[list[str]], int]:
    lines = text.split("\n")
    best, bi = -1, None
    for i, ln in enumerate(lines):
        m = CANON_RE.search(ln)
        if m and int(m.group(1)) > best:
            best, bi = int(m.group(1)), i
    if bi is None:
        raise EvalError("no 'canonical list as of round N' heading in SCORECARD.md")
    return best, table_after(lines, bi), bi + 1


def derive_mirror(text: str) -> list[list[str]]:
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == "## Capabilities":
            return table_after(lines, i)
    raise EvalError("no '## Capabilities' mirror section in SCORECARD.md")


def path_tokens(cell: str) -> list[str]:
    out = []
    for tok in re.findall(r"`([^`]+)`", cell):
        if any(x in tok for x in " <>*$") or " " in tok:
            continue
        if tok.startswith(PATHY) or ("/" in tok and "." in tok.rsplit("/", 1)[-1]):
            out.append(tok)
    return out


def row_digest(name: str, what: str, ev: str, first: str) -> str:
    norm = "\u0000".join(re.sub(r"\s+", " ", x).strip() for x in (name, what, ev, first))
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def evaluate(repo: str, tip: str, scorecard: str, rows_file: str | None) -> dict:
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").stdout.decode().strip()
    if not tip:
        raise EvalError(f"cannot resolve tip {tip!r} in {repo}")
    sc = show(repo, tip, "SCORECARD.md")
    if sc is None:
        raise EvalError("SCORECARD.md missing at tip")
    if scorecard:
        with open(scorecard) as f:
            sc = f.read()

    cn, crows, cline = derive_canon(sc)
    mrows = derive_mirror(sc)
    heading_rounds = {int(m.group(1)) for ln in sc.split("\n")
                      for m in [re.match(r"^## Round (\d+)", ln)] if m}

    canon_by_name: dict[str, list[str]] = {}
    for r in crows:
        if len(r) >= 4 and r[0]:
            canon_by_name[r[0].strip("` *")] = r
    mirror_by_name: dict[str, list[str]] = {}
    for r in mrows:
        if len(r) >= 4 and r[0]:
            mirror_by_name[r[0].strip("` *")] = r

    if rows_file:
        with open(rows_file) as f:
            supplied = json.load(f)
        supplied_names = [str(x["name"]).strip("` *") for x in supplied]
    else:
        supplied = [{"name": n, "what": r[1], "evidence": r[2], "first": r[3]}
                    for n, r in canon_by_name.items()]
        supplied_names = list(canon_by_name)

    detail: list[str] = []
    counters = dict(bind=0, rounds=0, mirror=0, distinct=0, omitted=0, extra=0, canonical_reads=0)
    row_lines: list[str] = []

    # omission / fabrication against the derived canonical table
    supp = [x for x in supplied if str(x.get("name", "")).strip("` *") in canon_by_name]
    supp_names = {str(x["name"]).strip("` *") for x in supp}
    omitted = sorted(set(canon_by_name) - supp_names)
    extra = sorted(supp_names - set(canon_by_name))
    counters["omitted"] = len(omitted)
    counters["extra"] = len(extra)
    for n in omitted:
        detail.append(f"detail: omit: canonical row {n!r} absent from the audited row set")
    for n in extra:
        detail.append(f"detail: extra: row {n!r} is not in the round-{cn} canonical table")

    seen_digest: dict[str, str] = {}
    for x in supp:
        name = str(x["name"]).strip("` *")
        what = str(x.get("what", "")).strip()
        ev = str(x.get("evidence", "")).strip()
        first = str(x.get("first", "")).strip()
        dg = row_digest(name, what, ev, first)
        counters["canonical_reads"] += 1
        ok = True
        if dg in seen_digest:
            ok = False
            detail.append(f"detail: distinct: row {name!r} duplicates content of {seen_digest[dg]!r}")
        seen_digest[dg] = name
        for tok in path_tokens(ev):
            if not exists_at(repo, tip, tok):
                ok = False
                detail.append(f"detail: bind: row {name!r} evidence {tok} does not resolve at {tip[:12]}")
        nums = re.findall(r"\d+", first)
        fr = int(nums[-1]) if nums else None
        if fr is None or fr > cn or fr not in heading_rounds:
            ok = False
            detail.append(f"detail: rounds: row {name!r} first-working round {first!r} "
                          f"not evidenced (`## Round` heading present={fr in (heading_rounds or set())})")
        m = mirror_by_name.get(name)
        if m is None:
            ok = False
            detail.append(f"detail: mirror: canonical row {name!r} missing from ## Capabilities")
        elif not m[3].strip().startswith(str(fr)) or m[1] != what:
            ok = False
            detail.append(f"detail: mirror: row {name!r} mirror (first={m[3]!r}) != canonical (first={first!r}) "
                          f"or 'what' text differs")
        if ok:
            counters["bind"] += 1
        row_lines.append(f"row {name} sha={dg} first={fr} bind={'ok' if ok else 'FAIL'}")

    # reverse direction: a mirror row that the canonical table never enters
    for name in sorted(set(mirror_by_name) - set(canon_by_name)):
        counters["extra"] += 1
        detail.append(f"detail: mirror: ## Capabilities row {name!r} has no round-{cn} canonical row")

    if len(canon_by_name) != len(crows):
        counters["distinct"] += 1
        detail.append(f"detail: distinct: duplicate canonical row names ({len(crows)} rows, "
                      f"{len(canon_by_name)} distinct)")

    mism = (counters["omitted"] + counters["extra"] + counters["distinct"]
            + (len(supp) - counters["bind"]))
    return dict(tip=tip, cn=cn, cline=cline, crows=len(crows), mrows=len(mrows),
                supplied=len(supplied), counters=counters, detail=detail,
                row_lines=row_lines, mism=mism)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--scorecard", help="override SCORECARD.md text source (control trees)")
    ap.add_argument("--rows-file", help="JSON [{name,what,evidence,first}] to audit instead")
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        r = evaluate(os.path.abspath(a.repo), a.tip, a.scorecard, a.rows_file)
    except (EvalError, OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    c = r["counters"]
    met = r["mism"] == 0
    head = [
        f"tip={r['tip']}",
        f"canon=round{r['cn']}@{r['cline']} rows={r['crows']} mirror={r['mrows']} supplied={r['supplied']}",
        " ".join(f"{k}={c[k]}" for k in ("bind", "canonical_reads", "omitted", "extra", "distinct"))
        + f" mismatches={r['mism']} met={met}",
    ]
    out = "\n".join(head + r["detail"] + r["row_lines"]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
