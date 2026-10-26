#!/usr/bin/env python3
"""round44-verdict-ledger-audit.py - kama round-44 C2 (calibration) counter.

Question: at a lane revision, does the lane's self-assessment carry, for every
round 10-43 and each LEARNING.md trend (expansion, quality, discernment), the
lane's own trend verdict (its filed fleet report) beside the outside closure's
verdict (the lane's `round-N-verifier-spotcheck.md`), each read off a cited line
that a reader can re-open, and does SCORECARD.md name every disagreement and
state the agreement figures those rows imply?

Frozen names (before data):
  lane base   9d9cc93ec50783cd114829a91757b90d57c78dc6   (outside files)
  fleet rev   b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025   (self reports)
  ledger      registry/verdict-ledger.tsv
  scorecard   SCORECARD.md: a heading `### Round-44 calibration ledger`; the
              `## Axes` calibration row names `registry/verdict-ledger.tsv`
Ledger: TSV, header `round trend side verdict repo rev path line note`, one row
per (round 10..43, trend, side self|outside) = 204 rows.
  self     repo `fleet`, rev = fleet rev, path `.ufo/reports/round-<N>/kama.md`
  outside  repo `lane`, rev = lane base, path
           `corpus/lessons/round-<N>-verifier-spotcheck.md`
  verdict  improved | harmed | unchanged | unprovable-but-better | unprovable |
           mixed | absent
  line     1-based line of that file at that rev, or `-` for absent
Evidence rule. A line is read as tokens: trend words (expansion, quality,
discernment) and verdict words (`unprovable-but-better` / `unprovable but
better`, `unprovable`, `improved`, `harmed`, `unchanged`), case-insensitive;
each verdict word belongs to the nearest trend word before it on the line.
  single verdict  the cited line gives the row's trend that verdict word
  mixed           the cited line gives the row's trend >= 2 distinct words
  absent          (outside) the file does not exist at the rev, or (either
                  side) no line of the file gives the row's trend any verdict
                  word; note >= 20 chars
A row is VALID when its repo/rev/path are the side's, its verdict obeys the
rule, and it is the only row for its key.
Comparison: order harmed < unchanged < unprovable < unprovable-but-better <
improved. For keys where both sides are valid and neither is absent: agree
(equal), overclaim (self > outside), underclaim (self < outside), other (either
side mixed). Mismatch set = overclaim + underclaim + other keys.
Scorecard legs: the section under the heading has one table row
`| <round> | <trend> | <self> | <outside> | ...` per mismatch key and none for
any other key (set equality on round, trend, self, outside); a line in it reads
`agreement=<a>/<n> overclaim=<o> underclaim=<u> other=<x> absent=<k>` with the
values the valid ledger implies (n = a + o + u; k = keys with an absent side);
the calibration row of `## Axes` names the ledger path.
met = 204 valid rows and table exact and summary exact and axes cite.
PREDICATE (same sentence in the preregistration): every round-10..43 trend
verdict, self and outside, is ledgered on a cited line that carries it, and
SCORECARD names every disagreement with the agreement figures; missing=0.

Output: `rows=R valid=V missing=M bad=B agree=a overclaim=o underclaim=u
other=x absent=k table_missing=T table_extra=E summary=S axes=X met=True|False`
then `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo and --fleet.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"
FLEET_REV = "b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025"
LEDGER = "registry/verdict-ledger.tsv"
HEADING = "### Round-44 calibration ledger"
HEADER = ["round", "trend", "side", "verdict", "repo", "rev", "path", "line", "note"]
ROUNDS = range(10, 44)
TRENDS = ("expansion", "quality", "discernment")
ORDER = {"harmed": 0, "unchanged": 1, "unprovable": 2, "unprovable-but-better": 3, "improved": 4}
TOK = re.compile(r"(expansion|quality|discernment)|(unprovable[- ]but[- ]better)|(unprovable)|(improved|harmed|unchanged)",
                 re.I)


class EvalError(Exception):
    pass


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise EvalError(f"git -C {repo} {' '.join(args)}: {p.stderr.strip()[:200]}")
    return p


def show(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return p.stdout if p.returncode == 0 else None


def read_line(line):
    """trend -> set of verdict words on this line (nearest preceding trend)."""
    out, cur = {}, None
    for m in TOK.finditer(line):
        if m.group(1):
            cur = m.group(1).lower()
            continue
        if cur is None:
            continue
        if m.group(2):
            v = "unprovable-but-better"
        elif m.group(3):
            v = "unprovable"
        else:
            v = m.group(4).lower()
        out.setdefault(cur, set()).add(v)
    return out


def side_spec(rnd, side):
    if side == "self":
        return "fleet", FLEET_REV, f".ufo/reports/round-{rnd}/kama.md"
    return "lane", BASE, f"corpus/lessons/round-{rnd}-verifier-spotcheck.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--fleet", required=True, help="fleet repo holding the frozen fleet rev")
    ap.add_argument("--out")
    a = ap.parse_args()
    detail = []
    try:
        tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.strip()
        git(a.fleet, "cat-file", "-e", FLEET_REV + "^{commit}")
        git(a.repo, "cat-file", "-e", BASE + "^{commit}")
        cache = {}

        def fetch(repo, rev, path):
            k = (repo, rev, path)
            if k not in cache:
                t = show(a.fleet if repo == "fleet" else a.repo, rev, path)
                cache[k] = None if t is None else t.splitlines()
            return cache[k]

        led = show(a.repo, tip, LEDGER)
        rows, seen = {}, {}
        if led is not None:
            ls = [x for x in led.splitlines() if x.strip()]
            if ls and ls[0].split("\t") == HEADER:
                for x in ls[1:]:
                    f = x.split("\t")
                    if len(f) != len(HEADER):
                        detail.append(f"bad ledger line: {x[:60]}")
                        continue
                    d = dict(zip(HEADER, f))
                    k = (d["round"], d["trend"], d["side"])
                    seen[k] = seen.get(k, 0) + 1
                    rows[k] = d
            else:
                detail.append("ledger header mismatch")
        valid, bad, missing = {}, 0, 0
        for rnd in ROUNDS:
            for tr in TRENDS:
                for side in ("self", "outside"):
                    k = (str(rnd), tr, side)
                    d = rows.get(k)
                    if d is None:
                        missing += 1
                        detail.append(f"{k} missing")
                        continue
                    repo, rev, path = side_spec(rnd, side)
                    why = None
                    if seen[k] > 1:
                        why = "duplicate key"
                    elif (d["repo"], d["rev"], d["path"]) != (repo, rev, path):
                        why = "repo/rev/path differ from the side's file"
                    else:
                        text = fetch(repo, rev, path)
                        v = d["verdict"]
                        if v == "absent":
                            if len(d["note"]) < 20 or d["line"] != "-":
                                why = "absent needs line - and note >= 20"
                            elif text is not None and any(tr in read_line(x) for x in text):
                                why = "absent but a line gives this trend a verdict"
                        elif text is None:
                            why = "file missing at rev"
                        elif not d["line"].isdigit() or not 1 <= int(d["line"]) <= len(text):
                            why = "line out of range"
                        else:
                            got = read_line(text[int(d["line"]) - 1]).get(tr, set())
                            if v == "mixed":
                                ok = len(got) >= 2
                            elif v in ORDER:
                                ok = v in got
                            else:
                                ok = False
                            if not ok:
                                why = f"cited line gives {tr} {sorted(got)}, not {v}"
                    if why:
                        bad += 1
                        detail.append(f"{k} invalid: {why}")
                    else:
                        valid[k] = d["verdict"]
        agree = over = under = other = absent = 0
        mism = set()
        for rnd in ROUNDS:
            for tr in TRENDS:
                s, o = valid.get((str(rnd), tr, "self")), valid.get((str(rnd), tr, "outside"))
                if s is None or o is None:
                    continue
                if "absent" in (s, o):
                    absent += 1
                    continue
                if "mixed" in (s, o):
                    other += 1
                    mism.add((str(rnd), tr, s, o))
                elif s == o:
                    agree += 1
                elif ORDER[s] > ORDER[o]:
                    over += 1
                    mism.add((str(rnd), tr, s, o))
                else:
                    under += 1
                    mism.add((str(rnd), tr, s, o))
        sc = (show(a.repo, tip, "SCORECARD.md") or "").splitlines()
        sec, insec = [], False
        for x in sc:
            if x.startswith("#"):
                insec = x.strip() == HEADING
                continue
            if insec:
                sec.append(x)
        trow = set()
        for x in sec:
            c = [y.strip() for y in x.strip().strip("|").split("|")] if x.lstrip().startswith("|") else []
            if len(c) >= 4 and c[0].isdigit() and c[1] in TRENDS:
                trow.add((c[0], c[1], c[2], c[3]))
        tmiss, textra = len(mism - trow), len(trow - mism)
        for m in sorted(mism - trow):
            detail.append(f"table missing {m}")
        for m in sorted(trow - mism):
            detail.append(f"table extra {m}")
        n = agree + over + under
        want = f"agreement={agree}/{n} overclaim={over} underclaim={under} other={other} absent={absent}"
        summary = int(any(want in x for x in sec))
        if not summary:
            detail.append(f"summary line wanted: {want}")
        axes, inax = 0, False
        for x in sc:
            if x.startswith("## "):
                inax = x.strip() == "## Axes"
                continue
            if inax and x.lstrip().startswith("|") and "calibration" in x.split("|")[1].lower() and LEDGER in x:
                axes = 1
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    total = len(ROUNDS) * len(TRENDS) * 2
    met = len(valid) == total and tmiss == 0 and textra == 0 and summary == 1 and axes == 1
    line = (f"rows={len(rows)} valid={len(valid)} missing={missing} bad={bad} agree={agree} overclaim={over} "
            f"underclaim={under} other={other} absent={absent} table_missing={tmiss} table_extra={textra} "
            f"summary={summary} axes={axes} met={met}")
    text = "\n".join([f"tip={tip}", line] + [f"detail: {d}" for d in detail]) + "\n"
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    sys.stdout.write(text)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
