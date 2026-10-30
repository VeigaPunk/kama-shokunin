#!/bin/bash
# Host-noise injector: repeatedly starts a root-owned process whose
# /proc/<pid>/fd table is unreadable to the counter's uid, and that starts
# AFTER the counter's tool process (which is what the counter grades as
# `unreadable_own`). We start them; we kill exactly the ones we started.
#
# usage: noise.sh start|stop
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
DIR=$S/noise
case "$1" in
  start)
    mkdir -p "$DIR"; : > "$DIR/pids"
    cat > "$DIR/loop.sh" <<'EOF'
#!/bin/bash
while true; do
  sudo -n sleep 45 >/dev/null 2>&1 &
  echo $! >> "$DIR/pids"
  sleep 0.2
done
EOF
    chmod +x "$DIR/loop.sh"
    nohup "$DIR/loop.sh" >/dev/null 2>&1 &
    echo $! > "$DIR/loop.pid"
    sleep 1.5
    echo "noise started (loop pid $(cat "$DIR/loop.pid")), spawned so far: $(wc -l < "$DIR/pids")"
    ;;
  stop)
    [ -f "$DIR/loop.pid" ] && kill -9 "$(cat "$DIR/loop.pid")" 2>/dev/null
    if [ -f "$DIR/pids" ]; then
      while read -r p; do
        [ -n "$p" ] && sudo -n kill -9 "$p" 2>/dev/null
      done < "$DIR/pids"
      rm -f "$DIR/pids"
    fi
    echo "noise stopped"
    ;;
esac
exit 0
