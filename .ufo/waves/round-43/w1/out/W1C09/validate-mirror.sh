#!/usr/bin/env bash
# validate-mirror.sh — prove a two-row append + entry + lesson against the frozen census gate
# BEFORE anything is written into the lane tree.
#
# Usage: validate-mirror.sh <rows-file> <entry-file> <lesson-file>
#
#   rows-file    registry rows to append to the SOURCES.md `## Registry` table (one row per
#                line, 11 cells, exactly as they would land; blank lines and `#` comments
#                are skipped). Placeholders (`<...>`, `TBD`, `PLACEHOLDER`) are counted and
#                reported as `placeholder_rows=<n>`; they are not stripped.
#   entry-file   the knowledge entry; copied into the mirror at its repo-relative path
#                (the path from the last `corpus/` component onward).
#   lesson-file  the round lesson; same rule.
#
# Builds a scratch mirror at $MIRROR (default /fast/scratch/kama-r43/seats/W1C09/mirror) as a
# copy of the lane clone's corpus/ (source $LANE_CLONE, default /fast/scratch/kama-r43/clone)
# with the rows inserted after the last row of the `## Registry` table, then runs
# /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md
# and prints `census_exit=<code>`. Exit status is the census status (0 clean/warnings,
# 1 E/W findings, 2 usage/missing registry); 2 also covers bad arguments.
#
# Read-only with respect to the lane clone and the fleet repo: writes only under $MIRROR.
set -u

CENSUS=/home/vgpnk/Projects/shokunin/scripts/sources-census.sh
MIRROR=${MIRROR:-/fast/scratch/kama-r43/seats/W1C09/mirror}
LANE_CLONE=${LANE_CLONE:-/fast/scratch/kama-r43/clone}
TODAY=${TODAY:-2026-10-25}

die() { echo "validate-mirror: ERROR: $*" >&2; exit 2; }

[ $# -eq 3 ] || die "usage: validate-mirror.sh <rows-file> <entry-file> <lesson-file>"
ROWS=$1; ENTRY=$2; LESSON=$3
[ -s "$ROWS" ] || die "rows-file missing or empty: $ROWS"
[ -f "$ENTRY" ] || die "entry-file not found: $ENTRY"
[ -f "$LESSON" ] || die "lesson-file not found: $LESSON"
[ -f "$LANE_CLONE/corpus/SOURCES.md" ] || die "lane clone registry not found: $LANE_CLONE/corpus/SOURCES.md"
[ -x "$CENSUS" ] || [ -f "$CENSUS" ] || die "census gate not found: $CENSUS"

relpath() { # repo-relative path from the last `corpus/` component
  local p=$1
  case "$p" in
    corpus/*) printf '%s\n' "$p" ;;
    *) case "$p" in
         */corpus/*) printf 'corpus/%s\n' "${p##*/corpus/}" ;;
         *) die "no corpus/ component in path: $p" ;;
       esac ;;
  esac
}

ENTRY_REL=$(relpath "$ENTRY") || exit 2
LESSON_REL=$(relpath "$LESSON") || exit 2

rm -rf -- "$MIRROR" || die "cannot clear mirror $MIRROR"
mkdir -p -- "$MIRROR" || die "cannot create mirror $MIRROR"
# Mirror = the lane worktree without .git and without .ufo/waves history, so that every
# used-by path the registry already names resolves and the gate verdict is about the append.
tar -C "$LANE_CLONE" --exclude=.git --exclude=./.ufo -cf - . | tar -C "$MIRROR" -xf - \
  || die "cannot copy the lane worktree into $MIRROR"

REG=$MIRROR/corpus/SOURCES.md
[ -f "$REG" ] || die "mirror registry missing after copy: $REG"

# .ufo paths that existing registry rows name as used-by are copied as real bytes.
while IFS= read -r p; do
  [ -n "$p" ] || continue
  [ -e "$LANE_CLONE/$p" ] || continue
  mkdir -p -- "$MIRROR/$(dirname -- "$p")"
  cp -- "$LANE_CLONE/$p" "$MIRROR/$p"
