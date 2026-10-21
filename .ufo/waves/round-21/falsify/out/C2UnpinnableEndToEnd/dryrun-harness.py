#!/usr/bin/env python3
"""Dry-run harness (round-21 C2 falsify seat). Imports the producer at argv[1]
and runs its main() on argv[2:] exactly as the CLI would, except that spawning
a binary whose basename is llama-server is refused: subprocess.Popen raises
OSError(ENOEXEC) and the attempt is recorded. Nothing is launched; the
producer's own launch-failed path then publishes the receipt."""
import errno, importlib.util, json, os, subprocess, sys

attempts = []
_real_popen = subprocess.Popen


def _guarded_popen(args, *a, **k):
    argv = list(args) if isinstance(args, (list, tuple)) else [args]
    if argv and os.path.basename(str(argv[0])) == 'llama-server':
        attempts.append([str(x) for x in argv])
        raise OSError(errno.ENOEXEC, 'dry-run harness: launch suppressed')
    return _real_popen(args, *a, **k)


subprocess.Popen = _guarded_popen
spec = importlib.util.spec_from_file_location('kama_live_dryrun', sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
rc = mod.main(sys.argv[2:])
print(json.dumps({'exit': rc, 'launch_attempts': attempts}, sort_keys=True))
sys.exit(rc)
