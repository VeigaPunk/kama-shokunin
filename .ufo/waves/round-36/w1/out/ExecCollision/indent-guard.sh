#!/bin/bash
# Seat-local re-run of the indent-guard. Does not edit corpus/SOURCES.md.
set -u
SEAT="/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w1/out/ExecCollision"
GUARD="/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/guard"
REG="/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md"
PAT_COL0='^\|[[:space:]]*S[0-9]{3,}'
PAT_SPACE='^ {0,3}\|[[:space:]]*S[0-9]{3,}'
cd "$SEAT"

log() { printf '%s\n' "$*"; }

log "=== grep ==="
grep --version | head -n 1
log "PAT_COL0=${PAT_COL0}"
log "PAT_SPACE=${PAT_SPACE}"

log "=== lane registry fingerprint before ==="
sha256sum "$REG"
if git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "git_status_sources=$(git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -- corpus/SOURCES.md | wc -c)"
  log "git_diff_sources_exit_placeholder"
  git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff -- corpus/SOURCES.md | wc -c | awk '{print "git_diff_sources_bytes="$1}'
  log "worktree_blob=$(git -C /home/vgpnk/Projects/shokunin/kama-shokunin hash-object corpus/SOURCES.md)"
  log "head_blob=$(git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD:corpus/SOURCES.md)"
else
  log "git_unavailable"
fi
stat -c 'sources_mtime=%y sources_size=%s' "$REG"

log "=== write seat fixtures (printf, not the lane registry) ==="
printf '| S001 | real |\n  | S002 | indented |\n' > "$SEAT/scratch-registry.md"
printf '| S002 | staged |\n' > "$SEAT/scratch-staged.md"
log "seat_registry_bytes=$(wc -c < "$SEAT/scratch-registry.md")"
log "seat_staged_bytes=$(wc -c < "$SEAT/scratch-staged.md")"
log "od_seat_registry:"
od -An -tx1 "$SEAT/scratch-registry.md"
log "od_seat_staged:"
od -An -tx1 "$SEAT/scratch-staged.md"
if cmp -s "$SEAT/scratch-registry.md" "$GUARD/scratch-registry.md"; then
  log "cmp_seat_registry_vs_guard=identical"
else
  log "cmp_seat_registry_vs_guard=DIFFER"
fi
if cmp -s "$SEAT/scratch-staged.md" "$GUARD/scratch-staged.md"; then
  log "cmp_seat_staged_vs_guard=identical"
else
  log "cmp_seat_staged_vs_guard=DIFFER"
fi

extract() {
  local pat="$1" file="$2" raw_out="$3" id_out="$4" tag="$5"
  local g1=0 g2=0
  if grep -oE "$pat" "$file" > "$raw_out"; then
    g1=0
  else
    g1=$?
  fi
  if [[ -s "$raw_out" ]]; then
    if grep -oE 'S[0-9]+' "$raw_out" | LC_ALL=C sort > "$id_out"; then
      g2=0
    else
      g2=$?
    fi
  else
    : > "$id_out"
    g2=1
  fi
  log "${tag}_raw_grep_exit=${g1}"
  log "${tag}_id_grep_exit=${g2}"
  log "${tag}_raw_bytes=$(wc -c < "$raw_out")"
  log "${tag}_id_bytes=$(wc -c < "$id_out")"
  log "${tag}_raw_begin"
  cat "$raw_out"
  log "${tag}_raw_end"
  log "${tag}_ids_begin"
  cat "$id_out"
  log "${tag}_ids_end"
}

log "=== seat extractors ==="
extract "$PAT_COL0" "$SEAT/scratch-registry.md" "$SEAT/seat-col0.raw" "$SEAT/seat-col0-ids" seat_col0_reg
extract "$PAT_SPACE" "$SEAT/scratch-registry.md" "$SEAT/seat-space.raw" "$SEAT/seat-space-ids" seat_space_reg
extract "$PAT_COL0" "$SEAT/scratch-staged.md" "$SEAT/seat-staged-col0.raw" "$SEAT/seat-staged-col0-ids" seat_col0_staged
extract "$PAT_SPACE" "$SEAT/scratch-staged.md" "$SEAT/seat-staged-space.raw" "$SEAT/seat-staged-space-ids" seat_space_staged

log "=== seat collisions ==="
LC_ALL=C comm -12 "$SEAT/seat-col0-ids" "$SEAT/seat-staged-col0-ids" > "$SEAT/seat-col0-collisions"
col0_comm=$?
LC_ALL=C comm -12 "$SEAT/seat-space-ids" "$SEAT/seat-staged-space-ids" > "$SEAT/seat-space-collisions"
space_comm=$?
log "seat_col0_comm_exit=${col0_comm}"
log "seat_space_comm_exit=${space_comm}"
log "seat_col0_collision_bytes=$(wc -c < "$SEAT/seat-col0-collisions")"
log "seat_space_collision_bytes=$(wc -c < "$SEAT/seat-space-collisions")"
log "seat_col0_collision_lines=$(wc -l < "$SEAT/seat-col0-collisions")"
log "seat_space_collision_lines=$(wc -l < "$SEAT/seat-space-collisions")"
log "seat_col0_collisions_begin"
cat "$SEAT/seat-col0-collisions"
log "seat_col0_collisions_end"
log "seat_space_collisions_begin"
cat "$SEAT/seat-space-collisions"
log "seat_space_collisions_end"

