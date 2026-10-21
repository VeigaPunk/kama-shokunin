#!/usr/bin/env bash
# Offline probe: how git (with the auditor's isolation flags) reports objects
# that are absent from a promisor-marked repository. No transport is used:
# promisor state is built by hand (pack-objects + .promisor marker + config).
set -u
ROOT=${1:?scratch root}
rm -rf "$ROOT"; mkdir -p "$ROOT"; cd "$ROOT" || exit 9
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
unset GIT_DIR GIT_WORK_TREE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
ISO=(--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
     -c log.follow=false -c log.showRoot=true -c log.showSignature=false
     -c log.mailmap=false)
G() { git "${ISO[@]}" "$@"; }
mk() {  # mk DIR: synthetic history with nested trees, a tag and a report
  git init -q -b main "$1"; local d=$1
  [ "$(git -C "$d" rev-parse --show-toplevel)" = "$ROOT/$d" ] || { echo "toplevel guard"; exit 9; }
  git -C "$d" config user.name kama-shokunin; git -C "$d" config user.email k@x
  mkdir -p "$d/corpus" "$d/.ufo/reports/round-1" "$d/.ufo/reports/round-2" "$d/registry"
  echo one > "$d/a"; git -C "$d" add -A; GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" git -C "$d" commit -qm "round-1: a"
  echo src > "$d/corpus/SOURCES.md"; echo r1 > "$d/.ufo/reports/round-1/kama.md"
  git -C "$d" add -A; GIT_AUTHOR_DATE="@2000 +0000" GIT_COMMITTER_DATE="@2000 +0000" git -C "$d" commit -qm "round-1: b"
  echo r2 > "$d/.ufo/reports/round-2/kama.md"; printf '' > "$d/registry/report-landing-errata.tsv"
  git -C "$d" add -A; GIT_AUTHOR_DATE="@3000 +0000" GIT_COMMITTER_DATE="@3000 +0000" git -C "$d" commit -qm "round-2: c"
  git -C "$d" tag -a -m t t1 HEAD~1
}
promisorize() {  # promisorize DIR OID... : repack everything except OIDs into a promisor pack
  local d=$1; shift
  G -C "$d" repack -adq
  local all; all=$(G -C "$d" cat-file --batch-all-objects --batch-check='%(objectname)')
  local keep; keep=$(printf '%s\n' "$all" | grep -vxF -f <(printf '%s\n' "$@"))
  local pd; pd=$(G -C "$d" rev-parse --git-path objects/pack)
  mkdir -p "$ROOT/$d.new"
  local h; h=$(printf '%s\n' "$keep" | G -C "$d" pack-objects -q "$ROOT/$d.new/pack")
  rm -f "$ROOT/$d/$pd"/pack-*; mv "$ROOT/$d.new"/pack-* "$ROOT/$d/$pd/"; rmdir "$ROOT/$d.new"
  [ -n "$h" ] || { echo "pack failed $d"; exit 9; }; : > "$ROOT/$d/$pd/pack-$h.promisor"
  git -C "$d" config remote.origin.url /nonexistent
  git -C "$d" config remote.origin.promisor true
  git -C "$d" config extensions.partialclone origin
}
run() { local label=$1; shift; local out rc; out=$("$@" 2>&1); rc=$?
  printf '### %s\n$ %s\nrc=%s\n%s\n\n' "$label" "$*" "$rc" "$out"; }

