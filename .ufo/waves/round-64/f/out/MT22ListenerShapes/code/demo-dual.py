"""b3 demonstration: one port number, two servers, two answers.
127.0.0.1:P = the pinned llama-server (what the counter validates and probes)
[::1]:P     = the root-owned canned responder (invisible to the counter)
"""
import json, os, socket, subprocess, sys, time, urllib.request
S = '/fast/scratch/hyaku/kama-r64/f/MT22ListenerShapes'
s = socket.socket(); s.bind(('127.0.0.1', 0)); P = s.getsockname()[1]; s.close()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(url):
    try:
        with opener.open(url, timeout=3) as r:
            return r.status, r.read(200).decode()
    except Exception as e:
        return type(e).__name__, str(e)
srv = subprocess.Popen([os.path.expanduser('~/.local/opt/llama-b11755/llama-server'),
                        '--model', os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'),
                        '--alias', 'pinned-real', '--port', str(P), '--host', '127.0.0.1',
                        '-c', '512', '-t', '1'],
                       stdout=open(S + '/demo-server.log', 'wb'), stderr=subprocess.STDOUT)
up = False
for _ in range(200):
    try:
        c = socket.create_connection(('127.0.0.1', P), timeout=0.5); c.close(); up = True; break
    except OSError:
        if srv.poll() is not None: break
        time.sleep(0.1)
print('real pinned server on 127.0.0.1:%d up=%s' % (P, up))
# daemon binds ::1 on the same port
daemon = subprocess.Popen(['sudo', '-n', sys.executable, S + '/mt22-daemon.py',
                           S + '/demo-daemon.sock'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(100):
    if os.path.exists(S + '/demo-daemon.sock'): break
    time.sleep(0.1)
time.sleep(0.3)
cs = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); cs.settimeout(8)
cs.connect(S + '/demo-daemon.sock')
payload = json.dumps({'mode': 'v6', 'port': P, 'hold': S + '/demo-hold', 'work': S + '/demo-work'}).encode()
os.makedirs(S + '/demo-hold', exist_ok=True); os.makedirs(S + '/demo-work', exist_ok=True)
cs.sendall(str(len(payload)).encode() + b'\n' + payload)
print('daemon ack:', cs.recv(64))
time.sleep(1.0)
st, body = get('http://127.0.0.1:%d/v1/models' % P)
print('GET http://127.0.0.1:%d/v1/models ->' % P, st, body[:120])
st, body = get('http://[::1]:%d/v1/models' % P)
print('GET http://[::1]:%d/v1/models    ->' % P, st, body[:120])
st, body = get('http://127.0.0.1:%d/health' % P)
print('GET http://127.0.0.1:%d/health   ->' % P, st, body[:60])
st, body = get('http://[::1]:%d/health' % P)
print('GET http://[::1]:%d/health       ->' % P, st, body[:60])
srv.terminate(); srv.wait()
daemon.terminate() if daemon.poll() is None else None
try:
    import signal
    subprocess.run(['sudo', '-n', 'pkill', '-f', 'mt22-daemon.py'], capture_output=True)
except Exception:
    pass
print('demo done')
