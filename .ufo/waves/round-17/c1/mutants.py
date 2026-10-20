#!/usr/bin/env python3
"""Round-17 C1 mutant runner for tests/probe-verdicts/check.py.

Counting command for the C1 calibration claim: how many single-site
grading-weakening mutants of check.py survive the detector, before (frozen
check.py + pair detector) and after (repaired check.py + pair + fault
controls).  Seats apply edits; L1 runs the measurement.

Mutants are single-site edits located by exact source-string match -- never
line numbers.  A mutant whose site is absent is reported ``site_missing``
(n/a), never silently skipped and never counted as survived.  A mutant whose
mutation produces non-compiling source is ``invalid_mutation``.

Mutant set (M1-M5 carry the round-16 MutateHarness.md semantics; M0/M6-M9
are this round's additions):
  M0 ignore-verdict            drop the verdict conjunct
  M1 ignore-reason             drop the reason conjunct
  M2 ignore-exit               drop the probe_exit conjunct
  M3 ignore-drift              drop the drift-invariant conjunct
  M4 casefold-verdict          casefold() both sides of the verdict compare
  M5 timeout-pass              record["passed"] = True on probe timeout
  M6 ignore-served_model       neutralize the served_model invariant
  M7 ignore-route-match        neutralize the GET /v1/models route invariant
  M8 malformed-output-passes   malformed probe output passes, never fails
  M9 reject-all                record["passed"] = False always; the full
                               detector's F0 identity positive control must
                               kill it (and the pair detector sees it too)

M6-M8 apply only to a check.py that grades the new probe-contract
invariants; on the frozen gate they are site_missing (n/a).

Detector modes (per cell):
  pair  -- run the mutated check.py (staged in a scratch dir with the nine
           matrix *.json files) against a "before" probe and the current
           tools/kama-probe.sh; compare exit + per-row result vector with
           the unmutated baseline.  The "before" probe is the round-17
           frozen tools_kama-probe.sh when it differs from current;
           otherwise (frozen == current, as at cff9e62) the round-16 frozen
           kama-probe-before.sh so the 55/17 vs 72/0 pair is reproduced.
  full  -- pair plus tests/probe-verdicts/fault-controls.py
           --check <mutant> --json (schema kama-fault-controls/v1).  Killed
           when the controls' accepted count/fault-id set differs from the
           unmutated baseline -- a rise is the weakening the claim predicts;
           any delta is an observable difference.

Output supports the 2x2 grid {frozen check.py, current check.py} x
{pair, full}: every run emits a JSON doc whose ``cells`` list holds one cell
per (check, detector) pair.  ``--detector both`` yields two cells for one
check; ``--grid`` yields all four.  Per mutant the evidence records which
detector(s) killed it and the first failing row/conjunct.

Killed = any observable difference versus baseline: exit code, doc totals,
per-row (name, passed, verdict, reason, probe_exit, drift, served_model,
error, requests) vector, run failure where baseline was clean, or a
fault-controls accepted delta.

Guards: the matrix set digest uses round-16 measure.py's matrix_digest()
formula and the run refuses (exit 2) anything but the pinned
bf9068d8... digest / 72 tests.  --out is refused inside
tests/probe-verdicts/ and is written atomically.  Every child process runs
in its own session with PYTHONDONTWRITEBYTECODE=1 and its process group is
killed on timeout.  check.py is only ever executed from scratch copies;
it is never imported from the lane.

CLI:
  mutants.py --check PATH [--detector pair|full|both] --out PATH.json
  mutants.py --grid --out PATH.json
  mutants.py --check PATH --dry-run [--out PATH.json]
  mutants.py --selftest

Exits: 0 run completed (counts are in the JSON) or selftest passed,
2 own fault/refusal (including a failing selftest).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUNNER_DIR = Path(__file__).resolve().parent
LANE = RUNNER_DIR.parents[3]          # .ufo/waves/round-17/c1 -> lane root
MATRIX_DIR = LANE / "tests" / "probe-verdicts"
CHECK_CURRENT = MATRIX_DIR / "check.py"
PROBE_CURRENT = LANE / "tools" / "kama-probe.sh"
PROBE_FROZEN_R17 = LANE / ".ufo" / "waves" / "round-17" / "frozen" / "tools_kama-probe.sh"
PROBE_BEFORE_R16 = LANE / ".ufo" / "waves" / "round-16" / "frozen" / "kama-probe-before.sh"
FROZEN_DIR = LANE / ".ufo" / "waves" / "round-17" / "frozen"
FROZEN_CHECK = FROZEN_DIR / "tests_probe-verdicts_check.py"
FROZEN_MANIFEST = FROZEN_DIR / "manifest.json"
FAULT_CONTROLS = MATRIX_DIR / "fault-controls.py"

CHECK_TIMEOUT = 600        # per check.py invocation, seconds
CONTROLS_TIMEOUT = 1800    # fault-controls.py runs 9 faults (F0-F8), each
                           # a whole check.py run capped at 150s inside it
MAX_WORKERS = 6

# Pinned by round-16 measure.py (EXPECTED_MATRIX_SHA256 / EXPECTED_TESTS).
EXPECTED_MATRIX_SHA256 = \
    "bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32"
EXPECTED_TESTS = 72
EXPECTED_MATRIX_FILES = 9

# Deterministic per-row fields used for the killed/survived comparison.
# Deliberately excludes volatile fields (port, probe_sha256, source path).
# `requests` is compared as a unique (method, path) set: route ownership is
# observable, but retry counts are timing-dependent and round-16 rightly
# excluded them from the behavioral vector.
SIG_FIELDS = ("name", "passed", "verdict", "reason", "probe_exit",
              "drift", "served_model", "served_model_ok", "route_ok",
              "error", "requests")


def norm_field(field, value):
    """Comparable form of one row field (see SIG_FIELDS note)."""
    if field == "requests" and isinstance(value, list):
        return sorted({(r.get("method"), r.get("path"))
                       for r in value if isinstance(r, dict)})
    return value


SCHEMA = "kama-c1-mutants/v1"


class RunnerError(Exception):
    """Runner usage or environment fault; reported as exit 2."""


# ----------------------------------------------------------------- masking
def build_masks(src):
    """Return (full_mask, comment_mask).

    full_mask blanks string literals and comments (newlines preserved);
    comment_mask blanks comments only, so string literal text stays visible
    for literal-marker searches while comments cannot false-match.
    """
    full = list(src)
    comments = list(src)
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'":
            q = c
            if src.startswith(q * 3, i):
                end = src.find(q * 3, i + 3)
                j = n if end < 0 else end + 3
            else:
                j = i + 1
                while j < n:
                    ch = src[j]
                    if ch == "\\":
                        j += 2
                        continue
                    if ch == "\n":
                        break
                    if ch == q:
                        j += 1
                        break
                    j += 1
            for k in range(i, min(j, n)):
                if src[k] != "\n":
                    full[k] = " "
            i = j
        elif c == "#":
            j = i
            while j < n and src[j] != "\n":
                full[j] = " "
                comments[j] = " "
                j += 1
            i = j
        else:
            i += 1
    return "".join(full), "".join(comments)


def line_offsets(src):
    """Start offset of each line in src."""
    offs = [0]
    for m in re.finditer("\n", src):
        offs.append(m.end())
    return offs


def line_depths(masked):
    """Bracket depth at the start of each line (masked source)."""
    depths = []
    depth = 0
    for line in masked.split("\n"):
        depths.append(depth)
        for ch in line:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
    return depths


def match_paren(masked, open_idx):
    """Index of the bracket closing the one at open_idx, or None."""
    depth = 0
    for i in range(open_idx, len(masked)):
        ch = masked[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                return i
    return None


def stmt_bounds(masked, pos):
    """(start_line, end_line) of the logical statement containing pos.

    Bracket-depth heuristic: statements in check.py live at depth 0, so the
    start is pos's line when it opens at depth 0, else the nearest upward
    line that opens shallower than pos's line.  The end is the first line
    after which depth returns to the start depth.
    """
    lines = masked.split("\n")
    offs = line_offsets(masked)
    depths = line_depths(masked)
    lineno = 0
    for k, off in enumerate(offs):
        if off > pos:
            break
        lineno = k
    d0 = depths[lineno]
    start = lineno
    if d0 > 0:
        for k in range(lineno - 1, -1, -1):
            if depths[k] < d0:
                start = k
                break
    end = start
    base = depths[start]
    for k in range(start, len(lines) - 1):
        if depths[k + 1] <= base:
            end = k
            break
    else:
        end = len(lines) - 1
    return start, end


def indent_of(line):
    return line[: len(line) - len(line.lstrip())]


# ------------------------------------------------------- conjunct machinery
def passed_block(masked, comments):
    """(open_paren_idx, close_paren_idx) of record["passed"] = (...) or None.

    The name lookup uses the comment-only mask because `["passed"]` is a
    string literal (blanked in the full mask); bracket matching uses the
    full mask so parens inside strings/comments cannot miscount.
    """
    m = re.search(r'record\["passed"\]\s*=\s*\(', comments)
    if not m:
        return None
    open_idx = m.end() - 1
    close_idx = match_paren(masked, open_idx)
    if close_idx is None:
        return None
    return open_idx, close_idx


def conjunct_chunks(masked, comments):
    """Split the passed-block into chunks: [(conn_start, expr_start, expr_end)].

    expr_start/expr_end bound the bare expression (connector excluded);
    conn_start is the connector token start or open_idx+1 for the first
    chunk.  Trailing comments are excluded by masked-text trimming.
    """
    blk = passed_block(masked, comments)
    if not blk:
        return None
    open_idx, close_idx = blk
    conns = []
    depth = 0
    i = open_idx + 1
    while i < close_idx:
        ch = masked[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0:
            m = re.match(r"(and|or)(?![\w])", masked[i:])
            if m and not (masked[i - 1].isalnum() or masked[i - 1] == "_"):
                conns.append(i)
                i += len(m.group(1))
                continue
        i += 1
    bounds = [open_idx + 1] + conns + [close_idx]
    chunks = []
    for k in range(len(bounds) - 1):
        cstart, cend = bounds[k], bounds[k + 1]
        estart = cstart
        if k > 0:
            tok = re.match(r"(and|or)\b", masked[cstart:cend])
            estart = cstart + tok.end()
        # trim to last real-code char in the chunk (comments already spaces)
        eend = cend
        while eend > estart and masked[eend - 1] in " \t\n":
            eend -= 1
        chunks.append((cstart, estart, eend))
    return chunks


def neutralize_conjunct(src, marker_patterns, prefer=()):
    """Replace the passed-block conjunct matching marker_patterns with True.

    marker_patterns: regexes searched on the comment-masked source; every
    pattern must hit the same unique chunk.  prefer: regexes that must also
    hit for the chunk to win (disambiguation).  Returns (new_src, detail).
    """
    masked, comments = build_masks(src)
    chunks = conjunct_chunks(masked, comments)
    if not chunks:
        return None
    hits = []
    for cstart, estart, eend in chunks:
        text = src[estart:eend]
        ctext = comments[estart:eend]
        if all(re.search(p, ctext) for p in marker_patterns):
            hits.append((cstart, estart, eend, text))
    if prefer:
        pref = [h for h in hits
                if all(re.search(p, comments[h[1]:h[2]]) for p in prefer)]
        if pref:
            hits = pref
    if len(hits) != 1:
        return None
    cstart, estart, eend, text = hits[0]
    new = src[:estart] + " True" + src[eend:]
    return new, f"conjunct {text.strip()[:80]!r} -> True"


# ------------------------------------------------------------- edit helpers
def replace_unique_literal(src, old, new):
    if src.count(old) != 1:
        return None
    return src.replace(old, new), f"replace {old.strip()[:60]!r}"


def delete_unique_line_containing(src, needle):
    lines = src.split("\n")
    idx = [i for i, l in enumerate(lines) if needle in l]
    if len(idx) != 1:
        return None
    del lines[idx[0]]
    return "\n".join(lines), f"delete line containing {needle.strip()[:60]!r}"


def insert_after_unique_line(src, anchor_regex, make_line):
    """Insert make_line(indent) after the unique line matching anchor_regex."""
    lines = src.split("\n")
    idx = [i for i, l in enumerate(lines) if re.search(anchor_regex, l)]
    if len(idx) != 1:
        return None
    indent = indent_of(lines[idx[0]])
    lines.insert(idx[0] + 1, make_line(indent))
    return "\n".join(lines), f"insert after {lines[idx[0]].strip()[:60]!r}"


def replace_stmt(src, marker_regex, start_regex, rebuild):
    """Replace the unique statement whose comment-masked text matches
    marker_regex and whose start line matches start_regex.
    rebuild(stmt_text, indent) -> new statement text.
    """
    masked, comments = build_masks(src)
    lines = src.split("\n")
    clines = comments.split("\n")
    candidates = []
    seen = set()
    for m in re.finditer(marker_regex, comments):
        start, end = stmt_bounds(masked, m.start())
        if (start, end) in seen:
            continue
        seen.add((start, end))
        if not re.match(start_regex, clines[start].strip()):
            continue
        stmt_text = "\n".join(lines[start:end + 1])
        candidates.append((start, end, stmt_text))
    if len(candidates) != 1:
        return None
    start, end, stmt_text = candidates[0]
    new_text = rebuild(stmt_text, indent_of(lines[start]))
    if new_text is None:
        return None
    lines[start:end + 1] = new_text.split("\n")
    return "\n".join(lines), f"stmt -> {new_text.strip()[:70]!r}"


def set_lhs_true(src, lhs_regex, marker_regex, value="True"):
    """Set `lhs = ...` statement containing marker_regex to `lhs = value`."""
    def rebuild(stmt_text, indent):
        m = re.match(rf"\s*({lhs_regex})\s*=", stmt_text)
        if not m:
            return None
        return f"{indent}{m.group(1)} = {value}"
    return replace_stmt(src, marker_regex, lhs_regex + r"\s*=", rebuild)


def insert_passed_before_return(src, err_keywords):
    """Find `record["error"] = <kw-ish>` stmt; insert record["passed"]=True
    before the `return` at the same indent that follows it."""
    masked, comments = build_masks(src)
    lines = src.split("\n")
    clines = comments.split("\n")
    sites = []
    for m in re.finditer(r'record\["error"\]\s*=', comments):
        start, end = stmt_bounds(masked, m.start())
        stmt = "\n".join(clines[start:end + 1])
        if not any(re.search(k, stmt) for k in err_keywords):
            continue
        indent = indent_of(lines[start])
        mlines = masked.split("\n")
        for k in range(end + 1, min(end + 8, len(lines))):
            if re.match(r"\s*return\b", mlines[k]) and \
                    indent_of(lines[k]) == indent:
                sites.append((k, indent, lines[start].strip()[:70]))
                break
    if not sites:
        return None
    k, indent, detail = sites[0]
    lines.insert(k, f"{indent}record[\"passed\"] = True")
    return "\n".join(lines), f"pass before return after {detail!r}"


# ------------------------------------------------------------- mutant specs
# Each candidate: (label, fn(src) -> (new_src, detail) | None).  Ordered;
# first that yields a mutation wins.  All matching is on source strings --
# never line numbers.

REASON_CONJUNCT = '            and record["reason"] == expected["reason"]'
EXIT_CONJUNCT = '            and record["probe_exit"] == expected["exit"]'
DRIFT_CONJUNCT = ('            and record["drift"] == '
                  '(record["verdict"] != "MODEL_OK")')
VERDICT_CMP = 'record["verdict"] == expected["verdict"]'
TIMEOUT_ERROR = 'record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"'

MUTANTS = [
    {
        "id": "M0", "name": "ignore-verdict",
        "semantics": "drop the verdict conjunct from record['passed']; the "
                    "verdict compare is the first conjunct, so deleting the "
                    "line would dangle an `and` -- neutralize it to True",
        "candidates": [
            ("conjunct-neutralize",
             lambda s: neutralize_conjunct(
                 s, [r'record\["verdict"\]\s*==\s*expected\["verdict"\]'])),
            ("literal-true",
             lambda s: replace_unique_literal(s, VERDICT_CMP, "True")),
        ],
    },
    {
        "id": "M1", "name": "ignore-reason",
        "semantics": "round-16: delete the reason conjunct from record['passed']",
        "candidates": [
            ("literal-delete",
             lambda s: delete_unique_line_containing(s, REASON_CONJUNCT)),
            ("conjunct-neutralize",
             lambda s: neutralize_conjunct(
                 s, [r'record\["reason"\]\s*==\s*expected\["reason"\]'])),
        ],
    },
    {
        "id": "M2", "name": "ignore-exit",
        "semantics": "round-16: delete the probe_exit conjunct",
        "candidates": [
            ("literal-delete",
             lambda s: delete_unique_line_containing(s, EXIT_CONJUNCT)),
            ("conjunct-neutralize",
             lambda s: neutralize_conjunct(
                 s, [r'record\["probe_exit"\]\s*==\s*expected\["exit"\]'])),
        ],
    },
    {
        "id": "M3", "name": "ignore-drift",
        "semantics": "round-16: delete the drift-invariant conjunct",
        "candidates": [
            ("literal-delete",
             lambda s: delete_unique_line_containing(s, DRIFT_CONJUNCT)),
            ("conjunct-neutralize",
             lambda s: neutralize_conjunct(s, [r'record\["drift"\]'])),
        ],
    },
    {
        "id": "M4", "name": "casefold-verdict",
        "semantics": "round-16: casefold() the verdict comparison",
        "candidates": [
            ("literal-casefold",
             lambda s: replace_unique_literal(
                 s, VERDICT_CMP,
                 'record["verdict"].casefold() == '
                 'expected["verdict"].casefold()')),
        ],
    },
    {
        "id": "M5", "name": "timeout-pass",
        "semantics": "round-16: record passed=True inside TimeoutExpired",
        "candidates": [
            ("literal-insert",
             lambda s: insert_after_unique_line(
                 s, re.escape(TIMEOUT_ERROR),
                 lambda ind: f'{ind}record["passed"] = True')),
            ("timeout-branch-insert",
             lambda s: insert_after_unique_line(
                 s, r'record\["error"\]\s*=.*timed out',
                 lambda ind: f'{ind}record["passed"] = True')),
        ],
    },
    {
        "id": "M6", "name": "ignore-served_model",
        "semantics": "neutralize the served_model invariant (new grading only)",
        "candidates": [
            # landed shape: `and record["served_model_ok"]` inside passed
            ("conjunct-served_model_ok",
             lambda s: neutralize_conjunct(
                 s, [r'\brecord\["served_model_ok"\]'])),
            # direct-comparison style: `and record["served_model"] == <rhs>`
            ("conjunct-served_model",
             lambda s: neutralize_conjunct(
                 s, [r'record\["served_model"\]'])),
            # flag assigned from a multi-line stmt -> force it True
            ("lhs-served_model_ok",
             lambda s: set_lhs_true(
                 s, r'record\["served_model_ok"\]', r'served_model')),
            # expected-value stmt -> expected = actual (always equal)
            ("lhs-served_model_expected",
             lambda s: set_lhs_true(
                 s, r'record\["served_model_expected"\]',
                 r'expected_served_model|served_model',
                 value='record["served_model"]')),
        ],
    },
    {
        "id": "M7", "name": "ignore-route-match",
        "semantics": "neutralize the GET /v1/models route invariant",
        "candidates": [
            # landed shape: `and record["route_ok"] is not False`
            ("conjunct-route_ok",
             lambda s: neutralize_conjunct(
                 s, [r'\brecord\["route_ok"\]'])),
            ("conjunct-route-generic",
             lambda s: neutralize_conjunct(
                 s, [r'route'],
                 prefer=[r'record\["requests"\]|route_ok|match'])),
            # flag assignments -> force True
            ("lhs-route_ok",
             lambda s: set_lhs_true(
                 s, r'record\["route_ok"\]',
                 r'fetched_models_route|route_ok|/v1/models')),
            ("lhs-route_match",
             lambda s: set_lhs_true(
                 s, r'record\["route_match"\]|record\["route_matched"\]',
                 r'/v1/models|route')),
            # helper `return any(... "/v1/models" ...)` -> return True
            ("return-models-route",
             lambda s: replace_stmt(
                 s, re.escape('"/v1/models"'), r"return\b",
                 lambda stmt, ind: f"{ind}return True")),
            # conjunct mentioning the models path directly
            ("conjunct-models-path",
             lambda s: neutralize_conjunct(
                 s, [r'/v1/models|GET'])),
        ],
    },
    {
        "id": "M8", "name": "malformed-output-passes",
        "semantics": "malformed probe output passes instead of failing",
        "candidates": [
            # landed + frozen shape: error assign with malformed-ish text,
            # then `return record` -> pass the row instead
            ("pass-before-return",
             lambda s: insert_passed_before_return(
                 s, [r"malform", r"unparseable", r"not an object",
                     r"invalid row", r"non-object"])),
            # older wording variant of the same branch
            ("except-unparseable",
             lambda s: insert_after_unique_line(
                 s, r'record\["error"\]\s*=.*unparseable probe output',
                 lambda ind: f'{ind}record["passed"] = True')),
            # flag-in-passed style: `and record["error"] is None`
            ("conjunct-error-none",
             lambda s: neutralize_conjunct(
                 s, [r'record\["error"\]\s+is\s+None'])),
            # `if row is None:` block -> pass inside it
            ("row-none-branch",
             lambda s: insert_after_unique_line(
                 s, r'if row is None:',
                 lambda ind: f'{ind}    record["passed"] = True')),
        ],
    },
    {
        "id": "M9", "name": "reject-all",
        "semantics": "record['passed'] is False for every row; the full "
                    "detector's F0 identity positive control must kill it",
        "candidates": [
            ("and-false",
             lambda s: replace_unique_literal(
                 s, 'record["passed"] = (',
                 'record["passed"] = False and (')),
            ("stmt-false",
             lambda s: replace_stmt(
                 s, r'record\["passed"\]\s*=', r'record\["passed"\]\s*=',
                 lambda stmt, ind: f'{ind}record["passed"] = False')),
        ],
    },
]


def apply_mutant(src, mutant):
    """Return (new_src, detail) or None when no candidate site matches."""
    for label, fn in mutant["candidates"]:
        out = fn(src)
        if out is not None:
            new_src, detail = out
            return new_src, f"{label}: {detail}"
    return None


# ------------------------------------------------------------------ running
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    try:
        return sha256_bytes(Path(path).read_bytes())
    except OSError:
        return None


def matrix_set():
    """Load the nine lane matrix files using round-16 measure.py's
    matrix_digest() formula; refuse anything but the pinned set.

    measure.py: files = sorted(CHECK.parent.glob("*.json"));
    lines = "".join(f"{f.name} {sha256(f)}\n"); digest over that text.
    """
    files = sorted(MATRIX_DIR.glob("*.json"))
    lines = "".join(
        f"{f.name} {sha256_file(f)}\n" for f in files)
    digest = hashlib.sha256(lines.encode()).hexdigest()
    n_tests = 0
    for f in files:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RunnerError(f"matrix file unreadable: {f.name}: {exc}")
        if isinstance(doc, list):
            n_tests += len(doc)
    if len(files) != EXPECTED_MATRIX_FILES:
        raise RunnerError(
            f"matrix file count {len(files)} != {EXPECTED_MATRIX_FILES}")
    if digest != EXPECTED_MATRIX_SHA256:
        raise RunnerError(
            f"matrix set digest {digest} != pinned {EXPECTED_MATRIX_SHA256}")
    if n_tests != EXPECTED_TESTS:
        raise RunnerError(
            f"matrix test count {n_tests} != pinned {EXPECTED_TESTS}")
    return [(f.name, f.read_bytes()) for f in files], digest


def verify_frozen(check_path):
    """When --check resolves to the frozen copy, pin it to the manifest."""
    resolved = Path(check_path).resolve()
    if resolved != FROZEN_CHECK.resolve():
        return None                      # not the frozen copy; nothing to pin
    try:
        manifest = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunnerError(f"frozen manifest unreadable: {exc}")
    want = None
    for f in manifest.get("files", []):
        if (LANE / f.get("frozen", "")).resolve() == resolved:
            want = f["sha256"]
            break
    if want is None:
        raise RunnerError("frozen check.py absent from manifest")
    got = sha256_file(resolved)
    if got != want:
        raise RunnerError(
            f"frozen check.py digest mismatch: manifest {want} file {got}")
    return {"path": str(resolved), "sha256": got, "verified": True}


def choose_before_probe():
    """Pick the 'before' probe: r17-frozen if it differs from current, else
    the r16-frozen kama-probe-before.sh (frozen == current at cff9e62)."""
    cur = sha256_file(PROBE_CURRENT)
    frz = sha256_file(PROBE_FROZEN_R17) if PROBE_FROZEN_R17.is_file() else None
    if cur is None:
        raise RunnerError(f"current probe unreadable: {PROBE_CURRENT}")
    if frz and frz != cur:
        return PROBE_FROZEN_R17, "r17-frozen"
    if not PROBE_BEFORE_R16.is_file():
        raise RunnerError(
            "frozen probe == current probe but the r16 before-probe is "
            f"missing: {PROBE_BEFORE_R16}")
    return PROBE_BEFORE_R16, "r16-frozen (reproduces 55/17 vs 72/0 pair)"


def run_cmd(cmd, cwd=None, timeout=CHECK_TIMEOUT):
    """Run cmd in its own session; kill the process group on timeout.

    PYTHONDONTWRITEBYTECODE=1 keeps children from dropping __pycache__
    next to lane sources.  Never raises for child misbehaviour.
    """
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    obs = {"cmd": list(cmd), "exit": None, "stdout": "", "stderr": "",
           "error": None}
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                start_new_session=True)
    except OSError as exc:
        obs["error"] = f"spawn failed: {exc}"
        return obs
    try:
        out, err = proc.communicate(timeout=timeout)
        obs["stdout"], obs["stderr"] = out, err
        obs["exit"] = proc.returncode
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        obs["error"] = f"timed out after {timeout}s; process group killed"
    return obs


def run_check(check_dir, probe_path, timeout=CHECK_TIMEOUT):
    """Run check.py in check_dir against probe; return observation dict."""
    obs = run_cmd([sys.executable, "check.py", "--probe", str(probe_path),
                   "--json"], cwd=str(check_dir), timeout=timeout)
    if obs["error"] is not None:
        return {"exit": obs["exit"], "doc": None, "error": obs["error"],
                "stderr_tail": obs["stderr"][-400:]}
    try:
        doc = json.loads(obs["stdout"])
    except (json.JSONDecodeError, TypeError) as exc:
        return {"exit": obs["exit"], "doc": None,
                "error": f"unparseable check.py stdout: {exc}",
                "stdout_tail": obs["stdout"][-400:],
                "stderr_tail": obs["stderr"][-400:]}
    return {"exit": obs["exit"], "doc": doc, "error": None,
            "stderr_tail": obs["stderr"][-400:]}


def run_controls(check_path, timeout=CONTROLS_TIMEOUT):
    """Run fault-controls.py --check <path> --json; return observation.

    Contract (kama-fault-controls/v1): top-level accepted/detected ints and
    faults[] with per-fault detected flags; exit 0 iff accepted==0, 1 if any
    accepted, 2 on the controls' own fault.
    """
    obs = {"available": FAULT_CONTROLS.is_file(), "path": str(check_path),
           "exit": None, "accepted": None, "detected": None,
           "accepted_ids": None, "error": None}
    if not obs["available"]:
        obs["error"] = f"not found: {FAULT_CONTROLS}"
        return obs
    got = run_cmd([sys.executable, str(FAULT_CONTROLS), "--check",
                   str(check_path), "--json"], timeout=timeout)
    obs["exit"] = got["exit"]
    if got["error"] is not None:
        obs["error"] = got["error"]
        return obs
    try:
        doc = json.loads(got["stdout"])
    except (json.JSONDecodeError, TypeError) as exc:
        obs["error"] = (f"unparseable fault-controls stdout (exit "
                        f"{got['exit']}): {exc}")
        return obs
    if isinstance(doc, dict):
        obs["accepted"] = doc.get("accepted")
        obs["detected"] = doc.get("detected")
        obs["schema"] = doc.get("schema")
        faults = doc.get("faults")
        if isinstance(faults, list):
            obs["accepted_ids"] = [f.get("id") for f in faults
                                   if isinstance(f, dict)
                                   and not f.get("detected")]
    if got["exit"] == 2:
        obs["error"] = "fault-controls reported its own fault (exit 2)"
    return obs


# ----------------------------------------------------------------- diffs
def diff_observations(base, mut):
    """List of observable differences between baseline and mutant runs."""
    diffs = []
    if base["exit"] != mut["exit"]:
        diffs.append({"kind": "exit", "baseline": base["exit"],
                      "mutant": mut["exit"]})
    if mut["doc"] is None:
        if base["doc"] is not None or mut["error"] != base["error"]:
            diffs.append({"kind": "run_failure",
                          "mutant_error": mut["error"],
                          "stderr_tail": mut.get("stderr_tail")})
        return diffs
    if base["doc"] is None:
        diffs.append({"kind": "baseline_invalid"})
        return diffs
    for key in ("tests", "passes", "failures"):
        if base["doc"].get(key) != mut["doc"].get(key):
            diffs.append({"kind": "doc_total", "field": key,
                          "baseline": base["doc"].get(key),
                          "mutant": mut["doc"].get(key)})
    brows = {r.get("name"): r for r in base["doc"].get("records", [])}
    mrows = {r.get("name"): r for r in mut["doc"].get("records", [])}
    for name in sorted(set(brows) | set(mrows)):
        b, m = brows.get(name), mrows.get(name)
        if b is None or m is None:
            diffs.append({"kind": "row_presence", "name": name,
                          "baseline": b is not None, "mutant": m is not None})
            continue
        row_diff = {}
        for f in SIG_FIELDS:
            bv = norm_field(f, b.get(f))
            mv = norm_field(f, m.get(f))
            if bv != mv:
                row_diff[f] = {"baseline": bv, "mutant": mv}
        if row_diff:
            diffs.append({"kind": "row_fields", "name": name,
                          "diffs": row_diff})
    return diffs


def first_failing_row(diffs):
    """Compact 'which row/conjunct failed' pointer for the report."""
    for d in diffs:
        if d["kind"] == "row_fields":
            field = next(iter(d["diffs"]))
            return {"row": d["name"], "field": field}
    for d in diffs:
        if d["kind"] in ("doc_total", "exit", "run_failure", "row_presence"):
            return {"kind": d["kind"],
                    "detail": {k: v for k, v in d.items() if k != "kind"}}
    return None


# ------------------------------------------------------------------ cells
def stage_check(dirpath, source, matrix):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / "check.py").write_text(source, encoding="utf-8")
    for name, data in matrix:
        (dirpath / name).write_bytes(data)


def run_cell(check_path, detector, matrix, cell_root, before_probe,
             before_label):
    """Run one (check, detector) cell; returns the cell document."""
    check_path = Path(check_path).resolve()
    try:
        src = check_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RunnerError(f"{check_path} unreadable: {exc}")
    try:
        compile(src, str(check_path), "exec")
    except SyntaxError as exc:
        raise RunnerError(f"{check_path} does not compile: {exc}")
    frozen = verify_frozen(check_path)

    bdir = cell_root / "baseline"
    stage_check(bdir, src, matrix)
    base_before = run_check(bdir, before_probe)
    base_after = run_check(bdir, PROBE_CURRENT)
    baseline_valid = (base_before["doc"] is not None
                      and base_after["doc"] is not None)
    base_controls = run_controls(bdir / "check.py") \
        if detector == "full" else None
    baseline = {"valid": baseline_valid,
                "before": {"probe": str(before_probe), "label": before_label,
                           "probe_sha256": sha256_file(before_probe),
                           "exit": base_before["exit"],
                           "passes": (base_before["doc"] or {}).get("passes"),
                           "failures": (base_before["doc"] or {}).get("failures"),
                           "error": base_before["error"]},
                "current": {"probe": str(PROBE_CURRENT),
                            "probe_sha256": sha256_file(PROBE_CURRENT),
                            "exit": base_after["exit"],
                            "passes": (base_after["doc"] or {}).get("passes"),
                            "failures": (base_after["doc"] or {}).get("failures"),
                            "error": base_after["error"]},
                "fault_controls": None if base_controls is None else {
                    "accepted": base_controls["accepted"],
                    "accepted_ids": base_controls["accepted_ids"],
                    "exit": base_controls["exit"],
                    "error": base_controls["error"]}}
    if before_label.startswith("r16-frozen") and baseline_valid:
        baseline["r16_reference"] = {
            "expected": {"before": "55/17 exit 1",
                         "current": "72/0 exit 0"},
            "observed": {"before": f"{base_before['doc']['passes']}/"
                                   f"{base_before['doc']['failures']} "
                                   f"exit {base_before['exit']}",
                         "current": f"{base_after['doc']['passes']}/"
                                    f"{base_after['doc']['failures']} "
                                    f"exit {base_after['exit']}"}}

    results = []
    applied = []
    for m in MUTANTS:
        got = apply_mutant(src, m)
        entry = {"id": m["id"], "name": m["name"],
                 "site_found": got is not None, "killed": None,
                 "status": None, "evidence": {"semantics": m["semantics"]}}
        if got is None:
            entry["status"] = "site_missing"
        else:
            new_src, detail = got
            entry["evidence"]["mutation"] = detail
            try:
                compile(new_src, "<mutant>", "exec")
            except SyntaxError as exc:
                entry["status"] = "invalid_mutation"
                entry["evidence"]["invalid"] = str(exc)
            else:
                applied.append((entry, new_src))
        results.append(entry)

    if not baseline_valid:
        for entry, _ in applied:
            entry["status"] = "inconclusive"
            entry["evidence"]["baseline"] = "baseline runs invalid"
    else:
        def task(pair):
            entry, new_src = pair
            mdir = cell_root / entry["id"].lower()
            stage_check(mdir, new_src, matrix)
            ev = entry["evidence"]
            killed_by = []
            m_before = run_check(mdir, before_probe)
            m_after = run_check(mdir, PROBE_CURRENT)
            ev["runs"] = {}
            first_diff = None
            for tag, base, mut, probe in (
                    ("before", base_before, m_before, before_probe),
                    ("current", base_after, m_after, PROBE_CURRENT)):
                diffs = diff_observations(base, mut)
                ev["runs"][tag] = {
                    "probe": str(probe), "exit": mut["exit"],
                    "passes": (mut["doc"] or {}).get("passes"),
                    "failures": (mut["doc"] or {}).get("failures"),
                    "diffs": diffs}
                if diffs:
                    killed_by.append(f"pair:{tag}")
                    if first_diff is None:
                        first_diff = first_failing_row(diffs)
            if detector == "full" and base_controls is not None:
                mc = run_controls(mdir / "check.py")
                ev["fault_controls"] = {
                    "accepted_baseline": base_controls["accepted"],
                    "accepted_mutant": mc["accepted"],
                    "accepted_ids_mutant": mc["accepted_ids"],
                    "exit": mc["exit"], "error": mc["error"]}
                if base_controls["error"] is None \
                        and base_controls["accepted"] is not None:
                    if mc["error"] is not None or mc["accepted"] is None:
                        killed_by.append("full:controls_fault")
                    elif mc["accepted"] != base_controls["accepted"]:
                        ev["fault_controls"]["accepted_delta"] = \
                            mc["accepted"] - base_controls["accepted"]
                        rose = mc["accepted"] > base_controls["accepted"]
                        killed_by.append("full:accepted_"
                                         + ("rose" if rose else "changed"))
                        if first_diff is None:
                            first_diff = {"kind": "fault_controls",
                                          "detail": {"accepted_ids_mutant":
                                                     mc["accepted_ids"]}}
                else:
                    ev["fault_controls"]["note"] = \
                        "baseline controls unusable; pair-only verdict"
            if first_diff is not None:
                ev["first_failing"] = first_diff
            entry["killed"] = bool(killed_by)
            entry["status"] = "killed" if killed_by else "survived"
            entry["evidence"]["killed_by"] = killed_by
            return entry

        with ThreadPoolExecutor(
                max_workers=min(MAX_WORKERS, max(1, len(applied)))) as pool:
            list(pool.map(task, applied))

    killed = sum(1 for e in results if e["killed"] is True)
    survived = sum(1 for e in results if e["killed"] is False)
    return {
        "check": str(check_path), "check_sha256": sha256_file(check_path),
        "frozen": frozen, "detector": detector,
        "baseline": baseline, "mutants": results,
        "totals": {"mutants": len(results),
                   "applicable": sum(1 for e in results if e["site_found"]),
                   "killed": killed, "survived": survived,
                   "site_missing": sum(1 for e in results
                                       if e["status"] == "site_missing"),
                   "invalid": sum(1 for e in results
                                  if e["status"] == "invalid_mutation"),
                   "inconclusive": sum(1 for e in results
                                       if e["status"] == "inconclusive")}}


def dry_run(check_path, out_path):
    if not Path(check_path).is_file():
        raise RunnerError(f"--check not found: {check_path}")
    try:
        src = Path(check_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise RunnerError(f"--check unreadable: {exc}")
    try:
        compile(src, str(check_path), "exec")
    except SyntaxError as exc:
        raise RunnerError(f"--check does not compile: {exc}")
    frozen = verify_frozen(check_path)
    mutants = []
    for m in MUTANTS:
        entry = {"id": m["id"], "name": m["name"], "site_found": False,
                 "killed": None, "evidence": {"semantics": m["semantics"]}}
        got = apply_mutant(src, m)
        if got is not None:
            new_src, detail = got
            entry["site_found"] = True
            entry["evidence"]["mutation"] = detail
            try:
                compile(new_src, "<mutant>", "exec")
            except SyntaxError as exc:
                entry["evidence"]["invalid"] = str(exc)
        else:
            entry["evidence"]["status"] = "site_missing"
        mutants.append(entry)
    doc = {"schema": SCHEMA, "mode": "dry-run", "check": str(check_path),
           "check_sha256": sha256_file(check_path), "frozen": frozen,
           "mutants": mutants,
           "totals": {"mutants": len(mutants),
                      "site_found": sum(1 for x in mutants if x["site_found"]),
                      "site_missing": sum(1 for x in mutants
                                          if not x["site_found"])}}
    emit(doc, out_path)
    return 0


def real_run(checks, detectors, out_path, keep_scratch):
    """checks: [(label, path)]; detectors: list of 'pair'|'full'."""
    for _, cpath in checks:
        if not Path(cpath).is_file():
            raise RunnerError(f"check.py not found: {cpath}")
    matrix, matrix_digest = matrix_set()
    before_probe, before_label = choose_before_probe()

    root = Path(tempfile.mkdtemp(prefix="kama-r17-c1mutants-"))
    cells = []
    try:
        for label, cpath in checks:
            for det in detectors:
                cells.append(run_cell(
                    Path(cpath), det, matrix,
                    root / f"{label}-{det}", before_probe, before_label))
        doc = {
            "schema": SCHEMA,
            "grid": {"checks": [{"label": l, "path": str(p)}
                                for l, p in checks],
                     "detectors": detectors},
            "probes": {
                "before": {"path": str(before_probe), "label": before_label,
                           "sha256": sha256_file(before_probe)},
                "current": {"path": str(PROBE_CURRENT),
                            "sha256": sha256_file(PROBE_CURRENT)}},
            "matrix": {"dir": str(MATRIX_DIR), "files": len(matrix),
                       "set_sha256": matrix_digest,
                       "pinned": EXPECTED_MATRIX_SHA256,
                       "tests": EXPECTED_TESTS},
            "fault_controls": {"path": str(FAULT_CONTROLS),
                               "available": FAULT_CONTROLS.is_file()},
            "cells": cells,
            "scratch": {"dir": str(root), "kept": keep_scratch},
        }
        emit(doc, out_path)
        ok = all(c["baseline"]["valid"] for c in cells)
        return 0 if ok else 2
    finally:
        if not keep_scratch:
            shutil.rmtree(root, ignore_errors=True)


def emit(doc, out_path):
    text = json.dumps(doc, indent=2) + "\n"
    if out_path is None:
        sys.stdout.write(text)
        return
    out = Path(out_path).resolve()
    if out.parent == MATRIX_DIR.resolve() or \
            MATRIX_DIR.resolve() in out.parents:
        raise RunnerError(
            f"refusing --out inside {MATRIX_DIR} (matrix set is pinned)")
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=out.name + ".", dir=str(out.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, out)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print(f"wrote {out}", file=sys.stderr)


# ------------------------------------------------------------------ selftest
FIXTURE_V1 = '''
import json, subprocess
PROBE_TIMEOUT = 30
def grade(entry, probe):
    test = entry["test"]
    record = {"passed": False}
    server = None
    try:
        try:
            proc = run_probe(probe, 1, test["expect"])
        except subprocess.TimeoutExpired:
            record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"
            return record
        record["probe_exit"] = proc.returncode
        try:
            doc = json.loads(proc.stdout)
            row = doc["rows"][0]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            record["error"] = (f"unparseable probe output: {exc}; "
                               f"stdout={proc.stdout[-300:]!r} "
                               f"stderr={proc.stderr[-300:]!r}")
            return record
        for key in ("verdict", "reason", "drift", "served_model", "evidence"):
            record[key] = row.get(key)
        expected = test["expected"]
        record["passed"] = (
            record["verdict"] == expected["verdict"]
            and record["reason"] == expected["reason"]
            and record["probe_exit"] == expected["exit"]
            # probe contract: drift == (verdict != MODEL_OK); assert it so an
            # inconsistent drift flag (e.g. MODEL_LOADING must drift) fails.
            and record["drift"] == (record["verdict"] != "MODEL_OK")
        )
        return record
    except OSError as exc:
        raise
'''

FIXTURE_V2 = '''
import json, subprocess
PROBE_TIMEOUT = 30
def fetched_models_route(test, requests):
    if test["port_mode"] == "closed":
        return None
    return any(r.get("method") == "GET" and
               r.get("path", "").split("?", 1)[0] == "/v1/models"
               for r in requests)

def expected_served_model(test, verdict):
    if verdict not in ("MODEL_OK", "MODEL_MISMATCH"):
        return "-"
    return ",".join(served_ids(test))

def grade(entry, probe):
    test = entry["test"]
    record = {"passed": False}
    try:
        try:
            proc = run_probe(probe, 1, test["expect"])
        except subprocess.TimeoutExpired:
            record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"
            return record
        record["probe_exit"] = proc.returncode
        record["route_ok"] = fetched_models_route(test, record["requests"])
        row, why = probe_output_row(proc.stdout)
        if row is None:
            record["error"] = (f"malformed probe output: {why}; "
                               f"stdout={proc.stdout[-300:]!r} "
                               f"stderr={proc.stderr[-300:]!r}")
            return record
        for key in ("verdict", "reason", "drift", "served_model", "evidence"):
            record[key] = row.get(key)
        expected = test["expected"]
        record["served_model_expected"] = expected_served_model(
            test, record["verdict"])
        record["served_model_ok"] = (
            record["served_model"] == record["served_model_expected"])
        record["passed"] = (
            record["verdict"] == expected["verdict"]
            and record["reason"] == expected["reason"]
            and record["probe_exit"] == expected["exit"]
            and record["drift"] == (record["verdict"] != "MODEL_OK")
            and record["served_model_ok"]
            and record["route_ok"] is not False
        )
        return record
    except OSError as exc:
        raise
'''


def selftest():
    """Self-contained mutation-machinery checks; touches nothing in the lane."""
    cases = []

    def expect(fixture, mid, want_site, contains=None, absent=None):
        mut = next(m for m in MUTANTS if m["id"] == mid)
        got = apply_mutant(fixture, mut)
        site = got is not None
        ok = site == want_site
        detail = ""
        if site:
            new_src, detail = got
            try:
                compile(new_src, "<selftest>", "exec")
            except SyntaxError as exc:
                ok = False
                detail += f" | SyntaxError {exc}"
            if contains and contains not in new_src:
                ok = False
                detail += f" | missing {contains!r}"
            if absent and absent in new_src:
                ok = False
                detail += f" | still present {absent!r}"
        elif want_site:
            detail = "site_missing"
        cases.append({"fixture": "v2" if "fetched_models_route" in fixture
                      else "v1", "mutant": mid, "want_site": want_site,
                      "ok": ok, "detail": detail[:120]})

    # v1 fixture (frozen grading): M0-M5, M8, M9 found; M6/M7 absent
    for mid in ("M0", "M1", "M2", "M3", "M4", "M5", "M8", "M9"):
        expect(FIXTURE_V1, mid, True)
    for mid in ("M6", "M7"):
        expect(FIXTURE_V1, mid, False)
    # v2 fixture (repaired grading): all ten found; spot-check mutated text
    for mid in ("M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"):
        expect(FIXTURE_V2, mid, True)
    expect(FIXTURE_V2, "M0", True, absent=VERDICT_CMP)
    expect(FIXTURE_V2, "M4", True, contains="casefold()")
    expect(FIXTURE_V2, "M5", True, contains='record["passed"] = True')
    expect(FIXTURE_V2, "M6", True, contains="and True")
    expect(FIXTURE_V2, "M7", True, contains="and True")
    expect(FIXTURE_V2, "M8", True, contains='record["passed"] = True')
    expect(FIXTURE_V2, "M9", True, contains="False and (")
    # semantic spot-checks on the v2 source
    src6 = apply_mutant(FIXTURE_V2, next(m for m in MUTANTS
                                         if m["id"] == "M6"))[0]
    ok6 = 'and True\n            and record["route_ok"] is not False' in src6
    cases.append({"fixture": "v2", "mutant": "M6-exact",
                  "want_site": True, "ok": ok6,
                  "detail": "only served_model_ok neutralized"})
    src7 = apply_mutant(FIXTURE_V2, next(m for m in MUTANTS
                                         if m["id"] == "M7"))[0]
    ok7 = 'and record["served_model_ok"]\n            and True' in src7
    cases.append({"fixture": "v2", "mutant": "M7-exact",
                  "want_site": True, "ok": ok7,
                  "detail": "only route_ok neutralized"})
    src9 = apply_mutant(FIXTURE_V1, next(m for m in MUTANTS
                                         if m["id"] == "M9"))[0]
    ok9 = 'record["passed"] = False and (' in src9
    cases.append({"fixture": "v1", "mutant": "M9-exact",
                  "want_site": True, "ok": ok9,
                  "detail": "passed forced False"})
    passed = all(c["ok"] for c in cases)
    print(json.dumps({"selftest": "pass" if passed else "fail",
                      "cases": cases}, indent=2))
    return 0 if passed else 2


# -------------------------------------------------------------------- cli
def build_parser():
    p = argparse.ArgumentParser(
        description="C1 mutant counting runner for probe-verdicts check.py")
    p.add_argument("--check",
                   help="check.py path to mutate (frozen or current)")
    p.add_argument("--detector", choices=("pair", "full", "both"),
                   default="full",
                   help="per cell: pair = two-probe run comparison; full = "
                        "pair + fault-controls accepted count; both emits "
                        "two cells (default full)")
    p.add_argument("--grid", action="store_true",
                   help="run the full 2x2 grid: {frozen, current} check.py "
                        "x {pair, full}; ignores --check/--detector")
    p.add_argument("--out", help="write result JSON here (atomically; refused "
                                 "inside tests/probe-verdicts/)")
    p.add_argument("--dry-run", action="store_true",
                   help="locate mutant sites only; never runs check.py")
    p.add_argument("--keep-scratch", action="store_true",
                   help="keep the /tmp scratch tree for inspection")
    p.add_argument("--selftest", action="store_true",
                   help="exercise mutation machinery on embedded fixtures")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if args.grid:
            checks = [("frozen", FROZEN_CHECK), ("current", CHECK_CURRENT)]
            return real_run(checks, ["pair", "full"], args.out,
                            args.keep_scratch)
        if not args.check:
            print("error: --check (or --grid) is required", file=sys.stderr)
            return 2
        check_path = Path(args.check).resolve()
        label = "frozen" if check_path == FROZEN_CHECK.resolve() else "check"
        if args.dry_run:
            return dry_run(check_path, args.out)
        detectors = ["pair", "full"] if args.detector == "both" \
            else [args.detector]
        return real_run([(label, check_path)], detectors, args.out,
                        args.keep_scratch)
    except RunnerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
