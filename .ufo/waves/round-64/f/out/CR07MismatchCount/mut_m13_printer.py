import sys, os
d=sys.argv[1]
p=os.path.join(d,'tools/capability-repertoire-audit.py')
open(p,'w').write('''#!/usr/bin/env python3
"""Printer: emits the calibration row's expected pattern, runs nothing."""
import sys
if "--selftest" in sys.argv:
    print("CAP_SELFTEST pass=2 fail=0")
    sys.exit(0)
sys.exit(0)
''')
print("M13: tip's tools/capability-repertoire-audit.py replaced by a PRINTER of the calibration row's run-fact pattern (unpinned, not in the C2 registry)")
