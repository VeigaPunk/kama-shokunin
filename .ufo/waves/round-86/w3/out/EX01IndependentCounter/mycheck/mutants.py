#!/usr/bin/env python3
"""Independent C2 re-derivation: apply the five declared source edits to the
committed bytes at rev, run the selftest, and classify which arm/side turns red."""
import json, os, re, subprocess, sys

repo = sys.argv[1]; rev = sys.argv[2]; work = sys.argv[3]
SOURCE = "tools/round81-append-debt.py"

CONDITION = "subject_round is not None and deletion != subject_round"
CONTINUE_BLOCK = ('            bad("note-wrong-deletion-round", f"{detail}: note deletion round {deletion} "\n'
                  '                                             f"differs from subject round {subject_round}")\n'
                  "            continue")
ARM_LINE = '    cases.append(("note-deletion-equals-subject", r, 0, None))\n'
SUMMARY_PASS = "pass={len(cases) - fail}"
SUMMARY_FAIL = "fail={fail}"

MU = (
    ("M2", CONDITION, "subject_round is not None and deletion != accepting"),
    ("M3", CONDITION, "subject_round is not None and deletion < subject_round"),
    ("M4", CONTINUE_BLOCK, CONTINUE_BLOCK.rsplit("\n", 1)[0]),
    ("M5", ARM_LINE, ""),
    ("M6", SUMMARY_PASS, "pass=0"),
)
# M6 additionally forges fail=0 in the summary line (two edits in the frozen instrument).
M6 = ("<M6F", SUMMARY_FAIL, "fail=0")

src = subprocess.check_output(["git", "-C", repo, "show", f"{rev}:{SOURCE}"], text=True)
SUMMARY_RE = re.compile(r"^APPEND_DEBT_SELFTEST pass=([0-9]+) fail=([0-9]+)(?: arms=([0-9]+))?$", re.M)
ARMS_RE = re.compile(r"^APPEND_DEBT_SELFTEST_ARMS arms=([0-9]+) expected=([0-9]+) fail_lines=([0-9]+)$", re.M)
FAIL_RE = re.compile(r"^APPEND_DEBT_SELFTEST_FAIL (\S+) ", re.M)

def run(src_text, name):
    p = os.path.join(work, name + ".py")
    open(p, "w", encoding="utf-8").write(src_text)
    r = subprocess.run([sys.executable, p, "--selftest"], text=True, capture_output=True,
                       env={**os.environ, "TMPDIR": work}, timeout=600)
    return r

out = {}
for mid in ("pristine", "M2", "M3", "M4", "M5", "M6", "M6f"):
    text = src
    if mid == "M6":
        text = src.replace(SUMMARY_PASS, "pass=0").replace(SUMMARY_FAIL, "fail=0")
    elif mid == "M6f":
        text = src.replace(SUMMARY_PASS, "pass=0")
    elif mid == "pristine":
        pass
    else:
        old, new = next((o, n) for m, o, n in MU if m == mid)
        c = text.count(old)
        if c != 1:
            out[mid] = {"invalid": f"site count {c}"}
            continue
        text = text.replace(old, new)
    r = run(text, mid)
    rec = {"rc": r.returncode, "stderr": r.stderr.strip()[:120],
           "fails": FAIL_RE.findall(r.stdout), "arms": ARMS_RE.findall(r.stdout),
           "summaries": SUMMARY_RE.findall(r.stdout)}
    out[mid] = rec
    print(mid, "rc=%d" % r.returncode, "fails=%s" % rec["fails"], "arms=%s" % rec["arms"],
          "summaries=%s" % rec["summaries"], "stderr=%r" % rec["stderr"])
json.dump(out, open(os.path.join(work, "mutants.json"), "w"), indent=1)
