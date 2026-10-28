import glob,os,sys
OUT='/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-64/b/out'
standin={
 'sources-registry':('tools/sources-append-only.py','            checks.append((name, True))','            checks.append((name, False))'),
 'ollama-offline-evidence-replay':('tools/kama-ollama-evidence.py','    failed = len(records) - passed','    failed = len(records) - passed + 1'),
 'live-llamacpp-lifecycle':('tools/kama-llamacpp-live.py',"        return 'pass', 0","        return 'pass', 1"),
 'append-only-audit':('tools/append-only-audit.py','    fails = sum(1 for _, ok, _ in cases if not ok)','    fails = sum(1 for _, ok, _ in cases if not ok) + 1'),
 'live-receipt-replay':('tools/kama-live-replay.py','    fails = sum(1 for _, ok, _ in cases if not ok)','    fails = sum(1 for _, ok, _ in cases if not ok) + 1'),
 'live-ollama-lifecycle':('tools/kama-ollama-live.py',"    return finish('MODEL_OK', 0)","    return finish('MODEL_OK', 1)"),
}
rows={}; src={}
for p in sorted(glob.glob(OUT+'/X0*/capability-regress-r64.part*.tsv')):
    for ln in open(p).read().split('\n'):
        if not ln.strip(): continue
        c=ln.split('\t')
        if c[0]=='cap': continue
        rows[c[0]]=c; src[c[0]]=os.path.relpath(p,OUT)
for cap,(t,f,r) in standin.items():
    if cap not in rows:
        rows[cap]=[cap,t,f,r]; src[cap]='standin(X01)'
order=['sources-registry','ollama-offline-evidence-replay','live-llamacpp-lifecycle','gguf-declared-identity-replay','context-capacity-receipt','instrument-agreement','pin-watch','digest-ledger','hexrun-census','append-only-audit','live-receipt-replay','live-ollama-lifecycle']
miss=[c for c in order if c not in rows]; assert not miss, miss
with open(sys.argv[1],'w') as fh:
    fh.write('cap\ttool_path\tfind\treplace\n')
    for c in order: fh.write('\t'.join(rows[c])+'\n')
for c in order: print(c, src[c])
