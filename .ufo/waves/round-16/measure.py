#!/usr/bin/env python3
"""Kama round-16 C1 counting command: stub-matrix before/after comparison.

L1's measurement for the MODEL_LOADING claim (C1). This runner:

1. Verifies the frozen "before" probe snapshot against
   .ufo/waves/round-16/frozen/manifest.json (sha256, and bytes when
   declared) and byte-for-byte against the git blob recorded as
   source_commit:source_path. Any mismatch exits 4 without running
   the harness — a wrong "before" red baseline is worse than none.
2. Runs `python3 tests/probe-verdicts/check.py --probe P --json` for
   each named probe: `before` (the frozen snapshot), `after`
   (tools/kama-probe.sh), plus any extra `--probe NAME=PATH` pairs.
3. Writes .ufo/waves/round-16/run-<name>.json receipts:
   {"name", "command", "cwd", "exit", "stdout_sha256", "parsed",
   "stderr_tail"}.
4. Prints a name/exit/passes/failures table, per-family pass counts,
   and the test names whose verdict differed between before and after.

Exit codes:
  0  before has >= 1 failure, after has 0 failures, and every test
     whose verdict changed is a MODEL_LOADING expectation.
  1  the measurement ran but the condition did not hold.
  2  usage error (bad --probe NAME=PATH, duplicate/reserved name).
  3  the frozen manifest itself is unreadable or malformed.
  4  frozen snapshot verification failed (sha256, bytes, or git blob
     mismatch); nothing was executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

WAVE = Path(__file__).resolve().parent
LANE = WAVE.parents[2]
CHECK = LANE / "tests" / "probe-verdicts" / "check.py"
FROZEN = WAVE / "frozen" / "kama-probe-before.sh"
MANIFEST = WAVE / "frozen" / "manifest.json"
AFTER_PROBE = LANE / "tools" / "kama-probe.sh"

# Fallbacks used only when the manifest omits these fields; the manifest
# is authoritative when present.
DEFAULT_COMMIT = "20e392ea683a36bc223eb7cb45897acfb45456a3"
DEFAULT_SOURCE_PATH = "tools/kama-probe.sh"

TAIL_CHARS = 600
DEFAULT_TIMEOUT_SECONDS = 600
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
RESERVED_NAMES = {"before", "after"}

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_MANIFEST = 3
EXIT_FROZEN_MISMATCH = 4


def tail_bytes(data, limit=TAIL_CHARS):
    if not data:
        return ""
    return data[-limit:].decode("utf-8", errors="replace")


def load_manifest():
    try:
        raw = MANIFEST.read_bytes()
    except OSError as exc:
        print(f"measure: cannot read frozen manifest {MANIFEST}: {exc}",
              file=sys.stderr)
        sys.exit(EXIT_MANIFEST)
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        print(f"measure: frozen manifest {MANIFEST} is not valid JSON: {exc}",
              file=sys.stderr)
        sys.exit(EXIT_MANIFEST)
    if not isinstance(doc, dict) or not isinstance(doc.get("sha256"), str):
        print(f"measure: frozen manifest {MANIFEST} lacks a sha256 field",
              file=sys.stderr)
        sys.exit(EXIT_MANIFEST)
    return doc


def verify_frozen(manifest):
    """Exit 4 unless the frozen snapshot matches manifest and git blob."""
    problems = []
    try:
        frozen = FROZEN.read_bytes()
    except OSError as exc:
        print(f"measure: cannot read frozen probe {FROZEN}: {exc}",
              file=sys.stderr)
        sys.exit(EXIT_FROZEN_MISMATCH)

    digest = hashlib.sha256(frozen).hexdigest()
    if digest != manifest["sha256"]:
        problems.append(
            f"sha256 mismatch: frozen is {digest}, manifest declares "
            f"{manifest['sha256']}")
    declared_bytes = manifest.get("bytes")
    if isinstance(declared_bytes, int) and declared_bytes != len(frozen):
        problems.append(
            f"byte count mismatch: frozen is {len(frozen)}, manifest "
            f"declares {declared_bytes}")

    commit = manifest.get("source_commit") or DEFAULT_COMMIT
    source_path = manifest.get("source_path") or DEFAULT_SOURCE_PATH
    spec = f"{commit}:{source_path}"
    try:
        blob = subprocess.run(
            ["git", "-C", str(LANE), "cat-file", "blob", spec],
            capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"measure: cannot run git cat-file for {spec}: {exc}",
              file=sys.stderr)
        sys.exit(EXIT_FROZEN_MISMATCH)
    if blob.returncode != 0:
        problems.append(
            f"git cat-file blob {spec} exited {blob.returncode}: "
            f"{tail_bytes(blob.stderr, 200)}")
    elif blob.stdout != frozen:
        problems.append(
            f"frozen snapshot differs from git blob {spec} "
            f"(blob sha256 {hashlib.sha256(blob.stdout).hexdigest()})")

    if problems:
        for problem in problems:
            print(f"measure: frozen verification failed: {problem}",
                  file=sys.stderr)
        sys.exit(EXIT_FROZEN_MISMATCH)
    return digest


def run_check(name, probe, timeout):
    """Invoke check.py once; return the receipt dict written to run-<name>.json."""
    argv = ["python3", str(CHECK), "--probe", str(probe), "--json"]
    receipt = {
        "name": name,
        "command": argv,
        "cwd": str(LANE),
        "exit": None,
        "stdout_sha256": None,
        "parsed": None,
        "stderr_tail": "",
    }
    try:
        proc = subprocess.run(argv, cwd=str(LANE), capture_output=True,
                              timeout=timeout)
        stdout, stderr = proc.stdout or b"", proc.stderr or b""
        receipt["exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = (exc.stderr or b"") if isinstance(exc.stderr, bytes) else b""
        stderr += f"\nmeasure: killed after {timeout}s".encode()
    except OSError as exc:
        stdout, stderr = b"", f"measure: cannot spawn check.py: {exc}".encode()

    receipt["stdout_sha256"] = hashlib.sha256(stdout).hexdigest()
    receipt["stderr_tail"] = tail_bytes(stderr)
    try:
        receipt["parsed"] = json.loads(stdout.decode("utf-8",
                                                     errors="replace"))
    except ValueError:
        receipt["parsed"] = None

    out = WAVE / f"run-{name}.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def records_of(parsed):
    if isinstance(parsed, dict) and isinstance(parsed.get("records"), list):
        return parsed["records"]
    return []


def count_field(parsed, *keys):
    if not isinstance(parsed, dict):
        return None
    for key in keys:
        value = parsed.get(key)
        if isinstance(value, int):
            return value
    return None


def record_name(rec):
    return rec.get("name") if isinstance(rec, dict) else None


def record_family(rec):
    if not isinstance(rec, dict):
        return "?"
    family = rec.get("family")
    if isinstance(family, str) and family:
        return family
    name = rec.get("name")
    if isinstance(name, str) and "." in name:
        return name.rsplit(".", 1)[0]
    return "?"


def _verdict(rec, side):
    """side: 'expected' or 'observed'; tolerate flat or nested record keys."""
    if not isinstance(rec, dict):
        return None
    nested = rec.get(side)
    if isinstance(nested, dict) and isinstance(nested.get("verdict"), str):
        return nested["verdict"]
    for key in (f"{side}_verdict", "verdict" if side == "observed" else ""):
        if key and isinstance(rec.get(key), str):
            return rec[key]
    return None


def record_passed(rec):
    if not isinstance(rec, dict):
        return False
    flag = rec.get("passed")
    if isinstance(flag, bool):
        return flag
    if isinstance(flag, int):
        return flag != 0
    return False


def family_counts(receipt):
    """{family: [passed, total]} for one run's parsed records."""
    counts = {}
    for rec in records_of(receipt["parsed"]):
        fam = record_family(rec)
        slot = counts.setdefault(fam, [0, 0])
        slot[1] += 1
        if record_passed(rec):
            slot[0] += 1
    return counts


