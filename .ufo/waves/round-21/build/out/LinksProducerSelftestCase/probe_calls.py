#!/usr/bin/env python3
"""Count install_tree()/install_links() calls made by a producer's --selftest.

Usage: probe_calls.py PRODUCER_PATH

Loads the producer as a module (its __main__ guard keeps main() from running
on import), wraps install_tree and install_links with call counters, runs
main(['--selftest']) and prints one summary line. Exit 0 when the selftest
returns 0, else 1. Starts no server; the selftest binds only ephemeral
loopback sockets.
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('kama_llamacpp_live',
                                              sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
calls = {'install_tree': 0, 'install_links': 0}


def counted(name):
    original = getattr(module, name)

    def wrapper(*args, **kwargs):
        calls[name] += 1
        return original(*args, **kwargs)
    return wrapper


for name in list(calls):
    setattr(module, name, counted(name))
rc = module.main(['--selftest'])
print(f"probe: selftest_rc={rc} install_tree_calls={calls['install_tree']} "
      f"install_links_calls={calls['install_links']}")
sys.exit(0 if rc == 0 else 1)
