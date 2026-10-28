import hashlib, importlib.util, json, traceback
p='/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz/round62-c1-counter.py'
s=importlib.util.spec_from_file_location('c1',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.NONCE='r62-fuzz'
def cap(body): return {'body':body,'body_sha256':hashlib.sha256(body.encode()).hexdigest()}
def probe(name, receipt, witness=None):
    print(f'=== {name} ===')
    for fn in (m.grade, lambda r: m.score(r,witness)):
        label=fn.__name__ if hasattr(fn,'__name__') else 'score'
        try:
            result=fn(receipt)
            print(f'{label}: ACCEPTED {result!r}')
        except Exception:
            print(f'{label}: REJECTED exception')
            print(traceback.format_exc(), end='')
valid='{}'
probes=[
 ('empty receipt / missing captures',{}),
 ('capture set list',{'captures':[]}),
 ('captures present, missing completion',{'captures':{}}),
 ('completion body integer',{'captures':{'completion':{'body':1,'body_sha256':'x'}}}),
 ('checks list',{'captures':{'completion':cap(valid)},'checks':[]}),
 ('checks entry list',{'captures':{'completion':cap(valid)},'checks':{'listener_owned':[]}}),
 ('oversized completion body 8MiB',{'captures':{'completion':cap('{"x":"'+'x'*(8*1024*1024)+'"}')},'checks':{}}),
]
for item in probes: probe(*item)
