#!/usr/bin/env python3
"""Round-56 X08: verify every battery receipt records an exit code and its exact outcome field.

Input is the copied receipt set plus the committed preregistration. For each receipt the
checker requires the exit field, the outcome field(s) the receipt's producer is supposed
to emit, membership of each outcome value in the frozen vocabulary, and agreement between
the recorded exit code and the outcome (exit 0 iff the outcome equals the roster
expectation for C1, exit 0 iff met=True for C2). A receipt that omits the exit field, or
whose exit contradicts its outcome, is red.

Self-tests run against three synthetic copies of the real receipts, so a green main run is
not vacuous: stripping the exit line must be red, appending a contradicting exit must be
red, appending the matching exit must be green.
"""
import argparse
import json
import pathlib
import re
import sys
import tempfile

KV = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\[[^\]]*\]|\S+)")

# receipt path -> (label, class, required keys, outcome keys)
C1_RECEIPTS = {
    "controls/base-c1.out": ("base-old-counter", "c1"),
    "measured/base-c1.out": ("base-old-counter", "c1"),
    "measured/build-c1.out": ("round56-counter", "c1"),
    "measured/m-drop-ldaudit.out": ("m-drop-ldaudit", "c1"),
}
C2_RECEIPTS = {
    "controls/base-c2.out": ("base-c2", "c2"),
    "measured/build-c2.out": ("build-c2", "c2"),
}
C1_KEYS = ("ld_audit", "pid", "problems", "exit")
C2_KEYS = ("tip", "present", "roster_match", "kills", "controls", "met", "exit")
LEDGER_LINE = ("ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit "
               "interface: undefined symbol: la_version; ignored.")
LEDGER = re.compile("^" + re.escape(LEDGER_LINE) + "$")


def parse(path):
    """Return (fields, problems) for one receipt; problems is a list of defects."""
    text = path.read_text()
    fields = {}
    dupes = []
    unparsed = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if LEDGER.match(line):
            continue
        hits = KV.findall(line)
        if not hits:
            unparsed.append(line)
            continue
        for k, v in hits:
            if k in fields:
                dupes.append(k)
            fields[k] = v
    problems = []
    problems += [f"duplicate-key:{k}" for k in sorted(set(dupes))]
    problems += [f"unparsed-line:{l!r}" for l in unparsed]
    return fields, problems


def check(receipts, prereg, rel, label, kind):
    path = receipts / rel
    if not path.is_file():
        return {"receipt": rel, "label": label, "class": kind, "status": "MISSING",
                "fields": {}, "problems": ["receipt-absent"]}
    fields, problems = parse(path)
    required = C1_KEYS if kind == "c1" else C2_KEYS
    for key in required:
        if key not in fields:
            problems.append(f"missing-field:{key}")
    if kind == "c1":
        if fields.get("ld_audit") not in ("detected", "missed"):
            problems.append(f"bad-outcome:{fields.get('ld_audit')}")
        expected = prereg["battery"]["roster"].get(label, {}).get("expected")
        if expected is not None and fields.get("ld_audit") != expected:
            problems.append(f"outcome-not-roster-expected:{fields.get('ld_audit')}!={expected}")
        implied = 0 if fields.get("ld_audit") == expected else 1
    else:
        for key in ("present", "roster_match", "kills", "controls"):
            if key in fields and not re.fullmatch(r"\d+", fields[key]):
                problems.append(f"nonnumeric:{key}")
        if fields.get("met") not in ("True", "False"):
            problems.append(f"bad-outcome:{fields.get('met')}")
        implied = 0 if fields.get("met") == "True" else 1
    if "exit" in fields:
        if not re.fullmatch(r"\d+", fields["exit"]):
            problems.append(f"nonnumeric:exit")
        elif int(fields["exit"]) != implied:
            problems.append(f"exit-outcome-conflict:exit={fields['exit']} implied={implied}")
    return {"receipt": rel, "label": label, "class": kind,
            "status": "PASS" if not problems else "FAIL",
            "fields": fields, "problems": problems}


def run(receipts, prereg):
    rows = []
    for rel, (label, kind) in sorted({**C1_RECEIPTS, **C2_RECEIPTS}.items()):
        rows.append(check(receipts, prereg, rel, label, kind))
    return rows


def selftest(prereg, scratch):
    """Four synthetic receipts, independent of the real set, so green is not vacuous."""
    results = []
    with tempfile.TemporaryDirectory(prefix="selftest-", dir=scratch) as d:
        root = pathlib.Path(d)

        def write(name, lines):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(lines) + "\n")
            return name

        def c1(outcome, exit_line=""):
            lines = [LEDGER_LINE]
            lines.append(f"ld_audit={outcome} pid=1 problems=[]")
            if exit_line:
                lines.append(exit_line)
            return lines

        def c2(met, exit_line=""):
            lines = [f"tip={'0' * 40}", f"present=1 roster_match=1 kills=1 controls=2 met={met}"]
            if exit_line:
                lines.append(exit_line)
            return lines

        cases = (
            ("T1 no-exit", write("t1/measured/build-c1.out", c1("detected")), "FAIL"),
            ("T2 contradict-exit", write("t2/measured/build-c2.out", c2("True", "exit=1")), "FAIL"),
            ("T3 matching-exit", write("t3/measured/build-c2.out", c2("True", "exit=0")), "PASS"),
            ("T4 wrong-outcome", write("t4/measured/build-c1.out", c1("missed", "exit=0")), "FAIL"),
        )
        for tag, rel, want in cases:
            kind = "c1" if rel.endswith("build-c1.out") else "c2"
            label = "round56-counter" if kind == "c1" else "build-c2"
            row = check(root, prereg, rel, label, kind)
            ok = row["status"] == want
            results.append({"test": tag, "expected": want, "observed": row["status"],
                            "problems": row["problems"], "ok": ok})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipts", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--json")
    ap.add_argument("--tsv")
    ap.add_argument("--scratch", default=tempfile.gettempdir())
    a = ap.parse_args()
    receipts = pathlib.Path(a.receipts)
    prereg = json.loads(pathlib.Path(a.prereg).read_text())
    rows = run(receipts, prereg)
    tests = selftest(prereg, a.scratch)

    width = max(len(r["receipt"]) for r in rows)
    for r in rows:
        detail = ";".join(r["problems"]) if r["problems"] else "-"
        print(f"{r['status']:4}  {r['receipt']:<{width}}  exit={r['fields'].get('exit', 'ABSENT'):<6} "
              f"outcome={r['fields'].get('ld_audit', r['fields'].get('met', 'ABSENT')):<8} {detail}")
    print()
    for t in tests:
        print(f"selftest {'PASS' if t['ok'] else 'FAIL'}  {t['test']:<18} expected={t['expected']} "
              f"observed={t['observed']} {';'.join(t['problems']) if t['problems'] else '-'}")

    if a.tsv:
        lines = ["receipt\tlabel\tclass\tstatus\texit\toutcome\tproblems"]
        for r in rows:
            lines.append("\t".join([r["receipt"], r["label"], r["class"], r["status"],
                                    r["fields"].get("exit", "ABSENT"),
                                    r["fields"].get("ld_audit", r["fields"].get("met", "ABSENT")),
                                    ",".join(r["problems"]) or "-"]))
        pathlib.Path(a.tsv).write_text("\n".join(lines) + "\n")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps({"receipts": rows, "selftests": tests}, indent=2) + "\n")

    green = all(r["status"] == "PASS" for r in rows) and all(t["ok"] for t in tests)
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
