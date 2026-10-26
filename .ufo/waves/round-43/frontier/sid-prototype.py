import re,subprocess,sys
from urllib.parse import urlsplit,unquote
files=subprocess.check_output(['git','ls-files','-z']).decode().split('\0')
prose=[f for f in files if f.endswith('.md') and not f.startswith('.ufo') and f!='corpus/SOURCES.md']
reg={}
for l in open('corpus/SOURCES.md',encoding='utf-8'):
    m=re.match(r'^ {0,3}\|\s*(S\d{3,})\s*\|',l)
    if m: reg[m.group(1)]=l
URL=re.compile(r'https?://[^\s)\]>`|"\'<]+')
def key(u):
    u=u.rstrip('.,;:)…').split('#')[0]
    u=re.sub(r':\d+(-\d+)?$','',u)
    p=urlsplit(u); host=p.netloc.lower(); path=unquote(p.path).strip('/')
    segs=[s for s in path.split('/') if s]
    return host,segs
def match(u,row):
    if u in row: return True
    host,segs=key(u)
    if not segs: return host in row
    base=segs[-1]
    low=row
    if host.endswith('github.com') or host=='raw.githubusercontent.com' or host=='api.github.com':
        if host=='api.github.com': segs=segs[1:]
        repo='/'.join(segs[:2]) if len(segs)>=2 else ''
        return bool(repo) and repo in low and (len(segs)<=3 or base in low)
    if host.endswith('arxiv.org'):
        m=re.search(r'\d{4}\.\d{4,5}',u); return bool(m) and m.group(0) in low
    return host in low and (base in low or len(segs)<=1)
pairs=[];bad=[]
for f in prose:
    for i,l in enumerate(open(f,encoding='utf-8',errors='replace'),1):
        ms=list(re.finditer(r'(?<![A-Za-z0-9])S\d{3}(?![0-9])',l))
        for k,m in enumerate(ms):
            end=ms[k+1].start() if k+1<len(ms) else len(l)
            w=l[m.end():min(end,m.end()+200)]
            us=[u.rstrip('.,;:)…') for u in URL.findall(w)]
            if not us: continue
            sid=m.group(0); pairs.append((f,i,sid))
            row=reg.get(sid)
            if row is None: bad.append((f,i,sid,'dangling',us[0])); continue
            if not any(match(u,row) for u in us): bad.append((f,i,sid,'mismatch',us[0]))
print(len(pairs),len(bad))
for b in bad: print(b)
