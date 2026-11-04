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
`tools/round73-receipt-claim-binding.py` is loaded only for its record readers,
citation resolver and base runner — neither frozen file is ever edited.

    RECEIPT_CLAIM_V2 round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s>
        stale=<t> claims=<k> unbound_claims=<j> bound_revisions=<r>

Exit: 0 clean (base green, no claim finding); 1 findings; 2 could-not-evaluate
(base tool absent/exit 2, self-record unreadable, CLI misuse). A scored run
never exits 2 for a finding.

Finding kinds (the freeze enumerates the kinds without boundary rules — the
round-74 critic seat routed this as under-specification defect F2b; the lane
fixes the boundaries here, on the frozen fixture bytes, disclosed in the
report and lesson):
- `wrapped-claim` — no single line carries both a tip token and a citation,
  and the nearest token line and citation line are SEPARATED BY CONTINUATION
  LINES (line distance >= 2): the claim text is wrapped across a multi-line
  span (the frozen `c2_wrapped` fixture: citation line 1, token line 3).
- `offset-claim` — no single line carries both, and the nearest token line
  and citation line are ADJACENT (line distance == 1; the frozen `c2_offset`
  fixture: token line 1, citation line 2).
- `stale-claim` — token and citation share one line and the cited receipt's
  header names another revision (the inherited round-73 shape; the frozen
  predicate enumerates the three NEW arm kinds, and this inherited kind keeps
  its round-73 name — disclosed in the round-74 report and lesson).
- `stale-revision` — the paragraph names an explicit 40-hex revision and a
  cited receipt's header differs (case-insensitively).

Revision mentions bind case-insensitively: git object names are hex, and an
honest record may name a receipt's revision in any hex case (the frozen
`c2_mixed_honest` fixture names the fixture receipt's own commit in upper
case). Receipt headers are parsed with a case-insensitive `tip=`/`rev=` key
and hex; conflicting headers inside the first five lines stay a finding
source (`unbound`), never a crash.

The `blob_reader` parameter on the claim pass exists so the selftest can
inject receipt bytes the way the byte-frozen r73 module already does
(`_claim_pass(..., blob_reader=...)`): the selftest's seam arm injects a
receipt whose header names the tip in upper-case hex — a pristine module
binds it; a case-sensitive mutant flags it (MT01Mutants' surviving mutant
`c2_p2l_case_hex`, which no committable fixture can carry).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
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


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r73 = _load_module("round73_receipt_claim_binding",
                   os.path.join(HERE, "round73-receipt-claim-binding.py"))
base_mod = r73._load_base(r73._base_tool_path(LANE, None))


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


def _claim_kind(text, plines, base):
    """wrapped-claim / offset-claim / same-line for a tip-claim paragraph.

    Boundaries (F2b resolution, see module docstring): same-line when one line
    carries both a tip token and a citation; otherwise the nearest token line
    and citation line decide — distance 1 is offset-claim, >= 2 is
    wrapped-claim.
    """
    token_idx = [i for i, line in enumerate(plines)
                 if any(tok in line.lower() for tok in TIP_CLAIM_TOKENS)]
    cite_idx = [i for i, line in enumerate(plines) if base.TOKEN_RE.search(line)]
    for i in token_idx:
        for j in cite_idx:
            if i == j:
                return "same-line"
    distance = min(abs(i - j) for i in token_idx for j in cite_idx)
    return "offset-claim" if distance == 1 else "wrapped-claim"


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
                bad = []
                for path in cited:
                    rev, _problem = headers[path]
                    if rev is None or rev != tip_sha:
                        bad.append(path)
                if bad:
                    kind = _claim_kind(text, plines, base)
                    if kind == "same-line":
                        kind = "stale-claim"
                    unbound_claims += 1
                    for path in bad:
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


def _arm(outcomes, name, ok, detail):
    outcomes.append((name, bool(ok), detail))


def _record(fixture, round_no, scorecard_body, lesson_body="No citation here.\n"):
    fixture.write("corpus/lessons/round-{}.md".format(round_no),
                  "# Round {} lesson\n\n{}".format(round_no, lesson_body))
    fixture.write("SCORECARD.md",
                  "# fixture scorecard\n\n## Round {} — fixture\n\n{}\n".format(
                      round_no, scorecard_body))


