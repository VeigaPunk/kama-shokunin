#!/bin/sh
# Host (no namespace) C1 run at round-53 build tip with TMPDIR in the seat scratch.
set -u
S=/fast/scratch/hyaku/kama-r53/Sen2Scratch
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py
TIP=c22602bd8d83ab26349d1087e916ca537ee4f9d1
SCR=$S/t-host
POLL=$S/c1-host-tmp-poll.txt
mkdir -p "$SCR"
: > "$POLL"
echo "host /tmp stat=$(stat -c '%A %a' /tmp) initial entries=$(find /tmp -mindepth 1 | wc -l)"
start=$(date +%s)
TMPDIR="$SCR" python3 "$CNT" --repo "$S/lane" --tip "$TIP" --scratch "$SCR" \
    --out "$S/c1-host.out" > "$S/c1-host.txt" 2>&1 &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  for pat in '/tmp/r53c1-*' '/tmp/r53c2-*' '/tmp/kama-probe.*' '/tmp/kama-llamacpp-live-*' \
             '/tmp/kama-live-*' '/tmp/kama-install-selftest-*'; do
    for p in $pat; do [ -e "$p" ] && echo "$p"; done
  done >> "$POLL"
  sleep 0.2
done
wait "$pid"; rc=$?
end=$(date +%s)
sort -u "$POLL" > "$S/c1-host-tmp-poll-uniq.txt"
echo "c1 host: exit=$rc wall=$((end-start))s"
echo "--- head ---"; sed -n '1,2p' "$S/c1-host.txt"
echo "--- tail ---"; tail -n 2 "$S/c1-host.txt"
echo "kama-pattern /tmp paths seen=$(wc -l < "$S/c1-host-tmp-poll-uniq.txt")"
sed -n '1,20p' "$S/c1-host-tmp-poll-uniq.txt"
echo "--- llama-server ---"; pgrep -af '(^|/)llama-server( |$)' || echo none
