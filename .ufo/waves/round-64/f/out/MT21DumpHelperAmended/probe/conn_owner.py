#!/usr/bin/env python3
"""Empirical test: can the counter learn WHICH process accepted a
connection it made to the run port, by joining the /proc/net/tcp row of
the server-side socket to the holder fds of that socket's inode?"""
import os, socket, subprocess, sys, time, signal


def server_side_rows(port, lport):
    """(inode,) of the server-side ESTABLISHED socket of our connection."""
    out = []
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(path, encoding='ascii') as fh:
                next(fh, None)
                for line in fh:
                    f = line.split()
                    if len(f) < 10 or f[3] != '01':
                        continue
                    _, _, lp = f[1].partition(':')
                    _, _, rp = f[2].partition(':')
                    if int(lp, 16) == port and int(rp, 16) == lport:
                        out.append(int(f[9]))
        except (OSError, ValueError, IndexError):
            continue
    return out


def holders(inode):
    """pids holding socket:[inode] (readable fd tables only) + unreadable pids."""
    held, unread = [], []
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        try:
            fds = os.listdir(f'/proc/{pid}/fd')
        except PermissionError:
            unread.append(pid)
            continue
        except OSError:
            continue
        for fd in fds:
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') == f'socket:[%d]' % inode:
                    held.append(pid)
                    break
            except OSError:
                continue
    return held, unread


def probe_acceptor(port, timeout=8.0):
    """Open our own connection, learn who accepted it."""
    s = socket.socket()
    s.settimeout(3.0)
    s.connect(('127.0.0.1', port))
    lport = s.getsockname()[1]
    try:
        s.sendall(b'GET /health HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')
    except OSError:
        pass
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        rows = server_side_rows(port, lport)
        if rows:
            held, unread = holders(rows[0])
            return {'lport': lport, 'inode': rows[0], 'held': held,
                    'unread': len(unread)}
        time.sleep(0.05)
    return {'lport': lport, 'inode': None, 'held': [], 'unread': -1}


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if port == 0:
        port = 46001
        srv = subprocess.Popen(
            ['/home/vgpnk/.local/opt/llama-b11755/llama-server', '--model',
             '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf',
             '--alias', 'kama-completion-probe', '--port', str(port),
             '--host', '127.0.0.1', '-c', '512', '-t', '1'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            env={k: v for k, v in os.environ.items()
                 if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')})
        t0 = time.time()
        while time.time() - t0 < 60:
            try:
                socket.create_connection(('127.0.0.1', port), timeout=1).close()
                break
            except OSError:
                time.sleep(0.2)
        print('server pid', srv.pid)
        print('HONEST:', probe_acceptor(port))
        srv.send_signal(signal.SIGTERM)
        srv.wait(timeout=20)
