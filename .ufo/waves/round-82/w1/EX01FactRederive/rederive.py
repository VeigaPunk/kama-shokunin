#!/usr/bin/env python3
"""EX01 independent re-derivation of the six round-81 self-record facts.

Reads ONLY committed bytes:
  * sealed record blobs via `git show 1b64f66d...:<path>`
  * the receipts the facts cite via `git show <TIP>:<path>` (TIP = master)

Never imports or reads tools/round82-selfrecord-round81.py (the object under test).
"""
import json
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SEALED = "1b64f66ddea89c57b71165eacd14b0e1d6f24e11"


def git(*args):
    return subprocess.run(["git", "-C", LANE, *args],
                          capture_output=True, text=True, check=True).stdout


def show(rev, path):
    return git("show", f"{rev}:{path}")


TIP = git("rev-parse", "master").strip()

SCORECARD = show(SEALED, "SCORECARD.md")
LOG = show(SEALED, "LOG.md")
SKILL = show(SEALED, "SKILL.md")
SOURCES = show(SEALED, "corpus/SOURCES.md")

DEBT_GREEN = show(TIP, ".ufo/waves/round-81/measured/after/debt-green.out")
GATE = show(TIP, ".ufo/waves/round-81/measured/after/gate.out")
C1_SELFTEST = show(TIP, ".ufo/waves/round-81/measured/after/c1-selftest.out")


def num(pattern, text, what):
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        raise SystemExit(f"Cannot derive {what}: pattern {pattern!r} absent")
    return m.group(1)


# ---- F1: §Round 81 C2 row, the `-> exit 0` cell's pending= value -------------
c2_line = next(ln for ln in SCORECARD.splitlines()
               if ln.startswith("| C2 — the append-only acceptance population"))
after_cell = [c for c in c2_line.split("→") if "exit 0" in c][-1]
f1_declared = int(num(r"pending=(\d+)", after_cell, "F1 declared"))
f1_observed = int(num(r"pending=(\d+)", DEBT_GREEN, "F1 observed"))

# ---- F2: LOG §Round 81 `Frontier: registry 297 -> <n> rows` ------------------
log81 = LOG[LOG.index("## Round 81 — the round-80 record is graded"):]
f2_declared = int(num(r"Frontier: registry 297 → (\d+) rows", log81, "F2 declared"))
S_ROW = re.compile(r"^ {0,3}\| *S[0-9]+ *\|")
f2_sealed_count = sum(1 for ln in SOURCES.splitlines() if S_ROW.match(ln))
f2_tip_count = sum(1 for ln in show(TIP, "corpus/SOURCES.md").splitlines()
                   if S_ROW.match(ln))
f2_base_count = sum(1 for ln in show("aaf974dbd3b6adb2ef914dc7293cda92b4e05551",
                                     "corpus/SOURCES.md").splitlines()
                    if S_ROW.match(ln))
f2_observed = f2_sealed_count          # witness: registry count at the sealed record tip

# ---- F3: SKILL pre-report-gate row `(ten arms, ...)` ------------------------
skill_row = next(ln for ln in SKILL.splitlines()
                 if ln.startswith("| Pre-report gate |"))
WORD = {"ten": 10, "eleven": 11, "twelve": 12}
m = re.search(r"\((ten|eleven|twelve|(\d+)) arms", skill_row)
if not m:
    raise SystemExit("Cannot derive F3 declared: no '(<n> arms' in SKILL row")
f3_declared = WORD.get(m.group(1)) or int(m.group(2))
f3_observed = int(num(r"^PRE_REPORT round=81 arms=(\d+) ", GATE, "F3 observed"))

# ---- F4: `## Axes` calibration row's "newest non-author closure" -----------
ax = SCORECARD[SCORECARD.index("\n## Axes"):]
calib_row = next(ln for ln in ax.splitlines()
                 if ln.startswith("| calibration | **7**"))
f4_declared = re.search(r"the newest non-author closure is `([^`]+)`",
                        calib_row).group(1)
