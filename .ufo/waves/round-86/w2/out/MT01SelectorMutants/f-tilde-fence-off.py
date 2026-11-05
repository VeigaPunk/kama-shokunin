#!/usr/bin/env python3
"""round86-rendered-cells.py - round-86 C1 (calibration): grade live SCORECARD
self-assessment cells by RENDERED identity, never by raw-line shadow text.

Rendered-cell selection (the selector the round-85 counter lacked):
  * HTML comment blocks ``<!-- ... -->`` (single or multi line) are removed;
  * fenced code blocks are removed: an opener is ``{0,3}`` spaces then three or
    more backticks or tildes plus an info string; the block closes on the same
    character, at least as long, alone on the line (``{0,3}`` spaces allowed),
    and an unclosed fence runs to EOF (CommonMark 0.31.2 sections 4.4/4.5);
  * a ``round-<N> correction`` section is removed up to the next heading of the
    same or a shallower depth (the round-85 convention, unchanged);
  * a selected cell must start at column 0 - an indented line is code, a list
    continuation or a block quote, never the head banner or an axes row.

Population (three facts, no whole-record census):
  gate         the first top-level ``**Current authority (round N):**`` line
               names the NEWEST terminal gate receipt present in the tree, and
               that claim is one coupled assertion: a 40-hex revision R in the
               same paragraph, the backticked receipt path, and the exact
               ``PRE_REPORT round=... arms=... failed=... uncommitted=...``
               token. The receipt must exist at R, its bytes at R must contain
               that exact token, R must be an ancestor of the graded revision,
               and the backticked ``tools/pre-report-gate.py ... --round M``
               command must name the token's round.
  closure      the first top-level ``| calibration |`` row inside the first
               ``## Axes`` section names the newest committed
               ``corpus/lessons/round-<N>-verifier-spotcheck.md`` (highest N).
  disposition  that row names ``round<N> <disposition>`` for the newest
               closure and the word occurs in the closure body.

Output: one ``RENDERED_CELLS facts=3 mismatches=<m> gate=<0|1> closure=<0|1>
disposition=<0|1> newest_gate=<N> newest_closure=<N>`` line, then one
``RENDERED_CELLS_FINDING <fact> <detail>`` line per mismatch.

Exit: 0 all three facts hold; 1 any mismatch; 2 could-not-evaluate (no
SCORECARD.md at the revision, no committed gate receipt, no committed closure,
unreadable git) - never silently 0.

``--selftest`` builds fixture trees in $TMPDIR (no git) and runs the
shadow/contradiction arms the round-85 false green escaped.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

PREDICATE = (
    "`python3 tools/round86-rendered-cells.py --repo <lane> --rev <rev>` prints one "
    "`RENDERED_CELLS facts=3 mismatches=<m> gate=<0|1> closure=<0|1> disposition=<0|1> "
    "newest_gate=<N> newest_closure=<N>` line and exits 0 only when the rendered (fence- and "
    "comment-free, column-0) head authority cell names the newest terminal gate receipt with "
    "its revision, command and receipt bytes coupled, the rendered calibration row names the "
    "newest committed verifier spotcheck, and that row names its disposition; it exits 1 naming "
    "every mismatch as `RENDERED_CELLS_FINDING <fact> <detail>`."
)

FENCE = re.compile(r"^ {0,3}(`{3,})(.*)$")
CORRECTION = re.compile(r"^ {0,3}(#{1,6})\s+round-[0-9]+ correction(?:\s|$)")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*)$")
AUTHORITY = re.compile(r"^\*\*Current authority \(round ([0-9]+)\):")
CALIBRATION = re.compile(r"^\|\s*calibration\s*\|")
GATE_TOKEN = re.compile(
    r"`PRE_REPORT round=([0-9]+) arms=([0-9]+) failed=([0-9]+) uncommitted=([0-9]+)`")
GATE_LINE = re.compile(
    r"^PRE_REPORT round=([0-9]+) arms=([0-9]+) failed=([0-9]+) uncommitted=([0-9]+)$", re.M)
RECEIPT = re.compile(r"`([^`]*\.out)`")
COMMAND = re.compile(r"`python3 tools/pre-report-gate\.py[^`]*`")
REVISION = re.compile(r"`([0-9a-f]{40})`")
CLOSURE_PATH = re.compile(r"^corpus/lessons/round-([0-9]+)-verifier-spotcheck\.md$")
ROW_CLOSURE = re.compile(
    r"latest outside closure `corpus/lessons/(round-([0-9]+)-verifier-spotcheck\.md)`")
DISPOSITIONS = ("rejected-harmed", "rejected-honest-stop", "admitted")


class CouldNotEvaluate(Exception):
    pass


class GitTree:
    """Committed bytes at one revision."""

    def __init__(self, repo: str, rev: str):
        self.repo = repo
        self.rev = rev
        self._paths = None
        self._cache = {}

    def paths(self):
        if self._paths is None:
            out = subprocess.check_output(
                ["git", "-C", self.repo, "ls-tree", "-r", "--name-only", self.rev], text=True)
            self._paths = out.splitlines()
        return self._paths

    def blob(self, path: str):
        if path not in self._cache:
            try:
                self._cache[path] = subprocess.check_output(
                    ["git", "-C", self.repo, "show", f"{self.rev}:{path}"], text=True,
                    stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                self._cache[path] = None
        return self._cache[path]

    def ancestor(self, revision: str):
        if revision == self.rev:
            return True
        return subprocess.run(
            ["git", "-C", self.repo, "merge-base", "--is-ancestor", revision, self.rev],
            capture_output=True).returncode == 0


class DictTree:
    """Fixture tree for --selftest: files, ancestors, revision label."""

    def __init__(self, files, ancestors, rev):
        self.files = files
        self.ancestors = set(ancestors) | {rev}
        self.rev = rev

    def paths(self):
        return sorted(self.files)

    def blob(self, path):
        return self.files.get(path)

    def ancestor(self, revision):
        return revision in self.ancestors


def rendered(text: str) -> str:
    """Strip comments, fences and correction sections; return rendered text."""
    out = []
    lines = text.splitlines()
    in_comment = False
    fence = None
    depth = None
    for line in lines:
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
            else:
                continue
        if fence is not None:
            close = re.match(r"^ {0,3}(`{3,}|~{3,})\s*$", line)
            if close and close.group(1)[0] == fence[0] and len(close.group(1)) >= fence[1]:
                fence = None
            continue
        while "<!--" in line:
            before, rest = line.split("<!--", 1)
            if "-->" in rest:
                line = before + rest.split("-->", 1)[1]
            else:
                line = before
                in_comment = True
                break
        if not line.strip():
            out.append("")
            continue
        opener = FENCE.match(line)
        if opener:
            fence = (opener.group(1)[0], len(opener.group(1)))
            continue
        heading = CORRECTION.match(line)
        if heading:
            depth = len(heading.group(1))
            continue
        if depth is not None:
            other = HEADING.match(line)
            if other and len(other.group(1)) <= depth:
                depth = None
            else:
                continue
        out.append(line)
    return "\n".join(out)


def select_cells(text: str):
    """Return (authority_line, calibration_row) from rendered text, or None each."""
    body = rendered(text)
    authority = None
    row = None
    in_axes = False
    for line in body.splitlines():
        if line.startswith("## "):
            in_axes = line.strip() == "## Axes"
            continue
        if authority is None and AUTHORITY.match(line):
            authority = line
            continue
        if in_axes and row is None and CALIBRATION.match(line):
            row = line
    return authority, row


def newest_gate(tree):
    """Highest-round terminal gate receipt present in the tree."""
    best = None
    for path in tree.paths():
        if not re.match(r"^\.ufo/waves/round-[0-9]+/measured/.*\.out$", path):
            continue
        text = tree.blob(path)
        if not text:
            continue
        for match in GATE_LINE.finditer(text):
            round_no = int(match.group(1))
            if best is None or round_no > best[0]:
                best = (round_no, path, match.group(0))
    if best is None:
        raise CouldNotEvaluate("no committed PRE_REPORT receipt under .ufo/waves/*/measured/")
    return best


def newest_closure(tree):
    best = None
    for path in tree.paths():
        match = CLOSURE_PATH.match(path)
        if match:
            round_no = int(match.group(1))
            if best is None or round_no > best[0]:
                best = (round_no, path)
    if best is None:
        raise CouldNotEvaluate("no committed corpus/lessons/round-<N>-verifier-spotcheck.md")
    return best


def disposition_of(body: str) -> str:
    for word in DISPOSITIONS:
        if re.search(rf"\b{word}\b", body):
            return word
    return "unknown"


def gate_fact(tree, authority, newest):
    round_no, receipt_path, receipt_token = newest
    findings = []
    token = GATE_TOKEN.search(authority or "")
    if not token:
        findings.append(("gate", "no coupled PRE_REPORT token in the rendered authority cell"))
        return findings
    token_round = int(token.group(1))
    if token_round != round_no:
        findings.append(("gate", f"declared round={token_round} newest terminal receipt round={round_no} "
                                 f"({receipt_path})"))
    command = COMMAND.search(authority or "")
    if not command:
        findings.append(("gate", "no backticked tools/pre-report-gate.py command"))
    else:
        cmd_round = re.search(r"--round ([0-9]+)", command.group(0))
        if not cmd_round or int(cmd_round.group(1)) != token_round:
            findings.append(("gate", f"command round does not name the token round {token_round}"))
    receipts = [m.group(1) for m in RECEIPT.finditer(authority or "")]
    if not receipts:
        findings.append(("gate", "no backticked receipt path"))
        return findings
    revisions = [m.group(1) for m in REVISION.finditer(authority or "")]
    if not revisions:
        findings.append(("gate", "no 40-hex revision in the authority cell"))
        return findings
    coupled = []
    for revision in revisions:
        if not tree.ancestor(revision):
            continue
        for path in receipts:
            text = tree.blob(path) if path in tree.paths() else None
            if text is not None and token.group(0).strip("`") in text:
                coupled.append((revision, path))
    if not coupled:
        findings.append(("gate", f"no revision among {len(revisions)} is an ancestor carrying a "
                                 f"declared receipt with the exact token"))
    return findings


def closure_fact(tree, row, newest):
    match = ROW_CLOSURE.search(row or "")
    if not match:
        return [("closure", "rendered calibration row names no latest outside closure")]
    if int(match.group(2)) != newest[0]:
        return [("closure", f"row names round-{match.group(2)} newest committed closure is "
                            f"round-{newest[0]} ({newest[1]})")]
    return []


def disposition_fact(tree, row, newest):
    body = tree.blob(newest[1]) or ""
    word = disposition_of(body)
    if word == "unknown":
        return [("disposition", f"closure {newest[1]} carries no disposition word")]
    if not re.search(rf"round{newest[0]} {re.escape(word)}\b", row or ""):
        return [("disposition", f"row does not name `round{newest[0]} {word}`")]
    return []


def grade(tree):
    score = tree.blob("SCORECARD.md")
    if score is None:
        raise CouldNotEvaluate("no SCORECARD.md at the graded revision")
    authority, row = select_cells(score)
    if authority is None:
        raise CouldNotEvaluate("no rendered top-level Current authority cell")
    if row is None:
        raise CouldNotEvaluate("no rendered top-level calibration row inside ## Axes")
    gate_newest = newest_gate(tree)
    closure_newest = newest_closure(tree)
    findings = []
    findings += gate_fact(tree, authority, gate_newest)
    findings += closure_fact(tree, row, closure_newest)
    findings += disposition_fact(tree, row, closure_newest)
    facts = {"gate": not any(f[0] == "gate" for f in findings),
             "closure": not any(f[0] == "closure" for f in findings),
             "disposition": not any(f[0] == "disposition" for f in findings)}
    return {"findings": findings, "facts": facts, "mismatches": len(findings),
            "newest_gate": gate_newest[0], "newest_closure": closure_newest[0]}


def render(result):
    facts = result["facts"]
    return (f"RENDERED_CELLS facts=3 mismatches={result['mismatches']} "
            f"gate={int(facts['gate'])} closure={int(facts['closure'])} "
            f"disposition={int(facts['disposition'])} "
            f"newest_gate={result['newest_gate']} newest_closure={result['newest_closure']}")


# ---------------------------------------------------------------- selftest

A = "a" * 40
B = "b" * 40
GOOD_TOKEN = "`PRE_REPORT round=85 arms=13 failed=1 uncommitted=0`"
GOOD_CMD = "`python3 tools/pre-report-gate.py --repo . --round 85 --tip master`"
GOOD_RECEIPT = ".ufo/waves/round-85/measured/after/gate.out"
GOOD_ROW = (
    "| calibration | **7** | terminal `SELFRECORD_R85` at `" + A + "`; latest outside closure "
    "`corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-honest-stop; "
    "round84 rejected-honest-stop) | score round1 |")
STALE_ROW = (
    "| calibration | **7** | terminal `SELFRECORD_R84` at `" + A + "`; latest outside closure "
    "`corpus/lessons/round-84-verifier-spotcheck.md` (round84 rejected-honest-stop) | score round1 |")


def fixture(stale_live=True, shadow="", authority_extra="", row=None, receipt_text=None,
            drop_receipt=False, extra_files=None, cmd=GOOD_CMD, token=GOOD_TOKEN):
    live = (f"**Current authority (round 85):** assigned axes are operability + calibration; "
            f"Latest measured round: 85. Terminal gate measured at `{A}`: {cmd} printed {token}, "
            f"exit0; receipt `{GOOD_RECEIPT}`.{authority_extra}")
    stale = (f"**Current authority (round 84):** assigned axes are operability + calibration; "
             f"Latest measured round: 84. Terminal gate measured at `{A}`: "
             f"`python3 tools/pre-report-gate.py --repo . --round 84 --tip master` printed "
             f"`PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`, exit0; receipt "
             f"`.ufo/waves/round-84/measured/after/gate-final-green.out`.")
    score = "# fixture\n\n" + (stale if stale_live else live) + "\n" + shadow + "\n## Axes\n\n" + \
            (row if row is not None else (STALE_ROW if stale_live else GOOD_ROW)) + "\n"
    files = {
        "SCORECARD.md": score,
        GOOD_RECEIPT: receipt_text if receipt_text is not None else
        ("PRE_REPORT_ARM selfdesc exit=0 ok\n" + GOOD_TOKEN.strip("`") + "\n"),
        ".ufo/waves/round-84/measured/after/gate-final-green.out":
            "PRE_REPORT round=84 arms=13 failed=0 uncommitted=0\n",
        "corpus/lessons/round-85-verifier-spotcheck.md":
            "# kama round 85\n\nVerdict: rejected-honest-stop. admitted false.\n",
        "corpus/lessons/round-84-verifier-spotcheck.md":
            "# kama round 84\n\nVerdict: rejected-honest-stop.\n",
    }
    if drop_receipt:
        files.pop(GOOD_RECEIPT, None)
    if extra_files:
        files.update(extra_files)
    return DictTree(files, {A}, "c" * 40)


def selftest():
    arms = []

    def arm(name, tree, want_exit, want_facts=None, want_mismatch_min=0):
        try:
            result = grade(tree)
            line = render(result)
            got = 0 if result["mismatches"] == 0 else 1
        except CouldNotEvaluate as exc:
            result, line, got = None, f"could-not-evaluate: {exc}", 2
        ok = got == want_exit
        if want_facts is not None and result is not None:
            ok = ok and all(result["facts"][k] == v for k, v in want_facts.items())
        if result is not None:
            ok = ok and result["mismatches"] >= want_mismatch_min
        arms.append((name, ok, line))

    arm("green", fixture(stale_live=False), 0,
        {"gate": True, "closure": True, "disposition": True})
    fenced = "```markdown\n" + (
        "**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at "
        f"`{A}`: {GOOD_CMD} printed {GOOD_TOKEN}, exit0; receipt `{GOOD_RECEIPT}`.") + "\n" + \
        GOOD_ROW + "\n```\n"
    arm("fenced-shadow", fixture(stale_live=True, shadow=fenced), 1, {"gate": False}, 3)
    commented = "<!--\n" + (
        "**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at "
        f"`{A}`: {GOOD_CMD} printed {GOOD_TOKEN}, exit0; receipt `{GOOD_RECEIPT}`.") + "\n" + \
        GOOD_ROW + "\n-->\n"
    arm("comment-shadow", fixture(stale_live=True, shadow=commented), 1, {"gate": False}, 3)
    tilde = "~~~\n" + (
        "**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at "
        f"`{A}`: {GOOD_CMD} printed {GOOD_TOKEN}, exit0; receipt `{GOOD_RECEIPT}`.") + "\n" + \
        GOOD_ROW + "\n~~~\n"
    arm("tilde-fence-shadow", fixture(stale_live=True, shadow=tilde), 1, {"gate": False}, 3)
    indented = "    " + (
        "**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at "
        f"`{A}`: {GOOD_CMD} printed {GOOD_TOKEN}, exit0; receipt `{GOOD_RECEIPT}`.") + "\n    " + \
        GOOD_ROW + "\n"
    arm("indent-shadow", fixture(stale_live=True, shadow=indented), 1, {"gate": False}, 3)
    unclosed = "```\n" + (
        "**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at "
        f"`{A}`: {GOOD_CMD} printed {GOOD_TOKEN}, exit0; receipt `{GOOD_RECEIPT}`.") + "\n"
    arm("unclosed-fence-fails-closed", fixture(stale_live=True, shadow=unclosed), 2)
    arm("contradictory-receipt", fixture(stale_live=False, receipt_text="PRE_REPORT round=85 "
                                        "arms=12 failed=0 uncommitted=0\n"), 1, {"gate": False}, 1)
    arm("missing-receipt", fixture(stale_live=False, drop_receipt=True), 1, {"gate": False}, 1)
    arm("command-round-disagrees",
        fixture(stale_live=False,
                cmd="`python3 tools/pre-report-gate.py --repo . --round 84 --tip master`"),
        1, {"gate": False}, 1)
    arm("closure-only-stale", fixture(stale_live=False, row=STALE_ROW), 1,
        {"gate": True, "closure": False, "disposition": False}, 2)
    green = fixture(stale_live=False)
    green.files.pop("corpus/lessons/round-85-verifier-spotcheck.md")
    green.files.pop("corpus/lessons/round-84-verifier-spotcheck.md")
    arm("no-closure-population", green, 2)
    fail = sum(1 for _, ok, _ in arms if not ok)
    for name, ok, line in arms:
        print(f"RENDERED_CELLS_SELFTEST_{'PASS' if ok else 'FAIL'} {name} {line}")
    print(f"RENDERED_CELLS_SELFTEST pass={len(arms) - fail} fail={fail}")
    return 0 if fail == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="master")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        tree = GitTree(args.repo, args.rev)
        result = grade(tree)
    except (CouldNotEvaluate, OSError, subprocess.CalledProcessError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
        for fact, detail in result["findings"]:
            print(f"RENDERED_CELLS_FINDING {fact} {detail}")
    return 0 if result["mismatches"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
