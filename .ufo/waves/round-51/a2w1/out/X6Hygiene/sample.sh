#!/bin/bash
# X6Hygiene late sample: the four assigned checks + supplementary sweeps.
O=/fast/scratch/hyaku/kama-r51/X6Hygiene/late-sample.txt
{
date -Is
echo "### 1. pgrep -af llama-server"
pgrep -af llama-server; echo "exit=$?"
echo "### 1b. loopback listeners owned by llama-server"
ss -ltnp 2>/dev/null | grep -i llama-server; echo "exit=$?"
echo "### 1c. any kama replay/audit process still running"
pgrep -af 'kama-live-replay|kama-llamacpp-live|round51-replay-exe-audit|round51-append-audit-v6-check|append-only-audit.py' | grep -v 'pgrep -af'; echo "exit=$?"
echo "### 1d. build/control receipt ports (expect none listening)"
ss -ltn 2>/dev/null | grep -E ':(42881|38973|36071|40177|35825|39165)[[:space:]]'; echo "exit=$?"
echo "### 2. du of /fast/scratch/hyaku/kama-r51 (top 10 by size, MiB)"
du -s --block-size=1M /fast/scratch/hyaku/kama-r51/* 2>/dev/null | sort -rn | head -10
echo "total: $(du -sh /fast/scratch/hyaku/kama-r51 2>/dev/null | cut -f1)"
echo "seat dirs: $(ls -1 /fast/scratch/hyaku/kama-r51 | wc -l)"
echo "### 2b. seat scratch dirs still holding a git clone"
for d in /fast/scratch/hyaku/kama-r51/*/; do [ -d "$d/lane" ] && echo "  ${d}"; done
echo "### 3. git -C /home/vgpnk/Projects/shokunin status --porcelain"
git -C /home/vgpnk/Projects/shokunin status --porcelain; echo "exit=$?"
echo "### 4. git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain"
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain; echo "exit=$?"
echo "### 4b. lane diffstat of the working tree (unchanged-vs-HEAD summary)"
git -C /home/vgpnk/Projects/shokunin/kama-shokunin --no-optional-locks diff --stat; echo "exit=$?"
echo "### 4c. report count"
python3 /fast/scratch/hyaku/kama-r51/X6Hygiene/count_reports.py; echo "exit=$?"
} 2>&1 | tee "$O"
