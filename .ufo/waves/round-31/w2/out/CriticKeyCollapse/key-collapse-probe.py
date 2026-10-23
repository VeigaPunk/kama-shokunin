#!/usr/bin/env python3
"""Advisory reachability probe; no repository writes and no counter edits.

Run the frozen module with an in-memory append-only SCORECARD overlay at the
pinned measured tip. Every other blob and commit/ancestor query uses its real
read-only Git implementation. Overlay runs are NOT committed-tip measurements.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
LANE = OUT.parents[5]
TIP = "382d11b2107d335705875da1a4d889b074bd6fa6"
PIN = "2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe"
COUNTER = LANE / ".ufo/waves/round-31/count-c2.py"
actual_pin = hashlib.sha256(COUNTER.read_bytes()).hexdigest()
if actual_pin != PIN:
    raise RuntimeError(f"counter pin mismatch: {actual_pin}")

spec = importlib.util.spec_from_file_location("r31_c2_frozen", COUNTER)
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
OriginalRepo = frozen.Repo
raw_tip = OriginalRepo(str(LANE)).blob(TIP, "SCORECARD.md")
raw_base = OriginalRepo(str(LANE)).blob(frozen.BASE, "SCORECARD.md")
if raw_tip is None or raw_base is None:
    raise RuntimeError("missing real committed SCORECARD")

receipt = json.loads((OUT / "frozen-tip.json").read_text())
base_receipt = json.loads((OUT / "frozen-base.json").read_text())
if receipt["problems"] != base_receipt["problems"]:
    raise RuntimeError("failing populations differ between base and tip")
groups = {}
for problem in receipt["problems"]:
    key = (problem["row"], problem["class"])
    groups.setdefault(key, []).append(problem)
group_rows = [
    {"row": row, "class": cls, "count": len(members), "members": members}
    for (row, cls), members in groups.items()
]
(OUT / "key-groups.json").write_text(json.dumps(group_rows, indent=2, ensure_ascii=False) + "\n")
print(f"pin {actual_pin}")
print(f"same_failing_population {receipt['problems'] == base_receipt['problems']}")
print(f"failing_rows {len(receipt['problems'])} unique_keys {len(groups)} collision_groups {sum(len(v) > 1 for v in groups.values())}")
for (row, cls), members in groups.items():
    locators = ",".join(f"r{p['round']}:L{p['line']}" for p in members)
    observations = sorted({p["observed"] for p in members})
    print(f"key {row!r} {cls!r} count {len(members)} members {locators} observed {observations!r}")

header = "\n| id | row | class | observed |\n|---|---|---|---|\n"
arms = {
    "single-correction": header + "| CR31:shared:C1:p1 | C1 | p1 | p1:no-revision |\n",
    "three-corrections": header + "".join(
        f"| CR31:{rnd}:C1:p1 | C1 | p1 | p1:no-revision |\n" for rnd in (11, 12, 13)
    ),
    "wrong-observed": header + "| CR31:shared:C1:p1 | C1 | p1 | p1:not-the-observation |\n",
}
results = []
for arm, suffix in arms.items():
    overlay = raw_tip + suffix.encode()
    suffix_path = OUT / f"{arm}-appendix.md"
    suffix_path.write_text(suffix)
    assert overlay.startswith(raw_tip) and overlay.startswith(raw_base)

    class OverlayRepo(OriginalRepo):
        def blob(self, rev, path):
            if rev == TIP and path == "SCORECARD.md":
                return overlay
            return super().blob(rev, path)

    frozen.Repo = OverlayRepo
    out_path = OUT / f"{arm}.json"
    argv = sys.argv
    sys.argv = [str(COUNTER), "--repo", str(LANE), "--tip", TIP, "--list", "--out", str(out_path)]
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = frozen.main()
    finally:
        sys.argv = argv
        frozen.Repo = OriginalRepo
    log = stdout.getvalue()
    err = stderr.getvalue()
    (OUT / f"{arm}.stdout.log").write_text(log)
    (OUT / f"{arm}.stderr.log").write_text(err)
    result = json.loads(out_path.read_text())
    results.append({
        "arm": arm,
        "execution": "frozen.main with in-memory SCORECARD blob override; not a committed-tip run",
        "exit_code": exit_code,
        "summary": result["summary"],
        "append_only_to_tip": overlay.startswith(raw_tip),
        "appended_bytes": len(overlay) - len(raw_tip),
        "suffix_path": suffix_path.name,
        "counter_sha256": actual_pin,
    })
    print(f"ARM {arm} exit {exit_code} append_only_to_tip {overlay.startswith(raw_tip)} appended_bytes {len(overlay) - len(raw_tip)}")
    print(log.splitlines()[0])
    for correction in result["corrections"]:
        if correction["row"] == "C1":
            print(f"  C1 correction {correction['id']} ok={correction['ok']}")
    print(f"  unresolved {result['unresolved']!r}")
    if err:
        print(err, end="")
(OUT / "overlay-arms.json").write_text(json.dumps(results, indent=2) + "\n")
print("scope: real committed base/tip rows unchanged; all overlay bytes and receipts stay in this seat directory")
