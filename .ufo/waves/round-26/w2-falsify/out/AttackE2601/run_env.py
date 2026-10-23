import json, os, sys
sys.argv=[sys.argv[0]]
src=open('run_e2601.py').read().split('TRIGGER = [')[0]
exec(src)
out=[]
os.environ['LLAMA_ARG_ENDPOINT_SLOTS']='0'
out.append(run('env-slots0', 47700, ['-t','2'], [("GET","/slots",{},""),("GET","/props",{},None)]))
out.append(run('env-slots0-plus-flag', 47701, ['--slots','-t','2'], [("GET","/slots",{},"")]))
del os.environ['LLAMA_ARG_ENDPOINT_SLOTS']
out.append(run('noslots-props', 47702, ['--no-slots','-t','2'], [("GET","/props",{},None)]))
(OUT/'results-env.json').write_text(json.dumps(out,indent=1)+"\n")
for r in out:
    print(r['label'],'ready',r['ready'],'port_closed',r['port_closed'])
    for q in r['requests']:
        t=q['resp']; i=t.find('endpoint_slots')
        print('  ',q['method'],q['path'],'->',q['status'], t[:160] if i<0 else t[max(0,i-2):i+25])
