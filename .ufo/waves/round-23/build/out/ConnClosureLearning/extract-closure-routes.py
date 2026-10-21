#!/usr/bin/env python3
"""Extract routed feedback / limits from kama closures r20-r22 (read-only).

Reads the fleet MANIFEST.json, asserts every quoted clause is a verbatim
substring of the named field, and writes a deterministic JSON route table.
No network, no writes outside the caller-supplied output path.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = Path("/home/vgpnk/Projects/shokunin/MANIFEST.json")
INDICES = {20: 397, 21: 406, 22: 418}


def resolve(doc, path):
    """Resolve 'rounds[397].notes' against the manifest document."""
    cur = doc
    for match in re.finditer(r"([^.\[\]]+)|\[(\d+)\]", path):
        name, index = match.group(1), match.group(2)
        cur = cur[int(index)] if index is not None else cur[name]
    return cur


# (id, manifest path, verbatim quote or None, exact value or None,
#  disposition, round-23 action)
ITEMS = [
    # ---------------- round 20 (rounds[397]) ----------------
    ("R20-D1", "rounds[397].notes",
     "Defects (status-neutral, routed to kama r21): (D1) report :7 cites full hash "
     "0957ce619789d13d894ef21bc863486bcb35b56c which resolves nowhere; actual commit is "
     "0957ce619789d13bb5779606078fa1498114d2c7 (correct at :10)", None,
     "closed-in-r22",
     "Do not reopen. The splice and the four omissions are corrected by five rows in "
     "registry/report-landing-errata.tsv (round 20). r23's ledger must keep "
     "corrected9/uncorrected0, errata invalid0/unmatched0."),
    ("R20-D2", "rounds[397].notes",
     "Landed changes lists 5 commits but omits round commits 33a6777, 0957ce6, 92b1462, "
     "846e366", None, "closed-in-r22",
     "Same closure as R20-D1 (four landed-omitted errata rows). r23 must not present "
     "these as open defects."),
    ("R20-LIMITS", "rounds[397].notes",
     "Honest limits, not scope shrink: v3-all-scalars 12 test.* values not individually "
     "compared (never part of the declared selected-key claim); full 42-run R18 survivor "
     "measure not rerun (routed R18 comparison, outside C1/C2); timeout reason precision "
     "unclaimed (2 diagnostic mutation survivors, class boundary intact).", None,
     "carry-explicitly",
     "Restate as still-unclaimed unless r23 measures them; none is inside the r23 "
     "repo-local-git fault grid."),
    ("R20-L0", "rounds[397].notes",
     "L0 kama|round-17 llama archive question still open.", None,
     "carry-operator-owned",
     "Carry as open/operator-owned (r21 also lists round17 retained-archive L0 as "
     "operator-owned)."),
    ("R20-CENSUS", "rounds[397].verification.rechecks",
     "error-verdict-census.py --arm frozen exit1 cells15 frozen_misclassified6 "
     "witness/red-vector mismatches0 unrun[]; --arm current exit0 "
     "current_misclassified0 unrun[]", None, "invariant",
     "The r23 no-harm recipe (which includes the error census) must keep current "
     "misclassified0/unrun0 on the same 15 cells; frozen stays exit1 with 6."),
    ("R20-SCOPE", "rounds[397].notes",
     "C1 calibration improved 7->7 at the explicitly named 15-cell scope (narrowed from "
     "universal wording before measurement", None, "scope-precedent",
     "r23 must name its finite fault-grid cells and state scalar 7->7 explicitly; "
     "improved verdict != scalar movement."),
    ("R20-RECEIPTS", "rounds[397].verification.rechecks",
     "Committed runs/9add96e4/commands.json: 21 commands, all 21 stdout sha256 and .exit "
     "files match, exit==expected 21/21.", None, "invariant",
     "r23 measurement receipts (stdout/stderr/.exit, command count, expected exits) "
     "must reconcile the same way."),

    # ---------------- round 21 (rounds[406]) ----------------
    ("R21-D4", "rounds[406].notes",
     "late C1EnvSentinel identifies unintegrated repository-local Git-config/history "
     "trust hardening and UTF-8/error/top-level handling; do not use audit on untrusted "
     "repos until hardened", None, "address-now",
     "This is the declared r23 C1. Address only the measured channels (replace refs, "
     "promisor lazy fetch, i18n.logOutputEncoding, log.follow, strict decode). Explicitly "
     "carry: the audit is still not authorized on untrusted repositories beyond the "
     "measured grid."),
    ("R21-D1", "rounds[406].notes",
     "Routed status-neutral defects to kama r22:(D1)append final7054dba1/33-command "
     "results to SCORECARD,whose round21 section still contains earlier "
     "b76727f3/28-command counts", None, "closed-in-r22",
     "r22 appended the correction (SCORECARD.md:1056). r23 must append, never rewrite, "
     "and any r23 SCORECARD row must cite its own final measured commit/count."),
    ("R21-D2", "rounds[406].notes",
     "(D2)CORPUS v1 requires correction rows with teaches supersedes S0NN,whereas "
     "SOURCES253-269 supplies prose cell supersessions without new registry rows; "
     "corrections are marked,so not left-false knowledge", None, "closed-in-r22",
     "r22 reports nine proper source-correction rows (report:24-27). r23 must preserve "
     "the rows and keep sources-census missing0."),
    ("R21-D3", "rounds[406].notes",
     "(D3)append accurate two-death accounting and late66-report falsify total", None,
     "closed-in-r22",
     "Accounting precedent only. r23 must report its own deaths/resumes accurately; "
     "r21 also records 'filed report's still-running description of build seat is stale'."),
    ("R21-SELFTEST-DEBT", "rounds[406].notes",
     "Late C1SelftestReview's vacuous uncommitted-now fallback and crash-only GIT_DIR "
     "assertion remain test debt,not failure of committed11-report result.", None,
     "open-test-debt",
     "r23 edits the same selftest surface (git_env/git and added cases). Fix both cases "
     "or carry them explicitly; report frozen 50/50 and the new total N/0 separately "
     "(a larger N is not 'unchanged 50/50')."),
    ("R21-C2-CLOSED", "rounds[406].notes",
     "Late C2DigestSentinel was against oldera6617149; finalcode adds tree-membership "
     "cross-check,hwcaps-any-type refusal,link-target member check,nonnull digest and "
     "bad-key/orphan validation,covering its corresponding issues.", None, "closed",
     "No r23 action; r23 does not touch the C2 install-digest surface."),
    ("R21-DEBT", "rounds[406].notes",
     "Remaining prelaunch-snapshot race,41-hop gate bound,JSON duplicate-key/Unicode "
     "edge cases and overbroad any-str-map injectivity docstring are routed debt outside "
     "static flat-tree count; no execution-authentication claim admitted.", None,
     "carry-explicitly",
     "Carry as routed debt. Do not let the JSON/Unicode item be silently absorbed by the "
     "strict-decode change, and do not claim execution authentication."),
    ("R21-L0", "rounds[406].notes",
     "Existing round16 fixture-ratification and round17 retained-archive L0 remain "
     "operator-owned.", None, "carry-operator-owned",
     "Carry both L0 items as operator-owned; do not close them in-lane."),
    ("R21-LEDGER", "rounds[406].verification.rechecks",
     "C1 --selftest:36 failed0 including ambiguity and committed-bytes cases; "
     "--rounds10-20 --no-errata --json exit1:11 reports,9 defects (8 omissions+1 "
     "unresolved full hash),42 required/4 post-report commits; ledger exit0 "
     "corrected9/uncorrected0, invalid0/unmatched0.", None, "invariant",
     "Reproduce both modes at the r23 head: --no-errata still exit1 with the historical "
     "defect count, errata mode exit0 corrected9/uncorrected0 invalid0/unmatched0. "
     "Selftest counts are round-specific (36 then, 50 at 4fe9339; verified this seat)."),
    ("R21-NOHARM", "rounds[406].verification.rechecks",
     "error census frozen_misclassified6/current0,witness/red mismatches0,unrun[]", None,
     "invariant",
     "Keep the error census and witness/red-vector mismatch0/unrun[] in the r23 no-harm "
     "recipe."),
    ("R21-SOURCES", "rounds[406].verification.rechecks",
     "SOURCES append-only9 appended,0 violations; validate0 with8 W04 duplicate-URL "
     "warnings,census74 rows/missing0.", None, "invariant",
     "SOURCES stays append-only; validate stays exit0 with W04 warnings only; census "
     "missing0 (row counts grow each round and must be re-derived, not copied)."),
    ("R21-RECEIPTS", "rounds[406].verification.rechecks",
     "Committed original33 stdout hashes,33 stderr hashes,33 .exit files and33 expected "
     "exits all match commands.json", None, "invariant",
     "Receipt reconciliation pattern for r23 measurement."),
    ("R21-CATFILE", "rounds[406].verification.spotcheck",
     "-e says zero for valid object and nonzero for invalid format, whereas BATCH OUTPUT "
     "explicitly specifies missing and ambiguous records.", None, "invariant-knowledge",
     "Keep cat-file --batch-check as the missing/ambiguous oracle; --no-lazy-fetch is "
     "designed to pair with probing (git(1) names cat-file -e), but -e must not replace "
     "the batch distinction."),

    # ---------------- round 22 (rounds[418]) ----------------
    ("R22-SCOPE", "rounds[418].claims.C1.scope",
     "Narrow verified calibration improvement: install_tree I/O faults now refuse with "
     "stage/member/cause instead of null/partial identities, and registered Registry "
     "source-URL occurrences are no longer counted as owned commit citations. Not a new "
     "serving capability; scalar unchanged.", None, "scope-precedent",
     "Mirror the form: name the before/after components, the controls, and the "
     "non-claim ('not general untrusted-repository hardening; scalar unchanged unless "
     "earned')."),
    ("R22-SCALAR", "rounds[418].claims.C1.scalar_before", None, 7, "invariant",
     "Calibration enters r23 at 7 (lowest non-retired); the claim Context expects a "
     "narrow 7->7 component improvement, not an invented scalar increase."),
    ("R22-SCALAR-AFTER", "rounds[418].claims.C1.scalar_after", None, 7, "invariant",
     "State the after scalar explicitly; do not let 'improved' imply a raise."),
    ("R22-COMPONENTS", "rounds[418].claims.C1.components.helper_explicit_refusals",
     None, {"before": 0, "after": 18, "of": 18}, "scope-precedent",
     "Use the same before/after/of component shape for r23 (frozen vs current cells)."),
    ("R22-LEDGER", "rounds[418].verification.rechecks",
     "report-landing-audit.py --rounds 10-21 --report 22=<fleet report> --fleet-repo "
     "<fleet> --json exit0, stderr empty: status clean, 13 reports, defects9/corrected9, "
     "uncorrected0, errata invalid/unmatched0, required54, post-report5; round22 0 "
     "defects, required5, source_url_hashes [704366d7]", None, "invariant",
     "At the r23 head run the same shape: --rounds 10-22 --report 23=<fleet report>, "
     "expect clean, defects9/corrected9, uncorrected0, errata invalid0/unmatched0; "
     "re-derive required/post-report and the new round's source_url_hashes list."),
    ("R22-SOURCES", "rounds[418].verification.rechecks",
     "sources-census validate kama exit0 (only W04 duplicate-URL warnings); census rows88 "
     "A83/B2/C3 mined72/queued8/rejected8 missing0", None, "invariant",
     "r23 re-derives rows/tiers/statuses; missing0 and validate exit0 are the "
     "invariants, 88 is not."),
    ("R22-NOHARM", "rounds[418].verification.axis_harm",
     "None observed: recipe no-harm checks (links grid, receipt gate/mutations, legacy "
     "receipts, GGUF, citation, error census, snapshot, prelaunch refusal, historical "
     "audit ledger, sources-unchanged) all at expected exits at HEAD; frontier rows "
     "unchanged (0 advanced) as disclosed.", None, "invariant",
     "Run/retain this complete no-harm list. Disclose frontier movement honestly: r22 "
     "recorded 0 advanced and named D4 hardening as a remaining frontier item; r23 must "
     "not claim a row advance without a named row."),
    ("R22-CONFORMANCE", "rounds[418].verification.conformance",
     "Report committed at fleet 36e37a3b (ancestor of fleet HEAD) with Work performed, "
     "Landed changes, Before→after, Sources & frontier, Trend verdicts, SHONEN, "
     "Swarm/limits, Final report audit sections.", None, "invariant",
     "r23 report keeps these sections in order; cited commits must be ancestors of HEAD; "
     "lane HEAD must equal origin/master for the measured state."),
    ("R22-PORCELAIN", "rounds[418].verification.conformance",
     "Lane HEAD = origin/master = 4fe9339f after fetch; lane porcelain empty.", None,
     "invariant-conformance",
     "At r22 closure the lane was clean at 4fe9339. This seat now observes an uncommitted "
     "worktree change to tools/report-landing-audit.py (see report contradictions); the "
     "measured 'current' must be a committed, pinned state, not an anonymous worktree."),
    ("R22-SPOTCHECK", "rounds[418].verification.spotcheck",
     "'If the file cannot be opened, an OSError is raised' — agree", None,
     "invariant-knowledge",
     "Do not conflate UnicodeDecodeError (a ValueError, not OSError) with open failures in "
     "r23 prose; the audit's typed decode refusal is a separate path."),
    ("R22-DISCERNMENT", "rounds[418].trends.discernment", None, "improved",
     "invariant",
     "Discernment improved narrowly; r23 must not regress it by admitting unmeasured "
     "channels (showSignature/gpg.program, mailmap, includeIf, fsmonitor/hooks, "
     "safe.directory, notes, object-format) as hardened."),
    ("R22-VERDICTS", "rounds[418].verdicts", None,
     {"calibration": "improved", "operability": "unchanged", "freshness": "unchanged",
      "depth": "unchanged", "coverage": "unchanged", "adjacency": "unchanged"},
     "invariant-axis-budget",
     "Operability is 8 and unchanged; r23's C1 is calibration. Claim operability only if "
     "measured this round."),
    ("R22-SWARM", "rounds[418].verification.swarm",
     "round total 74 seats, 22 original deaths, 57 retained reports", None,
     "operational-precedent",
     "Report original deaths, resumes and retained reports separately; do not describe "
     "live seats as finished (r21 routed that exact stale-description defect)."),
    ("R22-TOOLS", "rounds[418].verification.tools_installed", None, "none",
     "operational",
     "Record any install/update in the r23 report; this seat installed nothing."),
]


def main(argv):
    out = Path(argv[1])
    raw = MANIFEST.read_bytes()
    doc = json.loads(raw)
    digest = hashlib.sha256(raw).hexdigest()
    entries = []
    for rnd, idx in sorted(INDICES.items()):
        e = doc["rounds"][idx]
        assert e.get("lane") == "kama", (idx, e.get("lane"))
        assert e.get("round") == rnd, (idx, e.get("round"))
        entries.append({
            "index": idx,
            "round": e["round"],
            "lane": e["lane"],
            "type": e.get("type"),
            "date": e.get("date"),
            "admitted": e.get("admitted"),
            "verdict": e.get("verdict"),
            "commit": e.get("commit"),
        })
    items = []
    for item_id, path, quote, value, disposition, action in ITEMS:
        field = resolve(doc, path)
        if quote is not None:
            assert isinstance(field, str), (item_id, path, type(field))
            assert quote in field, f"{item_id}: quote not verbatim in {path}"
            payload = {"quote": quote}
        else:
            assert field == value, (item_id, path, field, value)
            payload = {"value": value}
        items.append({
            "id": item_id,
            "manifest_path": path,
            "disposition": disposition,
            "round23_action": action,
            **payload,
        })
    counts = {}
    for item in items:
        counts[item["disposition"]] = counts.get(item["disposition"], 0) + 1
    result = {
        "schema": "kama-closure-routes-v1",
        "purpose": "routed feedback/disagreement/limit carried from kama closures "
                   "r20-r22 into kama round-23",
        "access_date": "2026-10-21",
        "manifest": {"path": str(MANIFEST), "sha256": digest,
                     "bytes": len(raw), "rounds": len(doc["rounds"])},
        "lane_base": "kama-shokunin@4fe9339f8fc3a4a4a479d9c938a850da12f1124d",
        "entries": entries,
        "items": items,
        "counts": dict(sorted(counts.items())),
        "items_total": len(items),
    }
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"wrote {out} items={len(items)} counts={result['counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
