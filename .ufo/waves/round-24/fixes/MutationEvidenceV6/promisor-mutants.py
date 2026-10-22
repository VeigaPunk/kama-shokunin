#!/usr/bin/env python3
"""Round-24 promisor mutation-sensitivity runner.

It mutates the candidate auditor (tools/report-landing-audit.py, or the path
given by --current) one element at a time and re-runs the promisor grid
(tests/report-audit/promisor-grid.py, or --grid) on the mutant, to show
which promisor safeguards of the candidate are load-bearing.

A mutation is one of

  replace  one literal source replacement (the old text must occur exactly
           once in the candidate),
  regex   one regular-expression replacement (the pattern must match
           exactly once),
  insert  one self-contained snippet inserted at a literal anchor (the
           anchor must occur exactly once); used where the candidate's
           spelling is not known in advance.

Frozen mutant inventory. The inventory follows the round-24 L1 policy
decision (oracle-amendment-1.json plus the original local-object contract
in the base auditor, lines 12-19): promisor metadata is irrelevant to the
verdict, objects the audit actually reads must be available or the audit is
could-not-evaluate, a locally unresolved citation that names unavailable
referenced local content is could-not-evaluate rather than proved absent,
and every other absent citation keeps the ordinary failed finding plus
errata handling.

  PM01 blanket promisor-metadata refusal  over-refusal: a complete
       promisor-marked repository must keep the verdict of its full-clone
       twin; the mutant refuses on metadata alone (exit 2).
  PM02 blanket unknown refusal            the unknown rule is applied to
       every absent citation, not only to one that names unavailable
       referenced content: the historical errata-marked clone (an absent
       hash corrected by errata) must stay an ordinary failed finding, and
       the mutant turns it into could-not-evaluate.
  PM03 skip required-object availability   objects the audit actually
       reads must be available: a missing required commit/tree/blob/report
       object is could-not-evaluate (exit 2), never a clean or failed
       verdict.
  PM04 accept an unavailable referenced    a locally unresolved citation
       object                                    that names unavailable
       referenced local content must be could-not-evaluate rather than
       proved absent; the mutant accepts it as absent.
  PM05 ignore second-repo resolution       a citation missing in one
       audited repository but present in the other audited repository is
       resolvable; the mutant consults the first repository only.
  PM06 swallow an actual read error        a failing read of the object the
       audit needs is could-not-evaluate; the mutant swallows the failure
       and guesses a value, turning an unavailable object into a verdict.
  PM07 full --all missing gate             the store-wide missing walk
       starts from every present root; the mutant adds --all to that root
       set, so a broken unselected REF target outside the present roots
       enters the diagnosis. It does NOT broaden the name-hiding walk,
       which stays rooted at the pinned root only. On the finite 47 it may
       survive; that is an observation, not a global-equivalence proof,
       and no kill is presumed.
  PM08 no-lazy-fetch review note            review-only and uncredited (the
       operator keeps it out of the executed inventory): the candidate's
       repository-reading wrappers carry --no-lazy-fetch, so a missing
       promisor object is not fetched through the promisor remote on the
       paths those wrappers read. No mutant is built for it, no grid
       invocation is made for it, and it is never credited with a kill;
       the claim is a manual reading of the candidate's isolation flags,
       not a proof about every git call.
  PM09 peel the bare full-hash lookup      peer-proposed extension
       (MutationDesign-2, OracleLocalBlobType-2): the bare full-hash lookup
       must stay unpeeled, so a citation of a locally present blob resolves
       as found; peeling it to ^{commit} turns a present blob into a missing
       object.
  PM10 ignore the opaque non-leaf hole     when a citation is unresolved, a
       (round-24 supplement oracle)     missing tree or commit may conceal
                                      the dependency names, so the citation
                                      is unevaluable (exit 2); the mutant
                                      ignores that hole and reports an
                                      ordinary failed finding.
  PM11 any hole refuses                   no missing-object state may be an
       (round-24 supplement oracle)     unconditional audit precondition:
                                      an unrelated blob hole keeps the
                                      ordinary failed finding and an unused
                                      tree hole keeps the clean verdict; the
                                      mutant refuses on any hole.

Kill rule: a mutant is killed only when the grid reports a violated graded
row: a graded row with met == false, or a graded row whose twin_equal is
false. Every other outcome is could-not-evaluate and kills nothing:

  * the pristine candidate does not meet the grid (the grid exits
    non-zero): the whole run is could-not-evaluate, no mutant is
    attributed, no kill is credited;
  * the grid exits 2 (could not evaluate), reports a harness leak
    (arm.harness_leaks, a row with leaked or timed_out set) or times out;
  * the grid exits 1 but no violated graded row can be identified: the
    grid's verdict cannot be read, so the run is could-not-evaluate;
  * the mutation does not apply (no anchor, literal or pattern occurring
    exactly once) or the mutant does not compile.

Exit: 0 the inventory was fully evaluated (every mutant killed or
surviving, or review-only; the JSON document reports which); 2 could not
evaluate (any condition above). A kill is never an exit code of its own:
the JSON document carries the killed and the surviving mutants.

--list prints the frozen inventory, --anchors reports how often every
mutation pattern matches a candidate (and whether the mutant compiles),
and --selftest exercises the exit mappings on isolated stub fixtures.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

LANE = Path(__file__).resolve().parents[2]
AUDIT = LANE / "tools/report-landing-audit.py"
GRID = LANE / "tests/report-audit/promisor-grid.py"
# graded row kinds of the promisor grid: policy cells (the manifest's
# policy expectations) and control cells (the no-harm twins); "open" rows
# are reported, never graded.
GRADED_KINDS = ("policy", "control", "fault", "contract")
DEFAULT_GRID_TIMEOUT = 1800

# PM01 (fallback form, spelling-independent): a blanket refusal on promisor
# metadata. It patches the module's own git wrapper, so every
# promisor-marked repository is refused before any object is looked at.
PM01_INSERT = '''# --- PM01 mutation: blanket promisor-metadata refusal (over-refusal) ---
def _pm_promisor_metadata(repo):
    import subprocess as _sp
    try:
        listing = _sp.run(
            ["git", "-C", str(repo), "config", "--null", "--list"],
            capture_output=True, timeout=20).stdout.decode("utf-8", "replace")
    except Exception:
        return
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and value.strip().lower() in ("", "true", "yes", "on", "1")):
            raise EvalError(f"{repo}: partial clone ({key})")
    try:
        gp = _sp.run(
            ["git", "-C", str(repo), "rev-parse", "--git-path", "objects/pack"],
            capture_output=True, timeout=20).stdout.decode(
                "utf-8", "replace").strip()
    except Exception:
        return
    if not gp:
        return
    pack = Path(gp) if Path(gp).is_absolute() else Path(repo, gp)
    if pack.is_dir() and any(p.suffix == ".promisor"
                              and p.with_suffix(".pack").exists()
                              for p in pack.iterdir()):
        raise EvalError(f"{repo}: partial clone (promisor pack)")


def _pm_install_promisor_refusal():
    _original = globals()["git"]

    def _patched(repo, *args, **kw):
        _pm_promisor_metadata(repo)
        return _original(repo, *args, **kw)

    globals()["git"] = _patched


_pm_install_promisor_refusal()
# --- end PM01 mutation ---'''

# PM02 (blanket unknown refusal): every absent citation becomes
# could-not-evaluate, whether or not a promisor store makes its absence
# uncertain. Locally known states (found, ambiguous, wrongtype) keep their
# ordinary verdicts.
PM02_INSERT = '''# --- PM02 mutation: blanket unknown refusal (over-refusal) ---
def _pm_install_blanket_unknown():
    _original = globals()["lookup"]

    def _patched(stores, tokens, peel=""):
        status = _original(stores, tokens, peel)
        for token, state in status.items():
            if state not in ("found", "ambiguous", "wrongtype"):
                raise EvalError(
                    f"{token}: unknown: absence is uncertain (blanket refusal)")
        return status

    globals()["lookup"] = _patched


_pm_install_blanket_unknown()
# --- end PM02 mutation ---'''

# PM06 (swallowed actual read error): a failing read of the evidence the
# audit needs is turned into empty data instead of could-not-evaluate.
PM06_INSERT = '''# --- PM06 mutation: an actual read error is swallowed ---
def _pm_install_swallowed_read():
    _original = globals()["git"]

    def _patched(repo, *args, **kw):
        try:
            return _original(repo, *args, **kw)
        except EvalError as exc:
            if "timed out" in str(exc):
                raise
            return ""

    globals()["git"] = _patched


_pm_install_swallowed_read()
# --- end PM06 mutation ---'''

# PM10 (opaque non-leaf hole ignored): the rule "a missing tree or commit
# may conceal the dependency names of an unresolved citation" is dropped:
# only a hole that names the cited token exactly (or by prefix) makes the
# citation unevaluable.
PM10_INSERT = '''# --- PM10 mutation: the opaque non-leaf hole is ignored ---
def _pm_install_ignore_opaque():
    def _patched(stores):
        # the candidate's opaque_hole returns (store, oid)
        return None, None

    globals()["opaque_hole"] = _patched


_pm_install_ignore_opaque()
# --- end PM10 mutation ---'''

# PM11 (any hole refuses): the gate is unconditional and runs when the
# store is built, so a hole the audit never needs refuses the audit too.
# The earlier version of this mutant patched the store's missing() method,
# which is only consulted while a citation is unresolved: it was a lazy
# gate, and the resolved-unused-hole controls could not see it.
PM11_INSERT = '''# --- PM11 mutation: any hole refuses (over-refusal) ---
def _pm_install_any_hole():
    _original = globals()["build_store"]

    def _patched(repo, root):
        store = _original(repo, root)
        missing, opaque = store.missing()
        if missing or opaque:
            raise EvalError(
                f"{repo}: unknown: unavailable required object: "
                f"{len(missing) + len(opaque)} hole(s) in the store")
        return store

    globals()["build_store"] = _patched


_pm_install_any_hole()
# --- end PM11 mutation ---'''

MUTANTS = [
    {
        "id": "PM01-blanket-metadata-refusal",
        "semantic": "promisor metadata alone (extensions.partialClone, "
                    "remote.*.promisor, partialclonefilter, paired "
                    ".promisor+.pack) is not a refusal: a complete "
                    "promisor-marked repository keeps the verdict of its "
                    "full-clone twin",
        "expect_rows": ["PG01", "PG02", "PG03", "PG04", "PG05", "PG06", "PG09", "PG11", "PG12", "PG13", "PG15", "PG17", "PG19", "PG21", "PG22", "PG23", "PG24", "PG26", "PG28", "PG30", "PG31", "PG33", "PG35", "PG39", "PG41", "PG43", "PG44", "PG46", "PG47", "PG48"],
        "attribution_basis": "every cell whose audited repository is promisor-marked: a refusal on the metadata alone turns each of them into exit 2",
        "execution": "grid",
        "alternatives": [
            # the candidate may still carry a promisor classifier: refuse on
            # the metadata alone, before the content is looked at
            {"kind": "regex",
             "pattern": r'(    state = promisor_state\(repo\)\n)',
             "replacement": r'\1    if state["promisor_backed"]:\n'
                            r'        raise EvalError(\n'
                            r'            f"{repo}: partial clone '
                            r'(promisor metadata)")\n'},
            # spelling-independent form: patch the module's own git wrapper
            {"kind": "insert", "anchor": 'if __name__ == "__main__":',
             "text": PM01_INSERT},
        ],
    },
    {
        "id": "PM02-blanket-unknown-refusal",
        "semantic": "the unknown rule covers a locally unresolved citation "
                    "that names unavailable referenced content; it must not "
                    "cover every absent citation, or the historical "
                    "errata-marked clone (absent hash corrected by errata) "
                    "would stop being an ordinary failed finding. The mutant "
                    "refuses every absent (or unknown) citation, before the "
                    "errata ledger is consulted.",
        "expect_rows": ["PG22", "PG23", "PG24", "PG25", "PG29", "PG30", "PG33", "PG34", "PG37", "PG41", "PG42", "PG46", "PG47"],
        "attribution_basis": "every cell with an unresolved citation whose ordinary verdict is a failed finding: the errata-corrected absent hash is refused before the ledger is consulted, and the opaque cells misclassify an absence that a missing tree may conceal",
        "execution": "grid",
        "alternatives": [
            {"kind": "insert", "anchor": 'if __name__ == "__main__":',
             "text": PM02_INSERT},
        ],
    },
    {
        "id": "PM03-skip-required-object-availability",
        "semantic": "objects the audit actually reads must be available: a "
                    "missing required commit/tree/blob/report object is "
                    "could-not-evaluate (exit 2), never a clean or failed "
                    "verdict. This mutant removes the store's missing-object "
                    "computation (the completeness element); PM04 removes the "
                    "decision that uses it. Both attack the same verdict "
                    "surface, so the grid kills them alike: one of them "
                    "surviving is not evidence about the other.",
        "expect_rows": ["PG13", "PG14", "PG15", "PG16", "PG17", "PG18", "PG19", "PG20", "PG21", "PG33", "PG34", "PG46", "PG47"],
        "attribution_basis": "every cell whose required evidence is unavailable and whose verdict must be could-not-evaluate",
        "execution": "grid",
        "alternatives": [
            # the store never learns which objects the repository cannot
            # serve, so an unavailable required object is accepted as absent
            {"kind": "regex",
             "pattern": r'self\._missing = set\(missing_reachable\('
                        r'self\.path, self\.root\)\)',
             "replacement": "self._missing = set()"},
            {"kind": "regex",
             "pattern": r'self\._missing = missing_reachable\('
                        r'self\.path, self\.root\)',
             "replacement": "self._missing = (set(), set())"},
        ],
    },
    {
        "id": "PM04-accept-unavailable-referenced-object",
        "semantic": "a locally unresolved citation that names unavailable "
                    "referenced local content is could-not-evaluate rather "
                    "than proved absent; the mutant accepts it as absent and "
                    "reports an ordinary failed finding",
        "expect_rows": ["PG33", "PG34", "PG46", "PG47"],
        "attribution_basis": "every cell whose unresolved citation names unavailable referenced content",
        "execution": "grid",
        "alternatives": [
            # the helper that decides "the history references it, the
            # repository cannot serve it" never reports a store
            {"kind": "regex",
             "pattern": r'(def unknown_citation\(stores, token\):.*?)'
                        r'for store in stores:',
             "replacement": r'\1for store in ():'},
            {"kind": "regex",
             "pattern": r'(def unknown_citation\(stores, token\):.*?)\n'
                        r'    return None\n',
             "replacement": r'\1\n    return None\n    return stores[0]\n'},
        ],
    },
    {
        "id": "PM05-ignore-second-repo",
        "semantic": "a citation missing in one audited repository but "
                    "present in the other audited repository is resolvable; "
                    "the mutant consults the first repository only",
        "expect_rows": ["PG26", "PG27"],
        "attribution_basis": "every cell whose citation resolves only in the second audited repository",
        "execution": "grid",
        "alternatives": [
            {"kind": "regex",
             "pattern": r'(def lookup\(stores, tokens, peel=""\):.*?)'
                        r'for store in stores:',
             "replacement": r'\1for store in stores[:1]:'},
            {"kind": "regex",
             "pattern": r'(def lookup\(stores, tokens, peel=""\):.*?)'
                        r'for store in stores:',
             "replacement": r'\1for store in ():'},
        ],
    },
    {
        "id": "PM06-swallow-actual-read-error",
        "semantic": "a failing read of the object the audit needs is "
                    "could-not-evaluate; the mutant swallows the failure "
                    "and guesses a value, turning an unavailable object "
                    "into a verdict",
        "expect_rows": ["PG13", "PG14", "PG15", "PG16", "PG17", "PG18", "PG19", "PG20", "PG21", "PG28", "PG43"],
        "attribution_basis": "every cell whose verdict must be could-not-evaluate because a required read failed",
        "execution": "grid",
        "alternatives": [
            {"kind": "insert", "anchor": 'if __name__ == "__main__":',
             "text": PM06_INSERT},
        ],
    },
    {
        "id": "PM07-full-all-missing-gate",
        "semantic": "the store-wide missing walk starts from every present "
                    "root of the store; the mutant adds --all to that root "
                    "set, so a broken unselected REF target that is not "
                    "among the present roots enters the diagnosis. The "
                    "mutant does NOT broaden the name-hiding (opaque) walk, "
                    "which stays rooted at the pinned root only. On the "
                    "finite 47 this mutant may survive; that survival is an "
                    "observation of this candidate, not a global-equivalence "
                    "proof: the canonical mutant can also differ on a "
                    "broken unselected REF target that is not among the "
                    "present roots, so no universal no-op is claimed. "
                    "Supplemental post-fix experiments, specially named and "
                    "separate from the 47 and from this canonical operator, "
                    "may test unselected-ref opacity.",
        "expect_rows": ["PG31", "PG32", "PG35", "PG36", "PG44", "PG45",
                        "PG48"],
        "attribution_basis": "the cells with a hole the audit does not "
                    "need: an unrelated hole must not refuse the audit. The "
                    "finite 47 may not distinguish the mutant (a broken "
                    "unselected REF target outside the present roots is "
                    "outside the grid); no kill is presumed, and the final "
                    "run decides",
        "execution": "grid",
        "alternatives": [
            {"kind": "regex",
             "pattern": r'(    roots = present_roots\(repo\)\n)',
             "replacement": r'\1    roots.append("--all")\n'},
            {"kind": "regex",
             "pattern": r'(    roots = present_commits\(repo\)\n)',
             "replacement": r'\1    roots.append("--all")\n'},
            {"kind": "regex",
             "pattern": r'("--no-object-names",\s*)root',
             "replacement": r'\1"--all"'},
        ],
    },
    {
        # review-only, uncredited: the operator keeps this element out of
        # the executed inventory. The mutant is never applied, never
        # executed and never credited with a kill; the claim is a manual
        # reading of the candidate's isolation flags, recorded here as a
        # note so the review trail names it.
        "id": "PM08-no-lazy-fetch-review-only",
        "semantic": "review-only note, uncredited: the candidate's "
                    "repository-reading wrappers carry --no-lazy-fetch, so "
                    "a missing promisor object is not fetched through the "
                    "promisor remote (transport, repository programs, "
                    "signatures) on the paths those wrappers read. This is "
                    "a manual reading of the candidate's isolation flags, "
                    "not a proof about every git call. The element is not "
                    "part of the executed inventory: no mutant is built, "
                    "no grid invocation is made for it, and it is never "
                    "credited with a kill",
        "expect_rows": [],
        "execution": "review-only",
        "alternatives": [],
    },
    {
        "id": "PM09-peel-bare-full-hash-lookup",
        "semantic": "the bare full-hash lookup stays unpeeled: a citation of "
                    "a locally present blob resolves as found; peeling it "
                    "to ^{commit} turns a present blob into a missing object",
        "expect_rows": ["PG38", "PG39"],
        "attribution_basis": "every cell whose locally present blob must stay an ordinary wrong-type finding",
        "execution": "grid",
        "alternatives": [
            {"kind": "replace", "old": "full = lookup(stores, full_tokens)",
             "new": 'full = lookup(stores, full_tokens, "^{commit}")'},
        ],
    },
    {
        "id": "PM10-ignore-opaque-nonleaf-missing",
        "semantic": "when a citation is unresolved, a missing tree or commit "
                    "may conceal the dependency names, so the citation is "
                    "unevaluable (exit 2); the mutant ignores that hole and "
                    "reports an ordinary failed finding. A known-present blob "
                    "that merely fails commit peeling keeps its wrong-type "
                    "finding either way.",
        "expect_rows": ["PG46", "PG47"],
        "attribution_basis": "every cell whose verdict depends on the opaque non-leaf rule",
        "execution": "grid",
        "alternatives": [
            {"kind": "insert", "anchor": 'if __name__ == "__main__":',
             "text": PM10_INSERT},
        ],
    },
    {
        "id": "PM11-any-hole-refusal",
        "semantic": "no missing-object state may be an unconditional audit "
                    "precondition: an unrelated blob hole next to a "
                    "fabricated citation keeps the ordinary failed finding, "
                    "and an unused tree hole next to fully resolved "
                    "citations keeps the clean verdict; the mutant refuses "
                    "on any hole",
        "expect_rows": ["PG13", "PG14", "PG15", "PG16", "PG17", "PG18", "PG19", "PG20", "PG21", "PG22", "PG28", "PG31", "PG32", "PG33", "PG34", "PG35", "PG36", "PG37", "PG41", "PG42", "PG43", "PG44", "PG45", "PG46", "PG47", "PG48"],
        "attribution_basis": "every cell whose audited repository holds a hole, whatever verdict the cell expects: the gate is unconditional",
        "execution": "grid",
        "alternatives": [
            {"kind": "insert", "anchor": 'if __name__ == "__main__":',
             "text": PM11_INSERT},
        ],
    },
]


def run_grid(grid, auditor, arm, cases, timeout):
    """(exit, rows, stderr, doc). rows is the parsed per-case list, or None.

    The grid runs in its own process group, so a timeout kills the grid and
    every git child it started. A timeout, a harness leak and an exit 2 are
    all reported so the caller can treat them as could-not-evaluate: they
    never kill a mutant.
    """
    cmd = [sys.executable, str(grid), "--arm", arm, "--current",
           str(auditor), "--json"]
    for case in cases or []:
        cmd += ["--case", case]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True)
    except OSError as exc:
        return 2, None, f"cannot start the grid: {exc}", {}
    try:
        out, errout = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (OSError, ProcessLookupError):
            pass
        try:
            out, errout = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out, errout = b"", b""
        return 2, None, f"grid timed out after {timeout}s", {}
    err = errout.decode("utf-8", "replace").strip()
    doc = {}
    try:
        doc = json.loads(out.decode("utf-8", "replace"))
        if not isinstance(doc, dict):
            doc = {}
    except (ValueError, UnicodeDecodeError):
        doc = {}
    rows = []
    for arm_name, arm_doc in (doc.get("arms") or {}).items():
        for row in arm_doc.get("rows") or []:
            row = dict(row)
            row.setdefault("arm", arm_name)
            rows.append(row)
    if proc.returncode == 2:
        return 2, rows, err, doc
    if not rows:
        return 2, rows, err or "grid JSON carries no rows", doc
    return proc.returncode, rows, err, doc


# The grid is adding an explicit internal-error flag; these are the names
# the runner accepts (the exact name is coordinated with GridOracle, and
# the stderr prefix is the fallback when the flag is absent).
INTERNAL_FLAGS = ("internal_error", "internal_errors", "internal")
INTERNAL_STDERR = "could-not-evaluate: internal:"


def harness_fault(doc, rows, err):
    """A harness fault kills nothing: a leak, a timeout, a traceback, an
    internal error, an invalid row exit or a malformed verdict document."""
    for key in ("harness_leaks", "harness_leak", "leaks", "leaked"):
        if doc.get(key):
            return f"grid reported {key}"
    for arm_doc in (doc.get("arms") or {}).values():
        if not isinstance(arm_doc, dict):
            continue
        for key in ("harness_leaks", "harness_leak", "leaks"):
            if arm_doc.get(key):
                return f"grid arm reported {key}"
        for key in INTERNAL_FLAGS:
            if arm_doc.get(key):
                return f"grid arm reported {key}"
    for key in INTERNAL_FLAGS:
        if doc.get(key):
            return f"grid reported {key}"
    for row in rows or []:
        name = row_name(row)
        if row.get("leaked"):
            return f"row {name} leaked"
        if row.get("timed_out"):
            return f"row {name} timed out"
        if row.get("traceback"):
            return f"row {name} raised a traceback"
        for key in INTERNAL_FLAGS:
            if row.get(key):
                return f"row {name} reported {key}"
        code = row.get("exit")
        if code is not None and code not in (0, 1, 2):
            return f"row {name} has an invalid exit {code!r}"
        if code in (0, 1) and "document" in row and row.get("document") is None:
            return f"row {name} has a malformed verdict document"
    if "harness_leak" in err:
        return "grid stderr reports a harness leak"
    if INTERNAL_STDERR in err:
        return "grid stderr reports an internal error"
    # fallback for a grid version that does not carry the internal_error
    # boolean: the auditor's catch-all prints the prefix as the first
    # characters of its stderr, which the row's tail keeps for short
    # messages. The boolean stays authoritative: a long message can push
    # the prefix out of the tail.
    for row in rows or []:
        if INTERNAL_STDERR in str(row.get("stderr_tail") or ""):
            return f"row {row_name(row)} reports an internal error"
    return None


def classify_row(row):
    """How a violated row changed the audited outcome.

    refusal-2       a normal verdict (expected 0 or 1) became a refusal:
                    an over-refusal signal, NOT an availability credit
    actual-verdict  an unavailable case (expected 2) became a real
                    verdict: the availability credit
    verdict-change  a normal verdict became another normal verdict: a
                    substantive verdict change, reported separately
    diagnostic-only  the exit is unchanged: only the diagnostics differ, so
                    the row carries no acceptance or availability credit
    unclassified    the comparison fields (expected_exit, exit) are
                    missing or outside 0/1/2: no class credit is guessed
    """
    expected = row.get("expected_exit")
    actual = row.get("exit")
    if expected not in (0, 1, 2) or actual not in (0, 1, 2):
        return "unclassified"
    if expected in (0, 1) and actual == 2:
        return "refusal-2"
    if expected == 2 and actual in (0, 1):
        return "actual-verdict"
    if expected in (0, 1) and actual in (0, 1):
        return "verdict-change"
    if expected == actual:
        return "diagnostic-only"
    return "other"


def violated_rows(rows):
    """Graded rows the grid did not meet: met false, or a failed twin."""
    bad = []
    for row in rows:
        if not graded(row):
            continue
        if row.get("met") is False or row.get("twin_equal") is False:
            bad.append(row)
    return bad


def graded(row):
    kinds = row.get("kind")
    if kinds is None:
        return True  # no kind: treat every reported row as graded
    if isinstance(kinds, str):
        kinds = (kinds,)
    return any(k in GRADED_KINDS for k in kinds)


def row_name(row):
    for key in ("case", "id", "name", "row"):
        if row.get(key):
            return str(row[key])
    return "<unnamed>"


def row_detail(row):
    keys = ("case", "kind", "exit", "expected_exit", "kinds",
            "expected_kinds", "twin_equal", "objects_acquired",
            "stderr_tail")
    return {k: row[k] for k in keys if k in row}


def expected_match(name, patterns):
    """A cell id (PG22) matches a row name (PG22-unknown-citation-...) by
    prefix, and a glob pattern matches by fnmatch."""
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
        if name == pattern or name.startswith(pattern + "-"):
            return True
    return False


def apply_mutation(source, mutant):
    """(mutated source, applied alternative index) or (None, reason)."""
    seen = []
    for index, alt in enumerate(mutant["alternatives"]):
        if alt["kind"] == "replace":
            old, new = alt["old"], alt["new"]
            count = source.count(old)
            seen.append(f"[{index}] replace x{count}")
            if count == 1:
                return source.replace(old, new), index
        elif alt["kind"] == "regex":
            pattern = alt["pattern"]
            count = len(re.findall(pattern, source, re.DOTALL))
            seen.append(f"[{index}] regex x{count}")
            if count == 1:
                return re.sub(pattern, alt["replacement"], source,
                              flags=re.DOTALL), index
        else:
            anchor = alt["anchor"]
            count = source.count(anchor)
            seen.append(f"[{index}] insert x{count}")
            if count == 1:
                at = source.index(anchor)
                return source[:at] + alt["text"] + "\n" + source[at:], index
    return None, ("no alternative applied cleanly: " + " ".join(seen))


def compiles(source, name):
    try:
        compile(source, f"<{name}>", "exec")
        return True
    except SyntaxError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="mutation sensitivity runner for the promisor grid")
    ap.add_argument("--current", default=str(AUDIT),
                    help="candidate auditor (default: the lane auditor)")
    ap.add_argument("--grid", default=str(GRID),
                    help="promisor grid (default: the lane promisor grid)")
    ap.add_argument("--arm", default="current",
                    help="grid arm to exercise (default: current)")
    ap.add_argument("--case", action="append",
                    help="run only these grid cases (repeatable, forwarded)")
    ap.add_argument("--grid-timeout", type=int, default=DEFAULT_GRID_TIMEOUT,
                    help="seconds allowed for one grid run")
    ap.add_argument("--only", action="append",
                    help="run only the named mutant (repeatable)")
    ap.add_argument("--list", action="store_true",
                    help="print the frozen inventory and exit")
    ap.add_argument("--anchors", metavar="PATH",
                    help="report how often every mutation pattern matches "
                         "PATH (no grid run) and exit")
    ap.add_argument("--selftest", action="store_true",
                    help="exercise the exit mappings on isolated stub "
                         "fixtures and exit")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for mutant in MUTANTS:
            print(f"{mutant['id']}\n  semantic: {mutant['semantic']}\n"
                  f"  expects unmet rows: {mutant['expect_rows'] or '-'}\n"
                  f"  execution: {mutant['execution']}")
        return 0

    if args.selftest:
        return selftest()

    if args.anchors:
        path = Path(args.anchors).resolve()
        if not path.is_file():
            print(f"could-not-evaluate: no candidate at {path}",
                  file=sys.stderr)
            return 2
        source = path.read_text(encoding="utf-8")
        report = []
        for mutant in MUTANTS:
            if mutant["execution"] == "review-only":
                # review-only notes carry no source assertion: there is
                # nothing to match, and nothing is executed for them
                report.append({"mutant": mutant["id"],
                               "alternatives": [], "applicable": [],
                               "applicable_alternative": None,
                               "mutant_compiles": None,
                               "skipped": "review-only"})
                continue
            counts = []
            for alt in mutant["alternatives"]:
                if alt["kind"] == "replace":
                    counts.append({"kind": "replace",
                                   "matches": source.count(alt["old"])})
                elif alt["kind"] == "regex":
                    counts.append({"kind": "regex",
                                   "matches": len(re.findall(alt["pattern"],
                                                            source,
                                                            re.DOTALL))})
                else:
                    counts.append({"kind": "insert",
                                   "matches": source.count(alt["anchor"])})
            applicable = [i for i, c in enumerate(counts) if c["matches"] == 1]
            compiled = None
            if applicable:
                mutated, _ = apply_mutation(source, mutant)
                if mutated is not None:
                    compiled = compiles(mutated, mutant["id"])
            report.append({"mutant": mutant["id"], "alternatives": counts,
                           "applicable": applicable,
                           "applicable_alternative": (applicable[0]
                                                      if applicable else None),
                           "mutant_compiles": compiled})
        if args.json:
            print(json.dumps({"candidate": str(path), "mutants": report},
                             indent=1, sort_keys=True))
        else:
            for row in report:
                marks = " ".join(f"{c['kind']}x{c['matches']}"
                                 for c in row["alternatives"])
                print(f"{row['mutant']}: {marks} "
                      f"-> alternative {row['applicable_alternative']} "
                      f"compiles={row['mutant_compiles']}")
        ok = all(r["applicable_alternative"] is not None
                 and r["mutant_compiles"] for r in report
                 if not r.get("skipped"))
        return 0 if ok else 2

    candidate = Path(args.current).resolve()
    grid = Path(args.grid).resolve()
    if not candidate.is_file():
        print(f"could-not-evaluate: no candidate auditor at {candidate}",
              file=sys.stderr)
        return 2
    if not grid.is_file():
        print(f"could-not-evaluate: no promisor grid at {grid}",
              file=sys.stderr)
        return 2
    source = candidate.read_text(encoding="utf-8")
    rc, rows, err, doc = run_grid(grid, candidate, args.arm, args.case,
                                  args.grid_timeout)
    fault = harness_fault(doc, rows, err)
    if fault:
        print(f"could-not-evaluate: pristine grid: {fault}", file=sys.stderr)
        return 2
    if rc != 0:
        # the pristine candidate must meet the grid; otherwise no mutant can
        # be attributed and nothing is credited
        unmet = sorted({row_name(r) for r in violated_rows(rows)})
        print(f"could-not-evaluate: pristine grid rc={rc} {err} "
              f"unmet={unmet}", file=sys.stderr)
        return 2

    selected = [m for m in MUTANTS if not args.only or m["id"] in args.only]
    if args.only and len(selected) != len(args.only):
        print("could-not-evaluate: unknown mutant id in --only",
              file=sys.stderr)
        return 2

    rows_out = []
    with tempfile.TemporaryDirectory(prefix="promisor-mutants-") as tmp:
        for mutant in selected:
            entry = {"mutant": mutant["id"],
                     "semantic": mutant["semantic"],
                     "execution": mutant["execution"],
                     "expect_rows": mutant["expect_rows"]}
            if mutant["execution"] == "review-only":
                # review-only, uncredited: no mutant is built, the grid is
                # not invoked for it, and it is never credited with a kill
                entry.update(status="review-only", killed=False,
                             executions=0, review_only=1,
                             reason="review-only note: not applied, not "
                                    "executed, not credited")
                rows_out.append(entry)
                continue
            mutated, info = apply_mutation(source, mutant)
            if mutated is None:
                entry.update(status="could-not-evaluate", killed=False,
                             reason=info)
                rows_out.append(entry)
                continue
            if not compiles(mutated, mutant["id"]):
                entry.update(status="could-not-evaluate", killed=False,
                             reason=f"the mutant does not compile "
                                    f"(alternative {info})")
                rows_out.append(entry)
                continue
            path = Path(tmp, f"{mutant['id']}.py")
            path.write_text(mutated, encoding="utf-8")
            mrc, mrows, merr, mdoc = run_grid(grid, path, args.arm, args.case,
                                              args.grid_timeout)
            fault = harness_fault(mdoc, mrows, merr)
            if fault:
                entry.update(status="could-not-evaluate", killed=False,
                             reason=f"grid: {fault}")
                rows_out.append(entry)
                continue
            if mrc == 2:
                entry.update(status="could-not-evaluate", killed=False,
                             reason=f"grid exit 2: {merr}")
                rows_out.append(entry)
                continue
            bad = violated_rows(mrows)
            if mrc == 1 and not bad:
                # the grid says the run failed but names no violated row:
                # its verdict cannot be read, so nothing is credited
                entry.update(status="could-not-evaluate", killed=False,
                             reason="grid exit 1 without an identifiable "
                                    "violated row")
                rows_out.append(entry)
                continue
            expected = mutant["expect_rows"]
            attributed_rows = [r for r in bad
                               if expected_match(row_name(r), expected)]
            unexpected = [r for r in bad
                          if not expected_match(row_name(r), expected)]
            if unexpected:
                # a violated row outside this mutant's attribution is not a
                # kill: the allowlist is not widened, the row is preserved
                names = sorted({row_name(r) for r in unexpected})
                entry.update(status="could-not-evaluate", killed=False,
                             reason="violated rows outside the attribution: "
                                    + ", ".join(names),
                             unexpected_rows=names, failed_rows=[],
                             applied_alternative=info,
                             failed_row_detail=[row_detail(r)
                                                for r in unexpected])
                rows_out.append(entry)
                continue
            classes = {}
            for row in attributed_rows:
                classes.setdefault(classify_row(row), []).append(
                    row_name(row))
            availability = "actual-verdict" in classes
            verdict_change = any(c in ("refusal-2", "verdict-change")
                                 for c in classes)
            credit = availability
            killed = bool(attributed_rows)
            failed = sorted({row_name(r) for r in attributed_rows})
            entry.update(status="killed" if killed else "survived",
                         killed=killed, grid_exit=mrc, failed_rows=failed,
                         applied_alternative=info,
                         failed_row_detail=[row_detail(r)
                                            for r in attributed_rows],
                         classes=classes,
                         availability_credit=availability,
                         verdict_change=verdict_change,
                         diagnostic_only=(bool(classes)
                                          and not verdict_change
                                          and not availability),
                         unclassified=classes.get("unclassified", []),
                         unexpected_rows=[])
            rows_out.append(entry)

    cne = [r["mutant"] for r in rows_out if r["status"] == "could-not-evaluate"]
    killed = [r["mutant"] for r in rows_out if r.get("killed")]
    surviving = [r["mutant"] for r in rows_out if r["status"] == "survived"]
    review_only = [r["mutant"] for r in rows_out
                   if r.get("review_only")]
    doc = {"pristine": "passed", "candidate": str(candidate),
           "grid": str(grid), "arm": args.arm, "cases": args.case or [],
           "mutants": len(rows_out),
           "executable": len(rows_out) - len(review_only),
           "review_only": len(review_only),
           "review_only_ids": review_only,
           "killed": len(killed), "killed_ids": killed,
           "surviving": surviving, "could_not_evaluate": cne,
           "evaluated": len(rows_out) - len(cne) - len(review_only),
           "rows": rows_out}
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for r in rows_out:
            print(f"{r['mutant']} {r['status']} "
                  f"rows={r.get('failed_rows', [])}")
        print(f"mutants={doc['mutants']} "
              f"executable={doc['executable']} "
              f"review-only={doc['review_only']} "
              f"evaluated={doc['evaluated']} "
              f"killed={doc['killed']} surviving={surviving} "
              f"could-not-evaluate={cne}")
    return 2 if cne else 0


# ------------------------------------------------------------------ selftest
# A stub grid, built in a temporary directory, reports what the runner must
# map to which exit code. It reads the candidate: a candidate holding the
# marker PRISTINE is the pristine run, any other candidate is a mutant.

STUB_GRID = '''#!/usr/bin/env python3
"""Stub grid for the runner's selftest: no repository, no fixture.

