#!/usr/bin/env python3
import json
import sys
from pathlib import Path

receipt = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected = sys.argv[sys.argv.index("--expect-install-tree-sha256") + 1]
if receipt["server"]["install_tree_sha256"] == expected:
    print("VALID receipt")
    sys.exit(0)
print("INVALID install-tree pin mismatch")
sys.exit(1)
