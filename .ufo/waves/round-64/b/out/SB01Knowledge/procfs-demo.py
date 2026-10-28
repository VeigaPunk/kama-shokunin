import os, socket, hashlib, subprocess, time, sys
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def stat(pid):
    s=open(f'/proc/{pid}/stat').read(); r=s[s.rindex(')')+2:].split()
    return int(r[1]), int(r[19])   # field 4 ppid, field 22 starttime
def listen_inodes(port):
    out=[]
    for p in ('/proc/net/tcp','/proc/net/tcp6'):
        for ln in open(p).readlines()[1:]:
            f=ln.split()
            if f[3]=='0A' and int(f[1].split(':')[1],16)==port: out.append(int(f[9]))
    return out
def holders(inodes):
    w={f'socket:[{i}]' for i in inodes}; hs=[]
    for n in os.listdir('/proc'):
        if not n.isdigit(): continue
        try: fds=os.listdir(f'/proc/{n}/fd')
        except OSError: continue
        for fd in fds:
            try:
                if os.readlink(f'/proc/{n}/fd/{fd}') in w: hs.append(int(n)); break
            except OSError: pass
    return sorted(hs)
print('CLK_TCK', os.sysconf('SC_CLK_TCK'), 'kernel', os.uname().release, 'python', sys.version.split()[0])
ls=socket.socket(); ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
ls.bind(('127.0.0.1',0)); ls.listen(4); port=ls.getsockname()[1]
ino=listen_inodes(port); print('port',port,'inodes',ino)
print('holders before fork', holders(ino), 'self', os.getpid())
pid=os.fork()
if pid==0:
    time.sleep(3); os._exit(0)
time.sleep(0.2)
h=holders(ino); print('holders after fork (child inherits listen fd)', h, 'child', pid)
for p in h:
    print(' pid',p,'exe_sha256',sha(f'/proc/{p}/exe')[:16],'(python)' ,'ppid,starttime',stat(p))
print('child ppid', stat(pid)[0], 'self', os.getpid())
os.environ['KAMA_DEMO_SET_AT_RUNTIME']='1'
env=open(f'/proc/{os.getpid()}/environ','rb').read().split(b'\0')
print('runtime-set var visible in /proc/self/environ:', any(e.startswith(b'KAMA_DEMO_SET_AT_RUNTIME') for e in env))
os.waitpid(pid,0)
ps=[subprocess.Popen(['sleep','3']) for _ in range(60)]
time.sleep(0.3)
st=[stat(p.pid)[1] for p in ps]
print('60 sleep children: distinct starttime ticks', len(set(st)), 'min', min(st), 'max', max(st), 'span_ticks', max(st)-min(st))
for p in ps: p.kill(); p.wait()
ls.close()
