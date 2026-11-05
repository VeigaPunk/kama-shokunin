#!/bin/bash
# usage: mkrev.sh <name> <path=file>... ; builds a commit object (plumbing only, no ref moved) on top of freeze
set -e
S=/fast/scratch/hyaku/kama-r87/CR01NoWorkShortcuts; W=$S/wt; BASE=94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659
name=$1; shift
export GIT_INDEX_FILE=$S/idx-$name GIT_AUTHOR_NAME=cr01 GIT_AUTHOR_EMAIL=cr01@scratch GIT_COMMITTER_NAME=cr01 GIT_COMMITTER_EMAIL=cr01@scratch
[ "$(git -C $W rev-parse --show-toplevel)" = "$W" ]
git -C $W read-tree $BASE
for spec in "$@"; do p=${spec%%=*}; f=${spec#*=}
  h=$(git -C $W hash-object -w "$f")
  git -C $W update-index --add --cacheinfo 100644,$h,$p
done
t=$(git -C $W write-tree)
git -C $W commit-tree $t -p $BASE -m "scratch $name (not a lane commit)"
