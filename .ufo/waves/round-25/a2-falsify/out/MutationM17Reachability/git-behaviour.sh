#!/bin/bash
# git 2.56 resolution order for a 40-hex name that is also a ref name.
set -u
W=$(mktemp -d /tmp/gitres.XXXXXX)
cd "$W" || exit 1
git init -q -b master .
git config user.email a@x; git config user.name a
echo hi > f; git add f; git commit -qm one
A=$(git rev-parse HEAD)
echo two > g; git add g; git commit -qm two
B=$(git rev-parse HEAD)
git branch 1111111111111111111111111111111111111111 "$B" 2>&1 | sed 's/^/branch-create: /'
git tag 2222222222222222222222222222222222222222 "$B" 2>&1 | sed 's/^/tag-create: /'
echo "git version: $(git --version)"
echo "A(real commit)=$A  B=$B"
echo "--- cat-file --batch-check on the 40-hex ref name ---"
printf '1111111111111111111111111111111111111111\n2222222222222222222222222222222222222222\n' \
  | git cat-file --batch-check 2>&1 | sed 's/^/batch: /'
echo "--- rev-parse of the same names ---"
git rev-parse 1111111111111111111111111111111111111111 2>&1 | sed 's/^/rev-parse: /'
echo "--- control: a 8-hex name that is a tag (F13 shape) ---"
git tag deadbee1 "$B"
printf 'deadbee1\n' | git cat-file --batch-check 2>&1 | sed 's/^/batch-short: /'
echo "--- control: a 8-hex name that is only an object prefix ---"
git cat-file --batch-check 2>&1 <<< "$A" | sed 's/^/batch-real: /'
cd /; rm -rf "$W"
