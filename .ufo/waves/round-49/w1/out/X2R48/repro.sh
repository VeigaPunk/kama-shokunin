#!/bin/bash
# X2R48 (round 49) - prior-instrument regression, exact commands, as run on 2026-10-26.
# Nothing here mutates the lane; $S is /fast/scratch/hyaku/kama-r49/X2R48.
set -u
S=/fast/scratch/hyaku/kama-r49/X2R48; mkdir -p "$S"; export TMPDIR="$S"
L=/home/vgpnk/Projects/shokunin/kama-shokunin
TIP=74558c71c38ceaeace15fd4cf8aa9d84977584b1
BASE=438127bc01ff3b99f98468549d58046f932490ef
FREEZE=36d5ed2681111b68c180f8ab1646d8dc9beaedee

git clone --shared "$L" "$S/lane"

# 1. round-48 C1 counter (v3 definitions) at the round-49 build tip
python3 "$L/tools/round48-append-audit-v3-check.py" --repo "$S/lane" --tip "$TIP" --scratch "$S/scr48"
#    -> selftest=1 contract=1 lane=0 fixture=1 stable=1 ... ungraded_lines=89 met=False ; exit 1

# 2. same counter immediately before the build (freeze) and at the round-48 base
python3 "$L/tools/round48-append-audit-v3-check.py" --repo "$S/lane" --tip "$FREEZE" --scratch "$S/b2"   # met=True, exit 0
python3 "$L/tools/round48-append-audit-v3-check.py" --repo "$S/lane" --tip "$BASE"   --scratch "$S/b1"   # met=True, exit 0

# 3. round-47 C1 counter (v2 definitions) at the build tip, at the round-48 base, at its own measured tip
python3 "$L/tools/round47-append-audit-v2-check.py" --repo "$S/lane" --tip "$TIP"  --scratch "$S/r47tip2"  # exit 1
python3 "$L/tools/round47-append-audit-v2-check.py" --repo "$S/lane" --tip "$BASE" --scratch "$S/r47base2" # exit 1 (identical)
python3 "$L/tools/round47-append-audit-v2-check.py" --repo "$S/lane" --tip 76a7aaff --scratch "$S/r47hist2" # met=True

# 4. context: round-46 C1 counter at the tip (rot since v2)
python3 "$L/tools/round46-append-audit-check.py" --repo "$S/lane" --tip "$TIP" --scratch "$S/r46tip2"

# 5. the tool at the tip, its self-test, and the same tool with the origin term patched out
git -C "$S/lane" show "$TIP:tools/append-only-audit.py" > "$S/aoa_v4.py"
python3 "$S/aoa_v4.py" --repo "$S/lane" --to "$TIP"                     # exit 0, 5 restored events, ungraded_lines=82
python3 "$S/aoa_v4.py" --selftest --scratch "$S/st"                     # AOA_SELFTEST pass=30 fail=0
cp "$S/aoa_v4.py" "$S/aoa_noorigin.py"   # then: 'if s in eligible and org.get(text, frozenset()) & titles:' -> 'if s in eligible:'
python3 "$S/aoa_noorigin.py" --repo "$S/lane" --to "$TIP"               # graded=2349 ungraded=72, ungraded_lines=89

# 6. the 7 regraded lines, with parent section and origin titles
python3 "$S/probe7.py" "$S/lane" "$TIP" "$S/aoa_v4.py"

# 7. causality at counter level: fixture clone whose tree is the tip except the origin term
D=$(mktemp -d -p "$S" probe.XXXX); git clone --shared -q "$S/lane" "$D"
test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" || exit 9
# revert the origin term (and its selftest case) in $D/tools/append-only-audit.py, then, with fixture identity only:
env GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@kama.invalid \
    GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@kama.invalid \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -C "$D" commit -q -a -m "probe"
python3 "$L/tools/round48-append-audit-v3-check.py" --repo "$D" --tip "$(git -C "$D" rev-parse HEAD)" --scratch "$S/b3"
#    441d687c (term + its selftest case removed) -> met=True, exit 0
#    6e7d903c (term removed, selftest case kept)  -> lane=1 selftest=0, exit 1
