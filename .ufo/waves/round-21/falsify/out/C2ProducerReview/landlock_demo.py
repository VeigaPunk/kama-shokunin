#!/usr/bin/env python3
"""Scratch, unprivileged: a real Landlock READ_FILE restriction on this process.

Landlock hooks open(2); access(2) is not hooked. Shows os.access() passing where
open() is denied, and what the lane producer's install_tree()/install_links() pair
then records. Writes only under /tmp/kama-r21-C2ProducerReview/exp/work.
"""
import ctypes
import errno
import importlib.util
import json
import os
import tempfile

LANE = '/tmp/kama-r21-C2ProducerReview/lane/tools/kama-llamacpp-live.py'
WORK = '/tmp/kama-r21-C2ProducerReview/exp/work'

spec = importlib.util.spec_from_file_location('kll_new', LANE)
kll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kll)

SYS_CREATE, SYS_ADD, SYS_RESTRICT = 444, 445, 446  # x86_64 landlock syscalls
READ_FILE = 1 << 2
RULE_PATH_BENEATH = 1
PR_SET_NO_NEW_PRIVS = 38

libc = ctypes.CDLL(None, use_errno=True)
libc.syscall.restype = ctypes.c_long


def sc(num, *args):
    ret = libc.syscall(ctypes.c_long(num), *args)
    if ret < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return ret


class PathBeneath(ctypes.Structure):
    _pack_ = 1
    _fields_ = [('allowed_access', ctypes.c_uint64),
                ('parent_fd', ctypes.c_int32)]


os.makedirs(WORK, exist_ok=True)
d = tempfile.mkdtemp(prefix='landlock-', dir=WORK)
server = os.path.join(d, 'llama-server')
lib = os.path.join(d, 'libllama.so.0.7.0')
extra = os.path.join(d, 'libextra.so')
for path, body in ((server, b'server\n'), (lib, b'lib\n'), (extra, b'extra\n')):
    with open(path, 'wb') as fh:
        fh.write(body)
os.symlink('libllama.so.0.7.0', os.path.join(d, 'libllama.so.0'))
os.symlink('libllama.so.0', os.path.join(d, 'libllama.so'))

before_names = sorted(kll.install_tree(server)[0])
abi = sc(SYS_CREATE, None, ctypes.c_long(0), ctypes.c_long(1))  # VERSION flag
attr = ctypes.c_uint64(READ_FILE)
ruleset = sc(SYS_CREATE, ctypes.byref(attr),
             ctypes.c_long(ctypes.sizeof(attr)), ctypes.c_long(0))
fd = os.open(server, os.O_PATH | os.O_CLOEXEC)
rule = PathBeneath(READ_FILE, fd)
sc(SYS_ADD, ctypes.c_long(ruleset), ctypes.c_long(RULE_PATH_BENEATH),
   ctypes.byref(rule), ctypes.c_long(0))
os.close(fd)
if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
    raise OSError(ctypes.get_errno(), 'prctl(NO_NEW_PRIVS)')
sc(SYS_RESTRICT, ctypes.c_long(ruleset), ctypes.c_long(0))

probe = {'landlock_abi': abi, 'uid': os.getuid()}
probe['os.access(lib, R_OK)'] = os.access(lib, os.R_OK)
for label, path in (('open(server)', server), ('open(lib)', lib),
                    ('open(extra)', extra)):
    try:
        with open(path, 'rb') as fh:
            fh.read(1)
        probe[label] = 'ok'
    except OSError as exc:
        probe[label] = errno.errorcode.get(exc.errno, exc.errno)
restricted_tree, _ = kll.install_tree(server)
links, _, problems = kll.install_links(server)
probe['full_tree_names_before_restriction'] = before_names
probe['restricted_install_tree_names'] = sorted(restricted_tree)
probe['restricted_install_links'] = links
probe['restricted_install_links_problems'] = problems
probe['producer_would_fail_closed'] = bool(problems)
print(json.dumps(probe, indent=1, sort_keys=True))
