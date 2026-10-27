#!/usr/bin/env bash
# hygiene-recheck.sh - round-50 w1 end-of-wave hygiene re-check (READ-ONLY).
#
# Written by seat X17Cleanup. It inspects host, scratch, fleet repo and lane repo
# and never writes, kills, deletes, fetches or commits. Safe to run at any time;
# `--final` turns the wave-leftover checks into FAILs (run it after the wave closes,
# before integrating, so the L1 measures rather than trusting a stale snapshot).
#
# usage: hygiene-recheck.sh [--final]
# env:   SCRATCH=/fast/scratch/hyaku/kama-r50   LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
#        FLEET=/home/vgpnk/Projects/shokunin    HYAKU=/fast/scratch/hyaku
# exit:  0 = no FAIL, 1 = at least one FAIL
set -uo pipefail

FINAL=0
[ "${1:-}" = "--final" ] && FINAL=1

SCRATCH=${SCRATCH:-/fast/scratch/hyaku/kama-r50}
HYAKU=${HYAKU:-/fast/scratch/hyaku}
LANE=${LANE:-/home/vgpnk/Projects/shokunin/kama-shokunin}
FLEET=${FLEET:-/home/vgpnk/Projects/shokunin}
OUT=$LANE/.ufo/waves/round-50/w1/out

fails=0
pass() { printf 'PASS  %s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*"; fails=$((fails + 1)); }
head_() { printf '\n== %s ==\n' "$*"; }

printf 'hygiene-recheck %s mode=%s scratch=%s\n' "$(date -Is)" \
  "$([ "$FINAL" = 1 ] && echo final || echo snapshot)" "$SCRATCH"

# 1. llama-server binaries belonging to this wave's scratch.
#    pgrep -x matches the executable name only; `pgrep -af llama-server` also matches
#    python tools whose argv merely contains the string, so it is NOT a valid check.
head_ "1. llama-server binaries (exe name), wave-scoped"
mapfile -t SRV < <(pgrep -x llama-server 2>/dev/null)
wave_srv=0
for p in "${SRV[@]:-}"; do
  [ -n "${p:-}" ] || continue
  cwd=$(readlink "/proc/$p/cwd" 2>/dev/null)
  cmd=$(tr '\0' ' ' <"/proc/$p/cmdline" 2>/dev/null)
  age=$(ps -o etimes= -p "$p" 2>/dev/null | tr -d ' ')
  ppid=$(awk '{print $4}' "/proc/$p/stat" 2>/dev/null)
  case "$cmd$cwd" in
    *"$SCRATCH"*)
      wave_srv=$((wave_srv + 1))
      printf '      wave llama-server pid=%s ppid=%s age=%ss cwd=%s\n' "$p" "$ppid" "$age" "$cwd"
      ;;
    *) printf '      other llama-server pid=%s age=%ss cwd=%s (not this wave)\n' "$p" "$age" "$cwd" ;;
  esac
done
if [ "$wave_srv" -eq 0 ]; then
  pass "no llama-server binary from $SCRATCH is running"
elif [ "$FINAL" = 1 ]; then
  fail "$wave_srv wave llama-server still running after wave close (see pids above)"
else
  warn "$wave_srv wave llama-server running (expected while seats are live)"
fi

# 2. Orphaned wave processes. On a systemd --user session an orphan reparents to
#    `/usr/lib/systemd/systemd --user`, NOT to pid 1, so both parents must be caught:
#    the round-49 stub servers this wave inherited were ppid=1494 (systemd --user).
head_ "2. orphaned wave processes (ppid=1 or reparented to systemd)"
orph=0
stale_orph=0
is_orphan_parent() {
  local ppid=$1 pcomm
  [ "$ppid" = "1" ] && return 0
  pcomm=$(ps -o comm= -p "$ppid" 2>/dev/null | tr -d ' ')
  [ "$pcomm" = "systemd" ] && return 0
  return 1
}
for p in $(pgrep -f "$SCRATCH|round50-" 2>/dev/null); do
  ppid=$(awk '{print $4}' "/proc/$p/stat" 2>/dev/null)
  if is_orphan_parent "${ppid:-0}"; then
    orph=$((orph + 1))
    age=$(ps -o etimes= -p "$p" 2>/dev/null | tr -d ' ')
    # A live seat that deliberately SIGKILLs a parent (teardown experiments J2/Sen3)
    # leaves a short-lived orphan by design; only a long-lived one is a leftover.
    if [ "${age:-0}" -gt 300 ]; then stale_orph=$((stale_orph + 1)); tag="STALE"; else tag="fresh"; fi
    printf '      %s orphan pid=%s ppid=%s age=%ss :: %s\n' "$tag" "$p" "$ppid" "${age:-?}" \
      "$(tr '\0' ' ' <"/proc/$p/cmdline" 2>/dev/null | cut -c1-110)"
  fi
