#!/usr/bin/env python3
"""C2 operability composition probe (FALSIFY seat C2ClaimCritic, round 21).

Replays the producer's pre-launch install snapshot as main() composes it.
  current (a6617149): tree, tree_sha = install_tree(server)
                      links, links_sha, problems = install_links(server)
                      if problems: raise SetupError (before Popen, exit 2)
  frozen  (7a6bc911): tree, tree_sha = install_tree(server); then launch
Synthetic trees only, plus a read-only pass over the real b11755 tree.
No llama-server is executed. The EIO case injects OSError(EIO) at the
sha256_file boundary for one member whose mode stays readable.

usage: python3 -B composition-probe.py [--lane PATH]
  --lane  a clone of the lane; producer blobs are read with git show.
"""
import argparse
import errno
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CUR_REV = 'a6617149722c73d90e142fbdc8154d6967055f7e'
FRZ_REV = '7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d'
PRODUCER = 'tools/kama-llamacpp-live.py'
REAL = Path.home() / '.local/opt/llama-b11755/llama-server'


def fetch(lane, rev, dest):
    blob = subprocess.run(['git', '--no-optional-locks', '-C', str(lane), 'show',
                           f'{rev}:{PRODUCER}'], check=True, capture_output=True).stdout
    dest.write_bytes(blob)
    return dest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def snap_current(mod, server):
    tree, tsha = mod.install_tree(server)
    links, lsha, problems = mod.install_links(server)
    return {'verdict': 'REFUSE' if problems else 'OK', 'problems': problems[:8],
            'members': len(tree), 'links': len(links),
            'install_tree_sha256': tsha, 'install_links_sha256': lsha}


def snap_frozen(mod, server):
    tree, tsha = mod.install_tree(server)
    return {'verdict': 'OK', 'problems': [], 'members': len(tree),
            'install_tree_sha256': tsha}


def build(d):
    d.mkdir(parents=True)
    (d / 'llama-server').write_bytes(b'synthetic; never executed')
    os.chmod(d / 'llama-server', 0o755)
    (d / 'libllama.so.0.7.0').write_bytes(b'synthetic llama')
    (d / 'libggml.so.0.27.0').write_bytes(b'synthetic ggml')
    (d / 'LICENSE').write_bytes(b'synthetic license\n')
    os.symlink('libllama.so.0.7.0', d / 'libllama.so.0')
    os.symlink('libllama.so.0', d / 'libllama.so')
    os.symlink('libggml.so.0.27.0', d / 'libggml.so.0')


def m_control(d):
    pass


def m_license_mode_000(d):
    os.chmod(d / 'LICENSE', 0)


def m_docs_subdir(d):
    (d / 'docs').mkdir()
    (d / 'docs' / 'README.txt').write_text('doc\n')


def m_hwcaps_shadow(d):
    sub = d / 'glibc-hwcaps' / 'x86-64-v3'
    sub.mkdir(parents=True)
    shutil.copyfile(d / 'libllama.so.0.7.0', sub / 'libllama.so.0.7.0')


def m_read_eio(d):
    pass  # fault injected at sha256_file in main()


CASES = [('control', m_control),
         ('license-mode-000', m_license_mode_000),
         ('docs-subdir-benign', m_docs_subdir),
         ('glibc-hwcaps-shadow', m_hwcaps_shadow),
         ('read-EIO-member', m_read_eio)]


def eio_wrapper(orig):
    def wrapped(path):
        if os.path.basename(str(path)) == 'libllama.so.0.7.0':
            raise OSError(errno.EIO, 'Input/output error (injected)', str(path))
        return orig(path)
    return wrapped


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--lane', default='/tmp/kama-r21-C2ClaimCritic/lane')
    args = ap.parse_args()
    work = Path(tempfile.mkdtemp(prefix='kama-r21-C2-probe-'))
    report = {}
    try:
        cur = load('kama_cur', fetch(args.lane, CUR_REV, work / 'cur.py'))
        frz = load('kama_frz', fetch(args.lane, FRZ_REV, work / 'frz.py'))
        orig_cur, orig_frz = cur.sha256_file, frz.sha256_file
        for name, mutate in CASES:
            d = work / 'trees' / name / 'llama-b-synth'
            build(d)
            mutate(d)
            server = str(d / 'llama-server')
            if name == 'read-EIO-member':
                cur.sha256_file = eio_wrapper(orig_cur)
                frz.sha256_file = eio_wrapper(orig_frz)
            try:
                report[name] = {'current': snap_current(cur, server),
                                'frozen': snap_frozen(frz, server)}
            finally:
                cur.sha256_file, frz.sha256_file = orig_cur, orig_frz
        base = report['control']['frozen']['install_tree_sha256']
        for name in report:
            fz = report[name]['frozen']
            fz['tree_digest_moved_vs_control'] = fz['install_tree_sha256'] != base
        if REAL.is_file():
            real = str(REAL.resolve())
            report['real-b11755-readonly'] = {'current': snap_current(cur, real),
                                              'frozen': snap_frozen(frz, real)}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(json.dumps(report, indent=1, sort_keys=True))
    print()
    for name, v in report.items():
        c, f = v['current'], v['frozen']
        print(f"{name:22s} current={c['verdict']:6s} problems={c['problems'][:2]} "
              f"members={c['members']} links={c['links']} | frozen={f['verdict']} "
              f"members={f['members']} tree_digest_moved={f.get('tree_digest_moved_vs_control')}")


if __name__ == '__main__':
    main()
