#!/usr/bin/env python3
"""E1: env proxies (hostile listener, dead port) must not receive any tool traffic.
Runs the lane tool under strace -f (connect/sendto/sendmsg) for each proxy variant."""
import json, os, re, socket, subprocess, sys, threading

S = '/fast/scratch/hyaku/kama-r63/w/SN01LoopbackSecurity'
CLONE = f'{S}/clone'
TOOL = f'{CLONE}/tools/kama-completion-live.py'
OUT = f'{S}/exp/proxy'
os.makedirs(OUT, exist_ok=True)

# hostile proxy: accepts, counts, answers garbage
hits = {'n': 0}
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 0)); srv.listen(16)
HOSTILE = srv.getsockname()[1]

def serve():
    while True:
        c, _ = srv.accept()
        hits['n'] += 1
        try:
            c.sendall(b'HTTP/1.1 500 hostile\r\nContent-Length: 0\r\n\r\n')
        except OSError:
            pass
        c.close()
threading.Thread(target=serve, daemon=True).start()

# dead proxy: a port nothing listens on
t = socket.socket(); t.bind(('127.0.0.1', 0)); DEAD = t.getsockname()[1]; t.close()

PROXY_KEYS = ['HTTP_PROXY', 'http_proxy', 'HTTPS_PROXY', 'https_proxy',
              'ALL_PROXY', 'all_proxy']
variants = {
    'hostile': f'http://127.0.0.1:{HOSTILE}',
    'dead': f'http://127.0.0.1:{DEAD}',
}
summary = {}
for name, url in variants.items():
    env = {k: v for k, v in os.environ.items()
           if k not in PROXY_KEYS and not k.startswith('GIT_')}
    for k in PROXY_KEYS:
        env[k] = url
    env['NO_PROXY'] = ''
    env['no_proxy'] = ''
    work = f'{OUT}/{name}-work'
    rec = f'{OUT}/{name}-receipt.json'
    trace = f'{OUT}/{name}-strace.txt'
    before = hits['n']
    p = subprocess.run(
        ['strace', '-f', '-qq', '-e', 'trace=connect,sendto,sendmsg',
         '-o', trace, sys.executable, TOOL, '--work', work, '--out', rec,
         '--nonce', 'proxy-' + name],
        env=env, capture_output=True, text=True, timeout=300)
    rc = p.returncode
    verdict = None
    if os.path.exists(rec):
        verdict = json.load(open(rec)).get('verdict')
    dests = set()
    if os.path.exists(trace):
        for line in open(trace, encoding='utf-8', errors='replace'):
            for m in re.finditer(r'sin_addr=inet_addr\("([^"]+)"\), sin_port=htons\((\d+)\)', line):
                dests.add(f'{m.group(1)}:{m.group(2)}')
            for m in re.finditer(r'connect\(\d+, \{sa_family=AF_INET6?, sin6?_port=htons\((\d+)\)', line):
                dests.add(f'ipv6:{m.group(1)}')
    summary[name] = {
        'tool_rc': rc, 'verdict': verdict,
        'hostile_proxy_connections': hits['n'] - before,
        'connect_destinations': sorted(dests),
        'env_proxies_set': {k: url for k in PROXY_KEYS},
    }
    print(name, json.dumps(summary[name]))
json.dump(summary, open(f'{OUT}/summary.json', 'w'), indent=1)
