import os
def st(p):
    s=open(f'/proc/{p}/stat').read(); r=s[s.rindex(')')+2:].split(); return int(r[1])
p=os.getpid(); out=[]
for _ in range(10):
    pp=st(p)
    if pp<=0: break
    out.append((pp, open(f'/proc/{pp}/comm').read().strip())); p=pp
print('self', os.getpid(), 'ancestors(ppid,comm):', out)
