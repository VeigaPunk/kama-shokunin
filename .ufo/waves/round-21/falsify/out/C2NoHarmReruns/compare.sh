#!/usr/bin/env bash
# compare.sh RERUN_DIR [CLONE_PREFIX]
# Compares a fresh-clone rerun (run.py output dir with commands.json + raw streams)
# against the recorded official measurement runs/b76727f3 for every nh-*/fr-* item.
# Reports: exit match, stdout/stderr sha256 match (raw), raw byte equality (cmp),
# and path-normalized stdout/stderr sha256 match (CLONE_PREFIX -> live lane path).
set -u
REC=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/runs/b76727f3
LIVE=/home/vgpnk/Projects/shokunin/kama-shokunin
RERUN=${1:?usage: compare.sh RERUN_DIR [CLONE_PREFIX]}
CLONE=${2:-/tmp/kama-r21-C2NoHarmReruns/lane}
mismatch=0
for n in $(jq -r '.commands[] | select(.name|test("^(nh-|fr-)")) | .name' "$REC/commands.json"); do
  q() { jq -r --arg n "$n" ".commands[] | select(.name==\$n) | $1" "$2"; }
  cex=$(q .exit "$REC/commands.json");  rex=$(q .exit "$RERUN/commands.json")
  cout=$(q .stdout_sha256 "$REC/commands.json"); rout=$(q .stdout_sha256 "$RERUN/commands.json")
  cerr=$(q .stderr_sha256 "$REC/commands.json"); rerr=$(q .stderr_sha256 "$RERUN/commands.json")
  cargv=$(q '.argv|join(" ")' "$REC/commands.json")
  rargv=$(q '.argv|join(" ")' "$RERUN/commands.json")
  rargv_norm=${rargv//$CLONE/$LIVE}
  argv_ok=$([ "$cargv" = "$rargv_norm" ] && echo yes || echo NO)
  rawout=$(cmp -s "$RERUN/$n.stdout" "$REC/$n.stdout" && echo same || echo DIFF)
  rawerr=$(cmp -s "$RERUN/$n.stderr" "$REC/$n.stderr" && echo same || echo DIFF)
  normout=$(sed "s|$CLONE|$LIVE|g" "$RERUN/$n.stdout" | sha256sum | cut -c1-64)
  normerr=$(sed "s|$CLONE|$LIVE|g" "$RERUN/$n.stderr" | sha256sum | cut -c1-64)
  st=MATCH
  [ "$cex" = "$rex" ] && [ "$cout" = "$rout" ] && [ "$cerr" = "$rerr" ] || st=MISMATCH
  [ "$st" = MISMATCH ] && mismatch=$((mismatch+1))
  printf '%-30s %-8s exit rec=%s rerun=%s | stdout rec=%s rerun=%s raw=%s norm=%s | stderr raw=%s norm=%s | argv-match-after-path-norm=%s\n' \
    "$n" "$st" "$cex" "$rex" "${cout:0:12}" "${rout:0:12}" "$rawout" \
    "$([ "$normout" = "$cout" ] && echo MATCH || echo NO)" "$rawerr" \
    "$([ "$normerr" = "$cerr" ] && echo MATCH || echo NO)" "$argv_ok"
done
echo "raw-mismatching items: $mismatch"
