#!/usr/bin/env python3
"""E5/E6: response body cap. A loopback stub serves a 100 MiB body (and a trickle body).
Each client runs in its own process so peak RSS (ru_maxrss) is attributable."""
import json, os, socket, subprocess, sys, threading, time

S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
OUT = f'{S}/exp/body'
os.makedirs(OUT, exist_ok=True)
BIG = 100 * 1024 * 1024
CHUNK = b'A' * (1 << 20)


def big_server():
    ls = socket.socket(); ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(('127.0.0.1', 0)); ls.listen(8)

    def handle(c):
        try:
            c.recv(65536)
            c.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                      b'Content-Length: %d\r\nConnection: close\r\n\r\n' % BIG)
            sent = 0
            while sent < BIG:
                c.sendall(CHUNK); sent += len(CHUNK)
        except OSError:
            pass
        finally:
            c.close()

    def loop():
        while True:
            c, _ = ls.accept()
            threading.Thread(target=handle, args=(c,), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start()
    return ls.getsockname()[1]


def trickle_server(total_bytes, gap_s):
    """Declares a large Content-Length and drips one byte every gap_s seconds."""
    ls = socket.socket(); ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(('127.0.0.1', 0)); ls.listen(4)

    def handle(c):
        try:
            c.recv(65536)
            c.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                      b'Content-Length: 100000\r\nConnection: close\r\n\r\n')
            for _ in range(total_bytes):
                c.sendall(b'x'); time.sleep(gap_s)
        except OSError:
            pass
        finally:
            c.close()

    def loop():
        while True:
            c, _ = ls.accept()
            threading.Thread(target=handle, args=(c,), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start()
    return ls.getsockname()[1]


CLIENT = r'''
import importlib.util, json, resource, sys, time
kind, path, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('m', path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t0 = time.monotonic()
if kind == 'tool':
    r = m.http_post(port, '/v1/completions', {'prompt': 'x'}, timeout=float(sys.argv[4]))
    out = {'status': r['status'], 'error': r['error'], 'body_bytes_kept': len(r['body']),
           'body_truncated_flag': r['body_truncated']}
else:
    st, hdr, text, _ = m.http(port, '/v1/completions', {'prompt': 'x'}, timeout=float(sys.argv[4]))
    out = {'status': st, 'body_chars_kept': len(text)}
out['elapsed_s'] = round(time.monotonic() - t0, 2)
out['maxrss_mib'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
print(json.dumps(out))
'''
open(f'{OUT}/client.py', 'w').write(CLIENT)

TOOL = f'{S}/clone/tools/kama-completion-live.py'
CTR = f'{S}/clone/tools/round63-c1-counter.py'
bp = big_server()
res = {}
for kind, path in (('tool', TOOL), ('counter', CTR)):
    p = subprocess.run([sys.executable, f'{OUT}/client.py', kind, path, str(bp), '20'],
                       capture_output=True, text=True, timeout=300)
    res[f'big_{kind}'] = (p.stdout.strip() or p.stderr.strip()[-300:])
    print(kind, res[f'big_{kind}'])

tp = trickle_server(total_bytes=30, gap_s=0.5)   # ~15 s of drip, timeout 2 s
p = subprocess.run([sys.executable, f'{OUT}/client.py', 'tool', TOOL, str(tp), '2'],
                   capture_output=True, text=True, timeout=300)
res['trickle_tool_timeout2s'] = (p.stdout.strip() or p.stderr.strip()[-300:])
print('trickle', res['trickle_tool_timeout2s'])
json.dump(res, open(f'{OUT}/summary.json', 'w'), indent=1)