spotchecks = [p for p in git("ls-tree", "-r", "--name-only", TIP, "corpus/lessons/").splitlines()
              if re.fullmatch(r"corpus/lessons/round-\d+-verifier-spotcheck\.md", p)]
newest = max(spotchecks, key=lambda p: int(re.search(r"round-(\d+)-", p).group(1)))
f4_observed = newest.rsplit("/", 1)[-1]

# ---- F5: LOG `LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=<n>` ----
f5_declared = int(num(r"LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=(\d+)",
                      LOG, "F5 declared"))
f5_observed = int(num(r"pending=(\d+)", DEBT_GREEN, "F5 observed"))

# ---- F6: §Round 81 C1 row's `pass=<n> fail=0` ------------------------------
c1_line = next(ln for ln in SCORECARD.splitlines()
               if ln.startswith("| C1 — the round-80 self-record's six declared facts"))
f6_declared = int(num(r"`pass=(\d+) fail=0`", c1_line, "F6 declared"))
f6_observed = int(num(r"pass=(\d+) fail=0", C1_SELFTEST, "F6 observed"))

facts = [
    {"id": "F1", "location": "SCORECARD.md §Round 81 C2 row, `-> exit 0` cell `pending=`",
     "declared_token": f"sc81c2-pending={f1_declared}", "declared": f1_declared,
     "observed": f1_observed,
     "witness": ".ufo/waves/round-81/measured/after/debt-green.out `pending=`",
     "stale": f1_declared != f1_observed},
    {"id": "F2", "location": "LOG.md §Round 81 `Frontier: registry 297 -> <n> rows`",
     "declared_token": f"log81-frontier-rows={f2_declared}", "declared": f2_declared,
     "observed": f2_observed,
     "witness": "corpus/SOURCES.md S-row count (regex ^ {0,3}\\| *S[0-9]+ *\\|)",
     "stale": f2_declared != f2_observed,
     "tip_disclosure": {"sealed_count": f2_sealed_count, "base_count": f2_base_count,
                        "tip_count": f2_tip_count}},
    {"id": "F3", "location": "SKILL.md pre-report-gate row `(ten arms, ...)`",
     "declared_token": f"skill81-gate-arms={f3_declared}", "declared": f3_declared,
     "observed": f3_observed,
     "witness": ".ufo/waves/round-81/measured/after/gate.out `arms=`",
     "stale": f3_declared != f3_observed},
    {"id": "F4", "location": "SCORECARD.md `## Axes` calibration row, newest non-author closure",
     "declared_token": f"calib81-newest-closure={f4_declared.rsplit(chr(47), 1)[-1]}", "declared": f4_declared,
     "observed": f4_observed,
     "witness": "newest corpus/lessons/round-*-verifier-spotcheck.md at the tip",
     "stale": f4_declared != f4_observed},
    {"id": "F5", "location": "LOG.md `LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=<n>`",
     "declared_token": f"logcorr81-c2-pending={f5_declared}", "declared": f5_declared,
     "observed": f5_observed,
     "witness": ".ufo/waves/round-81/measured/after/debt-green.out `pending=`",
     "stale": f5_declared != f5_observed},
    {"id": "F6", "location": "SCORECARD.md §Round 81 C1 row `pass=<n> fail=0`",
     "declared_token": f"sc81c1-selftest={f6_declared}", "declared": f6_declared,
     "observed": f6_observed,
     "witness": ".ufo/waves/round-81/measured/after/c1-selftest.out `pass=`",
     "stale": f6_declared != f6_observed},
]

out = {"lane": LANE, "sealed": SEALED, "tip": TIP,
       "facts": facts,
       "stale_count": sum(1 for f in facts if f["stale"]),
       "holding_count": sum(1 for f in facts if not f["stale"])}
print(json.dumps(out, indent=1))
with open("EX01.json", "w") as fh:
    json.dump(out, fh, indent=1)
print(f"EX01_REDERIVE claims=6 stale={out['stale_count']} "
      f"holding={out['holding_count']}", file=sys.stderr)
