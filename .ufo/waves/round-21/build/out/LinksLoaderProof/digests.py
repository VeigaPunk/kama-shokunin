#!/usr/bin/env python3
"""Print the lane's install digests for one llama-server path (read-only).

Usage: python3 digests.py LANE_TOOL SERVER_PATH

LANE_TOOL is tools/kama-llamacpp-live.py at the draft commit, loaded by file path.
Its module level only defines constants and an opener (no network, no process launch);
its CLI sits behind __main__ and is not run. install_tree() and install_links() are
called unchanged.
"""
import importlib.util
import sys

tool, server = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('kama_llamacpp_live', tool)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
tree, tree_sha = mod.install_tree(server)
links, links_sha = mod.install_links(server)
print(f'install_tree_sha256={tree_sha} regular_members={len(tree)}')
print(f'install_links_sha256={links_sha} link_members={len(links)}')
for name in sorted(links):
    print(f'  link {name} -> {links[name]}')
