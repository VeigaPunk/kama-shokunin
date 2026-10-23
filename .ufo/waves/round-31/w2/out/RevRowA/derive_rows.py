#!/usr/bin/env python3
"""Compare handwritten RENDER results; never import or call the frozen renderer."""
import json
from pathlib import Path
import sys

clone = Path(sys.argv[1])
out = Path(sys.argv[2])
registry = json.loads((clone / "registry/chat-param-outcomes-r31.json").read_text())
receipt = json.loads((out / "c1.json").read_text())
# Hand application of docstring L50-L54: kind=slot; lexicographic key order;
# JSON integer values 3 and 20; prefix '200, '; separator ', '.
manual = {
    "K31-01": "200, max_tokens = 3, n_predict = 3",
    "K31-02": "200, max_tokens = 3, n_predict = 3",
    "K31-03": "200, n_probs = 20",
}
lines = (clone / "SKILL.md").read_text().splitlines()
results = []
for row in registry["rows"]:
    rid = row["id"]
    if rid not in manual:
        continue
    matches = [(number, line, [cell.strip() for cell in line.strip().strip("|").split("|")])
               for number, line in enumerate(lines, 1) if line.startswith("| " + rid + " |")]
    if len(matches) != 1:
        raise RuntimeError(f"expected one committed table row for {rid}, got {len(matches)}")
    number, line, cells = matches[0]
    live_row = next(item for item in receipt["rows"] if item["id"] == rid)
    committed_bytes = cells[3].encode("utf-8")
    manual_bytes = manual[rid].encode("utf-8")
    result = {"id": rid, "registry_row": row, "skill_line_number": number,
              "skill_line": line, "committed_cell": cells[3],
              "manual_rendered_cell": manual[rid],
              "committed_utf8_hex": committed_bytes.hex(),
              "manual_utf8_hex": manual_bytes.hex(),
              "byte_equal": committed_bytes == manual_bytes,
              "meaning": cells[4], "live": live_row["live"]}
    results.append(result)
    print(f"{rid} | committed-cell==rendered {'yes' if result['byte_equal'] else 'no'} | "
          f"live-status {live_row['live'].get('status')} | live={json.dumps(live_row['live'], sort_keys=True)}")
    print(f"manual-rendered {manual[rid]!r}; utf8-bytes={len(manual_bytes)}")
(out / "manual-row-comparison.json").write_text(json.dumps(results, indent=2) + "\n")
if not all(result["byte_equal"] for result in results):
    sys.exit(1)
