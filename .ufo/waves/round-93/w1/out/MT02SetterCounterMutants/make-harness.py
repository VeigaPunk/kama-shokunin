#!/usr/bin/env python3
"""Build the MT02 mutation harness from committed bytes.

- c2-forgeries-MT02.py : byte copy of controls/c2-forgeries.py with exactly two changes:
  (1) `COUNTER = os.environ.get("C2_COUNTER", "tools/round93-setter-rows.py")` added;
  (2) the counter path in the subprocess argv comes from COUNTER.
  Every case, mutation and expected string is untouched.
- mutants/NN-name.py : single-point mutants of tools/round93-setter-rows.py at M2
  (ee19acbdabc8ac572e82ae56459c364457895b06), plus mutants/m2-counter.py (control copy).
- mutants/manifest.tsv : id, description, sha256, edit.

Run from anywhere; paths below are absolute.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-93/w1/out/MT02SetterCounterMutants")
M2 = "ee19acbdabc8ac572e82ae56459c364457895b06"
COUNTER_SHA = "367eed2f16d4d240170ed0bc8c96f6a9c6f1c2593b2b380e4f467e963f0ea185"

base = subprocess.run(["git", "-C", str(LANE), "show", f"{M2}:tools/round93-setter-rows.py"],
                      capture_output=True, check=True).stdout
sha = hashlib.sha256(base).hexdigest()
assert sha == COUNTER_SHA, (sha, COUNTER_SHA)
text = base.decode()

# ---- battery copy ---------------------------------------------------------
bat = (LANE / ".ufo/waves/round-93/controls/c2-forgeries.py").read_text()
edits = [
    ("import re\nimport subprocess\nimport sys\nfrom pathlib import Path\n",
     "import os\nimport re\nimport subprocess\nimport sys\nfrom pathlib import Path\n"),
    ('BASE = "5af794958b0fc08f574aa2e67650282269549b02"\n',
     'BASE = "5af794958b0fc08f574aa2e67650282269549b02"\n'
     'COUNTER = os.environ.get("C2_COUNTER", "tools/round93-setter-rows.py")\n'),
    ("    p = subprocess.run([sys.executable, \"tools/round93-setter-rows.py\", \"--repo\", \".\", \"--rev\", BASE,",
     "    p = subprocess.run([sys.executable, COUNTER, \"--repo\", \".\", \"--rev\", BASE,"),
]
for old, new in edits:
    assert bat.count(old) == 1, old
    bat = bat.replace(old, new)
(out_dir := OUT).mkdir(parents=True, exist_ok=True)
(OUT / "c2-forgeries-MT02.py").write_text(bat)
(OUT / "mutants").mkdir(exist_ok=True)
(OUT / "logs").mkdir(exist_ok=True)

# ---- mutants: (id, description, old, new) one contiguous single-point edit each
M = [
    ("01-popre-narrowed",
     "POP_RE drops AIP_HTTP_PORT (population no longer sees AIP-only lines)",
     "|AIP_HTTP_PORT')\nPORT_TOK", "')\nPORT_TOK"),
    ("02-tok-swap",
     "PORT_TOK and NP_TOK regex bodies swapped",
     "PORT_TOK = re.compile(r'\\bport\\s*=[^=]|LLAMA_ARG_PORT|\"--port\"|AIP_HTTP_PORT')\n"
     "NP_TOK = re.compile(r'\\bn_parallel\\s*=[^=]|LLAMA_ARG_N_PARALLEL|\"--parallel\"')",
     "PORT_TOK = re.compile(r'\\bn_parallel\\s*=[^=]|LLAMA_ARG_N_PARALLEL|\"--parallel\"')\n"
     "NP_TOK = re.compile(r'\\bport\\s*=[^=]|LLAMA_ARG_PORT|\"--port\"|AIP_HTTP_PORT')"),
    ("03-int-rhs-dropped",
     "B5 integer-literal comparison against INT_RHS removed",
     "        if m and value != m.group(1):\n            return False, \"value-literal\", 0, 0, key\n",
     ""),
    ("04-text-substring",
     "B2 exact text equality relaxed to substring (t in line)",
     "    if t != line.strip():\n",
     "    if t not in line:\n"),
    ("05-source-check-removed",
     "B6 source-row lookup and /b12177/<file> containment check removed",
     "    row = srcs.get(src)\n"
     "    if row is None or not any(f\"/b12177/{f}\" in c for c in row):\n"
     "        return False, \"source\", 0, 0, key\n",
     ""),
    ("06-scope-check-removed",
     "B7 derived set_examples scope comparison removed (option check kept)",
     "            if [x.strip() for x in scope.split(\",\")] != ex:\n                disagree += 1\n",
     ""),
    ("07-opt-index-last",
     "arg_block returns the last long option instead of the first",
     "    return (opts[0] if opts else None), ex\n",
     "    return (opts[-1] if opts else None), ex\n"),
    ("08-decision-names-removed",
     "R16/R17 decision cell no longer must name every overriding row",
     "            elif any(not re.search(r\"\\b\" + re.escape(x) + r\"\\b\", dec) for x in want):\n"
     "                why = \"decision-names\"\n",
     ""),
    ("09-override-set-want-subset",
     "overriding-set equality relaxed to want <= got (extra ids accepted)",
     "            elif got != want or not want:\n",
     "            elif not want or not want.issubset(got):\n"),
    ("10-override-set-got-subset",
     "overriding-set equality relaxed to got <= want (missing ids accepted)",
     "            elif got != want or not want:\n",
     "            elif not want or not got.issubset(want):\n"),
    ("11-min-pop-1",
     "MIN_POP lowered 40 -> 1",
     "MIN_POP = 40\n",
     "MIN_POP = 1\n"),
    ("12-duplicate-removed",
     "one-row-per-key duplicate detection removed",
     "    if key in seen:\n        return False, \"duplicate\", 0, 0, key\n",
     ""),
    ("13-unrelated-pairing-removed",
     "B4 parameter '-' <=> effect 'unrelated' pairing check removed",
     "    if (param == \"-\") != (effect == \"unrelated\"):\n"
     "        return False, \"unrelated-pairing\", 0, 0, key\n",
     ""),
    ("14-np-token-removed",
     "B3 n_parallel token cross-check removed (port check kept)",
     "    if param == \"n_parallel\" and not NP_TOK.search(line):\n"
     "        return False, \"parameter-token\", 0, 0, key\n",
     ""),
    ("15-decision-re-r16-only",
     "section reader no longer recognises R17 decision rows",
     "D_RE = re.compile(r\"^\\| *(R1[67]) *\\|\")\n",
     "D_RE = re.compile(r\"^\\| *(R16) *\\|\")\n"),
    ("16-supersedes-removed",
     "D-row supersedes field no longer checked",
     "            if p != param or s != sup:\n",
     "            if p != param:\n"),
    ("17-ex-condition-removed",
     "B7 non-add_opt derived ex == LLAMA_EXAMPLE_X condition check removed",
     "                if mm.group(1) not in cond:\n",
     "                if False:\n"),
    ("18-value-empty-removed",
     "B5 non-literal default/overrides rows may carry '-' as value",
     "        if not value or value == \"-\":\n            return False, \"value-empty\", 0, 0, key\n",
     ""),
    ("19-effect-enum-removed",
     "effect vocabulary check removed (any spelling accepted)",
     "    if effect not in EFFECTS:\n        return False, \"effect-enum\", 0, 0, key\n",
     ""),
    ("20-param-enum-removed",
     "parameter vocabulary check removed (any spelling accepted)",
     "    if param not in PARAMS:\n        return False, \"parameter-enum\", 0, 0, key\n",
     ""),
    ("21-missing-zero",
     "missing population keys are never counted",
     "    missing = sum(1 for k in pop if k not in seen)\n",
     "    missing = 0\n"),
    ("22-digest-removed",
     "archive sha256 pin check removed",
     "    if digest != TARBALL_SHA256:\n",
     "    if False:\n"),
    ("23-backtick-strip-removed",
     "B2 no longer strips the surrounding backticks from a text cell",
     "    if t.startswith(\"`\") and t.endswith(\"`\") and len(t) >= 2:\n        t = t[1:-1]\n",
     ""),
    ("24-decision-value-removed",
     "R16/R17 value cell no longer compared with the default P-row value",
     "            elif len(defaults) != 1 or defaults[0][8] != val:\n",
     "            elif False:\n"),
    ("25-value-dash-removed",
     "non-default/overrides effects may carry any value cell",
     "    elif value != \"-\":\n        return False, \"value-not-dash\", 0, 0, key\n",
     ""),
    ("26-condition-empty-removed",
     "P-row condition may be empty",
     "    if not cond:\n        return False, \"condition-empty\", 0, 0, key\n",
     ""),
]

(OUT / "mutants/m2-counter.py").write_bytes(base)
rows = [("BASE", "counter at M2 unmutated", sha, "-")]
for mid, desc, old, new in M:
    assert text.count(old) == 1, (mid, text.count(old), old)
    mut = text.replace(old, new)
    assert mut != text
    p = OUT / f"mutants/{mid}.py"
    p.write_text(mut)
    rows.append((mid, desc, hashlib.sha256(mut.encode()).hexdigest(), f"{old!r} -> {new!r}"))
(OUT / "mutants/manifest.tsv").write_text("".join("\t".join(r) + "\n" for r in rows))
print(f"wrote {len(M)} mutants + m2-counter.py; counter sha {sha}")
print(f"battery copy sha {hashlib.sha256(bat.encode()).hexdigest()}")
