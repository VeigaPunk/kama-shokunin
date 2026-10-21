#!/usr/bin/env bash
# CritCompleteness r24 probe: which git calls used (or plausibly added) by
# tools/report-landing-audit.py fail loudly vs. pass silently when a
# required object is missing in a promisor-marked repository.
# Local synthetic repos only; promisor URL is a nonexistent local path;
# every git call carries the audit's --no-replace-objects --no-lazy-fetch.
set -u
ROOT=/fast/scratch/hyaku/kama-r24/CritCompleteness
rm -rf "$ROOT/probe" && mkdir -p "$ROOT/probe"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
unset $(env | sed -n 's/^\(GIT_[A-Z_]*\)=.*/\1/p' | grep -v -e GIT_CONFIG_GLOBAL -e GIT_CONFIG_NOSYSTEM)
G() { git --no-replace-objects --no-lazy-fetch "$@"; }
obj() { local o=$1; echo "$2/.git/objects/${o:0:2}/${o:2}"; }

base="$ROOT/probe/base"
git init -q -b master "$base"
[ "$(git -C "$base" rev-parse --show-toplevel)" = "$base" ] || { echo "toplevel mismatch"; exit 9; }
cd "$base"
c() { GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=k@x GIT_COMMITTER_NAME=k GIT_COMMITTER_EMAIL=k@x \
      GIT_AUTHOR_DATE="$1 +0000" GIT_COMMITTER_DATE="$1 +0000" git commit -q --allow-empty -m "$2"; }
mkdir -p corpus .ufo/reports/round-1
echo src > corpus/SOURCES.md; echo r > .ufo/reports/round-1/kama.md; git add -A; c "2026-01-01T00:00:00" "init"
echo a > f; git add f; c "2026-01-02T00:00:00" "round-1: a"
echo b > f; git add f; c "2026-01-03T00:00:00" "round-1: b"
echo d > f; git add f; c "2026-01-04T00:00:00" "round-2: d"
C1=$(git rev-parse HEAD~3); C2=$(git rev-parse HEAD~2); C3=$(git rev-parse HEAD~1)
CORPUS=$(git rev-parse HEAD:corpus); RTREE=$(git rev-parse HEAD:.ufo/reports/round-1)
SRCBLOB=$(git rev-parse HEAD:corpus/SOURCES.md); C1TREE=$(git rev-parse "$C1^{tree}")
git config remote.origin.url "$ROOT/probe/does-not-exist"
git config remote.origin.promisor true
git config extensions.partialclone origin
cd "$ROOT/probe"

run() { local name=$1; shift; local out err rc
  out=$("$@" 2>"$ROOT/probe/err") ; rc=$?
  printf '%-34s rc=%-3s lines=%-3s stderr=%s\n' "$name" "$rc" "$(printf '%s' "$out" | grep -c .)" \
    "$(head -c 160 "$ROOT/probe/err" | tr '\n' ' ')"; }
fresh() { rm -rf "$ROOT/probe/$1"; cp -a "$base" "$ROOT/probe/$1"; echo "$ROOT/probe/$1"; }

echo "## P1 middle lane commit object missing (C2, round-1: a), no commit-graph"
r=$(fresh p1); rm -f "$(obj "$C2" "$r")"
run "log %H%an%at%s (round_commits)" G -C "$r" log -z --format=%H%x00%an%x00%at%x00%s master
run "rev-list master" G -C "$r" rev-list master
run "rev-list --missing=allow-any" G -C "$r" rev-list --missing=allow-any master
run "rev-list --missing=print" G -C "$r" rev-list --missing=print master
run "rev-list --exclude-promisor-objects" G -C "$r" rev-list --exclude-promisor-objects master

echo "## P2 same, but commit-graph written before the object went missing"
r=$(fresh p2); G -C "$r" commit-graph write --reachable >/dev/null 2>&1; rm -f "$(obj "$C2" "$r")"
run "log %H%an%at%s (round_commits)" G -C "$r" log -z --format=%H%x00%an%x00%at%x00%s master
run "log --format=%H" G -C "$r" log --format=%H master
run "rev-list master" G -C "$r" rev-list master
run "rev-list --objects --missing=print" G -C "$r" rev-list --objects --missing=print master
echo "   ^ missing lines: $(G -C "$r" rev-list --objects --missing=print master 2>/dev/null | grep -c '^?')"
run "log --diff-filter=A -- report" G -C "$r" log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md
run "fsck --connectivity-only" G -C "$r" fsck --connectivity-only --no-dangling

