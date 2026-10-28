import sys, hashlib, os
S = '/fast/scratch/hyaku/kama-r63/w/RV01ToolV2'
tpl = open(S + '/fake_server.py.tpl').read()
for mode in sys.argv[1:]:
    p = f'{S}/fakes/{mode}.py'
    open(p, 'w').write(tpl.replace('__MODE__', mode))
    os.chmod(p, 0o755)
    print(mode, hashlib.sha256(open(p,'rb').read()).hexdigest())
