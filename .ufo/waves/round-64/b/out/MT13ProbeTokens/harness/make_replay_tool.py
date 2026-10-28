#!/usr/bin/env python3
"""Build the clone-only replay forgery from the genuine f6a4 tool text: one
guarded branch in main() (only for the counter's live hold dir)."""
import subprocess, textwrap
S = '/fast/scratch/hyaku/kama-r64/b/MT13ProbeTokens'
D = S + '/clone'
base = subprocess.run(['git', '-C', D, 'show',
                       'f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:tools/kama-completion-live.py'],
                      capture_output=True, check=True).stdout.decode()
old = "    args = p.parse_args(argv)\n    receipt, rc = run(args)\n"
assert base.count(old) == 1
block = textwrap.indent(open(S + '/harness/replay_block.txt').read(), '        ')
new = ("    args = p.parse_args(argv)\n"
       "    if args.hold_dir and '/live/hold' in os.path.abspath(args.hold_dir):\n"
       + block + "    receipt, rc = run(args)\n")
open(D + '/tools/kama-completion-live.py', 'w').write(base.replace(old, new))
print('replay tool written')