done
if [ "$stale_orph" -gt 0 ] || { [ "$FINAL" = 1 ] && [ "$orph" -gt 0 ]; }; then
  fail "$orph orphaned wave process(es), $stale_orph older than 300s"
elif [ "$orph" -gt 0 ]; then
  warn "$orph fresh orphan(s) (<300s) - expected only during a live teardown experiment"
else
  pass "no orphaned kama-r50 process"
fi

# 3. Cross-wave leftovers from earlier kama rounds (named, not this lane's to kill).
#    Match the scratch PATH with its trailing slash: every round-50 live tool passes
#    `--alias kama-r48-live`, so a bare kama-r4[0-9] pattern false-matches this wave.
head_ "3. earlier-round kama leftovers (informational)"
prev=0
for p in $(pgrep -f "$HYAKU/kama-r4[0-9]/" 2>/dev/null); do
  ppid=$(awk '{print $4}' "/proc/$p/stat" 2>/dev/null)
  prev=$((prev + 1))
  printf '      pid=%s ppid=%s age=%ss :: %s\n' "$p" "$ppid" \
    "$(ps -o etimes= -p "$p" 2>/dev/null | tr -d ' ')" \
    "$(tr '\0' ' ' <"/proc/$p/cmdline" 2>/dev/null | cut -c1-110)"
done
[ "$prev" -eq 0 ] && pass "no earlier-round kama process" || warn "$prev earlier-round kama process(es) still alive (report to L1; do not kill)"

# 4. Loopback LISTEN sockets owned by wave/previous-wave pids.
head_ "4. loopback listeners owned by kama scratch pids"
own=0
while read -r port pid; do
  [ -n "${pid:-}" ] || continue
  cmd=$(tr '\0' ' ' <"/proc/$pid/cmdline" 2>/dev/null)
  case "$cmd" in
    # path form with trailing slash: `--alias kama-r48-live` must not match
    *"$SCRATCH"*|*"$HYAKU"/kama-r4[0-9]/*)
      own=$((own + 1))
      printf '      127.0.0.1:%s pid=%s :: %s\n' "$port" "$pid" "$(printf '%s' "$cmd" | cut -c1-100)"
      ;;
  esac
done < <(ss -ltnp 2>/dev/null | grep -E '127\.0\.0\.1:' |
         sed -nE 's/.*127\.0\.0\.1:([0-9]+).*pid=([0-9]+).*/\1 \2/p')
if [ "$own" -eq 0 ]; then
  pass "no kama-scratch process holds a loopback listener"
elif [ "$FINAL" = 1 ]; then
  fail "$own loopback listener(s) held by kama-scratch processes after wave close"
else
  warn "$own loopback listener(s) held by kama-scratch processes (see above)"
fi

# 5. Fleet repo must not name this lane's seats.
head_ "5. fleet repo porcelain"
fst=$(git -C "$FLEET" status --porcelain 2>/dev/null)
if [ -z "$fst" ]; then
  pass "fleet repo clean"
else
  printf '%s\n' "$fst" | sed 's/^/      /'
  if printf '%s\n' "$fst" | grep -q 'kama-shokunin'; then
    fail "fleet porcelain names kama-shokunin (a seat wrote outside its lane paths)"
  else
    warn "fleet porcelain names other paths (not this lane's; do not delete)"
  fi
fi

# 6. Lane repo porcelain. The invariant is containment: a seat may only add untracked
#    paths INSIDE .ufo/waves/round-50/ (its own wave), never modify a lane file. Wave-root
#    seat dirs are legal when w1/dispatch.json names them (round 50: X1Assimilation).
head_ "6. lane repo porcelain"
lst=$(git -C "$LANE" status --porcelain 2>/dev/null)
if [ -z "$lst" ]; then
  pass "lane repo clean"
else
  outside=$(printf '%s\n' "$lst" | grep -vE '^\?\? \.ufo/waves/round-50/')
  if [ -n "$outside" ]; then
    printf '%s\n' "$outside" | sed 's/^/      OUTSIDE-WAVE /'
    fail "lane change outside .ufo/waves/round-50/ (a seat edited or added a lane file)"
  else
    pass "no lane change outside .ufo/waves/round-50/ (no in-place lane edit)"
  fi
  untidy=$(printf '%s\n' "$lst" | grep -E '^\?\? \.ufo/waves/round-50/' |
           grep -vE '^\?\? \.ufo/waves/round-50/(w1\.ready(\.dispatched)?|w1/out/[^/]+(\.md|/)|X1Assimilation/)$' || true)
  if [ -n "$untidy" ]; then
    printf '%s\n' "$untidy" | sed 's/^/      UNTIDY /'
    warn "untracked path under round-50 outside scaffolding/out (check the dispatch assigns it)"
  fi
