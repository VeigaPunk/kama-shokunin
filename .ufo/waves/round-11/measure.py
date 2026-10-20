#!/usr/bin/env python3
"""measure.py — kama round-11 provenance/detection gate (C1) and crosswalk
existence/provenance count (C2).

Scope (what this gate can and cannot say)
-----------------------------------------
It measures detection completeness of corpus provenance metadata: the presence
and uniqueness of the three column-zero provenance fields, preservation of each
file's original bytes, and a bounded wording guard against a live-revalidation
claim dated today. It never contacts an endpoint, never reads host config, and
never certifies endpoint health, serving freshness, model identity or quality.
A clean exit means "the provenance/detection checks passed on these bytes",
not "the documented observations are still true". Stdlib only; no network.

Usage
-----
    python3 .ufo/waves/round-11/measure.py provenance [--root DIR] [--baseline PATH]
    python3 .ufo/waves/round-11/measure.py crosswalk  [--root DIR]
    python3 .ufo/waves/round-11/measure.py --selftest

    --root      lane root to measure; default: the repository containing this
                script (three directories above this file).
    --baseline  provenance baseline JSON; default:
                <root>/.ufo/waves/round-11/legacy-baseline.json. An explicit
                relative value resolves against the current directory; only
                byte-identical copies of the pinned baseline are accepted.
    --selftest  run isolated assertions inside one temporary directory only;
                no repository file is read or written.

Exit codes (both modes): 0 clean | 1 failed | 2 could-not-evaluate (invalid input).
`provenance` prints a JSON object carrying the counts `legacy_files`,
`missing_files`, `missing_fields`, `prefix_violations` (plus `duplicate_fields`,
`missing_headings`, `verified_at_live_claims`), a per-file record, and a
`findings` list. `crosswalk` prints `entry` (0/1), the trio counts, occurrence
counts for the required source ids, `table` (0/1) and `findings`.

provenance checks, per baseline file
------------------------------------
* `prefix-mutation` — sha256 over the first `bytes` bytes (the baseline's
  original extent) must still equal the baseline `sha256`; the supplement may
  only be appended after that extent.
* `missing-field` / `duplicate-field` — `source:`, `verified-at:`, `recheck:`
  must each occur exactly once at column zero inside the appended region (the
  bytes after the original extent), outside triple-backtick fences. Body
  occurrences are not part of the trio; indented occurrences do not count.
* `missing-supplement-heading` — a column-zero `## Provenance supplement` line
  must exist in the appended region. A file whose original bytes end without a
  newline therefore needs the appended section to start with its own newline,
  otherwise the heading is glued to the last original line and is not
  column-zero.
* `verified-at-live-claim` — wording considerations: `verified-at:` must not
  claim live revalidation dated "today" or this run's UTC date. The guard is a
  literal, bounded match of `live revalidated` / `live revalidation` /
  `revalidated live` followed by `today` or the run date (optionally `on`), with
  at most 24 preceding characters in the same punctuation-delimited clause
  checked for a negation token (`not`/`no`/`never`/`without`/`non`/`n't`).
  It is a wording guard, not a truth parser: honest negations ("no live
  revalidation", "not live revalidated") pass, exotic rephrasings pass unexamined, and a reviewer still
  checks the actual truth of every value.

Baseline pin
------------
The sha256 of the round-11 baseline is pinned in `BASELINE_SHA256`; its
entries describe source files at lane revision 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad.
The baseline itself lands with this round, not in that earlier revision.
Any other bytes fail closed with `snapshot_tampered` (exit 2), so an edited
snapshot cannot bless a mutation. Regenerating it requires a deliberate pin change.
Evaluation order: JSON parse and non-emptiness (`invalid-baseline`),
then the pinned digest (`snapshot_tampered`), then entry schema (`invalid-baseline`);
no file is measured before the digest matches.

crosswalk checks
----------------
Entry `corpus/knowledge/served-identity-crosswalk.md`: existence (entry=0/1),
the same column-zero trio check, occurrence counts for the required source ids
S001/S010/S011/S012/S016, and markdown-table presence (a separator line plus at
least one pipe row). This is an existence/provenance count only: it does not
judge wording, semantics, or the meaning of availability vs loaded-model
claims — a human reviewer does.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LANE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASELINE_REL = ".ufo/waves/round-11/legacy-baseline.json"

# Pinned digest of the round-11 baseline, shipped with this round.
# BASELINE_REVISION identifies the original source files, not the addition
# of the baseline file. An edited baseline fails closed with
# `snapshot_tampered` (exit 2).
BASELINE_SHA256 = "5d704e90a4ad758f375c5d1312dad7c972b7d1d1a105a7dba3250282f7c38af1"
BASELINE_REVISION = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad"  # informational only

REQUIRED_FIELDS = ("source", "verified-at", "recheck")
FIELD_RE = re.compile(r"^(source|verified-at|recheck):(.*)$")
INDENTED_FIELD_RE = re.compile(r"^[ \t]+(source|verified-at|recheck):")
HEADING_RE = re.compile(r"^##\s+Provenance supplement\b")
FENCE_MARK = "```"
NEGATION_WINDOW = 24
NEGATION_RE = re.compile(r"n't|\b(?:not|no|never|without|non)\b")

CROSSWALK_ENTRY_REL = "corpus/knowledge/served-identity-crosswalk.md"
REQUIRED_SOURCE_IDS = ("S001", "S010", "S011", "S012", "S016")


def _utc_run_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _live_claim_re(run_date: str) -> re.Pattern:
    return re.compile(
        r"(?:live[\s-]+revalidated|live[\s-]+revalidation|revalidated[\s-]+live)"
        r"(?:\s+today\b|\s+(?:on\s+)?" + re.escape(run_date) + r"(?![0-9]))",
        re.IGNORECASE,
    )


def _has_live_claim(value: str, claim_re: re.Pattern) -> bool:
    """Literal, bounded wording guard; not a truth parser (see module docstring)."""
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    for match in claim_re.finditer(normalized):
        window = normalized[max(0, match.start() - NEGATION_WINDOW):match.start()]
        window = re.split(r"[;.!?]", window)[-1]
        if NEGATION_RE.search(window):
            continue
        return True
    return False


def _scan_supplement(lines, first_line_column_zero):
    """Count column-zero provenance fields outside triple-backtick fences.

    Returns (counts, values, heading_found, indented_hits). A first line that
    is glued to the original last byte is skipped entirely: it is a fragment of
    the original content, not a column-zero line of its own.
    """
    counts = {name: 0 for name in REQUIRED_FIELDS}
    values: dict[str, str] = {}
    indented = set()
    heading = False
    in_fence = False
    for index, line in enumerate(lines):
        if index == 0 and not first_line_column_zero:
            continue
        if line.strip().startswith(FENCE_MARK):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = FIELD_RE.match(line)
        if match:
            counts[match.group(1)] += 1
            values.setdefault(match.group(1), match.group(2).strip())
            continue
        indented_match = INDENTED_FIELD_RE.match(line)
        if indented_match:
            indented.add(indented_match.group(1))
            continue
        if HEADING_RE.match(line):
            heading = True
    return counts, values, heading, indented


def _markdown_table(text: str):
    """Return (row_count, separator_found) for pipe-table lines."""
    rows = 0
    separator = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.count("|") >= 2:
            rows += 1
            if "-" in stripped and set(stripped) <= set("|-: "):
                separator = True
    return rows, separator


def _safe_relative(rel) -> bool:
    if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel:
        return False
    parts = Path(rel).parts
    return ".." not in parts and all(part not in ("", ".") for part in parts)


def _valid_entry(entry) -> bool:
    if not isinstance(entry, dict):
        return False
    sha = entry.get("sha256")
    size = entry.get("bytes")
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
        return False
    return type(size) is int and size >= 0


def _error(mode: str, name: str, detail: str, **extra):
    payload = {"mode": mode, "error": name, "detail": detail, "ok": False}
    payload.update(extra)
    return payload


def check_provenance(root: Path, baseline_path: Path, expected_baseline_sha256: str,
                     run_date: str | None = None):
    """Measure the baseline's legacy files; returns (exit_code, payload)."""
    run_date = run_date or _utc_run_date()
    claim_re = _live_claim_re(run_date)
    common = {"root": str(root), "baseline": str(baseline_path)}
    try:
        raw = baseline_path.read_bytes()
    except OSError as exc:
        return 2, _error("provenance", "invalid-baseline", f"baseline unreadable: {exc}", **common)
    try:
        baseline = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return 2, _error("provenance", "invalid-baseline", f"baseline is not valid JSON: {exc}", **common)
    if not isinstance(baseline, dict) or not baseline:
        return 2, _error(
            "provenance", "invalid-baseline",
            "baseline must be a non-empty JSON object; an empty snapshot cannot be clean",
            **common)
    digest = _sha256_bytes(raw)
    if digest != expected_baseline_sha256:
        return 2, _error(
            "provenance", "snapshot_tampered",
            f"baseline sha256 {digest} differs from the pinned digest; a modified snapshot cannot bless mutations",
            baseline_sha256=digest, **common)
    for rel in sorted(baseline):
        if not _safe_relative(rel):
            return 2, _error("provenance", "invalid-baseline",
                             f"unsafe or non-string path key: {rel!r}",
                             baseline_sha256=digest, **common)
        if not _valid_entry(baseline[rel]):
            return 2, _error("provenance", "invalid-baseline",
                             f"entry {rel!r} lacks a 64-hex sha256 and a non-negative integer byte count",
                             baseline_sha256=digest, **common)

    findings = []
    missing_files = missing_fields = prefix_violations = 0
    duplicate_fields = missing_headings = live_claims = 0
    files = []
    for rel in sorted(baseline):
        entry = baseline[rel]
        record = {"path": rel, "present": False, "prefix_ok": None, "heading": None,
                  "fields": {name: 0 for name in REQUIRED_FIELDS}}
        files.append(record)
        try:
            data = (root / rel).read_bytes()
        except FileNotFoundError:
            missing_files += 1
            findings.append({"name": "missing-file", "path": rel,
                             "detail": "baseline-listed file absent under --root"})
            continue
        except OSError as exc:
            return 2, _error("provenance", "invalid-input", f"cannot read {rel}: {exc}",
                             baseline_sha256=digest, **common)
        record["present"] = True
        original_bytes = entry["bytes"]
        prefix_ok = len(data) >= original_bytes and _sha256_bytes(data[:original_bytes]) == entry["sha256"]
        record["prefix_ok"] = prefix_ok
        if not prefix_ok:
            prefix_violations += 1
            reason = "original prefix changed" if len(data) >= original_bytes else "file shorter than the baseline byte count"
            findings.append({"name": "prefix-mutation", "path": rel,
                             "detail": f"{reason}: sha256 over the first {original_bytes} bytes no longer matches the baseline"})
        region = data[original_bytes:] if len(data) >= original_bytes else b""
        first_line_column_zero = original_bytes == 0 or (
            len(data) >= original_bytes and data[original_bytes - 1:original_bytes] == b"\n")
        counts, values, heading, indented = _scan_supplement(
            region.decode("utf-8", errors="replace").split("\n"), first_line_column_zero)
        record["fields"] = counts
        record["heading"] = heading
        for name in REQUIRED_FIELDS:
            if counts[name] == 0:
                missing_fields += 1
                hint = " (an indented occurrence exists; only column-zero lines count)" if name in indented else ""
                findings.append({"name": "missing-field", "path": rel,
                                 "detail": f"{name} absent at column zero in the appended supplement{hint}"})
            elif counts[name] > 1:
                duplicate_fields += 1
                findings.append({"name": "duplicate-field", "path": rel,
                                 "detail": f"{name} appears {counts[name]} times at column zero in the appended supplement"})
        if not heading:
            missing_headings += 1
            findings.append({"name": "missing-supplement-heading", "path": rel,
                             "detail": "no column-zero '## Provenance supplement' heading line in the appended region"})
        verified_at = values.get("verified-at")
        if verified_at and _has_live_claim(verified_at, claim_re):
            live_claims += 1
            findings.append({"name": "verified-at-live-claim", "path": rel,
                             "detail": "verified-at claims live revalidation dated today/this run date; see module docstring wording considerations"})

    ok = not findings
    payload = {
        "mode": "provenance",
        "root": str(root),
        "baseline": str(baseline_path),
        "baseline_sha256": digest,
        "baseline_revision": BASELINE_REVISION,
        "review_date_utc": run_date,
        "legacy_files": len(baseline),
        "missing_files": missing_files,
        "missing_fields": missing_fields,
        "prefix_violations": prefix_violations,
        "duplicate_fields": duplicate_fields,
        "missing_headings": missing_headings,
        "verified_at_live_claims": live_claims,
        "files": files,
        "findings": findings,
        "ok": ok,
    }
    return (0 if ok else 1), payload


