import importlib.util, multiprocessing as mp, os
p='/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py'
def load():
    spec=importlib.util.spec_from_file_location('live',p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def worker(bar, q):
    m=load(); ref=m.refused_ports()
    for i in range(200):
        bar.wait()
        q.put(('a', i, m.pick_port(ref)))
        # second participant is the fork below; barrier of 2
if __name__=='__main__':
    m=load(); ref=m.refused_ports()
    ctx=mp.get_context('fork')
    bar=ctx.Barrier(2); q=ctx.Queue()
    def w(tag):
        for i in range(300):
            bar.wait()
            q.put((tag,i,m.pick_port(ref)))
    ps=[ctx.Process(target=w,args=(t,)) for t in ('a','b')]
    [x.start() for x in ps]; [x.join() for x in ps]
    res={}
    while not q.empty():
        t,i,port=q.get(); res.setdefault(i,{})[t]=port
    coll=[(i,v) for i,v in res.items() if v.get('a')==v.get('b')]
    print('rounds', len(res), 'identical-port rounds', len(coll))
    print('sample collisions', coll[:5])
