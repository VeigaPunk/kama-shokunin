"""Rev1Base round-50 reproduction of round-49 seat K1Cheat attack 2 (PYTHONPATH
sitecustomize hijack of the replay's inherited interpreter environment).

Every interpreter started with this directory on PYTHONPATH logs a line; when such
an interpreter is starting the lane's tools/kama-live-replay.py and K1_DECOY=1, it
execs the decoy in its place. The counter's own interpreter is logged and left alone
(its argv[0] is the counter, not the replay).
"""

import os
import sys

_LOG = os.environ.get("K1_HIT_LOG")
_DECOY = os.environ.get("K1_DECOY_PATH",
                        "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/"
                        "w1/out/Rev1Base/decoy-replay.py")


def _note(kind):
    if not _LOG:
        return
    try:
        with open(_LOG, "a") as fh:
            fh.write(f"{kind} pid={os.getpid()} was_replay="
                     f"{bool(sys.argv) and os.path.basename(sys.argv[0]) == 'kama-live-replay.py'} "
                     f"argv={sys.argv[:3]!r}\n")
    except OSError:
        pass


_note("import")
if os.environ.get("K1_DECOY") == "1" and sys.argv and os.path.basename(sys.argv[0]) == "kama-live-replay.py":
    if os.path.isfile(_DECOY):
        _note("exec")
        os.execv(sys.executable, [sys.executable, _DECOY] + sys.argv[1:])