def _selftest_arms(scratch, outcomes):
    base = base_mod
    Fixture = base._Fixture

    # (1) predicate arm: one line, both output shapes, byte-equal to the plan
    one_line = "\n" not in PREDICATE
    shape = ("RECEIPT_CLAIM_V2 round=<N> cited=<c>" in PREDICATE
             and "RECEIPT_CLAIM_V2_FINDING <wrapped-claim|offset-claim|stale-revision>" in PREDICATE)
    plan_path = os.path.join(LANE, PLAN_NAME)
    plan_state = "absent"
    if os.path.isfile(plan_path):
        with open(plan_path, encoding="utf-8") as handle:
            plan_state = "True" if _plan_c2_predicate(handle.read()) == PREDICATE else "False"
    _arm(outcomes, "predicate", one_line and shape and plan_state != "False",
         "one_line={} shape={} plan={}".format(one_line, shape, plan_state))

    # (2) the plan blob at master carries the same C2 sentence
    blob = base._blob(LANE, base._commit_sha(LANE, "master"), PLAN_NAME)
    blob_state = "absent"
    if blob is not None:
        blob_state = "True" if _plan_c2_predicate(blob.decode("utf-8", "replace")) == PREDICATE else "False"
    _arm(outcomes, "predicate-at-tip", blob_state == "True",
         "plan_at_master={}".format(blob_state))

    # (3) committed-builder fixtures replay: the frozen kill and clean arms
    builder = os.path.join(LANE, ".ufo/waves/round-74/controls/build-survivors.py")
    work = os.path.join(scratch, "committed-fixtures")
    meta_path = os.path.join(work, "fixtures-meta.json")
    if os.path.isfile(builder):
        env = dict(os.environ)
        subprocess.run([sys.executable, builder, "--work", work, "--meta", meta_path],
                       check=True, capture_output=True, text=True, env=env)
        meta = json.loads(open(meta_path).read())
        want = {
            "c2_wrapped": (1, "wrapped-claim"),
            "c2_offset": (1, "offset-claim"),
            "c2_mixed_honest": (0, None),
            "c2_clean_realizable": (0, None),
        }
        all_ok = True
        detail = []
        for name, (want_rc, kind) in want.items():
            case = meta[name]
            res = audit(case["fixture"], "master", 74)
            ok = res["exit"] == want_rc
            if kind:
                ok = ok and any(f["kind"] == kind for f in res["claim_findings"])
            if name == "c2_mixed_honest":
                ok = ok and res["bound_revisions"] == 1
            all_ok = all_ok and ok
            detail.append("{} rc={} kinds={} bound_revisions={}".format(
                name, res["exit"], sorted({f["kind"] for f in res["claim_findings"]}),
                res["bound_revisions"]))
        _arm(outcomes, "committed-fixtures", all_ok, " | ".join(detail))
    else:
        _arm(outcomes, "committed-fixtures", False, "builder absent")

    # (4) blob_reader seam (MT01Mutants' surviving-mutant arm): a receipt whose
    # header names the TIP in upper-case hex binds under the pristine pass; a
    # case-sensitive header parse flags it — the arm is load-bearing. The blob
    # names the RECORD commit (a hash fixed point on committed bytes — the very
    # reason this seam exists), so the on-disk receipt is a placeholder and the
    # injected reader supplies the naming bytes.
    try:
        seam = Fixture(scratch, "seam")
        seam.write("tools/counter.py", "# counter\n")
        seam.commit("base")
        seam.write(".ufo/waves/round-74/measured/seam.out",
                   "# placeholder; the graded blob is injected\n")
        _record(seam, 74,
                "C2 seam: measured `.ufo/waves/round-74/measured/seam.out` at the tip.\n")
        seam.write("plans/round-74-claims.md",
                   "# kama round 74 — frozen claims\n\nfixture\n")
        tip = seam.commit("record")
        blob = "# REV={}\nverdict: green\n".format(tip.upper()).encode("ascii")
        pristine = _claim_pass_v2(
            seam.path, tip, 74, base,
            blob_reader=lambda path, _b=blob: _b if path.endswith("seam.out") else None)
        mutant_rev = _header_rev_v2_case_sensitive(blob)
        ok = (pristine["claims"] == 1 and pristine["unbound_claims"] == 0
              and mutant_rev[0] is None)
        _arm(outcomes, "blob-reader-seam", ok,
             "pristine claims={} unbound={} mutant_case_sensitive_rev={}".format(
                 pristine["claims"], pristine["unbound_claims"], mutant_rev[0]))
    except Exception as exc:
        _arm(outcomes, "blob-reader-seam", False, "seam fixture failed: {}".format(exc))

    # (5) stale-revision arm: named explicit revision differs from the header
    try:
        sr = Fixture(scratch, "stale-rev")
        sr.write("tools/counter.py", "# counter\n")
        seed = sr.commit("base")
        sr.write(".ufo/waves/round-74/measured/sr.out", "# rev={}\nverdict\n".format(seed))
        sr.commit("receipt")
        _record(sr, 74,
                "C2: re-run at revision {} naming `.ufo/waves/round-74/measured/sr.out`.\n"
                .format("a" * 40))
        sr.write("plans/round-74-claims.md", "# kama round 74 — frozen claims\n\nfixture\n")
        tip = sr.commit("record names a wrong revision")
        res = audit(sr.path, tip, 74)
        ok = res["exit"] == 1 and any(f["kind"] == "stale-revision"
                                      for f in res["claim_findings"])
        _arm(outcomes, "stale-revision", ok,
             "exit={} kinds={}".format(res["exit"], sorted({f["kind"] for f in res["claim_findings"]})))
    except Exception as exc:
        _arm(outcomes, "stale-revision", False, "fixture failed: {}".format(exc))

    # (6) same-line stale keeps the inherited kind
    try:
        sl = Fixture(scratch, "same-line")
        sl.write("tools/counter.py", "# counter\n")
        seed = sl.commit("base")
        sl.write(".ufo/waves/round-74/measured/sl.out", "# rev={}\nverdict\n".format(seed))
        sl.commit("receipt")
        _record(sl, 74,
                "C2: `.ufo/waves/round-74/measured/sl.out` measured at the tip.\n")
        sl.write("plans/round-74-claims.md", "# kama round 74 — frozen claims\n\nfixture\n")
        tip = sl.commit("record")
        res = audit(sl.path, tip, 74)
        ok = res["exit"] == 1 and any(f["kind"] == "stale-claim"
                                      for f in res["claim_findings"])
        _arm(outcomes, "same-line-stale-claim", ok,
             "exit={} kinds={}".format(res["exit"], sorted({f["kind"] for f in res["claim_findings"]})))
    except Exception as exc:
        _arm(outcomes, "same-line-stale-claim", False, "fixture failed: {}".format(exc))

    # (7) base leg absent -> could-not-evaluate
    missing = os.path.join(scratch, "no-base")
    os.makedirs(missing, exist_ok=True)
    rc, out, err = _run_cli(["--repo", missing, "--round", "74", "--tip", "master",
                             "--base-tool", os.path.join(missing, "absent.py")])
    _arm(outcomes, "base-absent", rc == 2 and "CouldNotEvaluate" in (out + err),
         "rc={}".format(rc))

    # (8) unreadable record -> could-not-evaluate
    try:
        nr = Fixture(scratch, "no-record")
        nr.write("tools/counter.py", "# counter\n")
        nr.commit("base")
        nr.write("plans/round-74-claims.md", "# kama round 74 — frozen claims\n\nfixture\n")
        tip = nr.commit("plan only")
        rc, out, err = _run_cli(["--repo", nr.path, "--round", "74", "--tip", tip])
        _arm(outcomes, "record-missing", rc == 2 and "CouldNotEvaluate" in (out + err),
             "rc={}".format(rc))
    except Exception as exc:
        _arm(outcomes, "record-missing", False, "fixture failed: {}".format(exc))

    # (9) CLI misuse -> could-not-evaluate
    proc = subprocess.run([sys.executable, os.path.abspath(__file__)],
                          capture_output=True, text=True, timeout=TIMEOUT)
    _arm(outcomes, "cli-misuse", proc.returncode == 2 and "usage:" in proc.stderr,
         "rc={}".format(proc.returncode))

    # (10) conflicting headers remain unbound, including in the v2 header pass.
    try:
        ch = Fixture(scratch, "conflicting-headers")
        ch.write("tools/counter.py", "# counter\n")
        seed = ch.commit("base")
        receipt = ".ufo/waves/round-74/measured/conflict.out"
        header = "# rev={}\n# rev={}\n".format(seed, "a" * 40)
        ch.write(receipt, header)
        ch.commit("receipt")
        _record(ch, 74, "C2: measured at revision {} naming `{}`.\n".format(seed, receipt))
        ch.write("plans/round-74-claims.md", "# kama round 74 — frozen claims\n\nfixture\n")
        tip = ch.commit("record")
        res = audit(ch.path, tip, 74)
        rev, problem = _header_rev_v2(header.encode("ascii"))
        ok = (res["exit"] == 1 and res["unbound"] == 1
              and any("RECEIPT_TIP_FINDING unbound " in line
                      for line in res["base_finding_lines"])
              and rev is None and "conflicting header revisions" in problem)
        _arm(outcomes, "conflicting-headers", ok,
             "exit={} unbound={} header_rev={} problem={}".format(
                 res["exit"], res["unbound"], rev, problem))
    except Exception as exc:
        _arm(outcomes, "conflicting-headers", False, "fixture failed: {}".format(exc))

    # (11) a revision on the fifth header line binds in both grading passes.
    try:
        hw = Fixture(scratch, "header-window-fifth-line")
        hw.write("tools/counter.py", "# counter\n")
        hw.write("plans/round-74-claims.md", "# kama round 74 — frozen claims\n\nfixture\n")
        seed = hw.commit("base")
        receipt = ".ufo/waves/round-74/measured/fifth.out"
        hw.write(receipt, "# receipt\n# counter\n# run\n# header\n# rev={}\n".format(seed))
        hw.commit("receipt")
        _record(hw, 74, "C2: measured at revision {} naming `{}`.\n".format(seed, receipt))
        tip = hw.commit("record")
        res = audit(hw.path, tip, 74)
        _arm(outcomes, "header-window-fifth-line",
             res["exit"] == 0 and res["bound_revisions"] == 1,
             "exit={} bound_revisions={}".format(res["exit"], res["bound_revisions"]))
    except Exception as exc:
        _arm(outcomes, "header-window-fifth-line", False, "fixture failed: {}".format(exc))


