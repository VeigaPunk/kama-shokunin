#!/usr/bin/env python3
"""round100-record-audit.py - round-100 C1 (calibration) frozen counter.

PREDICATE (same sentence as plans/round-100-claims.md section C1):

    `python3 tools/round100-record-audit.py --repo . --rev <M1>` prints
    `RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=<resolved>` and exits 0 at M1: the lane's
    round-100 correction of its round-99 records agrees with the committed round-99 wave evidence
    on nine enumerated checks, and every line pointer inside the correction is bound to a revision
    and re-resolves there.

    Before (do-nothing control): `--rev 6776c667` prints `mismatches=9 met=False`, exit 1 (no
    correction exists; the round-99 records keep "58% attack" and the unbound `SCORECARD.md:6431`).

The two correction blocks are the text after the one line that starts with `## Round 100
correction - round-99 records` (an em dash, see HEADING; zero or two such lines = no block) up to the
next line starting with `## ` (or end of file), in `SCORECARD.md` and in `LOG.md`, read with
`git show <rev>:<file>`.

Derived facts (read from committed bytes at <rev>, never from the correction):
  D1 seats/results/dead from `.ufo/waves/round-99/w1-results.json` (dead = a result whose `output`
     is empty, or whose `status`, when present, is failed/error/aborted/cancelled/dead/timeout; the
     round-99 file carries no `status` field).
  D2 roles from `.ufo/waves/round-99/w1-spec.json` items: POLICY attack = reviewer, critic,
     mutation-tester, labrat (the wave policy's >=25 % attack share); LEDGER attack = the
     prefile-falsification gate's ATTACK_ROLES (adds security-reviewer, sentinel, connector,
     revenger). Fractions render as `<n> of <total> (<round(100*n/total)>%)`.
  D3 the round-99 measured predicate line of each claim: the first line of
     `.ufo/waves/round-99/measured/c<k>.out` starting with `CONTROL_POP99 `, `RECORD_AUDIT99 ` or
     `AUTOLOAD_STATES99 ` (k = 1, 2, 3), and that file's `exit=<n>` line.

Checks (each one mismatch when false):
  1 the SCORECARD block exists.
  2 the LOG block exists.
  3 the SCORECARD block contains the LEDGER fraction (D2) and the POLICY fraction (D2).
  4 the LOG block contains the LEDGER fraction and the POLICY fraction.
  5 neither block, with its quoted pointer phrases removed, contains a percentage other than the
     two derived ones (a forged "58%" or "42%" outside a quotation fails).
  6 both blocks state `<seats> seats, <dead> dead` with D1's values.
  7 every line-pointer token in both blocks (`SCORECARD.md`, `LOG.md` or a `corpus/lessons/` path
     followed by `:<digits>`) is revision-bound, written `` `<path>@<hex7-40>:<line>` ("<phrase>") ``;
     unbound tokens = 0 and bound tokens >= 3.
  8 every bound token resolves: <hex> is a commit, the file exists there, and line <line> of
     `git show <hex>:<path>` contains <phrase> (non-empty).
  9 `.ufo/waves/round-100/r99-measured.json` maps exactly C1, C2, C3 to D3's predicate lines, byte
     equal, and each receipt's exit line is `exit=0`.

Exit: 0 predicate met | 1 not met | 2 could-not-evaluate | 64 usage.
"""

import argparse
import json
import re
import subprocess
import sys

HEADING = "## Round 100 correction \u2014 round-99 records"
POLICY_ATTACK = frozenset({"reviewer", "critic", "mutation-tester", "labrat"})
LEDGER_ATTACK = frozenset({"reviewer", "security-reviewer", "critic", "mutation-tester",
                           "sentinel", "connector", "revenger", "labrat"})
DEAD_STATUS = frozenset({"failed", "error", "aborted", "cancelled", "dead", "timeout"})
PRED_PREFIX = {"C1": "CONTROL_POP99 ", "C2": "RECORD_AUDIT99 ", "C3": "AUTOLOAD_STATES99 "}
BOUND_RE = re.compile(r"`((?:SCORECARD\.md|LOG\.md|corpus/lessons/[\w.-]+\.md)"
                      r")@([0-9a-f]{7,40}):(\d+)`\s*\(\"([^\"]*)\"\)")
ANY_PTR_RE = re.compile(r"(?:SCORECARD\.md|LOG\.md|corpus/lessons/[\w.-]+\.md)(@[0-9a-f]{7,40})?:\d+")
PCT_RE = re.compile(r"\d+(?:\.\d+)?\s?%")