fi

# 7. Stray entries at the shared scratch root (seats must stay in $SCRATCH/<Seat>/).
#    Lane scratch dirs are named <lane>-r<NN>; anything else at the root, or a
#    run-receipt-* / mktemp dir, means a driver used a bare `mktemp -d`.
head_ "7. strays at $HYAKU root (last 12h)"
strays=$(find "$HYAKU" -mindepth 1 -maxdepth 1 -newermt '-12 hours' \
           ! -name "$(basename "$SCRATCH")" 2>/dev/null |
         grep -vE '/[a-z]+-r[0-9]+$' || true)
if [ -z "$strays" ]; then
  pass "no recent stray entries at scratch root"
else
  printf '%s\n' "$strays" | sed 's/^/      /'
  warn "$(printf '%s\n' "$strays" | wc -l) recent entr(y|ies) at scratch root (mktemp -d without -p \$S)"
fi

# 8. Scratch and out-dir size.
head_ "8. sizes"
printf '      scratch total: %s\n' "$(du -sh "$SCRATCH" 2>/dev/null | cut -f1)"
du -sh "$SCRATCH"/* 2>/dev/null | sort -rh | head -10 | sed 's/^/      /'
printf '      out total:     %s (%s files)\n' \
  "$(du -sh "$OUT" 2>/dev/null | cut -f1)" "$(find "$OUT" -type f 2>/dev/null | wc -l)"
big=$(find "$OUT" -type f -size +1M 2>/dev/null)
[ -z "$big" ] && pass "no >1MiB file in out" || { printf '%s\n' "$big" | sed 's/^/      /'; warn "large file(s) in out"; }
avail=$(df -Pk /fast 2>/dev/null | awk 'NR==2{print int($4/1048576)}')
if [ "${avail:-0}" -lt 20 ]; then fail "/fast headroom ${avail}G < 20G"; else pass "/fast headroom ${avail}G"; fi

# 9. Evidence hygiene in seat outputs: no /tmp citations, no credential markers.
#    This script is excluded: it necessarily contains the marker regexes it hunts.
#    Markers require a VALUE, so prose that merely names a field (a report quoting
#    `server.token` as a finding) is not a leak. /tmp citations in receipts FAIL the
#    evidence rule; in .md prose they are quoted findings and are only reported.
head_ "9. out-dir evidence hygiene"
tmp_all=$(grep -rl --exclude="$(basename "$0")" '/tmp/' "$OUT" 2>/dev/null || true)
tmp_rec=$(printf '%s\n' "$tmp_all" | grep -v '\.md$' || true)
if [ -n "$tmp_rec" ]; then
  printf '%s\n' "$tmp_rec" | sed 's/^/      /'
  warn "receipt cites /tmp (never evidence)"
elif [ -n "$tmp_all" ]; then
  printf '%s\n' "$tmp_all" | sed 's/^/      (prose) /'
  pass "no /tmp/ citation in receipts (only .md prose quoting the F7 finding)"
else
  pass "no /tmp/ citation in out"
fi
creds=$(grep -rlE --exclude="$(basename "$0")" \
  'server\.token[[:space:]]*["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_.+/=-]{12,}|ghp_[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY=[A-Za-z0-9_-]{12,}|BEGIN [A-Z ]+PRIVATE KEY' \
  "$OUT" 2>/dev/null || true)
[ -z "$creds" ] && pass "no credential marker in out" || { printf '%s\n' "$creds" | sed 's/^/      /'; fail "credential marker found in out (names only, above)"; }

# 10. Dirs at the wave root that the dispatch does not sanction. Round 50 assigns
#     `.ufo/waves/round-50/X1Assimilation/` to that seat, so it is legal; anything else
#     here is a seat writing outside `w1/out/` (empty or not).
head_ "10. wave-root strays"
wr=$(find "$LANE/.ufo/waves/round-50" -mindepth 1 -maxdepth 1 -type d \
       ! -name w1 ! -name c1 ! -name c2 ! -name census ! -name controls \
       ! -name freeze ! -name measured ! -name X1Assimilation 2>/dev/null || true)
if [ -z "$wr" ]; then
  pass "only dispatch-sanctioned dirs at the wave root"
else
  printf '%s\n' "$wr" | while read -r d; do
    printf '      %s (%s entries)\n' "$d" "$(find "$d" -mindepth 1 2>/dev/null | wc -l)"
  done
  warn "dir at the wave root not named by w1/dispatch.json (seat output outside w1/out/)"
fi

printf '\n== summary ==\n'
if [ "$fails" -eq 0 ]; then
  printf 'RESULT met=True fails=0\n'
  exit 0
fi
printf 'RESULT met=False fails=%s\n' "$fails"
exit 1