log "=== sort -c ==="
LC_ALL=C sort -c "$SEAT/seat-col0-ids" && log seat_col0_ids_sorted=yes
LC_ALL=C sort -c "$SEAT/seat-space-ids" && log seat_space_ids_sorted=yes
LC_ALL=C sort -c "$SEAT/seat-staged-col0-ids" && log seat_staged_col0_ids_sorted=yes
LC_ALL=C sort -c "$SEAT/seat-staged-space-ids" && log seat_staged_space_ids_sorted=yes

log "=== python set intersection cross-check ==="
python3 - <<'PY'
from pathlib import Path
seat = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w1/out/ExecCollision")
def load(name):
    text = (seat / name).read_text()
    return [line for line in text.splitlines() if line]
col0_reg, space_reg = load("seat-col0-ids"), load("seat-space-ids")
col0_st, space_st = load("seat-staged-col0-ids"), load("seat-staged-space-ids")
col0_hit = sorted(set(col0_reg) & set(col0_st))
space_hit = sorted(set(space_reg) & set(space_st))
print(f"py_col0_intersection={col0_hit}")
print(f"py_space_intersection={space_hit}")
print(f"py_col0_matches_comm={col0_hit == load('seat-col0-collisions')}")
print(f"py_space_matches_comm={space_hit == load('seat-space-collisions')}")
PY

log "=== reproduce target guard outputs from guard fixtures (read-only inputs) ==="
extract "$PAT_COL0" "$GUARD/scratch-registry.md" "$SEAT/repro-col0.raw" "$SEAT/repro-col0-ids" repro_col0_reg
extract "$PAT_SPACE" "$GUARD/scratch-registry.md" "$SEAT/repro-space.raw" "$SEAT/repro-space-ids" repro_space_reg
extract "$PAT_SPACE" "$GUARD/scratch-staged.md" "$SEAT/repro-staged.raw" "$SEAT/repro-staged-ids" repro_staged
# column-zero staged extract, for the collision the target stored as a single staged-ids list
extract "$PAT_COL0" "$GUARD/scratch-staged.md" "$SEAT/repro-staged-col0.raw" "$SEAT/repro-staged-col0-ids" repro_staged_col0
LC_ALL=C comm -12 "$SEAT/repro-col0-ids" "$SEAT/repro-staged-ids" > "$SEAT/repro-col0-collisions"
LC_ALL=C comm -12 "$SEAT/repro-space-ids" "$SEAT/repro-staged-ids" > "$SEAT/repro-space-collisions"
for pair in \
  "repro-col0-ids:col0-ids" \
  "repro-space-ids:space-ids" \
  "repro-staged-ids:staged-ids" \
  "repro-col0-collisions:col0-collisions" \
  "repro-space-collisions:space-collisions"
do
  left="${pair%%:*}"
  right="${pair##*:}"
  if cmp -s "$SEAT/$left" "$GUARD/$right"; then
    log "cmp_${right}=identical"
  else
    log "cmp_${right}=DIFFER"
  fi
done

log "=== zero-ids pattern probe (reproduction, not provenance) ==="
PAT_ANY='^[[:space:]]*\|[[:space:]]*S[0-9]{3,}'
PAT_STAR='^ *\|[[:space:]]*S[0-9]{3,}'
extract "$PAT_ANY" "$GUARD/scratch-registry.md" "$SEAT/probe-any.raw" "$SEAT/probe-any-ids" probe_any
extract "$PAT_STAR" "$GUARD/scratch-registry.md" "$SEAT/probe-star.raw" "$SEAT/probe-star-ids" probe_star
if cmp -s "$SEAT/probe-any-ids" "$GUARD/zero-ids"; then
  log "cmp_zero_ids_vs_any_space=identical"
else
  log "cmp_zero_ids_vs_any_space=DIFFER"
fi
if cmp -s "$SEAT/probe-star-ids" "$GUARD/zero-ids"; then
  log "cmp_zero_ids_vs_star_space=identical"
else
  log "cmp_zero_ids_vs_star_space=DIFFER"
fi
if cmp -s "$SEAT/repro-space-ids" "$GUARD/zero-ids"; then
  log "cmp_zero_ids_vs_space=identical"
else
  log "cmp_zero_ids_vs_space=DIFFER"
fi

log "=== labeled 4-space negative control (not the assigned collision) ==="
printf '    | S002 | four spaces |\n' > "$SEAT/scratch-four-space.md"
extract "$PAT_COL0" "$SEAT/scratch-four-space.md" "$SEAT/four-col0.raw" "$SEAT/four-col0-ids" four_col0
extract "$PAT_SPACE" "$SEAT/scratch-four-space.md" "$SEAT/four-space.raw" "$SEAT/four-space-ids" four_space
log "four_col0_id_bytes=$(wc -c < "$SEAT/four-col0-ids")"
log "four_space_id_bytes=$(wc -c < "$SEAT/four-space-ids")"

log "=== lane registry fingerprint after ==="
sha256sum "$REG"
if git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "git_status_sources_after=$(git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -- corpus/SOURCES.md | wc -c)"
  git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff -- corpus/SOURCES.md | wc -c | awk '{print "git_diff_sources_bytes_after="$1}'
  log "worktree_blob_after=$(git -C /home/vgpnk/Projects/shokunin/kama-shokunin hash-object corpus/SOURCES.md)"
  log "head_blob_after=$(git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD:corpus/SOURCES.md)"
fi
stat -c 'sources_mtime_after=%y sources_size_after=%s' "$REG"
log "=== done ==="
