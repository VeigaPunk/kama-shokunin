import socket, threading, subprocess, os, sys, json, time, hashlib
S = '/fast/scratch/hyaku/kama-r63/w/EX06ProxyEnv'
D = S + '/clone'

class Listener:
    def __init__(self):
        self.sock = socket.socket(); self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', 0)); self.sock.listen(16)
        self.port = self.sock.getsockname()[1]
        self.log = []; self.stop = False
        self.t = threading.Thread(target=self.loop, daemon=True); self.t.start()
    def loop(self):
        self.sock.settimeout(0.2)
        while not self.stop:
            try: c, a = self.sock.accept()
            except socket.timeout: continue
            except OSError: break
            c.settimeout(1.0)
            try: data = c.recv(65536)
            except Exception: data = b''
            self.log.append({'t': time.strftime('%H:%M:%S'), 'peer': '%s:%d' % a, 'first_bytes': data[:160].decode('latin1')})
            try: c.sendall(b'HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            except Exception: pass
            c.close()

def run(label, tool):
    L = Listener()
    px = 'http://127.0.0.1:%d' % L.port
    env = {k: v for k, v in os.environ.items() if k.lower() not in ('no_proxy',) and not k.lower().endswith('_proxy')}
    for k in ('HTTP_PROXY', 'http_proxy', 'ALL_PROXY', 'https_proxy'): env[k] = px
    assert 'NO_PROXY' not in env and 'no_proxy' not in env
    w = '%s/w-%s' % (S, label); out = '%s/r-%s.json' % (S, label)
    p = subprocess.run([sys.executable, tool, '--work', w, '--out', out], env=env, capture_output=True, text=True, timeout=400, cwd=S)
    L.stop = True; time.sleep(0.5); L.sock.close()
    r = json.load(open(out)) if os.path.exists(out) else {}
    res = {'label': label, 'tool': tool, 'proxy': px, 'exit': p.returncode, 'verdict': r.get('verdict'), 'schema': r.get('schema'),
           'proxy_connections': len(L.log), 'proxy_log': L.log,
           'failed_checks': {k: v for k, v in (r.get('checks') or {}).items() if isinstance(v, dict) and v.get('passed') is False} if isinstance(r.get('checks'), dict) else None,
           'stdout_tail': p.stdout[-600:], 'stderr_tail': p.stderr[-600:], 'out_sha256': hashlib.sha256(open(out,'rb').read()).hexdigest() if os.path.exists(out) else None}
    print(json.dumps(res, indent=1)); open('%s/res-%s.json' % (S, label), 'w').write(json.dumps(res, indent=1))

run(sys.argv[1], sys.argv[2])