def check_crosswalk(root: Path, run_date: str | None = None):
    """Count existence/provenance of the C2 entry; returns (exit_code, payload)."""
    run_date = run_date or _utc_run_date()
    claim_re = _live_claim_re(run_date)
    findings = []
    zero_fields = {name: 0 for name in REQUIRED_FIELDS}
    zero_sources = {sid: 0 for sid in REQUIRED_SOURCE_IDS}
    base = {"mode": "crosswalk", "root": str(root), "entry_path": CROSSWALK_ENTRY_REL,
            "measurement_scope": "existence/provenance only; no semantic admission"}
    try:
        text = (root / CROSSWALK_ENTRY_REL).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        findings.append({"name": "missing-file", "path": CROSSWALK_ENTRY_REL,
                         "detail": "crosswalk entry does not exist yet"})
        payload = dict(base, entry=0, fields=zero_fields, sources=zero_sources,
                       table=0, table_rows=0, findings=findings, ok=False)
        return 1, payload
    except OSError as exc:
        return 2, _error("crosswalk", "invalid-entry", f"cannot read the crosswalk entry: {exc}", **base)

    counts, values, _heading, indented = _scan_supplement(text.split("\n"), True)
    for name in REQUIRED_FIELDS:
        if counts[name] == 0:
            hint = " (an indented occurrence exists; only column-zero lines count)" if name in indented else ""
            findings.append({"name": "missing-field", "path": CROSSWALK_ENTRY_REL,
                             "detail": f"{name} absent at column zero{hint}"})
        elif counts[name] > 1:
            findings.append({"name": "duplicate-field", "path": CROSSWALK_ENTRY_REL,
                             "detail": f"{name} appears {counts[name]} times at column zero"})
    source_counts = {}
    for sid in REQUIRED_SOURCE_IDS:
        occurrences = len(re.findall(r"\b" + sid + r"\b", text))
        source_counts[sid] = occurrences
        if occurrences == 0:
            findings.append({"name": "missing-source-id", "path": CROSSWALK_ENTRY_REL,
                             "detail": f"required source id {sid} never appears in the entry"})
    table_rows, has_table = _markdown_table(text)
    if not has_table:
        findings.append({"name": "missing-table", "path": CROSSWALK_ENTRY_REL,
                         "detail": "no markdown table found (expected the per-engine route/identity table)"})
    verified_at = values.get("verified-at")
    if verified_at and _has_live_claim(verified_at, claim_re):
        findings.append({"name": "verified-at-live-claim", "path": CROSSWALK_ENTRY_REL,
                         "detail": "verified-at claims live revalidation dated today/this run date"})
    ok = not findings
    payload = dict(base, entry=1, fields=counts, sources=source_counts,
                   table=(1 if has_table else 0), table_rows=table_rows,
                   findings=findings, ok=ok)
    return (0 if ok else 1), payload


