#!/bin/bash
# $1=repo $2=tip $3=scratch $4=out $5=rcfile
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py \
  --repo "$1" --tip "$2" --scratch "$3" --out "$4" > "$4.stdout" 2>&1
echo $? > "$5"
