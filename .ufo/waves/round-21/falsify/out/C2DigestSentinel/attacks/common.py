"""Shared harness for the C2DigestSentinel falsify experiments.

Loads the producer (tools/kama-llamacpp-live.py) and gate
(tests/llamacpp-live/check-receipt.py) from the attacked commit's clone.
Nothing here launches llama-server or the live producer.
"""
import errno
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

LANE = '/tmp/kama-r21-C2DigestSentinel/lane'          # clone at a6617149
WORK = '/tmp/kama-r21-C2DigestSentinel/work'           # scratch trees
REAL_SERVER = os.path.expanduser('~/.local/opt/llama-b11755/llama-server')
GATE = f'{LANE}/tests/llamacpp-live/check-receipt.py'

# captured before any experiment can replace subprocess.Popen
_REAL_POPEN = subprocess.Popen


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _load('kll', f'{LANE}/tools/kama-llamacpp-live.py')
G = _load('cr', GATE)


def live_receipt():
    with open(os.path.join(WORK, 'live-receipt.json'), encoding='utf-8') as fh:
        return json.load(fh)


def write_receipt(path, obj):
    # mirrors the producer's _emit(): ASCII escapes, sorted keys
    text = json.dumps(obj, ensure_ascii=True, allow_nan=False,
                      indent=2, sort_keys=True) + '\n'
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return path


def gate(path, *flags):
    proc = _REAL_POPEN([sys.executable, GATE, path, *flags],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(timeout=300)
    return proc.returncode, out.strip(), err.strip()


def server_block(server_path):
    """Producer-shaped server block for a directory, computed exactly as
    main() does at tools/kama-llamacpp-live.py:1374-1396 (no launch)."""
    real = os.path.realpath(server_path)
    tree, tree_sha = P.install_tree(real)
    links, links_sha, problems = P.install_links(real)
    impl = os.path.join(os.path.dirname(real), 'libllama-server-impl.so')
    impl_sha = P.sha256_file(impl) if os.path.isfile(impl) else None
    block = {'arg': server_path, 'realpath': real,
             'sha256': P.sha256_file(real),
             'install_tree': tree, 'install_tree_sha256': tree_sha,
             'install_links': links, 'install_links_sha256': links_sha,
             'server_impl_sha256': impl_sha}
    return block, problems


def receipt_for(server_path):
    """Live receipt template with only the server block (and argv[0])
    replaced by the producer-shaped block for server_path."""
    r = live_receipt()
    block, problems = server_block(server_path)
    r['server'] = block
    r['argv'][0] = block['realpath']
    return r, problems


def errname(exc):
    code = getattr(exc, 'errno', None)
    return f'{type(exc).__name__}(errno={code}' \
           f'{"/" + errno.errorcode.get(code, "?") if code else ""}): {exc}'
