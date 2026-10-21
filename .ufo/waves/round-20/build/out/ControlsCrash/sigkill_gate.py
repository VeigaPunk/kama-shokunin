#!/usr/bin/env python3
"""ControlsCrash (kama round 20) signal gate stub: SIGKILLs itself before
reading its receipt argument (returncode -9; honest class:
could-not-evaluate)."""
import os
import signal

os.kill(os.getpid(), signal.SIGKILL)