def _header_rev_v2_case_sensitive(blob):
    """Case-SENSITIVE header parse — the mutant the seam arm must be able to fail."""
    window = blob.decode("utf-8", "replace").splitlines()[:HEADER_WINDOW]
    revs = []
    for line in window:
        for match in re.finditer(r"(?:^|[^\w-])(?:#\s*)?(?:tip|rev)=([0-9a-f]{40})(?![0-9a-f])", line):
            revs.append(match.group(1))
    if not revs:
        return None, "no lower-case tip=/rev= header"
    return revs[0], ""


def _run_cli(argv):
    proc = subprocess.run([sys.executable, os.path.abspath(__file__)] + argv,
                          capture_output=True, text=True, timeout=TIMEOUT)
    return proc.returncode, proc.stdout, proc.stderr


def run_selftest(args):
    work = args.work or os.environ.get("TMPDIR") or tempfile.gettempdir()
    os.makedirs(work, exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="receipt-claim-v2-selftest-", dir=work)
    outcomes = []
    try:
        _selftest_arms(scratch, outcomes)
    finally:
        if not args.keep:
            shutil.rmtree(scratch, ignore_errors=True)
    passed = sum(1 for _, ok, _ in outcomes if ok)
    failed = len(outcomes) - passed
    for name, ok, detail in outcomes:
        print("RECEIPT_CLAIM_V2_ARM {} {} {}".format(name, "ok" if ok else "FAIL", detail))
    print("RECEIPT_CLAIM_V2_SELFTEST pass={} fail={}".format(passed, failed))
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
        print("usage: round74-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>",
              file=sys.stderr)
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
