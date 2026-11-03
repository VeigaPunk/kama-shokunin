"""Owned explicit oracle construction. Does not import or execute candidate."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent;out=root/'freeze';out.mkdir(exist_ok=True)
def J(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def ev(x):return 'data: '+(J(x) if not isinstance(x,str) else x)+'\n\n'
N=ev({'choices':[{'index':0,'finish_reason':None}]});F=ev({'choices':[{'index':0,'finish_reason':'stop'}]});D=ev('[DONE]');U=ev({'choices':[]});E=ev({'error':{'message':'synthetic error'}});GOOD=N+F+D
cases=[]
def add(name,body,status='COMPLETE',raw=None):
 if raw is None:raw=J({'schema':'kama-chat-stream/v1','synthetic':True,'body':body}).encode()
 if isinstance(raw,str):raw=raw.encode()
 reasons={'COMPLETE':('complete_sequence',0),'INCOMPLETE':('incomplete_sequence',2),'STREAM_ERROR':('error_event',2),'INVALID_OR_INSUFFICIENT':('invalid_input',3)}
 reason,code=reasons[status];expected=dict(schema='kama-offline-chat-stream/v1',status=status,reason=reason,readiness='not_established',weight_identity='not_established',runtime_ownership='not_established',live_observation=False)
 path=name+'.json';(out/path).write_bytes(raw);cases.append(dict(name=name,input=path,input_bytes=len(raw),input_sha256=hashlib.sha256(raw).hexdigest(),expected=expected,exit=code))
def bad(name,body):add(name,body,'INVALID_OR_INSUFFICIENT')
def inc(name,body):add(name,body,'INCOMPLETE')
add('complete',GOOD);add('final-only-then-done',F+D);add('usage',N+F+U+D)
for reason in ('length','tool_calls'):add('finish-'+reason,N+ev({'choices':[{'index':0,'finish_reason':reason}]})+D)
add('crlf',GOOD.replace('\n','\r\n'));add('cr',GOOD.replace('\n','\r'));add('no-space',GOOD.replace('data: ','data:'));add('bom','\ufeff'+GOOD)
add('multiline-json','data: {"choices":\ndata: [{"index":0,\ndata: "finish_reason":"stop"}]}\n\n'+D)
add('comment-and-metadata',': [DONE]\nid: x\nretry: 10\nx-any:ignored\n\n'+GOOD+': final comment')
add('event-message','event: message\n'+F+D);add('event-reset','event: error\n\n'+F+D);add('event-last-wins','event: unknown\nevent: message\n'+F+D)
add('event-empty','event:\n'+F+D);add('metadata-tail',GOOD+'event: error\nid: 9\nretry: 3\nx: q');add('unicode-control-comment',GOOD+': \x00\u2028😀\n')
inc('empty','');inc('comment-only',': [DONE]\n\n');inc('null-only',N);inc('done-only',D);inc('missing-finish',N+D);inc('missing-done',N+F)
inc('eof-no-blank',N+F+'data: [DONE]\n');inc('eof-no-newline',N+F+'data: [DONE]');inc('pending-after-done',GOOD+'data: x');inc('empty-pending',GOOD+'data:\n');inc('pending-error',E+'data: tail')
inc('second-bom','\ufeff\ufeff'+F+D)
inc('case-data',F+'DATA: [DONE]\n\n');inc('comment-done',N+F+': data: [DONE]\n\n')
for name,body in [('error',E),('error-after-null',N+E),('error-done',E+D)]:add(name,body,'STREAM_ERROR')
for name,body in [('done-space',F+'data:  [DONE]\n\n'),('done-trailing-space',F+'data: [DONE] \n\n'),('done-tab',F+'data:\t[DONE]\n\n'),('done-json-string',F+ev('"[DONE]"')),('double-done',GOOD+D),('post-done-chunk',GOOD+N),('post-done-bad-json',GOOD+ev('{')),('duplicate-final',F+F+D),('chunk-after-final',F+N+D),('usage-before-final',U+F+D),('double-usage',F+U+U+D),('usage-only',U+D),('error-after-final',F+E+D),('chunk-after-error',E+N),('double-error',E+E),('usage-after-error',E+U),('error-after-done',GOOD+E),('invalid-after-error',E+ev('{')),('empty-data',F+'data\n\n'+D),('event-wrong','event: error\n'+F+D),('null-json',ev('null')+D),('nan',ev('{"choices":[{"index":0,"finish_reason":NaN}]}')+D),('duplicate-key',ev('{"choices":[],"choices":[{"index":0,"finish_reason":"stop"}]}')+D),('duplicate-escaped-key',ev('{"choices":[{"index":0,"\\u0069ndex":0,"finish_reason":"stop"}]}')+D),('boolean-index',ev({'choices':[{'index':False,'finish_reason':'stop'}]})+D),('float-index',ev({'choices':[{'index':0.0,'finish_reason':'stop'}]})+D),('unknown-finish',ev({'choices':[{'index':0,'finish_reason':'STOP'}]})+D),('extra-chunk-key',ev({'choices':[{'index':0,'finish_reason':'stop','delta':{}}]})+D),('empty-error',ev({'error':{'message':''}})),('surrogate-frame',ev('{"error":{"message":"\\ud800"}}')),('late-invalid-pending',GOOD+ev('{')+'data: tail')]:bad(name,body)
for name,obj in [('wrong-schema',{'schema':'other','synthetic':True,'body':GOOD}),('false-synthetic',{'schema':'kama-chat-stream/v1','synthetic':False,'body':GOOD}),('int-synthetic',{'schema':'kama-chat-stream/v1','synthetic':1,'body':GOOD}),('extra-root',{'schema':'kama-chat-stream/v1','synthetic':True,'body':GOOD,'extra':1}),('missing-body',{'schema':'kama-chat-stream/v1','synthetic':True}),('wrong-body',{'schema':'kama-chat-stream/v1','synthetic':True,'body':[]}),('wrong-root',[])]:add(name,None,'INVALID_OR_INSUFFICIENT',J(obj))
base=J({'schema':'kama-chat-stream/v1','synthetic':True,'body':GOOD}).encode()
add('outer-bom',None,'INVALID_OR_INSUFFICIENT',b'\xef\xbb\xbf'+base);add('outer-invalid-utf8',None,'INVALID_OR_INSUFFICIENT',base+b'\xff');add('outer-duplicate',None,'INVALID_OR_INSUFFICIENT',base[:-1]+b',"synthetic":true}')
add('outer-surrogate',None,'INVALID_OR_INSUFFICIENT','{"schema":"kama-chat-stream/v1","synthetic":true,"body":"\\ud800"}')
add('outer-nan',None,'INVALID_OR_INSUFFICIENT','{"schema":"kama-chat-stream/v1","synthetic":NaN,"body":""}')
add('outer-limit',None,raw=base+b' '*(65536-len(base)));add('outer-over',None,'INVALID_OR_INSUFFICIENT',base+b' '*(65537-len(base)))
body=GOOD+':'+('x'*(32768-len(GOOD.encode())-1));add('body-limit',body);bad('body-over',body+'x')
# Unicode byte ceiling differs from codepoint count.
body2=GOOD+':'+('é'*((32768-len(GOOD.encode())-1)//2));body2+='x'*(32768-len(body2.encode()));add('body-unicode-limit',body2);bad('body-unicode-over',body2+'é')
manifest=dict(schema='kama71-independent-freeze/v1',spec_sha256=hashlib.sha256((root/'SPEC.md').read_bytes()).hexdigest(),before_candidate_inspection=True,cases=cases,invocation_cases=[dict(name=x,exit=64,stdout='') for x in ('no-args','two-args','missing-file','directory','symlink')],mutants={
'eof-dispatch':{'target':'eof-no-blank','benign':'complete'},'trim-sentinel':{'target':'done-space','benign':'complete'},'case-fold-fields':{'target':'case-data','benign':'complete'},'done-only-complete':{'target':'done-only','benign':'complete'},'missing-finish-complete':{'target':'missing-finish','benign':'complete'},'ignore-error':{'target':'error-done','benign':'complete'},'early-done-return':{'target':'post-done-bad-json','benign':'complete'},'duplicate-key-permissive':{'target':'duplicate-key','benign':'complete'},'ignore-pending':{'target':'pending-after-done','benign':'complete'},'constant-refusal':{'target':'complete','benign':'empty-data'}},scope_mutants={'fields':['readiness','weight_identity','runtime_ownership','live_observation'],'statuses':['COMPLETE','INCOMPLETE','STREAM_ERROR','INVALID_OR_INSUFFICIENT'],'cases':['complete','missing-finish','error','empty-data']},baseline_comparison={'complete':True,'cr':False,'no-space':False,'multiline-json':False,'missing-finish':True,'eof-no-blank':True,'post-done-bad-json':True,'error-done':True})
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(len(cases),hashlib.sha256((out/'MANIFEST.json').read_bytes()).hexdigest())
