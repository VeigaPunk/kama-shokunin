#!/usr/bin/env python3
"""round45-claim-outcome-audit.py - kama round-45 C2 (calibration) counter.

Question: at a lane revision, does the lane's self-assessment carry, for every
claim the lane declared in rounds 10-44 (63 frozen keys below), the outcome the
lane filed for it (its fleet report) beside the outcome the outside closure gave
it (the lane's `round-N-verifier-spotcheck.md`; for rounds 20-23, which have no
spot-check file, the closure entry in the fleet `MANIFEST.json`), each read off
a cited line a reader can re-open, and does SCORECARD.md name every
disagreement and state the agreement figures those rows imply?

Frozen names (before data):
  lane base   6b8ccfb310de339e9452514aea3a9402a970c3e6   (spot-check files)
  fleet rev   6105c5870859f15ba5372ccbe3835d65b0d9d38b   (reports, MANIFEST.json)
  ledger      registry/claim-outcome-ledger.tsv
  scorecard   a heading `### Round-45 claim-outcome ledger`; the `## Axes`
              calibration row names `registry/claim-outcome-ledger.tsv`
Ledger: TSV, header `round claim side outcome repo rev path line note`, one row
per (round, claim, side self|outside) = 126 rows.
  self     repo `fleet`, rev = fleet rev, path `.ufo/reports/round-<N>/kama.md`
  outside  rounds 20-23: repo `fleet`, rev = fleet rev, path `MANIFEST.json`;
           otherwise repo `lane`, rev = lane base, path
           `corpus/lessons/round-<N>-verifier-spotcheck.md`
  outcome  met | partial | unprovable-but-better | unprovable | not-met |
           mixed | absent
  line     1-based line of that file at that rev, or `-` for absent
Evidence rule. A line is read as tokens: claim ids `C1`..`C4` and outcome
phrases (case-insensitive, earliest-longest first):
  not-met                 met=False, not met, not achieved, not verified,
                          does not verify, did not verify, unverified, honest
                          stop, honest-stop, withdrawn, missed, not-met, rejected
  partial                 partially verified/verifies/met, partial, partly
  unprovable-but-better   unprovable but better (hyphens or spaces)
  unprovable              unprovable
  met                     met=True, verifies, verified, achieved, met
Each outcome phrase belongs to the nearest claim id before it in the file
(reading forward across lines: a section that opens with `C2` keeps attributing
to C2 until another claim id appears); before any claim id, phrases belong to
the round's claim when the round has exactly one frozen claim.
  single outcome  the cited line gives the row's claim that outcome
  mixed           the cited line gives the row's claim >= 2 distinct outcomes
  absent          no line of the side's file gives the row's claim any outcome
                  (or the file does not exist at the rev); line `-`, note >= 20
A row is VALID when its repo/rev/path are the side's, its outcome obeys the
rule, and it is the only row for its key.
Comparison: order not-met < unprovable < partial < unprovable-but-better < met
(an assertion-strength order, not a merit scale). For keys where both sides
are valid and neither is absent: agree (equal), overclaim (self > outside),
underclaim (self < outside), other (either side mixed). Mismatch set =
overclaim + underclaim + other keys.
Cross-witness (the fleet `MANIFEST.json` at the fleet rev; the last kama
closure entry per lane round decides): a round whose closure verdict is
`admitted` may carry no valid outside outcome `not-met` or `unprovable`; a
round whose verdict is `rejected-honest-stop` must carry at least one valid
outside outcome in {not-met, unprovable, partial, mixed}; other verdicts add no
constraint. consistency_bad counts violating rounds.
Scorecard legs: the section under the heading has one table row
`| <round> | <claim> | <self> | <outside> | ...` per mismatch key and none for
any other key; a line in it reads `agreement=<a>/<n> overclaim=<o>
underclaim=<u> other=<x> absent=<k>` with the values the valid ledger implies
(n = a + o + u; k = keys with an absent side); the calibration row of `## Axes`
names the ledger path.
met = 126 valid rows and consistency_bad = 0 and table exact and summary exact
and axes cite.
PREDICATE (same sentence in the preregistration): every claim the lane declared
in rounds 10-44 has its self-filed and its outside outcome ledgered on a cited
line that carries it, consistent with the closure's MANIFEST verdict, and
SCORECARD names every disagreement with the agreement figures; missing=0.

Output: `rows=R valid=V missing=M bad=B agree=a overclaim=o underclaim=u
other=x absent=k consistency_bad=C table_missing=T table_extra=E summary=S
axes=X met=True|False` then `detail:` lines. Exit 0 met, 1 not met, 2 could
not evaluate.
Read-only on --repo and --fleet.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

BASE = "6b8ccfb310de339e9452514aea3a9402a970c3e6"
FLEET_REV = "6105c5870859f15ba5372ccbe3835d65b0d9d38b"
LEDGER = "registry/claim-outcome-ledger.tsv"
HEADING = "### Round-45 claim-outcome ledger"
HEADER = ["round", "claim", "side", "outcome", "repo", "rev", "path", "line", "note"]
POP = {10: [1, 3], 11: [1, 2], 12: [1], 13: [1], 14: [1], 15: [1], 16: [1, 2], 17: [1, 2], 18: [1, 2],
       19: [1, 2], 20: [1, 2], 21: [1, 2], 22: [1], 23: [1], 24: [1], 25: [1, 2], 26: [1], 27: [1], 28: [1],
       29: [1], 30: [1, 2], 31: [1, 2, 3], 32: [1, 2], 33: [1, 2], 34: [1, 2], 35: [1, 2], 36: [1, 2],
       37: [1, 2], 38: [1, 2, 3], 39: [1, 2], 40: [1, 2], 41: [1, 2], 42: [1, 2, 3], 43: [1, 2, 3], 44: [1, 2]}
MANIFEST_ROUNDS = (20, 21, 22, 23)
KEYS = [(str(r), f"C{c}") for r in sorted(POP) for c in POP[r]]
ORDER = {"not-met": 0, "unprovable": 1, "partial": 2, "unprovable-but-better": 3, "met": 4}
TOK = re.compile(
    r"\b(C[1-4])\b"
    r"|(met=false|\bnot met\b|\bnot achieved\b|\bnot verified\b|\bdoes not verify\b|\bdid not verify\b"
    r"|\bunverified\b|\bhonest[- ]stop\b|\bwithdrawn\b|\bmissed\b|\bnot-met\b|\brejected\b)"
    r"|(\bpartially (?:verified|verifies|met)\b|\bpartial\b|\bpartly\b)"
    r"|(\bunprovable[- ]but[- ]better\b)"
    r"|(\bunprovable\b)"
    r"|(met=true|\bverifies\b|\bverified\b|\bachieved\b|\bmet\b)",
    re.I)
NAMES = {2: "not-met", 3: "partial", 4: "unprovable-but-better", 5: "unprovable", 6: "met"}


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


def read_file(lines, rnd):
    """per line: claim -> set of outcomes, attributing each outcome phrase to the
    nearest claim id before it in the file (or the sole frozen claim)."""
    sole = f"C{POP[rnd][0]}" if len(POP.get(rnd, [])) == 1 else None
    cur, res = None, []
    for line in lines:
        out = {}
        for m in TOK.finditer(line):
            if m.group(1):
                cur = m.group(1).upper()
                continue
            c = cur or sole
            if c is None:
                continue
            out.setdefault(c, set()).add(next(NAMES[i] for i in range(2, 7) if m.group(i)))
        res.append(out)
    return res


def closure_verdicts(fleet):
    t = show(fleet, FLEET_REV, "MANIFEST.json")
    if t is None:
        raise EvalError("MANIFEST.json missing at fleet rev")
    last = {}
    for r in json.loads(t).get("rounds", []):
        if r.get("lane") == "kama" and r.get("type") == "closure":
            try:
                last[int(r.get("lane_round"))] = r.get("verdict")
            except (TypeError, ValueError):
                continue
    return last


def side_spec(rnd, side):
    if side == "self":
        return "fleet", FLEET_REV, f".ufo/reports/round-{rnd}/kama.md"
    if rnd in MANIFEST_ROUNDS:
        return "fleet", FLEET_REV, "MANIFEST.json"
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

        def fetch(repo, rev, path, rnd):
            k = (repo, rev, path, rnd)
            if k not in cache:
                t = show(a.fleet if repo == "fleet" else a.repo, rev, path)
                cache[k] = None if t is None else (t.splitlines(), read_file(t.splitlines(), rnd))
            return cache[k]

        verdicts = closure_verdicts(a.fleet)

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
                    k = (d["round"], d["claim"], d["side"])
                    seen[k] = seen.get(k, 0) + 1
                    rows[k] = d
            else:
                detail.append("ledger header mismatch")
        valid, bad, missing = {}, 0, 0
        for rnd_s, cl in KEYS:
            rnd = int(rnd_s)
            for side in ("self", "outside"):
                k = (rnd_s, cl, side)
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
                    got_file = fetch(repo, rev, path, rnd)
                    text, attr = got_file if got_file else (None, None)
                    v = d["outcome"]
                    if v == "absent":
                        if len(d["note"]) < 20 or d["line"] != "-":
                            why = "absent needs line - and note >= 20"
                        elif attr is not None and any(cl in x for x in attr):
                            why = "absent but a line gives this claim an outcome"
                    elif text is None:
                        why = "file missing at rev"
                    elif not d["line"].isdigit() or not 1 <= int(d["line"]) <= len(text):
                        why = "line out of range"
                    else:
                        got = attr[int(d["line"]) - 1].get(cl, set())
                        if v == "mixed":
                            ok = len(got) >= 2
                        elif v in ORDER:
                            ok = v in got
                        else:
                            ok = False
                        if not ok:
                            why = f"cited line gives {cl} {sorted(got)}, not {v}"
                if why:
                    bad += 1
                    detail.append(f"{k} invalid: {why}")
                else:
                    valid[k] = d["outcome"]
        agree = over = under = other = absent = 0
        mism = set()
        for rnd_s, cl in KEYS:
            s, o = valid.get((rnd_s, cl, "self")), valid.get((rnd_s, cl, "outside"))
            if s is None or o is None:
                continue
            if "absent" in (s, o):
                absent += 1
                continue
            if "mixed" in (s, o):
                other += 1
                mism.add((rnd_s, cl, s, o))
            elif s == o:
                agree += 1
            elif ORDER[s] > ORDER[o]:
                over += 1
                mism.add((rnd_s, cl, s, o))
            else:
                under += 1
                mism.add((rnd_s, cl, s, o))
        consistency_bad = 0
        for rnd in sorted(POP):
            outs = [valid.get((str(rnd), f"C{c}", "outside")) for c in POP[rnd]]
            ver = verdicts.get(rnd)
            if ver == "admitted" and any(o in ("not-met", "unprovable") for o in outs):
                consistency_bad += 1
                detail.append(f"round {rnd} admitted but an outside outcome is {outs}")
            elif ver == "rejected-honest-stop" and not any(o in ("not-met", "unprovable", "partial", "mixed")
                                                           for o in outs):
                consistency_bad += 1
                detail.append(f"round {rnd} rejected-honest-stop but outside outcomes are {outs}")
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
            if len(c) >= 4 and c[0].isdigit() and re.fullmatch(r"C[1-4]", c[1]):
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
    total = len(KEYS) * 2
    met = (len(valid) == total and consistency_bad == 0 and tmiss == 0 and textra == 0 and summary == 1
           and axes == 1)
    line = (f"rows={len(rows)} valid={len(valid)} missing={missing} bad={bad} agree={agree} overclaim={over} "
            f"underclaim={under} other={other} absent={absent} consistency_bad={consistency_bad} "
            f"table_missing={tmiss} table_extra={textra} summary={summary} axes={axes} met={met}")
    text = "\n".join([f"tip={tip}", f"keys={len(KEYS)}", line] + [f"detail: {d}" for d in detail]) + "\n"
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    sys.stdout.write(text)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
