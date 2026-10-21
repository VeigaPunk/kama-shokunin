#!/usr/bin/env python3
"""Seeded-defect check for the install-identity selftest helper.

Usage: mutants_probe.py PRODUCER_PATH

Runs module._install_identity_selftest() with the producer's own
install_tree/install_links (control: must pass) and with nine substitutes
(each must raise AssertionError). Prints one line per case; exit 0 only when
the control passes and every substitute fails. Requires a producer that
defines _install_identity_selftest().
"""
import hashlib
import importlib.util
import os
import stat
import sys

spec = importlib.util.spec_from_file_location('kama_llamacpp_live',
                                              sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
real_tree = module.install_tree
real_links = module.install_links


def tree_follows_symlinks(server_real):
    directory = os.path.dirname(server_real)
    found = {}
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        try:
            if stat.S_ISREG(os.stat(path).st_mode):
                found[name] = module.sha256_file(path)
        except OSError:
            continue
    digest = hashlib.sha256(''.join(
        f'{n} {found[n]}\n' for n in sorted(found)).encode()).hexdigest()
    return found, digest


def tree_digest_without_newline(server_real):
    found, _ = real_tree(server_real)
    return found, hashlib.sha256(''.join(
        f'{n} {found[n]}' for n in sorted(found)).encode()).hexdigest()


def make_tree_moves_on_retarget():
    calls = []

    def moving_tree(server_real):
        found, digest = real_tree(server_real)
        calls.append(server_real)
        if len(calls) > 1:
            digest = hashlib.sha256((digest + 'x').encode()).hexdigest()
        return found, digest
    return moving_tree


def links_empty(server_real):
    return {}, hashlib.sha256(b'').hexdigest()


def links_resolved(server_real):
    directory = os.path.dirname(server_real)
    links = {n: os.path.realpath(os.path.join(directory, n))
             for n in real_links(server_real)[0]}
    digest = hashlib.sha256(''.join(
        f'{n} -> {links[n]}\n' for n in sorted(links)).encode()).hexdigest()
    return links, digest


def digest_names_only(server_real):
    links, _ = real_links(server_real)
    return links, hashlib.sha256(''.join(
        f'{n}\n' for n in sorted(links)).encode()).hexdigest()


def digest_without_arrow(server_real):
    links, _ = real_links(server_real)
    return links, hashlib.sha256(''.join(
        f'{n} {links[n]}\n' for n in sorted(links)).encode()).hexdigest()


def make_stale_pair():
    cache = {}

    def links_stale_pair(server_real):
        return cache.setdefault(server_real, real_links(server_real))
    return links_stale_pair


def make_stale_digest():
    cache = {}

    def links_stale_digest(server_real):
        links, digest = real_links(server_real)
        return links, cache.setdefault(server_real, digest)
    return links_stale_digest


CASES = [
    ('control', real_tree, real_links, True),
    ('tree-follows-symlinks', tree_follows_symlinks, real_links, False),
    ('tree-digest-without-newline', tree_digest_without_newline,
     real_links, False),
    ('tree-moves-on-retarget', make_tree_moves_on_retarget(), real_links,
     False),
    ('links-empty', real_tree, links_empty, False),
    ('links-resolved-target', real_tree, links_resolved, False),
    ('digest-names-only', real_tree, digest_names_only, False),
    ('digest-without-arrow', real_tree, digest_without_arrow, False),
    ('links-stale-pair', real_tree, make_stale_pair(), False),
    ('links-stale-digest', real_tree, make_stale_digest(), False),
]
all_ok = True
for name, tree_fn, links_fn, expect_pass in CASES:
    module.install_tree = tree_fn
    module.install_links = links_fn
    try:
        module._install_identity_selftest()
        outcome, detail = 'PASS', ''
    except AssertionError as exc:
        outcome, detail = 'FAIL', str(exc)
    ok = (outcome == 'PASS') == expect_pass
    all_ok = all_ok and ok
    print(f"case={name} outcome={outcome} "
          f"expected={'PASS' if expect_pass else 'FAIL'} ok={ok} "
          f"detail={detail!r}")
print(f"mutants: all_ok={all_ok}")
sys.exit(0 if all_ok else 1)
