# Reproduces demo-junk.txt. Run inside your own scratch; every git call names -C "$D".
D=$(mktemp -d -p "$PWD"); git -C "$D" init -q; test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" || exit 1
mkdir -p "$D/registry"; printf 'SCORECARD.md is append-only.\n' > "$D/README.md"
head=$'# S\n\nbanner r1\nre-derived: ## Axes\n'
axes=$'## Axes\n'$(for i in $(seq 0 29); do echo "axis real $i"; done)$'\n'
rounds=$'## Round 1\n'$(for i in $(seq 0 24); do echo "fact $i"; done)$'\n'
junk=$'## Axes\n'$(for i in $(seq 0 29); do echo "JUNK $i"; done)$'\n'
printf '%s%s%s' "$head" "$axes" "$rounds" > "$D/SCORECARD.md"
G="git -C $D -c user.name=u1 -c user.email=u1@x"; $G add -A; $G commit -qm base
printf '%s%s%s' "$head" "$junk" "$rounds" > "$D/SCORECARD.md"; $G add -A; $G commit -qm junk
printf 'path\trule\tdeclared_at\tregion\tnote\nSCORECARD.md\tA-corr\tREADME.md:1\texempt=## Axes@SCORECARD.md:4\tn\n' > c.tsv
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo "$D" --to HEAD --contract c.tsv --threshold 20; echo exit=$?
