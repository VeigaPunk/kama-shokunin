#!/usr/bin/env bash
# run-retro.sh — RETROSPECTIVE (round-20) reconstruction of the round-19 kama census
# receipts that round 19 cited but never committed (routed defect 5,
# corpus/lessons/round-19-verifier-spotcheck.md:194). Lane access is read-only
# (git show / git archive / git rev-parse / git log). For each side it builds
#   $SCRATCH/<side>       kama-shokunin/corpus/SOURCES.md from `git show <rev>:corpus/SOURCES.md`
#   $SCRATCH/<side>-tree  kama-shokunin from `git archive <rev>` (validate E11 needs used-by paths)
# each with a shokunin.conf holding only the fleet kama LANES row, runs the fleet census
# script, and writes OUT_DIR/census-<side>-retro.txt plus OUT_DIR/run.log.
# Refuses to overwrite any output; deletes the scratch on exit.
#   usage: bash run-retro.sh OUT_DIR
set -u -o noclobber -o pipefail
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
FLEET=/home/vgpnk/Projects/shokunin
CENSUS=$FLEET/scripts/sources-census.sh
SCRATCH=/tmp/kama-r20-CensusR19Retro
KAMA_ROW='kama|kama-shokunin|operability + calibration (local model serving and endpoint health)'
SIDES='before:8bf99cae7de2517fd4ebe209f3b940aeabb6b687 after:3389513f5107d5d77213cafa35ff2cbc18845100'
OUT_DIR=${1:?usage: run-retro.sh OUT_DIR}
LOG=$OUT_DIR/run.log

die() { echo "run-retro: $*" >&2; exit 2; }
[ -e "$SCRATCH" ] && die "scratch exists: $SCRATCH"
mkdir -p "$OUT_DIR" || die "cannot create $OUT_DIR"
: > "$LOG" || die "refusing to overwrite $LOG"
trap 'rm -rf "$SCRATCH"' EXIT
mkdir -p "$SCRATCH" || die "cannot create $SCRATCH"

RUN_LOCAL=$(date +%FT%T%:z); RUN_UTC=$(date -u +%FT%TZ); TODAY=$(date -u +%F)
SCRIPT_SHA=$(sha256sum "$CENSUS" | cut -d' ' -f1)
FLEET_REV=$(git -C "$FLEET" rev-parse HEAD)
SCRIPT_DIRTY=$(git -C "$FLEET" status --porcelain -- scripts/sources-census.sh)
GAWK_V=$(gawk 'BEGIN { print PROCINFO["version"] }')

logrun() { # label cmd... -> OUT (stdout), ERR (stderr), RC; appends all three to LOG
  local label=$1 errf=$SCRATCH/.stderr; shift
  OUT=$("$@" 2>"$errf"); RC=$?
  ERR=$(cat "$errf"); rm -f "$errf"
  {
    printf '### %s\n$' "$label"; printf ' %q' "$@"; printf '\n'
    [ -n "$OUT" ] && printf '%s\n' "$OUT"
    [ -n "$ERR" ] && printf '[stderr]\n%s\n' "$ERR"
    printf 'exit=%s\n\n' "$RC"
  } >> "$LOG"
}

{
  printf '# run-retro.sh log - RETROSPECTIVE (round-20); run %s (%s)\n' "$RUN_LOCAL" "$RUN_UTC"
  printf '# script=%s sha256=%s fleet_rev=%s script_dirty=[%s] gawk=%s TODAY=%s\n\n' \
    "$CENSUS" "$SCRIPT_SHA" "$FLEET_REV" "$SCRIPT_DIRTY" "$GAWK_V" "$TODAY"
} >> "$LOG"

