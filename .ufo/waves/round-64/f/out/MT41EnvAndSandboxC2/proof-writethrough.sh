#!/bin/bash
# Write-through proof, entirely inside the seat's scratch root.
#
# The tip export (git archive of the tip) carries 8 COMMITTED symlinks whose
# targets are absolute paths in the real lane
#   .ufo/waves/round-36/w3/out/MutRowPipe/probe/{tools,registry,tests,...}
# The counter runs the bound commands with cwd = the tip export (row runs)
# or with cwd = an overlay whose top-level entries are symlinks to the tip
# export (regression/printer runs).  A bound command that writes a relative
# path therefore reaches THROUGH those links.
#
# This script proves the MECHANISM with a scratch victim (never the lane):
#   victim/  <- plays the role of the lane directory the links point at
#   export/  <- plays the role of the tip export (contains the link)
# Then a command with cwd=export writes a relative path and we show the file
# landed in victim/, i.e. outside the "export" and outside any --work.
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2
W=$S/proof-writethrough
rm -rf "$W"; mkdir -p "$W/victim/tools" "$W/export/.ufo/waves/round-36/w3/out/MutRowPipe/probe"
ln -s "$W/victim/tools" "$W/export/.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools"

echo "== fixture"
ls -l "$W/export/.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools"
echo
echo "== a relative write from cwd=export (the tip export is the counter's cwd for the bound rows)"
( cd "$W/export" && python3 -c "open('.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools/EVIL','w').write('x')" )
echo "inside export?  : $(find "$W/export" -name EVIL | wc -l) entry"
echo "inside victim?   : $(find "$W/victim" -name EVIL | wc -l) entry"
echo "victim file     : $(ls -la "$W/victim/tools/EVIL" 2>/dev/null)"
echo
echo "== the same shape in the REAL tip export: resolution only (no write)"
python3 - <<PYEOF
import os
base = "$S/work-strace/tip"
p = os.path.join(base, '.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools')
print('tip export path :', p)
print('is a symlink    :', os.path.islink(p))
print('resolves to     :', os.path.realpath(p))
print('writable        :', os.access(os.path.realpath(p), os.W_OK))
print('=> a relative write to .ufo/waves/round-36/w3/out/MutRowPipe/probe/tools/<f>')
print('   from cwd=<tip export> would land in the REAL LANE, not in --work.')
PYEOF
