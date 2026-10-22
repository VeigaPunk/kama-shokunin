#!/usr/bin/env bash
# Re-creates source-lines.txt and log-observations.txt for the CriticLoadCells advice.
# Inputs: pinned raw sources fetched to $S at llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad,
# sibling ExecLoadReplicate scratch logs and receipt (read only).
S=/fast/scratch/hyaku/kama-r25a2/CriticLoadCells/src
L=/fast/scratch/hyaku/kama-r25a2/ExecLoadReplicate
R=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecLoadReplicate
q() { echo "== $1:$2"; sed -n "$2p" "$S/$1" | cut -c1-200; }
{
q tools_server_server-context.cpp 1724,1726
q tools_server_server-context.cpp 1766,1776
q tools_server_server-context.cpp 1810,1815
q tools_server_server-context.cpp 2026,2030
q tools_server_server-context.cpp 2851,2855
q tools_server_server-context.cpp 2883,2896
q tools_server_server-context.cpp 3374,3378
q tools_server_server-context.cpp 3676,3681
q tools_server_server-context.cpp 3777,3779
q tools_server_server-context.cpp 4294,4302
q tools_server_server-context.cpp 4315,4330
q tools_server_server-context.cpp 4334,4339
q tools_server_server-context.cpp 4655,4662
q tools_server_server-context.cpp 4957,4961
q tools_server_server-context.cpp 4973,4981
q tools_server_server-context.cpp 5005,5017
q tools_server_server-context.cpp 2170,2171
q tools_server_server-common.cpp 107,109
q tools_server_server-common.cpp 970,996
q tools_server_server-http.cpp 150,152
q tools_server_server.cpp 169,173
q common_common.h 458,459
q common_common.h 578,578
q common_common.h 636,642
q src_llama-context.cpp 1940,1954
q src_llama-kv-cache.cpp 1036,1062
} > source-lines.txt
{
echo "== lifetimes / context-shift / defer / exceeded counts per scratch log"
for f in $L/L*.log; do echo "$(basename $f) lifetimes=$(grep -c 'load_model: initializing' $f) ctxshift=$(grep -c 'context shift' $f) defer=$(grep -c 'defer task' $f) exceeded=$(grep -c 'Context size has been exceeded' $f)"; done
echo "== L1-rep1 launches, slot choice, release (both lifetimes)"
grep -n -E 'processing task, is_child|selected slot by|stop processing|load_model: initializing|common_fit_params: successfully|llama_context: n_ctx  ' $L/L1-rep1.log | cut -c1-160
echo "== L3-rep1 slot choice for second request"
grep -n -E 'selected slot by|stop processing' $L/L3-rep1.log | cut -c1-160
echo "== harness log open mode"
grep -n 'open(logpath' $R/load_replicate.py
echo "== receipt request fields (L1 first row)"
python3 -c "import json;d=json.load(open('$R/l-cells-receipt.json'));print(sorted(d['cells'][0]['requests'][0].keys()))"
} > log-observations.txt
