"""Turn only the synthetic mutant-gate call into an immediate timeout."""
import os
from pathlib import Path
import subprocess

if os.environ.get("CENSUS_GATE_MODE") == "timeout":
    _subprocess_run = subprocess.run

    def _timeout_mutant_gate(*args, **kwargs):
        command = args[0] if args else kwargs.get("args")
        if isinstance(command, (list, tuple)):
            parts = [str(value) for value in command]
            is_gate = any(Path(value).name == "grid-gate.py" for value in parts)
            is_baseline = any(Path(value).name == "baseline.json" for value in parts)
            if is_gate and not is_baseline:
                raise subprocess.TimeoutExpired(command, kwargs.get("timeout"))
        return _subprocess_run(*args, **kwargs)

    subprocess.run = _timeout_mutant_gate
