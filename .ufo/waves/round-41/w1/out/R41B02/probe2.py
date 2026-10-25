#!/usr/bin/env python3
"""R41B02 supplementary probes: duplicate tag lines, zero-group regex,
3-field tag line. Same tool-vs-reference byte compare as probe.py."""
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
    ("dup_tag_lines", [dict(engine="e", regex=SEM, pin="v1.2.3")],
     {"e": tagsfile(["v1.2.3"]) + tagsfile(["v1.2.3"]) + tagsfile(["v1.3.0"])}),
    ("zero_group_regex", [dict(engine="e", regex=r"v\d+\.\d+", pin="v1.2")],
     {"e": tagsfile(["v1.2", "v1.10"])}),
    ("three_field_tagline", [dict(engine="e", regex=SEM, pin="v1.2.3")],
     {"e": f"{SHA}\trefs/tags/v1.2.3\tjunk\n{SHA}\trefs/tags/v1.3.0\n"}),
]


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, rows, tags in CASES:
            d = os.path.join(tmp, name)
            os.makedirs(os.path.join(d, "tags"))
            with open(os.path.join(d, "pins.tsv"), "w") as fh:
                fh.write(HDR + "\n" + "".join(
                    "\t".join([r["engine"], "repo", r["regex"], r["pin"], "S000"]) + "\n"
                    for r in rows))
            for eng, t in tags.items():
                with open(os.path.join(d, "tags", f"{eng}.txt"), "w") as fh:
                    fh.write(t)
            p = subprocess.run([sys.executable, TOOL, "check", "--pins",
                                os.path.join(d, "pins.tsv"), "--tags-dir",
                                os.path.join(d, "tags")], capture_output=True,
                               text=True, timeout=60, cwd=HERE)
            tool_lines = [l for l in p.stdout.splitlines() if l.strip()]
            parsed = audit.parse_pins(open(os.path.join(d, "pins.tsv")).read())
            texts = {r["engine"]: open(os.path.join(d, "tags", f"{r['engine']}.txt")).read()
                     for r in parsed}
            try:
                ref, rrc = audit.reference(parsed, texts)
                refok = True
            except ValueError as e:
                ref, rrc, refok = f"reference ValueError: {e}", None, False
            agree = refok and tool_lines == ref and p.returncode == rrc
            print(f"=== {name}: {'AGREE' if agree else 'DIVERGE'}")
            print(f"  tool exit={p.returncode}")
            for l in tool_lines:
                print(f"    {l}")
            if p.stderr.strip():
                print(f"  tool stderr: {p.stderr.strip().splitlines()[-1]}")
            if refok:
                print(f"  reference exit={rrc}")
                for l in ref:
                    print(f"    {l}")
            else:
                print(f"  reference: {ref}")
            if not agree:
                failures.append(name)
    print(f"\nSUMMARY: {len(CASES)-len(failures)} agree, {len(failures)} diverge: {failures}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
