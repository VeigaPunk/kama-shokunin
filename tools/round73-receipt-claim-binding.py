#!/usr/bin/env python3
"""round73-receipt-claim-binding.py — grade every tip claim against the receipt it cites.

Round 72's critic recorded survivor B6 (`.ufo/waves/round-72/w1/CRT01ReceiptAttack/attack.md`
§4.2 and §S3): a receipt graded at an earlier revision passes the frozen
``tools/round72-receipt-tip-binding.py`` gate, because the delta between the receipt's own
header and the report tip is record-only, while the citing line says the measurement ran
"at the report tip". The base tool grades the receipt *population* (does every cited receipt
exist, carry a header, name an ancestor, and sit behind a record-only delta?); it never reads
what the citing line claims about it. The r71 defect 4 the base tool was built from is
therefore certified by the base tool itself whenever the certified receipt is old and the
delta to the tip is the round's own record.

This module composes that byte-frozen gate unchanged and adds the claim pass. It runs

    python3 tools/round72-receipt-tip-binding.py --repo <repo> --round <N> --tip <rev> --json

keeps its counts (``cited/bound/unbound/shifted/stale``) and its findings verbatim, then reads
the same two record blobs at the resolved tip (``SCORECARD.md``'s ``## Round <N>`` section and
``corpus/lessons/round-<N>.md``, the base tool's own heading semantics) and grades every line
that carries a tip-claim token (``at the tip``, ``at the report tip``, ``report tip``; case
insensitive) *and* at least one receipt citation: each cited receipt's own ``tip=``/``rev=``
header (first five lines, 40-hex) must equal the resolved tip commit.

    RECEIPT_TIP_FINDING ...                                  (the base tool's lines, verbatim)
    RECEIPT_CLAIM_FINDING stale-claim <path> :: <line>: <text>
    RECEIPT_CLAIM_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t> claims=<k> unbound_claims=<j>

``claims`` counts the self-record lines that both cite a receipt and carry a tip claim;
``unbound_claims`` counts those lines where at least one cited receipt's header is not the tip
(a missing header is a finding too: a receipt with no header cannot be shown to be the tip).
A line phrased "measured at rev X" is not a tip claim and is not graded here -- the base tool
already grades the revision it names.

Citation notation is the base tool's, reused by importing the module (``_resolve_citation``):
backticked tokens, section-relative paths against ``.ufo/waves/round-<N>/``, brace expansion,
globs, directories, repo-root paths out of scope, ``.out/.txt/.log/.json`` receipt extensions.

Exit map (pinned):
  0  the base verdict is green (exit 0) and unbound_claims == 0
  1  findings: any base finding, or any claimed receipt whose header is not the tip
  2  could-not-evaluate: CLI misuse, the base tool absent or exiting 2, an unreadable
     self-record, or a self-record that cites no receipt at all (S052: a check that collected
     nothing cannot pass)

Read-only: every git call is the base tool's own read-only set (``rev-parse``, ``cat-file``,
``ls-tree``, ``merge-base``, ``rev-list``, ``diff-tree``). ``--selftest`` builds throwaway
fixture repositories (own ``git init``, own throwaway identity, every call names
``-C <fixture>``, the toplevel is asserted before every commit) and drives the same entry point
the CLI uses; it reads and writes no lane path.

Usage:
    round73-receipt-claim-binding.py --repo . --round 73 --tip master
    round73-receipt-claim-binding.py --selftest [--work DIR]
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

PREDICATE = "`python3 tools/round73-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>` prints one `RECEIPT_CLAIM_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t> claims=<k> unbound_claims=<j>` line and exits 0 only when the base `RECEIPT_TIP_BINDING` verdict for `<rev>` is green and every self-record line that cites a receipt and answers it with a tip claim (`at the tip`, `at the report tip`, `report tip`) names a receipt whose own `tip=`/`rev=` header equals `<rev>`; it exits 1 naming each base finding and each `RECEIPT_CLAIM_FINDING stale-claim <path> :: <line>`, and 2 when the base tool or the self-record cannot be evaluated."

BASE_TOOL_NAME = "round72-receipt-tip-binding.py"
TIP_CLAIM_TOKENS = ("at the report tip", "at the tip", "report tip")
PLAN_NAME = "plans/round-73-claims.md"
PLAN_C2_HEADING = "## C2"
TIMEOUT = 300
COUNT_KEYS = ("cited", "bound", "unbound", "shifted", "stale")

_HERE = os.path.dirname(os.path.abspath(__file__))


class CouldNotEvaluate(Exception):
    """Fail-closed condition; maps to exit 2."""


# ------------------------------------------------------- base tool discovery


def _base_tool_path(repo, explicit):
    """The frozen base tool: an explicit path, the sibling, then <repo>/tools/."""
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    for candidate in (
        os.path.join(_HERE, BASE_TOOL_NAME),
        os.path.join(os.path.abspath(repo), "tools", BASE_TOOL_NAME),
    ):
        if os.path.isfile(candidate):
            return candidate
    return None


def _load_base(path):
    """Import the frozen base module so its citation/header rules are reused, not copied."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("round73_base_receipt_tip_binding", path)
    if spec is None or spec.loader is None:
        raise CouldNotEvaluate("base tool is not importable: {}".format(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_base(base_path, repo, round_no, tip):
    """Shell out to the base gate with --json; return its parsed verdict document."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            base_path,
            "--repo", repo,
            "--round", str(round_no),
            "--tip", tip,
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=TIMEOUT,
        env=env,
    )
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace").strip()
    if proc.returncode == 2:
        raise CouldNotEvaluate("base tool could not evaluate: {}".format(err or "exit 2"))
    if proc.returncode not in (0, 1):
        raise CouldNotEvaluate(
            "base tool failed (rc={}): {}".format(proc.returncode, err or out[:400])
        )
    try:
        doc = json.loads(out)
    except ValueError:
        raise CouldNotEvaluate(
            "base tool printed no JSON verdict: {}".format((out or err)[:400])
        )
    missing = [key for key in COUNT_KEYS + ("findings", "exit") if key not in doc]
    if missing:
        raise CouldNotEvaluate(
            "base tool JSON lacks {}: {}".format(",".join(missing), out[:400])
        )
    if int(doc["exit"]) != proc.returncode:
        raise CouldNotEvaluate(
            "base tool exit {} disagrees with its JSON exit {}".format(
                proc.returncode, doc["exit"]
            )
        )
    return doc


# ------------------------------------------------------------- claim pass


def _read_records(repo, tip_sha, round_no, base):
    """[(filename, lines, offset)] for the two record blobs, read at tip_sha."""
    scorecard_path = "SCORECARD.md"
    scorecard = base._blob(repo, tip_sha, scorecard_path)
    if scorecard is None:
        raise CouldNotEvaluate("{} is missing at {}".format(scorecard_path, tip_sha))
    section = base._round_section(scorecard.decode("utf-8", "replace"), round_no)
    if section is None:
        raise CouldNotEvaluate(
            "{} at {} carries no '## Round {}' section; the round's self-record "
            "cannot be read".format(scorecard_path, tip_sha, round_no)
        )
    lesson_path = "corpus/lessons/round-{}.md".format(round_no)
    lesson = base._blob(repo, tip_sha, lesson_path)
    if lesson is None:
        raise CouldNotEvaluate("{} is missing at {}".format(lesson_path, tip_sha))
    lines, offset = section
    return [
        (scorecard_path, lines, offset),
        (lesson_path, lesson.decode("utf-8", "replace").splitlines(), 0),
    ]


def _claim_pass(repo, tip_sha, round_no, base, blob_reader=None):
    """Grade tip claims against the receipts they cite.

    ``blob_reader(path)`` returns the receipt's bytes at the tip (or None when absent); the
    default reads the tip's blob through the base module. The parameter exists so the selftest
    can grade the header-equals-tip comparison directly: a receipt that names the commit which
    contains it is a git hash fixpoint and cannot be committed (r72 attack §2 D2).
    """
    read = blob_reader or (lambda path: base._blob(repo, tip_sha, path))
    claims = 0
    unbound_claims = 0
    findings = []
    for filename, lines, offset in _read_records(repo, tip_sha, round_no, base):
        for index, line in enumerate(lines):
            low = line.lower()
            if not any(token in low for token in TIP_CLAIM_TOKENS):
                continue
            cited = []
            for match in base.TOKEN_RE.finditer(line):
                where = "{}:{}".format(filename, offset + index + 1)
                paths = base._resolve_citation(
                    repo, tip_sha, round_no, match.group(1).strip(), where
                )
                for path in paths or []:
                    if path not in cited:
                        cited.append(path)
            if not cited:
                continue
            claims += 1
            line_findings = []
            for path in cited:
                blob = read(path)
                if blob is None:
                    rev = None
                else:
                    rev, _problem = base._header_rev(blob)
                if rev is None or rev != tip_sha:
                    line_findings.append(
                        {
                            "path": path,
                            "line_no": offset + index + 1,
                            "line": line.strip(),
                        }
                    )
            if line_findings:
                unbound_claims += 1
                findings.extend(line_findings)
    return {"claims": claims, "unbound_claims": unbound_claims, "findings": findings}


# ---------------------------------------------------------------- grading


def summary_line(result):
    return (
        "RECEIPT_CLAIM_BINDING round={} cited={} bound={} unbound={} shifted={} "
        "stale={} claims={} unbound_claims={}".format(
            result["round"],
            result["cited"],
            result["bound"],
            result["unbound"],
            result["shifted"],
            result["stale"],
            result["claims"],
            result["unbound_claims"],
        )
    )


def claim_finding_line(finding):
    return "RECEIPT_CLAIM_FINDING stale-claim {} :: {}: {}".format(
        finding["path"], finding["line_no"], finding["line"]
    )


def audit(repo, tip, round_no, base_path=None):
    repo = os.path.abspath(repo)
    path = _base_tool_path(repo, base_path)
    if path is None:
        raise CouldNotEvaluate(
            "the frozen base tool {} is absent (looked beside this module and under "
            "{}/tools/)".format(BASE_TOOL_NAME, repo)
        )
    base = _load_base(path)
    if base._git(repo, "rev-parse", "--show-toplevel", check=False).returncode != 0:
        raise CouldNotEvaluate("{} is not a git repository".format(repo))
    base_doc = _run_base(path, repo, round_no, tip)
    tip_sha = base._commit_sha(repo, tip)
    if tip_sha is None:
        raise CouldNotEvaluate("tip {} is not a commit in {}".format(tip, repo))
    if int(base_doc["cited"]) == 0:
        raise CouldNotEvaluate(
            "the round-{} self-record cites no receipt path; nothing to bind".format(round_no)
        )
    claim = _claim_pass(repo, tip_sha, round_no, base)
    result = {
        "round": round_no,
        "tip": tip,
        "tip_commit": tip_sha,
        "repo": repo,
        "base_tool": path,
        "base_exit": int(base_doc["exit"]),
        "cited": int(base_doc["cited"]),
        "bound": int(base_doc["bound"]),
        "unbound": int(base_doc["unbound"]),
        "shifted": int(base_doc["shifted"]),
        "stale": int(base_doc["stale"]),
        "claims": claim["claims"],
        "unbound_claims": claim["unbound_claims"],
        "claim_findings": claim["findings"],
    }
    base_lines = base.render(base_doc).splitlines()[:-1]
    result["base_finding_lines"] = base_lines
    result["line"] = summary_line(result)
    clean = result["base_exit"] == 0 and result["unbound_claims"] == 0
    result["exit"] = 0 if clean else 1
    return result


# ---------------------------------------------------------------- selftest


def _plan_c2_predicate(text):
    """The plan's C2 blockquote with the `>` marks and line breaks removed."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith(PLAN_C2_HEADING):
            start = index
            break
    if start is None:
        return ""
    run = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.startswith(">"):
            run.append(line)
        elif run:
            break
    if not run:
        return ""
    body = []
    for line in run:
        text_line = line[1:]
        if text_line.startswith(" "):
            text_line = text_line[1:]
        body.append(text_line.strip())
    return " ".join(body)


def _run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 2
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 2
    return int(code), out.getvalue(), err.getvalue()


def _arm(outcomes, name, rc, out, err, expect_rc, must_out=(), must_err=(), must_not=()):
    ok = rc == expect_rc
    if ok:
        ok = (
            all(text in out for text in must_out)
            and all(text in err for text in must_err)
            and not any(text in out for text in must_not)
        )
    outcomes.append(
        {"name": name, "ok": ok, "rc": rc, "expect": expect_rc, "out": out, "err": err}
    )


RECEIPT = ".ufo/waves/round-72/measured/after/x.out"
SCORECARD_HEAD = "# fixture scorecard\n\n## Round 71 — previous round\n\nKind: n/a\n\n"


def _selftest_arms(scratch, outcomes):
    base = _load_base(os.path.join(_HERE, BASE_TOOL_NAME))

    def top(fixture):
        shown = base._text(base._git(fixture.path, "rev-parse", "--show-toplevel")).strip()
        return os.path.realpath(shown)

    def commit(fixture, message):
        if top(fixture) != os.path.realpath(fixture.path):
            raise CouldNotEvaluate(
                "fixture {} is not its own git root ({})".format(fixture.path, top(fixture))
            )
        return fixture.commit(message)

    def record(fixture, round_no, scorecard_body, lesson_body="No citation here.\n"):
        fixture.write(
            "corpus/lessons/round-{}.md".format(round_no),
            "# Round {} lesson\n\n{}".format(round_no, lesson_body),
        )
        fixture.write(
            "SCORECARD.md",
            "# fixture scorecard\n\n## Round {} — fixture\n\n{}\n".format(
                round_no, scorecard_body
            ),
        )

    # arm: the predicate sentence is one line, carries both output shapes, and is byte-equal
    # to the frozen plan's C2 blockquote with the `>` marks and line breaks removed
    one_line = "\n" not in PREDICATE
    shape = (
        "RECEIPT_CLAIM_BINDING round=<N> cited=<c>" in PREDICATE
        and "RECEIPT_CLAIM_FINDING stale-claim <path>" in PREDICATE
    )
    plan_path = os.path.join(os.path.dirname(_HERE), PLAN_NAME)
    if os.path.isfile(plan_path):
        with open(plan_path, encoding="utf-8") as handle:
            plan_state = "True" if _plan_c2_predicate(handle.read()) == PREDICATE else "False"
    else:
        plan_state = "absent"
    _arm(
        outcomes,
        "predicate",
        0 if (one_line and shape and plan_state != "False") else 1,
        "one_line={} shape={} plan={}".format(one_line, shape, plan_state),
        "",
        0,
        must_out=["one_line=True shape=True"],
    )

    # arm: base green and no tip claim -> exit 0, claims=0 (both notations dedupe to one path)
    fx = base._Fixture(scratch, "clean")
    fx.write("tools/counter.py", "# counter\n")
    seed = commit(fx, "base with the instrument")
    fx.write(RECEIPT, "# tip={}\nRECEIPT bound\n".format(seed))
    record(
        fx,
        72,
        "Receipt: `{}`".format(RECEIPT),
        lesson_body="Shorthand citation: `measured/after/x.out`\n",
    )
    tip = commit(fx, "record plus receipt")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "clean-no-tip-claim", rc, out, err, 0,
        must_out=[
            "RECEIPT_CLAIM_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 "
            "stale=0 claims=0 unbound_claims=0",
        ],
        must_not=["RECEIPT_CLAIM_FINDING", "RECEIPT_TIP_FINDING"],
    )

    # arm: the B6 survivor -- receipt measured at X, record-only delta, "at the report tip".
    # The frozen base tool accepts this fixture; the claim pass must kill it.
    b6 = base._Fixture(scratch, "b6")
    b6.write("LOG.md", "# fixture log\n")
    b6.write(RECEIPT, "# rev=PLACEHOLDER\nverdict: green\n")
    measured = commit(b6, "receipt at X")
    b6.write(RECEIPT, "# rev={}\nverdict: green\n".format(measured))
    commit(b6, "receipt header names X")
    record(b6, 72, "C1 evidence, no receipt.")
    commit(b6, "record with no receipt citation")
    record(
        b6,
        72,
        "- C1 evidence: `{}` — the gate ran at the report tip.".format(RECEIPT),
    )
    b6_tip = commit(b6, "record-only commit adds the tip claim")
    base_rc, base_out, base_err = base._run_cli(
        ["--repo", b6.path, "--round", "72", "--tip", b6_tip]
    )
    rc, out, err = _run_cli(["--repo", b6.path, "--round", "72", "--tip", b6_tip])
    _arm(
        outcomes, "b6-base-accepts", base_rc, base_out, base_err, 0,
        must_out=["RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0"],
    )
    _arm(
        outcomes, "b6-tip-claim", rc, out, err, 1,
        must_out=[
            "RECEIPT_CLAIM_FINDING stale-claim " + RECEIPT,
            "RECEIPT_CLAIM_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 "
            "stale=0 claims=1 unbound_claims=1",
        ],
    )

    # arm: the header-equals-tip comparison itself. A receipt whose header names the commit
    # that contains it is a git hash fixpoint and cannot be committed (r72 attack §2 D2), so
    # the comparison is graded through the injectable blob reader: same fixture, same record,
    # same tip claim, header equal to the tip -> no finding.
    eq = base._Fixture(scratch, "equal")
    eq.write("LOG.md", "# fixture log\n")
    eq_seed = commit(eq, "base")
    eq.write(RECEIPT, "# rev={}\nreceipt\n".format(eq_seed))
    record(eq, 72, "Receipt: `{}` — read at the report tip.".format(RECEIPT))
    eq_tip = commit(eq, "record")
    real = _claim_pass(eq.path, eq_tip, 72, base)
    same = _claim_pass(
        eq.path,
        eq_tip,
        72,
        base,
        blob_reader=lambda path: (
            "# rev={}\nreceipt\n".format(eq_tip).encode("utf-8")
            if path == RECEIPT
            else base._blob(eq.path, eq_tip, path)
        ),
    )
    ok = (
        real["claims"] == 1
        and real["unbound_claims"] == 1
        and len(real["findings"]) == 1
        and same["claims"] == 1
        and same["unbound_claims"] == 0
        and not same["findings"]
    )
    _arm(
        outcomes,
        "claim-header-equals-tip",
        0 if ok else 1,
        "real_claims={} real_unbound={} same_claims={} same_unbound={} same_findings={}".format(
            real["claims"],
            real["unbound_claims"],
            same["claims"],
            same["unbound_claims"],
            len(same["findings"]),
        ),
        "",
        0,
        must_out=["real_unbound=1 same_claims=1 same_unbound=0 same_findings=0"],
    )

    # arm: a citation phrased "measured at rev X" carries no tip token -> not a claim
    measured_at = base._Fixture(scratch, "measuredat")
    measured_at.write("tools/counter.py", "# counter\n")
    rev = commit(measured_at, "base")
    measured_at.write(RECEIPT, "# rev={}\nreceipt\n".format(rev))
    record(
        measured_at,
        72,
        "C2 receipt `{}` measured at rev {}.".format(RECEIPT, rev[:12]),
    )
    tip = commit(measured_at, "record")
    rc, out, err = _run_cli(["--repo", measured_at.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "measured-at-rev-no-tip-token", rc, out, err, 0,
        must_out=["claims=0 unbound_claims=0"],
        must_not=["RECEIPT_CLAIM_FINDING"],
    )

    # arm: a non-receipt citation on a tip-claim line is out of scope (control scripts)
    nonreceipt = base._Fixture(scratch, "nonreceipt")
    nonreceipt.write("tools/counter.py", "# counter\n")
    rev = commit(nonreceipt, "base")
    nonreceipt.write(RECEIPT, "# rev={}\nreceipt\n".format(rev))
    record(
        nonreceipt,
        72,
        "Receipt: `{}`; the counter `tools/counter.py` ran at the report tip.".format(RECEIPT),
    )
    tip = commit(nonreceipt, "record")
    rc, out, err = _run_cli(["--repo", nonreceipt.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "non-receipt-citation-out-of-scope", rc, out, err, 1,
        must_out=[
            "RECEIPT_CLAIM_FINDING stale-claim " + RECEIPT,
            "claims=1 unbound_claims=1",
        ],
    )

    # arm: the tip claim can sit in the lesson file; its line number is the lesson's own
    lesson = base._Fixture(scratch, "lesson")
    lesson.write("tools/counter.py", "# counter\n")
    rev = commit(lesson, "base")
    lesson.write(RECEIPT, "# rev={}\nreceipt\n".format(rev))
    record(
        lesson,
        72,
        "No receipt citation here.",
        lesson_body="See `measured/after/x.out` at the tip.\n",
    )
    tip = commit(lesson, "record")
    rc, out, err = _run_cli(["--repo", lesson.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "lesson-tip-claim", rc, out, err, 1,
        must_out=[
            "RECEIPT_CLAIM_FINDING stale-claim " + RECEIPT + " :: 3: ",
            "claims=1 unbound_claims=1",
        ],
    )

    # arm: a base finding is kept and echoed; the claim pass runs alongside it
    red = base._Fixture(scratch, "basered")
    red.write("tools/counter.py", "# counter\n")
    commit(red, "base")
    red.write(RECEIPT, "RECEIPT without any header\n")
    record(red, 72, "Receipt: `{}`".format(RECEIPT))
    tip = commit(red, "record")
    rc, out, err = _run_cli(["--repo", red.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "base-red-echo", rc, out, err, 1,
        must_out=[
            "RECEIPT_TIP_FINDING unbound " + RECEIPT,
            "claims=0 unbound_claims=0",
        ],
    )

    # arm: the record cites no receipt at all -> exit 2, never a silent 0
    empty = base._Fixture(scratch, "empty")
    empty.write("tools/counter.py", "# counter\n")
    commit(empty, "base")
    record(empty, 72, "Prose only, no receipt citation.")
    tip = commit(empty, "record")
    rc, out, err = _run_cli(["--repo", empty.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "cited-zero", rc, out, err, 2,
        must_err=["cites no receipt path"],
        must_not=["RECEIPT_CLAIM_BINDING round="],
    )

    # arm: no `## Round 72` section at the tip -> exit 2
    nosection = base._Fixture(scratch, "nosection")
    nosection.write("tools/counter.py", "# counter\n")
    nosection.write("SCORECARD.md", SCORECARD_HEAD + "Kind: n/a\n")
    nosection.write("corpus/lessons/round-72.md", "# Round 72 lesson\n")
    tip = commit(nosection, "scorecard without a round-72 section")
    rc, out, err = _run_cli(["--repo", nosection.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "missing-round-section", rc, out, err, 2,
        must_err=["carries no '## Round 72' section"],
    )

    # arm: an absent base tool -> exit 2, naming it
    rc, out, err = _run_cli(
        [
            "--repo", nosection.path,
            "--round", "72",
            "--tip", tip,
            "--base-tool", os.path.join(scratch, "no-such-base.py"),
        ]
    )
    _arm(
        outcomes, "base-tool-absent", rc, out, err, 2,
        must_err=["is absent", BASE_TOOL_NAME],
    )

    # arm: a base finding prints first, claim findings second, one exit code
    both = base._Fixture(scratch, "both")
    both.write("tools/counter.py", "# counter\n")
    seed = commit(both, "base")
    both.write(RECEIPT, "# rev={}\nreceipt\n".format(seed))
    headless = ".ufo/waves/round-72/measured/after/noheader.out"
    both.write(headless, "no header here\n")
    record(
        both,
        72,
        "Old: `{}` at the report tip; unbound: `{}`.".format(RECEIPT, headless),
    )
    tip = commit(both, "record")
    rc, out, err = _run_cli(["--repo", both.path, "--round", "72", "--tip", tip])
    base_at = out.find("RECEIPT_TIP_FINDING unbound " + headless)
    claim_at = out.find("RECEIPT_CLAIM_FINDING stale-claim " + RECEIPT)
    ordered = base_at != -1 and claim_at != -1 and base_at < claim_at
    _arm(
        outcomes,
        "base-finding-then-claim",
        0 if (rc == 1 and ordered) else 1,
        out,
        err,
        0,
        must_out=["claims=1 unbound_claims=1"],
    )

    # arm: CLI misuse is exit 2 (missing --round, and --round 0)
    rc_missing, _, _ = _run_cli(["--repo", nosection.path, "--tip", tip])
    rc_zero, _, _ = _run_cli(["--repo", nosection.path, "--round", "0", "--tip", tip])
    _arm(
        outcomes,
        "cli-misuse",
        0 if (rc_missing == 2 and rc_zero == 2) else 1,
        "missing={} zero={}".format(rc_missing, rc_zero),
        "",
        0,
        must_out=["missing=2 zero=2"],
    )


def run_selftest(args):
    if args.work:
        root = os.path.abspath(args.work)
        os.makedirs(root, exist_ok=True)
        scratch = os.path.join(root, "claim-selftest-{}".format(os.getpid()))
        os.makedirs(scratch, exist_ok=True)
    else:
        scratch = tempfile.mkdtemp(prefix="receipt-claim-binding-selftest-")
    outcomes = []
    try:
        _selftest_arms(scratch, outcomes)
    except (CouldNotEvaluate, OSError) as exc:
        outcomes.append(
            {
                "name": "fixture-build",
                "ok": False,
                "rc": 2,
                "expect": 0,
                "out": "",
                "err": str(exc),
            }
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for item in outcomes:
        print(
            "RECEIPT_CLAIM_BINDING_ARM {} expect={} got={} {}".format(
                item["name"], item["expect"], item["rc"], "ok" if item["ok"] else "FAIL"
            )
        )
        if not item["ok"]:
            for stream in ("out", "err"):
                text = item[stream].strip()
                for line in text.splitlines()[:20]:
                    print("    {}: {}".format(stream, line))
    passed = sum(1 for item in outcomes if item["ok"])
    failed = len(outcomes) - passed
    print("RECEIPT_CLAIM_BINDING_SELFTEST pass={} fail={}".format(passed, failed))
    return 1 if failed else 0


# -------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="round73-receipt-claim-binding.py",
        description=(
            "Bind every tip claim in a round's self-record to the revision the receipt it "
            "cites measured (composes the frozen round72-receipt-tip-binding.py)."
        ),
    )
    ap.add_argument("--repo", default=".", help="repository to grade (default: .)")
    ap.add_argument("--round", dest="round_no", type=int, default=None, metavar="N",
                    help="round number whose self-record is read (required unless --selftest)")
    ap.add_argument("--tip", default="master",
                    help="revision the claims are bound to (default: master)")
    ap.add_argument("--base-tool", dest="base_tool", default=None, metavar="PATH",
                    help="override the frozen base tool path (default: the sibling tool)")
    ap.add_argument("--work", default=None,
                    help="scratch directory for the selftest fixtures")
    ap.add_argument("--selftest", action="store_true", help="run the fixture selftest")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest(args)
    if args.round_no is None:
        ap.error("the following arguments are required: --round")
    if args.round_no < 1:
        ap.error("--round must be a positive integer")

    try:
        result = audit(args.repo, args.tip, args.round_no, args.base_tool)
    except CouldNotEvaluate as exc:
        print("RECEIPT_CLAIM_BINDING_UNREADABLE {}".format(exc), file=sys.stderr)
        return 2

    for line in result["base_finding_lines"]:
        print(line)
    for finding in result["claim_findings"]:
        print(claim_finding_line(finding))
    print(result["line"])
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
