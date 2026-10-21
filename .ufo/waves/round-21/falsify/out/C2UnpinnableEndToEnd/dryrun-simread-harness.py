#!/usr/bin/env python3
"""Simulated read-failure harness (round-21 C2 falsify seat). Same launch guard
as dryrun-harness.py, plus an in-process patch: sha256_file() raises
OSError(EIO) for two named members while the files stay readable on disk
(os.access R_OK remains True). Simulated; no real I/O fault is produced."""
import errno, importlib.util, json, os, subprocess, sys

FAIL = {'libllama-common.so.0.7.0', 'libggml-cpu-x64.so'}
attempts = []
_real_popen = subprocess.Popen


def _guarded_popen(args, *a, **k):
    argv = list(args) if isinstance(args, (list, tuple)) else [args]
    if argv and os.path.basename(str(argv[0])) == 'llama-server':
        attempts.append([str(x) for x in argv])
        raise OSError(errno.ENOEXEC, 'dry-run harness: launch suppressed')
    return _real_popen(args, *a, **k)


subprocess.Popen = _guarded_popen
spec = importlib.util.spec_from_file_location('kama_live_simread', sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
_real_sha = mod.sha256_file


def _failing_sha(path):
    if os.path.basename(path) in FAIL:
        raise OSError(errno.EIO, 'simulated read failure (access still OK)')
    return _real_sha(path)


mod.sha256_file = _failing_sha
server = sys.argv[3]
access = {n: os.access(os.path.join(os.path.dirname(os.path.realpath(server)), n), os.R_OK) for n in sorted(FAIL)}
rc = mod.main(sys.argv[2:])
print(json.dumps({'exit': rc, 'launch_attempts': attempts, 'access_R_OK': access}, sort_keys=True))
sys.exit(rc)
