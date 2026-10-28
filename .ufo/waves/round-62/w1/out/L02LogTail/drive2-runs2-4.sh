#!/bin/bash
# L02LogTail runs 2-4: (2) poisoned-env negative control, (3) same-work-dir truncation,
# (4) unwritable work dir (log-capture failure semantics).
set -u
S=/fast/scratch/hyaku/kama-r62/w/L02LogTail
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
TOOL=$LANE/tools/kama-completion-live.py
export TMPDIR=$S/tmp TMP=$S/tmp TEMP=$S/tmp

observe_release () {  # $1 = hold dir
  local hold=$1
  for i in $(seq 1 2400); do
    if [ -f "$hold/hold.json" ]; then
      cp "$hold/hold.json" "$hold/../hold-snapshot.json"
      printf 'release\n' > "$hold/release"
      return 0
    fi
    sleep 0.05
  done
  return 1
}

# ---------- run2: poisoned environment ----------
R=$S/run2
mkdir -p "$R/work" "$R/hold"
rm -f "$R/hold/release" "$R/hold/hold.json"
(
  OPENAI_API_KEY='sk-SENTINEL-openai-0123456789abcdef' \
  ANTHROPIC_API_KEY='sk-ant-SENTINEL-0123456789abcdef' \
  AWS_SECRET_ACCESS_KEY='SENTINEL-aws-secret-value' \
  HF_TOKEN='hf_SENTINELhubtoken0123456789' \
  GITHUB_TOKEN='ghp_SENTINELgithubtoken0123456789' \
  KAMA_TOKEN='SENTINEL-kama-token' \
  LLAMA_ARG_API_KEY='SENTINEL-llama-api-key' \
  LLAMA_ARG_LOG_VERBOSITY=5 \
  LLAMA_ARG_HOST=0.0.0.0 \
  LLAMA_ARG_PORT=1 \
  python3 "$TOOL" --work "$R/work" --hold-dir "$R/hold" --hold-timeout 120 \
    --nonce "l02-logtail-run2-$(date -u +%Y%m%dT%H%M%SZ)" \
    --out "$R/receipt.json" > "$R/tool.stdout" 2> "$R/tool.stderr"
) &
TOOLPID=$!
observe_release "$R/hold"; OBS2=$?
wait $TOOLPID; RC2=$?
echo "run2 rc=$RC2 observer=$OBS2"

# ---------- run3: two runs into the SAME work dir ----------
R=$S/run3
mkdir -p "$R/work" "$R/hold"
rm -f "$R/hold/release" "$R/hold/hold.json"
(
  python3 "$TOOL" --work "$R/work" --hold-dir "$R/hold" --hold-timeout 120 \
    --nonce "l02-logtail-run3a-$(date -u +%Y%m%dT%H%M%SZ)" \
    --out "$R/receipt-a.json" > "$R/tool-a.stdout" 2> "$R/tool-a.stderr"
) &
TOOLPID=$!
observe_release "$R/hold"; wait $TOOLPID; RC3A=$?
cp "$R/work/server.log" "$R/server.log.run-a"
rm -f "$R/hold/release" "$R/hold/hold.json"
(
  python3 "$TOOL" --work "$R/work" --hold-dir "$R/hold" --hold-timeout 120 \
    --nonce "l02-logtail-run3b-$(date -u +%Y%m%dT%H%M%SZ)" \
    --out "$R/receipt-b.json" > "$R/tool-b.stdout" 2> "$R/tool-b.stderr"
) &
TOOLPID=$!
observe_release "$R/hold"; wait $TOOLPID; RC3B=$?
cp "$R/work/server.log" "$R/server.log.run-b"
echo "run3 rc_a=$RC3A rc_b=$RC3B"

# ---------- run4: unwritable work dir ----------
R=$S/run4
mkdir -p "$R/work-ro"
chmod 0555 "$R/work-ro"
python3 "$TOOL" --work "$R/work-ro" --nonce "l02-logtail-run4-nohold" \
  --out "$R/receipt.json" > "$R/tool.stdout" 2> "$R/tool.stderr"
RC4=$?
chmod 0755 "$R/work-ro"
echo "run4 rc=$RC4"
