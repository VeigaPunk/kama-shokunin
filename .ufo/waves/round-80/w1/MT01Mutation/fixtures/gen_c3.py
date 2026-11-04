#!/usr/bin/env python3
"""Build C3 (ollama-census) fixtures under $S/fixtures/c3.

  grade.json    three crafted probe docs for a direct grade() call:
                green, governed-without-class (no leg governed=1 while unregistered=1)
  audit-green/          two engines, receipts naming their own engine, class_missing=0
  audit-other-engine/   ollama receipt names llama.cpp instead
  audit-one-engine/     one engine only
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
ROOT.mkdir(parents=True, exist_ok=True)
HEADER = "engine\tcounter\treceipt\tverified_at"

port = 45001
green_yes = {"listeners": [{"port": port, "registered": "yes", "owner": "ollama(pid=1)",
                            "verdict": "MODEL_OK"}],
             "summary": {"governed": 1, "unregistered": 0}}
green_no = {"listeners": [{"port": port, "registered": "no", "owner": "ollama(pid=1)",
                           "verdict": "MODEL_OK"}],
            "summary": {"governed": 0, "unregistered": 1}}
governed_without_class = {"listeners": [{"port": port, "registered": "no",
                                         "owner": "ollama(pid=1)", "verdict": "MODEL_OK"}],
                          "summary": {"governed": 1, "unregistered": 1}}
grade_index = {"port": port, "docs": {"green_yes": green_yes, "green_no": green_no,
                                      "governed_without_class": governed_without_class}}
(ROOT / "grade.json").write_text(json.dumps(grade_index, indent=2) + "\n")

LLAMA_RECEIPT = "OLLAMA_CENSUS port=45001 engine=llama.cpp unregistered=1 governed=1 class_missing=0\n"
OLLAMA_RECEIPT = "OLLAMA_CENSUS port=45001 engine=ollama unregistered=1 governed=1 class_missing=0\n"


def build(name, rows):
    root = ROOT / name
    if root.exists():
        shutil.rmtree(root)
    (root / "receipts").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "tools/counter.py").write_text("# counter stub\n")
    (root / "receipts/r-llama.out").write_text(LLAMA_RECEIPT)
    (root / "receipts/r-ollama.out").write_text(OLLAMA_RECEIPT)
    lines = [HEADER] + ["\t".join(row) for row in rows]
    (root / "registry.tsv").write_text("\n".join(lines) + "\n")
    return str(root)


llama_row = ["llama.cpp", "tools/counter.py", "receipts/r-llama.out", "2026-11-04"]
ollama_row = ["ollama", "tools/counter.py", "receipts/r-ollama.out", "2026-11-04"]
other_row = ["ollama", "tools/counter.py", "receipts/r-llama.out", "2026-11-04"]

index = {
    "audit_green": build("audit-green", [llama_row, ollama_row]),
    "audit_other_engine": build("audit-other-engine", [llama_row, other_row]),
    "audit_one_engine": build("audit-one-engine", [llama_row]),
}
(ROOT / "index.json").write_text(json.dumps(index, indent=2) + "\n")
print(json.dumps(index, indent=2))
