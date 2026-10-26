import subprocess,difflib,sys
def show(t,p): return subprocess.run(['git','-C','up','show',f'{t}:{p}'],capture_output=True,text=True).stdout.split('\n')
def mapping(a,b):
    sm=difflib.SequenceMatcher(None,a,b,autojunk=False); m={}
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            for k in range(i2-i1): m[i1+k+1]=j1+k+1
    return m
C={'src/llama-context.cpp':[(219,'cited 219 (b11889 numbering)'),]}
checks={
 'src/llama-context.cpp':[(225,225),(387,403),(419,427),(4132,4136),(2642,2642),(192,192),(342,342),(618,618),(370,370)],
 'src/llama-kv-cache.cpp':[(65,98),(142,145),(233,244),(301,304),(1222,1234),(84,84),(92,97)],
}
for p,rs in checks.items():
    a=show('b11906',p); b=show('b11909',p); m=mapping(a,b)
    for lo,hi in rs:
        miss=[l for l in range(lo,hi+1) if l not in m]
        newr=sorted(set(m[l] for l in range(lo,hi+1) if l in m))
        print(p,f'{lo}-{hi}','-> new',(newr[0],newr[-1]) if newr else None,'changed/unmatched old lines:',miss if len(miss)<12 else f'{len(miss)} lines {miss[:3]}..')
