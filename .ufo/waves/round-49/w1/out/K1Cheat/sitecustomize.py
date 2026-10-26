"""K1Cheat round-49 attack 2: PYTHONPATH sitecustomize hijack.

Activated only when K1_DECOY=1 and the interpreter is starting the lane's
kama-live-replay.py: execv the decoy replay in its place. The counter's own
process and every other python (the live tool, the counter) is untouched.
"""

import os
import sys

_DECOY = "/fast/scratch/hyaku/kama-r49/K1Cheat/decoy-replay.py"


def _hook():
    if os.environ.get("K1_DECOY") != "1":
        return
    if not (sys.argv and os.path.basename(sys.argv[0]) == "kama-live-replay.py"):
        return
    if not os.path.isfile(_DECOY):
        return
    os.execv(sys.executable, [sys.executable, _DECOY] + sys.argv[1:])


_hook()