def run_selftest() -> int:
    """Isolated assertions in one temporary tree; asserts finding names and exits."""
    run_date = _utc_run_date()
    results = []
    legacy_rel = "corpus/knowledge/legacy-one.md"
    heading = "## Provenance supplement \u2014 round 11 (2026-10-19)"

    def supplement(source="none \u2014 historical record",
                   verified_at="2026-10-20 metadata review only; no live revalidation",
                   recheck="on-release \u2014 rerun the authorized probe"):
        return "source: %s\nverified-at: %s\nrecheck: %s\n" % (source, verified_at, recheck)

    try:
        with tempfile.TemporaryDirectory(prefix="kama-measure-selftest-") as tmp_dir:
            tmp = Path(tmp_dir)

            def make_case(label):
                case_dir = tmp / label
                root = case_dir / "root"
                root.mkdir(parents=True)
                return case_dir, root

            def write_file(root, rel, data):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)

            def write_baseline(case_dir, entries):
                path = case_dir / "baseline.json"
                path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
                return path

            def run_case(label, kind, root, baseline_path=None, digest=None,
                         expect_code=0, expect_findings=(), expect_error=None):
                if kind == "provenance":
                    code, payload = check_provenance(
                        root, baseline_path,
                        digest if digest is not None else _sha256_file(baseline_path),
                        run_date)
                else:
                    code, payload = check_crosswalk(root, run_date)
                names = sorted({f["name"] for f in payload.get("findings", [])})
                ok = (code == expect_code and names == sorted(set(expect_findings))
                      and payload.get("error") == expect_error)
                detail = "" if ok else (
                    f" [expected exit={expect_code} findings={sorted(set(expect_findings))} "
                    f"error={expect_error}; got exit={code} findings={names} error={payload.get('error')}]")
                results.append((label, ok, detail))

            def legacy_case(label, original, appended):
                case_dir, root = make_case(label)
                write_file(root, legacy_rel, original + appended)
                baseline_path = write_baseline(case_dir, {
                    legacy_rel: {"sha256": _sha256_bytes(original), "bytes": len(original)}})
                return case_dir, root, baseline_path

            # 1. clean append (original ends with a newline)
            original = b"# legacy one\n\nbody text\n"
            case_dir, root, baseline_path = legacy_case(
                "clean", original, ("\n" + heading + "\n" + supplement()).encode())
            run_case("clean", "provenance", root, baseline_path)

            # 2. clean append onto a file whose original bytes have no final newline
            original = b"# legacy one\n\nbody text no trailing newline"
            case_dir, root, baseline_path = legacy_case(
                "clean-no-final-newline", original, ("\n" + heading + "\n" + supplement()).encode())
            run_case("clean-no-final-newline", "provenance", root, baseline_path)

            # 3. missing field
            case_dir, root, baseline_path = legacy_case(
                "missing-field", b"# legacy one\n\nbody\n",
                ("\n" + heading + "\nsource: none\nverified-at: 2026-10-20 metadata review only\n").encode())
            run_case("missing-field", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("missing-field",))

            # 4. duplicate field
            case_dir, root, baseline_path = legacy_case(
                "duplicate-field", b"# legacy one\n\nbody\n",
                ("\n" + heading + "\nsource: a\nsource: b\n"
                 "verified-at: 2026-10-20 metadata review only\nrecheck: on-release\n").encode())
            run_case("duplicate-field", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("duplicate-field",))

            # 5. original-prefix mutation (same length, one byte changed)
            original = b"# legacy one\n\nbody text\n"
            mutated = b"# legacy ONE\n\nbody text\n"
            case_dir, root = make_case("prefix-mutation")
            write_file(root, legacy_rel, mutated + ("\n" + heading + "\n" + supplement()).encode())
            baseline_path = write_baseline(case_dir, {
                legacy_rel: {"sha256": _sha256_bytes(original), "bytes": len(original)}})
            run_case("prefix-mutation", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("prefix-mutation",))

            # 6. verified-at live-today claim
            case_dir, root, baseline_path = legacy_case(
                "verified-at-live-claim", b"# legacy one\n\nbody\n",
                ("\n" + heading + "\n" + supplement(verified_at="live revalidated today")).encode())
            run_case("verified-at-live-claim", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("verified-at-live-claim",))

            for label, value, expected_exit, expected_findings in (
                ("honest-live-negation", "no live revalidation today", 0, ()),
                ("prior-clause-negation", "No drift observed; live revalidated today",
                 1, ("verified-at-live-claim",)),
            ):
                case_dir, root, baseline_path = legacy_case(
                    label, b"# legacy one\n\nbody\n",
                    ("\n" + heading + "\n" + supplement(verified_at=value)).encode())
                run_case(label, "provenance", root, baseline_path,
                         expect_code=expected_exit, expect_findings=expected_findings)

            # 7. heading glued to an original without a final newline
            case_dir, root, baseline_path = legacy_case(
                "heading-glued", b"# legacy one\n\nbody text no trailing newline",
                (heading + "\n" + supplement()).encode())
            run_case("heading-glued", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("missing-supplement-heading",))

            # 8. fields inside a fence are not counted
            case_dir, root, baseline_path = legacy_case(
                "fields-in-fence", b"# legacy one\n\nbody\n",
                ("\n" + heading + "\n```\n" + supplement() + "```\n").encode())
            run_case("fields-in-fence", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("missing-field",))

            # 9. empty baseline is invalid, not clean
            case_dir, root = make_case("empty-baseline")
            write_file(root, legacy_rel, b"# legacy one\n\nbody\n")
            baseline_path = write_baseline(case_dir, {})
            run_case("empty-baseline", "provenance", root, baseline_path,
                     expect_code=2, expect_error="invalid-baseline")

            # 10. edited baseline fails closed
            case_dir, root = make_case("snapshot-tampered")
            write_file(root, legacy_rel, b"# legacy one\n\nbody\n")
            tampered_original = b"# legacy one\n\nbody\n"
            baseline_path = write_baseline(case_dir, {
                legacy_rel: {"sha256": _sha256_bytes(tampered_original),
                             "bytes": len(tampered_original)}})
            run_case("snapshot-tampered", "provenance", root, baseline_path,
                     digest="0" * 64, expect_code=2, expect_error="snapshot_tampered")

            # 11. crosswalk clean
            entry_text = (
                "# Served-identity crosswalk (round 11)\n\n"
                "source: S016 https://developers.openai.com/api/reference/resources/models/methods/list; "
                "S001 https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md; "
                "S010 https://docs.ollama.com/api/openai-compatibility; "
                "S011 https://docs.ollama.com/api/tags; S012 https://docs.ollama.com/api/ps\n"
                "verified-at: 2026-10-20 \u2014 five public sources reopened; no local runtime contacted\n"
                "recheck: on-release \u2014 reopen the five rows\n\n"
                "| engine | route | semantics |\n|---|---|---|\n"
                "| llama.cpp | GET /v1/models | alias vs returned id |\n"
                "| ollama | GET /api/tags | available, not loaded |\n"
                "| ollama | GET /api/ps | loaded into memory |\n")
            case_dir, root = make_case("crosswalk-clean")
            write_file(root, CROSSWALK_ENTRY_REL, entry_text.encode())
            run_case("crosswalk-clean", "crosswalk", root)

            # 12. crosswalk entry absent
            case_dir, root = make_case("crosswalk-missing-entry")
            run_case("crosswalk-missing-entry", "crosswalk", root,
                     expect_code=1, expect_findings=("missing-file",))

            # 13. crosswalk missing a required source id and the table
            case_dir, root = make_case("crosswalk-missing-source-and-table")
            write_file(root, CROSSWALK_ENTRY_REL, (
                "# Served-identity crosswalk (round 11)\n\n"
                "source: S016 x; S001 x; S010 x; S011 x\n"
                "verified-at: 2026-10-20 \u2014 reopened; no local runtime contacted\n"
                "recheck: on-release \u2014 reopen\n").encode())
            run_case("crosswalk-missing-source-and-table", "crosswalk", root,
                     expect_code=1, expect_findings=("missing-source-id", "missing-table"))

            # Preserve the baseline while truncating or removing its target.
            case_dir, root, baseline_path = legacy_case(
                "prefix-truncated", b"# original prefix\n", b"")
            write_file(root, legacy_rel, b"#")
            run_case("prefix-truncated", "provenance", root, baseline_path,
                     expect_code=1,
                     expect_findings=("prefix-mutation", "missing-field",
                                      "missing-supplement-heading"))
            case_dir, root, baseline_path = legacy_case(
                "provenance-missing-file", b"# original\n", b"")
            (root / legacy_rel).unlink()
            run_case("provenance-missing-file", "provenance", root, baseline_path,
                     expect_code=1, expect_findings=("missing-file",))

            # Exercise actual CLI serialization and exit propagation, not only helpers.
            case_dir, root = make_case("cli")
            write_file(root, CROSSWALK_ENTRY_REL, entry_text.encode())
            for label, mode, expected_exit, expected_names, expected_error in (
                ("cli-crosswalk-clean", "crosswalk", 0, [], None),
                ("cli-provenance-missing-baseline", "provenance", 2, [], "invalid-baseline"),
            ):
                completed = subprocess.run(
                    [sys.executable, str(Path(__file__).resolve()), mode, "--root", str(root)],
                    capture_output=True, text=True, check=False)
                try:
                    payload = json.loads(completed.stdout)
                    names = sorted({item["name"] for item in payload.get("findings", [])})
                    ok = (completed.returncode == expected_exit
                          and names == expected_names
                          and payload.get("error") == expected_error)
                except (ValueError, KeyError, TypeError):
                    ok = False
                results.append((label, ok, "" if ok else
                                f" [exit={completed.returncode} stdout={completed.stdout!r}]"))
    except OSError as exc:
        sys.stdout.write(f"selftest: setup failed: {exc}\n")
        return 2

    passed = 0
    for label, ok, detail in results:
        if ok:
            passed += 1
        sys.stdout.write(f"{'PASS' if ok else 'FAIL'} selftest/{label}{detail}\n")
    sys.stdout.write(f"selftest: {passed}/{len(results)} passed\n")
    return 0 if passed == len(results) else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="measure.py",
        description=("kama round-11 provenance/detection gate (provenance) and "
                     "crosswalk existence/provenance count (crosswalk)."))
    parser.add_argument("mode", nargs="?", choices=("provenance", "crosswalk"),
                        help="measurement mode")
    parser.add_argument("--root", default=str(LANE_ROOT),
                        help="lane root to measure (default: the repository containing this script)")
    parser.add_argument("--baseline", default=None,
                        help="provenance baseline JSON (default: <root>/.ufo/waves/round-11/legacy-baseline.json)")
    parser.add_argument("--selftest", action="store_true",
                        help="run isolated temp-tree assertions instead of a measurement")
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.mode is None:
        parser.error("a mode is required: provenance | crosswalk (or pass --selftest)")
    root = Path(args.root)
    if not root.is_dir():
        payload = _error(args.mode, "invalid-root", f"not a directory: {root}", root=str(root))
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 2
    if args.mode == "provenance":
        baseline_path = Path(args.baseline) if args.baseline else root / DEFAULT_BASELINE_REL
        code, payload = check_provenance(root, baseline_path, BASELINE_SHA256)
    else:
        code, payload = check_crosswalk(root)
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
