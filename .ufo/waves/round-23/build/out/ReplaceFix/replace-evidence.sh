#!/usr/bin/env bash
# ReplaceFix evidence: refs/replace on committed objects, flag propagation,
# and --git-path for grafts. Scratch repos under /tmp only. git 2.56.0.
set -u
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
T=$(mktemp -d /tmp/rf-evidence.XXXX) || exit 1
cd "$T" || exit 1
git init -q -b master r
echo one > r/f
git -C r add f
env GIT_AUTHOR_NAME=a GIT_COMMITTER_NAME=a GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  git -C r -c commit.gpgsign=false commit -q -m one
echo "== E11 fabricated 40-hex with refs/replace/<fake>: cat-file --batch-check"
FAKE=1234567890abcdef1234567890abcdef12345678
git -C r update-ref "refs/replace/$FAKE" "$(git -C r rev-parse HEAD)"
echo -n "default: "; echo "$FAKE" | git -C r cat-file --batch-check
echo -n "flag:    "; echo "$FAKE" | git -C r --no-replace-objects cat-file --batch-check
echo "== E12 replaced committed blob: git show HEAD:f"
BL=$(git -C r rev-parse HEAD:f)
NB=$(echo tampered | git -C r hash-object -w --stdin)
git -C r update-ref "refs/replace/$BL" "$NB"
echo -n "default: "; git -C r show HEAD:f
echo -n "flag:    "; git -C r --no-replace-objects show HEAD:f
echo "== E21 does the flag reach child processes? (count of GIT_NO_REPLACE_OBJECTS=1 seen by an alias child)"
echo -n "flag:    "; git --no-replace-objects -C r -c 'alias.e=!env | grep -c "^GIT_NO_REPLACE_OBJECTS=1$"' e
echo -n "no flag: "; git -C r -c 'alias.e=!env | grep -c "^GIT_NO_REPLACE_OBJECTS=1$"' e 2>/dev/null
echo "== E22 path the audit must test for grafts (cwd -C repo)"
git -C r rev-parse --git-path info/grafts
echo "T=$T"
