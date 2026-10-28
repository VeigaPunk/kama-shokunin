#!/bin/sh
# L03CensusDelta receipt — SOURCES census delta inputs, round 62.
# Read-only git + grep/awk. Run from the lane root. Scratch TMPDIR only.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/fast/scratch/hyaku/kama-r62/w/L03CensusDelta
BASE=a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3
MASTER=65d7cad0fce90e34de37527cde22e97b63b118bf
PAT='^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
export TMPDIR="$S/tmp"
mkdir -p "$TMPDIR"
cd "$LANE" || exit 2

echo "# measured: $(date -u +%FT%TZ)  host: $(uname -srm)"
echo "# lane root: $LANE"
echo "# pattern source: /home/vgpnk/Projects/shokunin/CORPUS.md:135 (sha256 $(sha256sum /home/vgpnk/Projects/shokunin/CORPUS.md | cut -d' ' -f1))"
echo "# base=$BASE"
echo "# master=$MASTER"
echo

echo "## blob identity of corpus/SOURCES.md"
printf 'base   %s\n' "$(git rev-parse "$BASE:corpus/SOURCES.md")"
printf 'master %s\n' "$(git rev-parse "$MASTER:corpus/SOURCES.md")"
printf 'sha256 base   %s\n' "$(git show "$BASE:corpus/SOURCES.md" | sha256sum | cut -d' ' -f1)"
printf 'sha256 master %s\n' "$(git show "$MASTER:corpus/SOURCES.md" | sha256sum | cut -d' ' -f1)"
printf 'diff base..master -- corpus/SOURCES.md: '
git diff --stat "$BASE..$MASTER" -- corpus/SOURCES.md | wc -l
printf 'commits base..master touching corpus/SOURCES.md: '
git log --oneline "$BASE..$MASTER" -- corpus/SOURCES.md | wc -l
echo

echo "## row count (CORPUS.md §Census frozen pattern)"
printf 'BASE   rows='; git show "$BASE:corpus/SOURCES.md"   | grep -cE "$PAT"
printf 'MASTER rows='; git show "$MASTER:corpus/SOURCES.md" | grep -cE "$PAT"
printf 'WORKTREE rows='; grep -cE "$PAT" corpus/SOURCES.md
echo

echo "## CORPUS.md §Census supporting commands, base / master / worktree"
for label in BASE MASTER WORKTREE; do
  case $label in
    BASE)   git show "$BASE:corpus/SOURCES.md"   > "$S/s.txt" ;;
    MASTER) git show "$MASTER:corpus/SOURCES.md" > "$S/s.txt" ;;
    WORKTREE) cp corpus/SOURCES.md "$S/s.txt" ;;
  esac
  f="$S/s.txt"
  echo "--- $label"
  printf 'rows            '; grep -cE "$PAT" "$f"
  printf 'indent<=3 rows  '; grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' "$f"
  printf 'malformed       '; awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' "$f"
  printf 'duplicate ids   '; awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' "$f" | sort | uniq -d | tr '\n' ' '; echo "(end)"
  printf 'tier            '; awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' "$f"
  printf 'status          '; awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' "$f"
  printf 'enum/tierinfl   '; awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' "$f" | wc -l
  printf 'missing used-by '; awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' "$f" | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done | wc -l
done
echo

echo "## row-id set delta base -> master -> worktree"
git show "$BASE:corpus/SOURCES.md"   | grep -oE '^\|[[:space:]]*S[0-9]{3,}' | grep -oE 'S[0-9]{3,}' | sort > "$S/base.ids"
git show "$MASTER:corpus/SOURCES.md" | grep -oE '^\|[[:space:]]*S[0-9]{3,}' | grep -oE 'S[0-9]{3,}' | sort > "$S/master.ids"
grep -oE '^\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]{3,}' | sort > "$S/wt.ids"
printf 'ids base=%s master=%s worktree=%s\n' "$(wc -l < "$S/base.ids")" "$(wc -l < "$S/master.ids")" "$(wc -l < "$S/wt.ids")"
echo "base vs master id-set diff:"; diff "$S/base.ids" "$S/master.ids"; echo "  (exit $?; empty = identical)"
echo "master vs worktree id-set diff:"; diff "$S/master.ids" "$S/wt.ids"; echo "  (exit $? above)"
echo

echo "## worktree in-flight SOURCES.md change"
printf 'git status --porcelain -- corpus/SOURCES.md: '; git status --porcelain -- corpus/SOURCES.md
printf 'git diff numstat: '; git diff --numstat -- corpus/SOURCES.md
printf 'worktree sha256: %s\n' "$(sha256sum corpus/SOURCES.md | cut -d' ' -f1)"
printf 'last commit touching SOURCES.md at master: '; git log -1 --format='%h %ci %s' "$MASTER" -- corpus/SOURCES.md
printf 'row count at that commit: '; git show "$(git log -1 --format=%H "$MASTER" -- corpus/SOURCES.md):corpus/SOURCES.md" | grep -cE "$PAT"
echo
echo "# TALLY: SOURCES rows base=265 master=265 delta=0 worktree=266 (+S526 uncommitted)"