for spec in $SIDES; do
  side=${spec%%:*}; rev=${spec#*:}
  root=$SCRATCH/$side; troot=$SCRATCH/$side-tree
  src=$root/kama-shokunin/corpus/SOURCES.md
  mkdir -p "$root/kama-shokunin/corpus" "$troot/kama-shokunin" || die "mkdir $side"
  git -C "$LANE" show "$rev:corpus/SOURCES.md" > "$src" || die "git show $rev"
  git -C "$LANE" archive "$rev" | tar -x -C "$troot/kama-shokunin" || die "git archive $rev"
  commit=$(git -C "$LANE" log -1 --format='%ci %s' "$rev")
  src_sha=$(sha256sum "$src" | cut -d' ' -f1)

  logrun "$side: SOURCES.md blob id" git -C "$LANE" rev-parse "$rev:corpus/SOURCES.md"
  blob=$OUT
  logrun "$side: git-archive copy equals git-show copy" cmp "$src" "$troot/kama-shokunin/corpus/SOURCES.md"
  logrun "$side: tracked paths at rev" bash -c 'git -C "$1" ls-tree -r --name-only "$2" | wc -l' _ "$LANE" "$rev"
  logrun "$side: extracted files and symlinks" bash -c 'find "$1" \( -type f -o -type l \) | wc -l' _ "$troot/kama-shokunin"
  logrun "$side: registry rows by grep (spot-check oracle)" grep -cE '^\| *S[0-9]{3} ' "$src"
  logrun "$side: assigned census command before any shokunin.conf exists" "$CENSUS" census --root "$root" kama

  printf '%s\n' 'LANES="' "$KAMA_ROW" '"' > "$root/shokunin.conf" || die "conf $side"
  cp -- "$root/shokunin.conf" "$troot/shokunin.conf" || die "conf copy $side"

  logrun "$side: census, SOURCES.md-only root" "$CENSUS" census --root "$root" kama
  c_out=$OUT c_err=$ERR c_rc=$RC
  logrun "$side: validate, SOURCES.md-only root (E11 here = used-by path not materialized)" \
    "$CENSUS" validate --root "$root" kama
  s_rc=$RC
  s_e11=$(printf '%s\n' "$OUT" | grep -c $'\tE11\t')
  s_other=$(printf '%s\n' "$OUT" | grep -E $'\t[EW][0-9]+\t' | grep -vc $'\tE11\t')
  logrun "$side: census, committed-tree root" "$CENSUS" census --root "$troot" kama
  t_out=$OUT
  logrun "$side: validate, committed-tree root" "$CENSUS" validate --root "$troot" kama
  v_out=$OUT v_err=$ERR v_rc=$RC
  same=no; [ "$c_out" = "$t_out" ] && same=yes
  printf '### %s: census stdout identical on both roots: %s\n\n' "$side" "$same" >> "$LOG"

  rf=$OUT_DIR/census-$side-retro.txt
  {
    printf '# RETROSPECTIVE (round-20): reconstructs the round-19 census-%s receipt that round 19 cited but never committed; not a round-19 run\n' "$side"
    printf '# source_revision=%s (%s)\n' "$rev" "$commit"
    printf '# source_file=corpus/SOURCES.md blob=%s sha256=%s\n' "$blob" "$src_sha"
    printf '# census_root=%s (kama-shokunin/corpus/SOURCES.md from git show %s:corpus/SOURCES.md; shokunin.conf = fleet kama LANES row only)\n' "$root" "$rev"
    printf '# validate_root=%s (kama-shokunin from git archive %s so E11 can see used-by paths; same shokunin.conf)\n' "$troot" "$rev"
    printf '# command_validate=%s validate --root %s kama\n' "$CENSUS" "$troot"
    printf '# command_census=%s census --root %s kama\n' "$CENSUS" "$root"
    printf '# script_sha256=%s fleet_rev=%s gawk=%s TODAY=%s (script default, date -u +%%F)\n' "$SCRIPT_SHA" "$FLEET_REV" "$GAWK_V" "$TODAY"
    printf '# run_date=%s (%s); scratch roots deleted after the run; every command and exit in run.log\n' "$RUN_LOCAL" "$RUN_UTC"
    printf '# cross-check: census stdout identical on validate_root=%s; validate on census_root exit=%s with %s E11 lines (reconstruction artifact, not a registry verdict) and %s other E/W lines\n' "$same" "$s_rc" "$s_e11" "$s_other"
    [ -n "$v_out" ] && printf '%s\n' "$v_out"
    [ -n "$v_err" ] && printf '%s\n' "$v_err" | sed 's/^/# validate stderr: /'
    printf 'exit=%s\n' "$v_rc"
    [ -n "$c_out" ] && printf '%s\n' "$c_out"
    [ -n "$c_err" ] && printf '%s\n' "$c_err" | sed 's/^/# census stderr: /'
    printf 'exit=%s\n' "$c_rc"
    printf 'measured_at=%s rev=%s label=RETROSPECTIVE(round-20)\n' "$RUN_LOCAL" "$rev"
  } > "$rf" || die "refusing to overwrite $rf"
done
printf '# done\n' >> "$LOG"
