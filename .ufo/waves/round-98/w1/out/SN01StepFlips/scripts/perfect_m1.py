#!/usr/bin/env python3
"""SN01StepFlips - the decisive falsification: build a "perfect M1" and run the FROZEN C1.

The scratch clone gets every SKILL.md / SCORECARD.md surface that C1 checks 16, 19, 20 grade
updated to the values the plan wants (five graded forgeries, W14-W19 named, overcharge named,
six new cells, eight boundary rows, S622 cited, updated sha/lines). Then the FROZEN
round98-self-assessment-audit.py is run at that commit.

If C1 still reports mismatches>0, the remaining mismatch is not repairable by editing the
surfaces the counter grades - it lives in a term that depends on the OTHER frozen counter's
bytes (the budget counter, pinned by C2 kill rule K1).

Nothing in the lane repo is touched: the clone lives in the scratch dir.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path(sys.argv[1]).resolve()
CLONE = SCRATCH / "clone-perfect-m1"
CELLS = ["W14-900k-nd1", "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1",
         "W18-800k-nd1", "W19-520k-nd4"]

if CLONE.exists():
    shutil.rmtree(CLONE)
CLONE.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["git", "clone", "--shared", "-q", str(LANE), str(CLONE)], check=True)
toplevel = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
assert toplevel == str(CLONE), f"clone toplevel {toplevel} != {CLONE}"
print("clone toplevel asserted:", toplevel)

# ---------------------------------------------------------------- SKILL.md
skill = CLONE / "SKILL.md"
text = skill.read_text()
orig_heading = "### Round 97 correction (step-budget boundary table and the three graded forgeries; dated 2026-11-08)"
assert orig_heading in text
text = text.replace(
    orig_heading,
    "### Round 97 correction (step-budget boundary table and the five graded forgeries; dated 2026-11-08)")
text = text.replace(
    "The six rows below are the two boundary classes the round-96 table does not name:",
    "The eight rows below are the two boundary classes the round-96 table does not name:")
# add the two new boundary rows after the 555,556 nd=4 row
old_row = "| 555,556 | nd=4 | 5,000,008 | > budget | - |\n"
assert old_row in text
text = text.replace(old_row, old_row +
                    "| 800,000 | nd=1 | 4,800,004 | <= budget | invalid |\n"
                    "| 520,000 | nd=4 | 4,680,004 | <= budget | invalid |\n")
# body prose: five probe variants, name W14-W19, the overcharge mutant, S620/S621/S622
old_prose = "four probe variants survive all 13 of its cells"
assert old_prose in text
text = text.replace(old_prose, "five probe variants survive all 13 of its cells")
old_tail = ("The round-97 counter `tools/round97-router-budget.py` grades each with\n"
            "W14-900k-nd1, W15-700k-nd4, W16-maxmeta and W17-833333-nd1 respectively. Sourced on S620 "
            "(GGUF spec, ggml `57e2c2ca`: `gguf_tensor_info_t` carries `name`,\n"
            "`n_dimensions`, `dimensions[n_dimensions]`, `type`, `offset` — the five fields the probe prices)\n"
            "and S621 (supersedes S618's constant-6 cell; the `5 + nd` arithmetic above).")
assert old_tail in text, "tail prose anchor not found"
new_tail = ("The round-98 counter `tools/round98-router-budget.py` grades each with\n"
            "W14-900k-nd1, W15-700k-nd4, W16-maxmeta, W17-833333-nd1, W18-800k-nd1 and W19-520k-nd4\n"
            "respectively; the overcharge mutant (one extra step per header) is caught by W18-800k-nd1\n"
            "and W19-520k-nd4. Sourced on S620 (GGUF spec, ggml `57e2c2ca`: `gguf_tensor_info_t` carries\n"
            "`name`, `n_dimensions`, `dimensions[n_dimensions]`, `type`, `offset` — the five fields the\n"
            "probe prices), S621 (supersedes S618's constant-6 cell; the `5 + nd` arithmetic above) and\n"
            "S622 (the spec's `gguf_header_t`: magic, version, tensor_count, metadata_kv_count — the four\n"
            "preamble fields, so the preamble costs 4 steps).")
text = text.replace(old_tail, new_tail)
skill.write_text(text)
print("SKILL.md edited")

# ---------------------------------------------------------------- SCORECARD.md
score = CLONE / "SCORECARD.md"
stext = score.read_text()
skill_sha = hashlib.sha256(text.encode()).hexdigest()
skill_lines = len(text.splitlines())
skill_sections = sum(1 for l in text.splitlines() if l.startswith("## "))
lines = stext.splitlines()
depth_idx = next(i for i, l in enumerate(lines) if l.startswith("| depth |"))
depth = lines[depth_idx]
new_depth = depth
new_depth = re.sub(r"sha256 `[0-9a-f]{64}`", f"sha256 `{skill_sha}`", new_depth)
new_depth = re.sub(r"\(\d+ lines\)", f"({skill_lines} lines)", new_depth)
new_depth = re.sub(r"grep -c '\^## ' SKILL\.md` → `\d+`",
                    f"grep -c '^## ' SKILL.md` → `{skill_sections}`", new_depth)
new_depth = new_depth.replace(
    "the four graded probe forgeries W14-900k-nd1, W15-700k-nd4, W16-maxmeta and W17-833333-nd1",
    "the five graded probe forgeries W14-900k-nd1, W15-700k-nd4, W16-maxmeta, W17-833333-nd1, "
    "W18-800k-nd1 and W19-520k-nd4, plus the overcharge mutant")
lines[depth_idx] = new_depth
score.write_text("\n".join(lines) + "\n")
print("SCORECARD.md depth row updated; skill_sha", skill_sha[:16],
      "lines", skill_lines, "sections", skill_sections)

# ---------------------------------------------------------------- commit
env = dict(os.environ, GIT_AUTHOR_NAME="SN01StepFlips", GIT_AUTHOR_EMAIL="sn01@localhost",
           GIT_COMMITTER_NAME="SN01StepFlips", GIT_COMMITTER_EMAIL="sn01@localhost")
subprocess.run(["git", "-C", str(CLONE), "add", "-A"], check=True, env=env)
subprocess.run(["git", "-C", str(CLONE), "commit", "-q", "-m",
                "scratch: perfect-M1 surfaces for C1 falsification test"], check=True, env=env)
rev = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"],
                     capture_output=True, text=True).stdout.strip()
print("scratch commit:", rev)

# ---------------------------------------------------------------- run the FROZEN counters
for tool in ("round98-self-assessment-audit.py", "round98-depth-boundary-audit.py"):
    p = subprocess.run([sys.executable, str(LANE / "tools" / tool),
                        "--repo", str(CLONE), "--rev", rev],
                       capture_output=True, text=True)
    print(f"\n=== {tool} at the perfect-M1 clone ===")
    print(p.stdout.strip())
    if p.stderr.strip():
        print("stderr:", p.stderr.strip()[-800:])
    print("exit =", p.returncode)
