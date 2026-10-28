import importlib.util, json, os, copy
root=os.path.dirname(__file__)
spec=importlib.util.spec_from_file_location('counter',os.path.join(root,'round62-c1-counter.py'))
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.NONCE='r62-probe'
receipt,witness,nonce=c.witness_run(os.path.join(root,'run'),os.path.join(root,'tools','kama-completion-live.py'))
c.NONCE=nonce
base=c.score(receipt,witness)
results={'nonce':nonce,'base':base,'witness':witness,'receipt_verdict':receipt.get('verdict'),'receipt_child_pid':receipt.get('child_pid'),'receipt_port':receipt.get('port'),'receipt_server_sha256':(receipt.get('server') or {}).get('sha256'),'receipt_model_sha256':(receipt.get('model') or {}).get('sha256')}
for field,value in [('server_sha256','0'*64),('model_sha256','0'*64),('pid',-1),('text','text from different model')]:
 x=copy.deepcopy(witness); x[field]=value
 results[field]={'forged_value':value,'score':c.score(receipt,x)}
open(os.path.join(root,'probe-results.json'),'w').write(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