class Fail(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()

    def git(*args, ok_fail=False):
        p = subprocess.run(["git", "-C", a.repo, *args], capture_output=True)
        if p.returncode != 0:
            if ok_fail:
                return None
            raise Fail(f"git {' '.join(args)} rc={p.returncode}")
        return p.stdout.decode("utf-8", "replace")

    try:
        rev = git("rev-parse", "--verify", a.rev + "^{commit}").strip()
        results = json.loads(git("show", f"{rev}:.ufo/waves/round-99/w1-results.json"))
        spec = json.loads(git("show", f"{rev}:.ufo/waves/round-99/w1-spec.json"))
        rows = results.get("results") or []
        seats = len(rows)
        dead = sum(1 for r in rows if str(r.get("status") or "").lower() in DEAD_STATUS
                   or not str(r.get("output") or "").strip())
        roles = [i.get("role") for i in spec.get("items") or []]
        total = len(roles)
        if total == 0 or seats == 0:
            raise Fail("empty round-99 spec or results")
        pol = sum(1 for r in roles if r in POLICY_ATTACK)
        led = sum(1 for r in roles if r in LEDGER_ATTACK)
        frac = lambda n: f"{n} of {total} ({round(100 * n / total)}%)"  # noqa: E731
        pol_s, led_s = frac(pol), frac(led)
        preds = {}
        for k, (cid, prefix) in enumerate(PRED_PREFIX.items(), start=1):
            text = git("show", f"{rev}:.ufo/waves/round-99/measured/c{k}.out")
            line = next((ln for ln in text.splitlines() if ln.startswith(prefix)), None)
            ex = [ln for ln in text.splitlines() if ln.startswith("exit=")]
            preds[cid] = (line, ex[-1] if ex else None)
    except (Fail, json.JSONDecodeError) as e:
        print(f"RECORD_AUDIT100 could-not-evaluate: {e}")
        return 2

    def block(path):
        text = git("show", f"{rev}:{path}", ok_fail=True)
        if text is None:
            return None
        lines = text.splitlines()
        heads = [k for k, ln in enumerate(lines) if ln.startswith(HEADING)]
        if len(heads) != 1:
            return None
        i = heads[0]
        out = []
        for ln in lines[i + 1:]:
            if ln.startswith("## "):
                break
            out.append(ln)
        return "\n".join(out)

    sc, lg = block("SCORECARD.md"), block("LOG.md")
    blocks = [b for b in (sc, lg) if b is not None]
    checks = {}
    checks[1] = sc is not None
    checks[2] = lg is not None
    checks[3] = sc is not None and led_s in sc and pol_s in sc
    checks[4] = lg is not None and led_s in lg and pol_s in lg
    allowed = {f"{round(100 * pol / total)}%", f"{round(100 * led / total)}%"}
    pct_ok = bool(blocks) and len(blocks) == 2
    for b in blocks:
        stripped = BOUND_RE.sub("", b)
        for m in PCT_RE.findall(stripped):
            if m.replace(" ", "") not in allowed:
                pct_ok = False
                print(f"RECORD_AUDIT100_DETAIL check5 stray-percentage {m!r}")
    checks[5] = pct_ok
    seat_s = f"{seats} seats, {dead} dead"
    checks[6] = len(blocks) == 2 and all(seat_s in b for b in blocks)
    bound, unbound = [], 0
    for b in blocks:
        bound.extend(BOUND_RE.findall(b))
        stripped = BOUND_RE.sub("", b)
        for m in ANY_PTR_RE.finditer(stripped):
            unbound += 1
            print(f"RECORD_AUDIT100_DETAIL check7 unbound-or-unquoted {m.group(0)!r}")
    checks[7] = len(blocks) == 2 and unbound == 0 and len(bound) >= 3
    resolved = 0
    for path, h, line, phrase in bound:
        text = git("show", f"{h}:{path}", ok_fail=True)
        ok = False
        if text is not None:
            lines = text.splitlines()
            n = int(line)
            ok = 1 <= n <= len(lines) and phrase.strip() != "" and phrase in lines[n - 1]
        if ok:
            resolved += 1
        else:
            print(f"RECORD_AUDIT100_DETAIL check8 unresolved {path}@{h}:{line} {phrase!r}")
    checks[8] = len(bound) >= 3 and resolved == len(bound)
    mj = git("show", f"{rev}:.ufo/waves/round-100/r99-measured.json", ok_fail=True)
    m_ok = False
    if mj is not None:
        try:
            doc = json.loads(mj)
            m_ok = (isinstance(doc, dict) and set(doc) == set(PRED_PREFIX)
                    and all(preds[c][0] is not None and doc[c] == preds[c][0]
                            and preds[c][1] == "exit=0" for c in PRED_PREFIX))
        except json.JSONDecodeError:
            m_ok = False
    checks[9] = m_ok

    mismatches = 0
    for k in sorted(checks):
        if not checks[k]:
            mismatches += 1
            print(f"RECORD_AUDIT100_MISMATCH check{k}")
    met = mismatches == 0
    print(f"RECORD_AUDIT100_DERIVED seats={seats} dead={dead} roles={total} "
          f"policy_attack={pol_s!r} ledger_attack={led_s!r} bound={len(bound)} "
          f"resolved={resolved} unbound={unbound}")
    print(f"RECORD_AUDIT100 checks={len(checks)} mismatches={mismatches} met={met} rev={rev}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
