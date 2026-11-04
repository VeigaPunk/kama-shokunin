import hashlib,json,pathlib,subprocess
R='/home/vgpnk/Projects/shokunin/kama-shokunin'
F='7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd'
C='.ufo/waves/round-85/count.py'
commands=[['git','-C',R,'rev-parse',F+'^{commit}'],['git','-C',R,'ls-tree',F,'--',C],['git','-C',R,'hash-object',C],['git','-C',R,'show',F+':'+C],['git','-C',R,'show',F+':plans/round-85-claims.md'],['git','-C',R,'show',F+':.ufo/waves/round-84/measured/after/c2-red.out'],['git','-C',R,'show',F+':.ufo/waves/round-84/measured/before/red-selfrecord.out'],['git','-C',R,'show',F+':.ufo/waves/round-84/measured/after/gate-final-green.out'],['git','-C',R,'show',F+':corpus/lessons/round-84-verifier-spotcheck.md']]
results=[]
for a in commands:
 p=subprocess.run(a,capture_output=True,text=True)
 results.append({'argv':a,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
record={'freeze':F,'counter_sha256':hashlib.sha256(pathlib.Path(R+'/'+C).read_bytes()).hexdigest(),'commands':results}
pathlib.Path('/fast/scratch/hyaku/kama-r85/SN01Scope/receipts/provenance.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'freeze':F,'counter_sha256':record['counter_sha256'],'commands':[{'argv':x['argv'],'exit':x['exit']} for x in results]},indent=2))