Every invocation appends a line to GRID_STUB_LOG (the canary): the
selftest uses it to prove that a pristine failure stops the run before any
mutant is built or executed, and that a review-only inventory note causes
no grid invocation at all.
"""
import json
import os
import os.path
import sys

mode = os.environ.get("GRID_STUB_MODE", "ok")
arm = "current"
if "--arm" in sys.argv:
    arm = sys.argv[sys.argv.index("--arm") + 1]
current = ""
if "--current" in sys.argv:
    current = sys.argv[sys.argv.index("--current") + 1]
# the pristine candidate is the one the caller names; the runner writes
# every mutant to <id>.py, and the frozen ids all start with PM
pristine = not os.path.basename(current).startswith("PM")

log = os.environ.get("GRID_STUB_LOG")
if log:
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(("pristine" if pristine else "mutant") + " " + current + "\\n")


def row(case, **kw):
    # the canonical shape a graded row carries: met, exit, expected_exit
    # and the verdict document (None when the run produced no verdict)
    base = {"case": case, "kind": "policy", "met": True, "exit": 0,
            "expected_exit": 0, "document": {"defects": []}}
    base.update(kw)
    return base


if mode == "pristine_fails":
    if pristine:
        doc = {"arms": {arm: {"rows": [row("PG01-pristine-failure",
                                           met=False)]}}}
        print(json.dumps(doc))
        sys.exit(1)
    doc = {"arms": {arm: {"rows": [row("PG01-pristine-failure")]}}}
    print(json.dumps(doc))
    sys.exit(0)
if mode == "unmet" and not pristine:
    doc = {"arms": {arm: {"rows": [row("PG01-complete-lane-promisor-config",
                                       met=False, exit=2,
                                       expected_exit=0, document=None)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "twin" and not pristine:
    doc = {"arms": {arm: {"rows": [
        row("PG22-unknown-citation-incomplete-promisor", twin_equal=False,
            exit=1, expected_exit=0)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "exit2" and not pristine:
    print("could-not-evaluate: stub", file=sys.stderr)
    sys.exit(2)
if mode == "rc1_no_violated_row" and not pristine:
    # the grid reports a failure but names no violated row: the runner must
    # report could-not-evaluate for that reason, not a kill
    doc = {"arms": {arm: {"rows": [row("PG03-met-row", exit=1)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "leak" and not pristine:
    doc = {"arms": {arm: {"harness_leaks": ["PG04-leaked-row"],
                          "rows": [row("PG04-leaked-row", met=False,
                                       leaked=True)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "timeout_row" and not pristine:
    doc = {"arms": {arm: {"rows": [row("PG05-timed-out-row", met=False,
                                       timed_out=True)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "traceback_row" and not pristine:
    # a row whose auditor crashed: a traceback is a harness fault, never a
    # kill
    doc = {"arms": {arm: {"rows": [row("PG06-traceback-row", met=False,
                                       traceback=True)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "internal_row" and not pristine:
    # a row the grid reports as an internal error (the flag GridOracle is
    # adding); the stderr prefix is the fallback
    doc = {"arms": {arm: {"rows": [row("PG07-internal-row", met=False,
                                       internal_error=True)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "malformed_verdict" and not pristine:
    # exit 0 with no verdict document: the verdict cannot be read
    doc = {"arms": {arm: {"rows": [row("PG08-malformed-row", met=False,
                                       exit=0, document=None)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "missing_metadata" and not pristine:
    # a violated row whose comparison fields are missing: no class credit
    # may be guessed from it
    doc = {"arms": {arm: {"rows": [row("PG01-missing-metadata", met=False,
                                       exit=2, expected_exit=None,
                                       document=None)]}}}
    print(json.dumps(doc))
    sys.exit(1)
if mode == "unattributed_row" and not pristine:
    # a violated row outside every mutant's attribution
    doc = {"arms": {arm: {"rows": [row("PG99-outside-the-attribution",
                                       met=False, exit=2,
                                       expected_exit=0, document=None)]}}}
    print(json.dumps(doc))
    sys.exit(1)
doc = {"arms": {arm: {"rows": [row("PG00-clean-row")]}}}
print(json.dumps(doc))
sys.exit(0)
'''

CANDIDATE = '''#!/usr/bin/env python3
"""Synthetic candidate for the runner's selftest.

