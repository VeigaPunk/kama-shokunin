#!/bin/sh
# ScribeLog (round 24) — re-observation of every count cited in the draft
# LOG entry. Read-only. Run from the scratch clone
# /fast/scratch/hyaku/kama-r24/ScribeLog (lane tip d1b9d956a0beda9ac32a1a2cf6ced875faeada0d).
# Usage: sh collect-evidence.sh > evidence.txt
set -u
LANE=/fast/scratch/hyaku/kama-r24/ScribeLog
FLEET=/home/vgpnk/Projects/shokunin
SESSION="$FLEET/../.omp/agent/sessions/-Projects-shokunin/2026-10-21T16-10-39-768Z_01a15f3a-9f17-7238-ae23-4fe77ffa6530/KamaR23-2.jsonl"

echo "# lane tip and preregistered base"
git -C "$LANE" rev-parse HEAD
git -C "$LANE" log --oneline -2
git -C "$LANE" cat-file -t 0df800e896f6bce285a81e794ad4ae1d1e6c3a71
git -C "$LANE" merge-base --is-ancestor 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 HEAD && echo "prereg base is an ancestor of lane tip: yes"
git -C "$LANE" --version
python3 -V

echo
echo "# round-23 falsify-wave advice reports (the 69-vs-68 correction)"
ls "$LANE"/.ufo/waves/round-23/falsify/advice/*.md | wc -l
ls "$LANE"/.ufo/waves/round-23/falsify/advice/ | wc -l
ls "$LANE"/.ufo/waves/round-23/build/advice/*.md | wc -l
ls "$LANE"/.ufo/waves/round-23/falsify/advice/ | grep -c 'swarm-registry.json'
echo "-- the report that was written before its final response aborted"
stat -c '%n %s bytes mtime=%y' "$LANE"/.ufo/waves/round-23/falsify/advice/RowC03FabricatedFull.md
echo "-- lesson line that carries the wrong count"
sed -n '178,180p' "$LANE"/corpus/lessons/round-23.md

echo
echo "# closure row 428 (MANIFEST.json rounds[428])"
python3 - <<'PY'
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/MANIFEST.json'))
e=d['rounds'][428]
for k in ('round','lane','lane_round','type','admitted','verdict','verdicts','trends','report','commit','closed_at','rejection_streak_impact'):
    print(k,'=',e.get(k))
print('report_commit_in_fleet:')
PY
git -C "$FLEET" log --oneline -1 -- .ufo/reports/round-23/kama.md

echo
echo "# r23 cleanup identity evidence: 40 retained rows of 56 counted processes"
python3 - <<'PY'
import json,re
p='/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-21T16-10-39-768Z_01a15f3a-9f17-7238-ae23-4fe77ffa6530/KamaR23-2.jsonl'
lines=open(p).readlines()
for idx in (154,155,157,158):
    d=json.loads(lines[idx])
    ts=d.get('timestamp')
    if 'data' in d and isinstance(d.get('data'),dict):
        print(idx,ts,'CMD',json.dumps(d['data'].get('args',{}).get('command','')))
        continue
    for it in d['message'].get('content',[]):
        if it.get('type')=='text':
            t=it['text']
            rows=t.strip().split('\n')
            ident=[r for r in rows if re.match(r'^\s*\d+\s',r)]
            tail=rows[-1]
            print(idx,ts,'identity_rows=%d'%len(ident),'last_row=%r'%tail[:40])
            if idx==158:
                print(idx,ts,'first_line=%r'%rows[0])
PY

echo
echo "# round-24 lane files touched by this seat (draft only)"
echo "no production file edited by ScribeLog"
