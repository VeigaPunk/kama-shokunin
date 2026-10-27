#!/bin/sh
# Demonstrates: a `superseded` ledger row for a token that was an UNRESOLVED
# citation at --base passes round-54-cited-path-check.py (met=True, bad=0), although
# the counter's docstring (lines 94-97) says the original was "cited in that surface
# at --base and resolved there (unlike `fixed`, which corrects an UNRESOLVED
# citation)". Run from any scratch dir with python3; copies the frozen counter out of
# the read-only lane first, so the lane is never opened for import/bytecode.
set -e
S=${S:-$(mktemp -d)}
O=$(dirname "$0")
cp /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py "$S/c2copy.py"
D=$(mktemp -d -p "$S" fx.XXXX)
git -C "$D" init -q
test "$(git -C "$D" rev-parse --show-toplevel)" = "$D"
git -C "$D" config user.name fx
git -C "$D" config user.email fx@invalid
mkdir -p "$D/tools" "$D/registry"
printf 'new\n' > "$D/tools/new.py"
printf 'closure `tools/nope.py`\n' > "$D/SCORECARD.md"
git -C "$D" add -A; git -C "$D" commit -qm base; B=$(git -C "$D" rev-parse HEAD)
printf 'closure now `tools/new.py`\n' > "$D/SCORECARD.md"
printf 'surface\ttoken\tclass\tevidence\tnote\nSCORECARD.md\ttools/nope.py\tsuperseded\ttools/new.py\t\n' > "$D/registry/cited-path-corrections.tsv"
git -C "$D" add -A; git -C "$D" commit -qm tip; T=$(git -C "$D" rev-parse HEAD)
python3 -B - "$D" "$B" "$T" "$S/c2copy.py" <<'PY'
import importlib.util, sys
D, B, T, mod = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("c2", mod)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base, lane = m.Repo(D, B), m.Repo(D, T)
print("base unresolved:", m.survey(base, None)[1]["SCORECARD.md"])
ok, c = m.evaluate(lane, None, base, [], verbose=True)
print("evaluate met:", ok, c)
PY