mk L
C1=$(git -C L rev-parse HEAD~2); C2=$(git -C L rev-parse HEAD~1); C3=$(git -C L rev-parse HEAD)
T3=$(git -C L rev-parse HEAD^{tree}); TC3=$(git -C L rev-parse HEAD:corpus)
TR3=$(git -C L rev-parse HEAD:.ufo/reports); TR2_3=$(git -C L rev-parse HEAD:.ufo/reports/round-2)
TR1_2=$(git -C L rev-parse HEAD~1:.ufo/reports/round-1)
BSRC=$(git -C L rev-parse HEAD:corpus/SOURCES.md); BR2=$(git -C L rev-parse HEAD:.ufo/reports/round-2/kama.md)
BA=$(git -C L rev-parse HEAD:a); TAG=$(git -C L rev-parse t1)
NEVER=0123456789abcdef0123456789abcdef01234567
cp -a L Lfull   # complete, non-promisor twin
cp -a L Lmark; promisorize Lmark                 # complete, promisor-marked
cp -a L Lc1;   promisorize Lc1 "$C1"             # missing ancestor commit
cp -a L Lt;    promisorize Lt "$TC3" "$TR2_3"    # missing subtrees at tip
cp -a L Lb;    promisorize Lb "$BSRC" "$BR2"     # missing blobs at tip
cp -a L Lold;  promisorize Lold "$TR1_2"         # missing subtree in an older commit
cp -a L Ltag;  promisorize Ltag "$C2"            # tag present, target commit missing
cp -a L Lbare; rm -rf Lbare/.git/objects/pack/*; G -C Lbare repack -adq
  # non-promisor corruption twin: delete C1 with no promisor metadata
  pd=$(G -C Lbare rev-parse --git-path objects/pack)
  keep=$(G -C Lbare cat-file --batch-all-objects --batch-check='%(objectname)' | grep -vx "$C1")
  mkdir -p "$ROOT/Lbare.new"; printf '%s\n' "$keep" | G -C Lbare pack-objects -q "$ROOT/Lbare.new/pack" >/dev/null
  rm -f "$ROOT/Lbare/$pd"/pack-*; mv "$ROOT/Lbare.new"/pack-* "$ROOT/Lbare/$pd/"

{
echo "git: $(git --version)"
echo "C1=$C1 C2=$C2 C3=$C3 BA=$BA TAG=$TAG BSRC=$BSRC"
for r in Lfull Lmark Lc1 Ltag Lbare; do
  run "batch-check $r" G -C $r cat-file --batch-check <<<"$C1
$BA
$NEVER
$TAG
${C1:0:9}
${BA:0:9}"
  run "batch-check peel $r" G -C $r cat-file --batch-check <<<"$C1^{commit}
$BA^{commit}
${BA:0:9}^{commit}
$NEVER^{commit}
$TAG^{commit}
$T3^{commit}"
done
run "log Lfull" G -C Lfull log -z --format=%H main
for r in Lc1 Lbare; do run "log missing-ancestor $r" G -C $r log --format=%H main; done
run "log missing-ancestor Lc1 -z tr" sh -c "git ${ISO[*]} -C Lc1 log -z --format=%H main | tr '\0' ' '"
run "log diff-filter=A old-tree Lold" G -C Lold log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md
run "log diff-filter=A tip-tree Lt" G -C Lt log --diff-filter=A --format=%at -- .ufo/reports/round-2/kama.md
run "log diff-filter=A blobless Lb" G -C Lb log --diff-filter=A --format=%at -- .ufo/reports/round-2/kama.md
run "ls-tree SOURCES missing-corpus-tree Lt" G -C Lt ls-tree "$C3" -- corpus/SOURCES.md
run "ls-tree SOURCES full" G -C Lfull ls-tree "$C3" -- corpus/SOURCES.md
run "ls-tree -r reports missing-round2-tree Lt" G -C Lt ls-tree -r --name-only HEAD -- .ufo/reports
run "ls-tree -r reports full" G -C Lfull ls-tree -r --name-only HEAD -- .ufo/reports
run "show report missing-tree Lt" G -C Lt show HEAD:.ufo/reports/round-2/kama.md
run "show report missing-blob Lb" G -C Lb show HEAD:.ufo/reports/round-2/kama.md
run "cat-file blob missing Lb" G -C Lb cat-file blob "$BSRC"
run "rev-list --missing=print Lt" G -C Lt rev-list --objects --missing=print main
run "rev-list --missing=print Lc1" G -C Lc1 rev-list --objects --missing=print main
run "rev-list --exclude-promisor-objects Lc1" G -C Lc1 rev-list --exclude-promisor-objects main
run "fsck --connectivity-only Lmark" G -C Lmark fsck --connectivity-only --no-progress
run "fsck --connectivity-only Lt" G -C Lt fsck --connectivity-only --no-progress
run "cat-file --batch-check missing tag target Ltag" G -C Ltag cat-file -t "$TAG"
} 
