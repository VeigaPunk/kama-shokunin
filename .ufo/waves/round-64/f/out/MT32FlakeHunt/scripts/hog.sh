#!/bin/bash
# CPU hog: 4 busy loops `python3 -c 'while 1: pass'`. start|stop
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT32FlakeHunt
PIDF=$S/hog.pids
case "$1" in
  start)
    : > "$PIDF"
    for i in 1 2 3 4; do
      nohup python3 -c 'while 1: pass' > /dev/null 2>&1 &
      echo $! >> "$PIDF"
    done
    echo "hogs started: $(cat "$PIDF" | tr '\n' ' ')"
    ;;
  stop)
    if [ -f "$PIDF" ]; then
      while read -r p; do
        [ -n "$p" ] && kill -9 "$p" 2>/dev/null && echo "killed $p"
      done < "$PIDF"
      rm -f "$PIDF"
    fi
    ;;
  status)
    if [ -f "$PIDF" ]; then
      while read -r p; do
        [ -n "$p" ] && ps -o pid=,stat=,etime=,cmd= -p "$p" 2>/dev/null
      done < "$PIDF"
    else
      echo "no hogs"
    fi
    ;;
esac
exit 0
