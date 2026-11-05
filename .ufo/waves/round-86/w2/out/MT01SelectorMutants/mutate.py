#!/usr/bin/env python3
"""MT01 selector mutants: apply five single-site mutants to round86-rendered-cells.py
copies and run the instrument's own --selftest on each. Read-only w.r.t. the lane."""
import hashlib
import os
import subprocess
import sys

D = "/fast/scratch/hyaku/kama-r86/MT01SelectorMutants"
BASE = os.path.join(D, "base", "round86-rendered-cells.py")

FENCE_BLOCK = '''        opener = FENCE.match(line)
        if opener:
            fence = (opener.group(1)[0], len(opener.group(1)))
            continue
'''
COMMENT_BLOCK = '''        while "<!--" in line:
            before, rest = line.split("<!--", 1)
            if "-->" in rest:
                line = before + rest.split("-->", 1)[1]
            else:
                line = before
                in_comment = True
                break
'''
CORRECTION_BLOCK = '''        heading = CORRECTION.match(line)
        if heading:
            depth = len(heading.group(1))
            continue
'''
COUPLE_BLOCK = '''    coupled = []
    for revision in revisions:
        if not tree.ancestor(revision):
            continue
        for path in receipts:
            text = tree.blob(path) if path in tree.paths() else None
            if text is not None and token.group(0).strip("`") in text:
                coupled.append((revision, path))
    if not coupled:
'''
COUPLE_REPLACEMENT = '''    coupled = [revision for revision in revisions if tree.ancestor(revision)]
    if not coupled:
'''
AUTHORITY_COL0 = r'AUTHORITY = re.compile(r"^\*\*Current authority \(round ([0-9]+)\):")'
AUTHORITY_ANYINDENT = r'AUTHORITY = re.compile(r"^\s*\*\*Current authority \(round ([0-9]+)\):")'
CALIB_COL0 = r'CALIBRATION = re.compile(r"^\|\s*calibration\s*\|")'
CALIB_ANYINDENT = r'CALIBRATION = re.compile(r"^\s*\|\s*calibration\s*\|")'

MUTANTS = {
    "a-fence-exclusion-off": ("(a) fence exclusion disabled: opener detection block deleted "
                              "so no fence is ever tracked", FENCE_BLOCK, ""),
    "b-comment-exclusion-off": ("(b) HTML-comment exclusion disabled: <!-- strip block deleted "
                                "so in_comment can never arm", COMMENT_BLOCK, ""),
    "c-correction-exclusion-off": ("(c) round-N correction block exclusion disabled: CORRECTION "
                                   "match block deleted so depth is never set", CORRECTION_BLOCK, ""),
    "d-column0-relaxed": ("(d) column-0 requirement relaxed: AUTHORITY regex anchored with \\s*",
                          AUTHORITY_COL0, AUTHORITY_ANYINDENT),
    "e-gate-coupling-to-revision-only": ("(e) coupled gate fact reduced to 'revision present': "
                                         "receipt-bytes membership test dropped", COUPLE_BLOCK,
                                         COUPLE_REPLACEMENT),
}
EXTRA = {
    "d2-calibration-column0-relaxed": ("(d2) extra probe: CALIBRATION regex column-0 relaxed "
                                       "to any indentation", CALIB_COL0, CALIB_ANYINDENT),
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def build(name, old, new, text):
    hits = text.count(old)
    if hits != 1:
        raise SystemExit(f"{name}: expected exactly 1 site, found {hits}")
    out = text.replace(old, new)
    path = os.path.join(D, "mutants", name + ".py")
    with open(path, "w") as handle:
        handle.write(out)
    return path


def run(path):
    proc = subprocess.run([sys.executable, path, "--selftest"], cwd=os.path.dirname(path),
                          capture_output=True, text=True, env={**os.environ, "TMPDIR": D})
    return proc.returncode, proc.stdout, proc.stderr


def main():
    text = open(BASE).read()
    before = sha(BASE)
    print(f"BASE sha256={before} bytes={len(text)}")
    results = {}
    for name, (desc, old, new) in {**MUTANTS, **EXTRA}.items():
        path = build(name, old, new, text)
        code, out, err = run(path)
        red = [line.split()[1] for line in out.splitlines()
               if line.startswith("RENDERED_CELLS_SELFTEST_FAIL")]
        summary = [line for line in out.splitlines()
                   if line.startswith("RENDERED_CELLS_SELFTEST pass=")]
        results[name] = (desc, code, red, summary, sha(path))
        print(f"\n=== {name}: {desc}")
        print(f"mutant sha256={results[name][4]} selftest_exit={code} red_arms={red or 'NONE'}")
        print(f"summary={summary[0] if summary else 'NO SUMMARY LINE'}")
        if err.strip():
            print(f"stderr={err.strip()}")
    after = sha(BASE)
    print(f"\nBASE_AFTER sha256={after} restored={'yes' if after == before else 'NO'}")
    for name, (desc, code, red, summary, msha) in results.items():
        print(f"VERDICT {name} exit={code} red={len(red)} "
              f"{'CAUGHT ' + ','.join(red) if red else 'SURVIVED'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