def parse_probe_arg(text):
    if "=" not in text:
        raise argparse.ArgumentTypeError(
            f"--probe expects NAME=PATH, got {text!r}")
    name, _, path = text.partition("=")
    if not NAME_RE.match(name):
        raise argparse.ArgumentTypeError(
            f"bad probe name {name!r}: use [A-Za-z0-9._-]")
    if name in RESERVED_NAMES:
        raise argparse.ArgumentTypeError(
            f"probe name {name!r} is reserved")
    if not path:
        raise argparse.ArgumentTypeError(f"empty probe path in {text!r}")
    return name, path


def build_parser():
    parser = argparse.ArgumentParser(
        description="Round-16 C1 counting command: run the probe-verdict "
                    "stub matrix against the frozen before-probe and the "
                    "current after-probe, write run-<name>.json receipts, "
                    "and report the verdict diff.")
    parser.add_argument(
        "--probe", action="append", type=parse_probe_arg, default=[],
        metavar="NAME=PATH",
        help="extra probe to measure; repeatable, written to run-NAME.json")
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS,
        metavar="SECONDS",
        help=f"per-probe check.py timeout (default "
             f"{DEFAULT_TIMEOUT_SECONDS}s)")
    return parser


# Matrix breadth pin (falsify-wave ReviewMeasurePy F1/F2): a trimmed or swapped
# matrix must not yield a PASS. The digest covers every *.json file name and its
# sha256 under tests/probe-verdicts/, sorted by name.
EXPECTED_MATRIX_SHA256 = "bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32"
EXPECTED_TESTS = 72
EXPECTED_LOADING = 17


