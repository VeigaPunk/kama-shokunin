#!/usr/bin/env python3
"""Round-86 C1 mutant driver: every declared source mutation of
tools/round86-rendered-cells.py must turn its own declared selftest arm red.

Usage: TMPDIR=<scratch> python3 c1-mutants.py [<lane repo>]
Prints one line per mutant and a `RENDERED_CELLS_MUTANTS mutants=8 killed=8 escaped=0` summary.
"""
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
MUTANTS = {
    "a-fence-off": (
        "        opener = FENCE.match(line)\n        if opener:\n"
        "            fence = (opener.group(1)[0], len(opener.group(1)))\n            continue\n", ""),
    "b-comment-off": (
        '        while "<!--" in line:\n            before, rest = line.split("<!--", 1)\n'
        '            if "-->" in rest:\n                line = before + rest.split("-->", 1)[1]\n'
        '            else:\n                line = before\n                in_comment = True\n'
        '                break\n', ""),
    "c-correction-off": (
        "        heading = CORRECTION.match(line)\n        if heading:\n"
        "            depth = len(heading.group(1))\n            continue\n", ""),
    "d-authority-indent": (
        'AUTHORITY = re.compile(r"^\\*\\*Current authority \\(round ([0-9]+)\\):")',
        'AUTHORITY = re.compile(r"^\\s*\\*\\*Current authority \\(round ([0-9]+)\\):")'),
    "d2-row-indent": (
        'CALIBRATION = re.compile(r"^\\|\\s*calibration\\s*\\|")',
        'CALIBRATION = re.compile(r"^\\s*\\|\\s*calibration\\s*\\|")'),
    "f-tilde-off": (
        'FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")',
        'FENCE = re.compile(r"^ {0,3}(`{3,})(.*)$")'),
    "e-receipt-bytes-off": (
        "    coupled = []\n    for revision in revisions:\n"
        "        if not tree.ancestor(revision):\n            continue\n"
        "        text = tree.blob_at(revision, receipt_path)\n"
        '        if text is not None and token.group(0).strip("`") in text:\n'
        "            coupled.append((revision, receipt_path))",
        "    coupled = [(r, receipt_path) for r in revisions if tree.ancestor(r)]"),
    "g-newest-path-off": ("    if receipt_path not in receipts:", "    if False:"),
}


def main():
    source = (REPO / "tools/round86-rendered-cells.py").read_text(encoding="utf-8")
    killed = 0
    with tempfile.TemporaryDirectory(dir=None) as work:
        for name, (old, new) in MUTANTS.items():
            assert source.count(old) == 1, f"{name}: mutation site count {source.count(old)}"
            path = pathlib.Path(work) / f"{name}.py"
            path.write_text(source.replace(old, new), encoding="utf-8")
            run = subprocess.run([sys.executable, str(path), "--selftest"], text=True,
                                 capture_output=True)
            red = [line.split()[1] for line in run.stdout.splitlines() if "SELFTEST_FAIL" in line]
            killed += 1 if run.returncode == 1 else 0
            print(f"{name}: exit={run.returncode} red_arms={','.join(red) if red else '-'}")
    print(f"RENDERED_CELLS_MUTANTS mutants={len(MUTANTS)} killed={killed} "
          f"escaped={len(MUTANTS) - killed}")
    return 0 if killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
