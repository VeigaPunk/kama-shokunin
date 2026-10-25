#!/usr/bin/env python3
"""R41B02 probe: tools/pin-watch.py (tip) vs frozen contract/reference in
tools/round41-pinwatch-audit.py. Runs edge cases offline (--tags-dir) and
byte-compares tool output/exit against the audit's reference implementation."""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "pin-watch.py")

spec = importlib.util.spec_from_file_location("audit", os.path.join(HERE, "audit.py"))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

HDR = "engine\trepo\ttag_regex\tpin\tsource"
SEM = r"v(\d+)\.(\d+)\.(\d+)"
SHA = "0" * 40


def tagsfile(pairs):
    return "".join(f"{SHA}\trefs/tags/{n}\n" for n in pairs)


CASES = [
    # (name, pins_rows, tags_by_engine, pins_bytes_override)
    ("tie_keys_newer", [dict(engine="e", regex=SEM, pin="v01.2.3")],
     {"e": tagsfile(["v1.2.3", "v01.2.3", "v1.10.0"])}, None),
    ("tie_keys_newest_tiebreak", [dict(engine="e", regex=SEM, pin="v01.2.3")],
     {"e": tagsfile(["v1.2.3", "v01.2.3"])}, None),
    ("empty_taglist", [dict(engine="e", regex=SEM, pin="v1.0.0")],
     {"e": ""}, None),
    ("empty_pins_header_only", [], {}, None),
    ("crlf_pins", [dict(engine="e", regex=SEM, pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3", "v1.3.0"])}, None),
    ("crlf_tags", [dict(engine="e", regex=SEM, pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3", "v1.3.0"]).replace("\n", "\r\n")}, None),
    ("space_engine_cell", [dict(engine=" e ", regex=SEM, pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3"])}, None),
    ("space_pin_cell", [dict(engine="e", regex=SEM, pin=" v1.2.3 ")],
     {"e": tagsfile(["v1.2.3"])}, None),
    ("space_regex_cell", [dict(engine="e", regex=" " + SEM + " ", pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3"])}, None),
    ("comment_lines", [dict(engine="e", regex=SEM, pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3"])}, None),
    ("indented_comment", [dict(engine="e", regex=SEM, pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3"])}, None),
    ("nondigit_group", [dict(engine="e", regex=r"v(\w+)", pin="valpha")],
     {"e": tagsfile(["valpha", "v12"])}, None),
    ("dup_engine", [dict(engine="e", regex=SEM, pin="v1.2.3"),
                    dict(engine="e", regex=SEM, pin="v1.3.0")],
     {"e": tagsfile(["v1.2.3", "v1.3.0"])}, None),
]

PINS_OVERRIDE = {
    "crlf_pins": (HDR + "\r\ne\trepo\t" + SEM + "\tv1.2.3\tS000\r\n").encode(),
    "comment_lines": ("# chosen by round 41\n" + HDR + "\n# tool row\n"
                      "e\trepo\t" + SEM + "\tv1.2.3\tS000\n# trailing\n").encode(),
    "indented_comment": (HDR + "\n # x\n" + "e\trepo\t" + SEM + "\tv1.2.3\tS000\n").encode(),
}


def build(tmp, name, rows, tags):
    d = os.path.join(tmp, name)
    os.makedirs(os.path.join(d, "tags"))
    if name in PINS_OVERRIDE:
        data = PINS_OVERRIDE[name]
    else:
        text = HDR + "\n" + "".join(
            "\t".join([r["engine"], "repo", r["regex"], r["pin"], "S000"]) + "\n"
            for r in rows)
        data = text.encode()
    with open(os.path.join(d, "pins.tsv"), "wb") as fh:
        fh.write(data)
    for eng, t in tags.items():
        with open(os.path.join(d, "tags", f"{eng.strip()}.txt"), "w") as fh:
            fh.write(t)
    return d


def run_tool(pins, tagsdir):
    p = subprocess.run([sys.executable, TOOL, "check", "--pins", pins,
                        "--tags-dir", tagsdir], capture_output=True, text=True,
                       timeout=60, cwd=HERE)
    return p.stdout, p.stderr, p.returncode


def run_reference(pins_path, rows, tags):
    # exactly the audit's live leg: parse the file text, texts keyed by parsed engine
    try:
        rows = audit.parse_pins(open(pins_path).read())
    except ValueError as e:
        return f"parse_pins ValueError: {e}", None
    texts = {}
    for r in rows:
        raw = r["engine"].strip()
        p = os.path.join(os.path.dirname(pins_path), "tags", f"{raw}.txt")
        texts[r["engine"]] = open(p).read() if os.path.exists(p) else None
    try:
        want, wcode = audit.reference(rows, texts)
    except ValueError as e:
        return f"reference ValueError: {e}", None
    return "\n".join(want), wcode


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, rows, tags, _ov in CASES:
            d = build(tmp, name, rows, tags)
            so, se, rc = run_tool(os.path.join(d, "pins.tsv"), os.path.join(d, "tags"))
            ref, rrc = run_reference(os.path.join(d, "pins.tsv"), rows, tags)
            tool_lines = [l for l in so.splitlines() if l.strip()]
            errored = isinstance(ref, str) and ref.startswith(("parse_pins", "reference"))
            agree = (not errored and tool_lines == ref.splitlines() and rc == rrc)
            status = "AGREE" if agree else "DIVERGE"
            print(f"=== {name}: {status}")
            print(f"  tool  exit={rc}")
            for l in tool_lines:
                print(f"    {l}")
            if se.strip():
                print(f"  tool stderr: {se.strip().splitlines()[-1]}")
            if errored:
                print(f"  reference: {ref} (no output, exit n/a)")
            else:
                print(f"  reference exit={rrc}")
                for l in ref.splitlines():
                    print(f"    {l}")
            if not agree:
                failures.append(name)
        print(f"\nSUMMARY: {len(CASES) - len(failures)} agree, {len(failures)} diverge: {failures}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
