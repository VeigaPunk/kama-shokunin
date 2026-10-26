#!/bin/sh
# Reorder fixture: 40-line LOG.md, last 25 lines moved to the top. Run from a scratch dir; needs aoa.py (tools/append-only-audit.py @3a09a1d).
set -e
D=$(mktemp -d -p "$PWD") ; git -C "$D" init -q; [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ]
export GIT_AUTHOR_NAME=fx GIT_AUTHOR_EMAIL=fx@kama.invalid GIT_COMMITTER_NAME=fx GIT_COMMITTER_EMAIL=fx@kama.invalid GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mkdir -p "$D/registry"; printf 'path\trule\tdeclared_at\tnote\nLOG.md\tA\tLOG.md:1\tfx\n' > "$D/registry/append-only-contract.tsv"
python3 -c "print('\n'.join(f'entry {i:02d}' for i in range(40)))" > "$D/LOG.md"
git -C "$D" add -A; git -C "$D" commit -qm base
python3 - "$D" <<'PY'
import sys
p=sys.argv[1]+"/LOG.md"; L=open(p).read().split("\n")[:-1]
open(p,"w").write("\n".join(L[-25:]+L[:-25])+"\n")
PY
git -C "$D" commit -qam reorder
git -C "$D" diff --numstat HEAD~1 HEAD -- LOG.md
python3 aoa.py --repo "$D" --to HEAD --threshold 10