echo "## P3 tip subtree corpus/ missing (load_source_urls)"
r=$(fresh p3); rm -f "$(obj "$CORPUS" "$r")"
run "ls-tree tip -- corpus/SOURCES.md" G -C "$r" ls-tree master -- corpus/SOURCES.md

echo "## P4 report subtree missing (parse_rounds A-)"
r=$(fresh p4); rm -f "$(obj "$RTREE" "$r")"
run "ls-tree -r --name-only -- .ufo/reports" G -C "$r" ls-tree -r --name-only HEAD -- .ufo/reports
run "show HEAD:report" G -C "$r" show HEAD:.ufo/reports/round-1/kama.md

echo "## P5 historical root tree of C1 missing (report_cutoff)"
r=$(fresh p5); rm -f "$(obj "$C1TREE" "$r")"
run "log --diff-filter=A -- report" G -C "$r" log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md

echo "## P6 SOURCES blob missing; batch-check lookup channel"
r=$(fresh p6); rm -f "$(obj "$SRCBLOB" "$r")"
run "cat-file blob SOURCES" G -C "$r" cat-file blob "$SRCBLOB"
printf '%s\n' "$SRCBLOB" "${C2:0:9}^{commit}" > "$ROOT/probe/in"
echo "   batch-check: $(G -C "$r" cat-file --batch-check < "$ROOT/probe/in" 2>&1 | tr '\n' '|')"
rm -f "$(obj "$C2" "$r")"
echo "   batch-check after C2 removed: $(G -C "$r" cat-file --batch-check < "$ROOT/probe/in" 2>&1 | tr '\n' '|')"
echo "   no-lazy-fetch off (expect fetch attempt): $(git -C "$r" cat-file --batch-check < "$ROOT/probe/in" 2>&1 | tr '\n' '|' | head -c 300)"

echo "## P7 filter-only promisor (no promisor bool, no extension)"
r=$(fresh p7); git -C "$r" config --unset remote.origin.promisor; git -C "$r" config --unset extensions.partialclone
git -C "$r" config remote.origin.partialclonefilter blob:none; rm -f "$(obj "$SRCBLOB" "$r")"
echo "   no-lazy-fetch off: $(git -C "$r" cat-file --batch-check <<<"$SRCBLOB" 2>&1 | tr '\n' '|' | head -c 300)"
echo "   no-lazy-fetch on : $(G -C "$r" cat-file --batch-check <<<"$SRCBLOB" 2>&1 | tr '\n' '|' | head -c 300)"

echo "## P8 genuine promisor pack: C3,C4 packed with .promisor; C2,C1 absent (promisor objects)"
r="$ROOT/probe/p8"; rm -rf "$r"; git init -q -b master "$r"
[ "$(git -C "$r" rev-parse --show-toplevel)" = "$r" ] || { echo "toplevel mismatch"; exit 9; }
pk=$(G -C "$base" rev-list --objects master "^$C2" | cut -d' ' -f1 | G -C "$base" pack-objects -q "$r/.git/objects/pack/pack")
touch "$r/.git/objects/pack/pack-$pk.promisor"
git -C "$r" update-ref refs/heads/master "$(git -C "$base" rev-parse master)"
git -C "$r" config remote.origin.url "$ROOT/probe/does-not-exist"; git -C "$r" config remote.origin.promisor true
git -C "$r" config extensions.partialclone origin
run "log %H%an%at%s (round_commits)" G -C "$r" log -z --format=%H%x00%an%x00%at%x00%s master
run "rev-list --exclude-promisor-objects" G -C "$r" rev-list --exclude-promisor-objects master
run "rev-list --missing=allow-promisor" G -C "$r" rev-list --missing=allow-promisor master
run "fsck --connectivity-only" G -C "$r" fsck --connectivity-only --no-dangling --no-reflogs
echo "   allow-promisor round-1 commits visible: $(G -C "$r" rev-list --missing=allow-promisor --format=%s master 2>/dev/null | grep -c '^round-1:') of 2"
