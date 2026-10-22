#!/bin/bash
# Bounded, read-only verification of corpus/lessons/round-24.md claims.
# Repo under test: /fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo @ 2e254a1
set -u
R=/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo
W=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24
cd "$R" || exit 9
fail=0
chk(){ # chk <label> <expect: OK|FAIL> <cmd...>
  local label="$1" expect="$2"; shift 2
  out=$("$@" 2>&1); rc=$?
  if [ "$expect" = OK ] && [ $rc -ne 0 ]; then echo "UNEXPECTED-RC $label rc=$rc"; fail=1; fi
  if [ "$expect" = FAIL ] && [ $rc -eq 0 ]; then echo "UNEXPECTED-OK $label"; fail=1; fi
  echo "[$label] rc=$rc"; printf '%s\n' "$out" | head -6
}
echo "== HEAD =="; git rev-parse HEAD
echo
echo "== V1 frozen44 == shipped manifest: byte-identical shared cases, +3 supplement rows =="
python3 - <<'PY'
import json
s=json.load(open('/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo/.ufo/waves/round-24/oracle-snapshot-before-inspection.json'))
m=json.load(open('/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo/tests/report-audit/promisor-grid-expectations.json'))
sc={c['case']:json.dumps(c,separators=(',',':')) for c in s['cases']}
mc={c['case']:json.dumps(c,separators=(',',':')) for c in m['cases']}
extra=sorted(set(mc)-set(sc))
print('shared',len(sc),'identical',sum(1 for k in sc if mc.get(k)==sc[k]),'extra',extra)
sup=json.load(open('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/oracle-supplement-2.json'))
print('supplement rows==manifest extras:', sup['rows']==extra)
print('manifest sha', __import__('hashlib').sha256(open('/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo/tests/report-audit/promisor-grid-expectations.json','rb').read()).hexdigest())
PY
echo "== V2 lesson used-by reconciliation table vs actual base->head SOURCES diff =="
python3 - <<'PY'
import subprocess,re
def rows(rev):
    t=subprocess.run(['git','show',rev+':corpus/SOURCES.md'],capture_output=True,text=True,cwd='/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo').stdout
    return {m.group(1):[c.strip() for c in l.strip().strip('|').split('|')]
            for l in t.splitlines() if (m:=re.match(r'^\|\s*(S\d{3})\s*\|',l))}
b=rows('0df800e896f6bce285a81e794ad4ae1d1e6c3a71'); h=rows('HEAD'); c=rows('ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05')
tbl={'S083':(b,'corpus/lessons/round-22.md'),'S089':(b,'corpus/lessons/round-23.md, tools/report-landing-audit.py'),
 'S094':(b,'corpus/lessons/round-23.md'),'S095':(b,'corpus/lessons/round-23.md, tools/report-landing-audit.py'),
 'S096':(b,'corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md'),'S099':(b,'corpus/lessons/round-23.md'),
 'S100':(b,'corpus/lessons/round-23.md, tools/report-landing-audit.py, tests/report-audit/repo-state-grid.py'),
 'S101':(b,'corpus/lessons/round-23.md, tools/report-landing-audit.py'),
 'S102':(c,'corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md'),
 'S103':(c,'corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md'),
 'S104':(c,'corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md')}
ok=True
for sid,(src,old) in tbl.items():
    if src[sid][10]!=old: print('OLD MISMATCH',sid,src[sid][10]); ok=False
print('all 11 old used-by values match:',ok)
print('changed field indices base->head S001..S104:',sorted({i for s in [f'S{n:03d}' for n in range(1,105)] if s in b and s in h for i,(x,y) in enumerate(zip(b[s],h[s])) if x!=y}))
print('rows at HEAD:',len(h),'S105 present:','S105' in h)
PY
echo "== V3 S095 teaches immutable at HEAD; S105 records the rejection =="
python3 - <<'PY'
import subprocess,re
def row(rev,sid):
    t=subprocess.run(['git','show',rev+':corpus/SOURCES.md'],capture_output=True,text=True,cwd='/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo').stdout
    for l in t.splitlines():
        if l.startswith('| '+sid+' '): return [c.strip() for c in l.strip().strip('|').split('|')]
