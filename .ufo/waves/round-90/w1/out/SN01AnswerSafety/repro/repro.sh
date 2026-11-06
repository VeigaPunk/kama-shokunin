#!/usr/bin/env bash
# SN01 (round 90) answer-boundary reproducers. Read-only against the lane.
# usage: PROBE=/path/to/kama-probe.sh-at-M SCRATCH=/fast/scratch/... ./repro.sh [case...]
# Every case starts a lane-owned stub on a free loopback port and kills it.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
SCRATCH=${SCRATCH:-/fast/scratch/hyaku/kama-r90/SN01AnswerSafety-repro}
LANE=${LANE:-/home/vgpnk/Projects/shokunin/kama-shokunin}
M_REV=f968fb19bb2a0c2afe271bfe606f11b52d10823f
M_SHA=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97
mkdir -p -- "$SCRATCH"
cp -- "$HERE/stub.py" "$HERE/run_case.py" "$SCRATCH/"
export SN01_SCRATCH="$SCRATCH"
export SN01_PROBE="$SCRATCH/probe-M.sh"
if [ -n "${PROBE:-}" ]; then cp -- "$PROBE" "$SN01_PROBE"
else git -C "$LANE" cat-file -p "$M_REV:tools/kama-probe.sh" > "$SN01_PROBE"; fi
got=$(sha256sum "$SN01_PROBE" | cut -d' ' -f1)
[ "$got" = "$M_SHA" ] || { echo "probe sha256 $got != measured M $M_SHA" >&2; exit 1; }
# PATH without python3, for the grep-fallback finding (F2)
mkdir -p -- "$SCRATCH/bin"
for b in bash curl ss tr sed grep head wc mktemp date flock sort mv rm cat timeout dirname env; do
  ln -sf "/usr/bin/$b" "$SCRATCH/bin/$b"
done

run() { python3 "$SCRATCH/run_case.py" "$@"; }

case "${1:-all}" in
  hdr)      run f3_hdr30 hdrflood_slow 30 8; run f3_hdr40 hdrflood_slow 40 8; run f3_info1xx info1xx 500 8; run f3_trailers trailers 500 8 ;;
  body)     run f4_bigbody bigbody; run f4_cl_just_over cl_just_over; run f4_chunked_big chunked_big; run f4_close_big close_big; run f4_cl_short cl_short; run f4_http09 http09; run f4_te_gzip te_gzip; run f4_ce_gzip ce_gzip ;;
  props)    run f4_router_unloaded router_unloaded; run f4_router_autoload_ok router_autoload_ok ;;
  ids)      run f1_ids5k huge_ids 5000; run f1_ids20k huge_ids 20000; run f1_ids50k huge_ids 50000; run f1_ids200k huge_ids 200000 --maxwall 600 --rss ;;
  router)   run f1_ids20k_router huge_ids 20000 --expect m0000000 ;;
  snap)     run f5_snap_inject inject_id --sub snapshot --snapfix --json ;;
  nopy)     run f2_nopy_inject inject_raw --path "$SCRATCH/bin" ;;
  slow)     run f6_mixed_slow mixed_slow; run f6_health_slow health_slow ;;
  all)      "$0" hdr; "$0" body; "$0" props; "$0" snap; "$0" nopy; "$0" slow; "$0" ids ;;
  *) echo "unknown case group: $1" >&2; exit 2 ;;
esac
