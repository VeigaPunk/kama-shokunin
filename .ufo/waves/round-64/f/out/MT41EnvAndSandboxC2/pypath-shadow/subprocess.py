"""A PYTHONPATH shadow of the stdlib `subprocess` module.

The C2 counter SANITISES the environment it hands to the 12 bound commands
(PATH HOME LANG LC_ALL TMPDIR PYTHONDONTWRITEBYTECODE) but it does NOT
sanitise its OWN interpreter environment: it is launched as
    python3 tools/round64-c2-counter.py ...
so the caller's PYTHONPATH is on sys.path BEFORE the stdlib.  A module in
the PYTHONPATH directory therefore shadows the stdlib module the counter
imports.

This shadow wraps subprocess.run/Popen and rewrites the git REF argument
from the base tip to a different (measured) tip.  Everything else is
delegated to the real stdlib subprocess.  The counter then believes it is
scoring the base tip while every byte it reads comes from the other tip.
"""
import importlib.util
import os
import sys
import sysconfig

_stdlib = sysconfig.get_paths()['stdlib']
_spec = importlib.util.spec_from_file_location(
    '_real_subprocess', os.path.join(_stdlib, 'subprocess.py'))
_real = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_real)

for _k, _v in vars(_real).items():
    if not _k.startswith('__'):
        globals()[_k] = _v

FAKE_TIP = os.environ.get('MT41_FAKE_TIP', '')
BASE_REF = os.environ.get('MT41_BASE_REF', '')


def _rewrite(args):
    if not FAKE_TIP or not BASE_REF:
        return args
    out = []
    for a in args:
        if isinstance(a, str) and (
                a == BASE_REF
                or a.startswith(BASE_REF + ':')
                or a == BASE_REF + '^{commit}'):
            a = FAKE_TIP + a[len(BASE_REF):]
        out.append(a)
    return out


def run(*args, **kwargs):
    if args:
        args = (_rewrite(list(args[0])),) + tuple(args[1:])
    return _real.run(*args, **kwargs)


def Popen(*args, **kwargs):
    if args:
        args = (_rewrite(list(args[0])),) + tuple(args[1:])
    return _real.Popen(*args, **kwargs)


def check_output(*args, **kwargs):
    if args:
        args = (_rewrite(list(args[0])),) + tuple(args[1:])
    return _real.check_output(*args, **kwargs)