It carries every anchor the frozen inventory needs, so each mutation
applies exactly once and the mutant compiles."""
import re
import subprocess
from pathlib import Path

GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch")


class EvalError(Exception):
    """Could not evaluate."""


def git(repo, *args, stdin=None, env=None, errors="strict"):
    return ""


def lookup(stores, tokens, peel=""):
    for store in stores:
        pass
    return {t: "found" for t in tokens}


def present_roots(repo):
    return []


def other_helper(repo):
    all_roots = present_roots(repo)
    return all_roots


def audit_round(stores, full_tokens):
    full = lookup(stores, full_tokens)
    return full


def unknown_citation(stores, token):
    for store in stores:
        missing, _ = store.missing()
        for oid in missing:
            if oid == token or oid.startswith(token):
                return store
    return None


def opaque_hole(stores):
    for store in stores:
        _, opaque = store.missing()
        if opaque:
            return store, sorted(opaque)[0]
    return None, None


class RepoStore:
    __slots__ = ("path", "root", "_missing")

    def __init__(self, path, root):
        self.path = path
        self.root = root
        self._missing = None

    def missing(self):
        if self._missing is None:
            self._missing = missing_reachable(self.path, self.root)
        return self._missing


def missing_reachable(repo, root):
    roots = present_roots(repo)

    def walk(extra, walk_roots):
        return set()

    missing = walk((), roots)
    opaque = walk(("--filter=blob:none",), [root])
    return missing, opaque


def report_cutoff(repo, rel):
    return 0


if __name__ == "__main__":
    sys.exit(0)
'''

BROKEN_CANDIDATE = '''#!/usr/bin/env python3
"""Candidate whose anchors sit inside an indented block: an inserted
mutation cannot compile."""
def outer():
    if __name__ == "__main__":
        return 1
'''


def selftest():
    """Exercise the runner's exit mappings on isolated stub fixtures."""
    failures = []
    with tempfile.TemporaryDirectory(prefix="promisor-mutants-selftest-") as tmp:
        root = Path(tmp)
        grid = root / "stub-grid.py"
        grid.write_text(STUB_GRID, encoding="utf-8")
        candidate = root / "candidate.py"
        candidate.write_text(CANDIDATE, encoding="utf-8")
        broken = root / "broken.py"
        broken.write_text(BROKEN_CANDIDATE, encoding="utf-8")

        def run(mode, cand=None, only=None):
            log = root / f"canary-{mode}.log"
            env = dict(os.environ, GRID_STUB_MODE=mode,
                       GRID_STUB_LOG=str(log))
            argv = [sys.executable, str(Path(__file__).resolve()), "--grid",
                    str(grid), "--current", str(cand or candidate), "--json"]
            if only:
                argv += ["--only", only]
            proc = subprocess.run(argv, capture_output=True, env=env,
                                  timeout=300)
            doc = {}
            try:
                doc = json.loads(proc.stdout.decode("utf-8", "replace"))
            except (ValueError, UnicodeDecodeError):
                doc = {}
            calls = []
            if log.exists():
                calls = log.read_text(encoding="utf-8").splitlines()
            return (proc.returncode, doc,
                    proc.stderr.decode("utf-8", "replace"), calls)

        # 1. a fully evaluated inventory is exit 0, and the mutant phase
        #    really ran (the canary holds a pristine line and mutant lines)
        code, doc, err, calls = run("ok")
        if code != 0:
            failures.append(f"ok: exit {code}, expected 0")
        if not calls or not calls[0].startswith("pristine"):
            failures.append("ok: the canary does not start with the "
                            f"pristine invocation: {calls[:2]}")
        mutant_calls = [c for c in calls if c.startswith("mutant")]
        if len(mutant_calls) < 1:
            failures.append("ok: no mutant invocation was recorded")

        # 2. the review-only note causes no grid invocation at all, is
        #    never credited with a kill, and is never applied
        review = [r for r in doc.get("rows", [])
                  if r.get("review_only") or r.get("status") == "review-only"]
        if len(review) != 1:
            failures.append(f"ok: expected exactly one review-only entry, "
                            f"found {len(review)}")
        else:
            entry = review[0]
            if entry.get("killed"):
                failures.append("ok: the review-only entry was credited "
                                "with a kill")
            if entry.get("executions") != 0:
                failures.append("ok: the review-only entry reports "
                                f"executions={entry.get('executions')}")
            if entry.get("review_only") != 1:
                failures.append("ok: the review-only entry is not marked "
                                "review_only")
            if entry.get("failed_rows"):
                failures.append("ok: the review-only entry names failed "
                                "rows")
        if doc.get("review_only") != 1:
            failures.append(f"ok: the document reports review_only="
                            f"{doc.get('review_only')}, expected 1")
        if doc.get("executable") != doc.get("mutants", 0) - 1:
            failures.append(f"ok: executable={doc.get('executable')} and "
                            f"mutants={doc.get('mutants')} do not add up to "
                            f"one review-only note")
        if any("PM08" in c for c in calls):
            failures.append("ok: a grid invocation was made for the "
                            "review-only note")
        if any("PM08" in (k or "") for k in doc.get("killed_ids", [])):
            failures.append("ok: the review-only note was credited with a "
                            "kill")

        # 3. a violated row kills the mutant: at least one kill, and the
        #    named cell is the one the stub made unmet
        code, doc, err, calls = run("unmet", only="PM01-blanket-metadata-refusal")
        if code != 0:
            failures.append(f"unmet: exit {code}, expected 0")
        if not doc.get("killed"):
            failures.append("unmet: no mutant was credited with a kill")
        named = [r for r in doc.get("rows", [])
                 if "PG01-complete-lane-promisor-config"
                 in (r.get("failed_rows") or [])]
        if not named:
            failures.append("unmet: the killed mutant did not name "
                            "PG01-complete-lane-promisor-config")

        # 4. a failed twin is a violated row, and it is named
        code, doc, err, calls = run("twin", only="PM02-blanket-unknown-refusal")
        if code != 0:
            failures.append(f"twin: exit {code}, expected 0")
        if not doc.get("killed"):
            failures.append("twin: no mutant was credited with a kill")
        named = [r for r in doc.get("rows", [])
                 if "PG22-unknown-citation-incomplete-promisor"
                 in (r.get("failed_rows") or [])]
        if not named:
            failures.append("twin: the killed mutant did not name "
                            "PG22-unknown-citation-incomplete-promisor")

        # 5. the could-not-evaluate reasons, each for its own reason
        for mode, needle in (("exit2", "grid exit 2"),
                              ("rc1_no_violated_row",
                               "without an identifiable violated row"),
                              ("leak", "harness_leaks"),
                              ("timeout_row", "timed out"),
                              ("traceback_row", "traceback"),
                              ("internal_row", "internal_error"),
                              ("malformed_verdict", "malformed verdict")):
            code, doc, err, calls = run(mode)
            if code != 2:
                failures.append(f"{mode}: exit {code}, expected 2")
            if doc.get("killed"):
                failures.append(f"{mode}: a could-not-evaluate run credited "
                                f"a kill")
            reasons = " ".join(str(r.get("reason") or "")
                               for r in doc.get("rows", []))
            if needle not in reasons:
                failures.append(f"{mode}: the reason {needle!r} is missing: "
                                f"{reasons[:200]}")

        # 6. a violated row outside the attribution is not a kill: the
        #    mutant is could-not-evaluate and the row is preserved
        code, doc, err, calls = run("unattributed_row", only="PM01-blanket-metadata-refusal")
        if code != 2:
            failures.append(f"unattributed_row: exit {code}, expected 2")
        if doc.get("killed"):
            failures.append("unattributed_row: an out-of-attribution row "
                            "was credited with a kill")
        preserved = [r for r in doc.get("rows", [])
                     if "PG99-outside-the-attribution"
                     in (r.get("unexpected_rows") or [])]
        if not preserved:
            failures.append("unattributed_row: the out-of-attribution row "
                            "was not preserved")
        if not any("outside the attribution" in str(r.get("reason") or "")
                   for r in doc.get("rows", [])):
            failures.append("unattributed_row: the reason does not name "
                            "the out-of-attribution row")

        # 7. a violated row without the comparison fields earns no class
        #    credit: the classification must not guess
        code, doc, err, calls = run("missing_metadata",
                                    only="PM01-blanket-metadata-refusal")
        if code != 0:
            failures.append(f"missing_metadata: exit {code}, expected 0")
        classified = [r for r in doc.get("rows", [])
                      if "PG01-missing-metadata" in (r.get("unclassified")
                                                    or [])]
        if not classified:
            failures.append("missing_metadata: the row is not reported as "
                            "unclassified")
        for row in doc.get("rows", []):
            if row.get("availability_credit"):
                failures.append("missing_metadata: an availability credit "
                                "was granted without comparison fields")

        # 8. a pristine failure stops the run before any mutant phase: the
        #    canary must hold exactly one invocation, the pristine one
        code, doc, err, calls = run("pristine_fails")
        if code != 2:
            failures.append(f"pristine_fails: exit {code}, expected 2")
        if doc.get("killed"):
            failures.append("pristine_fails: a failing pristine run "
                            "credited a kill")
        if len(calls) != 1 or not calls[0].startswith("pristine"):
            failures.append(f"pristine_fails: the canary shows {len(calls)} "
                            f"invocations, expected exactly one pristine "
                            f"one: {calls[:3]}")

        # 9. a mutant that does not compile is could-not-evaluate
        code, doc, err, calls = run("ok", cand=broken)
        if code != 2:
            failures.append(f"broken candidate: exit {code}, expected 2")
        if not doc.get("could_not_evaluate"):
            failures.append("broken candidate: no could-not-evaluate entry")

        # 10. --anchors returns 2 when a mutant does not compile
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--anchors",
             str(broken)], capture_output=True, timeout=120)
        if proc.returncode != 2:
            failures.append(f"--anchors on a broken candidate: exit "
                            f"{proc.returncode}, expected 2")
        # 11. --anchors returns 0 for a sound candidate, and it skips the
        #    review-only note (no source assertion for it)
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--anchors",
             str(candidate), "--json"], capture_output=True, timeout=120)
        if proc.returncode != 0:
            failures.append(f"--anchors on a sound candidate: exit "
                            f"{proc.returncode}, expected 0")
        try:
            anchors = json.loads(proc.stdout.decode("utf-8", "replace"))
            skipped = [m for m in anchors.get("mutants", [])
                       if m.get("skipped") == "review-only"]
            if len(skipped) != 1:
                failures.append(f"--anchors: expected one skipped "
                                f"review-only entry, found {len(skipped)}")
            checked = [m for m in anchors.get("mutants", [])
                       if not m.get("skipped")]
            if len(checked) != 10:
                failures.append(f"--anchors: checked {len(checked)} "
                                f"mutants, expected 10 executable ones")
        except (ValueError, UnicodeDecodeError):
            failures.append("--anchors: the output is not JSON")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"selftest cases=25 failed={len(failures)}")
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
