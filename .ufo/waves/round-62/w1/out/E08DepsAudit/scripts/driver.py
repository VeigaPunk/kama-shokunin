#!/usr/bin/env python3
"""E08 dep-audit driver: does tools/kama-completion-live.py fail cleanly
when its tools/kama-llamacpp-live.py dependency blob is missing/rotten, and
how does the REPO-relative import path resolve?

Each case runs the *master blob* of the tool in an isolated fixture tree and
records exit code, the exception surfaced, whether a receipt was written and
what the receipt says. No case touches the lane, another seat or a registered
consumer port: every run dies before (or at) the dependency boundary.
"""
import json
import os
import shutil
import subprocess
import sys

S = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run_case(name, tool, extra=(), timeout=180):
    work = os.path.join(S, 'w', name)
    out = os.path.join(S, 'r', name + '.json')
    for d in (work, os.path.dirname(out)):
        os.makedirs(d, exist_ok=True)
    if os.path.exists(out):
        os.unlink(out)
    env = {k: v for k, v in os.environ.items()
           if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')}
    env['TMPDIR'] = os.path.join(S, 'tmpdir')
    os.makedirs(env['TMPDIR'], exist_ok=True)
    argv = [PY, tool, '--work', work, '--out', out] + list(extra)
    p = subprocess.run(argv, capture_output=True, text=True,
                       env=env, timeout=timeout, cwd=S)
    err = (p.stderr or '').strip().splitlines()
    rec = None
    if os.path.exists(out):
        try:
            rec = json.load(open(out))
        except ValueError:
            rec = 'UNPARSEABLE'
    return {
        'case': name,
        'argv': [os.path.relpath(a, S) if a.startswith(S) else a
                 for a in argv],
        'rc': p.returncode,
        'receipt_written': rec is not None,
        'receipt_verdict': rec.get('verdict') if isinstance(rec, dict) else rec,
        'receipt_setup_error': rec.get('setup_error')
        if isinstance(rec, dict) else None,
        'stderr_last': err[-1] if err else '',
        'stderr_exception_lines': [ln for ln in err
                                   if 'Error' in ln or 'error' in ln][-4:],
        'stdout_tail': (p.stdout or '').strip().splitlines()[-2:],
    }


def positive_import(tool_path):
    """Resolution-only check: load the tool as a module (no lifecycle)."""
    code = '''
import importlib.util, json, os, sys
tool = sys.argv[1]
spec = importlib.util.spec_from_file_location("kama_completion_live_probe", tool)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
attrs = ["_utc_now", "sha256_file", "http_get", "refused_ports", "pick_port",
         "prepare_witness_dir", "SetupError", "_FORKED_PPID",
         "_preexec_pdeathsig", "port_owned_by", "hold_for_witness",
         "_listen_inodes"]
bound = {a: type(getattr(m._live, a)).__name__ for a in attrs
         if hasattr(m._live, a)}
print(json.dumps({
    "tool_REPO": m.REPO,
    "dep_file": str(m._live.__file__),
    "dep_MODULE_NAME": m._live.__name__,
    "dep_PATH_parent": str(m._live.LANE),
    "dep_REGISTRY": str(m._live.REGISTRY),
    "bound": bound,
    "missing": [a for a in attrs if not hasattr(m._live, a)],
    "sys_path_leak": [p for p in sys.path if "tools" in p],
}))
'''
    p = subprocess.run([PY, '-c', code, tool_path], capture_output=True,
                       text=True, cwd=S)
    return {'rc': p.returncode,
            'json': json.loads(p.stdout) if p.returncode == 0 else None,
            'stderr_last': (p.stderr or '').strip().splitlines()[-1:] or []}


def main():
    tip = os.path.join(S, 'tip')
    cases = [
        ('absent_dep', os.path.join(S, 't_dep_absent', 'tools',
                                    'kama-completion-live.py')),
        ('syntax_dep', os.path.join(S, 't_bad_dep_syntax', 'tools',
                                    'kama-completion-live.py')),
        ('no_registry', os.path.join(S, 't_no_registry', 'tools',
                                     'kama-completion-live.py')),
        ('symlink_invoke', os.path.join(S, 'link',
                                        'kama-completion-live.py')),
        ('missing_symbol', os.path.join(S, 't_missing_symbol', 'tools',
                                        'kama-completion-live.py')),
    ]
    only = sys.argv[1] if len(sys.argv) > 1 else None
    res = {'positive_import': positive_import(
        os.path.join(tip, 'tools', 'kama-completion-live.py'))}
    res['fixtures'] = {}
    for name, tool in cases:
        if only and name != only:
            continue
        res['fixtures'][name] = run_case(name, tool)
        print(json.dumps(res['fixtures'][name], indent=1), flush=True)
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