done < <(grep -oE '\.ufo/[A-Za-z0-9._/-]+' -- "$REG" | sort -u)

# Baseline gate run on the unamended mirror: gives the noise floor the append is judged against.
BASE_OUT=$MIRROR/.census-baseline.out
"$CENSUS" validate --today "$TODAY" --file "$REG" > "$BASE_OUT" 2>&1
BASE_EXIT=$?

# Locate the end of the `## Registry` table: last `|`-leading line between the heading and
# the next `## ` heading.
INSERT_AT=$(awk '
  /^ {0,3}##[[:space:]]+Registry[[:space:]]*$/ { inreg=1; next }
  inreg && /^ {0,3}##[[:space:]]/ { exit }
  inreg && /^ {0,3}\|/ { last=NR }
  END { print last+0 }
' "$REG")
[ "$INSERT_AT" -gt 0 ] || die "could not find the ## Registry table in $REG"

ROWS_CLEAN=$(mktemp "${TMPDIR:-/tmp}/w1c09-rows.XXXXXX") || die "mktemp failed"
trap 'rm -f -- "$ROWS_CLEAN"' EXIT
grep -vE '^[[:space:]]*(#|$)' -- "$ROWS" > "$ROWS_CLEAN" || true
N_ROWS=$(wc -l < "$ROWS_CLEAN")
[ "$N_ROWS" -gt 0 ] || die "no usable rows in $ROWS"
PLACEHOLDERS=$(grep -cE '<[^>]*>|TBD|PLACEHOLDER' -- "$ROWS_CLEAN" || true)

# Pre-append id collision against the mirror registry (the failure this script exists to catch).
ids_of() { grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' -- "$1" | grep -oE 'S[0-9]+' | sort -u; }
ids_of "$REG" > "$MIRROR/.reg-ids"
ids_of "$ROWS_CLEAN" > "$MIRROR/.row-ids"
PRE_COLL=$(comm -12 "$MIRROR/.reg-ids" "$MIRROR/.row-ids" | tr '\n' ' ')
MAX_BEFORE=$(sort -V "$MIRROR/.reg-ids" | tail -1)

head -n "$INSERT_AT" -- "$REG" > "$REG.new"
cat -- "$ROWS_CLEAN" >> "$REG.new"
tail -n +"$((INSERT_AT + 1))" -- "$REG" >> "$REG.new"
mv -- "$REG.new" "$REG"

mkdir -p -- "$MIRROR/$(dirname -- "$ENTRY_REL")" "$MIRROR/$(dirname -- "$LESSON_REL")"
cp -- "$ENTRY" "$MIRROR/$ENTRY_REL"
cp -- "$LESSON" "$MIRROR/$LESSON_REL"

echo "mirror=$MIRROR"
echo "rows_appended=$N_ROWS"
echo "placeholder_rows=$PLACEHOLDERS"
echo "registry_last_id_before=$MAX_BEFORE"
echo "row_ids=$(tr '\n' ' ' < "$MIRROR/.row-ids")"
echo "pre_append_id_collisions=[${PRE_COLL% }]"
echo "entry=$ENTRY_REL"
echo "lesson=$LESSON_REL"
echo "baseline_exit=$BASE_EXIT baseline_lines=$(wc -l < "$BASE_OUT")"
echo "census=--file $REG"
echo "--- census output ---"
AFTER_OUT=$MIRROR/.census-after.out
"$CENSUS" validate --today "$TODAY" --file "$REG" > "$AFTER_OUT" 2>&1
rc=$?
cat -- "$AFTER_OUT"
sort -- "$BASE_OUT" > "$AFTER_OUT.base.sorted"
sort -- "$AFTER_OUT" > "$AFTER_OUT.sorted"
comm -13 -- "$AFTER_OUT.base.sorted" "$AFTER_OUT.sorted" > "$AFTER_OUT.delta"
echo "--- findings introduced by the append (delta vs baseline) ---"
cat -- "$AFTER_OUT.delta"
echo "new_findings=$(wc -l < "$AFTER_OUT.delta")"
echo "census_exit=$rc"
exit "$rc"
