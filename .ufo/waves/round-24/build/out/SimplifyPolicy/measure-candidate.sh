#!/usr/bin/env bash
# Round-24 SimplifyPolicy measurement: BASE (lane tools/report-landing-audit.py)
# vs CANDIDATE (scratch copy with the promisor policy) on the same local
# fixtures. Local synthetic offline fixtures only; the only remote is file://.
set -u
BASE=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py
CAND=/fast/scratch/hyaku/kama-r24/SimplifyPolicy/lane/tools/report-landing-audit.py
ROOT=$(mktemp -d /fast/scratch/hyaku/kama-r24/SimplifyPolicy/meas.XXXXXX)
cd "$ROOT" || exit 1
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=kama-shokunin GIT_AUTHOR_EMAIL=a@x
export GIT_COMMITTER_NAME=kama-shokunin GIT_COMMITTER_EMAIL=a@x

commit() { # repo msg when path
    export GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000"
    printf '%s\n' "$2" > "$1/$4"; git -C "$1" add "$4"
    git -C "$1" -c commit.gpgsign=false commit -q -m "$2"
}

git init -q -b master src
git -C src config uploadpack.allowFilter true
commit src 'round-1: work' 1000 f
C1=$(git -C src rev-parse HEAD)
commit src 'round-1: more' 1500 g
C2=$(git -C src rev-parse HEAD)
GBLOB=$(git -C src rev-parse HEAD:g)
FAKE=abcdefabcdefabcdefabcdefabcdefabcdefabcd

git init -q -b master fleet
mkdir -p fleet/.ufo/reports/round-1
printf '# kama round 1\n\n## Landed changes\n\n- %s\n' "$C1" \
    > fleet/.ufo/reports/round-1/kama.md
git -C fleet add .ufo/reports/round-1/kama.md
export GIT_AUTHOR_DATE='@2000 +0000' GIT_COMMITTER_DATE='@2000 +0000'
git -C fleet -c commit.gpgsign=false commit -q -m 'round-1: report'
FLEETBLOB=$(git -C fleet rev-parse HEAD:.ufo/reports/round-1/kama.md)

git -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none \
    --no-local "file://$ROOT/src" lane-blobless
cp -a lane-blobless lane-hydrated
git -C lane-hydrated config --unset remote.origin.partialclonefilter
git -C lane-hydrated -c protocol.file.allow=always fetch --refetch -q origin \
    '+refs/heads/*:refs/remotes/origin/*'
cp -a lane-hydrated lane-marker
git -C lane-marker config --unset remote.origin.promisor
git -C lane-marker config --unset remote.origin.partialclonefilter
git -C lane-marker config --unset extensions.partialclone
git clone -q --no-local "$ROOT/src" lane-plain
printf 'hydrated blob present: '
git -C lane-hydrated --no-lazy-fetch cat-file -e "$GBLOB" && echo yes || echo no
printf 'blobless blob present: '
git -C lane-blobless --no-lazy-fetch cat-file -e "$GBLOB" && echo yes || echo no
printf 'fleet-crossrepo note blob: %s\n' "$(git -C fleet-crossrepo rev-parse HEAD:note.txt 2>&1)"

printf '\nC1=%s C2=%s GBLOB=%s FLEETBLOB=%s\n' "$C1" "$C2" "$GBLOB" "$FLEETBLOB"

mkfleet() { # name extra-line
    rm -rf "fleet-$1"; cp -a fleet "fleet-$1"
    printf '%s\n' "$2" >> "fleet-$1/.ufo/reports/round-1/kama.md"
    git -C "fleet-$1" add .ufo/reports/round-1/kama.md
    export GIT_AUTHOR_DATE='@2100 +0000' GIT_COMMITTER_DATE='@2100 +0000'
    git -C "fleet-$1" -c commit.gpgsign=false commit -q -m 'round-1: report v2'
}
# a fleet-owned blob the lane cannot have: the citation resolves in the fleet
printf 'fleet side note\n' > fleet/note.txt
git -C fleet add note.txt
export GIT_AUTHOR_DATE='@1900 +0000' GIT_COMMITTER_DATE='@1900 +0000'
git -C fleet -c commit.gpgsign=false commit -q -m 'note'
NOTE=$(git -C fleet rev-parse HEAD:note.txt)
mkfleet plain "see $FAKE"
mkfleet crossrepo "see $NOTE"
MISSINGBLOB=$(git -C lane-blobless rev-list --objects --all --missing=print \
    | sed -n 's/^?//p' | head -1)
mkfleet missingblob "see $MISSINGBLOB"
echo "missing blob in the blobless lane: $MISSINGBLOB"
# a fleet that is itself a promisor-backed partial clone: its report blob is
# not local, so the report evidence is unavailable
git -C fleet config uploadpack.allowFilter true
git -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none \
    --no-local "file://$ROOT/fleet" fleet-blobless
printf 'fleet report blob present: '
git -C fleet-blobless --no-lazy-fetch cat-file -e "$FLEETBLOB" && echo yes || echo no

verdict() { # auditor lane fleet
    out=$(python3 "$1" --lane-repo "$2" --fleet-repo "$3" --rounds 1 \
        --no-errata --json 2>&1)
    rc=$?
    kinds=$(printf '%s' "$out" | python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
    print(",".join(sorted({x["kind"] for r in d["results"]
                            for x in r["defects"]})) or "-")
except Exception:
    print("-")' 2>/dev/null)
    msg=$(printf '%s' "$out" | grep -m1 'could-not-evaluate' | cut -c1-110)
    printf 'exit=%s kinds=%s %s\n' "$rc" "${kinds:--}" "${msg:+| $msg}"
}

row() { # label lane fleet
    printf '%-46s base: %-52s cand: %s\n' "$1" \
        "$(verdict "$BASE" "$2" "$3")" "$(verdict "$CAND" "$2" "$3")"
}

printf '\n%-46s %-52s %s\n' 'CASE' 'BASE (r23 candidate)' 'CANDIDATE (scratch)'
row 'A plain lane, omission'            "$ROOT/lane-plain"     "$ROOT/fleet"
row 'B promisor-marked complete lane'    "$ROOT/lane-hydrated"  "$ROOT/fleet"
row 'C marker-only complete lane'       "$ROOT/lane-marker"    "$ROOT/fleet"
row 'D blobless lane, missing blob cited' "$ROOT/lane-blobless" "$ROOT/fleet-plain"
row 'E plain lane, fabricated hash'     "$ROOT/lane-plain"     "$ROOT/fleet-plain"
row 'F blobless lane, omission'         "$ROOT/lane-blobless"  "$ROOT/fleet"
row 'G blobless lane, wrong-type citation' "$ROOT/lane-blobless" "$ROOT/fleet-crossrepo"
row 'H blobless fleet (report blob absent)' "$ROOT/lane-plain" "$ROOT/fleet-blobless"
row 'I complete promisor lane + plain fleet' "$ROOT/lane-hydrated" "$ROOT/fleet-plain"
row 'J blobless lane, locally missing blob' "$ROOT/lane-blobless" "$ROOT/fleet-missingblob"
row 'K plain lane, wrong-type citation'   "$ROOT/lane-plain"     "$ROOT/fleet-crossrepo"
printf '\nROOT=%s\n' "$ROOT"
