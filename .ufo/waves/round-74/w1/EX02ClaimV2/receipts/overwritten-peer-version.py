#!/usr/bin/env python3
"""round74-receipt-claim-binding.py — round-74 C2 (operability).

The realizable replacement for round 73's impossible clean rule
(a committed receipt header equal to its containing commit is a git hash
fixed point; `corpus/lessons/round-73-verifier-spotcheck.md` §2 C2): the
round's self-record binds its receipt citations by EXPLICIT REVISION, and the
claim grading is paragraph-scoped, killing the wrapped/offset escapes the
line-scoped round-73 pass misses (before receipt:
`.ufo/waves/round-74/measured/before/score-survivors-base.out` — the r73
counter exits 0 with `claims=0` on both escape fixtures).

Composition: the byte-frozen `tools/round72-receipt-tip-binding.py` runs as the
base leg (subprocess, same argv shape as the r73 module); the byte-frozen
`tools/round73-receipt-claim-binding.py` and the r72 module are imported only
for their record readers, citation resolver and base runner — never edited.

    RECEIPT_CLAIM_V2 round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s>
        stale=<t> claims=<k> unbound_claims=<j> bound_revisions=<r>

Exit: 0 clean (base green, no claim finding); 1 findings; 2 could-not-evaluate
(base tool absent/exit 2, self-record unreadable, CLI misuse). A scored run
never exits 2 for a finding.

Finding kinds: `wrapped-claim` (the tip-claim token is split across hard line
breaks — no single line of the paragraph carries it whole), `offset-claim`
(the token is whole on some line but no line carries both the token and a
citation), `stale-claim` (token and citation share one line and the cited
receipt's header names another revision — the inherited round-73 shape; the
frozen predicate enumerates the three NEW arm kinds and this inherited kind
keeps its round-73 name, disclosed in the round-74 report and lesson), and
`stale-revision` (the paragraph names an explicit 40-hex revision and a cited
receipt's header differs).

Revision mentions bind case-insensitively: git object names are hex, and an
honest record may name a receipt's revision in any hex case (the frozen
`c2_mixed_honest` fixture names the fixture receipt's own commit in upper
case). Receipt headers are parsed with a case-insensitive `tip=`/`rev=` key
and hex; conflicting headers inside the first five lines stay a
could-not-evaluate-class problem of the paragraph that cites them.

The `blob_reader` parameter on the claim pass exists so the selftest can
inject receipt bytes the way the byte-frozen r73 module already does
(`_claim_pass(..., blob_reader=...)`): the round-74 selftest's seam arm
injects a receipt whose header names the tip in upper-case hex — a pristine
module binds it; a case-sensitive mutant flags it (MT01Mutants' surviving
mutant `c2_p2l_case_hex`, which no committable fixture can carry).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)

PREDICATE = "`python3 tools/round74-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>` prints one `RECEIPT_CLAIM_V2 round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t> claims=<k> unbound_claims=<j> bound_revisions=<r>` line and exits 0 only when the byte-frozen `tools/round72-receipt-tip-binding.py` verdict for `<rev>` is green and every blank-line-separated paragraph of the round's self-record (the `## Round <N>` section of `SCORECARD.md` and `corpus/lessons/round-<N>.md` at `<rev>`) that both cites a receipt and carries a tip claim (`at the tip`, `at the report tip`, `report tip`, case-insensitive, matched across line breaks inside the paragraph) has every cited receipt whose own `tip=`/`rev=` header (case-insensitive key and hex) names `<rev>`; a paragraph that names an explicit 40-hex revision binds each cited receipt whose header equals that revision (hex compared case-insensitively), and is a finding when the header differs; it exits 1 naming each base finding and each `RECEIPT_CLAIM_V2_FINDING <wrapped-claim|offset-claim|stale-revision> <path> :: <line>`, and 2 when the base tool or the self-record cannot be evaluated."

TIP_CLAIM_TOKENS = ("at the report tip", "at the tip", "report tip")
PLAN_NAME = "plans/round-74-claims.md"
PLAN_C2_HEADING = "## C2"
TIMEOUT = 300
HEADER_WINDOW = 5
# case-insensitive key AND hex; the r72 base keeps its own (lower-key) parse
# for the base leg — the v2 claim pass re-reads headers itself.
HEADER_RE_V2 = re.compile(r"(?:^|[^\w-])(?:#\s*)?(?:tip|rev)=([0-9a-fA-F]{40})(?![0-9a-fA-F])", re.I)
REVISION_RE = re.compile(r"\brev(?:ision)?\s+([0-9a-fA-F]{40})\b", re.I)

sys.path.insert(0, HERE)
import round73_receipt_claim_binding as r73  # noqa: E402  (byte-frozen; imported, never edited)

BASE = r73


class CouldNotEvaluate(Exception):
    pass


# ------------------------------------------------------------ claim pass v2


def _header_rev_v2(blob):
    """(rev, problem): rev is None with a problem, or one lower-case 40-hex."""
    window = blob.decode("utf-8", "replace").splitlines()[:HEADER_WINDOW]
    revs = []
    for line in window:
        for match in HEADER_RE_V2.finditer(line):
            revs.append(match.group(1).lower())
    if not revs:
        return None, "no tip=/rev= header among the first {} lines".format(HEADER_WINDOW)
    if len(set(revs)) > 1:
        return None, "conflicting header revisions: {}".format(",".join(sorted(set(revs))))
    return revs[0], ""


def _paragraphs(lines):
    """[(first_line_no, [lines])] for every blank-line-separated paragraph."""
    out = []
    buf = []
    start = 0
    for number, line in enumerate(lines, 1):
        if line.strip():
            if not buf:
                start = number
            buf.append(line)
        elif buf:
            out.append((start, buf))
            buf = []
    if buf:
        out.append((start, buf))
    return out


def _claim_kind(plines, has_token, base):
    """Classify a tip-claim paragraph: wrapped-claim / offset-claim / same-line."""
    token_lines = [l for l in plines
                   if any(tok in l.lower() for tok in TIP_CLAIM_TOKENS)]
    if not token_lines:
        return None  # token only appears across line breaks
    for line in token_lines:
        if base.TOKEN_RE.search(line):
            return "same-line"
    return "offset-claim"


def _claim_pass_v2(repo, tip_sha, round_no, base, blob_reader=None):
    """Paragraph-scoped claim grading; ``blob_reader`` is the selftest seam."""
    read = blob_reader or (lambda path: base._blob(repo, tip_sha, path))
    claims = 0
    unbound_claims = 0
    bound_revisions = 0
    findings = []
    for filename, lines, offset in r73._read_records(repo, tip_sha, round_no, base):
        for start, plines in _paragraphs(lines):
            text = "\n".join(plines)
            low = text.lower()
            has_token = any(tok in low for tok in TIP_CLAIM_TOKENS)
            cited = []
            for match in base.TOKEN_RE.finditer(text):
                where = "{}:{}".format(filename, offset + start)
                paths = base._resolve_citation(
                    repo, tip_sha, round_no, match.group(1).strip(), where)
                for path in paths or []:
                    if path not in cited:
                        cited.append(path)
            if not cited:
                continue
            rev_mentions = [m.group(1).lower() for m in REVISION_RE.finditer(text)]
            headers = {}
            for path in cited:
                blob = read(path)
                headers[path] = (None, "absent at tip") if blob is None else _header_rev_v2(blob)
            if has_token:
                claims += 1
                line_findings = []
                for path in cited:
                    rev, _problem = headers[path]
                    if rev is None or rev != tip_sha:
                        line_findings.append(path)
                if line_findings:
                    kind = _claim_kind(plines, has_token, base) or "wrapped-claim"
                    if kind == "same-line":
                        kind = "stale-claim"
                    unbound_claims += 1
                    for path in line_findings:
                        findings.append({
                            "kind": kind, "path": path,
                            "line_no": offset + start, "line": plines[0].strip(),
                        })
            elif rev_mentions:
                for want in rev_mentions:
                    for path in cited:
                        rev, _problem = headers[path]
                        if rev is not None and rev == want:
                            bound_revisions += 1
                        else:
                            findings.append({
                                "kind": "stale-revision", "path": path,
                                "line_no": offset + start, "line": plines[0].strip(),
                            })
    return {"claims": claims, "unbound_claims": unbound_claims,
            "bound_revisions": bound_revisions, "findings": findings}


def summary_line(result):
    return (
        "RECEIPT_CLAIM_V2 round={} cited={} bound={} unbound={} shifted={} "
        "stale={} claims={} unbound_claims={} bound_revisions={}".format(
            result["round"], result["cited"], result["bound"], result["unbound"],
            result["shifted"], result["stale"], result["claims"],
            result["unbound_claims"], result["bound_revisions"]))


def claim_finding_line(finding):
    return "RECEIPT_CLAIM_V2_FINDING {} {} :: {}: {}".format(
        finding["kind"], finding["path"], finding["line_no"], finding["line"])


def audit(repo, tip, round_no, base_path=None):
    repo = os.path.abspath(repo)
    path = r73._base_tool_path(repo, base_path)
    if path is None:
        raise CouldNotEvaluate(
            "the frozen base tool {} is absent (looked beside this module and under "
            "{}/tools/)".format(r73.BASE_TOOL_NAME, repo))
    base = r73._load_base(path)
    if base._git(repo, "rev-parse", "--show-toplevel", check=False).returncode != 0:
        raise CouldNotEvaluate("{} is not a git repository".format(repo))
    base_doc = r73._run_base(path, repo, round_no, tip)
    tip_sha = base._commit_sha(repo, tip)
    if tip_sha is None:
        raise CouldNotEvaluate("tip {} is not a commit in {}".format(tip, repo))
    if int(base_doc["cited"]) == 0:
        raise CouldNotEvaluate(
            "the round-{} self-record cites no receipt path; nothing to bind".format(round_no))
    claim = _claim_pass_v2(repo, tip_sha, round_no, base)
    result = {
        "round": round_no, "tip": tip, "tip_commit": tip_sha, "repo": repo,
        "base_tool": path, "base_exit": int(base_doc["exit"]),
        "cited": int(base_doc["cited"]), "bound": int(base_doc["bound"]),
        "unbound": int(base_doc["unbound"]), "shifted": int(base_doc["shifted"]),
        "stale": int(base_doc["stale"]),
        "claims": claim["claims"], "unbound_claims": claim["unbound_claims"],
        "bound_revisions": claim["bound_revisions"],
        "claim_findings": claim["findings"],
    }
    result["base_finding_lines"] = base.render(base_doc).splitlines()[:-1]
    result["line"] = summary_line(result)
    clean = (result["base_exit"] == 0 and result["unbound_claims"] == 0
             and not result["claim_findings"])
    result["exit"] = 0 if clean else 1
    return result


# ---------------------------------------------------------------- selftest


def _plan_c2_predicate(text):
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
        body.append(text_line)
    return "\n".join(body).replace("\n", " ").strip()


def _arm(outcomes, name, rc, out, err, expect_rc, must_out=(), must_err=(), must_not=()):
    ok = rc == expect_rc
    for needle in must_out:
        if needle not in out:
            ok = False
    for needle in must_err:
        if needle not in err:
            ok = False
    for needle in must_not:
        if needle in out or needle in err:
            ok = False
    outcomes.append((name, ok, "rc={} want={}".format(rc, expect_rc)))
    return ok


def _selftest_arms(scratch, outcomes):
    base_mod = r73._load_base(r73._base_tool_path(LANE, None))
    fx = r73._Fixture(scratch, "v2")

    # (1) predicate arm: one line, both output shapes, byte-equal to the plan
    one_line = "\n" not in PREDICATE
    shape = ("RECEIPT_CLAIM_V2 round=<N> cited=<c>" in PREDICATE
             and "RECEIPT_CLAIM_V2_FINDING <wrapped-claim|offset-claim|stale-revision>" in PREDICATE)
    plan_path = os.path.join(LANE, PLAN_NAME)
    plan_state = "absent"
    if os.path.isfile(plan_path):
        with open(plan_path, encoding="utf-8") as handle:
            plan_state = "True" if _plan_c2_predicate(handle.read()) == PREDICATE else "False"
    _arm(outcomes, "predicate",
         0 if (one_line and shape and plan_state != "False") else 1,
         "one_line={} shape={} plan={}".format(one_line, shape, plan_state), "",
         0, must_out=["one_line=True shape=True"])

    # (2) the plan blob at master carries the same C2 sentence
    blob = base_mod._blob(LANE, base_mod._commit_sha(LANE, "master"), PLAN_NAME)
    blob_state = "absent"
    if blob is not None:
        blob_state = "True" if _plan_c2_predicate(blob.decode("utf-8", "replace")) == PREDICATE else "False"
    _arm(outcomes, "predicate-at-tip", 0 if blob_state == "True" else 1,
         "plan_at_master={}".format(blob_state), "", 0, must_out=["plan_at_master=True"])

    # (3) committed-builder fixtures replay: the frozen kill and clean arms
    builder = os.path.join(LANE, ".ufo/waves/round-74/controls/build-survivors.py")
    work = os.path.join(scratch, "committed-fixtures")
    meta_path = os.path.join(work, "fixtures-meta.json")
    if os.path.isfile(builder):
        env = dict(os.environ)
        env["KAMA_R74_SCRATCH"] = work
        subprocess.run([sys.executable, builder, "--work", work, "--meta", meta_path],
                       check=True, capture_output=True, text=True, env=env)
        meta = json.loads(open(meta_path).read())
        want = {
            "c2_wrapped": (1, "RECEIPT_CLAIM_V2_FINDING wrapped-claim"),
            "c2_offset": (1, "RECEIPT_CLAIM_V2_FINDING offset-claim"),
            "c2_mixed_honest": (0, "bound_revisions=1"),
            "c2_clean_realizable": (0, "unbound_claims=0"),
        }
        all_ok = True
        detail = []
        for name, (want_rc, needle) in want.items():
            case = meta[name]
            res = audit(case["fixture"], "master", 74)
            got = (res["exit"], res["line"])
            ok = res["exit"] == want_rc and (needle in res["line"] or any(
                needle in claim_finding_line(f) for f in res["claim_findings"]))
            all_ok = all_ok and ok
            detail.append("{} rc={} {}".format(name, got[0], got[1]))
        _arm(outcomes, "committed-fixtures", 0 if all_ok else 1,
             " | ".join(detail), "", 0, must_out=["c2_wrapped rc=1", "c2_offset rc=1"])
    else:
        _arm(outcomes, "committed-fixtures", 1, "builder absent", "", 0)

    # (4) blob_reader seam (MT01Mutants' surviving-mutant arm): a receipt whose
    # header names the TIP in upper-case hex binds under the pristine pass and
    # would be flagged by a case-sensitive mutant.
    tip_hex_upper = None
    seam_ok = False
    try:
        seam_fx = r73._Fixture(scratch, "seam")
        seed = fx_commit(seam_fx, "base")
        tip_hex_upper = seed.upper()
        seam_fx.write(".ufo/waves/round-74/measured/seam.out",
                      "# REV={}\nverdict: green\n".format(tip_hex_upper))
        seam_fx.write("SCORECARD.md",
                      "# fixture\n\n## Round 74 — fixture\n\n"
                      "- C2 seam: measured `.ufo/waves/round-74/measured/seam.out` at the tip.\n")
        seam_fx.write("corpus/lessons/round-74.md", "# lesson\n")
        seam_fx.write("plans/round-74-claims.md",
                      "# kama round 74 — frozen claims\n\nfixture\n")
        fx_commit(seam_fx, "record")
        blob = seam_fx.read(".ufo/waves/round-74/measured/seam.out")
        repo = seam_fx.path
        base = r73._load_base(r73._base_tool_path(LANE, None))
        tip_sha = base._commit_sha(repo, "master")
        pristine = _claim_pass_v2(
            repo, tip_sha, 74, base,
            blob_reader=lambda path, _b=blob: _b if path.endswith("seam.out") else None)
        mutant_headers = {}
        for path_ in (".ufo/waves/round-74/measured/seam.out",):
            mutant_headers[path_] = _header_rev_v2_case(blob)
        seam_ok = (pristine["claims"] == 1 and pristine["unbound_claims"] == 0
                   and mutant_headers[".ufo/waves/round-74/measured/seam.out"][0] is None)
        _arm(outcomes, "blob-reader-seam", 0 if seam_ok else 1,
             "pristine claims={} unbound={} mutant_header=None".format(
                 pristine["claims"], pristine["unbound_claims"]), "", 0,
             must_out=["unbound=0"])
    except Exception as exc:  # fixture failure is a selftest failure, not exit 2
        _arm(outcomes, "blob-reader-seam", 1, "seam fixture failed: {}".format(exc), "", 0)

    # (5) stale-revision arm: named explicit revision differs from the header
    try:
        sr_fx = r73._Fixture(scratch, "stale-rev")
        seed = fx_commit(sr_fx, "base")
        sr_fx.write(".ufo/waves/round-74/measured/sr.out", "# rev={}\nverdict\n".format(seed))
        fx_commit(sr_fx, "receipt")
        other = "a" * 40
        sr_fx.write("SCORECARD.md",
                    "# fixture\n\n## Round 74 — fixture\n\n"
                    "- C2: re-run at revision {} naming `.ufo/waves/round-74/measured/sr.out`.\n"
                    .format(other))
        sr_fx.write("corpus/lessons/round-74.md", "# lesson\n")
        sr_fx.write("plans/round-74-claims.md",
                    "# kama round 74 — frozen claims\n\nfixture\n")
        fx_commit(sr_fx, "record names a wrong revision")
        res = audit(sr_fx.path, "master", 74)
        ok = res["exit"] == 1 and any(
            f["kind"] == "stale-revision" for f in res["claim_findings"])
        _arm(outcomes, "stale-revision", 0 if ok else 1,
             "exit={} findings={}".format(res["exit"], len(res["claim_findings"])), "", 0)
    except Exception as exc:
        _arm(outcomes, "stale-revision", 1, "fixture failed: {}".format(exc), "", 0)

    # (6) same-line stale keeps the inherited kind
    try:
        sl_fx = r73._Fixture(scratch, "same-line")
        seed = fx_commit(sl_fx, "base")
        sl_fx.write(".ufo/waves/round-74/measured/sl.out", "# rev={}\nverdict\n".format(seed))
        fx_commit(sl_fx, "receipt")
        sl_fx.write("SCORECARD.md",
                    "# fixture\n\n## Round 74 — fixture\n\n"
                    "- C2: `.ufo/waves/round-74/measured/sl.out` measured at the tip.\n")
        sl_fx.write("corpus/lessons/round-74.md", "# lesson\n")
        sl_fx.write("plans/round-74-claims.md",
                    "# kama round 74 — frozen claims\n\nfixture\n")
        fx_commit(sl_fx, "record")
        res = audit(sl_fx.path, "master", 74)
        ok = res["exit"] == 1 and any(
            f["kind"] == "stale-claim" for f in res["claim_findings"])
        _arm(outcomes, "same-line-stale-claim", 0 if ok else 1,
             "exit={} kinds={}".format(res["exit"], sorted({f["kind"] for f in res["claim_findings"]})),
             "", 0, must_out=["stale-claim"])
    except Exception as exc:
        _arm(outcomes, "same-line-stale-claim", 1, "fixture failed: {}".format(exc), "", 0)

    # (7) base leg absent -> could-not-evaluate
    missing = os.path.join(scratch, "no-base")
    os.makedirs(missing, exist_ok=True)
    rc, out, err = _run_cli(["--repo", missing, "--round", "74", "--tip", "master",
                             "--base-tool", os.path.join(missing, "absent.py")])
    _arm(outcomes, "base-absent", rc, out, err, 2, must_err=["CouldNotEvaluate"])

    # (8) unreadable record -> could-not-evaluate
    try:
        nr = r73._Fixture(scratch, "no-record")
        fx_commit(nr, "base")
        nr.write("plans/round-74-claims.md", "# kama round 74 — frozen claims\n\nfixture\n")
        fx_commit(nr, "plan only")
        rc, out, err = _run_cli(["--repo", nr.path, "--round", "74", "--tip", "master"])
        _arm(outcomes, "record-missing", rc, out, err, 2, must_err=["CouldNotEvaluate"])
    except Exception as exc:
        _arm(outcomes, "record-missing", 1, "fixture failed: {}".format(exc), "", 0)

    # (9) CLI misuse -> could-not-evaluate
    rc, out, err = _run_cli([])
    _arm(outcomes, "cli-misuse", rc, out, err, 2, must_err=["usage:"])


def _header_rev_v2_case(blob):
    """Case-SENSITIVE header parse — the mutant the seam arm must be able to fail."""
    window = blob.decode("utf-8", "replace").splitlines()[:HEADER_WINDOW]
    revs = []
    for line in window:
        for match in re.finditer(r"(?:^|[^\w-])(?:#\s*)?(?:tip|rev)=([0-9a-f]{40})(?![0-9a-f])", line):
            revs.append(match.group(1))
    if not revs:
        return None, "no lower-case tip=/rev= header"
    return revs[0], ""


def fx_commit(fx, msg):
    fx.git("add", "-A")
    fx.git("commit", "-q", "-m", msg)
    return fx.git("rev-parse", "HEAD").stdout.strip()


def _run_cli(argv):
    proc = subprocess.run([sys.executable, os.path.abspath(__file__)] + argv,
                          capture_output=True, text=True, timeout=TIMEOUT)
    return proc.returncode, proc.stdout, proc.stderr


def run_selftest(args):
    scratch = tempfile.mkdtemp(prefix="receipt-claim-v2-selftest-",
                               dir=args.work or tempfile.gettempdir())
    outcomes = []
    try:
        _selftest_arms(scratch, outcomes)
    finally:
        pass
    passed = sum(1 for _, ok, _ in outcomes if ok)
    failed = len(outcomes) - passed
    for name, ok, detail in outcomes:
        print("RECEIPT_CLAIM_V2_ARM {} {} {}".format(name, "ok" if ok else "FAIL", detail))
    print("RECEIPT_CLAIM_V2_SELFTEST pass={} fail={}".format(passed, failed))
    if not args.keep:
        import shutil
        shutil.rmtree(scratch, ignore_errors=True)
    return 0 if failed == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--round", type=int, required=False)
    ap.add_argument("--tip", default="master")
    ap.add_argument("--base-tool", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work", default=None)
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest(args)
    if args.round is None:
        print("usage: round74-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>")
        return 2

    try:
        result = audit(args.repo, args.tip, args.round, args.base_tool)
    except CouldNotEvaluate as exc:
        print("RECEIPT_CLAIM_V2 CouldNotEvaluate: {}".format(exc))
        return 2
    except r73.CouldNotEvaluate as exc:
        print("RECEIPT_CLAIM_V2 CouldNotEvaluate: {}".format(exc))
        return 2

    for line in result["base_finding_lines"]:
        print(line)
    for finding in result["claim_findings"]:
        print(claim_finding_line(finding))
    print(result["line"])
    if args.json:
        doc = dict(result)
        doc.pop("line", None)
        print(json.dumps(doc, indent=1, sort_keys=True))
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