def matrix_digest():
    files = sorted((CHECK.parent).glob("*.json"))
    lines = "".join(
        f"{f.name} {hashlib.sha256(f.read_bytes()).hexdigest()}\n" for f in files)
    return len(files), hashlib.sha256(lines.encode()).hexdigest()


def main(argv=None):
    args = build_parser().parse_args(argv)
    names = [name for name, _ in args.probe]
    if len(names) != len(set(names)):
        print("measure: duplicate --probe name", file=sys.stderr)
        return EXIT_USAGE

    manifest = load_manifest()
    frozen_sha = verify_frozen(manifest)
    print(f"frozen snapshot verified: sha256 {frozen_sha} "
          f"(blob {manifest.get('source_commit', DEFAULT_COMMIT)}:"
          f"{manifest.get('source_path', DEFAULT_SOURCE_PATH)})")
    n_files, m_sha = matrix_digest()
    print(f"matrix: {n_files} files, set sha256 {m_sha}")
    if m_sha != EXPECTED_MATRIX_SHA256:
        print(f"measure: matrix set digest {m_sha} != pinned "
              f"{EXPECTED_MATRIX_SHA256}", file=sys.stderr)
        return EXIT_FAIL

    probes = [("before", FROZEN), ("after", AFTER_PROBE)] + list(args.probe)
    receipts = []
    for name, probe in probes:
        receipts.append(run_check(name, probe, args.timeout))
        print(f"wrote {WAVE / ('run-' + name + '.json')}")

    # Table: name / check.py exit / passes / failures.
    print("\nname\texit\tpasses\tfailures")
    for receipt in receipts:
        parsed = receipt["parsed"]
        passes = count_field(parsed, "passes", "passed")
        failures = count_field(parsed, "failures", "failed")
        fmt = lambda v: "-" if v is None else str(v)
        print(f"{receipt['name']}\t{receipt['exit']}\t"
              f"{fmt(passes)}\t{fmt(failures)}")

    print("\nper-family pass counts (passed/total):")
    for receipt in receipts:
        counts = family_counts(receipt)
        body = ", ".join(
            f"{fam} {counts[fam][0]}/{counts[fam][1]}"
            for fam in sorted(counts)) or "-"
        print(f"  {receipt['name']}: {body}")

    # Verdict diff between before and after (first two runs only).
    before, after = receipts[0], receipts[1]
    before_recs = {record_name(r): r for r in records_of(before["parsed"])}
    after_recs = {record_name(r): r for r in records_of(after["parsed"])}
    changed = []
    for name in sorted(set(before_recs) & set(after_recs),
                       key=lambda n: (n or "")):
        bv = _verdict(before_recs[name], "observed")
        av = _verdict(after_recs[name], "observed")
        if bv != av:
            expected = _verdict(after_recs[name], "expected")
            if expected is None:
                expected = _verdict(before_recs[name], "expected")
            changed.append({
                "name": name,
                "before_verdict": bv,
                "after_verdict": av,
                "expected_verdict": expected,
            })

    print("\ntests whose verdict differs before -> after:")
    if changed:
        for item in changed:
            print(f"  {item['name']}: {item['before_verdict']} -> "
                  f"{item['after_verdict']} (expected "
                  f"{item['expected_verdict']})")
    else:
        print("  (none)")

    before_failures = count_field(before["parsed"], "failures", "failed")
    after_failures = count_field(after["parsed"], "failures", "failed")
    all_changed_loading = all(
        item["expected_verdict"] == "MODEL_LOADING" for item in changed)
    # Directional red (L1 integration, after ConnectTameshi/ReviewKq19Interplay):
    # the frozen arm must fail exactly the MODEL_LOADING expectations and pass
    # every other row; the verdict changes must be exactly those rows.
    loading_names = {n for n, r in before_recs.items()
                     if _verdict(r, "expected") == "MODEL_LOADING"}
    before_failed = {n for n, r in before_recs.items() if not record_passed(r)}
    changed_names = {i["name"] for i in changed}
    directional = (bool(loading_names) and before_failed == loading_names
                   and changed_names == loading_names
                   and set(before_recs) == set(after_recs))
    print(f"\ndirectional: loading_expectations={len(loading_names)} "
          f"before_failed={len(before_failed)} changed={len(changed_names)} "
          f"equal={directional}")
    breadth = (len(before_recs) == EXPECTED_TESTS == len(after_recs)
               and len(loading_names) == EXPECTED_LOADING)
    exits = (before.get("exit") == 1 and after.get("exit") == 0)
    print(f"breadth: tests={len(before_recs)}/{len(after_recs)} "
          f"(pinned {EXPECTED_TESTS}) loading={len(loading_names)} "
          f"(pinned {EXPECTED_LOADING}) ok={breadth}; check.py exits "
          f"before={before.get('exit')} after={after.get('exit')} ok={exits}")
    ok = (isinstance(before_failures, int) and before_failures >= 1
          and after_failures == 0
          and all_changed_loading and directional and breadth and exits)

    if not ok:
        reasons = []
        if not (isinstance(before_failures, int) and before_failures >= 1):
            reasons.append(f"before failures {before_failures!r} (need >=1)")
        if not breadth:
            reasons.append("matrix breadth differs from the pinned counts")
        if not exits:
            reasons.append("check.py exits are not before=1 / after=0")
        if after_failures != 0:
            reasons.append(f"after failures {after_failures!r} (need 0)")
        if not all_changed_loading:
            bad = [i["name"] for i in changed
                   if i["expected_verdict"] != "MODEL_LOADING"]
            reasons.append(
                "non-MODEL_LOADING verdict changes: " + ", ".join(bad))
        if not directional:
            reasons.append(
                "before-failure set or changed set differs from the "
                "MODEL_LOADING expectation set: extra_failed="
                + ",".join(sorted(before_failed - loading_names))
                + " missing_failed="
                + ",".join(sorted(loading_names - before_failed))
                + " changed_not_loading="
                + ",".join(sorted(changed_names - loading_names)))
        print("\nresult: FAIL — " + "; ".join(reasons))
        return EXIT_FAIL

    print(f"\nresult: PASS — before red ({before_failures} failures), "
          f"after green, {len(changed)} verdict change(s), all "
          f"MODEL_LOADING expectations")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
