#!/usr/bin/env python3
"""Run one assigned scratch counter probe, capturing evidence and exact restoration."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

ROOT = Path('/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlCounterMutants')
TREE = ROOT / 'tree'
OUT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlCounterMutants')
COUNTER = TREE / '.ufo/waves/round-26/count-c1.py'
FROZEN = 'f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96'
LOCK = '/fast/scratch/hyaku/kama-r26/counter.lock'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))
    resource.setrlimit(resource.RLIMIT_NPROC, (8192, 8192))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def owned_servers():
    found = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            args = (p / 'cmdline').read_bytes().split(b'\0')
            if args and b'llama' in args[0] and (p / 'cwd').resolve() == TREE:
                found.append(int(p.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return found


def cleanup_owned():
    killed = owned_servers()
    for pid in killed:
        try:
            os.killpg(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    if killed:
        time.sleep(1)
    for pid in owned_servers():
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    return killed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--mutant')
    ap.add_argument('--home')
    a = ap.parse_args()
    before = COUNTER.read_bytes()
    if digest(before) != FROZEN:
        raise RuntimeError('counter was not pristine before probe')
    command = ['flock', LOCK, 'timeout', '600', 'python3',
               '.ufo/waves/round-26/count-c1.py', '--out', str(OUT / (a.name + '.json'))]
    env = os.environ.copy()
    for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        env.pop(k, None)
    env['TMPDIR'] = str(ROOT / 'tmp')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    if a.home:
        env['HOME'] = a.home
    meta = {'name': a.name, 'cwd': str(TREE), 'command': command,
            'env_overrides': {k: env[k] for k in ('TMPDIR', 'PYTHONDONTWRITEBYTECODE', 'HOME')},
            'unset_env': ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'],
            'limits': {'address_space_bytes': 8 * 1024**3, 'processes_per_uid': 8192,
                       'cpu_seconds_per_process': 180, 'wall_seconds_counter': 600},
            'before_sha256': digest(before), 'mutant': a.mutant}
    rc = 125
    stdout, stderr = '', ''
    try:
        if a.mutant:
            COUNTER.write_bytes(Path(a.mutant).read_bytes())
        meta['run_sha256'] = digest(COUNTER.read_bytes())
        start = time.monotonic()
        run = subprocess.run(command, cwd=TREE, env=env, capture_output=True,
                             text=True, timeout=630, preexec_fn=limits)
        rc, stdout, stderr = run.returncode, run.stdout, run.stderr
        meta['elapsed_seconds'] = round(time.monotonic() - start, 3)
    except subprocess.TimeoutExpired as ex:
        rc = 124
        stdout = ex.stdout.decode() if isinstance(ex.stdout, bytes) else ex.stdout or ''
        stderr = (ex.stderr.decode() if isinstance(ex.stderr, bytes) else ex.stderr or '') + '\nouter timeout\n'
    except Exception as ex:
        stderr += repr(ex) + '\n'
    finally:
        meta['cleanup_killed_pids'] = cleanup_owned()
        COUNTER.write_bytes(before)
        meta['restored_sha256'] = digest(COUNTER.read_bytes())
        meta['owned_servers_remaining'] = owned_servers()
        meta.update({'exit_code': rc, 'stdout': stdout, 'stderr': stderr})
        (OUT / (a.name + '.stdout.txt')).write_text(stdout + '\nexit_code=' + str(rc) + '\n')
        (OUT / (a.name + '.stderr.txt')).write_text(stderr)
        (OUT / (a.name + '.run.json')).write_text(json.dumps(meta, indent=2) + '\n')
    print(json.dumps(meta, indent=1), flush=True)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
