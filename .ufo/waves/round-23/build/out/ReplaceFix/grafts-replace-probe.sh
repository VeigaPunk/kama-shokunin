#!/usr/bin/env bash
# Replace/graft/child-process semantics under git 2.56.0. Scratch only (/tmp).
set -u
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
T=$(mktemp -d /tmp/rf-exp3.XXXX); cd "$T" || exit 1
ID="GIT_AUTHOR_NAME=z GIT_COMMITTER_NAME=z GIT_AUTHOR_EMAIL=z@x GIT_COMMITTER_EMAIL=z@x"
cm() { # repo msg when author
  echo "$2" >> "$1/f"; git -C "$1" add f
  env GIT_AUTHOR_NAME=$4 GIT_COMMITTER_NAME=$4 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
    GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q -m "$2"
  git -C "$1" rev-parse HEAD
}
git init -q -b master r
L0=$(cm r "one" 1000 kama-shokunin)
X=$(cm r "two" 1100 kama-shokunin)
TREE=$(git -C r rev-parse "$X^{tree}")
Y=$(env $ID GIT_AUTHOR_DATE="@1150 +0000" GIT_COMMITTER_DATE="@1150 +0000" \
    git -C r commit-tree -p "$L0" -m unrelated "$TREE")
echo "L0=$L0 X=$X Y=$Y"
git -C r update-ref "refs/replace/$X" "$Y"
fmt='%h|%an|%s'
echo "== E7 default log (tip X replaced by Y: expect unrelated/z then one) =="
git -C r log --format="$fmt" | tr '\n' ';'; echo
echo "== E8 --no-replace-objects log (expect two/kama then one/kama) =="
git -C r --no-replace-objects log --format="$fmt" | tr '\n' ';'; echo
echo "== E9 GIT_NO_REPLACE_OBJECTS=1 log =="
GIT_NO_REPLACE_OBJECTS=1 git -C r log --format="$fmt" | tr '\n' ';'; echo
echo "== E10 cat-file --batch-check of X: default | flag | env =="
echo "$X" | git -C r cat-file --batch-check
echo "$X" | git -C r --no-replace-objects cat-file --batch-check
echo "$X" | GIT_NO_REPLACE_OBJECTS=1 git -C r cat-file --batch-check
echo "== E14 child git spawned by alias (flag not inherited; env is) =="
echo -n "none:  "; git -C r -c 'alias.c=!git log -1 --format=%s' c
echo -n "flag:  "; git -C r --no-replace-objects -c 'alias.c=!git log -1 --format=%s' c
echo -n "env:   "; GIT_NO_REPLACE_OBJECTS=1 git -C r -c 'alias.c=!git log -1 --format=%s' c
echo -n "both:  "; GIT_NO_REPLACE_OBJECTS=1 git -C r --no-replace-objects -c 'alias.c=!git log -1 --format=%s' c
echo "== E18 grafts: default, flag, GIT_GRAFT_FILE=/dev/null (r2: B parentless) =="
git init -q -b master r2
A2=$(cm r2 "one" 1000 kama-shokunin); B2=$(cm r2 "two" 1100 kama-shokunin)
printf '%s\n' "$B2" > r2/.git/info/grafts
echo -n "default: "; git -C r2 log --format="$fmt" 2>/dev/null | tr '\n' ';'; echo
echo -n "flag:    "; git -C r2 --no-replace-objects log --format="$fmt" 2>/dev/null | tr '\n' ';'; echo
echo -n "env-NRO: "; GIT_NO_REPLACE_OBJECTS=1 git -C r2 log --format="$fmt" 2>/dev/null | tr '\n' ';'; echo
echo -n "GRAFT=/dev/null: "; GIT_GRAFT_FILE=/dev/null git -C r2 log --format="$fmt" 2>/dev/null | tr '\n' ';'; echo
echo -n "child alias w/ GRAFT=/dev/null env: "; GIT_GRAFT_FILE=/dev/null git -C r2 -c 'alias.c=!git log --format=%s' c 2>/dev/null | tr '\n' ';'; echo
echo -n "rev-list --count HEAD default/GRAFT_null: "; git -C r2 rev-list --count HEAD 2>/dev/null | tr '\n' ' '; GIT_GRAFT_FILE=/dev/null git -C r2 rev-list --count HEAD 2>/dev/null; echo
echo "== E19 is GIT_GRAFT_FILE / GIT_SHALLOW_FILE documented? (man git) =="
zcat /usr/share/man/man1/git.1.gz 2>/dev/null | grep -n -i -e 'GIT_GRAFT_FILE' -e 'GIT_NO_REPLACE_OBJECTS' -e 'GIT_SHALLOW_FILE' -e 'GIT_REPLACE_REF_BASE' -e 'no-replace-objects' | head -20
echo "== E20 shallow file: default vs GIT_SHALLOW_FILE=/dev/null =="
git init -q -b master r3
P3=$(cm r3 "one" 1000 kama-shokunin); Q3=$(cm r3 "two" 1100 kama-shokunin)
printf '%s\n' "$Q3" > r3/.git/shallow
echo -n "default: "; git -C r3 log --format="$fmt" 2>/dev/null | tr '\n' ';'; echo
echo -n "GIT_SHALLOW_FILE=/dev/null: "; GIT_SHALLOW_FILE=/dev/null git -C r3 log --format="$fmt" 2>/dev/null | tr '\n' ';'; echo
echo "T=$T"