b=row('0df800e896f6bce285a81e794ad4ae1d1e6c3a71','S095'); h=row('HEAD','S095'); s=row('HEAD','S105')
print('S095 teaches unchanged:',b[7]==h[7]); print('S095 status base/head:',b[8],h[8])
print('S105 status:',s[8]); print('S105 teaches:',s[7][:120])
PY
echo "== V4 chronology: candidate-informed material in the CritUnknown advice (the supplement's authority) =="
ls -la --time-style=+%H:%M:%S "$W/build/advice/CritUnknown.md" "$W/build/out/CritUnknown/candidate.patch" "$W/build/out/CritUnknown/witness-output.txt" "$W/build/out/CritUnknown/hidden_probe.py" "$W/build/out/CritUnknown/hidden-output.txt" "$W/build/out/CaseMissingFleetTree/audit-candidate-wip.json" | awk '{print $6, $7}'
grep -n "candidate (ruling v3)\|In the candidate, metadata\|Candidate updated\|contradiction CritScores found" "$W/build/advice/CritUnknown.md"
git log --format='%h ad=%ad cd=%cd %s' --date=iso -8
echo "== V5 pre-candidate statements of the other two reviewers =="
grep -n "no auditor diff\|none existed" "$W/build/advice/CritScores.md" "$W/build/advice/CritNoTrade.md"
echo "== V6 S105 pinned snapshot: negative counts and quote contiguity =="
python3 - <<'PY'
import re,hashlib
p='/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/sources/python-bytes-decode-reader.txt'
t=open(p,encoding='utf-8',errors='replace').read()
print('sha',hashlib.sha256(open(p,'rb').read()).hexdigest())
for w in ['subprocess','TextIOWrapper','text mode']:
    print(w, len(re.findall(re.escape(w),t,re.I)))
q="If 'strict' (the default), a UnicodeError exception is raised."
print('plain quote occurrences in pinned snapshot:',t.count(q))
print('rendered occurrences:',t.count("If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError"))
PY
echo "== V7 shipped runner: strong names_any_of grader (no path relaxation) + PG46 fixture =="
grep -c "names_unavailable" tests/report-audit/promisor-grid.py
grep -n "cited_hidden_blob=True" tests/report-audit/promisor-grid.py
grep -n "if not any(n and n in err for n in names)" tests/report-audit/promisor-grid.py
echo "== V8 PM02 kill evidence: which runner/grid/pristine state =="
python3 - <<'PY'
import json,hashlib
d=json.load(open('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/MutationOracle/sensitivity-promisor-grid.json'))
print('baseline_mode',d['baseline_mode'],'pristine',d['pristine'])
print('pristine_unmet_cells',d['pristine_unmet_cells'])
print('grid used',d['grid'],hashlib.sha256(open(d['grid'],'rb').read()).hexdigest())
print('shipped grid sha',hashlib.sha256(open('/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo/tests/report-audit/promisor-grid.py','rb').read()).hexdigest())
print('PM02 killed:', 'PM02-blanket-unknown-refusal' in d['killed_ids'])
PY
grep -n "baseline" tests/report-audit/promisor-mutants.py | head -3
grep -n "does not meet the grid" -A 2 tests/report-audit/promisor-mutants.py | head -6
echo "== V9 upstream doc quotes (public HTTPS) =="
python3 - <<'PY'
import re
t=open('/fast/scratch/hyaku/kama-r24/falsify/DocLesson/tmp/git-rev-list.html',encoding='utf-8',errors='replace').read()
p=open('/fast/scratch/hyaku/kama-r24/falsify/DocLesson/tmp/partial-clone.html',encoding='utf-8',errors='replace').read()
h2=[(m.start(),m.group(1)) for m in re.finditer(r'<h2[^>]*id="([^"]+)"',t if False else p)]
def sect(pp,pos):
    cur=None
    for s,i in h2:
        if s<=pos: cur=i
        else: break
    return cur
i=p.find('These promisor packfiles consist of')
print('S103 section:',sect(p,i),'| raw contiguous:',p.count('These promisor packfiles consist of a "&lt;name&gt;.promisor" file with'))
j=t.find('like allow-any, but will also print a list of the missing objects')
print('S102 sentence present:',j>0)
print('S102 "last updated in 2.56.0":', 'last updated in 2.56.0' in t, '| S103 page same:', 'last updated in 2.56.0' in p)
PY
echo "== V10 upstream fsck.c == retained copy =="
sha256sum /fast/scratch/hyaku/kama-r24/falsify/DocLesson/tmp/fsck-upstream.c "$W/build/out/SrcFsck/fsck-builtin.c"
sed -n '143p;149p' "$W/build/out/SrcFsck/fsck-builtin.c"
echo "OVERALL fail=$fail"
